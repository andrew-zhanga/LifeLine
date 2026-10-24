# Screening economics and portfolio solver

Run from the repository root:

```sh
.data-venv/bin/python scripts/portfolio/build.py --economics-only
.data-venv/bin/python scripts/portfolio/build.py
.data-venv/bin/python -m unittest discover -s tests/portfolio -v
```

The full build requires `data/build/exposure/site-benefits.json` from the final exposure run. It checks source identities, eligibility and the sum of all source contributions before optimization. The economics-only path can run independently. All outputs go to `data/build/portfolios/`; prepared inputs are read only. Dependencies are NumPy, SciPy, Shapely and pyproj, centrally pinned by the coordinator.

Pipeline distances use actual projected line segments in EPSG:32614 and Shapely's nearest geometry index. A clipping edge flag marks sites whose nearest downloaded line is farther away than the boundary of the downloaded geometry. This cannot detect missing pipelines or establish access, capacity, rights or connection feasibility.

Central `contracts/parameters.json` determines capture, conversion, costs, project life, discount, budget, solver time and Balanced retention. Gas recovery uses captured Mcf/day for capacity cost and applies the separate sellable fraction to marketed energy. NPV subtracts installation cost once and discounts seven annual operating margins. Payback is simple capex divided by first-year positive margin; it is null for zero/negative margin and may exceed the seven-year project life.

SciPy/HiGHS solves binary installations subject to capex budget. Financial maximizes NPV and permits an empty selection. Exposure maximizes captured population-weighted source contributions, including projects with negative returns. Balanced maximizes exposure while retaining at least 95% of the Financial reference NPV. A nonpositive Financial reference disables Balanced. Each solve stores its status, gap and elapsed time. A time-limited incumbent is explicitly `feasible_best_found`.

Six intermediate epsilon constraints join the objective endpoints, with duplicate/dominated optional points removed. The result is a sampled frontier, not a complete enumeration of feasible tradeoffs. Named presets are retained even if another sampled point dominates them; `on_sampled_frontier` explicitly identifies chart frontier membership.

Eight bounded $5m sensitivities re-optimize named objectives: 75/125% installation cost, 50/90/100% capture, 15% yearly gas decline, and $1.50/$4 gas. Cost multipliers apply to total installation cost and consequently fixed operating cost. Decline changes future gas cashflows; annual captured volume and exposure values still describe the first-year historical scenario. Selection overlap is Jaccard overlap against the corresponding baseline preset. These are illustrative scenario ranges, not confidence intervals.

Checks include independent hand calculations and exhaustive tiny-fixture selection tests. Export validation separately recomputes totals, budget feasibility, source eligibility, unique selections, Balanced retention and nondominance among exported frontier points. Source hashes make the inputs auditable.
