"""Hostile archive fixtures and atomic-publication boundary checks."""
from dataclasses import replace
from hashlib import md5, sha256
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZipInfo
from tools import package_gui_native_trial as package


OLD_SOURCE_SHA = '41075290eab177ffbb011e438bbc8e2a6e6efb643566813bc6d0a54e3baa2630'
OLD_ARCHIVE_SHA = '17565bf3c6c7b2c27db3e9ed8e5efc17ac537c693eeaf6ea61a7c8619364b5ce'
OLD_POLICY = package.NativePackagePolicy(OLD_SOURCE_SHA, OLD_ARCHIVE_SHA)

def archive(source=b'G1 X1\n', extras=()):
    output = BytesIO()
    with ZipFile(output, 'w') as zipped:
        zipped.comment = b'keep archive comment'
        for name, content in ((package.GCODE_MEMBER, source), (package.MD5_MEMBER, md5(source).hexdigest().upper().encode()),
                              ('Metadata/plate_1.json', json.dumps({'bbox_all': [0, 0, 20, 20]}).encode()), *extras):
            info = ZipInfo(name, (2026, 10, 18, 10, 20, 30))
            info.comment = b'keep member comment'
            zipped.writestr(info, content)
    return output.getvalue()


def read(content, source=b'G1 X1\n', policy=OLD_POLICY, cancelled=lambda: False):
    return package._read_archive(content, source, policy, cancelled)


class NativePackageTests(unittest.TestCase):
    def test_readback_source_md5_comments(self):
        infos, comment, members = read(archive())
        self.assertEqual(comment, b'keep archive comment')
        self.assertTrue(all(i.comment == b'keep member comment' for i in infos))
        self.assertEqual(members[0], b'G1 X1\n')
        with self.assertRaisesRegex(ValueError, 'stale-source'):
            read(archive(), b'changed')

    def test_duplicate_alias_unsafe_and_unknown_integrity(self):
        for name in ('Metadata/PLATE_1.GCODE', '../escape', '/absolute', 'Metadata:alias', 'Metadata/unknown.sha256', 'Metadata/checksum.txt'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                read(archive(extras=((name, b'hostile'),)))

    def test_every_archive_budget(self):
        for policy in (package.NativePackagePolicy(OLD_SOURCE_SHA, OLD_ARCHIVE_SHA, max_archive_bytes=1), package.NativePackagePolicy(OLD_SOURCE_SHA, OLD_ARCHIVE_SHA, max_members=1),
                       package.NativePackagePolicy(OLD_SOURCE_SHA, OLD_ARCHIVE_SHA, max_member_bytes=1), package.NativePackagePolicy(OLD_SOURCE_SHA, OLD_ARCHIVE_SHA, max_uncompressed_bytes=1)):
            with self.subTest(policy=policy), self.assertRaises(ValueError):
                read(archive(), policy=policy)

    def test_cancel_and_exact_boolean(self):
        with self.assertRaisesRegex(ValueError, 'cancelled'):
            read(archive(), cancelled=lambda: True)
        for status in (1, None, 'false'):
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, 'invalid-cancellation'):
                read(archive(), cancelled=lambda: status)

    def test_containment_all_bounds_and_finite_numbers(self):
        infos, _, members = read(archive())
        package._containment(infos, members, (((0, 0, 0), (20, 20, 5)),))
        for bounds in ((), (((0, 0, 0), (21, 20, 5)),), (((0, 0, 0), (float('nan'), 20, 5)),)):
            with self.subTest(bounds=bounds), self.assertRaises(ValueError):
                package._containment(infos, members, bounds)

    def test_atomic_publish_nooverwrite_stale_alias(self):
        content = b'new archive'
        trial = package.NativeTrialPackage(content, sha256(content).hexdigest(), 'archive', 'source', 'copy',
                                            (package.GCODE_MEMBER, package.MD5_MEMBER), ())
        inputs = dict(gui_archive=b'', source_gcode=b'', trial_copy=None, copy_recipe=None, policy=OLD_POLICY)
        with tempfile.TemporaryDirectory() as folder, patch.object(package, 'build_native_trial_package', return_value=trial) as rebuild:
            destination = Path(folder) / 'trial.gcode.3mf'
            package.write_native_trial_package(destination, trial, **inputs)
            self.assertEqual(destination.read_bytes(), content)
            with self.assertRaisesRegex(ValueError, 'exists-or-alias'):
                package.write_native_trial_package(destination, trial, **inputs)
            missing = Path(folder) / 'missing'
            rebuild.return_value = replace(trial, copy_sha256='stale')
            with self.assertRaisesRegex(ValueError, 'stale-package'):
                package.write_native_trial_package(missing, trial, **inputs)
            self.assertFalse(missing.exists())
            with self.assertRaisesRegex(ValueError, 'exists-or-alias'):
                package.write_native_trial_package(missing, trial, protected_paths=(missing,), **inputs)
            self.assertFalse(list(Path(folder).glob('.native-trial-*')))

    def test_public_package_fresh_owner_rebuild_closed_changes_and_forgery(self):
        from tests.unit.test_gui_native_trial_copy import recipe_fixture
        from tools.gui_native_trial_copy import rebuild_native_trial_copy
        recipe = recipe_fixture()
        project = recipe.project_bytes
        trial = rebuild_native_trial_copy(recipe, cancelled=lambda: False)
        policy = package.NativePackagePolicy(sha256(recipe.source_bytes).hexdigest(), sha256(project).hexdigest())
        packaged = package.build_native_trial_package(project, recipe.source_bytes, trial, copy_recipe=recipe, policy=policy)
        self.assertEqual(set(packaged.changed_members), {package.GCODE_MEMBER, package.MD5_MEMBER})
        self.assertFalse(packaged.physical_authority)
        with ZipFile(BytesIO(packaged.archive_bytes)) as after:
            self.assertEqual(after.read(package.GCODE_MEMBER), trial.output_bytes)
            self.assertEqual(after.read(package.MD5_MEMBER), md5(trial.output_bytes).hexdigest().upper().encode())
        forged = replace(trial, output_bytes=b'arbitrary', output_sha256=sha256(b'arbitrary').hexdigest())
        with self.assertRaisesRegex(ValueError, 'stale-copy'):
            package.build_native_trial_package(project, recipe.source_bytes, forged, copy_recipe=recipe, policy=policy)

    def test_local_central_header_disagreement_and_corrupt_crc(self):
        raw = bytearray(archive())
        raw[6] ^= 8
        with self.assertRaisesRegex(ValueError, 'local-central-disagreement'):
            read(bytes(raw))
        raw = bytearray(archive())
        with ZipFile(BytesIO(raw)) as zipped:
            info = zipped.infolist()[0]
            offset = info.header_offset + 30 + len(info.filename.encode()) + len(info.extra)
        raw[offset] ^= 1
        from zipfile import BadZipFile
        with self.assertRaises(BadZipFile):
            read(bytes(raw))

    def test_equal_mutable_receipt_rejected_before_temporary_file(self):
        content = b'PK immutable archive'
        fresh = package.NativeTrialPackage(content, sha256(content).hexdigest(), 'archive', 'source', 'copy', (), ())
        forged = replace(fresh, archive_bytes=bytearray(content))
        with tempfile.TemporaryDirectory() as folder, patch.object(package, 'build_native_trial_package', return_value=fresh), patch.object(package.tempfile, 'mkstemp') as allocate:
            with self.assertRaisesRegex(ValueError, 'stale-package'):
                package.write_native_trial_package(Path(folder) / 'new.3mf', forged,
                    gui_archive=b'', source_gcode=b'', trial_copy=None, copy_recipe=None, policy=OLD_POLICY)
            allocate.assert_not_called()
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_write_phase_cancel_cleans_temporary_and_prevents_publication(self):
        content = b'immutable archive'
        fresh = package.NativeTrialPackage(content, sha256(content).hexdigest(), 'archive', 'source', 'copy', (), ())
        cancelled = [False]
        actual_fsync = package.os.fsync
        def cancel_during_fsync(fd):
            actual_fsync(fd)
            cancelled[0] = True
        with tempfile.TemporaryDirectory() as folder, patch.object(package, 'build_native_trial_package', return_value=fresh), patch.object(package.os, 'fsync', side_effect=cancel_during_fsync):
            with self.assertRaisesRegex(ValueError, 'cancelled'):
                package.write_native_trial_package(Path(folder) / 'new.3mf', fresh,
                    gui_archive=b'', source_gcode=b'', trial_copy=None, copy_recipe=None, policy=OLD_POLICY,
                    cancelled=lambda: cancelled[0])
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_actual_pinned_archive_recompression_differences_are_enumerated(self):
        root = Path(__file__).resolve().parents[2]
        original = (root / 'artifacts/gui-angle0to30-trial-v1/plain-gui-export.gcode.3mf').read_bytes()
        source = (root / 'artifacts/gui-angle0to30-trial-v1/plain-gui-original.gcode').read_bytes()
        self.assertEqual(sha256(original).hexdigest(), OLD_ARCHIVE_SHA)
        self.assertEqual(sha256(source).hexdigest(), OLD_SOURCE_SHA)
        supplemented = source + b'; archive serialization regression only\n'
        rebuilt, changed, flags, sizes = package._repack_archive(original, source, supplemented,
            (((75,80,0),(105,100,5)),), OLD_POLICY, lambda: False)
        self.assertEqual(set(changed), {package.GCODE_MEMBER, package.MD5_MEMBER})
        with ZipFile(BytesIO(original)) as before, ZipFile(BytesIO(rebuilt)) as after:
            expected_sizes = tuple((i.filename,i.compress_size,after.getinfo(i.filename).compress_size)
                for i in before.infolist() if i.compress_size != after.getinfo(i.filename).compress_size)
            self.assertEqual(sizes, expected_sizes)
            for info in before.infolist():
                if info.filename not in changed:
                    self.assertEqual(before.read(info), after.read(info.filename))
                    self.assertEqual((info.CRC,info.file_size,info.compress_type),
                        (after.getinfo(info.filename).CRC,after.getinfo(info.filename).file_size,after.getinfo(info.filename).compress_type))
        differences = {name:(old,new) for name,old,new in sizes if name not in changed}
        self.assertEqual(differences, {'[Content_Types].xml': (242,241),
            'Metadata/project_settings.config': (11919,11932),
            'Metadata/slice_info.config': (658,659), 'Metadata/filament_sequence.json': (68,63)})

    def test_policy_requires_explicit_lowercase_immutable_identities(self):
        from dataclasses import FrozenInstanceError
        with self.assertRaises(TypeError):
            package.NativePackagePolicy()
        for digest in ('', 'a'*63, 'A'*64, 'g'*64, b'a'*64):
            with self.subTest(digest=digest), self.assertRaises(ValueError):
                package.NativePackagePolicy(digest, OLD_ARCHIVE_SHA)
        with self.assertRaises(FrozenInstanceError):
            OLD_POLICY.expected_source_sha256 = 'a'*64

    def test_current_and_legacy_explicit_policies_reject_cross_pins(self):
        root = Path(__file__).resolve().parents[2] / 'artifacts'
        old_archive = (root / 'gui-angle0to30-trial-v1/plain-gui-export.gcode.3mf').read_bytes()
        old_source = (root / 'gui-angle0to30-trial-v1/plain-gui-original.gcode').read_bytes()
        current_archive = (root / 'gui-angle0to30-trial-v2/current-gui-export.gcode.3mf').read_bytes()
        current_source = (root / 'gui-angle0to30-trial-v2/current-gui-original.gcode').read_bytes()
        current_policy = package.NativePackagePolicy(
            'a6314651032bc7faa8ceda39440a4f5e20ccf5b0bfd615bde3e0e83313bc2f59',
            '1d7143385b8be0d1fce4d68b8566cd493283d27f34a8db9586af1e1d9df6ca6e')
        self.assertEqual(sha256(current_archive).hexdigest(), current_policy.expected_gui_archive_sha256)
        self.assertEqual(sha256(current_source).hexdigest(), current_policy.expected_source_sha256)
        package._read_archive(current_archive, current_source, current_policy, lambda:False)
        for policy, gui, source in ((OLD_POLICY,current_archive,current_source),
                (current_policy,old_archive,old_source), (current_policy,current_archive,old_source),
                (current_policy,old_archive,current_source)):
            with self.subTest(policy=policy), self.assertRaisesRegex(ValueError, 'input-pin'):
                package.build_native_trial_package(gui,source,None,copy_recipe=None,policy=policy)
