use std::cell::{Cell, RefCell};
use std::collections::HashSet;
type DeclarationIndex = u32;
bitflags! { #[derive(Clone,Copy,Debug,Default,PartialEq,Eq)] struct RuleCascadeFlags:u8 { const APPEARANCE_BASE=1; } }
#[derive(Clone,Copy,Debug,PartialEq,Eq,Hash)]
enum LonghandId { FontFamily, XTextScale, FontSize, FontWeight, Appearance, Display, Content }
#[derive(Clone,Copy,Debug)]
enum PrioritaryPropertyId { FontSize, FontWeight, Appearance, XTextScale, FontFamily }
#[derive(Default)] struct PrioritaryPropertyIdSet(HashSet<LonghandId>);
impl PrioritaryPropertyIdSet {fn contains(&self,id:PrioritaryPropertyId)->bool{self.0.contains(&id.to_longhand())}}
impl PrioritaryPropertyId {
    fn from_longhand(id:LonghandId)->Option<Self>{match id {LonghandId::FontFamily=>Some(Self::FontFamily),LonghandId::XTextScale=>Some(Self::XTextScale),LonghandId::FontSize=>Some(Self::FontSize),LonghandId::FontWeight=>Some(Self::FontWeight),LonghandId::Appearance=>Some(Self::Appearance),_=>None}}
    fn to_longhand(self)->LonghandId{match self{Self::FontFamily=>LonghandId::FontFamily,Self::XTextScale=>LonghandId::XTextScale,Self::FontSize=>LonghandId::FontSize,Self::FontWeight=>LonghandId::FontWeight,Self::Appearance=>LonghandId::Appearance}}
}
#[derive(Clone,Copy,Debug,PartialEq,Eq)] enum RevertKind { Origin, Layer, Rule }
#[derive(Clone,Copy,Debug,PartialEq,Eq)] struct CascadePriority { level:u8, flags:RuleCascadeFlags }
impl CascadePriority {
    fn flags(&self)->RuleCascadeFlags{self.flags}
    fn allows_when_reverted(&self,other:&Self,_:RevertKind)->bool{other.level<self.level}
}
#[derive(Clone,Copy,Debug,PartialEq,Eq)] enum CSSWideKeyword { Initial, Inherit, Unset, Revert, RevertLayer, RevertRule }
impl CSSWideKeyword {
    fn revert_kind(self)->Option<RevertKind>{match self{Self::Revert=>Some(RevertKind::Origin),Self::RevertLayer=>Some(RevertKind::Layer),Self::RevertRule=>Some(RevertKind::Rule),_=>None}}
    fn parse(input:&mut Parser)->Result<Self,ParseError>{
        let v=input.expect_ident()?.to_string();
        let value=match v.as_str(){"initial"=>Self::Initial,"inherit"=>Self::Inherit,"unset"=>Self::Unset,"revert"=>Self::Revert,"revert-layer"=>Self::RevertLayer,"revert-rule"=>Self::RevertRule,_=>return Err(ParseError::custom(()))};
        input.expect_exhausted()?;Ok(value)
    }
}
#[derive(Clone)] struct VariableDeclaration { id:LonghandId,value:Arc<UnparsedValue> }
#[derive(Clone)] struct UnparsedValue {variable_value:VariableValue,from_shorthand:Option<ShorthandId>}
impl UnparsedValue {fn substitution_property_id(&self,_:LonghandId)->PropertyIdRef<'static>{PropertyIdRef::NonCustom(0)}}
#[derive(Clone)] enum PropertyDeclaration { WithVariables(VariableDeclaration), Number(LonghandId,f32), Wide(LonghandId,CSSWideKeyword) }
impl PropertyDeclaration {
    fn css_wide_keyword(id:LonghandId,k:CSSWideKeyword)->Self{Self::Wide(id,k)}
    fn get_css_wide_keyword(&self)->Option<CSSWideKeyword>{match self{Self::Wide(_,k)=>Some(*k),_=>None}}
    fn id(&self)->PropertyDeclarationId{PropertyDeclarationId(match self{Self::WithVariables(v)=>v.id,Self::Number(id,_)|Self::Wide(id,_)=>*id})}
}
struct PropertyDeclarationId(LonghandId);
impl PropertyDeclarationId{fn as_longhand(&self)->Option<LonghandId>{Some(self.0)}}
#[derive(Clone,Copy)] struct Declaration<'a>{decl:&'a PropertyDeclaration,priority:CascadePriority,next_index:DeclarationIndex}
#[derive(Clone,Copy)] struct DeclarationPosition{most_important:DeclarationIndex}
struct Declarations<'a>{longhand_declarations:Vec<Declaration<'a>>,prioritary_positions:[DeclarationPosition;5]}
fn next_font_declaration(_: &Declarations,_:LonghandId,_:usize)->Option<usize>{None}
fn is_synthesis_longhand(_:LonghandId)->bool{false}
#[derive(Default)]struct LonghandSet(HashSet<LonghandId>);
impl LonghandSet{fn contains(&self,id:LonghandId)->bool{self.0.contains(&id)}}
#[derive(Default)]struct Seen{longhands:LonghandSet}
#[derive(Default)]struct Reverted{longhands:FxHashMap<LonghandId,(CascadePriority,RevertKind)>}
#[derive(Default)]struct Cascade<'a>{seen:Seen,reverted:Reverted,ensured_prioritary:PrioritaryPropertyIdSet,marker:std::marker::PhantomData<&'a ()>}
#[derive(Default)]struct CacheConditions{marks:usize}
impl CacheConditions{fn set_uncacheable(&mut self){self.marks+=1}}
struct ComputedValueFlags;
impl ComputedValueFlags{const DISPLAY_OR_CONTENT_DEPEND_ON_INHERITED_STYLE:u8=1;}
#[derive(Default)]struct Builder{invalid_non_custom_properties:LonghandSet,writing_mode:(),flags:usize}
impl Builder{fn add_flags(&mut self,_:u8){self.flags+=1}}
mod computed {use super::*;#[derive(Default)]pub struct Context{pub in_container_query:bool,pub included_cascade_flags:RuleCascadeFlags,pub builder:Builder,pub rule_cache_conditions:RefCell<CacheConditions>,pub quirks_mode:bool}}
#[derive(Clone,Copy,Debug,PartialEq,Eq,Hash)]enum ShorthandId{Font}
type ShorthandsWithPropertyReferencesCache=FxHashMap<(ShorthandId,LonghandId),(Arc<UnparsedValue>,PropertyDeclaration)>;
struct Origin;impl Origin{const Author:()=();}
struct ParsingMode;impl ParsingMode{const DEFAULT:()=();}
struct ParserContext{taint:AttrTaint}
impl ParserContext {
    fn new(_:(),_:&UrlExtraData,_:Option<()>,_:(),_:bool,_:(),_:Option<()>,_:Option<()>,taint:AttrTaint)->Self{Self{taint}}
    fn with_property_declaration<T>(&self,_:PropertyIdRef,f:impl FnOnce(&Self)->T)->T{f(self)}
}
thread_local!{static PARSES:Cell<usize>=const{Cell::new(0)};static LAST_TAINT:RefCell<Vec<(usize,usize)>>=const{RefCell::new(Vec::new())};}
impl LonghandId {
    fn inherited(self)->bool{matches!(self,Self::FontSize|Self::FontWeight)}
    fn is_logical(self)->bool{false}
    fn to_physical(self,_:())->Self{self}
    fn parse_value(self,context:&ParserContext,input:&mut Parser)->Result<PropertyDeclaration,ParseError>{
        PARSES.with(|n|n.set(n.get()+1));
        LAST_TAINT.with(|v|*v.borrow_mut()=context.taint.0.iter().map(|r|(r.start,r.end)).collect());
        let n=match input.next()?{Token::Dimension{value,unit,..} if unit.as_ref()=="px"=>*value,Token::Number{value,..}=>*value,_=>return Err(ParseError::custom(()))};
        Ok(PropertyDeclaration::Number(self,n))
    }
}
#[derive(Default)]struct SourcePropertyDeclaration{declarations:Vec<PropertyDeclaration>}
impl ShorthandId {
    fn parse_into(self,decls:&mut SourcePropertyDeclaration,context:&ParserContext,input:&mut Parser)->Result<(),ParseError>{
        decls.declarations.push(input.parse_entirely(|input|LonghandId::FontSize.parse_value(context,input))?);Ok(())
    }
}
