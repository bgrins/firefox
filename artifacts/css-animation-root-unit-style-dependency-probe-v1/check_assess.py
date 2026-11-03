import copy, importlib.util, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('assessor', HERE / 'assess.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original = json.loads((HERE.parent / 'css-animation-root-unit-invalidation-original-runtime-v1/REPORT.json').read_text())
data = {'schema': 'animation-root-unit-style-dependency-v1', 'cleanup': True, 'errors': [], 'frames': []}
for unit in ('rem', 'rlh'):
    source = next(f for f in original['frames'] if f['unit'] == unit)
    for mode in module.ORDERS:
        frame = copy.deepcopy(source)
        frame['order'] = mode
        frame['rows'] = frame['rows'][:4]
        for row in frame['rows']:
            base = row['rootSize'] if unit == 'rem' else row['rootLine']
            row['targetMargins'] = [f'{base if mode == "ordinary-relative" else 0}px'] * 3
        data['frames'].append(frame)
old = module.assess(data)
assert old['calibrated'] and old['rows_count'] == 16
fixed = copy.deepcopy(data)
for frame in fixed['frames']:
    if frame['order'] != 'ordinary-relative':
        continue
    for row in frame['rows']:
        value = row['expectedCurrent']
        row.update(variationRaw=f'"wdth" {value}', variationValue=value, widthRaw=f'{value}px', widthValue=value, opacityRaw=str(value/1000), opacityRatioValue=value/1000)
out = module.assess(fixed)
assert out['calibrated']
for row in out['rows']:
    if row['phase'] == 'root-change':
        expected = 'current-root' if row['order'] == 'ordinary-relative' else 'original-root'
        assert set(row['classifications'].values()) == {expected}
bad = copy.deepcopy(fixed)
bad['frames'][1]['rows'][2]['targetMargins'][0] = '0px'
assert not module.assess(bad)['calibrated']
for mutate in (
    lambda d: d['frames'].pop(),
    lambda d: d['frames'][0]['rows'].pop(),
    lambda d: d.update(cleanup=False),
    lambda d: d['frames'][0]['rows'][2].update(expectedCurrent=46),
    lambda d: d['frames'][0]['rows'][2]['variationAnimation'].update(progress=0.2),
):
    broken = copy.deepcopy(data)
    mutate(broken)
    try:
        module.assess(broken)
    except AssertionError:
        pass
    else:
        raise AssertionError('corruption accepted')
print(json.dumps({'synthetic_paths': 2, 'rejected_corruptions': 5, 'uncalibrated_margin_controls': 1, 'rows_per_path': 16, 'browser_execution': False}, indent=2))
