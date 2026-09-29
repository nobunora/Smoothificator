# Surface Error and Material Model

## Reference
M = ideal source-model boundary.
P = predicted final printed surface.

Primary signed error:
e_n(q) = (q - p) dot n(p)

Required metrics:
- E_max absolute normal error
- E_rms
- E_p95
- signed mean/bias

## Final printed surface
Candidate quality MUST include:
- lower structural/post-ZAA beads
- all candidate Sub-edge beads
- upper structural/post-ZAA beads Orca will still print

Sub-edges are extra material, not replacement layers.

## Orca/ZAA baseline normalization
Orca ContourZ stores each ZAA point Z as offset d from layer.print_z.

Normalize:
z_abs = layer.print_z + d

For non-ironing ZAA segments Orca scales extrusion:
h_eff = h_nominal + d
q_eff = q_nominal * h_eff / h_nominal

The baseline predictor MUST reproduce these semantics.

Printable v1 rejects ironing and scarf/sloped seams so nonzero path Z has unambiguous ZAA meaning.

## Rounded-rectangle bead model
Initial Orca parity:
q = h * (w - h * (1 - pi/4))

where:
- q = mm3_per_mm
- h = effective deposited bead height
- w = bead width

## Candidate bead height
The initial 0.08 mm limit applies to **effective bead height above local support**, not pairwise path-Z difference.

For candidate segment:
h_eff = z_nozzle - z_support

Require h_eff >= min_bead_height.

Neighboring paths may have Z differences smaller than 0.08 mm if finite-bead overlap, support, machine resolution and nozzle-envelope clearance are valid.

This is essential for shallow slopes, where paths separated laterally by about one line width may need only small Z increments.

## Geometry boundary vs tool centerline
Mesh-plane intersection C(z) is a material boundary.

It MUST NOT be emitted directly as a nozzle path.

Path layout offsets/positions centerlines on the material side using bead width and final-envelope scoring.

## Nested top-facing v1 condition
For target region:
C(z_high) must be contained in C(z_low) within tolerance.

Higher layers recede inward as Z increases.

Outward-growing/downward-facing overhang targets are rejected in printable v1.

## Surface coverage
A plan may contain many SubEdgePaths at different, closely spaced nozzle Z values.

The optimizer evaluates the union/envelope of deposited beads. It does not assume one path per nominal subdivision or one path is enough for a shallow terrace.

## Candidate flow
SubEdge segments carry accepted width/effective-height/q.

Engine accounts for:
- overlap with structural beads
- overlap between Sub-edges
- missing target volume
- overbuild
- feasible flow/shape limits

Emitter only converts accepted q to relative filament E.

## Nozzle clearance
A->B lower-to-higher order reduces collision risk but does not mathematically guarantee nozzle-body clearance when paths are close in XY/Z.

Use a configurable nozzle envelope + safety margin.

Unknown/unvalidated nozzle geometry may allow analysis but blocks physical Injection.

## Acceptance
1. predict post-ZAA baseline
2. identify residual-error regions
3. verify nested support
4. generate boundary/path candidates
5. compute support and h_eff
6. score combined final bead envelope
7. enforce nozzle/support/flow constraints
8. choose minimum-cost solution meeting tolerance
9. otherwise leave Orca/ZAA unchanged

## Regression geometry
- fixed 1/5/10/15/20/25/30 degree slopes
- smooth 1-30 degree slope
- translated/rotated/scaled copies for coordinate tests
- later domes/chamfers
