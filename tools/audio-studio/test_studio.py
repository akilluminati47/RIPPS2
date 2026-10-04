"""Drives RIPPS2 Audio Studio with key presses, off screen, and checks what lands in output/AUDIO.

    python test_studio.py [bios.bin]
"""
import os
import shutil
import sys
import tempfile
import time
import wave
from pathlib import Path

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import numpy as np
import pygame

import studio


def tone_wav(path, seconds, f=660.0):
    t = np.arange(int(seconds * 44100)) / 44100
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t * 3) * 20000).astype('<i2')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(x.tobytes())


def main():
    work = Path(tempfile.mkdtemp(prefix='studio_test_'))
    tone_wav(work / 'cursor.wav', 0.3)
    tone_wav(work / 'My Song.wav', 31.0, 220.0)
    tone_wav(work / 'click 2.wav', 0.2, 1200.0)
    out = work / 'output' / 'AUDIO'          # never the real output folder
    studio.OUT_DIR = out
    app = studio.Studio()
    app.vis, app.out_vis, app.pop_vis = [], [], []
    app.cwd = work
    app.list_dir()

    def key(k, mod=0):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=k, mod=mod, unicode=''))

    def run(frames=1):
        for _ in range(frames):
            for ev in pygame.event.get():
                app.handle(ev)
            while not app.results.empty():
                done, res, err = app.results.get()
                if err:
                    raise err
                done(res)
            app.towers.feed(app.player.frame(), 44100, 1 / 60)
            app.frame()

    def settle(timeout=600):
        t = time.time()
        while time.time() - t < timeout:
            run(2)
            if app.busy is None and app.jobs.empty() and app.results.empty():
                run(2)
                if app.busy is None and app.jobs.empty() and app.results.empty():
                    return
            time.sleep(0.02)
        raise TimeoutError('the app stayed busy')

    names = [e[2] for e in app.entries]
    print('listed', names)
    # 1. one file: pick "click 2.wav", Enter, choose Confirm in the popup, Enter
    app.sel = names.index('click 2.wav')
    key(pygame.K_SPACE); run(3); settle()
    assert app.player.sound is not None, 'Space should play the original'
    key(pygame.K_p); run(3); settle()
    assert app.player.kind == 'PS2 VERSION', app.player.kind
    key(pygame.K_RETURN); run(2)
    assert app.popup and app.popup['kind'] == 'assign'
    rows = [r[0] for r in app.popup['rows']]
    app.popup['sel'] = rows.index('confirm')
    key(pygame.K_RETURN); run(2); settle()
    assert (out / 'confirm.adp').exists(), 'confirm.adp was not written'
    print('single file -> confirm.adp', (out / 'confirm.adp').stat().st_size)
    # 2. the whole folder: S, then Enter in the plan
    key(pygame.K_s); run(2)
    assert app.popup and app.popup['kind'] == 'folder'
    plan = {p.name: e for p, e in app.popup['plan']}
    print('folder plan', plan)
    key(pygame.K_RETURN); run(2); settle()
    files = sorted(p.name for p in out.iterdir())
    print('output', files)
    assert 'cursor.adp' in files and any(f.startswith('bgm_01 My Song') for f in files)
    # 3. the AUDIO FOLDER tab lists them; Tab moves there
    key(pygame.K_TAB); run(2)
    assert app.tab == 1 and len(app.outputs()) == len(files)
    # 3b. Square plays here too; Triangle asks first: Circle keeps the file, Cross deletes it
    app.out_sel = [p.name for p, e, s in app.outputs()].index('cursor.adp')
    key(pygame.K_SPACE); run(3); settle()
    assert app.player.sound is not None and app.player.label == 'cursor.adp', 'Square should play on AUDIO FOLDER'
    key(pygame.K_p); run(2)
    assert app.popup and app.popup['kind'] == 'delete'
    pygame.image.save(app.screen, str(work / 'delete_modal.png'))
    key(pygame.K_ESCAPE); run(2)
    assert app.popup is None and (out / 'cursor.adp').exists(), 'Circle must keep the file'
    key(pygame.K_p); run(2); key(pygame.K_RETURN); run(2)
    assert not (out / 'cursor.adp').exists(), 'Cross must delete it'
    print('delete modal: kept on Circle, deleted on Cross')
    # 4. your BIOS
    if len(sys.argv) > 1:
        key(pygame.K_TAB, pygame.KMOD_SHIFT); run(2)
        app.load_bios(Path(sys.argv[1])); settle()
        assert app.tab == 2 and app.bios
        print('bios items', len(app.bios['items']))
        app.bios_sel = 6
        key(pygame.K_SPACE); run(2); settle()
        print('played', app.player.label, app.player.kind)
        t = time.time()
        key(pygame.K_s); run(2); settle(1800)
        files = sorted(p.name for p in out.iterdir())
        print('after rip (%.0f s):' % (time.time() - t), files)
        assert 'boot.adp' in files and 'launch.adp' in files and any('Ambient' in f for f in files)
    pygame.image.save(app.screen, str(work / 'last.png'))
    pygame.quit()
    print('ALL OK', work)


if __name__ == '__main__':
    main()
