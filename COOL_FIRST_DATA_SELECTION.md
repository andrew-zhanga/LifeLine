# Cool First: data to choose for the first building heat map

## Scoring unit and meaning

Use the **BDNB building-group ID and footprint** as the row key for the first pilot. The color means *relative susceptibility to overheating under a common heat-wave scenario*. It is not measured indoor temperature, individual death risk, or proof that the building lacks AC. Census variables remain in a later 200 m **community-priority** layer.

## Recommended inputs, in build order

| Priority | Feature to calculate | Source | Native scale | Why it belongs / limitation |
| --- | --- | --- | --- | --- |
| **Must** | Building ID, footprint, residential use, height or number of floors, roof/floor geometry | [BDNB open](https://www.data.gouv.fr/datasets/base-de-donnees-nationale-des-batiments); underlying [IGN BD TOPO building fields](https://geoservices.ign.fr/sites/default/files/2021-07/DC_BDTOPO_3-0.pdf) | Building group / construction | Makes each polygon renderable and joinable; roof exposure and height matter. Verify actual Paris extract columns and null rates. Use the same geometry for scoring and 3D extrusion when possible. |
| **Must** | Local nighttime urban-heat intensity, shared by buildings in the same source cell | [CSTB urban-heat indicators](https://www.data.gouv.fr/datasets/cartographie-nationale-des-indicateurs-lies-a-lilot-de-chaleur-urbain) (choose the *UHI* layer, not the already-combined HVI); [Météo-France 250 m Paris map](https://meteofrance.com/sites/meteofrance.com/files/files/editorial/ICU_MApUCE_v2025-2_Paris.pdf) for visual context | Published GIS cell/area; Météo map 250 m | Establishes that a building sits in a hotter part of the city. Inspect actual downloadable GIS geometry first; a PDF map cannot be used as numeric building input. Shared cell values must be labeled as area estimates. |
| **Must, if pilot coverage passes** | Visible exterior shutters/awnings and observable-window count | [Mapillary API and coverage viewer](https://github.com/mapillary/api-demo) + team's vision model + human review | Observed façade/image | Produces the team's new auditable dataset. `yes/no/unknown` per seen façade; no label for unseen sides, and no inferred AC absence. Date, direction, occlusion and image-to-building match confidence are mandatory fields. |
| **High value** | Construction period, roof/mural insulation, glazing and envelope quality **where observed** | [BDNB envelope synthesis schema](https://bdnb.io/schema/latest/bdnb_v07/tables/batiment_groupe_synthese_enveloppe.html) and construction records | Building group or DPE-derived record | More directly relevant to heat flow than age alone. May be missing or based on partial DPE; retain BDNB reliability/source fields and show unknowns. A poor DPE energy letter is not itself a summer-heat label. |
| **High value** | South/west façade exposure, roof area, nearby building shadow | Footprint/height geometry from BDNB or BD TOPO; [BDNB geometry method](https://www.bdnb.io/documentation/predictions_dpe/) explains its own wall azimuth and solar-mask approach | Building/facade | Distinguishes buildings in the same heat cell. Begin with simple roof/footprint and orientation; full solar simulation is optional. Avoid using a BDNB expert solar-mask field unless it is actually accessible. |
| **Useful if easy** | Nearby street trees or tree-canopy proxy | [Paris tree points](https://opendata.paris.fr/explore/dataset/les-arbres/) | Tree point | Outdoor/near-façade shade context. City data omit some private trees and are not a precise shadow model; avoid counting trees as guaranteed indoor cooling. |
| **Optional evidence** | Recorded cooling equipment in available DPEs | [ADEME DPE records](https://www.data.gouv.fr/dataservices/api-dpe-logements) | Diagnosed dwelling / building | Show a documented presence where matched; an absent or unmatched record cannot establish no AC for a whole building. Do not make this the core image label. |
| **Benchmark only** | Existing modeled summer overheating (`ISB-DH`) | [BDNB expert indicator](https://www.bdnb.io/documentation/predictions_isb_dh/) | Building group / estimated dwelling conditions | A useful reference if access is available. It already combines climate, envelope, top-floor and urban form, and excludes AC/fans. Do not use it both as an input and as independent validation. |

## Separate, later health-action inputs

| Data | Source | Proper use |
| --- | --- | --- |
| Older residents, one-person households, income and population | [Insee 200 m grid](https://www.insee.fr/fr/statistiques/8735162) | Score **areas** for outreach; do not impute individual building residents from floor area. Small-cell values may be imputed. |
| Libraries, public cooling facilities, parks and opening times | [Paris cool facilities](https://opendata.paris.fr/explore/dataset/ilots-de-fraicheur-equipements-activites/) and [cool parks](https://opendata.paris.fr/explore/dataset/ilots-de-fraicheur-espaces-verts-frais/) | Identify service-access gaps for the response layer, not physical overheating of a building. Verify actual opening, capacity and accessibility in the chosen scenario. |
| Heat-wave weather scenario | Météo-France observations/forecast or a clearly labeled fixed scenario | Change the scenario shown to the judge. A coarse weather forecast is shared across the pilot; it does not supply building-by-building indoor temperature. |
| Building/planning rules | [Paris guidance](https://www.paris.fr/pages/volets-stores-climatiseurs-quelles-sont-les-regles-a-respecter-avant-toute-installation-35881) | Filter **future interventions** such as exterior shutters, not the first heat score. |

## Recommended first choice

Start with **five feature families**: (1) residential building polygon/height/roof, (2) local urban heat, (3) observed exterior solar protection, (4) any trustworthy envelope/age fields actually populated for the pilot, and (5) simple orientation/neighbor-shadow geometry. Display each as a separate score component and mark missingness. Keep demographic exposure and cooling access for the second layer.

Before scoring, inspect **20–30 pilot rows** and report coverage for each field. Reject any field that is mostly missing, mismatched to buildings, or only weakly related to summer overheating. The Mapillary pilot location should be chosen from a count of recent, usable **residential façades**; a preliminary visual check found older coverage around Belleville and some recent examples near République, but no systematic residential coverage count yet.
