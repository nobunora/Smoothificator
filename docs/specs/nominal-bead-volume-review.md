# Exact nominal bead-pair volume audit

Repository disposition: validated for a tools-only pure audit using the existing
exact nominal support kernel (SPEC 12 / ADR0048), not a physical tool-clearance
certificate. The actual outward candidate exposed a concrete downstream-material
overlap which tip-Z ordering alone misses. Research and implementation are separate.

Implement tools/audit_nominal_bead_overlap.py and focused tests. Inputs are two
immutable ExactNominalTopSegments plus explicit bounded refinement/cancellation
policy. Do not parse or mutate G-code, choose future chronology, or alter bead
geometry. Caller owns association and execution order. Output is immutable,
retains pair IDs/policy/exact witnesses and permanently false physical authority.

First use conservative XYZ envelopes for broad-phase exclusion. For remaining
positive-area XY boxes, query each individual bead's exact top bounds with the
existing query_exact_nominal_top_cell. Obtain bottom bounds by querying its
vertical reflection: reflected command Z = height - original command Z, same
XY/width/height. The reflected top equals negative original bottom. This reuses
the existing stadium/flat-cap owner and is valid for linear varying-Z structural
segments too. No new cap/joint or float-distance model is permitted.

A cell is volumetrically disjoint if either XY support is absent, or either
bead's top upper bound is <= the other's bottom lower bound. A positive-volume
intersection is proven only on a positive-area cell fully covered by both beads
where max(bottom upper bounds) < min(top lower bounds). Otherwise subdivide the
XY box along its longer axis. Preserve coverage, exact boundaries, all unresolved
work and explicit query/depth/input-bit limits. Resource exhaustion or cancellation
must never pass. Zero-area/zero-height boundary touching is not positive volume;
distinguish this from physical clearance or allowed contact policy.

Reports distinguish disjoint-interiors / overlap-proven / incomplete and retain
mixed unresolved work. Reject malformed types/policies, validate exact boolean
cancellation and latch cancellation. Do not declare a full job safe from one pair.

Tests use the real kernel for identical/partial overlap, separated XY/Z, touching,
oblique/reversed segments, flat caps and varying-Z reflection; cancellation and
resource outcomes; exact witness positivity. Include the prior actual outward
ring25 / future4.4 overlap regression with pinned source provenance. Independent
review plus parent audit precede use to accept planner alternatives.
