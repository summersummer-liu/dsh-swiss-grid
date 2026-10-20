# -*- coding: utf-8 -*-
"""Grid geometry calculator for the Swiss-grid method.

Print all numbers needed to lay out a page with a Müller-Brockmann-style grid:
text area, column/row positions, cell size, baseline, and a type scale derived
from that baseline.

Examples:
  python grid_calculator.py --preset a2-32
  python grid_calculator.py --preset a4-32
  python grid_calculator.py --page 420x594 --margins 34,42,34,57.7 --cols 4 \
      --col-gap 9 --rows 8 --row-gap 11.3
  python grid_calculator.py --preset a1-32 --json out/a1_grid.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from poster_builder import PRESETS, Grid, SCALE, TITLE_EM  # noqa: E402


def parse_page(s):
    w, h = s.lower().split("x")
    return float(w), float(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", choices=sorted(PRESETS))
    ap.add_argument("--page", help="WxH mm, e.g. 420x594")
    ap.add_argument("--margins", help="left,top,right,bottom mm")
    ap.add_argument("--cols", type=int)
    ap.add_argument("--col-gap", type=float)
    ap.add_argument("--rows", type=int)
    ap.add_argument("--row-gap", type=float)
    ap.add_argument("--bleed", type=float, default=3.0)
    ap.add_argument("--json", help="write geometry as JSON to this path")
    args = ap.parse_args()

    if args.page:
        g = Grid(page=parse_page(args.page), bleed=args.bleed, cols=args.cols,
                 margins=tuple(float(v) for v in args.margins.split(",")) if args.margins else None,
                 rows=args.rows, col_gap=args.col_gap, row_gap=args.row_gap)
    else:
        g = Grid(args.preset or "a2-32", bleed=args.bleed, cols=args.cols,
                 margins=tuple(float(v) for v in args.margins.split(",")) if args.margins else None,
                 rows=args.rows, col_gap=args.col_gap, row_gap=args.row_gap)

    print("# Grid geometry\n")
    print(f"- trim: {g.w:.2f} x {g.h:.2f} mm; bleed {g.bleed:.1f} mm -> page {g.pw:.2f} x {g.ph:.2f} mm")
    print(f"- text area: {g.tw:.2f} x {g.th:.2f} mm at ({g.x0:.2f}, {g.y0:.2f}) -> ({g.right:.2f}, {g.bottom:.2f})")
    print(f"- margins: left {g.p['margin_side']:.2f}, top {g.p['margin_top']:.2f}, "
          f"right {g.p['margin_side']:.2f}, bottom {g.p['margin_bottom']:.2f}")
    print(f"- grid: {g.p['cols']} cols x {g.p['rows']} rows = {g.p['cols'] * g.p['rows']} cells")
    print(f"- column {g.cw:.2f} mm, gutter {g.p['col_gap']:.2f} mm")
    print(f"- cell {g.cell:.2f} mm, row gap {g.p['row_gap']:.2f} mm")
    print(f"- baseline {g.base:.2f} mm (cell / 6)\n")
    print("column x (mm): " + ", ".join(f"{v:.2f}" for v in g.col))
    print("row y (mm):    " + ", ".join(f"{v:.2f}" for v in g.row))
    print("\n## Type scale (multiples of baseline unless noted)\n")
    print("| role | size mm | pt | ratio |")
    print("|---|---|---|---|")
    for role in ["title", "en_title", "tagline", "body", "date", "section", "info", "label",
                 "caption", "footer_big", "footer_small"]:
        mm = g.sizes[role]
        ratio = TITLE_EM if role == "title" else SCALE[role]
        note = "× column width" if role == "title" else "× baseline"
        print(f"| {role} | {mm:.2f} | {mm * 2.8346:.1f} | {ratio:.3f} {note} |")
    print(f"\nBaseline-grid check: cell = {g.cell:.2f} mm = 6 x {g.base:.2f} mm; "
          f"body {g.sizes['body']:.2f} mm = {g.sizes['body'] / g.base:.2f} x baseline")
    print(f"Line count per cell: {g.cell / g.base:.0f} lines; rows total: {g.p['rows']} x {g.cell / g.base:.0f} = "
          f"{g.p['rows'] * g.cell / g.base:.0f} lines")

    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        data = {
            "trim": [g.w, g.h], "bleed": g.bleed, "page": [g.pw, g.ph],
            "text_area": [g.x0, g.y0, g.tw, g.th],
            "margins": [g.p["margin_side"], g.p["margin_top"], g.p["margin_side"], g.p["margin_bottom"]],
            "grid": {"cols": g.p["cols"], "rows": g.p["rows"], "cols_x": g.col, "rows_y": g.row,
                     "column": g.cw, "col_gap": g.p["col_gap"], "cell": g.cell, "row_gap": g.p["row_gap"],
                     "baseline": g.base},
            "types": {k: g.sizes[k] for k in g.sizes},
        }
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("\njson ->", args.json)


if __name__ == "__main__":
    main()
