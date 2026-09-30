# ADR-0003: Restrict v1 to a deliberately narrow printable domain

Status: Accepted
Date: 2026-09-30

## Context
Source audit found several cases that substantially increase matching and safety complexity:
- duplicate/shared PrintObjects do not receive every object-scoped slicing hook independently;
- source ModelVolume meshes are local-coordinate components requiring CSG handling for multi-volume/negative-volume objects;
- By-object printing changes execution ordering;
- arc fitting changes G-code geometry representation;
- absolute extrusion makes local original-wall E rewriting much more invasive;
- scarf/fuzzy/multitool features alter wall/path semantics;
- another post-processing plugin may mutate G-code between geometry analysis and injection.

The first printable proof-of-concept should validate the surface-reconstruction idea, not solve all Orca features at once.

## Decision
v1 printable injection supports only:
- exactly one printable PrintObject;
- exactly one printable instance;
- exactly one positive ModelPart volume;
- no negative/modifier/support-enforcer/support-blocker volumes;
- single tool/extruder;
- print sequence By Layer;
- relative extrusion mode in the target G-code;
- absolute XY positioning in target intervals;
- arc fitting disabled;
- scarf/seam-slope features disabled;
- fuzzy skin disabled;
- spiral/vase mode disabled;
- no classic post-processing scripts;
- no other active G-code/geometry-mutating slicing-pipeline plugin;
- outward/top-facing, non-crossing external-wall loops;
- no support-dependent refined region.

Unsupported cases remain analyzable where safe, but **injection MUST be disabled**.

## Coordinate frame
Domain geometry uses **absolute print-space millimeters**.

Orca ExtrusionPath point Z is a layer-relative contour offset, not absolute print Z. Adapter conversion is:

Z_abs = Layer.print_z + unscale(path_point.z)

Source mesh vertices are transformed from volume-local to print space using the audited Orca transforms before analysis.

## Alternatives considered
Supporting all objects/features from the first release was rejected because failures would be difficult to attribute and community testing would be unsafe.

## Safety impact
Significantly reduces ambiguity in plan/G-code matching and execution.

## Compatibility impact
Many ordinary models can still be analyzed, but printable injection is intentionally limited to calibration coupons/simple one-part models in v1.

## Test impact
Every rejected feature requires a gate test with a stable reason code.

## Migration
Expand one capability at a time only after dedicated tests and, where required, ADR review.

Supersedes: none.
