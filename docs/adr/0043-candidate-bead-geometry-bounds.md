# ADR-0043: Make candidate bead geometry bounds explicit

Status: Accepted
Date: 2026-10-08

## Context

The v1 rounded-rectangle bead model uses:

`q = h * (w - h * (1 - pi/4))`

Earlier documents required only positive width/height and generic calibrated bounds.

Orca's non-bridge Flow implementation assumes the normal rounded-extrusion geometry has `width >= height` in operations such as spacing/cross-section transforms.

Allowing a candidate with width smaller than height can produce a mathematically positive area while violating the intended geometric model.

The upper printable width/height bounds are also hardware/material dependent and must not be invented by an implementation agent.

## Decision

For every printable v1 candidate segment using the rounded-rectangle model:

- `effective_height_mm > 0`;
- `width_mm > 0`;
- `width_mm >= effective_height_mm`;
- `effective_height_mm >= min_candidate_height_mm`;
- `effective_height_mm <= max_candidate_height_mm`;
- `width_mm >= min_candidate_width_mm`;
- `width_mm <= max_candidate_width_mm`;
- geometric line volume is finite and positive.

The min/max candidate width/height bounds are validated plugin Settings and participate in PluginSettingsFingerprint.

The existing initial research value `min_candidate_height_mm = 0.08` for the 0.4 mm nozzle target remains a research default.

Physical injection requires the max/min width/height envelope used by the fixture to have documented calibration/evidence. The implementation MUST NOT infer a universal max width from nozzle diameter.

## Requirements / invariants introduced

- Rounded-rectangle candidate geometry has an explicit validity domain.
- Invalid width/height combinations are infeasible before flow/E generation.
- Settings own printable bounds; engine code does not hard-code hidden limits.

## Test impact

Add:
- width == height accepted;
- width < height rejected;
- below/above configured height bounds rejected;
- below/above configured width bounds rejected;
- NaN/Inf/non-positive geometry rejected.

## Rollback / disable condition

Missing physical-mode bead bounds => analysis-only.
