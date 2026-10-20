from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parent

def block(text, anchor):
    if text.count(anchor)!=1: raise ValueError((anchor,text.count(anchor)))
    start=text.index(anchor); opening=text.index('{',start)
    depth=0; i=opening; state='code'
    while i<len(text):
        c=text[i]; pair=text[i:i+2]
        if state=='line':
            if c=='\n': state='code'
        elif state=='comment':
            if pair=='*/': state='code';i+=1
        elif state in ['"',"'"]:
            if c=='\\': i+=1
            elif c==state: state='code'
        elif pair=='//':state='line';i+=1
        elif pair=='/*':state='comment';i+=1
        elif c in ['"',"'"]:state=c
        elif c=='{':depth+=1
        elif c=='}':
            depth-=1
            if depth==0:return start,text[start:i+1]
        i+=1
    raise ValueError('unterminated '+anchor)

def selected(variant='combined-after'):
    if variant not in ('combined-before','combined-after','standalone-before','standalone-after'): raise ValueError('variant')
    stem='inputs/evidence/css-sticky-writing-mode-fix-v1/matrix-combined-v1-sources/'
    sticky='inputs/'+variant+'.cpp'
    header='inputs/'+('before-StickyScrollContainer.h' if variant.endswith('before') else 'combined-final-StickyScrollContainer.h')
    wm=stem+'layout__generic__WritingModes.h'
    records=[]
    def take(name,path,anchor):
        text=(ROOT/path).read_text();start,body=block(text,anchor)
        records.append(dict(name=name,path=path,start_byte=len(text[:start].encode()),body=body,sha256=hashlib.sha256(body.encode()).hexdigest()))
    for name,anchor in [
        ('nearest_scroll','static ScrollContainerFrame* GetScrollContainerForStickyFrame('),
        ('get_container','StickyScrollContainer* StickyScrollContainer::GetForFrame('),
        ('side_offset','static nscoord ComputeStickySideOffset('),
        ('scroll_size','static nsSize GetScrollContainerSize('),
        ('compute_offsets','void StickyScrollContainer::ComputeStickyOffsets('),
        ('limits','StickyScrollContainer::StickyLimits StickyScrollContainer::ComputeStickyLimits('),
        ('position','nsPoint StickyScrollContainer::ComputePosition('),
        ('ignoring','nsPoint StickyScrollContainer::ComputePositionIgnoringScrolling('),
        ('do_position','nsPoint StickyScrollContainer::DoComputePosition('),
        ('translation','nsPoint StickyScrollContainer::ComputeTranslationIgnoringScrolling('),
        ('stuck_y','bool StickyScrollContainer::IsStuckInYDirection('),
        ('scroll_ranges','void StickyScrollContainer::GetScrollRanges('),
        ('axis_ranges','StickyScrollContainer::StickyScrollRanges\nStickyScrollContainer::GetStickyScrollRangesForAxis('),
        ('continuations','void StickyScrollContainer::PositionContinuations('),
        ('update','void StickyScrollContainer::UpdatePositions(')]:take(name,sticky,anchor)
    for name,anchor in [('wm_vertical','bool IsVertical() const'),('wm_inline_reverse','bool IsInlineReversed() const'),('wm_rtl','bool IsBidiRTL() const'),('wm_block','static mozilla::Side PhysicalSideForBlockAxis('),('wm_inline','mozilla::Side PhysicalSideForInlineAxis('),('wm_side','mozilla::Side PhysicalSide(LogicalSide')]:take(name,wm,anchor)
    for name,path,anchor in [
        ('provider_mode','providers/servo__components__style__logical_geometry.rs','pub fn new(inheritedbox_style:'),
        ('get_normal','discovery/frame-inlines-upstream.txt','nsPoint nsIFrame::GetNormalPosition('),
        ('get_cb','discovery/frame-upstream.txt','nsIFrame* nsIFrame::GetContainingBlock('),
        ('nearest_block','discovery/frame-upstream.txt','static nsIFrame* GetNearestBlockContainer('),
        ('is_block','discovery/frame-upstream.txt','bool nsIFrame::IsBlockContainer() const'),
        ('union','discovery/layout-utils-upstream.txt','nsRect nsLayoutUtils::GetAllInFlowRectsUnion('),
        ('union_add','discovery/layout-utils-upstream.txt','void nsLayoutUtils::RectAccumulator::AddRect('),
        ('timeline_displacement','providers/dom__animation__ViewTimeline.cpp','Maybe<std::pair<nscoord, ViewTimeline::StickyDisplacement>>\nViewTimeline::ComputeStickyDisplacement('),
        ('displacement_record','discovery/view-timeline-upstream.h','struct StickyDisplacement {'),
        ('timeline_earliest','providers/dom__animation__ViewTimeline.cpp','nscoord ViewTimeline::StickyDisplacement::Earliest('),
        ('timeline_latest','providers/dom__animation__ViewTimeline.cpp','nscoord ViewTimeline::StickyDisplacement::Latest('),
        ('margin_default','providers/gfx__2d__BaseMargin.h','constexpr BaseMargin()'),
        ('margin_constructor','providers/gfx__2d__BaseMargin.h','constexpr BaseMargin(Coord'),
        ('margin_horizontal','providers/gfx__2d__BaseMargin.h','Coord LeftRight() const'),
        ('margin_vertical','providers/gfx__2d__BaseMargin.h','Coord TopBottom() const'),
        ('margin_side','providers/gfx__2d__BaseMargin.h','Coord& Side(SideT'),
        ('margin_const_side','providers/gfx__2d__BaseMargin.h','Coord Side(SideT'),
        ('compute_cb_value','discovery/layout-utils-upstream.h','static nscoord ComputeCBDependentValue(nscoord aPercentBasis,\n                                         const LengthPercentage&'),
        ('union_saturating','discovery/nsrect-upstream.h','[[nodiscard]] nsRect SaturatingUnion(const nsRect&'),
        ('union_saturating_edges','discovery/nsrect-upstream.h','[[nodiscard]] nsRect SaturatingUnionEdges(const nsRect&'),
        ('rect_union_edges','discovery/nsrect-upstream.h','[[nodiscard]] nsRect UnionEdges(const nsRect&'),
        ('rect_union','discovery/nsrect-upstream.h','[[nodiscard]] nsRect Union(const nsRect&'),
        ('rect_union_assign','discovery/nsrect-upstream.h','void UnionRect(const nsRect&'),
        ('rect_deflate','providers/gfx__2d__BaseRect.h','void Deflate(const MarginT&'),
        ('rect_margin','providers/gfx__2d__BaseRect.h','MarginT operator-(const Sub&'),
        ('rect_left','providers/gfx__2d__BaseRect.h','void SetLeftEdge('),
        ('rect_right','providers/gfx__2d__BaseRect.h','void SetRightEdge('),
        ('rect_top','providers/gfx__2d__BaseRect.h','void SetTopEdge('),
        ('rect_bottom','providers/gfx__2d__BaseRect.h','void SetBottomEdge('),
        ('rect_overflows','discovery/nsrect-upstream.cpp','bool nsRect::Overflows() const'),
        ('absolute','discovery/rect-absolute-upstream.h','struct BaseRectAbsolute {')]:take(name,path,anchor)
    take('limits_record',header,'struct StickyLimits {')
    return records
