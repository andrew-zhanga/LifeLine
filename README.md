# LifeLine · FlareWise

A historical investment-screening product: **where should a limited flare-capture budget go, considering gas value and people downwind?**

The app preserves the interactive globe and camera journey into South Texas, now using actual prepared 2023 data, a full-year wind-driven relative exposure model and budgeted integer portfolios. The investment model is deterministic screening, not a pollution monitor or health forecast. The additive simulation workbench keeps its transport and satellite research experiments explicitly separate from that annual model.

## Run the app

```sh
cd demo
npm ci
npm run dev -- --port 5174
```

Open [localhost:5174](http://localhost:5174). Node.js 20.19+ or a compatible newer release is required. Static analytical assets are committed under `demo/public/data/`; no source download or Python run is required to use the app.

```sh
npm run build
npm exec vite preview -- --host 127.0.0.1 --port 5173
```

## Judge walkthrough

1. Explore the 8,783-site global 2023 inventory, then fly into the South Texas study box.
2. Step or play December 10–11 hourly weather. Inspect a source and a community. Time changes wind and the modeled field, never installations.
3. Compare exact Financial, Balanced and Exposure selections at $2m/$5m/$10m. At $5m Financial and Balanced coincide; the app explicitly explains that result. At $10m they differ.
4. Switch Baseline / After capture using identical weather and legend thresholds. Click a real frontier point to load its exact matching residual map.
5. Explore population density/age layers, pipelines, sources and real wind arrows. Turn off Basemap to rehearse the local Census-geography fallback.
6. Open Sources & assumptions, or export the selected scenario with actual IDs, metrics and provenance.

## Simulation workbench extension

Open **Simulation workbench** from the header. It adds a smooth Three.js transport scene with actual historical winds, mass-preserving capture and source-focused camera inspection; a Financial/Balanced/Community site comparison with separate Census age objectives; fixed-plan seasonal and economic stress tests; and global country inventory discovery. The Satellite lab presents a separate industrial-smoke segmentation experiment when its verified results are available.

The transport scene uses eight real sources and seventeen cell receptors over eight hours. It is an explicitly assumed Gaussian gas-volume proxy model, distinct from the annual screening calculation. Geography is schematic and height is exaggerated sixfold. Global inventory coverage does not imply global economic modeling. External satellite-map links provide location context; no Street View availability is asserted.

[Extension plan](docs/EXTENSION_PLAN.md), [status](docs/EXTENSION_STATUS.md), and [extended presentation evidence](presentation/extensions/README.md) preserve the original build and document the additions.

```sh
.data-venv/bin/python scripts/transport/build_transport.py
.data-venv/bin/python scripts/community/build.py
.data-venv/bin/python scripts/community/global_inventory.py
.data-venv/bin/python scripts/assemble_extensions.py
.data-venv/bin/python scripts/make_extension_assets.py
```

## Reproduce the calculations

Prepared inputs are in `data/verified/processed/`. Raw acquisition is not needed for this build.

```sh
python3 -m venv .data-venv
.data-venv/bin/pip install -r scripts/build-requirements.txt
.data-venv/bin/python scripts/model/build_exposure.py
.data-venv/bin/python scripts/portfolio/build.py
.data-venv/bin/python scripts/assemble_app.py
.data-venv/bin/python scripts/make_pitch_assets.py
```

Model: 422 sources × 7,543 allocated cells, 71,862 sparse links, all 8,760 hours, actual 48-hour replay. Portfolios: 392 eligible sources, three supported budgets, observed 2023 benchmark price, named objectives and sampled nondominated feasible points. Every displayed point has its own precomputed map. Assumptions are centralized in `contracts/parameters.json`; interfaces in `contracts/app-v1.md`.

```sh
.data-venv/bin/python -m unittest discover -s tests/model -v
.data-venv/bin/python -m unittest discover -s tests/portfolio -v
node --test tests/ui/data.test.mjs
```

## Evidence and limits

The [presentation pack](presentation/README.md) contains the three-minute script, seven-slide storyboard, claim ledger, reproducible figures, screenshots and judge Q&A. [Build status](docs/BUILD_STATUS.md) records Git checkpoints and verification. [Source provenance](data/verified/README.md) documents the retrieved inputs.

Volumes are satellite estimates; hourly source activity is assumed constant. Population is allocated uniformly inside Census tracts. The kernel is an uncalibrated relative index, not concentration or personal exposure. Capture efficiency, heating value and project costs are assumptions; proximity to a pipeline does not establish access or capacity. Solver optimality applies only to the stated screening objective. No measured environmental validation or causal health claim is made.

All analytical assets are served locally. Basemap tiles and optional web fonts use the network; local Census geography and system-font fallbacks keep the regional decision legible. This is not a service-worker-installed offline application. Public deployment is optional and not configured by this build.
