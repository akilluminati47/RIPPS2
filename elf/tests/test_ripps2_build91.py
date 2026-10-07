"""Build 91: the launch disc (launch_disc=pop|spin, Flow and Grid > Launch Disc), Interface > Flow and Grid (the
vignette in place of the dim, Grid Layout), <RIPgrid> built in, no two dialog ids alike, a row of hidden controls
taking no line, the Network page's order, and Memory Files calling a folder a folder.

Static checks on the patched tree; then, with a C compiler, every dialog id compiled and checked unique (with
and without PADEMU), and Memory Files' wording (fbWhat) run on the PC."""
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
elf = Path(__file__).resolve().parents[1]
rd = lambda p: (root / p).read_text(encoding='utf-8')
thm, gui, mk, dia, dlg, opl, ui, bg, files, yml = (rd('src/themes.c'), rd('src/gui.c'), rd('Makefile'), rd('src/dia.c'), rd('src/dialogs.c'),
                                                   rd('src/opl.c'), rd('src/ripps2ui.c'), rd('src/ripps2bg.c'), rd('src/ripps2files.c'),
                                                   rd('lng_tmpl/_base.yml'))
fail = []

# the launch disc
if '"launch_disc"' not in thm or 'RIPPS2_LAUNCH_DISC], RIPPS2_LAUNCH_DISC' not in thm or 'ripps2_disc' not in mk:
    fail.append('themes must set launch_disc and carry its disc image')
png = elf / 'theme' / 'gfx' / 'ripps2_disc.png'
if not png.exists() or struct.unpack('>IIBB', png.read_bytes()[16:26])[2:] != (8, 3):
    fail.append("elf/theme/gfx/ripps2_disc.png must be RIPPS2's 8-bit disc")
if 'void rmDrawPixmapRotated(' not in rd('src/renderman.c'):
    fail.append('the spin needs a turned texture (rmDrawPixmapRotated)')
if 'ripps2LaunchDiscArm(support, gameIdStartup);' not in opl or opl.count('!ripps2LaunchDiscFrame()') != 2:
    fail.append("a game launch must arm its disc, and the disc stand in for Please Wait")
if 'ripps2DrawLaunchDisc();' not in bg or 'if (!ripps2DrawLaunchDisc())' not in bg:
    fail.append('the launch light-up and its waits must draw the disc')
if '"ICO"' not in ui or 'DISC_REVMAX' not in ui:
    fail.append("the disc is the game's ICO art, and the spin ramps to a cap")
if 'launch_disc=spin' not in rd('misc/theme_coverflow.cfg') or 'launch_disc=pop' not in rd('misc/theme_ripgrid.cfg'):
    fail.append('RIPFLOW spins its disc and RIPgrid pops its in')
if 'ripps2_launch_disc' not in opl:
    fail.append('Launch Disc must be saved')

# Flow and Grid; <RIPgrid> built in
if 'string: Flow and Grid' not in yml or 'string: Vignette Other Covers' not in yml:
    fail.append('Interface must call the page Flow and Grid, its old dim Vignette Other Covers')
if 'COVERFLOW_CFG_LAYOUT' not in dlg or 'COVERFLOW_CFG_LAUNCHDISC' not in dlg:
    fail.append('Flow and Grid must have Grid Layout and Launch Disc')
if 'drawCoverVignette(' not in thm or 'gCoverflowDimCovers && i != centerIdx' in thm:
    fail.append('the covers not chosen must take the vignette in place of the dim')
if 'gRipps2GridLayout >= 1' not in thm or 'thmSetGuiValue(thmGetGuiValue(), 1)' not in gui:
    fail.append('a Grid Layout must apply (the theme loads again with it)')
if '"<RIPgrid>"' not in thm or 'theme_ripgrid.o' not in mk or 'gLoadGridBuiltin' not in thm:
    fail.append('<RIPgrid> must be built in')

# hidden rows, Network, the BDMA row
if dia.count('diaRowCollapses(') < 3:
    fail.append('a row of hidden controls must take no line, drawn and measured alike')
net = dlg[dlg.index('struct UIItem diaNetConfig[]'):]
net = net[:net.index('{UI_TERMINATOR}')]
if '"RIPPS2", -1' in net or 'NETCFG_RA_BUTTON' not in net:
    fail.append('Network: no RIPPS2 header, and Achievements with the other features')
if '{UI_SPLITTER},' not in net.split('_STR_POPSTARTER_NETWORK_SETTINGS')[0][-600:]:
    fail.append('Network: a line under the share settings, then POPSTARTER, NBD, Cover Art, Achievements')
if 'string: Default' not in yml[yml.index('- label: NO_ITEMS'):yml.index('- label: NO_ITEMS') + 60]:
    fail.append('an empty value must read Default')

# Memory Files' words
if 'fbFiles(' in files or '"%d / %d FILES"' not in files or 'FOLDER AND CONTENTS' not in files:
    fail.append('Memory Files must call a folder a folder and count the files as a paste goes')

cc = shutil.which('gcc') or shutil.which('cc')
if cc:
    h = rd('include/dialogs.h')
    body = h[h.index('enum UI_ITEMS {'):h.index('};', h.index('enum UI_ITEMS {')) + 2]
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # every build flavour's ids: the names come from the enum as the preprocessor leaves it for each
        for pademu, ra in ((1, 1), (0, 1), (1, 0)):
            flags = (['-DPADEMU'] if pademu else []) + (['-DRETROACHIEVEMENTS'] if ra else [])
            (td / 'e.c').write_text(body)
            pre = subprocess.run([cc, '-E', '-P'] + flags + [str(td / 'e.c')], capture_output=True, text=True).stdout
            names = [m.group(1) for m in re.finditer(r'^\s*([A-Z][A-Z_0-9]+)\s*(?:=\s*[^,]+)?,', pre, re.M)]
            src = ['#include <stdio.h>', pre, 'int main(void){']
            src += ['printf("%%d %s%s", %s);' % (n, chr(92) + 'n', n) for n in sorted(set(names))]
            src.append('return 0;}')
            (td / 'ids.c').write_text('\n'.join(src))
            r = subprocess.run([cc, str(td / 'ids.c'), '-o', str(td / 'ids.exe')], capture_output=True, text=True)
            if r.returncode:
                fail.append('dialog ids must compile: ' + r.stderr[-300:])
                break
            out = subprocess.run([str(td / 'ids.exe')], capture_output=True, text=True).stdout.split('\n')
            seen = {}
            for row in out:
                if not row.strip():
                    continue
                v, n = row.split(' ', 1)
                if n.startswith('COMPAT_MODE_BASE') or n == 'UIID_BTN_CANCEL':
                    continue
                if v in seen:
                    fail.append('dialog ids %s and %s are both %s (%s)' % (seen[v], n, v, ' '.join(flags)))
                seen[v] = n
            modeBase = [int(r.split()[0]) for r in out if r.endswith(' COMPAT_MODE_BASE')]
            if modeBase and max(int(v) for v in seen) >= modeBase[0]:
                fail.append('the per-game ids must stay under COMPAT_MODE_BASE')
        m = re.search(r'static void fbWhat\(char \*out, int size, int dirs, int files\)\n\{.*?\n\}\n', files, re.S)
        if not m:
            fail.append('fbWhat must name what a paste moves')
        else:
            (td / 'w.c').write_text('#include <stdio.h>\n#include <string.h>\n' + m.group(0) + r'''
int main(void)
{
    char b[64];
    int bad = 0;
    fbWhat(b, sizeof(b), 0, 1); bad |= strcmp(b, "1 FILE") != 0;
    fbWhat(b, sizeof(b), 0, 3); bad |= strcmp(b, "3 FILES") != 0;
    fbWhat(b, sizeof(b), 1, 0); bad |= strcmp(b, "FOLDER AND CONTENTS") != 0;
    fbWhat(b, sizeof(b), 2, 0); bad |= strcmp(b, "2 FOLDERS AND CONTENTS") != 0;
    fbWhat(b, sizeof(b), 1, 2); bad |= strcmp(b, "1 FOLDER, 2 FILES") != 0;
    printf("%d\n", bad);
    return bad;
}
''')
            r = subprocess.run([cc, str(td / 'w.c'), '-o', str(td / 'w.exe')], capture_output=True, text=True)
            if r.returncode or subprocess.run([str(td / 'w.exe')]).returncode:
                fail.append('Memory Files must say FOLDER AND CONTENTS for folders and count files as files')

print('\n'.join(fail) or 'build91: launch disc, Flow and Grid, <RIPgrid>, unique dialog ids, hidden rows, Network, folder wording OK')
sys.exit(1 if fail else 0)
