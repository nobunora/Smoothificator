import unittest
from fractions import Fraction as F
from dataclasses import replace
from types import SimpleNamespace as NS
from adaptive_subedge.domain.prepared_matrix import SourceRatioMatrixPolicy,source_relative_conditions,PreparedMatrixPolicy,prepared_conditions
from tools.native_prepared_matrix import MatrixSourceSpeedReference,freeze_prepared_line,resolve_source_speed_reference

class Tests(unittest.TestCase):
 def reference(self,speed=F(200)):
  return MatrixSourceSpeedReference('matrix-source-speed-reference-v1','a'*64,'b'*64,F('.8'),'Outer wall',(1,2,3,4),speed,F(12000),F(200),F(200),speed)
 def freeze(self,c,p,ref):return freeze_prepared_line(c,diameter_mm=F('1.75'),speed_mm_s=F(200),maximum_volume_mm3_s=F(21),policy=p,source_reference=ref)
 def test_percentages_resolve_and_volume_unchanged(self):
  p=SourceRatioMatrixPolicy();ref=self.reference();cells=source_relative_conditions(p,ref.resolved_reference_speed_mm_s)
  self.assertEqual(tuple(c.print_speed_mm_s for c in cells[:5]),tuple(map(F,(40,80,120,160,200))))
  for row in range(5):
   lines=[self.freeze(c,p,ref) for c in cells[row*5:row*5+5]]
   self.assertEqual(len({l.commanded_e_mm for l in lines}),1);self.assertEqual(tuple(l.feed_mm_min for l in lines),tuple(map(F,(2400,4800,7200,9600,12000))))
 def test_schema_types_and_reference_arithmetic(self):
  for changes in ({'schema_version':True},{'schema_version':2},{'trial_id':'h_volume'}):
   with self.assertRaises(ValueError):SourceRatioMatrixPolicy(**changes)
  for changes in ({'resolved_reference_speed_mm_s':F(201)},{'source_line_numbers':[1,2]},{'source_line_numbers':(True,)},{'machine_x_cap_mm_s':'200'}):
   with self.assertRaises(ValueError):replace(self.reference(),**changes)
  with self.assertRaises(ValueError):self.freeze(source_relative_conditions(SourceRatioMatrixPolicy(),F(200))[0],SourceRatioMatrixPolicy(),None)
 def test_feed_floor_never_rounds_up(self):
  p=SourceRatioMatrixPolicy();ref=self.reference(F(1,7));c=source_relative_conditions(p,F(1,7))[1];line=self.freeze(c,p,ref)
  self.assertLessEqual(line.feed_mm_min,c.print_speed_mm_s*60);self.assertLess(c.print_speed_mm_s*60-line.feed_mm_min,F('.001'))
 def test_source_evidence_and_caps(self):
  setting={'outer_wall_speed':F(200),'conservative_machine_max_speed_x':F(180),'conservative_machine_max_speed_y':F(190)}
  profile=NS(setting=lambda k:NS(number=lambda:setting[k]),projection_identity='b'*64)
  a=NS(xyz_mm=(F(1),F(2),F('.8')));b=NS(xyz_mm=(F(3),F(2),F('.8')),feed_mm_min=F(12000))
  event=NS(feature='Outer wall',deposited_filament_mm=F(1),before=NS(machine=a),after=NS(machine=b),branch_depth=0,line_number=3)
  self.assertEqual(resolve_source_speed_reference(NS(events=(event,)),profile,'a'*64).resolved_reference_speed_mm_s,F(180))
  for events in ((),(NS(**(vars(event)|{'branch_depth':1})),)):
   with self.assertRaises(ValueError):resolve_source_speed_reference(NS(events=events),profile,'a'*64)
 def test_old_policy_keeps_absolute_axis(self):
  p=PreparedMatrixPolicy('volume_speed');self.assertEqual(tuple(c.print_speed_mm_s for c in prepared_conditions(p)[:5]),tuple(map(F,(5,10,20,30,40))))
if __name__=='__main__':unittest.main()
