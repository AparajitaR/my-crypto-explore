"""Writes index.html and compositions/*.html for the Kasol anniversary reel (1080x1920).

Run from the project folder:  python3 tools/generate.py
Edit SCENES to add, remove or reorder shots. Shot lengths are worked out so the reel
lasts exactly TOTAL seconds: photos get one unit, clips and landscape photos more.
Music: put the track at assets/audio/music.mp3 (or .m4a / .wav) and run this again.
Hand edits to index.html or compositions/ are overwritten when this runs.
"""
import glob, json, os, subprocess

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P, V = "assets/photos/", "assets/video/"
W, H, FPS, TOTAL = 1080, 1920, 30, 90
INTRO, OUTRO = 6.0, 7.5
WEIGHT = {"photo": 1.0, "video": 1.7, "wide": 1.7, "hero": 1.9}


def ph(name, pos=None, pan=None, kind=None):
    """A photo. pos: horizontal focus in % for wide photos; pan: (from %, to %) to sweep across one."""
    return {"tag": "img", "src": P + name + ".jpg", "pos": pos, "pan": pan, "kind": kind}


def vd(name, start=0.0):
    return {"tag": "video", "src": V + name + ".mp4", "start": start, "kind": "video"}


SCENES = [
    ("morning", "The morning", [
        ph("breakfast", pos=58), ph("scooter-valley", pos=70), ph("him-river-sun"), ph("her-river-sun"),
        ph("him-beer-cafe", pos=65), ph("cafe-food"), ph("her-cafe", pos=40),
    ]),
    ("golden", "Golden hour", [vd("walk-to-sunset"), vd("valley-sunset", start=6.0), vd("sun-rays")]),
    ("sunset", "Sunset", [
        ph("road-walk"), vd("her-on-road"), ph("sunset-view", pos=62), ph("her-photographing-sunset", pos=55),
        ph("sunset-fire"), ph("dusk-pines", pos=35),
    ]),
    ("manikaran", "Manikaran", [
        ph("gurudwara", pan=(30, 70)), ph("gurudwara-front", pos=40), ph("manikaran-temple-river", pos=40),
        ph("hot-spring-pool", pos=70), vd("river-run"), vd("manikaran-river"), ph("langar-thali"),
        ph("her-on-bridge", pos=52), ph("couple-selfie-manikaran", pos=43), ph("him-on-bridge", pos=55),
        ph("her-gurudwara-railing", pos=62), ph("him-bridge-walk", pos=56), ph("her-peace-gurudwara", pos=60),
        ph("him-gurudwara-railing", pos=55),
    ]),
    ("afternoons", "Slow afternoons", [
        ph("her-heart", pos=45), ph("her-river-dusk", pos=45), ph("him-river-rock", pos=58),
        ph("couple-selfie-cafe", pan=(12, 72)),
    ]),
    ("night", "After dark", [
        ph("enfield-night", pan=(0, 100)), ph("snooker-him", pos=40), ph("snooker-her", pos=55),
        ph("apple-mirror"), ph("couple-cosy-night", pos=26), ph("room-mirror"),
    ]),
    ("oneyear", "One year", [
        ph("anniversary-candles", kind="hero"), ph("anniversary-cake", kind="hero"), ph("story-coaster", kind="hero"),
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
unit = budget / sum(WEIGHT[kind(s)] for s in shots)
for s in shots:
    s["frames"] = max(frames(0.9), round(WEIGHT[kind(s)] * unit))
shots[-1]["frames"] += budget - sum(s["frames"] for s in shots)  # land exactly on TOTAL

# ---- markup helpers -------------------------------------------------------------------------
SHOT_CSS = """
    #root { position: absolute; inset: 0; overflow: hidden; background: #07080b; font-family: "Montserrat", sans-serif; }
    #root .shot { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: hidden; }
    #root .kb { position: absolute; left: 0; top: 0; width: 100%; height: 100%; }
    #root .kb img, #root .kb video { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }
    #root .scrim { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;
      background: linear-gradient(180deg, rgba(7,8,11,0.25) 0%, rgba(7,8,11,0) 16%, rgba(7,8,11,0) 50%, rgba(7,8,11,0.72) 74%, rgba(7,8,11,0.82) 100%); }
    #root .label { position: absolute; left: 120px; top: 1170px; height: 40px; display: flex; align-items: center; gap: 22px;
      color: #eef0f3; font-size: 34px; letter-spacing: 0.32em; text-transform: uppercase; white-space: nowrap;
      text-shadow: 0 2px 14px rgba(0,0,0,0.6); }
    #root .label .rule { width: 64px; height: 3px; background: linear-gradient(90deg, #ffc27a, #ff8a3d); transform-origin: left center; }
"""


def media_tag(item, mid, start, dur, lane):
    style = ""
    if item.get("pan"):
        style = f' style="object-position:{item["pan"][0]}% 50%;"'
    elif item.get("pos") is not None:
        style = f' style="object-position:{item["pos"]}% 50%;"'
    if item["tag"] == "img":
        return (f'<img id="{mid}" class="clip" data-start="{start:g}" data-duration="{dur:g}" '
                f'data-track-index="{lane}" src="{item["src"]}"{style} alt="" />')
    ms = f' data-media-start="{item["start"]:g}"' if item.get("start") else ""
    return (f'<video id="{mid}" class="clip" data-start="{start:g}" data-duration="{dur:g}" data-track-index="{lane}"{ms} '
            f'muted playsinline src="{item["src"]}"{style}></video>')


def build_scene(sid, chapter, items):
    html, js = [], []
    t = 0
    for i, item in enumerate(items):
        n = i + 1
        s, d = t / FPS, item["frames"] / FPS
        fid = f"{sid}-s{n}"
        html.append(f'    <div id="{fid}" class="shot" data-layout-allow-overflow><div id="{fid}-kb" class="kb">'
                    f'{media_tag(item, f"{fid}-m", round(s, 4), round(d, 4), i % 2)}</div></div>')
        if i == 0:  # chapter opens with a whip
            js.append(f'    tl.fromTo("#{fid}-kb", {{ x: 160, filter: "blur(16px)" }}, '
                      f'{{ x: 0, filter: "blur(0px)", duration: 0.32, ease: "power3.out" }}, {s:.4f});')
        else:  # hard cut that lands slightly large and settles
            js.append(f'    tl.fromTo("#{fid}-kb", {{ scale: 1.07 }}, {{ scale: 1, duration: 0.55, ease: "expo.out" }}, {s:.4f});')
        if item.get("pan"):
            a, b = item["pan"]
            js.append(f'    tl.fromTo("#{fid}-m", {{ objectPosition: "{a}% 50%" }}, '
                      f'{{ objectPosition: "{b}% 50%", duration: {d:.4f}, ease: "sine.inOut" }}, {s:.4f});')
        t += item["frames"]
    dur = t / FPS
    html.append(f'    <div id="{sid}-scrim" class="scrim"></div>')
    html.append(f'    <div id="{sid}-label" class="label"><div id="{sid}-rule" class="rule"></div>'
                f'<span id="{sid}-label-text" data-var-text="chapter">{chapter}</span></div>')
    js.append(f'    tl.fromTo("#{sid}-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.7, ease: "expo.out" }}, 0.3);')
    js.append(f'    tl.fromTo("#{sid}-label-text", {{ opacity: 0, filter: "blur(8px)" }}, '
              f'{{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 0.5);')
    js.append(f'    tl.to("#{sid}-label", {{ opacity: 0, filter: "blur(8px)", duration: 0.2, ease: "power3.in" }}, {dur - 0.35:.4f});')
    variables = json.dumps([{"id": "chapter", "type": "string", "label": "Chapter label", "default": chapter}])
    return dur, f"""<template>
  <style>{SHOT_CSS}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}" data-duration="{dur:.4f}"
    data-composition-variables='{variables}'>
{chr(10).join(html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""


# ---- title scenes ---------------------------------------------------------------------------
TITLE_CSS = """
    #root .dim { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;
      background: linear-gradient(180deg, rgba(7,8,11,0.35) 0%, rgba(7,8,11,0.62) 30%, rgba(7,8,11,0.66) 60%, rgba(7,8,11,0.4) 100%); }
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
    #root .sub { font-size: 38px; letter-spacing: 0.12em; text-transform: uppercase; color: #ffc98a; padding-left: 0.14em;
      white-space: nowrap; }
    #root .sub span { display: inline-block; margin: 0 0.12em; }
    #root .closing { margin-top: 44px; color: #f1f2f4; font-size: 38px; letter-spacing: 0.04em; text-shadow: 0 2px 14px rgba(0,0,0,0.6); }
"""
GLOW_OFF = '"0 0 0px rgba(255,170,90,0), 0 0 0px rgba(255,140,60,0)"'
GLOW_ON = '"0 0 16px rgba(255,170,90,0.85), 0 0 46px rgba(255,140,60,0.55)"'


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
    return f'<div id="{sid}-embers" class="embers" data-layout-ignore>' + "".join(out) + "</div>"


def ember_drift(sid, dur):
    return f"""    document.querySelectorAll("#{sid}-embers .ember").forEach((el) => {{
      tl.fromTo(el, {{ y: 0 }}, {{ y: -Number(el.dataset.rise), duration: {dur}, ease: "none" }}, 0);
    }});"""


def subwords(sid):
    return "".join(f'<span id="{sid}-w{i + 1}">{w}</span>' for i, w in enumerate(["1st", "Year", "Anniversary"]))


def bg(sid, item, d):
    return (f'<div id="{sid}-bg" class="shot" data-layout-allow-overflow><div id="{sid}-bg-kb" class="kb">'
            f'{media_tag(item, f"{sid}-bg-m", 0, d, 0)}</div></div><div id="{sid}-dim" class="dim"></div>')


def intro(d):
    letters = "".join(f'<span id="intro-k{i + 1}">{c}</span>' for i, c in enumerate("KASOL"))
    x = d - 0.9
    return f"""<template>
  <style>{SHOT_CSS}{TITLE_CSS}
  </style>
  <div id="root" data-composition-id="intro" data-width="{W}" data-height="{H}" data-duration="{d:g}"
    data-composition-variables='[{{"id":"kicker","type":"string","label":"Kicker","default":"Parvati Valley"}}]'>
    {bg("intro", INTRO_BG, d)}
    <div id="intro-glow" class="glow"></div>
    {embers("intro", 7)}
    <div id="intro-stack" class="stack" data-hold>
      <div id="intro-kicker" class="kicker" data-var-text="kicker">Parvati Valley</div>
      <h1 id="intro-title" class="title">{letters}</h1>
      <div id="intro-rule" class="trule"></div>
      <div id="intro-sub" class="sub">{subwords("intro")}</div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{ember_drift("intro", d)}
    tl.fromTo("#intro-bg-kb", {{ scale: 1.0 }}, {{ scale: 1.08, duration: {d:g}, ease: "sine.inOut" }}, 0);
    tl.fromTo("#intro-glow", {{ opacity: 0.4 }}, {{ opacity: 1, duration: 2.2, ease: "power2.inOut" }}, 0);
    tl.fromTo("#intro-kicker", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.5, ease: "power4.out" }}, 0.4);
    tl.fromTo("#intro-title span", {{ opacity: 0.3, filter: "blur(4px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.6, ease: "power3.out", stagger: 0.1 }}, 0.7);
    tl.fromTo("#intro-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.9, ease: "expo.out" }}, 1.6);
    tl.fromTo("#intro-sub span", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power4.out", stagger: 0.09 }}, 1.9);
    tl.fromTo("#intro-sub", {{ textShadow: {GLOW_OFF} }}, {{ textShadow: {GLOW_ON}, duration: 1.4, ease: "power2.inOut" }}, 2.2);
    tl.to(["#intro-kicker", "#intro-title span", "#intro-rule", "#intro-sub span"], {{ opacity: 0, filter: "blur(8px)", duration: 0.25, ease: "power3.in", stagger: 0.04 }}, {x:g});
    tl.to(["#intro-glow", "#intro-embers"], {{ opacity: 0, duration: 0.6, ease: "power2.in" }}, {x:g});
    window.__timelines["intro"] = tl;
  </script>
</template>
"""


def outro(d):
    closing_var = json.dumps([{"id": "closing", "type": "string", "label": "Closing line", "default": CLOSING}])
    return f"""<template>
  <style>{SHOT_CSS}{TITLE_CSS}
  </style>
  <div id="root" data-composition-id="outro" data-width="{W}" data-height="{H}" data-duration="{d:g}"
    data-composition-variables='{closing_var}'>
    <div id="outro-stage" class="shot">
      {bg("outro", OUTRO_BG, d)}
      <div id="outro-glow" class="glow"></div>
      {embers("outro", 23)}
      <div id="outro-stack" class="stack" data-hold>
        <h1 id="outro-title" class="title">KASOL</h1>
        <div id="outro-rule" class="trule"></div>
        <div id="outro-sub" class="sub">{subwords("outro")}</div>
        <div id="outro-closing" class="closing" data-var-text="closing">{CLOSING}</div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{ember_drift("outro", d)}
    tl.fromTo("#outro-bg-kb", {{ x: 160, filter: "blur(16px)", scale: 1.0 }}, {{ x: 0, filter: "blur(0px)", duration: 0.32, ease: "power3.out" }}, 0);
    tl.fromTo("#outro-bg-kb", {{ scale: 1.0 }}, {{ scale: 1.07, duration: {d:g}, ease: "sine.inOut", immediateRender: false }}, 0);
    tl.fromTo("#outro-dim", {{ opacity: 0 }}, {{ opacity: 1, duration: 1.0, ease: "power2.inOut" }}, 0.6);
    tl.fromTo("#outro-glow", {{ opacity: 0 }}, {{ opacity: 1, duration: 1.6, ease: "power2.inOut" }}, 0.8);
    tl.fromTo("#outro-title", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.8, ease: "power3.out" }}, 1.0);
    tl.fromTo("#outro-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.9, ease: "expo.out" }}, 1.6);
    tl.fromTo("#outro-sub span", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power4.out", stagger: 0.09 }}, 1.9);
    tl.fromTo("#outro-sub", {{ textShadow: {GLOW_OFF} }}, {{ textShadow: {GLOW_ON}, duration: 1.4, ease: "power2.inOut" }}, 2.2);
    tl.fromTo("#outro-closing", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.4, ease: "power4.out" }}, 3.0);
    tl.to("#outro-stage", {{ opacity: 0, duration: 2.0, ease: "power2.inOut" }}, {d - 2.1:g});
    window.__timelines["outro"] = tl;
  </script>
</template>
"""


# ---- write ----------------------------------------------------------------------------------
os.makedirs(f"{OUT}/compositions", exist_ok=True)
for f in glob.glob(f"{OUT}/compositions/*.html"):
    os.remove(f)

files = [("intro", INTRO, intro(INTRO))]
for sid, chapter, items in SCENES:
    d, html = build_scene(sid, chapter, items)
    files.append((sid, d, html))
files.append(("outro", OUTRO, outro(OUTRO)))

t, hosts = 0.0, []
for sid, d, html in files:
    with open(f"{OUT}/compositions/{sid}.html", "w") as fh:
        fh.write(html)
    hosts.append(f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                 f'data-start="{t:.4f}" data-duration="{d:.4f}" data-track-index="1" data-track-kind="graphics" '
                 f'data-width="{W}" data-height="{H}"></div>')
    t += d

music = sorted(glob.glob(f"{OUT}/assets/audio/music.*"))
audio = ""
if music:
    rel = os.path.relpath(music[0], OUT)
    audio = (f'      <audio id="music" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="2" '
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
print(f"wrote {len(files)} scenes, {len(shots)} shots, {t:.3f} s, unit {unit / FPS:.2f} s, music: {music[0] if music else 'none'}")
