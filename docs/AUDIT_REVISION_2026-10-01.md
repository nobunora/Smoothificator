# Audited Canonical Revision Manifest — 2026-10-01

Purpose: freeze the exact normative document contents approved by the 2026-10-01 full consistency + technical feasibility audit without relying on the branch-head endpoint.

Orca source audit baseline:
`789f848694b955d293ca6b277d1c8046aa6f7436`

## Core normative / governance blobs

- `AGENTS.md` — `dac97cb887b6e5765c067a901be70154a0850385`
- `docs/DOCUMENT_CONTRACT.md` — `4d92e0c6e1bb5a256bc9de03aa776bc05381658a`
- `docs/ADR_PROCESS.md` — `587fd4c7b0971c4e927482b5016c645e74c4e070`
- `docs/SPECIFICATION.md` — `c3c092ce578ad497518833c3f42d890038dcfb1a`
- `docs/ARCHITECTURE.md` — `3ab1817cdf28856ed922ae962e7205d4c1dd52ea`
- `docs/IMPLEMENTATION.md` — `2f1af1b44114f155e03186dd73436a3a781cb9f2`
- `docs/PLUGIN_REQUIREMENTS.md` — `6f240c0e5c322869b67c311c6ef30416f40a513f`
- `docs/ERROR_MODEL.md` — `98247d5ced3c2cc7941f7931f90e3448832d485f`
- `docs/ZAA_INTEGRATION.md` — `67eccf4d49644806c9d0f076d7f7c15eb74b1ded`
- `docs/TEST_STRATEGY.md` — `53d03feb4bb0ce3010ffd7136f9fa4aabbe900af`
- `docs/QUALITY_GATES.md` — `ea88a8cc85d167b11868217cda7e7ce3194927fd`
- `docs/REVIEW_PROCESS.md` — `00b1658a1f25956f6fedf3b4583cce352499d680`
- `docs/ROADMAP.md` — `1917d36b8c6cd852d19a412a08f6d1de8161db8c`
- `docs/FULL_CONSISTENCY_AUDIT_2026-10-01.md` — `9f5ff12433b8f648b1501119514fdcaed7a57c42`

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

Before repository review or implementation:
1. fetch every listed path from the target branch;
2. require its Git blob SHA to match this manifest;
3. require ADR identifiers to remain unique;
4. require ADR-0010 to remain Superseded by ADR-0015.

Any mismatch invalidates this audited revision.

Do not silently proceed:
- inspect the changed file;
- re-run the affected consistency/technical review;
- create a new audit manifest if accepted.

## Why a blob manifest

During the documentation work, the GitHub branch-head endpoint intermittently exposed stale public history while connector file reads/writes reflected the active branch content.

Per-file Git blob SHAs identify the exact normative content set directly.

This manifest is the canonical revision reference for the 2026-10-01 Phase 0.5 repository-review handoff.
