# Exact span queries for continuous path contact

Repository disposition: validated additive research API within the existing
engine/domain ownership. SPEC 12 / ADR0044/0048 geometry and all physical gates
are unchanged. Current axis-box path audit is sound but a real source-offset
64-edge path needs 24,860 queries because diagonal boxes include off-path area.

Expose `query_exact_nominal_top_span` in engine/support_cell.py, validating two
distinct immutable exact XY endpoints. Reuse `_exact_top_query` with those two
corners; no replacement geometry or finite point-sampling acceptance. Existing
core bounds apply to the ENTIRE straight span: projection and signed lateral
coordinate are affine over its parameter interval, so their extrema are at its
ends; interval squared-distance/cap and varying command-Z bounds remain valid.
Add a clearly named full-bound reason to ExactNominalTopBounds if necessary.
Existing point/cell functions and their behavior must remain unchanged.

Extend the tools continuous-path auditor with an explicit optional query geometry
mode (old padded-axis-box remains default). In exact-span mode, query every full
parameter piece with the public span owner, bisect on uncertainty, and preserve
all chronology, partition, cancellation/resource and false-authority behavior.
Report actual queried span endpoints; do not label line bounds as cell bounds or
retain a fictitious queried padded box. Policy/receipt must identify the mode.

Tests: a whole covered oblique span; endpoint support from different disjoint
sources cannot pass a span containing a gap; partial coverage/incomplete; varying
Z and rounded lateral profile; degenerate/nonexact endpoints, duplicate sources,
resource/cancellation; new tool mode exact partition and future exclusion.
Existing default-mode tests must pass unchanged. Compare real source-offset
candidate whole-path results against previous axis-box proof, with current pins;
query-count improvement may be reported, never confused with physical clearance.

No source parser, candidate optimizer, overlap auditor, printer or G-code output
changes in this stage. Parent and independent review precede acceptance use.
