# Phase 0.5 — ADR-0043 candidate-bead bounds standalone DTO: pre-implementation review

Date: 2026-10-14
**Disposition: VALIDATED for standalone immutable value DTO only, NOT full Settings v2 schema or physical injection.**

## Accepted source / owner
- `docs/adr/0043-candidate-bead-geometry-bounds.md`: Accepted, normative values are `min_candidate_height_mm`, `max_candidate_height_mm`, `min_candidate_width_mm`, `max_candidate_width_mm`; all lengths measured in mm.
- A printable candidate must have `effective_height_mm > 0`, `width_mm > 0`, `width_mm >= effective_height_mm`, lie within each configured min/max bound and have a finite positive geometric line volume. This is an engine/algorithm feasibility test in later Phase 1A, **not** an automatic Plan/gate authorization.
- Source reviewed: `domain/settings.py` has exact immutable numeric helper `_nonnegative_finite` and research-only standalone `ErrorEstimatorConfig`, `MeshSectionPolicy`; `application/serialization.py::_FIELDS` is the single explicit canonical DTO owner. v1 `PluginSettings` still uses a fixed seven-field schema and must not gain more fields under schema `"1"`.
- Design ADR-0066 currently says the bead bounds must enter a future Settings v2 fingerprint. The Accepted ADR-0043 names above supersede **proposed** alternatives that use `min_candidate_effective_height_mm` instead of `min_candidate_height_mm`.
- No external Orca binding/physical machine fixture is used for this schema-only addition; original 216-tests evidence and 81/81 audited manifest unchanged.

## Approved narrow implementation and constraints
- Add `CandidateBeadBounds` as a standalone frozen slots dataclass in `adaptive_subedge/domain/settings.py` using exactly those four Accepted ADR field names, no defaults:
  `min_candidate_height_mm: float`, `max_candidate_height_mm: float`, `min_candidate_width_mm: float`, `max_candidate_width_mm: float`.
- Every bound is finite binary64 and strictly positive, bool excluded; min <= max for each axis. Do not impose `min_candidate_width_mm >= max_candidate_height_mm`: ADR-0043 imposes width >= effective height **per candidate**, not for all pairings of declared ranges. Candidate feasibility remains engine-owned.
- Register exactly those four declared fields in the current canonical DTO serializer; maintain existing v1 serialization and hash bytes exactly. Do not add the DTO to `PluginSettings(schema_version="1")`.
- Positive/equality bounds, invalid NaN/Inf/zero/negative/bool, swapped extrema, immutable field mutation, deterministic canonical projection, field sensitivity, and fail-closed rejection if passed as the entire v1 `fingerprint_plugin_settings`.
- This establishes no universal hardware bounds and no field defaults or printer calibration evidence. No engine candidate generation, G-code or physical behavior changes.

## Stop/gate
The complete future v2 PluginSettings semantic schema, support coverage tolerance and objective weights still require Proposed ADR-0066 adjudication, exact root version and new handoff/manifest. **This standalone DTO is not Phase 0.5 completion.**

## Verified implementation / tests / disposition

- Source `CandidateBeadBounds` immutable value schema in `adaptive_subedge/domain/settings.py` and exact `application/serialization.py::_FIELDS` registry, implementation commit `8e54aa768f1f802ba2d3ef288e887299ef9fd92a`.
- Five focused new tests `tests/unit/test_candidate_bead_bounds.py` commit `29081b1d9f0c2e47aa03f7c3497928dfc322b99c`, including exact four ADR-0043 fields, frozen dataclass, finite/strict positivity, min<=max, and no guessed cross-axis/hardware default; deterministic semantic bytes change when one declared bound changes; `fingerprint_plugin_settings` refuses the DTO as a full v1 Settings schema.
- GitHub Actions [38476672618](https://github.com/nobunora/Smoothificator/actions/runs/38476672618) on the complete source+test commit: Python 3.12 compileall PASS, **221/221 unittest PASS**.
- Accepted ADR-0043 name/field provenance supersedes earlier speculative PR #3 field spellings; the Proposed Settings v2 review packet has been corrected on Draft PR #3 at commit `34c6bdbcd50fc65128423e0606b9a458c245cab2`.
- Disposition: `validated -> implemented` **for standalone immutable candidate bead bounds schema only**. Complete v2 Settings fingerprint field composition and normalization are still **spec-change-required**. No safety-critical values or printer operating parameters were chosen; Phase 0.5 remains incomplete.
