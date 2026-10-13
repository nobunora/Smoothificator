# Phase 0.5 — unique attempt ID collision fail-closed review

Date: 2026-10-14
Disposition: **VALIDATED for bounded ADR-0037/0065 uniqueness invariant**, primary review, NOT external Orca release approval.

## Evidence and risk
- Starting in-scope code: `adaptive_subedge/application/execution_status.py::InjectionAttemptStore.begin` at blob `fea68919b4911faa0c0d548cb1997ea0c2299088`: under a private `RLock`, it constructs an immutable `InjectionAttemptRecord(uuid4().hex, ... STARTED)` and assigns `self._records[record.attempt_id] = record`.
- Accepted ADR-0037/0065 require **unique process-local InjectionAttemptId per invocation** and independent immutable outcome records. If two generated UUIDs were equal, the second assignment would silently overwrite the first record, contradicting the hard uniqueness/information-preservation invariant. UUIDv4 collisions are extremely unlikely, but the record store's interface MUST not silently erase evidence when any ID source returns an existing key.
- Root cause is a missing collision guard at the store's authoritative mutable ownership boundary, not an Orca ID/spec issue. The application already owns typed `ContractError(INVALID_STATE_TRANSITION)`; no new schema, public API, UUID derivation or field is needed.
- Scope allowed: detect a duplicate generated ID *before* publishing, fail closed with stable ContractError while preserving first record. Caller can reattempt with a fresh invocation; no fabricated ID, unbounded retry loop or mutation to old attempt. Atomic PlanStore pairing should roll back its unexposed issued snapshot when `begin` rejects.
- Test a deterministic monkeypatched `uuid4` returning one fixed UUID for two starts. Ensure no history overwrite and the original working-file identity/status survives. Test the new `PlanStore.begin_postprocess_attempt` interaction: duplicate attempt-ID failure must not evict plans or corrupt active epoch and existing record.
- No external dependency or physical behavior. CI Python3.12 compileall/unittest, exact source-head SHA/diff evidence. Ruff/mypy, physical printer, actual Orca executable remain NOT VERIFIED.

Expected disposition if CI passes: confirmed -> resolved for the narrowly established record ownership contract. Status of the entire Phase 0.5 remains SPEC-CHANGE-REQUIRED (separate unaccepted ADR-0066/0067).

## Verified implementation, focused regression and disposition

- Implementation commit `cf1c3bd6f7b0921ba89f9900f673e2aedfb13791` adds one fail-closed duplicate-key guard in `InjectionAttemptStore.begin` *before* storing the newly generated attempt record under its single existing lock.
- Three deterministic `tests/unit/test_attempt_uuid_collision.py` regressions at `d002f833b921b2c51a188f9ca77e495b5c908cc0` monkeypatch generated UUIDs: duplicate attempts cannot overwrite historical evidence; a later genuinely different UUID is accepted; an atomic `PlanStore.begin_postprocess_attempt` rejects a duplicate and preserves existing issued snapshot, plan/epoch and prior Attempt record.
- Prior focused `tests/unit/test_attempt_snapshot_issuance_atomic_races.py` commit `51f1178ad3addc362924b3f0d10422fb8836e305` added three adversarial reset lock / failure cleanup / cross-store provenance tests, CI [38426481158](https://github.com/nobunora/Smoothificator/actions/runs/38426481158) **213/213 PASS**.
- Python 3.12 [GitHub Actions 38426756545](https://github.com/nobunora/Smoothificator/actions/runs/38426756545) on collision tests: compileall **PASS**, `python -m unittest discover -s tests -p 'test_*.py' -v` **216/216 PASS**, 0 failures/errors.
- Outcome: collision-overwrite condition **confirmed -> resolved** for process-local status ownership. No assumption about UUID randomness quality, external Orca IDs, actual working-file path exclusivity, Settings v2 or physical mode was added.
