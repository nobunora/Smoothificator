"""Whole-solid support-function bounds on exact unnormalized axes."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
from hashlib import sha256
import json
import unittest

from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.engine.support_cell import query_exact_nominal_bead_projection
from tests.unit.test_nominal_bead_overlap import bead
from tools.exponential_top_fixture import ROOT


def query(segment=None, axis=(F(1), F(0), F(0)), **options):
    arguments = dict(max_coordinate_bits=4096, sqrt_fraction_bits=128, cancelled=lambda: False)
    arguments.update(options)
    return query_exact_nominal_bead_projection(segment or bead(start=('0', '0', '1'),
        end=('4', '0', '1'), width='2', height='1'), axis, **arguments)


class NominalBeadProjectionTests(unittest.TestCase):
    def test_actual_341_pinned_pair_axes_reproduce_strict_certificates(self):
        folder = ROOT/'artifacts/revolved-exponential-derived5000-9-seam0-v2-research'
        pins = ((folder/'nominal-model-rows.json', '46c23686ef31072f9ba0dec968603325f55477fa966fd0414df9ad4340fddb1b'),
                (ROOT/'artifacts/print-source-inspection/source-offset-candidate-budget100k.json',
                 '2b4af8efc9d1cba5dff24e4871096d4f3162ba4fcd941578cc98a79e2b922dbf'),
                (ROOT/'artifacts/print-source-inspection/source-offset-future-separation.json',
                 'cc70ab46be497d8c170914acd6e5278568399acd313f6ca85717511448866cad'))
        contents = []
        for path, digest in pins:
            content = path.read_bytes()
            self.assertEqual(sha256(content).hexdigest(), digest)
            contents.append(json.loads(content))
        rows, candidates, reference = contents
        by_line = {row['line']: row for row in rows}
        self.assertEqual(len(reference['certificates']), 341)
        for certificate in reference['certificates']:
            index, line = certificate['candidate_segment'], certificate['future_line']
            c, row = candidates['segments'][index-1], by_line[line]
            candidate = bead(f'candidate-{index}', c['start'], c['end'], c['width_from_E'], c['height'])
            future = bead(f'future-{line}', row['start'], row['end'], row['width'], row['height'])
            axis = tuple(map(F, certificate['axis']))
            a, b = query(candidate, axis), query(future, axis)
            self.assertEqual(a.state, 'bounded')
            self.assertEqual(b.state, 'bounded')
            margin = max(a.lower_dot_units-b.upper_dot_units, b.lower_dot_units-a.upper_dot_units)
            self.assertGreater(margin, 0)
            self.assertEqual(margin, F(certificate['strict_separation_margin_dot_units']))

    def test_cardinal_flat_caps_lateral_width_and_vertical_extent(self):
        for axis, expected in (((F(1), F(0), F(0)), (F(0), F(4))),
                               ((F(0), F(1), F(0)), (F(-1), F(1))),
                               ((F(0), F(0), F(1)), (F(0), F(1))),
                               ((F(1), F(1), F(0)), (F(-1), F(5)))):
            result = query(axis=axis)
            self.assertEqual(result.state, 'bounded')
            self.assertEqual((result.lower_dot_units, result.upper_dot_units), expected)
            self.assertEqual(result.axis_xyz, axis)
            with self.assertRaises(FrozenInstanceError):
                result.lower_dot_units = F(1)

    def test_oblique_reverse_and_unnormalized_axis_scaling(self):
        segment = bead(start=('0', '0', '1'), end=('3', '4', '1'), width='2', height='1')
        normal = (F(4), F(-3), F(0))
        result = query(segment, normal)
        self.assertEqual((result.lower_dot_units, result.upper_dot_units), (F(-5), F(5)))
        along = query(segment, (F(3), F(4), F(0)))
        self.assertEqual((along.lower_dot_units, along.upper_dot_units), (F(0), F(25)))
        reversed_segment = replace(segment, start_xyz_mm=segment.end_xyz_mm, end_xyz_mm=segment.start_xyz_mm)
        reversed_result = query(reversed_segment, normal)
        self.assertEqual((reversed_result.lower_dot_units, reversed_result.upper_dot_units), (F(-5), F(5)))
        scaled = query(segment, tuple(3*v for v in normal))
        self.assertEqual((scaled.lower_dot_units, scaled.upper_dot_units), (F(-15), F(15)))
        negative = query(segment, (F(-3), F(-4), F(0)))
        self.assertEqual((negative.lower_dot_units, negative.upper_dot_units), (-along.upper_dot_units, -along.lower_dot_units))

    def test_varying_z_and_rounded_vertical_normal_contribution(self):
        segment = bead(start=('0', '0', '1'), end=('3', '4', '2'), width='2', height='1')
        vertical = query(segment, (F(0), F(0), F(1)))
        self.assertEqual((vertical.lower_dot_units, vertical.upper_dot_units), (F(0), F(2)))
        tilted = query(segment, (F(3), F(4), F(2)))
        self.assertEqual((tilted.lower_dot_units, tilted.upper_dot_units), (F(0), F(29)))
        rounded = query(segment, (F(4), F(-3), F(1)))
        self.assertEqual(rounded.lower_dot_units+rounded.upper_dot_units, F(2))
        upper_sqrt = 2*(rounded.upper_dot_units-F(4))
        self.assertGreaterEqual(upper_sqrt**2, F(26))
        self.assertLess((upper_sqrt-F(1, 2**128))**2, F(26))

    def test_malformed_zero_nonexact_axis_and_bad_limits_reject(self):
        for axis in ((F(0), F(0), F(0)), [F(1), F(0), F(0)], (F(1), F(0)),
                     (1, F(0), F(0)), (float('nan'), F(0), F(0))):
            with self.subTest(axis=axis), self.assertRaises(ContractError):
                query(axis=axis)
        for options in ({'max_coordinate_bits': True}, {'sqrt_fraction_bits': 0},
                        {'sqrt_fraction_bits': 4097}, {'cancelled': None}):
            with self.subTest(options=options), self.assertRaises(ContractError):
                query(**options)
        with self.assertRaises(ContractError):
            query_exact_nominal_bead_projection(None, (F(1), F(0), F(0)),
                max_coordinate_bits=4096, sqrt_fraction_bits=128, cancelled=lambda: False)

    def test_resources_and_latched_cancellation_carry_no_bounds(self):
        for options in ({'max_coordinate_bits': 1}, {'cancelled': lambda: True}):
            result = query(**options)
            self.assertEqual(result.state, 'incomplete')
            self.assertIsNone(result.lower_dot_units)
            self.assertIsNone(result.upper_dot_units)
        calls = 0
        def cancelled():
            nonlocal calls
            calls += 1
            return calls == 2
        result = query(cancelled=cancelled)
        self.assertEqual(result.reason, 'cancelled')
        self.assertIsNone(result.lower_dot_units)
        with self.assertRaises(ContractError):
            query(cancelled=lambda: 1)
