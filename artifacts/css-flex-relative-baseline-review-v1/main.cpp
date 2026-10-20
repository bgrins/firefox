#include "generated.hpp"
int main(){
 int helperRows=0,fallbackRows=0,helperWrong=0,fallbackWrong=0,providerWrong=0;
 const nsSize container{160,180};
 for(int wm=0;wm<3;++wm)for(bool present:{false,true})for(int delta:{-10,0,10})for(int origin:{-15,0,19}){
  WritingMode mode{wm};
  nsPoint normal{origin+23,origin+29},current=normal;
  if(wm==0)current.y+=delta;else current.x+=(wm==2?-delta:delta);
  FlexItem item{{current,normal,present,{{40,50}},mode}};
  const nscoord normalB=wm==0?normal.y:wm==1?normal.x:container.width-40-normal.x;
  const nscoord currentB=wm==0?current.y:wm==1?current.x:container.width-40-current.x;
  const nscoord expectedB=present?normalB:currentB;
  bool found=!present;auto actualPoint=item.frame.GetNormalPosition(&found);
  auto expectedPoint=present?normal:current;
  if(found!=present||actualPoint.x!=expectedPoint.x||actualPoint.y!=expectedPoint.y)++providerWrong;
  if(item.frame.GetLogicalNormalPosition(mode,container).B(mode)!=expectedB)++providerWrong;
  const nscoord size=item.frame.BSize(mode),c=wm==0?container.height:container.width;
  const auto actual=fallback(item,mode,container);
  if(actual.mAscent!=expectedB+13)++fallbackWrong;
  if(actual.mAscentForLast!=c-expectedB-size+7)++fallbackWrong;
  fallbackRows+=2;
#if HAS_HELPER
  FlexLine line;line.mItems.push_back(item);FlexboxAxisTracker axis{mode};
  auto first=line.NaturalBaselineBOffset(axis,BaselineSharingGroup::First,container);
  auto last=line.NaturalBaselineBOffset(axis,BaselineSharingGroup::Last,container);
  if(!first||*first!=expectedB+13)++helperWrong;
  if(!last||*last!=c-expectedB-size+7)++helperWrong;
  helperRows+=2;
#endif
  assert(item.frame.current.x==current.x&&item.frame.current.y==current.y);
 }
 std::cout<<"{\"helperRows\":"<<helperRows<<",\"fallbackRows\":"<<fallbackRows<<",\"helperWrong\":"<<helperWrong<<",\"fallbackWrong\":"<<fallbackWrong<<",\"providerWrong\":"<<providerWrong<<"}\n";
}
