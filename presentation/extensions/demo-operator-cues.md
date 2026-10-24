# Three-minute live demo: operator cues

**Earlier live-rehearsal route.** The final narrated video now uses the problem-first, rubric-aligned `three-minute-script.md`; see `video/README.md` for its updated timing. This click sheet remains a manual product-tour reference, not the final video edit list.

Use this short route for the timed pitch. The longer route in `README.md` is an exploration/Q&A menu, not the live click sequence. These cues are grounded in the current UI and saved results; the coordinator owns the actual browser rehearsal and measured timing.

**Twelve button clicks and one scroll. No budget dropdown, layer menu, camera drag, source dropdown, timeline scrub, or scenario export is needed.** The only live animation is the transport replay. Keep the cursor still while the speaker makes a claim.

## Before the audience arrives

1. Use the already verified production server and the same projector size as rehearsal, preferably 1440×900 or 1366×768. Wait for the home-page **Explore Eagle Ford** button to become enabled.
2. Warm the lazy assets once: open **Simulation workbench**, visit **Communities**, **Transport**, and **Satellite lab**, and confirm that the saved experiment scores/images load. This is preparation, not part of the timed demo.
3. Return using **Investment map**, then click the **flarewise** brand to restore the world/home view. Reload once if previous rehearsals left uncertain state; allow the analytical assets to finish loading before starting. Keep backup screenshots open in a separate window.
4. Confirm reduced motion is not disabling the transport play button. If reduced motion is intentional, retain it and use the static scene/curve explanation or a pre-rehearsed timeline scrub instead; do not diagnose settings live.
5. Do not leave developer tools, Diagnostics, the methods drawer, or a country-inspection overlay open. No external satellite-map link is used in this run.

## Timed click sheet

Times are cue targets, not a claim that browser latency has been measured. Names match visible controls; icon-only controls include their accessible label.

| Time | Click | Exact action | Expected visible state / speaker anchor |
|---|---:|---|---|
| 0:00–0:20 | — | Begin on the world/home view. | Actual 2023 global flare points; 8,783 positive-volume sites. Establish the investment question, not a worldwide optimization claim. |
| 0:20 | 1 | **Explore Eagle Ford**. | Camera enters South Texas. Give the fly-in about two seconds. State 392 capture candidates plus 30 background sources, historical weather and Census context. Do not quote the main map's default $5m metrics as the forthcoming $10m comparison. |
| 0:35 | 2 | Header **Simulation workbench**. | It initially opens Transport at **23:00:00 UTC**, paused, baseline, all eight local sources. This is a brief loading/transition glimpse, not yet the transport explanation. |
| 0:39 | 3 | Top tab **Communities**. | Defaults are **$10m**, **All residents**, **Community**. No dropdown changes are required. |
| 0:42 | 4 | Strategy **Financial**. | Nine selected sites; **$33.64m seven-year NPV**, **5.25%** annual modeled all-resident index reduction. Let the map and readouts settle before speaking. |
| 0:55 | 5 | Strategy **Balanced**. | Ten selected sites; **$32.13m NPV**, **10.61%** reduction. It retains **95.51%** of Financial NPV. This is the main judge moment: same budget, visible change in chosen sites, more than twice the modeled index reduction. |
| 1:10 | 6 | Strategy **Community**. | Nine selected sites; **$19.72m NPV**, **22.22%** reduction. This shows the explicit value/community tradeoff. Point to the ranked tract panel; do not click extra tracts. |
| 1:25 | 7 | Top tab **Transport**. | Returns to the paused **23:00:00 UTC** scene. Introduce the wind replay and its real source locations. Operator context: these eight scene sources are separate from the annual portfolio selection. |
| 1:30 | 8 | Bottom circular play icon, **Play transport replay**. | Clock advances and puffs move smoothly. Default speed is **4 min/s**. Keep all-source focus and the default camera. |
| 1:45 | 9 | Right inspector **Install 90% capture**. | Button becomes **90% capture selected**, status **Capture active**. This switches to a scenario with installation at the fixed **22:00 UTC** marker, not at the current mouse-click time. Newer emissions are smaller; already-emitted material follows the same path. Continue replay while explaining the linked receptor curve. |
| 2:10 | 10 | Top tab **Satellite lab**. | Switching tabs automatically pauses transport. Show saved trained-model results: **47.1% foreground IoU** vs **23.6%** RGB baseline; **374 held-out images**. Read the aggregate score, then scroll down approximately one screen over the image column to show the median and strongest prediction panels. Leave the example labels visible. The aggregate result is 47.1%; the strongest example is 86%, not the overall score. |
| 2:40 | 11 | Top tab **Communities**. | The decision panel remounts at $10m / All residents / Community. |
| 2:42 | 12 | Strategy **Balanced**. | End on the main investment result: $32.13m NPV and 10.61% modeled index reduction. Close with the operator decision and the 95.5%-value / more-than-double-index-improvement result. Finish by 3:00. |

The timed route changes only the three strategy buttons, view tabs, play, capture, and navigation. Returning to Balanced at the end deliberately restores the hero decision instead of leaving the audience in the research appendix. **Stress tests, demographic objectives, Global inventory, source focus, Diagnostics and the remaining controls are Q&A material.** They are useful capabilities, not obligations during a three-minute pitch.

## Exact statements that prevent state confusion

- **Annual comparison:** “At the same $10 million budget, Balanced retains 95.5% of the Financial plan's NPV and raises modeled all-resident index reduction from 5.25% to 10.61%.” These are screening-model results, not health outcomes or measured pollutant concentrations.
- **Transport toggle:** “This compares no capture with capture installed at 22:00. Existing material stays downwind; new emissions shrink.” Do not say “we install it right now” at the current clock time.
- **Transport scope:** The right inspector's proxy is interpolated across **17 sampled receptors**, not a regional population total. The geographic plane is schematic and vertical scale is exaggerated 6×.
- **Satellite result:** “A separately trained 12-band U-Net scored 47.1% held-out foreground IoU, against 23.6% for a simple three-band RGB heuristic.” Different inputs mean this is not an architecture-only comparison. The dataset is European industrial smoke; it does not validate Texas flare detection, gas estimates, or transport.

## State pitfalls and safe recovery

| Symptom | Safe recovery |
|---|---|
| Main map starts at $5m | Expected. The timed comparison is the workbench **Communities** view, which initializes at $10m. Do not spend a click changing the main map budget. |
| Communities already shows Community | Expected default. Click **Financial** first, then **Balanced**, then **Community** so the narrative starts with financial return. |
| A previous rehearsal left the workbench open | Before the timer, use **Investment map**, then reopen **Simulation workbench**. Closing unmounts it and resets its local state on reopen. |
| You leave Communities for Transport and later return | The decision panel can remount at its defaults ($10m / All residents / Community). Reassert **Financial** if repeating the comparison; do not assume the previous strategy survived. |
| Capture is already On | Before the timer, reopen the workbench. During the pitch, do not toggle blindly; read **Baseline emissions** versus **Capture active**. |
| The transport button says Pause rather than Play | It is already playing. Do not click it merely because the cue sheet says “Play”; use the current state. Switching to Satellite lab pauses automatically. |
| Transport reaches the end | Its play action rewinds to the empty start. Avoid this live. The planned ~40 seconds at 4 min/s stays well within the eight-hour experiment. |
| Source focus or orbit looks wrong | **Reset camera** restores all-scene framing but does not clear a source filter. Select **All 8 scene sources** in **Inspect a source** if needed, then Reset camera. This is a recovery branch, not part of the normal route. |
| Data loading/error interrupts a claim | Stop clicking. Use the matching screenshot below and say it is a saved verified run. Retry once only if there is obvious time; do not read stale values as the requested new scenario. |
| Satellite scores/images are unavailable | Use the saved satellite figure/screenshot; say “saved held-out results,” not “training live.” Do not invent scores or wait for training on stage. |
| Presenter is running late | Omit the **Community** strategy click/explanation and go straight from Balanced to Transport. Keep the principal Financial→Balanced result and use the metric names in the narration. Do not add age/stress/global tabs. |

## Prepared recovery assets

- World: `presentation/extensions/rehearsal/01-home.png`.
- Balanced and Community: `presentation/extensions/screenshots/04-balanced.png`, `03-community.png`.
- Transport baseline/capture: `presentation/extensions/screenshots/01-transport-baseline.png`, `02-transport-capture.png`; projector view `08-transport-1366.png`.
- Satellite: `presentation/extensions/screenshots/10-satellite-lab.png` and `presentation/extensions/satellite-experiment.png`.

These are saved runs, not claims of live interactivity. Do not use an older Financial screenshot to assert a $10m state unless its visible budget is checked. The exact $10m numbers above are verified from `demo/public/data/extensions/community/community.json`; satellite metrics are from `demo/public/data/extensions/experiments/results.json`; transport start and installation times are from `demo/public/data/extensions/transport/scene.json`.
