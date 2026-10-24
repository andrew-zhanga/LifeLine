export function framePair(frames, elapsed) {
  let lo=0,hi=frames.length-1;
  while(lo<hi){const mid=Math.ceil((lo+hi)/2);if(frames[mid].elapsed_s<=elapsed)lo=mid;else hi=mid-1;}
  const next=Math.min(lo+1,frames.length-1),span=frames[next].elapsed_s-frames[lo].elapsed_s;
  return {a:lo,b:next,t:span>0?Math.max(0,Math.min(1,(elapsed-frames[lo].elapsed_s)/span)):0};
}
export function interpolatePuffs(scene,elapsed,capture=false){
  const {a,b,t}=framePair(scene.frames,elapsed),next=new Map(scene.frames[b].puffs.map(p=>[p[0],p])),out=[];
  for(const row of scene.frames[a].puffs){const puff=scene.puffs[row[0]];if(!puff||puff.birth_elapsed_s>elapsed)continue;const target=next.get(row[0]);const mass=capture?puff.mass_capture:puff.mass_baseline;out.push({id:row[0],source_index:puff.source_index,mass,baseline_mass:puff.mass_baseline,values:row.slice(1).map((v,i)=>target?v+(target[i+1]-v)*t:v),fade:target?1:1-t});}
  const existing=new Set(scene.frames[a].puffs.map(p=>p[0]));
  for(const row of scene.frames[b].puffs){if(existing.has(row[0]))continue;const puff=scene.puffs[row[0]];if(!puff||puff.birth_elapsed_s>elapsed)continue;const source=scene.sources[puff.source_index],duration=scene.frames[b].elapsed_s-puff.birth_elapsed_s,progress=duration>0?Math.max(0,Math.min(1,(elapsed-puff.birth_elapsed_s)/duration)):1;const start=[source.x_m,source.y_m,source.z_m,scene.assumptions.initial_sigma_horizontal_m,scene.assumptions.initial_sigma_vertical_m];out.push({id:row[0],source_index:puff.source_index,mass:capture?puff.mass_capture:puff.mass_baseline,baseline_mass:puff.mass_baseline,values:start.map((v,i)=>v+(row[i+1]-v)*progress),fade:Math.min(1,progress*4)});}
  return out;
}
export function receptorAt(scene,elapsed,capture=false){if(elapsed<Math.min(...scene.puffs.map(p=>p.birth_elapsed_s)))return scene.receptor_series.baseline[0].map(()=>0);const {a,b,t}=framePair(scene.frames,elapsed),series=scene.receptor_series[capture?'capture':'baseline'];return series[a].map((v,i)=>v+(series[b][i]-v)*t)}

export function windAt(scene,elapsed,sourceIndex=0){const {a,b,t}=framePair(scene.frames,elapsed),first=scene.frames[a].wind.find(w=>w.source_index===sourceIndex),next=scene.frames[b].wind.find(w=>w.source_index===sourceIndex)||first;return first?{source_index:sourceIndex,east_mps:first.east_mps+(next.east_mps-first.east_mps)*t,north_mps:first.north_mps+(next.north_mps-first.north_mps)*t}:null;}
