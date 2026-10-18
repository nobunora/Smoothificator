"""Closed, fingerprinted geometric taper document; never an empirical E policy."""
from dataclasses import fields
from hashlib import sha256
import json
from adaptive_subedge.domain.smooth_dimensions import SmoothDimensionPolicy
from adaptive_subedge.engine.smooth_dimensions import resolve_policy, resolve_user_policy, validate_resolved_policy
from adaptive_subedge.application.empirical_material_settings import decimal_text, _number

SCHEMA_V1='smoothificator-geometric-dimension-taper-v1'
SCHEMA='smoothificator-geometric-dimension-taper-v2'
SCHEMA_V3='smoothificator-geometric-dimension-taper-v3'
SCHEMA_V4='smoothificator-geometric-dimension-taper-v4'
SCHEMA_V5='smoothificator-geometric-dimension-taper-v5'
NAMES=tuple(f.name for f in fields(SmoothDimensionPolicy))
MAX_POLICY_BYTES=4096
BASE_NAMES=('admission_layer_height_mm','admission_minimum_width_mm','maximum_angle_degrees','plateau_end_degrees','minimum_height_mm','minimum_width_mm','dimension_grid_mm','maximum_width_ticks')
VERSION_NAMES={1:BASE_NAMES,2:BASE_NAMES+('maximum_extra_width_ticks',),3:BASE_NAMES+('maximum_extra_width_ticks','research_endpoint_envelope'),4:BASE_NAMES+('maximum_extra_width_ticks','retention_expression'),5:BASE_NAMES+('maximum_extra_width_ticks','retention_expression','reference_minimum_width_mm','width_tail_start_degrees','width_tail_expression')}
VERSION_SCHEMAS={1:SCHEMA_V1,2:SCHEMA,3:SCHEMA_V3,4:SCHEMA_V4,5:SCHEMA_V5}


def policy_document(policy):
    validate_resolved_policy(policy)
    return {'schema':VERSION_SCHEMAS[policy.schema_version],'mode':'geometry-only-no-empirical-factor','settings':{
        name:getattr(policy,name) if name in ('maximum_width_ticks','maximum_extra_width_ticks','research_endpoint_envelope','retention_expression','width_tail_expression') else decimal_text(getattr(policy,name)) for name in VERSION_NAMES[policy.schema_version]}}



def encode_policy(policy):
    return (json.dumps(policy_document(policy),sort_keys=True,separators=(',',':'))+'\n').encode('ascii')


def policy_identity(policy):
    return sha256(encode_policy(policy)).hexdigest()


def decode_policy(content):
    if type(content) is not bytes or len(content)>MAX_POLICY_BYTES:raise ValueError('invalid-dimension-policy-bytes')
    def unique(pairs):
        root={}
        for k,v in pairs:
            if k in root:raise ValueError('duplicate-dimension-policy-key')
            root[k]=v
        return root
    try:root=json.loads(content.decode('ascii'),object_pairs_hook=unique)
    except (UnicodeError,json.JSONDecodeError,RecursionError) as e:raise ValueError('invalid-dimension-policy-json') from e
    if type(root) is not dict or set(root)!={'schema','mode','settings'} or type(root['schema']) is not str or root['schema'] not in VERSION_SCHEMAS.values() or root['mode']!='geometry-only-no-empirical-factor' or type(root['settings']) is not dict:
        raise ValueError('invalid-dimension-policy-schema')
    version=next(v for v,schema in VERSION_SCHEMAS.items() if schema==root['schema'])
    if set(root['settings'])!=set(VERSION_NAMES[version]):raise ValueError('invalid-dimension-policy-schema')
    settings={name:v if name in ('maximum_width_ticks','maximum_extra_width_ticks','research_endpoint_envelope','retention_expression','width_tail_expression') else _number(v) for name,v in root['settings'].items()}
    settings.update(schema_version=version)
    if version==1:settings.update(maximum_extra_width_ticks=0)
    return validate_resolved_policy(SmoothDimensionPolicy(**settings))



def policy_from_message(message):
    names=(set(BASE_NAMES)-{'maximum_angle_degrees','maximum_width_ticks'})|{'retention_expression','reference_minimum_width_mm','width_tail_start_degrees','width_tail_expression'}
    if type(message) is not dict or set(message)!=names|{'command'} or message['command']!='save_dimension_policy':raise ValueError('invalid-dimension-policy-request')
    if any(type(message[name]) is not str for name in ('retention_expression','width_tail_expression')):raise ValueError('invalid-retention-expression')
    return resolve_user_policy(**{name:message[name] if name in ('retention_expression','width_tail_expression') else _number(message[name]) for name in names})
