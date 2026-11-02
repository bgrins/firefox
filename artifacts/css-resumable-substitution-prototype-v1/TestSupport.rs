#![allow(dead_code, non_snake_case, non_upper_case_globals, private_interfaces)]
use cssparser::{CowRcStr, Parser, Token, SourcePosition, TokenSerializationType, Delimiter};
use bitflags::bitflags;
use smallvec::SmallVec;
use servo_arc::Arc;
use std::{borrow::Cow, num};
type ParseError = cssparser::ParseError<()>;
type Name = String;
type Atom = String;
type Prefix = String;
type Namespace = String;
type FxHashMap<K,V> = std::collections::HashMap<K,V>;
type PropertyIdRef<'a> = &'a str;
#[derive(Clone, Debug)] struct UrlExtraData;
#[derive(Clone, Debug, PartialEq)] enum ParsedNamespace { Known(Namespace), Unknown }
impl ParsedNamespace {
    fn parse(names: &FxHashMap<Prefix,Namespace>, input: &mut Parser)->Result<Self,ParseError> {
        let name=input.expect_ident()?.to_string();
        input.expect_delim('|')?;
        Ok(names.get(&name).cloned().map_or(Self::Unknown,Self::Known))
    }
}
#[derive(Clone, Debug, PartialEq)] enum AttrUnit { Number, Percentage, Px, Em }
impl AttrUnit {
    fn from_ident(s:&str)->Result<Self,()> {match s {"number"=>Ok(Self::Number),"px"=>Ok(Self::Px),"em"=>Ok(Self::Em),_=>Err(())}}
    fn as_ref(&self)->&str {match self {Self::Number=>"",Self::Percentage=>"%",Self::Px=>"px",Self::Em=>"em"}}
}
#[derive(Clone, Debug, PartialEq)] struct SyntaxDescriptor(String);
impl SyntaxDescriptor {
    fn from_css_parser(input:&mut Parser)->Result<Self,ParseError> {
        let start=input.position();
        while input.next_including_whitespace_and_comments().is_ok() {}
        Ok(Self(input.slice_from(start).to_string()))
    }
}
enum AllowComputationallyDependent { Yes }
struct SpecifiedRegisteredValue(VariableValue);
impl SpecifiedRegisteredValue {
    fn parse(input:&mut Parser, syntax:&SyntaxDescriptor, url:&UrlExtraData, _:Option<()>, _:AllowComputationallyDependent, _:AttrTaint, _:Option<PropertyIdRef>)->Result<Self,()> {
        let start=input.position();
        match syntax.0.as_str() {
            "<length>"=>{match input.next().map_err(|_|())? {Token::Dimension{unit,..} if matches!(unit.as_ref(),"px"|"em"|"ch")=>{},_=>return Err(())}},
            "<number>"=>{input.expect_number().map_err(|_|())?;},
            "*"=>{while input.next_including_whitespace_and_comments().is_ok() {}},
            _=>panic!("typed syntax outside extracted facade"),
        }
        input.expect_exhausted().map_err(|_|())?;
        let css=input.slice_from(start);
        let value=VariableValue::parse(&mut Parser::new(css),None,url).map_err(|_|())?;
        Ok(Self(value))
    }
    fn to_variable_value(&self)->VariableValue {self.0.clone()}
}
mod StyleParseErrorKind {
    pub const BadUrlInDeclarationValueBlock:()=(); pub const BadStringInDeclarationValueBlock:()=();
    pub const UnbalancedCloseParenthesisInDeclarationValueBlock:()=();
    pub const UnbalancedCloseSquareBracketInDeclarationValueBlock:()=();
    pub const UnbalancedCloseCurlyBracketInDeclarationValueBlock:()=(); pub const UnspecifiedError:()=();
}
mod SelectorParseErrorKind {pub const UnexpectedIdent:()=();}
impl SubstitutionFunctionKind {
    fn from_ident(s:&str)->Result<Self,()> {
        cssparser::match_ignore_ascii_case! {s,"var"=>Ok(Self::Var),"env"=>Ok(Self::Env),"attr"=>Ok(Self::Attr),_=>Err(())}
    }
}
type ComputedValue=VariableValue;
#[derive(Clone)] struct ComputedRegisteredValue { value:VariableValue, attr_tainted:bool }
impl ComputedRegisteredValue {
    fn as_universal(&self)->Option<&VariableValue> {Some(&self.value)}
    fn to_variable_value(&self)->VariableValue {self.value.clone()}
}
#[derive(Default)] struct ComputedSubstitutionFunctions {
    vars:FxHashMap<Name,ComputedRegisteredValue>, attrs:FxHashMap<Name,ComputedRegisteredValue>,
}
impl ComputedSubstitutionFunctions {
    fn get_var(&self,_:&(),name:&Name)->Option<&ComputedRegisteredValue> {self.vars.get(name)}
    fn get_attr(&self,name:&Name,_:&Namespace)->Option<&ComputedRegisteredValue> {self.attrs.get(name)}
}
#[derive(Default)] struct Device { values:FxHashMap<Name,VariableValue> }
impl Device {
    fn environment(&self)->&Self {self}
    fn get(&self,name:&Name,_:&Device,_:&UrlExtraData)->Option<VariableValue> {self.values.get(name).cloned()}
}
#[derive(Default)] struct Stylist {device:Device}
impl Stylist {
    fn device(&self)->&Device {&self.device}
    fn get_custom_property_registration(&self,_:&Name)->&() {&()}
}
mod computed {#[derive(Default)] pub struct Context {pub in_container_query:bool}}
#[derive(Default)] struct AttributeTracker {values:FxHashMap<Name,String>, queries:Vec<String>}
impl AttributeTracker {
    fn query(&mut self,name:&str,namespace:&Namespace)->Option<String> {
        self.queries.push(format!("{namespace}:{name}"));self.values.get(name).cloned()
    }
}
struct LocalName;
impl LocalName {fn with_name<T>(name:&Name,f:impl FnOnce(&str)->T)->T {f(name)}}
