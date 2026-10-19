import json
import re
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
helper = runpy.run_path(str(ROOT / 'native/extract-full.py'))
full, strip = helper['full'], helper['strip']
OUT = ROOT / 'development-build/full'
SRC = ROOT / 'source/providers'
BRIDGE = ROOT / 'provider-bridge-v1'
prefix = (ROOT / 'native/facade.hpp').read_text().split('extern "C" int8_t u_charType')[0]
prefix = prefix.replace('struct nsAtom{std::string value;};', 'struct nsAtom{std::string value;mutable std::u16string utf16;size_t GetLength()const{return value.size();}const char16_t*GetUTF16String()const{utf16.assign(value.begin(),value.end());return utf16.data();}};')
prefix = '#define U_DISABLE_RENAMING 1\n#include "unicode/uchar.h"\n#include "unicode/uscript.h"\n' + prefix
unicode = (BRIDGE / 'development-build/provider/unicode-native.h').read_text()
properties = SRC / 'intl/components/src/UnicodeProperties.h'
script = full(SRC / 'intl/components/src/UnicodeScriptCodes.h', 'enum class Script', True)
unicode = unicode.replace('namespace mozilla::intl {', 'namespace mozilla::intl {\n' + script, 1)
methods = '\n'.join(full(properties, marker, marker.startswith('enum')) for marker in [
    'enum class IntProperty', 'static inline int32_t GetIntPropertyValue(',
    'enum class BinaryProperty', 'static inline bool HasBinaryProperty(',
    'static inline bool IsEastAsianWidthFHW(', 'static inline bool IsEastAsianWidthFHWexcludingEmoji(',
    'static inline bool IsPunctuation(', 'static inline Script GetScriptCode(',
])
unicode = unicode.replace('class UnicodeProperties { public:', 'class UnicodeProperties { public:\n' + methods)
skip = '\n'.join(strip((SRC / name).read_text()) for name in ['mfbt/BinarySearch.h', 'gfx/thebes/gfxSkipChars.h', 'gfx/thebes/gfxSkipChars.cpp'])
skip_prefix = '#define MOZ_STACK_CLASS\n#define MOZ_UNLIKELY(x) (x)\nstruct CriticalError{template<class T>CriticalError&operator<<(T x){std::cerr<<x;return *this;}};inline CriticalError gfxCriticalError(){return {};}\n'
header = SRC / 'layout/generic/nsTextFrameUtils.h'
clazz = full(header, 'class nsTextFrameUtils {', True)
ops = '''using TextFlags=nsTextFrameUtils::Flags;
inline TextFlags operator|(TextFlags a,TextFlags b){return TextFlags(uint16_t(a)|uint16_t(b));}
inline TextFlags&operator|=(TextFlags&a,TextFlags b){return a=a|b;}
'''
bidi = (SRC / 'intl/unicharutil/util/nsBidiUtils.h').read_text()
bidi = bidi[bidi.index('#define LRM_CHAR'):bidi.index('/**', bidi.index('inline bool IsBidiControl(uint32_t'))]
arabic = re.search(r'#define IS_ARABIC_CHAR\(c\)[\s\S]*?(?=\n#define)', (SRC / 'intl/unicharutil/util/nsBidiUtils.h').read_text())[0]
helpers = 'namespace mozilla::unicode {\n' + '\n'.join([
    full(SRC / 'intl/unicharutil/util/nsUnicodeProperties.cpp', 'bool IsClusterExtenderExcludingJoiners(uint32_t aCh, uint8_t aCategory)'),
    full(SRC / 'intl/unicharutil/util/nsUnicodeProperties.h', 'inline bool IsClusterExtenderExcludingJoiners(uint32_t aCh)'),
    full(SRC / 'intl/unicharutil/util/nsUnicodeProperties.h', 'inline bool IsDefaultIgnorable('),
]) + '\n}\n'
unichar = SRC / 'intl/unicharutil/util/nsUnicharUtils.cpp'
helpers += full(unichar, 'char16_t ToLowerCaseASCII(char16_t')
helpers += '\nnamespace mozilla {\nstatic constexpr uint32_t kWonCurrencySign = 0x20A9;\n' + full(unichar, 'bool IsSegmentBreakSkipChar(') + '\n' + full(unichar, 'bool IsEastAsianPunctuation(') + '\n}\n'
source = strip((SRC / 'layout/generic/nsTextFrameUtils.cpp').read_text())
source = source[:source.index('template <typename CharT>\nstatic uint32_t DoComputeApproximateLength')]
text = '\n'.join([prefix, unicode, skip_prefix, skip, 'namespace mozilla::dom{class Text;}\nstruct nsStyleText;', clazz, ops,
    re.search(r'^#define CH_SHY[^\n]*', header.read_text(), re.M)[0] + '\n' + re.search(r'^#define IS_ZERO_WIDTH_SPACE[^\n]*', (SRC / 'intl/unicharutil/util/nsUnicharUtils.h').read_text(), re.M)[0], bidi, arabic, helpers, source])
(OUT / 'transform-native.hpp').write_text(text)
(OUT / 'transform.cpp').write_text(text + '\n' + (ROOT / 'native/transform-runner.cpp').read_text())
(OUT / 'transform-extraction.json').write_text(json.dumps(helper['records'], indent=2) + '\n')
