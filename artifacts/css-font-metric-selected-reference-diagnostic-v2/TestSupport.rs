use std::cmp;
use std::collections::hash_map::Entry as EntryRef;
use std::borrow::Cow;
use std::cell::Cell;
use std::collections::{HashMap, HashSet};
use servo_arc::Arc;

type DeclarationIndex = u16;
#[derive(Clone, Copy, Debug, Eq, PartialEq, Hash)]
pub enum LonghandId { FontWeight, FontWidth, FontStyle, FontSizeAdjust, Direction, WritingMode, TextOrientation, Appearance, FontSize, LineHeight, ColorScheme, FontSynthesisWeight, FontSynthesisStyle, FontSynthesisSmallCaps, FontSynthesisPosition, FontFeatureSettings }
#[derive(Clone, Copy, Debug)]
pub enum PrioritaryPropertyId { FontWeight, FontWidth, FontStyle, FontSizeAdjust, Direction, WritingMode, TextOrientation, Appearance, FontSize, LineHeight, ColorScheme }
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
    fn to_longhand(self) -> LonghandId { match self { Self::FontWeight => LonghandId::FontWeight, Self::FontWidth => LonghandId::FontWidth, Self::FontStyle => LonghandId::FontStyle, Self::FontSizeAdjust => LonghandId::FontSizeAdjust, Self::Direction => LonghandId::Direction, Self::WritingMode => LonghandId::WritingMode, Self::TextOrientation => LonghandId::TextOrientation, Self::Appearance => LonghandId::Appearance, Self::FontSize => LonghandId::FontSize, Self::LineHeight => LonghandId::LineHeight, Self::ColorScheme => LonghandId::ColorScheme } }
    fn from_longhand(id:LonghandId)->Option<Self>{match id {LonghandId::FontWeight => Some(Self::FontWeight), LonghandId::FontWidth => Some(Self::FontWidth), LonghandId::FontStyle => Some(Self::FontStyle), LonghandId::FontSizeAdjust => Some(Self::FontSizeAdjust), LonghandId::Direction => Some(Self::Direction), LonghandId::WritingMode => Some(Self::WritingMode), LonghandId::TextOrientation => Some(Self::TextOrientation), LonghandId::Appearance => Some(Self::Appearance), LonghandId::FontSize => Some(Self::FontSize), LonghandId::LineHeight => Some(Self::LineHeight), LonghandId::ColorScheme => Some(Self::ColorScheme), _=>None}}
    fn dependencies(self) -> &'static PrioritaryPropertyIdSet {
        static APPEARANCE: PrioritaryPropertyIdSet = PrioritaryPropertyIdSet(1 << 7);
        static EMPTY: PrioritaryPropertyIdSet = PrioritaryPropertyIdSet(0);
        if (self as u8) < 4 { &APPEARANCE } else { &EMPTY }
    }
}
impl LonghandId {
 fn name(self)->&'static str {match self {Self::FontSynthesisWeight=>"font-synthesis-weight",Self::FontSynthesisStyle=>"font-synthesis-style",Self::FontSynthesisSmallCaps=>"font-synthesis-small-caps",Self::FontSynthesisPosition=>"font-synthesis-position",Self::FontFeatureSettings=>"font-feature-settings",_=>"font-weight"}}
 fn is_logical(self)->bool{false}
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
struct UnparsedValue { result: Box<PropertyDeclaration>, variable_value:VariableValue }
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
mod computed { #[derive(Default)] pub struct Context { pub included_cascade_flags: super::RuleCascadeFlags, pub preparations: std::cell::Cell<usize>, pub computations: std::cell::Cell<usize>, pub builder: super::Builder, pub events:Vec<String> }
 impl Context { pub fn is_root_element(&self)->bool{false} } }
type ComputedContext=computed::Context;
struct ShorthandsWithPropertyReferencesCache;

impl Cascade<'_> {
    fn substitute_variables_if_needed<'a>(&self, context: &mut computed::Context, _: &mut ShorthandsWithPropertyReferencesCache, declaration: &'a PropertyDeclaration, _: &mut AttributeTracker) -> Cow<'a,PropertyDeclaration> {
        if let PropertyDeclaration::WithVariables(v)=declaration { self.substitutions.set(self.substitutions.get()+1); Cow::Owned(resolve_declaration(&v.value, context)) } else {Cow::Borrowed(declaration)}
    }
    fn apply_one_longhand(&mut self, _: &mut computed::Context, id: LonghandId, declaration: &PropertyDeclaration, priority: CascadePriority, _: &mut ShorthandsWithPropertyReferencesCache, _: &mut AttributeTracker) {
        let prepared;
        let declaration=if let PropertyDeclaration::WithVariables(v)=declaration {self.substitutions.set(self.substitutions.get()+1);prepared=(*v.value.result).clone();&prepared}else{declaration};
        if let Some(kind)=declaration.get_css_wide_keyword().and_then(|kw|kw.revert_kind()) { self.reverted.longhands.insert(id,(priority,kind)); } else { self.seen.longhands.insert(id); }
        self.publications.push(declaration.clone());
    }
    fn did_apply_prioritary_property(&mut self, _: &mut computed::Context, _: PrioritaryPropertyId) { self.fixups+=1; }
}
fn var(value: PropertyDeclaration) -> PropertyDeclaration { PropertyDeclaration::WithVariables(VariableDeclaration { value: Arc::new(UnparsedValue { result: Box::new(value), variable_value:VariableValue::default() }), longhand: LonghandId::FontWeight }) }
fn declarations<'a>(values: &'a [PropertyDeclaration], priorities: &[CascadePriority]) -> Declarations<'a> {
    Declarations { longhand_declarations: values.iter().enumerate().map(|(i,decl)|Declaration { decl, priority: priorities[i], next_index: if i+1==values.len(){0}else{(i+1)as DeclarationIndex} }).collect(), prioritary_positions: [DeclarationPosition { most_important: if values.is_empty(){DeclarationIndex::MAX}else{0} };11] }
}
fn priority(origin:u8,layer:u8,rule:u8,flags:u8) -> CascadePriority { CascadePriority { origin,layer,rule,flags:RuleCascadeFlags(flags) } }

use bitflags::bitflags;
type CowRcStr = str;
struct NoCalcLength;
impl NoCalcLength {
 const EM:&'static str="em";const EX:&'static str="ex";const CAP:&'static str="cap";const CH:&'static str="ch";const IC:&'static str="ic";const LH:&'static str="lh";
 const REM:&'static str="rem";const REX:&'static str="rex";const RCAP:&'static str="rcap";const RCH:&'static str="rch";const RIC:&'static str="ric";const RLH:&'static str="rlh";
}

#[derive(Clone,Copy,PartialEq,Eq)]enum PropertyDeclarationId{Longhand(LonghandId)}
impl PropertyDeclaration {fn id(&self)->PropertyDeclarationId{PropertyDeclarationId::Longhand(match self{Self::Synthesis(id,_)|Self::SynthesisWide(id,_)=>*id,Self::WithVariables(v)=>v.longhand,_=>LonghandId::FontWeight})}}
type LonghandIdSet=LonghandSet;
fn synthesis_var(id:LonghandId,value:PropertyDeclaration)->PropertyDeclaration{PropertyDeclaration::WithVariables(VariableDeclaration{value:Arc::new(UnparsedValue{result:Box::new(value),variable_value:VariableValue::default()}),longhand:id})}

type Name = String;
type Namespace = String;
type PrecomputedHashMap<K,V> = HashMap<K,V>;
type SmallVec<T> = Vec<<T as Array>::Item>;
trait Array { type Item; }
impl<T,const N:usize> Array for [T;N] {type Item=T;}
#[derive(Debug)]
struct NonCustomReferenceMap<T>([Option<T>;3]);
impl<T> Default for NonCustomReferenceMap<T>{fn default()->Self{Self(std::array::from_fn(|_|None))}}
impl<T> std::ops::Index<SingleNonCustomReference> for NonCustomReferenceMap<T>{type Output=Option<T>;fn index(&self,i:SingleNonCustomReference)->&Option<T>{&self.0[i as usize]}}
impl<T> std::ops::IndexMut<SingleNonCustomReference> for NonCustomReferenceMap<T>{fn index_mut(&mut self,i:SingleNonCustomReference)->&mut Option<T>{&mut self.0[i as usize]}}
type NonCustomPropertyReferences=NonCustomReferenceMap<Vec<(LonghandId,Arc<UnparsedValue>)>>;
#[derive(Clone,Copy,Debug,Eq,PartialEq)]
enum SubstitutionFunctionKind{Var,Attr,Env}
#[derive(Clone,Debug,Default)]
struct References{refs:Vec<Reference>,flags:ReferenceFlags}
#[derive(Clone,Debug)]
struct Reference{name:Name,substitution_kind:SubstitutionFunctionKind,attribute_data:AttrData,fallback:Option<Box<VariableValue>>}
impl Reference{fn is_attr_with_type(&self)->bool{self.substitution_kind==SubstitutionFunctionKind::Attr&&self.attribute_data.typed}}
#[derive(Clone,Debug,Default)]
struct AttrData{namespace:Option<Namespace>,typed:bool,valid_non_type:bool,expected_consumer:Option<LonghandId>}
impl AttrData{
 fn namespace(&self)->Option<&Namespace>{self.namespace.as_ref()}
 fn non_type_primary_is_valid(&self,_:&Name,t:&mut AttributeTracker)->bool{t.non_type_reads+=1;self.valid_non_type}
 fn parse_typed_value(&self,p:&mut cssparser::Parser,_:&UrlExtraData,consumer:Option<PropertyIdRef>)->Result<(),()>{if p.css=="bad" || self.expected_consumer.is_some_and(|id|consumer.and_then(|p|p.0)!=Some(id)){Err(())}else{Ok(())}}
}
#[derive(Clone,Debug,Default)]struct UrlExtraData;
#[derive(Clone,Copy)]struct PropertyIdRef(Option<LonghandId>);
impl From<&Name> for PropertyIdRef{fn from(_:&Name)->Self{Self(None)}}
#[derive(Clone,Debug,Default)]struct VariableValue{css:String,references:References,url_data:UrlExtraData}
impl VariableValue{fn has_references(&self)->bool{!self.references.refs.is_empty()}}
type ComputedPropertyValue=VariableValue;
impl UnparsedValue{fn substitution_property_id(&self,id:LonghandId)->PropertyIdRef{PropertyIdRef(Some(id))}}
#[derive(Clone,Debug)]struct Value{universal:Option<Arc<VariableValue>>,css:String}
impl Value{fn as_universal(&self)->Option<&Arc<VariableValue>>{self.universal.as_ref()}fn to_variable_value(&self)->VariableValue{VariableValue{css:self.css.clone(),..Default::default()}}}
#[derive(Default)]struct Map{vars:HashMap<Name,Value>,attrs:HashMap<(Name,Namespace),Value>}
impl Map{
 fn contains_attr(&self,n:&Name,ns:&Namespace)->bool{self.attrs.contains_key(&(n.clone(),ns.clone()))}
 fn insert_attr(&mut self,n:&Name,ns:&Namespace,v:Value){self.attrs.insert((n.clone(),ns.clone()),v);}
 fn get_attr(&self,n:&Name,ns:&Namespace)->Option<&Value>{self.attrs.get(&(n.clone(),ns.clone()))}
 fn get_var(&self,_:&PropertyDescriptors,n:&Name)->Option<&Value>{self.vars.get(n)}
}
#[derive(Default)]struct Builder{substitution_functions:Map}
struct PreparedCustomValue{css:String}
impl PreparedCustomValue{
 fn depends_on_color_scheme(&self)->bool{self.css.contains("color")}
 fn apply(self,n:&Name,_:&Stylist,c:&mut ComputedContext){c.events.push(format!("prepared:{n}"));c.builder.substitution_functions.vars.insert(n.clone(),computed(&self.css));}
}
fn prepare_custom_value(n:&Name,v:&VariableValue,_:&Stylist,c:&mut ComputedContext,_:&mut AttributeTracker)->PreparedCustomValue{c.events.push(format!("prepare:{n}"));PreparedCustomValue{css:v.css.clone()}}
fn substitute_references_if_needed_and_apply(n:&Name,ns:Option<&Namespace>,v:&VariableValue,_:&Stylist,c:&mut ComputedContext,_:&mut AttributeTracker){
 c.events.push(format!("substitute:{n}:{ns:?}"));
 let css=resolve_value(v,c);
 if v.css=="flags:1em" {c.included_cascade_flags=RuleCascadeFlags(1);}
 if let Some(ns)=ns{c.builder.substitution_functions.insert_attr(n,ns,computed(&css));}else{c.builder.substitution_functions.vars.insert(n.clone(),computed(&css));}
}
fn invalid_custom_value_depends_on_color_scheme(n:&Name,s:&Stylist,_:&ComputedContext)->bool{s.default_color.contains(n)}
fn find_non_custom_references(r:&PropertyDescriptors,v:&VariableValue,_:bool)->ReferenceFlags{if r.is_universal(){ReferenceFlags::empty()}else{v.references.flags - (ReferenceFlags::VAR | ReferenceFlags::ATTR | ReferenceFlags::ENV)}}
mod properties_and_values{pub mod syntax{
 pub mod data_type{#[derive(Clone,Copy)]pub struct DependentDataTypes;impl DependentDataTypes{pub const COLOR:Self=Self;pub fn intersects(self,_:Self)->bool{true}}pub enum DataType{Image}}
 pub enum ComponentName{DataType(data_type::DataType)}
 pub struct Component;impl Component{pub fn name(&self)->ComponentName{ComponentName::DataType(data_type::DataType::Image)}}
 pub struct Syntax{pub components:Vec<Component>}impl Syntax{pub fn dependent_types(&self)->data_type::DependentDataTypes{data_type::DependentDataTypes}}
}}
use properties_and_values::syntax::Syntax;
struct PropertyDescriptors{syntax:Option<Syntax>}
impl PropertyDescriptors{fn unregistered()->&'static Self{static U:PropertyDescriptors=PropertyDescriptors{syntax:None};&U}fn is_universal(&self)->bool{self.syntax.is_none()}}
#[derive(Default)]struct Stylist{device:Device,registered:HashMap<Name,PropertyDescriptors>,default_color:HashSet<Name>}
impl Stylist{fn device(&self)->&Device{&self.device}fn get_custom_property_registration(&self,n:&Name)->&PropertyDescriptors{self.registered.get(n).unwrap_or(PropertyDescriptors::unregistered())}}
#[derive(Default)]struct Device{environment:Environment}impl Device{fn environment(&self)->&Environment{&self.environment}}
#[derive(Default)]struct Environment{values:HashMap<Name,String>}impl Environment{fn get(&self,n:&Name,_:&Device,_:&UrlExtraData)->Option<&String>{self.values.get(n)}}
#[derive(Default)]struct AttributeTracker{loads:usize,non_type_reads:usize,raw:HashMap<Name,Value>}
fn get_attr_value_for_cycle_resolution(n:&Name,_:&AttrData,_:&UrlExtraData,t:&mut AttributeTracker)->Result<Value,()>{t.loads+=1;t.raw.get(n).cloned().ok_or(())}
mod cssparser{pub struct Parser<'a>{pub css:&'a str}impl<'a> Parser<'a>{pub fn new(css:&'a str)->Self{Self{css}}}}
fn computed(css:&str)->Value{Value{universal:None,css:css.into()}}
fn variable(css:&str,refs:Vec<Reference>,flags:ReferenceFlags)->Value{Value{universal:Some(Arc::new(VariableValue{css:css.into(),references:References{refs,flags},url_data:UrlExtraData})),css:css.into()}}
fn reference(n:&str,fallback:Option<&str>)->Reference{Reference{name:n.into(),substitution_kind:SubstitutionFunctionKind::Var,attribute_data:AttrData::default(),fallback:fallback.map(|n|Box::new(VariableValue{references:References{refs:vec![reference(n,None)],flags:ReferenceFlags::VAR},..Default::default()}))}}

fn resolve_value(v:&VariableValue,c:&computed::Context)->String {
 if v.css=="1em" || v.css=="flags:1em" { return "20".into(); }
 if let Some(reference)=v.references.refs.first() {
  let value=match reference.substitution_kind {SubstitutionFunctionKind::Var=>c.builder.substitution_functions.vars.get(&reference.name),SubstitutionFunctionKind::Attr=>reference.attribute_data.namespace().and_then(|ns|c.builder.substitution_functions.get_attr(&reference.name,ns)),_=>None};
  if let Some(value)=value {assert!(value.as_universal().is_none(), "consumer read before child publication");return value.css.clone();}
  if let Some(fallback)=&reference.fallback {return resolve_value(fallback,c);}
 }
 v.css.clone()
}
fn resolve_declaration(v:&UnparsedValue,c:&mut computed::Context)->PropertyDeclaration {
 if v.variable_value.references.refs.is_empty(){return (*v.result).clone();}
 let value=resolve_value(&v.variable_value,c);c.events.push(format!("selected:{value}"));
 if value=="revert" {PropertyDeclaration::Wide(CSSWideKeyword::Revert(RevertKind::Origin))}
 else {PropertyDeclaration::Value(value.parse::<u16>().unwrap()*35)}
}
struct Context<'a,'b>{
 count:usize,index_map:OrderIndexMap,non_custom_index_map:NonCustomReferenceMap<usize>,var_info:Vec<VarInfo>,stack:Vec<usize>,
 frames:Vec<TraversalFrame>,frame_root:Option<VarType>,frame_reply:Option<(VarType,VisitResult)>,
 stylist:&'a Stylist,computed_context:&'a mut ComputedContext,
 decls:&'a Declarations<'b>,font_preparation:Option<MetricPreparation<'a,'b>>,completed_font_inputs:LonghandSet,font_completion_flags:Option<RuleCascadeFlags>,metric_action:Option<MetricAction>,metric_references:Option<MetricReferences>,
 priority_completion:PriorityCompletion,metric_drain:MetricDrain<'a,'b>,cascade:&'a mut Cascade<'b>,cache:&'a mut ShorthandsWithPropertyReferencesCache,
}
impl Context<'_,'_>{
 fn map(&self)->&Map{&self.computed_context.builder.substitution_functions}fn map_mut(&mut self)->&mut Map{&mut self.computed_context.builder.substitution_functions}
 fn handle_loop(&mut self,var:&VarType){self.computed_context.events.push(format!("invalid:{var:?}"));match var{VarType::Custom(n)=>{self.map_mut().vars.remove(n);},VarType::Attr(n,ns)=>{self.map_mut().attrs.remove(&(n.clone(),ns.clone()));},VarType::NonCustom(_)=>{}}}
 fn apply_prioritary_property(&mut self,id:PrioritaryPropertyId,_:&mut AttributeTracker){self.computed_context.events.push(format!("priority:{id:?}"));self.cascade.completed_prioritary.insert(id);}
}
