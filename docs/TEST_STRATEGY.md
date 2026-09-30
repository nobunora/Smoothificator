# Test Strategy and Release Gates

Tests are organized by ownership boundary so failures identify the responsible module.

## A. Architecture tests
Owner: tests/architecture/

Check:
- forbidden imports;
- immutable boundary DTOs;
- canonical serializer ownership;
- no live Orca type leakage into adaptive_subedge domain/engine.

Blocks all later phases.

## B. Domain/flow tests
Owner: tests/unit/domain + tests/unit/engine/

Check:
- command-Z/effective-height arithmetic;
- Orca rounded-rectangle flow reference values;
- invalid width/height;
- per-segment ZAA top-wall remaining height;
- no-refinement identity schedule;
- deterministic hashing.

## C. Geometry engine tests
Owner: tests/analytic/

Check:
- mesh plane sections;
- fixed-angle surfaces;
- smooth 1-30 degree surface;
- finite-bead envelope;
- normal error metrics;
- optimizer constraints;
- support/non-crossing logic.

No Orca dependency.

## D. Orca adapter contract tests
Owner: tests/integration/orca_adapter/

Check on pinned Orca:
- posSimplifyPath fires with ZAA on;
- posSimplifyPath fires with ZAA off;
- path Z relative-offset normalization;
- source mesh transforms;
- feature gates;
- no live reference escape.

## E. G-code parser dry-run tests
Owner: tests/fixtures/gcode + tests/unit/gcode/

Each supported profile gets golden fixtures.

Check:
- G90/G91;
- M82/M83;
- E/retraction/feed/tool state;
- layer and wall role boundaries;
- unknown state-changing command rejection;
- arc target rejection;
- wall ordering.

No file writes.

## F. Plan matcher tests
Check:
- exactly one plan match;
- zero match;
- multiple match;
- runtime ObjectID changes do not break stable match;
- stale plan rejected.

## G. Rewrite tests
Check:
- planar top wall E rewrite;
- varying-Z ZAA top wall per-segment E rewrite;
- no-refinement byte identity;
- comments/XY preserved;
- relative-E arithmetic.

## H. Emitter tests
Check:
- intermediate passes sorted lower-Z first;
- E from mm3/mm and filament diameter;
- safe state transitions;
- no unsupported command invention.

## I. Atomic injector tests
Check:
- full parse before write;
- temp/prepared output validation;
- original unchanged on every failure;
- idempotent marker behavior;
- duplicate postprocess invocation.

## J. Preview tests
Check:
- same plan hash as injector;
- status stored outside immutable plan;
- no optimizer invocation;
- no live Orca dependency.

## K. Physical test gates
Physical printing is forbidden until A-J pass for the exact Orca/profile fixture.

Physical sequence:
1. simple 5-degree coupon;
2. 10/20 degree coupons;
3. smooth slope;
4. broader benchmark.

Any unexpected over-extrusion, collision, delamination, or severe dimensional error pauses printer testing and returns project to model/spec review.

## Compatibility expansion rule
Every newly supported Orca version, printer profile, G-code mode, object topology or wall feature requires:
- fixture;
- gate tests;
- regression run;
- ADR if it relaxes a safety/architecture assumption.
