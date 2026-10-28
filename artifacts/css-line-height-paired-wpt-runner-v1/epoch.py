import json
import hashlib
from pathlib import Path
import copy
import stat


def derive(old, current, check, sources, tested_binaries, ledger_paths, provenance):
    assert check['status'] == 'POST_SIGNING_LEDGER_ROOT_VERIFIED'
    assert check['index_empty'] is True
    assert check['native_and_binary_bodies_unchanged'] is True
    assert check['head'] == current['semantic_index']['head']
    assert set(current['pins']) == set(old['pins'])
    assert set(ledger_paths) == set(check['ledger_paths']) and len(ledger_paths) == 6
    assert all(current['pins'][p] == pin for p, pin in old['pins'].items()
               if p not in ledger_paths)
    assert len(sources) == 21 and len(tested_binaries) == 4
    assert all(p in current['pins'] and current['pins'][p] == pin
               for p, pin in (sources | tested_binaries).items())
    assert current['installed_identities'] == old['installed_identities']
    assert len(current['installed_identities']) == 35
    assert current['nested_semantic_index'] == old['nested_semantic_index']
    assert current['untracked_native'] == old['untracked_native']
    assert len(current['untracked_native']) == 12
    assert set(current['modified_native_paths']) <= set(old['modified_native_paths'])
    assert current['staged_working'] == {}
    assert all(current['committed_research_working_payloads'].get(p) == pin
               for p, pin in old['committed_research_working_payloads'].items())
    assert current['counts']['roles'] == len(current['pins']) == check['roles']
    assert current['counts']['native_modified_paths'] == len(current['modified_native_paths'])
    assert current['counts']['committed_research_payloads'] == len(current['committed_research_working_payloads'])
    assert current['raw_index_observation']['current']
    assert {'build', 'compile_sources', 'gtest_attempt', 'gtest_results',
            'packaging_validation', 'post_signing_epoch', 'post_signing_check',
            'signing_execution', 'signing_manifest', 'failed_reconciliation'} <= set(provenance)
    assert all(set(r) == {'path', 'sha256'} and r['path'] and len(r['sha256']) == 64
               for r in provenance.values())
    result = copy.deepcopy(current)
    result['provenance'] = copy.deepcopy(provenance)
    result['operation_descriptor_transition'] = {
        'source_paths': 21,
        'test_reexecution': False,
        'signing_changes_head_and_index': True,
        'accepted_fix_increment': 0,
        'canonical_coverage_increment': 0,
    }
    return result


def verify_current(h, root, env, epoch):
    before = h.index_state(root, env)
    assert before['raw_index'] == epoch['raw_index_observation']['current']
    assert h.semantic_index(before) == epoch['semantic_index']
    nested_before = h.index_state(root / 'artifacts/css-spec-lean', env)
    assert h.semantic_index(nested_before) == epoch['nested_semantic_index']
    for name in ('pins', 'staged_working', 'committed_research_working_payloads'):
        assert {p: h.fingerprint(root, p) for p in epoch[name]} == epoch[name], name
    for path, identity in epoch['installed_identities'].items():
        info = (root / path).lstat()
        assert stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == identity
    staging = json.loads((Path(__file__).resolve().parent / 'STAGING.json').read_text())
    assert sorted(h.git(root, env, 'diff', '--cached', '--name-only').decode().splitlines()) == staging['staged_files']
    assert hashlib.sha256(h.git(root, env, 'diff', '--cached', '--binary', '--full-index', epoch['semantic_index']['head'])).hexdigest() == staging['staged_patch_sha256']
    assert epoch['staged_working'] == staging['staged_working']
    assert all(p.startswith('artifacts/') for p in staging['staged_files'])
    assert all(hashlib.sha256(h.git(root, env, 'show', ':' + p)).hexdigest() == pin for p, pin in staging['staged_working'].items())
    native = {p for p in h.git(root, env, 'diff', '--name-only').decode().splitlines()
              if not p.startswith('artifacts/')}
    assert native == set(epoch['modified_native_paths'])
    untracked = {p for p in h.git(root, env, 'ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt').decode().splitlines()
                 if not p.startswith('artifacts/')}
    assert untracked == set(epoch['untracked_native'])
    after = h.index_state(root, env)
    assert after == before
    assert h.index_state(root / 'artifacts/css-spec-lean', env) == nested_before
    return {'index': after, 'nested_index': nested_before,
            'current_raw_stable_during_check': True,
            'working_sources_binaries_research_preserved': True}
