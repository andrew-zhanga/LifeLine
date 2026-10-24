# FlareWise coordinated implementation plan

Status: ready for a new execution chat; this document is a plan, not a statement that the full build has been implemented.

This plan supersedes conflicting implementation details in the earlier `FLAREWISE_EXECUTABLE_PLAN.md` and original roadmap. Source priority: latest user instructions → this plan and verified build contract → verified source files → earlier plans. Unrelated Paris/heat-project documents are out of scope.

## 1. Outcome and operating priorities

Deliver a convincing, usable, data-backed hackathon product that answers: **where should a limited capture budget go, considering both gas value and people downwind?** Preserve the existing dark globe, smooth transitions and overall layout. Finish the core judge journey before adding features.

Priority order:

1. Complete Earth → Texas → wind/population → budget → portfolio comparison → before/after.
2. Make the map, controls, metrics and story agree.
3. Improve legibility and visual quality at presentation resolution.
4. Save reproducible evidence and pitch assets as work progresses.
5. Add only extensions that make the same investment story stronger.

Do not spend time on code-style rewrites, framework migrations, perfect abstractions, exhaustive mobile polish or unused features. A feature that looks good and behaves correctly is finished. However, wrong units, reversed winds, inconsistent metrics, budget violations, duplicate populations or invented model claims must be fixed even if visually subtle: they invalidate the judge-facing story.

Prefer simple Python preprocessing and static browser assets. No backend service, authentication or external API call is required during the core demo. Existing basemap/font dependencies need a simple visual fallback.

## 2. Baseline and scope freeze

Repository: `https://github.com/andrew-zhanga/LifeLine`, verified starting checkpoint `78ef33a` on main. Inspect the actual remote and working tree at startup; preserve newer/user changes. Original workspace: `/Users/aditya/Documents/ChatGPT/CleanTechHackathon`.

Use existing packages: React, Vite, MapLibre and Lucide. Keep JavaScript unless a small isolated type addition helps; no full TypeScript migration. Add NumPy/SciPy for computation and optimization if needed, and Matplotlib for reproducible figures. Only the coordinator changes dependency manifests.

Use 2023 World Bank flares, 2023 ERA5 weather, ACS 2019–2023, the prepared 5 km allocated population grid, downloaded pipeline geometry and Henry Hub benchmark. Do not reopen data acquisition for core inputs. Primary files are in `data/verified/processed/`; raw downloads are ignored by Git and not required to run the finished app.

Primary region: bbox [-100.2,27.5,-97.5,29.5]. Buffered sources/receptors: [-100.5,27.25,-97.25,29.75]. This is a South Texas/Eagle Ford study box, not an official basin polygon. Only 392 flagged candidates can be captured; 30 buffer sources remain background. Town and tract population layers overlap and must not be summed.

Core exposure output is a relative index, not pollution concentration or health prediction. Annual volume implies constant source activity for this scenario. No hourly operation, routine-flare classification, actual capture installations, or measured construction costs are available.

## 3. Parallel team and exclusive ownership

Run **three worker agents plus the coordinator**, the four available concurrent slots. All work in the same integration checkout with disjoint ownership; do not create competing Git histories for these tightly coupled changes. The coordinator alone changes Git state. If isolation later becomes necessary, pause the affected worker and deliberately reassign paths rather than introducing concurrent edits.

| Owner | Exclusive write paths | Responsibilities |
|---|---|---|
| A: Exposure and replay | `scripts/model/`, `data/build/exposure/`, `tests/model/` | Source/receptor geometry, weather assignment, deterministic model, annual contributions, replay, model diagnostics |
| B: Economics and optimization | `scripts/portfolio/`, `data/build/portfolios/`, `tests/portfolio/` | Pipeline-distance screening economics, NPV, solver, portfolios, objective totals, sensitivity |
| C: Frontend and interaction | `demo/src/`, `demo/public/ui/`, `tests/ui/` | Integrate actual assets, preserve globe/style, purposeful controls, coherent state, responsive presentation layout |
| Coordinator | `contracts/`, `scripts/assemble_app.py`, `scripts/make_pitch_assets.py`, `data/build/app/`, `demo/public/data/`, `presentation/`, `reports/`, `docs/`, root README, dependency/build/deployment config, Git | Contracts, shared examples, assembly, end-to-end checks, evidence figures, pitch, screenshots, checkpoint commits and pushes |

Treat `data/verified/` as read-only input. A source-data correction is proposed to the coordinator with evidence and applied centrally. Workers do not change another owner's paths. A and B request additional dependencies; coordinator installs/records them. C alone refactors the existing large `main.jsx` into a few components if useful.

Coordinator does not silently fix C's files while C is working. Send a concrete requested change; take ownership only after an explicit handoff/idle confirmation. If work moves between agents, update `docs/BUILD_STATUS.md` first.

Each worker reports at meaningful milestones: deliverables/paths, how verified, exact dependencies needed, blocker, next step. Use messages for contract questions; avoid polling or duplicated broad reviews. A lightweight status update about every 20–30 minutes is enough while working; no token-heavy transcripts.

## 4. Phase 0: coordinator setup, first 15–25 minutes

1. Read the pitch brief, this plan, data README/build contract, root README and current frontend. Inspect Git status, remote main, and available runtime/dependencies.
2. Create or reuse `codex/flarewise-full-build` from the current appropriate base. Do not discard uncommitted work or reset main. No automatic merge into main at completion.
3. Verify prepared file hashes; run the existing production build once. Do not redownload 200 MB of source tables when prepared inputs already pass.
4. Create `contracts/app-v1.md`, `contracts/example-bundle/` and centralized parameter JSON. Include one small real-data-derived vertical slice, with all temporary stub calculations visibly marked development-only.
5. Freeze the shared contract described below. Workers acknowledge it before wiring consumers. Start all three workers; B and C can work against the contract fixture while A computes.
6. Record baseline screenshots at 1440×900 and the current source commit. Initialize `docs/BUILD_STATUS.md` with owners and active tasks.

## 5. Shared contract and data flow

All data carries `schema_version`, `model_version` and source provenance. Stable site IDs from the prepared inventory; stable cell IDs from the grid; UTC ISO timestamps; WGS84 frontend geometry; metric calculations in EPSG:32614. Arrays always refer to explicitly ordered ID lists. Missing is null plus a reason, never NaN/Infinity or silently zero. Dollars are USD; never mix million-dollar display values with base-unit storage.

A writes:

- `exposure-manifest.json`: parameters, analysis coverage/mode, ordered site/cell/weather IDs, source→weather map, replay timestamps, units and hashes.
- `site-benefits.json`: each source's annual/period mean population-weighted contribution and optional under-five/65+ components. Baseline contributions include buffer sites; eligibility is explicit.
- `annual-baseline.json`: ordered mean cell index and regional weighted total.
- `annual-source-contributions.*`: sparse source→cell means, allowing exact removal of selected contributions.
- `replay-baseline.*`: baseline cell arrays for 48 consecutive actual hours.
- `replay-source-contributions.*`: sparse per-source cell indices and 48-hour contributions.
- `validation.json` and timing/memory summary.

B writes:

- `assumptions.json`: all economic coefficients, units, rationale and scenario ranges.
- `site-economics.json`: keyed by site ID, pipeline distance, capex, yearly volume/energy, margin, NPV and payback by price scenario.
- `scenarios.json`: scenario ID, budget, price, named preset IDs and plans. Each plan has selected IDs, capex, seven-year NPV, annual captured m³, annual sellable MMBtu, annual margin, period exposure benefit/index reduction, solver status/gap and assumption version.
- `sensitivity.json`, `validation.json` and solve timings.

Coordinator assembles a single browser contract:

```
demo/public/data/manifest.json
  schema_version, model_version, source_commit, years, units, sources,
  assumptions, analysis_coverage, default_scenario_id, default_plan_id,
  replay_hours_utc, fixed_legend_breaks, asset_urls
  global inventory; region sites/cells/tracts/communities/pipelines
  economics; scenarios and plan IDs
  annual and replay baselines; per-plan residual asset URLs
```

At first ship three budgets × one benchmark price × three named plans. Build all residual arrays offline from A's contributions and B's selected IDs. Chart points must have matching map assets. Lazy-load one plan bundle at a time; baseline is shared. Expand to five budgets × three prices and 5–8 frontier points only once the first version is responsive. If per-plan bundles get too large, use sparse source arrays with a browser worker, but don't add that architecture preemptively.

Coordinator validates selected IDs, source/cell ordering, budgets, sums and timestamp alignment during assembly. C consumes one loader adapter; it does not recompute economics or substitute generated numbers. Dev fixtures cannot silently load in the final production path.

## 6. Agent A: exposure and replay implementation

### Required calculation

- Build source→nearby-cell links once, cutoff 30 km. Use the prepared 5 km area-weighted cells; no fresh 1 km population dataset is implied.
- Use 100 m ERA5 winds consistently, nearest returned weather location per source. Keep 10 m data for a bounded sensitivity check.
- Meteorological direction is FROM. Unit transport vector: east = -sin(direction), north = -cos(direction). Interpolate vectors if interpolation is needed.
- Freeze a single kernel version, based on the verified integration prototype: distances in km; downwind x, crosswind y; for x>0 and d≤30:
  `w = exp(-0.5*(y/(1+0.15*x))^2) * exp(-x/15) / (max(speed_mps,0.5)*(1+x))`.
- Below 0.5 m/s, use `exp(-(dx²+dy²)/8)` within the same cutoff and label calm-direction uncertainty. This is a screening convention, not atmospheric calibration.
- Use annual m³ / 8,760 as source-strength proxy. Sum contributions before computing population-weighted output. Capture scales a selected source's contribution by 1−capture_fraction; it does not arbitrarily shorten a polygon.
- Full-period objective is mean hourly population-weighted index. The fixed source-volume proxy and omitted pollutant factors must be declared.
- Fine visual smoothing may be used only for display; tooltips and optimization use the prepared cell model. Do not suggest 5 km output means 5 km meteorology or observed population locations.

### Compute strategy and bounds

Do not allocate hours × all sites × all cells: that is about 112 GB even as float32. Vectorize sparse links in time chunks; accumulate annual means without retaining the year of frames. Retain detailed arrays only for the replay window.

Time a small slice first. Target a full-year run within roughly 20 minutes and a few GB memory. If it projects beyond that or repeatedly fails, switch to a deterministic stratified sample across every month and all hours of day, with weights and an explicit `analysis_mode`/coverage label. Never describe the existing midnight-only 365-sample smoke test as full hourly annual analysis. Coordinator approves the scope change internally and updates UI/slide wording.

Pick one real 48-hour replay interval with variation and relevant regional footprints. Record selection criteria and dates. No synthetic turning winds; do not select the replay based solely on a desired intervention percentage. Prefer one source and community that remain easy to follow.

### Acceptance and outputs for slides

Tests: cardinal winds; finite calm behavior; upwind rule; source linearity; buffer sources unchanged; identical baseline/residual ordering; no negative residuals; capture never raises index; population conservation; source-rate integration returns annual volume. Keep the test suite small and consequential.

Export real wind rose/time series, site-contribution distribution and exposure coverage statistics. These are data/model diagnostics, not pollutant prediction accuracy. Handoff one usable frame early before waiting for the full year.

## 7. Agent B: economics and optimization implementation

Work independently on geometry and economics while A computes. Develop against the contract fixture but require A's final benefits for published portfolios.

### Screening economics

Use nearest downloaded pipeline segment distance as a cost proxy, never a confirmed feasible connection. Record whether geometry edge effects matter. Don't label distances conservative upper bounds without evidence about missing pipeline segments.

Initial explicit scenario assumptions (coordinator may adjust once if inspection shows unusable scale; record changes, do not tune to manufacture impact):

- Capture fraction 0.90; sellable fraction of captured gas 0.95.
- Heating value 1.1 MMBtu/Mcf; 1 m³ = 35.3146667 ft³. These are screening conventions, not measured site composition.
- Seven-year life, 10% discount; constant annual gas for baseline, optional 15% annual decline sensitivity.
- Example capex USD: 250,000 + 350,000 × pipeline_distance_km + 125,000 × (recovered_Mcf_per_day / 100)^0.6.
- Example annual costs: 3% of capex plus $0.50 per sellable MMBtu.
- Baseline price: observed daily-mean Henry Hub benchmark from prepared file (~$2.5336/MMBtu). Low/high scenarios $1.50/$4.00 are assumptions, not forecasts or regional realized prices.
- NPV = −capex + sum(yearly net cash / 1.1^year). No capex double counting. Nonpositive margin has no finite payback.

The exact coefficients live centrally with units and a source/assumption flag. The UI exposes enough to explain the result without overwhelming controls.

### Portfolio rules

Start budgets $2m/$5m/$10m; default $5m. Expose discrete supported values, not interpolated site selections. Expand to $1m/$20m and three prices if useful.

- Financial: maximize total NPV subject to budget, empty portfolio permitted.
- Exposure: maximize aggregate modeled exposure reduction under budget; negative economic returns are allowed but visibly reported.
- Balanced: maximize exposure benefit while retaining at least 95% of the positive Financial optimum's NPV. Disable this preset with explanation if no positive Financial baseline exists.
- Chart: sampled nondominated feasible portfolios from epsilon constraints; start endpoints + 5–8 targets. Do not call it every mathematically possible frontier point.
- Use SciPy/HiGHS or the simplest available integer solver. Cap each solve around 5 seconds; retain feasible solutions and report optimality gaps. If optimality is not proven, label the reference best-found rather than optimal. If unavailable, a deterministic heuristic is acceptable only when clearly identified and checked for feasibility; do not claim optimality.
- Buffer sources are in the regional exposure denominator but are not selectable. Use the same capture fraction for economic recovery and modeled source reduction.

Tests: hand-calculated economics; zero/negative margin; exhaustive enumeration on a tiny selection fixture; budget feasibility; no duplicate or buffer selections; recomputed portfolio totals; nondominance among exported points. Don't write tests that merely duplicate every implementation line.

Sensitivity: a small declared set of lower/higher capex, 50/90/100% capture, and optional decline. Record selection overlap and benefit/value changes. These are scenario ranges, not calibrated confidence intervals. Do not spend the night on 1,000 Monte Carlo runs.

## 8. Agent C: frontend and purposeful behavior

Preserve MapLibre globe and same mounted map across transitions. Improve hierarchy and typography rather than redesigning the app. Use actual inventory points, source IDs, towns, grid and pipeline geometry. Replace fake wedges, dummy speed functions, town circles pretending to be demographic surfaces, and greedy dummy portfolios in the production path.

Layout: map is dominant; left controls and shortlist; right contextual inspection; bottom compact metrics/replay; tradeoff panel expands on demand. Core labels ≥12 px where practical. Confirm at 1440×900 and 1366×768. Avoid overlapping cards and tiny legalistic text; put detailed methods in a drawer.

| Control | Exact purpose and invariants |
|---|---|
| Explore Eagle Ford | Camera transition plus initial regional defaults, only on first entry |
| Explore / Downwind / Capture impact | Change focus; preserve chosen scenario, hour and selection where meaningful |
| Time slider / play / step | Update actual wind and hourly exposure; never change installations or period economics |
| Period average | Pause playback; show aggregate field and period label, not an arithmetic wind-angle average |
| Budget / gas-price scenario | Snap to exported scenarios; preserve named preset if available; load coherently |
| Financial / Balanced / Exposure | Select exact portfolio and update metrics/list/map/chart together; preserve hour |
| Frontier point | Select that exact plan, with a residual map available |
| Baseline / After capture | Same hour, sources, camera and fixed legend scale; only selected source strength changes |
| Fill selector | One of exposure, population density, under-five share, 65+ share; correct units and legend |
| Wind / sources / communities / pipelines / selections | Independent visibility toggles only; no hidden numerical effects |
| Site click / shortlist row | Real site details; outline and focus without changing portfolio |
| Community or tract click | Actual aggregate demographic context and clearly labeled model result |
| Recenter | Camera only; do not reset mode or time |
| Back to Earth | Return camera/view while preserving current regional work |
| Reset demo | Restore all documented defaults, clear selection and pause playback |
| Sources & assumptions | Explain observed vs estimated vs assumed inputs, dates, kernel and financial assumptions |
| Export scenario, if added | Download actual selected IDs, metrics and assumptions; not a decorative button |

Metric strip: capital used, seven-year NPV, annual gas captured, period modeled exposure reduction. Keep current-hour exposure separate. Do not label all residents in the buffered tracts as affected. If a footprint population threshold is added, fix it from baseline and count each cell once; otherwise omit the count.

No generic copy such as “planet intelligence” or “scenario ready.” Replace with useful context: 2023 historical scenario, model coverage, selected-site count, exact units. Name locations only when actual data supplies names; site ID is preferable to an invented well name.

Loading: retain a coherent prior scenario until the next complete bundle is ready. Missing frame pauses playback and shows unavailable; never show stale data with a new timestamp. Unknown values display — with a reason. Empty/negative-return plans remain explainable.

Wind arrows are tied to the actual field. Decorative particles are restrained, aligned and optional; never describe them as computed pollutant particles. Reduced motion removes animation while preserving functionality.

## 9. Coordinator: integration and judge evidence

Assemble validated outputs into browser assets, precompute matching residuals, and keep ordering/version metadata explicit. Target <5 MB compressed initial load and <10 MB per lazily loaded replay bundle, as measured rather than assumed. Compact arrays and remove duplicated geometry first if size is excessive.

Verify the browser, not only `npm run build`. Exercise every visible control on the judge path; inspect console/network errors. Measure a few repeated cached plan switches and playback responsiveness. Target cached switches around 300 ms and 2–4 replay hours per second, but report measured values rather than promising them.

Save evidence at these checkpoints:

1. Real global inventory with year and clear CTA.
2. Regional baseline with readable sources, towns and legend.
3. Two distinct real replay hours, same installations.
4. One site and one community inspection panel.
5. Financial vs Balanced, same budget/hour/camera.
6. Before vs After, same legend and weather.
7. Actual frontier, named plans and numerical axes.
8. Final method/source drawer and offline/degraded-map fallback.

Write `reports/checkpoints/<name>.md`: commit, completed features, checks, screenshot paths, measured performance, unresolved limitations and next action. Do not create a long report after every edit.

## 10. Presentation assets and metrics

Own `presentation/` centrally to avoid edits colliding with frontend work. Generate charts from saved results with Matplotlib (SVG + PNG), not image generation. Browser screenshots must show actual output. Keep export scripts/data alongside figures.

Required files:

- `presentation/pitch.md`: timed three-minute narration with final actual numbers.
- `presentation/slide-outline.md`: 6–8 slides, each with a claim, figure and speaker note.
- `presentation/claims.csv`: claim, value, unit, source/result path, scenario, commit, limitation.
- `presentation/figures/`: architecture/source→transport→population→investment diagram; real wind rose; actual frontier; matched before/after maps; data-coverage card; one sensitivity chart.
- `presentation/screenshots/`: the actual walkthrough and fallback frames.
- `presentation/qa.md`: brief answers on changing winds/fixed equipment, data age, estimated volumes, costs, demographic resolution, and lack of causal health claims.

If time allows, make an attractive locally viewable HTML slide deck using these assets. A polished deck is useful but cannot delay a working product; a complete storyboard and ready-to-use visual pack are the required presentation deliverable. No PPTX dependency is necessary unless requested.

Useful evidence with genuinely strong expected values: 763/763 tract joins, complete weather timestamps, conserved population, 100% budget-feasible displayed portfolios, no residual increases under source removal, exact agreement on tiny solver fixtures. Label these **data quality and implementation verification**, not predictive model accuracy. Actual NPV retained/exposure improvement and timings must be measured after implementation.

Do not target a flattering number by changing labels, suppressing failed results or leaking validation data. Attractive maps can be improved through legibility and consistent scale; unsupported optional features can be dropped. Preserve substantive limitations in the methods and claim ledger.

## 11. Training and segmentation decision

The current core does **not train a neural network**. It combines published satellite estimates, a deterministic wind/population model and discrete optimization. The original PDF explicitly made segmentation a stretch goal, and the retrieved bundle contains no training imagery or masks.

For the main method visual, show the actual data flow or source→community contribution matrix. Do not draw a neural-network diagram and imply it was trained.

An imagery experiment is allowed only after all core gates pass and there is spare time:

- Timebox access/label feasibility to 20 minutes, total experiment about 45–60 minutes.
- Require actual downloadable imagery, usable labels, suitable hardware and a defined held-out split by site/scene.
- Begin with a simple hotspot baseline. Any trained model must be compared against that baseline on independent evaluation labels; agreement with weak training labels alone is not independent validation.
- Save input, actual mask/prediction, overlay, train/validation split manifest, run config, metrics and examples including failures.
- Report IoU/Dice/precision/recall only if actually computed and meaningful; no pixel-accuracy headline dominated by background.
- If access, labels or results are poor, archive the experiment and keep it out of the main demo. Keep its limitation in the report. Do not fabricate segmentation or burn the core polish budget rescuing it.

A learned surrogate of the screening kernel is lower priority: it predicts simulated outputs, not real pollution, and adds little if the demo is already precomputed. Do not add ML merely to produce a training curve.

## 12. GitHub coordination and recovery

**Regular GitHub checkpoints are mandatory; constant conflicting Git operations are not.**

- Coordinator alone runs branch changes, fetch/pull, staging, commits, pushes and PR creation. Workers never `git add .`, commit, checkout, reset, stash, pull, merge or push.
- Check Git status/diff at each work handoff and integration milestone. Fetch remote about every 20–30 minutes or at coherent checkpoints to detect collaborator updates.
- Commit and push a meaningful working checkpoint roughly every 20–30 minutes when available, plus each milestone. Avoid empty/churn commits or publishing a known-broken demo just to satisfy a timer.
- Stage explicit owned paths only. Exclude raw bulk downloads, environments, credentials, caches and unrelated workspace documents. Commit final static app assets and reproducible scripts.
- If remote changes overlap, pause the relevant owner, inspect the diff and reconcile centrally. Never force-push away someone else's work. Don't pull/rebase while workers are writing overlapping files.
- Keep a known-good checkpoint. For a bad experimental feature, disable it or revert only its own scoped change after inspecting the diff; no blanket resets.
- After the first complete vertical slice, open/update a draft PR from `codex/flarewise-full-build` to main, attach it to the Codex chat, and keep its description about the final scope and tests. Do not auto-merge.
- On every major checkpoint update `docs/BUILD_STATUS.md` with commit SHA, owners, completed gates, blockers, exact resume commands and next steps. This is the handoff source if context compacts or a new chat takes over.

Only check in completed agent edits after the agent reports them ready. Because the filesystem is shared, a Git commit can accidentally include another agent's partial changes unless paths are inspected carefully.

## 13. Execution gates and time allocation

Estimated 4–6 hour focused run, with a useful integrated checkpoint targeted in the first two hours. This is a planning estimate, not a timer to fill. Stop earlier when deliverables are complete; do not manufacture extra work to use tokens. If the user supplies a deadline, prioritize backward from it.

| Gate | Target | Exit condition |
|---|---|---|
| G0 contract | 0–25 min | Known-good build, parameter/schema freeze, worker ownership acknowledged |
| G1 real vertical slice | ~25–75 min | Actual globe/site + one real exposure frame + one economic detail in UI |
| G2 decision flow | ~75–150 min | Real replay, valid financial/exposure plans, budget controls and consistent before/after |
| G3 complete product | ~150–240 min | Balanced/frontier, all layers/details, assumptions, no dead controls; core checks pass |
| G4 judge package | ~240–300 min | Screenshots, measured charts, storyboard/script/Q&A, browser rehearsal and visual polish |
| G5 bounded extensions | only spare time | Highest-impact pitch extension; full core remains stable and rollback-ready |

Don't wait until all numerical runs finish to integrate. A supplies one real frame early; B supplies economics independently; C uses versioned fixtures temporarily. Root keeps a complete thin slice alive.

When a blocker consumes ~15 minutes or two unsuccessful approaches, select a simple fallback unless it threatens a core invariant. Examples: fewer scenarios instead of many solves; simple SVG chart instead of a new chart library; static field arrows instead of broken particles; scenario sensitivity instead of Monte Carlo; no ML instead of pretending to train.

Cuts in order: optional ML; independent satellite validation experiment; second region; guided animation; extra price/budget presets; particle effects. Preserve global→regional transition, real wind/population, budgeted plans, actual before/after, legible details and honest explanation.

## 14. Extensions ranked by pitch value

Only after G3, and not at the expense of G4:

1. Guided “Present demo” sequence that uses the same real controls and can be exited.
2. Downloadable one-page investment scenario brief/CSV with actual sites and assumptions.
3. “Why this site?” comparison showing financial contribution vs community contribution.
4. Budget-response chart and concise robustness view for stated assumptions.
5. Local HTML slides and a short actual screen recording if reliable tooling is available.
6. Genuine independent-data/model experiment only if feasibility is already demonstrated.

Every extension proposal must state which pitch sentence it strengthens, estimated effort, concrete artifact and fallback. Drop anything whose only justification is “looks like AI.”

## 15. Completion and final handoff

Required:

- Production build passes; all runtime data loads and units are coherent.
- Actual data replaces dummy values along the complete judge path.
- All visible controls work, have a clear purpose, or are removed/disabled with explanation.
- Fixed installations across time; shared legend/weather before/after; portfolios meet budget.
- Reproducible offline numerical pipeline and methods/assumption files.
- Browser check at projector sizes; no overlap blocking critical controls; no console errors on rehearsed path.
- Network-loss recovery: cached analytical assets work; missing external basemap produces an intelligible locally drawn boundary/geography fallback, and screenshots tell the story. Do not bulk-download restricted public map tiles.
- Presentation evidence pack and timed script with supported metrics.
- GitHub checkpoint/PR updated; clear resume/run commands and remaining limitations.

A public deployment is useful if an already configured service is available. Keep local preview working regardless. If deploying, verify the real URL and browser behavior; do not claim GitHub code storage is hosting. No paid resource/account creation is required by this plan.

Final report: repository/branch/commit and PR, local/deployed URL, core features, verification results, presentation paths, known limitations, and any intentionally omitted stretch work. Don't describe planned work as completed.
