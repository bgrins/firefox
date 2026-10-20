import hashlib
import json
from pathlib import Path
import re
import sys

source, output = map(Path,sys.argv[1:])
rows = []
for binding in json.loads((source/'SOURCE-BINDINGS.json').read_text()):
    raw = (source/binding['file']).read_bytes()
    body = binding['body']
    assert raw[binding['start_byte']:binding['end_byte']].decode() == body
    assert hashlib.sha256(body.encode()).hexdigest() == binding['sha256']
    code = re.sub(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])\'',
                  lambda match:' '*len(match[0]),body,flags=re.S)
    start = code.index('{')
    depth = 0
    end = None
    for index,char in enumerate(code[start:],start):
        if char == '{': depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                end = index+1
                break
    assert end == len(body)
    rows.append({'file':binding['file'],'signature':binding['signature'],'byte_slice_matches':True,'first_body_brace_closes_at_retained_end':True})
output.write_text(json.dumps(rows,indent=2)+'\n')
