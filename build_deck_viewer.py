"""Generate deck/index.html -- an in-browser viewer for the status demo deck.

WHY THIS EXISTS
No browser renders .pptx natively, so "view the deck" used to mean "download
41 MB, wait, open PowerPoint". This builds a self-hosted slide viewer from the
PNGs that render_deck.py exports, so the deck opens like any other page.

WHAT IT PRESERVES THAT A FLAT IMAGE EXPORT WOULD LOSE
1. The embedded video on slide 6. That single MP4 is 39.56 of the deck's 41 MB
   and is byte-identical to assets/video/skillproof-walkthrough-2k.mp4, so a
   real <video> is overlaid on the slide's own video region, pointed at the
   existing asset. No second copy, and it plays inline.
2. The deck's hyperlinks. Slide 6 has a "Launch the live STU101 coach" button
   and slide 7 has two links to this site. Real <a> elements are overlaid on
   the exact regions the shapes occupy.

Both overlays are positioned in PERCENTAGES read out of the slide XML (EMU
offsets over slide size), never eyeballed, so they track the deck rather than a
particular render width -- the same approach build_prototypes.py uses for the
persona walkthrough hotspots.

RUN-LEVEL LINK WIDTHS ARE MEASURED, NOT TRUSTED
A hyperlink on a text RUN reports the geometry of its whole containing text
box, which is usually far wider than the visible text. On slide 7 the
"brady-wgu.github.io/SkillProof" line sits in a 45%-wide box but the text only
covers about 15% of the slide. Using the box verbatim would leave a large
invisible click target over blank space that silently navigates away. For those
links the width is narrowed by measuring the actual ink extent in the rendered
PNG. Links attached to a SHAPE (the filled buttons) are already tight and are
used as-is.

Run:  python render_deck.py && python build_deck_viewer.py
"""
import json
import os
import re
import zipfile

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.abspath(__file__))
DECK_REL = 'assets/decks/skillproof-status-demo_v1-1_30JUL2026.pptx'
DECK = os.path.join(REPO, DECK_REL)
SLIDES_DIR = os.path.join(REPO, 'assets', 'decks', 'slides')
OUT = os.path.join(REPO, 'deck', 'index.html')
VIDEO_REL = '../assets/video/skillproof-walkthrough-2k.mp4'

# Bumped whenever the slide PNGs are re-rendered. Slide images are served with a
# ?v= cache-buster for the same reason the persona screenshots are: without it,
# browsers keep showing the previous render.
VERSION = 1

# Hand-checked against the rendered PNGs. Auto-extracting "the first text on the
# slide" picks up the footer on slide 6 rather than its heading, so the labels
# are stated explicitly. If the deck gains slides, unlisted ones fall back to
# "Slide N" and should be named here.
TITLES = {
    1: 'SkillProof — AI Coaching + Extensibility',
    2: 'Program Experience Strategy',
    3: 'Why SkillProof',
    4: 'The coaching loop — diagnostic, feedback, practice',
    5: 'One engine, any subject',
    6: 'STU101 — live walkthrough (video)',
    7: 'Questions — explore on your own',
}


# --------------------------------------------------------------------------
# Deck geometry
# --------------------------------------------------------------------------
def slide_size(z):
    pres = z.read('ppt/presentation.xml').decode('utf-8', 'ignore')
    m = re.search(r'sldSz[^/]*cx="(\d+)"[^/]*cy="(\d+)"', pres)
    return int(m.group(1)), int(m.group(2))


def rels_for(z, num):
    path = f'ppt/slides/_rels/slide{num}.xml.rels'
    out = {}
    if path in z.namelist():
        xml = z.read(path).decode('utf-8', 'ignore')
        for rid, tgt, mode in re.findall(
                r'Id="([^"]+)"\s+Type="[^"]*"\s+Target="([^"]+)"(?:\s+TargetMode="([^"]+)")?', xml):
            out[rid] = (tgt, mode)
    return out


def box(blk, cx, cy):
    off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>', blk)
    ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"/>', blk)
    if not (off and ext):
        return None
    x, y = int(off.group(1)), int(off.group(2))
    w, h = int(ext.group(1)), int(ext.group(2))
    return dict(left=100 * x / cx, top=100 * y / cy,
                width=100 * w / cx, height=100 * h / cy)


def overlaps(a, b):
    return not (a['left'] + a['width'] <= b['left'] or b['left'] + b['width'] <= a['left'] or
                a['top'] + a['height'] <= b['top'] or b['top'] + b['height'] <= a['top'])


def union(a, b):
    l, t = min(a['left'], b['left']), min(a['top'], b['top'])
    r = max(a['left'] + a['width'], b['left'] + b['width'])
    bo = max(a['top'] + a['height'], b['top'] + b['height'])
    return dict(left=l, top=t, width=r - l, height=bo - t)


def measure_ink(png, rect, pad_pct=0.4, gap_pct=1.5):
    """Narrow a rect's width to the visible ink inside it, in slide percentages.

    A run-level hyperlink reports its whole text box. This finds the columns
    that actually differ from the box's background so the click target matches
    what the reader sees.

    It deliberately stops at the first horizontal gap wider than gap_pct of the
    slide rather than spanning leftmost-to-rightmost ink. A text box often
    overhangs whatever sits beside it -- on slide 7 the URL line's box is 45%
    wide and reaches into the screenshot panel that starts at 43%, so
    min-to-max would have measured 40% and produced a hotspot covering most of
    the slide. Word spaces are far narrower than the clear space between two
    shapes, so cutting at the first wide gap isolates the run's own text. The
    text is left-aligned in its box, so the walk starts from the leftmost ink.
    """
    im = Image.open(png).convert('RGB')
    W, H = im.size
    x0 = max(0, int(rect['left'] / 100 * W))
    x1 = min(W, int((rect['left'] + rect['width']) / 100 * W))
    y0 = max(0, int(rect['top'] / 100 * H))
    y1 = min(H, int((rect['top'] + rect['height']) / 100 * H))
    if x1 - x0 < 2 or y1 - y0 < 2:
        return rect

    band = np.asarray(im.crop((x0, y0, x1, y1)), dtype=np.int16)
    # Background = the median colour of the band's outer rows.
    edge = np.concatenate([band[:2].reshape(-1, 3), band[-2:].reshape(-1, 3)])
    bg = np.median(edge, axis=0)
    ink = (np.abs(band - bg).sum(axis=2) > 40).any(axis=0)
    cols = np.nonzero(ink)[0]
    if cols.size == 0:
        return rect

    gap_px = max(4, int(round(gap_pct / 100 * W)))
    start = int(cols.min())
    end = start
    run = 0
    for i in range(start, ink.size):
        if ink[i]:
            end = i
            run = 0
        else:
            run += 1
            if run >= gap_px:
                break

    left_px, right_px = x0 + start, x0 + end + 1
    out = dict(rect)
    out['left'] = 100 * left_px / W - pad_pct
    out['width'] = 100 * (right_px - left_px) / W + 2 * pad_pct
    return out


def extract(z, num, cx, cy, png):
    """Return ([link rects], video rect or None) for one slide."""
    xml = z.read(f'ppt/slides/slide{num}.xml').decode('utf-8', 'ignore')
    rels = rels_for(z, num)

    video = None
    links = []          # (url, rect, is_run_level)
    for blk in re.findall(r'<p:(?:sp|pic|graphicFrame)>.*?</p:(?:sp|pic|graphicFrame)>', xml, re.S):
        b = box(blk, cx, cy)
        if b is None:
            continue
        if 'videoFile' in blk and video is None:
            video = b
        for rid in dict.fromkeys(re.findall(r'<a:hlinkClick[^>]*r:id="([^"]+)"', blk)):
            tgt, mode = rels.get(rid, (None, None))
            if not tgt or mode != 'External':
                continue
            run_level = bool(re.search(
                r'<a:rPr[^>]*>(?:\s*<[^>]+>)*?\s*<a:hlinkClick[^>]*r:id="' + re.escape(rid), blk))
            text = ' '.join(t.strip() for t in re.findall(r'<a:t>([^<]*)</a:t>', blk) if t.strip())
            links.append(dict(url=tgt, rect=b, run=run_level, text=text[:80]))

    # A button is authored as several stacked shapes (fill + icon + label) that
    # all carry the same link. Merge overlapping same-URL rects so one anchor
    # covers the button instead of three fighting for the same clicks.
    merged = []
    for item in links:
        for m in merged:
            if m['url'] == item['url'] and overlaps(m['rect'], item['rect']):
                m['rect'] = union(m['rect'], item['rect'])
                m['run'] = m['run'] and item['run']
                m['text'] = m['text'] or item['text']
                break
        else:
            merged.append(dict(item))

    for m in merged:
        if m['run']:
            m['rect'] = measure_ink(png, m['rect'])
    return merged, video


# --------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------
PAGE = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SkillProof — Status Demo Deck</title>
  <link rel="icon" href="../favicon.ico" sizes="16x16 32x32 48x48">
  <link rel="icon" type="image/png" sizes="512x512" href="../assets/wgu-owl-favicon.png">
  <link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
  <link rel="stylesheet" href="https://brady-wgu.github.io/brady-design-system/fonts/aptos.css">
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">

  <!--
    GENERATED by build_deck_viewer.py -- do not hand-edit; edits are overwritten
    on the next build. Slides are PNGs exported from the .pptx by render_deck.py.
    The video on slide 6 and every deck hyperlink are overlaid as real elements,
    positioned in percentages read out of the slide XML.
  -->

  <style>
    :root {
      --navy: #001730;
      --panel: #0A2540;
      --accent: #0070F0;
      --sky: #46B1EF;
      --bar-h: 56px;
      --font-heading: 'Aptos Display', Arial, sans-serif;
      --font-body: 'Aptos', Arial, sans-serif;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--font-body);
      background: var(--navy);
      color: #fff;
      min-height: 100vh;
      overflow: hidden;            /* the stage sizes itself; the page never scrolls */
    }
    a { color: var(--sky); }
    :focus-visible { outline: 3px solid var(--sky); outline-offset: 2px; }

    .skip-nav { position: absolute; left: -9999px; }
    .skip-nav:focus { left: 8px; top: 8px; z-index: 99; padding: 8px 16px;
                      background: var(--accent); color: #fff; font-weight: 700; }

    /* ---------------- top bar ---------------- */
    .bar {
      height: var(--bar-h);
      display: flex; align-items: center; gap: 16px;
      padding: 0 20px;
      background: var(--panel);
      border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    .bar-brand {
      display: flex; align-items: center; gap: 10px;
      color: #fff; text-decoration: none; font-weight: 700; font-size: 14px;
      white-space: nowrap;
    }
    .bar-brand img { height: 24px; }
    .bar-title {
      font-family: var(--font-heading); font-size: 14px; font-weight: 700;
      color: rgba(255,255,255,0.65);
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .bar-spacer { flex: 1 1 auto; }
    .bar-btn {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 7px 12px; border-radius: 8px;
      background: transparent; color: rgba(255,255,255,0.8);
      border: 1px solid rgba(255,255,255,0.22);
      font-family: var(--font-body); font-size: 13px; font-weight: 700;
      text-decoration: none; cursor: pointer;
      transition: background 150ms, border-color 150ms, color 150ms;
      white-space: nowrap;
    }
    .bar-btn:hover:not(:disabled) { background: rgba(255,255,255,0.1); border-color: #fff; color: #fff; text-decoration: none; }
    .bar-btn:disabled { opacity: 0.35; cursor: default; }
    .bar-btn .material-icons-outlined { font-size: 17px; }
    .counter {
      font-variant-numeric: tabular-nums; font-size: 13px; font-weight: 700;
      color: rgba(255,255,255,0.8); min-width: 52px; text-align: center;
    }
    @media (max-width: 860px) { .bar-title, .bar-label { display: none; } }

    /* ---------------- stage ----------------
       The slide is a fixed 16:9 box sized to whichever of width or height runs
       out first, so the whole slide is always visible without page scrolling. */
    .stage {
      height: calc(100vh - var(--bar-h));
      display: flex; align-items: center; justify-content: center;
      padding: 18px;
    }
    .slide-box {
      position: relative;
      width: min(100%, calc((100vh - var(--bar-h) - 36px) * 16 / 9));
      aspect-ratio: 16 / 9;
      background: #000;
      box-shadow: 0 18px 50px rgba(0,0,0,0.5);
      border: 1px solid rgba(255,255,255,0.1);
      overflow: hidden;
    }
    .slide { display: none; position: absolute; inset: 0; }
    .slide.active { display: block; }
    .slide img { display: block; width: 100%; height: 100%; }

    /* Real player over the slide's own video region. */
    .slide video {
      position: absolute; display: block;
      background: #fff; object-fit: contain; z-index: 2;
    }
    /* Real anchors over the deck's hyperlink shapes. Invisible until hovered or
       focused, so the slide looks like the slide but the links still work. */
    .hot {
      position: absolute; z-index: 3;
      border-radius: 6px;
      background: transparent;
      box-shadow: 0 0 0 0 rgba(70,177,239,0);
      transition: background 120ms, box-shadow 120ms;
    }
    .hot:hover, .hot:focus-visible {
      background: rgba(70,177,239,0.22);
      box-shadow: 0 0 0 2px var(--sky);
    }

    /* ---------------- thumbnails ---------------- */
    .rail {
      position: fixed; bottom: 0; left: 0; right: 0;
      display: flex; gap: 8px; justify-content: center; align-items: center;
      padding: 8px 12px;
      background: linear-gradient(to top, rgba(0,23,48,0.94), rgba(0,23,48,0));
      opacity: 0; transition: opacity 180ms; pointer-events: none;
    }
    .rail.show, .rail:hover, .rail:focus-within { opacity: 1; pointer-events: auto; }
    .rail button {
      width: 12px; height: 12px; padding: 0; border-radius: 50%;
      border: 1px solid rgba(255,255,255,0.5);
      background: transparent; cursor: pointer;
      transition: background 120ms, transform 120ms;
    }
    .rail button:hover { transform: scale(1.25); }
    .rail button[aria-current="true"] { background: var(--sky); border-color: var(--sky); }

    .sr-only {
      position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
      overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0;
    }
  </style>
</head>
<body>

<a href="#slide-stage" class="skip-nav">Skip to the slides</a>

<header class="bar">
  <a class="bar-brand" href="../index.html">
    <img src="../assets/wgu-corporation-full-color-reverse.png" alt="WGU">
    SkillProof
  </a>
  <span class="bar-title">Status Demo Deck &middot; v1.1 &middot; 30 JUL 2026</span>

  <span class="bar-spacer"></span>

  <button class="bar-btn" id="prev" type="button">
    <span class="material-icons-outlined">chevron_left</span><span class="bar-label">Prev</span>
  </button>
  <span class="counter" id="counter">1 / %%COUNT%%</span>
  <button class="bar-btn" id="next" type="button">
    <span class="bar-label">Next</span><span class="material-icons-outlined">chevron_right</span>
  </button>

  <button class="bar-btn" id="full" type="button" title="Full screen (F)">
    <span class="material-icons-outlined">fullscreen</span>
  </button>
  <a class="bar-btn" href="%%DECK%%" download
     title="Download the original PowerPoint file (%%SIZE%% MB)">
    <span class="material-icons-outlined">download</span><span class="bar-label">.pptx</span>
  </a>
</header>

<main class="stage" id="slide-stage">
  <div class="slide-box" id="box">
%%SLIDES%%
  </div>
</main>

<nav class="rail" id="rail" aria-label="Jump to slide">
%%DOTS%%
</nav>

<p class="sr-only" aria-live="polite" id="live"></p>

<script>
  var TITLES = %%TITLES%%;
  var COUNT = %%COUNT%%;
  var cur = 1;

  var slides  = [].slice.call(document.querySelectorAll('.slide'));
  var dots    = [].slice.call(document.querySelectorAll('#rail button'));
  var counter = document.getElementById('counter');
  var live    = document.getElementById('live');
  var prevBtn = document.getElementById('prev');
  var nextBtn = document.getElementById('next');
  var rail    = document.getElementById('rail');

  function show(n, opts) {
    n = Math.max(1, Math.min(COUNT, n));
    cur = n;
    slides.forEach(function (s) {
      var on = +s.dataset.n === n;
      s.classList.toggle('active', on);
      // Slides that are not showing must not be reachable by keyboard, or Tab
      // would walk into links on hidden slides.
      [].slice.call(s.querySelectorAll('a.hot')).forEach(function (a) {
        if (on) { a.removeAttribute('tabindex'); } else { a.setAttribute('tabindex', '-1'); }
      });
      // Never leave the walkthrough playing behind a slide the viewer left.
      var v = s.querySelector('video');
      if (v && !on && !v.paused) { v.pause(); }
    });
    dots.forEach(function (d, i) { d.setAttribute('aria-current', i + 1 === n ? 'true' : 'false'); });
    counter.textContent = n + ' / ' + COUNT;
    prevBtn.disabled = (n === 1);
    nextBtn.disabled = (n === COUNT);
    live.textContent = 'Slide ' + n + ' of ' + COUNT + ': ' + (TITLES[n] || '');
    if (!opts || !opts.silent) {
      history.replaceState(null, '', '#' + n);
    }
    preload(n + 1); preload(n - 1);
    flashRail();
  }

  // Fetch the neighbouring slide images so paging does not flash white.
  var warmed = {};
  function preload(n) {
    if (n < 1 || n > COUNT || warmed[n]) { return; }
    warmed[n] = true;
    var img = slides[n - 1] && slides[n - 1].querySelector('img');
    if (img && img.getAttribute('loading') === 'lazy') { img.removeAttribute('loading'); }
  }

  var railTimer;
  function flashRail() {
    rail.classList.add('show');
    clearTimeout(railTimer);
    railTimer = setTimeout(function () { rail.classList.remove('show'); }, 1600);
  }

  prevBtn.addEventListener('click', function () { show(cur - 1); });
  nextBtn.addEventListener('click', function () { show(cur + 1); });
  dots.forEach(function (d, i) { d.addEventListener('click', function () { show(i + 1); }); });

  document.getElementById('full').addEventListener('click', function () {
    if (document.fullscreenElement) { document.exitFullscreen(); }
    else if (document.documentElement.requestFullscreen) { document.documentElement.requestFullscreen(); }
  });

  document.addEventListener('keydown', function (e) {
    var t = e.target || {};
    var tag = (t.tagName || '').toLowerCase();
    // Let the video keep its own keyboard handling (space, arrows to seek).
    if (tag === 'video' || tag === 'input' || tag === 'textarea') { return; }
    if (e.key === 'ArrowRight' || e.key === 'PageDown') { show(cur + 1); e.preventDefault(); }
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { show(cur - 1); e.preventDefault(); }
    else if (e.key === 'Home') { show(1); e.preventDefault(); }
    else if (e.key === 'End') { show(COUNT); e.preventDefault(); }
    else if (e.key === 'f' || e.key === 'F') { document.getElementById('full').click(); }
  });

  // Deep-linkable: /deck/#4 opens on slide 4, and Back/Forward step through.
  function fromHash() {
    var n = parseInt((location.hash || '').replace('#', ''), 10);
    return (n >= 1 && n <= COUNT) ? n : 1;
  }
  window.addEventListener('hashchange', function () { show(fromHash(), { silent: true }); });
  show(fromHash(), { silent: true });
</script>

</body>
</html>
"""


def main():
    z = zipfile.ZipFile(DECK)
    cx, cy = slide_size(z)
    count = len([n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)])

    rendered = sorted(f for f in os.listdir(SLIDES_DIR) if re.match(r'slide-\d+\.png$', f))
    if len(rendered) != count:
        raise SystemExit(f'{len(rendered)} PNGs in {SLIDES_DIR} but the deck has {count} '
                         f'slides -- run render_deck.py first')

    blocks, dots, n_links, n_video = [], [], 0, 0
    for n in range(1, count + 1):
        png = os.path.join(SLIDES_DIR, f'slide-{n}.png')
        links, video = extract(z, n, cx, cy, png)
        title = TITLES.get(n, f'Slide {n}')

        parts = [f'    <div class="slide" data-n="{n}">']
        # Only the first slide loads eagerly; the rest are pulled in as the
        # viewer approaches them (see preload() in the page script).
        lazy = '' if n == 1 else ' loading="lazy"'
        parts.append(f'      <img src="../assets/decks/slides/slide-{n}.png?v={VERSION}"'
                     f'{lazy} alt="Slide {n} of {count}: {esc(title)}">')

        if video:
            n_video += 1
            # preload="none" matters: this is a 40 MB file and most viewers never
            # reach slide 6. The poster is cropped from the slide's own render so
            # the region looks identical until someone presses play.
            parts.append(
                f'      <video controls preload="none"'
                f' poster="../assets/decks/slides/slide-{n}-video-poster.png?v={VERSION}"'
                f' style="left:{video["left"]:.3f}%; top:{video["top"]:.3f}%;'
                f' width:{video["width"]:.3f}%; height:{video["height"]:.3f}%;"'
                f' aria-label="SkillProof STU101 walkthrough, 4 minutes 19 seconds">\n'
                f'        <source src="{VIDEO_REL}" type="video/mp4">\n'
                f'        Your browser cannot play embedded video.'
                f' <a href="{VIDEO_REL}">Download the walkthrough</a> instead.\n'
                f'      </video>')

        for lk in links:
            n_links += 1
            r = lk['rect']
            label = lk['text'] or lk['url']
            parts.append(
                f'      <a class="hot" href="{esc(lk["url"])}" target="_blank" rel="noopener"'
                f' style="left:{r["left"]:.3f}%; top:{r["top"]:.3f}%;'
                f' width:{r["width"]:.3f}%; height:{r["height"]:.3f}%;"'
                f' title="{esc(label)}"><span class="sr-only">{esc(label)}</span></a>')

        parts.append('    </div>')
        blocks.append('\n'.join(parts))
        dots.append(f'  <button type="button" aria-label="Slide {n}: {esc(title)}"></button>')

        if video:
            make_video_poster(png, video, n)

    size_mb = os.path.getsize(DECK) / 1048576
    html = (PAGE
            .replace('%%SLIDES%%', '\n'.join(blocks))
            .replace('%%DOTS%%', '\n'.join(dots))
            .replace('%%TITLES%%', json.dumps({str(k): v for k, v in TITLES.items()}))
            .replace('%%COUNT%%', str(count))
            .replace('%%DECK%%', '../' + DECK_REL)
            .replace('%%SIZE%%', f'{size_mb:.0f}'))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)

    print(f'built deck/index.html -- {count} slides, {n_video} video overlay, {n_links} link overlay(s)')


def make_video_poster(png, rect, n):
    """Crop the slide's own video region out of the render to use as the poster."""
    im = Image.open(png).convert('RGB')
    W, H = im.size
    crop = im.crop((int(round(rect['left'] / 100 * W)), int(round(rect['top'] / 100 * H)),
                    int(round((rect['left'] + rect['width']) / 100 * W)),
                    int(round((rect['top'] + rect['height']) / 100 * H))))
    out = os.path.join(SLIDES_DIR, f'slide-{n}-video-poster.png')
    crop.save(out, optimize=True)
    print(f'  poster {os.path.basename(out)} {crop.size[0]}x{crop.size[1]}'
          f'  {os.path.getsize(out)/1024:.0f} KB')


def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


if __name__ == '__main__':
    main()
