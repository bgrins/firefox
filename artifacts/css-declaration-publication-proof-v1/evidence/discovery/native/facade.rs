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
fn parse_attr_type(input:&mut Parser)->AttributeType {
    let state=input.state();
    let accepted=matches!(input.next(),Err(_)|Ok(Token::Comma));
    input.reset(&state);
    assert!(accepted,"typed attribute outside witness");
    AttributeType::None
}
mod StyleParseErrorKind {
    pub const UnspecifiedError:()=();
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

mod style_traits {pub struct StyleParseErrorKind; impl StyleParseErrorKind {pub const UnspecifiedError:()=();}}
type SourcePropertyDeclaration = Vec<&'static str>;
struct Namespaces { prefixes: FxHashMap<Prefix,Namespace> }
struct ParserContext<'a> { namespaces: Namespaces, url_data: &'a UrlExtraData }
enum CSSWideKeyword { Initial }
impl CSSWideKeyword {fn from_ident(s:&str)->Result<Self,()> {if s.eq_ignore_ascii_case("initial"){Ok(Self::Initial)}else{Err(())}}}
mod custom_properties {pub use super::VariableValue;}
const ARBITRARY_SUBSTITUTION_FUNCTIONS:&[&str]=&["var","env","attr"];
type ArcSlice<T> = Vec<T>;
type OwnedStr = String;
struct LinkParamValue(String);
struct LinkParam {name:DashedIdent,value:LinkParamValue}
struct LinkParameters(ArcSlice<LinkParam>);
impl LinkParameters {fn none()->Self {Self(vec![])}}
trait Parse:Sized {fn parse(context:&ParserContext,input:&mut Parser)->Result<Self,ParseError>;}
struct DashedIdent(String);
impl Parse for DashedIdent {fn parse(_:&ParserContext,input:&mut Parser)->Result<Self,ParseError> {let name=input.expect_ident_cloned()?;if name.starts_with("--") && name.len()>2 {Ok(Self(name.to_string()))}else{Err(ParseError::custom(()))}}}
