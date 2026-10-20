# QA — the gate before any grid artwork counts as done

Run both layers: **automatic PDF checks** and a **visual grid check**. A layout that "looks
fine" but does not snap to the grid is not finished by this skill's definition.

## 1. Automatic (required)

```powershell
$py = 'python'   # any Python 3.10+; the DSH runtime python works too
& $py <skill>\assets\verify_print_pdf.py --pdf out\poster_a2-32.pdf --trim 420x594 --bleed 3
```

Pass criteria:

- [ ] page size = trim + 2 × bleed within 0.6 mm
- [ ] TrimBox = trim size, inset by the bleed; BleedBox = the full page box
- [ ] text layer present (real text, not outlined)
- [ ] all visible glyphs embedded as Type0 subsets; no visible Type3 glyphs
      (a blank Type3 is acceptable only if ideographic spaces are used)
- [ ] crop marks present near all four trim corners (bleed > 0)
- [ ] preview rendered and inspected (`read_image` / open the JPG)

## 2. Grid check (required)

Open the `*_grid.pdf` and check every element against the lines:

- [ ] every text block starts on a column line and ends on a column line (or is deliberately
      inset by a defined amount);
- [ ] every block's top/bottom sits on a row line, or on the baseline grid inside a cell;
- [ ] body lines are on the 8.65 mm (or format-specific) baseline — no drifting;
- [ ] captions occupy whole lines (1/2/3 lines), never a fraction;
- [ ] images occupy whole cells (1/2/3/4 columns × whole rows) and their top/bottom align to
      text lines or cell edges;
- [ ] the title spans an exact number of columns and its optical left/right edges align;
- [ ] footer/info bands equal whole rows or columns.

If one item fails: change the grid or the element's size — never nudge text off the grid to
make it fit. A small change to the grid is always cheaper than a layout full of exceptions.

## 3. Typographic check

- [ ] one type family per text role; no two similar families mixed;
- [ ] hierarchy by size/weight/style, not by adding fonts;
- [ ] body 8–12 pt equivalent (book) / ≥2.5–3.5 mm cap height (poster); 7–10 words per line;
      CJK ≈14–16 characters per single column, 28–32 when the block spans two columns;
- [ ] leading is constant for body text; headings are whole-line multiples of the body line;
- [ ] no widows/orphans, no single-character last lines in CJK;
- [ ] latin punctuation and CJK punctuation typeset correctly; spaces around inline Latin;
- [ ] letter-spacing on display lines only, never on body text.

## 4. Image / colour check

- [ ] image size classes are few (2–3); no random one-off sizes;
- [ ] images crop on cell edges; faces/subjects not cut;
- [ ] captions sit outside the image or on a defined tint block, not on busy detail;
- [ ] colour blocks either inset text or bleed past the grid — never letterforms touching an
      edge;
- [ ] accent colour used sparingly (1–3 places); paper/ink colours consistent;
- [ ] CMYK intent noted in the spec (flat colour, no RGB-only glow).

## 5. Print check

- [ ] bleed 3 mm (digital) or 5 mm (offset) and crop marks in the bleed band;
- [ ] all elements that should bleed actually cross the trim edge;
- [ ] no hairlines below 0.25 pt; no transparency that flattens badly;
- [ ] final PDF page size noted in `spec.md`;
- [ ] fonts and images embedded; file opens and prints at 100 %.

## 6. Delivery check

- [ ] artwork PDF + grid diagram PDF + source (SVG/HTML) + `spec.md` + preview JPG;
- [ ] names carry format and grid (`poster_a2-32.pdf`);
- [ ] the spec lists: page/bleed, text area, grid, baseline, type sizes, colours, fonts;
- [ ] a note says what is replaceable (copy, art, photos) and how to regenerate
      (`python poster_builder.py --preset ... --outdir ... --pdf`).

## Common failure modes

| Symptom | Cause | Fix |
|---|---|---|
| everything 2–3 % too small | print scaling "fit to page" | print at 100 %, `@page` size mm |
| CJK text disappears / tofu | no CJK font in the print environment | install Noto Sans SC or set `font-family` fallback |
| grid lines misaligned in overlay | overlay coordinates computed separately | derive from the same `Grid` object |
| crop marks missing | drawn outside the media box | keep marks inside the bleed band |
| PDF page 1 mm off | Chromium rounding | tolerance 0.6 mm in verifier; fine for print |
| Type3 font in preflight | CJK face is CFF/OTF/variable and gets outlined by Chromium | put a TrueType (glyf) CJK face first (Microsoft YaHei/SimHei) or install a static TTF |
