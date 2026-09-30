# Adaptive Sub-Edge Surface Reconstruction — System Specification

## 1. Goal

Adaptive Sub-Edge is a stock-OrcaSlicer Python plugin that improves FDM outer-surface fidelity where Orca's normal slicing and Z Anti-Aliasing (ZAA / Z Contouring) still leave unacceptable geometric error.

v1 MUST NOT require a custom Orca build.

The central strategy is:

1. let Orca finish its normal geometry work, including ZAA when applicable;
2. inspect the final simplified structural toolpaths;
3. predict the finite-bead printed surface;
4. find residual surface bands that remain outside tolerance;
5. plan the minimum additional printable SubEdge paths required;
6. preview that exact immutable plan;
7. inject that exact plan into the final working G-code only after strict compatibility, coordinate, state, and safety validation.

## 2. Canonical pipeline

```text
Orca slice
  -> ZAA / normal path generation
  -> path simplification
  -> posSimplifyPath
       -> Orca adapter snapshot
       -> centered source-mesh reconstruction
       -> ZAA absolute-Z + local-flow normalization
       -> finite-bead baseline
       -> residual-error / surface-band planning
       -> immutable SubEdgePlan
            -> plugin preview
  -> normal Orca G-code generation
  -> psGCodePostProcess
       -> export config fingerprint validation
       -> streaming parser / actual machine state
       -> seam-invariant structural-path matching
       -> execution-frame translation
       -> quantized execution validation
       -> safe additive injection
       -> exact state restoration
       -> atomic replace
  -> file / printer
```

The original Orca structural extrusion remains unchanged in printable v1.

## 3. Single source of truth

The exact same immutable `SubEdgePlan` MUST drive:
- preview;
- predicted metrics;
- final G-code injection.

The injector MUST NOT:
- rerun the optimizer;
- infer replacement geometry from G-code;
- silently change the plan to make it fit final G-code.

Execution status is stored separately from the immutable plan.

## 4. Canonical geometry frame

All domain/engine geometry uses **Orca centered PrintObject slice-space expressed in millimeters**.

For printable v1:
- exactly one PrintObject;
- exactly one total source ModelInstance;
- exactly one positive ModelPart volume;
- the current bound source mesh is finite and manifold;
- every required arbitrary-Z section forms an unambiguous closed material boundary.

The Orca adapter MUST reconstruct the centered frame defined by ADR-0012. A direct `PrintObject.trafo() @ ModelVolume.matrix()` transform is insufficient.

No plan is injectable unless source mesh, PrintObject bounding geometry, and simplified path geometry pass the centered-frame parity checks.

## 5. ZAA baseline semantics

The analyzer reads final simplified paths at `posSimplifyPath`.

For a Z-contoured path:
- Orca path-point Z is a relative offset `d`;
- absolute slice-space nozzle Z is:

[
Z_{abs}=Layer.print_z + d
]

after Orca unscale conversion;

- for non-ironing ZAA segments, Orca locally scales extrusion by:

[
r_{zaa}=rac{path.height+d}{path.height}.
]

The baseline predictor MUST include both the Z change and effective local command-flow change.

If ZAA did not apply, ordinary planar paths naturally become the baseline.

## 6. Surface boundary and SubEdge centerlines

A source mesh-plane intersection is a **target material boundary**, not an extrusion centerline.

The engine:
1. derives a residual surface band;
2. determines the material side;
3. lays out one or more printable centerlines inside that material;
4. evaluates the finite-bead envelope against the source boundary.

A residual band may require:
- multiple paths at one Z;
- multiple paths at different independently optimized Z values;
- a combination.

Each printable v1 SubEdgePath itself is planar/constant-Z. Segment-local effective height may still vary because the support surface below it varies.

No fixed half-pitch, 1/2, 1/3, or uniform subdivision rule is permitted.

## 7. Effective bead-height rule

Initial 0.4 mm nozzle research uses:

[
h_{min}=0.08	ext{ mm}
]

as a configurable/calibratable **minimum effective deposited bead height above local support**.

For candidate segment (j):

[
h_{eff,j}=Z_{nozzle,j}-Z_{support,j}.
]

It is NOT a mandatory pairwise Z separation between neighboring SubEdge paths.

Pairwise feasibility is determined by:
- finite bead overlap/overbuild;
- local support;
- nozzle clearance;
- path crossing;
- machine/G-code quantization.

## 8. Segment-local candidate extrusion

A `SubEdgePath` is an explicit open execution path at one immutable `command_z_mm`, composed of ordered immutable `SubEdgeSegment` records.

Closed candidate contours are converted to open executable paths by a deterministic candidate seam/gap policy before plan finalization. That seam/gap is included in preview and finite-bead scoring.

Each segment carries the local:
- start/end XYZ;
- support height;
- effective bead height;
- width;
- geometric volumetric flow;
- commanded volumetric flow;
- final relative-E value after compatibility conversion/quantization;
- speed constraint.

A path-wide constant flow MUST NOT be assumed when support height varies.

## 9. Geometric versus commanded flow

For an ideal non-bridge candidate bead of width (w) and effective height (h), the initial geometric rounded-rectangle cross-section is:

[
q_{geom}
=
hleft(w-h(1-pi/4)ight)
]

in mm³/mm.

For the audited Orca external-wall semantics, commanded candidate flow is:

[
q_{cmd}
=
q_{geom}
cdot r_{print}
cdot r_{filament}
cdot r_{outer}
]

where:
- (r_{print}) = `print_flow_ratio`;
- (r_{filament}) = resolved `filament_flow_ratio`;
- (r_{outer}) = `outer_wall_flow_ratio` when `set_other_flow_ratios` is enabled, otherwise 1.

The final relative-E command is based on (q_{cmd}) and filament cross-section, then Orca-compatible E quantization.

The documentation MUST distinguish:
- ideal geometric bead volume;
- commanded calibrated volume;
- predicted physical bead geometry.

v1 uses a commanded-volume approximation; empirical bead calibration comes later.

## 10. Final combined surface

Candidate quality is evaluated from the combined finite-bead envelope of:
- existing lower structural/ZAA beads;
- candidate SubEdge beads;
- existing upper structural/ZAA beads.

v1 does NOT rewrite the original structural outer wall.

A candidate that reduces one local error but causes unacceptable overbuild elsewhere is infeasible.

## 11. Supported printable geometry

Printable v1 requires nested/self-supported top-facing geometry.

Higher target material must remain supported by lower predicted material within configured tolerance.

Reject printable injection for:
- outward-expanding unsupported/overhang surface bands;
- support-dependent targets;
- bridge target extrusion;
- uncertain nozzle-body clearance;
- candidate/path crossings;
- invalid or unresolvable local support.

Unsupported geometry may still be analyzed and previewed as non-injectable.

## 12. Optimization target

Where feasible:

[
E_{max}le tolerance
]

using surface-normal / closest-reference signed error.

Required quality metrics:
- (E_{max});
- (E_{rms});
- (E_{p95});
- signed mean/bias.

Among feasible candidate sets minimize a documented cost containing:
- geometric error;
- candidate path length;
- added commanded material;
- estimated print time;
- complexity/risk penalty.

Optimization MUST be deterministic for identical canonical input/settings.

## 13. Preview contract

Orca standard G-code preview represents the pre-`psGCodePostProcess` file.

Plugin preview displays the exact immutable plan:
- final structural/ZAA baseline;
- target material boundary;
- planned SubEdge centerlines/segments;
- local bead height/flow ranges;
- support/nesting diagnostics;
- error map;
- metrics;
- compatibility/injectability gates;
- plan hash;
- execution status.

Status:
- PLANNED
- INJECTION_PASS
- INJECTION_SKIPPED
- INJECTION_FAIL

Status does not alter plan hash.

## 14. Thread and lifetime contract

SlicingPipeline geometry callbacks run in the slicing workflow thread.

MUST NOT call `orca.host.ui.*` from the geometry callback.

Live Orca/pybind objects and zero-copy arrays backed by Orca MUST NOT survive `execute(ctx)`.

The adapter copies and normalizes all required information before returning.

## 15. Planning/export configuration identity

Planning creates:
- a versioned `ExecutionConfigFingerprint` from Orca/export safety-relevant semantics;
- a versioned `PluginSettingsFingerprint` from the complete validated Adaptive Sub-Edge settings that can affect plan geometry, optimization, seam policy, collision margins, or execution policy.

At `psGCodePostProcess`:
- recompute the Orca fingerprint with `ctx.config_value()`;
- recompute the plugin-settings fingerprint from the SlicingPipeline capability's current `self.get_config()`.

Injection requires exact equality for both fingerprints.

The fingerprint covers at minimum all settings that affect:
- geometry/frame identity;
- ZAA and flow semantics;
- seam matching;
- extrusion conversion;
- retraction;
- motion/speed/Zsafe;
- custom layer/role G-code;
- printable feature gates.

Missing or unresolved required settings disable injection.

## 16. Final-G-code structural matching

Final G-code is not expected to be point-for-point identical to the `posSimplifyPath` loop.

The matcher MUST account for normal Orca seam processing:
- cyclic loop start change;
- seam split;
- collinear subdivision;
- configured single seam-gap clipping interval;
- final G-code coordinate translation/quantization.

Scarf/sloped seams and arc-fitted target geometry are unsupported in printable v1.

Comments/tags may strengthen matching but are not the sole geometry evidence.

Exactly one plan/structural reference must match. Zero or multiple matches => skip.

## 17. Print-space to machine-G-code frame

Plan coordinates MUST NOT be emitted directly.

At postprocess:
1. match baseline structural geometry;
2. infer one constant translation ((dx,dy,dz)) from multiple anchors;
3. require translation consistency within versioned tolerance;
4. reject rotation/scale/shear/non-constant mapping;
5. apply the translation only in the G-code adapter.

The translation accounts for final instance/origin/extruder/Z-offset effects.

## 18. Orca-compatible G-code quantization

For the audited Orca source family, the compatibility layer reproduces Orca formatter semantics:
- XYZ/F: 3 decimals;
- E: 5 decimals;
- C++ `std::round` midpoint behavior.

After frame translation and quantization, execution-critical geometry/flow constraints MUST be revalidated.

Unknown formatter behavior for another Orca version disables injection.

## 19. Relative-E and retraction contract

Printable v1 requires:
- relative E;
- firmware retraction disabled;
- an unambiguously parsed, positively retracted insertion state;
- zero ordinary restart-extra;
- known retraction/deretraction speeds.

Candidate blocks temporarily unretract/retract exactly the parsed saved amount and finish in the same retracted state.

The original Orca G-code performs its original later unretract.

If retraction state cannot be proven, skip injection.

## 20. Layer-boundary and actual-state restoration

The layer-change marker does not imply that physical machine Z has already reached the new nominal layer height.

At the insertion point, the parser captures the **actual emitted machine state**.

Injected travel:
- raises vertically to validated `Zsafe`;
- performs all non-extruding XY travel at `Zsafe`;
- descends vertically to candidate Z;
- prints;
- returns to `Zsafe`.

After the final candidate, restore the exact actual pre-insertion XYZ/E/feed/modal state and resume the original file unchanged.

Do NOT synthesize Orca's deferred layer synchronization.

## 21. Motion/extrusion safety envelope

Printable v1 additionally requires:
- one tool / one filament execution context;
- normal non-calibration print;
- no first-layer SubEdge refinement;
- fuzzy skin disabled for the target;
- filament adaptive volumetric speed disabled;
- adaptive pressure advance disabled;
- extrusion-role-change custom G-code empty;
- line numbers/checksums off;
- arc fitting off;
- spiral vase off;
- ironing off;
- scarf/sloped seam off;
- support/raft off;
- no other slicing-pipeline plugin;
- no classic post-process script;
- verbose G-code/comments enabled for initial physical fixtures;
- fresh current-session plan.

Static pressure advance may remain enabled and is inherited unchanged.

Candidate segment speed MUST NOT exceed:
- resolved outer-wall speed;
- resolved filament max volumetric speed divided by candidate commanded mm³/mm;
- optional lower plugin/user cap.

Zsafe uses resolved active Z-hop/travel lift and MUST remain below the active tool printable-height limit.

The plugin never silently changes Orca settings; unsupported settings are reported as analysis-only gates.

Candidate execution speed is additionally bounded by the actual feed rate observed on the uniquely matched structural external-wall reference in final G-code when that observed feed is lower than config-derived limits.

## 22. Printable v1 environment

Physical injection is enabled only for an explicitly golden-fixtured Bambu/Orca 0.4 mm single-tool profile family satisfying every requirement above.

The normal Bambu process may enable arc fitting by default; such a profile is analysis-only until arc fitting is explicitly disabled in the user/process configuration and the resulting profile is fixture-validated.

No fixture => no injection.

## 23. Downstream original-motion clearance

Safe plugin travel is necessary but not sufficient because Orca generated all later G-code without knowledge of injected material.

Before mutation, validate candidate material against unchanged downstream original motions using ADR-0025:
- transform and quantize candidate bead envelopes into machine space;
- scan downstream original motions over a conservative clearance horizon;
- reject low-Z travel or extrusion whose nozzle-clearance proxy intersects candidate material;
- reject unknown XYZ/E-affecting motion in the horizon.

The software nozzle-clearance proxy is a screening model, not proof of arbitrary real hotend-body clearance. Physical nozzle-family clearance calibration is required before broad collision-safety claims.

## 24. G-code file mutation contract

`psGCodePostProcess` uses a streaming, all-or-nothing workflow:

1. validation pass;
2. exact plan/config/matcher/state validation;
3. temp-file emission pass;
4. sanity parse/verification;
5. atomic replacement only after success.

Original bytes/lines outside intentional insertion markers/blocks remain preserved as far as the line-streaming representation permits.

Idempotence markers prevent duplicate injection.

Expected unsupported/validation failures return plugin `Skipped` and preserve valid Orca output.

`Success` is reserved for successful injection or a validated already-injected no-op.

## 25. Failure behavior

Any uncertainty in:
- source centered frame;
- current-session plan identity;
- export config fingerprint;
- structural-loop match;
- execution-frame translation;
- formatter compatibility;
- actual machine/modal/retraction state;
- flow/speed/profile compatibility;
- support/collision;
- calibration/custom code;
- safe ceiling;
causes injection to be skipped.

The project MUST prefer an unchanged valid Orca G-code over a guessed modification.

## 26. Non-goals v1

- custom Orca/C++ dependency;
- mutating live Orca perimeters;
- replacing ZAA;
- rewriting structural wall extrusion;
- full non-planar printing;
- multi-object / multi-instance / multi-volume CSG injection;
- multitool/multifilament injection;
- absolute-E injection;
- firmware retract;
- arc G2/G3 candidate output;
- adaptive-PA emulation;
- unsupported overhang reconstruction;
- first-layer SubEdge refinement;
- fuzzy-skin correction;
- adaptive-volumetric-speed parity;
- calibration-mode injection;
- claiming Orca standard preview contains injected paths.

## 27. Governance

Implementation MUST follow:
- `AGENTS.md`;
- `docs/DOCUMENT_CONTRACT.md`;
- Accepted ADRs;
- `docs/ARCHITECTURE.md`;
- `docs/IMPLEMENTATION.md`;
- `docs/TEST_STRATEGY.md`;
- `docs/QUALITY_GATES.md`;
- `docs/REVIEW_PROCESS.md`.

A repository/API discovery that changes a material contract requires specification/ADR adjudication before implementation continues.
