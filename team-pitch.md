# Lifeline: an Oakland flood twin for dialysis access

## The pitch to the team

**What if a city could see a flood coming, watch which dialysis clinics lose the ability to treat people, and spend a limited resilience budget where it preserves the most treatment access?**

We build a cinematic 3D view of a real Oakland neighborhood. A water-level control changes the mapped flood scenario. Roads go underwater, clinic markers change from operating to at risk, and the dashboard shows estimated treatment capacity lost over a 12-, 24-, or 48-hour outage. Then we give the planner a hypothetical **$1 million resilience grant**. They can protect electrical equipment, add backup power, or prepare alternate-clinic transfers. An optimizer picks a portfolio within that budget and shows the same flood again, with the interventions visible in the scene and the estimated treatment gap reduced.

This fits the hackathon's **Resilient Systems** track: distributed energy, predictive disruption mapping, and keeping a community safe. The memorable angle is that a dialysis clinic can have power and still close if its water treatment, entrance, staff route, or patient route fails. [CMS says water interruption prevents dialysis treatments](https://www.cms.gov/Medicare/Provider-Enrollment-and-Certification/SurveyCertEmergPrep/Downloads/Guide-for-Chronic-Dialysis-Facilities-All-Hazards.pdf). [Federal rules do not universally require outpatient dialysis facilities to have emergency generators](https://www.cms.gov/medicare/provider-enrollment-and-certification/surveycertificationgeninfo/downloads/scletter09_56.pdf), though individual clinics may have them. That makes this an actual planning question, not a blanket claim that clinics lack backup power.

## Where and what is real

**Pilot: Oakland and nearby Alameda County clinics.** Oakland has mapped shoreline flood concerns, and its [Sea Level Rise Roadmap](https://www.oaklandca.gov/Community/Community-Development/Sustainability-Environment/Sea-Level-Rise-Roadmap) gives a local reason to start here. [CMS's dialysis facility listing](https://data.cms.gov/provider-data/dataset/23ew-n7w9) supplies real facility locations and station counts. The [BCDC Adapting to Rising Tides Explorer](https://explorer.adaptingtorisingtides.org/) supplies mapped Bay Area coastal water-level scenarios. We must run a GIS intersection before claiming that any named clinic is actually inundated; a downtown Oakland clinic can be a visible focus even if the modeled failure comes from a nearby road or utility dependency rather than water inside the building.

The flood control should use the **published mapped water levels** as discrete scenarios, such as 12, 24, and 36 inches above the map's tidal reference. A smooth water animation between them is for presentation; service outcomes are calculated at the actual mapped levels. A separate outage-duration control (12/24/48 hours) changes backup-power endurance and missed appointment estimates. We are **not forecasting when floodwater will arrive** or simulating rainfall runoff with a fluid solver.

## What the 3D simulation does

The city remains recognizable: terrain, streets, and 3D buildings provide context. A translucent water surface and animated currents reveal the flooded footprint. On each scenario change we evaluate:

1. **Building and entrance exposure:** whether mapped water reaches a facility footprint or its assumed entrance elevation.
2. **Electrical vulnerability:** whether a modeled switchboard, generator, or utility service is below a configurable flood threshold; whether any backup has enough kW and kWh/fuel for the critical load and outage duration.
3. **Water availability:** whether treated water is available; if it is not, dialysis capacity falls to zero unless an explicitly modeled, medically compatible backup supply exists.
4. **Access:** which roads become impassable under an assumed vehicle-depth threshold; whether staff, patients, and backup equipment can reach the clinic or an alternate clinic.
5. **Capacity:** estimated treatment slots available at each clinic and alternate site, given station count, operating shifts, and assumed staffing. CMS station counts are real; appointment demand and shift capacity in a hackathon demo are **assumptions**, visibly labeled.

Buildings do **not collapse**. That would need structural drawings, flow velocity, foundation conditions, and validated engineering models. The credible digital twin is a **functional failure simulator**: water rises around a realistic scene, electrical rooms glow red, a clinic darkens when it cannot operate, and routes break or reroute. This is visually dramatic and directly tied to a defensible decision model.

## The actual budget decision

Oakland's [adopted FY 2025–27 budget page](https://www.oaklandca.gov/Government/Finance-Budget/Budget/Fiscal-Year-2025-2027-Budget) shows that the city has a real budget, but its total is **not** money available to retrofit privately operated clinics. The **$1 million on screen is an illustrative joint city/health-system/grant pilot**, not a claimed Oakland allocation. Each project has a dollar cost, a site, a modeled effect, and constraints. The optimizer can choose only interventions that fit the pilot budget.

### Initial intervention price book

These are **planning benchmarks in source-year dollars**, not Oakland bids. The interface should show editable low/base/high costs. Site surveys, permits, interconnection, labor, and ownership agreements could change them substantially.

| Intervention | Demo cost rule | What it changes | Source and caveat |
| --- | ---: | --- | --- |
| Permanently installed diesel generator | **$650 per kW**; example 100 kW ≈ **$65k**, plus site-specific transfer-switch/fuel/permit allowance | Supplies critical power while fuel lasts, only if generator and electrical connection stay dry | [NREL/DOE REopt prefeasibility study](https://www.nrel.gov/docs/fy24osti/87988.pdf) uses $650/kW installed, $20/kW fixed O&M, and $3.61/gal fuel as its study assumptions. These are model inputs, not a local quote. |
| Stationary battery | **$775 per kW + $388 per kWh**; example 100 kW/400 kWh ≈ **$233k** | Supplies up to roughly four hours at full 100 kW before efficiency/reserve adjustments; longer support requires a smaller critical load or charging source | [NREL REopt scenario assumptions](https://www.nrel.gov/docs/fy25osti/90865.pdf), derived from its 2024 battery baseline. The report is for a different region, so this is a transparent order-of-magnitude benchmark, not a Bay Area installed price. [NREL's commercial battery model](https://atb.nrel.gov/electricity/2024/commercial_battery_storage) confirms that pack price alone omits inverter and balance-of-system costs. |
| Building dry floodproofing | **~$88k–$157k** for example 1,000–5,100 sq ft structures at low modeled depths | Keeps shallow floodwater out of protected rooms if design depth is not exceeded | [US Army Corps nonstructural cost appendix](https://www.nan.usace.army.mil/Portals/37/Appendix%20B5_Nonstructural_HATS.pdf), using its reference examples. Not transferable as a clinic quote without footprint and site design. |
| Deployable barrier | **$500–$3,000 per linear foot**; 100 ft ≈ **$50k–$300k** | Protects a specific entry or asset if installed before the event | [US Army Corps feasibility report](https://www.saw.usace.army.mil/Portals/59/siteimages/Flood%20risk%20management/Lumber_River_Basin_FRM_FinalReport.pdf?ver=5bmofg-tURRYZJz3Xx6H7w%3D%3D). Requires storage, crews, lead time, and monitoring. |
| Alternate-clinic transfer plan | **User-entered contract and per-trip costs** until we obtain a local operator quote | Shifts appointments to clinics with spare capacity and viable routes | [CMS emergency guidance](https://www.cms.gov/esrdnetworkorganizations/downloads/emergencypreparednessforfacilities2.pdf) discusses closing a facility and referring patients elsewhere. A generic ride price would be made up, so the demo must label any sample price as an assumption. |

**Crucial:** a $233k battery in the example cannot run 100 kW for 24 hours. A 24-hour outage requires at least 2.4 MWh at that load before losses, or a generator/charging source. The screen should expose this rather than quietly treating one battery icon as a universal fix. We should also not offer a generator or battery at a clinic whose electrical connection is under water unless the plan protects or relocates that connection.

### Optimization in one sentence

Select the set of clinic upgrades and response agreements that minimizes **estimated missed treatment slots across selected flood/outage scenarios**, subject to the $1 million cap, power and water requirements, intervention dependencies, alternate-clinic capacity, and passable-road routes.

For each scenario and clinic, compute available treatment slots from the **minimum of** station capacity, staff capacity, power-supported capacity, safe-water capacity, and reachable demand. The optimizer can use a weighted objective (expected gap across scenarios) or a worst-case objective; the UI should let us toggle between them. Show a baseline and a simple comparison such as “protect the largest clinics first” so judges can see why optimization changes the decision. The metric is treatment **access**, not “lives saved”; we lack patient schedules and clinical outcomes to make that claim.

## The three-minute demo

**0:00–0:25 — Establish the stakes.** Start above Oakland with dialysis clinics glowing cyan. “Dialysis is time-sensitive. During floods, one flooded switchboard or blocked road can remove treatment capacity across a neighborhood.” Zoom into the shoreline. Label all facility and hazard data sources.

**0:25–1:10 — Break the system.** Drag the mapped water-level control from 12 to 36 inches. Water fills low streets; a clinic glows amber because access fails; another goes red because its modeled electrical room floods. Switch outage duration from 12 to 24 hours: the small backup battery runs out. A panel shows the *estimated* treatment slots at risk and their causes. The visual should show the causal chain, not just a colored heatmap.

**1:10–2:05 — Make a constrained decision.** Set the hypothetical budget to $1 million and press **Optimize**. Candidate projects appear with their dollar costs. The chosen interventions animate into the 3D view: a protected electrical room, a backup-power icon with runtime, and a highlighted route to an alternate clinic. The budget meter fills. Unchosen projects stay visible but dimmed, making the tradeoff obvious.

**2:05–2:40 — Replay and compare.** Run the same flood again. Side-by-side before/after scenes show which clinics remain operational, which routes still fail, and the modeled reduction in missed slots. Raise water another level: the plan can fail again. This demonstrates scenario robustness instead of implying a perfect solution.

**2:40–3:00 — Land the mission.** “Lifeline turns flood maps into a concrete, budgeted continuity plan for essential care. Oakland is the pilot; the same data pipeline could be adapted to other coastal cities and other critical services.” Show a compact source/assumption badge so the judges see what is measured versus modeled.

## Build plan for five people

Use a **code-first web stack**: React/TypeScript + [CesiumJS and Cesium OSM Buildings](https://cesium.com/platform/cesium-ion/content/cesium-osm-buildings/) for the 3D city; Python for GIS preprocessing, road-network analysis, and optimization. Cesium supports [styling buildings and features](https://cesium.com/learn/cesiumjs-learn/cesiumjs-3d-tiles-styling/). No one needs to operate a Unity editor. Keep the scenario evaluator as a deterministic function behind the UI so the beautiful rendering always agrees with the numbers.

1. **Geodata:** download/crop the BCDC flood layers, terrain, and roads for one Oakland pilot area; verify the flood polygons and coordinates.
2. **Facilities and water/power:** ingest CMS clinics and station counts; define transparent, editable site assumptions for entrance elevation, generator, critical kW, water, and shifts.
3. **Scenario engine:** intersect facilities and roads with each mapped flood level; compute closures, backup runtime, reachable clinics, and estimated treatment slots.
4. **Optimizer:** choose intervention bundles under the dollar cap with dependencies; produce baseline, optimized, and larger-clinic-first comparison.
5. **3D experience and pitch:** build the water reveal, glowing service failures, intervention animation, comparison panel, and reliable three-minute click path.

**Hackathon scope:** one Oakland area, several real clinics, three mapped water levels, three outage durations, and five intervention types. The architecture can later support city search and many scenarios. For the 24-hour demo, make one local scene and its data airtight before making “any city” a promise.

## Biggest truth checks before we pitch

- Verify that the selected Oakland clinics or **their routes/utilities** intersect the published flood layer. If they do not, move the pilot focus within the Bay Area instead of inventing flooding.
- Check whether each featured clinic has a generator. Mark unknown infrastructure as an assumption; CMS says backup generators are not universally required, which does not tell us what a particular clinic has.
- Distinguish **coastal water level** from rainfall, river flooding, and outage duration. The controls represent different inputs.
- Check site-specific battery power, energy, critical load, and connection state. Generator fuel and water quality matter as much as the icon on the map.
- Tell judges that clinic station counts are observed, while appointments, staffing, room elevations, and some costs are scenario assumptions. This is a planning prototype, not an emergency dispatch system.
