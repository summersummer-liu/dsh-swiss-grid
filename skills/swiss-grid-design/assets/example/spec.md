# Poster spec — 合成自然 / SYNTHETIC NATURE

## Page and print
- trim: 420.00 x 594.00 mm; bleed 3.0 mm; PDF page 426.00 x 600.00 mm
- TrimBox 3.0 mm inset; BleedBox = full page; crop marks in bleed band
- RGB PDF for screen/office print; for offset CMYK ask the printer to convert, or convert in Acrobat/Ghostscript before prepress
- vector text; minimum stroke 0.25 pt (0.088 mm)

## Grid
- 4 columns x 8 rows = 32 cells (preset a2-32)
- text area: 352.00 x 494.00 mm at (37.00, 45.00)
- column 81.23 mm, gutter 9.02 mm; cell 51.88 mm, row gap 11.28 mm; baseline 8.65 mm (cell / 6)
- column x (mm): 37.00, 127.25, 217.51, 307.76
- row y (mm): 45.00, 108.16, 171.32, 234.48, 297.64, 360.80, 423.96, 487.12

## Type scale (mm / pt)
| role | mm | pt |
|---|---|---|
| title | 84.00 | 238.1 |
| en_title | 7.39 | 21.0 |
| tagline | 6.40 | 18.1 |
| body | 5.59 | 15.9 |
| date | 4.80 | 13.6 |
| section | 4.50 | 12.7 |
| info | 3.40 | 9.6 |
| label | 3.10 | 8.8 |
| caption | 2.59 | 7.4 |
| footer_big | 8.59 | 24.4 |
| footer_small | 2.80 | 7.9 |

## Colours (RGB -> approximate CMYK)

- paper: #F4F2EC -> CMYK 0/1/3/4
- ink: #111111 -> CMYK 0/0/0/93
- accent: #FF3B00 -> CMYK 0/77/100/0
- dark: #0C0C0C -> CMYK 0/0/0/95
- white: #F7F5F0 -> CMYK 0/1/3/3

## Fonts

- Latin: `Arial, Helvetica, sans-serif`
- CJK: `'Microsoft YaHei', 'SimHei', 'PingFang SC', 'Noto Sans SC', 'Source Han Sans SC', sans-serif`
- the PDF must embed Type0 subsets; a Type3 entry usually means only blank ideographic spaces were rasterised (harmless) — see references/output.md

## Replaceable content

- `TEXTS` — all copy (title, dates, body lines, lists, footer)
- `ART` / `draw_art()` — hero image or generative artwork
- `PAPER / INK / ACCENT / DARK / WHITE` and `F_LAT / F_CJK / F_MIX`
- `content()` — element structure; keep every coordinate on `g.col/g.row/g.base`

## Reproduce

```powershell
python poster_builder.py --preset a2-32 --outdir _example_build --grid --pdf --preview
```

## Files

- poster_a2-32.svg
- poster_a2-32.html
- poster_a2-32_grid.html
- poster_a2-32.pdf
- poster_a2-32_grid.pdf
- poster_a2-32_preview.jpg
