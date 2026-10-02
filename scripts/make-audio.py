"""Build the full soundtrack for the Grasp "night before" promo.

Reads assets/timing.js (the same timing map index.html uses) and mixes:
  - the Kokoro voice lines (assets/vo/lineNN.wav) at their VO start times
  - a synthesized music bed: clock ticks + heartbeat in the hook, a 120 BPM groove
    through the demo, a build into the end card
  - UI sound effects: clicks, keystrokes, whooshes, page flutter, pops, hits
  - ducking: music drops under every voice line
Writes assets/audio/mix.m4a (via ffmpeg). Deterministic (seeded noise).
"""
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
T = json.loads(re.search(r"window\.T\s*=\s*(\{.*\});", (ROOT / "assets/timing.js").read_text(), re.S).group(1))

SR = 44100
DUR = T["duration"]
N = int(SR * DUR)
rng = np.random.default_rng(11)

music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
voice = np.zeros(N)


def put(buf, sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i + len(sig) <= 0:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[: N - i]
    if buf.ndim == 1:
        buf[i : i + len(sig)] += sig * gain
    else:
        buf[i : i + len(sig), 0] += sig * gain * (1 - max(pan, 0))
        buf[i : i + len(sig), 1] += sig * gain * (1 + min(pan, 0))


def tt(n):
    return np.arange(n) / SR


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, "same")


# ---------- instruments ----------
def kick(depth=1.0):
    n = int(0.45 * SR)
    t = tt(n)
    f = 46 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 7.5) + 0.25 * np.tanh(np.sin(ph) * 3) * np.exp(-t * 30)) * depth


def heartbeat():
    n = int(0.5 * SR)
    t = tt(n)
    lub = np.sin(2 * np.pi * (38 + 40 * np.exp(-t * 30)) * t) * np.exp(-t * 14)
    out = lub.copy()
    j = int(0.22 * SR)
    out[j:] += 0.7 * lub[: n - j]
    return lowpass(out, 6)


def tick():
    n = int(0.03 * SR)
    t = tt(n)
    noise = rng.standard_normal(n)
    hp = noise - lowpass(noise, 3)
    return (hp * 0.6 + np.sin(2 * np.pi * 3200 * t) * 0.5) * np.exp(-t * 260)


def clap():
    n = int(0.3 * SR)
    t = tt(n)
    noise = rng.standard_normal(n)
    bp = lowpass(noise, 3) - lowpass(noise, 18)
    return bp * np.exp(-t * 18) * 0.9


def hat(open_=False):
    n = int((0.22 if open_ else 0.06) * SR)
    t = tt(n)
    noise = rng.standard_normal(n)
    return (noise - lowpass(noise, 4)) * np.exp(-t * (14 if open_ else 70))


def bass(freq, length):
    n = int(length * SR)
    t = tt(n)
    s = np.tanh((np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t)) * 1.6)
    return s * np.minimum(t / 0.005, 1) * np.exp(-t / (length * 0.55))


def pad(freqs, length, bright=1.0):
    n = int(length * SR)
    t = tt(n)
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.7, 0.0, 0.7):
            s += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6.28))
            s += 0.25 * bright * np.sin(4 * np.pi * (f + det) * t)
    a = np.clip(np.minimum(t / 0.4, 1.0) * np.minimum((length - t) / 0.4, 1.0), 0, 1)
    return s / (len(freqs) * 3) * a


def drone(length):
    n = int(length * SR)
    t = tt(n)
    s = np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.4 * t) + 0.2 * np.sin(2 * np.pi * 110 * t)
    s *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * t)
    a = np.clip(np.minimum(t / 1.5, 1.0) * np.minimum((length - t) / 0.3, 1.0), 0, 1)
    return s * a


def riser(length):
    n = int(length * SR)
    t = tt(n)
    noise = rng.standard_normal(n)
    out = np.empty(n)
    acc = 0.0
    w = np.linspace(40, 2, n)
    for i in range(n):
        acc += (noise[i] - acc) / w[i]
        out[i] = acc
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / length) ** 2) / SR) * 0.15
    return (out * 3 + tone) * (t / length) ** 2


def impact():
    n = int(1.6 * SR)
    t = tt(n)
    s = np.sin(2 * np.pi * (36 + 70 * np.exp(-t * 9)) * t) * np.exp(-t * 2.6)
    s += lowpass(rng.standard_normal(n), 30) * np.exp(-t * 4) * 0.9
    return s


def whoosh(length=0.45):
    n = int(length * SR)
    t = tt(n)
    noise = rng.standard_normal(n)
    sm = lowpass(noise, 5)
    return sm * np.sin(np.pi * t / length) ** 2 * 0.9


def click():
    n = int(0.05 * SR)
    t = tt(n)
    body = np.sin(2 * np.pi * 1700 * t) * np.exp(-t * 180)
    noise = rng.standard_normal(n)
    return (body * 0.8 + (noise - lowpass(noise, 3)) * 0.4 * np.exp(-t * 400))


def key(i):
    n = int(0.035 * SR)
    t = tt(n)
    noise = rng.standard_normal(n)
    f = 2400 + (i * 137) % 900
    return ((noise - lowpass(noise, 2)) * 0.5 + np.sin(2 * np.pi * f * t) * 0.25) * np.exp(-t * 300)


def pop():
    n = int(0.35 * SR)
    t = tt(n)
    s = np.sin(2 * np.pi * (500 + 900 * np.exp(-t * 25)) * t) * np.exp(-t * 14)
    for k, f in enumerate((1568, 2093, 2637)):
        j = int((0.05 + 0.05 * k) * SR)
        s[j:] += 0.25 * np.sin(2 * np.pi * f * t[: n - j]) * np.exp(-t[: n - j] * 18)
    return s


def flutter(length):
    n = int(length * SR)
    t = tt(n)
    noise = lowpass(rng.standard_normal(n), 3)
    env = (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t)) ** 3
    return noise * env * np.minimum(t / 0.3, 1) * np.minimum((length - t) / 0.3, 1)


# ---------- music bed ----------
# hook: drone + clock ticks, heartbeat once the pages arrive
put(music, drone(T["reveal"] - 0.1), 0.0, 0.22)
for s in np.arange(0.6, T["flight"], 1.0):
    put(sfx, tick(), s, 0.22, pan=0.2)
hb = T["flight"]
while hb < T["reveal"] - 0.6:
    put(music, heartbeat(), hb, 0.55)
    hb += 0.82 if hb < T["question"] else 0.7
put(music, riser(2.2), T["reveal"] - 2.2, 0.22)

# groove from the reveal through the demo (120 BPM, one bar = 2 s)
BEAT = 0.5
ROOTS = [55.0, 43.65, 65.41, 49.0]
CHORDS = [[220, 261.6, 329.6], [174.6, 220, 261.6], [196, 261.6, 329.6], [196, 246.9, 293.7]]
g0, g1 = T["reveal"], T["outro"]
K, CL, H, HO = kick(), clap(), hat(), hat(True)
b = 0
while g0 + b * BEAT < g1:
    t = g0 + b * BEAT
    pos, bar = b % 4, b // 4
    put(music, K, t, 0.8)
    if pos in (1, 3):
        put(music, CL, t, 0.35)
    put(music, H, t + BEAT / 2, 0.25, pan=0.3)
    put(music, H, t + BEAT / 4, 0.1, pan=-0.3)
    put(music, H, t + 3 * BEAT / 4, 0.1, pan=-0.3)
    if pos == 3 and bar % 2:
        put(music, HO, t + BEAT / 2, 0.15, pan=0.2)
    for e in range(2):
        put(music, bass(ROOTS[bar % 4] * (2 if (e == 1 and pos == 3) else 1), BEAT * 0.45), t + e * BEAT / 2, 0.3)
    if pos == 0:
        put(music, pad(CHORDS[bar % 4], 4 * BEAT), t, 0.13)
    b += 1

# outro: build into the end card, then a held chord
for i in range(24):
    put(music, CL, T["outro"] + i * ((T["endHit"] - T["outro"]) / 24), 0.06 + 0.32 * i / 23)
put(music, riser(T["endHit"] - T["outro"]), T["outro"], 0.22)
put(music, pad([220, 261.6, 329.6, 440], DUR - T["endHit"], 1.4), T["endHit"], 0.26)
for k in range(3):
    put(music, kick(0.7), T["endHit"] + 2.0 * k, 0.6)

# ---------- sfx ----------
put(sfx, impact(), T["reveal"], 0.7)
put(sfx, impact(), T["endHit"], 0.75)
put(sfx, impact() * 0.5, T["oneNight"], 0.5)
put(sfx, flutter(T["oneNight"] - T["flight"]), T["flight"], 0.25)
for w in T["whooshes"]:
    put(sfx, whoosh(), w - 0.15, 0.32, pan=0.15)
for c in T["clicks"]:
    put(sfx, click(), c, 0.45, pan=-0.1)
n_chars = len(T["url"])
for i in range(n_chars):
    put(sfx, key(i), T["typeStart"] + i * (T["typeEnd"] - T["typeStart"]) / n_chars, 0.22, pan=0.05 * ((i % 3) - 1))
put(sfx, pop(), T["modal"], 0.5)
put(sfx, pop() * 0.6, T["notify"], 0.5, pan=0.2)

# ---------- voice ----------
vo_spans = []
for key_, start in T["vo"].items():
    data, sr = sf.read(str(ROOT / f"assets/vo/line{key_}.wav"))
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != SR:
        x_old = np.arange(len(data)) / sr
        x_new = np.arange(int(len(data) * SR / sr)) / SR
        data = np.interp(x_new, x_old, data)
    data = data / (np.max(np.abs(data)) + 1e-9)
    # gentle presence: a touch of low-cut via subtracting a long average
    data = data - lowpass(data, 220)
    put(voice, data, start, 1.0)
    vo_spans.append((start, start + len(data) / SR))

# ducking envelope for the music (−9 dB under voice, smooth 120 ms ramps)
duck = np.ones(N)
for a, z in vo_spans:
    duck[int(max(a - 0.12, 0) * SR) : int(min(z + 0.2, DUR) * SR)] = 0.36
duck = lowpass(duck, int(0.12 * SR))

mix = music * duck[:, None] * 0.75 + sfx * 0.8 + voice[:, None] * 0.95
fade = np.clip((DUR - tt(N)) / 1.8, 0, 1)
mix *= fade[:, None]
mix = np.tanh(mix * 1.05)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.9

out_wav = ROOT / "assets/audio/mix.wav"
out_wav.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(out_wav), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out_wav), "-c:a", "aac", "-b:a", "256k", str(ROOT / "assets/audio/mix.m4a")], check=True)
out_wav.unlink()
print("vo spans:", [(round(a, 2), round(z, 2)) for a, z in vo_spans])
