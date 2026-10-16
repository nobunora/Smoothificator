# Phase 0.5 complete research Plan v2 handoff

Status: SPEC_VALIDATED for the closed research graph and identity scope.

Repository review: the implementation lead independently traced domain values,
the serializer/root dispatcher, hashing and PlanStore. The initial planar-only
loop-context restriction conflicted with ZAA and was corrected to an exact
maximum-path-Z bound. Final recheck found no unresolved schema conflict in this
scope. No production implementation preceded this disposition.

Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `76fe20cb8d7503e576af5bbf2be6697e935f6c01`

## Owning contract and scope

ADR-0067's Closed research Plan v2 graph and identity section owns every field,
reference version, graph rule, projection and outcome. ADR-0062/0064 own the
unchanged byte grammar, hash domain and derived identity construction. The
canonical manifest must be refreshed and its exact Git blob recorded after
review, before implementation. An existing manifest is not authority for this
new section.

Implement the complete immutable research graph, its eighteen-field Plan
content, frozen derived-hash envelope, explicit canonical projection and
dedicated application create/verify boundaries. Reuse existing point, path,
segment, loop, anchor, directional/time evidence and typed identity classes;
do not weaken their validators. Add only the closed wrappers/registries named
by the ADR. No placeholders for engine, Orca or G-code modules.

## Decisions and rationale

Typed region registries make identity/frame/source membership checkable without
pretending referenced topology has been computed. Separate loop chronology binds
existing loop geometry to declared structural intervals without changing its
standalone schema. Segment support wrappers preserve local provenance while
reusing v1 numeric geometry. Explicit adjacent-path transitions make planned
intent and complexity counts inspectable without inferring emitted commands.
Canonical tuple ordering prevents arbitrary registry permutations from becoming
competing semantic encodings. Existing unavailable/error-state evidence permits
incomplete research without numeric sentinels or false successful proof.

Research-only outcomes and existing PlanStore eligibility filtering deliberately
prevent schema work from creating physical authority. The same store accepts
verified v1/v2 artifacts for preview; research v2 is never an execution candidate.
Plan v2 uses a root-context-specific projection and preserves public standalone
semantic_tree rejection for the new vocabulary. It does not change legacy v1
projections or enable runtime validation. Actual geometry, policy/model evidence and physical feasibility
remain owned by later engines/verifiers.

## Required validation

- Frozen exact classes, all required fields and malformed/numeric/version cases.
- Region/frame/source mismatches; missing/extra loop contexts; unsorted/duplicate
  registries; parent cycles; unknown/forward/same-Z/self support; dependency-set
  mismatch; foreign bands/anchors/intervals/layers; missing/extra transitions.
- Directional Settings and available-time execution identities must match Plan.
- Empty research graph, unavailable time and unknown/failed error states remain
  representable only with explicit non-injectable research outcome.
- Independent complete v2 canonical bytes/hash vector, field/leaf sensitivity,
  root/payload version/type mismatch and unknown/missing/extra-field rejection.
- All existing v1 vectors unchanged; legacy v1 create/verify APIs reject v2;
  the existing PlanStore accepts verified v2 for preview but never eligibility;
  no implicit upgrade; other identity domains reject schema 2; supplied wrong
  hash rejects; standalone semantic_tree still rejects the new vocabulary.
- Normal syntax/import, architecture, focused/full regression and package gates;
  independent implementation review and exact-source CI before completion.

## Exclusions and remaining gates

No source mesh/topology algorithm, estimator, optimizer, time predictor,
canonical shape-hash producer, actual insertion matcher, G-code mutation, Orca
adapter, runtime proof issuer, merge or physical release. Schema/graph checks do
not certify real geometry or printer behavior. Runtime validation evidence and
full installed-Orca verification remain separate Phase 0.5/release work; this
handoff must not be reported as completion of those gates.
