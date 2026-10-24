import React,{useEffect,useState} from 'react';
import {ScanLine,RefreshCw,ExternalLink} from 'lucide-react';
import {json,format} from './data';
const ROOT='/data/extensions/experiments/';
const percent=value=>Number.isFinite(value)?`${format(value*100,1)}%`:'—';
export default function SatelliteLab(){
 const [result,setResult]=useState(null),[error,setError]=useState(''),[attempt,setAttempt]=useState(0);
 useEffect(()=>{let active=true;setError('');json(ROOT+'results.json').then(data=>{if(data.status!=='completed'||!data.unet_test||!data.baseline_test||!Array.isArray(data.examples))throw new Error('The completed experiment results are not available yet.');if(active)setResult(data)}).catch(()=>{if(active)setError('Completed satellite experiment results are not available. Retry after the research run has finished.')});return()=>{active=false}},[attempt]);
 if(!result)return <div className="wb-loading" role="status"><ScanLine size={35}/><h2>{error?'Research results unavailable':'Loading satellite results'}</h2><p>{error||'Reading held-out scores and image predictions.'}</p>{error&&<button onClick={()=>setAttempt(attempt+1)}><RefreshCw size={14}/> Retry results</button>}</div>;
 return <main className="wb-lab">
  <div className="wb-lab-intro"><span>Satellite research</span><h1>Can satellite imagery identify visible smoke?</h1><p>Industrial smoke segmentation research; not validated gas-flare detection.</p></div>
  <aside className="wb-lab-method">
   <div className="wb-lab-scope"><ScanLine size={20}/><span>Industrial smoke segmentation<br/><b>Held-out evaluation</b></span></div>
   <h2>Model performance</h2><p>Scores across all held-out pixels.</p>
   <table className="wb-lab-metrics"><thead><tr><th scope="col">Metric</th><th scope="col">U-Net</th><th scope="col">RGB baseline</th></tr></thead><tbody>{[['iou','IoU'],['dice','Dice'],['precision','Precision'],['recall','Recall']].map(([key,label])=><tr key={key}><th scope="row">{label}</th><td>{percent(result.unet_test[key])}</td><td>{percent(result.baseline_test[key])}</td></tr>)}</tbody></table>
   <p className="wb-lab-baseline"><b>Different inputs:</b> U-Net uses 12 spectral bands; the baseline uses three RGB bands. Scores compare both the inputs and the methods.</p>
   <h2>Geographically separated splits</h2>
   <table className="wb-lab-splits"><thead><tr><th scope="col">Split</th><th scope="col">Images</th><th scope="col">Sites</th><th scope="col">Location groups</th></tr></thead><tbody>{Object.entries(result.split_counts).map(([name,counts])=><tr key={name}><th scope="row">{name}</th><td>{counts.images}</td><td>{counts.sites}</td><td>{counts.location_groups}</td></tr>)}</tbody></table>
   <details className="wb-model-details"><summary>Training and evaluation details</summary>
    <p>{result.architecture}</p><div className="wb-lab-facts"><span>Parameters <b>{format(result.parameter_count,0)}</b></span><span>Training epochs <b>{result.epochs}</b></span><span>Selected checkpoint <b>Epoch {result.best_epoch}</b></span></div>
    <p>Model and threshold selection used validation data. Overlapping site footprints are grouped before split assignment. Test scores include positive and published negative images.</p>
    <p>{result.metric_aggregation}</p><p><b>Baseline:</b> {result.baseline?.method||'RGB brightness and neutrality baseline'}.</p><p>The different band counts mean this is not an architecture-only ablation.</p>
   </details>
   <a href={result.source_url} target="_blank" rel="noreferrer">Published dataset <ExternalLink size={13}/></a><p className="wb-lab-attribution">{result.attribution}</p>
  </aside>
  <section className="wb-lab-results">
   <div className="wb-lab-example-heading"><h2>Compare the predictions</h2><p>Lowest, median and highest IoU among positive test scenes · 120 × 120 input pixels.</p></div>
   {result.examples.map(example=><article className="wb-lab-example" key={example.id}><div className="wb-lab-example-title"><div><h3>{example.selection}</h3><span>Site {example.site_id} · {example.id}</span></div><b>IoU {percent(example.iou)}</b></div><div className="wb-lab-panel-labels">{example.panels.map(label=><span key={label}>{label}</span>)}</div><img src={ROOT+example.image} alt={`${example.selection}: ${example.panels.join(', ')} for held-out site ${example.site_id}. Scene IoU ${percent(example.iou)}.`}/></article>)}
   <details className="wb-lab-limitations wb-model-details"><summary>Research scope and limitations</summary><ul>{result.limitations.map((text,i)=><li key={i}>{text}</li>)}</ul><p>This separate experiment does not validate the Texas gas estimates, investment assumptions or modeled exposure reductions. Images preserve the original input grid using nearest-neighbor display.</p></details>
  </section>
 </main>
}
