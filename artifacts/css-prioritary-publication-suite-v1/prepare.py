import hashlib
import json
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / 'testing/web-platform/tests'
sys.path[:0] = [str(p) for p in (WPT / 'tools/third_party').iterdir() if p.is_dir()] + [str(WPT / 'tools'), str(WPT), str(ROOT / 'third_party/python/pyyaml/lib')]
def audit(event, args):
    if event == 'subprocess.Popen':
        assert Path(args[0]).name != 'git'
sys.addaudithook(audit)
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pin = lambda p: {'path': str(p.relative_to(ROOT)), 'sha256': sha(p)}
references = {}
def reference(p):
    references[str(p.relative_to(ROOT))] = {'sha256': sha(p), 'bytes': p.stat().st_size}
def copy(source, target, expected=None):
    if expected is not None:
        assert sha(source) == expected
    reference(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert target.read_bytes() == source.read_bytes()
        return
    with target.open('xb') as stream:
        stream.write(source.read_bytes())

plan = ROOT / 'artifacts/css-prioritary-native-publication-plan-v1'
probe = ROOT / 'artifacts/css-prioritary-line-height-probe-v1'
suite = ROOT / 'artifacts/css-prioritary-selection-suite-v3'
for directory, digest in [(plan, '5228ae65d273767881a223ff4ff8f3eac2874d775e5c3682b2725c20c53bb46a'), (probe, '43f7476d595655ec27903ef18534a060efcf6799751f07b44147c33c4d7850eb')]:
    assert sha(directory / 'FILES.json') == digest
    reference(directory / 'FILES.json')
    for name, claim in read(directory / 'FILES.json').items():
        assert sha(directory / name) == claim['sha256'] and (directory / name).stat().st_size == claim['bytes']
reference(plan / 'PLAN.json')
reference(suite / 'INPUTS.json')
reference(suite / 'ROSTER.json')
source_resources = {}
for row in read(plan / 'PLAN.json')['files']:
    if row['kind'] == 'native':
        continue
    source = ROOT / row.get('proposed', row['source'])
    relative = row['path'].removeprefix('testing/web-platform/')
    copy(source, HERE / relative, row.get('proposed_sha256', row['source_sha256']))
    if row['kind'] != 'metadata':
        url = '/_mozilla/' + relative.removeprefix('mozilla/tests/') if relative.startswith('mozilla/tests/') else '/' + relative.removeprefix('tests/')
        source_resources[url] = pin(source)
page = 'css/css-properties-values-api/registered-overridden-line-height.tentative.html'
copy(probe / Path(page).name, HERE / 'tests' / page)
source_resources['/' + page] = pin(probe / Path(page).name)
for name in ['testharness.js', 'testharnessreport.js']:
    source = suite / 'tests/resources' / name
    copy(source, HERE / 'tests/resources' / name)
    source_resources['/resources/' + name] = pin(source)

old = read(suite / 'INPUTS.json')
for name in ['testharness.js', 'testharnessreport.js']:
    assert sha(HERE / 'tests/resources' / name) == old['resources']['/resources/' + name]['sha256']
metadata = {'portable': {}, 'mozilla': {}}
for kind, names, target in [('portable', ['__dir__.ini', 'css/__dir__.ini', 'css/css-properties-values-api/__dir__.ini', 'forced-colors-mode/__dir__.ini'], 'meta'), ('mozilla', ['__dir__.ini'], 'mozilla/meta')]:
    for name in names:
        record = old['metadata'][kind][name]
        copy(ROOT / record['path'], HERE / target / name, record['sha256'])
for kind, folder in [('portable', 'meta'), ('mozilla', 'mozilla/meta')]:
    for path in (HERE / folder).rglob('*.ini'):
        assert 'expected:' not in path.read_text()
        metadata[kind][str(path.relative_to(HERE / folder))] = pin(path)
for name in ['css/__dir__.ini', 'css/css-cascade/__dir__.ini']:
    metadata['mozilla'][name] = {'path': None, 'sha256': None, 'require_absent_in_staged_root': True}
program = "const vm=require('vm');let input='';process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const names=[];const c=vm.createContext({window:{},test:(_,n)=>names.push(n),promise_test:(_,n)=>names.push(n),promise_setup:()=>{}});for(const s of JSON.parse(input))vm.runInContext(s,c);process.stdout.write(JSON.stringify(names));});"
roster, resources, lint_results = {}, {}, {}
for kind, folder, base, manifest_name in [('portable', 'tests', '/', 'MANIFEST.json'), ('mozilla', 'mozilla/tests', '/_mozilla/', 'MOZILLA-MANIFEST.json')]:
    root = HERE / folder
    paths = sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file())
    errors = []
    for name in paths:
        path = root / name
        resources[base + name] = pin(path)
        if path.suffix == '.html':
            dom = html5lib.parse(path.read_text(), namespaceHTMLElements=False)
            scripts = [node.text or '' for node in dom.iter('script') if not node.get('src')]
            result = subprocess.run(['node', '-e', program], input=json.dumps(scripts), text=True, capture_output=True, check=True)
            names = json.loads(result.stdout)
            assert names and len(set(names)) == len(names)
            roster[base + name] = names
            errors += lint.check_path(str(root), name) + lint.check_file_contents(str(root), name)
    errors += lint.check_unique_testharness_basenames(str(root), paths)
    errors += lint.check_unique_case_insensitive_paths(str(root), paths)
    lint_results[kind] = errors
    manifest = Manifest(str(root), base)
    manifest.update([(name, None, True) for name in paths], parallel=False)
    (HERE / manifest_name).write_text(json.dumps(manifest.to_json(), indent=2, sort_keys=True) + '\n')
assert not lint_results['portable'], lint_results
assert len(lint_results['mozilla']) == 4 and all(row[0] == 'SPECIALPOWERS API' for row in lint_results['mozilla']), lint_results
lanes = {}
for lane, prefix in [('ordinary', '/css/'), ('forced_colors', '/forced-colors-mode/'), ('mozilla_appearance', '/_mozilla/')]:
    subset = {p:names for p,names in roster.items() if p.startswith(prefix)}
    lanes[lane] = {'roster': subset, 'callbacks': sum(map(len, subset.values())), 'pages': len(subset)}
assert [(lanes[k]['callbacks'], lanes[k]['pages']) for k in lanes] == [(20, 3), (2, 1), (6, 2)]
assert len(resources) == 8 and sum(map(len, roster.values())) == 28
for url in roster:
    if not url.startswith('/_mozilla/'):
        metadata['portable'][url[1:] + '.ini'] = {'path': None, 'sha256': None, 'require_absent_in_staged_root': True}
for relative in ['tools/manifest/manifest.py', 'tools/manifest/sourcefile.py', 'tools/lint/lint.py', 'tools/lint/rules.py']:
    reference(WPT / relative)
inputs = {'callbacks': 28, 'pages': 6, 'signatures': 34, 'resources': resources, 'source_resources': source_resources,
          'copy_resources': resources, 'install_managed_resources': {}, 'sealed_resource_count': 8, 'metadata': metadata,
          'manifests': {'portable': pin(HERE / 'MANIFEST.json'), 'mozilla': pin(HERE / 'MOZILLA-MANIFEST.json')},
          'current_binding': None, 'execution': None, 'baseline_outcomes': None, 'expected_statuses': None,
          'candidate_desired_PASS': 28, 'fresh_original_required': True, 'capture_helper': None}
for name, body in [('INPUTS.json', inputs), ('ROSTER.json', roster), ('LANES.json', lanes), ('REFERENCES.json', references), ('LINT.json', lint_results)]:
    (HERE / name).write_text(json.dumps(body, indent=2, sort_keys=True) + '\n')
print(json.dumps({'callbacks': 28, 'pages': 6, 'resources': 8, 'signatures': 34, 'portable_lint': lint_results['portable'], 'mozilla_portable_lint': lint_results['mozilla'], 'genuine_manifests': True, 'browser_execution': False}))
