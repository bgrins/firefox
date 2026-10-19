from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent

def text(path, variant='original'):
    a, b = variant in ['A', 'AB'], variant in ['B', 'AB']
    candidate = BASE / ('threshold-proposal' if b and path.endswith('gfxFontUtils.cpp') else 'lexicographic-proposal') / path
    if candidate.exists() and (a or (b and path.endswith('gfxFontUtils.cpp'))):
        return candidate.read_text()
    return (BASE / 'original' / path).read_text()

def block(source, marker, semicolon=False):
    start = source.index(marker)
    body = source.index('{', start)
    masked = re.sub(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                    lambda m: ' ' * len(m.group()), source, flags=re.S)
    depth = 1
    end = body + 1
    while depth:
        depth += (masked[end] == '{') - (masked[end] == '}')
        end += 1
    if semicolon:
        assert source[end] == ';'
        end += 1
    return source[start:end]

ITEMS = [
    ('gfx/thebes/gfxFontUtils.cpp', 'double StyleDistance(', ''),
    ('gfx/thebes/gfxFontUtils.cpp', 'double WidthDistance(', ''),
    ('gfx/thebes/gfxFontUtils.cpp', 'double WeightDistance(', ''),
    ('gfx/thebes/gfxFontEntry.cpp', 'WeightStyleWidthDistance(', 'score'),
    ('gfx/thebes/gfxFontEntry.cpp', 'void gfxFontFamily::FindAllFontsForStyle(', ''),
    ('gfx/thebes/gfxFontEntry.cpp', 'void gfxFontFamily::CheckForSimpleFamily(', ''),
    ('gfx/thebes/gfxFontEntry.h', 'inline bool gfxFontEntry::SupportsBold()', ''),
    ('gfx/thebes/gfxFontEntry.cpp', 'void gfxFontFamily::FindFontForChar(', ''),
    ('gfx/thebes/gfxFontEntry.cpp', 'void gfxFontFamily::SearchAllFontsForChar(', ''),
    ('gfx/thebes/SharedFontList.cpp', 'void Family::AddFaces(', 'shared'),
    ('gfx/thebes/SharedFontList.cpp', 'WSSDistance(', 'shared-score'),
    ('gfx/thebes/SharedFontList.cpp', 'bool Family::FindAllFacesForStyleInternal(', 'shared'),
    ('gfx/thebes/SharedFontList.cpp', 'void Family::FindAllFacesForStyle(', 'shared'),
    ('gfx/thebes/SharedFontList.cpp', 'void Family::SearchAllFontsForChar(', 'shared'),
    ('gfx/thebes/gfxPlatformFontList.cpp', 'already_AddRefed<gfxFont> gfxPlatformFontList::GlobalFontFallback(', ''),
]

def extracted(variant):
    result = []
    for path, marker, owner in ITEMS:
        src = text(path, variant)
        if owner.endswith('score'):
            marker = ('static inline ' if owner == 'score' else 'static ') + ('FontMatchDistance ' if variant in ['A', 'AB'] else 'double ') + marker
        body = block(src, marker)
        result.append({'source': path, 'owner': owner, 'marker': marker, 'body': body,
                       'source_sha256': hashlib.sha256(src.encode()).hexdigest(),
                       'body_sha256': hashlib.sha256(body.encode()).hexdigest()})
    return result

def provider_items(variant):
    gen = text('objdir-full.noindex/layout/style/ServoStyleConsts.h')
    forward = text('layout/style/ServoStyleConstsForwards.h')
    inline = text('layout/style/ServoStyleConstsInlines.h')
    macro = forward[forward.index('#define SERVO_FIXED_POINT_HELPERS'):forward.index('\n\n', forward.index('#define SERVO_FIXED_POINT_HELPERS'))]
    parts = [('layout/style/ServoStyleConstsForwards.h', 'SERVO_FIXED_POINT_HELPERS', macro)]
    for name in ['WEIGHT', 'WIDTH', 'STYLE']:
        parts.append(('objdir-full.noindex/layout/style/ServoStyleConsts.h', 'fraction-bits-'+name, re.search(r'constexpr static const uint16_t StyleFONT_'+name+r'_FRACTION_BITS = \d+;', gen).group()))
    start = gen.rfind('template<', 0, gen.index('struct StyleFixedPoint {'))
    if start < 0:
        start = gen.rfind('template <', 0, gen.index('struct StyleFixedPoint {'))
    parts.append(('objdir-full.noindex/layout/style/ServoStyleConsts.h','StyleFixedPoint',block(gen[start:], gen[start:gen.index('struct StyleFixedPoint {')], True)))
    for name in ['Weight', 'Width', 'Style']:
        start = gen.index('using StyleFont'+name+'FixedPoint =')
        end = gen.index('struct StyleComputedFont'+name+'Range', start)
        end = gen.rfind('///', start, end)
        parts.append(('objdir-full.noindex/layout/style/ServoStyleConsts.h','StyleFont'+name+'-complete-and-constants',gen[start:end]))
    for marker in ['inline bool StyleFontWeight::IsBold()', 'inline bool StyleFontWeight::PreferBold()',
                   'inline bool StyleFontStyle::IsItalic()', 'inline float StyleFontStyle::ObliqueAngle()',
                   'inline float StyleFontStyle::SlantAngle()']:
        parts.append(('layout/style/ServoStyleConstsInlines.h',marker,block(inline, marker)))
    ranges = text('gfx/src/FontPropertyTypes.h')
    start = ranges.index('using FontSlantStyle =')
    parts.append(('gfx/src/FontPropertyTypes.h','FontPropertyRange-and-specializations',ranges[start:ranges.index('\n}  // namespace mozilla', start)]))
    if variant in ['A', 'AB']:
        parts.append(('gfx/thebes/gfxFontUtils.h','FontMatchDistance',block(text('gfx/thebes/gfxFontUtils.h', variant), 'class FontMatchDistance', True)))
    return [{'source': path, 'marker': marker, 'body': body,
             'source_sha256': hashlib.sha256(text(path,variant).encode()).hexdigest(),
             'body_sha256': hashlib.sha256(body.encode()).hexdigest()} for path,marker,body in parts]

def types(variant):
    return 'namespace mozilla {\n' + '\n\n'.join(row['body'] for row in provider_items(variant)) + '\n}\nusing namespace mozilla;\n'

def generate(variant, driver):
    prefix = (BASE / 'adapter-prefix.h').read_text()
    suffix = (BASE / 'adapter.h').read_text()
    providers=environment_items(variant)
    suffix=suffix.replace('PRESENTATION_DECLARATIONS', providers[0]['body']+'\n'+providers[1]['body'])
    suffix=suffix.replace('NORMAL_STYLE_PROVIDER',providers[2]['body'])
    globalsrc = block(text('gfx/thebes/gfxFontEntry.h', variant), 'struct GlobalFontMatch', True)
    score = text('gfx/thebes/gfxFontUtils.h', variant)
    constants = '\n'.join(re.findall(r'constexpr double k(?:PresentationMismatch|WidthFactor|StyleFactor|WeightFactor) = [^;]+;', score))
    out = [prefix, types(variant), constants, suffix.replace('GLOBAL_MATCH_DECLARATION', globalsrc)]
    for row in extracted(variant):
        body = row['body']
        if row['owner'].startswith('shared'):
            body = 'namespace mozilla::fontlist {\n' + body + '\n}'
        out.append(body)
    out.append(driver)
    return '\n\n'.join(out)

if __name__ == '__main__':
    print(json.dumps({v: [{k:x for k,x in e.items() if k != 'body'} for e in extracted(v)]
                      for v in ['original', 'B', 'A', 'AB']}, indent=2))


def manifest(variant):
    rows=extracted(variant)+provider_items(variant)+environment_items(variant)
    for path,marker,body in [
        ('gfx/thebes/gfxFontEntry.h','GlobalFontMatch',block(text('gfx/thebes/gfxFontEntry.h',variant),'struct GlobalFontMatch',True)),
    ]:
        rows.append(dict(source=path,marker=marker,body=body,
                         source_sha256=hashlib.sha256(text(path,variant).encode()).hexdigest(),
                         body_sha256=hashlib.sha256(body.encode()).hexdigest()))
    src=text('gfx/thebes/gfxFontUtils.h',variant)
    for constant in re.findall(r'constexpr double k(?:PresentationMismatch|WidthFactor|StyleFactor|WeightFactor) = [^;]+;',src):
        rows.append(dict(source='gfx/thebes/gfxFontUtils.h',marker=constant.split('=')[0].strip(),body=constant,
                         source_sha256=hashlib.sha256(src.encode()).hexdigest(),body_sha256=hashlib.sha256(constant.encode()).hexdigest()))
    return rows


def environment_items(variant):
    rows=[]
    for path,marker,semicolon in [
        ('gfx/thebes/gfxPlatform.h','enum class FontPresentation',True),
        ('gfx/thebes/gfxPlatform.h','inline bool PrefersColor(',False),
        ('gfx/thebes/gfxFont.h','bool IsNormalStyle() const',False),
    ]:
        src=text(path,variant);body=block(src,marker,semicolon)
        rows.append(dict(source=path,marker=marker,body=body,source_sha256=hashlib.sha256(src.encode()).hexdigest(),body_sha256=hashlib.sha256(body.encode()).hexdigest()))
    return rows
