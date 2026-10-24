# Extension status — completed October 24, 2026

The original build and execution plan remain intact. This is the additive implementation of EXTENSION_PLAN.md. Original checkpoint: `3d7ee12`; planning checkpoint: `ff45117`; numerical checkpoint: `75eee36`; integrated UI checkpoint: `2c22382`. The final evidence commit follows these checkpoints on `codex/flarewise-full-build`, draft PR #1.

## Three workers and review

- Exposure worker: deterministic Gaussian puff transport, mass accounting, real historical wind replay, refinement diagnostics, source/receptor contracts. Reviewed community attribution and frontend interpolation.
- Portfolio worker: actual ACS demographic objectives, tract attribution, fixed-plan seasonal/economic stress tests, robust optimization and global inventory. Independently reviewed transport and the segmentation experiment.
- Frontend worker: Three.js instanced smoke, smooth source framing, synchronized replay controls, community/stress/global views, research lab and responsive diagnostics. Reconciled scientific labels and calculations with both numerical workers.
- Coordinator: integration, production browser testing, actual satellite training/evaluation, presentation assets and Git checkpoints. All workers finished; no worker writes remain active. Cross-review record: `reports/extensions/peer-review.md`.

## Verified deliverables

Transport: 8 real sources, 17 selected cell receptors, 8 historical hours, 97 frames. Emission pulse refinement difference 0.453%; mass accounting passes. Capture preserves material emitted before installation. This is a separate bounded transport experiment, not a replacement for annual screening.

Community: 37 plans, 763 tracts, all-resident/under-5/65+ counts. Seasonal aggregation reconciles with annual results. Robust seasonal selection coincides with Balanced at the tested budgets. Global discovery covers 77 countries and 8,783 sources; analytical investment coverage remains South Texas.

Frontend: production browser checks cover capture timing, source focus, demographic selection, fixed-plan stress, country navigation, satellite results and missing-asset Retry recovery. Measured 1366×768 playback: median 16.7 ms, p95 17.6 ms, 59.9 median-frame FPS, 0% over 33 ms across 180 frames/3 seconds, 1,241 visible puffs and 39 draw calls. This is a short local measurement, not a guarantee across devices. Lazy-loaded workbench; adaptive resolution and hidden-tab pause.

Satellite research: published imagery checksum verified. Trained a 119,569-parameter, 12-channel U-Net from scratch for 24 epochs. Overlapping footprints grouped before splitting: 1,433 train / 507 validation / 374 test images. Validation selected epoch 21 and threshold 0.4. Held-out foreground IoU 0.47117, Dice 0.64054; RGB heuristic IoU 0.23554. The inputs differ (12 bands versus RGB), so this is not an architecture-only comparison. Saved checkpoint, split manifest, learning history, examples including failures, checksum and reproducible scripts are included. European industrial smoke is not validated Texas flare detection.

## Verification and presentation

33 Python tests and 8 Node UI/data tests pass. Production Vite build passes with nonfatal bundle-size warnings (MapLibre and lazy Three.js workbench). Numerical export and research-verification checks pass. See `reports/extensions/verification.json`, assembly hashes and screenshot evidence.

Open http://localhost:5173/ and choose Simulation workbench. Presentation guide: `presentation/extensions/README.md`. No public deployment was configured. Site imagery opens an external satellite-map link; embedded Street View and a calibrated global pollution/health model were not implemented.
