"""Build 119 (the user, 10/27): the sidebar out of sight on the info page of every theme, Left bringing it out, Circle or
Right putting it away with the page staying, Up / Down stepping the games (info_sidebar=1 keeps it drawn); the ART Pack's flow as the other long jobs have it: the
sizes, the time it should take, RIPPS2's numbered progress bar, and only the drives it fits on; those panels in RIPPS2's
Roboto on every theme.

Static checks on the patched tree."""
import os
import sys
from pathlib import Path
from r2src import unwrap  # noqa: E402

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: unwrap((root / p).read_text(encoding='utf-8').replace('\r\n', '\n'))
fail = []


def need(text, items, where):
    for s, why in items:
        if s not in text:
            fail.append('%s: %s' % (where, why))


def body(text, head):
    i = text.index(head)
    return text[i:text.index('\n}\n', i) + 3]


# ---- the info page
th = rd('src/themes.c')
need(th, (('newT->infoSidebar = configGetInt(themeConfig, "info_sidebar", &intValue) && intValue == 1;',
           'info_sidebar, off unless a theme asks for it'),), 'themes.c')
for cfg in ('misc/theme_ripgrid.cfg', 'misc/theme_coverflow.cfg', 'misc/conf_theme_OPL.cfg'):
    if 'info_sidebar=1' in rd(cfg):
        fail.append('%s: no built-in theme keeps the sidebar on its info page' % cfg)
menu = rd('src/menusys.c')
need(menu, (('return menuInfoSidebarReach() && gTheme != NULL && gTheme->infoSidebar;', 'drawn all the time only with info_sidebar=1'),
            ('return ripps2SidebarOn() && !ripps2Legacy();', 'brought out on every theme with the sidebar on')), 'menusys.c')
info = body(menu, 'void menuRenderInfo(void)')
if 'if (menuInfoSidebar() || (menuInfoSidebarReach() && ripps2SidebarFocused()))\n        ripps2SidebarRender();' not in info:
    fail.append('menuRenderInfo: the sidebar out of sight on the info page until it is brought out')
inp = body(menu, 'void menuHandleInputInfo()')
if 'if (menuInfoSidebarReach()) {' not in inp or 'ripps2SidebarOpen(0);' not in inp or 'ripps2SidebarInput();' not in inp:
    fail.append('menuHandleInputInfo: Left brings it out, its own Circle and Right put it away (the page stays)')
if 'if (menuInfoSidebar() &&' not in rd('src/gui.c'):
    fail.append('gui.c: the sidebar stays through the page morph only when the info page keeps it')

# ---- the ART Pack's flow
ap = rd('src/ripps2artpack.c')
need(ap, (('apSrc[s].bytes += st.st_size;', 'each picture sized as it is listed'),
          ('if (apSrc[i].freeBytes < need || (vol.fsType != RIPPS2_FS_EXFAT && need > 0xFFFFFFFFLL))', 'only where it fits (FAT: under 4 GB)'),
          ('if (apSrc[i].fits)\n                order[n++] = i;', 'drives it does not fit on are not offered'),
          ('No started drive has room for the ART Pack: it needs about %s.', 'and says so when none has room'),
          ('ripps2AskHold("ART PACK", pack, info, when,', "the long jobs' panel, SELECT held"),
          ('"Pictures: %d (%s). ART folders: %d."', 'the sizes on it'),
          ('return (int)(s + (double)apTotal / 1024.0 / apWriteKbs(apSrc[target].root) + 0.5);', 'how long: read as measured, written as the drive takes'),
          ('ripps2DrawProgress("PACKING THE ART", pack, done, apTotal, left, 1);', "RIPPS2's numbered progress bar"),
          ('snprintf(left, sizeof(left), "PICTURE %d OF %d", n, total);', 'which picture of how many'),
          ('"Stop? The unfinished pack is removed; the ART folders stay as they are."', 'the back key asks before it stops')), 'ripps2artpack.c')
gm = rd('src/ripps2games.c')
ask, bar = body(gm, 'int ripps2AskHold('), body(gm, 'void ripps2DrawProgress(')
if 'gTheme->fonts[' in ask or 'gTheme->fonts[' in bar:
    fail.append("ripps2games.c: the long jobs' panel and bar in RIPPS2's Roboto, not the theme's display face")
need(gm, (('int ripps2AskHold(const char *head, const char *name, const char *info, const char *when, const char *note)', 'the panel shared'),
          ('return ripps2AskHold(head, name, info, when, "Experimental: OPL core only (not Neutrino)");', 'ZSO keeps its note'),
          ('void ripps2SizeText(long long bytes, char *out, int size)', 'the sizes shared')), 'ripps2games.c')

# ---- EXIT: the browser unless the reset can load the IGR Path, never RIPPS2 itself (no black screen)
boot = rd('src/ripps2boot.c')
loadable = body(boot, 'static int exitLoadable(void)')
for s, why in (('strncmp(gExitPath, "mc0:", 4) && strncmp(gExitPath, "mc1:", 4) && strncmp(gExitPath, "mass:", 5)',
                'only a memory card or USB path survives the reset'),
               ('exitStale', 'a card file that is not there goes to the browser'),
               ('!(ripps2BootLockIgrPath(own, sizeof(own)) && !strcasecmp(gExitPath, own))', 'and RIPPS2 itself never loads straight after a game')):
    if s not in loadable:
        fail.append('exitLoadable: ' + why)
exitp = body(boot, 'const char *ripps2ExitPath(char *buf, int size)')
if 'exitLoadable() ? gExitPath : "Browser"' not in exitp or 'ripps2BootLockIgrPath' in exitp:
    fail.append('ripps2ExitPath: an empty IGR Path is the browser (the boot loader), not RIPPS2 loaded straight after the game')
if 'ripps2ExitPathIgnored()' not in rd('src/ripps2status.c'):
    fail.append('ripps2status.c: STATUS says when an IGR Path is passed over')

# ---- the memory card icon (a v1.60 browser called the three-shape hat corrupted data)
opl = rd('src/opl.c')
home = body(opl, 'static int ripps2CardSettingsHome(')
if 'ripps2CardFolderIcon(out); // build 119' not in home or 'rmdir(out);' not in home:
    fail.append('ripps2CardSettingsHome: the hat made whole when the settings load from a card; no bare folder left when it does not fit')
if 'ripps2CardFolderIcon(fbHome);' not in opl:
    fail.append("opl.c: Fast Boot's card home gets its hat made whole too")
if 'l1 = blSjis(first, sys + 0xC0, 66);' not in boot:
    fail.append('blIconSysNamed: titles in Shift-JIS (a v1.60 browser shows ASCII as nothing)')

# ---- no text past its box: the chooser's items, the progress bar's lines, the hold panel's head
if 'fntRenderStringFit(ED_MENU_FONT, x + 16, ry + 11 + l * ED_MENU_LINE_H, ALIGN_VCENTER, w - 32, part' not in rd('src/ripps2edit.c'):  # build 144: a row wraps
    fail.append("ripps2edit.c: the chooser's items kept inside its box")
if 'fntRenderString(' in bar:
    fail.append('ripps2DrawProgress: every line fitted to the panel')
if 'fntRenderStringFit(RIPPS2_NOTE_FONT, 320, y + 26, ALIGN_CENTER, w - 40, head' not in ask:
    fail.append("ripps2AskHold: the head fitted to the panel too")

# ---- 16:9: a game's pictures cropped, its covers and logos kept in shape (no stretched art in 1080i)
th2 = rd('src/themes.c')
need(th2, (('elem->wideCrop = -1;', 'widecrop unset means on its own'),
           ('return s != NULL && (!strncasecmp(s, "BG", 2) || !strncasecmp(s, "SCR", 3));', "a game's pictures: its BG and screenshots"),
           ('} else if (gWideScreen && thmArtWideCrop(drawElem, gameImage))', 'the middle 3/4 of a picture in 16:9, on every theme'),
           ('int w = drawElem->width * 3 / 4, x = drawElem->posX;', 'a cover or logo 3/4 as wide, in the middle of its box'),
           ('gTheme->frostCrop[slot] = thmArtWideCrop(e, mi);', 'the frost cropped as its backdrop is')), 'themes.c')

# ---- the About page: every tester, a line for the ones to come, the music's decoders
about = rd('src/ripps2about.c')
need(about, (('"lukeatmynose - ahavasi - DarkNerdShawny"', 'the newest testers by name'),
             ('"Thanks to everyone testing on Discord and opening issues on GitHub:"', 'and everyone after them'),
             ('"Special thanks to all the YouTube love as well:"', 'the YouTube thanks kept'),
             ('"Ogg Vorbis by Xiph.Org (BSD), minimp3 by lieff (CC0)"', 'the music decoders credited')), 'ripps2about.c')

# ---- the boot sound sent by the IO worker only (v1.1.8 stopped on the towers with a card language and a sound set)
snd = rd('src/sound.c')
start = body(snd, 'void sfxBootStart(void)')
if 'sfxBootEarlyUpload();' in start or 'ioPutRequestFront(IO_CUSTOM_SIMPLEACTION, &sfxBootEarlyUpload)' not in start:
    fail.append('sfxBootStart: the early boot sound goes to the SPU from the IO worker, never the main thread')

# ---- Music off keeps only the menu music away: the media player's tracks and the file CD player still play
need(snd, (("return gEnableBGM || bgmPcmExternal != NULL || bgmOverride[0] != '\\0';", "a track of the user's own plays with Music off"),
           ('if (terminateFlag || !bgmStreamAllowed())', 'the decoder goes on for it'),
           ('} while (!terminateFlag && bgmStreamAllowed() && !bgmPcmEnded);', 'and keeps going')), 'sound.c')
if '(!gEnableBGM && bgmPcmExternal == NULL)' in snd:
    fail.append('sound.c: no stream gate left that only the disc CD player passes')

# ---- BIBLE's sky: the theme's Storage sky saved with the settings, for BIBLE to read
ui = rd('src/ripps2ui.c')
need(ui, (('void ripps2BibleSky(char *out, size_t size)', "the theme's sky as BIBLE_COLOR text"),
          ('static const unsigned char sky[3][3] = {{0x01, 0x02, 0x09}, {0x0B, 0x19, 0x4C}, {0x02, 0x04, 0x10}};', 'the Storage sky at rest'),
          ('tintSolve(sw.c[0], &hue, &sat, &lift);', "a Color Sweep's first colour"),
          ('configSetStr(config, "ripps2_bible_sky", line);', 'saved with the settings')), 'ripps2ui.c')

# ---- Source Name: Pop In and Name, the big name as the source changes and the name over the games too
need(rd('include/ripps2.h'), (('enum { RIPPS2_SRC_POP = RIPPS2_SHOW_COUNT, RIPPS2_SRC_POPNAME, RIPPS2_SRC_COUNT };', 'a fifth Source Name'),), 'ripps2.h')
need(th2, (('if (ripps2SourceNameMode() == RIPPS2_SRC_POPNAME) // build 119: the big name as the source changes, and the line too', 'it pops the name in'),
           ('newT->srcNamePop = !strcmp(srcName, "pop") ? 1 : !strcmp(srcName, "pop_name") ? 2 : 0;', 'source_name=pop_name')), 'themes.c')
need(ui, (('return mode >= RIPPS2_SRC_POP ? 1.0f : showAlpha(mode);', 'and keeps the line drawn'),), 'ripps2ui.c')
need(rd('src/gui.c'), (('"Pop In", "Pop In and Name", NULL};', 'its name in the list'),), 'gui.c')
if 'source_name=shown' not in rd('misc/theme_coverflow.cfg'):
    fail.append("theme_coverflow.cfg: RIPFLOW's Source Name is the name (Shown)")

if fail:
    print('\n'.join(fail))
    sys.exit(1)
print("build119: the sidebar on the info page; the ART Pack sized, timed, numbered and offered where it fits; the card icon whole; EXIT never black; no text past its box; the testers; the boot sound on the IO worker; tracks with Music off; BIBLE's sky saved; Pop In and Name OK")
