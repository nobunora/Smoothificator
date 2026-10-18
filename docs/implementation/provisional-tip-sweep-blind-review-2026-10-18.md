# Provisional planar-tip pair classifier independent blind review

Date:2026-10-18. Read-only review of `tools/audit_provisional_tip_sweep.py` and its complete direct tests against the amended whole-job planar-contact contract and existing exact finite flat-cap projection owner. No parent pair-review conclusions consulted. No code/test/baseline edits.

Disposition: **no material finding established** for the sufficient nominal pair classifier. It does not own chronological availability or contact permissions and grants no physical authority.

## Exact reasoning reviewed

Whole-motion AABB includes the radius in XY and affine endpoint extrema in Z, with no invented axial tip height. Material AABB encloses full XY width and bottom/top height. Strict positive interval separation is sound. Projection uses exact whole-sweep support `min/max(n·start,n·end) ± R*sqrt(nx²+ny²)` with outward square-root radius and the authoritative public bead projection. Proposed float-free rational axes are proposals only; a strict positive exact margin is required. Varying-Z material can use the projection owner; witness shortcuts conservatively remain restricted to constant-top material.

Boundary contact requires a global nonpenetration plane (the complete tip sweep at or above the constant material top) AND an exact shared material-centerline-top point lying in an actual swept disc. Projection interval equality alone is insufficient. Exact closest finite-segment witnesses handle stationary, parallel, intersecting and endpoint cases. Centerline top belongs to the finite bead including endpoint boundaries.

Positive penetration requires an actual tip-disc interior witness on the material's interior center plane, strictly inside both axial endpoints and bottom/top. Therefore the witness is interior material, not a point on an infinite extended line or a sampled off-line gap. Checking a bounded set of candidate motion parameters is a sufficient existence search only; failure stays unknown. No finite sampling is treated as proof of absence.

Reviewed immutable exact geometry/policy validation, nonzero exact proposed axes, input coordinate/query/square-root bounds, callback exact bool, resource/cancel/incomplete projection outcomes and axis-query cap. Unknown returns carry no acceptance margin/witness. This remains a pair geometry function: no same-path, same-layer, adjacency or support exemption is inferred inside it.

## Checks

Command: `.\.venv\Scripts\python.exe -m unittest tests.unit.test_provisional_tip_sweep -v` — PASS,4 tests,.016 seconds, Python3.12.10. Cases include exact top touch, projection-plane equality without shared point, sloped sweep penetrating between safe-looking endpoints, nonaxis strict separation, vertical endpoint contact and explicit resource/cancel/malformed axes.

Independently applied this new API to all4 actual non-AABB certificates in `whole28-actual-anchor-firsttravel-tip-disc-research.json` using current v4 frozen bead geometry and each stored exact axis. All classify strictly separated and reproduce the identical exact rational margin: floor4.2 return/outer7; floor4.2 motion14804/outer6 and7; floor5.2 motion18578/bead7.

Additional deterministic200 rational motions against a known finite horizontal bead produced177 strict separations,16 unknowns and7 positive-penetration witnesses. Independently reconstructed each witness's motion parameter, exact disc membership, finite axial membership and strict interior Z/distance conditions. Every witness passes. These probes supplement the proof conditions above, not a completeness claim.

## Integration limits

Caller must bind source/motion/material identities and policy to the run, validate which material exists at each command parameter and classify intended adjacency/support versus unrelated boundary contact. Boundary contact is neither positive penetration nor physical clearance. Unknown is not touch. Same-path causal material creation still requires explicit chronological scope; this API does not silently exempt any material. A complete job also needs source/support association and actual composed command accounting. Configurable nominal planar diameter remains an assumption; no head height/CAD, firmware, physical calibration or print authority is asserted.

## Public top-witness extension follow-up

Independently reviewed the frozen optional proposed-top-point extension. No material pair-geometry finding established. Exact immutable proposals have explicit count/bit limits. The function independently finds a valid actual motion parameter at the witness Z (rather than nearest XY at a different sloped-motion time), verifies disc membership and uses the public exact top-point owner against the actual finite material. Only a full-bounded equal top plus whole-sweep nonpenetration plane yields boundary contact. Wrong/off-solid witnesses do not establish contact; no caller boolean or arbitrary point supplies authority. Existing defaults retain previous sufficient classification behavior.

The combined9-test chronology/pair command above passes; all5 direct pair tests pass, including off-center flat-top contact that centerline-only witnessing could not prove, forged off-solid proposal, wrong sloped time, malformed tuple and resource/cancel outcomes. No change to physical authority or contact permission semantics follows.
