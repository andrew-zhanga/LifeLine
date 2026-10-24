# FlareWise presentation evidence pack

- `pitch.md`: timed three-minute narration with measured portfolio figures.
- `slide-outline.md`: seven-slide storyboard with demo cues.
- `claims.csv`: slide-level values, scenario IDs, result paths, source commit and limitations.
- `metrics.json`: full named plans used for the $10m comparison. The app defaults to $5m; Financial and Balanced coincide there.
- `figures/`: SVG and PNG wind rose, sampled frontier, matched annual before/after maps, method diagram, data coverage and sensitivity chart.
- `screenshots/`: actual browser walkthrough at presentation resolution. `00-baseline-prototype.png` is explicitly the original dummy UI, retained only for development comparison; do not use it as evidence of the finished model.
- `qa.md`: concise answers on data age, costs, changing winds, fixed equipment and model limits.
- `sensitivity-source.json`: actual scenario results behind the sensitivity chart.

Recreate figures and text with `.data-venv/bin/python scripts/make_pitch_assets.py` after assembly. Matplotlib figures depict saved results, not fabricated scientific imagery. Numerical artifacts retain full precision; browser arrays have six significant digits. Screenshots are presentation recovery assets, not substitutes for numerical verification.


## Additive simulation and research evidence

See [extensions/README.md](extensions/README.md) for the 3D replay, demographic priorities, stress tests, global inventory and completed satellite-segmentation experiment. The original pitch assets remain available.
