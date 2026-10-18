"""Whole swept-disc certificates distinguish touch, penetration and unknown."""
from fractions import Fraction as F
import unittest

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from tools.audit_provisional_tip_sweep import PlanarTipSweepPolicy, audit_provisional_tip_sweep
from tools.provisional_tool_geometry import ProvisionalPlanarTip


def audit(start, end, **changes):
    kwargs = dict(policy=PlanarTipSweepPolicy(128, 4096, 128), cancelled=lambda: False)
    kwargs.update(changes)
    bead = ExactNominalTopSegment('material', (F(0), F(0), F(1)), (F(2), F(0), F(1)), F('.4'), F('.2'), 'structural')
    return audit_provisional_tip_sweep(tuple(map(F, start)), tuple(map(F, end)), ProvisionalPlanarTip(), bead, **kwargs)


class ProvisionalTipSweepTests(unittest.TestCase):
    def test_exact_top_contact_requires_shared_point_and_never_claims_clearance(self):
        result = audit(('.5', 0, 1), ('1.5', 0, 1))
        self.assertEqual(result.state, 'boundary-contact')
        self.assertEqual(result.boundary_or_penetration_witness_xyz_mm[2], F(1))
        # Projection-plane equality alone is insufficient to assert contact.
        ambiguous = audit(('.5', '.25', 1), ('1.5', '.25', 1))
        self.assertEqual(ambiguous.state, 'unknown')
        self.assertIsNone(ambiguous.boundary_or_penetration_witness_xyz_mm)

    def test_whole_sloped_sweep_cannot_use_safe_endpoint_only(self):
        result = audit((1, 1, '.7'), (1, -1, '1.1'))
        self.assertEqual(result.state, 'positive-penetration')
        self.assertEqual(result.boundary_or_penetration_witness_xyz_mm[2], F('.9'))
        safe = audit((1, 2, '.7'), (1, 3, '1.1'))
        self.assertEqual(safe.state, 'strictly-separated')

    def test_proposed_top_point_is_independently_verified_and_uses_correct_sloped_time(self):
        witness = ((F(1), F('.1'), F(1)),)
        contact = audit(('.5', '.25', 1), ('1.5', '.25', 1), proposed_top_witnesses=witness)
        self.assertEqual(contact.state, 'boundary-contact')
        self.assertEqual(contact.reason, 'global-top-plane-and-public-exact-top-witness')
        self.assertEqual(contact.point_queries, 1)
        fake = audit(('.5', '.25', 1), ('1.5', '.25', 1),
            proposed_top_witnesses=((F(1), F('.15'), F(1)),))
        self.assertEqual(fake.state, 'unknown')
        varying_z = audit((1, '.25', 2), (1, 2, 1), proposed_top_witnesses=witness)
        self.assertNotEqual(varying_z.state, 'boundary-contact')
        with self.assertRaises(ValueError):
            audit((1, 0, 1), (1, 0, 2), proposed_top_witnesses=((1, 0, 1),))

    def test_same_height_nonaxis_projection_can_prove_strict_separation(self):
        result = audit(('.5', '.32', 1), ('1.5', '.32', 1))
        self.assertEqual(result.state, 'strictly-separated')
        self.assertEqual(result.reason, 'exact-whole-swept-disc-projection')
        self.assertGreater(result.strict_margin, 0)
        self.assertGreater(result.axis_queries, 0)

    def test_exact_touch_endpoint_raise_and_resource_cancellation_unknown(self):
        self.assertEqual(audit((1, 0, 1), (1, 0, 2)).state, 'boundary-contact')
        for changes in (dict(cancelled=lambda: True), dict(policy=PlanarTipSweepPolicy(1, 4096, 128)),
                        dict(policy=PlanarTipSweepPolicy(128, 1, 128))):
            self.assertEqual(audit(('.5', '.32', 1), ('1.5', '.32', 1), **changes).state, 'unknown')
        with self.assertRaises(ValueError):
            audit((1, 0, 1), (1, 0, 2), cancelled=lambda: 0)
        with self.assertRaises(ValueError):
            audit((1, 0, 1), (1, 0, 2), proposed_axes=((1, 0, 0),))


if __name__ == '__main__':
    unittest.main()
