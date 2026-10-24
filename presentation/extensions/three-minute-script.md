# FlareWise — rubric-aligned three-minute pitch

Final script for the narrated demo. Read only blockquotes; the stage directions and source notes are not spoken. Four judging criteria receive a clear evidence-bearing section: challenge, creativity, technical feasibility and scale. Target: 180 seconds at a confident conversational pace.

## 0:00–0:40 · Sustainability challenge

**Visual:** global home; transition into Eagle Ford near the end. Use a brief opening overlay for the global statistics so the audience does not mistake 2025 totals for the app's 2023 inventory.

> “In 2025, the world burned 167 billion cubic meters of gas through flaring: an estimated 54 billion dollars in wasted value. This is also a community issue. A study in Eagle Ford associated high nearby flaring with fifty percent higher odds of preterm birth. Operators face a practical question: with limited capital, which flares should they fix first? FlareWise connects that investment decision to the people downwind. Recovering gas creates a financial reason to act; targeting the right sources makes community priorities part of the investment case.”

## 0:40–1:25 · Creativity and measurable value

**Visual:** Communities; $10 million, All residents. Financial → Balanced → Community. Let each click settle before reading its result.

> “Our users are operator capital teams, working with health, safety and environment teams and public-health planners. In South Texas, we evaluate 392 candidates using gas volumes, economics, hourly winds and real Census demographics. Give us ten million dollars. Financial delivers 33.6 million in projected seven-year net present value and a 5.2 percent reduction in our population-weighted exposure index. Now switch to Balanced: retain 95.5 percent of financial value while more than doubling that index improvement to 10.6 percent. Community prioritization reaches 22.2 percent. The creative step is making these competing priorities one explicit, inspectable investment decision.”

## 1:25–2:15 · Technical feasibility

**Visual:** Transport, play, then compare capture installed at 22:00. Transition to Satellite lab for the final two sentences.

> “Underneath, integer optimization selects actual projects within budget. Annual analysis uses every hour of weather, while Census attribution shows which tracts benefit. This interactive three-dimensional replay follows moving emissions. Compare capture installed at ten p.m.: new emissions shrink while previously emitted material continues downwind. GPU-instanced rendering delivered about sixty frames per second in our local test. We also trained a twelve-band Sentinel-2 U-Net for industrial-smoke segmentation. On 374 held-out images, its intersection-over-union reached 47.1 percent, versus 23.6 percent for a simple RGB heuristic. These are saved predictions and a reproducible model. Forty-one tests verify the build.”

## 2:15–3:00 · Path to scale and TotalEnergies relevance

**Visual:** return Communities → Balanced for the hero metrics. Optionally use a concise closing overlay: “Pilot → validate → expand basin by basin.” Keep the selected map visible underneath.

> “TotalEnergies has committed to ending routine flaring by 2030. FlareWise could help turn that commitment into a prioritized project pipeline. Our proposed first pilot pairs one asset team's engineering costs and infrastructure constraints with local environmental validation. Success means a shortlist ready for engineering review, with economics and community priorities assessed together. We would measure recovered gas, project returns and independently verified emissions changes. Then expand basin by basin through regional weather, population and infrastructure data. Our global inventory already provides discovery across 77 countries. Our vision is a new standard for climate investment: every dollar evaluated for both economic return and the communities it can benefit. FlareWise makes that future actionable.”

## Sources and claim notes — not spoken

- **Problem statistics:** [World Bank 2026 Global Gas Flaring Tracker](https://www.worldbank.org/en/programs/gasflaringreduction/publication/2026-global-gas-flaring-tracker-report), covering calendar 2025. These are worldwide total-flaring figures, not this application's calculated impact or TotalEnergies' emissions. The app currently displays the separate 2023 World Bank inventory.
- **Health motivation:** [Cushing et al., 2020, Environmental Health Perspectives](https://pubmed.ncbi.nlm.nih.gov/32673511/). The retrospective Eagle Ford study reported OR 1.50 for preterm birth comparing high nightly flare-event exposure with none. “Associated” and “odds” are deliberate. This is motivation for considering communities, not a causal result or a health prediction from FlareWise.
- **Strategic relevance:** [TotalEnergies: Reducing Our Emissions](https://totalenergies.com/sustainability/climate-and-sustainable-energy/reducing-our-emissions), “Eliminating routine flaring by 2030.” The proposed pilot is an opportunity, not an existing partnership; routine flaring does not include safety flaring.
- **Built-product results:** `data/build/community/community.json`, `data/build/experiments/results.json`, `reports/extensions/verification.json`, and `reports/extensions/performance-1366.txt`. Financial and community percentages measure the annual population-weighted index. The separate transport replay illustrates intervention timing; the separate U-Net evaluates European industrial-smoke segmentation.
- **Scale path:** engineering-cost integration, pilot validation, and further regional analytical coverage are proposed next steps. Global inventory is already built. Do not say global financial optimization is complete.

The main narration leads with success and keeps technical distinctions in the nouns: projected NPV, exposure index, replay, held-out segmentation and proposed pilot. It does not require an on-stage limitations detour.
