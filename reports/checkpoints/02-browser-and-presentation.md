# G3/G4 — judge rehearsal and evidence

Implementation checkpoint: `51e086b` on `codex/flarewise-full-build`; draft PR https://github.com/andrew-zhanga/LifeLine/pull/1. Presentation assets reference the checked-in implementation used to generate them.

## Rehearsed in Chrome

- Real globe inventory (8,783 sites), smooth flight into South Texas, same mounted map.
- Actual December 10 00:00 and December 11 01:00 frames, unchanged selected installations and period economics.
- Site 142545: $2.25m capex, $7.93m seven-year NPV, actual assigned hourly wind. Encinal community: population 992, under-five 1.3%, age65+ 33.9%, explicitly nearest-cell relative index.
- All three budgets, Financial/Balanced/Exposure, and Frontier 3 exact selection. At $5m Financial and Balanced coincide; at $10m Balanced retains 95.51% of Financial NPV and changes annual reduction from 5.2479% to 10.6107%.
- At $2m Exposure, negative NPV remains visible (−$0.53m); it is not silently removed.
- Before/after keeps time, camera and thresholds fixed. Period-average, play/pause, next/previous and slider update actual frames.
- Independent sources/wind/communities/pipelines/selections/basemap toggles; population density and both age shares; meaningful Explore/Downwind/Capture focus; recenter; Back to Earth preserves regional plan/hour; Reset restores defaults.
- Downloaded Financial and Frontier JSON exports checked against saved IDs and totals (reports/export-verification.json). The browser automation download-event waiter timed out, but both files downloaded successfully and were independently read from Downloads.
- Missing-plan recovery tested by temporarily withholding only a generated dist asset. The previous $5m Exposure plan, hour17, selection and metrics remained coherent; restoring the asset allowed $2m loading. Error copy was then improved to a concise data-unavailable message. No source data was removed.
- Sources/methods drawer and intentional Basemap-off local Census-geography fallback captured. This verifies locally drawn fallback; it is not a claim of a fully disconnected cold boot or a service worker.

## Measurements

- Four cached plan switches: 300, 301, 340, 318 ms (median 309.5 ms), measured from automation click to visible matching plan label; includes connector overhead, not isolated GPU render time.
- Replay advanced hour0→17 in 6.741 s (~2.52 hours/s); source list and period economics unchanged.
- Shared analytical assets: 2.560 MB gzip; largest plan: 0.649 MB gzip. Vite may serve uncompressed responses. Full production JS/CSS add 0.535 MB gzip including MapLibre worker; raw main chunk warning remains.
- Normal production rehearsal console: no captured errors/warnings. Intentional missing-asset test is separately identified above.
- 1440×900 and 1366×768 screenshots inspected; details/legend overlap found and corrected. Layers drawer can overlay right-side metrics while open; it has an always visible close control and scrolls at smaller height.

## Evidence and boundaries

Required script, storyboard, claim ledger, six SVG/PNG figures, actual screenshots and Q&A are in presentation/. The $10m tradeoff is the pitch comparison; the $5m alignment is explicitly stated. No model training, concentration validation, health claims or public deployment is claimed. Optional slide deck/ML/extra regions omitted in favor of the finished core.

Final 51e086b failure-copy check: withholding the uncached $2m Financial residual showed the friendly data-unavailable message while retaining the $10m Financial scenario. The file was restored immediately. Final production rebuild and all 18 automated tests pass.
