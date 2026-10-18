# Saved machine-program restoration and offline baseline

Contract: `docs/specs/restore-saved-print-profile.md`; parent disposition in
`print-development-loop-2026-10-18.md`: validated for separate profile restoration
and offline baseline slicing. Geometry quality improvement remains deferred.

## Changes

- `tools/restore_saved_print_profile.py`: pure-bytes pinned project restoration,
  duplicate/malformed/sliced input rejection, exact saved `*_gcode` value/type
  transfer, non-settings member preservation, non-program settings preservation,
  aliased-output rejection and a fixed-output offline research runner. It rejects
  external postprocess hooks, verifies executable hash, creates an isolated
  datadir and records exact arguments, logs, hashes and decimal opcode inventory.
- `tests/unit/test_restore_saved_print_profile.py`: 9 tests cover exact JSON
  transfer including the non-template emit-machine-limits key and integer JSON
  values, geometry/settings preservation, stale pins, malformed/duplicate/sliced
  archives on both inputs, external hooks, changed-key hashes, output aliases,
  unchanged receipts and decimal manufacturer command tokens.

No production parser, gate, hook, original fixture, source or current preview
was edited. No dependencies added. Restored programs come only from the pinned
saved seed, never installed presets or invented startup/shutdown templates.
All seed/model program-key sets must agree; unknown association fails closed.
Existing output folder rejects rather than overwriting prior evidence.

## Actual baseline

Executed `& .\.venv\Scripts\python.exe -m tools.restore_saved_print_profile`
with exit 0. Its exact offline Orca command, working folder and preservation
hashes are retained in
`artifacts/revolved-exponential-execution/restoration-receipt.json`.
Only the new `artifacts/revolved-exponential-execution/` folder was written.
CLI uses `--slice 0 --orient 0 --arrange 0 --export-3mf sliced.3mf`, isolated
`--datadir`, explicit `--outputdir`; no send/connect operation.

Input pins verified before use:

- Model: `b22af0e25a9e29a95e7a3c0f6aa93cf058d5119fa456205c05d62d3c1f89295f`.
- Saved seed (`MODEL_SHA256` imported from `tools.exponential_top_fixture`):
  `6b17c12a81ea54a0bfb8545713c2119e7d6604b6ee9abfbbdc23b73e883eebc4`.
- Executable: `480b64a3a5e95e3b43ed5ff93f7490af4e57f4e3cf6f19d8c9a4e4b2c9906aba`.
- Actual generated header: `OrcaSlicer 2.5.0-dev`.

All 17 saved suffix-matching keys restored; 9 changed:
change-filament, emit-machine-limits, filament-end/start, layer-change,
machine-end/pause/start and time-lapse G-code. Receipt records each exact key and
canonical JSON old/new SHA256 without duplicating full program text.
The earlier report of 18 keys was a reporting count error; the original seed
and receipt both contain 17. No receipt or restored data was changed for this
correction.
`enable_arc_fitting='0'` and all non-program settings remain unchanged.

Outputs:

- `restored-unsliced.3mf`: separate restored project.
- `original-slice/plate_1.gcode`: baseline SHA256
  `8bd04a71933ddef80372014d8bec8d9fe71674a416f1e8efdd1e53c0816726f3`.
- `original-slice/sliced.3mf`: SHA256
  `6355256385beac751ac3659463bf109e3cee9dadada1b5bad51b62b917e51050`.
- Embedded/separate G-code are byte-identical. All pinned inputs, prior source
  G-code/3MF, current review manifest and existing preview G-code hashes match
  before/after. Non-settings original ZIP member contents remain identical.
- Stdout/stderr retained (both empty); Orca also generated `00000.log`.
- Inventory contains 66 exact opcode tokens, including decimal manufacturer
  subcommands, and zero unrecognized lexical command lines. This is not semantic
  interpretation. G2 remains in saved startup programs despite arc fitting off.

The first receipt inventory grouped decimal subcommands as UNRECOGNIZED. This
lexical reporting defect was corrected and unit-tested; the saved receipt was
regenerated from the same unchanged baseline without reslicing.

## Verification

Required interpreter: `C:\VSC\Smoothificator\.venv\Scripts\python.exe`,
Python 3.12.10. Final checks all exit 0:

1. `& .\.venv\Scripts\python.exe -m py_compile tools/restore_saved_print_profile.py tests/unit/test_restore_saved_print_profile.py`
   -> PASS.
2. `& .\.venv\Scripts\python.exe -m unittest discover -s tests/architecture -q`
   -> PASS, 45 tests.
3. `& .\.venv\Scripts\python.exe -m unittest tests.unit.test_restore_saved_print_profile tests.unit.test_supplemental_copy tests.unit.test_supplemental_z_hop tests.unit.test_print_source_inspection -q`
   -> PASS, 51 tests.

Parent owns the final combined full regression. No dependency/type/lint tool
added; no package build or physical test performed.

## Review status and limits

Independent review BR-1 identified accepted JSON fractional numbers being rounded
or underflowed through binary64 parsing. Confirmed and fixed with standard-library
`Decimal` parsing and deterministic exact JSON numeric serialization; no dependency
or grammar narrowing. Regression cases cover `0.123456789012345678901` and `1e-400`
in copied numeric program values, their changed-key hashes, and untouched numeric
settings. Required Python3.12 syntax and focused restoration tests (10) passed.
In-memory restoration of the actual pins still reproduces the original
`restored-unsliced.3mf` byte-for-byte, SHA256
`d9ed61e14793a06256ae947d713c3d14b82aea84057ceb02947468d055bdf31d`.
No existing baseline, receipt or slicing output was rewritten for this fix.
Independent follow-up disposition is pending parent review.

Independent follow-up accepted BR-1 and identified LOW BR-2: integral exponent
tokens such as `1e0` could serialize as integer-category JSON. Fixed by requiring
every serialized Decimal token to retain a decimal point or exponent, appending
`.0` when necessary. Regressions cover copied and untouched `1e0`, `-12e0`,
`0e0` and signed `-0e0`, asserting Decimal category, exact value and sign.
Required Python3.12 syntax and focused restoration tests (11) passed, exit 0;
the in-memory exact-pin restoration still matches the unchanged stored bytes
and SHA256 `d9ed61e14793a06256ae947d713c3d14b82aea84057ceb02947468d055bdf31d`.
No receipt or artifact changed. Ring-intent source/tests were held unchanged.

Ready for parent and independent review. Manufacturer command expansion is now
visible, including firmware conditionals, homing, offsets, arcs and tool changes;
none is newly accepted by the strict parser. Execution/support/clearance and
physical-print authority remain false in every receipt. No printer connected or
printing performed. Removing this tools-only utility does not change production
behavior or original artifacts. No commit, push, merge or release performed.
