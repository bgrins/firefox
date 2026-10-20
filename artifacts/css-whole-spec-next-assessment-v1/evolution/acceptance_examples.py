"""Structural migration examples, not a CSS interpretation checker."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def affected(changed, consumers):
    result = set(changed)
    while True:
        new = result | {consumer for source in result for consumer in consumers.get(source, [])}
        if new == result:
            return sorted(result)
        result = new


def admissible_claim(claim, target):
    return (claim['profile'] == target['profile']
            and claim['clause'] == target['clause']
            and claim['interpretation'] == 'reviewed'
            and set(target['observers']) <= set(claim['observers'])
            and set(target['open_assumptions']) <= set(claim['open_assumptions'])
            and claim['tier'] == target['tier'])


def first_grid_stage(second_truncation):
    prefix, start, end, capacity = 2, 1, 2, 2
    stages = [('strict', prefix + start + end),
              ('lines', prefix + start + end),
              ('avoid', prefix + start + end),
              ('endClone', prefix + start),
              ('bothClone', prefix + (0 if second_truncation == 'start' else start))]
    return next((name for name, extent in stages if extent <= capacity), None)


case = json.loads((ROOT / 'change-case.json').read_text())
target = case['proposed_claim_contract']
good = dict(target, interpretation='reviewed')
checks = {}
checks['illustrative_literal_end_twice_has_no_fitting_prefix'] = first_grid_stage('end') is None
checks['ed_start_truncation_grid_prefix_fits'] = first_grid_stage('start') == 'bothClone'
checks['old_profile_stale_even_with_same_theorem'] = not admissible_claim(dict(good, profile='cr2018-literal-candidate'), target)
checks['new_profile_label_does_not_refresh_old_binding'] = not admissible_claim(dict(good, clause='old-end-again'), target)
checks['missing_observer_rejected'] = not admissible_claim(dict(good, observers=['cut-position']), target)
checks['hidden_provider_assumption_rejected'] = not admissible_claim(dict(good, open_assumptions=[]), target)
checks['ambiguous_interpretation_cannot_promote'] = not admissible_claim(dict(good, interpretation='unresolved'), target)
checks['native_tier_cannot_follow_model_replay'] = not admissible_claim(dict(good, tier='native'), target)
checks['reviewed_conditional_claim_structurally_eligible'] = admissible_claim(good, target)
checks['transitive_change_frontier'] = affected(['truncate-start'], case['consumer_edges']) == [
    'fragment-observation', 'grid-placement', 'stage-selection', 'truncate-start']
assert all(checks.values())
print(json.dumps({'status': 'PASS', 'checks': checks,
                  'limitation': 'Review states, required observer/dependency roster and interpretation are supplied; this cannot establish semantic authority.'}, indent=2))
