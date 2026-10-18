# Supplemental Z-hop implementation

Specification: `docs/specs/supplemental-z-hop-review.md`.
Repository disposition: validated for offline block composition and real-candidate
transition review. User explicitly defers quality-error improvement. No need to
ask for that decision again; physical clearance is not inferred from it.

Approved scope: `tools/supplemental_z_hop.py`, focused tests and review evidence.
Use existing frozen MachineState and flow arithmetic; do not register production
hooks or change the original source/profile. No real anchor is available from
the current strict source parser. Real candidates can therefore show explicit
inter-path travel proposals, while complete block restoration is verified with
synthetic modal fixtures. Physical-print and independent-review gates remain
outstanding; no independent approval is claimed.

Verification: syntax, architecture, focused motion/modal restoration tests,
current 30-ring fixture transition audit, full regression and diff check.

## Implemented behavior

`compose_retracted_cycle` generates explicit G1 Z / G1 XY / G1 Z moves for
supplemental paths. The entire path-to-path travel and return XY move take
place while retracted, at `max(saved_actual_z, target_upper_z)+z_hop`, rounded
up. Restoring actual saved Z deliberately does not force the nominal upper Z.
The emitted block restores logical E with G92 without erasing retraction debt,
and then restores saved F. It never edits the original source.

Paths are sorted by physical thickness only inside one original-layer batch.
Mixed-layer calls reject; no global thin-first reordering of original layers.
Height, width, 0..30% overlap, minimum remaining thickness, quantization,
saved-state representability and machine height are checked. The slice-derived
factory also rejects a bead-height bound over 90% of saved original layer height.

`source_profile.read_sliced_profile(include_motion_caps=True)` additionally
reads/compares the complete saved machine XYZ speed vectors. Conservative
minimum caps across exported modes are retained with source-key provenance.
Saved XY request is 700 mm/s; explicit supplemental XY is capped to 200 mm/s.
Saved Z request is 0; explicit vertical travel uses the inherited request capped
to saved machine Z maximum 30 mm/s. Retraction/deretraction remain 30 mm/s.
No printer constants were invented. The local `artifacts/orca-source/PrintConfig.cpp`
travel_speed_z definition documents the zero sentinel; this implementation
defines explicit supplemental feeds, not a certified firmware timing model.

## Actual 30-ring fixture

`python -m tools.review_supplemental_hops` produces JSON evidence for 30 paths,
12 original-layer batches and 18 inter-path bridges. It does not fabricate the
missing source insertion anchors. Every batch explicitly carries
`entry_exit_anchor_verified=false`; overall `printable_authorized=false`.

Example bridge (requires an already retracted state):

```gcode
G1 Z3.600 F1800.000
G1 X90.925 Y90.000 F12000.000
G1 Z3.080 F1800.000
```

Z hop setting is 0.4 mm **above the next original-layer plane** (or higher saved
actual Z), rather than merely adding 0.4 to each candidate top. Original slicer
travel/retraction behavior is preserved because original bytes are untouched.

Exact nominal height audit of the requested order: candidate tops are globally
nondecreasing across the 12 proposed batches. Maximum physical height is
0.18 mm; minimum gap below the next 0.20-mm source-layer tip plane is 0.02 mm.
This supports the user's height-order reasoning for the declared candidate
geometry. It is not an actual chronological source trace, support proof or a
whole-tool-body sweep certificate, especially during deposition/re-entry.

## Verification and review

- Python 3.12.10 syntax/import: PASS.
- Architecture: 45 tests PASS, including unchanged closed production-hook gates.
- Focused profile and hop tests: 33 PASS (15 new hop tests + 18 existing).
- Full final-code regression: **769 tests PASS in 152.856 seconds**, after the
  slice-height guard. The earlier run also passed (147.609 seconds).
- `git diff --check`: PASS; existing LF/CRLF notices only.
- Lint/type: NOT CONFIGURED.

Tests interpret generated blocks with the existing strict modal reader and
check all nonextruding XY moves are retracted at Zsafe, vertical moves preserve
XY, saved XYZ/logical E/debt/feed return exactly, emitted feed/E obey the nominal
volume cap, unsafe height overflow never clamps, bad/unknown state rejects,
minimum remaining height and overlap survive permitted quantization, and the
real-shape transition adapter never creates an entry anchor. Parser replay is
not firmware validation. Source review additionally checked round-up ceiling,
F mm/s-to-mm/min conversion, G92/debt separation and hash association.

Artifacts: `artifacts/supplemental-z-hop-review/{syntax,architecture,focused,
real-transitions,full-tests}.log`, `transition-review.json`,
`vertical-order-audit.json`, `source-preservation.json`.
`bridge-replay-audit.json` separately records replay of all 18 actual proposed
bridges: all XY travel at Zsafe and all Z changes vertical, using declared
nominal candidate coordinates without assuming physical retraction or a real
source insertion anchor.

Original source, sliced 3MF and candidate manifest are byte-identical before
and after this run. No real source insertion, printer connection, physical
print, commit, push, merge or release. `log_iotc.txt` remains untouched/unstaged.
Independent blind review and complete source/firmware/tool-clearance validation
remain outstanding before any physical use of these offline blocks. Current
limitation: formatting is an explicit research policy, not certified Orca
formatter equivalence, and some unrepresentable quantized intents reject.
