# FlareWise execution status

## Current delivery

Core build and presentation evidence pack complete. Branch `codex/flarewise-full-build`; draft PR [#1](https://github.com/andrew-zhanga/LifeLine/pull/1), deliberately not merged. Implementation checkpoint `51e086b`; final evidence commit follows this status entry. All three workers have completed and are idle; coordinator owns final handoff. Unrelated untracked user documents remain untouched.

| Gate | Status |
|---|---|
| G0 contract / baseline | Complete — e4bb5ec |
| G1 real vertical slice | Complete — real inventory, exposure, economics |
| G2 decision flow | Complete — 3 budgets, 25 exact plans, 48-hour replay |
| G3 product integration | Complete — 534a98b, then failure/focus polish 51e086b |
| G4 presentation / rehearsal | Complete — figures, screenshots, claims, script, storyboard, Q&A |
| G5 optional extensions | Actual JSON scenario export delivered; ML/extra regions/HTML deck omitted |

## Verified outcomes

- Prepared source inputs preserved; 19/19 available raw hashes matched. Input hash baseline: reports/input-integrity.json.
- Full 8,760-hour annual screening, 422 sources, 7,543 cells, 71,862 sparse links. Real Dec 10–11 replay. Rebuild 57.24 s, peak RSS 1.106 GB.
- Three budgets at observed $2.533574/MMBtu benchmark; 25 named/frontier plans, all solves optimal. Eight sensitivity cases.
- Eight model + six portfolio + four UI-adapter tests pass. Ten model invariants, seven portfolio export checks, and every plan's assembly budget/totals/order/monotonicity checks pass. These are implementation verification, not predictive accuracy.
- $5m Financial and Balanced coincide: 4 sites, $4.965m capex, $19.754m NPV, 3.6401% modeled reduction. No invented tradeoff.
- $10m Financial: $33.644m NPV / 5.2479% reduction. Balanced: $32.134m NPV / 10.6107% reduction, retaining 95.51% NPV. This is the main pitch comparison.
- Analytical shared assets 2.560 MB gzip; largest lazy plan 0.649 MB gzip. Four cached switches 300–340 ms including automation overhead; replay ~2.52 hours/s.
- Browser walkthrough at 1440×900 and 1366×768: inventory, camera, source/community, real hours, presets/budgets/frontier, before/after, layers, reset, return to Earth, methods and export. No normal-path console errors recorded.
- Missing residual test retained prior complete scenario, then recovered when file restored. User-facing errors are concise. Local-geography fallback captured with Basemap disabled.

## Git checkpoints

- e4bb5ec — frozen runtime contracts, dependencies and input integrity.
- 3c38635 — verified full-year numerical outputs and portfolio solver.
- 534a98b — real-data frontend and committed static assets; draft PR opened/attached.
- 51e086b — concise failure recovery and meaningful map focus, no scenario resets.
- Final evidence checkpoint: see current branch HEAD and reports/checkpoints/02-browser-and-presentation.md. Asset provenance records the implementation commit used for generation.

## Run / reproduce

Working production preview: http://localhost:5173. Development preview: http://localhost:5174. Existing preview on 5173 predates this run and was preserved; current dist contains the final build.

```sh
cd demo
npm ci
npm run dev -- --port 5174
npm run build
npm exec vite preview -- --host 127.0.0.1 --port 5173
```

Numerical rebuild from project root (prepared inputs already committed):

```sh
python3 -m venv .data-venv
.data-venv/bin/pip install -r scripts/build-requirements.txt
.data-venv/bin/python scripts/model/build_exposure.py
.data-venv/bin/python scripts/portfolio/build.py
.data-venv/bin/python scripts/assemble_app.py
.data-venv/bin/python scripts/make_pitch_assets.py
.data-venv/bin/python -m unittest discover -s tests/model -v
.data-venv/bin/python -m unittest discover -s tests/portfolio -v
node --test tests/ui/data.test.mjs
```

## Ownership and remaining boundaries

A completed scripts/model, data/build/exposure, tests/model. B completed scripts/portfolio, data/build/portfolios, tests/portfolio. C completed demo/src, tests/ui. Coordinator alone performed Git operations, assembly and evidence generation. No active worker writes remain.

Relative screening index, not measured pollutant concentration, health prediction or a trained model. Constant annual activity, uniform tract-area population allocation, coarse wind mesh, uncalibrated kernel, assumed costs/capture/gas composition, unknown pipeline rights/capacity. 30 buffer sources remain background. No public deployment was configured. Basemap/fonts use network; local geography/system fonts provide a fallback, but disconnected cold boot/service-worker caching is not claimed. Existing MapLibre main-chunk size warning is nonfatal. Layers drawer intentionally overlays part of the right side when open and can be closed/scrolls.

Presentation entry: presentation/README.md. Use pitch.md and slide-outline.md with the corresponding claims.csv. Screenshot 00 is the old prototype and must not be used as final model evidence. Further work should be a user-directed extension or engineering validation, not a restart of this completed core build.


## Subsequent authorized extensions

The original completed checkpoint above is preserved. See [EXTENSION_STATUS.md](EXTENSION_STATUS.md) for the completed additive simulation, demographic, robustness and satellite-research work. The separate research network does not change the core screening model into a trained exposure model.
