# Print-source inspection implementation task

## Specification and repository review

- Contract: `docs/specs/print-source-inspection.md`.
- Canonical basis: `docs/SPECIFICATION.md` sections 22–29, 32.
- User authorization: implement printing; derive hardware/process inputs from
  the saved slice settings (2026-10-18).
- Disposition: **validated for read-only source inspection only**.
- Reviewed actual source: `orca_plugin/__init__.py`, research builders,
  `adaptive_subedge/engine/flow_model.py`, working-file port and plan DTOs.
- No existing executable G-code parser/injector was found. The research viewer
  sorts original extrusion segments by Z and cannot preserve print execution.
- Current revolution study worsens sampled mesh error in six of eight angle
  bins. Whole-path support, nozzle-body clearance, downstream collision,
  hardware motion-time validation and executable Plan publication are absent.
  Promotion of the research algorithm to executable output is **blocked** on
  those existing acceptance contracts; user visual acceptance is not a waiver.

## Implementation scope

Add an immutable sliced-profile adapter and strict read-only linear execution
reader under `orca_plugin/gcode/`, plus JSON inspection CLI and meaningful
failure tests. No file mutation, printer connection, injection switch, fabricated
validation certificate or new hardware constants. Required values come from the
sliced project and are associated with exact embedded source G-code.

The first architecture run exposed two tests that encoded the old Phase-0.5
directory ban, rather than distinguishing read-only source inspection from an
executor. For this later authorized prerequisite, replace that directory ban
with a closed three-file allowlist plus dependency/I/O and unregistered-entrypoint
checks. Phase-0.5 DTO ownership and all physical-enablement gates stay intact.
This is an explicit milestone-scope update, not acceptance of any executable
injection implementation. Do not add an executor to this whitelist.

## Verification plan

Python syntax/import; architecture suite; focused profile/parser tests;
inspection of actual pinned revolution fixture; full unittest discovery;
diff check. Lint/type tooling remains unconfigured. Physical enablement and
release require the separate normal and independent blind reviews in
`docs/REVIEW_PROCESS.md`; neither is represented as completed by this task.

## Results

- `source_profile.py`: frozen resolved settings with exact numeric parsing,
  source-key provenance, filament override precedence, selected CONFIG_BLOCK
  agreement, input hashes and byte-exact embedded plate association.
- `linear_trace.py`: immutable command-prefix trace with raw byte offsets,
  modal XYZ/feed, distinct logical E and physical retraction debt. G92 does not
  erase debt. Unknown units, unsupported commands, origin remaps, duplicate
  words and control characters reject instead of continuing a guessed trace.
- `tools.inspect_print_source`: stdout JSON only; no output G-code and no
  printer/export hook. Inspection returns exit 2 for unresolved requirements.
- The actual pinned revolution project resolved Bambu Lab A1 mini, 0.4-mm
  nozzle, PLA, 0.20-mm layer height, filament ratio 0.98, maximum volume flow
  21 mm3/s, retraction 0.8 mm at 30 mm/s and Z hop 0.4 mm. These are saved
  settings, not verified hardware measurements. Travel-Z speed remains the
  exported sentinel 0, not a usable zero-time motion parameter.
- The embedded/source G-code bytes agree. Original project/source hashes
  remain unchanged (`source-preservation.json`). Source SHA256:
  `8d7b530bc351826f496182c6c080c5f8f379e0eb22f01e7ccea4a26966811b95`;
  project SHA256:
  `0f4d85b55a2c3e1f579cc013d722f755a657f17dadb840d8a020792099aa3d61`.
- The strict interpreter stops at **line 760, M73**, byte offset 24611. It
  interprets zero commands of this real source; do not claim a full-file modal
  trace. M624/M625/M981 and thermal/fan/acceleration commands also require
  reviewed firmware-specific handlers. The full opcode histogram is evidence
  only and does not stand in for an interpreter.
- The actual exporter repeats unconsumed wipe_tower_x/y configuration keys.
  Those duplicates are reported unresolved; no last-value-wins acceptance was
  added. Duplicating a consumed key rejects even when values are equal.
- The fixture builder deliberately sanitized machine/filament custom G-code.
  A saved printer name is not evidence that this is a physically ready startup
  or shutdown program. Do not print this research source or its preview.

## Checks and review

Python 3.12.10 syntax/import: PASS. Focused tests: 18 PASS. Architecture: 45
PASS. Full final-code regression: **754 tests PASS in 174.634 seconds**.
`git diff --check`: PASS (existing LF/CRLF conversion notices only).
Lint/type tooling: NOT CONFIGURED (no project configuration found).
Logs are in
`artifacts/print-source-inspection/`; inspection exit 2 is an expected blocked
result, not a successful printable validation.

Primary source review found and fixed two unit/state ambiguities: E values
cannot be called filament length with unknown volumetric mode, and an earlier
M83 assertion must not be assumed to survive G90. Both now reject uncertain
interpretation and have regression tests. Retraction reset, exact decimal
arithmetic, malformed input, source/project mismatch and unsupported-command
prefix behavior were also reviewed and tested.

No physical enablement, production/release convergence or independent blind
approval is claimed. That review gate remains outstanding for any future
executable-output implementation. `log_iotc.txt` remains untouched and
unstaged. No printer connection, print, commit, push, merge or release.

## Next unresolved implementation gate

Resolve the actual mesh/triangle vertical alignment and run the existing
directional-error acceptance contract; construct chronologically supported
immutable Plans; review the exact firmware command family and hardware
envelope; implement and verify quantized insertion, saved-state restoration
and every affected downstream motion. A successful read-only inspection
cannot authorize any of those steps by itself.
