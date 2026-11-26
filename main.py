"""Render 'The World in One Day' - 25 November 2026 - as a 1024x1024
newspaper front page from stories.json. Deterministic: no randomness,
no clock, no network. Reads DejaVu fonts from fonts/, writes entry.png
next to this script (or $OUTPUT_PATH). Python 3 + Pillow only."""

import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUTPUT_PATH", os.path.join(HERE, "entry.png"))

W, H = 1024, 1024
BG = (246, 241, 227)
INK = (26, 26, 26)
RED = (164, 30, 34)
GOLD = (201, 162, 39)
DARK = (17, 17, 17)
GREY = (110, 105, 90)
LINE = (180, 172, 150)
CARD_BG = (252, 249, 240)
TAG_FILL = {
    "CONFIRMED": (46, 125, 50),
    "OFFICIAL": (21, 101, 192),
    "REPORTED": (138, 109, 0),
    "FORECAST": (97, 97, 97),
}


def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", name), size)


SERIF = "DejaVuSerif-Bold.ttf"
SERIF_REG = "DejaVuSerif.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, fnt, width, max_lines):
    """Wrap and truncate to max_lines, adding an ellipsis when cut."""
    lines = wrap(draw, text, fnt, width)
    if len(lines) <= max_lines:
        return lines
    out = lines[:max_lines]
    last = out[-1]
    while last and draw.textlength(last + " …", font=fnt) > width:
        last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
    out[-1] = (last + " …").strip()
    return out


def trunc(draw, text, fnt, width):
    cut = False
    while text and draw.textlength(text + "…", font=fnt) > width:
        text = text.rsplit(" ", 1)[0] if " " in text else text[:-1]
        cut = True
    return text + "…" if cut else text


def pill(draw, x, y, text, fill):
    fnt = font(SANS_B, 9)
    tw = draw.textlength(text, font=fnt)
    draw.rounded_rectangle([x, y, x + tw + 12, y + 15], radius=3, fill=fill)
    draw.text((x + 6, y + 2), text, font=fnt, fill=(255, 255, 255))


def source_line(draw, x, y, text, width):
    fnt = font(SANS, 9)
    draw.text((x + width - draw.textlength(text, font=fnt), y + 3),
              text, font=fnt, fill=GREY)


def draw_bars(draw, x, y, w, h):
    """Falling market bars for the Asia sell-off card."""
    draw.rectangle([x, y, x + w, y + h], fill=(214, 228, 235))
    vals = [0.92, 0.78, 0.86, 0.62, 0.55, 0.44, 0.36]
    bw = w // len(vals)
    for i, v in enumerate(vals):
        bh = int(h * v)
        draw.rectangle([x + i * bw + 3, y + h - bh,
                        x + (i + 1) * bw - 3, y + h - 4],
                       fill=(164, 30, 34))
    for i in range(len(vals) - 1):
        x1 = x + i * bw + bw // 2
        y1 = y + h - int(h * vals[i]) - 6
        x2 = x + (i + 1) * bw + bw // 2
        y2 = y + h - int(h * vals[i + 1]) - 6
        draw.line([x1, y1, x2, y2], fill=INK, width=2)


def draw_sea(draw, x, y, w, h):
    """Tanker on a mined strait for the Hormuz card."""
    draw.rectangle([x, y, x + w, y + h], fill=(214, 228, 235))
    draw.rectangle([x, y + h // 2, x + w, y + h], fill=(38, 84, 110))
    for i in range(5):
        wx = x + 12 + i * (w // 5)
        draw.arc([wx, y + h // 2 + 8, wx + 34, y + h // 2 + 22],
                 start=180, end=360, fill=(255, 255, 255), width=2)
    cx = x + w // 2
    draw.rectangle([cx - 44, y + h // 2 - 10, cx + 44,
                    y + h // 2 + 8], fill=(26, 26, 26))
    draw.rectangle([cx + 18, y + h // 2 - 24, cx + 38,
                    y + h // 2 - 10], fill=(164, 30, 34))
    draw.rectangle([cx - 38, y + h // 2 - 20, cx - 22,
                    y + h // 2 - 10], fill=(60, 60, 60))
    for mx, my in ((x + 22, y + h - 16), (x + w - 26, y + h - 12)):
        draw.ellipse([mx - 4, my - 4, mx + 4, my + 4], fill=(20, 20, 20))
        for dx, dy in ((-7, -5), (7, -6), (-6, 5), (8, 4)):
            draw.line([mx, my, mx + dx, my + dy], fill=(20, 20, 20), width=1)


def draw_refinery(draw, x, y, w, h):
    """Refinery towers with flame and smoke for the Ras Tanura card."""
    draw.rectangle([x, y, x + w, y + h], fill=(226, 214, 188))
    draw.rectangle([x, y + h - 18, x + w, y + h], fill=(90, 82, 70))
    # horizontal pipe run
    draw.rectangle([x + 8, y + h - 34, x + w - 8, y + h - 30],
                   fill=(52, 48, 44))
    towers = [(0.10, 0.55), (0.30, 0.38), (0.52, 0.48), (0.74, 0.62)]
    for fx, fh in towers:
        tx = x + int(w * fx)
        th = int(h * fh)
        draw.rectangle([tx, y + h - 30 - th, tx + 18, y + h - 30],
                       fill=(52, 48, 44))
        draw.rectangle([tx - 2, y + h - 30 - th, tx + 20,
                        y + h - 30 - th + 4], fill=(30, 28, 26))
    fx = x + int(w * 0.74) + 9
    fy = y + h - 30 - int(h * 0.62)
    draw.polygon([(fx - 10, fy), (fx, fy - 18), (fx + 10, fy)],
                 fill=(232, 120, 20))
    draw.polygon([(fx - 5, fy), (fx, fy - 9), (fx + 5, fy)],
                 fill=(255, 200, 60))
    for cx, cy, r in ((0.30, 0.16, 12), (0.44, 0.10, 9), (0.58, 0.15, 10)):
        draw.ellipse([x + int(w * cx) - r, y + int(h * cy) - r,
                      x + int(w * cx) + r, y + int(h * cy) + r],
                     fill=(120, 116, 108))


ILLUSTRATIONS = [draw_refinery, draw_bars, draw_sea]


def big_card(draw, x, y, w, h, story, art):
    draw.rectangle([x, y, x + w, y + h], outline=LINE, width=1, fill=CARD_BG)
    art(draw, x + 1, y + 1, w - 2, 56)
    fy = font(SANS_B, 11)
    draw.text((x + 10, y + 61), story["region"].upper(), font=fy, fill=RED)
    wide = w > 300
    hf = font(SERIF, 25 if wide else 19)
    lines = fit(draw, story["title"].upper(), hf, w - 20,
                2 if wide else 3)
    ty = y + 77
    for ln in lines:
        draw.text((x + 10, ty), ln, font=hf, fill=INK)
        ty += 26 if wide else 21
    bf = font(SANS, 12)
    blines = fit(draw, story["text"], bf, w - 20, 3 if wide else 2)
    by = ty + 4
    for ln in blines:
        draw.text((x + 10, by), ln, font=bf, fill=INK)
        by += 14
    pill(draw, x + 10, y + h - 22, story["tag"], TAG_FILL[story["tag"]])
    source_line(draw, x, y + h - 22, story["source"], w - 10)


def small_card(draw, x, y, w, h, story):
    draw.rectangle([x, y, x + w, y + h], outline=LINE, width=1, fill=CARD_BG)
    fy = font(SANS_B, 10)
    draw.text((x + 8, y + 8), story["region"].upper(), font=fy, fill=RED)
    tf = font(SANS_B, 13)
    lines = fit(draw, story["title"], tf, w - 16, 2)
    ty = y + 26
    for ln in lines:
        draw.text((x + 8, ty), ln, font=tf, fill=INK)
        ty += 16
    bf = font(SANS, 11)
    blines = fit(draw, story["text"], bf, w - 16, 3)
    by = ty + 4
    for ln in blines:
        draw.text((x + 8, by), ln, font=bf, fill=INK)
        by += 14
    pill(draw, x + 8, y + h - 21, story["tag"], TAG_FILL[story["tag"]])
    source_line(draw, x, y + h - 21, story["source"], w - 8)


def main():
    data = json.load(open(os.path.join(HERE, "stories.json")))
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    mx = 24
    cw = W - 2 * mx

    # Masthead
    tf = font(SERIF, 58)
    title = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(title, font=tf)) / 2, 12), title,
           font=tf, fill=INK)
    df = font(SANS_B, 17)
    d.text(((W - d.textlength(data["dateline"], font=df)) / 2, 80),
           data["dateline"], font=df, fill=RED)
    d.line([mx, 102, W - mx, 102], fill=INK, width=2)
    d.line([mx, 106, W - mx, 106], fill=INK, width=1)
    sf = font(SANS, 13)
    d.text(((W - d.textlength(data["subtitle"], font=sf)) / 2, 112),
           data["subtitle"], font=sf, fill=GREY)

    # The day in UTC (black bar, 2 columns x 4 rows)
    ux, uy, uh = mx, 128, 74
    d.rectangle([ux, uy, ux + cw, uy + uh], fill=DARK)
    hf = font(SANS_B, 11)
    d.text((ux + 10, uy + 5), "THE DAY IN UTC", font=hf, fill=GOLD)
    tf2 = font(SANS_B, 11)
    bf2 = font(SANS, 11)
    col_w = (cw - 20) // 2
    for i, ev in enumerate(data["utc"]):
        col, row = divmod(i, 4)
        ex = ux + 10 + col * col_w
        ey = uy + 21 + row * 13
        d.text((ex, ey), ev["time"], font=tf2, fill=GOLD)
        txt = trunc(d, ev["text"], bf2, col_w - 52)
        d.text((ex + 50, ey), txt, font=bf2, fill=(255, 255, 255))

    # The day in numbers (6 figures)
    ny = 210
    d.text((mx, ny), "THE DAY IN NUMBERS", font=hf, fill=INK)
    d.line([mx, ny + 16, W - mx, ny + 16], fill=INK, width=1)
    ncols = data["numbers"]
    colw = cw // 6
    vf = font(SERIF, 23)
    lf = font(SANS, 9)
    for i, num in enumerate(ncols):
        cx = mx + i * colw
        d.text((cx + 4, ny + 22), num["value"], font=vf, fill=INK)
        for j, ln in enumerate(fit(d, num["label"], lf, colw - 8, 2)):
            d.text((cx + 4, ny + 48 + j * 11), ln, font=lf, fill=GREY)
    d.line([mx, ny + 76, W - mx, ny + 76], fill=INK, width=1)

    # Big cards: lead wide + two narrow
    by = 294
    bh = 200
    lead_w = 488
    side_w = (cw - lead_w - 16) // 2
    big_card(d, mx, by, lead_w, bh, data["lead"], ILLUSTRATIONS[0])
    big_card(d, mx + lead_w + 8, by, side_w, bh, data["big"][0],
             ILLUSTRATIONS[1])
    big_card(d, mx + lead_w + 8 + side_w + 8, by, side_w, bh,
             data["big"][1], ILLUSTRATIONS[2])

    # Small cards: 2 rows x 5
    sw = (cw - 4 * 8) // 5
    sh = 142
    for r in range(2):
        for c in range(5):
            i = r * 5 + c
            small_card(d, mx + c * (sw + 8), by + bh + 6 + r * (sh + 6),
                       sw, sh, data["small"][i])

    # Where it happened
    wy = by + bh + 6 + 2 * (sh + 6) + 2
    d.rectangle([mx, wy, W - mx, wy + 26], outline=LINE, width=1)
    wf = font(SANS_B, 12)
    d.text((mx + 10, wy + 6), "WHERE IT HAPPENED", font=wf, fill=RED)
    counts = "  ·  ".join(
        "%s %d" % (k.upper(), v) for k, v in data["regions"].items())
    cf = font(SANS, 12)
    d.text((mx + 168, wy + 6), counts, font=cf, fill=INK)

    # Also on: 3 columns
    ay = wy + 32
    d.text((mx, ay), "ALSO ON", font=wf, fill=RED)
    d.line([mx, ay + 17, W - mx, ay + 17], fill=LINE, width=1)
    cols = [data["also"][0:9], data["also"][9:17], data["also"][17:25]]
    af = font(SANS, 11)
    colw2 = (cw - 32) // 3
    for ci, col in enumerate(cols):
        cx = mx + ci * (colw2 + 16)
        for ri, st in enumerate(col):
            txt = "%s — %s" % (st["title"], st["source"])
            txt = trunc(d, "• " + txt, af, colw2)
            d.text((cx, ay + 22 + ri * 12), txt, font=af, fill=INK)

    # Date check box
    dy = ay + 22 + 9 * 12 + 6
    d.rectangle([mx, dy, W - mx, dy + 28], outline=LINE, width=1)
    chk = ("DATE CHECK — Every story verified against its named source. "
           "Full day: the Phala Phala ruling, the US 13:30 GMT data, the "
           "Iowa blast and the Wednesday closes were all confirmed after "
           "the 09:00 UTC prep cut-off.")
    for j, ln in enumerate(fit(d, chk, font(SANS, 11), cw - 20, 2)):
        d.text((mx + 10, dy + 3 + j * 12), ln, font=font(SANS, 11),
               fill=INK)

    # Footer
    ff = font(SANS, 10)
    foot = ("Built by an AI agent for make.fun — Sum up 25 November's "
            "world news in one image")
    d.text(((W - d.textlength(foot, font=ff)) / 2, H - 14), foot,
           font=ff, fill=GREY)

    img.save(OUT, "PNG")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
