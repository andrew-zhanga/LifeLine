# Community / robustness extension v1

Both JSON files carry `schema_version: 1.0`, `model_version: screening-v1`, provenance, assumptions and limitations. These values attribute the existing annual screening model, **not transport replay**. All money is USD; IDs match existing sites and plans.

`community.json`:
- `groups`: `population`, `under5`, `age65plus` (actual allocated counts, no health multipliers).
- `tracts`: `{id, name, county, population, under5, age65plus, baseline: {population,under5,age65plus}, top_sources: [{id, population,under5,age65plus}]}`. Baseline values are weighted indices, counts are separate fields. Top sources are truncated to five ranked by all-resident contribution; not claimed to sum to baseline.
- `plans`: existing 25 plans plus newly optimized age-objective plans and robust plans. Each includes original economics fields and selected_ids, `objective_group`, `regional: {population:{baseline,residual,reduction,reduction_pct},under5:{...},age65plus:{...}}`, `tract_results: [{tract_id,population:{baseline,residual,reduction,reduction_pct},under5:{...},age65plus:{...}}]`. Zero baseline → null percentage. Existing plan IDs unchanged; new IDs `community-{budget in m}m-{group}` and `robust-{budget in m}m`.
- `objective_plans`: `{budget_usd, group, plan_id}` entries to identify three separately optimized objectives per budget.

`robustness.json`:
- `weather_scenarios`: `{id,name,hours,months,baseline_population_weighted_index}` for DJF/MAM/JJA/SON, all actual 2023 hours; not holdout or forecasts.
- `economic_scenarios`: explicit benchmark, $1.50/$4 price, 75/125% capex.
- `fixed_plan_evaluations`: `{plan_id,weather:[{scenario_id,exposure_benefit,exposure_reduction_pct}],economics:[{scenario_id,capex_usd,npv_usd,annual_margin_usd,budget_feasible}],weather_reduction_pct_range:[min,max],npv_usd_range:[min,max]}`. Fixed IDs across scenarios.
- `robust_plans`: standard plan totals + `minimum_seasonal_reduction_pct`, `financial_floor_usd`, `seasonal_results`. Objective maximizes minimum seasonal fractional reduction, at frozen budget and ≥95% of corresponding annual Financial NPV. A floor based on best-found financial reference is labeled as such. No probabilities.

Existing plans remain intact. New selections require annual residual asset assembly if used on the main map; the attribution panel may display them immediately using exported values.

## Global inventory discovery

`global-inventory.json` is `inventory-summary-v1` (not a global model). `countries` is sorted by total annual flared volume and contains `{id,country,site_count,annual_flared_m3,center:[longitude,latitude],bounds:[west,south,east,north],top_sites:[{id,longitude,latitude,annual_flared_m3}],available_analysis:{inventory:true,annual_screening:false,economics:false},analysis_region_ids:[]}`. Country IDs are original inventory country names. Longitude bounds use the smallest enclosing arc, with east possibly above 180; centers are volume-weighted spherical means. The US links to `texas-eagle-ford` in `regions`, where screening and economic flags are true only for the study box. No country is assigned modeled global financial value.
