import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
DRAFT = ROOT / 'artifacts/css-attr-raw-nested-ledger-plan-v1'
PROPOSAL = ROOT / 'artifacts/css-attr-raw-nested-repair-v2'
CAPSULE = ROOT / 'artifacts/css-attr-raw-nested-wpt-capsule-v3'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
PREREQUISITE = 'aa3f0588538800300df20a2f7de40ce8ac2ffec1'
PATHS = ['artifacts/stylo-bloom-tools/CURRENT-COMMITS.json',
         'artifacts/css-fix-readout-20261023/GROUPS.json',
         'artifacts/stylo-bloom-tools/BUGFIX-COMMITS.md',
         'artifacts/css-fix-readout-20261023/README.md',
         'artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def ref(path):
    return {'path': str(path.resolve().relative_to(ROOT)), 'sha256': sha(path)}


def body(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=ENV)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def once(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after, 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--signing-dir', type=Path, required=True)
    for name in ('acceptance', 'native-receipt', 'tools-receipt', 'validation-receipt',
                 'epoch', 'original-assessment', 'candidate-assessment'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--epoch-sha256', required=True)
    args = parser.parse_args()
    assert all(not os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE',
        'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    assert git('symbolic-ref', 'HEAD').decode().strip() == 'refs/heads/stylo-bloom-verification-2'
    signing = args.signing_dir.resolve()
    assert signing.is_relative_to(ROOT / 'artifacts') and signing.is_dir()
    assert not (signing / 'raw-ledger-preimages').exists()
    assert not (signing / 'RAW-LEDGER-UPDATE.json').exists()
    assert args.epoch.resolve() == signing / 'CURRENT-EPOCH.json'
    assert sha(args.epoch) == args.epoch_sha256
    epoch_bytes = args.epoch.read_bytes()
    epoch = json.loads(epoch_bytes)
    input_paths = (args.acceptance, args.native_receipt, args.tools_receipt, args.validation_receipt,
                   args.original_assessment, args.candidate_assessment)
    evidence_pins = {str(p.resolve().relative_to(ROOT)): sha(p) for p in input_paths}
    h = load('preserve', 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
    a = load('epoch', 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
    before_state = a.verify_current(h, ROOT, ENV, epoch)
    flags = {p: h.git(ROOT / p, ENV, 'ls-files', '-v', '-z') for p in ('.', 'artifacts/css-spec-lean')}
    tracked = {p: h.git(ROOT / p, ENV, 'ls-files', '-f', '-z') for p in flags}
    assert sha(DRAFT / 'FILES.json') == 'fc425b68a3fbcf068382cffd407beca393bdf07e4ec4e94dc8ddead7ce3a22bd'
    for name, pin in read(DRAFT / 'FILES.json').items():
        assert sha(DRAFT / name) == pin['sha256'], name
    for directory, expected in ((PROPOSAL, '3ec8cab27096244ce30b8cbaea3af19f73c542a5658f9d9b9fbe9c396fd6ba79'),
                                (CAPSULE, '46eee2d63d2d063f4fdf5f1b48fb8dd9baf2e9d809511d7f46da3819f46caff5')):
        assert sha(directory / 'FILES.json') == expected
        for name, pin in read(directory / 'FILES.json').items():
            assert sha(directory / name) == (pin['sha256'] if isinstance(pin, dict) else pin), name
    old = {name: (ROOT / name).read_bytes() for name in PATHS}
    assert {name: hashlib.sha256(value).hexdigest() for name, value in old.items()} == read(DRAFT / 'LEDGER-PREIMAGES.json')
    assert all(any(name in epoch[key] for key in ('pins', 'staged_working', 'committed_research_working_payloads')) for name in PATHS)
    native, tools, validation = [read(p) for p in (args.native_receipt, args.tools_receipt, args.validation_receipt)]
    assert all(r['signature_verified'] for r in (native, tools, validation))
    assert native['parent'] == validation['commit'] and validation['parent'] == tools['commit']
    assert native['exact_remaining_diff_verified'] and native['all_epoch_pins_and_working_bodies_preserved']
    assert git('rev-parse', 'HEAD').decode().strip() == native['commit']
    for receipt in (native, tools, validation):
        commit = receipt['commit']
        assert git('rev-list', '--parents', '-n', '1', commit).decode().split() == [commit, receipt['parent']]
        assert git('rev-parse', commit + '^{tree}').decode().strip() == receipt['tree']
        git('-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / 'artifacts/css-local-signing-20261027-v1/allowed-signers'), 'verify-commit', commit)
    for receipt in (tools, validation):
        paths = git('diff-tree', '--no-commit-id', '--name-only', '-r', receipt['commit']).decode().splitlines()
        assert paths == sorted(receipt['files']) and all(p.startswith('artifacts/') for p in paths)
    git('merge-base', '--is-ancestor', PREREQUISITE, native['parent'])
    acceptance = read(args.acceptance)
    assert acceptance['status'] == 'READY_FOR_STANDALONE_SIGNED_COMMIT' and acceptance['fix'] == 138
    assert acceptance['canonical_lean_increment'] == 0 and acceptance['native_refinement_proved'] is False
    entry = read(DRAFT / 'ENTRY-TEMPLATE.json')
    assert sorted(native['paths']) == sorted(acceptance['native_paths']) == sorted(entry['native_paths'])
    assert git('diff-tree', '--no-commit-id', '--name-only', '-r', native['commit']).decode().splitlines() == sorted(entry['native_paths'])
    assert acceptance['validated_patch'] == entry['patch'] and sha(PROPOSAL / 'fix.patch') == entry['patch']['sha256']
    for name in entry['native_paths']:
        role = 'head-candidate' if name.endswith('.rs') else 'candidate'
        expected = (PROPOSAL / role / name).read_bytes()
        assert git('show', native['commit'] + ':' + name) == expected
        assert git('ls-tree', native['commit'], '--', name).decode().split()[0] == '100644'
    review = acceptance['terminal_review']
    assert sha(ROOT / review['path']) == review['sha256']
    original, candidate = read(args.original_assessment), read(args.candidate_assessment)
    for name, digest in candidate['native_sources'].items():
        assert epoch['pins'][name] == digest
    assert candidate['native_sources']['servo/components/style/properties/cascade.rs'] == sha(PROPOSAL / 'candidate/servo/components/style/properties/cascade.rs')
    assert candidate['native_sources']['servo/components/style/custom_properties.rs'] == read(PROPOSAL / 'BASE.json')['helper_sha256']
    candidate_binaries = args.candidate_assessment.parent / 'NORMAL-BINARIES.json'
    evidence_pins[str(candidate_binaries.resolve().relative_to(ROOT))] = sha(candidate_binaries)
    for name, digest in read(candidate_binaries).items():
        assert epoch['pins'][name] == digest
    policy = read(CAPSULE / 'POLICY.json')
    capsule_sha = sha(CAPSULE / 'FILES.json')
    assert capsule_sha == '46eee2d63d2d063f4fdf5f1b48fb8dd9baf2e9d809511d7f46da3819f46caff5'
    target_ids = {(t, n) for t, names in policy['target_subtests'].items() for n in names}
    regression_ids = {(t, n) for t, names in policy['regression_subtests'].items() for n in names}
    assert len(target_ids) == 73 and len(regression_ids) == 329
    maps = []
    for assessment in (original, candidate):
        assert assessment['capsule_manifest_sha256'] == capsule_sha
        assert assessment['complete'] and assessment['execution_preserved']
        assert not assessment['errors'] and not assessment['infrastructure_faults']
        rows = {(r['test'], r['subtest']): r['status'] for r in assessment['rows']}
        assert len(rows) == len(assessment['rows']) == 402 and rows.keys() == target_ids | regression_ids
        assert all(rows[k] == 'PASS' for k in regression_ids)
        assert sum(e['status'] == 'PASS' and policy['tests'][e['test']] == 'reftest' for e in assessment['ends']) == 6
        maps.append(rows)
    assert candidate['comparison_gate_passed'] and not candidate['comparison_errors']
    assert all(maps[1][k] == 'PASS' for k in target_ids)
    assert original['regression_signature'] == candidate['regression_signature']
    phase_counts = [[sum(rows[k] == status for k in target_ids) for status in ('PASS', 'FAIL')] for rows in maps]
    assert all(sum(count) == 73 for count in phase_counts)
    repaired = sum(maps[0][k] == 'FAIL' and maps[1][k] == 'PASS' for k in target_ids)
    controls = sum(maps[0][k] == maps[1][k] == 'PASS' for k in target_ids)
    regressions = {'subtests_PASS': 329, 'reftests_PASS': 6, 'exact_both_phases': True}
    assert acceptance['phase_counts'] == phase_counts
    assert acceptance['observed_repairs'] == repaired and acceptance['unchanged_controls'] == controls
    assert acceptance['existing_regressions'] == regressions
    assert acceptance['phase_order'] == [original['phase'], candidate['phase']]
    entry.update(status='COMMITTED_NATIVE_WPT', native_commit=native['commit'], research_commit=validation['commit'],
        companion_commit=validation['commit'], phase_order=acceptance['phase_order'], phase_counts=phase_counts,
        observed_repairs=repaired, unchanged_landing_controls=controls, existing_regressions=regressions,
        terminal_review=review, acceptance=ref(args.acceptance), commit_verification=ref(args.native_receipt),
        research_commit_verification=ref(args.validation_receipt), candidate_source_installed=True,
        browser_binary_contains_fix=True, signature_verified=True,
        comparison_runtime=[str(p.resolve().parent.relative_to(ROOT)) for p in (args.original_assessment, args.candidate_assessment)])
    for name in entry['native_paths']:
        assert sha(ROOT / name) == sha(PROPOSAL / 'candidate' / name)
    ledger = json.loads(old[PATHS[0]])
    previous_ledger = copy.deepcopy(ledger)
    assert ledger['committed_native_fixes'] == 136 and all(x.get('fix') != 138 for x in ledger['new_queue'])
    assert ledger['accepted_pending_native_fixes'] == ledger['accepted_pending_native_fixes_on_hold'] == 1
    assert ledger['accepted_pending_native_fixes_excluding_holds'] == 0
    ledger['new_queue'].append(entry)
    ledger['committed_native_fixes'] = 137
    ledger.setdefault('local_signing_history', []).append(copy.deepcopy(ledger['latest_signing']))
    ledger['latest_signing'] = {'status': 'SIGNED_VERIFIED_LOCAL', 'fix': 138, 'native_commit': native['commit'],
        'research_commit': validation['commit'], 'verification': ref(args.native_receipt)}
    ledger.setdefault('research_signing_history', []).append(copy.deepcopy(ledger['latest_research_signing']))
    ledger['previous_research_signing'] = copy.deepcopy(ledger['latest_research_signing'])
    ledger['latest_research_signing'] = {'status': 'SIGNED_VERIFIED_LOCAL', 'commits': {
        'raw-tools': tools['commit'], 'raw-validation': validation['commit']}, 'directory': str(signing.relative_to(ROOT))}
    ledger.setdefault('verified_working_epoch_history', []).append(copy.deepcopy(ledger['latest_verified_working_epoch']))
    binary_fixes = ledger['latest_verified_working_epoch']['browser_binary_contains_fixes']
    ledger['latest_verified_working_epoch'] = {'path': str(args.epoch.resolve().relative_to(ROOT)),
        'status': 'Signed raw-nested fix; fresh 73-target comparison passed with exact regressions',
        'browser_binary_contains_fixes': sorted(set(binary_fixes) | {138})}
    ledger['latest_raw_attribute_fix'] = {'fix': 138, 'acceptance': ref(args.acceptance), 'commit_verification': ref(args.native_receipt)}
    ledger.setdefault('cycle_repair_queue_history', []).append(copy.deepcopy(ledger['cycle_repair_queue']))
    ledger['cycle_repair_queue']['raw_nested_attr'] = copy.deepcopy(entry)
    ledger['cycle_repair_queue']['status'] = 'USED_FALLBACK_AND_RAW_NESTED_COMMITTED_REGISTERED_NUMBER_UNACCEPTED'
    ledger['cycle_repair_queue']['next'] = 'Continue registered-number investigation and pending-provider integration; preserve fixes137 and138 separately.'
    ledger['signing_next_action'] = ledger['cycle_repair_queue']['next']
    assert ledger['new_queue'][:-1] == previous_ledger['new_queue']
    assert ledger['cycle_repair_queue']['used_attr_fallback'] == previous_ledger['cycle_repair_queue']['used_attr_fallback']
    assert ledger['cycle_repair_queue']['registered_number'] == previous_ledger['cycle_repair_queue']['registered_number']
    groups = json.loads(old[PATHS[1]])
    previous_groups = copy.deepcopy(groups)
    assert groups['committed'] == groups['accepted'] == 136 and groups['tracked'] == 137
    for group in groups['groups']:
        if group['group'] == entry['group']:
            assert group['committed'] == group['total'] == 17
            group['fixes'].append(copy.deepcopy(entry))
            group['committed'] = group['total'] = 18
    groups.update(head=native['commit'], committed=137, accepted=137, tracked=138)
    assert sum(g['committed'] for g in groups['groups']) == 137
    for key in ('held', 'accepted_pending', 'formal_library_checkpoint', 'formal_library_checkpoint_history'):
        assert groups[key] == previous_groups[key]
    for before, after in zip(previous_groups['groups'], groups['groups']):
        assert before['fixes'] == (after['fixes'][:-1] if after['group'] == entry['group'] else after['fixes'])
    new = {PATHS[0]: body(ledger), PATHS[1]: body(groups)}
    summary = (f"Fix 138, raw nested attribute cycles, is committed as `{native['commit']}` after research `{validation['commit']}`. "
        f"The fresh original/candidate comparison changes {phase_counts[0][0]} PASS + {phase_counts[0][1]} FAIL to 73 PASS; "
        "all 329 regression assertions and six reftests remain passing. The three-file fix requires fix 137. "
        "Three historical oracle corrections are explicit, including EOF recovery; metadata is unchanged. "
        "The earlier 66-target candidate failure remains recorded. Source/spec audit and browser reproduction found the issue. "
        "Parsing and EOF recovery remain outside the normalized Lean guard proof; no canonical coverage or native-refinement credit is added.")
    for name in PATHS[2:]:
        text = old[name].decode()
        title, rest = text.split('\n', 1)
        text = title + '\n\n' + summary + '\n' + rest
        for before, after in (
            ('**136 accepted fixes: 136 committed locally, 0 accepted pending, and 1 additional held repair excluded.**',
             '**137 accepted fixes: 137 committed locally, 0 accepted pending, and 1 additional held repair excluded.**'),
            ('| Attributes and custom properties | 17 | 0 |', '| Attributes and custom properties | 18 | 0 |'),
            ('| **Total** | **136** | **0** |', '| **Total** | **137** | **0** |'),
            ('All 135 accepted fixes remain committed; held repair 120 stays excluded.',
             'All 137 accepted fixes remain committed; held repair 120 stays excluded.')):
            text = once(text, before, after)
        if name.endswith('PLAN-OF-RECORD.md'):
            old_status = 'The used bare/unit attribute fallback defect is now fixed and committed as fix 137. The raw-nested lead still has five reproduced discrepancies and eight controls; its reviewed proposal explicitly corrects two old WPT expectations and adds 29 tests, but is not browser-validated. Registered-number comparison still shows seven shared discrepancies and one additional local prototype control failure. Those remaining leads are unaccepted.'
            text = once(text, old_status, 'Used-fallback fix 137 and raw-nested fix 138 are signed separately. The latter passes the fresh 73-target comparison (37 existing and 36 new), including three explicitly corrected oracles. Registered-number discrepancies and the additional local prototype control failure remain unaccepted.')
            text = once(text, '2. Build and validate the reviewed raw-nested repair and 29-case WPT, including explicit correction of two historical attr-cycle expectations.',
                '2. Preserve fix 138 and its explicit oracle/EOF evidence, its fix 137 prerequisite, and the failed earlier comparison; continue remaining registered-number and pending-provider work.')
        else:
            marker = '| 137: Used non-type attr fallback cycles |'
            text = once(text, marker, f"| 138: Raw nested attr cycles | `{native['commit']}` | `{validation['commit']}` |\n" + marker)
        new[name] = text.encode()
    assert set(new) == set(PATHS)
    assert a.verify_current(h, ROOT, ENV, epoch) == before_state
    assert sha(args.epoch) == args.epoch_sha256
    assert {name: sha(ROOT / name) for name in evidence_pins} == evidence_pins
    assert {name: (ROOT / name).read_bytes() for name in PATHS} == old
    backup = signing / 'raw-ledger-preimages'
    backup.mkdir()
    (backup / 'EPOCH.json').write_bytes(epoch_bytes)
    for name in PATHS:
        path = backup / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(old[name])
    (backup / 'INPUTS.json').write_bytes(body(evidence_pins))
    for name in PATHS:
        (ROOT / name).write_bytes(new[name])
    updated = copy.deepcopy(epoch)
    for name in PATHS:
        for key in ('pins', 'staged_working', 'committed_research_working_payloads'):
            if name in updated[key]:
                updated[key][name] = sha(ROOT / name)
    state = h.index_state(ROOT, ENV)
    for key in ('head', 'entries', 'cached_diff', 'raw_index'):
        assert state[key] == before_state['index'][key]
    updated['semantic_index'] = h.semantic_index(state)
    updated['raw_index_observation']['current'] = state['raw_index']
    after = a.verify_current(h, ROOT, ENV, updated)
    assert after['nested_index'] == before_state['nested_index']
    assert all(h.git(ROOT / p, ENV, 'ls-files', '-v', '-z') == value for p, value in flags.items())
    assert all(h.git(ROOT / p, ENV, 'ls-files', '-f', '-z') == value for p, value in tracked.items())
    assert {name: (ROOT / name).read_bytes() for name in PATHS} == new
    assert {name: sha(ROOT / name) for name in evidence_pins} == evidence_pins
    assert sha(args.epoch) == args.epoch_sha256
    args.epoch.write_text(json.dumps(updated, indent=2, sort_keys=True) + '\n')
    with (signing / 'RAW-LEDGER-UPDATE.json').open('x') as stream:
        json.dump({'native_commit': native['commit'], 'research_commit': validation['commit'],
            'accepted_committed': 137, 'tracked': 138, 'held': 1, 'attributes_group': 18,
            'prior_entries_preserved': True, 'canonical_checkpoint_preserved': True,
            'files': PATHS, 'full_preservation_verified': True,
            'postimages': {name: sha(ROOT / name) for name in PATHS}}, stream, indent=2)
        stream.write('\n')
    print('Updated five ledgers:137 committed,138 tracked;held120 excluded')


if __name__ == '__main__':
    main()
