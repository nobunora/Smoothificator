# GUI native-trial package independent blind review — 2026-10-18

Initial disposition: **three Medium findings**. Reviewed only frozen `tools/package_gui_native_trial.py` and `tests/unit/test_gui_native_trial_package.py`, the validated handoff, required native-arc/package research and review process. No parent findings were received before these independent findings. Native trace/copy implementation is a separate unreviewed dependency here. No GUI, network, printer operation or source edit occurred.

Owner SHA256 `beec0092a4ecbaf8b783decb66d8e6b276033cf9b3ffd35e80db1bbc55f5f0c3`; test SHA256 `5f039419a580928495f589bd634791b87ef09f7a59ac6d2ff4bb8b162a807f68`, unchanged at the end of checks. Original GUI archive SHA `17565bf3c6c7b2c27db3e9ed8e5efc17ac537c693eeaf6ea61a7c8619364b5ce`; embedded/separate source SHA `41075290eab177ffbb011e438bbc8e2a6e6efb643566813bc6d0a54e3baa2630`. Any subsequently authorized re-slice is a separate identity and does not replace this review's input.

## GNP-1 — Medium — Mutable receipt bytes can bypass fresh publication validation

Location: `tools/package_gui_native_trial.py:184` through189/192, fresh receipt comparison followed by writing caller `package.archive_bytes`.

`NativeTrialPackage` is a frozen dataclass but its fields are not type-validated. A forged receipt with `archive_bytes=bytearray(valid_bytes)` compares equal to the freshly rebuilt immutable `bytes` receipt, and SHA256 accepts that buffer. After validation the writer continues using the caller's mutable buffer rather than the fresh trusted bytes. A mutation between validation and write is therefore published; readback compares against the same mutated buffer, not the validated digest.

Independent isolated writer probe followed the existing writer-test dependency-injection pattern: mocked the fresh owning rebuild to return a valid immutable package, passed an equal receipt containing a bytearray, and deterministically mutated its first byte at temporary-file allocation after validation. The writer published a file beginning `QK\x03\x04` instead of ZIP `PK\x03\x04`; its hash differed from the accepted receipt hash. No original archive/source was modified. The hook models a concurrent caller mutation, not a failure of the rebuild implementation.

Invariant: immutable/fresh receipt validation must bind the bytes actually published. Reject mutable payload categories and/or write only `fresh.archive_bytes`; verify readback against its fixed digest. Add the hostile equal-bytearray/interleaving regression. Confidence high; disposition pending reconciliation.

## GNP-2 — Medium — Cancellation during writing does not prevent publication

Location: `tools/package_gui_native_trial.py:187`–195, no cancellation checkpoint between file writing/readback and `os.link`.

The build polls cancellation, but the writer never polls again after the build returns. An independent writer probe toggled cancellation to true from the fsync hook, with normal write/readback and a valid fresh rebuilt package. The destination was nevertheless published (`PUBLISHED_AFTER_CANCEL=True`). This can occur when cancellation arrives during the actual I/O phase.

Invariant: a cancelled operation must not publish a newly successful experimental artifact. Poll the exact boolean cancellation callback immediately before the atomic link; retain cleanup on rejection. Add a write-phase cancellation regression. Confidence high; disposition pending reconciliation. This is offline artifact publication, not evidence of an actual printer action.

## GNP-3 — Medium — Actual GUI archive always fails unchanged compressed-size equality

Location: `tools/package_gui_native_trial.py:166`–167, comparing unchanged `compress_size` after stdlib recompression.

Independently read the exact pinned 70317-byte/16-member GUI archive with the new reader, then executed the production cloning loop entirely in memory. Only a review comment was appended to the new G-code and its uppercase MD5 regenerated; all other uncompressed bytes remained exact. Readback/source/MD5 succeeded and16 permitted flags normalized. However four unchanged members have different compressed serialization sizes:

| Member | Original | Recompressed |
|---|---:|---:|
| `[Content_Types].xml` |242|241|
| `Metadata/project_settings.config` |11919|11932|
| `Metadata/slice_info.config` |658|659|
| `Metadata/filament_sequence.json` |68|63|

Consequently the production equality gate rejects the required genuine GUI archive for any otherwise valid supplemented copy. This failure is independent of the still-separate native-copy implementation or its G-code contents. The gate fails closed, but the required actual-container workflow cannot complete.

Remediation requires preserving unchanged compressed records, or explicit specification adjudication permitting enumerated recompression serialization changes while preserving uncompressed contents, CRC, names and all agreed semantic metadata. Do not silently remove an integrity requirement or claim compressed-byte identity. Add a real pinned-archive packaging regression rather than only stdlib-created synthetic archives. Confidence high; disposition pending reconciliation.

## Executed checks and negative coverage

Command `.\.venv\Scripts\python.exe -m unittest tests.unit.test_gui_native_trial_package -v` — PASS,8 tests,.558 seconds, Python3.12.10. Tests cover source/MD5 readback, names/aliases/duplicates, unsafe paths/unknown integrity names, byte/member/uncompressed limits, exact cancellation booleans, finite XY containment, stale/forged receipt, atomic no-overwrite publication, local/central flag disagreement and corrupt CRC. The synthetic public rebuild test executes the native-copy dependency as a black box; it does not approve that moving dependency.

Independently verified original source/GUI archive pins,16 decoded members, matching uppercase source MD5, actual local/central timestamps, supported flags and actual data-descriptor records. The reader validates local signature/name/version/flags/method, non-descriptor local integrity fields and full decompressed CRC. Generic raw descriptor-footer validation is not established by these tests; the original literal archive pin protects its current admission. Actual local ZIP64 extras differ from central extras in two members; no false claim of raw local-header byte equality is made.

The changed-content inventory is closed to G-code and its MD5. Cached times/filament/thumbnails are explicitly labeled stale. Aggregate XY containment checks actual retained bbox `[75,80,105,100]`; complete motion-bound correctness, Z/arc geometry, source equivalence and recipe semantics remain the separate fresh native-copy owner's obligation and require its own review. A successful package must not promote cached estimates, UI availability or these fields into physical authority.

Writer no-overwrite/alias checks and hard-link publication preserve originals in the examined ordinary paths; temporary cleanup exists. GNP-1/GNP-2 prevent claiming the stronger immutable/cancellation publication guarantees. GNP-3 blocks real archive completion despite clean synthetic tests. All checks used read-only inputs, memory-only archive clones or new disposable test outputs. No actual supplemented GUI package, UI loading, job sending or physical result is accepted by this report.

## GNP-1/2/3 correction verification

Parent confirmed all three findings after the initial report. Reviewed corrected owner SHA `1f821387d1c07524992181454431b44939d63e35ba7db61b3d4df99a4533c505` and test SHA `8e9710f7288d9b087ac576922d4bb6fbbe0254b4d563cb39cd0eb7be1e676071`. The amended handoff explicitly adjudicates same-method recompression with every compressed-size difference enumerated, while unchanged uncompressed bytes/CRC/size and agreed ZipInfo fields remain exact.

Independently repeated the original counterexamples. Equal bytearray receipt is rejected before temporary allocation; writer uses fresh immutable bytes and fixed-digest readback. Cancellation toggled at fsync now rejects before link and cleans the temporary file. The exact original17565 archive now repacks successfully in memory: only G-code/MD5 contents change,16 allowed flag normalizations and the same four unchanged-member compressed-size differences are recorded. No silent CRC/content weakening occurred. Disposition: **GNP-1, GNP-2 and GNP-3 confirmed, fixed and independently verified** under the amended serialization contract.

Combined command `.\.venv\Scripts\python.exe -m unittest tests.unit.test_gui_native_trial_trace tests.unit.test_gui_native_trial_copy tests.unit.test_gui_native_trial_package tests.unit.test_gui_native_trial_planner -v` — PASS,30 tests,.773 seconds, including11 packaging tests. This correction remains based on the preserved old literal archive/source; any subsequent re-slice requires its own pins and actual artifact checks. No new physical/UI/print approval is conferred.

Final stability check detected a subsequent package owner/test change to hashes `1d2b92532a35ed410ba1fec9c6789fc7615790c5ebc500a25abf87e32f795576` / `8e5a29a743d4af42b8cd6ce432eb3e737e2a04cf3ac83338ed319a0a7f8666bc`, introducing explicit expected source/archive fields in the policy. That new input-policy interface was not part of the reviewed correction snapshot above. Parent notified; current-owner approval requires a separately frozen delta review. GNP-1/2/3 verification remains valid for the explicitly recorded1f821387 snapshot, not silently transferred to the newer files.

## Explicit package-policy identity delta — independent verification

Reviewed frozen owner SHA `1d2b92532a35ed410ba1fec9c6789fc7615790c5ebc500a25abf87e32f795576`, test SHA `8e5a29a743d4af42b8cd6ce432eb3e737e2a04cf3ac83338ed319a0a7f8666bc`, and handoff SHA `44dd5ce84b21d4109f6b543126484cc500ca70a03dcc4e22bf8d942120274dd2`. Disposition: **validated for the bounded packaging delta; no new material finding**. This closes the newer-owner review hold recorded above.

`NativePackagePolicy` requires both source and GUI-archive SHA-256 identities as immutable exact strings matching lowercase64hex. Public build/write APIs require explicit policy. Actual source/archive byte hashes are checked against that policy before invoking native-copy rebuilding; rebuilt copy identities must also agree. No legacy global pin or implicit default authorizes a newer source. Private `_read_archive` remains a bounded ZIP/content validator, not a public identity-admission substitute.

Command `.\.venv\Scripts\python.exe -m unittest tests.unit.test_gui_native_trial_package -q` — PASS,13 tests,.503 seconds, Python3.12.10. The current actual archive/source hashes are independently matched by the regression, its archive reads with matching embedded G-code/MD5, and all four old/current cross-pin combinations reject before native-copy use. Additional stdin probe rejected eight forged digest inputs (equal-to-anything object, `str` subclass, bytearray and bool in either policy identity field). Existing GNP-1 mutable receipt, GNP-2 cancellation-at-fsync and GNP-3 real old-archive recompression regressions all pass under this same current owner. Source/test/spec hashes were checked again after execution and remained unchanged.

This review does not approve a current final supplemented copy, planner/material resolver, profile-effective interpretation, GUI behavior or physical printing. Those remain separate scopes; no old-source artifact acceptance transfers through this policy change.
