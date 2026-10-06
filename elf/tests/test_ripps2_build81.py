"""Build 81: Source Name's Pop In is the view word.

The source's name is not drawn over the list when Pop In is set; it plays like L3's toast, centred, in
the view word's letters, the whole name in capitals (ALL GAMES: the GAMES tells it from L3's ALL), on
the first list after boot, on a source change and on coming back to Storage, not after an info page.
Static checks on the patched tree."""
import os, sys
from pathlib import Path
root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text()
th, ui, hdr = rd('src/themes.c'), rd('src/ripps2ui.c'), rd('include/ripps2.h')
fail = []

# --- the theme's source line: with Pop In, the toast and nothing else (no line, no glyphs)
mt = th[th.index('static void drawMenuText(struct menu_list'):]
mt = mt[:mt.index('\n}\n')]
pop = mt.find('if (ripps2SourceNameMode() == RIPPS2_SRC_POP) {')
if pop < 0 or 'ripps2SourceToast(text);\n        return;' not in mt[pop:pop + 200]:
    fail.append('Pop In must hand the name to the toast and draw no line')
if pop > 0 and (mt.find('rmDrawPixmap(', 0, pop) >= 0 or mt.find('fntRenderString(', 0, pop) >= 0):
    fail.append('nothing may draw beside or over the list before the Pop In check')

# --- the toast: the whole name upper-cased, no caption, a view word
st = ui[ui.index('void ripps2SourceToast(const char *text)'):]
st = st[:st.index('\n}\n')]
if 'toupper(' not in st or 'ripps2ShowViewWord(word, -1, NULL);' not in st:
    fail.append('the toast must be the whole name in capitals as a view word, no caption')
if 'srcToastArmed' not in st or 'strncmp(shown, text' not in st:
    fail.append('the toast must play once per source, and again when armed')
sc = ui[ui.index('void ripps2SetCategory(int cat)'):]
sc = sc[:sc.index('\n}\n')]
if 'if (cat == RIPPS2_CAT_STORAGE)\n        srcToastArmed = 1;' not in sc:
    fail.append('coming back to Storage must name the source again')
if 'static int srcToastArmed = 1;' not in ui:
    fail.append('the first list after boot must name its source')

# --- room for the longest names, kept on screen
if 'static char viewWord[24]' not in ui or 'WORD_MAX_SPAN' not in ui:
    fail.append('the view word must hold and fit a source name (UDPFSBD GAMES)')
if 'ripps2DrawSourcePop' in ui + th + hdr:
    fail.append('the old letter-by-letter line must be gone')

print('\n'.join(fail) or 'build81: Pop In as the view word OK')
sys.exit(1 if fail else 0)
