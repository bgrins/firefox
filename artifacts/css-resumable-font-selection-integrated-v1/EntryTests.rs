struct MetricAction{current:bool}
struct EntryBindings{root:Arc<()>,valid:bool}
impl EntryBindings{fn valid_for(&mut self,_:RuleCascadeFlags)->bool{self.valid}}
struct EntryContext{frames:Vec<()>,metric_references:Option<()>,frame_reply:Option<()>,lookup_reply:Option<(LonghandId,FontSelectionReply)>,lookup_bindings:EntryBindings,computed_context:computed::Context}
impl EntryContext{
 fn new(root:Arc<()>)->Self{Self{frames:vec![()],metric_references:None,frame_reply:None,lookup_reply:None,lookup_bindings:EntryBindings{root,valid:true},computed_context:computed::Context::default()}}
 fn metric_action_is_current(&self,a:&MetricAction,depth:usize)->bool{a.current&&depth==1}
}
#[test]fn actual_authorization_selector_and_lookup_reach_first_attribute_without_prewalk(){
 for body in ["20px","attr(data-size type(<length>),9px)"]{
  PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"attr(data-size type(<length>),1px)")];let decls=declarations(&values,&[2]);let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();tracker.values.insert("data-size".into(),body.into());let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());let mut entry=EntryContext::new(generation.clone());
  let MetricPreparationStep::References(longhand,value)=cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None)else{panic!()};let raw=value.clone();assert!(entry.authorize_metric_substitution(&MetricAction{current:true},longhand,value));let (_,initial)=entry.lookup_reply.take().unwrap();assert!(Arc::ptr_eq(&initial.value,&raw));assert!(Arc::ptr_eq(&initial.generation,&generation));assert!(initial.lookup.is_none());
  let mut inputs=LookupContext::new();inputs.nodes.insert(VarType::Attr("data-size".into(),String::new()),VisitResult::CycleSettled);let mut reply=Some(initial);let mut requests=0;
  loop{match cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,reply.take()){
   MetricPreparationStep::Lookup(_,value,request)=>{assert!(request.guards.iter().any(|g|matches!(g.key,SubstitutionGuardKey::Property(PropertyId::NonCustom(_)))));let result=inputs.owned_lookup_value(&request,&mut tracker).unwrap().unwrap();reply=answer(&value,&request,&generation,result);requests+=1;},
   MetricPreparationStep::Complete=>break,
   _=>panic!("unexpected prewalk or incomplete selector"),
  }}
  assert!(requests>=2);assert_eq!(numeric(&state),if body=="20px"{20.0}else{1.0});assert_eq!(tracker.queries.len(),1);assert_eq!(context.rule_cache_conditions.borrow().marks,0);PARSES.with(|n|assert_eq!(n.get(),1));
 }
}
#[test]fn authorization_rejects_wrong_owner_or_unretired_context(){
 let value=Arc::new(UnparsedValue{variable_value:tokens("20px"),from_shorthand:None});
 for reason in 0..5{let mut c=EntryContext::new(Arc::new(()));match reason{1=>c.metric_references=Some(()),2=>c.frame_reply=Some(()),3=>c.lookup_bindings.valid=false,4=>c.frames.clear(),_=>{}}
 assert!(!c.authorize_metric_substitution(&MetricAction{current:reason!=0},LonghandId::FontSize,value.clone()));assert!(c.lookup_reply.is_none());}
}
