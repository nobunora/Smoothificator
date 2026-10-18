"""Plugin-owned atomic experimental policy persistence; no native output execution."""
from pathlib import Path
import os
import tempfile
from adaptive_subedge.application.empirical_material_settings import (
    MAX_POLICY_BYTES, encode_policy, decode_policy, policy_identity, policy_document)
from adaptive_subedge.engine.empirical_material import resolve_policy

FILENAME = "supplemental-material-policy.json"


def policy_path(storage_root):
    if type(storage_root) is not str or not storage_root:
        raise ValueError("invalid-material-storage")
    root = Path(storage_root)
    if root.is_symlink():
        raise ValueError("unsafe-material-storage")
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    target = root / FILENAME
    if target.is_symlink() or target.exists() and not target.is_file():
        raise ValueError("unsafe-material-policy-file")
    return target


def load_policy(storage_root):
    target = policy_path(storage_root)
    if not target.exists():
        return resolve_policy(), target
    if target.stat().st_size > MAX_POLICY_BYTES:
        raise ValueError("material-policy-file-limit")
    with target.open("rb") as source:
        content = source.read(MAX_POLICY_BYTES + 1)
    return decode_policy(content), target


def save_policy(storage_root, policy):
    target = policy_path(storage_root)
    content = encode_policy(policy)
    descriptor, temporary = tempfile.mkstemp(prefix=".material-policy-", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)
    restored, _ = load_policy(storage_root)
    if restored != policy:
        raise ValueError("material-policy-readback-mismatch")
    return restored, target


def presentation(policy, target, *, saved):
    return {"settings": policy_document(policy)["settings"], "path": str(target),
            "identity": policy_identity(policy), "saved": saved}
