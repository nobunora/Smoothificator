# Test Strategy and Release Gates

Tests are organized by ownership boundary so failures identify the responsible module.

## A. Architecture tests
Owner: tests/architecture/

Check:
- forbidden imports;
- immutable boundary DTOs;
- canonical serializer ownership;
- no live Orca type leakage into domain/engine;
- only canonical ADR numbers/files exist.

Blocks all later phases.

## B. Domain/flow tests
Owner: tests/unit/domain + tests/unit/engine/

Check:
- Orca rounded-rectangle candidate flow formula;
- effective bead height above local support;
- 0.08 mm rule applies to bead height, not pairwise Z;
- ZAA local effective flow ratio parity;
- invalid width/height/flow;
- deterministic hashing;
- Orca volumetric-to-E parity including non-unity filament_flow_ratio.

## C. Surface-band geometry tests
Owner: tests/analytic/

Check:
- mesh-plane intersection as boundary, not centerline;
- centerline offset/layout inside material;
- multiple paths at same Z;
- multiple paths at different Z;
- shallow-angle terrace coverage;
- nesting/self-support;
- outward-expanding rejection.

## D. Final-surface/error tests
Check combined finite-bead surface:
- lower structural/ZAA beads;
- candidate beads;
- upper structural/ZAA beads unchanged.

Verify:
- E_max/E_rms/E_p95/bias;
- overlap/overbuild penalties;
- candidate flow optimization;
- no structural-wall rewrite.

## E. Orca adapter contract tests
Pinned Orca:
- posSimplifyPath fires with ZAA on;
- posSimplifyPath fires with ZAA off;
- ContourZ relative-Z -> absolute-Z;
- GCode ZAA flow ratio parity;
- mesh transforms;
- feature gates;
- no live reference escape;
- cache/no-plan behavior.

## F. Plan/config/preview tests
Check:
- immutable plan;
- canonical ExecutionConfigFingerprint;
- same-config export acceptance;
- every required config-key change rejects injection;
- missing required config key rejects injection;
- separate runtime status;
- stable hash excludes runtime ObjectIDs/timestamps;
- preview hash equals injector plan hash;
- UI does not invoke optimizer/live Orca.

## G. Bambu G-code fixture tests
Each supported profile fixture records:
- exact Orca version/commit;
- machine/process profile;
- relative E;
- firmware retract off;
- line-number mode off;
- arcs off;
- layer-change custom code;
- structural boundary markers.

If any required property changes, injection support for that fixture is invalid until reviewed.

## H. Streaming parser tests
Check:
- G90/G91 tracking;
- M82/M83 tracking;
- E/feed/retraction/tool state;
- reserved layer tags;
- object/type comments;
- supported Bambu custom commands;
- unknown critical command rejection;
- no full-file memory requirement.

No writes.

## I. Plan matcher tests
Check:
- exactly one plan;
- zero plan;
- multiple plans;
- stale plan;
- runtime ObjectID changes;
- config/profile mismatch;
- constant print-space -> G-code-space translation;
- non-zero XY/Z offset mapping;
- inconsistent/ambiguous mapping rejection.

## J. Emitter tests
Check ADR-0007:
- Zsafe raise before any non-extruding XY;
- vertical descend to candidate Z;
- relative-E volume conversion with filament_flow_ratio;
- retract/unretract state;
- lower-risk ordering;
- return at Zsafe;
- restore saved upper structural state;
- no original structural extrusion modification;
- marker/idempotence.

## K. Atomic postprocess tests
Three passes:
1. validate
2. temp-file emit
3. sanity parse

Check:
- original unchanged on every failure;
- temp cleanup;
- atomic replace;
- repeated export/upload working copies;
- already-injected file no-op.

## L. Physical test gate
Physical printing forbidden until A-K pass for exact supported fixture.

Sequence:
1. simple 5 degree coupon;
2. 10/20 degree coupons;
3. continuous smooth coupon;
4. benchmark.

Any nozzle contact, severe overbuild, delamination, or dimensional failure pauses physical testing and returns to model/spec review.

## M. Compatibility expansion
Every newly supported:
- Orca version
- printer profile
- G-code mode
- object topology
- support/overhang mode
- extrusion mode
requires fixtures, regression tests, and ADR when safety semantics change.
