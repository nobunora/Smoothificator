"""Real exact-kernel pair-volume and future-source regression tests."""
from dataclasses import FrozenInstanceError, asdict, replace
from fractions import Fraction as F
from hashlib import sha256
import json
import unittest

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from adaptive_subedge.engine.support_cell import query_exact_nominal_top_point
from tools.audit_nominal_bead_overlap import BeadOverlapPolicy, audit_nominal_bead_overlap, reflected_bead
from tools.build_revolved_top_review import ring_vertices
from tools.exponential_top_fixture import ROOT
from tools.prepare_executable_ring_intents import SOURCE_SHA256, MANIFEST_SHA256
from tools.supplemental_z_hop import rounded


def bead(name='first', start=('0', '0', '2.2'), end=('1', '0', '2.2'), width='.4', height='.2'):
    return ExactNominalTopSegment(name, tuple(map(F, start)), tuple(map(F, end)), F(width), F(height), 'structural')


def policy(**changes):
    return replace(BeadOverlapPolicy(12, 4096, 4096, 128), **changes)


def audit(first=None, second=None, settings=None, cancelled=lambda: False):
    return audit_nominal_bead_overlap(first or bead(), second or bead('second'),
                                     policy=policy() if settings is None else settings, cancelled=cancelled)


def actual_outward_pair():
    folder = ROOT/'artifacts/revolved-exponential-review'
    source = (folder/'original-slice/plate_1.gcode').read_bytes()
    manifest_bytes = (folder/'current-review.json').read_bytes()
    if sha256(source).hexdigest() != SOURCE_SHA256 or sha256(manifest_bytes).hexdigest() != MANIFEST_SHA256:
        raise ValueError('actual regression source/manifest pin mismatch')
    manifest = json.loads(manifest_bytes)
    ring = next(row for row in manifest['rings'] if row['id'] == 'ring-25')
    center = tuple(manifest['center_mm'])
    top = F(ring['floor_z_exact_mm'])+F('.126')
    points = ring_vertices(center, F(ring['radius_exact_mm'])+F('.04'), top)
    start, end = tuple(tuple(rounded(v, 3) for v in point) for point in points[:2])
    candidate = ExactNominalTopSegment('outward-ring25-chord1', start, end,
        F(ring['width_exact_mm']), F('.18'), 'candidate')
    diagnostic_path = ROOT/'artifacts/print-source-inspection/outward-next-layer-geometry.json'
    diagnostic_bytes = diagnostic_path.read_bytes()
    if sha256(diagnostic_bytes).hexdigest() != 'dd2e359477fef64794f52cdbcf5949f93fd92b0073a0a501399a0ed3ae22f0de':
        raise ValueError('actual regression geometry diagnostic pin mismatch')
    diagnostic = json.loads(diagnostic_bytes)
    source_row = diagnostic['affected_source_segments'][0]
    if source_row['line'] != 14787 or source.splitlines()[14786].split(b';', 1)[0].split()[:1] != [b'G1']:
        raise ValueError('future source provenance line mismatch')
    if (source.splitlines()[14785] != b'G1 X98.405 Y90.413 E.02537'
            or source.splitlines()[14786] != b'G1 X98.405 Y89.602 E.02491'):
        raise ValueError('future source endpoint provenance mismatch')
    # Independent fixture record carries the explicit move endpoints and dimensions.
    future = bead('future-source-line14787', tuple(map(str, source_row['start'])),
                  tuple(map(str, source_row['end'])), str(source_row['width']), '.2')
    provenance = {'source_sha256': SOURCE_SHA256, 'manifest_sha256': MANIFEST_SHA256,
        'diagnostic_sha256': sha256(diagnostic_path.read_bytes()).hexdigest(),
        'source_line': 14787, 'chronology_owner': 'caller; future-source pair regression only',
        'candidate_recipe': 'original ring25 radius+0.04; h0.18; remaining0.126; original first endpoints then XYZ3',
        'first': asdict(candidate), 'second': asdict(future)}
    return candidate, future, provenance


class NominalBeadOverlapTests(unittest.TestCase):
    def assert_volume_witness(self, report):
        witnesses = [cell for cell in report.cells if cell.state == 'overlap']
        self.assertTrue(witnesses)
        for witness in witnesses:
            self.assertGreater(witness.cell.x_max_mm, witness.cell.x_min_mm)
            self.assertGreater(witness.cell.y_max_mm, witness.cell.y_min_mm)
            self.assertLess(witness.overlap_bottom_upper_mm, witness.overlap_top_lower_mm)

    def test_identical_and_partial_beads_prove_positive_volume(self):
        for second in (bead('second'), bead('second', start=('.5', '0', '2.3'), end=('1.5', '0', '2.3'))):
            report = audit(second=second)
            self.assertEqual(report.state, 'overlap-proven')
            self.assert_volume_witness(report)
            self.assertFalse(report.printable_authorized)
            self.assertFalse(report.physical_clearance_verified)
            with self.assertRaises(FrozenInstanceError):
                report.printable_authorized = True

    def test_separated_xy_z_and_exact_boundary_touching_are_not_volume(self):
        for second in (bead('second', start=('2', '0', '2.2'), end=('3', '0', '2.2')),
                       bead('second', start=('0', '0', '2.5'), end=('1', '0', '2.5')),
                       bead('second', start=('0', '0', '2.4'), end=('1', '0', '2.4')),
                       bead('second', start=('0', '.4', '2.2'), end=('1', '.4', '2.2')),
                       bead('second', start=('1', '0', '2.2'), end=('2', '0', '2.2'))):
            report = audit(second=second)
            self.assertEqual(report.state, 'disjoint-interiors')
            self.assertEqual(report.overlap_cells, 0)

    def test_oblique_and_reversed_orientation_keep_overlap(self):
        first = bead(start=('0', '0', '2.2'), end=('1', '1', '2.2'))
        second = bead('second', start=('1', '1', '2.2'), end=('0', '0', '2.2'))
        report = audit(first, second)
        self.assertEqual(report.state, 'overlap-proven')
        self.assert_volume_witness(report)

    def test_kernel_proves_disjoint_when_oblique_xyz_envelopes_overlap(self):
        first = bead(start=('0', '0', '2.2'), end=('1', '1', '2.2'))
        second = bead('second', start=('0', '1', '2.2'), end=('1', '2', '2.2'))
        report = audit(first, second)
        self.assertEqual(report.state, 'disjoint-interiors')
        self.assertGreater(report.kernel_queries, 0)
        self.assertEqual(report.unresolved_cells, 0)
        self.assertTrue(all(cell.state == 'disjoint' for cell in report.cells))

    def test_flat_caps_do_not_get_round_extension(self):
        report = audit(second=bead('second', start=('1.01', '0', '2.2'), end=('2', '0', '2.2')))
        self.assertEqual(report.state, 'disjoint-interiors')
        self.assertEqual(report.kernel_queries, 0)

    def test_varying_z_reflection_uses_existing_exact_kernel(self):
        first = bead(start=('0', '0', '2'), end=('1', '0', '2.4'))
        reflected = reflected_bead(first)
        self.assertEqual(reflected.start_xyz_mm[2], F('-1.8'))
        self.assertEqual(reflected.end_xyz_mm[2], F('-2.2'))
        query = query_exact_nominal_top_point(F('.5'), F(0), (reflected,), max_sources=1,
            max_coordinate_bits=4096, sqrt_fraction_bits=128, cancelled=lambda: False)
        self.assertEqual(query.top_z_lower_mm, F(-2))
        self.assertEqual(query.top_z_upper_mm, F(-2))
        report = audit(first, bead('second', start=('0', '0', '2.1'), end=('1', '0', '2.5')))
        self.assertEqual(report.state, 'overlap-proven')
        self.assert_volume_witness(report)

    def test_limits_cancellation_and_unresolved_work_do_not_pass(self):
        for settings in (policy(max_depth=0), policy(max_queries=3), policy(max_coordinate_bits=2)):
            report = audit(settings=settings)
            self.assertEqual(report.state, 'incomplete')
            self.assertFalse(report.printable_authorized)
        report = audit(cancelled=lambda: True)
        self.assertEqual(report.state, 'incomplete')
        self.assertTrue(report.cancelled)
        calls = 0
        def cancellation():
            nonlocal calls
            calls += 1
            return calls == 5
        report = audit(cancelled=cancellation)
        self.assertTrue(report.cancelled)
        self.assertEqual(report.state, 'incomplete')
        with self.assertRaisesRegex(ValueError, 'exact bool'):
            audit(cancelled=lambda: 1)
        report = audit()
        self.assertEqual(report.state, 'overlap-proven')
        self.assertGreater(report.unresolved_cells, 0)
        initial = report.overlap_xy_box
        area = lambda c: (c.x_max_mm-c.x_min_mm)*(c.y_max_mm-c.y_min_mm)
        self.assertEqual(sum(area(w.cell) for w in report.cells), area(initial))

    def test_malformed_types_duplicate_identity_and_policy_reject(self):
        with self.assertRaises(ValueError):
            audit(second=bead())
        with self.assertRaises(ValueError):
            audit_nominal_bead_overlap(None, bead(), policy=policy(), cancelled=lambda: False)
        for changes in ({'max_depth': True}, {'max_queries': 0}, {'max_coordinate_bits': .5},
                        {'sqrt_fraction_bits': 4097}, {'stop_after_overlap': 1}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                policy(**changes)

    def test_actual_outward_ring25_overlaps_future44_nominal_volume(self):
        candidate, future, provenance = actual_outward_pair()
        self.assertEqual(provenance['source_line'], 14787)
        report = audit(candidate, future)
        self.assertEqual(report.state, 'overlap-proven')
        self.assert_volume_witness(report)
