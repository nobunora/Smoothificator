# Current GUI native package readback — 2026-10-18

Disposition: **PASS for first-floor package/copy consistency only**. Scope is `artifacts/gui-angle0to30-trial-v2/trial-floor38-v1`, one insertion group and **two paths only**. This is not the proposed full26step coupon artifact. No geometry/contact/causal/physical acceptance follows from these checks. No reusable source/test, original input, GUI or device was changed.

## Exact identities

| Input/artifact | SHA256 |
|---|---|
| Immutable geometry project |6812137dc99250a48a20ebb4d90877e043c6ded567342d863af19eccaae83e0a|
| Genuine current GUI source archive |1d7143385b8be0d1fce4d68b8566cd493283d27f34a8db9586af1e1d9df6ca6e|
| Original current source |a6314651032bc7faa8ceda39440a4f5e20ccf5b0bfd615bde3e0e83313bc2f59|
| Producer binary |480b64a3a5e95e3b43ed5ff93f7490af4e57f4e3cf6f19d8c9a4e4b2c9906aba|
| First-floor plan record |e71b09fc594dd59104d52121902f425171c8c2fa36907f4f8bd443d2ac3a809d|
| First-floor WITH raw G-code |e01fbdd9bbb3d2b8f1ba94d4f39e037c05413ca7089c33c8422501c48515079e|
| First-floor WITH G-code3MF |3c5357a2b26bd14acec4c551575fa0f669728a223a8215c0d4add5b8bb84a94a|

All three input snapshot identities match `input-snapshots.json`; mutable GUI filenames still match their corresponding immutable snapshots at this check. The recipe loader independently pins source, archive, geometry and producer, rebinds selected-material profile, verifies plan/source/context and frozen plan identities. Fresh source-context identity is `fae80b7c7324d4e2022cc67d0435c94b756f2cf3107ae46b80a04ea9ba7204ef`.

## Checks executed

Two in-memory Python probes were executed with `.\.venv\Scripts\python.exe -` from repository root, both exit0. The first imported `recipe_from_plans` from the artifact driver, inspected the actual16-member old/new archives, used the bounded package reader for local/central/header/CRC and exact source/MD5 checks, compared every semantic ZipInfo field, independently enumerated changed contents/flags/compressed sizes against the JSON receipt, recovered original bytes by removing insertion spans, and freshly rebuilt recipe/copy/package with their actual owners. Final output: `FRESH_RECIPE_COPY_PACKAGE_EQUAL_PASS`. Fresh copy bytes equal actual raw bytes; fresh package bytes equal the actual container exactly.

Second probe checked snapshot hashes and mutable-name byte equality, printed exact old/new MD5, plan identity, stale-cache status and retained bbox. Original uppercase MD5 is `B44C07F9F35DF3DE1CCA9BF14C44937C`; WITH uppercase MD5 is `0867DF2ABF3FB3F2B1745E553CCE8381`. Both containers' embedded MD5 matches their corresponding embedded G-code.

Removing output bytes177081..178216 from the one declared insertion span restores the complete original source byte-for-byte. The closed changed-content list, in archive order, is exactly `Metadata/plate_1.gcode.md5`, `Metadata/plate_1.gcode`. All14 other members retain identical uncompressed bytes, CRC and uncompressed size. Archive/member comments, names/order, timestamps, extras, compression method, internal/external attributes, creator/extractor version/system, reserved and volume fields agree.

## Enumerated serialization exceptions

Flags changed2056→0 for all members except `Metadata/plate_1.gcode`, which changed8→0. Exact member names, in order: `[Content_Types].xml`, `Metadata/plate_1.png`, `Metadata/plate_1_small.png`, `Metadata/plate_no_light_1.png`, `Metadata/top_1.png`, `Metadata/pick_1.png`, `Metadata/plate_1.json`, `3D/3dmodel.model`, `Metadata/project_settings.config`, `Metadata/plate_1.gcode.md5`, `Metadata/plate_1.gcode`, `Metadata/_rels/model_settings.config.rels`, `Metadata/model_settings.config`, `Metadata/slice_info.config`, `Metadata/filament_sequence.json`, `_rels/.rels`. These clear only permitted descriptor/UTF8 bits on unchanged legal ASCII names.

| Member | Old compressed bytes | WITH compressed bytes |
|---|---:|---:|
|[Content_Types].xml|242|241|
|3D/3dmodel.model|399|400|
|Metadata/project_settings.config|12401|12400|
|Metadata/plate_1.gcode.md5|37|34|
|Metadata/plate_1.gcode|35606|35980|
|Metadata/slice_info.config|633|634|
|Metadata/filament_sequence.json|72|67|

These are all compressed-size differences. The two intended changed members naturally change compression; the other five are explicitly permitted stdlib recompression differences with equal content/CRC/file size. No compressed-byte identity is claimed.

## Retained metadata and limits

Time, filament estimates and thumbnails are retained cached values and **stale for supplementation**, explicitly labeled `retained-stale-time-filament-thumbnails`. Original settings still retain three material presets and actual used Basic material selection. Original plate metadata remains Textured Cool Plate, `filament_ids:[2]`, `first_extruder:2`; this is unchanged external representation, not a claim of physical tool index2. Retained `bbox_all` is XY `[75,80,105,100]`; fresh builder's inserted-motion containment passed. This package check does not independently establish geometric support, upper-parent chronology, collision freedom or bounds-owner correctness.

All physical/whole-job/printable authority fields remain false. Opaque OEM effects, startup, source/binary/firmware arc equivalence, original baseline execution and logical-counter translation remain recorded premises. No Orca loading, print selection, transmission or physical result was inspected here.

## Bounded rerun for the final artifact

Use the final directory supplied by the parent; keep immutable input paths/pins unchanged. Read its `trial-package.UNVERIFIED.json`, require all artifact/plan/source hashes to match actual bytes, inspect both archives with `_read_archive`, and compare the closed changed list, complete semantic ZipInfo fields, comments, unchanged CRC/file size, every permitted flag delta and every compressed-size delta against the receipt. Remove **all ordered insertion spans** and require exact source recovery. Then import `recipe_from_plans(receipt['plans_path'])`, call `rebuild_native_trial_copy(recipe,cancelled=lambda:False)` and `build_native_trial_package(...,copy_recipe=recipe,policy=NativePackagePolicy(expected_source_sha256,expected_gui_archive_sha256),cancelled=lambda:False)` entirely in memory; require copy and archive byte equality with the final published files. Report that artifact's actual group/path counts and hashes separately. Do not call `build`/writer or infer full-coupon/physical acceptance from the first-floor result. A changed source/geometry/producer requires fresh explicit identity review.

## Final actual artifact:26groups/70paths

Disposition: **PASS for final actual archive/copy consistency**, superseding first-floor-only scope for this section. Artifact directory is `artifacts/gui-angle0to30-trial-v2/trial-all26-v1`; actual merged plan is `planner-all26-merged-v1/plans.UNVERIFIED.json`. Immutable input pins are unchanged from the table above. This section does not certify geometry, contact, chronology, firmware or physical behavior.

| Final artifact | SHA256 |
|---|---|
| Merged26group plan |cd84832ca83097bb2a0ce708bfc63beabd0a19802a7d47ad6a03fcfc5d0edd9a|
| WITH raw G-code |5860e0f21eb5b94d9d2b21cd432d9ddcf64c47210b154db9324d7172a6429ec4|
| WITH G-code3MF |1c32ea351bb2f21dd5f79563d468e783eb844a0b76642da5db25b49130b7caf6|

Executed the bounded Python stdin probe with `.\.venv\Scripts\python.exe -`, exit0. It verified actual receipt/plan/raw/archive hashes, both16-member archives with the bounded reader, every semantic ZipInfo field and archive/member comments, the complete changed-content list, every flag and compressed-size difference, and equal unchanged CRC/file size/content. All26 insertion spans are ordered, nonempty and within the actual output. Removing them recovers the complete original source byte-for-byte. Fresh recipe reconstruction and direct owning copy/package rebuild ran entirely in memory and produced exact raw/archive byte equality. Final terminal marker: `FINAL26GROUP70PATH_FRESH_RECIPE_COPY_PACKAGE_EQUAL_PASS`. Fresh recipe independently contains26 insertions and70 paths, matching the receipt.

The closed changed-content inventory remains exactly `Metadata/plate_1.gcode.md5` and `Metadata/plate_1.gcode`; all14 other uncompressed contents remain exact. Original MD5 is `B44C07F9F35DF3DE1CCA9BF14C44937C`; final WITH uppercase MD5 is `5375FBB1979F943E98A94486831737CE`, matching embedded G-code. All16 permitted flag differences are identical to the full member list above:15members2056→0 and G-code8→0.

Final complete compressed-size differences:

| Member | Original compressed bytes | Final compressed bytes |
|---|---:|---:|
|[Content_Types].xml|242|241|
|3D/3dmodel.model|399|400|
|Metadata/project_settings.config|12401|12400|
|Metadata/plate_1.gcode.md5|37|34|
|Metadata/plate_1.gcode|35606|38955|
|Metadata/slice_info.config|633|634|
|Metadata/filament_sequence.json|72|67|

Retained time/filament/thumbnails remain explicitly stale. Fresh package rebuild again passed retained XY bbox containment. This establishes source/container identity and package serialization consistency for the actual26group/70path artifact; it is separate from geometry/contact/causal audits running elsewhere. No source/test/original edit, artifact rewrite, Orca action, printer transmission or physical operation was performed by this QA.

## Revised posthop artifact — current package consistency result

**Old `trial-all26-v1` is HELD due to the separate causal audit.** Its section above is historical package-consistency evidence only and is not final delivery approval. The replacement examined here is `trial-all26-posthop-v1`,26groups/70paths; geometry counts are unchanged. This report does not adjudicate the separate causal audit.

| Revised artifact | SHA256 |
|---|---|
| Posthop merged plan |18409c1b1093beb9ebaf3abde7e8a785351575f05d2357dabd9e2149baa3a3b3|
| Posthop WITH raw G-code |0173d90d7710c614839f167dff340c406875a1c65fefb3a2c24b46049e61926b|
| Posthop WITH G-code3MF |860001afafc396e7d3c8aa20f2ff5566553025a5b0bb0b4a5473fef11f05fc9b|

Re-executed the same bounded in-memory Python stdin probe using `.\.venv\Scripts\python.exe -`, exit0, against the actual revised container/raw and the plan named by its actual JSON receipt. Fresh recipe loading includes26 non-null original-floor witness offsets. Direct owning copy rebuild and direct package rebuild produce the actual raw and archive bytes exactly. Terminal marker: `POSTHOP26GROUP70PATH_FRESH_RECIPE_COPY_PACKAGE_EQUAL_PASS`. The owner therefore replayed its current restoration/profile/witness checks on the actual fresh inputs; this is not an independent firmware or causal proof.

All26 ordered insertion spans are within output bounds; stripping them restores original source SHA `a6314651032bc7faa8ceda39440a4f5e20ccf5b0bfd615bde3e0e83313bc2f59` exactly. Original genuine archive pin remains `1d7143385b8be0d1fce4d68b8566cd493283d27f34a8db9586af1e1d9df6ca6e`; geometry/producer pins remain the previously verified immutable inputs. Fresh recipe contains exactly26 insertions and70 paths.

The16-member semantic ZipInfo/comment checks, local/central header/CRC checks, uppercase MD5 and closed changed-member checks all pass. Revised WITH MD5 is `16AC2C32E8D4B215E8C8B5B8F79EBC16`. Changed contents remain only `Metadata/plate_1.gcode.md5` and `Metadata/plate_1.gcode`; all14 others retain bytes/CRC/file size. All16 flag differences remain exactly the previously enumerated permitted descriptor/UTF8 clears.

All revised compressed-size differences are: `[Content_Types].xml`242→241; `3D/3dmodel.model`399→400; `Metadata/project_settings.config`12401→12400; `Metadata/plate_1.gcode.md5`37→34; `Metadata/plate_1.gcode`35606→38927; `Metadata/slice_info.config`633→634; `Metadata/filament_sequence.json`72→67. This independent enumeration equals the actual receipt.

Disposition: **PASS for revised actual package/copy consistency only**. Cached time/filament/thumbnails remain stale; physical/whole-job authority remains false. No source/test/original/artifact rewrite, GUI action or device operation was performed. Final geometry/contact/causal findings and release/physical decisions remain separate gates.
