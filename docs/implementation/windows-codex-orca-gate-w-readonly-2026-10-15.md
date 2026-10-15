# Windows Codex handoff — OrcaSlicer runtime and plugin Gate W (READ-ONLY)

Date: 2026-10-15  
Task type: **Windows-specific evidence collection / environment verification**, not plugin implementation or injection.  
Source repository: https://github.com/nobunora/Smoothificator  
Implementation branch: \`phase-0.5-skeleton-20261013\` (inspect latest HEAD before work).  
Unified design PR: https://github.com/nobunora/Smoothificator/pull/5 — Proposed, NOT Accepted.  
Safety classification: G-code mutation and physical printing are **FORBIDDEN** in this task.

## Instructions to Codex (copy as a single task)

You are running **on my Windows PC** and may inspect the local Windows/OrcaSlicer environment to provide an independently verifiable runtime evidence report for the Smoothificator project.

**Read first:**
- \`AGENTS.md\`
- \`docs/DOCUMENT_CONTRACT.md\`
- \`docs/PLUGIN_REQUIREMENTS.md\`
- \`docs/TEST_STRATEGY.md\` (Gate W, Gates X/Y)
- \`docs/implementation/phase05-release-readiness-2026-10-15.md\`
- \`docs/implementation/phase05-orca-postprocess-invocation-review-2026-10-14.md\` on the unified design PR #5.

**Constraints:**
1. This is **strictly read-only environment diagnostics**. Do not modify system settings, Windows registry, firewalls, routing, certificates, environment variables, repository files, Orca plugin directories or any installed OrcaSlicer files. No install/download/upgrade/build of Orca; no \`pip install\`; no auto-merges, tags, releases or pushes. Do not execute an unfamiliar plugin.
2. Never call slicer print, send-to-printer, G-code postprocess, upload or anything that could affect hardware. Do not open/edit/rewrite a user's G-code or a real customer/project file. No physical printer communication.
3. Do not dump \`.env\`, credentials, arbitrary logs, configuration containing access tokens, personal filenames or full environment variables. Redact usernames and absolute user-home portions of paths in shared reports; never upload raw proprietary profiles/G-code.
4. Use **short one-line read-only PowerShell 7 commands** with bounded output. Prefer \`Get-Command\`, \`Get-Item\`, \`Get-FileHash\`, \`Select-Object\`, \`Select-String\` and carefully scoped listing. Do not run long recursive folder traversals or mutate anything before separate authorization.
5. Source index/search is routing evidence only; material claims about Orca API must cite the inspected actual installed version/source/visible GUI observation. If unknown, report UNKNOWN/BLOCKED rather than assuming it matches a GitHub main commit.
6. This phase is a **reconnaissance prerequisite**, not a pass of an actual Orca plugin load. Current \`orca_plugin/__init__.py\` deliberately registers **no capabilities**, so the earlier Linux Python venv 254/254 tests **cannot** demonstrate Orca integration.

### Stage W0 — local host/runtime inventory (perform now)

A. Confirm exact git repository HEAD and tree status **without changing files**. Record PR #2 HEAD and compare it with the checked-out source. State if checkout is not the PR #2 branch and DO NOT switch branches without approval. Do not print secrets in git config.

B. Identify OS and installed OrcaSlicer executable using \`Get-Command OrcaSlicer.exe -ErrorAction SilentlyContinue | Select-Object Source,Version\` and a small number of **known installation folders only** if PATH lookup fails. You may query Windows "Uninstall" registry **read-only** for OrcaSlicer DisplayName/DisplayVersion/InstallLocation. Do not recursively scan the user profile or assume one universal install path.

C. For the *confirmed* exe path, record:
- executable product/file version from \`(Get-Item -LiteralPath 'EXE_PATH').VersionInfo | Select-Object ProductVersion,FileVersion,CompanyName\`;
- \`Get-FileHash -LiteralPath 'EXE_PATH' -Algorithm SHA256 | Select-Object Algorithm,Hash\`;
- optional Authenticode \`Get-AuthenticodeSignature -LiteralPath 'EXE_PATH' | Select-Object Status\`;
- whether the installed binary is a release/portable/development build, **only if established by visible file metadata or official release provenance**.
A version string is not enough to prove equality to the audited source commit \`7d44b60ae4042b4de8c3844eb9dd2671c2d2d873\`.

D. Determine the **exact installed embedded Python** version and availability of NumPy *only through a documented OrcaSlicer interface, bundled interpreter, or harmless official diagnostic*. Do not import arbitrary Orca internal DLLs or execute a bundled interpreter unless its supported invocation is established. The current source audit reports Python 3.12.13 but do not claim the installed binary uses that version without direct evidence. Capture complete short version strings, not full system paths.

E. Open the installed OrcaSlicer GUI only as needed for **read-only inspection**, without enabling experimental features or plugins. Document whether the app exposes Plugin Manager / Plugins / package registration / SlicingPipeline or Script capability surfaces; record UI label and visible version. Do not add/install/load untrusted plugin archives; the present Phase 0.5 research ZIP is **not** an Orca plugin.

F. Compare what you can verify with \`docs/PLUGIN_REQUIREMENTS.md\` and \`docs/TEST_STRATEGY.md\` Gate W. Report exact version and unverified APIs separately. No mock API should be called "installed-runtime pass."

### Stage W1 — later gate, **DO NOT RUN NOW**

After a separately reviewed installable **read-only/analysis-only** Orca plugin artifact is built, ask for separate authorization before:
- installing or enabling it in Orca;
- validating capability registration and \`execute(ctx)\` callback;
- running a synthetic fixture or producing **any** export working copy;
- writing any diagnostics under the Orca plugin folder.

That later plan must specify the exact plugin commit, Orca executable fingerprint, fixture, expected result, rollback/disable procedure and zero-G-code-mutation assertion. No actual physical injection or printer activity.

### Required report (return in this conversation; do not commit or upload automatically)

| Gate | Status (PASS / FAIL / BLOCKED / UNKNOWN) | Evidence |
| --- | --- | --- |
| Installed Windows OS/architecture | | |
| Orca executable located, version and SHA-256 | | |
| Installed Orca embedded Python version | | |
| Installed NumPy availability/version | | |
| Documented plugin manager/install route | | |
| SlicingPipeline and Script actual availability | | |
| Exact audited Orca commit equivalence | | |
| Real Smoothificator plugin registered | BLOCKED (not implemented yet) | |
| Read-only G-code-preserving Orca callback fixture | BLOCKED (not authorized yet) | |
| Gate W completed | | |

Conclude with: (1) exact commands actually executed (one line per command, no secret output), (2) observed results and any scrubbed screenshots, (3) unknown/missing facts, (4) whether the installed build is a suitable **candidate** for the future read-only integration test, and (5) the minimum safe follow-up. Do **not** falsely declare Gate W PASS merely because the existing Python project imports or compiles.

**Stop conditions:** unknown API, app crash, unexpected writing, incompatible runtime, missing evidence, or any safety uncertainty => stop and report BLOCKED with the evidence. Never "fix" the user's environment as part of diagnostics.
