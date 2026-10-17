# Orca read-only model-world convex chord preview

Status: SPEC_VALIDATED for the isolated read-only research preview.

Independent implementation-lead repository review accepted ADR-0068 after checking
the source-verified matrix/NumPy dependency, narrowly scoped model-world frame
exception, unchanged research-archive safety gates and worker-post lifecycle.
No material conflict remains in this bounded scope. Actual runtime/UI verification
remains required before reporting that the preview runs in the target Orca.

Authority: ADR-0068 owns the isolated Script/UI package, coordinate exception,
bounded lifecycle and shared exact preview API. ADR-0005 owns unscored proposals;
ADR-0030/0059 own reused geometry. Printable/Plan/G-code contracts are unchanged.
Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `7e96ba2c2f77717503fcee1e22e8c6de3ba3501e`

Implement smoothificator_preview adapters/UI/entrypoint as a separate distribution.
Add immutable ConvexChordPreview and the same-owner propose_convex_chord_preview
entrypoint sharing fresh embedding/section with existing proposal generation.
No PlanStore or slicing/postprocess capability; keep existing research ZIP intact.

UI-thread snapshot: exactly one object, one total printable instance, one ModelPart;
bounded indexed mesh copy and validated instance@volume transform. Report the
explicit orca_model_world_mm_v1 frame, not centered PrintObject geometry. NumPy
matrix access is required and must be verified/pinned for the target interpreter.
Source-example evidence is documented in ADR-0068; actual runtime receipt remains
a separate verification obligation, never inferred from unit tests.

HTML displays exact source-section-derived render geometry and unscored proposals
with input controls Z/axis/width/trim/positions and explicit Generate/Cancel.
Use the ADR's fixed operational limits and one job owner; UI closes cancel workers,
15-second deadline fails incomplete, stale results cannot revive closed windows.
Escape all untrusted strings and bound requests/render output; no remote content.

Required tests: existing proposal API parity; source-section identity in a single
call; partial-result suppression; unsupported model shape/kinds; transform order,
mirroring and invalid matrices; adapter count-before-copy; bounded parse/HTML
escaping including script-closing input; one-job/cancel/timeout/window-generation;
architecture boundaries; separate wheel metadata/capabilities and research ZIP
non-runnable allowlist. Runtime smoke must record exact Orca/Python/NumPy version
and actual small-model Generate/display/Cancel behavior. No physical test is needed.

Adapter implementation must follow the demonstrated bindings. No
unreviewed alternative API or model-frame assumption may fill a missing binding.
