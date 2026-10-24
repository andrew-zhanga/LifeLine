# LifeLine · FlareWise demo

An interactive hackathon prototype for exploring gas flares, wind, communities, and capture-project trade-offs.

## Run locally

```sh
cd demo
npm ci
npm run dev -- --port 5173
```

Open http://localhost:5173. Requires Node.js 20.19+ or a compatible newer release.

## Build

```sh
cd demo
npm run build
```

The production files are generated in `demo/dist`.

## Explore

- Interactive globe and camera flight to Eagle Ford, Texas.
- Financial, Balanced, and Exposure scenario presets.
- Budget slider updating selected projects and summary metrics.
- Hourly wind playback and illustrative downwind footprints.
- Baseline/after-capture comparison.
- Layer controls for flares, wind, community circles, illustrative pipelines, capture selections, and population/age views.
- Clickable site and community details, plus an interactive scenario chart.

All site locations, financial values, population figures, and exposure results are illustrative. This prototype demonstrates interactions; it does not provide validated financial or health estimates. Map tiles and fonts require internet access.

![Demo preview](demo/screenshots/demo-desktop.png)

See [demo documentation](demo/README.md) for more details.

## Verified data for the next build

The [data bundle](data/verified/README.md) contains prepared 2023 flare, weather, population, pipeline, and gas-price inputs, with source manifests and validation results. The running frontend still uses its original dummy data; integration is the next implementation step.

See the [build contract](data/verified/build_contract.json) for assumptions and scope. Retrieval and preparation scripts are in `scripts/`; large raw downloads and the local Python environment are excluded from Git.

## Coordinated full-build plan

The [execution plan](docs/EXECUTION_PLAN.md) defines the parallel agent roles, feature behavior, calculation contracts, GitHub checkpoints and presentation deliverables. Start a new implementation chat with the [ready-to-paste build prompt](docs/BUILD_PROMPT.md). The [pitch brief](docs/PITCH_BRIEF.md) carries the product context, and [build status](docs/BUILD_STATUS.md) records what is complete versus still planned.
