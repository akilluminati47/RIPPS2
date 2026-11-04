"""Build 140: DISC_STOP in Manage's BIBLE menu (BIBLE's default stops the disc at a launch and waits on the drive), and
DISC_STOP = 0 in the config a fresh install writes; a config already on the card is kept as it is. DIAG.TXT says where the
boot sound's time goes, the IO worker sends the sound as soon as audio is up, the sounds line never ends on a blank "from", and STATUS's hand-off row names the file alone.

Static checks on the patched tree."""
import os
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
boot = (root / 'src/ripps2boot.c').read_text(encoding='utf-8')
snd = (root / 'src/sound.c').read_text(encoding='utf-8')
st = (root / 'src/ripps2status.c').read_text(encoding='utf-8')
fail = []

s = boot.find('static const blSet_t blSets[] = {')
sets = boot[s:boot.find('};', s)]
if '{"DISC_STOP", N_("Stop Disc at Launch"), 2, {"0", "1"}, {N_("Off"), N_("On")}, 1},' not in sets:
    fail.append('the BIBLE menu has DISC_STOP: Off is 0, On is 1, and a file without the key shows On (BIBLE\'s default)')

c = boot.find('static int blBibleConfig(const char *alt, const char *backupKelf)')
conf = boot[c:boot.find('\n}\n', c)]
if 'EJECT_TRAY = 0\\r\\nDISC_STOP = 0\\r\\n' not in conf:
    fail.append('a fresh install writes DISC_STOP = 0')


def body(name):
    a = snd.find(name)
    return snd[a:snd.find('\n}\n', a)]


for fn, want in (('void sfxIntroStarted(void)', '"the towers are up"'),
                 ('static void sfxBootPlay(void)', '"boot: the boot sound plays"'),
                 ('static void sfxBootEarlyUpload(void)', '"boot: the boot sound goes to the sound chip (%d bytes)"'),
                 ('static void sfxBootEarlyUpload(void)', '"boot: the boot sound is in the sound chip, %d ms to send"'),
                 ('static void sfxBootEarlyWork(void)', '"boot: the boot sound is in RAM%s"'),
                 ('void sfxBootStart(void)', '"boot: audio starts"'),
                 ('void sfxBootStart(void)', '"boot: audio is up%s"')):
    if want not in body(fn):
        fail.append('%s logs %s' % (fn, want))

early = body('static void sfxBootEarlyWork(void)')
w, u = early.find('while (!sfxAudioUp && !sfxAudioFailed'), early.find('sfxBootEarlyUpload();')
if w < 0 or u < w or '(long)(clock() - until) < 0' not in early or 'DelayThread(2000);' not in early:
    fail.append('the IO worker sends the boot sound itself once audio is up, with a time limit, before any drive job')
if 'sfxAudioFailed = 1;' not in body('void sfxBootStart(void)'):
    fail.append('no audio ends the wait at once')

if 'audioSfx ? audio_path : "", themeSfx' in snd or '"BIBLE\'s copy in RAM"' not in snd or '"nowhere, no sound files found"' not in snd:
    fail.append('the sounds line always says where they came from')

if 'name != NULL ? name + 1 : card' not in st:
    fail.append('STATUS\'s hand-off row names the file alone')

print('\n'.join(fail) or 'build140: DISC_STOP, the boot sound sent as audio comes up, its timing lines, the sounds line and the STATUS row OK')
sys.exit(1 if fail else 0)
