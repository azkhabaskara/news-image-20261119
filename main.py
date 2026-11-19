#!/usr/bin/env python3
"""news-image-20261119: sum up the world's news of Thursday 19 November 2026
in one image.

Pure Python 3.13 standard library only (zlib, struct, os, math, sys): no
network, no files read, no randomness, no clock. The program draws a
newspaper front page -- masthead with the date, one lead story and four
further stories plus two short items -- pixel by pixel with an embedded
5x7 bitmap font, encodes it as a PNG, and writes /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png). Two runs write byte-identical output.
"""

import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 230)
WHITE = (255, 253, 246)
INK = (26, 26, 26)
RED = (179, 38, 30)
NAVY = (31, 78, 121)
BLUE = (47, 117, 181)
SKY = (214, 232, 240)
SAND = (232, 210, 160)
SEA = (58, 122, 158)
TEAL = (38, 110, 100)
GOLD = (201, 162, 39)
ORANGE = (224, 122, 33)
PALE = (255, 248, 220)
GREY = (120, 120, 118)
DARKGREEN = (46, 92, 58)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 pixels, '1' = ink. Uppercase + digits + punctuation.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def rect(x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i], px[i + 1], px[i + 2] = color


def hline(x, y, w, color, t=1):
    rect(x, y, w, t, color)


def vline(x, y, h, color, t=1):
    rect(x, y, t, h, color)


def line(x0, y0, x1, y1, color, t=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        rect(x - t // 2, y - t // 2, t, t, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def circle(cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(xx, yy, color)


def ring(cx, cy, r, color, t=3):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = math.hypot(xx - cx, yy - cy)
            if r - t <= d <= r:
                set_px(xx, yy, color)


def polygon(points, color):
    """Scanline fill of a simple polygon given as [(x, y), ...]."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(max(0, int(xs[i])), min(W, int(xs[i + 1]) + 1)):
                set_px(x, y, color)


def star(cx, cy, r_out, r_in, color, rot=-90):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 36)
        pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
    polygon(pts, color)


# ---------------------------------------------------------------- text
def text_w(s, scale):
    return len(s) * 6 * scale - scale if s else 0


def draw_text(x, y, s, scale, color, align="left"):
    s = s.upper()
    if align == "center":
        x -= text_w(s, scale) // 2
    elif align == "right":
        x -= text_w(s, scale)
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT['?'])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    rect(cx + col * scale, y + row * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def wrap(text, width, scale):
    """Greedy word wrap; returns a list of lines fitting `width` px."""
    words = text.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, text, width, scale, color, leading=None):
    lh = (leading if leading is not None else 7 * scale + 4)
    for i, ln in enumerate(wrap(text, width, scale)):
        draw_text(x, y + i * lh, ln, scale, color)
    return y + len(wrap(text, width, scale)) * lh


# ---------------------------------------------------------------- pictures
def draw_flag_us(x, y, w, h):
    """Simplified Stars and Stripes."""
    rect(x, y, w, h, WHITE)
    for i in range(7):
        rect(x, y + i * (h // 7), w, h // 14 + 1, RED)
    cw, ch = int(w * 0.42), int(h * 0.54)
    rect(x, y, cw, ch, NAVY)
    for r in range(3):
        for c in range(4):
            set_px(x + 5 + c * 9, y + 5 + r * 7, WHITE)


def draw_flag_cn(x, y, w, h):
    rect(x, y, w, h, RED)
    star(x + 16, y + 15, 11, 4, GOLD)
    for sx, sy in ((36, 8), (44, 14), (44, 24), (36, 30)):
        circle(sx + x - 0, sy + y - 0, 2, GOLD)


def draw_flag_ru(x, y, w, h):
    rect(x, y, w, h // 3 + 1, WHITE)
    rect(x, y + h // 3, w, h // 3 + 1, BLUE)
    rect(x, y + 2 * h // 3, w, h - 2 * h // 3, RED)


def draw_lead_picture(x, y, w, h):
    """Three flags over the Shenzhen skyline."""
    rect(x, y, w, h, SKY)
    circle(x + 210, y + 32, 18, (224, 84, 48))         # rising sun
    # skyline silhouettes
    base = y + h - 34
    skyline = [(0, 90), (52, 60), (104, 110), (156, 70), (208, 120),
               (260, 55), (312, 95), (364, 65), (416, 105), (468, 80)]
    for bx, bh in skyline:
        rect(x + bx, base - bh, 48, bh + 34, NAVY)
    for bx, bh in skyline:                                  # lit windows
        for wy in range(base - bh + 8, base - 6, 16):
            for wx in (x + bx + 10, x + bx + 28):
                rect(wx, wy, 5, 6, GOLD)
    rect(x, base, w, 34, (24, 40, 56))                      # ground
    # three flag poles
    poles = [(x + 78, draw_flag_us), (x + 238, draw_flag_cn),
             (x + 398, draw_flag_ru)]
    for px0, fn in poles:
        vline(px0, y + 22, base - y - 18, INK, 4)
        circle(px0, y + 20, 5, GOLD)
        fn(px0 + 4, y + 26, 96, 58)
    # caption strip
    rect(x, y + h - 24, w, 24, NAVY)
    draw_text(x + 10, y + h - 19, "FIRST MEETING OF ITS KIND", 2, WHITE)


def draw_gulf_picture(x, y, w, h):
    """Tanker in the Strait of Hormuz, flame and smoke."""
    rect(x, y, w, h, (250, 222, 182))
    rect(x, y + h // 2, w, h - h // 2, SEA)
    for i in range(4):                                       # waves
        hline(x + (i * 53) % w, y + h // 2 + 12 + i * 14, 34, WHITE, 3)
    # tanker
    rect(x + 34, y + 88, 168, 26, INK)
    rect(x + 150, y + 62, 52, 26, INK)
    rect(x + 158, y + 46, 16, 16, RED)
    # flame above the tanker: tall red-orange tongues, yellow core
    polygon([(x + 56, y + 88), (x + 68, y + 44), (x + 82, y + 66),
             (x + 96, y + 34), (x + 110, y + 62), (x + 124, y + 88)],
            (214, 48, 24))
    polygon([(x + 74, y + 88), (x + 84, y + 58), (x + 96, y + 74),
             (x + 104, y + 88)], (240, 200, 60))
    circle(x + 196, y + 34, 12, GREY)
    circle(x + 210, y + 26, 9, GREY)


def draw_bridge_picture(x, y, w, h):
    """Kerch Bridge: deck, towers, blast."""
    rect(x, y, w, h, (226, 234, 240))
    rect(x, y + h - 34, w, 34, SEA)
    # towers and deck
    rect(x + 48, y + 30, 10, 84, INK)
    rect(x + 178, y + 30, 10, 84, INK)
    hline(x + 8, y + 108, w - 16, INK, 6)
    line(x + 53, y + 32, x + 110, y + 106, INK, 2)
    line(x + 183, y + 32, x + 126, y + 106, INK, 2)
    line(x + 53, y + 32, x + 10, y + 106, INK, 2)
    line(x + 183, y + 32, x + 226, y + 106, INK, 2)
    # blast on the deck
    star(x + 118, y + 92, 30, 12, (240, 200, 60))
    star(x + 118, y + 92, 18, 7, ORANGE)
    circle(x + 118, y + 56, 10, GREY)
    circle(x + 134, y + 44, 8, GREY)


def draw_gaza_picture(x, y, w, h):
    """Sand, the Yellow Line, tanks crossing it."""
    rect(x, y, w, h, SAND)
    rect(x, y + h - 26, w, 26, (206, 178, 128))
    # Yellow Line, diagonal dashed
    for i in range(9):
        lx = x + 12 + i * 26
        ly = y + 18 + i * 12
        line(lx, ly, lx + 16, ly + 8, GOLD, 4)
    # tanks
    for tx, ty in ((x + 52, y + 78), (x + 128, y + 96)):
        rect(tx, ty, 62, 20, DARKGREEN)
        rect(tx + 16, ty - 12, 30, 12, DARKGREEN)
        line(tx + 46, ty - 6, tx + 78, ty - 12, DARKGREEN, 4)
        circle(tx + 14, ty + 22, 7, INK)
        circle(tx + 32, ty + 22, 7, INK)
        circle(tx + 50, ty + 22, 7, INK)


def draw_justice_picture(x, y, w, h):
    """Scales of justice."""
    rect(x, y, w, h, (220, 235, 230))
    cx = x + w // 2
    vline(cx, y + 18, 92, INK, 5)
    hline(cx - 62, y + 26, 124, INK, 5)
    circle(cx, y + 16, 7, GOLD)
    for sx in (cx - 62, cx + 62):
        line(sx, y + 28, sx - 20, y + 66, INK, 3)
        line(sx, y + 28, sx + 20, y + 66, INK, 3)
        polygon([(sx - 24, y + 66), (sx + 24, y + 66), (sx, y + 88)], GOLD)
    rect(cx - 34, y + 108, 68, 8, INK)
    rect(cx - 22, y + 116, 44, 6, INK)


def draw_chart(x, y, w, h, color):
    bars = [0.45, 0.65, 0.55, 0.85, 1.0]
    bw = w // 6
    for i, f in enumerate(bars):
        bh = int(h * f)
        rect(x + i * (bw + 4), y + h - bh, bw, bh, color)
    line(x - 4, y + h + 2, x + w + 4, y + h + 2, INK, 2)


def draw_atom(x, y, r, color):
    ring(x, y, r, color, 3)
    for ang in (30, 90, 150):
        a = math.radians(ang)
        dx, dy = int(r * math.cos(a)), int(r * math.sin(a))
        line(x - dx, y - dy, x + dx, y + dy, color, 2)
    circle(x, y, 5, RED)


# ---------------------------------------------------------------- layout
def panel(x, y, w, h, kicker, kcolor, headline, sub, picture):
    rect(x, y, w, h, WHITE)
    # border
    hline(x, y, w, INK, 3)
    hline(x, y + h - 3, w, INK, 3)
    vline(x, y, h, INK, 3)
    vline(x + w - 3, y, h, INK, 3)
    # kicker band
    rect(x + 3, y + 3, w - 6, 26, kcolor)
    draw_text(x + 12, y + 10, kicker, 2, WHITE)
    # picture
    picture(x + 3, y + 29, w - 6, 130)
    # headline (max 3 lines) + sub (max 4 lines)
    end = draw_para(x + 12, y + 170, headline, w - 24, 3, INK, leading=25)
    draw_para(x + 12, end + 6, sub, w - 24, 2, (64, 64, 64), leading=16)


def build():
    rect(0, 0, W, H, PAPER)
    # outer frame
    hline(0, 0, W, INK, 5)
    hline(0, H - 5, W, INK, 5)
    vline(0, 0, H, INK, 5)
    vline(W - 5, 0, H, INK, 5)

    # ---- masthead
    draw_text(W // 2, 22, "THE WORLD TODAY", 8, INK, align="center")
    hline(120, 92, W - 240, RED, 4)
    draw_text(W // 2, 104, "THURSDAY, 19 NOVEMBER 2026", 5, RED,
              align="center")
    draw_text(W // 2, 146, "FIVE STORIES THAT DEFINED THE DAY", 3, INK,
              align="center")

    # ---- lead story
    lx, ly, lw, lh = 16, 186, 992, 284
    rect(lx, ly, lw, lh, WHITE)
    hline(lx, ly, lw, INK, 3)
    hline(lx, ly + lh - 3, lw, INK, 3)
    vline(lx, ly, lh, INK, 3)
    vline(lx + lw - 3, ly, lh, INK, 3)
    rect(lx + 3, ly + 3, lw - 6, 30, NAVY)
    draw_text(lx + 14, ly + 11, "LEAD STORY  -  SHENZHEN, CHINA", 3, WHITE)
    draw_lead_picture(lx + 12, ly + 45, 520, 224)
    tx = lx + 556
    draw_para(tx, ly + 48, "TRUMP, XI AND PUTIN MEET IN SHENZHEN", 420, 5,
              INK, leading=40)
    draw_para(tx, ly + 48 + 3 * 40 + 8,
              "FIRST THREE-WAY SUMMIT. PEACE DECLARATION ISSUED. "
              "NO DEAL ON UKRAINE OR IRAN.", 420, 3,
              (64, 64, 64), leading=25)

    # ---- four stories
    py, ph, pw = 486, 320, 236
    panel(16, py, pw, ph, "MIDDLE EAST", RED,
          "IRAN HITS KUWAIT AND BAHRAIN",
          "U.S. STRUCK QESHM ISLAND. HOUTHI MISSILE DAMAGES RIYADH TOWER.",
          draw_gulf_picture)
    panel(268, py, pw, ph, "UKRAINE", BLUE,
          "KERCH BRIDGE HIT 3RD TIME",
          "UKRAINE STRIKE HALTS RAIL TRAFFIC TO CRIMEA.",
          draw_bridge_picture)
    panel(520, py, pw, ph, "GAZA", (146, 90, 32),
          "ISRAEL PUSHES INTO GAZA",
          "TANKS CROSS THE CEASEFIRE LINE NEAR NUSEIRAT.",
          draw_gaza_picture)
    panel(772, py, pw, ph, "JUSTICE", TEAL,
          "MYANMAR GUILTY OF GENOCIDE",
          "U.N. COURT RULES ON THE ROHINGYA. FIRST OF ITS KIND.",
          draw_justice_picture)

    # ---- bottom strip: two short items
    by, bh = 822, 140
    for bx in (16, 524):
        rect(bx, by, 484, bh, PALE)
        hline(bx, by, 484, INK, 3)
        hline(bx, by + bh - 3, 484, INK, 3)
        vline(bx, by, bh, INK, 3)
        vline(bx + 481, by, bh, INK, 3)
    draw_text(30, by + 12, "TECH & MARKETS", 2, RED)
    draw_text(30, by + 38, "ANTHROPIC IPO", 3, INK)
    draw_text(30, by + 63, "RAISES $81BN", 3, INK)
    draw_para(30, by + 96, "RECORD DEBUT AT $83 A SHARE.", 350, 2,
              (64, 64, 64), leading=16)
    draw_chart(400, by + 44, 76, 64, BLUE)
    draw_text(538, by + 12, "ASIA", 2, RED)
    draw_text(538, by + 38, "N. KOREA EXPANDS", 3, INK)
    draw_text(538, by + 63, "URANIUM ENRICHMENT", 3, INK)
    draw_para(538, by + 96, "IAEA WARNS OF GROWTH AT YONGBYON.", 350, 2,
              (64, 64, 64), leading=16)
    draw_atom(940, by + 76, 34, NAVY)

    # ---- footer
    hline(120, 978, W - 240, INK, 3)
    draw_text(W // 2, 988, "19 NOVEMBER 2026 - THE WORLD IN ONE IMAGE", 2,
              INK, align="center")


# ---------------------------------------------------------------- PNG out
def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += px[y * W * 3:(y + 1) * W * 3]

    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data +
                struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def main():
    build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes())
    return 0


if __name__ == "__main__":
    sys.exit(main())
