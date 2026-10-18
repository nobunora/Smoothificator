# Audited Canonical Revision Manifest — 2026-10-13

Status: BLOB-PINNED for Phase 0.5 contract delta; implementation authorization requires a separate dated repository review disposition.

Purpose: preserve the exact source-of-truth content after adding ADR-0064/0065 and propagating ADR-0061–0065 into normative design, handoff requirements, and test strategy.

## Scope and provenance

- Repository: `nobunora/Smoothificator`
- Branch: `adaptive-subedge-design`
- Normative baseline commit before final review corrections: `017aaf7fb2e31f9ae42a829451cae3cd24cccd0b`
- Audited normative tree: `9658d9250a7dfe40d3db323fff8f542cea891dd4`
- Previous external Orca review remains `docs/FULL_CONSISTENCY_AUDIT_2026-10-08.md`, source baseline `7d44b60ae4042b4de8c3844eb9dd2671c2d2d873`. This manifest does **not** assert fresh current-Orca API or physical-fixture verification.
- The 2026-10-01/02 manifest/review records are historical and must not authorize current implementation.
- The handoff `docs/specs/adaptive-subedge-v1.md` is intentionally excluded: it must cite **this manifest's own blob SHA**, so including it would create a hash reference cycle. Review it separately against the manifest after restamping.
- This manifest itself and the future review report are excluded from the enumerated normative source set.

## Core governance / normative and audit-evidence blobs (16)

- `AGENTS.md` — `dac97cb887b6e5765c067a901be70154a0850385`
- `docs/DOCUMENT_CONTRACT.md` — `1ab5e9b8780875e0d13311af08b35d85b5e165e9`
- `docs/ADR_PROCESS.md` — `587fd4c7b0971c4e927482b5016c645e74c4e070`
- `.codex/repository-review.md` — `c2574b93299e25752b696c5f71e438ff4988d6ed`
- `docs/SPECIFICATION.md` — `aa50c940b0ea6f442eb47cfd32c94a28a4bf310f`
- `docs/ARCHITECTURE.md` — `f2b66f659eafc0cc26636da1e5996991936e3d4b`
- `docs/IMPLEMENTATION.md` — `3f0fe6153167ee64e36665b13c62ca31baa1bed5`
- `docs/PLUGIN_REQUIREMENTS.md` — `0892a59dec04ca87dd9cb4ddab7df39ca7118bcd`
- `docs/ERROR_MODEL.md` — `6a892dfd333974007982ede5f91a5a5e24b7e338`
- `docs/ZAA_INTEGRATION.md` — `67eccf4d49644806c9d0f076d7f7c15eb74b1ded`
- `docs/TEST_STRATEGY.md` — `3eef3c9a94f2c09a869dbeb5f2e1eecabffce488`
- `docs/QUALITY_GATES.md` — `ea88a8cc85d167b11868217cda7e7ce3194927fd`
- `docs/REVIEW_PROCESS.md` — `00b1658a1f25956f6fedf3b4583cce352499d680`
- `docs/ROADMAP.md` — `1241c6052a8babdc3d562d5e7d9596bf7c0c5ed3`
- `docs/FULL_CONSISTENCY_AUDIT_2026-10-08.md` — `ef8403036a91f0954fef455ec0e5fa5703405583`
- `docs/FOLLOWUP_AUDIT_2026-10-08.md` — `5eaed1bc49d2c74237028ca4382b4c3462eec70b`

## ADR blobs (65, unique 0001–0065)

- `docs/adr/0001-analyzer-hook-after-path-simplification.md` — `21af5233ef2710fdf2afa8a74986683e42717710`
- `docs/adr/0002-v1-supported-geometry-and-plugin-environment.md` — `e66ea1a183de6713d9d19b0cff9efcd89f2c172d`
- `docs/adr/0003-subedge-flow-and-final-surface-model.md` — `f325e91a3a66e2d8d62d47e5e1659d2d2d2f255c`
- `docs/adr/0004-bead-height-not-neighbor-z-spacing.md` — `ec43f9d97120226d3927b87ed2c7d39be6b1f4f3`
- `docs/adr/0005-surface-band-centerline-and-nesting.md` — `636af83c9729a08c2061e0473b986e004e97864f`
- `docs/adr/0006-orca-zaa-z-semantics-and-flow.md` — `69eb5b68c436ad5ff0d1d5d126311e964516eb9e`
- `docs/adr/0007-bambu-layer-boundary-injection.md` — `3668bbec10d4f15a377d2ed67ccf9035f6cfa19a`
- `docs/adr/0008-v1-relative-e-bambu-profile.md` — `cc615640a7ac3db117cd0c6939c038b89790a201`
- `docs/adr/0009-gcode-execution-frame-translation.md` — `51f7b2f4529da846ae2688a1143cda384800b676`
- `docs/adr/0010-orca-filament-flow-ratio-e-conversion.md` — `444bb3ccca72bee3a030e47eb9d02b2024291dce`
- `docs/adr/0011-export-config-fingerprint.md` — `a6b84f93dfd597b7205a0d3a1f791c341a0248e5`
- `docs/adr/0012-reconstruct-orca-centered-slice-frame.md` — `40d8be3d3d287a6495477baa1d569d8c64e9a38a`
- `docs/adr/0013-restore-actual-emitted-machine-state.md` — `c25cb8256ceca79f0fdf3becc0d0c2a0066e51a7`
- `docs/adr/0014-segment-local-subedge-extrusion-contract.md` — `17dbb25569b927692fd31b8b4479776bfd254a90`
- `docs/adr/0015-match-orca-effective-external-wall-flow.md` — `521da752e17f257cc3a79888f9ccf0d8e889275e`
- `docs/adr/0016-seam-invariant-structural-path-matching.md` — `cf8fb2143c5d6e0a2d4e0fd9d35386f39f7ead8e`
- `docs/adr/0017-orca-gcode-quantization-parity.md` — `a4c16408fe2183ec1a45eb79f3648e7c2b42ddef`
- `docs/adr/0018-preserve-relative-e-retraction-state.md` — `0a652791397687cc31b1867e249f20fee456f839`
- `docs/adr/0019-plugin-result-fail-closed-policy.md` — `39d341fdd29190676e74292b0ac0073a2a74351d`
- `docs/adr/0020-v1-motion-and-extrusion-safety-envelope.md` — `726664188a42f9fcb9f8f19fe61ef3cfaa87132a`
- `docs/adr/0021-derived-emitted-e-after-quantization.md` — `f76fe2748183ece39eb5c34a24733b68631bd605`
- `docs/adr/0022-separate-geometric-and-commanded-volume.md` — `6b17835603f7277fb4379445b7e4e6997fd49c56`
- `docs/adr/0023-plugin-settings-fingerprint.md` — `b5afef3e2adb8ebfac7a0a768f857215391e766b`
- `docs/adr/0024-exclude-first-layer-v1.md` — `4b236d2b39477a9fdf530af5279a0dbbf17ef1ae`
- `docs/adr/0025-downstream-original-motion-clearance.md` — `f9dfe4a05532dbe973e25a179c8013e94a933fcf`
- `docs/adr/0026-v1-subedge-paths-are-planar-constant-z.md` — `7dec7e133f1fd5baebd2da82458ecc0e6ae91cc0`
- `docs/adr/0027-require-manifold-finite-source-mesh-v1.md` — `b96f52efb4625a594f78e37a9be1d087fc08ac73`
- `docs/adr/0028-disable-unreplicated-dynamic-extrusion-features-v1.md` — `380cd51c811ae884d32113e088af00e0dae71213`
- `docs/adr/0029-plan-candidate-seams-before-gcode-emission.md` — `ae0a28ef48465729ce3c0d583c933d9ae6075efb`
- `docs/adr/0030-validate-source-orientation-material-side.md` — `8f40ca1613935ab27c9eb693adf0d3ef2db35fd9`
- `docs/adr/0031-byte-preserving-streaming-gcode.md` — `c4b2fbd54130dd399810fbdfb628d2723b5fc18f`
- `docs/adr/0032-chronological-material-state-and-support-order.md` — `81599b3a48ef52f300a987db3f12e4436f55b661`
- `docs/adr/0033-unified-final-tool-clearance-validation.md` — `f3c491f661cca9202cd747d243f4b82d263eb0ec`
- `docs/adr/0034-v1-require-mm-units-and-absolute-xyz.md` — `14fefd9e24769e9c9c77bc7c377f127fb8f8279d`
- `docs/adr/0035-v1-gcode-modal-and-runtime-override-envelope.md` — `715706c24bda2ba8566aa36c5ca759176a0ac140`
- `docs/adr/0036-v1-require-unity-firmware-feed-flow-overrides.md` — `82995925a99130f4777a969a26b916a54fe7ace0`
- `docs/adr/0037-attempt-scoped-state-and-precommit-revalidation.md` — `1c111f8303f8bed71c40a554341d084e92ec561e`
- `docs/adr/0038-v1-simple-connected-topology.md` — `f9949e56396b17e06a4029a14e26e3d08e924579`
- `docs/adr/0039-disable-unreplicated-extrusion-rate-smoothing-v1.md` — `b2fd7c31513c66b52a3ce845dd892863ba3e3636`
- `docs/adr/0040-v1-inherited-acceleration-gate.md` — `8da6cd8f331200c058ab20d55a2520dce638589b`
- `docs/adr/0041-postprocess-metadata-and-progress-limitation.md` — `d7d89517ffb2642e61532a144247066538a687a8`
- `docs/adr/0042-disable-mixed-filament-sublayers-v1.md` — `459de51a869799a574100a106d3018368a779ca9`
- `docs/adr/0043-candidate-bead-geometry-bounds.md` — `f6322896e404a82b3e708388d2ef01befd4be33a`
- `docs/adr/0044-versioned-support-coverage-metric.md` — `5d069597dc426a6e7a218e70e568852cd1b99679`
- `docs/adr/0045-converged-error-estimation-contract.md` — `6dc799f71ff8c003c0f0061967ad54ffc3358261`
- `docs/adr/0046-inherited-jerk-gate.md` — `288b355ef22ef3820ff10bb459e0e66ed36ce8c5`
- `docs/adr/0047-bidirectional-surface-error-and-coverage.md` — `ec8075af4122b30621eee97b40e77182473077c2`
- `docs/adr/0048-versioned-nominal-bead-solid.md` — `56ee4413e536dfa3d3e24da07c808d64a9595473`
- `docs/adr/0049-canonical-serialization-and-hashing.md` — `af60a9979223bfff43d6d53d5f4b6477e54ead6a`
- `docs/adr/0050-local-surface-correspondence-policy.md` — `437fc444fae43ec55d5cfe716cb09f8d14f9692f`
- `docs/adr/0051-gate-orca-slice-geometry-modifiers.md` — `e4241b1a404a3f3da353fab67c31c94f8862a61f`
- `docs/adr/0052-gcode-feedrate-unit-contract.md` — `21e273c75a4d12c7c4362d8560789f4cb5f7aada`
- `docs/adr/0053-robust-mesh-plane-section-policy.md` — `be019549faa153dea04b8e5c17a940efe52dd6ad`
- `docs/adr/0054-final-structural-deposition-revalidation.md` — `102a593e5bb1aef55781d1a8b8efb49f0fe719e3`
- `docs/adr/0055-v1-simple-target-loop-only.md` — `c70b604fafe612f01ba41a5fe675019651f955bb`
- `docs/adr/0056-v1-timelapse-wrapping-and-object-cancellation-gates.md` — `085a1f78c1a14a7d0bc398aa4ca5951647904327`
- `docs/adr/0057-postprocess-time-cooling-metadata-limitations.md` — `b6190dbbc6a982735efcc7a82dc9908ab890e8cc`
- `docs/adr/0058-conservative-converged-support-coverage.md` — `e8aa90e054f881402fd74fd527c753da1343cb3b`
- `docs/adr/0059-topology-aware-mesh-section.md` — `ed8741401e6a58bc1a8b5737f5381624055d69bf`
- `docs/adr/0060-closed-candidate-influence-error-domain.md` — `48e8052a76cc0ff6c951fa81a5aa5cea08e5dc16`
- `docs/adr/0061-working-file-commit-lock.md` — `879ae9cca66e15210c4087b0bbc1f5a6859f2cc6`
- `docs/adr/0062-canonical-bytes-and-hash-domain-separation.md` — `38aba5f3b2c84dd1de1462d03314eb60c0b0e851`
- `docs/adr/0063-candidate-segment-regularity.md` — `9594b50023b3a765f0d31dc11fb360e4e7cc8b89`
- `docs/adr/0064-canonical-plan-identity-construction.md` — `589322d5ddb22f9a5c997078942f09d4ea6b808e`
- `docs/adr/0065-planstore-session-and-generation-selection.md` — `a4bf46263c17269a96e1d96a65b147da0e4ac212`

ADR-0010 remains Superseded by ADR-0015. ADR-0064 refines ADR-0049/0062 for self-reference and nested-array token identity. ADR-0065 clarifies ADR-0037 for session/generation eligibility. ADR-0061 controls the later same-file commit critical section, and ADR-0063 controls candidate segment regularity. All must be followed within scope.

## Revalidation rule

Before handoff repository review or implementation:
1. Fetch the exact Git blobs for **every** path listed here and compare their SHA to the entries above. A branch-head SHA or search index alone is insufficient.
2. Require uniqueness and contiguous coverage of ADR identifiers 0001–0065 and validate status/supersession for relevant ADRs.
3. Confirm the handoff references this manifest's **actual Git blob SHA**, and that it does not override any accepted ADR or normative contract.
4. Revalidate the Phase 0.5 scope and record a new review-only disposition. A historical `validated` disposition is not reusable.
5. If any listed SHA differs or a required contract is ambiguous, invalidate this handoff and return to specification adjudication.

Physical injection, plugin parsing/emitting and real printer operation remain independently gated. No production code changes are authorized by this manifest alone.
