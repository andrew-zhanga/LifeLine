# FlareWise — executable build and demo plan

Updated: 2026-10-23. Status: implementation specification; application and data pipeline not yet built.

Data audit update: see [FLAREWISE_DATA_FEASIBILITY_AUDIT.md](FLAREWISE_DATA_FEASIBILITY_AUDIT.md). Sentinel-3 SLSTR is the proposed independent detection alternative; its gas-volume link is an explicit release gate. The data-access tests and corrections in that audit take precedence over unverified availability assumptions below.

Source: `/Users/aditya/Downloads/FlareWise Hackathon Roadmap.pdf`. This document refines its proposed scope, resolves implementation ambiguities, and incorporates the requested global globe and time-dependent wind/population layer. It does not activate the unrelated Paris heat planning documents in this workspace.

## 1. Product and scope decisions

FlareWise helps an operator choose which flare capture projects to fund under a fixed budget, comparing financial return with reduced modeled exposure in surrounding communities.

The demonstrable journey is **Earth → Eagle Ford → flare → wind and residents → capture portfolio comparison → Earth**.

Defaults for execution:

- One interactive global flare inventory; full economics and exposure analysis for Eagle Ford only.
- React + TypeScript + Vite, MapLibre GL JS, and a small chart component. Add deck.gl only if needed for performant grid rendering. Python preprocessing with pandas, NumPy, GeoPandas and SciPy/HiGHS. No application server required for the core demo.
- Historical hourly weather playback. Do not call this live pollution monitoring.
- A dated real flare inventory and real weather/population inputs. Synthetic fixtures are permitted during development and visibly labeled; they are not presented as observed results.
- Main health-related objective: reduction in population-weighted modeled exposure index. Birth-outcome estimates are deferred.
- Precomputed portfolio scenarios and exposure frames served as static assets. No data acquisition, model training or optimizer call during the presentation.
- Team size and remaining deadline are unconfirmed. Work packages below work sequentially or can be assigned to the four roles from the original roadmap; timings are estimates, not evidence of staffing.

## 2. Exact judge-facing experience

### A. Global opening

The initial screen is a dark globe, centered so Texas is easy to reach, with dated global flare markers. Markers represent the source inventory, not every flare currently burning. A modest atmospheric effect is optional; readability is required.

Visible elements: FlareWise name, one-sentence purpose, inventory year/source, legend, and **Explore Eagle Ford**. No global exposure or financial total is displayed unless actually computed.

Drag rotates the globe; scroll zooms. Clicking an unsupported region gives inventory details and “Detailed capture analysis available for Eagle Ford.” The primary action flies to Eagle Ford in approximately two seconds. Skip/reduced-motion behavior jumps directly to the destination.

### B. Regional analysis

The same map remains mounted. At regional zoom, show towns, flare markers, study boundary and an optional population layer. The region extent includes receptors outside the analysis boundary when they are within 20 km of an included flare; include known sources within a matching exterior buffer as fixed background contributions, ineligible for capture decisions. Label edge coverage and exclude unmodeled incoming sources from claims of total pollution burden.

Layout:

- Left: budget, gas-price scenario, Financial return / Balanced / Exposure reduction presets, selected-project list.
- Center: dominant map with clear legend and layer controls.
- Right: contextual flare or community details; collapsed until selection.
- Bottom: trade-off chart; wind playback timeline appears in hourly mode.
- Summary strip: capital used, seven-year NPV, captured annual gas estimate, and modeled exposure reduction. State currency, units and time horizon.

On entering, load the default scenario and Financial return plan. Global marker styling transitions to regional styling without moving site coordinates.

### C. Flare inspection

Clicking a flare selects it, outlines its influence area and opens a details panel:

- Site ID, coordinates, inventory period, source and detection confidence if available.
- Annual gas-volume estimate; persistence only if supported by nightly data.
- Capture option, assumed capital cost, annual operating margin and seven-year NPV.
- Selected/not selected in the current portfolio.
- Contribution to modeled exposure; nearby communities and their aggregate demographic composition.
- A small provenance/assumptions disclosure.

In hourly mode, the selected flare's transport footprint uses that hour's weather. In period-average mode, it uses the aggregate footprint. A label distinguishes “Selected flare contribution” from “All modeled flares.” Details remain open when the plan changes.

### D. Wind and population playback — required

Toggle **Wind & communities** to reveal historical hourly playback. The default is a preselected, continuous 48-hour interval with good data coverage, within the analysis period. Select a sequence with visible wind variation after reviewing the real data; do not manufacture the variation.

Controls: play/pause, previous/next hour, scrubber, readable local timestamp with UTC offset, and **Period average**. Store UTC internally; repeated daylight-saving hours must be distinguishable.

For each hour the map shows:

1. Wind arrows indicating the direction air travels, with speed in m/s. Tooltip: “Wind from W; moving E,” for example.
2. A continuous-color relative exposure grid from all included sources, with an optional selected-source outline.
3. Population or demographic context, selectable as a separate layer.
4. Community highlight and panel on click: estimated residents in modeled footprint, demographic counts, weather source/resolution, and relative exposure before/after the selected portfolio.

Hourly changes update wind arrows, exposure grid and hourly population summaries together. Demographic data stays fixed in time: this represents residential population, not individual tracking or daytime mobility.

Choose one base fill at a time: exposure, population density, under-5 share, age-65+ share, or tract social vulnerability if available. Wind arrows and source markers remain independently toggleable. Demographic tooltips identify the source geography; do not imply tract estimates were measured at 1 km resolution.

The default shows wind arrows. Optional particles illustrate wind movement only, use a restrained density, stop under reduced-motion settings, and are labeled visual illustration. They are not pollutant parcels or the numerical model.

Hourly playback does not silently re-optimize the portfolio: capture investments use the full analysis period. Label this explicitly next to the timeline.

### E. Portfolio comparison — required

At an unchanged budget and gas price, clicking **Balanced** loads the precomputed balanced portfolio. Marker outlines, list, exposure field, chart selection and totals update atomically.

Captured sites remain visible with a distinct outline; hypothetical capture is not represented as an observed shutdown. Provide **Baseline / After capture** exposure views with the same color scale. The regional summary shows period-average benefit; an hourly summary is separately labeled.

Clicking a frontier point selects that exact portfolio. Financial return, Balanced and Exposure reduction are shortcuts to identified points; there is no unexplained combined score.

The before/after visual change must use the source removal assumption in the data model. Default: 90% reduction in the captured site's modeled flare contribution, a disclosed scenario assumption rather than measured engineering performance. Include 50% and 100% sensitivity runs offline. Residual emissions from capture equipment are not modeled, so report reduction in flare-related exposure index, not net facility health benefit.

### F. Presentation recovery

**Reset demo** restores the global camera, default scenario, no selected feature, paused playback and default layers. **Back to Earth** changes the camera without destroying the selected portfolio.

A guided sequence may move between the above states; every state must also be accessible manually. Include pre-rendered backup screenshots and a locally served fallback basemap/region outline so the core story survives network loss.

## 3. What the wind layer models

### Core: physics-informed screening, not calibrated dispersion

We use wind to route an estimated source-strength proxy toward receptor cells and reduce its relative influence with distance and ventilation. This supports comparisons of locations, hours and capture scenarios. Output units are a **relative exposure index**, never µg/m³, AQI, individual dose or probability of illness.

A full dispersion model additionally needs defensible emissions, source height, plume rise, turbulence/stability and other parameters. EPA describes AERMOD as a steady-state plume model incorporating boundary-layer turbulence and surface/elevated sources. Implementing a simple kernel is not equivalent to running or validating AERMOD.

### Inputs and geometry

- Receptor grid: 1 km cells; candidates within 20 km of each source. Use a suitable local metric CRS, default EPSG:32614 after checking the region geometry.
- Hourly winds: ERA5 or a documented historical-weather product; record model, grid resolution, wind height and missingness. Prefer one consistent product/height across the region.
- Source strength q[f,t]: annual volume / hours per year for inventory-only mode. With usable nightly histories, use a normalized monthly activity/strength profile whose integral preserves annual volume. Do not multiply annualized volume by burn probability a second time.
- Hourly operation is inferred, not observed. A nighttime satellite detection does not establish daytime operation. Carry `activity_basis` in every source record.
- Wind is assigned from weather grid cells to sources using a documented nearest-cell mapping for MVP. Do not imply 1 km weather resolution because the receptor grid is 1 km.
- Population: WorldPop where usable, otherwise ACS tract population allocated to cells by tract/cell overlap. Record allocation method. Preserve tract totals.

### Deterministic kernel

Let e be the unit vector pointing downwind, r the source-to-cell vector in meters, x = dot(r,e), and y the signed crosswind offset. Meteorological direction denotes where wind comes FROM; convert to travel direction by adding 180 degrees. With u/v components, the travel vector is (eastward u, northward v).

For ordinary receptor sample points with x > 0 and distance d <= 20 km (area-sample the source-containing cell so residents are not dropped by an upwind centroid or x=0):

`w = exp(-0.5 * (y / (500 + x*tan(22.5 degrees)))^2) * exp(-d/5000) / ((1 + d/1000) * max(speed_mps, 1))`

Otherwise w = 0. All distance constants are in meters and are versioned screening parameters, not fitted atmospheric constants. This gives a smooth widening downwind influence pattern without a hard sector edge.

If valid boundary-layer height is available consistently, multiply by `500 / max(height_m, 100)`; if not, omit this term for the entire scenario and name it the wind-only variant. Never silently mix variants by hour.

`I[c,t] = sum_f(q[f,t] * w[f,c,t])`

For calm wind below 1 m/s, do not assign a confident downwind direction: use an isotropic distance-decay screening footprint at speed floor 1 m/s, visibly flag “Calm wind: direction uncertain,” and include this assumption in sensitivity analysis. Missing weather is unavailable, not zero exposure. Apply a single documented completeness mask to all compared plans.

This is a sequence of hourly quasi-steady footprints. It does not simulate pollutants traveling between hours, accumulated pollution mass, chemistry, terrain or deposition. The UI must not describe it as plume arrival-time prediction. A time-evolving puff/advection model is a later upgrade.

### Population and demographic summaries

`E_period = sum_valid_t(sum_c(pop[c] * I[c,t])) / number_of_valid_hours`

This is the optimization objective before/after capture. No binary threshold is required to compute it.

For a separate, interpretable footprint population count, define T once as the population-weighted 75th percentile of positive baseline cell-hour index values over the complete analysis period. Export its value and method. Count each cell's population once per hour where I >= T. Call this **Residents in higher modeled exposure areas**, and state that T is a relative display threshold, not a health standard. Keep T fixed across plans and hours; test 50th/90th percentiles for sensitivity. If no positive exposure exists, show zero with an explanatory message.

For period summaries, count unique residents/cells meeting the specified criterion; never sum hourly resident counts and label the result people. Person-hours, if shown, use that unit explicitly. Never add per-flare population counts to derive a regional total because footprints overlap.

Under-5 and age-65+ counts may be estimated using tract shares applied to allocated population, labeled as estimates. Groups can overlap other demographic groupings and must not be added indiscriminately. Social vulnerability is contextual in MVP, not a hidden multiplier. Race/ethnicity is not a physical transport coefficient or biological susceptibility assumption.

No claims of avoided preterm births or lives saved in the core demo. A later outcome module needs pregnancy cohorts/windows, a matched exposure definition, baseline risk, uncertainty and explicit causal assumptions.

## 4. Data acquisition gates and fallback behavior

First gate, before extensive UI polish: obtain and inspect a real global site inventory, a regional subset, a weather sample and regional population counts. Record actual schema, units, access terms and years in `manifest.json`. API metadata or HTTP 200 alone is not proof of data retrieval: verify content type, parse records, and check regional coverage. Census API queries currently require a key; official table-based ACS Summary Files are the fallback.

Choose the latest complete common analysis year supported by the acquired inputs; do not choose a year based on the pitch. Prefer one full year of hourly weather. If only a shorter interval is available, name that exact interval everywhere and do not call its results annual. Demographic reference years may differ but must be disclosed.

| Input | Preferred | Fallback and resulting limitation |
|---|---|---|
| Flare locations/activity | Sentinel-3 C3S v1.2 dedicated gas-flare monthly summary CSVs, subject to real-file/region check | EOG if access is available; World Bank/ORNL annual inventories remain VIIRS-derived, not independent sensor replacements |
| Gas volume | Verified flare-only RRC records with defensible source/project match for a VIIRS-free route | World Bank annual individual-site volume if VIIRS-derived inputs are acceptable; otherwise hide financial optimization until a volume source is established |
| Weather | Downloaded ERA5 fields | Open-Meteo historical product after variable/coverage check; wind-only kernel if mixing height unavailable |
| Population | WorldPop + ACS context | ACS tract allocation with allocation uncertainty |
| Capture infrastructure | Public pipeline geometry | Explicit cost scenarios; nearest line is a proximity proxy, not a verified connection |
| Site activity | Quality-controlled nightly observations | Inventory annual average; hide persistence metric |

If inventory and weather years cannot align, label the product **weather replay over historical inventory**, not a reconstruction of actual contemporaneous emissions. Resolve this limitation before finalizing the pitch.

Do not infer satellite observation opportunities from ERA5 cloud cover alone. Nightly persistence requires overpass coverage and quality/cloud information or a clearly labeled proxy. Persistent detections are not sufficient to establish regulatory “routine flaring.” A site going dark is not proof of capture.

## 5. Economics and optimization

MVP supports one screening capture option: pipeline tie-in, with documented distance-based capex and operating-cost assumptions. Other technologies require separate feasibility models and are deferred. Unknown infrastructure feasibility is visible. Waha is not automatically the Eagle Ford price: use a justified benchmark or label it simply a user-selected gas-price scenario.

Use explicit conversions from m³ to thousand cubic feet to MMBtu. Annual margin = recovered sellable energy × price − operating costs. Recovered sellable energy must apply the same capture fraction used for source reduction, then subtract treatment/shrinkage and parasitic use; include gathering, processing and compression in operating costs. Do not book revenue from 100% of gas while modeling only 90% capture. NPV = discounted seven-year cash flows − initial capex; discount rate defaults to 10%. Constant volume is the MVP assumption, with a disclosed decline sensitivity; do not fit an Arps curve without adequate histories. Nonpositive cash flow gives no finite payback, not a negative payback period.

Budget constraint: sum(capex[f] * selected[f]) <= budget. Exposure benefit is each site's reduction in period population-weighted index under the stated capture assumption. This objective is additive; the thresholded resident count remains a reporting metric, not the objective.

For each scenario, maximize NPV subject to minimum exposure benefit for up to 20 epsilon targets, including endpoints. Keep feasible unique nondominated portfolios; report solver gap/status and do not call this an exhaustive frontier. Permit the empty plan.

Balanced preset: highest exposure reduction among computed portfolios retaining at least 95% of positive money-only optimal NPV. If optimal NPV <= 0, show “No positive-return financial baseline” and disable the balanced shortcut; the exposure-maximizing option remains available with its financial cost stated. The 95% choice is visible and documented.

Choose five budget presets after inspecting the capex distribution and three gas-price scenarios after inspecting a defensible benchmark range; export actual values and rationale. No invented defaults presented as market observations. Controls snap to these 15 precomputed combinations. Changing either control resets to the selected preset in that scenario or the financial baseline if the previous custom point has no equivalent. Never interpolate selected-site portfolios.

## 6. Static data contract and computation boundaries

Separate source detections from capture projects. Each project has explicit source IDs; assign volume records once and prohibit overlapping project selection. Store detection source, volume source, source-strength units, match quality, activity basis and economic eligibility separately. Detection-only sites remain visible but have null financial metrics; never mix FRP-based and gas-volume-based exposure scores.

Use stable string IDs everywhere; coordinates are WGS84 longitude/latitude in frontend assets; all timestamps are ISO UTC; no NaN/Infinity in JSON. Missing values are null with a reason. Monetary values are USD with a declared price basis. Include `schema_version` and `model_version`.

| Asset | Required contents |
|---|---|
| `manifest.json` | Sources/URLs/licenses, reference years, analysis interval, assumptions, model parameters, coverage, units, scenario IDs, default camera/time/plan, thresholds and fixed legend breaks |
| `global_sites.geojson` | Site ID, point geometry, inventory year, annual volume if known, regional-analysis availability |
| `regions/eagle-ford/sites.json` | Site IDs, coordinates, source/activity basis, volume, cost inputs, economic values by price scenario, optional persistence and missingness |
| `regions/eagle-ford/cells.geojson` | Grid geometry, cell ID, resident population, tract allocation, demographic estimates, coverage flags |
| `regions/eagle-ford/weather.json` | Grid/source weather mapping, UTC hourly winds, optional mixing height, validity flags |
| `regions/eagle-ford/scenarios.json` | Budget/price combinations, portfolios with selected site IDs, capex/NPV/gas totals, period exposure benefit, reporting population counts, solver metadata and preset IDs |
| `regions/eagle-ford/replay-index.json` | Replay hours and frame paths keyed by scenario and plan, baseline path, selected-flare footprint paths |
| `regions/eagle-ford/replay/*.json` | Per-hour baseline/residual cell indices and reporting totals for the 48-hour window; matching weather timestamps |

Backend computes full-period source-to-cell contributions in spatially sparse, time-chunked batches. Do not allocate a dense hours × all flares × all cells tensor. Aggregate site benefits for the optimizer. Only the 48-hour replay needs detailed browser frames.

Replay baseline is shared; lazy-load the selected portfolio's replay and cache it. Only expose chart points with a valid replay bundle. Compress assets; target initial application/global data under 5 MB compressed and each replay bundle under 10 MB, revising grid representation if measured sizes exceed this. Browser interpolates visual opacity only, not model values or portfolio membership.

## 7. Frontend state and failure behavior

Single application state: `view`, `scenarioId`, `planId`, `selectedSiteId`, `selectedCellId`, `timeMode`, `hourIndex`, `playing`, `activeFill`, `showWind`, `exposureView`.

- Changing hour preserves scenario and portfolio.
- Changing plan preserves hour and selection; updates all dependent visualizations together.
- Selecting a site clears community selection and vice versa.
- Layer toggles do not change calculations or ranking.
- Period-average mode pauses playback and swaps to correctly labeled period data; it does not average wind directions arithmetically.
- Missing frame: pause and show unavailable; do not show a prior frame under a new timestamp.
- Scenario load failure: retain previous coherent scenario and show a retry message.
- Legend uses fixed baseline-derived breaks across time and plans; never auto-normalize each frame.
- Empty portfolio, no affected cells, unknown economics and unavailable demographics have explicit readable states.

## 8. Ordered work packages and completion gates

| Package | Work | Exit gate |
|---|---|---|
| 0 — feasibility and contract, ~2 h | Acquire samples, choose period/region, define schema and fallback tier | One real site, weather hour and population cell join correctly; access limitations recorded |
| 1 — globe and vertical slice, ~3 h | App shell, globe flight, regional markers, details panel, fixture-driven shared state | Global → region → site works; fixtures visibly labeled |
| 2 — wind and communities, ~4 h | Weather normalization, kernel, population allocation, real replay data | One real source/hour footprint verified; 48-hour playback changes communities correctly |
| 3 — economics and optimizer, ~3 h | Unit conversions, cost scenarios, full-period exposure aggregation, frontier | Feasible real-data portfolios with reproducible objective values |
| 4 — integration, ~3 h | Scenario controls, chart/map synchronization, residual replay, provenance | One complete real-data judge journey; no synthetic values in production path |
| 5 — verification and polish, ~3 h | Tests below, performance, offline recovery, projection/readability checks | All critical checks pass; actual trade-off recorded |
| 6 — rehearsal and delivery, ~4 h | Guided path, screenshots, README/methods, timed pitch | Two full runs under 3 minutes and a network-disabled recovery run |

These sum to 22 estimated hours sequentially and leave little contingency. If time slips, remove optional demographics beyond age, extra price/budget presets and visual particles first. Preserve real wind/population replay and a truthful portfolio comparison. If access blocks the current-year pipeline, switch to the labeled historical tier rather than spend the whole event on ingestion.

Deferred: Sentinel segmentation, learned flare classifiers, operational routine classification, Gaussian/AERMOD dispersion, puff transport, TROPOMI validation, birth outcomes, operator attribution, shared gathering infrastructure, live weather feed, second analyzed region and Monte Carlo confidence rings.

## 9. Verification and acceptance criteria

Scientific/data checks:

- A wind FROM west creates an eastward footprint; reversing wind reverses the footprint.
- Upwind receptors receive zero from a non-calm source; calm handling is finite and flagged.
- Larger source strength increases index proportionally; distance/crosswind decay matches the defined kernel.
- Capturing one source changes only its contribution; overlapping sources are summed before resident counts.
- Baseline and residual arrays use identical timestamps, weather, population and legend thresholds; residual index never exceeds baseline under the defined removal model.
- Population allocation conserves tract totals within documented numeric tolerance; no population counted twice per hourly regional footprint.
- Missing weather is excluded consistently and coverage reported. Annual source strength integrates back to annual inventory volume.
- Test economics against a hand-calculated case; capex counted once in NPV. Negative prices produce sensible losses/no-payback states.
- On a tiny portfolio fixture, compare optimizer outputs to exhaustive enumeration; all displayed plans meet budget and reported objective totals.
- Sensitivity: vary sector width (15/22.5/30 degrees), distance scale, capture fraction and cost assumptions. Report whether the showcased recommendation changes. Scenario ranges are not confidence intervals.

Interaction checks:

- Globe transitions, site/community click, timeline, presets and chart points all work by mouse and keyboard where applicable.
- Plan switch preserves the chosen hour; hour change preserves the plan. Metrics and map never disagree during loading.
- A displayed before/after change is traceable to actual source contributions and selected IDs.
- At least one real weather sequence visibly changes the modeled footprint. A financial/exposure trade-off is shown only if the computed portfolios differ; otherwise explain the alignment or select another disclosed scenario.
- Cached plan switches target <300 ms on the presentation laptop; playback targets 2–4 model hours per second without UI stalls. Measure rather than assume performance.
- Readable at projector resolution; reduced-motion setting; network-disabled fallback; no console errors on the rehearsed path.

## 10. Three-minute presentation

0:00–0:20 — Global inventory: gas flaring is widespread; show source/year rather than an unverified current-world total.

0:20–0:40 — Fly to Eagle Ford: this is the region with implemented analysis.

0:40–1:15 — Select a flare, play wind sequence: “Weather changes which communities are downwind. We combine historical wind, estimated flare strength and residential population to screen exposure.”

1:15–1:40 — Click a community: show residents and age composition with data resolution and model label.

1:40–2:20 — Same budget, Financial return → Balanced: show actual NPV difference and modeled exposure reduction. Map and chart explain which projects changed. Do not prewrite unsupported improvement percentages.

2:20–2:40 — Explain the model and limits in one sentence; open assumptions if asked. Name the product's value as an inspectable capture decision.

2:40–3:00 — Return to Earth: the inventory is global; detailed modeling expansion is the next step.

## 11. Delivery checklist and outstanding inputs

Deliver runnable frontend, reproducible preprocessing scripts, versioned static data, source/assumption manifest, automated checks for the critical calculations, README with local commands, methods note and demo screenshots. Keep credentials out of browser assets and repository.

Inputs still needed before implementation scheduling: actual deadline, assignment of frontend versus entire pipeline, any existing mockup, and available Nightfire access/data. Defaults in this document allow initial implementation to proceed while these are clarified; none is a reason to fabricate missing evidence.

## Sources checked for this revision

- Original roadmap: `/Users/aditya/Downloads/FlareWise Hackathon Roadmap.pdf`.
- EOG Nightfire access and format: https://eogdata.mines.edu/products/vnf/ — licensing/access must be verified against actual downloaded data.
- MapLibre globe example: https://maplibre.org/maplibre-gl-js/docs/examples/globe-custom-simple/
- deck.gl map integration: https://deck.gl/docs/api-reference/mapbox/overview
- Open-Meteo historical weather API: https://open-meteo.com/en/docs/historical-weather-api — check available variables for the chosen underlying product and dates.
- EPA dispersion model description: https://www.epa.gov/scram/air-quality-dispersion-modeling-preferred-and-recommended-models
- Cushing et al. study: https://pubmed.ncbi.nlm.nih.gov/32673511/ — observational birth-outcome evidence; no outcome model implemented in this MVP.
