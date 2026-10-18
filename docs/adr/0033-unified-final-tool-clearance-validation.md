# ADR-0033: Validate plugin-generated and resumed-original motions with one chronological tool-clearance model

Status: Accepted
Date: 2026-10-01

## Context

ADR-0025 closes the important risk that unchanged downstream Orca motion was generated without injected SubEdge material.

A second related risk remains if the same physical ToolClearanceProfile is not applied to the plugin's own motions:
- vertical descent to a candidate start can bring the nozzle/hotend body near existing structural material;
- candidate extrusion can pass near adjacent structural/candidate beads;
- vertical lift at the end can pass near nearby geometry;
- later plugin candidate travel can collide with earlier injected candidates.

"All non-extruding XY occurs at Zsafe" protects lateral travel but is not a complete swept-volume proof for vertical and extrusion motion.

## Decision

Before file mutation, run one chronological **FinalToolClearanceValidator** over the complete planned execution schedule relevant to each injection interval.

It validates BOTH:

1. plugin-generated motions; and
2. unchanged original Orca motions after each injected block,

against the material that physically exists at each point in time.

## Chronological material state

Use ADR-0032 ChronologicalSupportEnvelope / printed-material state.

As simulation advances:
- existing structural material is present according to original print order;
- a candidate bead is added only after its candidate extrusion move completes;
- later plugin/original motions are checked against that newly present material;
- future structural/candidate material is not treated as an obstacle before it is printed.

## Plugin-generated motion validation

Validate ToolClearanceProfile swept volume for:
- vertical raise to Zsafe;
- XY travel at Zsafe;
- vertical descent to candidate start;
- candidate extrusion path;
- vertical lift after candidate;
- return-to-saved-state motion;
- later plugin candidate motion.

### Intended deposition contact

Candidate extrusion necessarily creates/contact-supports material at the nozzle tip.

The validator distinguishes:
- the intentional deposition/support contact zone represented by the finite-bead model; from
- forbidden intersection of the non-deposition nozzle/hotend keep-out envelope with already printed material.

No arbitrary nozzle-body rubbing/remelting is permitted.

If the ToolClearanceProfile cannot express this distinction conservatively for the target hardware, physical injection is disabled.

## Resumed original motion validation

Retain ADR-0025 requirements:
- validate downstream travel;
- validate downstream extrusion including lowered ZAA paths;
- continue until a conservative safe barrier or full relevant remainder is proven;
- unknown motion fails closed.

## ToolClearanceProfile

One versioned profile is authoritative for both plugin and downstream validation.

Its physical source/evidence and safety margins remain part of fixture/review requirements.

## Requirements / invariants introduced

- Safe-ceiling travel alone is not considered complete plugin-motion collision proof.
- Final clearance validation is chronological.
- Earlier injected candidate material is an obstacle for later plugin/original motion.
- Future not-yet-printed material is not an obstacle.
- Intentional deposition contact is narrow and explicit; nozzle-body collision remains forbidden.
- Final validation consumes the immutable plan and may only accept/reject, not replan.

## Architecture

Add/rename the final execution validator to:
`orca_plugin/gcode/tool_clearance.py`

It composes:
- ToolClearanceProfile;
- quantized plugin motion schedule;
- parsed original motion schedule;
- chronological material state.

The narrower downstream-only implementation may remain as an internal helper but is not the authoritative physical clearance decision.

## Alternatives considered

- Trust geometry-engine nozzle clearance for plugin motions: rejected because final machine mapping/quantization and physical ToolClearanceProfile are only fully known at execution validation.
- Check downstream original motion only: incomplete.
- Replan unsafe plugin motion in postprocess: rejected; immutable plan/execution contract permits acceptance or rejection only.

## Safety impact

Critical.

## Compatibility impact

Physical v1 remains hardware-fixture specific.

## Performance / resource impact

Adds chronological swept-volume checks for plugin motions, but plugin motion count is bounded by the plan.

## Observability impact

Report:
- minimum plugin-motion clearance;
- minimum resumed-original-motion clearance;
- rejecting motion class/index;
- ToolClearanceProfile id/version;
- whether rejection occurred before or after candidate material deposition.

## Test / validation impact

Add:
- vertical descent near adjacent wall -> reject;
- safe descent -> accept;
- candidate extrusion body-envelope collision -> reject;
- later candidate colliding with earlier candidate -> reject;
- Zsafe XY travel clear -> accept;
- downstream Orca collision tests from ADR-0025;
- intentional tip deposition contact does not self-reject;
- future material not incorrectly treated as already present.

## Migration / rollout

Update Specification, Architecture, Implementation, Plugin Requirements, Test Strategy, and Roadmap.

## Rollback / disable condition

If chronological physical clearance cannot be proven, return Skipped and preserve original G-code.

## Open questions

More detailed empirical hotend/body thermal-contact models are out of v1 scope.

Supersedes: any interpretation that ADR-0025 downstream-only validation or ADR-0007 Zsafe travel alone is sufficient for complete final tool-clearance validation.
