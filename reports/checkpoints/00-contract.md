# G0 — interface and baseline

Base commit: `3a0039b`; integration branch `codex/flarewise-full-build`.

- Frozen contracts/app-v1.md and centralized parameters.json, disjoint three-worker ownership recorded in BUILD_STATUS.
- Baseline Vite build passes (11.31 s); existing warning: main JS chunk >500 kB.
- 19/19 available raw source hashes verified against download manifest; 12 prepared file hashes recorded in reports/input-integrity.json.
- Baseline Chrome screenshot at 1440×900: presentation/screenshots/00-baseline-prototype.png. This is explicitly the old illustrative UI, not final evidence.
- Dependencies pinned for offline computation. No bulk input downloads.
- Local preview already running at http://localhost:5173.

Next: actual sparse exposure frame, economics output, frontend loader, then validated assembly and browser rehearsal. No product claims from old smoke-test values.
