import ast
import copy
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DRAFT = ROOT / 'artifacts/css-central-baseline-origin-comparison-v1'
SEAL = '2b11bca118b7bbe570e283b36f16c90f5ea0e411509693a229affd03c916e1ea'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def authenticate(base, mapping):
    for name, value in mapping.items():
        p = base / name
        assert not p.is_symlink() and p.is_file() and digest(p) == value, name

assert digest(DRAFT / 'DRAFT-FILES.json') == SEAL
payloads = read(DRAFT / 'DRAFT-FILES.json')
refs = read(DRAFT / 'REFERENCES.json')
authenticate(DRAFT, payloads)
authenticate(ROOT, refs)
for name in ['css-wide-baseline-interface-compile-runtime-v1', 'css-central-baseline-origin-working-v2']:
    p = ROOT / 'artifacts' / name
    authenticate(p, read(p / 'FILES.json'))
c = read(DRAFT / 'CONFIG.json')
resources = read(DRAFT / 'RESOURCES.json')
pins = read(DRAFT / 'TEST-SOURCE-PINS.json')
assert c['ready_for_execution'] is False
assert len(c['sources']) == 32 and len(set(c['sources'])) == 32
assert len(c['guard_sources']) == 44 and set(c['sources']) <= set(c['guard_sources'])
assert set(c['candidate_sources']) == {'layout/base/Baseline.cpp'}
assert len(c['tests']) == len(set(c['tests'])) == 14
assert len(c['existing_tests']) == 61 and len(c['tracked_existing_tests']) == 48
prior = ROOT / 'artifacts/css-wide-baseline-interface-compile-runtime-v1'
prior_config = read(prior / 'CONFIG.json')
for key in ['sources', 'guard_sources', 'source_pins', 'head_pins', 'modified_native_paths',
            'existing_tests', 'existing_test_pins', 'tracked_existing_tests', 'must_be_absent']:
    assert c[key] == prior_config[key], key
assert c['source_pins'] == read(prior / 'FINAL.json')['sources']
for name, value in read(prior / 'RESOURCES.json').items():
    assert resources[name] == value, name
assert len(resources) == 232 and len(pins) == 13
assert set(c['comparison_tests']) == set(pins)
assert set(c['tests']) == set(pins) | set(c['install'])
assert set(c['expected_subtests']) | {c['reference_test']} == {n.removeprefix('testing/web-platform/tests') for n in c['tests']}
for name in c['tests']:
    metadata = name.replace('testing/web-platform/tests/', 'testing/web-platform/meta/') + '.ini'
    assert metadata in resources, metadata
    parent = Path(metadata).parent
    while str(parent) != 'testing/web-platform':
        assert str(parent / '__dir__.ini') in resources, parent
        if str(parent) == 'testing/web-platform/meta':
            break
        parent = parent.parent
owned = next(iter(c['install']))
assert resources[owned] is None
assert digest(DRAFT / 'fixture.html') == refs['artifacts/css-central-baseline-origin-oracle-v2/central-baseline-source-margin-center.html']
authenticate(ROOT, pins)

class Children(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.count = 0
    def handle_starttag(self, tag, attrs):
        if self.stack and self.stack[-1][1]:
            self.count += 1
            assert not dict(attrs).get('title')
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append((tag, 'target' in dict(attrs).get('class', '').split()))
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

counts = {}
for name in pins:
    url = name.removeprefix('testing/web-platform/tests')
    if url == c['reference_test']:
        continue
    source = (ROOT / name).read_text()
    assert "checkLayout('.target > *')" in source
    parser = Children()
    parser.feed(source)
    assert c['expected_subtests'][url] == [f'.target > * {i}' for i in range(1, parser.count + 1)]
    counts[url] = parser.count
assert sum(map(len, c['expected_subtests'].values())) == 216
for name in ['run.py', 'tests.py']:
    ast.parse((DRAFT / name).read_text())
namespace = {}
exec(compile((DRAFT / 'tests.py').read_text(), 'reviewed-tests.py', 'exec'), namespace)
def need(ok, message):
    if not ok:
        raise RuntimeError(message)
saved = {}
wpt = SimpleNamespace(CONFIG=c, need=need, save=lambda n, d: saved.update({n: d}))
rows = [{'test': t, 'subtest': n, 'status': 'PASS', 'message': None, 'expected': 'PASS', 'known_intermittent': []}
        for t, names in c['expected_subtests'].items() for n in names]
base = {'rows': rows, 'ends': [{'test': c['reference_test'], 'status': 'PASS'}]}
namespace['compare'](wpt, base, copy.deepcopy(base))
negative = 0
for kind in ['regression', 'changed_failure', 'main_failure', 'reference_regression']:
    a, b = copy.deepcopy(base), copy.deepcopy(base)
    if kind == 'reference_regression':
        b['ends'][0]['status'] = 'FAIL'
    elif kind == 'changed_failure':
        a['rows'][-1]['status'] = b['rows'][-1]['status'] = 'FAIL'
        a['rows'][-1]['message'] = 'old'
        b['rows'][-1]['message'] = 'changed'
    elif kind == 'main_failure':
        a['rows'][0]['status'] = b['rows'][0]['status'] = 'FAIL'
    else:
        b['rows'][-1]['status'] = 'FAIL'
    try:
        namespace['compare'](wpt, a, b)
    except RuntimeError:
        negative += 1
    else:
        raise AssertionError(kind)
faults = [{'action': 'crash'}, {'action': 'suite_abort'}, {'action': 'test_abort'},
          {'action': 'log', 'level': 'ERROR'}, {'action': 'log', 'level': 'CRITICAL'},
          {'action': 'process_exit', 'exitcode': 1},
          {'action': 'process_output', 'data': 'TEST-UNEXPECTED-TIMEOUT'},
          {'action': 'assertion_count', 'count': 1, 'min_expected': 0, 'max_expected': 0}]
assert all(namespace['infrastructure_faults']([e]) for e in faults)
result = {'status': 'PASS', 'draft_sha256': SEAL, 'payloads': len(payloads), 'refs': len(refs),
          'sources': 32, 'guards': 44, 'resources': 232, 'files': 14, 'subtests': 216,
          'derived_counts': counts, 'comparison_rejection_checks': negative,
          'infrastructure_rejection_checks': len(faults), 'controller_executed': False,
          'native_browser_build_index_actions': False}
(HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
