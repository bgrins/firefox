#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <optional>
#include <sstream>
#include <string>
#include <vector>
#include <cmath>
#define MOZ_ASSERT(...) assert((__VA_ARGS__,true))
#undef MOZ_ASSERT
#define MOZ_ASSERT(x,...) assert(x)
#define NS_ASSERTION(x,...) assert(x)
#define MOZ_ASSERT_UNREACHABLE(...) ((void)0)
#define MOZ_ALWAYS_INLINE inline
#define MOZ_UNLIKELY(x) (x)
using nscoord=int32_t;
constexpr nscoord nscoord_MAX=(1<<30)-1;
constexpr nscoord nscoord_MIN=-nscoord_MAX;
constexpr nscoord NS_AUTOOFFSET=nscoord_MAX;
constexpr nscoord NS_UNCONSTRAINEDSIZE=nscoord_MAX;
constexpr uint32_t SKIP_SCROLLED_FRAME=1;
std::vector<int> providerTrace;
namespace mozilla {
template<class T> struct CheckedInt {
 int64_t value; CheckedInt(T x):value(x){}
 CheckedInt& operator+=(T x){value+=int64_t(x);return *this;}
 bool isValid()const{return value>=std::numeric_limits<T>::min()&&value<=std::numeric_limits<T>::max();}
};
enum Side {eSideTop,eSideRight,eSideBottom,eSideLeft};
enum class LogicalSide {BStart,BEnd,IStart,IEnd};
enum class LogicalEdge {Start,End};
bool IsBlock(LogicalSide s){return s==LogicalSide::BStart||s==LogicalSide::BEnd;}
LogicalEdge GetEdge(LogicalSide s){return s==LogicalSide::BStart||s==LogicalSide::IStart?LogicalEdge::Start:LogicalEdge::End;}
struct StyleWritingMode {
 uint8_t _0=0;
 constexpr explicit operator bool()const{return _0!=0;}
 friend constexpr StyleWritingMode operator&(StyleWritingMode a,StyleWritingMode b){return {uint8_t(a._0&b._0)};}
 static const StyleWritingMode VERTICAL,VERTICAL_LR,INLINE_REVERSED,LINE_INVERTED,RTL;
};
inline constexpr StyleWritingMode StyleWritingMode::VERTICAL{1};
inline constexpr StyleWritingMode StyleWritingMode::INLINE_REVERSED{2};
inline constexpr StyleWritingMode StyleWritingMode::VERTICAL_LR{4};
inline constexpr StyleWritingMode StyleWritingMode::LINE_INVERTED{8};
inline constexpr StyleWritingMode StyleWritingMode::RTL{16};
constexpr uint8_t kWritingModeSidewaysMask=4;
struct WritingMode {
 StyleWritingMode mWritingMode;
 explicit WritingMode(uint8_t raw=0):mWritingMode{raw}{}
 bool IsBidiLTR()const{return !IsBidiRTL();}
 @@WM_METHODS@@
};
template<class T> struct Maybe:std::optional<T>{using std::optional<T>::optional; bool isSome()const{return this->has_value();}};
namespace layers {enum class ScrollDirection {eHorizontal,eVertical};}
class ScrollContainerFrame;
class StickyScrollContainer;
}
using namespace mozilla;
struct nsPoint {
 nscoord x=0,y=0;
 nsPoint()=default;nsPoint(nscoord a,nscoord b):x(a),y(b){}
 friend nsPoint operator+(nsPoint a,nsPoint b){return {a.x+b.x,a.y+b.y};}
 friend nsPoint operator-(nsPoint a,nsPoint b){return {a.x-b.x,a.y-b.y};}
};
struct nsSize {nscoord width=0,height=0;};
template<class Coord> struct BaseMargin {
 using SideT=mozilla::Side;
 Coord top,right,bottom,left;
 @@MARGIN_METHODS@@
};
struct nsMargin:BaseMargin<nscoord> {
 using BaseMargin::BaseMargin;
 bool operator==(const nsMargin& b)const{return top==b.top&&right==b.right&&bottom==b.bottom&&left==b.left;}
};
struct nsRect {
 using T=nscoord;using MarginT=nsMargin;using Sub=nsRect;
 nscoord x=0,y=0,width=0,height=0;
 nsRect()=default;nsRect(nscoord a,nscoord b,nscoord c,nscoord d):x(a),y(b),width(c),height(d){}
 nscoord X()const{return x;}nscoord Y()const{return y;}
 nscoord Width()const{return width;}nscoord Height()const{return height;}
 nscoord XMost()const{return x+width;}nscoord YMost()const{return y+height;}
 nsPoint TopLeft()const{return {x,y};}
 void MoveBy(nsPoint p){x+=p.x;y+=p.y;}
 bool IsEmpty()const{return width<=0||height<=0;}
 bool Overflows()const;
 @@RECT_METHODS@@
};
@@RECT_OVERFLOW@@
@@ABSOLUTE@@
struct nsRectAbsolute:BaseRectAbsolute<nscoord,nsRectAbsolute,nsPoint,nsRect>{using BaseRectAbsolute::BaseRectAbsolute;};
struct nsStyleDisplay{};
enum class StyleDirection {Ltr,Rtl};
struct nsStyleVisibility {StyleDirection mDirection=StyleDirection::Ltr;};
enum class PseudoStyleType {Normal,MozScrolledContent};
struct FakeStyle {PseudoStyleType type=PseudoStyleType::Normal;PseudoStyleType GetPseudoType()const{return type;}};
struct LengthPercentage {
 nscoord value;
 bool HasPercent()const{return false;}
 nscoord Resolve(nscoord)const{providerTrace.push_back(950);return value;}
};
struct ResolvedSide {
 bool automatic=true;nscoord length=0;
 bool IsAuto()const{return automatic;}
 LengthPercentage AsLengthPercentage()const{return {length};}
};
struct AnchorPosOffsetResolutionParams {
 struct Params {void* frame;int property;};
 static int UseCBFrameSize(Params){return 0;}
};
struct StylePositionProperty {static constexpr int Sticky=1;};
struct nsStylePosition {
 ResolvedSide sides[4];
 const ResolvedSide* GetAnchorResolvedInset(Side s,int)const{providerTrace.push_back(100+int(s));return &sides[s];}
};
struct nsIFrame {
 int id=0;
 nsIFrame* parent=nullptr;nsIFrame* continuation=nullptr;nsIFrame* first=nullptr;
 ScrollContainerFrame* nearestScroll=nullptr;
 bool rowGroup=false,lineParticipant=false,blockWrapper=false,tableRow=false,absolute=false,sticky=true;
 nsPoint position,normal,offsetToScroll,transform;
 bool hasNormal=true,hasComputed=true;
 nsMargin offsets,padding,border;
 nsRect borderBox,marginBox,contentBox,overflow;
 WritingMode mWritingMode;
 nsStyleDisplay display;nsStyleVisibility visibility;FakeStyle style;nsStylePosition stylePosition;
 const nsStyleVisibility* StyleVisibility()const{return &visibility;}
 nsIFrame* GetParent()const{return parent;}
 bool IsLineParticipant()const{return lineParticipant;}bool IsBlockWrapper()const{return blockWrapper;}bool IsTableRowFrame()const{return tableRow;}
 bool IsBlockContainer()const;
 bool IsAbsolutelyPositioned(const nsStyleDisplay*)const{return absolute;}
 const nsStyleDisplay* StyleDisplay()const{return &display;}
 const FakeStyle* Style()const{return &style;}
 nsIFrame* GetContainingBlock(uint32_t,const nsStyleDisplay*)const;
 nsIFrame* GetContainingBlock()const{providerTrace.push_back(200+id);return GetContainingBlock(0,StyleDisplay());}
 bool IsTableRowGroupFrame()const{return rowGroup;}
 WritingMode GetWritingMode()const{providerTrace.push_back(300+id);return mWritingMode;}
 bool IsStickyPositioned()const{return sticky;}
 nsPoint GetPosition()const{return position;}
 nsPoint GetNormalPosition(bool* has=nullptr)const;
 static int ComputedOffsetProperty(){return 0;}
 static int NormalPositionProperty(){return 1;}
 const nsMargin* GetProperty(int)const{providerTrace.push_back(400+id);return hasComputed?&offsets:nullptr;}
 nsPoint GetProperty(int,bool* has)const{*has=hasNormal;return normal;}
 void SetOrUpdateDeletableProperty(int,nsMargin v){providerTrace.push_back(500+id);hasComputed=true;offsets=v;}
 void SetPosition(nsPoint p){providerTrace.push_back(600+id);auto d=p-position;borderBox.MoveBy(d);marginBox.MoveBy(d);contentBox.MoveBy(d);position=p;}
 nsMargin GetUsedPadding()const{return padding;}nsMargin GetUsedBorder()const{return border;}
 nsRect ScrollableOverflowRectRelativeToSelf()const{return overflow;}
 nsPoint GetOffsetTo(nsIFrame*)const{return offsetToScroll;}
 const nsStylePosition* StylePosition()const{return &stylePosition;}
};
namespace mozilla {
struct FakePresContext {bool cross=false;bool IsRootContentDocumentCrossProcess()const{return cross;}};
struct FakePresShell {nsSize fixedSize;nsSize GetFixedViewportSize()const{return fixedSize;}};
class ScrollContainerFrame {
 public:
 nsIFrame* scrolled=nullptr;StickyScrollContainer* stickyContainer=nullptr;nsSize size;bool root=false;
 FakePresContext context;FakePresShell shell;
 nsIFrame* GetScrolledFrame()const{return scrolled;}
 nsSize GetScrolledFrameSize()const{providerTrace.push_back(700);return size;}
 bool IsRootScrollFrameOfDocument()const{return root;}
 const FakePresContext* PresContext()const{return &context;}
 const FakePresShell* PresShell()const{return &shell;}
 StickyScrollContainer* GetStickyContainer()const{return stickyContainer;}
};
struct OverflowChangedTracker {
 static constexpr int CHILDREN_CHANGED=1;
 void SetSubtreeRoot(nsIFrame*){providerTrace.push_back(800);}
 void AddFrame(nsIFrame* frame,int){providerTrace.push_back(810+frame->id);}
 void Flush(){providerTrace.push_back(899);}
};
struct DepthOrderedFrameList {
 std::vector<nsIFrame*> frames;
 const std::vector<nsIFrame*>& IterFromShallowest()const{return frames;}
};
class StickyScrollContainer {
 public:
 enum class StickyLimitSpace:uint8_t {RelativeToCurrentScroll,IgnoreCurrentScroll};
 struct StickyLimits {nsRect mStick,mContain;};
 struct StickyScrollRange {nscoord mScrollPosition=0,mMaxOffset=0;};
 struct StickyScrollRanges {Maybe<StickyScrollRange> mStartSide,mEndSide;};
 ScrollContainerFrame* mScrollContainerFrame;nsPoint mScrollPosition;DepthOrderedFrameList mFrames;
 explicit StickyScrollContainer(ScrollContainerFrame* s):mScrollContainerFrame(s){}
 ScrollContainerFrame* ScrollContainer()const{return mScrollContainerFrame;}
 static StickyScrollContainer* GetForFrame(const nsIFrame*);
 static void ComputeStickyOffsets(nsIFrame*);
 StickyLimits ComputeStickyLimits(nsIFrame*,StickyLimitSpace=StickyLimitSpace::RelativeToCurrentScroll)const;
 nsPoint ComputePosition(nsIFrame*)const;nsPoint ComputePositionIgnoringScrolling(nsIFrame*)const;
 nsPoint DoComputePosition(nsIFrame*,StickyLimitSpace)const;
 nsPoint ComputeTranslationIgnoringScrolling(const nsIFrame*)const;
 bool IsStuckInYDirection(nsIFrame*)const;
 void GetScrollRanges(nsIFrame*,nsRectAbsolute*,nsRectAbsolute*)const;
 StickyScrollRanges GetStickyScrollRangesForAxis(const nsIFrame*,layers::ScrollDirection)const;
 void PositionContinuations(nsIFrame*);void UpdatePositions(nsPoint,nsIFrame*);
};
}
namespace nsLayoutUtils {
constexpr int SCROLLABLE_SAME_DOC=1,SCROLLABLE_STOP_AT_PAGE=2,SCROLLABLE_INCLUDE_HIDDEN=4;
namespace GetAllInFlowRectsFlag {constexpr int UseContentBox=1,UseMarginBoxWithAutoResolvedAsZero=2;}
using GetAllInFlowRectsFlags=int;
bool IsFirstContinuationOrIBSplitSibling(nsIFrame* f){return !f->first||f->first==f;}
bool IsProperAncestorFrame(nsIFrame* a,nsIFrame* f){while(f){if(f==a)return true;f=f->parent;}return false;}
nsIFrame* FirstContinuationOrIBSplitSibling(const nsIFrame* f){return f->first?f->first:const_cast<nsIFrame*>(f);}
nsIFrame* GetNextContinuationOrIBSplitSibling(nsIFrame* f){return f->continuation;}
ScrollContainerFrame* GetNearestScrollContainerFrame(nsIFrame* f,int flags){providerTrace.push_back(900+flags);return f?f->nearestScroll:nullptr;}
@@CB_VALUE@@
void TransformRect(nsIFrame* frame,nsIFrame*,nsRect& r){providerTrace.push_back(1000+frame->id);r.MoveBy(frame->transform);}
struct RectAccumulator {
 nsRect mResultRect,mFirstRect;bool mSeenFirstRect=false;
 void AddRect(const nsRect&);
};
void GetAllInFlowRects(nsIFrame* f,const nsIFrame*,RectAccumulator* cb,int flags){
 providerTrace.push_back(1100+10*f->id+flags);
 for(auto* c=f;c;c=c->continuation)cb->AddRect(flags==1?c->contentBox:flags==2?c->marginBox:c->borderBox);
}
nsRect GetAllInFlowRectsUnion(nsIFrame*,const nsIFrame*,GetAllInFlowRectsFlags=0);
}
@@FRAME_METHODS@@
@@UNION_METHODS@@
namespace mozilla {
static constexpr nscoord gUnboundedNegative=nscoord_MIN/2;
static constexpr nscoord gUnboundedExtent=nscoord_MAX;
static constexpr nscoord gUnboundedPositive=gUnboundedNegative+gUnboundedExtent;
@@STICKY_METHODS@@
}

namespace mozilla::dom {
inline std::nullopt_t Nothing(){return std::nullopt;}
template<class T> Maybe<T> Some(T x){return Maybe<T>{x};}
struct ViewTimeline {
 @@DISPLACEMENT_RECORD@@;
 static Maybe<std::pair<nscoord,StickyDisplacement>> ComputeStickyDisplacement(const nsIFrame*,const ScrollContainerFrame*,layers::ScrollDirection);
};
@@TIMELINE_METHODS@@
}
