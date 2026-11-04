"""Build 140: DISC_STOP in Manage's BIBLE menu (BIBLE's default stops the disc at a launch and waits on the drive), and
DISC_STOP = 0 in the config a fresh install writes; a config already on the card is kept as it is.

Static checks on the patched tree."""
import os
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
boot = (root / 'src/ripps2boot.c').read_text(encoding='utf-8')
fail = []

s = boot.find('static const blSet_t blSets[] = {')
sets = boot[s:boot.find('};', s)]
if '{"DISC_STOP", N_("Stop Disc at Launch"), 2, {"0", "1"}, {N_("Off"), N_("On")}, 1},' not in sets:
    fail.append('the BIBLE menu has DISC_STOP: Off is 0, On is 1, and a file without the key shows On (BIBLE\'s default)')

c = boot.find('static int blBibleConfig(const char *alt, const char *backupKelf)')
conf = boot[c:boot.find('\n}\n', c)]
if 'EJECT_TRAY = 0\\r\\nDISC_STOP = 0\\r\\n' not in conf:
    fail.append('a fresh install writes DISC_STOP = 0')

print('\n'.join(fail) or 'build140: DISC_STOP row and fresh install default OK')
sys.exit(1 if fail else 0)
