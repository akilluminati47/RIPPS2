"""Build 94: what is left to hunt. CHECK GAME SUPPORT also asks xeRAbora's interface page for the game's whole
set (GET /state, with OPEN TO THE NETWORK on) and keeps it as RA/<serial>.ach. Achievements > YOUR ACCOUNT
shows how many are left and opens LEFT TO HUNT (title, points, how to earn each); a launch with the In-Game
Menu on packs the locked ones into module storage, and the menu's ACHIEVEMENTS opens the same page.

Static checks on the patched tree; then, with a C compiler, rahunt.c (the /state reader, the .ach reader and
the menu's packing) and the menu's LEFT TO HUNT page rendered on the PC. RIPPS2_IGR_DUMP=<dir> writes the
pages as .ppm pictures."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8')
hunt, net, ra, mk = rd('src/rahunt.c'), rd('src/ranet.c'), rd('src/ripps2ra.c'), rd('Makefile')
sb, sysc, cfg, menu = rd('src/supportbase.c'), rd('src/system.c'), rd('ee_core/include/coreconfig.h'), rd('ee_core/src/igrmenu.c')
fail = []

if 'rahunt.o' not in mk:
    fail.append('rahunt.c must be built')
# the fetch: the PC that answered, its interface page, never fatal to the check
if 'g_peer = from.sin_addr.s_addr' not in net or 'GET /state' not in net or 'RA_UI_PORT + 5' not in net:
    fail.append("CHECK GAME SUPPORT must ask the PC that answered for GET /state (18280 and the four above)")
if 'raHuntFromState(state, stateLen, serial' not in net or 'RA/%s.ach' not in net:
    fail.append('the set must be kept as RA/<serial>.ach beside the .inf')
if 'free(state)' not in net or 'free(ach)' not in net:
    fail.append("the page's answer must be let go of after the check")
# YOUR ACCOUNT
if 'static void raHuntPage(const ra_game_t *g)' not in ra or '"LEFT TO HUNT"' not in ra:
    fail.append('YOUR ACCOUNT must open LEFT TO HUNT')
if 'games[i].hunt = raHuntLeft(&games[i])' not in ra or 'left to hunt' not in ra:
    fail.append("YOUR ACCOUNT's card must say how many are left")
if 'free(all)' not in ra or 'free(lockedAt)' not in ra:
    fail.append('LEFT TO HUNT must let go of its list when it closes')
# the launch
if 'sbLoadRaHunt(path, file)' not in sb or 'raHuntBlob(list, n, sbRaHunt' not in sb:
    fail.append('a launch must read RA/<serial>.ach and pack it for the menu')
m = re.search(r'gRipps2IgrMenu && \(huntSrc = sbGetRaHunt.*?\n.*?\n', sysc)
if not m or 'OPL_MOD_STORAGE' not in m.group(0) or '0xD0000' not in m.group(0):
    fail.append('the hunt list goes into module storage only with the menu on, at the default address, below 0xD0000')
if 'config->RaHunt = raHunt' not in sysc:
    fail.append('ee_core must be told where the hunt list is')
# coreconfig: appended, never inserted
i_unl, i_hunt = cfg.find('int RaUnlocked;'), cfg.find('const u8 *RaHunt;')
if i_unl < 0 or i_hunt < i_unl or cfg.find('int RaHuntCount;') < i_hunt:
    fail.append('RaHunt and RaHuntCount must be appended after RaUnlocked')
# the menu
if 'igrmComposeHunt' not in menu or 'hunt = 0;' not in menu or 'LEFT TO HUNT' not in menu:
    fail.append("the menu's ACHIEVEMENTS must open LEFT TO HUNT")
if 'info.hunt = 0;' not in menu:
    fail.append('a build without RetroAchievements must show no hunt list')

cc = shutil.which('gcc') or shutil.which('cc')
if cc and not fail:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # rahunt.c on the PC
        (td / 'h.c').write_text(r'''
#include <stdio.h>
#include <string.h>
#include "include/rahunt.h"
static const char *state =
    "{\"version\":\"0.1\",\"follow\":{\"on\":false,"
    "\"game\":{\"id\":9,\"serial\":\"\",\"title\":\"Other\",\"achievements\":["
    "{\"id\":1,\"title\":\"Wrong\",\"description\":\"from follow\",\"points\":5,\"state\":1}]}},"
    "\"game\":{\"id\":1234,\"serial\":\"SLUS-20482\",\"hash\":\"abcd\",\"title\":\"Burnout 3\",\"checked_only\":1},"
    "\"achievements\":["
    "{\"id\":11,\"title\":\"First Crash\",\"description\":\"Cause a \\\"takedown\\\" in any race\",\"points\":5,"
    "\"state\":2,\"percent\":0.0,\"type\":0},"
    "{\"id\":12,\"title\":\"Caf\xc3\xa9 Racer\",\"description\":\"Win\\nthe\\tcup\",\"points\":10,\"state\":1,"
    "\"badge\":{\"url\":\"x\",\"sizes\":[1,2]}},"
    "{\"id\":13,\"title\":\"Pok\u00e9mon\u2019s Rival\",\"description\":\"Beat \u201cBlue\u201d\u2026\",\"points\":15,\"state\":0}"
    "],\"subsets\":[],\"tracking\":[]}";
int main(void)
{
    static char ach[4096];
    static ra_hunt_t list[8];
    unsigned char blob[256];
    int n, count, bytes;
    n = raHuntFromState(state, (int)strlen(state), "SLUS_204.82", ach, sizeof(ach));
    if (n != 3) return 1;
    if (raHuntFromState(state, (int)strlen(state), "SLES_111.11", ach, sizeof(ach)) != -2) return 2;
    if (raHuntFromState("{\"game\":{}}", 11, "", ach, sizeof(ach)) != -1) return 3;
    raHuntFromState(state, (int)strlen(state), "SLUS_204.82", ach, sizeof(ach));
    n = raHuntRead(ach, (int)strlen(ach), list, 8);
    printf("%s", ach); /* shown when a check fails */
    if (n != 3 || list[0].unlocked != 1 || list[1].unlocked != 0 || list[1].points != 10) return 4;
    /* UTF-8 kept for the menus' fonts; marks they lack made plain */
    if (strcmp(list[0].desc, "Cause a \"takedown\" in any race") || strcmp(list[1].title, "CafÃ© Racer")) return 5;
    if (strcmp(list[1].desc, "Win the cup")) return 6;
    if (strcmp(list[2].title, "PokÃ©mon's Rival") || strcmp(list[2].desc, "Beat \"Blue\"...")) return 15;
    if (raHuntRead("nope", 4, list, 8) != -1) return 7;
    bytes = raHuntBlob(list, n, blob, sizeof(blob), &count);
    /* the locked ones, in the menu's lines: points, 1 title line, 1 description line; accents folded */
    if (count != 2 || blob[0] != 10 || blob[1] != 1 || blob[2] != 1) return 8;
    if (strcmp((char *)blob + 3, "CAFE RACER") || strcmp((char *)blob + 14, "WIN THE CUP")) return 9;
    if (strcmp((char *)blob + 29, "POKEMON'S RIVAL") || strcmp((char *)blob + 45, "BEAT 'BLUE'...")) return 16;
    if (bytes != 3 + 11 + 12 + 3 + 16 + 15) return 10;
    bytes = raHuntBlob(list, n, blob, 20, &count); /* no room: nothing half written */
    if (count != 0 || bytes != 0) return 11;
    /* a long one: the title in two lines at most, every line in 24, the description cut with "..." */
    list[1].unlocked = 0;
    strcpy(list[1].title, "The long way round the whole circuit and back");
    strcpy(list[1].desc, "Finish every race of the World Tour in first place without once using the boost, "
                         "on the hardest setting, with the camera in the cockpit and the radio off");
    bytes = raHuntBlob(list + 1, 1, blob, sizeof(blob), &count);
    if (count != 1 || blob[1] != 2 || blob[2] != RA_HUNT_ROWS - 1 - 2) return 12;
    {
        const char *l = (const char *)blob + 3, *last = l;
        int k;
        for (k = 0; k < blob[1] + blob[2]; k++) {
            if (strlen(l) > RA_HUNT_COLS || strlen(l) == 0 || l[strlen(l) - 1] == ' ') return 13;
            last = l;
            l += strlen(l) + 1;
        }
        if (strcmp(last + strlen(last) - 3, "...") || l != (const char *)blob + bytes) return 14;
    }
    printf("rahunt ok\n");
    return 0;
}
''')
        exe = td / 'h.exe'
        r = subprocess.run([cc, '-I', str(root), str(td / 'h.c'), str(root / 'src/rahunt.c'), '-o', str(exe)],
                           capture_output=True, text=True)
        if r.returncode:
            fail.append('rahunt.c must build on the PC: ' + r.stderr[-400:])
        else:
            r = subprocess.run([str(exe)], capture_output=True, text=True)
            if r.returncode:
                fail.append('rahunt.c failed check %d: %r' % (r.returncode, r.stdout[-600:]))

        # the menu's page on the PC
        (td / 'tamtypes.h').write_text('typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32; typedef unsigned long long u64;\n')
        dump = os.environ.get('RIPPS2_IGR_DUMP', '')
        (td / 't.c').write_text(r'''
#include <stdio.h>
#include <string.h>
#include "igrmenu.c"
#include "include/rahunt.h"
static u8 buf[320 * 212 * 3];
static u8 blob[RA_HUNT_BLOB];
static ra_hunt_t list[3] = {
    {0, 10, "First Crash", "Cause a takedown in any race"},
    {0, 25, "The long way round the whole circuit", "Finish every race of the World Tour in first place without once "
     "using the boost, on the hardest setting, with the camera in the cockpit and the radio turned off"},
    {0, 1, "Quiet", ""},
};
static void save(const char *dir, const char *name)
{
    char path[512];
    FILE *f;
    if (!dir[0]) return;
    snprintf(path, sizeof(path), "%s/%s.ppm", dir, name);
    if ((f = fopen(path, "wb")) == NULL) return;
    fprintf(f, "P6 320 212 255\n");
    fwrite(buf, 1, sizeof(buf), f);
    fclose(f);
}
static int longest(void) { int i, m = 0; for (i = 0; i < igrmLines; i++) if (igrmLine[i].len > m) m = igrmLine[i].len; return m; }
int main(int argc, char **argv)
{
    const char *dir = argc > 1 ? argv[1] : "";
    int k, count;
    raHuntBlob(list, 3, blob, sizeof(blob), &count); /* packed as a launch packs it */
    igrm_info_t a = {0, "SLUS_204.82", "mc0:/BOOT/RIPPS2.ELF", 1, 1, 40, 12, 1, 2, blob, count};
    igrmTestRender(&a, 1, 0, 2, 2, buf);
    save(dir, "achievements");
    if (count != 3 || igrmLine[igrmLines - 1].glyph[0] != G_CROSS) return 1; /* ok SEE THEM */
    for (k = 0; k < 3; k++) {
        char name[16];
        if (igrmTestRender(&a, 3 + k, 0, 2, 2, buf) != 212) return 2;
        sprintf(name, "hunt%d", k);
        save(dir, name);
        if (igrmLines > IGRM_LINES || longest() > TEXT_CHARS) return 10 + k;
        if (igrmLine[igrmLines - 2].y + 7 > ROW_HINT) return 20 + k; /* the page stays above its hint */
        if (igrmLine[igrmLines - 1].y != ROW_HINT || igrmLine[igrmLines - 1].glyph[0] == G_CROSS) return 30 + k;
    }
    /* the long one is cut with "..." on its last row */
    igrmTestRender(&a, 4, 0, 2, 2, buf);
    {
        igrm_line_t *l = &igrmLine[igrmLines - 2];
        if (l->glyph[l->len - 1] != '.' - 32) return 40;
    }
    /* without a list: the old page */
    a.hunt = NULL;
    a.huntCount = 0;
    igrmTestRender(&a, 1, 0, 2, 2, buf);
    if (igrmLine[igrmLines - 1].glyph[0] != G_CIRCLE) return 50;
    printf("rendered\n");
    return 0;
}
''')
        exe = td / 't.exe'
        r = subprocess.run([cc, '-DIGR_MENU_HOST_TEST', '-I', str(td), '-I', str(root / 'ee_core/include'),
                            '-I', str(root / 'ee_core/src'), '-I', str(root), str(td / 't.c'), str(root / 'src/rahunt.c'),
                            '-o', str(exe)], capture_output=True, text=True)
        if r.returncode:
            fail.append('the menu renderer must build on the PC: ' + r.stderr[-400:])
        else:
            r = subprocess.run([str(exe), dump], capture_output=True, text=True)
            if r.returncode:
                fail.append('LEFT TO HUNT failed check %d' % r.returncode)

print('\n'.join(fail) or 'build94: xeRAbora set kept as RA/<serial>.ach, YOUR ACCOUNT and the in-game menu show LEFT TO HUNT OK')
sys.exit(1 if fail else 0)
