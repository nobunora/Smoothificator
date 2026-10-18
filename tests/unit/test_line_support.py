"""All-real-X interval coverage, exact joins and genuine narrow holes."""
from fractions import Fraction as F
import unittest

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from tools.audit_line_support import audit_line, minimum_centerline_support, _root_bounds


def bead(name,ax,ay,bx,by,z='1',width='.42',height='.2'):
    return ExactNominalTopSegment(name,tuple(map(F,(ax,ay,z))),tuple(map(F,(bx,by,z))),
                                 F(width),F(height),'structural')


class LineSupportTests(unittest.TestCase):
    def test_rational_perfect_root_is_exact_not_inward_dyadic(self):
        self.assertEqual(_root_bounds(F('1.79')**2),(F('1.79'),F('1.79')))

    def test_exact_shared_boundary_does_not_become_artificial_gap(self):
        sources = (bead('vertical','0','-1','0','.79'),
                   bead('horizontal','.21','0','2','0'))
        for model in ('nominal','diamond'):
            report = audit_line(F('-.21'),F(2),F(0),F('.9'),sources,model=model)
            self.assertEqual(report['state'],'full-centerline-intersection-proven')

    def test_real_small_axial_gap_is_preserved(self):
        sources = (bead('left','0','0','.501','0'),bead('right','.502','0','1','0'))
        report = audit_line(F(0),F(1),F(0),F('.9'),sources)
        self.assertEqual(report['state'],'gap-proven')
        self.assertEqual(report['gap_intervals_exact_mm'],[['501/1000','251/500']])

    def test_lower_source_can_bridge_projection_without_trimming(self):
        sources = (bead('left','0','0','.501','0'),bead('right','.502','0','1','0'),
                   bead('base','0','0','1','0',z='.8'))
        report = minimum_centerline_support(F(0),F(1),F(0),sources)
        self.assertEqual(report['state'],'full-bounded')
        self.assertLessEqual(F(report['minimum_lower_exact_mm']),F('.8'))
        self.assertGreaterEqual(F(report['minimum_upper_exact_mm']),F('.8'))
        self.assertLessEqual(report['minimum_bracket_width_mm'],.001)


if __name__ == '__main__':
    unittest.main()
