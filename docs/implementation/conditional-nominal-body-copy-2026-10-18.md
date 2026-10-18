# Conditional nominal body execution and copy

Implementation of parent-validated
`docs/specs/conditional-nominal-body-copy-review.md`, 2026-10-18.
This is a tools-only conditional experiment, not physical startup interpretation,
production anchor enablement, geometry acceptance or print authorization.

## Change and ownership

- `tools/conditional_nominal_body.py`: immutable producer/entry/motion contracts;
  exact pinned body interpretation with typed single-object scopes, acceleration,
  fan and producer notifications. Existing strict linear arithmetic owns XYZ/E/F,
  logical extrusion and ordinary retraction debt. Prefix/end stay opaque.
- `tools/conditional_nominal_copy.py`: fresh derived recipe associations,
  reconstructed conditional anchors, immutable cycle replay, exact original-byte
  reconstruction and atomic no-replace separate UNVERIFIED output.
- `tests/unit/test_conditional_nominal_copy.py`: synthetic malformed/stale/mode,
  unknown-debt, scope, cap, byte/state replay and writer cases.
- `tests/unit/test_conditional_nominal_actual.py`: complete actual typed body
  accounting and freshly associated65-edge sample against the derived baseline.
- `artifacts/conditional-nominal-body-review/reproduce.py`: repeatable concrete
  receipt generation, requiring new output path (rerun intentionally rejects an
  existing output rather than replacing it).

The strict whole-source tracer/synthetic compositor, geometry engine, factory,
source profiles, original source and printer runtime are unchanged. No command
override is introduced. The distinct conditional anchor cannot become a strict
synthetic anchor. All authority flags remain false.

Parent review corrections incorporated: known6000 entry acceleration is traced;
only anchors over the requested5000 cap reject. Saved external-wall speed and
ALL positive scoped outer-wall XY events at the original floor constrain speed,
independently of selected geometry witnesses. A slower omitted wall therefore
still caps the candidate; the selected witness list cannot hide it.

## Actual evidence

Source SHA256:
`f917caf88191253f22004d47545daa4e6f78f4b4132d61529101271e4d3ba288`.
Project SHA256:
`6fe38676704d886a0aa82b1179343629ff612ccb55e2ee534811d1011008e567`.
Producer SHA256:
`480b64a3a5e95e3b43ed5ff93f7490af4e57f4e3cf6f19d8c9a4e4b2c9906aba`.
The exact body is lines1246..20796, excluding M981 at20797.
All19551 lines are accounted:18073 G1,394 M204,31 M624,31 M625,
10 M106,76 M73,31 M991,905 comment/blank events.

The floor4.4 zero-offset sample is freshly reconstructed from actual saved width,
height, source XY and E-implied emission policy;65 source edges are uniquely
matched to this source. All relevant floor-wall F contributes to the source cap
`6319/60` mm/s. The conditional anchor at byte418990 is inside the next object
scope, with complete nominal retracted state and eligible inherited caps.
No old source acceptance, F equality or byte offsets are transferred.

New evidence under `artifacts/conditional-nominal-body-review/`:
`single-sample-copy.UNVERIFIED.txt`, `single-sample-receipt.UNVERIFIED.json`,
`body-events.UNVERIFIED.jsonl`. Output SHA256:
`887152ebd1a71aa6a7421edd9ae7d9f699c8280d3577be7a9731407fc60b813d`.
Deleting the recorded insertion span reconstructs all original source bytes;
prefix/end bytes, original XYZ/E/F and project bytes are retained exactly.
Each cycle independently replays to the exact nominal XYZ/F/E/debt/modes state.

The separately established branch-free baseline intentionally lost time-lapse
camera/head-wrap macros, retained manufacturer templates, and reslicing changed
model F. This task performs no additional reslice/removal. Startup completion,
frame/tool, relative-E semantics, startup physical retraction reference, live
overrides and non-cancellation remain explicit declared-unverified premises.
The single sample does not establish full-group contact/future-material/tool
validation or whole-job authorization.

## Checks

All checks used `.venv\Scripts\python.exe` (required Python3.12.10).

1. `.\.venv\Scripts\python.exe -m py_compile tools/conditional_nominal_body.py tools/conditional_nominal_copy.py tests/unit/test_conditional_nominal_copy.py tests/unit/test_conditional_nominal_actual.py artifacts/conditional-nominal-body-review/reproduce.py`
   PASS, exit0.
2. `.\.venv\Scripts\python.exe -m unittest discover -s tests/architecture -q`
   PASS,45 tests,4.277s, exit0.
3. `.\.venv\Scripts\python.exe -m unittest tests.unit.test_conditional_nominal_copy tests.unit.test_conditional_nominal_actual -q`
   PASS,12 tests,4.745s, exit0.
4. `.\.venv\Scripts\python.exe artifacts/conditional-nominal-body-review/reproduce.py`
   PASS, exit0, emitted the hashes/counts above. Atomic writer rebuilds the copy
   again from pinned originals and rejects stale/forged receipt bytes.
5. `.\.venv\Scripts\python.exe -m unittest tests.unit.test_conditional_nominal_copy tests.unit.test_conditional_nominal_actual tests.unit.test_supplemental_copy tests.unit.test_supplemental_z_hop -q`
   PASS,36 tests,5.834s, exit0 (including unchanged strict/synthetic paths).

Full suite deferred to parent after review convergence. Existing dirty/untracked
work and `log_iotc.txt` preserved. No dependencies, printer connection, print,
commit, push, merge or release. New modules/tests held stable for primary and
independent blind review. Rollback is removal of this separate tools-only flow
and new experiment artifacts; original inputs need no restoration.

## CBR-1 profile-policy association correction

Independent blind review and parent primary probes confirmed a Medium defect:
self-consistent refreezing/reassociation could replace saved filament diameter
or hop (and other saved fields) while retaining the same source identity.
Disposition: confirmed, fixed, pending independent follow-up verification.

The composer now derives canonical policy through current `read_sliced_profile`
and existing `policy_from_slice` using explicit plugin bounds/precision, before
accepting path associations or emitting any block. All source-owned hop,
printable height, XY/Z travel, retract/deretract rates, filament diameter,
volumetric cap, flow multipliers and other-flow flag must match exactly. Candidate
speed alone may be lower than canonical; it also remains constrained by all
source-floor external-wall moves. Plugin bounds retain the existing saved90%
maximum-height rule. No override contract or original parser changes.

Actual regression refreezes/reassociates each of12 source-owned substitutions,
including hop.001 and diameter2.85, and verifies rejection. A lower candidate
feed with otherwise canonical policy remains accepted. Synthetic fixtures now
derive policy from their actual saved settings. The earlier speed101 regression
now rejects at the stronger saved-policy check before the floor-feed check.

Corrected artifacts are separate under
`artifacts/conditional-nominal-body-review/profile-bound-v2/`; prior receipts and
output remain unchanged. Reproduction accepts explicit `--output-directory` and
still never replaces an existing copy. Corrected receipt explicitly records
`policy_bound_to_current_saved_profile=true`.

RequiredPython3.12 syntax passed. Focused synthetic+actual14 tests passed,
26.178s,exit0. Exact commands:

- `.\.venv\Scripts\python.exe -m py_compile tools/conditional_nominal_copy.py tests/unit/test_conditional_nominal_copy.py tests/unit/test_conditional_nominal_actual.py artifacts/conditional-nominal-body-review/reproduce.py`
- `.\.venv\Scripts\python.exe -m unittest tests.unit.test_conditional_nominal_copy tests.unit.test_conditional_nominal_actual -q`
- `.\.venv\Scripts\python.exe artifacts/conditional-nominal-body-review/reproduce.py --output-directory artifacts/conditional-nominal-body-review/profile-bound-v2`

Corrected reproduction PASS,exit0. Its output SHA256 remains
`887152ebd1a71aa6a7421edd9ae7d9f699c8280d3577be7a9731407fc60b813d`:
valid source-derived emission bytes did not change. Combined regression
`.\.venv\Scripts\python.exe -m unittest tests.unit.test_conditional_nominal_copy tests.unit.test_conditional_nominal_actual tests.unit.test_supplemental_copy tests.unit.test_supplemental_z_hop -q`
passed38 tests,31.546s,exit0. Files frozen again for independent fix verification.
Post-fix architecture discovery also passed45 tests,5.319s,exit0, using the
same architecture command recorded above.
