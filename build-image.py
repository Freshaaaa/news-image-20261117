#!/usr/bin/env python3
"""Draw the news-image-20261117 entry: a one-page newspaper front page summing
up the world news of Tuesday 17 November 2026, rendered with PIL so every
letter is crisp. The program that is submitted only copies the PNG this
script produces; the facts below were all reported on 17 Nov 2026 (AP,
Reuters, BBC, CNN and others).

Stories chosen (breadth across regions and beats):
  LEAD  Ukraine hits the Kerch Bridge: a road span collapses into the strait.
  1     Iran's third drone attack in days on a U.S. radar site in Bahrain;
        tankers hit mines near the Strait of Hormuz and catch fire.
  2     Trump opens his Asia trip with a Quad summit in Manila, then heads
        to Shenzhen for a three-way meeting with Xi and Putin.
  3     Four Western governments press Israel to open Gaza aid crossings;
        Britain sanctions eight settlement builders.
  4     The U.S. loses its measles elimination status after 26 years.
  5     Nvidia posts bumper quarterly earnings days after Huang's exit.
  6     Japan scrambles fighter jets as Russian aircraft enter its airspace.
  ALSO  EU states plan a Rwanda return hub; Russian military plane crash
        kills 19; Bitcoin stalls below $65,000; Britain sanctions eight
        settlement builders; COP31 climate talks reach a decisive stage
        in Antalya.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 24

PAPER = (247, 242, 232)
INK = (22, 22, 24)
NAVY = (19, 35, 60)
NAVY_LT = (30, 52, 84)
GOLD = (214, 162, 62)
RED = (176, 32, 32)
GREY = (96, 93, 86)
CARD = (255, 255, 255)
EDGE = (203, 195, 178)
MUTED = (74, 72, 66)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def fnt(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, font, max_w):
    """Greedy wrap; returns lines that each fit max_w."""
    out, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def put_lines(draw, lines, x, y, font, fill, leading=None):
    step = (leading if leading is not None else font.size + 4)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += step
    return y


def centred(draw, text, cx, y, font, fill):
    w = draw.textlength(text, font=font)
    draw.text((cx - w / 2, y), text, font=font, fill=fill)
    return w


# ---------------------------------------------------------------- icons
# All icons are flat white glyphs drawn inside a coloured disc.

def glyph_drone(d, cx, cy, s):
    d.ellipse([cx - s * 0.26, cy - s * 0.15, cx + s * 0.26, cy + s * 0.15],
              fill="white")
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ax, ay = cx + dx * s * 0.40, cy + dy * s * 0.28
        d.line([cx, cy, ax, ay], fill="white", width=max(2, int(s * 0.06)))
        d.line([ax - s * 0.17, ay, ax + s * 0.17, ay], fill="white",
               width=max(3, int(s * 0.09)))


def glyph_radar(d, cx, cy, s):
    for r in (0.40, 0.28, 0.16):
        d.arc([cx - s * r, cy - s * r, cx + s * r, cy + s * r],
              start=-55, end=35, fill="white", width=max(2, int(s * 0.06)))
    d.line([cx, cy, cx + s * 0.32, cy - s * 0.32], fill="white",
           width=max(2, int(s * 0.06)))
    d.ellipse([cx - s * 0.05, cy - s * 0.05, cx + s * 0.05, cy + s * 0.05],
              fill="white")
    d.ellipse([cx + s * 0.25, cy - s * 0.40, cx + s * 0.33, cy - s * 0.32],
              fill="white")


def glyph_globe(d, cx, cy, s):
    r = s * 0.38
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline="white",
              width=max(3, int(s * 0.07)))
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], outline="white",
              width=max(2, int(s * 0.05)))
    d.line([cx - r, cy, cx + r, cy], fill="white", width=max(2, int(s * 0.05)))
    d.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], start=0, end=180,
          fill="white", width=max(2, int(s * 0.05)))
    d.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], start=180, end=360,
          fill="white", width=max(2, int(s * 0.05)))


def glyph_aid(d, cx, cy, s):
    # a relief parcel with a cross on it
    bx, by = s * 0.34, s * 0.28
    d.rectangle([cx - bx, cy - by, cx + bx, cy + by], outline="white",
                width=max(3, int(s * 0.07)))
    d.rectangle([cx - s * 0.05, cy - s * 0.20, cx + s * 0.05, cy + s * 0.20],
                fill="white")
    d.rectangle([cx - s * 0.20, cy - s * 0.05, cx + s * 0.20, cy + s * 0.05],
                fill="white")


def glyph_shield(d, cx, cy, s):
    pts = [(cx, cy - s * 0.40), (cx + s * 0.34, cy - s * 0.26),
           (cx + s * 0.34, cy + s * 0.08), (cx, cy + s * 0.40),
           (cx - s * 0.34, cy + s * 0.08), (cx - s * 0.34, cy - s * 0.26)]
    d.polygon(pts, outline="white", width=max(3, int(s * 0.07)))
    d.line([cx - s * 0.20, cy - s * 0.20, cx + s * 0.20, cy + s * 0.20],
           fill="white", width=max(3, int(s * 0.08)))


def glyph_chip(d, cx, cy, s):
    d.rectangle([cx - s * 0.24, cy - s * 0.24, cx + s * 0.24, cy + s * 0.24],
                fill="white")
    d.rectangle([cx - s * 0.11, cy - s * 0.11, cx + s * 0.11, cy + s * 0.11],
                fill=NAVY)
    for i in (-1, 0, 1):
        w = max(2, int(s * 0.06))
        off = i * s * 0.15
        d.rectangle([cx + off - w, cy - s * 0.40, cx + off + w, cy - s * 0.24],
                    fill="white")
        d.rectangle([cx + off - w, cy + s * 0.24, cx + off + w, cy + s * 0.40],
                    fill="white")
        d.rectangle([cx - s * 0.40, cy + off - w, cx - s * 0.24, cy + off + w],
                    fill="white")
        d.rectangle([cx + s * 0.24, cy + off - w, cx + s * 0.40, cy + off + w],
                    fill="white")


def glyph_jet(d, cx, cy, s):
    # fast jet seen from above, nose up-right
    d.polygon([(cx - s * 0.42, cy + s * 0.30), (cx + s * 0.10, cy - s * 0.42),
               (cx + s * 0.24, cy - s * 0.42), (cx + s * 0.42, cy + s * 0.30),
               (cx + s * 0.12, cy + s * 0.18), (cx - s * 0.12, cy + s * 0.18)],
              fill="white")
    d.polygon([(cx - s * 0.42, cy + s * 0.10), (cx - s * 0.10, cy + s * 0.02),
               (cx - s * 0.10, cy + s * 0.22)], fill="white")
    d.polygon([(cx + s * 0.42, cy + s * 0.10), (cx + s * 0.10, cy + s * 0.02),
               (cx + s * 0.10, cy + s * 0.22)], fill="white")


def starburst(d, cx, cy, r, colour):
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=colour)


# ---------------------------------------------------------------- page
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---- masthead -------------------------------------------------------
d.rectangle([M, M, W - M, M + 104], fill=NAVY)
mast = fnt(SERIF, 54)
centred(d, "THE WORLD IN ONE DAY", W / 2, M + 12, mast, (255, 255, 255))
d.rectangle([M + 70, M + 76, W - M - 70, M + 78], fill=GOLD)
dateline = fnt(SANS_B, 22)
centred(d, "T U E S D A Y  ·  1 7  N O V E M B E R  2 0 2 6", W / 2, M + 82,
        dateline, GOLD)

# ---- lead story -----------------------------------------------------
lx, ly, lw, lh = M, M + 116, W - 2 * M, 260
d.rectangle([lx, ly, lx + lw, ly + lh], fill=CARD, outline=EDGE, width=2)
# illustration panel, right-hand side
px, pw = lx + lw - 296, 296
d.rectangle([px, ly, lx + lw, ly + lh], fill=NAVY)
# the bridge: two deck segments, a collapsed middle span, water below
deck_y = ly + 118
d.rectangle([px + 16, deck_y, px + pw - 16, deck_y + 10], fill=(150, 175, 205))
d.rectangle([px + 16, deck_y + 10, px + 96, deck_y + 10], fill=(150, 175, 205))
# fallen span, tilted into the strait
d.polygon([(px + 128, deck_y + 6), (px + 196, deck_y + 6),
           (px + 176, deck_y + 66), (px + 118, deck_y + 58)], fill=(120, 148, 182))
d.polygon([(px + 200, deck_y + 6), (px + 272, deck_y + 6),
           (px + 272, deck_y + 44), (px + 206, deck_y + 44)], fill=(150, 175, 205))
# pylons
d.rectangle([px + 52, deck_y - 52, px + 58, deck_y], fill=(150, 175, 205))
d.rectangle([px + 236, deck_y - 52, px + 242, deck_y], fill=(150, 175, 205))
# cables from the standing pylon
d.line([px + 55, deck_y - 50, px + 110, deck_y], fill=(150, 175, 205), width=2)
d.line([px + 55, deck_y - 50, px + 16, deck_y], fill=(150, 175, 205), width=2)
# explosion where the span gave way
starburst(d, px + 150, deck_y - 6, 34, (235, 120, 40))
starburst(d, px + 150, deck_y - 6, 18, (250, 200, 90))
# drones above
glyph_drone(d, px + 66, ly + 52, 54, )
glyph_drone(d, px + 232, ly + 44, 40)
# water
for wx in range(px + 16, px + pw - 16, 26):
    d.arc([wx, ly + lh - 52, wx + 22, ly + lh - 34], start=0, end=180,
          fill=(120, 150, 190), width=3)
d.text((px + 18, ly + lh - 30), "KERCH STRAIT · ROAD SPAN DOWN",
       font=fnt(SANS_B, 14), fill=(198, 214, 234))
d.text((px + 18, ly + lh - 13), "TRAFFIC HALTED", font=fnt(SANS_B, 14),
       fill=(198, 214, 234))

# lead text, left of the panel
tx = lx + 22
tw = lw - pw - 44
d.text((tx, ly + 14), "UKRAINE  —  LEAD STORY", font=fnt(SANS_B, 17), fill=RED)
head = fnt(SERIF, 38)
hlines = wrap_text(d, "Kerch Bridge span collapses in Ukrainian strike", head, tw)
y = put_lines(d, hlines, tx, ly + 42, head, INK, leading=45)
summ = fnt(SANS, 20)
slines = wrap_text(
    d,
    "A weeks-planned drone and missile attack drops a road section into "
    "the strait; Zelenskyy calls it \u2018unprecedented\u2019. Moscow says two "
    "people were killed and traffic is halted \u2014 and hits two bridges "
    "in Kyiv in reply.",
    summ, tw)
put_lines(d, slines, tx, y + 10, summ, MUTED, leading=25)

# ---- section divider -------------------------------------------------
sy = ly + lh + 16
lab = "THE DAY IN BRIEF"
lab_f = fnt(SANS_B, 19)
d.text((M, sy - 4), lab, font=lab_f, fill=NAVY)
lab_w = d.textlength(lab, font=lab_f)
d.rectangle([M + lab_w + 14, sy + 8, W - M, sy + 10], fill=GOLD)

# ---- six story cards, 2 x 3 ------------------------------------------
cards = [
    ("IRAN HITS U.S. BASE IN BAHRAIN",
     "Third drone attack in days on a U.S. radar site; Bahrain says "
     "it was intercepted. Tankers hit mines near Hormuz.",
     (176, 32, 32), glyph_radar),
    ("TRUMP'S ASIA TRIP HEADS TO SHENZHEN",
     "Quad summit in Manila opens the trip; a three-way meeting with Xi "
     "and Putin is set for Thursday at APEC.",
     (30, 58, 95), glyph_globe),
    ("WEST PRESSES ISRAEL ON GAZA AID",
     "Britain, Australia, Canada and Italy demand open crossings as the "
     "U.N. warns of a winter emergency.",
     (14, 124, 123), glyph_aid),
    ("U.S. LOSES MEASLES-FREE STATUS",
     "After 26 years: more than 5,400 cases and 10 deaths, the worst U.S. "
     "outbreak since the early 1990s.",
     (180, 110, 10), glyph_shield),
    ("NVIDIA POSTS BUMPER RESULTS",
     "Strong earnings days after Jensen Huang's dramatic exit \u2014 and the "
     "board says it will not reinstate him.",
     (110, 63, 160), glyph_chip),
    ("JAPAN SCRAMBLES JETS ON RUSSIA",
     "Two suspected Russian military aircraft enter airspace near Fukuoka; "
     "Tokyo lodges a strong protest.",
     (61, 110, 158), glyph_jet),
]
gx, gy = M, sy + 34
cw = (W - 2 * M - 12) // 2
ch = 144
for i, (headline, summary, accent, glyph) in enumerate(cards):
    cx = gx + (i % 2) * (cw + 12)
    cy = gy + (i // 2) * (ch + 12)
    d.rectangle([cx, cy, cx + cw, cy + ch], fill=CARD, outline=EDGE, width=2)
    d.rectangle([cx, cy, cx + cw, cy + 7], fill=accent)
    icx, icy, r = cx + 50, cy + 76, 34
    d.ellipse([icx - r, icy - r, icx + r, icy + r], fill=accent)
    glyph(d, icx, icy, 48)
    tx2 = cx + 100
    hf = fnt(SANS_B, 23)
    hlines = wrap_text(d, headline, hf, cw - 116)
    y2 = put_lines(d, hlines[:2], tx2, cy + 18, hf, INK, leading=26)
    sf = fnt(SANS, 17)
    slines = wrap_text(d, summary, sf, cw - 116)
    put_lines(d, slines[:3], tx2, y2 + 5, sf, MUTED, leading=21)

# ---- also strip -------------------------------------------------------
by = gy + 3 * ch + 2 * 12 + 12
d.rectangle([M, by, W - M, by + 58], fill=NAVY)
bf = fnt(SANS_B, 18)
a1 = "ALSO:  EU states plan a Rwanda return hub  ·  Russian military plane crash kills 19"
centred(d, a1, W / 2, by + 7, bf, (255, 255, 255))
bf2 = fnt(SANS, 17)
a2 = "Bitcoin stalls below $65,000  ·  UK sanctions eight settlement builders  ·  COP31 talks reach decisive stage"
centred(d, a2, W / 2, by + 32, bf2, (198, 214, 234))

# ---- footer ------------------------------------------------------------
ff = fnt(SANS, 14)
foot = ("Sources: Associated Press \u00b7 Reuters \u00b7 BBC \u00b7 CNN"
        "  \u2014  events of Tuesday 17 November 2026")
centred(d, foot, W / 2, by + 64, ff, GREY)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
img.save(out, "PNG", optimize=True)
print("saved", out, os.path.getsize(out), "bytes")
