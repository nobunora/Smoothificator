# OrcaSlicer Plugin / Geometry / G-code Research

Audit baseline: OrcaSlicer main commit `789f848694b955d293ca6b277d1c8046aa6f7436` (2026-09-29).

This document records source evidence. Normative decisions live in Accepted ADRs and higher-precedence specifications.

## 1. Stock-Orca feasibility

A conservative printable v1 remains technically feasible without a custom Orca build by combining:
- `posSimplifyPath` for read-only post-ZAA/post-simplification geometry analysis;
- `psGCodePostProcess` for final working-file modification;
- a Script capability for preview.

No source-level blocker was found inside the deliberately narrow v1 scope, but multiple implementation assumptions required correction during the audit.

## 2. Hook ordering

Source: `src/libslic3r/Print.cpp`.

Findings:
- `posContouring` plugin execution is conditional on `need_z_contouring()`;
- `simplify_extrusion_path()` runs later;
- `posSimplifyPath` runs after path simplification for freshly processed objects;
- cache-loaded plugin-final objects may not re-fire geometry hooks.

Conclusion:
- canonical analyzer = `posSimplifyPath`;
- missing current-session plan at export => no injection.

ADR: 0001.

## 3. Plugin postprocess context

Sources:
- `SlicingPipelinePluginCapability.cpp`;
- `PostProcessor.cpp`;
- official sandbox G-code-stamp plugin.

At `psGCodePostProcess`:
- no live Print/PrintObject;
- `ctx.gcode_path` points to working export;
- `ctx.config_value()` still resolves final full config;
- plugin edits working file in place;
- postprocess can execute more than once for separate export/upload copies;
- standard Orca preview does not include plugin postprocessed paths.

PluginResult behavior from Orca postprocessor:
- `RecoverableError` / `FatalError` can abort the export pipeline;
- routine Adaptive Sub-Edge unsupported/validation conditions should therefore return `Skipped`.

ADR: 0011, 0019.

## 4. Multiple capabilities

Sources:
- `PyPluginPackage`;
- official Script/Inspector sandbox examples.

One plugin package may register multiple capability classes.

Therefore one package can provide:
- SlicingPipeline analyzer/injector;
- Script/UI preview.

## 5. Readable geometry and mutability

`PluginHostSlicing.cpp` exposes read access to:
- Print / PrintObject;
- Layer / LayerRegion;
- source Model snapshot;
- ExtrusionPath 3D points;
- width / height / mm3_per_mm / role;
- resolved config.

Generated perimeter/path geometry is not freely appendable/mutable from public Python bindings.

This is not a v1 blocker because v1 plans geometry read-only and injects additive commands at final G-code.

## 6. Source mesh centered coordinate frame

Sources:
- `PrintObject.cpp`;
- `PrintObjectSlice.cpp`;
- `PrintApply.cpp`;
- `Model.cpp`;
- PluginHostModel bindings.

Critical finding:
the earlier direct source transform

`PrintObject.trafo() @ ModelVolume.matrix()`

does NOT reproduce Orca's sliced frame.

Orca slicing uses `PrintObject::trafo_centered()`, which subtracts XY `m_center_offset`.

The offset is derived from the raw ModelPart bounding box after applying the source ModelInstance transform with translation removed.

Python does not expose `trafo_centered()`, but exposes enough inputs to reconstruct it for the one-instance/one-volume v1 scope.

ADR: 0012.

## 7. ZAA Z semantics

Source: `ContourZ.cpp`.

ContourZ stores path-point Z as a relative offset (d).

Absolute centered-slice nozzle Z:

[
Z=Layer.print_z+d.
]

External perimeters are prevented from positive local d but may be lowered.

ADR: 0006.

## 8. ZAA local E semantics

Source: `GCode.cpp::_extrude`.

For `path.z_contoured` non-ironing segments:

[
r_{zaa}=(path.height+d)/path.height
]

and emitted E is multiplied by this local ratio.

Therefore a correct baseline model needs:
- local Z;
- local effective height;
- local geometry-directed volume ratio.

ADR: 0006, 0022.

## 9. Orca external-wall flow chain

Source: `GCode.cpp::_extrude` and `Extruder.cpp`.

Critical finding:
ADR-0010's original formula was incomplete.

For supported external-perimeter semantics, effective commanded volumetric line flow includes:
- `print_flow_ratio`;
- `filament_flow_ratio`;
- optional `outer_wall_flow_ratio` when `set_other_flow_ratios` is enabled.

Extruder E conversion includes filament cross-section.

Small Area Flow Compensation is not applied to external-perimeter role in the audited source.

ADR-0015 supersedes ADR-0010's complete formula.

## 10. Geometry versus calibration flow

Global flow ratios are execution/calibration controls.

Treating them as direct geometric width multipliers is not physically justified without empirical calibration.

v1 therefore distinguishes:
- nominal geometric bead volume used for ideal surface prediction;
- commanded calibrated volume used for G-code and volumetric limits.

ADR: 0022.

## 11. Loop seam processing before final G-code

Source: `GCode::extrude_loop()`.

Before final extrusion:
- Orca places/splits the seam;
- applies normal seam-gap clipping;
- may subdivide paths during processing;
- may emit wipe moves.

The default `seam_gap` in audited PrintConfig is 10%.

Therefore ordered `posSimplifyPath` point hashes are not stable final-G-code identifiers.

ADR: 0016.

## 12. Layer-change physical-state behavior

Source: `GCode::change_layer()` and GCodeWriter lift handling.

Critical finding:
normal layer change updates Orca's internal nominal Z but does not guarantee an immediate physical Z G-code move. Z/lift synchronization may be deferred until later motion.

Therefore postprocess restoration must return to the actual parsed emitted machine state at the insertion point, not force nominal upper-layer Z.

ADR: 0013.

## 13. Retraction/wipe state

Sources:
- GCode/GCodeWriter/Extruder retraction logic;
- Bambu machine/filament profiles.

Bambu profiles commonly:
- retract on layer change;
- allow filament-specific retraction overrides;
- may use wipe.

Blindly emitting configured full retracts could double-retract.

v1 uses parsed actual retracted state and restores it exactly.

ADR: 0018.

## 14. G-code coordinate frame

Source: `GCode::point_to_gcode()`, `set_origin()`, `change_layer()`.

Final machine coordinates include effects such as:
- PrintInstance shift/current GCode origin;
- active extruder XY offset;
- printer Z offset.

Plan centered-slice coordinates MUST NOT be emitted directly.

Final matcher derives one validated constant translation for the one-instance/one-tool v1 scope.

ADR: 0009.

## 15. G-code formatter precision

Source: `GCodeFormatter`.

Audited formatter behavior:
- XYZ/F: 3 decimal digits;
- E: 5 decimal digits;
- C++ `std::round` semantics.

Python built-in round has different midpoint behavior.

Final candidate validity must be rechecked after Orca-compatible quantization.

ADR: 0017, 0021.

## 16. Final E derivation timing

Because final XYZ quantization can alter a short segment's emitted length, the immutable geometry-time plan must not store authoritative final E.

Final E is derived after:
- execution-frame mapping;
- XYZ quantization;
- emitted-length recomputation.

ADR: 0021.

## 17. Bambu layer-change templates

Audited Bambu common machine templates use motion-neutral progress/notification layer-change G-code for the initial family inspected.

However calibration modes can add extra layer-boundary behavior after normal markers.

Therefore:
- profile custom code is fingerprinted/validated;
- calibration/tower G-code is unsupported in v1.

ADR: 0007, 0013, 0020.

## 18. Bambu profile defaults affecting v1

Audited profile observations include:
- global Orca default relative E = enabled;
- Bambu machine common retract-on-layer-change = enabled;
- Bambu process common may enable arc fitting;
- default seam_gap = 10%;
- Bambu filament profiles may use flow ratio != 1 and filament-specific retraction/wipe settings.

Consequences:
- nonzero seam gap is supported by matcher rather than forcing 0;
- arc fitting remains a visible unmet injection gate unless disabled;
- flow/retraction must use resolved semantics rather than hard-coded defaults.

## 19. Pressure advance and role-change behavior

`GCode::_extrude()` may evaluate adaptive pressure advance and may execute machine/filament/process extrusion-role-change custom G-code.

Injected paths bypass that orchestration.

v1 therefore:
- rejects adaptive PA;
- requires extrusion-role-change custom G-code empty;
- may inherit static pressure advance unchanged.

ADR: 0020.

## 20. Candidate speed and machine Z limits

Relevant full config exposes:
- outer-wall speed;
- filament max volumetric speed;
- travel / Z-travel speed;
- Z hop;
- printable height / extruder printable height.

v1 uses these resolved profile values rather than hard-coded motion rates/lifts.

ADR: 0020.

## 21. Large G-code files

Full-file in-memory rewrite is not required.

v1 uses:
1. streaming validation;
2. streaming temp emission;
3. streaming sanity validation;
4. atomic replacement.

## 22. Remaining highest-risk engineering areas

No currently known stock-Orca API impossibility remains for the narrowed v1.

The highest-risk implementation areas are:
- exact centered-frame parity;
- geometry-aware final-G-code matching;
- parser/retraction/modal-state correctness;
- execution-frame/quantization parity;
- finite-bead physical model accuracy.

The first four are software contracts with deterministic fixtures.

The last remains a physical-model hypothesis and requires coupon calibration before production-quality claims.
