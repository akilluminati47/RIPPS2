"""Builds a RIPPS2 sound pack (the SOUND folder that sits beside RIPPS2.ELF) from sounds you have
downloaded yourself, using the map below. RIPPS2 ships none of these sounds; this only converts
your own copies (elf/theme/tools/make_adp.py does the conversion, so ffmpeg must be on the PATH).

    python elf/theme/tools/make_sound_pack.py --bios <folder> --system <folder> --ps3 <folder> --out SOUND

--bios holds the PS2 BIOS system sounds (SCPH-10000) named by track: 07.flac, 10.flac ...
--system holds the PS2 system music, for the launch: "04. Game Boot.flac" (any name with "Game Boot").
--ps3 holds the PS3 system sounds, for the error: "10 - SND System Ng.flac" (any name with "System Ng").
Any audio ffmpeg reads will do (flac, mp3, wav).

An event left out of the map plays RIPPS2's built-in sound, or the one it falls back to (random
uses the cursor's).
"""
import argparse
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_adp  # noqa: E402

# event file: (album, track)
MAP = {
    'boot.adp': ('bios', '07'),           # the boot, as the towers rise
    'page_in.adp': ('bios', '10'),        # into an info page or the settings
    'page_out.adp': ('bios', '11'),       # back out to the list
    'cursor.adp': ('bios', '12'),         # every move (and L2 + R2's random pick)
    'confirm.adp': ('bios', '13'),
    'cancel.adp': ('bios', '14'),
    'error.adp': ('ps3', 'System Ng'),    # something could not be done
    'transition.adp': ('bios', '15'),     # the category switch (Launch Disc, Storage, Memory Files)
    'save.adp': ('bios', '17'),
    'message.adp': ('bios', '17'),        # a message pops up
    'disc.adp': ('bios', '17'),           # a disc read after the tray closes
    'launch.adp': ('system', 'Game Boot'),  # a game or disc starting, as the towers light (OPL's own PS2 logo can be off)
    'bd_connect.adp': ('bios', '13'),     # a drive plugged in: the confirm sound
    'bd_disconnect.adp': ('bios', '13'),  # a drive removed
}


def find(folder, key, album):
    if folder is None:
        return None
    if album == 'bios':
        hits = [p for p in glob.glob(os.path.join(folder, '*'))
                if os.path.splitext(os.path.basename(p))[0].split()[0].strip('.').zfill(2) == key]
    else:
        hits = [p for p in glob.glob(os.path.join(folder, '*')) if key.lower() in os.path.basename(p).lower()]
    return sorted(hits)[0] if hits else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--bios', help='folder of the BIOS system sounds (01.mp3 ... 17.mp3)')
    ap.add_argument('--system', help='folder of the PS2 system music ("04. Game Boot.flac")')
    ap.add_argument('--ps3', help='folder of the PS3 system sounds ("10 - SND System Ng.flac")')
    ap.add_argument('--out', default='SOUND')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    folders = {'bios': a.bios, 'system': a.system, 'ps3': a.ps3}
    made = 0
    for event, (album, key) in MAP.items():
        src = find(folders[album], key, album)
        if src is None:
            print('skip %-18s (no %s track %s found)' % (event, album, key))
            continue
        samples = make_adp.decode_input(src, True, 0.0)
        data = make_adp.encode(samples)
        open(os.path.join(a.out, event), 'wb').write(data)
        print('%-18s <- %s  (%.2f s)' % (event, os.path.basename(src), len(samples) / make_adp.RATE))
        made += 1
    print('%d sounds in %s: copy the folder beside RIPPS2.ELF as SOUND' % (made, a.out))


if __name__ == '__main__':
    main()
