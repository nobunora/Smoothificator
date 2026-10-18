# Layer-angle coupon ruler association — bounded independent repository review

Date2026-10-19. Disposition: spec-change-required for integrated ruler geometry; recommendation only, no production edits. Task: new0..45degree specimen, one degree per original.2mm slice layer, half supplemented, physical ticks. Read current `tools/coupon_profile_association.py` and applicable latest ADR0071/handoff context. Existing pureextrusion validator is authoritative for its historical shape and must remain unchanged.

## Repository conflict

The existing validator requires exactly4 vertices per placed profile station, flat bottomZ0, one build item/component/mesh, and all expected side/top/bottom/end triangles. Integrated sidebase/tick geometry necessarily changes these counts/sets. Ignoring extra vertices/faces belowZ2 or comparing only the top profile would weaken the recently corrected actual geometry association. A manifest containing only an arbitrary mesh digest next to an arbitrary claimed profile also fails to prove their relationship.

## Recommended smallest robust extension

Introduce an explicitly versioned supported coupon+ruler geometry mode. A bounded deterministic constructor owns the working profile plus ruler parameters and generates the complete expected mesh, including all connection/base/tick faces. The association validator reconstructs that expected whole mesh from validated parameters and compares every placed vertex and triangle against actual pinned3MF bytes, retaining exact CORE hierarchy, millimeter-only units, pure supported translation, archive/XML resource limits and one component/object restrictions. Reject unknown schema/constructor versions, absent/duplicate geometry, unexpected features, altered profile/placement/ticks or out-of-bounds ruler geometry.

Use one authoritative constructor instead of separately maintained generator/validator formulas. Its outputs need independent tests that establish working surface is the requested fixed30mm strip, ruler geometry lies outside that strip and below comparisonZ2, the mesh is closed/manifold/oriented as required, and ruler stations correspond to the declared tick coordinate/labels. Constructor identity/parameters and complete expected mesh identity bind native recipe/calibration provenance. Do not treat shared-constructor agreement alone as independent proof that the constructor meets the requested shape.

Native/3MF parsing remains a tools adapter. Any pure geometric parameter DTO/arithmetic belongs inward; no native live objects, filesystem or G-code imports enter domain/engine/UI. Accepted ADR/handoff must explicitly authorize this supported shape extension before implementation.

## Working bounds versus mesh bounds

The existing helper returns whole-mesh min/maxX. Once a side ruler extends X, those limits are no longer the30mm working surface. Bind `working_surface_x_bounds` separately from overall mesh bounds and derive the half-supplemented span from the former. Do not shift the comparison midpoint toward the ruler. Source catalog selection must classify ruler/base deposits separately from comparison terraces, but retain every genuine ruler/base deposit as material/contact/tool-collision context. This requires a new genuine slice and new source/context/catalog/anchor identities; old source associations cannot transfer.

The manifest should bind profile/constructor version, working strip/origin, base plane/comparisonZ, saved layerH, angle increment/max, tick coordinate/positions/label meaning and ruler placement/dimensions. The exact zero-angle endpoint/first-layer indexing belongs to the separately adjudicated new coupon formula; do not guess it in association code.

## Alternatives

A separate ruler object preserves the coupon mesh but broadens current one-object/source-material/3MF gates and creates its own placement/scope identity. It is not the smallest extension without specific approval. Full-X extruded bottom notches could keep the top profile unchanged but still violate the current flat-bottom/count contract, alter bed-contact geometry and are less faithful to a side ruler. They should be selected only if the user accepts that physical layout. Neither alternative authorizes silently weakening the existing validator.

No tests run: this is a targeted source-contract review/recommendation, not an implementation or actual mesh acceptance result. Parent owns mathematical/profile adjudication and production implementation assignment.

## Focused handoff disposition

Reviewed `docs/specs/stepped-layer-angle-coupon.md` after parent adjudication. Disposition: VALIDATED for StageA geometry generation, genuine isolated CLI original slicing and the explicit deterministic whole-mesh association extension, subject to the required Accepted ADR addendum before implementation. The handoff preserves legacy pure extrusion, whole-mesh/source/profile/state identities, working-strip bounds, every ruler interaction and all independent gates. StageB remains gated on actual first/last printed contour evidence and parent-adjudicated integer-angle tolerance; no mesh-only angle ledger claim is authorized.

One editorial command-token correction sent to parent: actual `tools/restore_saved_print_profile.py:175` uses separate argv tokens `--slice`, `0`, `--orient`, `0`, `--arrange`, `0`; handoff's compact `--slice0`/`--orient0`/`--arrange0` text must not be executed as literal flags. No old restoration seed/output reuse is permitted. No other material repository conflict found within this bounded handoff review. No production edits/tests/GUI/print performed.
