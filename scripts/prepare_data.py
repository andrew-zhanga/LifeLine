"""Validate downloaded inputs and generate frontend-ready historical case-study fixtures.
Run with dependencies in scripts/data-requirements.txt. No network calls.
"""
import csv, io, json, math, zipfile, pathlib, statistics, datetime, collections
import openpyxl, shapefile
from shapely.geometry import shape, mapping, box, Point
from shapely.ops import transform
from pyproj import Transformer
ROOT=pathlib.Path(__file__).resolve().parents[1]/'data/verified'
RAW=ROOT/'raw'; OUT=ROOT/'processed'; OUT.mkdir(exist_ok=True)
CORE=(-100.2,27.5,-97.5,29.5)
BUFFER=(-100.5,27.25,-97.25,29.75)
core=box(*CORE); buffer=box(*BUFFER)
report={'study_bbox':CORE,'buffer_bbox':BUFFER,'checks':{},'limitations':[
 '2023 satellite-estimated annual flare volumes; not current operations or metered flow.',
 '2019–2023 ACS population is a five-year estimate, not a census on each playback date.',
 'Population is tract-level; the 5 km grid uses uniform area allocation, not observed residential locations.',
 'Nine sampled ERA5 cells are a coarse weather mesh, not street-level wind.',
 'Pipeline geometry is context only; availability, capacity, tie-in permission and costs unknown.',
 'Capture efficiency, installation cost, operating cost and project life remain scenario assumptions.',
 'Smoke-test exposure is a relative screening calculation, not concentration or health risk.'
]}
def dump(name,obj): (OUT/name).write_text(json.dumps(obj,separators=(',',':'),allow_nan=False))
def fc(features):return {'type':'FeatureCollection','features':features}
def feature(geom,props):return {'type':'Feature','geometry':geom,'properties':props}
def read_shapes(name):
 z=zipfile.ZipFile(RAW/name)
 def data(ext):return io.BytesIO(z.read(next(n for n in z.namelist() if n.endswith(ext))))
 r=shapefile.Reader(shp=data('.shp'),shx=data('.shx'),dbf=data('.dbf'))
 # Census cartographic boundaries declare NAD83. Transform explicitly to web-map WGS84.
 project=Transformer.from_crs('EPSG:4269','EPSG:4326',always_xy=True).transform
 for sr in r.iterShapeRecords():
  if not box(*sr.shape.bbox).intersects(buffer): continue
  g=transform(project,shape(sr.shape.__geo_interface__))
  assert g.is_valid and not g.is_empty
  yield sr.record.as_dict(),g
# Flare sheet contains annual site records, not monthly observations.
w=openpyxl.load_workbook(RAW/'wb_2024.xlsx',read_only=True,data_only=True)
global_f=[]; regional=[]; excluded=0; volume_discrepancies=[]
for idx,row in enumerate(w.active.values):
 country,lat,lon,bcm,mmscfd,year,kind,field,operator,location,level,million_m3=row
 if year!=2023:continue
 if not all(isinstance(x,(int,float)) and math.isfinite(x) for x in [lat,lon,bcm]):excluded+=1;continue
 assert -90<=lat<=90 and -180<=lon<=180 and bcm>=0
 if bcm==0:excluded+=1;continue
 assert isinstance(million_m3,(int,float)) and million_m3>0
 if not math.isclose(bcm*1000,million_m3,rel_tol=1e-5,abs_tol=1e-6):
  volume_discrepancies.append({'row':idx+1,'country':country,'bcm_raw':bcm,'million_m3_raw':million_m3,'relative_difference':abs(bcm*1000-million_m3)/million_m3})
 assert math.isclose(million_m3*35.3146667/365,mmscfd,rel_tol=.001,abs_tol=1e-6),('MMscfd mismatch',idx+1)
 raw_bcm=bcm; bcm=million_m3/1000
 p={'id':f'wb-2023-row-{idx+1}','country':country,'year':2023,'annual_flared_bcm':bcm,'raw_workbook_bcm':raw_bcm,'annual_flared_m3':bcm*1e9,'source_type':kind,'field_name':field,'operator':operator,'location':location,'volume_basis':'satellite estimate','source_workbook_row':idx+1}
 f=feature({'type':'Point','coordinates':[lon,lat]},p)
 global_f.append(f)
 if buffer.covers(Point(lon,lat)):
  p=p.copy();p['eligible_for_capture']=core.covers(Point(lon,lat));regional.append(feature(f['geometry'],p))
assert len({f['properties']['id'] for f in global_f})==len(global_f)
assert len({tuple(f['geometry']['coordinates']) for f in regional})==len(regional)
dump('flares_global_2023.geojson',fc(global_f));dump('flares_regional_2023.geojson',fc(regional))
report['flares']={'global_positive_volume_sites':len(global_f),'core_sites':sum(f['properties']['eligible_for_capture'] for f in regional),'buffer_inclusive_sites':len(regional),'excluded_nonpositive_or_invalid':excluded,'core_annual_bcm':sum(f['properties']['annual_flared_bcm'] for f in regional if f['properties']['eligible_for_capture'])}
report['volume_column_audit']={'discrepant_global_rows':len(volume_discrepancies),'examples':volume_discrepancies[:5],'canonical_column':'Flaring Vol (million m3)','normalization':'m3 = million_m3 * 1e6; bcm = million_m3 / 1000','cross_check':'MMscfd consistent within 0.1%; raw bcm can be rounded'}
# Retain complete intersecting tracts; clipping geometry while retaining population would overstate density.
tracts={p['GEOID']:(p,g) for p,g in read_shapes('census_tracts.zip') if g.intersects(buffer)}
acs={}; places_acs={}
with (RAW/'acs_b01001.dat').open() as f:
 for r in csv.DictReader(f,delimiter='|'):
  geoid=r['GEO_ID']
  if (geoid.startswith('1400000US') and geoid[9:] in tracts) or geoid.startswith('1600000US48'):
   def e(n):return int(r[f'B01001_E{n:03}'])
   vals=[e(n) for n in range(1,50)]
   assert min(vals)>=0,('ACS suppression sentinel',geoid)
   total=e(1);child=e(3)+e(27);senior=sum(e(n) for n in [20,21,22,23,24,25,44,45,46,47,48,49])
   assert total==e(2)+e(26) and total==sum(e(n) for n in list(range(3,26))+list(range(27,50)))
   assert child+senior<=total
   p={'population':total,'under5':child,'age65plus':senior,'under5_share':child/total if total else 0,'age65plus_share':senior/total if total else 0,'population_moe':int(r['B01001_M001']),'acs_period':'2019–2023','age_basis':'B01001 sex-by-age counts'}
   (acs if geoid.startswith('140') else places_acs)[geoid[9:]]=p
missing=set(tracts)-set(acs);assert not missing,missing
tract_features=[];receptors=[]
for geoid,(p,g) in tracts.items():
 pop=acs[geoid];pt=g.representative_point()
 props={'geoid':geoid,'name':p['NAMELSAD'],'county':p['NAMELSADCO'],'land_area_m2':p['ALAND'],'density_per_land_km2':pop['population']/(p['ALAND']/1e6) if p['ALAND'] else 0,**pop}
 tract_features.append(feature(mapping(g),props))
 receptors.append(feature(mapping(pt),props))
dump('population_tracts.geojson',fc(tract_features));dump('population_tract_points.geojson',fc(receptors))
# Area-weighted 5 km cells eliminate giant-tract single-point gaps without inventing census precision.
to_m=Transformer.from_crs(4326,32614,always_xy=True).transform
to_ll=Transformer.from_crs(32614,4326,always_xy=True).transform
receptors=[];grid=[]
for f in tract_features:
 g=transform(to_m,shape(f['geometry'])); minx,miny,maxx,maxy=g.bounds
 parts=[]
 for x in range(math.floor(minx/5000)*5000,math.ceil(maxx/5000)*5000,5000):
  for y in range(math.floor(miny/5000)*5000,math.ceil(maxy/5000)*5000,5000):
   cut=g.intersection(box(x,y,x+5000,y+5000))
   if cut.area>0:parts.append(cut)
 area=sum(p.area for p in parts);assert math.isclose(area,g.area,rel_tol=1e-8)
 props=f['properties']; allocated=0
 for j,part in enumerate(parts):
  share=part.area/area
  q={'id':props['geoid']+'-'+str(j),'geoid':props['geoid'],'population':props['population']*share,'under5':props['under5']*share,'age65plus':props['age65plus']*share,'allocation':'uniform tract area; modeled, not measured cell population'}
  allocated+=q['population']
  grid.append(feature(mapping(transform(to_ll,part)),q))
  receptors.append(feature(mapping(transform(to_ll,part.representative_point())),q))
 assert math.isclose(allocated,props['population'],rel_tol=1e-9,abs_tol=1e-7)
dump('population_grid.geojson',fc(grid));dump('population_receptors.geojson',fc(receptors))
towns=[]
for p,g in read_shapes('places.zip'):
 if g.intersects(core) and p['GEOID'] in places_acs:
  towns.append(feature(mapping(g.representative_point()),{'geoid':p['GEOID'],'name':p['NAME'],**places_acs[p['GEOID']]}))
dump('communities.geojson',fc(towns))
report['population']={'tracts':len(tracts),'matched':len(acs),'missing':len(missing),'population_full_intersecting_tracts':sum(p['population'] for p in acs.values()),'communities':len(towns),'zero_population_tracts':sum(p['population']==0 for p in acs.values()),'area_weighted_grid_cells':len(grid),'allocated_population':sum(f['properties']['population'] for f in receptors),'allocation_conserves_tract_totals':True}
# Preserve source time axes and locations returned by ERA5 (not just requested coordinates).
weather=[];stats=[]
for p in sorted(RAW.glob('weather_*.json')):
 d=json.loads(p.read_text());h=d['hourly'];n=len(h['time']);assert n==8760 # non-leap year
 times=[datetime.datetime.fromisoformat(t) for t in h['time']]
 assert times[0]==datetime.datetime(2023,1,1) and times[-1]==datetime.datetime(2023,12,31,23)
 assert all((b-a).total_seconds()==3600 for a,b in zip(times,times[1:]))
 assert d['utc_offset_seconds']==0
 for k,v in h.items():
  assert len(v)==n
  if k=='time':continue
  assert all(isinstance(x,(int,float)) and math.isfinite(x) for x in v)
  assert min(v)>=0
  if 'direction' in k:assert max(v)<=360 and d['hourly_units'][k]=='°'
  else:assert d['hourly_units'][k]=='m/s'
 lon=d['longitude'];lat=d['latitude']
 weather.append({'id':p.stem,'longitude':lon,'latitude':lat,'hourly':h,'units':d['hourly_units']})
 stats.append({'id':p.stem,'returned_coordinates':[lon,lat],'hours':n,'speed100m_min':min(h['wind_speed_100m']),'speed100m_max':max(h['wind_speed_100m']),'mean_speed100m':statistics.mean(h['wind_speed_100m']),'calm_hours_below_0_5ms':sum(v<0.5 for v in h['wind_speed_100m']),'direction_bins_45deg':len({int(v%360//45) for v in h['wind_direction_100m']})})
assert len(weather)==9
assert len({(x['longitude'],x['latitude']) for x in weather})==9
# Meteorological direction is where wind comes FROM. Transport vectors point the opposite way.
def windvector(speed,degrees):return -speed*math.sin(math.radians(degrees)),-speed*math.cos(math.radians(degrees))
assert windvector(1,0)[1]==-1 and abs(windvector(1,90)[0]+1)<1e-10
assert abs(windvector(1,180)[1]-1)<1e-10 and abs(windvector(1,270)[0]-1)<1e-10
dump('weather_2023.json',{'model':'ERA5','timezone':'UTC','direction_convention':'meteorological FROM; vector east=-speed*sin(direction), north=-speed*cos(direction)','locations':weather})
report['weather']={'locations':stats,'total_location_hours':sum(s['hours'] for s in stats),'missing_values':0}
# Pipeline completeness: compare feature download with server count, then crop for rendering.
pipes=json.loads((RAW/'pipelines.json').read_text())['features'];count=json.loads((RAW/'pipeline_count.json').read_text())['count']
assert len(pipes)==count
clipped=[]
for f in pipes:
 g=shape(f['geometry']);assert g.is_valid
 cut=g.intersection(buffer)
 if not cut.is_empty:clipped.append(feature(mapping(cut),f['properties']))
dump('pipelines.geojson',fc(clipped));report['pipelines']={'returned':len(pipes),'server_count':count,'clipped':len(clipped)}
prices=list(csv.DictReader((RAW/'henry_hub_2023.csv').open()));prices=[{'date':r['observation_date'],'usd_per_mmbtu':float(r['DHHNGSP'])} for r in prices if r['DHHNGSP'] not in ['', '.']]
assert len(prices)>200 and all(p['usd_per_mmbtu']>0 for p in prices)
dump('gas_price_2023.json',{'series':'DHHNGSP','basis':'Henry Hub spot benchmark; not site netback','observations':prices,'mean_observed_daily_usd_per_mmbtu':statistics.mean(p['usd_per_mmbtu'] for p in prices)})
report['gas_price']={'observations':len(prices),'mean_observed_daily_usd_per_mmbtu':statistics.mean(p['usd_per_mmbtu'] for p in prices)}
# Smoke-test a minimal data flow, not the eventual dispersion model. Same sites/people/hour before/after.
# Area-weighted population receptors retain tract totals; quantify spatial coverage.
project=Transformer.from_crs('EPSG:4326','EPSG:32614',always_xy=True).transform
xy=[project(*f['geometry']['coordinates']) for f in regional]
rxy=[project(*f['geometry']['coordinates']) for f in receptors]
near=[min(math.dist(a,b) for b in rxy)/1000 for a in xy]
report['spatial']={'sites_with_representative_receptor_within_30km':sum(d<=30 for d in near),'sites_total':len(near),'max_nearest_receptor_km':max(near)}
links=[]
for i,(f,a) in enumerate(zip(regional,xy)):
 lng,lat=f['geometry']['coordinates']
 wi=min(range(len(weather)),key=lambda j:(weather[j]['longitude']-lng)**2*math.cos(math.radians(lat))**2+(weather[j]['latitude']-lat)**2)
 nearby=[(j,(b[0]-a[0])/1000,(b[1]-a[1])/1000) for j,b in enumerate(rxy) if math.dist(a,b)<=30000]
 links.append((i,wi,nearby))
selected=set(sorted([i for i,f in enumerate(regional) if f['properties']['eligible_for_capture']],key=lambda i:regional[i]['properties']['annual_flared_m3'],reverse=True)[:20])
def exposure(hour,efficiency):
 values=[0.]*len(receptors)
 for i,wi,nearby in links:
  h=weather[wi]['hourly'];speed=h['wind_speed_100m'][hour];theta=h['wind_direction_100m'][hour]
  east,north=windvector(1,theta)
  q=regional[i]['properties']['annual_flared_m3']/1e6*(1-efficiency if i in selected else 1)
  for j,dx,dy in nearby:
   along=dx*east+dy*north;cross=dx*north-dy*east
   if speed<0.5:weight=math.exp(-(dx*dx+dy*dy)/8) # explicit calm fallback
   elif along<=0:weight=0
   else:weight=math.exp(-0.5*(cross/(1+0.15*along))**2)*math.exp(-along/15)/(max(speed,0.5)*(1+along))
   values[j]+=q*weight
 return sum(v*f['properties']['population'] for v,f in zip(values,receptors))
samples=[]
for hour in range(0,8760,24):
 before=exposure(hour,0);after=exposure(hour,.9)
 assert 0<=after<=before+1e-8
 samples.append({'time':weather[0]['hourly']['time'][hour],'baseline_index':before,'capture_index':after})
assert max(x['baseline_index'] for x in samples)>min(x['baseline_index'] for x in samples)
assert sum(x['capture_index'] for x in samples)<sum(x['baseline_index'] for x in samples)
dump('integration_smoke_test.json',{'purpose':'Data-integration check only; not production model or optimized portfolio','selected_ids':[regional[i]['properties']['id'] for i in sorted(selected)],'capture_fraction_assumption':.9,'samples':samples})
report['integration']={'sampled_days':len(samples),'fixed_selected_sites':len(selected),'baseline_min':min(x['baseline_index'] for x in samples),'baseline_max':max(x['baseline_index'] for x in samples),'aggregate_reduction_pct':100*(1-sum(x['capture_index'] for x in samples)/sum(x['baseline_index'] for x in samples)),'all_after_values_at_or_below_baseline':True}
report['checks']={'unique_flare_ids':True,'population_join_complete':True,'age_counts_sum_to_population':True,'weather_hourly_axis_complete':True,'weather_units_and_ranges_valid':True,'wind_from_direction_cardinals':True,'pipeline_response_not_truncated':True,'before_after_monotonic':True}
dump('validation_report.json',report)
print(json.dumps(report,indent=2))
