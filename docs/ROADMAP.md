# Development Roadmap

Implementation is gated. Do not advance until the previous phase exit criteria pass.

## Phase 0 — specification and technical audit

Complete before production code:
- document precedence and AGENTS workflow;
- unique ADR set through ADR-0029;
- source-verified Orca hook/ZAA/config/G-code semantics;
- centered source-frame contract;
- geometric versus commanded flow separation;
- constant-Z candidate path and deterministic seam/gap contract;
- final matcher/frame/quantization/retraction contract;
- downstream original-motion clearance contract;
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
- PlanStore/status store;
- architecture/import-boundary tests.

No Orca/G-code/optimizer behavior yet.

## Phase 1A — bead / flow primitives

Implement/test:
- rounded-rectangle geometric bead formula;
- ZAA local geometry ratio;
- geometric versus commanded volume separation;
- Orca external-wall command-flow multipliers;
- effective bead height above support;
- no-refinement baseline identity.

Exit:
- reference formulas/parity tests pass;
- invalid physical candidates reject deterministically.

## Phase 1B — surface-band geometry

Implement:
- finite/manifold mesh validity gates;
- mesh plane sections;
- material boundary representation;
- centerline placement inside material;
- constant-Z SubEdgePath invariant;
- same-Z and different-Z multi-path coverage;
- deterministic candidate seam/gap;
- nesting/support checks.

Exit:
- boundary is never treated as centerline;
- shallow terrace may require multiple paths;
- varying-Z candidate path rejected;
- unsupported/ambiguous geometry rejected.

## Phase 1C — error / optimizer

Implement:
- structural + candidate nominal finite-bead envelope;
- normal-error metrics;
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
- source/profile gate detection.

Exit:
- translated/rotated/scaled/shrink fixtures;
- ZAA on/off fixtures;
- manifold/section gates;
- no live-reference escape.

## Phase 2B — Analyzer / PlanStore

Wire snapshot -> engine -> immutable plan.

Implement:
- both fingerprints;
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

Verify all Gate J assumptions in TEST_STRATEGY.

No physical injector support until fixtures exist.

## Phase 4B — streaming parser dry-run

Read-only:
- modal state;
- actual XYZ/feed/tool;
- E/retraction debt;
- layer/custom-code markers;
- calibration/unknown-motion rejection;
- plugin idempotence markers.

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

## Phase 4D — Orca quantizer / E / speed / retraction

Implement:
- XYZ/F 3-decimal parity;
- E 5-decimal parity;
- C++ half-away-from-zero rounding;
- final E from quantized XYZ length;
- commanded-flow conversion;
- speed/volumetric limits;
- exact temporary unretract/retract state cycle;
- Zsafe travel and actual-state restore.

Exit:
- all Gates N–Q pass on fixture copies;
- no original-file mutation.

## Phase 4E — downstream original-motion clearance

Implement:
- quantized candidate bead envelopes;
- ToolClearanceProfile swept volume;
- downstream original travel/extrusion classification;
- conservative validation horizon;
- full-file fallback when no earlier barrier is proven.

Exit:
- safe cases pass;
- low-Z ZAA/travel collisions reject;
- missing keep-out evidence disables physical mode;
- deterministic clearance tests pass.

## Phase 4F — streaming atomic injector

Implement:
1. validation pass;
2. temp emission;
3. sanity pass;
4. atomic replacement.

Exit:
- original unchanged on every failed validation;
- PluginResult policy tested;
- repeated export/upload copies handled independently;
- idempotence passes;
- bounded-memory large-file test passes.

## Phase 4G — implementation review convergence

Before hardware:
- primary implementation review;
- independent blind review;
- finding reconciliation;
- zero unresolved Critical/High findings;
- exact ToolClearanceProfile evidence reviewed.

Exit:
- REVIEW_PROCESS convergence criteria satisfied.

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
