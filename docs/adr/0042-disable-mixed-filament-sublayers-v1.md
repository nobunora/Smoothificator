# ADR-0042: Disable mixed-filament sublayer emission for printable v1

Status: Accepted
Date: 2026-10-08

## Context

Current OrcaSlicer main (audited at `7d44b60ae4042b4de8c3844eb9dd2671c2d2d873`) contains mixed-filament sublayer emission.

In `GCode.cpp`, mixed filament groups may temporarily change:
- `m_nominal_z`;
- `m_sub_layer_flow_ratio`;
- `m_sub_layer_height`;

and emit structural geometry at sub-Z values with scaled flow.

Adaptive Sub-Edge v1 assumes the surrounding structural layer/ZAA baseline is the ordinary one-tool / one-filament path family represented by its current geometry/final-deposition contracts.

The mixed-sublayer path is a materially different execution model and must not be inherited implicitly.

## Decision

Printable v1 requires that no mixed-filament slot/sublayer behavior is active.

At minimum, the resolved export configuration must prove:
- all `filament_is_mixed` values are false;
- no active mixed-component slot is referenced;
- mixed-sublayer/gradient definitions do not participate in the target print.

Relevant mixed-filament project keys are included in ExecutionConfigFingerprint for the pinned Orca family, including as applicable:
- `filament_is_mixed`;
- `filament_mixed_components`;
- `filament_mixed_sublayer_ratios`;
- `filament_mixed_gradient`;
- `filament_mixed_gradient_range`;
- `filament_mixed_gradient_curve`;
- `filament_mixed_gradient_per_part`.

The final G-code validator also rejects any fixture/output pattern identified by the pinned compatibility descriptor as mixed-sublayer emission.

Analysis/preview may continue, but injection is disabled.

## Requirements / invariants introduced

- "one tool / one filament execution context" is not considered sufficient unless mixed virtual filament features are also disabled.
- v1 does not model Orca `m_sub_layer_flow_ratio` or mixed sub-Z structural emission.
- Future support requires dedicated source/fixture parity.

## Safety impact

High for Z/flow correctness.

## Test impact

Add:
- all mixed flags false -> eligible;
- any `filament_is_mixed=true` -> reject;
- mixed gradient/sublayer fixture -> reject;
- fingerprint mismatch when mixed settings change.

## Rollback / disable condition

Unknown mixed-filament semantics => no injection.
