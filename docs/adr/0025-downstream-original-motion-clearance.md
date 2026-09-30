# ADR-0025: Validate downstream original Orca motions against injected bead geometry

Status: Accepted
Date: 2026-09-30

## Context

Adaptive Sub-Edge injects new material that Orca did not know existed when it generated the original G-code.

Making only the plugin's own travel moves use a high Zsafe is not sufficient.

After the injected block, unchanged original Orca G-code may:
- perform low-Z non-extruding travel;
- print the upper structural outer wall;
- execute ZAA segments locally below nominal layer Z;
- move the nozzle/hotend near a newly added bead.

A candidate can therefore be geometrically useful and internally printable yet create a collision with later original Orca motion.

This risk is especially relevant to ZAA because an upper structural extrusion may contain local negative Z offsets.

Current Orca profile data exposes nozzle diameter and machine limits, but not a complete physical nozzle/hotend swept envelope. Generic body-collision safety cannot therefore be inferred from nozzle diameter alone.

## Decision

Printable v1 requires a **DownstreamMotionClearanceValidator** before file mutation.

### Validation domain

For every candidate SubEdge bead set, scan the unchanged original G-code beginning immediately after the planned insertion anchor through a conservative clearance horizon.

Initial v1:
- validate every original motion in the target upper structural layer;
- continue into later G-code while the candidate material and nozzle keep-out vertical ranges may overlap;
- a fixture-specific proof may establish an earlier safe barrier only when the parser can prove that subsequent supported motion cannot descend/intersect the candidate region;
- full remaining-file validation is permitted;
- never shorten the window based only on layer number or nominal layer Z.

If no finite safe barrier can be proven, injection is disabled unless the full remaining supported motion is validated.

### Motion classes

Classify downstream motion as:
- non-extruding XY/travel;
- extrusion motion;
- pure Z motion;
- supported modal/state command;
- unsupported/unknown motion.

Unknown motion that may affect XYZ/E or clearance semantics inside the validation horizon => injection Skipped.

### Candidate material envelope

Use the same finite candidate bead envelope produced by the plan, after:
- execution-frame translation;
- Orca-compatible XYZ quantization;
- final execution-command derivation.

The validator operates on material volume/envelope, not centerlines alone.

### Physical nozzle/hotend keep-out model

Define a versioned `NozzleKeepoutProfile` in plugin settings / compatibility configuration.

For physical injection it MUST provide, at minimum:
- a conservative radial keep-out as a function of vertical distance above the nozzle tip, represented by a piecewise-linear radius profile or an equivalent explicitly documented envelope;
- modeled axial height;
- additional radial safety margin;
- additional vertical safety margin;
- profile id/version and target printer/hotend/nozzle family.

The profile MUST NOT be silently inferred from nozzle diameter alone.

Before first physical injection, the chosen keep-out profile must be:
- explicitly documented in the fixture record;
- reviewed independently;
- validated by conservative clearance coupons/measurement appropriate to the target hardware.

Unknown keep-out geometry => analysis/preview only.

### Motion swept-volume test

For every downstream original motion in the validation horizon:
1. reconstruct the actual machine-space path/state;
2. sweep the versioned nozzle keep-out profile along that motion;
3. test intersection/minimum clearance against all relevant injected bead envelopes;
4. apply configured radial/vertical safety margins.

Printable v1 rejects unsupported arc motion in the validation window through the arc-fitting/unknown-motion gates.

### Non-extruding downstream motion

Any non-extruding original motion whose swept keep-out intersects candidate material is a hard reject.

The plugin MUST NOT rewrite/lift original Orca travel in v1 merely to make a candidate fit.

### Downstream original extrusion

Original extrusion is not automatically safe.

For each downstream extrusion:
- reconstruct actual nozzle centerline/Z;
- test nozzle swept keep-out against candidate material;
- evaluate candidate/original bead interaction with the same finite-bead/support model where the interaction is intentional;
- reject a low-Z ZAA/structural extrusion that drives the nozzle keep-out through candidate material or produces an unsupported/invalid material overlap.

### Order

Downstream clearance is authoritative only after:
- unique structural matching;
- execution-frame resolution;
- Orca-compatible quantization;
- final candidate execution derivation.

It runs before temp-file emission/atomic replacement.

## Requirements / invariants introduced

- Candidate-candidate lower-to-higher ordering is necessary but not sufficient.
- Every injectable plan has a downstream-clearance result.
- Final validation uses quantized machine-space candidate geometry and actual parsed future G-code.
- Unknown relevant downstream motion fails closed.
- Physical nozzle-body safety requires an explicit keep-out profile; nozzle diameter alone is insufficient.
- Original Orca downstream motion is never silently replanned in v1.

## Architecture

Add:
- domain/settings `NozzleKeepoutProfile`;
- `orca_plugin/gcode/downstream_clearance.py`.

The engine may use a simplified compatible keep-out abstraction for early pruning, but the authoritative execution check is in the G-code layer after final matching/quantization.

## Alternatives considered

- Validate only plugin-inserted travel: rejected.
- Assume upper structural layer is always above candidates: rejected because ZAA may lower local path Z.
- Scan only non-extruding travel: rejected because later extrusion can also collide.
- Infer one Bambu nozzle body from nozzle diameter: rejected without hardware evidence.
- Rewrite downstream Orca travel to avoid the candidate: rejected as too invasive for v1.

## Safety impact

Critical. Prevents the plugin from creating material that unchanged Orca motion was never planned to avoid.

## Compatibility impact

Physical v1 requires a declared/validated keep-out profile for the exact hardware fixture.

## Performance / resource impact

Potentially significant.

Use deterministic broad-phase spatial indexing/bounding volumes before exact swept-volume tests while keeping bounded memory.

## Observability impact

Record:
- validation horizon;
- motions examined;
- minimum computed clearance;
- first rejecting original motion index/type;
- keep-out profile id/version;
- applied margins.

Do not log full G-code.

## Test / validation impact

Add fixtures for:
- safe upper-layer motion;
- low-Z ZAA extrusion intersecting candidate -> reject;
- non-extruding travel crossing candidate -> reject;
- pure-Z safe motion;
- near miss within safety margin -> reject;
- missing keep-out profile -> reject for physical mode;
- extended validation beyond immediate upper layer;
- unsupported arc/unknown motion -> reject;
- quantization changing clearance outcome;
- deterministic broad-phase/exact-phase parity.

Physical tests must exercise conservative near-clearance coupons before broader collision-safety claims.

## Migration / rollout

Add downstream clearance as a mandatory final-validation gate before temp emission.

Update:
- Specification;
- Architecture;
- Implementation;
- Plugin Requirements;
- Test Strategy;
- Roadmap;
- physical fixture format;
- plugin settings/config fingerprints.

## Rollback / disable condition

If downstream clearance cannot be proven under the supported keep-out model, return Skipped and leave original G-code unchanged.

## Open questions

A future native-Orca implementation could integrate added material into Orca's own travel/collision planning. v1 remains post-process and therefore validates rather than replans downstream motion.

Supersedes: any earlier implication that ADR-0007 safe-ceiling travel alone establishes complete collision safety.
