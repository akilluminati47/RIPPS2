"""Build 133: RIPGRID's L1 / R1 turn the grid's pages with the sidebar on; the star on Right stands at the row's right
edge and is the default on a theme from a drive (Adapt, a theme made for OPL); a towers=0 theme (Adapt, RIPGRID)
draws Storage's sky where it had a flat bg_color, and the sky's vignette over a list page's game art.

Static checks on the patched tree."""
import os
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8')
menu, themes, bg, hdr = rd('src/menusys.c'), rd('src/themes.c'), rd('src/ripps2bg.c'), rd('include/ripps2.h')
fail = []

if menu.count('if (ripps2PageButtons() != 2 || gridSide)') != 2:
    fail.append('L1 and R1 must turn a grid\'s pages with the sidebar on, Page Buttons on L2 / R2 or not')

if 'itemsList->starSide = themePath != NULL ? THM_STAR_RIGHT : THM_STAR_LEFT;' not in themes:
    fail.append('a theme from a drive defaults the star to the right, the built-in ones to the left')
if 'starSide == THM_STAR_LEFT ? posX : starRightX' not in themes or 'starSide == THM_STAR_RIGHT && roomEnd > starRightX - 6' not in themes:
    fail.append('a right star stands at the row\'s right edge and the titles stop short of it')
if 'textEndX + 4' in themes:
    fail.append('the right star must no longer follow the end of the title')

if 'void ripps2DrawRestSky(void)' not in bg or 'void ripps2DrawSkyVignette(void)' not in bg or 'ripps2DrawSkyVignette(void);' not in hdr:
    fail.append('ripps2bg.c must draw the rest sky and its vignette')
if 'ripps2DrawRestSky(); // build 133' not in themes:
    fail.append('a towers=0 theme draws the sky where it filled bg_color')
if 'elem->drawElem = &drawGameBackground;' not in themes or 'gTheme->noTowers && !thmElemIsInfo(elem)' not in themes:
    fail.append('the vignette goes over a towers=0 list page\'s game art, never on the info page')

print('\n'.join(fail) or 'build133: RIPGRID L1 / R1 pages with the sidebar, the star at the right edge, the sky and its vignette OK')
sys.exit(1 if fail else 0)
