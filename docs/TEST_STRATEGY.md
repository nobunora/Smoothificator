# Test Strategy and Release Gates

Tests are organized by ownership boundary so failures identify the responsible component.

Apply docs/QUALITY_GATES.md before broad behavioral suites.

Physical printing is forbidden until every preceding software, fixture, and review gate required by this document passes for the exact target compatibility descriptor.

## Gate A — Governance and architecture

Check:
- ADR identifiers unique;
- superseded ADR status/reference consistency;
- handoff/canonical revision present;
- forbidden imports;
- no live Orca types in domain/engine;
- G-code adapter does not import optimizer/source-mesh modules;
- UI does not import optimizer/live Orca;
- one config-resolution owner;
- one Orca-quantizer owner;
- no generic utility dumping ground.

## Gate B — Domain determinism

Check:
- frozen DTOs;
- schema versioning;
- canonical serializer;
- deterministic plan hash;
- timestamp/runtime ObjectID/machine translation/final E excluded from plan hash;
- PlanExecutionStatus separate from plan;
- deterministic ExecutionConfigFingerprint;
- deterministic PluginSettingsFingerprint;
- ToolClearanceProfile canonicalization/versioning.

## Gate C — Source mesh and centered-frame adapter

Pinned Orca/source fixtures verify:
- one total source instance accepted;
- multiple total instances rejected for injection;
- one ModelPart volume;
- finite vertices/indices;
- manifold gate;
- globally reversed mesh handling;
- locally inconsistent winding rejection;
- mirrored-transform material-side parity;
- inside/outside material-side checks;
- non-degenerate transformed bounds;
- translated instance;
- rotated instance;
- scaled instance;
- shrink-compensated PrintObject transform;
- mirrored case if supported;
- centered-frame parity;
- ambiguous/open candidate section rejection;
- no live/zero-copy reference escape.

## Gate D — Orca ZAA parity

Verify:
- relative path Z -> absolute centered-slice Z;
- local effective height;
- local ZAA geometry-directed volume ratio;
- non-ZAA planar identity;
- invalid effective height rejection;
- ZAA enabled/disabled posSimplifyPath behavior.

## Gate E — Flow semantics

Geometric model:
- rounded-rectangle formula;
- invalid width/height;
- geometric envelope independent from global calibration ratios.

Commanded model:
- print_flow_ratio;
- filament_flow_ratio;
- set_other_flow_ratios on/off;
- outer_wall_flow_ratio;
- filament cross-section conversion.

Separation:
- changing filament_flow_ratio changes commanded E/material diagnostics;
- it does not directly change nominal geometric bead envelope;
- ZAA local height/volume behavior does change the nominal local envelope.

## Gate F — Surface-band and candidate topology

Check:
- mesh section is boundary, not centerline;
- inward/material-side centerline placement;
- multiple same-Z paths;
- multiple different-Z paths;
- every v1 SubEdgePath has constant command Z;
- varying-Z candidate construction rejected;
- segment-local support/effective height;
- nested/self-supported acceptance;
- outward-expanding unsupported rejection;
- candidate crossing/nozzle-clearance rejection.

## Gate G — Candidate seam/gap

Check:
- deterministic seam selection;
- cyclic/reversed closed-loop input gives same canonical result;
- candidate seam/gap stored in plan;
- finite-bead scoring includes gap;
- preview shows exact gap;
- translation does not change seam choice;
- invalid short-loop gap rejects candidate;
- postprocessor cannot change seam/gap.

## Gate H — Error and optimizer

Analytic geometry:
- fixed slopes 1, 5, 10, 15, 20, 25, 30 degrees;
- continuous approximately 1–30 degree surface;
- shallow terraces requiring multiple paths;
- synthetic varying-support surface.

Verify:
- E_max / E_rms / E_p95 / signed bias;
- combined structural + candidate nominal envelope;
- overbuild rejection;
- deterministic candidate selection;
- deterministic ties;
- infeasible result rather than unsafe fallback;
- cancellation polling.

## Gate I — Plan / config / preview

Check:
- both fingerprints stored in plan;
- same plugin settings/config accepted;
- tolerance/min-height/seam-gap/speed-cap/ToolClearanceProfile changes reject;
- every required Orca safety-semantic change rejects;
- missing required value rejects;
- plan segment has geometric/commanded flow but no final E;
- preview plan hash equals injector plan hash;
- preview status separate from plan;
- preview cannot reoptimize/mutate;
- compatibility gate reasons visible.

## Gate J — Golden Bambu fixture acquisition

Record exact:
- Orca version/commit;
- plugin compatibility descriptor;
- machine/process/filament profiles;
- resolved semantic config;
- plugin settings;
- ToolClearanceProfile id/version/evidence;
- source G-code.

Verify fixture:
- one object / one total instance / one ModelPart;
- not first-layer target;
- relative E;
- firmware retract off;
- restart extra zero;
- positive unambiguous anchor retraction;
- arc fitting off;
- line numbers off;
- adaptive PA off;
- filament adaptive volumetric speed off;
- fuzzy skin off;
- role-change custom G-code empty;
- spiral/ironing/scarf/support/raft off;
- verbose comments on;
- no classic post_process;
- no other slicing-pipeline capability;
- supported motion-neutral layer-change custom G-code;
- normal non-calibration print;
- positive Z hop;
- printable-height margin.

A standard Bambu profile with arc fitting still enabled must be proven analysis-only.

## Gate K — Streaming parser state

Read-only, no writes.

Track:
- actual XYZ;
- G90/G91;
- M82/M83;
- active tool;
- relative-E moves;
- feed;
- retraction state;
- supported acceleration/modal state;
- layer/reserved markers;
- comment/type evidence;
- plugin markers.

Cases:
- normal layer-change retract;
- filament retraction override;
- wipe-enabled source;
- no-retract/ambiguous state reject;
- unknown critical command reject;
- calibration block reject.

## Gate L — Seam-invariant structural matcher

Check:
- cyclic start;
- seam split;
- nonzero Orca seam gap;
- collinear subdivision;
- final translation;
- quantization tolerance;
- incorrect loop reject;
- ambiguous multiple loops -> Skipped;
- comments are supporting, not sole, evidence.

No raw ordered-loop hash dependency.

## Gate M — Execution-frame mapping

Fixtures:
- nonzero instance translation;
- nonzero/synthetic extruder XY offset;
- nonzero Z offset;
- multiple non-collinear references.

Verify:
- one constant dx/dy/dz;
- translation-only acceptance;
- rotation/scale/shear/non-constant reject;
- immutable plan coordinates unchanged;
- only G-code adapter applies mapping.

## Gate N — Orca quantization parity

Check:
- XYZ/F 3-decimal parity;
- E 5-decimal parity;
- positive/negative midpoint ties;
- half-away-from-zero;
- no Python bankers-rounding leakage;
- post-quantization validity rerun;
- short-segment emitted length changes;
- final E derived after quantized XYZ.

## Gate O — E and speed derivation

For quantized segment verify:
- emitted 3D length;
- commanded mm3/mm;
- filament area;
- quantized relative E;
- max-volumetric-speed cap uses commanded mm3/mm;
- outer-wall speed cap;
- optional plugin cap;
- fixture-required matched-wall feed cap;
- missing/non-positive bound rejects.

## Gate P — Retraction controller

Verify:
- saved retracted amount reconstruction;
- no blind extra retract;
- exact temporary unretract;
- candidate extrusion;
- exact re-retract;
- final retraction equality;
- restart-extra nonzero reject;
- firmware-retract reject;
- ambiguous state reject.

## Gate Q — Safe-ceiling and actual-state restoration

Verify:
- insertion physical Z may differ from nominal layer Z;
- vertical raise before any XY;
- no plugin non-extruding XY below Zsafe;
- vertical descend at destination;
- positive active Z hop required;
- printable-height overflow reject;
- resolved travel feeds;
- final actual XYZ/feed/modal/retraction equality;
- original deferred Orca layer-Z behavior remains untouched.

## Gate R — Chronological plugin + downstream tool clearance

Using quantized plugin motion, parsed original motion, chronological material state, and ToolClearanceProfile verify:
- plugin safe vertical descent;
- plugin descent/body-envelope collision -> reject;
- plugin candidate-extrusion body collision -> reject;
- later plugin candidate colliding with earlier candidate material -> reject;
- intentional deposition/support contact does not self-reject;
- future material is not treated as already printed;
- safe upper structural motion;
- low-Z ZAA extrusion collision -> reject;
- original low-Z travel collision -> reject;
- spatially distant low-Z motion accepted;
- pure Z safe motion;
- near miss inside safety margin -> reject;
- missing ToolClearanceProfile -> physical gate disabled;
- unsupported arc/unknown motion in validation horizon -> reject;
- horizon extends beyond immediate upper layer when needed;
- full-remaining-file fallback;
- broad-phase and exact check deterministic parity.

## Gate S — Advanced-feature rejection

Fixtures reject:
- first-layer target;
- fuzzy skin;
- filament adaptive volumetric speed;
- adaptive PA;
- non-empty role-change custom G-code;
- calibration/tower mode;
- arc fitting;
- line-number/checksum;
- unsupported tool/multifilament;
- unsupported classic postprocess/other slicing pipeline;
- unsupported support/bridge/scarf/spiral/ironing.

Static PA may remain and must be preserved unchanged.

## Gate T — PluginResult policy

Integration:
- expected unsupported/config mismatch -> Skipped;
- plan missing/ambiguous -> Skipped;
- parser/matcher/frame/retraction/final-tool-clearance validation -> Skipped;
- successful injection -> Success;
- validated already-injected -> Success/no duplicate;
- unexpected exception before mutation with original intact -> Skipped + failure status;
- file integrity uncertain -> FatalError.

Expected plugin rejection must not destroy valid original export.

## Gate U — Binary byte-preserving streaming atomic injector

Three passes:
1. validation;
2. temp emission;
3. sanity scan.

Check:
- bounded memory on large fixture;
- binary-line parsing/emission;
- LF/CRLF preservation;
- no-final-newline preservation;
- opaque non-ASCII comment bytes preserved;
- unsupported non-ASCII command token rejected;
- original byte-for-byte unchanged on every failure;
- temp cleanup;
- marker/hash/count;
- state restoration;
- chronological tool-clearance decision preserved;
- atomic replace only after sanity;
- repeated export/upload working copies;
- no duplicate injection.

## Gate V — Package/runtime

Check:
- embedded Python version;
- NumPy availability/version;
- wheel metadata;
- clean install/load;
- SlicingPipeline + Script capability registration;
- current capability get_config available at postprocess;
- unsupported runtime fails clearly.

## Gate W — Primary implementation review

Review:
- final diff;
- affected execution paths;
- specification/ADR compliance;
- source/profile compatibility;
- tests/gates;
- residual gaps.

Every finding gets a disposition.

## Gate X — Independent blind review

Before first physical injection:
- reviewer receives authoritative spec/source/diff, not primary findings;
- follow REVIEW_PROCESS;
- reconcile only after blind report completion;
- no unresolved Critical/High finding.

ToolClearanceProfile evidence must be included.

## Gate Y — First physical coupon

Only after A–X PASS for the exact fixture.

Sequence:
1. conservative 5-degree nested coupon;
2. 10/20-degree coupons;
3. smooth 1–30-degree coupon;
4. deliberate conservative near-clearance coupon.

Inspect:
- nozzle/hotend clearance;
- unexpected machine motion;
- stringing/retraction;
- overbuild/underfill;
- bonding;
- dimensional bias;
- surface roughness.

Any unsafe/unexplained behavior returns to model/spec adjudication.

## Gate Z — Comparative benchmark

Compare:
- normal layer;
- fine conventional layer;
- ZAA-only;
- ZAA + Adaptive Sub-Edge.

Report:
- E metrics;
- roughness where measured;
- geometric and commanded added material;
- print time;
- failure/artifact modes.

Do not generalize beyond measured geometry/profile/hardware classes.

## Compatibility expansion rule

Every newly supported Orca version, printer/profile, G-code mode, object topology, hardware keep-out profile, support class, E mode, PA/role behavior, firmware, or tool architecture requires:
- explicit fixture;
- focused compatibility tests;
- relevant full regression gates;
- ADR when a safety/architecture contract changes.
