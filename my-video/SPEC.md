# Kasol: 1st Year Anniversary

A 90 s, 1920×1080, 30 fps dark-mode film of the couple's first anniversary trip to Kasol. It opens and closes on a glowing title and ends on #SayAnAparajitaStory.

## Look

- Ground `#07080b`; warm radial glow and drifting embers behind the titles only.
- "KASOL": Playfair Display 700, 230 px. Subtitle "1st Year Anniversary": Montserrat 54 px, amber `#ffc27a`, with a glow that rises once and then holds still.
- Chapter labels: Montserrat 28 px with an amber rule, bottom left inside title-safe.
- Media sit in rounded frames on the dark ground, sized to fit each beat's row (up to 780 px tall); single landscape photos fill the frame with a slow push.

## Structure

`tools/generate.py` holds the whole edit as a list of chapters and beats. Change that list and run `python3 tools/generate.py`.

| Time | Chapter | Beats |
| --- | --- | --- |
| 0–8 | Title | KASOL, glowing subtitle |
| 8–19 | The morning | breakfast · scooter + river walks · café |
| 19–27 | Golden hour | three sunset clips |
| 27–37 | Sunset | road walks · red sky + photographing the sun |
| 37–54 | Manikaran | gurudwara · temple and springs · river and langar · bridge · railings |
| 54–62 | Slow afternoons | heart frame · river rock + café selfie |
| 62–72 | After dark | Enfield · snooker · mirrors + cosy night |
| 72–80 | One year | candles and gift · cake · coaster |
| 80–90 | Outro | KASOL, subtitle, #SayAnAparajitaStory, fade to black |

Beat entrances rotate between a clip-path rise, a blur-in, a horizontal whip and a slow staggered reveal; every beat leaves with a short blur-out.

## Media notes

- iPhone clips were HLG HDR; they are tone-mapped to SDR BT.709 so the render stays a standard H.264 MP4.
- Short clips are slowed offline with frame interpolation, not with `data-playback-rate`.
- Not used: `dusk-ridge.jpg` (blurred), `last-light.mp4` (1.9 s, mostly dark), `river-drive.mp4` (replaced by the steadier `river-run.mp4`). The second IMG_4303 upload was an exact duplicate.

## Sound

Silent until a track is supplied. A music bed goes on its own lane at volume 0.8 with a 2.5 s fade-out ending at 90 s.
