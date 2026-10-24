# Cool First: a Paris heat adaptation planner

## The challenge

**Which Paris blocks should receive help before the next heat wave, and which changes to their buildings would reduce heat exposure most within a limited budget?**

Build a map that joins published heat vulnerability and building data with a small, audited sample of street-level photos. The user selects a heat-wave scenario and a hypothetical adaptation budget. The tool identifies priority **200 m areas**, recommends near-term outreach and longer-term building measures, and replays the scenario to show the *modeled* change in exposure. Its central output is a decision: where to act, what to do, what permissions to check, and what remains uncertain.

This follows the structure of the [Oakland flood challenge](team-pitch.md): a real hazard, a vulnerable service or population, a constrained intervention portfolio, and a before/after demo. The Paris-specific problem is summer **overheating and access to cooling**. Winter heating is a different problem; the model and interventions below are for heat waves.

## Why Paris, and what already exists

Paris's [2024–2030 Climate Plan](https://cdn.paris.fr/paris/2025/06/25/plan-climat-fr-WxE3.pdf) treats summer habitability as a priority. Public inputs already include [national heat-island and heat-vulnerability indicators](https://www.data.gouv.fr/datasets/cartographie-nationale-des-indicateurs-lies-a-lilot-de-chaleur-urbain), [BDNB building records](https://www.data.gouv.fr/datasets/base-de-donnees-nationale-des-batiments), [Insee 200 m demographic grids](https://www.insee.fr/fr/statistiques/8735162), and [Paris cooling-place data](https://opendata.paris.fr/explore/dataset/ilots-de-fraicheur-espaces-verts-frais/). The BDNB also has an [expert summer-overheating indicator](https://www.bdnb.io/documentation/predictions_isb_dh/) that covers much of the housing stock and explicitly excludes actual AC and fans. **Do not claim to invent the first heat-vulnerability map or building overheating estimate.** The new work is a small, inspectable layer of façade observations plus a tool that turns existing maps into feasible actions.

**Pilot:** a few adjoining 200 m grid cells around Belleville/Ménilmontant, subject to a first-hour Mapillary coverage check. This is a manageable visual area, not a claim that these are Paris's highest-risk streets. If image coverage or quality is poor, move the pilot to the best-covered high-vulnerability cells. Pick the final location from the evidence.

## How the system works

1. **Set the baseline.** Load a published heat-vulnerability or urban-heat layer, BDNB footprints/building age and available energy data, Insee age/income indicators at 200 m, and cooling places with opening hours. Keep source dates and missing values visible. A neighborhood's risk is a planning score, **not** an estimate of deaths or indoor temperature.
2. **Audit the street imagery.** Use the [Mapillary API coverage layer and imagery](https://github.com/mapillary/api-demo) to sample, say, 40–80 recent street-facing views from the pilot. A vision model marks *visible* exterior shutters/awnings, shade, trees, roof exposure where visible, and visible cooling equipment. A human reviews a stratified sample and records false positives/negatives. Link every displayed observation back to its image and capture date, with Mapillary attribution.
3. **Keep the inference honest.** A window with no visible AC unit is **not** evidence that the dwelling lacks cooling: Parisian systems can be internal, roof-mounted, courtyard-facing, or simply invisible. A street image does not reveal apartment-level vulnerability, indoor temperature, insulation, occupant age, or AC operability. Use imagery to estimate visible façade protection and street shade, plus a confidence/coverage score. Where available, use [DPE cooling-equipment fields](https://www.data.gouv.fr/dataservices/api-dpe-logements) only as a partial cross-check; DPE records are not a representative census of all occupied homes.
4. **Rank areas, not households.** For each 200 m cell, combine heat exposure, population vulnerability, likely building overheating, and lack of nearby accessible cooling into a transparent score. Report component values separately, alongside imagery coverage. Use a 200 m cell or coarser output for public display; do not turn the score into a named-building door-knocking list. Official outreach can use its own opt-in vulnerable-person register, which [Paris already operates](https://handicap.paris.fr/inscription-sur-le-registre-parisien-de-vigilance-pour-les-personnes-vulnerables/).
5. **Recommend actions with real constraints.** The [Paris guidance on shutters, awnings, films, and AC](https://www.paris.fr/pages/volets-stores-climatiseurs-quelles-sont-les-regles-a-respecter-avant-toute-installation-35881) distinguishes interior measures from exterior changes, which may need planning and condominium approval. Its bioclimatic planning rules favor appropriately integrated solutions and do not allow a street-facing exterior AC unit as a blanket fix. Make each action a *feasibility candidate*, with a permit/heritage/condominium check, not an automatically approved project.

### Example action menu

| Action | Timescale | Demo effect | Constraint to display |
| --- | --- | --- | --- |
| Open or extend an existing cooling place; arrange outreach and transport | Days | Improves access for a priority grid cell | Opening hours, capacity, accessibility and staffing must be confirmed |
| Interior solar film, blinds, or fan support | Days–weeks | Reduces modeled indoor heat exposure for a targeted building group | Tenant/owner access and suitability; no assumed measured temperature drop |
| Exterior shutters or awnings | Months | Reduces solar gain on exposed façades | Façade, heritage, planning and condominium review |
| Roof treatment, insulation, or broader renovation | Months–years | Improves top-floor overheating scenario | Engineering, moisture, heritage and owner approval |
| Street trees/shade | Years | Improves outdoor exposure and shaded access routes | Planting space, utilities, water, maintenance |

Prices and effect sizes in the demo are **editable scenario assumptions** until local quotes and validated building simulation are available. Do not present the output as a predicted number of deaths prevented.

## The ambitious 24-hour challenge

**Minimum complete demo:** one pilot area, real published data, 40–80 dated Mapillary views if accessible, one reviewed visual label (for example, exterior shutters) plus street shade, a transparent 200 m priority map, three action types, and a fictional **€250,000 pilot budget**. The planner chooses a portfolio and sees a before/after exposure score plus a list of feasibility checks. A low-coverage cell stays explicitly uncertain.

**Stretch goal:** optimize the portfolio under the budget while comparing two objectives: reduce the most total modeled heat exposure, or reduce exposure in the most vulnerable cells. Show why the choices differ. A stronger technical stretch is to estimate shade and façade orientation from imagery, then cross-check the result against BDNB's summer-overheating indicator. Treat that indicator as a comparison, not independent ground truth, because it already models building and urban heat factors.

The core objective can be written simply: maximize the sum of **vulnerability-weighted exposure reduction** across the pilot grid cells, subject to budget, implementation time, and mutually exclusive or dependent actions. Show an uncomplicated baseline such as “fund the hottest cells first.” No complex optimizer is needed for five to ten candidate projects; enumerating valid combinations is enough.

## Three-minute demo

1. **0:00–0:40 — Start with the heat map.** Pan over the pilot cells. Click a hot cell to reveal its published heat score, age/income indicators, building records, nearby cooling places, and source dates.
2. **0:40–1:15 — Reveal the street evidence.** Open two Mapillary views: one exposed frontage and one shaded frontage. Show model labels, reviewer corrections, image dates, and the fraction of the cell actually observed. Make a missing-image cell gray rather than pretending it has no shutters or AC.
3. **1:15–2:15 — Allocate the budget.** Select a heat-wave scenario and €250,000. Press **Plan**. The tool chooses a cooling-place/outreach action plus a few building measures, explains why, and flags exterior work requiring approval. Toggle between total exposure and equity-weighted objectives.
4. **2:15–3:00 — Replay the same scenario.** Compare before/after modeled exposure and walking access to cooling. Increase the severity or lower the budget: the plan leaves a visible residual gap. End on a compact “observed / modeled / assumed” legend.

## First-hour gates and 24-hour build

**Hour 0–1: coverage and data gate.** Use Mapillary's [coverage demo](https://mapillary.github.io/api-demo/) or a registered API token to inspect the candidate pilot at street zoom, filter for recent imagery, open actual façades, and tally usable frontages. Registering an app/access token is required for Mapillary platform data. At research time, a direct token-free coverage-tile request returned HTTP 403, so **pilot coverage has not been verified here**. If there are too few usable views, relocate the pilot or drop the photo model and retain the decision planner.

**Hours 1–6:** select cells and download small spatial extracts; define the scoring formula and action assumptions. **Hours 6–12:** sample and label images; build the map and evidence cards. **Hours 12–18:** implement the action rules, portfolio selection, and scenario replay. **Hours 18–24:** audit model labels, check joins and permissions copy, rehearse the three-minute click path, and prepare a static fallback if an external API fails.

For five people: one geodata lead, one imagery/validation lead, one scenario/optimization lead, one front-end/map lead, and one integration/pitch lead. A simple web map (MapLibre or Leaflet), a Python preprocessing script, and static GeoJSON are sufficient. 3D can be a visual stretch, not a dependency.

## What the prototype can claim

It can show a **reproducible, source-linked ranking of small areas and a constrained menu of possible actions**. It cannot infer which specific apartment lacks AC, issue official outreach orders, certify building-code compliance, or predict clinical outcomes. Its useful innovation is closing the loop from heat-vulnerability data to a reviewable, budgeted intervention plan.
