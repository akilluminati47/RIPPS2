"""Build 86: the CARD MANAGER (Square on a memory card in Memory Files, CARD MANAGER on a card image) and
Neutrino's automatic -logo sent first.

Static checks on the patched tree."""
import os
import re
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8')
card, files, sysc, mk = rd('src/ripps2card.c'), rd('src/ripps2files.c'), rd('src/system.c'), rd('Makefile')
fail = []

if 'ripps2card.o' not in mk:
    fail.append('ripps2card.c must be built')
for what in ('ripps2CardManager(fbCardSlot(&fbList[fbCursor]), NULL)', 'ripps2CardManager(-1, from)', '"CARD MANAGER"'):
    if what not in files:
        fail.append('Memory Files must open the CARD MANAGER: %s' % what)
# destructive steps: two screens, the last one START only; never format the card RIPPS2 runs from
if card.count('cmLastCheck(') < 4:
    fail.append('DELETE, ERASE and FORMAT must each end on a START-only last check')
if 'cmBootedHere()' not in card or 'RIPPS2 WAS STARTED FROM THIS CARD' not in card:
    fail.append('FORMAT must refuse the card RIPPS2 was started from')
if 'VMC_card_slot = -1' not in card or 'RIPPS2_SAVE_FOLDER, from, cmSaves[i].name, RIPPS2_SAVE_VMC, path' not in card:
    fail.append('BACK UP must make a blank image and copy every folder in')
if 'ripps2SaveCopy(RIPPS2_SAVE_VMC, cmImage' not in card:
    fail.append('WRITE must copy a card image\'s saves with the save tools')
if 'cmIsSystem' not in card or '"BOOT"' not in card:
    fail.append('ERASE must keep the folders that are not game saves')

# Neutrino: the automatic -logo right after neutrino.elf
body = sysc[sysc.index('static int sysRunNeutrinoLaunch('):]
i_path = body.find('argv[argc++] = (char *)neutrinoPath;')
i_logo = body.find('argv[argc++] = "-logo";')
i_bsd = body.find('argv[argc++] = bsd;')
if not (0 <= i_path < i_logo < i_bsd):
    fail.append('the automatic -logo must come right after neutrino.elf, before -bsd')
if body.count('argv[argc++] = "-logo";') != 1:
    fail.append('exactly one automatic -logo')

print('\n'.join(fail) or 'build86: CARD MANAGER wired, safe and complete; Neutrino -logo first OK')
sys.exit(1 if fail else 0)
