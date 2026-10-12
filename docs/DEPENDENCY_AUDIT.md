# Pre-implementation Dependency and Feasibility Audit

> Historical partial audit. Superseded for readiness decisions by [FULL_CONSISTENCY_AUDIT_2026-09-30.md](FULL_CONSISTENCY_AUDIT_2026-09-30.md). This file is retained as the chronological record of earlier findings.

Date: 2026-09-29
Status: Completed and reconciled before Phase 0.5 implementation (final consistency pass 2026-09-30).

## Scope reviewed
- README
- SPECIFICATION
- IMPLEMENTATION
- ARCHITECTURE
- ERROR_MODEL
- PLUGIN_REQUIREMENTS
- ORCASLICER_PLUGIN_RESEARCH
- ZAA_INTEGRATION
- SMOOTHIFICATOR_ANALYSIS
- ROADMAP
- ADR process
- upstream Smoothificator scripts
- current OrcaSlicer plugin/host source relevant to slicing, mesh, geometry and post-processing

## Findings requiring correction

### F-01 Analyzer hook was conditional and too early — Critical
Old: `posContouring`.

Orca source shows the hook only fires when Z contouring is needed. It also precedes `simplify_extrusion_path()`.

Fix: ADR-0001 changes analysis to `posSimplifyPath`.

### F-02 Old and new package layouts coexisted — High
IMPLEMENTATION contained both a flat module list and the later layered package structure.

Fix: remove the old layout; one normative source tree remains.

### F-03 Multi-volume arbitrary-Z source geometry was underspecified — Critical
Raw volume meshes are available, but arbitrary-Z fully evaluated Orca CSG/modifier output is not directly exposed.

Fix: ADR-0002 limits printable v1 to one instance / one ModelPart volume and no modifier/negative volumes.

### F-04 Post-process interference was not gated — High
`psGCodePostProcess` runs after classic post-processing scripts, and multiple slicing-pipeline capabilities may run in configured order.

Fix: v1 requires no classic post-process script and no other active slicing-pipeline capability.

### F-05 Flow/material overlap was underspecified — Critical
Adding a path changes volume. The unchanged next structural outer wall remains in the G-code.

Fix: ADR-0003 requires final combined finite-bead simulation and makes sub-edge flow part of optimization.

### F-06 ZAA local height invalidates nominal-only spacing — High
ZAA paths may be non-planar inside a structural layer. Simple `z_i-Z0` constraints are insufficient.

Fix: local finite-bead support/clearance constraints are authoritative; nominal Z bounds only limit search.

### F-07 Plan identity across hooks was incomplete — High
Post-process context has no live Print/object. Output name is unavailable during geometry analysis.

Fix: one-object v1 + immutable PlanStore + configuration/layer/geometry execution fingerprint. Injector selects exactly one matching finalized plan; zero or multiple matches => skip.

### F-08 Cache behavior was omitted — High
`posSimplifyPath` hooks are deliberately not fired for cache-loaded plugin-final objects.

Fix: require a fresh slice after plugin load/reload; missing current-session plan => skip.

### F-09 Injection location/travel contract was incomplete — Critical
Returning Z downward after added paths could cross printed material.

Fix: inject at structural layer boundary, print sub-edges low-to-high, then move upward to the next structural layer Z before returning control to Orca.

### F-10 Extrusion-coordinate scope was too broad — High
Added extrusion changes firmware E state. The earlier audit proposed supporting both relative and absolute E immediately.

Further scope review narrowed printable v1 via ADR-0008:
- relative E only;
- firmware retraction off;
- line-number/checksum mode off;
- absolute-E injection deferred.

The parser may still recognize M82/M83/G92 for diagnostics, but v1 MUST NOT inject in absolute-E mode.

### F-11 Full-file in-memory rewrite does not scale — Medium
Large G-code files can be hundreds of MB.

Fix: two/three-pass streaming design: validation pass -> temp-file emission pass -> sanity pass -> atomic replace.

### F-12 Domain status and immutable plan were conflated — Medium
Injection status changes after planning, but SubEdgePlan is immutable.

Fix: keep plan immutable; store InjectionAttempt/PlanRuntimeStatus separately.

### F-13 Preview/UI lifecycle needed source confirmation — Medium
Confirmed: one plugin may register multiple capabilities; Script capability runs in UI-safe plugin execution while SlicingPipeline runs in slicing workflow. Capability instances live for plugin load.

Fix: shared application PlanStore, UI-safe Script capability, no live Orca refs.

### F-14 ZAA path Z and flow semantics were incomplete — Critical
Direct Orca source verification found that ContourZ stores path-point Z as a layer-relative offset `d`, while GCode.cpp emits:
- absolute Z = nominal layer Z + d;
- non-ironing extrusion multiplier = (path.height + d) / path.height.

Treating the bound path Z as absolute, or treating ZAA flow as spatially constant, would corrupt the baseline surface model.

Fix: ADR-0006; the Orca adapter normalizes both absolute Z and local effective flow.

### F-15 The 0.08 mm constraint was assigned to the wrong quantity — Critical
Earlier drafts treated 0.08 mm as a minimum pairwise Z difference between neighboring SubEdge paths.

That unnecessarily prevents dense shallow-slope surface-band coverage and does not represent the physical constraint.

Fix: ADR-0004. The 0.08 mm initial value applies to **effective deposited bead height above local support**. Pairwise path Z differences are governed by support, overlap, nozzle clearance, crossing, and machine quantization.

### F-16 Mesh section was incorrectly close to being treated as a tool centerline — Critical
A plane/mesh intersection is a material boundary. Printing that curve directly as a bead centerline would generally grow the part outward by roughly part of the bead width.

Fix: ADR-0005. Derive a printable surface band and place one or more centerlines inside the material side; score final finite-bead coverage.

### F-17 Structural-wall rewrite was considered, then rejected for v1 — High
A later interim design proposed redistributing/re-writing the original upper structural outer-wall extrusion.

Review against ADR-0003 and the surface-band interpretation showed this was an unnecessary and risky coupling for the first stock-Orca injector. SubEdge paths may occupy exposed lateral/terrace material without vertically replacing the structural wall.

Fix: canonical v1 leaves original Orca structural/ZAA G-code unchanged and optimizes **candidate SubEdge flow** against the combined final envelope.

### F-18 Duplicate Accepted ADR identifiers existed — Critical governance defect
Parallel design work created two different Accepted decisions under the same ADR numbers 0001-0005.

That made precedence undefined and could cause a coding agent to implement mutually incompatible requirements.

Fix:
- removed the duplicate later ADR files;
- retained one canonical Accepted ADR sequence 0001-0008;
- ADR_PROCESS now forbids identifier reuse;
- CI/document audit must verify ADR identifier uniqueness.

## Feasibility conclusion
No fundamental source/API blocker is currently known for the deliberately narrow v1 on stock Orca.

This is an implementation-feasibility conclusion, not a claim that the physical printing concept is proven. Physical validity remains gated by staged simulation, golden-G-code tests, and coupon printing.

The highest-risk area is not plugin access; it is safe translation of a geometry-derived plan into final G-code. The all-or-nothing parser/anchor/state architecture remains mandatory.

## Mandatory implementation gates before real printing
1. Architecture/import boundary tests.
2. Geometry/reference engine.
3. Orca snapshot/coordinate-frame tests.
4. Plan identity/fresh-slice tests.
5. G-code parser read-only tests.
6. Dry-run injection generation.
7. Golden G-code tests.
8. File atomicity/idempotence tests.
9. Simulator/manual G-code review.
10. Only then physical printing.


### F-19 Plan print-space coordinates were not mapped to final G-code coordinates — Critical
Orca source shows GCode::point_to_gcode() applies the current PrintInstance origin and active extruder XY offset, while change_layer() adds printer z_offset to machine Z.

A plan generated from sliced print-space geometry therefore cannot be emitted directly as G-code XYZ.

Fix: ADR-0009. At final G-code matching, derive and validate a constant (dx,dy,dz) translation from existing Orca-generated structural geometry. Only the G-code adapter applies it. Any inconsistent/non-constant mapping disables injection.

### F-20 Candidate E conversion omitted Orca filament_flow_ratio — Critical
A naive candidate emitter formula E = volume / filament_area is incomplete.

Orca Extruder.cpp uses:
E_per_mm3 = filament_flow_ratio / filament_crosssection.

Fix: ADR-0010. Capture/validate active filament diameter and flow ratio and use Orca-equivalent conversion for candidate extrusion.

## Final consistency result
After the corrections above:
- one canonical ADR sequence exists: 0001 through 0011;
- normative documents use posSimplifyPath;
- ZAA relative-Z and local-flow semantics are consistent;
- 0.08 mm semantics are effective bead height, not neighbor spacing;
- source boundary and nozzle centerline are separated;
- original structural wall is unchanged in v1;
- machine-coordinate emission requires validated execution-frame translation;
- injected E includes filament_flow_ratio;
- final G-code processing is streaming/all-or-nothing.

No known document-level contradiction remains in the reviewed v1 architecture at this audit point.


### F-21 Export-time resolved settings were not directly revalidated — High
psGCodePostProcess has no live Print object, but Orca's SlicingPipelineContext still exposes config_value(key) from the final full export config.

Without using that API, a plan could theoretically survive a relevant settings change and rely only on G-code/header heuristics.

Fix: ADR-0011. Store a versioned safety-key ExecutionConfigFingerprint at planning and recompute it at export through ctx.config_value(). Any missing/mismatched key disables injection.

### F-22 Plugin Python/dependency floor was not explicit — Medium
Official Orca plugin samples declare requires-python >= 3.12, and geometry bindings rely on NumPy for array access.

Fix: plugin packaging must declare Python >=3.12 for the currently audited runtime and NumPy explicitly. Exact dependency versions are pinned after Phase 0.5 environment verification.
