use std::borrow::Cow;
use std::cell::Cell;
use std::collections::{HashMap, HashSet};
use std::sync::Arc;

type DeclarationIndex = u32;
type LonghandId = PrioritaryPropertyId;
#[derive(Clone, Copy, Debug, Eq, PartialEq, Hash)]
enum PrioritaryPropertyId { FontWeight, FontWidth, FontStyle, FontSizeAdjust, Direction, WritingMode, TextOrientation, Appearance }
#[derive(Clone, Copy, Default)]
struct PrioritaryPropertyIdSet(u16);
impl PrioritaryPropertyIdSet {
    fn contains(&self, id: PrioritaryPropertyId) -> bool { self.0 & (1 << id as u8) != 0 }
    fn insert(&mut self, id: PrioritaryPropertyId) { self.0 |= 1 << id as u8; }
    fn remove(&mut self, id: PrioritaryPropertyId) { self.0 &= !(1 << id as u8); }
    fn iter(&self) -> impl Iterator<Item=PrioritaryPropertyId> { let ids=[PrioritaryPropertyId::FontWeight,PrioritaryPropertyId::FontWidth,PrioritaryPropertyId::FontStyle,PrioritaryPropertyId::FontSizeAdjust,PrioritaryPropertyId::Direction,PrioritaryPropertyId::WritingMode,PrioritaryPropertyId::TextOrientation,PrioritaryPropertyId::Appearance]; let bits=self.0; ids.into_iter().filter(move |id|bits & (1 << *id as u8)!=0) }
    fn contains_all(&self, other: &Self) -> bool { self.0 & other.0 == other.0 }
}
impl PrioritaryPropertyId {
    fn to_longhand(self) -> Self { self }
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
struct VariableDeclaration { value: Arc<UnparsedValue> }
#[derive(Clone, Debug)]
enum PropertyDeclaration { WithVariables(VariableDeclaration), Wide(CSSWideKeyword), Value(u16) }
impl PropertyDeclaration { fn get_css_wide_keyword(&self) -> Option<CSSWideKeyword> { if let Self::Wide(kw)=self {Some(*kw)} else {None} } }
#[derive(Clone, Copy)]
struct Declaration<'a> { decl: &'a PropertyDeclaration, priority: CascadePriority, next_index: DeclarationIndex }
#[derive(Clone, Copy)]
struct DeclarationPosition { most_important: DeclarationIndex }
struct Declarations<'a> { longhand_declarations: Vec<Declaration<'a>>, prioritary_positions: [DeclarationPosition;8] }
#[derive(Default)]
struct Seen { longhands: LonghandSet }
#[derive(Default)]
struct LonghandSet(HashSet<LonghandId>);
impl LonghandSet {
 fn contains(&self, id: LonghandId) -> bool { self.0.contains(&id) }
 fn insert(&mut self, id: LonghandId) { self.0.insert(id); }
 fn is_empty(&self) -> bool { self.0.is_empty() }
}
#[derive(Default)]
struct Reverted { longhands: HashMap<LonghandId,(CascadePriority,RevertKind)> }
#[derive(Default)]
struct Cascade<'a> { seen: Seen, reverted: Reverted, ensured_prioritary: PrioritaryPropertyIdSet, substitutions: Cell<usize>, publications: Vec<PropertyDeclaration>, fixups: usize, lifetime: std::marker::PhantomData<&'a ()> }
mod computed { #[derive(Default)] pub struct Context { pub included_cascade_flags: super::RuleCascadeFlags } }
struct ShorthandsWithPropertyReferencesCache;
struct AttributeTracker;
impl Cascade<'_> {
    fn substitute_variables_if_needed<'a>(&self, _: &mut computed::Context, _: &mut ShorthandsWithPropertyReferencesCache, declaration: &'a PropertyDeclaration, _: &mut AttributeTracker) -> Cow<'a,PropertyDeclaration> {
        if let PropertyDeclaration::WithVariables(v)=declaration { self.substitutions.set(self.substitutions.get()+1); Cow::Owned((*v.value.result).clone()) } else {Cow::Borrowed(declaration)}
    }
    fn apply_one_longhand(&mut self, _: &mut computed::Context, id: LonghandId, declaration: &PropertyDeclaration, priority: CascadePriority, _: &mut ShorthandsWithPropertyReferencesCache, _: &mut AttributeTracker) {
        assert!(!matches!(declaration, PropertyDeclaration::WithVariables(..)));
        if let Some(kind)=declaration.get_css_wide_keyword().and_then(|kw|kw.revert_kind()) { self.reverted.longhands.insert(id,(priority,kind)); } else { self.seen.longhands.insert(id); }
        self.publications.push(declaration.clone());
    }
    fn did_apply_prioritary_property(&mut self, _: &mut computed::Context, _: PrioritaryPropertyId) { self.fixups+=1; }
}
fn var(value: PropertyDeclaration) -> PropertyDeclaration { PropertyDeclaration::WithVariables(VariableDeclaration { value: Arc::new(UnparsedValue { result: Box::new(value) }) }) }
fn declarations<'a>(values: &'a [PropertyDeclaration], priorities: &[CascadePriority]) -> Declarations<'a> {
    Declarations { longhand_declarations: values.iter().enumerate().map(|(i,decl)|Declaration { decl, priority: priorities[i], next_index: if i+1==values.len(){0}else{(i+1)as u32} }).collect(), prioritary_positions: [DeclarationPosition { most_important: if values.is_empty(){DeclarationIndex::MAX}else{0} };8] }
}
fn priority(origin:u8,layer:u8,rule:u8,flags:u8) -> CascadePriority { CascadePriority { origin,layer,rule,flags:RuleCascadeFlags(flags) } }

#[derive(Clone,Debug,Eq,PartialEq)]
enum VarType { Custom(String) }
#[derive(Clone,Copy)]
enum FramePhase { Publish, Other }
#[derive(Clone)]
struct TraversalFrame {var:VarType,index:usize,phase:FramePhase,lowlink:usize,cursor:usize}
struct VarInfo {publication:NodePublication<()>}
#[derive(Debug,PartialEq,Eq)]
enum VisitResult {ComputationPending(usize),Complete}
struct Context<'a,'b> {
 metric_action:Option<MetricAction>,frame_root:Option<VarType>,frames:Vec<TraversalFrame>,var_info:Vec<VarInfo>,stack:Vec<usize>,
 priority_completion:PriorityCompletion,metric_drain:MetricDrain<'a,'b>,cascade:&'a mut Cascade<'b>,computed_context:&'a mut computed::Context,cache:&'a mut ShorthandsWithPropertyReferencesCache,
}
fn with_context<'b>(values:&'b [PropertyDeclaration],f:impl FnOnce(&mut Context<'_,'b>,&mut AttributeTracker)){
 let priorities=vec![priority(2,2,2,0);values.len()];let decls=declarations(values,&priorities);let mut cascade=Cascade::default();let mut computed=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache;let mut tracker=AttributeTracker;
 let root=VarType::Custom("metric".into());
 let mut context=Context{metric_action:None,frame_root:Some(root),frames:vec![],var_info:vec![VarInfo{publication:NodePublication::Pending(())}],stack:vec![9],priority_completion:PriorityCompletion::default(),metric_drain:MetricDrain::new(&decls),cascade:&mut cascade,computed_context:&mut computed,cache:&mut cache};
 f(&mut context,&mut tracker);
}
fn paused_frame()->TraversalFrame{TraversalFrame{var:VarType::Custom("metric".into()),index:0,phase:FramePhase::Publish,lowlink:3,cursor:2}}
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
