"""Your own PS2 BIOS dump, played back: the console's menu sounds and its system music.

A PS2 BIOS (the 4 MB file PCSX2 asks you to dump from your own console) keeps its sounds in a module
called SNDIMAGE: a small ROM directory of its own holding two sound banks (SNDOSDD: the browser's
menu sounds; SNDBOOT: the instruments of the system music) and the music's sequences (SNDBOOTS the
boot, SNDTNNLS the tower tunnel, SNDCLOKS the clock, SNDWARNS the warning screen and a few more).
Every file in it is compressed with the BIOS's own LZ scheme (unlz below).

Nothing from any BIOS ships with RIPPS2 or this tool: this module reads the dump you point it at and
renders what is inside, on your machine, the way the console's sound chip (SPU2) would play it.

    python ps2bios.py <bios.bin> <out folder>     every sound and sequence as a .wav, plus a list
"""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

import numpy as np

RATE = 48000                     # the SPU2's output rate
FILTERS = [(0, 0), (60, 0), (115, -52), (98, -55), (122, -60)]


# ------------------------------------------------------------------------------ the ROM
def romdir(data: bytes, base: int = 0):
    """name -> (offset, size) for a ROM directory (the BIOS's own, or SNDIMAGE's inside it)."""
    i = data.find(b'RESET\x00\x00\x00\x00\x00', base)
    if i < 0:
        raise ValueError('no ROM directory (is this a PS2 BIOS dump?)')
    out, off, j = {}, base, i
    while True:
        name = data[j:j + 10].rstrip(b'\x00').decode('latin1')
        if not name:
            break
        _ext, size = struct.unpack_from('<HI', data, j + 10)
        out.setdefault(name, (off, size))
        off += (size + 15) & ~15
        j += 16
    return out


def unlz(c: bytes) -> bytes:
    """The BIOS resource compression: u32 size, then groups led by a big-endian 32-bit word whose top
    30 bits flag 30 tokens (1: a 2-byte back reference, 0: a literal byte) and whose low 2 bits set
    how the references split: (14 - mode) bits of distance, the rest length - 3."""
    n = struct.unpack_from('<I', c, 0)[0]
    out = bytearray()
    i = 4
    while len(out) < n:
        flags = struct.unpack_from('>I', c, i)[0]
        i += 4
        db = 14 - (flags & 3)
        mask = (1 << db) - 1
        for b in range(31, 1, -1):
            if len(out) >= n:
                break
            if flags >> b & 1:
                v = (c[i] << 8) | c[i + 1]
                i += 2
                d = (v & mask) + 1
                for _ in range((v >> db) + 3):
                    out.append(out[-d])
            else:
                out.append(c[i])
                i += 1
    return bytes(out[:n])


def sound_files(bios_path) -> dict[str, bytes]:
    """The decompressed files of the BIOS's SNDIMAGE (SNDOSDDH, SNDOSDDB, SNDBOOTH, SNDBOOTB, ...)."""
    data = Path(bios_path).read_bytes()
    top = romdir(data)
    if 'SNDIMAGE' not in top:
        raise ValueError('this BIOS has no SNDIMAGE (dumps older than about SCPH-30000 keep their sounds '
                         'inside OSDSND instead, which this tool does not read yet)')
    o, s = top['SNDIMAGE']
    img = data[o:o + s]
    files = {}
    for name, (oo, ss) in romdir(img).items():
        if name.startswith('SND'):
            files[name] = unlz(img[oo:oo + ss])
    ver = top.get('ROMVER')
    files['_ROMVER'] = data[ver[0]:ver[0] + ver[1]] if ver else b''
    return files


# ------------------------------------------------------------------------------ the SPU2
def adpcm(bd: bytes, addr: int, max_blocks: int = 1 << 20):
    """SPU2 ADPCM at addr: (samples, loop start sample or None). Stops at the end flag."""
    out = []
    s1 = s2 = 0
    loop = None
    o = addr
    for blk in range(max_blocks):
        if o + 16 > len(bd):
            break
        head, flags = bd[o], bd[o + 1]
        if flags & 4 and loop is None:
            loop = blk * 28
        k1, k2 = FILTERS[min(head >> 4, 4)]
        sh = head & 0xF
        for byte in bd[o + 2:o + 16]:
            for q in (byte & 0xF, byte >> 4):
                q = q - 16 if q >= 8 else q
                y = ((q << 12) >> sh) + ((s1 * k1 + s2 * k2 + 32) >> 6)
                y = -32768 if y < -32768 else 32767 if y > 32767 else y
                out.append(y)
                s2, s1 = s1, y
        o += 16
        if flags & 1:
            if not flags & 2:
                loop = None   # a one-shot: no repeat
            break
    return np.array(out, np.float32) / 32768.0, loop


class Envelope:
    """The SPU2 ADSR envelope, from the two 16-bit registers. One value per output sample."""

    def __init__(self, adsr1: int, adsr2: int):
        sl = adsr1 & 0xF
        self.phases = [
            # (decreasing, exponential, shift, step, target)
            (False, bool(adsr1 >> 15 & 1), adsr1 >> 10 & 0x1F, 7 - (adsr1 >> 8 & 3), 0x7FFF),
            (True, True, adsr1 >> 4 & 0xF, -8, (sl + 1) << 11),
            (bool(adsr2 >> 14 & 1), bool(adsr2 >> 15 & 1), adsr2 >> 8 & 0x1F,
             (~(7 - (adsr2 >> 6 & 3))) if adsr2 >> 14 & 1 else 7 - (adsr2 >> 6 & 3), None),
            (True, bool(adsr2 >> 5 & 1), adsr2 & 0x1F, -8, 0),
        ]

    def render(self, n: int, key_off: int | None):
        """n samples of envelope (0..1); release starts at key_off (or never)."""
        out = np.zeros(n, np.float32)
        value, counter, phase, i = 0, 0, 0, 0
        while i < n:
            if key_off is not None and i >= key_off and phase < 3:
                phase, counter = 3, 0
            dec, exp, shift, step, target = self.phases[phase]
            inc = max(1, 0x8000 >> max(0, shift - 11))
            lev = step << max(0, 11 - shift)
            if exp and not dec and value > 0x6000:
                inc = max(1, inc >> 2)
            if exp and dec:
                lev = (lev * value) >> 15    # an arithmetic shift, as the chip does: it floors, so a decay reaches 0
            # samples until the next step lands (the value holds until then)
            k = max(1, -(-(0x8000 - counter) // inc))
            if key_off is not None and phase < 3 and i < key_off:
                k = min(k, key_off - i)
            k = min(k, n - i)
            out[i:i + k] = value / 32767.0
            i += k
            counter += inc * k
            if counter >= 0x8000:
                counter = 0
                value = min(0x7FFF, max(0, value + lev))
            if phase == 2:
                if value == 0:
                    break
                continue
            if (not dec and value >= target) or (dec and value <= target):
                phase += 1
                if phase > 3:
                    break
        return out


def play_voice(samples, loop, pitch: float, env: Envelope, n_out: int, key_off: int | None):
    """One voice: the sample read at pitch (1.0 = 48 kHz), looping if it loops, under its envelope."""
    if len(samples) == 0:
        return np.zeros(n_out, np.float32)
    pos = np.arange(n_out, dtype=np.float64) * pitch
    if loop is not None and loop < len(samples) - 1:
        L = len(samples) - loop
        over = pos >= len(samples)
        pos[over] = loop + np.mod(pos[over] - loop, L)
    else:
        n_out = min(n_out, int((len(samples) - 1) / max(pitch, 1e-6)) + 1)
        pos = pos[:n_out]
    i0 = np.floor(pos).astype(np.int64)
    f = (pos - i0).astype(np.float32)
    i1 = np.minimum(i0 + 1, len(samples) - 1)
    i0 = np.minimum(i0, len(samples) - 1)
    y = samples[i0] * (1 - f) + samples[i1] * f
    e = env.render(len(y), key_off)
    return y * e


def reverb(stereo, wet=0.35, size=1.0, seed=7):
    """A soft hall in the spirit of the SPU2's reverb (the console runs one under its menus): a few
    early reflections, then a diffuse tail that loses its highs faster than its lows."""
    rng = np.random.default_rng(seed)
    n = int(RATE * 2.4 * size)
    t = np.arange(n) / RATE
    ir = np.zeros((2, n), np.float32)
    for lo, hi, decay in ((0, 400, 0.75), (400, 2500, 0.55), (2500, 24000, 0.28)):
        noise = rng.standard_normal((2, n))
        spec = np.fft.rfft(noise, axis=1)
        fr = np.fft.rfftfreq(n, 1 / RATE)
        spec[:, (fr < lo) | (fr >= hi)] = 0
        band = np.fft.irfft(spec, n=n, axis=1)
        ir += (band * np.exp(-t / (decay * size))).astype(np.float32)
    ir[:, :int(0.018 * RATE)] = 0
    for d, g in ((0.011, 0.5), (0.017, 0.4), (0.023, 0.33), (0.031, 0.25)):
        ir[0, int(d * RATE)] += g
        ir[1, int((d + 0.003) * RATE)] += g
    m = len(stereo[0]) + n
    k = np.fft.rfft(ir, n=m, axis=1)
    x = np.fft.rfft(stereo, n=m, axis=1)
    w = np.fft.irfft(x * k, n=m, axis=1).astype(np.float32)
    w *= wet * np.abs(stereo).max() / (np.abs(w).max() + 1e-9)
    out = w
    out[:, :len(stereo[0])] += stereo
    return out


# ------------------------------------------------------------------------------ the menu sounds
def osd_sounds(hd: bytes):
    """The browser's sound list: 64-byte entries after the SShd header (count at +0x84)."""
    base = struct.unpack_from('<I', hd, 0x2C)[0]       # 0x80
    count = struct.unpack_from('<I', hd, base + 4)[0]
    out = []
    for k in range(count):
        e = base + 0x20 + k * 0x40
        vl, vr, pitch, extra, a1, a2, x, y, addr = struct.unpack_from('<HHHHHHHHI', hd, e)
        out.append(dict(index=k, vol_l=vl, vol_r=vr, pitch=pitch, extra=extra, adsr1=a1, adsr2=a2,
                        x=x, y=y, addr=addr))
    return out


def render_osd(files, index, wet=0.3, hold=None):
    """One menu sound, as the console plays it: its sample at its pitch, envelope and stereo volumes."""
    hd, bd = files['SNDOSDDH'], files['SNDOSDDB']
    e = osd_sounds(hd)[index]
    smp, loop = adpcm(bd, e['addr'])
    pitch = e['pitch'] / 4096.0
    n = int(len(smp) / max(pitch, 1e-6)) + 1
    if loop is not None:
        n = int(RATE * (hold or 1.5))
    v = play_voice(smp, loop, pitch, Envelope(e['adsr1'], e['adsr2']), n, None if loop is None else int(n * 0.8))
    st = np.stack([v * (e['vol_l'] / 0x3FFF), v * (e['vol_r'] / 0x3FFF)])
    st = trim_tail(reverb(st, wet) if wet else st)
    return st


# ------------------------------------------------------------------------------ the system music
def bank_programs(hd: bytes):
    """Programs of an instrument bank (SShd): program -> {vol, pan, tones}. A tone is one layer of an
    instrument: its sample (address in 8-byte units; a tone without the sample flag is the SPU2 noise),
    root note and fine tune, envelope, volume and pan."""
    base = struct.unpack_from('<I', hd, 0x10)[0]
    last = struct.unpack_from('<H', hd, base)[0]
    progs = {}
    for p in range(last + 1):
        off = struct.unpack_from('<H', hd, base + 2 + p * 2)[0]
        if off == 0xFFFF:
            continue
        o = base + off
        h = hd[o:o + 8]
        tones = []
        for k in range((h[0] & 0x7F) + 1):
            t = hd[o + 8 + k * 16:o + 24 + k * 16]
            tones.append(dict(key_hi=t[1], root=t[2], fine=struct.unpack('b', t[3:4])[0],
                              addr=struct.unpack_from('<H', t, 4)[0] * 8,
                              adsr1=struct.unpack_from('<H', t, 6)[0], adsr2=struct.unpack_from('<H', t, 8)[0],
                              key_lo=t[10], vol=t[11], pan=t[12], noise=not (t[15] & 1)))
        progs[p] = dict(vol=h[1], pan=h[2], tones=tones)
    return progs


def seq_events(sq: bytes):
    """(header, events) of a sequence (SSsq). The header holds the volume, ticks per quarter note and
    tempo, then a set-up row for each of the 16 channels (program, volume, pan); the events that follow
    are MIDI: (tick, kind, channel, data)."""
    vol, ppq, tempo = struct.unpack_from('<HHH', sq, 0)
    chans = {}
    for c in range(16):
        r = sq[0x10 + c * 16:0x20 + c * 16]
        chans[r[1]] = dict(prog=r[2], vol=r[3], pan=r[4])
    i, t, status, first, out = 0x110, 0, 0x90, True, []
    while i < len(sq):
        if not first:
            d = 0
            while True:
                b = sq[i]
                i += 1
                d = (d << 7) | (b & 0x7F)
                if not b & 0x80:
                    break
            t += d
        first = False
        if i >= len(sq):
            break
        b = sq[i]
        if b == 0xFF:
            if sq[i + 1] == 0x51:
                out.append((t, 'tempo', 0, [sq[i + 2] | (sq[i + 3] << 8)]))
                i += 4
                continue
            out.append((t, 'end', 0, []))
            break
        if b & 0x80:
            status = b
            i += 1
        hi, ch = status & 0xF0, status & 0xF
        n = 1 if hi in (0xC0, 0xD0) else 2
        data = list(sq[i:i + n])
        i += n
        kind = {0x80: 'off', 0x90: 'on', 0xA0: 'at', 0xB0: 'cc', 0xC0: 'prog', 0xD0: 'cat', 0xE0: 'bend'}[hi]
        if kind == 'on' and data[1] == 0:
            kind = 'off'
        out.append((t, kind, ch, data))
    return dict(vol=vol, ppq=ppq, tempo=tempo, chans=chans), out


SEQUENCES = {   # the BIOS's sequences: their instrument bank, and what each one is
    'SNDBOOTS': ('SNDBOOT', 'Boot'),
    'SNDTNNLS': ('SNDBOOT', 'Tower tunnel'),
    'SNDLOGOS': ('SNDBOOT', 'PS2 logo'),
    'SNDCLOKS': ('SNDBOOT', 'Clock'),
    'SNDWARNS': ('SNDBOOT', 'Ambient'),
    'SNDRCLKS': ('SNDBOOT', 'Clock return'),
    'SNDTM30S': ('SNDBOOT', 'Timer 30'),
    'SNDTM60S': ('SNDBOOT', 'Timer 60'),
}

TUNING = dict(noise_base=750.0, fine_div=128.0, wet=0.4, room=1.4)   # matched to a recording of a real console


class _Fixed:
    """An envelope already rendered."""

    def __init__(self, e):
        self.e = e

    def render(self, n, key_off):
        return self.e[:n]


def noise_voice(n, rate, rng):
    """The SPU2 noise: a random level held for 48000 / rate samples at a time."""
    hold = max(1.0, RATE / max(rate, 1.0))
    k = int(n / hold) + 2
    lv = rng.uniform(-1, 1, k).astype(np.float32)
    return lv[(np.arange(n) / hold).astype(np.int64)]


def _curve(points, n):
    """A step curve over n samples from (seconds, value) points."""
    out = np.empty(n, np.float32)
    pts = sorted(points)
    for k, (s, v) in enumerate(pts):
        a = int(s * RATE)
        b = int(pts[k + 1][0] * RATE) if k + 1 < len(pts) else n
        out[max(0, a):max(0, min(n, b))] = v
    if pts and pts[0][0] > 0:
        out[:int(pts[0][0] * RATE)] = pts[0][1]
    return out


def render_seq(files, name, tail=4.0, max_seconds=None, tuning=None):
    """A sequence played on its bank as the SPU2 would: one voice per layer of every note, each
    channel through its own volume and expression, then a hall like the console's."""
    tu = dict(TUNING, **(tuning or {}))
    bank = SEQUENCES[name][0]
    progs = bank_programs(files[bank + 'H'])
    bd = files[bank + 'B']
    head, ev = seq_events(files[name])
    tmap = [(0, 0.0, head['tempo'])]
    for t, kind, _ch, data in ev:
        if kind == 'tempo' and data[0] != tmap[-1][2]:
            t0, s0, bpm = tmap[-1]
            tmap.append((t, s0 + (t - t0) * 60.0 / (bpm * head['ppq']), data[0]))

    def sec(t):
        for t0, s0, bpm in reversed(tmap):
            if t >= t0:
                return s0 + (t - t0) * 60.0 / (bpm * head['ppq'])
        return 0.0

    end_s = sec(ev[-1][0]) + tail
    if max_seconds:
        end_s = min(end_s, max_seconds)
    n_total = int(end_s * RATE) + 1
    chans = {c: dict(prog=v['prog'], vol=[(0.0, v['vol'] / 127.0)], pan=[(0.0, v['pan'])], expr=[(0.0, 1.0)])
             for c, v in head['chans'].items() if c < 16}
    for c in range(16):
        chans.setdefault(c, dict(prog=0, vol=[(0.0, 100 / 127.0)], pan=[(0.0, 64)], expr=[(0.0, 1.0)]))
    notes, held = [], {}
    cur = {c: chans[c]['prog'] for c in range(16)}
    for t, kind, ch, data in ev:
        s = sec(t)
        if kind == 'prog':
            cur[ch] = data[0]
        elif kind == 'cc' and data[0] in (7, 11, 10):
            key = {7: 'vol', 11: 'expr', 10: 'pan'}[data[0]]
            chans[ch][key].append((s, data[1] if key == 'pan' else data[1] / 127.0))
        elif kind == 'on':
            held[(ch, data[0])] = len(notes)
            notes.append(dict(ch=ch, note=data[0], vel=data[1], prog=cur[ch], on=s, off=None))
        elif kind == 'off':
            k = held.pop((ch, data[0]), None)
            if k is not None:
                notes[k]['off'] = s
    rng = np.random.default_rng(1)
    cache = {}
    buses = {}
    for nt in notes:
        prog = progs.get(nt['prog'])
        i0 = int(nt['on'] * RATE)
        if not prog or i0 >= n_total:
            continue
        n = n_total - i0
        key_off = None if nt['off'] is None else int((nt['off'] - nt['on']) * RATE)
        bus = buses.setdefault(nt['ch'], np.zeros((2, n_total), np.float32))
        for tn in prog['tones']:
            if not (tn['key_lo'] <= nt['note'] <= max(tn['key_hi'], tn['key_lo'])):
                continue
            ratio = 2.0 ** ((nt['note'] - tn['root'] + tn['fine'] / tu['fine_div']) / 12.0)
            env = Envelope(tn['adsr1'], tn['adsr2'])
            e = env.render(n, key_off)
            live = np.nonzero(e > 1e-5)[0]
            if not len(live):
                continue
            m = int(live[-1]) + 1            # the voice ends when its envelope does, not with the song
            if tn['noise']:
                y = noise_voice(m, tu['noise_base'] * ratio / 64.0, rng) * e[:m]
            else:
                if tn['addr'] not in cache:
                    cache[tn['addr']] = adpcm(bd, tn['addr'])
                smp, loop = cache[tn['addr']]
                y = play_voice(smp, loop, ratio, _Fixed(e[:m]), m, None)
            g = (nt['vel'] / 127.0) * (tn['vol'] / 127.0) * (prog['vol'] / 127.0)
            pan = max(-1.0, min(1.0, ((tn['pan'] - 64) + (prog['pan'] - 64)) / 64.0))
            bus[0, i0:i0 + len(y)] += y * g * math.cos((pan + 1) * math.pi / 4)
            bus[1, i0:i0 + len(y)] += y * g * math.sin((pan + 1) * math.pi / 4)
    mix = np.zeros((2, n_total), np.float32)
    for c, bus in buses.items():
        g = _curve(chans[c]['vol'], n_total) * _curve(chans[c]['expr'], n_total)
        pc = (_curve(chans[c]['pan'], n_total) - 64) / 64.0
        pc = np.clip(pc, -1, 1)
        mix[0] += bus[0] * g * np.cos((pc + 1) * math.pi / 4) * math.sqrt(2)
        mix[1] += bus[1] * g * np.sin((pc + 1) * math.pi / 4) * math.sqrt(2)
    mix *= head['vol'] / 127.0
    st = reverb(mix, tu['wet'], size=tu['room']) if tu['wet'] else mix
    return trim_tail(st, 1e-4)


def trim_tail(st, floor=1e-4):
    a = np.abs(st).max(axis=0)
    idx = np.nonzero(a > floor)[0]
    return st[:, :idx[-1] + 1] if len(idx) else st


def write_wav(path, stereo, rate=RATE):
    st = np.clip(stereo, -1, 1)
    pcm = (st.T * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())


if __name__ == '__main__':
    import sys
    files = sound_files(sys.argv[1])
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    print('ROMVER', files['_ROMVER'][:14])
    for e in osd_sounds(files['SNDOSDDH']):
        st = render_osd(files, e['index'])
        write_wav(out / ('osd_%02d.wav' % e['index']), st / max(1e-6, np.abs(st).max()) * 0.9)
        print('osd %2d  pitch %04x  adsr %04x %04x  vol %04x %04x  extra %04x  x %04x y %04x  addr %05x  %.2f s'
              % (e['index'], e['pitch'], e['adsr1'], e['adsr2'], e['vol_l'], e['vol_r'], e['extra'], e['x'], e['y'],
                 e['addr'], st.shape[1] / RATE))
