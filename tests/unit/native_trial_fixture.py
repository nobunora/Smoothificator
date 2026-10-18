"""Small genuine-shaped archives for native material/trace contract tests."""
from io import BytesIO
import json
from hashlib import md5
from zipfile import ZipFile

from tests.unit.test_conditional_nominal_copy import conditional_fixture
from tools.native_used_material_profile import FILAMENT_FIELDS


def material_fixture(body,*,count=3,index=2,settings_changes=None):
    with ZipFile(BytesIO(conditional_fixture()[1])) as archive:
        settings=json.loads(archive.read('Metadata/project_settings.config'))
    for key in FILAMENT_FIELDS:
        original=settings[key]
        value=original[0] if isinstance(original,list) else original
        settings[key]=[value]*count
    settings['filament_settings_id']=[f'Material {i}' for i in range(count)]
    settings['filament_type']=['PLA']*count
    settings['filament_flow_ratio']=['1']*count;settings['filament_flow_ratio'][index]='0.98'
    settings['filament_max_volumetric_speed']=['6']*count;settings['filament_max_volumetric_speed'][index]='21'
    if settings_changes: settings.update(settings_changes)
    config=['; total layer number: 2','; model label id: 7',f'; filament: {index+1}','; CONFIG_BLOCK_START']
    for key,value in settings.items():
        if isinstance(value,list):
            if key in ('filament_settings_id','filament_start_gcode','filament_end_gcode'):
                value=';'.join(json.dumps(v) for v in value)
            elif key=='filament_type': value=';'.join(value)
            elif key.startswith('filament_') and all(v=='nil' for v in value): continue
            else: value=','.join(value)
        config.append(f'; {key} = {value}')
    config.extend(('; CONFIG_BLOCK_END','M620 M',f'M620 S{index}A',f'T{index}',f'M621 S{index}A','T1000'))
    entry_scope=None
    if b'M624 ' not in body:
        config.append('M624 AQAAAAAAAAA=');entry_scope='AQAAAAAAAAA='
    prefix=('\n'.join(config)+'\n').encode('ascii')
    suffix=b''
    if b'M625' not in body or body.rfind(b'M624 ')>body.rfind(b'M625'):
        suffix+=b'M625\n'
    suffix+=b'M620 S255\nT255\nM621 S255\n'
    source=prefix+body+suffix
    saved=json.dumps(settings).encode('ascii')
    plate=json.dumps({'bbox_all':[0,0,30,30],'bbox_objects':[{'name':'fixture.stl','bbox':[0,0,30,30]}],
        'filament_ids':[index],'first_extruder':index}).encode()
    usage=(f'<config><plate><metadata key="index" value="1"/><object identify_id="7" name="fixture.stl" skipped="false"/>'
        f'<filament id="{index+1}" used_for_object="true" used_for_support="false" nozzle_diameter="0.4" type="PLA"/>'
        '<nozzle id="0" extruder_id="1" nozzle_diameter="0.4"/>'
        f'<layer_filament_lists><layer_filament_list filament_list="{index}" layer_ranges="0 1"/>'
        '<layer_filament_list filament_list="" layer_ranges="2 2"/></layer_filament_lists></plate></config>').encode()
    model_settings=(f'<config><object id="2"><metadata key="name" value="fixture.stl"/><metadata key="extruder" value="{index+1}"/>'
        '<part id="1"/></object><plate><metadata key="plater_id" value="1"/><model_instance>'
        '<metadata key="object_id" value="2"/><metadata key="instance_id" value="0"/>'
        '<metadata key="identify_id" value="7"/></model_instance></plate></config>').encode()
    archive_buffer=BytesIO();geometry_buffer=BytesIO()
    with ZipFile(archive_buffer,'w') as archive:
        for name,content in {'Metadata/project_settings.config':saved,'Metadata/plate_1.gcode':source,
            'Metadata/plate_1.gcode.md5':md5(source).hexdigest().upper().encode(),'Metadata/plate_1.json':plate,
            'Metadata/slice_info.config':usage}.items(): archive.writestr(name,content)
    with ZipFile(geometry_buffer,'w') as archive:
        archive.writestr('Metadata/project_settings.config',saved)
        archive.writestr('Metadata/model_settings.config',model_settings)
        archive.writestr('3D/3dmodel.model','<model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources><object id="2" type="model"/></resources><build><item objectid="2"/></build></model>')
    return source,archive_buffer.getvalue(),geometry_buffer.getvalue(),len(prefix),len(prefix)+len(body),entry_scope


def change_member(archive_bytes,name,content):
    output=BytesIO()
    with ZipFile(BytesIO(archive_bytes)) as archive,ZipFile(output,'w') as target:
        for info in archive.infolist(): target.writestr(info,content if info.filename==name else archive.read(info))
    return output.getvalue()
