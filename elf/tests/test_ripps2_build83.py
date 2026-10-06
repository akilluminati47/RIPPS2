"""Build 83: Star and Starred Games on screen, and YOUR ACCOUNT laid out so nothing is cut off.

Static checks on the patched tree."""
import os
import re
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8')
lng, opl, dia, ra = rd('lng_tmpl/_base.yml'), rd('src/opl.c'), rd('src/dialogs.c'), rd('src/ripps2ra.c')
fail = []

# --- Favorite / Favorites never reach the screen: R3 says Star, the list is Starred Games
strings = dict(re.findall(r'- label: (\w+)\s*\n\s*string: (.*)', lng))
for label, want in (('FAV', 'Starred Games'), ('FAV_HINT', 'Star'), ('FAVMODE', 'Starred Games Start Mode')):
    if strings.get(label, '').strip().strip('"') != want:
        fail.append('%s should read %r (has %r)' % (label, want, strings.get(label)))
for label, text in strings.items():
    if re.search(r'favou?rite', text, re.I):
        fail.append('on-screen string %s still says favorite: %s' % (label, text))
if '"FAVORITES"' in opl or '"STARRED GAMES"' not in opl:
    fail.append("L3's caption on the starred list must read STARRED GAMES")
if 'Favorites Page Start Mode' in dia:
    fail.append('the Game Sources label still says Favorites')

# --- YOUR ACCOUNT: wrapped messages, scrolling titles, no 64 px face for the numbers
acct = ra[ra.index('static void raAccount(void)'):]
acct = acct[:acct.index('\n}\n')]
if 'static void raWrap(' not in ra or 'raWrap(RIPPS2_CASE_FONT, tx' not in acct:
    fail.append('the account card must wrap its messages (raWrap), not clip them')
if 'fonts[14]' in acct:
    fail.append('the account page must not draw its numbers in the 64 px view-word face')
if 'fntRenderStringFit(gTheme->fonts[8], tx, 154, ALIGN_VCENTER, tw, g->title, RA_LIT, 1)' not in acct:
    fail.append("the card's title must scroll when it is too long")
if re.search(r'fntRenderString\(gTheme->fonts\[8\][^;]*cw - 20, 70', acct):
    fail.append('the boxed title render (which read past a short title into old text) is back')

print('\n'.join(fail) or 'build83: Star and Starred Games, YOUR ACCOUNT nothing cut off OK')
sys.exit(1 if fail else 0)
