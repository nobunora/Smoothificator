# ADR-0024: Exclude first-layer SubEdge refinement from printable v1

Status: Accepted
Date: 2026-09-30

## Context

The first printed layer has materially different geometry and extrusion behavior:
- bed-contact squish/support differs from ordinary inter-layer support;
- elephant-foot/first-layer geometry corrections may affect the final boundary;
- Orca may apply `first_layer_flow_ratio` in its flow chain;
- first-layer speeds/acceleration/temperatures differ;
- safe candidate travel near the build plate has a different collision envelope.

The v1 error/support/bead model is designed for material supported by previously deposited model material, not the build plate.

## Decision

Printable v1 MUST NOT create or inject SubEdge paths whose support interval is the first printed/model layer.

The analyzer may calculate diagnostic error for first-layer geometry, but any candidate region touching the first-layer refinement domain is marked non-injectable with a stable reason code.

The first printable SubEdge interval begins only after at least one ordinary structural model layer exists below the candidate support.

## Requirements / invariants introduced

- No first-layer flow/squish model is required by v1.
- `first_layer_flow_ratio` remains part of compatibility diagnostics where useful but does not need to be implemented for candidate E because first-layer candidates are forbidden.
- Physical fixture tests begin above the first-layer region.

## Alternatives considered

- Implement first-layer flow and build-plate support immediately: rejected as outside the initial surface-staircase goal.
- Treat build plate as an ordinary support envelope: rejected as physically inaccurate.

## Safety impact

Reduces nozzle/bed and adhesion risk.

## Compatibility impact

Small first-layer-only geometry is analysis-only.

## Performance / resource impact

None.

## Observability impact

Preview marks excluded first-layer regions with a specific gate reason.

## Test / validation impact

Add:
- first-layer target rejection;
- second/upper-layer candidate acceptance when all other gates pass.

## Migration / rollout

Add the gate to geometry eligibility and fixture requirements.

## Rollback / disable condition

None.

## Open questions

First-layer reconstruction may be studied only under a later dedicated physical-model ADR.

Supersedes: none.
