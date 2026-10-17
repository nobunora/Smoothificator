# Top-surface multi-line Orca Preview probe

Disposition: bounded native visual display PASS; printable geometry and
G-code safety remain unverified. This record supersedes the underside
single-line candidate in the earlier layered viewer *for future research*.

The fixed-hash offline generic Marlin slice of `offline-coupon.3mf` remained
SHA-256 `499ecc78586fea15694eea16a33bfebea761522aa0bf5eee9069e67c0ae1dd9e`.
The ignored research builder `artifacts/build_orca_layered_overlay_probe.py`
reconstructed the same 669 baseline extrusions on 15 layers. It selected only
the 18 `Top surface` source segments at each of Z=2.2 and 2.4 mm; no underside
segment was used to generate a candidate. Direct segment-by-segment midpoint
pairing collapsed to one horizontal line, so the builder interpolated the
coupon's top-surface centerline envelope at true Z=2.3 mm and covered its
2.674-mm Y span with seven parallel paths. Their display width is 0.4 mm and
centerline pitch is 0.379 mm. These values bound a visual rectangular fill,
not a certified footprint of the actual model.

The new display-only viewer file is
`artifacts/layered-viewer/smoothificator-0f17b22cd4744c848b2e427bae9bf4bc.VIEW_ONLY.gcode`,
SHA-256 `ad6344db331bf324098d4f52a1a99e240d0a57637383d126f6a29fc666d05025`.
Its adjacent JSON records the source digest, 18+18 source top-surface line
numbers, each of the seven display centerlines, the true Z=2.3 mm and the
projected viewer Z=2.4 mm, with support and printable flags false. A bounded
check confirmed 15 viewer layers, 669 original segments, seven `Custom` tags
only on the Z=2.4 mm layer, positive pitch no greater than width, and an
unchanged source digest.

The dedicated Orca viewer opened this representation in standard Preview.
At layer 12 / Z=2.4 mm, the red original top-surface hatch and seven green
Custom lines appear together. A targeted Python Pillow/pywin32 window capture
is at `artifacts/layered-viewer/orca-top-multiline-final.png` (2560x1400,
SHA-256 `d20c6fc7302bfe9a1ae28b26666c292795ccbb881a1b2e668c883a4a2025d5974`).
The layer slider and disabled slice/export controls are visible. The original
G-code was not modified; no printer connection or output operation occurred.

This is not a shape-preservation result. The top-surface envelope can include
points outside the mesh, and viewer projection puts true Z=2.3-mm candidates
on the existing Z=2.4-mm layer. Minimum/maximum bead-width policy, structural
support, collisions and exact affected-surface error are not proven. The
positive-E VIEW_ONLY file must not be printed. Production integration awaits
the top-only, multi-path specification and its geometry/output gates.
