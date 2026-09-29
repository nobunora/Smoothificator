# ADR-0005: Reconstruct surface bands, not raw mesh-intersection centerlines

Status: Accepted
Date: 2026-09-29

## Context
A mesh-plane intersection C(z) is a geometric material boundary, not an extrusion centerline.

Printing directly on C(z) would generally overgrow the part by approximately half a bead width.

Also, a single contour bead at an intermediate Z may not cover a wide shallow-angle terrace. Multiple adjacent paths can be required.

Finally, v1 support is only reliable for top-facing geometry whose material cross-section recedes/nests as Z increases.

## Decision
C(z) is used as a **target boundary**.

The planner derives an exposed surface band and lays out one or more bead centerlines inside the material side using bead width/spacing.

v1 requires local nesting:
material_cross_section(z_high) is contained in material_cross_section(z_low)
within tolerance over the target region.

Higher levels must not expand outward beyond lower support.

Each generated centerline is scored with the finite-bead model; no fixed half-width offset is assumed to be exact.

## Surface coverage
The optimizer may generate multiple paths at the same or different nozzle Z values.

Coverage quality is determined by the final bead envelope, not by centerline distance alone.

## Consequence
The project remains named Adaptive Sub-Edge, but a "sub-edge" plan may contain a local surface-band group of several extrusion paths.

## Test impact
- geometric boundary vs tool-center offset tests
- low-angle coverage tests
- nested-section support tests
- outward-expanding/overhang rejection tests
