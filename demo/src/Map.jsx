import React,{useEffect,useRef,useState} from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
maplibregl.setWorkerUrl(workerUrl);
const fc=features=>({type:'FeatureCollection',features});
const empty=fc([]);
export default function Map({data,region,mode,values,surface,layers,chosen,selected,hour,mapRef,onSelect,onError}) {
 const el=useRef(),[ready,setReady]=useState(false);
 useEffect(()=>{
 const m=new maplibregl.Map({container:el.current,style:{version:8,sources:{basemap:{type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,attribution:'© OpenStreetMap contributors',maxzoom:19}},layers:[{id:'ocean',type:'background',paint:{'background-color':'#102832'}},{id:'base',type:'raster',source:'basemap',paint:{'raster-saturation':-1,'raster-brightness-max':.28}}]},center:[-45,23],zoom:1.5,maxZoom:12,attributionControl:{compact:true}});
 mapRef.current=m;m.on('error',()=>onError(true));
 m.on('load',()=>{m.setProjection({type:'globe'});m.setSky({'sky-color':'#06121d','horizon-color':'#254953','fog-color':'#0a2432','sky-horizon-blend':.7,'horizon-fog-blend':.7,'fog-ground-blend':.6,'atmosphere-blend':['interpolate',['linear'],['zoom'],0,1,5,0]});
 for(const id of ['global','sites','cells','tracts','communities','pipelines','wind','boundary'])m.addSource(id,{type:'geojson',data:empty});
 m.addLayer({id:'tract-fill',type:'fill',source:'tracts',paint:{'fill-color':'#24454c','fill-opacity':.4}});
 m.addLayer({id:'tract-line',type:'line',source:'tracts',paint:{'line-color':'#668b90','line-width':.5,'line-opacity':.35}});
 m.addLayer({id:'tract-selected',type:'line',source:'tracts',filter:['==',['get','geoid'],''],paint:{'line-color':'#c9f7e4','line-width':2}});
 m.addLayer({id:'cells-fill',type:'fill',source:'cells',paint:{'fill-color':'#d8854f','fill-opacity':.55}});
 m.addLayer({id:'pipes-line',type:'line',source:'pipelines',paint:{'line-color':'#a1a8dc','line-width':1.5,'line-opacity':.6}});
 m.addLayer({id:'boundary-line',type:'line',source:'boundary',paint:{'line-color':'#8bb4b7','line-width':1.3,'line-dasharray':[4,3]}});
 m.addLayer({id:'global-glow',type:'circle',source:'global',paint:{'circle-radius':7,'circle-color':'#ff9f43','circle-blur':1,'circle-opacity':.35}});
 m.addLayer({id:'global-dots',type:'circle',source:'global',paint:{'circle-radius':1.7,'circle-color':'#ffd398'}});
 m.addLayer({id:'community-dots',type:'circle',source:'communities',paint:{'circle-radius':4,'circle-color':'#9acbd6','circle-stroke-width':1,'circle-stroke-color':'#102832'}});
 m.addLayer({id:'sites-dots',type:'circle',source:'sites',paint:{'circle-radius':['case',['get','inspected'],8,4],'circle-color':['case',['get','eligible_for_capture'],'#ffc078','#8a959e'],'circle-stroke-width':['case',['get','captured'],3,1],'circle-stroke-color':['case',['get','inspected'],'#ffffff',['get','captured'],'#6ee4b7','#493b2d']}});
 m.addLayer({id:'wind-lines',type:'line',source:'wind',paint:{'line-color':'#b0eef3','line-width':2,'line-opacity':.85}});
 m.on('click',e=>{const hits=m.queryRenderedFeatures(e.point,{layers:['sites-dots','community-dots','tract-fill']});if(!hits.length)return;const f=hits[0];onSelect({type:f.layer.id==='sites-dots'?'site':f.layer.id==='community-dots'?'community':'tract',id:f.properties.id??f.properties.geoid})});
 for(const id of ['sites-dots','community-dots']){m.on('mouseenter',id,()=>m.getCanvas().style.cursor='pointer');m.on('mouseleave',id,()=>m.getCanvas().style.cursor='')}
 setReady(true);
 });return()=>{m.remove();mapRef.current=null};
 },[]);
 useEffect(()=>{if(!ready||!data)return;const m=mapRef.current;for(const key of ['global','tracts','pipelines'])m.getSource(key).setData(data[key]);m.getSource('communities').setData(fc(data.communities.features.map(f=>({...f,geometry:f.geometry.type==='Point'?f.geometry:{type:'Point',coordinates:[f.properties.lng,f.properties.lat]}}))));m.getSource('boundary').setData(fc([{type:'Feature',properties:{},geometry:{type:'Polygon',coordinates:[[[-100.2,27.5],[-97.5,27.5],[-97.5,29.5],[-100.2,29.5],[-100.2,27.5]]]}}]));},[ready,data]);
 useEffect(()=>{if(!ready||!data)return;const m=mapRef.current;const property=surface==='Exposure'?'value':surface==='Population density'?'density_per_km2':surface==='Under 5 share'?'under5_share':'age65plus_share';
 m.getSource('cells').setData(fc(data.cells.features.map((f,i)=>({...f,properties:{...f.properties,value:values?.[i]??0}}))));
 const breaks=surface==='Exposure'?data.manifest.fixed_legend_breaks:surface==='Population density'?[1,10,100,1000]:[.05,.1,.2,.3];
 const colors=surface==='Exposure'?['#18383d','#70583d','#bc824e','#ed985d','#ffd29a']:['#163d50','#276176','#408b9b','#78bcc5','#c3eddf'];
 const stops=breaks.filter((v,i,a)=>v>0&&(i===0||v>a[i-1])).slice(0,4);
 m.setPaintProperty('cells-fill','fill-color',['step',['coalesce',['get',property],0],colors[0],...stops.flatMap((v,i)=>[v,colors[i+1]])]);
 m.setPaintProperty('cells-fill','fill-opacity',['case',['>', ['coalesce',['get',property],0],0],.6,0]);
 m.getSource('sites').setData(fc(data.sites.features.map(f=>({...f,properties:{...f.properties,captured:chosen.includes(f.properties.id)&&layers.Selections,inspected:selected?.type==='site'&&selected.id===f.properties.id}}))));
 const wind=[];if(hour!==null)for(const loc of data.weather.locations){const a=loc.direction_from_deg[hour]*Math.PI/180,s=loc.speed_mps[hour];if(!Number.isFinite(a)||!Number.isFinite(s)||s<.5)continue;const dx=-Math.sin(a)*.14,dy=-Math.cos(a)*.14,x=loc.longitude,y=loc.latitude,tip=[x+dx,y+dy];wind.push({type:'Feature',properties:{},geometry:{type:'MultiLineString',coordinates:[[[x,y],tip],[ [tip[0]-dx*.28-dy*.2,tip[1]-dy*.28+dx*.2],tip,[tip[0]-dx*.28+dy*.2,tip[1]-dy*.28-dx*.2]]]}})}m.getSource('wind').setData(fc(wind));
 m.setFilter('tract-selected',['==',['get','geoid'],selected?.type==='tract'?selected.id:'']);
 const vis=(ids,v)=>ids.forEach(id=>m.setLayoutProperty(id,'visibility',v?'visible':'none'));
 vis(['base'],layers.Basemap);vis(['global-glow','global-dots'],!region);vis(['tract-fill','tract-line','tract-selected','boundary-line'],region);vis(['cells-fill'],region&&mode!=='Explore');vis(['sites-dots'],region&&layers.Sources);vis(['community-dots'],region&&layers.Communities);vis(['pipes-line'],region&&layers.Pipelines);vis(['wind-lines'],region&&layers.Wind&&hour!==null);
 },[ready,data,region,mode,values,surface,layers,chosen,selected,hour]);
 return <div ref={el} className="map"/>;
}
