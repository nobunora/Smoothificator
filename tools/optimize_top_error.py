"""Numerical full-face error optimization, balanced around the target plane.

Finite search and quadrature are not global geometric/contact certificates.
Uses only the standard library and the source-bound offline research fixture.
"""
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from fractions import Fraction as F
import hashlib
import json
import math

from tools.build_tilted_cuboid_review import ROOT, baseline, sliced_top_face, slicer_height_limit


@dataclass(frozen=True)
class Proposal:
    terrace: str
    y: F
    width: F
    height: F
    fraction: F
    z: F
    gain: float

    @property
    def left(self):
        return self.y-self.width/2

    @property
    def right(self):
        return self.y+self.width/2


def bead_top(distance,width,height,z):
    if distance > width/2:
        return -math.inf
    side = max(0.,distance-(width-height)/2)
    return z-height/2+math.sqrt(max(0.,(height/2)**2-side**2))


def source_grid(rows,metadata,bounds,nx,ny):
    x0,x1,y0,y1 = map(float,bounds)
    dx,dy = (x1-x0)/nx,(y1-y0)/ny
    xs = [x0+(i+.5)*dx for i in range(nx)]
    ys = [y0+(j+.5)*dy for j in range(ny)]
    grid = [[-math.inf]*nx for j in range(ny)]
    unsupported_ceiling = -math.inf
    for z,ax,ay,bx,by,w,number in sorted(rows,reverse=True):
        h = float(metadata[number][1])
        if w < h:
            unsupported_ceiling = max(unsupported_ceiling,z)
            continue
        ix0 = max(0,math.ceil((min(ax,bx)-w/2-x0)/dx-.5))
        ix1 = min(nx-1,math.floor((max(ax,bx)+w/2-x0)/dx-.5))
        iy0 = max(0,math.ceil((min(ay,by)-w/2-y0)/dy-.5))
        iy1 = min(ny-1,math.floor((max(ay,by)+w/2-y0)/dy-.5))
        vx,vy = bx-ax,by-ay
        length2 = vx*vx+vy*vy
        length = math.sqrt(length2)
        for j in range(iy0,iy1+1):
            yy = ys[j]-ay
            row = grid[j]
            for i in range(ix0,ix1+1):
                if row[i] >= z:
                    continue
                xx = xs[i]-ax
                t = (xx*vx+yy*vy)/length2
                if not 0<=t<=1:
                    continue
                distance = abs(xx*vy-yy*vx)/length
                top = bead_top(distance,w,h,z)
                if top>row[i]:
                    row[i] = top
    for row in grid:
        for i,value in enumerate(row):
            if value == -math.inf or value <= unsupported_ceiling:
                row[i] = None
    return xs,ys,grid


def metrics(grid,ys,slope,intercept):
    count = sum(sum(z is not None for z in row) for row in grid)
    if not count:
        raise ValueError('no evaluable source surface')
    total = squared = shortage = excess = maximum = 0.
    for y,row in zip(ys,grid):
        target = float(slope)*y+float(intercept)
        for z in row:
            if z is None:
                continue
            error = z-target
            total += abs(error)
            squared += error*error
            shortage += max(0.,-error)
            excess += max(0.,error)
            maximum = max(maximum,abs(error))
    return {'mean_absolute_vertical_mm':total/count,'rms_vertical_mm':math.sqrt(squared/count),
        'maximum_sampled_absolute_vertical_mm':maximum,'mean_shortage_mm':shortage/count,
        'mean_excess_mm':excess/count,
        'evaluated_point_count':count,'missing_source_coverage_point_count':sum(map(len,grid))-count,
        'mean_absolute_plane_normal_mm':total/count/math.sqrt(1+float(slope)**2)}


def apply_proposals(grid,xs,ys,proposals,x0,x1):
    result = [row.copy() for row in grid]
    for p in proposals:
        w,h,y,z = map(float,(p.width,p.height,p.y,p.z))
        for j,yy in enumerate(ys):
            top = bead_top(abs(yy-y),w,h,z)
            if top == -math.inf:
                continue
            for i,x in enumerate(xs):
                if float(x0)<=x<=float(x1):
                    if result[j][i] is None:
                        raise ValueError('candidate affects an unevaluable source sample')
                    result[j][i] = max(result[j][i],top)
    return result


def best_nonoverlapping(proposals):
    """Exact weighted interval scheduling on the finite candidate set."""
    ordered = sorted((p for p in proposals if p.gain>0),key=lambda p:(p.right,p.left))
    rights = [p.right for p in ordered]
    scores = [0.]
    paths = [()]
    for i,p in enumerate(ordered):
        predecessor = bisect_right(rights,p.left,0,i)
        score = scores[predecessor]+p.gain
        if score>scores[-1]+1e-14:
            scores.append(score)
            paths.append(paths[predecessor]+(p,))
        else:
            scores.append(scores[-1])
            paths.append(paths[-1])
    return paths[-1]


def search(grid,xs,ys,bounds,slope,intercept,groups,maximum_height):
    inside = [i for i,x in enumerate(xs) if float(bounds[0])+0.3<=x<=float(bounds[1])-0.3]
    distributions = []
    for y,row in zip(ys,grid):
        target = float(slope)*y+float(intercept)
        if any(row[i] is None for i in inside):
            raise ValueError('unresolved source coverage in the candidate X domain')
        values = sorted(row[i] for i in inside)
        prefix = [0.]
        for value in values:
            prefix.append(prefix[-1]+abs(target-value))
        distributions.append((target,values,prefix))
    heights = tuple(F(i,1000) for i in range(50,int(maximum_height*1000)+1,5))
    by_height = {h:[] for h in heights}
    adaptive = []
    evaluated = 0
    for group in groups:
        floor = F(group['rectangle_exact_mm'][2])
        frontier = F(group['rectangle_exact_mm'][1])
        terrace = str(floor)
        best_footprint = {}
        uniform_footprints = {h:{} for h in heights}
        for width_index in range(25,46):
            w = F(width_index,100)
            for position_index in range(-18,9):
                y = frontier+F(position_index,40)
                if y-w/2<bounds[2] or y+w/2>bounds[3]:
                    continue
                j0,j1 = bisect_left(ys,float(y-w/2)),bisect_right(ys,float(y+w/2))
                middle = slope*y+intercept
                for h in heights:
                    for f in (F('-.1'),F('-.05'),F(0),F('.05'),F('.1')):
                        z = floor+h*(1+f)
                        # Center between inscribed and circumscribed levels;
                        # permit only a line-relative 10% deviation from it.
                        if abs(z-middle)>h/10:
                            continue
                        evaluated += 1
                        gain = 0.
                        for j in range(j0,j1):
                            top = bead_top(abs(ys[j]-float(y)),float(w),float(h),float(z))
                            target,values,prefix = distributions[j]
                            k = bisect_left(values,top)
                            gain += prefix[k]-k*abs(target-top)
                        p = Proposal(terrace,y,w,h,f,z,gain)
                        key = (y,w)
                        if gain>0 and (key not in best_footprint or gain>best_footprint[key].gain):
                            best_footprint[key] = p
                        if gain>0 and (key not in uniform_footprints[h] or gain>uniform_footprints[h][key].gain):
                            uniform_footprints[h][key] = p
        adaptive.extend(best_nonoverlapping(best_footprint.values()))
        for h in heights:
            by_height[h].extend(best_nonoverlapping(uniform_footprints[h].values()))
    # Terrace candidate bands are disjoint in this fixture. Verify that the
    # separate scheduling problems did not hide cross-terrace interactions.
    ordered = sorted(adaptive,key=lambda p:p.left)
    if any(a.right>b.left for a,b in zip(ordered,ordered[1:])):
        raise ValueError('cross-terrace overlap requires a joint optimizer')
    return tuple(adaptive),by_height,evaluated


def encode(p):
    return {'terrace_z_exact_mm':p.terrace,'y_exact_mm':str(p.y),'width_exact_mm':str(p.width),
        'height_exact_mm':str(p.height),'offset_fraction_exact':str(p.fraction),
        'top_z_exact_mm':str(p.z),'sampled_error_sum_reduction':p.gain}


def run(source,project,plan):
    digest = hashlib.sha256(source).hexdigest()
    if digest!=plan['source_slice_sha256'] or hashlib.sha256(project).hexdigest()!=plan['placed_project_sha256']:
        raise ValueError('unpinned source or placed model')
    bounds,slope,intercept = sliced_top_face(project)
    configured,maximum_height = slicer_height_limit(source)
    rows,exact,metadata,omitted = baseline(source,digest,F(2))
    groups = [g for g in plan['section_diagnostics'] if g['reason']=='rectangle-line-tiling']
    xs,ys,grid = source_grid(rows,metadata,bounds,64,384)
    selected,uniform,evaluated = search(grid,xs,ys,bounds,slope,intercept,groups,maximum_height)
    x0,x1 = bounds[0]+F('.3'),bounds[1]-F('.3')
    old = []
    for g in groups:
        _,_,bottom,z = map(F,g['rectangle_exact_mm'])
        for a,b in g['line_intervals_exact_mm']:
            a,b = F(a),F(b)
            h = z-bottom
            old.append(Proposal(str(bottom),(a+b)/2,b-a,h,F('-.1'),z-h/10,0))
    height_table = []
    for h,proposals in uniform.items():
        trial = apply_proposals(grid,xs,ys,proposals,x0,x1)
        height_table.append({'height_mm':float(h),'line_count':len(proposals),
                             'metrics':metrics(trial,ys,slope,intercept)})
    # Independent finer quadrature: same whole face, never selected footprints.
    vx,vy,validation = source_grid(rows,metadata,bounds,128,768)
    best_uniform_height = min(uniform,key=lambda h:metrics(
        apply_proposals(grid,xs,ys,uniform[h],x0,x1),ys,slope,intercept)['mean_absolute_vertical_mm'])
    comparisons = {}
    for name,proposals in (('baseline',()),('previous_inscribed',old),
            ('balanced_fixed_minimum_height',uniform[F('.05')]),
            ('balanced_best_uniform_height',uniform[best_uniform_height]),
            ('optimized_balanced',selected)):
        comparisons[name] = metrics(apply_proposals(validation,vx,vy,proposals,x0,x1),vy,slope,intercept)
    stable = comparisons['optimized_balanced']['mean_absolute_vertical_mm'] <= comparisons['previous_inscribed']['mean_absolute_vertical_mm']
    return {'scope':'sampled-full-face-balanced-error-research-only','source_slice_sha256':digest,
        'placed_project_sha256':plan['placed_project_sha256'],'target_bounds_exact_mm':list(map(str,bounds)),
        'target_plane_exact':[str(slope),str(intercept)],'original_segment_count':len(rows),
        'objective':'equal-weight mean absolute vertical error on fixed source-evaluable projected-face samples; equivalent plane-normal ordering',
        'optimization_grid':[64,384],'validation_grid':[128,768],
        'candidate_count_evaluated':evaluated,'chosen_line_count':len(selected),
        'selected':[encode(p) for p in selected],'fixed_height_search':height_table,
        'best_uniform_height_mm':float(best_uniform_height),
        'validation_comparison':comparisons,'validation_improves_previous':stable,
        'unevaluated_validation_fraction':comparisons['baseline']['missing_source_coverage_point_count']/(128*768),
        'unevaluated_samples_affected_by_any_selected_line':False,
        'constraints_mm':{'minimum_width':.25,'maximum_width':.45,'minimum_height':.05,
                          'maximum_height':float(maximum_height)},
        'maximum_offset_fraction_exact':'1/10','placement':'within line-height/10 of the midpoint target level',
        'global_continuous_minimum_proven':False,'continuous_contact_verified':False,
        'shape_improvement_certified':False,'printable_authorized':False,
        'limitations':'Finite parameter search and independent midpoint quadrature, not continuous area/contact or global-optimality proof. Overshoot and shortage are both penalized; no inscribed-only cap.'}


def main():
    folder = ROOT/'artifacts/cuboid-tilt10-review'
    report = run((folder/'original-slice/plate_1.gcode').read_bytes(),
        (folder/'original-slice/sliced.3mf').read_bytes(),json.loads((folder/'current-review.json').read_text()))
    (folder/'balanced-error-optimization.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('selected','fixed_height_search')},indent=2))


if __name__ == '__main__':
    main()
