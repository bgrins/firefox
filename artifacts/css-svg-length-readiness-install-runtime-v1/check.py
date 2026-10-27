import ast
import hashlib
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
    for name, h in mapping.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert stat.S_ISREG((base / name).lstat().st_mode) and sha(base / name) == h
c = read(HERE / 'CONFIG.json')
assert c['ready_for_execution'] is False
assert all(c[n] is None for n in ('epoch','epoch_manifest_sha256','epoch_receipt','acceptance','acceptance_sha256','acceptance_receipt'))
auth(read(HERE / 'REFERENCES.json'), ROOT)
comp = ROOT / 'artifacts/css-svg-length-readiness-comparison-v1'
auth(read(comp / 'DRAFT-FILES.json'), comp)
cc = read(comp / 'CONFIG.json')
proposal = ROOT / c['proposal']
auth(read(proposal / 'FILES.json'), proposal)
assert c['source_pins'] == cc['source_pins'] and c['guard_sources'] == cc['guard_sources'] and len(c['guard_sources']) == 53
assert c['modified_native_paths'] == cc['modified_native_paths'] and len(c['modified_native_paths']) == 30
assert c['sources'] == ['dom/svg/DOMSVGLength.cpp'] and set(c['sources']) <= set(c['modified_native_paths'])
assert c['candidate_sources'] == {n:cc['candidate_sources'][n] for n in c['sources']}
assert c['candidate_pins'] == {n:cc['candidate_pins'][n] for n in c['sources']}
assert sha(ROOT / c['original_source_artifact']) == c['source_pins']['dom/svg/DOMSVGLength.cpp']
assert c['source_pins']['dom/svg/DOMSVGLength.h'] == sha(proposal / 'candidate/dom/svg/DOMSVGLength.h')
assert c['candidate_pins']['dom/svg/DOMSVGLength.cpp'] == sha(proposal / 'candidate/dom/svg/DOMSVGLength.cpp')
assert c['install'] == cc['install'] and len(c['install']) == 1
assert c['expected_subtests'] == {t:cc['expected_subtests'][t] for t in cc['main_tests']}
assert len(c['expected_subtests']) == 3 and sum(map(len,c['expected_subtests'].values())) == 25
assert c['tests'] == ['testing/web-platform/tests'+t for t in cc['main_tests']]
assert c['installed_tests'] == cc['epoch_receipt']['installed_tests'] and len(c['installed_tests']) == 7
assert c['existing_tests'] == cc['existing_tests'] and c['existing_test_pins'] == cc['existing_test_pins']
assert not set(c['install']) & set(c['existing_tests'])
resources = read(HERE / 'RESOURCES.json')
assert resources == read(comp / 'RESOURCES.json')
for name, fixture in c['install'].items():
    assert (HERE / fixture).read_bytes() == (proposal / c['proposal_test_files'][name]).read_bytes()
    assert resources[name] is None and resources['testing/web-platform/meta/' + name.removeprefix('testing/web-platform/tests/') + '.ini'] is None
for name, source in c['proposal_test_files'].items():
    if name not in c['install']:
        assert sha(proposal / source) == c['existing_test_pins'][name] == resources[name]
for name, item in c['installed_tests'].items():
    assert resources[name] == item['sha256']
base = ROOT / 'artifacts/css-svg-absolute-factor-install-v2/run.py'
def function(path,name):
    return next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name == name)
assert ast.unparse(function(base,'replace_source')).replace('.svg-factor-install.tmp','.svg-readiness-install.tmp') == ast.unparse(function(HERE / 'run.py','replace_source'))
marker = 'finally:\n    if not succeeded:'
assert base.read_text().split(marker,1)[1] == (HERE / 'run.py').read_text().replace('.svg-readiness-install.tmp','.svg-factor-install.tmp').split(marker,1)[1]
for name in ('run.py','check.py'):
    compile((HERE/name).read_text(), name, 'exec')
tree=ast.parse((HERE/'run.py').read_text())
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='require_phase' for n in ast.walk(tree))
gate=next(n for n in ast.walk(tree) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
          and any(isinstance(a,ast.Constant) and a.value=='own25 integration' for a in n.value.args))
def need(condition,message):
    if not condition: raise RuntimeError(message)
rows=[{'test':t,'subtest':n,'status':'PASS'} for t,names in c['expected_subtests'].items() for n in names]
def run_gate(rows):
    exec(compile(ast.Module(body=[gate],type_ignores=[]),'integration gate','exec'), {'need':need,'result':{'rows':rows}})
run_gate(rows)
negative=0
for i in range(25):
    changed=[dict(r) for r in rows];changed[i]['status']='FAIL'
    try: run_gate(changed)
    except RuntimeError: negative+=1
    else: raise AssertionError(i)
for changed in (rows[:-1], rows+[rows[0]]):
    try: run_gate(changed)
    except RuntimeError: negative+=1
    else: raise AssertionError('count')
receipt={'disabled':True,'epoch_acceptance_restored_binary_bindings_null':True,'source_guards':53,
 'preserved_native_inventory':30,'native_writes':1,'header_unchanged':True,'preserved_existing_test_identities':7,
 'new_owned_tests':1,'required_main_cases':25,'harness_files':3,'resources':len(resources),
 'atomic_helper_same_except_tempname':True,'restoration_tail_same_except_tempname':True,
 'reused_comparison_WPT_runner':True,'integration_gate_negatives':negative,
 'live_native_bodies_read':False,'native_index_build_browser_actions':False}
(HERE/'STATIC-CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
