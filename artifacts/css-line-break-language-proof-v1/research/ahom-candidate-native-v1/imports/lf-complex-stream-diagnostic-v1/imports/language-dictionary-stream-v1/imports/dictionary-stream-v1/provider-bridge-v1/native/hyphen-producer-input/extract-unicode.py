import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "development-build/provider"
OUT.mkdir(parents=True, exist_ok=True)
units = []


def full(path, marker, semicolon=False):
    raw = (ROOT / 'source/providers' / path).read_bytes()
    s = raw.decode()
    start = s.index(marker)
    brace = s.index('{', start)
    depth = 0
    pattern = r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|[{}]'
    for token in re.finditer(pattern, s[brace:], re.S):
        t = token[0]
        if t == '{':
            depth += 1
        elif t == '}':
            depth -= 1
            if not depth:
                end = brace + token.end()
                if semicolon:
                    end = s.index(';', end) + 1
                text = s[start:end]
                units.append(dict(source=path, source_sha256=hashlib.sha256(raw).hexdigest(), marker=marker, text_sha256=hashlib.sha256(text.encode()).hexdigest()))
                return text
    raise ValueError(marker)


prop = 'intl/components/src/UnicodeProperties.h'
util = 'intl/unicharutil/util/nsUnicodeProperties.h'
cpp = 'intl/unicharutil/util/nsUnicodeProperties.cpp'
case = 'intl/unicharutil/util/nsUnicharUtils.cpp'
category = full('intl/components/src/GeneralCategory.h', 'enum class GeneralCategory', True)
char = full(prop, '  static inline GeneralCategory CharType')
lower = full(prop, '  static inline uint32_t ToLower(')
hb = full('gfx/harfbuzz/src/hb-unicode.h', 'typedef enum', True)
gen = full('intl/unicharutil/nsUGenCategory.h', 'enum class nsUGenCategory', True)
arr1 = full(cpp, 'const nsUGenCategory sDetailedToGeneralCategory[]', True)
arr2 = full(cpp, 'const hb_unicode_general_category_t sICUtoHBcategory', True)
get1 = full(util, 'inline uint8_t GetGeneralCategory')
get2 = full(util, 'inline nsUGenCategory GetGenCategory')
ascii_table = full(case, 'static const uint8_t gASCIIToLower', True)
inline = full(case, 'static MOZ_ALWAYS_INLINE uint32_t ToLowerCase_inline')
call = full(case, 'uint32_t ToLowerCase(uint32_t')
text = '''#pragma once
#include <cstdint>
#define MOZ_ALWAYS_INLINE inline
#define IS_ASCII(u) ((u) < 0x80)
#define U_CHAR_CATEGORY_COUNT 30
extern "C" { int8_t u_charType(int32_t); int32_t u_tolower(int32_t); }
''' + hb + '\n' + gen + '\nnamespace mozilla::intl {\n' + category + '\nclass UnicodeProperties { public:\n' + char + '\n' + lower + '\n};\n}\nnamespace mozilla::unicode {\n' + arr1 + '\n' + arr2 + '\n' + get1 + '\n' + get2 + '\n}\nusing namespace mozilla;\n' + ascii_table + '\n' + inline + '\n' + call + '\n'
(OUT / 'unicode-native.h').write_text(text)
(OUT / 'unicode-extraction.json').write_text(json.dumps(units, indent=2) + '\n')
