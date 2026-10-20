# Method — the Müller-Brockmann grid system, distilled

Source: Josef Müller-Brockmann, *Grid systems in graphic design* (Niggli, 1981; Chinese ed.
上海人民美术出版社 2016). This file is the working summary; the full study pack lives in the
workspace folder `grid-systems/` when available.

---

## 1. Why a grid

- A grid is an **order system**, not decoration: it expresses a structural, predictive design
  attitude — objective, functional, with mathematical logic.
- It lets the designer control **quantity and combination** of visual elements, producing a
  compact, legible, orderly layout that raises the credibility of information.
- It is a **social** position: objective, constructed work can serve public communication;
  systematic work turns design rules into reproducible solutions.
- It is honest work: the grid forces you to inventory content and to analyse it. The done
  state is not "everything added" but "nothing can be removed".

## 2. Components and terms

| Term | Meaning |
|---|---|
| 版心 type area | the area carrying text and images; set by format + margins |
| 栏 column / 栏间距 gutter | vertical text blocks and the space between them |
| 单元网格 unit cell | smallest repeating module; **height = an integer number of body lines**, width = column width |
| 空行 empty line | a full text line left blank; used between cells and above/below images |
| baseline | the body-text line rhythm inside a cell (cell = n × baseline) |
| 天头 head / 地脚 foot / 订口 inner / 切口 outer | margins; head < foot, inner < outer for binding |
| 出血 bleed | 3–5 mm printed beyond the trim; pairs with 1–3 mm cutting tolerance |

## 3. Construction algorithm

1. **Inventory content.** Number of text lines, images and their size classes, captions,
   tables, footnotes, page numbers. Sketch at final proportions (ideally 1:1) with real type
   sizes — a sketch must read like a miniature of the finished piece.
2. **Choose format and margins.** Start from DIN/ISO sizes (A4/A3/A2/A1). Classic margin
   ratio **head 1 : inner 1 : outer 2 : foot 3** for bound books and spreads; single-sheet
   posters may use symmetric side margins. Optically centre the type area (a slightly larger
   foot margin makes it sit correctly). Keep ≥3 mm bleed for print.
3. **Choose columns.** 1, 2, 3 or 4; subdivide: 2→4, 3→6, 4→8→16. Compound grids (e.g. two
   columns above, three below) are allowed if they share the same baseline. More columns means
   smaller type but **every line must still hold ≥7 English words** (or ~25–40 CJK characters).
4. **Set body type and leading**, then derive the cell. Cell height must equal an integer
   number of text lines. Working example from the book:
   - A column of 57 lines, a 4-cell grid with one empty line between cells:
     57 − 3 = 54; 54 ÷ 4 = 13.5 → take **13 lines/cell** → total **4×13 + 3 = 55 lines**.
   - General formula for k cells with h lines each and one empty line between:
     **N = k·h + (k−1)**.
   - 53 lines can be 9×5+8 or 6×8+5; 59 lines can be 12×4+11, 10×5+9, 6×9+5, 5×11+4, 4×14+3.
5. **Build the baseline.** All text lines sit on one baseline grid (pitch = body leading).
   Every type size is a simple multiple of it:
   - 24 pt = 3×8 = 2×12 = 1×24 → 8 pt, 12 pt and 24 pt type align on the same lines;
   - a 2-line caption at 6/6 pt = 12 pt = one 10/12 pt body line;
   - a 20/24 pt heading = two 10/12 pt body lines.
   Keep image heights in whole cells (or whole lines) and align image top to the cap line,
   bottom to the descender line of the adjacent text line.
6. **Snap everything.** Images occupy 1–4 cells or multiples; captions use whole lines only
   (never half a line); colour blocks align to cell edges; page numbers sit one empty line
   from the type area (or one gutter away on the side).
7. **Prove it.** Draw the 1:1 grid overlay and check every element's start/end against grid
   lines. If it does not snap, fix the grid or the proportions — not the type.

## 4. Typographic rules

- Body size 8–12 pt for books; reading distance 30–35 cm; 7–10 words per line.
- Leading: too tight → lines interfere; too loose → the text loses cohesion. A sound ratio
  for body text is roughly **1.3–1.5× the type size**; display sizes may tighten.
- Hierarchy by **size, weight, style** inside one family: medium (light grey), semi-bold
  (middle grey), bold (dark grey). Never mix two similar families (Helvetica vs Univers,
  Garamond vs Bodoni).
- Captions are part of the system: 1–2 lines, aligned to the image edge, never half a line.
- Page numbers: on the centre axis for calm, at the outer edge for liveliness; aligned to a
  text line; one empty line from the type area.
- **CJK adaptation** — square characters fit the grid naturally. Use full-width glyphs, keep
  one character per em, set leading around 1.5–1.8× the character size, and treat punctuation
  width (、。，：) as part of the column measure. Latin/CJK mixing: Latin from a neutral grotesque
  (Arial/Helvetica/Inter), CJK from a modern sans (Noto Sans SC, Microsoft YaHei, Source Han
  Sans, PingFang SC).

## 5. Images, illustration, colour

- Image sizes should differ **little** if the page is to stay calm; too many size classes
  becomes noisy. Use 1/2/3/4-cell modules.
- Cropping: align the crop to cell edges; add a tint panel (grey or spot colour) behind a
  photo to lock it into the grid.
- Illustrations without a background get a tint block; closed geometric illustrations work
  best when exactly one column wide.
- Colour blocks + text: either keep the block on the grid and **inset the text** by a
  proportional margin, or let the block **bleed past the grid** while text stays on the
  column lines. Never let letterforms touch the block edge.
- Spot colour instead of four-colour, or a tint screen, is a legitimate typographic tool.

## 6. Where the system scales

- **Print**: posters, books, catalogues, magazines, annual reports, stationery.
- **Corporate identity**: one grid, one type system, one colour logic across every medium;
  the book's Weishaupt example uses a 30-cell grid on A4 with Helvetica.
- **Three dimensions**: walls, floor and ceiling use the same cell logic; cell size derives
  from room size, information amount, object sizes and furniture; eye level ≈ **170 cm**;
  exhibition boards 150×300 cm with 2×4 = 8 cells; unfold the six faces to plan the grid.
- **History**: Pythagoras → Vitruvius → Dürer → Le Corbusier's Modulor; the Greek grid plan
  of Miletus (51.6×29.9 m blocks), the tatami module (90×180 cm, 1:2), Max Bill's 60×420 cm
  column (1:7) — order as a trans-historical principle.

## 7. Deliverable pair

Every grid layout ships as two documents:

1. the **artwork** (print PDF, bleed + crop marks), and
2. the **grid diagram** — the same artwork faded, with column/row/baseline lines,
   dimensions and type sizes labelled.

The second file is the proof that the first one is actually gridded; it is also the handover
document for collaborators.
