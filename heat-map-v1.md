# Cool First: heat map first

## Product for the first milestone

An interactive Paris map of **building heat susceptibility**, with an evidence card for each mapped building group. The card shows published building attributes, neighborhood heat exposure, and a traceable street-photo observation. A separate 200 m layer shows community vulnerability. Resource allocation comes after this map and its evidence are credible. Building regulations enter later as filters on retrofit options, not as inputs to the heat score.

## The novel dataset

**Visible solar protection on Paris residential façades.** For each sampled façade, use a vision-language model to locate visible windows and classify exterior shutters, awnings, or neither. The minimal feature is `visible_exterior_shading` with values `yes`, `no`, or `unknown/occluded`. Report the number of observable windows and, only where defensible, the fraction visibly protected. Record the image ID, capture date, camera direction, matched building ID, model output, reviewer correction, and confidence in the image-to-building match. One building can have several façades; one street image may show only one. Never assume the unseen sides have the same treatment.

Why this feature: solar protection is a physical heat-mitigation characteristic; [ADEME identifies it as a key comfort measure](https://www.ademe.fr/presse/communique-national/avis-de-lademe-vagues-de-chaleur-la-climatisation-va-t-elle-devenir-indispensable/). It is more observable and actionable than AC access. A street photo cannot show apartment interiors or prove the absence of air conditioning. Trees and street shade are useful secondary labels, but a winter image with bare trees does not establish summer shade.

### Suggested row schema

| Field | Meaning |
| --- | --- |
| `building_id`, `facade_id` | BDNB/building join and locally assigned façade identifier |
| `mapillary_image_id`, `captured_at`, `source_url` | Reproducible source and age of observation |
| `visible_windows`, `protected_windows` | Human-auditable counts; null when view is unusable |
| `shade_type` | Shutter, awning, both, none visible, or unknown |
| `occlusion_reason` | Trees, vehicle, angle, blur, darkness, cropped upper floor, etc. |
| `match_confidence`, `model_confidence` | Different uncertainties: building association and visual label |
| `reviewed_label` | Human correction on the validation subset |

Publish the **derived labels, code, methods, and image links** as the open-source artifact. Mapillary says derived metadata can be published for community use under [ODbL with attribution](https://help.mapillary.com/hc/en-us/articles/115001777705-OpenStreetMap-compatibility). Attribute each linked image under its [CC-BY-SA guidance](https://help.mapillary.com/hc/en-us/articles/115001770409-CC-BY-SA-license-for-open-data/); keep source imagery linked instead of bundling photos into the dataset. Check the final merged-data license before releasing a combined export.

## Mapillary feasibility check completed so far

On 23 October 2026, the [official Mapillary API demo](https://mapillary.github.io/api-demo/) showed many image traces around Belleville before date filtering. An opened example was from **14 March 2016** and looked down a tree-lined street; it was too old and too oblique to support a broad residential façade claim. Filtering the map to imagery since **1 January 2022** left only sparse traces in the viewed Belleville area. Near Place de la République, the same filter showed denser traces; opened examples from **27 June 2024** and **22 August 2026** displayed façades clearly, though they were around a major square rather than a representative residential block. This is a **visual spot check, not a coverage count**. The next gate is to select several candidate residential blocks and tally distinct usable façades, not just green image dots.

## Data layers and score design

1. **Building base:** [BDNB](https://www.data.gouv.fr/datasets/base-de-donnees-nationale-des-batiments) building geometry and available envelope, age, roof/top-floor proxies. DPE gaps remain explicit. Do not treat a poor winter energy label as a direct summer heat label.
2. **Local heat:** [national urban-heat indicators](https://www.data.gouv.fr/datasets/cartographie-nationale-des-indicateurs-lies-a-lilot-de-chaleur-urbain) or an accessible Paris heat raster. Use [Météo-France's 250 m map](https://meteofrance.com/sites/meteofrance.com/files/files/editorial/ICU_MApUCE_v2025-2_Paris.pdf) for context if its underlying data cannot be downloaded. Do not substitute daytime land-surface temperature for indoor or nighttime air temperature.
3. **Street observation:** exterior solar protection from the new dataset, applied only to observed and correctly matched façades. Buildings without a usable image retain a published-data baseline and an `imagery_missing` badge.
4. **Population and relief, on a separate layer:** [Insee 200 m grid](https://www.insee.fr/fr/statistiques/8735162) age/single-person-household data and [Paris cooling places](https://opendata.paris.fr/explore/dataset/ilots-de-fraicheur-espaces-verts-frais/). Do not assign grid demographics to an individual building.

Display a 0–100 **relative susceptibility index** with component bars: urban heat, building form/envelope, and observed solar protection. Publish the weights and run a sensitivity check. It is a triage score, not measured indoor temperature or a predicted death probability. Keep the image contribution small until human review shows it is reliable. If the public BDNB data lack a key feature, show unknown rather than fill it with a guessed number.

## Build order and pass/fail gates

1. **Coverage gate:** compare 2–3 candidate residential clusters, including Belleville only if recent images are usable. Sample about 20 distinct façades per cluster. Pick the one with at least 40 usable, recent, distributed façade observations; otherwise make the published-data heat map the first deliverable and treat photo labels as a small case study.
2. **Join gate:** manually verify 10 image-to-building matches on the map. A camera point on a street is not the building location; use bearing and manual review where needed.
3. **Vision gate:** label 30 images by hand before relying on the model. Measure precision/recall for exterior shading and inspect errors by image age, angle, and occlusion. The first demo only needs one feature that works well.
4. **Map gate:** ship clickable building cards with score components, image links, capture dates, observed/unknown status, and source attribution. Ship the 200 m community layer separately.
5. **Decision gate:** after the map is stable, add an allocation panel for outreach, cooling-place hours, and retrofit candidates. Put building-code and condominium checks here. Emergency action and year-round retrofit should have separate timelines.

## Judge demo for the first milestone

“Existing maps tell Paris where it is hot. We make the buildings inspectable. Here are two buildings in the same hot area. This one has a photographed, reviewer-confirmed exterior shade feature; this one has an exposed visible façade. Click either to see its physical data, the exact photo, and what is unknown. Now switch to the community layer to see where those physical exposures overlap with vulnerable residents. That is the input to our response planner.”
