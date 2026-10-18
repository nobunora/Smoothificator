# Native trial Custom and end wipe

Bounded amendment/repository review: parent adjudicated `validated` for tools-only,
opt-in experimental native trial. Canonical runtime and legacy exact formatter
contracts remain unchanged. Existing native cycle replay is the authoritative
physical debt/XYZ/feed/mode restoration gate; frozen deposition E is unchanged.

`NativeSupplementEndPolicy` explicitly selects trial 0.8 mm end debt, 30 mm/s
retract/de-retract, 0.5 mm reverse wipe and half stationary/half moving retraction.
These are calibration parameters for this saved profile, not universal printer
defaults. Speeds must not exceed saved retraction limits. Coordinated feed is
floored and independently bounds XY and E speed. Wipe clips to the last deposited
axis-aligned segment; unsupported geometry and unrepresentable XYZ/E fail closed.
Source debt is reconciled at the raised ceiling before returning to source XYZ.
No end flow reduction or extra positive moving extrusion is introduced.

Optional annotation policy selects consumer `FEATURE: Custom`; exact prior
feature, height, width and Z metadata are restored. Custom consumer time,
filament and bounding-box statistics may exclude these moves. Package cached
estimates are preserved source estimates, not supplemented estimates. Actual
deposition is independently frozen and replay checked. Original plate/profile
metadata is preserved; compatibility dialog resolution must not invent a plate
alias or rewrite temperatures.

Files: `tools/native_supplement_end.py`, native copy/annotation opt-in fields,
`tests/unit/test_native_supplement_end.py`, distinct artifact builder
`artifacts/gui-angle0to30-trial-v2/build_angle_table_trial.py`.

Verification: `python -m unittest tests.unit.test_native_supplement_end
tests.unit.test_gui_native_trial_copy tests.unit.test_conditional_preview_annotations
tests.unit.test_gui_native_trial_package` exit 0, 29 tests. Includes debt differing
from source in both directions, exact source recovery, unchanged total deposition,
Custom restoration, clipped wipe, speed cap and precision rejection.

Remaining required gate: actual new artifact causal audit must include every
E-negative XY wipe as travel against completed current and prior material and
the moving tool envelope. Unit replay alone is not collision evidence. Independent
review requested. No GUI, printer transport or physical print is performed here.


## New artifact audit integration

Prior artifact scripts remain immutable. New builder/context/geometry/tool scripts
use the angle-table policy, Custom role and explicit end policy. Context replay
requires exactly one moving negative-E wipe per frozen path, no wipe deposition,
and independently verifies the formatted XY and E rates. Every wipe enters the
same chronological material sweep as all other G1 motions.

Parent validated the narrow own-material TOP amendment: only a fresh
`boundary-contact` certificate, a flat prior bead, affine move wholly at/above its
constant top, exact current/prior identity, and both XY endpoints on that closed
centerline may admit reverse wipe or vertical lift. The zero-height provisional
planar-disc premise is unchanged. Unknown or positive intrusion is rejected;
all other material remains audited. New table path IDs receive no inherited
adjacent-lane allowance from old trial IDs.

New geometry audit recomputes above-floor union error using emitted widths and
heights, compares actual formatted improvement to the stored fingerprinted table
policy, and preserves physical spill/contact/material checks. Parent adjudicated
that the old per-location optimum is no longer a hard gate for the newly approved
precomputed epsilon/minimum-path objective. No per-location optimality is claimed.


## Native strict saved-height amendment

Parent validated the user's new strict `< saved layer height` cap for the new
native trial only. `allow_strict_saved_layer_height` defaults false. When true,
the exact actual saved height must exceed the configured bound; every inherited
motion/flow/profile field is still checked by the unchanged legacy validator
through a bounds-only safe-height adapter. Legacy 90-percent validation remains
unchanged. The immutable emission-policy fingerprint includes this permission,
end policy and annotation policy. Tests cover .199 valid with saved .2, equality,
.201, default rejection and changed inherited XY cap rejection. Authoritative
`.venv/Scripts/python.exe -m unittest tests.unit.test_native_supplement_end
 tests.unit.test_gui_native_trial_copy tests.unit.test_conditional_preview_annotations
 tests.unit.test_gui_native_trial_package` passed 30 tests. Independent reviewer
reported no material finding for this adapter.
