"""Bounded, deterministic Gaussian puff transport of a flared-volume proxy.
No emission factors, chemistry, calibration, terrain or pollutant prediction.
"""
from pathlib import Path
import hashlib,json,time,resource,gzip,copy
import numpy as np
from pyproj import Transformer
from scipy.spatial import cKDTree

ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/'data/verified/processed'
OUT=ROOT/'data/build/transport'
VERSION='transport-puff-v1'


def load(path): return json.loads(path.read_text())
def xy(coords):
    c=np.asarray(coords); a,b=Transformer.from_crs(4326,32614,always_xy=True).transform(c[:,0],c[:,1]); return np.column_stack([a,b])
def wind_vectors(speed,direction):
    a=np.deg2rad(direction);return np.asarray(speed)*-np.sin(a),np.asarray(speed)*-np.cos(a)
def density_at_receptors(centers,sh,sv,receptors):
    """Ground-reflected 3-D Gaussian; each puff integrates to 1 above z=0."""
    delta=receptors[None,:,:]-centers[:,None,:]
    horizontal=np.exp(-np.sum(delta[:,:,:2]**2,axis=2)/(2*sh[:,None]**2))/(2*np.pi*sh[:,None]**2)
    vertical=(np.exp(-delta[:,:,2]**2/(2*sv[:,None]**2))+np.exp(-(receptors[None,:,2]+centers[:,None,2])**2/(2*sv[:,None]**2)))/(np.sqrt(2*np.pi)*sv[:,None])
    return horizontal*vertical


def inputs():
    sf=load(INPUT/'flares_regional_2023.geojson')['features'];cf=load(INPUT/'population_receptors.geojson')['features'];wf=load(INPUT/'weather_2023.json')['locations']
    benefit=load(ROOT/'data/build/exposure/site-benefits.json')['sites'];bs={r['id']:r['annual_population_weighted_index'] for r in benefit}
    eligible=[s for s in sf if s['properties']['eligible_for_capture']]
    eligible_xy=xy([s['geometry']['coordinates'] for s in eligible])
    neighborhoods=cKDTree(eligible_xy).query_ball_point(eligible_xy,12000)
    candidates=[i for i,near in enumerate(neighborhoods) if len(near)>=4]
    anchor_index=max(candidates,key=lambda i:(sum(bs[eligible[j]['properties']['id']] for j in neighborhoods[i]),eligible[i]['properties']['id']))
    anchor=eligible[anchor_index]
    origin=xy([anchor['geometry']['coordinates']])[0]
    ordered=sorted(eligible,key=lambda s:(float(np.linalg.norm(xy([s['geometry']['coordinates']])[0]-origin)),s['properties']['id']))
    chosen=[s for s in ordered if np.linalg.norm(xy([s['geometry']['coordinates']])[0]-origin)<=12000][:8]
    weather_xy=xy([[w['longitude'],w['latitude']] for w in wf]); sources=[]
    for s in chosen:
        coords=s['geometry']['coordinates'];projected=xy([coords])[0];local=projected-origin
        wi=int(cKDTree(weather_xy).query(projected)[1]);p=s['properties']
        sources.append({'id':p['id'],'longitude':coords[0],'latitude':coords[1],'x_m':float(local[0]),'y_m':float(local[1]),'z_m':60.,'annual_flared_m3':p['annual_flared_m3'],'rate_m3_per_s':p['annual_flared_m3']/(8760*3600),'weather_id':wf[wi]['id'],'weather_index':wi})
    receptor_xy=xy([c['geometry']['coordinates'] for c in cf])-origin
    nearby=[i for i,p in enumerate(receptor_xy) if np.linalg.norm(p)<=25000 and cf[i]['properties']['population']>0]
    # Include a populated near-source cell plus populous cells in each compass octant.
    picked={min(nearby,key=lambda i:np.linalg.norm(receptor_xy[i]))}
    for octant in range(8):
        group=[i for i in nearby if int(((np.arctan2(receptor_xy[i,1],receptor_xy[i,0])+np.pi)/(2*np.pi)*8))%8==octant]
        picked.update(sorted(group,key=lambda i:(-cf[i]['properties']['population'],cf[i]['properties']['id']))[:2])
    receptors=[]
    for i in sorted(picked):
        c=cf[i];p=c['properties'];coords=c['geometry']['coordinates']
        receptors.append({'id':p['id'],'longitude':coords[0],'latitude':coords[1],'x_m':float(receptor_xy[i,0]),'y_m':float(receptor_xy[i,1]),'z_m':0.,'population':p['population'],'geoid':p['geoid']})
    start='2023-12-10T20:00';times=wf[0]['hourly']['time'];start_index=times.index(start)
    vectors=[]
    for s in sources:
        w=wf[s['weather_index']]['hourly'];u,v=wind_vectors(np.array(w['wind_speed_100m']),np.array(w['wind_direction_100m']));vectors.append(np.column_stack([u[start_index:start_index+10],v[start_index:start_index+10]]))
    return sources,receptors,np.array(vectors),origin,anchor


def simulate(sources,receptors,vectors,dt=60,duration=28800,emission_interval=120,frame_interval=300,install=7200,capture_fraction=.9,rate_scale=1.,bounds=25000):
    """Midpoint advection; midpoint emission pulses preserve interval total mass."""
    nsource=len(sources); receptor_positions=np.array([[r['x_m'],r['y_m'],r['z_m']] for r in receptors])
    rates=np.array([s['rate_m3_per_s'] for s in sources])*rate_scale
    source_positions=np.array([[s['x_m'],s['y_m'],s['z_m']] for s in sources])
    def wind(t):
        h=t/3600;lo=int(np.floor(h));a=h-lo
        return vectors[:,lo]*(1-a)+vectors[:,lo+1]*a
    puffs=[];active=[];centers=np.empty((0,3));frames=[];series=[];captured=[];per_source=[];per_source_capture=[];budgets=[]
    exited=np.zeros(nsource);exited_capture=np.zeros(nsource)
    for t in range(0,duration+1,dt):
        if t>0 and len(active):
            si=np.array([puffs[i]['source_index'] for i in active]);centers[:,:2]+=wind(t-dt/2)[si]*dt
            inside=(np.abs(centers[:,0])<=bounds)&(np.abs(centers[:,1])<=bounds)
            for index in np.flatnonzero(~inside):
                puff=puffs[active[index]];exited[puff['source_index']]+=puff['mass_baseline'];exited_capture[puff['source_index']]+=puff['mass_capture']
            active=[i for i,keep in zip(active,inside) if keep];centers=centers[inside]
        if t<duration and t%emission_interval==emission_interval//2:
            for si,s in enumerate(sources):
                mass=float(rates[si]*emission_interval);capture=mass*(1-capture_fraction if t>=install else 1)
                i=len(puffs);puffs.append({'id':f"{s['id']}-t{t}",'source_index':si,'birth_elapsed_s':t,'mass_baseline':mass,'mass_capture':capture})
                active.append(i)
            centers=np.vstack([centers,source_positions])
        if t%frame_interval==0:
            age=np.array([t-puffs[i]['birth_elapsed_s'] for i in active]);sh=np.sqrt(80**2+2*120*age);sv=np.sqrt(20**2+2*5*age)
            weights=density_at_receptors(centers,sh,sv,receptor_positions)
            source_curves=np.zeros((nsource,len(receptors)));source_capture=np.zeros_like(source_curves)
            for k,i in enumerate(active):
                p=puffs[i];source_curves[p['source_index']]+=weights[k]*p['mass_baseline'];source_capture[p['source_index']]+=weights[k]*p['mass_capture']
            per_source.append(source_curves.tolist());per_source_capture.append(source_capture.tolist());series.append(source_curves.sum(axis=0).tolist());captured.append(source_capture.sum(axis=0).tolist())
            timestamp=str(np.datetime64('2023-12-10T20:00:00')+np.timedelta64(t,'s'))+'Z'
            frames.append({'timestamp_utc':timestamp,'elapsed_s':t,'puffs':[[i,*map(float,center),float(h),float(v)] for i,center,h,v in zip(active,centers,sh,sv)],'wind':[{'source_index':i,'east_mps':float(w[0]),'north_mps':float(w[1])} for i,w in enumerate(wind(t))]})
            emitted=np.array([sum(p['mass_baseline'] for p in puffs if p['source_index']==i) for i in range(nsource)])
            emitted_capture=np.array([sum(p['mass_capture'] for p in puffs if p['source_index']==i) for i in range(nsource)])
            remaining=np.array([sum(puffs[k]['mass_baseline'] for k in active if puffs[k]['source_index']==i) for i in range(nsource)])
            remaining_capture=np.array([sum(puffs[k]['mass_capture'] for k in active if puffs[k]['source_index']==i) for i in range(nsource)])
            budgets.append({'elapsed_s':t,'emitted':emitted.tolist(),'remaining':remaining.tolist(),'exited':exited.tolist(),'captured_at_source':(emitted-emitted_capture).tolist(),'capture_remaining':remaining_capture.tolist(),'capture_exited':exited_capture.tolist()})
    return {'puffs':puffs,'frames':frames,'receptor_series':{'baseline':series,'capture':captured,'baseline_per_source':per_source,'capture_per_source':per_source_capture},'mass_budget':budgets}


def build():
    begin=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    sources,receptors,vectors,origin,anchor=inputs()
    data=simulate(sources,receptors,vectors)
    paths=[INPUT/'flares_regional_2023.geojson',INPUT/'population_receptors.geojson',INPUT/'weather_2023.json',ROOT/'data/build/exposure/site-benefits.json']
    provenance=[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
    metadata={'schema_version':'1.0','model_version':VERSION,'provenance':provenance}
    scene={**metadata,'origin':{'longitude':anchor['geometry']['coordinates'][0],'latitude':anchor['geometry']['coordinates'][1],'crs':'EPSG:32614','x_m':float(origin[0]),'y_m':float(origin[1])},'coordinate_system':'local east/north/up metres; subtract projected origin from EPSG:32614 x/y','bounds':{'x_m':[-25000,25000],'y_m':[-25000,25000],'z_m':[0,2000]},'sources':sources,'receptors':receptors,'capture':{'fraction':.9,'install_time_utc':'2023-12-10T22:00:00Z','install_elapsed_s':7200,'source_ids':[s['id'] for s in sources]},'frame_interval_s':300,'duration_s':28800,'puff_state_columns':['puff_index','x_m','y_m','z_m','sigma_horizontal_m','sigma_vertical_m'],'units':{'position':'m','time':'s','wind':'m/s','mass_baseline':'m³ flared-gas volume proxy','mass_capture':'m³ flared-gas volume proxy','receptor_series':'m³ flared-gas proxy per m³ idealized model space; relative proxy, not pollutant concentration'},'selection':{'anchor_id':anchor['properties']['id'],'criterion':'Eligible-source neighborhood with highest sum screening-v1 annual population-weighted contribution among 12 km neighborhoods containing at least four sources; up to eight nearest sources to its center. Receptors: nearest populated cell and up to two most populous cells per compass octant within 25 km. Deliberately bounded subset, not regional population aggregate.'},'assumptions':{'advection_timestep_s':60,'emission_pulse_interval_s':120,'emission_pulse_timing':'midpoint of each 2-minute interval; each pulse contains its exact interval volume','source_rate':'2023 annual volume / (8760*3600), constant','source_release_height_m':60,'horizontal_diffusivity_m2_per_s':120,'vertical_diffusivity_m2_per_s':5,'initial_sigma_horizontal_m':80,'initial_sigma_vertical_m':20,'wind':'Actual 100 m ERA5; nearest returned location at source; linearly interpolate east/north vectors between hours, fixed weather assignment for each source','vertical':'Fixed release-height centers with Gaussian spreading and reflective ground; no plume rise','boundary':'When a puff center exits the ±25 km horizontal square, remove whole puff and account its mass as exited. Infinite Gaussian tails are not clipped. z bounds are display only.','initial_condition':'Empty at replay start; no upstream or prior-hour puff spinup','capture':'90% of newly emitted volume removed at source from installation time; all existing puff masses and trajectories persist','numerics':'Deterministic analytic Gaussian states; midpoint time integration; no stochastic seed or random particles in scientific data'},'limitations':['Distinct transport-puff-v1 model; does not reproduce or replace annual screening-v1 metrics.','Illustrative transport of a gas-volume proxy, not pollutant concentration, exposure or health risk; no emissions factors.','Diffusivities and 60 m release height are explicit assumptions, not measured or calibrated.','No terrain, building wakes, buoyancy, chemistry, deposition or spatially resolved wind; weather is coarse reanalysis.','Local projected axes approximate true east/north without grid-convergence correction.','Open-boundary removal approximates exit by puff center; Gaussian tails extend outside domain before removal.','Eight-hour, up-to-eight-source subset and selected cell receptor points; not complete regional exposure or community-average estimates.','Puff releases are deterministic 2-minute mass packets; changing this temporal discretization can change near-source curves.'],**copy.deepcopy(data)}
    write=lambda name,obj:(OUT/name).write_text(json.dumps(obj,separators=(',',':'),allow_nan=False)+'\n')
    # Export centimetre-precision geometry; report receptor reconstruction error.
    exported_curves=[]
    for f in scene['frames']:
        for row in f['puffs']:
            row[1:]=[round(value,2) for value in row[1:]]
        if f['puffs']:
            states=np.array(f['puffs']);positions=states[:,1:4];sh=states[:,4];sv=states[:,5]
            receptor_positions=np.array([[r['x_m'],r['y_m'],r['z_m']] for r in receptors])
            mass=np.array([scene['puffs'][int(i)]['mass_baseline'] for i in states[:,0]])
            exported_curves.append(mass @ density_at_receptors(positions,sh,sv,receptor_positions))
        else: exported_curves.append(np.zeros(len(receptors)))
    unrounded=np.array(data['receptor_series']['baseline'])
    export_error=float(np.abs(np.array(exported_curves)-unrounded).sum()/max(np.abs(unrounded).sum(),1e-30))
    scene['assumptions']['geometry_export_precision_m']=.01
    write('scene.json',scene)
    example=copy.deepcopy(scene)
    example['example_only']=True
    example['frames']=example['frames'][:2]
    keep=max((row[0] for f in example['frames'] for row in f['puffs']),default=-1)+1
    example['puffs']=example['puffs'][:keep]
    example['mass_budget']=example['mass_budget'][:2]
    example['receptor_series']={k:v[:2] for k,v in example['receptor_series'].items()}
    write('example.json',example)
    print(json.dumps({'scene_ready':True,'sources':len(sources),'receptors':len(receptors),'frames':len(data['frames']),'puffs':len(data['puffs']),'bytes':(OUT/'scene.json').stat().st_size}),flush=True)
    fine=simulate(sources,receptors,vectors,dt=30)
    base=np.array(data['receptor_series']['baseline']);finebase=np.array(fine['receptor_series']['baseline'])
    relative_l1=float(np.abs(base-finebase).sum()/max(np.abs(finebase).sum(),1e-30))
    position_differences=[]
    for coarse_frame,fine_frame in zip(data['frames'],fine['frames']):
        fine_positions={row[0]:row[1:4] for row in fine_frame['puffs']}
        position_differences.extend(np.linalg.norm(np.array(row[1:4])-fine_positions[row[0]]) for row in coarse_frame['puffs'] if row[0] in fine_positions)
    halfpulse=simulate(sources,receptors,vectors,dt=30,emission_interval=60)
    halfbase=np.array(halfpulse['receptor_series']['baseline'])
    pulse_error=float(np.abs(base-halfbase).sum()/max(np.abs(halfbase).sum(),1e-30))
    mass_error=max(abs(sum(b['emitted'])-sum(b['remaining'])-sum(b['exited'])) for b in data['mass_budget'])
    capture_error=max(abs(sum(b['emitted'])-sum(b['capture_remaining'])-sum(b['capture_exited'])-sum(b['captured_at_source'])) for b in data['mass_budget'])
    checks={'finite_nonnegative_receptor_proxy':bool(np.isfinite(base).all() and (base>=0).all()),'capture_does_not_increase_receptor_proxy':bool((np.array(data['receptor_series']['capture'])<=base+1e-20).all()),'preinstall_mass_unchanged':all(p['mass_baseline']==p['mass_capture'] for p in data['puffs'] if p['birth_elapsed_s']<7200),'mass_budget_baseline':mass_error<1e-7,'mass_budget_capture':capture_error<1e-7,'timestep_receptor_l1_under_one_percent':relative_l1<.01,'pulse_refinement_l1_under_five_percent':pulse_error<.05,'export_rounding_l1_under_point_one_percent':export_error<.001,'geometry_finite_bounded':all(np.isfinite(row[1:]).all() and abs(row[1])<=25000 and abs(row[2])<=25000 for f in data['frames'] for row in f['puffs'])}
    diag={**metadata,'assumptions':scene['assumptions'],'limitations':scene['limitations'],'checks':checks,'all_passed':all(checks.values()),'timestep_convergence':{'coarse_s':60,'fine_s':30,'receptor_relative_l1_error':relative_l1,'maximum_center_difference_m':max(position_differences),'note':'Linear hourly vector interpolation and midpoint advection are exact away from boundary exit; same source pulses in both runs. Does not test weather uncertainty.'},'emission_discretization_sensitivity':{'coarse_pulse_s':120,'fine_pulse_s':60,'receptor_relative_l1_difference':pulse_error,'note':'Difference in near-source/time-resolved proxy from finite emission pulses; reported sensitivity, not a calibrated error bound.'},'mass_budget_max_abs_error_m3':mass_error,'capture_mass_budget_max_abs_error_m3':capture_error,'scene_bytes':(OUT/'scene.json').stat().st_size,'scene_gzip_bytes':len(gzip.compress((OUT/'scene.json').read_bytes())),'export_geometry_receptor_relative_l1_error':export_error,'build_seconds':time.perf_counter()-begin,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'peak_rss_platform':'macOS','max_active_puffs':max(len(f['puffs']) for f in data['frames']),'proxy_min':float(base.min()),'proxy_max':float(base.max()),'frame_count':len(data['frames'])}
    write('diagnostics.json',diag);assert all(checks.values()),checks
    print(json.dumps(diag),flush=True)

if __name__=='__main__':build()
