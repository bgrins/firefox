import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIXES = {'rem': 'two-hop', 'lh': 'lh-chain', 'property': 'property-only'}
MODES = ('literal', 'ordinary', 'animated')
IDENTITY = ('pid', 'window', 'document')
TARGET = ('target', 'pseudo', 'identifier')
FULL_KEY = (*IDENTITY, 'compositor', *TARGET, 'cascade')


def digest(body):
    return hashlib.sha256(body).hexdigest()


def read(path):
    path = Path(path)
    assert stat.S_ISREG(path.lstat().st_mode), str(path)
    return path.read_bytes()


def json_body(body):
    def reject(value):
        raise ValueError('Non-JSON number: ' + value)
    return json.loads(body, parse_constant=reject)


def load(path):
    spec = importlib.util.spec_from_file_location('sealed_' + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inputs():
    config = json_body(read(HERE / 'INPUTS.json'))
    for name, expected in config['references'].items():
        assert digest(read(ROOT / name)) == expected, name
    order = json_body(read(ROOT / config['order']))
    mapping = json_body(read(ROOT / config['mapping']))
    parser = load(ROOT / config['parser'])
    policy = json_body(read(ROOT / config['record_policy']))
    schemas = {rule['kind']: load(ROOT / rule['schema']) for rule in policy['record_kinds'].values()}
    return config, order, mapping, parser, policy['record_kinds'], schemas


def field(observation, path):
    value = observation
    for part in path.split('.'):
        match = re.fullmatch(r'([A-Za-z]+)\[([0-9]+)\]', part)
        value = value[match[1]][int(match[2])] if match else value[part]
    assert type(value) in (int, float) and math.isfinite(value), path
    return value


def number(text, prop):
    decimal = r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?'
    suffix = '' if prop == 'opacity' else 's' if prop == 'animation-duration' else 'px'
    assert re.fullmatch('(' + decimal + ')' + suffix, text), (prop, text)
    value = float(text[:-len(suffix)] if suffix else text)
    assert math.isfinite(value), text
    return value * (1000 if prop == 'animation-duration' else 1)


def join(report, collector, envelopes, binding, order, mapping, schemas):
    assert binding['compiled_generated_header_sha256'] == mapping['header_sha256']
    assert binding['fixture_hashes'] == binding['expected_fixture_hashes']
    assert re.fullmatch(r'[A-Za-z0-9_-]{16,128}', binding['run_id'])
    assert report['syntax_and_sequence_valid'] and report['closed_query_scopes']
    assert not report['errors'] and not report['caps'] and not report['limitations']
    assert collector['complete'] and not collector['errors'] and not collector['missing']
    assert collector['expected_records'] == 9 and collector['run_id'] == binding['run_id']
    expected = {f'{prefix}-{mode}.json' for prefix in PREFIXES.values() for mode in MODES}
    assert set(envelopes) == set(collector['records']) == expected
    for name, record in envelopes.items():
        assert set(record) == {'run_id', 'kind', 'observation'}
        assert record['run_id'] == binding['run_id'] and name == record['kind'] + '.json'
        assert collector['records'][name]['schema_valid']
        assert collector['records'][name]['callback_status'] in ('PASS', 'FAIL')
        assert schemas[record['kind']].validate({'kind': record['kind'], 'observation': record['observation']}) == record['kind']
    assert len(report['queries']) == report['query_count'] == 258
    groups = {}
    for query in report['queries']:
        entry, end = query['entry'], query['exit']
        assert entry['query'] == end['query'] and entry['parent'] == end['parent'] == 0
        assert entry['window'] and entry['document'] != '0x0' and entry['target'] != '0x0'
        assert entry['page'] in PREFIXES and entry['mode'] in MODES
        for key in (*IDENTITY, *TARGET, 'page', 'mode', 'role', 'property'):
            assert entry[key] == end[key], key
        assert not any(e['stage'] == 'query-enter' and e['query'] != entry['query'] for e in query['events'])
        group = tuple(entry[key] for key in IDENTITY)
        groups.setdefault(group, []).append(query)
    assert len(groups) == 9 and len({group[:2] for group in groups}) == 9
    seen, output, matched = set(), [], 0
    for identity, queries in groups.items():
        queries.sort(key=lambda query: query['entry']['seq'])
        page, mode = queries[0]['entry']['page'], queries[0]['entry']['mode']
        assert (page, mode) not in seen
        seen.add((page, mode))
        roster = order[page]['reads']
        assert len(queries) == len(roster)
        name = f'{PREFIXES[page]}-{mode}.json'
        observation = envelopes[name]['observation']
        targets, aligned, phases, first = {}, [], {}, None
        for query, row in zip(queries, roster):
            entry, end = query['entry'], query['exit']
            assert (entry['page'], entry['mode'], entry['role'], entry['property']) == (page, mode, row['role'], mapping['properties'][row['css_property']])
            target = tuple(entry[key] for key in TARGET)
            assert entry['identifier'] == '0x0'
            assert targets.setdefault(row['role'], target) == target
            text = end['decoded_value']
            assert not end['valueTruncated']
            assert bytes.fromhex(end['value']).decode('ascii') == text
            numeric = number(text, row['css_property'])
            record_path = row['record_path']
            if record_path is not None:
                assert numeric == field(observation, record_path), (page, mode, row['ordinal'], record_path, numeric)
                matched += 1
            item = {**row, 'query_id': entry['query'], 'entry_sequence': entry['seq'], 'exit_sequence': end['seq'], 'return_text': text, 'converted_value': numeric, 'posted_value_joined': record_path is not None}
            aligned.append(item)
            phases.setdefault(row['phase'], []).append(entry['query'])
            if row['phase'] == 'first-child-read':
                first = {'query_id': entry['query'], 'events': [{'full_key': {key: event[key] for key in FULL_KEY}, 'event': event} for event in query['events']]}
        assert len({target[0] for target in targets.values()}) == len(targets)
        assert first is not None
        output.append({'identity': dict(zip(IDENTITY, identity)), 'page': page, 'mode': mode, 'record': name, 'callback_status': collector['records'][name]['callback_status'], 'role_targets': targets, 'phase_query_ids': phases, 'reads': aligned, 'first_child_query': first})
    assert seen == {(page, mode) for page in PREFIXES for mode in MODES} and matched == 204
    return {'full_authored_rosters_matched': True, 'groups': output, 'query_count': 258, 'posted_css_fields_joined': matched, 'unposted_initial_reads': 54, 'effect_timing_and_membership_fields_native_joined': False, 'native_causality_or_composition_proved': False, 'first_freshness_or_callback_pass_inferred': False}


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('--runtime', type=Path, required=True)
    cli.add_argument('--runtime-manifest-sha256', required=True)
    args = cli.parse_args()
    config, order, mapping, parser, rules, schemas = inputs()
    manifest_body = read(args.runtime / 'FILES.json')
    assert digest(manifest_body) == args.runtime_manifest_sha256
    manifest = json_body(manifest_body)
    def bound(name):
        relative = Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        path = args.runtime / relative
        for parent in (path, *path.parents):
            if parent == args.runtime.parent:
                break
            assert not parent.is_symlink(), str(parent)
        body = read(path)
        pin = manifest[str(relative)]
        assert digest(body) == (pin if isinstance(pin, str) else pin['sha256']), name
        if isinstance(pin, dict):
            assert len(body) == pin['bytes']
        return body
    trace_binding = json_body(bound('TRACE-BINDING.json'))
    progress_binding = json_body(bound('PROGRESS-BINDING.json'))
    assert trace_binding['parser'] == config['parser']
    assert trace_binding['parser_sha256'] == config['references'][config['parser']]
    assert trace_binding['diagnostic_capture_complete']
    assert trace_binding['generated_header_before'] == trace_binding['generated_header']
    header = trace_binding['generated_header']
    assert header['matches'] and header['path'] == mapping['header_path']
    assert header['sha256'] == header['expected_sha256'] == mapping['header_sha256']
    raw = bound(trace_binding['raw_path'])
    assert digest(raw) == trace_binding['raw_sha256']
    report_body = bound('TRACE.json')
    assert digest(report_body) == trace_binding['trace_sha256']
    report = json_body(report_body)
    assert parser.analyze(raw.decode().splitlines(True)) == report
    fixtures = {}
    for page, expected in config['fixture_hashes'].items():
        fixtures[page] = digest(bound('candidate-wpt/tests/' + page.lstrip('/')))
        assert fixtures[page] == expected
    binding = {'run_id': progress_binding['run_id'], 'fixture_hashes': fixtures,
               'expected_fixture_hashes': config['fixture_hashes'],
               'compiled_generated_header_sha256': header['sha256']}
    collector_body = bound('PROGRESS-RECORDS.json')
    collector = json_body(collector_body)
    records = args.runtime / 'progress-records'
    assert stat.S_ISDIR(records.lstat().st_mode)
    assert {p.name for p in records.iterdir()} == set(rules)
    envelopes = {}
    for filename in rules:
        body = bound('progress-records/' + filename)
        receipt = collector['records'][filename]
        assert len(body) == receipt['bytes'] and digest(body) == receipt['sha256']
        envelopes[filename] = json_body(body)
    result = join(report, collector, envelopes, binding, order, mapping, schemas)
    result['input_hashes'] = {'runtime_manifest': digest(manifest_body), 'trace': digest(report_body), 'raw': digest(raw), 'collector': digest(collector_body), 'trace_binding': digest(bound('TRACE-BINDING.json')), 'progress_binding': digest(bound('PROGRESS-BINDING.json'))}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
