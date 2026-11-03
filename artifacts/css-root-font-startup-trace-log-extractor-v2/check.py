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

queue = (b'RFST document-enter set=0xA document=0xA flags=4\n'
         b'RFST document-enter set=0xB document=0xD flags=0\n'
         b'RFST pre-enter compositor=0xA root_node=0xE flags=4\n'
         b'RFST document-pass-begin set=0xa pass=2\n'
         b'RFST request compositor=0xa target_node=0xE pseudo=95 level=0 type=2 posted_before=0\n'
         b'RFST request-post compositor=0xa target_node=0xe pseudo=95 level=0 skip=0\n'
         b'RFST post-deferred compositor=0xa target_node=0xe normalized_node=0xF pseudo=95 level=0 pretraverse=0\n'
         b'RFST pre-queue compositor=0xa level=0 count=1\n'
         b'RFST pre-selected compositor=0xa target_node=0xe pseudo=95 level=0 posted=1\n'
         b'RFST pre-remaining compositor=0xa level=0 count=0\n'
         b'RFST pre-exit compositor=0xa found=1\n'
         b'RFST document-pass-end set=0xa pass=1 post_required=1\n'
         b'RFST document-exit set=0xb post_required=0\n'
         b'RFST document-exit set=0xa post_required=1\n'
         b'RFST post-shell compositor=0xA target_node=0xe normalized_node=0xf pseudo=95 level=0\n'
         b'RFST document-no-root set=0xa\n'
         b'RFST document-pre set=0xa\n'
         b'RFST document-subtree set=0xa pass=1 root_node=0xe\n'
         b'RFST document-new-subtree set=0xa pass=1 root_node=0xf\n'
         b'RFST document-between-pre set=0xa\n')
q = module.extract(queue)
assert all(r['recognized'] for r in q['records'])
assert [r['line'] for r in q['records']] == list(range(1, 21))
for row in q['records']:
    assert row['raw'].encode('utf-8', errors='surrogateescape') == queue.splitlines(keepends=True)[row['line'] - 1]
assert q['indexes']['document']['0xa'] == [{'line': 1, 'field': 'document'}]
assert q['indexes']['set']['0xa'][0] == {'line': 1, 'field': 'set'}
assert q['indexes']['compositor']['0xa'][0] == {'line': 3, 'field': 'compositor'}
assert {'line': 3, 'field': 'root_node'} in q['indexes']['node']['0xe']
assert {'line': 7, 'field': 'normalized_node'} in q['indexes']['node']['0xf']
assert q['records'][3]['fields'] == {'set': '0xa', 'pass': '2'}
assert q['records'][4]['fields']['posted_before'] == '0'
assert q['records'][5]['fields']['skip'] == '0'
assert q['records'][6]['fields']['pretraverse'] == '0'
assert q['records'][7]['fields']['count'] == '1'
assert q['records'][8]['fields']['posted'] == '1'
assert q['records'][10]['fields']['found'] == '1'
assert q['records'][11]['fields']['pass'] == '1'
assert q['records'][12]['fields'] == {'set': '0xb', 'post_required': '0'}
assert set(q) == set(result)
assert all(set(r) == {'line', 'raw', 'recognized', 'fields', 'event'} for r in q['records'])
assert not q['indexes']['thread'] and not q['indexes']['device'] and not q['indexes']['effect']

ambiguous = (b'RFST future compositor=0xAA document=0xAA set=0xAA\n'
             b'RFST request compositor=0xBB compositor=0xCC target_node=0xDD\n'
             b'RFST document-enter set=0xEE RFST request compositor=0xFF\n'
             b'RFST pre-enter compositor=(nil) root_node=0xNO flags=4\r\n'
             b'RFST ??\xff\n')
a = module.extract(ambiguous)
assert len(a['records']) == 5
assert a['records'][1]['duplicate_fields'] == ['compositor']
assert a['records'][2]['multiple_markers'] == 2
for kind in ['node', 'set', 'document', 'compositor']:
    assert a['indexes'][kind] == {}
for row in a['records']:
    assert row['raw'].encode('utf-8', errors='surrogateescape') == ambiguous.splitlines(keepends=True)[row['line'] - 1]
assert json.loads(json.dumps(q)) == q and json.loads(json.dumps(a)) == a

source = HERE.parent / 'css-root-font-startup-queue-trace-instrumentation-v1'
new_events = set(module.re.findall(r'RFST ([a-z-]+)', (source / 'PARENT-DELTA.patch').read_text()))
assert len(new_events) == 18 and new_events <= module.EVENTS
assert new_events <= {row['event'] for row in q['records']}
print(json.dumps({'synthetic_checks': ['all inherited assertions', '18 exact queue/pass event names', '20 chronological queue/pass rows', 'independent set/compositor/document namespaces', 'root and normalized node fields', 'exact string queue/pass values', 'no inferred pass or pointer joins', 'five unknown/duplicate/multimarker/null/malformed rows', 'CRLF invalid bytes and JSON roundtrip'],
                  'actual_trace_read': False,
                  'tested': {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in ['extract.py', 'check.py']}}, indent=2))
