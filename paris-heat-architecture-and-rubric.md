# Cool First — Paris heat risk and resilient cooling

## One-sentence pitch

**When a heat wave hits Paris, Cool First identifies the buildings most prone to overheating, shows which neighborhoods contain vulnerable residents, and helps the city choose a feasible mix of outreach, passive cooling, and outage-resilient cooling hubs under a budget.**

The two submissions share one product. **Track 2** asks whether scarce public-health help reaches the people most exposed to heat. **Track 3** asks whether the places offering relief still function during an electricity interruption. A map alone is the input; the judged outcome is a better allocation decision.

## What the product measures

There are three distinct outputs. Keeping them separate prevents a precise-looking but misleading “death risk per address.”

| Output | Unit | Meaning | Appropriate use |
| --- | --- | --- | --- |
| Building heat susceptibility | Building or building group | Estimated tendency to overheat under the same weather, given observed or recorded physical features | Find candidates for building surveys and retrofits |
| Community priority | Insee 200 m cell | Exposure × population vulnerability × limited access to relief | Prioritize area-level outreach and service placement |
| Cooling continuity | Candidate public cooling site | How many service hours a site can maintain under a specified power-loss scenario | Compare backup-power and passive-cooling options |

The building score is **not an AC detector**. Mapillary shows the street-facing exterior, not the inside of apartments. The lack of a visible outdoor unit cannot establish that a home lacks AC. DPE cooling-system fields exist, but the subset of homes with DPE records is not a complete census. France already has [national heat-vulnerability data](https://www.data.gouv.fr/datasets/cartographie-nationale-des-indicateurs-lies-a-lilot-de-chaleur-urbain) and a [BDNB expert overheating estimate](https://www.bdnb.io/documentation/predictions_isb_dh/), so the honest novelty is street-level evidence, coverage/uncertainty, and a constrained action planner.

## Architecture

```text
Published data                         Street imagery
BDNB buildings + DPE                   Mapillary dated images
Météo-France heat layer                VLM labels + human audit
Insee 200 m age/living-alone           shutters, shade, visible equipment
Paris cooling places                   image coverage and confidence
            \                         /
             -> spatial join -> building susceptibility
                            -> area priority
                            -> candidate actions + feasibility rules
                            -> budget/outage scenario optimizer
                            -> map, evidence card, before/after comparison
```

### 1. Choose a pilot and lock the data

Start with **3–6 adjoining 200 m cells** and roughly **50–150 residential building groups**. Belleville/Ménilmontant is a candidate, pending an actual façade count. An initial [Mapillary coverage demo](https://mapillary.github.io/api-demo/) spot check found broad older coverage around Belleville but sparse visible traces there after filtering to 2022 onward; recent examples near République showed façades. See the [heat-map v1 feasibility note](heat-map-v1.md). In hour 1, sample candidate residential blocks and count usable, recent, front-facing views; date and direction matter. If fewer than about 40 usable, geographically spread views are found, move the pilot. Do not label unphotographed buildings as lacking shutters.

Ingest a small, cached extract rather than all of France: [BDNB building groups](https://www.data.gouv.fr/datasets/base-de-donnees-nationale-des-batiments), [Insee 200 m grids](https://www.insee.fr/fr/statistiques/8735162), [Paris cooling places and opening times](https://opendata.paris.fr/explore/dataset/ilots-de-fraicheur-espaces-verts-frais/), and an urban heat layer such as the [CSTB indicators](https://www.data.gouv.fr/datasets/cartographie-nationale-des-indicateurs-lies-a-lilot-de-chaleur-urbain). [Météo-France's Paris MApUCE map](https://meteofrance.com/sites/meteofrance.com/files/files/editorial/ICU_MApUCE_v2025-2_Paris.pdf) shows modeled air-temperature differences at 250 m and supports the story; check whether its underlying data are accessible before treating it as a computable layer. Record vintage, geometry and license for each source.

The BDNB `ISB-DH` overheating estimate is an **expert** product, not guaranteed in the open extract. Use it only if accessible within the hackathon. Its method already incorporates climate, building form and roof effects, and assumes heat-aware occupant behavior, while excluding AC and fans. If used as a scoring input, it cannot also serve as independent validation of the same score.

### 2. Make the photo model narrow and testable

Sample by street segment rather than selecting only photogenic buildings. Have a VLM return structured labels for: `exterior_shading_visible`, `street_tree_shade_visible`, `visible_cooling_equipment`, `facade_obstruction`, `capture_date`, and `confidence`. “Unknown/occluded” is a real result. Prefer one image per façade/segment, and store source image ID and attribution. Human-review 25–30 diverse images, including positives, negatives, and occlusions. Report precision and recall for **one primary label** (for example, exterior shading); use the other labels as exploratory evidence. If the label performs badly, remove it from the risk score but keep the audited examples.

The score must not infer apartment occupancy, AC status, indoor temperature, medical condition, or whether someone lives alone from photos. Published [DPE data](https://www.data.gouv.fr/dataservices/api-dpe-logements) can provide some technical attributes, but unmatched or missing records stay unknown.

### 3. Compute transparent scores

Use a small, explicit feature model rather than an untrained black box:

```text
building_susceptibility_b = weighted combination of
  roof/top-floor exposure, building/envelope data, solar orientation,
  externally visible shade, and surrounding vegetation

area_priority_c = exposed_population_c × heat_intensity_c ×
  vulnerable_population_factor_c × relief_access_gap_c
```

Scale components to 0–1 using declared thresholds and show every component on click. Missing imagery does **not** equal zero shade; calculate a base score from published data and add a photo adjustment only where observations pass quality checks. Attach a coverage and confidence badge. Perform a sensitivity check: if reasonable weight changes reorder the top cells, show a priority band rather than a single authoritative rank.

Insee has age and single-person-household variables at 200 m, with some privacy-driven imputation. These are **area indicators**, not evidence that an elderly person occupies any particular building. Public view: building *thermal susceptibility* and grid-cell *health priority* on separate layers. An authorized health department can use its existing [Paris REFLEX opt-in register](https://www.paris.fr/pages/paris-s-adapte-au-changement-climatique-18541) for person-level contact; the hackathon app does not generate a list of inferred vulnerable residents.

Use scenario weather to change intensity, not to pretend that satellite pixels measure indoor air. [Landsat land-surface temperature](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2) is useful context but measures a surface, and imagery is intermittent/cloud-sensitive. [ERA5 hourly 2 m air temperature](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_HOURLY) is about 28 km per pixel, so it cannot resolve Paris blocks. For the 24-hour build, published urban-heat maps plus one clearly labeled historical or synthetic heat-wave scenario are safer than a new microclimate model. Add air pollution only if time-matched local data and a defensible distinct health role are available; do not simply add a pollution score to heat and double-count disadvantage.

### 4. Turn the score into two decisions

**Track 2 — this heat wave (hours to days).** Choose which grid cells receive an outreach team, which existing cooling place gets extended hours, and where accessibility/transport support is needed. Candidate action effects are **assumptions** such as additional staffed hours or residents within a 10-minute walking route, not a claimed reduction in deaths. Optimize `vulnerability-weighted people-hours with access to relief` under staff hours, site hours, transport capacity, and budget. Compare against “serve the hottest cell first.”

**Track 3 — continuity under a power interruption.** Put a 4-, 12-, or 24-hour outage scenario on selected cooling hubs. Model critical electrical load (ventilation, lights, communications, accessibility equipment and any active cooling) and show the hours supported by an assumed battery, generator, or solar-plus-storage configuration. `usable_kWh / critical_kW` is an upper-bound runtime before discharge rate, efficiency, charging, fuel, and site constraints. Optimize which candidate hub upgrades preserve the most vulnerable-person service hours within a second hypothetical budget. Label site loads and infrastructure as assumptions until a site operator confirms them. Paris's [resilience assessment](https://cdn.paris.fr/paris/2023/05/23/mie-paris-a-50-Moer.pdf) describes electricity interruptions during the 2003 heat wave, providing a real rationale for the compound heat-plus-outage scenario. The demo need not claim to forecast which feeder will fail.

**Between heat waves (months to years).** Queue passive retrofits: interior solar film/blinds, exterior shutters/awnings, roof improvements, and trees. [ADEME recommends passive cooling measures](https://www.ademe.fr/presse/communique-national/avis-de-lademe-vagues-de-chaleur-la-climatisation-va-t-elle-devenir-indispensable/). [Paris's current guidance](https://www.paris.fr/pages/volets-stores-climatiseurs-quelles-sont-les-regles-a-respecter-avant-toute-installation-35881) says exterior changes can require planning and condominium approval; heritage rules matter. Show each as “possible,” “needs review,” or “not applicable under an explicit rule.” Never label a specific retrofit legally approved from a photo alone. These longer-term actions belong on a separate timeline from emergency response.

### 5. Validate the parts that can be validated

| Claim | Verification in 24 hours | Remaining limit |
| --- | --- | --- |
| VLM finds visible shutters or awnings | Blind human audit; confusion matrix for primary label | Only seen façades and image dates |
| Spatial joins are correct | Manually inspect 10 mapped buildings and 3 grid cells | Source geometry and vintage may differ |
| Priorities are robust | Compare with published heat layer; vary score weights; baseline ranking | Correlation with inputs is not outcome validation |
| Optimizer helps | Compare chosen portfolio to a fixed baseline under the *same* assumptions | Modeled benefit, not measured health benefit |
| Backup lasts long enough | Calculate kW, kWh, reserve, efficiency and duration; reveal unmet hours | No audited electrical drawings/site loads |

Use 2003 as the **historical motivation and a plausibility check**, not a backtest of today's building scores. A [published Paris case-control study](https://www.santepubliquefrance.fr/regions-et-territoires/ile-de-france/article/impact-heat-islands-mortality-paris-during-august-2003-heatwave) found an association between night-time thermal exposure and mortality among older people, but its individual health records are not an open building-level label set. Building stock, population and interventions have changed since 2003. For a recent stakes slide, [Santé publique France estimated 557 heat-attributable deaths across Île-de-France in summer 2025](https://www.santepubliquefrance.fr/regions-et-territoires/ile-de-france/infographie/chaleur-et-sante-en-ile-de-france-bilan-de-lete-2025-infographie); that is a **regional** estimate, not deaths attributable to the pilot cells or preventable by this app.

## Hackathon scope and division of work

**Minimum shippable demo by hour 18:** real Paris pilot data, a building susceptibility layer, a separate 200 m community layer, 40+ usable images if coverage supports them, one audited VLM label, three emergency actions, a transparent budget choice, and before/after *modeled* service coverage. Use static GeoJSON/JSON to keep the demo reliable.

**Track 3 addition by hour 22:** two or three candidate cooling hubs, one outage toggle, editable critical load, backup options, runtime arithmetic, and a constrained choice of upgrades. This is the differentiator for SE Ventures. Leave predictive outage mapping, full building energy simulation, automatic permit rulings and real-time citywide image ingestion for later.

Five workstreams can proceed in parallel: (1) geodata and joins, (2) Mapillary access/VLM audit, (3) scoring and sensitivity, (4) action/backup optimizer, (5) map/interface and pitch. At hour 4, decide whether imagery and BDNB expert data are usable; at hour 12, freeze the model and prioritize a complete click path. The interface can be MapLibre/React or a simple Python backend and static front end. No 3D city or live API call is required during judging.

## Three-minute judge story

1. **Stakes (0:00–0:30):** Show a Paris heat-wave headline and the 2025 Île-de-France health figure, clearly labeled by geography. “Existing heat maps show exposure; our tool decides what to do with limited resources.”
2. **Evidence (0:30–1:15):** Click two buildings in one 200 m cell. Reveal observed shutter/shade labels beside BDNB data, sources, image dates, and uncertainty. Show that the health-priority grid remains separate from buildings.
3. **Track 2 decision (1:15–2:10):** Give the city a hypothetical €250,000 response/retrofit budget and limited staff. Optimize. Compare outreach and extended cooling-place hours with a heat-only baseline. Show additional *modeled service hours* and the residual unmet area.
4. **Track 3 decision (2:10–2:45):** Toggle a 12-hour outage. A chosen cooling hub loses active cooling after its assumed backup expires. Add a right-sized backup and replay. Show critical load, usable energy, supported hours and cost.
5. **Close (2:45–3:00):** “Cool First links heat exposure to action and keeps relief available when power fails.” Name the pilot scale and the validation achieved.

## Sponsor-oriented rubric (our estimate, not the organizers' official scoring)

Weights reflect the prompts supplied by the team: Track 2 rewards public-health action; Track 3 rewards power and service continuity. Scores are for the **concept as currently spoken** and for the **focused plan above if actually built and audited**. A strong pitch alone does not earn the future score.

| Criterion | Weight | Track 2 now | Track 2 with plan | Track 3 now | Track 3 with outage module |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sponsor/track fit | 20 | 18 | 20 | 9 | 18 |
| Plausible real-world impact | 20 | 16 | 18 | 12 | 17 |
| Distinctive contribution | 15 | 10 | 12 | 9 | 12 |
| Data, validation, honest claims | 15 | 9 | 12 | 8 | 11 |
| Deliverability in 24 hours | 15 | 10 | 11 | 10 | 9 |
| Demo and decision clarity | 10 | 8 | 9 | 7 | 9 |
| Transferability | 5 | 4 | 4 | 3 | 4 |
| **Total** | **100** | **75** | **86** | **58** | **80** |

**Why Track 2 scores better now:** heat exposure, elderly residents, outreach and cooling access answer its health-action question directly. It loses points if it remains only a heatmap or claims unvalidated lives saved. **Why Track 3 is weaker now:** scoring buildings does not keep power on. The cooling-hub outage module gives it a concrete resilience decision, though it is still a service-continuity prototype rather than a grid outage forecast. If build time tightens, protect the Track 2 result first and present Track 3 as an explicit, working extension only if it is finished.

## Main risks and gates

- **Imagery gap:** Mapillary coverage and access may be thin. Gate in hour 1; keep a source-data-only scoring path.
- **Duplicate novelty:** BDNB expert and national heat indicators already exist. Show the incremental street evidence and the chosen actions, not a claim that no heat map exists.
- **False precision:** No indoor photos, apartment-level AC census, measured indoor temperature or address-level mortality validation. Use unknown values, separate geographic levels, and modeled outcomes.
- **Power credibility:** A battery icon must have kW, kWh and runtime. Do not imply that one small battery powers a cooling center for 24 hours.
- **Policy credibility:** Building codes shape interventions; they are not a proxy for current heat exposure. Exterior work requires site review.
