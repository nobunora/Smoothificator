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
- SHA-256 full authoritative identity;
- canonical float +0/-0 equivalence;
- NaN/Inf serialization rejection;
- mapping-order independence;
- ndarray memory-layout independence with shape/dtype distinction;
- timestamp/runtime ObjectID/machine translation/final E excluded from plan hash;
- PlanExecutionStatus separate from plan;
- deterministic ExecutionConfigFingerprint;
- deterministic PluginSettingsFingerprint;
- ToolClearanceProfile canonicalization/versioning;
- canonical SHA-256 serializer/hash golden vectors;
- mapping-order independence;
- +0/-0 normalization and NaN/Inf rejection;
- array shape/dtype/logical-order identity rules.

## Gate C — Source mesh and centered-frame adapter

Pinned Orca/source fixtures verify:
- one total source instance accepted;
- multiple total instances rejected for injection;
- one ModelPart volume;
- exactly one connected closed shell;
- simple target sections with no hole/disconnected/branched/self-intersection;
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

Compatibility:
- all mixed-filament virtual-slot flags false accepted;
- mixed virtual filament / sublayer / gradient execution rejected;
- mixed-setting change invalidates ExecutionConfigFingerprint.

Compatibility gate:
- all mixed-filament virtual-slot flags false accepted;
- mixed filament / mixed sublayer / gradient execution rejected;
- mixed setting changes invalidate ExecutionConfigFingerprint.

Geometric model:
- rounded-rectangle formula;
- width == height accepted;
- width < height rejected;
- configured min/max width rejected outside bounds;
- configured min/max height rejected outside bounds;
- invalid/NaN/Inf width/height/flow rejected;
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

## Gate E2 — Source-target modifier gates

Check:
- xy_contour_compensation nonzero -> reject;
- xy_hole_compensation nonzero -> reject for first fixture;
- unsupported slicing/closing mode -> reject;
- make_overhang_printable active -> reject;
- target interval inside elephant-foot compensated layers -> reject;
- interval above all affected layers may proceed;
- relevant modifier change invalidates ExecutionConfigFingerprint.

## Gate F — Surface-band and candidate topology

Check:
- mesh section is boundary, not centerline;
- exact source-vertex Z candidate forbidden;
- horizontal-facet Z candidate forbidden;
- endpoint dedup/join deterministic;
- open/branched/self-intersecting section rejected;
- triangle-order permutation invariance;
- inward/material-side centerline placement;
- multiple same-Z paths;
- multiple different-Z paths;
- every v1 SubEdgePath has constant command Z;
- varying-Z candidate construction rejected;
- segment-local support/effective height;
- nested/self-supported acceptance;
- outward-expanding unsupported rejection;
- candidate crossing/nozzle-clearance rejection.

## Gate F2 — NominalBeadSolidV1

Check:
- stadium cross-section area parity;
- ZAA effective width reconstructed from local q_geom/h;
- candidate top/bottom Z placement;
- adjacent segment solid union;
- flat open-path axial caps;
- internal overlap surfaces excluded from exposed envelope;
- deterministic geometry under equivalent path canonicalization.

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

## Gate H — Bidirectional converged error estimator and optimizer

Analytic geometry:
- fixed slopes 1, 5, 10, 15, 20, 25, 30 degrees;
- continuous approximately 1–30 degree surface;
- shallow terraces requiring multiple paths;
- synthetic varying-support surface.

Verify:
- deterministic initial sample spacing;
- refinement discovers a feature missed by coarse sampling;
- convergence of every hard metric;
- max-refinement non-convergence => infeasible;
- estimator settings fingerprint changes;
- predicted->source max/RMS/p95;
- source->predicted max/RMS/p95;
- completely missing target patch rejected by source->predicted;
- external overbuild rejected by predicted->source;
- public bidirectional E_max/E_p95/E_rms aggregation;
- thin-wall opposite-face correspondence trap rejected;
- normal-incompatible closest point rejected;
- no-correspondence sample rejected;
- unequal directional sample counts do not implicitly reweight E_rms;
- signed bias diagnostic;
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

## Gate K — Streaming parser and modal state

Read-only, no writes.

Track and verify:
- actual XYZ;
- units G20/G21;
- G90/G91;
- M82/M83;
- M200 volumetric-E state where relevant;
- M220 speed factor;
- M221 flow factor;
- G92 XYZ origin state;
- logical E coordinate separately from physical retraction debt;
- active tool;
- feed;
- retraction state;
- supported acceleration/modal state;
- layer/reserved markers;
- comment/type evidence;
- plugin markers.

Cases:
- G21/G90/M83 accepted;
- G20 reject;
- G91 anchor reject;
- M82 anchor reject;
- M200 active reject;
- M220 != 100 reject;
- M221 != 100 reject;
- physical-run instruction records live printer speed/flow override must remain 100%;
- G92 E does not clear retraction debt;
- G92 XYZ target-context reject;
- feed restore equality;
- normal layer-change retract;
- filament retraction override;
- wipe-enabled source;
- no-retract/ambiguous state reject;
- unknown critical command reject;
- calibration block reject.

## Gate K2 — Final structural deposition parity

After final structural matching verify:
- lower-wall seam gap can remove required support -> reject;
- candidate far from seam remains valid;
- upper-wall final seam/quantization changes hard local error -> revalidate;
- nearby inner/perimeter positive-E material participates in support/collision context;
- final actual wall feed is a mandatory speed cap;
- no representative final wall feed -> reject.


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
- final E derived after quantized XYZ;
- quantized segment collapsed to zero XYZ length -> reject;
- nonzero path with quantized E=0 when material intent is nonzero -> reject.

## Gate O — E / speed / acceleration derivation

For quantized segment verify:
- emitted 3D length;
- commanded mm3/mm;
- filament area;
- quantized relative E;
- max-volumetric-speed cap uses commanded mm3/mm;
- outer-wall speed cap;
- optional plugin cap;
- final matched-wall feed is always an upper bound;
- configured external-wall speed is an upper bound;
- missing/non-positive speed/volumetric bound rejects;
- extrusion-rate smoothing slope = 0 accepted;
- positive extrusion-rate smoothing slope rejected;
- known conservative inherited acceleration accepted;
- high inherited acceleration rejected;
- known conservative classic jerk accepted;
- high inherited jerk rejected;
- unsupported/unknown cornering semantics rejected;
- known conservative classic XY jerk accepted;
- high inherited jerk rejected;
- unknown/junction-deviation or otherwise unsupported cornering state rejected;
- unknown/non-finite acceleration rejected;
- max_subedge_acceleration settings fingerprint changes deterministically;
- max_subedge_jerk settings fingerprint changes deterministically;
- max_subedge_jerk settings fingerprint changes deterministically;
- plugin block leaves acceleration and jerk/cornering state unchanged.

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

## Gate S — Advanced-feature and dynamic-runtime rejection

Fixtures reject:
- first-layer target;
- disconnected-shell / hole / multi-loop target topology;
- fuzzy skin;
- filament adaptive volumetric speed;
- adaptive PA;
- non-empty role-change custom G-code;
- calibration/tower mode;
- smooth timelapse;
- farthest_point_timelapse;
- wrapping detection;
- generated prime/wipe tower;
- exclude_object;
- unknown traditional timelapse motion/state;
- arc fitting;
- line-number/checksum;
- unsupported tool/multifilament;
- unsupported classic postprocess/other slicing pipeline;
- unsupported support/bridge/scarf/spiral/ironing.

Traditional timelapse is accepted only through an exact parser-supported fixture.
gcode_label_objects alone may remain enabled.
Static PA may remain and must be preserved unchanged.

## Gate S2 — Attempt state and TOCTOU

Verify:
- no partially constructed plan is visible;
- plan publication is atomic;
- each postprocess invocation gets a unique InjectionAttemptId;
- simultaneous attempts on separate working files keep independent records;
- attempt state transitions are monotonic;
- newer analysis generation during an old matching export does not silently swap the selected immutable plan;
- plugin settings change before commit -> abort/Skipped;
- source working file changed between Pass 1 and Pass 2 -> abort;
- source metadata/identity changed immediately before replace -> abort;
- Pass-1 and Pass-2 source digests match for successful attempt.


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

## Gate V2 — Estimate/progress labeling

Check:
- standard Orca preview/time/material remains explicitly labeled pre-postprocess;
- plugin added path/material/time delta is deterministic;
- M73/progress metadata is not silently claimed to be corrected;
- benchmark/report code does not treat original Orca estimate as final modified-file truth.

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


## Compatibility drift smoke check

Before pinning a new Orca build:
- compare the pinned source family against the previous audited baseline for SlicingPipeline bindings, Print/GCode export paths, formatter constants, profile semantics, and dynamic feature generation;
- rerun the relevant source-parity fixtures;
- never infer compatibility from version numbering alone.

The 2026-10-02 audit found PluginHost/SlicingPipeline bindings stable while GCode.cpp/Print.cpp and profiles continued to evolve, validating this requirement.
