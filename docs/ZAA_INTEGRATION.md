# ZAA Integration Strategy

## 1. Role

Orca Z Contouring/ZAA remains the first low-cost surface-improvement stage.

Adaptive Sub-Edge reads the final simplified structural geometry after ZAA has run when applicable. It does not reproduce or replace ZAA.

## 2. Analysis point

Use `posSimplifyPath`.

`posContouring` is unsuitable as the general analyzer because it is conditional on Orca deciding that contouring is needed and it occurs before final path simplification.

## 3. Z semantics

ContourZ stores each path point's Z component as relative offset (d).

Adapter reconstructs:

[
Z_{abs}=Layer.print_z+d
]

after unscale conversion.

Domain/engine uses absolute centered-slice Z only.

## 4. Local ZAA geometric-volume semantics

Audited Orca G-code applies:

[
r_{zaa}=rac{path.height+d}{path.height}
]

for non-ironing Z-contoured segment extrusion.

For nominal geometry modeling, this local ZAA ratio is paired with local effective height (path.height+d).

It is distinct from global user/material calibration multipliers such as filament_flow_ratio.

## 5. Global commanded-flow semantics

Commanded G-code material additionally includes Orca's global/external-wall flow modifiers per ADR-0015.

These affect E generation and volumetric-speed limits.

They do not directly redefine the ideal nominal bead geometry in v1; empirical physical correction is deferred per ADR-0022.

## 6. Hybrid workflow

1. normal Orca slice/perimeters;
2. ZAA if Orca applies it;
3. Orca path simplification;
4. `posSimplifyPath` centered-frame snapshot;
5. normalize local ZAA Z + geometry-directed volume;
6. build nominal finite-bead baseline;
7. evaluate residual surface-normal error;
8. derive printable residual surface bands;
9. plan additional SubEdge centerlines/segment flow;
10. score structural + candidate nominal bead envelope;
11. export normal Orca G-code;
12. validate final execution config/state/structural matching;
13. inject only the immutable candidate plan.

## 7. Different solution spaces

ZAA:
- changes existing path Z;
- retains existing topology;
- locally scales extrusion for the altered height;
- very low time/material overhead.

Adaptive Sub-Edge:
- adds new centerlines where existing topology cannot represent the desired surface;
- may place several paths at the same/different Z;
- uses explicit residual-error/support model;
- incurs additional time/material.

## 8. Structural G-code remains unchanged

Printable v1 does not rewrite the original ZAA/structural wall.

Candidate flow is optimized so the combined nominal finite-bead surface does not create unacceptable overbuild.

## 9. 0.08 mm rule

Initial 0.08 mm applies to candidate effective bead height above local support.

It is not a required difference between neighboring path Z coordinates.

## 10. Matching ZAA paths to final G-code

ZAA geometry is still subject to normal seam processing before final G-code.

Final structural matching therefore follows ADR-0016:
- seam start invariant;
- subdivision invariant;
- configured seam-gap allowance;
- no raw ordered-point equality.

## 11. Benchmark question

Compare:
- conventional normal layer;
- conventional fine layer;
- ZAA-only;
- ZAA + Adaptive Sub-Edge.

Target claim to test:

Where ZAA-only exceeds the requested surface-error tolerance, Adaptive Sub-Edge can reduce that residual error with less global time cost than reducing layer height everywhere.

This remains a hypothesis until simulation and physical benchmarks support it.
