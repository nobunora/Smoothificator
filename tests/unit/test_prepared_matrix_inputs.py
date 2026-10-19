import unittest,json,tempfile
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from dataclasses import asdict
from tools.prepare_calibration_library import profile_guard
from tools.prepared_matrix_inputs import load_recipe
from tools.gui_native_trial_trace import NativeTrialContext,NativeTrialState
from orca_plugin.gcode.linear_trace import MachineState
from smoothificator_preview.calibration_profile import REQUIRED_PROFILE_KEYS

class Tests(unittest.TestCase):
 def header(self,extra=b''):
  return b'; CONFIG_BLOCK_START\n'+b''.join(('; '+k+' = a \\n b\n').encode() for k in REQUIRED_PROFILE_KEYS)+extra+b'; CONFIG_BLOCK_END\n'
 def test_exact_serialized_guard_and_unrelated_duplicates(self):
  source=self.header(b'; wipe_tower_x = 1\n; wipe_tower_x = 2\n');g=profile_guard(source)
  self.assertEqual(len(g['required_key_sha256']),60)
  self.assertEqual(set(g['required_key_sha256'].values()),{sha256(b'a \\n b').hexdigest()})
 def test_guard_missing_or_ambiguous_required_rejected(self):
  for s in (self.header().replace(('; '+REQUIRED_PROFILE_KEYS[0]+' = a \\n b\n').encode(),b''),self.header(('; '+REQUIRED_PROFILE_KEYS[0]+' = other\n').encode())):
   with self.assertRaises(ValueError):profile_guard(s)
 def test_context_pin_and_closed_json_fail_before_inputs(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)/'context.json';p.write_text('{}')
   args=dict(source_path='absent',project_path='absent',producer_path='absent',geometry_path='absent',context_path=p)
   with self.assertRaises(ValueError):load_recipe(**args,context_sha256='0'*64)
   with self.assertRaises(ValueError):load_recipe(**args,context_sha256=sha256(p.read_bytes()).hexdigest())
   p.write_text('['*1000+']'*1000)
   with self.assertRaises(ValueError):load_recipe(**args,context_sha256=sha256(p.read_bytes()).hexdigest())
if __name__=='__main__':unittest.main()
