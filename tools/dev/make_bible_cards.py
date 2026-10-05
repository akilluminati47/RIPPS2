"""Two PCSX2 test cards for build 69's BOOT LOADER detection (never the user's Mcd001/Mcd002):

  bible-slot1-fmcb.ps2  an FMCB card: B?EXEC-SYSTEM/osdmain.elf (a dummy), icon.sys titled "Free McBoot",
                        SYS-CONF/FREEMCB.CNF, and the SYS-CONF/PS2BBL.INI build 68 wrote for it
  bible-slot2-bbl.ps2   a KELFBinder PS2BBL card: icon.sys titled PS2BBL(USA), PS2BBL/CONFIG.INI (stock)

The system folders go in for every region (A, E, I, C), whatever BIOS PCSX2 boots.
"""
import os
import subprocess
import sys

OLD = os.path.dirname(os.path.abspath(__file__))  # make_mc_image.py sits beside this script
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'bible-cards')
WORK = os.path.join(OUT, 'work')
ICON_SYS = 'C:/Users/Mini PC/Desktop/Webpages - Projects/RiptOPL/misc/icon.sys'
ICN = 'C:/Users/Mini PC/Desktop/Webpages - Projects/RiptOPL/misc/list.icn'
os.makedirs(WORK, exist_ok=True)


def mc(card, *args):
    r = subprocess.run([sys.executable, '-m', 'mymcplus', card] + list(args), capture_output=True, text=True)
    if r.returncode:
        print('mymcplus', args, r.stdout, r.stderr)
        sys.exit(1)
    return r.stdout


def icon_sys(title, icn):
    d = bytearray(open(ICON_SYS, 'rb').read())
    d[6:8] = (0).to_bytes(2, 'little')
    d[0xC0:0xC0 + 68] = title.encode('ascii').ljust(68, b'\0')
    for o in (0x104, 0x144, 0x184):
        d[o:o + 64] = icn.encode('ascii').ljust(64, b'\0')
    return bytes(d)


def put(name, data):
    p = os.path.join(WORK, name)
    open(p, 'wb').write(data)
    return p


def card(path):
    if os.path.exists(path):
        os.remove(path)
    subprocess.run([sys.executable, os.path.join(OLD, 'make_mc_image.py'), path], check=True)


icn = open(ICN, 'rb').read()
dummy = put('osdmain.elf', b'\x01\x00\x00\x04' + b'\0' * 2044)  # a KELF-looking stand-in: never run here

# slot 1: FMCB, plus build 68's stray PS2BBL.INI
c1 = os.path.join(OUT, 'bible-slot1-fmcb.ps2')
card(c1)
for r in 'AEIC':
    f = 'B%sEXEC-SYSTEM' % r
    mc(c1, 'mkdir', f)
    mc(c1, 'add', '-d', f, dummy, put('icon.sys', icon_sys('Free McBoot', 'FMCB.icn')), put('FMCB.icn', icn))
mc(c1, 'mkdir', 'SYS-CONF')
mc(c1, 'add', '-d', 'SYS-CONF', put('FREEMCB.CNF', b'CNF_version = 1\r\nhacked_OSDSYS = 1\r\n'),
   put('PS2BBL.INI', b"# PS2BBL config, created by RIPPS2's BOOT LOCK\r\nKEY_READ_WAIT_TIME = 500\r\n#RIPPS2 BOOT LOCK: RIPPS2 starts first.\r\nNAME_AUTO = RIPPS2\r\nLK_AUTO_E1 = mass:/RIPPS2.ELF\r\nLK_AUTO_E2 = $OSDSYS\r\n"))

# slot 2: PS2BBL as KELFBinder installs it, with its stock config
c2 = os.path.join(OUT, 'bible-slot2-bbl.ps2')
card(c2)
names = {'A': 'USA', 'E': 'Europe', 'I': 'Japan', 'C': 'China'}
for r in 'AEIC':
    f = 'B%sEXEC-SYSTEM' % r
    mc(c2, 'mkdir', f)
    mc(c2, 'add', '-d', f, dummy, put('icon.sys', icon_sys('PS2BBL(%s)' % names[r], 'PS2BBL.icn')), put('PS2BBL.icn', icn))
mc(c2, 'mkdir', 'PS2BBL')
mc(c2, 'add', '-d', 'PS2BBL', put('CONFIG.INI', b'# PlayStation2 Basic BootLoader config file\r\nSKIP_PS2LOGO = 0\r\nKEY_READ_WAIT_TIME = 4000\r\nOSDHISTORY_READ = 1\r\n\r\nLK_AUTO_E1 = mass:/APPS/OPNPS2LD.ELF\r\nLK_AUTO_E2 = mc?:/APPS/OPNPS2LD.ELF\r\n\r\nLK_START_E1 = rom0:OSDSYS\r\nLK_CROSS_E1 = $CDVD\r\n'))

for c in (c1, c2):
    print(os.path.basename(c))
    print(mc(c, 'ls', '/'))
