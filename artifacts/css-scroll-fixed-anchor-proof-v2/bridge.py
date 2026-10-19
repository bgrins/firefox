import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def body(source, marker):
    start = source.index(marker)
    opened = source.index('{', start)
    depth = 0
    state = 'code'
    i = opened
    while i < len(source):
        c = source[i]
        pair = source[i:i + 2]
        if state == 'line':
            if c == '\n':
                state = 'code'
        elif state == 'block':
            if pair == '*/':
                state = 'code'
                i += 1
        elif state in ['"', "'"]:
            if c == '\\':
                i += 1
            elif c == state:
                state = 'code'
        elif pair == '//':
            state = 'line'
            i += 1
        elif pair == '/*':
            state = 'block'
            i += 1
        elif c in ['"', "'"]:
            state = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
        i += 1
    raise AssertionError(marker)


ITEMS = [
    'static void SetAnchorFlags(',
    'bool ScrollAnchorContainer::CanMaintainAnchor() const',
    'void ScrollAnchorContainer::SelectAnchor()',
    'ScrollAnchorContainer::ExamineResult\nScrollAnchorContainer::ExamineAnchorCandidate(',
    'nsIFrame* ScrollAnchorContainer::FindAnchorIn(nsIFrame*',
    'nsIFrame* ScrollAnchorContainer::FindAnchorInList(',
]


def extract(candidate=True):
    for e in json.loads((ROOT / 'SOURCE-v1.json').read_text()):
        assert hashlib.sha256((ROOT / e['copy']).read_bytes()).hexdigest() == e['sha256'], e['copy']
    name = 'candidate.cpp' if candidate else 'original.cpp'
    source = (ROOT / 'source' / name).read_text()
    snippets = {marker: body(source, marker) for marker in ITEMS}
    header = (ROOT / 'source/ScrollAnchorContainer.h').read_text()
    enum = body(header, 'enum class ExamineResult') + ';'
    placeholder = (ROOT / 'source/nsPlaceholderFrame.h').read_text()
    helpers = '\n'.join(body(placeholder, marker) for marker in [
        'static nsIFrame* GetRealFrameFor(nsIFrame*',
        'static nsIFrame* GetRealFrameForPlaceholder(const nsIFrame*'])
    return snippets, enum, helpers


def generate(candidate=True):
    snippets, enum, helpers = extract(candidate)
    adapter = (ROOT / 'adapter.cpp').read_text()
    return adapter.replace('/*EXAMINE_ENUM*/', enum).replace(
        '/*PLACEHOLDER_HELPERS*/', helpers).replace(
        '/*EXTRACTED_FUNCTIONS*/', '\n\n'.join(snippets.values()))


def extraction_map():
    result = []
    for candidate in [False, True]:
        snippets, enum, helpers = extract(candidate)
        for name, text in list(snippets.items()) + [('enum', enum), ('placeholder helpers', helpers)]:
            result.append(dict(variant='candidate' if candidate else 'original', item=name,
                               sha256=hashlib.sha256(text.encode()).hexdigest(), bytes=len(text.encode())))
    return result
