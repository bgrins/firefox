import argparse
import configparser
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'artifacts/css-revert-rule-indexed-single-trigger-wpt-v1'
SEAL = '4abad3d5f2904d606360a0c9b7876fa3f02adbc165490ee112949f8b5342b972'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def load(name):
    spec = importlib.util.spec_from_file_location('cost_comparison_' + name, PACKAGE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def describe(report):
    rows, durations = [], []
    for row in report['rows']:
        times = [sample['usPerUpdate'] for sample in row['samples']]
        durations.extend(sample['elapsedMs'] for sample in row['samples'])
        rows.append({'payload_blocks': row['payloadBlocks'], 'mode': row['mode'], 'median_us': statistics.median(times),
                     'min_us': min(times), 'max_us': max(times), 'samples_us': times})
    zero = [row for row in rows if row['payload_blocks'] == 0]
    return {'rows': rows, 'batch_range_ms': [min(durations), max(durations)],
            'total_measured_ms': sum(durations),
            'round_medians_ms': [statistics.median(row['samples'][i]['elapsedMs'] for row in report['rows']) for i in range(7)],
            'zero_payload_modes_have_distinct_css': len({row['css'] for row in report['rows'] if row['payloadBlocks'] == 0}) == 3,
            'zero_payload_mode_median_us': {row['mode']: row['median_us'] for row in zero},
            'zero_payload_semantics': 'Rule mode still has one Rule declaration; literal and Layer controls have none. This is not an identical-CSS noise floor.',
            'observed_20us_grid_max_residual_ms': max(abs(v - round(v / .02) * .02) for v in durations)}


def inspect(runtime, role, repetitions):
    runtime = Path(runtime).resolve()
    assert sha(PACKAGE / 'FILES.json') == SEAL
    assert all(sha(PACKAGE / name) == digest for name, digest in read(PACKAGE / 'FILES.json').items())
    runner, reports = load('run'), load('reports')
    result, pins = read(runtime / 'RESULT.json'), read(runtime / 'PINS.json')
    assert pins['source_role'] == result['source_role'] == role
    assert pins.get('repetitions', 2) == repetitions
    gates = ('complete_observation', 'safe_to_continue', 'supplemental_audit_passed', 'all_pass')
    assert all(result[gate] is True for gate in gates) and result['execution_error'] is None
    assert result['repetitions_requested'] == result['repetitions_completed'] == result['repetitions_recorded'] == repetitions
    assert len(result['runs']) == repetitions
    role_key = 'base_sha256' if role == 'baseline' else 'candidate_sha256'
    assert all(pins['files'][name] == row[role_key] for name, row in read(PACKAGE / 'SOURCE-ROLES.json').items())
    expected, policy = read(PACKAGE / 'EXPECTED.json'), read(PACKAGE / 'POLICY.json')
    evidence = {str(PACKAGE / 'FILES.json'): SEAL}
    descriptions = []
    for index, record in enumerate(result['runs'], 1):
        assert record['directory'] == f'repeat-{index}' and record['report'] == f'repeat-{index}/BENCHMARK-REPORT.json'
        phase = runtime / record['directory']
        child = read(phase / 'RESULT.json')
        assert child == record['result'] and read(phase / 'PINS.json') == pins
        assert all(child[gate] is True for gate in (*gates, 'browser_complete_observation', 'report_valid', 'preserved'))
        assert child['exit'] == 0 and child['execution_error'] is None and not child['cancelled'] and not child['external_timeout']
        before, after = read(phase / 'PRE.json'), read(phase / 'POST.json')
        assert before == after and before['files'] == pins['files'] and before['head'] == pins['harness_revision']
        cleanup = read(phase / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        assert all(sha(phase / name) == digest for name, digest in read(phase / 'STAGED-RESOURCES.json').items())
        application = phase / 'application.ini'
        app_name = str(Path(pins['binary']).parent.parent / 'Resources/application.ini')
        assert sha(application) == pins['files'][app_name]
        config = configparser.ConfigParser(interpolation=None)
        config.read(application)
        binding = {'build_id': config['App']['BuildID'], 'harness_revision': pins['harness_revision'],
                   'source_stamp': config.get('App', 'SourceStamp', fallback=None), 'build_revision': pins['build_revision']}
        assert read(phase / 'RUN-INFO-BINDING.json') == binding
        command = read(phase / 'COMMAND.json')['command']
        for pref in ('layout.css.revert-rule.enabled=true', 'dom.window.dump.enabled=true', 'privacy.reduceTimerPrecision=false'):
            assert command.count('--setpref=' + pref) == 1
        assert read(phase / 'EXPECTED.json') == expected and read(phase / 'POLICY.json') == policy
        raw = phase / 'raw.jsonl'
        events = [json.loads(line) for line in raw.read_bytes().splitlines()]
        assert all(isinstance(event, dict) for event in events)
        parsed = {'missing': False, 'errors': [], 'sha256': sha(raw)}
        assert read(phase / 'RAW-PARSE.json') == parsed
        assessment = runner.assess(events, parsed, 0, expected, policy, binding)
        assert assessment == read(phase / 'ASSESSMENT.json') and assessment['all_pass'] and assessment['supplemental_audit_passed']
        captured = reports.extract(events)
        assert captured == read(phase / 'BENCHMARK-REPORT.json') and captured['valid']
        descriptions.append({'phase': str(phase), 'binding': binding, **describe(captured['payload']['report'])})
        for name in ('RESULT.json', 'PINS.json', 'PRE.json', 'POST.json', 'CLEANUP.json', 'COMMAND.json',
                     'STAGED-RESOURCES.json', 'RUN-INFO-BINDING.json', 'EXPECTED.json', 'POLICY.json',
                     'application.ini', 'raw.jsonl', 'RAW-PARSE.json', 'ASSESSMENT.json', 'BENCHMARK-REPORT.json'):
            evidence[str(phase / name)] = sha(phase / name)
    for name in ('RESULT.json', 'PINS.json'):
        evidence[str(runtime / name)] = sha(runtime / name)
    return {'runtime': str(runtime), 'role': role, 'verified_record_replay': True,
            'repetitions': descriptions, 'evidence': evidence,
            'scope': 'Recorded raw events/pins only; not a live restoration audit or independent source-to-binary proof.'}


def compare(a1, b, a2):
    records = {'A1': inspect(a1, 'baseline', 1), 'B': inspect(b, 'candidate', 2), 'A2': inspect(a2, 'baseline', 1)}
    runs = {'A1': records['A1']['repetitions'][0], 'B1': records['B']['repetitions'][0],
            'B2': records['B']['repetitions'][1], 'A2': records['A2']['repetitions'][0]}
    lookup = {name: {(row['payload_blocks'], row['mode']): row['median_us'] for row in value['rows']} for name, value in runs.items()}
    rows = []
    for key in sorted(lookup['A1']):
        values = {name: table[key] for name, table in lookup.items()}
        baselines, candidates = [values['A1'], values['A2']], [values['B1'], values['B2']]
        rows.append({'payload_blocks': key[0], 'mode': key[1], 'median_us': values,
                     'baseline_median_range_us': [min(baselines), max(baselines)],
                     'candidate_median_range_us': [min(candidates), max(candidates)],
                     'candidate_to_baseline_observed_median_ratio_range':
                     [ratio(min(candidates), max(baselines)), ratio(max(candidates), min(baselines))]})
    return {'verified_record_replay': True, 'records': records, 'rows': rows,
            'within_run_descriptors': {name: {key: value[key] for key in ('round_medians_ms', 'zero_payload_mode_median_us', 'zero_payload_semantics')} for name, value in runs.items()},
            'statistical_significance_claimed': False, 'performance_acceptance': False,
            'interpretation': 'Descriptive observed medians/ranges only. Ratio ranges are not confidence intervals. Null ratios have zero denominators. The axis is matched custom-only payload blocks; Rule mode has one Rule at every count. Zero payload is not a shared no-Rule floor. Retain literal/Layer controls and baseline drift; no timing acceptance threshold.'}


if __name__ == '__main__':
    assert __debug__, 'Run without Python optimization'
    parser = argparse.ArgumentParser()
    for name in ('a1', 'b', 'a2', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    value = compare(args.a1, args.b, args.a2)
    assert args.output.parent.resolve().is_relative_to(ROOT / 'artifacts')
    with args.output.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print('Recorded evidence verified; descriptive analysis written to', args.output)
