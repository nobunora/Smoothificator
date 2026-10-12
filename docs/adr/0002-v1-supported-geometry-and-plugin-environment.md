# ADR-0002: Restrict v1 geometry and plugin environment

Status: Accepted
Date: 2026-09-29

## Context
The source mesh API exposes individual ModelVolume meshes and transforms. It does not expose a single arbitrary-Z cross-section of Orca's fully evaluated multi-volume CSG/modifier result.

Likewise, final G-code may be altered by classic post-processing scripts or other slicing-pipeline plugins after the geometry plan was computed.

Supporting all combinations in v1 would make correctness unverifiable.

## Decision
Printable v1 injection is limited to:

- exactly one printable PrintObject;
- exactly one printable ModelInstance;
- printable injection is further tightened by ADR-0012 to exactly one total source ModelInstance, because Orca centered-frame reconstruction depends on the complete source instance set;
- exactly one ModelPart volume;
- no NegativeVolume;
- no ParameterModifier;
- no multimaterial painting/tool changes;
- single tool/extruder;
- no other active slicing-pipeline capability;
- no classic `post_process` scripts;
- outward/top-facing, non-crossing target geometry;
- a fresh slice generated in the current plugin load.

Transforms are allowed and MUST be handled explicitly. World/model geometry is reconstructed from the bound transforms and validated by coordinate-frame tests.

Analysis-only mode MAY inspect unsupported models but MUST NOT offer printable injection for them.

## Alternatives considered
- Reimplement Orca CSG/modifier slicing in Python: rejected for v1 due correctness and maintenance risk.
- Infer final geometry from G-code only: rejected because it loses source-surface information.
- Allow multiple post-processors and rely only on anchors: rejected for first printable version.

## Safety impact
Strongly reduces false geometry assumptions and cross-plugin mutation risk.

## Compatibility impact
Initial community testing uses simple calibration and single-part models. Scope may be expanded by later ADRs.

## Test impact
Each rejected condition requires an explicit gate/reason-code test.


Expansion: ADR-0012 defines the exact centered-frame reconstruction and stricter total-instance rule.
