"""Decode an explicitly pinned offline matrix source packet; no implicit local paths."""
from dataclasses import fields
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
from tools.gui_native_trial_trace import NativeTrialContext,NativeTrialState,NativeTrialLimits,interpret_native_trial
from orca_plugin.gcode.linear_trace import MachineState
from tools.flat_matrix_fixture import FlatMatrixFixture
from tools.native_microextrusion_matrix import NativeMicroextrusionMatrixRecipe

LIMITS=NativeTrialLimits(1000000,10000000,100000000,20000,16,4096,100,20000000)

def _closed(value,kind):
 if type(value) is not dict or set(value)!={f.name for f in fields(kind)}:raise ValueError('closed offline matrix packet required')
 return dict(value)

def load_recipe(*,source_path,project_path,producer_path,geometry_path,context_path,context_sha256):
 def bounded(path,maximum):
  path=Path(path)
  if path.stat().st_size>maximum:raise ValueError('offline matrix input size limit')
  content=path.read_bytes()
  if len(content)>maximum:raise ValueError('offline matrix input changed size')
  return content
 raw=bounded(context_path,65536)
 if type(context_sha256) is not str or sha256(raw).hexdigest()!=context_sha256:raise ValueError('offline context pin differs')
 def unique(pairs):
  out={}
  for k,v in pairs:
   if k in out:raise ValueError('duplicate offline context key')
   out[k]=v
  return out
 try:context=_closed(json.loads(raw,object_pairs_hook=unique),NativeTrialContext)
 except (UnicodeError,json.JSONDecodeError,RecursionError) as error:raise ValueError('invalid offline context JSON') from error
 entry=_closed(context['entry'],NativeTrialState);machine=_closed(entry['machine'],MachineState)
 def number(v):
  if v is None:return None
  if type(v) is not str or len(v)>256:raise ValueError('bounded exact offline state number required')
  try:n=F(v)
  except (ValueError,ZeroDivisionError) as error:raise ValueError('invalid offline state number') from error
  if max(abs(n.numerator).bit_length(),n.denominator.bit_length())>4096:raise ValueError('offline number bit limit')
  return n
 if type(machine['xyz_mm']) is not list or len(machine['xyz_mm'])!=3:raise ValueError('closed offline XYZ required')
 machine['xyz_mm']=tuple(number(v) for v in machine['xyz_mm'])
 for k in ('feed_mm_min','logical_e_mm','retraction_debt_mm'):machine[k]=number(machine[k])
 for k in set(machine)-{'xyz_mm','feed_mm_min','logical_e_mm','retraction_debt_mm'}:
  if type(machine[k]) is not bool and machine[k] is not None:raise ValueError('exact offline machine flag required')
 entry['machine']=MachineState(**machine)
 for k in ('acceleration_mm_s2','classic_jerk_xy_mm_s'):entry[k]=number(entry[k])
 context['entry']=NativeTrialState(**entry)
 for k in ('judge_flags','opaque_command_texts','unresolved_premises'):
  if type(context[k]) is not list or len(context[k])>256 or any(type(v) is not str or len(v)>4096 for v in context[k]):raise ValueError('bounded offline context strings required')
  context[k]=tuple(context[k])
 context=NativeTrialContext(**context)
 source,project,producer,geometry=(bounded(p,cap) for p,cap in ((source_path,LIMITS.max_source_bytes),(project_path,LIMITS.max_project_bytes),(producer_path,LIMITS.max_producer_bytes),(geometry_path,LIMITS.max_project_bytes)))
 trace=interpret_native_trial(source,project,producer,context,geometry_project=geometry,limits=LIMITS,cancelled=lambda:False)
 last=max(e.byte_offset for e in trace.events if e.deposited_filament_mm is not None and e.deposited_filament_mm>0)
 anchors=[e.byte_offset for e in trace.events if e.command=='M625' and e.byte_offset>last]
 if len(anchors)!=1:raise ValueError('unique offline post-label anchor required')
 return NativeMicroextrusionMatrixRecipe(source,project,producer,context,geometry,LIMITS,FlatMatrixFixture(),anchors[0])
