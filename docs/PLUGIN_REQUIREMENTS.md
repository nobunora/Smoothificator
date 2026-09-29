# Plugin Requirements and Compatibility

## Minimum Orca requirement
The project targets OrcaSlicer builds containing the Python Plugin System and SlicingPipeline API.

Official documentation currently states:
- Nightly builds, or
- releases greater than 2.4.2.

Because SlicingPipeline is experimental, exact supported Orca versions must be pinned per plugin release.

## Stock-Orca capability today
A stock compatible Orca can run a read-only/research version that:
- reads source mesh/model data
- reads layers and surfaces
- reads 3D extrusion paths after ZAA
- reads width/height/flow
- computes residual error
- computes and visualizes/logs proposed sub-edges

It cannot currently inject arbitrary-Z new extrusion paths using the public Python API.

## Requirement for working Sub-Edge printing
One of the following must be true:

### Preferred
Orca upstream exposes a safe sub-edge/path insertion binding.

### Development
Use a custom Orca build containing this repository's small C++/pybind extension.

### Not preferred
Post-process final G-code. This remains a debugging fallback only and is not the target architecture.

## Required binding behavior
The extension must:
- accept copied Python path specifications
- validate geometry and extrusion parameters
- insert paths into an Orca-owned graph
- preserve preview/export
- maintain required caches/invariants
- preserve deterministic lower-Z-first grouping
- reject invalid stages
- fail atomically

## Plugin package
Target: pure-Python wheel.

Why:
- project is multi-module
- easier version/dependency metadata
- avoids platform-specific native Python wheels
- native mutation belongs in Orca's C++ API, not a hidden second ABI layer

## Runtime checks
At plugin start:
1. verify Orca version
2. verify SlicingPipeline API
3. verify required insertion binding and version
4. inspect ZAA state
5. verify required geometry attributes
6. if injection unavailable, enter analysis-only mode rather than modifying G-code

## First supported print domain
- 0.4 mm nozzle
- PLA calibration profile
- outward/top-facing slopes
- non-crossing sub-edges
- default min adjacent Z spacing 0.08 mm
- no downward-facing reconstruction
- ZAA-first when applicable

## Compatibility philosophy
Never silently approximate a missing capability. If an Orca update changes graph semantics or invalidates the insertion API, disable modification and report incompatibility.
