# Source-top straight fragment alternative — initial one-group feasibility, 2026-10-18

Exploratory research only; no reusable edits, source changes, slicing or printer operations. Conditional-copy handoff was separately re-reviewed after its explicit motion-envelope/path-association amendments: disposition validated for tools-only conditional implementation, with existing strict gates unchanged.

## Concrete floor3.2 proposal

Actual seam0-v2 source SHA256 `fc1655086645ba1fd3758b4c5554fa3039044d6ba126457f473470d2d28eee60`, nominal source line10230:

`(89.105,94.696,3.2) -> (91.119,92.682,3.2)`, source width0.42691,height0.2.

Take an exactly collinear, grid-representable interior fragment:

`(89.855,93.946,3.28) -> (90.355,93.446,3.28)`.

Its intended h=0.08, remaining=0.08, overlap0, desired width0.27 all satisfy current user bounds. Authoritative flow helpers with source filament1.75/ratio0.98 and nearestE5 produce E=583/100000 and effective nominal width27011743920811887/100000000000000000 (~0.2701174392). No ceilE or changed bound is used.

Existing real exact whole-span query on source10230 returns full-bounded with top lower exactly3.2 across this entire clipped source-aligned fragment. Endpoints lie inside the same source flat axial span, so the source-cap wedges that hurt independent circles are avoided. This proves nominal centerline-bottom contact only; full-footprint support remains a separate metric.

## Exact finite residual-region containment

Original floor3.2 radial stair triangle has left radius2.587, base1.732,rise0.2. Use its existing finite ideal target convention: 0<=radial-left<=base and0<=Z-floor<=rise*(radial-left)/base. Do not replace it by an infinite sloped half-plane or a differently oriented local rectangle without respecifying the objective.

Independently computed exact rational endpoint/projection radius bounds with outward sqrt enclosures. Expanding centerline radial range by actual E-derived width/2 conservatively encloses the complete flat-cap stadium XY footprint. Resulting radial band is approximately[3.3291787145,4.0837219111]. For a full height0.08 rectangle to lie below this finite triangle, radius must be at least2.587+1.732*0.08/0.2=3.2798 and at most4.319. The entire conservative band lies strictly inside those limits. Therefore this complete fragment bead lies within the ideal finite residual prism: conservative outside-triangle fraction0, stronger than<=50%. This containment proof avoids pretending a tangential fragment has the same radial rectangle area/error score as a circular lane.

## Future nominal material check

Assume candidate follows completed floor3.2 and precedes first nominal3.4 source deposition at line10486. Enumerated all8,690 future model segments by source order. Full nominal bead lowerZ separates7,917 strictly above candidate top3.28. For remaining773, exact source centerline minimum radius minus width/2 is greater than candidate full-footprint outer bound; minimum conservative radial gap is approximately0.2345899156. Thus every declared future model bead is separated by whole-solid bounds, not tipZ alone.

This is conditional on the nominal rows/source geometry convention, not source execution or physical head clearance. Existing source-state and tool-motion gates remain separate.

## Tradeoff and bounded next step

This supplies a real admissible **partial** residual-domain improvement where the source deposition is oblique/straight. It does not cover the whole3.2 stair annulus, nor the remaining3.0..4.0 groups. Uncovered areas must be retained explicitly in residual/error reports; a bag of passing fragments must not be mislabeled a solved complete group.

A reviewed alternate-family search could clip source-aligned spans to the existing exposed residual domain, evaluate finite rounded-bead union effect through the canonical affected-surface/error owner, enforce overlap/support/future/tool gates, and select multiple independent fragments under the same complete-domain error objective. It must account for fragment endpoints/caps, restart/bridge count and residual holes. Different orientation changes the predicted bead union and optimization tradeoff; no unchanged circular error/optimality claim is available. The example is feasibility evidence for that future bounded specification, not authority to introduce a parallel error estimator or optimize now.

Validation: read-only exact `.venv` Python3.12.10 probes exited0; authoritative flow/quantizer/kernel used; whole future set and conservative finite-region bounds independently computed. No output G-code or physical authority.
