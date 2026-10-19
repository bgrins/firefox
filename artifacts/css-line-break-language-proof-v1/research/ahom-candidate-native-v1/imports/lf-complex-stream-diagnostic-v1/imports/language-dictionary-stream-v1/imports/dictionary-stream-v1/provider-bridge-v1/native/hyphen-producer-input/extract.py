from pathlib import Path
import re, hashlib, json

def without_includes(text):
    return re.sub(r'^#include[^\n]*\n', '', text, flags=re.M)

def generate(root, out, flavor='candidate'):
    header=root/'source'/flavor/'dom/base/nsLineBreaker.h'
    cpp=root/'source'/flavor/'dom/base/nsLineBreaker.cpp'
    provider=root/'source/providers/intl/hyphenation/glue/nsHyphenator.cpp'
    h=provider.read_text()
    start=h.index('nsresult nsHyphenator::Hyphenate(')
    end=h.index('ipc::ReadOnlySharedMemoryHandle nsHyphenator::CloneHandle()',start)
    pieces=[(root/'native/facade.hpp').read_text(), without_includes(header.read_text()), h[start:end], without_includes(cpp.read_text()), (root/'native/runner.cpp').read_text()]
    dest=out/('breaker-'+flavor+'.cpp')
    dest.write_text('\n'.join(pieces))
    return dest
