"""Actual thirty-ring intent, exact band and nearest-extrusion regressions."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
from hashlib import sha256
import json
import unittest

from tools.exponential_top_fixture import ROOT
from tools.prepare_executable_ring_intents import (
    _emission, prepare_ring_intents, radial_segment_in_band, select_ring_chords, synthetic_replay,
)
from tools.supplemental_z_hop import SupplementalPath, compose_retracted_cycle
from orca_plugin.gcode.linear_trace import _words, trace_linear_execution
from tests.unit.test_supplemental_z_hop import anchor_fixture


FOLDER = ROOT/'artifacts/revolved-exponential-review'


class ExecutableRingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = (FOLDER/'original-slice/sliced.3mf').read_bytes()
        cls.source = (FOLDER/'original-slice/plate_1.gcode').read_bytes()
        cls.manifest_bytes = (FOLDER/'current-review.json').read_bytes()
        cls.manifest = json.loads(cls.manifest_bytes)
        cls.intents = prepare_ring_intents(cls.project, cls.source, cls.manifest_bytes)

    def prepare_changed(self, manifest, **options):
        content = json.dumps(manifest).encode()
        return prepare_ring_intents(self.project, self.source, content,
                                    expected_manifest_sha256=sha256(content).hexdigest(), **options)

    def changed_manifest(self):
        return json.loads(self.manifest_bytes)

    def test_actual_all_thirty_radius_width_preserved_and_deterministic_divisors(self):
        self.assertEqual(len(self.intents.rings), 30)
        self.assertEqual(sum(len(r.path.points_mm)-1 for r in self.intents.rings), 5568)
        for ring, original in zip(self.intents.rings, self.manifest['rings']):
            self.assertEqual(ring.path.path_id, original['id'])
            self.assertEqual(ring.radius_mm, F(original['radius_exact_mm']))
            self.assertEqual(ring.path.width_mm, F(original['width_exact_mm']))
            expected = 96 if original['id'] in ('ring-2', 'ring-3') else 192
            self.assertEqual(len(ring.path.points_mm)-1, expected)
            self.assertEqual(ring.selected_endpoint_indices, tuple(range(0, 193, 192//expected)))
        self.assertEqual(self.intents, prepare_ring_intents(self.project, self.source, self.manifest_bytes))
        self.assertFalse(self.intents.printable_authorized)
        with self.assertRaises(FrozenInstanceError):
            self.intents.printable_authorized = True

    def test_original_fixed_height_failures_are_corrected_without_dropping(self):
        failed = []
        for ring in self.intents.rings:
            original = replace(ring.path, height_mm=ring.original_height_mm,
                points_mm=tuple((p[0], p[1], ring.original_top_z_mm) for p in ring.path.points_mm))
            anchor = replace(anchor_fixture(), xyz_mm=(F(90), F(90), ring.upper_z_mm))
            try:
                compose_retracted_cycle(anchor, (original,), ring.upper_z_mm, self.intents.policy)
            except ValueError:
                failed.append(ring.path.path_id)
        self.assertEqual(len(failed), 7)
        self.assertTrue(all(r.path.height_mm == r.path.points_mm[0][2]-r.path.floor_z_mm for r in self.intents.rings))
        self.assertTrue(all(r.spill_fraction <= F('.5') for r in self.intents.rings))

    def test_nearest_e192_failure_then96_success_without_special_case_search(self):
        grouped = {}
        for segment in self.manifest['candidate_segments']:
            grouped.setdefault(segment['ring_id'], []).append(segment)
        for ring in self.intents.rings[1:3]:
            segments = grouped[ring.path.path_id]
            xy = [segments[0]['start_mm']]+[s['end_mm'] for s in segments]
            points = tuple((F(str(p[0])), F(str(p[1])), ring.path.points_mm[0][2]) for p in xy)
            original = replace(ring.path, points_mm=points)
            with self.assertRaisesRegex(ValueError, 'width outside'):
                _emission(original, self.intents.policy, (F(90), F(90)), ring.radius_mm, F('.002'))
            selected, indices, rejected, _ = select_ring_chords(original, center=(F(90), F(90)),
                radius=ring.radius_mm, budget=F('.002'), policy=self.intents.policy)
            self.assertEqual(len(selected.points_mm)-1, 96)
            self.assertEqual(rejected[0][0], 192)
            self.assertEqual(indices, ring.selected_endpoint_indices)

    def test_exact_squared_band_accepts_boundary_rejects_nearby_and_clips_projection(self):
        center = (F(0), F(0))
        self.assertTrue(radial_segment_in_band((F(1), F(0)), (F(1), F(1)), center, F(1), F('.5')))
        self.assertFalse(radial_segment_in_band((F(-1), F(0)), (F(1), F(0)), center, F(1), F('.001')))
        self.assertFalse(radial_segment_in_band((F(1), F(0)), (F('1.000000001'), F(0)), center, F(1), F(0)))
        self.assertFalse(radial_segment_in_band((F(1), F(0)), (F(1), F(0)), center, F(1), F('.1')))
        self.assertTrue(radial_segment_in_band((F(1), F(0)), (F('1.1'), F(0)), center, F(1), F('.1')))
        with self.assertRaises(ValueError):
            prepare_ring_intents(self.project, self.source, self.manifest_bytes, radial_budget_mm=F('0.000000001'))

    def test_emitted_widths_positive_e_flow_cap_and_synthetic_composer_replay(self):
        self.assertTrue(all(min(r.emitted_e_mm)>0 for r in self.intents.rings))
        self.assertTrue(all(F('.25') <= r.minimum_emitted_width_mm <= r.maximum_emitted_width_mm <= F('.45') for r in self.intents.rings))
        self.assertTrue(all(r.maximum_volume_rate_mm3_s <= float(self.intents.policy.max_volume_mm3_s) for r in self.intents.rings))
        receipts = synthetic_replay(self.intents)
        self.assertTrue(receipts)
        self.assertTrue(all(r['exact_restore'] and not r['real_anchor_verified'] for r in receipts))
        for ring in self.intents.rings:
            anchor = replace(anchor_fixture(), xyz_mm=(F(90), F(90), ring.upper_z_mm))
            block = compose_retracted_cycle(anchor, (ring.path,), ring.upper_z_mm, self.intents.policy)
            trace = trace_linear_execution(block, initial_state=anchor)
            self.assertIsNone(trace.failure)
            self.assertEqual(trace.final_state, anchor)
            emissions = []
            for record in trace.records:
                _, words = _words(record.raw.decode().strip())
                if words.get('E', F(0)) > 0 and record.before.xyz_mm[:2] != record.after.xyz_mm[:2]:
                    emissions.append((words['E'], words['F']))
            self.assertEqual(tuple(e for e, _ in emissions), ring.emitted_e_mm)
            self.assertEqual(tuple(feed for _, feed in emissions), ring.emitted_feed_mm_min)

    def test_source_project_manifest_pin_and_association_mismatch_reject(self):
        for source, project, manifest in ((self.source+b'; stale', self.project, self.manifest_bytes),
                (self.source, self.project+b'stale', self.manifest_bytes),
                (self.source, self.project, self.manifest_bytes+b' ')):
            with self.assertRaisesRegex(ValueError, 'hash pin'):
                prepare_ring_intents(project, source, manifest)
        manifest = self.changed_manifest()
        manifest['source_slice_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'association'):
            self.prepare_changed(manifest)

    def test_malformed_duplicate_orphan_and_disconnected_graph_reject(self):
        for mode in ('duplicate-ring', 'duplicate-chord', 'missing', 'orphan', 'disconnected'):
            manifest = self.changed_manifest()
            if mode == 'duplicate-ring':
                manifest['rings'].append(manifest['rings'][0])
            elif mode == 'duplicate-chord':
                manifest['candidate_segments'][1]['chord_index'] = 1
            elif mode == 'missing':
                manifest['candidate_segments'].pop(0)
            elif mode == 'orphan':
                manifest['candidate_segments'][0]['ring_id'] = 'orphan'
            else:
                manifest['candidate_segments'][1]['start_mm'][0] += 1
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                self.prepare_changed(manifest)

    def test_overlap_minheight_saved_height_cap_ceiling_and_spill_reject(self):
        for mode in ('overlap', 'minheight', 'heightcap', 'ceiling', 'spill'):
            manifest = self.changed_manifest()
            if mode == 'overlap':
                manifest['overlap_percent_exact'] = '31'
            elif mode == 'minheight':
                manifest['rectangle_constraints_exact_mm']['minimum_remaining_height'] = '.1'
            elif mode == 'heightcap':
                manifest['rectangle_constraints_exact_mm']['maximum_physical_height'] = '.181'
            elif mode == 'ceiling':
                manifest['section_diagnostics'][0]['upper_z_exact_mm'] = '3.07'
                manifest['section_diagnostics'][0]['triangle_height_exact_mm'] = '.07'
            else:
                row = manifest['section_diagnostics'][0]
                row['triangle_base_exact_mm'] = '100'
                row['right_radius_exact_mm'] = '100'
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                self.prepare_changed(manifest)
