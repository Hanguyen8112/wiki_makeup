#!/usr/bin/env python3
# sync.py -- Dong bo note/*.md --> makeup-wiki.html
#
# Cach dung:
#   python sync.py           # sync mot lan
#   python sync.py --watch   # tu dong sync khi file .md thay doi

import re
import sys
import time
import html as html_mod
from pathlib import Path

BASE      = Path(__file__).parent
NOTE_DIR  = BASE / "note"
HTML_FILE = BASE / "makeup-wiki.html"

# Mapping: ten file MD (khong co .md) --> id trong SYNC marker
PAGES = {
    "01. Lớp học cá nhân/buoi-1-danh-nen":         "c1",
    "01. Lớp học cá nhân/buoi-2-tao-khoi-ma-hong": "c2",
    "01. Lớp học cá nhân/buoi-3":                  "c3",
    "01. Lớp học cá nhân/buoi-4":                  "c4",
    "01. Lớp học cá nhân/buoi-5":                  "c5",
    "03. Sản phẩm/Makeup":                          "san-pham-makeup",
    "03. Sản phẩm/Skincare":                        "san-pham-skincare",
    "04. Hồ sơ cá nhân/Khuôn mặt và da":           "profile",
    "04. Hồ sơ cá nhân/Routine":                    "routine",
}

EMPTY_STATE = (
    '<div class="empty">'
    '<span class="ico">📝</span>'
    '<p>Chưa có ghi chú. Gửi notes sau buổi học để mình tổng hợp.</p>'
    '</div>'
)


def inline(text):
    """**bold**, *italic*, `code` --> HTML. Escape HTML entities truoc."""
    text = html_mod.escape(text, quote=False)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


def box_class(text):
    """Xac dinh class CSS cho blockquote dua tren emoji."""
    if '⚠️' in text: return 'warn'   # ⚠️
    if '\U0001f4a1' in text: return 'tip'       # 💡
    if any(e in text for e in ['\U0001f49b', '✨', '\U0001f31f', '\U0001f33f']):
        return 'gold'                           # 💛 ✨ 🌟 🌿
    return 'note'


def render_table(lines):
    rows = []
    for line in lines:
        s = line.strip()
        if not s or re.match(r'^\|[-| :]+\|$', s):
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        rows.append(cells)
    if not rows:
        return ''
    head, body = rows[0], rows[1:]
    th  = ''.join('<th>' + inline(c) + '</th>' for c in head)
    trs = '<tr>' + th + '</tr>'
    for row in body:
        td   = ''.join('<td>' + inline(c) + '</td>' for c in row)
        trs += '<tr>' + td + '</tr>'
    return '<div class="tw"><table class="t">' + trs + '</table></div>'


def md_to_html(md_text):
    lines = md_text.splitlines()
    out   = []
    i     = 0

    while i < len(lines):
        line = lines[i]
        raw  = line.strip()

        # Bo qua H1
        if re.match(r'^# [^#]', line):
            i += 1
            continue

        # Bo qua metadata front matter
        if re.match(r'^\*\*[^*]+:\*\*', line):  # bo qua dong metadata **Key:** Value
            i += 1
            continue

        # HR
        if re.match(r'^-{3,}$', raw):
            i += 1
            continue

        # HTML comment
        if raw.startswith('<!--'):
            i += 1
            continue

        # H2
        if line.startswith('## '):
            out.append('<h2 class="sec">' + inline(line[3:]) + '</h2>')
            i += 1
            continue

        # H3
        if line.startswith('### '):
            out.append('<h3 class="sub">' + inline(line[4:]) + '</h3>')
            i += 1
            continue

        # Blockquote
        if line.startswith('> '):
            bq = []
            while i < len(lines) and lines[i].startswith('> '):
                bq.append(lines[i][2:].rstrip())
                i += 1
            full = ' '.join(bq)
            cls  = box_class(full)
            parts = []
            for b in bq:
                # Xoa emoji box (+ variation selector U+FE0F) khoi noi dung hien thi
                b = re.sub(
                    r'^[⚠\U0001f4a1\U0001f49b✨\U0001f31f\U0001f33f\U0001f4dd]️?\s*',
                    '', b
                )
                if b.strip():
                    parts.append(inline(b))
            inner = '<br>'.join(parts)
            out.append('<div class="box ' + cls + '">' + inner + '</div>')
            continue

        # Image ![alt](src)
        img_m = re.match(r'^!\[(.+?)\]\((.+?)\)$', raw)
        if img_m:
            alt = html_mod.escape(img_m.group(1))
            src = img_m.group(2)
            out.append(
                '<div class="illus">'
                '<img src="' + src + '" alt="' + alt + '" style="max-width:100%;border-radius:8px;">'
                '<div class="illus-cap">' + alt + '</div>'
                '</div>'
            )
            i += 1
            continue

        # Table
        if raw.startswith('|'):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tbl.append(lines[i])
                i += 1
            out.append(render_table(tbl))
            continue

        # Unordered list
        if re.match(r'^[-*] ', line):
            items = []
            while i < len(lines) and re.match(r'^[-*] ', lines[i]):
                items.append('<li>' + inline(lines[i][2:]) + '</li>')
                i += 1
            out.append('<ul class="bul">' + ''.join(items) + '</ul>')
            continue

        # Ordered list
        if re.match(r'^\d+\. ', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                text = re.sub(r'^\d+\. ', '', lines[i])
                items.append('<li>' + inline(text) + '</li>')
                i += 1
            out.append('<ol class="steps">' + ''.join(items) + '</ol>')
            continue

        # Dong trong
        if not raw:
            i += 1
            continue

        # Paragraph
        out.append('<p>' + inline(line) + '</p>')
        i += 1

    return '\n'.join(out)


def sync_all(verbose=True):
    html    = HTML_FILE.read_text(encoding='utf-8')
    changed = False

    for stem, sync_id in PAGES.items():
        md_file = NOTE_DIR / (stem + '.md')
        if not md_file.exists():
            continue

        md_text = md_file.read_text(encoding='utf-8')
        body    = md_to_html(md_text).strip()
        if not body:
            body = EMPTY_STATE

        s_marker = '<!-- SYNC:' + sync_id + ' -->'
        e_marker = '<!-- /SYNC:' + sync_id + ' -->'
        pat = re.compile(
            re.escape(s_marker) + r'.*?' + re.escape(e_marker),
            re.DOTALL
        )

        if not pat.search(html):
            if verbose:
                print('  ! Marker khong tim thay: ' + sync_id + ' -- bo qua')
            continue

        replacement = s_marker + '\n' + body + '\n' + e_marker
        new_html    = pat.sub(replacement, html)

        if new_html != html:
            html    = new_html
            changed = True
            if verbose:
                print('  OK ' + stem + '.md --> #' + sync_id)

    if changed:
        HTML_FILE.write_text(html, encoding='utf-8')
        if verbose:
            print('  --> makeup-wiki.html da duoc cap nhat\n')
    elif verbose:
        print('  --> Khong co thay doi\n')


def watch():
    print('Dang theo doi thu muc note/ ... (Ctrl+C de dung)\n')
    mtimes = {}
    for f in NOTE_DIR.rglob('*.md'):
        mtimes[f] = f.stat().st_mtime

    while True:
        time.sleep(1)
        for f in NOTE_DIR.rglob('*.md'):
            try:
                mtime = f.stat().st_mtime
            except FileNotFoundError:
                continue
            if mtimes.get(f) != mtime:
                print('[' + time.strftime('%H:%M:%S') + '] ' + f.name + ' thay doi')
                sync_all()
                mtimes[f] = mtime


if __name__ == '__main__':
    sync_all()
    if '--watch' in sys.argv or '-w' in sys.argv:
        watch()
