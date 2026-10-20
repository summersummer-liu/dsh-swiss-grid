# Changelog — swiss-grid-design

## 1.1 — 2026-10-20

Fixes after an independent agent usability test (14 findings). The four that could
produce a wrong layout are marked ★.

- ★ `content()` baseline snaps: `en_sub` 2.05→2.0 ×base; plate caption moved inside the
  hero on the last baseline of row 5; tickets 5.85→6.0; footer display 2.40→2.0 and
  4.05→4.0. Every text baseline is now an integer multiple of the baseline grid.
- ★ Title guidance fixed: move the title baseline by whole lines (e.g. `+4.0*base`, not
  `4.2*base`); adaptive title sizing (from character count) documented.
- ★ `--page` without `--margins` now derives proportional margins from the preset instead
  of silently reusing old margins; custom formats produce `poster_custom_<W>x<H>` names.
- ★ `--preview` now implies `--pdf` (no more silent no-op); PDF print failure exits non-zero.
- PDF post-processing sets **TrimBox / BleedBox** and document metadata via PyMuPDF.
- Verifier checks TrimBox, BleedBox, Type0/Type3 usage (visible Type3 = FAIL), page size,
  text layer, crop marks, metadata title.
- CJK font stack now puts a TrueType/glyf face first (Microsoft YaHei, SimHei). CFF/OTF and
  variable CJK fonts (Noto Sans SC VF, Source Han Sans) are emitted as Type3 by Chromium and
  are documented as unsupported for print embedding.
- `spec.md` now includes colours (RGB→CMYK approximation), fonts, print notes, replaceable
  items, exact reproduction command, and relative file names.
- `Grid(..., strict_layout=True)` rejects non-4×8 structures with a clear error instead of
  failing later in `content()`; `grid_calculator.py` stays generic.
- Hero grid rules raised from 0.072 mm to 0.088 mm (0.25 pt minimum).
- Section labels no longer carry duplicate numbering; ideographic spaces removed so no
  blank Type3 glyphs remain in the PDF.
- Docs: margin ratio scoped to bound books (single-sheet posters may use symmetric sides),
  accent usage wording, per-column body measure, QA checklist and common failures updated.

## 1.0 — 2026-10-20

Initial skill: method distillation, parameter tables, SVG→PDF pipeline, poster builder,
grid calculator, PDF verifier, grid-overlay proof, example poster.
