"""Revolve the existing 0..40-degree profile around the vertical axis."""
from fractions import Fraction as F
import hashlib
from io import BytesIO
import json
import math
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from tools.exponential_top_fixture import ROOT, PANELS, profile, prepare as prepare_seed


ANGULAR_PANELS = 128
REVIEW_FOLDER = ROOT/'artifacts/revolved-exponential-review'


def mesh():
    points = profile()
    vertices = [(0.,0.,0.),(0.,0.,points[0][1])]
    for radius,z in points[1:]:
        vertices.extend((radius*math.cos(2*math.pi*j/ANGULAR_PANELS),
                         radius*math.sin(2*math.pi*j/ANGULAR_PANELS),z)
                        for j in range(ANGULAR_PANELS))
    bottom_start = len(vertices)
    vertices.extend((12*math.cos(2*math.pi*j/ANGULAR_PANELS),
                     12*math.sin(2*math.pi*j/ANGULAR_PANELS),0.) for j in range(ANGULAR_PANELS))
    faces = []
    for j in range(ANGULAR_PANELS):
        k = (j+1)%ANGULAR_PANELS
        faces.append((1,2+j,2+k))
        for i in range(PANELS-1):
            a,b = 2+i*ANGULAR_PANELS,2+(i+1)*ANGULAR_PANELS
            faces.extend(((a+j,b+j,b+k),(a+j,b+k,a+k)))
        a = 2+(PANELS-1)*ANGULAR_PANELS
        faces.extend(((0,bottom_start+k,bottom_start+j),
                      (bottom_start+j,bottom_start+k,a+k),(bottom_start+j,a+k,a+j)))
    return vertices,faces


def prepare(folder=REVIEW_FOLDER):
    folder.mkdir(parents=True,exist_ok=True)
    # Reuse the pinned, sanitized offline settings/package; replace its mesh.
    seed = prepare_seed(folder/'profile-seed')
    vertices,faces = mesh()
    vertex_xml = ''.join(f'<vertex x="{x:.9f}" y="{y:.9f}" z="{z:.9f}"/>' for x,y,z in vertices)
    face_xml = ''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in faces)
    model = ('<?xml version="1.0"?><model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
        '<resources><object id="1" type="model" name="Revolved exponential bowl top"><mesh><vertices>'
        +vertex_xml+'</vertices><triangles>'+face_xml+'</triangles></mesh></object></resources>'
        '<build><item objectid="1" transform="1 0 0 0 1 0 0 0 1 90 90 0"/></build></model>')
    project = folder/'revolved-exponential.3mf'
    with ZipFile(seed) as source, ZipFile(project,'w',compression=ZIP_DEFLATED) as target:
        for entry in source.infolist():
            target.writestr(entry.filename,model if entry.filename=='3D/3dmodel.model' else source.read(entry.filename))
    stl = ['solid revolved_exponential']
    for f in faces:
        stl.extend(('facet normal 0 0 0','outer loop'))
        stl.extend('vertex '+' '.join(f'{v:.9f}' for v in vertices[i]) for i in f)
        stl.extend(('endloop','endfacet'))
    stl.append('endsolid revolved_exponential')
    stl_path = folder/'revolved-exponential.stl'
    stl_path.write_text('\n'.join(stl)+'\n',encoding='ascii')
    receipt = {'surface':'360-degree revolution of unchanged exponential 0..40-degree profile',
        'radius_mm':12,'angular_panels':ANGULAR_PANELS,'radial_panels':PANELS,
        'center_top_z_mm':3,'outer_top_z_mm':profile()[-1][1],
        'angular_polygon_radius_deficit_bound_mm':12*(1-math.cos(math.pi/ANGULAR_PANELS)),
        'model_3mf_sha256':hashlib.sha256(project.read_bytes()).hexdigest(),
        'model_stl_sha256':hashlib.sha256(stl_path.read_bytes()).hexdigest()}
    (folder/'fixture.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return project


def placed_geometry(project):
    with ZipFile(BytesIO(project)) as archive:
        root = ET.fromstring(archive.read('3D/3dmodel.model'))
        component,item = root.find('.//{*}component'),root.find('.//{*}build/{*}item')
        transform = tuple(map(F,item.attrib['transform'].split()))
        if transform[:9]!=tuple(map(F,(1,0,0,0,1,0,0,0,1))) or component.attrib.get('transform')!='1 0 0 0 1 0 0 0 1 0 0 0':
            raise ValueError('unexpected revolution placement')
        path = next(v for k,v in component.attrib.items() if k.endswith('}path'))
        part = ET.fromstring(archive.read(path.lstrip('/')))
    vertices = [tuple(float(F(n.attrib[a])+transform[9+i]) for i,a in enumerate('xyz'))
                for n in part.findall('.//{*}vertex')]
    if len(vertices)!=2+(PANELS+1)*ANGULAR_PANELS:
        raise ValueError('changed revolved topology')
    center = vertices[1]
    top = [(F(0),F(str(center[2])))]
    for i in range(PANELS):
        x,y,z = vertices[2+i*ANGULAR_PANELS]
        if abs(y-center[1])>1e-5:
            raise ValueError('unexpected revolution axis')
        top.append((F(str(x-center[0])),F(str(z))))
    if any(b[0]<=a[0] or b[1]<=a[1] for a,b in zip(top,top[1:])):
        raise ValueError('nonmonotone revolution profile')
    return center,tuple(top),vertices
