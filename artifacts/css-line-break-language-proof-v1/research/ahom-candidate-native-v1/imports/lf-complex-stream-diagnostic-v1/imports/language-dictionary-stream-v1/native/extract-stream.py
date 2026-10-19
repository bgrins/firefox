import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'development-build/stream'
OUT.mkdir(parents=True,exist_ok=True)
adaptations=[]


def replace_once(text, before, after, name):
    count=text.count(before)
    assert count==1, (name,count)
    adaptations.append({'name':name,'before':before,'after':after,'count':count})
    return text.replace(before,after)


def strip(s):
    return re.sub(r'^#include[^\n]*\n','',s,flags=re.M)


def generate(flavor):
    facade=(ROOT/'native/hyphen-producer-input/facade.hpp').read_text()
    facade=replace_once(facade,'namespace mozilla { template<class T>using StaticRefPtr=RefPtr<T>;template<class T>void ClearOnShutdown(T*){} }\nstruct nsAtom{std::string value;};','#include "retained-atom-facade.h"',flavor+' retained atom')
    facade=replace_once(facade,'#include "provider/unicode-native.h"','#include "unicode-native.h"',flavor+' unicode include')
    facade=replace_once(facade,'#include "../native/range-types.hpp"','#include "range-types-native.hpp"',flavor+' glyph include')
    begin=facade.index('namespace mozilla::intl {\ninline bool NS_IsSpace')
    end=facade.index('#include "range-types-native.hpp"',begin)
    facade=facade[:begin]+(ROOT/'native/stream-provider-facade.h').read_text()+facade[end:]
    header=replace_once(strip((ROOT/f'source/{flavor}/dom/base/nsLineBreaker.h').read_text()),' private:', ' public:',flavor+' state access')
    native=strip((ROOT/f'source/{flavor}/dom/base/nsLineBreaker.cpp').read_text())
    hit='if (sLastLanguage == aLanguage) {' if flavor=='candidate' else 'if (sLastHyphenationLanguage == aHyphenationLanguage) {'
    native=replace_once(native,hit,hit+'\n    language_trace("resolver cache hit");',flavor+' cache hit trace')
    if flavor=='candidate':
        entry='static bool IsChineseOrJapanese(nsAtom* aLanguage) {'
        trace='\n  language_trace((std::string("resolver request ")+(aLanguage?aLanguage->value:"<null>")).c_str());'
    else:
        entry='if (aHyphenationLanguage && !mCurrentWordLanguage) {'
        trace='\n  language_trace((std::string("resolver request ")+aHyphenationLanguage->value).c_str());'
    native=replace_once(native,entry,entry+trace,flavor+' resolver request trace')
    h=(ROOT/'source/candidate/intl/hyphenation/glue/nsHyphenator.cpp').read_text()
    hyphen=h[h.index('nsresult nsHyphenator::Hyphenate('):h.index('ipc::ReadOnlySharedMemoryHandle nsHyphenator::CloneHandle()')]
    runner=(ROOT/'native/stream-runner.cpp').read_text()
    target=OUT/f'stream-{flavor}.cpp'
    target.write_text('\n'.join([facade,header,'#include "break-sink-native.hpp"',hyphen,native,runner]))
    return target


if __name__=='__main__':
    for flavor in ['original','candidate']:
        print(generate(flavor))
    (OUT/'adaptations.json').write_text(json.dumps(adaptations,indent=2)+'\n')
