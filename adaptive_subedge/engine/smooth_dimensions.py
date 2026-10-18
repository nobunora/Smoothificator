"""ADR0071 exact quintic targets; native tools own quantization and refreeze."""
from fractions import Fraction as F
from adaptive_subedge.domain.smooth_dimensions import SmoothDimensionPolicy, SmoothDimensionTargets
from adaptive_subedge.engine.retention_polynomial import DEFAULT_RETENTION_EXPRESSION, retention_coefficients, retention_for_t
from adaptive_subedge.engine.empirical_material import admission_maximum_angle, section_angle_degrees


def resolve_policy(*,admission_layer_height_mm=F('.2'),admission_minimum_width_mm=F('.21'),
                   plateau_end_degrees=F(10),minimum_height_mm=F('.08'),minimum_width_mm=F('.21'),
                   dimension_grid_mm=F('.001'),maximum_width_ticks=1000,maximum_extra_width_ticks=1,schema_version=2,research_endpoint_envelope=False,retention_expression=DEFAULT_RETENTION_EXPRESSION,
                   reference_minimum_width_mm=F('.1'),width_tail_start_degrees=F(30),width_tail_expression=DEFAULT_RETENTION_EXPRESSION):
    return validate_resolved_policy(SmoothDimensionPolicy(admission_layer_height_mm,admission_minimum_width_mm,
        admission_maximum_angle(admission_layer_height_mm,admission_minimum_width_mm),plateau_end_degrees,
        minimum_height_mm,minimum_width_mm,dimension_grid_mm,maximum_width_ticks,maximum_extra_width_ticks,schema_version,research_endpoint_envelope,retention_expression,reference_minimum_width_mm,width_tail_start_degrees,width_tail_expression))


def validate_resolved_policy(policy):
    if type(policy) is not SmoothDimensionPolicy or policy.maximum_angle_degrees != admission_maximum_angle(policy.admission_layer_height_mm,policy.admission_minimum_width_mm):
        raise ValueError('smooth-dimension-derived-angle-mismatch')
    retention_coefficients(policy.retention_expression)
    if policy.schema_version >= 5:retention_coefficients(policy.width_tail_expression)
    return policy


def target_dimensions_for_angle(angle_degrees,original_width_mm,original_height_mm,policy):
    validate_resolved_policy(policy)
    if (type(angle_degrees) is not F or not 0<=angle_degrees<90 or (angle_degrees*100000000).denominator!=1
            or any(type(v) is not F or max(v.numerator.bit_length(),v.denominator.bit_length())>128 for v in (original_width_mm,original_height_mm))
            or not policy.minimum_height_mm<=original_height_mm<policy.admission_layer_height_mm
            or not policy.minimum_width_mm<=original_width_mm<=10 or original_height_mm>original_width_mm):
        raise ValueError('invalid-smooth-dimension-original')
    if policy.schema_version >= 5 and original_width_mm < policy.reference_minimum_width_mm:
        raise ValueError('smooth-dimension-original-below-reference-width')
    t=max(F(0),min(F(1),(angle_degrees-policy.plateau_end_degrees)/(policy.maximum_angle_degrees-policy.plateau_end_degrees)))
    retention=retention_for_t(policy.retention_expression,t)
    baseline_minimum_width = policy.reference_minimum_width_mm if policy.schema_version >= 5 else policy.minimum_width_mm
    width=baseline_minimum_width+(original_width_mm-baseline_minimum_width)*retention
    height=policy.minimum_height_mm+(original_height_mm-policy.minimum_height_mm)*retention
    if policy.schema_version >= 5 and angle_degrees > policy.width_tail_start_degrees:
        u=min(F(1),(angle_degrees-policy.width_tail_start_degrees)/(policy.maximum_angle_degrees-policy.width_tail_start_degrees))
        tail=retention_for_t(policy.width_tail_expression,u)
        width=tail*width+(1-tail)*policy.minimum_width_mm
    if height>width:raise ValueError('smooth-dimension-target-height-exceeds-width')
    return SmoothDimensionTargets(angle_degrees,retention,width,height)


def target_dimensions_for_section(base_mm,rise_mm,original_width_mm,original_height_mm,policy):
    validate_resolved_policy(policy)
    angle=section_angle_degrees(base_mm,rise_mm)
    return target_dimensions_for_angle(angle,original_width_mm,original_height_mm,policy)


def resolve_user_policy(**settings):
    version=settings.get('schema_version',5)
    defaults=dict(schema_version=version,minimum_height_mm=F('.01'),minimum_width_mm=F('.02') if version>=5 else F('.1'))
    defaults.update(settings)
    return resolve_policy(**defaults)
