"""Build the site favicon set from the official WGU logo art.

WHY THIS EXISTS
`assets/wgu-favicon.png` was never a favicon: it is the 2000x910 "WGU" WORDMARK
lockup in deep navy on transparency. Browsers squashed a 2.2:1 wordmark into a
16x16 tab slot, which rendered as an illegible blob, and because the art is navy
on transparency it disappeared entirely against a dark tab strip.

WHAT THIS PRODUCES
The owl mark, cropped from the official FY26 reverse lockup (where the owl is
white), centred on an opaque WGU deep-navy square. Opaque matters: a transparent
icon inherits the tab strip colour and loses either the light or the dark case,
whereas navy-with-white-owl reads on both.

The art is only cropped and scaled, never redrawn -- the owl geometry comes
straight from the official file.

WHY EACH SIZE GETS ITS OWN PADDING AND STROKE WEIGHT
The owl is an OUTLINE mark. A plain LANCZOS downscale of a 465px outline to 16px
averages each hairline stroke with the navy around it, so the 16px frame came out
mid-grey and mushy -- legible as "a dark shape", not as an owl. Each size is
therefore rendered with its own padding and a small dilation of the mark measured
in TARGET pixels, so the strokes land at roughly one full pixel wide after the
downscale instead of a fraction of one. Values below were picked by rendering the
candidates side by side at 10x and comparing; see SIZES.

Outputs:
    favicon.ico                    16 + 32 + 48, auto-discovered at the site root
    assets/wgu-owl-favicon.png     512x512 master, referenced by <link rel="icon">
    assets/apple-touch-icon.png    180x180, iOS home-screen

Deliberately NEW filenames rather than overwriting wgu-favicon.png: favicons are
cached hard, so reusing the path would leave the old blob in place for anyone who
had already loaded the site. wgu-favicon.png is left on disk because the archived
mockups under _archive/ still reference it.

Usage:  python make_favicon.py
"""
from PIL import Image, ImageFilter
import numpy as np
import io
import os
import struct

REPO = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(REPO, 'assets', 'wgu-corporation-full-color-reverse.png')
NAVY = (0, 23, 48, 255)          # WGU FY26 Deep Navy #001730

# size -> (padding as a share of the square per side, stroke dilation in TARGET pixels)
SIZES = {
    16:  (0.020, 0.35),   # tab strip at 1x -- needs every pixel, and the most weight help
    32:  (0.050, 0.20),   # tab strip at 2x / taskbar
    48:  (0.060, 0.15),   # Windows shortcut, bookmark bars
    180: (0.085, 0.00),    # apple-touch-icon: large enough that the raw art is crisp
    512: (0.085, 0.00),    # master
}


def owl_crop(path):
    """Return the owl mark from the left cluster of the lockup, tightly cropped."""
    im = Image.open(path).convert('RGBA')
    a = np.array(im)[:, :, 3]
    cols = (a > 40).sum(axis=0)
    nz = np.nonzero(cols)[0]

    # The lockup is owl + wordmark separated by clear space. Find the first gap
    # wider than 25px after the art starts; everything before it is the owl.
    empty = cols <= 2
    run, owl_end = None, None
    for i, e in enumerate(empty):
        if e and run is None:
            run = i
        elif not e and run is not None:
            if i - run > 25 and run > nz.min():
                owl_end = run
                break
            run = None
    if owl_end is None:
        raise SystemExit('could not separate the owl from the wordmark')

    box = im.crop((int(nz.min()), 0, int(owl_end), im.size[1]))
    return box.crop(box.getbbox())      # tighten vertically too


def render(owl, size):
    """Centre the owl on an opaque navy square, weight-compensated for this size."""
    pad, dilate_target = SIZES[size]
    canvas = Image.new('RGBA', (size, size), NAVY)

    inner = int(round(size * (1 - 2 * pad)))
    w, h = owl.size
    scale = min(inner / w, inner / h)
    tw, th = max(1, int(round(w * scale))), max(1, int(round(h * scale)))

    # The owl is flat white on transparency, so its alpha channel IS the mark.
    # Grow the mask at SOURCE resolution by however many source pixels equal the
    # requested target-pixel dilation, then downscale and paint solid white
    # through it. Painting through the mask (rather than resizing the RGBA art)
    # also keeps the transparent regions from bleeding their RGB into the edges.
    mask = owl.split()[3]
    if dilate_target > 0:
        r = max(1, int(round(dilate_target / scale)))
        mask = mask.filter(ImageFilter.MaxFilter(r * 2 + 1))
    mask = mask.resize((tw, th), Image.LANCZOS)

    art = Image.new('RGBA', (tw, th), (255, 255, 255, 0))
    art.putalpha(mask)
    canvas.alpha_composite(art, ((size - tw) // 2, (size - th) // 2))
    return canvas


def write_ico(path, frames):
    """Write a multi-size .ico from a list of already-rendered square images.

    Pillow's own ICO writer downscales every frame from one source image, which
    would throw away the per-size weight compensation above. The container is
    trivial, so the frames are packed by hand as embedded PNGs (supported by
    every browser and by Windows Vista and later).
    """
    blobs = []
    for im in frames:
        buf = io.BytesIO()
        im.convert('RGBA').save(buf, format='PNG', optimize=True)
        blobs.append(buf.getvalue())

    out = bytearray(struct.pack('<HHH', 0, 1, len(blobs)))     # ICONDIR
    offset = 6 + 16 * len(blobs)
    for im, blob in zip(frames, blobs):
        s = im.size[0]
        out += struct.pack('<BBBBHHII',
                           0 if s >= 256 else s,   # width  (0 means 256)
                           0 if s >= 256 else s,   # height
                           0, 0,                   # palette count, reserved
                           1, 32,                  # colour planes, bits per pixel
                           len(blob), offset)
        offset += len(blob)
    for blob in blobs:
        out += blob

    with open(path, 'wb') as f:
        f.write(bytes(out))


def main():
    owl = owl_crop(SRC)
    print(f'owl cropped from {os.path.basename(SRC)}: {owl.size[0]}x{owl.size[1]}')

    out_png = os.path.join(REPO, 'assets', 'wgu-owl-favicon.png')
    render(owl, 512).convert('RGB').save(out_png, optimize=True)
    print(f'wrote {out_png} 512x512')

    touch = os.path.join(REPO, 'assets', 'apple-touch-icon.png')
    render(owl, 180).convert('RGB').save(touch, optimize=True)
    print(f'wrote {touch} 180x180')

    ico = os.path.join(REPO, 'favicon.ico')
    write_ico(ico, [render(owl, s) for s in (16, 32, 48)])
    print(f'wrote {ico} 16+32+48 (each rendered at its own size)')


if __name__ == '__main__':
    main()
