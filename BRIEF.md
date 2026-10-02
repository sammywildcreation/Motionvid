---
workflow: product-launch-video
flow: automation
storyboard: no
message: "Grasp turns whatever you're given to learn into something you actually understand — coming soon"
destination: youtube
aspect: 1920x1080
fps: 30
language: en
audience: students, working professionals and self-taught learners facing long PDFs, lectures and recordings
length: 50s
angle: "The Night Before" — 11:47 PM, 192 pages, one night; Grasp as a live, cursor-driven session
---

## Intent

A 1-minute kinetic SaaS promo for Grasp, which is not launched yet ("coming soon").
The user asked for a story that hooks viewers without being given one: open on the
fear of a huge document, introduce Grasp, then walk through the real web screens.
Style in the user's words: "Kinetic style: fast zooms and pans into the screenshots,
big bold words between the screens, cuts on a steady beat."

## Assets

- assets/screens/*.png — exported from the Grasp UI Figma file (Light Theme page), used as-is. 2x exports except video-summary, streak, library, login (1x — network policy blocked the 2x export of photo-heavy frames).
- assets/grasp-logo.svg — the Grasp app icon, exported as SVG from Figma node 5670:11912.
- assets/fonts — Onest + Cal Sans (the fonts the designs use), from @fontsource.

## Customizations

- Each screen: zoom into the part that matters with an orange focus ring and one short line of what it does for the user.
- Bold word interstitials between screens.
- End card: logo, "Learn smarter. Grasp anything." (line from the login screen), CTA "Coming soon".
- Music: synthesized 120 BPM beat (no HeyGen sign-in, no local MusicGen); every cut lands on a beat.

## Notes

- Screens must not be redrawn — show the exported PNGs.
- No claims of users or launch; it's a coming-soon promo.
- Render to renders/promo.mp4.

## v2 (requested after v1)

- "Use your highest motion skill", a new story that hooks hard, a real human-sounding voice,
  no highlight rings — show inputting on the screen so the motion looks real — and sharper.
- Voice: Kokoro af_heart (user chose Kokoro because HeyGen's API is paid).
- Sharpness: all hero screens are 2x exports; results is 1.5x; streak modal is a 2x crop.
  figma.com is still blocked by the network policy, so 3x exports were not possible yet.
- Output: renders/promo-v2.mp4 (CRF 12).
