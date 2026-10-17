# Layered same-slice Orca Preview probe

Disposition: research viewer load PASS; visual Custom/slider acceptance
INCONCLUSIVE. This is not a printable Plan or safe G-code export.

The pinned offline OrcaSlicer 2.5.0-dev (`86905a8a`) sliced
`artifacts/fixtures/offline-coupon.3mf` with the isolated generic Marlin
profile. Source G-code SHA-256 was
`499ecc78586fea15694eea16a33bfebea761522aa0bf5eee9069e67c0ae1dd9e`
before and after the probe. Ignored research scripts
`artifacts/build_same_slice_overlay_demo.py` and
`artifacts/build_orca_layered_overlay_probe.py` read only that pinned input.
The latter generated a unique plugin-style `VIEW_ONLY.gcode` under
`artifacts/layered-viewer/` (SHA-256
`843e295ca339b30474671c638783e4fdfa07fd0dbb0dc4c9bbfb69e699d9b2d5`)
and a JSON provenance manifest. These ignored local artifacts are not
production plugin output or reviewable code in this PR.

The representation contains the 669 positive-extrusion baseline segments
from all 15 original layers, plus one `Custom` display segment on the
existing Z=0.6 mm layer. Each baseline segment maps to its original G-code
line number; the Custom segment records source lines 145 and 234. Its XY is
the midpoint of the corresponding adjacent-layer overhang segments. The
true 3D midpoint Z=0.5 mm is *projected* to Z=0.6 mm for this display and
must not be mistaken for a validated executable path. The manifest records
this difference, source hash, layer ordinals, source line IDs, nominal width,
and false support/printable flags. This mapping is a provenance starting
point for later G-code validation, not insertion authorization.

The viewer file contains only G21/G90/M83/G92 E0/G1 and comments, with no
temperature, homing, printer connection or original machine macros. Source
settings were filtered using the existing viewer configuration gate. A
dedicated Orca process with a separate data directory opened the file in
G-code-only mode. Orca's native log recorded successful config and G-code
parsing, `GCodeViewer::load_as_gcode`, and navigation to Preview. Windows
accessibility showed the export and slice controls disabled. No network TCP
connection was found for that process; no device action was requested.

Visual verification could not be completed: Windows Graphics Capture still
returned `SetIsBorderRequired / 0x80004002`, and element clicking returned
`coordinate input geometry is unavailable`. The profile's first launch also
reported a malformed copied configuration; Orca regenerated its isolated
profile, the notification was dismissed, and the G-code viewer loaded. The
user's ordinary Orca profile was untouched. Computer Use state was reset
after inspection; the dedicated viewer window remains open for manual review.

This proof is outside accepted ADR-0069's Custom-only plugin mode. Do not
promote it to the plugin or rely on the `.gcode` viewer file for printing.
Before product integration, adjudicate a new read-only baseline-overlay
contract with source-slice identity, true layer scheduling, bounded modal
parsing, display-only artifact lifecycle, and independent output gates. A
native in-memory Orca overlay would avoid a derivative G-code file, but the
full pinned source/build tree is not currently present on this PC.
