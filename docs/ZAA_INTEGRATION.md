# ZAA Integration Strategy

## 1. Role of ZAA
Orca Z Contouring/ZAA is the first low-cost improvement stage.

Adaptive Sub-Edge reads the final simplified structural paths after ZAA has had a chance to act. It does not reproduce ZAA itself.

## 2. Analyzer hook
Use posSimplifyPath.

posContouring is conditional on Orca deciding Z contouring is needed and therefore is not sufficient for a general analyzer.

## 3. ZAA Z semantics
ContourZ stores path point Z as layer-relative offset d.

Adapter reconstructs:
Z_abs = layer.print_z + unscale(d)

Engine only receives absolute print-space Z.

## 4. ZAA flow semantics
Orca GCode.cpp emits Z-contoured non-ironing extrusion with:

extrusion_ratio = (path.height + d) / path.height

Therefore local effective flow is:
effective_mm3_per_mm = path.mm3_per_mm * extrusion_ratio

Baseline prediction MUST use this local variation.

Treating ZAA path mm3_per_mm as spatially constant is incorrect.

## 5. Hybrid workflow
1. Orca slice/perimeters.
2. ZAA where Orca applies it.
3. Orca path simplification.
4. posSimplifyPath snapshot.
5. Normalize absolute Z and local effective flow.
6. Predict existing finite-bead surface.
7. Measure residual error.
8. Derive residual surface bands.
9. Add candidate SubEdge beads only where useful.
10. Score final combined surface including unchanged structural/ZAA beads.
11. Export normal Orca G-code.
12. Add planned SubEdge G-code at validated layer boundaries.

## 6. What SubEdge adds
ZAA changes existing path Z/flow within Orca's existing topology.

Adaptive Sub-Edge can add new printable centerlines to cover material/surface bands unavailable to the existing path topology.

Candidate paths can be:
- same-Z neighbors;
- different-Z neighbors;
- several paths across one shallow terrace.

## 7. No structural-wall rewrite in v1
The original ZAA/structural wall remains exactly Orca's path.

Overbuild risk is controlled by:
- optimizing candidate width/height/flow;
- predicting the final combined bead envelope;
- rejecting candidates that exceed error/overbuild limits.

This is intentionally simpler and safer for stock-Orca post-process testing than rewriting existing G-code extrusion.

## 8. Minimum bead-height rule
0.08 mm initial value applies to candidate effective bead height above local support.

It is not a mandatory difference between candidate nozzle Z values.

## 9. Collision/travel distinction
Candidate extrusion paths are generated only in nested/self-supported regions.

Execution uses safe-ceiling non-extruding travel per ADR-0007.

No low-Z lateral travel between candidates in printable v1.

## 10. Success criterion
Benchmark:
- normal
- fine conventional layer
- ZAA-only
- ZAA + Adaptive Sub-Edge

Primary target:
Where ZAA-only misses requested surface tolerance, ZAA + SubEdge should improve error with less time penalty than globally using a fine layer height.
