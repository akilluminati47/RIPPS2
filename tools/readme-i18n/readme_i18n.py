"""RIPPS2's READMEs in RIPPS2's 32 languages (the user, 11/01: "international software", opencode's language bar).

A README is cut into blocks: a heading, a paragraph, a list item with its following lines, a table row, a quote line, an
HTML line. Code fences, badge rows, pictures, rules and table separators are not words and stay as they are. Each
language keeps its blocks in <repo>/i18n/<code>.json as {block id: {"en": <the English's hash>, "t": <translation>}};
the block id is the hash of the English block, so an English edit makes a new id and the old one shows as stale.

    python readme_i18n.py units <repo> [code]   the blocks a language still needs (all of them without a code), as JSON
    python readme_i18n.py check <repo>          every translation: links, code, tags and table cells kept; stale; missing
    python readme_i18n.py build <repo>          the language bar on README.md and README.<code>.md for every language

A translation must keep every link target, every `code` span, every HTML tag and a table row's cells; a block that does
not passes as missing and the English is used in its place. The English README stays the one source.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

# RIPPS2's languages: README.<code>.md, the name each language calls itself, and whether it is written right to left
LANGS = [
    ('en', 'English', 0), ('es', 'Español', 0), ('pt-BR', 'Português (Brasil)', 0), ('pt', 'Português', 0),
    ('fr', 'Français', 0), ('de', 'Deutsch', 0), ('it', 'Italiano', 0), ('nl', 'Nederlands', 0), ('da', 'Dansk', 0),
    ('sv', 'Svenska', 0), ('pl', 'Polski', 0), ('cs', 'Čeština', 0), ('hr', 'Hrvatski', 0), ('sr', 'Srpski', 0),
    ('bg', 'Български', 0), ('ru', 'Русский', 0), ('el', 'Ελληνικά', 0), ('hu', 'Magyar', 0), ('ro', 'Română', 0),
    ('gl', 'Galego', 0), ('sq', 'Shqip', 0), ('tr', 'Türkçe', 0), ('ar', 'العربية', 1), ('fa', 'فارسی', 1),
    ('ja', '日本語', 0), ('ko', '한국어', 0), ('zh-CN', '简体中文', 0), ('zh-TW', '繁體中文', 0), ('vi', 'Tiếng Việt', 0),
    ('lo', 'ລາວ', 0), ('id', 'Bahasa Indonesia', 0), ('fil', 'Filipino', 0), ('ceb', 'Cebuano', 0),
]
CODES = [c for c, _, _ in LANGS]
BAR_START, BAR_END = '<!-- i18n: the language bar, made by ps2-pillars tools/readme-i18n -->', '<!-- /i18n -->'

# the note under the bar on a translated page, per language (the English is the one kept current)
NOTE = {
    'es': 'Traducción del README en inglés; si difieren, vale el inglés.',
    'pt-BR': 'Tradução do README em inglês; se diferirem, vale o inglês.',
    'pt': 'Tradução do README em inglês; se diferirem, vale o inglês.',
    'fr': 'Traduction du README anglais ; en cas de différence, l’anglais fait foi.',
    'de': 'Übersetzung der englischen README; bei Abweichungen gilt das Englische.',
    'it': 'Traduzione del README inglese; se differiscono, vale l’inglese.',
    'nl': 'Vertaling van de Engelse README; bij verschillen geldt het Engels.',
    'da': 'Oversættelse af den engelske README; hvis de afviger, gælder den engelske.',
    'sv': 'Översättning av den engelska README; vid skillnader gäller den engelska.',
    'pl': 'Tłumaczenie angielskiego README; w razie różnic obowiązuje wersja angielska.',
    'cs': 'Překlad anglického README; pokud se liší, platí angličtina.',
    'hr': 'Prijevod engleskog README-a; ako se razlikuju, vrijedi engleski.',
    'sr': 'Prevod engleskog README-a; ako se razlikuju, važi engleski.',
    'bg': 'Превод на английския README; при разлики важи английският.',
    'ru': 'Перевод английского README; при расхождениях верен английский.',
    'el': 'Μετάφραση του αγγλικού README· αν διαφέρουν, ισχύει το αγγλικό.',
    'hu': 'Az angol README fordítása; eltérés esetén az angol az irányadó.',
    'ro': 'Traducerea README-ului în engleză; dacă diferă, este valabilă engleza.',
    'gl': 'Tradución do README en inglés; se difiren, vale o inglés.',
    'sq': 'Përkthim i README-së në anglisht; nëse ndryshojnë, vlen anglishtja.',
    'tr': 'İngilizce README’nin çevirisi; farklılık olursa İngilizce geçerlidir.',
    'ar': 'ترجمة لملف README الإنجليزي؛ إن اختلفا فالإنجليزي هو المعتمد.',
    'fa': 'ترجمهٔ README انگلیسی؛ اگر فرق داشتند، نسخهٔ انگلیسی معتبر است.',
    'ja': '英語の README の翻訳です。内容が異なる場合は英語版が正です。',
    'ko': '영어 README의 번역입니다. 내용이 다르면 영어판이 기준입니다.',
    'zh-CN': '英文 README 的译本；如有出入，以英文为准。',
    'zh-TW': '英文 README 的譯本；如有出入，以英文為準。',
    'vi': 'Bản dịch README tiếng Anh; nếu khác nhau, bản tiếng Anh là chuẩn.',
    'lo': 'ການແປ README ພາສາອັງກິດ; ຖ້າແຕກຕ່າງກັນ ໃຫ້ຖືພາສາອັງກິດ.',
    'id': 'Terjemahan README bahasa Inggris; jika berbeda, yang berlaku bahasa Inggris.',
    'fil': 'Salin ng README sa Ingles; kung magkaiba, ang Ingles ang masusunod.',
    'ceb': 'Hubad sa README nga Iningles; kung lahi, ang Iningles ang sundon.',
}

# The family's link bar (the same in every repo): its four words, per language; the repo names stay as they are
FAMILY = {
    'es': ('Descargar', 'Temas', 'Fuentes', 'Web'), 'pt-BR': ('Baixar', 'Temas', 'Fontes', 'Site'),
    'pt': ('Transferir', 'Temas', 'Tipos de letra', 'Site'), 'fr': ('Télécharger', 'Thèmes', 'Polices', 'Site web'),
    'de': ('Download', 'Themes', 'Schriften', 'Website'), 'it': ('Scarica', 'Temi', 'Font', 'Sito'),
    'nl': ('Downloaden', "Thema's", 'Lettertypen', 'Website'), 'da': ('Hent', 'Temaer', 'Skrifttyper', 'Websted'),
    'sv': ('Ladda ner', 'Teman', 'Typsnitt', 'Webbplats'), 'pl': ('Pobierz', 'Motywy', 'Czcionki', 'Strona'),
    'cs': ('Stáhnout', 'Motivy', 'Písma', 'Web'), 'hr': ('Preuzmi', 'Teme', 'Fontovi', 'Web'),
    'sr': ('Preuzmi', 'Teme', 'Fontovi', 'Sajt'), 'bg': ('Изтегляне', 'Теми', 'Шрифтове', 'Сайт'),
    'ru': ('Скачать', 'Темы', 'Шрифты', 'Сайт'), 'el': ('Λήψη', 'Θέματα', 'Γραμματοσειρές', 'Ιστότοπος'),
    'hu': ('Letöltés', 'Témák', 'Betűtípusok', 'Weboldal'), 'ro': ('Descarcă', 'Teme', 'Fonturi', 'Site'),
    'gl': ('Descargar', 'Temas', 'Fontes', 'Web'), 'sq': ('Shkarko', 'Temat', 'Fontet', 'Faqja'),
    'tr': ('İndir', 'Temalar', 'Yazı tipleri', 'Web sitesi'), 'ar': ('تنزيل', 'السمات', 'الخطوط', 'الموقع'),
    'fa': ('دانلود', 'پوسته‌ها', 'فونت‌ها', 'وب‌سایت'), 'ja': ('ダウンロード', 'テーマ', 'フォント', 'ウェブサイト'),
    'ko': ('다운로드', '테마', '글꼴', '웹사이트'), 'zh-CN': ('下载', '主题', '字体', '网站'),
    'zh-TW': ('下載', '主題', '字型', '網站'), 'vi': ('Tải về', 'Giao diện', 'Phông chữ', 'Trang web'),
    'lo': ('ດາວໂຫຼດ', 'ທີມ', 'ຟອນ', 'ເວັບໄຊ'), 'id': ('Unduh', 'Tema', 'Fon', 'Situs'),
    'fil': ('I-download', 'Mga tema', 'Mga font', 'Website'), 'ceb': ('I-download', 'Mga tema', 'Mga font', 'Website'),
}


def family_bar(t):
    return t.lstrip().startswith('<p align="center"><sub>') and '&middot;' in t and 'akilluminati47' in t


def family_tr(t, code):
    w = FAMILY[code]
    for en, tr in zip(('Download', 'Themes', 'Fonts', 'Website'), w):
        t = t.replace('>%s</a>' % en, '>%s</a>' % tr).replace('<b>%s</b>' % en, '<b>%s</b>' % tr)
    return t


FENCE = re.compile(r'^\s*(```|~~~)')
LIST = re.compile(r'^(\s*)([-*+]|\d+\.)\s+')
LINK_TARGET = re.compile(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)|(?:href|src)="([^"]+)"')
CODE = re.compile(r'`[^`]+`')
TAG = re.compile(r'</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>')
LETTER = re.compile(r'[A-Za-z]')


def sid(text):
    return hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]


def word_line(line):
    s = line.strip()
    if not s or not LETTER.search(TAG.sub('', s)):  # nothing but tags (a <p>, a badge <img>) is not words
        return False
    if re.fullmatch(r'\|?[\s:|-]+\|?', s):  # a table's separator row
        return False
    if re.fullmatch(r'(\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\)\s*)+', s):  # a row of badges
        return False
    if re.fullmatch(r'!\[[^\]]*\]\([^)]*\)', s):  # a picture alone
        return False
    if s.startswith('<!--'):
        return False
    return True


def blocks(text):
    """The README as a list of (kind, text): 'w' a block of words, 'k' kept as it is"""
    lines = text.split('\n')
    out, i, n = [], 0, len(lines)

    def single(s):  # a line that is a block of its own
        t = s.strip()
        return t.startswith(('#', '|', '>', '<')) or not word_line(s)

    while i < n:
        line = lines[i]
        if FENCE.match(line):
            j = i + 1
            while j < n and not FENCE.match(lines[j]):
                j += 1
            out.append(('k', '\n'.join(lines[i:j + 1])))
            i = j + 1
            continue
        if single(line):
            out.append(('w' if word_line(line) and not line.strip().startswith('<!--') else 'k', line))
            i += 1
            continue
        # a paragraph or a list item: its lines until a blank line, a new item, or a line that stands alone
        j = i + 1
        while j < n and lines[j].strip() and not LIST.match(lines[j]) and not single(lines[j]) and not FENCE.match(lines[j]):
            j += 1
        out.append(('w', '\n'.join(lines[i:j])))
        i = j
    return out


def strip_bar(text):
    a = text.find(BAR_START)
    if a < 0:
        return text
    b = text.find(BAR_END, a)
    return (text[:a] + text[b + len(BAR_END):]).lstrip('\n')


def english(repo):
    return strip_bar(Path(repo, 'README.md').read_text(encoding='utf-8').replace('\r\n', '\n'))


def prefix(s):
    # the block's structure only: quote marks, a heading's #s, a list marker, a table's first pipe (not bold or italics)
    m = re.match(r'^\s*((?:>\s*)*)(#+\s|[-*+]\s|\d+\.\s|\|)?', s)
    return (m.group(1) + (m.group(2) or '')).replace(' ', '') if m else ''


def problems(en, tr):
    """What a translation lost: link targets, code spans, tags, its lead (a heading, a list or quote mark), table cells"""
    bad = []
    if sorted(a or b for a, b in LINK_TARGET.findall(en)) != sorted(a or b for a, b in LINK_TARGET.findall(tr)):
        bad.append('links')
    if sorted(CODE.findall(en)) != sorted(CODE.findall(tr)):
        bad.append('code')
    if sorted(TAG.findall(en)) != sorted(TAG.findall(tr)):
        bad.append('tags')
    if prefix(en) != prefix(tr):
        bad.append('lead')
    if en.strip().startswith('|') and en.count('|') != tr.count('|'):
        bad.append('cells')
    if '—' in tr and '—' not in en:  # the house style has no em dashes
        bad.append('em dash')
    return bad


def load(repo, code):
    p = Path(repo, 'i18n', code + '.json')
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}


def bar(current):
    items = []
    for code, name, _ in LANGS:
        href = 'README.md' if code == 'en' else 'README.%s.md' % code
        items.append('<b>%s</b>' % name if code == current else '<a href="%s">%s</a>' % (href, name))
    return '\n'.join([BAR_START, '<p align="center">', '  ' + ' |\n  '.join(items), '</p>', BAR_END])


def cmd_units(repo, code=None):
    en = [t for k, t in blocks(english(repo)) if k == 'w' and not family_bar(t)]
    have = load(repo, code) if code else {}
    need = [{'id': sid(t), 'en': t} for t in en if not (code and sid(t) in have and not problems(t, have[sid(t)]['t']))]
    seen, uniq = set(), []
    for u in need:
        if u['id'] not in seen:
            seen.add(u['id'])
            uniq.append(u)
    print(json.dumps(uniq, ensure_ascii=False, indent=1))


def cmd_check(repo):
    en = [t for k, t in blocks(english(repo)) if k == 'w' and not family_bar(t)]
    ids = {sid(t): t for t in en}
    ok = True
    for code in CODES[1:]:
        tr = load(repo, code)
        if not tr:
            print('%-6s no translation yet' % code)
            continue
        missing = [i for i in ids if i not in tr]
        stale = [i for i in tr if i not in ids]
        broken = [(i, problems(ids[i], tr[i]['t'])) for i in ids if i in tr and problems(ids[i], tr[i]['t'])]
        print('%-6s %d/%d blocks%s%s%s' % (code, len(ids) - len(missing), len(ids),
                                         ', %d missing' % len(missing) if missing else '',
                                         ', %d stale (English changed)' % len(stale) if stale else '',
                                         ', %d broken: %s' % (len(broken), '; '.join('%s %s' % (i, '/'.join(p)) for i, p in broken[:5])) if broken else ''))
        ok = ok and not broken
    return ok


def slug(heading):
    """The anchor GitHub gives a heading: lower case, punctuation dropped, spaces to hyphens"""
    s = re.sub(r'^#+\s*', '', heading.strip()).lower()
    return re.sub(r'[^\w\- ]', '', s).replace(' ', '-')


def cmd_build(repo):
    src = english(repo)
    parts = blocks(src)
    Path(repo, 'README.md').write_text(bar('en') + '\n\n' + src, encoding='utf-8')
    for code, _, rtl in LANGS[1:]:
        tr = load(repo, code)
        if not tr:
            continue
        body = []
        for kind, t in parts:
            if kind == 'w' and family_bar(t):
                body.append(family_tr(t, code))
                continue
            u = tr.get(sid(t)) if kind == 'w' else None
            out = u['t'] if u and not problems(t, u['t']) else t
            if t.startswith('#') and slug(out) != slug(t):  # keep the English #anchor the page's links use
                body.append('<a id="%s"></a>\n' % slug(t))
            body.append(out)
        text = '\n'.join(body)
        head = bar(code) + '\n\n<p align="center"><sub>%s <a href="README.md">English</a></sub></p>\n\n' % NOTE[code]
        if rtl:
            text = '<div dir="rtl">\n\n' + text + '\n\n</div>'
        Path(repo, 'README.%s.md' % code).write_text(head + text + '\n', encoding='utf-8')
        print('README.%s.md' % code)


if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] not in ('units', 'check', 'build'):
        sys.exit(__doc__)
    if sys.argv[1] == 'units':
        cmd_units(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif sys.argv[1] == 'check':
        sys.exit(0 if cmd_check(sys.argv[2]) else 1)
    else:
        cmd_build(sys.argv[2])
