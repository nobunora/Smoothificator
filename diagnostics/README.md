# Read-only Windows runtime probe

This separate PEP 723 `.py` package is **diagnostic tooling**, not the
Smoothificator geometry analyzer or an injector. No Plan is selected. Old Plans,
fingerprint comparisons, surface quality and printer safety are not certified.

Target: official OrcaSlicer nightly source
`86905a8a20d5887f3b13017e66cd897766334bd3`, reporting `2.5.0-dev` / `86905a8a`.
Stable 2.4.2 lacks this API. The nightly URL is mutable: always compare the
download to the recorded SHA-256 before use; never silently substitute a later
nightly. External venv Python is separate from Orca's embedded Python 3.12.13.
The probe uses standard library only. NumPy availability is reported, not required.

## Offline procedure

1. Launch the verified portable application with `--datadir` pointing at a new
   disposable profile. Do not sign in, install networking plugins or connect a printer.
2. In Plugins, install `smoothificator_readonly_probe.py` from this directory or
   `dist/`. This is the actual source-verified `.py` package format. Do not install
   `phase05-research-only.zip` in Orca.
3. Run **Smoothificator runtime diagnostics**. It shows version/build/Python and
   arms read-only observation only on the exact target. Each reload starts unarmed.
4. Slice a synthetic model with an offline profile. Export to a disposable local
   file. Never use Send/Print/Upload. The pipeline returns Skipped and reads the
   working G-code twice, bounded to 64 MiB. It never opens any file for writing.
5. Run runtime diagnostics again. Require `READ_ONLY_UNCHANGED`, equal SHA-256
   before/after and byte count. Record the final exported file hash separately;
   an application operation after the hook is not covered by its internal hashes.
6. Repeat export. Disable the pipeline capability in Plugin Manager and confirm
   no new observation occurs. Re-enable and confirm it occurs again. Configure
   `{"enabled":false}` to test the probe's own disabled path separately.
7. Disable both probe capabilities at completion. Keep the isolated profile for
   evidence. No personal Orca profile needs to be changed or restored.

The native Python stderr log and Script dialog contain sanitized diagnostics.
The history is bounded to 16 observations and is process-local. The read comparison
detects changed bytes/metadata; it is not an atomic writer or TOCTOU safety proof.
No UI runs on the slicing worker, and no live context escapes the callback.

## Repeatable local checks

Run from the repository in PowerShell, using an existing Python 3.12 installation:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m compileall -q adaptive_subedge orca_plugin diagnostics tools tests
.\.venv\Scripts\python -m unittest discover -s tests/architecture -p 'test_*.py' -v
.\.venv\Scripts\python -m unittest tests.unit.test_readonly_probe -v
.\.venv\Scripts\python -m unittest discover -s tests -p 'test_*.py' -v
.\.venv\Scripts\python tools/build_validation_artifacts.py
```

Check each command's exit code before advancing. Lint/type tools remain
NOT CONFIGURED under the Phase 0.5 quality contract. The Windows CI workflow
performs these checks, but **does not install Orca**. Mock tests are explicitly
separate from real callback evidence. Build output includes a hash manifest,
a non-installable research ZIP and the diagnostic `.py` file.
