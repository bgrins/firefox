
nsRect nsLayoutUtils::TransformFrameRectToAncestor(const nsIFrame* frame,const nsRect& r,const nsIFrame* ancestor,bool*,Maybe<Matrix4x4Flagged>* cache) {
 fallbackCalls++;
 Matrix4x4Flagged m;
 if(cache&&*cache){cachedFallbackCalls++;m=cache->value();}
 else m=GetTransformToAncestor(RelativeTo{frame},RelativeTo{ancestor});
 float apd=frame->PresContext()->apd, target=ancestor->PresContext()->apd;
 auto coord=[](double n){return int32_t(std::fmax(nscoord_MIN,std::fmin(nscoord_MAX,std::floor(n+0.5))));};
 return nsRect(coord((float(r.x)/apd*m.sx+m.tx)*target),coord((float(r.y)/apd*m.sy+m.ty)*target),coord(float(r.width)/apd*m.sx*target),coord(float(r.height)/apd*m.sy*target));
}
int main(){
 Context context,other;other.apd=30;
 int rows=0;
 for(int depth : {1,8,128})for(int mode=0;mode<12;mode++)for(int flags : {0,1,2,4}) {
  std::vector<nsIFrame> frames(depth+1);
  for(int i=0;i<=depth;i++){auto&f=frames[i];f.context=&context;if(i<depth)f.parent=&frames[i+1];f.position={i+1,-i};f.ignoredPosition={i+11,3-i};}
  nsIFrame* leaf=&frames[0];nsIFrame* root=&frames[depth];
  int selected=depth==1?0:depth-1;
  if(mode==1||mode==2){auto&f=frames[mode==1?0:selected];f.transformed=true;f.transform.sx=2;f.transform.sy=3;f.transform.tx=4;f.transform.ty=-5;f.transform.trace="X";}
  if(mode==3)frames[selected].svgText=true;
  if(mode==4)frames[selected].states=NS_FRAME_SVG_LAYOUT;
  if(mode==5)frames[selected].context=&other;
  if(mode==6){frames[selected].crossParent=frames[selected].parent;frames[selected].parent=nullptr;frames[selected].crossOffset={4,8};}
  if(mode==7){frames[selected].zoomed=true;}
  if(mode==8){frames[selected].stacking=true;}
  if(mode==9){frames[selected].displayPort=true;}
  if(mode==10){frames[0].combines=true;}
  if(mode==11){root->transformed=true;root->transform.tx=700;root->transform.trace="TARGET";}
  RelativeTo target{root,mode==7?ViewportType::Visual:ViewportType::Layout};
  nsIFrame* stop=nullptr;matrixCalls=0;
#if CANDIDATE
  Maybe<nsPoint> exact=Some(nsPoint(123,456));
  auto m=nsLayoutUtils::GetTransformToAncestor(RelativeTo{leaf},target,TransformMatrixFlags{unsigned(flags)},&stop,&exact);
  if(flags||mode==1||mode==2||mode==3||mode==4||mode==5||mode==6||mode==7)require(!exact,100+mode);
  else {require(bool(exact),200+mode);require(exact->x==depth*(depth+1)/2 && exact->y==-depth*(depth-1)/2,220+mode);}
#else
  auto m=nsLayoutUtils::GetTransformToAncestor(RelativeTo{leaf},target,TransformMatrixFlags{unsigned(flags)},&stop);
#endif
  printf("ROW %d %d %d %.9g %.9g %.9g %.9g %s %d %td\n",depth,mode,flags,m.sx,m.sy,m.tx,m.ty,m.trace.c_str(),matrixCalls,stop?stop-frames.data():-1);
  rows++;
 }
#if CANDIDATE
 nsIFrame root,mid,leaf;root.context=mid.context=leaf.context=&context;mid.parent=&root;leaf.parent=&mid;
 mid.position={700,1100};leaf.position={-8383188,-1100};
 matrixCalls=fallbackCalls=cachedFallbackCalls=0;
 auto r=TransformClientRectToAncestor(&leaf,nsRect(0,0,8388488,600),&root);
 require(r.x==-8382488 && r.y==0 && int64_t(r.x)+r.width==6000 && !fallbackCalls && matrixCalls==1,301);
 for(int boundary=0;boundary<7;boundary++){
  mid.transformed=boundary==0;mid.svgText=boundary==1;mid.states=boundary==2?NS_FRAME_SVG_LAYOUT:0;
  mid.context=boundary==3?&other:&context;
  nsRect box=boundary==4?nsRect(nscoord_MAX,0,1,1):nsRect(0,0,8388488,600);
  if(boundary==5)box=nsRect(0,0,nscoord_MAX+1,1);
  if(boundary==6)box=nsRect(0,0,-1,1);
  if(boundary==4){leaf.position={0,0};mid.position={0,0};}
  matrixCalls=fallbackCalls=cachedFallbackCalls=0;
  (void)TransformClientRectToAncestor(&leaf,box,&root);
  require(fallbackCalls==1,310+boundary);
  require(cachedFallbackCalls==(boundary<5?1:0),320+boundary);
  require(matrixCalls==(boundary==0?2:1),330+boundary);
 }
 matrixCalls=fallbackCalls=0;
 r=TransformClientRectToAncestor(&root,nsRect(-8382488,0,8388488,1),&root);
 require(r.x==-8382488 && int64_t(r.x)+r.width==6000 && !fallbackCalls && matrixCalls==0,339);
 leaf.parent=&root;leaf.position={0,0};
 Maybe<nsPoint> exact=Some(nsPoint(5,6));
 (void)nsLayoutUtils::GetTransformToAncestor(RelativeTo{&root},RelativeTo{&root},{},nullptr,&exact);require(!exact,340);
 nsIFrame* stop=nullptr;exact=Some(nsPoint(5,6));
 (void)root.GetTransformMatrix(ViewportType::Layout,RelativeTo{nullptr},&stop,{},&exact);require(!exact,341);
 leaf.position={nscoord_MAX+100,0};mid.position={-nscoord_MAX-100,0};leaf.parent=&mid;mid.parent=&root;mid.context=&context;
 matrixCalls=fallbackCalls=0;r=TransformClientRectToAncestor(&leaf,nsRect(0,0,1,1),&root);require(r.x==0 && !fallbackCalls,342);
 puts("EXACT_CHECKS_PASS");
#endif
 printf("ROWS %d\n",rows);
}
