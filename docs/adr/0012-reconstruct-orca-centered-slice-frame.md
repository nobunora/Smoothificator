# ADR-0012: Reconstruct Orca's centered slice frame exactly for v1 source geometry

Status: Accepted
Date: 2026-09-30

## Context

The earlier implementation specification mapped source mesh vertices with:

PrintObject.trafo() @ ModelVolume.matrix()

That is incomplete.

In audited OrcaSlicer source commit `789f848694b955d293ca6b277d1c8046aa6f7436`:
- `PrintObjectSlice.cpp` slices with `PrintObject::trafo_centered()`;
- `PrintObject::trafo_centered()` applies `m_trafo` and pre-translates XY by `-m_center_offset`;
- `m_center_offset` is the XY center of `ModelObject::raw_bounding_box()`;
- `raw_bounding_box()` is built from ModelPart volumes transformed by the first ModelInstance transformation with translation removed;
- `PrintObject.trafo()` is the print transformation used by the PrintObject and may include shrink compensation.

The Python plugin bindings expose `ModelInstance.matrix()`, `ModelVolume.matrix()`, `PrintObject.trafo()`, and the source mesh, but not `center_offset` or `trafo_centered()`.

## Decision

Printable v1 requires exactly:
- one PrintObject;
- one total ModelInstance in its source ModelObject, not merely one printable instance;
- one positive ModelPart volume.

The Orca adapter reconstructs the same centered slice frame:

1. Copy the source ModelInstance 4x4 matrix.
2. Create an instance-no-offset transform by zeroing its affine XYZ translation while retaining rotation/scale/mirror.
3. Transform the ModelPart mesh by:

   instance_no_offset @ volume_matrix

4. Compute the transformed raw bounding-box center `C=(Cx,Cy)`.
5. Transform source mesh vertices for domain analysis using:

   Translate(-Cx,-Cy,0) @ print_object_trafo @ volume_matrix

6. Verify the resulting mesh footprint against `PrintObject.bounding_box()` / sliced-path geometry within a versioned tolerance before making an injectable plan.

All matrix multiplication conventions are verified by fixtures. Do not infer them from NumPy storage layout alone.

## Invariants introduced

- Domain source mesh and simplified extrusion paths share the same centered PrintObject slice frame.
- No source-mesh plan is injectable unless the frame parity fixture/check passes.
- Multiple total ModelInstances are analysis-only until a later ADR defines instance-specific reconstruction.

## Alternatives considered

- Use `PrintObject.trafo()` directly: rejected; misses center offset.
- Infer an arbitrary best-fit transform from mesh to toolpath: rejected as primary construction because it can hide a wrong source transform.
- Require custom Orca binding for `trafo_centered()`: unnecessary for v1 because required inputs are already exposed.

## Safety impact

Critical. A frame error would move every planned SubEdge relative to the real model/toolpath.

## Compatibility impact

Tightens v1 from one printable instance to exactly one total source ModelInstance.

## Performance / resource impact

One additional transformed-mesh bounding-box pass during snapshot construction.

## Observability impact

Snapshot diagnostics record:
- reconstructed center offset;
- transform parity error;
- source instance/volume counts.

## Test / validation impact

Add fixtures for:
- translated instance;
- rotated instance;
- scaled instance;
- shrink-compensated PrintObject transform;
- mirrored transform if supported by the target fixture;
- mismatch rejection.

## Migration / rollout

Replace the old direct `PrintObject.trafo() @ volume.matrix()` formula everywhere before engine implementation.

## Rollback / disable condition

Any transform parity failure marks the plan non-injectable.

## Open questions

None for the one-instance/one-volume v1 scope.

Supersedes: the source-mesh transform formula previously stated in IMPLEMENTATION/ARCHITECTURE.
