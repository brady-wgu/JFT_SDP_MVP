"""Generate the persona screenshot click-through prototypes from per-persona flow specs.

Each persona folder (student/, instructor/, tenant_admin/, super_admin/) holds:
    flow.json            — the wiring spec (screens, labels, hotspots) — hand-authored
    screenshots/         — screen-NN.png full-page captures of the LIVE SkillProof app
    screenshots_dark/    — optional dark-theme set (enables the theme toggle when complete)

This script reads each flow.json and emits a fully-static <persona>/index.html: one
`<section class="screen">` per screen containing the screenshot plus transparent,
percentage-positioned `<button class="hotspot">` overlays that call goToScreen(). The
screenshots carry all of the app's own chrome (navbar, footer), so the prototype adds
none of its own — only a collapsible demo "meta-bar" for navigating between screens.

Hotspot coordinates are PERCENTAGES of each screenshot (produced by capture-screen.js in
skillproof-qa-tools/), so they are resolution/DPR-independent and track the image at any
render width. GitHub Pages stays build-free: this runs at dev time and commits static HTML,
exactly like capture_screens.py.

Usage:
    python build_prototypes.py                 # build the 4 default personas
    python build_prototypes.py student         # build only named persona folder(s)
    python build_prototypes.py ../scratch/foo  # build an arbitrary dir holding flow.json

flow.json schema:
    {
      "persona": "student",
      "title": "SkillProof — Coding Coach (Student)",
      "metabarLabel": "SkillProof Project Link Page · Student",
      "v": 1,                       # cache-bust version appended to every screenshot src
      "hasDark": false,             # only honoured if a full screenshots_dark set exists
      "screens": [
        { "n": 1, "file": "screen-01.png", "label": "Coding Coach landing", "docW": 1344,
          "wire": [
            { "label": "Begin Diagnostic", "goto": 2,
              "pct": { "left": 11.61, "top": 47.84, "width": 14.84, "height": 4.49 } }
          ] }
      ]
    }
Each wire entry needs a "pct" box and either a "goto" (target screen number) or an
"action" (a JS call such as "toggleTheme()"). Screens are rendered in list order.
"""
import json
import os
import sys
import html

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PERSONAS = ["student", "instructor", "tenant_admin", "super_admin"]

# --- page template (token-replaced; tokens are %%NAME%% to avoid brace escaping) ---

PAGE = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <title>%%TITLE%%</title>
  <link rel="icon" type="image/png" href="../assets/wgu-favicon.png">
  <link rel="stylesheet" href="https://brady-wgu.github.io/brady-design-system/fonts/aptos.css">
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
  <style>
    :root {
      --nav-bg: #0A2540;
      --nav-bg-2: #0F2B4A;
      --accent: #0070F0;
      --pill-bg: #13294d;
      --pill-border: rgba(255,255,255,0.14);
      --backdrop: #55657a;
      --text-dim: rgba(255,255,255,0.72);
      --font-body: 'Aptos', Arial, sans-serif;
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; }
    body {
      font-family: var(--font-body);
      background: var(--backdrop);
      padding-bottom: 148px; /* room for the expanded meta-bar */
    }
    body.metabar-collapsed { padding-bottom: 46px; }
    :focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
    .visually-hidden {
      position: absolute; width: 1px; height: 1px;
      overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap;
    }

    /* --- screens --- */
    .screen { display: none; }
    .screen.active { display: block; }
    .shot {
      position: relative;
      width: 100%;
      max-width: var(--shot-css-w, 1344px);
      margin: 0 auto;
      background: #fff;
      box-shadow: 0 10px 40px rgba(0,0,0,0.25);
    }
    .shot > img { display: block; width: 100%; height: auto; }

    /* --- hotspots --- */
    .hotspot {
      position: absolute;
      margin: 0; padding: 0; border: 0;
      background: transparent;
      cursor: pointer;
      border-radius: 6px;
      transition: background 120ms, box-shadow 120ms;
    }
    .hotspot:hover,
    body.reveal-hotspots .hotspot {
      background: rgba(0,112,240,0.20);
      box-shadow: 0 0 0 2px rgba(0,112,240,0.65) inset;
    }
    .hotspot:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }

    /* --- demo meta-bar --- */
    .meta-bar {
      position: fixed; left: 0; right: 0; bottom: 0; z-index: 50;
      background: var(--nav-bg);
      color: #fff;
      border-top: 1px solid rgba(255,255,255,0.12);
      box-shadow: 0 -6px 24px rgba(0,0,0,0.28);
    }
    .meta-bar-header {
      display: flex; align-items: center; gap: 12px;
      padding: 9px 16px; font-size: 13px;
    }
    .meta-id { font-weight: 700; letter-spacing: 0.01em; }
    .meta-bar-header .sep { color: var(--text-dim); }
    .meta-link { color: #8fc4ff; text-decoration: none; font-weight: 600; }
    .meta-link:hover { text-decoration: underline; }
    .meta-btn {
      display: inline-flex; align-items: center; justify-content: center;
      background: transparent; color: #fff; border: 1px solid var(--pill-border);
      border-radius: 6px; cursor: pointer; padding: 4px; line-height: 1;
    }
    .meta-btn:hover { background: var(--nav-bg-2); }
    .meta-btn .material-icons-outlined { font-size: 18px; }
    .flow-nav {
      display: flex; flex-wrap: wrap; gap: 6px;
      padding: 0 16px 12px;
      max-height: 96px; overflow-y: auto;
    }
    .step-btn {
      background: var(--pill-bg); color: var(--text-dim);
      border: 1px solid var(--pill-border); border-radius: 999px;
      padding: 4px 11px; font-size: 12px; font-family: var(--font-body);
      cursor: pointer; white-space: nowrap;
    }
    .step-btn:hover { color: #fff; border-color: rgba(255,255,255,0.4); }
    .step-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }
    .meta-bar.metabar-collapsed .flow-nav { display: none; }
  </style>
</head>
<body>

%%SCREENS%%

  <nav class="meta-bar" aria-label="Storyboard navigation">
    <div class="meta-bar-header">
      <span class="meta-id">%%METABAR_LABEL%%</span>
      <span class="sep" style="margin-left:auto;"></span>
      <a href="../" class="meta-link">&larr; Storyboard Index</a>
      <button class="meta-btn" type="button" onclick="toggleReveal()" aria-pressed="false"
              title="Highlight the clickable areas on this screen" aria-label="Highlight clickable areas">
        <span class="material-icons-outlined">ads_click</span>
      </button>%%THEME_BTN%%
      <button class="meta-btn meta-bar-toggle" type="button" onclick="toggleMetaBar()"
              aria-expanded="true" aria-label="Hide/show the navigation bar" title="Hide/show this navigation bar">
        <span class="material-icons-outlined">expand_more</span>
      </button>
    </div>
    <div class="flow-nav" role="tablist" aria-label="Screen jump buttons">
%%STEP_BTNS%%
    </div>
  </nav>

  <script>
  (function () {
    var TOTAL = %%TOTAL%%;

    window.goToScreen = function (n) {
      if (n < 1 || n > TOTAL) return;
      document.querySelectorAll('.screen').forEach(function (s) { s.classList.remove('active'); });
      document.querySelectorAll('.step-btn').forEach(function (b) {
        var on = (b.getAttribute('data-goto') === String(n));
        b.classList.toggle('active', on);
        b.setAttribute('aria-current', on ? 'step' : 'false');
      });
      var t = document.getElementById('screen-' + n);
      if (!t) return;
      t.classList.add('active');
      window.scrollTo(0, 0);
      var h = t.querySelector('.screen-heading');
      if (h) { h.focus({ preventScroll: true }); }
      try { history.replaceState(null, '', '?screen=' + n); } catch (e) {}
    };

    document.querySelectorAll('.step-btn').forEach(function (b) {
      b.addEventListener('click', function () { goToScreen(parseInt(b.getAttribute('data-goto'), 10)); });
    });

    document.addEventListener('keydown', function (e) {
      var a = document.querySelector('.screen.active'); if (!a) return;
      var m = a.id.match(/^screen-(\d+)$/); if (!m) return;
      var n = parseInt(m[1], 10);
      if (e.key === 'ArrowRight' && n < TOTAL) goToScreen(n + 1);
      if (e.key === 'ArrowLeft'  && n > 1)     goToScreen(n - 1);
    });

    var KEY = 'skillproof-metabar-collapsed';
    var bar = document.querySelector('.meta-bar');
    var toggle = bar && bar.querySelector('.meta-bar-toggle');
    function applyBar(c) {
      if (!bar) return;
      bar.classList.toggle('metabar-collapsed', c);
      document.body.classList.toggle('metabar-collapsed', c);
      if (toggle) toggle.setAttribute('aria-expanded', String(!c));
    }
    applyBar(localStorage.getItem(KEY) === '1');
    window.toggleMetaBar = function () {
      var c = !bar.classList.contains('metabar-collapsed');
      applyBar(c); localStorage.setItem(KEY, c ? '1' : '0');
    };

    window.toggleReveal = function () {
      var on = document.body.classList.toggle('reveal-hotspots');
      var b = document.querySelector('.meta-btn[onclick="toggleReveal()"]');
      if (b) b.setAttribute('aria-pressed', String(on));
    };
%%THEME_JS%%
    var p = new URLSearchParams(location.search);
    var d = parseInt(p.get('screen'), 10);
    if (d >= 1 && d <= TOTAL) goToScreen(d);
  })();
  </script>
</body>
</html>
"""

THEME_BTN = r"""
      <button class="meta-btn" type="button" onclick="toggleTheme()"
              title="Toggle light / dark screenshots" aria-label="Toggle light or dark theme">
        <span class="material-icons-outlined">dark_mode</span>
      </button>"""

THEME_JS = r"""
    function swapShotTheme(theme) {
      document.querySelectorAll('.shot > img').forEach(function (img) {
        img.setAttribute('src', img.getAttribute('src').replace(/screenshots(_dark)?\//, theme === 'dark' ? 'screenshots_dark/' : 'screenshots/'));
      });
    }
    window.toggleTheme = function () {
      var dark = document.documentElement.getAttribute('data-theme') === 'dark';
      var next = dark ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      swapShotTheme(next);
      localStorage.setItem('skillproof-theme', next);
    };
    (function () {
      if (localStorage.getItem('skillproof-theme') === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        swapShotTheme('dark');
      }
    })();
"""


def esc(s):
    return html.escape(str(s), quote=True)


def render_hotspot(w):
    pct = w["pct"]
    style = "left:{left}%;top:{top}%;width:{width}%;height:{height}%;".format(**pct)
    if "action" in w and w["action"]:
        onclick = w["action"] if w["action"].strip().endswith(")") else w["action"] + "()"
    else:
        onclick = "goToScreen({})".format(int(w["goto"]))
    label = esc(w.get("label", "Navigate"))
    return ('    <button class="hotspot" style="{style}" aria-label="{label}" '
            'onclick="{onclick}"></button>').format(style=style, label=label, onclick=onclick)


def render_screen(scr, persona, version, has_dark):
    n = int(scr["n"])
    label = scr.get("label", "Screen {}".format(n))
    docw = scr.get("docW")
    shot_w = "--shot-css-w:{}px;".format(int(docw)) if docw else ""
    src = "screenshots/{}?v={}".format(scr["file"], version)
    alt = esc("{} screen {}: {}".format(persona, n, label))
    hotspots = "\n".join(render_hotspot(w) for w in scr.get("wire", []))
    active = " active" if n == 1 else ""
    return (
        '  <section class="screen{active}" id="screen-{n}" aria-labelledby="s{n}-heading">\n'
        '    <h2 id="s{n}-heading" class="screen-heading visually-hidden" tabindex="-1">Screen {n} — {label}</h2>\n'
        '    <div class="shot" style="{shot_w}">\n'
        '      <img src="{src}" alt="{alt}">\n'
        '{hotspots}\n'
        '    </div>\n'
        '  </section>'
    ).format(active=active, n=n, label=esc(label), shot_w=shot_w, src=esc(src), alt=alt, hotspots=hotspots)


def render_step_btn(scr):
    n = int(scr["n"])
    label = esc("{:02d} {}".format(n, scr.get("label", "")))
    cls = "step-btn active" if n == 1 else "step-btn"
    cur = "step" if n == 1 else "false"
    return ('      <button class="{cls}" data-goto="{n}" role="tab" aria-current="{cur}">{label}</button>'
            ).format(cls=cls, n=n, cur=cur, label=label)


def full_dark_set_exists(persona_dir, screens):
    dark_dir = os.path.join(persona_dir, "screenshots_dark")
    if not os.path.isdir(dark_dir):
        return False
    return all(os.path.isfile(os.path.join(dark_dir, s["file"])) for s in screens)


def build(persona_dir):
    persona_dir = os.path.abspath(persona_dir)
    flow_path = os.path.join(persona_dir, "flow.json")
    if not os.path.isfile(flow_path):
        print("  SKIP {} (no flow.json)".format(persona_dir))
        return False
    with open(flow_path, "r", encoding="utf-8") as f:
        flow = json.load(f)

    persona = flow.get("persona", os.path.basename(persona_dir))
    screens = flow["screens"]
    version = flow.get("v", 1)
    total = len(screens)

    has_dark = bool(flow.get("hasDark")) and full_dark_set_exists(persona_dir, screens)
    if flow.get("hasDark") and not has_dark:
        print("  note: hasDark requested but the dark set is incomplete → theme toggle omitted")

    screens_html = "\n".join(render_screen(s, persona, version, has_dark) for s in screens)
    steps_html = "\n".join(render_step_btn(s) for s in screens)

    page = (PAGE
            .replace("%%TITLE%%", esc(flow.get("title", "SkillProof — " + persona)))
            .replace("%%METABAR_LABEL%%", esc(flow.get("metabarLabel", "SkillProof Project Link Page")))
            .replace("%%SCREENS%%", screens_html)
            .replace("%%STEP_BTNS%%", steps_html)
            .replace("%%TOTAL%%", str(total))
            .replace("%%THEME_BTN%%", THEME_BTN if has_dark else "")
            .replace("%%THEME_JS%%", THEME_JS if has_dark else ""))

    out_path = os.path.join(persona_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print("  built {}  ({} screens, dark={})".format(os.path.relpath(out_path, REPO_ROOT), total, has_dark))
    return True


def main():
    targets = sys.argv[1:] or DEFAULT_PERSONAS
    dirs = []
    for t in targets:
        dirs.append(t if os.path.isabs(t) or os.sep in t or "/" in t else os.path.join(REPO_ROOT, t))
    print("Building {} prototype(s)...".format(len(dirs)))
    built = sum(1 for d in dirs if build(d))
    print("Done -- {} page(s) generated.".format(built))


if __name__ == "__main__":
    main()
