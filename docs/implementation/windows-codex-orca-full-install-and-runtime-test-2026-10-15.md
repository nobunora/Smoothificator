# Windows Codex handoff — full installation, isolated integration, and release-gate testing

**Date:** 2026-10-15  
**Authority:** user authorizes Codex to operate with necessary Windows administrator privileges, download/install/update trusted software, provision isolated test environments, create and execute tests, alter test-only plugin settings, and make bounded repository changes. This is broader than the former read-only Gate W0 request.  
**Project:** https://github.com/nobunora/Smoothificator  
**Implementation PR:** https://github.com/nobunora/Smoothificator/pull/2 (branch `phase-0.5-skeleton-20261013`)  
**Integrated specification PR:** https://github.com/nobunora/Smoothificator/pull/5 (Draft / proposed ADR-0066 and ADR-0067)  
**Scope:** Windows install and runtime compatibility, virtual environment, disposable read-only Orca integration probe, repeatable test/build and evidence. Full OS permission is **not** permission to bypass release/safety gates.

## Copy-paste task for Codex (execute, not just plan)

You are operating my Windows machine **with full implementation/installation privileges** to advance Smoothificator. Execute all safe, independently verifiable tasks possible in this session. Do not stop at environment inventory or an implementation plan. Install required trusted tooling if missing, establish a reproducible Windows test environment, build and test the Python code, and create a disposable read-only OrcaSlicer plugin probe if the actual verified SDK permits it. Record exact outcomes and blockers, then provide a reproducible handoff to the main branch.

### Authorized operations (no separate confirmation needed for these categories)

- Inspect Windows OS architecture, application versions, installed runtimes, configuration locations, event logs *scoped to this task*, file hashes and documented Orca plugin APIs.
- Download/install/update **official verified** OrcaSlicer and supported Python/venv/build tools, NumPy **only when required and justified**; use a dedicated test environment. Elevate through UAC where needed; never disable UAC, antivirus, SmartScreen or certificate verification.
- Create/modify disposable test directories, venvs, synthetic 3D/G-code fixtures, test-only Orca profiles, a **non-writing read-only integration probe** and isolated plugin installation in the dedicated test instance/profile.
- Run linters/type checks if already configured; compile Python, execute unittest, perform read-only plugin registration/callback tests, generate *offline test-only* slicer exports if source-verified and safe. Inspect hashes before/after to prove no G-code mutation.
- Create a dedicated feature branch, make bounded source/tests/docs changes, commit and push the changes and open a **Draft** PR with verified results. Respect project review workflow; do not merge speculative contract changes.
- Remove disposable installations/files created solely for this exercise and restore original user configuration when required; prefer portable/side-by-side install and backups.

**No additional permission should be requested for ordinary installation, isolated test writes, environment setup, compile/test execution or Draft PR submission.** If UAC prompts, use the normal Windows elevation flow. If user action is inherently required (credential entry, UAC approval, GUI prompts inaccessible to Codex), state the exact step rather than bypassing the prompt.

### Non-negotiable boundaries

1. **NO real printer connection, upload, network print, heater movement, motion commands, actual physical printing, or printer firmware changes.** No customer/personal project data.
2. **NO production G-code mutation or physical injection.** Do not activate any unfinished injector, change a real user's G-code or feed modified G-code to a printer. Synthetic generated G-code can be *observed* in a sandboxed test run; it must remain byte-identical through a read-only probe.
3. Do not publish a GitHub **production plugin Release** or label a research ZIP an installable/working plugin until official package metadata, real Orca install/load, capability registration, test fixtures, safety review, independent review and required gated checks are complete. A non-installable GitHub Actions research artifact is not a Release.
4. Do not silently Accept proposed ADR-0066/0067, alter v1 canonical hash golden bytes, merge Draft PRs, change legacy `Smoothificator.py`/`Smoothificator_Adaptive.py`, or invent hardware calibration/tolerances. `AGENTS.md` and Accepted ADRs override user-level workflow enthusiasm.
5. Protect user security/privacy. Do not dump secrets, personal profiles, full environment, registry hives, paths containing personal names, private G-code or tokens. Never upload raw private Orca profiles or logs.
6. Limit system changes to verified vendor installers and task-specific isolated/test scope. Back up or isolate config before changing it; do not overwrite an existing production Orca installation if a side-by-side option exists. Do not disable security controls or bypass network/domain policy.
7. Do not use `pip --break-system-packages`, run unreviewed scripts, execute arbitrary downloaded binaries, or install unpinned packages without source/need/licensing check. No dangerous recursive deletion or broad environment cleanup.
8. Missing actual Orca API/source evidence => report BLOCKED, not a guessed mock success. A mock-only test can be PASS for the mock test, not the real install gate.

## Required preflight

Read, in order: `AGENTS.md`, `docs/DOCUMENT_CONTRACT.md`, `docs/PLUGIN_REQUIREMENTS.md`, `docs/QUALITY_GATES.md`, `docs/TEST_STRATEGY.md` (A/B/W/X/Y), `docs/ROADMAP.md`, `docs/implementation/phase05-release-readiness-2026-10-15.md` and PR #5's proposed ADRs + latest review findings. Retrieve latest PR #2 and PR #5 HEADs and confirm working-tree status before editing.

Use concise one-line PowerShell 7 commands for targeted inspection. Keep output bounded. Representative read-only commands (replace placeholders only after locating paths):
- `$PSVersionTable.PSVersion.ToString()`
- `Get-ComputerInfo | Select-Object OsName,OsVersion,OsArchitecture`
- `git status --short`
- `git rev-parse HEAD`
- `Get-Command OrcaSlicer.exe -ErrorAction SilentlyContinue | Select-Object Source,Version`
- `(Get-Item -LiteralPath 'CONFIRMED_EXE_PATH').VersionInfo | Select-Object ProductVersion,FileVersion,CompanyName`
- `Get-FileHash -LiteralPath 'CONFIRMED_EXE_PATH' -Algorithm SHA256 | Select-Object Algorithm,Hash`
- `Get-AuthenticodeSignature -LiteralPath 'CONFIRMED_EXE_PATH' | Select-Object Status,StatusMessage`
- `winget search --name OrcaSlicer`
- `py -0p`

For changes/tests, use short one-line commands or checked-in, reviewed script files after reading them. This task explicitly authorizes writes/tests, but keep every change narrow, logged, reversible and limited to the project/test environment; never use generic copy-paste installer scripts fetched from unverified web hosts.

## Stage W0 — install and pin the Windows runtime (DO NOW)

1. Record Windows edition/build, architecture, PowerShell, Git, Python launcher, and existing OrcaSlicer build. If none is installed, acquire OrcaSlicer **from its verified official repository/release distributor**, inspect publisher/signature and published digest where available, and install it or choose an isolated portable/side-by-side deployment. If installed version is unsupported or undocumented, first establish whether a separate vetted build is needed.
2. Record the exact Orca executable path (redacted), product/file version, SHA-256, Authenticode result (including when unsigned), distribution channel, official release URL/commit evidence and install method. A version number alone must never be reported as matching the audited Orca source commit `7d44b60ae4042b4de8c3844eb9dd2671c2d2d873`.
3. Check plugin manager/package format, documented Python embedding version and NumPy import/version using the installed program's documented facilities. If unsupported or impossible without guessing an API, record UNKNOWN. Do not inject arbitrary Python into a process or load random DLLs.
4. Preserve current user preferences. Create a test-specific Orca configuration/profile or a safe portable instance wherever supported; choose synthetic geometry only. No real printer discovery, Wi-Fi printer login or upload.
5. Compile a compatibility matrix contrasting installed build evidence against `PLUGIN_REQUIREMENTS.md` with independent `SUPPORTED / NOT SUPPORTED / UNKNOWN` entries. If source-level API has drifted, record exact path/line/commit and open a design issue rather than inventing callback signatures.

## Stage W1 — isolated Python, dependencies and reproducible bundle (DO NOW)

1. Provision a project-specific **Windows Python >=3.12** venv (do not confuse normal Windows Python with Orca's own bundled Python). Run compilation and the entire suite from the checked-out verified implementation branch.
2. Run `python -m compileall -q adaptive_subedge orca_plugin tests` and `python -m unittest discover -s tests -p 'test_*.py' -v` using the venv interpreter. Report exact full command, interpreter version, SHA and test count. Baseline observed on Linux: 254/254; don't assume Windows will match.
3. Inspect the research-only ZIP artifact produced by GitHub Actions, its contents and manifest. Unpack in a separate directory, import the modules using a clean interpreter, validate CRC and hashes, and verify no Orca callback is registered in the Phase 0.5 package. **Do not pass the research ZIP to Orca as an installable plugin.**
4. If a standard wheel or Orca package can be built from reviewed metadata and a validated dependency contract, document the scope first and add packaging in a separate Draft PR. Do not improvise installer metadata or call a generic ZIP a verified package.
5. Generate a Windows evidence record with hashes, git SHA, interpreter paths redacted, requirements, command success/failure, and an independently reproducible build procedure.

## Stage W2 — real Orca read-only load test (DO NOW IF SDK VERIFIED)

The current repo has only `orca_plugin/__init__.py`; it has NO runnable capability. To learn the real plugin API, inspect the **exact installed build** plus official/source-verified plugin examples and package manifest/entrypoint before writing anything. Then:

1. Create a separate disposable **diagnostic-only plugin** project/package in a test-only directory or a dedicated test feature branch. Implement only the *minimum verified* registration/initialization callback/API and clear module version/reporting. Do not pretend this is the production Smoothificator injector.
2. Install/enable the diagnostic plugin into the isolated Orca instance using its **verified official UI or documented plugin manager**. Verify the app recognizes it, capability registration logs are present and the expected callback is invoked. If necessary, a minimal Script capability can first prove registration; inspect binding/source before attempting SlicingPipeline.
3. If and only if source/fixture evidence supports it, produce a tiny **synthetic offline** model slice and postprocess working-file copy. The probe should report metadata and return the documented no-op/Skipped result. Record SHA-256 and byte-size of the file immediately before and after; assert **unchanged bytes**, with no writing, injection or printer export. A test can write its own synthetic fixture to a temp directory but the plugin must not mutate the working G-code.
4. Include positive and negative cases: plugin disabled, plugin enabled, unknown callback/type, absent `ctx.gcode_path`, malformed config, repeated callbacks, cancellation. Never infer a unique Orca invocation ID; application assigns attempt IDs if this is later integrated.
5. Capture sanitized short logs and screenshots where helpful. If real GUI automation is unavailable, detail precisely what manual one-time GUI action is needed; perform every remaining automated check.

A **successful W2** means *only* the diagnostic plugin registers/executes without modifying G-code on the pinned Windows Orca target. It does **not** mean geometry analysis, Settings v2, G-code injection or print safety is complete.

## Stage W3 — engineering and CI follow-through (WHEN GATES ALLOW)

1. If SDK/API findings expose a verified problem, record severity, file/line, failing fixture and fix within the smallest approved interface contract; write Windows-specific integration tests. Do not change proposed ADR fields/identity schemas until accepted and a review-only repository validation is `validated`.
2. If official Orca load works, prepare an **analysis-only** plugin package target with correct manifest, version, entrypoint and documented requirements. It may intentionally return unsupported/no-plan and must report no physical injection. Such packaging is a later reviewed step, not implicit Phase 0.5 capability.
3. Add a repeatable Windows CI job when reliable automated fixture support exists. Keep Windows GitHub runner tests distinct from local installed-Orca integration evidence; don't claim a fresh runner contains Orca unless the job explicitly installs/verifies it.
4. Create a Draft PR with exact changed files, supported OS/Orca versions, SHA, commands, build/install screenshots/logs, safety gates and rollback path. No silent merge or tag.
5. If later all formal release gates pass (including mandatory independent review for high-risk executable G-code), assemble a versioned release asset and concise accurate changelog, then request the final go/no-go based on that evidence. User authorizes tooling installation/testing now; **public release of an unvalidated printer plugin is not authorized by this handoff**.

## Stage W4 — clean rollback and final report

Before completion, remove or disable test-only plugin registrations as appropriate; check that personal Orca settings were not altered. State any tool/config changes left installed (versions, reversible uninstall method, no sensitive paths). Ensure no test G-code was sent to a printer. Record exact git commit and current Draft PR.

Mandatory report table:

| Gate | Status PASS/FAIL/BLOCKED/UNKNOWN | Exact evidence |
| --- | --- | --- |
| Windows host, architecture, privilege/elevation path | | |
| Trusted Orca installation, version, SHA-256, signature | | |
| Orca embedded Python and NumPy | | |
| Isolated external Python venv + full tests | | |
| ZIP/wheel build and clean extracted test | | |
| Documented plugin package format/entrypoints | | |
| Disposable diagnostic plugin registered | | |
| Real read-only Orca callback invoked | | |
| G-code byte-identical before/after probe | | |
| Source API drift + compatibility contract | | |
| Rollback and original config preservation | | |
| Gate W readiness and release decision | | |

Conclude with actual command history (brief and redacted), official download/verification links, artifact filenames/SHA-256, tests and callbacks observed, any blockers, GitHub Draft PR/commit links and the **next smallest safe change**. Explicitly separate `VENV PASS`, `ORCA DIAGNOSTIC LOAD PASS`, `USABLE ANALYSIS PLUGIN`, and `PRINTABLE INJECTOR RELEASE` statuses. Do not report the last two unless their own gates are proved.

### Stop conditions and incident handling

Unexpected printer communication, real G-code mutation, signature/security warning, corrupted Orca configuration, inability to isolate user data, unverified plugin API, unrelated system access or installer provenance uncertainty => immediately disable the affected test, preserve evidence in the sandbox, restore a known-good configuration where safe, and report the exact blocker. Never hide a failure by disabling security protections.

## Links

- Orca source audit pinned reference (not automatically equivalent to installed exe): https://github.com/OrcaSlicer/OrcaSlicer/tree/7d44b60ae4042b4de8c3844eb9dd2671c2d2d873
- Existing Windows read-only instruction (superseded by this full-install document): `docs/implementation/windows-codex-orca-gate-w-readonly-2026-10-15.md`.
