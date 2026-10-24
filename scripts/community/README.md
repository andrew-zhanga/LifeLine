# Community attribution and seasonal robustness

```sh
.data-venv/bin/python scripts/community/build.py
.data-venv/bin/python -m unittest discover -s tests/community -v
```

Build takes approximately 30 seconds using the existing full-year screening assets. It writes only `data/build/community/` and does not alter original model/portfolio files. All tracts and original enabled plans are retained. Nine additional plans independently maximize all-resident, under-five and 65+ weighted contribution at each supported budget. These weights are actual allocated demographic counts, with no invented vulnerability multipliers. At $2m all three objectives coincide; at $5m and $10m they differ. A negative economic NPV is allowed for demographic-maximizing objectives.

Attribution multiplies each sparse annual source→cell mean by the cell's group count, then aggregates by source and tract GEOID. Capture removes the frozen fraction only for selected eligible sources. Cell counts conserve original tract counts for each group independently. Tract totals reconcile source totals and regional totals. Top-five source lists describe unmitigated contributions; they are not complete sums. A zero-baseline tract has a null reduction percentage.

Robustness recomputes every 2023 hour in four explicit meteorological seasons. December, January and February are grouped within the same calendar year; DJF is not a contiguous chronological winter. Hour-weighted seasonal source means recover the original annual source means. These are within-year scenarios, not held-out estimates or forecasts. No scenario probabilities are assigned.

For each budget, a binary max-min solve maximizes the smallest seasonal **fraction of the seasonal regional baseline removed**, while retaining at least 95% of the benchmark annual Financial plan's NPV. The denominator includes buffer sources. Each result records solver status and gap. These robust solutions happen to match the existing Balanced selections at every supported budget: they demonstrate robustness under the stated floor, not a newly superior selection. The exported objective values remain useful for verifying worst-season performance.

Each fixed plan is also evaluated under benchmark economics, $1.50/$4 gas, and 75/125% installation cost. Installations remain fixed; high installation costs may violate the original budget and are flagged. Fixed operating cost follows the changed capital cost. Scenarios are varied one factor at a time; ranges are not probabilistic confidence intervals. Annual screening-v1 values are distinct from the bounded transport-puff-v1 replay.

`SCHEMA.md` documents frontend fields. `example.json` is a tiny actual-data schema example and is not an alternative full dataset. New plan residuals must be assembled from the existing annual/replay sparse contributions by the coordinator before selecting these installations on the main annual map. Community attribution can use its own plan data immediately.
