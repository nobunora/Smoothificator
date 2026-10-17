# Native Custom band preview: implementation and runtime evidence

Disposition: bounded milestone PASS; printable plugin completion is NOT claimed.
Authority: Accepted ADR0069 / SPEC_VALIDATED orca-native-band-preview,
specification commits bbc5149 and 09181f1. Repository review validated the
exact geometry owner, pinned native parser and separate viewer-only boundary.

## Behavior

The separate preview wheel 0.2.1 accepts transverse span, minimum/maximum
width, nominal display height and trim. It chooses the fewest feasible equal
bands, rejecting infeasible widths and resource/cancellation failures without
partial geometry. Exact Fraction centers and widths partition the span; only
the common planar rectangle is certified by that research computation.
Original chord APIs are preserved. HTML now draws nominal footprint widths.

A copied, filtered Orca configuration supports a separate Custom-only viewer
file in host-provided plugin storage. Original G-code is neither read nor
modified. Commands are limited to G21/G90/M83/G92 E0/G1 and comments. Positive
E represents visualization only. No automatic launch, print, upload, slicing
hook or executable Plan authority is added. File paths are unique/exclusive;
cancellation/deadline checks extend through publication and discard stale files.

## Native acceptance

Dedicated portable Orca 2.5.0-dev, source/build
86905a8a20d5887f3b13017e66cd897766334bd3; Python 3.12.13 and NumPy 2.2.6.
Installed package was loaded through the native plugin manager. Final local
development refresh was performed while disabled, into the actual nested wheel
extraction directory; every extracted member was compared with the wheel bytes.
It was then reactivated and the Script capability executed normally.

Loaded existing offline-coupon.3mf, generated with:

- Z 1.522544393 mm; X running direction; transverse span
  87.4611717775 .. 92.5388282225 mm.
- Width limits 0.3 .. 0.6 mm, nominal display height 0.2 mm, trim 0.25 mm.
- Result complete/bands-proposed: 9 bands, exact-computation width approximately
  0.564184049444 mm; common running interval 85.25 .. 94.75 mm.
- A unique VIEW_ONLY.gcode appeared under the host plugin_data directory.
  Its 9 positive-E extrusion moves and BBL Custom/width/height tags were checked.
- Opened that file in a separate dedicated Orca process via its positional
  file argument. The native Preview tab rendered 9 nonzero-width green paths
  with the Japanese Custom legend (カスタム). The extrusion-width view displayed
  0.56 mm and layer-height view 0.20 mm, at the native legend's decimal precision.
  Left the native viewer open in Custom classification.

Local evidence (ignored artifacts; screenshots capture the target window only):

| Artifact | SHA256 |
| --- | --- |
| dist/smoothificator_preview-0.2.1-py3-none-any.whl | 974ae239ca8d0eb7110c25a16c3755c6dea0646ba510bbd3180e4a034dee5295 |
| artifacts/native-custom-preview.png | ae563fe71fc46f78f2a7e4db094c34ebc9d93a3843ccb31f9393a90a32c4eb2a |
| artifacts/native-width-preview.png | d1e4f7dc7502edc1a303d8a391da7c885d20950746a0d6acedc6d0bf0026ac6f |
| artifacts/native-height-preview.png | 4d8a6cf6266dccbfb526ebe46cecfe31950a07182fdc89065075678e6384a93f |

## Failures resolved and independent review

- Independent review found I/O excluded from cancellation/deadline handling.
  Shared final-publication checks now reject stale/expired work; regressions
  exercise deadline after rendering, cancellation during write and stale
  generation after write, including file cleanup.
- Runtime rejected valid uppercase Orca keys. Pinned PrintConfig source showed
  required_nozzle_HRC, machine_max_force_Y and machine_bed_mass_Y. ADR0069 was
  amended before allowing ASCII uppercase keys. Raw values are never logged;
  intentional error codes distinguish key type/duplicate/grammar problems.
- Existing wheel extraction is reused across reload/restart. Pinned
  PythonInterpreter.cpp:1105-1112 establishes the actual nested extraction
  location. New package version plus byte-verified disabled refresh removed
  stale-code ambiguity; no permissions were bypassed.
- Runtime storage() raised outside the capability context. Pinned
  PluginHostUi.cpp:91-106 only acquires the GIL for window message callbacks;
  PluginHost.cpp:22-24 requires current_plugin for storage(). Capture storage
  in Script.execute and reuse the copied path. Regression denies storage access
  in the subsequent window callback.

## Checks

Local Python 3.12.10. No new dependencies.

- `.venv/Scripts/python -m compileall -q adaptive_subedge smoothificator_preview tests tools`: PASS.
- `.venv/Scripts/python -m unittest discover -s tests/architecture -p 'test_*.py' -q`: 43 PASS.
- Nearest geometry, adapter, lifecycle and wheel tests: PASS; final full run below supersedes earlier counts.
- `.venv/Scripts/python -m unittest discover -s tests -p 'test_*.py' -q`: 566 PASS.
- `tools/check_canonical_manifest.py --handoff docs/specs/orca-native-band-preview.md`: 85 canonical blobs PASS after staging the new ADR.
- `tools/build_preview_plugin.py`: PASS, separate 0.2.1 wheel.
- `tools/build_validation_artifacts.py`: PASS, research ZIP remains non-installable.
- Lint/type analyzers: NOT CONFIGURED, not a passing static-analysis gate.

## Remaining boundaries

This is a convex-section equal-band research preview, not a residual-surface
optimizer. It does not determine calibrated printer width limits, prove bead
support/clearance, compute improvement, or validate a printable execution Plan.
The width/height defaults are explicitly research examples. Baseline sliced
paths are not overlaid. Native Custom-only layers show Z=0.00 in their layer
labels even though generated commands contain the requested Z; this is a pinned
native viewer limitation and must not be interpreted as certified coordinates.
The native rounded footprint is a display approximation of exact research bands.
Nonzero extruder offsets, unrepresentable widths, native width clamping and
unrepresentable Z=0 display are explicitly rejected.

No printer was connected or sent commands. No merge/release occurred. Temporary
UI controllers exit after each action; no screen-capture/control session remains.
