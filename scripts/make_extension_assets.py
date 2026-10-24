"""Reproducible extension evidence figures from actual exported calculations."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'presentation/extensions';OUT.mkdir(parents=True,exist_ok=True)
c=json.loads((ROOT/'data/build/community/community.json').read_text());r=json.loads((ROOT/'data/build/community/robustness.json').read_text())
plt.rcParams.update({'figure.facecolor':'#151a22','axes.facecolor':'#151a22','axes.edgecolor':'#60717d','text.color':'#e5ebef','axes.labelcolor':'#d7e3ec','xtick.color':'#b4c0c9','ytick.color':'#b4c0c9','font.size':11,'savefig.facecolor':'#151a22'})
plans={p['id']:p for p in c['plans']}
ids=['budget-5m-benchmark-financial','community-5m-population','community-5m-under5','community-5m-age65plus']
fig,ax=plt.subplots(figsize=(11,5.5));x=np.arange(4)
for i,(group,label,color) in enumerate([('population','All residents','#f4b36b'),('under5','Under 5','#81cbd3'),('age65plus','65+','#a8dfbc')]):
 vals=[plans[k]['regional'][group]['reduction_pct'] for k in ids];ax.bar(x+(i-1)*.23,vals,.21,color=color,label=label)
ax.set_xticks(x,['Financial return','All-resident priority','Under-5 priority','65+ priority']);ax.set_ylabel('Annual weighted index reduction (%)');ax.set_title('The objective changes which people benefit · $5m budget',loc='left',pad=22);ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False);fig.text(.06,.025,'ACS age counts; screening-v1. Relative index reductions, not health-risk reductions.',fontsize=10,color='#a5b3bf');fig.tight_layout(rect=[0,.05,1,1])
for ext in ['png','svg']:fig.savefig(OUT/f'demographic-objectives.{ext}',dpi=180)
plt.close(fig)
ids=['budget-10m-benchmark-financial','budget-10m-benchmark-balanced','community-10m-population']
fig,ax=plt.subplots(figsize=(10,5.5));evaluations={p['plan_id']:p for p in r['fixed_plan_evaluations']}
for k,color,label in zip(ids,['#f4b36b','#a8dfbc','#81cbd3'],['Financial','Balanced / robust','Community']):
 vals=[w['exposure_reduction_pct'] for w in evaluations[k]['weather']];ax.plot(range(4),vals,'o-',color=color,label=label,lw=2.5)
ax.set_xticks(range(4),['Winter','Spring','Summer','Autumn']);ax.set_ylabel('Population-weighted index reduction (%)');ax.set_title('Fixed installations across actual 2023 seasons · $10m',loc='left',pad=22);ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False);fig.text(.06,.025,'All 8,760 hours partitioned by season. Scenario results, not holdout validation or confidence intervals.',fontsize=9,color='#a5b3bf');fig.tight_layout(rect=[0,.05,1,1])
for ext in ['png','svg']:fig.savefig(OUT/f'seasonal-robustness.{ext}',dpi=180)
plt.close(fig)
print(OUT)
import csv,hashlib
with (OUT/'claims.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=['claim','value','unit','source','scenario','limitation']);writer.writeheader()
 for pid in ['budget-10m-benchmark-financial','budget-10m-benchmark-balanced','community-10m-population','community-5m-under5','community-5m-age65plus']:
  p=plans[pid];g=p.get('objective_group') or 'population'
  if g not in p['regional']:g='population'
  writer.writerow({'claim':'NPV','value':p['npv_usd'],'unit':'USD seven-year screening NPV','source':'data/build/community/community.json','scenario':pid,'limitation':'Assumed costs/price; no engineering feasibility claim'})
  writer.writerow({'claim':f'{g} index reduction','value':p['regional'][g]['reduction_pct'],'unit':'percent','source':'data/build/community/community.json','scenario':pid,'limitation':'Relative age/population-weighted screening index, not health improvement'})
 diag=json.loads((ROOT/'data/build/transport/diagnostics.json').read_text())
 writer.writerow({'claim':'Emission pulse refinement L1 difference','value':diag['emission_discretization_sensitivity']['receptor_relative_l1_difference']*100,'unit':'percent','source':'data/build/transport/diagnostics.json','scenario':'120s versus60s pulses','limitation':'Numerical sensitivity, not environmental validation'})
