"""Pinned Orca Script-only entrypoint. No slicing or export capabilities."""
from threading import Lock
import sys
import orca

from .adapters import copy_model
from .application import parse_request, PreviewJob, BandRequest
from .ui import page, render_result, render_artifact_path
from .native_scene import ViewerSceneError
from .material_settings import load_policy, save_policy, presentation
from adaptive_subedge.application.empirical_material_settings import policy_from_message
from . import dimension_settings
from adaptive_subedge.application.smooth_dimension_settings import policy_from_message as dimension_policy_from_message

EXPECTED_VERSION = "2.5.0-dev"
EXPECTED_BUILD = "86905a8a"


class CandidatePreview(orca.script.ScriptPluginCapabilityBase):
    def __init__(self):
        super().__init__()
        self.window = None
        self.job = None
        self.generation = 0
        self.window_epoch = 0
        self.closed = True
        self.storage = None
        self.lock = Lock()

    def get_name(self):
        return "Smoothificator candidate preview (unscored)"

    def execute(self):
        self.on_close()
        if self.window is not None and self.window.is_open():
            self.window.close()
        try:
            app = orca.host.app_info()
            if app.get("version") != EXPECTED_VERSION or app.get("build") != EXPECTED_BUILD:
                raise ValueError("unsupported-runtime")
            import numpy
            if numpy.__version__ != "2.2.6":
                raise ValueError("unsupported-numpy-version")
            snapshot = copy_model(orca.host.model())
            self.storage = orca.host.plugin.storage()
            material_policy, material_path = load_policy(self.storage)
            dimension_policy, dimension_path = dimension_settings.load_policy(self.storage)
            html = page(snapshot, presentation(material_policy, material_path, saved=material_path.exists()),
                dimension_settings.presentation(dimension_policy, dimension_path, saved=dimension_path.exists()))
            with self.lock:
                self.closed = False
                epoch = self.window_epoch
            self.window = orca.host.ui.create_window(
                title="Smoothificator candidate preview — 未評価",
                html=html, width=1000, height=850,
                on_message=lambda msg: self.on_message(msg, epoch),
                on_close=lambda: self.on_close(epoch))
            print(f"SMOOTHIFICATOR_PREVIEW opened build={EXPECTED_BUILD} "
                  f"python={sys.version.split()[0]} numpy={numpy.__version__}", flush=True)
            return orca.ExecutionResult.success("Read-only candidate preview opened")
        except Exception as error:
            self.on_close()
            reason = str(error) if type(error) is ValueError else type(error).__name__
            orca.host.ui.message(reason[:160], title="Smoothificator preview unavailable",
                                 buttons="ok", icon="info")
            return orca.ExecutionResult.skipped("Preview unavailable")

    def on_close(self, epoch=None):
        with self.lock:
            if epoch is not None and epoch != self.window_epoch:
                return
            self.window_epoch += 1
            self.closed = True
            self.generation += 1
            if self.job is not None:
                self.job.cancel()

    def on_unload(self):
        self.on_close()
        if self.window is not None:
            self.window.close()

    def _post(self, generation, state, reason, html=""):
        with self.lock:
            if self.closed or generation != self.generation:
                return
            self.window.post({"generation": generation, "state": state,
                              "reason": reason, "html": html})

    def on_message(self, message, epoch=None):
        if self.closed or epoch is not None and epoch != self.window_epoch:
            return
        if type(message) is dict and message.get("command") == "save_dimension_policy":
            with self.lock:
                if self.closed or epoch is not None and epoch != self.window_epoch:
                    return
                try:
                    policy = dimension_policy_from_message(message)
                    policy, target = dimension_settings.save_policy(self.storage, policy)
                    self.window.post({"dimension_settings": dimension_settings.presentation(policy, target, saved=True)})
                except (ValueError, OSError) as error:
                    self.window.post({"dimension_error": str(error)[:160]})
            return
        if type(message) is dict and message.get("command") == "save_material_policy":
            # Serialize the small atomic settings commit with window close/reopen.
            with self.lock:
                if self.closed or epoch is not None and epoch != self.window_epoch:
                    return
                try:
                    policy = policy_from_message(message)
                    policy, target = save_policy(self.storage, policy)
                    self.window.post({"material_settings": presentation(policy, target, saved=True)})
                except (ValueError, OSError) as error:
                    self.window.post({"material_error": str(error)[:160]})
            return
        if message == {"command": "cancel"}:
            with self.lock:
                self.generation += 1
                if self.job is not None:
                    self.job.cancel()
            self._post(self.generation, "cancelled", "cancelled")
            return
        if self.job is not None and self.job.is_alive():
            self._post(self.generation, "incomplete", "busy — wait for cancellation/completion, then retry")
            return
        with self.lock:
            self.generation += 1
            generation = self.generation
        self._post(generation, "copying", "copying current model")
        try:
            request = parse_request(message)
            snapshot = copy_model(orca.host.model())
            config = storage = None
            if isinstance(request, BandRequest):
                from .native_scene import copy_viewer_config
                config = copy_viewer_config(orca.host.preset_bundle())
                storage = self.storage
            def completed(state, reason, result):
                html = ""
                try:
                    if result is not None:
                        html = render_result(snapshot, request, result)
                    if isinstance(request, BandRequest) and state == "complete" and result is not None:
                        from .native_scene import render_scene
                        from .viewer_artifact import write_scene
                        def cancelled():
                            return self.closed or generation != self.generation or job.cancelled()
                        if cancelled():
                            raise InterruptedError("cancelled")
                        content = render_scene(result, request, config)
                        path = write_scene(storage, content, cancelled)
                        # I/O stays cancellable; only final advertisement shares the
                        # generation lock. Unadvertised stale files are removed.
                        with self.lock:
                            if cancelled():
                                path.unlink(missing_ok=True)
                                raise InterruptedError("cancelled")
                            self.window.post({"generation": generation, "state": state,
                                "reason": reason, "html": render_artifact_path(path) + html})
                        print(f"SMOOTHIFICATOR_NATIVE Custom count={len(result.proposals)} "
                              f"width_mm={float(result.width_mm):.12g} saved=1", flush=True)
                        return
                    self._post(generation, state, reason, html)
                    rows = (result.proposals if isinstance(request, BandRequest)
                            else result.proposals.proposals) if result else ()
                    print(f"SMOOTHIFICATOR_PREVIEW result generation={generation} "
                          f"state={state} reason={reason} "
                          f"proposed={sum(r.state == 'proposed' for r in rows)}", flush=True)
                except InterruptedError:
                    self._post(generation, "incomplete", "cancelled-or-time-limit")
                except Exception as error:
                    self._post(generation, "error", str(error) if isinstance(error, ViewerSceneError) else type(error).__name__)
            job = PreviewJob(snapshot, request, completed)
            self.job = job
            self._post(generation, "running", "generating unscored candidates")
            self.job.start()
        except Exception as error:
            reason = str(error) if isinstance(error, ViewerSceneError) or type(error) is ValueError and str(error) in (
                "invalid-request", "position-limit", "invalid-numeric-input",
                "one-model-object-required", "one-instance-and-volume-required",
                "printable-model-part-required", "resource-limit") else type(error).__name__
            self._post(generation, "rejected", reason)


@orca.plugin
class PreviewPackage(orca.base):
    def register_capabilities(self):
        orca.register_capability(CandidatePreview)
