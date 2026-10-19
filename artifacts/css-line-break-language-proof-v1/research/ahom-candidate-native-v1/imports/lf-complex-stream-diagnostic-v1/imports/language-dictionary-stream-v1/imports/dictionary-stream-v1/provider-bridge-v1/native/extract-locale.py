import hashlib
import json
import re
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'development-build/provider'
helper = runpy.run_path(str(ROOT/'native/extract-unicode.py'))
full = helper['full']
units = helper['units']


def strip(s):
    return re.sub(r'^#include[^\n]*\n', '', s, flags=re.M)


def whole(path, name):
    raw=(ROOT/'source/providers'/path).read_bytes()
    (OUT/name).write_text(strip(raw.decode()))
    units.append(dict(source=path,source_sha256=hashlib.sha256(raw).hexdigest(),marker='complete file excluding includes'))


whole('intl/components/src/Locale.h','gecko-locale.h')
whole('intl/components/src/LocaleGenerated.cpp','locale-generated.cpp')
glue='intl/components/src/ICU4CGlue.h'
functions = [
    full(glue,'template <typename ICUStringFunction, typename Buffer>\nICUResult FillBufferWithICUCall'),
    full(glue,'template <typename T, size_t N>\nclass VectorToBufferAdaptor',True),
    full(glue,'template <typename ICUStringFunction, size_t InlineSize, typename CharType>\nICUResult FillBufferWithICUCall'),
]
(OUT/'locale-glue.h').write_text('namespace mozilla::intl {\n'+'\n'.join(functions)+'\n}\n')
path='intl/components/src/Locale.cpp'
s=(ROOT/'source/providers'/path).read_text()
prefix=strip(s[:s.index('ptrdiff_t Locale::UnicodeExtensionIndex')])
sort=full(path,'template <size_t InitialCapacity>\nstatic void SortAlphabetically(')
canonical=full(path,'Result<Ok, Locale::CanonicalizationError> Locale::CanonicalizeBaseName()')
rest=s[s.index('using LocaleId ='):]
(OUT/'locale.cpp').write_text(prefix+'\n'+sort+'\n'+canonical+'\n'+rest)
units.append(dict(source=path,source_sha256=hashlib.sha256(s.encode()).hexdigest(),marker='complete structural validators, complete SortAlphabetically/CanonicalizeBaseName, complete LocaleId through end'))
(OUT/'locale-extraction.json').write_text(json.dumps(units,indent=2)+'\n')
