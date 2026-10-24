"""Descriptive inventory summaries only; no inferred global economics."""
from pathlib import Path
import json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/'data/verified/processed/flares_global_2023.geojson'
OUT=ROOT/'data/build/community/global-inventory.json'

def geometry_summary(coords,weights):
    a=np.deg2rad(np.asarray(coords));w=np.asarray(weights);lon,lat=a.T
    xyz=np.column_stack([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)])
    center=np.average(xyz,axis=0,weights=w)
    if np.linalg.norm(center)<1e-12:
        # Explicit deterministic fallback for nearly antipodal inventory distributions.
        lng,latitude=coords[int(np.argmax(w))]
    else:
        lng,latitude=np.rad2deg([np.arctan2(center[1],center[0]),np.arctan2(center[2],np.hypot(center[0],center[1]))])
    longs=np.sort(np.mod(np.asarray(coords)[:,0],360));gaps=np.diff(np.r_[longs,longs[0]+360]);gap=int(np.argmax(gaps));west=float(longs[(gap+1)%len(longs)]);width=float(360-gaps[gap]);west=(west+180)%360-180
    return [float(lng),float(latitude)],[west,float(np.min(np.asarray(coords)[:,1])),west+width,float(np.max(np.asarray(coords)[:,1]))]

def main():
    fs=json.loads(INPUT.read_text())['features'];groups={}
    for f in fs:groups.setdefault(f['properties']['country'],[]).append(f)
    rows=[]
    for country,features in groups.items():
        coords=[f['geometry']['coordinates'] for f in features];weights=[f['properties']['annual_flared_m3'] for f in features];center,bounds=geometry_summary(coords,weights)
        top=sorted(features,key=lambda f:(-f['properties']['annual_flared_m3'],f['properties']['id']))[:5]
        rows.append(dict(id=country,country=country,site_count=len(features),annual_flared_m3=float(sum(weights)),center=center,bounds=bounds,top_sites=[dict(id=f['properties']['id'],longitude=f['geometry']['coordinates'][0],latitude=f['geometry']['coordinates'][1],annual_flared_m3=f['properties']['annual_flared_m3']) for f in top],available_analysis=dict(inventory=True,annual_screening=False,economics=False),analysis_region_ids=['texas-eagle-ford'] if country=='United States' else []))
    rows.sort(key=lambda r:(-r['annual_flared_m3'],r['country']))
    data=dict(schema_version='1.0',model_version='inventory-summary-v1',provenance=[dict(path=str(INPUT.relative_to(ROOT)),sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest())],year=2023,units=dict(annual_flared_m3='m3/year',center='longitude, latitude degrees',bounds='west,south,east,north degrees; smallest longitude arc, east may exceed 180'),assumptions=['Center is flared-volume-weighted spherical mean of source locations, not national geographic centroid.','Counts and totals cover positive-volume prepared inventory records only.'],limitations=['Satellite-estimated gas volume; not measured emissions, recoverable gas or financial value.','Country sorting is inventory volume, not investment ranking.','Only the Texas study box has annual screening, demographic attribution and screening economic scenarios.'],site_count=len(fs),country_count=len(rows),annual_flared_m3=sum(f['properties']['annual_flared_m3'] for f in fs),countries=rows,regions=[dict(id='texas-eagle-ford',name='South Texas / Eagle Ford study box',country='United States',bounds=[-100.2,27.5,-97.5,29.5],center=[-98.85,28.5],candidate_site_count=392,buffer_site_count=30,available_analysis=dict(inventory=True,annual_screening=True,economics=True),model_version='screening-v1',note='Study bounding box, not an official basin boundary; assumed economics, no measured connection costs.')])
    assert sum(r['site_count'] for r in rows)==len(fs)
    assert np.isclose(sum(r['annual_flared_m3'] for r in rows),data['annual_flared_m3'])
    OUT.write_text(json.dumps(data,separators=(',',':'),allow_nan=False)+'\n');print({'countries':len(rows),'sites':len(fs),'bytes':OUT.stat().st_size})
if __name__=='__main__':main()
