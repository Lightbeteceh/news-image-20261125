#!/usr/bin/env python3
"""The World in One Day - 25 November 2026.

A deterministic program that draws one 1024x1024 newspaper front page
summing up Wednesday 25 November 2026 from stories.json. No network, no
clock, no randomness: running it twice writes byte-identical PNG bytes.

Usage: python3 main.py   (writes /output/entry.png, or $OUTPUT_PATH)
"""
import hashlib
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
DATA = BASE / "stories.json"
FONTS = BASE / "fonts"

W, H = 1024, 1024
PAPER = (246, 239, 220)
INK = (26, 26, 26)
MUTED = (96, 90, 76)
RED = (163, 22, 33)
BLUE = (29, 78, 137)
GREEN = (31, 111, 68)
AMBER = (176, 110, 0)
PURPLE = (98, 70, 140)
LINE = (70, 64, 50)
CARD = (255, 252, 242)
BAND = (233, 225, 204)
MAPBG = (226, 232, 226)

TAG_COLORS = {
    "CONFIRMED": GREEN,
    "OFFICIAL": BLUE,
    "REPORTED": AMBER,
    "FORECAST": PURPLE,
}

MARGIN = 26
CW = W - 2 * MARGIN


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def serif_b(size):
    return font("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return font("DejaVuSerif.ttf", size)


def sans_b(size):
    return font("DejaVuSans-Bold.ttf", size)


def sans(size):
    return font("DejaVuSans.ttf", size)


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill, leading, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and text_w(draw, lines[-1] + "...", fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "..."
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def truncate(draw, text, fnt, max_w):
    if text_w(draw, text, fnt) <= max_w:
        return text
    while text and text_w(draw, text + "...", fnt) > max_w:
        text = text[:-1]
    return text.rstrip() + "..."


def tag_chip(draw, x, y, tag):
    fnt = sans_b(8)
    label = " " + tag + " "
    tw = text_w(draw, label, fnt)
    color = TAG_COLORS.get(tag, MUTED)
    draw.rounded_rectangle([x, y, x + tw + 6, y + 14], radius=3, fill=color)
    draw.text((x + 3, y + 2), label, font=fnt, fill=(255, 255, 255))
    return tw + 6


def rule(draw, x0, x1, y, width=1, fill=LINE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_card(draw, box, kicker, title, body, tag, source, tsize=15, bsize=10):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=CARD, outline=LINE, width=1)
    inner = x0 + 9
    iw = x1 - x0 - 18
    y = y0 + 8
    kf = sans_b(8)
    draw.text((inner, y), kicker, font=kf, fill=RED)
    y += 13
    y = draw_wrapped(draw, inner, y, title, serif_b(tsize), iw, INK,
                     int(tsize * 1.18), max_lines=3)
    y += 2
    body_leading = int(bsize * 1.32)
    avail = (y1 - 24) - y
    body_lines = max(1, avail // body_leading)
    y = draw_wrapped(draw, inner, y, body, sans(bsize), iw, (48, 48, 44),
                     body_leading, max_lines=body_lines)
    fy = y1 - 19
    chip_w = tag_chip(draw, inner, fy, tag)
    sf = sans(7)
    src = truncate(draw, source, sf, iw - chip_w - 8)
    draw.text((inner + chip_w + 8, fy + 2), src, font=sf, fill=MUTED)
    return y


def draw_header(draw, data):
    x0 = MARGIN
    x1 = W - MARGIN
    y = 24
    title = "THE WORLD IN ONE DAY"
    tf = serif_b(52)
    tw = text_w(draw, title, tf)
    draw.text(((W - tw) / 2, y), title, font=tf, fill=INK)
    y += 62
    rule(draw, x0, x1, y, width=2)
    y += 6
    sub = data["dateline"] + "  ·  " + data["subtitle"]
    sf = sans_b(11)
    sw = text_w(draw, sub, sf)
    draw.text(((W - sw) / 2, y), sub, font=sf, fill=RED)
    y += 20
    rule(draw, x0, x1, y, width=1)
    return y + 8


def draw_utc_strip(draw, data, y):
    x0 = MARGIN
    x1 = W - MARGIN
    label = "THE DAY IN UTC"
    lf = sans_b(10)
    draw.text((x0, y), label, font=lf, fill=INK)
    y += 16
    draw.rectangle([x0, y, x1, y + 62], fill=BAND, outline=LINE, width=1)
    n = len(data["utc"])
    col_w = CW / n
    for i, ev in enumerate(data["utc"]):
        cx = x0 + i * col_w
        if i:
            draw.line([(cx, y + 6), (cx, y + 56)], fill=(190, 182, 160), width=1)
        tx = cx + 7
        tw = col_w - 14
        tf = sans_b(10)
        draw.text((tx, y + 5), ev["time"], font=tf, fill=RED)
        draw_wrapped(draw, tx, y + 20, ev["text"], sans(8), tw, INK, 10,
                     max_lines=4)
    return y + 62 + 8


def draw_numbers_strip(draw, data, y):
    x0 = MARGIN
    x1 = W - MARGIN
    label = "THE DAY IN NUMBERS"
    lf = sans_b(10)
    draw.text((x0, y), label, font=lf, fill=INK)
    y += 16
    draw.rectangle([x0, y, x1, y + 52], fill=CARD, outline=LINE, width=1)
    n = len(data["numbers"])
    col_w = CW / n
    for i, num in enumerate(data["numbers"]):
        cx = x0 + i * col_w
        if i:
            draw.line([(cx, y + 6), (cx, y + 46)], fill=(190, 182, 160), width=1)
        tx = cx + 7
        tw = col_w - 14
        vf = serif_b(19)
        val = num["value"]
        while text_w(draw, val, vf) > tw and vf.size > 13:
            vf = serif_b(vf.size - 1)
        draw.text((tx, y + 4), val, font=vf, fill=INK)
        draw_wrapped(draw, tx, y + 28, num["label"], sans_b(7), tw, MUTED, 9,
                     max_lines=2)
    return y + 52 + 8


def draw_lead(draw, data, y):
    lead = data["lead"]
    x0 = MARGIN
    x1 = W - MARGIN
    y1 = y + 118
    draw_card(draw, (x0, y, x1, y1),
              "LEAD  ·  " + lead["region"].upper(),
              lead["title"], lead["text"], lead["tag"], lead["source"],
              tsize=26, bsize=10)
    return y1 + 8


def draw_big(draw, data, y):
    x0 = MARGIN
    gap = 10
    bw = (CW - gap) // 2
    y1 = y + 104
    for i, story in enumerate(data["big"]):
        bx0 = x0 + i * (bw + gap)
        draw_card(draw, (bx0, y, bx0 + bw, y1),
                  "BIG STORY  ·  " + story["region"].upper(),
                  story["title"], story["text"], story["tag"],
                  story["source"], tsize=14, bsize=9)
    return y1 + 8


def draw_small(draw, data, y):
    x0 = MARGIN
    gap = 8
    ncols = 5
    bw = (CW - (ncols - 1) * gap) // ncols
    row_h = 100
    for r in range(2):
        for c in range(ncols):
            story = data["small"][r * ncols + c]
            bx0 = x0 + c * (bw + gap)
            by0 = y + r * (row_h + gap)
            draw_card(draw, (bx0, by0, bx0 + bw, by0 + row_h),
                      str(story["id"]) + "  ·  " + story["region"].upper(),
                      story["title"], story["text"], story["tag"],
                      story["source"], tsize=10, bsize=8)
    return y + 2 * row_h + gap + 8


def draw_map_row(draw, data, y):
    x0 = MARGIN
    h = 72
    y1 = y + h
    map_w = 560
    gap = 10
    draw.rectangle([x0, y, x0 + map_w, y1], fill=MAPBG, outline=LINE, width=1)
    lf = sans_b(9)
    draw.text((x0 + 8, y + 5), "WHERE IT HAPPENED — STORIES PER REGION",
              font=lf, fill=INK)
    order = ["Europe", "Asia", "Middle East", "Africa",
             "North America", "South America", "Oceania", "World"]
    counts = data["regions"]
    cell_w = (map_w - 16) / 4
    for i, region in enumerate(order):
        cx = x0 + 8 + (i % 4) * cell_w
        cy = y + 20 + (i // 4) * 25
        cf = serif_b(15)
        draw.text((cx, cy), str(counts[region]), font=cf, fill=RED)
        nf = sans(7)
        label = region.upper()
        draw.text((cx + 26, cy + 4), label, font=nf, fill=INK)
    bx0 = x0 + map_w + gap
    bx1 = W - MARGIN
    draw.rectangle([bx0, y, bx1, y1], fill=CARD, outline=LINE, width=1)
    draw.text((bx0 + 8, y + 5), "DATE CHECK", font=sans_b(9), fill=RED)
    note = ("Wednesday 25 November 2026. Cut-off 09:00 UTC; two items are "
            "scheduled, not yet happened: the Phala Phala ruling and US GDP "
            "data due 13:30 GMT. Tuesday closes are labelled TUE.")
    draw_wrapped(draw, bx0 + 8, y + 20, note, sans(8), bx1 - bx0 - 16,
                 INK, 11, max_lines=4)
    return y1 + 6


def draw_also(draw, data, y):
    x0 = MARGIN
    lf = sans_b(10)
    draw.text((x0, y), "ALSO ON WEDNESDAY 25 NOVEMBER — 14 TO 38",
              font=lf, fill=INK)
    y += 15
    rule(draw, x0, W - MARGIN, y, width=1)
    y += 5
    col_gap = 14
    col_w = (CW - col_gap) // 2
    items = data["also"]
    per_col = 13
    for col in range(2):
        cx = x0 + col * (col_w + col_gap)
        cy = y
        for item in items[col * per_col:(col + 1) * per_col]:
            num = str(item["id"]) + ". "
            nf = sans_b(8)
            draw.text((cx, cy), num, font=nf, fill=RED)
            nx = cx + text_w(draw, num, nf)
            rest_w = col_w - (nx - cx)
            tf = sans_b(7)
            title = item["title"]
            full = title + " — " + item["text"]
            line = truncate(draw, full, tf, rest_w)
            # Title stays bold; the tail is drawn in the same line.
            draw.text((nx, cy), line, font=tf, fill=INK)
            cy += 11
    return y + per_col * 11 + 4


def draw_footer(draw, y):
    x0 = MARGIN
    x1 = W - MARGIN
    rule(draw, x0, x1, y, width=1)
    y += 5
    legend = ("CONFIRMED — reported as fact   ·   OFFICIAL — government or "
              "UN statement   ·   REPORTED — claim, not independently "
              "verified   ·   FORECAST — scheduled")
    draw.text((x0, y), legend, font=sans(7), fill=MUTED)
    y += 11
    credit = ("Sources are named on every story. Partial day: cut-off 09:00 UTC. "
              "Drawn by main.py — deterministic, no network, no clock.")
    draw.text((x0, y), credit, font=sans(7), fill=MUTED)
    return y + 11


def main():
    with open(DATA, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    y = draw_header(draw, data)
    y = draw_utc_strip(draw, data, y)
    y = draw_numbers_strip(draw, data, y)
    y = draw_lead(draw, data, y)
    y = draw_big(draw, data, y)
    y = draw_small(draw, data, y)
    y = draw_map_row(draw, data, y)
    y = draw_also(draw, data, y)
    draw_footer(draw, y)
    out = Path(os.environ.get("OUTPUT_PATH", "/output/entry.png"))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG")
    raw = out.read_bytes()
    print("wrote", out, len(raw), "bytes sha256",
          hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
