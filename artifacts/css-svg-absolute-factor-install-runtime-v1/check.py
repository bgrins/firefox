import ast
import hashlib
import importlib.util
import json
import stat
import sys
from pathlib import Path
from types import SimpleNamespace

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
assert all(c[n] is not None for n in ('epoch', 'epoch_manifest_sha256', 'epoch_receipt', 'acceptance', 'acceptance_sha256', 'acceptance_receipt'))
epoch_dir = ROOT / c['epoch']
assert sha(epoch_dir / 'FILES.json') == c['epoch_manifest_sha256']
auth(read(epoch_dir / 'FILES.json'), epoch_dir)
epoch, receipt = read(epoch_dir / 'STATE.json'), read(epoch_dir / 'ROOT-FINAL-CHECK.json')
assert epoch['status'] == 'terminal' and epoch['restored'] and epoch['restore_build_exit'] == 0
assert epoch['recovery_errors'] == [] and 'failure' not in epoch and epoch['paired_preservation_passed']
assert set(epoch['phases']) == {'baseline','candidate'} and all(p['build_exit'] == 0 for p in epoch['phases'].values())
assert receipt == c['epoch_receipt'] and receipt['status'] == 'RESTORED_VERIFIED' and receipt['exit'] == 0
assert receipt['state_sha256'] == sha(epoch_dir / 'STATE.json') and receipt['final_sha256'] == sha(epoch_dir / 'FINAL.json')
assert receipt['final_pins_sha256'] == sha(epoch_dir / 'FINAL-PINS.json')
assert receipt['restored_binary_pins'] == epoch['restored_binary_pins']
final = read(epoch_dir / 'FINAL.json')
assert final == read(epoch_dir / 'BEFORE.json') and final['sources'] == c['source_pins']
assert read(epoch_dir / 'FINAL-PINS.json') == {**read(epoch_dir / 'RESOURCES.json'), **final['sources'], **epoch['restored_binary_pins']}
assert c['installed_tests'] == receipt['installed_tests'] == read(epoch_dir / 'CONFIG.json')['epoch_receipt']['installed_tests']
acceptance = ROOT / c['acceptance']
assert sha(acceptance) == c['acceptance_sha256'] and read(acceptance) == c['acceptance_receipt']
assert c['acceptance_receipt']['status'] == 'SCOPED_ACCEPTED' and c['acceptance_receipt']['fix'] == 115
assert c['acceptance_receipt']['runtime_files_sha256'] == c['epoch_manifest_sha256']
assert c['acceptance_receipt']['patch']['sha256'] == sha(ROOT / c['proposal'] / 'standalone.patch')
assert c['acceptance_receipt']['native_paths'] == c['sources'] + list(c['install'])
assert (HERE / 'run.py').read_bytes() == (ROOT / 'artifacts/css-svg-absolute-factor-install-v1/run.py').read_bytes()
auth(read(HERE / 'REFERENCES.json'), ROOT)
proposal = ROOT / c['proposal']
auth(read(proposal / 'FILES.json'), proposal)
comp = ROOT / 'artifacts/css-svg-absolute-factor-comparison-v1'
auth(read(comp / 'DRAFT-FILES.json'), comp)
cc = read(comp / 'CONFIG.json')
assert c['source_pins'] == cc['source_pins'] and c['guard_sources'] == cc['guard_sources'] and len(c['guard_sources']) == 53
assert c['modified_native_paths'] == cc['modified_native_paths'] and len(c['modified_native_paths']) == 29
assert c['sources'] == ['dom/svg/SVGLength.cpp']
assert c['candidate_pins'] == cc['candidate_pins'] and c['candidate_sources'] == cc['candidate_sources']
assert c['source_pins']['dom/svg/SVGLength.cpp'] == sha(proposal / 'original-SVGLength.cpp')
assert c['candidate_pins']['dom/svg/SVGLength.cpp'] == sha(proposal / 'candidate-SVGLength.cpp')
assert c['install'] == cc['install'] and len(c['install']) == 2
assert c['expected_subtests'] == {t:cc['expected_subtests'][t] for t in cc['main_tests']}
assert sum(map(len,c['expected_subtests'].values())) == 16
assert set(c['tests']) == set(c['install'])
resources = read(HERE / 'RESOURCES.json')
assert resources == read(comp / 'RESOURCES.json')
assert resources['testing/web-platform/meta/svg/animations/__dir__.ini'] is None
for name, fixture in c['install'].items():
    assert (HERE / fixture).read_bytes() == (proposal / c['proposal_test_files'][name]).read_bytes()
    assert resources[name] is None
    assert resources['testing/web-platform/meta/' + name.removeprefix('testing/web-platform/tests/') + '.ini'] is None
assert c['installed_tests'] == cc['epoch_receipt']['installed_tests'] and len(c['installed_tests']) == 5
assert c['existing_tests'] == cc['existing_tests'] and c['existing_test_pins'] == cc['existing_test_pins']
assert not set(c['install']) & set(c['existing_tests'])
for n, v in c['installed_tests'].items():
    assert resources[n] == c['existing_test_pins'][n] == v['sha256']
for n in ('run.py','check.py'):
    compile((HERE / n).read_text(),n,'exec')
old = ROOT / 'artifacts/css-svg-length-conversion-install-v1/run.py'
def function(path, name):
    return next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name == name)
assert ast.unparse(function(old,'replace_source')).replace('.svg-length-install.tmp','.svg-factor-install.tmp') == ast.unparse(function(HERE / 'run.py','replace_source'))
spec = importlib.util.spec_from_file_location('factor_install_tests', comp / 'tests.py')
tests = importlib.util.module_from_spec(spec);spec.loader.exec_module(tests)
class Wpt:
    CONFIG = c
    @staticmethod
    def need(ok,message):
        if not ok: raise RuntimeError(message)
rows = [{'test':t,'subtest':n,'status':'PASS'} for t,names in c['expected_subtests'].items() for n in names]
tests.require_phase(Wpt,'candidate',{'rows':rows,'ends':[]})
negative = 0
for i in range(16):
    changed = [dict(r) for r in rows];changed[i]['status'] = 'FAIL'
    try: tests.require_phase(Wpt,'candidate',{'rows':changed,'ends':[]})
    except RuntimeError: negative += 1
    else: raise AssertionError(i)
# Replay the actual per-test cleanup loop with an injected first-test replacement.
tree = ast.parse((HERE / 'run.py').read_text())
loop = next(n for n in ast.walk(tree) if isinstance(n,ast.For) and ast.unparse(n.iter) == 'owned_identities.items()')
class File:
    def __init__(self, inode): self.inode, self.removed = inode, False
    def lstat(self): return SimpleNamespace(st_mode=stat.S_IFREG,st_dev=1,st_ino=self.inode)
    def unlink(self): self.removed = True
class FakeRoot:
    def __init__(self, files): self.files = files
    def __truediv__(self, name): return self.files[name]
checks = 0
for replaced in (False,True):
    files = {'first':File(99 if replaced else 1),'second':File(2)}
    scope = {'ROOT':FakeRoot(files),'owned_identities':{'first':(1,1),'second':(1,2)},'stat':stat,'need':Wpt.need,'errors':[]}
    exec(compile(ast.Module(body=[loop],type_ignores=[]),'owned cleanup','exec'),scope)
    assert files['second'].removed and files['first'].removed == (not replaced)
    assert len(scope['errors']) == int(replaced)
    checks += 1
receipt = {'disabled':True,'actual_epoch_acceptance_and_restored_binaries_bound':True, 'driver_byte_identical':True,
    'guards':53,'preserved_native_paths':29,'candidate_native_paths':1,'existing_test_identities':5,
    'new_owned_wpt':2,'main_rows':16,'resources':len(resources),'exact_fixtures':True,
    'source_replacement_ast_same_except_tempname':True,'candidate_failure_controls_rejected':negative,
    'independent_cleanup_simulations':checks,'live_native_bodies_read':False,
    'executed_native_build_browser_lint':False,'python_syntax':True}
(HERE / 'STATIC-CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
