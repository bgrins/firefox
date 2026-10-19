import hashlib
import json
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
RECORD = BASE / 'CANDIDATE-SOURCE-v1.json'
MIX = 'servo/components/style/color/mix.rs'
FLAGS = 'servo/components/style/values/generics/color.rs'
RGB_GUARD = 'if source.color_space.is_rgb_or_xyz_like() && self.color_space.is_rgb_or_xyz_like() {\n'
RGB_INSERT = '            self.flags |= source.flags & (F::C0_IS_NONE | F::C1_IS_NONE | F::C2_IS_NONE);\n'
OLD_SKIP = '''        if combined == 0.0 {
            // If both are 0, this fold doesn't contribute anything to the result.
            continue;
        }'''
NEW_SKIP = '''        if !normalize && combined == 0.0 {
            continue;
        }'''
OLD_WEIGHTS = '''        let (left_weight, right_weight) = if normalize {
            (accumulated_weight / combined, weight / combined)
        } else {
            (accumulated_weight, weight)
        };'''
NEW_WEIGHTS = '''        let (left_weight, right_weight) = if normalize {
            if combined == 0.0 {
                (0.5, 0.5)
            } else {
                (accumulated_weight / combined, weight / combined)
            }
        } else {
            (accumulated_weight, weight)
        };'''
SHAPES = {
    'normalize-flag': 'let normalize = flags.contains(ColorMixFlags::NORMALIZE_WEIGHTS);',
    'zero-total-shortcut': '''        if sum == 0.0 {
            return finalize(AbsoluteColor::TRANSPARENT_BLACK.to_color_space(interpolation.space));
        }''',
    'initialize': '''    let (first, rest) = items.split_first().unwrap();
    let mut accumulated_color = convert_for_mix(&first.color, interpolation.space);
    let mut accumulated_weight = first.weight * weight_scale;''',
    'ordered-loop': '''    for item in rest {
        let weight = item.weight * weight_scale;
        let combined = accumulated_weight + weight;''',
    'raw-skip': NEW_SKIP,
    'conversion': '        let right = convert_for_mix(&item.color, interpolation.space);',
    'weights': NEW_WEIGHTS,
    'helper-and-weight': '''        accumulated_color = mix_with_weights(
            &accumulated_color,
            left_weight,
            &right,
            right_weight,
            interpolation.hue,
        );
        accumulated_weight = combined;''',
    'alpha-scale': '    let alpha = components[3] * alpha_multiplier;',
}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def replace_once(source, old, new):
    if source.count(old) != 1:
        raise RuntimeError('Unexpected source cardinality')
    return source.replace(old, new, 1)

def rgb_delta(source):
    return replace_once(source, RGB_GUARD, RGB_GUARD + RGB_INSERT)

def zero_delta(source):
    return replace_once(replace_once(source, OLD_SKIP, NEW_SKIP), OLD_WEIGHTS, NEW_WEIGHTS)

def shape(source, flags):
    for name, snippet in SHAPES.items():
        if source.count(snippet) != 1:
            raise RuntimeError('Source shape: ' + name)
    if flags.count('const NORMALIZE_WEIGHTS = 1 << 0;') != 1:
        raise RuntimeError('Flag definition drift')
    start = source.index(SHAPES['ordered-loop'])
    expected = (SHAPES['ordered-loop'] + '\n' + NEW_SKIP + '\n' + SHAPES['conversion']
                + '\n\n' + NEW_WEIGHTS + '\n\n' + SHAPES['helper-and-weight'] + '\n    }')
    if source[start:start + len(expected)] != expected:
        raise RuntimeError('Loop order or intervening expression drift')

def lineage(parent, before, after):
    if rgb_delta(parent) != before or zero_delta(before) != after:
        raise RuntimeError('Unexpected native patch delta')
    if rgb_delta(zero_delta(parent)) != after:
        raise RuntimeError('RGB and zero-prefix deltas do not commute')

def materialize(directory):
    record = json.loads(RECORD.read_text())
    result = {}
    for path in [MIX, FLAGS]:
        parent = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show',
                                         record['parent'] + ':' + path], cwd=ROOT).decode()
        result['parent-mix.rs' if path == MIX else 'flags.rs'] = parent
    result['prezero-mix.rs'] = rgb_delta(result['parent-mix.rs'])
    result['candidate-mix.rs'] = zero_delta(result['prezero-mix.rs'])
    result['zero-only-mix.rs'] = zero_delta(result['parent-mix.rs'])
    directory.mkdir(parents=True, exist_ok=True)
    for name, source in result.items():
        if digest(source.encode()) != record['snapshots'][name]:
            raise RuntimeError('Materialized source identity: ' + name)
        target = directory / name
        if target.exists() and target.read_text() != source:
            raise RuntimeError('Existing snapshot drift: ' + name)
        target.write_text(source)
    return result

def run(directory, live=False):
    snapshots = materialize(directory)
    parent, before, after, flags = [snapshots[name] for name in
        ['parent-mix.rs', 'prezero-mix.rs', 'candidate-mix.rs', 'flags.rs']]
    shape(after, flags)
    lineage(parent, before, after)
    rejected = []
    for name, snippet in SHAPES.items():
        altered = replace_once(after, snippet, '')
        try:
            shape(altered, flags)
        except RuntimeError:
            rejected.append(name)
        else:
            raise RuntimeError('Accepted shape mutation: ' + name)
    mutations = {
        'foreign-delta': (parent, before, after + '\n'),
        'fake-prezero': (parent, before + '\n', after),
        'missing-rgb': (parent, parent, after),
        'restore-old-skip': (parent, before, after.replace(NEW_SKIP, OLD_SKIP)),
        'unit-accumulated-weight': (parent, before, after.replace('accumulated_weight = combined;', 'accumulated_weight = 1.0;')),
    }
    for name, args in mutations.items():
        try:
            lineage(*args)
        except RuntimeError:
            rejected.append(name)
        else:
            raise RuntimeError('Accepted lineage mutation: ' + name)
    try:
        shape(after, flags.replace('const NORMALIZE_WEIGHTS = 1 << 0;', 'const NORMALIZE_WEIGHTS = 1 << 1;'))
    except RuntimeError:
        rejected.append('flag-value')
    else:
        raise RuntimeError('Accepted flag mutation')
    if live:
        for path, expected in [(MIX, after), (FLAGS, flags)]:
            if (ROOT / path).read_text() != expected:
                raise RuntimeError('Live source drift: ' + path)
    return {'live_native_verified': live, 'source_controls': rejected,
            'snapshots': {name: digest(source.encode()) for name, source in snapshots.items()}}
