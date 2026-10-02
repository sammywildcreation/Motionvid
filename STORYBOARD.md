---
format: 1920x1080
fps: 30
duration: 50
voice: Kokoro af_heart (offline)
music: synthesized bed + UI sound design (scripts/make-audio.py → assets/audio/mix.m4a)
message: "You don't have to read all of it to understand all of it — Grasp, coming soon"
mode: autonomous
---

# Grasp — "The Night Before" (v2)

All times live in `assets/timing.js`; the composition and the audio mix both read it.
v1 (the 60 s beat-cut promo) is in git history and `renders/promo.mp4`.

| Time        | Beat                  | Picture                                                                                         | Voice                                                                 |
| ----------- | --------------------- | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 0.0–4.9     | 11:47 PM              | Lock screen clock, ticking. A Course Rep notification drops in: exam Friday, all 192 pages.     | "It's eleven forty-seven p.m. Your exam is on Friday."                |
| 4.9–8.0     | The pile              | Camera dives through a corridor of real document pages; page counter races 1 → 192.             | "And it covers all one hundred and ninety-two pages."                 |
| 8.0–9.0     | One night.            | Silence + hit, "One night." slams in.                                                           | —                                                                     |
| 9.0–12.6    | The question          | Words land with the voice; "understand" in orange. White flash.                                 | "What if you didn't have to read all of it… to understand all of it?" |
| 12.6–14.3   | Meet Grasp            | Logo spring, wordmark; camera pushes through the logo.                                          | "Meet Grasp."                                                         |
| 14.3–18.3   | Drop the PDF          | The app window flies in from depth. Cursor drags Impact_Guide.pdf (192 pages) onto Documents; drop zone lights; upload bar fills. | "Drop in your PDF."                                                   |
| 18.3–21.3   | It reads with you     | Document opens; cursor clicks Get Started; quiz-generation bar fills.                           | "Grasp reads it with you, then quizzes you on it."                    |
| 21.3–26.5   | Wrong → the page      | Cursor hovers, picks the wrong answer; window jolts; the explanation appears; cursor clicks "Page 1"; whip-pan with motion blur to the source paragraph, which gets selected line by line. | "Get one wrong, and it takes you straight to the page where the answer lives." |
| 26.5–30.3   | Flashcards            | Cursor opens Flashcards, clicks the card; it flips in 3D to the answer + page reference.        | "Flashcards bring back exactly what you keep missing."                |
| 30.3–34.0   | Record a class        | Record setup → cursor clicks Start recording; live waveform; timer time-lapses to 45 min (▶▶ 4×). | "Sitting in class? Just hit record."                                  |
| 34.0–37.9   | Paste the link        | Cursor clicks the link field and types the YouTube URL; the link is detected; clicks Add as source. | "Missed the lecture? Paste the link."                                 |
| 37.9–41.6   | Come back tomorrow    | Quiz results; screen dims; 3-day streak popup springs in with a confetti burst.                 | "Come back tomorrow, and you'll know more than you did today."        |
| 41.6–43.15  | Everything, spinning  | The window becomes one face of a 3D ring of every Grasp screen that spins away into depth.      | —                                                                     |
| 43.15–50.0  | End card              | Logo + wordmark, "Learn smarter. Grasp anything.", CTA "Coming soon".                           | "Grasp. Learn smarter. Grasp anything. Coming soon."                  |

## Rules this cut follows

- Screens are the real Figma exports (2x), never redrawn. Only what changes state is live DOM:
  cursor, ripples, dragged PDF chip, drop zone, progress fills, text selection, the flipping card
  (cut from the two real card states), recording timer + waveform, typed URL + caret, dim layer,
  streak modal (real 2x crop) and confetti.
- No highlight rings or spotlights; every emphasis is an interaction or a camera move.
