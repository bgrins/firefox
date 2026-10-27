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
NEXT = 'Integrate winning pending animation providers through the real cascade and dependency scheduler; preserve explicit current-base, cycle-policy, dependency-publication and memory-reporting obligations.'
OLD_NEXT = 'Run the quote append candidate/original/candidate comparison with fresh captures and exact restoration; then integrate winning pending animation providers through the real cascade and dependency scheduler.'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def validate(binding):
    assert binding['ready'] is True and binding['terminal_GO'] is True
    assert binding['signatures_verified'] is True
    for key in ['research_commit', 'native_commit']:
        assert re.fullmatch('[0-9a-f]{40}', binding[key])
    assert binding['native_commit'] != binding['research_commit']
    assert binding['phase_counts'] == [[64, 0], [52, 12], [64, 0]]
    assert binding['existing_regressions'] == {'PASS': 15, 'expected_FAIL': 3, 'exact_all_phases': True}
    for key in ['terminal_review', 'signing_verification']:
        ref = binding[key]
        path = (ROOT / ref['path']).resolve()
        assert path.is_relative_to(ROOT / 'artifacts') and sha(path) == ref['sha256']


def candidates(binding):
    before = {n: (HERE / 'before' / n).read_text() for n in read(HERE / 'BEFORE-PINS.json')}
    after = dict(before)
    current, groups = json.loads(before[CURRENT]), json.loads(before[GROUPS])
    old_current, old_groups = copy.deepcopy(current), copy.deepcopy(groups)
    assert current['committed_native_fixes'] == groups['accepted'] == groups['committed'] == 133
    assert all(x.get('fix') != 135 for x in current['new_queue'])
    entry = {
        'fix': 135, 'repair': 'contained-quote-append-invalidation',
        'status': 'COMMITTED_NATIVE_WPT', 'group': 'Text and fonts',
        'native_commit': binding['native_commit'], 'research_commit': binding['research_commit'],
        'native_paths': ['layout/base/nsQuoteList.cpp', 'layout/base/nsQuoteList.h',
                         'testing/web-platform/tests/css/css-contain/quote-scoping-append-invalidation.html'],
        'phase_order': ['candidate', 'scoped_original', 'candidate_restored'],
        'phase_counts': binding['phase_counts'], 'observed_repairs': 12,
        'landing_cases': 64, 'unchanged_landing_controls': 52,
        'existing_regressions': binding['existing_regressions'],
        'terminal_review': binding['terminal_review'], 'commit_verification': binding['signing_verification'],
        'triage': 'Tentative P3 visual correctness; no demonstrated security impact.',
        'discovery': 'Source audit and controlled browser reproduction; not a proof-discovered bug.',
        'formal_attribution': 'Conditional Lean delivery and ordered-scope models corroborate the dependency argument. Uniform provider, actual native traversal/delivery, cache coherence and machine arithmetic remain correspondence premises; no universal native refinement or new canonical coverage credit.',
        'limits': ['Shared experimental checkout; no clean-upstream browser build claim.',
                   'Three existing regression expected failures remain unchanged.',
                   'Raw index bytes may refresh under exact semantic and flags guards; cause is not established.',
                   'Adjacent counter append hypothesis is unrun and not included in this fix.']}
    current['new_queue'].append(entry)
    current['committed_native_fixes'] = 134
    current.setdefault('signing_next_action_history', []).append(current['signing_next_action'])
    current['signing_next_action'] = NEXT
    current['latest_quote_fix'] = {'fix': 135, 'terminal_review': binding['terminal_review'],
                                  'commit_verification': binding['signing_verification']}
    text_group = next(g for g in groups['groups'] if g['group'] == 'Text and fonts')
    text_group['fixes'].append(copy.deepcopy(entry))
    text_group['committed'] = text_group['total'] = 14
    animation = next(g for g in groups['groups'] if g['group'] == 'Animations, timelines and transitions')
    assert animation['total'] == 14 and len(animation['fixes']) == animation['committed'] == 16
    animation['total'] = 16
    groups.update(head=binding['native_commit'], committed=134, accepted=134)
    groups['tracked'] = sum(g['total'] for g in groups['groups'])
    assert groups['tracked'] == 135 and sum(g['committed'] for g in groups['groups']) == 134
    assert current['new_queue'][:-1] == old_current['new_queue']
    for old, new in zip(old_groups['groups'], groups['groups']):
        assert new['fixes'][:len(old['fixes'])] == old['fixes']
    for old, new in [(old_current, current), (old_groups, groups)]:
        for key, value in old.items():
            if key.startswith('previous') or 'history' in key:
                assert (new[key][:len(value)] == value) if isinstance(value, list) else new[key] == value
    after[CURRENT] = json.dumps(current, indent=2) + '\n'
    after[GROUPS] = json.dumps(groups, indent=2) + '\n'
    paragraph = (f"Fix 135, contained quote append invalidation, is committed as `{binding['native_commit']}` after research `{binding['research_commit']}`. The candidate/original/candidate comparison gives 64 PASS / 52 PASS + 12 FAIL / 64 PASS, with all 18 existing regressions unchanged (15 PASS and three expected FAIL). Tentative P3 visual correctness. Discovery came from source audit and browser reproduction; conditional Lean models corroborate scope/dependency laws, not universal native correctness. No clean-upstream build, security or measured performance claim. The adjacent counter hypothesis remains unrun and uncounted.\n\n")
    for name in before:
        if name.endswith('.json'):
            continue
        text = before[name]
        text = text.replace('**133 accepted fixes: 133 committed locally, 0 accepted pending, and 1 additional held repair excluded.**', '**134 accepted fixes: 134 committed locally, 0 accepted pending, and 1 additional held repair excluded.**', 1)
        text = text.replace('All 133 accepted fixes remain committed;', 'All 134 accepted fixes remain committed;', 1)
        text = text.replace('| Text and fonts | 13 | 0 |', '| Text and fonts | 14 | 0 |', 1)
        text = text.replace('| **Total** | **133** | **0** |', '| **Total** | **134** | **0** |', 1)
        text = text.replace(OLD_NEXT, NEXT, 1)
        title_end = text.index('\n') + 1
        text = text[:title_end] + '\n' + paragraph + text[title_end:]
        if name.endswith('PLAN-OF-RECORD.md'):
            text = text.replace('1. Run fresh quote append candidate/original/candidate captures and exact control/restoration checks.', '1. Keep quote fix 135 and its research separately reviewable; retain its exact comparison evidence.', 1)
        after[name] = text
    return before, after


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--binding', type=Path)
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.preview != bool(args.binding)
    output = args.output.resolve()
    assert output.is_relative_to(ROOT / 'artifacts') and not output.exists()
    for n, digest in read(HERE / 'BEFORE-PINS.json').items():
        assert sha(HERE / 'before' / n) == digest and sha(ROOT / n) == digest, n
    binding = read(HERE / 'BINDING.template.json') if args.preview else read(args.binding)
    if args.preview:
        binding.update(native_commit='PENDING_NATIVE_COMMIT', research_commit='PENDING_RESEARCH_COMMIT',
                       terminal_review={'path': 'PENDING_TERMINAL_GO', 'sha256': None},
                       signing_verification={'path': 'PENDING_SIGNED_COMMIT_VERIFICATION', 'sha256': None})
    else:
        validate(binding)
    before, after = candidates(binding)
    output.mkdir()
    delta = []
    for name, body in after.items():
        dest = output / 'candidate' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body)
        delta.extend(difflib.unified_diff(before[name].splitlines(True), body.splitlines(True), fromfile='a/' + name, tofile='b/' + name))
    (output / 'ledger.patch').write_text(''.join(delta))
    (output / 'BINDING.json').write_text(json.dumps(binding, indent=2) + '\n')
    (output / 'CHECK.json').write_text(json.dumps({'status': 'PREVIEW_NOT_FOR_APPLICATION' if args.preview else 'CANDIDATES_READY_FOR_ROOT_REVIEW', 'live_writes': False, 'postimages': {n: hashlib.sha256(s.encode()).hexdigest() for n, s in after.items()}}, indent=2) + '\n')


if __name__ == '__main__':
    main()
