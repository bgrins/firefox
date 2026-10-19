#![allow(dead_code, non_snake_case, non_upper_case_globals, private_interfaces)]
use cssparser::{CowRcStr, Parser, Token, SourcePosition, TokenSerializationType, Delimiter};
use bitflags::bitflags;
use smallvec::SmallVec;
use std::{borrow::Cow, num};
use std::io::{self, BufRead};
type ParseError = cssparser::ParseError<()>;
type Name = String;
type Atom = String;
type Prefix = String;
type Namespace = String;
type FxHashMap<K,V> = std::collections::HashMap<K,V>;
#[derive(Clone,Debug)] struct UrlExtraData;
#[derive(Debug)] struct AttributeData {kind:AttributeType,namespace:ParsedNamespace}
#[derive(Debug)] enum AttributeType {None}
#[derive(Debug)] enum ParsedNamespace {Known(Namespace)}
impl ParsedNamespace {
    fn parse(_: &FxHashMap<Prefix,Namespace>,_: &mut Parser)->Result<Self,ParseError> {panic!("namespace provider outside witness")}
}
fn parse_attr_type(input:&mut Parser)->AttributeType {
    let state=input.state();
    let accepted=matches!(input.next(),Err(_)|Ok(Token::Comma));
    input.reset(&state);
    assert!(accepted,"typed attribute outside witness");
    AttributeType::None
}
mod StyleParseErrorKind {
    pub const BadUrlInDeclarationValueBlock:()=();
    pub const BadStringInDeclarationValueBlock:()=();
    pub const UnbalancedCloseParenthesisInDeclarationValueBlock:()=();
    pub const UnbalancedCloseSquareBracketInDeclarationValueBlock:()=();
    pub const UnbalancedCloseCurlyBracketInDeclarationValueBlock:()=();
}
mod SelectorParseErrorKind {pub const UnexpectedIdent:()=();}
impl SubstitutionFunctionKind {
    fn from_ident(s:&str)->Result<Self,()> {
        cssparser::match_ignore_ascii_case! {s,"var"=>Ok(Self::Var),"env"=>Ok(Self::Env),"attr"=>Ok(Self::Attr),_=>Err(())}
    }
}
#[derive(Default)] struct AttrTaint(Vec<(usize,usize)>);
impl AttrTaint {fn push(&mut self,start:usize,end:usize) {self.0.push((start,end));}}
type ComputedValue = VariableValue;
type PropertyIdRef = ();
struct ComputedSubstitutionFunctions {present:bool}
struct Stylist;
mod computed {pub struct Context;}
struct AttributeTracker;
