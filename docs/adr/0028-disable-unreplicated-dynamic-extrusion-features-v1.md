# ADR-0028: Disable v1 features whose runtime extrusion behavior is not reproduced by the injector

Status: Accepted
Date: 2026-09-30

## Context

Injected SubEdge extrusion bypasses Orca's normal path-generation/extrusion pipeline.

Two current features materially change geometry/execution in ways not reproduced by the first injector:

1. **Fuzzy skin**
   - intentionally perturbs wall geometry;
   - would make residual source-surface error intentional rather than a defect.

2. **Filament adaptive volumetric speed**
   - Orca may reduce max volumetric speed using height/width-dependent coefficients;
   - the initial injector only reproduces the fixed filament max-volumetric limit.

Trying to silently ignore either feature would make planning/execution diverge from Orca semantics.

## Decision

Printable v1 requires:
- fuzzy skin disabled for the target object/region;
- `filament_adaptive_volumetric_speed=false`.

The ExecutionConfigFingerprint includes the relevant resolved settings.

Analysis may still report why the configuration is non-injectable.

## Requirements / invariants introduced

- No attempt is made to "correct" intentional fuzzy-skin displacement.
- Candidate speed limiting uses fixed validated filament max volumetric speed in v1.
- Nonzero adaptive-volumetric coefficients are diagnostic only while the feature is disabled.

## Alternatives considered

- Reimplement fuzzy-skin intent-aware source target: deferred.
- Reimplement Orca adaptive volumetric-speed polynomial immediately: unnecessary for first PoC.

## Safety impact

High for geometry intent and extrusion-rate parity.

## Compatibility impact

Some standard/custom profiles require a user-visible settings change before injection.

## Performance / resource impact

Simplifies v1 execution.

## Observability impact

Preview reports the specific disabled-feature requirement.

## Test / validation impact

Add fuzzy-skin rejection and adaptive-volumetric-speed rejection fixtures.

## Migration / rollout

Add both to config fingerprint and compatibility gates.

## Rollback / disable condition

None.

## Open questions

Future support requires separate parity tests/ADR.

Supersedes: none.
