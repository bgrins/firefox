import copy
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile

import join


def fixture():
    config, order, mapping, parser, rules, schemas = join.inputs()
    runtime = join.ROOT / 'artifacts/css-contextual-duration-progress-candidate-runtime-1'
    collector = join.json_body(join.read(runtime / 'PROGRESS-RECORDS.json'))
    envelopes = {name: join.json_body(join.read(runtime / 'progress-records' / name)) for name in rules}
    lines, sequence, query_id = [], 0, 0
    for group, (page, mode) in enumerate((p, m) for p in join.PREFIXES for m in join.MODES):
        observation = envelopes[join.PREFIXES[page] + '-' + mode + '.json']['observation']
        targets = {}
        for row in order[page]['reads']:
            query_id += 1
            targets.setdefault(row['role'], hex(0x10000 + group * 16 + len(targets)))
            value = 1.0 if row['record_path'] is None else join.field(observation, row['record_path'])
            prop = row['css_property']
            text = repr(value / 1000 if prop == 'animation-duration' else value)
            text += '' if prop == 'opacity' else 's' if prop == 'animation-duration' else 'px'
            assert join.number(text, prop) == value
            for stage in ('query-enter', 'query-exit'):
                sequence += 1
                event = {key: -1 for key in parser.FIELDS if key not in parser.STRINGS}
                event.update({key: '0x0' for key in parser.POINTERS})
                event.update(v=1, pid=42, seq=sequence, query=query_id, parent=0,
                             window=100 + group, document=hex(0x1000 + group),
                             target=targets[row['role']], compositor='0x900', shell='0xa00',
                             page=page, mode=mode, role=row['role'], pseudo=95,
                             stage=stage, cascade=-1, state=-2, servo=0, pre=-1,
                             refresh=0, property=mapping['properties'][prop], flags=0,
                             count=0, value='-', valueLength=0, valueTruncated=0)
                if stage == 'query-exit':
                    event.update(value=text.encode().hex(), valueLength=len(text))
                lines.append(parser.PREFIX + ' '.join(f'{key}={event[key]}' for key in parser.FIELDS))
    report = parser.analyze(lines)
    binding = {'compiled_generated_header_sha256': mapping['header_sha256'],
               'fixture_hashes': config['fixture_hashes'], 'expected_fixture_hashes': config['fixture_hashes'],
               'run_id': collector['run_id']}
    return report, collector, envelopes, binding, order, mapping, schemas


def main():
    args = fixture()
    result = join.join(*args)
    assert result['query_count'] == 258 and result['posted_css_fields_joined'] == 204
    assert all(len(group['phase_query_ids']) == (11 if group['page'] != 'property' else 9) for group in result['groups'])
    negatives = []
    def negative(name, mutate):
        values = list(copy.deepcopy(args[:6])) + [args[6]]
        mutate(values)
        try:
            join.join(*values)
        except (AssertionError, ValueError, KeyError, TypeError, UnicodeError):
            negatives.append(name)
        else:
            raise AssertionError('Accepted: ' + name)
    negative('header', lambda v: v[3].update(compiled_generated_header_sha256='0' * 64))
    negative('fixture', lambda v: v[3].update(fixture_hashes={}))
    negative('run id', lambda v: v[3].update(run_id='different_record_run_id'))
    negative('cap', lambda v: v[0]['caps'].append({'cap': 'limit'}))
    negative('truncation', lambda v: v[0]['limitations'].append({'reason': 'truncated'}))
    negative('sequence error', lambda v: v[0]['errors'].append({'reason': 'gap'}))
    negative('missing query', lambda v: v[0]['queries'].pop())
    negative('extra query', lambda v: v[0]['queries'].append(copy.deepcopy(v[0]['queries'][0])))
    negative('nested', lambda v: v[0]['queries'][0]['entry'].update(parent=99))
    negative('role', lambda v: v[0]['queries'][0]['entry'].update(role='child'))
    negative('property', lambda v: v[0]['queries'][0]['entry'].update(property=331))
    negative('unknown mode', lambda v: v[0]['queries'][0]['entry'].update(mode='unknown'))
    negative('exit identity', lambda v: v[0]['queries'][0]['exit'].update(document='0xdead'))
    def change_target(values):
        query = values[0]['queries'][2]
        query['entry']['target'] = query['exit']['target'] = '0xbeef'
    negative('changed role target', change_target)
    negative('wrong value', lambda v: v[2]['two-hop-literal.json']['observation']['samples'][0].update(opacity=0.123))
    negative('null posted value', lambda v: v[2]['two-hop-literal.json']['observation']['samples'][0].update(opacity=None))
    negative('wrong kind', lambda v: v[2]['two-hop-literal.json'].update(kind='two-hop-ordinary'))
    negative('missing record', lambda v: v[2].pop('two-hop-literal.json'))
    negative('invalid schema receipt', lambda v: v[1]['records']['two-hop-literal.json'].update(schema_valid=False))
    negative('incomplete collector', lambda v: v[1].update(complete=False))
    for text, prop in [('1ms', 'animation-duration'), ('2s garbage', 'animation-duration'), ('NaN', 'opacity'), ('Infinity', 'width'), ('16em', 'font-size'), ('', 'opacity')]:
        try:
            join.number(text, prop)
        except AssertionError:
            negatives.append('numeric ' + text)
        else:
            raise AssertionError(text)
    failed = list(copy.deepcopy(args[:6])) + [args[6]]
    failed[1]['records']['two-hop-literal.json']['callback_status'] = 'FAIL'
    assert join.join(*failed)['groups'][0]['callback_status'] == 'FAIL'
    assert join.number('1.375s', 'animation-duration') == 1375
    assert join.number('5.6e1px', 'width') == 56
    config, order, mapping, parser, rules, schemas = join.inputs()
    with tempfile.TemporaryDirectory(prefix='duration-trace-join-') as scratch:
        runtime = Path(scratch)
        def save(name, value):
            path = runtime / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value))
        report, collector, envelopes, binding = args[:4]
        collector = copy.deepcopy(collector)
        for name, envelope in envelopes.items():
            save('progress-records/' + name, envelope)
            body = (runtime / 'progress-records' / name).read_bytes()
            collector['records'][name].update(bytes=len(body), sha256=join.digest(body))
        raw = '\n'.join(parser.PREFIX + ' '.join(f'{key}={event[key]}' for key in parser.FIELDS) for event in report['events']) + '\n'
        raw_path = runtime / 'candidate-wpt/raw.jsonl'
        raw_path.parent.mkdir(parents=True)
        raw_path.write_text(raw)
        save('TRACE.json', report)
        save('PROGRESS-RECORDS.json', collector)
        save('PROGRESS-BINDING.json', {'run_id': binding['run_id']})
        header = {'path': mapping['header_path'], 'sha256': mapping['header_sha256'], 'expected_sha256': mapping['header_sha256'], 'matches': True}
        save('TRACE-BINDING.json', {'parser': config['parser'], 'parser_sha256': config['references'][config['parser']], 'raw_path': 'candidate-wpt/raw.jsonl', 'raw_sha256': join.digest(raw.encode()), 'trace_sha256': join.digest((runtime / 'TRACE.json').read_bytes()), 'generated_header': header, 'generated_header_before': header, 'diagnostic_capture_complete': True})
        fixtures = join.json_body(join.read(join.ROOT / 'artifacts/css-contextual-duration-first-read-trace-proposal-v1/FIXTURES.json'))
        for row in fixtures:
            path = runtime / ('candidate-wpt/tests/' + row['execution_page'].lstrip('/'))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(join.read(join.ROOT / row['fixture']['path']))
        manifest = {str(path.relative_to(runtime)): {'sha256': join.digest(path.read_bytes()), 'bytes': path.stat().st_size} for path in runtime.rglob('*') if path.is_file()}
        save('FILES.json', manifest)
        original_argv = sys.argv
        sys.argv = ['join.py', '--runtime', str(runtime), '--runtime-manifest-sha256', join.digest((runtime / 'FILES.json').read_bytes())]
        try:
            with contextlib.redirect_stdout(io.StringIO()) as output:
                join.main()
            assert json.loads(output.getvalue())['posted_css_fields_joined'] == 204
            raw_path.write_text(raw + 'tampered')
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    join.main()
            except AssertionError:
                negatives.append('raw body tampering against frozen manifest')
            else:
                raise AssertionError('tampered raw accepted')
        finally:
            sys.argv = original_argv
    check = {'synthetic_complete_roster_positive': True, 'synthetic_failure_status_preserved': True,
             'synthetic_frozen_runtime_cli_passed': True, 'temporary_runtime_removed': not Path(scratch).exists(),
             'exact_numeric_conversion_positives': 2, 'negative_cases': negatives,
             'actual_native_trace_executed_or_aligned': False,
             'historical_record_values_used_only_to_construct_synthetic_getter_stream': True}
    if '--write' in sys.argv:
        (Path(__file__).resolve().parent / 'CHECK.json').write_text(json.dumps(check, indent=2) + '\n')
    print(json.dumps(check, indent=2))


if __name__ == '__main__':
    main()
