"""Reproducible pipeline screening economics and binary budget portfolios.

Run .data-venv/bin/python scripts/portfolio/build.py [--economics-only].
No network access. Final portfolios require the exposure worker's final benefits.
"""
from pathlib import Path
import argparse
import hashlib
import json
import time
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint
from shapely.geometry import shape, box
from shapely.ops import transform
from shapely.strtree import STRtree
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'data/verified/processed'
OUT = ROOT / 'data/build/portfolios'
PARAMS = ROOT / 'contracts/parameters.json'


def read(path):
    return json.loads(path.read_text())


def envelope(**data):
    files = [PARAMS, INPUT/'flares_regional_2023.geojson', INPUT/'pipelines.geojson', INPUT/'gas_price_2023.json']
    return dict(schema_version='1.0', model_version='screening-v1', provenance=[{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files], **data)


def save(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/name).write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def economics(volume_m3, distance_km, price, p, capex_multiplier=1., decline=0.):
    captured = volume_m3*p['capture_fraction']
    recovered_mcf_day = captured*p['ft3_per_m3']/1000/365
    energy = captured*p['ft3_per_m3']/1000*p['heating_value_mmbtu_per_mcf']*p['sellable_fraction']
    capex = capex_multiplier*(p['capex_base_usd']+p['capex_per_pipeline_km_usd']*distance_km+p['capex_capacity_usd']*(recovered_mcf_day/p['capex_capacity_reference_mcf_day'])**p['capex_capacity_exponent'])
    fixed = p['annual_fixed_opex_fraction']*capex
    margin = energy*(price-p['variable_opex_usd_per_mmbtu'])-fixed
    cash = [energy*(1-decline)**(y-1)*(price-p['variable_opex_usd_per_mmbtu'])-fixed for y in range(1,p['life_years']+1)]
    npv = -capex+sum(v/(1+p['discount_rate'])**y for y,v in enumerate(cash,1))
    return dict(capex_usd=capex, annual_captured_m3=captured, annual_sellable_mmbtu=energy, annual_margin_usd=margin, npv_usd=npv, payback_years=capex/margin if margin>0 else None, payback_reason=None if margin>0 else 'Nonpositive annual operating margin; no finite simple payback.')


def prepare_economics(p):
    project = Transformer.from_crs('EPSG:4326','EPSG:32614',always_xy=True).transform
    lines = [transform(project,shape(f['geometry'])) for f in read(INPUT/'pipelines.geojson')['features']]
    tree = STRtree(lines)
    boundary = transform(project,box(-100.5,27.25,-97.25,29.75)).boundary
    gas = read(INPUT/'gas_price_2023.json')
    price = float(np.mean([v['usd_per_mmbtu'] for v in gas['observations']]))
    sites = []
    for f in read(INPUT/'flares_regional_2023.geojson')['features']:
        q = f['properties']; point = transform(project,shape(f['geometry']))
        distance = point.distance(lines[tree.nearest(point)])/1000
        edge = point.distance(boundary)/1000
        sites.append(dict(id=q['id'], eligible_for_capture=q['eligible_for_capture'], annual_flared_m3=q['annual_flared_m3'], pipeline_distance_km=distance, distance_to_data_boundary_km=edge, geometry_edge_effect_possible=distance>=edge, **economics(q['annual_flared_m3'],distance,price,p), price_scenarios={label:economics(q['annual_flared_m3'],distance,value,p) for label,value in [('low',1.5),('benchmark',price),('high',4.)]}))
    save('site-economics.json',envelope(benchmark_price_usd_per_mmbtu=price, assumption_version=p['assumption_version'], sites=sites))
    save('assumptions.json',envelope(assumption_version=p['assumption_version'], parameters=p, benchmark_price_usd_per_mmbtu=price, price_scenarios={'low':1.5,'benchmark':price,'high':4.}, units={'capex':'USD','npv':'USD over seven years','pipeline_distance':'km in EPSG:32614','annual_captured':'m3/year','annual_sellable':'MMBtu/year'}, basis={'benchmark_price':'Observed mean of 249 available 2023 Henry Hub daily prices; not site netback.', 'economic_coefficients':'All capture, sellable fraction, heating value, cost, lifetime and discount coefficients are explicit screening assumptions, not measured site composition or installation quotes.', 'pipeline_distance':'Nearest downloaded line segment; no evidence of feasible access, capacity, rights, or construction route. Geometry vintage is not established as 2023.', 'volume':'Satellite-estimated 2023 annual gas; constant annual baseline, not observed hourly operation.', 'payback':'Simple undiscounted capex / first-year positive margin; not a claim payback occurs within project life.', 'edge_effect':'Flag if nearest downloaded segment is farther than the clipped-data boundary. Unflagged distances exclude only clipping edge effects, not missing inventory.'}, edge_effect_possible_count=sum(s['geometry_edge_effect_possible'] for s in sites)))
    return sites, price


def solve(cost, npv, benefit, budget, objective='exposure', min_npv=None, limit=5):
    """Scaled binary MILP; return feasible incumbent with truthful solver status."""
    cost,npv,benefit = map(lambda x:np.asarray(x,dtype=float),(cost,npv,benefit))
    rows=[cost/1e6]; lower=[-np.inf]; upper=[budget/1e6]
    if min_npv is not None:
        scale=max(np.max(np.abs(npv)),1.)
        rows.append(npv/scale); lower.append(min_npv/scale); upper.append(np.inf)
    value=npv if objective=='financial' else benefit
    scale=max(np.max(np.abs(value)),1.)
    start=time.perf_counter()
    result=milp(-value/scale,integrality=np.ones(len(cost)),bounds=Bounds(0,1),constraints=LinearConstraint(np.array(rows),lower,upper),options={'time_limit':limit,'mip_rel_gap':0.000001})
    if result.x is None:
        raise RuntimeError(f'No feasible MILP incumbent: {result.message}')
    selected=np.flatnonzero(result.x>.5)
    assert cost[selected].sum()<=budget+0.01
    if min_npv is not None:
        assert npv[selected].sum()>=min_npv-max(0.01,abs(min_npv)*1e-7)
    gap=getattr(result,'mip_gap',None)
    return selected,dict(solver_status='optimal' if result.status==0 else 'feasible_best_found',solver_gap=float(gap) if gap is not None and np.isfinite(gap) else None,solve_seconds=time.perf_counter()-start,solver_message=result.message)


def dominates(a,b):
    return a['npv_usd']>=b['npv_usd']-0.01 and a['exposure_benefit']>=b['exposure_benefit']-1e-6 and (a['npv_usd']>b['npv_usd']+0.01 or a['exposure_benefit']>b['exposure_benefit']+1e-6)


def make_scenario(sites, benefits, baseline, budget, price, p, sid, capex_multiplier=1.,decline=0.,frontier=True):
    eligible=[s for s in sites if s['eligible_for_capture']]
    econ=[economics(s['annual_flared_m3'],s['pipeline_distance_km'],price,p,capex_multiplier,decline) for s in eligible]
    keys=['capex_usd','npv_usd','annual_captured_m3','annual_sellable_mmbtu','annual_margin_usd']
    arrays={k:np.array([e[k] for e in econ]) for k in keys}
    benefit=np.array([benefits[s['id']]*p['capture_fraction'] for s in eligible])
    def plan(name,preset=None,minimum=None,objective='exposure'):
        sel,info=solve(arrays['capex_usd'],arrays['npv_usd'],benefit,budget,objective,minimum,p['solver_time_limit_seconds'])
        reduction=float(benefit[sel].sum())
        return dict(id=sid+'-'+name.lower().replace(' ','-'),name=name,preset=preset,selected_ids=[eligible[i]['id'] for i in sel],**{k:float(a[sel].sum()) for k,a in arrays.items()},exposure_benefit=reduction,exposure_reduction_pct=100*reduction/baseline,assumption_version=p['assumption_version'],npv_floor_usd=minimum,**info)
    financial=plan('Financial','Financial',objective='financial')
    exposure=plan('Exposure','Exposure')
    if financial['npv_usd']>0:
        balanced=plan('Balanced','Balanced',financial['npv_usd']*p['balanced_npv_retention'])
    else:
        balanced=dict(id=sid+'-balanced',name='Balanced',preset='Balanced',selected_ids=[],disabled_reason='No positive Financial reference NPV exists at this budget and price.')
    plans=[financial,balanced,exposure]
    candidates=[]
    if frontier:
        # Epsilon-constrained exposure maxima at six intermediate NPV targets.
        for index,target in enumerate(np.linspace(exposure['npv_usd'],financial['npv_usd'],8)[1:-1]):
            candidates.append(plan(f'Frontier {index+1}',minimum=float(target)))
    unique=[]
    for candidate in candidates:
        if any(set(candidate['selected_ids'])==set(other['selected_ids']) for other in plans+unique):
            continue
        unique.append(candidate)
    enabled=[x for x in plans if not x.get('disabled_reason')]
    points=[x for x in enabled+unique if not any(dominates(y,x) for y in enabled+unique)]
    for x in plans+unique:
        x['on_sampled_frontier']=x in points
    # Drop dominated optional points; preserve named objective presets.
    plans+= [x for x in unique if x in points]
    return dict(id=sid,budget_usd=budget,gas_price_usd_per_mmbtu=price,plans=plans,default_plan_id=balanced['id'] if not balanced.get('disabled_reason') else financial['id'],frontier_note='Sampled nondominated feasible portfolios among exported candidates; not every mathematically possible frontier point.')


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--economics-only',action='store_true'); args=parser.parse_args()
    p=read(PARAMS); sites,price=prepare_economics(p)
    if args.economics_only:
        print(json.dumps({'sites':len(sites),'benchmark_price':price,'status':'economics ready'})); return
    path=ROOT/'data/build/exposure/site-benefits.json'
    exposure=read(path)
    assert exposure['schema_version']=='1.0' and exposure['model_version']=='screening-v1'
    assert {s['id'] for s in sites}=={s['id'] for s in exposure['sites']}
    eligibility={s['id']:s['eligible_for_capture'] for s in sites}
    assert all(s['eligible_for_capture']==eligibility[s['id']] for s in exposure['sites'])
    benefits={s['id']:s['annual_population_weighted_index'] for s in exposure['sites']}
    baseline=exposure['baseline_population_weighted_index']
    assert np.isclose(sum(benefits.values()),baseline,rtol=1e-8)
    scenarios=[make_scenario(sites,benefits,baseline,budget,price,p,f'budget-{int(budget/1e6)}m-benchmark') for budget in p['budgets_usd']]
    provenance={'exposure_benefits_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    save('scenarios.json',envelope(assumption_version=p['assumption_version'],**provenance,scenarios=scenarios))
    reference=next(s for s in scenarios if s['budget_usd']==5000000)
    ref=next(x for x in reference['plans'] if x['preset']=='Balanced' and not x.get('disabled_reason'))
    cases=[]
    for name,multiplier,capture,decline,scenario_price in [('capex-low',.75,.9,0,price),('capex-high',1.25,.9,0,price),('capture-50pct',1,.5,0,price),('capture-90pct',1,.9,0,price),('capture-100pct',1,1.,0,price),('annual-decline-15pct',1,.9,.15,price),('gas-price-low',1,.9,0,1.5),('gas-price-high',1,.9,0,4.)]:
        params={**p,'capture_fraction':capture}
        result=make_scenario(sites,benefits,baseline,5000000,scenario_price,params,'sensitivity-'+name,multiplier,decline,False)
        for plan in result['plans']:
            if plan.get('disabled_reason'): continue
            ref_plan=next(x for x in reference['plans'] if x['preset']==plan['preset'])
            a,b=set(plan['selected_ids']),set(ref_plan['selected_ids'])
            plan['selection_jaccard_vs_reference']=len(a&b)/len(a|b) if a|b else 1.
            plan['npv_change_usd_vs_reference']=plan['npv_usd']-ref_plan['npv_usd']
            plan['exposure_benefit_change_vs_reference']=plan['exposure_benefit']-ref_plan['exposure_benefit']
        cases.append(dict(name=name,capex_multiplier=multiplier,capture_fraction=capture,annual_gas_decline=decline,exposure_basis='Historical 2023 index; future decline affects discounted cashflows only.',**result))
    save('sensitivity.json',envelope(**provenance,reference_scenario_id=reference['id'],note='Bounded assumptions, not calibrated confidence intervals. Re-optimized at $5m. Decline affects future revenues; displayed exposure remains historical annual benefit.',cases=cases))
    checks=validate(sites,benefits,baseline,scenarios,p,price)
    save('validation.json',envelope(**provenance,checks=checks,scenario_count=len(scenarios),plan_count=sum(len(s['plans']) for s in scenarios),solve_seconds=sum(x.get('solve_seconds',0) for s in scenarios for x in s['plans']),default_balanced=ref))
    print(json.dumps({'checks':checks,'default_balanced':ref},indent=2))


def validate(sites,benefits,baseline,scenarios,p,price):
    lookup={s['id']:s for s in sites}
    for scenario in scenarios:
        for plan in scenario['plans']:
            if plan.get('disabled_reason'):continue
            ids=plan['selected_ids']; assert len(ids)==len(set(ids))
            assert all(lookup[i]['eligible_for_capture'] for i in ids)
            assert plan['capex_usd']<=scenario['budget_usd']+.01
            for key in ['capex_usd','npv_usd','annual_captured_m3','annual_sellable_mmbtu','annual_margin_usd']:
                assert np.isclose(plan[key],sum(lookup[i][key] for i in ids),atol=.01)
            assert np.isclose(plan['exposure_benefit'],sum(benefits[i]*p['capture_fraction'] for i in ids))
            assert 0<=plan['exposure_reduction_pct']<=100*p['capture_fraction']+1e-8
        frontier=[x for x in scenario['plans'] if x.get('on_sampled_frontier')]
        assert not any(dominates(a,b) for a in frontier for b in frontier)
        financial=next(x for x in scenario['plans'] if x['preset']=='Financial')
        balanced=next(x for x in scenario['plans'] if x['preset']=='Balanced')
        if not balanced.get('disabled_reason'):
            assert balanced['npv_usd']>=financial['npv_usd']*p['balanced_npv_retention']-.01
    return dict(unique_eligible_selections=True,budget_feasibility=True,recomputed_totals=True,capture_consistency=True,balanced_npv_retention=True,exported_frontier_nondominance=True,full_source_benefits_alignment=True)

if __name__=='__main__': main()
