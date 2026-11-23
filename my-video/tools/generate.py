"""Writes index.html and compositions/*.html for the Kasol anniversary film."""
import os, sys

OUT = sys.argv[1]
os.makedirs(f"{OUT}/compositions", exist_ok=True)

W, H = 1920, 1080
FRAME_H, FRAME_TOP, GAP = 780, 110, 36
AMBER = "#ffc27a"

BASE_CSS = """
    #root { position: absolute; inset: 0; overflow: hidden; background: #07080b; font-family: "Montserrat", sans-serif; }
    #root .frame { position: absolute; border-radius: 18px; overflow: hidden; background: #111318;
      border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 30px 80px rgba(0,0,0,0.65), 0 0 60px rgba(255,150,70,0.06); }
    #root .full { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; overflow: hidden; }
    #root .kb { position: absolute; left: 0; top: 0; width: 100%; height: 100%; }
    #root .kb img, #root .kb video { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }
    #root .scrim { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px;
      background: linear-gradient(180deg, rgba(7,8,11,0) 55%, rgba(7,8,11,0.78) 100%); }
    #root .label { position: absolute; left: 192px; top: 918px; height: 30px; display: flex; align-items: center; gap: 22px;
      color: #c4c8cf; font-size: 28px; letter-spacing: 0.4em; text-transform: uppercase; white-space: nowrap; }
    #root .label .rule { width: 64px; height: 2px; background: linear-gradient(90deg, #ffc27a, #ff8a3d); transform-origin: left center; }
"""


def layout(items):
    """items: list of aspect ratios (w/h). Returns [(left, width)] centred on the canvas."""
    widths = [round(FRAME_H * a) for a in items]
    total = sum(widths) + GAP * (len(widths) - 1)
    x = (W - total) // 2
    out = []
    for w in widths:
        out.append((x, w))
        x += w + GAP
    return out


def media(tag, mid, src, start, dur, lane, rate=None):
    if tag == "img":
        return (f'<img id="{mid}" class="clip" data-start="{start}" data-duration="{dur}" '
                f'data-track-index="{lane}" src="{src}" alt="" />')
    r = f' data-playback-rate="{rate}"' if rate else ""
    return (f'<video id="{mid}" class="clip" data-start="{start}" data-duration="{dur}" data-track-index="{lane}"{r} '
            f'muted playsinline src="{src}"></video>')


def label(sid, text):
    return (f'<div id="{sid}-label" class="label"><div id="{sid}-rule" class="rule"></div>'
            f'<span id="{sid}-label-text" data-var-text="chapter">{text}</span></div>')


def scene(sid, dur, chapter, body, script, extra_css=""):
    variables = f'[{{"id":"chapter","type":"string","label":"Chapter label","default":"{chapter}"}}]'
    return f"""<template>
  <style>{BASE_CSS}{extra_css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080" data-duration="{dur}"
    data-composition-variables='{variables}'>
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{script}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""


def label_in(sid, at):
    return f"""    tl.fromTo("#{sid}-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.9, ease: "expo.out" }}, {at});
    tl.fromTo("#{sid}-label-text", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, {at + 0.25});
"""


def label_out(sid, at):
    return f"""    tl.to("#{sid}-label", {{ opacity: 0, filter: "blur(8px)", duration: 0.25, ease: "power3.in" }}, {at});
"""


def blur_out(sel, at, dur=0.5):
    return f"""    tl.to("{sel}", {{ opacity: 0, filter: "blur(8px)", duration: {dur}, ease: "power3.in" }}, {at});
"""


def push(sel, dur, a=1.0, b=1.06, at=0):
    return f"""    tl.fromTo("{sel}", {{ scale: {a} }}, {{ scale: {b}, duration: {dur}, ease: "sine.inOut" }}, {at});
"""


def frames(sid, specs, start, dur, lane0=0):
    """specs: list of (tag, src, aspect, rate). Returns HTML of frames with timed media inside."""
    html = []
    for i, ((tag, src, aspect, rate), (x, w)) in enumerate(zip(specs, layout([s[2] for s in specs]))):
        n = i + 1
        html.append(f'    <div id="{sid}-f{n}" class="frame" style="left:{x}px;top:{FRAME_TOP}px;width:{w}px;height:{FRAME_H}px;">'
                    f'<div id="{sid}-kb{n}" class="kb">{media(tag, f"{sid}-m{n}", src, start, dur, lane0 + i, rate)}</div></div>')
    return "\n".join(html)


def full(sid, key, tag, src, start, dur, lane=0):
    return (f'    <div id="{sid}-{key}" class="full"><div id="{sid}-{key}-kb" class="kb">'
            f'{media(tag, f"{sid}-{key}-m", src, start, dur, lane)}</div></div>')


files = {}

# ---- intro / outro shared bits -------------------------------------------------------------
def embers(sid, count=36, seed=7):
    s = seed
    def rnd():
        nonlocal s
        s = (s * 1103515245 + 12345) % 2147483648
        return s / 2147483648
    out = []
    for i in range(count):
        x, y = round(120 + rnd() * 1680), round(260 + rnd() * 820)
        size = round(2 + rnd() * 3, 1)
        op = round(0.25 + rnd() * 0.55, 2)
        rise = round(140 + rnd() * 300)
        out.append(f'<div class="ember" data-rise="{rise}" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px;opacity:{op};"></div>')
    return f'    <div id="{sid}-embers" class="embers" data-layout-ignore>' + "".join(out) + "</div>"


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
    #root .closing { margin-top: 46px; color: #c9ccd2; font-size: 30px; letter-spacing: 0.12em; }
"""
GLOW_OFF = '"0 0 0px rgba(255,170,90,0), 0 0 0px rgba(255,140,60,0)"'
GLOW_ON = '"0 0 18px rgba(255,170,90,0.75), 0 0 52px rgba(255,140,60,0.45)"'
EMBER_DRIFT = """    document.querySelectorAll("#{sid}-embers .ember").forEach((el) => {{
      tl.fromTo(el, {{ y: 0 }}, {{ y: -Number(el.dataset.rise), duration: {dur}, ease: "none" }}, 0);
    }});
"""
letters = "".join(f'<span id="intro-k{i+1}">{c}</span>' for i, c in enumerate("KASOL"))
subwords = lambda sid: "".join(f'<span id="{sid}-w{i+1}">{w}</span>' for i, w in enumerate(["1st", "Year", "Anniversary"]))

files["intro"] = f"""<template>
  <style>{BASE_CSS}{TITLE_CSS}
  </style>
  <div id="root" data-composition-id="intro" data-width="1920" data-height="1080" data-duration="12"
    data-composition-variables='[{{"id":"kicker","type":"string","label":"Kicker","default":"Parvati Valley · Himachal Pradesh"}}]'>
    <div id="intro-glow" class="glow"></div>
{embers("intro")}
    <div id="intro-stack" class="stack" data-hold>
      <div id="intro-kicker" class="kicker" data-var-text="kicker">Parvati Valley · Himachal Pradesh</div>
      <h1 id="intro-title" class="title">{letters}</h1>
      <div id="intro-rule" class="trule"></div>
      <div id="intro-sub" class="sub">{subwords("intro")}</div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{EMBER_DRIFT.format(sid="intro", dur=12)}
    tl.fromTo("#intro-embers", {{ opacity: 0.5 }}, {{ opacity: 1, duration: 2, ease: "power2.inOut" }}, 0);
    tl.fromTo("#intro-glow", {{ opacity: 0.35 }}, {{ opacity: 1, duration: 3, ease: "power2.inOut" }}, 0.3);
    tl.fromTo("#intro-kicker", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.6, ease: "power4.out" }}, 1.0);
    tl.fromTo("#intro-title span", {{ opacity: 0.3, filter: "blur(4px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.7, ease: "power3.out", stagger: 0.12 }}, 1.6);
    tl.fromTo("#intro-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 1.0, ease: "expo.out" }}, 2.9);
    tl.fromTo("#intro-sub span", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.35, ease: "power4.out", stagger: 0.1 }}, 3.3);
    tl.fromTo("#intro-sub", {{ textShadow: {GLOW_OFF} }}, {{ textShadow: {GLOW_ON}, duration: 1.8, ease: "power2.inOut" }}, 3.7);
    tl.to(["#intro-kicker", "#intro-title span", "#intro-rule", "#intro-sub span"], {{ opacity: 0, filter: "blur(8px)", duration: 0.3, ease: "power3.in", stagger: 0.06 }}, 10.5);
    tl.to("#intro-glow", {{ opacity: 0, duration: 1.1, ease: "power2.in" }}, 10.6);
    tl.to("#intro-embers", {{ opacity: 0, duration: 1.0, ease: "power2.in" }}, 10.8);
    window.__timelines["intro"] = tl;
  </script>
</template>
"""

files["outro"] = f"""<template>
  <style>{BASE_CSS}{TITLE_CSS}
  </style>
  <div id="root" data-composition-id="outro" data-width="1920" data-height="1080" data-duration="12"
    data-composition-variables='[{{"id":"closing","type":"string","label":"Closing line","default":"Here\\u2019s to the next trail"}}]'>
    <div id="outro-stage" class="full">
      <div id="outro-glow" class="glow"></div>
{embers("outro", seed=23)}
      <div id="outro-stack" class="stack" data-hold>
        <h1 id="outro-title" class="title">KASOL</h1>
        <div id="outro-rule" class="trule"></div>
        <div id="outro-sub" class="sub">{subwords("outro")}</div>
        <div id="outro-closing" class="closing" data-var-text="closing">Here’s to the next trail</div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{EMBER_DRIFT.format(sid="outro", dur=12)}
    tl.fromTo("#outro-embers", {{ opacity: 0 }}, {{ opacity: 1, duration: 2, ease: "power2.inOut" }}, 0);
    tl.fromTo("#outro-glow", {{ opacity: 0 }}, {{ opacity: 1, duration: 2, ease: "power2.inOut" }}, 0);
    tl.fromTo("#outro-title", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.9, ease: "power3.out" }}, 0.6);
    tl.fromTo("#outro-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 1.0, ease: "expo.out" }}, 1.4);
    tl.fromTo("#outro-sub span", {{ opacity: 1, color: "#3a3d44" }}, {{ opacity: 1, color: "{AMBER}", duration: 0.5, ease: "power2.out", stagger: 0.1 }}, 1.8);
    tl.fromTo("#outro-sub", {{ textShadow: {GLOW_OFF} }}, {{ textShadow: {GLOW_ON}, duration: 1.8, ease: "power2.inOut" }}, 2.4);
    tl.fromTo("#outro-closing", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.4, ease: "power4.out" }}, 4.8);
    tl.to("#outro-stage", {{ opacity: 0, duration: 2.6, ease: "power2.inOut" }}, 9.2);
    window.__timelines["outro"] = tl;
  </script>
</template>
"""

# ---- photo / footage scenes -----------------------------------------------------------------
P, V = "assets/photos/", "assets/video/"
PORT34, PORT916 = 3 / 4, 9 / 16

# morning: breakfast full frame
files["morning"] = scene("morning", 9, "The morning", "\n".join([
    full("morning", "photo", "img", P + "breakfast.jpg", 0, 9),
    '    <div id="morning-scrim" class="scrim"></div>',
    "    " + label("morning", "The morning"),
]), "".join([
    push("#morning-photo-kb", 9, 1.04, 1.12),
    '    tl.fromTo("#morning-photo", { opacity: 0 }, { opacity: 1, duration: 0.9, ease: "power2.out" }, 0);\n',
    label_in("morning", 0.8),
    label_out("morning", 8.2),
    blur_out("#morning-photo", 8.4),
]))

# golden: triptych of footage, clip-path reveal from the bottom
g = [("video", V + "walk-to-sunset.mp4", PORT916, None), ("video", V + "valley-sunset.mp4", PORT916, None),
     ("video", V + "sun-rays.mp4", PORT916, None)]
files["golden"] = scene("golden", 12, "Golden hour", "\n".join([frames("golden", g, 0, 11.9), "    " + label("golden", "Golden hour")]), "".join([
    '    tl.fromTo("#golden-f1, #golden-f2, #golden-f3", { clipPath: "inset(100% 0% 0% 0% round 18px)" }, '
    '{ clipPath: "inset(0% 0% 0% 0% round 18px)", duration: 1.1, ease: "expo.out", stagger: 0.15 }, 0.1);\n',
    '    tl.fromTo("#golden-kb1, #golden-kb2, #golden-kb3", { scale: 1.15 }, { scale: 1, duration: 1.6, ease: "expo.out", stagger: 0.15 }, 0.1);\n',
    label_in("golden", 1.0),
    label_out("golden", 11.2),
    blur_out("#golden-f1, #golden-f2, #golden-f3", 11.4),
]))

# sunset: photo, footage, photo
s = [("img", P + "road-walk.jpg", PORT34, None), ("video", V + "her-on-road.mp4", PORT916, None),
     ("img", P + "sunset-view.jpg", PORT34, None)]
files["sunset"] = scene("sunset", 11, "Sunset", "\n".join([frames("sunset", s, 0, 11), "    " + label("sunset", "Sunset")]), "".join([
    '    tl.fromTo("#sunset-f1, #sunset-f2, #sunset-f3", { opacity: 0, scale: 0.94, filter: "blur(12px)" }, '
    '{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 1.2, ease: "expo.out", stagger: 0.18 }, 0.1);\n',
    push("#sunset-kb1, #sunset-kb3", 11, 1.0, 1.07),
    label_in("sunset", 1.0),
    label_out("sunset", 10.2),
    blur_out("#sunset-f1, #sunset-f2, #sunset-f3", 10.4),
]))

# night: Royal Enfield full frame, then the snooker diptych
n = [("img", P + "snooker-him.jpg", PORT34, None), ("img", P + "snooker-her.jpg", PORT34, None)]
files["night"] = scene("night", 12, "After dark", "\n".join([
    full("night", "bike", "img", P + "enfield-night.jpg", 0, 6),
    '    <div id="night-scrim" class="scrim"></div>',
    frames("night", n, 5.4, 6.6, lane0=1),
    "    " + label("night", "After dark"),
]), "".join([
    '    tl.fromTo("#night-bike", { opacity: 0 }, { opacity: 1, duration: 1.4, ease: "power2.inOut" }, 0);\n',
    push("#night-bike-kb", 6, 1.1, 1.03),
    label_in("night", 1.2),
    blur_out("#night-bike, #night-scrim", 5.4, 0.45),
    '    tl.fromTo("#night-f1", { opacity: 0, x: -60, filter: "blur(10px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 1.1, ease: "expo.out" }, 5.5);\n',
    '    tl.fromTo("#night-f2", { opacity: 0, x: 60, filter: "blur(10px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 1.1, ease: "expo.out" }, 5.62);\n',
    push("#night-kb1, #night-kb2", 6.6, 1.0, 1.06, 5.4),
    label_out("night", 11.2),
    blur_out("#night-f1, #night-f2", 11.4),
]))

# manikaran: gurudwara full frame, then the river clip beside a title
files["manikaran"] = scene("manikaran", 12, "Manikaran", "\n".join([
    full("manikaran", "shrine", "img", P + "gurudwara.jpg", 0, 6.2),
    '    <div id="manikaran-scrim" class="scrim"></div>',
    "    " + label("manikaran", "Manikaran"),
    f'    <div id="manikaran-f1" class="frame" style="left:250px;top:{FRAME_TOP}px;width:439px;height:{FRAME_H}px;">'
    f'<div id="manikaran-kb1" class="kb">{media("video", "manikaran-m1", V + "river-drive.mp4", 5.6, 6.3, 1)}</div></div>',
    f'    <div id="manikaran-f2" class="frame" style="left:725px;top:{FRAME_TOP}px;width:439px;height:{FRAME_H}px;">'
    f'<div id="manikaran-kb2" class="kb">{media("video", "manikaran-m2", V + "manikaran-river.mp4", 5.6, 6.3, 2)}</div></div>',
    '    <div id="manikaran-text" class="mtext"><div id="manikaran-name" class="mname"><span id="manikaran-n1">Manikaran</span></div>'
    '<div id="manikaran-note" class="mnote"><span id="manikaran-t1">Parvati</span> <span id="manikaran-t2">river</span> '
    '<br><span id="manikaran-t3">hot</span> <span id="manikaran-t4">springs</span></div></div>',
]), "".join([
    '    tl.fromTo("#manikaran-shrine", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 1.0, ease: "power3.out" }, 0);\n',
    push("#manikaran-shrine-kb", 6.2, 1.02, 1.09),
    label_in("manikaran", 0.9),
    label_out("manikaran", 5.3),
    blur_out("#manikaran-shrine, #manikaran-scrim", 5.5, 0.45),
    '    tl.fromTo("#manikaran-f1, #manikaran-f2", { clipPath: "inset(0% 100% 0% 0% round 18px)" }, { clipPath: "inset(0% 0% 0% 0% round 18px)", duration: 1.0, ease: "expo.out", stagger: 0.15 }, 5.7);\n',
    '    tl.fromTo("#manikaran-n1", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }, 6.3);\n',
    '    tl.fromTo("#manikaran-note span", { opacity: 0.12 }, { opacity: 1, duration: 0.3, ease: "power2.out", stagger: 0.08 }, 6.7);\n',
    blur_out("#manikaran-f1, #manikaran-f2, #manikaran-text", 11.4),
]), extra_css="""
    #root .mtext { position: absolute; left: 1250px; top: 400px; width: 520px; }
    #root .mname { font-family: "Playfair Display", serif; font-weight: 700; font-size: 92px; color: #f4efe6; line-height: 1.05; }
    #root .mnote { margin-top: 26px; font-size: 28px; letter-spacing: 0.22em; line-height: 1.6; text-transform: uppercase; color: #c4c8cf; }
""")

# homeward: dusk diptych, horizontal whip in, dip out
h = [("img", P + "dusk-ridge.jpg", PORT916, None), ("img", P + "dusk-pines.jpg", PORT34, None)]
files["homeward"] = scene("homeward", 10, "The road home", "\n".join([frames("homeward", h, 0, 10), "    " + label("homeward", "The road home")]), "".join([
    '    tl.fromTo("#homeward-f1, #homeward-f2", { opacity: 0, x: 320, filter: "blur(20px)" }, '
    '{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.55, ease: "power3.out", stagger: 0.12 }, 0.15);\n',
    push("#homeward-kb1, #homeward-kb2", 10, 1.0, 1.06),
    label_in("homeward", 0.9),
    label_out("homeward", 9.0),
    '    tl.to("#homeward-f1, #homeward-f2", { opacity: 0, duration: 0.5, ease: "power2.in" }, 9.4);\n',
]))

for sid, html in files.items():
    with open(f"{OUT}/compositions/{sid}.html", "w") as f:
        f.write(html)

# ---- root -----------------------------------------------------------------------------------
order = [("intro", 12), ("morning", 9), ("golden", 12), ("sunset", 11), ("night", 12), ("manikaran", 12), ("homeward", 10), ("outro", 12)]
t, hosts = 0, []
for sid, d in order:
    hosts.append(f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                 f'data-start="{t}" data-duration="{d}" data-track-index="1" data-track-kind="graphics" '
                 f'data-width="1920" data-height="1080"></div>')
    t += d
assert t == 90, t

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
    <div id="root" data-composition-id="main" data-start="0" data-duration="90" data-width="1920" data-height="1080">
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
with open(f"{OUT}/index.html", "w") as f:
    f.write(index)
print("wrote", list(files), "total", t)
