import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('progress_report', HERE / 'report.py')
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)
modules = report.validators()
RUN = 'synthetic_progress_run_1234'


def snapshot(suite, mode, time):
    result = {}
    for field, (value, _) in report.oracle(suite, mode, time).items():
        if '.' in field:
            key, member = field.split('.')
            result.setdefault(key, {})[member] = value
        else:
            result[field] = value
    if suite == 'property-only':
        result['state'] = 'paused'
    else:
        for key in ('child', 'middle'): result[key]['state'] = 'paused'
        result['middle']['progress'] = time / 2000
    return result


def envelope(kind):
    suite, mode = kind.rsplit('-', 1)
    dimension, expected = ('width', 56) if suite == 'property-only' else ('opacity', 6 / 11)
    sample = dict(mode=mode, samples=[dict(phase=phase, **{dimension: expected}) for phase in modules['shared'].PHASES],
                  beforeMembership=snapshot(suite, mode, 750), afterMembership=snapshot(suite, mode, 750),
                  seek751=snapshot(suite, mode, 751), afterSeek=snapshot(suite, mode, 750), driverTiming=None)
    if mode == 'animated':
        sample['driverTiming'] = dict(time=1000, state='paused')
        if suite != 'property-only': sample['driverTiming'].update(duration=1000, progress=1)
    if suite == 'property-only': sample['same'] = True
    else: sample['membership'] = dict(middle=True, child=True, middleEffect=True, childEffect=True)
    return dict(kind=kind, run_id=RUN, observation=sample)


checks = []
for suite in ('two-hop', 'lh-chain'):
    assert report.oracle(suite, 'animated', 750)['childOpacity'][0] == 6 / 11
    assert report.oracle(suite, 'animated', 750)['childDuration'][0] == 1375
    assert report.oracle(suite, 'animated', 751)['childDuration'][0] == 1375.5
    assert report.oracle(suite, 'literal', 751)['childDuration'][0] == 1375
assert report.oracle('property-only', 'animated', 750)['width'][0] == 56
assert report.oracle('property-only', 'animated', 751)['width'][0] == 56.032
checks.append('independent fixed constants and literal-versus-dependent751ms distinction')
with tempfile.TemporaryDirectory(prefix='progress-analysis-check-') as temp:
    directory = Path(temp) / 'records'; directory.mkdir()
    originals = {kind: envelope(kind) for kind in report.KINDS}
    def put(kind, value): (directory / (kind + '.json')).write_text(json.dumps(value))
    for kind, value in originals.items(): put(kind, value)
    data = report.analyze(directory, RUN, modules)
    assert data['collection_complete'] and all(r['availability'] == 'valid' for r in data['records'].values())
    assert all(r['observation']['first_sample_matches_fixed_oracle'] is True for r in data['records'].values())
    assert not data['callback_pass_fail_inferred'] and not data['first_flush_correctness_claim']
    checks.append('nine correct records retain all eight stages without callback or first-flush verdict')
    for record in data['records'].values():
        assert len(record['observation']['stages']) == 8
        assert all(not v['fixture_asserts_this_stage'] for v in record['observation']['stages'][6]['comparisons'].values())
    checks.append('751ms reference explicitly unasserted')
    kind = 'two-hop-animated'; value = copy.deepcopy(originals[kind])
    value['observation']['samples'][0]['opacity'] = 3 / 7; put(kind, value)
    observed = report.analyze(directory, RUN, modules)['records'][kind]['observation']
    assert observed['first_sample_matches_fixed_oracle'] is False
    assert observed['last_passive_sample_matches_fixed_oracle'] is True and observed['first_mismatch_then_last_match']
    assert observed['stages'][0]['raw']['opacity'] == 3 / 7 and not observed['first_flush_correctness_claim']
    checks.append('stale first then correct last remains explicit')
    put(kind, originals[kind])
    kind = 'property-only-animated'; value = copy.deepcopy(originals[kind])
    for sample in value['observation']['samples']: sample['width'] = 28
    value['observation']['beforeMembership']['width'] = 28; put(kind, value)
    observed = report.analyze(directory, RUN, modules)['records'][kind]['observation']
    assert observed['stages'][4]['comparisons']['width']['actual'] == 28
    assert observed['stages'][4]['comparisons']['width']['within_tolerance'] is False
    assert observed['stages'][7]['comparisons']['width']['within_tolerance'] is True
    checks.append('later seek rescue does not hide stale passive and pre-membership output')
    value['observation']['samples'][1]['width'] = None; put(kind, value)
    observed = report.analyze(directory, RUN, modules)['records'][kind]['observation']
    assert observed['stages'][1]['comparisons']['width']['within_tolerance'] is None
    checks.append('null observation remains unavailable rather than zero or pass')
    put(kind, originals[kind])
    kind = 'lh-chain-ordinary'; (directory / (kind + '.json')).unlink()
    data = report.analyze(directory, RUN, modules)
    assert data['missing_kinds'] == [kind] and not data['collection_complete']
    assert data['records'][kind]['observation'] is None
    checks.append('missing record reports incomplete collection without invented samples')
    put(kind, originals[kind])
    value = copy.deepcopy(originals[kind]); value['run_id'] = 'different_identity_12345'; put(kind, value)
    record = report.analyze(directory, RUN, modules)['records'][kind]
    assert record['availability'] == 'invalid' and record['raw_envelope'] == value
    checks.append('wrong run identity invalid with raw envelope retained')
    value = copy.deepcopy(originals[kind]); value['observation']['samples'].pop(); put(kind, value)
    record = report.analyze(directory, RUN, modules)['records'][kind]
    assert record['availability'] == 'invalid' and len(record['raw_envelope']['observation']['samples']) == 3
    checks.append('partial schema retains available raw samples without applying oracle')
    path = directory / (kind + '.json'); path.write_text('{"bad":1e999}')
    record = report.analyze(directory, RUN, modules)['records'][kind]
    assert record['availability'] == 'invalid' and record['raw_text'] == '{"bad":1e999}'
    checks.append('overflowing JSON retained as text without invalid JSON report output')
    path.unlink(); path.symlink_to(directory / 'two-hop-literal.json')
    record = report.analyze(directory, RUN, modules)['records'][kind]
    assert record['availability'] == 'invalid' and 'raw_envelope' not in record
    checks.append('symlink record refused')
    path.unlink(); put(kind, originals[kind]); (directory / 'unexpected.json').write_text('{}')
    data = report.analyze(directory, RUN, modules)
    assert data['unexpected_names'] == ['unexpected.json'] and not data['collection_complete']
    checks.append('unexpected filenames reported without reading their bodies')
    missing = report.analyze(Path(temp) / 'absent', RUN, modules)
    assert len(missing['missing_kinds']) == 9 and not missing['directory_available']
    checks.append('missing directory explicitly reports all nine absent')
    json.dumps(data, allow_nan=False)
result = {'synthetic_checks': checks, 'scratch_removed': not Path(temp).exists(), 'browser_executed': False,
          'live_runtime_read': False, 'schema_packages_authenticated': report.PACKAGES}
(HERE / 'CHECK.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
