import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / 'artifacts/css-svg-length-context-refresh-acceptance-draft-v1'
OUTPUT = ROOT / 'artifacts/css-svg-length-conversion-commit-queue-v3'

def need(ok, why):
    if not ok:
        raise RuntimeError(why)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def path(name):
    p = Path(name)
    need(not p.is_absolute() and '..' not in p.parts and p.parts[0] == 'artifacts', 'artifact-relative path required')
    return ROOT / p

def pinned(name, digest):
    p = path(name)
    need(stat.S_ISREG(p.lstat().st_mode) and sha(p) == digest, 'pin ' + name)
    return p

def capsule(pair):
    manifest = pinned(*pair)
    need(manifest.name in ('FILES.json', 'DRAFT-FILES.json'), 'capsule manifest')
    values = read(manifest)
    for name, digest in values.items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'unsafe capsule member')
        p = manifest.parent / name
        need(stat.S_ISREG(p.lstat().st_mode) and sha(p) == digest, 'payload ' + str(p))
    return manifest.parent, values

def require_review_binding(directory, files, digest):
    need(any(digest in (directory / n).read_text() for n in files if Path(n).suffix in ('.json', '.md', '.py')),
         'review lacks full target manifest hash')

def results(directory, phase, expected, required_failures):
    d = directory / ('wpt-' + phase)
    raw = d / 'raw.json'
    need(stat.S_ISREG(raw.lstat().st_mode) and raw.stat().st_size <= 128 * 1024 * 1024, 'raw size/type')
    events = [json.loads(line) for line in raw.read_text().splitlines()]
    rows = [e for e in events if e.get('action') == 'test_status']
    starts = [e for e in events if e.get('action') == 'test_start']
    ends = [e for e in events if e.get('action') == 'test_end']
    keys = [(r['test'], r['subtest']) for r in rows]
    wanted = {(test, name) for test, names in expected.items() for name in names}
    need(len(keys) == len(set(keys)) == len(wanted) and set(keys) == wanted, 'exact raw testcase roster')
    need(len(starts) == len(ends) == len(expected) and {e['test'] for e in starts} == set(expected)
         and {e['test'] for e in ends} == set(expected) and all(e['status'] == 'OK' for e in ends), 'harness completeness')
    failures = {(r['test'], r['subtest']): {k:r.get(k) for k in ('status', 'message', 'expected', 'known_intermittent')}
                for r in rows if r['status'] != 'PASS'}
    need(failures == required_failures, 'raw outcomes/diagnostics')
    run = read(d / 'RUN.json')
    need(run['complete'] is True and run['rows'] == rows and run['starts'] == starts and run['ends'] == ends
         and run['infrastructure_faults'] == [] and run['before'] == run['after']
         and run['exit'] == (1 if failures else 0), 'RUN preservation/completeness')
    need(read(d / 'CLEANUP.json') == {'owned_group_absent': True, 'errors': []}, 'cleanup')
    return run

parser = argparse.ArgumentParser()
for option in ('comparison', 'results-review', 'acceptance', 'installation', 'installation-review', 'updater', 'updater-review'):
    parser.add_argument('--' + option, nargs=2, metavar=('MANIFEST', 'SHA256'), required=True)
parser.add_argument('--preflight', nargs=2, metavar=('FILE', 'SHA256'), required=True)
parser.add_argument('--research-extra', nargs=2, metavar=('MANIFEST', 'SHA256'), action='append', default=[])
args = parser.parse_args()
need(not OUTPUT.exists() and not OUTPUT.is_symlink(), 'successor already exists')
self_manifest = read(HERE / 'FILES.json')
for name, digest in self_manifest.items():
    need(sha(HERE / name) == digest, 'finalizer seal')
for name, digest in read(HERE / 'REFERENCES.json').items():
    pinned(name, digest)
base_manifest = read(BASE / 'FILES.json')
for name, digest in base_manifest.items():
    need(sha(BASE / name) == digest, 'base draft changed')
research, native = read(BASE / 'research.draft.json'), read(BASE / 'native.draft.json')
need(len(research['files']) == 438 and set(research['files']) == set(research['source_pins']), 'base438')
for name, digest in research['source_pins'].items():
    pinned(name, digest)
need(sha(ROOT / native['patch']) == native['patch_sha256'] and len(native['source_pins']) == 5, 'frozen five-path patch')
input_pairs = {role: getattr(args, role) for role in
               ('comparison', 'results_review', 'acceptance', 'installation', 'installation_review', 'updater', 'updater_review')}
input_pairs.update({'research_extra_' + str(i): pair for i, pair in enumerate(args.research_extra)})
input_pairs['finalizer'] = [str((HERE / 'FILES.json').relative_to(ROOT)), sha(HERE / 'FILES.json')]
loaded = {role: capsule(pair) for role, pair in input_pairs.items()}
comparison, _ = loaded['comparison']; installation, _ = loaded['installation']
acceptance, _ = loaded['acceptance']; updater, _ = loaded['updater']
preflight = pinned(*args.preflight)
for review, target in [('results_review', 'comparison'), ('installation_review', 'installation'), ('updater_review', 'updater')]:
    require_review_binding(*loaded[review], getattr(args, target)[1])
a = read(acceptance / 'ACCEPTANCE.json')
need(a['status'] == 'SCOPED_ACCEPTED' and a['fix'] == 114 and a['landing_cases'] == 25
     and a['patch']['sha256'] == native['patch_sha256'] and sha(ROOT / a['patch']['path']) == native['patch_sha256'], 'expanded114 acceptance')
need(a['runtime'] == args.comparison[0].rsplit('/', 1)[0] and a['runtime_files_sha256'] == args.comparison[1]
     and a['independent_result_review']['files_sha256'] == args.results_review[1], 'acceptance/comparison/review join')
s = read(comparison / 'STATE.json'); c = read(comparison / 'CONFIG.json'); root = read(comparison / 'ROOT-FINAL-CHECK.json')
need(s['status'] == 'terminal' and s['restored'] is True and s['restore_build_exit'] == 0
     and s['recovery_errors'] == [] and 'failure' not in s and s['paired_preservation_passed'] is True
     and set(s['phases']) == {'baseline', 'candidate'} and all(v['build_exit'] == 0 for v in s['phases'].values()), 'comparison terminal success')
need(root['status'] == 'RESTORED_VERIFIED' and root['state_sha256'] == sha(comparison / 'STATE.json')
     and root['final_sha256'] == sha(comparison / 'FINAL.json')
     and root['final_pins_sha256'] == sha(comparison / 'FINAL-PINS.json')
     and read(comparison / 'BEFORE.json') == read(comparison / 'FINAL.json')
     and root['restored_binary_pins'] == s['restored_binary_pins'], 'comparison restoration')
allowed = {(t,n):v for t,names in c['baseline_allowed_failures'].items() for n,v in names.items()}
need(len(allowed) == 16 and sum(map(len,c['expected_subtests'].values())) == 51 and len(c['main_tests']) == 3, 'comparison51/repair16')
old = results(comparison, 'baseline', c['expected_subtests'], allowed)
new = results(comparison, 'candidate', c['expected_subtests'], {})
paired = read(comparison / 'COMPARISON.json')
need(not paired['regressions'] and not paired['changed_failures'] and {tuple(k) for k in paired['repaired']} == set(allowed), 'paired16 exact')
is_ = read(installation / 'STATE.json'); ic = read(installation / 'CONFIG.json'); ir = read(installation / 'ROOT-FINAL-CHECK.json')
need(is_['status'] == 'terminal' and is_['installed'] is True and is_['restored'] is False
     and is_['build_exit'] == is_['lint_exit'] == 0 and not is_['recovery_errors'] and 'failure' not in is_
     and is_['subtests'] == {'PASS':25,'FAIL':0} and is_['files_ok'] == 3, 'installed25 success')
need(ir['status'] == 'INSTALLED_VERIFIED' and ir['state_sha256'] == sha(installation / 'STATE.json')
     and ir['final_sha256'] == sha(installation / 'FINAL.json')
     and ir['final_pins_sha256'] == sha(installation / 'FINAL-PINS.json')
     and ir['installed_binary_pins'] == is_['installed_binary_pins'], 'installed root receipt')
need(ic['epoch_manifest_sha256'] == args.comparison[1] and ic['acceptance_sha256'] == sha(acceptance / 'ACCEPTANCE.json')
     and is_['acceptance_sha256'] == ic['acceptance_sha256'], 'installation epoch/acceptance joins')
need(read(updater / 'CONFIG.json')['candidate_sources'] == ic['candidate_sources']
     and sha(updater / 'run.py') == sha(installation / 'run.py'), 'reviewed updater candidate/driver')
need(sum(map(len,ic['expected_subtests'].values())) == 25 and len(ic['expected_subtests']) == 3, 'installed25 roster')
installed_run = results(installation, 'candidate', ic['expected_subtests'], {})
need({k:v for k,v in c['expected_subtests'].items() if k in c['main_tests']} == ic['expected_subtests'], 'same final-path25 tests')
before = read(installation / 'BEFORE.json'); final = read(installation / 'FINAL.json')
need(before == read(comparison / 'FINAL.json')
     and final['sources'] == {**before['sources'], 'dom/svg/DOMSVGLength.cpp':native['source_pins']['dom/svg/DOMSVGLength.cpp']}
     and all(final[k] == before[k] for k in ('head','index_diff_sha256','index_entries_sha256'))
     and len(final['sources']) == 53 and ir['native_modified_paths'] == 30 and ir['staged_paths'] == 925, 'installed stack preservation')
need(len(root['installed_tests']) == 7 and all(ir['installed_tests'][n] == v for n,v in root['installed_tests'].items()), 'seven prior installed identities')
finalpins = read(installation / 'FINAL-PINS.json')
need(installed_run['before'] == finalpins, 'installed final full role map')
for name, digest in native['source_pins'].items():
    p = ROOT / name
    need(stat.S_ISREG(p.lstat().st_mode) and sha(p) == digest == finalpins[name], 'five live patch bodies ' + name)

selection = dict(research['source_pins']); omitted = {}; manifests = {}; external = {}
for role, (directory, values) in loaded.items():
    manifest_name, manifest_sha = input_pairs[role]
    manifests[manifest_name] = manifest_sha
    selection[manifest_name] = manifest_sha
    for name, digest in values.items():
        full = str((directory / name).relative_to(ROOT))
        if any(part in ('original', 'originals', 'inputs', 'profiles', 'profile', 'head', 'baseline', 'candidate') for part in Path(name).parts[:-1]):
            omitted[full] = {'sha256':digest,'reason':'Redundant saved source/input snapshot or browser profile; historical replay remains external.'}
        else:
            need(full not in selection or selection[full] == digest, 'selection conflict')
            selection[full] = digest
    references = directory / 'REFERENCES.json'
    if references.exists():
        for name, digest in read(references).items():
            pinned(name,digest)
            if name not in selection:
                external[name] = digest
selection[args.preflight[0]] = args.preflight[1]
for name,digest in read(BASE / 'REFERENCES.json').items():
    if name not in selection:
        external[name] = digest
external = {n:h for n,h in external.items() if n not in selection}
research.update(expected_head=None, status='ACCEPTED_EXPANDED114_EVIDENCE_SIGNED_PARENT_PENDING',
                files=sorted(selection), source_pins=dict(sorted(selection.items())), required_later=['signed_research_parent','signed_native_parent'], ready_for_execution=False)
native.update(expected_head=None,status='ACCEPTED_EXPANDED114_INSTALLED_SIGNED_PARENT_PENDING',
              acceptance=str((acceptance/'ACCEPTANCE.json').relative_to(ROOT)),
              post_acceptance_installation=str(installation.relative_to(ROOT)),ready_for_execution=False)
check={'base_research_files':438,'selected_files':len(selection),'selected_bytes':sum((ROOT/n).stat().st_size for n in selection),
       'added_files':len(set(selection)-set(read(BASE/'research.draft.json')['files'])),
       'native_paths':5,'comparison_cases':51,'main_cases':25,'repairs':16,'five_live_pins':native['source_pins'],
       'signed_parents_bound':False,'native_index_build_browser_signing_actions':False}
OUTPUT.mkdir()
def save(name,value):
    (OUTPUT/name).write_text(json.dumps(value,indent=2)+'\n')
save('research.draft.json',research);save('native.draft.json',native);save('CHECK.json',check)
save('PENDING.json',{'signed_research_parent':None,'signed_native_parent':None})
save('REFERENCES.json',{**read(HERE/'REFERENCES.json'),**manifests,args.preflight[0]:args.preflight[1]})
save('OMITTED-NEW.json',omitted);save('EXTERNAL-REFERENCES.json',external)
save('ADDED-RESEARCH.json',{n:h for n,h in selection.items() if n not in read(BASE/'research.draft.json')['source_pins']})
(OUTPUT/'README.md').write_text('Expanded accepted114 queue: preceding research, then exact two-native/three-WPT patch. All438 prior selected files retained; actual final comparison, acceptance, installed25 and reviews added. Both signed parents remain null; this is not permission to stage/sign. Prior queue-v2 and acceptance-draft omission/external disclosures remain in force. OMITTED-NEW lists omitted source/profile snapshots. EXTERNAL-REFERENCES lists unselected direct references; this is not recursive dependency closure or a self-contained historical replay bundle. No native or index changes.\n')
save('FILES.json',{str(p.relative_to(OUTPUT)):sha(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()})
print(json.dumps({'output':str(OUTPUT.relative_to(ROOT)),'manifest_sha256':sha(OUTPUT/'FILES.json'),**check},indent=2))
