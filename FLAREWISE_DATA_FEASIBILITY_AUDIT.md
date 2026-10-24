# FlareWise — alternative data and feasibility audit

> **Updated retrieval status:** See [the verified data bundle](data/verified/README.md) and its validation report. The World Bank 2012–2024 workbook, 2023 ERA5 winds, ACS population/age table, Census geometry, pipeline geometry and gas-price history have now been downloaded. The selected case study uses 2023. Earlier access failures below describe the initial investigation; they are not the current readiness status. The selected World Bank route remains VIIRS-derived; Sentinel-3 and RRC joins are not established.

Research date: 2026-10-23. Read together with `FLAREWISE_EXECUTABLE_PLAN.md`.

## Decision

**Sentinel-3 SLSTR / Copernicus C3S dedicated gas-flare data is the strongest independent satellite replacement found for the raw VIIRS Nightfire feed.** It is not a complete replacement for all inputs: its radiative power needs a separate, defensible gas-volume source for economics.

Distinguish two requirements:

1. **Avoid EOG daily-feed access:** World Bank annual site-volume inventory is a practical candidate for the globe and economics. It is still VIIRS-derived, so it does not meet sensor independence.
2. **Avoid VIIRS entirely:** use Sentinel-3 flare detections plus verified Texas RRC flared-gas reports and a defensible report-to-source match. This is a conditional build path; the regional match and export schema have not been demonstrated yet.

Do not claim the whole pipeline is verified. Weather retrieval and CDS metadata succeeded; flare observations, volume joins and complete population geometry are still acceptance gates.

## Candidate datasets and what they support

### Sentinel-3 SLSTR: recommended independent detection source

[Copernicus dataset and download](https://cds.climate.copernicus.eu/datasets/satellite-fire-radiative-power?tab=overview), DOI 10.24381/cds.95afd6ae.

Select **v1.2, table summary, monthly, gas flares, Sentinel-3A and/or 3B**. The monthly CSV packages contain individual observation timestamps. Gas-flare coverage starts March 2022 according to the catalog; do not assume the general product's 2020 start applies. The gridded products are too coarse to represent individual project sites. This supplies observed hotspots and radiative power, not metered gas volume or hourly operation.

The [algorithm documentation](https://confluence.ecmwf.int/spaces/CKB/pages/621021768/Active+Fire+Fire+Radiative+Power+AF+FRP+Gas+Flare+Products+V1.2+Algorithm+Theoretical+Basis+Document+ATBD) distinguishes the dedicated SWIR flare product from general fire labels based on known geographic zones. The dedicated product uses spectral discrimination and persistence filtering, including detections across three consecutive 27-day cycles. Consequently, it favors persistent sources and can miss transient/new flares. Its SWIR detection resolution is 500 m at nadir; the catalog's generic summary description says 1 km. Inspect actual fields and geolocation uncertainty before selecting clustering distances. Neither number means a precisely located stack.

Verification: retrieved the actual public CDS process schema; it exposes `table_summary`, `gas_flares`, `sentinel_3a`, `sentinel_3b`, and `1_2`. Saved as `data/feasibility/cds_metadata.json`. This proves the request options exist, not that an observation file was downloaded. CDS download access/account, license conditions, requested month availability and Eagle Ford coverage remain unverified. Consult both catalog terms and the product guide's specific attribution/promotion wording before public redistribution; no license acceptance was performed during this review.

### Texas RRC Form PR: independent reported volume, conditional

[Official datasets](https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/) and [Form PR instructions](https://www.rrc.state.tx.us/media/mxcpw5vn/form-pr-instructions-01-25-2022.pdf).

The reporting instructions separate gas disposition **10 = flared** and **11 = vented**. Volume is MCF at specified base conditions. This is operator-reported lease-level monthly gas, not satellite measurement and not stack coordinates. The pending-lease dataset explicitly added separate fields in 2021, but covers pending leases, not all leases. An older or compatibility export may combine vented/flared quantities. Inspect the exact export and an actual report before interpreting a field.

Required join: reporting identifier + district + oil/gas schedule + month/revision → lease/well reference → surface location → satellite source cluster. Preserve all candidate matches and match quality. RRC describes some downloadable GIS coordinates as NAD27; transform the declared CRS to WGS84. Do not merely relabel coordinates. A well surface location is not necessarily its flare stack; a bottom-hole location is unsuitable.

A many-well lease cannot have its full volume copied to every hotspot. For MVP, select only unambiguous matches or treat the whole lease as one project with explicit spatial uncertainty. Unsupported allocation excludes a source from financial ranking. A nearby well alone does not establish operator ownership.

### World Bank annual site inventory: best alternate distribution route, still VIIRS-derived

[Official inventory page](https://www.worldbank.org/en/programs/gasflaringreduction/global-flaring-data) lists annual individual-site volume workbooks through 2025, as well as the 2012–2024 release. This can support a dated global map and annual economics without rebuilding the daily Nightfire pipeline. It cannot supply observed hourly activity or nightly persistence.

Direct workbook access attempts did not return a usable file in this session; website requests encountered 403 errors/tool retrieval errors. Availability is verified at catalog level only. Do not claim a local working inventory. The ORNL 2012–2019 inventory is also VIIRS-derived and is not an independent-sensor backup.

### Other alternatives assessed

- [DAFI v2 research](https://re.public.polimi.it/retrieve/768f5d68-b1a8-4272-9851-1cbcf456970b/Faruolo_2024_Environ._Res._Lett._19_114053.pdf): Landsat/Sentinel-2 daytime source catalog; useful for location cross-checks, but a ready bulk inventory and local coverage have not been verified here. Not a default volume source.
- [FlareSat](https://zenodo.org/records/17619196): labeled Landsat imagery for segmentation research. It is a 2019 image benchmark, not a gas-volume/time-series feed; sampling references Nightfire. Reserve for later imagery work.
- [2017 SLSTR flaring/black-carbon inventory](https://essd.copernicus.org/articles/12/2137/2020/): independent sensor measurements with modeled volumes/black carbon. Old, gridded, and uses calibration/observation corrections; not a current, stack-level financial dataset. Download and methodological independence of calibration have not been audited.
- [EPA GHGRP](https://www.epa.gov/ghgreporting/ghgrp-and-oil-and-gas-industry): reporting can aggregate an operator's onshore wells within a basin. Do not attach that total to the map coordinate as a single flare. Potential aggregate check, not a direct Eagle Ford point-source replacement.

## Recommended complete data chain

**Sentinel-3 source candidates → independently verified gas volume where available → hourly historical weather → residential population and age context → relative exposure → screening capture scenarios.**

Keep `detection_source`, `volume_source`, `source_strength_basis`, `location_accuracy`, `match_status`, `activity_basis`, and `eligible_for_economics` separate in the schema.

Two honest operating modes:

- **Volume-backed:** q is inferred gas rate from a matched annual/monthly volume, used consistently in exposure and economics. Satellite power is corroborating activity evidence, not added to volume as another emission source.
- **Detection-only:** source remains on the map; optionally show a separate thermal-activity screening index with explicit FRP assumptions. No inferred dollars, NPV or capture portfolio ranking without a supported volume/cost scenario. Never mix volume-weighted and MW-weighted sources in one unlabeled exposure index.

The global map may show source inventory coverage while the regional model contains only supported sources. It must disclose modeled-source coverage. Unknown sources do not equal clean air.

## Concrete access tests

- **Weather: PASS for one sample.** Downloaded 48 hours at 28.5 N, 99 W, July 1–2 2023, explicit ERA5 model, 10 m wind direction and speed in m/s, GMT. Saved `data/feasibility/weather_sample.json`. One coordinate is a retrieval check, not a spatial validation or full regional weather grid.
- **Sentinel-3: metadata PASS; observations NOT TESTED.** Public process schema retrieved, no authenticated data request completed.
- **Census API: failed unauthenticated.** HTTP 200 returned an HTML “Missing Key” page rather than observations. Official [ACS API documentation](https://www.census.gov/data/developers/data-sets/acs-5year.html) now states that data queries require a key. Use an authorized key or official [table-based Summary Files](https://www.census.gov/programs-surveys/acs/data/summary-file.html). Check content type and parse schema, not HTTP status alone.
- **World Bank: catalog PASS; workbook NOT RETRIEVED.** Do not base the build schedule on an untested download.
- **RRC: documentation PASS; raw report sample/join NOT TESTED.** Export access, revision rules and flare-only coverage remain blockers for an entirely VIIRS-free financial model.

## Holes closed by changing the design

| Failure mode | Required change / release gate |
|---|---|
| Radiative MW converted directly into annual sellable gas | Separate volume source or validated calibration. Until then financial metrics unavailable. Do not borrow a VIIRS calibration coefficient for SLSTR. |
| Assumed hourly flaring presented as observation | Label “historical wind scenario under inferred source activity.” Test constant versus monthly activity; do not claim observed real-time smoke. |
| A narrow moving footprint presented as accurate exposure | Keep relative screening units. Weather height, stack/plume rise and spatial resolution mismatch remain scientific limitations. Validate ranking against alternate wind heights/resolutions before strong local claims. |
| Immediate footprint reaches distant towns when wind changes | Declare quasi-steady hourly model. No arrival-time prediction. A future puff model is needed for transient transport. |
| Volume-to-pollution equivalence | Disclose the common source-factor assumption; combustion composition/efficiency varies. Test site-specific factor perturbations. No pollutant-specific dose or health outcome claims. |
| Site lies within a cell but centroid is upwind or exactly at source | Area-sample each source-containing receptor cell; do not omit local residents because x=0. Test translation sensitivity with finer subcells. |
| Missing sources outside boundary | Buffer sources and receptors. Sources in the buffer contribute fixed background index but are not eligible projects; report unobserved sources separately. Compare model radius 10/20/30 km. |
| Different observation dates/years across inputs | Freeze a complete common year after data inspection. Five-year ACS estimates are a reference-period estimate, not a single-year census; disclose reference windows. |
| Annual inventory extrapolated into future guaranteed income | Cap capture fraction; subtract gas treatment/transport/compression costs and losses; stress-test decline, netback and capex. Label NPV engineering-screening scenario, not bankable return. |
| Population scattered uniformly across empty land | Prefer populated-area allocation, normalized to tract totals; retain area-allocation fallback and compare its effect on rankings. Keep tract age shares labeled as modeled local allocation. |
| Tiny arbitrary tails define “affected residents” | Main objective remains continuous population-weighted index; any thresholded count is relative, baseline-fixed, and accompanied by threshold sensitivity. No claim it is a health limit. |
| Selected-source IDs duplicate a project's volume or cost | Define site versus project explicitly; match each volume record once, aggregate co-located observations, and prohibit conflicting/overlapping project selections. |
| Wrong map tells an overstated success story | Same source set, hour, weather and legend before/after; fixed background unchanged. Show actual frontier results, even if financial and exposure objectives align. |

## Hard go/no-go checklist before the real-data UI is called ready

1. Retrieve one actual monthly Sentinel-3 gas-flare file; inspect field names, units, timestamps, quality, duplicate observations, clear-look information and Eagle Ford counts. No valid-denominator persistence claim without observation opportunities.
2. Retrieve one actual flare-only volume record and its spatial reference; demonstrate the match. Then audit at least 20 matched candidates, reporting match coverage by both count and volume. If matches are insufficient, use the labeled World Bank annual route if VIIRS-derived inputs are acceptable, or ship exposure screening without financial optimization. Do not silently invent volumes.
3. Acquire regional population plus compatible geometry and validate totals/age fields and missing-value sentinels. API metadata alone does not satisfy this gate.
4. Freeze the full analysis year, regional polygon, weather grid, units and source/project IDs; persist checksums and retrieval timestamps.
5. Run a real subset through weather → exposure → population → before/after removal. Verify conservation, overlap counting, wind orientation, calm/missing handling and same legend scale.
6. Validate tiny optimizer fixtures against exhaustive enumeration, then report the actual real-data frontier and sensitivity. If rankings are unstable, expose that and avoid a confident recommendation.
7. Verify download/reuse terms, bundle only redistributable assets, test the demo without upstream API access, and rehearse on the actual laptop.

**Readiness judgment:** a feasible alternative exists, but the all-VIIRS-free capture-economics chain is not yet proven. This audit identifies its unresolved gates instead of declaring the approach hole-free. The frontend can be built against a stable schema now; scientific and financial claims must remain gated on these checks.
