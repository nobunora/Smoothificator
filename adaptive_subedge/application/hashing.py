"""ADR-0062 typed and domain-separated SHA-256 identity owner."""
from collections.abc import Mapping
import hashlib

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.plan import IdentityReference, PlanSemanticContent, SubEdgePlan
from adaptive_subedge.domain.settings import PluginSettings
from .serialization import canonical_bytes, identity_root, validate_root

_MAGIC = b"AdaptiveSubEdgeCanonicalV1"
_DOMAIN = {"subedge-plan": "plan", "execution-config": "execution-config",
           "plugin-settings": "plugin-settings", "source-geometry": "source-geometry"}


def domain_digest(domain_tag: str, payload: bytes) -> str:
    if domain_tag not in frozenset((*_DOMAIN.values(), "array")) or type(payload) is not bytes:
        raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "unknown hash domain")
    return hashlib.sha256(_MAGIC + b"\0" + domain_tag.encode("ascii") + b"\0" + payload).hexdigest()


def typed_identity(identity_type: str, semantic_payload: object) -> IdentityReference:
    if identity_type not in _DOMAIN:
        raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "unrecognized identity type")
    root = identity_root(identity_type, semantic_payload)
    validate_root(root, identity_type)
    return IdentityReference(identity_type, "1", "1", domain_digest(_DOMAIN[identity_type], canonical_bytes(root)))


def fingerprint_plugin_settings(settings: PluginSettings) -> IdentityReference:
    if type(settings) is not PluginSettings:
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "validated settings required")
    return typed_identity("plugin-settings", settings)


def fingerprint_resolved_execution(semantics: Mapping[str, object]) -> IdentityReference:
    """Accepts only an already-resolved semantic config, not raw Orca override data."""
    if type(semantics) is not dict or not semantics or any(type(k) is not str or not k for k in semantics):
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "resolved semantic map required")
    return typed_identity("execution-config", semantics)


def create_plan(content: PlanSemanticContent) -> SubEdgePlan:
    if type(content) is not PlanSemanticContent:
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "plan content must be immutable")
    references = (content.source_geometry, content.execution_config, content.plugin_settings)
    if tuple(x.identity_type for x in references) != ("source-geometry", "execution-config", "plugin-settings") or any(x.schema_version != "1" or x.canonical_encoding_version != "1" for x in references):
        raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "incompatible plan reference")
    digest = typed_identity("subedge-plan", content).digest_hex
    return SubEdgePlan(content, digest, digest)


def verify_plan(plan: SubEdgePlan) -> None:
    if type(plan) is not SubEdgePlan or create_plan(plan.content).plan_hash != plan.plan_hash:
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "plan hash disagrees with its content")
