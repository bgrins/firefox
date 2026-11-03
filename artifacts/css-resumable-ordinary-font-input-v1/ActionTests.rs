#![allow(dead_code)]
use std::collections::HashSet;
#[derive(Clone,Copy,Debug,Eq,PartialEq,Hash)]
enum LonghandId { FontSynthesisWeight, FontSynthesisStyle, FontSynthesisSmallCaps, FontSynthesisPosition, FontKerning, FontOpticalSizing, FontVariantLigatures, FontFeatureSettings }
#[derive(Default)]struct LonghandIdSet(HashSet<LonghandId>);
impl LonghandIdSet { fn contains(&self,id:LonghandId)->bool {self.0.contains(&id)} fn insert(&mut self,id:LonghandId){self.0.insert(id);} }
#[derive(Clone,Copy,Debug,PartialEq)] enum FontTarget { OrdinaryFontInput(LonghandId) }
#[derive(Debug,PartialEq)] enum MetricActionProgress { Unsupported, AlreadyComplete, Invalidated, References(LonghandId,()), Lookup(LonghandId,(),()), Published(FontTarget) }
#[derive(Clone,Copy)]enum MetricPreparationStep { References(LonghandId,()), Lookup(LonghandId,(),()), Prerequisites(()), Invalidated, Complete }
struct MetricPreparation { longhand:LonghandId }
struct FontSelectionReply;
struct AttributeTracker;
struct NativeContext;
struct Declarations;
struct Cache;
#[derive(Default)]struct PriorityCompletion {complete:()}
#[derive(Default)]struct Cascade {begins:usize,resumes:usize,applies:usize,stage:usize,reject_publish_once:bool}
impl Cascade {
 fn begin_font_preparation(&mut self,_:&mut NativeContext,_:&Declarations,id:LonghandId)->MetricPreparation {self.begins+=1;MetricPreparation{longhand:id}}
 fn resume_metric_preparation(&mut self,_:&mut NativeContext,_:&mut Cache,_:&mut AttributeTracker,s:&mut MetricPreparation,_:&(),reply:Option<FontSelectionReply>)->MetricPreparationStep {
  self.resumes+=1;
  match self.stage {1=>{self.stage=2;MetricPreparationStep::References(s.longhand,())},2=>{assert!(reply.is_some());self.stage=3;MetricPreparationStep::Lookup(s.longhand,(),())},3=>{assert!(reply.is_some());self.stage=0;MetricPreparationStep::Complete},_=>MetricPreparationStep::Complete}
 }
 fn publish_prepared_metric(&mut self,_:&mut NativeContext,_:&mut Cache,_:&mut AttributeTracker,s:MetricPreparation,_:&())->Result<(),MetricPreparation> {
  if self.reject_publish_once {self.reject_publish_once=false;return Err(s)}
  self.applies+=1;Ok(())
 }
}
struct Context<'a> {completed_font_inputs:LonghandIdSet,metric_action:Option<()>,font_preparation:Option<MetricPreparation>,cascade:&'a mut Cascade,computed_context:&'a mut NativeContext,decls:&'a Declarations,cache:&'a mut Cache,priority_completion:PriorityCompletion}
// EXACT-PREDICATE
impl Context<'_> {
// EXACT-ACTION
}
fn with_context(f:impl FnOnce(&mut Context)) {
 let mut cascade=Cascade::default();let mut native=NativeContext;let decls=Declarations;let mut cache=Cache;
 let mut c=Context{completed_font_inputs:LonghandIdSet::default(),metric_action:Some(()),font_preparation:None,cascade:&mut cascade,computed_context:&mut native,decls:&decls,cache:&mut cache,priority_completion:PriorityCompletion::default()};f(&mut c);
}
#[test]fn seven_inputs_publish_once_and_reuse_completion() {
 for id in [LonghandId::FontSynthesisWeight,LonghandId::FontSynthesisStyle,LonghandId::FontSynthesisSmallCaps,LonghandId::FontSynthesisPosition,LonghandId::FontKerning,LonghandId::FontOpticalSizing,LonghandId::FontVariantLigatures] {
  with_context(|c|{let mut tracker=AttributeTracker;
   assert_eq!(c.perform_font_input_action(id,&mut tracker,None),MetricActionProgress::Published(FontTarget::OrdinaryFontInput(id)));
   assert!(c.completed_font_inputs.contains(id));assert!(c.metric_action.is_none());assert!(c.font_preparation.is_none());
   c.metric_action=Some(());assert_eq!(c.perform_font_input_action(id,&mut tracker,None),MetricActionProgress::AlreadyComplete);
   assert_eq!((c.cascade.begins,c.cascade.resumes,c.cascade.applies),(1,1,1));assert!(c.metric_action.is_none());
  });
 }
}
#[test]fn suspended_selector_and_exact_reply_are_retained() {
 with_context(|c|{let mut tracker=AttributeTracker;let id=LonghandId::FontKerning;c.cascade.stage=1;
  assert_eq!(c.perform_font_input_action(id,&mut tracker,None),MetricActionProgress::References(id,()));
  assert!(c.metric_action.is_some());assert!(c.font_preparation.is_some());assert!(!c.completed_font_inputs.contains(id));assert_eq!(c.cascade.applies,0);
  assert_eq!(c.perform_font_input_action(id,&mut tracker,Some((LonghandId::FontOpticalSizing,FontSelectionReply))),MetricActionProgress::Invalidated);
  assert_eq!(c.cascade.resumes,1);
  assert_eq!(c.perform_font_input_action(id,&mut tracker,Some((id,FontSelectionReply))),MetricActionProgress::Lookup(id,(),()));
  assert!(!c.completed_font_inputs.contains(id));assert_eq!(c.cascade.applies,0);
  assert_eq!(c.perform_font_input_action(id,&mut tracker,Some((id,FontSelectionReply))),MetricActionProgress::Published(FontTarget::OrdinaryFontInput(id)));
  assert_eq!((c.cascade.begins,c.cascade.resumes,c.cascade.applies),(1,3,1));
 });
}
#[test]fn wrong_target_does_not_steal_retained_selector() {
 with_context(|c|{let mut tracker=AttributeTracker;c.cascade.stage=1;let id=LonghandId::FontOpticalSizing;
  c.perform_font_input_action(id,&mut tracker,None);
  assert_eq!(c.perform_font_input_action(LonghandId::FontKerning,&mut tracker,None),MetricActionProgress::Invalidated);
  assert_eq!(c.font_preparation.as_ref().unwrap().longhand,id);assert_eq!(c.cascade.resumes,1);assert_eq!(c.cascade.applies,0);
 });
}
#[test]fn rejected_publication_keeps_state_without_completion() {
 with_context(|c|{let mut tracker=AttributeTracker;let id=LonghandId::FontVariantLigatures;c.cascade.reject_publish_once=true;
  assert_eq!(c.perform_font_input_action(id,&mut tracker,None),MetricActionProgress::Invalidated);
  assert!(c.font_preparation.is_some());assert!(!c.completed_font_inputs.contains(id));assert!(c.metric_action.is_some());assert_eq!(c.cascade.applies,0);
  assert_eq!(c.perform_font_input_action(id,&mut tracker,None),MetricActionProgress::Published(FontTarget::OrdinaryFontInput(id)));
  assert_eq!(c.cascade.begins,1);assert_eq!(c.cascade.applies,1);
 });
}
#[test]fn unaudited_input_is_not_falsely_completed() {
 with_context(|c|{let mut tracker=AttributeTracker;let id=LonghandId::FontFeatureSettings;
  assert_eq!(c.perform_font_input_action(id,&mut tracker,None),MetricActionProgress::Unsupported);
  assert!(!c.completed_font_inputs.contains(id));assert_eq!((c.cascade.begins,c.cascade.resumes,c.cascade.applies),(0,0,0));
 });
}
