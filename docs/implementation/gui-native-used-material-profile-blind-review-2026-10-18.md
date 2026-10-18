# Native effective-used-material integration — independent blind review

Date: 2026-10-18. Scope: nine immutable files in `artifacts/gui-angle0to30-trial-v2/native-integrated-freeze-v3.json`, under the validated effective-material section of `docs/specs/gui-native-paired-trial-review.md`. No primary findings were supplied. **Disposition: no material finding in this bounded profile/resolver and trace/copy integration.** Physical/whole-job authority remains false.

## Snapshot and checks

All nine manifest SHA-256 values matched before and after review/test execution. New profile owner: `dbb939ac15a92511ee9bcf1385701f7fc9d0cbaa3c63d06a2c0f3921ca8f3f99`; integrated trace: `31636ea00be7ee1c4fd2444752ed11349c3167f84a957370be6f5ff21f5656d7`; integrated copy: `7d29148645a1d5ef2429a6a5f6bdaa49be0aeeabd0d4d0cb1f9d5a68ec469674`. Other six exact pins are retained in that manifest. Planner owner is unchanged from its separately reviewed freeze.

Executed with Python3.12.10:

- `.\.venv\Scripts\python.exe -m unittest tests.unit.test_native_used_material_profile tests.unit.test_gui_native_trial_trace tests.unit.test_gui_native_trial_copy tests.unit.test_gui_native_trial_planner -q`: **27 PASS, .556 seconds**.
- `.\.venv\Scripts\python.exe artifacts/gui-angle0to30-trial-v2/native_context.py`: **7948 fresh events**,487 unmodeled effects; context `fae80b7c7324d4e2022cc67d0435c94b756f2cf3107ae46b80a04ea9ba7204ef`.
- Independent stdin probe on the actual pinned immutable inputs: material index2/physical extruder0 and Basic flow0.98 verified; forged effective-profile identity and geometry identity rejected; legacy `read_sliced_profile` still rejects the genuine multi-preset archive; fresh material projection **2397 linear /8 arc bounds /5 unresolved**. Nine final hashes unchanged. No input/output artifact was overwritten.

## Negative-review coverage

Read the full resolver and tests, changed trace/copy trust boundaries and directly relevant tests, closed field registry/handoff, and targeted legacy profile contract. Resolver uses the genuine archive with embedded source/uppercase MD5, common full settings bytes, and separately supplied placed project. It binds all four identities and every unused saved setting through the immutable projection fingerprint. No temporary fake ZIP or relaxed legacy scalar reader is used.

Selection is reconstructed from one used object material, support flags, layer ranges, plate filament IDs/first extruder, source object/material headers, startup material/tool ordering, placed object/part/instance/resource/build mappings, and physical nozzle metadata. Material index2 does not select physical extruder2: physical values require the singleton domain/index0. Unknown body tool selections and unsupported sentinels reject. Tests exercise disagreements across these independent evidence channels and extra used support material.

The closed registry preserves complete filament and machine-mode vectors. Full source numeric vectors and quoted/semicolon text identities are compared before selecting material values; consumed duplicate/missing exports reject. Explicit selected nil alone inherits the machine setting, missing overrides fail, non-nil overrides retain source-key/full-vector provenance. Machine speed/jerk modes preserve their full vectors and conservative minimum. Unknown requested settings reject. Numeric limits, boolean domains, cardinalities, cancellation and stale source/MD5/settings are exercised.

Public native interpretation requires literal geometry bytes/hash and fresh resolver reconstruction matching the declared profile identity. Copy/anchor rebuilding routes through that boundary and derives caps/policy from the fresh profile. Forged selected-index projection or stale geometry cannot be trusted merely because the caller supplies a matching DTO fingerprint. Previous NTC-1 protection remains: all known-positive future deposition includes stationary/vertical events, unknown deposited amounts reject and both endpoint floors are checked. Derived arc center/radius/bounds/turns bit checks remain present. Source-byte recovery and state/acceleration restoration tests continue to pass.

## Limits

The profile resolver establishes consistency among pinned exported evidence; it does not prove physical AMS tray assignment, printer firmware behavior, geometry/source mesh equivalence or undocumented startup effects. Actual geometry shape validation remains the separate pinned-input/artifact obligation. The fresh material readback explicitly retains eight conservative arc envelopes and five unresolved entries; it does not turn them into exact contact support or complete collision evidence. This review accepts neither a current final trial plan/container nor physical printing, and transfers no old-source geometric proof.
