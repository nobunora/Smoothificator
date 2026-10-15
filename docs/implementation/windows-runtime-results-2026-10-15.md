# Windows implementation and runtime results

Overall: **INCONCLUSIVE — diagnostic source/build/CI PASS, real plugin load and
callbacks NOT VERIFIED. No usable analysis-plugin or Release claim.**

## Repository and environment

- Implementation source commit: `f95125798caebc7e8319d2529bf60132d3e2d3b2`.
- Branch: `codex/windows-runtime-validation`, based on PR #2 HEAD
  `01cc65a632f5b14755a5d90f0b54771e8e45cb86`.
- PR #5 was refreshed during execution to
  `6b1f04ea29b6c29413b04f4e5b6e57c439d1601c`. Schema/policy owner approval is
  recorded there; independent review, manifest/handoff and SPEC_VALIDATED remain
  incomplete. This work does not alter its decisions or merge either PR.
- Windows 10 Pro x64, 10.0.19045; PowerShell 7.6.6; Git 2.53.0.windows.2.
- Elevated shell; normal UAC is the elevation route, never disabled.
- C: free space at initial inventory: 423,380,930,560 bytes.
- Existing Python 3.12.10 reused to create `.venv`; existing global Python 3.14.7
  and other installations preserved. GitHub authentication already available.
- Official portable Orca nightly installed under ignored `artifacts/runtime`.
  No system-wide installer or new Python/NumPy dependency was required.

## Checks actually performed

Commands below ran through `.venv/Scripts/python.exe` on Windows:

| Check | Result |
| --- | --- |
| isolated prefix and package imports | PASS |
| `-m compileall -q adaptive_subedge orca_plugin tests` at base | PASS |
| `-m unittest discover -s tests/architecture -p 'test_*.py' -v` | 41 PASS |
| full suite at original implementation HEAD | 254 PASS |
| compileall including `diagnostics tools tests` | PASS |
| `-m unittest tests.unit.test_readonly_probe -v` | 12 PASS (mock API only) |
| `-m unittest discover -s tests -p 'test_*.py' -v` after implementation | 266 PASS |
| `tools/build_validation_artifacts.py` | PASS: ZIP CRC, source comparison, fresh `-I` extracted imports |
| `tools/generate_probe_fixture.py` | PASS: synthetic closed 10 x 10 x 2 mm STL |
| `git diff --check` | PASS |
| lint/type analyzers | NOT CONFIGURED under Phase 0.5 contract |
| real Plugin Manager registration / enable-disable / Script callback | NOT VERIFIED |
| real slicing/postprocess callback / offline slice | NOT VERIFIED |
| real G-code before/after SHA-256 | NOT VERIFIED; synthetic mock preservation only |

Windows CI [run 38753110917](https://github.com/nobunora/Smoothificator/actions/runs/38753110917)
completed successfully with **headSha exactly equal to source commit
f95125798caebc7e8319d2529bf60132d3e2d3b2**. It runs Python 3.12.10, architecture,
all 266 tests, artifact build and clean extracted imports. The artifact was
downloaded locally. This runner does not install Orca; CI is not runtime proof.

## Official Orca provenance

Official release URLs:

- https://github.com/OrcaSlicer/OrcaSlicer/releases/tag/v2.4.2
- https://github.com/OrcaSlicer/OrcaSlicer/releases/tag/nightly-builds

| Item | Evidence |
| --- | --- |
| stable x64 portable ZIP | SHA-256 `feba3009dfb9d268779cca5758a1a5bc3b7d0722bf8fa48d5c57340de975d6be`, matching GitHub asset digest |
| nightly x64 portable ZIP | SHA-256 `b7a77d21090ce4a61daeb27a526c41e3364401399ce143d7e6b8c4bb1f278133`, matching GitHub asset digest |
| nightly tag source | `86905a8a20d5887f3b13017e66cd897766334bd3` |
| nightly executable SHA-256 | `480b64a3a5e95e3b43ed5ff93f7490af4e57f4e3cf6f19d8c9a4e4b2c9906aba` |
| executable signature | NotSigned; verified official distribution digest, no security warning bypass |
| PE file/product version | empty; not inferred from the directory name |
| actual startup log version | `2.5.0-dev build 86905a8a` |
| bundled external interpreter check | Python 3.12.13; NumPy absent (not an in-process plugin import test) |
| isolated profile | explicit `--datadir artifacts/orca-profile`; user completed first-run wizard |

Stable v2.4.2 source lacks the Python SlicingPipeline seam; it is NOT SUPPORTED.
Nightly has the source-verified seam and `.py`/`.whl` loader; actual capability
load remains UNKNOWN. The old audited source is not treated as the installed build.
An initial `--help` process terminated with Windows event 1000 / c0000409;
the later isolated normal GUI launch succeeded. CLI support is not certified.

## Built artifacts (source f951257)

| Artifact | SHA-256 |
| --- | --- |
| local `dist/phase05-research-only.zip` (18,974 bytes) | `3d37c304271a9abf22309d0162232a584a82f56033e5086ec09987673124bb42` |
| local diagnostic `.py` (6,031 bytes, LF) | `92b7d9944f7484399c447c85b4e77eb82e4033fa4f2a9b9578f25bf608bd6a85` |
| Windows CI diagnostic `.py` (6,187 bytes, CRLF) | `6529e30d98b9193785095ec45ae8062fdfc7798a4060996d58d32df1380571e6` |
| synthetic STL | `d785d15dba5e3675215abd4f98cb0c7d227e90caa1d1d424709eba8f11cf5b7a` |

The CI research ZIP matches the local ZIP. The diagnostic checkout line endings
explain its distinct hashes; each manifest records the actual distributed bytes.
Neither research ZIP is an installable plugin. The standalone `.py` has verified
package syntax but must not be called a successfully loaded plugin yet.

## GUI tool failure and attempted recovery

Computer Use 26.915.31945 with desktop package 26.915.4065.0:

- list_apps/list_windows and accessibility-only inspection work;
- capture fails with `SetIsBorderRequired ... 0x80004002`;
- indexed click fails with `element 19 has no cached bounds`;
- secondary action fails with `no cached secondary actions`;
- keyboard actions did not produce the expected observed Orca dialog;
- a fresh node session, reacquired target and activation did not repair capture;
- a diagnostic Notepad launch could not subsequently be targeted; no input
  success is claimed;
- winget alias is unavailable; invoking the installed package executable for a
  read-only update inventory returns Access denied. No package ACL was changed.

Microsoft documents IsBorderRequired as introduced in build 20348; this host is
19045: https://learn.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturesession.isborderrequired
Matching upstream report remains open:
https://github.com/openai/codex/issues/25178
This is an API compatibility failure, not evidence that antivirus/UAC must be
disabled. No security setting was changed. GUI tool recovery is **not complete**.

## Remaining gates and smallest next action

1. Restore supported Computer Use capture/input (vendor fix or compatible host),
   then use Plugin Manager to install the built diagnostic `.py` and execute
   `diagnostics/README.md`'s offline callback procedure. No plugin registration
   was left behind by this task; the isolated app/profile and artifacts remain.
2. Complete PR #5 independent specification review, canonical reconciliation,
   manifest/handoff and repository validation before v2 production code.
3. Complete real callback, cancellation/disable and file-invariance evidence,
   followed by implementation review before any analysis-plugin release claim.

No printer connection/upload/print was initiated by this task. No G-code mutation
was enabled. No files on non-C drives were deleted. No Release or merge performed.
CodebaseMemory was not used: bounded direct source/API routing was sufficient
under the target repository's rules; no daemon or registration was enabled.
