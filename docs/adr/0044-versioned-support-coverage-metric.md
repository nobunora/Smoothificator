# ADR-0044: Define a versioned deterministic support-coverage metric

Status: Accepted
Date: 2026-10-08

## Context

Current v1 documents correctly separate ChronologicalSupportEnvelope from FinalSurfaceEnvelope, but still use phrases such as "sufficient overlap/contact" without defining one authoritative metric.

That leaves a serious implementation ambiguity:
two implementations could accept/reject the same candidate using different support interpretations.

Physical support thresholds are empirical, so hard-coding an arbitrary percentage during architecture work is also unacceptable.

## Decision

Introduce one versioned `SupportCoverageMetric` owned by the engine contract.

For each candidate segment:

1. construct the candidate XY footprint from its finite bead width and centerline segment;
2. query ChronologicalSupportEnvelope over that footprint using deterministic sampling/integration;
3. classify footprint locations as support-eligible only when the local support top produces a valid effective bead-height/contact state;
4. compute at minimum:
   - `supported_area_fraction`;
   - `minimum_contiguous_support_width_mm`;
   - `minimum_effective_height_mm`;
   - `maximum_effective_height_mm`;
5. compare these values with validated plugin Settings.

Required settings include:
- `min_support_area_fraction`;
- `min_support_contact_width_mm`;
- support-query numeric tolerance/version.

These settings participate in PluginSettingsFingerprint.

No universal physical defaults are claimed except where a research fixture explicitly supplies them.

For physical injection, support thresholds are fixture/calibration evidence and are independently reviewed.

## Same-Z and dependency semantics

The metric consumes only ChronologicalSupportEnvelope material.

It therefore preserves ADR-0032:
- no future material;
- no cyclic dependency;
- same-Z candidates cannot provide required vertical support to one another in v1.

## Requirements / invariants introduced

- One support metric owner.
- "Sufficient support" is never a free-form implementation judgment.
- Missing/unvalidated physical support thresholds => analysis-only.

## Test impact

Add analytic fixtures for:
- fully supported footprint;
- partial support;
- narrow disconnected contact;
- same area fraction but insufficient contiguous width;
- future-material exclusion;
- lower-candidate support;
- deterministic results under segment reversal/canonicalization.

## Rollback / disable condition

Support metric fails to converge/resolve => candidate infeasible.


## Refinement note

ADR-0058 is the canonical hard-acceptance refinement contract. Fixed-resolution sampling alone is insufficient; conservative bounds and convergence are required.
