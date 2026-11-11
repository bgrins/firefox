import hashlib
import json
from pathlib import Path
import subprocess
from html.parser import HTMLParser

r = Path(__file__).resolve().parent
m = json.loads((r / 'SOURCES.json').read_text())
for path, expected in m['files'].items():
    data = (r / 'source' / path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected
    assert data == subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', m['revision'] + ':' + path], cwd=r.parent.parent)

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ['id', 'name']:
                self.ids.add(value)

for name, receipt in json.loads((r / 'HTML-ANCHORS.json').read_text()).items():
    raw = (r / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == receipt['sha256']
    parser = Anchors()
    parser.feed(raw.decode(receipt['encoding']))
    assert set(receipt['validated_anchors']) <= parser.ids
for i in range(7):
    assert '"exists": true' in (r / f'anchor-{i}.txt').read_text()
trace = (r / 'trace-accumulation.md').read_text()
assert 'Found 1 trace(s).' in trace and 'Search was truncated' not in trace
assert 'step 12.2' in trace
assert '**Verdict: REACHED**' in (r / 'CSS-TRACE.md').read_text()
assert '**Verdict: INCONCLUSIVE**' in (r / 'SVG-TRACE.md').read_text()
print(json.dumps({'result': 'PASS', 'native_and_test_pins': len(m['files']), 'indexed_css_anchors': 7, 'direct_html_anchors': 6, 'css_accumulation_route': 'one untruncated step route', 'svg_graph_exhaustiveness_claimed': False, 'runtime_executed': False, 'new_bug_count': 0}, indent=2))
