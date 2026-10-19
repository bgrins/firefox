int main(){
  std::cout<<std::setprecision(17);
  int id,mode,count,selected,mask,custom,dirty,selectedOp,envBits,extraFlags;
  while(std::cin>>id>>mode>>count>>selected>>mask>>custom>>dirty>>selectedOp>>envBits>>extraFlags){
    trace.clear();
    env.theme=envBits&1;env.themeSupports=envBits&2;env.canvas=envBits&4;
    env.images=envBits&8;env.color=envBits&16;env.chrome=envBits&32;
    env.content=envBits&64;env.paginated=envBits&128;env.transformed=envBits&256;
    env.page=envBits&512;env.slice=envBits&1024;
    DrawTarget target;double opacity;
    std::cin>>target.alpha>>opacity>>target.rect.x>>target.rect.y>>target.rect.width>>target.rect.height;
    for(double& v:target.transform.data)std::cin>>v;
    nsStyleImageLayers layers;layers.mImageCount=count;
    for(int i=0;i<std::max(count,1);++i){
      nsStyleImageLayers::Layer layer;layer.mImage.id=i;
      int prep,draw,op,maskMode,layerDirty,repeatX,repeatY,fixed,blend,clipKind;
      std::cin>>prep>>draw>>layer.mImage.alpha>>layer.mSize.width>>layer.mSize.height
        >>layer.mPosition.x>>layer.mPosition.y>>op>>maskMode>>layerDirty>>repeatX>>repeatY>>fixed
        >>layer.clip.x>>layer.clip.y>>layer.clip.width>>layer.clip.height>>blend>>clipKind;
      layer.mImage.prepare=ImgDrawResult(prep);layer.mImage.draw=ImgDrawResult(draw);
      layer.mComposite=StyleMaskComposite(op);layer.mMaskMode=StyleMaskMode(maskMode);
      layer.dirty=layerDirty;layer.mRepeat.mXRepeat=StyleImageLayerRepeat(repeatX);
      layer.mRepeat.mYRepeat=StyleImageLayerRepeat(repeatY);layer.mAttachment=StyleImageLayerAttachment(fixed);
      layer.mBlendMode=CompositionOp(blend);layer.mClip=StyleBackgroundClip(clipKind<0?(i%3)+1:clipKind);
      layers.mLayers.push_back(layer);
    }
    assert(std::cin.good());
    nsIFrame frame;nsPresContext context;context.shell.root=&frame;
    ComputedStyle style;style.reset.mMask=layers;style.background.mImage=layers;
    nsStyleBorder border;
    gfxContext drawing(&target);
    nsRect borderArea{0,0,40,40},dirtyArea{0,0,dirty?40:0,40},customArea{0,0,40,40};
    uint32_t flags=extraFlags|(mask?nsCSSRendering::PAINTBG_MASK_IMAGE:0);
    auto params=selected<0?nsCSSRendering::PaintBGParams::ForAllLayers(context,dirtyArea,borderArea,&frame,flags,opacity)
      :nsCSSRendering::PaintBGParams::ForSingleLayer(context,dirtyArea,borderArea,&frame,flags,selected,CompositionOp(selectedOp),opacity);
    params.bgClipRect=custom?&customArea:nullptr;
    ImgDrawResult result=ImgDrawResult::SUCCESS;
    std::string preparation="null";
    if(mode){
      bool transformed=false;
      auto state=nsCSSRendering::PrepareImageLayer(&context,&frame,flags,borderArea,layers.mLayers[0].clip,layers.mLayers[0],&transformed);
      result=state.mImageRenderer.PrepareResult();
      std::ostringstream values;
      values<<"["<<state.mImageRenderer.IsReady()<<","<<transformed<<","<<rectText(state.mDestArea)<<","<<rectText(state.mFillArea)
        <<","<<state.mAnchor.x<<","<<state.mAnchor.y<<","<<state.mRepeatSize.width<<","<<state.mRepeatSize.height<<"]";
      preparation=values.str();
    }else{
      result=nsCSSRendering::PaintStyleImageLayerWithSC(params,drawing,&style,border);
    }
    std::cout<<"{\"id\":"<<id<<",\"alpha\":"<<target.alpha<<",\"result\":"<<int(result)<<",\"op\":"<<int(drawing.op)<<",\"matrix\":[";
    for(int i=0;i<6;++i){if(i)std::cout<<",";std::cout<<target.transform.data[i];}
    std::cout<<"],\"preparation\":"<<preparation<<",\"trace\":[";
    for(size_t i=0;i<trace.size();++i){if(i)std::cout<<",";std::cout<<"\""<<trace[i]<<"\"";}
    std::cout<<"]}\n";
  }
}
