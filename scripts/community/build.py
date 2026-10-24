"""Annual screening attribution and explicit seasonal robustness; no transport claims."""
from pathlib import Path
import sys,json,hashlib,time
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/portfolio'))
import build as portfolio
sys.path.insert(0,str(ROOT/'scripts/model'))
import build_exposure as model
OUT=ROOT/'data/build/community'; IN=ROOT/'data/verified/processed'; EXP=ROOT/'data/build/exposure'
GROUPS=['population','under5','age65plus']

def read(p):return json.loads(p.read_text())
def save(name,data):
    files=[Path(__file__),ROOT/'data/build/portfolios/site-economics.json',EXP/'site-benefits.json',EXP/'annual-source-contributions.npz',EXP/'exposure-manifest.json',IN/'population_receptors.geojson',IN/'population_tracts.geojson',IN/'weather_2023.json',ROOT/'data/build/portfolios/scenarios.json',ROOT/'contracts/parameters.json']
    meta=dict(schema_version='1.0',model_version='screening-v1',provenance=[{'path':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files],assumptions=['90% source reduction, frozen seven-year economic assumptions.','Age objectives weight actual allocated residents in that age band, with no medical-risk multipliers.','Seasonal weather uses all 2023 hours with constant annual gas-rate proxy; not held-out testing.'],limitations=['Relative screening index, not concentration, health impact or the separate transport replay.','Uniform within-tract population allocation; no exact home locations.','All retained tract residents are population context, not an affected-resident count.','Scenario ranges are not probabilities or confidence intervals.'])
    (OUT/name).write_text(json.dumps({**meta,**data},allow_nan=False,separators=(',',':'))+'\n')

def attribution(si,ci,values,cell_tract,weights,nsite,ntract):
    return np.array([np.bincount(si*ntract+cell_tract[ci],weights=values*w[ci],minlength=nsite*ntract).reshape(nsite,ntract) for w in weights])

def metric(baseline,reduction):
    return dict(baseline=float(baseline),residual=float(max(0,baseline-reduction)),reduction=float(reduction),reduction_pct=float(100*reduction/baseline) if baseline>0 else None)

def seasonal_sources(manifest,si,ci,weights,p):
    sites=read(IN/'flares_regional_2023.geojson')['features'];cells=read(IN/'population_receptors.geojson')['features'];weather=read(IN/'weather_2023.json')['locations']
    sx=model.projected([f['geometry']['coordinates'] for f in sites]);cx=model.projected([f['geometry']['coordinates'] for f in cells]);dx,dy=(cx[ci]-sx[si]).T
    wi={w['id']:i for i,w in enumerate(weather)};assignment=np.array([wi[w] for w in manifest['site_weather_ids']])
    speed=np.array([w['hourly']['wind_speed_100m'] for w in weather]);direction=np.array([w['hourly']['wind_direction_100m'] for w in weather])
    times=weather[0]['hourly']['time'];months=np.array([int(t[5:7]) for t in times]);rates=np.array([f['properties']['annual_flared_m3'] for f in sites])/8760
    outputs=[];defs=[]
    for name,seasonmonths in [('DJF',[12,1,2]),('MAM',[3,4,5]),('JJA',[6,7,8]),('SON',[9,10,11])]:
        indices=np.flatnonzero(np.isin(months,seasonmonths));total=np.zeros(len(si))
        for start in range(0,len(indices),96):
            idx=indices[start:start+96]
            total+=(model.kernel(dx[None,:],dy[None,:],speed[:,idx][assignment[si]].T,direction[:,idx][assignment[si]].T,p)*rates[si]).sum(axis=0)
        source=np.bincount(si,weights=total/len(indices)*weights[ci],minlength=len(sites));outputs.append(source)
        defs.append(dict(id=name,name=name+' 2023',months=seasonmonths,hours=len(indices),baseline_population_weighted_index=float(source.sum())))
        print('season complete',name,flush=True)
    return np.array(outputs),defs

def robust_solve(cost,npv,seasonal,budget,floor,limit):
    # Last continuous variable t is minimum fractional seasonal regional reduction.
    n=len(cost);rows=[np.r_[cost/1e6,0],np.r_[npv/1e6,0]];lower=[-np.inf,floor/1e6];upper=[budget/1e6,np.inf]
    for row in seasonal:
        rows.append(np.r_[row,-1]);lower.append(0);upper.append(np.inf)
    objective=np.zeros(n+1);objective[-1]=-1
    start=time.perf_counter();r=milp(objective,integrality=np.r_[np.ones(n),0],bounds=Bounds(np.zeros(n+1),np.ones(n+1)),constraints=LinearConstraint(np.array(rows),lower,upper),options={'time_limit':limit,'mip_rel_gap':1e-6})
    if r.x is None:raise RuntimeError(r.message)
    sel=np.flatnonzero(r.x[:n]>.5)
    assert cost[sel].sum()<=budget+.01 and npv[sel].sum()>=floor-.01
    return sel,dict(solver_status='optimal' if r.status==0 else 'feasible_best_found',solver_gap=float(r.mip_gap),solve_seconds=time.perf_counter()-start,minimum_seasonal_reduction_pct=float(100*seasonal[:,sel].sum(axis=1).min()),financial_floor_usd=float(floor))

def main():
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    p=read(ROOT/'contracts/parameters.json');manifest=read(EXP/'exposure-manifest.json');raw=np.load(EXP/'annual-source-contributions.npz');si,ci,values=(raw[k] for k in ['site_index','cell_index','values'])
    cells=read(IN/'population_receptors.geojson')['features'];tracts=read(IN/'population_tracts.geojson')['features'];sites=read(ROOT/'data/build/portfolios/site-economics.json')['sites'];scenarios=read(ROOT/'data/build/portfolios/scenarios.json')['scenarios']
    ids=manifest['site_ids'];assert ids==[s['id'] for s in sites];assert manifest['cell_ids']==[c['properties']['id'] for c in cells]
    ti={t['properties']['geoid']:i for i,t in enumerate(tracts)};ct=np.array([ti[c['properties']['geoid']] for c in cells]);weights=np.array([[c['properties'][g] for c in cells] for g in GROUPS])
    matrix=attribution(si,ci,values,ct,weights,len(sites),len(tracts));source=matrix.sum(axis=2);baseline=matrix.sum(axis=1);total=baseline.sum(axis=1);ididx={v:i for i,v in enumerate(ids)}
    expected=read(EXP/'site-benefits.json')['sites'];keys=['annual_population_weighted_index','under5_weighted_index','age65plus_weighted_index']
    assert np.allclose(source,np.array([[s[k] for s in expected] for k in keys]),rtol=1e-10)
    for j,g in enumerate(GROUPS):assert np.allclose(np.bincount(ct,weights=weights[j],minlength=len(tracts)),[t['properties'][g] for t in tracts],atol=1e-7)
    plans=[];objective_plans=[];eligible=np.array([i for i,s in enumerate(sites) if s['eligible_for_capture']]);cost=np.array([sites[i]['capex_usd'] for i in eligible]);npv=np.array([sites[i]['npv_usd'] for i in eligible])
    def summarize(sel,pid,name,budget,**extra):
        chosen=[sites[i] for i in sel]
        return dict(id=pid,name=name,preset=None,selected_ids=[s['id'] for s in chosen],budget_usd=budget,**{k:float(sum(s[k] for s in chosen)) for k in ['capex_usd','npv_usd','annual_captured_m3','annual_sellable_mmbtu','annual_margin_usd']},exposure_benefit=float(source[0,sel].sum()*p['capture_fraction']),exposure_reduction_pct=float(source[0,sel].sum()*p['capture_fraction']/total[0]*100),assumption_version=p['assumption_version'],**extra)
    for scenario in scenarios:
        for plan in scenario['plans']:
            if not plan.get('disabled_reason'):plans.append({**plan,'budget_usd':scenario['budget_usd'],'objective_group':'population','origin':'existing'})
        for j,g in enumerate(GROUPS):
            chosen,info=portfolio.solve(cost,npv,source[j,eligible]*p['capture_fraction'],scenario['budget_usd'],limit=p['solver_time_limit_seconds'])
            pid=f"community-{int(scenario['budget_usd']/1e6)}m-{g}"
            plans.append(summarize(eligible[chosen],pid,{'population':'All residents','under5':'Under five','age65plus':'Age 65+'}[g],scenario['budget_usd'],objective_group=g,origin='age_objective',**info))
            objective_plans.append(dict(budget_usd=scenario['budget_usd'],group=g,plan_id=pid))
    season,weatherdefs=seasonal_sources(manifest,si,ci,weights[0],p)
    assert np.allclose(np.average(season,axis=0,weights=[d['hours'] for d in weatherdefs]),source[0],rtol=1e-10)
    robust=[]
    for scenario in scenarios:
        financial=next(x for x in scenario['plans'] if x['preset']=='Financial');floor=max(0,financial['npv_usd']*p['balanced_npv_retention'])
        norm=season[:,eligible]*p['capture_fraction']/season.sum(axis=1)[:,None]
        sel,info=robust_solve(cost,npv,norm,scenario['budget_usd'],floor,p['solver_time_limit_seconds'])
        plan=summarize(eligible[sel],f"robust-{int(scenario['budget_usd']/1e6)}m",'Seasonally robust',scenario['budget_usd'],objective_group='population',origin='robust',financial_reference_status=financial['solver_status'],**info)
        plan['seasonal_results']=[dict(scenario_id=d['id'],exposure_reduction_pct=float(norm[k,sel].sum()*100)) for k,d in enumerate(weatherdefs)]
        robust.append(plan);plans.append(plan)
    tractrows=[]
    for k,t in enumerate(tracts):
        prop=t['properties'];top=np.argsort(matrix[0,:,k])[::-1][:5]
        tractrows.append(dict(id=prop['geoid'],name=prop['name'],county=prop['county'],**{g:prop[g] for g in GROUPS},baseline={g:float(baseline[j,k]) for j,g in enumerate(GROUPS)},top_sources=[dict(id=ids[i],**{g:float(matrix[j,i,k]) for j,g in enumerate(GROUPS)}) for i in top if matrix[0,i,k]>0]))
    for plan in plans:
        selected=np.array([ididx[i] for i in plan['selected_ids']],dtype=int);red=matrix[:,selected,:].sum(axis=1)*p['capture_fraction']
        plan['regional']={g:metric(total[j],red[j].sum()) for j,g in enumerate(GROUPS)}
        plan['tract_results']=[dict(tract_id=t['id'],**{g:metric(baseline[j,k],red[j,k]) for j,g in enumerate(GROUPS)}) for k,t in enumerate(tractrows)]
        assert np.isclose(red[0].sum(),plan['exposure_benefit']) and np.all(red<=baseline+1e-8)
    save('community.json',dict(groups=GROUPS,tracts=tractrows,plans=plans,objective_plans=objective_plans,regional_baseline={g:float(total[j]) for j,g in enumerate(GROUPS)}))
    # Fixed installations under explicitly varied economic/weather scenarios.
    price=read(ROOT/'data/build/portfolios/site-economics.json')['benchmark_price_usd_per_mmbtu']
    econdefs=[dict(id=name,gas_price_usd_per_mmbtu=gas,capex_multiplier=mult) for name,gas,mult in [('benchmark',price,1),('price-low',1.5,1),('price-high',4.,1),('capex-low',price,.75),('capex-high',price,1.25)]]
    evaluations=[]
    for plan in plans:
        selected=[ididx[i] for i in plan['selected_ids']];w=[dict(scenario_id=d['id'],exposure_benefit=float(season[k,selected].sum()*p['capture_fraction']),exposure_reduction_pct=float(season[k,selected].sum()*p['capture_fraction']/season[k].sum()*100)) for k,d in enumerate(weatherdefs)]
        ev=[]
        for d in econdefs:
            es=[portfolio.economics(sites[i]['annual_flared_m3'],sites[i]['pipeline_distance_km'],d['gas_price_usd_per_mmbtu'],p,d['capex_multiplier']) for i in selected]
            row=dict(scenario_id=d['id'],**{k:float(sum(e[k] for e in es)) for k in ['capex_usd','npv_usd','annual_margin_usd']});row['budget_feasible']=row['capex_usd']<=plan['budget_usd']+.01;ev.append(row)
        evaluations.append(dict(plan_id=plan['id'],weather=w,economics=ev,weather_reduction_pct_range=[min(x['exposure_reduction_pct'] for x in w),max(x['exposure_reduction_pct'] for x in w)],npv_usd_range=[min(x['npv_usd'] for x in ev),max(x['npv_usd'] for x in ev)]))
    save('robustness.json',dict(weather_scenarios=weatherdefs,economic_scenarios=econdefs,fixed_plan_evaluations=evaluations,robust_plans=[{k:v for k,v in r.items() if k!='tract_results'} for r in robust],robust_objective='Maximize minimum seasonal fraction of baseline weighted index removed, under budget and >=95% annual Financial reference NPV. Seasons are distinct explicit weather slices, not probabilistic draws.',seasonal_source_benefits=dict(site_ids=ids,values=season.tolist())))
    checks=dict(source_tract_regional_conservation=True,allocated_age_counts_conserved=True,all_hours_seasons_reconcile_annual=True,selected_ids_unique_eligible=all(len(x['selected_ids'])==len(set(x['selected_ids'])) and all(sites[ididx[i]]['eligible_for_capture'] for i in x['selected_ids']) for x in plans),all_budgets_feasible=all(x['capex_usd']<=x['budget_usd']+.01 for x in plans),reductions_never_exceed_baseline=True)
    assert all(checks.values());save('validation.json',dict(checks=checks,all_passed=True,plan_count=len(plans),tract_count=len(tracts),total_seconds=time.perf_counter()-start));print(checks,flush=True)
if __name__=='__main__':main()
