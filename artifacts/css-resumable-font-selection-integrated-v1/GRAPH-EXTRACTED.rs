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
    fn get_var(&self,_:&PropertyDescriptors,name:&Name)->Option<&ComputedRegisteredValue> {self.vars.get(name)}
    fn get_attr(&self,name:&Name,_:&Namespace)->Option<&ComputedRegisteredValue> {self.attrs.get(name)}
}
#[derive(Default)] struct Device { values:FxHashMap<Name,VariableValue>, contextual:FxHashMap<(Name,u8),VariableValue> }
impl Device {
    fn environment(&self)->&Self {self}
    fn get(&self,name:&Name,_:&Device,url:&UrlExtraData)->Option<VariableValue> {self.contextual.get(&(name.clone(),url.0)).or_else(||self.values.get(name)).cloned()}
}
#[derive(Default)] struct Stylist {device:Device,registrations:FxHashMap<Name,PropertyDescriptors>}
impl Stylist {
    fn device(&self)->&Device {&self.device}
    fn get_custom_property_registration(&self,n:&Name)->&PropertyDescriptors {static UNREGISTERED:PropertyDescriptors=PropertyDescriptors{syntax:None,initial_value:None,inherited:false}; self.registrations.get(n).unwrap_or(&UNREGISTERED)}
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
    pub fn for_each_non_custom<F>(mut self, is_root_element: bool, mut f: F)
    where
        F: FnMut(SingleNonCustomReference),
    {
        // On the root element, rem etc refer to the root's own dependencies.
        if is_root_element {
            if self.intersects(Self::ROOT_FONT_UNITS) {
                self.remove(Self::ROOT_FONT_UNITS);
                self |= Self::FONT_UNITS;
            }
            if self.intersects(Self::ROOT_LH_UNITS) {
                self.remove(Self::ROOT_FONT_UNITS);
                self |= Self::LH_UNITS;
            }
        }

        for (_, r) in self.iter_names() {
            let single = match r {
                Self::FONT_UNITS => SingleNonCustomReference::FontUnits,
                Self::LH_UNITS => SingleNonCustomReference::LhUnits,
                Self::COLOR_SCHEME => SingleNonCustomReference::ColorScheme,
                Self::ROOT_FONT_UNITS
                | Self::ROOT_LH_UNITS
                | Self::FONT_METRICS
                | Self::ROOT_FONT_METRICS
                | Self::FONT_ORIENTATION
                | Self::ROOT_FONT_ORIENTATION
                | Self::VAR
                | Self::ENV
                | Self::ATTR => continue,
                _ => unreachable!("Unexpected single bit value"),
            };
            f(single);
        }
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
use std::{cmp,collections::HashSet};
type RuleCascadeFlags=u8;
type ComputedPropertyValue=VariableValue;
#[derive(Clone,Debug,Eq,PartialEq,Hash)]enum VarType{Custom(Name),Attr(Name,Namespace),NonCustom(SingleNonCustomReference)}
impl VarType{fn namespace(&self)->Option<&Namespace>{match self{Self::Attr(_,n)=>Some(n),_=>None}}}
#[derive(Clone,Copy,Debug,Eq,PartialEq,Hash)]enum SingleNonCustomReference{FontUnits,LhUnits,ColorScheme}
impl SingleNonCustomReference{fn to_prioritary_id(self)->PrioritaryPropertyId{PrioritaryPropertyId}}
#[derive(Clone,Copy)]struct PrioritaryPropertyId;impl PrioritaryPropertyId{fn to_longhand(self)->u8{0}}
#[derive(Default)]struct PrioritaryPropertyIdSet;
#[derive(Clone,Copy)]enum FontTarget{Metric}
impl FontTarget{fn same_as(self,_:Self)->bool{true}}
struct NonCustomPropertyReferences;
#[derive(Clone,Copy)]enum FontDependencyDemand{None}
#[derive(Clone,Copy)]enum PublicationDemand{Ready}
#[derive(Clone,Copy,Eq,PartialEq)]enum ComputationStatus{Ready,Pending}
#[derive(Clone,Copy)]enum FramePhase{References,Prepare,Units,LateDefault,Close,Publish}
#[derive(Clone,Copy)]enum LinkPurpose{Reference,Unit,PrioritySize,LateDefault}
#[derive(Clone,Copy,Eq,PartialEq)]enum ReferenceReadiness{Ready,SemanticOpen,SemanticCycle,ComputationPending}
#[derive(Clone)]struct MetricAction{identity:Arc<()>,root:VarType,owner:VarType,index:usize,prerequisite:FontTarget}
struct Bindings{root:Arc<()>,flags:RuleCascadeFlags,values:FxHashMap<Name,Option<ComputedRegisteredValue>>,pending:HashSet<Name>}
impl Bindings{
 fn valid_for(&mut self,f:RuleCascadeFlags)->bool{self.flags==f}
 fn value(&self,n:&Name,_:&PropertyDescriptors)->Option<Option<ComputedRegisteredValue>>{if self.pending.contains(n){None}else{Some(self.values.get(n).cloned().unwrap_or(None))}}
}
#[derive(Default)]struct LookupCascade{attribute_inputs:FxHashMap<(Name,Namespace),CapturedAttributeInput>}
#[derive(Default)]struct Builder{substitution_functions:ComputedSubstitutionFunctions,invalid_non_custom_properties:HashSet<u8>,inherited_style:Inherited,is_root_element:bool}
#[derive(Default)]struct Inherited{map:ComputedSubstitutionFunctions}impl Inherited{fn custom_properties(&self)->&ComputedSubstitutionFunctions{&self.map}}
mod computed{#[derive(Default)]pub struct Context{pub builder:super::Builder,pub included_cascade_flags:u8,pub computations:Vec<String>}impl Context{pub fn is_root_element(&self)->bool{self.builder.is_root_element}}}
#[derive(Clone)]struct Initial{css:String,url_data:UrlExtraData}
struct PropertyDescriptors{syntax:Option<SyntaxDescriptor>,initial_value:Option<Initial>,inherited:bool}
impl PropertyDescriptors{fn is_universal(&self)->bool{self.syntax.is_none()}fn inherits(&self)->bool{self.inherited}}
enum CSSWideKeyword{Initial}
impl CSSWideKeyword{fn parse(p:&mut Parser)->Result<Self,ParseError>{p.expect_ident_matching("initial")?;p.expect_exhausted()?;Ok(Self::Initial)}}
impl SpecifiedRegisteredValue{
 fn depends_on_color_scheme(&self)->bool{false}
 fn to_computed_value(self,c:&mut computed::Context)->ComputedRegisteredValue{c.computations.push(self.0.css.clone());ComputedRegisteredValue{value:self.0,attr_tainted:false}}
}
fn prepare_invalid_custom_kind(_:&Name,r:&PropertyDescriptors,_:&computed::Context)->PreparedCustomKind{
 match &r.initial_value{Some(v)=>PreparedCustomKind::Initial(SpecifiedRegisteredValue(tokens(&v.css,v.url_data.0))),None=>PreparedCustomKind::Invalid}
}
fn apply_substituted_value(n:&Name,_:Option<&Namespace>,_:&UrlExtraData,input:SubstitutionInput,s:&Stylist,c:&mut computed::Context){
 let SubstitutionInput::Prepared(v)=input;match v{Ok(v)=>{let mut value=ComputedRegisteredValue::universal(Arc::new(tokens(&v.css,0)));value.attr_tainted=v.attr_tainted;c.builder.substitution_functions.insert_var(s.get_custom_property_registration(n),n,value)},Err(())=>handle_invalid_at_computed_value_time(n,s.get_custom_property_registration(n),c)}
}
enum SubstitutionInput{Prepared(Result<Substitution<'static>,()>)}
fn compute_value(css:&str,url:&UrlExtraData,_:&PropertyDescriptors,_:&mut computed::Context,_:AttrTaint,_:Option<PropertyIdRef>)->Result<ComputedRegisteredValue,()>{Ok(ComputedRegisteredValue::universal(Arc::new(tokens(css,url.0))))}
fn substitute_references_if_needed_and_apply(_: &Name,_:Option<&Namespace>,_:&VariableValue,_:&Stylist,_:&mut computed::Context,_:&mut AttributeTracker){panic!("guarded value must not substitute twice")}
fn tokens(css:&str,url:u8)->VariableValue{VariableValue::parse(&mut Parser::new(css),None,&UrlExtraData(url)).unwrap()}
impl ComputedSubstitutionFunctions{
 fn insert_var(&mut self,_:&PropertyDescriptors,n:&Name,v:ComputedRegisteredValue){self.vars.insert(n.clone(),v);}
 fn remove_var(&mut self,_:&PropertyDescriptors,n:&Name){self.vars.remove(n);}
 fn remove_attr(&mut self,n:&Name,_:&Namespace){self.attrs.remove(n);}
 fn get(&self,_:&PropertyDescriptors,n:&Name)->Option<&ComputedRegisteredValue>{self.vars.get(n)}
}
struct TraversalFrame{guarded_custom:Option<GuardedCustomFrame>,var:VarType,index:usize,lowlink:usize,self_ref:bool,phase:FramePhase,waiting:Option<(VarType,LinkPurpose)>,reference_reply:Option<(VarType,ReferenceReadiness)>,prepared_custom:Option<PreparedCustomValue>,value:Option<Arc<VariableValue>>,value_non_custom_refs:ReferenceFlags,unit_cursor:usize,registered:bool,unit_links:Vec<SingleNonCustomReference>}
enum FrameStep{Link(VarType),Complete(VisitResult),ComputedSize,Pending(Option<FontTarget>)}
struct Context{frames:Vec<TraversalFrame>,frame_reply:Option<(VarType,VisitResult)>,deferred_size:Option<TraversalFrame>,finished_root:Option<VisitResult>,metric_action:Option<MetricAction>,frame_root:Option<VarType>,computed_context:&'static mut computed::Context,var_info:Vec<VarInfo>,stack:Vec<usize>,stylist:&'static mut Stylist,indices:FxHashMap<VarType,usize>,specs:FxHashMap<Name,VariableValue>,published:Vec<Name>,lookup_bindings:Bindings,cascade:LookupCascade,environment_inputs:Vec<(Name,UrlExtraData,Option<VariableValue>)>,blocked:HashSet<Name>,unit_ready:bool,unit_visits:Vec<SingleNonCustomReference>,lookup_reply:Option<(LonghandId,FontSelectionReply)>}
impl Context{
 fn new()->Self{Self{frames:vec![],frame_reply:None,deferred_size:None,finished_root:None,metric_action:None,frame_root:None,computed_context:Box::leak(Box::default()),var_info:vec![],stack:vec![],stylist:Box::leak(Box::default()),indices:FxHashMap::default(),specs:FxHashMap::default(),published:vec![],lookup_bindings:Bindings{root:Arc::new(()),flags:0,values:FxHashMap::default(),pending:HashSet::new()},cascade:LookupCascade::default(),environment_inputs:vec![],blocked:HashSet::new(),unit_ready:false,unit_visits:vec![],lookup_reply:None}}
 fn computed_size_ready(&self,_:usize)->bool{false}
 fn apply_prioritary_property(&mut self,_:PrioritaryPropertyId,_:&mut AttributeTracker)->ComputationStatus{unreachable!()}
 fn visited(&self,var:&VarType)->Option<VisitResult>{self.indices.get(var).map(|&i|match self.var_info[i].publication.readiness(){NodeReadiness::SemanticOpen=>VisitResult::SemanticOpen(i),NodeReadiness::ComputationPending=>VisitResult::ComputationPending(i),NodeReadiness::Complete=>VisitResult::Complete,NodeReadiness::CycleSettled=>VisitResult::CycleSettled})}
 fn record_lookup_publication(&mut self,i:usize){assert!(self.var_info[i].publication.can_retire());let VarType::Custom(n)=self.indices.iter().find(|(_,v)|**v==i).unwrap().0 else{panic!()};self.published.push(n.clone());self.lookup_bindings.pending.remove(n);self.lookup_bindings.values.insert(n.clone(),self.computed_context.builder.substitution_functions.vars.get(n).cloned());}
 fn add(&mut self,n:&str,css:&str,url:u8,registered:bool){self.specs.insert(n.into(),tokens(css,url));self.lookup_bindings.pending.insert(n.into());self.stylist.registrations.insert(n.into(),PropertyDescriptors{syntax:registered.then(||SyntaxDescriptor("<length>".into())),initial_value:registered.then(||Initial{css:"8px".into(),url_data:UrlExtraData(0)}),inherited:false});}
}
fn start_frame(var:VarType,c:&mut Context,_:&mut AttributeTracker)->Result<TraversalFrame,VisitResult>{
 if let Some(result)=c.visited(&var){return Err(result)};
 if let VarType::NonCustom(unit)=var{c.unit_visits.push(unit);return Err(if c.unit_ready{VisitResult::Complete}else{VisitResult::ComputationPending(usize::MAX)})}
 let VarType::Custom(n)=&var else{panic!("unexpected legacy attribute graph")};
 if c.blocked.contains(n){return Err(VisitResult::ComputationPending(usize::MAX))}
 let registered=!c.stylist.get_custom_property_registration(n).is_universal();
 let value=c.specs.get(n).unwrap().clone();let i=c.var_info.len();c.indices.insert(var.clone(),i);c.var_info.push(VarInfo{var:Some(var.clone()),lowlink:i,publication:NodePublication::SemanticOpen});c.stack.push(i);
 Ok(TraversalFrame{guarded_custom:None,var,index:i,lowlink:i,self_ref:false,phase:FramePhase::References,waiting:None,reference_reply:None,prepared_custom:None,value:Some(Arc::new(value)),value_non_custom_refs:ReferenceFlags::empty(),unit_cursor:0,registered,unit_links:vec![]})
}

struct FontSelectionReply{value:Arc<VariableValue>,generation:Arc<()>,lookup:Option<SubstitutionLookupReply>}
struct MetricLookup{action:MetricAction,flags:u8,generation:Arc<()>,depth:usize,semantic_floor:usize,request:SubstitutionLookup,longhand:LonghandId,value:Arc<VariableValue>}
enum PreparedCustomKind {
    Existing,
    Typed(SpecifiedRegisteredValue),
    Initial(SpecifiedRegisteredValue),
    Invalid,
}
pub(crate) struct PreparedCustomValue {
    substitution: Result<Substitution<'static>, ()>,
    url_data: UrlExtraData,
    kind: PreparedCustomKind,
}
impl PreparedCustomValue {
    pub fn depends_on_color_scheme(&self) -> bool {
        match &self.kind {
            PreparedCustomKind::Typed(value) | PreparedCustomKind::Initial(value) => {
                value.depends_on_color_scheme()
            }
            PreparedCustomKind::Existing | PreparedCustomKind::Invalid => false,
        }
    }

    pub fn apply(self, name: &Name, stylist: &Stylist, context: &mut computed::Context) {
        let registration = stylist.get_custom_property_registration(name);
        match self.kind {
            PreparedCustomKind::Typed(specified) => {
                let mut value = specified.to_computed_value(context);
                value.attr_tainted |= self.substitution.unwrap().attr_tainted;
                context
                    .builder
                    .substitution_functions
                    .insert_var(registration, name, value);
            }
            PreparedCustomKind::Initial(specified) => {
                let value = specified.to_computed_value(context);
                context
                    .builder
                    .substitution_functions
                    .insert_var(registration, name, value);
            }
            PreparedCustomKind::Invalid => {
                handle_invalid_at_computed_value_time(name, registration, context)
            }
            PreparedCustomKind::Existing => apply_substituted_value(
                name,
                None,
                &self.url_data,
                SubstitutionInput::Prepared(self.substitution),
                stylist,
                context,
            ),
        }
    }
}
pub(crate) fn prepare_completed_custom_value(
    name: &Name,
    url_data: &UrlExtraData,
    result: Result<SubstitutionResult<'static>, ()>,
    stylist: &Stylist,
    context: &computed::Context,
) -> (PreparedCustomValue, ReferenceFlags) {
    let mut flags = ReferenceFlags::empty();
    let substitution = result.and_then(|result| {
        let mut parser = Parser::new(&result.css);
        let parsed = VariableValue::parse(&mut parser, None, url_data).map_err(|_| ())?;
        drop(parser);
        flags = parsed.references.flags;
        Ok(Substitution {
            css: result.css,
            first_token_type: parsed.first_token_type,
            last_token_type: parsed.last_token_type,
            attr_tainted: !result.attr_taint.is_empty(),
        })
    });
    (
        prepare_custom_substitution(name, url_data.clone(), substitution, stylist, context),
        flags,
    )
}
fn prepare_custom_substitution(
    name: &Name,
    url_data: UrlExtraData,
    substitution: Result<Substitution<'static>, ()>,
    stylist: &Stylist,
    context: &computed::Context,
) -> PreparedCustomValue {
    let registration = stylist.get_custom_property_registration(name);
    let mut kind = match substitution.as_ref() {
        Err(()) => PreparedCustomKind::Invalid,
        Ok(value) => {
            let mut parser = Parser::new(&value.css);
            if parser.try_parse(CSSWideKeyword::parse).is_ok() || registration.is_universal() {
                PreparedCustomKind::Existing
            } else if let Some(syntax) = registration.syntax.as_ref() {
                let taint = if value.attr_tainted {
                    AttrTaint::new_fully_tainted(value.css.len())
                } else {
                    AttrTaint::default()
                };
                let mut parser = Parser::new(&value.css);
                match SpecifiedRegisteredValue::parse(
                    &mut parser,
                    syntax,
                    &url_data,
                    None,
                    AllowComputationallyDependent::Yes,
                    taint,
                    Some(PropertyIdRef::from(name)),
                ) {
                    Ok(parsed) => PreparedCustomKind::Typed(parsed),
                    Err(_) => PreparedCustomKind::Invalid,
                }
            } else {
                PreparedCustomKind::Invalid
            }
        }
    };
    if matches!(kind, PreparedCustomKind::Invalid) {
        kind = prepare_invalid_custom_kind(name, registration, context);
    }
    PreparedCustomValue {
        substitution,
        url_data,
        kind,
    }
}
pub fn handle_invalid_at_computed_value_time(
    name: &Name,
    registration: &PropertyDescriptors,
    context: &mut computed::Context,
) {
    if !registration.is_universal() {
        // For the root element, inherited maps are empty. We should just
        // use the initial value if any, rather than removing the name.
        if registration.inherits() && !context.builder.is_root_element {
            let inherited = context.builder.inherited_style.custom_properties();
            if let Some(value) = inherited.get(registration, name) {
                context.builder.substitution_functions.insert_var(
                    registration,
                    name,
                    value.clone(),
                );
                return;
            }
        } else if let Some(ref initial_value) = registration.initial_value
            && let Ok(initial_value) = compute_value(
                &initial_value.css,
                &initial_value.url_data,
                registration,
                context,
                AttrTaint::default(),
                Some(PropertyIdRef::from(name)),
            )
        {
            context
                .builder
                .substitution_functions
                .insert_var(registration, name, initial_value);
            return;
        }
    }
    context
        .builder
        .substitution_functions
        .remove_var(registration, name);
}
    enum ClosedValue {
        Prepared(Name, PreparedCustomValue),
        Substitute(VarType, Arc<ComputedPropertyValue>),
        Prioritary(PrioritaryPropertyId),
    }
    enum NodePublication<T> {
        SemanticOpen,
        CycleUnsettled,
        Pending(T),
        Applying,
        Complete,
        CycleSettled,
    }
    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum NodeReadiness {
        SemanticOpen,
        ComputationPending,
        Complete,
        CycleSettled,
    }
    impl<T> NodePublication<T> {
        fn readiness(&self) -> NodeReadiness {
            match self {
                Self::SemanticOpen => NodeReadiness::SemanticOpen,
                Self::CycleUnsettled | Self::Pending(_) | Self::Applying => {
                    NodeReadiness::ComputationPending
                }
                Self::Complete => NodeReadiness::Complete,
                Self::CycleSettled => NodeReadiness::CycleSettled,
            }
        }

        fn close(&mut self, value: T) {
            assert!(matches!(self, Self::SemanticOpen));
            *self = Self::Pending(value);
        }

        fn take_ready(&mut self, prerequisites_ready: bool) -> Option<T> {
            if !prerequisites_ready {
                return None;
            }
            assert!(matches!(self, Self::Pending(_)));
            let Self::Pending(value) = std::mem::replace(self, Self::Applying) else {
                unreachable!()
            };
            Some(value)
        }

        fn finish(&mut self) {
            assert!(matches!(self, Self::Applying));
            *self = Self::Complete;
        }

        fn begin_cycle(&mut self) {
            assert!(matches!(self, Self::SemanticOpen));
            *self = Self::CycleUnsettled;
        }

        fn settle_cycle(&mut self) {
            assert!(matches!(self, Self::CycleUnsettled));
            *self = Self::CycleSettled;
        }

        fn can_retire(&self) -> bool {
            matches!(self, Self::Complete | Self::CycleSettled)
        }
    }
    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum VisitResult {
        SemanticOpen(usize),
        ComputationPending(usize),
        ComputedSize(usize),
        Complete,
        CycleSettled,
    }
    struct VarInfo {
        /// The name of the variable. It will be taken when the corresponding variable is popped
        /// from the stack, which serves as a mark for whether the variable is currently in the
        /// stack below.
        var: Option<VarType>,
        /// If the variable is in a dependency cycle, lowlink represents a smaller index which
        /// corresponds to a variable in the same strong connected component, which is known to be
        /// accessible from this variable. It is not necessarily the root, though.
        lowlink: usize,
        publication: NodePublication<ClosedValue>,
    }
    struct GuardedCustomFrame {
        substitution: ResumableSubstitution<'static>,
        request: Option<SubstitutionLookup>,
        flags: RuleCascadeFlags,
        generation: Arc<()>,
    }
impl Context{
        fn poll_root(
            &mut self,
            var: VarType,
            references: &NonCustomPropertyReferences,
            attribute_tracker: &mut AttributeTracker,
            publication_ready: &mut impl FnMut(
                FontDependencyDemand,
                &PrioritaryPropertyIdSet,
                Option<LonghandId>,
            ) -> PublicationDemand,
        ) -> VisitResult {
            if let Some(root) = &self.frame_root {
                assert_eq!(*root, var);
            } else {
                assert!(self.frames.is_empty() && self.frame_reply.is_none());
                self.frame_root = Some(var.clone());
                match start_frame(var, self, attribute_tracker) {
                    Ok(mut frame) => {
                        frame.enter_guarded_custom(Vec::new(), self);
                        self.frames.push(frame);
                    }
                    Err(result) => {
                        self.frame_root = None;
                        return result;
                    }
                }
            }
            if let Some(action) = &self.metric_action {
                return VisitResult::ComputationPending(action.index);
            }
            loop {
                let result =
                    self.poll_frames(references, attribute_tracker, publication_ready, 0, 0, None);
                if matches!(result, VisitResult::ComputationPending(_)) {
                    return result;
                }
                if let Some(frame) = self.deferred_size.take() {
                    assert!(self.finished_root.is_none());
                    self.finished_root = Some(result);
                    self.frames.push(frame);
                    continue;
                }
                self.frame_root = None;
                return self.finished_root.take().unwrap_or(result);
            }
        }
        fn poll_frames(
            &mut self,
            references: &NonCustomPropertyReferences,
            attribute_tracker: &mut AttributeTracker,
            publication_ready: &mut impl FnMut(
                FontDependencyDemand,
                &PrioritaryPropertyIdSet,
                Option<LonghandId>,
            ) -> PublicationDemand,
            depth: usize,
            semantic_floor: usize,
            attribute_attempt: Option<&Arc<()>>,
        ) -> VisitResult {
            loop {
                assert!(self.frames.len() > depth);
                let mut frame = self.frames.pop().expect("Active root owns a frame");
                if let Some((target, _)) = &frame.waiting {
                    if attribute_attempt.is_some()
                        && frame.guarded_custom.is_none()
                        && matches!(target, VarType::Attr(..))
                    {
                        let index = frame.index;
                        self.frames.push(frame);
                        return VisitResult::ComputationPending(index);
                    }
                    if let Some((_, VisitResult::SemanticOpen(index))) = &self.frame_reply {
                        if *index < semantic_floor {
                            let index = *index;
                            self.frames.push(frame);
                            return VisitResult::ComputationPending(index);
                        }
                    }
                    if let Some((target, result)) = self.frame_reply.take() {
                        assert!(frame.receive(target, result, self));
                    } else {
                        let target = target.clone();
                        let guards = frame
                            .guarded_custom
                            .as_ref()
                            .and_then(|state| state.request.as_ref())
                            .map(|request| request.guards.clone());
                        self.frames.push(frame);
                        match start_frame(target.clone(), self, attribute_tracker) {
                            Ok(mut child) => {
                                if let Some(guards) = guards {
                                    child.enter_guarded_custom(guards, self);
                                }
                                self.frames.push(child);
                            }
                            Err(VisitResult::ComputationPending(index))
                                if self.frames.last().is_some_and(|parent| {
                                    parent.accepts_computed_size(
                                        self.computed_context.is_root_element(),
                                    )
                                }) && self.computed_size_ready(index) =>
                            {
                                self.frame_reply = Some((target, VisitResult::ComputedSize(index)));
                            }
                            Err(VisitResult::ComputationPending(index)) => {
                                return VisitResult::ComputationPending(index);
                            }
                            Err(VisitResult::SemanticOpen(index)) if index < semantic_floor => {
                                return VisitResult::ComputationPending(index);
                            }
                            Err(result) => self.frame_reply = Some((target, result)),
                        }
                        continue;
                    }
                } else {
                    assert!(self.frame_reply.is_none());
                }
                match frame.step(references, self, attribute_tracker, publication_ready) {
                    FrameStep::Link(_) => self.frames.push(frame),
                    FrameStep::Pending(prerequisite) => {
                        let index = frame.index;
                        if depth == 0 {
                            self.metric_action = prerequisite.map(|prerequisite| MetricAction {
                                identity: Arc::new(()),
                                root: self.frame_root.as_ref().unwrap().clone(),
                                owner: frame.var.clone(),
                                index,
                                prerequisite,
                            });
                        }
                        self.frames.push(frame);
                        return VisitResult::ComputationPending(index);
                    }
                    FrameStep::ComputedSize => {
                        assert!(self.deferred_size.is_none());
                        assert!(self.frames.last().is_some_and(|parent| {
                            parent.accepts_computed_size(self.computed_context.is_root_element())
                        }));
                        let index = frame.index;
                        let var = frame.var.clone();
                        self.deferred_size = Some(frame);
                        self.frame_reply = Some((var, VisitResult::ComputedSize(index)));
                    }
                    FrameStep::Complete(result) => {
                        if self.frames.len() == depth {
                            return result;
                        }
                        assert!(self.frame_reply.is_none());
                        self.frame_reply = Some((frame.var, result));
                    }
                }
            }
        }
        fn publish_closed(
            &mut self,
            index: usize,
            attr_tracker: &mut AttributeTracker,
        ) -> ComputationStatus {
            let priority = match &self.var_info[index].publication {
                NodePublication::Pending(ClosedValue::Prioritary(id)) => Some(*id),
                _ => None,
            };
            if let Some(id) = priority {
                let status = self.apply_prioritary_property(id, attr_tracker);
                if status != ComputationStatus::Ready {
                    return status;
                }
            }
            let value = self.var_info[index].publication.take_ready(true).unwrap();
            match value {
                ClosedValue::Prepared(name, prepared) => {
                    prepared.apply(&name, self.stylist, self.computed_context);
                }
                ClosedValue::Substitute(var, value) => {
                    let name = match &var {
                        VarType::Custom(name) | VarType::Attr(name, _) => name,
                        VarType::NonCustom(_) => unreachable!(),
                    };
                    substitute_references_if_needed_and_apply(
                        name,
                        var.namespace(),
                        &value,
                        self.stylist,
                        self.computed_context,
                        attr_tracker,
                    );
                }
                ClosedValue::Prioritary(_) => {}
            }
            self.var_info[index].publication.finish();
            self.record_lookup_publication(index);
            ComputationStatus::Ready
        }
        fn handle_loop(&mut self, name: &VarType) {
            match name {
                VarType::Attr(name, namespace) => {
                    self.computed_context
                        .builder
                        .substitution_functions
                        .remove_attr(name, namespace);
                }
                VarType::Custom(name) => {
                    // This variable is in a loop. Resolve to invalid.
                    handle_invalid_at_computed_value_time(
                        name,
                        self.stylist.get_custom_property_registration(name),
                        self.computed_context,
                    );
                }
                VarType::NonCustom(non_custom) => {
                    self.computed_context
                        .builder
                        .invalid_non_custom_properties
                        .insert(non_custom.to_prioritary_id().to_longhand());
                }
            }
        }
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
        fn metric_action_is_current(&self, action: &MetricAction, depth: usize) -> bool {
            let Some(current) = &self.metric_action else {
                return false;
            };
            std::ptr::eq(current.identity.as_ref(), action.identity.as_ref())
                && current.root == action.root
                && current.owner == action.owner
                && current.index == action.index
                && current.prerequisite.same_as(action.prerequisite)
                && self.frame_root.as_ref() == Some(&action.root)
                && depth > 0
                && self.frames.get(depth - 1).is_some_and(|frame| {
                    frame.index == action.index
                        && frame.var == action.owner
                        && matches!(frame.phase, FramePhase::Publish)
                })
                && matches!(
                    self.var_info[action.index].publication,
                    NodePublication::Pending(_)
                )
        }
        fn resolve_metric_lookup_inner(
            &mut self,
            state: &MetricLookup,
            references: &NonCustomPropertyReferences,
            tracker: &mut AttributeTracker,
            publication_ready: &mut impl FnMut(
                FontDependencyDemand,
                &PrioritaryPropertyIdSet,
                Option<LonghandId>,
            ) -> PublicationDemand,
        ) -> Result<bool, ()> {
            if !self.metric_action_is_current(&state.action, state.depth)
                || state.flags != self.computed_context.included_cascade_flags
                || !Arc::ptr_eq(&state.generation, &self.lookup_bindings.root)
            {
                return Err(());
            }
            let mut value = if self.frames.len() > state.depth {
                None
            } else {
                self.owned_lookup_value(&state.request, tracker)?
            };
            if value.is_none() {
                let target = match state.request.kind {
                    SubstitutionLookupKind::Variable => VarType::Custom(state.request.name.clone()),
                    SubstitutionLookupKind::TypedAttribute => VarType::Attr(
                        state.request.name.clone(),
                        state.request.namespace.clone().ok_or(())?,
                    ),
                    _ => return Err(()),
                };
                let result = if self.frames.len() > state.depth {
                    if self.frames[state.depth].var != target {
                        return Err(());
                    }
                    self.poll_frames(
                        references,
                        tracker,
                        publication_ready,
                        state.depth,
                        state.semantic_floor,
                        state.request.attribute_attempt.as_ref(),
                    )
                } else {
                    if self.frames.len() != state.depth || self.frame_reply.is_some() {
                        return Err(());
                    }
                    match start_frame(target, self, tracker) {
                        Ok(mut frame) => {
                            if state.request.attribute_attempt.is_some() {
                                frame.enter_guarded_custom(state.request.guards.clone(), self);
                            }
                            self.frames.push(frame);
                            self.poll_frames(
                                references,
                                tracker,
                                publication_ready,
                                state.depth,
                                state.semantic_floor,
                                state.request.attribute_attempt.as_ref(),
                            )
                        }
                        Err(result) => result,
                    }
                };
                if !matches!(result, VisitResult::Complete | VisitResult::CycleSettled) {
                    return Ok(false);
                }
                value = self.owned_lookup_value(&state.request, tracker)?;
            }
            let Some(value) = value else { return Ok(false) };
            if self.frames.len() != state.depth || self.lookup_reply.is_some() {
                return Err(());
            }
            self.lookup_reply = Some((
                state.longhand,
                FontSelectionReply {
                    value: state.value.clone(),
                    generation: state.generation.clone(),
                    lookup: Some(SubstitutionLookupReply {
                        identity: state.request.identity.clone(),
                        value,
                    }),
                },
            ));
            Ok(true)
        }
}
impl TraversalFrame{
fn accepts_computed_size(&self,_:bool)->bool{false}
        fn enter_guarded_custom(&mut self, guards: Vec<SubstitutionGuard>, context: &Context) {
            let VarType::Custom(name) = &self.var else {
                return;
            };
            assert!(self.guarded_custom.is_none());
            self.guarded_custom = Some(GuardedCustomFrame {
                substitution: ResumableSubstitution::for_custom(
                    (**self.value.as_ref().unwrap()).clone(),
                    name.clone(),
                    guards,
                ),
                request: None,
                flags: context.computed_context.included_cascade_flags,
                generation: context.lookup_bindings.root.clone(),
            });
        }
        fn guarded_references(
            &mut self,
            context: &mut Context,
            tracker: &mut AttributeTracker,
        ) -> Option<FrameStep> {
            let state = self.guarded_custom.as_mut().unwrap();
            if state.flags != context.computed_context.included_cascade_flags
                || !Arc::ptr_eq(&state.generation, &context.lookup_bindings.root)
            {
                return Some(FrameStep::Pending(None));
            }
            if state.substitution.body_marked()
                || self
                    .reference_reply
                    .as_ref()
                    .is_some_and(|(_, reply)| matches!(reply, ReferenceReadiness::SemanticOpen))
            {
                self.reference_reply = None;
                self.self_ref |= state.substitution.body_marked();
                self.phase = FramePhase::LateDefault;
                return None;
            }
            self.reference_reply = None;
            let mut reply = None;
            loop {
                if let Some(request) = state.request.as_ref() {
                    let value = match context.owned_lookup_value(request, tracker) {
                        Ok(Some(value)) => value,
                        Ok(None) => {
                            if request.kind != SubstitutionLookupKind::Variable {
                                return Some(FrameStep::Pending(None));
                            }
                            SubstitutionGuard::mark_reentry(
                                &request.guards,
                                &SubstitutionGuardKey::Property(PropertyId::Custom(
                                    request.name.clone(),
                                )),
                            );
                            let target = VarType::Custom(request.name.clone());
                            return Some(self.link(target, LinkPurpose::Reference));
                        }
                        Err(()) => return Some(FrameStep::Pending(None)),
                    };
                    reply = Some(SubstitutionLookupReply {
                        identity: request.identity.clone(),
                        value,
                    });
                    state.request = None;
                }
                match state.substitution.poll(reply.take()) {
                    SubstitutionPoll::Lookup(request) => state.request = Some(request),
                    SubstitutionPoll::Complete(result) => {
                        if state.substitution.body_marked() {
                            self.self_ref = true;
                            self.phase = FramePhase::LateDefault;
                            return None;
                        }
                        let VarType::Custom(name) = &self.var else {
                            unreachable!()
                        };
                        let (prepared, flags) = prepare_completed_custom_value(
                            name,
                            &self.value.as_ref().unwrap().url_data,
                            result,
                            context.stylist,
                            context.computed_context,
                        );
                        self.value_non_custom_refs |= flags;
                        self.value_non_custom_refs
                            .remove(ReferenceFlags::COLOR_SCHEME);
                        if prepared.depends_on_color_scheme() {
                            self.value_non_custom_refs |= ReferenceFlags::COLOR_SCHEME;
                        }
                        self.prepared_custom = Some(prepared);
                        self.phase = FramePhase::Prepare;
                        return None;
                    }
                    SubstitutionPoll::WrongReply | SubstitutionPoll::Finished => {
                        unreachable!("Guarded frame owns its exact lookup reply")
                    }
                }
            }
        }
        fn link(&mut self, target: VarType, purpose: LinkPurpose) -> FrameStep {
            assert!(self.waiting.is_none());
            self.waiting = Some((target.clone(), purpose));
            FrameStep::Link(target)
        }
        fn receive(&mut self, target: VarType, result: VisitResult, context: &Context) -> bool {
            let Some((waiting, purpose)) = self.waiting.as_ref() else {
                return false;
            };
            if *waiting != target || matches!(result, VisitResult::ComputationPending(_)) {
                return false;
            }
            if let VisitResult::ComputedSize(index) = result {
                if !self.accepts_computed_size(context.computed_context.is_root_element())
                    || !context.computed_size_ready(index)
                {
                    return false;
                }
            }
            if let VisitResult::SemanticOpen(next_index) = result {
                let next = &context.var_info[next_index];
                assert!(matches!(
                    next.publication.readiness(),
                    NodeReadiness::SemanticOpen
                ));
                if next_index > self.index {
                    self.lowlink = cmp::min(self.lowlink, next.lowlink);
                } else if next_index == self.index {
                    self.self_ref = true;
                } else if next.var.is_some() {
                    self.lowlink = cmp::min(self.lowlink, next_index);
                }
            }
            match purpose {
                LinkPurpose::Reference => {
                    assert!(self.reference_reply.is_none());
                    self.reference_reply = Some((
                        target,
                        match result {
                            VisitResult::SemanticOpen(_) => ReferenceReadiness::SemanticOpen,
                            VisitResult::Complete => ReferenceReadiness::Ready,
                            VisitResult::CycleSettled => ReferenceReadiness::SemanticCycle,
                            VisitResult::ComputationPending(_) | VisitResult::ComputedSize(_) => {
                                unreachable!()
                            }
                        },
                    ));
                }
                LinkPurpose::Unit => self.unit_cursor += 1,
                LinkPurpose::PrioritySize | LinkPurpose::LateDefault => {}
            }
            self.waiting = None;
            true
        }
fn step(&mut self,_:&NonCustomPropertyReferences,context:&mut Context,attribute_tracker:&mut AttributeTracker,_:&mut impl FnMut(FontDependencyDemand,&PrioritaryPropertyIdSet,Option<LonghandId>)->PublicationDemand)->FrameStep{
 loop{match self.phase{
 FramePhase::References=>{assert!(self.guarded_custom.is_some());if let Some(step)=self.guarded_references(context,attribute_tracker){return step;}},
 FramePhase::Prepare=>{if self.registered{self.value_non_custom_refs.for_each_non_custom(context.computed_context.is_root_element(),|r|self.unit_links.push(r));}self.phase=FramePhase::Units;},
                     FramePhase::Units => {
                        if let Some(reference) = self.unit_links.get(self.unit_cursor) {
                            return self.link(VarType::NonCustom(*reference), LinkPurpose::Unit);
                        }
                        self.phase = FramePhase::LateDefault;
                    },
 FramePhase::LateDefault=>{self.phase=FramePhase::Close;},
                     FramePhase::Close => {
                        context.var_info[self.index].lowlink = self.lowlink;
                        if self.lowlink != self.index {
                            return FrameStep::Complete(VisitResult::SemanticOpen(self.index));
                        }
                        let mut in_loop = self.self_ref;
                        let mut members = SmallVec::<[usize; 5]>::new();
                        loop {
                            let index = context.stack.pop().expect("Frame's SCC remains owned");
                            let var = context.var_info[index].var.take().expect("Node pops once");
                            if index != self.index {
                                in_loop = true;
                            }
                            if in_loop {
                                context.var_info[index].publication.begin_cycle();
                                members.push(index);
                                context.handle_loop(&var);
                            }
                            if index == self.index {
                                assert_eq!(var, self.var);
                                break;
                            }
                        }
                        if in_loop {
                            for index in members {
                                context.var_info[index].publication.settle_cycle();
                                context.record_lookup_publication(index);
                            }
                            return FrameStep::Complete(VisitResult::CycleSettled);
                        }
                        let publication = match &self.var {
                            VarType::Custom(name) | VarType::Attr(name, _) => {
                                if let Some(prepared) = self.prepared_custom.take() {
                                    ClosedValue::Prepared(name.clone(), prepared)
                                } else {
                                    ClosedValue::Substitute(
                                        self.var.clone(),
                                        self.value.take().unwrap(),
                                    )
                                }
                            }
                            VarType::NonCustom(reference) => {
                                ClosedValue::Prioritary(reference.to_prioritary_id())
                            }
                        };
                        context.var_info[self.index].publication.close(publication);
                        self.phase = FramePhase::Publish;
                    },
 FramePhase::Publish=>{assert!(context.publish_closed(self.index,attribute_tracker)==ComputationStatus::Ready);return FrameStep::Complete(VisitResult::Complete);}
 }}
}
}
type LonghandId=u8;
struct Driver{engine:ResumableSubstitution<'static>,request:Option<SubstitutionLookup>,floor:usize}
impl Driver{
 fn new(css:&str,url:u8)->Self{Self{engine:ResumableSubstitution::new(tokens(css,url),None,false),request:None,floor:0}}
 fn poll(&mut self,c:&mut Context,t:&mut AttributeTracker)->Option<Result<String,()>>{
  let mut reply=None;
  for _ in 0..100000{
   if let Some(request)=self.request.as_ref(){
    let mut value=if c.frames.is_empty(){c.owned_lookup_value(request,t).unwrap()}else{None};
    if value.is_none(){
     if c.frames.is_empty(){
      self.floor=c.var_info.len();let target=VarType::Custom(request.name.clone());
      let mut frame=match start_frame(target.clone(),c,t){Ok(f)=>f,Err(VisitResult::ComputationPending(_))=>return None,Err(_)=>panic!("unjoined root")};
      frame.enter_guarded_custom(request.guards.clone(),c);c.frames.push(frame);c.frame_root=Some(target);
     }
     let result=c.poll_frames(&NonCustomPropertyReferences,t,&mut|_,_,_|PublicationDemand::Ready,0,self.floor,request.attribute_attempt.as_ref());
     if !matches!(result,VisitResult::Complete|VisitResult::CycleSettled){return None}
     value=c.owned_lookup_value(request,t).unwrap();
    }
    reply=Some(SubstitutionLookupReply{identity:request.identity.clone(),value:value.unwrap()});self.request=None;
   }
   match self.engine.poll(reply.take()){
    SubstitutionPoll::Lookup(r)=>self.request=Some(r),
    SubstitutionPoll::Complete(v)=>return Some(v.map(|v|v.css.into_owned())),
    _=>panic!("wrong driver state"),
   }
  }panic!("finite test driver exhausted")
 }
}
fn raw(t:&mut AttributeTracker,n:&str,s:&str){t.values.insert(n.into(),s.into());}
fn result(c:&Context,n:&str)->Option<String>{c.lookup_bindings.values.get(n).and_then(|v|v.as_ref()).map(|v|v.value.css.clone())}
#[test]fn reached_attribute_custom_frontier_finishes_with_actual_body_parser(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");raw(&mut t,"x","20px");c.add("b","attr(x type(<length>))",2,true);
 let mut d=Driver::new("attr(a type(<length>))",1);assert_eq!(d.poll(&mut c,&mut t),Some(Ok("20px".into())));
 assert_eq!(result(&c,"b"),Some("20px".into()));assert_eq!(c.published,vec!["b"]);assert_eq!(t.queries,vec![":a",":x"]);assert_eq!(c.computed_context.computations,vec!["20px"]);
}
#[test]fn cross_url_registered_initial_does_not_clear_ancestor_attribute_mark(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");c.add("b","attr(a type(<length>), 9px)",2,true);
 let mut d=Driver::new("attr(a type(<length>), 1px)",1);assert_eq!(d.poll(&mut c,&mut t),Some(Ok("1px".into())));
 assert_eq!(result(&c,"b"),Some("8px".into()));assert_eq!(c.published,vec!["b"]);assert_eq!(t.queries.len(),1);
 assert!(matches!(c.var_info[0].publication.readiness(),NodeReadiness::CycleSettled));
 let mut next=Driver::new("attr(a type(<length>), 1px)",2);assert_eq!(next.poll(&mut c,&mut t),Some(Ok("8px".into())));assert_eq!(c.published,vec!["b"]);
}
#[test]fn valid_primary_avoids_unused_self_fallback_for_registered_and_unregistered(){
 for registered in [false,true]{let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");c.add("b","var(--ready,var(--b))",2,registered);c.lookup_bindings.values.insert("ready".into(),Some(ComputedRegisteredValue::universal(Arc::new(tokens("1px",0)))));
 let mut d=Driver::new("attr(a type(<length>))",1);assert_eq!(d.poll(&mut c,&mut t),Some(Ok("1px".into())));assert_eq!(result(&c,"b"),Some("1px".into()));assert!(matches!(c.var_info[0].publication.readiness(),NodeReadiness::Complete));}
}
#[test]fn invalid_primary_reaches_self_fallback_and_settles_registered_default(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");c.add("b","var(--missing,var(--b))",2,true);
 let mut d=Driver::new("attr(a type(<length>))",1);assert_eq!(d.poll(&mut c,&mut t),Some(Ok("8px".into())));assert!(matches!(c.var_info[0].publication.readiness(),NodeReadiness::CycleSettled));
}
#[test]fn child_local_custom_scc_settles_before_parent_consumption(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");c.add("b","var(--c)",2,true);c.add("c","var(--b)",3,true);
 let mut d=Driver::new("attr(a type(<length>))",1);assert_eq!(d.poll(&mut c,&mut t),Some(Ok("8px".into())));assert_eq!(result(&c,"b"),Some("8px".into()));assert_eq!(result(&c,"c"),Some("8px".into()));assert_eq!(c.published.len(),2);
}
#[test]fn scheduler_pause_retains_exact_request_and_does_not_select_fallback(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");raw(&mut t,"x","var(--c,99px)");c.add("b","attr(x type(<length>))",2,true);c.add("c","7px",3,true);c.blocked.insert("c".into());
 let mut d=Driver::new("attr(a type(<length>), 2px)",1);assert_eq!(d.poll(&mut c,&mut t),None);let identity=c.frames[0].guarded_custom.as_ref().unwrap().request.as_ref().unwrap().identity.clone();assert_eq!(t.queries.len(),2);assert!(c.published.is_empty());assert_eq!(d.poll(&mut c,&mut t),None);assert!(Arc::ptr_eq(&identity,&c.frames[0].guarded_custom.as_ref().unwrap().request.as_ref().unwrap().identity));c.blocked.clear();assert_eq!(d.poll(&mut c,&mut t),Some(Ok("7px".into())));assert_eq!(t.queries.len(),2);
}
#[test]fn registered_output_units_remain_pending_until_separate_readiness(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");raw(&mut t,"x","1em");c.add("b","attr(x type(<length>))",2,true);
 let mut d=Driver::new("attr(a type(<length>))",1);assert_eq!(d.poll(&mut c,&mut t),None);assert!(c.frames[0].value_non_custom_refs.intersects(ReferenceFlags::FONT_UNITS));assert_eq!(c.unit_visits,vec![SingleNonCustomReference::FontUnits]);assert!(matches!(c.frames[0].waiting,Some((VarType::NonCustom(SingleNonCustomReference::FontUnits),LinkPurpose::Unit))));assert!(c.published.is_empty());c.unit_ready=true;assert_eq!(d.poll(&mut c,&mut t),Some(Ok("1em".into())));assert_eq!(t.queries.len(),2);
}
#[test]fn changed_generation_or_flags_cannot_resume_guarded_body(){
 for generation in [false,true]{let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");c.add("b","var(--c)",2,true);c.add("c","7px",2,true);c.blocked.insert("c".into());let mut d=Driver::new("attr(a type(<length>))",1);assert!(d.poll(&mut c,&mut t).is_none());if generation{c.lookup_bindings.root=Arc::new(())}else{c.computed_context.included_cascade_flags=1;c.lookup_bindings.flags=1}c.blocked.clear();assert!(d.poll(&mut c,&mut t).is_none());assert!(!c.published.contains(&"b".into()));}
}
#[test]fn foreign_semantic_root_is_wait_not_cycle_or_fallback(){
 let mut c=Context::new();let mut t=AttributeTracker::default();c.add("outer","4px",0,true);let frame=start_frame(VarType::Custom("outer".into()),&mut c,&mut t).unwrap();drop(frame);raw(&mut t,"a","var(--b)");c.add("b","var(--outer,99px)",2,true);
 let mut d=Driver::new("attr(a type(<length>),2px)",1);assert_eq!(d.poll(&mut c,&mut t),None);assert_eq!(d.poll(&mut c,&mut t),None);assert!(c.published.is_empty());assert!(matches!(c.var_info[0].publication.readiness(),NodeReadiness::SemanticOpen));assert!(!c.frames[0].guarded_custom.as_ref().unwrap().substitution.body_marked());
}
#[test]fn custom_attribute_alternation_is_iterative_on_small_stack(){
 std::thread::Builder::new().stack_size(256*1024).spawn(||{
 let mut c=Context::new();let mut t=AttributeTracker::default();for i in 0..256{raw(&mut t,&format!("a{i}"),&format!("var(--b{i})"));c.add(&format!("b{i}"),&if i==255{"7px".into()}else{format!("attr(a{} type(<length>))",i+1)},0,true);}
 let mut d=Driver::new("attr(a0 type(<length>))",0);assert_eq!(d.poll(&mut c,&mut t),Some(Ok("7px".into())));assert_eq!(c.published.len(),256);assert_eq!(t.queries.len(),256);
 }).unwrap().join().unwrap();
}
#[test]fn actual_metric_lookup_entry_attaches_guards_and_preserves_outer_owner(){
 for recurrent in [false,true]{
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");raw(&mut t,"x","20px");c.add("b",if recurrent{"attr(a type(<length>),9px)"}else{"attr(x type(<length>))"},2,true);
 let mut engine=ResumableSubstitution::new(tokens("attr(a type(<length>),1px)",1),None,false);let mut reply=None;
 let request=loop{let SubstitutionPoll::Lookup(r)=engine.poll(reply.take())else{panic!()};if r.kind==SubstitutionLookupKind::Variable{break r}reply=Some(SubstitutionLookupReply{identity:r.identity.clone(),value:c.owned_lookup_value(&r,&mut t).unwrap().unwrap()});};
 let owner=VarType::NonCustom(SingleNonCustomReference::FontUnits);c.var_info.push(VarInfo{var:None,lowlink:0,publication:NodePublication::Pending(ClosedValue::Prioritary(PrioritaryPropertyId))});
 c.frames.push(TraversalFrame{guarded_custom:None,var:owner.clone(),index:0,lowlink:0,self_ref:false,phase:FramePhase::Publish,waiting:None,reference_reply:None,prepared_custom:None,value:None,value_non_custom_refs:ReferenceFlags::empty(),unit_cursor:0,registered:false,unit_links:vec![]});
 let action=MetricAction{identity:Arc::new(()),root:owner.clone(),owner:owner.clone(),index:0,prerequisite:FontTarget::Metric};c.metric_action=Some(action.clone());c.frame_root=Some(owner.clone());
 let raw=Arc::new(tokens("var(--b)",1));let state=MetricLookup{action,flags:0,generation:c.lookup_bindings.root.clone(),depth:1,semantic_floor:1,request,longhand:0,value:raw.clone()};
 assert_eq!(c.resolve_metric_lookup_inner(&state,&NonCustomPropertyReferences,&mut t,&mut|_,_,_|PublicationDemand::Ready),Ok(true));assert_eq!(c.frames.len(),1);assert_eq!(c.frame_root,Some(owner));
 let (_,answer)=c.lookup_reply.take().unwrap();assert!(Arc::ptr_eq(&raw,&answer.value));let SubstitutionPoll::Complete(Ok(value))=engine.poll(answer.lookup)else{panic!()};assert_eq!(value.css,if recurrent{"1px"}else{"20px"});assert_eq!(c.published,vec!["b"]);
 }
}
#[test]fn actual_ordinary_custom_root_enters_guard_before_legacy_attribute_cycle(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","20px");c.add("b","attr(a type(<length>))",2,true);
 c.indices.insert(VarType::Attr("a".into(),String::new()),0);c.var_info.push(VarInfo{var:None,lowlink:0,publication:NodePublication::CycleSettled});
 assert!(matches!(c.poll_root(VarType::Custom("b".into()),&NonCustomPropertyReferences,&mut t,&mut|_,_,_|PublicationDemand::Ready),VisitResult::Complete));assert_eq!(result(&c,"b"),Some("20px".into()));assert_eq!(c.published,vec!["b"]);assert!(c.frame_root.is_none());
}
#[test]fn actual_ordinary_custom_root_keeps_property_and_attribute_cycle_marks(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");c.add("b","attr(a type(<length>), 9px)",2,true);
 assert!(matches!(c.poll_root(VarType::Custom("b".into()),&NonCustomPropertyReferences,&mut t,&mut|_,_,_|PublicationDemand::Ready),VisitResult::CycleSettled));assert_eq!(result(&c,"b"),Some("8px".into()));assert_eq!(c.published,vec!["b"]);
}
#[test]fn ordinary_and_custom_property_guard_identities_are_distinct(){
 let custom=SubstitutionGuard::new(SubstitutionGuardKey::Property(PropertyId::Custom("font-size".into())));assert!(!SubstitutionGuard::mark_reentry(&[custom.clone()],&SubstitutionGuardKey::Property(PropertyId::NonCustom(0))));assert!(!custom.marked());
}
