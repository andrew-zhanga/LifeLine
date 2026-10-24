# G1/G2 — full-year model and real investment portfolios

Base checkpoint: e4bb5ec. Branch: codex/flarewise-full-build.

Eight model unit/artifact checks, six portfolio checks and three frontend data-adapter tests pass. The assembly validates all 25 plans against source IDs, budgets and independently summed economic totals; every residual cell is nonnegative and no greater than baseline across annual and all 48 replay frames.

A complete 8,760-hour run uses 71,862 sparse links, 422 sources and 7,543 receptors. Rebuild 57.24 seconds; peak RSS 1.106 GB. Replay Dec 10–11 is selected by circular wind variation, independently of intervention results.

Three supported budgets use the observed $2.533574/MMBtu benchmark. All exported solves prove optimal. At $5m Financial and Balanced coincide; at $10m they differ. Eight sensitivities are scenario comparisons, not confidence intervals.

Browser integration verified real global inventory, Earth-to-Texas camera, annual map, first replay hour and actual site economics. Screenshots 01-global.png and 02-region-baseline.png are actual data. Further controls and responsive/fallback rehearsal remain.

Measured compressed analytical assets: 2.558 MB shared initial assets, largest lazy plan 0.649 MB. These are gzip measurements, not a claim that Vite dev sends compressed responses. Browser-performance measurements pending.
