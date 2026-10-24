# FlareWise execution status

## Current state

- Execution brief prepared. The full implementation run has **not started**.
- Existing demo and verified data bundle were pushed to main at `78ef33a`.
- Current frontend still uses dummy values. The prepared real-data bundle is separate.
- Two read-only planning reviewers assessed frontend and model coordination; their recommendations are incorporated into `EXECUTION_PLAN.md`. They did not implement features.
- No active file-ownership claims from implementation workers yet.

## Start here

1. Read `BUILD_PROMPT.md`, `EXECUTION_PLAN.md` and `PITCH_BRIEF.md`.
2. Inspect actual Git status/remote; do not assume this status file's recorded base is the latest commit.
3. Create/reuse `codex/flarewise-full-build`, freeze the shared schema and dispatch three workers as specified.
4. Use the verified processed files; do not rerun bulk downloads unnecessarily.

## Gate tracker

| Gate | Status |
|---|---|
| Verified source-data acquisition | Complete |
| Dummy UI prototype | Complete |
| G0 final runtime contract and worker dispatch | Not started |
| G1 real vertical slice | Not started |
| G2 complete decision flow | Not started |
| G3 full product integration | Not started |
| G4 presentation assets and browser rehearsal | Not started |
| G5 optional extensions | Not started; not required |

## Known boundaries

- Data is historical, not live; World Bank inventory is VIIRS-derived.
- Population within tracts is allocated by area; fine-grained resident locations are not observed.
- Costs, capture efficiency and gas composition are screening assumptions.
- No imagery/labels for segmentation and no independent pollutant-validation dataset are in the bundle.
- The initial 17.41% integration result is a smoke-test fixture, not the final portfolio claim.
- Basemap/font requests still depend on network; final run needs a basic fallback and presentation backup.

## Working commands

```sh
cd demo
npm ci
npm run dev -- --port 5173
# Production check:
npm run build
```

The existing local preview may already occupy port 5173. Inspect before starting a conflicting process; use the existing session or a free port deliberately.

## Update during execution

Append only concise milestone entries: date/time, commit/branch, owner/path assignments, completed outputs, checks, current blockers, next action and exact restart command. Record a known-good commit before optional experiments. Do not fill this file with full agent transcripts.
