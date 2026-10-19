import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def between(text, start, end):
    assert text.count(start) == 1, start
    first = text.index(start)
    last = text.index(end, first)
    return text[first:last]


def generate(candidate=True):
    for entry in json.loads((BASE / 'SOURCE-v1.json').read_text()):
        assert hashlib.sha256((BASE / entry['copy']).read_bytes()).hexdigest() == entry['sha256'], entry['copy']
    label = 'candidate' if candidate else 'original'
    callee = (BASE / 'source' / (label + '-SVGMaskFrame.cpp')).read_text()
    caller = (BASE / 'source' / (label + '-SVGIntegrationUtils.cpp')).read_text()
    header = (BASE / 'source' / (label + '-SVGMaskFrame.h')).read_text()
    rendering = (BASE / 'source/nsCSSRendering.h').read_text()
    callee = between(callee, 'already_AddRefed<SourceSurface> SVGMaskFrame::GetMaskForMaskedFrame(', '\ngfxRect SVGMaskFrame::GetMaskArea')
    caller = between(caller, 'static bool PaintMaskSurface(', '\nstruct MaskPaintResult')
    params = between(header, '  struct MaskParams {', '\n  // SVGMaskFrame method:')
    operator = between(rendering, '  static CompositionOp GetGFXCompositeMode(', '\n\n protected:')
    start = header.index('  already_AddRefed<SourceSurface> GetMaskForMaskedFrame(')
    declaration = header[start:header.index(';', start) + 1]

    prefix = (BASE / 'adapter-prefix.cpp').read_text()
    prefix = prefix.replace('@@PARAMS@@', params).replace('@@DECLARATION@@', declaration).replace('@@OPERATOR@@', operator)
    return '#define CANDIDATE ' + str(int(candidate)) + '\n' + prefix + callee + caller + (BASE / 'adapter-suffix.cpp').read_text()
