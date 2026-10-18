"""Strict experimental settings JSON and identity; no filesystem or preset mutation."""
from dataclasses import fields
from fractions import Fraction as F
from hashlib import sha256
import json
import re
from adaptive_subedge.domain.empirical_material import EmpiricalMaterialPolicy
from adaptive_subedge.engine.empirical_material import resolve_policy, validate_resolved_policy

SCHEMA_V1 = "smoothificator-empirical-material-v1"
SCHEMA = "smoothificator-empirical-material-v2"
MAX_POLICY_BYTES = 4096
NAMES = tuple(field.name for field in fields(EmpiricalMaterialPolicy))


def decimal_text(number):
    if type(number) is not F or (number * 100000000).denominator != 1:
        raise ValueError("nondecimal-material-setting")
    scaled = number * 100000000
    sign = "-" if scaled < 0 else ""
    whole, part = divmod(abs(scaled.numerator), 100000000)
    return sign + str(whole) + (f".{part:08d}".rstrip("0") if part else "")


def _number(text):
    if type(text) is not str or re.fullmatch(r"(?:0|[1-9][0-9]{0,5})(?:\.[0-9]{1,8})?", text) is None:
        raise ValueError("invalid-material-setting-text")
    return F(text)


def policy_document(policy):
    validate_resolved_policy(policy)
    names = NAMES if policy.minimum_modeled_thickness_mm is not None else NAMES[:-1]
    return {"schema": SCHEMA if policy.minimum_modeled_thickness_mm is not None else SCHEMA_V1, "angle_decimal_places": 8,
            "settings": {name: decimal_text(getattr(policy, name)) for name in names}}


def encode_policy(policy):
    return (json.dumps(policy_document(policy), sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def policy_identity(policy):
    return sha256(encode_policy(policy)).hexdigest()


def decode_policy(content):
    if type(content) is not bytes or len(content) > MAX_POLICY_BYTES:
        raise ValueError("invalid-material-policy-bytes")
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result: raise ValueError("duplicate-material-policy-key")
            result[key] = value
        return result
    try:
        root = json.loads(content.decode("ascii"), object_pairs_hook=unique_pairs)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ValueError("invalid-material-policy-json") from error
    if (type(root) is not dict or set(root) != {"schema", "angle_decimal_places", "settings"}
            or root["schema"] not in (SCHEMA_V1, SCHEMA) or type(root["angle_decimal_places"]) is not int
            or root["angle_decimal_places"] != 8 or type(root["settings"]) is not dict
            or set(root["settings"]) != set(NAMES if root["schema"] == SCHEMA else NAMES[:-1])):
        raise ValueError("invalid-material-policy-schema")
    policy = EmpiricalMaterialPolicy(**{name: _number(root["settings"][name]) for name in root["settings"]})
    return validate_resolved_policy(policy)


def policy_from_message(message):
    names = {"command", "start_percent", "end_percent", "retract_mm", "wipe_mm",
             "admission_layer_height_mm", "admission_minimum_width_mm", "minimum_modeled_thickness_mm"}
    if (type(message) is not dict or set(message) != names or message["command"] != "save_material_policy"
            or any(type(value) is not str for value in message.values())
            or len(json.dumps(message).encode("utf8")) > MAX_POLICY_BYTES):
        raise ValueError("invalid-material-policy-request")
    return resolve_policy(**{name: _number(value) for name, value in message.items() if name != "command"})
