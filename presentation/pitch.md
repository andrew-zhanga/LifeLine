# FlareWise · three-minute narration

**0:00–0:25 — The decision.** Gas flaring wastes a potentially useful resource. For an operator with a limited capture budget, the question is where to invest. The projects with the strongest gas economics may differ from those that reduce the most modeled exposure downwind. FlareWise makes that choice inspectable.

**0:25–0:45 — Enter South Texas.** These are 8,783 real sites in the World Bank's 2023 satellite-derived inventory. We focus on a South Texas study box with 392 capture candidates and 30 background sources. This is a historical scenario, not a live pollution monitor.

**0:45–1:15 — Follow real wind.** Play the 48-hour window. The weather changes, and so does the modeled field. The equipment stays fixed. Selection uses all 8,760 hours of the year. We combine coarse ERA5 winds with a relative transport kernel and population allocated within Census tracts. This is screening, not a concentration or health prediction.

**1:15–1:35 — Inspect the inputs.** Open a source to see estimated annual gas and pipeline-distance-based cost. Open a community to see Census population and age context. We distinguish source observations, published estimates, and assumed project costs, rather than hiding those differences behind one score.

**1:35–2:15 — Make the decision.** At $5 million, Financial and Balanced select the same sites: the objectives align. Switch to $10 million to see a distinct tradeoff. The Financial plan selects 9 sites, with a seven-year screening NPV of $33.64 million and 5.25% annual modeled exposure reduction. Balanced selects 10 sites and retains 95.51% of that NPV while reaching 10.61% reduction: a change of 5.36 percentage points. Before and after use identical weather and a shared scale. Only the chosen sources are reduced, using the stated 90% capture assumption.

**2:15–2:40 — Show the tradeoff.** Every plotted point is an actual budget-feasible portfolio with a matching map. The method is deterministic exposure screening plus integer optimization. We verify population conservation, portfolio budgets, source-removal monotonicity, and agreement with an exhaustive small solver example. These are implementation checks, not predictive accuracy.

**2:40–3:00 — Next step.** The practical next step is an operator pilot: replace screening costs with engineering quotes, confirm pipeline access, and compare transport estimates with independent environmental observations. FlareWise provides an auditable way to decide which projects deserve that deeper investigation.
