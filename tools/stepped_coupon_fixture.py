"""Deterministic Stage A five-degree edge-notch ruler mesh."""
import math
import struct
from functools import lru_cache
from dataclasses import dataclass
from fractions import Fraction as F
from tools.coupon_profile_association import read_coupon_mesh

@dataclass(frozen=True)
class SteppedCouponFixture:
    translation_mm: tuple
    schema_version: int = 1
    serialization_mode: str = 'input-v1'

    def __post_init__(self):
        if type(self.schema_version) is not int or self.schema_version!=1 or self.serialization_mode not in ('input-v1','orca-f32-v1') or type(self.translation_mm) is not tuple or len(self.translation_mm)!=3 or any(type(v) is not F or abs(v)>256 or max(abs(v.numerator).bit_length(),v.denominator.bit_length())>128 for v in self.translation_mm) or self.translation_mm[2]!=0:
            raise ValueError('bounded bed-placed stepped coupon translation required')

    def placed_angle_profile(self):
        vertices,_,center,transform=_serialized_mesh(self)
        _,_,profile,_=stepped_coupon_mesh()
        def placed_y(y):
            if center is None:return F(format(y,'.9f'))+self.translation_mm[1]
            return F(format(_f32(_f32(float(F(format(y,'.9f'))))-center[1]),'.9g'))+transform[1]
        start,end=placed_y(profile[2][0]),placed_y(profile[-2][0])
        boundary={}
        for x,y,z in vertices:
            if x==self.translation_mm[0] and start<=y<=end:
                boundary[y]=max(boundary.get(y,F(0)),z)
        return tuple(sorted(boundary.items()))


def _f32(number):return struct.unpack('f',struct.pack('f',number))[0]


def _serialized_mesh(fixture):
    vertices,faces,_,_=stepped_coupon_mesh()
    if fixture.serialization_mode=='input-v1':
        return tuple(tuple(F(format(v,'.9f'))+fixture.translation_mm[i] for i,v in enumerate(point)) for point in vertices),tuple(faces),None,fixture.translation_mm
    # Pinned Orca import/recenter/export route, independently checked on every coordinate.
    imported=tuple(tuple(_f32(float(F(format(v,'.9f')))) for v in point) for point in vertices)
    center=tuple(_f32((min(p[i] for p in imported)+max(p[i] for p in imported))/2) for i in range(3))
    transform=tuple(F(format(float(fixture.translation_mm[i])+center[i],'.9g')) for i in range(3))
    placed=tuple(tuple(F(format(_f32(point[i]-center[i]),'.9g'))+transform[i] for i in range(3)) for point in imported)
    return placed,tuple(faces),center,transform


def verify_stepped_coupon(geometry_project,profile,fixture):
    if type(fixture) is not SteppedCouponFixture:raise ValueError('typed stepped fixture required')
    vertices,faces,transform=read_coupon_mesh(geometry_project)
    placed,triangles,_,expected_translation=_serialized_mesh(fixture)
    if transform[9:]!=expected_translation or tuple(vertices)!=placed or tuple(faces)!=triangles or profile!=fixture.placed_angle_profile():
        raise ValueError('stepped coupon full mesh/profile association differs')
    return fixture.translation_mm[0],fixture.translation_mm[0]+30


@lru_cache(maxsize=1)
def stepped_coupon_mesh():
 profile=[(0.,1.8),(2.,1.8),(2.,1.9)]
 for k in range(1,46):profile.append((profile[-1][0]+.2/math.tan(math.radians(k)),1.9+.2*k))
 profile.extend(((profile[-1][0]+.1,11.),(profile[-1][0]+1.1,11.)))
 ticks=[]
 for k in range(5,46,5):
  a,b=profile[k+1],profile[k+2];center=(a[0]+b[0])/2;ticks.append((k,center-.225,center+.225))
 ys=sorted(set([y for y,z in profile]+[a for k,a,b in ticks]+[b for k,a,b in ticks]));xs=(-7.,-5.,0.,30.)
 def roof(y,side):
  pairs=[(a,b) for a,b in zip(profile,profile[1:]) if b[0]>a[0] and a[0]-1e-10<=y<=b[0]+1e-10]
  a,b=(pairs[-1] if side=='right' else pairs[0]);return a[1]+(b[1]-a[1])*(y-a[0])/(b[0]-a[0])
 cells={}
 for j,(a,b) in enumerate(zip(ys,ys[1:])):
  mark=any(lo<(a+b)/2<hi for k,lo,hi in ticks)
  for i in range(3):
   if i==0 and not mark:continue
   cells[i,j]=(roof(a,'right'),roof(b,'left')) if i==2 else(.8,.8)
 vertices=[];lookup={};faces=[]
 def vertex(p):
  p=tuple(round(t,9) for t in p)
  if p not in lookup:lookup[p]=len(vertices);vertices.append(p)
  return lookup[p]
 def quad(points):
  indices=tuple(vertex(p) for p in points)
  for tri in (indices[:3],(indices[0],indices[2],indices[3])):
   if len(set(tri))==3:faces.append(tri)
 for (i,j),(ha,hb) in cells.items():
  x,xx=xs[i:i+2];y,yy=ys[j:j+2]
  quad(((x,y,ha),(xx,y,ha),(xx,yy,hb),(x,yy,hb)));quad(((x,y,0),(x,yy,0),(xx,yy,0),(xx,y,0)))
  for di,left in ((-1,True),(1,False)):
   nh=cells.get((i+di,j),(0.,0.));lo,loo=min(ha,nh[0]),min(hb,nh[1])
   if ha<=nh[0] and hb<=nh[1]:continue
   points=((x,y,lo),(x,y,ha),(x,yy,hb),(x,yy,loo)) if left else((xx,y,lo),(xx,yy,loo),(xx,yy,hb),(xx,y,ha));quad(points)
  for dj,front in ((-1,True),(1,False)):
   h=ha if front else hb;neighbor=cells.get((i,j+dj),(0.,0.));low=min(h,neighbor[1] if front else neighbor[0])
   if h<=low:continue
   yp=y if front else yy;points=((x,yp,low),(xx,yp,low),(xx,yp,h),(x,yp,h)) if front else((x,yp,low),(x,yp,h),(xx,yp,h),(xx,yp,low));quad(points)
 # Exact vertical-edge subdivisions ensure watertight main/rail joins.
 final=[]
 for tri in faces:
  queue=[tri]
  while queue:
   current=queue.pop();split=False
   for j in range(3):
    ai,bi,ci=current[j],current[(j+1)%3],current[(j+2)%3];a,b=vertices[ai],vertices[bi]
    varying=[k for k in range(3) if a[k]!=b[k]]
    if len(varying)!=1:continue
    axis=varying[0]
    for pi,p in enumerate(vertices):
     if all(p[k]==a[k] for k in range(3) if k!=axis) and min(a[axis],b[axis])<p[axis]<max(a[axis],b[axis]):
      queue.extend(((ai,pi,ci),(pi,bi,ci)));split=True;break
    if split:break
   if not split:final.append(current)
 edges={}
 for tri in final:
  for a,b in zip(tri,tri[1:]+tri[:1]):edges.setdefault(tuple(sorted((a,b))),[]).append((a,b))
 assert all(len(p)==2 and p[0]==p[1][::-1] for p in edges.values())
 return tuple(vertices),tuple(final),tuple(profile),tuple(ticks)
