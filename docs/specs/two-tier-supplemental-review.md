# Opt-in two-tier supplemental rectangles and causal execution

Parent disposition: validated for tools-only implementation after separate
repository review on2026-10-18; no material canonical conflict found.
User explicitly approved the
illustrated wide-lower/narrow-upper construction on2026-10-18. This changes the
previous direct-original-floor interpretation for this new opt-in route only.
Existing nonstack plans, identities, annotations, copies and defaults stay exact.

Canonical revision: docs/SPECIFICATION.md SHA256
e6f049ecf1ea24a6372cd486a3245178ccee5ee3aecf1614d12694d586005dd9.
SPEC14 already permits earlier lower-Z candidate support and requires acyclic
dependencies. Accepted ADR0043/0044/0048/0058 and SPEC27-29 remain in force.
Tools-only offline research, not a production capability or physical gate change.
Do not create a new Accepted ADR merely for a tools DTO; adjudicate an actual
normative conflict before implementation if repository review discovers one.

## Meaning and immutable ownership

Keep original_source_floor_z_mm and original_next_layer_z_mm separate from every
path's support_plane_z_mm. Tier1 support plane equals the original floor. Tier2
has explicitly identified, earlier, immutable tier1 parent material at a common
constant top plane; no future, missing, foreign-source/profile/step, cyclic,
same-Z-as-required-support or third-tier dependency. Initial geometry family may
restrict to one parent per upper path and straight parallel centerlines; reject
other families explicitly instead of inventing parent geometry at that height.

For each physical bead: top=support_plane+remaining_height;
bottom=top-physical_height; overlap=1-remaining_height/physical_height.
At0% the upper bottom equals its parent's top. At positive overlap the upper
penetrates its immediate parent, not an unspecified original-layer reference.
Bounds remain plugin configuration: width0.25..0.45mm, minimum remaining height
0.08mm, overlap0..30%, physical height at most90% of the saved source layer
(0.18mm for0.20mm). Increase the analyzed physical minimum by dividing required
remaining height by(1-overlap); never bury the minimum. Every upper top is
STRICTLY below the next original layer. Frozen XYZ/E-implied widths must pass
these same bounds; no tolerance or rounding waiver.

Expose a new immutable versioned supported intent/graph/frozen identity rather
than silently changing the old SupplementalPath.floor semantics. An explicit
internal local-support numeric adapter may reuse the existing freeze owner;
its public result must retain original-floor and support-plane identities and
cannot be passed off as original structural-source association. Reuse numeric
and formatting owners; avoid copied formatter/flow implementations or a second
extrusion conversion. G-code composition executes validated immutable paths;
it does not optimize geometry.

## Bounded section search

Add an opt-in exact 2D two-tier candidate family to the triangle packing tools.
One block has a tier1 rectangle and optionally one tier2 rectangle whose X
interval is contained in its parent; blocks have disjoint X interiors. Original
triangle coordinates are preserved. Enumerate an explicit bounded X lattice and
physical-height lattice (caller configuration, not a hidden claim of continuous
optimality), widths/heights/overlap limits and the existing strict short-base
rule base^2<2*minimum_width^2. Zero-degree flat areas need no slope filling;
30degrees with rise0.2/minwidth0.25 is explicitly excluded by this rule.
Each search receives ONE exact configured overlap percent in[0,30], applied to
both tiers; it does not optimize an unspecified continuous overlap variable.
Another overlap value requires a separately configured search. Enumerate only
height combinations meeting compensated minimum/total-height constraints before
the X-interval loops; explicit initial grid48 and physical-height step0.02 are
an acceptable bounded illustration family, not universal hard-coded policy.

Use exact finite_triangle_rectangle_intersection_area for each posed rectangle
and parent/child intersection. Each rectangle must have outside area<=half its
own physical area. Rank by exact triangle/rectangle-union symmetric difference,
counting the shared parent/child volume only once; never sum overlapping areas
as if disjoint. Compare the best stacked family against the existing floor-only
packing at the same declared X lattice; never force stacking when its error is
worse. The existing continuous-median-height floor solver is a separate stronger
comparator, not falsely part of the enumerated height family. At nonzero overlap,
pose and re-evaluate any floor comparator's actual rectangles/finite spill; never
reuse its zero-overlap error or feasibility. State precisely which finite family
was exhaustively evaluated. Explicit
event/candidate/bit/query/cancellation budgets must fail closed or report a
noncomplete search; a partial search cannot claim lattice optimality.

The user's section surrogate is explicitly one source-layer rise and the gap
between consecutive sliced contours. Its original finite triangle must retain
that supplied coordinate frame. It is NOT automatically the original CAD
triangle: midpoint slicing and nozzle-center offsets require a separate mesh
comparison. Report both when available; a low surrogate spill/error is never
an original-mesh tolerance certificate. The actual20 fixture shows this
distinction, and failed CAD diagnostics remain explicit. This tools-only
surrogate experiment cannot pass the canonical mesh-error/physical gates on
surrogate evidence. Any additional finite placement offsets or emission
adjustments must be declared, freshly scored after formatting and compared
against the stronger posed floor comparator; do not label them the original
lattice optimum.

## Causal association, execution and certificates

Root source/feed/profile/anchor association comes from the ACTUAL original floor.
Tier2 support association separately binds freshly frozen parent identities and
source context, not fictitious structural source IDs at the raised plane.
Validate the dependency graph before ordering. Choose the lowest world top Z
among ready nodes, then physical height and canonical path ID. Every dependency
strictly increases top Z. Physical-thickness sorting must never place an upper
before its parent. Require deterministic ordering and exact immutable identity.

Use the saved-profile hop via the existing safe-ceiling owner, computed from the
saved actual Z and ORIGINAL next-layer Z, with upward grid rounding. Every path
has retracted raise->XY->descend and safe exit/return; do not slide at a low Z
through other material. Restore source XYZ/feed/logical E/debt/modal state and
preview metadata exactly. Preserve the entire source prefix/suffix and all
noninsertion bytes. New optional copy/writer must rebuild stale/forged inputs,
refuse overwrite/alias, atomically publish UNVERIFIED_VIEW_ONLY and never print.

Freshly certify upper centerline contact against ONLY completed declared parent
beads using the existing exact nominal span owner. Remaining/full-footprint
support metrics stay distinct; no centerline-to-physical promotion. Every parent
pair's intended physical overlap is limited to its declared immediate-support
slab[child_bottom,parent_top], depth<=30% of child's physical height. Verify actual
constant parent top, child bottom/top and spatial relation. All other positive
material intersections remain failures/unknowns. Never blanket-exempt all
candidate pairs or every support pair; store exact parent/child provenance.
Use the original finite triangle for spill, not a translated triangle starting
at the support plane. Re-query actual emitted geometry after XYZ/E formatting.

The causal tool audit must include lower material while printing, descending to,
and leaving the upper, and all later original body moves. Reuse existing exact
tip/sweep/contact owners and explicit allowed regions. Keep opaque prefix/tail,
full-head and physical assumptions unverified; this permission does not resolve
the previous whole-job execution blocker. No new M204/jerk/PA override.

## Concrete review artifact and checks

Produce a NEW genuine Orca20degree source using pinned existing saved
settings/producer. A flat-bottom rectangle with a flat top portion and a20degree
sloped top portion is the approved concrete fixture if the wholly tilted cuboid
cannot enter the unchanged complete nominal model. Preserve failed experimental
sources and record why they failed; do not widen geometry/parser contracts to
accept unsupported features. Do not overwrite the original/current28-path artifacts,
sanitize away manufacturer routines or reinterpret the previous10degree adapter
as20degrees. A genuine automatic Brim before the first M624 may remain in an
explicitly NEW opaque prefix. If the first scoped layer inherits section metadata
from that prefix, the body may instead start after its complete M625, at the next
explicit LAYER_HEIGHT before fresh scoped LINE_WIDTH/deposition. In the actual20
fixture this is line4486; the first Support layer then also remains opaque.
Use freshly declared/reconstructed entry assumptions and pins. This is not
support for parsing or accepting prefix material: the pre-existing-prefix material
obligation remains unresolved. Never erase Brim, claim the old prefix identity,
or hide a positive material event inside an audited body. Preserve all bytes.
Generate a new opt-in two-tier view-only copy and evidence showing
parent/lower-first order, remaining/physical heights and overlap bounds, upper
top margin, all intended/unrelated material pairs, source restoration and actual
native Orca height preview. At least one actually stacked path must be present;
report if no feasible emitted choice exists rather than fabricating success.
The0..30angle section fixture covers flat/eligible/short-base cases separately.

The flat-ramp fixture has one unsupported terminal Gap infill with width below
height. For this view-only experiment, a newly pinned body may end at a complete
M625 before that layer. All remaining positive model moves and OEM shutdown then
form an explicitly opaque suffix; retain their raw count, locations and failure
reason. Do not call the bounded body the entire moving model or certify later
material outside it. Preserve every suffix byte and leave all future-material,
whole-job and print authorities unresolved there. No model/parser relaxation or
additional slice/profile workaround is authorized by this boundary.

Required focused boundaries:0%/30%/over30; compensated minimum0.08 and below;
width min/max and E-implied overflow; total top==next-layer rejection; missing,
cyclic/depth3/future/foreign/noncoplanar parents; thinner upper still later;
unsupported child span; forged/stale frozen parent/context; union-area overlap
double-counting; search limits/cancellation; exact source/metadata restoration;
intended-overlap slab vs unrelated intersection; low-Z travel into existing
parent; exact legacy default tuple/copy identity. Independent review must test
the new path, not merely assert default regression. Run related architecture and
full tests after final coupled changes. All physical/runtime/print flags remain
false, no printer operation, no merge/release, log_iotc.txt untouched.
