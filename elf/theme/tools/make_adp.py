"""Make a RIPPS2 sound effect (.adp) from any audio file ffmpeg can read (mp3, flac, wav, ...).

    python elf/theme/tools/make_adp.py in.mp3 out.adp [--trim] [--gain DB]
    python elf/theme/tools/make_adp.py --decode in.adp out.wav     (to check a file by ear)

RIPPS2 plays its sounds through audsrv, as OPL does: a 16-byte header ("APCM", version 1, one
channel, no loop, the SPU2 pitch for 44.1 kHz, the sample count), then SPU2 ADPCM, 28 samples in
every 16-byte block (a filter and shift byte, a flags byte, 14 bytes of 4-bit steps). The last
block ends the sound and a silent terminator block follows, as in OPL's own sounds.

Each block tries the SPU2's five prediction filters, every one with its best shift, quantizes with
the decoder's exact integer arithmetic (so the error does not build up from block to block), and
keeps whichever is closest to the source.

Drop the result in SOUND/ beside RIPPS2.ELF, named for its event: boot, cursor, confirm, cancel,
message, transition, bd_connect, bd_disconnect, page_in, page_out, error, save, launch, disc,
random (.adp). ffmpeg must be on the PATH.
"""
import argparse
import struct
import subprocess
import sys

import numpy as np

RATE = 44100
PITCH = RATE * 4096 // 48000  # the SPU2 runs at 48 kHz
FILTERS = [(0, 0), (60, 0), (115, -52), (98, -55), (122, -60)]  # SPU2 ADPCM predictors, /64


def decode_input(path, trim, gain_db):
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', path, '-vn', '-ac', '1', '-ar', str(RATE)]
    filters = []
    if trim:  # leading and trailing silence off
        filters.append('silenceremove=start_periods=1:start_threshold=-60dB,areverse,'
                       'silenceremove=start_periods=1:start_threshold=-60dB,areverse')
    if gain_db:
        filters.append('volume=%sdB' % gain_db)
    if filters:
        cmd += ['-af', ','.join(filters)]
    cmd += ['-f', 's16le', '-']
    pcm = subprocess.run(cmd, check=True, stdout=subprocess.PIPE).stdout
    return np.frombuffer(pcm, dtype='<i2').astype(np.int64)


def clamp16(v):
    return -32768 if v < -32768 else 32767 if v > 32767 else v


def encode_block(blk, s1, s2):
    """Best (error, header byte, nibbles, s1, s2) for 28 samples after history s1, s2."""
    best = None
    for f, (k1, k2) in enumerate(FILTERS):
        # the largest step the ideal prediction leaves sets the shift
        p1, p2, peak = s1, s2, 0
        for x in blk:
            r = x - ((p1 * k1 + p2 * k2 + 32) >> 6)
            peak = max(peak, abs(r))
            p2, p1 = p1, int(x)
        shift = 12
        while shift > 0 and peak > (7 << (12 - shift)):
            shift -= 1
        for sh in {shift, max(shift - 1, 0)}:  # one step coarser can win on a block with a spike
            scale = 1 << (12 - sh)
            p1, p2, err, nibs = s1, s2, 0, []
            for x in blk:
                pred = (p1 * k1 + p2 * k2 + 32) >> 6
                q = int(round((x - pred) / scale))
                q = -8 if q < -8 else 7 if q > 7 else q
                y = clamp16(((q << 12) >> sh) + pred)
                err += (int(x) - y) ** 2
                nibs.append(q & 0xF)
                p2, p1 = p1, y
            if best is None or err < best[0]:
                best = (err, (f << 4) | sh, nibs, p1, p2)
    return best


def encode(samples):
    n = len(samples)
    blocks = max(1, (n + 27) // 28)
    pad = np.zeros(blocks * 28, dtype=np.int64)
    pad[:n] = samples
    out = bytearray()
    s1 = s2 = 0
    head = 0
    for b in range(blocks):
        _, head, nibs, s1, s2 = encode_block(pad[b * 28:(b + 1) * 28], s1, s2)
        flags = 1 if b == blocks - 1 else 0  # the last block ends the sound
        out += bytes([head, flags]) + bytes(nibs[i] | (nibs[i + 1] << 4) for i in range(0, 28, 2))
    out += bytes([head, 7]) + bytes(14)  # the silent terminator OPL's own sounds carry
    return struct.pack('<4sBBBBII', b'APCM', 1, 1, 0, 0, PITCH, n) + out


def decode(data):
    magic, _, channels, _, _, _, n = struct.unpack('<4sBBBBII', data[:16])
    if magic != b'APCM' or channels != 1:
        sys.exit('not a mono audsrv ADPCM file')
    s1 = s2 = 0
    out = []
    for o in range(16, len(data) - 15, 16):
        head, flags = data[o], data[o + 1]
        k1, k2 = FILTERS[min(head >> 4, 4)]
        sh = head & 0xF
        for byte in data[o + 2:o + 16]:
            for q in (byte & 0xF, byte >> 4):
                q = q - 16 if q >= 8 else q
                y = clamp16(((q << 12) >> sh) + ((s1 * k1 + s2 * k2 + 32) >> 6))
                out.append(y)
                s2, s1 = s1, y
        if flags & 1:
            break
    return np.array(out[:n], dtype='<i2')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--decode', action='store_true', help='turn an .adp back into a .wav')
    ap.add_argument('--trim', action='store_true', help='cut silence off both ends')
    ap.add_argument('--gain', type=float, default=0.0, help='dB, e.g. -3')
    a = ap.parse_args()
    if a.decode:
        pcm = decode(open(a.src, 'rb').read())
        import wave
        with wave.open(a.dst, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(pcm.tobytes())
        print('wrote %s: %.2f s' % (a.dst, len(pcm) / RATE))
        return
    samples = decode_input(a.src, a.trim, a.gain)
    if len(samples) == 0:
        sys.exit('no audio in ' + a.src)
    data = encode(samples)
    open(a.dst, 'wb').write(data)
    back = decode(data).astype(np.float64)
    src = samples.astype(np.float64)
    noise = np.sum((src - back) ** 2) or 1.0
    print('wrote %s: %.2f s, %d bytes, SNR %.1f dB' % (a.dst, len(samples) / RATE, len(data),
                                                      10 * np.log10(np.sum(src ** 2) / noise)))


if __name__ == '__main__':
    main()
