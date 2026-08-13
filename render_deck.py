"""Render the status demo deck to PNGs so it can be viewed in a browser.

WHY THIS EXISTS
No browser renders .pptx natively. The landing page previously linked the raw
41 MB file, which meant "view the deck" was really "download the deck, wait,
then open PowerPoint". This renders each slide to an image so deck/index.html
can present it inline instead.

WHY NOT THE MICROSOFT OFFICE ONLINE VIEWER
The obvious alternative (view.officeapps.live.com/op/embed.aspx?src=...) is a
dead end here on three counts: it caps at 10 MB and this deck is 41 MB, it
would not play the embedded video anyway, and it would hand a WGU URL to a
third-party service to fetch on every page load. Self-hosted PNGs have none of
those problems and keep working if that service changes.

THE VIDEO
Slide 6 is 39.56 of the deck's 41 MB: one embedded MP4, which is byte-identical
(sha256) to assets/video/skillproof-walkthrough-2k.mp4 already in the repo. So
the slide is rendered like any other -- PowerPoint paints the video's poster
frame -- and deck/index.html overlays a real <video> element on top of that
region, pointed at the existing asset. No second copy of a 40 MB file.

Geometry for that overlay is read out of the slide XML rather than eyeballed;
this script prints it so deck/index.html can be checked against it. As of v1.1
the shape sits at left 28%, top 0%, width 72%, height 100% of the slide, and
its aspect (1.28) matches the video's native 2560x2000 exactly, so the player
fills the region with no letterboxing.

REQUIREMENTS
Desktop PowerPoint via COM (Windows only). There is no LibreOffice or
pdftoppm on this machine, which is why COM is the export path.

Usage:  python render_deck.py
"""
import hashlib
import os
import re
import zipfile

import win32com.client

REPO = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(REPO, 'assets', 'decks', 'skillproof-status-demo_v1-1_30JUL2026.pptx')
OUT = os.path.join(REPO, 'assets', 'decks', 'slides')
VIDEO = os.path.join(REPO, 'assets', 'video', 'skillproof-walkthrough-2k.mp4')

# 16:9 slide rendered at 2x a 1280-wide viewer, so it stays crisp on HiDPI
# displays and when a slide is opened full-screen on a 2K monitor.
WIDTH, HEIGHT = 2560, 1440


def inspect():
    """Read slide count, the video overlay geometry, and confirm the video reuse."""
    z = zipfile.ZipFile(DECK)
    pres = z.read('ppt/presentation.xml').decode('utf-8', 'ignore')
    m = re.search(r'sldSz[^/]*cx="(\d+)"[^/]*cy="(\d+)"', pres)
    cx, cy = int(m.group(1)), int(m.group(2))

    slides = sorted(
        (n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)),
        key=lambda s: int(re.search(r'(\d+)', s.split('/')[-1]).group(1)))

    overlays = {}
    for s in slides:
        num = int(re.search(r'slide(\d+)', s).group(1))
        xml = z.read(s).decode('utf-8', 'ignore')
        for blk in re.findall(r'<p:pic>.*?</p:pic>', xml, re.S):
            if 'videoFile' not in blk:
                continue
            off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>', blk)
            ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"/>', blk)
            if off and ext:
                x, y = int(off.group(1)), int(off.group(2))
                w, h = int(ext.group(1)), int(ext.group(2))
                overlays[num] = dict(left=100 * x / cx, top=100 * y / cy,
                                     width=100 * w / cx, height=100 * h / cy)

    # The deck's embedded MP4 should be the same file already served from
    # assets/video/. If this ever stops matching, the viewer is showing a
    # different cut than the deck and the overlay src needs revisiting.
    same = None
    if 'ppt/media/media1.mp4' in z.namelist() and os.path.exists(VIDEO):
        a = hashlib.sha256(z.read('ppt/media/media1.mp4')).hexdigest()
        with open(VIDEO, 'rb') as f:
            b = hashlib.sha256(f.read()).hexdigest()
        same = (a == b)

    return len(slides), overlays, same


def render(expected):
    os.makedirs(OUT, exist_ok=True)
    for stale in os.listdir(OUT):
        if re.match(r'slide-\d+\.png$', stale):
            os.remove(os.path.join(OUT, stale))

    app = win32com.client.Dispatch('PowerPoint.Application')
    pres = None
    try:
        # ReadOnly + WithWindow=0: never risk writing back to the source deck,
        # and do not steal focus with a PowerPoint window.
        pres = app.Presentations.Open(DECK, ReadOnly=1, Untitled=0, WithWindow=0)
        count = pres.Slides.Count
        if count != expected:
            raise SystemExit(f'deck has {count} slides, XML reported {expected}')
        for i in range(1, count + 1):
            path = os.path.join(OUT, f'slide-{i}.png')
            pres.Slides(i).Export(path, 'PNG', WIDTH, HEIGHT)
            print(f'  slide-{i}.png  {os.path.getsize(path) / 1024:7.0f} KB')
        return count
    finally:
        if pres is not None:
            pres.Close()
        app.Quit()


def main():
    count, overlays, same_video = inspect()
    print(f'deck: {os.path.basename(DECK)} -- {count} slides')
    print(f'embedded video matches assets/video/skillproof-walkthrough-2k.mp4: {same_video}')
    if same_video is False:
        print('  WARNING: they differ -- deck/index.html would show a different cut')
    for num, o in sorted(overlays.items()):
        print(f'video overlay on slide {num}: '
              f'left={o["left"]:.3f}% top={o["top"]:.3f}% '
              f'width={o["width"]:.3f}% height={o["height"]:.3f}%')

    print(f'rendering at {WIDTH}x{HEIGHT}:')
    render(count)
    print('done')


if __name__ == '__main__':
    main()
