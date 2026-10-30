import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import secrets
import stat
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / "artifacts/css-registered-number-native-runtime-v1"
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(pin):
    assert sha(HERE / "FILES.json") == pin
    for name, expected in read(HERE / "FILES.json").items():
        assert sha(HERE / name) == expected, name
    policy = read(HERE / "POLICY.json")
    assert policy["original_only"] is True
    if sys.argv[1] == "--run":
        assert policy["feedback_transport_pending"] is False
    for name, expected in policy["references"].items():
        assert sha(ROOT / name) == expected, name
    if sys.argv[1] == "--run":
        assert policy["execution_enabled"] is True
        assert policy["activation_pending"] == []
        assert policy["head"] and policy["prepared_application_metadata"] and policy["build_epoch"]
        assert {name: sha(RUNTIME / name) for name in policy["controls"]} == policy["controls"]
        assert not (RUNTIME / "SOURCE-TRANSITION.lock").exists()
    return policy


def main():
    assert len(sys.argv) == 3 and sys.argv[1] in ("--check", "--run")
    policy = authenticate(sys.argv[2])
    if sys.argv[1] == "--check":
        load("easing_static_check", str(HERE / "check.py")).check(policy)
        print("Static easing baseline checks passed; no browser or full state verification performed")
        return
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1",
               MOZCONFIG=str(ROOT / "mozconfig"), MOZ_OBJDIR=str(ROOT / "objdir-full.noindex"),
               MOZ_HEADLESS="1", MOZ_SKIP_PATH_PERFORMANCE_CHECK="1")
    assert not any(os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"))
    state = load("easing_state", policy["state_helper"])
    epoch = read(RUNTIME / "CURRENT-EPOCH.json")
    assert epoch["semantic_index"]["head"] == policy["head"] and epoch["staged_working"] == {}
    assert epoch["accepted_pow_special_value"]["fix"] == 150
    assert epoch["pow_special_value_transition"]["accepted"]
    assert epoch["pins"]["servo/components/style/values/generics/calc.rs"] == policy["accepted_calc_sha256"]
    built = read(ROOT / policy["build_epoch"])
    bound = [name for name in built["pins"]
             if name.startswith(("servo/", "layout/", "dom/")) or name in policy["rebuilt_binaries"]]
    assert bound and all(epoch["pins"][name] == built["pins"][name] for name in bound)

    assert len(policy["accepted_current_payloads"]) == 29
    for name, claim in policy["accepted_current_payloads"].items():
        assert epoch["pins"][name] == claim["sha256"] and epoch["installed_identities"][name] == claim["identity"]

    def verify():
        authenticate(sys.argv[2])
        for name, pin in policy["source_role_pins"].items():
            assert sha(ROOT / name) == pin, name
            if name in built["pins"]:
                assert epoch["pins"][name] == built["pins"][name] == pin, name
            else:
                assert name in policy["build_unpinned_sources"], name
                assert name not in built["modified_native_paths"]
                assert built["semantic_index"]["head"] == policy["wpt"]["phase_revisions"]["original"]
                assert epoch["pins"].get(name, pin) == pin
                for revision in (policy["head"], policy["wpt"]["phase_revisions"]["original"]):
                    body = state.h.git(ROOT, env, "show", revision + ":" + name)
                    assert hashlib.sha256(body).hexdigest() == pin, (name, revision)
        return state.a.verify_current(state.h, ROOT, env, epoch)

    metadata = load("easing_metadata", policy["wpt"]["metadata_helper"])
    prepared = metadata.application_metadata(ROOT / policy["wpt"]["application_ini"], policy["wpt"]["phase_revisions"]["original"])
    prepared.update(build_revision=prepared["revision"], harness_revision=policy["wpt"]["harness_revision"], source_role="original")
    assert prepared == policy["prepared_application_metadata"]
    verify()
    output = ROOT / policy["output"]
    assert not output.exists() and not output.is_symlink()
    output.mkdir()
    stopped = [False]
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, frame: stopped.__setitem__(0, True))
    runner = load("easing_wpt", policy["wpt_helper"])
    owned = {}
    initial = verify()
    runner.save(output / 'PRE.json', initial)
    phases = {}
    for kind in ('feedback',):
        current = dict(policy, wpt=policy['phases'][kind])
        phase_env = dict(env)
        if kind == 'feedback':
            records = output / 'feedback-records'
            records.mkdir(mode=0o700)
            directory_identity = [records.stat().st_dev, records.stat().st_ino]
            run_id = secrets.token_hex(24)
            phase_env.update(DURATION_FEEDBACK_RECORD_DIR=str(records), DURATION_FEEDBACK_RUN_ID=run_id)
            runner.save(output / 'FEEDBACK-BINDING.json', {'directory': str(records), 'identity':directory_identity, 'run_id': run_id})
        phases[kind] = runner.run(ROOT, HERE, output / (kind + '-wpt'), 'original', current,
                                 phase_env, verify, owned, lambda: stopped[0])
        assert not owned
        assessment = read(output / (kind + '-wpt') / 'ASSESSMENT.json')
        phase_directory = output / (kind + '-wpt')
        assert read(phase_directory / 'PRE.json') == read(phase_directory / 'POST.json') == initial
        assert read(phase_directory / 'APPLICATION-METADATA.json') == read(phase_directory / 'APPLICATION-METADATA-POST.json') == policy['prepared_application_metadata']
        if kind == 'feedback':
            assert not records.is_symlink() and [records.stat().st_dev, records.stat().st_ino] == directory_identity
            assert stat.S_IMODE(records.stat().st_mode) == 0o700 and records.stat().st_uid == os.getuid()
            expected = {'self.json':'self font', 'coupled.json':'coupled font and opacity', 'zero-start.json':'zero-start self font'}
            assert {p.name for p in records.iterdir()} == set(expected)
            pins = {}
            for filename, label in expected.items():
                path = records / filename
                assert path.is_file() and not path.is_symlink()
                info = path.stat()
                assert stat.S_IMODE(info.st_mode) == 0o600 and info.st_uid == os.getuid() and info.st_nlink == 1
                record = read(path)
                assert set(record) == {'run_id','kind','samples'}
                assert record['run_id'] == run_id and record['kind'] == label
                assert len(record['samples']) == 8
                for sample in record['samples']:
                    assert set(sample) == {'font','cssDuration','opacity','effects','repeatFont','repeatDuration'}
                    assert len(sample['effects']) == (2 if label == 'coupled font and opacity' else 1)
                    assert all(set(effect) == {'name','time','duration','progress','state'} for effect in sample['effects'])
                pins[filename] = {'sha256':sha(path),'identity':[info.st_dev,info.st_ino],'mode':stat.S_IMODE(info.st_mode)}
            assert all(row['status'] == 'PASS' for row in assessment['rows'])
            runner.save(output / 'FEEDBACK-RECORDS.json', {'run_id':run_id,'records':pins,'numeric_or_convergence_oracle':False})
        runner.save(output / (kind.upper() + '-ROSTER.json'), {
            'observed_subtest_count': len(assessment['rows']),
            'expected_subtests': {page:[r['subtest'] for r in assessment['rows'] if r['test']==page] for page in current['wpt']['expected_subtests']},
            'endings': assessment['ends'], 'phase':phases[kind], 'owner_sha256':sys.argv[2]})
    after = verify()
    assert initial == after and not owned
    runner.save(output / 'POST.json', after)
    runner.save(output / 'RESULT.json', {'phases':phases,'preservation_verified':True,
        'source_or_canonical_mutation':False,'native_fix_accepted':False,
        'numeric_feedback_oracle':False,'feedback_only':True})
    print('Completed fresh feedback-only original observation; no acceptance', flush=True)


if __name__ == "__main__":
    main()
