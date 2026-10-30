use std::collections::{HashMap, HashSet};
use std::sync::Arc;
use std::cmp;
use std::collections::hash_map::Entry as EntryRef;
type Name = String;
type Namespace = String;
type PrecomputedHashMap<K,V> = HashMap<K,V>;
type SmallVec<T> = Vec<<T as Array>::Item>;
trait Array { type Item; }
impl<T,const N:usize> Array for [T;N] {type Item=T;}
#[derive(Clone,Copy,Debug,Default,Eq,PartialEq)]
struct ReferenceFlags(u16);
impl ReferenceFlags {
 const VAR:Self=Self(1);const ATTR:Self=Self(2);const ENV:Self=Self(4);const COLOR_SCHEME:Self=Self(8);const FONT:Self=Self(16);const LH:Self=Self(32);
 fn empty()->Self{Self(0)} fn is_empty(self)->bool{self.0==0}
 fn intersects(self,v:Self)->bool{self.0&v.0!=0} fn remove(&mut self,v:Self){self.0&=!v.0;}
 fn for_each_non_custom(self,_:bool,mut f:impl FnMut(SingleNonCustomReference)){
  for (flag,id) in [(Self::FONT,SingleNonCustomReference::FontUnits),(Self::LH,SingleNonCustomReference::LhUnits),(Self::COLOR_SCHEME,SingleNonCustomReference::ColorScheme)] {if self.intersects(flag){f(id);}}
 }
}
impl std::ops::BitOr for ReferenceFlags {type Output=Self;fn bitor(self,b:Self)->Self{Self(self.0|b.0)}}
impl std::ops::BitOrAssign for ReferenceFlags {fn bitor_assign(&mut self,b:Self){self.0|=b.0;}}
#[derive(Clone,Copy,Debug,Eq,PartialEq)]
enum SingleNonCustomReference{FontUnits,LhUnits,ColorScheme}
impl SingleNonCustomReference{fn to_prioritary_id(self)->usize{self as usize}}
type PrioritaryPropertyId=usize;
type LonghandId=usize;
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
struct AttrData{namespace:Option<Namespace>,typed:bool,valid_non_type:bool}
impl AttrData{
 fn namespace(&self)->Option<&Namespace>{self.namespace.as_ref()}
 fn non_type_primary_is_valid(&self,_:&Name,t:&mut AttributeTracker)->bool{t.non_type_reads+=1;self.valid_non_type}
 fn parse_typed_value(&self,p:&mut cssparser::Parser,_:&UrlExtraData,_:Option<PropertyIdRef>)->Result<(),()>{if p.css=="bad"{Err(())}else{Ok(())}}
}
#[derive(Clone,Debug,Default)]struct UrlExtraData;
#[derive(Clone,Copy)]struct PropertyIdRef;
impl From<&Name> for PropertyIdRef{fn from(_:&Name)->Self{Self}}
#[derive(Clone,Debug,Default)]struct VariableValue{css:String,references:References,url_data:UrlExtraData}
impl VariableValue{fn has_references(&self)->bool{!self.references.refs.is_empty()}}
type ComputedPropertyValue=VariableValue;
struct UnparsedValue{variable_value:VariableValue}
impl UnparsedValue{fn substitution_property_id(&self,_:LonghandId)->PropertyIdRef{PropertyIdRef}}
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
#[derive(Default)]struct ComputedContext{builder:Builder,events:Vec<String>}
impl ComputedContext{fn is_root_element(&self)->bool{false}}
struct PreparedCustomValue{css:String}
impl PreparedCustomValue{
 fn depends_on_color_scheme(&self)->bool{self.css.contains("color")}
 fn apply(self,n:&Name,_:&Stylist,c:&mut ComputedContext){c.events.push(format!("prepared:{n}"));c.builder.substitution_functions.vars.insert(n.clone(),computed(&self.css));}
}
fn prepare_custom_value(n:&Name,v:&VariableValue,_:&Stylist,c:&mut ComputedContext,_:&mut AttributeTracker)->PreparedCustomValue{c.events.push(format!("prepare:{n}"));PreparedCustomValue{css:v.css.clone()}}
fn substitute_references_if_needed_and_apply(n:&Name,ns:Option<&Namespace>,v:&VariableValue,_:&Stylist,c:&mut ComputedContext,_:&mut AttributeTracker){
 c.events.push(format!("substitute:{n}:{ns:?}"));
 if let Some(ns)=ns{c.builder.substitution_functions.insert_attr(n,ns,computed(&v.css));}else{c.builder.substitution_functions.vars.insert(n.clone(),computed(&v.css));}
}
fn invalid_custom_value_depends_on_color_scheme(n:&Name,s:&Stylist,_:&ComputedContext)->bool{s.default_color.contains(n)}
fn find_non_custom_references(r:&PropertyDescriptors,v:&VariableValue,_:bool)->ReferenceFlags{if r.is_universal(){ReferenceFlags::empty()}else{ReferenceFlags(v.references.flags.0&56)}}
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
struct Context<'a>{
 count:usize,index_map:OrderIndexMap,non_custom_index_map:NonCustomReferenceMap<usize>,var_info:Vec<VarInfo>,stack:Vec<usize>,
 frames:Vec<TraversalFrame>,frame_root:Option<VarType>,frame_reply:Option<(VarType,VisitResult)>,
 stylist:&'a Stylist,computed_context:&'a mut ComputedContext,
}
impl<'a> Context<'a>{
 fn new(stylist:&'a Stylist,computed_context:&'a mut ComputedContext)->Self{Self{count:0,index_map:OrderIndexMap::default(),non_custom_index_map:Default::default(),var_info:vec![],stack:vec![],frames:vec![],frame_root:None,frame_reply:None,stylist,computed_context}}
 fn map(&self)->&Map{&self.computed_context.builder.substitution_functions}fn map_mut(&mut self)->&mut Map{&mut self.computed_context.builder.substitution_functions}
 fn handle_loop(&mut self,var:&VarType){self.computed_context.events.push(format!("invalid:{var:?}"));match var{VarType::Custom(n)=>{self.map_mut().vars.remove(n);},VarType::Attr(n,ns)=>{self.map_mut().attrs.remove(&(n.clone(),ns.clone()));},VarType::NonCustom(_)=>{}}}
 fn apply_prioritary_property(&mut self,id:usize,_:&mut AttributeTracker){self.computed_context.events.push(format!("priority:{id}"));}
}
