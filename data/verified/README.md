# FlareWise retrieved data bundle

This directory contains downloaded source files and prepared map inputs, not mocked observations. The selected case study uses **2023 flare volumes and weather**, with **2019–2023 ACS five-year population estimates**. The source workbook also contains other years through 2024.

## Verified result

All required downloads and preparation checks passed for the selected historical screening demo.

| Data | Retrieved and validated |
|---|---|
| 2023 flare inventory | 8,783 positive-volume global sites; 392 study-area candidates plus 30 buffer sources |
| 2023 weather | 9 locations × 8,760 hourly records, at both 10 m and 100 m; no missing values |
| Population and age | 763 of 763 tract joins; 157 named Census communities |
| Modeled population grid | 7,543 area-weighted cells; total population and both age groups conserved by tract |
| Pipelines | 1,385 features, matching the server's count; no truncation |
| Gas benchmark | 249 available daily 2023 prices; mean $2.5336/MMBtu |

The initial centroid representation missed 20 sources within the 30 km test radius. With the area-weighted grid, all 422 sources have a receptor within 3.39 km. This fixes a sampling gap, not uncertainty about where residents actually live.

A smoke test across 365 daily weather samples kept the same 20 capture sites fixed. Exposure changed with weather and never increased after reducing those sources. The 17.41% aggregate reduction in that test is a **test-fixture result**, not a validated estimate or an optimized portfolio recommendation.

## Reproduce

From the project root:

```sh
python3 -m venv .data-venv
.data-venv/bin/pip install -r scripts/data-requirements.txt
python3 scripts/retrieve_data.py
.data-venv/bin/python scripts/prepare_data.py
```

The downloader caches raw files, records source URLs, verification timestamps, sizes and SHA-256 checksums in `download_manifest.json`. It falls back to curl for public files that reject the Python HTTP client. No API keys were needed. Raw files (approximately 220 MB, mainly the nationwide Census table) and the Python environment are ignored by Git. Prepared files are small enough to use as static assets; they have not yet been wired into the dummy website.

`processed/validation_report.json` is the machine-readable result of the checks. `build_contract.json` records scope and assumptions still needed for implementation. `fallback_2020/` contains an earlier fallback, not the chosen case study.

## Inputs and meaning

| Input | Source | Meaning and intended use |
|---|---|---|
| Global and regional flares | [World Bank annual inventory](https://www.worldbank.org/en/programs/gasflaringreduction/global-flaring-data) | Satellite-estimated annual gas volumes and source locations. Actual workbook downloaded. **VIIRS-derived**, not an independent Sentinel-3 source. Use 2023 records with positive volume. |
| Weather | [ERA5 through Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api) | Nine sampled locations, every UTC hour in 2023, wind speed and direction at both 10 m and 100 m. Coarse reanalysis, not measurements at each flare. |
| Population and age | [Census ACS B01001 summary file](https://www2.census.gov/programs-surveys/acs/summary_file/2023/table-based-SF/data/5YRData/) | Total residents, under-five residents and residents aged 65+, matched to Census tract identifiers. Includes sampling uncertainty; five-year estimates are not daily population observations. |
| Boundaries and communities | [2023 Census cartographic boundaries](https://www2.census.gov/geo/tiger/GENZ2023/shp/) | Texas tract polygons and place polygons. NAD83 explicitly transformed to WGS84. Whole intersecting tracts retained, to avoid assigning full populations to clipped slivers. |
| Pipelines | [EIA pipeline layer hosted by DOE NETL](https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer/3) | Real geometry for contextual display. Not proof of capacity, availability, legal access or connection cost. The service's vintage is not established as 2023. |
| Gas price | [EIA Henry Hub spot prices via FRED](https://fred.stlouisfed.org/series/DHHNGSP) | Actual 2023 benchmark prices in USD/MMBtu. Trading-day observations; do not count missing days as zero. Benchmark is not the net price available at an individual flare. |

Retain provider attribution in the built app. FRED identifies the underlying EIA series as public domain with citation requested. This retrieval pass is not a blanket license grant for every provider's branding, imagery or map tiles.

## Prepared files

- `flares_global_2023.geojson`: global positive-volume points for the globe.
- `flares_regional_2023.geojson`: study-area and buffer sources; `eligible_for_capture` distinguishes project candidates from buffer sources.
- `population_tracts.geojson`: actual polygons, age counts, shares, total-population margin of error and density per land area.
- `population_grid.geojson`: 5 km cells intersected with tract polygons, with population and age groups allocated in proportion to area. Totals are conserved separately within each tract. This is a modeled distribution, not a measured 5 km population dataset.
- `population_receptors.geojson`: representative points inside those cells for integration.
- `population_tract_points.geojson`: original one-point-per-tract representation, retained for comparison; not the integration default.
- `communities.geojson`: Census place labels with population/age context. Place totals overlap tract totals; **never add both layers' populations together**.
- `weather_2023.json`: nine complete time series, UTC, explicit units, actual returned grid coordinates.
- `pipelines.geojson`: downloaded pipeline features cropped to the buffered study extent.
- `gas_price_2023.json`: benchmark history and mean across available daily observations.
- `integration_smoke_test.json`: a fixed-source capture experiment sampled across the year; verification artifact, not a final optimized investment plan.
- `validation_report.json`: counts, units, joins, coverage, and integration checks.

## Behavior and data rules for the implementation

1. **Volume:** use `Flaring Vol (million m3)` as the canonical workbook column; multiply by one million for annual m³. The workbook's `bcm` column has rounded values in some rows. Preserve raw values and audit the cross-check against `MMscfd`. Annual estimates must not be advertised as hourly measured flaring.
2. **Wind:** direction is where the wind comes **from**. Transport east = `-speed * sin(direction)` and north = `-speed * cos(direction)`, with angles converted to radians. Interpolate vectors, not raw angles across 359°/0°. Use UTC internally and explicit timezone conversion for display.
3. **Weather mesh:** nine samples are a deliberately coarse regional mesh. Keep actual returned grid coordinates. Nearest-cell assignment is sufficient for a first screening model; do not describe it as street-level wind.
4. **Demographics:** under five = B01001 male-under-five + female-under-five. Age 65+ sums six male and six female bins. Treat age shares within a tract as an allocation assumption if generating finer grids. A polygon's full population is not an exact count of residents inside a small plume intersection.
5. **Geometry:** the study area is a bounding box, not an official Eagle Ford geological boundary. Buffer sources contribute background but cannot be selected. Full intersecting-tract totals include residents outside the box. Label totals accordingly.
6. **Portfolio:** changing time must not move installations. Rank projects using aggregated weather and population; show the same sources, weather and population before/after capture. Changing budget or objectives can change the selected sites.
7. **Economics:** installation costs, treatment/compression costs, capture fraction, gas heating value, project life and discount rate remain explicit scenario inputs. They are not site measurements. Pipeline distance is at most a screening proxy, never a quote.
8. **Output:** use a relative exposure index. There is no downloaded pollutant concentration, personal exposure or health-outcome dataset behind this bundle.

## Scope of the smoke test

The test checks real file joins, changing wind, fixed selected sites, positive population weights and monotonic reductions when source strength is reduced. It uses a simple directional decaying kernel, a 30 km cutoff and an explicit calm-wind fallback. It is not validation of a physical dispersion model. The initial one-point-per-tract method left 20 regional sources more than 30 km from a receptor because rural tracts can be very large. The prepared 5 km area-weighted grid addresses this sampling problem while preserving tract totals. It still assumes uniform population within each tract; it does not locate individual homes. Sensitivity to population allocation remains a modeling question, not a download-access blocker.

## Access issues resolved and remaining

- World Bank files initially returned HTTP 403 through Python's default client. The 2012–2024 workbook downloaded successfully with curl and parsed as an actual Excel workbook.
- Census data API access was not needed: the public summary table and shapefiles downloaded directly and were joined locally.
- Sentinel-3 CDS observation download and RRC lease-to-flare joins are **not established** and are **not dependencies of this bundle**. If a strictly VIIRS-free project becomes mandatory, that is a separate unresolved requirement.
- No dataset provides per-site capture installation quotes or guaranteed pipeline access here. Use transparent scenario assumptions.
- Analytical data is cached locally. The existing website still fetches external basemap tiles and fonts, so whole-app offline readiness has not been established.
