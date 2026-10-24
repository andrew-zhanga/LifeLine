# FlareWise execution status

Active branch: `codex/flarewise-full-build`; base `3a0039b`. Unrelated untracked user documents preserved.

## Ownership
- Coordinator: contracts, config/dependencies, assembly, public data, integration, presentation, reports, docs, Git.
- Worker A: scripts/model, data/build/exposure, tests/model.
- Worker B: scripts/portfolio, data/build/portfolios, tests/portfolio.
- Worker C: demo/src, demo/public/ui, tests/ui.
Workers do not change Git state or edit outside assigned paths.

## Gates
G0 in progress: data inspected, integration branch created, contracts/app-v1.md and parameters.json frozen. Baseline production build running.
G1–G4 pending. Core uses historical deterministic screening; no trained model or health claims.

## Resume
Read contracts/app-v1.md, docs/EXECUTION_PLAN.md and this status. Use `.data-venv/bin/python` for preprocessing. Run `cd demo && npm run dev -- --port 5173` for preview; `npm run build` for production verification. Coordinator alone stages explicit completed paths, commits and pushes. Do not stage unrelated untracked files.

## Checkpoint G0
- Baseline production build passed in 11.31 s; existing large-chunk warning retained.
- 19/19 source hashes verified; prepared hash baseline in reports/input-integrity.json.
- All three workers acknowledged frozen contract. Dependencies installed and pinned.
- Baseline 1440×900 screenshot saved; current local preview http://localhost:5173.
- Coordinator assembly implementation in progress; do not treat as verified until actual outputs arrive.
