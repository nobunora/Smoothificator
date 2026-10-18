"""Assumed tip radius affects review sweep geometry, never emitted commands."""
from dataclasses import FrozenInstanceError
from fractions import Fraction as F
from hashlib import sha256
import json
import unittest

from tests.unit.test_print_source_inspection import fixture, settings_fixture
from tools.provisional_tool_geometry import ProvisionalPlanarTip, swept_planar_disc_bounds, swept_planar_polyline_bounds
from tools.review_supplemental_hops import review_hops


def review_fixture():
    settings = settings_fixture()
    settings.update(printable_height='180', z_hop=['.4'], travel_speed=['700'],
        machine_max_speed_x=['500', '200'], machine_max_speed_y=['500', '200'], machine_max_speed_z=['30', '30'])
    project, source = fixture(settings)
    manifest = {'source_slice_sha256': sha256(source).hexdigest(),
        'placed_project_sha256': sha256(project).hexdigest(),
        'rectangle_constraints_exact_mm': {'minimum_remaining_height': '.08',
            'maximum_physical_height': '.18', 'minimum_width': '.25', 'maximum_width': '.45'},
        'rings': [], 'candidate_segments': [],
        'section_diagnostics': [{'floor_z_exact_mm': '3', 'upper_z_exact_mm': '3.2'}]}
    for name, height, start in (('thin', '.08', [10.00049, 11.00051]),
                                ('thick', '.18', [-2.00049, -3.00051])):
        top = float(F(3)+F(height))
        a, b = [*start, top], [start[0]+1, start[1]+1, top]
        manifest['rings'].append({'id': name, 'chord_count': 2, 'floor_z_exact_mm': '3',
            'top_z_exact_mm': str(F(3)+F(height)), 'width_exact_mm': '.3', 'height_exact_mm': height})
        for index, (left, right) in enumerate(((a, b), (b, a)), 1):
            manifest['candidate_segments'].append({'ring_id': name, 'chord_index': index,
                                                   'start_mm': left, 'end_mm': right})
    return project, source, json.dumps(manifest).encode()


class ProvisionalToolTests(unittest.TestCase):
    def test_default_positive_exact_diameter_radius_identity_and_immutability(self):
        geometry = ProvisionalPlanarTip()
        self.assertEqual(geometry.assumed_diameter_mm, F('.4'))
        self.assertEqual(geometry.radius_mm, F('.2'))
        self.assertEqual(geometry.identity, ProvisionalPlanarTip(F(2, 5)).identity)
        self.assertNotEqual(geometry.identity, ProvisionalPlanarTip(F('.6')).identity)
        with self.assertRaises(FrozenInstanceError):
            geometry.assumed_diameter_mm = F(1)
        for bad in (0, F(0), F(-1), .4, '0.4', float('nan'), float('inf'), True):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                ProvisionalPlanarTip(bad)

    def test_pure_z_sweep_has_exact_touching_xy_bounds_and_no_axial_extension(self):
        start, end = (F(-1), F(2), F(3)), (F(-1), F(2), F(4))
        bounds = swept_planar_disc_bounds(start, end, ProvisionalPlanarTip())
        self.assertEqual(bounds.lower_xyz_mm, (F('-1.2'), F('1.8'), F(3)))
        self.assertEqual(bounds.upper_xyz_mm, (F('-.8'), F('2.2'), F(4)))
        self.assertEqual(bounds.upper_xyz_mm[0]-start[0], F('.2'))

    def test_oblique_negative_xy_sweep_uses_both_endpoints(self):
        start, end = (F(-3), F(2), F(4)), (F(1), F(-2), F(4))
        bounds = swept_planar_disc_bounds(start, end, ProvisionalPlanarTip(F('.6')))
        self.assertEqual(bounds.lower_xyz_mm, (F('-3.3'), F('-2.3'), F(4)))
        self.assertEqual(bounds.upper_xyz_mm, (F('1.3'), F('2.3'), F(4)))
        with self.assertRaises(ValueError):
            swept_planar_disc_bounds((-3, F(2), F(4)), end, ProvisionalPlanarTip())

    def test_complete_polyline_bounds_include_interior_extreme(self):
        points = ((F(0), F(0), F(2)), (F(-5), F(7), F(2)), (F(1), F(1), F(2)))
        bounds = swept_planar_polyline_bounds(points, ProvisionalPlanarTip())
        self.assertEqual(bounds.point_count, 3)
        self.assertEqual(bounds.lower_xyz_mm, (F('-5.2'), F('-.2'), F(2)))
        self.assertEqual(bounds.upper_xyz_mm, (F('1.2'), F('7.2'), F(2)))
        with self.assertRaises(ValueError):
            swept_planar_polyline_bounds(points[:1], ProvisionalPlanarTip())

    def test_review_geometry_changes_identity_bounds_not_commands_hops_or_source(self):
        inputs = review_fixture()
        original_hashes = tuple(sha256(content).hexdigest() for content in inputs)
        small = review_hops(*inputs)
        equivalent = review_hops(*inputs, assumed_tool_diameter_mm=F(2, 5))
        large = review_hops(*inputs, assumed_tool_diameter_mm=F('.6'))
        self.assertEqual(small['review_identity'], equivalent['review_identity'])
        self.assertNotEqual(small['review_identity'], large['review_identity'])
        self.assertFalse(small['assumed_vs_saved_nozzle_mismatch'])
        self.assertTrue(large['assumed_vs_saved_nozzle_mismatch'])
        self.assertEqual(large['saved_nozzle_diameter_mm'], F('.4'))
        for key in ('source_sha256', 'project_sha256', 'manifest_sha256', 'profile_z_hop_mm'):
            self.assertEqual(small[key], large[key])
        a = small['batches'][0]['transitions'][0]
        b = large['batches'][0]['transitions'][0]
        self.assertEqual(a['unverified_bridge_commands'], b['unverified_bridge_commands'])
        legs = a['provisional_tip_sweep_bounds']
        self.assertEqual(len(legs), 3)
        self.assertEqual(legs[0]['start_xyz_mm'], (F(10), F('11.001'), F('3.08')))
        self.assertEqual(legs[1]['end_xyz_mm'], (F(-2), F('-3.001'), F('3.6')))
        self.assertEqual(legs[2]['end_xyz_mm'], (F(-2), F('-3.001'), F('3.18')))
        self.assertEqual(a['unverified_bridge_commands'][1], 'G1 X-2.000 Y-3.001 F12000.000')
        for first, second in zip(legs, b['provisional_tip_sweep_bounds']):
            self.assertEqual(first['start_xyz_mm'], second['start_xyz_mm'])
            self.assertEqual(first['end_xyz_mm'], second['end_xyz_mm'])
            for axis in (0, 1):
                self.assertEqual(second['lower_xyz_mm'][axis], first['lower_xyz_mm'][axis]-F('.1'))
                self.assertEqual(second['upper_xyz_mm'][axis], first['upper_xyz_mm'][axis]+F('.1'))
            self.assertEqual(second['lower_xyz_mm'][2], first['lower_xyz_mm'][2])
            self.assertEqual(second['upper_xyz_mm'][2], first['upper_xyz_mm'][2])
        for key in ('printable_authorized', 'physical_print_authorized', 'complete_head_verified', 'tool_clearance_verified'):
            self.assertFalse(large[key])
        self.assertEqual(tuple(sha256(content).hexdigest() for content in inputs), original_hashes)
        self.assertEqual(len(small['supplemental_path_tip_bounds']), 2)
        for first, second in zip(small['supplemental_path_tip_bounds'], large['supplemental_path_tip_bounds']):
            self.assertEqual(first['path_id'], second['path_id'])
            self.assertEqual(first['quantized_centerline_sha256'], second['quantized_centerline_sha256'])
            self.assertEqual(first['swept_tip_bounds']['point_count'], 3)
            for axis in (0, 1):
                self.assertEqual(second['swept_tip_bounds']['lower_xyz_mm'][axis], first['swept_tip_bounds']['lower_xyz_mm'][axis]-F('.1'))
