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
type PropertyDeclaration = &'static str;
type SubpropertiesVec<T> = Vec<T>;
type ArrayVecDrain<'a,T,const N:usize> = std::vec::Drain<'a,T>;
mod property_counts {pub const MAX_SHORTHAND_EXPANDED:usize=128;}
use std::mem;
#[derive(Default,Debug,PartialEq)] enum AllShorthand {#[default] NotSet, Marker(u32)}
trait TryPush<T> {fn try_push(&mut self,value:T)->Result<(),T>;}
impl<T> TryPush<T> for Vec<T> {fn try_push(&mut self,value:T)->Result<(),T> {if self.len()<128 {self.push(value);Ok(())}else{Err(value)}}}

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

#[derive(Debug)]
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

#[derive(Debug)]
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

#[derive(Debug)]
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

#[derive(Debug,Default)]
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

#[derive(Clone,Copy,Debug,Default,PartialEq,Eq)]
pub struct ReferenceFlags(u8);
bitflags! {
    impl ReferenceFlags : u8 {
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
        /// All dependencies not depending on the root element.
        const NON_ROOT_DEPENDENCIES = Self::FONT_UNITS.0 | Self::LH_UNITS.0;
        /// All dependencies depending on the root element.
        const ROOT_DEPENDENCIES = Self::ROOT_FONT_UNITS.0 | Self::ROOT_LH_UNITS.0;
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
            return Self::FONT_UNITS | Self::LH_UNITS;
        }
        if value.eq_ignore_ascii_case(NoCalcLength::EM)
            || value.eq_ignore_ascii_case(NoCalcLength::EX)
            || value.eq_ignore_ascii_case(NoCalcLength::CAP)
            || value.eq_ignore_ascii_case(NoCalcLength::CH)
            || value.eq_ignore_ascii_case(NoCalcLength::IC)
        {
            return Self::FONT_UNITS;
        }
        if value.eq_ignore_ascii_case(NoCalcLength::RLH) {
            return Self::ROOT_FONT_UNITS | Self::ROOT_LH_UNITS;
        }
        if value.eq_ignore_ascii_case(NoCalcLength::REM)
            || value.eq_ignore_ascii_case(NoCalcLength::REX)
            || value.eq_ignore_ascii_case(NoCalcLength::RCH)
            || value.eq_ignore_ascii_case(NoCalcLength::RCAP)
            || value.eq_ignore_ascii_case(NoCalcLength::RIC)
        {
            return Self::ROOT_FONT_UNITS;
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
    pub fn parse(
        input: &mut Parser,
        namespaces: Option<&FxHashMap<Prefix, Namespace>>,
        url_data: &UrlExtraData,
    ) -> Result<Self, ParseError> {
        let mut references = References::default();
        let mut missing_closing_characters = String::new();
        let mut removed_backslash = false;
        let start_position = input.position();
        let (first_token_type, last_token_type) = parse_declaration_value(
            input,
            start_position,
            namespaces,
            &mut references,
            &mut missing_closing_characters,
            &mut removed_backslash,
        )?;
        let mut css = input
            .slice_from(start_position)
            .trim_ascii_start()
            .to_owned();
        if !missing_closing_characters.is_empty() {
            // Unescaped backslash at EOF in a quoted string is ignored.
            if removed_backslash {
                css.pop();
            }
            css.push_str(&missing_closing_characters);
        }

        css.truncate(css.trim_ascii_end().len());
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
) -> Result<(TokenSerializationType, TokenSerializationType), ParseError> {
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
) -> Result<(TokenSerializationType, TokenSerializationType), ParseError> {
    let mut is_first = true;
    let mut first_token_type = TokenSerializationType::Nothing;
    let mut last_token_type = TokenSerializationType::Nothing;
    let mut prev_reference_index: Option<usize> = None;
    loop {
        let token_start = input.position();
        let Ok(token) = input.next_including_whitespace_and_comments() else {
            break;
        };

        let prev_token_type = last_token_type;
        let serialization_type = token.serialization_type();
        last_token_type = serialization_type;
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
                            let (first, last) = parse_declaration_value(
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
    Ok((first_token_type, last_token_type))
}

#[derive(Debug)]
pub enum ParsedNamespace {
    /// Unregistered namespace
    Unknown,
    /// Registered namespace
    Known(Namespace),
}
impl ParsedNamespace {
    /// Parse a namespace prefix and resolve it to the correct
    /// namespace URI.
    pub fn parse(
        namespaces: &FxHashMap<Prefix, Namespace>,
        input: &mut Parser,
    ) -> Result<Self, ParseError> {
        // We don't need to keep the prefix because different
        // prefixes can resolve to the same id. Additionally,
        // we also don't need it for serialization as substitution
        // functions serialize from the direct css declaration.
        parse_namespace(namespaces, input).map(|(_prefix, namespace)| namespace)
    }
}
impl Default for ParsedNamespace {
    fn default() -> Self {
        Self::Known(Namespace::default())
    }
}
pub fn parse_namespace(
    namespaces: &FxHashMap<Prefix, Namespace>,
    input: &mut Parser,
) -> Result<(Prefix, ParsedNamespace), ParseError> {
    let ns_prefix = match input.next()? {
        Token::Ident(prefix) => Some(Prefix::from(prefix.as_ref())),
        Token::Delim('|') => None,
        _ => return Err(ParseError::custom(StyleParseErrorKind::UnspecifiedError)),
    };

    if ns_prefix.is_some() && !matches!(*input.next_including_whitespace()?, Token::Delim('|')) {
        return Err(ParseError::custom(StyleParseErrorKind::UnspecifiedError));
    }

    if let Some(prefix) = ns_prefix {
        let ns = match namespaces.get(&prefix).cloned() {
            Some(ns) => ParsedNamespace::Known(ns),
            None => ParsedNamespace::Unknown,
        };
        Ok((prefix, ns))
    } else {
        Ok((Prefix::default(), ParsedNamespace::default()))
    }
}

impl Parse for LinkParameters {
    fn parse(context: &ParserContext, input: &mut Parser) -> Result<Self, ParseError> {
        if input.try_parse(|i| i.expect_ident_matching("none")).is_ok() {
            return Ok(Self::none());
        }

        let params = input.parse_comma_separated(|input| {
            input.expect_function_matching("param")?;
            input.parse_nested_block(|input| {
                let name = DashedIdent::parse(context, input)?;
                input.expect_comma()?;
                // if a comma exists then parse it and set value as specified, even if no value provided
                // need to handle url references properly https://bugzilla.mozilla.org/show_bug.cgi?id=2028998
                let parsed = VariableValue::parse(input, None, context.url_data)?;
                let value = LinkParamValue(OwnedStr::from(parsed.css));
                Ok(LinkParam { name, value })
            })
        })?;

        Ok(Self(crate::ArcSlice::from_iter(params.into_iter())))
    }
}

#[derive(Default,Debug)]
pub struct SourcePropertyDeclaration {
    /// The storage for the actual declarations (except for all).
    pub declarations: SubpropertiesVec<PropertyDeclaration>,
    /// Stored separately to keep SubpropertiesVec smaller.
    pub all_shorthand: AllShorthand,
}
pub struct SourcePropertyDeclarationDrain<'a> {
    /// A drain over the non-all declarations.
    pub declarations:
        ArrayVecDrain<'a, PropertyDeclaration, { property_counts::MAX_SHORTHAND_EXPANDED }>,
    /// The all shorthand that was set.
    pub all_shorthand: AllShorthand,
}
impl SourcePropertyDeclaration {
    /// Create one with a single PropertyDeclaration.
    #[inline]
    pub fn with_one(decl: PropertyDeclaration) -> Self {
        let mut result = Self::default();
        result.declarations.push(decl);
        result
    }

    /// Similar to Vec::drain: leaves this empty when the return value is dropped.
    pub fn drain(&mut self) -> SourcePropertyDeclarationDrain<'_> {
        SourcePropertyDeclarationDrain {
            declarations: self.declarations.drain(..),
            all_shorthand: mem::replace(&mut self.all_shorthand, AllShorthand::NotSet),
        }
    }

    /// Reset to initial state
    pub fn clear(&mut self) {
        self.declarations.clear();
        self.all_shorthand = AllShorthand::NotSet;
    }

    /// Whether we're empty.
    pub fn is_empty(&self) -> bool {
        self.declarations.is_empty() && matches!(self.all_shorthand, AllShorthand::NotSet)
    }

    /// Push a single declaration.
    pub fn push(&mut self, declaration: PropertyDeclaration) {
        let _result = self.declarations.try_push(declaration);
        debug_assert!(_result.is_ok());
    }
}

fn parse_non_custom_property_declaration_value_into(
    declarations: &mut SourcePropertyDeclaration,
    context: &ParserContext,
    input: &mut Parser,
    start: &cssparser::ParserState,
    parse_entirely_into: impl FnOnce(
        &mut SourcePropertyDeclaration,
        &mut Parser,
    ) -> Result<(), ParseError>,
    parsed_wide_keyword: impl FnOnce(&mut SourcePropertyDeclaration, CSSWideKeyword),
    parsed_custom: impl FnOnce(&mut SourcePropertyDeclaration, custom_properties::VariableValue),
) -> Result<(), ParseError> {
    let mut starts_with_curly_block = false;
    input.look_for_arbitrary_substitution_functions(ARBITRARY_SUBSTITUTION_FUNCTIONS);
    if let Ok(token) = input.next() {
        match token {
            cssparser::Token::Ident(ident) => {
                if let Ok(wk) = CSSWideKeyword::from_ident(ident)
                    && input.expect_exhausted().is_ok()
                {
                    parsed_wide_keyword(declarations, wk);
                    let _ = input.seen_arbitrary_substitution_functions();
                    return Ok(());
                }
            },
            cssparser::Token::CurlyBracketBlock => {
                starts_with_curly_block = true;
            },
            _ => {},
        }
    };

    input.reset(start);

    let mut saw_arbitrary_substitution_functions = false;
    let err = match parse_entirely_into(declarations, input) {
        Ok(()) => {
            saw_arbitrary_substitution_functions = input.seen_arbitrary_substitution_functions();
            if !saw_arbitrary_substitution_functions {
                return Ok(());
            }
            declarations.clear();
            ParseError::custom(style_traits::StyleParseErrorKind::UnspecifiedError)
        },
        Err(e) => e,
    };

    input.reset(start);

    // Look for var(), env() and top-level curly blocks in the whole value.
    let start_pos = start.position();
    let mut at_start = start_pos == input.position();
    let mut invalid = false;
    while let Ok(token) = input.next() {
        if matches!(token, cssparser::Token::CurlyBracketBlock) {
            if !starts_with_curly_block || !at_start {
                invalid = true;
                break;
            }
        } else if starts_with_curly_block {
            invalid = true;
            break;
        }
        at_start = false;
    }
    saw_arbitrary_substitution_functions =
        saw_arbitrary_substitution_functions || input.seen_arbitrary_substitution_functions();
    if !saw_arbitrary_substitution_functions || invalid {
        return Err(err);
    }
    input.reset(start);
    let value = custom_properties::VariableValue::parse(
        input,
        Some(&context.namespaces.prefixes),
        context.url_data,
    )?;
    parsed_custom(declarations, value);
    declarations.clear();
    Ok(())
}

fn main() {
    let values=["param(--a, var(--x, red))","param(--a, env(not-real, red))","param(--a, attr(data-x))","param(--a, )","none","param(--a, var(invalid))","param(--a, var())","param(--a, env())","param(--a, red !important)","param(--a, var(--x)) junk","initial","var(--whole)","param(--a, var(--x)), param(--b, blue)"];
    for value in values {
        let context=ParserContext{namespaces:Namespaces{prefixes:Default::default()},url_data:&UrlExtraData};
        let mut ordinary=Parser::new(value);
        ordinary.look_for_arbitrary_substitution_functions(ARBITRARY_SUBSTITUTION_FUNCTIONS);
        let ordinary_ok=ordinary.parse_entirely(|i|LinkParameters::parse(&context,i)).is_ok();
        let seen=ordinary.seen_arbitrary_substitution_functions();
        let mut input=Parser::new(value);let start=input.state();let mut scratch=SourcePropertyDeclaration::default();
        let result=parse_non_custom_property_declaration_value_into(&mut scratch,&context,&mut input,&start,
            |d,i|{i.parse_entirely(|i|LinkParameters::parse(&context,i))?;d.push("ordinary");Ok(())},
            |d,_|d.push("wide"),|d,_|d.push("with-variables"));
        println!("{{\"value\":{:?},\"ordinary_ok\":{},\"seen\":{},\"helper_ok\":{},\"scratch\":{:?}}}",value,ordinary_ok,seen,result.is_ok(),scratch.declarations);
    }
    for mode in ["failure-declarations","failure-all"] {
        let context=ParserContext{namespaces:Namespaces{prefixes:Default::default()},url_data:&UrlExtraData};
        let mut input=Parser::new("var(invalid)");let start=input.state();let mut scratch=SourcePropertyDeclaration::default();
        let result=parse_non_custom_property_declaration_value_into(&mut scratch,&context,&mut input,&start,
            |d,i|{while i.next().is_ok() {} if mode=="failure-all" {d.all_shorthand=AllShorthand::Marker(9)}else{d.push("ordinary")};Ok(())},
            |d,_|d.push("wide"),|d,_|d.push("with-variables"));
        println!("{{\"mode\":{:?},\"helper_ok\":{},\"declarations\":{:?},\"all_present\":{}}}",mode,result.is_ok(),scratch.declarations,!matches!(scratch.all_shorthand,AllShorthand::NotSet));
    }
    let mut scratch=SourcePropertyDeclaration::with_one("ordinary");
    scratch.all_shorthand=AllShorthand::Marker(9);
    let (drained,all)= {let d=scratch.drain();(d.declarations.collect::<Vec<_>>(),matches!(d.all_shorthand,AllShorthand::Marker(9)))};
    println!("{{\"mode\":\"drain\",\"drained\":{:?},\"all_drained\":{},\"empty_after\":{}}}",drained,all,scratch.is_empty());
}
