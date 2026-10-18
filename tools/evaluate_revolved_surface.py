"""Actual placed triangular revolution surface and fixed-XY error quadrature."""
from bisect import bisect_right
from fractions import Fraction as F
import json
import math

from tools.revolved_exponential_fixture import REVIEW_FOLDER, ANGULAR_PANELS, PANELS, placed_geometry
from tools.build_tilted_cuboid_review import baseline
from tools.optimize_top_error import source_grid
from tools.evaluate_curved_surface import ANGLE_BINS, angle_bin_index, summarize, write_csv


def triangle_height(a,b,c,x,y):
    ax,ay,az = a
    bx,by,bz = b
    cx,cy,cz = c
    denominator = (bx-ax)*(cy-ay)-(cx-ax)*(by-ay)
    u = ((x-ax)*(cy-ay)-(cx-ax)*(y-ay))/denominator
    v = ((bx-ax)*(y-ay)-(x-ax)*(by-ay))/denominator
    if min(u,v,1-u-v)<-1e-7:
        return None
    gx = ((bz-az)*(cy-ay)-(cz-az)*(by-ay))/denominator
    gy = ((bx-ax)*(cz-az)-(cx-ax)*(bz-az))/denominator
    return az+u*(bz-az)+v*(cz-az),math.hypot(gx,gy)


def target_at_xy(center,radii,vertices,x,y):
    dx,dy = x-center[0],y-center[1]
    phi = math.atan2(dy,dx)%(2*math.pi)
    sector = int(phi*ANGULAR_PANELS/(2*math.pi))%ANGULAR_PANELS
    mid = (sector+.5)*2*math.pi/ANGULAR_PANELS
    radial = (dx*math.cos(mid)+dy*math.sin(mid))/math.cos(math.pi/ANGULAR_PANELS)
    if radial>radii[-1]+1e-7:
        return None
    index = min(PANELS-1,max(0,bisect_right(radii,radial)-1))
    for angular in (sector,(sector-1)%ANGULAR_PANELS,(sector+1)%ANGULAR_PANELS):
        j,k = angular,(angular+1)%ANGULAR_PANELS
        for band in (index,index-1,index+1):
            if not 0<=band<PANELS:
                continue
            if band==0:
                faces = ((vertices[1],vertices[2+j],vertices[2+k]),)
            else:
                a,b = 2+(band-1)*ANGULAR_PANELS,2+band*ANGULAR_PANELS
                faces = ((vertices[a+j],vertices[b+j],vertices[b+k]),
                         (vertices[a+j],vertices[b+k],vertices[a+k]))
            for face in faces:
                value = triangle_height(*face,x,y)
                if value is not None:
                    return value
    raise ValueError('inside revolution footprint but no target triangle found')


def evaluate(source,project,manifest,*,nx,ny):
    center,top,vertices = placed_geometry(project)
    radius = top[-1][0]
    radii = [float(r) for r,z in top]
    bounds = tuple(F(str(v)) for v in (center[0]-float(radius),center[0]+float(radius),
                                      center[1]-float(radius),center[1]+float(radius)))
    rows,_,metadata,_ = baseline(source,manifest['source_slice_sha256'],F(2))
    if any(w<float(metadata[n][1]) for _,_,_,_,_,w,n in rows):
        raise ValueError('unsupported nominal source bead')
    xs,ys,before = source_grid(rows,metadata,bounds,nx,ny)
    combined = list(rows)
    next_line = max(metadata)+1
    for c in manifest['candidate_segments']:
        ax,ay,z = c['start_mm']
        bx,by,_ = c['end_mm']
        combined.append((z,ax,ay,bx,by,c['width_mm'],next_line))
        metadata[next_line] = ('Custom',F(str(c['height_mm'])))
        next_line += 1
    _,_,after = source_grid(combined,metadata,bounds,nx,ny)
    buckets = [[[],[],0,0] for _ in ANGLE_BINS]
    for y,a,b in zip(ys,before,after):
        for x,old,new in zip(xs,a,b):
            target = target_at_xy(center,radii,vertices,x,y)
            if target is None:
                continue
            z,slope = target
            index = angle_bin_index(slope)
            if old is None:
                buckets[index][2] += 1
                buckets[index][3] += new is not None
                continue
            if new is None or new<old-1e-12:
                raise ValueError('candidate union lost original surface')
            buckets[index][0].append(old-z)
            buckets[index][1].append(new-z)
    bins = []
    for angles,(a,b,missing,filled) in zip(ANGLE_BINS,buckets):
        original,result = summarize(a,missing),summarize(b,missing)
        bins.append({'angle_degrees':list(angles),'before':original,'after':result,
            'mae_change_fraction':None if not a or original['mae_vertical_mm']==0 else
                result['mae_vertical_mm']/original['mae_vertical_mm']-1,
            'empty_baseline_columns_filled_by_candidates':filled})
    return {'grid':[nx,ny],'source_covered_only_angle_bins':bins,
        'domain':'actual placed revolved mesh XY footprint; fixed common source-covered mask',
        'target':'barycentric height and facet gradient of actual exported top triangles',
        'continuous_surface_or_contact_certificate':False}


def main():
    folder = REVIEW_FOLDER
    manifest = json.loads((folder/'current-review.json').read_text())
    source = (folder/'original-slice/plate_1.gcode').read_bytes()
    project = (folder/'original-slice/sliced.3mf').read_bytes()
    report = {'source_slice_sha256':manifest['source_slice_sha256'],
        'placed_project_sha256':manifest['placed_project_sha256'],
        'viewer_sha256':manifest['viewer_sha256'],
        'coarse':evaluate(source,project,manifest,nx=256,ny=256),
        'fine':evaluate(source,project,manifest,nx=512,ny=512)}
    (folder/'angle-errors.json').write_text(json.dumps(report,indent=2)+'\n')
    write_csv(folder/'angle-errors.csv',report['fine'])
    print(json.dumps(report['fine'],indent=2))


if __name__=='__main__':
    main()
