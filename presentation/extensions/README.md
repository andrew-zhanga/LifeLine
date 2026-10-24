# Extended judge demo

This evidence supplements the original presentation rather than replacing its verified historical screening results. Start app at localhost:5173 after production build, or localhost:5174 for development. Open **Simulation workbench** from the header.

## Three-minute path

1. **Global inventory (20 seconds).** 8,783 satellite-estimated sources across77 countries. Pick a country and view its geography. Clearly distinguish global inventory from regional analytical coverage.
2. **Communities (60 seconds).** Set$10m, compare Financial, Balanced and Community on the same site map. Financial yields$33.64m modeled NPV and5.25% population-weighted index reduction; Balanced retains95.51% of that NPV and achieves10.61%; Community achieves22.22% with$19.72m NPV. Inspect a tract and show which source contributions explain its benefit. At$5m, demonstrate under5 versus65+ objectives selecting actual different investments. Counts are ACS estimates, not health multipliers.
3. **Transport (50 seconds).** Explain that this is a distinct bounded transport experiment:8 actual sites,17 selected cell receptors,8 historical hours. Play from before22:00 UTC and toggle capture. New emissions shrink after installation; old puffs keep moving. Point to changing real wind and linked receptor-proxy curve. The landscape is schematic; smoke envelopes depict assumed Gaussian transport, not observed smoke or pollutant concentrations.
4. **Stress tests (30 seconds).** Keep installation choices fixed across seasons and economic cases. Explain that under the95% financial floor, the robust seasonal optimum coincides with Balanced; this is a result, not a missing feature. Cost increases can make a fixed plan exceed budget. These ranges are scenario comparisons, not confidence intervals.
5. **Technical evidence (20 seconds).** Open diagnostics if asked. Describe sparse annual source attribution, binary mixed-integer optimization, time-dependent mass-conserving puffs, numerical refinement checks, and batched WebGL rendering. Satellite lab is a completed research appendix: show held-out metrics and the failure/median/best examples.

## Claim discipline

- Annual screening-v1 and eight-hour transport-puff-v1 are different models. Do not use transport visuals as evidence that the annual optimizer was rerun with that model.
- Population-weighted relative index reduction is not a percentage reduction in disease or personal exposure.
- Selected cell receptor population weights are not whole-community averages or a count of people exposed.
- Gas volumes are annual satellite estimates, and continuous hourly release is assumed.
- Global inventory is not worldwide financial optimization. Second-region feasibility is documented, not modeled.
- Satellite segmentation is a distinct European industrial-smoke research task, not demonstrated Texas flare detection or verification of transport.

## Assets

`demographic-objectives.{png,svg}` shows actual$5m demographic portfolio results. `seasonal-robustness.{png,svg}` shows fixed$10m portfolio seasonal results. Rebuild with `.data-venv/bin/python scripts/make_extension_assets.py`.

Screenshots and rendering measurements were captured in the production browser after verification. Original screenshots under `presentation/screenshots/` describe the previous working checkpoint.


## Completed satellite appendix

A 119,569-parameter U-Net trained from scratch for 24 epochs on 12 Sentinel-2 bands. Train / validation / test: 1,433 / 507 / 374 images, with overlapping locations kept in the same split. Validation selected epoch 21 and threshold 0.4. Held-out foreground IoU is **0.47117** and Dice **0.64054**, versus **0.23554 IoU** for a simple RGB heuristic. The model and baseline use different inputs; do not present this as an architecture-only ablation.

Use `satellite-experiment.{png,svg}` for the learning curve and comparison. The Satellite lab displays actual masks for the lowest, median and highest positive-test scene IoU, including a complete miss. Saved checkpoint and exact split are in `data/build/experiments/`; reproduction and dataset attribution are in `scripts/experiments/README.md`. These European industrial-smoke results do not validate Texas flare detection or pollution transport.

## Rendering evidence

`reports/extensions/performance-1366.txt`: 1366×768 production playback, 180-frame/3-second sample, median 16.7 ms, p95 17.6 ms, 1,241 visible puffs, 39 draw calls, 0% frames over 33 ms. Report the device-specific measurement, not a universal performance promise. `08-transport-1366.png` shows the scene; `09-nigeria-inspection.png` and `10-satellite-lab.png` show the completed added views. Earlier screenshots retain their original viewport sizes.


## Timed live demo

Use [three-minute-script.md](three-minute-script.md) for the spoken pitch and [demo-operator-cues.md](demo-operator-cues.md) for the matching 12-click, one-scroll route. The live browser rehearsal and screenshots are in [rehearsal/README.md](rehearsal/README.md). This shorter route supersedes the exploration sequence above for timed judging.
