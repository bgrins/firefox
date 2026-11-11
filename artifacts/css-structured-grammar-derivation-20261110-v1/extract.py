import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
NAME = r'[a-z][a-z-]*'
TOKEN = re.compile(r'\s+|<<' + NAME + r'>>|' + NAME + r'|[|?\[\]]')
PRE = re.compile(r'<pre class=(?:"(propdef|prod)"|\'(propdef|prod)\')>(.*?)</pre>', re.S)


class Refusal(ValueError):
    pass


class Parser:
    def __init__(self, text, offset):
        self.tokens = []
        cursor = 0
        while cursor < len(text):
            match = TOKEN.match(text, cursor)
            if not match:
                raise Refusal('Unsupported grammar text at ' + str(offset + cursor))
            if not match[0].isspace():
                self.tokens.append((match[0], offset + match.start(), offset + match.end()))
            cursor = match.end()
        self.index = 0

    def peek(self):
        return self.tokens[self.index][0] if self.index < len(self.tokens) else None

    def pop(self):
        result = self.tokens[self.index]
        self.index += 1
        return result

    def alternative(self):
        node = self.sequence()
        while self.peek() == '|':
            token = self.pop()
            if self.peek() == '|':
                raise Refusal('Unsupported double-bar combinator')
            right = self.sequence()
            node = dict(op='alt', args=[node, right], span=[node['span'][0], right['span'][1]], operator=[token[1], token[2]])
        return node

    def sequence(self):
        nodes = []
        while self.peek() not in (None, '|', ']'):
            token, start, end = self.pop()
            if token == '[':
                node = self.alternative()
                if self.peek() != ']':
                    raise Refusal('Unclosed group')
                closing = self.pop()
                node = dict(node, span=[start, closing[2]])
            elif re.fullmatch(NAME, token):
                node = dict(op='keyword', args=[token], span=[start, end])
            elif token.startswith('<<'):
                node = dict(op='ref', args=[token[2:-2]], span=[start, end])
            else:
                raise Refusal('Unexpected grammar token: ' + token)
            if self.peek() == '?':
                _, start, end = self.pop()
                node = dict(op='optional', args=[node], span=[node['span'][0], end], operator=[start, end])
            nodes.append(node)
        if not nodes:
            raise Refusal('Empty grammar component')
        node = nodes[0]
        for right in nodes[1:]:
            node = dict(op='seq', args=[node, right], span=[node['span'][0], right['span'][1]], operator=[node['span'][1], right['span'][0]])
        return node

    def parse(self):
        result = self.alternative()
        if self.peek() is not None:
            raise Refusal('Trailing grammar tokens')
        return result


def extract(source, property_name='justify-content'):
    properties, productions = {}, {}
    for block in PRE.finditer(source):
        kind = block[1] or block[2]
        body = block[3]
        offset = block.start(3)
        if kind == 'propdef':
            fields = {}
            for line in re.finditer(r'[^\n]+', body):
                if not line[0].strip():
                    continue
                field = re.fullmatch(r'\s*([A-Za-z ]+):[ \t]*(.*)', line[0])
                if not field or field[1] in fields:
                    raise Refusal('Unsupported or duplicate property field')
                fields[field[1]] = (field[2], offset + line.start() + field.start(2))
            if 'Name' not in fields:
                raise Refusal('Missing property name')
            name = fields['Name'][0]
            if name in properties:
                raise Refusal('Duplicate property definition: ' + name)
            properties[name] = (fields, [block.start(), block.end()])
        else:
            label = re.search(r'<dfn>&lt;(' + NAME + r')></dfn>', body)
            if label:
                name = label[1]
                if name in productions:
                    raise Refusal('Duplicate production: ' + name)
                productions[name] = (body, offset, [block.start(), block.end()])
    if property_name not in properties:
        raise Refusal('Missing property: ' + property_name)
    fields, block_span = properties[property_name]
    anchors = {'justify-content': 'align-justify-content', 'justify-items': 'justify-items-property'}
    expected_anchor = anchors.get(property_name)
    if expected_anchor is None:
        raise Refusal('Property has no reviewed source anchor')
    headings = list(re.finditer(r"<h([1-3]) id=([\"'])([^\"']+)\2>", source))
    candidates = [h for h in headings if h[3] == expected_anchor]
    preceding = [h for h in headings if h.start() < block_span[0]]
    if len(candidates) != 1 or not preceding or preceding[-1][3] != expected_anchor:
        raise Refusal('Missing, duplicate or moved property anchor')
    if 'Value' not in fields:
        raise Refusal('Missing Value field')
    text, offset = fields['Value']
    tree = Parser(text, offset).parse()
    program, maps, definitions, edges = [], [], {}, []

    def location(span):
        start, end = span
        return dict(bytes=[len(source[:start].encode()), len(source[:end].encode())], text=source[start:end])

    def emit(node, active):
        if node['op'] == 'ref':
            name = node['args'][0]
            if name in active:
                raise Refusal('Cyclic production: ' + name)
            if name not in productions:
                raise Refusal('Unresolved production: ' + name)
            body, start, span = productions[name]
            match = re.fullmatch(r'\s*<dfn>&lt;' + re.escape(name) + r'></dfn>\s*=\s*(.*?)\s*', body, re.S)
            if not match:
                raise Refusal('Unsupported production markup: ' + name)
            rhs = match[1]
            parsed = Parser(rhs, start + match.start(1)).parse()
            definitions[name] = dict(grammar=rhs, source=location(span))
            edges.append(dict(name=name, source=location(node['span']), via=active))
            emit(parsed, active + [name])
            return
        if node['op'] != 'keyword':
            for child in node['args']:
                emit(child, active)
        instruction = [node['op']] + (node['args'] if node['op'] == 'keyword' else [])
        maps.append(dict(instruction=len(program), op=node['op'], source=location(node['span']), operator_source=location(node.get('operator', node['span'])), via=active))
        program.append(instruction)

    emit(tree, [])
    return dict(property=property_name, anchor=expected_anchor, program=program, source_map=maps, dependencies=definitions,
        references=edges, property_block=location(block_span), value=location([offset, offset+len(text)]),
        ignored_property_fields={k: v[0] for k, v in fields.items() if k not in ('Name', 'Value')})


def quote_program(program):
    ops = ['.keyword ' + json.dumps(op[1]) if op[0] == 'keyword' else '.' + op[0]
           for op in program]
    json_ops = ['.arr #[' + ', '.join('.str ' + json.dumps(x) for x in op) + ']' for op in program]
    return ('import ProgramLaws\nimport Laws\nimport JsonInput\n\nnamespace CssGrammar\n\n'
            'def extractedProgram : List Op := [\n  ' + ',\n  '.join(ops) +
            ']\n\ndef extractedJson : Lean.Json := .arr #[\n  ' + ',\n  '.join(json_ops) + ']\n\nend CssGrammar\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--property', default='justify-content')
    args = parser.parse_args()
    pins = json.loads((ROOT / 'SOURCE.json').read_text())
    for record in pins['files']:
        if hashlib.sha256((ROOT / record['file']).read_bytes()).hexdigest() != record['sha256']:
            raise Refusal('Pinned source changed')
    result = extract((ROOT / 'inputs/css-align-3.bs').read_text(), args.property)
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'program.json').write_text(json.dumps(result['program'], indent=2) + '\n')
    (args.out / 'extraction.json').write_text(json.dumps(result, indent=2) + '\n')
    (args.out / 'Fixture.lean').write_text(quote_program(result['program']))


if __name__ == '__main__':
    main()
