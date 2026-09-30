# Smoothificator Upstream Analysis

Upstream: TengerTechnologies/Smoothificator

## Upstream behavior
Original Smoothificator is a G-code post-processing script.

It:
- identifies external-perimeter / outer-wall blocks;
- derives a pass count from base layer height and requested outer height;
- places repeated passes at equal Z spacing;
- repeats the same XY outer path;
- divides extrusion among passes;
- inserts Z/travel commands.

Adaptive version reads per-layer HEIGHT/min_layer_height and chooses a nearby integer pass count.

## What remains valuable
Upstream established two important practical ideas:
1. outer-wall vertical resolution can differ from the interior;
2. original outer-wall extrusion must be distributed across the smaller-height passes rather than simply adding full-flow material.

The second point is retained explicitly in ADR-0002.

## Limitations relative to this fork
Upstream:
- decides refinement from G-code, without source-mesh error;
- uses equal Z spacing;
- repeats identical XY geometry;
- has no residual-error tolerance;
- has no finite-bead optimizer;
- does not use ZAA result as the baseline;
- does not separate preview plan from execution plan.

## This fork's architecture
The current target is NOT "normal path generation inside Orca's mutable geometry graph."

It is:

1. geometry-time read-only analysis at Orca posSimplifyPath;
2. create immutable error-driven WallPassSchedules from source mesh + final simplified paths;
3. preview the exact plan;
4. let Orca export normal G-code;
5. at official psGCodePostProcess:
   - match the plan to the exported wall loop;
   - reduce/rewrite the original upper-wall extrusion;
   - inject non-uniform intermediate contours lower-Z first.

Legacy:
target outer layer height -> equal passes -> duplicate XY -> split E

New:
post-ZAA residual error -> optimize true intermediate contours + Z schedule -> redistribute outer-wall flow -> validated G-code execution

## Code-reuse policy
The legacy scripts remain reference material.

Do not directly extend their regex/block-processing architecture for the new injector. The new G-code implementation uses an explicit parser/state machine and all-or-nothing validation.

Legacy scripts are not modified unless an explicit task requires it.
