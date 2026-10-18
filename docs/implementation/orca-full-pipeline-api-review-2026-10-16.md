# Orca full-pipeline API review — 2026-10-16

## Disposition and evidence boundary

The inspected API supports an immutable snapshot at `posSimplifyPath` and a separate Orca-hosted HTML preview. It does not establish complete production injection compatibility.

This review is **static source evidence only**. No new live Orca callback, GUI action, installation, cancellation test, or generated-file test was performed. The local source files under `artifacts/orca-source/` are the previously collected audit copy associated with Orca revision `86905a8a20d5887f3b13017e66cd897766334bd3`. This review did not freshly authenticate their upstream hashes or prove that a currently running executable matches them. Runtime activation must separately verify the exact build and required bindings.

## Snapshot route and ownership

The source-supported route is `ctx.object.layers()` → `layer.regions()` → `region.perimeters.flatten_paths()` / `region.fills.flatten_paths()`. Copy path coordinates, role, width, height, flow, layer geometry, resolved configuration, source mesh and transforms into application-owned immutable records before returning from `execute(ctx)`.

- `artifacts/orca-source/PluginHostSlicing.cpp:91–100`: graph references and NumPy views are valid only during `execute(ctx)`; container mutators can invalidate them earlier.
- `artifacts/orca-source/PluginHostSlicing.cpp:170–195`: `flatten_paths()` avoids unregistered polymorphic tree-node limitations; `ExtrusionPath.points()` supplies a read-only int64 `(N,3)` NumPy view, requiring NumPy.
- `artifacts/orca-source/PluginHostSlicing.cpp:227–241`: recursive leaf-path extraction.
- `artifacts/orca-source/PluginHostSlicing.cpp:326–338`: Print-owned `model_object()` and NumPy-dependent `trafo()`.
- `artifacts/orca-source/PluginHostSlicing.cpp:352–357`: use `ctx.print.model()`, never live GUI `orca.host.model()` in slicing callbacks.
- `artifacts/orca-source/SlicingPipelinePluginCapability.cpp:48–51`: convert scaled coordinates using `orca.slicing.unscale()`; the scale can vary, so a fixed conversion constant is not justified.
- `artifacts/orca-source/SlicingPipelinePluginCapability.hpp:39–41` and `artifacts/orca-source/PluginHooks.cpp:67–70`: slicing callbacks run on the slicing worker; UI calls can deadlock and are prohibited.

The earlier diagnostic result reported NumPy unavailable; that is historical evidence, not a new observation in this review. Required extraction remains unverified until NumPy is available and tested in the exact Orca runtime. The official example declares `dependencies = ["numpy"]` (`artifacts/orca-source/orca_inspector_plugin_any.py:3`); `artifacts/orca-source/PluginLoader.cpp:275` calls dependency installation. This establishes an installation mechanism, not a completed installation or dependency approval.

## Preview decision

Use the originally specified **separate Orca-hosted HTML plugin preview**, populated from the exact selected immutable plan and attempt summary. Do not label the ordinary Orca slice preview as the modified result.

`artifacts/orca-source/SlicingPipelinePluginCapability.cpp:34–39` explicitly states that postprocess output is not reflected in the normal G-code preview: the viewer maps the pre-postprocess file. The inspected Plater bindings (`artifacts/orca-source/PluginHostApp.cpp:158–188`) expose no preview replacement method. This is consistent with `docs/PLUGIN_REQUIREMENTS.md`, section 23.

The official Script example demonstrates `orca.host.ui.create_window(title=..., html=..., on_message=..., on_close=...)` at `artifacts/orca-source/orca_inspector_plugin_any.py:1339–1379`. Its nonmodal window survives `execute()`; capability instances persist across executions, so previous windows must be closed or reused deliberately. Page messages use `orca.postMessage`; responses use `win.post` and `orca.onMessage` (`:25–44`). `on_message` runs on the UI thread; `win.post` is thread-safe (`:1505–1506`). The project prohibition on UI calls from slicing callbacks still applies: UI-triggered reads of the immutable store are the supported application boundary. NumPy scalars must be converted to builtin numbers before UI serialization (`:73`).

## Postprocess and cancellation gap

At `psGCodePostProcess`, `ctx.print` and `ctx.object` are null; the plugin receives a working-file path, export host and output name. It runs after classic postprocess scripts and can run repeatedly for one slice on separate working copies (`artifacts/orca-source/SlicingPipelinePluginCapability.hpp:20–30`; `.cpp:34–39`). Resolved configuration remains accessible through `ctx.config_value()` via `full_config` (`.cpp:80–90`). No live graph may be inferred at this seam.

**`ctx.cancelled()` does not provide postprocess cancellation evidence.** Its implementation is `return print && print->canceled()` (`artifacts/orca-source/SlicingPipelinePluginCapability.cpp:16`); with null Print it returns false. The existing diagnostic probe's checks of this method therefore do not certify cancellation during export. A separately verified cancellation protocol or an explicitly unsupported cancellation-sensitive operation is required before claiming that acceptance condition complete.

## Remaining acceptance work

- Verify the exact runtime build and required bindings, install/document the necessary dependency, and acquire a real immutable snapshot without retaining Orca objects.
- Exercise the HTML preview against the exact plan identity, including stale selection and lifecycle behavior.
- Verify postprocess configuration, repeated exports, original-file preservation, failure handling and the cancellation limitation with real runtime evidence.
- Complete geometry, profile, clearance and output certification independently. API presence and a visible preview do not establish printable compatibility; unknown compatibility remains analysis-only under `docs/PLUGIN_REQUIREMENTS.md`.

No implementation source was changed by this review.
