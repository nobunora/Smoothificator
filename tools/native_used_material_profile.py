"""Actual multi-preset GUI archive -> explicit one-used-material numeric view.

No archive or legacy SlicedProfile is synthesized. All original settings remain
bound, including unused material presets and machine-mode vectors.
"""
from dataclasses import dataclass,field
from fractions import Fraction as F
from hashlib import sha256,md5
from io import BytesIO
import json
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile,BadZipFile

from orca_plugin.gcode.source_profile import DECIMAL,_configuration,_unique_object
from tools.conditional_nominal_body import fingerprint


FILAMENT_FIELDS=('filament_settings_id','filament_type','filament_start_gcode','filament_end_gcode',
    'filament_diameter','filament_flow_ratio','filament_max_volumetric_speed',
    'filament_retraction_length','filament_retraction_speed','filament_deretraction_speed',
    'filament_retract_restart_extra','filament_z_hop')
EXTRUDER_FIELDS=('nozzle_diameter','outer_wall_speed','travel_speed','travel_speed_z','extruder_printable_height',
    'retraction_length','retraction_speed','deretraction_speed','retract_restart_extra','z_hop',
    'outer_wall_acceleration','outer_wall_jerk')
GLOBAL_FIELDS=('printer_model','printer_variant','printer_settings_id','print_settings_id','gcode_flavor',
    'machine_start_gcode','machine_end_gcode','layer_height','print_flow_ratio','outer_wall_flow_ratio',
    'printable_height','use_firmware_retraction','enable_arc_fitting','set_other_flow_ratios')
MODE_FIELDS=('machine_max_speed_x','machine_max_speed_y','machine_max_speed_z','machine_max_jerk_x','machine_max_jerk_y')
OVERRIDES=('retraction_length','retraction_speed','deretraction_speed','retract_restart_extra','z_hop')
TEXT_FIELDS=('filament_settings_id','filament_type','filament_start_gcode','filament_end_gcode',
    'printer_model','printer_variant','printer_settings_id','print_settings_id','gcode_flavor','machine_start_gcode','machine_end_gcode')


@dataclass(frozen=True)
class NativeMaterialProfileLimits:
    max_source_bytes: int
    max_archive_bytes: int
    max_archive_members: int
    max_uncompressed_bytes: int
    max_metadata_entries: int
    max_number_bits: int

    def __post_init__(self):
        if any(type(v) is not int or v<1 for v in self.__dict__.values()):
            raise ValueError('positive exact native profile limits required')


@dataclass(frozen=True)
class NativeEffectiveSetting:
    name: str
    source_key: str
    value: str
    domain: str
    material_index: int | None
    physical_extruder_index: int | None
    full_saved_vector: tuple[str,...]
    source_export_binding: str

    def number(self):
        if not DECIMAL.fullmatch(self.value): raise ValueError('finite decimal native effective setting required')
        return F(self.value)


@dataclass(frozen=True)
class NativeMaterialSelectionEvidence:
    material_index: int
    physical_extruder_index: int
    material_count: int
    object_id: int
    instance_id: int
    identify_id: int
    source_header_material_id: int
    layer_material_ranges: tuple[tuple[int,int,tuple[int,...]],...]
    metadata_sha256: tuple[tuple[str,str],...]


@dataclass(frozen=True)
class NativeEffectiveSingleMaterialProfile:
    source_sha256: str
    project_sha256: str
    geometry_project_sha256: str
    full_settings_sha256: str
    plate_member: str
    selection: NativeMaterialSelectionEvidence
    settings: tuple[NativeEffectiveSetting,...]
    unconsumed_duplicate_config_keys: tuple[str,...]
    schema: str=field(default='native-effective-one-used-material-v1',init=False)
    physical_authority: bool=field(default=False,init=False)

    def setting(self,name):
        if type(name) is not str: raise ValueError('closed native setting name required')
        for setting in self.settings:
            if setting.name==name: return setting
        raise ValueError('unknown native consumed setting/domain: '+name)

    @property
    def projection_identity(self): return fingerprint(self)


def _archive(content,limits):
    if type(content) is not bytes or len(content)>limits.max_archive_bytes: raise ValueError('native profile archive byte budget')
    try:
        with ZipFile(BytesIO(content)) as archive:
            infos=archive.infolist(); names=[i.filename for i in infos]
            if (len(infos)>limits.max_archive_members or len(names)!=len(set(names))
                    or sum(i.file_size for i in infos)>limits.max_uncompressed_bytes):
                raise ValueError('native profile duplicate/archive work budget')
            if archive.testzip() is not None: raise ValueError('native profile bad CRC')
            return {i.filename:archive.read(i) for i in infos}
    except BadZipFile as exc: raise ValueError('invalid native profile ZIP/CRC') from exc


def _xml(content,limits):
    if b'<!DOCTYPE' in content or b'<!ENTITY' in content: raise ValueError('native metadata DTD/entity forbidden')
    try: root=ET.fromstring(content)
    except ET.ParseError as exc: raise ValueError('invalid native XML metadata') from exc
    if sum(1 for _ in root.iter())>limits.max_metadata_entries: raise ValueError('native metadata entry budget')
    return root


def _metadata(element):
    result={}
    for child in element.findall('metadata'):
        key=child.get('key')
        if key in result or key is None: raise ValueError('duplicate native usage metadata')
        result[key]=child.get('value')
    return result


def _integer(value):
    if type(value) is not str or re.fullmatch(r'0|[1-9]\d*',value) is None: raise ValueError('exact native usage integer required')
    return int(value)


def _only(sequence,reason):
    if len(sequence)!=1: raise ValueError(reason)
    return sequence[0]


def _json(content):
    try: return json.loads(content,object_pairs_hook=_unique_object)
    except RecursionError as exc: raise ValueError('native JSON nesting resource limit') from exc


def _extended_empty_terminal_end(source,settings,total_layers,limits):
    """Bound genuine empty nominal planes using independent source counters."""
    progress=re.findall(rb'^; layer num/total_layer_count: (\d+)/(\d+)\r?$',source,re.M)
    if (tuple(int(n) for n,d in progress)!=tuple(range(1,total_layers+1))
            or len({int(d) for n,d in progress})!=1
            or len(re.findall(rb'^; CHANGE_LAYER\r?$',source,re.M))!=total_layers):
        raise ValueError('extended empty terminal progress/printed count disagreement')
    nominal=int(progress[0][1])
    if not total_layers<nominal<=limits.max_metadata_entries:
        raise ValueError('extended empty nominal layer count outside bounds')
    maximum=_only(re.findall(rb'^; max_z_height: ([0-9]+(?:\.[0-9]+)?)\r?$',source,re.M),
        'unique extended empty nominal max Z required').decode('ascii')
    exported=_only(_configuration(source).get('layer_height',()),'unique exported uniform layer height required')
    saved=settings.get('layer_height')
    if type(saved) is list and len(saved)==1:saved=saved[0]
    if any(type(v) is not str or DECIMAL.fullmatch(v) is None for v in (maximum,exported,saved)):
        raise ValueError('finite uniform source/saved height and nominal max Z required')
    maximum,height,saved_height=map(F,(maximum,exported,saved))
    if any(max(v.numerator.bit_length(),v.denominator.bit_length())>limits.max_number_bits for v in (maximum,height,saved_height)):
        raise ValueError('extended empty terminal numeric bit budget')
    if height<=0 or maximum<=0 or height!=saved_height or maximum/height!=nominal:
        raise ValueError('extended empty terminal nominal max Z/uniform height disagreement')
    declared_z=re.findall(rb'^; Z_HEIGHT: (.+)\r?$',source,re.M)
    fields=tuple(word.decode('ascii').strip() for word in declared_z)
    if any(DECIMAL.fullmatch(word) is None for word in fields):
        raise ValueError('finite printed Z/layer height metadata required')
    z_planes=tuple(F(word.decode('ascii').strip()) for word in declared_z)
    # LAYER_HEIGHT is feature thickness (e.g. bridges), not the nominal grid.
    if z_planes!=tuple(height*i for i in range(1,total_layers+1)):
        raise ValueError('extended empty terminal printed uniform Z/height disagreement')
    return nominal-1


def _usage(source,archive,geometry,settings,plate,limits,cancelled):
    slice_root=_xml(archive['Metadata/slice_info.config'],limits)
    usage_plate=_only(slice_root.findall('plate'),'one actual sliced plate required')
    if _metadata(usage_plate).get('index')!=str(plate): raise ValueError('native selected plate index mismatch')
    used=[]
    for filament in usage_plate.findall('filament'):
        flags=filament.get('used_for_object'),filament.get('used_for_support')
        if any(flag not in ('true','false') for flag in flags): raise ValueError('explicit used-material flags required')
        if 'true' in flags: used.append(filament)
    filament=_only(used,'exactly one actually used material required')
    if filament.get('used_for_object')!='true': raise ValueError('one object material required')
    material_id=_integer(filament.get('id')); index=material_id-1
    identities=settings.get('filament_settings_id')
    if type(identities) is not list or not identities or any(type(v) is not str or not v for v in identities):
        raise ValueError('explicit full saved material identity vector required')
    count=len(identities)
    if count>limits.max_metadata_entries: raise ValueError('native material count budget')
    if not 0<=index<count: raise ValueError('used material index outside saved vector')
    nozzle=_only(usage_plate.findall('nozzle'),'one physical nozzle required')
    if nozzle.get('id')!='0' or nozzle.get('extruder_id')!='1': raise ValueError('one physical extruder0/nozzle0 required')
    layer_count=_only(re.findall(rb'^; total layer number: (\d+)\r?$',source,re.M),'source layer count missing/duplicate')
    total_layers=int(layer_count)
    if total_layers<1 or total_layers>limits.max_metadata_entries: raise ValueError('native finite layer count required')
    ranges=[]; cursor=0
    for row in usage_plate.findall('./layer_filament_lists/layer_filament_list'):
        endpoints=row.get('layer_ranges','').split()
        if len(endpoints)!=2: raise ValueError('declared finite layer range grammar required')
        start,end=map(_integer,endpoints)
        entries=tuple(map(_integer,row.get('filament_list','').split()))
        if start!=cursor or end<start or entries not in ((),(index,)) or start>total_layers:
            raise ValueError('layer/material usage disagreement')
        if entries and end>=total_layers:raise ValueError('nonempty material beyond printed layers')
        if end>total_layers:
            if start!=total_layers or entries or end!=_extended_empty_terminal_end(source,settings,total_layers,limits):
                raise ValueError('extended empty terminal layer/material disagreement')
        if start<total_layers and entries!=(index,): raise ValueError('missing actually used layer material')
        if start==total_layers and entries: raise ValueError('unexpected terminal layer material')
        cursor=end+1; ranges.append((start,end,entries))
    if cursor<total_layers: raise ValueError('incomplete actual layer material coverage')
    plate_json=_json(archive[f'Metadata/plate_{plate}.json'])
    if type(plate_json) is not dict: raise ValueError('native plate JSON object required')
    ids=plate_json.get('filament_ids')
    if (type(ids) is not list or any(type(v) is not int for v in ids) or ids!=[index] or type(plate_json.get('first_extruder')) is not int
            or plate_json['first_extruder']!=index): raise ValueError('plate material/index disagreement')
    geometry_root=_xml(geometry['Metadata/model_settings.config'],limits)
    obj=_only(geometry_root.findall('object'),'one placed object required')
    obj_meta=_metadata(obj)
    if _integer(obj_meta.get('extruder'))!=material_id: raise ValueError('object material assignment disagreement')
    parts=obj.findall('part')
    if not parts: raise ValueError('placed object part evidence required')
    for part in parts:
        override=_metadata(part).get('extruder')
        if override is not None and _integer(override)!=material_id: raise ValueError('part material override disagreement')
    model_plate=_only(geometry_root.findall('plate'),'one geometry plate required')
    if _metadata(model_plate).get('plater_id')!=str(plate): raise ValueError('geometry plate index disagreement')
    instance=_only(model_plate.findall('model_instance'),'one placed model instance required')
    instance_meta=_metadata(instance)
    object_id=_integer(obj.get('id'))
    if _integer(instance_meta.get('object_id'))!=object_id or instance_meta.get('instance_id')!='0':
        raise ValueError('placed instance/object mapping disagreement')
    identify=_integer(instance_meta.get('identify_id'))
    slice_obj=_only(usage_plate.findall('object'),'one actual sliced object required')
    boxes=plate_json.get('bbox_objects')
    if (slice_obj.get('identify_id')!=str(identify) or slice_obj.get('skipped')!='false'
            or type(boxes) is not list or len(boxes)!=1 or type(boxes[0]) is not dict or boxes[0].get('name')!=obj_meta.get('name')
            or slice_obj.get('name')!=obj_meta.get('name')): raise ValueError('sliced/placed object identity disagreement')
    model=_xml(geometry['3D/3dmodel.model'],limits)
    resource=_only(model.findall('./{*}resources/{*}object'),'one placed build resource required')
    if resource.get('id')!=str(object_id): raise ValueError('placed resource object mapping disagreement')
    item=_only(model.findall('./{*}build/{*}item'),'one geometry build item required')
    if item.get('objectid')!=str(object_id): raise ValueError('geometry build object mapping disagreement')
    header_id=_only(re.findall(rb'^; model label id: (\d+)\r?$',source,re.M),'source object label missing/duplicate')
    header_material=_only(re.findall(rb'^; filament: (\d+)\r?$',source,re.M),'source used material missing/duplicate')
    if int(header_id)!=identify or int(header_material)!=material_id: raise ValueError('source material/object header disagreement')
    executable=[raw.split(b';',1)[0].strip().decode('ascii') for raw in source.splitlines()]
    opens=[i for i,text in enumerate(executable) if text.startswith('M624 ')]
    closes=[i for i,text in enumerate(executable) if text=='M625']
    if not opens or not closes: raise ValueError('actual object execution scope required')
    first,last=min(opens),max(closes)
    tools=[]; begin=[]; finish=[]
    for line,text in enumerate(executable):
        _checkpoint(cancelled)
        if text.startswith(('T','M620','M621')):
            if first<=line<=last: raise ValueError('body material/tool switch forbidden')
            if re.fullmatch(r'T\d+',text):
                tool=int(text[1:]);tools.append((line,tool))
                if tool not in (index,1000,255) or (tool in (index,1000) and line>=first) or (tool==255 and line<=last):
                    raise ValueError('unknown material tool/sentinel or wrong execution region')
            elif text==f'M620 S{index}A' and line<first: begin.append(line)
            elif text==f'M621 S{index}A' and line<first: finish.append(line)
            elif text=='M620 M' and line<first: pass
            elif line<first and re.fullmatch(r'M620\.1 E F[0-9]+(?:\.[0-9]+)? T[0-9]+(?:\.[0-9]+)?',text):
                # Pinned OEM E feed/temperature setup, not a tool-selection T word.
                if any(F(token[1:])<=0 for token in text.split()[2:]): raise ValueError('positive OEM setup feed/temperature required')
            elif text=='M620.3 W1' and line<first: pass
            elif text in ('M620 S255','M621 S255') and line>last: pass
            else: raise ValueError('unknown source material selection syntax')
    if len(begin)!=1 or len(finish)!=1 or len([v for _,v in tools if v==index])!=1:
        raise ValueError('one source startup material selection required')
    if not begin[0]<next(line for line,v in tools if v==index)<finish[0]: raise ValueError('source material selection ordering mismatch')
    hashes=tuple((name,sha256(content).hexdigest()) for name,content in (
        ('slice_info',archive['Metadata/slice_info.config']),('plate_json',archive[f'Metadata/plate_{plate}.json']),
        ('placed_model_settings',geometry['Metadata/model_settings.config'])))
    if any(v.bit_length()>limits.max_number_bits for v in (index,count,object_id,identify,material_id)):
        raise ValueError('native selection numeric bit budget')
    return NativeMaterialSelectionEvidence(index,0,count,object_id,0,identify,material_id,tuple(ranges),hashes),nozzle,filament


def _checkpoint(cancelled):
    answer=cancelled()
    if type(answer) is not bool or answer: raise ValueError('native profile cancelled or invalid cancellation result')


def read_native_used_material_profile(project,source,geometry_project,*,limits,plate=1,cancelled=lambda:False):
    if type(limits) is not NativeMaterialProfileLimits or type(plate) is not int or plate<1 or not callable(cancelled):
        raise ValueError('explicit native profile limits/plate required')
    if type(source) is not bytes or len(source)>limits.max_source_bytes: raise ValueError('native profile source byte budget')
    _checkpoint(cancelled)
    archive=_archive(project,limits);geometry=_archive(geometry_project,limits)
    member=f'Metadata/plate_{plate}.gcode'
    if not {member,member+'.md5','Metadata/project_settings.config',f'Metadata/plate_{plate}.json','Metadata/slice_info.config'}<=archive.keys():
        raise ValueError('missing actual native sliced usage/settings members')
    if not {'Metadata/project_settings.config','Metadata/model_settings.config','3D/3dmodel.model'}<=geometry.keys():
        raise ValueError('missing actual placed geometry/settings members')
    if archive.get(member)!=source or archive.get(member+'.md5')!=md5(source).hexdigest().upper().encode('ascii'):
        raise ValueError('native embedded source/uppercase MD5 mismatch')
    raw=archive['Metadata/project_settings.config']
    if geometry.get('Metadata/project_settings.config')!=raw: raise ValueError('actual sliced/geometry full settings mismatch')
    settings=_json(raw)
    if type(settings) is not dict or len(settings)>limits.max_metadata_entries: raise ValueError('bounded saved settings object required')
    selection,nozzle,filament=_usage(source,archive,geometry,settings,plate,limits,cancelled)
    config=_configuration(source); resolved=[]; consumed=set()

    def number(text):
        if type(text) is not str or DECIMAL.fullmatch(text) is None: raise ValueError('finite decimal saved native number required')
        value=F(text)
        if max(value.numerator.bit_length(),value.denominator.bit_length())>limits.max_number_bits:
            raise ValueError('native profile numeric bit budget')
        return value

    def match_export(key,vector,*,nil_omission=False):
        occurrences=config.get(key,())
        if not occurrences and nil_omission and all(v=='nil' for v in vector): return 'explicit-all-nil-writer-omission'
        if len(occurrences)!=1: raise ValueError('missing/duplicate consumed native source config: '+key)
        exported=tuple(part.strip() for part in occurrences[0].split(','))
        if len(exported)!=len(vector) or any(a!=b and (a=='nil' or b=='nil' or number(a)!=number(b)) for a,b in zip(exported,vector)):
            raise ValueError('full native source/config vector mismatch: '+key)
        consumed.add(key);return 'full-source-vector-agreement'

    for key in FILAMENT_FIELDS+EXTRUDER_FIELDS+GLOBAL_FIELDS+MODE_FIELDS:
        _checkpoint(cancelled)
        if key not in settings: raise ValueError('missing native consumed setting: '+key)
        saved=settings[key]
        if key in FILAMENT_FIELDS:
            if type(saved) is not list or len(saved)!=selection.material_count or any(type(v) is not str for v in saved):
                raise ValueError('full filament vector cardinality/type mismatch: '+key)
            vector=tuple(saved);selected=vector[selection.material_index];domain='FILAMENT';mi=selection.material_index;ei=None
        elif key in EXTRUDER_FIELDS:
            # Each listed field's legacy contract permits string or singleton vector.
            vector=tuple(saved) if type(saved) is list else (saved,)
            if len(vector)!=1 or type(vector[0]) is not str: raise ValueError('single physical extruder cardinality mismatch: '+key)
            selected=vector[0];domain='PHYSICAL_EXTRUDER';mi=None;ei=0
        elif key in MODE_FIELDS:
            if type(saved) is not list or not saved or any(type(v) is not str for v in saved): raise ValueError('full machine mode vector required')
            vector=tuple(saved);selected=min(vector,key=number);domain='MACHINE_MODE';mi=ei=None
        else:
            if type(saved) is not str: raise ValueError('global native scalar required: '+key)
            vector=(saved,);selected=saved;domain='GLOBAL';mi=ei=None
        if key in TEXT_FIELDS:
            if not selected and 'gcode' not in key: raise ValueError('nonempty native setting identity required')
            binding='saved-full-settings-and-actual-usage'
            if key=='filament_type':
                occurrences=config.get(key,())
                if len(occurrences)!=1 or tuple(occurrences[0].split(';'))!=vector: raise ValueError('full filament type vector mismatch')
                consumed.add(key);binding='full-semicolon-text-vector'
            elif key=='filament_settings_id':
                occurrences=config.get(key,())
                if len(occurrences)!=1: raise ValueError('full quoted filament identities required')
                encoded=';'.join(json.dumps(v,ensure_ascii=True) for v in vector)
                if occurrences[0]!=encoded: raise ValueError('full quoted filament identity vector mismatch')
                consumed.add(key);binding='full-quoted-semicolon-text-vector'
            elif key in ('printer_model','gcode_flavor'):
                if config.get(key)!=[selected]: raise ValueError('native source identity mismatch: '+key)
                consumed.add(key);binding='source-scalar-agreement'
        else:
            for value in vector:
                if value=='nil' and key.startswith('filament_') and key[len('filament_'):] in OVERRIDES: continue
                numeric=number(value)
                if numeric<0: raise ValueError('nonnegative native numeric setting required')
            binding=match_export(key,vector,nil_omission=key.startswith('filament_') and key[len('filament_'):] in OVERRIDES)
            if key in ('use_firmware_retraction','enable_arc_fitting','set_other_flow_ratios') and number(selected) not in (0,1):
                raise ValueError('native boolean setting requires0/1')
            if key in ('nozzle_diameter','filament_diameter','filament_flow_ratio','filament_max_volumetric_speed',
                       'layer_height','print_flow_ratio','outer_wall_flow_ratio','outer_wall_speed','travel_speed',
                       'printable_height','outer_wall_acceleration','retraction_speed','deretraction_speed') and number(selected)<=0:
                raise ValueError('positive native numeric setting required: '+key)
            if key.startswith('machine_max_speed_') and any(number(v)<=0 for v in vector): raise ValueError('positive machine speed modes required')
        resolved.append(NativeEffectiveSetting(key,key,selected,domain,mi,ei,vector,binding))
    by_name={setting.name:setting for setting in resolved}
    if number(nozzle.get('nozzle_diameter'))!=by_name['nozzle_diameter'].number() or number(filament.get('nozzle_diameter'))!=by_name['nozzle_diameter'].number():
        raise ValueError('actual physical nozzle diameter disagreement')
    if filament.get('type')!=by_name['filament_type'].value: raise ValueError('actual used filament type disagreement')
    for name in OVERRIDES:
        override=by_name['filament_'+name]
        selected=by_name[name] if override.value=='nil' else override
        if selected.number()<0 or name.endswith('speed') and selected.number()<=0: raise ValueError('invalid effective retraction/hop override')
        resolved=[setting for setting in resolved if setting.name!=name]
        resolved.append(NativeEffectiveSetting(name,selected.source_key,selected.value,selected.domain,
            selection.material_index,0,selected.full_saved_vector,selected.source_export_binding))
    for key in MODE_FIELDS:
        if key.startswith('machine_max_speed_'):
            selected=by_name[key]
            resolved.append(NativeEffectiveSetting('conservative_'+key,key,selected.value,'MACHINE_MODE',None,None,
                selected.full_saved_vector,selected.source_export_binding))
    height=by_name['extruder_printable_height']
    if height.number()==0: height=by_name['printable_height']
    resolved.append(NativeEffectiveSetting('effective_printable_height',height.source_key,height.value,height.domain,None,0,
        height.full_saved_vector,height.source_export_binding))
    return NativeEffectiveSingleMaterialProfile(sha256(source).hexdigest(),sha256(project).hexdigest(),sha256(geometry_project).hexdigest(),
        sha256(raw).hexdigest(),member,selection,tuple(resolved),tuple(sorted(k for k,v in config.items() if len(v)>1 and k not in consumed)))
