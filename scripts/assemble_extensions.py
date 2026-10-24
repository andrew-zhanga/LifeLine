"""Validate and copy additive extension artifacts without modifying original browser assets."""
from pathlib import Path
import gzip, hashlib, json, shutil, subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'demo/public/data/extensions'

def read(path):return json.loads(path.read_text())

def main():
 checks={}
 for part,report in [('transport','diagnostics.json'),('community','validation.json')]:
  p=ROOT/'data/build'/part/report
  obj=read(p);assert obj['all_passed'],(part,obj)
  checks[part]=obj['checks']
 community=read(ROOT/'data/build/community/community.json')
 for plan in community['plans']:
  assert len(plan['selected_ids'])==len(set(plan['selected_ids']))
  assert plan['capex_usd']<=plan['budget_usd']+1e-5
  for group in ['population','under5','age65plus']:
   r=plan['regional'][group]
   assert r['baseline']>=r['residual']-1e-5 and r['residual']>=-1e-5
 artifacts=[]
 for part,names in [('transport',['scene.json','diagnostics.json']),('community',['community.json','robustness.json'])]:
  for name in names:
   src=ROOT/'data/build'/part/name;dest=OUT/part/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
   b=dest.read_bytes();artifacts.append({'url':f'/data/extensions/{part}/{name}','bytes':len(b),'gzip_bytes':len(gzip.compress(b)),'sha256':hashlib.sha256(b).hexdigest()})
 experiment=ROOT/'data/build/experiments/results.json'
 if experiment.exists():
  dest=OUT/'experiments';dest.mkdir(exist_ok=True)
  shutil.copy2(experiment,dest/'results.json')
  shutil.copytree(experiment.parent/'examples',dest/'examples',dirs_exist_ok=True)
 report={'schema_version':'1.0','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'checks':checks,'artifacts':artifacts,'original_assets_unchanged':True}
 (ROOT/'reports/extensions/assembly.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
