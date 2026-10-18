# Angle table / Custom / end-wipe trial parent audit

Status: implementation and actual-artifact verification in progress. No new job
has been sent. The user reports completion of the previous supplemented print;
this is physical completion evidence, not dimensional measurement.

The user approved a new experimental trial with width 0.21..0.45 mm, exposed
height >=0.08 mm, physical height strictly below saved layer height, overlap
0..30%, evaluation end exclusions 5 mm each, precomputed angle selection and
optional parameterized end retraction/wipe. Within-line curvature subdivision
is explicitly omitted. Same genuine GUI slice and placed model are retained.

Parent validated the tools-only amendment in angle-table-trial-review.md,
requiring a model-independent table rather than source-specific optimizer knots.
The finite family and angular boundary uncertainty must be disclosed. Actual
formatted contact, support, material, state restoration, and moving-tool checks
remain mandatory. No canonical runtime or whole-job physical proof is inferred.

With 30% overlap and exact 0.001 mm Z coordinates, nominal strict-H limit 0.199
mm yields effective legal physical lattice maximum 0.19 mm. This is disclosed
rather than silently rounding remaining height or changing overlap.

The new epsilon/minimum-path floor-union objective supersedes the old quality
comparison against a .25/.18 buried-overlap floor pack. Actual new quality must
be independently recomputed; old comparison is optional diagnostic only. No
contact, collision, flow or state gate is relaxed by this objective amendment.

Native end policy is opt-in: saved-profile trial 0.8 mm retraction, 30 mm/s,
0.5 mm reverse wipe, half stationary and half moving. All negative-E XY moves
must participate in tool auditing. Own-path TOP allowance requires a fresh
boundary-contact proof, constant prior top, the entire affine sweep at or above
that top, exact own identity and endpoints on the completed centerline. This
remains the explicitly provisional zero-height 0.4 mm planar-disc model.

Native `; FEATURE: Custom` is supported by pinned Orca sources and official
Bambu Studio v02.08.02.61 sources. Role must be restored after each addition.
Consumer material/time statistics handle Custom specially and are not a new
estimation proof. Original plate/profile metadata is retained: no verified
semantic replacement for Textured Cool Plate has been established.

The Studio GUI had unrelated unsaved project/settings changes. Parent saved a
new copy without overwriting the original:
`artifacts/gui-angle0to30-trial-v3/studio-user-project-preserved.3mf`, SHA256
814a48f2dfea9e924b3d127cbaadb5ab17ffd3c8910da6c19f89b423904ab0d8.
This is preservation only, not the new slicing input.

Original source/geometry hashes rechecked unchanged: a6314651... raw G-code,
1d714338... sliced archive, 6812137d... geometry project. Unrelated log_iotc.txt
is untracked and untouched; beginning hash54df04a1... . No commit, reset, branch
switch, push, merge, release, printer start, or CodebaseMemory daemon occurred.

Independent reviewer identified AT-1 numeric type validation, AT-2 unbounded
height lattice construction, and AT-3 lookup dimension/binding validation;
owner correction and final independent replay are required before completion.

## Latest source and actual candidate review

AT-1..4 were corrected and independently rechecked. AT-5 identified that a
precomputed fallback may be outside the original epsilon band. Parent rejected
claiming that as epsilon-optimal: the artifact binder now validates all retained
finite alternatives and applies the epsilon/path/upper ranking to their actual
formatted, feasible errors. This is finite retained-family optimality only.
The final source-binding receipt must contain the feasible minimum, epsilon
limit, selected alternative, actual candidate count and pinned table bytes.

Native strict-height support required an additional opt-in bounds adapter:
the user-requested strict saved-H limit would otherwise still fail the legacy
90% validator. Parent approved only the native recipe flag; all other inherited
profile fields still use the unchanged legacy validator. The first full suite
was stopped after its source snapshot changed and is explicitly INCOMPLETE,
not a passing regression. Final full suite is final-tests-v2 under trial-v3.

## Requested cross-section explanation

Python/Matplotlib script and PNG/SVG are under
`artifacts/gui-angle0to30-trial-v3/render_contact_explanation.py` and
`contact-cross-section.*`. At X=80.5165,Y=81.013, the rejected v3 root has
bottomZ1.964 and the public all-source point upper bound is1.96187565782725;
therefore centerline gap>=0.00212434217mm in the nominal model. The plotted
1349 earlier finite flat-axial-cap bead sections independently reproduce the
upper value numerically (dominant source3970). The exact query receipt is the
proof; plotting samples are visual explanation only, not physical measurement.
The rectangle overlaps source on either side: this is not wholly floating
material. The user was explicitly told the centerline rule is stricter than
mere footprint overlap. Its relaxation is not silently inferred from a graph.

## User tolerance amendment and final regression

The user explicitly accepted nominal inconsistencies up to 0.08 mm. The v7
artifact binder applies this as a configurable root-support gap tolerance,
querying actual bottom minus 0.08 mm. Parent-child contact, physical dimensions,
overlap, future material, tool intrusion and state gates remain unchanged.
All 50 root receipts label this tolerance-qualified, not exact nominal contact.
The finite feasible-family ranking yields 26 groups / 63 paths (50 roots and
13 uppers). This increase from strict-v6 54 paths is caused by previously
excluded lower-error candidates entering the feasible 2-percent band.

Final frozen-source regression completed with Python 3.12.10:
`python -m unittest discover -s tests -v`, 987 tests PASS in 831.122 seconds.
Receipt: artifacts/gui-angle0to30-trial-v3/final-tests-v2/receipt.json.
Log SHA256: 901765471f7ef4b2d493aab62c83386b2c582cf0e4d42f56a1a259e954cb80eb.
Source/test snapshots and all preserved inputs including log_iotc.txt were
unchanged. This does not substitute for the actual v7 artifact audits.

The first v7 material audit could not separate table_g00_b005_u from original
segment 4061 using its coarse k/4 projection axes. Independent exact projection
on (0,1,-2/25), with outward 128-bit bounds, establishes strict separation with
positive margin 0.0005604402966013152 in projection units. This is a stronger
certificate, not a relaxed overlap threshold. Final full material/tool audits
remain required; the failed coarse-axis run is preserved as diagnostic evidence.

## Studio visual readback

Parent reopened installed Bambu Studio and loaded the immutable v7 sliced
archive through the file dialog. `studio-v7-preview.png` and
`studio-v7-current.png` under trial-v3 were captured with Pillow and viewed.
The legend includes green Custom and supplemental lines are visibly green in
the side view. The latter image includes user viewport interaction; no shape
or contact claim is inferred from the diamond-style rendering. The original
four compatibility substitutions are still reported by Studio. No reslice,
save, send or print was performed. The archive keeps all non-G-code/MD5 members
byte-identical; Studio's temporary UI conversion is not written to the file.

## User rejection and consumer regression (supersedes v7 visual acceptance)

The user correctly identified reversed-looking stacks and corrupted original
lines. The previous visual observation was insufficient: Custom was visible,
but source parser geometry was not preserved. Official Studio's unknown-Orca
producer path ignores forced height/width comments. Supplemental extrusion
changes its last-extruded-Z and therefore shrinks the inferred height of later
original lines (source layer 2.2 became 0.011 instead of 0.2 mm). The same issue
can render a nominal 0.34 mm supplemental line about 2 mm wide. See independent
research record angle-table-v7-preview-rejection-independent-research-2026-10-18.md.

Separately, the table's equal-width stack family did not express the user's
large-base/small-upper requirement. Revised topology-v2 yields 53 paths with
4 uppers, all actually narrower, contained and no taller after E quantization.

V8's first truthful Studio-dialect marker failed the REAL consumer. The producer
detector matches a substring, but Config.cpp requires a `; BambuStudio` prefix
before the original CONFIG_BLOCK_START. The marker inside the first supplemental
block satisfies neither the stricter prefix nor forward ordering. Reduced parser
tests were insufficient to catch this second reader contract. V8 is therefore
also not an accepted preview. Final-tests-v3 was stopped for this necessary
source correction and is INCOMPLETE, not a passing regression.

The user then explicitly requested merging the new table with the successfully
printed method. Independent comparison establishes identical original raw,
archive, producer, context and all 26 original post-hop anchors between that
successful trial-all26-posthop-v1 route and v8. Preserve this native copy/package
route; update only immutable table geometry and the approved end/preview options.
The reader adapter must be a truthful, tracked comment-only preamble before the
original config, with exact original recovery and independent reader validation.
Do not change or forge the original generated-by provenance. Physical commands
remain on the proven route, while display compatibility requires its own gate.

## Successful route fusion candidate v9

The corrected prefix is exactly 92 bytes at offset zero and is separately
tracked as adapter_prefix. Final candidate package SHA256:
bfbbb557e82fa66d37f3a6c390302925d1accee5b958d53f155a53d93874980f.
Raw SHA256: 996153fc9f2afe717c397dbc26504fbfe2c18b7b24f920494f498058e2857649.
Location: artifacts/gui-angle0to30-trial-v2/trial-angle-table-v9/.
successful-pipeline-fusion.UNVERIFIED.json verifies the old successful context
and all original post-hop anchors, exact original recovery after prefix/span
removal, and firmware-command equality with v8 (only adapter comments differ).
The original generated-by OrcaSlicer header is retained. The deliberate new
options are table geometry, configured end retract/wipe and Custom metadata.

Independent corrected-prefix focused review passed 42 tests; emitter's focused
set passed 35 and architecture checks passed 45. Final full source-frozen suite
is final-tests-v4 under trial-v3; v2's earlier 987-pass result is not a substitute
for this new revision. No test success is inferred while that suite is running.

The user physically stopped Computer Use with Escape while v8 failed. After
explicit permission to resume, even list_windows was rejected by the helper's
retained stopped state. No further UI input was attempted. Parent supplied the
concrete v9 link and requested manual Studio load/readback while software and
artifact checks continue. Actual v9 GUI acceptance remains open until evidence
arrives; the reduced consumer replay alone cannot establish it.

## Actual v9 readback and fresh causal audit

User manually loaded v9 and reported no error and broadly correct display,
then asked why steep-angle rows remain. Parent captured and viewed
trial-v3/studio-manual-readback.png: original orange layer thickness is uniform
again, Custom supplements are green, and the former inflated-width/flattened
original-line artifact is absent in this view. The live Studio extracted
Metadata/plate_1.gcode under its current bamboo_model temporary directory hashes
to 996153fc9f2afe717c397dbc26504fbfe2c18b7b24f920494f498058e2857649,
matching the exact v9 delivered raw file. This is actual consumer acceptance,
not inferred solely from the reduced parser.

Fresh v9 causal audit reports zero issues across 2748 motions and 1195419 pairs,
53 wipes, 53 forming checks and 1822 strictly separated native-arc pairs. No
adjacent-lane TOP exception was used. Independent replay checked 218 non-box
tool certificates and 24 material certificates. The 128 opaque-original-XYZ
obligations match the previous successful trial exactly and remain unresolved;
whole-job and physical proof flags remain false.

Current steep rows are intentional under the stated short-base rule. With
H=0.2 and minimum width0.21, Bmin=sqrt(2)*0.21=0.29698485mm and the straight
slope cutoff is atan(0.2/Bmin)=33.95770549degrees. The last three actual source
terraces have B=0.384/0.374/0.365mm, average angles27.512/28.136/28.720degrees,
and one root each of width0.251/0.249/0.248mm and physical height0.19mm
(remaining0.133mm at30percent overlap). Their presence is not a failure of the
skip rule. Final all-row table-to-output replay is recorded separately.

Independent raw-JSON/Fraction replay (no planner API or optimizer) subsequently
matched every width, height, Y/Z position and parent link in all 26 groups /
53 paths to the pinned generic table. Table SHA256:
d7d9f8214c6e36e9a2e8cdb94ea2eb1c27c32fb9d028f397e64d55e2616edfa9.
Plans SHA256: 09e5274971f42ec01b323d80227c56d47104fa5b84c19c07b8e7c60724fc61a9.
Receipt: trial-v3/independent-table-intent-replay.json; CSV and replay script
are alongside it. The last three rows use slope bins0.52/0.53/0.54, alternative0.
Even sqrt(2) times each selected actual E-width remains below its source base
(0.354964/0.352142/0.350726mm versus0.384/0.374/0.365mm). No hidden geometry
optimization or table bypass was required to reproduce those outputs.

## Final corrected-source regression

Final-tests-v4 completed PASS: Python3.12.10, 993 tests in451.236seconds,
exit0. Source/test hashes unchanged throughout and all preserved original
inputs plus unrelated log_iotc.txt unchanged. Receipt:
artifacts/gui-angle0to30-trial-v3/final-tests-v4/receipt.json.
Log SHA256: a91daca2a446bed92aeea986b994bb0c20fc5bfa38e5d5c1d7d33111ac38cc3b.
No new physical print was sent, no merge/release performed. V9 is the corrected
experimental preview/trial artifact; prior v7/v8 failed previews remain preserved
for diagnosis and must not be confused with the accepted v9 readback.
