# ADR-0048: Define one deterministic nominal bead-solid geometry for v1

Status: Accepted
Date: 2026-10-08

## Context

The project already defines:
- effective bead height h;
- nominal/effective width w;
- geometric line volume q_geom.

But a finite-bead surface predictor also needs an exact 3D solid construction.

Without one, independent implementations can differ at:
- segment sides;
- polyline corners;
- open-path seam ends;
- variable segment height/width transitions.

A ZAA-specific inconsistency is especially important.

Orca keeps ExtrusionPath.width metadata but scales emitted ZAA extrusion approximately with:

q_zaa = q_nominal * h_local / h_nominal

If an implementation combines:
- original path.width unchanged;
- new local h_local;
- q_zaa;

the rounded-rectangle area formula generally cannot satisfy all three simultaneously.

One quantity must be treated as derived for the nominal predictor.

## Decision

Define one versioned NominalBeadSolidV1.

### Cross-section

For a non-bridge segment, the local cross-section is a horizontal-major-axis stadium / rounded rectangle in the plane perpendicular to the XY path tangent and vertical Z axis.

Its:
- total vertical height = h;
- total horizontal width = w;
- area = h * (w - h * (1 - pi/4));
- validity requires w >= h > 0.

### Vertical placement

For a candidate SubEdge segment:
- top Z = parent path command_z_mm;
- bottom Z = command_z_mm - h_eff;
- center is midway between top/bottom.

For a structural planar segment:
- top/bottom follow the corresponding nominal layer/path height convention.

For a ZAA structural segment:
- h = h_local;
- q_geom = q_nominal * h_local / h_nominal;
- derive the predictor effective width from q_geom and h:

w_effective = q_geom / h + h * (1 - pi/4)

The stale nominal ExtrusionPath.width remains diagnostic metadata; it is NOT simultaneously imposed as the local ZAA predictor width when that would violate the area relation.

### Along-path sweep

Each polyline segment sweeps its local stadium cross-section along the segment centerline.

At polyline vertices:
- nominal solid is the geometric union of adjacent segment sweeps;
- no double-volume counting in the surface envelope.

At an open path start/end:
- v1 uses a flat axial cap at the planned endpoint for the nominal model.

Start/stop blobs, pressure swelling, and thermal deformation are empirical effects and are NOT silently added to the nominal model.

### Segment-local changes

Within one SubEdgePath, command Z is constant but h/w/q may differ by segment.

The v1 solid treats each segment with its own validated local cross-section and uses union at the shared vertex.

No hidden interpolation rule may alter immutable segment intent.

### Explicit source-segment top query — 2026-10-16

For the bounded nominal-support cell query, source start/end XYZ are immutable
normalized nozzle coordinates. Within one segment width w and effective height h
are constant; require w>=h>0 and nonzero XY length. No interpolation of width or
height is introduced. A sloped structural/ZAA segment uses the explicit linear
nozzle locus z(t)=start.z+t*(end.z-start.z), 0<=t<=1. A candidate source segment
remains constant-command-Z. Source adapters must establish these normalized
inputs; this mathematical convention does not assert actual Orca parity.

Let r=h/2, a=(w-h)/2 and u the lateral distance from the segment centerline.
The swept solid's top is z(t) when abs(u)<=a, and
z(t)-r+sqrt(r*r-(abs(u)-a)**2) when a<abs(u)<=a+r; elsewhere it is absent.
The closed axial interval [0,1] retains the existing flat caps. In particular,
the XY projection is a rectangle, not an XY capsule. For a union, the top is
the maximum of all present source tops, never their sum or an average. This
definition includes the circular-section limit a=0 and curved lateral edges.

ADR-0044's closed cell query uses certified bounds on this actual nominal top.
It must account for partial higher overlaps and must not choose a lower support
surface to avoid an obstruction. Source chronology, candidate eligibility and
actual collision/physical contact remain distinct checks.

### Surface extraction

FinalSurfaceEnvelope is the exposed boundary of the union of the relevant nominal bead solids.

ChronologicalSupportEnvelope uses the corresponding union of solids that have actually been printed at that simulated time.

Internal overlap surfaces are not treated as exposed target surfaces for error scoring.

## Requirements / invariants introduced

- One bead-solid owner/implementation.
- width/height/q_geom are algebraically consistent.
- ZAA local predictor width is derived when local volume/height changes.
- Candidate seam/gap end-cap behavior is deterministic.
- Error/support/collision planners consume the same nominal solid representation.

## Physical-model limitation

This is a nominal geometric model, not a claim that real extrusion forms an exact stadium with flat path ends.

Physical calibration may later replace/correct it through a versioned empirical model without changing the geometry/execution ownership boundary.

## Test impact

Add:
- area parity for w/h/q;
- w<h reject;
- ZAA effective-width reconstruction;
- adjacent segment union;
- open seam flat-cap behavior;
- internal-overlap surfaces excluded from exposed envelope;
- deterministic solid under path reversal/canonicalization where geometry should be equivalent.

## Rollback / disable condition

Inconsistent local h/w/q or inability to construct the nominal solid => candidate/baseline region non-injectable.
