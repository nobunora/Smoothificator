# Test Strategy and Release Gates

Tests are organized by ownership boundary so failures identify the responsible component.

Apply `docs/QUALITY_GATES.md` before broad behavioral suites.

Physical printing is forbidden until every preceding software, fixture, and review gate required by this document passes for the exact target compatibility descriptor.

## Gate A — Governance and architecture

Owner: `tests/architecture/`

Check:
- ADR identifiers unique;
- superseded ADR status/reference consistency;
- required handoff/canonical revisions present;
- forbidden imports;
- no live Orca types in domain/engine;
- G-code adapter does not import optimizer/source-mesh modules;
- UI does not import optimizer/live Orca;
- config-resolution owner is unique;
- quantizer owner is unique;
- no generic utility dumping-ground introduced.

## Gate B — Domain determinism

Check:
- frozen domain DTOs;
- schema versioning;
- canonical serializer;
- deterministic plan hash;
- timestamp/runtime ObjectID/machine translation excluded from plan hash;
- PlanExecutionStatus separate from plan;
- deterministic ExecutionConfigFingerprint canonicalization.

## Gate C — Orca centered-frame adapter

Pinned Orca/source fixtures verify:
- exactly one total instance accepted;
- multiple total instances reject injection;
- volume-local -> centered PrintObject frame parity;
- translated instance;
- rotated instance;
- scaled instance;
- shrink-compensated PrintObject transform;
- mirrored case if target profile/model supports it;
- bounding/path parity tolerance;
- wrong transform rejection;
- no live/zero-copy reference escape.

## Gate D — Orca ZAA parity

Verify against audited source behavior:
- path Z offset -> absolute Z;
- local effective height;
- local ZAA geometry-directed volume ratio;
- non-ZAA planar identity;
- invalid effective height rejection;
- ZAA enabled/disabled `posSimplifyPath` behavior.

## Gate E — Flow semantics

### Geometric bead
- rounded-rectangle geometric area formula;
- invalid width/height;
- effective width reconstruction where used.

### Commanded flow
Parity for:
- print_flow_ratio;
- filament_flow_ratio;
- set_other_flow_ratios off/on;
- outer_wall_flow_ratio;
- filament cross-section conversion.

### Modeling separation
- changing filament_flow_ratio changes commanded E/material diagnostics;
- it does not directly change the ideal geometric envelope;
- ZAA local geometry ratio does change nominal local envelope.

## Gate F — Surface-band geometry

Analytic tests:
- mesh section is material boundary, not centerline;
- inward centerline layout;
- multiple same-Z paths;
- multiple different-Z paths;
- shallow terrace coverage;
- local support height;
- candidate segment-local flow;
- nested-section acceptance;
- outward-expanding/unsupported rejection;
- path crossing/nozzle-clearance rejection.

## Gate G — Error and optimizer

Models:
- fixed slopes 1°, 5°, 10°, 15°, 20°, 25°, 30°;
- continuous ~1°–30° curve;
- synthetic curved/nested surface bands.

Verify:
- E_max / E_rms / E_p95 / signed bias;
- combined structural + candidate envelope;
- overbuild rejection;
- deterministic candidate selection;
- cost tie determinism;
- infeasible result rather than unsafe fallback;
- cancellation polling.

## Gate H — Plan/config/preview

Check:
- ExecutionConfigFingerprint same-config equality;
- every required safety semantic mismatch rejects injection;
- missing required semantic rejects injection;
- plan schema contains segment-local geometric/commanded flow but no authoritative final E;
- preview hash equals injector plan hash;
- preview reads separate status;
- preview cannot mutate/reoptimize plan;
- compatibility gate reasons displayed.

## Gate I — Golden Bambu fixture acquisition

Before parser/emitter implementation is considered printable, record exact:
- Orca release/commit;
- plugin API compatibility descriptor;
- Bambu machine/process/filament profile files;
- effective resolved config;
- G-code fixture.

Verify fixture assumptions:
- one object/one total instance/one ModelPart;
- relative E;
- firmware retract off;
- restart-extra zero;
- positive layer-change retraction state;
- arc fitting off;
- line numbers off;
- adaptive PA off;
- role-change custom G-code empty;
- spiral/ironing/scarf/support/raft off;
- verbose G-code/comments on;
- no classic post_process;
- no other slicing-pipeline plugin;
- motion-neutral supported layer-change custom G-code;
- normal print, not calibration mode;
- positive Z hop;
- printable-height margin.

A standard Bambu profile with arc fitting still enabled must be proven analysis-only by a gate test.

## Gate J — Streaming parser state

Read-only, no writes.

Track and verify:
- actual XYZ;
- G90/G91;
- M82/M83;
- active tool;
- relative-E moves;
- feed;
- retraction debt/state;
- supported acceleration/modal state;
- layer tags/markers;
- comments/role evidence;
- plugin markers.

Cases:
- normal layer-change retract;
- filament retraction override;
- wipe-enabled source;
- no-retract/ambiguous state rejection;
- unknown critical command rejection;
- calibration block rejection.

## Gate K — Seam-invariant structural matcher

Check:
- cyclic start change;
- seam split;
- Orca-resolved nonzero seam gap;
- collinear subdivision;
- final coordinate translation;
- geometry tolerance;
- incorrect loop rejection;
- two plausible loop matches => ambiguous skip;
- comments absent from core geometry evidence.

No raw ordered-loop hash may be required.

## Gate L — Execution-frame mapping

Fixtures:
- non-zero instance translation;
- synthetic/non-zero extruder XY offset;
- non-zero Z offset;
- multiple non-collinear anchors.

Verify:
- one constant ((dx,dy,dz));
- translation-only acceptance;
- rotation/scale/shear/non-constant mismatch rejection;
- plan coordinates unchanged;
- only G-code adapter applies mapping.

## Gate M — Orca quantization parity

Check:
- XYZ/F 3-decimal parity;
- E 5-decimal parity;
- positive and negative midpoint ties;
- C++ std::round-compatible half-away-from-zero;
- no Python bankers-rounding leakage;
- pre-valid/post-invalid candidate rejection;
- final E recomputed from quantized XYZ segment length.

## Gate N — E and speed derivation

For quantized segment:
- emitted 3D length;
- commanded mm³/mm;
- filament area;
- quantized E.

Verify:
- flow ratios and role factor;
- max-volumetric-speed limit;
- outer-wall speed limit;
- optional lower plugin cap;
- missing/non-positive limits reject.

## Gate O — Retraction controller

Verify:
- saved retracted amount reconstruction;
- no extra retract before first safe travel;
- exact temporary unretract;
- candidate extrusion;
- exact re-retract;
- final retraction equality;
- restart-extra nonzero rejection;
- firmware-retract rejection;
- ambiguous state rejection.

## Gate P — Safe-ceiling motion and state restoration

Verify:
- actual emitted pre-insertion Z may differ from nominal upper layer;
- vertical raise before any XY;
- no non-extruding XY below Zsafe;
- vertical descend at destination;
- Zsafe uses positive active Z hop;
- printable-height overflow rejects;
- travel feed rates use resolved profile values;
- final X/Y/Z/feed/modal/retraction state equals saved actual emitted state;
- original deferred Orca Z behavior remains untouched.

## Gate Q — Advanced-feature rejection

Fixtures reject:
- adaptive pressure advance;
- non-empty role-change custom G-code;
- calibration/tower modes;
- arc fitting;
- line-number/checksum;
- unsupported tool/multifilament;
- unsupported classic postprocess/other slicing pipeline;
- unsupported support/bridge/scarf/spiral/ironing combinations.

Static PA may remain and must be preserved unchanged.

## Gate R — PluginResult policy

Integration tests:
- expected unsupported/config mismatch -> Skipped;
- plan missing/ambiguous -> Skipped;
- parser/matcher/frame/retraction validation -> Skipped;
- successful injection -> Success;
- validated already-injected -> Success/no duplicate;
- unexpected exception before mutation with original intact -> Skipped + failure status;
- cannot guarantee working-file integrity -> FatalError.

Verify valid original export is not destroyed by expected plugin rejection.

## Gate S — Streaming atomic injector

Three-pass test:
1. validation;
2. temp emission;
3. sanity scan.

Check:
- bounded memory on large generated fixture;
- original unchanged on every failure;
- temp cleanup;
- markers/hash/count;
- state restoration;
- atomic replace only after sanity;
- repeated export/upload working copies;
- no duplicate injection.

## Gate T — Package/runtime

Check:
- target embedded Python version;
- NumPy availability/version;
- wheel metadata;
- clean install/load;
- both SlicingPipeline and Script capability registration;
- unsupported runtime fails clearly.

## Gate U — Primary implementation review

Review:
- final diff;
- affected execution paths;
- specification/ADR compliance;
- source/profile compatibility;
- tests/gates;
- residual gaps.

All findings receive dispositions.

## Gate V — Independent blind review

Before first physical injection:
- independent reviewer receives specification/source/diff but not primary findings;
- review follows `docs/REVIEW_PROCESS.md`;
- reconciliation happens only after blind report completion;
- no unresolved Critical/High finding remains.

## Gate W — First physical coupon

Only after A–V PASS for the exact fixture.

Sequence:
1. simple 5° nested coupon;
2. 10° / 20°;
3. smooth 1°–30° coupon.

Inspect:
- nozzle contact;
- stringing/retraction;
- overbuild/underfill;
- bonding;
- dimensional bias;
- surface roughness;
- unexpected machine motion.

Any unsafe/unexplained behavior pauses physical testing and returns to model/spec adjudication.

## Gate X — Comparative benchmark

Compare:
- normal layer;
- fine conventional layer;
- ZAA-only;
- ZAA + Adaptive Sub-Edge.

Report:
- E metrics;
- measured surface roughness where available;
- material;
- print time;
- failure/artifact modes.

Do not claim superiority outside measured geometry/profile classes.

## Compatibility expansion rule

Every newly supported:
- Orca version;
- printer/process/filament family;
- G-code mode;
- object topology;
- support/overhang class;
- E mode;
- PA/role behavior;
- firmware/tool architecture;

requires:
- explicit fixture;
- focused compatibility tests;
- full relevant regression gates;
- ADR if a safety/architecture contract changes.
