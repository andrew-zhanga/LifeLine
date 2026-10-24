# Judge Q&A

**Does capture equipment move with the wind?** No. We select fixed sites using annual mean population-weighted contribution over 8,760 actual hours. Replay changes weather, not selected installations.

**How current is the data?** The scenario uses 2023 flare volumes and ERA5 winds, plus ACS 2019–2023 five-year population estimates. Pipeline geometry vintage is not established as 2023. Nothing is labeled live.

**Are these measured gas volumes?** They are published VIIRS-derived satellite estimates from the World Bank. Annual activity is spread uniformly across the year for screening; hourly flare operation is not observed.

**Where do costs come from?** Explicit scenario coefficients for equipment, capacity and distance to the nearest downloaded pipeline. These are not engineering quotes. Nearest geometry does not establish capacity, access, rights or a feasible connection.

**Is the population map precise?** Tract population and ages are allocated by intersected area to approximately 5 km cells. Totals are conserved, but individual households are not located. Place and tract populations overlap and are never added together.

**Does this measure avoided illness?** No. The output is a relative wind-driven index weighted by population, not pollutant concentration, personal exposure, AQI or a causal health outcome.

**Did you train an AI model?** No. The core is deterministic sparse transport screening and integer portfolio optimization. There are no training images, masks or independent pollutant measurements in the delivered bundle.

**What does Balanced mean?** It maximizes modeled exposure benefit while retaining at least 95% of the positive Financial NPV reference, at the same budget and price. It is unavailable if that positive reference does not exist. Solver status and gaps are retained.

**How robust is this?** The evidence pack varies declared capex, capture fraction and decline assumptions and recomputes portfolios. These are sensitivity scenarios, not confidence intervals.

**What works without internet?** All analytical assets are local. The map can show local study and tract geography without external basemap tiles. A cold visit still needs the local server; this is not a service-worker-installed offline app.
