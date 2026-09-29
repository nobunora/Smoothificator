# Smoothificator Upstream Analysis

Upstream: TengerTechnologies/Smoothificator

## Upstream behavior
Smoothificator is a final-G-code post-processing script. It detects external perimeter/outer-wall blocks and repeats the same XY path at additional equally spaced Z values, dividing extrusion among passes.

Adaptive variant chooses an integer equal subdivision closest to requested outer-wall height.

## Useful inheritance
This fork retains:
- GPL lineage
- proof that post-generated G-code can be altered for outer-wall refinement
- Orca/Prusa marker knowledge
- baseline tests/concepts for outer-only refinement

## What is NOT reused as architecture
- regex-driven geometry decisions
- identical XY repeated at equal Z
- target fixed outer layer height
- pass-count-only optimization
- G-code as the source of geometric truth

## Current fork architecture
Geometry decisions happen while source mesh and finalized post-ZAA/post-simplification paths are available at Orca posSimplifyPath.

The resulting immutable SubEdgePlan is later translated into final G-code at psGCodePostProcess.

Therefore the architecture is hybrid:

source mesh + Orca toolpath -> error/optimization -> immutable plan
final G-code + matching plan -> validated execution

G-code post-processing is execution only, not geometry inference.

## Major additional difference
Added sub-edges are extra material. The optimizer includes lower/upper structural beads and candidate flow in a finite-bead final-surface model to prevent naive overfill.
