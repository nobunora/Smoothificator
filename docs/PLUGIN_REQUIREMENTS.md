# Plugin Requirements — Stock Orca Printable Architecture

## 1. Orca compatibility
Target Orca builds containing:
- Python Plugin System
- SlicingPipeline capability
- posSimplifyPath
- psGCodePostProcess
- host UI Script capability

Pin exact tested Orca commit/version per release because SlicingPipeline is experimental.

## 2. Plugin capabilities
One package registers:
1. SlicingPipeline capability
   - posSimplifyPath analyzer
   - psGCodePostProcess injector
2. Script capability
   - preview/diagnostics through orca.host.ui

No UI calls from slicing worker.

## 3. Geometry inputs
Stock Orca must expose:
- Print/PrintObject/Layer/LayerRegion
- Print-owned Model snapshot
- ModelVolume mesh/transforms
- simplified ExtrusionPath 3D points
- width/height/mm3_per_mm
- active filament diameter and filament_flow_ratio
- resolved config

Adapter normalizes all data before domain use.

## 4. ZAA normalization
For ContourZ paths:
- raw point.z is layer-relative offset;
- absolute Z = layer.print_z + unscale(point.z);
- effective local extrusion for non-ironing segments matches Orca's (height+d)/height scaling.

Any profile/source change that invalidates this assumption requires compatibility review.

## 5. Printable v1 geometry gates
Injection requires:
- exactly one printable PrintObject;
- exactly one printable instance;
- exactly one ModelPart volume;
- no NegativeVolume/ParameterModifier;
- nested/self-supported top-facing target;
- no support/raft;
- no bridge target;
- ironing disabled;
- scarf/sloped seam disabled;
- spiral vase disabled.

Unsupported geometry may be analyzed but not injected.

## 6. Printable v1 plugin-environment gates
Requires:
- fresh slice in current plugin load/session;
- no classic post_process script;
- no other active slicing-pipeline plugin.

Missing current-session plan => skip and request re-slice.

## 7. Printable v1 Bambu/G-code gates
Requires a repository golden-fixture family for the exact supported Orca/profile.

Initial target:
- current Bambu 0.4 mm single-tool profile family;
- use_relative_e_distances=true;
- use_firmware_retraction=false;
- gcode_add_line_number=false;
- enable_arc_fitting=false;
- one tool;
- validated before_layer_change_gcode/layer_change_gcode environment;
- no unknown motion-producing custom code around insertion anchor.

The supported exact machine/profile list is not active until corresponding fixtures/tests exist.

## 8. Surface-band semantics
Source mesh boundary is not a print centerline.

Planner must derive centerlines inside material and may create several paths at one/different Z.

0.08 mm initial limit applies to effective bead height above local support, not pairwise candidate Z distance.

## 9. Execution semantics
v1 only **adds** validated SubEdge paths.

It does not rewrite original Orca structural wall flow or XY.

Final-surface optimization must account for overlap/overbuild with unchanged structural/ZAA beads.

## 10. Execution-frame mapping and safe travel
Plan geometry is print-space mm. Final G-code uses instance/origin/extruder/Z-offset adjusted machine coordinates.

Before emission, injector MUST derive and validate one constant (dx,dy,dz) translation from matched Orca structural geometry per ADR-0009.

No plan coordinate may be emitted before that validation.

All non-extruding XY moves for injected paths occur at validated machine-coordinate Zsafe per ADR-0007.

Injector restores saved upper structural-layer state before Orca resumes.

## 11. Cross-hook state
PlanStore:
- process-local
- thread-safe
- immutable plans
- separate runtime status
- candidate enumeration for final G-code matching
- no Orca live references

At export exactly one plan must match. Zero/multiple => skip.

## 12. Preview
Orca standard G-code preview is pre-postprocess.

Plugin preview uses exact immutable plan and separate execution status.

## 13. Extrusion conversion
Candidate E generation MUST match Orca's single-filament volumetric conversion:

E_per_mm3 = filament_flow_ratio / filament_cross_section

Do not assume flow ratio = 1.0.

The planned filament parameters must match the final supported profile fingerprint.

## 14. File processing
G-code postprocessor must be:
- stateful parser based
- streaming/multi-pass
- idempotent
- all-or-nothing
- temp-file + atomic replace
- original-preserving on failure

No full-file regex substitution.

## 15. Packaging
Target pure-Python wheel.

No native/custom Orca dependency in v1.

## 16. Golden-fixture requirement
Before any physical support for a profile:
- exact Orca version/commit
- exact printer/process profile metadata
- source G-code fixture
- expected parser states
- layer-boundary anchors
- expected injected output
- idempotence fixture
- failure fixtures

No fixture => analysis-only.

## 17. Compatibility default
Unknown Orca/profile/dialect/state -> injection disabled.

Never best-effort mutate.
