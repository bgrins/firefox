/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

//! Specified types for CSS Easing functions.
use crate::derives::*;
use crate::parser::{Parse, ParserContext};
use crate::piecewise_linear::{PiecewiseLinearFunction, PiecewiseLinearFunctionBuilder};
use crate::values::computed::easing::TimingFunction as ComputedTimingFunction;
use crate::values::computed::{Context, ToComputedValue};
use crate::values::generics::easing::TimingFunction as GenericTimingFunction;
use crate::values::generics::easing::{StepPosition, TimingKeyword};
use crate::values::specified::{AnimationName, Integer, Number, Percentage};
use cssparser::{Delimiter, Parser, Token, match_ignore_ascii_case};
use selectors::parser::SelectorParseErrorKind;
use std::fmt::{self, Write};
use style_traits::{CssWriter, ParseError, StyleParseErrorKind, ToCss};

/// A specified timing function.
pub type TimingFunction = GenericTimingFunction<Integer, Number, LinearFunction>;

/// An authored linear stop retained until contextual computation.
#[derive(Clone, Debug, MallocSizeOf, PartialEq, SpecifiedValueInfo, ToShmem)]
#[repr(C)]
pub struct LinearStop {
    output: Number,
    input_start: Option<Percentage>,
    input_end: Option<Percentage>,
}

/// Specified linear stops or their context-independent canonical representation.
#[derive(Clone, Debug, MallocSizeOf, PartialEq, SpecifiedValueInfo, ToShmem)]
#[repr(u8, C)]
pub enum LinearFunction {
    /// A function whose stop values have already resolved.
    Resolved(PiecewiseLinearFunction),
    /// Stops that still need the owning element's computation context.
    Contextual(crate::OwnedSlice<LinearStop>),
}

impl LinearFunction {
    fn from_stops(stops: Vec<LinearStop>) -> Self {
        let specified = Self::Contextual(stops.into());
        match specified.try_to_computed_value_without_context() {
            Some(computed) => Self::Resolved(computed),
            None => specified,
        }
    }

    fn try_to_computed_value_without_context(&self) -> Option<PiecewiseLinearFunction> {
        let stops = match self {
            Self::Resolved(computed) => return Some(computed.clone()),
            Self::Contextual(stops) => stops,
        };
        let mut builder = PiecewiseLinearFunctionBuilder::default();
        for stop in stops.iter() {
            let output = stop.output.resolve()?;
            let input_start = match &stop.input_start {
                Some(value) => Some(value.resolve()?),
                None => None,
            };
            builder.push(output, input_start);
            if let Some(value) = &stop.input_end {
                builder.push(output, Some(value.resolve()?));
            }
        }
        Some(builder.build())
    }
}

impl ToComputedValue for LinearFunction {
    type ComputedValue = PiecewiseLinearFunction;

    fn to_computed_value(&self, context: &Context) -> Self::ComputedValue {
        let stops = match self {
            Self::Resolved(computed) => return computed.clone(),
            Self::Contextual(stops) => stops,
        };
        let mut builder = PiecewiseLinearFunctionBuilder::default();
        for stop in stops.iter() {
            let output = stop.output.to_computed_value(context);
            let input_start = stop
                .input_start
                .as_ref()
                .map(|v| v.to_computed_value(context).0);
            builder.push(output, input_start);
            if let Some(value) = &stop.input_end {
                builder.push(output, Some(value.to_computed_value(context).0));
            }
        }
        builder.build()
    }

    fn from_computed_value(computed: &Self::ComputedValue) -> Self {
        Self::Resolved(computed.clone())
    }
}

impl ToCss for LinearFunction {
    fn to_css<W>(&self, dest: &mut CssWriter<W>) -> fmt::Result
    where
        W: fmt::Write,
    {
        let stops = match self {
            Self::Resolved(computed) => return computed.to_css(dest),
            Self::Contextual(stops) => stops,
        };
        for (index, stop) in stops.iter().enumerate() {
            if index != 0 {
                dest.write_str(", ")?;
            }
            stop.output.to_css(dest)?;
            for value in stop.input_start.iter().chain(stop.input_end.iter()) {
                dest.write_char(' ')?;
                value.to_css(dest)?;
            }
        }
        Ok(())
    }
}

impl Parse for TimingFunction {
    fn parse(context: &ParserContext, input: &mut Parser) -> Result<Self, ParseError> {
        if let Ok(keyword) = input.try_parse(TimingKeyword::parse) {
            return Ok(GenericTimingFunction::Keyword(keyword));
        }
        if let Ok(ident) = input.try_parse(|i| i.expect_ident_cloned()) {
            let position = match_ignore_ascii_case! { &ident,
                "step-start" => StepPosition::Start,
                "step-end" => StepPosition::End,
                _ => {
                    return Err(ParseError::custom(
                        SelectorParseErrorKind::UnexpectedIdent
                    ));
                },
            };
            return Ok(GenericTimingFunction::Steps(Integer::new(1), position));
        }
        let function = input.expect_function()?.clone();
        input.parse_nested_block(move |i| {
            match_ignore_ascii_case! { &function,
                "cubic-bezier" => Self::parse_cubic_bezier(context, i),
                "steps" => Self::parse_steps(context, i),
                "linear" => Self::parse_linear_function(context, i),
                _ => Err(ParseError::custom(StyleParseErrorKind::UnexpectedFunction)),
            }
        })
    }
}

impl TimingFunction {
    fn parse_cubic_bezier(context: &ParserContext, input: &mut Parser) -> Result<Self, ParseError> {
        let x1 = Number::parse(context, input)?;
        input.expect_comma()?;
        let y1 = Number::parse(context, input)?;
        input.expect_comma()?;
        let x2 = Number::parse(context, input)?;
        input.expect_comma()?;
        let y2 = Number::parse(context, input)?;

        if matches!(x1.get(), Some(x) if !(0.0..=1.0).contains(&x))
            || matches!(x2.get(), Some(x) if !(0.0..=1.0).contains(&x))
        {
            return Err(ParseError::custom(StyleParseErrorKind::UnspecifiedError));
        }

        Ok(GenericTimingFunction::CubicBezier { x1, y1, x2, y2 })
    }

    fn parse_steps(context: &ParserContext, input: &mut Parser) -> Result<Self, ParseError> {
        let steps = Integer::parse_positive(context, input)?;
        let position = input
            .try_parse(|i| {
                i.expect_comma()?;
                StepPosition::parse(i)
            })
            .unwrap_or(StepPosition::End);

        // Literal counts are range-checked here; calculations are clamped on computation.
        if position == StepPosition::JumpNone && steps.get() == Some(1) {
            return Err(ParseError::custom(StyleParseErrorKind::UnspecifiedError));
        }
        Ok(GenericTimingFunction::Steps(steps, position))
    }

    fn parse_linear_function(
        context: &ParserContext,
        input: &mut Parser,
    ) -> Result<Self, ParseError> {
        let mut stops = Vec::new();
        // Closely follows `parse_comma_separated`, but can generate multiple entries for one comma-separated entry.
        loop {
            input.parse_until_before(Delimiter::Comma, |i| {
                let mut input_start = i.try_parse(|i| Percentage::parse(context, i)).ok();
                let mut input_end = i.try_parse(|i| Percentage::parse(context, i)).ok();

                let output = Number::parse(context, i)?;
                if input_start.is_none() {
                    debug_assert!(input_end.is_none(), "Input end parsed without input start?");
                    input_start = i.try_parse(|i| Percentage::parse(context, i)).ok();
                    input_end = i.try_parse(|i| Percentage::parse(context, i)).ok();
                }

                stops.push(LinearStop {
                    output,
                    input_start,
                    input_end,
                });

                Ok(())
            })?;

            match input.next() {
                Err(_) => break,
                Ok(&Token::Comma) => continue,
                Ok(_) => unreachable!(),
            }
        }
        // By spec, specifying only a single stop makes the function invalid, even if that single entry may generate
        // two entries.
        if stops.len() < 2 {
            return Err(ParseError::custom(StyleParseErrorKind::UnspecifiedError));
        }

        Ok(GenericTimingFunction::LinearFunction(
            LinearFunction::from_stops(stops),
        ))
    }

    /// Returns true if the name matches any keyword.
    #[inline]
    pub fn match_keywords(name: &AnimationName) -> bool {
        if let Some(name) = name.as_atom() {
            #[cfg(feature = "gecko")]
            return name.with_str(|n| TimingKeyword::from_ident(n).is_ok());
            #[cfg(feature = "servo")]
            return TimingKeyword::from_ident(name).is_ok();
        }
        false
    }
}

impl TimingFunction {
    /// Compute a timing function only when its inputs are context independent.
    pub fn try_to_computed_value_without_context(&self) -> Option<ComputedTimingFunction> {
        Some(match self {
            GenericTimingFunction::Steps(steps, pos) => {
                let count = steps.resolve()?;
                let count = if *pos == StepPosition::JumpNone && steps.get().is_none() {
                    count.max(2)
                } else {
                    count
                };
                GenericTimingFunction::Steps(count, *pos)
            },
            GenericTimingFunction::CubicBezier { x1, y1, x2, y2 } => {
                GenericTimingFunction::CubicBezier {
                    x1: x1.resolve()?.clamp(0.0, 1.0),
                    y1: y1.resolve()?,
                    x2: x2.resolve()?.clamp(0.0, 1.0),
                    y2: y2.resolve()?,
                }
            },
            GenericTimingFunction::Keyword(keyword) => GenericTimingFunction::Keyword(*keyword),
            GenericTimingFunction::LinearFunction(function) => {
                GenericTimingFunction::LinearFunction(
                    function.try_to_computed_value_without_context()?,
                )
            },
        })
    }
}

impl ToComputedValue for TimingFunction {
    type ComputedValue = ComputedTimingFunction;
    fn to_computed_value(&self, context: &Context) -> Self::ComputedValue {
        if let Some(computed) = self.try_to_computed_value_without_context() {
            return computed;
        }
        match self {
            GenericTimingFunction::Steps(steps, pos) => {
                let count = steps.to_computed_value(context);
                let count = if *pos == StepPosition::JumpNone && steps.get().is_none() {
                    count.max(2)
                } else {
                    count
                };
                GenericTimingFunction::Steps(count, *pos)
            },
            GenericTimingFunction::CubicBezier { x1, y1, x2, y2 } => {
                GenericTimingFunction::CubicBezier {
                    x1: x1.to_computed_value(context).clamp(0.0, 1.0),
                    y1: y1.to_computed_value(context),
                    x2: x2.to_computed_value(context).clamp(0.0, 1.0),
                    y2: y2.to_computed_value(context),
                }
            },
            GenericTimingFunction::Keyword(keyword) => GenericTimingFunction::Keyword(*keyword),
            GenericTimingFunction::LinearFunction(function) => {
                GenericTimingFunction::LinearFunction(function.to_computed_value(context))
            },
        }
    }

    fn from_computed_value(computed: &Self::ComputedValue) -> Self {
        match &computed {
            ComputedTimingFunction::Steps(steps, pos) => Self::Steps(Integer::new(*steps), *pos),
            ComputedTimingFunction::CubicBezier { x1, y1, x2, y2 } => Self::CubicBezier {
                x1: Number::new(*x1),
                y1: Number::new(*y1),
                x2: Number::new(*x2),
                y2: Number::new(*y2),
            },
            ComputedTimingFunction::Keyword(keyword) => GenericTimingFunction::Keyword(*keyword),
            ComputedTimingFunction::LinearFunction(function) => {
                GenericTimingFunction::LinearFunction(LinearFunction::from_computed_value(function))
            },
        }
    }
}
