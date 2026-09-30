# Development Roadmap

Implementation is gated. Do not advance until the previous phase exit criteria pass.

## Phase 0 — specification and audit
Completed:
- ZAA-first architecture
- stock-Orca post-process execution
- architecture boundaries
- ADR process
- pre-implementation source audit
- hook change to posSimplifyPath
- coordinate normalization
- outer-wall flow redistribution
- narrowed v1 injection domain

Exit: normative docs consistent; audit has no known implementation impossibility in v1 domain.

## Phase 0.5 — architecture skeleton
Create package tree only.

Implement:
- frozen domain DTOs
- typed errors/reason codes
- Settings validation
- canonical serializer/hash
- PlanStore + status store interfaces
- import-boundary tests

No Orca/G-code/optimizer implementation.

Exit:
- architecture tests pass
- no forbidden imports
- hash deterministic

## Phase 1A — flow and pass-schedule primitives
Implement/test:
- Orca-compatible rounded-rectangle flow formula
- command-Z/effective-height semantics
- WallPass / OriginalWallRewrite / WallPassSchedule
- no-refinement identity schedule

Exit:
- reference flow cases match Orca formula
- invalid height/width rejected

## Phase 1B — standalone geometry/error engine
Implement:
- mesh plane section
- finite-bead envelope
- normal-error metrics
- candidate generation
- whole-loop Z schedule optimizer
- support/non-crossing checks
- cost model

Use analytic fixed-angle + smooth coupons.

Exit:
- optimizer reduces error on known geometry
- deterministic results
- no G-code dependency

## Phase 2A — Orca coordinate/snapshot adapter
Stock Orca, read-only:
- posSimplifyPath hook
- copy mesh/path/config
- relative path-Z -> absolute Z conversion
- source mesh transform validation
- feature gate detection

Exit:
- transform/coordinate fixtures pass
- ZAA on/off both produce snapshots
- no live refs escape

## Phase 2B — Orca analyzer
Wire snapshot -> engine -> immutable plan.

No G-code mutation.

Exit:
- plan generated from real Orca coupon
- unsupported configurations produce stable non-injectable reason

## Phase 3 — Plugin preview
Script capability:
- plan paths
- rewritten top wall
- Z/effective heights
- error heatmap
- metrics/hash/status

Exit:
- preview hash equals stored plan hash
- UI never touches live slicing objects

## Phase 4A — G-code fixture acquisition
Before parser mutation:
- choose exact supported Orca version
- choose exact Bambu/printer profile
- generate golden coupon G-code
- verify G90 absolute XYZ
- verify M83 relative E in target
- arc fitting off
- identify layer/outer-wall comments/anchors

If fixture does not satisfy assumptions, update spec/ADR before implementation.

## Phase 4B — parser/state machine dry-run
Parse only, no writes.

Exit:
- full target fixture parses
- expected layer/loop/state report matches manually verified fixture
- unknown critical command causes safe rejection

## Phase 4C — plan matcher
Match stored plan candidates to G-code.

Exit:
- exactly-one match on correct fixture
- zero/multiple candidates fail safely
- nondeterministic ObjectIDs not required

## Phase 4D — outer-wall rewrite offline
Rewrite copied fixture only:
- scale/recompute relative-E increments for reduced top-pass height
- preserve XY/comments/non-target bytes where feasible

Exit:
- no-refinement output byte-identical
- refined expected output golden test passes

## Phase 4E — intermediate-pass emitter offline
Emit lower-Z-first passes into copied fixture.

Exit:
- correct E from mm3/mm and filament area
- state restoration tests
- parser re-reads modified output
- idempotence markers pass

## Phase 4F — atomic postprocessor integration
Use psGCodePostProcess on working copies.

Exit:
- full validation before replacement
- all failure paths preserve original bytes
- repeated export/upload copies handled independently

## Phase 5 — first physical PoC
Only after all previous gates.

Hardware:
- 0.4 mm nozzle
- never first-layer refinement
- PLA
- single-volume fixed-angle coupon
- supported exact Orca/profile fixture family

Sequence:
1. 5° simple coupon at conservative speed
2. 10°/20°
3. continuous smooth coupon

Inspect for:
- over/under extrusion
- wall bonding
- nozzle contact
- dimensional bias

Any unexpected physical behavior may trigger spec/flow-model revision.

## Phase 6 — benchmark
Compare:
- normal
- fine conventional
- ZAA-only
- ZAA + Adaptive Sub-Edge

Measure quality/time/material/failure modes.

## Phase 7 — controlled expansion
One feature per step with tests/ADR as needed:
- multiple loops/holes
- partial-loop local schedules
- multiple volumes/CSG
- multiple objects/instances
- absolute E
- arc fitting
- additional firmware/profile families
- supports/concave geometry
- multitool last

## Phase 8 — production plugin
- pinned compatibility matrix
- wheel packaging
- tolerance UI
- performance optimization
- regression corpus
- analysis-only safe fallback

## Optional future native integration
Only if plugin evidence justifies it. Native Orca integration is not required for v1/community proof.
