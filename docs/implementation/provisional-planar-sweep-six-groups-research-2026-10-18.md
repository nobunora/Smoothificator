# Chronological provisional planar-tip sweeps — six-group research, 2026-10-18

## Concrete result

Applied the user-approved configurable assumed diameter0.4 mm (radius1/5), zero axial height, to the frozen source-offset4.2 path and source-follow single lanes4.4,4.6,4.8,5.0,5.2. Actual E-derived bead widths/heights and quantized endpoints were retained. Source is seam0-v2 SHA256 `fc1655086645ba1fd3758b4c5554fa3039044d6ba126457f473470d2d28eee60`. No reusable code edits, original mutation, reslice or printer operations. Exact research evidence: artifacts/provisional-planar-sweep-research/six-groups.UNVERIFIED.json.

For this **zero-height nominal planar tip**, candidate deposition is strictly above every earlier original/candidate bead, and every explicit later original body travel/deposition tip is strictly above already placed candidates. These facts admit exact vertical-axis separation certificates without a head-CAD prerequisite. There are unavoidable same-path top-touch events during continuous deposition and closure, requiring typed intended-contact policy; no strict vertical penetration was identified under these declared geometries. Runtime opaque motions remain unresolved rather than safe.

| Floor | Edges | Candidate top | Before-source order | Earlier original top maximum | Later explicit original tip minimum | Later tip/candidate Z gap |
| --- | --- | --- | --- | --- | --- | --- |
| 4.2 | 64 | 4.326 |15994|4.2|4.4|0.074|
| 4.4 | 65 | 4.48 |16920|4.4|4.6|0.12|
| 4.6 | 65 | 4.68 |17795|4.6|4.8|0.12|
| 4.8 | 65 | 4.88 |18679|4.8|5.0|0.12|
| 5.0 | 65 | 5.08 |19430|5.0|5.2|0.12|
| 5.2 | 65 | 5.28 |20049|5.2|5.4|0.12|

Every earlier candidate top is also below the next floor (4.326<4.4,4.48<4.6,etc.), so earlier-candidate material does not defeat these certificates. Source ordering is nominal line order; the listed boundaries are not real retracted anchor certificates. Explicit source G0/G1 tokens include inline conditional camera/detection travel. Their modeled Z intervals satisfy the table, but hidden G39/G39.3 motion and predicate execution are not determined by their tokens.

## Exact algorithm using existing owners

A zero-height planar disc swept along command endpoints A→B is the Minkowski sum of the finite3D center segment and a horizontal radiusR disc. On exact rational nonzero axis n, its support interval is:

`[min(n·A,n·B)-R*sqrt(nx²+ny²), max(n·A,n·B)+R*sqrt(nx²+ny²)]`.

Use outward upper bounds from the existing exact sqrt owner. Query each bead through public query_exact_nominal_bead_projection; no copied bead geometry or h=0 fake ExactNominalTopSegment is needed. Separate tools-owned provisional sweep input from real physical ToolClearanceProfile. A positive gap between outward intervals proves disjointness. AxisZ=(0,0,1) is exact and sufficient for all strict separations in the table. Other rational axes may be proposed if needed; no float axis search result alone may accept.

Broad phase uses tool endpointXYZ extrema±R inXY only, and full bead XYZ bounds. Track chronology at motion/deposition order, adding each completed candidate segment only after it exists. Check candidate extrusion against all earlier material, every raise/XY/descent/lift/return against then-existing material, and every later original motion against all placed candidates. No future material may support or obstruct earlier events. Frozen E-derived widths must be used, not nominal desired widths.

Overlapping projections are inconclusive. For a concrete intersection witness at trajectory parameter t, choose exactXY point P within radiusR of the exact tip center(t). Use existing exact top point owner plus its vertical reflection for bead bottom. If bottom_upper<tipZ<top_lower, P lies in bead interior: **strict penetration**, forbidden unless a separately explicit deposition policy truly permits it. If a certified exact boundary equals tipZ, classify **touch**, not penetration; current centerline flat tops give exact rational equality. Do not call a zero-height plane intersection “positive3D overlap volume.” Unresolved cap/equality remains unresolved and is refined or rejected, never rounded into separation.

For complete sweep proof when axes fail, refine the time/XY query domain conservatively with explicit bit/query/depth/cancellation limits and preserve interval coverage. A touch witness disproves strict disjointness but does not prove the rest of a sweep safe. Existing top-span owner supplies whole-line bounds, not endpoint sampling. The lower-bound centerline-contact test remains a separate weak support diagnostic; it cannot substitute for full-footprint support or collision checks.

## Concrete six-group bridge scenario

A nominal bridge scenario can use the source-token XYZ immediately before each listed first-upper-layer deposition, a ceiling upper+0.4 from saved hop, candidate first point and exact return to the saved source XYZ. Prefix tokenZ is upper; candidate top lies below upper but above all earlier material. Raise/ceilingXY/entrydescent therefore stay above earlier material. Following path deposition, terminal lift touches its own intended endpoint only at the closed initial instant and becomes vertically separated for t>0; ceiling return and descent to source upper remain above completed candidate top.

This validates geometric **scenarios**, not a complete generated program: actual saved retraction debt/feed/modes and chronological insertion location must come from the separate source-state adapter. No commands were emitted or source anchors invented. Do not accept a source trace merely because these simplified scenarios are safe.

## Real touching counterexamples and simple fixes

At a same-path segment junction the radius0.2 tip disc reaches the completed previous segment's flat top at the sameZ. These are expected intended continuous-deposition contacts, not strict penetration. A typed adjacency rule must identify exact parent path/segment IDs, execution order and contact region; a blanket exemption for all candidate material would hide unrelated sameZ collisions.

There is a sharper **direct-adjacency-only counterexample** in four source-follow paths. Their short closing edge65 lies between edge64 and first edge1. At edge64's endpoint (also edge65's start), the tip disc touches first-edge centerline/top with exact squared XY distances:

| Floor | Squared distance to first segment | Classification |
| --- | --- | --- |
|4.4|317/500000|top touch|
|4.6|29/50000|top touch|
|4.8|89/200000|top touch|
|5.0|13/50000|top touch|

All are strictly below R²=1/25. The artifact retains exact tip/point coordinates and source segment parameter witnesses. Edge64 is not directly cyclic adjacent to1 because65 intervenes, so exempting immediate predecessor plus direct cyclic adjacency alone would reject this real intended seam approach.

Two bounded remediation options:

1. Define an explicit **seam-closure contact region** tied to this closed path and its first/terminal portion, with exact geometric and chronology witnesses. Permit only top touching there; strict penetration and unrelated sameZ paths remain forbidden. Derive the local reach from actual provisional radius and bead geometry rather than an invented physical clearance threshold.
2. Planner coalesces/removes the very short closing edge before intent freeze, then recomputes quantized geometry, E/feed, actual widths, triangle spill, support, future bead separation and seam/contact proofs. This is a geometry change and needs its own reviewed intent; do not smooth it in the emitter.

The current investigation did not exhaustively certify every same-path sweep against every older segment. It established unavoidable joint/seam touches and the specific adjacency-policy failures above. Full pair sweep validation must retain nonlocal/self-approach possibilities rather than infer absence from these witnesses.

## Proposed implementation contract and priorities

Implement a public exact planar-disc sweep projection in the geometry layer alongside existing bead projection, with immutable tools-owned assumption identity passed explicitly; no whole-head height. Add immutable `SweepEvent` (exact endpoints, order, source-span/provenance, role=raise/travel/descent/extrusion/lift/return), `PlacedBead` (frozen E width/height, completion order), and typed `AllowedContact` (parent-path adjacency or named seam region, exact source segment IDs, touching-only predicate). Every pair result is strict-separated / allowed-touch / forbidden-touch / penetration-proven / incomplete, with rational axis or point/parameter witnesses. A global report cannot pass with unknown opaque motion or unexamined material pair.

First complete the six-group vertical-axis strict certificates and explicit bridge scenario ownership; then add same-path adjacency/seam touching tests and broad-phase pair coverage. Couple to the derived branch-free nominal source adapter so model geometry/travel are actual frozen events. Preserve unknown startup/conditional/detection state until evidence resolves it; their existence does not prevent building these software contracts now. The configurable0.4 tip assumption numerically drives XY sweep extent and contact regions, while full head/physical authority remains false.

## Evidence and limitations

Used exact repository Python3.12.10 in read-only computation plus creation of a new research JSON/report. Checked actual frozen dimensions, strict chronological original/candidate top bounds, all explicit post-boundary model-body G0/G1 endpointZ ranges, and exact nearest centerline-point witnesses. No additional reslice or production code. Manufacturer runtime G39/G39.3 and object-cancellation effects are recorded unknown; startup/end opaque programs remain outside a whole-source certificate. Zero-height tip results say nothing about axial hotend geometry, deformation or calibrated support. No physical/whole-print authority granted.
