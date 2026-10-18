# Localized original source-joint detour proposals

Implementation of parent-validated
`docs/specs/localized-source-joint-detours-review.md`; ready for independent review.

The existing `tools/prepare_source_contour_intents.py` owns optional immutable
`SourceJointDetour` recipes. Recipes identify an ORIGINAL segment START joint
and exact positive source arclength. Walking uses original edges even when the
proposal regularizer removes vertices. Both waypoints record original edge IDs,
walked edges, edge parameter and construction/quantized positions. Generated
identity strings are distinct from original vertex indices. Original contour
objects remain unchanged.

Empty recipes preserve the base `SourceContourProposal` serialization/identity;
explicit recipes produce frozen `SourceJointContourProposal` with added recipe,
waypoint, replacement and removal-stage provenance. The same numeric freezer runs
once after all construction. No accepted frozen path is edited. Joint and both
waypoints are protected during post-splice regularization; shortest-edge removal
uses the unprotected endpoint, with existing end priority when both unprotected,
and rejects when both protected. This rule was explicitly adjudicated in handoff.
Source-edge neighborhoods, walks, vertices, coordinate bits, geometry checks and
cancellation remain bounded. No physical/contact/future/print flags are enabled.

New focused tests: `tests/unit/test_source_joint_detours.py`; reproduction script:
`artifacts/source-joint-detour-review/reproduce.py`.

## Repository conflict requiring parent adjudication

The actual floor3.8 outer contour's initial existing short-edge regularization
removes original joint13000 (the end of its closing shortest edge). The first
implementation correctly rejects `vanished-joint`. The research script instead
overwrites its first retained miter with original joint13000, losing the identity
distinction. That cannot silently satisfy the explicit retained-original-joint
contract. Proposed adjudication: protect requested joints during INITIAL
regularization too, choosing the unprotected endpoint, then run the same protected
post-splice rule. This should be tested against every final coordinate/E/proof;
no unreviewed acceptance or geometry transfer is permitted. Affected actual outer
construction is held pending parent's decision.

The unaffected actual inner path freshly reproduces all geometry, E and implied
widths;65contact queries prove all65 centerlines; all418015 future pairs exclude
by417886 conservative full-bead boxes and129 strict radial bounds. No final
two-path receipt has been written while outer construction is unresolved.

## Checks to date

All used required `.venv\Scripts\python.exe`, Python3.12.10.

- `-m py_compile tools/prepare_source_contour_intents.py`:PASS,exit0.
- `-m unittest tests.unit.test_source_contour_intents tests.unit.test_executable_ring_intents -q`:15PASS,11.796s,exit0.
- `-m unittest tests.unit.test_source_joint_detours -q`:5PASS,0.030s,exit0.
- `artifacts/source-joint-detour-review/reproduce.py`:exit1 at explicit
  vanished-joint rejection for outer path, after the independent inner checks
  above. No final output file written or prior evidence overwritten.

No conditional-copy files, parser, source, profiles, engine, printer operations,
dependencies, commits/pushes/merges/releases changed. Unrelated dirty work and
`log_iotc.txt` preserved. Full suite deferred until bounded stage review.

## Adjudication and final actual result

Parent amended the contract: requested original joints are protected during
INITIAL regularization too, with the same unprotected-endpoint rule. Implemented
that explicit rule; no original vertex is silently relabeled. Empty recipes are
unchanged. Parent separately accepted the66-edge result as a NEW proposal, with
no requirement to recreate the research script's undocumented65-edge overwrite.

New `floor38-two-paths.UNVERIFIED.json` under
`artifacts/source-joint-detour-review/` records complete proposals and proofs.
Inner geometry/E/actual widths match research exactly. Outer geometry/E/width
parity flags are explicitly false: original joint13000 remains itself; original
13064's short miter is removed initially; original13001's miter at
(96.783,88.994) remains between forward waypoint and the next miter. Research had
overwritten that miter with original joint13000 after losing the joint. The new
closing route also honestly omits13064's removed miter. All coordinates and
emission were frozen anew and validated without old verdict transfer.

The reverse0.03-mm original source walk crosses13064 then reaches13063; forward
walk lies on13000. Waypoints, original joint, source edge parameters, walked IDs,
replacement miter and removal-stage count are in the immutable proposal.
Original source objects/IDs remain unchanged. No optional collinear coalescing
was needed; existing unsupported-collinear rejection remains unchanged.

Fresh results using current saved profile/shared emission/exact public owners:

| Path | Edges/contact queries | Future pairs | Box / radial / exact projection |
| --- | ---: | ---: | ---: |
|Inner|65 /65|418015|417886 /129 /0|
|New outer|66 /66|424446|424160 /132 /154|

Every edge is whole-span nominal centerline-contact proven; no gap/incomplete.
Every future pair is accounted, with no unknown. Research axes are proposals
only; each new projection certificate is recomputed for actual new geometry.
Full radial-footprint packing lower gap is0.03772072709270941 mm. Rigorous
whole-range spill bounds are0.4111961220199645 and0.3160289791840106, exact<=1/2.

The finite target interval stays[6.304,7.025] mm. Actual radial footprint intervals
are approximately[6.3518862582,6.6844934784] and[6.7222142055,7.0831077235].
Outer right overhang is0.05810772348738711 mm. Parent adjudicated this diagnostic,
not an extra containment gate: the user permits up to half outside area and the
finite-clipped spill owner accounts for it. No unrequested tighter rule added.

`floor38-quality-surrogate.UNVERIFIED.json` conservatively bounds whole-range
radial-rectangle symmetric difference by triangle area plus maximum total
rectangle area minus twice minimum guaranteed retained area. Positive inter-lane
radial gaps justify adding union contributions. Unsupplemented surrogate error
is0.0721 mm². Intended research geometry/intent widths have upper bound
0.05470888928894345; actual new geometry/E-implied widths have upper bound
0.05910335052789605 mm². These are sufficient whole-range surrogate bounds,
not exact optima, canonical3D affected-domain quality, full footprint support or
physical clearance. Quality-error improvement work remains deferred; no complete
job selection or print/runtime authority follows.

Final checks (required Python3.12.10):

- `-m py_compile tools/prepare_source_contour_intents.py tests/unit/test_source_joint_detours.py artifacts/source-joint-detour-review/reproduce.py artifacts/source-joint-detour-review/quality_surrogate.py`:PASS,exit0.
- `-m unittest discover -s tests/architecture -q`:45PASS,4.563s,exit0.
- `-m unittest tests.unit.test_source_joint_detours tests.unit.test_source_contour_intents tests.unit.test_executable_ring_intents -q`:21PASS,14.952s,exit0. This includes exact entire serialized parity for all6 existing factory proposals and legacy30-ring numeric tuples, plus short-source-edge traversal, both orientations, translation, multiple/disjoint/overlapping joints, protected removal, limits/cancellation and recipe identity.
- `artifacts/source-joint-detour-review/reproduce.py`:PASS,exit0,5.485s internal proof timer. New exact receipt, all original input pins rechecked after computation.
- `artifacts/source-joint-detour-review/quality_surrogate.py`:PASS,exit0; separate new diagnostic receipt with input hashes and exact certificates.

The initial rejected attempts are recorded above rather than presented as passes.
The final recipe is an explicit new66-edge proposal; earlier long-diagonal/wider
future-overlap variants remain rejected. Rollback removes optional recipe support
and new tools artifacts only; source inputs need no restoration.
