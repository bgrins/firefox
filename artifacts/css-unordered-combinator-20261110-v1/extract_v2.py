import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('baseline_extract', ROOT / 'baseline/extract.py')
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)
Refusal = baseline.Refusal
TOKEN = re.compile(r'\s+|<<' + baseline.NAME + r'>>|' + baseline.NAME + r'|\|\||[|?\[\]]')


class Parser(baseline.Parser):
    def __init__(self, text, offset=0):
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

    def alternative(self):
        node = self.unordered()
        while self.peek() == '|':
            token = self.pop()
            right = self.unordered()
            node = dict(op='alt', args=[node, right], span=[node['span'][0], right['span'][1]], operator=[token[1], token[2]])
        return node

    def unordered(self):
        nodes, operators = [self.sequence()], []
        while self.peek() == '||':
            token = self.pop()
            operators.append([token[1], token[2]])
            nodes.append(self.sequence())
        if len(nodes) == 1:
            return nodes[0]
        return dict(op='unordered', args=nodes, span=[nodes[0]['span'][0], nodes[-1]['span'][1]], operators=operators)

    def sequence(self):
        nodes = []
        while self.peek() not in (None, '|', '||', ']'):
            token, start, end = self.pop()
            if token == '[':
                node = self.alternative()
                if self.peek() != ']':
                    raise Refusal('Unclosed group')
                closing = self.pop()
                node = dict(node, span=[start, closing[2]])
            elif re.fullmatch(baseline.NAME, token):
                node = dict(op='keyword', args=[token], span=[start, end])
            elif token.startswith('<<'):
                raise Refusal('Unresolved production: ' + token)
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


def emit(tree, source):
    program, locations = [], []

    def location(span):
        start, end = span
        return dict(bytes=[len(source[:start].encode()), len(source[:end].encode())], text=source[start:end])

    def visit(node):
        if node['op'] != 'keyword':
            for child in node['args']:
                visit(child)
        args = node['args'] if node['op'] == 'keyword' else [len(node['args'])] if node['op'] == 'unordered' else []
        operators = node.get('operators', [node.get('operator', node['span'])])
        locations.append(dict(instruction=len(program), source=location(node['span']), operators=[location(x) for x in operators]))
        program.append([node['op']] + args)

    visit(tree)
    return dict(program=program, source_map=locations)


def pinned_text_transform(source=None, contexts=None):
    source = (ROOT / 'inputs/css-text-3.bs').read_bytes() if source is None else source
    expected = '87014a5f761a435f769754e6ab62be43c80628c6fc7cee59671c810122a9de28'
    if hashlib.sha256(source).hexdigest() != expected:
        raise Refusal('Pinned source changed')
    contexts = json.loads((ROOT / 'inputs/transfer-contexts.json').read_text()) if contexts is None else contexts
    records = [x for x in contexts['properties'] if x['property'] == 'text-transform']
    if len(records) != 1 or records[0]['anchor'] != 'text-transform-property':
        raise Refusal('Missing or changed reviewed anchor')
    record = records[0]
    for field in ('block', 'value', 'heading'):
        start, end = record[field]['bytes']
        if source[start:end].decode() != record[field]['text']:
            raise Refusal('Changed reviewed source span')
    start = record['value']['bytes'][0]
    offset = len(source[:start].decode())
    tree = Parser(record['value']['text'], offset).parse()
    return dict(property='text-transform', anchor=record['anchor'], **emit(tree, source.decode()))


if __name__ == '__main__':
    print(json.dumps(pinned_text_transform(), indent=2))
