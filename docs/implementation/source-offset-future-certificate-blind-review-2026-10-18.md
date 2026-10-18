# Source-offset future separation — independent certificate audit, 2026-10-18

## Scope, independence and result

Read-only independent mathematical/fixture audit of artifacts/print-source-inspection/research_offset_future_separation.py, source-offset-future-separation.json, source-offset-candidate-budget100k.json, actual seam0-v2 source/project and nominal-model-rows.json, against ADR-0048's finite flat-cap stadium convention and existing exact support kernel. No parent primary findings consulted, no production edits, no artifact overwrite, no research-script execution (it writes output), no slicing or printer operation. Only this report written.

**All315,136 declared nominal candidate/future pairs independently accounted for. All341 rational separating-axis certificates independently recompute with strictly positive margins. No mathematical certificate defect identified for the declared pinned fixture/model.** This is conditional nominal deposition geometry, not actual source-anchor eligibility, a whole-print certificate, or physical head clearance.

## Source/fixture association and chronology

Actual seam0-v2 source SHA256 `fc1655086645ba1fd3758b4c5554fa3039044d6ba126457f473470d2d28eee60`; sliced project SHA256 `dd9a236689c0517057f14fc38d6ec36876c79777ed3a56307b17e32c55d0fc9b`. Verified separate source equals embedded Metadata/plate_1.gcode. Candidate receipt uses that source identity.

Independently reconstructed every positive-XY-relativeE nominal model event from actual source using modal XYZ/E/F and explicit LINE_WIDTH/LAYER_HEIGHT comments, with complete source line numbers and feature blocks excluded explicitly as a nominal model projection. All14,985 rows exactly equal nominal-model-rows.json, whose SHA256 is `46c23686ef31072f9ba0dec968603325f55477fa966fd0414df9ad4340fddb1b`. Candidate artifact SHA256 is `2b4af8efc9d1cba5dff24e4871096d4f3162ba4fcd941578cc98a79e2b922dbf`.

The script chooses first nominal model deposition ending at Z4.4, source line15994, as the future boundary. It includes **every subsequent model row by source order**, not just rows at higher Z or nearby radial distance:4,924 rows. Correct interpretation is candidate deposition occurs immediately before this boundary and after preceding model deposition. No source insertion anchor is reconstructed or verified here. If placement is earlier, or another insertion order is chosen, recompute the future set and earlier-support audit. Current fixture future rows are constantZ; no varyingZ row occurs among the source's14,985 model rows.

## Independent support-function derivation

Let bead XY direction d=(dx,dy), D=dx²+dy², lateral unit n=(dy,-dx)/sqrt(D), h<=w. Under ADR-0048, the solid is the Minkowski sum of:

1. the center segment from start-(0,0,h/2) to end-(0,0,h/2), including its closed finite endpoints;
2. a lateral segment of half-length (w-h)/2 along n;
3. a radius h/2 disc in span(n,Z).

For exact rational axis a, squared lateral projection is L²=(a_x*dy-a_y*dx)²/D. Cross-section support extent is `(w-h)/2*sqrt(L²) + h/2*sqrt(L²+a_z²)`. The support interval is min/max endpoint dot products plus/minus this extent. This retains flat caps: no tangent-axis round extension is introduced. Because the center segment may slope in Z without changing the cross-section plane, the same support expression also holds for ADR-0048's constant-w/h linear varyingZ convention. No varying width/height interpolation is covered.

The research implementation matches this expression. Using outward upper sqrt bounds and nonnegative coefficients w-h,h produces an enclosing interval, so a strictly positive interval gap proves exact separation of the declared solids. Every actual input satisfies w>=h>0 and nonzero XY length. Candidate widths are the stored E-derived decimal model inputs treated as exact Fractions; this proof is conditional on that source-adapter width convention, not independent physical calibration.

Axes selected using float length/ratio are converted into exact rational triples before verification. Any nonzero axis is valid; approximate axis proposal cannot falsify a certificate because acceptance recomputes outward rational intervals and requires a strict rational gap. No float margin threshold is used. Dot-unit margins are unnormalized and must not be reported as millimeter clearance.

## Full accounting and independent execution

Used exact repository `.venv` Python3.12.10 in read-only `@' ... '@ | .\.venv\Scripts\python.exe -` probes, exit0.

- Recomputed conservative **full bead XYZ boxes**, expanding both XY endpoint ranges by w/2 and Z from min(commandZ)-h to max(commandZ). These may be loose around oblique flat caps but cannot omit bead material. Exclusion requires strict coordinate separation; no nozzle-tip-only or topZ-only test is used.
- Enumerated all64 candidates ×4,924 future model segments =315,136 pairs.
- Exactly314,795 pairs are separated by these conservative XYZ boxes.
- Exactly341 remaining pairs correspond one-to-one with the341 stored certificates: no missing/orphan/duplicate near pair.
- Implemented an independent outward sqrt enclosure with integer isqrt at2^128 scale; asserted squared rational containment for every radicand. Did not call the research script's projection function or its _sqrt_bounds helper.
- Recomputed each rational-axis support interval, strict gap in either direction, and exact stored margin. All341 margins equal the stored fractions and are >0; reported minimum fraction also matches. Approximate minimum is4.986186291301395e-05 **dot units**, not normalized physical distance.

There are zero unresolved pairs within this declared nominal pair set. This does not turn skipped non-model commands, startup/detection travel or other candidate interactions into safe motions.

## Reusable owner and implementation recommendation

Do not import the artifact script or copy its arithmetic/float search into a planner. A reusable certified projection belongs with the existing ADR-0048 exact geometry owner, preferably a small public query in adaptive_subedge/engine/support_cell.py using ExactNominalTopSegment and the single outward sqrt primitive. If cohesion requires a new exact nominal-bead bounds module, move/share the primitive rather than establish a second geometry definition. Domain owns frozen axis/bounds/certificate DTOs; tools may propose axes and serialize research receipts.

Proposed pure kernel input: exact immutable segment, nonzero rational3-axis, explicit coordinate/axis-bit and sqrt limits, exact-bool cancellation. Output: frozen lower/upper projection bounds, model/version and typed incomplete reasons. Pair helper checks both intervals and returns a positive exact margin witness or unresolved; never interprets failed axis search as overlap or safety. Geometry owner has no filesystem/source-parser/planner dependencies. The planner owns chronological pair-set construction and source association, with all material sources retained until conservative broad-phase exclusion.

Required focused fixtures before planner acceptance: rational analytic axis cases, horizontal/vertical/oblique flat caps, negative/reversed axes and endpoint order, positive scaling invariance, varyingZ support, h=w circular limit, zero/invalid axes, w<h rejection, bit/sqrt/cancellation limits, outward enclosures near exact tangency, pair-order symmetry, and this complete341-certificate/315,136-pair pinned regression. All explicit source hashes, candidate representation/policy and chronology boundary must participate in any reusable review identity. The present ad hoc script lacks production input validation/pinning/cancellation, so its successful receipt must not be promoted wholesale into a production gate.

## Limits

Only declared model deposition beads are included. Source firmware/runtime branches, actual retraction/volumetric state, object cancellation, tool motions, complete head geometry, physical pressure/deformation and every other candidate are outside this audit. Positive/zero material contacts may require different policy from strict disjointness. Reusing this certificate after any source, candidate width/height/position, ordering or model change is invalid. No physical/runtime authority or production convergence declared.
