# ADR-0051: Gate Orca slice-geometry modifiers that change the target boundary

Status: Accepted
Date: 2026-10-08

## Context

Adaptive Sub-Edge v1 defines its ideal target surface from the centered/oriented source ModelPart mesh.

Current OrcaSlicer may intentionally modify sliced geometry after mesh intersection, including:
- xy_contour_compensation;
- xy_hole_compensation;
- elephant-foot compensation over one or more lower layers;
- make-overhang-printable / conical-overhang geometry rewriting;
- slicing/closing modes that repair or morph slice contours.

Those changes are valid Orca user intent.

If the plugin continues to compare final structural paths against the raw source mesh without modeling those modifiers, it may classify the intentional Orca offset as "surface error" and add material that counteracts the user's dimensional/support correction.

That is a target-definition conflict, not merely a parser issue.

## Decision

Printable v1 uses the source mesh as the authoritative target only when relevant Orca slice-boundary modifiers are absent for the target interaction region.

### Global v1 gates

For the first physical fixture:
- xy_contour_compensation = 0;
- xy_hole_compensation = 0;
- slicing_mode = regular;
- slice-closing / contour-repair behavior that can morph the simple target section is disabled by the pinned fixture contract;
- make_overhang_printable is disabled for the target object/regions.

The exact key/value representation is pinned in the Orca compatibility descriptor and ExecutionConfigFingerprint.

### Elephant-foot compensation

Elephant-foot compensation need not be globally zero if the candidate target interval is provably above every layer to which Orca applies it.

No candidate:
- may be generated in;
- may use as its local final-structural target;
a layer whose outer contour was modified by elephant-foot compensation.

If affected-layer determination is ambiguous, injection is disabled.

### Other geometry-changing options

The compatibility audit for each supported Orca family maintains an explicit allowlist/gate for slice-boundary modifiers.

A newly introduced Orca option that can modify object slice geometry after source-mesh intersection is unsupported until:
- it is proven irrelevant for the target region; or
- the target-surface model is extended by a later ADR.

## Requirements / invariants introduced

- "source mesh is the ideal target" and "Orca intentionally compensated slice is the target" are never mixed silently.
- ExecutionConfigFingerprint includes relevant geometry-modifier semantics.
- Preview reports the exact gate preventing injection.
- The plugin never silently disables the user's Orca compensation settings.

## Alternatives considered

- Reconstruct the fully compensated arbitrary-Z target surface in v1: rejected as substantially more complex.
- Ignore compensation because it is usually small: rejected; values are intentional dimensional corrections and may be comparable to SubEdge tolerances.
- Compare only against final structural G-code: rejected because then the plugin no longer reconstructs the source target surface.

## Safety / dimensional impact

High for dimensional correctness and user intent.

## Test impact

Add:
- xy_contour_compensation nonzero -> reject;
- xy_hole_compensation nonzero -> reject for the first fixture;
- make_overhang_printable active -> reject;
- unsupported slicing/closing mode -> reject;
- candidate inside elephant-foot compensated layer -> reject;
- candidate safely above all compensated layers -> eligible when all other gates pass;
- relevant config change invalidates ExecutionConfigFingerprint.

## Rollback / disable condition

Unknown slice-boundary modifier semantics => analysis-only.
