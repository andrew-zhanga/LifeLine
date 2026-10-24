# FlareWise — three-minute judge demo

**The story:** turn a capture budget into an investment decision that accounts for both gas value and people downwind. The decisive moment is the Financial → Balanced switch: roughly double the population-weighted index improvement while retaining 95.5% of financial value.

Read only the quoted narration. Stage directions are for the operator. Rehearse at approximately 140–150 words per minute, allowing the remaining time for transitions. Use the companion `demo-operator-cues.md` for exact controls and recovery. Leave methods, diagnostics and extra controls closed during the main pitch.

## 0:00–0:20 · The problem, on the globe

**Screen:** global home. Begin with the page fully loaded; allow the globe to establish the scale.

> “Gas flaring burns a valuable resource, while communities live downwind. But with a limited capture budget, which flares should we fix first? FlareWise connects the business case to the people affected. We start with 8,783 satellite-estimated flare sites across 77 countries.”

## 0:20–0:40 · Bring the decision to South Texas

**Action:** click **Explore Eagle Ford**. Let the regional map settle. Then open **Simulation workbench** → **Communities**, leaving **$10m** and **All residents** selected; click **Financial** before the next passage.

> “Here in South Texas, we evaluate 392 capture candidates. We connect gas volumes and project economics with a full year of hourly wind data and real Census demographics. The result is a specific investment shortlist, with a clear explanation of which communities benefit.”

## 0:40–1:25 · The investment reveal

**Screen:** Communities, $10 million, All residents. Hold each strategy long enough to see its selected sites and metrics. Financial → Balanced is the hero transition; Community completes the choice.

> “Give us a ten-million-dollar budget. Financial chooses the strongest economic portfolio: 33.6 million dollars in projected seven-year net present value, with a 5.2 percent improvement in our population-weighted exposure index.”

**Action:** click **Balanced**.

> “Now watch the selected sites change. Balanced keeps 95.5 percent of that financial value, while more than doubling the index improvement to 10.6 percent. That's the opportunity this tool uncovers: a better community outcome without giving up most of the business case.”

**Action:** click **Community**.

> “Prioritize communities, and the index improvement reaches 22.2 percent. We can also prioritize actual counts of young children or older residents. Each choice maps back to specific sites and Census tracts.”

## 1:25–2:10 · Make the intervention visible

**Action:** click **Transport**. Use the default 23:00 UTC view, with capture off. Start **Play transport replay**; let the smoke move for several seconds. Click **Install 90% capture** while playback continues. Keep the camera stable so the change is legible.

> “Now make the intervention visible. This three-dimensional wind replay follows emissions as they move from real source locations toward populated areas. The wind, moving plumes and downstream response share the same timeline.”

**Action:** capture on; gesture toward the source plumes and linked chart, without opening another panel.

> “Compare the baseline with capture installed at ten p.m. New emissions fall; material emitted before installation keeps moving. That time delay matters: fixing a source doesn't instantly clear everything around it. The chart connects the intervention to the downstream response. We built this with time-dependent puff transport and GPU-instanced rendering, so the scene stays responsive as more than a thousand puffs move.”

## 2:10–2:40 · Show the trained model

**Action:** click **Satellite lab** (transport pauses automatically). Show the metrics, then scroll down about one screen over the image column to reveal the median and highest-IoU prediction panels. Keep the example labels visible; the headline score remains the aggregate 47.1%, not the best single image.

> “We also trained a U-Net to segment industrial smoke from twelve-band Sentinel-2 imagery. On 374 held-out images, it achieved 47.1 percent intersection-over-union, compared with 23.6 percent for a simple RGB heuristic. Here are the human masks and our model's predictions. This gives us a concrete research foundation for expanding how we observe emissions.”

## 2:40–3:00 · Return to the decision

**Action:** click **Communities**, then **Balanced**. Confirm $10 million and All residents; finish on the selected investment map and its metrics.

> “FlareWise brings satellite data, weather, Census demographics, investment optimization and interactive transport into one decision workflow. The result: retain over 95 percent of financial value while more than doubling the exposure-index improvement. The pitch is simple: don't just find the biggest flares. Find the investments that recover value and put communities into the decision.”

## Keep for questions, not the opening three minutes

- **“What if weather or prices change?”** Open Stress tests. Show fixed-site seasonal performance and the economic scenario range.
- **“How does this account for vulnerable communities?”** On Communities, choose Community, then Under 5 or Age 65+. Explain that the optimization uses actual demographic counts. Use $5 million to show a distinct age-priority selection.
- **“Is this global?”** Open Global inventory and search a country. The inventory is global; the completed investment analysis is South Texas.
- **“Did you really train it?”** Show Satellite lab's split, held-out scores and image examples; the checkpoint and reproducible training scripts are saved.
- **“How fast is the rendering?”** Open Transport diagnostics while playing. The recorded local test was approximately 60 FPS with 1,241 visible puffs. Describe the current live measurement if it differs.
- **“Can we inspect a source?”** Select a source in Transport to frame its plume; the external satellite-map link opens its coordinates.

## Numbers to memorize

| $10m portfolio | Seven-year NPV | All-resident index reduction |
|---|---:|---:|
| Financial | $33.64m | 5.25% |
| Balanced | $32.13m | 10.61% |
| Community | $19.72m | 22.22% |

Balanced retains **95.51%** of Financial NPV. The percentages above describe the population-weighted model index, not measured disease reductions. The transport replay and satellite experiment are distinct components; do not describe the U-Net as controlling the displayed plumes. These distinctions need not interrupt the main pitch: the narration already names what each result measures.

Evidence: `presentation/extensions/README.md`, `reports/extensions/verification.json`, `data/build/experiments/results.json`, and `reports/extensions/performance-1366.txt`.
