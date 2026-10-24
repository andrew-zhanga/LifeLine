#!/usr/bin/env python3
"""Validate worker artifacts and emit compact, entirely local browser assets."""
from pathlib import Path
import copy, gzip, hashlib, json, subprocess
import numpy as np
from pyproj import Transformer
from scipy.spatial import cKDTree
from shapely.geometry import shape
from shapely.ops import transform

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data/verified/processed'
A = ROOT / 'data/build/exposure'
B = ROOT / 'data/build/portfolios'
OUT = ROOT / 'demo/public/data'
META = {'schema_version': '1.0', 'model_version': 'screening-v1'}

def read(path):
    return json.loads(path.read_text())

def write(name, data):
    target = OUT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, separators=(',', ':'), allow_nan=False) + '\n')
    return '/data/' + name

def compact(v):
    # Six significant digits; relative rounding <= 5e-6, full precision remains in numerical artifacts.
    return json.loads(json.dumps(np.asarray(v).tolist()), parse_float=lambda x: float(format(float(x), '.6g')))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    params = read(ROOT / 'contracts/parameters.json')
    manifest = read(A / 'exposure-manifest.json')
    annual = read(A / 'annual-baseline.json')
    econ = read(B / 'site-economics.json')
    scenarios = read(B / 'scenarios.json')
    sites = read(INPUT / 'flares_regional_2023.geojson')
    cells = read(INPUT / 'population_grid.geojson')
    receptors = read(INPUT / 'population_receptors.geojson')
    tracts = read(INPUT / 'population_tracts.geojson')
    communities = read(INPUT / 'communities.geojson')
    cell_ids = [f['properties']['id'] for f in cells['features']]
    site_ids = [f['properties']['id'] for f in sites['features']]
    assert cell_ids == manifest['cell_ids'] == annual['cell_ids']
    assert site_ids == manifest['site_ids']
    population = np.array([f['properties']['population'] for f in cells['features']])
    base_annual = np.array(annual['values'])
    base_replay = np.load(A / 'replay-baseline.npz')['values']
    ac = np.load(A / 'annual-source-contributions.npz')
    rc = np.load(A / 'replay-source-contributions.npz')
    assert base_replay.shape == (48, len(cell_ids))
    assert len(manifest['replay_hours_utc']) == 48
    assert np.isfinite(base_replay).all() and (base_replay >= 0).all()
    recon = np.bincount(ac['cell_index'], weights=ac['values'], minlength=len(cell_ids))
    assert np.allclose(recon, base_annual, rtol=1e-5, atol=1e-5)
    eligible = {f['properties']['id'] for f in sites['features'] if f['properties']['eligible_for_capture']}
    by_econ = {s['id']: s for s in econ['sites']}
    project = Transformer.from_crs(4326, 32614, always_xy=True).transform
    points = np.array([project(*f['geometry']['coordinates']) for f in receptors['features']])
    tree = cKDTree(points)
    for i, f in enumerate(cells['features']):
        p = f['properties']; area = transform(project, shape(f['geometry'])).area / 1e6
        p.update(index=i, density_per_km2=p['population']/area if area else 0,
                 under5_share=p['under5']/p['population'] if p['population'] else 0,
                 age65plus_share=p['age65plus']/p['population'] if p['population'] else 0)
    for f in communities['features']:
        center = shape(f['geometry']).representative_point()
        _, idx = tree.query(project(center.x, center.y))
        f['properties'].update(lng=center.x, lat=center.y, nearest_cell_index=int(idx),
            exposure_basis='Nearest modeled cell proxy; not community-average exposure')
    baseline = dict(META, cell_ids=cell_ids, annual=compact(base_annual), replay=compact(base_replay),
        annual_population_weighted_index=float(base_annual @ population),
        replay_population_weighted_index=compact(base_replay @ population))
    urls = {}
    for name, data in [('global',read(INPUT/'flares_global_2023.geojson')),('sites',sites),('cells',cells),
                       ('tracts',tracts),('communities',communities),('pipelines',read(INPUT/'pipelines.geojson'))]:
        urls[name] = write(name+'.geojson',data)
    urls['baseline'] = write('baseline.json',baseline)
    urls['economics'] = write('economics.json',econ)
    raw_weather = read(INPUT/'weather_2023.json')
    times = manifest['replay_hours_utc']
    weather_locations = []
    for loc in raw_weather['locations']:
        lookup = {t+':00Z':i for i,t in enumerate(loc['hourly']['time'])}
        indices = [lookup[t] for t in times]
        weather_locations.append({k:loc[k] for k in ['id','longitude','latitude']} | {
            'speed_mps':[loc['hourly']['wind_speed_100m'][i] for i in indices],
            'direction_from_deg':[loc['hourly']['wind_direction_100m'][i] for i in indices]})
    assignments = manifest['site_weather_ids']
    if isinstance(assignments,list): assignments = dict(zip(site_ids, assignments))
    urls['weather'] = write('weather.json',dict(META,locations=weather_locations,site_weather_ids=assignments,replay_hours_utc=times))
    checks = []; plan_ids = set()
    for scenario in scenarios['scenarios']:
        for plan in scenario['plans']:
            if plan.get('disabled_reason'): continue
            assert plan['id'] not in plan_ids
            plan_ids.add(plan['id'])
            chosen = plan['selected_ids']; assert len(chosen) == len(set(chosen))
            assert set(chosen) <= eligible
            for field in ['capex_usd','npv_usd','annual_captured_m3','annual_sellable_mmbtu','annual_margin_usd']:
                actual = sum(by_econ[s][field] for s in chosen)
                assert np.isclose(actual,plan[field],rtol=1e-7,atol=.02), (plan['id'],field,actual,plan[field])
            assert plan['capex_usd'] <= scenario['budget_usd'] + .01
            selected_indices = [site_ids.index(s) for s in chosen]
            mask_a = np.isin(ac['site_index'],selected_indices)
            mask_r = np.isin(rc['site_index'],selected_indices)
            removed_a = np.bincount(ac['cell_index'][mask_a],weights=ac['values'][mask_a],minlength=len(cell_ids))*params['capture_fraction']
            removed_r = np.array([np.bincount(rc['cell_index'][mask_r],weights=v[mask_r],minlength=len(cell_ids)) for v in rc['values']])*params['capture_fraction']
            residual_a = base_annual - removed_a; residual_r = base_replay - removed_r
            assert residual_a.min() >= -1e-4 and residual_r.min() >= -1e-3
            residual_a = np.maximum(0,residual_a); residual_r = np.maximum(0,residual_r)
            assert (residual_a <= base_annual + 1e-5).all() and (residual_r <= base_replay + 1e-5).all()
            reduction = 100*float(removed_a @ population)/baseline['annual_population_weighted_index']
            assert np.isclose(reduction,plan['exposure_reduction_pct'],rtol=1e-5,atol=1e-4), (reduction,plan)
            residual = dict(META, plan_id=plan['id'],cell_ids=cell_ids,annual=compact(residual_a),replay=compact(residual_r),
                annual_population_weighted_index=float(residual_a @ population),replay_population_weighted_index=compact(residual_r @ population))
            plan['residual_url'] = write('plans/'+plan['id']+'.json',residual)
            checks.append({'plan_id':plan['id'],'budget_feasible':True,'totals_match':True,'monotonic_all_frames':True,'reduction_pct':reduction})
    urls['scenarios'] = write('scenarios.json',scenarios)
    positive = np.concatenate([base_annual, base_replay.flatten()]); positive = positive[positive>0]
    breaks = [0]+[float(x) for x in np.quantile(positive,[.25,.5,.75,.9,.98,1])]
    default = next(s for s in scenarios['scenarios'] if s['budget_usd']==5000000)
    default_plan = next(p for p in default['plans'] if p.get('preset')=='Financial')
    sources = [
        {'name':'World Bank 2023 flare inventory','url':'https://www.worldbank.org/en/programs/gasflaringreduction/global-flaring-data','note':'VIIRS-derived annual gas estimates; uniform hourly activity assumption.'},
        {'name':'ERA5 via Open-Meteo','url':'https://open-meteo.com/en/docs/historical-weather-api','note':'Nine returned grid locations, 100 m winds; 8,760 UTC hours.'},
        {'name':'US Census ACS 2019–2023','url':'https://www2.census.gov/programs-surveys/acs/summary_file/2023/table-based-SF/data/5YRData/','note':'763 tracts; 5 km uniform area allocation conserves population. Places overlap tracts.'},
        {'name':'EIA/NETL pipeline geometry','url':'https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer/3','note':'Distance proxy only; no confirmed access or capacity.'},
        {'name':'EIA Henry Hub via FRED','url':'https://fred.stlouisfed.org/series/DHHNGSP','note':'249 observed 2023 daily prices; benchmark, not site netback.'}]
    app = dict(META,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        years={'flares':2023,'weather':2023,'population':'2019–2023'},units={'money':'USD','gas':'m³/year','exposure':'relative screening index','wind':'m/s'},
        sources=sources, assumptions=read(B/'assumptions.json'), analysis_coverage=manifest['analysis_coverage'],
        default_scenario_id=default['id'],default_plan_id=default_plan['id'],replay_hours_utc=times,fixed_legend_breaks=breaks,asset_urls=urls,
        bbox=[-100.2,27.5,-97.5,29.5], parameters=params,
        limitations=read(INPUT/'validation_report.json')['limitations'],
        rounding='Browser arrays six significant digits; numerical artifacts retain full precision.')
    write('manifest.json',app)
    sizes = [{'path':str(f.relative_to(OUT)),'bytes':f.stat().st_size,'gzip_bytes':len(gzip.compress(f.read_bytes())),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(OUT.rglob('*')) if f.is_file()]
    initial = sum(s['gzip_bytes'] for s in sizes if not s['path'].startswith('plans/'))
    max_plan = max(s['gzip_bytes'] for s in sizes if s['path'].startswith('plans/'))
    report = dict(META,checks=checks,plan_count=len(checks),cell_count=len(cell_ids),replay_hours=len(times),
        initial_analytical_gzip_bytes=initial,max_plan_gzip_bytes=max_plan,initial_under_5mb=initial<5e6,plans_under_10mb=max_plan<1e7,assets=sizes)
    (ROOT/'reports/assembly-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['assets','checks']},indent=2))

if __name__ == '__main__': main()
