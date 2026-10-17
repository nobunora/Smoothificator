"""Band request, visible footprint, and stale native-publication regressions."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from smoothificator_preview import application, ui
from smoothificator_preview.adapters import ModelSnapshot
from smoothificator_preview.limits import FRAME
from tests.unit import test_readonly_preview as legacy
from tests.unit.test_mesh_topology import cube


def snapshot_fixture():
    return ModelSnapshot(cube(), "fixture", FRAME)


def band_message():
    return dict(command="generate_band", z="0.5", axis="X", span_min="0.25", span_max="0.75",
                minimum_width="0.125", maximum_width="0.25", display_height="0.125", trim="0.125")


class BandApplicationTests(unittest.TestCase):
    def native_completion(self, folder):
        from smoothificator_preview import native_scene
        module, windows = legacy.PreviewLifecycleTests().load_entrypoint()
        module.orca.host.preset_bundle = lambda: None
        module.orca.host.plugin = SimpleNamespace(storage=lambda: folder)
        capability = module.CandidatePreview()
        with patch.dict("sys.modules", {"numpy": SimpleNamespace(__version__="2.2.6")}):
            capability.execute()
        # Web-window callbacks do not carry Orca's plugin audit context.
        # storage() must already have been captured by Script.execute().
        module.orca.host.plugin.storage = lambda: (_ for _ in ()).throw(RuntimeError("no plugin context"))
        now = [0.0]
        callbacks = []
        def make_job(snapshot, request, completed):
            job = application.PreviewJob(snapshot, request, completed, clock=lambda: now[0])
            job.start = lambda: None
            job.deadline = 15.0
            callbacks.append(completed)
            return job
        with patch.object(module, "PreviewJob", side_effect=make_job), \
                patch.object(native_scene, "copy_viewer_config", return_value=()):
            capability.on_message(band_message())
        preview = application.compute(snapshot_fixture(),
                                      application.parse_request(band_message()), lambda: False)
        return capability, windows[0], callbacks[0], preview, now

    def test_renderer_crossing_deadline_cannot_write_or_publish(self):
        from smoothificator_preview import native_scene
        with TemporaryDirectory() as folder:
            capability, window, completed, preview, now = self.native_completion(folder)
            def slow_render(*args):
                now[0] = 15.0
                return "; fixture\n"
            with patch.object(native_scene, "render_scene", side_effect=slow_render):
                completed("complete", "bands-proposed", preview)
            self.assertTrue(capability.job.cancelled())
            self.assertEqual(list(Path(folder).iterdir()), [])
            self.assertEqual(window.posted[-1]["state"], "incomplete")
            self.assertNotIn("complete", [p["state"] for p in window.posted])

    def test_cancel_during_write_is_observed_and_partial_file_removed(self):
        from smoothificator_preview import native_scene, viewer_artifact
        with TemporaryDirectory() as folder:
            capability, window, completed, preview, _ = self.native_completion(folder)
            actual_write = viewer_artifact.write_scene
            checks = 0
            def writing(root, content, cancelled):
                def checkpoint():
                    nonlocal checks
                    checks += 1
                    if checks == 3:
                        capability.on_message({"command": "cancel"})
                    return cancelled()
                return actual_write(root, content, checkpoint)
            with patch.object(native_scene, "render_scene", return_value="; fixture\n"), \
                    patch.object(viewer_artifact, "write_scene", side_effect=writing):
                completed("complete", "bands-proposed", preview)
            self.assertEqual(list(Path(folder).iterdir()), [])
            self.assertTrue(capability.job.stop.is_set())
            self.assertEqual(window.posted[-1]["state"], "cancelled")
            self.assertNotIn("complete", [p["state"] for p in window.posted])

    def test_postwrite_stale_artifact_is_removed_before_advertisement(self):
        from smoothificator_preview import native_scene, viewer_artifact
        with TemporaryDirectory() as folder:
            capability, window, completed, preview, _ = self.native_completion(folder)
            actual_write = viewer_artifact.write_scene
            def writing(root, content, cancelled):
                path = actual_write(root, content, cancelled)
                self.assertTrue(path.exists())
                capability.on_message({"command": "cancel"})
                return path
            with patch.object(native_scene, "render_scene", return_value="; fixture\n"), \
                    patch.object(viewer_artifact, "write_scene", side_effect=writing):
                completed("complete", "bands-proposed", preview)
            self.assertEqual(list(Path(folder).iterdir()), [])
            self.assertEqual(window.posted[-1]["state"], "cancelled")
            self.assertNotIn("complete", [p["state"] for p in window.posted])

    def test_request_contract_rejects_bad_bounds_and_extra_fields(self):
        request = application.parse_request(band_message())
        self.assertIsInstance(request, application.BandRequest)
        for changes in ({"extra": "1"}, {"span_min": "0.75"}, {"maximum_width": "0.01"},
                        {"display_height": "nan"}, {"trim": "0"}, {"z": False}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                application.parse_request(band_message() | changes)

    def test_worker_and_width_scaled_render(self):
        snapshot = snapshot_fixture()
        request = application.parse_request(band_message())
        completed = []
        job = application.PreviewJob(snapshot, request, lambda *args: completed.append(args))
        job.start()
        job.thread.join(3)
        self.assertFalse(job.is_alive())
        state, reason, preview = completed[0]
        self.assertEqual((state, reason), ("complete", "bands-proposed"))
        self.assertEqual(len(preview.proposals), 2)
        html = ui.render_result(snapshot, request, preview)
        self.assertIn('stroke-width="130"', html)
        self.assertIn("本数：2", html)
        self.assertIn("平面上の共通被覆範囲", html)
        self.assertIn("maximum_width", ui.page(snapshot))
        self.assertIn("&lt;", ui.render_artifact_path(Path("<unsafe>")))

    def test_infeasible_band_render_does_not_need_width(self):
        snapshot = snapshot_fixture()
        request = application.parse_request(band_message() | {"display_height": "0.3"})
        preview = application.compute(snapshot, request, lambda: False)
        self.assertEqual(preview.state, "rejected")
        self.assertNotIn("<line ", ui.render_result(snapshot, request, preview))

    def test_cancelled_completion_cannot_publish_native_file(self):
        from smoothificator_preview import native_scene, viewer_artifact
        module, windows = legacy.PreviewLifecycleTests().load_entrypoint()
        module.orca.host.preset_bundle = lambda: None
        module.orca.host.plugin = SimpleNamespace(storage=lambda: "unused-storage")
        capability = module.CandidatePreview()
        with patch.dict("sys.modules", {"numpy": SimpleNamespace(__version__="2.2.6")}):
            capability.execute()
        callbacks = []
        class FakeJob:
            def __init__(self, snapshot, request, completed): callbacks.append(completed)
            def start(self): pass
            def cancel(self): pass
            def is_alive(self): return True
        with patch.object(module, "PreviewJob", FakeJob), patch.object(native_scene, "copy_viewer_config", return_value=()):
            capability.on_message(band_message())
        capability.on_message({"command": "cancel"})
        preview = application.compute(snapshot_fixture(),
                                      application.parse_request(band_message()), lambda: False)
        before = list(windows[0].posted)
        with patch.object(native_scene, "render_scene", return_value="fixture"), \
                patch.object(viewer_artifact, "write_scene", side_effect=AssertionError("stale write")):
            callbacks[0]("complete", "bands-proposed", preview)
        self.assertEqual(windows[0].posted, before)


if __name__ == "__main__":
    unittest.main()
