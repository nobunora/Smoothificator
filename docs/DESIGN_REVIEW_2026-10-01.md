# Adaptive Sub-Edge v1 — Principle Explanation and Human Design Review — 2026-10-01

Status: Phase 0.5 implementation-ready
Purpose: explain the audited technology in plain engineering terms and use the explanation itself as a final contradiction review.

This is an explanatory/review document, not a higher-precedence replacement for the canonical specification or ADRs.

## 1. What problem the technology solves

Ordinary FDM approximates a curved/sloped surface using structural layers.

ZAA improves that by moving points of an **existing** outer-wall path in Z.

Adaptive Sub-Edge addresses the remaining case where moving the existing path is still not enough because the available path topology cannot cover the desired surface band.

Conceptually:

```text
source model surface
        │
        ▼
normal Orca structural paths
        │
        ├── ZAA: move existing path points in Z
        │
        ▼
predicted existing finite-bead surface
        │
        ├── already within tolerance? ── yes ──> do nothing
        │
        ▼ no
residual exposed surface band
        │
        ▼
add the minimum new constant-Z surface paths
        │
        ▼
predict final structural + candidate bead envelope
        │
        ▼
accept only if error/support/collision/cost constraints pass
```

The key distinction is:

```text
ZAA
= change Z of existing topology

Adaptive Sub-Edge
= add new surface-path topology
```

They are complementary, not substitutes.

## 2. Cross-section intuition

A simplified side section:

```text
Z ↑

        ideal source surface
                    /
                   /
        [ upper structural / ZAA bead ]
                __/____
              _/
        [ B ]/          <- added SubEdge path B
           _/
      [ A ]             <- added SubEdge path A
       _/
 [ lower structural bead ]

  +--------------------------------→ X
```

The candidate paths do NOT become full intermediate structural layers.

They are local surface-only extrusion paths intended to fill part of the residual surface band.

Each candidate path has one constant command Z in v1.

Several candidates can:
- share the same Z;
- use different independently optimized Z values.

## 3. Mesh intersection is not the nozzle path

At candidate height Z:

```text
source mesh plane section
          │
          ▼
target MATERIAL boundary
          │
          │  not printable directly
          ▼
derive material-side surface band
          │
          ▼
place nozzle centerline(s) inside material
```

Why:

```text
If the bead center were placed directly on the source boundary:

        bead
      (=====)
         ^
         |
 source boundary

part of the bead would extend outside the model.
```

Therefore the optimizer reasons about finite bead width/height, not infinitely thin contour lines.

## 4. Two different material states

This is a central design correction.

### FinalSurfaceEnvelope

Used to answer:

> What will the completed part surface look like?

It may include future upper structural beads and every accepted SubEdge bead.

### ChronologicalSupportEnvelope

Used to answer:

> What material physically exists when this candidate is printed?

It contains only material already printed.

```text
time ──────────────────────────────────────────────→

lower structural material
██████████████████████████████████████████████████

candidate A
                 ███████

candidate B
                           ███████

upper structural layer
                                      █████████████


When printing A:
support = lower structural material only

When printing B:
support = lower structural + already printed A
          if geometry proves A can support B

Upper structural material:
NOT usable as support for A or B,
because it does not exist yet.
```

Candidate dependencies must be acyclic.

Same-Z candidates cannot require each other as vertical support in v1.

## 5. Effective bead height, not "Z spacing"

The initial 0.08 mm limit means:

```text
effective bead height
= nozzle command Z - local supporting surface Z
```

not:

```text
candidate Z difference >= 0.08 mm
```

Example:

```text
candidate A Z = 4.080
candidate B Z = 4.115

difference = 0.035 mm
```

This is not automatically invalid.

If A and B occupy different lateral positions and each has valid local support/effective height, they may both be printable.

This is important on shallow slopes where many laterally adjacent paths may have very similar absolute Z.

## 6. Segment-local flow

One constant-Z path can cross a support surface whose height changes.

Therefore:

```text
SubEdgePath
  command Z = constant

segment 1:
  support Z = 4.000
  h_eff = 0.100

segment 2:
  support Z = 4.015
  h_eff = 0.085

segment 3:
  support Z = 4.005
  h_eff = 0.095
```

The path remains planar, but its segment-local effective bead height and volumetric intent may change.

This avoids turning Adaptive Sub-Edge into another general non-planar path generator.

## 7. Geometric volume and commanded volume are different

The ideal bead geometry uses:

```text
q_geom = nominal geometric mm3/mm
```

For the initial rounded-rectangle model:

```text
q_geom = h * (w - h * (1 - pi/4))
```

Orca-style G-code material command uses:

```text
q_cmd
 = q_geom
 * print_flow_ratio
 * filament_flow_ratio
 * optional outer_wall_flow_ratio
```

These are intentionally separate.

A filament flow ratio of 0.98 is not treated as proof that the physical bead is exactly 2% geometrically smaller.

The real physical mapping is a later calibration problem.

## 8. Original structural wall remains unchanged

v1 does NOT split/rewrite the original Orca outer wall like legacy Smoothificator.

Instead:

```text
existing lower/upper structural beads
             +
new candidate SubEdge beads
             ↓
combined final finite-bead prediction
```

If added material causes too much overbuild when the unchanged upper wall is later printed, that candidate is rejected.

This is a deliberate simplification for stock-Orca safety.

## 9. Candidate seam is part of geometry

A closed added contour must not be magically opened only during G-code writing.

Before the plan is frozen:

```text
closed candidate loop
        ↓
deterministic orientation
        ↓
deterministic start/seam
        ↓
explicit candidate seam gap
        ↓
OPEN immutable SubEdgePath
        ↓
surface scoring + preview + injection all use this exact geometry
```

Thus Preview does not show a materially different path from what will be emitted.

## 10. Immutable plan versus final G-code commands

The plan owns **intent**, not final machine serialization.

Plan stores:
- print-space geometry;
- command Z;
- geometric mm3/mm;
- commanded mm3/mm;
- order/dependencies;
- seam/gap;
- safety intent.

Final G-code E cannot be frozen yet because:

```text
plan coordinate
   ↓
machine translation
   ↓
Orca-compatible XYZ quantization
   ↓
actual emitted segment length
   ↓
derive E
   ↓
Orca-compatible E quantization
```

This does NOT violate the single-source-of-truth rule.

The postprocessor performs a deterministic encoding of immutable plan intent; it is not allowed to re-optimize or alter the plan.

## 11. Two coordinate systems

Geometry engine:

```text
Orca centered PrintObject slice-space
```

Final printer G-code:

```text
machine coordinates
= print-space
+ instance/origin effect
- active extruder XY offset effect
+ printer Z offset effect
```

For v1 one-instance/one-tool scope this must reduce to one validated constant translation:

```text
G = P + (dx, dy, dz)
```

The translation is derived from existing Orca structural G-code, not guessed from profile defaults.

## 12. Final G-code matching

The path seen at posSimplifyPath is not expected to have identical point ordering in final G-code.

Orca can:
- move the seam;
- split the closed loop;
- clip seam_gap;
- subdivide lines.

So the matcher uses shape equivalence:

```text
same closed shape
+ cyclic start invariant
+ seam split invariant
+ collinear subdivision invariant
+ one expected seam-gap missing interval
+ translation / quantization tolerance
```

Exactly one match is required.

Ambiguity means no injection.

## 13. Actual machine state, not nominal layer state

At a layer-change marker, Orca may have updated its internal nominal layer Z without already emitting the corresponding physical Z motion.

Therefore:

```text
DO NOT:
"restore to the expected upper layer Z"

DO:
parse actual emitted machine state
save it
temporarily execute candidates
restore exactly that state
resume original bytes
```

This preserves Orca's own deferred motion behavior.

## 14. Retraction

Initial printable v1 uses relative E.

If the anchor is already retracted by R mm:

```text
saved state: retracted R

safe travel
↓
at candidate start:
unretract exactly R
↓
print candidate
↓
retract exactly R
↓
safe travel

finish:
same retracted R state as before injection
```

The original Orca code later performs its original unretract.

This prevents double-retraction.

## 15. Physical tool clearance is chronological

The final validator does not check only the new candidate centerline.

It simulates time.

```text
existing printed material
        ↓
plugin raise/travel/descent
        ↓  ToolClearanceProfile swept check
candidate A extrusion
        ↓
A becomes printed obstacle
        ↓
plugin travel to B
        ↓  check against existing + A
candidate B extrusion
        ↓
B becomes printed obstacle
        ↓
restore original state
        ↓
resume original Orca motion
        ↓  check against existing + A + B
later ZAA / travel / extrusion
```

This fixes the crucial postprocessor problem:

> Orca could not plan around material that did not exist when Orca sliced the model.

ToolClearanceProfile therefore applies to BOTH:
- plugin-generated motion;
- resumed original Orca motion.

## 16. File safety

Final modification is binary/byte-preserving.

```text
original G-code
     │
     ├─ Pass 1: read-only validation
     │
     ├─ Pass 2: copy raw bytes to same-directory temp
     │           + add only validated insertion bytes
     │
     ├─ Pass 3: sanity validation
     │
     ▼
atomic replace

failure anywhere before replace
     ↓
original file remains byte-for-byte unchanged
```

Normal unsupported conditions return PluginResult.Skipped, not an error that destroys a valid Orca export.

# Design Review

## A. Does Adaptive Sub-Edge still have a distinct technical identity from ZAA?

PASS.

ZAA changes an existing path's Z.

Adaptive Sub-Edge adds new path topology.

The constant-Z-per-added-path v1 restriction preserves this distinction.

## B. Does "add material but do not rewrite original wall" create a contradiction?

No logical contradiction remains.

It creates a feasibility constraint.

The final completed-surface model includes the unchanged original structural wall. If an added candidate causes unacceptable overbuild after that wall is printed, the optimizer must reject it.

This may reduce the number of feasible regions, but it is internally consistent.

## C. Could the optimizer use future material as support?

Previously ambiguous.

Resolved by ADR-0032.

Support uses ChronologicalSupportEnvelope only.

Final error uses FinalSurfaceEnvelope.

These are separate concepts.

## D. Could two candidate paths support each other circularly?

Previously ambiguous.

Resolved:
- dependencies are acyclic;
- support edges point only to earlier material;
- same-Z paths cannot require each other as vertical support in v1.

## E. Is constant-Z path compatible with segment-local bead height?

Yes.

Nozzle Z is constant.

Support Z may vary.

Therefore effective bead height and segment flow may vary without making the path non-planar.

## F. Does final-E derivation after planning violate immutable-plan semantics?

No.

The plan owns commanded volume-per-length and high-precision geometry.

Machine coordinate mapping and formatter quantization are deterministic serialization steps.

Postprocess may derive commands but may not change geometry/flow policy.

## G. Is plugin safe-ceiling travel sufficient for collision safety?

No.

This was an important earlier gap.

Resolved by ADR-0025 + ADR-0033:
- plugin motions are checked;
- later original Orca motions are checked;
- material state advances chronologically.

## H. Can software prove arbitrary nozzle/hotend physical safety from Orca config alone?

No.

This is explicitly NOT claimed.

Physical mode requires ToolClearanceProfile evidence for the exact tested hardware.

## I. Is the bead model a proven physical model?

No.

The current rounded-rectangle/nominal volume model is a controlled reference model.

The biggest scientific uncertainty before quality claims is the empirical mapping between:
- local support geometry;
- width/height;
- speed;
- temperature/cooling;
- pressure state;
- commanded flow;
and actual bead envelope.

This is intentionally a Phase 5/6 calibration task.

## J. Could segment-local flow changes cause pressure/transient artifacts?

Yes, this is a real residual physical risk.

It is not a Phase 0.5 architecture blocker.

Initial v1:
- disables adaptive PA;
- retains supported static PA state;
- uses conservative speed;
- uses physical coupons before quality claims.

If experiments show unacceptable flow-transition artifacts, a future ADR may introduce:
- flow-gradient limits;
- minimum segment length;
- smoothing of segment flow commands;
- explicit candidate acceleration/PA policy.

Do not add those before evidence exists.

## K. Could cooling/fan state differ from the ideal outer-wall state?

Yes.

Candidate extrusion inherits the validated current machine/fan environment unless a later contract explicitly changes it.

This is a physical-quality calibration risk, not a current logical inconsistency.

It must be observed in physical coupons before broad claims.

## L. Is stock Orca still sufficient?

For the narrowed v1 architecture: yes.

Required capabilities are available:
- post-simplification read-only geometry;
- source mesh/model snapshot;
- final G-code postprocess seam;
- plugin config;
- Script preview capability.

The architecture deliberately validates final execution instead of requiring live path insertion into Orca internals.

## M. What is actually ready now?

Ready:
- Phase 0.5 architecture/data-contract implementation.

Not yet ready:
- physical printer injection.

Later gates still need:
- exact Orca/Bambu fixtures;
- parser/matcher/emitter implementation;
- ToolClearanceProfile measurements/evidence;
- blind review;
- physical coupon calibration.

# Final review conclusion

No remaining material logical or source-API contradiction is known in the **Phase 0.5 implementation scope**.

The full v1 architecture is technically coherent as a staged research implementation, but its physical-quality claims remain intentionally unproven until calibration.

The most important residual risks are empirical, not architectural:

1. real bead geometry versus nominal finite-bead model;
2. pressure/flow transients from segment-local flow variation;
3. cooling/thermal interaction;
4. physical ToolClearanceProfile accuracy;
5. compatibility drift in experimental Orca plugin APIs;
6. computational cost of large-model optimization + chronological clearance checks.

These risks are already assigned to later explicit test/review gates and do not justify changing the Phase 0.5 architecture before evidence exists.
