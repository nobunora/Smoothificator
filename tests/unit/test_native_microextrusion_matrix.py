import unittest
from fractions import Fraction as F
from dataclasses import replace
from types import SimpleNamespace
from tools.flat_matrix_fixture import matrix_cells
from tools.native_microextrusion_matrix import *
from tools.gui_native_trial_copy import rebuild_native_trial_copy

class Tests(unittest.TestCase):
 def freeze(self,cell,**kw):return freeze_matrix_line(cell,diameter_mm=kw.get('diameter',F('1.75')),speed_mm_s=kw.get('speed',F(20)),maximum_volume_mm3_s=kw.get('cap',F(12)),policy=kw.get('policy',MatrixExperimentPolicy()))
 def test_final_volume_oracle_and_clearance_independence(self):
  lines=tuple(map(self.freeze,matrix_cells()));self.assertEqual(tuple(l.commanded_e_mm for l in lines[:5]),tuple(map(F,('.00031','.00062','.00125','.00249','.00499'))));self.assertEqual(sum(l.commanded_e_mm for l in lines),F('.04830'))
  for l in lines:self.assertLessEqual(abs(l.relative_volume_error),F('.02'));self.assertEqual(l.path.points_mm[0][2]-F('.8'),l.clearance_mm)
  for i in range(5):self.assertEqual(len({lines[i+5*j].commanded_e_mm for j in range(5)}),1)
 def test_no_invalid_stadium_or_geometry_claim(self):
  line=self.freeze(matrix_cells()[20]);self.assertGreater(line.clearance_mm,line.achieved_volume_mm3_per_mm/line.clearance_mm);self.assertEqual(line.envelope_upper_xyz_mm[2],1);self.assertFalse(hasattr(line,'physical_width_mm'))
 def test_flow_limit_and_feed_floor(self):
  line=self.freeze(matrix_cells()[4],cap=F('.00001'));self.assertLessEqual(line.feed_mm_min/60*line.achieved_volume_mm3_per_mm,F('.00001'));self.assertGreater(line.feed_mm_min,0)
 def test_strict_policy_and_cell_types(self):
  for bad in (True,None,[],2):
   with self.assertRaises(ValueError):MatrixExperimentPolicy(schema_version=bad)
  bad=dict(matrix_cells()[0],row=True)
  with self.assertRaises(ValueError):self.freeze(bad)
  for key,badfield in (('h_cmd_mm','1/100'),('final_volume_mm3_per_mm','3/40000'),('start_xy_mm',list(matrix_cells()[0]['start_xy_mm'])),('id',1)):
   with self.subTest(key=key),self.assertRaises(ValueError):self.freeze(dict(matrix_cells()[0],**{key:badfield}))
  with self.assertRaises(ValueError):self.freeze(matrix_cells()[0],diameter=F(2**130))
 def test_zero_E_and_unacceptable_rounding_fail(self):
  with self.assertRaises(ValueError):self.freeze(matrix_cells()[0],diameter=F(100))
  with self.assertRaises(ValueError):self.freeze(matrix_cells()[0],policy=MatrixExperimentPolicy(maximum_volume_error_fraction=F('.0000001')))
 def test_end_cleanup_replays_variable_source_debt_exactly(self):
  from tests.unit.test_supplemental_z_hop import policy_fixture,anchor_fixture
  from tools.native_microextrusion_matrix import _line_cycle
  from orca_plugin.gcode.linear_trace import _advance,_words
  hop=policy_fixture();line=self.freeze(matrix_cells()[0]);end=NativeSupplementEndPolicy(retract_mm=F('1.6'),wipe_mm=F(1))
  for debt in (F('.3'),F('.8'),F('1.2')):
   anchor=replace(anchor_fixture(),logical_e_mm=F(0),retraction_debt_mm=debt);machine=anchor;deposits=[];wipes=[]
   block=_line_cycle(line,anchor,hop,F(4),end)
   for raw in block.splitlines():
    text=raw.split(b';',1)[0].strip().decode()
    if not text:continue
    command,words=_words(text);before=machine;machine,deposited=_advance(machine,command,words)
    if deposited:deposits.append((before.xyz_mm,machine.xyz_mm,deposited))
    if words.get('E',F(0))<0 and before.xyz_mm[:2]!=machine.xyz_mm[:2]:wipes.append((before.xyz_mm,machine.xyz_mm))
   self.assertEqual(replace(machine,logical_e_mm=F(0)),anchor);self.assertEqual(machine.logical_e_mm,line.commanded_e_mm);self.assertEqual(len(deposits),1);self.assertEqual(deposits[0][2],line.commanded_e_mm);self.assertEqual(len(wipes),1);self.assertEqual(abs(wipes[0][1][0]-wipes[0][0][0]),1)
 def test_distinct_dispatch_rejects_arbitrary_recipe(self):
  with self.assertRaises(ValueError):rebuild_native_trial_copy(SimpleNamespace(),cancelled=lambda:False)
if __name__=='__main__':unittest.main()
