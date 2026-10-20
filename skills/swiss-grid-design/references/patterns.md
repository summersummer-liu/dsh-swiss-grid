# Layout recipes

These are starting structures, expressed in **grid rows** so they survive a format change
(A4/A3/A2/A1 all use the same 8-row 32-cell logic). Use `assets/poster_builder.py` for
posters; for other formats read the geometry from `assets/grid_calculator.py` and use the
same rules in any vector tool.

---

## 1. Poster — single sheet (the builder's default)

Grid: 4 columns × 8 rows = 32 cells. Row budget:

| rows | content |
|---|---|
| 1 | masthead: series label left, dates/city right, accent marker |
| 1–2 | tagline (one line, large) — optional |
| 2 | English title + subtitle |
| 2–3 | Chinese title across all 4 columns |
| 4–6 | hero image / generative field across all 4 columns (4×3 cells) |
| gap 6–7 | plate caption + secondary caption |
| 7 | three information columns: statement (cols 1–2), programme (col 3), visit (col 4) |
| 8 | footer band: wordmark, URL, credits, tickets |

Rules: title spans exactly 4 columns with tracking to justify the width; hero occupies whole
cells; captions sit in a row gap; footer is one row. If content is thin, merge rows 7–8 into
one information band and drop the footer fill.

Scaling: A1 = a1-32, A2 = a2-32, A3 = a3-32; keep the same row logic. For 8-cell posters
(2×4) use rows 1 (masthead), 2–3 (title/image), 4 (info) — fewer, larger blocks.

## 2. Book cover + spread

- Grid: treat the spread as one **8-column** field (4 per page) or a 4-column field per page.
  Spine/centre line is a hard boundary: no text crosses it.
- Margins (single page): head 1 : inner 1 : outer 2 : foot 3 — inner takes binding creep.
- Body: 9/12 or 10/13; captions 7/8; chapter number/title occupy whole baselines (e.g.
  2–4 body lines).
- Cover: use the same grid and type sizes as the inside; cover art may bleed full page.
  Do not "design the cover separately" — the series identity depends on one system.
- Page numbers: one empty line below the type area, on the outer edge (or centred for calm
  books); align to a text line.
- Running heads: one line of caps at the head margin, tracking to column width.

Practical route: build a spread as one wide page (`page = 2 × trim width`) in the builder,
put a centre line at the fold, and set `cols = 8` (or 4 per page via custom column x list).
The builder's row composition stays valid; content functions need a spread layout pass.

## 3. Magazine / journal

- 12-cell (3×4) or 16-cell (4×4) page grid; a 20/32-cell grid when images vary a lot.
- Keep **one baseline** across all article grids; different column counts may share it
  (compound grid: 3 columns of text + 4 columns of captions).
- Typical: 3-column body, 1-column side notes, full-width opener with a 2-column image.
- Use fewer image size classes than you think: 1/4, 1/2, full width is often enough.
- Headlines can hang into the margin by one column if the grid makes it deliberate.

## 4. Annual report / catalogue

- 20–32 cells; image size families (1/2/4/8 cells); tables snap to columns.
- Data pages: numbers right-aligned on a column edge; rules on row lines.
- Captions: 1–2 lines, same font size throughout; align to image left edge.
- Keep the grid identical across the whole document; only the content changes.

## 5. Exhibition / three-dimensional

- Cell module example: board **150×300 cm**, divided 2 columns × 4 rows = 8 cells; text and
  images occupy cells; boards can be prefabricated and reused.
- Unfold the room into six faces (four walls, floor, ceiling) and lay the same grid on each
  face before building; wall openings, lights and furniture snap to cells.
- Eye level ≈ **170 cm**; keep the main text band around it; avoid text below 80 cm.
- One grid across all boards; multi-language panels share the same cell edges.
- Plan at **1:20** scale; the drawings are the contract for the fabricator.

## 6. Corporate identity grid sheet

One page that defines the system for every medium:

- grid diagram with columns/rows/baseline;
- type specimen: family, weights, sizes (headline/body/caption), tracking;
- colour chips and paper;
- logo clear-space = whole cells;
- examples: letterhead, card, folder, poster, vehicle, sign;
- rule list (the book's 13 unification rules condensed):
  same grid on all formats, same type sizes for the same role, images on cell edges,
  no half lines, one colour logic, captions in one size, etc.

## 7. Extending the builder

- Change **format**: `--preset a1-32` / `a3-32`; everything scales from the grid.
- Change **copy**: edit `TEXTS` (all strings live there).
- Change **palette/fonts**: edit `PAPER/INK/ACCENT/DARK/WHITE` and `F_LAT/F_CJK/F_MIX`.
- Change **art**: replace `draw_art()` — return SVG in mm coordinates for the given
  `(x, y, w, h)`; or `ART["kind"] = "solid"` for a flat panel.
- Change **structure**: the `content()` function is the layout; row indices refer to
  `g.row[...]`, columns to `g.col[...]`. Keep every change on `g.row`/`g.col`/`g.base`
  multiples — that is the whole point.
- **Other formats**: copy the builder, replace `content()` with a spread or multi-page
  composition; emit one HTML per page or one long page with page breaks. The geometry,
  crop marks, overlay and verification code stay the same.
