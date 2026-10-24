# Pitch strategy, rubric and verified sources

Reviewed October 24, 2026. The user-provided rubric gives four criteria equal 25% weights. The attached guide confirms the Climate & Health track is judged by TotalEnergies and Stanford's Sustainability Accelerator (page 3), and judging allows three minutes plus two minutes of questions (page 6). The two listed Track 2 prompts concern heat plans and dengue; FlareWise addresses the broader track question about environmental data informing public-health action, not either named prompt. Do not imply it implements a named challenge.

## Scorecard

| Criterion | What the video proves | Screen |
|---|---|---|
| Relevant sustainability challenge | Wasted gas value; published Eagle Ford health association; limited-budget capture decision | Sourced opening statistics, globe, South Texas |
| Creativity | Joint economic/community prioritization produces different actual investment portfolios; 95.51% NPV retention with >2× index improvement | Financial → Balanced → Community |
| Technical feasibility | Mixed-integer optimization, all 8,760 historical weather hours, tract attribution, mass-accounted puff transport, GPU rendering, trained U-Net and held-out evaluation, 41 passing tests | Working maps, moving capture replay, actual prediction panels |
| Pathways for scale | Operator capital/HSE teams as prospective users; public-health planners as collaborators; proposed engineering-data pilot and measured outcomes; basin-by-basin expansion | Closing result and pilot roadmap |

## Strongest opening statistics

1. **167 billion cubic meters / $54 billion, calendar 2025.** World Bank, *Global Gas Flaring Tracker 2026*. Use the $54 billion value as the hook; volume establishes scale. Source: https://www.worldbank.org/en/programs/gasflaringreduction/publication/2026-global-gas-flaring-tracker-report . The report also gives 429 million tonnes CO2e, but adding this fourth opening number would dilute recall. Do not combine the 2025 figures with the older 2024 report's $63bn/151bcm figures. The product's source inventory remains the separately labeled 2023 dataset.
2. **50% higher odds of preterm birth associated with high flaring exposure.** Cushing et al., 2020, *Environmental Health Perspectives*, retrospective cohort of 23,487 births in Eagle Ford (2012–2015), OR 1.50, 95% CI 1.23–1.83. Source: https://pubmed.ncbi.nlm.nih.gov/32673511/ ; full article https://pmc.ncbi.nlm.nih.gov/articles/PMC7362742/ . Exposure classification counted nightly flares within 5 km during pregnancy. Further adjustment for nearby wells attenuated OR to 1.41. This motivates the community objective; it is not our model's predicted health benefit, proof of causation, or a 50-percentage-point increase.
3. **95.51% retained NPV; 5.25% → 10.61% population-weighted index reduction.** Our actual $10m South Texas Financial versus Balanced portfolios. Source: `data/build/community/community.json`. Community-only reaches 22.22%, with lower NPV. The creative result is the explicit tradeoff, not a promise of observed pollution or disease reduction.

## Why TotalEnergies would care

TotalEnergies publicly commits to ending routine flaring by 2030. It already operates emissions-detection programs such as AUSEA; FlareWise's proposed differentiator is an investment-prioritization and community-attribution workflow that can complement an operator's measurements. It does not replace engineering or claim TotalEnergies lacks monitoring. Sources: https://totalenergies.com/sustainability/climate-and-sustainable-energy/reducing-our-emissions and https://totalenergies.com/news/news/methane-emissions-innovation-serving-enhanced-monitoring .

Proposed buyer/user: asset-level capital allocation and decarbonization teams. Collaborators: HSE teams, local environmental/public-health planners, capture developers and infrastructure partners. Value proposition: compare economics and downwind community priorities under a real budget; explain why particular sites should proceed to engineering review. No existing TotalEnergies partnership is claimed.

## Scale narrative

A proposed first pilot imports operator-specific engineering costs, gas composition, infrastructure access and constraints. Environmental measurements check transport assumptions. Track recovered gas, project returns and independently verified emissions changes, then expand through regional weather, population and infrastructure inputs. The existing 77-country inventory supports discovery; worldwide analytical coverage is a future expansion.

Do not describe the industrial-smoke network as operational gas-flare detection or the upstream engine feeding today's optimizer. It is a separately trained segmentation capability with actual held-out results. Present the three technical components as demonstrated capabilities within one product, without inventing integration.

## Recording

Narration is computer-generated (Microsoft Andrew Multilingual Neural; refreshed from the original macOS Samantha voice). The final MP4 uses actual recorded product footage and browser screenshots, with sourced title cards. Spoken claims remain confident and concise; detailed scope and source notes belong here and in Q&A.
