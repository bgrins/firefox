use std::collections::HashMap;
#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
struct ReferenceFlags(u16);
impl ReferenceFlags {fn empty()->Self{Self(0)}}
impl std::ops::BitOrAssign for ReferenceFlags {fn bitor_assign(&mut self, other:Self){self.0|=other.0;}}
#[derive(Clone, Debug, Eq, PartialEq)]
enum VarType {Custom(String),Attr(String,String)}
#[derive(Clone, Copy, Eq, PartialEq)]
enum SubstitutionFunctionKind {Var,Attr,Env}
#[derive(Clone, Default)]
struct References {refs:Vec<Reference>,flags:ReferenceFlags}
#[derive(Clone)]
struct Reference {name:String,substitution_kind:SubstitutionFunctionKind,attribute_data:AttrData,fallback:Option<Box<VariableValue>>}
impl Reference {fn is_attr_with_type(&self)->bool{self.substitution_kind==SubstitutionFunctionKind::Attr && self.attribute_data.typed}}
#[derive(Clone,Default)]
struct AttrData {namespace:Option<String>,typed:bool,valid_non_type:bool}
impl AttrData {
 fn namespace(&self)->Option<&String>{self.namespace.as_ref()}
 fn non_type_primary_is_valid(&self,_:&String,tracker:&mut AttributeTracker)->bool{tracker.non_type_reads+=1;self.valid_non_type}
 fn parse_typed_value(&self,p:&mut cssparser::Parser,_:&UrlExtraData,_:Option<PropertyIdRef>)->Result<(),()>{if p.css=="bad"{Err(())}else{Ok(())}}
}
#[derive(Clone,Default)]
struct VariableValue {css:String,references:References}
impl VariableValue {fn has_references(&self)->bool{!self.references.refs.is_empty()}}
#[derive(Clone)]
struct Value {universal:Option<VariableValue>,css:String}
impl Value {fn as_universal(&self)->Option<&VariableValue>{self.universal.as_ref()} fn to_variable_value(&self)->VariableValue{VariableValue{css:self.css.clone(),references:References::default()}}}
#[derive(Default)]
struct Map {vars:HashMap<String,Value>,attrs:HashMap<(String,String),Value>}
impl Map {
 fn contains_attr(&self,n:&String,ns:&String)->bool{self.attrs.contains_key(&(n.clone(),ns.clone()))}
 fn insert_attr(&mut self,n:&String,ns:&String,v:Value){self.attrs.insert((n.clone(),ns.clone()),v);}
 fn get_attr(&self,n:&String,ns:&String)->Option<&Value>{self.attrs.get(&(n.clone(),ns.clone()))}
 fn get_var(&self,_:(),n:&String)->Option<&Value>{self.vars.get(n)}
}
#[derive(Default)]
struct Context {stylist:Stylist,map:Map}
impl Context {fn map(&self)->&Map{&self.map}fn map_mut(&mut self)->&mut Map{&mut self.map}}
#[derive(Default)]
struct Stylist {device:Device}
impl Stylist {fn device(&self)->&Device{&self.device}fn get_custom_property_registration(&self,_:&String){}}
#[derive(Default)]
struct Device {environment:Environment}
impl Device {fn environment(&self)->&Environment{&self.environment}}
#[derive(Default)]
struct Environment {values:HashMap<String,String>}
impl Environment {fn get(&self,n:&String,_:&Device,_:&UrlExtraData)->Option<&String>{self.values.get(n)}}
struct UrlExtraData;
type PropertyIdRef=();
#[derive(Default)]
struct AttributeTracker {loads:usize,non_type_reads:usize,raw:HashMap<String,Value>}
fn get_attr_value_for_cycle_resolution(n:&String,_:&AttrData,_:&UrlExtraData,t:&mut AttributeTracker)->Result<Value,()>{t.loads+=1;t.raw.get(n).cloned().ok_or(())}
mod cssparser {pub struct Parser<'a>{pub css:&'a str}impl<'a> Parser<'a>{pub fn new(css:&'a str)->Self{Self{css}}}}
fn reference(n:&str,fallback:Option<&str>)->Reference {Reference{name:n.into(),substitution_kind:SubstitutionFunctionKind::Var,attribute_data:AttrData::default(),fallback:fallback.map(|name|Box::new(VariableValue{css:String::new(),references:References{refs:vec![reference(name,None)],flags:ReferenceFlags(2)}}))}}
fn root(refs:Vec<Reference>)->References {References{refs,flags:ReferenceFlags(1)}}
fn computed(css:&str)->Value{Value{universal:None,css:css.into()}}
fn unresolved()->Value{Value{universal:Some(VariableValue{css:"var(--x)".into(),references:root(vec![reference("x",None)])}),css:"var(--x)".into()}}
fn next(w:&mut ReferenceWalk,c:&mut Context,t:&mut AttributeTracker,r:Option<(VarType,ReferenceReadiness)>)->ReferenceWalkStep {w.resume(&UrlExtraData,None,c,t,r)}
fn target(step:ReferenceWalkStep)->VarType{if let ReferenceWalkStep::Link(t)=step{t}else{panic!("expected request")}}
