# Kasol: 1st Year Anniversary (first cut)

1920×1080, 30 fps, 90 s, dark mode. A slow, warm recap of the trip that opens and closes on a glowing title.

## Look

- Ground `#07080b`, with a warm radial glow (`#ff9a4a` at 0–22% alpha) behind titles only.
- Title "KASOL": Playfair Display 700, 230 px (21% of height), tracking 0.08 em, ink `#f4efe6`.
- Subtitle "1st Year Anniversary": Montserrat 400, 54 px, uppercase, tracking 0.22 em, amber `#ffc27a`. Its glow is a two-layer text-shadow (18 px at 75% alpha, 52 px at 45% alpha) that rises once over 1.8 s and then holds still. No pulsing.
- Kicker and chapter labels: Montserrat 400, 22 px, tracking 0.45 em, `#9aa0aa`, with a 64 px amber rule.
- Media frames: 18 px radius, 1 px `rgba(255,255,255,0.08)` border, deep shadow. Portrait media sits in frames 780 px tall; landscape photos fill the frame.
- Embers: 36 tiny amber dots drifting upwards in the intro and outro only, each at its own constant speed.

## Banned defaults

Fade-and-slide-up on every element; titles moving after they land; pulsing glow; the same entrance on every scene; crossfading two worlds into each other.

## Beats

| Time | Scene | Content | In | Out |
| --- | --- | --- | --- | --- |
| 0–12 | intro | kicker, KASOL per letter, rule, subtitle per word, glow rises | letters 0.12 s apart from 1.6 s | words blur out 10.6–11.6 s |
| 12–21 | morning | breakfast photo full frame, slow push 1.04→1.12 | rise from black 0.9 s | blur swap 0.5 s |
| 21–33 | golden | triptych: walk to sunset, valley sunset, sun rays (all pre-slowed with frame interpolation) | clip-path reveal from the bottom, 0.15 s stagger | blur swap |
| 33–44 | sunset | road walk photo, her on the road video (pre-slowed), sunset view photo | blur 12→0 and scale 0.94→1 | blur swap |
| 44–56 | night | Royal Enfield full frame, then snooker diptych at 5.6 s | light-up from black | blur swap |
| 56–68 | manikaran | gurudwara full frame, then river-drive and Manikaran river clips beside a title | blur-in | blur swap |
| 68–78 | homeward | dusk ridge and dusk pines diptych | horizontal whip in | dip |
| 78–90 | outro | KASOL, glowing subtitle, closing line | whole line blur-in | everything fades to black 87.2–89.8 s |

## Sound

Silent in this cut: HeyGen is not signed in and no track was supplied. A music bed of the person's choice goes on its own lane at volume 0.8 with a 2.5 s fade-out ending at 90 s.

## Media notes

- All iPhone clips were HLG HDR; they are tone-mapped to SDR BT.709 so the render stays a standard H.264 MP4.
- Short clips are slowed offline (`minterpolate`) instead of with `data-playback-rate`, which stuttered below 12 fps.
- `tools/generate.py` rewrites `index.html` and `compositions/` from one place; hand edits to those files are overwritten if it runs again.
