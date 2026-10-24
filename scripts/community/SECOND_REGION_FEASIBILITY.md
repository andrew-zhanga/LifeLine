# One bounded second-region assessment: West Texas / Permian context

Assessed 2026-10-24. **Feasible as a subsequent data-preparation task; not implemented or validated in this build.** Keep its UI status inventory-only.

The existing verified 2023 global inventory contains **1,530 positive-volume sources totaling 5,276,158,597 m³/year** inside the exploratory box `[-104.5,30.5,-101.0,33.0]`. This is a convenient West Texas / southeastern New Mexico box, **not an official Permian basin polygon or a basin total**. Counts were computed directly from `data/verified/processed/flares_global_2023.geojson`; no new emissions or economics inferred.

Primary-source feasibility checks:

- [Census 2023 ACS B01001 variable definitions](https://api.census.gov/data/2023/acs/acs5/groups/B01001.html) supply sex-by-age estimates and uncertainty fields. The [2023 Census boundary archive](https://www2.census.gov/geo/tiger/GENZ2023/shp/) supplies tract/place boundaries. Rebuild tract selection and area-conserving cell allocation for this box; South Texas prepared cells cannot be reused spatially. The proposed box crosses Texas and New Mexico, so both state boundary files are needed.
- [Open-Meteo historical API documentation](https://open-meteo.com/en/docs/historical-weather-api) documents ERA5 historical coverage and 100 m wind speed/direction. Retrieve a new full-year regional weather mesh, preserving actual returned coordinates, UTC ordering and m/s conversion checks. Existing South Texas weather is not a validated proxy for West Texas.
- [DOE NETL's EIA pipeline layer metadata](https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer/3?f=pjson) identifies interstate/intrastate natural-gas lines, geometry query support and a 2,000-record limit. A new spatial query must verify total count/pagination. The current cropped South Texas lines cannot establish West Texas distances; provider metadata does not establish a historical 2023 geometry vintage or connection access/capacity.

Before publishing a second model: freeze source/receptor buffers, choose a suitable local projection (the box is west of the current UTM14 central study area), check all joins and population conservation, acquire weather and geometry, rerun exposure and portfolio checks, and review whether the same cost assumptions are useful. Henry Hub remains a benchmark, not a verified local netback. Distances remain screening proxies without rights/capacity data.

This assessment verified public documentation and counted already prepared inventory records. It did not download new weather/population/pipeline bundles, build a second exposure model, calculate second-region financial rankings, or verify project feasibility. It is intentionally excluded from `global-inventory.json` analysis-ready regions.
