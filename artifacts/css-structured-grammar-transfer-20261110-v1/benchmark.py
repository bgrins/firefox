import argparse
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent
ORIGINAL = runpy.run_path(str(ROOT / 'preserved/original-extract.py'))


def read(path):
    return json.loads(path.read_text())


def authenticate():
    assert hashlib.sha256((ROOT / 'PROTOCOL.json').read_bytes()).hexdigest() == (ROOT / 'PROTOCOL.sha256').read_text().strip()
    for record in read(ROOT / 'PRESERVED.json'):
        assert hashlib.sha256((ROOT / record['file']).read_bytes()).hexdigest() == record['sha256'], ('source or preserved input changed', record.get('file'))
    for record in read(ROOT / 'SOURCES.json')['sources']:
        assert hashlib.sha256((ROOT / record['file']).read_bytes()).hexdigest() == record['sha256'], ('source or preserved input changed', record.get('file'))
        assert hashlib.sha256((ROOT / record['metadata_file']).read_bytes()).hexdigest() == record['metadata_sha256']


def select(record, field):
    raw = (ROOT / record['source']).read_bytes()
    data = record[field]
    start, end = data['bytes']
    if raw[start:end].decode() != data['text']:
        raise ORIGINAL['Refusal']('Reviewed source span changed')
    return data['text'], len(raw[:start].decode()), raw.decode()


def adapted(record, productions):
    grammar, offset, source = select(record, 'value')
    select(record, 'block')
    heading, _, _ = select(record, 'heading')
    if record['anchor'] not in heading:
        raise ORIGINAL['Refusal']('Reviewed anchor changed')
    tree = ORIGINAL['Parser'](grammar, offset).parse()
    program, maps, references = [], [], []

    def emit(node, module, source_name, text, active):
        def span(values):
            start, end = values
            return dict(file=source_name, bytes=[len(text[:start].encode()), len(text[:end].encode())], text=text[start:end])
        if node['op'] == 'ref':
            name = node['args'][0]
            if name in active:
                raise ORIGINAL['Refusal']('Cyclic reviewed dependency: ' + name)
            candidates = [p for p in productions if p['module'] == module and p['name'] == name]
            if len(candidates) != 1:
                raise ORIGINAL['Refusal']('No unique reviewed structured production: ' + name)
            production = candidates[0]
            body, start, document = select(production, 'value')
            references.append(dict(name=name, source=span(node['span'])))
            parsed = ORIGINAL['Parser'](body, start).parse()
            emit(parsed, module, production['source'], document, active + [name])
            return
        if node['op'] != 'keyword':
            for child in node['args']:
                emit(child, module, source_name, text, active)
        maps.append(dict(instruction=len(program), expression=span(node['span']),
            operator=span(node.get('operator', node['span'])), via=active))
        program.append([node['op']] + (node['args'] if node['op'] == 'keyword' else []))

    emit(tree, record['module'], record['source'], source, [])
    return dict(program=program, source_map=maps, references=references)


def run():
    authenticate()
    protocol = read(ROOT / 'PROTOCOL.json')
    contexts = read(ROOT / 'CONTEXTS.json')
    assert [(r['module'], r['property']) for r in contexts['properties']] == [(r['module'], r['property']) for r in protocol['properties']]
    results, generated = [], {}
    for record in contexts['properties']:
        source = (ROOT / record['source']).read_text()
        try:
            original = ORIGINAL['extract'](source, record['property'])
            first = dict(status='success', instructions=len(original['program']))
        except ORIGINAL['Refusal'] as error:
            first = dict(status='refusal', exception=type(error).__name__, message=str(error))
        try:
            value = adapted(record, contexts['productions'])
            second = dict(status='success', instructions=len(value['program']))
            generated[record['property']] = value
        except ORIGINAL['Refusal'] as error:
            second = dict(status='refusal', exception=type(error).__name__, message=str(error))
        results.append(dict(module=record['module'], property=record['property'], anchor=record['anchor'],
            original=first, selected_context=second))
    assert [dict(module=r['module'], property=r['property'], original=r['original']) for r in results] == read(ROOT / 'ORIGINAL-RESULTS.json')
    return dict(results=results, original_successes=sum(r['original']['status'] == 'success' for r in results),
        selected_context_successes=sum(r['selected_context']['status'] == 'success' for r in results),
        grammar_parser_changed=False, observations_are_not_whole_property_conformance=True), generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    report, generated = run()
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'RESULTS.json').write_text(json.dumps(report, indent=2) + '\n')
    for name, value in generated.items():
        (args.out / (name + '.json')).write_text(json.dumps(value['program'], indent=2) + '\n')
        (args.out / (name + '-source-map.json')).write_text(json.dumps(value, indent=2) + '\n')


if __name__ == '__main__':
    main()
