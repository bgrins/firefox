import argparse
import hashlib
import json
import re
from pathlib import Path

MARKER = re.compile(r'\bRFST (?P<event>[a-z-]+)(?: |$)')
FIELD = re.compile(r'(?<!\S)([a-z_]+)=')
IDENTITIES = {'node', 'input_node', 'target_node', 'root', 'child', 'effect', 'device'}
EVENTS = {
    'entry', 'restyle', 'returned', 'finish', 'root-published', 'signal',
    'joined', 'seed', 'normal-dirty', 'tasks', 'skip-existing-animation',
    'delivery', 'effect-properties', 'build-properties', 'rem-basis',
    'converted-font', 'built-properties',
}


def extract(data):
    rows = []
    indexes = {'event': {}, 'node': {}, 'effect': {}, 'device': {}, 'thread': {}}
    for number, raw in enumerate(data.splitlines(keepends=True), 1):
        if b'RFST' not in raw:
            continue
        text = raw.decode('utf-8', errors='surrogateescape')
        matches = list(MARKER.finditer(text.rstrip('\r\n')))
        match = matches[0] if len(matches) == 1 else None
        row = {'line': number, 'raw': text, 'recognized': False, 'fields': {}}
        if len(matches) > 1:
            row['multiple_markers'] = len(matches)
        if match:
            event = match['event']
            row.update(event=event, recognized=event in EVENTS)
            body = text[match.end():].rstrip('\r\n')
            fields = list(FIELD.finditer(body))
            duplicates = []
            for i, field in enumerate(fields):
                key = field[1]
                value = body[field.end():fields[i + 1].start() if i + 1 < len(fields) else len(body)].rstrip()
                if key in row['fields']:
                    duplicates.append(key)
                else:
                    row['fields'][key] = value
            if duplicates:
                row['duplicate_fields'] = duplicates
            indexes['event'].setdefault(event, []).append(number)
            for key, value in row['fields'].items():
                if not row['recognized'] or duplicates:
                    continue
                if key == 'thread':
                    indexes['thread'].setdefault(value, []).append(number)
                elif key in IDENTITIES and re.fullmatch(r'0x[0-9a-fA-F]+', value):
                    normalized = hex(int(value, 16))
                    kind = key if key in ('effect', 'device') else 'node'
                    indexes[kind].setdefault(normalized, []).append({'line': number, 'field': key})
        rows.append(row)
    return {'input_sha256': hashlib.sha256(data).hexdigest(), 'input_bytes': len(data),
            'input_lines': len(data.splitlines(keepends=True)), 'records': rows,
            'indexes': indexes, 'interpretation': 'Log order and address equality only; no causal or lifetime inference.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('log', type=Path)
    args = parser.parse_args()
    result = extract(args.log.read_bytes())
    result['input_path'] = str(args.log)
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == '__main__':
    main()
