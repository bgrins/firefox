import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('use python3 -I -S, without optimization')
sys.dont_write_bytecode = True

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def selected(text, anchor):
    if text.count(anchor) != 1:
        raise ValueError(('anchor is not unique', anchor, text.count(anchor)))
    start = text.index(anchor)
    i = start
    depth = 0
    opened = False
    while i < len(text):
        if text.startswith('//', i):
            end = text.find('\n', i)
            i = len(text) if end < 0 else end + 1
            continue
        if text.startswith('/*', i):
            end = text.find('*/', i + 2)
            if end < 0:
                raise ValueError('unterminated comment')
            i = end + 2
            continue
        if text[i] in '\"\'':
            quote = text[i]
            i += 1
            while i < len(text) and text[i] != quote:
                i += 2 if text[i] == '\\' else 1
            if i == len(text):
                raise ValueError('unterminated quote')
            i += 1
            continue
        if text[i] == '{':
            opened = True
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if opened and depth == 0:
                return start, i + 1, text[start:i + 1]
        elif not opened and text[i] == ';':
            raise ValueError(('declaration has no body', anchor))
        i += 1
    raise ValueError(('missing close', anchor))

SPECS = {'nsFlexContainerFrame.frozen.cpp': ['class nsFlexContainerFrame::CachedBAxisMeasurement', 'class CachedFinalReflowMetrics', 'class nsFlexContainerFrame::CachedFlexItemData', 'struct nsFlexContainerFrame::SharedFlexData final', 'struct nsFlexContainerFrame::PerFragmentFlexData final', 'class nsFlexContainerFrame::FlexLine final', 'class nsFlexContainerFrame::FlexItem final'], 'nsIFrame.frozen.h': ['static void DeleteValue(T* aPropertyValue)', 'void RemoveAllProperties()'], 'FrameProperties.h': ['struct FramePropertyDescriptor : public FramePropertyDescriptorUntyped', 'void RemoveAll(const nsIFrame* aFrame)', 'void DestroyValueFor(const nsIFrame* aFrame)'], 'nsIFrame.frozen.cpp': ['void nsIFrame::Destroy(DestroyContext& aContext)'], 'PresShell.cpp': ['void PresShell::NotifyDestroyingFrame(nsIFrame* aFrame)'], 'nsTArray.h': ['~nsTArray_Impl() {', 'nsTArray_base<RelocationStrategy>::~nsTArray_base()', 'static inline void Destruct(E* aE)', 'void DestructRange(index_type aStart, size_type aCount)', 'MOZ_REINITIALIZES void ClearAndRetainStorage()', 'void nsTArray_base<RelocationStrategy>::MoveConstructNonAutoArray(', 'auto nsTArray_base<RelocationStrategy>::TakeHeaderForMove(size_type aElemSize)']}

def bindings():
    result = []
    for filename, anchors in SPECS.items():
        text = (ROOT / 'source' / filename).read_text()
        for anchor in anchors:
            start, end, body = selected(text, anchor)
            result.append({'file': 'source/' + filename, 'anchor': anchor,
                           'start_byte_utf8': len(text[:start].encode()),
                           'end_byte_utf8': len(text[:end].encode()),
                           'sha256': hashlib.sha256(body.encode()).hexdigest(),
                           'text': body})
    text = (ROOT / 'source/nsIFrame.frozen.h').read_text()
    for name in ['NS_DECLARE_FRAME_PROPERTY_DELETABLE', 'NS_DECLARE_FRAME_PROPERTY_WITH_DTOR']:
        anchor = '#define ' + name + '('
        if text.count(anchor) != 1:
            raise ValueError('macro not unique')
        start = text.index(anchor)
        end = start
        while True:
            newline = text.find('\n', end)
            if newline < 0:
                raise ValueError('unterminated macro')
            continued = text[newline - 1] == '\\'
            end = newline + 1
            if not continued:
                break
        body = text[start:end]
        result.append({'file': 'source/nsIFrame.frozen.h', 'anchor': anchor,
                       'start_byte_utf8': len(text[:start].encode()),
                       'end_byte_utf8': len(text[:end].encode()),
                       'sha256': hashlib.sha256(body.encode()).hexdigest(), 'text': body})
    return result

if __name__ == '__main__':
    print(json.dumps(bindings(), indent=2))
