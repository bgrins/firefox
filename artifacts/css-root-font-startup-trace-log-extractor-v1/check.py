import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('extractor', HERE / 'extract.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
data = (b'ordinary log\n'
        b'RFST root-published node=0xA flags=TraversalFlags(AnimationOnly | FinalAnimationTraversal) px=32 old_computed_px=Some(23.0) device=0xD thread=ThreadId(1)\r\n'
        b'RFST build-properties effect=0xE target_node=0xB pseudo=0 style=0xC\n'
        b'RFST rem-basis root_context=false media=false reference_px=32 factor=2 device=0xd thread=ThreadId(1)\n'
        b'RFST converted-font node=0xb keyframe=0 px=64 thread=ThreadId(1)\n'
        b'RFST tasks node=0xB flags=TraversalFlags(0x0) mask=0x4 thread=ThreadId(1)\n'
        b'RFST unknown node=0xB node=0xF\n'
        b'RFST malformed\xff')
result = module.extract(data)
assert result['input_sha256'] == hashlib.sha256(data).hexdigest()
assert [r['line'] for r in result['records']] == list(range(2, 9))
for row in result['records']:
    assert row['raw'].encode('utf-8', errors='surrogateescape') == data.splitlines(keepends=True)[row['line'] - 1]
assert result['records'][0]['fields']['flags'] == 'TraversalFlags(AnimationOnly | FinalAnimationTraversal)'
assert result['records'][0]['fields']['old_computed_px'] == 'Some(23.0)'
assert result['indexes']['device']['0xd'] == [{'line': 2, 'field': 'device'}, {'line': 4, 'field': 'device'}]
assert result['indexes']['effect']['0xe'] == [{'line': 3, 'field': 'effect'}]
assert result['indexes']['node']['0xb'] == [{'line': 3, 'field': 'target_node'}, {'line': 5, 'field': 'node'}, {'line': 6, 'field': 'node'}]
assert result['records'][-2]['duplicate_fields'] == ['node']
assert not result['records'][-2]['recognized'] and not result['records'][-1]['recognized']
assert module.extract(b'no diagnostic lines\n')['records'] == []
assert module.extract(b'RFST delivery target_node=(nil) pseudo=0\n')['indexes']['node'] == {}
mixed = module.extract(b'RFST tasks node=0xa RFST signal node=0xb\n')
assert mixed['records'][0]['multiple_markers'] == 2 and mixed['indexes']['node'] == {}
assert json.loads(json.dumps(result)) == result
print(json.dumps({'synthetic_checks': ['raw bytes and original line numbers', 'CRLF and invalid UTF-8 preserved', 'full flags and optional old value', 'same-device publication/basis index', 'node/effect co-occurrence index', 'unknown and duplicate fields retained', 'empty log and null pointer', 'JSON roundtrip'],
                  'multiple_marker_lines_not_correlated': True, 'actual_trace_read': False,
                  'tested': {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in ['extract.py', 'check.py']}}, indent=2))
