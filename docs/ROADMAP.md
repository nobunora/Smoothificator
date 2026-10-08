# Development Roadmap

Implementation is gated. Do not advance until the previous phase exit criteria pass.

## Phase 0 — specification and technical audit

Current-Orca drift check:
- re-audit the pinned source baseline whenever Orca main/release changes materially;
- explicitly diff PluginHostSlicing/SlicingPipeline/GCode/Flow/Extruder/Print/PrintObject/PrintConfig semantics;
- newly introduced execution paths default to analysis-only until modeled or gated.

Complete before production code:
- document precedence and AGENTS workflow;
- unique ADR set through ADR-0041;
- source-verified Orca hook/ZAA/config/G-code semantics;
- centered source-frame contract;
- geometric versus commanded flow separation;
- constant-Z candidate path and deterministic seam/gap contract;
- final matcher/frame/quantization/retraction contract;
- chronological plugin + downstream original-motion clearance contract;
- final structural deposition/seam-gap parity validation;
- modal/runtime override envelope;
- attempt-scoped runtime evidence / TOCTOU protection;
- timelapse/wrapping/object-exclusion gates;
- extrusion-rate-smoothing and inherited-acceleration gates;
- ToolClearanceProfile physical-evidence requirement;
- full-text consistency audit.

Exit:
- no duplicate/conflicting ADR identifiers;
- normative docs internally consistent;
- no known source/API blocker inside narrowed v1 scope;
- audit findings recorded;
- handoff spec references the audited canonical revision.

## Phase 0.25 — review-only repository validation

Before implementation:
- update docs/specs/adaptive-subedge-v1.md with the audited canonical commit;
- create an implementation record from TASK_TEMPLATE;
- run .codex/repository-review.md;
- disposition must be validated.

Any new material conflict returns to specification adjudication.

Specification/design PR and production implementation PR remain separate.

## Phase 0.5 — architecture skeleton

Implement only:
- package/module tree;
- frozen domain DTOs;
- typed errors/reason codes;
- validated Settings;
- ExecutionConfigFingerprint;
- PluginSettingsFingerprint;
- ToolClearanceProfile schema;
- canonical serializer/hash;
- PlanStore + InjectionAttemptStore;
- AnalysisGenerationId / InjectionAttemptId contracts;
- architecture/import-boundary tests.

No Orca/G-code/optimizer behavior yet.

## Phase 1A — bead / flow primitives

Implement/test:
- rounded-rectangle geometric bead formula and explicit width>=height domain;
- plugin-configured min/max candidate width/height bounds;
- ZAA local geometry ratio;
- geometric versus commanded volume separation;
- Orca external-wall command-flow multipliers including print/filament/optional outer-wall ratios;
- effective bead height above support;
- SupportCoverageMetric + configured support thresholds;
- versioned SupportCoverageMetric and threshold contract;
- no-refinement baseline identity.

Exit:
- reference formulas/parity tests pass;
- invalid physical candidates reject deterministically.

## Phase 1B — surface-band geometry

Implement:
- finite/manifold mesh validity gates;
- source orientation/material-side validation and mirrored-transform parity;
- orientation/material-side validation including mirrored transforms;
- mesh plane sections;
- exactly-one-simple-target-loop gate;
- material boundary representation;
- centerline placement inside material;
- constant-Z SubEdgePath invariant;
- same-Z and different-Z multi-path coverage;
- deterministic candidate seam/gap;
- nesting/support checks;
- chronological support envelope;
- acyclic candidate support dependency/order.

Exit:
- boundary is never treated as centerline;
- shallow terrace may require multiple paths;
- varying-Z candidate path rejected;
- unsupported/ambiguous geometry rejected.

## Phase 1C — converged error / optimizer

Implement:
- structural + candidate nominal finite-bead envelope;
- versioned deterministic ErrorEstimatorConfig;
- sampling refinement/convergence for hard normal-error metrics;
- candidate geometry/flow search;
- cost model;
- deterministic optimizer;
- cancellation.

Exit:
- synthetic/fixed-angle cases improve or safely report infeasible;
- no Orca/G-code dependency.

## Phase 2A — Orca snapshot and centered frame

Stock Orca read-only:
- posSimplifyPath;
- source ModelInstance/ModelVolume snapshot;
- centered-frame reconstruction;
- path relative-Z -> absolute Z;
- local ZAA geometry normalization;
- resolved semantic config;
- source/profile gate detection;
- mixed-filament virtual-slot/sublayer/gradient rejection for printable v1.

Exit:
- translated/rotated/scaled/shrink fixtures;
- ZAA on/off fixtures;
- connected-shell/simple-section/manifold/orientation gates;
- no live-reference escape.

## Phase 2B — Analyzer / PlanStore

Wire snapshot -> engine -> immutable plan.

Implement:
- both fingerprints;
- AnalysisGenerationId / InjectionAttemptRecord infrastructure;
- structural loop references;
- candidate open paths/seams;
- current-session plan state.

Exit:
- real Orca coupon plan generated;
- unsupported configs analysis-only;
- deterministic hashes;
- stale/fingerprint mismatch behavior tested.

## Phase 3 — Plugin preview

Script capability:
- baseline/ZAA paths;
- target material boundary;
- candidate paths and seams;
- local bead-height and geometric/commanded flow;
- error map;
- support diagnostics;
- unmet compatibility gates;
- plan hash/status.

Exit:
- preview uses exact stored plan;
- no UI from slicing worker;
- no plan mutation.

## Phase 4A — exact Bambu fixture acquisition

Choose the first exact Orca commit/release and Bambu 0.4 mm machine/process/filament set.

Record:
- resolved semantic config;
- source G-code;
- ToolClearanceProfile source/measurement;
- plugin settings.

Verify all Gate J assumptions in TEST_STRATEGY, including G21/G90 and M220/M221 unity at supported anchors.

No physical injector support until fixtures exist.

## Phase 4B — binary streaming parser dry-run

Read-only:
- units / XYZ / E / M200 / M220 / M221 / G92 modal state;
- logical E versus physical retraction debt;
- actual XYZ/feed/tool;
- E/retraction debt;
- layer/custom-code markers;
- calibration/unknown-motion rejection;
- plugin idempotence markers;
- raw-byte/newline preservation contract.

Exit:
- manually verified parser report matches fixture;
- no writes;
- unknown critical state rejects.

## Phase 4C — structural matcher and execution frame

Implement:
- seam-start invariant matching;
- seam-gap clipping allowance;
- collinear subdivision handling;
- unique-match requirement;
- constant machine translation derivation.

Exit:
- correct fixture matches exactly once;
- wrong/ambiguous loop rejects;
- non-constant transform rejects.

## Phase 4C2 — final structural deposition parity

Implement:
- local final positive-E structural deposition reconstruction;
- seam-gap/quantization-aware lower support parity;
- nearby structural support/collision context;
- actual final matched external-wall feed extraction.

Exit:
- support lost at final seam rejects;
- hard local tolerance/overbuild revalidation passes;
- actual matched feed upper bound established.

## Phase 4D — Orca quantizer / E / speed / acceleration / retraction

Implement:
- XYZ/F 3-decimal parity;
- E 5-decimal parity;
- C++ half-away-from-zero rounding;
- final E from quantized XYZ length;
- commanded-flow conversion;
- speed/volumetric limits;
- Pressure Equalizer disabled gate;
- inherited acceleration parsing/cap;
- exact temporary unretract/retract state cycle;
- Zsafe travel and actual-state restore.

Exit:
- all Gates N–Q pass on fixture copies;
- no original-file mutation.

## Phase 4E — chronological final tool-clearance validation

Implement:
- quantized candidate bead envelopes;
- ToolClearanceProfile swept volume;
- chronological printed-material simulation;
- plugin-generated vertical/travel/extrusion/return validation;
- downstream original travel/extrusion classification;
- conservative validation horizon;
- full-file fallback when no earlier barrier is proven.

Exit:
- safe cases pass;
- plugin self-motion/body collisions reject;
- later-candidate versus earlier-candidate collisions reject;
- low-Z ZAA/travel collisions reject;
- missing keep-out evidence disables physical mode;
- deterministic clearance tests pass.

## Phase 4E2 — runtime dynamic-feature compatibility

Implement/validate:
- timelapse mode gates;
- farthest-point timelapse gate;
- wrapping detection gate;
- wipe/prime tower presence gate;
- exclude_object gate;
- exact supported Traditional timelapse fixture behavior.

Exit:
- every unreplicated dynamic feature fails closed;
- permitted Traditional fixture is fully parser/state/clearance covered.

## Phase 4F — streaming atomic injector

Implement:
1. binary-stream validation pass;
2. byte-preserving temp emission;
3. binary-stream sanity pass;
4. atomic replacement.

Exit:
- original unchanged on every failed validation;
- source digest/metadata TOCTOU guards pass;
- PluginSettingsFingerprint precommit recheck passes;
- concurrent/repeated attempts preserve independent records;
- PluginResult policy tested;
- repeated export/upload copies handled independently;
- idempotence passes;
- bounded-memory large-file test passes;
- LF/CRLF/no-final-newline and opaque-comment byte preservation passes.

## Phase 4G — implementation review convergence

Before hardware:
- primary implementation review;
- independent blind review;
- finding reconciliation;
- zero unresolved Critical/High findings;
- exact ToolClearanceProfile evidence reviewed.

Exit:
- REVIEW_PROCESS convergence criteria satisfied.

## Phase 4H — metadata / thermal limitation validation

Before physical interpretation:
- verify original Orca progress/time/material metadata is treated as pre-injection;
- record plugin-added estimated time/material;
- document cooling/fan/min-layer-time settings;
- do not rewrite thermal/progress metadata in v1.

## Phase 5 — first physical PoC

Only after Phase 4G.

Initial:
- exact supported Bambu 0.4 mm fixture;
- PLA;
- one-object/one-instance/one-volume manifold coupon;
- nested/self-supported slope;
- first-layer region excluded.

Sequence:
1. 5-degree coupon;
2. 10/20-degree coupons;
3. smooth 1–30-degree surface;
4. conservative near-clearance coupon.

Unexpected motion/contact/overbuild/stringing returns project to specification/model review.

## Phase 5.5 — estimate/progress validation

Before broader benchmark:
- verify UI labels Orca time/material/progress as pre-postprocess;
- verify plugin delta estimates;
- document M73/progress under-reporting limitation.

## Phase 6 — physical calibration and benchmark

Calibrate/measure:
- actual bead geometry versus nominal model;
- ToolClearanceProfile margins;
- surface roughness/error;
- time/material.

Compare:
- normal;
- fine conventional;
- ZAA-only;
- ZAA + SubEdge.

No generalized superiority claim outside measured classes.

## Phase 7 — controlled expansion

One capability at a time:
- additional Bambu profiles/hotends;
- richer surface bands;
- holes/multiple loops;
- multi-volume CSG;
- multiple objects/instances;
- support/overhang classes;
- absolute E;
- arcs;
- adaptive volumetric speed;
- fuzzy skin;
- adaptive PA/role-state parity;
- other firmware;
- multitool last.

Each requires fixtures/tests and ADR when safety semantics change.

## Phase 8 — production plugin

- compatibility matrix;
- pure-Python wheel;
- tolerance/quality UI;
- performance/resource limits;
- regression corpus;
- analysis-only fallback;
- release/review records.
