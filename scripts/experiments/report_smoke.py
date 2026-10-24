"""Freeze verifiable research evidence; does not tune or retrain the model."""
from pathlib import Path
import hashlib,json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/build/experiments';PITCH=ROOT/'presentation/extensions'
r=json.loads((OUT/'results.json').read_text());split=json.loads((OUT/'split.json').read_text())['samples'];history=json.loads((OUT/'training-history.json').read_text())
sets={k:{s['location_group'] for s in split if s['split']==k} for k in ['train','validation','test']}
assert not sets['train']&sets['validation'] and not sets['train']&sets['test'] and not sets['validation']&sets['test']
assert hashlib.sha256((OUT/'checkpoints/unet-best.pt').read_bytes()).hexdigest()==r['checkpoint_sha256']
for m in [r['unet_test'],r['baseline_test']]:
 assert math.isclose(m['iou'],m['tp']/(m['tp']+m['fp']+m['fn']))
 assert math.isclose(m['dice'],2*m['tp']/(2*m['tp']+m['fp']+m['fn']))
assert r['best_epoch']==max(history,key=lambda h:h['validation_iou'])['epoch']
assert sum(v['images'] for v in r['split_counts'].values())==len(split)
(OUT/'verification.json').write_text(json.dumps({'all_passed':True,'checks':['location groups disjoint across splits','checkpoint hash matches published result','foreground metrics reconcile confusion counts','checkpoint epoch chosen by validation','split counts reconcile manifest'],'test_images':r['split_counts']['test']['images']},indent=2)+'\n')
plt.rcParams.update({'figure.facecolor':'#151a22','axes.facecolor':'#151a22','axes.edgecolor':'#60717d','text.color':'#e5ebef','axes.labelcolor':'#d7e3ec','xtick.color':'#b4c0c9','ytick.color':'#b4c0c9'})
fig,axes=plt.subplots(1,2,figsize=(11,4.5));axes[0].plot([h['epoch'] for h in history],[h['validation_iou'] for h in history],color='#81cbd3');axes[0].scatter([r['best_epoch']],[history[r['best_epoch']-1]['validation_iou']],color='#f4b36b',zorder=5);axes[0].set(xlabel='Training epoch',ylabel='Validation foreground IoU',title='Checkpoint selected on validation')
axes[1].bar(['RGB heuristic','Multispectral U-Net'],[r['baseline_test']['iou'],r['unet_test']['iou']],color=['#8ba0ae','#a8dfbc']);axes[1].set(ylim=(0,1),ylabel='Held-out foreground IoU',title=f"{r['split_counts']['test']['images']} held-out research images")
for a in axes:a.spines[['top','right']].set_visible(False)
fig.text(.05,.015,'Different input channels: RGB baseline3, U-Net12. Industrial smoke research; no validated Texas flare detection.',fontsize=9,color='#aabcc9');fig.tight_layout(rect=[0,.06,1,1])
for ext in ['png','svg']:fig.savefig(PITCH/f'satellite-experiment.{ext}',dpi=180)
print(r['unet_test'])
