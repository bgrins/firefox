import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-svg-length-readiness-install-runtime-v1'
SOURCE = 'dom/svg/DOMSVGLength.cpp'
HEADER = 'dom/svg/DOMSVGLength.h'

def need(ok, why):
    if not ok:
        raise RuntimeError(why)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def authenticate(mapping, base):
    for name, digest in mapping.items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'unsafe pin')
        p = base / name
        need(stat.S_ISREG(p.lstat().st_mode) and sha(p) == digest, 'pin ' + name)

def exact_pins(mapping):
    for name, digest in mapping.items():
        p = ROOT / name
        if digest is None:
            need(not p.exists() and not p.is_symlink(), 'required absence ' + name)
        else:
            need(stat.S_ISREG(p.lstat().st_mode) and sha(p) == digest, 'live pin ' + name)

def load(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

parser = argparse.ArgumentParser()
parser.add_argument('--session', type=int, required=True)
parser.add_argument('--session-exit', type=int, required=True)
parser.add_argument('--draft-sha', required=True)
args = parser.parse_args()
need(args.session > 0 and args.session_exit == 0, 'actual successful terminal session required')
authenticate(read(HERE / 'FILES.json'), HERE)
authenticate(read(HERE / 'REFERENCES.json'), ROOT)
need(sha(RUNTIME / 'DRAFT-FILES.json') == args.draft_sha, 'activated installer draft')
authenticate(read(RUNTIME / 'DRAFT-FILES.json'), RUNTIME)
authenticate(read(RUNTIME / 'REFERENCES.json'), ROOT)
need(sha(RUNTIME / 'run.py') == sha(ROOT / 'artifacts/css-svg-length-readiness-install-v1/run.py'), 'reviewed driver unchanged')
c = read(RUNTIME / 'CONFIG.json')
base = read(ROOT / 'artifacts/css-svg-length-readiness-install-v1/CONFIG.json')
need(c['expected_subtests'] == base['expected_subtests'] and c['install'] == base['install']
     and c['candidate_sources'] == base['candidate_sources'], 'reviewed scope unchanged')
state = read(RUNTIME / 'STATE.json'); state_pin = sha(RUNTIME / 'STATE.json')
need(state['status'] == 'terminal' and state['installed'] is True and state['restored'] is False
     and state['build_exit'] == state['lint_exit'] == 0 and state['recovery_errors'] == [] and 'failure' not in state
     and state['subtests'] == {'PASS':25,'FAIL':0} and state['files_ok'] == 3, 'terminal installed25')
acceptance = ROOT / c['acceptance']
need(sha(acceptance) == c['acceptance_sha256'] == state['acceptance_sha256'], 'actual acceptance')
a = read(acceptance)
need(a == c['acceptance_receipt'] and a['status'] == 'SCOPED_ACCEPTED' and a['fix'] == 114 and a['landing_cases'] == 25, 'expanded acceptance schema')
previous = ROOT / c['epoch']
need(sha(previous / 'FILES.json') == c['epoch_manifest_sha256'], 'actual comparison seal')
authenticate(read(previous / 'FILES.json'), previous)
need(read(previous / 'ROOT-FINAL-CHECK.json') == c['epoch_receipt'], 'comparison root receipt')
before, final = read(RUNTIME / 'BEFORE.json'), read(RUNTIME / 'FINAL.json')
need(before == read(previous / 'FINAL.json') and len(before['sources']) == 53
     and before['sources'] == c['source_pins'], 'original installed epoch')
need(set(c['candidate_sources']) == set(c['sources']) == {SOURCE} and len(c['install']) == 1, 'one native/one owned test')
candidate = {n:sha(ROOT / p) for n,p in c['candidate_sources'].items()}
need(final['sources'] == {**before['sources'], **candidate}
     and {n for n in before['sources'] if before['sources'][n] != final['sources'][n]} == {SOURCE}
     and final['sources'][HEADER] == '42e81aeba1faa8d1abddce2d015a9fb452b5da10fca5ddb09b5b8f2b6fc60b33'
     and candidate[SOURCE] == '61ef0fd08580513477043c6a0ff7a42f709c07c5982d163f956db96e53b0e1b3', 'exact CPP delta/header preserved')
need(all(final[k] == before[k] for k in ('head','index_diff_sha256','index_entries_sha256')), 'index/head preserved')
need(sha(RUNTIME / 'original' / SOURCE) == before['sources'][SOURCE]
     == '9a5759f20448150f17ec7d9b541fddb23cd1563a40057e8463272e325e78da8e', 'saved original')
resources = read(RUNTIME / 'RESOURCES.json'); need(len(resources) == 390, '390 resources')
fixtures = {name:sha(RUNTIME / file) for name,file in c['install'].items()}
need(set(fixtures.values()) == {'a884d63f09f5a544c9edbb24befcec830ca5f25177eb7f8ad6e7a78c4e2dda09'}, 'final new WPT')
phasepins = {**resources, **final['sources'], **fixtures, **state['installed_binary_pins']}
need(read(RUNTIME / 'FINAL-PINS.json') == phasepins, 'complete final map')
installation = read(RUNTIME / 'INSTALLATION.json')
need(installation['before'] == before and installation['after'] == final
     and installation['original_source_pins'] == {SOURCE:before['sources'][SOURCE]}
     and installation['installed_source_pins'] == candidate
     and installation['binary_pins'] == state['installed_binary_pins']
     and installation['acceptance_sha256'] == c['acceptance_sha256'], 'installation receipt')
wpt = load('installation_check_wpt', ROOT / c['helpers'] / 'run_wpt.py')
bindings = load('installation_check_bindings', ROOT / c['helpers'] / 'bindings.py')
tests = load('installation_check_tests', ROOT / 'artifacts/css-svg-length-readiness-comparison-v1/tests.py')
wpt.CONFIG, wpt.HERE = c, RUNTIME
need(set(state['installed_binary_pins']) == set(wpt.BINARIES), 'two installed binaries')
need(wpt.snapshot() == final and len(bindings.index_state(wpt)['staged_paths']) == 925, 'live53/index925')
exact_pins(phasepins)
modified = [n for n in wpt.git('diff','--name-only').decode().splitlines() if not n.startswith('artifacts/')]
need(modified == c['modified_native_paths'] and len(modified) == 30
     and not wpt.git('ls-files','--others','--exclude-standard','--','layout','dom','servo','mfbt'), 'native30 preserved')
need(not wpt.git('ls-files','--',*c['install']), 'owned WPT remains untracked')
need(wpt.git('ls-files','--',*c['existing_tests']).decode().splitlines() == c['tracked_existing_tests'], 'old ownership partition')
need(len(c['installed_tests']) == 7 and c['installed_tests'] == c['epoch_receipt']['installed_tests'], 'seven old identities')
need(set(installation['owned_tests']) == set(fixtures), 'one new identity')
installed_tests = {**c['installed_tests'], **installation['owned_tests']}
for name,item in installed_tests.items():
    p = ROOT / name; st = p.lstat()
    need(stat.S_ISREG(st.st_mode) and [st.st_dev,st.st_ino] == item['identity'] and sha(p) == item['sha256'], 'installed test identity ' + name)
need(all(installation['owned_tests'][n]['sha256'] == h for n,h in fixtures.items()), 'new fixture exact')
for name in c['must_be_absent']:
    p = ROOT / name
    need(not p.exists() and not p.is_symlink(), 'prior temp absent')
temp = (ROOT / SOURCE).with_name('.DOMSVGLength.cpp.svg-readiness-install.tmp')
need(not temp.exists() and not temp.is_symlink(), 'source temp absent')
d = RUNTIME / 'wpt-candidate'; raw = d / 'raw.json'
need(stat.S_ISREG(raw.lstat().st_mode) and raw.stat().st_size <= 128*1024*1024, 'raw log type/size')
events = [json.loads(line) for line in raw.read_text().splitlines()]
rows = [e for e in events if e.get('action') == 'test_status']
starts = [e for e in events if e.get('action') == 'test_start']; ends = [e for e in events if e.get('action') == 'test_end']
expected = {(test,name) for test,names in c['expected_subtests'].items() for name in names}
keys = [(r['test'],r['subtest']) for r in rows]
need(len(expected) == len(keys) == len(set(keys)) == 25 and set(keys) == expected
     and all(r['status'] == 'PASS' for r in rows), 'raw25PASS')
need(len(starts) == len(ends) == len(c['expected_subtests']) == 3
     and {r['test'] for r in starts} == {r['test'] for r in ends} == set(c['expected_subtests'])
     and all(r['status'] == 'OK' for r in ends) and not tests.infrastructure_faults(events)
     and sum(e.get('action') == 'suite_start' for e in events) == sum(e.get('action') == 'suite_end' for e in events) == 1, 'raw3OK/no faults')
run = read(d / 'RUN.json')
need(run['complete'] is True and run['exit'] == 0 and run['rows'] == rows and run['starts'] == starts and run['ends'] == ends
     and run['infrastructure_faults'] == [] and run['before'] == run['after'] == phasepins
     and run['command'] == ['./mach','wpt','--headless','--processes=1','--log-raw='+str(raw),*c['tests']], 'RUN/raw/pins join')
need(read(d / 'CLEANUP.json') == {'owned_group_absent':True,'errors':[]}, 'WPT cleanup')
need(read(RUNTIME / 'installed-build.json') == {'command':['./mach','build','binaries'],'exit':0}
     and read(RUNTIME / 'fixture-lint.json') == {'command':['./mach','lint','--linter','wpt',*c['install']],'exit':0}, 'build/lint commands')
need(wpt.snapshot() == final and sha(RUNTIME / 'STATE.json') == state_pin, 'final source/index/state stable')
exact_pins(phasepins)
receipt = {'status':'INSTALLED_VERIFIED','fix':114,'session':args.session,'exit':args.session_exit,
           'state_sha256':state_pin,'final_sha256':sha(RUNTIME/'FINAL.json'),'final_pins_sha256':sha(RUNTIME/'FINAL-PINS.json'),
           'installed_binary_pins':state['installed_binary_pins'],'installed_tests':installed_tests,
           'source_count':53,'resource_count':390,'pin_count':len(phasepins),'native_modified_paths':30,'staged_paths':925,
           'subtests':{'PASS':25,'FAIL':0},'files_ok':3,'raw_sha256':sha(raw),'run_sha256':sha(d/'RUN.json'),
           'accepted115_source_preserved':final['sources']['dom/svg/SVGLength.cpp'] == before['sources']['dom/svg/SVGLength.cpp'],
           'session_exit_supplied_by_root':True}
with (HERE / 'ROOT-FINAL-CHECK.json').open('x') as stream:
    stream.write(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
