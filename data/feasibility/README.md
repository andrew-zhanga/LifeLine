# Data feasibility probes

Research date: 2026-10-23. These are retrieval probes, not production datasets.

- `weather_sample.json`: Open-Meteo archive, ERA5, latitude 28.5 / longitude -99.0, 2023-07-01 through 2023-07-02, hourly 10 m wind direction/speed, m/s and GMT. Retrieved successfully; 48 non-null records. Endpoint: https://archive-api.open-meteo.com/v1/archive
- `cds_metadata.json`: public request schema, not flare observations. Retrieved from https://cds.climate.copernicus.eu/api/retrieve/v1/processes/satellite-fire-radiative-power
- Census 2023 ACS5 tract query for state 48 / county 283 returned HTML Missing Key; no Census observations saved. Official summary-file index is available, but attempted guessed legacy subpaths returned 404; follow the official directory listing rather than reuse those paths.
- World Bank workbook could not be retrieved in this environment; no workbook saved.

See `../../FLAREWISE_DATA_FEASIBILITY_AUDIT.md` for scope, sources and unresolved gates.
