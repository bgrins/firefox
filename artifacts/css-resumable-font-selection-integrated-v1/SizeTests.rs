fn size_states<'a,'b>(cascade:&Cascade,context:&computed::Context,decls:&'a Declarations<'b>)->ComputedSizePreparation<'a,'b>{ComputedSizePreparation{index:7,family:None,size:cascade.begin_font_preparation(context,decls,LonghandId::FontSize),text_scale:cascade.begin_font_preparation(context,decls,LonghandId::XTextScale)}}
fn size_declarations<'a>(values:&'a[PropertyDeclaration],levels:&[u8])->Declarations<'a>{let mut d=declarations(values,levels);d.prioritary_positions[3].most_important=DeclarationIndex::MAX;d}
#[test]
fn size_action_retains_real_selection_pending_and_routes_reply_once(){
 PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"var(--size, 30px)")];let d=size_declarations(&values,&[2]);let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);let generation=Arc::new(());
 let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),&generation);
 let(v,q)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))));
 for _ in 0..3{let(_,again)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,answer(&v,&q,&generation,SubstitutionLookupValue::Pending).unwrap()))));assert!(Arc::ptr_eq(&again.identity,&q.identity));}
 assert!(states.size.prepared.is_empty());assert!(!states.text_scale.complete);PARSES.with(|n|assert_eq!(n.get(),0));assert_eq!(ctx.rule_cache_conditions.borrow().marks,0);
 let r=answer(&v,&q,&generation,SubstitutionLookupValue::Value(tokens("20px"),false)).unwrap();assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))),MetricPreparationStep::Complete));assert_eq!(numeric(&states.size),20.0);assert!(states.text_scale.prepared.is_empty());assert!(states.text_scale.complete);PARSES.with(|n|assert_eq!(n.get(),1));
 assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Complete));PARSES.with(|n|assert_eq!(n.get(),1));
 ctx.included_cascade_flags=RuleCascadeFlags::APPEARANCE_BASE;assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Invalidated));
}
#[test]
fn size_action_keeps_rollback_and_rejects_reply_for_other_input(){
 let values=[dynamic(LonghandId::FontSize,"var(--rollback)"),PropertyDeclaration::Number(LonghandId::FontSize,20.0)];let d=size_declarations(&values,&[2,1]);let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);let g=Arc::new(());let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),&g);
 assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::XTextScale,r))),MetricPreparationStep::Invalidated));
 let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),&g);let(v,q)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))));let r=answer(&v,&q,&g,SubstitutionLookupValue::Value(tokens("revert-layer"),false)).unwrap();assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))),MetricPreparationStep::Complete));assert_eq!(states.size.prepared.len(),2);assert_eq!(numeric(&states.size),20.0);
}
#[test]
fn size_selection_checks_hidden_appearance_entries_before_any_substitution(){
 let values=[dynamic(LonghandId::FontSize,"var(--rollback)"),PropertyDeclaration::Number(LonghandId::FontSize,20.0)];let mut d=size_declarations(&values,&[2,1]);assert!(computed_size_selection_flags_stable(&d,PrioritaryPropertyId::FontSize));d.longhand_declarations[1].priority.flags=RuleCascadeFlags::APPEARANCE_BASE;assert!(!computed_size_selection_flags_stable(&d,PrioritaryPropertyId::FontSize));assert!(computed_size_selection_flags_stable(&d,PrioritaryPropertyId::XTextScale));
}
#[test]
fn size_selection_retains_inherit_and_absence_without_synthetic_numeric_value(){
 for absent in [false,true]{let values=[PropertyDeclaration::Wide(LonghandId::FontSize,CSSWideKeyword::Inherit)];let mut d=size_declarations(&values,&[2]);if absent{d.prioritary_positions[0].most_important=DeclarationIndex::MAX;}let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Complete));assert_eq!(states.size.prepared.len(),if absent{0}else{1});if !absent{assert!(matches!(states.size.prepared[0].declaration,PropertyDeclaration::Wide(_,CSSWideKeyword::Inherit)));}}
}
#[test]
fn size_action_routes_second_input_after_first_parse_without_repeating_it(){
 PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"var(--size)"),dynamic(LonghandId::XTextScale,"var(--scale)")];let mut d=size_declarations(&values,&[2,2]);d.longhand_declarations[0].next_index=0;d.prioritary_positions[3].most_important=1;let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);let g=Arc::new(());
 let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),&g);let(v,q)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))));let r=answer(&v,&q,&g,SubstitutionLookupValue::Value(tokens("20px"),false)).unwrap();let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))),&g);PARSES.with(|n|assert_eq!(n.get(),1));
 let(v,q)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::XTextScale,r))));assert_eq!(q.name,"scale");let r=answer(&v,&q,&g,SubstitutionLookupValue::Value(tokens("1"),false)).unwrap();assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::XTextScale,r))),MetricPreparationStep::Complete));assert_eq!(numeric(&states.size),20.0);assert_eq!(numeric(&states.text_scale),1.0);PARSES.with(|n|assert_eq!(n.get(),2));
}
#[test]
fn optional_keyword_family_resumes_after_size_and_scale_without_reparsing(){
 PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"var(--size)"),dynamic(LonghandId::FontFamily,"var(--family)")];let mut d=size_declarations(&values,&[2,2]);d.longhand_declarations[0].next_index=0;d.prioritary_positions[4].most_important=1;let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);let g=Arc::new(());
 let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),&g);let(v,q)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))));let r=answer(&v,&q,&g,SubstitutionLookupValue::Value(tokens("20px"),false)).unwrap();assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))),MetricPreparationStep::Complete));assert!(states.operation().is_some());
 states.family=Some(c.begin_font_preparation(&ctx,&d,LonghandId::FontFamily));let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),&g);let(v,q)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontFamily,r))));assert_eq!(q.name,"family");
 let(_,again)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontFamily,answer(&v,&q,&g,SubstitutionLookupValue::Pending).unwrap()))));assert!(Arc::ptr_eq(&q.identity,&again.identity));PARSES.with(|n|assert_eq!(n.get(),1));
 let r=answer(&v,&q,&g,SubstitutionLookupValue::Value(tokens("1"),false)).unwrap();assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontFamily,r))),MetricPreparationStep::Complete));assert_eq!(numeric(&states.size),20.0);assert_eq!(numeric(states.family.as_ref().unwrap()),1.0);PARSES.with(|n|assert_eq!(n.get(),2));
}
#[test]
fn reverted_to_absence_retains_rollback_without_misclassifying_it_as_font_size(){
 let values=[PropertyDeclaration::Wide(LonghandId::FontSize,CSSWideKeyword::RevertLayer)];let d=size_declarations(&values,&[2]);let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Complete));assert!(states.operation().is_none());assert_eq!(states.size.prepared.len(),1);
}

#[test]
fn unvisited_lower_appearance_does_not_block_selected_winner(){
 let values=[PropertyDeclaration::Number(LonghandId::FontSize,20.0),PropertyDeclaration::Number(LonghandId::FontSize,40.0)];let mut d=size_declarations(&values,&[2,1]);d.longhand_declarations[1].priority.flags=RuleCascadeFlags::APPEARANCE_BASE;let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Complete));assert_eq!(numeric(&states.size),20.0);assert!(states.size.stable_for_appearance_addition());
}
#[test]
fn skipped_higher_appearance_blocks_publication_even_with_numeric_winner(){
 let values=[PropertyDeclaration::Number(LonghandId::FontSize,40.0),PropertyDeclaration::Number(LonghandId::FontSize,20.0)];let mut d=size_declarations(&values,&[2,1]);d.longhand_declarations[0].priority.flags=RuleCascadeFlags::APPEARANCE_BASE;let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Complete));assert_eq!(numeric(&states.size),20.0);assert!(!states.size.stable_for_appearance_addition());
}
#[test]
fn rollback_reached_appearance_is_part_of_publication_prefix(){
 let values=[PropertyDeclaration::Wide(LonghandId::FontSize,CSSWideKeyword::RevertLayer),PropertyDeclaration::Number(LonghandId::FontSize,40.0),PropertyDeclaration::Number(LonghandId::FontSize,20.0)];let mut d=size_declarations(&values,&[3,2,1]);d.longhand_declarations[1].priority.flags=RuleCascadeFlags::APPEARANCE_BASE;let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Complete));assert_eq!(numeric(&states.size),20.0);assert!(!states.size.stable_for_appearance_addition());
}
#[test]
fn native_unit_readset_does_not_wait_on_unread_child_orientation(){
 use specified::length::LengthUnit::*;
 for root in [false,true]{for unit in [Px,In,Cm,Mm,Q,Pt,Pc,Em,Ex,Cap,Ic,Rem,Rex,Rcap,Ric,Vw,Vh,Vmin,Vmax,Cqw,Cqh]{assert!(!size_length_reads_writing_mode(unit,root),"{unit:?} {root}");}}
 for unit in [Ch,Lh,Vi,Vb,Svi,Svb,Lvi,Lvb,Dvi,Dvb,Cqi,Cqb,Cqmin,Cqmax]{assert!(size_length_reads_writing_mode(unit,false),"{unit:?}");}
 for unit in [Rch,Rlh]{assert!(!size_length_reads_writing_mode(unit,false));assert!(size_length_reads_writing_mode(unit,true));}
}
