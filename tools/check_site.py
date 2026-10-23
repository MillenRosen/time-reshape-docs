"""Check generated internal pages, fragments, images and scripts without network access."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.missing_alt = set(), [], 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if attr.get('id'):
            self.ids.add(attr['id'])
        if tag == 'img' and 'alt' not in attr:
            self.missing_alt += 1
        for key in ('href', 'src'):
            if attr.get(key):
                self.links.append(attr[key])


root = Path(sys.argv[1] if len(sys.argv) > 1 else 'build/html').resolve()
pages = {p.resolve(): Page(p.read_text(encoding='utf-8')) for p in root.rglob('*.html')}
assert pages, 'No HTML output'
errors, checked = [], 0
for path, page in pages.items():
    if re.search(r'\{\{\s*(?:version|build|apk_\w+|download_url|preview_url)\s*\}\}', path.read_text(encoding='utf-8')):
        errors.append(f'{path.relative_to(root)}: unresolved release metadata')
    if page.missing_alt:
        errors.append(f'{path.relative_to(root)}: image without alt attribute')
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        if url.path.startswith('/'):
            errors.append(f'{path.relative_to(root)}: root-relative URL breaks versioned hosting: {link}')
            continue
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        if target.is_dir():
            target /= 'index.html'
        if not target.is_relative_to(root) or not target.exists():
            errors.append(f'{path.relative_to(root)}: missing target {link}')
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            errors.append(f'{path.relative_to(root)}: missing fragment {link}')
        checked += 1
for path in root.rglob('*.css'):
    for raw in re.findall(r'url\(([^)]+)\)', path.read_text(encoding='utf-8')):
        url = urlsplit(raw.strip(' \"\''))
        if url.scheme or url.netloc or not url.path:
            continue
        if not (path.parent / unquote(url.path)).resolve().exists():
            errors.append(f'{path.relative_to(root)}: missing CSS resource {raw}')
assert not errors, '\n'.join(errors)
print(json.dumps({'html_pages': len(pages), 'internal_references_checked': checked, 'broken_links': 0,
                  'images_have_alt': True, 'css_resources_present': True}, ensure_ascii=False))
