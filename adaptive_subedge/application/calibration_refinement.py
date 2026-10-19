"""Proposal-only calibration refinement; no G-code generation or print settings."""
from decimal import Decimal,localcontext,ROUND_HALF_EVEN

AXES={
 'h_volume':(('h_cmd_mm','linear','0.001'),('final_volume_mm3_per_mm','log','0.000001')),
 'retract_wipe':(('retract_mm','linear','0.001'),('wipe_mm','linear','0.001')),
 'startup_extra_speed':(('startup_extra_e_mm','linear','0.00001'),('start_debt_unretract_speed_mm_s','linear','0.001')),
 'volume_speed':(('final_volume_mm3_per_mm','log','0.000001'),('print_speed_mm_s','linear','0.001'))}
AXIS_BOUNDS={'h_volume':(('0.010','0.040'),('0.000075','0.001200')),'retract_wipe':(('0.4','1.6'),('0.25','2.0')),'startup_extra_speed':(('0','0.00020'),('6','30')),'volume_speed':(('0.000075','0.001200'),('5','40'))}
SYMPTOMS=('acceptable','central_ridge','missing_center','end_blob','start_starvation','scraping','none_acceptable')


def refined_axis(values,index,*,scale,quantum,bounds):
    if len(values)!=5 or type(index) is not int or not 0<=index<5:raise ValueError('invalid-refinement-selection')
    try:
        points=tuple(Decimal(v) for v in values);q=Decimal(quantum)
        if any(not p.is_finite() or p<0 for p in points) or not all(a<b for a,b in zip(points,points[1:])) or scale not in ('linear','log') or q<=0:raise ValueError('invalid-refinement-axis')
        with localcontext() as context:
            context.prec=50
            if scale=='log' and points[0]<=0:raise ValueError('log-refinement-needs-positive-axis')
            transformed=tuple(p.ln() for p in points) if scale=='log' else points
            selected=transformed[index]
            lo=(transformed[index-1]+selected)/2 if index else selected-(transformed[1]-selected)/2
            hi=(selected+transformed[index+1])/2 if index<4 else selected+(selected-transformed[3])/2
            if scale=='linear':lo=max(Decimal(0),lo)
            low_bound,high_bound=(Decimal(v) for v in bounds)
            if points[index] in (low_bound,high_bound):raise ValueError('boundary-selection-needs-offline-range-expansion')
            if not 0<=low_bound<=points[index]<=high_bound:raise ValueError('selected-point-outside-approved-stage-bounds')
            low_bound=low_bound.ln() if scale=='log' else low_bound
            high_bound=high_bound.ln() if scale=='log' else high_bound
            lo=max(lo,low_bound);hi=min(hi,high_bound)
            if lo==selected:candidates=tuple(selected+(hi-selected)*Decimal(i)/4 for i in range(5));selected_slot=0
            elif hi==selected:candidates=tuple(lo+(selected-lo)*Decimal(i)/4 for i in range(5));selected_slot=4
            else:candidates=(lo,(lo+selected)/2,selected,(selected+hi)/2,hi);selected_slot=2
            candidates=tuple(p.exp() for p in candidates) if scale=='log' else candidates
            rounded=tuple((p/q).to_integral_value(rounding=ROUND_HALF_EVEN)*q for p in candidates)
            rounded=rounded[:selected_slot]+(points[index],)+rounded[selected_slot+1:]
            if len(set(rounded))!=5 or not all(a<b for a,b in zip(rounded,rounded[1:])) or scale=='log' and rounded[0]<=0:raise ValueError('refinement-grid-not-representable')
            return tuple(format(p,'f') for p in rounded)
    except (ArithmeticError,TypeError) as error:raise ValueError('invalid-refinement-number') from error


def proposal(trial_id,row_values,column_values,cell_id,symptom,*,schema_version=1):
    if trial_id not in AXES or type(cell_id) is not str or len(cell_id)!=2 or not cell_id.isascii() or not cell_id.isdigit() or not 1<=int(cell_id)<=25 or symptom not in SYMPTOMS:raise ValueError('invalid-calibration-selection')
    if type(schema_version) is not int or schema_version not in (1,2) or schema_version==2 and trial_id!='volume_speed':raise ValueError('unsupported-refinement-schema')
    n=int(cell_id)-1;axes=AXES[trial_id];bounds_by_axis=AXIS_BOUNDS[trial_id]
    if schema_version==2:
        axes=(axes[0],('print_speed_ratio','linear','0.001'));bounds_by_axis=(bounds_by_axis[0],('0.2','1'))
    try:
        proposed_axes=[{'name':name,'scale':scale,'quantum':q,'approved_bounds':bounds,'values':refined_axis(values,index,scale=scale,quantum=q,bounds=bounds)} for (name,scale,q),values,index,bounds in zip(axes,(row_values,column_values),(n//5,n%5),bounds_by_axis)]
    except ValueError as error:
        if str(error) not in ('refinement-grid-not-representable','boundary-selection-needs-offline-range-expansion'):raise
        return {'status':'offline_range_expansion_review_required' if str(error)=='boundary-selection-needs-offline-range-expansion' else 'resolution_limit_offline_range_review_required','offline_revalidation_required':True,'trial_id':trial_id,**({'schema_version':2} if schema_version==2 else {}),'selected_cell':cell_id,'symptom':symptom}
    return {'status':'proposal_only_not_generated','offline_revalidation_required':True,'trial_id':trial_id,**({'schema_version':2} if schema_version==2 else {}),'selected_cell':cell_id,'symptom':symptom,
        'axes':proposed_axes}
