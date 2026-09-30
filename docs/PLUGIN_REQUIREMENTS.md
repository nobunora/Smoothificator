# Plugin Requirements — Stock Orca Printable v1

## 1. Compatibility baseline

The technical audit used OrcaSlicer source commit:

`789f848694b955d293ca6b277d1c8046aa6f7436`

as the source-level reference.

Production injection support is granted only to explicitly tested Orca release/commit + printer/process/filament fixture families.

SlicingPipeline is experimental; unknown API/source behavior defaults to analysis-only.

## 2. Python/runtime

Initial audited Orca plugin examples use:
- Python >= 3.12;
- NumPy for bound array access.

Actual package metadata is finalized only after Phase 0.5 verifies the target embedded runtime.

## 3. Plugin capabilities

One package provides:
- SlicingPipeline capability:
  - `posSimplifyPath`;
  - `psGCodePostProcess`;
- Script/UI capability:
  - preview/diagnostics.

No UI calls from slicing workflow callbacks.

## 4. Required read-only Orca data

The compatible Orca build must expose:
- Print / PrintObject / Layer / LayerRegion;
- Print-owned Model snapshot;
- ModelObject / ModelInstance / ModelVolume;
- source mesh vertices/triangles;
- instance/volume/PrintObject transforms;
- PrintObject bounding box;
- simplified 3D ExtrusionPath geometry;
- width/height/mm3_per_mm/role;
- resolved config through geometry context;
- `ctx.config_value()` at G-code postprocess.

Missing required binding => analysis/injection capability disabled as appropriate.

## 5. Printable source topology

v1 injection requires:
- one PrintObject;
- exactly one total source ModelInstance;
- exactly one positive ModelPart volume;
- no negative/modifier/CSG helper volume;
- one tool/filament execution context.

The adapter reconstructs Orca's centered slice frame per ADR-0012.

Transform parity failure => no injection.

## 6. ZAA normalization

For Z-contoured paths:
- raw point Z is layer-relative;
- absolute centered-slice Z = layer.print_z + unscaled offset;
- local geometry-directed ZAA volume ratio = (path.height + offset) / path.height.

Global calibration flow ratios are tracked separately from nominal geometric bead prediction.

## 7. ExecutionConfigFingerprint

A versioned fingerprint is built both:
- during planning;
- during `psGCodePostProcess` using `ctx.config_value()`.

It contains resolved semantic values, not independently interpreted raw overrides.

Required semantic groups include:

### Geometry/seam
- nozzle diameter;
- seam_gap resolved semantics;
- scarf/seam-slope state;
- spiral state;
- ironing state;
- support/raft state.

### Flow/material
- print_flow_ratio;
- active filament_flow_ratio;
- set_other_flow_ratios;
- outer_wall_flow_ratio;
- filament diameter;
- filament max volumetric speed.

### Retraction
- relative/absolute E mode;
- firmware-retraction state;
- effective retract-on-layer-change;
- effective retraction length;
- retract speed;
- deretract speed;
- restart extra;
- wipe/retract-before-wipe/retract-after-wipe values required by fixture semantics.

### Motion
- outer-wall speed;
- XY travel speed;
- Z travel speed;
- active Z hop;
- printer/active extruder printable height;
- z_offset;
- active extruder XY offset.

### External execution behavior
- gcode line-number/checksum state;
- gcode_comments;
- arc fitting;
- adaptive pressure advance;
- static pressure-advance state for diagnostics;
- machine/filament/process extrusion-role-change G-code;
- before_layer_change_gcode;
- layer_change_gcode;
- classic post_process;
- selected slicing-pipeline capabilities;
- print-sequence/profile-family invariants required by fixtures.

Any missing/mismatched required semantic value => Skipped.

## 8. Printable geometry gates

Target region must be:
- top-facing/nested/self-supported;
- non-bridge;
- no support/raft dependency;
- valid local support height;
- no candidate crossing;
- no unresolved nozzle-clearance conflict.

Unsupported regions may be previewed as non-injectable.

## 9. Printable G-code/profile gates

Initial physical v1 requires a golden-fixtured Bambu/Orca 0.4 mm single-tool family with:

- relative E;
- firmware retraction off;
- line numbering/checksum off;
- arc fitting off;
- spiral vase off;
- ironing off for unsupported target;
- scarf/sloped seam off;
- support/raft off;
- adaptive PA off;
- role-change custom G-code empty;
- classic post_process empty;
- no other slicing-pipeline plugin;
- verbose G-code/comments enabled for fixture diagnostics/matching;
- supported motion-neutral before/layer-change custom code;
- normal print, not calibration/tower mode;
- fresh current-session plan;
- unambiguous positive retraction state at insertion boundary;
- zero ordinary retract restart-extra;
- positive active Z hop;
- valid printable-height margin.

Bambu standard process profiles may enable arc fitting by default. The plugin MUST report this as an unmet injection requirement; it MUST NOT silently change the user profile.

## 10. Seam handling

Nonzero normal seam gap is supported.

Matcher must tolerate:
- cyclic seam start;
- seam split;
- collinear subdivision;
- one contiguous clip interval equal to the Orca-resolved seam-gap amount within tolerance.

Raw ordered-loop equality is not a supported matcher.

## 11. Coordinate execution mapping

Domain plan geometry stays in centered PrintObject slice-space.

At final G-code:
- match unique structural geometry;
- derive constant ((dx,dy,dz));
- require consistency across multiple anchors;
- apply only in G-code adapter.

Unknown/non-constant mapping => Skipped.

## 12. Formatter compatibility

For the audited Orca source descriptor:
- XYZ/F precision: 3 decimals;
- E precision: 5 decimals;
- midpoint rounding matches C++ `std::round`.

Emitter and final validation share one compatibility quantizer.

Unknown formatter contract => no injection.

## 13. Flow and E conversion

Candidate plan segment stores:
- geometric mm³/mm;
- commanded mm³/mm.

For external-surface v1:

[
q_{cmd}
=
q_{geom}
cdot print_flow_ratio
cdot filament_flow_ratio
cdot applicable outer role ratio.
]

Final E is derived only after machine XYZ quantization from the quantized segment length.

Do not pre-store final E in the immutable plan.

## 14. Speed and volumetric limits

Each emitted segment speed is bounded by:
- resolved outer-wall speed;
- resolved filament max volumetric speed / commanded mm³/mm;
- optional lower plugin cap.

No resolved safe bound => no injection.

## 15. Retraction/state requirements

Parser reconstructs actual final-G-code state.

v1 candidate travel starts from an already-retracted supported boundary.

The plugin:
- travels safely while retracted;
- unretracts exactly saved amount;
- prints;
- retracts exactly saved amount;
- finishes in the same retraction state.

It does not reproduce wipe.

Ambiguous retraction => Skipped.

## 16. Safe-ceiling requirement

Machine-space Zsafe is based on:
- actual parsed saved Z;
- target upper structural machine Z;
- positive active Z hop.

Require:
- Zsafe within active tool printable-height limit;
- all injected non-extruding XY travel occurs at Zsafe;
- vertical-only raise/descend around candidate XY travel.

## 17. Final-state restoration

After injection, restore the actual parsed pre-insertion machine state, not an inferred nominal upper-layer state.

The unchanged original G-code remains responsible for Orca's deferred layer/Z behavior.

## 18. File processing

Postprocessor is:
- streaming;
- parser/state-machine based;
- validation-first;
- idempotent;
- temp-file based;
- sanity-checked;
- atomic;
- all-or-nothing.

Expected unsupported/validation result => PluginResult.Skipped + original file unchanged.

## 19. Preview

Standard Orca preview is pre-postprocess.

Plugin preview uses the exact immutable plan and separate execution status.

It explicitly shows unmet injection gates.

## 20. Packaging

Target: pure-Python wheel.

No native/custom-Orca dependency in v1.

## 21. Fixture requirement

No printer/profile family is injectable until repository fixtures record:
- exact Orca release/commit;
- exact machine/process/filament profile identity;
- resolved semantic config;
- source G-code;
- expected parser state;
- structural matching expectations;
- execution-frame translation;
- retraction state;
- quantization;
- expected injected output;
- idempotence;
- representative failure cases.

No fixture => analysis-only.

## 22. Compatibility default

Unknown Orca source/API, profile, config, modal state, custom code, calibration behavior, coordinate mapping, or machine limit => injection disabled.

Never best-effort mutate.
