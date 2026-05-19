from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math
import random

SIZE = 1200
OUT = Path("assets")
OUT.mkdir(exist_ok=True)

NAVY = (6, 12, 30)
INDIGO = (18, 32, 76)
PLUM = (58, 30, 92)
CYAN = (104, 225, 253)
VIOLET = (167, 139, 250)
AMBER = (255, 184, 108)
MINT = (143, 255, 205)
WHITE = (248, 250, 252)
MUTED = (203, 213, 225)
PANEL = (8, 14, 38)


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if mono:
        candidates += ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Supplemental/Courier New.ttf"]
    if bold:
        candidates += ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"]
    candidates += ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def text(draw: ImageDraw.ImageDraw, xy, value: str, size: int, *, fill=WHITE, bold=False, mono=False, anchor=None):
    draw.text(xy, value, font=font(size, bold=bold, mono=mono), fill=fill, anchor=anchor)


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def make_background() -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE), NAVY)
    px = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            nx, ny = x / SIZE, y / SIZE
            t = min(1.0, nx * 0.52 + ny * 0.62)
            base = tuple(int(NAVY[i] + (INDIGO[i] - NAVY[i]) * min(1, t * 1.35)) for i in range(3))
            if t > 0.52:
                u = (t - 0.52) / 0.48
                base = tuple(int(base[i] + (PLUM[i] - base[i]) * u * 0.82) for i in range(3))
            px[x, y] = base
    return img.convert("RGBA")


def radial_glow(base: Image.Image, cx: int, cy: int, radius: int, color, alpha: int):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for r in range(radius, 0, -10):
        a = int(alpha * (1 - r / radius) ** 1.8)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*color, a))
    base.alpha_composite(layer)


def shadowed_panel(base: Image.Image, box, radius: int = 34, fill=(8, 14, 38, 192), outline=(255, 255, 255, 42), shadow_alpha=85):
    x1, y1, x2, y2 = box
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x1, y1 + 26, x2, y2 + 26), radius=radius, fill=(0, 6, 22, shadow_alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    base.alpha_composite(shadow)

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)
    d.line((x1 + radius, y1 + 2, x2 - radius, y1 + 2), fill=(255, 255, 255, 54), width=2)
    base.alpha_composite(layer)


def draw_noise_and_grid(base: Image.Image):
    d = ImageDraw.Draw(base)
    random.seed(21)
    # Premium micro texture only. No visible white grid: it made the card feel cheap.
    for _ in range(220):
        x = random.randrange(0, SIZE)
        y = random.randrange(0, SIZE)
        a = random.randrange(8, 24)
        d.point((x, y), fill=(255, 255, 255, a))
    # No visible grid. Only sparse micro speckles for depth.


def draw_left_copy(base: Image.Image):
    d = ImageDraw.Draw(base)
    rounded(d, (72, 64, 300, 118), 27, (8, 14, 38, 176), (255, 255, 255, 58), 1)
    d.ellipse((94, 83, 116, 105), fill=CYAN)
    text(d, (136, 80), "Dambert Lab", 23, bold=True)

    text(d, (74, 178), "Agentic AI Architecture", 30, fill=CYAN)
    text(d, (74, 282), "Your agent", 76, bold=True)
    text(d, (74, 365), "spends before", 76, bold=True)
    text(d, (74, 448), "it thinks", 76, bold=True)

    text(d, (76, 530), "Preflight admission control", 27, fill=WHITE, bold=True)
    text(d, (76, 572), "before tool side effects.", 27, fill=MUTED)

    # Premium chips without the previous white-circle look.
    chips = [("Intent", CYAN), ("Policy", VIOLET), ("Reserve", MINT), ("Audit", AMBER)]
    for i, (label, color) in enumerate(chips):
        x = 74 + i * 112
        rounded(d, (x, 876, x + 92, 920), 22, (8, 14, 38, 166), (*color, 136), 1)
        text(d, (x + 46, 904), label, 17, fill=WHITE if i != 1 else color, bold=True, anchor="mm")

    rounded(d, (74, 960, 338, 1020), 30, WHITE, None, 1)
    text(d, (206, 997), "View repo", 24, fill=(15, 23, 42), bold=True, anchor="mm")
    text(d, (805, 997), "dambertmunoz.com", 21, fill=(255, 255, 255, 186), anchor="mm")
    text(d, (805, 1028), "linkedin.com/in/dambert-m-4b772397", 17, fill=(255, 255, 255, 142), anchor="mm")


def line_glow(base: Image.Image, points, color, width=5, glow=16):
    glow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    gd.line(points, fill=(*color, 120), width=width + glow, joint="curve")
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(glow // 2))
    base.alpha_composite(glow_layer)
    d = ImageDraw.Draw(base)
    d.line(points, fill=(*color, 220), width=width, joint="curve")


def draw_right_art(base: Image.Image):
    d = ImageDraw.Draw(base)

    # Abstract brand blob, toned down.
    blob = Image.new("RGBA", base.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(blob)
    bd.polygon([(650, 104), (1028, 202), (1110, 580), (974, 884), (612, 810), (510, 428)], fill=(255, 255, 255, 22), outline=(255, 255, 255, 30))
    blob = blob.filter(ImageFilter.GaussianBlur(0.8))
    base.alpha_composite(blob)

    # Back card.
    shadowed_panel(base, (612, 126, 1048, 390), radius=38, fill=(8, 14, 38, 158), outline=(255, 255, 255, 28), shadow_alpha=50)
    rounded(d, (650, 166, 822, 194), 14, (*CYAN, 220))
    for i, h in enumerate([54, 92, 66, 104, 82]):
        x = 658 + i * 54
        rounded(d, (x, 322 - h, x + 24, 322), 12, CYAN if i % 2 else VIOLET, None, 1)
    line_glow(base, [(664, 342), (740, 310), (810, 322), (878, 360), (948, 298)], CYAN, width=4, glow=12)

    # Main gate card, no white orbit/circle connectors.
    shadowed_panel(base, (578, 448, 1076, 812), radius=42, fill=(6, 12, 30, 214), outline=(255, 255, 255, 44), shadow_alpha=92)
    text(d, (628, 510), "ADMISSION CONTROL", 19, fill=CYAN, bold=True)
    text(d, (628, 552), "No side effect before", 34, fill=WHITE, bold=True)
    text(d, (628, 594), "policy + reservation", 34, fill=WHITE, bold=True)

    # Clean rail.
    rail_y = 676
    start_x = 636
    steps = [("Intent", CYAN), ("Policy", VIOLET), ("Reserve", MINT)]
    for i in range(2):
        x1 = start_x + i * 128 + 88
        x2 = start_x + (i + 1) * 128
        line_glow(base, [(x1, rail_y), (x2, rail_y)], steps[i + 1][1], width=4, glow=8)
    for i, (label, color) in enumerate(steps):
        x = start_x + i * 128
        rounded(d, (x, rail_y - 28, x + 88, rail_y + 28), 18, (8, 14, 38, 205), (*color, 170), 2)
        d.ellipse((x + 14, rail_y - 8, x + 30, rail_y + 8), fill=color)
        text(d, (x + 54, rail_y + 6), label, 15, fill=WHITE, bold=True, anchor="mm")

    gate_x = 1030
    line_glow(base, [(start_x + 2 * 128 + 88, rail_y), (gate_x - 54, rail_y)], CYAN, width=4, glow=8)
    rounded(d, (gate_x - 54, rail_y - 36, gate_x + 30, rail_y + 36), 22, (8, 14, 38, 215), CYAN, 2)
    d.line((gate_x - 34, rail_y - 12, gate_x - 16, rail_y + 10, gate_x + 12, rail_y - 18), fill=CYAN, width=5)
    text(d, (gate_x - 12, rail_y + 29), "GATE", 12, fill=CYAN, bold=True, anchor="mm")

    # Outcome strips, editorial not diagram literal.
    rounded(d, (628, 738, 820, 782), 22, (167, 139, 250, 42), (167, 139, 250, 130), 1)
    text(d, (724, 766), "manual_review", 18, fill=WHITE, bold=True, anchor="mm")
    rounded(d, (844, 738, 1026, 782), 22, (255, 184, 108, 38), (255, 184, 108, 130), 1)
    text(d, (935, 766), "no tool call", 18, fill=WHITE, bold=True, anchor="mm")

    # Small audit card, bottom-right.
    shadowed_panel(base, (716, 822, 1048, 914), radius=28, fill=(8, 14, 38, 170), outline=(255, 255, 255, 34), shadow_alpha=45)
    text(d, (748, 858), "audit_event", 20, fill=MUTED, mono=True)
    rounded(d, (916, 842, 1014, 874), 16, (143, 255, 205, 38), (*MINT, 130), 1)
    text(d, (965, 864), "HELD", 15, fill=MINT, bold=True, anchor="mm")
    rounded(d, (748, 880, 856, 898), 9, (*CYAN, 180), None, 1)
    rounded(d, (870, 880, 1014, 898), 9, (*VIOLET, 160), None, 1)


def render() -> None:
    base = make_background()
    radial_glow(base, 250, 150, 620, CYAN, 78)
    radial_glow(base, 1000, 880, 620, AMBER, 64)
    radial_glow(base, 820, 360, 640, VIOLET, 84)
    draw_noise_and_grid(base)
    draw_right_art(base)
    draw_left_copy(base)

    # Vignette for premium focus.
    vignette = Image.new("RGBA", base.size, (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    vd.rectangle((0, 0, SIZE, 95), fill=(0, 0, 0, 46))
    vd.rectangle((0, SIZE - 120, SIZE, SIZE), fill=(0, 0, 0, 72))
    vignette = vignette.filter(ImageFilter.GaussianBlur(52))
    base.alpha_composite(vignette)

    path = OUT / "preflight-budget-gate-social-card.png"
    base.convert("RGB").save(path, quality=96)
    print(path)


if __name__ == "__main__":
    render()
