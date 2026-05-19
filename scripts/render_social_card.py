from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math
import random

SIZE = 1200
OUT = Path("assets")
OUT.mkdir(exist_ok=True)

BG0 = (7, 17, 31)
BG1 = (23, 37, 84)
BG2 = (66, 32, 107)
WHITE = (255, 255, 255)
MUTED = (219, 234, 254)
CYAN = (104, 225, 253)
VIOLET = (167, 139, 250)
MINT = (143, 255, 205)
WARM = (255, 184, 108)
INK = (5, 10, 31)
PANEL = (9, 15, 42)


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if mono:
        candidates += [
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/Supplemental/Courier New.ttf",
        ]
    if bold:
        candidates += [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    candidates += [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def gradient_bg() -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE), BG0)
    px = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            tx = x / SIZE
            ty = y / SIZE
            t = min(1, max(0, (tx * 0.62 + ty * 0.72)))
            mid = tuple(lerp(BG0[i], BG1[i], min(1, t * 1.35)) for i in range(3))
            if t > 0.56:
                u = (t - 0.56) / 0.44
                mid = tuple(lerp(mid[i], BG2[i], u * 0.75) for i in range(3))
            px[x, y] = mid
    return img


def add_radial_glow(base: Image.Image, center: tuple[int, int], radius: int, color: tuple[int, int, int], alpha: int) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    cx, cy = center
    for r in range(radius, 0, -8):
        a = int(alpha * (1 - r / radius) ** 1.6)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*color, a))
    base.alpha_composite(overlay)


def rounded(d: ImageDraw.ImageDraw, box, radius, fill, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text(d: ImageDraw.ImageDraw, xy, s, size, fill=WHITE, bold=False, mono=False, anchor=None):
    d.text(xy, s, font=font(size, bold=bold, mono=mono), fill=fill, anchor=anchor)


def draw_glass_card(base: Image.Image, box, radius=34, fill=(9, 15, 42, 168), outline=(255, 255, 255, 38), shadow=True):
    if shadow:
        shadow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow_layer)
        sx1, sy1, sx2, sy2 = box
        sd.rounded_rectangle((sx1, sy1 + 24, sx2, sy2 + 24), radius=radius, fill=(0, 8, 32, 92))
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(24))
        base.alpha_composite(shadow_layer)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)
    x1, y1, x2, _ = box
    d.line((x1 + radius, y1 + 1, x2 - radius, y1 + 1), fill=(255, 255, 255, 46), width=2)
    base.alpha_composite(layer)


def draw_blob(base: Image.Image) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    points = [
        (640, 118), (923, 226), (1044, 456), (982, 735),
        (780, 932), (536, 870), (476, 620), (468, 332),
    ]
    d.polygon(points, fill=(255, 255, 255, 24), outline=(255, 255, 255, 32))
    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    base.alpha_composite(layer)


def draw_dotted_grid(base: Image.Image) -> None:
    d = ImageDraw.Draw(base)
    random.seed(9)
    for row in range(11):
        for col in range(11):
            x = 52 + col * 110
            y = 52 + row * 110
            r = 2.4 if (row + col) % 3 == 0 else 1.3
            a = 42 if (row + col) % 3 == 0 else 26
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, a))


def draw_dashboard(base: Image.Image, x: int, y: int, rotate: float = -4) -> None:
    card = Image.new("RGBA", (470, 360), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, 470, 360), radius=32, fill=(9, 15, 42, 198), outline=(255, 255, 255, 42), width=2)
    d.rounded_rectangle((28, 28, 156, 54), radius=13, fill=(*CYAN, 218))
    d.ellipse((386, 32, 406, 52), fill=(*WARM, 230))
    d.ellipse((420, 32, 440, 52), fill=(*CYAN, 230))
    text(d, (32, 98), "preflight.overview", 22, fill=(219, 234, 254), mono=True)
    bars = [0.35, 0.72, 0.48, 0.88, 0.58, 0.78]
    for i, h in enumerate(bars):
        bx = 42 + i * 42
        bh = int(98 * h)
        bar_color = CYAN if i % 2 else VIOLET
        d.rounded_rectangle((bx, 162 - bh, bx + 22, 162), radius=11, fill=(*bar_color, 165))
    pts = []
    for i in range(7):
        px = 52 + i * 55
        py = 245 - math.sin(i * 1.3) * 36 - i * 10
        pts.append((px, py))
    d.line(pts, fill=CYAN, width=7, joint="curve")
    d.line(pts, fill=(255, 255, 255, 100), width=2)
    d.rounded_rectangle((34, 282, 410, 330), radius=16, fill=(255, 255, 255, 20))
    text(d, (56, 313), "manual_review", 21, fill=WHITE, bold=True)
    text(d, (285, 313), "no tool call", 21, fill=CYAN, bold=True)
    card = card.rotate(rotate, resample=Image.Resampling.BICUBIC, expand=True)
    base.alpha_composite(card, (x, y))


def draw_code_card(base: Image.Image, x: int, y: int, rotate: float = 5) -> None:
    card = Image.new("RGBA", (500, 332), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, 500, 332), radius=30, fill=(5, 10, 31, 210), outline=(255, 255, 255, 38), width=2)
    d.rounded_rectangle((0, 0, 500, 62), radius=30, fill=(255, 255, 255, 20))
    for i, c in enumerate([(255, 123, 123), (255, 209, 102), (124, 247, 199)]):
        d.ellipse((36 + i * 28, 24, 52 + i * 28, 40), fill=c)
    lines = [
        "intent = ActionIntent(...) ",
        "decision = policy.classify(intent)",
        "reservation = ledger.reserve(intent)",
        "execute only if side_effect_allowed",
    ]
    for i, line in enumerate(lines):
        text(d, (36, 112 + i * 43), line, 21, fill=CYAN if i in (1, 3) else (224, 231, 255), mono=True)
    d.rounded_rectangle((36, 266, 206, 296), radius=15, fill=(*WARM, 205))
    d.rounded_rectangle((232, 266, 382, 296), radius=15, fill=(*VIOLET, 190))
    card = card.rotate(rotate, resample=Image.Resampling.BICUBIC, expand=True)
    base.alpha_composite(card, (x, y))


def draw_orbit(base: Image.Image, cx: int, cy: int) -> None:
    d = ImageDraw.Draw(base)
    d.ellipse((cx - 148, cy - 148, cx + 148, cy + 148), outline=(255, 255, 255, 40), width=2)
    d.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), fill=(255, 255, 255, 20), outline=(*CYAN, 130), width=2)
    text(d, (cx, cy + 9), "GATE", 28, fill=WHITE, bold=True, anchor="mm")
    labels = [("Intent", -210, -80, CYAN), ("Policy", 104, -128, VIOLET), ("Reserve", -142, 126, MINT), ("Audit", 124, 102, WARM)]
    for label, dx, dy, color in labels:
        x = cx + dx
        y = cy + dy
        d.line((cx, cy, x + 58, y + 42), fill=(*color, 90), width=3)
        d.rounded_rectangle((x, y, x + 116, y + 84), radius=24, fill=(255, 255, 255, 28), outline=(255, 255, 255, 48), width=1)
        d.ellipse((x + 45, y + 15, x + 71, y + 41), fill=(*color, 220))
        text(d, (x + 58, y + 63), label, 19, fill=WHITE, bold=True, anchor="mm")


def draw_stat_pills(base: Image.Image) -> None:
    d = ImageDraw.Draw(base)
    stats = [("Typed Intent", CYAN), ("Pure Policy", VIOLET), ("Audit Trace", MINT)]
    for i, (label, color) in enumerate(stats):
        x = 74 + i * 154
        d.rounded_rectangle((x, 895, x + 138, 941), radius=23, fill=(9, 15, 42, 156), outline=(255, 255, 255, 46), width=1)
        text(d, (x + 69, 924), label, 17, fill=color if i == 1 else WHITE, bold=True, anchor="mm")


def draw_title(base: Image.Image) -> None:
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((74, 68, 292, 116), radius=24, fill=(9, 15, 42, 150), outline=(255, 255, 255, 56), width=1)
    d.ellipse((94, 86, 114, 106), fill=CYAN)
    text(d, (132, 88), "Dambert Lab", 22, fill=WHITE, bold=True)
    text(d, (74, 178), "Agentic AI Architecture", 28, fill=CYAN, bold=False)
    text(d, (74, 286), "Your agent", 74, fill=WHITE, bold=True)
    text(d, (74, 366), "spends before", 74, fill=WHITE, bold=True)
    text(d, (74, 446), "it thinks", 74, fill=WHITE, bold=True)
    text(d, (76, 525), "Preflight admission control", 28, fill=MUTED, bold=True)
    text(d, (76, 565), "before tool side effects.", 28, fill=MUTED)
    d.rounded_rectangle((74, 966, 338, 1022), radius=28, fill=WHITE)
    text(d, (206, 1002), "View repo", 23, fill=(15, 23, 42), bold=True, anchor="mm")
    text(d, (812, 1000), "dambertmunoz.com", 20, fill=(255, 255, 255, 180), anchor="mm")
    text(d, (812, 1030), "linkedin.com/in/dambert-m-4b772397", 17, fill=(255, 255, 255, 135), anchor="mm")


def render() -> None:
    base = gradient_bg().convert("RGBA")
    add_radial_glow(base, (255, 150), 650, CYAN, 96)
    add_radial_glow(base, (980, 880), 560, WARM, 74)
    add_radial_glow(base, (780, 360), 600, VIOLET, 82)
    draw_dotted_grid(base)
    draw_blob(base)
    draw_dashboard(base, 585, 156, -4)
    draw_code_card(base, 566, 560, 5)
    draw_orbit(base, 790, 640)
    draw_title(base)
    draw_stat_pills(base)

    # Add a subtle final vignette.
    vignette = Image.new("RGBA", base.size, (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    vd.rectangle((0, 0, SIZE, 70), fill=(0, 0, 0, 60))
    vd.rectangle((0, SIZE - 90, SIZE, SIZE), fill=(0, 0, 0, 70))
    vignette = vignette.filter(ImageFilter.GaussianBlur(45))
    base.alpha_composite(vignette)

    png = OUT / "preflight-budget-gate-social-card.png"
    base.convert("RGB").save(png, quality=96)
    print(png)


if __name__ == "__main__":
    render()
