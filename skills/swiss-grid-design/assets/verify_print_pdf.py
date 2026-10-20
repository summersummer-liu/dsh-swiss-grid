# -*- coding: utf-8 -*-
"""Verify a print-ready grid poster PDF.

Checks page size, TrimBox/BleedBox, real text, embedded fonts (Type0 vs Type3),
and crop-mark pixels near the four trim corners.

Usage:
  python verify_print_pdf.py --pdf out/poster_a2-32.pdf --trim 420x594 --bleed 3
Exit code 0 = pass, 1 = hard failure.
"""
import argparse
import sys

try:
    import pymupdf
except ImportError:
    print("pymupdf is required:", sys.executable)
    sys.exit(2)


MM_PT = 72.0 / 25.4


def mm(v):
    return v / 72.0 * 25.4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--trim", default="420x594", help="WxH mm")
    ap.add_argument("--bleed", type=float, default=3.0)
    ap.add_argument("--tolerance", type=float, default=0.6, help="mm")
    ap.add_argument("--pages", type=int, default=1, help="expected page count (0 = ignore)")
    args = ap.parse_args()

    tw, th = [float(v) for v in args.trim.lower().split("x")]
    page_w, page_h = tw + 2 * args.bleed, th + 2 * args.bleed
    doc = pymupdf.open(args.pdf)
    failures, warnings = [], []
    print(f"PDF: {args.pdf}")

    print(f"pages: {doc.page_count}")
    if doc.page_count < 1:
        print("FAIL: empty PDF")
        return 1
    if args.pages and doc.page_count != args.pages:
        warnings.append(f"expected {args.pages} page(s), got {doc.page_count}")

    pg = doc[0]
    w, h = mm(pg.rect.width), mm(pg.rect.height)
    print(f"page: {w:.2f} x {h:.2f} mm (expected {page_w:.2f} x {page_h:.2f})")
    if abs(w - page_w) > args.tolerance or abs(h - page_h) > args.tolerance:
        failures.append("page size does not match trim + bleed")

    # TrimBox / BleedBox
    if args.bleed > 0:
        trim = pg.trimbox
        trim_w, trim_h = mm(trim.width), mm(trim.height)
        print(f"TrimBox: {trim_w:.2f} x {trim_h:.2f} mm at ({mm(trim.x0):.2f}, {mm(trim.y0):.2f})")
        if abs(trim_w - tw) > args.tolerance or abs(trim_h - th) > args.tolerance:
            failures.append("TrimBox does not equal the trim size")
        if abs(mm(trim.x0) - args.bleed) > args.tolerance or abs(mm(trim.y0) - args.bleed) > args.tolerance:
            warnings.append("TrimBox is not inset by the bleed")
        bleed = pg.bleedbox
        print(f"BleedBox: {mm(bleed.width):.2f} x {mm(bleed.height):.2f} mm")
        if abs(mm(bleed.width) - page_w) > args.tolerance or abs(mm(bleed.height) - page_h) > args.tolerance:
            warnings.append("BleedBox does not equal the page box")
    else:
        print("TrimBox: (bleed 0, skipped)")

    # text layer
    text = pg.get_text().strip()
    print(f"text layer: {len(text)} chars")
    if len(text) < 50:
        failures.append("almost no text extracted - text may be outlined")

    # fonts
    fonts = pg.get_fonts(full=True)
    print("fonts:")
    type0 = 0
    for f in fonts:
        name, ftype = f[3], f[2]
        print(f"  - {name or '(unnamed)'}  type={ftype}")
        if ftype == "Type0":
            type0 += 1
    if not fonts:
        failures.append("no fonts reported")
    elif type0 == 0:
        failures.append("no Type0 font found - glyphs may be Type3 outlines")

    # Type3 with visible (non-blank) text is a failure
    t3_chars = []
    for b in pg.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l.get("spans", []):
                if "Type3" in s["font"]:
                    t3_chars.append(s["text"])
    t3_text = "".join(t3_chars)
    visible = t3_text.replace("\u3000", "").replace(" ", "").replace("\n", "")
    print(f"Type3 glyphs: {len(t3_text)} chars (visible: {len(visible)})")
    if visible:
        failures.append("visible glyphs are Type3 outlines - use a TrueType (glyf) CJK font")
    elif t3_text:
        warnings.append("Type3 only used for blank ideographic spaces (harmless)")

    # images / vectors
    print(f"raster images: {len(pg.get_images(full=True))}")
    print(f"vector drawings: {len(pg.get_drawings())}")

    # crop marks: scan rendered pixels near the four trim corners
    def corner_dark(x0, y0, dx, dy):
        x1 = 0.0 if dx < 0 else x0 - 1
        x2 = x0 + 1 if dx < 0 else page_w
        y1 = 0.0 if dy < 0 else y0 - 1
        y2 = y0 + 1 if dy < 0 else page_h
        clip = pymupdf.Rect(x1 * MM_PT, y1 * MM_PT, x2 * MM_PT, y2 * MM_PT)
        pix = pg.get_pixmap(matrix=pymupdf.Matrix(6, 6), clip=clip, colorspace=pymupdf.csGRAY)
        import numpy as np
        a = np.frombuffer(pix.samples, dtype=np.uint8)
        return int((a < 120).sum())

    t = args.bleed
    if t > 0:
        corners = [(t, t, -1, -1), (page_w - t, t, 1, -1), (t, page_h - t, -1, 1),
                   (page_w - t, page_h - t, 1, 1)]
        hits = [corner_dark(x, y, dx, dy) for (x, y, dx, dy) in corners]
        print("dark px near trim corners:", hits)
        if min(hits) < 20:
            warnings.append("few/no dark pixels near a trim corner - crop marks may be missing")

    # metadata (soft)
    title = (doc.metadata or {}).get("title", "")
    if not title:
        warnings.append("PDF metadata has no title")

    doc.close()
    print()
    for wmsg in warnings:
        print("WARN:", wmsg)
    for f in failures:
        print("FAIL:", f)
    if failures:
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: PASS" + (" (with warnings)" if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
