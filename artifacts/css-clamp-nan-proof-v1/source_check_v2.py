import hashlib
from pathlib import Path
from materialize_v2 import BASE, ROOT, materialize

FEATURES = {
    'all-leaves': '(min.as_leaf(), center.as_leaf(), max.as_leaf())',
    'raw-value': 'let Some(value) = leaf.unitless_value() else',
    'percentage-hint': 'hint != Optional::Some(NumericBaseType::Percent)',
    'relative-infinity': 'value.is_infinite() && leaf.canonical_value().is_none()',
    'left-nan': 'if a.is_nan()',
    'right-nan': 'else if b.is_nan()',
    'inner-min': 'strict_op(a, b, crate::values::calc_min)',
    'outer-max': 'strict_op(a, b, crate::values::calc_max)',
    'result-nonfinite': 'has_relative_infinity && result.unitless_value().is_none_or(f32::is_finite)',
    'fallback-guards': 'has_relative_infinity || leaves.iter().any(|leaf| leaf.is_nan() != Ok(false))',
    'lower-winner': 'matches!(min_cmp_center, cmp::Ordering::Greater)',
    'upper-below-center': 'matches!(max_cmp_center, cmp::Ordering::Less)',
    'upper-below-lower': 'matches!(max_cmp_min, cmp::Ordering::Less)',
}


def feature_check(text):
    for name, fragment in FEATURES.items():
        if text.count(fragment) != 1:
            raise ValueError(name)


def run(out, live):
    manifest, values = materialize(out)
    branch = (BASE / 'clamp-after-v2.rs').read_text()
    feature_check(branch)
    rejected = []
    for name, fragment in FEATURES.items():
        altered = branch.replace(fragment, 'CONTROL_REMOVED')
        try:
            feature_check(altered)
        except ValueError as error:
            if str(error) != name:
                raise ValueError('Unexpected source-control rejection')
            rejected.append(name)
        else:
            raise ValueError('Source control accepted: ' + name)
    if live:
        if (ROOT / manifest['generic_path']).read_bytes() != values['candidate']:
            raise ValueError('Live generic source differs from frozen candidate')
        for path, expected in manifest['helper_sha256'].items():
            if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
                raise ValueError('Live helper differs: ' + path)
    return {'base_commit': manifest['base_commit'], 'snapshot_candidate_sha256': manifest['candidate_sha256'],
            'standalone_candidate_sha256': manifest['standalone_sha256'], 'live_native_verified': live,
            'source_controls': rejected,
            'limits': 'Exact source identity and reviewed text correspondence, not Rust extraction or execution'}
