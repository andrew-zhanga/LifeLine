export async function json(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Could not load ${url} (${response.status})`);
  return response.json();
}
export async function loadApp() {
  const manifest = await json('/data/manifest.json');
  if (manifest.schema_version !== '1.0') throw new Error('Unsupported analytical data version');
  const keys = ['global','sites','cells','tracts','communities','pipelines','economics','scenarios','baseline','weather'];
  const values = await Promise.all(keys.map(key => json(manifest.asset_urls[key])));
  const data = {manifest, ...Object.fromEntries(keys.map((key,i) => [key,values[i]]))};
  if (data.cells.features.length !== data.baseline.cell_ids.length || data.cells.features.some((f,i)=>f.properties.id !== data.baseline.cell_ids[i])) throw new Error('Baseline grid ordering mismatch');
  return data;
}
export function validateResidual(bundle, baseline, plan) {
  if (bundle.plan_id !== plan.id || bundle.cell_ids.length !== baseline.cell_ids.length || bundle.cell_ids.some((id,i)=>id!==baseline.cell_ids[i])) throw new Error('Portfolio map ordering mismatch');
  if (bundle.replay.length !== baseline.replay.length || bundle.annual.length !== baseline.annual.length) throw new Error('Portfolio map coverage mismatch');
  const frames = [bundle.annual, ...bundle.replay];
  if (frames.some(values => values.length !== baseline.cell_ids.length || values.some(value => !Number.isFinite(value) || value < 0))) throw new Error('Invalid portfolio exposure frame');
  return bundle;
}
export const format = (value, digits=1) => Number.isFinite(value) ? value.toLocaleString('en-US',{maximumFractionDigits:digits}) : '—';
export const money = value => Number.isFinite(value) ? `${value<0?'−':''}$${format(Math.abs(value)/1e6,2)}m` : '—';
export const frame = (bundle,hour) => hour === null ? bundle?.annual : bundle?.replay?.[hour];
export const total = (bundle,hour) => hour === null ? bundle?.annual_population_weighted_index : bundle?.replay_population_weighted_index?.[hour];
