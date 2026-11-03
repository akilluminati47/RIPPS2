"""Build 138: BIBLE's bind runs in an IOP session of its own (only the memory card and pad drivers, as KELFBinder has it:
the user's SD2PSX did not log in after the old restart, which brought MMCE and every drive back), then the IOP as usual
again; the MMCE and MX4SIO BIBLE builds are BIBLE a1ffb0b's, which reach the splash (f31c8d5's hung at power on).

Static checks on the patched tree and elf/bible."""
import hashlib
import os
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
elf = Path(__file__).resolve().parents[1]
rd = lambda p: (root / p).read_text(encoding='utf-8')
opl, boot, hdr = rd('src/opl.c'), rd('src/ripps2boot.c'), rd('include/ripps2.h')
fail = []

a = opl.find('int ripps2RebootIopForBind(const void *ioprp, int size)')
b = opl.find('void ripps2RebootIopAfterBind(void)')
if a < 0 or b < 0:
    fail.append('opl.c has the bind session: ripps2RebootIopForBind and ripps2RebootIopAfterBind')
else:
    forbind = opl[a:b]
    after = opl[b:opl.find('\n}', b)]
    rebooted = forbind[forbind.find('sysSetRebootImage(ioprp, size);'):]  # (a busy menu unblocks and leaves before it)
    if 'initAllSupport(1)' in forbind or 'audioInit' in forbind or 'ioBlockOps(0)' in rebooted:
        fail.append('the bind session brings back no drive, no sound, and keeps requests blocked')
    if 'sysSetRebootImage(ioprp, size);' not in forbind or 'startPads()' not in forbind:
        fail.append('the bind session reboots from the IOPRP image and has the pads')
    for want in ('reset();', 'ioBlockOps(0);', 'initAllSupport(1);', 'audioInit();'):
        if want not in after:
            fail.append('after the bind the IOP is as usual again (%s)' % want)
if 'int ripps2RebootIopForBind(const void *ioprp, int size);' not in hdr:
    fail.append('ripps2.h declares the bind session')

i = boot.find('static void blInstallOn(int port, const blWhere_t *w, const char *alt)')
on = boot[i:boot.find('\n}', i)]
if 'ripps2RebootIopForBind(img, imgSize)' not in on or 'blInstallBound(port, w, alt);' not in on or 'ripps2RebootIopAfterBind();' not in on \
        or 'ripps2DiagBeforeLaunch();' not in on or on.find('blInstallBound(port') > on.find('ripps2RebootIopAfterBind()'):
    fail.append('blInstallOn: the bind session, the install inside it, then the IOP back and DIAG.TXT written')
if 'ripps2RebootIopWith(img' in boot:
    fail.append('BIBLE no longer uses the restart that brings every drive back')
j = boot.find('static void blInstallBound(')
bound = boot[j:boot.find('SecrInit();', j)]
if 'l1 = blCardInfo(port, NULL), l2 = blCardInfo(port, NULL)' not in bound or 'card login after the restart' not in bound:
    fail.append('the card logs in twice before the bind, and DIAG.TXT says how')

sums = {'MMCE/SYSTEM.XLF': 'cacf865b196d4ee91e322152ae0d76107b56112c3e226c1c1918703641e269bb',
        'MX4SIO/SYSTEM.XLF': 'c961a8ff2b666b36aae246f9f6cfac5ebd26161dbdfd90eb04cb83a18ffba018'}
readme = (elf / 'bible' / 'README.md').read_text(encoding='utf-8')
for name, want in sums.items():
    if hashlib.sha256((elf / 'bible' / name).read_bytes()).hexdigest() != want:
        fail.append('elf/bible/%s is BIBLE a1ffb0b, signed 11/03' % name)
    if want not in readme:
        fail.append('elf/bible/README.md lists %s\'s SHA-256' % name)

print('\n'.join(fail) or 'build138: the bind in a session of its own, the IOP back after it, BIBLE a1ffb0b carried OK')
sys.exit(1 if fail else 0)
