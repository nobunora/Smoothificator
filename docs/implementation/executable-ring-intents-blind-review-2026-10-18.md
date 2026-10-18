# Executable ring intents — independent blind review, 2026-10-18

## Scope and independence

First review of this stage, completed without consulting its parent, research or implementation findings. Inspected docs/specs/executable-ring-intent-review.md, tools/prepare_executable_ring_intents.py, tests/unit/test_executable_ring_intents.py, relevant supplemental_z_hop composer/quantizer/policy code, authoritative adaptive_subedge.engine.flow_model helpers and CandidateBeadBounds validation, source_profile association/parser, and posed_intersection_area. Canonical basis: SPECIFICATION sections 12–13 and 23–24; Accepted ADR-0017; existing AGENTS/DOCUMENT_CONTRACT/REVIEW_PROCESS. Read the pinned actual manifest, source, sliced project and ring-intents.UNVERIFIED.json. No source/test changes, reslice, original mutation, printer operations, commit or subagents. Only this report was written.

## Result

No actionable material defect identified in the bounded offline immutable intent-preparation contract. This negative review is not firmware, physical-print, shape-quality, support, clearance, PlanStore or real-anchor approval.

## Paths and invariants checked

- Association: full source/project/manifest SHA256 pins precede preparation; manifest source/project hashes must match; read_sliced_profile requires embedded/separate source byte equality, unique ZIP/settings keys, supported saved setting representations and agreement of consumed source/project settings. Output freezes all three hashes, resolved setting identities, exact radial budget and XYZ/E precisions.
- Graph: unique safe ring IDs, complete integer chord-index sequence, duplicate/missing/orphan detection, adjacency and closure checks; source XY endpoints constrained to nine decimal places. All 30 original rings remain; no failed ring is omitted because accumulated ring failures reject the whole job.
- Height: exact original height/top/floor/overlap relationship, overlap 0–30%, maximum height capped by saved layer-height90%; top is rounded first with the existing half-away quantizer. New h derives from rounded top, floor and original overlap. Remaining height, h bounds, h<=width, width, upper ceiling and radial triangle dimensions are checked. Exact intersection computes each intended rectangle's spill, capped at50%.
- Divisor selection: visits legal divisors descending, including original count; uses only original endpoint indices, phase and closure. First legal divisor is deterministic; rejection reasons are retained. Neither radius nor nominal width changes, and no fresh trigonometric geometry is generated.
- Emission: quantizes XYZ before lengths/E, uses authoritative geometric and commanded-flow helpers, nearest explicit E precision, positive E, removes command multipliers before authoritative inverse width, checks current width bounds, and floors feed for actual commanded volume cap. Existing composer uses the same round/flow/length/filament-area arithmetic. Tests compare every emitted E/feed rather than relying only on final restored modal state.
- Radial proof: exact Fraction squared maximum norm at endpoints; exact clipped minimum projection; rejects collapsed segments and any entire-segment excursion beyond radius±budget. No floating sqrt tolerance admits geometry. Float length/flow arithmetic is confined to the already-authoritative emission model, not radial acceptance.
- Ownership/authority: nested path/policy/ring/settings diagnostics are frozen dataclasses, tuples and Fractions; CandidateBeadBounds is frozen. Main writes only a new exclusive-create unverified receipt. Source/profile reads are read-only. Synthetic replay uses declared anchors and explicitly records no real-anchor verification; all physical/execution authority flags stay false.

## Executed evidence

Interpreter: exact repository `.venv` Python 3.12.10 (verified earlier this same independent session).

`.\.venv\Scripts\python.exe -m unittest tests.unit.test_executable_ring_intents -v` → exit 0, all 8 tests pass (10.861 seconds). These cover unchanged30 paths/radii/widths, deterministic192/96 selection, seven original fixed-height failures, nearest-E192 width failure corrected at96, exact radial boundaries/projection/collapse, emitted positive E/width/rate, composer E/feed/restoration agreement, association pins and malformed graph, overlap/minheight/cap/ceiling/spill rejection.

Additional read-only `@' ... '@ | .\.venv\Scripts\python.exe -` verification → exit 0:

- Recomputed the whole immutable RingIntents object, converted it with the same publication representation, independently generated synthetic replay receipts, and compared the entire result to stored ring-intents.UNVERIFIED.json. Exact agreement.
- Independently implemented the rational translated-segment projection/max-endpoint checks for every emitted segment and asserted exact lower/upper squared bounds.
- Independently recomputed quantized segment length, E-derived command flow, removed the resolved command multiplier, inverted geometric flow through the authoritative helper and checked width/E/volume caps for all5,568 emitted segments.

Actual fixture result:30 paths,5,568 chords; ring-2/ring-3 select96 existing chords each, the remaining28 retain192. The receipt's source/project/manifest identities are the pinned original research source/project, not the separately restored manufacturer's baseline. This association is explicit and consistent with this handoff.

## Boundary/failure coverage and residuals

Considered empty jobs, duplicate counts/IDs/indices/keys, disconnected/missing/orphan graph, stale hashes and embedded source mismatch, invalid precision/budget, overlap extremes, minimum heights, upper ceilings, collapsed/zero E, width/rate failures and exhausted divisor search. Accepted outputs require at least one complete ring and exact ring/line counts. Certain malformed schema/type inputs can surface ordinary Python errors rather than a uniform reason-code receipt; they do not return authority or mutate input, and a stable cross-boundary error schema is not specified for this bounded pure tool.

This inspection does not prove manifest geometry derives faithfully from physical material or that a circle chord has continuous structural support; pinned provenance and exact emitted radial bounds are narrower claims. The copied float emission model is checked against the composer, not against firmware execution. Alternate overlap/profile combinations lack the full actual-fixture regression coverage available for current zero-overlap inputs. No architecture/full-suite/build gates were repeated independently; parent verification owns those. Unknown firmware/formatter family and manufacturer's expanded command semantics remain separate gates. No finding requires disposition; no production/physical convergence is declared.
