---
name: swiss-grid-design
description: Swiss grid layout system after Müller-Brockmann — compute 版心, 4-column/8-row unit grids (8/16/20/32-cell families), baseline and type scale, then produce print-ready SVG-to-PDF posters, books, magazines, exhibition graphics and CI systems with a grid-overlay proof. Use for 网格系统, 版式设计, 海报, 画册, 书籍排版, 展览, 企业形象, Swiss style, Swiss grid, 32格, baseline grid, A4/A3/A2/A1, bleed and crop marks.
license: MIT
metadata:
  version: "1.1"
---

# Swiss Grid Design

A method + renderer for layouts built on a Müller-Brockmann grid. Two things ship here: the
rules (why and how) and a parametric builder that turns a page format into a print-ready
SVG → PDF poster, plus the grid-overlay proof that shows it is actually gridded.

## 0. TL;DR

```powershell
# <skill> = the base directory the skill tool reports for this skill
$py = 'python'   # any Python 3.10+; the DSH runtime python works too
# 1. copy the builder into the project (never edit the installed skill copy)
Copy-Item <skill>\assets\poster_builder.py .\poster_builder.py
# 2. edit TEXTS / ART / colours, then:
& $py .\poster_builder.py --preset a2-32 --outdir out --grid --pdf --preview
# 3. verify the PDF and LOOK at the preview / grid overlay
& $py <skill>\assets\verify_print_pdf.py --pdf out\poster_a2-32.pdf --trim 420x594 --bleed 3
```

Deliver: artwork PDF (bleed + crop marks), grid diagram PDF, source SVG/HTML, `spec.md`,
preview JPG. A grid layout is not finished until both PDFs exist and the overlay shows every
element on a line.

## 1. When to use

Use whenever a layout must be **constructed** rather than merely styled:

- posters, book covers and spreads, catalogues, magazines, annual reports;
- exhibition graphics, wall graphics, spatial information systems;
- corporate-identity grid sheets and multi-medium systems;
- a "grid diagram / 网格结构图" requested as a proof or handover document;
- phrases like 网格系统, 版式设计, 版面, 海报, 画册, 书籍排版, 展览, 企业形象, Swiss style,
  32格, baseline grid, 出血, 裁切线.

Do not use for: app/UI screens, slide templates with no print output, single social-media
graphics where the overhead is not justified, or freeform illustration where the user
explicitly wants no grid. (A grid can still be used for expressive, asymmetric work — the
question is whether the output needs a print/spec handover.)

## 2. Non-negotiables

1. **Every element snaps** to a column line, row line or baseline multiple. No nudging text
   off the grid to make it fit — resize the element or adjust the grid.
2. **Cell height = integer body lines**; leading is constant; the baseline is derived from
   the cell (default cell ÷ 6 on posters).
3. **Type scale is multiples of the baseline** (see `references/parameters.md`). Captions
   and headings occupy whole lines; images occupy whole cells.
4. **Margins** start from head 1 : inner 1 : outer 2 : foot 3 for bound books and spreads,
   then optically centred (type area slightly high). Single-sheet posters may use symmetric
   side margins. Add bleed 3 mm (digital) or 5 mm (offset).
5. **One type family** (a second only for a script/logo), hierarchy by size/weight/style.
6. **Few image size classes** (2–3); images crop on cell edges; captions outside the image
   or on a defined tint block.
7. **The grid is not decoration**: no grid meta-text ("32 格网格" etc.) on the artwork. It
   belongs on the separate grid diagram.
8. **Deliver the pair**: artwork + grid diagram. The diagram is the proof and the handover.

## 3. Workflow

### Step 1 — inventory content and format
Count text lines, images and their size classes, captions, tables, credits. Default for a
poster: **A2 420×594 mm, portrait, 3 mm bleed, 32-cell grid** unless the user specifies
otherwise. For books use the trim the user gives (A5/A4); pick 8/12-cell grids.

### Step 2 — compute the grid
Do not eyeball the numbers. Either run the calculator:

```powershell
& $py <skill>\assets\grid_calculator.py --preset a2-32
& $py <skill>\assets\grid_calculator.py --page 420x594 --margins 34,42,34,58 --cols 4 --col-gap 9 --rows 8 --row-gap 11.3
```

or read the preset table in `references/parameters.md` (a4/a3/a2/a1/a0 × 32-cell, plus the
book's 8/20/32-cell A4 numbers). Write the chosen numbers down before drawing — they are the
contract for every later element.

### Step 3 — choose the type scale
From the baseline, pick roles by multiple (title ≈ 1.034 × column width; body ≈ 0.65 ×
baseline; caption ≈ 0.30). The builder ships a complete scale in `SCALE`; adjust only if the
format or content demands it. On posters: body ≥ ~2.5–3.5 mm cap height at 1–2 m; on books
8–12 pt body.

### Step 4 — build
Copy `assets/poster_builder.py` into the project. Edit, in this order:

1. `TEXTS` — all copy lives in this dict (content is self-authored when the user says so;
   keep copy short — a poster is not a brochure);
2. `ART` / `draw_art()` — replace the generative field with the user's image or your own art
   (SVG in mm for the given `x,y,w,h`; `kind = "solid"` gives a flat panel);
3. `PAPER/INK/ACCENT/DARK/WHITE` and `F_LAT/F_CJK/F_MIX` if the brand requires it;
4. `content()` only if the structure must change — every coordinate must stay on
   `g.col/g.row/g.base` multiples.

**Content-length adaptation.** The Chinese title size is computed from its character count so it
fills exactly 4 columns; a 4-char title is ~84 mm on A2, an 8-char title ~42 mm. If a long title
leaves the title block visually bottom-heavy, move its baseline by whole lines only (e.g.
`g.row[2] + 4.0*base`, never `4.2*base`) or set it on two lines. The body/caption lines in
`TEXTS` are hard-wrapped — re-break them to the measure: one column holds about column-width ÷
body-size CJK characters (A2/A3: ~14–15), while the statement block spans two columns (~28–30).
Then re-check the grid proof.

```powershell
& $py .\poster_builder.py --preset a2-32 --outdir out --grid --pdf --preview
```

The builder writes `poster_<preset>.svg/.html`, `*_grid.html`, `spec.md`, and with `--pdf`
the two PDFs plus a JPG preview. For a custom trim use `--page 500x700 --margins 40,50,40,70`
(the 4×8 row structure stays; type and columns rescale from the new geometry).

### Step 5 — prove and verify
- Render `*_grid.pdf` / look at `*_grid.html`: every block's edges on lines, all body lines
  on the baseline, captions whole lines, images whole cells.
- Run `assets/verify_print_pdf.py` (page size, text layer, embedded fonts, crop marks).
- **Look at the preview with `read_image`** — never claim a visual result without inspecting it.
- Fix alignment problems by changing the grid/element size, not by nudging.

### Step 6 — deliver
Artwork PDF + grid PDF + source + `spec.md` + preview; file names carry format and grid
(`poster_a2-32.pdf`). Present the PDFs with the `present` tool and show the preview inline in
the reply. Mention the fiction/placeholder status of self-authored content.

### Step 7 — iterate
Only after the grid proof passes: typographic refinements (tracking on display lines, optical
margin balance, image crop), then re-run the same pipeline. Re-check after every content
change — one added line can break the baseline.

## 4. Geometry cheat sheet

```
k cells, h lines each, 1 empty line between:  N = k·h + (k−1)   (57 → 55, 53 → 9×5+8, 59 → 12×4+11)
cell      = integer × leading
baseline  = cell / n            (poster default n = 6)
column    = (text width − (cols−1) × gutter) / cols
24 pt = 3×8 = 2×12 = 1×24      (8/12/24 pt align)
caption 2 × 6/6 pt = 12 pt = one 10/12 pt body line
8-cell cell = 2 × 32-cell cell + gap (153 pt = 2×69 + 15)
```

Preset numbers (32-cell, mm): see `references/parameters.md`. A2: text 352×494, column 81.2,
gutter 9.0, cell 51.9, gap 11.3, baseline 8.65.

## 5. Typography

- Latin: Arial/Helvetica/Inter; CJK: Noto Sans SC / Microsoft YaHei / Source Han Sans /
  PingFang SC. Give a fallback stack (Latin first, CJK second) so both scripts render.
- Body leading 1.3–1.5× type size (CJK often 1.5–1.8×); display sizes may tighten.
- Tracking only on display lines; body text keeps normal spacing.
- Page numbers one empty line from the type area (or one gutter on the side), aligned to a
  text line.
- No half lines anywhere; no half-cell images; no mixed similar families.

## 6. Images and colour

- Image modules 1/2/3/4 cells; fewer size classes = calmer page.
- Crop on cell edges; add a tint block to lock an image into the grid; illustrations without
  a background get one too.
- Colour + text: inset the text inside the block **or** bleed the block past the grid; never
  letterforms touching the block edge. A spot colour or tint screen is a valid tool.
- Accent colour used deliberately: 1–3 text accents plus the image colour; note CMYK intent
  in `spec.md`.

## 7. Format recipes

`references/patterns.md`: poster, book cover + spread, magazine, annual report/catalogue,
exhibition/3D (cell 150×300 cm, 2×4 cells, eye 170 cm), CI grid sheet, and how to extend the
builder (spread page = 2 × trim width, 8 columns, centre line at the fold).

## 8. Files

```
SKILL.md
references/
  method.md       the system, distillation of the book
  parameters.md   formats, presets, type scales, formulas
  output.md       SVG → browser → PDF pipeline and pitfalls
  qa.md           the delivery gate checklist
  patterns.md     layout recipes, builder extension
assets/
  poster_builder.py     parametric A-series poster builder (copy before editing)
  grid_calculator.py    geometry + type-scale calculator, JSON output
  verify_print_pdf.py   page size / TrimBox / fonts / crop-mark verifier
  example/              reference output (preview JPG, spec.md)
CHANGELOG.md            version history (current 1.1)
```

## 9. Changelog

See `CHANGELOG.md`. Current version 1.1 (2026-10-20): baseline snaps, adaptive title,
safe `--page`, `--preview` implies PDF, PDF TrimBox/BleedBox + metadata, verifier
upgrades, Type0-only fonts, spec completion, strict 4×8 validation.

## 10. Source

Method after Josef Müller-Brockmann, *Grid systems in graphic design* (Niggli, 1981; Chinese
ed. 上海人民美术出版社 2016). The method is distilled from the book; an optional study pack may exist in your workspace.
