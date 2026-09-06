"""Rebuild the self-contained HTML from the editable offline viewer (stdlib only)."""
from pathlib import Path
import base64
import json
import mimetypes
import re

ROOT = Path(__file__).resolve().parents[1]

def data_uri(relative):
    file = (ROOT / relative).resolve()
    if not file.is_relative_to(ROOT):
        raise ValueError(f'Resource is outside the project: {relative}')
    mime = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
    return 'data:' + mime + ';base64,' + base64.b64encode(file.read_bytes()).decode()

html = (ROOT / 'index.html').read_text()
css = (ROOT / 'styles.css').read_text()
css = re.sub(r'url\(([\"\']?)(assets/[^)\"\']+)\1\)', lambda m: 'url("' + data_uri(m[2]) + '")', css)
html = re.sub(r'(src|srcset|href|xlink:href)="(assets/[^"]+)"', lambda m: m[1] + '="' + data_uri(m[2]) + '"', html)
html, styles = re.subn(r'<link\b[^>]*href="styles.css"[^>]*>', lambda _: '<style>\n' + css + '\n</style>', html)
app = (ROOT / 'app.js').read_text()
html, scripts = re.subn(r'<script\b[^>]*src="app.js"[^>]*></script>', lambda _: '<script>document.addEventListener("DOMContentLoaded", () => {\n' + app + '\n});</script>', html)
assert styles == scripts == 1, 'Expected one stylesheet and one viewer script'
notices = {file.name: file.read_text() for file in sorted((ROOT / 'licenses').glob('*.txt'))}
notices['brand_assets'] = 'Simpaisa and payment-provider names and logos remain the property and trademarks of their respective owners. This export grants no new rights to those brand assets.'
html = html.replace('</head>', '<script type="application/json" id="third-party-notices">' + json.dumps(notices).replace('<', '\\u003c') + '</script>\n</head>', 1)
output = ROOT / 'simpaisa-network-playbook.html'
output.write_text(html)
print(f'Rebuilt {output.name} ({output.stat().st_size:,} bytes)')
