"""Build 139: BIBLE 3282396 carried (all four builds, signed by akilluminati47 on 11/03); Manage opens a BIBLE menu with
BIBLE's settings, each written in place in its settings file; the boot sound BIBLE hands over in RAM
(-bible-bootsnd=mem:A:S:C, BIBLE's docs/boot-sound-handoff.md) is taken first thing in main, and On (fast) keeps its copy
beside BIBLE's settings (-bible-home=); About credits KELFBinder's image and the user's signing.

Static checks on the patched tree and elf/bible."""
import hashlib
import os
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
elf = Path(__file__).resolve().parents[1]
rd = lambda p: (root / p).read_text(encoding='utf-8')
opl, boot, snd, gui = rd('src/opl.c'), rd('src/ripps2boot.c'), rd('src/sound.c'), rd('src/gui.c')
st, about = rd('src/ripps2status.c'), rd('src/ripps2about.c')
fail = []

# BIBLE 3282396, all four builds
sums = {'SYSTEM.XLF': 'f56c950f753c78b862ce5c0a6d3578e9850e1eefc1285d4a3ef560f27c457a8a',
        'MX4SIO/SYSTEM.XLF': '9f11f1d461e668d1a35179340b332aa446aa188932596618201dd750770f47f2',
        'MMCE/SYSTEM.XLF': 'cbcff26cf6900df479e43eb66a601294ba75029486d967c292687562d7bacf05',
        'HSYSTEM.XLF': '0f8f2a7ca76d4f3392636b0a1263b62d9a155285cce40b3226ab7926af5cf2b8'}
readme = (elf / 'bible' / 'README.md').read_text(encoding='utf-8')
for name, want in sums.items():
    data = (elf / 'bible' / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != want:
        fail.append('elf/bible/%s is BIBLE 3282396, signed 11/03' % name)
    if want not in readme:
        fail.append('elf/bible/README.md lists %s\'s SHA-256' % name)
if '3282396' not in readme or "KELFBinder's IOPRP image for that step" not in readme:
    fail.append('elf/bible/README.md names the commit and the bind\'s image')

# the hand-off: first thing in main, checked, taken by the boot
m = opl.find('int main(int argc, char *argv[])')
if m < 0 or opl.find('ripps2BibleArgs(argc, argv);', m) > opl.find('LOG_INIT();', m):
    fail.append('main reads BIBLE\'s arguments before anything else')
a = snd.find('void ripps2BibleArgs(int argc, char *argv[])')
args = snd[a:snd.find('\n}\n', a)]
for want in ('"-bible-home="', '"-bible-bootsnd=mem:"', 'crc32(0L, (const unsigned char *)addr, size) != crc', 'addr + size > 0x02000000',
             'size > SFX_MAX_BYTES', 'sfxHeaderMs((const unsigned char *)addr', 'memalign(64, size)', '"mc0:/"'):
    if want not in args:
        fail.append('ripps2BibleArgs checks %s' % want)
w = snd.find('static void sfxBootEarlyWork(void)')
work = snd[w:snd.find('\n}\n', w)]
if 'sfx_files[SFX_BOOT].buffer = sfxBibleSnd;' not in work or 'gBibleSoundHanded = 1;' not in work or 'BIBLE handed the boot sound over in RAM' not in work:
    fail.append('the boot plays the sound BIBLE handed over, and DIAG.TXT says so')
if work.find('sfxBibleSnd != NULL') > work.find('gEnableBootSND == 2 && sfxCardBootPath'):
    fail.append('the RAM copy comes before the card is read')
c = snd.find('int sfxCardBootPath(char *out, int size)')
if 'if (gBibleHome[0])' not in snd[c:c + 400]:
    fail.append('On (fast) keeps its copy beside BIBLE\'s settings when BIBLE started RIPPS2')
if 'sfxBibleCopyDrop();' not in gui or 'gEnableBootSND != 2' not in snd[snd.find('void sfxBibleCopyDrop(void)'):][:300]:
    fail.append('Boot Sound Off or On drops the copy BIBLE reads')
if '_t("Boot sound On (fast): %s, handed over by BIBLE")' not in st:
    fail.append('STATUS says the boot sound came from BIBLE')

# the BIBLE menu
for want in ('"BIBLE_BACKGROUND", N_("Background"), 3, {"AUTO", "SKY", "BLANK"}', '"LOGO_DISPLAY"', '"BIBLE_GLYPHS"', '"BIBLE_INFO"',
             '"KEY_READ_WAIT_TIME"', '"VIDEO_MODE"', '"BIBLE_WIDESCREEN"', 'static int blIniSet(const char *path, const char *key, const char *value)',
             '_t("UPDATE BIBLE: SLOT %d HAS AN OLDER ONE")', '_t("SET UP, UPDATE OR RESTORE BIBLE")', 'ripps2EditFile(blSetPath);',
             'snprintf(blSetPath, sizeof(blSetPath), "%sPS2BBL.INI", gBibleHome)'):
    if want not in boot:
        fail.append('the BIBLE menu has %s' % want)
mg = boot.find('void ripps2BibleManage(void)')
if 'blBibleMenu(boot, removed);' not in boot[mg:mg + 700] or 'blManageCards(boot, removed);' not in boot[mg:mg + 700]:
    fail.append('Manage opens the BIBLE menu when a card has BIBLE, the card summary otherwise')
s = boot.find('static int blIniSet(')
iniset = boot[s:boot.find('\n}\n', s)]
if 'memcpy(blOut + o, p, len);' not in iniset or 'blWrite(path, blOut, o) == 0' not in iniset:
    fail.append('a setting changes only its own line; the rest of the file is kept')

# the BIBLE builds RIPPS2 carried before are still BIBLE (older), and the menu offers the update
for want in ('{169016, 0x0EEFE882u, "MMCE"}', '{166264, 0xE42D0CA8u, "MX4SIO"}', '{166456, 0xA27798DDu, "MMCE"}', '{163704, 0xB2845BEDu, "MX4SIO"}',
             '{116136, 0x8E1FC367u, "memory card"}', 'crc32(crc32(0L, buf, 40), buf + 72, size - 72)', '"BIBLE (%s build, older)"',
             'blCards[port].bibleBuild == NULL || blCards[port].bibleOld'):
    if want not in boot:
        fail.append('older BIBLE builds are told apart: %s' % want)

# About
if "N_(\"KELFBinder by El Isra\")" not in about or "every build signed by akilluminati47" not in about or "ps2sdk's SECRMAN, from the FMCB installer" in about:
    fail.append('About credits KELFBinder\'s image and akilluminati47\'s signing')

print('\n'.join(fail) or 'build139: BIBLE 3282396 carried, the BIBLE menu, the boot sound hand-off, About OK')
sys.exit(1 if fail else 0)
