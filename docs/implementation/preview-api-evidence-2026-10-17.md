# Pinned Orca read-only preview API evidence

This is static source evidence, not a live plugin acceptance result. The fixed
Orca revision is `86905a8a20d5887f3b13017e66cd897766334bd3`. No GUI operation,
installation, mesh extraction or NumPy installation was performed for this review.

## Model access and coordinates

Fixed upstream source:
<https://github.com/OrcaSlicer/OrcaSlicer/tree/86905a8a20d5887f3b13017e66cd897766334bd3/src/slic3r/plugin>

- `host/PluginHostModel.cpp:52`: `volume.is_model_part()`.
- `host/PluginHostModel.cpp:69-70,107-108`: volume-to-object and object-to-world
  `matrix()` return copied 4x4 float64 NumPy arrays. World transform is
  `instance.matrix() @ volume.matrix()`. No plate-origin subtraction occurs here.
- `host/PluginHostModel.cpp:146-150,200-206`: `instance_count()`, `volume_count()`,
  `model.object_count()` and `model.object(index)`. The model enumeration covers
  all model objects; it is not selected-plate filtering.
- `PluginBindingUtils.hpp:22-30,95-105`: `mat4_to_numpy` constructs an ndarray;
  missing NumPy raises ImportError. There is no NumPy-free matrix route established
  by these bindings. Once available, copy ndarray entries into builtin values.
- `host/PluginHostMesh.cpp:54-73,90-107`: array mesh access requires NumPy;
  `vertex(index)` and `triangle(index)` are bounds-checked NumPy-free access.
  `is_manifold()` exposes `mesh.stats().manifold()`, not full geometric validation.
- Local `artifacts/orca-source/PluginHostApp.cpp:154-176`: live GUI model references
  are owned by the application. Copy geometry and transforms on the UI thread
  before dispatching research calculations to a worker. Do not retain host objects.

This preview frame is model world, distinct from PrintObject centered slice space.
The older `docs/ORCASLICER_PLUGIN_RESEARCH.md` starts from a different source baseline;
it must not be treated as fresh binary compatibility evidence.

## HTML lifecycle

Local official example `artifacts/orca-source/orca_inspector_plugin_any.py`:

- Lines 413-455 demonstrate mesh access and the world transform above.
- Lines 1339-1373 implement ScriptPluginCapabilityBase and
  `orca.host.ui.create_window(title, html, width, height, on_message, on_close)`.
  The host-owned nonmodal window survives `execute()`; repeat execution closes
  the previous window.
- Lines 23-28 define `orca.postMessage` / `win.post` / `orca.onMessage` JSON bridge.
- Line 1375 states `on_message` runs on the UI thread; lines 1505-1506 state
  `win.post()` is thread-safe. Convert NumPy scalars to builtin values for JSON.

Script execution has no slicing `ctx.cancelled()` argument. A worker needs an
application cancellation token and stale-result protection, including window close.
These APIs do not replace the ordinary Orca slice preview or authorize G-code edits.

## Standard wheel installation

- Local `GUI_App.cpp:8816-8827`: file picker accepts `.py` / `.whl`, then calls
  `install_local_plugin_package`.
- Local `PluginLoader.cpp:79-88`: local installation root is
  `data_dir()/orca_plugins/<escaped source filename>/`.
- Fixed `PluginFsUtils.cpp:1061-1079`: wheel METADATA requires Name and Version.
- Lines 1082-1090 require WHEEL/Wheel-Version; 1114-1117 accept `py3-none-any`;
  1146-1153 require nonempty RECORD.
- Lines 1180-1193 select entry package using catalog metadata, then METADATA
  Import-Name, then unambiguous top_level.txt, then normalized Name; dependencies
  come from Requires-Dist. An `orca.plugins` entry_points group alone is not this
  loader's entry selection contract.
- Local `PluginLoader.cpp:204-209` imports that entry package from the wheel.

The preview distribution therefore contains ordinary `adaptive_subedge` and
`smoothificator_preview` packages, explicit Import-Name, NumPy dependency,
METADATA/WHEEL/RECORD, existing LICENSE and source/manifest SHA256 provenance.
Importing the preview entry registers its Orca capability. No embedded source ZIP
loader is needed. Runtime dependency installation and actual import remain separate
acceptance checks.
