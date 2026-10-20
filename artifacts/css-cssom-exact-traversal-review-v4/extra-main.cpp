int main() {
 Context context;
 int rows=0;
 for(unsigned flags=0;flags<8;flags++)for(int view=0;view<3;view++)for(int transformed=0;transformed<2;transformed++) {
  nsIFrame root,mid,leaf;
  root.context=mid.context=leaf.context=&context;leaf.parent=&mid;mid.parent=&root;
  leaf.position={13,-7};mid.position={19,23};leaf.ignoredPosition={101,103};mid.ignoredPosition={107,109};
  mid.transformed=transformed;mid.stacking=true;mid.displayPort=true;
  mid.transform.sx=2;mid.transform.sy=3;mid.transform.tx=11;mid.transform.ty=-17;mid.transform.trace="X";
  RelativeTo from{&leaf,view==2?ViewportType::Visual:ViewportType::Layout};
  RelativeTo to{&root,view?ViewportType::Visual:ViewportType::Layout};
  Maybe<AppUnitTranslation> exact=Some(AppUnitTranslation{7,8});nsIFrame* stop=nullptr;
  matrixCalls=0;auto m=nsLayoutUtils::GetTransformToAncestor(from,to,TransformMatrixFlags{flags},&stop,&exact);
  require(bool(exact)==(!flags&&!view&&!transformed),600);
  if(exact)require(exact->x==32&&exact->y==16,601);
  int calls=matrixCalls;matrixCalls=0;nsIFrame* other=nullptr;
  auto n=nsLayoutUtils::GetTransformToAncestor(from,to,TransformMatrixFlags{flags},&other);
  require(m.sx==n.sx&&m.sy==n.sy&&m.tx==n.tx&&m.ty==n.ty&&m.trace==n.trace&&stop==other&&calls==matrixCalls,602);
  printf("DISPATCH %u %d %d %.9g %.9g %.9g %.9g %s %d %d\n",flags,view,transformed,m.sx,m.sy,m.tx,m.ty,m.trace.c_str(),calls,stop==&root);
  rows++;
 }
 for(unsigned bits : {0u,1u,2u,3u,8u,9u,10u,11u})for(int atLeaf=0;atLeaf<2;atLeaf++) {
  nsIFrame root,mid,leaf;root.context=mid.context=leaf.context=&context;leaf.parent=&mid;mid.parent=&root;
  (atLeaf?leaf:mid).states=bits;
  Maybe<AppUnitTranslation> exact;nsIFrame* stop=nullptr;
  nsLayoutUtils::GetTransformToAncestor(RelativeTo{&leaf},RelativeTo{&root},{},&stop,&exact);
  require(bool(exact)==!(bits&(NS_FRAME_IS_SVG_TEXT|NS_FRAME_SVG_LAYOUT)),603);
 }
 nsIFrame root,a,b,leaf;for(auto*f:{&root,&a,&b,&leaf})f->context=&context;
 leaf.parent=&a;a.parent=&b;b.parent=&root;
 auto check=[&](nsRect box,int x,int y,int id){fallbackCalls=0;auto r=TransformClientRectToAncestor(&leaf,box,&root);require(r.x==x&&r.y==y&&!fallbackCalls,id);};
 leaf.position={-2000000000,-2000000000};a.position={1400000000,1400000000};b.position={1400000000,1400000000};
 check(nsRect(0,0,1,1),800000000,800000000,604);
 leaf.position={-1500000000,-1500000000};a.position={-1000000000,-1000000000};b.position={0,0};
 check(nsRect(2000000000,2000000000,1,1),-500000000,-500000000,605);
 leaf.position={1500000000,1500000000};a.position={-2000000000,-2000000000};
 nsRect expanded(1000000000,1000000000,1,1);require(!GetUntransformedRectToAncestor(&leaf,expanded,&root),606);
 check(expanded,500000000,500000000,607);
 leaf.position={6000,6000};a.position={0,0};
 fallbackCalls=cachedFallbackCalls=matrixCalls=0;
 (void)TransformClientRectToAncestor(&leaf,nsRect(0,nscoord_MAX,1,1),&root);
 require(fallbackCalls==1&&cachedFallbackCalls==1&&matrixCalls==1,608);

 {
  nsIFrame root,mid,leaf;root.context=mid.context=leaf.context=&context;
  leaf.parent=&mid;mid.parent=&root;leaf.position={13,-7};mid.position={19,23};
  leaf.ignoredPosition={101,103};mid.ignoredPosition={107,109};
  nsIFrame* stop=nullptr;matrixCalls=0;
  auto ignored=nsLayoutUtils::GetTransformToAncestor(RelativeTo{&leaf},RelativeTo{&root},TransformMatrixFlags{1},&stop);
  require(ignored.tx==float(208)/60&&ignored.ty==float(212)/60&&stop==&root&&matrixCalls==1,620);
  mid.stacking=true;matrixCalls=0;
  auto stopped=nsLayoutUtils::GetTransformToAncestor(RelativeTo{&leaf},RelativeTo{&root},TransformMatrixFlags{4},&stop);
  require(stopped.tx==float(13)/60&&stopped.ty==float(-7)/60&&stop==&mid&&matrixCalls==1,621);
  mid.stacking=false;mid.zoomed=true;matrixCalls=0;
  auto visual=nsLayoutUtils::GetTransformToAncestor(RelativeTo{&leaf},RelativeTo{&root,ViewportType::Visual},{},&stop);
  require(visual.sx==2&&visual.sy==2&&stop==&root&&matrixCalls==2,622);
  matrixCalls=0;
  auto layout=nsLayoutUtils::GetTransformToAncestor(RelativeTo{&leaf},RelativeTo{&root},{},&stop);
  require(layout.sx==1&&layout.sy==1&&layout.tx==float(32)/60&&layout.ty==float(16)/60&&stop==&root&&matrixCalls==1,623);
  printf("NULL_BOUNDARIES_PASS %.9g %.9g %.9g %.9g\n",ignored.tx,stopped.tx,visual.tx,layout.tx);
 }
 const int64_t values[]={INT64_MIN,INT64_MIN+1,-4294967295LL,-1,0,1,4294967295LL,INT64_MAX-1,INT64_MAX};
 int arithmetic=0;
 for(int64_t x:values)for(int64_t y:values){
  int64_t output=123;
  bool success=SafeAdd(x,y,&output);
  auto old=CheckedInt<int64_t>(x)+CheckedInt<int64_t>(y);
  require(success==old.isValid(),609);
  if(success)require(output==old.value(),610);
  arithmetic++;
 }
 printf("INDEPENDENT_PASS dispatch=%d masks=16 geometry=4 arithmetic=%d\n",rows,arithmetic);
}
