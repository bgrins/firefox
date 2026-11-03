#[test]
fn integrated_size_selector_consumes_owned_attribute_then_next_input_once(){
 PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"attr(data-size type(<length>),9px)"),dynamic(LonghandId::XTextScale,"var(--scale)")];let mut d=size_declarations(&values,&[2,2]);d.longhand_declarations[0].next_index=0;d.prioritary_positions[3].most_important=1;
 let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();tracker.values.insert("data-size".into(),"20px".into());let mut states=size_states(&c,&ctx,&d);let g=Arc::new(());let mut entry=EntryContext::new(g.clone());let mut inputs=LookupContext::new();inputs.nodes.insert(VarType::Attr("data-size".into(),String::new()),VisitResult::CycleSettled);inputs.lookup_bindings.values.insert("scale".into(),Some(ComputedRegisteredValue::universal(Arc::new(tokens("1")))));let mut reply=None;
 loop{match states.poll(&c,&mut ctx,&mut cache,&mut tracker,reply.take()){
  MetricPreparationStep::References(id,value)=>{assert!(entry.authorize_metric_substitution(&MetricAction{current:true},id,value));reply=entry.lookup_reply.take();},
  MetricPreparationStep::Lookup(id,value,request)=>{let value_reply=inputs.owned_lookup_value(&request,&mut tracker).unwrap().unwrap();reply=Some((id,answer(&value,&request,&g,value_reply).unwrap()));},
  MetricPreparationStep::Complete=>break,
  _=>panic!("unexpected integrated selection wait"),
 }}
 assert_eq!(numeric(&states.size),20.0);assert_eq!(numeric(&states.text_scale),1.0);assert_eq!(tracker.queries.len(),1);assert!(states.size.stable_for_appearance_addition());PARSES.with(|n|assert_eq!(n.get(),2));
}
