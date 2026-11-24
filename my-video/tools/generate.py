"""Writes index.html and compositions/*.html for the Kasol anniversary reel (1080x1920).

Run from the project folder:  python3 tools/generate.py
Edit SCENES to add, remove or reorder shots. Shot lengths are worked out so the reel
lasts exactly TOTAL seconds: photos get one unit, clips and landscape photos more.
Every cut is a transition of OVERLAP seconds; the kinds rotate through TRANSITIONS, and
chapter changes use CHAPTER_TRANSITIONS.
Music: put the track at assets/audio/music.mp3 (or .m4a / .wav) and run this again.
Hand edits to index.html or compositions/ are overwritten when this runs.
"""
import glob, json, os, subprocess

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P, V = "assets/photos/", "assets/video/"
W, H, FPS, TOTAL = 1080, 1920, 30, 100
INTRO, OUTRO = 6.0, 7.5
OVERLAP = 0.4
WEIGHT = {"photo": 1.0, "video": 1.7, "wide": 1.7, "hero": 1.9, "split": 2.0, "pola": 2.8, "count": 2.6}
CAP_BONUS = 1.4  # a shot with a sticker caption stays on screen longer so it can be read
TRANSITIONS = ["zoom", "whip-left", "spin", "iris", "whip-up", "flash", "whip-right", "zoom-out"]
CHAPTER_TRANSITIONS = ["leak", "zoom", "leak", "spin"]


def ph(name, pos=None, pan=None, kind=None, cap=None, y=None, credit=None):
    """A photo. pos/y: focus point in %; pan: (from %, to %) to sweep across a wide one; cap: sticker text;
    credit: attribution line for licensed photos from Wikimedia Commons."""
    return {"tag": "img", "src": P + name + ".jpg", "pos": pos, "y": y, "pan": pan, "kind": kind, "cap": cap,
            "credit": credit}


def vd(name, start=0.0, cap=None):
    return {"tag": "video", "src": V + name + ".mp4", "start": start, "kind": "video", "pos": None, "y": None,
            "pan": None, "cap": cap}


def split(a, b, la, lb, cap=None):
    """Two photos stacked top and bottom, sliding in from opposite sides, each with a tag."""
    return {"tag": "split", "a": a, "b": b, "la": la, "lb": lb, "kind": "split", "cap": cap, "pan": None}


def pola(items, cap=None):
    """Polaroids dropping onto a warm board."""
    return {"tag": "pola", "items": items, "kind": "pola", "cap": cap, "pan": None}


def count(n, word, kicker):
    """A number rolling up like a slot machine."""
    return {"tag": "count", "n": n, "word": word, "kicker": kicker, "kind": "count", "cap": None, "pan": None}


SCENES = [
    ("drive", "The drive in", [
        vd("forest-drive"), vd("drive-traffic", start=1.0), vd("camp-pan"), ph("kasol-street", cap="Hello, Kasol"),
    ]),
    ("morning", "The morning", [
        ph("breakfast", pos=58, cap="Paratha o'clock"), ph("scooter-valley", pos=70, cap="Scooty diaries"),
        split(ph("him-river-sun", y=55), ph("her-river-sun", y=62), "His view", "Her view"),
        ph("cafe-food", cap="Carbs with a view"),
    ]),
    ("golden", "Golden hour", [
        vd("walk-to-sunset"), vd("valley-sunset", start=6.0, cap="Golden hour hits different"), vd("sun-rays"),
    ]),
    ("sunset", "Sunset", [
        ph("road-walk"), vd("her-on-road"), ph("sunset-view", pos=62),
        ph("her-photographing-sunset", pos=55, cap="One more photo, please"),
        ph("sunset-fire", cap="Sky on fire"), ph("sunset-road-red"),
    ]),
    ("manikaran", "Manikaran", [
        ph("gurudwara", pan=(30, 70)), ph("gurudwara-front", pos=40),
        ph("manikaran-temple-river", pos=40, cap="Hot springs, cold hands"),
        vd("river-valley"), vd("river-run"), vd("manikaran-river"), ph("langar-thali", cap="Langar love"),
        split(ph("him-on-bridge", pos=55, y=55), ph("her-on-bridge", pos=52, y=55), "His pose", "Her pose"),
        ph("him-bridge-walk", pos=56),
        split(ph("him-gurudwara-railing", pos=55, y=48), ph("her-peace-gurudwara", pos=60, y=45), "His lean", "Her peace"),
        ph("her-gurudwara-railing", pos=62),
    ]),
    ("afternoons", "Slow afternoons", [
        ph("her-heart", pos=45, cap="Heart full"), ph("her-river-dusk", pos=45),
        ph("him-river-rock", pos=58, cap="Rock star"),
        pola([ph("couple-selfie-manikaran", pos=43), ph("couple-selfie-cafe", pos=40), ph("couple-cosy-selfie", pos=45)],
             cap="Us, on repeat"),
    ]),
    ("night", "After dark", [
        ph("enfield-night", pan=(0, 100), cap="Night ride"),
        split(ph("snooker-him", pos=40, y=45), ph("snooker-her", pos=55, y=42), "His shot", "Her shot"),
        ph("apple-mirror", cap="Mirror, mirror"), ph("couple-cosy-night", pos=26), ph("room-mirror"),
    ]),
    ("oneyear", "One year", [
        count(365, "Days of us", "Our first year"), ph("anniversary-candles-crop", kind="hero", y=40),
        ph("anniversary-bracelet", kind="hero", cap="A for always"), ph("anniversary-cake", kind="hero"),
        ph("story-coaster", kind="hero"),
    ]),
]
INTRO_BG = vd("valley-sunset")
OUTRO_BG = ph("couple-heart", pos=48)
CLOSING = "#SayAnAparajitaStory"

# ---- timing ---------------------------------------------------------------------------------
_aspects = {}


def aspect(src):
    if src not in _aspects:
        out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                       "stream=width,height", "-of", "csv=p=0", os.path.join(OUT, src)], text=True)
        w, h = (int(x) for x in out.strip().split(","))
        _aspects[src] = w / h
    return _aspects[src]


def kind(item):
    if item["kind"]:
        return item["kind"]
    return "wide" if aspect(item["src"]) > 1.1 else "photo"


def frames(sec):
    return round(sec * FPS)


budget = frames(TOTAL - INTRO - OUTRO)
shots = [s for _, _, ss in SCENES for s in ss]
def weight(item):
    return WEIGHT[kind(item)] * (CAP_BONUS if item.get("cap") else 1.0)


unit = budget / sum(weight(s) for s in shots)
for s in shots:
    s["frames"] = max(frames(1.0), round(weight(s) * unit))
shots[-1]["frames"] += budget - sum(s["frames"] for s in shots)  # land exactly on TOTAL

# ---- transitions ----------------------------------------------------------------------------
# Each transition has an outgoing half (on the shot that leaves) and an incoming half (on the
# shot that arrives, which sits on top). Both run over [t, t + OVERLAP].
T = OVERLAP


def t_out(kind_, sel, t):
    if kind_ in ("zoom", "leak"):
        return f'    tl.to("{sel}", {{ scale: 1.35, filter: "blur(14px)", duration: {T}, ease: "power2.in" }}, {t:.4f});'
    if kind_ == "zoom-out":
        return f'    tl.to("{sel}", {{ scale: 0.8, filter: "blur(12px)", duration: {T}, ease: "power2.in" }}, {t:.4f});'
    if kind_.startswith("whip"):
        x, y = {"whip-left": (-W, 0), "whip-right": (W, 0), "whip-up": (0, -H)}[kind_]
        return f'    tl.to("{sel}", {{ x: {x}, y: {y}, filter: "blur(18px)", duration: {T}, ease: "power2.in" }}, {t:.4f});'
    if kind_ == "spin":
        return f'    tl.to("{sel}", {{ rotation: 22, scale: 1.45, filter: "blur(16px)", duration: {T}, ease: "power2.in" }}, {t:.4f});'
    if kind_ in ("iris", "flash"):
        return f'    tl.to("{sel}", {{ scale: 1.12, duration: {T}, ease: "power1.in" }}, {t:.4f});'
    raise ValueError(kind_)


def t_in(kind_, sel, t, sid):
    if kind_ in ("zoom", "leak"):
        js = (f'    tl.fromTo("{sel}", {{ scale: 1.5, opacity: 0, filter: "blur(14px)" }}, '
              f'{{ scale: 1, opacity: 1, filter: "blur(0px)", duration: {T}, ease: "power2.out" }}, {t:.4f});')
        if kind_ == "leak":
            a = max(0.0, t - T * 0.5)
            js += (f'\n    tl.set("#{sid}-leak", {{ x: -1700 }}, {a:.4f});'
                   f'\n    tl.to("#{sid}-leak", {{ x: 900, duration: {T * 2:.2f}, ease: "power1.inOut" }}, {a:.4f});'
                   f'\n    tl.to("#{sid}-leak", {{ opacity: 0.95, duration: {T * 0.8:.2f}, ease: "power2.out", yoyo: true, repeat: 1 }}, {a:.4f});')
        return js
    if kind_ == "zoom-out":
        return (f'    tl.fromTo("{sel}", {{ scale: 1.6, opacity: 0, filter: "blur(12px)" }}, '
                f'{{ scale: 1, opacity: 1, filter: "blur(0px)", duration: {T}, ease: "power3.out" }}, {t:.4f});')
    if kind_.startswith("whip"):
        x, y = {"whip-left": (W, 0), "whip-right": (-W, 0), "whip-up": (0, H)}[kind_]
        return (f'    tl.fromTo("{sel}", {{ x: {x}, y: {y}, filter: "blur(18px)" }}, '
                f'{{ x: 0, y: 0, filter: "blur(0px)", duration: {T}, ease: "power2.out" }}, {t:.4f});')
    if kind_ == "spin":
        return (f'    tl.fromTo("{sel}", {{ rotation: -22, scale: 1.45, opacity: 0, filter: "blur(16px)" }}, '
                f'{{ rotation: 0, scale: 1, opacity: 1, filter: "blur(0px)", duration: {T}, ease: "power2.out" }}, {t:.4f});')
    if kind_ == "iris":
        return (f'    tl.fromTo("{sel}", {{ clipPath: "circle(0% at 50% 46%)" }}, '
                f'{{ clipPath: "circle(74% at 50% 46%)", duration: {T * 1.1:.3f}, ease: "power2.inOut" }}, {t:.4f});')
    if kind_ == "flash":
        return (f'    tl.fromTo("{sel}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.06, ease: "none" }}, {t + T * 0.35:.4f});'
                f'\n    tl.to("#{sid}-flash", {{ opacity: 0.85, duration: {T * 0.4:.2f}, ease: "power2.out" }}, {t:.4f});'
                f'\n    tl.to("#{sid}-flash", {{ opacity: 0, duration: {T * 0.9:.2f}, ease: "power2.in" }}, {t + T * 0.4:.4f});')
    raise ValueError(kind_)


# Assign one transition to every boundary in the reel: intro -> first shot -> ... -> outro.
seq = [("intro", None)] + [(sid, s) for sid, _, ss in SCENES for s in ss] + [("outro", None)]
kinds, ti, ci = [], 0, 0
for i in range(1, len(seq)):
    if seq[i][0] != seq[i - 1][0]:
        kinds.append(CHAPTER_TRANSITIONS[ci % len(CHAPTER_TRANSITIONS)])
        ci += 1
    else:
        kinds.append(TRANSITIONS[ti % len(TRANSITIONS)])
        ti += 1
# kinds[k] is the boundary between seq[k] and seq[k+1]
for k, (sid, s) in enumerate(seq):
    if s is not None:
        s["in_kind"] = kinds[k - 1]
        s["out_kind"] = kinds[k]
INTRO_OUT = kinds[0]
OUTRO_IN = kinds[-1]

# ---- markup helpers -------------------------------------------------------------------------
SHOT_CSS = """
    #root { position: absolute; inset: 0; overflow: hidden; font-family: "Montserrat", sans-serif; }
    #root .shot { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    #root .tx, #root .kb { position: absolute; left: 0; top: 0; width: 100%; height: 100%; }
    #root .tx { overflow: hidden; }
    #root .kb img, #root .kb video { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }
    #root .scrim { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;
      background: linear-gradient(180deg, rgba(7,8,11,0.25) 0%, rgba(7,8,11,0) 16%, rgba(7,8,11,0) 50%, rgba(7,8,11,0.6) 74%, rgba(7,8,11,0.75) 100%); }
    #root .flash { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; background: #fff4e3; opacity: 0; }
    #root .leak { position: absolute; left: 0; top: 0; width: 1700px; height: 1920px; opacity: 0; mix-blend-mode: screen;
      background: radial-gradient(ellipse 45% 60% at 50% 45%, rgba(255,190,110,0.95), rgba(255,120,60,0.55) 45%, rgba(255,90,40,0) 75%); }
    #root .label { position: absolute; left: 120px; top: 1170px; height: 44px; display: flex; align-items: center; gap: 22px;
      color: #ffffff; font-size: 36px; letter-spacing: 0.3em; text-transform: uppercase; white-space: nowrap;
      text-shadow: 0 2px 16px rgba(0,0,0,0.65); transform-origin: left center; }
    #root .label .rule { width: 64px; height: 3px; background: linear-gradient(90deg, #ffc27a, #ff8a3d); transform-origin: left center; }
    #root .sticker { position: absolute; left: 160px; top: 380px; padding: 14px 28px; border-radius: 18px;
      font-family: "Poppins", sans-serif; font-weight: 700; font-size: 42px; line-height: 1.15; white-space: nowrap;
      box-shadow: 0 14px 36px rgba(0,0,0,0.35); transform-origin: 30% 50%; }
    #root .credit { position: absolute; left: 120px; top: 1262px; font-size: 22px; color: rgba(255,255,255,0.78);
      letter-spacing: 0.02em; text-shadow: 0 1px 6px rgba(0,0,0,0.7); white-space: nowrap; }
    #root .sticker.s0 { background: #ffffff; color: #15161a; }
    #root .sticker.s1 { background: linear-gradient(135deg, #ffd08a, #ff8a3d); color: #2a1206; }
    #root .sticker.s2 { background: #15161a; color: #ffd9a6; }
    #root .splitbg { background: linear-gradient(160deg, #ffb35c, #ff6a3d); }
    #root .half { position: absolute; left: 0; width: 1080px; height: 960px; overflow: hidden; }
    #root .bar { position: absolute; left: 0; top: 952px; width: 1080px; height: 16px; background: #fff3e2;
      box-shadow: 0 0 24px rgba(255,170,90,0.8); }
    #root .tag { position: absolute; left: 120px; padding: 10px 24px; border-radius: 999px; background: #ffffff; color: #15161a;
      font-family: "Poppins", sans-serif; font-weight: 700; font-size: 38px; text-transform: uppercase; letter-spacing: 0.08em;
      box-shadow: 0 10px 28px rgba(0,0,0,0.35); white-space: nowrap; }
    #root .tag.b { background: #ff8a3d; color: #1c0b03; }
    #root .board { background: radial-gradient(ellipse at 50% 35%, #fbefdd 0%, #f0d2ab 60%, #e2b585 100%); }
    #root .pol { position: absolute; width: 520px; height: 690px; background: #fffdf8; border-radius: 6px;
      box-shadow: 0 24px 50px rgba(60,30,10,0.35); }
    #root .kb .pol img { position: absolute; left: 22px; top: 22px; width: 476px; height: 560px; object-fit: cover; }
    #root .countbg { background: radial-gradient(ellipse at 50% 45%, #3a1a0a 0%, #160b06 55%, #07080b 100%); }
    #root .cstack { position: absolute; left: 120px; top: 288px; width: 840px; height: 960px; display: flex;
      flex-direction: column; align-items: center; justify-content: center; }
    #root .ckicker { color: #f1e3cf; font-size: 34px; letter-spacing: 0.3em; text-transform: uppercase; margin-bottom: 20px; padding-left: 0.3em; }
    #root .digits { display: flex; gap: 6px; height: 360px; }
    #root .dcol { width: 175px; height: 360px; overflow: hidden; }
    #root .dstrip { display: flex; flex-direction: column; }
    #root .dstrip span { display: block; height: 360px; line-height: 360px; text-align: center;
      font-family: "Playfair Display", serif; font-weight: 700; font-size: 280px; color: #ffc98a;
      text-shadow: 0 0 22px rgba(255,170,90,0.75), 0 0 60px rgba(255,120,50,0.5); }
    #root .cword { margin-top: 30px; padding: 14px 34px; border-radius: 999px; background: #fff3e2; color: #2a1206;
      font-family: "Poppins", sans-serif; font-weight: 700; font-size: 48px; text-transform: uppercase; letter-spacing: 0.1em; }
"""


def media_tag(item, mid, start, dur, lane):
    style = ""
    if item.get("pan"):
        style = f' style="object-position:{item["pan"][0]}% 50%;"'
    elif item.get("pos") is not None or item.get("y") is not None:
        px = item["pos"] if item.get("pos") is not None else 50
        py = item["y"] if item.get("y") is not None else 50
        style = f' style="object-position:{px}% {py}%;"'
    if item["tag"] == "img":
        return (f'<img id="{mid}" class="clip" data-start="{start:g}" data-duration="{dur:g}" '
                f'data-track-index="{lane}" src="{item["src"]}"{style} alt="" />')
    ms = f' data-media-start="{item["start"]:g}"' if item.get("start") else ""
    return (f'<video id="{mid}" class="clip" data-start="{start:g}" data-duration="{dur:g}" data-track-index="{lane}"{ms} '
            f'muted playsinline src="{item["src"]}"{style}></video>')


def shot_html(fid, item, start, dur, lane):
    return (f'    <div id="{fid}" class="shot" data-layout-allow-overflow><div id="{fid}-tx" class="tx">'
            f'<div id="{fid}-kb" class="kb">{media_tag(item, f"{fid}-m", round(start, 4), round(dur, 4), lane)}</div></div></div>')


_cap_n = [0]


def sticker(fid, item, s):
    """Returns (html, js) for the shot's caption sticker, which pops in after the transition."""
    if not item.get("cap"):
        return "", []
    n = _cap_n[0]
    _cap_n[0] += 1
    r = (-4, 3, -2, 5)[n % 4]
    h = f'<div id="{fid}-cap" class="sticker s{n % 3}">{item["cap"]}</div>'
    js = [f'    tl.fromTo("#{fid}-cap", {{ scale: 0, rotation: {r - 14} }}, '
          f'{{ scale: 1, rotation: {r}, duration: 0.5, ease: "back.out(2.6)" }}, {s + T + 0.05:.4f});']
    return h, js


def special(fid, item, s, d):
    """Inner html and js for split, polaroid and counter shots."""
    a, js = [], []
    if item["tag"] == "split":
        a.append(f'<div id="{fid}-a" class="half" style="top:0">{media_tag(item["a"], f"{fid}-ma", round(s, 4), round(d + T, 4), 2)}</div>')
        a.append(f'<div id="{fid}-b" class="half" style="top:960px">{media_tag(item["b"], f"{fid}-mb", round(s, 4), round(d + T, 4), 3)}</div>')
        a.append(f'<div id="{fid}-bar" class="bar"></div>')
        a.append(f'<div id="{fid}-la" class="tag" style="top:820px">{item["la"]}</div>')
        a.append(f'<div id="{fid}-lb" class="tag b" style="top:1000px">{item["lb"]}</div>')
        js += [f'    tl.fromTo("#{fid}-a", {{ x: -1080 }}, {{ x: 0, duration: 0.5, ease: "power3.out" }}, {s + 0.1:.4f});',
               f'    tl.fromTo("#{fid}-b", {{ x: 1080 }}, {{ x: 0, duration: 0.5, ease: "power3.out" }}, {s + 0.22:.4f});',
               f'    tl.fromTo("#{fid}-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "expo.out" }}, {s + 0.45:.4f});',
               f'    tl.fromTo("#{fid}-la", {{ scale: 0, rotation: -18 }}, {{ scale: 1, rotation: -4, duration: 0.45, ease: "back.out(2.6)" }}, {s + 0.6:.4f});',
               f'    tl.fromTo("#{fid}-lb", {{ scale: 0, rotation: 18 }}, {{ scale: 1, rotation: 3, duration: 0.45, ease: "back.out(2.6)" }}, {s + 0.75:.4f});']
        return "splitbg", "".join(a), js
    if item["tag"] == "pola":
        spots = [(90, 400, -8), (470, 720, 7), (150, 1060, -3)]
        for k, (it, (x, y, r)) in enumerate(zip(item["items"], spots)):
            a.append(f'<div id="{fid}-p{k + 1}" class="pol" style="left:{x}px;top:{y}px;">'
                     f'{media_tag(it, f"{fid}-mp{k + 1}", round(s, 4), round(d + T, 4), 2 + k)}</div>')
            js.append(f'    tl.fromTo("#{fid}-p{k + 1}", {{ y: -1500, rotation: {r * 3} }}, '
                      f'{{ y: 0, rotation: {r}, duration: 0.6, ease: "back.out(1.5)" }}, {s + 0.25 + k * 0.38:.4f});')
        return "board", "".join(a), js
    if item["tag"] == "count":
        digits = str(item["n"])
        cols = []
        for k, ch in enumerate(digits):
            loops = k + 1
            strip = "".join(f"<span>{i % 10}</span>" for i in range(10 * loops))
            cols.append(f'<div class="dcol"><div id="{fid}-d{k}" class="dstrip">{strip}</div></div>')
            target = 10 * (loops - 1) + int(ch)
            js.append(f'    tl.fromTo("#{fid}-d{k}", {{ y: 0 }}, {{ y: {-360 * target}, duration: 1.7, ease: "power3.out" }}, {s + 0.2:.4f});')
        a.append(f'<div id="{fid}-cs" class="cstack"><div id="{fid}-ck" class="ckicker">{item["kicker"]}</div>'
                 f'<div id="{fid}-dg" class="digits" data-layout-ignore>{"".join(cols)}</div>'
                 f'<div id="{fid}-cw" class="cword">{item["word"]}</div></div>')
        js += [f'    tl.fromTo("#{fid}-ck", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {s + 0.2:.4f});',
               f'    tl.fromTo("#{fid}-cw", {{ scale: 0, rotation: -10 }}, {{ scale: 1, rotation: -3, duration: 0.5, ease: "back.out(2.8)" }}, {s + 1.85:.4f});']
        return "countbg", "".join(a), js
    raise ValueError(item["tag"])


def wrap(sid, dur, html, js, css="", variables=None):
    v = f"\n    data-composition-variables='{json.dumps(variables)}'" if variables else ""
    return f"""<template>
  <style>{SHOT_CSS}{css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}" data-duration="{dur:.4f}"{v}>
{chr(10).join(html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""


def build_scene(sid, chapter, items):
    """Returns (nominal duration, html). The composition runs OVERLAP longer so its last shot
    stays under the next chapter's incoming transition."""
    html = []
    js = [f'    tl.set("#{sid}-leak", {{ x: -1700, opacity: 0 }}, 0);', f'    tl.set("#{sid}-flash", {{ opacity: 0 }}, 0);']
    t = 0
    for i, item in enumerate(items):
        n = i + 1
        s, d = t / FPS, item["frames"] / FPS
        fid = f"{sid}-s{n}"
        cap_html, cap_js = sticker(fid, item, s)
        if item["tag"] in ("img", "video"):
            sh = shot_html(fid, item, s, d + T, i % 2)
        else:
            bg, inner, sjs = special(fid, item, s, d)
            sh = (f'    <div id="{fid}" class="shot" data-layout-allow-overflow data-layout-allow-overlap>'
                  f'<div id="{fid}-tx" class="tx {bg}"><div id="{fid}-kb" class="kb">{inner}</div></div></div>')
            js.extend(sjs)
        if item.get("credit"):
            cap_html += f'<div id="{fid}-credit" class="credit" data-layout-ignore>Photo: {item["credit"]}</div>'
        if cap_html:
            k = sh.rindex("</div></div>")
            sh = sh[:k] + cap_html + sh[k:]
        html.append(sh)
        js.extend(cap_js)
        if i == 0:
            js.append(t_in(item["in_kind"], f"#{fid}-tx", 0, sid))
        else:
            js.append(t_in(item["in_kind"], f"#{fid}-tx", s, sid))
        js.append(t_out(item["out_kind"], f"#{fid}-tx", s + d))
        js.append(f'    tl.fromTo("#{fid}-kb", {{ scale: 1 }}, {{ scale: 1.06, duration: {d + T:.4f}, ease: "none" }}, {s:.4f});')
        if item.get("pan"):
            a, b = item["pan"]
            js.append(f'    tl.fromTo("#{fid}-m", {{ objectPosition: "{a}% 50%" }}, '
                      f'{{ objectPosition: "{b}% 50%", duration: {d:.4f}, ease: "sine.inOut" }}, {s:.4f});')
        t += item["frames"]
    dur = t / FPS
    html.append(f'    <div id="{sid}-scrim" class="scrim"></div>')
    html.append(f'    <div id="{sid}-label" class="label"><div id="{sid}-rule" class="rule"></div>'
                f'<span id="{sid}-label-text" data-var-text="chapter">{chapter}</span></div>')
    html.append(f'    <div id="{sid}-flash" class="flash" data-layout-ignore></div>')
    html.append(f'    <div id="{sid}-leak" class="leak" data-layout-ignore data-layout-allow-overflow></div>')
    js.append(f'    tl.fromTo("#{sid}-label", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(2.2)" }}, {T + 0.1:.2f});')
    js.append(f'    tl.fromTo("#{sid}-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "expo.out" }}, {T + 0.3:.2f});')
    js.append(f'    tl.to("#{sid}-label", {{ opacity: 0, x: -40, duration: 0.25, ease: "power3.in" }}, {dur - 0.3:.4f});')
    variables = [{"id": "chapter", "type": "string", "label": "Chapter label", "default": chapter}]
    return dur, wrap(sid, dur + T, html, js, variables=variables)


# ---- title scenes ---------------------------------------------------------------------------
TITLE_CSS = """
    #root .dim { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;
      background: linear-gradient(180deg, rgba(7,8,11,0.3) 0%, rgba(7,8,11,0.55) 30%, rgba(7,8,11,0.6) 60%, rgba(7,8,11,0.35) 100%); }
    #root .glow { position: absolute; left: 40px; top: 430px; width: 1000px; height: 700px; border-radius: 50%;
      background: radial-gradient(closest-side, rgba(255,154,74,0.28), rgba(255,120,50,0.08) 60%, rgba(7,8,11,0) 100%); }
    #root .embers { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    #root .ember { position: absolute; border-radius: 50%; background: #ffb46a; box-shadow: 0 0 8px #ff9a4a; }
    #root .stack { position: absolute; left: 120px; top: 288px; width: 660px; height: 960px; display: flex;
      flex-direction: column; align-items: center; justify-content: center; text-align: center; }
    #root .kicker { color: #e3e5e9; font-size: 30px; letter-spacing: 0.4em; text-transform: uppercase; margin-bottom: 28px;
      padding-left: 0.4em; text-shadow: 0 2px 14px rgba(0,0,0,0.6); }
    #root .title { font-family: "Playfair Display", serif; font-weight: 700; font-size: 172px; line-height: 1;
      letter-spacing: 0.06em; color: #f8f3ea; padding-left: 0.06em; text-shadow: 0 6px 40px rgba(0,0,0,0.45); }
    #root .title span { display: inline-block; }
    #root .trule { width: 420px; height: 3px; margin: 34px 0 30px;
      background: linear-gradient(90deg, rgba(255,194,122,0), #ffc27a 30%, #ff8a3d 70%, rgba(255,138,61,0)); }
    #root .sub { font-size: 38px; letter-spacing: 0.12em; text-transform: uppercase; color: #ffc98a; padding-left: 0.12em;
      white-space: nowrap; text-shadow: 0 2px 10px rgba(0,0,0,0.55); }
    #root .sub span { display: inline-block; margin: 0 0.12em; }
    #root .closing { margin-top: 44px; color: #f1f2f4; font-size: 38px; letter-spacing: 0.04em; text-shadow: 0 2px 14px rgba(0,0,0,0.6); }
"""
GLOW_OFF = '"0 0 0px rgba(255,170,90,0), 0 0 0px rgba(255,140,60,0), 0 2px 10px rgba(0,0,0,0.55)"'
GLOW_ON = '"0 0 16px rgba(255,170,90,0.85), 0 0 46px rgba(255,140,60,0.55), 0 2px 10px rgba(0,0,0,0.55)"'


def embers(sid, seed, count=28):
    s = seed
    def rnd():
        nonlocal s
        s = (s * 1103515245 + 12345) % 2147483648
        return s / 2147483648
    out = []
    for _ in range(count):
        x, y = round(60 + rnd() * 960), round(500 + rnd() * 1300)
        size, op, rise = round(2.5 + rnd() * 3.5, 1), round(0.3 + rnd() * 0.5, 2), round(160 + rnd() * 320)
        out.append(f'<div class="ember" data-rise="{rise}" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px;opacity:{op};"></div>')
    return f'    <div id="{sid}-embers" class="embers" data-layout-ignore>' + "".join(out) + "</div>"


def ember_drift(sid, dur):
    return f"""    document.querySelectorAll("#{sid}-embers .ember").forEach((el) => {{
      tl.fromTo(el, {{ y: 0 }}, {{ y: -Number(el.dataset.rise), duration: {dur}, ease: "none" }}, 0);
    }});"""


def subwords(sid):
    return "".join(f'<span id="{sid}-w{i + 1}">{w}</span>' for i, w in enumerate(["1st", "Year", "Anniversary"]))


def intro(d):
    letters = "".join(f'<span id="intro-k{i + 1}">{c}</span>' for i, c in enumerate("KASOL"))
    x = d - 0.8
    html = [shot_html("intro-bg", INTRO_BG, 0, d + T, 0),
            '    <div id="intro-dim" class="dim"></div>', '    <div id="intro-glow" class="glow"></div>',
            embers("intro", 7),
            f'''    <div id="intro-stack" class="stack" data-hold>
      <div id="intro-kicker" class="kicker" data-var-text="kicker">Parvati Valley</div>
      <h1 id="intro-title" class="title">{letters}</h1>
      <div id="intro-rule" class="trule"></div>
      <div id="intro-sub" class="sub">{subwords("intro")}</div>
    </div>''']
    js = [ember_drift("intro", d + T),
          f'    tl.fromTo("#intro-bg-kb", {{ scale: 1.0 }}, {{ scale: 1.08, duration: {d + T:g}, ease: "none" }}, 0);',
          '    tl.fromTo("#intro-glow", { opacity: 0.4 }, { opacity: 1, duration: 2.2, ease: "power2.inOut" }, 0);',
          '    tl.fromTo("#intro-kicker", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.5, ease: "power4.out" }, 0.4);',
          '    tl.fromTo("#intro-title span", { opacity: 0.3, y: 40, filter: "blur(4px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.7, ease: "back.out(1.6)", stagger: 0.09 }, 0.7);',
          '    tl.fromTo("#intro-rule", { scaleX: 0 }, { scaleX: 1, duration: 0.9, ease: "expo.out" }, 1.6);',
          '    tl.fromTo("#intro-sub span", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power4.out", stagger: 0.09 }, 1.9);',
          f'    tl.fromTo("#intro-sub", {{ textShadow: {GLOW_OFF} }}, {{ textShadow: {GLOW_ON}, duration: 1.4, ease: "power2.inOut" }}, 2.2);',
          f'    tl.to(["#intro-kicker", "#intro-title span", "#intro-rule", "#intro-sub span"], {{ opacity: 0, filter: "blur(8px)", duration: 0.25, ease: "power3.in", stagger: 0.04 }}, {x:g});',
          f'    tl.to(["#intro-glow", "#intro-embers", "#intro-dim"], {{ opacity: 0, duration: 0.6, ease: "power2.in" }}, {x:g});',
          t_out(INTRO_OUT, "#intro-bg-tx", d)]
    variables = [{"id": "kicker", "type": "string", "label": "Kicker", "default": "Parvati Valley"}]
    return wrap("intro", d + T, html, js, TITLE_CSS, variables)


def outro(d):
    html = ['    <div id="outro-stage" class="shot">',
            shot_html("outro-bg", OUTRO_BG, 0, d, 0),
            '    <div id="outro-dim" class="dim"></div>', '    <div id="outro-glow" class="glow"></div>',
            embers("outro", 23),
            f'''    <div id="outro-stack" class="stack" data-hold>
      <h1 id="outro-title" class="title">KASOL</h1>
      <div id="outro-rule" class="trule"></div>
      <div id="outro-sub" class="sub">{subwords("outro")}</div>
      <div id="outro-closing" class="closing" data-var-text="closing">{CLOSING}</div>
    </div>''',
            '    <div id="outro-flash" class="flash" data-layout-ignore></div>',
            '    <div id="outro-leak" class="leak" data-layout-ignore data-layout-allow-overflow></div>',
            '    </div>']
    js = ['    tl.set("#outro-leak", { x: -1700, opacity: 0 }, 0);', '    tl.set("#outro-flash", { opacity: 0 }, 0);',
          ember_drift("outro", d),
          t_in(OUTRO_IN, "#outro-bg-tx", 0, "outro"),
          f'    tl.fromTo("#outro-bg-kb", {{ scale: 1.0 }}, {{ scale: 1.07, duration: {d:g}, ease: "none" }}, 0);',
          '    tl.fromTo("#outro-dim", { opacity: 0 }, { opacity: 1, duration: 1.0, ease: "power2.inOut" }, 0.6);',
          '    tl.fromTo("#outro-glow", { opacity: 0 }, { opacity: 1, duration: 1.6, ease: "power2.inOut" }, 0.8);',
          '    tl.fromTo("#outro-title", { opacity: 0, scale: 0.85, filter: "blur(8px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.8, ease: "back.out(1.6)" }, 1.0);',
          '    tl.fromTo("#outro-rule", { scaleX: 0 }, { scaleX: 1, duration: 0.9, ease: "expo.out" }, 1.6);',
          '    tl.fromTo("#outro-sub span", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power4.out", stagger: 0.09 }, 1.9);',
          f'    tl.fromTo("#outro-sub", {{ textShadow: {GLOW_OFF} }}, {{ textShadow: {GLOW_ON}, duration: 1.4, ease: "power2.inOut" }}, 2.2);',
          '    tl.fromTo("#outro-closing", { opacity: 0, y: 20, filter: "blur(6px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.5, ease: "back.out(1.8)" }, 3.0);',
          f'    tl.to("#outro-stage", {{ opacity: 0, duration: 2.0, ease: "power2.inOut" }}, {d - 2.1:g});']
    variables = [{"id": "closing", "type": "string", "label": "Closing line", "default": CLOSING}]
    return wrap("outro", d, html, js, TITLE_CSS, variables)


# ---- write ----------------------------------------------------------------------------------
os.makedirs(f"{OUT}/compositions", exist_ok=True)
for f in glob.glob(f"{OUT}/compositions/*.html"):
    os.remove(f)

files = [("intro", INTRO, INTRO + T, intro(INTRO))]
for sid, chapter, items in SCENES:
    d, html = build_scene(sid, chapter, items)
    files.append((sid, d, d + T, html))
files.append(("outro", OUTRO, OUTRO, outro(OUTRO)))

t, hosts = 0.0, []
for z, (sid, d, slot, html) in enumerate(files):
    with open(f"{OUT}/compositions/{sid}.html", "w") as fh:
        fh.write(html)
    hosts.append(f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                 f'data-start="{t:.4f}" data-duration="{slot:.4f}" data-track-index="{1 + z % 2}" data-track-kind="graphics" '
                 f'data-width="{W}" data-height="{H}" style="z-index:{z + 1}"></div>')
    t += d

music = sorted(glob.glob(f"{OUT}/assets/audio/music.*"))
audio = ""
if music:
    rel = os.path.relpath(music[0], OUT)
    audio = (f'      <audio id="music" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="3" '
             f'data-volume="0.8" data-fade-in="0.5" data-fade-out="2.5" src="{rel}"></audio>\n')

index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #07080b; }}
      #root {{ width: 100%; height: 100%; }}
      #ground {{ position: absolute; inset: 0; background: #07080b; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
      <div id="ground"></div>
{chr(10).join(hosts)}
{audio}    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
with open(f"{OUT}/index.html", "w") as fh:
    fh.write(index)
print(f"wrote {len(files)} scenes, {len(shots)} shots, {t:.3f} s, unit {unit / FPS:.2f} s, "
      f"music: {os.path.basename(music[0]) if music else 'none'}")
