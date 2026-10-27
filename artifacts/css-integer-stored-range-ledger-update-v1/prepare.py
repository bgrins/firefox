import argparse
import copy
import difflib
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CURRENT = 'artifacts/stylo-bloom-tools/CURRENT-COMMITS.json'
GROUPS = 'artifacts/css-fix-readout-20261023/GROUPS.json'
CANONICAL = '162b20fb7c53a0ab89b20875a965baee98fb66bb'
META = 'testing/web-platform/meta/css/css-easing/timing-functions-syntax-computed.html.ini'
NEXT = 'Run the quote append candidate/original/candidate comparison with fresh captures and exact restoration; then integrate winning pending animation providers through the real cascade and dependency scheduler.'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.resolve().relative_to(ROOT)), 'sha256': sha(path)}


def at(obj, location):
    for key in location:
        obj = obj[key]
    return obj


def put(obj, location, value):
    at(obj, location[:-1])[location[-1]] = value


def validate(mapping, result, execution):
    expected = {r['old_commit'] for r in read(HERE / 'SEQUENCE.json')}
    assert set(mapping) == expected and len(mapping) == 37
    assert len(set(mapping.values())) == 37
    assert all(re.fullmatch('[0-9a-f]{40}', v) and v != k for k, v in mapping.items())
    assert result['status'] == 'FIX121_METADATA_HISTORY_REWRITE_VERIFIED'
    assert result['published'] is True and not result['errors']
    assert result['signatures_verified'] is True and result['final_tree_exact_carrier'] is True
    assert result['current_ledgers_modified'] is False and result['rewrites'] == mapping
    assert result['new_tip'] == mapping[read(HERE / 'SEQUENCE.json')[-1]['old_commit']]
    assert execution['exit'] == 0 and isinstance(execution['session'], int)
    assert isinstance(execution['terminal_chunk'], str) and execution['terminal_chunk']


def build(mapping, result, execution, evidence):
    validate(mapping, result, execution)
    audit = read(HERE / 'ACTIVE-LEDGER-REFERENCE-AUDIT.json')
    originals = {n: (HERE / 'before' / n).read_text() for n in audit['files']}
    docs = {n: json.loads(t) for n, t in originals.items() if n.endswith('.json')}
    old_docs = copy.deepcopy(docs)
    expected_fixes = {r['fix'] for r in read(HERE / 'CURRENT-FIX-MAPPING.json')}
    assert expected_fixes == set(range(121, 132)) | {133, 134}
    changed_fixes = set()
    summaries = {}
    for e in audit['entries']:
        n, loc, action = e['file'], e['location'], e['action']
        if n not in docs or action == 'preserve_historical_bytes':
            continue
        assert at(old_docs[n], loc) == e['old_spelling']
        if action == 'archive_original_summary_then_publish_new_current_equivalence_with_new_receipt':
            summaries.setdefault((n, loc[0]), []).append(e)
            continue
        if n == CURRENT:
            assert action == 'map_current_fix_field_from_verified_receipt'
            fix = docs[n]['new_queue'][loc[1]]['fix']
            assert fix in expected_fixes
            changed_fixes.add(fix)
        elif loc[0] == 'groups':
            assert docs[n]['groups'][loc[1]]['fixes'][loc[3]]['fix'] in expected_fixes
        put(docs[n], loc, mapping[e['old_commit']])
    assert changed_fixes == expected_fixes
    for (n, key), entries in summaries.items():
        original = old_docs[n][key]
        docs[n].setdefault('pre_fix121_rewrite_summaries', {})[key] = original
        equivalents = [{'location': e['location'][1:], 'old_commit': e['old_commit'],
                        'current_commit': mapping[e['old_commit']]} for e in entries]
        docs[n][key] = {'status': 'CURRENT_EQUIVALENTS_AFTER_VERIFIED_HISTORY_REWRITE',
                        'original_summary': ['pre_fix121_rewrite_summaries', key],
                        'equivalents': equivalents, 'rewrite_evidence': evidence}
    cur, groups = docs[CURRENT], docs[GROUPS]
    for n, records in [(CURRENT, cur['new_queue']), (GROUPS, [f for g in groups['groups'] for f in g['fixes']])]:
        for item in records:
            if item.get('fix') not in expected_fixes:
                continue
            if 'commit_verification' in item:
                item['pre_fix121_rewrite_commit_verification'] = item['commit_verification']
            item['commit_verification'] = evidence['result']
            if item['fix'] == 121:
                for key in ['native_paths', 'wpt_paths']:
                    if key in item and META not in item[key]:
                        item[key].append(META)
                item['metadata_fold'] = {'path': META, 'validation': 'artifacts/css-integer-stored-range-metadata-runtime-v1',
                                         'historical_patch_refs_unchanged': True, 'new_bug': False}
    assert cur['committed_native_fixes'] == groups['committed'] == 133
    groups['accepted'] = 133
    groups['head'] = result['new_tip']
    cur['current_history_rewrite'] = {'evidence': evidence, 'head': result['new_tip'],
                                      'affected_fixes': sorted(expected_fixes), 'accepted_count': 133}
    model = {'status': 'STEPS_ORIGIN_LIBRARY_FULL_CHECK_PASS', 'canonical_head': CANONICAL,
             'audits': 11840, 'cases': 12438, 'false_cases': 173, 'sources': 2155,
             'transferred_audits': 10, 'new_proof_discovery_credit': 0,
             'normative_coverage_delta': 0, 'native_refinement_proved': False,
             'directory': 'artifacts/css-steps-origin-library-application-runtime-v1',
             'terminal_review': 'artifacts/css-steps-origin-library-application-terminal-review-v1',
             'session': 36634, 'exit': 0, 'terminal': 'ddca02'}
    cur.setdefault('model_audit_history', []).append(copy.deepcopy(cur['active_model_audit']))
    cur['active_model_audit'] = model
    groups.setdefault('formal_library_checkpoint_history', []).append(copy.deepcopy(groups['formal_library_checkpoint']))
    groups['formal_library_checkpoint'] = model
    cur.setdefault('native_experiment_history', []).append(copy.deepcopy(cur['active_native_experiment']))
    cur['active_native_experiment'] = {'status': 'PROVIDER_RESOLVER_HOST_19_TESTS_VERIFIED',
        'directory': 'artifacts/css-keyframe-provider-resolver-host-runtime-v1', 'session': 48224,
        'exit': 0, 'terminal': 'ced012', 'native_tests_pass': 19, 'normal_producer_enabled': False,
        'terminal_review': 'artifacts/css-keyframe-provider-resolver-host-terminal-review-v1',
        'new_accepted_fixes': 0, 'remaining': 'Current winning-provider scheduling, base-value freshness, animated-cycle semantics and complete dependency/memory reporting; five variant documentation warnings remain.'}
    cur.setdefault('metadata_correction_history', []).extend(copy.deepcopy(cur.get('pending_metadata_corrections', [])))
    cur['pending_metadata_corrections'] = [x for x in cur.get('pending_metadata_corrections', []) if x['fix'] != 121]
    cur['latest_metadata_validation'] = {'fix': 121, 'status': 'VALIDATED_AND_FOLDED', 'subtests': 113,
        'PASS': 110, 'expected_FAIL': 3, 'changed_expectations': 1, 'other_expectations_exact': 112,
        'new_bug': False, 'runtime': 'artifacts/css-integer-stored-range-metadata-runtime-v1', 'rewrite_evidence': evidence}
    cur.setdefault('signing_next_action_history', []).append(copy.deepcopy(cur['signing_next_action']))
    cur['signing_next_action'] = NEXT
    for n, old in old_docs.items():
        for k, v in old.items():
            if k.startswith('previous') or 'history' in k:
                if isinstance(v, list):
                    assert docs[n][k][:len(v)] == v, k
                else:
                    assert docs[n][k] == v, k
    for e in audit['entries']:
        if e['action'] == 'preserve_historical_bytes':
            n, loc = e['file'], e['location']
            source = docs[n]['pre_fix121_rewrite_summaries'][loc[0]] if (n, loc[0]) in summaries else docs[n]
            assert at(source, loc[1:] if (n, loc[0]) in summaries else loc) == e['old_spelling']
    texts = dict(originals)
    for n in texts:
        if n in docs:
            continue
        lines = texts[n].splitlines(keepends=True)
        edits = {}
        for e in audit['entries']:
            if e['file'] == n:
                assert e['action'] == 'review_current_prose_or_group_reference_then_map_only_current_claim'
                edits.setdefault(e['location']['line'] - 1, []).append(e)
        for i, entries in edits.items():
            assert lines[i].rstrip('\n') == entries[0]['location']['text']
            for e in entries:
                lines[i] = lines[i].replace(e['old_spelling'], mapping[e['old_commit']][:len(e['old_spelling'])])
        texts[n] = ''.join(lines)
    receipt_link = '../../' + evidence['result']['path']
    intro = ('Fix 121 now includes its validated one-block expectation correction. The signed history rewrite preserves the final tree; current commit IDs below come from the [new rewrite receipt](' + receipt_link + '). Historical signing receipts retain their original IDs. All 133 accepted fixes remain committed; held repair 120 stays excluded.\n')
    checkpoint = ('The callable current-provider resolver passed the normal and GTest builds and all 19 native tests; normal pending recipe production remains disabled. The 113-case metadata comparison preserved all 110 PASS and three expected FAIL observations, changing only the fix 121 expectation. The canonical library is signed at `' + CANONICAL + '` and its full check passes 11,840 audits, 12,438 cases, 173 expected-false cases and 2,155 source fingerprints. Ten audits transfer from reviewed steps research, with no new discovery, normative coverage or native-refinement credit.\n\nNext: ' + NEXT + ' Preserve unresolved animated-cycle policy, current underlying-value provenance, dependency publication and memory-reporting obligations.\n')
    for n in texts:
        if n in docs:
            continue
        text = texts[n]
        start = text.index('Latest signed fixes:')
        end = text.index('\n', start)
        text = text[:start] + intro.rstrip('\n') + text[end:]
        if n.endswith('PLAN-OF-RECORD.md'):
            start = text.index('## Latest verified work')
            end = text.index('## Historical record')
            text = text[:start] + '## Latest verified work\n\n' + checkpoint + '\n## Execution order\n\n1. Run fresh quote append candidate/original/candidate captures and exact control/restoration checks.\n2. Continue the full animation pending-provider integration through winning cascade gates; do not replace scheduling with preselected provider snapshots.\n3. Preserve Bloom milestones 1–6 and scoped specification correspondence; keep accepted fixes and their research separately reviewable.\n\n' + text[end:]
        elif n.endswith('css-fix-readout-20261023/README.md'):
            start = text.index('The descriptor/operation prototype passed')
            end = text.index('Historical checkpoint text follows')
            text = text[:start] + checkpoint + '\n' + text[end:]
        else:
            text = text.replace(intro.rstrip('\n'), intro.rstrip('\n') + '\n\n' + checkpoint.rstrip('\n'), 1)
        texts[n] = text
    texts.update({n: json.dumps(d, indent=2) + '\n' for n, d in docs.items()})
    return originals, texts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rewrite-map', type=Path, required=True)
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--execution', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(ROOT / 'artifacts') and not output.exists()
    for n, h in read(HERE / 'BEFORE-PINS.json').items():
        assert sha(HERE / 'before' / n) == h and sha(ROOT / n) == h, n
    evidence = {k: ref(getattr(args, k)) for k in ['rewrite_map', 'result', 'execution']}
    before, after = build(read(args.rewrite_map), read(args.result), read(args.execution), evidence)
    output.mkdir()
    diff = []
    for n, text in after.items():
        for sub, body in [('before', before[n]), ('candidate', text)]:
            dest = output / sub / n
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(body)
        diff.extend(difflib.unified_diff(before[n].splitlines(True), text.splitlines(True), fromfile='a/' + n, tofile='b/' + n))
    (output / 'ledger.patch').write_text(''.join(diff))
    (output / 'REFERENCES.json').write_text(json.dumps(evidence, indent=2) + '\n')
    (output / 'CHECK.json').write_text(json.dumps({'status': 'FIX121_LEDGER_CANDIDATES_PREPARED',
        'live_writes': False, 'affected_fix_count': 13, 'accepted_fixes': 133,
        'postimages': {n: hashlib.sha256(t.encode()).hexdigest() for n, t in after.items()}}, indent=2) + '\n')
    (output / 'FILES.json').write_text(json.dumps({str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*')) if p.is_file()}, indent=2) + '\n')


if __name__ == '__main__':
    main()
