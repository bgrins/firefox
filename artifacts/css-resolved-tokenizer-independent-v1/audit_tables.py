import hashlib
import json
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
records = json.loads((root / 'generated/INVOCATIONS.json').read_text())
def masked(source):
    result = list(source)
    i = 0
    while i < len(source):
        end = i
        if source.startswith('//', i):
            end = source.find('\n', i)
            if end < 0: end = len(source)
        elif source.startswith('/*', i):
            depth = 1; end = i + 2
            while depth:
                assert end < len(source)
                if source.startswith('/*', end): depth += 1; end += 2
                elif source.startswith('*/', end): depth -= 1; end += 2
                else: end += 1
        elif source[i] == '"':
            end = i + 1
            while end < len(source):
                if source[end] == '\\': end += 2
                elif source[end] == '"': end += 1; break
                else: end += 1
        elif source[i] == "'":
            char = re.match(r"'(?:\\(?:u\{[0-9a-fA-F]+\}|x[0-9a-fA-F]{2}|.)|[^'\\])'", source[i:])
            if char: end = i + len(char[0])
        if end > i:
            result[i:end] = ['\n' if x == '\n' else ' ' for x in source[i:end]]
            i = end
        else: i += 1
    return ''.join(result)

inventory = []
for src in sorted((root / 'source/cssparser/src').glob('*.rs')):
    text = src.read_text(); code = masked(text)
    for m in re.finditer(r'\bmatch_byte\s*!\s*\{', code):
        start = m.start(); end = m.end(); depth = 1
        while depth:
            depth += (code[end] == '{') - (code[end] == '}'); end += 1
        inventory.append((str(src.relative_to(root)), start, hashlib.sha256(text[start:end].encode()).hexdigest()))
assert inventory == [(r['path'], r.get('source_character_start', r['byte_start']), r['invocation_sha256']) for r in records]

def byte(text):
    raw = text[2:-1]
    if len(raw) == 1: return ord(raw)
    if raw.startswith('\\x'): return int(raw[2:], 16)
    return {'\\n':10, '\\r':13, '\\t':9, '\\0':0, '\\\\':92, "\\'":39, '\\"':34}[raw]

output = []
for index, r in enumerate(records):
    sets = []; bindings = []
    for arm in r['arms']:
        pattern = re.sub(r'//[^\n]*', '', arm['pattern']).strip()
        if re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', pattern):
            members = set(range(256))
            if pattern != '_': bindings.append(pattern)
        else:
            members = set()
            # Split literal/punctuation tokens; no producer lexer or numeric lowering imported.
            parts = re.findall(r"b'(?:\\.|[^'\\])*'|\.\.=|\||\S+", pattern)
            j = 0
            while j < len(parts):
                lo = byte(parts[j]); hi = lo; j += 1
                if j < len(parts) and parts[j] == '..=': hi = byte(parts[j+1]); j += 2
                assert 0 <= lo <= hi < 256
                members.update(range(lo,hi+1))
                if j < len(parts): assert parts[j] == '|'; j += 1
        sets.append(members)
    assert len(bindings) <= 1
    expected = [next(i for i,s in enumerate(sets) if b in s) for b in range(256)]
    assert expected == r['table']
    assert len(r['arms']) <= 256
    src = (root / r['path']).read_text()
    output.append({'id':index, 'source':r['path'], 'arms':len(sets), 'named_bindings':bindings,
                   'decisions':256, 'actual_byte_offset':len(src[:r.get('source_character_start', r['byte_start'])].encode()),
                   'reported_character_offset':r.get('source_character_start', r['byte_start'])})
print(json.dumps({'status':'PASS','independent_inventory':len(inventory),
                  'independent_membership_decisions':len(inventory)*256,
                  'max_arms':max(x['arms'] for x in output),'details':output},indent=2))
