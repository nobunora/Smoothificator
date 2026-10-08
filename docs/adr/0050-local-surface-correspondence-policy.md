# ADR-0050: Constrain local surface correspondence and directional metric aggregation

Status: Accepted
Date: 2026-10-08

## Context

ADR-0047 makes surface error bidirectional, preventing missing material from disappearing from the metric.

A second ambiguity remains: an unconstrained closest-point query can pair a sample with the wrong nearby surface.

Examples:
- a thin wall has a geometrically close opposite face;
- a tight concavity has another branch closer in Euclidean distance;
- candidate material near a seam could be matched to a neighboring but unrelated surface patch.

This can understate error even when both sampling directions are present.

The optimizer also needs an explicit way to aggregate separate directional RMS/p95 values into its scalar cost.

## Decision

Introduce a versioned `SurfaceCorrespondencePolicy` owned by the ErrorEstimator configuration.

### Interaction-region ownership

Every residual target region has an explicit source-surface patch / interaction-region id.

Error correspondence for that region is restricted to:
- the source patch itself plus its explicitly allowed local neighborhood;
- predicted exposed material spatially associated with that interaction region.

Do not search the entire model globally when a local region is being scored.

### Normal-aware correspondence

Source orientation/material side is already validated by ADR-0030.

For source -> predicted sampling:
1. prefer intersections/search along the source normal line within the configured signed search distance;
2. preserve sign relative to the outward normal;
3. if the normal-line query is numerically unresolved, a closest-point fallback is allowed only inside the interaction search domain and only when the predicted exposed-surface normal is compatible.

For predicted -> source:
1. search only the paired source region/local neighborhood;
2. use source normal/material-side sign;
3. reject correspondences whose normal compatibility is below the configured threshold.

### Required settings

The versioned policy contains at minimum:
- `max_surface_correspondence_distance_mm`;
- `min_surface_normal_dot`;
- interaction-neighborhood expansion/tolerance;
- normal-ray numeric tolerance/version;
- closest-point fallback policy version.

These values participate in PluginSettingsFingerprint.

A sample with no valid correspondence inside the permitted domain is outside tolerance / unresolved, not silently ignored.

### Directional aggregation

Keep directional metrics authoritative:
- E_max_pred_to_src
- E_max_src_to_pred
- E_rms_pred_to_src
- E_rms_src_to_pred
- E_p95_pred_to_src
- E_p95_src_to_pred

Hard tolerance applies independently to both directional maximums.

For public summary values:
- E_max = max(direction maxima);
- E_p95 = max(direction p95 values);
- E_rms = sqrt((E_rms_pred_to_src^2 + E_rms_src_to_pred^2) / 2).

This equal directional weighting prevents a direction with more numerical samples from dominating merely because of sample count.

For optimizer cost, directional error terms and weights are explicit plugin Settings. The optimizer MUST NOT implicitly concatenate both sample arrays and compute an implementation-dependent sample-count-weighted score.

Signed bias remains diagnostic and uses a separately documented source-normal sign convention.

## Requirements / invariants introduced

- No whole-model unconstrained nearest-surface matching.
- Opposite-face/neighbor-patch accidental correspondence is rejected.
- No missing correspondence is dropped from statistics.
- Combined summary metrics have one deterministic definition.
- Optimizer directional weights are explicit/fingerprinted.

## Test impact

Add:
- thin-wall opposite-face trap;
- close concave neighboring patch;
- normal-incompatible closest point rejected;
- no-correspondence case rejected;
- unequal sample counts do not change equal-direction E_rms aggregation;
- interaction-region boundary tolerance tests.

## Rollback / disable condition

Ambiguous/unresolved surface correspondence for a hard-metric sample => non-injectable.
