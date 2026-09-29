# Pre-implementation Dependency and Feasibility Audit

Date: 2026-09-29
Status: Completed before Phase 0.5 implementation.

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

### F-10 Absolute-E restoration was unspecified — High
Added extrusion changes firmware E state.

Fix: parser/emitter handles both relative and absolute E. In absolute mode, injector restores the original logical E coordinate with a validated dialect-supported method (normally G92 E...) before handing control back.

### F-11 Full-file in-memory rewrite does not scale — Medium
Large G-code files can be hundreds of MB.

Fix: two/three-pass streaming design: validation pass -> temp-file emission pass -> sanity pass -> atomic replace.

### F-12 Domain status and immutable plan were conflated — Medium
Injection status changes after planning, but SubEdgePlan is immutable.

Fix: keep plan immutable; store InjectionAttempt/PlanRuntimeStatus separately.

### F-13 Preview/UI lifecycle needed source confirmation — Medium
Confirmed: one plugin may register multiple capabilities; Script capability runs on UI thread; SlicingPipeline runs in slicing workflow. Capability instances live for plugin load.

Fix: shared module-level/application PlanStore, UI-safe Script capability, no live Orca refs.

## Feasibility conclusion
No fundamental blocker remains for a conservative v1 on stock Orca.

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
