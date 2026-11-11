import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def render():
    corpus = json.loads((ROOT / 'corpus.json').read_text())
    corpus['inputSha256'] = hashlib.sha256((ROOT / 'corpus.json').read_bytes()).hexdigest()
    template = (ROOT / 'page-template.html').read_text()
    assert template.count('__PROBE_INPUT__') == template.count('__PROBE_SCRIPT__') == 1
    return template.replace('__PROBE_INPUT__', json.dumps(corpus, separators=(',', ':')).replace('<', '\\u003c')).replace('__PROBE_SCRIPT__', (ROOT / 'probe.js').read_text())


if __name__ == '__main__':
    (ROOT / 'probe.html').write_text(render())
