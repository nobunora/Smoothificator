"""ADR-0062 typed and domain-separated SHA-256 identity owner."""
from collections.abc import Iterable, Mapping
import hashlib
import hmac

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.plan import IdentityReference, PlanSemanticContent, SubEdgePlan
from adaptive_subedge.domain.settings import PluginSettings
from adaptive_subedge.domain.settings_v2 import PluginSettingsV2
from .serialization import canonical_bytes, identity_root, validate_root, identity_schema_supported

_MAGIC = b"AdaptiveSubEdgeCanonicalV1"
_DOMAIN = {"subedge-plan": "plan", "execution-config": "execution-config",
           "plugin-settings": "plugin-settings", "source-geometry": "source-geometry"}


def domain_digest_chunks(domain_tag: str, chunks: Iterable[bytes]) -> str:
    """One authoritative digest owner; incremental input keeps arrays bounded."""
    if type(domain_tag) is not str or domain_tag not in frozenset((*_DOMAIN.values(), "array")):
        raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "unknown hash domain")
    # The stream must be ordered and contain byte chunks. Empty mappings/sets
    # and scalar byte strings are not canonical streams, even when empty.
    if (not isinstance(chunks, Iterable)
            or isinstance(chunks, (str, bytes, bytearray, Mapping, set, frozenset))):
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "ordered byte-chunk iterable required")
    sha = hashlib.sha256(_MAGIC + b"\0" + domain_tag.encode("ascii") + b"\0")
    for chunk in chunks:
        if type(chunk) is not bytes:
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "canonical hash chunks must be bytes")
        sha.update(chunk)
    return sha.hexdigest()


def domain_digest(domain_tag: str, payload: bytes) -> str:
    if type(payload) is not bytes:
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "canonical payload must be bytes")
    return domain_digest_chunks(domain_tag, (payload,))


def typed_identities_equal(expected_type: str, left: IdentityReference, right: IdentityReference) -> bool:
    """Reject untyped/cross-schema comparisons rather than comparing raw hex."""
    if type(expected_type) is not str or expected_type not in _DOMAIN:
        raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "unknown identity comparison class")
    for ref in (left, right):
        if (type(ref) is not IdentityReference or ref.identity_type != expected_type
                or not identity_schema_supported(expected_type, ref.schema_version) or ref.canonical_encoding_version != "1"):
            raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "mismatched typed identity class/schema")
    if left.schema_version != right.schema_version:
        raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "mixed identity schemas")
    return hmac.compare_digest(left.digest_hex, right.digest_hex)


def typed_identity(identity_type: str, semantic_payload: object) -> IdentityReference:
    if type(identity_type) is not str or identity_type not in _DOMAIN:
        raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "unrecognized identity type")
    schema_version = "2" if type(semantic_payload) is PluginSettingsV2 else "1"
    root = identity_root(identity_type, semantic_payload, schema_version=schema_version)
    validate_root(root, identity_type)
    return IdentityReference(identity_type, schema_version, "1", domain_digest(_DOMAIN[identity_type], canonical_bytes(root)))


def fingerprint_plugin_settings(settings: PluginSettings | PluginSettingsV2) -> IdentityReference:
    if type(settings) not in (PluginSettings, PluginSettingsV2):
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
