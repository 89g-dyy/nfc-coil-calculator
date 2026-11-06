"""Render the application icon (PNG, ICO and SVG) with Pillow."""
from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFilter

ASSETS = Path(__file__).resolve().parents[1] / "src" / "nfc_coil_calculator" / "assets"
SCALE = 3
SIZE = 512

COIL = "M122 128 H369 Q384 128 384 143 V369 Q384 384 369 384 H143 Q128 384 128 369 V205 Q128 190 143 190 " \
       "H307 Q322 190 322 205 V307 Q322 322 307 322 H205 Q190 322 190 307 V266 Q190 251 205 251 " \
       "H248 Q259 251 259 262 V274"

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><defs>'
    '<linearGradient id="bg" x2="1" y2="1"><stop stop-color="#12364f"/>'
    '<stop offset="1" stop-color="#091323"/></linearGradient>'
    '<linearGradient id="coil" x1="0" y1="0" x2=".7" y2="1"><stop stop-color="#5fe9ff"/>'
    '<stop offset=".65" stop-color="#9ff5ff"/><stop offset="1" stop-color="#ffc36c"/></linearGradient>'
    '<filter id="glow"><feGaussianBlur stdDeviation="10"/></filter></defs>'
    '<rect x="8" y="8" width="496" height="496" rx="112" fill="url(#bg)" stroke="#3f7598" stroke-width="3"/>'
    f'<path d="{COIL}" fill="none" stroke="#26d9f7" stroke-width="30" filter="url(#glow)"/>'
    f'<path d="{COIL}" fill="none" stroke="url(#coil)" stroke-width="23" stroke-linejoin="round" '
    'stroke-linecap="round"/><circle cx="122" cy="128" r="16" fill="#d7fcff"/>'
    '<circle cx="122" cy="128" r="6" fill="#123040"/><circle cx="259" cy="274" r="16" fill="#ffc970"/>'
    '<circle cx="259" cy="274" r="6" fill="#123040"/></svg>'
)

# Corner points of the spiral, clockwise from the outer terminal.
CORNERS = [(122, 128), (384, 128), (384, 384), (128, 384), (128, 190), (322, 190), (322, 322),
           (190, 322), (190, 251), (259, 251), (259, 274)]


def rounded_path(points, radius_limit=15, steps=12):
    """Round orthogonal corners with quadratic interpolation."""
    path = [points[0]]
    for i in range(1, len(points) - 1):
        previous, corner, following = points[i - 1], points[i], points[i + 1]
        radius = min(radius_limit, math.dist(previous, corner) / 3, math.dist(corner, following) / 3)
        start = (corner[0] + (previous[0] - corner[0]) * radius / math.dist(previous, corner),
                 corner[1] + (previous[1] - corner[1]) * radius / math.dist(previous, corner))
        end = (corner[0] + (following[0] - corner[0]) * radius / math.dist(following, corner),
               corner[1] + (following[1] - corner[1]) * radius / math.dist(following, corner))
        path.append(start)
        for step in range(1, steps + 1):
            t = step / steps
            path.append(((1 - t) ** 2 * start[0] + 2 * (1 - t) * t * corner[0] + t * t * end[0],
                         (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * corner[1] + t * t * end[1]))
    path.append(points[-1])
    return path


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    s, n = SCALE, SIZE
    image = Image.new("RGBA", (n * s, n * s), (0, 0, 0, 0))
    mask = Image.new("L", image.size)
    ImageDraw.Draw(mask).rounded_rectangle((8 * s, 8 * s, 504 * s, 504 * s), radius=112 * s, fill=255)

    background = Image.new("RGBA", image.size)
    pixels = background.load()
    for y in range(n * s):
        for x in range(n * s):
            d = math.hypot(x / s - 125, y / s - 95) / 600
            pixels[x, y] = (int(15 - 5 * min(1, d)), int(43 - 25 * min(1, d)),
                            int(70 - 32 * min(1, d)), 255)
    background.putalpha(mask)
    image.alpha_composite(background)

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((10 * s, 10 * s, 502 * s, 502 * s), radius=110 * s,
                           outline=(77, 136, 169, 160), width=3 * s)
    for x in range(72, 480, 42):
        for y in range(72, 480, 42):
            if mask.getpixel((x * s, y * s)):
                draw.ellipse(((x - 1) * s, (y - 1) * s, (x + 1) * s, (y + 1) * s),
                             fill=(87, 161, 192, 60))

    scaled = [(x * s, y * s) for x, y in rounded_path(CORNERS)]
    glow = Image.new("RGBA", image.size)
    ImageDraw.Draw(glow).line(scaled, fill=(27, 217, 247, 230), width=27 * s, joint="curve")
    image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(15 * s)))

    draw = ImageDraw.Draw(image)
    draw.line([(x + 3 * s, y + 6 * s) for x, y in scaled], fill=(1, 8, 21, 255),
              width=27 * s, joint="curve")
    total = sum(math.dist(a, b) for a, b in zip(scaled, scaled[1:]))
    offset = 0.0
    for a, b in zip(scaled, scaled[1:]):
        t = offset / total
        if t < 0.67:
            color = (70 + int(65 * t), 226 + int(17 * t), 255)
        else:
            u = (t - 0.67) / 0.33
            color = (int(115 + 140 * u), int(237 - 54 * u), int(255 - 160 * u))
        draw.line([a, b], fill=color, width=23 * s)
        radius = 11 * s
        draw.ellipse((a[0] - radius, a[1] - radius, a[0] + radius, a[1] + radius), fill=color)
        offset += math.dist(a, b)

    for point, color in [(scaled[0], (215, 252, 255, 255)), (scaled[-1], (255, 201, 112, 255))]:
        radius = 16 * s
        draw.ellipse((point[0] - radius, point[1] - radius, point[0] + radius, point[1] + radius),
                     fill=color)
        radius = 6 * s
        draw.ellipse((point[0] - radius, point[1] - radius, point[0] + radius, point[1] + radius),
                     fill=(18, 48, 64, 255))
    draw.arc((29 * s, 29 * s, 483 * s, 483 * s), 192, 263, fill=(110, 201, 229, 100), width=2 * s)

    image = image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    image.save(ASSETS / "icon.png")
    image.resize((64, 64), Image.Resampling.LANCZOS).save(ASSETS / "icon_64.png")
    image.save(ASSETS / "icon.ico", sizes=[(16, 16), (20, 20), (24, 24), (32, 32), (40, 40),
                                           (48, 48), (64, 64), (128, 128), (256, 256)])
    (ASSETS / "icon.svg").write_text(SVG, encoding="utf-8")
    write_flags()
    print("Wrote icon.png, icon_64.png, icon.ico, icon.svg and the language flags")


def star(draw, center, radius, fill):
    points = []
    for index in range(10):
        angle = -math.pi / 2 + index * math.pi / 5
        distance = radius if index % 2 == 0 else radius * 0.382
        points.append((center[0] + distance * math.cos(angle),
                       center[1] + distance * math.sin(angle)))
    draw.polygon(points, fill=fill)


def union_jack(width, height):
    image = Image.new("RGBA", (width, height), (1, 33, 105, 255))
    draw = ImageDraw.Draw(image)
    white, red = (255, 255, 255, 255), (200, 16, 46, 255)
    for color, ratio in ((white, 0.34), (red, 0.18)):
        thickness = int(round(height * ratio))
        draw.line([(0, 0), (width, height)], fill=color, width=thickness)
        draw.line([(0, height), (width, 0)], fill=color, width=thickness)
    for color, ratio in ((white, 0.28), (red, 0.16)):
        half = height * ratio
        draw.rectangle((width / 2 - half, 0, width / 2 + half, height), fill=color)
        draw.rectangle((0, height / 2 - half, width, height / 2 + half), fill=color)
    return image


def china_flag(width, height):
    image = Image.new("RGBA", (width, height), (222, 41, 16, 255))
    draw = ImageDraw.Draw(image)
    yellow = (255, 222, 0, 255)
    star(draw, (width * 0.17, height * 0.25), height * 0.30, yellow)
    for x, y in ((0.33, 0.06), (0.40, 0.19), (0.40, 0.35), (0.33, 0.47)):
        star(draw, (width * x, height * y), height * 0.10, yellow)
    return image


def write_flags():
    """Small flag icons for the language switch button."""
    for language, render in (("en", union_jack), ("zh", china_flag)):
        for suffix, width, height in (("", 48, 32), ("_small", 24, 16)):
            supersampled = render(width * 4, height * 4)
            mask = Image.new("L", supersampled.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                (0, 0, supersampled.width - 1, supersampled.height - 1),
                radius=supersampled.height * 0.14, fill=255)
            supersampled.putalpha(mask)
            supersampled.resize((width, height), Image.Resampling.LANCZOS).save(
                ASSETS / f"flag_{language}{suffix}.png")


if __name__ == "__main__":
    main()
