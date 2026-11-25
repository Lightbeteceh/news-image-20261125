#!/usr/bin/env python3
"""The World in One Day -- 25 November 2026.

Renders one 1024x1024 newspaper front page summing up 25 November's
world news from stories.json (38 verified stories, 8 regions).
Deterministic: no randomness, no clock, no network.
Output: $OUTPUT_PATH, default /output/entry.png.
"""
import json
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 241, 227)
PAPER = (252, 249, 240)
INK = (26, 26, 26)
MUTED = (90, 86, 76)
RULE = (26, 26, 26)
RED = (176, 42, 28)
SEA = (38, 84, 110)
SKY = (214, 228, 232)
STEEL = (58, 64, 70)
TAG_COLORS = {
    "CONFIRMED": (31, 92, 46),
    "OFFICIAL": (31, 58, 92),
    "REPORTED": (138, 90, 0),
    "FORECAST": (91, 74, 138),
}
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUTPUT_PATH", "/output/entry.png")


def font(name, size):
    return ImageFont.truetype(os.path.join(BASE, "fonts", name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit width."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for w in words[1:]:
            if draw.textlength(cur + " " + w, font=fnt) <= width:
                cur += " " + w
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, width, max_lines):
    """Wrap text and keep at most max_lines, ending with an ellipsis
    on a word boundary when truncated."""
    lines = wrap(draw, text, fnt, width)
    if len(lines) <= max_lines:
        return lines
    out = lines[:max_lines]
    last = out[-1]
    while last and draw.textlength(last + "...", font=fnt) > width:
        last = last.rsplit(" ", 1)[0] if " " in last else ""
    out[-1] = (last + "...") if last else "..."
    return out


def tag_chip(draw, x, y, tag):
    """Draw a verification tag chip; returns its width."""
    fnt = SANS_B(8)
    color = TAG_COLORS.get(tag, (60, 60, 60))
    w = int(draw.textlength(tag, font=fnt)) + 12
    h = 14
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=color)
    draw.text((x + 6, y + 3), tag, font=fnt, fill=(255, 255, 255))
    return w


def art_ship(draw, x, y, w, h, kind):
    """Small flat illustration drawn on its own layer, so nothing can
    escape the picture box. kind: 'tanker', 'market', 'port'."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle([0, 0, w, h], fill=SKY + (255,))
    d.rectangle([0, int(h * 0.62), w, h], fill=SEA + (255,))
    if kind == "tanker":
        # two tankers with container stacks, waves below
        for sx, sw, sh in ((int(w * 0.08), int(w * 0.38), int(h * 0.22)),
                           (int(w * 0.54), int(w * 0.36), int(h * 0.18))):
            by = int(h * 0.62) - sh
            d.rectangle([sx, by, sx + sw, int(h * 0.62)], fill=STEEL + (255,))
            d.rectangle([sx + 6, by - int(h * 0.10), sx + int(sw * 0.45),
                         by], fill=RED + (255,))
            d.rectangle([sx + int(sw * 0.5), by - int(h * 0.07),
                         sx + sw - 6, by], fill=(214, 214, 200, 255))
        for wy in (int(h * 0.70), int(h * 0.80), int(h * 0.90)):
            for wx in range(6, w - 20, 34):
                d.arc([wx, wy, wx + 26, wy + 10], 0, 180,
                      fill=(255, 255, 255, 255), width=2)
    elif kind == "market":
        # falling chart bars
        base = int(h * 0.78)
        vals = [0.62, 0.50, 0.55, 0.34, 0.40, 0.22]
        bw = w // (len(vals) + 1)
        for i, v in enumerate(vals):
            bx = 10 + i * bw
            bh = int(h * v)
            d.rectangle([bx, base - bh, bx + bw - 8, base],
                        fill=RED + (255,))
        d.line([8, base - int(h * 0.66), w - 8, base - int(h * 0.16)],
               fill=INK + (255,), width=3)
    else:  # port
        # cranes and containers at a port
        for cx in (int(w * 0.18), int(w * 0.55)):
            d.rectangle([cx, int(h * 0.18), cx + 5, int(h * 0.62)],
                        fill=STEEL + (255,))
            d.rectangle([cx - 12, int(h * 0.18), cx + int(w * 0.34),
                         int(h * 0.18) + 5], fill=STEEL + (255,))
            d.line([cx + 2, int(h * 0.18) + 5, cx + int(w * 0.22),
                    int(h * 0.34)], fill=STEEL + (255,), width=2)
        for i, col in enumerate((RED, (214, 160, 40), SEA)):
            d.rectangle([12 + i * 34, int(h * 0.48), 12 + i * 34 + 28,
                         int(h * 0.62)], fill=col + (255,))
    return layer


def card_frame(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], outline=RULE, width=1, fill=PAPER)


def draw_story_card(draw, x, y, w, h, story, art=None, title_size=15,
                    body_size=10, body_lines=3):
    """A story card: optional picture box, title, body, tag chip and
    source. Body is fitted so it can never touch the chip."""
    card_frame(draw, x, y, w, h)
    pad = 10
    cy = y + pad
    if art is not None:
        ah = 64 if h >= 200 else 56
        pic = art_ship(draw, 0, 0, w - 2 * pad, ah, art)
        # paste the art layer inside the card, fully clipped
        img.paste(pic, (x + pad, cy), pic)
        draw.rectangle([x + pad, cy, x + w - pad, cy + ah], outline=RULE,
                       width=1)
        cy += ah + 8
    # region eyebrow
    draw.text((x + pad, cy), story["region"].upper(), font=SANS_B(8),
              fill=RED)
    cy += 12
    title_lines = fit_lines(draw, story["title"], SERIF_B(title_size),
                            w - 2 * pad, 3 if h >= 200 else 2)
    for ln in title_lines:
        draw.text((x + pad, cy), ln, font=SERIF_B(title_size), fill=INK)
        cy += title_size + 4
    cy += 2
    # body area ends above the chip row
    chip_y = y + h - 20
    avail = chip_y - cy - 4
    line_h = body_size + 3
    max_body = max(1, avail // line_h)
    body = fit_lines(draw, story["text"], SANS(body_size), w - 2 * pad,
                     min(body_lines, max_body))
    for ln in body:
        draw.text((x + pad, cy), ln, font=SANS(body_size), fill=INK)
        cy += line_h
    tag_chip(draw, x + pad, chip_y, story["tag"])
    src = story["source"]
    sw = draw.textlength(src, font=SANS(8))
    draw.text((x + w - pad - sw, chip_y + 2), src, font=SANS(8),
              fill=MUTED)


def main():
    global img
    with open(os.path.join(BASE, "stories.json"), encoding="utf-8") as f:
        data = json.load(f)
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    M = 30
    CW = W - 2 * M
    y = 20

    # ---- masthead ----
    mast = "THE WORLD IN ONE DAY"
    mf = SERIF_B(56)
    mw = draw.textlength(mast, font=mf)
    draw.text(((W - mw) / 2, y), mast, font=mf, fill=INK)
    y += 62
    dl = data["dateline"]
    df = SANS_B(13)
    dw = draw.textlength(dl, font=df)
    draw.text(((W - dw) / 2, y), dl, font=df, fill=RED)
    y += 20
    draw.line([M, y, W - M, y], fill=RULE, width=2)
    y += 6
    draw.line([M, y, W - M, y], fill=RULE, width=1)
    y += 8
    sub = data["subtitle"]
    sf = SANS(11)
    sw = draw.textlength(sub, font=sf)
    draw.text(((W - sw) / 2, y), sub, font=sf, fill=MUTED)
    y += 20

    # ---- THE DAY IN UTC ----
    utc_h = 84
    draw.rectangle([M, y, W - M, y + utc_h], fill=INK)
    draw.text((M + 12, y + 8), "THE DAY IN UTC", font=SANS_B(10),
              fill=(255, 255, 255))
    draw.line([M + 12, y + 26, W - M - 12, y + 26],
              fill=(120, 120, 120), width=1)
    evs = data["utc"]
    col_w = (CW - 24) // 2
    for i, ev in enumerate(evs):
        cx = M + 12 + (i % 2) * col_w
        cy = y + 30 + (i // 2) * 14
        if i // 2 > 3:
            continue
        draw.text((cx, cy), ev["time"], font=SANS_B(9),
                  fill=(255, 200, 90))
        txt = ev["text"]
        maxw = col_w - 52
        while draw.textlength(txt, font=SANS(9)) > maxw and len(txt) > 4:
            txt = txt.rsplit(" ", 1)[0] + "..."
        draw.text((cx + 48, cy), txt, font=SANS(9), fill=(255, 255, 255))
    y += utc_h + 8

    # ---- THE DAY IN NUMBERS ----
    num_h = 58
    draw.rectangle([M, y, W - M, y + num_h], outline=RULE, width=1,
                   fill=PAPER)
    draw.text((M + 12, y + 7), "THE DAY IN NUMBERS", font=SANS_B(10),
              fill=RED)
    nums = data["numbers"]
    seg = (CW - 24) / len(nums)
    for i, n in enumerate(nums):
        cx = M + 12 + i * seg
        vf = SERIF_B(20)
        draw.text((cx, y + 22), n["value"], font=vf, fill=INK)
        lab = n["label"]
        while draw.textlength(lab, font=SANS(7)) > seg - 8 and len(lab) > 4:
            lab = lab.rsplit(" ", 1)[0] + "..."
        draw.text((cx, y + 44), lab, font=SANS(7), fill=MUTED)
    y += num_h + 8

    # ---- lead row: lead + 2 big cards ----
    row_h = 228
    lead_w = 470
    big_w = (CW - lead_w - 20) // 2
    draw_story_card(draw, M, y, lead_w, row_h, data["lead"], art="tanker",
                    title_size=19, body_size=10, body_lines=3)
    draw_story_card(draw, M + lead_w + 10, y, big_w, row_h, data["big"][0],
                    art="market", title_size=14, body_size=9, body_lines=3)
    draw_story_card(draw, M + lead_w + 10 + big_w + 10, y, big_w, row_h,
                    data["big"][1], art="port", title_size=14, body_size=9,
                    body_lines=3)
    y += row_h + 10

    # ---- small cards: 5 + 5 ----
    small = data["small"]
    sw_ = (CW - 4 * 10) // 5
    sh_ = 126
    for r in range(2):
        for c in range(5):
            s = small[r * 5 + c]
            draw_story_card(draw, M + c * (sw_ + 10), y, sw_, sh_, s,
                            title_size=11, body_size=9, body_lines=3)
        y += sh_ + 10

    # ---- WHERE IT HAPPENED ----
    wh_h = 30
    draw.rectangle([M, y, W - M, y + wh_h], outline=RULE, width=1,
                   fill=PAPER)
    draw.text((M + 12, y + 10), "WHERE IT HAPPENED", font=SANS_B(10),
              fill=RED)
    parts = []
    for region, n in data["regions"].items():
        parts.append("%s %d" % (region.upper(), n))
    line = "  ·  ".join(parts)
    lf = SANS(10)
    lx = M + 12 + draw.textlength("WHERE IT HAPPENED  ", font=SANS_B(10))
    maxw = W - M - 12 - lx
    while draw.textlength(line, font=lf) > maxw and len(line) > 4:
        line = line.rsplit(" ", 1)[0] + "..."
    draw.text((lx, y + 10), line, font=lf, fill=INK)
    y += wh_h + 8

    # ---- ALSO ON ----
    also = data["also"]
    draw.text((M, y), "ALSO ON", font=SANS_B(10), fill=RED)
    y += 15
    ncols = 3
    col_w = (CW - (ncols - 1) * 16) // ncols
    per_col = (len(also) + ncols - 1) // ncols
    for i, s in enumerate(also):
        cx = M + (i // per_col) * (col_w + 16)
        cy = y + (i % per_col) * 12
        item = "• " + s["title"] + " — " + s["source"]
        while draw.textlength(item, font=SANS(8)) > col_w and len(item) > 4:
            item = item.rsplit(" ", 1)[0] + "..."
        draw.text((cx, cy), item, font=SANS(8), fill=INK)
    y += per_col * 12 + 6

    # ---- DATE CHECK + footer ----
    dc_h = 30
    draw.rectangle([M, y, W - M, y + dc_h], outline=RULE, width=1,
                   fill=PAPER)
    dc = ("DATE CHECK — Every story is verified against its named source. "
          "Cut-off 09:00 UTC, 25 Nov 2026. Partial day; the final edition "
          "corrects all figures.")
    draw.text((M + 10, y + 8), dc, font=SANS(9), fill=INK)
    y += dc_h + 6
    foot = "Built by an AI agent for make.fun — Sum up 25 November's world news in one image"
    ff = SANS(8)
    fw = draw.textlength(foot, font=ff)
    draw.text(((W - fw) / 2, y), foot, font=ff, fill=MUTED)

    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    img.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
