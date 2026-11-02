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
            },
            Token::BadUrl(..) => {
                let e = StyleParseErrorKind::BadUrlInDeclarationValueBlock;
                return Err(ParseError::custom(e));
            },
            Token::BadString(..) => {
                let e = StyleParseErrorKind::BadStringInDeclarationValueBlock;
                return Err(ParseError::custom(e));
            },
            Token::CloseParenthesis => {
                let e = StyleParseErrorKind::UnbalancedCloseParenthesisInDeclarationValueBlock;
                return Err(ParseError::custom(e));
            },
            Token::CloseSquareBracket => {
                let e = StyleParseErrorKind::UnbalancedCloseSquareBracketInDeclarationValueBlock;
                return Err(ParseError::custom(e));
            },
            Token::CloseCurlyBracket => {
                let e = StyleParseErrorKind::UnbalancedCloseCurlyBracketInDeclarationValueBlock;
                return Err(ParseError::custom(e));
            },
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
                                    },
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
            },
            Token::ParenthesisBlock => {
                nested!(")");
            },
            Token::CurlyBracketBlock => {
                nested!("}");
            },
            Token::SquareBracketBlock => {
                nested!("]");
            },
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
            },
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
            },
            _ => {},
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
                },
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
                                },
                                // The primary couldn't be resolved (invalid); use the fallback.
                                Err(()) => None,
                            }
                        }
                    },
                    _ => Some(Substitution::from_value(
                        v.to_variable_value(),
                        v.attr_tainted,
                    )),
                },
            }
        },
        SubstitutionFunctionKind::Env => {
            let device = stylist.device();
            device
                .environment()
                .get(&reference.name, device, url_data)
                .map(|v| Substitution::from_value(v, /* attr_tainted */ false))
        },
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
                            },
                            AttributeType::Type(_) => {
                                let value = reference
                                    .attribute_data
                                    .parse_typed_value(&mut parser, url_data, property_id)
                                    .ok()?;
                                let value = value.to_variable_value();
                                Some(Substitution::from_value(
                                    value, /* attr_tainted */ true,
                                ))
                            },
                            AttributeType::RawString | AttributeType::None => {
                                simple_attr_subst(&attr)
                            },
                            AttributeType::Invalid => None,
                        }
                    },
                )
        },
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
    pub identity: Arc<()>,
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

pub(crate) struct ResumableSubstitution<'a> {
    frames: Vec<SubstitutionFrame>,
    seen: Vec<Name>,
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
            returned: None,
            request: None,
            lookup_value: None,
            property_id,
            in_container_query,
            taint: AttrTaint::default(),
            finished: false,
        }
    }

    fn request(&mut self, frame: &mut SubstitutionReferenceFrame, kind: SubstitutionLookupKind) {
        let namespace = frame.reference.attribute_data.namespace().cloned();
        self.request = Some(SubstitutionLookup {
            identity: Arc::new(()),
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
            },
            AttributeType::Type(_) => {
                let value = reference
                    .attribute_data
                    .parse_typed_value(&mut parser, &frame.value.url_data, self.property_id)
                    .ok()?;
                Some(Substitution::from_value(value.to_variable_value(), true))
            },
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
                },
                (SubstitutionLookupKind::RawAttribute, _) => false,
                (SubstitutionLookupKind::Variable, SubstitutionLookupValue::Expand(..)) => true,
                (SubstitutionLookupKind::Variable, SubstitutionLookupValue::Value(value, _)) => {
                    !value.has_references()
                },
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
                let result = self.returned.take().expect("root substitution completed");
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
                },
                SubstitutionFrame::Reference(mut frame) => {
                    match frame.stage {
                        SubstitutionReferenceStage::Start => {
                            let kind = match frame.reference.substitution_kind {
                                SubstitutionFunctionKind::Var => SubstitutionLookupKind::Variable,
                                SubstitutionFunctionKind::Env => {
                                    SubstitutionLookupKind::Environment
                                },
                                SubstitutionFunctionKind::Attr => {
                                    SubstitutionLookupKind::RawAttribute
                                },
                            };
                            self.request(&mut frame, kind);
                        },
                        SubstitutionReferenceStage::Alias(tainted) => {
                            assert_eq!(self.seen.pop().as_ref(), Some(&frame.reference.name));
                            match self.returned.take().expect("alias completed") {
                                Ok(mut value) => {
                                    value.attr_tainted |= tainted;
                                    self.returned = Some(Ok(value));
                                },
                                Err(()) => self.invalid_primary(frame),
                            }
                            continue;
                        },
                        SubstitutionReferenceStage::Fallback => continue,
                        SubstitutionReferenceStage::Lookup(kind) => {
                            match self.lookup_value.take().expect("reply consumed once") {
                                SubstitutionLookupValue::Pending => unreachable!(),
                                SubstitutionLookupValue::Invalid => {
                                    self.invalid_primary(frame);
                                    continue;
                                },
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
                                },
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
                                },
                            }
                        },
                    }
                    self.frames.push(SubstitutionFrame::Reference(frame));
                    if let Some(request) = self.request.as_ref() {
                        return SubstitutionPoll::Lookup(request.clone());
                    }
                },
            }
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
fn value(css:&str)->VariableValue {
    VariableValue::parse(&mut Parser::new(css),None,&UrlExtraData).unwrap()
}
fn put(map:&mut FxHashMap<Name,ComputedRegisteredValue>,name:&str,css:&str,taint:bool) {
    map.insert(name.strip_prefix("--").unwrap_or(name).into(),ComputedRegisteredValue{value:value(css),attr_tainted:taint});
}
fn normalize(result:Result<SubstitutionResult<'_>,()>)->Result<(String,Vec<(usize,usize)>),()> {
    result.map(|r|(r.css.into_owned(),r.attr_taint.0.iter().map(|r|(r.start,r.end)).collect()))
}
fn drain(mut machine:ResumableSubstitution,functions:&ComputedSubstitutionFunctions,stylist:&Stylist,tracker:&mut AttributeTracker,pause:bool)->Result<(String,Vec<(usize,usize)>),()> {
    let mut poll=machine.poll(None);
    loop {match poll {
        SubstitutionPoll::Lookup(request)=>{
            if pause {
                for _ in 0..3 {
                    let again=machine.poll(Some(SubstitutionLookupReply{identity:request.identity.clone(),value:SubstitutionLookupValue::Pending}));
                    let SubstitutionPoll::Lookup(again)=again else {panic!("pending advanced")};
                    assert!(std::ptr::eq(again.identity.as_ref(),request.identity.as_ref()));
                }
            }
            poll=machine.poll(Some(request.read_current(functions,stylist,tracker)));
        },
        SubstitutionPoll::Complete(result)=>{
            assert!(matches!(machine.poll(None),SubstitutionPoll::Finished));
            return normalize(result);
        },
        _=>panic!("unexpected poll"),
    }}
}
fn compare(css:&str,functions:&ComputedSubstitutionFunctions,stylist:&Stylist,attrs:&[(String,String)],container:bool) {
    let v=value(css);
    let mut old_tracker=AttributeTracker{values:attrs.iter().cloned().collect(),queries:Vec::new()};
    let old=normalize(substitute(&v,Some("font-size"),functions,stylist,&computed::Context{in_container_query:container},&mut old_tracker));
    for pause in [false,true] {
        let mut tracker=AttributeTracker{values:attrs.iter().cloned().collect(),queries:Vec::new()};
        let new=drain(ResumableSubstitution::new(v.clone(),Some("font-size"),container),functions,stylist,&mut tracker,pause);
        assert_eq!(old,new,"{css}");assert_eq!(old_tracker.queries,tracker.queries,"query trace {css}");
    }
}

#[test]
fn complete_var_env_fallback_and_empty_equivalence() {
    let mut f=ComputedSubstitutionFunctions::default();
    for (name,css) in [("--a","foo"),("--b","bar"),("--empty",""),("--nested","var(--a)var(--missing, var(--b))")] {put(&mut f.vars,name,css,false)}
    assert_eq!(drain(ResumableSubstitution::new(value("var(--nested)"),None,false),&f,&Stylist::default(),&mut AttributeTracker::default(),true),Ok(("foo/**/bar".into(),vec![])));
    let mut s=Stylist::default();s.device.values.insert("test".into(),value("12px"));
    for css in ["var(--a)","var(--a)var(--empty)var(--b)","var(--nested)","env(test)","env(absent,var(--a))","var(--missing,)","var(--missing)","x var(--a) y env(test) z","var(--a,attr(unused raw-string))"] {compare(css,&f,&s,&[],false)}
}

#[test]
fn attr_forms_and_taint_equivalence() {
    let mut f=ComputedSubstitutionFunctions::default();put(&mut f.attrs,"length","20px",false);
    let attrs=vec![("text".into(),"a\"b".into()),("n".into()," 2.5 ".into()),("length".into(),"20px".into()),("bad".into(),"no".into())];
    for css in ["attr(text)","attr(missing)","attr(missing, fallback)","attr(text raw-string)","attr(n px)","attr(n %)","attr(n number)","attr(bad px,7px)","attr(text unknown,9px)","attr(length type(<length>))","attr(length type(<number>),8)","a attr(n px)var(--missing,attr(text)) z"] {compare(css,&f,&Stylist::default(),&attrs,false)}
    compare("attr(length type(<length>))",&ComputedSubstitutionFunctions::default(),&Stylist::default(),&attrs,true);
}

#[test]
fn typed_attribute_raw_query_is_not_repeated() {
    let mut f=ComputedSubstitutionFunctions::default();put(&mut f.attrs,"length","20px",false);
    let s=Stylist::default();let mut t=AttributeTracker::default();t.values.insert("length".into(),"20px".into());
    let mut m=ResumableSubstitution::new(value("attr(length type(<length>))"),None,false);
    let SubstitutionPoll::Lookup(raw)=m.poll(None) else {panic!()};assert_eq!(raw.kind,SubstitutionLookupKind::RawAttribute);
    let SubstitutionPoll::Lookup(cache)=m.poll(Some(raw.read_current(&f,&s,&mut t))) else {panic!()};assert_eq!(cache.kind,SubstitutionLookupKind::TypedAttribute);
    assert_eq!(t.queries.len(),1);t.values.remove("length");
    for _ in 0..4 {assert!(matches!(m.poll(Some(SubstitutionLookupReply{identity:cache.identity.clone(),value:SubstitutionLookupValue::Pending})),SubstitutionPoll::Lookup(_)));}
    let SubstitutionPoll::Complete(result)=m.poll(Some(cache.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(normalize(result),Ok(("20px".into(),vec![(0,4)])));assert_eq!(t.queries.len(),1);
}

#[test]
fn prefix_pause_preserves_output_and_does_not_choose_fallback() {
    let mut f=ComputedSubstitutionFunctions::default();let s=Stylist::default();let mut t=AttributeTracker::default();
    t.values.insert("prefix".into(),"old".into());t.values.insert("fallback".into(),"wrong".into());
    let mut m=ResumableSubstitution::new(value("attr(prefix raw-string) var(--later,attr(fallback raw-string))"),None,false);
    let SubstitutionPoll::Lookup(prefix)=m.poll(None) else {panic!()};
    let SubstitutionPoll::Lookup(later)=m.poll(Some(prefix.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(later.name,"later");assert_eq!(t.queries.len(),1);
    for _ in 0..4 {assert!(matches!(m.poll(None),SubstitutionPoll::Lookup(_)));}
    t.values.insert("prefix".into(),"changed".into());put(&mut f.vars,"--later","20px",false);
    let SubstitutionPoll::Complete(result)=m.poll(Some(later.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(normalize(result),Ok(("\"old\" 20px".into(),vec![(0,5)])));assert_eq!(t.queries.len(),1);
}

#[test]
fn alias_cycle_and_invalid_fallback_match_old() {
    let mut f=ComputedSubstitutionFunctions::default();put(&mut f.vars,"--a","var(--b,red)",false);put(&mut f.vars,"--b","var(--a,blue)",true);
    compare("var(--a)",&f,&Stylist::default(),&[],false);
    assert_eq!(drain(ResumableSubstitution::new(value("var(--a)"),None,false),&f,&Stylist::default(),&mut AttributeTracker::default(),true),Ok(("blue".into(),vec![(0,4)])));
    put(&mut f.vars,"--a","var(--b)",false);put(&mut f.vars,"--b","var(--a)",false);
    compare("var(--a,green)",&f,&Stylist::default(),&[],false);
}

#[test]
fn reply_identity_and_kind_are_checked_without_advancing() {
    let mut m=ResumableSubstitution::new(value("var(--a)"),None,false);
    let SubstitutionPoll::Lookup(r)=m.poll(None) else {panic!()};
    assert!(matches!(m.poll(Some(SubstitutionLookupReply{identity:Arc::new(()),value:SubstitutionLookupValue::Invalid})),SubstitutionPoll::WrongReply));
    assert!(matches!(m.poll(Some(SubstitutionLookupReply{identity:r.identity.clone(),value:SubstitutionLookupValue::Attribute(None)})),SubstitutionPoll::WrongReply));
    assert!(matches!(m.poll(Some(SubstitutionLookupReply{identity:r.identity.clone(),value:SubstitutionLookupValue::Value(value("var(--b)"),false)})),SubstitutionPoll::WrongReply));
    let SubstitutionPoll::Complete(result)=m.poll(Some(SubstitutionLookupReply{identity:r.identity,value:SubstitutionLookupValue::Value(value("20px"),false)})) else {panic!()};
    assert_eq!(normalize(result),Ok(("20px".into(),vec![])));
}

#[test]
fn unknown_namespace_never_queries_attribute() {
    let mut v=value("attr(text,ok)");v.references.refs[0].attribute_data.namespace=ParsedNamespace::Unknown;
    let mut t=AttributeTracker::default();let result=drain(ResumableSubstitution::new(v,None,false),&ComputedSubstitutionFunctions::default(),&Stylist::default(),&mut t,true);
    assert_eq!(result,Ok(("ok".into(),vec![])));assert!(t.queries.is_empty());
}

#[test]
fn output_limit_and_single_reference_shortcut_match_old() {
    let mut f=ComputedSubstitutionFunctions::default();put(&mut f.vars,"--large",&"a".repeat(1024*1024+1),false);
    compare("var(--large)var(--large)",&f,&Stylist::default(),&[],false);
    assert!(drain(ResumableSubstitution::new(value("var(--large)var(--large)"),None,false),&f,&Stylist::default(),&mut AttributeTracker::default(),true).is_err());
    put(&mut f.vars,"--large",&"a".repeat(2*1024*1024+1),true);
    compare("var(--large)",&f,&Stylist::default(),&[],false);
}

#[test]
fn environment_snapshot_is_retained_across_later_pause() {
    let mut f=ComputedSubstitutionFunctions::default();let mut s=Stylist::default();let mut t=AttributeTracker::default();
    s.device.values.insert("test".into(),value("12px"));
    let mut m=ResumableSubstitution::new(value("env(test) var(--later)"),None,false);
    let SubstitutionPoll::Lookup(env)=m.poll(None) else {panic!()};
    let SubstitutionPoll::Lookup(later)=m.poll(Some(env.read_current(&f,&s,&mut t))) else {panic!()};
    s.device.values.insert("test".into(),value("99px"));assert!(matches!(m.poll(None),SubstitutionPoll::Lookup(_)));
    put(&mut f.vars,"--later","20px",false);
    let SubstitutionPoll::Complete(result)=m.poll(Some(later.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(normalize(result),Ok(("12px 20px".into(),vec![])));
}

#[test]
fn alias_snapshot_survives_provider_map_mutation() {
    let mut f=ComputedSubstitutionFunctions::default();put(&mut f.vars,"--a","var(--b)",false);
    let s=Stylist::default();let mut t=AttributeTracker::default();
    let mut m=ResumableSubstitution::new(value("var(--a)"),None,false);
    let SubstitutionPoll::Lookup(a)=m.poll(None) else {panic!()};
    let SubstitutionPoll::Lookup(b)=m.poll(Some(a.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(b.name,"b");put(&mut f.vars,"--a","wrong",false);
    for _ in 0..3 {assert!(matches!(m.poll(None),SubstitutionPoll::Lookup(_)));}
    put(&mut f.vars,"--b","20px",false);
    let SubstitutionPoll::Complete(result)=m.poll(Some(b.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(normalize(result),Ok(("20px".into(),vec![])));
}

#[test]
fn settled_invalid_alone_selects_attribute_fallback() {
    let f=ComputedSubstitutionFunctions::default();let s=Stylist::default();let mut t=AttributeTracker::default();t.values.insert("fallback".into(),"chosen".into());
    let mut m=ResumableSubstitution::new(value("var(--missing,attr(fallback raw-string))"),None,false);
    let SubstitutionPoll::Lookup(primary)=m.poll(None) else {panic!()};
    assert!(matches!(m.poll(Some(SubstitutionLookupReply{identity:primary.identity.clone(),value:SubstitutionLookupValue::Pending})),SubstitutionPoll::Lookup(_)));assert!(t.queries.is_empty());
    let SubstitutionPoll::Lookup(fallback)=m.poll(Some(SubstitutionLookupReply{identity:primary.identity,value:SubstitutionLookupValue::Invalid})) else {panic!()};
    assert_eq!(fallback.kind,SubstitutionLookupKind::RawAttribute);
    let SubstitutionPoll::Complete(result)=m.poll(Some(fallback.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(normalize(result),Ok(("\"chosen\"".into(),vec![(0,8)])));assert_eq!(t.queries,vec![":fallback"]);
}

#[test]
fn exact_token_separator_and_taint_offsets() {
    let mut f=ComputedSubstitutionFunctions::default();put(&mut f.vars,"--a","foo",false);put(&mut f.vars,"--b","bar",false);
    let mut t=AttributeTracker::default();t.values.insert("n".into(),"2".into());
    let result=drain(ResumableSubstitution::new(value("var(--a)attr(n px)var(--b)"),None,false),&f,&Stylist::default(),&mut t,true);
    assert_eq!(result,Ok(("foo/**/2px/**/bar".into(),vec![(7,10)])));
}
