import hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
WPT = ROOT / 'testing/web-platform/tests'
sys.path[:0] = [str(p) for p in (WPT / 'tools/third_party').iterdir() if p.is_dir()] + [str(WPT / 'tools'), str(WPT), str(ROOT / 'third_party/python/pyyaml/lib')]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint
OUT = P / 'verification'; OUT.mkdir(exist_ok=True)
relative = 'web-animations/animation-model/combining-effects/transition-current-not-in-effect-priority.html'
helper = str(Path(relative).parent / 'resources/transition-routing-probe.js')
resources = {relative: P / 'transition-current-not-in-effect-priority.html', helper: P / 'resources/transition-routing-probe.js', 'resources/testharness.js': WPT / 'resources/testharness.js', 'resources/testharnessreport.js': WPT / 'resources/testharnessreport.js'}
html = html5lib.parse((P / 'transition-current-not-in-effect-priority.html').read_text(), namespaceHTMLElements=False)
scripts = [n.text or '' for n in html.iter('script') if not n.get('src')]
assert len(scripts) == 1
inline = scripts[0]
program = "const vm = require('vm'); let s=''; process.stdin.on('data',c=>s+=c); process.stdin.on('end',()=>{const names=[]; vm.runInNewContext(s,{window:{},promise_test:(_,n)=>names.push(n)}); console.log(JSON.stringify(names));});"
r = subprocess.run(['node', '-e', program], input=inline, text=True, capture_output=True, check=True)
names = json.loads(r.stdout)
assert names == ['Transition-only: important author is overridden by the held transition', 'Active overlap: important author overrides the animation-origin stack', 'Probe: a current non-filling effect does not demote the transition origin']
subprocess.run(['node', '--check'], input=inline, text=True, capture_output=True, check=True)
subprocess.run(['node', '--check', str(P / 'resources/transition-routing-probe.js')], capture_output=True, check=True)
standalone = html5lib.parse((P / 'standalone.html').read_text(), namespaceHTMLElements=False)
for script in standalone.iter('script'):
    if not script.get('src'): subprocess.run(['node', '--check'], input=script.text or '', text=True, capture_output=True, check=True)
with tempfile.TemporaryDirectory(prefix='transition-null-renderer-') as directory:
    tree = Path(directory)
    for name, file in resources.items():
        dest = tree / name; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(file, dest)
    findings = {}
    for name in [relative, helper]:
        findings[name] = lint.check_path(str(tree), name) + lint.check_file_contents(str(tree), name)
    (OUT / 'LINT.json').write_text(json.dumps(findings, indent=2) + '\n')
    assert not any(findings.values()), findings
    manifest = Manifest(str(tree), '/')
    manifest.update([(name, None, True) for name in resources], parallel=False)
    entries = [{'path': path, 'url': item.url} for kind, path, items in manifest if kind == 'testharness' for item in items]
    assert entries == [{'path': relative, 'url': '/' + relative}]
    (OUT / 'MANIFEST.json').write_text(json.dumps(manifest.to_json(), indent=2) + '\n')
assert not tree.exists()
result = {'status': 'PASS', 'callbacks': names, 'controls': 2, 'interpretation_probes': 1, 'observations_per_callback': 4, 'style_reads_per_observation': 3, 'genuine_wpt_lint_and_manifest': True, 'inert_registration': True, 'javascript_syntax': True, 'browser_execution': False, 'scratch_removed': True, 'sources': {str(f.relative_to(P)): hashlib.sha256(f.read_bytes()).hexdigest() for f in [P / 'transition-current-not-in-effect-priority.html', P / 'resources/transition-routing-probe.js', P / 'standalone.html']}}
(OUT / 'REPORT.json').write_text(json.dumps(result, indent=2) + '\n'); print(json.dumps(result, indent=2))
