# FlareWise pitch brief for implementation

This is the portable summary of the user-supplied *FlareWise Hackathon Roadmap* (27 pages, Oct 23, 2026), updated for the data actually retrieved and the user's subsequent scope decisions. The original PDF is at `/Users/aditya/Downloads/FlareWise Hackathon Roadmap.pdf` on the original laptop; a new checkout does not need it to execute.

## The decision we help make

**Which flare sites should an operator invest in capturing, given a limited budget, to recover gas value and reduce modeled exposure in surrounding communities?**

Gas flaring wastes potentially useful gas. A financially attractive capture project is not necessarily the project with the greatest community benefit. Wind changes who is downwind; infrastructure should be selected using recurring patterns, not relocated every hour.

The product combines the money and community perspectives in one inspectable investment decision. The memorable interaction is comparing Financial and Balanced at the same budget, then seeing which sites change and what happens to both results. Whether the financial sacrifice is small and the exposure improvement is large must come from actual computed results.

## Judge journey

Earth with dated real flare inventory → fly into Texas → select a flare → replay real changing wind → inspect population and age context → choose a budget → compare Financial/Balanced/Exposure portfolios → inspect before/after and the tradeoff curve → explain the method → return to global expansion story.

The primary persona is an operator's asset or sustainability team deciding where to allocate capital. Lenders and public-interest analysts are secondary users. This is a screening tool; it does not certify a technically feasible construction project.

## What exists now

- React/Vite/MapLibre demo with a globe, smooth regional transition, layer controls and scenario interactions. It still uses dummy values.
- World Bank annual flare workbook, 2012–2024; selected year 2023 with 8,783 positive-volume global sites.
- Texas study box: 392 candidate sites and 30 surrounding background sources.
- Nine ERA5 locations, each with all 8,760 hours of 2023, winds at 10 m and 100 m.
- Census ACS 2019–2023 population/age estimates joined to 763 tracts; 157 named places for inspection.
- A modeled 5 km allocation grid of 7,543 cells that preserves each tract's population and age totals.
- 1,385 pipeline features and 249 available Henry Hub daily benchmark prices for 2023.
- Reproducible retrieval/preparation scripts, hashes and integration checks.

See `../data/verified/README.md` for the complete source and validation record. The existing 17.41% smoke-test improvement is not a product claim: it used an arbitrary fixed set of 20 sites and sampled one hour per day.

## What changes from the original ambitious pitch

| Original stage or claim | Executable version |
|---|---|
| Download nightly detections, filter, cluster | Use already retrieved annual site inventory; no claim of nightly observation processing |
| Flare/routine classifiers | Not required with this inventory; no unsupported routine classification |
| Sentinel-2 segmentation | Optional later experiment requiring actual imagery, labels and independent evaluation |
| Gas volumes, capture cost, decline-aware NPV | Published annual estimated volumes; explicit screening cost model and seven-year NPV; decline only as an assumption sensitivity |
| Pollutant-specific physical transport | Wind-driven relative exposure screening; no calibrated concentration or AQI |
| Demographic and health impacts | Population and age context; no avoided births, lives saved, or causal health-outcome estimate |
| Validation against measured NO₂ | Not yet available; core verification checks math, data and behavior. Independent environmental validation is future work unless a genuine feasible experiment is completed |
| Monte Carlo confidence | Small, interpretable scenario sensitivity first; no probabilistic confidence unless distributions and interpretation are justified |
| Budget optimizer | Real discrete portfolios and a sampled nondominated tradeoff curve |

These decisions preserve the core pitch. They are not permission to silently claim the deferred capabilities.

## Language for the slides

Use: “2023 historical scenario”; “satellite-estimated annual gas volume”; “modeled exposure reduction”; “screening NPV under stated assumptions”; “population allocated within Census tracts”; “fixed installations selected using recurring weather.”

Avoid: “every flare on Earth”; “live pollution”; “we trained a neural network” when none was trained; “20 m exact stack location”; “95% health prediction accuracy”; “17.41% impact” from the test fixture; “guaranteed pipeline access.”

The original competitor comparison and global headline numbers are historical pitch material. Verify any retained external comparison or time-sensitive headline against primary sources before publishing slides; otherwise use the product's concrete capability statement without a sweeping “first/only” claim.

## Three-minute story, filled with final computed numbers

- 0:00–0:25 — Problem and globe: gas is being wasted; deciding where to invest is the problem.
- 0:25–0:45 — Enter Texas; identify the actual historical data and analysis coverage.
- 0:45–1:15 — Show real wind changing which communities are downwind; equipment stays fixed.
- 1:15–1:35 — Inspect one site and one community; connect gas value to population context.
- 1:35–2:15 — Same budget, Financial → Balanced → Before/After. State actual value retained and modeled exposure change.
- 2:15–2:40 — Show the real tradeoff curve and one concise method/verification visual.
- 2:40–3:00 — Explain expansion to more regions and a pilot with better engineering inputs.

If objectives align, say the same investments deliver both benefits. Do not fabricate a tradeoff to match the script. Use screenshots and an exported scenario summary as presentation recovery assets.
