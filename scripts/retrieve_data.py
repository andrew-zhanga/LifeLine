"""Download public data, retaining provenance and SHA-256. Python standard library only."""
import urllib.request, urllib.parse, json, hashlib, datetime, pathlib, concurrent.futures, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]/'data/verified'
RAW=ROOT/'raw'; RAW.mkdir(parents=True,exist_ok=True)
def fetch(name,url):
 p=RAW/name
 try:
  if not p.exists():
   try:
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=120) as r: body=r.read()
   except urllib.error.HTTPError as e:
    if e.code != 403: raise
    body=subprocess.check_output(['curl','-fsSL','--max-time','120','-A','Mozilla/5.0',url])
   if name.endswith('.json'): json.loads(body)
   p.write_bytes(body)
  body=p.read_bytes()
  out={'file':str(p.relative_to(ROOT)),'url':url,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'downloaded'}
 except Exception as e:out={'file':name,'url':url,'status':'failed','error':str(e)}
 print(name,out['status'],out.get('bytes',out.get('error')),flush=True)
 return out
jobs={
'wb_2024.xlsx':'https://thedocs.worldbank.org/en/doc/bd2432bbb0e514986f382f61b14b2608-0400072025/related/2012-2024-Flare-Volume-Estimates-by-individual-Flare-Location.xlsx',
'henry_hub_2023.csv':'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DHHNGSP&cosd=2023-01-01&coed=2023-12-31',
'places.zip':'https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_48_place_500k.zip',
'eog_2020.xlsx':'https://eogdata.mines.edu/global_flare_data/VIIRS_Global_flaring_d.7_slope_0.029353_2020_web_v1.xlsx',
'acs_b01001.dat':'https://www2.census.gov/programs-surveys/acs/summary_file/2023/table-based-SF/data/5YRData/acsdt5y2023-b01001.dat',
'census_tracts.zip':'https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_48_tract_500k.zip',
'acs_variables.json':'https://api.census.gov/data/2023/acs/acs5/groups/B01001.json',
'pipeline_metadata.json':'https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer/3?f=pjson',
}
q={'where':'1=1','geometry':'-100.5,27.25,-97.25,29.75','geometryType':'esriGeometryEnvelope','inSR':4326,'spatialRel':'esriSpatialRelIntersects','outFields':'*','outSR':4326,'f':'geojson','resultRecordCount':2000}
jobs['pipelines.json']='https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer/3/query?'+urllib.parse.urlencode(q)
q['f']='json'; q['returnCountOnly']='true'
jobs['pipeline_count.json']='https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer/3/query?'+urllib.parse.urlencode(q)
for lat in [27.75,28.5,29.25]:
 for lon in [-100,-99,-98]:
  q={'latitude':lat,'longitude':lon,'start_date':'2023-01-01','end_date':'2023-12-31','hourly':'wind_speed_10m,wind_direction_10m,wind_speed_100m,wind_direction_100m','models':'era5','wind_speed_unit':'ms','timezone':'GMT'}
  jobs[f'weather_{lat}_{lon}.json']='https://archive-api.open-meteo.com/v1/archive?'+urllib.parse.urlencode(q)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:results=list(ex.map(lambda kv:fetch(*kv),jobs.items()))
(ROOT/'download_manifest.json').write_text(json.dumps(results,indent=2))
