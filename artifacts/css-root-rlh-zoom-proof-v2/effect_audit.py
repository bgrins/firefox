import hashlib
import json
from pathlib import Path
import re
import sys
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / 'baseline'))
import extract

def run():
    props = BASE / 'baseline/source/servo/components/style/properties/properties.mako.rs'
    helper = extract.body(props.read_text(), 'pub fn add_flags(')
    builder = extract.body(props.read_text(), 'pub fn calc_line_height(')
    assert 'let flags = self.flags() | flag;' in helper
    assert 'self.flags.set(flags);' in helper
    assert 'if matches!(line_height, computed::LineHeight::Normal)' in builder
    assert builder.count('self.add_flags(flag);') == 1
    for name in ['DEPENDS_ON_SELF_FONT_METRICS', 'DEPENDS_ON_INHERITED_FONT_METRICS']:
        assert name in builder
    selectors = {}
    for variant, folder in [('original', 'source'), ('candidate', 'candidate')]:
        path = BASE / 'baseline' / folder / 'servo/components/style/values/specified/length.rs'
        body = extract.body(path.read_text(), 'fn reference_font_size_and_length(')
        arm = extract.body(body, 'LengthUnit::Rlh =>')
        assert 'rule_cache_conditions' not in arm
        assert body.count('.add_flags(ComputedValueFlags::USES_FONT_OR_WM_RELATIVE_UNITS);') == 1
        assert body.index('.add_flags(ComputedValueFlags::USES_FONT_OR_WM_RELATIVE_UNITS);') < body.index('let reference_font_size = base_size.resolve(context);')
        selectors[variant] = dict(source=hashlib.sha256(path.read_bytes()).hexdigest(),
            selector=hashlib.sha256(body.encode()).hexdigest(), rlhArm=hashlib.sha256(arm.encode()).hexdigest())
    flagfile = BASE / 'provider/servo/components/style/properties/computed_value_flags.rs'
    text = flagfile.read_text()
    assert 'pub struct ComputedValueFlags(u32);' in text
    mapping = {}
    for name, adapter in [('USES_FONT_OR_WM_RELATIVE_UNITS', 1), ('DEPENDS_ON_SELF_FONT_METRICS', 2), ('DEPENDS_ON_INHERITED_FONT_METRICS', 4)]:
        matches = re.findall(r'const ' + name + r' = 1 << (\d+);', text)
        assert len(matches) == 1
        mapping[name] = dict(nativeBit=int(matches[0]), adapterMask=adapter)
    conditions = BASE / 'provider/servo/components/style/rule_cache.rs'
    records = extract.body(conditions.read_text(), 'pub struct RuleCacheConditions')
    assert all(x in records for x in ['uncacheable: bool', 'font_size: Option<NonNegativeLength>', 'line_height: Option<NonNegativeLength>', 'writing_mode:', 'color_scheme:'])
    return dict(selectors=selectors, helperBody=helper,
        helperSource=hashlib.sha256(props.read_bytes()).hexdigest(), flagMapping=mapping,
        flagDefinitionSource=hashlib.sha256(flagfile.read_bytes()).hexdigest(),
        conditionsDefinitionSource=hashlib.sha256(conditions.read_bytes()).hexdigest(),
        conditionsDefinition=records,
        otherConditions='Opaque preserved payload models uncacheable/writing_mode/color_scheme; native supplemental facade exposes font/line-height only',
        normal='Actual selector/builder dispatch; deterministic metric adapter remains external',
        mutationBoundaries={'drop-relative':'Actual selector add_flags argument replaced by zero',
            'drop-normal':'Actual builder add_flags argument replaced by zero',
            'clear-incoming':'Selector-entry state clear through adapter Cell; private-field access is a facade mutation, not a compilable Gecko patch'})
