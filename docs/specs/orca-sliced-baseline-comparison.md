# Orca sliced-baseline Custom comparison (draft handoff)

Status: DRAFT_SPEC; implementation is not authorized by this document.
Authority under review: proposed ADR-0070. Existing Accepted ADR-0069
continues to forbid reading or appending an original G-code in its mode.
Canonical product revision: docs/AUDIT_REVISION_2026-10-16.json.

## Goal and boundary

For one explicitly selected offline slice and one candidate result, render
original sliced paths and generated Custom paths in the same native Orca
standard Preview, in the same target layer. The source file must remain
byte-identical. Produce only a disposable VIEW_ONLY derivative in plugin-owned
storage. No output/export/postprocess capability, printer connection, upload,
physical print or validated execution Plan is within this handoff.

## Required closure before SPEC_READY

1. Define how the source G-code is selected without invoking the GUI export or
   postprocess seam. The current Script/Pages host exposes no source path.
2. Define a source-to-candidate coordinate and slice identity proof for the
   supported offline fixture. A filename, model label or identical Z is not
   enough. Candidate production must use that proof or fail closed.
3. Define a bounded binary parser for nonfinal target-layer boundaries and all
   modal states needed to leave every later original command unchanged,
   including units, flow, retraction, forced tags, last-extruded-Z, wipe,
   flushing and skippable regions. Enumerate accepted commands and explicit
   refusal codes for the rest. Reject final-layer insertion in this first scope.
4. Define candidate placement, travel, extrusion and full state restoration,
   including XYZ/E modes, positions, feed, role, forced width and height. No insertion
   may generate another layer-change tag or change original moves.
5. Define source digest and identity rechecks, exclusive/atomic derivative
   publication, byte-exact source recovery from the derivative, bounded memory,
   cancellation cleanup and same-name reload avoidance.
6. Decide whether the derivative's normal printer commands create unacceptable
   accidental-output exposure despite VIEW_ONLY labeling. If it does, do not
   implement this route; retain the two existing separate views.

## Acceptance evidence when those decisions close

- A pinned-source repository review with `validated` disposition and no
  unresolved material input/API conflict.
- Parser fixtures covering single-tool conventional G-code, original mixed
  line endings, absolute/relative XYZ and E, retraction, feed restoration,
  exact target-layer insertion, and every unsupported command family.
- Source SHA256 and byte length unchanged on success, failure and cancellation;
  stripping only the inserted interval from the derivative reproduces the
  original bytes exactly.
- Native offline Orca Preview displays baseline and candidate Custom paths on
  the same layer. Candidate count, width and coordinates match the verified
  preview result. Later original moves remain identical after reparsing.
- No file is published on ambiguous state, stale source or failed validation.
  No physical-output or improvement claim follows from visual acceptance.

Current repository review disposition: **spec-change-required**. The fixed
Orca `SlicingPipelineContext.gcode_path` exists only at postprocess; that seam
also fires for export/upload and is outside this research mode. Manual local
file selection and same-slice coordinate provenance are not yet specified.
