"""Build 137 (the user, 11/03: "i want to bind it to my boot card myself to overwrite as real use case"): Manage on an
SD2PSX or MMCE card warns and binds on START (build 136 refused it); a refused bind logs the card's login and the bind's
header step to DIAG.TXT and tries once more; the confirm line names an SD2PSX or MMCE BOOT card again.

Static checks on the patched tree and the languages."""
import os
import sys
from pathlib import Path

import yaml

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
elf = Path(__file__).resolve().parents[1]
boot = (root / 'src/ripps2boot.c').read_text(encoding='utf-8')
fail = []

i, j = boot.find('if (port == 4 || port == 5) {'), boot.find('// where RIPPS2 starts from: where it is now')
mm = boot[i:j]
if 'guiMsgBoxStartOption(_t("BIND BIBLE"));' not in mm or 'if (guiMsgBox(msg, 0, NULL) != 2)' not in mm or 'nothing was tried' in mm:
    fail.append('an SD2PSX or MMCE card: a warning, and START binds BIBLE to it')
if 'h = SecrDownloadHeader(2 + port, 0, probe, &bits, &hsize);' not in boot or 'for (tries = 0; tries < 2 && !bound; tries++)' not in boot:
    fail.append('a refused bind logs the header step and tries once more after the card logs in again')
if 'bind try %d: %s' not in boot or '_t("(DIAG.TXT beside RIPPS2 has what the card said.)")' not in boot:
    fail.append('each bind try goes to DIAG.TXT, and the refusal points at it')
if '(a MagicGate card, or an SD2PSX or MMCE BOOT card): the one in slot %d.' not in boot:
    fail.append('the confirm line names an SD2PSX or MMCE BOOT card')

tpl = set(e['en'] for e in yaml.safe_load((elf / 'lang' / '_strings.yml').read_text(encoding='utf-8'))['strings'])
new = [k for k in tpl if k in ('BIND BIBLE', '(DIAG.TXT beside RIPPS2 has what the card said.)') or 'Its BOOT card can hold BIBLE' in k]
if len(new) != 3:
    fail.append('the template has build 137\'s lines (%d of 3)' % len(new))
for yml in sorted((elf / 'lang').glob('*.yml')):
    if yml.name.startswith('_'):
        continue
    d = yaml.safe_load(yml.read_text(encoding='utf-8'))['strings']
    miss = [k[:30] for k in new if k not in d]
    if miss:
        fail.append('%s lacks %s' % (yml.name, miss))

print('\n'.join(fail) or 'build137: an SD2PSX or MMCE card binds on START, a refused bind says where and tries again OK')
sys.exit(1 if fail else 0)
