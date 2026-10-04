"""RIPPS2 Audio Studio: make an AUDIO folder for RIPPS2 on your PC.

Browse to any sound or song, hear it as it is and as the PS2 will play it, and turn it into one of
RIPPS2's sounds (boot, cursor, confirm ...) or into a music track. Or point it at your own PS2 BIOS
dump and rip the console's own menu sounds and system music, rendered fresh from the BIOS.

Everything lands in output/AUDIO beside this app: copy that folder to a USB stick, and in RIPPS2's
Memory Files put it beside RIPPS2.ELF.

Keyboard: arrows move, Enter opens or converts, Backspace goes back, Space plays the original,
P plays the PS2 version, Q / E (or Tab) switch tabs, S converts a folder or rips a BIOS, O opens the
output folder. A gamepad works too: Cross, Circle, Square, Triangle, L1 / R1, Start.
"""
from __future__ import annotations

import math
import os
import queue
import string
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np
import pygame

import audio_io as aio
import ps2bios

W, H = 1280, 720
FPS = 60

BG_TOP = (3, 7, 22)
BG_MID = (10, 24, 70)
WHITE = (236, 242, 255)
SOFT = (170, 188, 236)
DIM = (110, 126, 176)
FAINT = (70, 84, 128)
BLUE = (90, 140, 255)
CYAN = (143, 227, 255)
SEL = (36, 76, 196)
WARN = (255, 196, 120)

EVENTS = [  # RiptOPL's names first, then RIPPS2's additions
    ('boot', 'Boot', 'As the towers rise at power on', 13.0),
    ('cursor', 'Cursor', 'Moving the cursor', 0.6),
    ('confirm', 'Confirm', 'Choosing something', 1.5),
    ('cancel', 'Cancel', 'Going back', 1.5),
    ('message', 'Message', 'A message box opens', 2.0),
    ('transition', 'Transition', 'Switching tabs', 1.5),
    ('bd_connect', 'Drive in', 'A USB or HDD drive arrives', 1.5),
    ('bd_disconnect', 'Drive out', 'A drive is removed', 1.5),
    ('page_in', 'Page in', 'Opening a page', 1.5),
    ('page_out', 'Page out', 'Closing a page', 1.5),
    ('error', 'Error', 'An error message', 1.5),
    ('save', 'Save', 'Settings saved', 2.0),
    ('launch', 'Launch', 'A game launching', 4.0),
    ('disc', 'Disc', 'A disc read in Launch Disc', 2.0),
    ('random', 'Random', 'L2 + R2 picks a random game', 1.5),
]
EVENT = {e[0]: e for e in EVENTS}
OUT_DIR = aio.HOME_DIR / 'output' / 'AUDIO'
SFX_BUDGET = 0x200000 - 0x5010   # audsrv loads every sound into the SPU2's 2 MB of sound RAM, from 0x5010 up

# What each menu sound of the BIOS is (matched against recordings of a real console), and the rip
OSD_ROLE = {6: 'cursor', 4: 'confirm', 12: 'cancel', 2: 'page_in', 1: 'page_out', 9: 'transition', 10: 'message'}
BIOS_RIP = [('boot', ('seq', 'SNDBOOTS')), ('cursor', ('osd', 6)), ('confirm', ('osd', 4)), ('cancel', ('osd', 12)),
            ('message', ('osd', 10)), ('transition', ('osd', 9)), ('bd_connect', ('osd', 4)), ('bd_disconnect', ('osd', 4)),
            ('page_in', ('osd', 2)), ('page_out', ('osd', 1)), ('error', ('osd', 5)), ('save', ('osd', 10)),
            ('launch', ('seq', 'SNDLOGOS')), ('disc', ('osd', 10)), ('random', ('osd', 6)),
            ('music', ('seq', 'SNDWARNS')), ('music', ('seq', 'SNDCLOKS'))]


# ------------------------------------------------------------------------------ helpers
def human(n):
    for u in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or u == 'GB':
            return ('%d %s' % (n, u)) if u == 'B' else ('%.1f %s' % (n, u))
        n /= 1024.0


def mmss(s):
    s = max(0, int(s))
    return '%d:%02d' % (s // 60, s % 60)


def clean_title(stem):
    """A music title for RIPPS2's picker: no 'bgm', no leading track number, at most 40 characters."""
    t = ''.join(c if c.isalnum() or c in ' -()' else ' ' for c in stem.replace('_', ' '))
    words = [w for w in t.split() if w.lower() != 'bgm']
    while words and (words[0].isdigit() or words[0] == '-'):
        words.pop(0)
    return (' '.join(words)[:40].strip() or 'Track')


def event_for_name(stem):
    s = ''.join(c for c in stem.lower() if c.isalnum() or c == '_')
    for key, label, _d, _m in sorted(EVENTS, key=lambda e: -len(e[0])):
        if s == key or s.startswith(key) or key in s or label.lower().replace(' ', '') in s.replace('_', ''):
            return key
    return None


def drives():
    if os.name != 'nt':
        return [Path('/')]
    out = []
    for c in string.ascii_uppercase:
        p = Path(c + ':/')
        try:
            if p.exists():
                out.append(p)
        except OSError:
            pass
    return out


def open_folder(p):
    p.mkdir(parents=True, exist_ok=True)
    if os.name == 'nt':
        os.startfile(str(p))
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', str(p)])
    else:
        subprocess.Popen(['xdg-open', str(p)])


# ------------------------------------------------------------------------------ the towers
class Towers:
    """RIPPS2's towers as a spectrum analyser: 16 bands across, the last moments rolling back."""
    BANDS, ROWS = 16, 9

    def __init__(self):
        self.h = np.zeros((self.ROWS, self.BANDS), np.float32)
        self.live = np.zeros(self.BANDS, np.float32)
        self.t_row = 0.0
        self.edges = np.geomspace(45, 16000, self.BANDS + 1)

    def feed(self, frame, rate, dt):
        if frame is None:
            t = time.time()
            target = 0.12 + 0.07 * np.sin(t * 0.9 + np.arange(self.BANDS) * 0.55) ** 2
        else:
            win = frame * np.hanning(len(frame))
            sp = np.abs(np.fft.rfft(win))
            f = np.fft.rfftfreq(len(frame), 1.0 / rate)
            target = np.zeros(self.BANDS, np.float32)
            for b in range(self.BANDS):
                m = (f >= self.edges[b]) & (f < self.edges[b + 1])
                if m.any():
                    e = sp[m].mean() * (1 + b * 0.08)
                    target[b] = np.clip((20 * np.log10(e + 1e-9) + 18) / 52, 0, 1)
        k = 1 - math.exp(-dt / 0.06)
        up = target > self.live
        self.live[up] += (target[up] - self.live[up]) * min(1, k * 2.5)
        self.live[~up] += (target[~up] - self.live[~up]) * k * 0.6
        self.t_row += dt
        if self.t_row > 0.07:
            self.t_row = 0
            self.h[1:] = self.h[:-1] * 0.97
        self.h[0] = self.live

    def draw(self, surf):
        cx, horizon, f = W / 2, H * 0.42, 760.0
        cam_y, cam_z = 6.5, -9.0
        lay = pygame.Surface((W, H), pygame.SRCALPHA)
        # the floor grid
        for i in range(-12, 13):
            x = i * 1.2
            p0 = (cx + x * f / (2 - cam_z), horizon + cam_y * f / (2 - cam_z))
            p1 = (cx + x * f / (40 - cam_z), horizon + cam_y * f / (40 - cam_z))
            pygame.draw.line(lay, (50, 90, 220, 70), p0, p1, 1)
        for j in range(0, 30):
            z = 2 + j * 1.3
            y = horizon + cam_y * f / (z - cam_z)
            pygame.draw.line(lay, (50, 90, 220, max(10, 80 - j * 3)), (0, y), (W, y), 1)
        bw, gap = 0.62, 0.78
        for r in range(self.ROWS - 1, -1, -1):
            z = 2.2 + r * 1.05
            for b in range(self.BANDS):
                x0 = (b - self.BANDS / 2) * gap
                hgt = 0.25 + float(self.h[r, b]) * 5.2
                pts = {}
                for nm, (x, y, zz) in {'a': (x0, 0, z), 'b': (x0 + bw, 0, z), 'c': (x0 + bw, hgt, z), 'd': (x0, hgt, z),
                                      'e': (x0, hgt, z + bw), 'f': (x0 + bw, hgt, z + bw), 'g': (x0 + bw, 0, z + bw)}.items():
                    d = zz - cam_z
                    pts[nm] = (cx + x * f / d, horizon + (cam_y - y) * f / d)
                fade = 1 - r / (self.ROWS + 1)
                glow = 0.35 + 0.65 * float(self.h[r, b])
                front = (40, 80, 200, int(70 * fade * glow + 20))
                top = (120, 170, 255, int(110 * fade * glow + 25))
                edge = (150, 200, 255, int(200 * fade * glow + 30))
                pygame.draw.polygon(lay, front, [pts['a'], pts['b'], pts['c'], pts['d']])
                pygame.draw.polygon(lay, top, [pts['d'], pts['c'], pts['f'], pts['e']])
                side = [pts['b'], pts['g'], pts['f'], pts['c']] if x0 + bw / 2 < 0 else [pts['a'], pts['d'], pts['e'], (pts['a'][0], pts['g'][1])]
                pygame.draw.polygon(lay, (30, 60, 160, int(60 * fade * glow + 15)), side)
                pygame.draw.lines(lay, edge, True, [pts['a'], pts['b'], pts['c'], pts['d']], 1)
                pygame.draw.lines(lay, edge, False, [pts['d'], pts['e'], pts['f'], pts['c']], 1)
        surf.blit(lay, (0, 0))


# ------------------------------------------------------------------------------ the player
class Player:
    def __init__(self):
        self.sound = None
        self.data = None
        self.start = 0.0
        self.label = ''
        self.kind = ''

    def play(self, x, label, kind):
        self.stop()
        pcm = (np.clip(x, -1, 1).T * 32767).astype(np.int16)
        self.data = pcm
        self.sound = pygame.sndarray.make_sound(np.ascontiguousarray(pcm))
        self.sound.play()
        self.start = time.time()
        self.label, self.kind = label, kind

    def stop(self):
        if self.sound:
            self.sound.stop()
        self.sound = None

    @property
    def playing(self):
        return self.sound is not None and pygame.mixer.get_busy()

    @property
    def pos(self):
        return time.time() - self.start if self.sound else 0.0

    @property
    def dur(self):
        return len(self.data) / 44100.0 if self.data is not None else 0.0

    def frame(self, n=2048):
        if not self.playing:
            return None
        i = int(self.pos * 44100)
        if i + n >= len(self.data):
            return None
        return self.data[i:i + n].mean(axis=1).astype(np.float32) / 32768.0


# ------------------------------------------------------------------------------ the app
class Studio:
    TABS = ['BROWSE', 'AUDIO FOLDER', 'YOUR BIOS']

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        pygame.display.set_caption('RIPPS2 Audio Studio')
        self.screen = pygame.display.set_mode((W, H), pygame.SCALED | pygame.RESIZABLE)
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        for k, hh in enumerate((14, 24, 18, 28, 12)):
            pygame.draw.rect(icon, (90 + k * 20, 150, 255), (2 + k * 6, 30 - hh, 5, hh))
        pygame.display.set_icon(icon)
        fp = aio.APP_DIR / 'fonts' / 'ripps2_sleek_case.ttf'
        self.f = {s: pygame.font.Font(str(fp), s) for s in (16, 18, 20, 22, 24, 26, 30, 40, 56)}
        self.clock = pygame.time.Clock()
        self.towers = Towers()
        self.player = Player()
        self.tab = 0
        self.bg = self._backdrop()
        home = Path.home() / 'Music'
        self.cwd = home if home.exists() else Path.home()
        self.entries, self.sel, self.top = [], 0, 0
        self.list_dir()
        self.cache = {}           # path -> stereo float (original)
        self.ps2 = {}             # key -> adp bytes (the PS2 version)
        self.popup = None
        self.toast = ('Browse to a sound or a song. Enter converts it for RIPPS2.', time.time())
        self.jobs = queue.Queue()
        self.results = queue.Queue()
        self.busy = None          # (label, fraction)
        threading.Thread(target=self.worker, daemon=True).start()
        self.out_sel, self.out_top = 0, 0
        self.bios = None          # dict(path, files, items, renders)
        self.bios_sel, self.bios_top = 0, 0
        self.pad = None
        self.repeat = {}
        self.last_click = (0, -1)
        self.running = True
        OUT_DIR.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------- background work
    def worker(self):
        while True:
            label, fn, done = self.jobs.get()
            self.busy = (label, 0.0)
            try:
                res = fn(lambda fr: setattr(self, 'busy', (label, fr)))
                self.results.put((done, res, None))
            except Exception as ex:      # shown to the user, never fatal
                self.results.put((done, None, ex))
            self.busy = None

    def submit(self, label, fn, done):
        self.jobs.put((label, fn, done))

    def say(self, text):
        self.toast = (text, time.time())

    # -------------------------------------------------------------- the browser
    def list_dir(self, keep=None):
        ents = []
        if self.cwd is None:
            ents = [('drive', p, p.drive or str(p), 0) for p in drives()]
        else:
            ents.append(('up', self.cwd.parent if self.cwd.parent != self.cwd else None, '..', 0))
            try:
                items = sorted(self.cwd.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            except OSError as ex:
                items = []
                self.say('Cannot open this folder: %s' % ex)
            for p in items:
                try:
                    if p.name.startswith('.') or p.name.startswith('$'):
                        continue
                    if p.is_dir():
                        ents.append(('dir', p, p.name, 0))
                    else:
                        ext = p.suffix.lower()
                        if ext in aio.AUDIO_EXT:
                            ents.append(('audio', p, p.name, p.stat().st_size))
                        elif ext in aio.BIOS_EXT and p.stat().st_size >= 2 * 1024 * 1024:
                            ents.append(('bios', p, p.name, p.stat().st_size))
                except OSError:
                    pass
        self.entries = ents
        self.sel = 0
        if keep is not None:
            for k, e in enumerate(ents):
                if e[1] == keep:
                    self.sel = k
        self.top = max(0, self.sel - 6)

    def enter(self):
        if not self.entries:
            return
        kind, p, name, _ = self.entries[self.sel]
        if kind == 'up':
            old = self.cwd
            self.cwd = p
            self.list_dir(keep=old)
        elif kind in ('dir', 'drive'):
            self.cwd = p
            self.list_dir()
        elif kind == 'audio':
            self.open_assign(('file', p))
        elif kind == 'bios':
            self.load_bios(p)

    def back(self):
        if self.cwd is None:
            return
        old = self.cwd
        par = self.cwd.parent
        self.cwd = None if par == self.cwd else par
        self.list_dir(keep=old)

    def get_audio(self, src, then):
        """src is ('file', path) or ('bios', key): the original sound, loaded or rendered once."""
        key = src
        if key in self.cache:
            then(self.cache[key])
            return
        if src[0] == 'file':
            fn = lambda prog: aio.load(src[1])
            label = 'READING ' + src[1].name
        else:
            fn = lambda prog: self.render_bios(src[1])
            label = 'RENDERING FROM YOUR BIOS'

        def done(res):
            self.cache[key] = res
            then(res)
        self.submit(label, fn, done)

    def play_original(self, src, name):
        self.get_audio(src, lambda x: self.player.play(x, name, 'ORIGINAL'))

    def play_ps2(self, src, name, event=None):
        def have(x):
            ev = event or ('music' if x.shape[1] > 30 * 44100 else 'confirm')
            if ev == 'music':
                self.player.play(x, name, 'MUSIC (STEREO, AS IS)')
                return
            key = (src, ev)
            if key in self.ps2:
                self.player.play(aio.adp_preview(self.ps2[key]), name, 'PS2 VERSION')
                return
            mx = EVENT[ev][3]
            fn = lambda prog: aio.to_adp(aio.peak_normalize(aio.trim(x)), progress=prog, max_seconds=mx)

            def done(data):
                self.ps2[key] = data
                self.player.play(aio.adp_preview(data), name, 'PS2 VERSION')
            self.submit('MAKING THE PS2 VERSION', fn, done)
        self.get_audio(src, have)

    # -------------------------------------------------------------- converting
    def open_assign(self, src):
        rows = [('music', 'Music', 'A track for Settings > Audio Settings > Music')] + [(k, l, d) for k, l, d, _m in EVENTS]
        guess = event_for_name(src[1].stem) if src[0] == 'file' else None
        sel = next((i for i, r in enumerate(rows) if r[0] == guess), 0)
        self.popup = dict(kind='assign', src=src, rows=rows, sel=sel, top=max(0, sel - 5))

    def convert(self, src, event, quiet=False, then=None):
        name = src[1].name if src[0] == 'file' else self.bios_label(src[1])

        def have(x):
            if event == 'music':
                n = 1 + sum(1 for p in OUT_DIR.glob('bgm_*'))
                title = clean_title(src[1].stem if src[0] == 'file' else self.bios_label(src[1]))
                dst = OUT_DIR / ('bgm_%02d %s' % (n, title))
                fn = lambda prog: aio.write_music(aio.loudness_match(x), dst)

                def done(path):
                    if not quiet:
                        self.say('Music: %s (%s)' % (Path(path).name, human(Path(path).stat().st_size)))
                    if then:
                        then()
                self.submit('WRITING MUSIC', fn, done)
                return
            mx = EVENT[event][3]
            fn = lambda prog: aio.to_adp(aio.peak_normalize(aio.trim(x)), progress=prog, max_seconds=mx)

            def done(data):
                (OUT_DIR / (event + '.adp')).write_bytes(data)
                self.ps2[(src, event)] = data
                if not quiet:
                    self.say('%s.adp from %s (%s)%s' % (event, name, human(len(data)),
                                                       '  The tail was faded at %g s.' % mx if x.shape[1] > mx * 44100 else ''))
                if then:
                    then()
            self.submit('CONVERTING TO ' + event.upper() + '.ADP', fn, done)
        self.get_audio(src, have)

    def convert_folder(self):
        if self.cwd is None:
            return
        files = [e[1] for e in self.entries if e[0] == 'audio']
        plan = []
        for p in files:
            ev = event_for_name(p.stem)
            if ev:
                plan.append((p, ev))
            else:
                try:
                    import soundfile as sf
                    dur = sf.info(str(p)).duration
                except Exception:
                    dur = p.stat().st_size / 40000.0
                plan.append((p, 'music' if dur > 25 else None))
        self.popup = dict(kind='folder', plan=plan, sel=0, top=0)

    def run_plan(self, plan):
        todo = [(('file', p), ev) for p, ev in plan if ev]
        self.say('Converting %d files ...' % len(todo))

        def step(i=0):
            if i >= len(todo):
                self.say('Done: %d files are in output/AUDIO.' % len(todo))
                return
            src, ev = todo[i]
            self.convert(src, ev, quiet=True, then=lambda: step(i + 1))
        step()

    # -------------------------------------------------------------- your BIOS
    def load_bios(self, path):
        def fn(prog):
            files = ps2bios.sound_files(path)
            items = []
            for e in ps2bios.osd_sounds(files['SNDOSDDH']):
                items.append((('osd', e['index']), 'Menu sound %d' % (e['index'] + 1), OSD_ROLE.get(e['index'])))
            for k, (bank, label) in ps2bios.SEQUENCES.items():
                if k in files:
                    items.append((('seq', k), label, {'SNDBOOTS': 'boot', 'SNDLOGOS': 'launch', 'SNDWARNS': 'music'}.get(k)))
            return dict(path=path, files=files, items=items)

        def done(b):
            self.bios = b
            self.bios_sel, self.bios_top = 0, 0
            self.tab = 2
            ver = b['files']['_ROMVER'][:14].decode('latin1', 'replace')
            self.say('BIOS %s: %d menu sounds and %d pieces of system music.' % (
                ver, sum(1 for i in b['items'] if i[0][0] == 'osd'), sum(1 for i in b['items'] if i[0][0] == 'seq')))
        self.submit('READING YOUR BIOS', fn, done)

    def bios_label(self, key):
        if self.bios:
            for k, label, _r in self.bios['items']:
                if k == key:
                    return label
        return str(key)

    def render_bios(self, key):
        f = self.bios['files']
        if key[0] == 'osd':
            st = ps2bios.render_osd(f, key[1], wet=0.3)
        else:
            st = ps2bios.render_seq(f, key[1])
        st = aio.resample(st, 48000, 44100)
        return aio.peak_normalize(st, 0.9)

    def rip_bios(self):
        if not self.bios:
            self.say('Pick your BIOS dump in BROWSE first (the .bin PCSX2 uses).')
            return
        have = {k for k, _l, _r in self.bios['items']}
        todo = [(('bios', key), ev) for ev, key in BIOS_RIP if key in have]

        def step(i=0):
            if i >= len(todo):
                self.say('Ripped %d sounds and tracks from your BIOS into output/AUDIO.' % len(todo))
                self.tab = 1
                return
            src, ev = todo[i]
            self.convert(src, ev, quiet=True, then=lambda: step(i + 1))
        self.say('Ripping your BIOS: %d items ...' % len(todo))
        step()

    # -------------------------------------------------------------- output
    def outputs(self):
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        rows = []
        for p in sorted(OUT_DIR.iterdir(), key=lambda p: (not p.name.lower().startswith('boot'), p.name.lower())):
            if p.is_file():
                ev = p.stem if p.suffix.lower() == '.adp' else 'music'
                rows.append((p, ev, p.stat().st_size))
        return rows

    # -------------------------------------------------------------- drawing
    def _backdrop(self):
        s = pygame.Surface((W, H))
        for y in range(H):
            u = y / H
            c = [int(BG_TOP[i] + (BG_MID[i] - BG_TOP[i]) * min(1, (u / 0.55) ** 1.5)) if u < 0.55 else
                 int(BG_MID[i] + (BG_TOP[i] - BG_MID[i]) * ((u - 0.55) / 0.45) ** 0.8) for i in range(3)]
            pygame.draw.line(s, c, (0, y), (W, y))
        return s

    def text(self, s, size, color, pos, anchor='topleft', maxw=None):
        f = self.f[size]
        if maxw:
            while f.size(s)[0] > maxw and len(s) > 4:
                s = s[:-4] + '...'
        img = f.render(s, True, color)
        r = img.get_rect(**{anchor: pos})
        self.screen.blit(img, r)
        return r

    def para(self, lines, x, y, w, size=18, color=SOFT, gap=6):
        """Lines of text, each wrapped to width w. Returns the y after the last line."""
        f = self.f[size]
        lh = f.get_linesize() + 2
        for ln in lines:
            if not ln:
                y += lh // 2
                continue
            words, cur = ln.split(' '), ''
            for wd in words:
                nxt = (cur + ' ' + wd).strip()
                if f.size(nxt)[0] <= w or not cur:
                    cur = nxt
                else:
                    self.screen.blit(f.render(cur, True, color), (x, y))
                    y += lh
                    cur = wd
            if cur:
                self.screen.blit(f.render(cur, True, color), (x, y))
                y += lh
            y += gap
        return y

    def panel(self, rect, alpha=150):
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        s.fill((6, 14, 44, alpha))
        self.screen.blit(s, rect[:2])
        pygame.draw.rect(self.screen, (60, 100, 220), rect, 1)

    def glyph(self, kind, center):
        x, y = center
        c = WHITE
        pygame.draw.circle(self.screen, c, (x, y), 10, 1)
        if kind == 'cross':
            pygame.draw.line(self.screen, c, (x - 4, y - 4), (x + 4, y + 4), 2)
            pygame.draw.line(self.screen, c, (x - 4, y + 4), (x + 4, y - 4), 2)
        elif kind == 'circle':
            pygame.draw.circle(self.screen, c, (x, y), 5, 2)
        elif kind == 'square':
            pygame.draw.rect(self.screen, c, (x - 4, y - 4, 9, 9), 2)
        elif kind == 'triangle':
            pygame.draw.polygon(self.screen, c, [(x, y - 5), (x - 5, y + 4), (x + 5, y + 4)], 2)
        elif kind == 'start':
            pygame.draw.polygon(self.screen, c, [(x - 3, y - 5), (x - 3, y + 5), (x + 5, y)], 0)
        elif kind in ('l1', 'r1'):
            pygame.draw.rect(self.screen, BG_TOP, (x - 11, y - 11, 23, 23))
            pygame.draw.rect(self.screen, c, (x - 12, y - 8, 24, 16), 1, border_radius=4)
            self.text(kind.upper(), 16, c, (x, y + 1), 'center')

    def hints(self, items):
        """The hint row at the bottom, as RIPPS2 draws it; each is clickable."""
        x = 40
        self.hint_rects = []
        for kind, label in items:
            self.glyph(kind, (x + 10, H - 30))
            r = self.text(label, 20, WHITE, (x + 26, H - 30), 'midleft')
            self.hint_rects.append((pygame.Rect(x - 4, H - 46, r.right - x + 12, 32), kind))
            x = r.right + 30

    def draw_tabs(self):
        self.tab_rects = []
        xs = [W / 2 - 300, W / 2, W / 2 + 300]
        for k, name in enumerate(self.TABS):
            active = k == self.tab
            r = self.text(name, 30 if active else 24, WHITE if active else DIM, (xs[k], 34), 'center')
            self.tab_rects.append(r.inflate(30, 20))
            if active:
                bar = pygame.Rect(r.centerx - 38, r.bottom + 6, 76, 5)
                pygame.draw.rect(self.screen, CYAN, bar)
                g = pygame.Surface((110, 24), pygame.SRCALPHA)
                pygame.draw.rect(g, (90, 160, 255, 60), (0, 0, 110, 24), border_radius=12)
                self.screen.blit(g, (r.centerx - 55, r.bottom - 3))
        self.text('L1', 16, FAINT, (xs[0] - 150, 34), 'center')
        self.text('R1', 16, FAINT, (xs[2] + 150, 34), 'center')
        self.text('RIPPS2 AUDIO STUDIO', 16, FAINT, (W - 24, H - 14), 'bottomright')

    def draw_list(self, rect, rows, sel, top, title):
        """rows: (icon, name, right text, color). Returns visible row rects (index, rect)."""
        x, y, w, h = rect
        self.panel(rect)
        self.text(title, 20, SOFT, (x + 16, y + 10), maxw=w - 32)
        pygame.draw.line(self.screen, (60, 100, 220), (x + 12, y + 38), (x + w - 12, y + 38))
        rh = 30
        vis = (h - 50) // rh
        out = []
        for k in range(top, min(len(rows), top + vis)):
            ry = y + 46 + (k - top) * rh
            rr = pygame.Rect(x + 8, ry, w - 16, rh - 2)
            if k == sel:
                pygame.draw.rect(self.screen, SEL, rr)
                pygame.draw.rect(self.screen, CYAN, (rr.x, rr.y, 4, rr.h))
            icon, name, right, color = rows[k]
            self.draw_icon(icon, (rr.x + 22, rr.centery))
            self.text(name, 20, color, (rr.x + 42, rr.centery), 'midleft', maxw=w - 200)
            if right:
                self.text(right, 18, SOFT if k != sel else WHITE, (rr.right - 10, rr.centery), 'midright')
            out.append((k, rr))
        if len(rows) > vis:
            frac = top / max(1, len(rows) - vis)
            sb = pygame.Rect(x + w - 6, y + 46 + int((h - 70) * frac), 3, 20)
            pygame.draw.rect(self.screen, BLUE, sb)
        return out

    def draw_icon(self, kind, c):
        x, y = c
        if kind in ('dir', 'up', 'drive'):
            pygame.draw.rect(self.screen, (120, 160, 255), (x - 9, y - 5, 18, 12))
            pygame.draw.rect(self.screen, (120, 160, 255), (x - 9, y - 8, 8, 4))
            if kind == 'up':
                pygame.draw.polygon(self.screen, BG_TOP, [(x, y - 3), (x - 4, y + 3), (x + 4, y + 3)])
        elif kind == 'bios':
            pygame.draw.rect(self.screen, CYAN, (x - 8, y - 7, 16, 14), 1)
            for k in range(-6, 8, 4):
                pygame.draw.line(self.screen, CYAN, (x + k, y - 10), (x + k, y - 7))
                pygame.draw.line(self.screen, CYAN, (x + k, y + 7), (x + k, y + 10))
        elif kind == 'music':
            pygame.draw.circle(self.screen, CYAN, (x - 4, y + 5), 4)
            pygame.draw.line(self.screen, CYAN, (x - 1, y + 5), (x - 1, y - 8), 2)
            pygame.draw.line(self.screen, CYAN, (x - 1, y - 8), (x + 6, y - 5), 2)
        else:
            pygame.draw.rect(self.screen, (170, 190, 240), (x - 6, y - 8, 13, 16), 1)
            for k in range(3):
                pygame.draw.line(self.screen, (170, 190, 240), (x - 3, y - 3 + k * 4), (x + 3, y - 3 + k * 4))

    def draw_preview(self, rect):
        """The player panel, laid out like RIPPS2's CD player."""
        x, y, w, h = rect
        self.panel(rect)
        p = self.player
        self.text('PREVIEW', 20, SOFT, (x + 16, y + 12))
        name = p.label if p.sound else 'Nothing playing'
        self.text(name, 24, WHITE, (x + 16, y + 44), maxw=w - 32)
        state = ('PLAYING ' + p.kind) if p.playing else 'STOPPED'
        self.text(state, 18, CYAN if p.playing else DIM, (x + 16, y + 78))
        if p.sound:
            self.text('%s / %s' % (mmss(min(p.pos, p.dur)), mmss(p.dur)), 18, SOFT, (x + w - 16, y + 78), 'topright')
            frac = min(1.0, p.pos / max(p.dur, 1e-6))
            pygame.draw.rect(self.screen, FAINT, (x + 16, y + 104, w - 32, 4))
            pygame.draw.rect(self.screen, BLUE, (x + 16, y + 104, int((w - 32) * frac), 4))

    def draw_status(self):
        if self.busy:
            label, fr = self.busy
            r = pygame.Rect(W / 2 - 260, H - 110, 520, 50)
            self.panel(r, 210)
            self.text(label, 20, WHITE, (r.centerx, r.y + 16), 'center', maxw=480)
            pygame.draw.rect(self.screen, FAINT, (r.x + 20, r.y + 34, r.w - 40, 4))
            t = time.time()
            if fr and fr > 0:
                pygame.draw.rect(self.screen, CYAN, (r.x + 20, r.y + 34, int((r.w - 40) * fr), 4))
            else:
                k = (t * 0.8) % 1.0
                pygame.draw.rect(self.screen, CYAN, (r.x + 20 + int((r.w - 120) * k), r.y + 34, 80, 4))
        msg, t0 = self.toast
        age = time.time() - t0
        if msg and age < 9:
            a = 255 if age < 7 else int(255 * (9 - age) / 2)
            img = self.f[20].render(msg, True, WHITE)
            img.set_alpha(a)
            self.screen.blit(img, img.get_rect(midtop=(W / 2, 74)))

    # -------------------------------------------------------------- screens
    def frame(self):
        self.screen.blit(self.bg, (0, 0))
        self.towers.draw(self.screen)
        self.draw_tabs()
        if self.tab == 0:
            self.screen_browse()
        elif self.tab == 1:
            self.screen_output()
        else:
            self.screen_bios()
        if self.popup:
            self.screen_popup()
        self.draw_status()

    def screen_browse(self):
        rows = []
        for kind, p, name, size in self.entries:
            if kind == 'up':
                rows.append(('up', '..', '', SOFT))
            elif kind in ('dir', 'drive'):
                rows.append(('dir', name, '', WHITE))
            elif kind == 'bios':
                rows.append(('bios', name, 'BIOS?  ' + human(size), CYAN))
            else:
                ev = event_for_name(p.stem)
                rows.append(('file', name, (EVENT[ev][1].upper() + '  ' if ev else '') + human(size), WHITE))
        title = 'COMPUTER' if self.cwd is None else str(self.cwd).replace('\\', '/')
        self.vis = self.draw_list((40, 100, 720, 500), rows, self.sel, self.top, title)
        self.draw_preview((790, 100, 450, 130))
        info = pygame.Rect(790, 250, 450, 350)
        self.panel(info)
        tx = info.x + 16
        if self.entries and self.entries[self.sel][0] == 'audio':
            p = self.entries[self.sel][1]
            ev = event_for_name(p.stem)
            self.text('A SOUND OR A SONG', 20, SOFT, (tx, info.y + 12))
            self.text(p.name, 24, WHITE, (tx, info.y + 44), maxw=info.w - 32)
            lines = ['Cross (Enter) makes it one of RIPPS2\'s sounds, or music.',
                     'Square (Space) plays it as it is.',
                     'Triangle (P) plays it as the PS2 will: mono SPU2 ADPCM at 44.1 kHz.']
            if ev:
                lines.append('Its name says %s: that is picked first.' % EVENT[ev][1])
        elif self.entries and self.entries[self.sel][0] == 'bios':
            self.text('A PS2 BIOS?', 20, SOFT, (tx, info.y + 12))
            self.text(self.entries[self.sel][2], 24, WHITE, (tx, info.y + 44), maxw=info.w - 32)
            lines = ['Your own console\'s BIOS dump (the file PCSX2 uses).',
                     'Enter opens it: its menu sounds and system music,',
                     'rendered fresh, ready to rip into output/AUDIO.']
        else:
            self.text('MAKE AN AUDIO FOLDER', 20, SOFT, (tx, info.y + 12))
            lines = ['Pick a sound or a song to convert it.',
                     'Start (S) converts a whole folder: files named for an event (cursor.wav, boot.mp3) become that sound, long ones become music.',
                     'Pick your PS2 BIOS dump to rip the console\'s own sounds.',
                     '',
                     'Everything lands in output/AUDIO beside this app. Copy it beside RIPPS2.ELF: a USB stick and RIPPS2\'s Memory Files are the easy way.']
        self.para(lines, tx, info.y + 84, info.w - 32)
        self.hints([('cross', 'OPEN / CONVERT'), ('circle', 'BACK'), ('square', 'PLAY'), ('triangle', 'PS2 VERSION'),
                    ('start', 'CONVERT FOLDER'), ('l1', 'TABS')])

    def screen_output(self):
        outs = self.outputs()
        sfx = sum(s for p, ev, s in outs if ev != 'music')
        rows = []
        have = {ev for p, ev, s in outs}
        for p, ev, size in outs:
            label = EVENT[ev][1] if ev in EVENT else ('Music' if ev == 'music' else ev)
            rows.append(('music' if ev == 'music' else 'file', p.name, '%s  %s' % (label.upper(), human(size)), WHITE))
        self.out_vis = self.draw_list((40, 100, 720, 500), rows, self.out_sel, self.out_top,
                                      str(OUT_DIR).replace('\\', '/'))
        self.draw_preview((790, 100, 450, 130))
        info = pygame.Rect(790, 250, 450, 350)
        self.panel(info)
        tx = info.x + 16
        self.text('THE AUDIO FOLDER', 20, SOFT, (tx, info.y + 12))
        col = WARN if sfx > SFX_BUDGET else WHITE
        self.text('Sounds: %s of %s sound RAM' % (human(sfx), human(SFX_BUDGET)), 22, col, (tx, info.y + 44))
        pygame.draw.rect(self.screen, FAINT, (tx, info.y + 76, info.w - 32, 5))
        pygame.draw.rect(self.screen, WARN if sfx > SFX_BUDGET else CYAN,
                         (tx, info.y + 76, int((info.w - 32) * min(1, sfx / SFX_BUDGET)), 5))
        missing = [EVENT[e][1] for e, *_ in EVENTS if e not in have]
        lines = ['Every sound is loaded into the PS2\'s sound RAM at once (the music streams, so it does not count). Sounds you leave out play RIPPS2\'s own, which take room too. Missing: ' + (', '.join(missing) if missing else 'none') + '.',
                 '',
                 'Copy this AUDIO folder to a USB stick, then in RIPPS2\'s Memory Files copy it beside RIPPS2.ELF.',
                 'Settings > Audio Settings > Music picks the track.']
        self.para(lines, tx, info.y + 98, info.w - 32)
        self.hints([('cross', 'PLAY'), ('triangle', 'DELETE'), ('start', 'OPEN FOLDER'), ('l1', 'TABS')])

    def screen_bios(self):
        if not self.bios:
            r = pygame.Rect(240, 200, 800, 300)
            self.panel(r)
            lines = ['BRING YOUR OWN BIOS',
                     '',
                     'Dump the BIOS of your own PS2 (the file PCSX2 asks for),',
                     'then pick it in BROWSE. Its menu sounds and its system music',
                     '(boot, tower tunnel, logo, clock, ambient) are rendered here',
                     'from the BIOS itself, the way the console\'s sound chip plays them.',
                     '',
                     'Nothing from any BIOS comes with RIPPS2 or this app.']
            for k, ln in enumerate(lines):
                self.text(ln, 24 if k == 0 else 20, WHITE if k == 0 else SOFT, (r.centerx, r.y + 30 + k * 30), 'midtop')
            self.hints([('l1', 'TABS')])
            return
        rows = []
        for key, label, role in self.bios['items']:
            role_s = ('-> ' + (EVENT[role][1] if role in EVENT else 'Music')).upper() if role else ''
            rows.append(('music' if key[0] == 'seq' else 'file', label, role_s, WHITE if key[0] == 'osd' else CYAN))
        ver = self.bios['files']['_ROMVER'][:14].decode('latin1', 'replace')
        self.bios_vis = self.draw_list((40, 100, 720, 500), rows, self.bios_sel, self.bios_top,
                                       '%s  (ROM %s)' % (Path(self.bios['path']).name, ver))
        self.draw_preview((790, 100, 450, 130))
        info = pygame.Rect(790, 250, 450, 350)
        self.panel(info)
        tx = info.x + 16
        self.text('YOUR BIOS', 20, SOFT, (tx, info.y + 12))
        lines = ['Square plays a sound, rendered from your BIOS the way the console\'s sound chip plays it.',
                 'Cross makes it one of RIPPS2\'s sounds, or music.',
                 'Start rips the lot as the console uses them: its boot, its menu sounds, the PS2 logo for a launch, and its ambient and clock music.',
                 '',
                 'For your own console and your own use only.']
        self.para(lines, tx, info.y + 48, info.w - 32)
        self.hints([('cross', 'CONVERT'), ('square', 'PLAY'), ('start', 'RIP ALL'), ('l1', 'TABS')])

    def screen_popup(self):
        pu = self.popup
        r = pygame.Rect(W / 2 - 330, 110, 660, 470)
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 120))
        self.screen.blit(s, (0, 0))
        self.panel(r, 235)
        if pu['kind'] == 'assign':
            name = pu['src'][1].name if pu['src'][0] == 'file' else self.bios_label(pu['src'][1])
            self.text('MAKE IT ...', 20, SOFT, (r.x + 20, r.y + 12))
            self.text(name, 24, WHITE, (r.x + 20, r.y + 40), maxw=r.w - 40)
            rows = [('music' if k == 'music' else 'file', l, d, WHITE) for k, l, d in pu['rows']]
            self.pop_vis = self.draw_list((r.x + 10, r.y + 76, r.w - 20, r.h - 86), rows, pu['sel'], pu['top'], 'RIPPS2 SOUNDS (RIPTOPL\'S NAMES FIRST)')
        else:
            plan = pu['plan']
            n_s = sum(1 for p, e in plan if e and e != 'music')
            n_m = sum(1 for p, e in plan if e == 'music')
            self.text('CONVERT THIS FOLDER', 20, SOFT, (r.x + 20, r.y + 12))
            self.text('%d sounds, %d music, %d skipped' % (n_s, n_m, sum(1 for p, e in plan if not e)), 24, WHITE, (r.x + 20, r.y + 40))
            rows = [('music' if e == 'music' else 'file', p.name, (EVENT[e][1] if e in EVENT else 'Music' if e else 'skipped').upper(),
                     WHITE if e else FAINT) for p, e in plan]
            self.pop_vis = self.draw_list((r.x + 10, r.y + 76, r.w - 20, r.h - 86), rows, pu['sel'], pu['top'], 'Cross converts them all, Circle cancels')

    # -------------------------------------------------------------- input
    def move(self, d):
        if self.popup:
            pu = self.popup
            n = len(pu['rows']) if pu['kind'] == 'assign' else len(pu['plan'])
            pu['sel'] = max(0, min(n - 1, pu['sel'] + d))
            pu['top'] = min(max(pu['top'], pu['sel'] - 10), pu['sel'])
            pu['top'] = max(pu['top'], pu['sel'] - 10)
            return
        if self.tab == 0:
            self.sel = max(0, min(len(self.entries) - 1, self.sel + d))
            self.top = min(self.top, self.sel)
            self.top = max(self.top, self.sel - 14)
        elif self.tab == 1:
            n = len(self.outputs())
            self.out_sel = max(0, min(n - 1, self.out_sel + d))
            self.out_top = max(min(self.out_top, self.out_sel), self.out_sel - 14)
        elif self.bios:
            n = len(self.bios['items'])
            self.bios_sel = max(0, min(n - 1, self.bios_sel + d))
            self.bios_top = max(min(self.bios_top, self.bios_sel), self.bios_sel - 14)

    def act(self, b):
        """b: cross, circle, square, triangle, start, l1, r1, select."""
        if b in ('l1', 'r1') and not self.popup:
            self.tab = (self.tab + (1 if b == 'r1' else -1)) % 3
            return
        if self.popup:
            pu = self.popup
            if b == 'circle':
                self.popup = None
            elif b == 'cross':
                self.popup = None
                if pu['kind'] == 'assign':
                    self.convert(pu['src'], pu['rows'][pu['sel']][0])
                else:
                    self.run_plan(pu['plan'])
            elif b == 'square' and pu['kind'] == 'assign':
                name = pu['src'][1].name if pu['src'][0] == 'file' else self.bios_label(pu['src'][1])
                ev = pu['rows'][pu['sel']][0]
                (self.play_original if ev == 'music' else (lambda s, n: self.play_ps2(s, n, ev)))(pu['src'], name)
            return
        if b == 'select':
            open_folder(OUT_DIR)
            return
        if self.tab == 0:
            ent = self.entries[self.sel] if self.entries else None
            if b == 'cross':
                self.enter()
            elif b == 'circle':
                self.back()
            elif b == 'square' and ent and ent[0] == 'audio':
                if self.player.playing:
                    self.player.stop()
                else:
                    self.play_original(('file', ent[1]), ent[2])
            elif b == 'triangle' and ent and ent[0] == 'audio':
                self.play_ps2(('file', ent[1]), ent[2], event_for_name(ent[1].stem))
            elif b == 'start':
                self.convert_folder()
        elif self.tab == 1:
            outs = self.outputs()
            if not outs:
                if b == 'start':
                    open_folder(OUT_DIR)
                return
            p, ev, _s = outs[min(self.out_sel, len(outs) - 1)]
            if b == 'cross':
                if self.player.playing:
                    self.player.stop()
                else:
                    self.play_original(('file', p), p.name)
                    self.cache.pop(('file', p), None)
            elif b == 'triangle':
                p.unlink(missing_ok=True)
                self.say('Deleted ' + p.name)
                self.out_sel = max(0, self.out_sel - 1)
            elif b == 'start':
                open_folder(OUT_DIR)
        else:
            if not self.bios:
                return
            key, label, role = self.bios['items'][self.bios_sel]
            if b == 'square':
                if self.player.playing:
                    self.player.stop()
                else:
                    self.play_original(('bios', key), label)
            elif b == 'cross':
                self.open_assign(('bios', key))
                if role:
                    rows = self.popup['rows']
                    self.popup['sel'] = next((i for i, r in enumerate(rows) if r[0] == role), 0)
                    self.popup['top'] = max(0, self.popup['sel'] - 5)
            elif b == 'start':
                self.rip_bios()

    KEYS = {pygame.K_RETURN: 'cross', pygame.K_KP_ENTER: 'cross', pygame.K_BACKSPACE: 'circle', pygame.K_ESCAPE: 'circle',
            pygame.K_SPACE: 'square', pygame.K_p: 'triangle', pygame.K_DELETE: 'triangle', pygame.K_s: 'start',
            pygame.K_F2: 'start', pygame.K_q: 'l1', pygame.K_e: 'r1', pygame.K_o: 'select'}
    PAD = {0: 'cross', 1: 'circle', 2: 'square', 3: 'triangle', 4: 'l1', 5: 'r1', 6: 'select', 7: 'start'}

    def handle(self, ev):
        if ev.type == pygame.QUIT:
            self.running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_TAB:
                self.act('l1' if ev.mod & pygame.KMOD_SHIFT else 'r1')
            elif ev.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                self.move({pygame.K_UP: -1, pygame.K_DOWN: 1, pygame.K_PAGEUP: -12, pygame.K_PAGEDOWN: 12}[ev.key])
            elif ev.key == pygame.K_LEFT and self.tab == 0 and not self.popup:
                self.back()
            elif ev.key == pygame.K_RIGHT and self.tab == 0 and not self.popup:
                if self.entries and self.entries[self.sel][0] in ('dir', 'drive', 'up'):
                    self.enter()
            elif ev.key in self.KEYS:
                self.act(self.KEYS[ev.key])
        elif ev.type == pygame.JOYDEVICEADDED:
            self.pad = pygame.joystick.Joystick(ev.device_index)
        elif ev.type == pygame.JOYBUTTONDOWN:
            if ev.button in self.PAD:
                self.act(self.PAD[ev.button])
        elif ev.type == pygame.JOYHATMOTION:
            x, y = ev.value
            if y:
                self.move(-y)
            if x and self.tab == 0 and not self.popup:
                self.back() if x < 0 else self.act('cross') if self.entries and self.entries[self.sel][0] in ('dir', 'drive', 'up') else None
        elif ev.type == pygame.MOUSEWHEEL:
            self.move(-ev.y * 3)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.click(ev.pos)

    def click(self, pos):
        now = time.time()
        for k, r in enumerate(getattr(self, 'tab_rects', [])):
            if r.collidepoint(pos) and not self.popup:
                self.tab = k
                return
        for r, kind in getattr(self, 'hint_rects', []):
            if r.collidepoint(pos):
                self.act('r1' if kind == 'l1' else kind)
                return
        vis = (self.pop_vis if self.popup else self.vis if self.tab == 0 else self.out_vis if self.tab == 1
               else getattr(self, 'bios_vis', []))
        for k, rr in vis:
            if rr.collidepoint(pos):
                double = self.last_click[1] == k and now - self.last_click[0] < 0.4
                self.last_click = (now, k)
                if self.popup:
                    self.popup['sel'] = k
                elif self.tab == 0:
                    self.sel = k
                elif self.tab == 1:
                    self.out_sel = k
                else:
                    self.bios_sel = k
                if double:
                    self.act('cross')
                return

    def held_axes(self, dt):
        if not self.pad:
            return
        try:
            y = self.pad.get_axis(1)
        except Exception:
            return
        d = 1 if y > 0.6 else -1 if y < -0.6 else 0
        r = self.repeat.get('y', [0, 0.0])
        if d and d != r[0]:
            self.move(d)
            self.repeat['y'] = [d, 0.35]
        elif d:
            r[1] -= dt
            if r[1] <= 0:
                self.move(d)
                r[1] = 0.07
        else:
            self.repeat['y'] = [0, 0.0]

    def run(self):
        self.vis, self.out_vis, self.pop_vis = [], [], []
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for ev in pygame.event.get():
                self.handle(ev)
            self.held_axes(dt)
            while not self.results.empty():
                done, res, err = self.results.get()
                if err:
                    self.say('Could not do that: %s' % err)
                else:
                    done(res)
            self.towers.feed(self.player.frame(), 44100, dt)
            self.frame()
            pygame.display.flip()
        pygame.quit()


def selftest(args):
    """python studio.py --convert <file> <event|music> | --rip <bios> : the app's work, no window."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if args[0] == '--convert':
        x = aio.load(args[1])
        if args[2] == 'music':
            print(aio.write_music(aio.loudness_match(x), OUT_DIR / ('bgm_01 ' + clean_title(Path(args[1]).stem))))
        else:
            data = aio.to_adp(aio.peak_normalize(aio.trim(x)), max_seconds=EVENT[args[2]][3])
            (OUT_DIR / (args[2] + '.adp')).write_bytes(data)
            print(args[2], len(data))
    elif args[0] == '--rip':
        files = ps2bios.sound_files(args[1])
        n = 1
        for ev, key in BIOS_RIP:
            if key[0] == 'seq' and key[1] not in files:
                continue
            st = ps2bios.render_osd(files, key[1], wet=0.3) if key[0] == 'osd' else ps2bios.render_seq(files, key[1])
            x = aio.peak_normalize(aio.resample(st, 48000, 44100), 0.9)
            if ev == 'music':
                p = aio.write_music(aio.loudness_match(x), OUT_DIR / ('bgm_%02d %s' % (n, ps2bios.SEQUENCES[key[1]][1])))
                n += 1
                print('music', Path(p).name, '%.1f s' % (x.shape[1] / 44100))
            else:
                data = aio.to_adp(aio.peak_normalize(aio.trim(x)), max_seconds=EVENT[ev][3])
                (OUT_DIR / (ev + '.adp')).write_bytes(data)
                print(ev, key, len(data))


def shot(out, tab, bios=None, popup=False):
    """--shot out.png <tab> [bios]: draw the window once, for checking the layout."""
    st = Studio()
    st.vis, st.out_vis, st.pop_vis = [], [], []
    if bios:
        files = ps2bios.sound_files(bios)
        st.bios = dict(path=bios, files=files, items=[(('osd', e['index']), 'Menu sound %d' % (e['index'] + 1),
                       OSD_ROLE.get(e['index'])) for e in ps2bios.osd_sounds(files['SNDOSDDH'])] +
                       [(('seq', k), lab, {'SNDBOOTS': 'boot', 'SNDLOGOS': 'launch', 'SNDWARNS': 'music'}.get(k))
                        for k, (bk, lab) in ps2bios.SEQUENCES.items() if k in files])
    st.tab = int(tab)
    if popup and st.tab == 0:
        for k, e in enumerate(st.entries):
            if e[0] == 'audio':
                st.sel = k
                st.open_assign(('file', e[1]))
                break
    for _ in range(40):
        st.towers.feed(None, 44100, 1 / 60)
    st.frame()
    pygame.image.save(st.screen, out)
    pygame.quit()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--shot':
        a = sys.argv[2:]
        shot(a[0], a[1], a[2] if len(a) > 2 and a[2] != '-' else None, popup=len(a) > 3)
    elif len(sys.argv) > 1 and sys.argv[1].startswith('--'):
        selftest(sys.argv[1:])
    else:
        Studio().run()
