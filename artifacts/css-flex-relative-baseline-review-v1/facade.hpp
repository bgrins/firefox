#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <optional>
#include <vector>
using nscoord=int32_t;
template<class T> using Maybe=std::optional<T>;
template<class T> Maybe<T> Some(T x){return x;}
static auto Nothing(){return std::nullopt;}
enum class BaselineSharingGroup{First,Last};
enum class BaselineExportContext{Other};
struct nsPoint{nscoord x,y;};
struct nsSize{nscoord width,height;nsSize operator-(nsSize b)const{return {width-b.width,height-b.height};}};
struct Rect{nsSize size;nsSize Size()const{return size;}};
namespace mozilla {
struct WritingMode{int mode;bool IsOrthogonalTo(WritingMode b)const{return (mode==0)!=(b.mode==0);}};
struct LogicalPoint{
 nscoord b;
 LogicalPoint(WritingMode w,nsPoint p,nsSize inner):b(w.mode==0?p.y:w.mode==1?p.x:inner.width-p.x){}
 nscoord B(WritingMode)const{return b;}
};
}
using WritingMode=mozilla::WritingMode;
struct LogicalSize{
 WritingMode wm;nsSize s;
 LogicalSize(WritingMode w,nsSize z):wm(w),s(z){}
 nscoord BSize(WritingMode w)const{return w.mode==0?s.height:s.width;}
 nsSize GetPhysicalSize(WritingMode)const{return s;}
};
struct nsIFrame{
 nsPoint current,normal;bool hasNormal;Rect mRect;WritingMode wm;
 static int NormalPositionProperty(){return 1;}
 nsPoint GetProperty(int key,bool* has)const{assert(key==1);*has=hasNormal;return hasNormal?normal:nsPoint{0,0};}
 nsPoint GetPosition()const{return current;}
 nsPoint GetNormalPosition(bool* aHasProperty=nullptr)const;
 mozilla::LogicalPoint GetLogicalNormalPosition(WritingMode,const nsSize&)const;
 mozilla::LogicalPoint GetLogicalPosition(WritingMode w,const nsSize& c)const{return {w,current,c-mRect.Size()};}
 nscoord BSize(WritingMode w)const{return w.mode==0?mRect.size.height:mRect.size.width;}
 Maybe<nscoord> GetNaturalBaselineBOffset(WritingMode w,BaselineSharingGroup g,BaselineExportContext e)const{
  assert(!w.IsOrthogonalTo(wm)&&e==BaselineExportContext::Other);return g==BaselineSharingGroup::First?13:7;
 }
};
struct FlexboxAxisTracker{WritingMode wm;WritingMode GetWritingMode()const{return wm;}};
struct FlexItem{
 nsIFrame frame;
 bool IsStrut()const{return false;}
 WritingMode GetWritingMode()const{return frame.wm;}
 const nsIFrame* Frame()const{return &frame;}
 nscoord ResolvedAscent(bool first)const{return first?13:frame.BSize(frame.wm)-7;}
};
template<class T>struct nsTArray:std::vector<T>{using std::vector<T>::vector;size_t Length()const{return this->size();}};
struct Result{nscoord mAscent=0,mAscentForLast=0;};
