import json
import math
import statistics

PREFIX = 'CSS_ROLLBACK_COLD_COST_V1 '
COUNTS = [0, 32, 64, 128, 256]
MODES = ['literal', 'revert-rule', 'revert-layer']


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('Duplicate JSON key')
        value[key] = item
    return value


def invalid_constant(value):
    raise ValueError('Non-finite JSON constant: ' + value)


def decode(text):
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def finite_nonnegative(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def stylesheet(count, mode):
    value = 'var(--floor)' if mode == 'literal' else mode
    rules = ['@layer rollback-bench-base { #rollback-probe { opacity: var(--floor); } }']
    rules.extend(f'#rollback-probe {{ opacity: {value}; --block: {index}; }}' for index in range(count))
    return '\n'.join(rules)


def validate(report):
    errors, summary = [], []
    if not isinstance(report, dict):
        return {'valid': False, 'errors': ['Missing report'], 'summary': []}
    if report.get('version') != 'cold-c-chain-v1' or report.get('complete') is not True or report.get('error') is not None:
        errors.append('Incomplete or failed benchmark')
    if report.get('config') != {'counts': COUNTS, 'samples': 7, 'updates': 16, 'warmups': 4}:
        errors.append('Unexpected configuration')
    if report.get('build') != 'WPT cold-C chain' or report.get('visibility') != 'visible':
        errors.append('Wrong wrapper label or hidden benchmark')
    if not all(isinstance(report.get(key), str) and report[key] for key in ('started', 'finished', 'userAgent')):
        errors.append('Missing report identity/completion fields')
    rows = report.get('rows')
    if not isinstance(rows, list) or len(rows) != 15:
        return {'valid': False, 'errors': errors + ['Wrong row count'], 'summary': []}
    pairs = []
    counters = {'setupWrites': 7, 'setupReads': 7, 'warmupWrites': 28, 'warmupReads': 28,
                'measuredWrites': 112, 'measuredReads': 112, 'checkedReads': 112}
    for row in rows:
        if not isinstance(row, dict) or type(row.get('rules')) is not int or row.get('rules') not in COUNTS or row.get('mode') not in MODES:
            errors.append('Unexpected row')
            continue
        pair = (row['rules'], row['mode'])
        pairs.append(pair)
        if row.get('css') != stylesheet(*pair) or row.get('mismatches') != []:
            errors.append('Wrong stylesheet or value mismatch: ' + str(pair))
        if any(type(row.get(key)) is not int or row[key] != value for key, value in counters.items()):
            errors.append('Wrong workload counters: ' + str(pair))
        samples = row.get('samples')
        if not isinstance(samples, list) or len(samples) != 7:
            errors.append('Wrong sample count: ' + str(pair))
            continue
        times, setups = [], []
        for sample in samples:
            if not isinstance(sample, dict):
                errors.append('Invalid sample: ' + str(pair))
                continue
            if sample.get('complete') is not True or sample.get('reason') is not None or type(sample.get('updates')) is not int or sample['updates'] != 16:
                errors.append('Incomplete sample: ' + str(pair))
            if not all(finite_nonnegative(sample.get(key)) for key in ('setupMs', 'elapsedMs', 'usPerUpdate')):
                errors.append('Invalid timing value: ' + str(pair))
                continue
            if not math.isclose(sample['usPerUpdate'], sample['elapsedMs'] * 1000 / 16, rel_tol=1e-12, abs_tol=1e-12):
                errors.append('Inconsistent timing units: ' + str(pair))
            times.append(sample['usPerUpdate'])
            setups.append(sample['setupMs'])
        if len(times) == 7:
            summary.append({'rules': pair[0], 'mode': pair[1], 'samples': 7,
                            'median_us_per_update': statistics.median(times),
                            'p90_us_per_update': sorted(times)[math.ceil(0.9 * len(times)) - 1],
                            'median_setup_ms': statistics.median(setups)})
    if len(pairs) != 15 or len(set(pairs)) != 15 or set(pairs) != {(count, mode) for count in COUNTS for mode in MODES}:
        errors.append('Missing, duplicate or unexpected mode/count pair')
    return {'valid': not errors, 'errors': errors, 'summary': summary,
            'measured_updates_required': 1680, 'timing_threshold_applied': False}


def extract(events):
    chunks, errors = [], []
    for event in events:
        if event.get('action') not in ('process_output', 'log'):
            continue
        text = (event.get('data') or '') + (event.get('message') or '')
        if PREFIX not in text:
            continue
        if text.count(PREFIX) != 1:
            errors.append('Multiple report markers in one event')
            continue
        try:
            chunk = decode(text.split(PREFIX, 1)[1].strip())
            if not isinstance(chunk, dict) or set(chunk) != {'runId', 'index', 'count', 'data'}:
                raise ValueError('Invalid chunk fields')
            if not isinstance(chunk['runId'], str) or not chunk['runId']:
                raise ValueError('Missing run identity')
            if type(chunk['count']) is not int or not 1 <= chunk['count'] <= 256:
                raise ValueError('Invalid chunk count')
            if type(chunk['index']) is not int or not 0 <= chunk['index'] < chunk['count']:
                raise ValueError('Invalid chunk index')
            if not isinstance(chunk['data'], str) or not 0 < len(chunk['data']) <= 4096:
                raise ValueError('Invalid chunk data')
            chunks.append(chunk)
        except (ValueError, TypeError) as exc:
            errors.append(str(exc))
    payload = None
    if not chunks:
        errors.append('Missing benchmark report')
    elif len({(row['runId'], row['count']) for row in chunks}) != 1 or len(chunks) != chunks[0]['count'] or sorted(row['index'] for row in chunks) != list(range(chunks[0]['count'])):
        errors.append('Incomplete, duplicate or mixed report chunks')
    else:
        try:
            payload = decode(''.join(row['data'] for row in sorted(chunks, key=lambda row: row['index'])))
            if not isinstance(payload, dict) or set(payload) != {'runId', 'wrapperError', 'report'}:
                raise ValueError('Invalid report envelope')
            if payload['runId'] != chunks[0]['runId'] or payload['wrapperError'] is not None:
                raise ValueError('Wrong report identity or wrapper error')
        except (ValueError, TypeError) as exc:
            errors.append(str(exc))
    assessment = validate(payload.get('report') if isinstance(payload, dict) else None)
    return {'valid': not errors and assessment['valid'], 'capture_errors': errors,
            'assessment': assessment, 'payload': payload, 'chunks': len(chunks)}
