static void printFrames(const nsTArray<Keyframe>& frames){
 std::cout<<"[";bool first=true;for(const auto&f:frames){if(!first)std::cout<<",";first=false;
 std::cout<<"{\"offset\":";if(f.mOffset)std::cout<<"["<<int(f.mOffset->mRangeName)<<","<<numeric(f.mOffset->mPercentage)<<"]";else std::cout<<"null";
 std::cout<<",\"offsetNegativeZero\":"<<(f.mOffset && f.mOffset->mPercentage==0 && std::signbit(f.mOffset->mPercentage)?"true":"false")<<",\"computedNegativeZero\":"<<(f.mComputedOffset==0 && std::signbit(f.mComputedOffset)?"true":"false")<<",\"computed\":"<<numeric(f.mComputedOffset)<<",\"easing\":"<<(f.mTimingFunction?f.mTimingFunction->value:-1)<<",\"composite\":"<<int(f.mComposite)<<",\"properties\":[";
 bool fp=true;for(const auto&p:f.mPropertyValues){if(!fp)std::cout<<",";fp=false;std::cout<<"["<<int(p.mProperty.mId)<<","<<quoted(p.mProperty.mCustomName)<<","<<(p.mServoDeclarationBlock?p.mServoDeclarationBlock->allocation:-1)<<","<<(p.mServoDeclarationBlock?numeric(p.mServoDeclarationBlock->value):"null")<<"]";}std::cout<<"]}";
 }std::cout<<"]";
}
static void printProperties(const nsTArray<AnimationProperty>&properties){
 std::cout<<"[";bool fp=true;for(const auto&p:properties){if(!fp)std::cout<<",";fp=false;std::cout<<"["<<int(p.mProperty.mId)<<","<<quoted(p.mProperty.mCustomName)<<","<<(p.mIsRunningOnCompositor?"true":"false")<<",[";
 bool fs=true;for(const auto&s:p.mSegments){if(!fs)std::cout<<",";fs=false;std::cout<<"["<<numeric(s.mFromKey)<<","<<numeric(s.mToKey)<<","<<(s.mFromValue.value?numeric(*s.mFromValue.value):"null")<<","<<(s.mToValue.value?numeric(*s.mToValue.value):"null")<<","<<(s.mTimingFunction?s.mTimingFunction->value:-1)<<","<<int(s.mFromComposite)<<","<<int(s.mToComposite)<<"]";}std::cout<<"]]";
 }std::cout<<"]";
}
static void printGetter(const nsTArray<JSObject*>& objects){
 std::cout<<"[";bool first=true;for(const auto*o:objects){if(!first)std::cout<<",";first=false;const auto&d=o->dictionary;
 std::cout<<"{\"offset\":";if(!d.mOffset.value)std::cout<<"null";else if(!d.mOffset.value->ranged)std::cout<<numeric(d.mOffset.value->percentage);else std::cout<<"["<<quoted(*d.mOffset.value->range.mRangeName)<<","<<numeric(*d.mOffset.value->range.mOffset)<<"]";
 std::cout<<",\"offsetNegativeZero\":"<<(d.mOffset.value && !d.mOffset.value->ranged && d.mOffset.value->percentage==0 && std::signbit(d.mOffset.value->percentage)?"true":"false")<<",\"computedNegativeZero\":"<<(*d.mComputedOffset==0 && std::signbit(*d.mComputedOffset)?"true":"false")<<",\"computed\":"<<numeric(*d.mComputedOffset)<<",\"easing\":"<<quoted(d.mEasing)<<",\"composite\":"<<int(d.mComposite)<<",\"properties\":[";bool f=true;for(const auto&[k,v]:o->properties){if(!f)std::cout<<",";f=false;std::cout<<"["<<quoted(k)<<","<<quoted(v)<<"]";}std::cout<<"]}";
 }std::cout<<"]";
}
int main(){
 ProviderDocument doc;Element target;ComputedStyle style;AnimationTimeline timeline;Animation animation;KeyframeEffect effect;JSContext cx;
 std::map<int,std::unique_ptr<StyleLockedDeclarationBlock>> declarations;
 std::string op;int step=0;
 while(std::cin>>op){
  trace.clear();failure=0;ErrorResult rv;nsTArray<JSObject*> getter;
  if(op=="RESET"){
   int targetOn,styleOn,animOn,relevant,view,resolved,composite,failValues;double start,delta,first,last,base,scale;
   std::cin>>targetOn>>styleOn>>animOn>>relevant>>view>>resolved>>start>>delta>>first>>last>>composite>>base>>scale>>failValues;
   effect=KeyframeEffect();declarations.clear();objectArena.clear();style={base,scale,bool(failValues)};timeline.view=view;timeline.geometry={bool(resolved),start,delta};animation.relevant=relevant;animation.timeline=view<0?nullptr:&timeline;timeline.view=view>0;animation.range={first,last};effect.mDocument=&doc;effect.mTarget.mElement=targetOn?&target:nullptr;effect.providerStyle=styleOn?&style:nullptr;effect.mAnimation=animOn?&animation:nullptr;effect.mEffectOptions.mComposite=CompositeOperation(composite);
  } else if(op=="SET"){
   JSObject input;int error,n;std::cin>>error>>n;input.processingError=error;
   for(int i=0;i<n;i++){Keyframe k;int kind,easing,composite,np;double percent,computed;std::cin>>kind>>percent>>computed>>easing>>composite>>np;if(kind>=0)k.mOffset.emplace(Keyframe::OffsetType{StyleTimelineRangeName(kind),percent});k.mComputedOffset=computed;if(easing>=0)k.mTimingFunction.emplace(StyleComputedTimingFunction{easing});k.mComposite=CompositeOperationOrAuto(composite);
    for(int j=0;j<np;j++){int id,allocation;std::string name;double value;std::cin>>id>>name>>allocation>>value;CSSPropertyId prop{NonCustomCSSPropertyId(id)};if(name!="-")prop.mCustomName=name;PropertyValuePair p(prop);
     if(allocation>=0){auto it=declarations.find(allocation);if(it==declarations.end())declarations[allocation]=std::make_unique<StyleLockedDeclarationBlock>(StyleLockedDeclarationBlock{allocation,value});else assert(it->second->value==value);p.mServoDeclarationBlock=declarations[allocation].get();}k.mPropertyValues.AppendElement(p);
    }input.input.AppendElement(k);
   }effect.SetKeyframes(&cx,&input,rv);
  } else if(op=="DEFAULT"){int v;std::cin>>v;effect.SetComposite(CompositeOperation(v));
  } else if(op=="GET"){std::cin>>failure;effect.GetKeyframes(&cx,getter,rv);
  } else if(op=="CONTEXT"){
   int view,resolved;std::cin>>view>>resolved>>timeline.geometry.start>>timeline.geometry.delta>>animation.range.first>>animation.range.second;
   timeline.view=view>0;timeline.geometry.resolved=resolved;animation.timeline=view<0?nullptr:&timeline;
   effect.GetKeyframes(&cx,getter,rv);
  } else if(op=="INVALIDATE"){
   int targetOn,styleOn;std::cin>>style.base>>style.scale>>targetOn>>styleOn;effect.mTarget.mElement=targetOn?&target:nullptr;effect.providerStyle=styleOn?&style:nullptr;
  } else if(op=="STYLE"){
   std::cin>>style.base>>style.scale;effect.UpdateProperties(&style,animation.timeline);
  } else if(op=="RUNNING"){
   for(auto&p:effect.mProperties)p.mIsRunningOnCompositor=true;
  } else if(op=="COST"){
   int repetitions,changed;std::cin>>repetitions>>changed;JSObject input;input.input=effect.mKeyframes.Clone();uint64_t checksum=0;
   auto before=std::chrono::steady_clock::now();
   for(int i=0;i<repetitions;i++){
    trace.clear();if(changed && !input.input.IsEmpty())input.input.LastElement().mComposite=CompositeOperationOrAuto(i%2);
    ErrorResult error;effect.SetKeyframes(&cx,&input,error);assert(!error.Failed());
    checksum+=effect.mKeyframes.Length()+effect.mProperties.Length()+trace.size();
    if(!effect.mKeyframes.IsEmpty())checksum+=int(effect.mKeyframes.LastElement().mComposite);
   }
   auto elapsed=std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-before).count();
   std::cout<<"{\"costNs\":"<<elapsed<<",\"repetitions\":"<<repetitions<<",\"changed\":"<<changed<<",\"checksum\":"<<checksum<<",\"frames\":"<<effect.mKeyframes.Length()<<"}\n";continue;
  } else {std::cerr<<"unknown "<<op;return 2;}
  std::cout<<"{\"step\":"<<step++<<",\"op\":"<<quoted(op)<<",\"error\":"<<rv.code<<",\"frames\":";printFrames(effect.mKeyframes);
  std::cout<<",\"range\":"<<int(effect.mKeyframeOffsetsHasRangeOffset)<<",\"default\":"<<int(effect.mEffectOptions.mComposite)<<",\"properties\":";printProperties(effect.mProperties);
  std::cout<<",\"base\":[";bool fb=true;for(const auto&[k,v]:effect.mBaseValues.values){if(!fb)std::cout<<",";fb=false;std::cout<<"["<<int(k.mId)<<","<<quoted(k.mCustomName)<<","<<numeric(v)<<"]";}std::cout<<"],\"cumulative\":"<<effect.mCumulativeChanges<<",\"getter\":";printGetter(getter);
  std::cout<<",\"trace\":[";bool ft=true;for(const auto&t:trace){if(!ft)std::cout<<",";ft=false;std::cout<<quoted(t);}std::cout<<"]}\n";
 }
}
