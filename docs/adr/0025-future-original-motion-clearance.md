# ADR-0025: Validate candidate material against subsequent original Orca motions

Status: Accepted
Date: 2026-09-30

## Context

Adaptive Sub-Edge inserts new material at a layer boundary and then resumes the original Orca G-code unchanged.

Orca planned that later G-code without knowledge of the new candidate beads.

Two collision classes therefore remain even when injected travel itself obeys ADR-0007 safe-ceiling rules:

1. the later original upper structural/ZAA extrusion may locally move the nozzle to a Z below or too close to a previously injected bead;
2. an original Orca travel move may cross the newly added bead at insufficient Z because Orca's travel planner did not know that obstacle existed.

This is especially important in ZAA hybrid mode because upper external-perimeter Z can vary downward within the structural layer.

A "non-crossing SubEdge paths, lower-Z first" invariant only protects candidate-to-candidate ordering. It does not prove candidate-to-future-original-G-code clearance.

## Decision

Printable v1 requires a **FutureOriginalMotionClearanceValidator** in the final G-code validation stage.

After:
- exact plan match;
- execution-frame mapping;
- candidate XYZ/E quantization;

but before any file mutation, the validator MUST compare the predicted quantized candidate material envelope against the subsequent original G-code motions that can geometrically reach it.

At minimum validate:
- original extrusion moves;
- original travel moves;
- ZAA 3D extrusion moves;
- layer/lift transitions;
until the original nozzle is permanently above the candidate obstacle height or the relevant object/layer scope ends.

## Tool clearance model

Physical collision checking requires a pinned `ToolClearanceProfile` for the exact printer/nozzle fixture.

It MUST define a conservative tool/nozzle envelope relative to the nozzle tip, sufficient for the vertical/lateral distances being checked.

The profile may initially be a conservative simple envelope, but its dimensions must come from:
- manufacturer geometry;
- measured hardware;
- or another documented physical source.

Do NOT infer body-clearance dimensions from nominal nozzle-orifice diameter alone.

Without a validated ToolClearanceProfile, analysis and G-code dry-run may proceed but **physical injection is disabled**.

## Candidate material envelope

Use the quantized candidate path plus the v1 finite-bead envelope and configured/calibrated conservative geometry margin.

A future original motion is valid only if the swept ToolClearanceProfile does not intersect the candidate obstacle envelope outside an explicitly supported deposition-contact case.

v1 does not authorize "small intentional nozzle collision/remelting" as a safety mechanism.

## Structural deposition interaction

The future original structural wall is allowed to approach/fuse with candidate material only when:
- its tool-clearance envelope is valid;
- its local nozzle tip Z does not imply a hard collision with the predicted candidate bead;
- the combined nominal bead model remains within geometric error/overbuild limits.

Any uncertain case is non-injectable.

## Requirements / invariants introduced

- Injected-travel safety and resumed-original-G-code safety are separate validations.
- Candidate plans that would obstruct a later original move are skipped.
- ZAA upper-path local Z is included in future-motion validation.
- Travel planning from the original file is never assumed safe merely because Orca generated it.

## Alternatives considered

- Trust Orca travel avoidance: rejected because candidate material did not exist during slicing.
- Require candidate Z below the global minimum future Z: safe but unnecessarily eliminates spatially disjoint candidates.
- Ignore nozzle body and check only XY centerline: rejected for physical safety.

## Safety impact

Critical for hardware collision avoidance.

## Compatibility impact

First physical profile support additionally requires a ToolClearanceProfile.

## Performance / resource impact

Adds a bounded swept-clearance validation over relevant future motions. Spatial indexing may be added later if profiling demonstrates need.

## Observability impact

Report:
- minimum future-motion clearance;
- motion type/location of limiting case;
- ToolClearanceProfile id/version;
- candidate causing rejection.

## Test / validation impact

Add:
- future planar upper wall safely above candidate;
- future ZAA segment dipping into candidate -> rejection;
- original low travel crossing candidate -> rejection;
- spatially distant low-Z motion accepted with validated tool envelope;
- clearance boundary/tolerance tests;
- missing ToolClearanceProfile -> physical gate disabled.

Physical fixture must document the tool-envelope source/measurement.

## Migration / rollout

Add the validator after quantized candidate derivation and before temp-file emission.

## Rollback / disable condition

Unknown tool geometry or unprovable future clearance => Skipped for physical injection.

## Open questions

The first Bambu 0.4 mm ToolClearanceProfile dimensions still require fixture-stage manufacturer/measurement evidence.

Supersedes: any interpretation that injected safe-ceiling travel alone proves total collision safety.
