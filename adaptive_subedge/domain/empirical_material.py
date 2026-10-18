"""Immutable experimental commanded-volume settings, separate from Settings v1/v2."""
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True, slots=True)
class EmpiricalMaterialPolicy:
    admission_layer_height_mm: Fraction
    admission_minimum_width_mm: Fraction
    maximum_angle_degrees: Fraction
    start_percent: Fraction
    end_percent: Fraction
    retract_mm: Fraction
    wipe_mm: Fraction
    minimum_modeled_thickness_mm: Fraction | None = None

    def __post_init__(self):
        for number in (self.admission_layer_height_mm, self.admission_minimum_width_mm,
                       self.maximum_angle_degrees, self.start_percent, self.end_percent,
                       self.retract_mm, self.wipe_mm):
            if (type(number) is not Fraction or number <= 0
                    or max(number.numerator.bit_length(), number.denominator.bit_length()) > 128
                    or (number * 100000000).denominator != 1):
                raise ValueError("invalid-empirical-material-number")
        threshold = self.minimum_modeled_thickness_mm
        if threshold is not None and (type(threshold) is not Fraction or not 0 < threshold <= self.admission_minimum_width_mm
                or max(threshold.numerator.bit_length(), threshold.denominator.bit_length()) > 128
                or (threshold * 100000000).denominator != 1):
            raise ValueError("invalid-modeled-thickness-threshold")
        if (not 0 < self.end_percent <= self.start_percent <= 100
                or self.maximum_angle_degrees >= 90
                or self.admission_layer_height_mm > 10 or self.admission_minimum_width_mm > 10
                or self.retract_mm > 10 or self.wipe_mm > 100):
            raise ValueError("invalid-empirical-material-range")


@dataclass(frozen=True, slots=True)
class EmpiricalMaterialFactor:
    angle_degrees: Fraction
    maximum_angle_degrees: Fraction
    factor: Fraction

    def __post_init__(self):
        if (any(type(v) is not Fraction for v in
                (self.angle_degrees, self.maximum_angle_degrees, self.factor))
                or not 0 <= self.angle_degrees < 90
                or not 0 < self.maximum_angle_degrees < 90 or not 0 < self.factor <= 1):
            raise ValueError("invalid-empirical-material-factor")


@dataclass(frozen=True, slots=True)
class ModeledThicknessProof:
    accepted: bool
    state: str
    difference_lower_mm2: Fraction
    difference_upper_mm2: Fraction
