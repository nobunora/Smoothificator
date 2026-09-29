# Adaptive Sub-Edge Surface Reconstruction — Specification

## Product goal
Use stock OrcaSlicer + Python plugin only.

Use Orca/ZAA first, inspect finalized simplified 3D extrusion geometry, measure residual surface error, and add only the minimum extra surface paths/material needed to improve quality.

## Canonical flow
fresh slice
-> ZAA if applicable
-> Orca path simplification
-> posSimplifyPath Analyzer
-> immutable SubEdgePlan
-> plugin Preview
-> normal Orca G-code
-> psGCodePostProcess validated Injection
-> output

No custom Orca build is required for v1.

## Fresh-slice rule
posSimplifyPath does not re-fire for Orca cache-loaded plugin-final objects.

Printable Injection requires a matching plan created by a fresh slice in the current plugin load.

No plan => Injection skipped, original G-code unchanged.

## Printable v1 scope
- one printable object
- one printable instance
- one ModelPart volume
- no negative/modifier volumes
- single material/tool
- no other slicing-pipeline capability
- classic post_process empty
- supported current Bambu 0.4 profile family
- relative E
- firmware retract off
- arc fitting off
- line numbering off
- spiral vase off
- ironing off
- scarf seam off
- support/raft off
- validated coordinate frame
- nested top-facing target geometry
- validated nozzle-envelope parameters before physical print

Broader models may be analyzed but not injected.

## ZAA baseline semantics
Analyzer consumes actual post-ZAA/post-simplification paths.

Orca path-point ZAA Z is a relative offset d:
z_abs = layer.print_z + d

For non-ironing ZAA:
h_eff = layer/path height + d
q_eff = q_nominal * h_eff / h_nominal

Adapter normalizes these before domain analysis.

## Sub-edge height semantics
0.08 mm is the initial minimum **effective bead height above local supporting surface** for the 0.4 mm target.

It is NOT a mandatory minimum Z difference between neighboring Sub-edge paths.

Multiple paths may have closely spaced nozzle Z values if finite-bead and nozzle-clearance validation passes.

## Geometry semantics
A source mesh cross-section is a material boundary, not a nozzle centerline.

Candidate paths are laid out on the material side using bead width/support geometry and are judged by the final deposited envelope.

Printable v1 requires higher-Z material cross-sections to be nested inside lower-Z cross-sections.

## Material model
Score the final combined surface:
- lower structural/post-ZAA material
- candidate Sub-edge material
- unchanged upper structural/post-ZAA material

Path flow is part of optimization.

Overfill is error, not free smoothing.

## Ordering
Accepted paths are non-crossing.

Primary order is lower nozzle Z -> higher nozzle Z.

Pairwise Z spacing is governed by actual nozzle/bead clearance, not a fixed pitch.

## G-code Injection
For supported Bambu v1, Injection occurs at a validated upper structural-layer boundary after Orca has completed its layer-Z transition and supported motion-neutral layer-change block.

Every non-extruding Sub-edge travel:
- raises to a safe ceiling
- moves XY only at that ceiling
- descends vertically at the path start

After final path, Injector returns to the exact saved layer-boundary state before resuming Orca G-code.

Unknown custom layer-change motion => skip.

## Plan/Preview identity
One immutable plan is the source for:
- preview
- metrics
- injection

Runtime Injection status is separate from plan hash.

## Injection safety
- parser/state-machine based
- structural layer tags, not arbitrary Z moves
- exact-one plan match
- all anchors validated before writing
- relative-E v1 only
- streaming temp-file output
- sanity parse
- atomic replacement
- idempotent markers
- no partial Injection
- any ambiguity preserves original Orca output

## Architecture
ARCHITECTURE.md and Accepted ADRs are normative.

Any safety/scope relaxation requires an ADR before code changes.
