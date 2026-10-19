import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "provider-bridge-v1"
OUT = ROOT / "development-build/full"
OUT.mkdir(parents=True, exist_ok=True)
records = []


def full(path, marker, semicolon=False):
    raw = path.read_bytes()
    source = raw.decode()
    lexical = r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|[{};]'
    definitions = []
    for occurrence in re.finditer(re.escape(marker), source):
        for token in re.finditer(lexical, source[occurrence.start():], re.S):
            if token[0] == ";":
                break
            if token[0] == "{":
                definitions.append((occurrence.start(), occurrence.start() + token.start()))
                break
    if len(definitions) != 1:
        raise ValueError((str(path), marker, "definition count", len(definitions)))
    start, brace = definitions[0]
    depth = 0
    tokens = r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|[{}]'
    for token in re.finditer(tokens, source[brace:], re.S):
        if token[0] == "{": depth += 1
        elif token[0] == "}":
            depth -= 1
            if depth == 0:
                end = brace + token.end()
                if semicolon: end = source.index(";", end) + 1
                text = source[start:end]
                records.append({"source": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(raw).hexdigest(), "marker": marker, "definition_count": len(definitions), "start_character": start, "end_character": end, "extracted_sha256": hashlib.sha256(text.encode()).hexdigest()})
                return text
    raise ValueError(marker)


def strip(text):
    return re.sub(r'^#include[^\n]*\n', '', text, flags=re.M)


def generate(flavor):
    facade = (ROOT / "native/facade.hpp").read_text()
    old = 'namespace mozilla { template<class T>using StaticRefPtr=RefPtr<T>;template<class T>void ClearOnShutdown(T*){} }\nstruct nsAtom{std::string value;};'
    assert facade.count(old) == 1
    atom = (BRIDGE / 'native/retained-atom-facade.h').read_text()
    atom = atom.replace('std::string value;', 'std::string value;mutable std::u16string utf16;size_t GetLength()const{return value.size();}const char16_t*GetUTF16String()const{utf16.assign(value.begin(),value.end());return utf16.data();}')
    facade = facade.replace(old, atom)
    facade = facade.replace('#include "provider/unicode-native.h"', '#include "transform-unicode.hpp"')
    facade = facade.replace('#include "../native/range-types.hpp"', '#include "range-types-adapted.hpp"')
    start = facade.index('namespace mozilla::intl {\ninline bool NS_IsSpace')
    end = facade.index('#include "range-types-adapted.hpp"', start)
    facade = facade[:start] + (BRIDGE / 'native/stream-provider-facade.h').read_text() + facade[end:]
    header = strip((ROOT / f'source/{flavor}/dom/base/nsLineBreaker.h').read_text()).replace(' private:', ' public:')
    native = strip((ROOT / f'source/{flavor}/dom/base/nsLineBreaker.cpp').read_text())
    provider = ROOT / 'source/providers/intl/hyphenation/glue/nsHyphenator.cpp'
    methods = full(provider, 'nsresult nsHyphenator::Hyphenate(') + '\n' + full(provider, 'void nsHyphenator::HyphenateWord(')
    frame = ROOT / f'source/{flavor}/layout/generic/nsTextFrame.cpp'
    sink = full(frame, 'class BreakSink final', True)
    captured = 'mCurrentWordHyphenationLimits' in header
    definitions = '#define HAS_CAPTURED_LIMITS ' + str(int(captured)) + '\n'
    runner = (ROOT / 'native/full-runner.cpp').read_text()
    target = OUT / f'breaker-{flavor}.cpp'
    target.write_text('\n'.join([facade, definitions, header, sink, methods, native, runner]))
    return target


if __name__ == '__main__':
    for flavor in ['original', 'candidate', 'standalone']:
        generate(flavor)
    (OUT / 'extraction.json').write_text(json.dumps(records, indent=2) + '\n')
