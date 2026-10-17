"""Independent read-only preview contracts; mocks do not certify Orca runtime."""
from fractions import Fraction as F
from types import SimpleNamespace
import unittest
import importlib.util
from pathlib import Path
from unittest.mock import patch

from adaptive_subedge.engine import convex_chords
from smoothificator_preview.adapters import copy_model
from smoothificator_preview.limits import FRAME, MAX_VERTICES, MAX_TRIANGLES
from smoothificator_preview import application, ui
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from tests.unit.test_convex_chords import triangle_prism


class Matrix:
    def __init__(self, rows=None):
        self.rows = rows or [[1, 0, 0, 0], [0, 1, 0, 0],
                             [0, 0, 1, 0], [0, 0, 0, 1]]
        self.shape = (len(self.rows), len(self.rows[0]))

    def __getitem__(self, indices):
        i, j = indices
        return self.rows[i][j]


def model_fixture():
    source = triangle_prism()
    vertices = [[p.x_mm, p.y_mm, p.z_mm] for p in source.vertices]
    triangles = [list(t) for t in source.triangles]
    reads = []
    def vertex(i):
        reads.append(("vertex", i))
        return vertices[i]
    def triangle(i):
        reads.append(("triangle", i))
        return triangles[i]
    mesh = SimpleNamespace(vertex_count=lambda: len(vertices), triangle_count=lambda: len(triangles),
                           vertex=vertex, triangle=triangle)
    instance_matrix, volume_matrix = Matrix(), Matrix()
    instance = SimpleNamespace(is_printable=lambda: True, matrix=lambda: instance_matrix)
    volume = SimpleNamespace(is_model_part=lambda: True, matrix=lambda: volume_matrix, mesh=lambda: mesh)
    obj = SimpleNamespace(name="<model>&", instance_count=lambda: 1, volume_count=lambda: 1,
                          instance=lambda i: instance, volume=lambda i: volume)
    model = SimpleNamespace(object_count=lambda: 1, object=lambda i: obj)
    return SimpleNamespace(model=model, obj=obj, instance=instance, volume=volume, mesh=mesh,
                           vertices=vertices, triangles=triangles, reads=reads,
                           instance_matrix=instance_matrix, volume_matrix=volume_matrix)


def proposal_kwargs():
    return dict(axis="X", width_mm=.25, end_trim_mm=.125, chord_positions_mm=(.25,),
                algorithm_version="convex_axis_chords_v1", max_positions=64,
                max_vertices=512, max_triangles=512, max_mesh_pair_checks=130816,
                max_section_segments=512, max_section_pair_checks=130816,
                max_ray_directions=8, cancelled=lambda: False)


class PreviewEngineTests(unittest.TestCase):
    def test_same_call_section_and_legacy_proposal_parity(self):
        mesh = triangle_prism()
        expected = convex_chords.propose_convex_chords(mesh, .5, **proposal_kwargs())
        observed_sections = []
        original = convex_chords._section
        def capture(*args, **kwargs):
            result = original(*args, **kwargs)
            observed_sections.append(result.loop)
            return result
        with patch.object(convex_chords, "_embedding", wraps=convex_chords._embedding) as embedding:
            with patch.object(convex_chords, "_section", side_effect=capture):
                result = convex_chords.propose_convex_chord_preview(mesh, .5, **proposal_kwargs())
        self.assertEqual(embedding.call_count, 1)
        self.assertEqual(len(observed_sections), 1)
        self.assertIs(result.section, observed_sections[0])
        self.assertEqual(result.proposals, expected)
        self.assertEqual(result.section.command_z_mm, F(1, 2))
        self.assertEqual(result.proposals.proposals[0].end_xy_mm, (F(1, 2), F(1, 4)))

    def test_global_cancellation_has_no_partial_section_or_rows(self):
        result = convex_chords.propose_convex_chord_preview(
            triangle_prism(), .5, **(proposal_kwargs() | {"cancelled": lambda: True}))
        self.assertIsNone(result.section)
        self.assertEqual(result.proposals.proposals, ())
        self.assertEqual(result.proposals.reason, "cancelled")


class SnapshotAdapterTests(unittest.TestCase):
    def test_transform_order_and_detached_immutable_copy(self):
        f = model_fixture()
        f.volume_matrix.rows[0][3] = 1
        f.instance_matrix.rows[0][0] = 2
        f.instance_matrix.rows[1][3] = 3
        snapshot = copy_model(f.model)
        self.assertEqual(snapshot.frame, FRAME)
        self.assertEqual(snapshot.mesh.vertices[0].x_mm, 2)
        self.assertEqual(snapshot.mesh.vertices[0].y_mm, 3)
        self.assertEqual(snapshot.mesh.vertices[1].x_mm, 4)
        f.vertices[0][0] = 999
        f.triangles[0][0] = 999
        f.instance_matrix.rows[0][3] = 999
        self.assertEqual(snapshot.mesh.vertices[0].x_mm, 2)
        self.assertEqual(snapshot.mesh.triangles[0], triangle_prism().triangles[0])

    def test_mirror_is_applied_once(self):
        f = model_fixture()
        f.instance_matrix.rows[0][0] = -1
        result = copy_model(f.model)
        self.assertEqual(result.mesh.vertices[1].x_mm, -1)
        self.assertEqual(result.mesh.triangles, triangle_prism().triangles)

    def test_counts_precede_mesh_reads_and_matrix_copy(self):
        for field, limit in (("vertex_count", MAX_VERTICES), ("triangle_count", MAX_TRIANGLES)):
            with self.subTest(field=field):
                f = model_fixture()
                setattr(f.mesh, field, lambda: limit + 1)
                f.instance.matrix = lambda: self.fail("matrix read before count rejection")
                with self.assertRaises(ValueError):
                    copy_model(f.model)
                self.assertEqual(f.reads, [])
        for field in ("instance_count", "volume_count"):
            f = model_fixture()
            setattr(f.obj, field, lambda: 2)
            with self.assertRaises(ValueError):
                copy_model(f.model)
            self.assertEqual(f.reads, [])

    def test_unsupported_kind_printability_and_object_count(self):
        for target, field in (("model", "object_count"), ("instance", "is_printable"),
                              ("volume", "is_model_part")):
            f = model_fixture()
            setattr(getattr(f, target), field, lambda: 0)
            with self.assertRaises(ValueError):
                copy_model(f.model)
            self.assertEqual(f.reads, [])

    def test_bad_affine_matrix_and_shape_reject_before_vertex_reads(self):
        for rows in ([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 1, 1]],
                     [[float("nan"), 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
                     [[int(i == j) for j in range(5)] for i in range(5)]):
            with self.subTest(rows=rows):
                f = model_fixture()
                f.instance.matrix = lambda: Matrix(rows)
                with self.assertRaises(ValueError):
                    copy_model(f.model)
                self.assertEqual(f.reads, [])

    def test_fractional_and_boolean_triangle_indices_are_not_coerced(self):
        for value in (1.5, True):
            f = model_fixture()
            f.triangles[0][0] = value
            with self.assertRaises(ValueError):
                copy_model(f.model)


def request_message():
    return {"command": "generate", "z": "0.5", "axis": "X", "width": "0.25",
            "trim": "0.125", "positions": "0.25"}


class PreviewApplicationTests(unittest.TestCase):
    def test_closed_request_and_exact_numeric_rejections(self):
        request = application.parse_request(request_message())
        self.assertEqual((request.z_mm, request.width_mm, request.positions_mm), (.5, .25, (.25,)))
        cases = [None, [], {k: v for k, v in request_message().items() if k != "positions"},
                 request_message() | {"unknown": "field"}, request_message() | {"axis": "Z"},
                 request_message() | {"command": "execute"}, request_message() | {"z": True}]
        for field, bad in (("z", "nan"), ("width", "inf"), ("trim", "0"),
                           ("positions", "0,-0"), ("positions", "1,1.0"),
                           ("positions", "1,,2"), ("positions", "")):
            cases.append(request_message() | {field: bad})
        for value in cases:
            with self.subTest(value=value), self.assertRaises(ValueError):
                application.parse_request(value)

    def test_request_and_position_caps(self):
        for positions in (",".join(str(i) for i in range(65)), "1" * 9000):
            with self.assertRaises(ValueError):
                application.parse_request(request_message() | {"positions": positions})

    def test_worker_completes_from_copied_snapshot(self):
        snapshot = copy_model(model_fixture().model)
        request = application.parse_request(request_message())
        results = []
        job = application.PreviewJob(snapshot, request, lambda *args: results.append(args))
        job.start()
        job.thread.join(3)
        self.assertFalse(job.is_alive())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][:2], ("complete", "proposals-evaluated"))
        self.assertIsNotNone(results[0][2].section)

    def test_cancel_discards_even_computed_geometry(self):
        snapshot = copy_model(model_fixture().model)
        request = application.parse_request(request_message())
        valid = application.compute(snapshot, request, lambda: False)
        results = []
        job = application.PreviewJob(snapshot, request, lambda *args: results.append(args))
        job.cancel()
        with patch.object(application, "compute", return_value=valid):
            job._run()
        self.assertEqual(results, [("cancelled", "cancelled", None)])

    def test_deadline_is_incomplete_without_geometry(self):
        snapshot = copy_model(model_fixture().model)
        request = application.parse_request(request_message())
        results = []
        ticks = iter((0, 16, 16))
        job = application.PreviewJob(snapshot, request, lambda *args: results.append(args),
                                     clock=lambda: next(ticks))
        def work(snapshot, request, cancelled):
            self.assertTrue(cancelled())
            return None
        with patch.object(application, "compute", side_effect=work):
            job._run()
        self.assertEqual(results, [("incomplete", "time-limit", None)])

    def test_worker_expected_and_unexpected_errors_are_bounded(self):
        for error, expected in ((ContractError(ReasonCode.INVALID_GEOMETRY, "private path"),
                                 ("rejected", ReasonCode.INVALID_GEOMETRY.value, None)),
                                (ValueError("secret-model-text"), ("error", "ValueError", None))):
            results = []
            job = application.PreviewJob(None, None, lambda *args: results.append(args))
            with patch.object(application, "compute", side_effect=error):
                job._run()
            self.assertEqual(results, [expected])


class PreviewRendererTests(unittest.TestCase):
    def test_html_escapes_model_and_displays_source_and_unscored_chord(self):
        fixture = model_fixture()
        fixture.obj.name = '</h2><script>alert("x")</script>&'
        snapshot = copy_model(fixture.model)
        request = application.parse_request(request_message())
        preview = application.compute(snapshot, request, lambda: False)
        rendered = ui.render_result(snapshot, request, preview)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("<polygon ", rendered)
        self.assertIn("<line ", rendered)
        self.assertIn("未評価", rendered)
        self.assertIn(FRAME, rendered)

    def test_renderer_size_limit_rejects_instead_of_truncating(self):
        snapshot = copy_model(model_fixture().model)
        request = application.parse_request(request_message())
        preview = application.compute(snapshot, request, lambda: False)
        with patch.object(ui, "MAX_HTML_BYTES", 32), self.assertRaises(ValueError):
            ui.render_result(snapshot, request, preview)


class PreviewLifecycleTests(unittest.TestCase):
    def load_entrypoint(self):
        windows = []
        def create_window(**kwargs):
            window = SimpleNamespace(callbacks=kwargs, posted=[], open=True)
            window.post = lambda message: window.posted.append(message)
            window.is_open = lambda: window.open
            def close():
                window.open = False  # Host callback deliberately delivered later.
            window.close = close
            windows.append(window)
            return window
        fake_orca = SimpleNamespace(script=SimpleNamespace(ScriptPluginCapabilityBase=object),
            base=object, plugin=lambda cls: cls, register_capability=lambda cls: None,
            ExecutionResult=SimpleNamespace(success=lambda reason: reason, skipped=lambda reason: reason),
            host=SimpleNamespace(app_info=lambda: {"version": "2.5.0-dev", "build": "86905a8a"},
                                 model=lambda: model_fixture().model,
                                 ui=SimpleNamespace(create_window=create_window, message=lambda *a, **k: None)))
        spec = importlib.util.spec_from_file_location("smoothificator_preview._entrypoint_test",
            Path(__file__).parents[2] / "smoothificator_preview" / "entrypoint.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", {"orca": fake_orca}):
            spec.loader.exec_module(module)
        return module, windows

    def test_old_window_close_and_message_do_not_affect_reopened_window(self):
        module, windows = self.load_entrypoint()
        capability = module.CandidatePreview()
        with patch.dict("sys.modules", {"numpy": SimpleNamespace(__version__="2.2.6")}):
            capability.execute()
            capability.execute()
        self.assertEqual(len(windows), 2)
        windows[0].callbacks["on_close"]()
        self.assertFalse(capability.closed, "stale close must not close the new window")
        before = list(windows[1].posted)
        windows[0].callbacks["on_message"]({"command": "cancel"})
        self.assertEqual(windows[1].posted, before, "stale message must not change new window")

    def test_cancel_invalidates_already_dispatched_completion(self):
        module, windows = self.load_entrypoint()
        capability = module.CandidatePreview()
        with patch.dict("sys.modules", {"numpy": SimpleNamespace(__version__="2.2.6")}):
            capability.execute()
        callbacks = []
        class FakeJob:
            def __init__(self, snapshot, request, completed):
                callbacks.append(completed)
            def start(self): pass
            def cancel(self): pass
            def is_alive(self): return True
        with patch.object(module, "PreviewJob", FakeJob):
            capability.on_message(request_message())
        capability.on_message({"command": "cancel"})
        before = list(windows[0].posted)
        # Models a worker that passed its stop check just before UI cancellation.
        preview = application.compute(copy_model(model_fixture().model),
                                      application.parse_request(request_message()), lambda: False)
        callbacks[0]("complete", "proposals-evaluated", preview)
        self.assertEqual(windows[0].posted, before)
        self.assertEqual(windows[0].posted[-1]["state"], "cancelled")

    def test_cancel_then_busy_retry_leaves_generate_enabled_state(self):
        module, windows = self.load_entrypoint()
        capability = module.CandidatePreview()
        with patch.dict("sys.modules", {"numpy": SimpleNamespace(__version__="2.2.6")}):
            capability.execute()
        cancelled = []
        capability.job = SimpleNamespace(cancel=lambda: cancelled.append(True), is_alive=lambda: True)
        capability.on_message({"command": "cancel"})
        with patch.object(module, "PreviewJob", side_effect=AssertionError("overlapping worker")):
            capability.on_message(request_message())
        self.assertEqual(cancelled, [True])
        self.assertEqual(windows[0].posted[-1]["state"], "incomplete")
        self.assertNotIn(windows[0].posted[-1]["state"], ("running", "copying"))
        self.assertIn("busy", windows[0].posted[-1]["reason"])


if __name__ == "__main__":
    unittest.main()
