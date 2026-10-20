import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('use python3 -I -S without optimization')
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

SPECS = {'nsFlexContainerFrame.current.cpp': ['class nsFlexContainerFrame::CachedFlexItemData', 'void nsFlexContainerFrame::MarkCachedFlexMeasurementsDirty(', 'const CachedBAxisMeasurement& nsFlexContainerFrame::MeasureBSizeForFlexItem(', 'nscoord nsFlexContainerFrame::MeasureFlexItemContentBSize(', 'Maybe<nscoord> FlexItem::MeasuredBSize()', 'bool FlexItem::NeedsFinalReflow(', 'void nsFlexContainerFrame::SizeItemInCrossAxis(', 'nsReflowStatus nsFlexContainerFrame::ReflowFlexItem(', 'void SetCrossSize(nscoord aCrossSize)', 'void SetAscent(nscoord aAscent) const'], 'FrameProperties.h': ['inline uint64_t FrameProperties::GetInternal(', 'inline void FrameProperties::SetInternal(', 'inline void FrameProperties::AddInternal(', 'inline uint64_t FrameProperties::TakeInternal(', 'inline bool FrameProperties::RemoveInternal(', 'void RemoveAll(const nsIFrame* aFrame)'], 'nsContainerFrame.frozen.cpp': ['void nsContainerFrame::ReflowChild(\n', 'void nsContainerFrame::FinishReflowChild(\n', 'void nsContainerFrame::DeleteNextInFlowChild('], 'nsIFrame.frozen.cpp': ['void nsIFrame::DidReflow(', 'void nsIFrame::MarkIntrinsicISizesDirty()', 'void nsIFrame::Destroy(DestroyContext& aContext)'], 'PresShell.cpp': ['void PresShell::NotifyDestroyingFrame(', 'nsresult PresShell::PostReflowCallback(', 'void PresShell::HandlePostedReflowCallbacks(', 'void PresShell::DidDoReflow(', 'bool PresShell::DoReflow(', 'bool PresShell::IsSafeToFlush()', 'bool PresShell::ProcessReflowCommands(', 'void PresShell::PostPendingScrollResnap(', 'void PresShell::PostPendingScrollAnchorAdjustment('], 'SVGObserverUtils.cpp': ['void SVGRenderingObserverSet::InvalidateAll(bool aFrameInReflow)', 'void SVGObserverUtils::InvalidateDirectRenderingObservers(\n    Element*', 'void SVGObserverUtils::InvalidateDirectRenderingObservers(\n    nsIFrame*', 'class SVGTextPathObserver final', 'void SVGTextPathObserver::OnRenderingChange()', 'class SVGMozElementObserver final', 'class BackgroundClipRenderingObserver :', 'void BackgroundClipRenderingObserver::OnRenderingChange()', 'void SVGPaintingProperty::OnRenderingChange()'], 'SVGObserverUtils.h': ['virtual bool ObservesReflow() const'], 'nsTableCellFrame.cpp': ['void nsTableCellFrame::NotifyPercentBSize('], 'ScrollContainerFrame.indexed.cpp': ['void ScrollContainerFrame::DidReflow(', 'void ScrollContainerFrame::PostPendingResnap()'], 'nsTableFrame.cpp': ['void nsTableFrame::RequestSpecialBSizeReflow(']}

def bindings():
    rows = []
    for filename, anchors in SPECS.items():
        text = (ROOT / 'source' / filename).read_text()
        for anchor in anchors:
            start, end, body = selected(text, anchor)
            rows.append(dict(file='source/' + filename, anchor=anchor,
                start_utf8=len(text[:start].encode()), end_utf8=len(text[:end].encode()),
                sha256=hashlib.sha256(body.encode()).hexdigest(), text=body))
    return rows

if __name__ == '__main__':
    print(json.dumps(bindings(), indent=2))
