import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "development-build/provider"
OUT.mkdir(parents=True, exist_ok=True)
units = []
def emit(relative, target, transform=lambda s:s):
    p = ROOT / relative
    raw = p.read_bytes()
    text = raw.decode()
    text = re.sub(r'^#include[^\n]*\n', '', text, flags=re.M)
    text = transform(text)
    (OUT / target).write_text(text)
    units.append(dict(source=relative, sha256=hashlib.sha256(raw).hexdigest(), output=target, output_sha256=hashlib.sha256(text.encode()).hexdigest()))
emit('source/providers/intl/components/src/UnicodeScriptCodes.h','script-codes.h')
emit('source/providers/mfbt/HashFunctions.h','hash.h')
emit('source/providers/mfbt/MruCache.h','mru.h')
s = (ROOT/'source/providers/intl/lwbrk/Segmenter.h').read_text()
enums = '\n'.join(re.search(r'enum class '+name+r' : uint8_t \{.*?\n\};',s,re.S)[0] for name in ['WordBreakRule','LineBreakRule'])
(OUT/'enums.h').write_text('namespace mozilla::intl {\n'+enums+'\n}\n')
emit('source/candidate/intl/lwbrk/LineBreakCache.h','cache.h')
emit('source/candidate/intl/lwbrk/LineBreaker.h','breaker.h')
emit('source/candidate/intl/lwbrk/LineBreaker.cpp','breaker.cpp')
(OUT/'extraction.json').write_text(json.dumps(units,indent=2)+'\n')

observed=(OUT/'breaker.cpp').read_text()
replacements=[
 ('  MOZ_ASSERT(aText.Length() == aBreakBefore.Length());','  provider_input(aText, unsigned(aWordBreak), unsigned(aLevel), aIsChineseOrJapanese);\n  MOZ_ASSERT(aText.Length() == aBreakBefore.Length());',2),
 ('    entry.emplace(LineBreakCache::Cache()->Lookup(key));','    entry.emplace(LineBreakCache::Cache()->Lookup(key));\n    provider_event(*entry ? "cache hit" : "cache miss");',1),
 ('    if (*entry) {','    if (*entry) {',1),
 ('  if (aUseDefault) {','  provider_event(std::string("segmenter ") + (aUseDefault ? "default" : "options"));\n  if (aUseDefault) {',1),
 ('    auto locale = capi::icu4x_Locale_from_string_mv1(','    provider_event("locale init zh");\n    auto locale = capi::icu4x_Locale_from_string_mv1(',1),
 ('    entry->Set(LineBreakCache::EntryType{','    provider_event("cache store");\n    entry->Set(LineBreakCache::EntryType{',1),
]
for before,after,count in replacements:
    assert observed.count(before)==count,(before,observed.count(before))
    observed=observed.replace(before,after)
(OUT/'breaker-observed.cpp').write_text(observed)
(OUT/'provider-instrumentation.json').write_text(json.dumps(replacements,indent=2)+'\n')
