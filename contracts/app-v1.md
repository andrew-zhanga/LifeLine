# Frozen FlareWise v1 interface

All outputs carry schema_version `1.0`, model_version `screening-v1`. Parameters in `parameters.json` are authoritative. Prepared inputs are read-only. IDs/order follow prepared GeoJSON feature order. USD and m³ stored in base units. UTC timestamps end Z. Missing values null with reason. No nonfinite JSON. Every output includes provenance pointing to prepared sources.

## A → coordinator/B

`data/build/exposure/exposure-manifest.json`: site_ids, cell_ids, weather_ids, site_weather_ids (array aligned to site_ids), replay_hours_utc, analysis_coverage, parameters, provenance.
`site-benefits.json`: sites array of {id, eligible_for_capture, annual_population_weighted_index, under5_weighted_index, age65plus_weighted_index}; baseline_population_weighted_index. Values are unmitigated contributions; B multiplies by capture_fraction.
`annual-baseline.json`: cell_ids, values (mean hourly), population_weighted_index.
`annual-source-contributions.npz`: site_index, cell_index, values (one entry per sparse link; annual mean).
`replay-baseline.npz`: values [48,cells].
`replay-source-contributions.npz`: site_index, cell_index, values [48,links].
`early-frame.json`: cell_ids, values, timestamp_utc. Deliver early for integration.
`validation.json`: real checks and timings. Additional diagnostic files allowed.

## B → coordinator

`data/build/portfolios/site-economics.json`: sites array with id, eligible_for_capture, pipeline_distance_km, capex_usd, annual_captured_m3, annual_sellable_mmbtu, annual_margin_usd, npv_usd, payback_years (null with reason if no positive margin). Benchmark price at top level.
`scenarios.json`: scenarios array {id, budget_usd, gas_price_usd_per_mmbtu, plans, default_plan_id}; each plan {id, name, preset (Financial/Balanced/Exposure or null), selected_ids, capex_usd, npv_usd, annual_captured_m3, annual_sellable_mmbtu, annual_margin_usd, exposure_benefit, exposure_reduction_pct, solver_status, solver_gap}. Disabled Balanced may have disabled_reason and no selected IDs. Plan IDs unique globally. named plans plus 5–8 actual feasible frontier candidates. Use final A benefits for publication.
`assumptions.json`, `sensitivity.json` (cases array), `validation.json`.

## Coordinator → frontend

Root `/data/manifest.json` has schema_version, model_version, source_commit, years, units, sources (array of {name,url,note}), assumptions (object), analysis_coverage, default_scenario_id, default_plan_id, replay_hours_utc, fixed_legend_breaks (ascending numeric exposure values), asset_urls.
asset_urls keys: global, sites, cells, tracts, communities, pipelines (GeoJSON); economics, scenarios, baseline, weather (JSON). Paths absolute `/data/...`.
GeoJSON properties preserve prepared input fields. Cells also have density_per_km2, under5_share, age65plus_share and index (aligned to baseline cell_ids). Communities include representative lng/lat properties and nearest_cell_index (explicit nearest cell proxy, not community-average exposure).
Economics/scenarios exactly B format; each enabled plan gains residual_url.
Baseline: {schema_version,model_version,cell_ids,annual:[cell values],replay:[[cell values] x48],annual_population_weighted_index,replay_population_weighted_index:[48 totals]}.
Residual: {schema_version,model_version,plan_id,cell_ids,annual:[cell values],replay:[[cell values] x48],annual_population_weighted_index,replay_population_weighted_index:[48 totals]}.
Weather: {locations:[{id,longitude,latitude,speed_mps:[48],direction_from_deg:[48]}],site_weather_ids:{siteId:weatherId},replay_hours_utc}.
Frontend loads baseline shared and one residual lazily. Keep old scenario coherent until load succeeds; use real per-hour weather and index, fixed installations and shared legend. Period average uses annual values, not averaged angles. No fabricated placeholders in production.
