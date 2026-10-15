# /// script
# requires-python = ">=3.12"
#
# [tool.orcaslicer.plugin]
# name = "Smoothificator Read-only Probe"
# description = "Diagnostic only: runtime and offline G-code hash observation. No geometry or injection."
# author = "Smoothificator contributors"
# version = "0.1.0"
# ///
"""Disposable probe for official Orca nightly 86905a8a, not the analysis plugin."""

from collections import deque
import hashlib
import importlib.util
import json
import os
import sys
from threading import Lock

import orca

EXPECTED_VERSION = "2.5.0-dev"
EXPECTED_BUILD = "86905a8a"
MAX_BYTES = 64 * 1024 * 1024
_verified_build = False
_observations = deque(maxlen=16)
_observation_lock = Lock()


def _record(reason, **fields):
    observation = {"probe": "0.1.0", "reason": reason, **fields}
    with _observation_lock:
        _observations.append(observation)
    print("SMOOTHIFICATOR_PROBE " + json.dumps(observation, sort_keys=True),
          file=sys.stderr, flush=True)
    return orca.ExecutionResult.skipped(reason)


def _enabled(capability):
    settings = json.loads(capability.get_config())
    if not isinstance(settings, dict) or set(settings) - {"enabled"}:
        raise ValueError("unknown settings")
    enabled = settings.get("enabled", True)
    if type(enabled) is not bool:
        raise ValueError("enabled must be boolean")
    return enabled


def _digest_file(path, cancelled):
    digest = hashlib.sha256()
    count = 0
    with open(path, "rb") as stream:
        before = os.fstat(stream.fileno())
        if before.st_size > MAX_BYTES:
            raise ValueError("size limit")
        while chunk := stream.read(1024 * 1024):
            if cancelled():
                raise InterruptedError("cancelled")
            count += len(chunk)
            if count > MAX_BYTES:
                raise ValueError("size limit")
            digest.update(chunk)
        after = os.fstat(stream.fileno())
    identity = lambda stat: (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)
    if identity(before) != identity(after) or count != before.st_size:
        raise ValueError("changed during read")
    return digest.hexdigest(), count, identity(after)


class ReadOnlyExportProbe(orca.slicing.SlicingPipelineCapabilityBase):
    def get_name(self):
        return "Smoothificator offline export probe"

    def get_default_config(self):
        return {"enabled": True}

    def on_load(self):
        _record("EXPORT_CAPABILITY_LOADED")

    def execute(self, ctx):
        try:
            if not _verified_build or ctx.orca_version != EXPECTED_VERSION:
                return _record("UNSUPPORTED_OR_UNVERIFIED_RUNTIME")
            if not _enabled(self):
                return _record("DISABLED")
            if ctx.cancelled():
                return _record("CANCELLED")
            if ctx.step != orca.slicing.Step.psGCodePostProcess:
                return orca.ExecutionResult.skipped("READ_ONLY_NO_GEOMETRY_ACTION")
            if ctx.host != "File":
                return _record("OFFLINE_FILE_EXPORT_REQUIRED")
            if not ctx.gcode_path:
                return _record("MISSING_GCODE_PATH")
            first = _digest_file(ctx.gcode_path, ctx.cancelled)
            second = _digest_file(ctx.gcode_path, ctx.cancelled)
            if ctx.cancelled():
                return _record("CANCELLED")
            if first != second:
                return _record("SOURCE_CHANGED")
            return _record("READ_ONLY_UNCHANGED", sha256_before=first[0],
                           sha256_after=second[0], bytes=first[1],
                           print_is_none=ctx.print is None,
                           object_is_none=ctx.object is None,
                           config_value_available=callable(ctx.config_value))
        except InterruptedError:
            return _record("CANCELLED")
        except (AttributeError, TypeError, ValueError):
            return _record("INVALID_CONTEXT_OR_SETTINGS")
        except OSError:
            return _record("READ_FAILED")
        except Exception as error:
            # Last-resort callback containment; no exception text/private paths logged.
            return _record("CALLBACK_FAILED", exception_type=type(error).__name__)


class RuntimeDiagnostics(orca.script.ScriptPluginCapabilityBase):
    def get_name(self):
        return "Smoothificator runtime diagnostics"

    def on_load(self):
        _record("SCRIPT_CAPABILITY_LOADED")

    def on_unload(self):
        global _verified_build
        _verified_build = False

    def execute(self):
        global _verified_build
        _verified_build = False
        try:
            app = orca.host.app_info()
            _verified_build = (app.get("version") == EXPECTED_VERSION
                               and app.get("build") == EXPECTED_BUILD)
            with _observation_lock:
                recent = list(_observations)
            report = {"diagnostic_only": True, "runtime_verified": _verified_build,
                      "version": app.get("version"), "build": app.get("build"),
                      "python": sys.version.split()[0],
                      "numpy_available": importlib.util.find_spec("numpy") is not None,
                      "recent_exports": recent}
            text = json.dumps(report, indent=2, sort_keys=True)
            print("SMOOTHIFICATOR_RUNTIME " + json.dumps(report, sort_keys=True),
                  file=sys.stderr, flush=True)
            orca.host.ui.message(text, title="Smoothificator diagnostic only",
                                 buttons="ok", icon="info")
            return orca.ExecutionResult.success("Diagnostic only; no geometry or injection")
        except Exception as error:
            _verified_build = False
            return _record("RUNTIME_DIAGNOSTIC_FAILED", exception_type=type(error).__name__)


@orca.plugin
class ReadOnlyProbePackage(orca.base):
    def register_capabilities(self):
        orca.register_capability(RuntimeDiagnostics)
        orca.register_capability(ReadOnlyExportProbe)
