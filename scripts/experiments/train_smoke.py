"""Bounded, site-held-out industrial smoke segmentation experiment; not flare validation.
Run after download_smoke.py. Outputs reproducible split, checkpoint, metrics and examples.
"""
from pathlib import Path
import argparse, hashlib, json, random, tarfile, time
import numpy as np
from PIL import Image, ImageDraw
import rasterio
from rasterio.warp import transform_bounds
from rasterio.io import MemoryFile
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/experiments/industrial-smoke'
OUT=ROOT/'data/build/experiments'; OUT.mkdir(parents=True,exist_ok=True)
SEED=20261024
BANDS=[0,1,2,3,4,5,6,7,8,9,11,12] # exclude Sentinel-2 B10 per source description

def dump(path,obj):path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def split(site):
 n=int(hashlib.sha256(('flarewise-v1:'+site).encode()).hexdigest()[:8],16)%10
 return 'test' if n<2 else 'validation' if n<4 else 'train'

def prepare():
 cache=DATA/'prepared.npz'
 label_paths=sorted((DATA/'labels').glob('*.json'))
 fingerprint=hashlib.sha256(Path(__file__).read_bytes()+b''.join(p.read_bytes() for p in label_paths)).hexdigest()
 if cache.exists():
  cached=np.load(cache)
  if 'fingerprint' in cached and str(cached['fingerprint'])==fingerprint:return cached
 labels={p.name.replace('_features.json',''):p for p in (DATA/'labels').glob('*.json')}
 xs=[]; ys=[]; ids=[]; geos=[]; negatives=0;matched=set();shape_counts={};invalid_polygons=[]
 # Include only independently annotated positive images and a bounded sample of published negative images.
 with tarfile.open(DATA/'images.tar.gz','r|gz') as archive:
  for member in archive:
   stem=Path(member.name).stem
   if not member.isfile() or not member.name.endswith('.tif'):continue
   labeled=stem in labels
   negative=member.name.startswith('negative/') and int(hashlib.sha256(stem.encode()).hexdigest()[:8],16)%20==0
   if not labeled and not negative:continue
   payload=archive.extractfile(member).read()
   with MemoryFile(payload) as mem:
    with mem.open() as src:
     x=src.read(); geo=list(transform_bounds(src.crs,'EPSG:4326',*src.bounds))
   if x.shape[0]!=13 or not np.isfinite(x).all() or min(x.shape[1:])<118 or max(x.shape[1:])>120:raise ValueError((stem,x.shape))
   shape_counts[str(x.shape)]=shape_counts.get(str(x.shape),0)+1
   if x.shape[1:]!=(120,120):
    x=np.pad(x,((0,0),(0,max(0,120-x.shape[1])),(0,max(0,120-x.shape[2]))),mode='edge')[:,:120,:120]
   mask=Image.new('L',(120,120)); draw=ImageDraw.Draw(mask)
   if labeled:
    matched.add(stem);doc=json.loads(labels[stem].read_text())
    for result in [r for completion in doc['completions'] for r in completion['result']]:
     if result['type']=='polygonlabels' and 'smoke' in result['value']['polygonlabels']:
      # Label Studio percentages; source explicitly specifies multiplying by 1.2.
      points=result['value']['points']
      if len(points)<3:invalid_polygons.append({'id':stem,'vertices':len(points)});continue
      draw.polygon([(float(a)*1.2,float(b)*1.2) for a,b in points],fill=1)
   else:negatives+=1
   xs.append(x.astype(np.float32));ys.append(np.asarray(mask,dtype=np.uint8));ids.append(stem);geos.append(json.dumps(geo))
 assert matched==set(labels),f'Missing annotated images: {len(set(labels)-matched)}'
 assert len(ids)==len(set(ids)), 'Duplicate image stems'
 dump(OUT/'preprocessing.json',{'fingerprint':fingerprint,'matched_labels':len(matched),'invalid_polygons_skipped':invalid_polygons,'shape_counts':shape_counts,'coordinate_frame':'WGS84 bounds','mask_rasterizer':'PIL polygon; percentage coordinates times1.2'})
 print({'prepared':len(ids),'published_negatives':negatives,'annotated':len(ids)-negatives},flush=True)
 np.savez_compressed(cache,x=np.array(xs),y=np.array(ys),ids=np.array(ids),geos=np.array(geos),fingerprint=np.array(fingerprint))
 return np.load(cache)

class UNet(nn.Module):
 def __init__(self):
  super().__init__()
  def block(a,b):return nn.Sequential(nn.Conv2d(a,b,3,padding=1),nn.ReLU(),nn.Conv2d(b,b,3,padding=1),nn.ReLU())
  self.a=block(12,16);self.b=block(16,32);self.c=block(32,64);self.d=block(96,32);self.e=block(48,16);self.out=nn.Conv2d(16,1,1)
 def forward(self,x):
  a=self.a(x);b=self.b(nn.functional.max_pool2d(a,2));c=self.c(nn.functional.max_pool2d(b,2))
  d=self.d(torch.cat([nn.functional.interpolate(c,size=b.shape[-2:],mode='bilinear',align_corners=False),b],1))
  return self.out(self.e(torch.cat([nn.functional.interpolate(d,size=a.shape[-2:],mode='bilinear',align_corners=False),a],1)))

def metrics(pred,y):
 pred=np.asarray(pred,dtype=bool); y=np.asarray(y,dtype=bool)
 tp=int((pred&y).sum());fp=int((pred&~y).sum());fn=int((~pred&y).sum())
 denom=tp+fp+fn
 return {'iou':tp/denom if denom else 1.,'dice':2*tp/(2*tp+fp+fn) if denom else 1.,'precision':tp/max(tp+fp,1),'recall':tp/max(tp+fn,1),'tp':tp,'fp':fp,'fn':fn}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--epochs',type=int,default=24);args=parser.parse_args()
 start=time.perf_counter();random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED);torch.set_num_threads(4)
 data=prepare();raw=data['x'];y=data['y'];ids=data['ids'];sites=np.array([s.split('_')[0] for s in ids]);
 # Merge site IDs with overlapping observed footprints before assigning holdouts.
 bounds=np.array([json.loads(g) for g in data['geos']]);unique=sorted(set(sites));parent={s:s for s in unique}
 def find(s):
  while parent[s]!=s:parent[s]=parent[parent[s]];s=parent[s]
  return s
 site_bounds={s:np.array([bounds[sites==s,0].min(),bounds[sites==s,1].min(),bounds[sites==s,2].max(),bounds[sites==s,3].max()]) for s in unique}
 overlap_pairs=0
 for i,a in enumerate(unique):
  aa=site_bounds[a]
  for b in unique[i+1:]:
   bb=site_bounds[b]
   if aa[0]<=bb[2] and bb[0]<=aa[2] and aa[1]<=bb[3] and bb[1]<=aa[3]:
    ra,rb=find(a),find(b);parent[max(ra,rb)]=min(ra,rb);overlap_pairs+=1
 location_groups=np.array([find(s) for s in sites]);parts=np.array([split(s) for s in location_groups])
 dump(OUT/'geographic-leakage-audit.json',{'site_ids':len(unique),'overlapping_site_pairs':overlap_pairs,'disjoint_location_groups':len(set(location_groups)),'rule':'Overlapping per-site observed WGS84 footprint envelopes are unioned before assigning any split.'})
 groups={k:np.flatnonzero(parts==k) for k in ['train','validation','test']}
 assert all(len(v)>0 for v in groups.values())
 assert not set(sites[groups['train']])&set(sites[groups['test']])
 # Fixed reflectance scaling; no test-statistics fitting. Values may exceed 10000, clip to 1.5.
 x=np.clip(raw[:,BANDS]/10000.,0,1.5).astype(np.float32)
 dump(OUT/'split.json',{'seed':SEED,'rule':'sha256(flarewise-v1:location_group) first 8 hex modulo10; 0,1 test; 2,3 validation; 4..9 train','samples':[{'id':str(s),'site_id':str(site),'location_group':str(location),'split':str(part),'positive_mask':bool(mask.any())} for s,site,location,part,mask in zip(ids,sites,location_groups,parts,y)]})
 device=torch.device('mps' if torch.backends.mps.is_available() else 'cpu');model=UNet().to(device)
 optimizer=torch.optim.Adam(model.parameters(),lr=0.001)
 train=groups['train'];val=groups['validation'];test=groups['test']
 loader=DataLoader(TensorDataset(torch.from_numpy(x[train]),torch.from_numpy(y[train,None].astype(np.float32))),batch_size=24,shuffle=True,generator=torch.Generator().manual_seed(SEED))
 pos=float(y[train].mean());positive_weight=min(20.,(1-pos)/max(pos,1e-6))
 loss_fn=nn.BCEWithLogitsLoss(pos_weight=torch.tensor([positive_weight],device=device))
 def predict(indices):
  model.eval();out=[]
  with torch.no_grad():
   for batch in np.array_split(indices,max(1,(len(indices)+23)//24)):
    out.append(model(torch.from_numpy(x[batch]).to(device)).sigmoid().cpu().numpy()[:,0])
  return np.concatenate(out)
 # Simple RGB bright-neutral baseline tuned ONLY on validation.
 rgb=np.clip(raw[:,[3,2,1]]/10000.,0,1.5);brightness=rgb.mean(axis=1);neutral=rgb.max(axis=1)-rgb.min(axis=1)
 candidates=[(float(t),float(s)) for t in [.10,.15,.20,.25,.30,.40,.50] for s in [.05,.10,.20,.30]]
 baseline_choice=max(candidates,key=lambda ts:metrics((brightness[val]>ts[0])&(neutral[val]<ts[1]),y[val])['iou'])
 history=[];best=-1;best_epoch=None;checkpoints=OUT/'checkpoints';checkpoints.mkdir(exist_ok=True)
 for epoch in range(args.epochs):
  tick=time.perf_counter();model.train();total=0
  for xb,yb in loader:
   xb=xb.to(device);yb=yb.to(device)
   if random.random()<.5:xb=xb.flip(-1);yb=yb.flip(-1)
   if random.random()<.5:xb=xb.flip(-2);yb=yb.flip(-2)
   optimizer.zero_grad();logits=model(xb)
   prob=logits.sigmoid();dice=1-(2*(prob*yb).sum()+1)/(prob.sum()+yb.sum()+1)
   loss=loss_fn(logits,yb)+dice;loss.backward();optimizer.step();total+=float(loss.detach().cpu())
  vp=predict(val);score=metrics(vp>.5,y[val])
  row={'epoch':epoch+1,'loss':total/len(loader),'validation_iou':score['iou'],'seconds':time.perf_counter()-tick};history.append(row);print(json.dumps(row),flush=True)
  if score['iou']>best:
   best=score['iou'];best_epoch=epoch+1;torch.save(model.state_dict(),checkpoints/'unet-best.pt')
  dump(OUT/'training-history.json',history)
 model.load_state_dict(torch.load(checkpoints/'unet-best.pt',map_location=device,weights_only=True))
 vp=predict(val);threshold=max([.2,.3,.4,.5,.6,.7,.8],key=lambda t:metrics(vp>t,y[val])['iou'])
 # Test used exactly once after model/threshold selection on validation.
 probabilities=predict(test);pred=probabilities>threshold;truth=y[test]
 baseline=(brightness[test]>baseline_choice[0])&(neutral[test]<baseline_choice[1])
 scores=[metrics(p,t)['iou'] for p,t in zip(pred,truth)]
 positive_examples=np.flatnonzero(truth.reshape(len(truth),-1).any(axis=1))
 ranked=positive_examples[np.argsort(np.array(scores)[positive_examples])];chosen=list(dict.fromkeys([int(ranked[0]),int(ranked[len(ranked)//2]),int(ranked[-1])]))
 example_dir=OUT/'examples';example_dir.mkdir(exist_ok=True);examples=[]
 for rank,i in enumerate(chosen):
  idx=test[i];im=np.moveaxis(np.clip(rgb[idx]/.35,0,1),0,-1);image=(im*255).astype(np.uint8)
  overlay=image.astype(float)*.65;overlay[pred[i]]+=np.array([30,100,100]);overlay=np.clip(overlay,0,255).astype(np.uint8)
  panels=[image,np.repeat((truth[i]*255).astype(np.uint8)[...,None],3,2),np.repeat((pred[i]*255).astype(np.uint8)[...,None],3,2),overlay]
  path=example_dir/f'example-{rank}.png';Image.fromarray(np.concatenate(panels,axis=1)).resize((960,240),Image.Resampling.NEAREST).save(path)
  examples.append({'id':str(ids[idx]),'site_id':str(sites[idx]),'iou':scores[i],'selection':['lowest positive-scene test IoU','median positive-scene test IoU','highest positive-scene test IoU'][rank],'image':f'examples/{path.name}','panels':['Sentinel-2 RGB','Human mask','U-Net prediction','Overlay']})
 result={'schema_version':'1.0','status':'completed','task':'Industrial smoke segmentation research; not validated gas-flare detection','source_url':'https://zenodo.org/records/4250706','attribution':'Mommert et al. (2020), CC BY 4.0; modified Copernicus Sentinel data 2019, processed by ESA','seed':SEED,'device':str(device),'architecture':'Small 12-channel U-Net, 16/32/64 channels, trained from scratch','parameter_count':sum(p.numel() for p in model.parameters()),'epochs':args.epochs,'best_epoch':best_epoch,'threshold':threshold,'metric_aggregation':'pixel-micro foreground metrics on a deliberately sampled research set; not deployment precision','split_counts':{k:{'images':len(v),'sites':len(set(sites[v])),'location_groups':len(set(location_groups[v])),'positive_images':int(y[v].reshape(len(v),-1).any(axis=1).sum()),'negative_images':int((~y[v].reshape(len(v),-1).any(axis=1)).sum())} for k,v in groups.items()},'unet_test':metrics(pred,truth),'baseline_test':metrics(baseline,truth),'baseline':{'method':'RGB brightness and neutrality thresholds selected on validation','brightness_threshold':baseline_choice[0],'max_channel_spread':baseline_choice[1]},'examples':examples,'seconds':time.perf_counter()-start,'checkpoint_sha256':hashlib.sha256((checkpoints/'unet-best.pt').read_bytes()).hexdigest(),'limitations':['European industrial smoke, not validated on Texas gas flares.','Visible smoke masks are not pollutant concentrations or emission rates.','Published negative image labels treated as empty masks; faint unannotated plumes may exist.','Small bounded training run; no claim to reproduce original paper metrics.','Site-disjoint split; MPS numerical results may vary slightly across versions.']}
 dump(OUT/'results.json',result);print(json.dumps(result),flush=True)

if __name__=='__main__':main()
