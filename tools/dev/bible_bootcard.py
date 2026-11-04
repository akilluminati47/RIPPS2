"""BIBLE's SD2PSX BOOT card: an 8 MB raw memory card image (no ECC, as SD2PSX keeps them) with BIBLE's MMCE build bound to
an SD2PSX card, ready to copy to an SD card. Made from a card a console already bound BIBLE to (KELFBinder, 11/03): the
bound file is copied to every name and region folder the SD2PSX's own PS2BBL BOOT card used, its extras go, and the
settings file BIBLE reads first, SYS-CONF/PS2BBL.INI, is written fresh. No key or binding is made here: a KELF is bound
by a console. SD2PSX firmware answers every card with the same identity (sd2psXtd ps2_mc_auth.c: a fixed IV and key
source), so the bound file starts on other SD2PSX cards too; tested on the user's own SD2PSX and USA PS2 only.

    python bible_bootcard.py <bound card .mcd> <out .mcd>
    python bible_bootcard.py --into <clean BOOT card .mcd> <bound card .mcd> <out .mcd>

--into (11/03 night, BIBLE 3282396): only the bound BIBLE file is taken from the bound card (the user's own card holds
their settings, lists and a boot.adp ripped from their BIOS, none of which may be published); it goes into a clean BOOT
card made before (the published one), in every name and region folder, with the settings file written fresh.
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mcecc  # noqa: E402
from mymcplus import ps2mc  # noqa: E402

P, S = 512, 16
BOUND = '/BAEXEC-SYSTEM/osdmain.elf'  # where KELFBinder bound it on a USA console
NAMES = {  # the names the SD2PSX PS2BBL BOOT card had in each region folder (the 7 KB osdsys/osd110 kernel loaders stay)
    'BAEXEC-SYSTEM': ('osdmain.elf', 'osd120.elf', 'osd130.elf'),
    'BEEXEC-SYSTEM': ('osdmain.elf', 'osd130.elf'),
    'BIEXEC-SYSTEM': ('osdmain.elf', 'osd130.elf'),
    'BCEXEC-SYSTEM': ('osdmain.elf',),
}
GONE_DIRS = ('PS2BBL', 'APPS', 'BOOT')  # KELFBinder's own extras
GONE_FILES = ('/BIEXEC-SYSTEM/xosdmain.elf',)  # the old PS2BBL for the PSX DESR: BIBLE has no PSX build

INI = """# BIBLE settings: mc?:/SYS-CONF/PS2BBL.INI on the BOOT card. BIBLE reads this file first (then PS2BBL/CONFIG.INI
# on a card, USB, MMCE or the HDD). Edit it in RIPPS2's Memory Files, or on a PC with any memory card tool. Lines that
# start with # are notes; every key is optional.
# BIBLE: akilluminati47's boot loader built on PS2BBL by El Isra (GPL-3), github.com/akilluminati47/BIBLE

# Hold a button this long (ms) at power on to pick its entry instead of AUTO
KEY_READ_WAIT_TIME = 1000
# 1: update the PS2's play history like the browser does
OSDHISTORY_READ = 0
# 1: open the disc tray at power on
EJECT_TRAY = 0
# 0 nothing on screen, 2 BIBLE's splash (logo, buttons, text), 3 the splash with each button's NAME_ shown
LOGO_DISPLAY = 2
# Buttons under the logo: 0 none, 1 the four face buttons, 2 all sixteen
BIBLE_GLYPHS = 1
# Behind the logo: AUTO (RIPPS2's sky when BIBLE starts RIPPS2, else black), SKY or BLANK (black)
BIBLE_BACKGROUND = AUTO
# 1: console model, clock and countdown on the splash
BIBLE_INFO = 0
# AUTO (the PS2's own, or RIPPS2's), NTSC, PAL, 480P, 576P, 720P, 1080I
VIDEO_MODE = AUTO
# AUTO (RIPPS2's Widescreen, else the PS2's 16:9 setting), ON or OFF
BIBLE_WIDESCREEN = AUTO
# The sky: top, horizon and floor colours. Unset, BIBLE uses the Color Theme RIPPS2 saved
# BIBLE_COLOR = 0D0000,700400,170000

# What starts with no button held: the first that exists of E1, E2, E3
NAME_AUTO = RIPPS2
LK_AUTO_E1 = mmce?:/APPS/RIPPS2.ELF
LK_AUTO_E2 = mmce?:/RIPPS2/RIPPS2.ELF
LK_AUTO_E3 = $OSDSYS

# Held at power on. $OSDSYS the PS2's browser, $CDVD the disc in the drive, $CREDITS BIBLE's credits.
# Also at power on: L2 + R2 the launch keys page, TRIANGLE + CROSS the video mode page.
NAME_START = Browser
LK_START_E1 = $OSDSYS
NAME_CROSS = Disc
LK_CROSS_E1 = $CDVD
NAME_R1 = OPL
LK_R1_E1 = mmce?:/APPS/OPNPS2LD.ELF
NAME_SQUARE = Credits
LK_SQUARE_E1 = $CREDITS
""".replace('\n', '\r\n').encode('ascii')


def with_ecc(raw):
    return b''.join(raw[o:o + P] + mcecc.spare(raw[o:o + P]) for o in range(0, len(raw), P))


def strip_ecc(img):
    return b''.join(img[o:o + P] for o in range(0, len(img), P + S))


def live(c, d):
    return [(e[8].decode('ascii', 'replace').rstrip('\0'), e[0]) for e in c.dir_open(d)
            if e[0] & 0x8000 and e[8].decode('ascii', 'replace').rstrip('\0') not in ('.', '..')]


def read(c, p):
    f = c.open(p, 'rb')
    d = f.read()
    f.close()
    return d


def write(c, p, data):
    f = c.open(p, 'wb')
    f.write(data)
    f.close()


def rmtree(c, d):
    for n, mode in live(c, d):
        if mode & 0x20:
            rmtree(c, d + '/' + n)
        else:
            c.remove(d + '/' + n)
    c.remove(d)


def main(src, out):
    raw = open(src, 'rb').read()
    assert len(raw) == 8 * 1024 * 1024, len(raw)
    buf = io.BytesIO(with_ecc(raw))
    c = ps2mc.ps2mc(buf)
    kelf = read(c, BOUND)
    assert kelf[16 + 6:16 + 8] == b'\x00\x01' and len(kelf) > 100000, 'not a bound BIBLE KELF'
    for d in GONE_DIRS:
        if d in [n for n, _ in live(c, '/')]:
            rmtree(c, '/' + d)
    for p in GONE_FILES:
        try:
            c.remove(p)
        except Exception:
            pass
    for d, names in NAMES.items():
        have = [n for n, _ in live(c, '/' + d)]
        for n in names:
            if n in have:
                c.remove('/%s/%s' % (d, n))
            write(c, '/%s/%s' % (d, n), kelf)
    if 'PS2BBL.INI' in [n for n, _ in live(c, '/SYS-CONF')]:
        c.remove('/SYS-CONF/PS2BBL.INI')
    write(c, '/SYS-CONF/PS2BBL.INI', INI)
    c.check()
    c.close()
    img = strip_ecc(buf.getvalue())
    c2 = ps2mc.ps2mc(io.BytesIO(with_ecc(img)))
    for d, names in NAMES.items():
        for n in names:
            assert read(c2, '/%s/%s' % (d, n)) == kelf, (d, n)
    assert read(c2, '/SYS-CONF/PS2BBL.INI') == INI
    for d in sorted(n for n, _ in live(c2, '/')):
        print(d + '/', ', '.join('%s %d' % (n, len(read(c2, '/%s/%s' % (d, n)))) for n, m in live(c2, '/' + d) if not m & 0x20))
    print('free', c2.get_free_space() // 1024, 'KB')
    c2.close()
    open(out, 'wb').write(img)
    print('wrote', out)


def into(clean, src, out):
    braw = open(src, 'rb').read()
    assert len(braw) == 8 * 1024 * 1024, len(braw)
    cb = ps2mc.ps2mc(io.BytesIO(with_ecc(braw)))
    kelf = read(cb, BOUND)
    cb.close()
    assert kelf[16 + 6:16 + 8] == b'\x00\x01' and len(kelf) > 100000, 'not a bound BIBLE KELF'
    raw = open(clean, 'rb').read()
    assert len(raw) == 8 * 1024 * 1024, len(raw)
    buf = io.BytesIO(with_ecc(raw))
    c = ps2mc.ps2mc(buf)
    for d, names in NAMES.items():
        have = [n for n, _ in live(c, '/' + d)]
        for n in names:
            if n in have:
                c.remove('/%s/%s' % (d, n))
            write(c, '/%s/%s' % (d, n), kelf)
    if 'PS2BBL.INI' in [n for n, _ in live(c, '/SYS-CONF')]:
        c.remove('/SYS-CONF/PS2BBL.INI')
    write(c, '/SYS-CONF/PS2BBL.INI', INI)
    c.check()
    c.close()
    img = strip_ecc(buf.getvalue())
    c2 = ps2mc.ps2mc(io.BytesIO(with_ecc(img)))
    for d, names in NAMES.items():
        for n in names:
            assert read(c2, '/%s/%s' % (d, n)) == kelf, (d, n)
    assert read(c2, '/SYS-CONF/PS2BBL.INI') == INI
    for d in sorted(n for n, _ in live(c2, '/')):
        print(d + '/', ', '.join('%s %d' % (n, len(read(c2, '/%s/%s' % (d, n)))) for n, m in live(c2, '/' + d) if not m & 0x20))
    print('free', c2.get_free_space() // 1024, 'KB')
    c2.close()
    open(out, 'wb').write(img)
    print('wrote', out)


if __name__ == '__main__':
    if sys.argv[1] == '--into':
        into(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        main(sys.argv[1], sys.argv[2])
