import hashlib, json, shutil, subprocess, sys, tempfile, tomllib
from pathlib import Path
sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
ROOT = P.parent.parent
OUT = P / 'verification'; OUT.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args, **kw):
    r = subprocess.run(args, capture_output=True, **kw)
    if r.returncode: raise RuntimeError((args, r.returncode, r.stdout, r.stderr))
    return r
pins = json.loads((P / 'SOURCES.json').read_text())
for name, digest in pins['files'].items():
    data = run(['git', '-c', 'core.fsmonitor=false', 'show', pins['revision'] + ':' + name], cwd=ROOT).stdout
    assert hashlib.sha256(data).hexdigest() == digest and data == (P / 'source' / name).read_bytes()
prior = json.loads((P / 'PREREQUISITE.json').read_text()); origin = ROOT / prior['capsule']
assert sha(origin / 'SOURCE-ONLY.json') == prior['manifest_sha256']
for name, digest in json.loads((origin / 'SOURCE-ONLY.json').read_text()).items(): assert sha(origin / name) == digest
for name, digest in prior['files'].items(): assert sha(P / 'prerequisite' / name) == digest == sha(origin / 'candidate' / name)
roles = json.loads((P / 'ROLES.json').read_text())
assert len(roles) == 4 and sum(r['base'] is None for r in roles) == 1
for row in roles:
    assert sha(P / 'candidate' / row['path']) == row['candidate']
    if row['base']: assert sha(P / 'prerequisite' / row['path']) == row['base']
with tempfile.TemporaryDirectory(prefix='combined-recascade-check-') as temp:
    tree = Path(temp); shutil.copytree(P / 'prerequisite', tree, dirs_exist_ok=True)
    run(['patch', '-p1', '--batch', '-i', str(P / 'driver.patch')], cwd=tree)
    for r in roles: assert (tree / r['path']).read_bytes() == (P / 'candidate' / r['path']).read_bytes()
    run(['patch', '-R', '-p1', '--batch', '-i', str(P / 'driver.patch')], cwd=tree)
    for r in roles:
        if r['base']: assert (tree / r['path']).read_bytes() == (P / 'prerequisite' / r['path']).read_bytes()
        else: assert not (tree / r['path']).exists()
sys.path[:0] = [str(ROOT / 'xpcom/idl-parser'), str(ROOT / 'third_party/python/ply')]
from xpidl import xpidl
idl = P / 'candidate/dom/interfaces/base/nsIDOMWindowUtils.idl'
parsed = xpidl.IDLParser().parse(idl.read_text(), filename=str(idl))
interface = next(x for x in parsed.productions if getattr(x, 'name', None) == 'nsIDOMWindowUtils')
method = [m for m in interface.members if getattr(m, 'name', None) == 'getMissingPseudoCompositedStyleForTesting']
assert len(method) == 1 and len(method[0].params) == 4
manifest = tomllib.loads((P / 'candidate/dom/base/test/mochitest.toml').read_text())
original = tomllib.loads((P / 'prerequisite/dom/base/test/mochitest.toml').read_text())
assert manifest == dict(original, **{'test_missing_pseudo_animation_composed.html': {}})
html = (P / 'test_missing_pseudo_animation_composed.html').read_text()
assert html == (P / 'candidate/dom/base/test/test_missing_pseudo_animation_composed.html').read_text()
inv = run(['node', str(P / 'inventory.cjs')], text=True, cwd=ROOT).stdout
assert inv == (P / 'ASSERTIONS.json').read_text()
a = json.loads(inv); rows = [r for t in a['tasks'] for r in t['assertions']]
assert a['assertion_count'] == 122 and len(a['tasks']) == 5
assert sum(r['classification'] == 'setup' for r in rows) == 33
assert sum(r['classification'] == 'probe' for r in rows) == 3
run(['node', '--check'], input=html.split('<script>')[1].split('</script>')[0], text=True)
for label, args in [('eslint', [str(ROOT / 'node_modules/.bin/eslint'), '--stdin', '--stdin-filename', 'dom/base/test/test_missing_pseudo_animation_composed.html', '--rule', 'mozilla/import-globals: off']), ('prettier', [str(ROOT / 'node_modules/.bin/prettier'), '--stdin-filepath', 'dom/base/test/test_missing_pseudo_animation_composed.html'])]:
    r = run(args, input=html, text=True, cwd=ROOT)
    (OUT / (label + '.stdout')).write_text(r.stdout); (OUT / (label + '.stderr')).write_text(r.stderr)
    if label == 'prettier': assert r.stdout == html
body = (P / 'driver.cpp').read_text()
assert body.count('RecascadeStyleForMissingPseudo(') == 1
assert body.index('RecascadeStyleForMissingPseudo(') > body.index('const bool admitted = compositor->ComposeServoAnimationRulesForMissingPseudo(')
assert body.index('  unchanged &= sameEffects();') > body.index('RecascadeStyleForMissingPseudo(')
assert body in (P / 'candidate/dom/base/nsDOMWindowUtils.cpp').read_text()
report = {'status': 'PASS', 'git_pins': len(pins['files']), 'prerequisite_files': 3, 'changed_or_new_files': 4, 'tasks': 5, 'assertions': 122, 'setup_checks': 33, 'interpretation_probes': 3, 'patch_forward_reverse': True, 'xpidl_syntax': True, 'xpidl_type_resolution': False, 'inert_js_syntax': True, 'scoped_eslint': True, 'eslint_import_globals_disabled': True, 'prettier_idempotent': True, 'native_build': False, 'browser_execution': False, 'patch_sha256': sha(P / 'driver.patch')}
(OUT / 'REPORT.json').write_text(json.dumps(report, indent=2) + '\n'); print(json.dumps(report, indent=2))
