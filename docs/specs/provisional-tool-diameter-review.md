# Configurable provisional tool diameter

User instruction 2026-10-18: proceed provisionally with 0.4 mm and make it
changeable later. In the context of missing head dimensions, use this as an
explicit **assumed diameter**, not radius or measured whole-head geometry.

Repository disposition: validated for tools-only offline review. Canonical
SPECIFICATION sections 27/29/30 and the existing ToolClearanceProfile contract
remain unchanged. No physical profile, evidence reference, axial height,
uncertainty margin or executable authority may be invented from this value.

Implement an immutable tools-owned provisional planar-tip model with positive
exact rational diameter (default 0.4 mm), derived radius, explicit model/version
and deterministic identity. Keep saved nozzle diameter from the sliced profile
separate in the receipt, including mismatch diagnostics. Changing this assumption
must not rewrite saved machine settings, line widths, extrusion or Z-hop values.

Wire the parameter into tools/review_supplemental_hops.py via a keyword option and
CLI `--assumed-tool-diameter-mm`. Report the assumption and its identity. For
each actual quantized raise / XY / descent bridge, use the radius to compute a
conservative swept planar-disc bounding box. XYZ bounds follow the command
endpoints; no axial head extension is assumed. These are broad-phase geometry
diagnostics, not obstacle queries or collision/contact certificates.
Also report one disk-expanded envelope of every complete quantized supplemental
polyline, retaining all path IDs, so the assumption is visible for paths as well
as their bridges. Such envelopes do not prove internal ring clearance.

Retain original commands and source/project/manifest hashes; add a deterministic
review identity incorporating geometry. All physical, complete-head and clearance
verification flags remain false. No production/domain/profile format changes.
Reject invalid/nonfinite/zero/negative diameter; document the CLI and limits.

Verify 0.4 and another diameter produce the expected radius/bounds and distinct
review identities, equivalent rationals the same identity; command bytes/hops,
inputs and source identities remain unchanged. Cover pure Z, oblique XY,
negative coordinates, quantized endpoint consistency and exact touching bounds.
Use real pinned model data for 0.4/0.6 JSON review evidence. Focused tests,
parent audit, independent review, then full repository verification.
