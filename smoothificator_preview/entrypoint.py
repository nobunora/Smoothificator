"""Pinned Orca Script-only entrypoint. No slicing or export capabilities."""
from threading import Lock
import sys
import orca

from .adapters import copy_model
from .application import parse_request, PreviewJob
from .ui import page, render_result

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
            html = page(snapshot)
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
            def completed(state, reason, result):
                html = ""
                try:
                    if result is not None:
                        html = render_result(snapshot, request, result)
                    self._post(generation, state, reason, html)
                    print(f"SMOOTHIFICATOR_PREVIEW result generation={generation} "
                          f"state={state} reason={reason} "
                          f"proposed={sum(r.state == 'proposed' for r in result.proposals.proposals) if result else 0}", flush=True)
                except Exception as error:
                    self._post(generation, "error", type(error).__name__)
            self.job = PreviewJob(snapshot, request, completed)
            self._post(generation, "running", "generating unscored candidates")
            self.job.start()
        except Exception as error:
            reason = str(error) if type(error) is ValueError and str(error) in (
                "invalid-request", "position-limit", "invalid-numeric-input",
                "one-model-object-required", "one-instance-and-volume-required",
                "printable-model-part-required", "resource-limit") else type(error).__name__
            self._post(generation, "rejected", reason)


@orca.plugin
class PreviewPackage(orca.base):
    def register_capabilities(self):
        orca.register_capability(CandidatePreview)
