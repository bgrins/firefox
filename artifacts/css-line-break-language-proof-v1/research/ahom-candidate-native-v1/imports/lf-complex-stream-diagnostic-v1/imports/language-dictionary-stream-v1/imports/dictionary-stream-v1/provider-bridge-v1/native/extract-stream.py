import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'development-build/stream'
OUT.mkdir(parents=True,exist_ok=True)


def strip(s):
    return re.sub(r'^#include[^\n]*\n','',s,flags=re.M)


def generate(flavor):
    facade=(ROOT/'native/hyphen-producer-input/facade.hpp').read_text()
    facade=facade.replace('namespace mozilla { template<class T>using StaticRefPtr=RefPtr<T>;template<class T>void ClearOnShutdown(T*){} }\nstruct nsAtom{std::string value;};','#include "retained-atom-facade.h"')
    facade=facade.replace('#include "provider/unicode-native.h"','#include "unicode-native.h"')
    facade=facade.replace('#include "../native/range-types.hpp"','#include "range-types-native.hpp"')
    begin=facade.index('namespace mozilla::intl {\ninline bool NS_IsSpace')
    end=facade.index('#include "range-types-native.hpp"',begin)
    facade=facade[:begin]+(ROOT/'native/stream-provider-facade.h').read_text()+facade[end:]
    header=strip((ROOT/f'source/{flavor}/dom/base/nsLineBreaker.h').read_text()).replace(' private:', ' public:')
    native=strip((ROOT/f'source/{flavor}/dom/base/nsLineBreaker.cpp').read_text())
    native=native.replace('if (sLastLanguage == aLanguage) {','if (sLastLanguage == aLanguage) {\n    language_trace("resolver cache hit");')
    native=native.replace('if (sLastLanguage == aHyphenationLanguage) {','if (sLastLanguage == aHyphenationLanguage) {\n    language_trace("resolver cache hit");')
    h=(ROOT/'source/candidate/intl/hyphenation/glue/nsHyphenator.cpp').read_text()
    hyphen=h[h.index('nsresult nsHyphenator::Hyphenate('):h.index('ipc::ReadOnlySharedMemoryHandle nsHyphenator::CloneHandle()')]
    runner=(ROOT/'native/stream-runner.cpp').read_text()
    target=OUT/f'stream-{flavor}.cpp'
    target.write_text('\n'.join([facade,header,'#include "break-sink-native.hpp"',hyphen,native,runner]))
    return target


if __name__=='__main__':
    for flavor in ['original','candidate']:
        print(generate(flavor))
