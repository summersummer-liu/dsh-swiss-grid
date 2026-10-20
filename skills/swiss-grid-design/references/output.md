# Output — from SVG to print-ready PDF

The skill's renderer is deliberately boring: a browser prints a single SVG page at exact mm
size. No InDesign required, no raster images, text stays real text.

## 1. Pipeline

```
poster_builder.py
  ├─ geometry (mm) ──► poster_<preset>.svg     vector source
  ├─ @page size mm ──► poster_<preset>.html    one page, margin 0
  │                       └─ Edge/Chromium --headless --print-to-pdf ──► PDF
  ├─ overlay layer ──► poster_<preset>_grid.html ──► *_grid.pdf
  └─ pymupdf render ──► *_preview.jpg
```

Command (from the project folder):

```powershell
$py = 'python'   # any Python 3.10+; the DSH runtime python works too
& $py <skill>/assets/poster_builder.py --preset a2-32 --outdir out --grid --pdf --preview
```

`--pdf` locates Edge or Chrome automatically (`Program Files (x86)\Microsoft\Edge\...` etc.).
The print call is:

```
msedge --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf=<abs path> <file url>
```

## 2. Page size and bleed

- In HTML/SVG, `@page { size: <pageW>mm <pageH>mm; margin: 0 }`, body margin 0,
  `svg { display: block }`, viewBox `0 0 <pageW> <pageH>`, coordinates in **mm**.
- `page = trim + 2 × bleed` (A2 420×594 + 3 mm → 426×600 mm).
- Crop marks: short lines in the bleed band, 0.2 mm, offset 0.4 mm from the trim corner
  (the builder draws them in `crop_marks()`).
- Chromium rounds the PDF box by ~0.1 mm — acceptable.
- The builder runs `finalize_pdf()`: it sets **TrimBox** (trim size, inset by the bleed),
  **BleedBox** (full page) and document metadata with PyMuPDF, because Edge only writes one
  MediaBox. Check with `assets/verify_print_pdf.py --pdf out/poster_a2-32.pdf --trim 420x594 --bleed 3`.

## 3. Fonts

- Latin: Arial, Helvetica, Inter, or a neutral grotesque.
- CJK: Microsoft YaHei, Noto Sans SC, Source Han Sans SC, PingFang SC.
- Always give a fallback stack in SVG `font-family` (Latin font first, CJK second) so Latin
  glyphs come from the grotesque and Chinese glyphs fall back to the CJK face.
- Verify embedded fonts in the PDF: `pymupdf` → `page.get_fonts()`. Subsets named
  `AAAAAA+MicrosoftYaHei` etc. are normal.
- Chromium embeds **TrueType (glyf)** faces as Type0 subsets. CFF/OTF and variable CJK fonts
  (Noto Sans SC VF, Source Han Sans) are converted to **Type3 outlines** — fine on screen,
  wrong for print. Keep a TrueType CJK face first (Microsoft YaHei, SimHei) or install a
  static TrueType CJK font. The verifier fails on visible Type3 glyphs.
- Blank Type3 for ideographic spaces is harmless; the builder replaces U+3000 with normal
  spaces, so a clean PDF contains no Type3 at all.

## 4. Geometry gotchas (learned the hard way)

- **SVG user units**: use a viewBox in mm (`viewBox="0 0 426 600"`) and set the root
  `width="426mm" height="600mm"`. Then all coordinates are millimetres.
- **clipPath + translate**: put the clip on an outer `<g>` whose coordinate system is the
  page, put `transform="translate(x,y)"` on an inner `<g>`. Clipping a translated group
  directly can clip in the wrong space.
- **letter-spacing** must be set as a CSS style (`style="letter-spacing:1.2mm"`); the plain
  attribute is not reliable in SVG.
- **Text baselines**: SVG `y` is the baseline. Do not use CSS line boxes for critical grids.
- **Opacity**: use `fill-opacity` / `stroke-opacity`, not `opacity`, when you need the colour
  to stay pure in PDF.
- **Do not use CSS `@page` marks** — draw crop marks yourself.

## 5. Verification

Hard checks (automatic):

| check | tool |
|---|---|
| page size = trim + bleed (±0.6 mm) | `assets/verify_print_pdf.py` |
| TrimBox = trim, BleedBox = page | same |
| text layer present (>50 chars) | same |
| visible glyphs are Type0; Type3 visible text is a failure | same |
| crop-mark pixels near four trim corners | same |
| PDF metadata title present | same (warning only) |

Soft checks (visual — always render a preview and look at it):

- title/image/info blocks start and end exactly on column and row lines;
- every text line sits on the baseline grid (compare with `*_grid.pdf`);
- captions occupy whole lines, never half;
- margins: head < foot, inner < outer; type area sits slightly high;
- no orphan/widow lines in the body copy; no image cropped through a face/object;
- accent colour renders as one flat value (no gradients unless intended).

```powershell
$py = 'python'   # any Python 3.10+; the DSH runtime python works too
& $py out\poster_a2-32_preview.jpg   # or read_image in DSH
& $py <skill>\assets\verify_print_pdf.py --pdf out\poster_a2-32.pdf --trim 420x594 --bleed 3
```

## 6. Deliverable set

```
out/
  poster_a2-32.pdf            print artwork (bleed + crop marks)
  poster_a2-32_grid.pdf       grid diagram (proof / handover)
  poster_a2-32.svg            vector source
  poster_a2-32.html           one-page HTML source
  poster_a2-32_preview.jpg    quick look
  spec.md                     geometry + type-scale table
```

Name files with format and grid, e.g. `poster_a2-32.pdf`, so nobody has to open them to know
what they are.

## 7. If the browser route is unavailable

- Illustrator / Affinity / Inkscape: open the `.svg` (mm sized) — all text is real text, fonts
  must be installed; export PDF with bleed.
- InDesign handover: use `spec.md` (grid coordinates + type sizes) as the layout contract.
- Any HTML renderer: the HTML page prints to PDF at exact size.
