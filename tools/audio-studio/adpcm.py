"""RIPPS2's sound effect format (.adp): audsrv's ADPCM, as OPL and RIPPS2 play their sounds.

A 16-byte header ("APCM", version 1, one channel, no loop, the SPU2 pitch for the rate, the sample
count), then SPU2 ADPCM: 28 samples in every 16-byte block (a filter and shift byte, a flags byte,
14 bytes of 4-bit steps). The last block ends the sound and a silent terminator block follows.

Each block tries the SPU2's five prediction filters, each with its best shift, quantizes with the
decoder's exact integer arithmetic (so the error never builds up from block to block), and keeps the
closest. This is the same encoder as elf/theme/tools/make_adp.py.
"""
import struct

import numpy as np

RATE = 44100
FILTERS = [(0, 0), (60, 0), (115, -52), (98, -55), (122, -60)]


def _clamp16(v):
    return -32768 if v < -32768 else 32767 if v > 32767 else v


def _encode_block(blk, s1, s2):
    best = None
    for f, (k1, k2) in enumerate(FILTERS):
        p1, p2, peak = s1, s2, 0
        for x in blk:
            r = x - ((p1 * k1 + p2 * k2 + 32) >> 6)
            if abs(r) > peak:
                peak = abs(r)
            p2, p1 = p1, x
        shift = 12
        while shift > 0 and peak > (7 << (12 - shift)):
            shift -= 1
        for sh in {shift, max(shift - 1, 0)}:
            scale = 1 << (12 - sh)
            p1, p2, err, nibs = s1, s2, 0, []
            for x in blk:
                pred = (p1 * k1 + p2 * k2 + 32) >> 6
                q = int(round((x - pred) / scale))
                q = -8 if q < -8 else 7 if q > 7 else q
                y = _clamp16(((q << 12) >> sh) + pred)
                err += (x - y) * (x - y)
                nibs.append(q & 0xF)
                p2, p1 = p1, y
            if best is None or err < best[0]:
                best = (err, (f << 4) | sh, nibs, p1, p2)
    return best


def encode(samples, rate=RATE, progress=None):
    """int16-range mono samples -> .adp bytes. progress(fraction) is called now and then."""
    samples = [int(v) for v in np.asarray(samples, np.int64)]
    n = len(samples)
    blocks = max(1, (n + 27) // 28)
    samples += [0] * (blocks * 28 - n)
    out = bytearray()
    s1 = s2 = 0
    head = 0
    for b in range(blocks):
        _, head, nibs, s1, s2 = _encode_block(samples[b * 28:(b + 1) * 28], s1, s2)
        flags = 1 if b == blocks - 1 else 0
        out += bytes([head, flags]) + bytes(nibs[i] | (nibs[i + 1] << 4) for i in range(0, 28, 2))
        if progress and b % 400 == 0:
            progress(b / blocks)
    out += bytes([head, 7]) + bytes(14)
    pitch = rate * 4096 // 48000
    return struct.pack('<4sBBBBII', b'APCM', 1, 1, 0, 0, pitch, n) + bytes(out)


def decode(data):
    """.adp bytes -> (int16 samples, rate)."""
    magic, _, channels, _, _, pitch, n = struct.unpack('<4sBBBBII', data[:16])
    if magic != b'APCM' or channels != 1:
        raise ValueError('not a mono audsrv ADPCM (.adp) file')
    s1 = s2 = 0
    out = []
    for o in range(16, len(data) - 15, 16):
        head, flags = data[o], data[o + 1]
        k1, k2 = FILTERS[min(head >> 4, 4)]
        sh = head & 0xF
        for byte in data[o + 2:o + 16]:
            for q in (byte & 0xF, byte >> 4):
                q = q - 16 if q >= 8 else q
                y = _clamp16(((q << 12) >> sh) + ((s1 * k1 + s2 * k2 + 32) >> 6))
                out.append(y)
                s2, s1 = s1, y
        if flags & 1:
            break
    return np.array(out[:n], np.int16), int(round(pitch * 48000 / 4096))
