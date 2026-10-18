"""ADR0070 angle precision and empirical volume interpolation; no geometry policy."""
from decimal import Decimal, ROUND_HALF_EVEN
from fractions import Fraction as F
from math import atan, degrees, sqrt, isfinite
from adaptive_subedge.domain.empirical_material import EmpiricalMaterialPolicy, EmpiricalMaterialFactor, ModeledThicknessProof

ANGLE_DECIMAL_PLACES = 8


def _angle(number):
    if not isfinite(number):
        raise ValueError("nonfinite-material-angle")
    return F(Decimal(str(number)).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_EVEN))


def admission_maximum_angle(layer_height_mm, minimum_width_mm):
    if (any(type(v) is not F or v <= 0 or v > 10
            or max(v.numerator.bit_length(), v.denominator.bit_length()) > 128
            for v in (layer_height_mm, minimum_width_mm))):
        raise ValueError("invalid-admission-angle-input")
    return _angle(degrees(atan(float(layer_height_mm) / (sqrt(2) * float(minimum_width_mm)))))


def resolve_policy(*, admission_layer_height_mm=F(".2"), admission_minimum_width_mm=F(".21"),
                   start_percent=F(100), end_percent=F(25), retract_mm=F("1.6"), wipe_mm=F(1),
                   minimum_modeled_thickness_mm=F(".08")):
    return EmpiricalMaterialPolicy(admission_layer_height_mm, admission_minimum_width_mm,
        admission_maximum_angle(admission_layer_height_mm, admission_minimum_width_mm),
        start_percent, end_percent, retract_mm, wipe_mm, minimum_modeled_thickness_mm)


def validate_resolved_policy(policy):
    if (type(policy) is not EmpiricalMaterialPolicy or policy.maximum_angle_degrees !=
            admission_maximum_angle(policy.admission_layer_height_mm, policy.admission_minimum_width_mm)):
        raise ValueError("empirical-derived-angle-mismatch")
    return policy


def factor_for_angle(angle_degrees, policy):
    validate_resolved_policy(policy)
    if (type(angle_degrees) is not F or not 0 <= angle_degrees < 90
            or (angle_degrees * 100000000).denominator != 1):
        raise ValueError("invalid-serialized-material-angle")
    t = min(F(1), angle_degrees / policy.maximum_angle_degrees)
    factor = (policy.start_percent + t * (policy.end_percent - policy.start_percent)) / 100
    return EmpiricalMaterialFactor(angle_degrees, policy.maximum_angle_degrees, factor)


def section_angle_degrees(base_mm, rise_mm):
    if any(type(v) is not F or v < 0 or max(v.numerator.bit_length(), v.denominator.bit_length()) > 128
           for v in (base_mm, rise_mm)) or base_mm <= 0:
        raise ValueError("invalid-material-section")
    return _angle(degrees(atan(float(rise_mm / base_mm))))


def factor_for_section(base_mm, rise_mm, policy):
    return factor_for_angle(section_angle_degrees(base_mm, rise_mm), policy)


def _atan_enclosure(inverse, terms=40):
    # Alternating arctan series: remainder lies between consecutive partial sums.
    x = F(1, inverse)
    partial = sum(((-1)**k * x**(2*k+1) / (2*k+1) for k in range(terms)), F(0))
    adjacent = partial + (-1)**terms * x**(2*terms+1) / (2*terms+1)
    return min(partial, adjacent), max(partial, adjacent)


_A5_LOW, _A5_HIGH = _atan_enclosure(5)
_A239_LOW, _A239_HIGH = _atan_enclosure(239)
# Machin identity pi = 16 atan(1/5) - 4 atan(1/239).
PI_LOWER = 16 * _A5_LOW - 4 * _A239_HIGH
PI_UPPER = 16 * _A5_HIGH - 4 * _A239_LOW


def compare_modeled_minimum_thickness(*, corrected_e_mm, filament_diameter_mm, length_mm,
                                      flow_multiplier, nominal_width_mm, minimum_height_mm):
    numbers = (corrected_e_mm, filament_diameter_mm, length_mm, flow_multiplier,
               nominal_width_mm, minimum_height_mm)
    if any(type(v) is not F or v <= 0 or max(v.numerator.bit_length(), v.denominator.bit_length()) > 256
           for v in numbers) or minimum_height_mm > nominal_width_mm:
        raise ValueError("invalid-modeled-thickness-input")
    coefficient = corrected_e_mm * filament_diameter_mm**2 / (4*length_mm*flow_multiplier) - minimum_height_mm**2/4
    constant = nominal_width_mm*minimum_height_mm - minimum_height_mm**2
    lower, upper = sorted((PI_LOWER*coefficient-constant, PI_UPPER*coefficient-constant))
    accepted = lower >= 0
    state = "proven-at-least-minimum" if accepted else "proven-below-minimum" if upper < 0 else "unresolved-pi-enclosure"
    return ModeledThicknessProof(accepted, state, lower, upper)
