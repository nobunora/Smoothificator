# Audited Canonical Revision Manifest — 2026-10-02

Purpose: freeze the exact normative document contents approved by the 2026-10-02 supplementary consistency/failure-mode audit.

Current Orca drift check:
`1a5f91d727f43d455b40ab475a00d622b34648e0`

Original deeper source baseline retained for detailed parity fixtures:
`789f848694b955d293ca6b277d1c8046aa6f7436`

## Core normative / governance blobs

- `AGENTS.md` — `dac97cb887b6e5765c067a901be70154a0850385`
- `docs/DOCUMENT_CONTRACT.md` — `05fa567b620f56547a4db26326475c869dc4fb3f`
- `docs/ADR_PROCESS.md` — `587fd4c7b0971c4e927482b5016c645e74c4e070`
- `docs/SPECIFICATION.md` — `5b1a15f5873504be030395c69480560d12f085d3`
- `docs/ARCHITECTURE.md` — `91deb4cf3a472d227e4997bb0ce40fea73f9ce57`
- `docs/IMPLEMENTATION.md` — `8d932c67e99d99486742b4094c8565ac30e5f425`
- `docs/PLUGIN_REQUIREMENTS.md` — `c186ebbf83a6fead4db2440aed10b75214843481`
- `docs/ERROR_MODEL.md` — `8dc8196ede2b5aec6faa8f3c08e52eb691f6eab7`
- `docs/ZAA_INTEGRATION.md` — `67eccf4d49644806c9d0f076d7f7c15eb74b1ded`
- `docs/TEST_STRATEGY.md` — `b03d8bf0a5ccd4900f4ae62d717580e4c85453e5`
- `docs/QUALITY_GATES.md` — `ea88a8cc85d167b11868217cda7e7ce3194927fd`
- `docs/REVIEW_PROCESS.md` — `00b1658a1f25956f6fedf3b4583cce352499d680`
- `docs/ROADMAP.md` — `8e1ba072b6358a29c73f529230bffd09aa96b044`
- `docs/FULL_CONSISTENCY_AUDIT_2026-10-02.md` — `e0f396f1e330a9ec2bdbfeaeff9192c329375490`

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
- `0032-chronological-material-state-and-support-order.md` — `81599b3a48ef52f300a987db3f12e4436f55b661`
- `0033-unified-final-tool-clearance-validation.md` — `f3c491f661cca9202cd747d243f4b82d263eb0ec`
- `0034-final-structural-deposition-revalidation.md` — `ffa355d8d1dfa5c246261c9e3da3f532097b8690`
- `0035-v1-gcode-modal-and-runtime-override-envelope.md` — `715706c24bda2ba8566aa36c5ca759176a0ac140`
- `0036-v1-timelapse-wrapping-and-object-cancellation-gates.md` — `f9a50bfa2da8525a5f829b6efeb05f8fdf7f8b7c`
- `0037-attempt-scoped-state-and-precommit-revalidation.md` — `1c111f8303f8bed71c40a554341d084e92ec561e`
- `0038-v1-simple-connected-topology.md` — `f9949e56396b17e06a4029a14e26e3d08e924579`
- `0039-disable-unreplicated-extrusion-rate-smoothing-v1.md` — `b2fd7c31513c66b52a3ce845dd892863ba3e3636`
- `0040-v1-inherited-acceleration-gate.md` — `8da6cd8f331200c058ab20d55a2520dce638589b`
- `0041-postprocess-metadata-and-progress-limitation.md` — `65d2f6f90d6b025bd221f8182cafef04ed07b9ee`

## Verification rule

Before repository review or implementation:
1. fetch every listed path;
2. require its Git blob SHA to match;
3. require ADR identifiers unique 0001–0041;
4. require ADR-0010 to remain Superseded by ADR-0015.

Any mismatch invalidates this audited revision and requires focused re-audit.

## Why a blob manifest

The GitHub branch-head endpoint has previously exposed stale public history while connector file reads/writes reflected active branch content.

Per-file blob SHAs identify the exact normative content set directly.

This manifest is the canonical revision reference for the 2026-10-02 Phase 0.5 handoff.
