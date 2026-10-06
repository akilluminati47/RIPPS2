"""Make theme images 8-bit palette PNGs, in place: RIPPS2 keeps those as 8-bit textures with a 32-bit
palette (alpha included), a quarter of the video memory of an RGBA PNG and quicker to load.

    python3 elf/theme/tools/png8.py elf/theme/gfx    convert what is not 8-bit yet (after any make_*.py here)
    python3 elf/theme/tools/png8.py --check elf/theme/gfx    list them, change nothing

(The same tool as RIPPS2-themes' tools/png8.py.)

An image of 256 colours or fewer (counting alpha) converts exactly. A larger one is cut to 256 by a
weighted median cut refined with k-means, in premultiplied colour, so soft edges and glows keep their
look: fully transparent pixels stay exactly transparent (no halos), and nothing is dithered (dither
on small icons is noise). The palette is always written whole, so the file is 8-bit, never 1/2/4-bit
(which RIPPS2 expands back to RGBA). Prints each change with its worst and mean error.
"""
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def depth(path):
    """(colour type, bit depth) from the PNG header"""
    b = open(path, 'rb').read(26)
    w, h, bd, ct = struct.unpack('>IIBB', b[16:26])
    return ct, bd


def is_png8(path):
    return depth(path) == (3, 8)


def quantize(rgba):
    """rgba (N, 4) uint8 -> (palette (K, 4) uint8, index (N,) uint8), K <= 256, index 0 transparent"""
    uniq, inv, cnt = np.unique(rgba, axis=0, return_inverse=True, return_counts=True)
    inv = inv.reshape(-1)
    clear = uniq[:, 3] == 0
    solid = np.nonzero(~clear)[0]
    lut = np.zeros(len(uniq), np.int64)  # unique colour -> palette index (0 for every clear one)
    if len(solid) <= 255:  # exact
        pal = np.vstack([[0, 0, 0, 0], uniq[solid]]).astype(np.uint8)
        lut[solid] = np.arange(1, len(solid) + 1)
        return pal, lut[inv].astype(np.uint8)

    a = uniq[solid, 3:4].astype(np.float64)
    x = np.hstack([uniq[solid, :3] * a / 255.0, a])  # premultiplied
    w = cnt[solid].astype(np.float64)

    def sse(ix):
        m = np.average(x[ix], axis=0, weights=w[ix])
        return float((w[ix, None] * (x[ix] - m) ** 2).sum())

    boxes = [np.arange(len(x))]
    errs = [sse(boxes[0])]
    while len(boxes) < 255:
        k = int(np.argmax(errs))
        if errs[k] <= 0:
            break
        ix = boxes[k]
        m = np.average(x[ix], axis=0, weights=w[ix])
        var = (w[ix, None] * (x[ix] - m) ** 2).sum(axis=0)
        ch = int(np.argmax(var))
        o = ix[np.argsort(x[ix, ch], kind='stable')]
        cw = np.cumsum(w[o])
        cut = int(np.searchsorted(cw, cw[-1] / 2.0)) + 1
        cut = min(max(cut, 1), len(o) - 1)
        boxes[k:k + 1] = [o[:cut], o[cut:]]
        errs[k:k + 1] = [sse(o[:cut]), sse(o[cut:])]
    cent = np.array([np.average(x[b], axis=0, weights=w[b]) for b in boxes])
    for _ in range(12):  # k-means, weighted by pixel count
        d = ((x[:, None, :] - cent[None, :, :]) ** 2).sum(axis=2)
        near = d.argmin(axis=1)
        for k in range(len(cent)):
            sel = near == k
            if sel.any():
                cent[k] = np.average(x[sel], axis=0, weights=w[sel])
    d = ((x[:, None, :] - cent[None, :, :]) ** 2).sum(axis=2)
    near = d.argmin(axis=1)
    ca = np.clip(np.round(cent[:, 3]), 1, 255)
    rgb = np.clip(np.round(cent[:, :3] * 255.0 / ca[:, None]), 0, 255)
    pal = np.vstack([[0, 0, 0, 0], np.hstack([rgb, ca[:, None]])]).astype(np.uint8)
    lut[solid] = near + 1
    return pal, lut[inv].astype(np.uint8)


def convert(path):
    src = Image.open(path).convert('RGBA')
    px = np.asarray(src, np.uint8).reshape(-1, 4)
    pal, idx = quantize(px)
    out = Image.frombytes('P', src.size, idx.tobytes())
    full = np.zeros((256, 4), np.uint8)
    full[:len(pal)] = pal
    out.putpalette(full[:, :3].reshape(-1).tolist())
    out.save(path, transparency=bytes(full[:, 3].tolist()))
    # how far it moved, in premultiplied colour (0-255)
    got = np.asarray(Image.open(path).convert('RGBA'), np.float64).reshape(-1, 4)
    def pm(v):
        return np.hstack([v[:, :3] * v[:, 3:4] / 255.0, v[:, 3:4]])
    err = np.abs(pm(px.astype(np.float64)) - pm(got))
    assert is_png8(path), path
    return len(np.unique(px, axis=0)), float(err.max()), float(err.mean())


def main():
    args = sys.argv[1:]
    check = '--check' in args
    args = [a for a in args if a != '--check']
    files = []
    for a in args:
        p = Path(a)
        files += sorted(p.rglob('*.png')) if p.is_dir() else [p]
    todo = [f for f in files if not is_png8(f)]
    for f in todo:
        if check:
            ct, bd = depth(f)
            print('%s: colour type %d, %d-bit' % (f, ct, bd))
            continue
        n, worst, mean = convert(f)
        print('%s: %d colours -> 8-bit palette (worst %.0f, mean %.2f)' % (f, n, worst, mean))
    print('%d of %d PNGs %s' % (len(todo), len(files), 'not 8-bit palette' if check else 'converted'))
    sys.exit(1 if check and todo else 0)


if __name__ == '__main__':
    main()
