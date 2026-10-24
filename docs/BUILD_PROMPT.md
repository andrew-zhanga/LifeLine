# Ready-to-paste execution prompt

Paste the text below into a new Codex chat attached to this LifeLine project. It authorizes the implementation run; writing this file has not started that run.

---

Build FlareWise end to end using this repository's `docs/EXECUTION_PLAN.md` as your execution specification and `docs/PITCH_BRIEF.md` as the product story. Read `docs/BUILD_STATUS.md` first to resume any completed work, then `data/verified/README.md`, `data/verified/build_contract.json`, the root README and the current `demo/` code. The repository is https://github.com/andrew-zhanga/LifeLine. Original local workspace: /Users/aditya/Documents/ChatGPT/CleanTechHackathon. If this checkout differs, use the actual project root. All necessary context is in the repository; the original PDF is not required.

Your goal is a strong, complete judge-facing hackathon product and presentation evidence pack. Preserve the existing globe, smooth camera transitions and dark visual design. Replace the demo's dummy calculations with the already retrieved 2023 flare/weather/population data, screening economics, fixed budgeted capture portfolios and consistent before/after maps. Complete the whole Earth → Texas → real wind/community inspection → investment tradeoff journey. Do not stop at writing another plan.

Use three worker agents in parallel, with you as coordinator:

1. Exposure/replay agent: only `scripts/model/`, `data/build/exposure/`, `tests/model/`. Implement sparse wind-driven exposure, period contributions, 48-hour replay and meaningful model checks. Deliver one actual frame early. Follow the frozen contract and parameter file.
2. Economics/optimization agent: only `scripts/portfolio/`, `data/build/portfolios/`, `tests/portfolio/`. Implement explicit screening costs, seven-year NPV, financial/balanced/exposure portfolios, actual tradeoff points and small sensitivity experiments. Start independently on economics; use final exposure benefits before publishing portfolios.
3. Frontend agent: only `demo/src/`, `demo/public/ui/`, `tests/ui/`. Wire the frozen data contract into the existing UI, replace dummy production values, make every button purposeful, preserve transitions, ensure coherent loading and polish at presentation resolution.

You own contracts, example fixtures, dependencies/config, final asset assembly, `demo/public/data/`, integration checks, GitHub operations, screenshots, `presentation/`, `reports/` and shared docs. Freeze interfaces before worker integration. Never edit a worker's active files without handing ownership back and forth. All agents share a filesystem: disjoint paths and a single Git writer are mandatory. Workers must not commit, switch branches, pull, merge, reset, stash or push.

Create/reuse the integration branch `codex/flarewise-full-build` after inspecting the actual local/remote state. Preserve existing user work. Fetch/check GitHub at coherent checkpoints, roughly every 20–30 minutes, and regularly commit and push verified incremental progress. Stage explicit ready paths only, never all workspace files. Resolve overlapping remote changes centrally without force-pushing. Create/update a draft PR after the first complete vertical slice and attach it to this chat. Do not merge it automatically. Keep `docs/BUILD_STATUS.md` current with checkpoints, commit IDs, ownership, blockers and resume steps.

Make practical decisions without repeatedly asking for confirmation. The plan supplies defaults. Finish authorized work, but don't spin: after roughly 15 minutes or two failed approaches on a noncritical problem, take a simpler fallback. Don't rewrite working code for elegance. Fix visibly poor behavior and the few numerical/state errors that would invalidate the story. If a feature is already convincing and coherent, move on.

The current model is deterministic exposure screening plus discrete optimization, not a trained neural network. Do not invent training, segmentation, accuracy, health outcomes or independent validation. Train anything only if core delivery is complete and the optional experiment has real inputs, labels and a meaningful held-out evaluation. A neural network is not required. Save actual run artifacts and report real metrics, including failures/limitations. High data-quality and invariant-test pass rates are welcome but are not predictive accuracy.

Generate professional pitch assets during checkpoints: actual wind rose, shared-scale before/after maps, real financial/exposure frontier, a sensitivity plot, an accurate method diagram, actual UI screenshots, and a claim ledger linking slide numbers to data/scenarios. Write a 3-minute script, 6–8-slide storyboard and concise judge Q&A. Optional: a locally viewable HTML slide deck if the app and evidence pack are already complete. Use real charts and model outputs, not fabricated scientific visuals.

The plan targets a useful integrated slice in ~2 hours and a focused 4–6-hour build, but these are estimates, not a reason to wait or burn tokens. Prioritize core deliverables, then presentation polish, then bounded extensions tied to the pitch. Don't leave unfinished background agents/processes you no longer need. No need to wait until a nominal overnight deadline if the deliverables are complete.

Run the app in the browser and rehearse the real judge path, not just a production build. Test budget/time/priority invariants, layer controls, details, before/after, responsive presentation layout and fallback behavior. Keep local preview working. Public deployment is optional if a configured service is available; no paid resources are required.

Carry the task through to implementation, testing, GitHub checkpoints and final handoff. Report the branch/commit/PR, preview/deployment URL, delivered features, actual verification, presentation assets and remaining limitations. Read the full execution plan for exact formulas, file contracts, acceptance gates, fallbacks and ownership.

---

## Short launcher when this file is already in the project

“Read `docs/BUILD_PROMPT.md` and execute the implementation request it contains. Use `docs/EXECUTION_PLAN.md` as the detailed specification, coordinate the three worker agents, and carry the build through to verified GitHub checkpoints and the presentation evidence pack.”
