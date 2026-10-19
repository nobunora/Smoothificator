"""Explicit source-header guard scope; values/macros never enter UI status."""
from hashlib import sha256

OPTIONAL_ABSENT_KEYS=('filament_retraction_length','filament_retraction_speed','filament_deretraction_speed','filament_retract_restart_extra','filament_z_hop')
REQUIRED_PROFILE_KEYS=tuple(sorted(set('''filament_settings_id filament_type filament_start_gcode filament_end_gcode filament_diameter filament_flow_ratio filament_max_volumetric_speed nozzle_diameter outer_wall_speed travel_speed travel_speed_z extruder_printable_height retraction_length retraction_speed deretraction_speed retract_restart_extra z_hop outer_wall_acceleration outer_wall_jerk printer_model printer_variant printer_settings_id print_settings_id gcode_flavor machine_start_gcode machine_end_gcode layer_height print_flow_ratio outer_wall_flow_ratio printable_height use_firmware_retraction enable_arc_fitting set_other_flow_ratios machine_max_speed_x machine_max_speed_y machine_max_speed_z machine_max_jerk_x machine_max_jerk_y printable_area bed_exclude_area extruder_offset z_offset curr_bed_type initial_layer_print_height nozzle_temperature nozzle_temperature_initial_layer textured_cool_plate_temp textured_cool_plate_temp_initial_layer fan_min_speed fan_max_speed close_fan_the_first_x_layers full_fan_speed_layer additional_cooling_fan_speed enable_pressure_advance pressure_advance adaptive_pressure_advance print_sequence top_shell_layers top_shell_thickness top_solid_infill_flow_ratio'''.split())))


def current_profile_hashes(bundle):
    """Call only on the host UI thread; copy strings, retain hashes only."""
    available=bundle.full_config_keys()
    if not isinstance(available,(list,tuple)) or len(available)>10000 or any(type(k) is not str for k in available):
        raise ValueError('invalid-current-profile-key-list')
    available=set(available);hashes={}
    for key in REQUIRED_PROFILE_KEYS:
        if key not in available:continue
        serialized=bundle.full_config_value(key)
        if type(serialized) is not str or len(serialized.encode('utf8'))>262144:
            continue
        hashes[key]=sha256(serialized.encode('utf8')).hexdigest()
    return hashes


def compare_profile(expected,current):
    return tuple(key for key in REQUIRED_PROFILE_KEYS if current.get(key)!=expected.get(key))
