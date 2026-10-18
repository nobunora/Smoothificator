"""Exact-interval contact over every X on a horizontal candidate centerline.

Inner intervals certify contact; outer intervals give gap witnesses. They
are not finite samples and do not certify contact across the whole bead width.
"""
from fractions import Fraction as F
from math import isqrt
from adaptive_subedge.engine.support_cell import _sqrt_bounds


def _root_bounds(radicand):
    """Keep rational perfect roots exact at shared closed boundaries."""
    numerator,denominator = isqrt(radicand.numerator),isqrt(radicand.denominator)
    if numerator*numerator == radicand.numerator and denominator*denominator == radicand.denominator:
        root = F(numerator,denominator)
        return root,root
    return _sqrt_bounds(radicand,128)


def _interval(source,x0,x1,y,threshold,model,outer):
    sx,sy,z = source.start_xyz_mm
    ex,ey,ez = source.end_xyz_mm
    if z != ez:
        raise ValueError('horizontal baseline source required')
    if threshold > z:
        return None
    w,h = source.width_mm,source.height_mm
    if model == 'nominal':
        radius = h/2
        half = w/2 if threshold <= z-radius else (w-h)/2+_root_bounds(
            radius*radius-(threshold-z+radius)**2)[int(outer)]
    elif model == 'diamond':
        half = min(w/2,w*(z-threshold)/h)
    else:
        raise ValueError('unsupported contact model')
    dx,dy = ex-sx,ey-sy
    squared = dx*dx+dy*dy
    length = _root_bounds(squared)[int(outer)]
    extent = half*length
    axial_extra = w*length/2 if outer and model=='diamond' else F(0)
    lo,hi = x0,x1
    # Each inequality is A*x+B >= 0; all bounds are rational and closed.
    p0 = -sx*dx+(y-sy)*dy
    c0 = -sx*dy-(y-sy)*dx
    for a,b in ((dx,p0+axial_extra),(-dx,squared-p0+axial_extra),
                (dy,c0+extent),(-dy,extent-c0)):
        if a == 0:
            if b < 0:
                return None
        elif a > 0:
            lo = max(lo,-b/a)
        else:
            hi = min(hi,-b/a)
        if lo > hi:
            return None
    return lo,hi


def _union(intervals):
    merged = []
    for a,b in sorted(intervals):
        if merged and a <= merged[-1][1]:
            merged[-1] = merged[-1][0],max(b,merged[-1][1])
        else:
            merged.append((a,b))
    return merged


def audit_line(x0,x1,y,threshold,sources,*,model='nominal'):
    if not x0 < x1:
        raise ValueError('positive centerline length required')
    inner = _union(r for s in sources if (r:=_interval(s,x0,x1,y,threshold,model,False)) is not None)
    if len(inner)==1 and inner[0] == (x0,x1):
        return {'state':'full-centerline-intersection-proven','covered_exact_mm':[[str(x0),str(x1)]],
                'source_count':len(sources),'model':model,'printable_authorized':False}
    outer = _union(r for s in sources if (r:=_interval(s,x0,x1,y,threshold,model,True)) is not None)
    cursor,gaps = x0,[]
    for a,b in outer:
        if a>cursor:
            gaps.append((cursor,a))
        cursor = max(cursor,b)
    if cursor < x1:
        gaps.append((cursor,x1))
    return {'state':'gap-proven' if gaps else 'unresolved',
        'gap_intervals_exact_mm':[[str(a),str(b)] for a,b in gaps],
        'model':model,'printable_authorized':False}


def minimum_centerline_support(x0,x1,y,sources,*,model='nominal',tolerance=F('.001')):
    sources = tuple(s for s in sources if _interval(s,x0,x1,y,
        s.start_xyz_mm[2]-s.height_mm,model,True) is not None)
    if not sources:
        return {'state':'unresolved','reason':'no projected source'}
    high = max(s.start_xyz_mm[2] for s in sources)
    low = high-F(1)
    proof = audit_line(x0,x1,y,low,sources,model=model)
    if proof['state'] != 'full-centerline-intersection-proven':
        return {'state':'unresolved','floor_z_exact_mm':str(low),'floor_audit':proof}
    peak_lower = low
    # Certified point intervals give an existence witness for the supremum;
    # full contact still requires interval coverage of every X above.
    for x in (x0,(x0+x1)/2,x1):
        for s in sources:
            z = s.start_xyz_mm[2]
            if _interval(s,x,x,y,z,model,False) is not None:
                peak_lower = max(peak_lower,z)
    failed_upper = high
    for iteration in range(10):
        if high-low <= tolerance:
            break
        threshold = (low+high)/2
        trial = audit_line(x0,x1,y,threshold,sources,model=model)
        if trial['state']=='full-centerline-intersection-proven':
            low,proof = threshold,trial
        else:
            high = threshold
            if trial['state']=='gap-proven':
                failed_upper = min(failed_upper,threshold)
    return {'state':'full-bounded','minimum_lower_exact_mm':str(low),
        'minimum_upper_exact_mm':str(failed_upper),'peak_lower_exact_mm':str(peak_lower),
        'minimum_lower_mm':float(low),'minimum_upper_mm':float(failed_upper),
        'minimum_bracket_width_mm':float(failed_upper-low),'whole_centerline_certificate':proof,
        'contact_scope':'continuous horizontal centerline; full bead width not certified'}
