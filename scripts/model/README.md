# Exposure screening build

Run from repository root:

```sh
.data-venv/bin/python scripts/model/build_exposure.py
.data-venv/bin/python -m unittest discover -s tests/model -v
```

Inputs are immutable prepared 2023 flare inventory, 2023 ERA5 hourly winds, and ACS 2019–2023 population allocated by tract area to 5 km cells. The build hashes every input plus the central parameter file. All arrays preserve prepared feature order. Sparse archives contain schema/model/provenance metadata; identifiers and replay UTC hours are in the exposure manifest.

Each source is assigned its nearest returned ERA5 grid location in EPSG:32614. Source-to-receptor links at most 30 km are retained. Meteorological FROM directions produce transport vectors (-sin(direction), -cos(direction)). For positive downwind x, the prescribed kernel multiplies crosswind Gaussian width 1+0.15x, distance decay exp(-x/15), and inverse speed/distance 1/(max(speed,0.5)(1+x)). Distances are km. Calm (<0.5 m/s) transport uses exp(-(dx²+dy²)/8), independent of direction. Winds use the local projected axes without a UTM grid-convergence correction, explicitly recorded as a limitation.

Every source has constant strength annual m³/8,760. The annual objective averages **all 8,760 actual hourly records**, then sums cell index times allocated population. Under-five and 65+ components are separate alternative demographic weights; they are not added to population. All 30 buffer sources remain in baseline but cannot be captured. The source archive permits exact linear subtraction of any fixed eligible portfolio's contribution, scaled by the common capture fraction.

The 48-hour replay starts at the UTC midnight with the largest mean circular direction variation across the nine weather locations, excluding calm directions. No intervention outcome enters that choice. This produces 2023-12-10 through 2023-12-11. The early frame is the replay's first actual hour. A separate, bounded wind-height sensitivity uses 48 specified hours (00,06,12,18 UTC on the first day of every month) at 100 m and 10 m; it is not an alternative annual estimate.

Output is a relative screening index, not concentrations, individual exposure, health risk, calibrated dispersion, or observed hourly flaring. The population coverage statistics are not counts of affected people. Source domain, weather mesh, population allocation, calm behavior and cutoff introduce unquantified uncertainty. Tests establish numerical/convention invariants, not predictive accuracy.

Figures in `data/build/exposure/` show observed reanalysis wind distributions and modeled index diagnostics. `validation.json` records conservation, capture monotonicity, ordering, source integration and sparse compute timing/memory checks.
