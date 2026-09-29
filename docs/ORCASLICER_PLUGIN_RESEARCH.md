# OrcaSlicer Plugin / Slicing Pipeline Research

Research target: current OrcaSlicer plugin documentation and source architecture as of 2026-09.

## Confirmed plugin direction
OrcaSlicer documents a Python plugin system. Slicing-pipeline plugins can participate at named slicing stages and post-process G-code.

Documented slicing hook names include stages such as:
- posSlice
- posPerimeters
- posPrepareInfill
- posInfill
- posContouring
- posSimplifyPath

The geometry-stage API is the intended target for this project because model/slice geometry is still available before final G-code emission.

## Important maturity note
The slicing-pipeline/plugin surface is comparatively new/experimental. The project must not assume every internal C++ geometry object required by the proposed algorithm is already exposed read/write to Python.

Before production implementation, verify for the exact OrcaSlicer version:
1. object types passed to posSlice/posPerimeters
2. mutability and lifetime of the live slicing graph
3. access to source mesh/model geometry
4. access to layer polygons/perimeters and extrusion attributes
5. whether a plugin can insert new geometry/path nodes, not merely inspect them
6. whether inserted paths flow through standard travel/collision/path ordering
7. serialization/threading constraints
8. plugin packaging/version compatibility

If Python bindings are insufficient, preferred fallback is a small upstream/fork-side Orca C++ extension that exposes the required geometry operation to the plugin. G-code post-processing is a prototype fallback, not the desired final architecture.

## Why geometry stage
Advantages over post-processing:
- true model cross-sections can be queried
- topology is explicit
- no need to reconstruct perimeter correspondence from G-code
- error can be evaluated before committing paths
- intermediate contours can be generated from the source geometry
- Orca can retain responsibility for downstream path planning where APIs permit

## Integration target
Preferred first hook to investigate deeply: posPerimeters, with posSlice as an earlier alternative if intermediate cross-sections must be introduced before perimeter generation.

The correct hook must be selected from actual object capabilities, not hook naming alone.

## References
- OrcaSlicer official GitHub repository and Wiki
- OrcaSlicer plugin development documentation
- OrcaSlicer slicing pipeline/plugin type documentation
- TengerTechnologies/Smoothificator upstream implementation

This document intentionally distinguishes documented API names from capabilities still requiring source-level verification.
