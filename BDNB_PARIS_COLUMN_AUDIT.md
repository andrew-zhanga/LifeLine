# BDNB Paris column audit

Checked the live `batiment_groupe_complet` API on 23 October 2026. The audit contains 150 distinct building-group records from Paris arrondissements 1, 11, 16, and 20. For each arrondissement, records were ordered by `batiment_groupe_id` and fetched in 10-row windows at offsets 0, 500, 1000, and 1500; the 1st arrondissement had no records at offset 1500. This is a deliberately spread pilot sample, **not a random or representative Paris sample**. Percentages below describe only these records. The complete field-by-field counts are in `bdnb_paris_sample_audit.json`.

Source: https://api.bdnb.io/v1/bdnb/donnees/batiment_groupe_complet

## Good first-pass columns

| Column(s) | Present | Use |
| --- | ---: | --- |
| `batiment_groupe_id` | 150/150 | Stable key for the building-group row. |
| `geom_groupe`, `surface_emprise_sol` | 150/150 | Map footprint and ground area. Geometry reports EPSG:2154 and must be transformed for most web maps. |
| `code_iris`, `code_commune_insee` | 150/150 | Join neighborhood context; do not imply IRIS values are measured per building. |
| `usage_principal_bdnb_open` | 148/150 | Restrict or label residential buildings. The sample has 125 residential, 23 tertiary, 2 missing. |
| `nb_log` | 148/150 | Number of dwellings; a scale indicator, not an occupancy or elderly count. |
| `hauteur_mean`, `nb_niveau` | 145/150, 148/150 | Building form and height. |
| `annee_construction` | 141/150 | Age/cohort; useful context, not direct evidence of insulation or overheating. |
| `fiabilite_emprise_sol`, `fiabilite_hauteur` | 148/150, 144/150 | Quality flags worth retaining. |

## Useful but incomplete construction and envelope columns

| Column(s) | Present | Finding |
| --- | ---: | --- |
| `mat_mur_txt` | 148/150 | Wall material. 43 records say `INDETERMINE`, leaving 105/150 with a named material. |
| `mat_toit_txt` | 148/150 | Roof material. 44 say `INDETERMINE`, leaving 104/150 with a named material. |
| `classe_inertie` | 117/150 | Thermal inertia class, with meaningful categories such as `Légère` and `Lourde`. |
| `type_isolation_mur_exterieur` | 118/150 | External-wall insulation; 9 of the 118 say `inconnu`. |
| `type_isolation_plancher_haut` | 113/150 | Upper-floor/roof-adjacent insulation; 17 say `inconnu`. |
| `type_vitrage`, `uw` | 118/150, 115/150 | Glazing and window thermal performance. |
| `facteur_solaire_baie_vitree`, `pourcentage_surface_baie_vitree_exterieur` | 115/150 each | Solar gain and glazed facade proportion. |
| `type_fermeture` | 115/150 | Window closure/shading type. 62 of 150 explicitly say absence of closure; this is a DPE-derived feature, not direct observation of every facade. |
| `traversant`, `l_orientation_baie_vitree`, `type_ventilation` | 115/150, 115/150, 116/150 | Cross-ventilation, window orientation, ventilation. These are especially relevant to summer heat. |
| `u_mur_exterieur` | 115/150 | Wall thermal transmittance; keep as a supplementary envelope feature. |

## Defer or treat carefully

| Column | Present | Reason |
| --- | ---: | --- |
| `u_plancher_haut_deperditif` | 54/150 | Too sparse for a required first-pass score; retain as optional evidence. |
| `type_generateur_climatisation` | 4/150 | A non-null value provides some evidence of cooling equipment; null **does not mean no AC**. |
| `classe_bilan_dpe` | 116/150 | Overall energy rating is not a summer-overheating rating. Keep for context, not as the heat target. |
| `mat_mur_txt`, `mat_toit_txt` when `INDETERMINE` | 43/150, 44/150 | Treat the value as missing, not as a material category. |

Recommended first table: one row per `batiment_groupe_id`, containing the first two groups of columns plus source/quality flags and nulls. Add derived heat features only in a separate processing step so the raw evidence remains inspectable. Do not fill missing envelope or cooling values with “uninsulated” or “no AC.”
