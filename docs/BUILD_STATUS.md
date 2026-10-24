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

## G1/G2 numerical integration
- G0 pushed: `e4bb5ec`.
- A complete: full 8,760-hour run, 71,862 links, real Dec 10–11 replay; 57.24 s rebuild, 1.106 GB peak RSS. Eight model tests and ten data invariants pass.
- B complete: 25 named/frontier plans at $2m/$5m/$10m benchmark price; eight sensitivities. All solves optimal; six tests and seven output invariants pass.
- $5m Financial/Balanced coincide (4 sites, $19.754m NPV, 3.6401% reduction). Do not imply a difference. $10m Balanced is distinct (10.611% vs Financial 5.248%).
- Assembly validates budgets, totals, ordering and all before/after frames. Analytical initial assets 2,558,309 gzip bytes; largest plan 648,991 gzip bytes (compression measurement, server transfer may be uncompressed).
- C delivered UI; real globe → region → replay → source economics verified in Chrome. C retains ownership for legend, chart labels and intentional basemap fallback control.
- Coordinator preview: http://localhost:5174 (Vite dev). Existing port 5173 is a production preview and needs a rebuilt dist to reflect changes.
- Next: finish browser walkthrough and projector-size checks, update pitch to honestly show aligned $5m objectives and distinct $10m tradeoff, create draft PR after frontend checkpoint.
