# ADR-0068: Separate read-only model-world chord research preview

Status: Accepted
Date: 2026-10-17

ADR-0069 adds a separate, explicitly bounded native-viewer artifact mode. The
read-only contract below and its existing public APIs remain unchanged.

## Context and evidence

The user authorized the shortest runnable Orca research preview using the existing
unscored convex chord primitive. Existing printable/Plan preview contracts assume
centered PrintObject geometry and an immutable executable plan. Neither exists
for this unsliced model inspection. A separate coordinate/capability/package
contract is required; the non-runnable research archive remains unchanged.

Static Orca audit evidence is associated with revision
86905a8a20d5887f3b13017e66cd897766334bd3. The official
orca_inspector_plugin_any.py example demonstrates host.model()/object/volume
access and indexed mesh copies (413-455), model counts (320-369), ModelPart and
printability predicates (258,301), instance.matrix() @ volume.matrix() world
transform (450-455), and Script create_window lifecycle (1339-1373).
PluginHostApp.cpp:154-176 exposes an application-owned live GUI model, not an
immutable snapshot. on_message executes on the UI thread (example1375); window
post is thread-safe (1505-1506). Script has no demonstrated ctx.cancelled.
Further source verification at that same revision: PluginHostModel.cpp:146-150
defines instance_count()/volume_count(); 200-206 model.object_count()/object(index)
enumerates the whole model, without selected-plate filtering. Matrix methods at
69-70 and107-108 are respectively volume-to-object and object-to-world. Both
return copied 4x4 float64 arrays. PluginBindingUtils.hpp:95-105 constructs those
arrays and22-30 requires NumPy. PluginHostMesh.cpp:107 exposes mesh statistics'
manifold flag, not a substitute for fresh engine geometry validation. Thus the
preview does not silently restrict model counts to a selected plate or subtract
an unverified plate origin.
These are source/example contracts, not proof of a locally installed binary.
Runtime capabilities and the actual packaged interpreter must be checked.

## Decision and coordinate exception

Add a separately distributed Script/UI-only research preview. It reads exactly
one model object, one total printable instance and one ModelPart volume; any
additional object/instance/volume, unsupported kind or missing required binding
rejects. It never evaluates CSG, modifiers or slicer-generated geometry.

The adapter copies bounded immutable vertices/triangles and both 4x4 matrices
on the UI thread, validates finite affine matrices, and transforms copied points
by instance_matrix @ volume_matrix. The explicit frame is
orca_model_world_mm_v1, a model-world/plate-view frame. Do not assert a particular
plate-local origin or centered PrintObject parity. Matrix affine bottom row must
be exactly (0,0,0,1); resulting coordinates must be finite and topology/embedding
must pass the existing engine. Do not infer repairs or use source file geometry.

This is a narrow exception to the centered-domain convention: immutable generic
mesh/point/section/chord vocabulary may carry this frame only inside this isolated
research-preview flow, with an explicit frame label at the application/UI boundary.
No object from this flow enters PlanStore, plan hashing, analyzer callbacks,
structural paths, physical eligibility or G-code processing. Printable geometry
continues to require the existing centered-frame contract unchanged.

## Engine and immutable presentation contract

Add frozen slotted domain/convex_chords.ConvexChordPreview:

```python
ConvexChordPreview(section: MeshSectionLoop | None,
                   proposals: ConvexChordProposalSet)
propose_convex_chord_preview(...same arguments as propose_convex_chords...)
    -> ConvexChordPreview
```

Both public functions delegate to one private owner in engine/convex_chords.py.
Within a call, fresh embedding and exact symbolic section are evaluated once;
the displayed source section is exactly the section used for the proposals.
Do not obtain the display through the differently tolerant public section API.
Complete proposal sets require an exact section with the same Fraction command Z;
all-rejected but completed sets may display that section. Every global rejected/
incomplete result has section None and the existing empty proposal tuple. No
partial geometry escapes. Constructors check exact types/state matrix only, never proof.
Existing public propose_convex_chords results and all canonical bytes remain unchanged.

The application snapshot/report explicitly labels its model-world frame and
unscored status. HTML shows the original section and proposed chord centerlines,
axes/units, explicit input values, rejected positions/reasons and diagnostics.
It does not label them improved, printable, optimized or validated toolpaths.
No support/flow/material/time estimate or improvement percentage is fabricated.

## UI ownership, cancellation and bounds

The UI exposes Z, X/Y axis, width, end trim and comma-separated positions.
Initial sample values may derive from copied bounds but are clearly marked
research examples; only an explicit Generate action starts computation.
Every request is strictly parsed and validated; no eval or arbitrary execution.
Messages are a closed Generate/Cancel action vocabulary. Unrecognized fields,
oversized input, nonfinite values or malformed geometry reject without a worker.

Fixed named operational limits for this first preview distribution:
vertices512, triangles512, mesh_pair_checks130816, positions64,
section_segments512, section_pair_checks130816, ray_directions8,
worker_deadline_seconds15, request_utf8_bytes8192, rendered_html_bytes2097152.
These are computational limits, not material defaults. Count preflight precedes
mesh array copies and position parsing follows the existing bounded proposal
contract. Larger models are explicitly unsupported at this stage.

One application owner manages one active job per preview window. Copy all live
Orca data on the UI thread before dispatch; workers receive only immutable copies
and never call model bindings. An internal Event/token plus monotonic deadline
implements the existing callable cancellation interface. Close/Cancel cancels;
deadline expiry becomes incomplete/time-limit, not successful partial output.
New Generate while busy is refused or first cancels and waits for the existing
job to end; never overlap jobs. Reopening closes/cancels the old window first.

Status vocabulary: idle, copying, running, complete, rejected, incomplete,
cancelled, error. Engine reasons remain visible but bounded/escaped. Job-generation
IDs prevent stale worker messages from modifying a closed or newer window; these
IDs are UI lifecycle metadata, never Plan/Attempt IDs. Worker completion uses the
demonstrated thread-safe window.post path; UI/model work remains on the UI thread.
Expected ContractError failures report typed reason; unexpected exceptions end
the job in error with bounded sanitized diagnostics. Do not swallow as success.

All model names, user values and diagnostic strings are untrusted text and must
be HTML-escaped. Use fixed scripts/styles, no remote assets or external requests,
no raw insertion into script literals, href or event-handler attributes. Structured
data embedded in HTML must be JSON encoded with HTML-significant characters
escaped; SVG numeric attributes come only from validated finite rendering values.
Reject unsafe/nonfinite render conversion or output exceeding the size cap.

## Packaging and dependency review

Own the Orca boundary in smoothificator_preview/{adapters,ui,entrypoint}.py,
with bounded coordination/rendering there or a dedicated application module.
Add a separate wheel containing smoothificator_preview and required engine/domain
modules. Register only Script/UI capability; no slicing/postprocess hooks,
G-code reader/writer, PlanStore wiring or output mutation capability. Keep a distinct
package/distribution identity from the non-runnable research archive.

The existing research ZIP's allowlist and orca_plugin/__init__-only restriction
remain intact. The new package is excluded from that archive and inspected by a
separate preview-package allowlist. Architecture tests enforce preview adapter ->
application/engine/domain direction and prohibit engine imports of Orca/UI/filesystem.

NumPy is permitted solely at this adapter boundary because the official matrix()
binding returns NumPy arrays. Indexed vertex access alone does not eliminate that
requirement. NumPy uses BSD-3-Clause; compiled wheel/platform maintenance and
security updates remain upstream dependency costs. Pin the exact version verified
against the target Orca Python3.12 Windows interpreter before distribution. Copy
values into built-in immutable tuples; do not move NumPy/live views into engine
workers. Missing/incompatible NumPy disables the preview, not an invented matrix
fallback. No additional dependency is authorized here.

## Validation, rollout and disable conditions

Fixture-test transformed cube/tetra/concave cases, unsupported counts/kinds,
matrix validation/mirroring, bounds preflight, exact source-section parity,
asynchronous cancellation/deadline/stale completion, safe HTML and package contents.
Verify the installed target's Script entrypoint, matrix binding and window bridge
before claiming Orca runtime success. A build/import/test alone is not UI evidence.
Failure disables this preview and leaves the user's model/slice/G-code unchanged.

This is an explicit isolated preview expansion, not relaxation of printable v1
gates. Alternatives rejected: presenting model-world proposals as executable Plan
preview, embedding a runnable capability into the existing research ZIP, guessing
missing bindings, or treating chord containment as finite-bead quality proof.
No prior ADR is superseded; existing physical/Plan contracts retain their scope.
