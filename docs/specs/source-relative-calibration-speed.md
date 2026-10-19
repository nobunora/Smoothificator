# Source-relative calibration drawing speed

Status: SPEC_VALIDATED; independent source/repository review confirmed the bounded amendment on2026-10-19.
Date:2026-10-19. User authority: drawing speed must use Orca slice settings as
its baseline and vary only downward. Parent contract: ADR0073 and
prepared-calibration-matrix-library.md; base revision f620b1ef5df2bf4a7ea883bd359a63936d7c465a,
current uncommitted calibration-library source is retained, no reset or merge.

Only the volume_speed trial changes. Preserve ready-v5, wheel0.3.0, historical
V1 raw, other3 raw outputs, geometry, flow, clearance, end/start treatment,
source restoration, original G-code and all ordinary printing gates.

Use a separately identified native policy schema3 for volume_speed. Retain schema2
absolute-speed behavior for historical replay. New column axis `print_speed_ratio`
is exactly .2/.4/.6/.8/1; rows remain the existing5 final volume/length values.
Resolve reference speed from the actual immutable source/profile:
min(saved outer_wall_speed, minimum positive-deposition Outer wall command feed
at original base top Z=.8, conservative saved machine X speed cap, conservative
saved machine Y speed cap). Missing/nonpositive/ineligible evidence rejects.
Current source: outer wall200mm/s,4 actual base-top outer-wall commands all200,
conservative X/Y caps200, hence reference200 and columns40/80/120/160/200mm/s.
Use exact fractions and floor F on the existing .001mm/min lattice; never round
up or silently clip a requested column. Validate each emitted XY and volume rate
against source caps. Recompute reference inside native rebuilding, not from an
untrusted caller. Bind settings, source event IDs/feeds, machine caps, source/profile
identities and resolved reference into the frozen recipe identity.

Keep actual per-cell print_speed_mm_s/feed/E in CSV/frozen manifest. Add ratio,
reference speed, requested speed and source-reference evidence with clear units.
A10mm line may not reach its commanded feed due to acceleration: show commanded
speed, not a claim about measured average/peak speed.

Add closed ready-bundle V2, preserving V1 decoding/validation and request semantics.
Only V2 volume_speed carries a `source_speed_reference` descriptor and ratio axis;
its fixed baseline20mm/s is not the reference speed and must be clearly distinguished.
Portable validator crosschecks ratio/reference/requested/resolved-speed/F and
CSV/frozen/reference identity. No tools/G-code parser imports enter UI.
UI displays percentages, actual mm/s and the source reference separately.
Proposal axis is ratio with quantum.001 and approved bounds.2..1, logarithmic
volume behavior unchanged; preserve endpoint/resolution-limit request statuses.
Old V1 proposals remain absolute-speed requests. Source-profile guard still
covers actual saved motion limits; the selected frozen source never masquerades
as live-preset regeneration. Version0.3.1 wheel includes the new audited bundle.

Ownership: emitter=domain/native policy/reference derivation/CLI/newreadyassets/tests;
UI owner=bundle/backward validation/presentation/proposal/storage/wheel/tests;
parent=spec/ADR/canonical summaries/integrated audit/final full suite;
researcher=read-only review and independent numeric/export audit. No overlapping
edits. Review specification before implementation, then focused/architecture,
new raw25cell/source/state/nominal audit, wheel readback, fresh full regression.
No printing, automatic app-opening, publication or merge in this task.
