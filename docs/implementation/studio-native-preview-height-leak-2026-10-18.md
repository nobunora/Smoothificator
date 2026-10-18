# Studio native preview height leak investigation

Review-only; v7 rejected by user. No emitter change is authorized by this record.

The immutable source identifies OrcaSlicer 2.5.0-dev. Exact Studio source
v02.08.02.61 recognizes its own producer name only; load-file processing enables
producer-specific handling. Native role and Z-height comments are accepted
unconditionally. Forced layer-height/line-width comments are accepted only when
producer handling is disabled or the detected producer is BambuStudio.

Consequently restoring the four comment keys does not restore Studio's hidden
last-extruded-Z state when it treats Orca source as Unknown. Supplemental moving
extrusion updates that hidden Z. The next original extrusion infers a reduced
height from its Z minus the supplemental Z. A reduced source-semantic replay
independently found 1050 original moving-height changes; one original source line
4050 changes from nominal .2 to .011 after supplemental Z2.189 before Z2.2.
That reduced replay is source evidence, not a compiled/runtime parser-equivalence
claim. Parent is comparing original and supplemented GUI views.

Primary source: https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/GCode/GCodeProcessor.cpp
Local snapshot SHA256: 9c7a9fbaff71738324fbfb4bc3c5ef9e322688d8465b8fc5c630317393a4bf29

The source exposes no comment that resets hidden last-extruded-Z for Unknown
producer. A possible explicit compatibility adapter is a truthful comment naming
the native preview metadata dialect and preserving the original producer, rather
than claiming BambuStudio generated the file. Studio's preliminary comment scan
matches its product-name substring anywhere in the file, so an inserted adapter
comment would select native metadata parsing and also load the original embedded
configuration through consumer defaults/substitution. This is a material consumer
interpretation change requiring parent adjudication and fresh GUI verification.
It does not change firmware commands or original bytes, but those properties alone
do not establish unchanged preview geometry or statistics.

Proposed example, not implemented:
`; Smoothificator adapter: BambuStudio preview metadata dialect; original producer OrcaSlicer`

If approved, verify original moving path height/width and role before/after,
supplemental actual frozen dimensions, exact restoration of all recognized
metadata, source byte recovery, archive closed changed-member inventory, and real
Studio/Orca rendering. Preserve original archive/profile/temperatures and do not
reslice, send or print.


## Parent adjudication and implementation

Parent approved the exact truthful adapter comment, with the consumer config
extraction effect recorded in the handoff spec before implementation. Native
`enable_studio_native_metadata` defaults false and participates in immutable
emission identity. Enabled mode requires original Orca provenance plus frozen
annotations and emits the marker exactly once inside the first tracked insertion.
No firmware command changes. New focused tests cover disabled/enabled mode,
unique placement, source recovery, metadata preservation, fingerprint difference,
missing annotations/provenance rejection and the pinned external parser recurrence.
Authoritative focused suite passed 33 tests. Sources were refrozen and parent
notified to rerun full regression. Actual consumer preview acceptance remains a
separate gate. The new same-marker original-motion control is a diagnostic G-code
artifact, not a replacement for the immutable genuine original archive.
