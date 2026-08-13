"""Generate the persona click-through demo pages from per-persona flow specs.

Each persona folder (student/, instructor/, tenant_admin/, super_admin/) holds:
    flow.json            — the wiring spec (screens, labels, hotspots)
    screenshots/         — screen-NN.png full-page captures of the LIVE SkillProof app

flow.json is WRITTEN BY skillproof-qa-tools/demo-capture.js, not by hand. That script
forces one uniform viewport for every capture and measures each hotspot's box off the
live DOM, so a hotspot cannot drift from the screenshot it sits on. Hand-editing
flow.json re-introduces exactly the drift it exists to prevent — re-run the capture
instead.

This script reads each flow.json and emits a fully-static <persona>/index.html: one
`<section class="screen">` per screen holding the screenshot plus transparent,
percentage-positioned `<button class="hotspot">` overlays that call goToScreen().

THE FRAME. Every screen renders FULL BROWSER WIDTH in a viewport-height window that
scrolls INTERNALLY. The captures vary wildly in height (a dashboard is ~1000px, an
analytics rollup is ~6000px); letting that variance reach the viewer is what made the
12 AUG 2026 first attempt feel broken, because every click jumped to a different page
shape. Full-bleed frame + internal scroll keeps all the content, keeps every screen the
same shape, and reads as one running app rather than a gallery of screenshots.

flow.json's `frame` width is the CAPTURE width, asserted against every PNG below. It is
NOT a display cap — the frame stretches to the browser, and hotspots are percentage-based
so they track the image at any scale.

Screenshots carry all of the app's own chrome (navbar, footer), so the page adds none
of its own — only a demo meta-bar for navigating screens and switching personas.
GitHub Pages stays build-free: this runs at dev time and commits static HTML.

Usage:
    python build_prototypes.py                 # build the 4 default personas
    python build_prototypes.py student         # build only named persona folder(s)
"""
import json
import os
import sys
import html

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PERSONAS = ["student", "instructor", "tenant_admin", "super_admin"]

# Persona switcher targets. A demo replacement has to let one person walk all four
# roles without logging into four accounts, so every page links to every other.
PERSONA_NAV = [
    ("student", "Student", "person"),
    ("instructor", "Instructor", "school"),
    ("tenant_admin", "School Admin", "admin_panel_settings"),
    ("super_admin", "Super Admin", "verified_user"),
]

PAGE = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <title>%%TITLE%%</title>
  <link rel="icon" href="../favicon.ico" sizes="16x16 32x32 48x48">
  <link rel="icon" type="image/png" sizes="512x512" href="../assets/wgu-owl-favicon.png">
  <link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
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
      --frame-w: %%FRAME_W%%px;
      --frame-h: %%FRAME_H%%px;
      --bar-h: 96px;
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; }
    body {
      font-family: var(--font-body);
      background: var(--backdrop);
      min-height: 100vh;
    }
    body.metabar-collapsed { --bar-h: 42px; }
    :focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
    .visually-hidden {
      position: absolute; width: 1px; height: 1px;
      overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap;
    }

    /* --- the app window ------------------------------------------------
       FULL BROWSER WIDTH, scrolls internally. The 12 AUG 2026 build pinned this
       at min(1440px, 100%) centred in a grey backdrop, so it read as a floating
       screenshot card rather than the app -- which is not what was asked for.
       Edge-to-edge with the frame owning the only scrollbar is the point: the
       capture fills the window exactly like the live app, and a 6000px-tall
       analytics page scrolls inside the frame instead of resizing the page.
       .stage is block, not flex: a flex row lets a second .active screen
       flex-shrink both children, which produced phantom width readings. */
    .stage {
      display: block;
      padding: 0 0 var(--bar-h);
    }
    .screen { display: none; }
    .screen.active { display: block; }
    .shot {
      position: relative;
      width: 100%;
      height: calc(100vh - var(--bar-h));
      overflow-y: auto;
      overflow-x: hidden;
      background: #fff;
      scroll-behavior: smooth;
      /* iOS: keep the inner scroll from chaining to the page */
      overscroll-behavior: contain;
    }
    /* inner is exactly the image box, so hotspot percentages track the image */
    .shot-inner { position: relative; width: 100%; }
    .shot-inner > img { display: block; width: 100%; height: auto; }

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
      display: flex; align-items: center; gap: 10px;
      padding: 8px 14px; font-size: 13px; flex-wrap: wrap;
    }
    .meta-id { font-weight: 700; }
    .meta-bar-header .spacer { margin-left: auto; }
    .persona-link {
      display: inline-flex; align-items: center; gap: 5px;
      color: var(--text-dim); text-decoration: none;
      border: 1px solid var(--pill-border); border-radius: 999px;
      padding: 3px 10px; font-size: 12px; font-weight: 600;
    }
    .persona-link:hover { color: #fff; background: var(--nav-bg-2); }
    .persona-link[aria-current="page"] {
      background: var(--accent); color: #fff; border-color: var(--accent);
    }
    .persona-link .material-icons-outlined { font-size: 15px; }
    .meta-btn {
      display: inline-flex; align-items: center; justify-content: center;
      background: transparent; color: #fff; border: 1px solid var(--pill-border);
      border-radius: 6px; cursor: pointer; padding: 4px; line-height: 1;
    }
    .meta-btn:hover { background: var(--nav-bg-2); }
    .meta-btn .material-icons-outlined { font-size: 18px; }
    .flow-nav {
      display: flex; flex-wrap: wrap; gap: 6px;
      padding: 0 14px 10px;
      max-height: 54px; overflow-y: auto;
    }
    .step-btn {
      background: var(--pill-bg); color: var(--text-dim);
      border: 1px solid var(--pill-border); border-radius: 999px;
      padding: 3px 10px; font-size: 12px; font-family: var(--font-body);
      cursor: pointer; white-space: nowrap;
    }
    .step-btn:hover { color: #fff; border-color: rgba(255,255,255,0.4); }
    .step-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }
    .meta-bar.metabar-collapsed .flow-nav { display: none; }
  </style>
</head>
<body>

<div class="stage">
%%SCREENS%%
</div>

  <nav class="meta-bar" aria-label="Demo navigation">
    <div class="meta-bar-header">
      <span class="meta-id">%%METABAR_LABEL%%</span>
      <span class="visually-hidden">Switch role:</span>
%%PERSONA_LINKS%%
      <span class="spacer"></span>
      <a href="../" class="persona-link">&larr; Index</a>
      <button class="meta-btn" type="button" onclick="toggleReveal()" aria-pressed="false"
              title="Highlight the clickable areas on this screen" aria-label="Highlight clickable areas">
        <span class="material-icons-outlined">ads_click</span>
      </button>
      <button class="meta-btn meta-bar-toggle" type="button" onclick="toggleMetaBar()"
              aria-expanded="true" aria-label="Hide or show the navigation bar" title="Hide/show this navigation bar">
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
      // Reset the frame's internal scroll: arriving on a screen should show its top,
      // the same as a real navigation would.
      var box = t.querySelector('.shot');
      if (box) box.scrollTop = 0;
      window.scrollTo(0, 0);
      var h = t.querySelector('.screen-heading');
      if (h) { h.focus({ preventScroll: true }); }
      try { history.replaceState(null, '', '?screen=' + n); } catch (e) {}
    };

    document.querySelectorAll('.step-btn').forEach(function (b) {
      b.addEventListener('click', function () { goToScreen(parseInt(b.getAttribute('data-goto'), 10)); });
    });

    document.addEventListener('keydown', function (e) {
      if (e.target && /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) return;
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

    var p = new URLSearchParams(location.search);
    var d = parseInt(p.get('screen'), 10);
    if (d >= 1 && d <= TOTAL) goToScreen(d);
  })();
  </script>
</body>
</html>
"""


def esc(s):
    return html.escape(str(s), quote=True)


def render_hotspot(w):
    pct = w["pct"]
    style = "left:{left}%;top:{top}%;width:{width}%;height:{height}%;".format(**pct)
    if w.get("action"):
        onclick = w["action"] if w["action"].strip().endswith(")") else w["action"] + "()"
    else:
        onclick = "goToScreen({})".format(int(w["goto"]))
    label = esc(w.get("label", "Navigate"))
    return ('        <button class="hotspot" style="{style}" aria-label="{label}" '
            'onclick="{onclick}"></button>').format(style=style, label=label, onclick=onclick)


def render_screen(scr, persona, version):
    n = int(scr["n"])
    label = scr.get("label", "Screen {}".format(n))
    src = "screenshots/{}?v={}".format(scr["file"], version)
    alt = esc("{}: {}".format(persona.replace("_", " ").title(), label))
    hotspots = "\n".join(render_hotspot(w) for w in scr.get("wire", []))
    active = " active" if n == 1 else ""
    return (
        '  <section class="screen{active}" id="screen-{n}" aria-labelledby="s{n}-heading">\n'
        '    <h2 id="s{n}-heading" class="screen-heading visually-hidden" tabindex="-1">Screen {n} — {label}</h2>\n'
        '    <div class="shot">\n'
        '      <div class="shot-inner">\n'
        '        <img src="{src}" alt="{alt}">\n'
        '{hotspots}\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>'
    ).format(active=active, n=n, label=esc(label), src=esc(src), alt=alt, hotspots=hotspots)


def render_step_btn(scr):
    n = int(scr["n"])
    label = esc("{:02d} {}".format(n, scr.get("label", "")))
    cls = "step-btn active" if n == 1 else "step-btn"
    cur = "step" if n == 1 else "false"
    return ('      <button class="{cls}" data-goto="{n}" role="tab" aria-current="{cur}">{label}</button>'
            ).format(cls=cls, n=n, cur=cur, label=label)


def render_persona_links(current):
    out = []
    for slug, name, icon in PERSONA_NAV:
        cur = ' aria-current="page"' if slug == current else ''
        out.append(
            '      <a class="persona-link" href="../{slug}/"{cur}>'
            '<span class="material-icons-outlined">{icon}</span>{name}</a>'.format(
                slug=slug, cur=cur, icon=icon, name=esc(name)))
    return "\n".join(out)


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
    frame = flow.get("frame") or {"width": 1440, "height": 900}

    # Every screenshot must be the frame width. A mismatch means the capture and the
    # frame disagree, which is the defect that made the first attempt feel broken, so
    # refuse to build rather than emit a page that jumps size.
    shots_dir = os.path.join(persona_dir, "screenshots")
    bad = []
    for s in screens:
        p = os.path.join(shots_dir, s["file"])
        if not os.path.isfile(p):
            bad.append("{} (missing)".format(s["file"]))
            continue
        with open(p, "rb") as fh:
            head = fh.read(24)
        w = int.from_bytes(head[16:20], "big")
        if w != int(frame["width"]):
            bad.append("{} is {}px, frame is {}px".format(s["file"], w, frame["width"]))
    if bad:
        print("  ABORT {}: {}".format(persona, "; ".join(bad)))
        return False

    hotspot_count = sum(len(s.get("wire", [])) for s in screens)
    screens_html = "\n".join(render_screen(s, persona, version) for s in screens)
    steps_html = "\n".join(render_step_btn(s) for s in screens)

    page = (PAGE
            .replace("%%TITLE%%", esc(flow.get("title", "SkillProof — " + persona)))
            .replace("%%METABAR_LABEL%%", esc(flow.get("metabarLabel", "SkillProof Demo")))
            .replace("%%SCREENS%%", screens_html)
            .replace("%%STEP_BTNS%%", steps_html)
            .replace("%%PERSONA_LINKS%%", render_persona_links(persona))
            .replace("%%FRAME_W%%", str(int(frame["width"])))
            .replace("%%FRAME_H%%", str(int(frame["height"])))
            .replace("%%TOTAL%%", str(total)))

    out_path = os.path.join(persona_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print("  built {}  ({} screens, {} hotspots, frame {}x{})".format(
        os.path.relpath(out_path, REPO_ROOT), total, hotspot_count,
        frame["width"], frame["height"]))
    return True


def main():
    targets = sys.argv[1:] or DEFAULT_PERSONAS
    dirs = []
    for t in targets:
        dirs.append(t if os.path.isabs(t) or os.sep in t or "/" in t else os.path.join(REPO_ROOT, t))
    print("Building {} demo page(s)...".format(len(dirs)))
    built = sum(1 for d in dirs if build(d))
    print("Done -- {} page(s) generated.".format(built))
    if built != len(dirs):
        sys.exit(1)


if __name__ == "__main__":
    main()
