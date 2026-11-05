#!/usr/bin/env python3
"""Build 144: the user's first console run of 143 (11/05).

Pins what the lab cannot show by itself: an IOP restart leaves All Games its saved rows and the file its drives, an MMCE roll is
written out, and the rows and pickers the user asked for.
"""
import os
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
fail = []


def src(name):
    return (root / name).read_text(encoding='utf-8')


def body(text, head):
    start = text.index(head + '\n{') if head + '\n{' in text else text.index(head + '\r\n{')
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ValueError(head)


mix = src('src/mixsupport.c')
if 'sbSnapForget(&mmceSnap)' not in body(src('src/mmcesupport.c'), 'void mmceInit(item_list_t *itemList)'):
    fail.append('mmceInit forgets the trusted list it just emptied')
reset = body(mix, 'void mixIopWasReset(void)')
if 'mixAnswered' not in reset or 'mixWaitSince' not in reset:
    fail.append('an IOP restart: every source answers again')
if 'mixIopWasReset();' not in body(src('src/opl.c'), 'static void reset(void)'):
    fail.append('reset() tells All Games')
save = body(mix, 'static void mixMasterSave(const mix_rec_t *arr, int count)')
if 'mixDropped[mixMaster[i].family]' not in save:
    fail.append('the list on file keeps a drive that has not answered')
if 'strcmp(path, mixMasterSavedPath)' not in save:
    fail.append('the list follows the settings to a new home')
if 'mixDropped[m->family] = 1' not in body(mix, 'static int mixBuildRows(item_list_t *itemList, mix_rec_t **out, int save)'):
    fail.append('a pass marks the drives it left off the page')

shot = body(src('src/ripps2shot.c'), 'static int rsMake(const char *root, const char *path)')
mmce = shot[shot.index('strncmp(root, "mmce", 4)'):]
mmce = mmce[:mmce.index('} else {')]
if 'write(fd, rsPiece, RS_PIECE)' not in mmce or 'lseek' in mmce:
    fail.append('an MMCE roll is written out, with no seek past the end')
igr = src('ee_core/src/igrmenu.c')
if '"DRIVE FULL"' in igr or 'NO ROLL' not in igr:
    fail.append('the in-game menu does not claim a full drive it never measured')

dia = src('src/dia.c')
run = dia[dia.index('int diaExecuteDialog(struct UIItem *ui'):]
if 'guiMsgBoxStartOption(_t("KEEP EDITING"))' not in run or 'guiMsgBoxBackLabel(_t("DISCARD"))' not in run:
    fail.append('Back on a changed page asks')
if 'diaHasOkButton(ui)' not in run:
    fail.append('it asks only on a page with an OK')
if 'ripps2ColorPick(' not in dia:
    fail.append('colour rows open the picker')

boot = src('src/ripps2boot.c')
sets = boot[boot.index('static const blSet_t blSets[]'):boot.index('#define BL_SETS')]
if 'OSDHISTORY_READ' in sets:
    fail.append('Read Console History is gone from Manage')
menu = body(boot, 'static void blBibleMenu(int boot, int removed)')
if menu.index('kind[n] = BLR_LOCK') > menu.index('kind[n] = BLR_KEYS'):
    fail.append('BOOT LOCK comes before Launch Keys')
if not sets.rstrip().rstrip('};').rstrip().endswith('0},') or '"BIBLE_WIDESCREEN"' not in sets.splitlines()[-2]:
    fail.append('Widescreen is the last row before BOOT LOCK')
if 'ripps2ColorPick(_t("Sky Color")' not in menu:
    fail.append('Sky Color opens the picker')
if 'char items[2][160], what[96]' not in boot:
    fail.append('the card line is not cut before the box can fit it')

gui = src('src/gui.c')
for head in ('guiBootLockEnd(diaConfig);    // build 144', 'guiBootLockEnd(ui);              // build 144'):
    if head not in gui:
        fail.append('a change on the page is applied before Manage opens: ' + head)

edit = src('src/ripps2edit.c')
if 'edMenuBreak(_t(items[i])' not in edit or 'ED_MENU_FONT   RIPPS2_MSG_FONT' not in edit:
    fail.append('pickers wrap, in Roboto')

card = src('src/ripps2card.c')
if '"KEPT BY ERASE"' in card or 'cmDrawTip(cursor, top)' not in card:
    fail.append('the card manager has a tip per item')

files = src('src/ripps2files.c')
if 'fbTipFromList(e)' not in files:
    fail.append('a card image answers details from its list')
if 'ripps2ViewSaveIconInVmc(fbVmc, save, e->name)' not in files:
    fail.append('an icon in a card image opens')
if 'fntRenderString(uiFont, FB_X, 30, ALIGN_VCENTER, 0, 0, fbPath[0]' in files:
    fail.append('the path rolls instead of running on')

menus = src('src/menusys.c')
if '_STR_PADMACROCONFIG' in menus or 'guiGameShowControllers(padId' not in menus:
    fail.append('a game has one Controller Settings row')
if 'GAME_PADEMU_SETTINGS, _STR_CONTROLLER_SETTINGS' not in menus:
    fail.append('its name')
if 'PADS/GAMES/%s.pad' not in gui or 'padMapParse(text, n, map' not in gui:
    fail.append('the button map reads and writes the file the launcher hands PADEMU')

if fail:
    print('\n'.join('FAIL: ' + f for f in fail))
    sys.exit(1)
print('build 144: ok')
