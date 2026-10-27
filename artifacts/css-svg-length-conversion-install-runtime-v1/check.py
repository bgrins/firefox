import ast
import hashlib
import importlib.util
import json
import stat
import sys
from pathlib import Path

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def auth(mapping, base):
    for n, h in mapping.items():
        assert not Path(n).is_absolute() and '..' not in Path(n).parts
        assert stat.S_ISREG((base / n).lstat().st_mode) and sha(base / n) == h, n
c = read(HERE / 'CONFIG.json')
assert c['ready_for_execution'] is False
assert all(c[n] is None for n in ('epoch', 'epoch_manifest_sha256', 'epoch_receipt', 'acceptance', 'acceptance_sha256', 'acceptance_receipt'))
auth(read(HERE / 'REFERENCES.json'), ROOT)
proposal = ROOT / c['proposal']
auth(read(proposal / 'FILES.json'), proposal)
comp = ROOT / 'artifacts/css-svg-length-conversion-comparison-v1'
auth(read(comp / 'DRAFT-FILES.json'), comp)
cc = read(comp / 'CONFIG.json')
assert c['source_pins'] == cc['source_pins'] and c['guard_sources'] == cc['guard_sources'] and len(c['guard_sources']) == 52
assert c['modified_native_paths'] == cc['modified_native_paths'] and len(c['modified_native_paths']) == 27
sp = read(proposal / 'SOURCE-PINS.json')
assert set(c['sources']) == set(c['candidate_sources']) == set(sp) and len(sp) == 2
assert c['candidate_pins'] == {n:v['candidate_sha256'] for n,v in sp.items()}
for n,v in sp.items():
    assert c['source_pins'][n] == v['before_sha256'] and sha(ROOT / c['candidate_sources'][n]) == v['candidate_sha256']
main = next(iter(c['install']))
assert len(c['install']) == len(c['tests']) == len(c['main_tests']) == len(c['expected_subtests']) == 1
assert c['expected_subtests'][c['main_tests'][0]] == read(proposal / 'EXPECTED-TESTS.json') and len(read(proposal / 'EXPECTED-TESTS.json')) == 9
assert (HERE / 'fixture.html').read_bytes() == (proposal / 'candidate' / main).read_bytes()
assert read(HERE / 'RESOURCES.json') == read(comp / 'RESOURCES.json')
resources = read(HERE / 'RESOURCES.json')
assert resources[main] is None and resources['testing/web-platform/meta/' + main.removeprefix('testing/web-platform/tests/') + '.ini'] is None
assert len(c['installed_tests']) == len(c['existing_tests']) == 3
for directory in ('css-cssom-client-install-runtime-v1', 'css-cssom-offset-scroll-install-runtime-v1', 'css-hidden-svg-matrix-install-runtime-v1'):
    epoch = ROOT / 'artifacts' / directory
    auth(read(epoch / 'FILES.json'), epoch)
    i = read(epoch / 'INSTALLATION.json'); n = i['owned_test']
    assert c['installed_tests'][n] == {'identity':i['owned_test_identity'], 'sha256':i['owned_test_sha256']}
    assert c['existing_test_pins'][n] == resources[n] == i['owned_test_sha256']
for name in ('run.py','check.py'):
    compile((HERE / name).read_text(),name,'exec')
base = ROOT / 'artifacts/css-hidden-svg-matrix-install-runtime-v1/run.py'
def fn(path, name):
    return next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == name)
old = ast.unparse(fn(base,'replace_source')).replace('.svg-install.tmp','.svg-length-install.tmp')
assert old == ast.unparse(fn(HERE / 'run.py','replace_source'))
spec = importlib.util.spec_from_file_location('length_install_tests', comp / 'tests.py')
tests = importlib.util.module_from_spec(spec);spec.loader.exec_module(tests)
class Wpt:
    CONFIG = c
    @staticmethod
    def need(ok, message):
        if not ok: raise RuntimeError(message)
rows = [{'test':t,'subtest':n,'status':'PASS'} for t,names in c['expected_subtests'].items() for n in names]
tests.require_phase(Wpt,'candidate',{'rows':rows,'ends':[]})
negative = 0
for i in range(9):
    changed = [dict(r) for r in rows]; changed[i]['status'] = 'FAIL'
    try: tests.require_phase(Wpt,'candidate',{'rows':changed,'ends':[]})
    except RuntimeError: negative += 1
    else: raise AssertionError(i)
receipt = {'disabled':True,'future_epoch_and_acceptance_unbound':True,'guards':52,'preserved_native_paths':27,
           'candidate_native_paths':2,'installed_existing_tests':3,'new_owned_wpt':1,'main_rows':9,
           'resources':len(resources),'exact_fixture':True,'source_replacement_ast_same_except_tempname':True,
           'nine_candidate_failure_controls_rejected':negative,'python_syntax':True,'executed_native_build_browser_lint':False}
(HERE / 'STATIC-CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
