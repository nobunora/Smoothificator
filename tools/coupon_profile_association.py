"""Bounded 3MF geometry association for the placed extruded coupon profile."""
from fractions import Fraction as F
from io import BytesIO
from xml.etree import ElementTree as ET
from zipfile import ZipFile, BadZipFile

MAX_ARCHIVE_BYTES=20000000
MAX_MEMBERS=128
MAX_TOTAL_UNCOMPRESSED_BYTES=50000000
MAX_XML_BYTES=4000000
IDENTITY=(F(1),F(0),F(0),F(0),F(1),F(0),F(0),F(0),F(1))
CORE='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'


def read_coupon_mesh(geometry_project):
    """Read one bounded translated core mesh; no optimizer or reslice."""
    if type(geometry_project) is not bytes or len(geometry_project)>MAX_ARCHIVE_BYTES:
        raise ValueError('coupon geometry archive byte bound')
    try:
        with ZipFile(BytesIO(geometry_project)) as archive:
            members=archive.infolist();names=[i.filename for i in members]
            if (len(members)>MAX_MEMBERS or len(names)!=len(set(names))
                    or sum(i.file_size for i in members)>MAX_TOTAL_UNCOMPRESSED_BYTES):
                raise ValueError('coupon geometry ZIP inventory bound')
            def xml(name):
                if name not in names or archive.getinfo(name).file_size>MAX_XML_BYTES:
                    raise ValueError('coupon geometry XML member bound')
                content=archive.read(name)
                try:text=content.decode('utf-8-sig')
                except UnicodeError as exc:raise ValueError('coupon geometry XML must use UTF-8') from exc
                if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
                    raise ValueError('coupon geometry XML declarations prohibited')
                model=ET.fromstring(text)
                if model.tag!='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}model':
                    raise ValueError('coupon geometry core namespace required')
                if model.get('unit','millimeter')!='millimeter':raise ValueError('coupon geometry millimeter units required')
                return model
            root=xml('3D/3dmodel.model')
            items=root.findall(f'./{CORE}build/{CORE}item');components=root.findall(f'./{CORE}resources/{CORE}object/{CORE}components/{CORE}component')
            objects=root.findall(f'./{CORE}resources/{CORE}object')
            if (len(root.findall(f'./{CORE}resources'))!=1 or len(root.findall(f'./{CORE}build'))!=1
                    or len(items)!=1 or len(components)!=1 or len(objects)!=1 or items[0].get('objectid')!=objects[0].get('id')
                    or len(objects[0].findall(f'./{CORE}components'))!=1):
                raise ValueError('one placed coupon component required')
            transform=tuple(map(F,items[0].attrib['transform'].split()))
            component_transform=tuple(map(F,components[0].attrib['transform'].split()))
            if len(transform)!=12 or transform[:9]!=IDENTITY or component_transform!=IDENTITY+(F(0),F(0),F(0)):
                raise ValueError('coupon geometry pure translation required')
            paths=[v for k,v in components[0].attrib.items() if k.endswith('}path')]
            if len(paths)!=1:raise ValueError('one internal coupon mesh reference required')
            path=paths[0].lstrip('/')
            if '..' in path.split('/') or ':' in path or '\\' in path or not path.startswith('3D/'):
                raise ValueError('external coupon mesh reference prohibited')
            part=xml(path);parts=part.findall(f'./{CORE}resources/{CORE}object')
            if (len(part.findall(f'./{CORE}resources'))!=1 or len(parts)!=1 or parts[0].get('id')!=components[0].get('objectid')
                    or len(parts[0].findall(f'./{CORE}mesh'))!=1
                    or len(parts[0].findall(f'./{CORE}mesh/{CORE}vertices'))!=1
                    or len(parts[0].findall(f'./{CORE}mesh/{CORE}triangles'))!=1):
                raise ValueError('coupon component target differs')
            vertices=tuple(tuple(F(v.attrib[axis])+transform[9+i] for i,axis in enumerate('xyz')) for v in parts[0].findall(f'./{CORE}mesh/{CORE}vertices/{CORE}vertex'))
            faces=tuple(tuple(int(t.attrib[k]) for k in ('v1','v2','v3')) for t in parts[0].findall(f'./{CORE}mesh/{CORE}triangles/{CORE}triangle'))
    except (BadZipFile,ET.ParseError,KeyError,StopIteration,ZeroDivisionError) as exc:
        raise ValueError('invalid coupon geometry archive') from exc
    return vertices,faces,transform


def verify_coupon_profile(geometry_project,profile):
    """Match the legacy placed extrusion, preserving its exact contract."""
    vertices,faces,_=read_coupon_mesh(geometry_project)
    if type(profile) is not tuple or not 2<=len(profile)<=4096 or len(vertices)!=4*len(profile) or len(faces)!=8*(len(profile)-1)+4:
        raise ValueError('coupon profile/mesh count differs')
    if any(type(p) is not tuple or len(p)!=2 or any(type(v) is not F for v in p) for p in profile):
        raise ValueError('exact coupon profile required')
    xs=(min(v[0] for v in vertices),max(v[0] for v in vertices))
    expected=tuple(v for y,z in profile for v in ((xs[0],y,F(0)),(xs[1],y,F(0)),(xs[0],y,z),(xs[1],y,z)))
    if len(set(vertices))!=len(vertices) or set(vertices)!=set(expected) or xs[0]>=xs[1]:
        raise ValueError('coupon placed profile differs from actual geometry')
    expected_faces=[]
    for i in range(len(profile)-1):
        a,b=4*i,4*(i+1)
        expected_faces.extend(((a,b,b+1),(a,b+1,a+1),(a+2,a+3,b+3),(a+2,b+3,b+2),
            (a,b+2,b),(a,a+2,b+2),(a+1,b+1,b+3),(a+1,b+3,a+3)))
    a=4*(len(profile)-1);expected_faces.extend(((0,1,3),(0,3,2),(a,a+2,a+3),(a,a+3,a+1)))
    if any(len(set(f))!=3 or any(index<0 or index>=len(vertices) for index in f) for f in faces):
        raise ValueError('invalid coupon mesh face')
    actual_set={frozenset(vertices[index] for index in f) for f in faces}
    expected_set={frozenset(expected[index] for index in f) for f in expected_faces}
    if len(actual_set)!=len(faces) or actual_set!=expected_set:raise ValueError('coupon extruded mesh faces differ')
    return xs
