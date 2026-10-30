import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
digest = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def git(*args, env=ENV, data=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env, input=data)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def flags(root):
    rows = subprocess.check_output(GIT + ['ls-files', '-v', '-z'], cwd=root, env=ENV)
    return {row[2:].decode(): row[:1].decode() for row in rows.split(b'\0') if row}


def untracked_names():
    return set(git('ls-files', '--others', '--exclude-standard', '-z').decode().rstrip('\0').split('\0'))


def main():
    assert len(sys.argv) == 3 and sys.argv[1] in ('--check', '--commit', '--park')
    assert digest((HERE / 'FILES.json').read_bytes()) == sys.argv[2]
    for name, record in read(HERE / 'FILES.json').items():
        path = HERE / name
        assert path.is_file() and not path.is_symlink()
        assert digest(path.read_bytes()) == record['sha256'] and path.stat().st_size == record['bytes']
    recipe = read(HERE / 'POLICY.json')
    for name, pin in recipe['references'].items():
        assert digest((ROOT / name).read_bytes()) == pin, name
    checkpoint = load('reviewed_checkpoint', recipe['checkpoint'] + '/run.py')
    checkpoint.authenticate(recipe['checkpoint'], recipe['checkpoint_manifest'])
    policy = read(ROOT / recipe['checkpoint'] / 'POLICY.json')
    prior = ROOT / policy['output']
    selected = read(prior / 'PRE.json')['selection']
    assert len(selected) == 199 and policy['head'] == recipe['head']
    assert read(prior / 'ROOT-REPORTED-TERMINAL.json') == recipe['failed_terminal']
    assert not recipe['failed_terminal']['commit_created'] and recipe['failed_terminal']['exit'] == 1
    assert read(prior / 'FAILURE.json')['staging_attempted']
    assert not read(prior / 'FAILURE.json')['commit_command_succeeded']
    state = load('recovery_state', policy['state_helper'])
    owned = load('recovery_ownership', policy['ownership_helper'])
    bundle = load('recovery_bundle', recipe['bundle_helper'])
    controls = {n: (RUNTIME / n).read_bytes() for n in policy['controls']}
    assert {n: digest(v) for n, v in controls.items()} == policy['controls'] == recipe['controls']
    epoch = json.loads(controls['CURRENT-EPOCH.json'])
    roadmap = policy['roadmap']
    original = git('show', policy['head'] + ':' + roadmap['path'])
    assert digest(original) == roadmap['before_sha256']
    assert digest((ROOT / recipe['checkpoint'] / 'ROADMAP-PREFIX.md').read_bytes() + original) == roadmap['after_sha256']
    before = read(ROOT / recipe['before_snapshot'])
    assert digest(owned.encoded(before)) == read(prior / 'PRE.json')['snapshot_sha256']
    lock = RUNTIME / 'SOURCE-TRANSITION.lock'
    app = ROOT / recipe['app']
    app_expected = read(ROOT / recipe['app_pre'])
    extras_expected = read(ROOT / recipe['extras_pre'])
    audit = read(ROOT / recipe['untracked_audit'])
    native_claims = {name: owned.claim(ROOT, name, record['sha256'], record['identity'])
                     for name, record in policy['accepted_current_payloads'].items()}
    control_claims = {n: owned.claim(ROOT, str((RUNTIME / n).relative_to(ROOT)), digest(body))
                      for n, body in controls.items()}
    roadmap_claim = owned.claim(ROOT, roadmap['path'], roadmap['after_sha256'])
    old_flags, nested_flags = flags(ROOT), flags(ROOT / 'artifacts/css-spec-lean')
    untracked = set(audit['paths'])
    assert len(native_claims) == 29 and len(untracked) == 563

    def verify_retained():
        assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
        assert git('symbolic-ref', 'HEAD').decode().strip() == policy['branch']
        index = state.h.index_state(ROOT, ENV)
        assert index == recipe['retained_index'] and index['head'] == policy['head']
        assert index['working_diff'] == before['index']['working_diff']
        assert sorted(git('diff', '--cached', '--name-only').decode().splitlines()) == sorted(selected)
        for name, pin in selected.items():
            assert digest(git('show', ':' + name)) == digest((ROOT / name).read_bytes()) == pin
            stage = git('ls-files', '--stage', '--', name).split()
            assert stage[0] == b'100644' and stage[2] == b'0'
        assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
        for mapping in ('pins', 'staged_working', 'committed_research_working_payloads'):
            for name, pin in epoch[mapping].items():
                expected = roadmap['after_sha256'] if name == roadmap['path'] else pin
                assert state.h.fingerprint(ROOT, name) == expected, name
        for name, identity in epoch['installed_identities'].items():
            info = (ROOT / name).lstat()
            assert stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == identity
        assert git('diff', '--name-only').decode().splitlines() == ['servo/components/style/custom_properties.rs']
        assert state.h.index_state(ROOT / 'artifacts/css-spec-lean', ENV) == before['nested_index']
        assert flags(ROOT) == old_flags and flags(ROOT / 'artifacts/css-spec-lean') == nested_flags
        assert {name: digest(subprocess.check_output(GIT + ['ls-files', '-v', '-z'], cwd=path, env=ENV))
                for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]} == recipe['retained_flag_hashes']
        assert untracked_names() == untracked
        prototype_rows = read(ROOT / recipe['project_audit'])['project_files']
        unrelated_rows = read(ROOT / recipe['unrelated_metadata'])
        assert len(prototype_rows) == 68 and len(unrelated_rows) == 495
        for record in prototype_rows + unrelated_rows:
            path = ROOT / record['path']
            info = path.lstat()
            assert info.st_size == record['bytes'] and stat.S_IMODE(info.st_mode) == record['mode']
            assert [info.st_dev, info.st_ino] == record['identity']
            assert ('symlink' if stat.S_ISLNK(info.st_mode) else 'file') == record['kind']
            if 'sha256' in record:
                assert digest(path.read_bytes()) == record['sha256']
                assert digest(git('show', policy['head'] + ':' + record['signed_copy_path'])) == record['sha256']
        for name, record in policy['accepted_current_payloads'].items():
            owned.claim(ROOT, name, record['sha256'], record['identity'])
            assert digest(git('show', policy['head'] + ':' + name)) == record['sha256']
        for name, value in policy['accepted_preservation_markers'].items():
            assert epoch[name] == value
        for name in policy['preserved_absent_metadata']:
            assert epoch['pins'][name] is None and not os.path.lexists(ROOT / name)
            assert name not in epoch['installed_identities'] and name not in json.loads(controls['OWNED.json'])
        assert not lock.is_symlink() and lock.is_dir() and not list(lock.iterdir())
        assert [lock.stat().st_dev, lock.stat().st_ino] == recipe['lock_identity']
        assert bundle.semantic(bundle.scan(app)) == bundle.semantic(app_expected)
        assert bundle.semantic({n: bundle.entry(ROOT / n) for n in extras_expected}) == bundle.semantic(extras_expected)
        return index

    verify_retained()
    if sys.argv[1] == '--check':
        print('Exact retained V62 state authenticated; no signer or index mutation')
        return
    mode = sys.argv[1][2:]
    assert recipe['execution_enabled'] and mode in recipe['enabled_modes']
    output = ROOT / recipe['outputs'][mode]
    assert not output.exists() and not output.is_symlink()
    output.mkdir()
    lock_identity = recipe['lock_identity']
    save(output / 'PRE.json', {'mode': mode, 'retained_index': recipe['retained_index'],
         'selection': selected, 'controls': recipe['controls'], 'prior_failure': recipe['failed_terminal'],
         'lock_identity': lock_identity})
    (output / 'LOCAL-CURRENT-EPOCH.json').write_bytes(controls['CURRENT-EPOCH.json'])
    save(output / 'LOCAL-RECOVERY-REFERENCES.json', {'LOCAL-CURRENT-EPOCH.json': digest(controls['CURRENT-EPOCH.json']),
         'roadmap_preimage': roadmap['before_sha256'], 'roadmap_postimage': roadmap['after_sha256']})
    try:
        verify_retained()
        if mode == 'commit':
            assert git('config', '--get', 'commit.gpgsign').strip() == b'true'
            tree = git('write-tree').decode().strip()
            message = output / 'message.txt'
            message.write_bytes((prior / 'message.txt').read_bytes())
            assert message.read_text() == policy['message'].rstrip() + '\n'
            with (output / 'commit.log').open('x') as stream:
                result = subprocess.run(GIT + ['commit', '--file', str(message)], cwd=ROOT, env=ENV,
                                        stdout=stream, stderr=subprocess.STDOUT)
            assert result.returncode == 0, 'Signing failed; staging and lock retained, no automatic retry'
            assert bundle.semantic(bundle.scan(app)) == bundle.semantic(app_expected)
            assert bundle.semantic({n: bundle.entry(ROOT / n) for n in extras_expected}) == bundle.semantic(extras_expected)
            finish_commit(policy, selected, tree, output, state, owned, epoch, before,
                          old_flags, nested_flags, untracked, controls, native_claims,
                          control_claims, lock, lock_identity)
        else:
            names = output / 'selected-paths.bin'
            names.write_bytes(b''.join(n.encode() + b'\0' for n in selected))
            git('restore', '--staged', '--source=' + policy['head'],
                '--pathspec-from-file=' + str(names), '--pathspec-file-nul')
            owned.write_owned(ROOT, roadmap_claim, original)
            index = state.h.index_state(ROOT, ENV)
            assert state.h.semantic_index(index) == epoch['semantic_index']
            restored = copy.deepcopy(epoch)
            restored['raw_index_observation']['current'] = index['raw_index']
            after = state.a.verify_current(state.h, ROOT, ENV, restored)
            expected = copy.deepcopy(before)
            expected['index']['raw_index'] = index['raw_index']
            assert after == expected
            head_paths = set(git('ls-tree', '-r', '--name-only', policy['head']).decode().splitlines())
            assert flags(ROOT) == {name: value for name, value in old_flags.items() if name in head_paths}
            assert flags(ROOT / 'artifacts/css-spec-lean') == nested_flags
            assert untracked_names() == untracked
            for name, pin in selected.items():
                assert digest((ROOT / name).read_bytes()) == (roadmap['before_sha256'] if name == roadmap['path'] else pin)
            assert bundle.semantic(bundle.scan(app)) == bundle.semantic(app_expected)
            assert bundle.semantic({n: bundle.entry(ROOT / n) for n in extras_expected}) == bundle.semantic(extras_expected)
            assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
            owned.write_owned(ROOT, control_claims['CURRENT-EPOCH.json'], owned.encoded(restored))
            assert state.a.verify_current(state.h, ROOT, ENV, restored) == after
            assert all((RUNTIME / n).read_bytes() == controls[n] for n in ('ROLE.json', 'OWNED.json'))
            save(output / 'RESULT.json', {'released_staging': True, 'roadmap_preimage_restored': True,
                 'research_files_preserved': True, 'head': policy['head'],
                 'only_epoch_change': 'raw_index_observation.current',
                 'epoch_sha256': digest(owned.encoded(restored)), 'signer_called': False,
                 'accepted_fixes': 149, 'tracked_fixes': 150})
            assert [lock.stat().st_dev, lock.stat().st_ino] == lock_identity
            lock.rmdir()
    except BaseException as error:
        save(output / 'FAILURE.json', {'error': repr(error), 'mode': mode,
             'actual_head': git('rev-parse', 'HEAD').decode().strip(),
             'manual_recovery_required': True, 'automatic_retry_or_reset': False})
        raise


def finish_commit(policy, selected, tree, output, state, owned, epoch, before,
                  old_flags, nested_flags, untracked, controls, native_claims,
                  control_claims, lock, lock_identity):
    roadmap = policy['roadmap']
    completion = policy['completed_pair']
    commit = git("rev-parse", "HEAD").decode().strip()
    assert git("rev-parse", commit + "^").decode().strip() == policy["head"]
    assert git("rev-parse", commit + "^{tree}").decode().strip() == tree
    assert sorted(git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).decode().splitlines()) == sorted(selected)
    with (output / "signature.log").open("x") as stream:
        subprocess.run(GIT + ["-c", "gpg.ssh.allowedSignersFile=" + str(ROOT / policy["allowed_signers"]), "verify-commit", commit], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
    actual = state.h.index_state(ROOT, ENV)
    assert not git("diff", "--cached", "--name-only")
    assert actual["working_diff"] == before["index"]["working_diff"]
    assert state.h.index_state(ROOT / "artifacts/css-spec-lean", ENV) == before["nested_index"]
    now_flags = flags(ROOT)
    assert all(now_flags[n] == value for n, value in old_flags.items())
    assert set(now_flags) == set(old_flags) | set(selected)
    assert all(now_flags[n] == "H" for n in set(now_flags) - set(old_flags))
    assert flags(ROOT / "artifacts/css-spec-lean") == nested_flags
    assert untracked_names() == untracked - set(selected)
    updated = copy.deepcopy(epoch)
    updated["semantic_index"] = state.h.semantic_index(actual)
    updated["raw_index_observation"]["current"] = actual["raw_index"]
    for mapping in ("pins", "staged_working"):
        if roadmap["path"] in updated[mapping]:
            assert updated[mapping][roadmap["path"]] == roadmap["before_sha256"]
            updated[mapping][roadmap["path"]] = roadmap["after_sha256"]
    updated["committed_research_working_payloads"].update(selected)
    updated["counts"]["committed_research_payloads"] = len(updated["committed_research_working_payloads"])
    post = state.a.verify_current(state.h, ROOT, ENV, updated)
    for name, pin in selected.items():
        assert digest(git("show", commit + ":" + name)) == pin
    assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
    for claim in native_claims.values():
        owned.claim(ROOT, claim["path"], claim["owned_sha256"], claim["identity"])
    canonical_started = True
    owned.write_owned(ROOT, control_claims["CURRENT-EPOCH.json"], owned.encoded(updated))
    assert state.a.verify_current(state.h, ROOT, ENV, updated) == post
    assert all((RUNTIME / n).read_bytes() == controls[n] for n in ("ROLE.json", "OWNED.json"))
    save(output / "FINAL-CHECK.json", {"head": commit, "parent": policy["head"], "tree": tree, "signature_verified": True, "runtime_epoch_synchronized": True, "current_epoch_sha256": digest(owned.encoded(updated)), "accepted_fixes": 149, "tracked_fixes": 150, "accepted_fix_increment": 0, "canonical_coverage_increment": 0, "provider_candidate_accepted": False, "easing_native_acceptance": False, "minmax_native_acceptance": False, "completed_pair_result_sha256": completion["evidence"][completion["result"]], "signing_performed_build_or_browser_execution": False, "native_and_binary_payloads_preserved": True, "nested_index_and_flags_preserved": True, "unselected_untracked_names_preserved": True, "untracked_before": len(untracked), "untracked_after": len(untracked_names()), "selection_count": len(selected), "full_epoch_copies_saved": 0})
    final_published = True
    assert [lock.stat().st_dev, lock.stat().st_ino] == lock_identity
    lock.rmdir()
    print("Signed research checkpoint and synchronized canonical epoch", commit, flush=True)


if __name__ == '__main__':
    main()
