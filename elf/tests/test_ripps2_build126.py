"""Build 126: CHEATS in the in-game menu (Settings > General > In-Game Menu > Cheats, off by default): every cheat of the
game's file, turned on or off while the game is paused, written into the engine's code list on RESUME. The code list
left ee_core's .bss for the space after the modules to make the room. The idea is RiptOPL's In-Game Menu's
(NathanNeurotic/RiptOPL #184, Open-PS2-Loader #1155).

Static checks on the patched tree, then, when a C compiler is around: the launcher's real packing and list code
(cheatman.c) against the engine's real SetupCheats (ee_core cheat_api.c), the menu's real writes (igrmenu.c
igrmCheatsWrite) checked pair by pair, and the pages drawn on the PC."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8').replace('\r\n', '\n')
fail = []

menu, eng, engh, api, cfg = rd('ee_core/src/igrmenu.c'), rd('ee_core/src/cheat_engine.S'), rd('ee_core/include/cheat_engine.h'), rd('ee_core/src/cheat_api.c'), rd('ee_core/include/coreconfig.h')
cm, sysc, shot, opl, dia = rd('src/cheatman.c'), rd('src/system.c'), rd('src/ripps2shot.c'), rd('src/opl.c'), rd('src/dialogs.c')

# off by default, saved, greyed with the menu off
if 'int gRipps2IgrCheats = 0;' not in shot:
    fail.append('Cheats must be off by default')
if '"ripps2_igr_cheats"' not in opl or opl.count('ripps2_igr_cheats') != 2:
    fail.append('Cheats must be read and saved (ripps2_igr_cheats)')
if 'diaSetEnabled(diaIgrConfig, UICFG_RIPPS2_IGRCHEATS, igr == 0);' not in shot:
    fail.append('Cheats is greyed while the menu is off')
if 'UICFG_RIPPS2_IGRCHEATS' not in dia.split('struct UIItem diaIgrConfig[]')[1].split('UI_TERMINATOR')[0]:
    fail.append('Cheats must be a row of In-Game Menu\'s page')

# the launch: the page only with Cheats on, the menu's stack, the engine on, not a disc game, not Mode 6
if 'if (gRipps2IgrCheats && igrStack != NULL && !discMode && GetCheatsEnabled() && !(compatflags & COMPAT_MODE_6) &&' not in sysc:
    fail.append('the CHEATS page: Cheats on, the menu on, the engine on, no disc, no Mode 6')
if 'config->CheatSet = config->gCheatList != NULL ? cheatSet : NULL;' not in sysc:
    fail.append('the code list must reach ee_core (config->CheatSet)')
if 'if (!discMode && GetCheatsEnabled() && cheatSet != NULL) {' not in sysc:
    fail.append('no code list room means no cheats (never a list ee_core cannot hold)')
if sysc.index('u32 *cheatSet = NULL;') > sysc.index('void *igrStack = NULL'):
    fail.append('the code list takes its room first, before the menu\'s stack')

# ee_core: appended fields, the list out of .bss, the engine's state word
for f in ('void *IgrCheats;', 'unsigned int *CheatSet;'):
    if f not in cfg or cfg.index(f) < cfg.index('const unsigned char *IgrFont;'):
        fail.append('coreconfig.h: %s must be appended' % f)
if 'codelist:' in eng or 'numcodes:' in eng or '0:(MAX_CODES*2)' in eng:
    fail.append('the code list must not be in ee_core\'s .bss any more')
if 'lw      $t0, codeset\n    beqz    $t0, ch_ret' not in eng:
    fail.append('CodeHandler must walk the list codeset points at, and none when it is NULL')
if eng.count('%lo(codestate)') != 2:
    fail.append('CodeHandler must say when it starts (1) and ends (2) a pass')
if 'codeset = set;' not in api or 'set[0] = k / 2;' not in api:
    fail.append('SetupCheats must fill the list after the modules')
if 'if (codestate == 1)\n        return 0;' not in menu:
    fail.append('the menu must leave the list alone while a paused thread is inside a pass')
if 'b->pairs == codeset[0]' not in menu:
    fail.append('the menu must check the list holds exactly the packed pairs before writing it')

cc = shutil.which('gcc') or shutil.which('cc') or shutil.which('clang')
if not cc and os.path.exists('C:/msys64/mingw64/bin/gcc.exe'):
    cc = 'C:/msys64/mingw64/bin/gcc.exe'


def body(text, start):
    """the function that starts with `start`, up to its closing brace at column 0"""
    i = text.index(start)
    return text[i:text.index('\n}\n', i) + 3]


LIST_TEST = r"""
#include <stdio.h>
#include <string.h>
#include "cm.h"

/* the engine's SetupCheats and the menu's write, as ee_core has them */
typedef struct { const u32 *gCheatList; u32 *CheatSet; } cfg_t;
static cfg_t cfgv;
#define USE_LOCAL_EECORE_CONFIG cfg_t *config = &cfgv;
static u32 hooklist[MAX_HOOKS * 2], numhooks, *codeset, codestate = 2, setmem[1 + MAX_CODES * 2];
SETUP
WRITE

static void add(int i, const char *name, int enabled, const u32 *pairs, int n)
{
    strcpy(gCheats[i].name, name);
    gCheats[i].enabled = enabled;
    for (int k = 0; k < n; k++) {
        gCheats[i].codes[k].addr = pairs[k * 2];
        gCheats[i].codes[k].val = pairs[k * 2 + 1];
    }
}

static u8 pack[64 * 1024];

/* every row's pairs in the engine's list are its own (ON) or {0, 1} (OFF), and nothing else is there */
static int same(const igr_cheats_t *h)
{
    const igr_cheat_t *row = IGR_CHEATS_ROWS(h);
    const u32 *codes = IGR_CHEATS_CODES(h);
    if (codeset == NULL || codeset[0] != h->pairs) return 0;
    for (u32 r = 0; r < h->count; r++)
        for (u32 k = row[r].at; k < (u32)row[r].at + row[r].count; k++)
            if (codeset[1 + k * 2] != (row[r].on ? codes[k * 2] : 0) || codeset[2 + k * 2] != (row[r].on ? codes[k * 2 + 1] : IGR_CHEAT_OFF_VAL))
                return 0;
    return 1;
}

int main(void)
{
    static cheat_entry_t table[MAX_CODES];
    gCheats = table;
    /* the master code (a hook and a plain write), a two-line 4-type code whose second line looks like a hook, a
       write of 0 (an OFF {0, 0} would end the list), and a cheat sharing the master's hook */
    const u32 m[] = {0x9019D2E8, 0x0C064A84, 0x20100000, 0x00000001};
    const u32 a[] = {0x40200000, 0x00010002, 0x90123456, 0x00000000};
    const u32 b[] = {0x20300000, 0x00000000, 0x20300004, 0x00000000};
    const u32 c[] = {0x9019D2E8, 0x0C064A84, 0x10400000, 0x0000FFFF};
    add(0, "MASTER CODE", 1, m, 2);
    add(1, "Infinite Health For Everyone", 0, a, 2);
    add(2, "ZEROES", 1, b, 2);
    add(3, "SHARED HOOK", 0, c, 2);

    int bytes = igrCheatsPack(pack, sizeof(pack));
    igr_cheats_t *h = (igr_cheats_t *)pack;
    igr_cheat_t *row = IGR_CHEATS_ROWS(h);
    if (bytes <= 0 || h->magic != IGR_CHEATS_MAGIC || h->count != 4 || h->pairs != 1 + 2 + 2 + 1) return 1;
    if (strcmp(row[1].name, "Infinite Health Fo") != 0) { printf("[%s]\n", row[1].name); return 2; } /* 18 characters */
    if (!row[0].on || row[1].on || !row[2].on || row[3].on) return 3;

    set_cheats_list_live(pack);
    cfgv.gCheatList = GetCheatsList();
    cfgv.CheatSet = setmem;
    SetupCheats();
    if (numhooks != 1 || hooklist[0] != (0x9019D2E8 & 0x01FFFFFC)) return 4; /* one hook, once */
    if (!same(h)) return 5;

    /* the menu turns cheats on and off: the list follows, row by row */
    row[1].on = 1;
    row[2].on = 0;
    if (!igrmCheatsWrite(h) || !same(h)) return 6;
    row[0].on = 0;
    row[3].on = 1;
    if (!igrmCheatsWrite(h) || !same(h)) return 7;
    /* a paused thread inside a pass: nothing is written */
    codestate = 1;
    row[3].on = 0;
    if (igrmCheatsWrite(h) || same(h)) return 8;
    codestate = 2;

    /* no room: no page */
    if (igrCheatsPack(pack, 64) != 0) return 9;

    /* more than the list holds: the ticked ones are kept, the others listed while they fit */
    memset(table, 0, sizeof(table));
    static u32 big[2 * 200];
    for (int k = 0; k < 200; k++) { big[k * 2] = 0x20000000 + k * 4; big[k * 2 + 1] = 1; }
    add(0, "BIG", 1, big, 200);
    add(1, "TOO BIG NOW", 0, big, 100);
    add(2, "SMALL", 0, big, 10);
    bytes = igrCheatsPack(pack, sizeof(pack));
    if (bytes <= 0 || h->count != 2 || h->pairs != 210) return 10;
    set_cheats_list_live(pack);
    SetupCheats();
    if (!same(h)) return 11;
    /* a ticked cheat that cannot be listed: no page */
    gCheats[1].enabled = 1;
    if (igrCheatsPack(pack, sizeof(pack)) != 0) return 12;
    printf("list OK\n");
    return 0;
}
"""

PAGES_TEST = r"""
#include <stdio.h>
#include <string.h>
#include "igrmenu.c"
static u8 buf[320 * 252 * 3];
static char txt[IGRM_LINES][40];
static void texts(void)
{
    int i, k;
    for (i = 0; i < igrmLines; i++) {
        for (k = 0; k < igrmLine[i].len; k++) {
            int g = igrmLine[i].glyph[k];
            txt[i][k] = g < 64 ? g + 32 : g == G_CROSS ? 'X' : g == G_CIRCLE ? 'O' : g == G_TILDE ? '~' : '>';
        }
        txt[i][k] = 0;
    }
}
static int has(const char *s)
{
    int i;
    texts();
    for (i = 0; i < igrmLines; i++)
        if (strcmp(txt[i], s) == 0) return 1;
    printf("missing [%s]; the page:", s);
    for (i = 0; i < igrmLines; i++) printf(" [%s]", txt[i]);
    printf("\n");
    return 0;
}
static int fits(void)
{
    int i;
    for (i = 0; i < igrmLines; i++)
        if (igrmLine[i].x + igrmLine[i].len * 6 - 1 > PW - 4 || igrmLine[i].y + 7 > igrmH - 2) return 0;
    return 1;
}
/* no two lines overlap (the six items' rows, a name and its ON / OFF) */
static int apart(void)
{
    int i, j;
    for (i = 0; i < igrmLines; i++)
        for (j = i + 1; j < igrmLines; j++) {
            const igrm_line_t *a = &igrmLine[i], *b = &igrmLine[j];
            if (a->y < b->y + 7 && b->y < a->y + 7 && a->x < b->x + b->len * 6 - 1 && b->x < a->x + a->len * 6 - 1) return 0;
        }
    return 1;
}
static struct { igr_cheats_t h; igr_cheat_t row[12]; } pk;
int main(void)
{
    igrm_info_t a = {0, "SLUS_209.46", "", 1, 1, 40, 12, 1, 2, NULL, 0, 1,
                     RIPSHOT_READY, 3, 3, 3, -1, 640, 448, "SLUS_209.46", "USB", "Aqua Teen Hunger Force"};
    int i, y;

    /* without cheats: the menu as before */
    igrmTestPage(&a, 0, 0, 0, 2, 2, "", buf);
    if (igrmItems != 5 || igrmBarH != 11) return 1;

    pk.h.magic = IGR_CHEATS_MAGIC;
    pk.h.count = 12;
    for (i = 0; i < 12; i++) {
        snprintf(pk.row[i].name, sizeof(pk.row[i].name), "CHEAT NUMBER %d", i + 1);
        pk.row[i].on = i % 3 == 0;
    }
    a.cheats = &pk.h;

    /* CHEATS second, six items in the five rows' room, between the separators */
    if (igrmTestPage(&a, 0, 1, 0, 2, 2, "", buf) != 252 || igrmItems != 6 || igrmIds[1] != IT_CHEATS) return 2;
    if (!has("CHEATS") || !has("4 OF 12 ON") || !has("CHANGES APPLY ON RESUME") || !fits() || !apart()) return 3;
    for (i = 0; i < igrmLines; i++)
        if (igrmLine[i].x == ITEM_X && (igrmLine[i].y <= ROW_SEP1 || igrmLine[i].y + 7 > ROW_SEP2)) return 4;
    for (y = 0; y < 6; y++) { /* every item's bar clears both separators */
        igrmTestPage(&a, 0, y, 0, 1, 1, "", buf);
        if (igrmBarY <= ROW_SEP1 || igrmBarY + igrmBarH - 1 > ROW_SEP2) return 5;
    }
    igrmTestPage(&a, 0, 5, 0, 2, 2, "", buf);
    if (!has("POWER OFF") || !fits() || !apart()) return 6;
    a.cheatsIdle = 1;
    igrmTestPage(&a, 0, 1, 0, 2, 2, "", buf);
    if (!has("THE CHEAT ENGINE HAS NOT") || !has("(CHECK THE MASTER CODE)") || !fits()) return 7;
    a.cheatsIdle = 0;
    a.cheatsBusy = 1;
    igrmTestPage(&a, 0, 1, 0, 2, 2, "", buf);
    if (!has("RESUME, THEN OPEN AGAIN") || !fits()) return 8;

    /* the page: nine rows, the cursor's row in view, ON / OFF to the right of 18 characters */
    strcpy(pk.row[0].name, "ABCDEFGHIJKLMNOPQR");
    igrmTestPage(&a, 3, 0, 0, 2, 2, "", buf);
    if (!has("1/12") || !has("ABCDEFGHIJKLMNOPQR") || !has("ON") || !has("OFF") || !has("X ON/OFF   O BACK") || !fits() || !apart()) return 9;
    igrmTestPage(&a, 3, 11, 0, 2, 2, "", buf);
    if (!has("12/12") || !has("CHEAT NUMBER 12") || has("CHEAT NUMBER 3") || !fits() || !apart()) return 10;
    printf("pages OK\n");
    return 0;
}
"""

if cc and not fail:
    env = dict(os.environ)
    if cc.startswith('C:/msys64'):
        env['PATH'] = 'C:/msys64/mingw64/bin' + os.pathsep + env.get('PATH', '')
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / 'tamtypes.h').write_text('typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32; typedef unsigned long long u64;\n')

        # the launcher's build-126 half of cheatman.c, with what it needs from the rest of it
        types = rd('include/cheatman.h')
        types = types[types.index('#define MAX_HOOKS'):types.index('// Lazily allocated')]
        types = re.sub(r'#define CHEAT_VERSION.*\n', '', types)
        launcher = cm[cm.index('/*\n * RIPPS2 build 126'):]
        (td / 'cm.h').write_text('#include <stdio.h>\n#include <string.h>\n#include <tamtypes.h>\n' + types +
                                 '#include "igrcheats.h"\nstatic cheat_entry_t *gCheats;\nstatic u32 gCheatList[MAX_CHEATLIST];\n'
                                 'const u32 *GetCheatsList(void) { return gCheatList; }\n' + launcher)
        setup = body(api, 'void SetupCheats()')
        write = body(menu, 'static int igrmCheatsWrite(const igr_cheats_t *b)')
        (td / 'l.c').write_text(LIST_TEST.replace('SETUP', setup).replace('WRITE', write))
        exe = td / 'l.exe'
        r = subprocess.run([cc, '-std=gnu99', '-Wall', '-Werror', '-Wno-unused-function', '-I', str(td), '-I', str(root / 'ee_core/include'),
                            str(td / 'l.c'), '-o', str(exe)], capture_output=True, text=True, env=env)
        if r.returncode:
            fail.append('the launcher\'s list and the engine\'s SetupCheats must build on the PC: ' + r.stderr[-800:])
        else:
            r = subprocess.run([str(exe)], capture_output=True, text=True, env=env)
            if r.returncode:
                fail.append('the cheat list failed check %d %s' % (r.returncode, r.stdout[-400:]))

        (td / 'p.c').write_text(PAGES_TEST)
        exe = td / 'p.exe'
        r = subprocess.run([cc, '-DIGR_MENU_HOST_TEST', '-I', str(td), '-I', str(root / 'ee_core/include'),
                            '-I', str(root / 'ee_core/src'), str(td / 'p.c'), '-o', str(exe)], capture_output=True, text=True, env=env)
        if r.returncode:
            fail.append('the CHEATS pages must build on the PC: ' + r.stderr[-600:])
        else:
            r = subprocess.run([str(exe)], capture_output=True, text=True, env=env)
            if r.returncode:
                fail.append('the CHEATS pages failed check %d %s' % (r.returncode, r.stdout[-400:]))
elif not cc:
    print('no C compiler: static checks only')

if fail:
    print('\n'.join(fail))
    sys.exit(1)
print('build 126 OK')
