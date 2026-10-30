import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urljoin

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WPT = ROOT / 'testing/web-platform/tests'
sys.path[:0] = [str(p) for p in (WPT / 'tools/third_party').iterdir() if p.is_dir()] + [str(WPT / 'tools'), str(WPT)]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (PACKAGE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


existing = [
    'AnimationEffect-updateTiming.tentative.html',
    'CSSAnimation-canceling.tentative.html',
    *[f'animation-base-response-00{i}.html' for i in range(1, 5)],
    'parsing/animation-duration-computed.html',
    'animation-duration-infinite.html',
    'css-duration-reactivation.html',
]
pages = ['css/css-animations/' + name for name in existing]
providers = {path: WPT / path for path in pages}
original = ROOT / 'artifacts/css-contextual-duration-animated-input-probe-v1'
assert digest(original / 'FILES.json') == 'a73d8cabfff91548ba14b9f8401194b611f7d35ebb7b115938e0e772bd7876c8'
for name, record in json.loads((original / 'FILES.json').read_text()).items():
    assert digest(original / name) == record['sha256']
for provider in [original / 'animation-duration-animated-inherited-font.tentative.html',
                 PACKAGE / 'animation-duration-animated-input-regressions.tentative.html',
                 PACKAGE / 'animation-duration-self-feedback-observation.tentative.html']:
    path = 'css/css-animations/' + provider.name
    pages.append(path)
    providers[path] = provider

records = []
absences = []


def capture(source, destination):
    assert source.is_file() and not source.is_symlink(), source
    target = PACKAGE / destination
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    assert digest(source) == digest(target)
    records.append({'source': str(source.relative_to(ROOT)), 'capture': destination,
                    'sha256': digest(target), 'bytes': target.stat().st_size})


scripts = {}
resources = set()
references = set()
for path in pages:
    capture(providers[path], 'capture/tests/' + path)
    document = html5lib.parse(providers[path].read_text(), namespaceHTMLElements=False)
    scripts[path] = []
    for node in document.iter('script'):
        if node.get('src'):
            resource = urljoin('/' + path, node.get('src')).lstrip('/')
            assert ':' not in resource and '..' not in Path(resource).parts
            resources.add(resource)
            scripts[path].append({'resource': resource})
        elif node.get('type') != 'application/json':
            scripts[path].append({'inline': node.text or ''})
    for node in document.iter('link'):
        if node.get('rel') in {'match', 'mismatch'}:
            references.add(urljoin('/' + path, node.get('href')).lstrip('/'))
assert references == {'css/css-animations/animation-duration-infinite-ref.html'}
assert resources == {'resources/testharness.js', 'resources/testharnessreport.js',
                     'css/css-animations/support/testcommon.js', 'css/support/computed-testcommon.js'}
for path in sorted(resources | references):
    capture(WPT / path, 'capture/tests/' + path)

auxiliary = set()
for path in pages + sorted(resources | references):
    auxiliary.add(('tests', path + '.headers'))
    if path in pages:
        auxiliary.add(('meta', path + '.ini'))
    for parent in Path(path).parents:
        auxiliary.add(('tests', str(parent / '__dir__.headers')))
        if path in pages:
            auxiliary.add(('meta', str(parent / '__dir__.ini')))
for tree, path in sorted(auxiliary):
    source = ROOT / 'testing/web-platform' / tree / path
    if source.exists():
        capture(source, 'capture/' + tree + '/' + path)
    else:
        assert not source.is_symlink()
        absences.append(str(source.relative_to(ROOT)))

program = """const vm=require('vm');let input='';process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const names=[],context=vm.createContext({test:(fn,name)=>names.push(name),promise_test:(fn,name)=>names.push(name)});try{for(const script of JSON.parse(input))vm.runInContext(script.code,context,{filename:script.path,timeout:1000});process.stdout.write(JSON.stringify({complete:true,names}));}catch(error){process.stdout.write(JSON.stringify({complete:false,names:null,error:String(error),registered_before_error:names.length}));}});"""
roster = {}
for path, entries in scripts.items():
    if path.endswith('animation-duration-infinite.html'):
        continue
    inputs = []
    for index, entry in enumerate(entries):
        resource = entry.get('resource')
        if resource in {'resources/testharness.js', 'resources/testharnessreport.js'}:
            continue
        inputs.append({'path': resource or path + ':inline:' + str(index),
                       'code': (WPT / resource).read_text() if resource else entry['inline']})
    result = subprocess.run(['node', '-e', program], input=json.dumps(inputs), text=True,
                            capture_output=True, check=True)
    row = json.loads(result.stdout)
    if row['complete']:
        assert all(isinstance(name, str) for name in row['names'])
        assert len(row['names']) == len(set(row['names']))
        row['count'] = len(row['names'])
    roster['/' + path] = row
for path, count in [('/css/css-animations/animation-duration-animated-inherited-font.tentative.html', 3),
                    ('/css/css-animations/animation-duration-animated-input-regressions.tentative.html', 5),
                    ('/css/css-animations/animation-duration-self-feedback-observation.tentative.html', 2),
                    ('/css/css-animations/css-duration-reactivation.html', 6)]:
    assert roster[path]['complete'] and roster[path]['count'] == count

with tempfile.TemporaryDirectory(prefix='duration-regression-static-') as temporary:
    scratch = Path(temporary)
    shutil.copytree(PACKAGE / 'capture/tests', scratch, dirs_exist_ok=True)
    (scratch / 'lint.ignore').write_text('')
    manifest = Manifest(str(scratch), '/')
    manifest.update([(path, None, True) for path in pages], parallel=False)
    serialized = json.loads(json.dumps(manifest.to_json()))
    def leaf_count(tree):
        return sum(leaf_count(value) if isinstance(value, dict) else 1 for value in tree.values())
    assert leaf_count(serialized['items']['testharness']) == 11
    assert leaf_count(serialized['items']['reftest']) == 1
    save('SUBSET-MANIFEST.json', serialized)
    old_directory = os.getcwd()
    try:
        os.chdir(scratch)
        authored = [path for path in pages if path not in providers or providers[path].is_relative_to(PACKAGE)]
        assert len(authored) == 2
        assert lint.lint(str(scratch), authored, 'normal', jobs=1) == 0
    finally:
        os.chdir(old_directory)

for record in records:
    assert digest(ROOT / record['source']) == record['sha256']
save('CAPTURE.json', {'pages': ['/' + path for path in pages], 'files': records,
                      'absent_paths': absences, 'reftests': ['/css/css-animations/animation-duration-infinite.html']})
save('ROSTER.json', {'pages': roster, 'aggregate_callback_count': None,
                     'callbacks_executed': False, 'dom_mocks': False,
                     'measurement_only_callbacks': 2, 'reftest_pages': 1})
save('REFERENCES.json', {str((original / 'FILES.json').relative_to(ROOT)): digest(original / 'FILES.json'),
                         'artifacts/css-contextual-duration-animation-only-proposal-v1/FILES.json':
                         digest(ROOT / 'artifacts/css-contextual-duration-animation-only-proposal-v1/FILES.json')})
result = {'pages': 12, 'testharness_pages': 11, 'reftest_pages': 1,
          'captured_regular_files': len(records), 'capture_bytes': sum(row['bytes'] for row in records),
          'known_rosters': {path: row['count'] for path, row in roster.items() if row['complete']},
          'unknown_rosters': [path for path, row in roster.items() if not row['complete']],
          'authored_lint_errors': 0, 'callbacks_executed': False, 'scratch_removed': True}
save('CHECK.json', result)
print(json.dumps(result))
