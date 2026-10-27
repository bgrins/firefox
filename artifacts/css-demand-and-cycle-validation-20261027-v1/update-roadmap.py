import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EP = ROOT / 'artifacts/css-keyframe-typed-attribute-demand-runtime-v1/CURRENT-EPOCH.json'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

h = load('preserve', 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a = load('epoch', 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
read = lambda path: json.loads(path.read_text())
epoch = read(EP)
a.verify_current(h, ROOT, ENV, epoch)
assert read(ROOT / 'artifacts/css-keyframe-demand-ordinary-wpt-runtime-v1/RESULT.json')['regression_gate_passed']
names = ['artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md', 'artifacts/stylo-bloom-tools/CURRENT-COMMITS.json']
old = {name: (ROOT / name).read_bytes() for name in names}
plan = old[names[0]].decode()
start = plan.index('The signed animation research now includes')
end = plan.index('\n\nFix 135', start)
plan = plan[:start] + 'The typed-demand prototype now passes its full native build, 20 native tests including 22 new real-resolver calls, and four ordinary WPTs (253 PASS, three existing expected FAIL; no unexpected results). Production pending-provider integration remains unfinished and disabled. The versioned var-fallback trace does not cover the newly observed attribute and unit dependency failures. Canonical Lean coverage counts are unchanged.' + plan[end:]
start = plan.index('The callable current-provider resolver passed')
end = plan.index('## Historical record', start)
plan = plan[:start] + '''The callable typed-demand resolver passed all 20 selected GTests across four suites. Four ordinary substitution WPTs produced 256 subtests (253 PASS and three existing expected FAIL), four OK harness endings and no unexpected results. Source/resource/metadata and root/nested preservation checks passed. See [validation checkpoint](../css-demand-and-cycle-validation-20261027-v1/REPORT.md).

Both attribute-cycle leads reproduce in release Firefox 158 and local Nightly 160: five raw-nested disagreements with eight controls, and seven used bare/unit fallback disagreements with six controls. A registered-number comparison shows seven shared discrepancies and one additional local prototype control failure. These are repair targets, not accepted fixes.

The signed substitution-completion model has 17 audits, 16 kernel examples and six rejected false claims, independently replayed. It proves already-settled outcomes stable under coherent completion, not native scheduler confluence or full CSS semantics. The canonical library remains at `162b20fb7c53a0ab89b20875a965baee98fb66bb` with previously verified 11,840 audits, 12,438 cases, 173 expected-false cases and 2,155 source fingerprints; this turn did not rerun or expand those counts.

## Execution order

1. Validate and commit a minimal used bare/unit attribute fallback cycle repair with its WPT and preceding evidence. Preserve quote fix 135 and counter fix 136 separately.
2. Repair raw nested attribute false cycles after explicit review of the existing WPT oracle.
3. Complete actual winning pending-provider collection and joint ordinary/animated/prioritary resolution, preserving current-base freshness, cycle policy, isolated endpoint contexts, effect publication and memory reporting. The single-collector and disposable-context proposals remain uncompiled.
4. Resolve registered-number false dependencies while retaining real numeric math operands; distinguish the additional local prototype failure from release defects.
5. Preserve Bloom milestones 1–6 and scoped specification correspondence; keep accepted fixes standalone and all work local.

''' + plan[end:]
d = json.loads(old[names[1]])
assert d['committed_native_fixes'] == 135
summary = read(HERE / 'SUMMARY.json')
d['typed_demand_validation_checkpoint'] = summary
d['native_experiment_history'].append(d['active_native_experiment'])
d['active_native_experiment'] = {'status': 'TYPED_DEMAND_20_GTESTS_AND_ORDINARY_WPT_VERIFIED', 'directory': 'artifacts/css-keyframe-typed-attribute-demand-runtime-v1', 'gtest': summary['gtest'], 'ordinary_wpt': summary['wpt'], 'normal_producer_enabled': False, 'new_accepted_fixes': 0, 'remaining': 'Actual winning collector/source transport, joint SCC completion, disposable contexts, base freshness, effects and memory reporting.'}
d['cycle_repair_queue'] = {'used_attr_fallback': summary['used_attr_fallback_branch'], 'raw_nested_attr': summary['raw_attr_branch'], 'registered_number': summary['registered_number'], 'status': 'REPRODUCED_NOT_ACCEPTED', 'next': summary['next']}
d['research_signing_history'].append(d['latest_research_signing'])
v8 = read(ROOT / 'artifacts/css-local-signing-20261027-v8/FINAL-CHECK.json')
d['latest_research_signing'] = {'status': 'SIGNED_VERIFIED_LOCAL', 'commits': {v['id']: v['commit'] for v in v8['commits']}, 'verification': 'artifacts/css-local-signing-20261027-v8/FINAL-CHECK.json'}
d['latest_verified_working_epoch'] = {'path': str(EP.relative_to(ROOT)), 'status': 'Typed-demand full build, 20 GTests and four ordinary WPTs; preservation verified', 'browser_binary_contains_fixes': [133, 134, 135, 136]}
d['signing_next_action'] = 'Commit validation/research frequently; accept used-attribute-fallback native/WPT fix after controlled comparison evidence.'
new = {names[0]: plan.encode(), names[1]: (json.dumps(d, indent=2) + '\n').encode()}
for i, name in enumerate(names):
    (HERE / ('before-' + str(i))).write_bytes(old[name])
    (ROOT / name).write_bytes(new[name])
current = copy.deepcopy(epoch)
for group in ['pins', 'staged_working', 'committed_research_working_payloads']:
    for name in names:
        if name in current[group]:
            current[group][name] = h.fingerprint(ROOT, name)
state = h.index_state(ROOT, ENV)
semantic = h.semantic_index(state)
assert all(semantic[k] == epoch['semantic_index'][k] for k in ['head', 'entries', 'cached_diff'])
current['semantic_index'] = semantic
current['raw_index_observation']['current'] = state['raw_index']
a.verify_current(h, ROOT, ENV, current)
EP.write_text(json.dumps(current, indent=2, sort_keys=True) + '\n')
(HERE / 'ROADMAP-UPDATE.json').write_text(json.dumps({'changed': {name: {'before': hashlib.sha256(old[name]).hexdigest(), 'after': hashlib.sha256(new[name]).hexdigest()} for name in names}, 'accepted': 135, 'full_preservation_verified': True, 'native_changed': False}, indent=2) + '\n')
print('Roadmap updated; 135 accepted; preservation verified', flush=True)
