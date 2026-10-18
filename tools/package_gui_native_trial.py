"""Bounded, source-pinned packaging for the experimental GUI native trial only."""
from __future__ import annotations

from copy import copy
from dataclasses import dataclass
from hashlib import md5, sha256
from io import BytesIO
import json
import math
import os
from pathlib import Path
import re
import struct
import tempfile
from zipfile import ZipFile, BadZipFile, ZIP_STORED, ZIP_DEFLATED

GCODE_MEMBER = 'Metadata/plate_1.gcode'
MD5_MEMBER = GCODE_MEMBER + '.md5'


@dataclass(frozen=True)
class NativePackagePolicy:
    expected_source_sha256: str
    expected_gui_archive_sha256: str
    max_archive_bytes: int = 16_000_000
    max_members: int = 128
    max_member_bytes: int = 8_000_000
    max_uncompressed_bytes: int = 32_000_000


    def __post_init__(self):
        for digest in (self.expected_source_sha256, self.expected_gui_archive_sha256):
            if type(digest) is not str or re.fullmatch(r'[0-9a-f]{64}', digest) is None:
                raise ValueError('native-package-explicit-lowercase-sha256-required')
        if any(type(getattr(self, key)) is not int or getattr(self, key) <= 0 for key in
               ('max_archive_bytes', 'max_members', 'max_member_bytes', 'max_uncompressed_bytes')):
            raise ValueError('native-package-invalid-policy')


@dataclass(frozen=True)
class NativeTrialPackage:
    archive_bytes: bytes
    archive_sha256: str
    source_archive_sha256: str
    source_sha256: str
    copy_sha256: str
    changed_members: tuple[str, ...]
    flag_differences: tuple[tuple[str, int, int], ...]
    compression_size_differences: tuple[tuple[str, int, int], ...] = ()
    cached_metadata_status: str = 'retained-stale-time-filament-thumbnails'
    physical_authority: bool = False
    whole_job_verified: bool = False


def _check_cancel(cancelled):
    status = cancelled()
    if type(status) is not bool:
        raise ValueError('native-package-invalid-cancellation')
    if status:
        raise ValueError('native-package-cancelled')


def _read_archive(content, source, policy, cancelled):
    if type(content) is not bytes or len(content) > policy.max_archive_bytes:
        raise ValueError('native-package-archive-limit')
    with ZipFile(BytesIO(content)) as archive:
        infos = archive.infolist()
        if len(infos) > policy.max_members or sum(i.file_size for i in infos) > policy.max_uncompressed_bytes:
            raise ValueError('native-package-member-limit')
        names = [i.filename for i in infos]
        aliases = [n.replace('\\', '/').casefold() for n in names]
        if len(set(aliases)) != len(names):
            raise ValueError('native-package-duplicate-or-alias')
        members = []
        for info in infos:
            _check_cancel(cancelled)
            name = info.filename
            if (not name.isascii() or '\\' in name or name.startswith('/') or ':' in name
                    or any(p in ('', '.', '..') for p in name.split('/'))):
                raise ValueError('native-package-member-name')
            if info.file_size > policy.max_member_bytes or info.compress_type not in (ZIP_STORED, ZIP_DEFLATED) or info.flag_bits & ~0x808:
                raise ValueError('native-package-unsupported-member')
            if re.search(r'(?:checksum|digest|\.(?:md5|sha\d*))', name, re.I) and name != MD5_MEMBER:
                raise ValueError('native-package-unknown-integrity')
            offset = info.header_offset
            if offset < 0 or offset + 30 > len(content):
                raise ValueError('native-package-local-header')
            header = struct.unpack_from('<4s5H3I2H', content, offset)
            signature, version, flags, method, clock, date, crc, compressed, size, name_size, extra_size = header
            name_end = offset + 30 + name_size
            if (signature != b'PK\x03\x04' or flags != info.flag_bits or method != info.compress_type
                    or version != info.extract_version or name_end + extra_size > len(content)
                    or content[offset + 30:name_end] != name.encode('ascii')):
                raise ValueError('native-package-local-central-disagreement')
            if not flags & 8 and (crc, compressed, size) != (info.CRC, info.compress_size, info.file_size):
                raise ValueError('native-package-local-integrity-disagreement')
            # ZipFile validates local filename, decompressed size and CRC on complete read.
            members.append(archive.read(info))
        contents = dict(zip(names, members))
        if contents.get(GCODE_MEMBER) != source or contents.get(MD5_MEMBER) != md5(source).hexdigest().upper().encode('ascii'):
            raise ValueError('native-package-stale-source-or-md5')
        return infos, archive.comment, tuple(members)


def _unique_json(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('native-package-duplicate-json-key')
        result[key] = value
    return result


def _containment(infos, members, bounds):
    contents = {i.filename: b for i, b in zip(infos, members)}
    metadata = json.loads(contents['Metadata/plate_1.json'], object_pairs_hook=_unique_json)
    bbox = metadata['bbox_all']
    if (type(bbox) is not list or len(bbox) != 4
            or any(type(v) not in (int, float) or not math.isfinite(v) for v in bbox)
            or bbox[0] > bbox[2] or bbox[1] > bbox[3]):
        raise ValueError('native-package-invalid-bbox')
    if not bounds:
        raise ValueError('native-package-missing-motion-bounds')
    for lower, upper in bounds:
        if (len(lower) != 3 or len(upper) != 3 or any(not math.isfinite(v) for v in (*lower, *upper))
                or any(a > b for a, b in zip(lower, upper))
                or lower[0] < bbox[0] or lower[1] < bbox[1] or upper[0] > bbox[2] or upper[1] > bbox[3]):
            raise ValueError('native-package-bbox-containment')


def build_native_trial_package(gui_archive, source_gcode, trial_copy, *, copy_recipe,
                               policy, cancelled=lambda: False):
    """Require a fresh owning-copy rebuild; arbitrary bytes cannot obtain a receipt."""
    from tools.gui_native_trial_copy import NativeTrialCopy, rebuild_native_trial_copy
    if type(policy) is not NativePackagePolicy:
        raise ValueError('native-package-invalid-policy')
    _check_cancel(cancelled)
    if type(gui_archive) is not bytes or type(source_gcode) is not bytes:
        raise ValueError('native-package-immutable-bytes-required')
    if len(gui_archive) > policy.max_archive_bytes or len(source_gcode) > policy.max_member_bytes:
        raise ValueError('native-package-input-byte-limit')
    if sha256(gui_archive).hexdigest() != policy.expected_gui_archive_sha256 or sha256(source_gcode).hexdigest() != policy.expected_source_sha256:
        raise ValueError('native-package-input-pin')
    rebuilt = rebuild_native_trial_copy(copy_recipe, cancelled=cancelled)
    if (type(trial_copy) is not NativeTrialCopy or type(rebuilt) is not NativeTrialCopy
            or type(trial_copy.output_bytes) is not bytes or type(rebuilt.output_bytes) is not bytes
            or rebuilt != trial_copy):
        raise ValueError('native-package-stale-copy')
    if (trial_copy.source_sha256 != policy.expected_source_sha256 or trial_copy.project_sha256 != policy.expected_gui_archive_sha256
            or sha256(trial_copy.output_bytes).hexdigest() != trial_copy.output_sha256
            or trial_copy.output_bytes == source_gcode):
        raise ValueError('native-package-copy-identity')
    archive_bytes, changed, flags, compressed_sizes = _repack_archive(
        gui_archive, source_gcode, rebuilt.output_bytes, (rebuilt.added_motion_bounds_mm,), policy, cancelled)
    return NativeTrialPackage(archive_bytes, sha256(archive_bytes).hexdigest(), policy.expected_gui_archive_sha256,
                              policy.expected_source_sha256, rebuilt.output_sha256, changed, flags, compressed_sizes)


def _repack_archive(gui_archive, source_gcode, supplemented_source, bounds, policy, cancelled):
    infos, comment, members = _read_archive(gui_archive, source_gcode, policy, cancelled)
    _containment(infos, members, bounds)
    output = BytesIO()
    with ZipFile(output, 'w') as archive:
        archive.comment = comment
        for info, original in zip(infos, members):
            _check_cancel(cancelled)
            content = supplemented_source if info.filename == GCODE_MEMBER else original
            if info.filename == MD5_MEMBER:
                content = md5(supplemented_source).hexdigest().upper().encode('ascii')
            cloned = copy(info)
            archive.writestr(cloned, content)
            cloned.external_attr = info.external_attr
    archive_bytes = output.getvalue()
    after, after_comment, after_members = _read_archive(archive_bytes, supplemented_source, policy, cancelled)
    if after_comment != comment or len(after) != len(infos):
        raise ValueError('native-package-archive-metadata-change')
    changed, flags, compressed_sizes = [], [], []
    fields = ('filename', 'date_time', 'comment', 'extra', 'compress_type', 'internal_attr',
              'external_attr', 'create_system', 'create_version', 'extract_version', 'reserved', 'volume')
    for before, new, old_content, new_content in zip(infos, after, members, after_members):
        if any(getattr(before, field) != getattr(new, field) for field in fields):
            raise ValueError('native-package-zipinfo-change')
        if before.flag_bits != new.flag_bits:
            if new.flag_bits & ~before.flag_bits or (before.flag_bits ^ new.flag_bits) & ~0x808:
                raise ValueError('native-package-flag-change')
            flags.append((before.filename, before.flag_bits, new.flag_bits))
        if before.compress_size != new.compress_size:
            compressed_sizes.append((before.filename, before.compress_size, new.compress_size))
        if old_content != new_content:
            changed.append(before.filename)
        elif (before.CRC, before.file_size) != (new.CRC, new.file_size):
            raise ValueError('native-package-unchanged-integrity-change')
    if set(changed) != {GCODE_MEMBER, MD5_MEMBER}:
        raise ValueError('native-package-changed-member-set')
    return archive_bytes, tuple(changed), tuple(flags), tuple(compressed_sizes)


def write_native_trial_package(destination, package, *, gui_archive, source_gcode,
                               trial_copy, copy_recipe, policy,
                               cancelled=lambda: False, protected_paths=()):
    """Revalidate immediately before atomic no-replace publication; preserve originals."""
    destination = Path(destination)
    resolved = destination.resolve()
    if destination.exists() or any(resolved == Path(p).resolve() for p in protected_paths):
        raise ValueError('native-package-output-exists-or-alias')
    fresh = build_native_trial_package(gui_archive, source_gcode, trial_copy,
        copy_recipe=copy_recipe, policy=policy, cancelled=cancelled)
    if (type(package) is not NativeTrialPackage or type(fresh) is not NativeTrialPackage
            or type(package.archive_bytes) is not bytes or type(fresh.archive_bytes) is not bytes
            or fresh != package or sha256(fresh.archive_bytes).hexdigest() != fresh.archive_sha256):
        raise ValueError('native-package-stale-package')
    fd, temporary = tempfile.mkstemp(prefix='.native-trial-', dir=destination.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(fresh.archive_bytes)
            stream.flush()
            os.fsync(stream.fileno())
        if sha256(Path(temporary).read_bytes()).hexdigest() != fresh.archive_sha256:
            raise ValueError('native-package-write-readback')
        # Hard-link publication is atomic and fails if the destination already exists.
        _check_cancel(cancelled)
        os.link(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)

