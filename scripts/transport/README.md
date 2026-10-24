# Bounded historical puff transport

```sh
.data-venv/bin/python scripts/transport/build_transport.py
.data-venv/bin/python -m unittest discover -s tests/transport -v
```

`data/build/transport/scene.json` is an additive `transport-puff-v1` visualization model. It is **separate from annual screening-v1**. It follows eight actual flare inventory sources for 2023-12-10 20:00 UTC through 2023-12-11 04:00 UTC, starting with an empty domain. Capture begins at 22:00 UTC. Selection is deterministic: highest sum annual screening benefit within a 12 km eligible-source neighborhood containing at least four sources, then the eight nearest eligible sources. This is a local explanatory scenario, not a new optimal portfolio.

## Scientific conventions

Annual flared m³ divided by 31,536,000 seconds is a constant volume-proxy rate. Every 120-second interval emits exactly rate × 120 as one puff at its midpoint. The nearest returned 100 m ERA5 weather grid location is assigned to each source; its actual hourly meteorological FROM winds become east/north velocity (-speed·sin(direction), -speed·cos(direction)). Velocity vectors are linearly interpolated in time. Midpoint advection with 60-second steps is exact for these piecewise-linear hourly velocities, apart from boundary event timing.

Each puff is a normalized horizontal Gaussian times a vertically ground-reflected Gaussian. Initial horizontal sigma is 80 m, vertical sigma 20 m, release height 60 m. Variances grow by 2Kt, with assumed horizontal diffusivity 120 m²/s and vertical diffusivity 5 m²/s. Reflection conserves vertical mass above ground. There is no loss to chemistry or deposition. A puff is removed and its full mass counted as exited when its center leaves the ±25 km horizontal square. Its infinite Gaussian tail is never spatially truncated: this is an approximate open boundary, not a rigorous finite-volume boundary flux. The 0–2,000 m vertical bounds are display bounds only.

Capture multiplies **only new post-installation puff masses** by 0.1. Old masses, paths and spreading are unchanged. Shared nonnegative Gaussian weights ensure capture cannot increase any receptor proxy. Source identity is retained in every puff and every receptor curve.

Receptors are actual prepared population-cell representative points: the closest populated cell and up to two most populous cells in each compass octant within 25 km. Their population is a contextual allocated-cell count; the curve is a point proxy, not a community average or regional exposure. Source emission factors are unavailable, so this model predicts neither pollutant concentration nor health risk. Units are m³ flared-gas proxy per m³ idealized model space; render this as a **relative transport proxy**.

## Export / UI contract

Every output has schema/model version and hashed provenance. See the real two-frame `example.json`.

- `origin`: geographic longitude/latitude and projected EPSG:32614 x/y in metres. Local coordinates subtract that origin; x east, y north, z up (grid-convergence approximation declared).
- `sources`: stable source ID, geographic/local coordinates, release height, annual volume, rate, assigned weather ID.
- `receptors`: stable cell ID, geoid, geographic/local coordinates and allocated population.
- `capture`: 90% fraction, actual install UTC and elapsed seconds, exact source IDs.
- `puffs`: stable ID, source index, midpoint birth elapsed seconds, baseline and capture mass. Index in this array is the puff index.
- `frames`: 97 frames at five-minute intervals. Each contains UTC, elapsed seconds, actual interpolated per-source east/north wind and compact puff rows `[puff_index,x_m,y_m,z_m,sigma_horizontal_m,sigma_vertical_m]`.
- `receptor_series`: baseline/capture arrays `[frame][receptor]` and baseline_per_source/capture_per_source `[frame][source][receptor]`. Values sum exactly over source dimension. Curves use unrounded scientific states; exported centimeter geometry reconstructs them to a reported negligible tolerance.
- `mass_budget`: per-frame per-source emitted, remaining, exited, captured-at-source, capture-remaining and capture-exited volumes.

Display may interpolate between states; new puffs cannot appear before birth. Initial birth coordinates and sigma are explicitly available. Interpolation is visual only and does not modify scientific exports. Transparent Gaussian envelopes are a rendering aid, not measured smoke density. If height is exaggerated, label its factor. The scene includes all scientific puffs; a render-only particle reduction must be disclosed and must not change receptor curves or masses.

## Verification

`diagnostics.json` reports mass budgets, 60/30-second advection convergence, **120/60-second emission-pulse sensitivity**, coordinate-rounding error, build time, byte/gzip size and peak memory. The pulse sensitivity is meaningful even when the advection test is numerically exact. Current receptor L1 difference at twice the emission resolution is 0.453%; this numerical sensitivity is not a physical confidence interval.

Tests independently check meteorological signs, zero emissions, unchanged old material, unchanged paths, mass including exits and capture, Gaussian normalization/reflection, deterministic runs, timestep convergence, actual IDs/timestamps and per-source sum reconciliation. The model remains uncalibrated: release heights, diffusion, constant activity, empty initial condition, source subset and coarse winds introduce unquantified uncertainty.
