from collections import Counter, defaultdict, deque
import hashlib
import gzip
import io
import json
from pathlib import Path
import re
import sys

assert sys.argv[1:] in ([], ['--check'])
CHECK_ONLY = sys.argv[1:] == ['--check']

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-contextual-easing-servo-compile-runtime-5'
CLOSURE = ROOT / 'artifacts/css-contextual-easing-servo-closure-v4'
sha = lambda data: hashlib.sha256(data).hexdigest()
read = lambda p: json.loads(p.read_bytes())
generated = read(HERE / 'GENERATED-SOURCES.json')
sources = {}
for item in generated.values():
    assert sha((ROOT / item['retained']).read_bytes()) == item['sha256']
summary_re = re.compile(r'^warning: `([^`]+)` \(([^)]+)\) generated (\d+) warnings?(?: \((\d+) duplicates?\))?$')
span_re = re.compile(r'^\s*(?:-->|:::) (.*):(\d+):(\d+)$')
gutter_re = re.compile(r'^\s*(\d+)\s*\| (.*)$')
all_records = []
roles = {}
snippet_mismatches = []


def source(role, name):
    actual = ROOT / generated[name]['retained'] if name in generated else Path(name)
    if not actual.is_absolute():
        actual = CLOSURE / role / actual
    if str(actual) not in sources:
        body = actual.read_bytes()
        sources[str(actual)] = {'sha256': sha(body), 'lines': body.decode().splitlines()}
    key = name
    for which in ('baseline', 'candidate'):
        key = key.removeprefix(str(CLOSURE / which) + '/')
    return key, actual, sources[str(actual)]


def diagnostic(role, block, crate, target, index):
    normalized = []
    spans = []
    snippets = []
    active_source = None
    for line in block['lines']:
        match = span_re.match(line)
        if match:
            name, row, column = match.groups()
            key, path, info = source(role, name)
            active_source = (name, path, info)
            row, column = int(row), int(column)
            assert 0 < row <= len(info['lines']), (path, row)
            spans.append({'source': key, 'actual_source': str(path.relative_to(ROOT)),
                          'source_sha256': info['sha256'], 'line': row, 'column': column,
                          'source_line_sha256': sha(info['lines'][row - 1].encode())})
        match = gutter_re.match(line)
        if match:
            assert active_source is not None, block
            row, rendered = match.groups()
            row = int(row)
            name, path, info = active_source
            assert 0 < row <= len(info['lines']), (path, row)
            actual = info['lines'][row - 1]
            options = {rendered.strip()}
            if rendered.startswith(('/ ', '| ')):
                options.add(rendered[2:].strip())
            if rendered in ('/', '|'):
                options.add('')
            matched = actual.strip() in options
            truncated = not matched and any(option.endswith('...') and actual.strip().startswith(option[:-3]) for option in options)
            matched = matched or truncated
            if not matched:
                snippet_mismatches.append({'role': role, 'diagnostic': index, 'source': str(path),
                                           'line': row, 'rendered': rendered, 'actual': actual})
            snippets.append({'source': name, 'line': row, 'source_line_sha256': sha(actual.encode()),
                             'rendered_sha256': sha(rendered.encode()), 'matched': matched,
                             'rustc_truncated_display_prefix': truncated})
        line = re.sub(re.escape(str(CLOSURE)) + r'/(baseline|candidate)/', '', line)
        line = re.sub(r'(--> |::: )(.+):\d+:(\d+)$', r'\1\2:<line>:\3', line)
        line = re.sub(r'^\s*\d+\s*\|', '|', line)
        line = re.sub(r'^\s*\|', '|', line)
        line = re.sub(r'^\s*(--> |::: )', r'\1', line)
        normalized.append(line.rstrip())
    assert spans and snippets, (role, block)
    semantic = crate + '|' + target + '\n' + '\n'.join(normalized).strip()
    return {'role': role, 'index': index, 'crate': crate, 'target': target,
            'category': block['lines'][0], 'raw_log_start_line': block['start'],
            'raw_log_end_line': block['end'], 'raw_block_sha256': sha('\n'.join(block['lines']).encode()),
            'semantic_sha256': sha(semantic.encode()), 'spans': spans, 'snippets': snippets}


for role in ('baseline', 'candidate'):
    path = RUNTIME / role / 'output.log'
    lines = path.read_text().splitlines()
    records, summaries, pending, resolver = [], [], [], []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith('warning: missing documentation'):
            end = index + 1
            while end < len(lines) and not lines[end].startswith('warning:') and not re.match(r'^\s+(?:Compiling|Checking|Finished) ', lines[end]):
                end += 1
            pending.append({'lines': lines[index:end], 'start': index + 1, 'end': end})
            index = end
            continue
        match = summary_re.match(line)
        if match:
            crate, target, total, duplicates = match.groups()
            assert len(pending) + int(duplicates or 0) == int(total), (role, line, len(pending))
            summaries.append({'crate': crate, 'target': target, 'reported': int(total),
                              'duplicate_count': int(duplicates or 0), 'rendered_count': len(pending)})
            for block in pending:
                records.append(diagnostic(role, block, crate, target, len(records)))
            pending = []
        elif line.startswith('warning:'):
            assert line.startswith('warning: patch `getrandom v0.2.999 '), line
            end = index + 1
            while end < len(lines) and not lines[end].startswith('warning:') and not re.match(r'^\s+(?:Compiling|Checking|Finished) ', lines[end]):
                end += 1
            resolver.append('\n'.join(lines[index:end]).strip())
        assert not re.match(r'^error(?:\[|:)', line), line
        index += 1
    assert not pending and len(resolver) == 1
    roles[role] = {'records': records, 'summaries': summaries, 'resolver_messages': resolver,
                   'raw_log_sha256': sha(path.read_bytes()), 'raw_log_bytes': path.stat().st_size}
    all_records.extend(records)

baseline = roles['baseline']['records']
candidate = roles['candidate']['records']
available = defaultdict(deque)
for entry in baseline:
    available[entry['semantic_sha256']].append(entry)
pairs = []
for entry in candidate:
    assert available[entry['semantic_sha256']], ('New candidate diagnostic', entry)
    old = available[entry['semantic_sha256']].popleft()
    assert len(old['spans']) == len(entry['spans'])
    for before, after in zip(old['spans'], entry['spans']):
        assert (before['source'], before['column'], before['source_line_sha256']) == (after['source'], after['column'], after['source_line_sha256']), (before, after)
    assert [s['source_line_sha256'] for s in old['snippets']] == [s['source_line_sha256'] for s in entry['snippets']]
    pairs.append({'baseline_index': old['index'], 'candidate_index': entry['index'],
                  'semantic_sha256': entry['semantic_sha256'],
                  'span_line_deltas': [a['line'] - b['line'] for b, a in zip(old['spans'], entry['spans'])]})
baseline_only = [entry for queue in available.values() for entry in queue]
candidate_scopes = {(r['crate'], r['target']) for r in candidate}
assert all((r['crate'], r['target']) not in candidate_scopes for r in baseline_only)
assert roles['baseline']['resolver_messages'] == roles['candidate']['resolver_messages']
assert not snippet_mismatches, snippet_mismatches[:5]
for name, records in [('DIAGNOSTICS.jsonl.gz', all_records), ('PAIRINGS.jsonl.gz', pairs)]:
    output = io.BytesIO()
    with gzip.GzipFile(filename=name[:-3], fileobj=output, mode='wb', mtime=0) as stream:
        for entry in records:
            stream.write((json.dumps(entry, sort_keys=True) + '\n').encode())
    if CHECK_ONLY:
        assert (HERE / 'local' / name).read_bytes() == output.getvalue(), name
    else:
        (HERE / 'local' / name).write_bytes(output.getvalue())
result = {
    'success': True, 'normalization': 'Only role workspace prefixes, diagnostic line numbers, and line-number gutter indentation. All other diagnostic text, columns, notes, code snippets and markers retained.',
    'candidate_diagnostics_all_matched': len(pairs), 'candidate_unmatched': 0,
    'baseline_only_diagnostics': len(baseline_only), 'baseline_only_scopes_absent_from_candidate': True,
    'source_files_checked': len(sources), 'source_snippet_lines_checked': sum(len(r['snippets']) for r in all_records),
    'source_snippet_mismatches': 0, 'line_shifted_candidate_diagnostics': sum(any(p['span_line_deltas']) for p in pairs),
    'rustc_truncated_display_snippet_lines': sum(s['rustc_truncated_display_prefix'] for r in all_records for s in r['snippets']),
    'raw_logs': {role: {k: roles[role][k] for k in ('raw_log_sha256', 'raw_log_bytes')} for role in roles},
    'roles': {role: {'rendered_diagnostics': len(roles[role]['records']), 'summaries': roles[role]['summaries'],
                    'categories': dict(Counter(r['category'] for r in roles[role]['records']))} for role in roles},
    'resolver_messages_identical': True, 'resolver_message_sha256': sha(roles['baseline']['resolver_messages'][0].encode()),
    'large_local_inventories': {name: {'sha256': sha((HERE / 'local' / name).read_bytes()), 'bytes': (HERE / 'local' / name).stat().st_size} for name in ('DIAGNOSTICS.jsonl.gz', 'PAIRINGS.jsonl.gz')},
    'generated_sources_retained': generated,
    'native_acceptance': False, 'strict_original_lint_policy_passed': False,
}
encoded = (json.dumps(result, indent=2, sort_keys=True) + '\n').encode()
if CHECK_ONLY:
    assert (HERE / 'WARNING-AUDIT.json').read_bytes() == encoded
else:
    (HERE / 'WARNING-AUDIT.json').write_bytes(encoded)
print(json.dumps({key: result[key] for key in ('success', 'candidate_diagnostics_all_matched', 'candidate_unmatched', 'baseline_only_diagnostics', 'source_files_checked', 'source_snippet_lines_checked', 'line_shifted_candidate_diagnostics')}, sort_keys=True))
