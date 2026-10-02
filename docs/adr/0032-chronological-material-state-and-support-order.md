# ADR-0032: Separate final-surface scoring from chronological support state

Status: Accepted
Date: 2026-10-01

## Context

Adaptive Sub-Edge uses material geometry for two different questions:

1. **Final quality** — what the complete part surface looks like after structural and candidate extrusion has finished.
2. **Printability/support** — what material physically exists at the moment a candidate segment is printed.

Those are not the same envelope.

A final-surface model may include the upper structural/ZAA wall and every planned candidate path, but those future beads cannot support an earlier candidate.

Multiple candidate paths also create a potential ordering ambiguity:
- different paths may have different command Z;
- several paths may share one command Z;
- a higher path may physically depend on a lower candidate bead;
- same-Z paths must not form a circular "mutual support" assumption.

Without an explicit chronological model, an optimizer could declare a candidate supported by material that does not exist yet.

## Decision

Maintain two distinct material-state concepts.

### FinalSurfaceEnvelope

Used only for final geometric error / overbuild scoring.

It may include:
- all unchanged structural/ZAA beads;
- every accepted candidate SubEdge bead.

It answers:
"what will the completed local surface look like?"

### ChronologicalSupportEnvelope

Used for support, collision, and printability.

For candidate path/segment execution, it contains only material proven to exist **before that candidate is printed**.

It answers:
"what is physically present under/around the nozzle now?"

## Candidate execution ordering

The plan contains a deterministic candidate execution order.

Primary order:
1. structural interval print order;
2. lower command_z_mm before higher command_z_mm;
3. deterministic stable tie-break for paths with the same command Z.

A support dependency is allowed only from a candidate to material earlier in this execution order.

### Different-Z candidate support

A higher-Z candidate MAY use already-printed lower-Z candidate material as support when the geometric/support model proves sufficient overlap/contact.

### Same-Z candidate paths

Paths at the same command Z MUST NOT rely on material deposited by another same-Z candidate as required vertical support.

For support evaluation of a same-Z group, required support must exist before the group begins, unless a later ADR defines and validates same-height sequential side-support semantics.

Same-Z paths may still be ordered deterministically for execution/collision purposes.

## Support dependency graph

Represent candidate support dependencies explicitly or derive them deterministically.

The graph MUST be acyclic.

Every dependency edge points to:
- pre-existing structural material; or
- a candidate that appears strictly earlier in the execution order.

A candidate whose required support depends on future/ambiguous material is infeasible.

## Temporal structural material

For a candidate inserted between structural layers Z0 and Z1:
- material from completed lower structural history may support it;
- the future upper structural layer at/above Z1 may be included in final-surface scoring;
- that future upper layer MUST NOT be used as support for the candidate.

## Requirements / invariants introduced

- Final-surface scoring and support-state queries use different explicit APIs/types.
- No "future material" can satisfy a support gate.
- Candidate ordering is part of immutable plan intent.
- Candidate support dependencies are acyclic.
- Preview may show both final envelope and chronological support relationship.

## Alternatives considered

- Allow only direct structural support for all v1 candidates: simpler but unnecessarily restricts valid lower-candidate -> higher-candidate support.
- Use the final combined envelope for support: rejected as temporally incorrect.
- Let postprocess choose order: rejected because order affects support/geometry and must already be represented in the immutable plan.

## Safety impact

Critical for preventing unsupported extrusion and hidden dependency cycles.

## Compatibility impact

No Orca API change; this is an engine/plan semantic requirement.

## Performance / resource impact

Requires chronological candidate simulation and support dependency bookkeeping.

## Observability impact

Preview/diagnostics can report:
- candidate execution order;
- support source class;
- dependency path;
- support rejection reason.

## Test / validation impact

Add:
- future upper wall cannot support earlier candidate;
- lower-Z candidate may support higher-Z candidate;
- same-Z mutual-support cycle rejected;
- explicit cycle rejected;
- deterministic same-Z tie ordering;
- final envelope can include future material while support envelope excludes it.

## Migration / rollout

Update domain/engine APIs before implementing support/optimizer logic.

## Rollback / disable condition

Any ambiguous/cyclic support dependency makes the affected candidate set infeasible.

## Open questions

Same-Z sequential side-support could be studied later but is not required for v1.

Supersedes: any ambiguous use of the final combined envelope as a support envelope.
