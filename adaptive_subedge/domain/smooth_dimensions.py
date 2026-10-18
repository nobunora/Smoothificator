"""Explicit nonlinear geometry mode, independent of empirical E correction."""
from dataclasses import dataclass
from fractions import Fraction as F


@dataclass(frozen=True, slots=True)
class SmoothDimensionPolicy:
    admission_layer_height_mm: F
    admission_minimum_width_mm: F
    maximum_angle_degrees: F
    plateau_end_degrees: F
    minimum_height_mm: F
    minimum_width_mm: F
    dimension_grid_mm: F
    maximum_width_ticks: int
    maximum_extra_width_ticks: int = 1
    schema_version: int = 2
    research_endpoint_envelope: bool = False
    retention_expression: str = "1-(6*t**5-15*t**4+10*t**3)"

    reference_minimum_width_mm: F = F('.1')
    width_tail_start_degrees: F = F(30)
    width_tail_expression: str = "1-(6*t**5-15*t**4+10*t**3)"

    def __post_init__(self):
        for number in (self.admission_layer_height_mm,self.admission_minimum_width_mm,self.maximum_angle_degrees,
                       self.plateau_end_degrees,self.minimum_height_mm,self.minimum_width_mm,self.dimension_grid_mm,
                       self.reference_minimum_width_mm,self.width_tail_start_degrees):
            if type(number) is not F or number < 0 or max(number.numerator.bit_length(),number.denominator.bit_length())>128 or (number*100000000).denominator!=1:
                raise ValueError("invalid-smooth-dimension-number")
        if (not 0 <= self.plateau_end_degrees < self.maximum_angle_degrees < 90
                or not 0 < self.minimum_height_mm < self.admission_layer_height_mm <= 10
                or not 0 < self.admission_minimum_width_mm <= 10
                or not 0 < self.minimum_width_mm <= 10
                or self.schema_version in (1,2) and self.minimum_width_mm < self.admission_minimum_width_mm
                or not self.minimum_height_mm <= self.minimum_width_mm
                or not 0 < self.dimension_grid_mm <= self.minimum_height_mm
                or (self.minimum_height_mm/self.dimension_grid_mm).denominator != 1
                or (self.minimum_width_mm/self.dimension_grid_mm).denominator != 1
                or type(self.maximum_extra_width_ticks) is not int or not 0 <= self.maximum_extra_width_ticks <= 1
                or self.maximum_extra_width_ticks*self.dimension_grid_mm > F('.001')
                or type(self.schema_version) is not int or self.schema_version not in (1,2,3,4,5)
                or type(self.research_endpoint_envelope) is not bool
                or self.research_endpoint_envelope != (self.schema_version == 3)
                or type(self.retention_expression) is not str or not 0 < len(self.retention_expression) <= 512 or not self.retention_expression.isascii()
                or self.schema_version < 4 and self.retention_expression != '1-(6*t**5-15*t**4+10*t**3)'
                or type(self.width_tail_expression) is not str or not 0 < len(self.width_tail_expression) <= 512 or not self.width_tail_expression.isascii()
                or self.schema_version < 5 and (self.reference_minimum_width_mm != F('.1') or self.width_tail_start_degrees != 30 or self.width_tail_expression != '1-(6*t**5-15*t**4+10*t**3)')
                or self.schema_version == 5 and (not self.plateau_end_degrees < self.width_tail_start_degrees < self.maximum_angle_degrees
                    or not self.minimum_width_mm <= self.reference_minimum_width_mm <= 10
                    or (self.reference_minimum_width_mm/self.dimension_grid_mm).denominator != 1)
                or self.schema_version == 3 and (self.minimum_height_mm<F('.01') or self.minimum_width_mm<F('.1'))
                or self.schema_version == 1 and self.maximum_extra_width_ticks != 0
                or type(self.maximum_width_ticks) is not int or not 1 <= self.maximum_width_ticks <= 10000):
            raise ValueError("invalid-smooth-dimension-range")


@dataclass(frozen=True, slots=True)
class SmoothDimensionTargets:
    angle_degrees: F
    retention: F
    target_width_mm: F
    target_height_mm: F
