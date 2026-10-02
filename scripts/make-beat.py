"""Synthesize the 60 s, 120 BPM beat bed for the Grasp promo.

Deterministic (seeded noise). Writes assets/audio/beat.wav; ffmpeg then encodes it to beat.m4a.
Cut times in index.html sit on this grid: one beat = 0.5 s, one bar = 2 s.
"""
import wave
from pathlib import Path

import numpy as np

SR = 44100
BPM = 120
BEAT = 60 / BPM
DUR = 60.0
N = int(SR * DUR)
rng = np.random.default_rng(7)

L = np.zeros(N)
R = np.zeros(N)


def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    L[i : i + len(sig)] += sig * gain * (1 - max(pan, 0))
    R[i : i + len(sig)] += sig * gain * (1 + min(pan, 0))


def env(n, a, d):
    t = np.arange(n) / SR
    e = np.minimum(t / max(a, 1e-4), 1.0) * np.exp(-t / d)
    return e


def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7.5)
    s += 0.25 * np.tanh(np.sin(ph) * 3) * np.exp(-t * 30)
    return s


def clap():
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    # crude band-pass: difference of two moving averages
    k1 = np.convolve(noise, np.ones(3) / 3, "same")
    k2 = np.convolve(noise, np.ones(18) / 18, "same")
    s = (k1 - k2) * np.exp(-t * 18)
    for off in (0.0, 0.012, 0.024):
        j = int(off * SR)
        s[j:] += (k1 - k2)[: n - j] * np.exp(-t[: n - j] * 60) * 0.6
    return s * 0.9


def hat(open_=False):
    n = int((0.22 if open_ else 0.06) * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    hp = noise - np.convolve(noise, np.ones(4) / 4, "same")
    return hp * np.exp(-t * (14 if open_ else 70))


def bass(freq, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2 * t)
    s = np.tanh(s * 1.6)
    return s * env(n, 0.005, length * 0.55)


def pad(freqs, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.6, 0.0, 0.6):
            s += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6.28))
    a = np.minimum(t / 0.25, 1.0) * np.minimum((length - t) / 0.3, 1.0)
    return s / (len(freqs) * 3) * np.clip(a, 0, 1)


def riser(length):
    n = int(length * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    lp_w = np.linspace(40, 2, n).astype(int)
    out = np.empty(n)
    acc = 0.0
    for i in range(n):  # one-pole low-pass opening up
        a = 1.0 / lp_w[i]
        acc += a * (noise[i] - acc)
        out[i] = acc
    return out * (t / length) ** 2 * 3


def whoosh(length=0.35):
    n = int(length * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    sm = np.convolve(noise, np.ones(6) / 6, "same")
    shape = np.sin(np.pi * t / length) ** 2
    return sm * shape * 0.9


def impact():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (40 + 60 * np.exp(-t * 10)) * t) * np.exp(-t * 3)
    noise = rng.standard_normal(n)
    s += np.convolve(noise, np.ones(30) / 30, "same") * np.exp(-t * 5) * 0.8
    return s


# A-minor-ish loop: Am  F  C  G (one chord per bar)
ROOTS = [55.0, 43.65, 65.41, 49.0]
CHORDS = [[220, 261.6, 329.6], [174.6, 220, 261.6], [196, 261.6, 329.6], [196, 246.9, 293.7]]

K, CL, H = kick(), clap(), hat()
HO = hat(True)

beats = int(DUR / BEAT)
for b in range(beats):
    t = b * BEAT
    bar = b // 4
    pos = b % 4
    intro = t < 6.0
    build = 50.0 <= t < 54.0
    outro = t >= 54.0
    # kick
    if not outro or pos == 0:
        add(K, t, 0.55 if intro else 0.9)
    # clap on 2 & 4 in the groove
    if not intro and not outro and pos in (1, 3):
        add(CL, t, 0.45)
    # hats
    if not outro:
        add(H, t + BEAT / 2, 0.22 if intro else 0.3, pan=0.3)
        if not intro:
            add(H, t + BEAT / 4, 0.12, pan=-0.3)
            add(H, t + 3 * BEAT / 4, 0.12, pan=-0.3)
    if not intro and not outro and pos == 3 and bar % 2 == 1:
        add(HO, t + BEAT / 2, 0.18, pan=0.2)
    # bass on 8ths after the reveal
    if not intro and not outro:
        root = ROOTS[bar % 4]
        for e in range(2):
            add(bass(root * (2 if (e == 1 and pos == 3) else 1), BEAT / 2 * 0.9), t + e * BEAT / 2, 0.32)

# pads: quiet in the intro, fuller in the groove, held in the outro
for bar in range(int(DUR / (4 * BEAT))):
    t = bar * 4 * BEAT
    g = 0.10 if t < 6 else (0.16 if t < 54 else 0.2)
    add(pad(CHORDS[bar % 4], 4 * BEAT), t, g)

# snare roll building into the close (50–54 s)
for i in range(32):
    t = 50.0 + i * (4.0 / 32)
    add(CL, t, 0.08 + 0.4 * (i / 31))

# risers into the reveal and the end card, impacts on the drops
add(riser(2.0), 4.0, 0.22)
add(riser(2.0), 52.0, 0.25)
add(impact(), 6.0, 0.55)
add(impact(), 54.0, 0.6)

# whooshes on every screen entry (frame starts in index.html)
for t in (2.0, 8.0, 14.0, 18.0, 24.0, 28.0, 35.0, 39.0, 43.0, 47.0):
    add(whoosh(), t - 0.12, 0.35, pan=0.15)

# master: gentle fade in/out, soft clip, normalize
mix = np.stack([L, R], axis=1)
fade_in = np.minimum(np.arange(N) / (0.05 * SR), 1.0)
fade_out = np.clip((DUR - np.arange(N) / SR) / 2.5, 0, 1)
mix *= (fade_in * fade_out)[:, None]
mix = np.tanh(mix * 1.1)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.89

out = Path(__file__).resolve().parent.parent / "assets" / "audio" / "beat.wav"
out.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(out), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print(out)
