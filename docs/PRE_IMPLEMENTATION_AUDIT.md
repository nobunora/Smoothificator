# Pre-Implementation Consistency and Feasibility Audit

Date: 2026-09-30
Status: Completed for Phase 0.5 entry

## Scope
Reviewed:
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
- relevant current OrcaSlicer plugin/slicing source

## Critical findings

### F-001 — posContouring is conditional
Severity: Critical
Status: Fixed by ADR-0001

Orca only calls the posContouring plugin hook when need_z_contouring() is true. The old specification promised analysis when ZAA was disabled/ineligible, which was impossible with posContouring alone.

Resolution: move analysis to posSimplifyPath.

### F-002 — ExtrusionPath Z was interpreted ambiguously
Severity: Critical
Status: Fixed by ADR-0003

ContourZ stores path point Z as an offset from layer print_z. Treating it as absolute would shift all ZAA geometry toward zero.

Resolution: canonical adapter conversion to absolute print-space millimeters:
Z_abs = layer.print_z + unscale(point.z).

### F-003 — additive-only sub-edges over-extrude the upper wall
Severity: Critical
Status: Fixed by ADR-0002

Intermediate material reduces the physical gap for the original upper outer-wall pass. Keeping its original full-layer flow is inconsistent.

Resolution: represent refined outer wall as a pass schedule and rescale/rewrite the original upper wall extrusion to the remaining pass height.

### F-004 — v1 local k(s)/z(s) was too broad for safe G-code rewriting
Severity: High
Status: Deferred

Segment-local schedules require splitting and rewriting only portions of a loop while preserving extrusion state.

Resolution: v1 uses one schedule for an entire matched external-wall loop. Local spatial adaptivity is Phase 7+.

### F-005 — multiple/duplicate objects were underspecified
Severity: High
Status: Fixed by ADR-0003

Orca may slice shared duplicate objects once, so object-scoped hooks do not map one-to-one to printed object copies.

Resolution: v1 injection supports one PrintObject / one printable instance. Multi-object support is deferred.

### F-006 — raw source mesh CSG was underspecified
Severity: High
Status: Fixed by ADR-0003

ModelVolume.mesh is local geometry; multi-volume/negative-volume reconstruction requires CSG. The old design implicitly assumed one ideal mesh.

Resolution: v1 injection supports one positive ModelPart volume and explicit transforms.

### F-007 — two package-layout specifications conflicted
Severity: Medium
Status: Fixed

IMPLEMENTATION contained an obsolete flat module list plus the later layered architecture.

Resolution: remove the obsolete layout; ARCHITECTURE is authoritative.

### F-008 — Smoothificator analysis described an obsolete target
Severity: Medium
Status: Fixed

It said the fork's final path generation moved wholly into Orca geometry pipeline.

Resolution: update to geometry-time planning + official psGCodePostProcess execution.

### F-009 — G-code compatibility envelope was too vague
Severity: High
Status: Fixed by ADR-0003

Arc fitting, absolute E, By-object, scarf/fuzzy, other postprocessors and multitool paths create significant ambiguity.

Resolution: reject these for v1 injection. Add explicit gate/reason-code tests.

### F-010 — plan selection at export needed a stricter contract
Severity: High
Status: Fixed

psGCodePostProcess has no live PrintObject. A plan cannot be selected by object pointer/id.

Resolution:
- PlanStore holds immutable candidate plans generated in the current plugin process;
- postprocessor parses the complete file and selects a plan only if exactly one candidate passes all header/config/anchor checks;
- object runtime IDs are diagnostic only and excluded from stable matching/hash;
- zero or multiple matches => no injection.

### F-011 — preview status must not mutate SubEdgePlan
Severity: Medium
Status: Fixed

The plan is immutable, but injection status changes after export.

Resolution: store execution/status records separately from SubEdgePlan. Preview combines immutable plan + status record.

### F-012 — UI capability feasibility
Severity: Resolved/confirmed

Orca plugin packages may register multiple capability classes. Official sandbox examples show Script capability windows via orca.host.ui.create_window. UI stays outside the slicing worker.

### F-013 — hook/cache behavior
Severity: Medium
Status: Guarded

Orca does not re-fire geometry hooks for cache-loaded plugin-final objects. Enabling/changing slicing_pipeline_plugin invalidates posSlice. Export without a matching in-process plan MUST skip injection and instruct re-slice.

## Additional implementation prerequisites

Before any real G-code write:
1. capture golden G-code fixtures from each explicitly supported Orca + printer profile;
2. confirm target fixtures use relative E and absolute XY;
3. confirm arc fitting disabled;
4. identify stable layer/type markers and wall-loop boundaries;
5. implement parser-only dry run and anchor report;
6. prove original bytes unchanged on every failure path.

## No remaining known implementation impossibility
Within the narrowed v1 domain, no source-level blocker was found for:
- reading final post-ZAA/simplified path geometry;
- computing plans in stock Orca;
- plugin-owned preview;
- official psGCodePostProcess working-file modification.

The largest remaining engineering risk is robust G-code matching/state restoration, which is isolated behind the G-code adapter and is explicitly gated before physical printing.


### F-014 — ZAA upper wall is locally non-planar
Severity: Critical
Status: Fixed by ADR-0004

ContourZ may lower perimeter points by varying offsets along one loop. Therefore the remaining height above the highest constant-Z sub-edge is not one scalar h_top.

Resolution: rewrite the original upper wall per matched extrusion segment using local absolute top Z; reject schedules where any segment leaves insufficient printable height.

### F-015 — first-layer/bridge target behavior was unspecified
Severity: High
Status: Fixed

First layer and bridge-role walls have special flow/support semantics.

Resolution: v1 never refines the first printed layer and rejects bridge-role target segments.
