# Adaptive Sub-Edge Surface Reconstruction — System Specification

## 1. Goal

Adaptive Sub-Edge is a stock-OrcaSlicer Python plugin that improves FDM outer-surface fidelity where Orca normal slicing and Z Anti-Aliasing (ZAA / Z Contouring) still leave residual geometric error above a requested tolerance.

v1 MUST NOT require a custom Orca build.

The system:
1. lets Orca finish normal slicing, ZAA when applicable, and path simplification;
2. reads the final simplified structural paths;
3. reconstructs the same centered source-model frame Orca sliced;
4. predicts the nominal finite-bead surface already produced by Orca;
5. finds residual printable surface bands;
6. plans additional constant-Z SubEdge paths;
7. previews that exact immutable plan;
8. injects that exact plan into the exported working G-code only after final configuration, coordinate, machine-state, quantization, motion, and collision validation.

The original Orca structural extrusion remains unchanged in printable v1.

## 2. Canonical pipeline

Orca slice
-> ZAA / normal path generation
-> path simplification
-> posSimplifyPath
   -> copy/normalize Orca geometry
   -> reconstruct centered source mesh
   -> normalize ZAA local Z / geometry-directed volume
   -> build structural finite-bead baseline
   -> residual error / surface-band analysis
   -> deterministic candidate seam/gap
   -> immutable SubEdgePlan
      -> plugin preview
-> normal Orca G-code generation
-> psGCodePostProcess
   -> plugin settings fingerprint check
   -> Orca execution config fingerprint check
   -> streaming G-code parse
   -> actual emitted machine-state reconstruction
   -> seam-invariant structural matching
   -> execution-frame translation
   -> Orca-compatible quantization
   -> final E/speed/travel derivation
   -> downstream-original-motion clearance validation
   -> temp-file emission
   -> sanity validation
   -> atomic replace
-> file / printer

## 3. Single source of truth

The exact same immutable SubEdgePlan drives:
- preview;
- predicted metrics;
- final G-code injection.

The injector MUST NOT:
- rerun the optimizer;
- move or re-seam a candidate;
- change candidate geometric or commanded flow intent;
- infer replacement geometry from G-code;
- silently alter the plan to make it executable.

Execution status is separate from the plan.

## 4. Printable v1 source geometry

Printable v1 requires:
- exactly one PrintObject;
- exactly one total source ModelInstance;
- exactly one positive ModelPart volume;
- no NegativeVolume, ParameterModifier, or equivalent CSG/helper volume;
- non-empty finite vertices/triangles;
- valid triangle indices;
- current bound ModelVolume reports manifold;
- shared-edge winding/material orientation can be validated consistently;
- global outward/material side can be determined deterministically, including mirrored transforms;
- non-degenerate transformed bounds;
- every required candidate-Z section used for a printable path has an unambiguous closed material boundary.

The plugin does not create an independent mesh-repair authority. Signed error and material-side insetting use a validated orientation view plus an independent inside/outside check per ADR-0030. Raw source normals are not trusted until orientation/material-side validation passes. Raw source normals are not trusted until orientation/material-side validation passes.

A model Orca can slice may still be analysis-only for this plugin.

## 5. Canonical geometry frame

All domain/engine geometry uses Orca centered PrintObject slice-space in millimeters.

The adapter reconstructs the centered frame defined by ADR-0012.

A direct PrintObject.trafo() @ ModelVolume.matrix() transform is insufficient because Orca slices with its centered PrintObject transform.

No plan is injectable until centered-frame parity is verified against PrintObject/sliced path geometry.

## 6. ZAA baseline semantics

The analyzer reads final simplified paths at posSimplifyPath.

For a Z-contoured path point with relative Z offset d:

Z_abs = layer.print_z + d

after Orca coordinate unscale.

For non-ironing ZAA extrusion, Orca locally changes the geometry-directed path volume using:

zaa_ratio = (path.height + d) / path.height

The nominal baseline model therefore carries:
- absolute local nozzle Z;
- local effective bead height;
- local ZAA geometry-directed volume target.

Global print/material flow calibration ratios are modeled separately from ideal geometry.

If ZAA did not apply, ordinary planar Orca paths form the baseline.

## 7. Boundary versus nozzle centerline

A source mesh-plane intersection is a target material boundary.

It is NOT automatically a nozzle centerline.

The engine:
1. derives a residual surface band;
2. determines the material side;
3. places one or more candidate centerlines inside that material;
4. scores the finite-bead envelope against the target boundary.

No fixed half-width inset is assumed universally correct.

## 8. Printable v1 SubEdge path topology

Each printable v1 SubEdgePath:
- is an explicit open execution path;
- has one immutable constant command_z_mm;
- contains ordered SubEdgeSegments;
- may have segment-local support height and effective bead height.

Different SubEdgePaths may:
- share one command Z;
- use independently optimized different command Z values.

Continuously varying-Z candidate paths are out of scope for v1.

## 9. Candidate seam and gap

A closed source candidate contour is converted into an explicit open execution path before the immutable plan is finalized.

The engine deterministically:
- canonicalizes orientation;
- selects candidate seam/start using a versioned geometry rule;
- applies an explicit candidate gap from validated plugin settings;
- includes that gap in finite-bead scoring and preview.

The postprocessor MUST NOT change candidate seam/gap.

Candidate seam/gap participates in PluginSettingsFingerprint and plan hash.

## 10. Effective bead-height rule

Initial 0.4 mm-nozzle research uses:

h_min_mm = 0.08

as a configurable/calibratable minimum effective deposited bead height above local support.

For candidate segment j:

h_eff_j = nozzle_z_j - support_z_j

This is NOT a minimum pairwise Z difference between neighboring candidate paths.

Pairwise feasibility depends on:
- finite bead overlap;
- local support;
- nozzle/tool clearance;
- path crossing;
- final G-code quantization.

## 11. Segment-local candidate extrusion

SubEdgeSegment stores:
- high-precision print-space start/end XY;
- parent constant command Z;
- local support Z;
- effective bead height;
- nominal width;
- geometric mm3/mm;
- commanded mm3/mm;
- speed-limit metadata;
- support/validation metadata.

It does NOT store authoritative final machine XYZ or final emitted E.

A path-wide constant flow MUST NOT hide local support-height variation.

## 12. Geometric bead model

For a supported non-bridge candidate with effective bead height h and nominal width w:

q_geom = h * (w - h * (1 - pi/4))

This is the nominal geometric line volume used for surface prediction.

## 13. Geometric versus commanded volume

v1 distinguishes:

### Geometric volume
Used for ideal finite-bead surface prediction.

### Commanded volume
Used for E generation and volumetric-speed limits.

For external-surface candidate segments in the audited Orca semantics:

q_cmd = q_geom * print_flow_ratio * filament_flow_ratio * outer_role_factor

outer_role_factor = outer_wall_flow_ratio when set_other_flow_ratios is enabled, otherwise 1.

### Empirical physical volume
Not yet modeled from first principles.

A calibration value such as filament_flow_ratio = 0.98 MUST NOT automatically be interpreted as exactly 2% smaller physical bead geometry.

Physical bead calibration is a later phase.

## 14. Final combined nominal surface

Candidate quality is evaluated from the combined nominal finite-bead envelope of:
- lower existing structural/ZAA beads;
- candidate SubEdge beads;
- upper existing structural/ZAA beads.

v1 does NOT rewrite the original structural outer wall.

A candidate that improves one area but creates unacceptable overbuild elsewhere is infeasible.

## 15. Printable geometric domain

Printable v1 requires nested/self-supported top-facing geometry.

Reject printable candidates for:
- first-layer refinement;
- outward-expanding unsupported/overhang bands;
- support-dependent targets;
- bridge target extrusion;
- fuzzy-skin target geometry;
- invalid or ambiguous mesh sections;
- unresolved local support;
- candidate crossing;
- unresolved nozzle/tool clearance.

Analysis may still describe why such a region is non-injectable.

## 16. Optimization target

Primary quality target where feasible:

E_max <= configured_tolerance

Required error metrics:
- E_max;
- E_rms;
- E_p95;
- signed mean/bias.

Among feasible candidate sets minimize a documented cost including:
- residual error;
- candidate path length;
- added commanded material;
- estimated time;
- complexity/risk.

Optimization MUST be deterministic for identical canonical inputs/settings.

## 17. Plugin-owned settings identity

Planning builds a versioned PluginSettingsFingerprint from all plugin settings that can affect:
- geometry;
- candidate seam/gap;
- minimum bead height;
- cost/optimization;
- ToolClearanceProfile;
- safety margins;
- candidate speed cap;
- execution policy.

At psGCodePostProcess, current plugin settings are re-read through the capability config contract and fingerprinted again.

Mismatch or missing/invalid settings => Skipped.

PlanStore invalidation is helpful but does not replace this final equality check.

## 18. Orca execution configuration identity

Planning also builds a versioned ExecutionConfigFingerprint from resolved Orca semantics.

At psGCodePostProcess it is recomputed using ctx.config_value().

The fingerprint includes every supported semantic that can affect:
- centered geometry/frame identity;
- ZAA behavior;
- seam matching;
- flow/E conversion;
- retraction;
- motion/speed/Zsafe;
- printable machine height;
- custom layer/role G-code;
- printable feature gates.

Fingerprint equality does not replace actual final-G-code parsing.

## 19. Preview contract

Orca standard G-code preview shows pre-postprocess output.

Plugin preview displays the exact immutable plan:
- structural/ZAA baseline;
- target surface boundary;
- candidate open paths and seam gaps;
- segment-local effective height;
- geometric versus commanded flow;
- support/nesting;
- error metrics;
- compatibility gates;
- plan hash;
- runtime execution status.

Preview MUST NOT reoptimize or mutate the plan.

## 20. Thread/lifetime contract

SlicingPipeline geometry callbacks run in Orca slicing workflow thread.

No orca.host.ui calls are allowed there.

Live Orca/pybind objects and Orca-backed zero-copy arrays MUST NOT survive execute(ctx).

The adapter copies/normalizes all required data before returning.

## 21. Final structural matching

Final G-code is not expected to preserve raw ordered posSimplifyPath points.

Matcher supports normal Orca transformations:
- cyclic seam start;
- seam split;
- collinear subdivision;
- one contiguous configured seam-gap clip;
- final translation/quantization.

Raw ordered-loop equality is forbidden as the sole identity check.

Scarf/sloped seams and arc-fitted target geometry are unsupported for injectable v1.

Exactly one plan/structural reference must match.

Zero or multiple matches => Skipped.

## 22. Print-space to machine-G-code frame

Plan coordinates MUST NOT be emitted directly.

After unique structural matching:
1. derive a constant translation (dx, dy, dz) from multiple non-collinear reference points/segments;
2. require consistency within a pinned tolerance;
3. reject rotation, scale, shear, or non-constant mapping;
4. apply translation only in the G-code adapter.

## 23. Orca-compatible quantization

For the audited Orca source family:
- XYZ/F precision: 3 decimals;
- E precision: 5 decimals;
- midpoint rounding matches C++ std::round, half away from zero.

Do not use Python built-in round as an Orca-parity implementation.

After translation and XYZ quantization, execution-sensitive geometry is revalidated.

Unknown formatter behavior for a new Orca version => no injection.

## 24. Final E derivation

Final E is NOT stored in the geometry-time plan.

For each candidate segment:
1. apply machine translation;
2. quantize machine XYZ;
3. compute actual emitted segment length from quantized coordinates;
4. use immutable commanded mm3/mm;
5. calculate unquantized relative E from emitted length and filament cross-section;
6. apply Orca-compatible E quantization;
7. revalidate the resulting execution command.

Postprocess derives execution commands deterministically but may not change candidate intent.

## 25. Relative-E / retraction contract

Printable v1 requires:
- relative E;
- firmware retraction disabled;
- unambiguous positive saved retraction at the insertion anchor;
- ordinary restart-extra = 0;
- known effective retract and deretract speeds.

Candidate cycle:
- safe travel while still in saved retracted state;
- unretract exactly the saved amount at candidate start;
- print;
- retract exactly the same amount;
- return to safe travel while retracted.

After all candidates, retraction state equals the original saved state.

The plugin does not emulate the original wipe path for its temporary cycle.

## 26. Actual layer-boundary machine state

A layer-change marker does NOT prove that physical machine Z has already reached the next nominal layer height.

The parser snapshots actual emitted machine state at the insertion point.

After candidate printing, restore the actual saved:
- XYZ;
- feed;
- E/retraction state;
- supported modal state.

Do NOT force nominal upper-layer Z or reproduce Orca deferred layer synchronization.

## 27. Injected safe-ceiling travel

All plugin-generated non-extruding XY travel occurs at machine-space Zsafe.

Initial v1:

Zsafe = max(saved_actual_z, target_upper_machine_z) + active_z_hop

Require:
- active Z hop > 0;
- Zsafe inside active tool printable-height limit;
- vertical raise before XY;
- vertical descend at destination.

Use resolved XY and Z travel-speed semantics from the supported profile.

## 28. Candidate speed / extrusion safety

Printable v1 requires:
- normal non-calibration print;
- one tool / one filament execution context;
- adaptive pressure advance disabled;
- filament adaptive volumetric speed disabled;
- machine/filament/process extrusion-role-change custom G-code empty;
- firmware retraction disabled;
- line numbers/checksums off;
- arc fitting off;
- spiral vase off;
- ironing off for target;
- scarf/sloped seam off;
- support/raft off;
- fuzzy skin off for target;
- no classic post_process script;
- no other slicing-pipeline capability besides this plugin;
- verbose G-code/comments enabled for initial physical fixtures;
- fresh current-session plan.

Static pressure advance may remain enabled and is inherited unchanged.

Candidate segment speed MUST NOT exceed:
- resolved outer-wall speed;
- resolved fixed filament max volumetric speed divided by candidate commanded mm3/mm;
- optional lower plugin cap;
- actual matched structural-wall feed when that feed is lower and the compatibility fixture requires it.

The plugin never silently changes Orca settings.

## 29. Downstream original-motion clearance

Safe injected travel is not enough because later original Orca motion was generated without the added material.

Before any file mutation, validate the quantized machine-space candidate bead envelope against unchanged downstream original G-code.

Use a versioned ToolClearanceProfile that describes a conservative physical nozzle/hotend keep-out envelope and safety margins for the exact hardware fixture.

The profile dimensions require documented manufacturer geometry, measured hardware, or another explicit physical source.

Do NOT infer body clearance from nozzle-orifice diameter alone.

Validate:
- downstream non-extruding travel;
- downstream extrusion, including locally lowered ZAA moves;
- pure Z motion;
- relevant modal/motion commands;
until a conservative safe barrier is proven or the remaining supported motion is fully checked.

Any swept tool keep-out intersection with candidate material, unsupported motion, or uncertain clearance => Skipped.

v1 does NOT rewrite later original Orca travel to make a candidate fit.

## 30. Printable v1 hardware/profile scope

Physical injection is enabled only for an explicitly golden-fixtured Bambu/Orca 0.4 mm single-tool family satisfying every contract above.

No ToolClearanceProfile => analysis/preview only.

No exact Orca/profile fixture => analysis/preview only.

A standard Bambu process with arc fitting still enabled is analysis-only until the user explicitly disables it and that resulting configuration is fixture-validated.

## 31. G-code file mutation

psGCodePostProcess uses binary, byte-preserving, streaming all-or-nothing processing per ADR-0031.

Pass 1:
- validate plugin settings fingerprint;
- validate Orca config fingerprint;
- parse actual state;
- match structural references;
- derive execution frame;
- quantize/derive candidate commands;
- validate retraction, motion, and downstream clearance.

Pass 2:
- stream the original as raw binary lines into a same-directory temp file;
- preserve every untouched original byte and original newline convention;
- inject only fully prevalidated ASCII-compatible blocks at exact anchors.

Pass 3:
- binary-stream sanity-check temp;
- verify markers, order, state restoration, integrity.

Only then atomically replace ctx.gcode_path.

Expected unsupported/validation failure => PluginResult.Skipped and original output unchanged.

Success => successful injection or validated already-injected no-op.

## 32. Failure behavior

Any uncertainty in:
- source mesh validity/orientation/material side;
- centered frame;
- plugin settings identity;
- Orca export config identity;
- structural-loop match;
- machine translation;
- formatter parity;
- actual modal/retraction state;
- flow/speed limits;
- support/collision;
- candidate seam/gap;
- calibration/custom G-code;
- Zsafe;
- downstream original-motion clearance;
- ToolClearanceProfile;
- source orientation/material-side ambiguity;
- unsupported binary/token/newline/filesystem atomic-replace behavior;
causes injection to be skipped.

The project always prefers unchanged valid Orca G-code over guessed modification.

## 33. Non-goals v1

- custom Orca/C++ dependency;
- mutating live Orca perimeters;
- replacing ZAA;
- rewriting original structural extrusion;
- continuously varying-Z added paths;
- multi-object / multi-instance / multi-volume CSG injection;
- multitool/multifilament injection;
- absolute-E injection;
- firmware retract;
- G2/G3 candidate output;
- adaptive-PA emulation;
- adaptive volumetric-speed parity;
- fuzzy-skin correction;
- support/overhang reconstruction;
- first-layer SubEdge refinement;
- calibration-mode injection;
- automatic downstream travel replanning;
- generic collision claims without hardware keep-out evidence;
- claiming Orca standard preview contains postprocessed paths.

## 34. Governance

Implementation follows:
- AGENTS.md;
- DOCUMENT_CONTRACT;
- non-superseded Accepted ADRs;
- ARCHITECTURE;
- IMPLEMENTATION;
- TEST_STRATEGY;
- QUALITY_GATES;
- REVIEW_PROCESS.

A material repository/API/physical-model contradiction returns to specification adjudication before implementation continues.
