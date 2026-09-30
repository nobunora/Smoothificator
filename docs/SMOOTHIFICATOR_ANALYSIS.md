# Smoothificator Upstream Analysis

Upstream: TengerTechnologies/Smoothificator

## Upstream behavior
Original Smoothificator post-processes G-code:
- finds external-wall blocks;
- chooses equal vertical pass count;
- repeats the same XY loop at those Z values;
- divides original outer-wall extrusion among passes.

Adaptive variant chooses integer pass count from current layer height.

## What this fork keeps conceptually
- outer-surface vertical resolution can differ from the interior;
- multiple external paths can be introduced without globally reducing layer height;
- G-code post-processing can be used with stock Orca.

## What this fork changes
Geometry decisions move earlier, while source mesh and final simplified Orca/ZAA paths are still available.

Canonical flow:
final simplified structural geometry -> residual error -> surface band -> optimized candidate centerlines/flow -> immutable plan -> final G-code validated injection.

## Important difference: flow
Upstream redistributes the original wall extrusion among repeated passes.

This fork v1 does **not** rewrite the original structural wall.

Instead:
- original lower/upper structural/ZAA beads remain in the final-surface model;
- candidate SubEdge bead flow is optimized;
- combined finite-bead overfill/underfill is scored explicitly.

A future structural-wall redistribution mode would require its own ADR and tests.

## Important difference: geometry
Upstream repeats identical XY.

This fork:
- treats source mesh section as material boundary;
- derives printable centerlines inside the material;
- may create multiple paths at same/different Z, while each printable v1 path itself stays constant-Z;
- uses local support/nesting;
- does not assume equal 1/2 or 1/3 pitch.

## Execution
Legacy scripts use regex/block logic.

New injector uses:
- geometry-time immutable plan;
- stateful streaming G-code parser;
- seam-invariant structural matching and execution-frame translation;
- Orca-compatible quantization;
- validated Bambu structural-layer boundary;
- exact parsed retraction/state restoration;
- safe-ceiling travel;
- downstream original-motion clearance against a versioned ToolClearanceProfile;
- relative-E candidate emission;
- atomic temp-file replacement.

## Code reuse
Keep legacy Smoothificator.py and Smoothificator_Adaptive.py unchanged as reference/baseline.

Do not extend their parser architecture for the new engine unless explicitly tasked.
