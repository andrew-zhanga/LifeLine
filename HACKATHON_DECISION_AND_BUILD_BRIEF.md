# Hackathon decision and 24-hour build brief

## Recommendation

Build **Cool First: a Paris building heat map that turns street photos and public data into an inspectable susceptibility score, then uses the map to allocate heat-wave response and plan retrofits**. Add one small cooling-hub outage scenario for Track 3 if the core map is working. Give it a polished 3D *view*, not a claimed heat-fluid or indoor-temperature simulation.

The hook for judges is a short causal story: **see a real façade → watch the model identify exterior solar protection → click the building's evidence card → run a heat scenario → spend a limited budget → see which high-priority areas gain cooling access and which remain exposed.** In an outage, one cooling site goes dark until the planner funds adequate backup power. Every visual change must come from the same calculation shown in the card.

This deliberately starts with data. A beautiful city rendering with unverified scores will be easy to challenge in Q&A. A score with real, clickable evidence can survive Q&A, and 3D can make it vivid.

## The ideas discussed and their tradeoffs

The rubric below is our judgment, **not an official organizer rubric**. It uses the team's earlier weights: sponsor fit 20, public impact 20, distinctiveness 15, evidence/validation 15, 24-hour feasibility 15, demo clarity 10, transferability 5. “Wow” is a separate 1–10 judgment of the three-minute demo. Scores assume each concept is executed as described, not merely pitched.

| Rank | Product direction | Track 2 /100 | Track 3 /100 | Wow /10 | Main upside | Main risk |
| --- | --- | ---: | ---: | ---: | --- | --- |
| **1** | **Cool First: Paris building evidence map + response allocation + small outage extension** | **86** | **80** | **8.5** | New audited façade-label dataset, clear public-health action, one product for both tracks | Mapillary coverage and building joins; scope creep |
| **2** | **Lifeline: Oakland flood scenario → dialysis-service failure → budgeted protection** | **70** | **86** | **9.5** | Most cinematic and a crisp causal failure chain; strong resilience fit | Harder to verify clinic water/power/access dependencies and real flood overlap in 24 hours |
| **3** | **Paris cooling-hub continuity planner focused on heat + outage + backup power** | **78** | **84** | **7.5** | Stronger Track 3 story, smaller build, clear backup-runtime calculation | Less distinctive visual dataset; hub electrical loads and capacities must be assumed |

Score breakdown (fit / impact / distinctive contribution / evidence / 24-hour feasibility / demo / transferability, with maximums **20 / 20 / 15 / 15 / 15 / 10 / 5**): Cool First **20/18/12/12/11/9/4** for Track 2 and **18/17/12/11/9/9/4** for Track 3; Lifeline **13/16/12/10/8/8/3** and **20/18/13/11/10/10/4**; cooling-hub planner **17/17/10/11/12/8/3** and **20/18/10/11/12/9/4**. These are directional estimates; a weak data audit or an unfinished decision panel would lower them materially.

**Why #1 wins overall:** it answers the team's desire to create an open, inspectable dataset and leaves room for a decision demo. **Why #2 is the strongest pure visual:** rising water, closed roads and service loss are legible in seconds; the operational claims need more evidence. **Why #3 matters:** it is a coherent fallback or a contained extension of #1, not a second full product to build simultaneously. The heat-action-plan audit and a city-scale heat CFD model are outside the top three: the audit has a weaker visual decision moment and little Track 3 fit; CFD would require geometry, boundary conditions and validation beyond a 24-hour build.

## What Cool First actually outputs

1. **A building layer:** each building group has a *relative heat susceptibility* score with separate bars for local heat exposure, physical building factors, and observed exterior solar protection. This is **not** a measured indoor temperature, death probability, or AC-status prediction.
2. **An evidence card:** source attributes, image/date/link, the model's shutter/awning result, human correction if reviewed, missing-data flags, and a short reason for the score.
3. **A community-priority layer:** public-health vulnerability at the **Insee 200 m cell** level. Elderly or single-person-household counts stay at this geographic resolution; they are not assigned to individual buildings by floor area.
4. **A decision panel:** choose a heat scenario, staff/cooling-place limits and an illustrative budget; compare a selected response portfolio with “hottest area first.” Output the *modeled vulnerable-person service hours or area coverage*, plus remaining unmet need.
5. **A small Track 3 card:** for 2–3 candidate cooling hubs, show an assumed critical load, usable battery energy, outage duration and resulting operating hours. It does **not** predict which feeder will fail.

## Exact data stack and units

| Input and source | Native unit | What it contributes | Feasibility / caveat |
| --- | --- | --- | --- |
| [BDNB open building database](https://www.data.gouv.fr/datasets/base-de-donnees-nationale-des-batiments) | Building group/footprint | IDs, geometry and available age/envelope/roof/DPE-derived attributes | Download a Paris extract. Inspect actual columns before choosing score features. The [BDNB expert summer-overheating indicator](https://www.bdnb.io/documentation/predictions_isb_dh/) is valuable but may require expert access; it already models several planned inputs. |
| [Mapillary API/coverage](https://github.com/mapillary/api-demo) | Dated street image | New `visible_exterior_shading` labels: shutters/awnings on observable windows; image and building-match confidence | In a preliminary spot check, Belleville had many older traces but few shown after a 2022 date filter; recent 2024/2026 images near République showed façades. **Usable residential coverage has not been counted.** |
| [CSTB national urban-heat indicators](https://www.data.gouv.fr/datasets/cartographie-nationale-des-indicateurs-lies-a-lilot-de-chaleur-urbain) | Published spatial grid/area, confirm in files | Local heat or vulnerability layer | Inspect actual geometry, variable names and Paris coverage before coding. Avoid double-counting its social-vulnerability inputs. |
| [Météo-France MApUCE Paris map](https://meteofrance.com/sites/meteofrance.com/files/files/editorial/ICU_MApUCE_v2025-2_Paris.pdf) | 250 m map | Credible nighttime urban-heat context | The public PDF alone is **not** a ready-to-join geospatial dataset. Use as a cited explainer unless raster/GIS values are obtained. |
| [Insee 200 m gridded data](https://www.insee.fr/fr/statistiques/8735162) | 200 m cell | Population, older residents, single-person households and income indicators | Some small-cell values are imputed for privacy. Use only at cell level. |
| [Paris cooling places: facilities](https://opendata.paris.fr/explore/dataset/ilots-de-fraicheur-equipements-activites/) and [parks](https://opendata.paris.fr/explore/dataset/ilots-de-fraicheur-espaces-verts-frais/) | Site/park | Public access, type, location and available hours | Verify current hours and accessibility; not every listed site is air-conditioned or open during the chosen scenario. |
| [Paris guidance on shutters, awnings and AC](https://www.paris.fr/pages/volets-stores-climatiseurs-quelles-sont-les-regles-a-respecter-avant-toute-installation-35881) | Rule/permit guidance | Feasibility flags for year-round interventions | A photo and rule summary cannot certify permit approval; exterior changes may require planning, heritage and condominium review. |
| [Cesium OSM Buildings](https://cesium.com/platform/cesium-ion/content/cesium-osm-buildings/) or extruded local footprints | 3D geometry | Camera flyover and colored building display | Rendering layer only. Resolve BDNB-to-rendered-building IDs carefully, or extrude the same BDNB footprints used by the score. Cesium is **not** the physical simulation. |

**Do not use a 200 m heat value as if it were measured separately for each building.** All buildings in that cell share the same local heat input; their rank within the cell changes only through building-specific evidence. Do not estimate an individual building's elderly residents by multiplying its floor area by the cell's elderly share. A cell-level planning score can use cell-level demographics without that false precision.

## Data pipeline and scoring contract

```text
BDNB footprints and attributes -----------┐
Urban-heat GIS layer --------------------->├─ spatial join → one building row per BDNB ID
Mapillary image metadata + VLM labels ----┘                 │
human review + image/building matching ---------------------┘
                                                           ↓
                                             physical susceptibility components
                                                           ↓
Insee 200 m grid + cooling sites → cell-level health priority
                                                           ↓
heat scenario + action capacities/costs → allocation → before/after view
                                                           ↓
optional outage duration + hub loads/backup → continuity view
```

**Feature contract for the vision model:** one record per *observed façade*, with `building_id`, `image_id`, `captured_at`, `camera_direction`, `visible_window_count`, `protected_window_count`, `shade_type`, `occlusion_reason`, `building_match_confidence`, `model_confidence`, and `reviewed_label`. `unknown` is valid. The street image cannot see inside a building, and “no visible AC” is not a reliable lack-of-AC label. Store image links and derived labels; attribute Mapillary. Mapillary's [derived-metadata guidance](https://help.mapillary.com/hc/en-us/articles/115001777705-OpenStreetMap-compatibility) permits community publication under ODbL with attribution; review the license of any *combined* dataset before publication.

**First scoring version:** normalize local heat, available building-form/envelope proxies, and audited solar-protection evidence to 0–1. Publish a fixed weighting and each component on the card. If imagery is missing, leave its component `unknown` and report a lower confidence; never interpret missing imagery as no shutters. Make a simple scenario multiplier for more severe weather, while keeping the score a *relative triage index*. Test whether plausible changes to weights reorder the top buildings/cells. Compare with any accessible BDNB expert overheating indicator **only if it was not used as an input**. A vision model can extract a feature; it should not invent the scoring formula without a documented rationale and audit.

**Area action version:** aggregate the building susceptibility distribution within each 200 m cell, then combine it with cell-level vulnerability and walking access to real cooling sites. Optimize a tiny, explicit set of actions (outreach team, extended cooling-place hours, accessible transport, perhaps an interim fan/solar-film program) under staff, hours and illustrative budget constraints. Report *people reached, travel time or service hours under assumptions*, not lives saved. Put structural retrofits on a **months-to-years** timeline. Avoid claiming a single building retrofit changes the temperature of an entire block.

## 24-hour plan with gates

| Time | Build and decision gate | Required artifact |
| --- | --- | --- |
| **0–2 h** | Inspect BDNB columns, heat-layer GIS files and Mapillary images in 2–3 **residential** candidate areas. Pick one where at least ~40 distinct, recent, usable façades can be sampled. | Pilot bounding box, data manifest, image coverage tally; if the threshold fails, keep imagery as a small case study. |
| **2–6 h** | Extract and spatially join building, heat and 200 m layers. Manually check 10 building joins. Hand-label 25–30 images before model evaluation. | Reproducible CSV/GeoJSON and label guide. |
| **6–11 h** | Run VLM, review disagreements, calculate one published score with missingness/confidence. Build clickable map/cards. | Working map, audited primary-label precision/recall, source-linked cards. |
| **11–16 h** | Add 2–3 heat scenarios, cell priority and simple resource-allocation comparison. Freeze the data/model by hour 16. | Baseline vs chosen plan and an explicit output metric. |
| **16–20 h** | Add polished 3D flyover/extrusion using the same building IDs. If core works, add cooling-hub outage/backup toggle. | One reliable three-minute click path; a 2D fallback. |
| **20–24 h** | Validate numbers and image-to-building matches; rehearse Q&A; cache all demo data; record a backup video. | Final open label dataset, method/limits README, demo and pitch. |

**Go/no-go rule:** by hour 6, if building joins or image quality are poor, ship a defensible 200 m health-priority map with a *small* audited photo sample rather than coloring every building with invented precision. By hour 16, if the resource decision is still incomplete, stop 3D work until that decision works. By hour 20, add Track 3 only if runtime arithmetic and site assumptions are visible and coherent.

## Three-minute demo and Q&A stance

1. **0:00–0:35:** 3D Paris flyover; heat-wave scenario colors the pilot. Zoom into two nearby buildings that share the same area heat value but have different physical evidence.
2. **0:35–1:15:** click each building. Show source attributes and a Mapillary façade; reveal the VLM solar-protection label and a human correction. The card states what is unknown.
3. **1:15–2:20:** switch to cell-level health priority, set a staff/budget limit, select actions, and replay. Compare against a naive “hottest first” allocation. Show service access gained and unmet areas.
4. **2:20–2:45:** optional Track 3: 12-hour power outage at a cooling site; the panel calculates backup runtime and how many service hours are lost or restored.
5. **2:45–3:00:** show the open derived dataset, validation result, and one sentence: “We turned climate maps and street photos into a traceable decision about where Paris can protect residents first.”

**What to say if asked about physics:** the 3D city renders buildings and scenario results; it does not solve heat transport around them. Published urban-heat data provide the area exposure. Building-specific attributes provide a relative overheating propensity. An actual indoor-danger threshold requires measured indoor temperatures or calibrated building simulation. **What to say if asked about 2003 deaths:** [the published case-control study](https://www.santepubliquefrance.fr/regions-et-territoires/ile-de-france/article/impact-heat-islands-mortality-paris-during-august-2003-heatwave) supports the importance of nighttime heat, but today's building map cannot be validated against individual 2003 deaths. For current stakes, [Île-de-France's 2025 health bulletin](https://www.santepubliquefrance.fr/regions-et-territoires/ile-de-france/infographie/chaleur-et-sante-en-ile-de-france-bilan-de-lete-2025-infographie) gives a regional impact figure, not a pilot-block outcome.

## Build-agent acceptance checklist

- The pipeline runs from cached raw extracts to building and 200 m outputs with recorded source versions and coordinate systems.
- At least 10 image-to-building joins and 25–30 primary vision labels receive human review; invalid/occluded views stay unknown.
- Every visible score exposes its components, data vintage, and missingness. Shared area values are not presented as building measurements.
- The map has a working click-through from 3D or 2D building to source-linked evidence card; IDs agree across data and visualization.
- The allocation changes a clearly named **modeled** outcome and respects budget/staff/site constraints; a baseline comparison uses the same assumptions.
- The Track 3 extension, if present, shows outage duration, critical kW, usable kWh, and backup runtime without claiming a feeder forecast.
- The deliverable includes an open derived-label dataset, attribution, reproducible method, three-minute demo path, and honest limits.
