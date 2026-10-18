"""Read resolved settings from the exact sliced project, without preset defaults."""
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from io import BytesIO
import json
import re
from zipfile import ZipFile


DECIMAL = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)\Z", re.ASCII)


class SourceProfileError(ValueError):
    """The project/source association or a required setting is unresolved."""


@dataclass(frozen=True)
class SliceSetting:
    name: str
    source_key: str
    value: str

    def number(self) -> Fraction:
        if not DECIMAL.fullmatch(self.value):
            raise SourceProfileError(f"{self.source_key}: finite decimal required")
        return Fraction(self.value)


@dataclass(frozen=True)
class SlicedProfile:
    project_sha256: str
    source_sha256: str
    plate_member: str
    settings: tuple[SliceSetting, ...]
    unconsumed_duplicate_config_keys: tuple[str, ...]

    def setting(self, name: str) -> SliceSetting:
        for setting in self.settings:
            if setting.name == name:
                return setting
        raise SourceProfileError(f"missing resolved setting: {name}")


TEXT_KEYS = ("printer_model", "printer_variant", "printer_settings_id",
             "print_settings_id", "filament_settings_id", "filament_type",
             "gcode_flavor", "machine_start_gcode", "machine_end_gcode",
             "filament_start_gcode", "filament_end_gcode")
POSITIVE_KEYS = ("nozzle_diameter", "filament_diameter", "filament_flow_ratio",
                 "filament_max_volumetric_speed", "layer_height", "print_flow_ratio",
                 "outer_wall_flow_ratio", "outer_wall_speed", "travel_speed",
                 "printable_height")
NONNEGATIVE_KEYS = ("travel_speed_z", "use_firmware_retraction", "enable_arc_fitting",
                    "set_other_flow_ratios", "extruder_printable_height")
OVERRIDES = ("retraction_length", "retraction_speed", "deretraction_speed",
             "retract_restart_extra", "z_hop")
COMPARED_KEYS = ("printer_model", "gcode_flavor", "nozzle_diameter",
                 "filament_diameter", "filament_flow_ratio", "layer_height",
                 "print_flow_ratio", "outer_wall_flow_ratio", "outer_wall_speed",
                 "filament_max_volumetric_speed", "use_firmware_retraction",
                 "enable_arc_fitting", "set_other_flow_ratios", "travel_speed",
                 "travel_speed_z", "printable_height", "extruder_printable_height")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise SourceProfileError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _scalar(settings, key):
    if key not in settings:
        raise SourceProfileError(f"missing setting: {key}")
    value = settings[key]
    if isinstance(value, list):
        if len(value) != 1:
            raise SourceProfileError(f"{key}: single tool/material required")
        value = value[0]
    if type(value) is not str:
        raise SourceProfileError(f"{key}: serialized string required")
    return value


def _configuration(source: bytes):
    try:
        lines = source.decode("ascii").splitlines()
    except UnicodeDecodeError as exc:
        raise SourceProfileError("ASCII source G-code required") from exc
    result = {}
    active = False
    starts = ends = 0
    for line in lines:
        if line == "; CONFIG_BLOCK_START":
            starts += 1
            active = True
        elif line == "; CONFIG_BLOCK_END":
            ends += 1
            active = False
        elif active:
            match = re.fullmatch(r"; ([a-z0-9_]+) = (.*)", line)
            if match:
                key, value = match.groups()
                result.setdefault(key, []).append(value)
    if starts != 1 or ends != 1 or active:
        raise SourceProfileError("one complete G-code CONFIG_BLOCK required")
    return result


def read_sliced_profile(project: bytes, source: bytes, *, plate: int = 1,
                        include_motion_caps: bool = False) -> SlicedProfile:
    """No filesystem access and no fallback to installed/user-modified presets."""
    if type(plate) is not int or plate <= 0:
        raise SourceProfileError("positive plate index required")
    if type(include_motion_caps) is not bool:
        raise SourceProfileError("exact motion-cap selection bool required")
    member = f"Metadata/plate_{plate}.gcode"
    with ZipFile(BytesIO(project)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise SourceProfileError("duplicate ZIP members")
        if member not in names or "Metadata/project_settings.config" not in names:
            raise SourceProfileError("sliced plate and resolved project settings required")
        if archive.read(member) != source:
            raise SourceProfileError("embedded and separate source G-code differ")
        settings = json.loads(archive.read("Metadata/project_settings.config"),
                              object_pairs_hook=_unique_object)
    if type(settings) is not dict:
        raise SourceProfileError("project settings object required")
    resolved = []
    for key in TEXT_KEYS + POSITIVE_KEYS + NONNEGATIVE_KEYS:
        item = SliceSetting(key, key, _scalar(settings, key))
        if key in POSITIVE_KEYS and item.number() <= 0:
            raise SourceProfileError(f"{key}: positive value required")
        if key in NONNEGATIVE_KEYS and item.number() < 0:
            raise SourceProfileError(f"{key}: nonnegative value required")
        if key in TEXT_KEYS and not item.value and "gcode" not in key:
            raise SourceProfileError(f"{key}: nonempty identity required")
        if key in ("use_firmware_retraction", "enable_arc_fitting", "set_other_flow_ratios") and item.number() not in (0, 1):
            raise SourceProfileError(f"{key}: 0 or 1 required")
        resolved.append(item)
    for key in OVERRIDES:
        override = f"filament_{key}"
        # Missing override is unresolved, distinct from an explicit inheritance sentinel.
        source_key = key if _scalar(settings, override) == "nil" else override
        item = SliceSetting(key, source_key, _scalar(settings, source_key))
        value = item.number()
        if value < 0 or (key.endswith("speed") and value <= 0):
            raise SourceProfileError(f"{source_key}: invalid retraction setting")
        resolved.append(item)
    config = _configuration(source)
    vector_keys = tuple(f"machine_max_speed_{axis}" for axis in "xyz") if include_motion_caps else ()
    for key in vector_keys:
        values = settings.get(key)
        if type(values) is not list or not values:
            raise SourceProfileError(f"{key}: nonempty speed-cap vector required")
        if any(type(v) is not str or not DECIMAL.fullmatch(v) or Fraction(v) <= 0 for v in values):
            raise SourceProfileError(f"{key}: positive decimal speed caps required")
        occurrences = config.get(key)
        if occurrences is None or len(occurrences) != 1:
            raise SourceProfileError(f"{key}: exactly one G-code speed-cap vector required")
        exported = tuple(part.strip() for part in occurrences[0].split(','))
        if (any(not DECIMAL.fullmatch(v) for v in exported)
                or tuple(map(Fraction, exported)) != tuple(map(Fraction, values))):
            raise SourceProfileError(f"3MF/G-code speed-cap vector mismatch: {key}")
        selected = min(values, key=Fraction)
        resolved.append(SliceSetting(f"conservative_{key}", key, selected))
    by_name = {s.name: s for s in resolved}
    consumed = COMPARED_KEYS + tuple(s.source_key for s in resolved if s.name in OVERRIDES)
    for key in consumed:
        expected = _scalar(settings, key)
        occurrences = config.get(key)
        if occurrences is None:
            raise SourceProfileError(f"missing G-code setting: {key}")
        if len(occurrences) != 1:
            raise SourceProfileError(f"duplicate consumed G-code setting: {key}")
        actual = occurrences[0]
        equivalent = (DECIMAL.fullmatch(expected) and DECIMAL.fullmatch(actual)
                      and Fraction(expected) == Fraction(actual))
        if actual != expected and not equivalent:
            raise SourceProfileError(f"3MF/G-code setting mismatch: {key}")
    height = by_name["extruder_printable_height"]
    if height.number() == 0:
        height = by_name["printable_height"]
    resolved.append(SliceSetting("effective_printable_height", height.source_key, height.value))
    duplicates = tuple(sorted(key for key, values in config.items()
                              if len(values) > 1 and key not in consumed + vector_keys))
    return SlicedProfile(sha256(project).hexdigest(), sha256(source).hexdigest(),
                         member, tuple(resolved), duplicates)
