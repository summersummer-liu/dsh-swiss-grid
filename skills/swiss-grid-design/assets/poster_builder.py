# -*- coding: utf-8 -*-
"""Parametric Swiss-grid poster builder (Müller-Brockmann method).

Copy this file into your project and edit CONFIG / TEXTS / COLORS / ART at the
bottom of this header block. It renders:

  <outdir>/poster.html   -> print with Edge/Chromium to PDF
  <outdir>/poster.svg    -> vector source
  <outdir>/grid.html     -> same layout, faded, with grid + dimension overlay
  <outdir>/spec.md       -> geometry + type-scale table

Usage:
  python poster_builder.py --preset a2-32 --outdir out
  python poster_builder.py --preset a2-32 --outdir out --grid --pdf --preview
  python poster_builder.py --preset a3-32 --outdir out --pdf

Requirements: Python 3.10+; optional pymupdf (PDF preview/verification),
Pillow (JPG preview), Microsoft Edge or Chromium (PDF printing).
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import xml.sax.saxutils as sx

# ============================== CONFIG ======================================
BLEED = 3.0                 # mm, 0 to disable bleed and crop marks
MARGIN_TOP_RATIO = 0.42     # share of vertical margin given to the head
# colours (hex)
PAPER = "#F4F2EC"
INK = "#111111"
ACCENT = "#FF3B00"
DARK = "#0C0C0C"
WHITE = "#F7F5F0"

# font stacks: latin / CJK / mixed
F_LAT = "Arial, Helvetica, sans-serif"
# TrueType (glyf) CJK faces embed as Type0 in Chromium; CFF/OTF and variable CJK
# fonts (Noto Sans SC VF, Source Han Sans) are emitted as Type3. Keep a glyf face first.
F_CJK = "'Microsoft YaHei', 'SimHei', 'PingFang SC', 'Noto Sans SC', 'Source Han Sans SC', sans-serif"
F_MIX = "Arial, Helvetica, 'Microsoft YaHei', 'Noto Sans SC', sans-serif"

# type scale: multiples of the baseline (BASE = cell height / 6)
SCALE = {
    "en_title": 0.855,
    "tagline": 0.740,
    "body": 0.647,
    "date": 0.555,
    "section": 0.520,
    "info": 0.393,
    "label": 0.358,
    "caption": 0.300,
    "footer_big": 0.994,
    "footer_small": 0.324,
}
TITLE_EM = 1.034            # reference only (4-char title on A2)
TITLE_TRACK = 0.0635        # tracking as a fraction of the title size

# generative art (replace draw_art() for your own; kind = cell_field | solid)
ART = {
    "kind": "cell_field",
    "colonies": [
        (0.165, 0.471, 0.114, 1.00), (0.432, 0.236, 0.080, 0.80),
        (0.710, 0.662, 0.131, 1.05), (0.881, 0.325, 0.074, 0.72),
        (0.557, 0.796, 0.091, 0.68), (0.273, 0.112, 0.057, 0.55),
        (0.812, 0.864, 0.057, 0.50),
    ],
    "ripple": 0.045,
}

TEXTS = {
    "kicker_cn": "2026 国际科技艺术展",
    "kicker_en": "INTERNATIONAL TECH-ART EXHIBITION",
    "dates": "2026.11.14 — 2027.02.08",
    "city": "SHENZHEN · 深圳",
    "tagline": "当自然可以被编写，我们如何重新设计生命？",
    "en_title": "SYNTHETIC NATURE",
    "en_sub": "A GROUP EXHIBITION ON SYNTHETIC BIOLOGY, ARTIFICIAL INTELLIGENCE & ECOLOGY",
    "cn_title": "合成自然",
    "caption_left": "PLATE 01 / 细胞场 — CELLULAR FIELD",
    "caption_right": "24 位/组艺术家 · 4 大板块 · 90 天展期",
    "label_statement": "策展论述 / STATEMENT",
    "body": [
        "当生命可以被编写，自然便不再是给定的。",
        "24 位/组艺术家以算法、合成生物、机器感知",
        "与数据气候为媒介，在展厅中培育一片不断生长",
        "的「第二自然」——一半是花园，一半是实验室。",
    ],
    "label_programme": "展览板块 / PROGRAMME",
    "programme": [
        ("01", "生成生命", "GENERATIVE LIFE"),
        ("02", "机器感知", "MACHINE PERCEPTION"),
        ("03", "硅基花园", "SILICON GARDEN"),
        ("04", "数据气候", "DATA CLIMATE"),
    ],
    "label_visit": "参观信息 / VISIT",
    "visit": [
        "2026.11.14—2027.02.08",
        "周二至周日 10:00—19:00 / 周一闭馆",
        "深圳 · 前海科技艺术中心 L1 主展厅",
        "QIANHAI CENTER FOR TECH & ART",
    ],
    "tickets": "早鸟 68 / 正价 98 / 学生 48",
    "footer_big": "SYNTHETIC NATURE",
    "footer_url": "syntheticnature.art",
    "footer_line": "主办 未来媒介实验室 / 深圳科技艺术基金会  策展人 李明远  联合策展 Anna Keller、周未",
    "footer_right": "TICKETS 68 / 98 / 48  ·  @syntheticnature",
}

# ============================ GEOMETRY ======================================
# Base: the book's A4 32-cell system (4 columns x 8 rows) in mm.
A4 = dict(page=(210.0, 297.0), text=(176.0, 247.0), cols=4, rows=8)

PRESETS = {}
for name, s, page in [
    ("a4-32", 1.0, (210.0, 297.0)),
    ("a3-32", 1.4142, (297.0, 420.0)),
    ("a2-32", 2.0, (420.0, 594.0)),
    ("a1-32", 2.8284, (594.0, 841.0)),
    ("a0-32", 4.0, (841.0, 1189.0)),
]:
    tw, th = A4["text"][0] * s, A4["text"][1] * s
    col_gap, row_gap = 4.51 * s, 5.64 * s
    col_w = (tw - (A4["cols"] - 1) * col_gap) / A4["cols"]
    cell = (th - (A4["rows"] - 1) * row_gap) / A4["rows"]
    mx = (page[0] - tw) / 2.0
    my = page[1] - th
    PRESETS[name] = dict(
        page=page, cols=A4["cols"], rows=A4["rows"], text_w=tw, text_h=th,
        col_w=col_w, col_gap=col_gap, cell=cell, row_gap=row_gap,
        margin_side=mx, margin_top=my * MARGIN_TOP_RATIO,
        margin_bottom=my * (1 - MARGIN_TOP_RATIO), scale=s,
    )


class Grid:
    def __init__(self, preset="a2-32", bleed=BLEED, page=None, margins=None,
                 cols=None, rows=None, col_gap=None, row_gap=None, strict_layout=False):
        p = dict(PRESETS[preset])
        if page:
            p["page"] = page
        if cols:
            p["cols"] = cols
        if rows:
            p["rows"] = rows
        if col_gap:
            p["col_gap"] = col_gap
        if row_gap:
            p["row_gap"] = row_gap
        if margins:
            mx, mt, mr, mb = margins
            p["text_w"] = p["page"][0] - mx - mr
            p["text_h"] = p["page"][1] - mt - mb
            p["margin_side"] = mx
            p["margin_top"] = mt
            p["margin_bottom"] = mb
        self.p = p
        self.preset = preset
        self.bleed = bleed
        self.w, self.h = p["page"]
        self.pw, self.ph = self.w + 2 * bleed, self.h + 2 * bleed
        self.x0 = bleed + p["margin_side"]
        self.y0 = bleed + p["margin_top"]
        self.tw = p["text_w"]
        self.th = p["text_h"]
        self.right = self.x0 + self.tw
        self.bottom = self.y0 + self.th
        self.cw = (self.tw - (p["cols"] - 1) * p["col_gap"]) / p["cols"]
        self.cell = (self.th - (p["rows"] - 1) * p["row_gap"]) / p["rows"]
        self.col = [self.x0 + i * (self.cw + p["col_gap"]) for i in range(p["cols"])]
        self.row = [self.y0 + i * (self.cell + p["row_gap"]) for i in range(p["rows"])]
        self.base = self.cell / 6.0
        self.sizes = {k: v * self.base for k, v in SCALE.items()}
        self.sizes["title"] = TITLE_EM * self.cw
        if strict_layout and (self.p["cols"] != 4 or self.p["rows"] != 8):
            raise ValueError(
                "poster_builder content() is a fixed 4-column x 8-row layout; "
                "use --page/--margins for other formats, edit content() for other structures, "
                "or use grid_calculator.py for arbitrary grids.")

    def col_x(self, i):
        return self.col[i]

    def row_y(self, i):
        return self.row[i]

    def baselines(self, row, n):
        return [self.row[row] + k * self.base for k in range(1, n + 1)]

    def cell_rect(self, col, row, span_cols=1, span_rows=1):
        x = self.col[col]
        y = self.row[row]
        w = span_cols * self.cw + (span_cols - 1) * self.p["col_gap"]
        h = span_rows * self.cell + (span_rows - 1) * self.p["row_gap"]
        return x, y, w, h


# ============================ SVG HELPERS ==================================
def esc(s):
    return sx.escape(str(s))


def mm(v):
    return f"{v:.2f}"


def text(x, y, s, size, weight=400, fill=INK, anchor="start", ls=0.0, font=F_MIX, opacity=None):
    a = (f'x="{mm(x)}" y="{mm(y)}" font-family="{font}" font-size="{mm(size)}" '
         f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"')
    if ls:
        a += ' style="letter-spacing:%smm"' % mm(ls)
    if opacity is not None:
        a += f' fill-opacity="{opacity}"'
    return f"<text {a}>{esc(s)}</text>"


def rect(x, y, w, h, fill, opacity=None, stroke=None, sw=0.0):
    a = f'x="{mm(x)}" y="{mm(y)}" width="{mm(w)}" height="{mm(h)}" fill="{fill}"'
    if opacity is not None:
        a += f' fill-opacity="{opacity}"'
    if stroke:
        a += f' stroke="{stroke}" stroke-width="{mm(sw)}"'
    return f"<rect {a}/>"


def line(x1, y1, x2, y2, stroke=INK, sw=0.2, dash=None, opacity=None):
    a = (f'x1="{mm(x1)}" y1="{mm(y1)}" x2="{mm(x2)}" y2="{mm(y2)}" '
         f'stroke="{stroke}" stroke-width="{mm(sw)}"')
    if dash:
        a += f' stroke-dasharray="{dash}"'
    if opacity is not None:
        a += f' stroke-opacity="{opacity}"'
    return f"<line {a}/>"


def crop_marks(g):
    """Short trim marks inside the 3 mm bleed band (outside the trim box)."""
    t = g.bleed
    if t <= 0.5:
        return ""
    L = min(2.2, t - 0.4)
    off = 0.4
    out = []
    # corners: (x, y, xdir, ydir) where dir points outward
    for (x, y, dx, dy) in [(t, t, -1, -1), (g.pw - t, t, 1, -1),
                           (t, g.ph - t, -1, 1), (g.pw - t, g.ph - t, 1, 1)]:
        out.append(line(x + dx * (off + L), y, x + dx * off, y, INK, 0.2))
        out.append(line(x, y + dy * (off + L), x, y + dy * off, INK, 0.2))
    return "".join(out)


# ============================== ART ========================================
def field(x, y, w, h):
    f = 0.0
    for (fx, fy, fs, amp) in ART["colonies"]:
        cx, cy, s = fx * w, fy * h, fs * w
        f += amp * math.exp(-(((x - cx) ** 2 + (y - cy) ** 2) / (2 * s * s)))
    f += ART["ripple"] * math.sin(x / (0.0275 * w) + 1.2) * math.sin(y / (0.0207 * h) + 0.4)
    return f


def draw_art(g, x, y, w, h):
    """Replace this function to use your own image / drawing."""
    if ART["kind"] == "solid":
        return ""
    pitch = 0.00866 * w
    nx, ny = int(w / pitch) + 1, int(h / pitch) + 1
    cap = 0.0044 * w
    out = []
    for iy in range(ny):
        cy = iy * pitch
        for ix in range(nx):
            cx = ix * pitch
            r = (field(cx, cy, w, h) - 0.40) * 0.006676 * w
            if r <= 0.04:
                continue
            r = min(r, cap)
            op = min(1.0, 0.28 + r / cap * 0.85)
            out.append(f'<circle cx="{mm(cx)}" cy="{mm(cy)}" r="{mm(r)}" fill="{ACCENT}" fill-opacity="{op:.2f}"/>')
    return f'<g transform="translate({mm(x)},{mm(y)})">{"".join(out)}</g>'


# ============================= COMPOSITION =================================
def content(g):
    P = []
    t = TEXTS
    base = g.base

    # ---- row 1: masthead ----
    sq = 0.97 * base
    P.append(rect(g.x0, g.row[0] + 0.42 * base, sq, sq, ACCENT))
    x_txt = g.x0 + 1.64 * base
    P.append(text(x_txt, g.row[0] + 1.0 * base, t["kicker_cn"], g.sizes["date"], 700, font=F_CJK))
    P.append(text(x_txt, g.row[0] + 2.0 * base, t["kicker_en"], 0.347 * base, 400, ls=0.5 * base / 8.65))
    P.append(text(g.right, g.row[0] + 1.0 * base, t["dates"], g.sizes["date"], 700, anchor="end"))
    P.append(text(g.right, g.row[0] + 2.0 * base, t["city"], g.sizes["caption"] * 1.05, 400, anchor="end", ls=0.5 * base / 8.65))

    # ---- tagline between rows 1 and 2 ----
    P.append(text(g.x0, g.row[0] + 5.0 * base, t["tagline"], g.sizes["tagline"], font=F_CJK))

    # ---- row 2: English title + subtitle ----
    P.append(text(g.x0, g.row[1] + 1.0 * base, t["en_title"], g.sizes["en_title"], 700, ls=1.35 * base / 8.65, font=F_LAT))
    P.append(text(g.x0, g.row[1] + 2.0 * base, t["en_sub"], g.sizes["caption"], 400, ls=0.3 * base / 8.65, font=F_LAT, opacity=0.85))

    # ---- rows 2-3: Chinese title spanning all columns (size adapts to length) ----
    title = t["cn_title"]
    n = max(1, len(title))
    fs = g.tw / (n * (1 + TITLE_TRACK) - TITLE_TRACK)
    g.sizes["title"] = fs
    tr = TITLE_TRACK * fs
    for i, ch in enumerate(title):
        P.append(text(g.x0 + i * (fs + tr), g.row[2] + 5.0 * base, ch,
                      fs, 700, font=F_CJK))

    # ---- rows 4-6: hero panel ----
    ax, ay, aw, ah = g.cell_rect(0, 3, g.p["cols"], 3)
    P.append(rect(ax, ay, aw, ah, DARK))
    P.append('<g clip-path="url(#heroClip)">')
    for i in range(1, g.p["cols"]):
        P.append(line(g.col[i], ay, g.col[i], ay + ah, WHITE, 0.088, opacity=0.16))
    for i in range(1, 3):
        yy = g.row[3] + i * (g.cell + g.p["row_gap"])
        P.append(line(ax, yy, ax + aw, yy, WHITE, 0.088, opacity=0.16))
    P.append(draw_art(g, ax, ay, aw, ah))
    P.append("</g>")

    # plate caption sits inside the hero image, on the last baseline of row 5
    cap_y = g.row[5] + 5.0 * base
    P.append(text(g.x0 + 0.58 * base, cap_y, t["caption_left"], g.sizes["caption"], 700, WHITE, ls=0.4 * base / 8.65))
    P.append(text(g.right - 0.58 * base, cap_y, t["caption_right"], g.sizes["caption"] * 0.96, 400, WHITE, anchor="end", font=F_CJK, opacity=0.75))

    # ---- row 7: three info columns ----
    lab_y = g.row[6] + 1.0 * base
    P.append(text(g.x0, lab_y, t["label_statement"], g.sizes["label"], 700, ls=0.55 * base / 8.65))
    for i, ln in enumerate(t["body"]):
        P.append(text(g.x0, g.row[6] + (2 + i) * base, ln, g.sizes["body"], font=F_CJK))

    c3 = g.col[2]
    P.append(text(c3, lab_y, t["label_programme"], g.sizes["label"], 700, ls=0.55 * base / 8.65))
    for i, (num, cn, en) in enumerate(t["programme"]):
        y = g.row[6] + (2 + i) * base
        P.append(text(c3, y, num, g.sizes["caption"] * 0.93, 400, ACCENT, font=F_LAT))
        P.append(text(c3 + 0.83 * base, y, cn, g.sizes["section"], 700, font=F_CJK))
        P.append(text(c3 + 3.24 * base, y, en, 0.31 * base, 400, font=F_LAT, opacity=0.75))

    c4 = g.col[3]
    P.append(text(c4, lab_y, t["label_visit"], g.sizes["label"], 700, ls=0.55 * base / 8.65))
    for i, ln in enumerate(t["visit"]):
        if i == 0:
            sz, wt = g.sizes["date"], 700
        elif i == 3:
            sz, wt = 0.31 * base, 400
        else:
            sz, wt = g.sizes["info"], 400
        ft = F_LAT if i in (0, 3) else F_CJK
        P.append(text(c4, g.row[6] + (2 + i) * base, ln, sz, wt, font=ft))
    P.append(text(c4, g.row[6] + 6.0 * base, t["tickets"], g.sizes["info"], 700, ACCENT, font=F_CJK))

    # ---- row 8: footer band ----
    fx, fy, fw, fh = g.cell_rect(0, 7, g.p["cols"], 1)
    P.append(rect(fx, fy, fw, fh, DARK))
    P.append(text(fx + 0.58 * base, fy + 2.0 * base, t["footer_big"], g.sizes["footer_big"], 700, WHITE,
                  ls=0.55 * base / 8.65, font=F_LAT))
    P.append(text(fx + fw - 0.58 * base, fy + 2.40 * base, t["footer_url"], g.sizes["date"] * 0.85, 400,
                  WHITE, anchor="end", font=F_LAT))
    P.append(text(fx + 0.58 * base, fy + 4.0 * base, t["footer_line"], g.sizes["footer_small"], 400,
                  WHITE, font=F_CJK, opacity=0.72))
    P.append(text(fx + fw - 0.58 * base, fy + 4.05 * base, t["footer_right"], g.sizes["footer_small"], 700,
                  ACCENT, anchor="end", font=F_LAT))
    return "".join(P)


# =========================== GRID OVERLAY ==================================
def grid_overlay(g):
    O = []
    s = g.base
    O.append(text(g.x0, 2.4 * s, "网格结构图 / GRID STRUCTURE", 0.49 * s, 700, ACCENT, ls=0.6))
    O.append(text(g.x0, 3.3 * s, "SWISS GRID POSTER · A 32-CELL GRID (4 COLS × 8 ROWS)", 0.35 * s, 400, INK,
                  font=F_LAT))
    O.append(rect(g.x0, g.y0, g.tw, g.th, "none", stroke=ACCENT, sw=0.35))
    for i in range(g.p["cols"]):
        O.append(line(g.col[i], g.y0, g.col[i], g.bottom, ACCENT, 0.22))
        O.append(line(g.col[i] + g.cw, g.y0, g.col[i] + g.cw, g.bottom, ACCENT, 0.22))
    for i in range(g.p["rows"]):
        O.append(line(g.x0, g.row[i], g.right, g.row[i], ACCENT, 0.22))
        O.append(line(g.x0, g.row[i] + g.cell, g.right, g.row[i] + g.cell, ACCENT, 0.22))
        for k in range(1, 6):
            O.append(line(g.x0, g.row[i] + k * s, g.right, g.row[i] + k * s, ACCENT, 0.08,
                          dash="2 2", opacity=0.45))
    for i in range(g.p["cols"]):
        cx = g.col[i] + g.cw / 2
        O.append(text(cx, g.y0 - 1.0 * s, "ABCD"[i], 0.53 * s, 700, ACCENT, anchor="middle", font=F_LAT))
        O.append(text(cx, g.y0 - 0.37 * s, f"{g.cw:.2f}", 0.28 * s, 400, ACCENT, anchor="middle", font=F_LAT))
    for i in range(g.p["cols"] - 1):
        gx = g.col[i] + g.cw + g.p["col_gap"] / 2
        O.append(text(gx, g.y0 - 0.37 * s, f"{g.p['col_gap']:.1f}", 0.24 * s, 400, ACCENT, anchor="middle", font=F_LAT))
    for i in range(g.p["rows"]):
        ry = g.row[i] + g.cell / 2 + 0.13 * s
        O.append(text(g.right + 0.35 * s, ry, f"{i + 1}", 0.35 * s, 700, ACCENT, font=F_LAT))
        O.append(text(g.right + 1.06 * s, ry, f"{g.cell:.1f}", 0.28 * s, 400, ACCENT, font=F_LAT))
    for i in range(g.p["rows"] - 1):
        gy = g.row[i] + g.cell + g.p["row_gap"] / 2 + 0.1 * s
        O.append(text(g.right + 1.06 * s, gy, f"{g.p['row_gap']:.1f}", 0.24 * s, 400, ACCENT, font=F_LAT))
    O.append(text(g.right, g.y0 - 2.1 * s, f"版心 {g.tw:.1f} × {g.th:.1f} mm", 0.35 * s, 700, ACCENT,
                  anchor="end", font=F_CJK))
    legend = [
        f"结构 {g.p['cols']} 栏 × {g.p['rows']} 行 = {g.p['cols'] * g.p['rows']} 格；单元 {g.cw:.2f} × {g.cell:.2f} mm；"
        f"栏间距 {g.p['col_gap']:.2f} mm；行间距 {g.p['row_gap']:.2f} mm；基线 {s:.2f} mm（虚线，＝单元高÷6）",
        f"字号 标题 {g.sizes['title']:.1f}｜英文题名 {g.sizes['en_title']:.1f}｜正文 {g.sizes['body']:.1f}/{s:.2f}｜"
        f"信息 {g.sizes['info']:.1f}｜标签 {g.sizes['label']:.1f} mm",
        f"页边距 上 {g.p['margin_top']:.1f} · 下 {g.p['margin_bottom']:.1f} · 左右 {g.p['margin_side']:.1f} mm（+{g.bleed:.0f} mm 出血）",
    ]
    y = g.bottom + 1.25 * s
    for i, ln in enumerate(legend):
        O.append(text(g.x0, y + i * 0.63 * s, ln, 0.31 * s, 400, INK, font=F_CJK))
    return "".join(O)


# ============================== RENDER =====================================
def svg_page(g, body, with_overlay=False):
    defs = (f'<defs><clipPath id="heroClip"><rect x="{mm(g.x0)}" y="{mm(g.row[3])}" '
            f'width="{mm(g.tw)}" height="{mm(g.cell * 3 + g.p["row_gap"] * 2)}"/></clipPath></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{mm(g.pw)}mm" height="{mm(g.ph)}mm" '
            f'viewBox="0 0 {mm(g.pw)} {mm(g.ph)}">{defs}'
            f'<rect x="0" y="0" width="{mm(g.pw)}" height="{mm(g.ph)}" fill="{PAPER}"/>' + body + "</svg>")


def to_html(svg, title, g):
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>{esc(title)}</title>
<style>@page {{ size: {mm(g.pw)}mm {mm(g.ph)}mm; margin: 0; }} html,body {{ margin:0; padding:0; background:#fff; }}
svg {{ display:block; }}</style></head><body>{svg}</body></html>"""


def find_browser():
    cands = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    for name in ("msedge", "chrome", "chromium", "chromium-browser"):
        p = shutil.which(name)
        if p:
            return p
    return None


def print_pdf(html_path, pdf_path):
    exe = find_browser()
    if not exe:
        print("! no Edge/Chromium found; open the HTML and print manually")
        return False
    url = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    cmd = [exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={os.path.abspath(pdf_path)}", url]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180, check=False)
    except Exception as e:  # noqa: BLE001
        print("! print failed:", e)
        return False
    return os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0


def finalize_pdf(pdf_path, g, title, trim=True):
    """Set TrimBox/BleedBox and metadata; Edge only writes one MediaBox."""
    try:
        import pymupdf
    except ImportError:
        print("! pymupdf missing; PDF boxes/metadata not set")
        return False
    pt = 72.0 / 25.4
    try:
        doc = pymupdf.open(pdf_path)
        page = doc[0]
        mb = page.mediabox
        if trim:
            bleed = pymupdf.Rect(0, 0, g.pw * pt, g.ph * pt) & mb
            page.set_bleedbox(bleed)
            trim_rect = pymupdf.Rect(bleed.x0 + g.bleed * pt, bleed.y0 + g.bleed * pt,
                                     bleed.x0 + (g.bleed + g.w) * pt,
                                     bleed.y0 + (g.bleed + g.h) * pt) & bleed
            if trim_rect.is_empty:
                raise ValueError("trim box outside media box")
            page.set_trimbox(trim_rect)
        doc.set_metadata({
            "title": title,
            "author": "swiss-grid-design",
            "subject": f"Swiss-grid layout {g.w:.0f}x{g.h:.0f} mm, {g.p['cols']}x{g.p['rows']} cells",
            "creator": "swiss-grid-design",
            "producer": "Edge/Chromium print + PyMuPDF",
        })
        tmp = pdf_path + ".tmp"
        doc.save(tmp, garbage=3, deflate=True)
        doc.close()
        os.replace(tmp, pdf_path)
        return True
    except Exception as e:  # noqa: BLE001
        print("! finalize_pdf failed:", e)
        return False


def preview_png(pdf_path, jpg_path, width=1600):
    try:
        import pymupdf
        from PIL import Image
    except ImportError:
        print("! pymupdf/Pillow missing; skip preview")
        return
    doc = pymupdf.open(pdf_path)
    pg = doc[0]
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(150 / 72, 150 / 72))
    tmp = os.path.join(os.path.dirname(pdf_path), "_preview.png")
    pix.save(tmp)
    doc.close()
    im = Image.open(tmp)
    h = int(width * im.height / im.width)
    im.resize((width, h), Image.LANCZOS).convert("RGB").save(jpg_path, "JPEG", quality=88, optimize=True)
    os.remove(tmp)


def _hex_to_cmyk(h):
    h = h.lstrip("#")
    r, g, b = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    k = 1 - max(r, g, b)
    if k >= 1:
        return (0, 0, 0, 1)
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return tuple(round(v * 100) for v in (c, m, y, k))


def write_spec(g, outdir, files):
    title = f"{TEXTS['cn_title']} / {TEXTS['en_title']}"
    L = [
        f"# Poster spec — {title}", "",
        "## Page and print",
        f"- trim: {g.w:.2f} x {g.h:.2f} mm; bleed {g.bleed:.1f} mm; PDF page {g.pw:.2f} x {g.ph:.2f} mm",
        f"- TrimBox {g.bleed:.1f} mm inset; BleedBox = full page; crop marks in bleed band",
        "- RGB PDF for screen/office print; for offset CMYK ask the printer to convert, or convert "
        "in Acrobat/Ghostscript before prepress",
        "- vector text; minimum stroke 0.25 pt (0.088 mm)", "",
        "## Grid",
        f"- {g.p['cols']} columns x {g.p['rows']} rows = {g.p['cols'] * g.p['rows']} cells "
        f"(preset {getattr(g, 'preset', '-')})",
        f"- text area: {g.tw:.2f} x {g.th:.2f} mm at ({g.x0:.2f}, {g.y0:.2f})",
        f"- column {g.cw:.2f} mm, gutter {g.p['col_gap']:.2f} mm; cell {g.cell:.2f} mm, "
        f"row gap {g.p['row_gap']:.2f} mm; baseline {g.base:.2f} mm (cell / 6)",
        "- column x (mm): " + ", ".join(f"{x:.2f}" for x in g.col),
        "- row y (mm): " + ", ".join(f"{y:.2f}" for y in g.row), "",
        "## Type scale (mm / pt)",
        "| role | mm | pt |",
        "|---|---|---|",
    ]
    for k in ["title", "en_title", "tagline", "body", "date", "section", "info", "label",
              "caption", "footer_big", "footer_small"]:
        L.append(f"| {k} | {g.sizes[k]:.2f} | {g.sizes[k] * 2.8346:.1f} |")
    L += ["", "## Colours (RGB -> approximate CMYK)", ""]
    for name, hexv in [("paper", PAPER), ("ink", INK), ("accent", ACCENT),
                       ("dark", DARK), ("white", WHITE)]:
        c, m, y, k = _hex_to_cmyk(hexv)
        L.append(f"- {name}: {hexv} -> CMYK {c}/{m}/{y}/{k}")
    L += ["", "## Fonts", "",
          f"- Latin: `{F_LAT}`", f"- CJK: `{F_CJK}`",
          "- the PDF must embed Type0 subsets; a Type3 entry usually means only blank "
          "ideographic spaces were rasterised (harmless) — see references/output.md",
          "", "## Replaceable content", "",
          "- `TEXTS` — all copy (title, dates, body lines, lists, footer)",
          "- `ART` / `draw_art()` — hero image or generative artwork",
          "- `PAPER / INK / ACCENT / DARK / WHITE` and `F_LAT / F_CJK / F_MIX`",
          "- `content()` — element structure; keep every coordinate on `g.col/g.row/g.base`",
          "", "## Reproduce", "", "```powershell"]
    preset = getattr(g, "preset", "a2-32")
    preset_page = PRESETS.get(preset, {}).get("page")
    outname = os.path.basename(os.path.abspath(outdir))
    if preset_page and (round(g.w, 2), round(g.h, 2)) != (round(preset_page[0], 2), round(preset_page[1], 2)):
        mg = (f"{g.p['margin_side']:.2f},{g.p['margin_top']:.2f},"
              f"{g.p['margin_side']:.2f},{g.p['margin_bottom']:.2f}")
        cmd = (f"python poster_builder.py --preset {preset} --page {g.w:g}x{g.h:g} "
               f"--margins {mg} --outdir {outname} --grid --pdf --preview")
    else:
        cmd = (f"python poster_builder.py --preset {preset} --outdir {outname} "
               f"--grid --pdf --preview")
    L += [cmd, "```", ""]
    L += ["## Files", ""]
    for f in files:
        L.append(f"- {os.path.basename(f)}")
    with open(os.path.join(outdir, "spec.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Swiss-grid poster builder")
    ap.add_argument("--preset", default="a2-32", choices=sorted(PRESETS))
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--bleed", type=float, default=BLEED)
    ap.add_argument("--page", help="custom trim WxH mm, e.g. 500x700 (4x8 structure kept)")
    ap.add_argument("--margins", help="custom margins left,top,right,bottom mm; auto-derived from preset if omitted")
    ap.add_argument("--grid", action="store_true", help="also emit grid overlay HTML/PDF")
    ap.add_argument("--pdf", action="store_true", help="print PDF via Edge/Chromium")
    ap.add_argument("--preview", action="store_true", help="JPG preview (implies --pdf)")
    args = ap.parse_args()

    page = None
    w = h = None
    if args.page:
        w, h = [float(v) for v in args.page.lower().split("x")]
        page = (w, h)
    margins = tuple(float(v) for v in args.margins.split(",")) if args.margins else None
    if page and margins is None:
        pr = PRESETS[args.preset]
        fx = pr["margin_side"] / pr["page"][0]
        fy1 = pr["margin_top"] / pr["page"][1]
        fy2 = pr["margin_bottom"] / pr["page"][1]
        margins = (fx * w, fy1 * h, fx * w, fy2 * h)

    g = Grid(args.preset, bleed=args.bleed, page=page, margins=margins, strict_layout=True)
    os.makedirs(args.outdir, exist_ok=True)
    name = f"poster_{args.preset}" if page is None else f"poster_custom_{w:g}x{h:g}"
    title = f"{TEXTS['cn_title']} / {TEXTS['en_title']}"
    body = content(g) + crop_marks(g)
    svg = svg_page(g, body)
    html = to_html(svg, title, g)
    svg_path = os.path.join(args.outdir, name + ".svg")
    html_path = os.path.join(args.outdir, name + ".html")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    files = [svg_path, html_path]

    if args.grid:
        ov = svg_page(g, f'<g opacity="0.26">{content(g)}</g>' + grid_overlay(g), with_overlay=True)
        ov_path = os.path.join(args.outdir, name + "_grid.html")
        with open(ov_path, "w", encoding="utf-8") as f:
            f.write(to_html(ov, "Grid overlay", g))
        files.append(ov_path)

    do_pdf = args.pdf or args.preview
    failed = False
    if do_pdf:
        pdf_path = os.path.join(args.outdir, name + ".pdf")
        if print_pdf(html_path, pdf_path):
            finalize_pdf(pdf_path, g, title, trim=True)
            files.append(pdf_path)
            if args.grid:
                gpdf = os.path.join(args.outdir, name + "_grid.pdf")
                if print_pdf(os.path.join(args.outdir, name + "_grid.html"), gpdf):
                    finalize_pdf(gpdf, g, title + " — grid", trim=False)
                    files.append(gpdf)
            if args.preview:
                jpg = os.path.join(args.outdir, name + "_preview.jpg")
                preview_png(pdf_path, jpg)
                files.append(jpg)
        else:
            print("! PDF printing failed", file=sys.stderr)
            failed = True

    write_spec(g, args.outdir, files)
    print("\n".join(files))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
