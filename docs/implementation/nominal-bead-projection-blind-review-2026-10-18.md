# Nominal bead projection — independent blind review, 2026-10-18

## Scope and result

Reviewed docs/specs/nominal-bead-projection-review.md, additive frozen ExactNominalProjectionBounds, query_exact_nominal_bead_projection and shared outward sqrt owner in support_cell.py, focused tests and actual source-offset341.UNVERIFIED.json. Canonical ADR-0048 finite flat-cap and varying structuralZ convention governs. No parent primary findings consulted. No code/test/artifact edits, slicing, source mutation or printer operation; only this report written.

No actionable material defect identified in this additive exact engine API. The bounded result is a whole nominal solid projection in unnormalized axis-dot units, not physical head clearance or a full-job certificate.

## Mathematical inspection

For XY direction d and D=dx²+dy², the squared projection onto the lateral unit normal is q=(ax*dy-ay*dx)²/D. The canonical stadium is a lateral segment of halfwidth (w-h)/2 plus a radius h/2 disc in the normal/vertical plane. Its axis support extent is (w-h)/2*sqrt(q)+h/2*sqrt(q+az²). Sweeping this fixed section along the finite centerline shifted down by h/2 adds exactly min/max endpoint dots. A linearly varying commandZ changes those endpoint dots; it does not change this section support. The implementation matches this derivation without adding tangent/round end caps or varying-width interpolation.

The source DTO guarantees w>=h>0 and nonzeroXY; therefore both coefficients of outward upper sqrt bounds are nonnegative. Expanding min/max dots by that upper extent bounds the entire exact solid. Axis is exact, immutable and nonzero; no normalization, float-distance threshold or approximate acceptance exists. Projection interval overlap remains inconclusive; the API itself does not classify solid intersection or choose chronology.

## Validation and failure paths

Exact type/shape checks reject malformed segment/axis, floats/bools/NaN and zero axis. Explicit coordinate/sqrt limits and callback requirements reject malformed policy. Input-bit overflow returns incomplete/resource-limit with no bounds. Cancellation is exact-bool checked, latched, checked before work/between sqrt evaluations/at publication; once observed, no bounded result can escape. Frozen result validates segment identity, axis and state/reason combinations, exact ordered bounds, and no bounds on incomplete outcomes. Shared _sqrt_bounds remains the only sqrt enclosure owner. Existing top/point/cell/span/overlap behavior is not redirected through this new API.

## Executed evidence

Exact repository `.venv` Python3.12.10, previously verified in this independent session.

- `.\.venv\Scripts\python.exe -m unittest tests.unit.test_nominal_bead_projection -v` → exit0, all6 tests pass (0.197 seconds): cardinal/oblique/flatcaps, reversal/scaling, vertical/varyingZ/rounded support, malformed inputs, resources/cancel and all341 pinned actual certificates.
- `.\.venv\Scripts\python.exe -m unittest tests.unit.test_exact_nominal_top_span tests.unit.test_nominal_bead_overlap -q` → exit0, all15 nearby regression cases pass (0.282 seconds).
- Additional read-only Python probe → exit0: verified all actual artifact input pins and embedded/separate source identity; reconstructed both segment inputs for each341 actual pair and reran the new engine owner. Every frozen first/second projection result equals the stored receipt exactly, and each exact separation margin is positive.
- Independently implemented a256-bit outward sqrt support enclosure for120 deterministic rational varyingZ solids and axes. Every128-bit engine result contains the independent tighter enclosure; reversing axis exactly negates/swaps bounds. This included h=w circular-section cases.

Prior independent certificate audit accounted for all315,136 fixture pairs, including314,795 conservative full-bead AABB exclusions. This projection stage's artifact explicitly states those AABB exclusions are not recomputed by its341-axis receipt; no stronger whole-job claim was inferred.

## Ownership and limits

The implementation correctly places reusable exact arithmetic in the existing engine owner with a domain-owned immutable result; tools may propose axes and record certificates. It does not import source/filesystem/planner dependencies. Callers still own exact model/source association, candidate widths/heights, complete chronological pair enumeration and axis-search policy. A failed candidate axis or overlapping intervals must not become proof of overlap or safety. Dot margins are not millimeters of clearance. The pinned fixture is constantZ, while varyingZ correctness has analytic/synthetic coverage. Physical nozzle/head geometry, deformation, runtime state and source anchor eligibility remain separate. Parent owns architecture/full regression beyond these independent focused checks. No finding requires disposition and no physical/production convergence declared.
