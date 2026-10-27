import hashlib
import json
from pathlib import Path


here = Path(__file__).resolve().parent
root = here.parents[1]
for path, digest in json.loads((here / 'REFERENCES.json').read_text()).items():
    assert hashlib.sha256((root / path).read_bytes()).hexdigest() == digest

matching = (here / 'current-source/servo/components/style/matching.rs').read_text()
assert matching.index('for_animation_only()') < matching.index('UpdateAnimationsTasks::EFFECT_PROPERTIES')
assert 'for_animation_only() && old_values.is_some() {\n            return;' in matching
wrapper = (here / 'current-source/servo/components/style/gecko/wrapper.rs').read_text()
assert 'let computed_data = self.borrow_data();' in wrapper
assert 'd.styles.primary()' in wrapper
compositor = (here / 'current-source/dom/animation/EffectCompositor.cpp').read_text()
assert 'effect->UpdateProperties(aStyle);' in compositor
assert 'if (ServoStyleSet::IsInServoTraversal() || mIsInPreTraverse)' in compositor
assert 'second traversal' in compositor
style = (here / 'searchfox/style-document.txt').read_text()
assert style.count('if (GetPresContext()->EffectCompositor()->PreTraverse(aFlags))') == 1

# This is the shared immutable-style update recurrence, not a native execution.
style1 = [40, 20, 20]
prepared1 = [40, style1[0], style1[1]]
style2 = prepared1
prepared2 = [40, style2[0], style2[1]]
assert style2 == [40, 40, 20] and prepared2 == [40, 40, 40]
cycle = [[1, 2]]
for _ in range(4):
    a, b = cycle[-1]
    cycle.append([b + 1, a + 1])
assert all(a != b for a, b in zip(cycle, cycle[1:]))
assert cycle[2] == [3, 4] and cycle[4] == [5, 6]
print(json.dumps({
    'status': 'SOURCE_REFRESH_BARRIER_CONFIRMED',
    'chain_styles': [style1, style2],
    'next_prepared_endpoints': prepared2,
    'cyclic_rebuild_recurrence': cycle,
    'native_execution': False,
    'cyclic_numeric_oracle': None,
    'repair_admitted': False,
    'scope': 'Pinned source guards and finite operational counterexamples; not native scheduler execution or a proof of nontermination.'
}, indent=2))
