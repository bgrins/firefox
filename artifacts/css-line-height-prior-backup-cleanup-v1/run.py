import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
policy = read(HERE / 'POLICY.json')
assert policy['execution_enabled'] is True
assert len(sys.argv) == 3 and sys.argv[1] == policy['epoch_sha256']
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
assert not any(os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
for name, pin in policy['references'].items():
    assert sha(ROOT / name) == pin
state = load('cleanup_state', 'artifacts/css-registered-number-native-runtime-v1/state.py')
owner = load('cleanup_owner', 'artifacts/css-registered-number-source-transition-v4/transition.py')
bundle = load('cleanup_bundle', 'artifacts/css-line-height-reversible-pair-v1/bundle.py')
owner.authenticate(HERE, sys.argv[2])
prior = ROOT / policy['prior_runtime']
owner.authenticate(prior, policy['prior_manifest'])
runtime = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
controls = {n: (runtime/n).read_bytes() for n in ('CURRENT-EPOCH.json','ROLE.json','OWNED.json')}
assert sha(runtime/'CURRENT-EPOCH.json') == policy['epoch_sha256']
epoch = json.loads(controls['CURRENT-EPOCH.json'])
assert epoch['semantic_index']['head'] == policy['head'] and epoch['staged_working'] == {}
assert not (runtime/'SOURCE-TRANSITION.lock').exists()
before = state.a.verify_current(state.h, ROOT, ENV, epoch)
flags = {n: state.h.git(path,ENV,'ls-files','-v','-z') for n,path in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')]}
result = read(prior/'RESULT.json')
assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['staged165_preserved']
assert read(prior/'RESTORATION.json')['errors'] == [] and read(prior/'RESTORATION.json')['owned_processes'] == {}
assert read(prior/'candidate-WRAPPER-CLEANUP.json')['no_browser_launch_certified']
for role in ('original','candidate'):
    directory = prior/(role+'-build')
    assert read(directory/'build-RESULT.json')['exit'] == 0
    assert read(directory/'build-GROUP-CLEANUP.json')['owned_group_absent']
    assert read(directory/'wake-GROUP-CLEANUP.json')['owned_group_absent']
    for name in ('build-PROCESS.json','WAKE-PROCESS.json'):
        owner.group_absent(read(directory/name)['pgid'])
assert read(prior/'original-wpt/CLEANUP.json')['owned_group_absent']
owner.group_absent(read(prior/'original-wpt/PROCESS.json')['pgid'])
app = ROOT/'objdir-full.noindex/dist/Nightly.app'
assert bundle.semantic(bundle.scan(app)) == bundle.semantic(read(prior/'APP-PRE.json'))
extras = read(prior/'EXTRA-PRE.json')
assert bundle.semantic({n:bundle.entry(ROOT/n) for n in extras}) == bundle.semantic(extras)
font = 'servo/components/style/values/specified/font.rs'
pre = read(prior/'PRE-OBSERVATION-EPOCH.json')
owner.claim(ROOT,font,pre['pins'][font],pre['installed_identities'][font])
backups = prior/'backups'
saved = read(prior/'BACKUPS.json')
assert bundle.scan(backups) == saved['owned_inventory']
assert all(r['kind'] in ('file','directory') for r in saved['owned_inventory'].values())
output = ROOT/policy['output']
assert output.parent == ROOT/'artifacts' and not output.exists() and not output.is_symlink()
bundle.parents(ROOT,output)
output.mkdir()
state.save(output/'PRE.json',before)
state.save(output/'OWNED-BACKUP-INVENTORY.json',saved)
assert state.a.verify_current(state.h,ROOT,ENV,epoch) == before
assert all((runtime/n).read_bytes() == body for n,body in controls.items())
assert bundle.scan(backups) == saved['owned_inventory']
assert not (runtime/'SOURCE-TRANSITION.lock').exists()
shutil.rmtree(backups)
assert not backups.exists() and not backups.is_symlink()
after = state.a.verify_current(state.h,ROOT,ENV,epoch)
assert after == before
assert all((runtime/n).read_bytes() == body for n,body in controls.items())
assert all(state.h.git(path,ENV,'ls-files','-v','-z') == flags[n] for n,path in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')])
assert bundle.semantic(bundle.scan(app)) == bundle.semantic(read(prior/'APP-PRE.json'))
assert bundle.semantic({n:bundle.entry(ROOT/n) for n in extras}) == bundle.semantic(extras)
owner.claim(ROOT,font,pre['pins'][font],pre['installed_identities'][font])
state.save(output/'POST.json',after)
state.save(output/'RESULT.json',{'removed_owned_backups':True,'removed_bytes':saved['bytes'],'backup_inventory_sha256':sha(prior/'BACKUPS.json'),'current_epoch_sha256':policy['epoch_sha256'],'preservation_verified':True,'app_source_native_index_runtime_unchanged':True,'prior_experiment_still_failed':True,'no_native_acceptance':True})
print('Removed only authenticated obsolete bundle backups; current app/source/index/runtime preserved')
