# Phase 0.5 isolated venv build and GitHub Release readiness (2026-10-15)

**Status: VENV RESEARCH BUILD PASS; INSTALLABLE ORCA PLUGIN / GITHUB RELEASE BLOCKED.**
No physical injection is authorized and no claim of usable Orca plugin was made.

## Starting evidence and source discipline

- Work branch: `phase-0.5-skeleton-20261013`; preceding implementation commit `e6609cd6e5fb22ed131e7efbca0f8e494a952d63`, Draft PR #2.
- Normative process: `AGENTS.md`, `docs/DOCUMENT_CONTRACT.md`, `docs/ROADMAP.md`, `docs/TEST_STRATEGY.md` Gate W / Gate X / Gate Y.
- Proposed Settings-v2 and DTO/Attempt contract is the **unaccepted Draft PR #5**, not a validated build contract.
- Present `orca_plugin/__init__.py` explicitly says there are **no Phase 0.5 capabilities enabled**. No Orca plugin loader manifest, capability registration, live context adapters, executor, G-code serializer/injector or installed Orca fixture exists in PR #2.
- `docs/PLUGIN_REQUIREMENTS.md` requires pinned Python 3.12.13, NumPy and exact Orca/plugin compatibility evidence prior to declaring a printable plugin.

## GitHub Actions virtual environment and research bundle

Introduced `.github/workflows/phase05-venv-research-bundle.yml` to run on the implementation branch and its PR. It uses GitHub-hosted Ubuntu and Python 3.12; creates a real isolated `venv` with `python -m venv`, asserts `sys.prefix != sys.base_prefix`, imports both pure namespaces, compiles source, runs every architecture/unit contract test **inside the venv**, and checks that the Orca namespace contains only `__init__.py`. A standard-library ZIP of source modules includes a `RESEARCH-ONLY.txt` disclaimer. The ZIP is uploaded as a temporary GitHub Actions artifact, **not a GitHub Release, wheel, or installable Orca plugin**.

First exact workflow source commit: `f4f352417effad1b449c41c6c9fe900edb8d57f6`.

- [GitHub Actions PR virtualenv run 38735069617](https://github.com/nobunora/Smoothificator/actions/runs/38735069617): **SUCCESS**. Job phases: venv import, compile, all 254 unittest, physical/Orca capability absence check, research ZIP build and upload, all green. The job log reports `Ran 254 tests` and `OK`.
- [Original contract CI run 38735069588](https://github.com/nobunora/Smoothificator/actions/runs/38735069588): **SUCCESS**.
- Research archive: artifact ID `11972625989` from the above workflow, uploaded successfully. GitHub PR workflows may name artifact using the synthetic merge `github.sha`; this does not mean the archive is an Orca executable.
- No network access to install/download a graphical OrcaSlicer binary in the assistant's local container; a real application load was **not** tested. GitHub's virtualenv tested the pure Python source only.

## Required Gate W, release, and simulator backlog

| Gate | Evidence | Status |
| --- | --- | --- |
| Python isolated venv import/compile/tests | GitHub Actions workflow above | PASS |
| Self-contained archive of research Python source | GitHub Actions artifact, clearly disclaimed | PASS (research-only) |
| Python wheel metadata and clean install/load | No build metadata or reviewed plugin distribution metadata | NOT CONFIGURED / BLOCKED |
| Exact Orca embedded Python/NumPy compatibility | Audited source baseline only, no installed Orca fixture | BLOCKED |
| Orca plugin loader and SlicingPipeline/Script capability registration | No runnable capability/module currently | NOT IMPLEMENTED |
| Actual Orca postprocess analyzer/injector fixtures | Later gated phases; no parser/matcher/physical safety/working file lock implementation | NOT IMPLEMENTED |
| Real Orca virtual/headless graphical plugin-load integration | No installed executable or approved fixture/test harness | NOT RUN |
| Independent blind review and no unresolved Critical/High | Unaccepted design contracts and no independent report | BLOCKED |
| GitHub Release usable plugin asset | No installable plugin, no verified Gate W/ X / Y, not suitable for publish | **DO NOT PUBLISH** |

### Why an empty placeholder must not be published

A test zip with only domain/application data and a deliberately inactive `orca_plugin` would mislead users as an installable printer plugin. `compileall` and 254 unittest tests do not exercise the Orca callback, actual source/engine solver, G-code parser, or printer. Publishing a production release or even calling this archive a working plugin would violate the acceptance strategy and AGENTS process. Do not use `gh release create`, a tag, or a GitHub Actions auto-release job to circumvent absent Gate W / X / Y evidence.

## Next work aligned with the approved roadmap

1. Complete accepted, internally consistent Settings v2/Plan v2/Attempt evidence specification in PR #5; independent review and canonical manifest/handoff update.
2. Implement and test the remaining Phase 0.5 immutable contracts in PR #2, preserving golden v1 hashes and no-injection.
3. Follow Phase 1A–3 for geometry, optimizer, read-only Orca snapshots and preview; obtain exact Orca source+installed fixture and an Orca-loadable plugin package.
4. Add virtual Orca callback simulation with explicit fixture parity, then real Orca runtime load/registration and read-only failure tests.
5. Later parser/injector safety gates, independent blind review and target-specific printer checks before enabling any G-code mutation.
6. Only publish GitHub Release assets explicitly labeled by validated capability and with an install/load success log for the exact commit and platform.

**No GitHub Release was created.** Temporary research artifact is not a substitute for a usable plugin.
