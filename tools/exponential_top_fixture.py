"""Closed mesh with exponential-ramp slope angle from 0 to 40 degrees."""
from bisect import bisect_right
from fractions import Fraction as F
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from tools.generate_top_surface_candidates import ROOT, MODEL_SHA256, _pinned


LENGTH_MM, WIDTH_MM, BASE_HEIGHT_MM = 20,12,3
PANELS = 256
REVIEW_FOLDER = ROOT/'artifacts/exponential-top-0to40-review'


def angle_radians(y_mm):
    return math.radians(40)*math.expm1(math.log(4)*y_mm/WIDTH_MM)/3


def profile(panels=PANELS):
    if type(panels) is not int or not 2 <= panels <= 4096:
        raise ValueError('profile panels must be an integer within 2..4096')
    step = WIDTH_MM/panels
    points = [(0.,float(BASE_HEIGHT_MM))]
    for i in range(panels):
        a,b = i*step,(i+1)*step
        rise = step/6*(math.tan(angle_radians(a))+4*math.tan(angle_radians((a+b)/2))
                      +math.tan(angle_radians(b)))
        points.append((b,points[-1][1]+rise))
    return points


def mesh():
    vertices = []
    for y,z in profile():
        vertices.extend(((0,y,0),(LENGTH_MM,y,0),(0,y,z),(LENGTH_MM,y,z)))
    faces = []
    for i in range(PANELS):
        a,b = 4*i,4*(i+1)
        faces.extend(((a,b,b+1),(a,b+1,a+1),(a+2,a+3,b+3),(a+2,b+3,b+2),
                      (a,b+2,b),(a,a+2,b+2),(a+1,b+1,b+3),(a+1,b+3,a+3)))
    faces.extend(((0,1,3),(0,3,2)))
    a = 4*PANELS
    faces.extend(((a,a+2,a+3),(a,a+3,a+1)))
    return vertices,faces


def prepare(folder: Path):
    folder.mkdir(parents=True,exist_ok=True)
    vertices,faces = mesh()
    coords = lambda p:' '.join(f'{v:.9f}' for v in p)
    stl = ['solid exponential_angle_top']
    for face in faces:
        stl.extend(('facet normal 0 0 0','outer loop'))
        stl.extend('vertex '+coords(vertices[i]) for i in face)
        stl.extend(('endloop','endfacet'))
    stl.append('endsolid exponential_angle_top')
    stl_path = folder/'exponential-angle-top.stl'
    stl_path.write_text('\n'.join(stl)+'\n',encoding='ascii')
    vertex_xml = ''.join(f'<vertex x="{x:.9f}" y="{y:.9f}" z="{z:.9f}"/>' for x,y,z in vertices)
    face_xml = ''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in faces)
    model = ('<?xml version="1.0"?><model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
        '<resources><object id="1" type="model" name="Exponential angle top"><mesh><vertices>'
        +vertex_xml+'</vertices><triangles>'+face_xml+'</triangles></mesh></object></resources>'
        '<build><item objectid="1" transform="1 0 0 0 1 0 0 0 1 80 84 0"/></build></model>')
    with ZipFile(BytesIO(_pinned(ROOT/'artifacts/fixtures/offline-coupon.3mf',MODEL_SHA256))) as original:
        settings = json.loads(original.read('Metadata/project_settings.config'))
    settings['enable_arc_fitting'] = '0'
    for key,value in tuple(settings.items()):
        if key.endswith('_gcode'):
            settings[key] = ['']*len(value) if isinstance(value,list) else ''
    settings['machine_start_gcode'] = 'G90\nM83\nG92 E0'
    project = folder/'exponential-angle-top.3mf'
    with ZipFile(project,'w',compression=ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>')
        archive.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        archive.writestr('3D/3dmodel.model',model)
        archive.writestr('Metadata/project_settings.config',json.dumps(settings))
    receipt = {'definition':'theta(y) = 40 degrees * (exp(log(4)*y/12 mm)-1)/3; dz/dy = tan(theta)',
        'panel_count':PANELS,'dimensions_xy_mm':[LENGTH_MM,WIDTH_MM],
        'bottom_z_mm':0,'first_top_z_mm':3,'last_top_z_mm':profile()[-1][1],
        'mesh_chord_vertical_bound_mm':math.log(4)/12*math.radians(40)*F(4,3)/math.cos(math.radians(40))**2*(12/PANELS)**2/8,
        'integration':'panelwise Simpson rule, 9-decimal serialized mesh vertices',
        'model_3mf_sha256':hashlib.sha256(project.read_bytes()).hexdigest(),
        'model_stl_sha256':hashlib.sha256(stl_path.read_bytes()).hexdigest()}
    (folder/'fixture.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return project


def placed_profile(project):
    """Read back actual exported placement; reject rotation or changed topology."""
    with ZipFile(BytesIO(project)) as archive:
        root = ET.fromstring(archive.read('3D/3dmodel.model'))
        component,item = root.find('.//{*}component'),root.find('.//{*}build/{*}item')
        transform = tuple(map(F,item.attrib['transform'].split()))
        if transform[:9] != tuple(map(F,(1,0,0,0,1,0,0,0,1))) or component.attrib.get('transform')!='1 0 0 0 1 0 0 0 1 0 0 0':
            raise ValueError('unexpected curved model placement')
        path = next(v for k,v in component.attrib.items() if k.endswith('}path'))
        part = ET.fromstring(archive.read(path.lstrip('/')))
    vertices = [tuple(F(n.attrib[a])+transform[9+i] for i,a in enumerate('xyz'))
                for n in part.findall('.//{*}vertex')]
    if len(vertices) != 4*(PANELS+1) or len(part.findall('.//{*}triangle'))!=8*PANELS+4:
        raise ValueError('unexpected curved mesh topology')
    top = []
    for i in range(PANELS+1):
        a,b = vertices[4*i+2:4*i+4]
        if a[1:]!=b[1:] or b[0]-a[0]!=20:
            raise ValueError('curved top is not an X extrusion')
        top.append((a[1],a[2]))
    if any(b[0]<=a[0] or b[1]<=a[1] for a,b in zip(top,top[1:])):
        raise ValueError('nonmonotone curved top')
    return (vertices[2][0],vertices[3][0],top[0][0],top[-1][0]),tuple(top)


def target_at(top, y):
    if not top[0][0] <= y <= top[-1][0]:
        raise ValueError('target query outside curved top domain')
    index = min(len(top)-2,max(0,bisect_right([p[0] for p in top],y)-1))
    (a,z0),(b,z1) = top[index:index+2]
    slope = (z1-z0)/(b-a)
    return z0+slope*(y-a),slope
