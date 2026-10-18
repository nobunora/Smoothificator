# GUI native trial package implementation — 2026-10-18

Scope: approved tools-only experimental route in `docs/specs/gui-native-paired-trial-review.md`; repository disposition validated. No canonical runtime, legacy source owner, printer, UI or original artifact was changed.

Changed `tools/package_gui_native_trial.py` and `tests/unit/test_gui_native_trial_package.py`. The new immutable package receipt pins the genuine GUI archive/source, directly rebuilds the owning immutable copy recipe and rejects stale/forged copies. Archive reads enforce byte/member budgets, unique legal ASCII names, integrity-member allowlist, exact uppercase MD5, local/central agreement and CRC. Repacking permits only the two intended changed contents; all listed ZipInfo fields, unchanged CRC/sizes, archive/member comments and extras remain preserved. Only clearing descriptor/UTF8 flags is permitted and every difference is reported. Cached time/filament/thumbnails are explicitly stale. Actual plate metadata claims an XY bounding box only; all freshly rebuilt inserted motion must fit it. Original physical Z/profile bounds remain the copy owner's responsibility.

Publication directly rebuilds the package from owner inputs, revalidates equality, writes/fsyncs/readbacks a temporary sibling and atomically creates a new destination via no-replace hard link. Existing targets and supplied protected-path aliases are rejected. No dependency was added. Caller-supplied arbitrary rebuild callbacks were rejected as a design alternative because they could certify arbitrary bytes.

Checks:
- `python -m py_compile tools/package_gui_native_trial.py tests/unit/test_gui_native_trial_package.py`: exit 0.
- `python -m unittest discover -s tests/unit -p test_gui_native_trial_package.py -v`: exit 0, 8 tests with boundary subtests. Includes genuine copy-owner reconstruction using a synthetic pinned fixture, forged-copy rejection, closed changed members, uppercase new MD5, cancellation exact boolean, budgets, aliases/unknown integrity, header/CRC corruption, bbox and atomic publication/no overwrite/stale readback.
- Read-only `_read_archive` against the actual pinned GUI archive and original G-code: exit 0, 16 members, 300867 uncompressed bytes. Local/central and source/MD5 validation passed.

No actual final WITH package was generated: actual feasible planner recipe is still required. Full regression, independent review, native Orca loading and user physical evaluation are separate remaining gates. All physical/whole-job authority flags remain false. Ready for independent review of this bounded package owner.

## Blind-review reconciliation

GNP-1, GNP-2 and GNP-3 are confirmed and corrected. Caller source/archive/copy-output/package-output must be exact immutable bytes. Publication writes only freshly rebuilt owning-recipe bytes and verifies the fixed fresh digest, rejecting an equal bytearray receipt before allocating a temporary file. A final exact-boolean cancellation checkpoint immediately before atomic publication aborts and cleans the temporary file when cancellation arrives during fsync.

The explicitly amended/revalidated handoff permits stdlib recompression-size serialization differences. `compression_size_differences` now enumerates every member whose compressed size changes, while unchanged uncompressed bytes, CRC, file size, compression method and other semantic ZipInfo metadata remain mandatory. Actual pinned regression reproduces and permits only the observed unchanged-content size differences: Content_Types 242→241, project settings11919→11932, slice info658→659, filament sequence68→63. This private serializer test appends a review-only comment in memory and produces no artifact or copy authorization.

New checks, both exit0:
- `.\.venv\Scripts\python.exe -m py_compile tools/package_gui_native_trial.py tests/unit/test_gui_native_trial_package.py`
- `.\.venv\Scripts\python.exe -m unittest tests.unit.test_gui_native_trial_package -v`:11 tests, including mutable-receipt, write-phase cancellation/cleanup and actual pinned recompression regressions.

Original fixed identity defaults remain unchanged pending explicit new-slice identity review. No GUI/printer/network operation, original write or arbitrary-byte certification was introduced. Ready for follow-up independent verification.

## Explicit current-source policy delta

Implemented the parent-validated final handoff delta (review record SHA prefix44dd5ce8). `NativePackagePolicy(expected_source_sha256, expected_gui_archive_sha256, ...)` now requires two explicit immutable lowercase64hex identities. Build and publication require this policy with no automatic expected-hash inference or old-global-only default. Expected pins, actual source/archive and freshly owning-rebuilt copy source/project identities must agree. Original v1 tests now provide explicit v1 pins. Current v2 archive/source pins are checked read-only; v1/v2 crossed archive/source/policy combinations reject before copy rebuilding. Current profile/selection/geometry semantics remain the direct copy owner's fresh-rebuild responsibility; the genuine archive remains the copied container.

Commands (exit0): `.\.venv\Scripts\python.exe -m py_compile tools/package_gui_native_trial.py tests/unit/test_gui_native_trial_package.py`; `.\.venv\Scripts\python.exe -m unittest tests.unit.test_gui_native_trial_package -v`:13 tests. No GUI/device actions, original writes or final actual current recipe package were performed. All earlier immutable-publication, cancellation and ZIP invariants remain enforced. Ready for parent regression and independent delta review.
