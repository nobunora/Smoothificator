import unittest
from dataclasses import replace
from fractions import Fraction as F
from adaptive_subedge.domain.prepared_matrix import *
from tools.native_prepared_matrix import freeze_prepared_line,_line_cycle
from tools.native_supplement_end import NativeSupplementEndPolicy
from orca_plugin.gcode.linear_trace import _advance,_words
from tests.unit.test_supplemental_z_hop import policy_fixture,anchor_fixture

class Tests(unittest.TestCase):
 def freeze(self,c,p,**kw):return freeze_prepared_line(c,policy=p,diameter_mm=F('1.75'),speed_mm_s=kw.get('speed',F(200)),maximum_volume_mm3_s=kw.get('volume',F(21)))
 def test_finite_axes_and_isolation(self):
  for stage in STAGES:
   p=PreparedMatrixPolicy(stage);cells=prepared_conditions(p);self.assertEqual(len(cells),25)
   names={a[0] for a in AXES[stage]}
   for field in PreparedMatrixCondition.__dataclass_fields__:
    if field not in names|{'cell_id','row','column'}:self.assertEqual(len({getattr(c,field) for c in cells}),1)
   for c in cells:self.assertGreater(self.freeze(c,p).commanded_e_mm,0)
 def test_startup_total_split_and_extra(self):
  p=PreparedMatrixPolicy('startup_extra_speed')
  for c in prepared_conditions(p):
   line=self.freeze(c,p);self.assertEqual(len(line.segments),2);self.assertEqual(line.commanded_e_mm,line.baseline_total_e_mm+c.startup_extra_e_mm);self.assertEqual(line.segments[0][1][0]-line.segments[0][0][0],2);self.assertEqual(line.segments[1][1][0]-line.segments[1][0][0],8);self.assertEqual(line.segments[1][2],F('.001'))
 def test_caps_reject_instead_of_axis_clipping(self):
  p=PreparedMatrixPolicy('volume_speed');c=prepared_conditions(p)[-1]
  for kw in ({'speed':F(30)},{'volume':F('.00001')}):
   with self.assertRaises(ValueError):self.freeze(c,p,**kw)
 def test_closed_types_and_malformed_conditions(self):
  for bad in (None,True,[],3):
   with self.assertRaises(ValueError):PreparedMatrixPolicy('retract_wipe',schema_version=bad)
  p=PreparedMatrixPolicy('retract_wipe');c=prepared_conditions(p)[0]
  for change in ({'retract_mm':'2/5'},{'row':True},{'startup_extra_e_mm':F(-1)}):
   with self.assertRaises(ValueError):replace(c,**change)
  with self.assertRaises(ValueError):self.freeze(replace(c,retract_mm=F(2)),p)
 def test_physical_debt_and_independent_start_speed(self):
  hop=policy_fixture()
  for stage in ('retract_wipe','startup_extra_speed','volume_speed'):
   p=PreparedMatrixPolicy(stage)
   for c in prepared_conditions(p):
    line=self.freeze(c,p)
    for debt in (F('.3'),F('.8'),F('1.2')):
     anchor=replace(anchor_fixture(),logical_e_mm=F(0),retraction_debt_mm=debt);machine=anchor;deposits=[];stationary=[]
     block=_line_cycle(line,anchor,hop,F(4))
     for raw in block.splitlines():
      text=raw.split(b';',1)[0].strip().decode()
      if not text:continue
      command,words=_words(text);before=machine;machine,deposit=_advance(machine,command,words)
      if deposit:deposits.append(deposit);self.assertNotEqual(before.xyz_mm[:2],machine.xyz_mm[:2])
      if words.get('E',F(0))>0 and before.xyz_mm==machine.xyz_mm:stationary.append((words['E'],machine.feed_mm_min))
     self.assertEqual(replace(machine,logical_e_mm=F(0)),anchor);self.assertEqual(machine.logical_e_mm,line.commanded_e_mm);self.assertEqual(sum(deposits),line.commanded_e_mm);self.assertEqual(stationary[0],(debt,c.start_debt_unretract_speed_mm_s*60))
     if c.retract_mm>debt:self.assertEqual(stationary[-1][1],1800)
 def test_start_speed_invalid_rejected(self):
  p=PreparedMatrixPolicy('startup_extra_speed');line=self.freeze(prepared_conditions(p)[0],p);hop=replace(policy_fixture(),deretract_speed_mm_s=F(5))
  with self.assertRaises(ValueError):_line_cycle(line,anchor_fixture(),hop,F(4))
if __name__=='__main__':unittest.main()
