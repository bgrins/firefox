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

SPECS = {
    'nsIFrame.frozen.cpp': [
        'void nsIFrame::Destroy(DestroyContext& aContext)',
        'static void MaybeScheduleReflowSVGNonDisplayText(nsIFrame* aFrame)',
        'void nsIFrame::RemoveDisplayItemDataForDeletion()',
        'void AutoWeakFrame::Clear(',
        'void WeakFrame::Clear(',
    ],
    'nsIFrame.frozen.h': [
        'static void DeleteValue(T* aPropertyValue)',
        'void RemoveAllProperties()',
    ],
    'FrameProperties.h': [
        'void RemoveAll(const nsIFrame* aFrame)',
        'void DestroyValueFor(const nsIFrame* aFrame)',
    ],
    'PresShell.cpp': [
        'void PresShell::NotifyDestroyingFrame(nsIFrame* aFrame)',
        'void PresShell::ClearFrameRefs(nsIFrame* aFrame)',
        'void PresShell::RemoveAutoWeakFrame(AutoWeakFrame* aWeakFrame)',
        'void PresShell::RemoveWeakFrame(WeakFrame* aWeakFrame)',
    ],
    'nsContainerFrame.frozen.cpp': [
        'void nsContainerFrame::Destroy(DestroyContext& aContext)',
        'void nsContainerFrame::SafelyDestroyFrameListProp(',
    ],
    'nsSplittableFrame.cpp': [
        'void nsSplittableFrame::Destroy(DestroyContext& aContext)',
        'void nsSplittableFrame::RemoveFromFlow(nsIFrame* aFrame)',
    ],
    'nsCSSFrameConstructor.frozen.cpp': [
        'void nsCSSFrameConstructor::NotifyDestroyingFrame(nsIFrame* aFrame)',
    ],
    'nsFlexContainerFrame.frozen.cpp': [
        'class nsFlexContainerFrame::CachedBAxisMeasurement',
        'class CachedFinalReflowMetrics',
        'class nsFlexContainerFrame::CachedFlexItemData',
        'struct nsFlexContainerFrame::SharedFlexData final',
        'struct nsFlexContainerFrame::PerFragmentFlexData final',
        'class nsFlexContainerFrame::FlexLine final',
        'class nsFlexContainerFrame::FlexItem final',
    ],
    'EventStateManager.cpp': [
        'void EventStateManager::ClearFrameRefs(nsIFrame* aFrame)',
        'void EventStateManager::MaybeLeavePendingLink(bool aWasCanceled)',
    ],
    'nsPresContext.cpp': ['void nsPresContext::RegisterManagedPostRefreshObserver('],
    'nsRefreshObservers.cpp': [
        'void ManagedPostRefreshObserver::Cancel()',
        'void ManagedPostRefreshObserver::DidRefresh()',
    ],
    'ImageLoader.cpp': [
        'void ImageLoader::DropRequestsForFrame(nsIFrame* aFrame)',
        'void ImageLoader::RemoveRequestToFrameMapping(',
        'void ImageLoader::UnblockOnloadIfNeeded(FrameWithFlags& aFwf)',
    ],
    'WebRenderUserData.cpp': [
        'void DestroyWebRenderUserDataTable(WebRenderUserDataTable* aTable)',
        'void WebRenderUserData::RemoveFromTable()',
        'WebRenderImageData::~WebRenderImageData()',
        'WebRenderCanvasData::~WebRenderCanvasData()',
        'WebRenderFallbackData::~WebRenderFallbackData()',
    ],
    'RestyleManager.h': ['void NotifyDestroyingFrame(nsIFrame* aFrame)'],
    'SVGObserverUtils.cpp': [
        'void SVGObserverUtils::InvalidateDirectRenderingObservers(\n    Element* aElement, InvalidationFlags aFlags)',
        'void SVGObserverUtils::InvalidateDirectRenderingObservers(\n    nsIFrame* aFrame, InvalidationFlags aFlags)',
        'void SVGRenderingObserverSet::InvalidateAll(bool aFrameInReflow)',
        'void SVGRenderingObserver::NotifyEvictedFromRenderingObserverSet()',
        'void SVGRenderingObserver::StopObserving()',
        'void SVGRenderingObserver::OnNonDOMMutationRenderingChange()',
        'void SVGIDRenderingObserver::OnRenderingChange()',
        'void SVGRenderingObserverProperty::OnRenderingChange()',
        'void SVGTextPathObserver::OnRenderingChange()',
        'void SVGMarkerObserver::OnRenderingChange()',
        'void SVGPaintingProperty::OnRenderingChange()',
        'void SVGTemplateElementObserver::OnRenderingChange()',
    ],
}

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
    return result

if __name__ == '__main__':
    print(json.dumps(bindings(), indent=2))
