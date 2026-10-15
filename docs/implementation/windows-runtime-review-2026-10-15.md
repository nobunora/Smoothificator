# Windows runtime repository review

Disposition: **validated for isolated diagnostic tooling only**; **blocked for
Phase 0.5 v2 schemas and the usable analysis plugin**.

Reviewed implementation base: `01cc65a632f5b14755a5d90f0b54771e8e45cb86` (PR #2).
Initial specification proposal: `7f3b3467961591295cafd207217864b61ba2dd65` (PR #5).
During this task PR #5 advanced to `6b1f04ea29b6c29413b04f4e5b6e57c439d1601c`.
Its delegated specification owner accepted schema/policy decisions; independent
review, canonical manifest/handoff reconciliation and SPEC_VALIDATED remain pending.
This task did not change ADR status. No canonical document, v1 identity, legacy script,
production namespace, geometry engine, or injector will change in this task.

## Verified external contract

Official stable v2.4.2 source lacks the Python plugin seam. The official nightly
asset downloaded on 2026-10-15 resolves through annotated tag
`bf1cb2e94302cb22d727e7e7ab0d4eb333a02c2a` to source
`86905a8a20d5887f3b13017e66cd897766334bd3`. Its startup log reports
`2.5.0-dev build 86905a8a`. This is distinct from the earlier audit baseline.

Source at that exact revision establishes:

- `sandboxes/orca_gcode_stamp_plugin_any.py`: PEP 723 `.py` metadata,
  `@orca.plugin`, `orca.base`, registration, SlicingPipeline execute(ctx).
  The example's file modification is deliberately NOT copied.
- `sandboxes/orca_inspector_plugin_any.py`: Script execute(), main-thread
  `orca.host.ui.message` and capability registration.
- `src/slic3r/plugin/PluginLoader.cpp`: only `.py`/`.whl` local packages;
  required name; installation below the selected data directory's `orca_plugins`.
- `host/PluginHostApp.cpp`: `orca.host.app_info()` returns version/build, UI only.
- `pluginTypes/slicingPipeline/SlicingPipelinePluginCapability.cpp` and `.hpp`:
  read-only context fields, config_value(), cancelled(), null print/object at
  postprocess, no worker UI calls.
- `PythonPluginInterface.hpp`: ExecutionResult.skipped(), lifecycle callbacks.

All paths above are relative to `src/slic3r/plugin` unless fully qualified.
Official sources: https://github.com/OrcaSlicer/OrcaSlicer/tree/86905a8a20d5887f3b13017e66cd897766334bd3

## Implementation boundary and acceptance

Create a standalone `diagnostics/` single-file plugin, separate from Phase 0.5.
It has no dependency on domain/Plan DTOs and never selects or injects a Plan.
Script diagnostics verify the exact running build before enabling observation
within the current plugin lifetime. Slicing diagnostics read only an offline
File export and report two bounded streaming hashes, size and unchanged status.
No write mode, network, subprocess, geometry mutation or printer operation.
All worker outcomes return Skipped; malformed/missing/unknown inputs fail closed.
No UI calls or retained live Orca references on the worker.

Tests cover unsupported runtime, not armed, disabled, malformed settings, absent
path, non-File host, cancellation, repeated calls, read failure, changed bytes,
and byte preservation with opaque comments. Mock API tests certify only Python
behavior. Actual load/callback and UI gates require separate runtime evidence.

Baseline checks already executed with isolated Windows Python 3.12.10:
compile/import PASS; architecture 41 PASS; full suite 254 PASS.
Lint/type/dependency analyzers are NOT CONFIGURED per QUALITY_GATES.
No new third-party runtime dependency is needed.

## Known blockers

The v2 final projection, independent review, canonical manifest/handoff and
SPEC_VALIDATED remain incomplete on the latest PR #5. Specification-owner
acceptance alone is not the required repository implementation gate.
Computer Use screenshots fail on this Windows host with SetIsBorderRequired
0x80004002; accessibility text works, but indexed actions report no cached bounds.
GUI evidence will be recorded separately and never inferred from unit tests.
