# Phase 0.5 analysis evidence and bounded Attempt history

Status: SPEC_VALIDATED for the bounded evidence/history slice; see
docs/implementation/evidence-history-review-2026-10-16.md. No release/merge approval.

## Canonical Contract

ADR-0067 closed analysis-evidence/bounded-history section owns exact contracts.
ADR-0037/0065 own Attempt lifecycle and atomic issuance. ADR-0066's initial time
model remains unavailable_v1. The refreshed 83-blob manifest is
docs/AUDIT_REVISION_2026-10-16.json; Manifest Git blob: `7c0e2b4787f9cb6df8f62786ea2c9bc3d1dc9688`

## Goal

Represent missing time and directional convergence without misleading numeric
sentinels, and optionally bound Attempt records/history without losing active work.

## Scope

Four standalone frozen evidence DTOs; runtime-only AttemptRevision; opt-in
retention in the existing InjectionAttemptStore. Tests exercise required values,
malformed tags/types, two-direction distinction, pruning, failed-begin atomicity,
duplicate UUID, concurrency and PlanStore issuance rollback.

## Non-goals

Full Plan v2 projection, SurfaceBand/loop/anchor references, actual estimator,
time model, canonical registration of evidence, verifier-generated VALIDATED
proof, new snapshot issuance IDs, G-code/Orca behavior, physical printing, release.

## Requirements / Invariants

Follow exact ADR-0067 fields, states and retention rules. Reuse existing identity
and directional metric DTOs. Domain never imports application or Orca. Evidence
strings/DTO construction never prove safety. No change to v1 canonical vectors.
Retained immutable records and history remain independent for every attempt.
New bounded mode is explicitly configured; zero-argument legacy callers retain
existing behavior. No active eviction, unbounded history or second state owner.

## Acceptance Criteria

Unknown time cannot be supplied as a bare numeric placeholder or mixed variant.
Unknown/failed convergence cannot masquerade as converged. Both directional
policies match. Canonical serializer rejects these standalone evidence objects
and runtime revisions. Capacity handling, revision numbering and failed-operation
atomicity pass deterministic and concurrent tests; old lifecycle tests still pass.

## Validation

Python 3.12 compile/import, architecture checks, focused evidence/history tests,
unchanged v1 golden suite, complete regression and package build. Independent
schema and implementation review. CI must match the last source commit.

## Risks / Rollback

Schema vocabulary is not estimator/fixture proof. Legacy mode remains unbounded
for backward compatibility and must not be described as bounded; new integrations
should explicitly select capacities. Bounded mode may reject a new attempt when
all slots are active; caller preserves G-code. No external state migration occurs.
