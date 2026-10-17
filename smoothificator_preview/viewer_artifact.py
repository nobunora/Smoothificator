"""Exclusive plugin-owned scene artifacts; never launch or overwrite files."""
from pathlib import Path
from uuid import uuid4
from .native_scene import MAX_BYTES


def write_scene(storage_root, content, cancelled):
    if type(content) is not str or not content.isascii() or len(content) > MAX_BYTES:
        raise ValueError("invalid-viewer-content")
    if not callable(cancelled):
        raise ValueError("invalid-cancellation")
    def check():
        value = cancelled()
        if type(value) is not bool:
            raise ValueError("invalid-cancellation")
        if value:
            raise InterruptedError("cancelled")
    check()
    root = Path(storage_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    target = root / f"smoothificator-{uuid4().hex}.VIEW_ONLY.gcode"
    created = False
    try:
        check()
        with target.open("xb") as stream:
            created = True
            data = content.encode("ascii")
            for offset in range(0, len(data), 65536):
                check()
                stream.write(data[offset:offset+65536])
        check()
        return target
    except BaseException:
        if created:
            target.unlink(missing_ok=True)
        raise
