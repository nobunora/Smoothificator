# ADR-0073: Prepared calibration matrix library and Script export

Status: Accepted for the bounded experimental calibration library.
Date: 2026-10-19

The user requests additional necessary matrices and access from the plugin. Extend ADR0072 with four separately identified prepared trials: clearance/volume, end-retraction/wipe, controlled first2mm extra extrusion/start debt-recovery speed, and final-volume/drawing-speed. Each uses the same original64mm numbered source and25cells. Ordinary geometric filler, legacy V1 identity/bytes and production injection gates remain unchanged.

Restart compensation is positive XY deposition along the first2mm, never an unexplained extra stationary unretract. Recover exactly the saved initial debt; vary only that start debt-recovery speed. End handling and raised-ceiling debt reconciliation retain their independently fixed parameters. Record startup dose, baseline/extra/total E and segment quantization separately. The approved maximum end retraction remains1.6mm; do not increase it to2.4mm as part of this task. Detailed finite axes and acceptance live in `../specs/prepared-calibration-matrix-library.md`.

The currently verified Script host API does not supply a verified live slicing/export backend. Add a dedicated Script calibration capability that requires no active model, exports immutable prepared rawG-code bytes into plugin-owned storage, and records user selections. It does not generate from the live model or live printer configuration, invoke an external slicer, mutate the current project, install software or send a printer job. Existing preview capability remains separate. Default distribution can omit prepared resources and must report that honestly; the delivered calibration wheel explicitly includes the vetted bundle.

UI/application code must not import tools, the optimizer or G-code mutation adapters. The offline owner generates and audits trials, CSV, plots, frozen manifests and a closed bounded bundle. The builder explicitly validates and packages only allowlisted bundle assets with per-file hashes and a pinned catalog identity. Plugin export checks these identities and copies exact prepared bytes into a unique contained directory. Raw`.gcode` is always the primary output; reslicing a model would lose the experiment. A geometry-only baseline project (no embedded G-code) may be exported separately to load the reference settings. No arbitrary local paths, code, URLs or commands are accepted from a UI message or resource manifest.

Read an explicit bounded allowlist of current `full_config_value` opt_serialize strings on the UI thread and compare SHA256 hashes against the exact corresponding original source-header strings; do not guess normalization or reuse the viewer sanitizer. Missing or mismatched REQUIRED keys disable raw/G-code-archive export; show key names, not configuration values or macros. Optional profile fields absent from the original header are explicitly outside the comparison scope rather than guessed as nil. The comparison is a source-header-key guard, not proof of complete live/saved profile equivalence. The files always use the identified FROZEN reference profile and provisional fixed settings, never a claim of live-profile generation. Geometry-only baseline-project export remains available when compatibility is unknown/mismatched. Current machine/material/frame/temperature/motion and available macro fields belong in the required guard; auth/host credentials never do.

Selection records bind trial/policy/source identities, selected cell and symptom. A next-range button may persist a clearly named proposal/request using deterministic refinement. Until a reviewed real backend exists, it must not claim a new trial/G-code has been produced. Choosing a cell or creating a request never starts printing or changes ordinary plugin policies. The fixed prepared trials remain explicitly provisional, not previously selected winners. Explain that the current .45mm display width is visualization metadata and actual commanded E/volume varies.

This changes the isolated Script package's capability from preview-only to preview plus source-bound prepared experimental file export; update canonical summaries and wheel metadata accordingly. It grants no production print safety certification or automatic printer access. Focused tests, full regression, independent execution/export review, bundle read-back and packaged/UI validation are required separately.


Amendment2026-10-19, latest user instruction: new volume_speed trials use source-
relative drawing speeds,20/40/60/80/100percent of an explicitly reconstructed
source/profile/machine-limited reference. Preserve the earlier absolute-speed
schema and prepared outputs for replay. New native policy3/ready-bundleV2 and
wheel0.3.1 use the bounded contract `../specs/source-relative-calibration-speed.md`.
This changes calibration parameters and evidence, not Script/export ownership.
