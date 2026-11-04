"""Build 102: the user's notes after v1.0.1-beta (10/17/2026). Static checks on the patched tree."""
import os
import re
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8').replace('\r\n', '\n')
fail = []


def body(src, name):  # a function's definition (its name, then its brace on the next line); '' when it is not there
    i = src.find(name + '\n{')
    return src[i:src.index('\n}\n', i)] if i >= 0 else ''


def cfg_blocks(text):  # {block name: {key: value}} and the global keys under ''
    out, cur = {'': {}}, ''
    for line in text.split('\n'):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if not line.startswith('\t') and line.endswith(':'):
            cur = line[:-1]
            out[cur] = {}
        elif '=' in line:
            k, _, v = line.strip().partition('=')
            out[cur][k] = v
    return out


# 1. the music never lets audsrv run dry (its ring loops: the beeping), and a stop never waits long on a stuck read
snd = rd('src/sound.c')
thread, stop, start = body(snd, 'static void bgmThread(void *arg)'), body(snd, 'void bgmStop(void)'), body(snd, 'static void bgmStartInner(void)')
if 'PollSema(outSema) < 0' not in thread or 'bgmFeedSilence();' not in thread or 'WaitSema(outSema);' in thread:
    fail.append('the playback thread must poll for a chunk and feed silence while none is ready')
if 'audsrv_queued()' not in body(snd, 'static void bgmFeedSilence(void)'):
    fail.append('the silence feed must measure what audsrv still has queued')
if 'gBgmInRead ? BGM_STOP_READ_SLICES : BGM_STOP_WAIT_SLICES' not in stop or 'bgmAbandoned = 1;' not in stop:
    fail.append('bgmStop must give a decoder inside a read only BGM_STOP_READ_SLICES, then leave it to finish')
if 'bgmStartWanted = 1;' not in start or 'bgmDeinit();' not in start[:start.find('bgmStartWanted = 0;')]:
    fail.append('bgmStart must wait for a decoder a stop left behind and clean up after it before a new stream')
if 'bgmStartWaiting();' not in body(snd, 'void bgmBootTick(void)'):
    fail.append('the frame tick must start a stream that waited for the old decoder')

# 2. the boot sound plays with the towers' first frame, not when it loads
init = body(snd, 'int sfxInit(int bootSnd)')
if 'audsrv_ch_play_adpcm(SFX_BOOT_VOICE' in init or 'sfxBootPending = 1;' not in init:
    fail.append('sfxInit must only mark the boot sound ready, never play it')
if 'sfxBootPlay();' not in body(snd, 'void bgmBootTick(void)') or 'if (!sfxBootPending || !sfxIntroOn)' not in snd:
    fail.append('the frame tick must play the boot sound once the intro has begun and the sound is in')
gui = rd('src/gui.c')
if gui.count('sfxIntroStarted();') < 2:
    fail.append('the intro (and a boot without it) must say when the towers begin')

# 3. no info page changes the source: Left / Right / Up / Down are its games on every theme
menu = rd('src/menusys.c')
info = menu[menu.index('void menuHandleInputInfo()'):menu.index('void menuRenderGameMenu()')]
if 'menuDriveStep' in info or 'gTheme->coverflow' in info:
    fail.append('the info page must never step drives, on any theme')
l, r = info.find('getKey(KEY_LEFT)'), info.find('getKey(KEY_RIGHT)')
if l < 0 or r < 0 or 'menuPrevV();' not in info[l:r] or 'menuNextV();' not in info[r:r + 80]:
    fail.append('the info page: Left the previous game, Right the next')

# 4. a game started from Memory Files starts its drive's games first
fb = rd('src/ripps2files.c')
if 'ripps2StartSources();' not in body(fb, 'static item_list_t *fbGameSourceStarted(void)'):
    fail.append("a launch from the file browser must start the drive's games (as All Games' Start does)")
if 'item_list_t *src = fbGameSourceStarted(), view;' not in fb or 'mod = fbGameModuleStarted();' not in fb:
    fail.append('the PS2 and PS1 launches from the file browser must use the started source')

# 5. the Colours page edits every theme's colours (RIPGRID, a disk theme) instead of greying them out
thm, thh = rd('src/themes.c'), rd('include/themes.h')
cols = body(gui, 'void guiShowColorsConfig(void)')
if 'diaSetEnabled(diaColorsConfig, UICFG_BGCOL, editable || own != NULL);' not in cols or 'thmColorsSet(own, c);' not in cols \
        or 'thmColorsClear(own);' not in cols or 'thmSetGuiValue(themeID, 1)' not in cols:
    fail.append("the Colours page must edit, keep and reset a theme's own colours, and reload it with them")
load = body(thm, 'static int thmLoad(const char *themePath)')
i_sel, i_user, i_elem = load.find('"sel_text_color"'), load.find('thmApplyUserColors(newT, thmLoadingColorName);'), load.find('addGUIElem(')
if not (0 <= i_sel < i_user < i_elem):
    fail.append("thmLoad must lay the user's colours over the theme's after its own and before its elements")
if 'thmLoadingColorName = thmColorName(themeID);' not in body(thm, 'int thmSetGuiValue(int themeID, int reload)'):
    fail.append('thmSetGuiValue must name the colours of the theme it loads')
if len('rcol_' + 'x' * 20 + '_plas') > 31:
    fail.append('a colour key must fit CONFIG_KEY_NAME_LEN')

# 6. a reflection fades with its cover; a cover in a case fades even without alpha of its own
rm = rd('src/renderman.c')
refl = body(rm, 'static void rmDrawReflection(GSTEXTURE *txt, rm_quad_t *q, float bottomY, float botV)')
if 'coverA / 0x80' not in refl or 'GS_SETREG_RGBA(0x80, 0x80, 0x80, a)' in refl:
    fail.append("the reflection must take its cover's alpha and colour")
if '((color >> 24) & 0xFF) < 0x80 ? GS_SETTING_ON : GS_SETTING_OFF' not in rm[rm.find('void rmDrawOverlayPixmap'):rm.find('#ifdef RETROACHIEVEMENTS', rm.find('void rmDrawOverlayPixmap'))]:
    fail.append("a case's cover must blend while it fades, whatever its texture")

# 7. glyph sets and sounds: RIPFLOW White, RIPGRID Standard; sounds=audio passes over a theme's sound folder
flow, grid = cfg_blocks(rd('misc/theme_coverflow.cfg')), cfg_blocks(rd('misc/theme_ripgrid.cfg'))
if flow[''].get('glyph_set') != 'white' or grid[''].get('glyph_set') != 'standard':
    fail.append('RIPFLOW takes the White glyph set and RIPGRID the Standard one')
if 'newT->soundsAudio = configGetStr(themeConfig, "sounds", &v)' not in load or 'thmPath != NULL && !gThemeSoundsAudio' not in init:
    fail.append('sounds=audio must keep a theme\'s sound folder out of the load')

# 8. smooth scrolling: the marquee slides by the display pixel through a clipped window, the roll by the pixel
fnt = rd('src/fntsys.c')
if 'FNT_MARQUEE_STEP_MS' in fnt or 'fntClipX0' not in body(fnt, 'static void fntRenderGlyph(fnt_glyph_cache_entry_t *glyph, int pen_x, int pen_y)'):
    fail.append('the marquee must slide through a clipped window, not step a character at a time')
if 'fntSetSubUnit(0.0f, ly - (float)iy);' not in thm:
    fail.append('the description roll must place its lines to the display pixel')

# 9. About and STATUS in RIPPS2's own faces on every theme
for f in ('src/ripps2about.c', 'src/ripps2status.c'):
    t = rd(f)
    if 'gTheme->fonts[' in t or 'RIPPS2_CASE' in t or 'thmPageFontsBegin();' not in t or 'thmPageFontsEnd();' not in t:
        fail.append('%s must draw in the page faces, opened and closed with the page' % f)

# 10. an app's case: PS1 square by default, PS2 or the theme's from its menu, on every cover path
for name in ('static void drawGameImageArt(', 'static void drawCoverFlow(', 'static void drawGridCover('):  # build 108: drawGameImage draws through drawGameImageArt
    i = thm.find(name)
    j = thm.find('\n}\n', i)
    if i < 0 or 'thmAppShapeBox(' not in thm[i:j]:
        fail.append('%s must shape an app\'s case' % name.strip('( '))
if '#define THM_APP_CASE_PS1   0' not in thh or 'APP_CASE_SHAPE' not in menu or 'appCaseLabel' not in menu:
    fail.append("an app's case must default to PS1 square and be set from the app's menu")

# 11. RIPGRID: its pages' slots as RIPFLOW's (CD player, file tree) and RIPPS2's (category pages); its grid raised
g = grid['']
want = {'font3': 'builtin:ripps2', 'font3_size': '13', 'font6': 'builtin:ripps2sleekbold', 'font6_size': '20',
        'font4': 'builtin:ripflowbold', 'font5': 'builtin:ripflow', 'font8': 'builtin:ripflow', 'font11': 'builtin:ripflowbold'}
for k, v in want.items():
    if g.get(k) != v:
        fail.append('RIPGRID %s must be %s (it is %s)' % (k, v, g.get(k)))
for name, keys in grid.items():
    if keys.get('font') in ('3', '4', '5', '6', '8', '11'):
        fail.append('RIPGRID %s draws with font%s, a slot RIPPS2\'s pages own' % (name, keys['font']))
if grid['main2'].get('y') != '80':  # main2 since build 114 dropped the side bar (main2, main3)
    fail.append("RIPGRID's grid stands at 80")
for a, b in (('info12', 'info13'),):  # info12/13 since build 114 dropped the side bar (info2, info3)
    t, u = grid[a], grid[b]
    top, bottom = int(t['y']) - int(t['height']) // 2, int(u['y']) + int(u['height']) // 2
    if top != 160 or bottom != 415:
        fail.append("RIPGRID's screenshots must stand flush with the text's glass (160 to 415)")

# 12. RIPFLOW: the hints in RIPPS2 Sleek Case (font15) as on every other theme, the source name in its own face
# (font7, as before build 102), the badges not over each other
menutext = [k for k in flow if flow[k].get('type') == 'MenuText'][0]
if flow[menutext].get('font') != '7' or flow[''].get('font13') != 'builtin:ripflow':
    fail.append("RIPFLOW's source name keeps its own face (font7)")
if flow[''].get('font15') != 'builtin:ripps2sleekcase' or grid[''].get('font15') != 'builtin:ripps2sleekcase':
    fail.append('the hints (font15) are RIPPS2 Sleek Case on RIPFLOW and RIPGRID alike')
xs = sorted(int(flow['info%d' % n]['x']) for n in range(19, 25))
w = int(flow['info19']['width'])
if any(b - a < w for a, b in zip(xs, xs[1:])):
    fail.append("RIPFLOW's badges must not overlap")

# 13. About wraps its rows to the column, in the faces it draws with, each row's lines as even as they go
about = rd('src/ripps2about.c')
if 'abWrap();' not in about or 'abWidth(font, t + off, n - off) > room' not in about or 'abWrapRow(i, room - 8, 0, 0) == k' not in about \
        or 'i < abLineCount' not in about:
    fail.append("About must wrap its rows to AB_ROOM and draw the wrapped lines")

# 14. logos just above their panels: valign=bottom stands the art's visible foot on its box; elements start clean
if 'iy += (texture->Height - 1 - vb) * ih / texture->Height;' not in thm or 'elem->artBottom = 1;' not in thm:
    fail.append("valign=bottom must stand the art's lowest visible row on its box")
ib = thm.find('theme_element_t *elem = (theme_element_t *)malloc(sizeof(theme_element_t));')
head = thm[ib:thm.find('snprintf(elemProp, sizeof(elemProp), "%s_x", name);', ib)]
for f in ('elem->blur = 0;', 'elem->wideCrop = -1;', 'elem->artBottom = 0;'):
    if f not in head:
        fail.append('a new element must start with %s' % f)
lg = grid['info3']  # info3 since build 114
if lg.get('valign') != 'bottom' or int(lg['y']) + int(lg['height']) // 2 >= 160:
    fail.append("RIPGRID's logo must stand on its box's foot, just above the glass (160)")

if fail:
    print('\n'.join(fail))
    sys.exit(1)
print('build102: music feed and stop, boot sound, info pages, file browser starts, colours, fades, glyphs, sounds, '
      'scrolling, page faces, app cases, RIPGRID and RIPFLOW layouts OK')
