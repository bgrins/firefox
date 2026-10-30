use std::borrow::Cow;
use std::cell::Cell;
use std::collections::{HashMap, HashSet};
use std::sync::Arc;

type DeclarationIndex = u16;
type LonghandId = PrioritaryPropertyId;
#[derive(Clone, Copy, Debug, Eq, PartialEq, Hash)]
pub enum PrioritaryPropertyId { FontWeight, FontWidth, FontStyle, FontSizeAdjust, Direction, WritingMode, TextOrientation, Appearance, FontSize, LineHeight, ColorScheme, FontSynthesisWeight, FontSynthesisStyle, FontSynthesisSmallCaps, FontSynthesisPosition, FontFeatureSettings }
#[derive(Clone, Copy, Default)]
struct PrioritaryPropertyIdSet(u16);
impl PrioritaryPropertyIdSet {
    fn contains(&self, id: PrioritaryPropertyId) -> bool { self.0 & (1 << id as u8) != 0 }
    fn insert(&mut self, id: PrioritaryPropertyId) { self.0 |= 1 << id as u8; }
    fn remove(&mut self, id: PrioritaryPropertyId) { self.0 &= !(1 << id as u8); }
    fn iter(&self) -> impl Iterator<Item=PrioritaryPropertyId> { let ids=[PrioritaryPropertyId::FontWeight,PrioritaryPropertyId::FontWidth,PrioritaryPropertyId::FontStyle,PrioritaryPropertyId::FontSizeAdjust,PrioritaryPropertyId::Direction,PrioritaryPropertyId::WritingMode,PrioritaryPropertyId::TextOrientation,PrioritaryPropertyId::Appearance,PrioritaryPropertyId::FontSize,PrioritaryPropertyId::LineHeight,PrioritaryPropertyId::ColorScheme]; let bits=self.0; ids.into_iter().filter(move |id|bits & (1 << *id as u8)!=0) }
    fn contains_all(&self, other: &Self) -> bool { self.0 & other.0 == other.0 }
}
impl PrioritaryPropertyId {
    fn to_longhand(self) -> Self { self }
    fn from_longhand(id:LonghandId)->Option<Self>{if (id as u8)<11{Some(id)}else{None}}
    fn name(self)->&'static str{match self {Self::FontSynthesisWeight=>"font-synthesis-weight",Self::FontSynthesisStyle=>"font-synthesis-style",Self::FontSynthesisSmallCaps=>"font-synthesis-small-caps",Self::FontSynthesisPosition=>"font-synthesis-position",Self::FontFeatureSettings=>"font-feature-settings",_=>"font-weight"}}

    fn is_logical(self) -> bool {false}
    fn dependencies(self) -> &'static PrioritaryPropertyIdSet {
        static APPEARANCE: PrioritaryPropertyIdSet = PrioritaryPropertyIdSet(1 << 7);
        static EMPTY: PrioritaryPropertyIdSet = PrioritaryPropertyIdSet(0);
        if (self as u8) < 4 { &APPEARANCE } else { &EMPTY }
    }
}
#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
struct RuleCascadeFlags(u8);
impl std::ops::Sub for RuleCascadeFlags { type Output = Self; fn sub(self, rhs: Self) -> Self { Self(self.0 & !rhs.0) } }
impl RuleCascadeFlags { fn is_empty(self) -> bool { self.0 == 0 } }
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum RevertKind { Origin, Layer, Rule }
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct CascadePriority { origin: u8, layer: u8, rule: u8, flags: RuleCascadeFlags }
impl CascadePriority {
    fn flags(self) -> RuleCascadeFlags { self.flags }
    fn allows_when_reverted(self, next: &Self, kind: RevertKind) -> bool {
        match kind { RevertKind::Origin => next.origin < self.origin, RevertKind::Layer => (next.origin,next.layer) < (self.origin,self.layer), RevertKind::Rule => (next.origin,next.layer,next.rule) < (self.origin,self.layer,self.rule) }
    }
}
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum CSSWideKeyword { Revert(RevertKind), Initial, Inherit, Unset }
impl CSSWideKeyword { fn revert_kind(self) -> Option<RevertKind> { if let Self::Revert(kind)=self {Some(kind)} else {None} } }
#[derive(Clone, Debug)]
struct UnparsedValue { result: Box<PropertyDeclaration> }
#[derive(Clone, Debug)]
struct VariableDeclaration { value: Arc<UnparsedValue>, longhand: LonghandId }
#[derive(Clone, Debug)]
enum PropertyDeclaration { WithVariables(VariableDeclaration), Wide(CSSWideKeyword), Value(u16), Synthesis(LonghandId,u16), SynthesisWide(LonghandId,CSSWideKeyword) }
impl PropertyDeclaration { fn get_css_wide_keyword(&self) -> Option<CSSWideKeyword> { match self {Self::Wide(kw)|Self::SynthesisWide(_,kw)=>Some(*kw),_=>None} } }
#[derive(Clone, Copy)]
struct Declaration<'a> { decl: &'a PropertyDeclaration, priority: CascadePriority, next_index: DeclarationIndex }
#[derive(Clone, Copy)]
struct DeclarationPosition { most_important: DeclarationIndex }
struct Declarations<'a> { longhand_declarations: Vec<Declaration<'a>>, prioritary_positions: [DeclarationPosition;11] }
#[derive(Default)]
struct Seen { longhands: LonghandSet }
#[derive(Default,Clone)]
struct LonghandSet(HashSet<LonghandId>);
impl LonghandSet {
 fn contains(&self, id: LonghandId) -> bool { self.0.contains(&id) }
 fn insert(&mut self, id: LonghandId) { self.0.insert(id); }
 fn is_empty(&self) -> bool { self.0.is_empty() }
}
#[derive(Default)]
struct Reverted { longhands: HashMap<LonghandId,(CascadePriority,RevertKind)> }
#[derive(Default)]
struct Cascade<'a> { seen: Seen, reverted: Reverted, ensured_prioritary: PrioritaryPropertyIdSet, completed_prioritary: PrioritaryPropertyIdSet, priority_completion_flags: Option<RuleCascadeFlags>, substitutions: Cell<usize>, publications: Vec<PropertyDeclaration>, fixups: usize, lifetime: std::marker::PhantomData<&'a ()> }
mod computed { #[derive(Default)] pub struct Context { pub included_cascade_flags: super::RuleCascadeFlags, pub preparations: std::cell::Cell<usize>, pub computations: std::cell::Cell<usize> }
 impl Context { pub fn is_root_element(&self)->bool{false} } }
struct ShorthandsWithPropertyReferencesCache;
struct AttributeTracker;
impl Cascade<'_> {
    fn substitute_variables_if_needed<'a>(&self, _: &mut computed::Context, _: &mut ShorthandsWithPropertyReferencesCache, declaration: &'a PropertyDeclaration, _: &mut AttributeTracker) -> Cow<'a,PropertyDeclaration> {
        if let PropertyDeclaration::WithVariables(v)=declaration { self.substitutions.set(self.substitutions.get()+1); Cow::Owned((*v.value.result).clone()) } else {Cow::Borrowed(declaration)}
    }
    fn apply_one_longhand(&mut self, _: &mut computed::Context, id: LonghandId, declaration: &PropertyDeclaration, priority: CascadePriority, _: &mut ShorthandsWithPropertyReferencesCache, _: &mut AttributeTracker) {
        let prepared;
        let declaration=if let PropertyDeclaration::WithVariables(v)=declaration {self.substitutions.set(self.substitutions.get()+1);prepared=(*v.value.result).clone();&prepared}else{declaration};
        if let Some(kind)=declaration.get_css_wide_keyword().and_then(|kw|kw.revert_kind()) { self.reverted.longhands.insert(id,(priority,kind)); } else { self.seen.longhands.insert(id); }
        self.publications.push(declaration.clone());
    }
    fn did_apply_prioritary_property(&mut self, _: &mut computed::Context, _: PrioritaryPropertyId) { self.fixups+=1; }
}
fn var(value: PropertyDeclaration) -> PropertyDeclaration { PropertyDeclaration::WithVariables(VariableDeclaration { value: Arc::new(UnparsedValue { result: Box::new(value) }), longhand: PrioritaryPropertyId::FontWeight }) }
fn declarations<'a>(values: &'a [PropertyDeclaration], priorities: &[CascadePriority]) -> Declarations<'a> {
    Declarations { longhand_declarations: values.iter().enumerate().map(|(i,decl)|Declaration { decl, priority: priorities[i], next_index: if i+1==values.len(){0}else{(i+1)as DeclarationIndex} }).collect(), prioritary_positions: [DeclarationPosition { most_important: if values.is_empty(){DeclarationIndex::MAX}else{0} };11] }
}
fn priority(origin:u8,layer:u8,rule:u8,flags:u8) -> CascadePriority { CascadePriority { origin,layer,rule,flags:RuleCascadeFlags(flags) } }

#[derive(Clone,Debug,Eq,PartialEq)]
enum VarType { Custom(String), NonCustom(SingleNonCustomReference) }
#[derive(Clone,Copy)]
enum FramePhase { Prepare, Units, LateDefault, Publish, Other }
#[derive(Clone)]
struct TraversalFrame {var:VarType,index:usize,phase:FramePhase,lowlink:usize,cursor:usize,registered:bool,selected_dependency_eligible:bool,value_non_custom_refs:ReferenceFlags,value:Option<Arc<TestValue>>,prepared_custom:Option<TestPrepared>,self_ref:bool,unit_links:Vec<SingleNonCustomReference>,unit_cursor:usize}
struct VarInfo {publication:NodePublication<()>}
#[derive(Debug,PartialEq,Eq)]
enum VisitResult {ComputationPending(usize),Complete}
struct Context<'a,'b> {
 stylist:(),decls:&'a Declarations<'b>,font_preparation:Option<MetricPreparation<'a,'b>>,completed_font_inputs:LonghandSet,font_completion_flags:Option<RuleCascadeFlags>,metric_action:Option<MetricAction>,frame_root:Option<VarType>,frames:Vec<TraversalFrame>,var_info:Vec<VarInfo>,stack:Vec<usize>,
 priority_completion:PriorityCompletion,metric_drain:MetricDrain<'a,'b>,cascade:&'a mut Cascade<'b>,computed_context:&'a mut computed::Context,cache:&'a mut ShorthandsWithPropertyReferencesCache,
}
fn with_context<'b>(values:&'b [PropertyDeclaration],f:impl FnOnce(&mut Context<'_,'b>,&mut AttributeTracker)){
 let priorities=vec![priority(2,2,2,0);values.len()];let decls=declarations(values,&priorities);let mut cascade=Cascade::default();let mut computed=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache;let mut tracker=AttributeTracker;
 let root=VarType::Custom("metric".into());
 let mut context=Context{stylist:(),decls:&decls,font_preparation:None,completed_font_inputs:LonghandSet::default(),font_completion_flags:None,metric_action:None,frame_root:Some(root),frames:vec![],var_info:vec![VarInfo{publication:NodePublication::Pending(())}],stack:vec![9],priority_completion:PriorityCompletion::default(),metric_drain:MetricDrain::new(&decls),cascade:&mut cascade,computed_context:&mut computed,cache:&mut cache};
 f(&mut context,&mut tracker);
}
fn paused_frame()->TraversalFrame{TraversalFrame{var:VarType::Custom("metric".into()),index:0,phase:FramePhase::Publish,lowlink:3,cursor:2,registered:false,selected_dependency_eligible:false,value_non_custom_refs:ReferenceFlags::empty(),value:None,prepared_custom:None,self_ref:false,unit_links:vec![],unit_cursor:0}}
fn complete_literal_appearance(c:&mut Context,t:&mut AttributeTracker){
 let cascade=&mut *c.cascade;let computed=&mut *c.computed_context;let cache=&mut *c.cache;
 let result=c.priority_completion.ensure_ordinary(PrioritaryPropertyId::Appearance,&mut |id|{
  cascade.apply_one_longhand(computed,id,&PropertyDeclaration::Value(0),priority(2,2,2,0),cache,t);
  cascade.did_apply_prioritary_property(computed,id);
  ComputationStatus::Ready
 });
 assert!(matches!(result,ComputationStatus::Ready));
}
fn snapshot(c:&Context)->(Vec<usize>,Vec<(usize,usize,usize)>,usize,usize){(c.stack.clone(),c.frames.iter().map(|f|(f.index,f.lowlink,f.cursor)).collect(),c.cascade.substitutions.get(),c.cascade.publications.len())}

use bitflags::bitflags;
type CowRcStr = str;
struct NoCalcLength;
impl NoCalcLength {
 const EM:&'static str="em";const EX:&'static str="ex";const CAP:&'static str="cap";const CH:&'static str="ch";const IC:&'static str="ic";const LH:&'static str="lh";
 const REM:&'static str="rem";const REX:&'static str="rex";const RCAP:&'static str="rcap";const RCH:&'static str="rch";const RIC:&'static str="ric";const RLH:&'static str="rlh";
}

#[derive(Clone)]struct TestValue;
#[derive(Clone)]struct TestPrepared;
impl TestPrepared {fn depends_on_color_scheme(&self)->bool{false}}
fn prepare_custom_value(_: &String,_:&TestValue,_:(),context:&computed::Context,_:&mut AttributeTracker)->TestPrepared{context.preparations.set(context.preparations.get()+1);TestPrepared}

enum LinkPurpose{Unit}
enum FrameStep{Link(VarType),Pending(Option<FontTarget>),Complete(VisitResult),Next}
impl TraversalFrame {fn link(&mut self,target:VarType,_:LinkPurpose)->FrameStep{FrameStep::Link(target)}}
impl Context<'_,'_> {fn publish_closed(&mut self,index:usize,_:&mut AttributeTracker){self.var_info[index].publication.take_ready(true).unwrap();self.computed_context.computations.set(self.computed_context.computations.get()+1);self.var_info[index].publication.finish();}}

#[derive(Clone,Copy,PartialEq,Eq)]enum PropertyDeclarationId{Longhand(LonghandId)}
impl PropertyDeclaration {fn id(&self)->PropertyDeclarationId{PropertyDeclarationId::Longhand(match self{Self::Synthesis(id,_)|Self::SynthesisWide(id,_)=>*id,Self::WithVariables(v)=>v.longhand,_=>PrioritaryPropertyId::FontWeight})}}
type LonghandIdSet=LonghandSet;
fn synthesis_var(id:LonghandId,value:PropertyDeclaration)->PropertyDeclaration{PropertyDeclaration::WithVariables(VariableDeclaration{value:Arc::new(UnparsedValue{result:Box::new(value)}),longhand:id})}

fn with_synthesis_context(values:&[PropertyDeclaration],priorities:&[CascadePriority],f:impl FnOnce(&mut Context,&mut AttributeTracker)){
 let mut decls=declarations(values,priorities);decls.prioritary_positions=[DeclarationPosition{most_important:DeclarationIndex::MAX};11];
 let mut cascade=Cascade::default();let mut computed=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache;let mut tracker=AttributeTracker;
 let mut context=Context{stylist:(),decls:&decls,font_preparation:None,completed_font_inputs:LonghandSet::default(),font_completion_flags:None,metric_action:None,frame_root:Some(VarType::Custom("metric".into())),frames:vec![],var_info:vec![VarInfo{publication:NodePublication::Pending(())}],stack:vec![9],priority_completion:PriorityCompletion::default(),metric_drain:MetricDrain::new(&decls),cascade:&mut cascade,computed_context:&mut computed,cache:&mut cache};
 for id in [PrioritaryPropertyId::Appearance,PrioritaryPropertyId::FontSize,PrioritaryPropertyId::FontWeight,PrioritaryPropertyId::FontWidth,PrioritaryPropertyId::FontStyle,PrioritaryPropertyId::FontSizeAdjust,PrioritaryPropertyId::Direction,PrioritaryPropertyId::WritingMode,PrioritaryPropertyId::TextOrientation] {context.cascade.ensure_prioritary_property(context.computed_context,&decls,context.cache,&mut tracker,id);}
 context.import_priority_completion();f(&mut context,&mut tracker);
}
