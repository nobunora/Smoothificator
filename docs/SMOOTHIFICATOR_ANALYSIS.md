# Smoothificator Upstream Analysis

Upstream: TengerTechnologies/Smoothificator

## Current behavior
The original Smoothificator is a G-code post-processing script. It identifies external-perimeter/outer-wall blocks and repeats them at additional Z values.

The fixed-height version:
- reads base layer height from G-code comments
- computes a pass count from base height / requested outer height
- divides the base height evenly
- duplicates the same XY outer-wall path
- divides extrusion by pass count
- inserts explicit Z and return-to-start travel moves

The adaptive version additionally:
- reads ;LAYER_CHANGE and ;HEIGHT
- reads min_layer_height when no explicit target is supplied
- evaluates floor/ceil integer pass counts
- selects the equal pass height closest to the requested target

## Limitations relative to this fork's target
1. It operates after geometry/path generation.
2. It does not measure error against the source model.
3. Added Z positions are equally spaced.
4. Repeated passes use the same XY contour.
5. It does not reconstruct the true intermediate model contour.
6. It has no finite-bead geometric optimizer.
7. It does not perform general 3D nozzle-clearance analysis.
8. Print-time/quality tradeoff is implicit rather than optimized.

## What this fork changes
The fork keeps Smoothificator as its conceptual and licensing starting point but moves the target architecture upstream into OrcaSlicer's slicing geometry pipeline.

The defining change is:

Legacy:
target outer layer height -> integer equal passes -> duplicate XY path

New:
model-vs-baseline error -> optimize arbitrary intermediate Z contours -> extract local surface-only sub-edges -> validate -> normal path generation
