"""Pinned Orca scripts: preview and frozen prepared-file export, no live slicing."""
from threading import Lock, Thread, Event
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


class CalibrationMatrices(orca.script.ScriptPluginCapabilityBase):
    """Dedicated prepared-file capability; no model copy or live slicing."""
    def __init__(self):
        super().__init__()
        self.window=None;self.storage=None;self.bundle=None;self.closed=True
        self.lock=Lock();self.epoch=0;self.cancel=Event();self.worker=None

    def get_name(self):
        return "Smoothificator 校正マトリクス（実G-code）"

    def _state(self,current=None,reason=""):
        from .calibration_profile import compare_profile
        from .calibration_storage import load_selections
        bundle=self.bundle
        mismatches=compare_profile(dict(bundle.profile_hashes),current or {}) if bundle else ()
        return {"trials":[t.presentation() for t in bundle.trials] if bundle else [],
            "compatible":bool(bundle) and not mismatches,"mismatched_keys":mismatches,
            "selections":load_selections(self.storage,bundle) if bundle else {},
            "busy":bool(self.worker and self.worker.is_alive()),"reason":reason or ("準備済みデータを選択してください" if bundle else "準備済みデータは同梱されていません")}

    def _profile(self):
        from .calibration_profile import current_profile_hashes
        return current_profile_hashes(orca.host.preset_bundle())

    def execute(self):
        from .calibration_bundle import installed_bundle
        from .calibration_ui import page as calibration_page
        self.on_close()
        if self.window is not None and self.window.is_open():self.window.close()
        try:
            app=orca.host.app_info()
            if app.get("version")!=EXPECTED_VERSION or app.get("build")!=EXPECTED_BUILD:raise ValueError("unsupported-runtime")
            self.storage=orca.host.plugin.storage();self.bundle=installed_bundle()
            try:current=self._profile() if self.bundle else {}
            except (ValueError,RuntimeError):current={}
            html=calibration_page(self._state(current))
            with self.lock:
                self.closed=False;epoch=self.epoch;self.cancel=Event()
            self.window=orca.host.ui.create_window(title="Smoothificator 校正マトリクス",html=html,width=1100,height=900,
                on_message=lambda message:self.on_message(message,epoch),on_close=lambda:self.on_close(epoch))
            return orca.ExecutionResult.success("Prepared calibration library opened")
        except (ValueError,OSError) as error:
            self.on_close();orca.host.ui.message(str(error)[:160],title="校正データを開けません",buttons="ok",icon="info")
            return orca.ExecutionResult.skipped("Prepared library unavailable")

    def on_close(self,epoch=None):
        with self.lock:
            if epoch is not None and epoch!=self.epoch:return
            self.closed=True;self.epoch+=1;self.cancel.set()

    def on_unload(self):
        self.on_close()
        if self.window is not None:self.window.close()

    def _post(self,epoch,message):
        with self.lock:
            if not self.closed and epoch==self.epoch:self.window.post(message)

    def on_message(self,message,epoch=None):
        from .calibration_bundle import installed_bundle
        from .calibration_profile import compare_profile
        from .calibration_storage import export_trial,remove_created_export,save_selection
        with self.lock:
            if self.closed or epoch is not None and epoch!=self.epoch:return
            epoch=self.epoch
            if self.worker is not None and self.worker.is_alive():
                self.window.post({"reason":"書き出し中です。完了を待ってください"});return
        try:
            if type(message) is not dict or type(message.get("command")) is not str:raise ValueError("invalid-calibration-message")
            command=message['command'];keys={"command"}
            if command in ("calibration_export","calibration_baseline_export"):keys.add("trial_id")
            elif command in ("calibration_save_selection","calibration_save_proposal"):keys.update(("trial_id","cell_id","symptom"))
            elif command!="calibration_refresh":raise ValueError("unknown-calibration-command")
            if set(message)!=keys:raise ValueError("invalid-calibration-message-fields")
            bundle=installed_bundle()
            if bundle is None:raise ValueError("prepared-calibration-data-not-packaged")
            if self.bundle is None or bundle.bundle_sha256!=self.bundle.bundle_sha256:raise ValueError("prepared-data-changed-reopen-window")
            # Host config strings are copied/hashed only on this UI callback thread.
            try:current=self._profile()
            except (ValueError,RuntimeError):current={}
            if command=="calibration_refresh":self._post(epoch,{"state":self._state(current)});return
            trial=bundle.trial(message['trial_id'])
            if command in ("calibration_save_selection","calibration_save_proposal"):
                with self.lock:
                    if self.closed or epoch!=self.epoch:return
                    path,record=save_selection(self.storage,bundle,trial.id,message['cell_id'],message['symptom'],refine=command=="calibration_save_proposal")
                    self.window.post({"reason":("範囲の端または分解能の限界です。選択を保存し、オフラインでの範囲見直しを依頼しました。新しいG-codeは生成していません" if record.get("proposal",{}).get("status") in ("resolution_limit_offline_range_review_required","offline_range_expansion_review_required") else "提案のみ保存しました。新しいG-codeは生成していません") if command=="calibration_save_proposal" else "選択を保存しました", "paths":[str(path)],"state":self._state(current)})
                return
            baseline=command=="calibration_baseline_export"
            if not baseline and compare_profile(dict(bundle.profile_hashes),current):raise ValueError("current-source-header-keys-missing-or-mismatched")
            cancel=self.cancel;storage=self.storage
            def work():
                target=None
                try:
                    target,receipt=export_trial(storage,bundle,trial.id,baseline_only=baseline,cancelled=cancel.is_set)
                    with self.lock:
                        stale=self.closed or epoch!=self.epoch or cancel.is_set()
                        if not stale:self.window.post({"reason":"基準プロジェクトを書き出しました" if baseline else "同梱済み実G-codeをそのまま書き出しました（新規生成ではありません）", "paths":[str(target/f['filename']) for f in receipt['files']],"state":dict(self._state(current),busy=False)})
                    if stale:remove_created_export(target,storage)
                except (ValueError,OSError,InterruptedError) as error:
                    self._post(epoch,{"reason":str(error)[:160],"state":dict(self._state(current),busy=False)})
            self.worker=Thread(target=work,daemon=True)
            self._post(epoch,{"state":dict(self._state(current),busy=True)})
            self.worker.start()
        except (ValueError,OSError) as error:self._post(epoch,{"reason":str(error)[:160]})


@orca.plugin
class PreviewPackage(orca.base):
    def register_capabilities(self):
        orca.register_capability(CandidatePreview)
        orca.register_capability(CalibrationMatrices)
