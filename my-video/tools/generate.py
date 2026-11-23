"""Writes index.html and compositions/*.html for the Kasol anniversary film.

Run from the project folder:  python3 tools/generate.py
Edit the SCENES list to add, remove or reorder media. Each beat is a group of photos or
clips shown together; its first number is how long it stays on screen, in seconds.
Hand edits to index.html or compositions/ are overwritten when this runs.
"""
import json, os, subprocess

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P, V = "assets/photos/", "assets/video/"
W, H = 1920, 1080
ROW_W, FRAME_H, FRAME_TOP, GAP = 1680, 780, 110, 36


def full(name):
    return {"tag": "img", "src": P + name + ".jpg", "full": True}


def img(name):
    return {"tag": "img", "src": P + name + ".jpg"}


def vid(name):
    return {"tag": "video", "src": V + name + ".mp4", "aspect": 9 / 16}


def beat(dur, items, enter=None):
    return {"dur": dur, "items": items, "enter": enter}


# ---- the film -------------------------------------------------------------------------------
SCENES = [
    ("intro", 8, None, None),
    ("morning", 11, "The morning", [
        beat(3, [full("breakfast")]),
        beat(4, [img("scooter-valley"), img("him-river-sun"), img("her-river-sun")], "whip"),
        beat(4, [img("him-beer-cafe"), img("cafe-food"), img("her-cafe")], "blur"),
    ]),
    ("golden", 8, "Golden hour", [
        beat(8, [vid("walk-to-sunset"), vid("valley-sunset"), vid("sun-rays")], "rise"),
    ]),
    ("sunset", 10, "Sunset", [
        beat(5, [img("road-walk"), vid("her-on-road"), img("sunset-view")], "blur"),
        beat(5, [img("her-photographing-sunset"), img("sunset-fire"), img("dusk-pines")], "rise"),
    ]),
    ("manikaran", 17, "Manikaran", [
        beat(3, [full("gurudwara")]),
        beat(3.5, [img("gurudwara-front"), img("manikaran-temple-river"), img("hot-spring-pool")], "blur"),
        beat(3.5, [vid("river-run"), vid("manikaran-river"), img("langar-thali")], "whip"),
        beat(3.5, [img("her-on-bridge"), img("couple-selfie-manikaran"), img("him-on-bridge")], "rise"),
        beat(3.5, [img("her-gurudwara-railing"), img("him-bridge-walk"), img("her-peace-gurudwara"),
                   img("him-gurudwara-railing")], "blur"),
    ]),
    ("afternoons", 8, "Slow afternoons", [
        beat(4, [img("couple-heart"), img("her-heart"), img("her-river-dusk")], "whip"),
        beat(4, [img("him-river-rock"), img("couple-selfie-cafe")], "blur"),
    ]),
    ("night", 10, "After dark", [
        beat(3, [full("enfield-night")]),
        beat(3.5, [img("snooker-him"), img("snooker-her")], "whip"),
        beat(3.5, [img("apple-mirror"), img("couple-cosy-night"), img("room-mirror")], "blur"),
    ]),
    ("oneyear", 8, "One year", [
        beat(8, [img("anniversary-candles"), img("anniversary-cake"), img("story-coaster")], "slow"),
    ]),
    ("outro", 10, None, None),
]
CLOSING = "#SayAnAparajitaStory"

# ---- helpers --------------------------------------------------------------------------------
_aspects = {}


def aspect(item):
    if "aspect" in item:
        return item["aspect"]
    src = item["src"]
    if src not in _aspects:
        out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                       "stream=width,height", "-of", "csv=p=0", os.path.join(OUT, src)], text=True)
        w, h = (int(x) for x in out.strip().split(","))
        _aspects[src] = w / h
    return _aspects[src]


def row_layout(items):
    asp = [aspect(i) for i in items]
    h = min(FRAME_H, int((ROW_W - GAP * (len(items) - 1)) / sum(asp)))
    widths = [round(h * a) for a in asp]
    x = (W - sum(widths) - GAP * (len(items) - 1)) // 2
    top = FRAME_TOP + (FRAME_H - h) // 2
    out = []
    for w in widths:
        out.append((x, top, w, h))
        x += w + GAP
    return out


def media_tag(item, mid, start, dur, lane):
    if item["tag"] == "img":
        return (f'<img id="{mid}" class="clip" data-start="{start:g}" data-duration="{dur:g}" '
                f'data-track-index="{lane}" src="{item["src"]}" alt="" />')
    return (f'<video id="{mid}" class="clip" data-start="{start:g}" data-duration="{dur:g}" '
            f'data-track-index="{lane}" muted playsinline src="{item["src"]}"></video>')


BASE_CSS = """
    #root { position: absolute; inset: 0; overflow: hidden; background: #07080b; font-family: "Montserrat", sans-serif; }
    #root .frame { position: absolute; border-radius: 18px; overflow: hidden; background: #111318;
      border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 30px 80px rgba(0,0,0,0.65), 0 0 60px rgba(255,150,70,0.06); }
    #root .full { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; overflow: hidden; }
    #root .kb { position: absolute; left: 0; top: 0; width: 100%; height: 100%; }
    #root .kb img, #root .kb video { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }
    #root .scrim { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px;
      background: linear-gradient(180deg, rgba(7,8,11,0) 55%, rgba(7,8,11,0.78) 100%); }
    #root .label { position: absolute; left: 192px; top: 918px; height: 34px; display: flex; align-items: center; gap: 22px;
      color: #c4c8cf; font-size: 28px; letter-spacing: 0.4em; text-transform: uppercase; white-space: nowrap; }
    #root .label .rule { width: 64px; height: 2px; background: linear-gradient(90deg, #ffc27a, #ff8a3d); transform-origin: left center; }
"""

ENTER = {
    "rise": ('{ opacity: 0, clipPath: "inset(100% 0% 0% 0% round 18px)" }',
             '{ opacity: 1, clipPath: "inset(0% 0% 0% 0% round 18px)", duration: 1.0, ease: "expo.out", stagger: 0.12 }'),
    "blur": ('{ opacity: 0, scale: 0.94, filter: "blur(12px)" }',
             '{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 1.0, ease: "expo.out", stagger: 0.14 }'),
    "whip": ('{ opacity: 0, x: 280, filter: "blur(18px)" }',
             '{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.55, ease: "power3.out", stagger: 0.1 }'),
    "slow": ('{ opacity: 0, filter: "blur(10px)" }',
             '{ opacity: 1, filter: "blur(0px)", duration: 1.4, ease: "power2.out", stagger: 0.6 }'),
}


def build_scene(sid, dur, chapter, beats):
    assert abs(sum(b["dur"] for b in beats) - dur) < 1e-6, (sid, dur)
    html, js = [], []
    t = 0.0
    for bi, b in enumerate(beats):
        n = bi + 1
        s, d = t, b["dur"]
        e = s + d
        last = bi == len(beats) - 1
        exit_at = e - (0.5 if last else 0.4)
        if b["items"][0].get("full"):
            fid = f"{sid}-b{n}"
            html.append(f'    <div id="{fid}" class="full"><div id="{fid}-kb" class="kb">'
                        f'{media_tag(b["items"][0], f"{fid}-m", s, d, 0)}</div>'
                        f'<div id="{fid}-scrim" class="scrim"></div></div>')
            js.append(f'    tl.fromTo("#{fid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.8, ease: "power2.out" }}, {s:g});')
            js.append(f'    tl.fromTo("#{fid}-kb", {{ scale: 1.04 }}, {{ scale: 1.12, duration: {d:g}, ease: "sine.inOut" }}, {s:g});')
            js.append(f'    tl.to("#{fid}", {{ opacity: 0, filter: "blur(8px)", duration: 0.4, ease: "power3.in" }}, {exit_at:g});')
        else:
            frames, kbs = [], []
            for ii, (item, (x, y, w, h)) in enumerate(zip(b["items"], row_layout(b["items"]))):
                fid = f"{sid}-b{n}f{ii + 1}"
                frames.append("#" + fid)
                kbs.append(f"#{fid}-kb")
                html.append(f'    <div id="{fid}" class="frame" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;">'
                            f'<div id="{fid}-kb" class="kb">{media_tag(item, f"{fid}-m", s, d, ii)}</div></div>')
            fs, ks = ", ".join(frames), ", ".join(kbs)
            frm, to = ENTER[b["enter"] or "blur"]
            js.append(f'    tl.fromTo("{fs}", {frm}, {to}, {s + 0.05:g});')
            if b["enter"] == "rise":
                js.append(f'    tl.fromTo("{ks}", {{ scale: 1.15 }}, {{ scale: 1, duration: 1.2, ease: "expo.out", stagger: 0.12 }}, {s + 0.05:g});')
                js.append(f'    tl.fromTo("{ks}", {{ scale: 1 }}, {{ scale: 1.05, duration: {d - 1.3:g}, ease: "sine.inOut", immediateRender: false }}, {s + 1.3:g});')
            else:
                js.append(f'    tl.fromTo("{ks}", {{ scale: 1 }}, {{ scale: 1.06, duration: {d:g}, ease: "sine.inOut" }}, {s:g});')
            js.append(f'    tl.to("{fs}", {{ opacity: 0, filter: "blur(8px)", duration: 0.35, ease: "power3.in" }}, {exit_at:g});')
        t = e
    html.append(f'    <div id="{sid}-label" class="label"><div id="{sid}-rule" class="rule"></div>'
                f'<span id="{sid}-label-text" data-var-text="chapter">{chapter}</span></div>')
    js.append(f'    tl.fromTo("#{sid}-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.9, ease: "expo.out" }}, 0.8);')
    js.append(f'    tl.fromTo("#{sid}-label-text", {{ opacity: 0, filter: "blur(8px)" }}, '
              f'{{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 1.05);')
    js.append(f'    tl.to("#{sid}-label", {{ opacity: 0, filter: "blur(8px)", duration: 0.25, ease: "power3.in" }}, {dur - 0.8:g});')
    variables = json.dumps([{"id": "chapter", "type": "string", "label": "Chapter label", "default": chapter}])
    return f"""<template>
  <style>{BASE_CSS}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080" data-duration="{dur:g}"
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
    #root .glow { position: absolute; left: 260px; top: 90px; width: 1400px; height: 900px; border-radius: 50%;
      background: radial-gradient(closest-side, rgba(255,154,74,0.22), rgba(255,120,50,0.08) 55%, rgba(7,8,11,0) 100%); }
    #root .embers { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }
    #root .ember { position: absolute; border-radius: 50%; background: #ffb46a; box-shadow: 0 0 8px #ff9a4a; }
    #root .stack { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; display: flex; flex-direction: column;
      align-items: center; justify-content: center; }
    #root .kicker { color: #b3b8c1; font-size: 28px; letter-spacing: 0.4em; text-transform: uppercase; margin-bottom: 26px; }
    #root .title { font-family: "Playfair Display", serif; font-weight: 700; font-size: 230px; line-height: 1;
      letter-spacing: 0.08em; color: #f4efe6; padding-left: 0.08em; }
    #root .title span { display: inline-block; }
    #root .trule { width: 520px; height: 2px; margin: 34px 0 30px;
      background: linear-gradient(90deg, rgba(255,194,122,0), #ffc27a 30%, #ff8a3d 70%, rgba(255,138,61,0)); }
    #root .sub { font-size: 54px; letter-spacing: 0.22em; text-transform: uppercase; color: #ffc27a; padding-left: 0.22em; }
    #root .sub span { display: inline-block; margin: 0 0.18em; }
    #root .closing { margin-top: 46px; color: #d6d9de; font-size: 34px; letter-spacing: 0.08em; }
"""
GLOW_OFF = '"0 0 0px rgba(255,170,90,0), 0 0 0px rgba(255,140,60,0)"'
GLOW_ON = '"0 0 18px rgba(255,170,90,0.75), 0 0 52px rgba(255,140,60,0.45)"'


def embers(sid, seed, count=36):
    s = seed
    def rnd():
        nonlocal s
        s = (s * 1103515245 + 12345) % 2147483648
        return s / 2147483648
    out = []
    for _ in range(count):
        x, y = round(120 + rnd() * 1680), round(260 + rnd() * 820)
        size, op, rise = round(2 + rnd() * 3, 1), round(0.25 + rnd() * 0.55, 2), round(140 + rnd() * 300)
        out.append(f'<div class="ember" data-rise="{rise}" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px;opacity:{op};"></div>')
    return f'<div id="{sid}-embers" class="embers" data-layout-ignore>' + "".join(out) + "</div>"


def ember_drift(sid, dur):
    return f"""    document.querySelectorAll("#{sid}-embers .ember").forEach((el) => {{
      tl.fromTo(el, {{ y: 0 }}, {{ y: -Number(el.dataset.rise), duration: {dur}, ease: "none" }}, 0);
    }});"""


def subwords(sid):
    return "".join(f'<span id="{sid}-w{i + 1}">{w}</span>' for i, w in enumerate(["1st", "Year", "Anniversary"]))


def intro(d):
    letters = "".join(f'<span id="intro-k{i + 1}">{c}</span>' for i, c in enumerate("KASOL"))
    x = d - 1.4
    return f"""<template>
  <style>{BASE_CSS}{TITLE_CSS}
  </style>
  <div id="root" data-composition-id="intro" data-width="1920" data-height="1080" data-duration="{d}"
    data-composition-variables='[{{"id":"kicker","type":"string","label":"Kicker","default":"Parvati Valley · Himachal Pradesh"}}]'>
    <div id="intro-glow" class="glow"></div>
    {embers("intro", 7)}
    <div id="intro-stack" class="stack" data-hold>
      <div id="intro-kicker" class="kicker" data-var-text="kicker">Parvati Valley · Himachal Pradesh</div>
      <h1 id="intro-title" class="title">{letters}</h1>
      <div id="intro-rule" class="trule"></div>
      <div id="intro-sub" class="sub">{subwords("intro")}</div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{ember_drift("intro", d)}
    tl.fromTo("#intro-embers", {{ opacity: 0.5 }}, {{ opacity: 1, duration: 2, ease: "power2.inOut" }}, 0);
    tl.fromTo("#intro-glow", {{ opacity: 0.35 }}, {{ opacity: 1, duration: 2.6, ease: "power2.inOut" }}, 0.2);
    tl.fromTo("#intro-kicker", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.6, ease: "power4.out" }}, 0.8);
    tl.fromTo("#intro-title span", {{ opacity: 0.3, filter: "blur(4px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.7, ease: "power3.out", stagger: 0.12 }}, 1.3);
    tl.fromTo("#intro-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 1.0, ease: "expo.out" }}, 2.5);
    tl.fromTo("#intro-sub span", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.35, ease: "power4.out", stagger: 0.1 }}, 2.9);
    tl.fromTo("#intro-sub", {{ textShadow: {GLOW_OFF} }}, {{ textShadow: {GLOW_ON}, duration: 1.6, ease: "power2.inOut" }}, 3.3);
    tl.to(["#intro-kicker", "#intro-title span", "#intro-rule", "#intro-sub span"], {{ opacity: 0, filter: "blur(8px)", duration: 0.3, ease: "power3.in", stagger: 0.05 }}, {x:g});
    tl.to("#intro-glow", {{ opacity: 0, duration: 1.0, ease: "power2.in" }}, {x + 0.1:g});
    tl.to("#intro-embers", {{ opacity: 0, duration: 0.9, ease: "power2.in" }}, {x + 0.3:g});
    window.__timelines["intro"] = tl;
  </script>
</template>
"""


def outro(d):
    closing_var = json.dumps([{"id": "closing", "type": "string", "label": "Closing line", "default": CLOSING}])
    return f"""<template>
  <style>{BASE_CSS}{TITLE_CSS}
  </style>
  <div id="root" data-composition-id="outro" data-width="1920" data-height="1080" data-duration="{d}"
    data-composition-variables='{closing_var}'>
    <div id="outro-stage" class="full">
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
    tl.fromTo("#outro-embers", {{ opacity: 0 }}, {{ opacity: 1, duration: 2, ease: "power2.inOut" }}, 0);
    tl.fromTo("#outro-glow", {{ opacity: 0 }}, {{ opacity: 1, duration: 2, ease: "power2.inOut" }}, 0);
    tl.fromTo("#outro-title", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.9, ease: "power3.out" }}, 0.5);
    tl.fromTo("#outro-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 1.0, ease: "expo.out" }}, 1.2);
    tl.fromTo("#outro-sub span", {{ opacity: 1, color: "#3a3d44" }}, {{ opacity: 1, color: "#ffc27a", duration: 0.5, ease: "power2.out", stagger: 0.1 }}, 1.5);
    tl.fromTo("#outro-sub", {{ textShadow: {GLOW_OFF} }}, {{ textShadow: {GLOW_ON}, duration: 1.6, ease: "power2.inOut" }}, 2.0);
    tl.fromTo("#outro-closing", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.4, ease: "power4.out" }}, 3.6);
    tl.to("#outro-stage", {{ opacity: 0, duration: 2.5, ease: "power2.inOut" }}, {d - 2.7:g});
    window.__timelines["outro"] = tl;
  </script>
</template>
"""


# ---- write ----------------------------------------------------------------------------------
os.makedirs(f"{OUT}/compositions", exist_ok=True)
for f in os.listdir(f"{OUT}/compositions"):
    if f.endswith(".html"):
        os.remove(f"{OUT}/compositions/{f}")

t, hosts = 0, []
for sid, d, chapter, beats in SCENES:
    html = intro(d) if sid == "intro" else outro(d) if sid == "outro" else build_scene(sid, d, chapter, beats)
    with open(f"{OUT}/compositions/{sid}.html", "w") as fh:
        fh.write(html)
    hosts.append(f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                 f'data-start="{t:g}" data-duration="{d:g}" data-track-index="1" data-track-kind="graphics" '
                 f'data-width="1920" data-height="1080"></div>')
    t += d

index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #07080b; }}
      #root {{ width: 100%; height: 100%; }}
      #ground {{ position: absolute; inset: 0; background: #07080b; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{t:g}" data-width="1920" data-height="1080">
      <div id="ground"></div>
{chr(10).join(hosts)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
with open(f"{OUT}/index.html", "w") as fh:
    fh.write(index)
used = sum(len(b["items"]) for _, _, _, bs in SCENES if bs for b in bs)
print(f"wrote {len(SCENES)} scenes, {used} media items, {t:g} s")
