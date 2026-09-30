# Audited Canonical Revision Manifest — 2026-09-30

Purpose: freeze the exact normative document contents approved by the full consistency + technical feasibility audit without relying on a potentially stale branch-head API.

Audit baseline for Orca source: `789f848694b955d293ca6b277d1c8046aa6f7436`.

## Core normative document blobs

- `AGENTS.md` — `dac97cb887b6e5765c067a901be70154a0850385`
- `docs/DOCUMENT_CONTRACT.md` — `a8b5368e3e823886d3b8e1c86b17728dad5a8601`
- `docs/SPECIFICATION.md` — `c9624db96f04dd9a121158240dd74a3aeb1597ae`
- `docs/ARCHITECTURE.md` — `8d4cca1e313109fc94bf55fca5809b13e5ff6ba5`
- `docs/IMPLEMENTATION.md` — `1590e0b7d7110456f9a4d5892b20f227ecab04e9`
- `docs/PLUGIN_REQUIREMENTS.md` — `8430653731de8df64d62d3c1f4417833c2cfdd5f`
- `docs/ERROR_MODEL.md` — `98247d5ced3c2cc7941f7931f90e3448832d485f`
- `docs/ZAA_INTEGRATION.md` — `67eccf4d49644806c9d0f076d7f7c15eb74b1ded`
- `docs/TEST_STRATEGY.md` — `5928f315089a5f329a2e67edf2b20df0a235c007`
- `docs/QUALITY_GATES.md` — `ea88a8cc85d167b11868217cda7e7ce3194927fd`
- `docs/REVIEW_PROCESS.md` — `00b1658a1f25956f6fedf3b4583cce352499d680`
- `docs/ROADMAP.md` — `7bd4d9db2ab2c763820fee341df4aed32b9e0112`
- `docs/FULL_CONSISTENCY_AUDIT_2026-09-30.md` — `6e71c02a250b200197c2b394f9aaea24418f70b4`

## ADR blobs

- `0001-analyzer-hook-after-path-simplification.md` — `21af5233ef2710fdf2afa8a74986683e42717710`
- `0002-v1-supported-geometry-and-plugin-environment.md` — `e66ea1a183de6713d9d19b0cff9efcd89f2c172d`
- `0003-subedge-flow-and-final-surface-model.md` — `f325e91a3a66e2d8d62d47e5e1659d2d2d2f255c`
- `0004-bead-height-not-neighbor-z-spacing.md` — `ec43f9d97120226d3927b87ed2c7d39be6b1f4f3`
- `0005-surface-band-centerline-and-nesting.md` — `636af83c9729a08c2061e0473b986e004e97864f`
- `0006-orca-zaa-z-semantics-and-flow.md` — `69eb5b68c436ad5ff0d1d5d126311e964516eb9e`
- `0007-bambu-layer-boundary-injection.md` — `3668bbec10d4f15a377d2ed67ccf9035f6cfa19a`
- `0008-v1-relative-e-bambu-profile.md` — `cc615640a7ac3db117cd0c6939c038b89790a201`
- `0009-gcode-execution-frame-translation.md` — `51f7b2f4529da846ae2688a1143cda384800b676`
- `0010-orca-filament-flow-ratio-e-conversion.md` — `444bb3ccca72bee3a030e47eb9d02b2024291dce` (Superseded by ADR-0015)
- `0011-export-config-fingerprint.md` — `a6b84f93dfd597b7205a0d3a1f791c341a0248e5`
- `0012-reconstruct-orca-centered-slice-frame.md` — `40d8be3d3d287a6495477baa1d569d8c64e9a38a`
- `0013-restore-actual-emitted-machine-state.md` — `c25cb8256ceca79f0fdf3becc0d0c2a0066e51a7`
- `0014-segment-local-subedge-extrusion-contract.md` — `17dbb25569b927692fd31b8b4479776bfd254a90`
- `0015-match-orca-effective-external-wall-flow.md` — `521da752e17f257cc3a79888f9ccf0d8e889275e`
- `0016-seam-invariant-structural-path-matching.md` — `cf8fb2143c5d6e0a2d4e0fd9d35386f39f7ead8e`
- `0017-orca-gcode-quantization-parity.md` — `a4c16408fe2183ec1a45eb79f3648e7c2b42ddef`
- `0018-preserve-relative-e-retraction-state.md` — `0a652791397687cc31b1867e249f20fee456f839`
- `0019-plugin-result-fail-closed-policy.md` — `39d341fdd29190676e74292b0ac0073a2a74351d`
- `0020-v1-motion-and-extrusion-safety-envelope.md` — `726664188a42f9fcb9f8f19fe61ef3cfaa87132a`
- `0021-derived-emitted-e-after-quantization.md` — `f76fe2748183ece39eb5c34a24733b68631bd605`
- `0022-separate-geometric-and-commanded-volume.md` — `6b17835603f7277fb4379445b7e4e6997fd49c56`
- `0023-plugin-settings-fingerprint.md` — `b5afef3e2adb8ebfac7a0a768f857215391e766b`
- `0024-exclude-first-layer-v1.md` — `4b236d2b39477a9fdf530af5279a0dbbf17ef1ae`
- `0025-downstream-original-motion-clearance.md` — `f9dfe4a05532dbe973e25a179c8013e94a933fcf`
- `0026-v1-subedge-paths-are-planar-constant-z.md` — `7dec7e133f1fd5baebd2da82458ecc0e6ae91cc0`
- `0027-require-manifold-finite-source-mesh-v1.md` — `b96f52efb4625a594f78e37a9be1d087fc08ac73`
- `0028-disable-unreplicated-dynamic-extrusion-features-v1.md` — `380cd51c811ae884d32113e088af00e0dae71213`
- `0029-plan-candidate-seams-before-gcode-emission.md` — `ae0a28ef48465729ce3c0d583c933d9ae6075efb`
- `0030-validate-source-orientation-material-side.md` — `8f40ca1613935ab27c9eb693adf0d3ef2db35fd9`
- `0031-byte-preserving-streaming-gcode.md` — `c4b2fbd54130dd399810fbdfb628d2723b5fc18f`

## Verification rule

Before repository review or implementation, re-fetch every listed path from the target branch and require its Git blob SHA to match this manifest.

If any blob differs:
- this audit revision is no longer current;
- do not silently proceed;
- inspect the change and either update/re-audit the manifest or restore the audited content.

## Why blob manifest instead of one branch commit

During this audit the GitHub connector's branch/ref endpoint returned a stale public head while connector file reads/writes exposed the current working branch contents.

A per-file Git blob manifest directly identifies the normative content set and avoids falsely stamping a stale branch SHA.

This manifest is the canonical revision reference for the first repository-review handoff.
