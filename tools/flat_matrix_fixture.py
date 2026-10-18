"""Deterministic one-piece flat 25-line experiment substrate and seven-segment IDs."""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
import struct
from tools.coupon_profile_association import read_coupon_mesh

DIGITS=('abcdef','bc','abdeg','abcdg','bcfg','acdfg','acdefg','abc','abcdefg','abcdfg')
ROWS=tuple(map(F,('.010','.015','.020','.030','.040')))
VOLUMES=tuple(map(F,('.000075','.000150','.000300','.000600','.001200')))

@dataclass(frozen=True)
class FlatMatrixFixture:
    translation_mm: tuple=(F(58),F(58),F(0))
    serialization_mode: str='orca-f32-v1'
    schema_version: int=1
    def __post_init__(self):
        if type(self.translation_mm) is not tuple or any(type(v) is not F for v in self.translation_mm) or type(self.serialization_mode) is not str or type(self.schema_version) is not int or self.schema_version!=1 or self.translation_mm!=(F(58),F(58),F(0)) or self.serialization_mode not in ('input-v1','orca-f32-v1'):
            raise ValueError('closed flat-matrix fixture placement and serialization required')


def matrix_cells():
    return tuple({'id':f'{row*5+col+1:02d}','row':row+1,'column':col+1,'h_cmd_mm':ROWS[row],'final_volume_mm3_per_mm':VOLUMES[col],
      'start_xy_mm':(F(58+8+12*col-5),F(58+6+12*row)),
      'end_xy_mm':(F(58+8+12*col+5),F(58+6+12*row)),
      'label_origin_xy_mm':(F(58+8+12*col)-F('2.2'),F(58+6+12*row+3))} for row in range(5) for col in range(5))


def label_rectangles():
    rectangles=[];w,h,s=F('1.9'),F('3.5'),F('.6')
    bars={'a':(0,w,h-s,h),'d':(0,w,0,s),'g':(0,w,(h-s)/2,(h+s)/2),
      'f':(0,s,h/2,h),'b':(w-s,w,h/2,h),'e':(0,s,0,h/2),'c':(w-s,w,0,h/2)}
    for cell in matrix_cells():
        ox,oy=cell['label_origin_xy_mm'];ox-=58;oy-=58
        for i,digit in enumerate(cell['id']):
            for bar in DIGITS[int(digit)]:
                x0,x1,y0,y1=map(F,bars[bar]);rectangles.append((ox+i*F('2.5')+x0,ox+i*F('2.5')+x1,oy+y0,oy+y1,cell['id']))
    return tuple(rectangles)

@lru_cache(maxsize=1)
def flat_matrix_mesh():
    rectangles=label_rectangles();xs=sorted({F(0),F(64),*(v for r in rectangles for v in r[:2])});ys=sorted({F(0),F(64),*(v for r in rectangles for v in r[2:4])})
    heights={}
    for i,(x,xx) in enumerate(zip(xs,xs[1:])):
        for j,(y,yy) in enumerate(zip(ys,ys[1:])):
            midx,midy=(x+xx)/2,(y+yy)/2
            heights[i,j]=F(1) if any(a<midx<b and c<midy<d for a,b,c,d,_ in rectangles) else F('.8')
    vertices=[];lookup={};faces=[]
    def vertex(point):
        if point not in lookup:lookup[point]=len(vertices);vertices.append(point)
        return lookup[point]
    def quad(points):
        a,b,c,d=map(vertex,points);faces.extend(((a,b,c),(a,c,d)))
    for (i,j),h in heights.items():
        x,xx=xs[i:i+2];y,yy=ys[j:j+2]
        quad(((x,y,h),(xx,y,h),(xx,yy,h),(x,yy,h)));quad(((x,y,F(0)),(x,yy,F(0)),(xx,yy,F(0)),(xx,y,F(0))))
        for di in (-1,1):
            low=heights.get((i+di,j),F(0))
            if h<=low:continue
            quad(((x,y,low),(x,y,h),(x,yy,h),(x,yy,low)) if di<0 else ((xx,y,low),(xx,yy,low),(xx,yy,h),(xx,y,h)))
        for dj in (-1,1):
            low=heights.get((i,j+dj),F(0))
            if h<=low:continue
            yp=y if dj<0 else yy
            quad(((x,yp,low),(xx,yp,low),(xx,yp,h),(x,yp,h)) if dj<0 else ((x,yp,low),(x,yp,h),(xx,yp,h),(xx,yp,low)))
    edges={}
    for face in faces:
        for a,b in zip(face,face[1:]+face[:1]):edges.setdefault(tuple(sorted((a,b))),[]).append((a,b))
    if not all(len(e)==2 and e[0]==e[1][::-1] for e in edges.values()):raise ValueError('matrix mesh must be closed oriented manifold')
    return tuple(vertices),tuple(faces)


def _f32(value):return struct.unpack('f',struct.pack('f',value))[0]


def serialized_matrix_mesh(fixture):
    if type(fixture) is not FlatMatrixFixture:raise ValueError('typed flat fixture required')
    vertices,faces=flat_matrix_mesh()
    if fixture.serialization_mode=='input-v1':return tuple(tuple(c+fixture.translation_mm[i] for i,c in enumerate(p)) for p in vertices),faces,fixture.translation_mm
    imported=tuple(tuple(_f32(float(c)) for c in p) for p in vertices);center=tuple(_f32((min(p[i] for p in imported)+max(p[i] for p in imported))/2) for i in range(3));transform=tuple(F(format(float(fixture.translation_mm[i])+center[i],'.9g')) for i in range(3))
    return tuple(tuple(F(format(_f32(p[i]-center[i]),'.9g'))+transform[i] for i in range(3)) for p in imported),faces,transform


def verify_flat_matrix(geometry_project,fixture):
    actual,faces,transform=read_coupon_mesh(geometry_project);expected,triangles,translation=serialized_matrix_mesh(fixture)
    if actual!=expected or faces!=triangles or transform[9:]!=translation:raise ValueError('flat matrix exact full mesh association differs')
    return matrix_cells()
