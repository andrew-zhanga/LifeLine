# Repository contents and current plan

The current application is FlareWise. Its code is in `demo/src/` and `scripts/`, with contracts, verified data, tests and presentation evidence in their matching directories. Current implementation specifications are `docs/BUILD_PROMPT.md`, `docs/EXECUTION_PLAN.md` and the additive `docs/EXTENSION_PLAN.md`. Completion records are `docs/BUILD_STATUS.md` and `docs/EXTENSION_STATUS.md`.

Final narrated presentation videos and the source recording are checked in under `presentation/extensions/video/`; its README identifies the Andrew-voice final version and the historical Samantha version.

## Historical planning material

The root-level Paris/heat/BDNB documents, `HACKATHON_DECISION_AND_BUILD_BRIEF.md`, and Oakland dialysis proposal `team-pitch.md` are earlier concept exploration. The root-level `FLAREWISE_DATA_FEASIBILITY_AUDIT.md` and `FLAREWISE_EXECUTABLE_PLAN.md` are pre-implementation planning records. They are preserved for project history and do not supersede the current specifications or describe the final shipped UI. `data/feasibility/` and `bdnb_paris_sample_audit.json` preserve public-data feasibility samples.

## Local-only dependencies and intermediates

Installed environments, node dependencies, Python bytecode, build caches, downloaded raw datasets and intermediate video renders are intentionally excluded. Source code, processed application artifacts, the trained small-model checkpoint, reproducible scripts and final presentation outputs are included. Raw datasets can be reacquired through the documented data workflows.
