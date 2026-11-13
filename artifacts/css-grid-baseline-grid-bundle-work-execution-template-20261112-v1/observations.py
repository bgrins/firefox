import json
import math
MAX_RAW_LINE = 4 * 1024 * 1024
MAX_STREAM_FILE = 4 * 1024 * 1024 * 1024
MAX_QUIET_FILE = 16 * 1024 * 1024

def observation(report, config):
    assert len(report['results']) == 1
    result = report['results'][0]
    assert result['status'] == 'OK' and len(result['subtests']) == 2
    assert all(row['status'] == 'PASS' for row in result['subtests'])
    names = [row['name'] for row in result['subtests']]
    assert 'Collect a bounded dual-axis baseline workload; native demand coverage is required' in names
    values = [json.loads(name[9:]) for name in names if name.startswith('WORKLOAD ')]
    assert len(values) == 1
    value = values[0]
    assert set(value) == {'depth', 'lines', 'columns', 'orientation', 'group', 'samples', 'checksum'}
    assert all(value[key] == config[key] for key in ['depth', 'lines', 'columns', 'orientation', 'group'])
    assert type(value['columns']) is bool
    assert len(value['samples']) == 3 and all(type(x) in [int, float] and math.isfinite(x) and x >= 0 for x in value['samples'])
    assert type(value['checksum']) in [int, float] and math.isfinite(value['checksum'])
    return value, {key: item for key, item in value.items() if key != 'samples'}

def extract_trace(raw_path, trace_path, parser):
    assert raw_path.stat().st_size <= MAX_STREAM_FILE
    producer = None
    count = 0
    with raw_path.open() as raw, trace_path.open('x') as trace:
        for line in parser.bounded_lines(raw, MAX_RAW_LINE):
            entry = json.loads(line)
            data = entry.get('data', '')
            if not isinstance(data, str) or 'GRIDWORK' not in data:
                continue
            assert entry['action'] == 'process_output'
            current = str(entry['process'])
            if producer is None:
                producer = current
            assert current == producer, 'One complete producer stream per invocation required'
            for record in data.splitlines():
                assert record.startswith('GRIDWORK ')
                assert len((record + '\n').encode('utf-8')) <= parser.MAX_LINE_BYTES
                trace.write(record + '\n')
                assert 'TRUNCATED' not in record
                count += 1
                assert count <= parser.MAX_RECORDS
    assert producer is not None and count
    return producer

def no_trace(raw_path, parser):
    assert raw_path.stat().st_size <= MAX_QUIET_FILE
    with raw_path.open() as raw:
        for line in parser.bounded_lines(raw, MAX_RAW_LINE):
            assert 'GRIDWORK' not in line
