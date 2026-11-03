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
#[derive(Clone,PartialEq)] enum PropertyId { Custom(Name), NonCustom(u8) }
#[derive(Clone,Copy)] enum PropertyIdRef<'a> { Custom(&'a Name), NonCustom(u8) }
impl<'a> From<&'a PropertyId> for PropertyIdRef<'a> { fn from(id:&'a PropertyId)->Self {match id {PropertyId::Custom(n)=>Self::Custom(n),PropertyId::NonCustom(id)=>Self::NonCustom(*id)}} }
impl<'a> From<&'a Name> for PropertyIdRef<'a> { fn from(n:&'a Name)->Self {Self::Custom(n)} }
#[derive(Clone, Debug, PartialEq)] struct UrlExtraData(u8);
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
    fn universal(value:Arc<VariableValue>)->Self{Self{value:(*value).clone(),attr_tainted:false}}
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
#[derive(Default)] struct Device { values:FxHashMap<Name,VariableValue>, contextual:FxHashMap<(Name,u8),VariableValue> }
impl Device {
    fn environment(&self)->&Self {self}
    fn get(&self,name:&Name,_:&Device,url:&UrlExtraData)->Option<VariableValue> {self.contextual.get(&(name.clone(),url.0)).or_else(||self.values.get(name)).cloned()}
}
#[derive(Default)] struct Stylist {device:Device}
impl Stylist {
    fn device(&self)->&Device {&self.device}
    fn get_custom_property_registration(&self,_:&Name)->&() {&()}
}

#[derive(Default)] struct AttributeTracker {values:FxHashMap<Name,String>, queries:Vec<String>}
impl AttributeTracker {
    fn query(&mut self,name:&str,namespace:&Namespace)->Option<String> {
        self.queries.push(format!("{namespace}:{name}"));self.values.get(name).cloned()
    }
}
struct LocalName;
impl LocalName {fn with_name<T>(name:&Name,f:impl FnOnce(&str)->T)->T {f(name)}}

#[derive(Clone,Debug,PartialEq)]
pub struct AttrTaintedRange {
    /// Start of the range, counted in bytes. Inclusive.
    start: usize,
    /// End of the range, counted in bytes. Exclusive.
    end: usize,
}

#[derive(Clone,Debug)]
pub struct VariableValue {
    /// The raw CSS string.
    pub css: String,

    /// The url data of the stylesheet where this value came from.
    pub url_data: UrlExtraData,

    first_token_type: TokenSerializationType,
    last_token_type: TokenSerializationType,

    /// var(), env(), attr() or non-custom property (e.g. through `em`) references.
    pub references: References,

    /// Was this variable value attr tainted before. Used to keep attr tainting
    /// information when uncomputing a style that needs to be put back into the
    /// cascade.
    pub explicitly_attr_tainted: bool,
}

#[derive(Clone,Debug)]
pub struct VariableFallback {
    // NOTE(emilio): We don't track fallback end, because we rely on the missing closing
    // parenthesis, if any, to be inserted, which means that we can rely on our end being
    // reference.end - 1.
    start: num::NonZeroUsize,
    first_token_type: TokenSerializationType,
    last_token_type: TokenSerializationType,
    /// References from this fallback value.
    pub references: References,
}

#[derive(Clone,Debug)]
pub struct SubstitutionFunctionReference {
    /// The identifier for this substitution function (the first argument).
    pub name: Name,
    start: usize,
    end: usize,
    /// The fallback for this function, if any.
    pub fallback: Option<VariableFallback>,
    /// attr() specific data, only relevant if substitution_kind is `Attr`..
    pub attribute_data: AttributeData,
    prev_token_type: TokenSerializationType,
    next_token_type: TokenSerializationType,
    /// The kind of substitution function we are.
    pub substitution_kind: SubstitutionFunctionKind,
}

#[derive(Clone,Debug,Default)]
pub struct References {
    /// The actual list of references that we end up with.
    pub refs: Vec<SubstitutionFunctionReference>,
    /// Various flags about the kind of references we hold. Note that these include data about our
    /// nested references.
    ///
    /// TODO(emilio): Do we need to distinguish between own and nested flags?
    pub flags: ReferenceFlags,
}

#[derive(Copy,Clone,Debug,PartialEq,Eq)]
pub enum SubstitutionFunctionKind {
    /// CSS variable / custom property
    Var,
    /// Environment variable
    Env,
    /// DOM attribute
    Attr,
}

#[derive(Clone,Debug,PartialEq)]
enum AttributeType {
    Invalid,
    None,
    RawString,
    Type(SyntaxDescriptor),
    Unit(AttrUnit),
}

#[derive(Clone,Debug,PartialEq)]
pub struct AttributeData {
    kind: AttributeType,
    namespace: ParsedNamespace,
}

#[derive(Debug,Default)]
struct Substitution<'a> {
    css: Cow<'a, str>,
    first_token_type: TokenSerializationType,
    last_token_type: TokenSerializationType,
    attr_tainted: bool,
}

#[derive(Debug)]
pub struct SubstitutionResult<'a> {
    /// The resolved CSS string after substitution.
    pub css: Cow<'a, str>,
    /// Regions in the `css` string that are attr()-tainted, if any.
    pub attr_taint: AttrTaint,
}
#[derive(Clone,Debug,Default)]
pub struct AttrTaint(SmallVec<[AttrTaintedRange; 1]>);
impl AttrTaintedRange {
    /// Creates a range within a CSS string that is tainted by attr().
    #[inline(always)]
    pub fn new(start: usize, end: usize) -> Self {
        debug_assert!(start <= end);
        Self { start, end }
    }
}
impl AttrTaint {
    /// For a CSS string, determine whether any `<url>` overlapping this `range`
    /// is disallowed due to attr()-tainting.
    #[inline(always)]
    pub fn should_disallow_urls_in_range(&self, range: &AttrTaintedRange) -> bool {
        self.0
            .iter()
            .any(|r| r.start.max(range.start) < r.end.min(range.end))
    }

    /// Returns true if the attr()-tainted range contains no elements.
    #[inline(always)]
    pub fn is_empty(&self) -> bool {
        self.0.is_empty()
    }

    #[inline(always)]
    fn new_fully_tainted(end: usize) -> Self {
        let mut taint = Self::default();
        taint.push(0, end);
        taint
    }

    #[inline(always)]
    fn push(&mut self, start: usize, end: usize) {
        self.0.push(AttrTaintedRange::new(start, end));
    }
}
impl AttributeData {
    pub(crate) fn non_type_primary_is_valid(
        &self,
        name: &Name,
        attribute_tracker: &mut AttributeTracker,
    ) -> bool {
        let namespace = match &self.namespace {
            ParsedNamespace::Known(namespace) => namespace,
            ParsedNamespace::Unknown => return false,
        };
        let Some(value) = LocalName::with_name(name, |local_name| {
            attribute_tracker.query(local_name, namespace)
        }) else {
            return false;
        };
        match &self.kind {
            AttributeType::None | AttributeType::RawString => true,
            AttributeType::Unit(_) => parse_attr_number(&mut Parser::new(&value)).is_ok(),
            AttributeType::Invalid => false,
            AttributeType::Type(_) => unreachable!("Typed attributes require substitution"),
        }
    }

    pub(crate) fn parse_typed_value(
        &self,
        input: &mut Parser,
        url_data: &UrlExtraData,
        property_id: Option<PropertyIdRef>,
    ) -> Result<SpecifiedRegisteredValue, ()> {
        let AttributeType::Type(syntax) = &self.kind else {
            return Err(());
        };
        SpecifiedRegisteredValue::parse(
            input,
            syntax,
            url_data,
            None,
            AllowComputationallyDependent::Yes,
            AttrTaint::default(),
            property_id,
        )
        .map_err(|_| ())
    }

    /// The resolved namespace, including the null namespace.
    pub fn namespace(&self) -> Option<&Namespace> {
        match &self.namespace {
            ParsedNamespace::Known(namespace) => Some(namespace),
            ParsedNamespace::Unknown => None,
        }
    }
}
impl SubstitutionFunctionReference {
    /// Whether we're an attr(... type(...)) reference.
    pub fn is_attr_with_type(&self) -> bool {
        self.substitution_kind == SubstitutionFunctionKind::Attr
            && matches!(self.attribute_data.kind, AttributeType::Type(..))
    }
}
#[derive(Clone,Copy,Debug,Default,PartialEq,Eq)]
pub struct ReferenceFlags(u16);
bitflags! {
    impl ReferenceFlags : u16 {
        /// At least one custom property depends on font-relative units.
        const FONT_UNITS = 1 << 0;
        /// At least one custom property depends on root element's font-relative units.
        const ROOT_FONT_UNITS = 1 << 1;
        /// At least one custom property depends on line height units.
        const LH_UNITS = 1 << 2;
        /// At least one custom property depends on root element's line height units.
        const ROOT_LH_UNITS = 1 << 3;
        /// The value depends on the used color-scheme (e.g. a registered `<color>` property).
        const COLOR_SCHEME = 1 << 4;
        const FONT_METRICS = 1 << 8;
        const ROOT_FONT_METRICS = 1 << 9;
        const FONT_ORIENTATION = 1 << 10;
        const ROOT_FONT_ORIENTATION = 1 << 11;
        /// All dependencies not depending on the root element.
        const NON_ROOT_DEPENDENCIES = Self::FONT_UNITS.0 | Self::LH_UNITS.0 | Self::FONT_METRICS.0 | Self::FONT_ORIENTATION.0;
        /// All dependencies depending on the root element.
        const ROOT_DEPENDENCIES = Self::ROOT_FONT_UNITS.0 | Self::ROOT_LH_UNITS.0 | Self::ROOT_FONT_METRICS.0 | Self::ROOT_FONT_ORIENTATION.0;
        /// All non-custom dependencies
        const NON_CUSTOM = Self::NON_ROOT_DEPENDENCIES.0 | Self::ROOT_DEPENDENCIES.0;
        /// At least one attr() reference.
        const ATTR = 1 << 5;
        /// At least one env() reference.
        const ENV = 1 << 6;
        /// At least one var() reference.
        const VAR = 1 << 7;
    }
}
impl ReferenceFlags {
    fn from_unit(value: &CowRcStr) -> Self {
        // For registered properties, any reference to font-relative dimensions
        // make it dependent on font-related properties.
        // TODO(dshin): When we unit algebra gets implemented and handled -
        // Is it valid to say that `calc(1em / 2em * 3px)` triggers this?
        if value.eq_ignore_ascii_case(NoCalcLength::LH) {
            return Self::FONT_UNITS | Self::LH_UNITS | Self::FONT_METRICS | Self::FONT_ORIENTATION;
        }
        if value.eq_ignore_ascii_case(NoCalcLength::EM) {
            return Self::FONT_UNITS;
        }
        if value.eq_ignore_ascii_case(NoCalcLength::EX)
            || value.eq_ignore_ascii_case(NoCalcLength::CAP)
        {
            return Self::FONT_UNITS | Self::FONT_METRICS;
        }
        if value.eq_ignore_ascii_case(NoCalcLength::CH)
            || value.eq_ignore_ascii_case(NoCalcLength::IC)
        {
            return Self::FONT_UNITS | Self::FONT_METRICS | Self::FONT_ORIENTATION;
        }
        if value.eq_ignore_ascii_case(NoCalcLength::RLH) {
            return Self::ROOT_FONT_UNITS
                | Self::ROOT_LH_UNITS
                | Self::ROOT_FONT_METRICS
                | Self::ROOT_FONT_ORIENTATION;
        }
        if value.eq_ignore_ascii_case(NoCalcLength::REM) {
            return Self::ROOT_FONT_UNITS;
        }
        if value.eq_ignore_ascii_case(NoCalcLength::REX)
            || value.eq_ignore_ascii_case(NoCalcLength::RCAP)
        {
            return Self::ROOT_FONT_UNITS | Self::ROOT_FONT_METRICS;
        }
        if value.eq_ignore_ascii_case(NoCalcLength::RCH)
            || value.eq_ignore_ascii_case(NoCalcLength::RIC)
        {
            return Self::ROOT_FONT_UNITS | Self::ROOT_FONT_METRICS | Self::ROOT_FONT_ORIENTATION;
        }
        Self::empty()
    }
}
struct NoCalcLength;
impl NoCalcLength {
    pub const EM: &'static str = "em";
    pub const EX: &'static str = "ex";
    pub const CH: &'static str = "ch";
    pub const CAP: &'static str = "cap";
    pub const IC: &'static str = "ic";
    pub const LH: &'static str = "lh";
    pub const REM: &'static str = "rem";
    pub const REX: &'static str = "rex";
    pub const RCH: &'static str = "rch";
    pub const RCAP: &'static str = "rcap";
    pub const RIC: &'static str = "ric";
    pub const RLH: &'static str = "rlh";
}
impl VariableValue {
    fn empty(url_data: &UrlExtraData) -> Self {
        Self {
            css: String::new(),
            last_token_type: Default::default(),
            first_token_type: Default::default(),
            url_data: url_data.clone(),
            references: Default::default(),
            explicitly_attr_tainted: false,
        }
    }
    pub fn new(
        css: String,
        url_data: &UrlExtraData,
        first_token_type: TokenSerializationType,
        last_token_type: TokenSerializationType,
    ) -> Self {
        Self {
            css,
            url_data: url_data.clone(),
            first_token_type,
            last_token_type,
            references: References::default(),
            explicitly_attr_tainted: false,
        }
    }
    fn push(
        &mut self,
        css: &str,
        css_first_token_type: TokenSerializationType,
        css_last_token_type: TokenSerializationType,
        attr_taint: Option<&mut AttrTaint>,
    ) -> Result<(), ()> {
        /// Prevent values from getting terribly big since you can use custom
        /// properties exponentially.
        ///
        /// This number (2MB) is somewhat arbitrary, but silly enough that no
        /// reasonable page should hit it. We could limit by number of total
        /// substitutions, but that was very easy to work around in practice
        /// (just choose a larger initial value and boom).
        const MAX_VALUE_LENGTH_IN_BYTES: usize = 2 * 1024 * 1024;

        if self.css.len() + css.len() > MAX_VALUE_LENGTH_IN_BYTES {
            return Err(());
        }

        // This happens e.g. between two subsequent var() functions:
        // `var(--a)var(--b)`.
        //
        // In that case, css_*_token_type is nonsensical.
        if css.is_empty() {
            return Ok(());
        }

        self.first_token_type.set_if_nothing(css_first_token_type);
        // If self.first_token_type was nothing,
        // self.last_token_type is also nothing and this will be false:
        if self
            .last_token_type
            .needs_separator_when_before(css_first_token_type)
        {
            self.css.push_str("/**/")
        }
        let start = self.css.len();
        self.css.push_str(css);
        let end = self.css.len();
        if let Some(taint) = attr_taint {
            taint.push(start, end);
        }
        self.last_token_type = css_last_token_type;
        Ok(())
    }
    pub fn parse(
        input: &mut Parser,
        namespaces: Option<&FxHashMap<Prefix, Namespace>>,
        url_data: &UrlExtraData,
    ) -> Result<Self, ParseError> {
        let state = input.state();
        if !matches!(
            input.next_including_whitespace_and_comments(),
            Ok(Token::WhiteSpace(_))
        ) {
            input.reset(&state);
        }
        let mut references = References::default();
        let mut missing_closing_characters = String::new();
        let mut removed_backslash = false;
        let start_position = input.position();
        let (
            first_token_type,
            mut last_token_type,
            last_non_whitespace_token_type,
            trailing_whitespace_len,
        ) = parse_declaration_value(
            input,
            start_position,
            namespaces,
            &mut references,
            &mut missing_closing_characters,
            &mut removed_backslash,
        )?;
        let mut css = input.slice_from(start_position).to_owned();
        if !missing_closing_characters.is_empty() {
            // Unescaped backslash at EOF in a quoted string is ignored.
            if removed_backslash {
                css.pop();
            }
            css.push_str(&missing_closing_characters);
        }

        let trimmed_len = css.len().saturating_sub(trailing_whitespace_len);
        if trimmed_len != css.len() {
            css.truncate(trimmed_len);
            last_token_type = last_non_whitespace_token_type;
        }
        css.shrink_to_fit();
        references.refs.shrink_to_fit();

        Ok(Self {
            css,
            url_data: url_data.clone(),
            first_token_type,
            last_token_type,
            references,
            explicitly_attr_tainted: false,
        })
    }
    pub fn has_references(&self) -> bool {
        self.references.has_references()
    }
}
impl References {
    fn has_references(&self) -> bool {
        !self.refs.is_empty()
    }
}
pub fn parse_name(s: &str) -> Result<&str, ()> {
    if s.starts_with("--") && s.len() > 2 {
        Ok(&s[2..])
    } else {
        Err(())
    }
}
fn parse_declaration_value(
    input: &mut Parser,
    input_start: SourcePosition,
    namespaces: Option<&FxHashMap<Prefix, Namespace>>,
    references: &mut References,
    missing_closing_characters: &mut String,
    removed_backslash: &mut bool,
) -> Result<
    (
        TokenSerializationType,
        TokenSerializationType,
        TokenSerializationType,
        usize,
    ),
    ParseError,
> {
    input.parse_until_before(Delimiter::Bang | Delimiter::Semicolon, |input| {
        parse_declaration_value_block(
            input,
            input_start,
            namespaces,
            references,
            missing_closing_characters,
            removed_backslash,
        )
    })
}
fn parse_declaration_value_block(
    input: &mut Parser,
    input_start: SourcePosition,
    namespaces: Option<&FxHashMap<Prefix, Namespace>>,
    references: &mut References,
    missing_closing_characters: &mut String,
    removed_backslash: &mut bool,
) -> Result<
    (
        TokenSerializationType,
        TokenSerializationType,
        TokenSerializationType,
        usize,
    ),
    ParseError,
> {
    let mut is_first = true;
    let mut first_token_type = TokenSerializationType::Nothing;
    let mut last_token_type = TokenSerializationType::Nothing;
    let mut last_non_whitespace_token_type = TokenSerializationType::Nothing;
    let mut trailing_whitespace_len = 0;
    let mut last_token_was_backslash = false;
    let mut prev_reference_index: Option<usize> = None;
    loop {
        let token_start = input.position();
        let Ok(token) = input.next_including_whitespace_and_comments() else {
            break;
        };

        let prev_token_type = last_token_type;
        let serialization_type = token.serialization_type();
        last_token_type = serialization_type;
        trailing_whitespace_len = match token {
            // A backslash delimiter needs its following newline when reserialized.
            Token::WhiteSpace(value) if !last_token_was_backslash => value.len(),
            _ => 0,
        };
        last_token_was_backslash = matches!(token, Token::Delim('\\'));
        if !matches!(token, Token::WhiteSpace(_)) {
            last_non_whitespace_token_type = serialization_type;
        }
        if is_first {
            first_token_type = last_token_type;
            is_first = false;
        }

        macro_rules! nested {
            ($closing:expr) => {{
                let mut inner_end_position = None;
                let result = input.parse_nested_block(|input| {
                    let result = parse_declaration_value_block(
                        input,
                        input_start,
                        namespaces,
                        references,
                        missing_closing_characters,
                        removed_backslash,
                    )?;
                    inner_end_position = Some(input.position());
                    Ok(result)
                })?;
                if inner_end_position.unwrap() == input.position() {
                    missing_closing_characters.push_str($closing);
                }
                result
            }};
        }
        if let Some(index) = prev_reference_index.take() {
            references.refs[index].next_token_type = serialization_type;
        }
        match *token {
            Token::Comment(_) => {
                let token_slice = input.slice_from(token_start);
                if !token_slice.ends_with("*/") {
                    missing_closing_characters.push_str(if token_slice.ends_with('*') {
                        "/"
                    } else {
                        "*/"
                    })
                }
            }
            Token::BadUrl(..) => {
                let e = StyleParseErrorKind::BadUrlInDeclarationValueBlock;
                return Err(ParseError::custom(e));
            }
            Token::BadString(..) => {
                let e = StyleParseErrorKind::BadStringInDeclarationValueBlock;
                return Err(ParseError::custom(e));
            }
            Token::CloseParenthesis => {
                let e = StyleParseErrorKind::UnbalancedCloseParenthesisInDeclarationValueBlock;
                return Err(ParseError::custom(e));
            }
            Token::CloseSquareBracket => {
                let e = StyleParseErrorKind::UnbalancedCloseSquareBracketInDeclarationValueBlock;
                return Err(ParseError::custom(e));
            }
            Token::CloseCurlyBracket => {
                let e = StyleParseErrorKind::UnbalancedCloseCurlyBracketInDeclarationValueBlock;
                return Err(ParseError::custom(e));
            }
            Token::Function(ref name) => {
                let substitution_kind = SubstitutionFunctionKind::from_ident(name).ok();
                if let Some(substitution_kind) = substitution_kind {
                    let our_ref_index = references.refs.len();
                    let mut input_end_position = None;
                    let fallback = input.parse_nested_block(|input| {
                        let mut namespace = ParsedNamespace::Known(Namespace::default());
                        if substitution_kind == SubstitutionFunctionKind::Attr
                            && let Some(namespaces) = namespaces
                            && let Ok(ns) =
                                input.try_parse(|input| ParsedNamespace::parse(namespaces, input))
                        {
                            namespace = ns;
                            let prev = input.state();
                            let next = match *input.next_including_whitespace()? {
                                Token::Ident(_) => Ok(()),
                                _ => Err(ParseError::unexpected_token()),
                            };
                            input.reset(&prev);
                            next?;
                        }
                        // TODO(emilio): For env() this should be <custom-ident> per spec, but no other browser does
                        // that, see https://github.com/w3c/csswg-drafts/issues/3262.
                        let name = input.expect_ident()?;
                        let name =
                            Atom::from(if substitution_kind == SubstitutionFunctionKind::Var {
                                match parse_name(name.as_ref()) {
                                    Ok(name) => name,
                                    Err(()) => {
                                        return Err(ParseError::custom(
                                            SelectorParseErrorKind::UnexpectedIdent,
                                        ));
                                    }
                                }
                            } else {
                                name.as_ref()
                            });

                        let attribute_kind = if substitution_kind == SubstitutionFunctionKind::Attr
                        {
                            parse_attr_type(input)
                        } else {
                            AttributeType::None
                        };

                        // We want the order of the references to match source order. So we need to reserve our slot
                        // now, _before_ parsing our fallback. Note that we don't care if parsing fails after all, since
                        // if this fails we discard the whole result anyways.
                        let start = token_start.byte_index() - input_start.byte_index();
                        references.refs.push(SubstitutionFunctionReference {
                            name,
                            start,
                            // To be fixed up after parsing fallback and auto-closing via our_ref_index.
                            end: start,
                            prev_token_type,
                            // To be fixed up (if needed) on the next loop iteration via prev_reference_index.
                            next_token_type: TokenSerializationType::Nothing,
                            // To be fixed up after parsing fallback.
                            fallback: None,
                            attribute_data: AttributeData {
                                kind: attribute_kind,
                                namespace,
                            },
                            substitution_kind,
                        });

                        let mut fallback = None;
                        if input.try_parse(|input| input.expect_comma()).is_ok() {
                            input.skip_whitespace();
                            let fallback_start = num::NonZeroUsize::new(
                                input.position().byte_index() - input_start.byte_index(),
                            )
                            .unwrap();
                            let mut references = References::default();
                            // NOTE(emilio): Intentionally using parse_declaration_value rather than
                            // parse_declaration_value_block, since that's what parse_fallback used to do.
                            let (first, last, _, _) = parse_declaration_value(
                                input,
                                input_start,
                                namespaces,
                                &mut references,
                                missing_closing_characters,
                                removed_backslash,
                            )?;
                            fallback = Some(VariableFallback {
                                start: fallback_start,
                                first_token_type: first,
                                last_token_type: last,
                                references,
                            });
                            input_end_position = Some(input.position());
                        } else {
                            let state = input.state();
                            // We still need to consume the rest of the potentially-unclosed
                            // tokens, but make sure to not consume tokens that would otherwise be
                            // invalid, by calling reset().
                            parse_declaration_value_block(
                                input,
                                input_start,
                                namespaces,
                                references,
                                missing_closing_characters,
                                removed_backslash,
                            )?;
                            input_end_position = Some(input.position());
                            input.reset(&state);
                        }
                        Ok(fallback)
                    })?;
                    if input_end_position.unwrap() == input.position() {
                        missing_closing_characters.push(')');
                    }
                    prev_reference_index = Some(our_ref_index);
                    let reference = &mut references.refs[our_ref_index];
                    reference.end = input.position().byte_index() - input_start.byte_index()
                        + missing_closing_characters.len()
                        - usize::from(*removed_backslash);
                    reference.fallback = fallback;
                    references.flags |= match substitution_kind {
                        SubstitutionFunctionKind::Var => ReferenceFlags::VAR,
                        SubstitutionFunctionKind::Env => ReferenceFlags::ENV,
                        SubstitutionFunctionKind::Attr => ReferenceFlags::ATTR,
                    };
                    // Bubble up flags from our fallback, so we know what we might reference from the outer scope.
                    if let Some(ref fb) = reference.fallback {
                        references.flags |= fb.references.flags;
                    }
                } else {
                    nested!(")");
                }
            }
            Token::ParenthesisBlock => {
                nested!(")");
            }
            Token::CurlyBracketBlock => {
                nested!("}");
            }
            Token::SquareBracketBlock => {
                nested!("]");
            }
            Token::QuotedString(_) => {
                let token_slice = input.slice_from(token_start);
                let quote = &token_slice[..1];
                debug_assert!(matches!(quote, "\"" | "'"));
                if !(token_slice.ends_with(quote)
                    && token_slice.len() > 1
                    && token_slice[..token_slice.len() - 1]
                        .bytes()
                        .rev()
                        .take_while(|&byte| byte == b'\\')
                        .count()
                        % 2
                        == 0)
                {
                    *removed_backslash = missing_closing_characters.is_empty()
                        && token_slice
                            .bytes()
                            .rev()
                            .take_while(|&byte| byte == b'\\')
                            .count()
                            % 2
                            == 1;
                    missing_closing_characters.push_str(quote)
                }
            }
            Token::Ident(ref value)
            | Token::AtKeyword(ref value)
            | Token::Hash(ref value)
            | Token::IDHash(ref value)
            | Token::UnquotedUrl(ref value)
            | Token::Dimension {
                unit: ref value, ..
            } => {
                if matches!(token, Token::Dimension { .. }) {
                    references.flags.insert(ReferenceFlags::from_unit(value));
                }
                let is_unquoted_url = matches!(token, Token::UnquotedUrl(_));
                if value.ends_with("�") && input.slice_from(token_start).ends_with("\\") {
                    // Unescaped backslash at EOF in these contexts is interpreted as U+FFFD
                    // Check the value in case the final backslash was itself escaped.
                    // Serialize as escaped U+FFFD, which is also interpreted as U+FFFD.
                    // (Unescaped U+FFFD would also work, but removing the backslash is annoying.)
                    missing_closing_characters.push('�')
                }
                if is_unquoted_url && !input.slice_from(token_start).ends_with(")") {
                    missing_closing_characters.push(')');
                }
            }
            _ => {}
        };
    }
    Ok((
        first_token_type,
        last_token_type,
        last_non_whitespace_token_type,
        trailing_whitespace_len,
    ))
}
fn parse_attr_type(input: &mut Parser) -> AttributeType {
    input
        .try_parse(|input| {
            Ok(match input.next()? {
                Token::Function(name) if name.eq_ignore_ascii_case("type") => AttributeType::Type(
                    input.parse_nested_block(SyntaxDescriptor::from_css_parser)?,
                ),
                Token::Ident(ident) => {
                    if ident.eq_ignore_ascii_case("raw-string") {
                        AttributeType::RawString
                    } else if let Ok(unit) = AttrUnit::from_ident(ident) {
                        AttributeType::Unit(unit)
                    } else {
                        AttributeType::Invalid
                    }
                }
                Token::Delim('%') => AttributeType::Unit(AttrUnit::Percentage),
                _ => return Err(ParseError::custom(StyleParseErrorKind::UnspecifiedError)),
            })
        })
        .unwrap_or(AttributeType::None)
}
fn parse_attr_number<'i>(input: &mut Parser<'i>) -> Result<&'i str, ()> {
    input.skip_whitespace();
    let start = input.position();
    input.expect_number().map_err(|_| ())?;
    let number = input.slice_from(start);
    input.expect_exhausted().map_err(|_| ())?;
    Ok(number)
}
fn quoted_css_string(src: &str) -> String {
    let mut dest = String::with_capacity(src.len() + 2);
    cssparser::serialize_string(src, &mut dest).unwrap();
    dest
}
fn do_substitute_chunk<'a>(
    css: &'a str,
    start: usize,
    end: usize,
    first_token_type: TokenSerializationType,
    last_token_type: TokenSerializationType,
    url_data: &UrlExtraData,
    property_id: Option<PropertyIdRef>,
    substitution_functions: &'a ComputedSubstitutionFunctions,
    stylist: &Stylist,
    computed_context: &computed::Context,
    references: &'a [SubstitutionFunctionReference],
    attribute_tracker: &mut AttributeTracker,
    seen: &mut SmallVec<[&'a Name; 8]>,
    mut attr_taint: Option<&mut AttrTaint>,
) -> Result<Substitution<'a>, ()> {
    if start == end {
        // Empty string. Easy.
        return Ok(Substitution::default());
    }
    // Easy case: no references involved.
    if references.is_empty() {
        let result = &css[start..end];
        return Ok(Substitution::new(
            Cow::Borrowed(result),
            first_token_type,
            last_token_type,
            Default::default(),
        ));
    }

    let mut substituted = ComputedValue::empty(url_data);
    let mut next_token_type = first_token_type;
    let mut cur_pos = start;
    let mut attr_tainted = false;
    let references = references.iter();
    for reference in references {
        if reference.start != cur_pos {
            substituted.push(
                &css[cur_pos..reference.start],
                next_token_type,
                reference.prev_token_type,
                /* attr_taint */ None,
            )?;
        }

        let substitution = substitute_one_reference(
            css,
            url_data,
            property_id,
            substitution_functions,
            reference,
            stylist,
            computed_context,
            attribute_tracker,
            seen,
        )?;

        // Optimize the property: var(--...) case to avoid allocating at all.
        if reference.start == start && reference.end == end {
            if let Some(taint) = attr_taint.filter(|_| substitution.attr_tainted) {
                taint.push(start, substitution.css.len());
            }
            return Ok(substitution);
        }

        substituted.push(
            &substitution.css,
            substitution.first_token_type,
            substitution.last_token_type,
            attr_taint
                .as_deref_mut()
                .filter(|_| substitution.attr_tainted),
        )?;
        attr_tainted |= substitution.attr_tainted;
        next_token_type = reference.next_token_type;
        cur_pos = reference.end;
    }
    // Push the rest of the value if needed.
    if cur_pos != end {
        substituted.push(
            &css[cur_pos..end],
            next_token_type,
            last_token_type,
            /* attr_taint */ None,
        )?;
    }
    Ok(Substitution::from_value(substituted, attr_tainted))
}
fn substitute_one_reference<'a>(
    css: &'a str,
    url_data: &UrlExtraData,
    property_id: Option<PropertyIdRef>,
    substitution_functions: &'a ComputedSubstitutionFunctions,
    reference: &'a SubstitutionFunctionReference,
    stylist: &Stylist,
    computed_context: &computed::Context,
    attribute_tracker: &mut AttributeTracker,
    seen: &mut SmallVec<[&'a Name; 8]>,
) -> Result<Substitution<'a>, ()> {
    let simple_attr_subst = |s: &str| {
        Some(Substitution::new(
            Cow::Owned(quoted_css_string(s)),
            TokenSerializationType::Nothing,
            TokenSerializationType::Nothing,
            /* attr_tainted */ true,
        ))
    };
    let substitution: Option<_> = match reference.substitution_kind {
        SubstitutionFunctionKind::Var => {
            let registration = stylist.get_custom_property_registration(&reference.name);
            match substitution_functions.get_var(registration, &reference.name) {
                None => None,
                // If the referenced value is itself still unresolved (i.e. it has references), we
                // are substituting against a partially-resolved map -- this happens while applying
                // a prioritary property in the middle of custom-property resolution. Resolve it
                // recursively, guarding against cycles (which the resolver will also remove, but it
                // may not have gotten to this variable yet).
                Some(v) => match v.as_universal() {
                    Some(u) if u.has_references() => {
                        if seen.contains(&&reference.name) {
                            // Cycle: the primary is guaranteed-invalid, so fall through to the
                            // fallback (if any), like any other invalid primary.
                            None
                        } else {
                            seen.push(&reference.name);
                            let result = substitute_internal(
                                u,
                                property_id,
                                substitution_functions,
                                stylist,
                                computed_context,
                                attribute_tracker,
                                seen,
                                /* attr_taint */ None,
                            );
                            seen.pop();
                            match result {
                                Ok(mut substitution) => {
                                    substitution.attr_tainted |= v.attr_tainted;
                                    Some(substitution)
                                }
                                // The primary couldn't be resolved (invalid); use the fallback.
                                Err(()) => None,
                            }
                        }
                    }
                    _ => Some(Substitution::from_value(
                        v.to_variable_value(),
                        v.attr_tainted,
                    )),
                },
            }
        }
        SubstitutionFunctionKind::Env => {
            let device = stylist.device();
            device
                .environment()
                .get(&reference.name, device, url_data)
                .map(|v| Substitution::from_value(v, /* attr_tainted */ false))
        }
        // https://drafts.csswg.org/css-values-5/#attr-substitution
        SubstitutionFunctionKind::Attr => {
            let namespace = match reference.attribute_data.namespace {
                ParsedNamespace::Known(ref ns) => Some(ns),
                ParsedNamespace::Unknown => None,
            };
            namespace
                .and_then(|namespace| {
                    LocalName::with_name(&reference.name, |local_name| {
                        attribute_tracker.query(local_name, namespace)
                    })
                })
                .map_or_else(
                    || {
                        // Special case when fallback and <attr-type> are omitted.
                        // See FAILURE: https://drafts.csswg.org/css-values-5/#attr-substitution
                        if reference.fallback.is_none()
                            && reference.attribute_data.kind == AttributeType::None
                        {
                            simple_attr_subst("")
                        } else {
                            None
                        }
                    },
                    |attr| {
                        let attr = if let AttributeType::Type(_) = &reference.attribute_data.kind {
                            // If we're evaluating a container query, we haven't run the cascade
                            // and populated substitution_functions.attributes, so we can't do the
                            // get_attr() lookup here.
                            // TODO: This means chained attr() references will not work reliably in
                            // container style queries:
                            // https://bugzilla.mozilla.org/show_bug.cgi?id=2028861
                            if computed_context.in_container_query {
                                attr
                            } else {
                                substitution_functions
                                    .get_attr(&reference.name, namespace?)
                                    .map(|v| v.to_variable_value())?
                                    .css
                            }
                        } else {
                            attr
                        };
                        let mut parser = Parser::new(&attr);
                        match &reference.attribute_data.kind {
                            AttributeType::Unit(unit) => {
                                let css = {
                                    let mut s = String::from(parse_attr_number(&mut parser).ok()?);
                                    s.push_str(unit.as_ref());
                                    s
                                };
                                let serialization = match unit {
                                    AttrUnit::Number => TokenSerializationType::Number,
                                    AttrUnit::Percentage => TokenSerializationType::Percentage,
                                    _ => TokenSerializationType::Dimension,
                                };
                                let value =
                                    ComputedValue::new(css, url_data, serialization, serialization);
                                Some(Substitution::from_value(
                                    value, /* attr_tainted */ true,
                                ))
                            }
                            AttributeType::Type(_) => {
                                let value = reference
                                    .attribute_data
                                    .parse_typed_value(&mut parser, url_data, property_id)
                                    .ok()?;
                                let value = value.to_variable_value();
                                Some(Substitution::from_value(
                                    value, /* attr_tainted */ true,
                                ))
                            }
                            AttributeType::RawString | AttributeType::None => {
                                simple_attr_subst(&attr)
                            }
                            AttributeType::Invalid => None,
                        }
                    },
                )
        }
    };

    if let Some(s) = substitution {
        return Ok(s);
    }

    let Some(ref fallback) = reference.fallback else {
        return Err(());
    };

    do_substitute_chunk(
        css,
        fallback.start.get(),
        reference.end - 1, // Skip the closing parenthesis of the reference value.
        fallback.first_token_type,
        fallback.last_token_type,
        url_data,
        property_id,
        substitution_functions,
        stylist,
        computed_context,
        &fallback.references.refs,
        attribute_tracker,
        seen,
        /* attr_taint */ None,
    )
}
fn substitute_internal<'a>(
    variable_value: &'a VariableValue,
    property_id: Option<PropertyIdRef>,
    substitution_functions: &'a ComputedSubstitutionFunctions,
    stylist: &Stylist,
    computed_context: &computed::Context,
    attribute_tracker: &mut AttributeTracker,
    seen: &mut SmallVec<[&'a Name; 8]>,
    attr_taint: Option<&mut AttrTaint>,
) -> Result<Substitution<'a>, ()> {
    do_substitute_chunk(
        &variable_value.css,
        /* start = */ 0,
        /* end = */ variable_value.css.len(),
        variable_value.first_token_type,
        variable_value.last_token_type,
        &variable_value.url_data,
        property_id,
        substitution_functions,
        stylist,
        computed_context,
        &variable_value.references.refs,
        attribute_tracker,
        seen,
        attr_taint,
    )
}
pub fn substitute<'a>(
    variable_value: &'a VariableValue,
    property_id: Option<PropertyIdRef>,
    substitution_functions: &'a ComputedSubstitutionFunctions,
    stylist: &Stylist,
    computed_context: &computed::Context,
    attribute_tracker: &mut AttributeTracker,
) -> Result<SubstitutionResult<'a>, ()> {
    debug_assert!(variable_value.has_references());
    let mut attr_taint = AttrTaint::default();
    let v = substitute_internal(
        variable_value,
        property_id,
        substitution_functions,
        stylist,
        computed_context,
        attribute_tracker,
        &mut SmallVec::new(),
        Some(&mut attr_taint),
    )?;
    Ok(SubstitutionResult {
        css: v.css,
        attr_taint,
    })
}
impl<'a> Substitution<'a> {
    fn from_value(v: VariableValue, attr_tainted: bool) -> Self {
        Substitution {
            css: v.css.into(),
            first_token_type: v.first_token_type,
            last_token_type: v.last_token_type,
            attr_tainted,
        }
    }
    fn new(
        css: Cow<'a, str>,
        first_token_type: TokenSerializationType,
        last_token_type: TokenSerializationType,
        attr_tainted: bool,
    ) -> Self {
        Self {
            css,
            first_token_type,
            last_token_type,
            attr_tainted,
        }
    }
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) enum SubstitutionLookupKind {
    Variable,
    Environment,
    RawAttribute,
    TypedAttribute,
}

#[derive(Clone)]
pub(crate) struct SubstitutionLookup {
    pub guards: Vec<SubstitutionGuard>,
    pub identity: Arc<()>,
    pub attribute_attempt: Option<Arc<()>>,
    pub kind: SubstitutionLookupKind,
    pub name: Name,
    pub namespace: Option<Namespace>,
    pub url_data: UrlExtraData,
}

pub(crate) enum SubstitutionLookupValue {
    Pending,
    Invalid,
    Value(VariableValue, bool),
    Expand(VariableValue, bool),
    AttributeSource(VariableValue),
    Attribute(Option<String>),
}

pub(crate) struct SubstitutionLookupReply {
    pub identity: Arc<()>,
    pub value: SubstitutionLookupValue,
}

pub(crate) enum SubstitutionPoll {
    Lookup(SubstitutionLookup),
    Complete(Result<SubstitutionResult<'static>, ()>),
    WrongReply,
    Finished,
}

struct SubstitutionChunk {
    value: Arc<VariableValue>,
    start: usize,
    end: usize,
    first: TokenSerializationType,
    last: TokenSerializationType,
    references: Vec<SubstitutionFunctionReference>,
    next: usize,
    position: usize,
    next_token: TokenSerializationType,
    output: ComputedValue,
    tainted: bool,
    waiting: bool,
    root: bool,
}

impl SubstitutionChunk {
    fn whole(value: VariableValue, root: bool) -> Self {
        let end = value.css.len();
        let first = value.first_token_type;
        let last = value.last_token_type;
        let references = value.references.refs.clone();
        Self::new(Arc::new(value), 0, end, first, last, references, root)
    }

    fn new(
        value: Arc<VariableValue>,
        start: usize,
        end: usize,
        first: TokenSerializationType,
        last: TokenSerializationType,
        references: Vec<SubstitutionFunctionReference>,
        root: bool,
    ) -> Self {
        let output = ComputedValue::empty(&value.url_data);
        Self {
            value,
            start,
            end,
            first,
            last,
            references,
            next: 0,
            position: start,
            next_token: first,
            output,
            tainted: false,
            waiting: false,
            root,
        }
    }
}

enum SubstitutionReferenceStage {
    Start,
    Lookup(SubstitutionLookupKind),
    Alias(bool),
    AttributeBody(Arc<()>),
    Fallback,
}

struct SubstitutionReferenceFrame {
    value: Arc<VariableValue>,
    reference: SubstitutionFunctionReference,
    stage: SubstitutionReferenceStage,
    raw_attribute: Option<String>,
}

enum SubstitutionFrame {
    Chunk(SubstitutionChunk),
    Reference(SubstitutionReferenceFrame),
}

#[derive(Clone, PartialEq)]
pub(crate) enum SubstitutionGuardKey {
    Attribute(Name, Namespace),
    Property(PropertyId),
}

#[derive(Clone)]
pub(crate) struct SubstitutionGuard {
    pub identity: Arc<()>,
    pub key: SubstitutionGuardKey,
    marked: Arc<std::sync::atomic::AtomicBool>,
}

impl SubstitutionGuard {
    pub(crate) fn new(key: SubstitutionGuardKey) -> Self {
        Self {
            identity: Arc::new(()),
            key,
            marked: Arc::new(std::sync::atomic::AtomicBool::new(false)),
        }
    }

    pub(crate) fn marked(&self) -> bool {
        self.marked.load(std::sync::atomic::Ordering::Relaxed)
    }

    pub(crate) fn mark_reentry(guards: &[Self], key: &SubstitutionGuardKey) -> bool {
        let Some(start) = guards.iter().position(|guard| &guard.key == key) else {
            return false;
        };
        for guard in &guards[start..] {
            guard
                .marked
                .store(true, std::sync::atomic::Ordering::Relaxed);
        }
        true
    }
}

pub(crate) struct ResumableSubstitution<'a> {
    frames: Vec<SubstitutionFrame>,
    seen: Vec<Name>,
    guards: Vec<SubstitutionGuard>,
    root_guard: Option<SubstitutionGuard>,
    owned_property_id: Option<PropertyId>,
    returned: Option<Result<Substitution<'static>, ()>>,
    request: Option<SubstitutionLookup>,
    lookup_value: Option<SubstitutionLookupValue>,
    property_id: Option<PropertyIdRef<'a>>,
    in_container_query: bool,
    taint: AttrTaint,
    finished: bool,
}

impl<'a> ResumableSubstitution<'a> {
    pub(crate) fn new(
        value: VariableValue,
        property_id: Option<PropertyIdRef<'a>>,
        in_container_query: bool,
    ) -> Self {
        Self {
            frames: vec![SubstitutionFrame::Chunk(SubstitutionChunk::whole(
                value, true,
            ))],
            seen: Vec::new(),
            guards: Vec::new(),
            root_guard: None,
            owned_property_id: None,
            returned: None,
            request: None,
            lookup_value: None,
            property_id,
            in_container_query,
            taint: AttrTaint::default(),
            finished: false,
        }
    }

    pub(crate) fn for_custom(
        value: VariableValue,
        name: Name,
        guards: Vec<SubstitutionGuard>,
    ) -> Self {
        Self::for_guarded_property(value, PropertyId::Custom(name), guards, false)
    }

    pub(crate) fn for_property(
        value: VariableValue,
        property: PropertyIdRef,
        in_container_query: bool,
    ) -> Self {
        let property = match property {
            PropertyIdRef::Custom(name) => PropertyId::Custom(name.clone()),
            PropertyIdRef::NonCustom(id) => PropertyId::NonCustom(id),
        };
        Self::for_guarded_property(value, property, Vec::new(), in_container_query)
    }

    fn for_guarded_property(
        value: VariableValue,
        property: PropertyId,
        mut guards: Vec<SubstitutionGuard>,
        in_container_query: bool,
    ) -> Self {
        let guard = SubstitutionGuard::new(SubstitutionGuardKey::Property(property.clone()));
        guards.push(guard.clone());
        let mut state = Self::new(value, None, in_container_query);
        state.guards = guards;
        state.root_guard = Some(guard);
        state.owned_property_id = Some(property);
        state
    }

    pub(crate) fn body_marked(&self) -> bool {
        self.root_guard
            .as_ref()
            .is_some_and(SubstitutionGuard::marked)
    }

    fn request(&mut self, frame: &mut SubstitutionReferenceFrame, kind: SubstitutionLookupKind) {
        let namespace = frame.reference.attribute_data.namespace().cloned();
        self.request = Some(SubstitutionLookup {
            identity: Arc::new(()),
            guards: self.guards.clone(),
            attribute_attempt: self.guards.iter().rev().find_map(|guard| {
                matches!(guard.key, SubstitutionGuardKey::Attribute(..))
                    .then(|| guard.identity.clone())
            }),
            kind,
            name: frame.reference.name.clone(),
            namespace,
            url_data: frame.value.url_data.clone(),
        });
        frame.stage = SubstitutionReferenceStage::Lookup(kind);
    }

    fn invalid_primary(&mut self, mut frame: SubstitutionReferenceFrame) {
        let Some(fallback) = frame.reference.fallback.as_ref() else {
            self.returned = Some(Err(()));
            return;
        };
        let child = SubstitutionChunk::new(
            frame.value.clone(),
            fallback.start.get(),
            frame.reference.end - 1,
            fallback.first_token_type,
            fallback.last_token_type,
            fallback.references.refs.clone(),
            false,
        );
        frame.stage = SubstitutionReferenceStage::Fallback;
        self.frames.push(SubstitutionFrame::Reference(frame));
        self.frames.push(SubstitutionFrame::Chunk(child));
    }

    fn begin_attribute_body(
        &mut self,
        mut frame: SubstitutionReferenceFrame,
        value: VariableValue,
    ) {
        let namespace = frame.reference.attribute_data.namespace().unwrap().clone();
        let key = SubstitutionGuardKey::Attribute(frame.reference.name.clone(), namespace);
        if SubstitutionGuard::mark_reentry(&self.guards, &key) {
            self.invalid_primary(frame);
            return;
        }
        let guard = SubstitutionGuard::new(key);
        let identity = guard.identity.clone();
        self.guards.push(guard);
        frame.stage = SubstitutionReferenceStage::AttributeBody(identity);
        self.frames.push(SubstitutionFrame::Reference(frame));
        self.frames
            .push(SubstitutionFrame::Chunk(SubstitutionChunk::whole(
                value, false,
            )));
    }

    fn attribute_value(
        &self,
        frame: &SubstitutionReferenceFrame,
        text: &str,
    ) -> Option<Substitution<'static>> {
        let reference = &frame.reference;
        let mut parser = Parser::new(text);
        match &reference.attribute_data.kind {
            AttributeType::Unit(unit) => {
                let mut css = String::from(parse_attr_number(&mut parser).ok()?);
                css.push_str(unit.as_ref());
                let serialization = match unit {
                    AttrUnit::Number => TokenSerializationType::Number,
                    AttrUnit::Percentage => TokenSerializationType::Percentage,
                    _ => TokenSerializationType::Dimension,
                };
                let value =
                    ComputedValue::new(css, &frame.value.url_data, serialization, serialization);
                Some(Substitution::from_value(value, true))
            }
            AttributeType::Type(_) => {
                let value = reference
                    .attribute_data
                    .parse_typed_value(
                        &mut parser,
                        &frame.value.url_data,
                        self.owned_property_id
                            .as_ref()
                            .map(PropertyIdRef::from)
                            .or(self.property_id),
                    )
                    .ok()?;
                Some(Substitution::from_value(value.to_variable_value(), true))
            }
            AttributeType::RawString | AttributeType::None => Some(Substitution::new(
                Cow::Owned(quoted_css_string(text)),
                TokenSerializationType::Nothing,
                TokenSerializationType::Nothing,
                true,
            )),
            AttributeType::Invalid => None,
        }
    }

    pub(crate) fn poll(&mut self, reply: Option<SubstitutionLookupReply>) -> SubstitutionPoll {
        if self.finished {
            return SubstitutionPoll::Finished;
        }
        if let Some(reply) = reply {
            let Some(request) = self.request.as_ref() else {
                return SubstitutionPoll::WrongReply;
            };
            if !std::ptr::eq(request.identity.as_ref(), reply.identity.as_ref()) {
                return SubstitutionPoll::WrongReply;
            }
            if matches!(reply.value, SubstitutionLookupValue::Pending) {
                return SubstitutionPoll::Lookup(request.clone());
            }
            let shape_matches = match (&request.kind, &reply.value) {
                (SubstitutionLookupKind::RawAttribute, SubstitutionLookupValue::Attribute(_)) => {
                    true
                }
                (SubstitutionLookupKind::RawAttribute, _) => false,
                (SubstitutionLookupKind::Variable, SubstitutionLookupValue::Expand(..)) => true,
                (
                    SubstitutionLookupKind::TypedAttribute,
                    SubstitutionLookupValue::AttributeSource(value),
                ) => value.url_data == request.url_data,
                (SubstitutionLookupKind::Variable, SubstitutionLookupValue::Value(value, _)) => {
                    !value.has_references()
                }
                (_, SubstitutionLookupValue::Invalid | SubstitutionLookupValue::Value(..)) => true,
                _ => false,
            };
            if !shape_matches {
                return SubstitutionPoll::WrongReply;
            }
            self.request = None;
            self.lookup_value = Some(reply.value);
        }
        if let Some(request) = self.request.as_ref() {
            return SubstitutionPoll::Lookup(request.clone());
        }
        loop {
            let Some(frame) = self.frames.pop() else {
                self.finished = true;
                let mut result = self.returned.take().expect("root substitution completed");
                if self.body_marked() {
                    result = Err(());
                }
                return SubstitutionPoll::Complete(result.map(|value| SubstitutionResult {
                    css: value.css,
                    attr_taint: std::mem::take(&mut self.taint),
                }));
            };
            match frame {
                SubstitutionFrame::Chunk(mut chunk) => {
                    if chunk.waiting {
                        let result = self.returned.take().expect("reference completed");
                        let Ok(substitution) = result else {
                            self.returned = Some(Err(()));
                            continue;
                        };
                        let reference = &chunk.references[chunk.next];
                        if reference.start == chunk.start && reference.end == chunk.end {
                            if chunk.root && substitution.attr_tainted {
                                self.taint.push(chunk.start, substitution.css.len());
                            }
                            self.returned = Some(Ok(substitution));
                            continue;
                        }
                        if chunk
                            .output
                            .push(
                                &substitution.css,
                                substitution.first_token_type,
                                substitution.last_token_type,
                                (chunk.root && substitution.attr_tainted)
                                    .then_some(&mut self.taint),
                            )
                            .is_err()
                        {
                            self.returned = Some(Err(()));
                            continue;
                        }
                        chunk.tainted |= substitution.attr_tainted;
                        chunk.next_token = reference.next_token_type;
                        chunk.position = reference.end;
                        chunk.next += 1;
                        chunk.waiting = false;
                    }
                    if chunk.start == chunk.end {
                        self.returned = Some(Ok(Substitution::default()));
                        continue;
                    }
                    if chunk.references.is_empty() {
                        self.returned = Some(Ok(Substitution::new(
                            Cow::Owned(chunk.value.css[chunk.start..chunk.end].to_owned()),
                            chunk.first,
                            chunk.last,
                            false,
                        )));
                        continue;
                    }
                    if let Some(reference) = chunk.references.get(chunk.next).cloned() {
                        if reference.start != chunk.position
                            && chunk
                                .output
                                .push(
                                    &chunk.value.css[chunk.position..reference.start],
                                    chunk.next_token,
                                    reference.prev_token_type,
                                    None,
                                )
                                .is_err()
                        {
                            self.returned = Some(Err(()));
                            continue;
                        }
                        let child = SubstitutionReferenceFrame {
                            value: chunk.value.clone(),
                            reference,
                            stage: SubstitutionReferenceStage::Start,
                            raw_attribute: None,
                        };
                        chunk.waiting = true;
                        self.frames.push(SubstitutionFrame::Chunk(chunk));
                        self.frames.push(SubstitutionFrame::Reference(child));
                        continue;
                    }
                    if chunk.position != chunk.end
                        && chunk
                            .output
                            .push(
                                &chunk.value.css[chunk.position..chunk.end],
                                chunk.next_token,
                                chunk.last,
                                None,
                            )
                            .is_err()
                    {
                        self.returned = Some(Err(()));
                    } else {
                        self.returned =
                            Some(Ok(Substitution::from_value(chunk.output, chunk.tainted)));
                    }
                }
                SubstitutionFrame::Reference(mut frame) => {
                    match frame.stage {
                        SubstitutionReferenceStage::Start => {
                            let kind = match frame.reference.substitution_kind {
                                SubstitutionFunctionKind::Var => SubstitutionLookupKind::Variable,
                                SubstitutionFunctionKind::Env => {
                                    SubstitutionLookupKind::Environment
                                }
                                SubstitutionFunctionKind::Attr => {
                                    SubstitutionLookupKind::RawAttribute
                                }
                            };
                            self.request(&mut frame, kind);
                        }
                        SubstitutionReferenceStage::Alias(tainted) => {
                            assert_eq!(self.seen.pop().as_ref(), Some(&frame.reference.name));
                            match self.returned.take().expect("alias completed") {
                                Ok(mut value) => {
                                    value.attr_tainted |= tainted;
                                    self.returned = Some(Ok(value));
                                }
                                Err(()) => self.invalid_primary(frame),
                            }
                            continue;
                        }
                        SubstitutionReferenceStage::AttributeBody(ref identity) => {
                            let attempt = self.guards.pop().expect("attribute body completed");
                            assert!(Arc::ptr_eq(&attempt.identity, identity));
                            assert!(
                                attempt.key
                                    == SubstitutionGuardKey::Attribute(
                                        frame.reference.name.clone(),
                                        frame.reference.attribute_data.namespace().unwrap().clone(),
                                    )
                            );
                            let result = self.returned.take().expect("attribute body result");
                            let value = if attempt.marked() {
                                None
                            } else {
                                result
                                    .ok()
                                    .and_then(|value| self.attribute_value(&frame, &value.css))
                            };
                            match value {
                                Some(value) => self.returned = Some(Ok(value)),
                                None => self.invalid_primary(frame),
                            }
                            continue;
                        }
                        SubstitutionReferenceStage::Fallback => continue,
                        SubstitutionReferenceStage::Lookup(kind) => {
                            match self.lookup_value.take().expect("reply consumed once") {
                                SubstitutionLookupValue::Pending => unreachable!(),
                                SubstitutionLookupValue::Invalid => {
                                    self.invalid_primary(frame);
                                    continue;
                                }
                                SubstitutionLookupValue::Attribute(raw) => {
                                    frame.raw_attribute = raw;
                                    if let Some(raw) = frame.raw_attribute.as_ref() {
                                        if frame.reference.is_attr_with_type()
                                            && !self.in_container_query
                                        {
                                            self.request(
                                                &mut frame,
                                                SubstitutionLookupKind::TypedAttribute,
                                            );
                                        } else {
                                            match self.attribute_value(&frame, raw) {
                                                Some(value) => self.returned = Some(Ok(value)),
                                                None => self.invalid_primary(frame),
                                            }
                                            continue;
                                        }
                                    } else if frame.reference.fallback.is_none()
                                        && frame.reference.attribute_data.kind
                                            == AttributeType::None
                                    {
                                        self.returned = Some(Ok(Substitution::new(
                                            Cow::Owned(quoted_css_string("")),
                                            TokenSerializationType::Nothing,
                                            TokenSerializationType::Nothing,
                                            true,
                                        )));
                                        continue;
                                    } else {
                                        self.invalid_primary(frame);
                                        continue;
                                    }
                                }
                                SubstitutionLookupValue::AttributeSource(value) => {
                                    self.begin_attribute_body(frame, value);
                                    continue;
                                }
                                SubstitutionLookupValue::Value(value, tainted)
                                | SubstitutionLookupValue::Expand(value, tainted) => {
                                    if kind == SubstitutionLookupKind::TypedAttribute {
                                        match self.attribute_value(&frame, &value.css) {
                                            Some(value) => self.returned = Some(Ok(value)),
                                            None => self.invalid_primary(frame),
                                        }
                                    } else if kind == SubstitutionLookupKind::Variable
                                        && value.has_references()
                                    {
                                        if self.seen.contains(&frame.reference.name) {
                                            self.invalid_primary(frame);
                                        } else {
                                            self.seen.push(frame.reference.name.clone());
                                            frame.stage =
                                                SubstitutionReferenceStage::Alias(tainted);
                                            self.frames.push(SubstitutionFrame::Reference(frame));
                                            self.frames.push(SubstitutionFrame::Chunk(
                                                SubstitutionChunk::whole(value, false),
                                            ));
                                        }
                                    } else {
                                        self.returned =
                                            Some(Ok(Substitution::from_value(value, tainted)));
                                    }
                                    continue;
                                }
                            }
                        }
                    }
                    self.frames.push(SubstitutionFrame::Reference(frame));
                    if let Some(request) = self.request.as_ref() {
                        return SubstitutionPoll::Lookup(request.clone());
                    }
                }
            }
        }
    }
}

#[derive(Clone)]
pub(crate) struct CapturedAttributeInput {
    pub raw: Option<String>,
    parsed: Vec<(UrlExtraData, Result<ComputedRegisteredValue, ()>)>,
}

impl CapturedAttributeInput {
    pub(crate) fn query(
        name: &Name,
        namespace: &Namespace,
        tracker: &mut AttributeTracker,
    ) -> Self {
        let raw = LocalName::with_name(name, |local_name| tracker.query(local_name, namespace))
            .map(|value| value.to_string());
        Self {
            raw,
            parsed: Vec::new(),
        }
    }

    pub(crate) fn parse(&mut self, url_data: &UrlExtraData) -> Result<ComputedRegisteredValue, ()> {
        if let Some((_, value)) = self.parsed.iter().find(|(url, _)| url == url_data) {
            return value.clone();
        }
        let result = (|| {
            let raw = self.raw.as_ref().ok_or(())?;
            let mut parser = Parser::new(raw);
            let value = VariableValue::parse(&mut parser, None, url_data).map_err(|_| ())?;
            Ok(ComputedRegisteredValue::universal(Arc::new(value)))
        })();
        self.parsed.push((url_data.clone(), result.clone()));
        result
    }
}
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
struct PreparedMetricDeclaration {
    declaration: PropertyDeclaration,
    priority: CascadePriority,
}
struct MetricPreparation<'a, 'b> {
    longhand: LonghandId,
    declarations: &'a Declarations<'b>,
    cursor: Option<usize>,
    flags: RuleCascadeFlags,
    observed_flags: RuleCascadeFlags,
    initial_revert: Option<(CascadePriority, RevertKind)>,
    revert: Option<(CascadePriority, RevertKind)>,
    waiting: Option<Arc<UnparsedValue>>,
    substitution: Option<ResumableSubstitution<'static>>,
    substitution_generation: Option<Arc<()>>,
    prepared: SmallVec<[PreparedMetricDeclaration; 2]>,
    complete: bool,
}
struct FontSelectionReply {
    value: Arc<UnparsedValue>,
    generation: Arc<()>,
    lookup: Option<SubstitutionLookupReply>,
}
enum MetricPreparationStep {
    Prerequisites(&'static PrioritaryPropertyIdSet),
    References(LonghandId, Arc<UnparsedValue>),
    Lookup(LonghandId, Arc<UnparsedValue>, SubstitutionLookup),
    Complete,
    Invalidated,
}
impl MetricPreparation<'_, '_> {
    fn stable_for_appearance_addition(&self) -> bool {
        self.complete
            && ((self.observed_flags - self.flags) & RuleCascadeFlags::APPEARANCE_BASE).is_empty()
    }

    fn retain(&mut self, declaration: PropertyDeclaration, priority: CascadePriority) {
        debug_assert!(!matches!(
            declaration,
            PropertyDeclaration::WithVariables(..)
        ));
        let revert = declaration
            .get_css_wide_keyword()
            .and_then(|keyword| keyword.revert_kind());
        self.prepared.push(PreparedMetricDeclaration {
            declaration,
            priority,
        });
        if let Some(revert) = revert {
            self.revert = Some((priority, revert));
            self.advance();
        } else {
            self.complete = true;
        }
    }

    fn advance(&mut self) {
        let index = self
            .cursor
            .expect("advancing an exhausted declaration cursor");
        if PrioritaryPropertyId::from_longhand(self.longhand).is_none() {
            self.cursor = next_font_declaration(self.declarations, self.longhand, index + 1);
            return;
        }
        let next = self.declarations.longhand_declarations[index].next_index;
        self.cursor = (next != 0).then_some(next as usize);
    }
}
struct ComputedSizePreparation<'a, 'b> {
    index: usize,
    size: MetricPreparation<'a, 'b>,
    text_scale: MetricPreparation<'a, 'b>,
    family: Option<MetricPreparation<'a, 'b>>,
}
impl ComputedSizePreparation<'_, '_> {
    fn poll(
        &mut self,
        cascade: &Cascade,
        context: &mut computed::Context,
        cache: &mut ShorthandsWithPropertyReferencesCache,
        tracker: &mut AttributeTracker,
        mut reply: Option<(LonghandId, FontSelectionReply)>,
    ) -> MetricPreparationStep {
        if reply.as_ref().is_some_and(|(id, _)| {
            let state = if *id == self.size.longhand {
                &self.size
            } else if *id == self.text_scale.longhand {
                &self.text_scale
            } else if self
                .family
                .as_ref()
                .is_some_and(|state| state.longhand == *id)
            {
                self.family.as_ref().unwrap()
            } else {
                return true;
            };
            state.complete || state.waiting.is_none()
        }) {
            return MetricPreparationStep::Invalidated;
        }
        for state in [&mut self.size, &mut self.text_scale]
            .into_iter()
            .chain(self.family.iter_mut())
        {
            let selected_reply = if reply.as_ref().is_some_and(|(id, _)| *id == state.longhand) {
                reply.take().map(|(_, value)| value)
            } else if reply.is_some() && !state.complete {
                return MetricPreparationStep::Invalidated;
            } else {
                None
            };
            match cascade.resume_font_selection(context, cache, tracker, state, selected_reply) {
                MetricPreparationStep::Complete => {}
                other => return other,
            }
        }
        MetricPreparationStep::Complete
    }

    fn operation(&self) -> Option<&PropertyDeclaration> {
        self.size.prepared.iter().rev().find_map(|entry| {
            (!entry
                .declaration
                .get_css_wide_keyword()
                .is_some_and(|keyword| keyword.revert_kind().is_some()))
            .then_some(&entry.declaration)
        })
    }
}
fn computed_size_selection_flags_stable(
    declarations: &Declarations,
    id: PrioritaryPropertyId,
) -> bool {
    let mut index = declarations.prioritary_positions[id as usize].most_important;
    if index == DeclarationIndex::MAX {
        return true;
    }
    loop {
        let entry = declarations.longhand_declarations[index as usize];
        if entry
            .priority
            .flags()
            .intersects(RuleCascadeFlags::APPEARANCE_BASE)
        {
            return false;
        }
        if entry.next_index == 0 {
            return true;
        }
        index = entry.next_index;
    }
}
mod specified { pub mod length { #[derive(Clone,Copy,Debug,PartialEq)] pub enum LengthUnit {
    // Absolute lengths.
    Px,
    In,
    Cm,
    Mm,
    Q,
    Pt,
    Pc,
    // Font-relative lengths.
    Em,
    Ex,
    Rex,
    Ch,
    Rch,
    Cap,
    Rcap,
    Ic,
    Ric,
    Rem,
    Lh,
    Rlh,
    // Viewport-percentage lengths.
    Vw,
    Svw,
    Lvw,
    Dvw,
    Vh,
    Svh,
    Lvh,
    Dvh,
    Vmin,
    Svmin,
    Lvmin,
    Dvmin,
    Vmax,
    Svmax,
    Lvmax,
    Dvmax,
    Vb,
    Svb,
    Lvb,
    Dvb,
    Vi,
    Svi,
    Lvi,
    Dvi,
    // Container-relative lengths.
    Cqw,
    Cqh,
    Cqi,
    Cqb,
    Cqmin,
    Cqmax,
    /// HTML5 "character width", as defined in HTML5 § 14.5.4. Internal-only.
    ServoCharacterWidth,
}} }
fn size_length_reads_writing_mode(unit: specified::length::LengthUnit, root: bool) -> bool {
    use specified::length::LengthUnit::*;
    matches!(
        unit,
        Ch | Lh | Vi | Vb | Svi | Svb | Lvi | Lvb | Dvi | Dvb | Cqi | Cqb | Cqmin | Cqmax
    ) || (root && matches!(unit, Rch | Rlh))
}
impl Cascade<'_> {
    fn note_variable_substitution(
        &self,
        context: &mut computed::Context,
        declaration: &VariableDeclaration,
    ) {
        if !declaration.id.inherited() {
            context.rule_cache_conditions.borrow_mut().set_uncacheable();

            // NOTE(emilio): We only really need to add the `display` /
            // `content` flag if the CSS variable has not been specified on our
            // declarations, but we don't have that information at this point,
            // and it doesn't seem like an important enough optimization to
            // warrant it.
            if matches!(declaration.id, LonghandId::Display | LonghandId::Content) {
                context
                    .builder
                    .add_flags(ComputedValueFlags::DISPLAY_OR_CONTENT_DEPEND_ON_INHERITED_STYLE);
            }
        }
    }
    fn begin_font_preparation<'a, 'b>(
        &self,
        context: &computed::Context,
        declarations: &'a Declarations<'b>,
        longhand: LonghandId,
    ) -> MetricPreparation<'a, 'b> {
        let cursor = if let Some(id) = PrioritaryPropertyId::from_longhand(longhand) {
            let index = declarations.prioritary_positions[id as usize].most_important;
            (index != DeclarationIndex::MAX).then_some(index as usize)
        } else {
            assert!(is_synthesis_longhand(longhand));
            next_font_declaration(declarations, longhand, 0)
        };
        let initial_revert = self.reverted.longhands.get(&longhand).copied();
        MetricPreparation {
            longhand,
            declarations,
            cursor,
            flags: context.included_cascade_flags,
            observed_flags: RuleCascadeFlags::empty(),
            initial_revert,
            revert: initial_revert,
            waiting: None,
            substitution: None,
            substitution_generation: None,
            prepared: SmallVec::new(),
            complete: false,
        }
    }
    fn resume_font_selection(
        &self,
        context: &mut computed::Context,
        cache: &mut ShorthandsWithPropertyReferencesCache,
        _attribute_tracker: &mut AttributeTracker,
        state: &mut MetricPreparation,
        mut resolved_reference: Option<FontSelectionReply>,
    ) -> MetricPreparationStep {
        let longhand = state.longhand;
        let priority = PrioritaryPropertyId::from_longhand(longhand);
        if priority.is_some_and(|id| self.ensured_prioritary.contains(id))
            || state.flags != context.included_cascade_flags
            || self.seen.longhands.contains(longhand)
            || self.reverted.longhands.get(&longhand).copied() != state.initial_revert
        {
            return MetricPreparationStep::Invalidated;
        }
        loop {
            if state.complete {
                return MetricPreparationStep::Complete;
            }
            let Some(index) = state.cursor else {
                state.complete = true;
                continue;
            };
            let entry = state.declarations.longhand_declarations[index];
            state.observed_flags |= entry.priority.flags();
            if let Some(value) = state.waiting.as_ref() {
                let mut reply = resolved_reference.take();
                if reply.as_ref().is_some_and(|reply| {
                    !Arc::ptr_eq(value, &reply.value)
                        || state
                            .substitution_generation
                            .as_ref()
                            .is_some_and(|generation| !Arc::ptr_eq(generation, &reply.generation))
                }) {
                    return MetricPreparationStep::Invalidated;
                }
                let PropertyDeclaration::WithVariables(variable) = entry.decl else {
                    return MetricPreparationStep::Invalidated;
                };
                if state.substitution.is_none() {
                    let Some(reference) = reply.as_ref() else {
                        return MetricPreparationStep::References(longhand, value.clone());
                    };
                    if reference.lookup.is_some() {
                        return MetricPreparationStep::Invalidated;
                    }
                    self.note_variable_substitution(context, variable);
                    state.substitution_generation = Some(reference.generation.clone());
                    match variable.begin_retained_substitution(context, cache) {
                        Ok(engine) => state.substitution = Some(engine),
                        Err(declaration) => {
                            state.waiting = None;
                            state.substitution_generation = None;
                            state.retain(declaration, entry.priority);
                            continue;
                        }
                    }
                }
                match state
                    .substitution
                    .as_mut()
                    .unwrap()
                    .poll(reply.take().and_then(|reply| reply.lookup))
                {
                    SubstitutionPoll::Lookup(request) => {
                        return MetricPreparationStep::Lookup(longhand, value.clone(), request);
                    }
                    SubstitutionPoll::Complete(result) => {
                        let declaration = variable
                            .finish_retained_substitution(result, context, cache)
                            .into_owned();
                        state.substitution = None;
                        state.substitution_generation = None;
                        state.waiting = None;
                        state.retain(declaration, entry.priority);
                        continue;
                    }
                    SubstitutionPoll::WrongReply | SubstitutionPoll::Finished => {
                        return MetricPreparationStep::Invalidated;
                    }
                }
            }
            if !(entry.priority.flags() - state.flags).is_empty()
                || state.revert.is_some_and(|(priority, kind)| {
                    !priority.allows_when_reverted(&entry.priority, kind)
                })
            {
                state.advance();
                continue;
            }
            if let PropertyDeclaration::WithVariables(value) = entry.decl {
                state.waiting = Some(value.value.clone());
                resolved_reference = None;
                continue;
            }
            state.retain(entry.decl.clone(), entry.priority);
        }
    }
}
impl VariableDeclaration {
    fn substitute_variables<'cache>(
        &self,
        substitution_functions: &ComputedSubstitutionFunctions,
        stylist: &Stylist,
        computed_context: &computed::Context,
        shorthand_cache: &'cache mut ShorthandsWithPropertyReferencesCache,
        attribute_tracker: &mut AttributeTracker,
    ) -> Cow<'cache, PropertyDeclaration> {
        let longhand_id = self.id;
        let unparsed = &self.value;
        let invalid_at_computed_value_time = || {
            let keyword = if longhand_id.inherited() {
                CSSWideKeyword::Inherit
            } else {
                CSSWideKeyword::Initial
            };
            Cow::Owned(PropertyDeclaration::css_wide_keyword(longhand_id, keyword))
        };

        if computed_context
            .builder
            .invalid_non_custom_properties
            .contains(longhand_id)
        {
            return invalid_at_computed_value_time();
        }

        if let Some(shorthand_id) = unparsed.from_shorthand {
            let key = (shorthand_id, longhand_id);
            if shorthand_cache
                .get(&key)
                .is_some_and(|(source, _)| Arc::ptr_eq(source, unparsed))
            {
                // FIXME: This double lookup should be avoidable, but rustc
                // doesn't like that, see:
                //
                // https://github.com/rust-lang/rust/issues/82146
                return Cow::Borrowed(&shorthand_cache[&key].1);
            }
        }

        let property_id = unparsed.substitution_property_id(longhand_id);
        let result = substitute(
            &unparsed.variable_value,
            Some(property_id),
            substitution_functions,
            stylist,
            computed_context,
            attribute_tracker,
        );
        self.finish_retained_substitution(result, computed_context, shorthand_cache)
    }
    pub(crate) fn begin_retained_substitution(
        &self,
        computed_context: &computed::Context,
        shorthand_cache: &ShorthandsWithPropertyReferencesCache,
    ) -> Result<ResumableSubstitution<'static>, PropertyDeclaration> {
        let longhand_id = self.id;
        if computed_context
            .builder
            .invalid_non_custom_properties
            .contains(longhand_id)
        {
            return Err(PropertyDeclaration::css_wide_keyword(
                longhand_id,
                if longhand_id.inherited() {
                    CSSWideKeyword::Inherit
                } else {
                    CSSWideKeyword::Initial
                },
            ));
        }
        if let Some(shorthand) = self.value.from_shorthand {
            if let Some((source, declaration)) = shorthand_cache.get(&(shorthand, longhand_id)) {
                if Arc::ptr_eq(source, &self.value) {
                    return Err(declaration.clone());
                }
            }
        }
        Ok(ResumableSubstitution::for_property(
            self.value.variable_value.clone(),
            self.value.substitution_property_id(longhand_id),
            computed_context.in_container_query,
        ))
    }
    pub(crate) fn finish_retained_substitution<'cache>(
        &self,
        result: Result<SubstitutionResult<'_>, ()>,
        computed_context: &computed::Context,
        shorthand_cache: &'cache mut ShorthandsWithPropertyReferencesCache,
    ) -> Cow<'cache, PropertyDeclaration> {
        let longhand_id = self.id;
        let unparsed = &self.value;
        let property_id = unparsed.substitution_property_id(longhand_id);
        let invalid_at_computed_value_time = || {
            let keyword = if longhand_id.inherited() {
                CSSWideKeyword::Inherit
            } else {
                CSSWideKeyword::Initial
            };
            Cow::Owned(PropertyDeclaration::css_wide_keyword(longhand_id, keyword))
        };
        let SubstitutionResult { css, attr_taint } = match result {
            Ok(value) => value,
            Err(()) => return invalid_at_computed_value_time(),
        };

        // As of this writing, only the base URL is used for property
        // values.
        //
        // NOTE(emilio): we intentionally pase `None` as the rule type here.
        // If something starts depending on it, it's probably a bug, since
        // it'd change how values are parsed depending on whether we're in a
        // @keyframes rule or not, for example... So think twice about
        // whether you want to do this!
        //
        // FIXME(emilio): ParsingMode is slightly fishy...
        let mut context = ParserContext::new(
            Origin::Author,
            &unparsed.variable_value.url_data,
            None,
            ParsingMode::DEFAULT,
            computed_context.quirks_mode,
            /* namespaces = */ Default::default(),
            None,
            None,
            attr_taint,
        );

        let mut input = Parser::new(&css);
        input.skip_whitespace();

        if let Ok(keyword) = input.try_parse(CSSWideKeyword::parse) {
            return Cow::Owned(PropertyDeclaration::css_wide_keyword(longhand_id, keyword));
        }

        let shorthand = match unparsed.from_shorthand {
            None => {
                return match context.with_property_declaration(property_id, |context| {
                    input.parse_entirely(|input| longhand_id.parse_value(context, input))
                }) {
                    Ok(decl) => Cow::Owned(decl),
                    Err(..) => invalid_at_computed_value_time(),
                };
            }
            Some(shorthand) => shorthand,
        };

        let mut decls = SourcePropertyDeclaration::default();
        // parse_into takes care of doing `parse_entirely` for us.
        if context
            .with_property_declaration(property_id, |context| {
                shorthand.parse_into(&mut decls, context, &mut input)
            })
            .is_err()
        {
            return invalid_at_computed_value_time();
        }

        for declaration in decls.declarations.drain(..) {
            let longhand = declaration.id().as_longhand().unwrap();
            if longhand.is_logical() {
                let writing_mode = computed_context.builder.writing_mode;
                shorthand_cache.insert(
                    (shorthand, longhand.to_physical(writing_mode)),
                    (unparsed.clone(), declaration.clone()),
                );
            }
            shorthand_cache.insert((shorthand, longhand), (unparsed.clone(), declaration));
        }

        let key = (shorthand, longhand_id);
        match shorthand_cache.get(&key) {
            Some((source, decl)) if Arc::ptr_eq(source, unparsed) => Cow::Borrowed(decl),
            // NOTE: Under normal circumstances we should always have a value, but when prefs
            // change we might hit this case. Consider something like `animation-timeline`, which
            // is a conditionally-enabled longhand of `animation`:
            //
            // If we have a sheet with `animation: var(--foo)`, and the `animation-timeline` pref
            // enabled, then that expands to an `animation-timeline` declaration at parse time.
            //
            // If the user disables the pref and, some time later, we get here wanting to compute
            // `animation-timeline`, parse_into won't generate any declaration for it anymore, so
            // we haven't inserted in the cache. Computing to invalid / initial seems like the most
            // sensible thing to do here.
            _ => invalid_at_computed_value_time(),
        }
    }
}
impl SubstitutionLookup {
    pub(crate) fn read_current(
        &self,
        functions: &ComputedSubstitutionFunctions,
        stylist: &Stylist,
        tracker: &mut AttributeTracker,
    ) -> SubstitutionLookupReply {
        let value = match self.kind {
            SubstitutionLookupKind::RawAttribute => {
                let raw = self.namespace.as_ref().and_then(|namespace| {
                    LocalName::with_name(&self.name, |name| tracker.query(name, namespace))
                });
                SubstitutionLookupValue::Attribute(raw.map(|value| value.to_string()))
            },
            SubstitutionLookupKind::Environment => {
                let device = stylist.device();
                match device.environment().get(&self.name, device, &self.url_data) {
                    Some(value) => SubstitutionLookupValue::Value(value, false),
                    None => SubstitutionLookupValue::Invalid,
                }
            },
            SubstitutionLookupKind::Variable | SubstitutionLookupKind::TypedAttribute => {
                let resolved = if self.kind == SubstitutionLookupKind::Variable {
                    functions.get_var(
                        stylist.get_custom_property_registration(&self.name),
                        &self.name,
                    )
                } else {
                    self.namespace
                        .as_ref()
                        .and_then(|namespace| functions.get_attr(&self.name, namespace))
                };
                match resolved {
                    None => SubstitutionLookupValue::Invalid,
                    Some(value) => {
                        let owned = value.to_variable_value();
                        if self.kind == SubstitutionLookupKind::Variable && owned.has_references() {
                            SubstitutionLookupValue::Expand(owned, value.attr_tainted)
                        } else {
                            SubstitutionLookupValue::Value(owned, value.attr_tainted)
                        }
                    },
                }
            },
        };
        SubstitutionLookupReply {
            identity: self.identity.clone(),
            value,
        }
    }
}
#[derive(Clone,PartialEq,Eq,Hash)]enum VarType{Custom(Name),Attr(Name,Namespace)}
#[derive(Clone,Copy)]enum VisitResult{Complete,CycleSettled,SemanticOpen(usize),ComputationPending(usize),ComputedSize(usize)}
#[derive(Default)]struct LookupBindings{pending:HashSet<Name>,values:FxHashMap<Name,Option<ComputedRegisteredValue>>,flags:RuleCascadeFlags,valid:bool}
impl LookupBindings{
    fn valid_for(&mut self,flags:RuleCascadeFlags)->bool{self.valid&=flags==self.flags;self.valid}
    fn value(&self,name:&Name,_:&())->Option<Option<ComputedRegisteredValue>>{if self.pending.contains(name){None}else{Some(self.values.get(name).cloned().unwrap_or(None))}}
}
#[derive(Default)]struct LookupCascade{attribute_inputs:FxHashMap<(Name,Namespace),CapturedAttributeInput>,attribute_value_urls:FxHashMap<(Name,Namespace),UrlExtraData>}
struct LookupContext{
    lookup_bindings:LookupBindings,computed_context:computed::Context,cascade:LookupCascade,stylist:Stylist,
    environment_inputs:Vec<(Name,UrlExtraData,Option<VariableValue>)>,
    settled_attributes:FxHashMap<(Name,Namespace),Option<ComputedRegisteredValue>>,
    functions:ComputedSubstitutionFunctions,nodes:FxHashMap<VarType,VisitResult>,
}
impl LookupContext{
    fn new()->Self{Self{lookup_bindings:LookupBindings{valid:true,..Default::default()},computed_context:computed::Context::default(),cascade:LookupCascade::default(),stylist:Stylist::default(),environment_inputs:Vec::new(),settled_attributes:FxHashMap::default(),functions:ComputedSubstitutionFunctions::default(),nodes:FxHashMap::default()}}
    fn visited(&self,var:&VarType)->Option<VisitResult>{self.nodes.get(var).copied()}
    fn map(&self)->&ComputedSubstitutionFunctions{&self.functions}
    fn map_mut(&mut self)->&mut ComputedSubstitutionFunctions{&mut self.functions}
}
impl ComputedSubstitutionFunctions{
    fn contains_attr(&self,name:&Name,_:&Namespace)->bool{self.attrs.contains_key(name)}
    fn insert_attr(&mut self,name:&Name,_:&Namespace,value:ComputedRegisteredValue){self.attrs.insert(name.clone(),value);}
}
impl LookupContext {
        fn captured_environment(
            &mut self,
            name: &Name,
            url_data: &UrlExtraData,
        ) -> Option<VariableValue> {
            if let Some((_, _, value)) = self
                .environment_inputs
                .iter()
                .find(|(cached_name, cached_url, _)| cached_name == name && cached_url == url_data)
            {
                return value.clone();
            }
            let device = self.stylist.device();
            let value = device.environment().get(name, device, url_data);
            self.environment_inputs
                .push((name.clone(), url_data.clone(), value.clone()));
            value
        }
        fn capture_attribute_input(
            &mut self,
            name: &Name,
            namespace: &Namespace,
            _url_data: &UrlExtraData,
            tracker: &mut AttributeTracker,
        ) -> &mut CapturedAttributeInput {
            self.cascade
                .attribute_inputs
                .entry((name.clone(), namespace.clone()))
                .or_insert_with(|| CapturedAttributeInput::query(name, namespace, tracker))
        }
        fn owned_lookup_value(
            &mut self,
            request: &SubstitutionLookup,
            tracker: &mut AttributeTracker,
        ) -> Result<Option<SubstitutionLookupValue>, ()> {
            if !self
                .lookup_bindings
                .valid_for(self.computed_context.included_cascade_flags)
            {
                return Err(());
            }
            let value = match request.kind {
                SubstitutionLookupKind::Environment => {
                    return Ok(Some(
                        match self.captured_environment(&request.name, &request.url_data) {
                            Some(value) => SubstitutionLookupValue::Value(value, false),
                            None => SubstitutionLookupValue::Invalid,
                        },
                    ));
                }
                SubstitutionLookupKind::RawAttribute => {
                    let raw = request.namespace.as_ref().and_then(|namespace| {
                        self.capture_attribute_input(
                            &request.name,
                            namespace,
                            &request.url_data,
                            tracker,
                        )
                        .raw
                        .clone()
                    });
                    return Ok(Some(SubstitutionLookupValue::Attribute(raw)));
                }
                SubstitutionLookupKind::Variable => {
                    if let Some(result) = self.visited(&VarType::Custom(request.name.clone())) {
                        if !matches!(result, VisitResult::Complete | VisitResult::CycleSettled) {
                            return Ok(None);
                        }
                    }
                    let registration = self.stylist.get_custom_property_registration(&request.name);
                    let Some(value) = self.lookup_bindings.value(&request.name, registration)
                    else {
                        return Ok(None);
                    };
                    value
                }
                SubstitutionLookupKind::TypedAttribute => {
                    let namespace = request.namespace.as_ref().ok_or(())?;
                    if request.guards.is_empty() {
                        match self.visited(&VarType::Attr(request.name.clone(), namespace.clone()))
                        {
                            Some(VisitResult::CycleSettled) => return Err(()),
                            Some(result) if !matches!(result, VisitResult::Complete) => {
                                return Ok(None);
                            }
                            _ => {}
                        }
                    }
                    let input = self.capture_attribute_input(
                        &request.name,
                        namespace,
                        &request.url_data,
                        tracker,
                    );
                    if input.raw.is_none() {
                        return Err(());
                    }
                    return Ok(Some(match input.parse(&request.url_data) {
                        Ok(value) => {
                            SubstitutionLookupValue::AttributeSource(value.to_variable_value())
                        }
                        Err(()) => SubstitutionLookupValue::Invalid,
                    }));
                }
            };
            Ok(Some(match value {
                None => SubstitutionLookupValue::Invalid,
                Some(value) => {
                    let tokens = value.to_variable_value();
                    if tokens.has_references() {
                        return Err(());
                    }
                    SubstitutionLookupValue::Value(tokens, value.attr_tainted)
                }
            }))
        }
}
fn tokens(css:&str)->VariableValue {VariableValue::parse(&mut Parser::new(css),None,&UrlExtraData(0)).unwrap()}
fn dynamic(id:LonghandId,css:&str)->PropertyDeclaration{PropertyDeclaration::WithVariables(VariableDeclaration{id,value:Arc::new(UnparsedValue{variable_value:tokens(css),from_shorthand:None})})}
fn declarations<'a>(values:&'a [PropertyDeclaration],levels:&[u8])->Declarations<'a>{Declarations{longhand_declarations:values.iter().enumerate().map(|(i,decl)|Declaration{decl,priority:CascadePriority{level:levels[i],flags:RuleCascadeFlags::empty()},next_index:if i+1<values.len(){(i+1)as DeclarationIndex}else{0}}).collect(),prioritary_positions:[DeclarationPosition{most_important:0};5]}}
fn reference(step:MetricPreparationStep,generation:&Arc<()>)->FontSelectionReply{match step{MetricPreparationStep::References(_,value)=>FontSelectionReply{value,generation:generation.clone(),lookup:None},_=>panic!("expected references")}}
fn lookup(step:MetricPreparationStep)->(Arc<UnparsedValue>,SubstitutionLookup){match step{MetricPreparationStep::Lookup(_,value,request)=>(value,request),_=>panic!("expected lookup")}}
fn answer(value:&Arc<UnparsedValue>,request:&SubstitutionLookup,generation:&Arc<()>,reply:SubstitutionLookupValue)->Option<FontSelectionReply>{Some(FontSelectionReply{value:value.clone(),generation:generation.clone(),lookup:Some(SubstitutionLookupReply{identity:request.identity.clone(),value:reply})})}
fn numeric(state:&MetricPreparation)->f32{match &state.prepared.last().unwrap().declaration{PropertyDeclaration::Number(_,n)=>*n,_=>panic!("not numeric")}}

#[test]
fn actual_caller_retains_pending_without_fallback_parse_or_restarting_effects(){
    PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::Appearance,"var(--main, var(--fallback))")];let decls=declarations(&values,&[2]);
    let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::Appearance);let generation=Arc::new(());
    let step=cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None);let reply=reference(step,&generation);
    let (value,request)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(reply)));assert_eq!(request.name,"main");
    for _ in 0..3{let (_,again)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&generation,SubstitutionLookupValue::Pending)));assert!(Arc::ptr_eq(&request.identity,&again.identity));}
    assert_eq!(state.cursor,Some(0));assert!(state.prepared.is_empty());assert_eq!(context.rule_cache_conditions.borrow().marks,1);PARSES.with(|n|assert_eq!(n.get(),0));assert!(cache.is_empty());
    let step=cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&generation,SubstitutionLookupValue::Value(tokens("20px"),false)));assert!(matches!(step,MetricPreparationStep::Complete));assert_eq!(numeric(&state),20.0);PARSES.with(|n|assert_eq!(n.get(),1));assert!(state.substitution.is_none());
}

#[test]
fn settled_invalid_uses_actual_fallback_then_shared_parser_once(){
    PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"var(--missing, 30px)")];let decls=declarations(&values,&[2]);let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());
    let reply=reference(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None),&generation);let(value,request)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(reply)));
    assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&generation,SubstitutionLookupValue::Invalid)),MetricPreparationStep::Complete));assert_eq!(numeric(&state),30.0);PARSES.with(|n|assert_eq!(n.get(),1));
}

#[test]
fn wrong_raw_arc_and_generation_cannot_complete_selected_entry(){
    let values=[dynamic(LonghandId::FontSize,"var(--size)")];let decls=declarations(&values,&[2]);let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());
    let reply=reference(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None),&generation);let(value,request)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(reply)));
    let wrong=Arc::new((*value).clone());assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&wrong,&request,&generation,SubstitutionLookupValue::Value(tokens("20px"),false))),MetricPreparationStep::Invalidated));
    assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&Arc::new(()),SubstitutionLookupValue::Value(tokens("20px"),false))),MetricPreparationStep::Invalidated));assert!(state.prepared.is_empty());
    let wrong_request=SubstitutionLookupReply{identity:Arc::new(()),value:SubstitutionLookupValue::Value(tokens("20px"),false)};
    assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(FontSelectionReply{value:value.clone(),generation:generation.clone(),lookup:Some(wrong_request)})),MetricPreparationStep::Invalidated));
}

#[test]
fn dynamic_rollback_retains_its_value_and_skips_ineligible_dynamic_loser(){
    let values=[dynamic(LonghandId::FontSize,"var(--rollback)"),dynamic(LonghandId::FontSize,"var(--loser)"),PropertyDeclaration::Number(LonghandId::FontSize,30.0)];let decls=declarations(&values,&[2,2,1]);let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());
    let reply=reference(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None),&generation);let(value,request)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(reply)));
    assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&generation,SubstitutionLookupValue::Value(tokens("revert-layer"),false))),MetricPreparationStep::Complete));assert_eq!(state.prepared.len(),2);assert_eq!(numeric(&state),30.0);assert_eq!(state.cursor,Some(2));
}

#[test]
fn typed_attr_raw_query_and_each_url_parse_are_retained_separately(){
    let mut tracker=AttributeTracker::default();tracker.values.insert("size".into(),"20px".into());let name="size".to_string();let ns=String::new();let mut input=CapturedAttributeInput::query(&name,&ns,&mut tracker);
    tracker.values.insert(name.clone(),"30px".into());
    let first=input.parse(&UrlExtraData(1)).unwrap();let second=input.parse(&UrlExtraData(2)).unwrap();let repeated=input.parse(&UrlExtraData(1)).unwrap();assert_eq!(tracker.queries.len(),1);assert_eq!(input.parsed.len(),2);assert_eq!(first.value.css,"20px");assert_eq!(first.value.url_data,UrlExtraData(1));assert_eq!(second.value.url_data,UrlExtraData(2));assert_eq!(repeated.value.url_data,UrlExtraData(1));
    let mut typed_first=CapturedAttributeInput::query(&name,&ns,&mut tracker);typed_first.parse(&UrlExtraData(2)).unwrap();assert_eq!(typed_first.raw.as_deref(),Some("30px"));typed_first.parse(&UrlExtraData(1)).unwrap();assert_eq!(typed_first.parsed.len(),2);
}

#[test]
fn real_engine_typed_attr_pending_keeps_taint_until_shared_parse_tail(){
    PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"attr(data-size type(<length>), 9px)")];let decls=declarations(&values,&[2]);let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());
    let reply=reference(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None),&generation);let(value,raw)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(reply)));assert!(matches!(raw.kind,SubstitutionLookupKind::RawAttribute));
    let(_,typed)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&raw,&generation,SubstitutionLookupValue::Attribute(Some("20px".into())))));assert!(matches!(typed.kind,SubstitutionLookupKind::TypedAttribute));
    let(_,again)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&typed,&generation,SubstitutionLookupValue::Pending)));assert!(Arc::ptr_eq(&typed.identity,&again.identity));PARSES.with(|n|assert_eq!(n.get(),0));
    assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&typed,&generation,SubstitutionLookupValue::Value(tokens("20px"),true))),MetricPreparationStep::Complete));assert_eq!(numeric(&state),20.0);LAST_TAINT.with(|v|assert_eq!(*v.borrow(),vec![(0,4)]));
}

fn declaration_key(d:&PropertyDeclaration)->String{match d{PropertyDeclaration::Number(id,n)=>format!("{id:?}:{n}"),PropertyDeclaration::Wide(id,k)=>format!("{id:?}:{k:?}"),_=>panic!("unresolved")}}
#[test]
fn actual_synchronous_and_retained_callers_share_parse_and_cache_results(){
    for css in ["var(--size)","var(--absent, 30px)","var(--empty)","var(--wide)","env(test-size)","attr(data-size type(<length>), 9px)"] {
        let mut functions=ComputedSubstitutionFunctions::default();
        for(name,text)in [("size","20px"),("empty",""),("wide","initial")] {functions.vars.insert(name.into(),ComputedRegisteredValue{value:tokens(text),attr_tainted:false});}
        functions.attrs.insert("data-size".into(),ComputedRegisteredValue{value:tokens("20px"),attr_tainted:true});
        let mut stylist=Stylist::default();stylist.device.values.insert("test-size".into(),tokens("30px"));
        let mut tracker=AttributeTracker::default();tracker.values.insert("data-size".into(),"20px".into());
        let values=[dynamic(LonghandId::FontSize,css)];let PropertyDeclaration::WithVariables(variable)=&values[0] else{unreachable!()};let decls=declarations(&values,&[2]);
        let mut context=computed::Context::default();let mut sync_cache=ShorthandsWithPropertyReferencesCache::default();
        let expected=variable.substitute_variables(&functions,&stylist,&context,&mut sync_cache,&mut tracker).into_owned();
        let cascade=Cascade::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());
        let mut reply=None;
        loop {match cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,reply.take()) {
            MetricPreparationStep::References(_,value)=>reply=Some(FontSelectionReply{value,generation:generation.clone(),lookup:None}),
            MetricPreparationStep::Lookup(_,value,request)=>reply=Some(FontSelectionReply{value,generation:generation.clone(),lookup:Some(request.read_current(&functions,&stylist,&mut tracker))}),
            MetricPreparationStep::Complete=>break,
            _=>panic!("unexpected readiness"),
        }}
        assert_eq!(declaration_key(&state.prepared.last().unwrap().declaration),declaration_key(&expected),"{css}");
    }
}

#[test]
fn shorthand_cache_is_inserted_only_after_complete_and_requires_source_arc(){
    PARSES.with(|n|n.set(0));let mut declaration=dynamic(LonghandId::FontSize,"var(--size)");
    let PropertyDeclaration::WithVariables(v)=&mut declaration else{unreachable!()};v.value=Arc::new(UnparsedValue{variable_value:tokens("var(--size)"),from_shorthand:Some(ShorthandId::Font)});
    let values=[declaration];let decls=declarations(&values,&[2]);let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());
    let reply=reference(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None),&generation);let(value,request)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(reply)));
    lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&generation,SubstitutionLookupValue::Pending)));assert!(cache.is_empty());
    assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&generation,SubstitutionLookupValue::Value(tokens("20px"),false))),MetricPreparationStep::Complete));assert_eq!(cache.len(),1);
    let PropertyDeclaration::WithVariables(v)=&values[0] else{unreachable!()};assert!(v.begin_retained_substitution(&context,&cache).is_err());
    let other=VariableDeclaration{id:v.id,value:Arc::new((*v.value).clone())};assert!(other.begin_retained_substitution(&context,&cache).is_ok());PARSES.with(|n|assert_eq!(n.get(),1));
}

fn request(kind:SubstitutionLookupKind,name:&str,url:u8)->SubstitutionLookup{SubstitutionLookup{guards:Vec::new(),kind,name:name.into(),identity:Arc::new(()),attribute_attempt:None,namespace:Some(String::new()),url_data:UrlExtraData(url)}}
#[test]
fn production_lookup_distinguishes_initial_absence_pending_and_cycle_default(){
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();let r=request(SubstitutionLookupKind::Variable,"x",0);
    assert!(matches!(context.owned_lookup_value(&r,&mut tracker),Ok(Some(SubstitutionLookupValue::Invalid))));
    context.lookup_bindings.pending.insert("x".into());assert!(matches!(context.owned_lookup_value(&r,&mut tracker),Ok(None)));
    context.lookup_bindings.pending.clear();context.lookup_bindings.values.insert("x".into(),Some(ComputedRegisteredValue{value:tokens("2px"),attr_tainted:false}));
    context.nodes.insert(VarType::Custom("x".into()),VisitResult::ComputationPending(0));assert!(matches!(context.owned_lookup_value(&r,&mut tracker),Ok(None)));
    context.nodes.insert(VarType::Custom("x".into()),VisitResult::CycleSettled);
    match context.owned_lookup_value(&r,&mut tracker).unwrap().unwrap(){SubstitutionLookupValue::Value(v,_)=>assert_eq!(v.css,"2px"),_=>panic!("registered cycle default")}
}

#[test]
fn production_attribute_lookup_returns_owned_source_per_url_without_global_publication() {
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();tracker.values.insert("x".into(),"20px".into());
    let raw=request(SubstitutionLookupKind::RawAttribute,"x",1);
    assert!(matches!(context.owned_lookup_value(&raw,&mut tracker),Ok(Some(SubstitutionLookupValue::Attribute(Some(_))))));
    context.cascade.attribute_value_urls.insert(("x".into(),String::new()),UrlExtraData(3));
    for url in [2,1,2] {
        let typed=request(SubstitutionLookupKind::TypedAttribute,"x",url);
        match context.owned_lookup_value(&typed,&mut tracker).unwrap().unwrap() {
            SubstitutionLookupValue::AttributeSource(value)=>{
                assert_eq!(value.css,"20px");assert_eq!(value.url_data,UrlExtraData(url));
            },_=>panic!("not raw child source"),
        }
    }
    assert_eq!(tracker.queries.len(),1);assert!(context.functions.attrs.is_empty());
    assert_eq!(context.cascade.attribute_inputs[&("x".into(),String::new())].parsed.len(),2);
}

#[test]
fn production_raw_namespace_missing_and_environment_snapshot_keep_distinct_paths(){
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();let mut unknown=request(SubstitutionLookupKind::RawAttribute,"x",1);unknown.namespace=None;
    assert!(matches!(context.owned_lookup_value(&unknown,&mut tracker),Ok(Some(SubstitutionLookupValue::Attribute(None)))));assert!(tracker.queries.is_empty());
    let missing=request(SubstitutionLookupKind::RawAttribute,"x",1);assert!(matches!(context.owned_lookup_value(&missing,&mut tracker),Ok(Some(SubstitutionLookupValue::Attribute(None)))));assert_eq!(tracker.queries.len(),1);
    assert!(context.owned_lookup_value(&request(SubstitutionLookupKind::TypedAttribute,"x",1),&mut tracker).is_err());
    context.stylist.device.values.insert("size".into(),tokens("20px"));let env=request(SubstitutionLookupKind::Environment,"size",1);
    context.owned_lookup_value(&env,&mut tracker).unwrap();context.stylist.device.values.insert("size".into(),tokens("30px"));
    match context.owned_lookup_value(&env,&mut tracker).unwrap().unwrap(){SubstitutionLookupValue::Value(v,_)=>assert_eq!(v.css,"20px"),_=>panic!("environment")};
}
fn child_source(css: &str, url: u8) -> VariableValue {
    VariableValue::parse(&mut Parser::new(css), None, &UrlExtraData(url)).unwrap()
}
fn child_drive(engine: &mut ResumableSubstitution, context: &mut LookupContext, tracker: &mut AttributeTracker) -> Result<SubstitutionResult<'static>, ()> {
    let mut reply = None;
    loop {
        match engine.poll(reply.take()) {
            SubstitutionPoll::Lookup(request) => {
                let value = context.owned_lookup_value(&request, tracker).unwrap().expect("test child inputs complete");
                reply = Some(SubstitutionLookupReply { identity: request.identity, value });
            }
            SubstitutionPoll::Complete(result) => return result,
            _ => panic!("unexpected child reply"),
        }
    }
}
fn child_run(css: &str, url: u8, context: &mut LookupContext, tracker: &mut AttributeTracker) -> Result<SubstitutionResult<'static>, ()> {
    child_drive(&mut ResumableSubstitution::new(child_source(css, url), None, false), context, tracker)
}
#[test]
fn independent_url_attempts_keep_env_primary_and_fallback_distinct() {
    let mut context = LookupContext::new();
    context.stylist.device.contextual.insert(("metric".into(), 1), child_source("7px", 1));
    let mut tracker = AttributeTracker::default();
    tracker.values.insert("a".into(), "env(metric, 1px)".into());
    for (url, expected) in [(0,"1px"),(1,"7px"),(0,"1px"),(1,"7px")] {
        let result = child_run("attr(a type(<length>))", url, &mut context, &mut tracker).unwrap();
        assert_eq!(result.css, expected);
        assert_eq!(result.attr_taint.0.as_slice(), &[AttrTaintedRange{start:0,end:3}]);
    }
    assert_eq!(tracker.queries.len(), 1);
    assert!(context.functions.attrs.is_empty());
}
#[test]
fn marked_attribute_body_cannot_be_laundered_by_inner_fallback() {
    let mut context = LookupContext::new();let mut tracker = AttributeTracker::default();
    tracker.values.insert("a".into(), "attr(a type(<length>), 2px)".into());
    assert_eq!(child_run("attr(a type(<length>), 9px)", 0, &mut context, &mut tracker).unwrap().css, "9px");
    assert!(child_run("attr(a type(<length>))", 0, &mut context, &mut tracker).is_err());
    tracker.values.insert("b".into(), "7px".into());
    assert_eq!(child_run("attr(a type(<length>), attr(b type(<length>)))", 0, &mut context, &mut tracker).unwrap().css, "7px");
}
#[test]
fn every_participating_attribute_stays_marked_until_its_body_finishes() {
    let mut context = LookupContext::new();let mut tracker = AttributeTracker::default();
    tracker.values.insert("a".into(), "attr(b type(<length>), 4px)".into());
    tracker.values.insert("b".into(), "attr(a type(<length>), 3px)".into());
    assert_eq!(child_run("attr(a type(<length>), 9px)", 0, &mut context, &mut tracker).unwrap().css, "9px");
}
#[test]
fn context_local_cycle_does_not_poison_independent_primary_context() {
    for order in [[0,1],[1,0]] {
        let mut context = LookupContext::new();let mut tracker = AttributeTracker::default();
        context.stylist.device.contextual.insert(("metric".into(),1), child_source("7px",1));
        tracker.values.insert("a".into(), "env(metric, attr(a type(<length>), 2px))".into());
        for url in order {
            assert_eq!(child_run("attr(a type(<length>), 9px)",url,&mut context,&mut tracker).unwrap().css, if url==1 {"7px"} else {"9px"});
        }
        assert_eq!(tracker.queries.len(),1);
    }
}
#[test]
fn child_pending_retains_raw_snapshot_guard_and_exact_request() {
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();
    tracker.values.insert("a".into(),"var(--ready, attr(fallback type(<length>)))".into());
    context.lookup_bindings.pending.insert("ready".into());
    let mut engine=ResumableSubstitution::new(tokens("attr(a type(<length>), 9px)"),None,false);
    let mut reply=None;
    let waiting=loop {
        let SubstitutionPoll::Lookup(request)=engine.poll(reply.take()) else {panic!("premature finish")};
        match context.owned_lookup_value(&request,&mut tracker).unwrap() {
            Some(value)=>reply=Some(SubstitutionLookupReply{identity:request.identity,value}),
            None=>break request,
        }
    };
    assert_eq!(waiting.name,"ready");assert_eq!(engine.guards.len(),1);
    assert!(Arc::ptr_eq(waiting.attribute_attempt.as_ref().unwrap(),&engine.guards[0].identity));
    for _ in 0..3 {
        let SubstitutionPoll::Lookup(again)=engine.poll(Some(SubstitutionLookupReply{identity:waiting.identity.clone(),value:SubstitutionLookupValue::Pending})) else {panic!("pending became fallback")};
        assert!(Arc::ptr_eq(&again.identity,&waiting.identity));
    }
    assert_eq!(tracker.queries.len(),1);
    tracker.values.insert("a".into(),"30px".into());
    context.lookup_bindings.pending.clear();
    context.lookup_bindings.values.insert("ready".into(),Some(ComputedRegisteredValue{value:tokens("20px"),attr_tainted:false}));
    let result=child_drive(&mut engine,&mut context,&mut tracker).unwrap();
    assert_eq!(result.css,"20px");assert!(engine.guards.is_empty());assert_eq!(tracker.queries.len(),1);
}
#[test]
fn child_wrong_url_reply_is_not_consumed() {
    let mut engine=ResumableSubstitution::new(child_source("attr(a type(<length>))",2),None,false);
    let SubstitutionPoll::Lookup(raw)=engine.poll(None) else {panic!()};
    let SubstitutionPoll::Lookup(typed)=engine.poll(Some(SubstitutionLookupReply{identity:raw.identity,value:SubstitutionLookupValue::Attribute(Some("20px".into()))})) else {panic!()};
    assert!(matches!(engine.poll(Some(SubstitutionLookupReply{identity:typed.identity.clone(),value:SubstitutionLookupValue::AttributeSource(child_source("20px",1))})),SubstitutionPoll::WrongReply));
    let SubstitutionPoll::Complete(Ok(result))=engine.poll(Some(SubstitutionLookupReply{identity:typed.identity,value:SubstitutionLookupValue::AttributeSource(child_source("20px",2))})) else {panic!()};
    assert_eq!(result.css,"20px");
}
#[test]
fn thousands_of_attribute_children_use_iterative_frames_on_small_thread_stack() {
    std::thread::Builder::new().stack_size(256*1024).spawn(|| {
        let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();
        for i in 0..4096 {tracker.values.insert(format!("a{i}"),if i==4095 {"20px".into()} else {format!("attr(a{} type(<length>))",i+1)});}
        assert_eq!(child_run("attr(a0 type(<length>))",0,&mut context,&mut tracker).unwrap().css,"20px");
        assert_eq!(tracker.queries.len(),4096);
    }).unwrap().join().unwrap();
}
#[test]
fn child_result_preserves_utf8_separator_and_taint_offsets() {
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();
    tracker.values.insert("a".into(),"var(--size)".into());
    context.lookup_bindings.values.insert("size".into(),Some(ComputedRegisteredValue{value:tokens("2px"),attr_tainted:false}));
    let result=child_run("é attr(a type(<length>))foo",0,&mut context,&mut tracker).unwrap();
    assert_eq!(result.css,"é 2px/**/foo");
    assert_eq!(result.attr_taint.0.as_slice(),&[AttrTaintedRange{start:3,end:6}]);
}
#[test]
fn expanded_child_still_enforces_existing_output_limit() {
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();
    tracker.values.insert("a".into(),"var(--big) var(--big)".into());
    context.lookup_bindings.values.insert("big".into(),Some(ComputedRegisteredValue{value:tokens(&"a".repeat(1024*1024)),attr_tainted:false}));
    assert_eq!(child_run("attr(a type(*), 9px)",0,&mut context,&mut tracker).unwrap().css,"9px");
}

#[test]
fn unscoped_graph_cycle_is_not_css_invalid_and_active_graph_is_pending() {
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();
    tracker.values.insert("a".into(),"20px".into());
    let typed=request(SubstitutionLookupKind::TypedAttribute,"a",0);
    context.nodes.insert(VarType::Attr("a".into(),String::new()),VisitResult::CycleSettled);
    assert!(context.owned_lookup_value(&typed,&mut tracker).is_err());
    context.nodes.insert(VarType::Attr("a".into(),String::new()),VisitResult::SemanticOpen(0));
    assert!(matches!(context.owned_lookup_value(&typed,&mut tracker),Ok(None)));
    assert!(tracker.queries.is_empty());
}
#[test]
fn completed_custom_default_is_authoritative_but_cannot_clear_active_attribute_marks() {
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();
    context.lookup_bindings.values.insert("b".into(),Some(ComputedRegisteredValue{value:tokens("8px"),attr_tainted:false}));
    context.nodes.insert(VarType::Custom("b".into()),VisitResult::CycleSettled);
    tracker.values.insert("a".into(),"attr(a type(<length>), var(--b))".into());
    tracker.values.insert("other".into(),"var(--b)".into());
    assert_eq!(child_run("attr(a type(<length>), 9px)",0,&mut context,&mut tracker).unwrap().css,"9px");
    assert_eq!(child_run("attr(other type(<length>))",0,&mut context,&mut tracker).unwrap().css,"8px");
    assert_eq!(context.lookup_bindings.values["b"].as_ref().unwrap().value.css,"8px");
}
struct MetricAction{current:bool}
struct EntryBindings{root:Arc<()>,valid:bool}
impl EntryBindings{fn valid_for(&mut self,_:RuleCascadeFlags)->bool{self.valid}}
struct EntryContext{frames:Vec<()>,metric_references:Option<()>,frame_reply:Option<()>,lookup_reply:Option<(LonghandId,FontSelectionReply)>,lookup_bindings:EntryBindings,computed_context:computed::Context}
impl EntryContext{
 fn new(root:Arc<()>)->Self{Self{frames:vec![()],metric_references:None,frame_reply:None,lookup_reply:None,lookup_bindings:EntryBindings{root,valid:true},computed_context:computed::Context::default()}}
 fn metric_action_is_current(&self,a:&MetricAction,depth:usize)->bool{a.current&&depth==1}
}
#[test]fn actual_authorization_selector_and_lookup_reach_first_attribute_without_prewalk(){
 for body in ["20px","attr(data-size type(<length>),9px)"]{
  PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"attr(data-size type(<length>),1px)")];let decls=declarations(&values,&[2]);let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();tracker.values.insert("data-size".into(),body.into());let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());let mut entry=EntryContext::new(generation.clone());
  let MetricPreparationStep::References(longhand,value)=cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None)else{panic!()};let raw=value.clone();assert!(entry.authorize_metric_substitution(&MetricAction{current:true},longhand,value));let (_,initial)=entry.lookup_reply.take().unwrap();assert!(Arc::ptr_eq(&initial.value,&raw));assert!(Arc::ptr_eq(&initial.generation,&generation));assert!(initial.lookup.is_none());
  let mut inputs=LookupContext::new();inputs.nodes.insert(VarType::Attr("data-size".into(),String::new()),VisitResult::CycleSettled);let mut reply=Some(initial);let mut requests=0;
  loop{match cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,reply.take()){
   MetricPreparationStep::Lookup(_,value,request)=>{assert!(request.guards.iter().any(|g|matches!(g.key,SubstitutionGuardKey::Property(PropertyId::NonCustom(_)))));let result=inputs.owned_lookup_value(&request,&mut tracker).unwrap().unwrap();reply=answer(&value,&request,&generation,result);requests+=1;},
   MetricPreparationStep::Complete=>break,
   _=>panic!("unexpected prewalk or incomplete selector"),
  }}
  assert!(requests>=2);assert_eq!(numeric(&state),if body=="20px"{20.0}else{1.0});assert_eq!(tracker.queries.len(),1);assert_eq!(context.rule_cache_conditions.borrow().marks,0);PARSES.with(|n|assert_eq!(n.get(),1));
 }
}
#[test]fn authorization_rejects_wrong_owner_or_unretired_context(){
 let value=Arc::new(UnparsedValue{variable_value:tokens("20px"),from_shorthand:None});
 for reason in 0..5{let mut c=EntryContext::new(Arc::new(()));match reason{1=>c.metric_references=Some(()),2=>c.frame_reply=Some(()),3=>c.lookup_bindings.valid=false,4=>c.frames.clear(),_=>{}}
 assert!(!c.authorize_metric_substitution(&MetricAction{current:reason!=0},LonghandId::FontSize,value.clone()));assert!(c.lookup_reply.is_none());}
}
fn size_states<'a,'b>(cascade:&Cascade,context:&computed::Context,decls:&'a Declarations<'b>)->ComputedSizePreparation<'a,'b>{ComputedSizePreparation{index:7,family:None,size:cascade.begin_font_preparation(context,decls,LonghandId::FontSize),text_scale:cascade.begin_font_preparation(context,decls,LonghandId::XTextScale)}}
fn size_declarations<'a>(values:&'a[PropertyDeclaration],levels:&[u8])->Declarations<'a>{let mut d=declarations(values,levels);d.prioritary_positions[3].most_important=DeclarationIndex::MAX;d}
#[test]
fn size_action_retains_real_selection_pending_and_routes_reply_once(){
 PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"var(--size, 30px)")];let d=size_declarations(&values,&[2]);let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);let generation=Arc::new(());
 let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),&generation);
 let(v,q)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))));
 for _ in 0..3{let(_,again)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,answer(&v,&q,&generation,SubstitutionLookupValue::Pending).unwrap()))));assert!(Arc::ptr_eq(&again.identity,&q.identity));}
 assert!(states.size.prepared.is_empty());assert!(!states.text_scale.complete);PARSES.with(|n|assert_eq!(n.get(),0));assert_eq!(ctx.rule_cache_conditions.borrow().marks,0);
 let r=answer(&v,&q,&generation,SubstitutionLookupValue::Value(tokens("20px"),false)).unwrap();assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))),MetricPreparationStep::Complete));assert_eq!(numeric(&states.size),20.0);assert!(states.text_scale.prepared.is_empty());assert!(states.text_scale.complete);PARSES.with(|n|assert_eq!(n.get(),1));
 assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Complete));PARSES.with(|n|assert_eq!(n.get(),1));
 ctx.included_cascade_flags=RuleCascadeFlags::APPEARANCE_BASE;assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Invalidated));
}
#[test]
fn size_action_keeps_rollback_and_rejects_reply_for_other_input(){
 let values=[dynamic(LonghandId::FontSize,"var(--rollback)"),PropertyDeclaration::Number(LonghandId::FontSize,20.0)];let d=size_declarations(&values,&[2,1]);let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);let g=Arc::new(());let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),&g);
 assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::XTextScale,r))),MetricPreparationStep::Invalidated));
 let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),&g);let(v,q)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))));let r=answer(&v,&q,&g,SubstitutionLookupValue::Value(tokens("revert-layer"),false)).unwrap();assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))),MetricPreparationStep::Complete));assert_eq!(states.size.prepared.len(),2);assert_eq!(numeric(&states.size),20.0);
}
#[test]
fn size_selection_checks_hidden_appearance_entries_before_any_substitution(){
 let values=[dynamic(LonghandId::FontSize,"var(--rollback)"),PropertyDeclaration::Number(LonghandId::FontSize,20.0)];let mut d=size_declarations(&values,&[2,1]);assert!(computed_size_selection_flags_stable(&d,PrioritaryPropertyId::FontSize));d.longhand_declarations[1].priority.flags=RuleCascadeFlags::APPEARANCE_BASE;assert!(!computed_size_selection_flags_stable(&d,PrioritaryPropertyId::FontSize));assert!(computed_size_selection_flags_stable(&d,PrioritaryPropertyId::XTextScale));
}
#[test]
fn size_selection_retains_inherit_and_absence_without_synthetic_numeric_value(){
 for absent in [false,true]{let values=[PropertyDeclaration::Wide(LonghandId::FontSize,CSSWideKeyword::Inherit)];let mut d=size_declarations(&values,&[2]);if absent{d.prioritary_positions[0].most_important=DeclarationIndex::MAX;}let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Complete));assert_eq!(states.size.prepared.len(),if absent{0}else{1});if !absent{assert!(matches!(states.size.prepared[0].declaration,PropertyDeclaration::Wide(_,CSSWideKeyword::Inherit)));}}
}
#[test]
fn size_action_routes_second_input_after_first_parse_without_repeating_it(){
 PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"var(--size)"),dynamic(LonghandId::XTextScale,"var(--scale)")];let mut d=size_declarations(&values,&[2,2]);d.longhand_declarations[0].next_index=0;d.prioritary_positions[3].most_important=1;let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);let g=Arc::new(());
 let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),&g);let(v,q)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))));let r=answer(&v,&q,&g,SubstitutionLookupValue::Value(tokens("20px"),false)).unwrap();let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))),&g);PARSES.with(|n|assert_eq!(n.get(),1));
 let(v,q)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::XTextScale,r))));assert_eq!(q.name,"scale");let r=answer(&v,&q,&g,SubstitutionLookupValue::Value(tokens("1"),false)).unwrap();assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::XTextScale,r))),MetricPreparationStep::Complete));assert_eq!(numeric(&states.size),20.0);assert_eq!(numeric(&states.text_scale),1.0);PARSES.with(|n|assert_eq!(n.get(),2));
}
#[test]
fn optional_keyword_family_resumes_after_size_and_scale_without_reparsing(){
 PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"var(--size)"),dynamic(LonghandId::FontFamily,"var(--family)")];let mut d=size_declarations(&values,&[2,2]);d.longhand_declarations[0].next_index=0;d.prioritary_positions[4].most_important=1;let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);let g=Arc::new(());
 let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),&g);let(v,q)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))));let r=answer(&v,&q,&g,SubstitutionLookupValue::Value(tokens("20px"),false)).unwrap();assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontSize,r))),MetricPreparationStep::Complete));assert!(states.operation().is_some());
 states.family=Some(c.begin_font_preparation(&ctx,&d,LonghandId::FontFamily));let r=reference(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),&g);let(v,q)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontFamily,r))));assert_eq!(q.name,"family");
 let(_,again)=lookup(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontFamily,answer(&v,&q,&g,SubstitutionLookupValue::Pending).unwrap()))));assert!(Arc::ptr_eq(&q.identity,&again.identity));PARSES.with(|n|assert_eq!(n.get(),1));
 let r=answer(&v,&q,&g,SubstitutionLookupValue::Value(tokens("1"),false)).unwrap();assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,Some((LonghandId::FontFamily,r))),MetricPreparationStep::Complete));assert_eq!(numeric(&states.size),20.0);assert_eq!(numeric(states.family.as_ref().unwrap()),1.0);PARSES.with(|n|assert_eq!(n.get(),2));
}
#[test]
fn reverted_to_absence_retains_rollback_without_misclassifying_it_as_font_size(){
 let values=[PropertyDeclaration::Wide(LonghandId::FontSize,CSSWideKeyword::RevertLayer)];let d=size_declarations(&values,&[2]);let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Complete));assert!(states.operation().is_none());assert_eq!(states.size.prepared.len(),1);
}

#[test]
fn unvisited_lower_appearance_does_not_block_selected_winner(){
 let values=[PropertyDeclaration::Number(LonghandId::FontSize,20.0),PropertyDeclaration::Number(LonghandId::FontSize,40.0)];let mut d=size_declarations(&values,&[2,1]);d.longhand_declarations[1].priority.flags=RuleCascadeFlags::APPEARANCE_BASE;let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Complete));assert_eq!(numeric(&states.size),20.0);assert!(states.size.stable_for_appearance_addition());
}
#[test]
fn skipped_higher_appearance_blocks_publication_even_with_numeric_winner(){
 let values=[PropertyDeclaration::Number(LonghandId::FontSize,40.0),PropertyDeclaration::Number(LonghandId::FontSize,20.0)];let mut d=size_declarations(&values,&[2,1]);d.longhand_declarations[0].priority.flags=RuleCascadeFlags::APPEARANCE_BASE;let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Complete));assert_eq!(numeric(&states.size),20.0);assert!(!states.size.stable_for_appearance_addition());
}
#[test]
fn rollback_reached_appearance_is_part_of_publication_prefix(){
 let values=[PropertyDeclaration::Wide(LonghandId::FontSize,CSSWideKeyword::RevertLayer),PropertyDeclaration::Number(LonghandId::FontSize,40.0),PropertyDeclaration::Number(LonghandId::FontSize,20.0)];let mut d=size_declarations(&values,&[3,2,1]);d.longhand_declarations[1].priority.flags=RuleCascadeFlags::APPEARANCE_BASE;let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut states=size_states(&c,&ctx,&d);assert!(matches!(states.poll(&c,&mut ctx,&mut cache,&mut tracker,None),MetricPreparationStep::Complete));assert_eq!(numeric(&states.size),20.0);assert!(!states.size.stable_for_appearance_addition());
}
#[test]
fn native_unit_readset_does_not_wait_on_unread_child_orientation(){
 use specified::length::LengthUnit::*;
 for root in [false,true]{for unit in [Px,In,Cm,Mm,Q,Pt,Pc,Em,Ex,Cap,Ic,Rem,Rex,Rcap,Ric,Vw,Vh,Vmin,Vmax,Cqw,Cqh]{assert!(!size_length_reads_writing_mode(unit,root),"{unit:?} {root}");}}
 for unit in [Ch,Lh,Vi,Vb,Svi,Svb,Lvi,Lvb,Dvi,Dvb,Cqi,Cqb,Cqmin,Cqmax]{assert!(size_length_reads_writing_mode(unit,false),"{unit:?}");}
 for unit in [Rch,Rlh]{assert!(!size_length_reads_writing_mode(unit,false));assert!(size_length_reads_writing_mode(unit,true));}
}
#[test]
fn integrated_size_selector_consumes_owned_attribute_then_next_input_once(){
 PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"attr(data-size type(<length>),9px)"),dynamic(LonghandId::XTextScale,"var(--scale)")];let mut d=size_declarations(&values,&[2,2]);d.longhand_declarations[0].next_index=0;d.prioritary_positions[3].most_important=1;
 let c=Cascade::default();let mut ctx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();tracker.values.insert("data-size".into(),"20px".into());let mut states=size_states(&c,&ctx,&d);let g=Arc::new(());let mut entry=EntryContext::new(g.clone());let mut inputs=LookupContext::new();inputs.nodes.insert(VarType::Attr("data-size".into(),String::new()),VisitResult::CycleSettled);inputs.lookup_bindings.values.insert("scale".into(),Some(ComputedRegisteredValue::universal(Arc::new(tokens("1")))));let mut reply=None;let mut completed=false;
 for _ in 0..128{match states.poll(&c,&mut ctx,&mut cache,&mut tracker,reply.take()){
  MetricPreparationStep::References(id,value)=>{assert!(entry.authorize_metric_substitution(&MetricAction{current:true},id,value));reply=entry.lookup_reply.take();},
  MetricPreparationStep::Lookup(id,value,request)=>{let value_reply=inputs.owned_lookup_value(&request,&mut tracker).unwrap().unwrap();reply=Some((id,answer(&value,&request,&g,value_reply).unwrap()));},
  MetricPreparationStep::Complete=>{completed=true;break},
  _=>panic!("unexpected integrated selection wait"),
 }}
 assert!(completed,"retained selector must make finite progress with ready inputs");
 assert_eq!(numeric(&states.size),20.0);assert_eq!(numeric(&states.text_scale),1.0);assert_eq!(tracker.queries.len(),1);assert!(states.size.stable_for_appearance_addition());PARSES.with(|n|assert_eq!(n.get(),2));
}
impl EntryContext {
        fn authorize_metric_substitution(
            &mut self,
            action: &MetricAction,
            longhand: LonghandId,
            value: Arc<UnparsedValue>,
        ) -> bool {
            if !self.metric_action_is_current(action, self.frames.len())
                || self.metric_references.is_some()
                || self.frame_reply.is_some()
                || self.lookup_reply.is_some()
                || !self
                    .lookup_bindings
                    .valid_for(self.computed_context.included_cascade_flags)
            {
                return false;
            }
            self.lookup_reply = Some((
                longhand,
                FontSelectionReply {
                    value,
                    generation: self.lookup_bindings.root.clone(),
                    lookup: None,
                },
            ));
            true
        }
}
