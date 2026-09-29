# Development Roadmap

## Phase 0 — specification/audit
Completed:
- ZAA-first architecture
- stock-Orca post-process execution
- architecture boundaries
- pre-implementation dependency audit
- ADR-0001/0002/0003

## Phase 0.5 — architecture skeleton
Before algorithms:
- normative package tree
- frozen/deep-immutable domain data
- typed errors/reason codes
- Settings validation
- canonical serializer/hash
- PlanStore + InjectionAttempt separation
- import-boundary tests
- no Orca/G-code mutation

Exit: architecture tests pass.

## Phase 1 — standalone reference engine
Steps:
1. Orca Flow parity bead model tests
2. analytic fixed/smooth slope baseline
3. final-surface model including lower + candidate + upper structural beads
4. normal-error metrics
5. arbitrary Z + flow candidate search
6. support/overlap/clearance feasibility
7. deterministic plan generation

No Orca plugin yet.

## Phase 2 — Orca snapshot Analyzer
Use posSimplifyPath.

Steps:
1. read-only hook smoke test with ZAA on/off
2. copy single-object/single-instance/single-volume snapshot
3. coordinate-frame validation on translated/rotated/scaled models
4. source mesh sectioning
5. post-simplification path extraction
6. create/store plan
7. cache/fresh-slice behavior tests

No G-code mutation.

## Phase 3 — Preview
Script capability on UI thread:
- plan geometry
- residual error
- before/after metrics
- plan hash
- runtime/injection history

## Phase 4 — G-code parser, read-only
1. dialect abstraction
2. streaming lexer/parser
3. state tracking
4. structural layer tag parsing
5. GCodeIdentity/fingerprint
6. plan selection
7. anchor validation

No writes.

## Phase 5 — Dry-run injector
1. generate insertion blocks
2. absolute/relative E restoration
3. safe layer-boundary travel
4. low-to-high subedges
5. end at next structural layer Z
6. output diff only
7. golden fixtures

## Phase 6 — Atomic injector
Two/three-pass streaming:
validation -> temp emission -> sanity parse -> atomic replace.

Test idempotence, failures, repeated export/upload copies.

## Phase 7 — First physical PoC
Only after all previous gates:
- Bambu/selected single-tool tested profile
- one calibration object/instance/volume
- 0.4 mm PLA
- simple outward slopes

Manual review of emitted G-code before print.

## Phase 8 — Benchmark
normal / fine layer / ZAA-only / ZAA+SubEdge.

Measure geometry error, roughness, time, material and failures.

## Phase 9 — Generalization
Only by ADR:
- multiple objects/instances
- multi-volume/CSG
- other pipeline/postprocess plugins
- other dialects/printers
- downward/concave geometry
