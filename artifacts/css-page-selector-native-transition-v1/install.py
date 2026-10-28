import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
OUT = ROOT / 'artifacts/css-page-selector-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    manifest, epoch_digest, baseline_name = sys.argv[1:]
    h = load('page_ownership', 'artifacts/css-registered-number-source-transition-v4/transition.py')
    h.authenticate(HERE, manifest)
    p = read(HERE / 'POLICY.json')
    for name, pin in p['references'].items():
        assert sha(ROOT / name) == pin
    assert not any(os.environ.get(k) for k in ['GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'])
    s = h.load_state(RUNTIME)
    epoch_path = RUNTIME / 'CURRENT-EPOCH.json'
    epoch_body = epoch_path.read_bytes()
    assert h.digest(epoch_body) == epoch_digest == p['original_epoch_sha256']
    epoch = json.loads(epoch_body)
    assert epoch['semantic_index']['head'] == p['head']
    assert epoch['staged_working'] == {} and epoch['modified_native_paths'] == ['servo/components/style/custom_properties.rs']
    baseline = ROOT / baseline_name
    assert baseline_name == p['baseline_directory']
    assert {'RESULT.json','ASSESSMENT.json','CLEANUP.json','EPOCH.json','PROCESS.json','raw.jsonl'} <= set(p['baseline_files'])
    for name, pin in p['baseline_files'].items():
        assert sha(baseline / name) == pin
    result, assessment, cleanup = [read(baseline / n) for n in ['RESULT.json','ASSESSMENT.json','CLEANUP.json']]
    assert result['observation_gate_passed'] and result['execution_error'] is None and result['preservation_error'] is None
    assert assessment['complete'] and assessment['execution_preserved'] and assessment['phase'] == 'original-1'
    assert assessment['capsule_manifest_sha256'] == p['baseline_capsule_sha256']
    assert read(baseline / 'EPOCH.json') == epoch
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    h.group_absent(read(baseline / 'PROCESS.json')['pgid'])
    h.quiescent(RUNTIME)
    for name in ['build-PROCESS.json','WAKE-PROCESS.json']:
        h.group_absent(read(RUNTIME / 'provider-default-candidate-build-3' / name)['pgid'])
    before = s.a.verify_current(s.h, ROOT, ENV, epoch)
    flags = {n:s.h.git(ROOT / n, ENV, 'ls-files','-v','-z') for n in ['.','artifacts/css-spec-lean']}
    controls = {n:(RUNTIME / n).read_bytes() for n in ['ROLE.json','OWNED.json']}
    claim = h.claim(ROOT, str(epoch_path.relative_to(ROOT)), epoch_digest)
    owned_claim = h.claim(ROOT, str((RUNTIME/'OWNED.json').relative_to(ROOT)), h.digest(controls['OWNED.json']))
    owned = json.loads(controls['OWNED.json'])
    role_claim = h.claim(ROOT, str((RUNTIME/'ROLE.json').relative_to(ROOT)), h.digest(controls['ROLE.json']))
    sources, original, desired = {}, {}, {}
    for name, record in p['sources'].items():
        original[name] = (ROOT / record['base_capture']).read_bytes()
        desired[name] = (ROOT / record['candidate_capture']).read_bytes()
        assert h.digest(original[name]) == record['base_sha256'] == epoch['pins'][name]
        assert h.digest(desired[name]) == record['candidate_sha256']
        sources[name] = h.claim(ROOT, name, record['base_sha256'], epoch['installed_identities'][name])
        assert owned[name] == sources[name]
    assert len(sources) == 2
    assert not OUT.exists()
    lock = RUNTIME / 'SOURCE-TRANSITION.lock'
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    lock_identity = lock.stat().st_dev, lock.stat().st_ino
    changed = []
    try:
        OUT.mkdir()
        (OUT / 'INITIAL-EPOCH.json').write_bytes(epoch_body)
        h.save(OUT / 'PRE.json', before)
        assert s.a.verify_current(s.h, ROOT, ENV, epoch) == before
        h.authenticate(HERE, manifest)
        for item in [claim, owned_claim, role_claim]: h.claim(ROOT,item['path'],item['owned_sha256'],item['identity'])
        h.group_absent(read(baseline/'PROCESS.json')['pgid'])
        for n in ['build-PROCESS.json','WAKE-PROCESS.json']: h.group_absent(read(RUNTIME/'provider-default-candidate-build-3'/n)['pgid'])
        for name in sources:
            changed.append(name)
            h.write_owned(ROOT, sources[name], desired[name])
        current = copy.deepcopy(epoch)
        for name, record in p['sources'].items():
            current['pins'][name] = record['candidate_sha256']
        index = s.h.index_state(ROOT, ENV)
        semantic = s.h.semantic_index(index)
        assert {k:v for k,v in semantic.items() if k != 'working_diff'} == {k:v for k,v in epoch['semantic_index'].items() if k != 'working_diff'}
        current['semantic_index'] = semantic
        current['raw_index_observation']['current'] = index['raw_index']
        dirty = sorted(n for n in s.h.git(ROOT, ENV, 'diff','--name-only').decode().splitlines() if not n.startswith('artifacts/'))
        assert dirty == sorted([*sources, 'servo/components/style/custom_properties.rs'])
        current['modified_native_paths'] = dirty
        current['counts']['native_modified_paths'] = len(dirty)
        current['page_selector_transition'] = {'role':'candidate','compiled':False,'accepted':False,'manifest_sha256':manifest}
        after = s.a.verify_current(s.h, ROOT, ENV, current)
        assert after['nested_index'] == before['nested_index']
        assert all(s.h.git(ROOT/n, ENV,'ls-files','-v','-z') == v for n,v in flags.items())
        assert all((RUNTIME/n).read_bytes() == b for n,b in controls.items())
        h.authenticate(HERE, manifest)
        h.claim(ROOT,role_claim['path'],role_claim['owned_sha256'],role_claim['identity'])
        for name in sources: owned[name] = sources[name]
        h.write_owned(ROOT, owned_claim, h.encoded(owned))
        h.write_owned(ROOT, claim, h.encoded(current))
        assert s.a.verify_current(s.h, ROOT, ENV, current) == after
        h.save(OUT / 'OWNED.json', sources)
        h.save(OUT / 'INSTALLED-EPOCH.json', current)
        h.save(OUT / 'POST.json', after)
        h.save(OUT / 'INSTALL-RESULT.json', {'installed':True,'compiled':False,'accepted':False,'preservation_verified':True,'sources':sorted(sources),'epoch_sha256':sha(epoch_path)})
        print('Installed exact two-source page-selector candidate', sha(epoch_path), flush=True)
    except BaseException as error:
        failures=[]
        try:
            for name in reversed(changed): h.write_owned(ROOT, sources[name], original[name])
            restored = copy.deepcopy(epoch)
            index = s.h.index_state(ROOT, ENV)
            assert s.h.semantic_index(index) == epoch['semantic_index']
            restored['raw_index_observation']['current'] = index['raw_index']
            s.a.verify_current(s.h, ROOT, ENV, restored)
            assert all(s.h.git(ROOT/n,ENV,'ls-files','-v','-z') == v for n,v in flags.items())
            h.claim(ROOT,role_claim['path'],role_claim['owned_sha256'],role_claim['identity'])
            assert (RUNTIME/'ROLE.json').read_bytes() == controls['ROLE.json']
            h.write_owned(ROOT, owned_claim, controls['OWNED.json'])
            h.write_owned(ROOT, claim, h.encoded(restored))
        except BaseException as rollback: failures.append(repr(rollback))
        if OUT.exists(): h.save(OUT/'FAILURE.json',{'error':repr(error),'rollback_errors':failures,'manual_recovery_required':bool(failures)})
        raise
    finally:
        assert not lock.is_symlink() and (lock.stat().st_dev,lock.stat().st_ino) == lock_identity
        lock.unlink()

if __name__ == '__main__':
    def interrupted(signum, frame): raise RuntimeError('Interrupted '+str(signum))
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    main()
