# ADR-0025: Validate downstream original Orca motions against injected SubEdge material

Status: Accepted
Date: 2026-09-30

## Context

Injected SubEdge material did not exist when Orca generated the original G-code.

Making the plugin's own travel moves use a high Zsafe is not sufficient.

After the injected block, unchanged original Orca G-code may:
- perform low-Z non-extruding travel;
- print the upper structural outer wall;
- execute ZAA segments locally below nominal layer Z;
- move through XY regions close to a newly added bead.

A candidate can therefore be geometrically useful and internally printable yet create a collision with a later original Orca motion.

The risk is especially relevant to ZAA because upper structural extrusion may contain local negative Z offsets.

## Decision

Printable v1 requires a **DownstreamMotionClearanceValidator** before file mutation.

### Validation domain

For every candidate SubEdge bead set, scan the unchanged original G-code beginning at the planned insertion anchor through a conservative clearance horizon.

Initial v1 horizon:
- at minimum, every original motion in the target upper structural layer;
- continue into subsequent G-code until a validated state is reached where the actual nozzle Z is above the maximum candidate bead envelope by the configured tip-clearance margin and the supported Orca layer/ZAA contract proves no subsequent motion in that print can descend into the candidate clearance envelope.

If that proof is not available, extend validation farther; a full remaining-file scan is permitted.

The validator MUST NOT assume the layer marker itself creates vertical clearance.

### Motion classes

Classify downstream motions into:
- non-extruding XY/travel;
- extrusion motion;
- pure Z motion;
- unsupported/unknown motion.

Unknown motion affecting XYZ/E in the clearance horizon => injection Skipped.

### Candidate material envelope

Use the same finite candidate bead envelope produced by the plan, transformed and quantized into machine execution coordinates.

### Nozzle clearance model

Software cannot infer full physical nozzle/hotend body geometry from current Orca profile data alone.

Therefore define a versioned `NozzleClearanceModel` with two levels:

1. **Required software tip-clearance proxy**
   - based on nozzle centerline, configured nozzle diameter, candidate finite bead envelope, and an explicit conservative vertical/radial clearance margin;
   - used to reject obvious tip/body-interference risks.

2. **Physical-envelope calibration**
   - required before production-quality collision claims;
   - records the tested Bambu nozzle/hotend family and empirical clearance coupon results.

The software proxy is a safety screen, not a proof of arbitrary real hotend-body clearance.

### Non-extruding downstream motion

A non-extruding XY sweep is invalid if the supported nozzle-clearance proxy intersects candidate material at the motion's actual Z.

### Original downstream extrusion

Original extrusion is not automatically considered a collision merely because its deposited/support region overlaps candidate material.

Instead:
- reconstruct the original nozzle centerline/Z;
- compare the swept nozzle-clearance proxy against candidate bead envelope;
- allow intended supported adjacency/overlap only if the finite-bead/nozzle proxy remains within configured clearance rules;
- reject low-Z ZAA/extrusion moves that would drive the nozzle tip/body proxy through previously injected candidate material.

### Order

Downstream-clearance validation occurs after:
- unique structural matching;
- execution-frame resolution;
- quantization;
- final candidate execution derivation;

and before temp-file emission.

## Requirements / invariants introduced

- Candidate-candidate lower-to-higher ordering is necessary but not sufficient.
- Every injectable plan has a downstream-clearance validation result.
- The validator uses final machine-space quantized candidate geometry and actual parsed future G-code motion.
- Unknown downstream motion in the relevant horizon fails closed.
- No document may claim generic physical nozzle-body collision proof from nozzle diameter alone.

## Alternatives considered

- Validate only plugin-inserted travel: rejected.
- Assume higher structural layer is always above candidates: rejected because ZAA may lower local path Z.
- Scan only non-extruding travel: rejected because later extrusion can also intersect candidate material.
- Hard-code one Bambu nozzle body shape without evidence: rejected.

## Safety impact

Critical. Prevents the plugin from creating material that the unchanged slicer-generated future motion was never planned to avoid.

## Compatibility impact

Adds a parser/simulation requirement and keeps physical production claims profile/nozzle-family specific.

## Performance / resource impact

Potentially another streaming future-motion pass. It must remain bounded-memory.

Spatial acceleration for candidate envelope checks may be introduced inside the G-code adapter without changing domain ownership.

## Observability impact

Record:
- downstream horizon;
- motions examined;
- minimum proxy clearance;
- first rejecting motion/segment reason;
- whether physical-envelope calibration exists for the tested nozzle family.

Do not log whole G-code.

## Test / validation impact

Add synthetic/golden fixtures for:
- safe upper-layer motion;
- low-Z ZAA move intersecting candidate -> reject;
- non-extruding low-Z travel crossing candidate -> reject;
- pure Z safe motion;
- unknown motion -> reject;
- full-file fallback horizon;
- candidate that becomes safe after quantization;
- candidate that becomes unsafe after quantization.

Physical coupon tests must deliberately exercise a near-clearance case before collision-safety claims are expanded.

## Migration / rollout

Add:
- `orca_plugin/gcode/downstream_clearance.py`;
- NozzleClearanceModel DTO/config;
- execution-config/plugin-settings fingerprint fields for clearance margins/model version;
- preview diagnostics.

## Rollback / disable condition

If downstream clearance cannot be proven under the supported proxy model, injection is skipped.

## Open questions

The calibrated physical nozzle/hotend swept envelope for each supported Bambu nozzle family remains a Phase 5/6 physical calibration task.

Supersedes: any earlier implication that ADR-0007 safe-ceiling travel alone is sufficient collision validation.
