"""Builds four 1080x1350 Instagram collage posts from the trip photos.

Run from the project folder:  python3 posts/build_posts.py
Writes posts/src/post-N.html, then renders posts/kasol-post-N.jpg with Playwright.
"""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
os.makedirs(SRC, exist_ok=True)
PH = "../../assets/photos/"

HEAD = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,500&family=Poppins:wght@600;700&family=Montserrat:wght@400;500&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 1080px; height: 1350px; overflow: hidden; }
  body { position: relative; font-family: "Montserrat", sans-serif; }
  .ph { position: absolute; overflow: hidden; border-radius: 22px; box-shadow: 0 18px 40px rgba(0,0,0,0.35); }
  .ph img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .dark { background: radial-gradient(ellipse at 50% 20%, #3a1a0a 0%, #170c06 55%, #07080b 100%); }
  .cream { background: radial-gradient(ellipse at 50% 30%, #fdf3e3 0%, #f2d6b0 60%, #e4b986 100%); }
  .kicker { font-size: 24px; letter-spacing: 0.42em; text-transform: uppercase; padding-left: 0.42em; }
  .title { font-family: "Playfair Display", serif; font-weight: 700; letter-spacing: 0.05em; line-height: 1; }
  .sub { font-weight: 500; letter-spacing: 0.16em; text-transform: uppercase; color: #ffc98a;
    text-shadow: 0 0 14px rgba(255,170,90,0.8), 0 0 40px rgba(255,140,60,0.5); }
  .sticker { position: absolute; padding: 12px 26px; border-radius: 16px; font-family: "Poppins", sans-serif;
    font-weight: 700; font-size: 34px; white-space: nowrap; box-shadow: 0 12px 30px rgba(0,0,0,0.35); }
  .s-white { background: #fff; color: #15161a; }
  .s-amber { background: linear-gradient(135deg, #ffd08a, #ff8a3d); color: #2a1206; }
  .s-dark { background: #15161a; color: #ffd9a6; }
  .tag { position: absolute; padding: 8px 20px; border-radius: 999px; font-family: "Poppins", sans-serif; font-weight: 700;
    font-size: 26px; letter-spacing: 0.08em; text-transform: uppercase; box-shadow: 0 8px 22px rgba(0,0,0,0.35); }
  .pol { position: absolute; background: #fffdf8; padding: 18px 18px 0 18px; border-radius: 6px;
    box-shadow: 0 22px 44px rgba(60,30,10,0.35); }
  .pol img { width: 100%; object-fit: cover; display: block; }
  .pol .cap { font-family: "Playfair Display", serif; font-style: italic; font-weight: 500; font-size: 30px;
    color: #3b2414; text-align: center; padding: 14px 0 18px; }
</style></head>"""


def img(name, x, y, w, h, pos="50% 50%", extra=""):
    return (f'<div class="ph" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{extra}">'
            f'<img src="{PH}{name}.jpg" style="object-position:{pos}"></div>')


posts = {}

# 1. Cover ---------------------------------------------------------------------------------
posts[1] = f"""{HEAD}<body class="dark">
  <div style="position:absolute;left:0;top:44px;width:1080px;text-align:center;">
    <div class="kicker" style="color:#e9dccb;">Parvati Valley</div>
    <div class="title" style="font-size:150px;color:#f8f3ea;margin-top:14px;padding-left:0.05em;">KASOL</div>
    <div class="sub" style="font-size:34px;margin-top:16px;padding-left:0.16em;">1st Year Anniversary</div>
  </div>
  {img("couple-heart", 36, 330, 620, 984, "48% 50%")}
  {img("sunset-fire", 680, 330, 364, 312, "50% 45%")}
  {img("couple-selfie-manikaran", 680, 666, 364, 312, "43% 40%")}
  {img("gurudwara-front", 680, 1002, 364, 312, "40% 50%")}
  <div class="sticker s-amber" style="left:70px;top:1220px;transform:rotate(-3deg);">#SayAnAparajitaStory</div>
</body></html>"""

# 2. His vs Her ----------------------------------------------------------------------------
posts[2] = f"""{HEAD}<body class="cream">
  <div style="position:absolute;left:0;top:46px;width:1080px;text-align:center;">
    <div class="title" style="font-size:112px;color:#2a1608;">HIS <span style="color:#ff7a2e;font-style:italic;">vs</span> HER</div>
    <div class="kicker" style="color:#6a4428;margin-top:18px;">Kasol edition</div>
  </div>
  {img("snooker-him", 36, 250, 492, 520, "40% 45%")}
  {img("snooker-her", 552, 250, 492, 520, "55% 42%")}
  {img("him-on-bridge", 36, 794, 492, 520, "55% 50%")}
  {img("her-on-bridge", 552, 794, 492, 520, "52% 50%")}
  <div class="tag" style="left:60px;top:694px;background:#fff;color:#15161a;transform:rotate(-4deg);">His shot</div>
  <div class="tag" style="left:576px;top:694px;background:#ff8a3d;color:#1c0b03;transform:rotate(3deg);">Her shot</div>
  <div class="tag" style="left:60px;top:1238px;background:#fff;color:#15161a;transform:rotate(3deg);">His pose</div>
  <div class="tag" style="left:576px;top:1238px;background:#ff8a3d;color:#1c0b03;transform:rotate(-3deg);">Her pose</div>
  <div class="sticker s-dark" style="left:408px;top:742px;font-size:30px;transform:rotate(-6deg);">Who won?</div>
</body></html>"""

# 3. Polaroid board ------------------------------------------------------------------------
def pol(name, x, y, w, ih, rot, cap, pos="50% 50%"):
    return (f'<div class="pol" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg);">'
            f'<img src="{PH}{name}.jpg" style="height:{ih}px;object-position:{pos}"><div class="cap">{cap}</div></div>')


posts[3] = f"""{HEAD}<body class="cream">
  <div style="position:absolute;left:0;top:40px;width:1080px;text-align:center;">
    <div class="title" style="font-size:96px;color:#2a1608;font-style:italic;font-weight:700;">Kasol diaries</div>
  </div>
  {pol("couple-selfie-cafe", 60, 178, 450, 290, -5, "café hopping", "40% 50%")}
  {pol("her-heart", 575, 170, 440, 290, 4, "heart spot", "45% 55%")}
  {pol("him-river-rock", 70, 568, 440, 290, 3, "rock star", "58% 62%")}
  {pol("couple-selfie-manikaran", 570, 560, 450, 290, -4, "Manikaran", "43% 40%")}
  {pol("couple-cosy-night", 60, 958, 450, 290, -3, "movie night", "26% 50%")}
  {pol("couple-cosy-selfie", 575, 950, 440, 290, 5, "us", "45% 45%")}
  <div class="sticker s-white" style="left:395px;top:500px;transform:rotate(-5deg);z-index:5;">Us, on repeat</div>
</body></html>"""

# 4. 365 days of us ------------------------------------------------------------------------
posts[4] = f"""{HEAD}<body class="dark">
  <div style="position:absolute;left:0;top:44px;width:1080px;text-align:center;">
    <div class="kicker" style="color:#f1e3cf;">Our first year</div>
  </div>
  {img("anniversary-candles-crop", 36, 120, 492, 590, "50% 45%")}
  {img("anniversary-bracelet", 552, 120, 492, 590, "50% 55%")}
  {img("anniversary-cake", 36, 734, 492, 590, "45% 45%")}
  {img("story-coaster", 552, 734, 492, 590, "50% 42%")}
  <div style="position:absolute;left:340px;top:522px;width:400px;height:400px;border-radius:50%;
    background:radial-gradient(circle, #2c1408 0%, #120905 75%);border:4px solid #ffb35c;
    box-shadow:0 0 50px rgba(255,150,70,0.6), 0 20px 50px rgba(0,0,0,0.6);display:flex;flex-direction:column;
    align-items:center;justify-content:center;">
    <div class="title" style="font-size:150px;color:#ffc98a;letter-spacing:0.02em;
      text-shadow:0 0 22px rgba(255,170,90,0.8), 0 0 60px rgba(255,120,50,0.5);">365</div>
    <div style="margin-top:14px;padding:8px 24px;border-radius:999px;background:#fff3e2;color:#2a1206;
      font-family:Poppins,sans-serif;font-weight:700;font-size:28px;letter-spacing:0.1em;text-transform:uppercase;">Days of us</div>
  </div>
  <div class="sticker s-white" style="left:600px;top:150px;font-size:30px;transform:rotate(4deg);">A for always</div>
</body></html>"""

for n, html in posts.items():
    with open(os.path.join(SRC, f"post-{n}.html"), "w") as f:
        f.write(html)

render = r"""
const { chromium } = require('playwright');
(async () => {
  const [src, out] = [process.argv[2], process.argv[3]];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (let n = 1; n <= 4; n++) {
    await page.goto('file://' + src + '/post-' + n + '.html', { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: out + '/kasol-post-' + n + '.jpg', type: 'jpeg', quality: 92 });
  }
  await browser.close();
})();
"""
js = os.path.join(SRC, "render.cjs")
with open(js, "w") as f:
    f.write(render)
subprocess.run(["node", js, SRC, HERE], check=True)
print("rendered", [f"kasol-post-{n}.jpg" for n in posts])
