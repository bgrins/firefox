
int main(){
  std::cout<<std::setprecision(17);
  std::string kind;
  while(std::cin>>kind){
    trace.clear();nsIFrame frame;imgDrawingParams img;DrawTarget target;
    if(kind=="callee"){
      int ref,empty,alloc,valid,snapshot,mode,type,linear,children,output,initial;double alpha,opacity;
      std::cin>>ref>>empty>>alloc>>valid>>snapshot>>mode>>type>>linear>>children>>output>>initial>>alpha>>opacity;
      SVGMaskFrame mask;mask.env={bool(ref),bool(empty),bool(alloc),bool(valid),bool(snapshot),bool(linear),StyleMaskType(type),alpha,children};
      Kid kid;if(children)mask.mFrames.push_back(&kid);
      Matrix userSpace;
      SVGMaskFrame::MaskParams params(&target,&frame,userSpace,opacity,StyleMaskMode(mode),img);
      bool flag=initial;
#if CANDIDATE
      auto surface=mask.GetMaskForMaskedFrame(params,output?&flag:nullptr);
#else
      auto surface=mask.GetMaskForMaskedFrame(params);
#endif
      std::cout<<(surface?1:0)<<' '<<flag<<' '<<(surface?surface->alpha:-1);
    }else{
      int n;std::cin>>n;std::vector<std::unique_ptr<SVGMaskFrame>> owned;nsTArray<SVGMaskFrame*> masks;ComputedStyle style;Builder builder;Kid kid;
      double initial;std::cin>>initial>>target.rect.x>>target.rect.y>>target.transform.x>>target.transform.y;target.alpha=initial;
      for(int i=0;i<n;i++){
        int ref,empty,alloc,valid,snapshot,mode,type,linear,children,op;double alpha;
        std::cin>>ref>>empty>>alloc>>valid>>snapshot>>mode>>type>>linear>>children>>op>>alpha;
        auto mask=std::make_unique<SVGMaskFrame>();mask->env={bool(ref),bool(empty),bool(alloc),bool(valid),bool(snapshot),bool(linear),StyleMaskType(type),alpha,children};
        if(children)mask->mFrames.push_back(&kid);
        masks.push_back(mask.get());owned.push_back(std::move(mask));Layer layer;layer.mComposite=StyleMaskComposite(op);layer.mMaskMode=StyleMaskMode(mode);style.reset.mMask.mLayers.push_back(layer);
      }
      PaintFramesParams params{&frame,img,{}, {},&builder};
      auto complete=PaintMaskSurface(params,&target,1.,&style,masks,{});
      std::cout<<complete<<' '<<target.alpha<<' '<<target.transform.x<<' '<<target.transform.y;
    }
    std::cout<<'|';for(auto& event:trace)std::cout<<event<<';';std::cout<<'\n';
  }
}
