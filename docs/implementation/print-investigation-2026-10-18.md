# Offline print investigation, 2026-10-18

Disposition: validated for an offline chronology/anchor audit; not a production
injector or physical-print authorization. Quality-error improvement is explicitly
deferred by the user and is not a blocker for this bounded work.

## Current exact source evidence

`artifacts/revolved-exponential-review/original-slice/plate_1.gcode` has SHA256
`8d7b530bc351826f496182c6c080c5f8f379e0eb22f01e7ccea4a26966811b95`,
525524 bytes, 20783 LF lines, no CRLF, and 31 changing-layer markers. This was
recomputed read-only. No source/project modification or printer operation occurred.

The strict reader in `orca_plugin/gcode/linear_trace.py` rejects the first
executable command, M73 at source line760. Its modal state does not include
acceleration, cornering, tool or object-wrapper state. Extending the grammar
without these semantics cannot produce a complete execution certificate.

The complete raw opcode inventory is G1 18108, M204 853, M73 105, M624/M625 31
each, M106 10, G90/M83 two each, M981 two, and M190/M104/G92/M109/G21 one each.
M624 has a base64 argument, outside the current numeric-word grammar. Preserve
its raw bytes and classify it explicitly; never pass it through a generic no-op
allowlist. Source-side Orca preview parsing is not firmware execution evidence.

Saved config is useful but does not prove runtime identity: line275 declares
`gcode_flavor = marlin`; line400 startup is only G90/M83/G92 E0. The generated
source contains no explicit M200 D0, M220 S100, M221 S100 or homing command.
The original saved Bambu A1 mini preset also declares marlin: this is NOT a
contradiction. Machine name/flavor alone nevertheless does not establish golden
firmware execution evidence or startup readiness. The current strict reader also
requires known linear-E units for G92, which occurs before G21 here. An offline
audit may retain that uncertainty; it must not silently seed physical defaults.

## Concrete first useful boundary

For the [3.0,3.2] interval, insert-point routing evidence is the changing-layer
marker line8087, immediately after M625 line8086, not wall-sample lines7288/8216
used by the geometry study. The byte offset immediately after marker8087 is
211527. Line8080 retracts .75085 and line8083 wipes with E-.04915, totalling
.8. The final emitted XYZ before the marker is (95.316,85.606,3.0), not nominal
3.2. F is 11693.563. A prior unknown physical debt remains unknown unless an
explicit justified initial-state/firmware contract resolves it.

Inherited M204 is S6000 from line8065. Config line441 says outer-wall
acceleration5000, while the next outer-wall block sets S5000 at line8201.
SPECIFICATION section28A prohibits changing acceleration and requires inherited
acceleration within the resolved wall cap. Thus this particular boundary cannot
be physically accepted under that gate merely by extending the parser.
Subsequent original motion begins sloped lifting at line8093 Z3.217. Returning
from supplemental tops to saved Z3.0 is a real downward motion requiring clearance.

## Smallest next implementation contract

Implement a read-only, byte-indexed offline chronology audit in tools, preserving
the strict reader fail-closed contract. Associate every result with exact source
and sliced-project hashes; inventory raw commands with line/offset spans; pair
CHANGE_LAYER/Z_HEIGHT/LAYER_HEIGHT/changing-layer markers; report actual modal
state and explicit unresolved fields at every boundary. Distinguish a routed
marker, a completely parsed anchor and a physically eligible anchor. Reject
ambiguous/duplicate marker structures and source/project mismatches. Tests must
cover wipe-split retraction, deferred lift, reset-E debt, M624 payload preservation,
unknown commands, acceleration mismatches and exact source slicing reconstruction.
No byte output should be labelled printable and no real source block should be
composed from guessed anchor state. This is missing-code work achievable offline.

After that: a separate pure byte-splice experiment can prove unchanged original
ranges/order and local newline preservation in a separately named preview copy.
It must not edit/replace canonical source or claim the ADR0061 production commit
lock/AtomicWriter workflow. Production mutation requires SPECIFICATION section32,
ADR0031 and ADR0061, immutable validated Plans and all final validation evidence.

## Formatter and physical evidence boundaries

ADR0017 pins XYZ/F3, E5 and C++ std::round at Orca commit
789f848694b955d293ca6b277d1c8046aa6f7436. It is useful established contract,
not verified equivalence for this runtime. The current explicit research policy
is valid for offline blocks only. Runtime-associated formatter source/parity and
final quantized revalidation remain required for physical promotion.

Saved source nozzle_height4.76 (line427), clearance radius73 (line144), rod
clearance56.5 (line141), lid180 (line142), and rod25 (line143) are real saved
inputs. `nozzle_type = undefine` at line433. These object-arrangement dimensions
and nozzle-orifice diameter do not define the non-deposition tool keep-out shape
and intended tip-contact zone required by ADR0033. No measured shape is invented.

A conditional sufficient downstream barrier is mathematically available: if all
relevant tool geometry lies at or above the tip, every future tip position stays
strictly above the maximum newly deposited material height with a conservative
margin, and no future downward/unknown motion occurs, injected material cannot
intersect that tool. Actual whole-body geometry and margins require documented
physical evidence. This barrier does not certify candidate descent/extrusion,
return to saved lower Z, same-batch interaction or support; every such motion
needs chronological local checking. Candidate top ordering alone is insufficient.

Support implementation can reuse the ADR0044 nominal cell provider and ADR0058
conservative refinement only with actual chronological deposition and explicit
thresholds. The final mesh cannot supply support from future material. Local
contact queries and dense samples do not establish converged whole-footprint
coverage/minimum contiguous width. Missing controller integration is offline
code work; unvalidated physical thresholds/tool geometry are external evidence.

## Verification performed

Read-only repository status, targeted source/config/ADR reads, opcode inventory,
exact marker/byte/hash/newline checks. No tests were run by this investigation;
769 passing tests are a prior implementation result, not fresh proof here.
No production/test code changes, printer connection, physical print, commit,
push, merge or release. Unrelated log_iotc.txt remains untouched.

## Follow-up: full saved startup is recoverable

The pinned `artifacts/fixtures/offline-coupon.3mf` actually retains full original
machine_start_gcode, machine_end_gcode, filament_start/end_gcode and
layer_change_gcode. Printer/process/filament ids are Bambu Lab A1 mini 0.4 nozzle,
0.20mm Standard @BBL A1M, Bambu PLA Basic @BBL A1M. That seed also says marlin;
it is not a Bambu mismatch. `tools/exponential_top_fixture.py:73-76` deliberately
blanks every *_gcode and substitutes the short research startup. Therefore a NEW
separate project can restore exact seed custom-code settings and be resliced
without touching any current original bytes. Full startup begins with thermal
setup/M1002 commands; full ending contains G392/M400. The expanded source then
needs its own reviewed command/state contract, not an opaque startup bypass.

## Follow-up: actual quantization blocker

Read-only exact-rational audit of all30 manifest rings at3decimal XYZ:
7 round up (rings4,6,18,19,23,29,30),12 down and11 exactly representable.
Maximum upward change is1/2072 mm. At requested zero overlap, the7 upward cases
necessarily fail current compose_retracted_cycle remaining<=physical_height
condition. This is correct fail-closed validation of immutable input, not a
reason to relax overlap or minimum-height bounds.

A bounded planner-owned executable-intent stage can quantize nozzle top first,
derive explicit physical height=quantized_top-floor for the requested zero-overlap
policy, validate unchanged min/max height and width constraints, recompute nominal
q_cmd, and publish immutable grid-aligned intent. The adapter must only quantize,
derive E and accept/reject; never silently optimize h/width. The alternative is
retain existing exact intent and correctly reject7. Both need explicit scope;
physical promotion additionally checks actual E-quantized flow/derived geometry.

## Follow-up: existing full support controller

`adaptive_subedge/engine/support_coverage.py:evaluate_support_coverage` already
implements a conservative adaptive controller over straight-chord footprints,
including supported-area fraction, minimum contiguous support width, effective
height, convergence, cancellation/resource disposition. `engine/support_width.py`
owns exact contiguous-width aggregation. Thus a new controller is unnecessary.

A complete circumferential offline audit can invoke it for every emitted chord,
with earlier structural/candidate NominalSupportSegments only and per-chord
execution order, then require all chord results numerically-supported. Source
width/height role changes and sloped Z must be preserved. Never declare a ring
supported from one radial section. Explicit CandidateBeadBounds,
SupportCoverageThresholds, SupportRefinementPolicy, SupportQueryNumericPolicy,
SupportCellQueryPolicy and max_cells are mandatory. DTOs deliberately supply no
validated physical defaults: selected analysis thresholds can be reported as
research assumptions; physical acceptance requires validated fixture thresholds.
Potentially unresolved seam coverage and cell budgets should remain visible.

## Follow-up 2: executable grid-intent task contract

Calculations now use `.venv\Scripts\python.exe` (requested Python3.12.10).
`artifacts/print-source-inspection/grid-intent-research.json` checks nearest,
floor and ceil XYZ3 top policies for every30 ring using exact rational arithmetic.
All90 nominal choices pass unchanged h=.08.. .18, w=.25.. .45, h<=w,
zero overlap with h=grid_top-floor, next-layer ceiling and <=50% radial rectangle
spill; maximum spill is36.4140926641%. Radius and192-chord topology stay fixed.
This is machine-format intent preparation, not deferred quality optimization.

However canonical nearest E5 after recomputed q_cmd produces64 too-narrow
chords in rings2/3 (minimum derived nominal width.2476877996412805). No E is
zero. All5760 chords were checked after XY3 quantization and removal of saved
command flow multipliers. Width perturbation range is about-.006681..+.006485mm.
See e5-width-research.json. Therefore unchanged-width intents cannot claim
all30 complete legality from XYZ alone.

A feasible research-only width adaptation was also calculated: increase intended
ring2 width by.003mm to.25520752895752896 and ring3 by.002mm to.25420752895752896,
then recompute flow before immutable publication. Both retain192 paths/chords,
canonical nearest E5 and original radii. Derived per-chord widths are respectively
.2503152455.. .2592656395 and.2508070857.. .2571745319. Other28 ring widths need
no adjustment. Worst derived width radial-spill checks give10.6683% and2.71834%,
well below50%. See e5-width-planner-study.json. This does not yet prove actual
XY-quantized circumferential support/body clearance or final-surface error.

Smallest implementation contract: a pure planner-owned research preparation
stage receives exact original ring intents, pinned formatter descriptor and saved
flow context; prepares nearest-grid top/h, considers a declared bounded width
candidate set for E5 robustness, and freezes only fully revalidated intent. It
must preserve IDs/radii/chord topology/original-layer association, report every
height/width/q_cmd delta and numerical rejected alternative, and retain all hard
bounds/spill/overlap rules. The emitter remains accept/reject only. Fixed input
assumptions and deterministic candidate grammar belong in the planning report;
never hide an epsilon or special-case ring IDs. This is a new explicit scope,
not an implied permission to alter the production optimizer.

## Follow-up 2: restoration receipts and exact transformation

profile-restoration-research.json pins seed6b17c12a81ea54a0bfb8545713c2119e7d6604b6ee9abfbbdc23b73e883eebc4,
current unsliced revolution projectb22af0e25a9e29a95e7a3c0f6aa93cf058d5119fa456205c05d62d3c1f89295f,
and runtime EXE480b64a3a5e95e3b43ed5ff93f7490af4e57f4e3cf6f19d8c9a4e4b2c9906aba.
Windows ProductVersion/FileVersion are blank. A read-only --help invocation
returned no captured text; it is not a verified runtime version receipt.

There are17 saved keys ending _gcode,9 changed by sanitization. IMPORTANT:
`emit_machine_limits_to_gcode` is one of them but is a numeric configuration key,
not a custom-G-code string. Restoration must copy its exact saved type/value too.
Changed keys: change_filament_gcode, emit_machine_limits_to_gcode,
filament_end_gcode, filament_start_gcode, layer_change_gcode, machine_end_gcode,
machine_pause_gcode, machine_start_gcode, time_lapse_gcode. (Receipt is the
source of truth for the exact count/keys; blank/list values must retain type.)
Unchanged keys remain byte-semantically identical as parsed JSON values.

Create a new separately named full-profile project by copying current model/
placement archive entries and replacing only those saved settings from seed.
Do not call existing prepare() on the canonical folder or overwrite any current
slice/receipt. Pin before/after hashes for seed/current project/source/3MF and
model bytes. Invoke the existing pinned EXE with --slice0 --orient0 --arrange0
--export-3mf sliced.3mf, isolated --datadir and --outputdir, argv array/cwd,
stdout/stderr/exit/duration receipts and output hashes. Do not connect/send/print.

Full layer-change template adds M73L/M991S/P before the changing-layer marker;
startup/end expands conditional/opaque firmware commands, E/G92/G90/M83 and
motion. Inventory generated source before defining any allowlist. Re-run exact
anchor/modal/debt/acceleration audit; restored machine limits may alter parser
requirements. Saved templates can be restored automatically but neither their
existence nor CLI slicing proves hardware safety or grants unknown commands
no-op semantics. Current source and previews remain unchanged for comparison.

## Follow-up 3: preserve radial packing; supersede width adaptation

Parent review correctly identified that widening packed rectangles could violate
neighbor nonoverlap. The widening experiment is SUPERSEDED; do not implement it.
A better format-robust planner alternative preserves every ring radius and
nominal width and reduces polygon segmentation only where needed.

`chord-count-research.json` scans32..192 chord counts for rings2/3.96 is legal for
both, with no emitter E rounding change. Their192-point original polygon already
contains every required96-point endpoint, so select every other existing point;
do not introduce a new trig/rounding source. All other28 rings keep192 chords.
Nearest XYZ3 tops/h as previously described, then recomputed nominal q_cmd and
canonical E5, produce5568 total chords over30 paths. In the exact existing
9decimal-endpoint check, there are zero E<=0 and zero derived-width .25.. .45
violations; all chord counts remain closed with unchanged path association.

At96chords ring2 nominal ideal sag=.000495351419mm, actual XY3-polyline max
radial deviation=.000851370358mm; ring3 ideal sag=.000630386488mm, actual
max=.000781483269mm. The actual metric includes endpoint radial deviations and
interior closest-point deviation, not merely endpoint samples. Across ALL30
rings actual maximum radial deviation=.001758775367mm, below existing.002mm
budget. XY rounding theoretical Euclidean bound is sqrt(2)*.0005mm; report this
separately from ideal sag rather than assume the bound is attained.
See `chord96-final-research.json` for all30 actual deviations. Radial packing
and nominal rectangle spill are unchanged except the already checked grid h.
Actual bead footprints/chronological support still need full adapter validation.

Recommended bounded intent task: explicitly plan nearest-grid h and a declared
format-aware segmentation family (e.g original192 and coarser divisor96), test
all emitted chord lengths/E/derived width/radial deviation and hard remaining/
overlap/height/spill limits, then freeze the chosen candidate. Keep radius,
nominal width and30 path count unchanged. No ring-ID special case in generic
logic, no hidden tolerance, no endpoint alteration after immutable publication,
no geometry choice inside the emitter. The research fixture proves a candidate
exists; it does not substitute for canonical physical motion regularity,
minimum segment time, acceleration, support or tool-envelope gates.

## Phase3: bounded support integration and actual gap witnesses

Reuse engine/support_coverage.evaluate_support_coverage, engine/support_cell
and engine/support_width. tools/audit_top_contact_cells.lower_sources is NOT a
chronological adapter: it filters by final Z and its ;HEIGHT parser misses current
;LAYER_HEIGHT. Production motion truth must come from full interpreted chronology;
no duplicate parser that guesses unknown firmware defaults.

Next standalone analysis adapter should accept frozen grid intent plus explicit
chronological source DTOs with actual start/end XYZ, width, local height, role,
source lines/orders and context eligibility. Resolve actual source widths/height
comments and validate against emitted flow; do not sort original execution by Z.
For each of5568 emitted chords call existing adaptive controller with only earlier
material. Same/higher-Z candidate support is already rejected by provider.

A maximally conservative ANALYSIS policy can request supported area fraction1,
minimum contiguous width equal to that chord's executed footprint width,
CandidateBeadBounds .08/.18/.25/.45, initial cell.05mm, refinement2,
convergence area/width0, minimum cell.0001mm, maximum10levels, numeric tolerance
.0001mm, sqrt128fraction bits, max_sources20000 and max_cells100000. These are
explicit research policy choices, not measured calibration or physical defaults.
If budget/convergence/seam union coverage remains unresolved, report incomplete.
The controller cannot assert success while unresolved cells exist; full area1
is intentionally stringent. Existing single-segment coverage proof is sufficient
but not necessary: unions of partial segments may stay unresolved despite
physical coverage. Preserve that limitation rather than invent a second engine.

Read-only `support-cardinal-research.json` contains120 exact nominal top point
bounds (four cardinal probes for each ring), from all original structural
segments at or below each nominal floor. This overinclusive source set is NOT
chronological acceptance; an absence/low-upper-bound witness against it remains
conservative for original material. Layer height.2 is explicit fixture input.
There are40 probes across10 rings where structural top is strictly below floor.
This refutes blanket zero-overlap bottom-plane contact, not whole-footprint
support by itself. Sample success is never accepted as complete support.

Concrete ring25 (floor4.2, radius8.06897954545) gap lower bound is.0757712691254mm.
With max physical height.18 and max30percent overlap, maximum bottom lowering
is.054mm, insufficient to close this witness even at max thickness. All earlier
candidate radial extents are<=7.94295909091, leaving>.126mm to this centerline;
they cannot rescue it (XY3 deviation is far smaller). At current h=.15409 the
nozzle-to-structural-top effective height at this witness exceeds.2298mm,
violating max.18. Ring14 current h=.08 has gap.0442668663; any lowering at fixed
h breaks minimum remaining.08. Other probes do not establish feasibility.

Therefore overlap0..30 alone cannot guarantee keeping every current ring at
its original floor/radius with current height constraints. A correct next task
should produce explicit reject/witness evidence and evaluate permitted candidate
alternatives in the planner; never blanket-lower everything or relax minimum
remaining. Changing floor association/support-height semantics or retaining
unsupported paths would require explicit specification adjudication.

## Phase3: available hardware evidence and smallest external gap

The seed3MF archive contains user coupon model/config/screenshots, not hardware
CAD. Its saved values include nozzle_height4.76, nozzle_typeundefine and object
arrangement clearances, but no hotend_model/tool envelope or safety margins.

A real local nominal visualization mesh exists:
resources/profiles/BBL/bbl-3dp-hotend.stl within pinned runtime;
SHA25640e3f659c0e5f760ec191d6ecde1f364b8ec0025188340aa2fa0a40f142d331c,
624triangles, X[-1.700000048,1.799999952],Y[-1.75,1.75],Z[approximately0,12].
It is a generic BBL asset, not evidence for the complete A1 mini nozzle/heater/
sock/fan body or calibrated tip coordinates. A1M.stl is identified as bed_model
in both official Orca and BambuStudio A1 mini machine-model JSON. Those primary
JSON sources do not declare this generic hotend asset as A1 mini hardware CAD:
https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/main/resources/profiles/BBL/machine/Bambu%20Lab%20A1%20mini.json
https://raw.githubusercontent.com/bambulab/BambuStudio/master/resources/profiles/BBL/machine/Bambu%20Lab%20A1%20mini.json
These were checked live2026-10-18; main/master are moving references, not pins.

Bounded official manufacturer searches and A1 hotend product/maintenance access
attempts did not supply a dimensioned tool-tip-referenced keep-out envelope.
This is a search limitation, not a claim that no drawing exists anywhere.
Do not estimate dimensions from product photographs or use third-party generic
CAD as measured fixture evidence.

The smallest genuinely missing physical clearance input is an evidence-backed
conservative radial keep-out-versus-height curve from the actual nozzle tip,
including the non-deposition tip contact distinction, relevant axial extent and
radial/vertical uncertainty margins, tied to the exact A1 mini hotend assembly.
ToolClearanceProfile already models that curve/margins/evidence reference; no
new DTO is needed. An exact official dimensioned/CAD source could establish
nominal geometry; hardware variant/assembly/uncertainty validation still requires
fixture evidence. No printer calibration or generic object radius substitutes.
This evidence gap does not block implementing adapters, reject/witness reports,
synthetic swept-volume tests or analysis using explicitly unverified nominal CAD;
it blocks physical approval only. Stop further open-ended geometry searches
until a specific new evidence source is available.

## Phase4: grid witness, bounded correction, restored-body association

The ring25 deficit is now checked at actual XYZ3 point(98.069,90) and throughout
the closed cell[98.0685,98.0695]x[89.9995,90.0005]. Existing exact top-cell query
returns full-bounded with a strictly positive gap>.0737mm over the ENTIRE cell,
still greater than maximum allowed.054mm bottom lowering. Exact rational bounds
are persisted in ring25-grid-witness.json;92 spatially relevant structural
segments participate. This proves local failure, not sampled success acceptance.

Earlier candidate material cannot rescue the cell even with conservative expansion:
largest earlier centerline radius is7.816938636mm. Granting maximum allowed
executed width.45mm and full.002mm radial path deviation gives an upper footprint
radius8.043938636mm. Cell minimum radius8.0685mm leaves gap>=.024561364mm.
This includes ring24 and does not assume its nominal width equals emitted width.

A bounded scalar routing screen checked1micron radial grid within the ring25
triangle-contained radius band[7.772020455,8.068979545].282 radii pass four-cardinal
point gap<=.054; this is only binary64 routing evidence and is not a continuous
support certificate. See ring25-radius-screen.json. Inward shift of ring25 alone
would overlap ring24, so it is not an admissible independent correction.

A specific JOINT correction is promising: shift same-floor rings24/25 inward
.03mm; available left packing slack is.044918182mm, so original widths and
nonoverlap are preserved. Ring24 keeps physicalh=.08,remaining=.08,overlap0.
Ring25 keeps physicalh339/2200 and uses remaining=.12,topZ4.320,overlap22.1238938%.
Radial triangle spills are37.8464513% and23.9524909%, both<50%. No minimum-height
relaxation and no whole-model blanket lowering is used. At grid cardinal radii
7.787/8.039, fourﾂｱ.0005mm cells each have support-lower4.2 /4.16780671058;
ring25 planned bottom is4.16590909091, so these local cells certify contact.
See ring25-shifted-cardinal-cells.json. This remains a planner candidate: ALL
emitted segments/footprints need local support/effective-height/flow/quantization/
spill/radial-gap and chronological tool checks before accepting it. Constant
path-wide q_cmd must not hide true local support-height variation (spec section11).
No claim is made that cardinal successes prove continuous circumference support.

Smallest next implementation: bounded planner candidate family may jointly shift
packed same-floor rings by declared offsets within existing band/slack, choose
permitted remaining/physical heights, retain pathcount where feasible, and evaluate
all actual quantized chords with existing support controller; publish only a fully
checked immutable candidate. Preserve original research intent for comparison.
If candidate fails, report exact rejected cells/reasons rather than silently skip,
reduce minimum remaining, change source layers, or call it physically ready.

Restored source association: full-profile and sanitized sources each contain14937
model positive-E XY moves inside31 balanced M624/M625 object spans. A read-only
routing inventory finds identical ordered tuples of start/endXYZ,width,height,E;
semantic SHA2561d4b3f6b1ca4bd605ef29b405c5bfb76ff88dfec137dc8da1e5fea745db75526.
See restored-body-comparison.json. Thus nominal source-bead geometry witnesses
transfer to restored model body. This inventory is NOT full modal interpretation.

Actual body adapter contract: source/project hash association; exact object/role/
layer markers; independently known G21/G90/M83/E/debt/feed/acceleration and actual
XYZ at entry; positive deposition after debt handling; local width/height context;
strict chronological orders; source-line/byte provenance; no startup purge treated
as model support. Startup/purge/firmware motions remain part of whole-print physical
material/clearance state and cannot simply be discarded from safety validation.

## Phase5: later pre-deposition anchors evaluated, not assumed impossible

Investigated the alternative region AFTER actual upper-Z positioning but BEFORE
first upper-layer positive material deposition, including the state immediately
before the original unretract. Such an anchor would avoid restoring lower floorZ.
It is not correct to assume the changing-layer marker is the only route candidate.

`predeposition-anchor-research.json` inventories every12 target interval in both
sanitized and full restored sources. In all24 interval/source cases, high-Z
positive-retraction states exist, but ZERO also have inherited acceleration<=saved
outer-wall5000. Minimum active M204 while retracted and actualZ>=upper is10000
in11 intervals and6000 in the upper4.0 interval. All before-unretract snapshots
are inside M624 object scope. This is conditional modal/debt routing inventory;
unknown firmware/startup commands are not asserted harmless.

Example upper3.2: sanitized line8118 (byteoffset recorded in artifact), restored
line9436. ActualZ3.2, conditional debt.8, activeM20410000. Original then unretracts
E.8, sets M2046000 and prints upper innerwall before later outerwall5000. Inserting
after unretract fails canonical positive-saved-retraction gate; inserting after
upper innerwall changes intended interval order. Neither is an unspoken fix.

Saved-before-unretract source lines for upper3.2..5.4:
sanitized8118,9287,10532,11728,12699,13666,14649,15569,16446,17289,17999,18565;
restored9436,10661,11962,13215,14244,15268,16308,17286,18219,19119,19886,20511.
Exact XYZ/debt/acceleration/objectscope/offset and first-deposition lines are in
artifact. No source acceleration was changed and no runtime override was assumed.

A future separately resliced fixture with explicitly approved lower saved travel/
default acceleration could create an eligible late anchor, but that is a new
profile/config identity and exact-source validation task, not a source mutation
or claim that current source has a usable physical anchor. Existing canonical
restriction on emitting new acceleration remains. A full downstream vertical
barrier still requires complete supported motion semantics and tool-profile
conditions; current nominal .02mm next-plane tip gap alone is not a hardware
clearance certificate.

## Phase6: approved derived-profile reslice and bounded contact resolution

Parent explicitly authorized ONE separate offline derived process variant. Created
artifacts/revolved-exponential-derived5000-9-research without overwriting existing
artifacts. Only changes (preserving saved list type): default_acceleration6000->5000,
travel_acceleration10000->5000, initial_layer_travel_acceleration6000->5000,
travel_jerk12->9. All machine limits, G-code templates and model entries preserved.
research-receipt.json records all original ZIP-entry hashes, before/after values,
input/output/executable hashes, full argv/cwd/stdout/stderr and exit0 in2.203s.
Original input hash unchanged. Output G-codeSHA256
6c9990c5ecab30f1ab56bc6ff7aa1f2d0128b426dd0976259fbd960f9e286036;
3MFSHA256b31f1489c9fbb975eefa3a087fa03c124d0b110eb331ce494d871d6cc16a15c8.

All12 late before-unretract anchors now conditionally have actualZ=upper,
positive debt, active M204S5000, parsed startup M205XY9, and inside object scope.
See conditional-anchor-review.json. Startup M204S6000 is overridden by actual
body commands before target intervals. Source also emits M204P/R/T at startup;
those semantics still require firmware-specific proper interpretation. Neither
saved jerk12 nor derived jerk9 is silently equated with actual inherited jerk:
actual file shows M205XY9 at startup and no later M205 changes in this inventory.

Model-body comparison against full restored baseline proves14937 identical ordered
start/endXYZ,width,height,E tuples AND zero changes to modal F at those deposition
moves. SemanticSHA2561d4b3f6b1ca4bd605ef29b405c5bfb76ff88dfec137dc8da1e5fea745db75526.
model-body-comparison.json records this. Source/config identity remains DISTINCT;
no old intent association or physical validation receipt is transferred.

One additional parent-authorized legal thicker jointshift experiment used the new
generic tools/audit_continuous_path_contact.py, not a duplicate geometry engine.
Artifact wrapper research_thick_pair_contact.py is runnable under exact.venv
Python and outputs thick-pair-continuous-contact.json. Uses chronological source
line orders below actual next-layer anchor14649, explicit original nominal height
.2, conservative local source culling, exact quantized points and padded rational
parameter boxes. Full-source modal truth is still a declared source-body
interpretation assumption; this is not a firmware certificate.

Ring24: shift-.03,h=.09,remaining=.08,overlap1/9,spill44.7524%.
Ring25: shift-.03,h=.17,remaining=.12,overlap5/17,spill31.0692%.
Both pass unchanged h/remaining/overlap/spill and radial packing constraints.
Audited every192 chord each with depth14,128sqrt fraction bits,1e-12mm box padding,
20000query global budget and90s cancellation per ring. Ring24:191certified,
1gap-proven,0incomplete-chord classifications;516queries,1.844s.
Ring25:128certified,64gap-proven,0incomplete-chord classifications;5488queries,6.125s.
Gap-precedence classification DOES NOT erase unresolved subintervals: failing
chords can contain supported, gap AND maximum-depth intervals. Counts retained
for all three interval states. Ring24 failure is near chord191, with actual
whole-piece-disjoint witness, refuting complete contact even if neighboring
seam intervals remain unresolved. Therefore this candidate is genuinely rejected,
not a mere proof-budget failure. No further sweep was run.

## General deterministic planner search contract (proposal, not implemented)

For each source-floor group, keep declared radial order and explicit nonoverlap.
Enumerate a finite declared set of JOINT shifts within exact triangle-band slack;
independent ring shifts require full pairwise interval revalidation. For every
shift enumerate physical h and remaining d from the pinned machine-height grid
plus explicitly retained original exact h, requiring .08<=d<=h<=.18,
0<=1-d/h<=.30, h<=w, width bounds, top within upper plane, and exact posed radial
spill<=.5. Search order/resource budget and whether all30paths must be retained
are explicit; no path silently disappears. Regenerate quantized chord families
using the approved divisor-of192 grammar; recompute q_cmd AFTER frozen intent,
then validate canonical E5-derived widths, XY radial bounds, length/time/adjacent
motion limits. Reject quantified conflicts, never relax epsilon or original G-code.

Use cheap exact/numerical rejection witnesses to route finite candidates, but
only whole-parameter interval certificates can accept centerline contact. All
whole-footprint support/effective-height/convergence gates remain in the existing
support controller. Same-Z/future candidate support is excluded. If no circular
candidate succeeds within finite family/budget, report infeasible-within-family
or incomplete (not globally impossible), and adjudicate a separate source-contour-
following/local-support planner family; do not call more samples proof. Such a
family needs explicit local bead height/flow ownership under SPECsection11 and
seam/topology/radial packing acceptance, rather than postprocess replanning.

The scalar shift/cardinal screen was routing only. Actual whole-path results
now show why it cannot justify keeping all rings. Software work can resolve this
by evaluating explicit bounded planner alternatives; absence of physical tool CAD
is separate and did not cause these nominal geometric gaps.

M204 adjustment disposition: ADR0040 explicitly defers always emitting external-
wall M204+restore and SPECsection28A forbids emitting acceleration setup/change.
Saved values do not override that prohibition. A temporary M204 cycle requires a
reviewed ADR/spec extension; current approved solution is the NEW derived slice
identity above, preserving canonical mutation restrictions.

## Phase7: one final bounded inward case; nominal-gap root cause

Parent authorized exactly one additional pair: jointshift-.044 within available
left slack.044918182. Ring24h.09/rem.08:spill49.5118394%,overlap1/9.
Ring25h.18/rem.126:spill33.4659120%,overlap30%. Original widths and pair spacing
preserved. All384 nearest-E5 amounts positive and derived nominal widths legal:
ring24.251529218.. .252565530; ring25.251837279.. .252295412.
Artifact inward-pair-e5-research.json. No epsilon/constraint relaxation.

Reviewed generic exact auditor classified ring24:191certified/1gap-proven chords,
564queries,1.766s; ring25:128certified/64gap-proven chords,4336queries,4.812s.
As before, gap-precedence chord counts can coexist with unresolved subintervals;
full interval counts/details are preserved. Wrapper research_inward_pair_contact.py
and inward-pair-continuous-contact.json are runnable/persisted. No further parameter
sweep is authorized or performed.

Root cause was traced to finite-source axial clipping, not just low curved tops:
- ring25 gap witness near(98.014895142,90.386036377), candidate bottom4.146.
  Source13802 ends and13803 starts at shared vertex(97.856,90.386,4.2).
  Lateral distances.158126/.158895 are inside width.42, but axial parameters
  1.0202285 and-.0000482453 are outside BOTH finite segments. Therefore the
  rectangle-projected nominal solids do not include this exterior polygon corner.
  The source centerline is connected at this vertex; this is not evidence that
  the real deposited join has a physical air gap.
- ring24 gap near(97.761588318,89.601187134), bottom4.19. Nearest13740 starts
  (97.854,89.592,4.2);13803 ends(97.856,89.632,4.2). These are actually separated
  source seam endpoints by approximately.04005mm. Point is laterally within both
  widths but lies just before/after their axial intervals. This combines a real
  source centerline seam gap with the finite flat-cap nominal abstraction.

Diagnostics inward-pair-gap-diagnostics.json preserves nearest source coordinates,
widths, lateral distances and unclamped projection parameters. Source material
below bottom was conservatively omitted from contact-query inputs because it
cannot reach required bottom; it still exists physically. A whole-piece-disjoint
result means NO qualifying high-enough nominal source solid in that interval,
not absence of all material everywhere and not measured print-void evidence.

Canonical ownership is explicit: ADR0048 states v1 flat axial caps and rectangular
XY projection rather than XY capsule, and warns the model is not a claim that
real extrusion forms exact stadiums with flat path ends. ADR0044 specifies axial
disjoint tests and flat-cap regression requirements. Do not invent rounded caps,
join lobes or endpoint disks to force an acceptance result. Changing the model
requires separate physical/source evidence and reviewed ADR/spec change.

Smallest geometry next step: source-contour-aware planner routing candidates,
remaining within declared radial band/packing and height/overlap/spill limits.
At ordinary connected vertices an exterior circular offset can leave both source
rectangles; a deterministic vertex detour toward their shared interior overlap
can be proposed and exact-tested. A source seam is different: first establish
that the qualifying support superlevel-set has a continuous corridor within the
allowed band, using conservative cells, before proposing a closed ring. Never
assume tracing a polygon or more sample points bridges a seam. Pairwise path
footprint nonoverlap and whole-footprint support must be revalidated for any
noncircular detours. This is a new planner family, not adapter interpolation.
The finite circular candidates tested are rejected under the current model;
no claim is made that every possible route in the allowed domain is impossible.

## Bounded next executable proposal and seam distinction

The tested constant-radius/jointshift/thickness family was rejected; it does NOT
prove global infeasibility. No further experiments are performed in this phase.

Smallest next planner family is a generic certified-support-corridor router:
1. Consume exact chronological nominal source segments and approved same-floor
   radial bands/packing, original IDs and required retained path count.
2. Enumerate an explicit finite h/remaining grid family satisfying existing bounds.
3. Use the existing exact kernel/refinement to certify support/effective-height
   corridors within each allowed band; preserve unresolved cells separately.
4. Derive deterministic radial detours at actual source polygon vertices, searching
   only corridors with the required closed winding topology and ordered pairwise
   bead-footprint nonoverlap. No hardcoded ring IDs or arbitrary endcaps.
5. Freeze quantized paths, recompute q_cmd/E5 and rerun whole centerline AND full
   footprint support, remaining/height/overlap/spill, regularity and clearance.
   Reject a specific candidate only with witnesses; unresolved corridor existence
   remains incomplete, never silently omitted paths or global impossibility.

This is an explicitly new planner scope/handoff, not permission for emitter
replanning. A first implementation milestone may publish corridor bounds and
routing feasibility only before producing new immutable candidate paths.

Actual saved source declares seam_gap10% at line536 and seam_positionaligned at
line537. Approximately.04005mm source seam endpoint separation is consistent
with that configured gap (not a measured physical void). Moving seam position
relocates this source-model defect; any complete circle can still cross the new
seam. It does not repair ring25's repeated ordinary convex-vertex flat-cap gaps.
A separate explicitly approved seam_gap0 experiment might remove source loop
truncation but still needs source proof and would not add missing exterior join
volume to the nominal model. No such profile change or experiment was performed in that earlier phase; see the later authorized seam0 experiment below.

## Outward diagnostic correction pending finite-area owner

Parent independent adjudication found posed_intersection_area extrapolates beyond
triangle base. The outwardring25+.04 reported30.03188% spill is INVALID for a
finite triangle; do not use it for admissibility. Parent independent finite-area
calculation gives41.14119% (still<50), pending new authoritative owner/review.
Previously contained radial cases are unaffected. Outward contact audit itself
is a separate geometric result:191certified/1gap-proven chords; band containment
is exceeded.04 and current numeric intent remains unapproved for this case.
No automatic fingerprint or plan identity transfer is made to seam0 source.

## Phase8 CURRENT: outward contact diagnostic and authorized seam-gap-zero slice

This phase supersedes earlier statements that no seam0 experiment occurred.
The parent explicitly authorized ONE separate experiment setting only saved
seam_gap10% to0%. Original canonical, restored and derived5000/9 sources remain
unchanged. First attempt folder
artifacts/revolved-exponential-derived5000-9-seam0-research was retained after an
assertion stopped BEFORE slicing: this key is a string, unlike acceleration
list fields. No original was modified. A NEW v2 folder was used, preserving exact
string type: seam_gap='0%'. No failed artifact was deleted or overwritten.

Successful folder: artifacts/revolved-exponential-derived5000-9-seam0-v2-research.
research-receipt.json has input/project/exe/output hashes, exact before/after,
original ZIP-member hashes, argv/cwd and exit0 in2.203s. G-code SHA256
fc1655086645ba1fd3758b4c5554fa3039044d6ba126457f473470d2d28eee60;
sliced3MFdd9a236689c0517057f14fc38d6ec36876c79777ed3a56307b17e32c55d0fc9b.

Actual model deposition changed legitimately:14985 positive-E XY moves versus
14937;13633 ordered XYZ/width/height/E tuples unchanged,154 changed sequence
blocks. Old deposited Etotal503.77006,new503.97845 (+.20839mm). Full ordered
actual source line,XYZ,width,height,E,F rows in nominal-model-rows.json and
alignment changes in model-body-comparison.json. Seam extensions alter last
segments, closure and subsequent path starts; never reuse old intent fingerprints
or assert source equivalence. This is a NEW source/config identity.

Outwardring25+.04,h.18/rem.126 retained30% overlap and pair separation but exceeded
original triangle-band containment by.04. Contact-only audit certified191chords
and found1gap-proven at seam, versus64ordinary corner-gap chords for inwardcases.
No admissibility is claimed. Its original extrapolated spill30.03188% was INVALID
outside the finite base; artifact now labels it invalid. Parent independent
finite-area diagnostic41.14119% awaits authoritative reviewed area owner. No
numeric-intent guard was widened.

Future material overlap matters separately: original upper4.4 source line14787
runs(98.405,90.413,4.4)->(98.405,89.602,4.4), width.42,height.2. At XYprobe98.22,90,
nominal candidate stadium interval is approximately[4.18625,4.28575] and future
structural bead[4.23386,4.36614], overlapping by approximately.05189mm vertically.
This binary64 diagnostic is in outward-next-layer-geometry.json; exact finite-
volume validation is still required. Higher future nozzle tipZ does not prove
future structural bead-volume compatibility or whole-tool clearance.

All30 ORIGINAL nominal circle recipes (192chords each) were audited against actual
NEW seam0 model rows by research_seam0_all_contact.py. Actual chronological source
line order at next-layer first model deposition is explicit; source widths/heights
come from new file. This is contact diagnosis with a deliberately unpromoted
research recipe, not current executable Plan publication. Full firmware startup
interpretation remains unknown; source body assumptions are labeled.

Policy: generic reviewed auditor, parameterdepth12,sqrt128bits,padding1e-12mm,
10000queries/ring,100000global,90s cancellation threshold. All5760chords received
classifications:2271fullycertified,2513gap-proven,976incomplete.46989queries,
97.234s total (90s stops kernel work; extraction/report bookkeeping adds time).
Interval totals:supported14098,gap10190,unresolved2574; gaps and unresolved
subintervals can coexist. NEW seam0 ring24 is fullycertified192/192, directly
supporting the configured source seam-gap cause. Ring25 hits budget after176gap
chords,16incomplete; rings26..30 each192incomplete. They are NOT declaredfailed.
Other original nominal recipes retain curved-top/flat-cap contact deficiencies;
seam0 alone does not establish all30 feasibility. Exact per-ring/chord counts and
policy in new folder/nominal30-contact-review.json. No further sweep performed.

Current smallest next work remains explicit immutable planner alternatives with
full chronological source/future-volume validation. Outward diagnostic supplies
a useful source-support family but cannot bypass containment/overbuild/volume or
packing constraints. Physical tool-envelope evidence remains separate. No printer
connection, physical print, code/test edits, commit, push, merge or release.

## FINAL evidence correction: authoritative finite-area receipt

Recomputed outwardring25+.04 using reviewed owner
`tools.solve_triangle_rectangle.finite_triangle_rectangle_intersection_area`
under exact.venv Python. Exact finite spill is61993776587/150685429950
(41.1411883734%), passing50%. The old extrapolated30.03188% remains
marked INVALID historical evidence; outward contact receipt now contains the
authoritative exact fraction. This does not remove.04mm radial containment
overshoot, future nominal structural bead-volume overlap or any physical gate.
No kernel experiment, reslice or sweep was repeated for this correction.

Final current state: the authorized seam0 experiment DID occur (Phase8 supersedes
earlier no-experiment statements). It certifies nominal ring24 centerline contact
but not all30paths. Tested-family rejections are not global infeasibility proofs.
The outward future-bead overlap is a nominal volumetric diagnostic, not a head
clearance or physical-print certificate. All originals preserved; no print,
connection, commit, push, merge or release.

## User-authorized provisional0.4mm dimensional analysis (research recommendation)

User explicitly said proceed provisionally with0.4mm and make it configurable.
Do not request CAD again or block offline software work. This authorizes a
PROVISIONAL dimensional assumption, not fabricated physical fixture evidence.

Smallest useful implementation: add one tools-owned keyword parameter
`provisional_tip_disk_diameter_mm` to review_hops and expose a CLI option such as
--provisional-tip-diameter-mm. Default is exact0.4mm (user assumption); derive
radius exactly by division2, so default radius0.2mm. Keep saved resolved
`profile.setting('nozzle_diameter')` separately reported as orifice diameter with
its existing source-key/hash provenance. Both happen to be0.4 now; never treat
that coincidence as a verified head-body radius or overwrite saved settings.

Wire the parameter into actual numeric review output, not metadata alone:
for every proposed transition compute the axis-aligned enclosure of its XY
segment swept by the provisional disk: min(startX,endX)-r through max+r and
analogousY. Also report path-wide XY footprint bounds from actual quantized
candidate points expanded by r. This is a conservative planar disk-sweep box,
not a3D cylinder, sphere or complete tool envelope. No head height is assumed.
It can directly drive an offline footprint overlay/inspection. Label its
scope tip-plane/provisional and its assumption source user-provisional.

A later optional diagnostic may use existing generic point-to-segment numerical
helper tools.audit_layered_preview_overlap._point_distance for endpoint-disk vs
source XY projections. centerline_distance in that file only accepts horizontal
candidate segments and must NOT be applied to arbitrary bridges. Those float
projection distances are review diagnostics, not exact collision certification;
projected overlap at Zsafe does not imply physical collision. No full clearance
validator exists here to activate; do not create one implicitly in this change.

Ownership remains tools/review layer. Do not construct ToolClearanceProfile,
ToolRadialKeepOut, fixture_evidence_ref, axial_height or safety margins from the
single diameter. Domain/settings.py stays unchanged; canonical SPECsection29
requires physical provenance for a real tool profile and forbids inferring body
clearance from orifice diameter. SPECsection30 explicitly permits analysis/
preview without ToolClearanceProfile, consistent with the user's provisional ask.
No physical injection or authorization result changes.

Identity: report a versioned research model tag and explicit exact diameter/radius,
assumption provenance, saved nozzle diameter, source/project/manifest hashes.
Bind these to a separate deterministic review-assumption fingerprint so changing
0.4 to0.6 changes review identity/cache eligibility. Do NOT smuggle it into the
closed canonical PluginSettings schema or claim a physical ExecutionConfig
fingerprint. Saved nozzle already belongs to resolved source identity. Review
assumption identity is not a PlanHash or validation certificate.

Focused tests: default0.4->radius0.2; override0.6->0.3 and each bound expands0.1;
zero/negative/nonfinite/malformed input rejects; diameter never used as radius;
axis-aligned, reversed and zero-XY-distance transition boxes remain correct;
all actual18bridges/30paths include derived bounds; changed diameter changes
research identity but not source/profile hashes; saved nozzle and assumed disk
can differ visibly; no ToolClearanceProfile created, no source bytes modified,
all existing physical-authorized flags remainfalse. Existing source-profile and
supplemental hop tests are nearest regression checks. No implementation/test
edits were made by this investigation.


### Current bounded template evidence: exact-span lanes, not complete remaining groups

This phase supersedes any earlier implication that the coalesced two-lane proposal file contains accepted groups. Current complete nominal groups remain six: floor 4.2 and the five single-path groups at floors 4.4 through 5.2. These establish nominal centerline contact and the recorded nominal bead separation only; they do not establish full flat-bottom support area or physical head clearance.

`artifacts/print-source-inspection/floor32-circle-exact-proposals.json` records a bounded five-lane attempt at floor 3.2. Original radii were increased by lane-index times 0.002 mm before XYZ3 freezing. Ring 9 used physical height 0.12 and remaining height 0.084 mm; the other four used 0.18 and 0.126 mm. Each lane had a 20,000-query/30-second contact budget. Ring 9 has 160 certified and 32 gap spans; rings 10–13 each have 192 certified spans, zero gaps/incomplete. All emitted E5-derived widths and finite-area spill bounds are legal. Conservative packing gaps are -0.000123124, -0.0000323572, +0.0000503259, +0.000132564 mm, respectively. Ring 13 has a negative radial future-separation bound (-0.00956457 mm), which is unresolved by that sufficient test and is not an overlap certificate. The group is not accepted. This exact result also demonstrates why the earlier vertex/midpoint routing probes were not acceptance evidence.

`early-group-sourcefollow-finitearea-grammar.json` enumerates actual closed-contour zero-offset templates on floors 3.0–3.6, physical heights 0.08:0.01:0.18 mm, remaining heights 0.080:0.001:0.180 mm, widths 0.27/0.35/0.45 mm, with unchanged overlap bounds and exact finite triangle area. This includes the subsequently authorized higher-remaining family. At floor 3.2 the inner 0.42-mm source contour has minimum spill 0.696924 within this finite grammar; the outer 0.45-mm contour lies outside the triangle. These are template-family rejections, not global infeasibility.

`early-source-follow-certified-lanes.json` adds three usable individual lane templates on the actual seam-zero source. Each follows the exact source XYZ3 vertices, uses intended width 0.27 mm and physical/remaining height 0.08 mm, and has legal E5-derived widths:

- Floor 3.4: 0.45-mm source contour beginning line 10486; all 64 spans certified, zero gaps/incomplete; finite spill 0; conservative future radial gap 0.331637882 mm.
- Floor 3.6: 0.42-mm contour beginning line 11831; all 64 spans certified, zero gaps/incomplete; spill 0.395188189; future radial gap 0.514256193 mm.
- Floor 3.6: 0.45-mm contour beginning line 11763; all 64 spans certified, zero gaps/incomplete; spill 0; future radial gap 0.078782239 mm.

These individual lanes are suitable inputs to a generic finite template/packing search; they are not complete three-lane groups. A circle-only or offset-only failure does not exclude other legal routes.

The one-micrometre junction perturbation in `two-lane-contour-junction-repair-proposals.json` is diagnostic only. For the inward-offset second lane at floor 3.8 it fixes the first span but transfers the exact finite-cap gap to the closing span. Adjacent source directions (-0.002,-0.020) and (-0.065,-0.660) form a slight concave junction. Their inward finite axial domains leave a wedge away from the shared source joint. A grid-neighborhood repair must not be presumed to bridge this topology. A source-joint detour must be explicitly represented before freezing and independently checked for finite-area, packing, contact, and future bead volume; invented endpoint caps or relaxed support gates are not permitted. At floor 4.0 moving the first lane inward to 0.05 mm gives positive conservative packing gap 0.020619915 mm, but contact gaps/incomplete remain, so that set is also unaccepted.

All receipts here are research records pinned to seam-zero source SHA256 `fc1655086645ba1fd3758b4c5554fa3039044d6ba126457f473470d2d28eee60`. They do not associate old immutable intents automatically, authorize source mutation, or grant printing authority.


#### Corrected exact-span budget accounting and source-joint detour follow-up

Parent review identified that `cells_queried` counts box queries only and is zero in exact-span mode. The research wrappers now use authoritative `query_count` in separately named `*_query_count_corrected.py` scripts, writing new `*-query-count-corrected.json` receipts. The previous receipts remain preserved and their query totals must not be used. The source-joint detour, early 3.4/3.6 zero-offset lanes, and floor 3.2 five-circle attempt were rerun under true shared query budgets; geometric classifications remained unchanged. Floor 3.8 detour lane counts are 65 and 80 queries; floor 4.0 counts are 92 and 66.

The detour recipe is explicit source geometry before freezing: at floor 3.8 the inward-offset route's seam vertex is replaced by the shared actual endpoint of source line 13064 and line 13000, XYZ (96.947,89.639,3.8). At floor 4.0 the outer counterpart is the common endpoint of lines 14062/13998. These identities explain the bounded recipe; a reusable generator must select a joint by source identity/topology rather than hardcoding vertex index zero. Source geometry remains unchanged.

At floor 3.8 the 0.27-mm-width detour has all 64 outer contact spans certified, spill 0.329787884 and positive pair packing gap 0.029357210 mm. Its all-future nominal volume review covers 411584 pairs: 411299 AABB separated, 282 exact separating-axis certified, three unresolved by that sufficient test. The reviewed pair auditor establishes two of those disjoint and a positive-volume overlap with future line 14068 (witness vertical depth approximately 0.000130532 mm). Therefore this set is rejected. Narrower intended width 0.253 mm also retains full contact, spill 0.315296782 and positive packing, but still has a proven overlap with line 14068. A further legal h=0.114, remaining=0.080, intended width=0.252 mm candidate retains full contact and spill 0.458195442; its first targeted future-pair audit also proves overlap. No all-future acceptance is claimed for these rejected variants. Pair-auditor early overlap leaves unvisited cells explicitly unresolved; that does not weaken the positive overlap witness.

Floor 4.0 source-joint detour fails finite spill (approximately 0.723195 at width 0.27) and packing, so it is not an admissible candidate. These bounded recipe rejections do not prove global infeasibility of other routes, varying lane placement, or the authorized second remaining-height family.


#### Accepted nominal seventh group: localized finite-joint detour at floor 3.8

The preceding rejected long-diagonal detours are superseded by a distinct localized route, not by weakening any gate. `two-lane-source-joint-localized-coalesced-detour-proposals.json`, group floor `19/5`, records:

- Inner lane: unchanged actual 0.42-mm source contour, intended width 0.27 mm, physical/remaining height 0.08 mm; all 65 spans certified, zero gaps/incomplete; maximum finite spill 0.309568938 and future radial separation 0.339916000 mm.
- Outer lane: actual 0.45-mm contour inward offset 0.10 mm, intended width 0.253 mm, physical height 0.09 mm, remaining 0.08 mm (overlap 1/9). At the explicitly identified source joint 13064→13000, insert candidate waypoints at source arclength 0.03 mm before/after the joint, and pass through the actual joint. Remove an adjacent candidate vertex when its segment to the new waypoint is shorter than 0.05 mm, before freezing, then independently check the entire route. All 65 final XYZ3 spans certify continuous nominal centerline contact, zero gaps/incomplete. E5-implied widths are legal; maximum finite spill 0.314888914. Conservative radial packing gap between the two actual-width lane envelopes is +0.014510598 mm.

`floor38-localized-detour-future-separation.json` proves separation from ALL 418015 chronological future nominal model pairs for this 65-edge outer candidate: 417730 conservative AABB exclusions, 285 exact rational support-axis separation certificates, zero unresolved. The pair universe is 65 candidate edges times 6431 future model beads. The support-axis proof uses the frozen E5-implied actual width of each candidate edge. All source and candidate beads satisfy the recorded flat-Z, width>=height, nonzero-XY conditions. The positive result belongs to this localized geometry only; it does not transfer to the rejected long-diagonal variants.

Current complete nominal groups are therefore SEVEN of twelve: floor 3.8, floor 4.2, and the five one-lane floors 4.4–5.2. This is still nominal centerline contact and nominal material nonoverlap, not full-bottom-area support, travel/head clearance, global job validation, or physical printing approval. The generic planner can generate explicit source-joint/arclength detour proposals before immutable freeze and accept them only after the same exact gates; it must not hardcode source indices or infer that every joint is feasible.


#### Accepted nominal eighth group: floor 3.2 re-packed circles

`floor32-repacked-spaced-circle-exact-proposals.json` records five circles with intended width 0.251 mm and radii `3.185 + k*0.254` mm for k=0..4. The first uses physical height 0.137 and remaining 0.096 mm; the other four use 0.18 and 0.126 mm. Every one of 960 XYZ3 spans certifies whole-centerline contact with zero gaps/incomplete; all E5-derived widths are legal. Maximum exact finite spill is 0.496601668. Conservative radial packing gaps are +0.000848691, +0.001204917, +0.001120222, +0.000814069 mm. The inner four have positive radial future separation. The outer candidate's full future universe contains 1668480 pairs: 1667758 AABB-separated, 722 exact support-axis separated, zero unresolved, 46.75 seconds.

The authoritative paired receipt is `floor32-repacked-outer-future-separation-provenance-corrected.json`. The earlier receipt incorrectly named the old source-offset candidate in a metadata label, although the executed script read the new five-circle last lane. The new receipt preserves the geometry/certificates, corrects candidate ownership, and adds candidate-file SHA256 `6c61e8fc7044463cf69aa54e400a05bc31d412944923b1b3157126455175ca55`, frozen-path canonical SHA256 `6c9ca45203a3db77cde1d209d305bea25a820a9623ebf8036a8f5d667c981a4f`, canonical encoding, and source/project/rows hashes. The original receipt remains preserved for provenance.

The width/height/radius changes alter quality. `floor32-repacked-area-comparison.json` records old radial-rectangle reference triangle symmetric-difference area `1294694681/60204500000` mm² and new intended reference `2550411739/21650000000` mm², plus separately labeled conservative actual-width/radial-rectangle surrogate bounds. This is not a claim of equal quality, full 3D volume accuracy, or a new quality gate. Error improvement remains deferred by the user.

Official complete nonstacked nominal groups are now EIGHT of twelve (3.2,3.8,4.2,4.4,4.6,4.8,5.0,5.2).

#### Conditional stacked research, not selected or implemented

Parent authorized a separate support-base research family, then requested user clarification because the earlier current-layer-top wording may require every bead to start from the original source floor. No stacked job is selected and no existing intent/composer base semantics are changed.

`stacked-sourcefollow-second-row-research.json` records a second row on each previously certified outer 0.45-mm source-follow first row at floors 3.4 and 3.6. It distinguishes `original_step_floor` from `current_support_top = original_step_floor+0.08`. The second physical height is 4/35 mm, remaining relative to immediate printed support is 0.08 mm, overlap is 30%, absolute top is original floor+0.16, and bottom is original floor+8/175. Its source dependencies are the actual chronological first-candidate E5 beads. Each second row has all64 spans certified, zero gaps/incomplete; widths are legal; spills are 0.391664249 and 0.126314436 respectively; future radial gaps are +0.331687045 and +0.078808023 mm.

Floor 3.4's third path is the original outer radius `5.3034888392857145` mm, re-frozen at intended width0.251, h0.18, remaining0.126; all192 spans certified, actual widths0.250618..0.251287, spill0.3, future radial gap+0.006983612 mm (`floor34-original-outer-circle-compensated-proposal.json`). Floor3.6's third path is its separately proven inner0.42-mm source-follow first row. Thus both floors have concrete three-path proposals conditional on support-base semantics.

`stacked-three-path-group-packing-union-review.json` records the DAG and allowed immediate-support overlap, with positive cross-corridor packing gaps +0.071845453 and +0.157075847 mm. Its 2D radial-Z surrogate union area subtracts the support/second-row overlap rather than double-counting it. Old/new reference symmetric-difference areas are respectively approximately0.016993919/0.074370321 mm² (3.4) and0.015138623/0.045941554 mm² (3.6). Contour reference radius is explicitly the midpoint of certified radial bounds; actual-width/radial union bounds are recorded separately. These remain surrogate diagnostics, not full 3D union-volume or support-area proof.


#### Explicit reduced-count floor3.0 trial (not selected)

Parent authorized a separate fewer-but-wider research family, retaining count8 as the first conservative target rather than a global user requirement. `floor30-seven-lane96-repacked-experimental-proposals.json` contains seven 96-chord circles, intended width0.252 mm, radii0.910+k*0.256 mm. Heights/remaining are0.137/0.096,0.175/0.123, then0.18/0.126 mm. All672 spans certify contact, zero gaps/incomplete; E5 widths remain within0.25..0.45; maximum finite spill0.487001724; six packing gaps are positive0.00134..0.00161 mm. All candidates have positive conservative future radial separation, minimum0.013921863 mm. Ideal chord deviation maximum0.001309619 mm is below the existing0.002-mm chord budget; XY3 displacement is separately bounded by sqrt(2)/2000 mm.

This is not silent omission: `floor30-seven-lane96-reference-comparison.json` lists every old/new radial interval and exact covered lengths. The old physical radial-rectangle reference symmetric difference is approximately0.0294503413 mm²; the seven-lane trial is0.1742798126 mm². The substantial surrogate quality regression is explicit, so the record remains a trial, not a selected job. Exact rectangle-solid-of-revolution union-volume coefficients are recorded separately from commanded filament volume and inferred un-unioned stadium sums. Actual finite-stadium chord union volume has not been exactly integrated; summing emitted E is not claimed to prove that union. This distinction prevents an unsupported volume/coverage assertion.


### Current handoff: nonstacked proposals now address all twelve steps

Parent clarified that complete processing does not require zero target residual: every original step must be analysed, pattern/count changes and uncovered/error terms must be explicit, and every actual path must meet its physical/numeric gates. A new feasible pattern may improve the unsupplemented stair while having worse surrogate error than the unprintable original preview. Consequently the earlier seven-lane3.0 trial is not blocked solely by its count/error difference; it remains subject to independent proof/error review and shared factory freezing.

`nonstacked-reduced-count-final-groups-review.json` rechecks fixed actual E5 width separately for every segment, finite spill, radial packing, interval coverage, rectangle-solid-of-revolution reference volume and conservative actual-width/radial-rectangle surrogate error bounds. It proves:

- Floor3.0: seven96-chord circles described above. Error upper0.181028891<unsupplemented0.2587 mm². Actual XYZ3 segment radial-band deviation is at most0.001463354 mm, below0.002 mm. All672 contact spans and actual numeric/future bounds remain valid.
- Floor3.4: source-follow actual0.45-mm contour, intended width0.39,height=remaining0.116 mm, all64 contact spans certified; plus original ring16 radius5.3034888392857145 at width0.251,height0.18,remaining0.126, all192 certified. Packing gap+0.011946031 mm, spills<=0.3, all-future minimum radial gap+0.006983612 mm. Error upper0.058334318<unsupplemented0.1118 mm².
- Floor3.6: actual inner0.42/outer0.45 source contours, both intended width0.42 mm; height=remaining0.08 and0.15 mm, respectively. Both64/64 contact-certified. Packing+0.007144028 mm, spills0.413505356/0.084971914, future minimum radial gap+0.003840682 mm. Error upper0.032186198<unsupplemented0.0867 mm².

These explicit two-path patterns replace the old three-path preview family at3.4/3.6; no stack semantics are needed or selected. Old preview quality, new intended reference and conservative executed-width surrogate bounds are separately retained. No global optimality or full3D union-volume result is claimed.

#### Floor4.0 open arcs and replacement patch

`floor40-local-arc-patch-family-proposal-with-angular-checks.json` defines a new explicit family. Starting from the positive-packing inner0.05-mm inward/outer0.19-mm inward contour routes, remove exactly inner edge IDs1/64 and outer IDs63/64 because their complete XY bead AABBs conflict with the reviewed broad patch. Keep each remaining62-edge chain as an OPEN arc; never reconnect across the omitted interval. All124 retained spans certify contact in124 exact-span queries, zero gaps/incomplete. Their unchanged E5 widths and heights are legal; finite spills are checked per emitted segment. Their radial packing remains+0.020619915 mm; future radial exclusions remain positive. Every retained full bead AABB is disjoint from the patch full bead AABB.

The replacement is the independently reviewed source-aligned fragment `(97.390,89.610,4.126)->(97.380,89.510,4.126)`, intended width0.44,h0.18,remaining0.126,E0.00296,actual width0.4402326934, supported by actual source14068. Its source/contact/finite-spill/all-future proof is `docs/implementation/floor40-local-seam-patch-feasibility-2026-10-18.md`. The patch gain is conservatively omitted from the proposed angular-weighted radial-rectangle surrogate upper bound:0.043848992<unsupplemented0.0621 mm². Removed arc sectors retain their unsupplemented target error. Exact cyclic angular ordering, adjacent cross/dot checks, disjoint radial lane envelopes and patch centerline angular cone checks are recorded. This is a proposed research extension/reference for the changed orientation and requires canonical error-owner/spec adjudication; it is not a full3D bead-union volume or surface-error certificate.

#### Shared chronology and handoff ownership

The twelve proposed groups have successive full candidate-bead Z gaps0.020,0.020,0.074,0.040,0.066,0.020,0.074,0.120,0.120,0.120,0.120 mm. Thus different source groups' candidate volumes are Z-separated using actual selected heights, including3.6 remaining0.15; the former global remaining<=0.126 search assumption is unnecessary. Same-group packing/patch bounds remain separately required.

`twelve-group-nonstacked-research-handoff.json` enumerates all12 floors and28 proposed paths. It includes2660 explicit frozen research segments and the existing192-edge ring24 factory recipe, for2852 total. It is a proposal manifest, not an immutable approved plan: generic shared factories must re-freeze the intended geometry/flow, match or re-audit actual widths, validate current source association and execute current body/anchor/motion/provisional-disc gates.

`branch-free-model-geometry-reassociation-evidence.json` explicitly compares all14985 ordered model depositions of proof sourcefc1655... and current branch-free sourcef917ca.... Start/endXYZ,width,height,E are exactly equal in order, canonical geometrySHA256 `efc398515a96ba55c1935adda08e4641c05d1c35d54a717eca71e418ef940282`. It records every deposition-index/old-line/new-line mapping and14253 F changes. Only saved time_lapse_gcode changed in the unsliced projects. This supports a reviewed geometric certificate reassociation, not automatic approval transfer, motion equivalence or firmware/head proof.

#### Sole additional seam-position experiment: hypothesis falsified

Parent authorized one isolated slice from the already branch-free seam-zero input, changing only seam_position aligned->back. All other settings (including already-empty time_lapse_gcode), nonsettings ZIP bytes, geometry/transforms and resolution0.012 were preserved. Official source commit8160f64cae78c6d4311c514d923841d8024f7d30 maps `back` tospRear and prefers largerY candidates, but still aligns seams; exact producer-binary commit equivalence was not assumed. Input/output/producer/source hashes, argv and changed values are saved under `artifacts/branch-free-seam0-back-nominal-research`; the single slice exited0 in1.469 seconds. New source SHA256 `d9cdb7800f595d533b93ce219ec66415f1c482a83c5e80946df87622e87195a6`.

Full model comparison is14985->14988 depositions,9822 ordered matching tuples,138 changed blocks and9351 F changes on matching geometry. New all-target contour catalog is retained. Floor4.0 outer loop still has65 edges and one concave turn; the targeted inward0.19/h0.11/remaining0.08 route is63 certified+1 gap, no incomplete. The seam-back hypothesis did not solve the connector. A broad contact diagnostic started before parent limited the scope was interrupted after four original circles; no fulljob result is claimed. No second slice was attempted. The working branch-free/seam-zero baseline and its proofs were preserved unchanged.


### Explicit input-recipe and whole-program geometry follow-up

The latest handoff is `twelve-group-nonstacked-explicit-recipes-v5.json`, SHA256 `165649f536f5ce99a999bc50c6b875b6baf6a1b865a2e7af6da63002baa3ed22`. Earlier versions are preserved. All12 groups/28 paths contain explicit intended width (never reconstructed from emitted E), physical/remaining height, exact original floor/upper, closed/open graph and all2853 grid segments. Circle center/radius/count/phase, source-contour IDs in bothfc/f917 namespaces, joint locality and regularization, arc exclusions/grid adjustment, and patch source/geometry are explicit. Ring24's192 edges and emission were actually derived through the pinned `prepare_ring_intents` owner and original source/project/manifest hashes. Legal emitted IDs are explicit. All recipes remain unaccepted proposal inputs requiring shared freezing and current-source verification.

The extra segment compared with the first research handoff is intentional: the generic source-joint factory protects source joint13000 before regularization, removes13064 and retains13001. Its outer3.8 contour has66 edges, not the research wrapper's65. The wrapper had removed13000 then overwritten the next surviving miter, so generic parity was not valid. The new factory receipt `artifacts/source-joint-detour-review/floor38-two-paths.UNVERIFIED.json` carries66 whole-contact queries, all424446 future pairs separated and positive packing0.037720727 mm. The manifest uses that actual new graph, records the difference, and never transfers old65-edge acceptance. v5 additionally opts into exact-collinear source-vertex coalescence only for floor4.0 inner arc; the owner/hash/test references are explicit, and other paths opt out.

`whole28-perpath-radial-spill-v4.json` uses the existing exact spill owner with32 center bins,8 width bins,max256 cells to bound all28 actual-width/radial parameter ranges. All report complete; largest spill bound is below0.497095. Every group's stated surrogate upper improves its unsupplemented triangle reference. In particular the3.8 updated contour's outer radial footprint extends approximately0.058107723 mm beyond the base. This is permitted only through the rigorous finite spill bound; it is not asserted contained in the base. A looser whole-envelope symmetric-difference diagnostic above0.0721 was inconclusive, not infeasibility; the partitioned-spill positive-gain bound is tighter.

`original-target-step-coverage-and-exclusions-v2.json`, SHA256 `64440af108352493e311e5ca789163a83861e0826bfb430b56d3514858bc16b1`, links v5 and enumerates ALL16 original selected steps. Twelve map to proposed groups; four retain explicit original short-base exclusions under strict `base^2 < 2*(minimum_width)^2`, with equality not excluded. Exact floor/upper/radii/base/rise, angle tangent, original boundary source identity, and every excluded triangle's residual/error remain recorded. No original target silently disappears.

#### Raw E and actual material reassociation correction

The raw model-tuple equivalence receipt is routing/geometry evidence, not deposited-material equivalence. Parent's actual typed f917 body identifies21 positive-E events that consume retraction debt0.00001 before depositing. Under the separately declared distance/E-affine nominal motion contract, structural support begins at parameter debt/rawE; rawE is not depositedE. Current support association must crop those starts and recheck affected contact. Uncropped source beads may only be used as conservative supersets for material avoidance, not successful support. Width/height/E annotations and old raw line identities are not sufficient by themselves. v5 does not contain accepted flags and does not override this correction.

#### Actual lower-floor anchors and provisional0.4-mm tip sweeps

The provisional tool is a configurable diameter0.4-mm, radius0.2-mm, zero-height disc, not measured head geometry. Parent's actual twelve-anchor receipt is `parent-twelve-current-anchors.UNVERIFIED.json`; saved anchors are at the lower source floor. The first subsequent travel is a spiral/sloped sequence beginning at that lower Z. Therefore the earlier upper-Z shortcut is valid only after the first-upper-positive barrier and must not erase the first travel or the return-to-floor motion.

`whole28-actual-anchor-firsttravel-tip-disc-research.json` reconstructs the existing typed f917 trace under its declared assumptions, checks return descent to each actual saved floor/XY and EVERY explicit G0/G1 motion through the first upper positive extrusion. Across77031 motion/candidate-bead pairs,77027 separate by conservative AABB and4 by existing public exact bead-projection queries with exact disc support bounds;23 projection queries,zero unknown. The non-AABB cases occur at4.2 (three) and5.2 (one). Earlier candidate groups are independently Z-separated. This is a nominal conditional-body result; startup/suffix/runtime or whole-head authority is not inferred.

`whole28-later-original-motion-Z-barriers.json` enumerates every later typed-body G0/G1 event after each first-upper-positive barrier and records ordered event identities. It covers25379882 source-event/candidate-bead pairs by strict Z separation, minimum gap0.05 mm. The opaque M981 suffix is outside this body proof. Candidate extrusion is above all earlier original-layer material; different earlier candidate heights/groups are separated by their actual Z bounds. The18 same-Z unrelated-path pairs were separately checked by whole radial top-flat bounds or all finite segment-pair distances in `whole28-provisional-tip-chronology-v3-research.json`; all separate. Lift/ceiling travel/entry descent use those same chronological bounds. The actual source-return descent is covered by the preceding77031-pair receipt, not assumed safe from its endpoint.

`whole12-anchor-source-boundary-touch-witnesses.json` gives exact XY/public-top-point witnesses for all12 saved source anchors against affine-cropped actual source material. These are initial raise/final return top-boundary contacts only. `whole28-ownpath-boundary-touch-witnesses.json` gives93 exact XY/top witnesses for lifts, predecessor joints and closed seams, including13 nonadjacent local deposited-trail contacts. Z equality alone was not used as an XY contact witness.

The complete same-path causal broad-phase inventory is `whole28-ownpath-all-causal-pairs-top-boundary-inventory.json`:186743 pairs,180348 strictly XY-separated from earlier top-flat strips,6395 potential boundary-contact pairs. All potential pairs are local in path topology (at most6 intervening edges on the smallest short-chord circle). A zero-height plane at a path's constant top cannot enter its own earlier bead's strict interior, but that does not authorize all boundary touching. The remaining scoped software gap is exact XY separation/touch classification and a typed geometric deposited-trail/seam contact region for those6395 potential pairs, with provenance. Direct adjacency alone is insufficient. No blanket same-path or source exemption is granted.

#### Full-footprint support metrics: diagnostic only

Used the existing `evaluate_support_coverage` owner with actual typed-source debt crops, actual per-segment widths, floor-relative Z translation, and per-segment effective-height range max(0.08,0.7*h)..h. Same/higher-Z candidate material cannot be passed as support because the owner explicitly requires candidate supports strictly lower than commandZ; it remains a separate collision input. No new physical support threshold was invented.

`whole2853-coarse-fullfootprint-support-diagnostic.json` queries ALL2853 full footprints with a conservative one-cell/two-level budget:204 numerically supported under the declared analysis-only area1/full-width benchmark,2649 incomplete due resource limit,2853 cells,10.06 seconds. No skipped/cancelled segment is converted to supported. `whole28-firstsegment-fullfootprint-support-diagnostic.json` additionally refines the first segment of each path with512 cells maximum/four levels:7 converged,21 incomplete,4348 cells,9.45 seconds. These representative refinements do not establish whole-path support. Empirical area/contiguous-width thresholds remain unconfigured and this diagnostic is not an added gate; centerline certification must not be relabeled full-footprint or physical support.


### Completed exact same-path top-boundary classification (latest phase)

The complete 186,743 causal own-path pair inventory for proposal v5 has 180,348 strict top-flat XY AABB separations. Its remaining 6,395 pairs are now closed: **5,067 exact touch witnesses, 1,328 strict projection separations, zero incomplete**. The bounded research command `.venv\Scripts\python.exe artifacts/print-source-inspection/research_classify_ownpath_boundary.py` exited 0 in 5.797 seconds, with 5,067 public exact-top point queries and 1,388 public bead-projection queries (limits 90 seconds / 150,000 queries / 4,096 coordinate bits / 128 sqrt fraction bits).

Evidence is `whole28-ownpath-top-boundary-exact-classification.json` and its new paired `...-provenance.json` in `artifacts/print-source-inspection/`. Every pair retains emitted path ID, current motion segment and earlier completed segment indices; touch records include exact rational motion parameter, tip position, material XY, squared distance and equal exact top bounds. Separation records retain rational axis and positive outward-bounded projection margin. The source is the finite axial stadium model, using E5-implied segment widths; no invented endcaps, epsilon, or zero-height material bead. This supersedes the earlier pending 6,395-pair status.

These witnesses prove existence of boundary contact, not whole swept-disc containment in an authorized contact region. The zero-height provisional diameter-0.4-mm tip is at its own previously printed material top plane, so there is no strict own-bead interior penetration; however the compiler/auditor must still bind witnessed causal pairs (including nonadjacent local trail and closed seam) to its explicit declared contact policy. No blanket same-path exemption follows. Source handoff contacts remain separately pinned to actual cropped source material. Full-footprint support remains the previously reported bounded incomplete diagnostic with empirical thresholds unconfigured; this phase does not promote it to a pass. Opaque source startup/final suffix and measured whole-head clearance remain outside nominal typed-body/disc analysis. No physical-print authorization is asserted.


### Fresh actual emitted whole-job geometry evidence (latest phase)

The actual output `artifacts/conditional-whole-job-review/whole-job.UNVERIFIED_VIEW_ONLY.gcode`, SHA256 `5200cc727e0c534913044f415894fc7470cd4b5f9a55ee3435a879acfe3a619d`, was independently reconstructed per insertion block with the existing strict modal trace from the actual source-bound anchor state. All 28 emitted HEIGHT markers exactly bind physical heights; all 2,853 actual positive-XY deposited E commands independently recover actual widths using the existing filament/flow/bead-width owner arithmetic. Actual XYZ and E-derived widths exactly match the immutable frozen emission reference; stored manifest E was not used to derive widths. The current public source-bound model was rebuilt from f917 source/project and retains all 21 known debt crops under the declared linear-E/affine-XYZ deposition premise.

Fresh continuous exact-span contact succeeds for **all 28 paths / 2,853 emitted segments**, with **4,231 kernel queries** and complete leaf parameter partitions. This is centerline-bottom contact, not full footprint coverage. All **28 finite-clipped radial rectangle spill bounds are complete**, maximum upper bound **0.4970942052552083 < 0.5**. All **3,881,635 distinct candidate-path bead pairs** strictly separate: 3,282,529 by whole Z intervals, 598,982 by outward exact radial footprint bounds, and 124 by outward rational integer AABBs. Same-path joins are separately governed by causal boundary-touch policy, not this interpath test.

Every chronological candidate versus subsequent original model-material pair was accounted: **21,396,718 pairs = 19,296,157 strict Z separations + 2,092,215 outward AABB separations + 8,346 fresh public exact-projection certificates**, **zero unresolved**. These future-source avoidance checks intentionally use uncropped original source beads as a conservative superset; contact uses cropped material. Actual nonradial near pairs are included, not assumed away by tip height or ideal circles. The base research run reached its explicit 300-second budget with 4,594 near pairs pending (303.25 seconds including accounting); its summary remains unchanged. A separate bounded continuation queried ONLY those explicit pairs, proving all 4,594 in 13.766 seconds / 50,408 fresh public projection queries, zero intrinsic or budget unknown. Total projection queries across proof sets: 89,175. An initial diagnostic reconstruction failed an exact parity assertion because it multiplied binary64 filament area in a different order; the rerun uses the same authoritative operation ordering, and the initial empty evidence directory is preserved. The continuation first failed a research dictionary field lookup (`kind` versus `source_kind`) before geometric queries; corrected research script then completed successfully. No reusable tool/test was edited.

The new identity-bearing merged receipt is `artifacts/conditional-whole-job-review/actual-geometry-research-v2/merged-explicit-proofsets.UNVERIFIED.json`; it pins the actual output, source/project, compact compiler receipt, driver/owner identities and individual detailed proof-set files. It verifies exact unique pair-ID set equality between all 4,594 original budget-unknown pairs and continuation certificates. Original v2 budget-incomplete receipt and all completed certificates are preserved. This supersedes proposal-only geometry evidence for the same actual bytes, without transferring whole-tool authority: provisional planar-tip full chronology, declared causal contact-region policy, incomplete footprint diagnostics and opaque startup/suffix remain separately scoped. No physical printing or verified head certificate is asserted.


### AG-1 stationary-material scope correction and isolated exact-debt experiment

The previous 14,985 moving-bead geometry reports do **not** cover all material in the original f917 typed body. Independent AG-1 correctly identified 27 positive deposited E-only stationary events; no stationary bead geometry was represented. Prior contact/spill/moving-bead separation evidence remains within its stated moving-bead scope, but must not be called complete original-material separation.

All 106 positive stationary body commands are identically `G1 E.8 F1800`, with no XYZ command words, one explicit object token and known relative linear-E/debt state. Saved ordinary retraction length is 0.8 mm, ordinary restart-extra is zero and filament restart-extra inherits (`nil`); toolchange restart-extra is also zero and firmware retraction is disabled. For every one of the 106 events, the exact sum of the preceding emitted negative E retraction/wipe chain equals its known prior debt. There are 58 debts exactly 0.8, 21 at 0.80001, 26 at 0.79999 and one at 0.79998 mm. The concrete cause is mismatch between the sum of emitted rounded retraction/wipe E terms and a fixed ordinary 0.8-mm restore. Saved zero restart-extra and the uniform ordinary restore pattern provide evidence against interpreting the surplus as deliberate extra-prime. This does not establish matched producer-binary internal rounding code or actual physical debt.

One parent-authorized isolated artifacts-only derivative replaces ONLY the 48 mismatching E-only command tokens by exact known prior debt (five decimal places); the other 58 commands and all other source lines remain byte-identical. The new separate source is `artifacts/exact-debt-unretract-normalization-research/source.exact-debt.UNVERIFIED.gcode`, SHA256 `2aa69c3ebabc86442456486ee616d3caac2e30850142e670cd8d77937779f374`. The cloned embedded project is `project.exact-debt.UNVERIFIED.3mf`, SHA256 `757b8826ff902f29e1bedfdf9c425cc07b4b31202e87d5c94d19527f049a42b4`. Every ZIP member's uncompressed bytes are unchanged except `Metadata/plate_1.gcode`, which exactly equals the separate derived source. Machine/process settings, templates, model, all original moving commands, prefix and suffix are preserved. Original f917 source/project remain untouched. This is explicitly a source command normalization experiment, not a new Orca reslice or unchanged slicer output.

Public source-bound typed reconstruction on the new inputs finds **zero stationary surplus and zero moving debt crops**, versus 27 stationary surpluses and 21 moving crops in the original. All **14,985 ordered original moving XYZ/raw E/annotation width/annotation height/F tuples are exactly invariant**, semantic SHA256 `b008dd9d1af66e41f612e7191ec7ed4662c6a5a8d4bd816fdcb8360ec8637ef4`. This hash uses this experiment's declared tuple serialization; it should not be compared as identical to differently serialized earlier hashes. The new moving deposited amounts include the former 21 missing 0.00001-mm pieces, while stationary surplus total 0.00028 mm of filament is removed. Net commanded E change is exactly −0.00007 mm. No body G92 exists, so the logical-E accumulator changes cumulatively; the receipt records every differing logical-E/debt event and both final states. XYZ/F/modes and all other interpreted state components are unchanged. Retained header summary estimates are not recomputed and are not claimed exact for the derivative.

Command: `.venv\Scripts\python.exe artifacts/print-source-inspection/research_exact_debt_unretract.py`, exit 0, 16.625 seconds. Full identity-bearing evidence: `artifacts/exact-debt-unretract-normalization-research/normalization-experiment.UNVERIFIED.json`, including all 48 changed lines, all 106 exact negative chains, ZIP member hashes, new descriptor/entry/motion inputs and complete logical-E/debt differences. No reusable tool/test or production source changed. Reusable normalization requires separate specification adjudication and review; old source/project associations and geometry/tool proofs do not automatically transfer. Opaque startup/suffix, actual firmware/material dynamics and physical authorization remain outside this bounded nominal experiment.

Additional exact ledger inspection: old final logical E is 503.17853 mm and derived final logical E is 503.17846 mm; both final retraction debts are 0.79999 mm from the unchanged final retraction. No prefix/body G92 command occurs. The preserved opaque suffix contains original line 20806 `G92 E0 ; zero the extruder`, which resets logical E under the declared semantics and does not reset physical debt. This observation does not interpret the surrounding opaque shutdown effects. Experiment receipt SHA256: `4c388c6457f14dfa449291db0fc94f3e2c9c3272dbdc7823294d0d6c3c9064c8`.


### Corrected archive dependency supersedes initial experiment clone

Repository review found that the initial derived 3MF (SHA757b8826...) retained stale original `Metadata/plate_1.gcode.md5`; that archive is INVALID as a ready derived baseline. The separate normalized source2aa69c... and its moving/debt analysis remain unchanged. The amended specification permits the validated exact uppercase32-byte MD5 sibling to change alongside embedded G-code and explicitly enumerated stdlib flag serialization differences only. New corrected project `project.exact-debt.md5-corrected.UNVERIFIED.3mf` SHA256 `ea5639da549ddc8d4f49029b46561164c4edfa292885cb5e05c4753903a4c1c0`, with receipt SHA256 `ea5ca2be379dc8e469c987067514f224b383c80b35ac78ee9e5fc6b09742f1c4`, validates new checksum E7E38E7516532730CCB32CE9CDE86424, all member contents/metadata exceptions and fresh typed profile/body association. Original and invalid clone remain preserved. Full repository-review disposition and acceptance bounds are in `docs/implementation/exact-debt-source-derivation-repository-review-2026-10-18.md`: validated after parent checksum/ZIP adjudication; no production implementation changes in this research/review pass.
