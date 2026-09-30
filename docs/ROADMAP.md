# Development Roadmap

Implementation is gated. Do not advance until the previous phase exit criteria pass.

## Phase 0 — specification and audit
Complete before code:
- architecture boundaries
- document precedence
- canonical ADR set 0001-0008
- dependency/feasibility audit
- stock-Orca execution architecture
- source-verified ZAA Z/flow semantics
- Bambu safe-boundary injection model
- v1 safety envelope

Exit:
- no duplicate/conflicting Accepted ADRs
- normative docs consistent
- no known source-level blocker in v1 domain

## Phase 0.5 — architecture skeleton
Implement only:
- package/module tree
- frozen domain DTOs
- typed errors/reason codes
- Settings validation
- canonical plan serializer/hash
- PlanStore/status interfaces
- import-boundary tests

No Orca/G-code/optimizer logic.

## Phase 1A — bead/flow primitives
Implement/test:
- Orca rounded-rectangle flow formula
- candidate effective bead height above support
- ZAA local effective flow normalization
- Orca filament_flow_ratio -> E conversion parity
- finite-bead representation
- no-refinement baseline identity

Exit:
- formula parity fixtures pass
- invalid physical candidates rejected

## Phase 1B — surface-band geometry
Implement:
- mesh plane section
- target-boundary representation
- centerline placement inside material
- same-Z multi-path coverage
- different-Z multi-path coverage
- nesting/support checks

Exit:
- boundary is never directly treated as centerline
- shallow terrace can require multiple paths
- unsupported outward-expanding geometry rejected

## Phase 1C — error/optimizer
Implement:
- final combined envelope
- normal-error metrics
- candidate flow/geometry search
- cost model
- deterministic optimizer

Exit:
- synthetic/fixed-angle cases improve or safely report infeasible
- no Orca/G-code dependency

## Phase 2A — Orca coordinate adapter
Stock Orca read-only:
- posSimplifyPath
- copy source mesh/path/config
- path-relative Z -> absolute Z
- local ZAA flow normalization
- source transform validation
- injection gate detection

Exit:
- ZAA on/off fixtures
- transformed coupon fixture
- no live reference escape

## Phase 2B — Analyzer/PlanStore
Wire Snapshot -> Engine -> immutable SubEdgePlan.

Exit:
- real Orca coupon plan
- unsupported configs marked analysis-only
- plan hash deterministic
- cache/no-plan behavior tested

## Phase 3 — Preview
Script capability:
- baseline/ZAA paths
- target material boundary
- candidate centerlines
- bead height/flow
- error heatmap
- support diagnostics
- metrics/hash/status

Exit:
- preview plan hash equals stored plan hash
- no UI call from slicing worker

## Phase 4A — Bambu golden fixture acquisition
Choose exact initial Orca commit and Bambu 0.4 mm profile set.

Verify:
- relative E
- firmware retract off
- line numbering off
- arc fitting off
- spiral/ironing/scarf/support/raft off
- layer-change custom code motion-neutral
- structural layer-boundary markers/state

No injector code enabled until fixtures exist.

## Phase 4B — streaming parser dry-run
Parse only:
- modal state
- layer boundaries
- object/type tags
- Bambu custom commands needed for state confidence
- target insertion anchors

Exit:
- manually verified report matches fixture
- unknown critical state => reject

## Phase 4C — plan matcher
Match stored plan candidates to final G-code.

Exit:
- exactly one correct match
- zero/multiple/stale plan safe skip
- runtime ObjectIDs not required
- validated constant print-space -> machine-G-code translation
- inconsistent mapping safe rejection

## Phase 4D — offline emitter
On fixture copies:
- safe-ceiling travel
- relative-E candidate extrusion with filament_flow_ratio
- state restore
- markers/idempotence

Original structural G-code remains unchanged.

Exit:
- parser can re-read result
- state at resume equals saved boundary state
- no low-Z non-extruding XY travel

## Phase 4E — streaming atomic postprocess
Implement:
1. validation pass
2. temp-file emission pass
3. sanity pass
4. atomic replace

Exit:
- original bytes unchanged on every failure
- repeated export/upload copies handled independently

## Phase 5 — first physical PoC
Only after all prior gates.

Initial:
- supported Bambu 0.4 mm
- PLA
- one-volume calibration coupon
- simple nested/self-supported slope

Sequence:
1. 5 degree coupon
2. 10/20 degree
3. smooth 1-30 degree surface

Inspect:
- nozzle contact
- overbuild
- bonding
- dimensional bias
- surface roughness

Unexpected physical behavior returns project to model/spec review.

## Phase 6 — benchmark
Compare:
- normal
- fine conventional
- ZAA-only
- ZAA + SubEdge

Measure:
quality / time / material / failure modes.

## Phase 7 — controlled expansion
One capability at a time:
- additional Bambu profiles
- more complex local surface bands
- holes/multiple loops
- multi-volume CSG
- multiple objects/instances
- supports/overhangs
- absolute E
- arcs
- other firmware
- multitool last

Each requires fixtures/tests and ADR when safety semantics change.

## Phase 8 — production plugin
- compatibility matrix
- pure-Python wheel
- tolerance/quality UI
- performance optimization
- regression corpus
- analysis-only fallback
