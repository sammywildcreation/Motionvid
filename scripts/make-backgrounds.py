"""Render the promo's background plates as PNGs.

Pre-rendered so the composition carries no CSS radial gradients (many of those make
headless capture unreliable). Writes assets/bg/{dark,orange,light,glow}.png.
"""
import struct
import zlib
from pathlib import Path

import numpy as np

W, H = 1920, 1080
OUT = Path(__file__).resolve().parent.parent / "assets" / "bg"


def write_png(path, rgba):
    h, w, c = rgba.shape
    color_type = 6 if c == 4 else 2
    raw = b"".join(b"\x00" + rgba[y].tobytes() for y in range(h))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, color_type, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i : i + 2], 16) for i in (0, 2, 4)], dtype=float)


yy, xx = np.mgrid[0:H, 0:W].astype(float)


def radial(cx, cy, rx, ry):
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return np.clip(d, 0, 1)


def mix(a, b, t):
    return a[None, None, :] * (1 - t[..., None]) + b[None, None, :] * t[..., None]


def dither(img):
    rng = np.random.default_rng(3)
    return np.clip(img + rng.uniform(-0.6, 0.6, img.shape), 0, 255).astype(np.uint8)


OUT.mkdir(parents=True, exist_ok=True)

# dark: warm centre falling off to ink
t = radial(960, 594, 1200, 700) ** 1.2
write_png(OUT / "dark.png", dither(mix(hexrgb("#2a211c"), hexrgb("#14100e"), t)))

# orange: bright centre → brand orange → deep orange
t = radial(960, 486, 1300, 800)
inner = mix(hexrgb("#ff7a3d"), hexrgb("#fa5d19"), np.clip(t / 0.45, 0, 1))
outer = mix(hexrgb("#fa5d19"), hexrgb("#e24e10"), np.clip((t - 0.45) / 0.55, 0, 1))
img = np.where((t < 0.45)[..., None], inner, outer)
write_png(OUT / "orange.png", dither(img))

# light: warm paper with a soft orange glow behind the screen card
t = radial(960, 540, 1400, 900)
base = mix(hexrgb("#fffaf6"), hexrgb("#ede5dc"), t ** 1.4)
g = 1 - radial(960, 560, 760, 520)
glow = (g**2) * 0.22
img = base * (1 - glow[..., None]) + hexrgb("#fa5d19")[None, None, :] * glow[..., None]
write_png(OUT / "light.png", dither(img))

# glow: transparent orange burst (800x800) for the logo moments
S = 800
gy, gx = np.mgrid[0:S, 0:S].astype(float)
d = np.clip(np.sqrt((gx - S / 2) ** 2 + (gy - S / 2) ** 2) / (S / 2), 0, 1)
alpha = ((1 - d) ** 2 * 0.6 * 255).astype(np.uint8)
rgba = np.zeros((S, S, 4), dtype=np.uint8)
rgba[..., :3] = hexrgb("#fa5d19").astype(np.uint8)
rgba[..., 3] = alpha
write_png(OUT / "glow.png", rgba)
print("ok", sorted(p.name for p in OUT.iterdir()))
