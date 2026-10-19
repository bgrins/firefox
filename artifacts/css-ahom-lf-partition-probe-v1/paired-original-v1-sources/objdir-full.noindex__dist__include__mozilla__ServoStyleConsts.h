/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

// See the comment in ServoBindings.h about the same.
#pragma GCC diagnostic push
#ifdef __clang__
#  pragma GCC diagnostic ignored "-Wreturn-type-c-linkage"
#endif

#ifndef mozilla_ServoStyleConsts_h
#define mozilla_ServoStyleConsts_h


/* Generated with cbindgen:0.29.4 */

/* DO NOT MODIFY THIS MANUALLY! This file was generated using cbindgen. See RunCbindgen.py
 * To modify this file, edit servo/ports/geckolib/cbindgen.toml and build Firefox.
 */


#include <cstdarg>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <ostream>
#include <new>
#include "mozilla/ServoStyleConstsForwards.h"
// Work-around silly windows.h define.
#pragma push_macro("STRICT")
#undef STRICT
#pragma push_macro("TRANSPARENT")
#undef TRANSPARENT


namespace mozilla {

/// Number of color-mix items to reserve on the stack to avoid heap allocations.
constexpr static const size_t StylePRE_ALLOCATED_COLOR_MIX_ITEMS = 3;

#if defined(CBINDGEN_IS_GECKO)
/// The minimum stack size for a thread in the styling pool, in kilobytes.
constexpr static const size_t StyleSTYLE_THREAD_STACK_SIZE_KB = 256;
#endif

/// The stack margin. If we get this deep in the stack, we will skip recursive
/// optimizations to ensure that there is sufficient room for non-recursive work.
///
/// We allocate large safety margins because certain OS calls can use very large
/// amounts of stack space [1]. Reserving a larger-than-necessary stack costs us
/// address space, but if we keep our safety margin big, we will generally avoid
/// committing those extra pages, and only use them in edge cases that would
/// otherwise cause crashes.
///
/// When measured with 128KB stacks and 40KB margin, we could support 53
/// levels of recursion before the limiter kicks in, on x86_64-Linux [2]. When
/// we doubled the stack size, we added it all to the safety margin, so we should
/// be able to get the same amount of recursion.
///
/// [1] https://bugzilla.mozilla.org/show_bug.cgi?id=1395708#c15
/// [2] See Gecko bug 1376883 for more discussion on the measurements.
constexpr static const size_t StyleSTACK_SAFETY_MARGIN_KB = 168;

/// The amount of nodes that the style sharing candidate cache should hold at most.
///
/// The cache size was chosen by measuring style sharing and resulting performance on a few pages;
/// sizes up to about 32 were giving good sharing improvements (e.g. 3x fewer styles having to be
/// resolved than at size 8) and slight performance improvements.  Sizes larger than 32 haven't
/// really been tested.
constexpr static const size_t StyleSHARING_CACHE_SIZE = 32;

constexpr static const size_t StyleNUMERIC_BASE_TYPE_COUNT = 7;

/// font-weight: range 1..1000, fractional values permitted; keywords
/// 'normal', 'bold' aliased to 400, 700 respectively.
///
/// We use an unsigned 10.6 fixed-point value (range 0.0 - 1023.984375)
constexpr static const uint16_t StyleFONT_WEIGHT_FRACTION_BITS = 6;

/// - Use a signed 8.8 fixed-point value (representable range -128.0..128)
///
/// Values of <angle> below -90 or above 90 are not permitted, so we use an out
/// of range value to represent `italic`.
constexpr static const uint16_t StyleFONT_STYLE_FRACTION_BITS = 8;

/// font-width is a percentage relative to normal.
///
/// We use an unsigned 10.6 fixed-point value (range 0.0 - 1023.984375)
///
/// We arbitrarily limit here to 1000%. (If that becomes a problem, we could
/// reduce the number of fractional bits and increase the limit.)
constexpr static const uint16_t StyleFONT_WIDTH_FRACTION_BITS = 6;

/// The minimum font-weight value per:
///
/// https://drafts.csswg.org/css-fonts-4/#font-weight-numeric-values
constexpr static const float StyleMIN_FONT_WEIGHT = 1.;

/// The maximum font-weight value per:
///
/// https://drafts.csswg.org/css-fonts-4/#font-weight-numeric-values
constexpr static const float StyleMAX_FONT_WEIGHT = 1000.;

/// From https://drafts.csswg.org/css-fonts-4/#valdef-font-style-oblique-angle:
///
///     Values less than -90deg or values greater than 90deg are
///     invalid and are treated as parse errors.
///
/// The maximum angle value that `font-style: oblique` should compute to.
constexpr static const float StyleFONT_STYLE_OBLIQUE_MAX_ANGLE_DEGREES = 90.;

/// The minimum angle value that `font-style: oblique` should compute to.
constexpr static const float StyleFONT_STYLE_OBLIQUE_MIN_ANGLE_DEGREES = -90.;

/// The default font size.
constexpr static const float StyleFONT_MEDIUM_PX = 16.0;

/// The default line height.
constexpr static const float StyleFONT_MEDIUM_LINE_HEIGHT_PX = (StyleFONT_MEDIUM_PX * 1.2);

/// The default ex height -- https://drafts.csswg.org/css-values/#ex
/// > In the cases where it is impossible or impractical to determine the x-height, a value of 0.5em must be assumed
constexpr static const float StyleFONT_MEDIUM_EX_PX = (StyleFONT_MEDIUM_PX * 0.5);

/// The default cap height -- https://drafts.csswg.org/css-values/#cap
/// > In the cases where it is impossible or impractical to determine the cap-height, the font’s ascent must be used
constexpr static const float StyleFONT_MEDIUM_CAP_PX = StyleFONT_MEDIUM_PX;

/// The default advance measure -- https://drafts.csswg.org/css-values/#ch
/// > Thus, the ch unit falls back to 0.5em in the general case
constexpr static const float StyleFONT_MEDIUM_CH_PX = (StyleFONT_MEDIUM_PX * 0.5);

/// The default idographic advance measure -- https://drafts.csswg.org/css-values/#ic
/// > In the cases where it is impossible or impractical to determine the ideographic advance measure, it must be assumed to be 1em
constexpr static const float StyleFONT_MEDIUM_IC_PX = StyleFONT_MEDIUM_PX;

/// The shift to the left needed to set the axis.
constexpr static const size_t StyleAXIS_SHIFT = 3;

/// The mask used to extract the axis.
constexpr static const uint8_t StyleAXIS_MASK = (7 << StyleAXIS_SHIFT);

/// The mask used to extract the track.
constexpr static const uint8_t StyleTRACK_MASK = 7;

/// The self-wm bit.
constexpr static const uint8_t StyleSELF_WM = (1 << 6);

/// Number of non-normal components
constexpr static const uint8_t StylePAINT_ORDER_COUNT = 3;

/// Number of bits for each component
constexpr static const uint8_t StylePAINT_ORDER_SHIFT = 2;

/// Mask with above bits set
constexpr static const uint8_t StylePAINT_ORDER_MASK = 3;

/// Max valid value for TextDecorationStyle, see above.
constexpr static const int32_t StyleMAX_LINE_STYLE = 5;

constexpr static const uint8_t StyleNUMERIC_UNION_TAG_INLINE = 1;

#if defined(CBINDGEN_IS_SERVO)
/// The count of all pseudo-elements.
constexpr static const size_t StylePSEUDO_COUNT = ((size_t)StylePseudoElement::ServoTableWrapper + 1);
#endif

#if defined(CBINDGEN_IS_SERVO)
/// The number of eager pseudo-elements. Keep this in sync with cascade_type.
constexpr static const size_t StyleEAGER_PSEUDO_COUNT = 4;
#endif

/// A color space representation in the CSS specification.
///
/// https://drafts.csswg.org/css-color-4/#typedef-color-space
enum class StyleColorSpace : uint8_t {
  /// A color specified in the sRGB color space with either the rgb/rgba(..)
  /// functions or the newer color(srgb ..) function. If the color(..)
  /// function is used, the AS_COLOR_FUNCTION flag will be set. Examples:
  /// "color(srgb 0.691 0.139 0.259)", "rgb(176, 35, 66)"
  Srgb = 0,
  /// A color specified in the Hsl notation in the sRGB color space, e.g.
  /// "hsl(289.18 93.136% 65.531%)"
  /// https://drafts.csswg.org/css-color-4/#the-hsl-notation
  Hsl,
  /// A color specified in the Hwb notation in the sRGB color space, e.g.
  /// "hwb(740deg 20% 30%)"
  /// https://drafts.csswg.org/css-color-4/#the-hwb-notation
  Hwb,
  /// A color specified in the Lab color format, e.g.
  /// "lab(29.2345% 39.3825 20.0664)".
  /// https://w3c.github.io/csswg-drafts/css-color-4/#lab-colors
  Lab,
  /// A color specified in the Lch color format, e.g.
  /// "lch(29.2345% 44.2 27)".
  /// https://w3c.github.io/csswg-drafts/css-color-4/#lch-colors
  Lch,
  /// A color specified in the Oklab color format, e.g.
  /// "oklab(40.101% 0.1147 0.0453)".
  /// https://w3c.github.io/csswg-drafts/css-color-4/#lab-colors
  Oklab,
  /// A color specified in the Oklch color format, e.g.
  /// "oklch(40.101% 0.12332 21.555)".
  /// https://w3c.github.io/csswg-drafts/css-color-4/#lch-colors
  Oklch,
  /// A color specified with the color(..) function and the "srgb-linear"
  /// color space, e.g. "color(srgb-linear 0.435 0.017 0.055)".
  SrgbLinear,
  /// A color specified with the color(..) function and the "display-p3"
  /// color space, e.g. "color(display-p3 0.84 0.19 0.72)".
  DisplayP3,
  /// A color specified with the color(..) function and the "display-p3-linear"
  /// color space.
  DisplayP3Linear,
  /// A color specified with the color(..) function and the "a98-rgb" color
  /// space, e.g. "color(a98-rgb 0.44091 0.49971 0.37408)".
  A98Rgb,
  /// A color specified with the color(..) function and the "prophoto-rgb"
  /// color space, e.g. "color(prophoto-rgb 0.36589 0.41717 0.31333)".
  ProphotoRgb,
  /// A color specified with the color(..) function and the "rec2020" color
  /// space, e.g. "color(rec2020 0.42210 0.47580 0.35605)".
  Rec2020,
  /// A color specified with the color(..) function and the "xyz-d50" color
  /// space, e.g. "color(xyz-d50 0.2005 0.14089 0.4472)".
  XyzD50,
  /// A color specified with the color(..) function and the "xyz-d65" or "xyz"
  /// color space, e.g. "color(xyz-d65 0.21661 0.14602 0.59452)".
  /// NOTE: https://drafts.csswg.org/css-color-4/#resolving-color-function-values
  ///       specifies that `xyz` is an alias for the `xyz-d65` color space.
  XyzD65,
};

/// The discriminator used for inline LengthPercentage variants.
enum class StyleLengthPercentageTag : uint8_t {
  /// A `<length>` value.
  Length = 0,
  /// A `<percentage>` value.
  Percentage = 1,
};

/// Whether to allow negative lengths or not.
enum class StyleAllowedNumericType : uint8_t {
  /// Allow all kind of numeric values.
  All,
  /// Allow only non-negative numeric values.
  NonNegative,
  /// Allow only numeric values greater or equal to 1.0.
  AtLeastOne,
  /// Allow only numeric values from 0 to 1.0.
  ZeroToOne,
};

/// https://drafts.css-houdini.org/css-typed-om-1/#cssnumericvalue-base-type
enum class StyleNumericBaseType : uint8_t {
  /// A `<length>` unit.
  Length,
  /// An `<angle>` unit.
  Angle,
  /// A `<time>` unit.
  Time,
  /// A `<frequency>` unit.
  Frequency,
  /// A `<resolution>` unit.
  Resolution,
  /// The `<flex>` unit.
  Flex,
  /// The percentage unit.
  Percent,
};

/// Whether we're a `min` or `max` function.
enum class StyleMinMaxOp : uint8_t {
  /// `min()`
  Min,
  /// `max()`
  Max,
};

/// The strategy used in `round()`
enum class StyleRoundingStrategy : uint8_t {
  /// `round(nearest, a, b)`
  /// round a to the nearest multiple of b
  Nearest,
  /// `round(up, a, b)`
  /// round a up to the nearest multiple of b
  Up,
  /// `round(down, a, b)`
  /// round a down to the nearest multiple of b
  Down,
  /// `round(to-zero, a, b)`
  /// round a to the nearest multiple of b that is towards zero
  ToZero,
};

/// Whether we're a `mod` or `rem` function.
enum class StyleModRemOp : uint8_t {
  /// `mod()`
  Mod,
  /// `rem()`
  Rem,
};

/// The clamping mode used in `progress()`
enum class StyleProgressClampingMode : uint8_t {
  /// `progress(value, start, end)`
  /// Progress result is clamped to the range [0, 1}.
  Clamp,
  /// `progress(no-clamp value, start, end)`
  /// Progress result can be any number.
  NoClamp,
};

/// The cascade origin of rules.
///
/// Presentational hints for SVG and HTML are in the "author-level zero-specificity" level, that
/// is, right after user rules, and before author rules.
///
/// The order of variants declared here is significant, and must be in _ascending_ order of
/// precedence.
///
/// [1]: https://drafts.csswg.org/css-cascade/#cascade-origin
/// [2]: https://drafts.csswg.org/css-cascade/#cascade-origin
enum class StyleCascadeOrigin : uint8_t {
  /// Normal User-Agent rules.
  UA = 0,
  /// User normal rules.
  User,
  /// Presentational hints.
  PresHints,
  /// Styles from author styles.
  Author,
  /// https://drafts.csswg.org/css-anchor-position-1/#position-fallback-origin
  PositionFallback,
  /// SVG SMIL animations.
  SMILOverride,
  /// CSS animations and script-generated animations.
  Animations,
  /// CSS Transitions
  Transitions,
};

/// Keyword values for the anchor positioning function.
enum class StyleAnchorSideKeyword : uint8_t {
  /// Inside relative (i.e. Same side) to the inset property it's used in.
  Inside,
  /// Same as above, but outside (i.e. Opposite side).
  Outside,
  /// Top of the anchor element.
  Top,
  /// Left of the anchor element.
  Left,
  /// Right of the anchor element.
  Right,
  /// Bottom of the anchor element.
  Bottom,
  /// Refers to the start side of the anchor element for the same axis of the inset
  /// property it's used in, resolved against the positioned element's containing
  /// block's writing mode.
  Start,
  /// Same as above, but for the end side.
  End,
  /// Same as `start`, resolved against the positioned element's writing mode.
  SelfStart,
  /// Same as above, but for the end side.
  SelfEnd,
  /// Halfway between `start` and `end` sides.
  Center,
};

/// Keyword values for the anchor size function.
enum class StyleAnchorSizeKeyword : uint8_t {
  /// Magic value for nothing.
  None,
  /// Width of the anchor element.
  Width,
  /// Height of the anchor element.
  Height,
  /// Block size of the anchor element.
  Block,
  /// Inline size of the anchor element.
  Inline,
  /// Same as `Block`, resolved against the positioned element's writing mode.
  SelfBlock,
  /// Same as `Inline`, resolved against the positioned element's writing mode.
  SelfInline,
};

enum class StyleFillRule : uint8_t {
  Nonzero,
  Evenodd,
};

/// Defines the point of reference for a <relative-control-point>.
///
/// When a reference is not specified, depending on whether the associated
/// <command-end-point> is absolutely or relatively positioned, the default
/// will be `Origin` or `Start`, respectively.
/// https://drafts.csswg.org/css-shapes/#typedef-shape-relative-control-point
enum class StyleControlReference {
  Start,
  End,
  Origin,
};

/// This indicates that the arc that is traced around the ellipse clockwise or counter-clockwise
/// from the center.
/// https://drafts.csswg.org/css-shapes-2/#typedef-shape-arc-sweep
enum class StyleArcSweep : uint8_t {
  /// Counter-clockwise. The default value. (This also represents 0 in the svg path.)
  Ccw = 0,
  /// Clockwise. (This also represents 1 in the svg path.)
  Cw = 1,
};

/// This indicates that the larger or smaller, respectively, of the two possible arcs must be
/// chosen.
/// https://drafts.csswg.org/css-shapes-2/#typedef-shape-arc-size
enum class StyleArcSize : uint8_t {
  /// Choose the small one. The default value. (This also represents 0 in the svg path.)
  Small = 0,
  /// Choose the large one. (This also represents 1 in the svg path.)
  Large = 1,
};

/// The <size> in ray() function.
///
/// https://drafts.fxtf.org/motion-1/#valdef-offsetpath-size
enum class StyleRaySize : uint8_t {
  ClosestSide,
  ClosestCorner,
  FarthestSide,
  FarthestCorner,
  Sides,
};

/// The CORS mode used for a CSS load.
enum class StyleCorsMode : uint8_t {
  /// No CORS mode, so cross-origin loads can be done.
  None,
  /// Anonymous CORS request.
  Anonymous,
};

/// The <coord-box> value, which defines the box that the <offset-path> sizes into.
/// https://drafts.fxtf.org/motion-1/#valdef-offset-path-coord-box
///
/// <coord-box> = content-box | padding-box | border-box | fill-box | stroke-box | view-box
/// https://drafts.csswg.org/css-box-4/#typedef-coord-box
enum class StyleCoordBox : uint8_t {
  ContentBox,
  PaddingBox,
  BorderBox,
  FillBox,
  StrokeBox,
  ViewBox,
};

/// A specified value for <transition-behavior-value>.
///
/// https://drafts.csswg.org/css-transitions-2/#transition-behavior-property
enum class StyleTransitionBehavior : uint8_t {
  /// Transitions will not be started for discrete properties, only for interpolable properties.
  Normal,
  /// Transitions will be started for discrete properties as well as interpolable properties.
  AllowDiscrete,
};

/// Each style rule has an origin, which determines where it enters the cascade.
///
/// <https://drafts.csswg.org/css-cascade/#cascading-origins>
enum class StyleOrigin : uint8_t {
  /// <https://drafts.csswg.org/css-cascade/#cascade-origin-user-agent>
  UserAgent = 1,
  /// <https://drafts.csswg.org/css-cascade/#cascade-origin-user>
  User = 2,
  /// <https://drafts.csswg.org/css-cascade/#cascade-origin-author>
  Author = 4,
};

/// Whether @import rules are allowed.
enum class StyleAllowImportRules : uint8_t {
  /// @import rules will be parsed.
  Yes,
  /// @import rules will not be parsed.
  No,
};

/// The kind of sanitization to use when parsing a stylesheet.
enum class StyleSanitizationKind : uint8_t {
  /// Perform no sanitization.
  None,
  /// Allow only @font-face, style rules, and @namespace.
  Standard,
  /// Allow everything but conditional rules.
  NoConditionalRules,
};

/// https://drafts.csswg.org/cssom-1/#dom-cssrule-type
enum class StyleCssRuleType : uint8_t {
  Style = 1,
  Import = 3,
  Media = 4,
  FontFace = 5,
  Page = 6,
  Keyframes = 7,
  Keyframe = 8,
  Margin = 9,
  Namespace = 10,
  CounterStyle = 11,
  Supports = 12,
  Document = 13,
  FontFeatureValues = 14,
  LayerBlock = 16,
  LayerStatement = 17,
  Container = 18,
  FontPaletteValues = 19,
  Property = 20,
  Scope = 21,
  StartingStyle = 22,
  PositionTry = 23,
  NestedDeclarations = 24,
  CustomMedia = 25,
  AppearanceBase = 26,
  ViewTransition = 27,
};

/// A font-display value for a @font-face rule.
/// The font-display descriptor determines how a font face is displayed based
/// on whether and when it is downloaded and ready to use.
enum class StyleFontDisplay : uint8_t {
  Auto,
  Block,
  Swap,
  Fallback,
  Optional,
};

/// Keywords for the font-face src descriptor's format() function.
/// ('None' and 'Unknown' are for internal use in gfx, not exposed to CSS.)
enum class StyleFontFaceSourceFormatKeyword : uint8_t {
  None,
  Collection,
  EmbeddedOpentype,
  Opentype,
  Svg,
  Truetype,
  Woff,
  Woff2,
  Unknown,
};

enum class StyleIsOrdinalInRange : uint8_t {
  Auto,
  InRange,
  NotInRange,
  NoOrdinalSpecified,
};

enum class StyleCounterSystem : uint8_t {
  Cyclic = 0,
  Numeric,
  Alphabetic,
  Symbolic,
  Additive,
  Fixed,
  Extends,
};

/// How to swap values for the automatically-generated position tactic.
enum class StylePositionTryFallbacksTryTacticKeyword : uint8_t {
  /// Swap the values in the block axis.
  FlipBlock,
  /// Swap the values in the inline axis.
  FlipInline,
  /// Swap the values in the start properties.
  FlipStart,
  /// Swap the values in the X axis.
  FlipX,
  /// Swap the values in the Y axis.
  FlipY,
};

/// A three-bit value that represents the axis in which position-area operates on.
/// Represented as 4 bits: axis type (physical or logical), direction type (physical or logical),
/// axis value.
///
/// There are two special values on top (Inferred and None) that represent ambiguous or axis-less
/// keywords, respectively.
enum class StylePositionAreaAxis : uint8_t {
  Horizontal = 0,
  Vertical = 1,
  X = 2,
  Y = 3,
  Block = 6,
  Inline = 7,
  Inferred = 4,
  None = 5,
};

/// Specifies which tracks(s) on the axis that the position-area span occupies.
/// Represented as 3 bits: start, center, end track.
enum class StylePositionAreaTrack : uint8_t {
  /// First track
  Start = 1,
  /// First and center.
  SpanStart = 3,
  /// Last track.
  End = 4,
  /// Last and center.
  SpanEnd = 6,
  /// Center track.
  Center = 2,
  /// All tracks
  SpanAll = 7,
};

/// Possible values for the `position-area` property's keywords.
/// Represented by [0z xxx yyy], where z means "self wm resolution", xxxx is the axis (as in
/// PositionAreaAxis) and yyy is the PositionAreaTrack
/// https://drafts.csswg.org/css-anchor-position-1/#propdef-position-area
enum class StylePositionAreaKeyword : uint8_t {
  None = ((uint8_t)StylePositionAreaAxis::None << StyleAXIS_SHIFT),
  Center = (((uint8_t)StylePositionAreaAxis::None << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::Center),
  SpanAll = (((uint8_t)StylePositionAreaAxis::None << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanAll),
  Start = (((uint8_t)StylePositionAreaAxis::Inferred << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::Start),
  End = (((uint8_t)StylePositionAreaAxis::Inferred << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::End),
  SpanStart = (((uint8_t)StylePositionAreaAxis::Inferred << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanStart),
  SpanEnd = (((uint8_t)StylePositionAreaAxis::Inferred << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanEnd),
  Left = (((uint8_t)StylePositionAreaAxis::Horizontal << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::Start),
  Right = (((uint8_t)StylePositionAreaAxis::Horizontal << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::End),
  Top = (((uint8_t)StylePositionAreaAxis::Vertical << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::Start),
  Bottom = (((uint8_t)StylePositionAreaAxis::Vertical << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::End),
  XStart = (((uint8_t)StylePositionAreaAxis::X << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::Start),
  XEnd = (((uint8_t)StylePositionAreaAxis::X << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::End),
  YStart = (((uint8_t)StylePositionAreaAxis::Y << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::Start),
  YEnd = (((uint8_t)StylePositionAreaAxis::Y << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::End),
  BlockStart = (((uint8_t)StylePositionAreaAxis::Block << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::Start),
  BlockEnd = (((uint8_t)StylePositionAreaAxis::Block << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::End),
  InlineStart = (((uint8_t)StylePositionAreaAxis::Inline << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::Start),
  InlineEnd = (((uint8_t)StylePositionAreaAxis::Inline << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::End),
  SpanLeft = (((uint8_t)StylePositionAreaAxis::Horizontal << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanStart),
  SpanRight = (((uint8_t)StylePositionAreaAxis::Horizontal << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanEnd),
  SpanTop = (((uint8_t)StylePositionAreaAxis::Vertical << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanStart),
  SpanBottom = (((uint8_t)StylePositionAreaAxis::Vertical << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanEnd),
  SpanXStart = (((uint8_t)StylePositionAreaAxis::X << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanStart),
  SpanXEnd = (((uint8_t)StylePositionAreaAxis::X << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanEnd),
  SpanYStart = (((uint8_t)StylePositionAreaAxis::Y << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanStart),
  SpanYEnd = (((uint8_t)StylePositionAreaAxis::Y << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanEnd),
  SpanBlockStart = (((uint8_t)StylePositionAreaAxis::Block << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanStart),
  SpanBlockEnd = (((uint8_t)StylePositionAreaAxis::Block << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanEnd),
  SpanInlineStart = (((uint8_t)StylePositionAreaAxis::Inline << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanStart),
  SpanInlineEnd = (((uint8_t)StylePositionAreaAxis::Inline << StyleAXIS_SHIFT) | (uint8_t)StylePositionAreaTrack::SpanEnd),
  SelfStart = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::Start),
  SelfEnd = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::End),
  SpanSelfStart = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::SpanStart),
  SpanSelfEnd = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::SpanEnd),
  SelfXStart = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::XStart),
  SelfXEnd = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::XEnd),
  SelfYStart = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::YStart),
  SelfYEnd = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::YEnd),
  SelfBlockStart = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::BlockStart),
  SelfBlockEnd = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::BlockEnd),
  SelfInlineStart = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::InlineStart),
  SelfInlineEnd = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::InlineEnd),
  SpanSelfXStart = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::SpanXStart),
  SpanSelfXEnd = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::SpanXEnd),
  SpanSelfYStart = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::SpanYStart),
  SpanSelfYEnd = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::SpanYEnd),
  SpanSelfBlockStart = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::SpanBlockStart),
  SpanSelfBlockEnd = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::SpanBlockEnd),
  SpanSelfInlineStart = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::SpanInlineStart),
  SpanSelfInlineEnd = (StyleSELF_WM | (uint8_t)StylePositionAreaKeyword::SpanInlineEnd),
};

enum class StyleMatchingDeclarationBlockOrigin : uint8_t {
  UserAgent,
  User,
  Author,
  PresHints,
  PositionFallback,
  Animations,
  Transitions,
  SMIL,
};

enum class StyleTimingKeyword : uint8_t {
  Linear,
  Ease,
  EaseIn,
  EaseOut,
  EaseInOut,
};

enum class StyleStepPosition : uint8_t {
  JumpStart,
  JumpEnd,
  JumpNone,
  JumpBoth,
  Start,
  End,
};

/// The <timeline-range-name> value type, which indicates a CSS identifier representing one of the
/// predefined named timeline ranges.
/// https://drafts.csswg.org/scroll-animations-1/#named-ranges
///
/// For now, only view timeline ranges use this type.
/// https://drafts.csswg.org/scroll-animations-1/#view-timelines-ranges
enum class StyleTimelineRangeName : uint8_t {
  /// The default normal value.
  Normal,
  /// No timeline range name specified.
  None,
  /// Represents the full range of the view progress timeline
  Cover,
  /// Represents the range during which the principal box is either fully contained by, or fully
  /// covers, its view progress visibility range within the scrollport.
  Contain,
  /// Represents the range during which the principal box is entering the view progress
  /// visibility range.
  Entry,
  /// Represents the range during which the principal box is exiting the view progress visibility
  /// range.
  Exit,
  /// Represents the range during which the principal box crosses the end border edge.
  EntryCrossing,
  /// Represents the range during which the principal box crosses the start border edge.
  ExitCrossing,
  /// Represents the full range of the scroll container on which the view progress timeline is
  /// defined.
  Scroll,
};

/// The unit of a `<length>` value. Note that if any new font-relative value is
/// added here, `custom_properties::NonCustomReferences::from_unit`
/// must also be updated. Consult the comment in that function as to why.
///
/// The variants are grouped (absolute, font-relative, viewport, container,
/// servo-internal) so that `is_*` predicates can be implemented with simple
/// range checks.
enum class StyleLengthUnit : uint8_t {
  Px,
  In,
  Cm,
  Mm,
  Q,
  Pt,
  Pc,
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
  Cqw,
  Cqh,
  Cqi,
  Cqb,
  Cqmin,
  Cqmax,
  /// HTML5 "character width", as defined in HTML5 § 14.5.4. Internal-only.
  ServoCharacterWidth,
};

/// The unit of a `<angle>` value.
enum class StyleAngleUnit : uint8_t {
  /// `deg`
  Deg,
  /// `grad`
  Grad,
  /// `rad`
  Rad,
  /// `turn`
  Turn,
};

/// A time unit.
enum class StyleTimeUnit : uint8_t {
  /// `s`
  Second,
  /// `ms`
  Millisecond,
};

/// The unit of a `<resolution>` value.
enum class StyleResolutionUnit : uint8_t {
  /// Dots per inch.
  Dpi,
  /// An alias unit for dots per pixel.
  X,
  /// Dots per pixel.
  Dppx,
  /// Dots per centimeter.
  Dpcm,
};

/// A CSS tree-counting function: `sibling-index()` or `sibling-count()`.
/// See <https://www.w3.org/TR/css-values-5/#tree-counting>.
enum class StyleTreeCountingFunction : uint8_t {
  /// `sibling-count()`: the total number of siblings of the element, including itself.
  SiblingCount,
  /// `sibling-index()`: the 1-based index of the element among its siblings.
  SiblingIndex,
};

/// A hue-interpolation-method as defined in [1].
///
/// [1]: https://drafts.csswg.org/css-color-4/#typedef-hue-interpolation-method
enum class StyleHueInterpolationMethod : uint8_t {
  /// https://drafts.csswg.org/css-color-4/#shorter
  Shorter,
  /// https://drafts.csswg.org/css-color-4/#longer
  Longer,
  /// https://drafts.csswg.org/css-color-4/#increasing
  Increasing,
  /// https://drafts.csswg.org/css-color-4/#decreasing
  Decreasing,
  /// https://drafts.csswg.org/css-color-4/#specified
  Specified,
};

enum class StyleCssSupportsUrlContext : uint8_t {
  Default,
  Chrome,
};

/// Whether this container uses attr() references and if so whether or not this
/// is a named or unnamed container query. Used for determining which kind of
/// restyle hint we need when traversing invalidation.
enum class StyleContainerAttributeDependencyKind {
  /// This container does not use attr() references.
  None = 0,
  /// This unnamed container uses attr() references.
  UnnamedContainer = 1,
  /// This named container uses attr() references.
  NamedContainer = 2,
};

/// Which edge side should the invalidation run for?
enum class StyleRelativeSelectorNthEdgeInvalidateFor : uint8_t {
  First,
  Last,
};

enum class StylePhysicalSide : uint8_t {
  Top = 0,
  Right,
  Bottom,
  Left,
};

enum class StylePhysicalAxis : uint8_t {
  Vertical = 0,
  Horizontal,
};

/// Font family names must either be given quoted as strings,
/// or unquoted as a sequence of one or more identifiers.
enum class StyleFontFamilyNameSyntax : uint8_t {
  /// The family name was specified in a quoted form, e.g. "Font Name"
  /// or 'Font Name'.
  Quoted,
  /// The family name was specified in an unquoted form as a sequence of
  /// identifiers.
  Identifiers,
};

/// A generic font-family name.
///
/// The order here is important, if you change it make sure that
/// `gfxPlatformFontList.h`s ranged array and `gfxFontFamilyList`'s
/// sSingleGenerics are updated as well.
///
/// NOTE(emilio): Should be u8, but it's a u32 because of ABI issues between GCC
/// and LLVM see https://bugs.llvm.org/show_bug.cgi?id=44228 / bug 1600735 /
/// bug 1726515.
enum class StyleGenericFontFamily : uint32_t {
  /// No generic family specified, only for internal usage.
  ///
  /// NOTE(emilio): Gecko code relies on this variant being zero.
  None = 0,
  Serif,
  SansSerif,
  Monospace,
  Cursive,
  Fantasy,
#if defined(CBINDGEN_IS_GECKO)
  Math,
#endif
  SystemUi,
#if defined(CBINDGEN_IS_GECKO)
  /// An internal value for emoji font selection.
  MozEmoji,
#endif
};

/// A custom style use counter that we may want to record.
enum class StyleCustomUseCounter : uint32_t {
  /// Whether we reference a non-local uri at all.
  HasNonLocalUriDependency = 0,
  /// Whether we are likely to be using relative URIs that depend on our path depth.
  MaybeHasPathBaseUriDependency,
  /// Whether we are likely to be using relative URIs that depend on our full URI.
  MaybeHasFullBaseUriDependency,
  /// Dummy value, used for indexing purposes.
  Last,
};

/// The keywords allowed in the Cursor property.
///
/// https://drafts.csswg.org/css-ui-4/#propdef-cursor
enum class StyleCursorKind : uint8_t {
  None,
  Default,
  Pointer,
  ContextMenu,
  Help,
  Progress,
  Wait,
  Cell,
  Crosshair,
  Text,
  VerticalText,
  Alias,
  Copy,
  Move,
  NoDrop,
  NotAllowed,
  Grab,
  Grabbing,
  EResize,
  NResize,
  NeResize,
  NwResize,
  SResize,
  SeResize,
  SwResize,
  WResize,
  EwResize,
  NsResize,
  NeswResize,
  NwseResize,
  ColResize,
  RowResize,
  AllScroll,
  ZoomIn,
  ZoomOut,
  Auto,
};

/// <https://drafts.csswg.org/css-view-transitions-2/#view-transition-navigation>
enum class StyleNavigationType : uint8_t {
  /// No transition
  None,
  /// Perform transition if conditions are met
  Auto,
};

/// Before flag, defined as per https://drafts.csswg.org/css-easing/#before-flag
/// This flag is never user-specified.
enum class StyleEasingBeforeFlag : uint8_t {
  Unset,
  Set,
};

enum class StyleRegisterCustomPropertyResult : uint8_t {
  SuccessfullyRegistered,
  InvalidName,
  AlreadyRegistered,
  InvalidSyntax,
  NoInitialValue,
  InvalidInitialValue,
  InitialValueNotComputationallyIndependent,
};

/// Any warning a selector may generate.
/// TODO(dshin): Bug 1860634 - Merge with never matching host selector warning, which is part of the rule parser.
enum class StyleSelectorWarningKind : uint8_t {
  /// Relative Selector with not enough constraint, either outside or inside the selector. e.g. `*:has(.a)`, `.a:has(*)`.
  /// May cause expensive invalidations for every element inserted and/or removed.
  UnconstraintedRelativeSelector,
  /// `:scope` can have 3 meanings, but in all cases, the relationship is defined strictly by an ancestor-descendant
  /// relationship. This means that any presence of sibling selectors to its right would make it never match.
  SiblingCombinatorAfterScopeSelector,
};

enum class StyleLogicalAxis : uint8_t {
  Block = 0,
  Inline,
};

/// Specified keyword values for case transforms in the text-transform property. (These are exclusive.)
enum class StyleTextTransformCase {
  /// No case transform.
  None,
  /// All uppercase.
  Uppercase,
  /// All lowercase.
  Lowercase,
  /// Capitalize each word.
  Capitalize,
  /// Automatic italicization of math variables.
  MathAuto,
};

#if defined(CBINDGEN_IS_SERVO)
/// A pseudo-element, both public and private.
///
/// NB: If you add to this list, be sure to update `each_simple_pseudo_element` too.
enum class StylePseudoElement : uint8_t {
#if defined(CBINDGEN_IS_SERVO)
  After = 0,
#endif
#if defined(CBINDGEN_IS_SERVO)
  Before,
#endif
#if defined(CBINDGEN_IS_SERVO)
  Selection,
#endif
#if defined(CBINDGEN_IS_SERVO)
  FirstLetter,
#endif
#if defined(CBINDGEN_IS_SERVO)
  Backdrop,
#endif
#if defined(CBINDGEN_IS_SERVO)
  DetailsContent,
#endif
#if defined(CBINDGEN_IS_SERVO)
  Marker,
#endif
#if defined(CBINDGEN_IS_SERVO)
  ColorSwatch,
#endif
#if defined(CBINDGEN_IS_SERVO)
  FileSelectorButton,
#endif
#if defined(CBINDGEN_IS_SERVO)
  Placeholder,
#endif
#if defined(CBINDGEN_IS_SERVO)
  SliderFill,
#endif
#if defined(CBINDGEN_IS_SERVO)
  SliderThumb,
#endif
#if defined(CBINDGEN_IS_SERVO)
  SliderTrack,
#endif
#if defined(CBINDGEN_IS_SERVO)
  MozProgressBar,
#endif
#if defined(CBINDGEN_IS_SERVO)
  ServoTextControlInnerContainer,
#endif
#if defined(CBINDGEN_IS_SERVO)
  ServoTextControlInnerEditor,
#endif
#if defined(CBINDGEN_IS_SERVO)
  ServoAnonymousBox,
#endif
#if defined(CBINDGEN_IS_SERVO)
  ServoAnonymousTable,
#endif
#if defined(CBINDGEN_IS_SERVO)
  ServoAnonymousTableCell,
#endif
#if defined(CBINDGEN_IS_SERVO)
  ServoAnonymousTableRow,
#endif
#if defined(CBINDGEN_IS_SERVO)
  ServoTableGrid,
#endif
#if defined(CBINDGEN_IS_SERVO)
  ServoTableWrapper,
#endif
};
#endif

/// A specified value for the `alignment-baseline` property.
/// https://drafts.csswg.org/css-inline-3/#alignment-baseline
enum class StyleAlignmentBaseline : uint8_t {
  /// Use the dominant baseline choice of the parent.
  Baseline,
  /// Use the text-under baseline.
  TextBottom,
#if defined(CBINDGEN_IS_GECKO)
  /// Use the alphabetic baseline.
  Alphabetic,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// Use the ideographic-under baseline.
  Ideographic,
#endif
  /// In general, use the x-middle baselines; except under text-orientation: upright
  /// (where the alphabetic and x-height baselines are essentially meaningless) use
  /// the central baseline instead.
  Middle,
#if defined(CBINDGEN_IS_GECKO)
  /// Use the central baseline.
  Central,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// Use the math baseline.
  Mathematical,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// Use the hanging baseline.
  Hanging,
#endif
  /// Use the text-over baseline.
  TextTop,
#if defined(CBINDGEN_IS_GECKO)
  /// Used to implement the deprecated "align=middle" attribute for HTML img elements.
  MozMiddleWithBaseline,
#endif
};

/// A value for the <Scroller> used in scroll().
///
/// https://drafts.csswg.org/scroll-animations-1/rewrite#typedef-scroller
enum class StyleScroller : uint8_t {
  /// The nearest ancestor scroll container. (Default.)
  Nearest,
  /// The document viewport as the scroll container.
  Root,
  /// Specifies to use the element’s own principal box as the scroll container.
  SelfElement,
};

/// A value for the <Axis> used in scroll(), or a value for {scroll|view}-timeline-axis.
///
/// https://drafts.csswg.org/scroll-animations-1/#typedef-axis
/// https://drafts.csswg.org/scroll-animations-1/#scroll-timeline-axis
/// https://drafts.csswg.org/scroll-animations-1/#view-timeline-axis
enum class StyleScrollAxis : uint8_t {
  /// The block axis of the scroll container. (Default.)
  Block = 0,
  /// The inline axis of the scroll container.
  Inline = 1,
  /// The horizontal axis of the scroll container.
  X = 2,
  /// The vertical axis of the scroll container.
  Y = 3,
};

/// https://drafts.csswg.org/css-animations/#propdef-animation-direction
enum class StyleAnimationDirection : uint8_t {
  Normal,
  Reverse,
  Alternate,
  AlternateReverse,
};

/// The specified value of the `background-clip` and `mask-clip` properties.
///
/// This is the union of the keywords both properties accept; each property restricts the set it
/// actually allows during parsing (see `valid_for_background` / `valid_for_mask`).
///
/// https://drafts.csswg.org/css-backgrounds-4/#background-clip
/// https://drafts.fxtf.org/css-masking-1/#propdef-mask-clip
enum class StyleBackgroundClip : uint8_t {
  BorderBox,
  PaddingBox,
  ContentBox,
#if defined(CBINDGEN_IS_GECKO)
  FillBox,
#endif
#if defined(CBINDGEN_IS_GECKO)
  StrokeBox,
#endif
#if defined(CBINDGEN_IS_GECKO)
  ViewBox,
#endif
#if defined(CBINDGEN_IS_GECKO)
  NoClip,
#endif
#if defined(CBINDGEN_IS_GECKO)
  Text,
#endif
  BorderArea,
};

/// https://drafts.csswg.org/css-animations/#propdef-animation-fill-mode
enum class StyleAnimationFillMode : uint8_t {
  None,
  Forwards,
  Backwards,
  Both,
};

/// https://drafts.csswg.org/css-animations/#animation-play-state
enum class StyleAnimationPlayState : uint8_t {
  Running,
  Paused,
};

/// https://drafts.csswg.org/css-animations-2/#animation-composition
enum class StyleAnimationComposition : uint8_t {
  Replace,
  Add,
  Accumulate,
};

/// The value for the `appearance` property.
///
/// https://developer.mozilla.org/en-US/docs/Web/CSS/-moz-appearance
enum class StyleAppearance : uint8_t {
  /// No appearance at all.
  None,
  /// Default appearance for the element.
  ///
  /// This value doesn't make sense for -moz-default-appearance, but we don't bother to guard
  /// against parsing it.
  Auto,
  /// A searchfield.
  Searchfield,
  /// A multi-line text field, e.g. HTML <textarea>.
  Textarea,
  /// A checkbox element.
  Checkbox,
  /// A radio element within a radio group.
  Radio,
  /// A dropdown list.
  Menulist,
  /// List boxes.
  Listbox,
  /// A horizontal meter bar.
  Meter,
  /// A horizontal progress bar.
  ProgressBar,
  /// A typical dialog button.
  Button,
  /// A single-line text field, e.g. HTML <input type=text>.
  Textfield,
  /// The dropdown button(s) that open up a dropdown list.
  MenulistButton,
  /// https://drafts.csswg.org/css-forms/#appearance
  Base,
  /// Only relevant to the <select> element and ::picker(select) pseudo-element, allowing them to
  /// be styled.
  BaseSelect,
  /// Menu Popup background.
  Menupopup,
  /// The "arrowed" part of the dropdown button that open up a dropdown list.
  MozMenulistArrowButton,
  /// For HTML's <input type=number>
  NumberInput,
  /// For HTML's <input type=password>
  PasswordInput,
  /// nsRangeFrame and its subparts
  Range,
  /// The scrollbar slider
  ScrollbarHorizontal,
  ScrollbarVertical,
  /// A scrollbar button (up/down/left/right).
  /// Keep these in order (some code casts these values to `int` in order to
  /// compare them against each other).
  ScrollbarbuttonUp,
  ScrollbarbuttonDown,
  ScrollbarbuttonLeft,
  ScrollbarbuttonRight,
  /// The scrollbar thumb.
  ScrollbarthumbHorizontal,
  ScrollbarthumbVertical,
  /// The scroll corner
  Scrollcorner,
  /// The up button of a spin control.
  SpinnerUpbutton,
  /// The down button of a spin control.
  SpinnerDownbutton,
  /// A single toolbar button (with no associated dropdown).
  Toolbarbutton,
  /// A tooltip.
  Tooltip,
  /// Sidebar appearance.
  MozSidebar,
  /// Mac help button.
  MozMacHelpButton,
  /// An appearance value for the root, so that we can get tinting and unified toolbar looks
  /// (which require a transparent gecko background) without really using the whole transparency
  /// set-up which otherwise loses window borders, see bug 1870481.
  MozMacWindow,
  /// Windows themed window frame elements.
  MozWindowButtonBox,
  MozWindowButtonClose,
  MozWindowButtonMaximize,
  MozWindowButtonMinimize,
  MozWindowButtonRestore,
  MozWindowTitlebar,
  MozWindowTitlebarMaximized,
  MozWindowDecorations,
  MozMacDisclosureButtonClosed,
  MozMacDisclosureButtonOpen,
  /// A themed focus outline (for outline:auto).
  ///
  /// This isn't exposed to CSS at all, just here for convenience.
  FocusOutline,
  /// A dummy variant that should be last to let the GTK widget do hackery.
  Count,
};

/// A kind of break between two boxes.
///
/// https://drafts.csswg.org/css-break/#break-between
enum class StyleBreakBetween : uint8_t {
  Always,
  Auto,
  Page,
  Avoid,
  Left,
  Right,
};

/// A kind of break within a box.
///
/// https://drafts.csswg.org/css-break/#break-within
enum class StyleBreakWithin : uint8_t {
  Auto,
  Avoid,
  AvoidPage,
  AvoidColumn,
};

/// A specified value for a single side of a `border-style` property.
///
/// The order here corresponds to the integer values from the border conflict
/// resolution rules in CSS 2.1 § 17.6.2.1. Higher values override lower values.
enum class StyleBorderStyle : uint8_t {
  Hidden,
  None,
  Inset,
  Groove,
  Outset,
  Ridge,
  Dotted,
  Dashed,
  Solid,
  Double,
};

/// Specified values for the `caption-side` property.
///
/// Note that despite having "physical" names, these are actually interpreted
/// according to the table's writing-mode: Top and Bottom are treated as
/// block-start and -end respectively.
///
/// https://drafts.csswg.org/css-tables/#propdef-caption-side
enum class StyleCaptionSide : uint8_t {
  Top,
  Bottom,
};

#if defined(CBINDGEN_IS_GECKO)
/// Values for the color-gamut media feature.
/// This implements PartialOrd so that lower values will correctly match
/// higher capabilities.
enum class StyleColorGamut : uint8_t {
#if defined(CBINDGEN_IS_GECKO)
  /// The sRGB gamut.
  Srgb,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// The gamut specified by the Display P3 Color Space.
  P3,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// The gamut specified by the ITU-R Recommendation BT.2020 Color Space.
  Rec2020,
#endif
};
#endif

/// A specified value for the `dominant-baseline` property.
/// https://drafts.csswg.org/css-inline-3/#dominant-baseline
enum class StyleDominantBaseline : uint8_t {
  /// Equivalent to 'alphabetic' in horizontal writing modes and in vertical writing
  /// modes when 'text-orientation' is sideways. Equivalent to 'central' in vertical
  /// writing modes when 'text-orientation' is 'mixed' or 'upright'.
  Auto,
  /// Use the text-under baseline.
  TextBottom,
  /// Use the alphabetic baseline.
  Alphabetic,
  /// Use the ideographic-under baseline.
  Ideographic,
  /// In general, use the x-middle baselines; except under text-orientation: upright
  /// (where the alphabetic and x-height baselines are essentially meaningless) use
  /// the central baseline instead.
  Middle,
  /// Use the central baseline.
  Central,
  /// Use the math baseline.
  Mathematical,
  /// Use the hanging baseline.
  Hanging,
  /// Use the text-over baseline.
  TextTop,
};

/// A boolean value for a pref query.
enum class StyleBoolValue : uint8_t {
  False,
  True,
};

/// Defines an element’s display type, which consists of
/// the two basic qualities of how an element generates boxes
/// <https://drafts.csswg.org/css-display/#propdef-display>
enum class StyleDisplayOutside : uint8_t {
  None = 0,
  Inline,
  Block,
  TableCaption,
  InternalTable,
#if defined(CBINDGEN_IS_GECKO)
  InternalRuby,
#endif
};

enum class StyleDisplayInside : uint8_t {
  None = 0,
  Contents,
  Flow,
  FlowRoot,
  Flex,
  Grid,
  GridLanes,
  Table,
  TableRowGroup,
  TableColumn,
  TableColumnGroup,
  TableHeaderGroup,
  TableFooterGroup,
  TableRow,
  TableCell,
#if defined(CBINDGEN_IS_GECKO)
  Ruby,
#endif
#if defined(CBINDGEN_IS_GECKO)
  RubyBase,
#endif
#if defined(CBINDGEN_IS_GECKO)
  RubyBaseContainer,
#endif
#if defined(CBINDGEN_IS_GECKO)
  RubyText,
#endif
#if defined(CBINDGEN_IS_GECKO)
  RubyTextContainer,
#endif
#if defined(CBINDGEN_IS_GECKO)
  WebkitBox,
#endif
};

#if defined(CBINDGEN_IS_GECKO)
/// Values for the display-mode media feature.
enum class StyleDisplayMode : uint8_t {
#if defined(CBINDGEN_IS_GECKO)
  Browser = 0,
#endif
#if defined(CBINDGEN_IS_GECKO)
  MinimalUi,
#endif
#if defined(CBINDGEN_IS_GECKO)
  Standalone,
#endif
#if defined(CBINDGEN_IS_GECKO)
  Fullscreen,
#endif
#if defined(CBINDGEN_IS_GECKO)
  PictureInPicture,
#endif
};
#endif

#if defined(CBINDGEN_IS_GECKO)
/// Allows front-end CSS to discern platform via media queries.
enum class StylePlatform : uint8_t {
#if defined(CBINDGEN_IS_GECKO)
  /// Matches any Android version.
  Android,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// For our purposes here, "linux" is just "gtk" (so unix-but-not-mac).
  /// There's no need for our front-end code to differentiate between those
  /// platforms and they already use the "linux" string elsewhere (e.g.,
  /// toolkit/themes/linux).
  Linux,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// Matches any iOS version.
  Ios,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// Matches any macOS version.
  Macos,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// Matches any Windows version.
  Windows,
#endif
};
#endif

/// https://drafts.csswg.org/css-anchor-position-1/#position-try-order-property
enum class StylePositionTryOrder : uint8_t {
  /// `normal`
  Normal,
  /// `most-width`
  MostWidth,
  /// `most-height`
  MostHeight,
  /// `most-block-size`
  MostBlockSize,
  /// `most-inline-size`
  MostInlineSize,
};

#if defined(CBINDGEN_IS_GECKO)
/// Allows front-end CSS to discern gtk theme via media queries.
enum class StyleGtkThemeFamily : uint8_t {
#if defined(CBINDGEN_IS_GECKO)
  /// Unknown theme family.
  Unknown = 0,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// Adwaita, the default GTK theme.
  Adwaita,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// Breeze, the default KDE theme.
  Breeze,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// Yaru, the default Ubuntu theme.
  Yaru,
#endif
};
#endif

/// Values for the prefers-color-scheme media feature.
enum class StylePrefersColorScheme : uint8_t {
  Light,
  Dark,
};

#if defined(CBINDGEN_IS_GECKO)
/// Possible values for prefers-contrast media query.
/// https://drafts.csswg.org/mediaqueries-5/#prefers-contrast
enum class StylePrefersContrast : uint8_t {
#if defined(CBINDGEN_IS_GECKO)
  /// More contrast is preferred.
  More,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// Low contrast is preferred.
  Less,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// Custom (not more, not less).
  Custom,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// The default value if neither high or low contrast is enabled.
  NoPreference,
#endif
};
#endif

#if defined(CBINDGEN_IS_GECKO)
/// Values for the dynamic-range and video-dynamic-range media features.
/// https://drafts.csswg.org/mediaqueries-5/#dynamic-range
/// This implements PartialOrd so that lower values will correctly match
/// higher capabilities.
enum class StyleDynamicRange : uint8_t {
#if defined(CBINDGEN_IS_GECKO)
  Standard,
#endif
#if defined(CBINDGEN_IS_GECKO)
  High,
#endif
};
#endif

#if defined(CBINDGEN_IS_GECKO)
/// Values for the scripting media feature.
/// https://drafts.csswg.org/mediaqueries-5/#scripting
enum class StyleScripting : uint8_t {
#if defined(CBINDGEN_IS_GECKO)
  /// Scripting is not supported or not enabled
  None,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// Scripting is supported and enabled, but only for initial page load
  /// We will never match this value as it is intended for non-browser user agents,
  /// but it is part of the spec so we should still parse it.
  /// See: https://github.com/w3c/csswg-drafts/issues/8621
  InitialOnly,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// Scripting is supported and enabled
  Enabled,
#endif
};
#endif

/// A value for any of the font-synthesis-{weight,small-caps,position} properties.
enum class StyleFontSynthesis : uint8_t {
  /// This attribute may be synthesized if not supported by a face.
  Auto,
  /// Do not attempt to synthesis this style attribute.
  None,
};

/// A value for the font-synthesis-style property.
enum class StyleFontSynthesisStyle : uint8_t {
  /// This attribute may be synthesized if not supported by a face.
  Auto,
  /// Do not attempt to synthesis this style attribute.
  None,
  /// Allow synthesis for oblique, but not for italic.
  ObliqueOnly,
};

/// The keywords allowed in the -moz-theme property.
enum class StyleMozTheme : uint8_t {
  /// Choose the default (maybe native) rendering.
  Auto,
  /// Choose the non-native rendering.
  NonNative,
};

/// Values for the `overflow-wrap` property.
enum class StyleOverflowWrap : uint8_t {
  Normal,
  BreakWord,
  Anywhere,
};

/// Internal -moz-user-focus property.
/// https://developer.mozilla.org/en-US/docs/Web/CSS/-moz-user-focus
enum class StyleUserFocus : uint8_t {
  Normal,
  None,
  Ignore,
};

/// The specified value for the `user-select` property.
///
/// https://drafts.csswg.org/css-ui-4/#propdef-user-select
enum class StyleUserSelect : uint8_t {
  Auto,
  Text,
  None,
#if defined(CBINDGEN_IS_SERVO)
  Contain,
#endif
  /// Force selection of all children.
  All,
};

/// The pointer-events property
/// https://svgwg.org/svg2-draft/interact.html#PointerEventsProperty
enum class StylePointerEvents : uint8_t {
  Auto,
  None,
#if defined(CBINDGEN_IS_GECKO)
  Visiblepainted,
#endif
#if defined(CBINDGEN_IS_GECKO)
  Visiblefill,
#endif
#if defined(CBINDGEN_IS_GECKO)
  Visiblestroke,
#endif
#if defined(CBINDGEN_IS_GECKO)
  Visible,
#endif
#if defined(CBINDGEN_IS_GECKO)
  Painted,
#endif
#if defined(CBINDGEN_IS_GECKO)
  Fill,
#endif
#if defined(CBINDGEN_IS_GECKO)
  Stroke,
#endif
#if defined(CBINDGEN_IS_GECKO)
  All,
#endif
};

/// Internal property to represent the inert attribute state:
/// https://html.spec.whatwg.org/multipage/#inert-subtrees
enum class StyleInert : uint8_t {
  None,
  Inert,
};

/// https://drafts.csswg.org/css-box/#propdef-float
enum class StyleFloat : uint8_t {
  Left,
  Right,
  None,
  InlineStart,
  InlineEnd,
};

/// https://drafts.csswg.org/css2/#propdef-clear
enum class StyleClear : uint8_t {
  None,
  Left,
  Right,
  Both,
  InlineStart,
  InlineEnd,
};

enum class StyleOverscrollBehavior : uint8_t {
  Auto,
  Contain,
  Chain,
  None,
};

/// Specified value of scroll-snap-align keyword value.
enum class StyleScrollSnapAlignKeyword : uint8_t {
  None,
  Start,
  End,
  Center,
};

/// https://drafts.csswg.org/css-scroll-snap-1/#snap-axis
enum class StyleScrollSnapAxis : uint8_t {
  X,
  Y,
  Block,
  Inline,
  Both,
};

enum class StyleScrollSnapStop : uint8_t {
  Normal,
  Always,
};

/// https://drafts.csswg.org/css-scroll-snap-1/#snap-strictness
enum class StyleScrollSnapStrictness : uint8_t {
  None,
  Mandatory,
  Proximity,
};

enum class StyleOverflowAnchor : uint8_t {
  Auto,
  None,
};

/// https://drafts.csswg.org/css-overflow-4/#overflow-clip-margin's <visual-box>. Note that the
/// spec has special behavior for the omitted keyword, but that's rather odd, see:
/// https://github.com/w3c/csswg-drafts/issues/13185
enum class StyleOverflowClipMarginBox : uint8_t {
  ContentBox,
  PaddingBox,
  BorderBox,
};

/// A computed value for the `resize` property.
enum class StyleResize : uint8_t {
  None,
  Both,
  Horizontal,
  Vertical,
};

/// The value for the `overflow-x` / `overflow-y` properties.
enum class StyleOverflow : uint8_t {
  Visible,
  Hidden,
  Scroll,
  Auto,
  Clip,
};

#if defined(CBINDGEN_IS_GECKO)
/// How an URI might depend on our base URI.
///
/// TODO(emilio): See if necko can provide this, but for our case local refs or empty URIs are
/// totally fine even though they wouldn't be in general...
enum class StyleNonLocalUriDependency : uint8_t {
#if defined(CBINDGEN_IS_GECKO)
  /// No non-local URI dependencies.
  No = 0,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// URI is absolute or not dependent on the base uri otherwise.
  Absolute,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// We might depend on our path depth. E.g. `https://example.com/foo` and
  /// `https://example.com/bar` both resolve a relative URI like `baz.css` as
  /// `https://example.com/baz.css`.
  Path,
#endif
#if defined(CBINDGEN_IS_GECKO)
  /// We might depend on our full URI. This is the case for query strings (and, in the general
  /// case, local refs and empty URIs, but that's not the case for CSS as described below.
  Full,
#endif
};
#endif

/// Identifies specific font metrics for use in the <text-edge> typedef.
///
/// https://drafts.csswg.org/css-inline-3/#typedef-text-edge
enum class StyleTextEdgeKeyword : uint8_t {
  /// Use the text-over baseline/text-under baseline as the over/under edge.
  Text,
  /// Use the ideographic-over baseline/ideographic-under baseline as the over/under edge.
  Ideographic,
  /// Use the ideographic-ink-over baseline/ideographic-ink-under baseline as the over/under edge.
  IdeographicInk,
  /// Use the cap-height baseline as the over edge.
  Cap,
  /// Use the x-height baseline as the over edge.
  Ex,
  /// Use the alphabetic baseline as the under edge.
  Alphabetic,
};

/// Implements text-decoration-skip-ink which takes the keywords auto | none | all
///
/// https://drafts.csswg.org/css-text-decor-4/#text-decoration-skip-ink-property
enum class StyleTextDecorationSkipInk : uint8_t {
  Auto,
  None,
  All,
};

enum class StyleBaselineShiftKeyword : uint8_t {
  /// Lower by the offset appropriate for subscripts of the parent’s box. The UA may use the
  /// parent’s font metrics to find this offset; otherwise it defaults to dropping by one
  /// fifth of the parent’s used font-size.
  Sub,
  /// Raise by the offset appropriate for superscripts of the parent’s box. The UA may use the
  /// parent’s font metrics to find this offset; otherwise it defaults to raising by one third
  /// of the parent’s used font-size.
  Super,
  /// Align the line-over edge of the aligned subtree with the line-over edge of the line box.
  Top,
  /// Align the center of the aligned subtree with the center of the line box.
  Center,
  /// Align the line-under edge of the aligned subtree with the line-under edge of the line box.
  Bottom,
};

/// A specified value for the `baseline-source` property.
/// https://drafts.csswg.org/css-inline-3/#baseline-source
enum class StyleBaselineSource : uint8_t {
  /// `Last` for `inline-block`, `First` otherwise.
  Auto,
  /// Use first baseline for alignment.
  First,
  /// Use last baseline for alignment.
  Last,
};

/// A single border-image-repeat keyword.
enum class StyleBorderImageRepeatKeyword : uint8_t {
  Stretch,
  Repeat,
  Round,
  Space,
};

/// The specified value of `transform-box`.
/// https://drafts.csswg.org/css-transforms-1/#transform-box
enum class StyleTransformBox : uint8_t {
  ContentBox,
  BorderBox,
  FillBox,
  StrokeBox,
  ViewBox,
};

/// Values for the `line-break` property.
enum class StyleLineBreak : uint8_t {
  Auto,
  Loose,
  Normal,
  Strict,
  Anywhere,
};

/// A keyword for the maximum lines used by `line-clamp`.
enum class StyleMaxLinesKeyword : uint8_t {
  /// No block-size clamping is applied.
  None,
  /// Clamp using the available block size.
  Auto,
};

/// Values for the `word-break` property.
enum class StyleWordBreak : uint8_t {
  Normal,
  BreakAll,
  KeepAll,
#if defined(CBINDGEN_IS_GECKO)
  /// The break-word value, needed for compat.
  ///
  /// Specifying `word-break: break-word` makes `overflow-wrap` behave as
  /// `anywhere`, and `word-break` behave like `normal`.
  BreakWord,
#endif
};

/// https://drafts.csswg.org/css-contain-2/#content-visibility
enum class StyleContentVisibility : uint8_t {
  /// `auto` variant, the element turns on layout containment, style containment, and paint
  /// containment. In addition, if the element is not relevant to the user (such as by being
  /// offscreen) it also skips its content
  Auto,
  /// `hidden` variant, the element skips its content
  Hidden,
  /// 'visible' variant, no effect
  Visible,
};

/// Values for the `text-justify` CSS property.
enum class StyleTextJustify : uint8_t {
  Auto,
  None,
  InterWord,
  InterCharacter,
};

/// Values for the `-moz-control-character-visibility` CSS property.
enum class StyleMozControlCharacterVisibility : uint8_t {
  Hidden,
  Visible,
};

/// Values for `ruby-position` property
enum class StyleRubyPosition : uint8_t {
  AlternateOver,
  AlternateUnder,
  Over,
  Under,
};

#if defined(CBINDGEN_IS_GECKO)
/// System colors. A bunch of these are ad-hoc, others come from Windows:
///
///   https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getsyscolor
///
/// Others are HTML/CSS specific. Spec is:
///
///   https://drafts.csswg.org/css-color/#css-system-colors
///   https://drafts.csswg.org/css-color/#deprecated-system-colors
enum class StyleSystemColor : uint8_t {
  Activeborder,
  /// Background in the (active) titlebar.
  Activecaption,
  Appworkspace,
  Background,
  Buttonface,
  Buttonhighlight,
  Buttonshadow,
  Buttontext,
  Buttonborder,
  /// Text color in the (active) titlebar.
  Captiontext,
  Field,
  /// Used for disabled field backgrounds.
  MozDisabledfield,
  Fieldtext,
  Mark,
  Marktext,
  /// Combobox widgets
  MozComboboxtext,
  MozCombobox,
  Graytext,
  Highlight,
  Highlighttext,
  Inactiveborder,
  /// Background in the (inactive) titlebar.
  Inactivecaption,
  /// Text color in the (inactive) titlebar.
  Inactivecaptiontext,
  Infobackground,
  Infotext,
  Menu,
  Menutext,
  Scrollbar,
  Threeddarkshadow,
  Threedface,
  Threedhighlight,
  Threedlightshadow,
  Threedshadow,
  Window,
  Windowframe,
  Windowtext,
  Canvastext,
  Canvas,
  MozDialog,
  MozDialogtext,
  /// Used for selected but not focused cell backgrounds.
  MozCellhighlight,
  /// Used for selected but not focused cell text.
  MozCellhighlighttext,
  /// Used for selected and focused html cell backgrounds.
  Selecteditem,
  /// Used for selected and focused html cell text.
  Selecteditemtext,
  /// Used for menu item backgrounds when hovered.
  MozMenuhover,
  /// Used for menu item backgrounds when hovered and disabled.
  MozMenuhoverdisabled,
  /// Used for menu item text when hovered.
  MozMenuhovertext,
  /// Used for menubar item text when hovered.
  MozMenubarhovertext,
  /// On platforms where this color is the same as field, or transparent, use fieldtext as
  /// foreground color.
  MozOddtreerow,
  /// Used for button text background when hovered.
  MozButtonhoverface,
  /// Used for button text color when hovered.
  MozButtonhovertext,
  /// Used for button border color when hovered.
  MozButtonhoverborder,
  /// Used for button background when pressed.
  MozButtonactiveface,
  /// Used for button text when pressed.
  MozButtonactivetext,
  /// Used for button border when pressed.
  MozButtonactiveborder,
  /// Used for button background when disabled.
  MozButtondisabledface,
  /// Used for button border when disabled.
  MozButtondisabledborder,
  /// Colors used for the header bar (sorta like the tab bar / menubar).
  MozHeaderbar,
  MozHeaderbartext,
  MozHeaderbarinactive,
  MozHeaderbarinactivetext,
  /// Foreground color of default buttons.
  MozMacDefaultbuttontext,
  /// Ring color around text fields and lists.
  MozMacFocusring,
  /// Text color of disabled text on toolbars.
  MozMacDisabledtoolbartext,
  /// The background of a sidebar.
  MozSidebar,
  /// The foreground color of a sidebar.
  MozSidebartext,
  /// The border color of a sidebar.
  MozSidebarborder,
  /// Theme accent color.
  /// https://drafts.csswg.org/css-color-4/#valdef-system-color-accentcolor
  Accentcolor,
  /// Foreground for the accent color.
  /// https://drafts.csswg.org/css-color-4/#valdef-system-color-accentcolortext
  Accentcolortext,
  /// The background-color for :autofill-ed inputs.
  MozAutofillBackground,
  Linktext,
  Activetext,
  Visitedtext,
  /// Color of tree column headers
  MozColheader,
  MozColheadertext,
  MozColheaderhover,
  MozColheaderhovertext,
  MozColheaderactive,
  MozColheaderactivetext,
  TextSelectDisabledBackground,
  TextSelectAttentionBackground,
  TextSelectAttentionForeground,
  TextHighlightBackground,
  TextHighlightForeground,
  TargetTextBackground,
  TargetTextForeground,
  IMERawInputBackground,
  IMERawInputForeground,
  IMERawInputUnderline,
  IMESelectedRawTextBackground,
  IMESelectedRawTextForeground,
  IMESelectedRawTextUnderline,
  IMEConvertedTextBackground,
  IMEConvertedTextForeground,
  IMEConvertedTextUnderline,
  IMESelectedConvertedTextBackground,
  IMESelectedConvertedTextForeground,
  IMESelectedConvertedTextUnderline,
  SpellCheckerUnderline,
  ThemedScrollbar,
  ThemedScrollbarThumb,
  ThemedScrollbarThumbHover,
  ThemedScrollbarThumbActive,
  End,
};
#endif

#if defined(CBINDGEN_IS_SERVO)
/// System colors. A bunch of these are ad-hoc, others come from Windows:
///
///   https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getsyscolor
///
/// Others are HTML/CSS specific. Spec is:
///
///   https://drafts.csswg.org/css-color/#css-system-colors
///   https://drafts.csswg.org/css-color/#deprecated-system-colors
enum class StyleSystemColor : uint8_t {
  Accentcolor,
  Accentcolortext,
  Activetext,
  Linktext,
  Visitedtext,
  Buttonborder,
  Buttonface,
  Buttontext,
  Canvas,
  Canvastext,
  Field,
  Fieldtext,
  Graytext,
  Highlight,
  Highlighttext,
  Mark,
  Marktext,
  Selecteditem,
  Selecteditemtext,
  Activeborder,
  Inactiveborder,
  Threeddarkshadow,
  Threedhighlight,
  Threedlightshadow,
  Threedshadow,
  Windowframe,
  Buttonhighlight,
  Buttonshadow,
  Threedface,
  Activecaption,
  Appworkspace,
  Background,
  Inactivecaption,
  Infobackground,
  Menu,
  Scrollbar,
  Window,
  Captiontext,
  Infotext,
  Menutext,
  Windowtext,
  Inactivecaptiontext,
};
#endif

#if defined(CBINDGEN_IS_GECKO)
/// System fonts.
enum class StyleSystemFont : uint8_t {
  /// https://drafts.csswg.org/css-fonts/#valdef-font-caption
  Caption,
  /// https://drafts.csswg.org/css-fonts/#valdef-font-icon
  Icon,
  /// https://drafts.csswg.org/css-fonts/#valdef-font-menu
  Menu,
  /// https://drafts.csswg.org/css-fonts/#valdef-font-message-box
  MessageBox,
  /// https://drafts.csswg.org/css-fonts/#valdef-font-small-caption
  SmallCaption,
  /// https://drafts.csswg.org/css-fonts/#valdef-font-status-bar
  StatusBar,
  /// Internal system font, used by the `<menupopup>`s on macOS.
  MozPullDownMenu,
  /// Internal system font, used for `<button>` elements.
  MozButton,
  /// Internal font, used by `<select>` elements.
  MozList,
  /// Internal font, used by `<input>` elements.
  MozField,
  End,
};
#endif

/// A keyword for the X direction.
enum class StyleHorizontalPositionKeyword : uint8_t {
  Left,
  Right,
};

/// A keyword for the Y direction.
enum class StyleVerticalPositionKeyword : uint8_t {
  Top,
  Bottom,
};

/// Whether we used the modern notation or the compatibility `-webkit`, `-moz` prefixes.
enum class StyleGradientCompatMode : uint8_t {
  /// Modern syntax.
  Modern,
  /// `-webkit` prefix.
  WebKit,
  /// `-moz` prefix
  Moz,
};

/// <https://drafts.csswg.org/css-images/#typedef-extent-keyword>
enum class StyleShapeExtent : uint8_t {
  ClosestSide,
  FarthestSide,
  ClosestCorner,
  FarthestCorner,
  Contain,
  Cover,
};

/// Fill mode for the text-emphasis-style property
enum class StyleTextEmphasisFillMode : uint8_t {
  /// `filled`
  Filled,
  /// `open`
  Open,
};

/// Shape keyword for the text-emphasis-style property
enum class StyleTextEmphasisShapeKeyword : uint8_t {
  /// `dot`
  Dot,
  /// `circle`
  Circle,
  /// `double-circle`
  DoubleCircle,
  /// `triangle`
  Triangle,
  /// `sesame`
  Sesame,
};

/// The specified value for a single CSS paint-order property.
enum class StylePaintOrder : uint8_t {
  /// `normal` variant
  Normal = 0,
  /// `fill` variant
  Fill = 1,
  /// `stroke` variant
  Stroke = 2,
  /// `markers` variant
  Markers = 3,
};

/// The writing-mode property (different from the WritingMode enum).
/// https://drafts.csswg.org/css-writing-modes/#block-flow
/// Aliases come from https://drafts.csswg.org/css-writing-modes-4/#svg-writing-mode
enum class StyleWritingModeProperty : uint8_t {
  HorizontalTb,
  VerticalRl,
  VerticalLr,
#if defined(CBINDGEN_IS_GECKO)
  SidewaysRl,
#endif
#if defined(CBINDGEN_IS_GECKO)
  SidewaysLr,
#endif
};

/// https://drafts.csswg.org/css-counter-styles/#typedef-symbols-type
enum class StyleSymbolsType : uint8_t {
  Cyclic,
  Numeric,
  Alphabetic,
  Symbolic,
  Fixed,
};

enum class StyleTransformStyle : uint8_t {
  Flat,
  Preserve3d,
};

/// https://drafts.csswg.org/css-shapes-1/#typedef-shape-box
enum class StyleShapeBox : uint8_t {
  MarginBox,
  BorderBox,
  PaddingBox,
  ContentBox,
};

/// Specified value of text-align keyword value.
enum class StyleTextAlignKeyword : uint8_t {
  Start,
  Left,
  Right,
  Center,
  Justify,
  End,
  MozCenter,
  MozLeft,
  MozRight,
};

/// Specified and computed value of text-align-last.
enum class StyleTextAlignLast : uint8_t {
  Auto,
  Start,
  End,
  Left,
  Right,
  Center,
  Justify,
};

/// CSS font keywords
enum class StyleFontSizeKeyword : uint8_t {
  XXSmall,
  XSmall,
  Small,
  Medium,
  Large,
  XLarge,
  XXLarge,
  XXXLarge,
#if defined(CBINDGEN_IS_GECKO)
  /// Indicate whether to apply font-size: math is specified so that extra
  /// scaling due to math-depth changes is applied during the cascade.
  Math,
#endif
  None,
};

/// The kind of change that happened for a given rule.
enum class StyleRuleChangeKind : uint32_t {
  /// Some change in the rule which we don't know about, and could have made
  /// the rule change in any way.
  Generic = 0,
  /// The rule was inserted.
  Insertion,
  /// The rule was removed.
  Removal,
  /// A change in the declarations of a style rule.
  StyleRuleDeclarations,
  /// A change in the declarations of an @position-try rule.
  PositionTryDeclarations,
};

/// Page orientation names.
///
/// https://drafts.csswg.org/css-page-3/#page-orientation-prop
enum class StylePageOrientation : uint8_t {
  /// upright
  Upright,
  /// rotate-left (counter-clockwise)
  RotateLeft,
  /// rotate-right (clockwise)
  RotateRight,
};

/// Paper orientation
///
/// https://drafts.csswg.org/css-page-3/#page-size-prop
enum class StylePageSizeOrientation : uint8_t {
  /// Portrait orientation
  Portrait,
  /// Landscape orientation
  Landscape,
};

/// Internal -moz-image-decoding property. This allows images to be forcefully sync-decoded.
///
/// We use different defaults for sync vs. async decoding, which sometimes cause site issues.
enum class StyleImageDecoding : uint8_t {
  /// Use the default heuristics.
  Auto,
  /// Force sync-decoding.
  Sync,
};

/// https://drafts.csswg.org/css-images/#propdef-image-rendering
enum class StyleImageRendering : uint8_t {
  Auto,
#if defined(CBINDGEN_IS_GECKO)
  Smooth,
#endif
  CrispEdges,
  Pixelated,
#if defined(CBINDGEN_IS_GECKO)
  Optimizespeed,
#endif
#if defined(CBINDGEN_IS_GECKO)
  Optimizequality,
#endif
};

/// https://drafts.csswg.org/css-color-adjust/#print-color-adjust
enum class StylePrintColorAdjust : uint8_t {
  /// Ignore backgrounds and darken text.
  Economy,
  /// Respect specified colors.
  Exact,
};

/// https://drafts.csswg.org/css-color-adjust-1/#forced-color-adjust-prop
enum class StyleForcedColorAdjust : uint8_t {
  /// Adjust colors if needed.
  Auto,
  /// Respect specified colors.
  None,
};

/// Possible values for the forced-colors media query.
/// <https://drafts.csswg.org/mediaqueries-5/#forced-colors>
enum class StyleForcedColors : uint8_t {
  /// Page colors are not being forced.
  None,
  /// Page colors would be forced in content.
  Requested,
  /// Page colors are being forced.
  Active,
};

/// How to do font-size scaling.
enum class StyleXTextScale : uint8_t {
  /// Both min-font-size and text zoom are enabled.
  All,
  /// Text-only zoom is enabled, but min-font-size is not honored.
  ZoomOnly,
  /// Neither of them is enabled.
  None,
};

enum class StylePositionProperty : uint8_t {
  Static = 0,
  Relative,
  Absolute,
  Fixed,
  Sticky,
};

/// https://drafts.csswg.org/css-break/#propdef-box-decoration-break
enum class StyleBoxDecorationBreak : uint8_t {
  Slice,
  Clone,
};

/// https://drafts.csswg.org/css-backgrounds/#the-background-attachment
enum class StyleImageLayerAttachment : uint8_t {
  Scroll,
  Fixed,
#if defined(CBINDGEN_IS_GECKO)
  Local,
#endif
};

/// Nonstandard (https://developer.mozilla.org/en-US/docs/Web/CSS/-moz-float-edge)
enum class StyleFloatEdge : uint8_t {
  ContentBox,
  MarginBox,
};

/// Whether an element lives in the top layer. Set by UA sheets.
enum class StyleTopLayer : uint8_t {
  None,
  Auto,
};

/// https://drafts.csswg.org/cssom-view/#propdef-scroll-behavior
enum class StyleScrollBehavior : uint8_t {
  Auto,
  Smooth,
};

/// https://drafts.fxtf.org/compositing/#isolation
enum class StyleIsolation : uint8_t {
  Auto,
  Isolate,
};

/// https://drafts.csswg.org/css-transforms/#backface-visibility-property
enum class StyleBackfaceVisibility : uint8_t {
  Visible,
  Hidden,
};

/// Nonstandard (https://developer.mozilla.org/en-US/docs/Web/CSS/-moz-orient)
enum class StyleOrient : uint8_t {
  Inline,
  Block,
  Horizontal,
  Vertical,
};

/// https://drafts.csswg.org/css-multicol/#propdef-column-fill
enum class StyleColumnFill : uint8_t {
  Balance,
  Auto,
};

/// https://drafts.csswg.org/css-multicol/#propdef-column-span
enum class StyleColumnSpan : uint8_t {
  None,
  All,
};

/// https://w3c.github.io/mathml-core/#the-math-shift
enum class StyleMathShift : uint8_t {
  Normal,
  Compact,
};

/// https://drafts.csswg.org/css-box/#propdef-visibility
enum class StyleVisibility : uint8_t {
  Visible,
  Hidden,
  Collapse,
};

/// Whether flexbox visibility: collapse items use legacy -moz-box behavior or not.
enum class StyleBoxCollapse : uint8_t {
  Flex,
  Legacy,
};

/// https://drafts.csswg.org/css-writing-modes/#propdef-text-orientation
enum class StyleTextOrientation : uint8_t {
  Mixed,
  Upright,
  Sideways,
};

/// https://drafts.csswg.org/css-images/#propdef-image-orientation
enum class StyleImageOrientation : uint8_t {
  FromImage,
  None,
};

/// https://svgwg.org/svg2-draft/text.html#TextAnchorProperty
enum class StyleTextAnchor : uint8_t {
  Start,
  Middle,
  End,
};

/// https://svgwg.org/svg2-draft/painting.html#ShapeRenderingProperty
enum class StyleShapeRendering : uint8_t {
  Auto,
  Optimizespeed,
  Crispedges,
  Geometricprecision,
};

/// https://svgwg.org/svg2-draft/painting.html#StrokeLinecapProperty
enum class StyleStrokeLinecap : uint8_t {
  Butt,
  Round,
  Square,
};

/// https://svgwg.org/svg2-draft/painting.html#StrokeLinejoinProperty
enum class StyleStrokeLinejoin : uint8_t {
  Miter,
  Round,
  Bevel,
};

/// https://drafts.csswg.org/css-tables/#propdef-border-collapse
enum class StyleBorderCollapse : uint8_t {
  Separate,
  Collapse,
};

/// https://drafts.csswg.org/css-tables/#propdef-empty-cells
enum class StyleEmptyCells : uint8_t {
  Show,
  Hide,
};

/// https://drafts.csswg.org/css-text/#propdef-hyphens
enum class StyleHyphens : uint8_t {
  Manual,
  None,
  Auto,
};

/// https://drafts.csswg.org/css-size-adjust/#adjustment-control
enum class StyleTextSizeAdjust : uint8_t {
  Auto,
  None,
};

/// https://drafts.csswg.org/css-ruby/#ruby-align-property
enum class StyleRubyAlign : uint8_t {
  SpaceAround,
  Start,
  Center,
  SpaceBetween,
};

/// https://drafts.csswg.org/css-writing-modes-3/#text-combine-upright
enum class StyleTextCombineUpright : uint8_t {
  None,
  All,
};

/// https://svgwg.org/svg2-draft/painting.html#TextRenderingProperty
enum class StyleTextRendering : uint8_t {
  Auto,
  Optimizespeed,
  Optimizelegibility,
  Geometricprecision,
};

/// https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/-webkit-text-security
enum class StyleTextSecurity : uint8_t {
  None,
  Circle,
  Disc,
  Square,
};

/// https://drafts.csswg.org/css-text-4/#propdef-text-wrap-mode
enum class StyleTextWrapMode : uint8_t {
  Wrap,
  Nowrap,
};

/// https://drafts.csswg.org/css-text-4/#text-wrap-style
enum class StyleTextWrapStyle : uint8_t {
  Auto,
  Stable,
  Balance,
};

/// https://drafts.csswg.org/css-lists/#propdef-list-style-position
enum class StyleListStylePosition : uint8_t {
  Outside,
  Inside,
};

/// https://drafts.csswg.org/css-flexbox/#flex-direction-property
enum class StyleFlexDirection : uint8_t {
  Row,
  RowReverse,
  Column,
  ColumnReverse,
};

/// https://drafts.csswg.org/css-ui/#propdef-box-sizing
enum class StyleBoxSizing : uint8_t {
  ContentBox,
  BorderBox,
};

/// https://drafts.csswg.org/css-images/#propdef-object-fit
enum class StyleObjectFit : uint8_t {
  Fill,
  Contain,
  Cover,
  None,
  ScaleDown,
};

/// https://drafts.fxtf.org/css-masking-1/#propdef-mask-type
enum class StyleMaskType : uint8_t {
  Luminance,
  Alpha,
};

/// https://drafts.fxtf.org/css-masking-1/#propdef-mask-mode
enum class StyleMaskMode : uint8_t {
  MatchSource,
  Alpha,
  Luminance,
};

/// https://drafts.fxtf.org/css-masking-1/#propdef-mask-composite
enum class StyleMaskComposite : uint8_t {
  Add,
  Subtract,
  Intersect,
  Exclude,
};

/// https://drafts.csswg.org/css-tables/#propdef-table-layout
enum class StyleTableLayout : uint8_t {
  Auto,
  Fixed,
};

/// https://drafts.csswg.org/css-writing-modes/#propdef-unicode-bidi
enum class StyleUnicodeBidi : uint8_t {
  Normal,
  Embed,
  Isolate,
  BidiOverride,
  IsolateOverride,
  Plaintext,
};

/// https://drafts.csswg.org/css-ui/#input-method-editor
enum class StyleImeMode : uint8_t {
  Auto,
  Normal,
  Active,
  Disabled,
  Inactive,
};

/// https://drafts.csswg.org/css-scrollbars-1/#scrollbar-width
enum class StyleScrollbarWidth : uint8_t {
  Auto,
  Thin,
  None,
};

/// Privileged property to control titlebar dragging area.
enum class StyleWindowDragging : uint8_t {
  Default,
  Drag,
  NoDrag,
};

/// None (Nonstandard internal property)
enum class StyleWindowShadow : uint8_t {
  Auto,
  None,
};

/// https://drafts.csswg.org/css-ui/#field-sizing
enum class StyleFieldSizing : uint8_t {
  Fixed,
  Content,
};

/// Nonstandard (https://developer.mozilla.org/en-US/docs/Web/CSS/box-align)
enum class StyleBoxAlign : uint8_t {
  Stretch,
  Start,
  Center,
  Baseline,
  End,
};

/// Nonstandard (https://developer.mozilla.org/en-US/docs/Web/CSS/box-direction)
enum class StyleBoxDirection : uint8_t {
  Normal,
  Reverse,
};

/// Nonstandard (https://developer.mozilla.org/en-US/docs/Web/CSS/box-orient)
enum class StyleBoxOrient : uint8_t {
  Horizontal,
  Vertical,
};

/// Nonstandard (https://developer.mozilla.org/en-US/docs/Web/CSS/box-pack)
enum class StyleBoxPack : uint8_t {
  Start,
  Center,
  End,
  Justify,
};

/// https://drafts.fxtf.org/compositing/#propdef-mix-blend-mode
enum class StyleBlend : uint8_t {
  Normal,
  Multiply,
  Screen,
  Overlay,
  Darken,
  Lighten,
  ColorDodge,
  ColorBurn,
  HardLight,
  SoftLight,
  Difference,
  Exclusion,
  Hue,
  Saturation,
  Color,
  Luminosity,
  PlusLighter,
};

/// https://mathml-refresh.github.io/mathml-core/#the-math-style-property
enum class StyleMathStyle : uint8_t {
  Normal,
  Compact,
};

/// Internal (not web-exposed). Presentation attribute for legacy mathml mathvariant.
enum class StyleMathVariant : uint8_t {
  None,
  Normal,
  Bold,
  Italic,
  BoldItalic,
  Script,
  BoldScript,
  Fraktur,
  DoubleStruck,
  BoldFraktur,
  SansSerif,
  BoldSansSerif,
  SansSerifItalic,
  SansSerifBoldItalic,
  Monospace,
  Initial,
  Tailed,
  Looped,
  Stretched,
};

/// https://drafts.csswg.org/css-fonts/#propdef-font-variant-emoji
enum class StyleFontVariantEmoji : uint8_t {
  Normal,
  Text,
  Emoji,
  Unicode,
};

/// https://drafts.csswg.org/css-writing-modes/#propdef-direction
enum class StyleDirection : uint8_t {
  Ltr,
  Rtl,
};

/// https://drafts.csswg.org/css-text-decor/#propdef-text-decoration-style
enum class StyleTextDecorationStyle : uint8_t {
  None = 0,
  Dotted = 1,
  Dashed = 2,
  Solid = 3,
  Double = 4,
  Wavy = 5,
};

/// https://svgwg.org/svg2-draft/painting.html#ColorInterpolationProperty
enum class StyleColorInterpolation : uint8_t {
  Auto,
  Srgb,
  Linearrgb,
};

/// https://www.w3.org/TR/css-fonts-4/#font-optical-sizing-def
enum class StyleFontOpticalSizing : uint8_t {
  Auto,
  None,
};

/// https://drafts.csswg.org/css-fonts/#propdef-font-kerning
enum class StyleFontKerning : uint8_t {
  Auto,
  None,
  Normal,
};

/// Nonstandard (https://developer.mozilla.org/en-US/docs/Web/CSS/font-smooth)
enum class StyleFontSmoothing : uint8_t {
  Auto,
  Grayscale,
  SubpixelAntialiased,
};

/// https://drafts.csswg.org/css-fonts/#propdef-font-variant-position
enum class StyleFontVariantPosition : uint8_t {
  Normal,
  Sub,
  Super,
};

/// https://drafts.csswg.org/css-fonts/#propdef-font-variant-caps
enum class StyleFontVariantCaps : uint8_t {
  Normal,
  SmallCaps,
#if defined(CBINDGEN_IS_GECKO)
  AllSmallCaps,
#endif
#if defined(CBINDGEN_IS_GECKO)
  PetiteCaps,
#endif
#if defined(CBINDGEN_IS_GECKO)
  AllPetiteCaps,
#endif
#if defined(CBINDGEN_IS_GECKO)
  Unicase,
#endif
#if defined(CBINDGEN_IS_GECKO)
  TitlingCaps,
#endif
};

/// https://drafts.csswg.org/css-text-4/#propdef-white-space-collapse
enum class StyleWhiteSpaceCollapse : uint8_t {
  Collapse,
  Preserve,
  PreserveBreaks,
  BreakSpaces,
#if defined(CBINDGEN_IS_GECKO)
  PreserveSpaces,
#endif
};

/// https://drafts.csswg.org/css-backgrounds/#the-background-origin
///
/// Also used by mask-origin, which additionally accepts the SVG boxes.
enum class StyleBackgroundOrigin : uint8_t {
  BorderBox,
  PaddingBox,
  ContentBox,
#if defined(CBINDGEN_IS_GECKO)
  FillBox,
#endif
#if defined(CBINDGEN_IS_GECKO)
  StrokeBox,
#endif
#if defined(CBINDGEN_IS_GECKO)
  ViewBox,
#endif
};

#if defined(CBINDGEN_IS_GECKO)
/// Gecko-FFI-safe Arc (T is an ArcInner).
///
/// This can be null.
///
/// Leaks on drop. Please don't drop this.
template<typename GeckoType>
struct StyleStrong {
  const GeckoType *ptr;

  bool operator==(const StyleStrong& other) const {
    return ptr == other.ptr;
  }
  already_AddRefed<GeckoType> Consume() {
    already_AddRefed<GeckoType> ret(const_cast<GeckoType*>(ptr));
    ptr = nullptr;
    return ret;
  }
};
#endif

/// The 3 components that make up a color.  (Does not include the alpha component)
struct StyleColorComponents {
  float _0;
  float _1;
  float _2;

  bool operator==(const StyleColorComponents& other) const {
    return _0 == other._0 &&
           _1 == other._1 &&
           _2 == other._2;
  }
};

/// Flags used when serializing colors.
struct StyleColorFlags {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleColorFlags operator~() const {
    return StyleColorFlags { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleColorFlags operator|(const StyleColorFlags& other) const {
    return StyleColorFlags { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleColorFlags& operator|=(const StyleColorFlags& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleColorFlags operator&(const StyleColorFlags& other) const {
    return StyleColorFlags { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleColorFlags& operator&=(const StyleColorFlags& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleColorFlags operator^(const StyleColorFlags& other) const {
    return StyleColorFlags { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleColorFlags& operator^=(const StyleColorFlags& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleColorFlags& other) const {
    return _0 == other._0;
  }
  static const StyleColorFlags C0_IS_NONE;
  static const StyleColorFlags C1_IS_NONE;
  static const StyleColorFlags C2_IS_NONE;
  static const StyleColorFlags ALPHA_IS_NONE;
  static const StyleColorFlags NONE_FLAGS;
  static const StyleColorFlags IS_LEGACY_SRGB;
};
/// Whether the 1st color component is `none`.
constexpr inline const StyleColorFlags StyleColorFlags::C0_IS_NONE = StyleColorFlags{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// Whether the 2nd color component is `none`.
constexpr inline const StyleColorFlags StyleColorFlags::C1_IS_NONE = StyleColorFlags{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// Whether the 3rd color component is `none`.
constexpr inline const StyleColorFlags StyleColorFlags::C2_IS_NONE = StyleColorFlags{
  /* ._0 = */ (uint8_t)(1 << 2)
};
/// Whether the alpha component is `none`.
constexpr inline const StyleColorFlags StyleColorFlags::ALPHA_IS_NONE = StyleColorFlags{
  /* ._0 = */ (uint8_t)(1 << 3)
};
/// Whether any color or alpha component is `none`.
constexpr inline const StyleColorFlags StyleColorFlags::NONE_FLAGS = StyleColorFlags{
  /* ._0 = */ (uint8_t)((((StyleColorFlags::C0_IS_NONE)._0 | (StyleColorFlags::C1_IS_NONE)._0) | (StyleColorFlags::C2_IS_NONE)._0) | (StyleColorFlags::ALPHA_IS_NONE)._0)
};
/// Marks that this color is in the legacy color format. This flag is
/// only valid for the `Srgb` color space.
constexpr inline const StyleColorFlags StyleColorFlags::IS_LEGACY_SRGB = StyleColorFlags{
  /* ._0 = */ (uint8_t)(1 << 4)
};

/// An absolutely specified color, using either rgb(), rgba(), lab(), lch(),
/// oklab(), oklch() or color().
struct StyleAbsoluteColor {
  /// The 3 components that make up colors in any color space.
  StyleColorComponents components;
  /// The alpha component of the color.
  float alpha;
  /// The current color space that the components represent.
  StyleColorSpace color_space;
  /// Extra flags used during serialization of this color.
  StyleColorFlags flags;

  bool operator==(const StyleAbsoluteColor& other) const {
    return components == other.components &&
           alpha == other.alpha &&
           color_space == other.color_space &&
           flags == other.flags;
  }
  /**
   * Create a new AbsoluteColor in the sRGB color space in legacy color syntax.
   */
  static inline StyleAbsoluteColor SrgbLegacy(float red, float green, float blue, float alpha);

  static inline StyleAbsoluteColor FromColor(nscolor);

  /**
   * Convert this color into the given color space.
   */
  StyleAbsoluteColor ToColorSpace(StyleColorSpace aColorSpace) const;

  /**
   * Convert this color to an nscolor. The color will be converted to sRGB first
   * if required.
   */
  nscolor ToColor() const;
  static const StyleAbsoluteColor TRANSPARENT_BLACK;
  static const StyleAbsoluteColor BLACK;
  static const StyleAbsoluteColor WHITE;
};
/// A fully transparent color in the legacy syntax.
constexpr inline const StyleAbsoluteColor StyleAbsoluteColor::TRANSPARENT_BLACK = StyleAbsoluteColor{
  /* .components = */ StyleColorComponents{
    /* ._0 = */ 0.0,
    /* ._1 = */ 0.0,
    /* ._2 = */ 0.0
  },
  /* .alpha = */ 0.0,
  /* .color_space = */ StyleColorSpace::Srgb,
  /* .flags = */ StyleColorFlags::IS_LEGACY_SRGB
};
/// An opaque black color in the legacy syntax.
constexpr inline const StyleAbsoluteColor StyleAbsoluteColor::BLACK = StyleAbsoluteColor{
  /* .components = */ StyleColorComponents{
    /* ._0 = */ 0.0,
    /* ._1 = */ 0.0,
    /* ._2 = */ 0.0
  },
  /* .alpha = */ 1.0,
  /* .color_space = */ StyleColorSpace::Srgb,
  /* .flags = */ StyleColorFlags::IS_LEGACY_SRGB
};
/// An opaque white color in the legacy syntax.
constexpr inline const StyleAbsoluteColor StyleAbsoluteColor::WHITE = StyleAbsoluteColor{
  /* .components = */ StyleColorComponents{
    /* ._0 = */ 1.0,
    /* ._1 = */ 1.0,
    /* ._2 = */ 1.0
  },
  /* .alpha = */ 1.0,
  /* .color_space = */ StyleColorSpace::Srgb,
  /* .flags = */ StyleColorFlags::IS_LEGACY_SRGB
};

/// A CSS float value.
using StyleCSSFloat = float;

/// A `<number>` value.
using StyleNumber = StyleCSSFloat;

/// A value of the `Scale` property
///
/// <https://drafts.csswg.org/css-transforms-2/#individual-transforms>
template<typename Number>
struct StyleGenericScale {
  enum class Tag : uint8_t {
    /// 'none'
    None,
    /// '<number>{1,3}'
    Scale,
  };

  struct StyleScale_Body {
    Number _0;
    Number _1;
    Number _2;

    bool operator==(const StyleScale_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2;
    }
  };

  Tag tag;
  union {
    StyleScale_Body scale;
  };

  static StyleGenericScale None() {
    StyleGenericScale result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericScale Scale(const Number &_0,
                                 const Number &_1,
                                 const Number &_2) {
    StyleGenericScale result;
    ::new (&result.scale._0) (Number)(_0);
    ::new (&result.scale._1) (Number)(_1);
    ::new (&result.scale._2) (Number)(_2);
    result.tag = Tag::Scale;
    return result;
  }

  bool IsScale() const {
    return tag == Tag::Scale;
  }

  const StyleScale_Body& AsScale() const {
    MOZ_DIAGNOSTIC_ASSERT(IsScale());
    return scale;
  }

  bool operator==(const StyleGenericScale& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Scale: return scale == other.scale;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericScale() {

  }
  public:


  ~StyleGenericScale() {
    switch (tag) {
      case Tag::Scale: scale.~StyleScale_Body(); break;
      default: break;
    }
  }

  StyleGenericScale(const StyleGenericScale& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Scale: ::new (&scale) (StyleScale_Body)(other.scale); break;
      default: break;
    }
  }
  StyleGenericScale& operator=(const StyleGenericScale& other) {
    if (this != &other) {
      this->~StyleGenericScale();
      new (this) StyleGenericScale(other);
    }
    return *this;
  }
};

/// A computed CSS `scale`
using StyleScale = StyleGenericScale<StyleNumber>;

/// The computed `<length>` value.
struct StyleCSSPixelLength {
  StyleCSSFloat _0;

  bool operator==(const StyleCSSPixelLength& other) const {
    return _0 == other._0;
  }
  static StyleCSSPixelLength FromPixels(CSSCoord aCoord) { return {aCoord}; }
  static StyleCSSPixelLength Zero() { return FromPixels(0.0f); }

  inline nscoord ToAppUnits() const;
  inline bool IsZero() const;
  CSSCoord ToCSSPixels() const { return _0; }
  inline void ScaleBy(float);
  inline StyleCSSPixelLength ScaledBy(float) const;
};

/// An alias of computed `<length>` value.
using StyleLength = StyleCSSPixelLength;

/// A percentage value, where [0 .. 100%] maps to [0.0 .. 1.0]
struct StyleNoCalcPercentage {
  StyleCSSFloat _0;

  bool operator==(const StyleNoCalcPercentage& other) const {
    return _0 == other._0;
  }
};

/// An optional value, much like `Option<T>`, but with a defined struct layout
/// to be able to use it from C++ as well.
///
/// Note that this is relatively inefficient, struct-layout-wise, as you have
/// one byte for the tag, but padding to the alignment of T. If you have
/// multiple optional values and care about struct compactness, you might be
/// better off "coalescing" the combinations into a parent enum. But that
/// shouldn't matter for most use cases.
template<typename T>
struct StyleOptional {
  enum class Tag : uint8_t {
    None,
    Some,
  };

  struct StyleSome_Body {
    T _0;

    bool operator==(const StyleSome_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleSome_Body some;
  };

  static StyleOptional None() {
    StyleOptional result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleOptional Some(const T &_0) {
    StyleOptional result;
    ::new (&result.some._0) (T)(_0);
    result.tag = Tag::Some;
    return result;
  }

  bool IsSome() const {
    return tag == Tag::Some;
  }

  const T& AsSome() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSome());
    return some._0;
  }

  bool operator==(const StyleOptional& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Some: return some == other.some;
      default: break;
    }
    return true;
  }

  private:
  StyleOptional() {

  }
  public:


  ~StyleOptional() {
    switch (tag) {
      case Tag::Some: some.~StyleSome_Body(); break;
      default: break;
    }
  }

  StyleOptional(const StyleOptional& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Some: ::new (&some) (StyleSome_Body)(other.some); break;
      default: break;
    }
  }
  StyleOptional& operator=(const StyleOptional& other) {
    if (this != &other) {
      this->~StyleOptional();
      new (this) StyleOptional(other);
    }
    return *this;
  }
  explicit operator bool() const { return IsSome(); }

  const T& operator*() const { return AsSome(); }

  const T* operator->() const {
    return &AsSome();
  }
};

/// The value of a percentage leaf node that contains an associated percent hint.
struct StyleCalcPercentageLeaf {
  /// The percentage value.
  StyleNoCalcPercentage value;
  /// The base type the percentage resolves against, or None if there is
  /// no specific percent hint (this is used by CSS Typed OM when parsing
  /// an expression without the context of a property).
  StyleOptional<StyleNumericBaseType> hint;

  bool operator==(const StyleCalcPercentageLeaf& other) const {
    return value == other.value &&
           hint == other.hint;
  }
};

/// A computed angle in degrees.
struct StyleAngle {
  StyleCSSFloat _0;

  bool operator==(const StyleAngle& other) const {
    return _0 == other._0;
  }
  inline static StyleAngle Zero();
  inline float ToDegrees() const;
  inline double ToRadians() const;
  StyleAngle operator+(const StyleAngle& aAngle) const {
    return StyleAngle{_0 + aAngle._0};
  }
  StyleAngle operator-(const StyleAngle& aAngle) const {
    return StyleAngle{_0 - aAngle._0};
  }
};

/// A computed `<time>` value.
struct StyleTime {
  StyleCSSFloat seconds;

  bool operator==(const StyleTime& other) const {
    return seconds == other.seconds;
  }
 float ToSeconds() const { return seconds; }
 float ToMilliseconds() const { return seconds * 1000.0f; }
};

/// A computed `<resolution>`.
struct StyleResolution {
  StyleCSSFloat _0;

  bool operator==(const StyleResolution& other) const {
    return _0 == other._0;
  }
};

/// The computed leaf of a calc() expression.
union StyleComputedLeaf {
  enum class Tag : uint8_t {
    Length,
    Percentage,
    Number,
    Angle,
    Time,
    Resolution,
  };

  struct Length_Body {
    Tag tag;
    StyleLength _0;

    bool operator==(const Length_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Percentage_Body {
    Tag tag;
    StyleCalcPercentageLeaf _0;

    bool operator==(const Percentage_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Number_Body {
    Tag tag;
    StyleNumber _0;

    bool operator==(const Number_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Angle_Body {
    Tag tag;
    StyleAngle _0;

    bool operator==(const Angle_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Time_Body {
    Tag tag;
    StyleTime _0;

    bool operator==(const Time_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Resolution_Body {
    Tag tag;
    StyleResolution _0;

    bool operator==(const Resolution_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Length_Body length;
  Percentage_Body percentage;
  Number_Body number;
  Angle_Body angle;
  Time_Body time;
  Resolution_Body resolution;

  static StyleComputedLeaf Length(const StyleLength &_0) {
    StyleComputedLeaf result;
    ::new (&result.length._0) (StyleLength)(_0);
    result.tag = Tag::Length;
    return result;
  }

  bool IsLength() const {
    return tag == Tag::Length;
  }

  const StyleLength& AsLength() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLength());
    return length._0;
  }

  static StyleComputedLeaf Percentage(const StyleCalcPercentageLeaf &_0) {
    StyleComputedLeaf result;
    ::new (&result.percentage._0) (StyleCalcPercentageLeaf)(_0);
    result.tag = Tag::Percentage;
    return result;
  }

  bool IsPercentage() const {
    return tag == Tag::Percentage;
  }

  const StyleCalcPercentageLeaf& AsPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPercentage());
    return percentage._0;
  }

  static StyleComputedLeaf Number(const StyleNumber &_0) {
    StyleComputedLeaf result;
    ::new (&result.number._0) (StyleNumber)(_0);
    result.tag = Tag::Number;
    return result;
  }

  bool IsNumber() const {
    return tag == Tag::Number;
  }

  const StyleNumber& AsNumber() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNumber());
    return number._0;
  }

  static StyleComputedLeaf Angle(const StyleAngle &_0) {
    StyleComputedLeaf result;
    ::new (&result.angle._0) (StyleAngle)(_0);
    result.tag = Tag::Angle;
    return result;
  }

  bool IsAngle() const {
    return tag == Tag::Angle;
  }

  const StyleAngle& AsAngle() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAngle());
    return angle._0;
  }

  static StyleComputedLeaf Time(const StyleTime &_0) {
    StyleComputedLeaf result;
    ::new (&result.time._0) (StyleTime)(_0);
    result.tag = Tag::Time;
    return result;
  }

  bool IsTime() const {
    return tag == Tag::Time;
  }

  const StyleTime& AsTime() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTime());
    return time._0;
  }

  static StyleComputedLeaf Resolution(const StyleResolution &_0) {
    StyleComputedLeaf result;
    ::new (&result.resolution._0) (StyleResolution)(_0);
    result.tag = Tag::Resolution;
    return result;
  }

  bool IsResolution() const {
    return tag == Tag::Resolution;
  }

  const StyleResolution& AsResolution() const {
    MOZ_DIAGNOSTIC_ASSERT(IsResolution());
    return resolution._0;
  }

  bool operator==(const StyleComputedLeaf& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Length: return length == other.length;
      case Tag::Percentage: return percentage == other.percentage;
      case Tag::Number: return number == other.number;
      case Tag::Angle: return angle == other.angle;
      case Tag::Time: return time == other.time;
      case Tag::Resolution: return resolution == other.resolution;

    }
    return true;
  }

  private:
  StyleComputedLeaf() {

  }
  public:


  ~StyleComputedLeaf() {
    switch (tag) {
      case Tag::Length: length.~Length_Body(); break;
      case Tag::Percentage: percentage.~Percentage_Body(); break;
      case Tag::Number: number.~Number_Body(); break;
      case Tag::Angle: angle.~Angle_Body(); break;
      case Tag::Time: time.~Time_Body(); break;
      case Tag::Resolution: resolution.~Resolution_Body(); break;

    }
  }

  StyleComputedLeaf(const StyleComputedLeaf& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Length: ::new (&length) (Length_Body)(other.length); break;
      case Tag::Percentage: ::new (&percentage) (Percentage_Body)(other.percentage); break;
      case Tag::Number: ::new (&number) (Number_Body)(other.number); break;
      case Tag::Angle: ::new (&angle) (Angle_Body)(other.angle); break;
      case Tag::Time: ::new (&time) (Time_Body)(other.time); break;
      case Tag::Resolution: ::new (&resolution) (Resolution_Body)(other.resolution); break;

    }
  }
  StyleComputedLeaf& operator=(const StyleComputedLeaf& other) {
    if (this != &other) {
      this->~StyleComputedLeaf();
      new (this) StyleComputedLeaf(other);
    }
    return *this;
  }
};

/// A struct that basically replaces a `Box<[T]>`, but which cbindgen can
/// understand.
///
/// We could rely on the struct layout of `Box<[T]>` per:
///
///   https://github.com/rust-lang/unsafe-code-guidelines/blob/c138499c1de03b908dfe719a41193c84f8146883/reference/src/layout/pointers.md
///
/// But handling fat pointers with cbindgen both in structs and argument
/// positions more generally is a bit tricky.
///
template<typename T>
struct StyleOwnedSlice {
  T *ptr;
  size_t len;
  constexpr StyleOwnedSlice() :
    ptr((T*)alignof(T)),
    len(0) {}

  inline void Clear();
  inline void CopyFrom(const StyleOwnedSlice&);
  inline void SwapElements(StyleOwnedSlice&);

  StyleOwnedSlice& operator=(const StyleOwnedSlice&);
  StyleOwnedSlice& operator=(StyleOwnedSlice&&);

  inline StyleOwnedSlice(const StyleOwnedSlice&);
  inline StyleOwnedSlice(StyleOwnedSlice&&);
  inline explicit StyleOwnedSlice(Vector<T>&&);

  inline ~StyleOwnedSlice();

  Span<const T> AsSpan() const {
    return {ptr, len};
  }

  size_t Length() const {
    return len;
  }

  bool IsEmpty() const { return Length() == 0; }

  bool operator==(const StyleOwnedSlice& other) const {
    return AsSpan() == other.AsSpan();
  }
};

/// A `random()` function.
/// https://drafts.csswg.org/css-values-5/#funcdef-random
template<typename L>
struct StyleGenericRandomFunction {
  /// The `<random-key>`, resolving to the random base value.
  StyleGenericCalcNode<L> key;
  /// The minimum value the function can resolve to, inclusive.
  StyleGenericCalcNode<L> min;
  /// The maximum value the function can resolve to, inclusive.
  StyleGenericCalcNode<L> max;
  /// The optional step value.
  StyleOptional<StyleGenericCalcNode<L>> step;

  bool operator==(const StyleGenericRandomFunction& other) const {
    return key == other.key &&
           min == other.min &&
           max == other.max &&
           step == other.step;
  }
};

/// Fallback type for anchor functions within `calc()`.
/// Ideally, the fallback type is initial type of the property (e.g.
/// `GenericInset` for `left`), but that causes circular reference.
/// TODO(dshin, bug 2034100): Investigate ways to not require this.
/// This handles the parsing of unitless zeros, as well as ensuring
/// that e.g. `calc(anchor(--foo left, 1px) + 10%)` round trips
/// (sorting aside), instead of becoming
/// `calc(anchor(--foo left, calc(1px)) + 10%)`.
template<typename L>
struct StyleGenericAnchorFunctionFallback {
  /// Was this node parsed as a calc node?
  bool is_calc_node;
  /// The parsed fallback value. Stored as a calc node to break
  /// the circular reference.
  StyleGenericCalcNode<L> node;

  bool operator==(const StyleGenericAnchorFunctionFallback& other) const {
    return is_calc_node == other.is_calc_node &&
           node == other.node;
  }
};

#if defined(CBINDGEN_IS_GECKO)
/// A handle to a Gecko atom. This is a type that can represent either:
///
///  * A strong reference to a dynamic atom (an `nsAtom` pointer), in which case
///    the `usize` just holds the pointer value.
///
///  * An index from `gGkAtoms` to the `nsStaticAtom` object (shifted to the left one bit, and with
///    the lower bit set to `1` to differentiate it from the above), so `(index << 1 | 1)`.
///
struct StyleAtom {
  StyleNonZeroUsize _0;

  bool operator==(const StyleAtom& other) const {
    return _0 == other._0;
  }
  StyleAtom(size_t) = delete;
  StyleAtom() = delete;

  inline bool IsStatic() const;
  inline nsAtom* AsAtom() const;

 private:
  inline void AddRef();
  inline void Release();

 public:
  inline explicit StyleAtom(already_AddRefed<nsAtom>);
  inline explicit StyleAtom(nsStaticAtom*);
  inline StyleAtom(const StyleAtom& aOther);
  inline StyleAtom& operator=(const StyleAtom&);
  inline ~StyleAtom();
};
#endif

/// <https://www.w3.org/TR/css-values-4/#dashed-idents>
/// This is simply an Atom, but will only parse if the identifier starts with "--".
using StyleDashedIdent = StyleAtom;

/// The cascade level these rules are relevant at, as per[1][2][3].
///
/// We store them as a bitfield with:
///
///  * Shadow cascade order (28 bits). See ShadowCascadeOrder for details.
///  * Importance bit. Whether the declaration was !important or not.
///  * The CascadeOrigin of the declaration as per [1].
///
/// Presentational hints for SVG and HTML are in the "author-level zero-specificity" level, that
/// is, right after user rules, and before author rules.
///
/// See also [4] for the Shadow DOM bits. We rely on the invariant that rules
/// from outside the tree the element is in can't affect the element.
///
/// The opposite is not true (i.e., :host and ::slotted) from an "inner" shadow tree may affect an
/// element connected to the document or an "outer" shadow tree.
///
/// [1]: https://drafts.csswg.org/css-cascade/#cascade-origin
/// [2]: https://drafts.csswg.org/css-cascade/#preshint
/// [3]: https://html.spec.whatwg.org/multipage/#presentational-hints
/// [4]: https://drafts.csswg.org/css-scoping/#shadow-cascading
struct StyleCascadeLevel {
  uint32_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleCascadeLevel operator~() const {
    return StyleCascadeLevel { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleCascadeLevel operator|(const StyleCascadeLevel& other) const {
    return StyleCascadeLevel { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleCascadeLevel& operator|=(const StyleCascadeLevel& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleCascadeLevel operator&(const StyleCascadeLevel& other) const {
    return StyleCascadeLevel { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleCascadeLevel& operator&=(const StyleCascadeLevel& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleCascadeLevel operator^(const StyleCascadeLevel& other) const {
    return StyleCascadeLevel { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleCascadeLevel& operator^=(const StyleCascadeLevel& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleCascadeLevel& other) const {
    return _0 == other._0;
  }
  inline static StyleCascadeLevel Default() {
    return SAME_TREE_AUTHOR_NORMAL;
  }
  inline int32_t ShadowCascadeOrder() const {
    bool neg(*this & CASCADE_ORDER_SIGN);
    int32_t abs = (*this & CASCADE_ORDER_BITS)._0 >> CASCADE_ORDER_SHIFT;
    return neg ? -abs : abs;
  }
  static const StyleCascadeLevel ORIGIN_BITS;
  static const StyleCascadeLevel IMPORTANT;
  static const StyleCascadeLevel CASCADE_ORDER_BITS;
  static const StyleCascadeLevel CASCADE_ORDER_SIGN;
  static const size_t CASCADE_ORDER_SHIFT;
  static const StyleCascadeLevel SAME_TREE_AUTHOR_NORMAL;
};
/// The three bits that represent the CascadeOrigin.
constexpr inline const StyleCascadeLevel StyleCascadeLevel::ORIGIN_BITS = StyleCascadeLevel{
  /* ._0 = */ (uint32_t)7
};
/// Whether the declarations are `!important` or not.
constexpr inline const StyleCascadeLevel StyleCascadeLevel::IMPORTANT = StyleCascadeLevel{
  /* ._0 = */ (uint32_t)(1 << 3)
};
/// The 27 bits for cascade order absolute value. If you change this, please change
/// CASCADE_ORDER_SHIFT accordingly.
constexpr inline const StyleCascadeLevel StyleCascadeLevel::CASCADE_ORDER_BITS = StyleCascadeLevel{
  /* ._0 = */ (uint32_t)2147483632
};
/// The bit for the sign.
constexpr inline const StyleCascadeLevel StyleCascadeLevel::CASCADE_ORDER_SIGN = StyleCascadeLevel{
  /* ._0 = */ (uint32_t)(1 << 31)
};
/// The shift that we apply to the cascade order.
constexpr inline const size_t StyleCascadeLevel::CASCADE_ORDER_SHIFT = 4;
/// The author level at the same tree. Here for convenience to avoid duplicating it from C++.
constexpr inline const StyleCascadeLevel StyleCascadeLevel::SAME_TREE_AUTHOR_NORMAL = StyleCascadeLevel{
  /* ._0 = */ (uint32_t)StyleCascadeOrigin::Author
};

/// A generic type for representing a value scoped to a specific cascade level
/// in the shadow tree hierarchy.
template<typename T>
struct StyleTreeScoped {
  /// The scoped value.
  T value;
  /// The cascade level in the shadow tree hierarchy.
  StyleCascadeLevel scope;

  bool operator==(const StyleTreeScoped& other) const {
    return value == other.value &&
           scope == other.scope;
  }
  inline StyleTreeScoped()
    : value(T()),
      scope(StyleCascadeLevel::Default())
  {}
  inline explicit StyleTreeScoped(T&& aValue)
    : value(std::move(aValue)),
      scope(StyleCascadeLevel::Default())
  {}
  inline bool IsEmpty() const;
  inline Span<const mozilla::StyleAtom> AsSpan() const;
};

/// Anchor side for the anchor positioning function.
template<typename P>
struct StyleGenericAnchorSide {
  enum class Tag {
    /// A keyword value for the anchor side.
    Keyword,
    /// Percentage value between the `start` and `end` sides.
    Percentage,
  };

  struct StyleKeyword_Body {
    StyleAnchorSideKeyword _0;

    bool operator==(const StyleKeyword_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StylePercentage_Body {
    P _0;

    bool operator==(const StylePercentage_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleKeyword_Body keyword;
    StylePercentage_Body percentage;
  };

  static StyleGenericAnchorSide Keyword(const StyleAnchorSideKeyword &_0) {
    StyleGenericAnchorSide result;
    ::new (&result.keyword._0) (StyleAnchorSideKeyword)(_0);
    result.tag = Tag::Keyword;
    return result;
  }

  bool IsKeyword() const {
    return tag == Tag::Keyword;
  }

  const StyleAnchorSideKeyword& AsKeyword() const {
    MOZ_DIAGNOSTIC_ASSERT(IsKeyword());
    return keyword._0;
  }

  static StyleGenericAnchorSide Percentage(const P &_0) {
    StyleGenericAnchorSide result;
    ::new (&result.percentage._0) (P)(_0);
    result.tag = Tag::Percentage;
    return result;
  }

  bool IsPercentage() const {
    return tag == Tag::Percentage;
  }

  const P& AsPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPercentage());
    return percentage._0;
  }

  bool operator==(const StyleGenericAnchorSide& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Keyword: return keyword == other.keyword;
      case Tag::Percentage: return percentage == other.percentage;

    }
    return true;
  }

  private:
  StyleGenericAnchorSide() {

  }
  public:


  ~StyleGenericAnchorSide() {
    switch (tag) {
      case Tag::Keyword: keyword.~StyleKeyword_Body(); break;
      case Tag::Percentage: percentage.~StylePercentage_Body(); break;

    }
  }

  StyleGenericAnchorSide(const StyleGenericAnchorSide& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Keyword: ::new (&keyword) (StyleKeyword_Body)(other.keyword); break;
      case Tag::Percentage: ::new (&percentage) (StylePercentage_Body)(other.percentage); break;

    }
  }
  StyleGenericAnchorSide& operator=(const StyleGenericAnchorSide& other) {
    if (this != &other) {
      this->~StyleGenericAnchorSide();
      new (this) StyleGenericAnchorSide(other);
    }
    return *this;
  }
};

/// Anchor function used by inset properties. This resolves
/// to length at computed time.
///
/// https://drafts.csswg.org/css-anchor-position-1/#funcdef-anchor
template<typename Percentage, typename Fallback>
struct StyleGenericAnchorFunction {
  /// Anchor name of the element to anchor to.
  /// If omitted, selects the implicit anchor element.
  /// The shadow cascade order of the tree-scoped anchor name
  /// associates the name with the host of the originating stylesheet.
  StyleTreeScoped<StyleDashedIdent> target_element;
  /// Where relative to the target anchor element to position
  /// the anchored element to.
  StyleGenericAnchorSide<Percentage> side;
  /// Value to use in case the anchor function is invalid.
  StyleOptional<Fallback> fallback;

  bool operator==(const StyleGenericAnchorFunction& other) const {
    return target_element == other.target_element &&
           side == other.side &&
           fallback == other.fallback;
  }
};

/// `anchor()` function used in math functions.
template<typename L>
using StyleGenericCalcAnchorFunction = StyleGenericAnchorFunction<StyleBox<StyleGenericCalcNode<L>>, StyleBox<StyleGenericAnchorFunctionFallback<L>>>;

/// Anchor size function used by sizing, margin and inset properties.
/// This resolves to the size of the anchor at computed time.
///
/// https://drafts.csswg.org/css-anchor-position-1/#funcdef-anchor-size
template<typename Fallback>
struct StyleGenericAnchorSizeFunction {
  /// Anchor name of the element to anchor to.
  /// If omitted (i.e. empty), selects the implicit anchor element.
  StyleTreeScoped<StyleDashedIdent> target_element;
  /// Size of the positioned element, expressed in that of the anchor element.
  /// If omitted, defaults to the axis of the property the function is used in.
  StyleAnchorSizeKeyword size;
  /// Value to use in case the anchor function is invalid.
  StyleOptional<Fallback> fallback;

  bool operator==(const StyleGenericAnchorSizeFunction& other) const {
    return target_element == other.target_element &&
           size == other.size &&
           fallback == other.fallback;
  }
};

/// `anchor-size()` function used in math functions.
template<typename L>
using StyleGenericCalcAnchorSizeFunction = StyleGenericAnchorSizeFunction<StyleBox<StyleGenericAnchorFunctionFallback<L>>>;

/// A generic node in a calc expression.
///
/// FIXME: This would be much more elegant if we used `Self` in the types below,
/// but we can't because of https://github.com/serde-rs/serde/issues/1565.
///
/// FIXME: The following annotations are to workaround an LLVM inlining bug, see
/// bug 1631929.
///
template<typename L>
union StyleGenericCalcNode {
  enum class Tag : uint8_t {
    /// A leaf node.
    Leaf,
    /// A node that negates its child, e.g. Negate(1) == -1.
    Negate,
    /// A node that inverts its child, e.g. Invert(10) == 1 / 10 == 0.1. The child must always
    /// resolve to a number unit.
    Invert,
    /// A sum node, representing `a + b + c` where a, b, and c are the
    /// arguments.
    Sum,
    /// A product node, representing `a * b * c` where a, b, and c are the
    /// arguments.
    Product,
    /// A `min` or `max` function.
    MinMax,
    /// A `clamp()` function.
    Clamp,
    /// A `round()` function.
    Round,
    /// A `mod()` or `rem()` function.
    ModRem,
    /// A `sin()` function.
    Sin,
    /// A `cos()` function.
    Cos,
    /// A `tan()` function.
    Tan,
    /// An `asin()` function.
    Asin,
    /// An `acos()` function.
    Acos,
    /// An `atan()` function.
    Atan,
    /// An `atan2()` function.
    Atan2,
    /// A `pow()` function.
    Pow,
    /// A `sqrt()` function.
    Sqrt,
    /// A `hypot()` function
    Hypot,
    /// A `log()` function.
    Log,
    /// An `exp()` function.
    Exp,
    /// An `abs()` function.
    Abs,
    /// A `sign()` function.
    Sign,
    /// A `progress()` function.
    Progress,
    /// A `random()` function.
    Random,
    /// An `anchor()` function.
    Anchor,
    /// An `anchor-size()` function.
    AnchorSize,
  };

  struct Leaf_Body {
    Tag tag;
    L _0;

    bool operator==(const Leaf_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Negate_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;

    bool operator==(const Negate_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Invert_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;

    bool operator==(const Invert_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Sum_Body {
    Tag tag;
    StyleOwnedSlice<StyleGenericCalcNode> _0;

    bool operator==(const Sum_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Product_Body {
    Tag tag;
    StyleOwnedSlice<StyleGenericCalcNode> _0;

    bool operator==(const Product_Body& other) const {
      return _0 == other._0;
    }
  };

  struct MinMax_Body {
    Tag tag;
    StyleOwnedSlice<StyleGenericCalcNode> _0;
    StyleMinMaxOp _1;

    bool operator==(const MinMax_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct Clamp_Body {
    Tag tag;
    /// The minimum value.
    StyleBox<StyleGenericCalcNode> min;
    /// The central value.
    StyleBox<StyleGenericCalcNode> center;
    /// The maximum value.
    StyleBox<StyleGenericCalcNode> max;

    bool operator==(const Clamp_Body& other) const {
      return min == other.min &&
             center == other.center &&
             max == other.max;
    }
  };

  struct Round_Body {
    Tag tag;
    /// The rounding strategy.
    StyleRoundingStrategy strategy;
    /// The value to round.
    StyleBox<StyleGenericCalcNode> value;
    /// The step value.
    StyleBox<StyleGenericCalcNode> step;

    bool operator==(const Round_Body& other) const {
      return strategy == other.strategy &&
             value == other.value &&
             step == other.step;
    }
  };

  struct ModRem_Body {
    Tag tag;
    /// The dividend calculation.
    StyleBox<StyleGenericCalcNode> dividend;
    /// The divisor calculation.
    StyleBox<StyleGenericCalcNode> divisor;
    /// Is the function mod or rem?
    StyleModRemOp op;

    bool operator==(const ModRem_Body& other) const {
      return dividend == other.dividend &&
             divisor == other.divisor &&
             op == other.op;
    }
  };

  struct Sin_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;

    bool operator==(const Sin_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Cos_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;

    bool operator==(const Cos_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Tan_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;

    bool operator==(const Tan_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Asin_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;

    bool operator==(const Asin_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Acos_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;

    bool operator==(const Acos_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Atan_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;

    bool operator==(const Atan_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Atan2_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;
    StyleBox<StyleGenericCalcNode> _1;

    bool operator==(const Atan2_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct Pow_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;
    StyleBox<StyleGenericCalcNode> _1;

    bool operator==(const Pow_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct Sqrt_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;

    bool operator==(const Sqrt_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Hypot_Body {
    Tag tag;
    StyleOwnedSlice<StyleGenericCalcNode> _0;

    bool operator==(const Hypot_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Log_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;
    StyleOptional<StyleBox<StyleGenericCalcNode>> _1;

    bool operator==(const Log_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct Exp_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;

    bool operator==(const Exp_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Abs_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;

    bool operator==(const Abs_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Sign_Body {
    Tag tag;
    StyleBox<StyleGenericCalcNode> _0;

    bool operator==(const Sign_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Progress_Body {
    Tag tag;
    /// Clamping mode for the result.
    StyleProgressClampingMode clamping_mode;
    /// The progress value calculation.
    StyleBox<StyleGenericCalcNode> value;
    /// The progress start calculation.
    StyleBox<StyleGenericCalcNode> start;
    /// The progress end calculation.
    StyleBox<StyleGenericCalcNode> end;

    bool operator==(const Progress_Body& other) const {
      return clamping_mode == other.clamping_mode &&
             value == other.value &&
             start == other.start &&
             end == other.end;
    }
  };

  struct Random_Body {
    Tag tag;
    StyleBox<StyleGenericRandomFunction<L>> _0;

    bool operator==(const Random_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Anchor_Body {
    Tag tag;
    StyleBox<StyleGenericCalcAnchorFunction<L>> _0;

    bool operator==(const Anchor_Body& other) const {
      return _0 == other._0;
    }
  };

  struct AnchorSize_Body {
    Tag tag;
    StyleBox<StyleGenericCalcAnchorSizeFunction<L>> _0;

    bool operator==(const AnchorSize_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Leaf_Body leaf;
  Negate_Body negate;
  Invert_Body invert;
  Sum_Body sum;
  Product_Body product;
  MinMax_Body min_max;
  Clamp_Body clamp;
  Round_Body round;
  ModRem_Body mod_rem;
  Sin_Body sin;
  Cos_Body cos;
  Tan_Body tan;
  Asin_Body asin;
  Acos_Body acos;
  Atan_Body atan;
  Atan2_Body atan2;
  Pow_Body pow;
  Sqrt_Body sqrt;
  Hypot_Body hypot;
  Log_Body log;
  Exp_Body exp;
  Abs_Body abs;
  Sign_Body sign;
  Progress_Body progress;
  Random_Body random;
  Anchor_Body anchor;
  AnchorSize_Body anchor_size;

  static StyleGenericCalcNode Leaf(const L &_0) {
    StyleGenericCalcNode result;
    ::new (&result.leaf._0) (L)(_0);
    result.tag = Tag::Leaf;
    return result;
  }

  bool IsLeaf() const {
    return tag == Tag::Leaf;
  }

  const L& AsLeaf() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLeaf());
    return leaf._0;
  }

  static StyleGenericCalcNode Negate(const StyleBox<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.negate._0) (StyleBox<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Negate;
    return result;
  }

  bool IsNegate() const {
    return tag == Tag::Negate;
  }

  const StyleBox<StyleGenericCalcNode>& AsNegate() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNegate());
    return negate._0;
  }

  static StyleGenericCalcNode Invert(const StyleBox<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.invert._0) (StyleBox<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Invert;
    return result;
  }

  bool IsInvert() const {
    return tag == Tag::Invert;
  }

  const StyleBox<StyleGenericCalcNode>& AsInvert() const {
    MOZ_DIAGNOSTIC_ASSERT(IsInvert());
    return invert._0;
  }

  static StyleGenericCalcNode Sum(const StyleOwnedSlice<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.sum._0) (StyleOwnedSlice<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Sum;
    return result;
  }

  bool IsSum() const {
    return tag == Tag::Sum;
  }

  const StyleOwnedSlice<StyleGenericCalcNode>& AsSum() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSum());
    return sum._0;
  }

  static StyleGenericCalcNode Product(const StyleOwnedSlice<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.product._0) (StyleOwnedSlice<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Product;
    return result;
  }

  bool IsProduct() const {
    return tag == Tag::Product;
  }

  const StyleOwnedSlice<StyleGenericCalcNode>& AsProduct() const {
    MOZ_DIAGNOSTIC_ASSERT(IsProduct());
    return product._0;
  }

  static StyleGenericCalcNode MinMax(const StyleOwnedSlice<StyleGenericCalcNode> &_0,
                                     const StyleMinMaxOp &_1) {
    StyleGenericCalcNode result;
    ::new (&result.min_max._0) (StyleOwnedSlice<StyleGenericCalcNode>)(_0);
    ::new (&result.min_max._1) (StyleMinMaxOp)(_1);
    result.tag = Tag::MinMax;
    return result;
  }

  bool IsMinMax() const {
    return tag == Tag::MinMax;
  }

  const MinMax_Body& AsMinMax() const {
    MOZ_DIAGNOSTIC_ASSERT(IsMinMax());
    return min_max;
  }

  static StyleGenericCalcNode Clamp(const StyleBox<StyleGenericCalcNode> &min,
                                    const StyleBox<StyleGenericCalcNode> &center,
                                    const StyleBox<StyleGenericCalcNode> &max) {
    StyleGenericCalcNode result;
    ::new (&result.clamp.min) (StyleBox<StyleGenericCalcNode>)(min);
    ::new (&result.clamp.center) (StyleBox<StyleGenericCalcNode>)(center);
    ::new (&result.clamp.max) (StyleBox<StyleGenericCalcNode>)(max);
    result.tag = Tag::Clamp;
    return result;
  }

  bool IsClamp() const {
    return tag == Tag::Clamp;
  }

  const Clamp_Body& AsClamp() const {
    MOZ_DIAGNOSTIC_ASSERT(IsClamp());
    return clamp;
  }

  static StyleGenericCalcNode Round(const StyleRoundingStrategy &strategy,
                                    const StyleBox<StyleGenericCalcNode> &value,
                                    const StyleBox<StyleGenericCalcNode> &step) {
    StyleGenericCalcNode result;
    ::new (&result.round.strategy) (StyleRoundingStrategy)(strategy);
    ::new (&result.round.value) (StyleBox<StyleGenericCalcNode>)(value);
    ::new (&result.round.step) (StyleBox<StyleGenericCalcNode>)(step);
    result.tag = Tag::Round;
    return result;
  }

  bool IsRound() const {
    return tag == Tag::Round;
  }

  const Round_Body& AsRound() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRound());
    return round;
  }

  static StyleGenericCalcNode ModRem(const StyleBox<StyleGenericCalcNode> &dividend,
                                     const StyleBox<StyleGenericCalcNode> &divisor,
                                     const StyleModRemOp &op) {
    StyleGenericCalcNode result;
    ::new (&result.mod_rem.dividend) (StyleBox<StyleGenericCalcNode>)(dividend);
    ::new (&result.mod_rem.divisor) (StyleBox<StyleGenericCalcNode>)(divisor);
    ::new (&result.mod_rem.op) (StyleModRemOp)(op);
    result.tag = Tag::ModRem;
    return result;
  }

  bool IsModRem() const {
    return tag == Tag::ModRem;
  }

  const ModRem_Body& AsModRem() const {
    MOZ_DIAGNOSTIC_ASSERT(IsModRem());
    return mod_rem;
  }

  static StyleGenericCalcNode Sin(const StyleBox<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.sin._0) (StyleBox<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Sin;
    return result;
  }

  bool IsSin() const {
    return tag == Tag::Sin;
  }

  const StyleBox<StyleGenericCalcNode>& AsSin() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSin());
    return sin._0;
  }

  static StyleGenericCalcNode Cos(const StyleBox<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.cos._0) (StyleBox<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Cos;
    return result;
  }

  bool IsCos() const {
    return tag == Tag::Cos;
  }

  const StyleBox<StyleGenericCalcNode>& AsCos() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCos());
    return cos._0;
  }

  static StyleGenericCalcNode Tan(const StyleBox<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.tan._0) (StyleBox<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Tan;
    return result;
  }

  bool IsTan() const {
    return tag == Tag::Tan;
  }

  const StyleBox<StyleGenericCalcNode>& AsTan() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTan());
    return tan._0;
  }

  static StyleGenericCalcNode Asin(const StyleBox<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.asin._0) (StyleBox<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Asin;
    return result;
  }

  bool IsAsin() const {
    return tag == Tag::Asin;
  }

  const StyleBox<StyleGenericCalcNode>& AsAsin() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAsin());
    return asin._0;
  }

  static StyleGenericCalcNode Acos(const StyleBox<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.acos._0) (StyleBox<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Acos;
    return result;
  }

  bool IsAcos() const {
    return tag == Tag::Acos;
  }

  const StyleBox<StyleGenericCalcNode>& AsAcos() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAcos());
    return acos._0;
  }

  static StyleGenericCalcNode Atan(const StyleBox<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.atan._0) (StyleBox<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Atan;
    return result;
  }

  bool IsAtan() const {
    return tag == Tag::Atan;
  }

  const StyleBox<StyleGenericCalcNode>& AsAtan() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAtan());
    return atan._0;
  }

  static StyleGenericCalcNode Atan2(const StyleBox<StyleGenericCalcNode> &_0,
                                    const StyleBox<StyleGenericCalcNode> &_1) {
    StyleGenericCalcNode result;
    ::new (&result.atan2._0) (StyleBox<StyleGenericCalcNode>)(_0);
    ::new (&result.atan2._1) (StyleBox<StyleGenericCalcNode>)(_1);
    result.tag = Tag::Atan2;
    return result;
  }

  bool IsAtan2() const {
    return tag == Tag::Atan2;
  }

  const Atan2_Body& AsAtan2() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAtan2());
    return atan2;
  }

  static StyleGenericCalcNode Pow(const StyleBox<StyleGenericCalcNode> &_0,
                                  const StyleBox<StyleGenericCalcNode> &_1) {
    StyleGenericCalcNode result;
    ::new (&result.pow._0) (StyleBox<StyleGenericCalcNode>)(_0);
    ::new (&result.pow._1) (StyleBox<StyleGenericCalcNode>)(_1);
    result.tag = Tag::Pow;
    return result;
  }

  bool IsPow() const {
    return tag == Tag::Pow;
  }

  const Pow_Body& AsPow() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPow());
    return pow;
  }

  static StyleGenericCalcNode Sqrt(const StyleBox<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.sqrt._0) (StyleBox<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Sqrt;
    return result;
  }

  bool IsSqrt() const {
    return tag == Tag::Sqrt;
  }

  const StyleBox<StyleGenericCalcNode>& AsSqrt() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSqrt());
    return sqrt._0;
  }

  static StyleGenericCalcNode Hypot(const StyleOwnedSlice<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.hypot._0) (StyleOwnedSlice<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Hypot;
    return result;
  }

  bool IsHypot() const {
    return tag == Tag::Hypot;
  }

  const StyleOwnedSlice<StyleGenericCalcNode>& AsHypot() const {
    MOZ_DIAGNOSTIC_ASSERT(IsHypot());
    return hypot._0;
  }

  static StyleGenericCalcNode Log(const StyleBox<StyleGenericCalcNode> &_0,
                                  const StyleOptional<StyleBox<StyleGenericCalcNode>> &_1) {
    StyleGenericCalcNode result;
    ::new (&result.log._0) (StyleBox<StyleGenericCalcNode>)(_0);
    ::new (&result.log._1) (StyleOptional<StyleBox<StyleGenericCalcNode>>)(_1);
    result.tag = Tag::Log;
    return result;
  }

  bool IsLog() const {
    return tag == Tag::Log;
  }

  const Log_Body& AsLog() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLog());
    return log;
  }

  static StyleGenericCalcNode Exp(const StyleBox<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.exp._0) (StyleBox<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Exp;
    return result;
  }

  bool IsExp() const {
    return tag == Tag::Exp;
  }

  const StyleBox<StyleGenericCalcNode>& AsExp() const {
    MOZ_DIAGNOSTIC_ASSERT(IsExp());
    return exp._0;
  }

  static StyleGenericCalcNode Abs(const StyleBox<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.abs._0) (StyleBox<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Abs;
    return result;
  }

  bool IsAbs() const {
    return tag == Tag::Abs;
  }

  const StyleBox<StyleGenericCalcNode>& AsAbs() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAbs());
    return abs._0;
  }

  static StyleGenericCalcNode Sign(const StyleBox<StyleGenericCalcNode> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.sign._0) (StyleBox<StyleGenericCalcNode>)(_0);
    result.tag = Tag::Sign;
    return result;
  }

  bool IsSign() const {
    return tag == Tag::Sign;
  }

  const StyleBox<StyleGenericCalcNode>& AsSign() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSign());
    return sign._0;
  }

  static StyleGenericCalcNode Progress(const StyleProgressClampingMode &clamping_mode,
                                       const StyleBox<StyleGenericCalcNode> &value,
                                       const StyleBox<StyleGenericCalcNode> &start,
                                       const StyleBox<StyleGenericCalcNode> &end) {
    StyleGenericCalcNode result;
    ::new (&result.progress.clamping_mode) (StyleProgressClampingMode)(clamping_mode);
    ::new (&result.progress.value) (StyleBox<StyleGenericCalcNode>)(value);
    ::new (&result.progress.start) (StyleBox<StyleGenericCalcNode>)(start);
    ::new (&result.progress.end) (StyleBox<StyleGenericCalcNode>)(end);
    result.tag = Tag::Progress;
    return result;
  }

  bool IsProgress() const {
    return tag == Tag::Progress;
  }

  const Progress_Body& AsProgress() const {
    MOZ_DIAGNOSTIC_ASSERT(IsProgress());
    return progress;
  }

  static StyleGenericCalcNode Random(const StyleBox<StyleGenericRandomFunction<L>> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.random._0) (StyleBox<StyleGenericRandomFunction<L>>)(_0);
    result.tag = Tag::Random;
    return result;
  }

  bool IsRandom() const {
    return tag == Tag::Random;
  }

  const StyleBox<StyleGenericRandomFunction<L>>& AsRandom() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRandom());
    return random._0;
  }

  static StyleGenericCalcNode Anchor(const StyleBox<StyleGenericCalcAnchorFunction<L>> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.anchor._0) (StyleBox<StyleGenericCalcAnchorFunction<L>>)(_0);
    result.tag = Tag::Anchor;
    return result;
  }

  bool IsAnchor() const {
    return tag == Tag::Anchor;
  }

  const StyleBox<StyleGenericCalcAnchorFunction<L>>& AsAnchor() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAnchor());
    return anchor._0;
  }

  static StyleGenericCalcNode AnchorSize(const StyleBox<StyleGenericCalcAnchorSizeFunction<L>> &_0) {
    StyleGenericCalcNode result;
    ::new (&result.anchor_size._0) (StyleBox<StyleGenericCalcAnchorSizeFunction<L>>)(_0);
    result.tag = Tag::AnchorSize;
    return result;
  }

  bool IsAnchorSize() const {
    return tag == Tag::AnchorSize;
  }

  const StyleBox<StyleGenericCalcAnchorSizeFunction<L>>& AsAnchorSize() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAnchorSize());
    return anchor_size._0;
  }

  MOZ_NEVER_INLINE bool operator==(const StyleGenericCalcNode& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Leaf: return leaf == other.leaf;
      case Tag::Negate: return negate == other.negate;
      case Tag::Invert: return invert == other.invert;
      case Tag::Sum: return sum == other.sum;
      case Tag::Product: return product == other.product;
      case Tag::MinMax: return min_max == other.min_max;
      case Tag::Clamp: return clamp == other.clamp;
      case Tag::Round: return round == other.round;
      case Tag::ModRem: return mod_rem == other.mod_rem;
      case Tag::Sin: return sin == other.sin;
      case Tag::Cos: return cos == other.cos;
      case Tag::Tan: return tan == other.tan;
      case Tag::Asin: return asin == other.asin;
      case Tag::Acos: return acos == other.acos;
      case Tag::Atan: return atan == other.atan;
      case Tag::Atan2: return atan2 == other.atan2;
      case Tag::Pow: return pow == other.pow;
      case Tag::Sqrt: return sqrt == other.sqrt;
      case Tag::Hypot: return hypot == other.hypot;
      case Tag::Log: return log == other.log;
      case Tag::Exp: return exp == other.exp;
      case Tag::Abs: return abs == other.abs;
      case Tag::Sign: return sign == other.sign;
      case Tag::Progress: return progress == other.progress;
      case Tag::Random: return random == other.random;
      case Tag::Anchor: return anchor == other.anchor;
      case Tag::AnchorSize: return anchor_size == other.anchor_size;

    }
    return true;
  }

  private:
  StyleGenericCalcNode() {

  }
  public:


  MOZ_NEVER_INLINE ~StyleGenericCalcNode() {
    switch (tag) {
      case Tag::Leaf: leaf.~Leaf_Body(); break;
      case Tag::Negate: negate.~Negate_Body(); break;
      case Tag::Invert: invert.~Invert_Body(); break;
      case Tag::Sum: sum.~Sum_Body(); break;
      case Tag::Product: product.~Product_Body(); break;
      case Tag::MinMax: min_max.~MinMax_Body(); break;
      case Tag::Clamp: clamp.~Clamp_Body(); break;
      case Tag::Round: round.~Round_Body(); break;
      case Tag::ModRem: mod_rem.~ModRem_Body(); break;
      case Tag::Sin: sin.~Sin_Body(); break;
      case Tag::Cos: cos.~Cos_Body(); break;
      case Tag::Tan: tan.~Tan_Body(); break;
      case Tag::Asin: asin.~Asin_Body(); break;
      case Tag::Acos: acos.~Acos_Body(); break;
      case Tag::Atan: atan.~Atan_Body(); break;
      case Tag::Atan2: atan2.~Atan2_Body(); break;
      case Tag::Pow: pow.~Pow_Body(); break;
      case Tag::Sqrt: sqrt.~Sqrt_Body(); break;
      case Tag::Hypot: hypot.~Hypot_Body(); break;
      case Tag::Log: log.~Log_Body(); break;
      case Tag::Exp: exp.~Exp_Body(); break;
      case Tag::Abs: abs.~Abs_Body(); break;
      case Tag::Sign: sign.~Sign_Body(); break;
      case Tag::Progress: progress.~Progress_Body(); break;
      case Tag::Random: random.~Random_Body(); break;
      case Tag::Anchor: anchor.~Anchor_Body(); break;
      case Tag::AnchorSize: anchor_size.~AnchorSize_Body(); break;

    }
  }

  MOZ_NEVER_INLINE StyleGenericCalcNode(const StyleGenericCalcNode& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Leaf: ::new (&leaf) (Leaf_Body)(other.leaf); break;
      case Tag::Negate: ::new (&negate) (Negate_Body)(other.negate); break;
      case Tag::Invert: ::new (&invert) (Invert_Body)(other.invert); break;
      case Tag::Sum: ::new (&sum) (Sum_Body)(other.sum); break;
      case Tag::Product: ::new (&product) (Product_Body)(other.product); break;
      case Tag::MinMax: ::new (&min_max) (MinMax_Body)(other.min_max); break;
      case Tag::Clamp: ::new (&clamp) (Clamp_Body)(other.clamp); break;
      case Tag::Round: ::new (&round) (Round_Body)(other.round); break;
      case Tag::ModRem: ::new (&mod_rem) (ModRem_Body)(other.mod_rem); break;
      case Tag::Sin: ::new (&sin) (Sin_Body)(other.sin); break;
      case Tag::Cos: ::new (&cos) (Cos_Body)(other.cos); break;
      case Tag::Tan: ::new (&tan) (Tan_Body)(other.tan); break;
      case Tag::Asin: ::new (&asin) (Asin_Body)(other.asin); break;
      case Tag::Acos: ::new (&acos) (Acos_Body)(other.acos); break;
      case Tag::Atan: ::new (&atan) (Atan_Body)(other.atan); break;
      case Tag::Atan2: ::new (&atan2) (Atan2_Body)(other.atan2); break;
      case Tag::Pow: ::new (&pow) (Pow_Body)(other.pow); break;
      case Tag::Sqrt: ::new (&sqrt) (Sqrt_Body)(other.sqrt); break;
      case Tag::Hypot: ::new (&hypot) (Hypot_Body)(other.hypot); break;
      case Tag::Log: ::new (&log) (Log_Body)(other.log); break;
      case Tag::Exp: ::new (&exp) (Exp_Body)(other.exp); break;
      case Tag::Abs: ::new (&abs) (Abs_Body)(other.abs); break;
      case Tag::Sign: ::new (&sign) (Sign_Body)(other.sign); break;
      case Tag::Progress: ::new (&progress) (Progress_Body)(other.progress); break;
      case Tag::Random: ::new (&random) (Random_Body)(other.random); break;
      case Tag::Anchor: ::new (&anchor) (Anchor_Body)(other.anchor); break;
      case Tag::AnchorSize: ::new (&anchor_size) (AnchorSize_Body)(other.anchor_size); break;

    }
  }
  StyleGenericCalcNode& operator=(const StyleGenericCalcNode& other) {
    if (this != &other) {
      this->~StyleGenericCalcNode();
      new (this) StyleGenericCalcNode(other);
    }
    return *this;
  }
  void ScaleLengthsBy(float);
};

/// The computed version of a calc() node for `<length-percentage>` values.
using StyleCalcNode = StyleGenericCalcNode<StyleComputedLeaf>;

/// The representation of a calc() function with mixed lengths and percentages.
struct StyleCalcLengthPercentage {
  StyleAllowedNumericType clamping_mode;
  StyleCalcNode node;

  bool operator==(const StyleCalcLengthPercentage& other) const {
    return clamping_mode == other.clamping_mode &&
           node == other.node;
  }
  inline CSSCoord ResolveToCSSPixels(CSSCoord aBasis) const;
  template<typename Rounder>
  inline nscoord Resolve(nscoord aBasis, Rounder) const;
};

template<typename T, typename N>
struct StyleInlineVariant {
  uint8_t tag;
  T numeric_tag;
  N value;

  bool operator==(const StyleInlineVariant& other) const {
    return tag == other.tag &&
           numeric_tag == other.numeric_tag &&
           value == other.value;
  }
};

#if defined(SERVO_32_BITS)
template<typename B>
struct StyleBoxedVariant {
  uint8_t tag;
  B *ptr;

  bool operator==(const StyleBoxedVariant& other) const {
    return tag == other.tag &&
           ptr == other.ptr;
  }
};
#endif

#if defined(HAVE_64BIT_BUILD)
template<typename B>
struct StyleBoxedVariant {
  size_t ptr;

  bool operator==(const StyleBoxedVariant& other) const {
    return ptr == other.ptr;
  }
};
#endif

struct StyleTagVariant {
  uint8_t tag;

  bool operator==(const StyleTagVariant& other) const {
    return tag == other.tag;
  }
};

template<typename T, typename N, typename B>
union StyleNumericUnionImpl {
  StyleInlineVariant<T, N> inl;
  StyleBoxedVariant<B> boxed;
  StyleTagVariant tag;
};

template<typename T, typename N, typename B>
struct StyleNumericUnion {
  StyleNumericUnionImpl<T, N, B> _0;
};

/// A `<length-percentage>` value. This can be either a `<length>`, a
/// `<percentage>`, or a combination of both via `calc()`.
///
/// https://drafts.csswg.org/css-values-4/#typedef-length-percentage
///
struct StyleLengthPercentage {
  StyleNumericUnion<StyleLengthPercentageTag, float, StyleCalcLengthPercentage> _0;
  using Self = StyleLengthPercentage;

  // We need to do all this manually because cbindgen can't reason about unions.
  inline StyleLengthPercentage();
  inline StyleLengthPercentage(const Self&);
  inline ~StyleLengthPercentage();
  inline Self& operator=(const Self&);

  inline bool operator==(const Self& aOther) const;

  inline bool IsLengthOrPercentage() const;
  inline bool IsLength() const;
  inline bool IsPercentage() const;
  inline bool IsCalc() const;

  inline const StyleLength& AsLength() const;
  inline StyleLength& AsLength();

  inline const StylePercentage& AsPercentage() const;
  inline StylePercentage& AsPercentage();

  inline const StyleCalcLengthPercentage& AsCalc() const;
  inline StyleCalcLengthPercentage& AsCalc();

  static inline Self Zero();
  static inline Self FromAppUnits(nscoord);
  static inline Self FromPixels(CSSCoord);
  static inline Self FromPercentage(float);

  inline void ScaleLengthsBy(float);
  inline bool HasPercent() const;
  inline bool ConvertsToLength() const;
  inline nscoord ToLength() const;
  inline CSSCoord ToLengthInCSSPixels() const;
  inline bool ConvertsToPercentage() const;
  inline bool HasLengthAndPercentage() const;
  inline float ToPercentage() const;
  inline bool IsDefinitelyZero() const;
  inline CSSCoord ResolveToCSSPixels(CSSCoord aPercentageBasisInCSSPixels) const;
  template<typename T> inline CSSCoord ResolveToCSSPixelsWith(T aPercentageGetter) const;
  template<typename T, typename Rounder>
  inline nscoord Resolve(T aPercentageGetter, Rounder) const;
  template<typename Rounder>
  inline nscoord Resolve(nscoord aPercentageBasis, Rounder) const;
  template<typename T> inline nscoord Resolve(T aPercentageGetter) const;
  inline nscoord Resolve(nscoord aPercentageBasis) const;
};

/// A value of the `translate` property
///
/// https://drafts.csswg.org/css-transforms-2/#individual-transform-serialization:
///
/// If a 2d translation is specified, the property must serialize with only one
/// or two values (per usual, if the second value is 0px, the default, it must
/// be omitted when serializing; however if 0% is the second value, it is included).
///
/// If a 3d translation is specified and the value can be expressed as 2d, we treat as 2d and
/// serialize accoringly. Otherwise, we serialize all three values.
/// https://github.com/w3c/csswg-drafts/issues/3305
///
/// <https://drafts.csswg.org/css-transforms-2/#individual-transforms>
template<typename LengthPercentage, typename Length>
struct StyleGenericTranslate {
  enum class Tag : uint8_t {
    /// 'none'
    None,
    /// <length-percentage> [ <length-percentage> <length>? ]?
    Translate,
  };

  struct StyleTranslate_Body {
    LengthPercentage _0;
    LengthPercentage _1;
    Length _2;

    bool operator==(const StyleTranslate_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2;
    }
  };

  Tag tag;
  union {
    StyleTranslate_Body translate;
  };

  static StyleGenericTranslate None() {
    StyleGenericTranslate result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericTranslate Translate(const LengthPercentage &_0,
                                         const LengthPercentage &_1,
                                         const Length &_2) {
    StyleGenericTranslate result;
    ::new (&result.translate._0) (LengthPercentage)(_0);
    ::new (&result.translate._1) (LengthPercentage)(_1);
    ::new (&result.translate._2) (Length)(_2);
    result.tag = Tag::Translate;
    return result;
  }

  bool IsTranslate() const {
    return tag == Tag::Translate;
  }

  const StyleTranslate_Body& AsTranslate() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTranslate());
    return translate;
  }

  bool operator==(const StyleGenericTranslate& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Translate: return translate == other.translate;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericTranslate() {

  }
  public:


  ~StyleGenericTranslate() {
    switch (tag) {
      case Tag::Translate: translate.~StyleTranslate_Body(); break;
      default: break;
    }
  }

  StyleGenericTranslate(const StyleGenericTranslate& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Translate: ::new (&translate) (StyleTranslate_Body)(other.translate); break;
      default: break;
    }
  }
  StyleGenericTranslate& operator=(const StyleGenericTranslate& other) {
    if (this != &other) {
      this->~StyleGenericTranslate();
      new (this) StyleGenericTranslate(other);
    }
    return *this;
  }
};

/// A computed CSS `translate`
using StyleTranslate = StyleGenericTranslate<StyleLengthPercentage, StyleLength>;

/// A value of the `Rotate` property
///
/// <https://drafts.csswg.org/css-transforms-2/#individual-transforms>
template<typename Number, typename Angle>
struct StyleGenericRotate {
  enum class Tag : uint8_t {
    /// 'none'
    None,
    /// '<angle>'
    Rotate,
    /// '<number>{3} <angle>'
    Rotate3D,
  };

  struct StyleRotate_Body {
    Angle _0;

    bool operator==(const StyleRotate_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleRotate3D_Body {
    Number _0;
    Number _1;
    Number _2;
    Angle _3;

    bool operator==(const StyleRotate3D_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2 &&
             _3 == other._3;
    }
  };

  Tag tag;
  union {
    StyleRotate_Body rotate;
    StyleRotate3D_Body rotate3_d;
  };

  static StyleGenericRotate None() {
    StyleGenericRotate result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericRotate Rotate(const Angle &_0) {
    StyleGenericRotate result;
    ::new (&result.rotate._0) (Angle)(_0);
    result.tag = Tag::Rotate;
    return result;
  }

  bool IsRotate() const {
    return tag == Tag::Rotate;
  }

  const Angle& AsRotate() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRotate());
    return rotate._0;
  }

  static StyleGenericRotate Rotate3D(const Number &_0,
                                     const Number &_1,
                                     const Number &_2,
                                     const Angle &_3) {
    StyleGenericRotate result;
    ::new (&result.rotate3_d._0) (Number)(_0);
    ::new (&result.rotate3_d._1) (Number)(_1);
    ::new (&result.rotate3_d._2) (Number)(_2);
    ::new (&result.rotate3_d._3) (Angle)(_3);
    result.tag = Tag::Rotate3D;
    return result;
  }

  bool IsRotate3D() const {
    return tag == Tag::Rotate3D;
  }

  const StyleRotate3D_Body& AsRotate3D() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRotate3D());
    return rotate3_d;
  }

  bool operator==(const StyleGenericRotate& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Rotate: return rotate == other.rotate;
      case Tag::Rotate3D: return rotate3_d == other.rotate3_d;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericRotate() {

  }
  public:


  ~StyleGenericRotate() {
    switch (tag) {
      case Tag::Rotate: rotate.~StyleRotate_Body(); break;
      case Tag::Rotate3D: rotate3_d.~StyleRotate3D_Body(); break;
      default: break;
    }
  }

  StyleGenericRotate(const StyleGenericRotate& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Rotate: ::new (&rotate) (StyleRotate_Body)(other.rotate); break;
      case Tag::Rotate3D: ::new (&rotate3_d) (StyleRotate3D_Body)(other.rotate3_d); break;
      default: break;
    }
  }
  StyleGenericRotate& operator=(const StyleGenericRotate& other) {
    if (this != &other) {
      this->~StyleGenericRotate();
      new (this) StyleGenericRotate(other);
    }
    return *this;
  }
};

/// A computed CSS `rotate`
using StyleRotate = StyleGenericRotate<StyleNumber, StyleAngle>;

/// A CSS integer value.
using StyleCSSInteger = int32_t;

/// A `<integer>` value.
using StyleInteger = StyleCSSInteger;

/// A generic 2D transformation matrix.
template<typename T>
struct StyleGenericMatrix {
  T a;
  T b;
  T c;
  T d;
  T e;
  T f;

  bool operator==(const StyleGenericMatrix& other) const {
    return a == other.a &&
           b == other.b &&
           c == other.c &&
           d == other.d &&
           e == other.e &&
           f == other.f;
  }
};

template<typename T>
struct StyleGenericMatrix3D {
  T m11;
  T m12;
  T m13;
  T m14;
  T m21;
  T m22;
  T m23;
  T m24;
  T m31;
  T m32;
  T m33;
  T m34;
  T m41;
  T m42;
  T m43;
  T m44;

  bool operator==(const StyleGenericMatrix3D& other) const {
    return m11 == other.m11 &&
           m12 == other.m12 &&
           m13 == other.m13 &&
           m14 == other.m14 &&
           m21 == other.m21 &&
           m22 == other.m22 &&
           m23 == other.m23 &&
           m24 == other.m24 &&
           m31 == other.m31 &&
           m32 == other.m32 &&
           m33 == other.m33 &&
           m34 == other.m34 &&
           m41 == other.m41 &&
           m42 == other.m42 &&
           m43 == other.m43 &&
           m44 == other.m44;
  }
};

/// A value for the `perspective()` transform function, which is either a
/// non-negative `<length>` or `none`.
template<typename L>
struct StyleGenericPerspectiveFunction {
  enum class Tag : uint8_t {
    /// `none`
    None,
    /// A `<length>`.
    Length,
  };

  struct StyleLength_Body {
    L _0;

    bool operator==(const StyleLength_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleLength_Body length;
  };

  static StyleGenericPerspectiveFunction None() {
    StyleGenericPerspectiveFunction result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericPerspectiveFunction Length(const L &_0) {
    StyleGenericPerspectiveFunction result;
    ::new (&result.length._0) (L)(_0);
    result.tag = Tag::Length;
    return result;
  }

  bool IsLength() const {
    return tag == Tag::Length;
  }

  const L& AsLength() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLength());
    return length._0;
  }

  bool operator==(const StyleGenericPerspectiveFunction& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Length: return length == other.length;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericPerspectiveFunction() {

  }
  public:


  ~StyleGenericPerspectiveFunction() {
    switch (tag) {
      case Tag::Length: length.~StyleLength_Body(); break;
      default: break;
    }
  }

  StyleGenericPerspectiveFunction(const StyleGenericPerspectiveFunction& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Length: ::new (&length) (StyleLength_Body)(other.length); break;
      default: break;
    }
  }
  StyleGenericPerspectiveFunction& operator=(const StyleGenericPerspectiveFunction& other) {
    if (this != &other) {
      this->~StyleGenericPerspectiveFunction();
      new (this) StyleGenericPerspectiveFunction(other);
    }
    return *this;
  }
};

/// A value of the `transform` property
template<typename T>
struct StyleGenericTransform {
  StyleOwnedSlice<T> _0;

  bool operator==(const StyleGenericTransform& other) const {
    return _0 == other._0;
  }
  inline Span<const T> Operations() const;
  inline bool IsNone() const;
  bool HasPercent() const;
};

/// A computed percentage.
struct StylePercentage {
  StyleCSSFloat _0;

  bool operator==(const StylePercentage& other) const {
    return _0 == other._0;
  }
};

/// A single operation in the list of a `transform` value
template<typename Angle, typename Number, typename Length, typename Integer, typename LengthPercentage>
struct StyleGenericTransformOperation {
  enum class Tag : uint8_t {
    /// Represents a 2D 2x3 matrix.
    Matrix,
    /// Represents a 3D 4x4 matrix.
    Matrix3D,
    /// A 2D skew.
    ///
    /// If the second angle is not provided it is assumed zero.
    ///
    /// Syntax can be skew(angle) or skew(angle, angle)
    Skew,
    /// skewX(angle)
    SkewX,
    /// skewY(angle)
    SkewY,
    /// translate(x, y) or translate(x)
    Translate,
    /// translateX(x)
    TranslateX,
    /// translateY(y)
    TranslateY,
    /// translateZ(z)
    TranslateZ,
    /// translate3d(x, y, z)
    Translate3D,
    /// A 2D scaling factor.
    ///
    /// Syntax can be scale(factor) or scale(factor, factor)
    Scale,
    /// scaleX(factor)
    ScaleX,
    /// scaleY(factor)
    ScaleY,
    /// scaleZ(factor)
    ScaleZ,
    /// scale3D(factorX, factorY, factorZ)
    Scale3D,
    /// Describes a 2D Rotation.
    ///
    /// In a 3D scene `rotate(angle)` is equivalent to `rotateZ(angle)`.
    Rotate,
    /// Rotation in 3D space around the x-axis.
    RotateX,
    /// Rotation in 3D space around the y-axis.
    RotateY,
    /// Rotation in 3D space around the z-axis.
    RotateZ,
    /// Rotation in 3D space.
    ///
    /// Generalization of rotateX, rotateY and rotateZ.
    Rotate3D,
    /// Specifies a perspective projection matrix.
    ///
    /// Part of CSS Transform Module Level 2 and defined at
    /// [§ 13.1. 3D Transform Function](https://drafts.csswg.org/css-transforms-2/#funcdef-perspective).
    ///
    /// The value must be greater than or equal to zero.
    Perspective,
    /// A intermediate type for interpolation of mismatched transform lists.
    InterpolateMatrix,
    /// A intermediate type for accumulation of mismatched transform lists.
    AccumulateMatrix,
  };

  struct StyleMatrix_Body {
    StyleGenericMatrix<Number> _0;

    bool operator==(const StyleMatrix_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleMatrix3D_Body {
    StyleGenericMatrix3D<Number> _0;

    bool operator==(const StyleMatrix3D_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleSkew_Body {
    Angle _0;
    Angle _1;

    bool operator==(const StyleSkew_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct StyleSkewX_Body {
    Angle _0;

    bool operator==(const StyleSkewX_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleSkewY_Body {
    Angle _0;

    bool operator==(const StyleSkewY_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleTranslate_Body {
    LengthPercentage _0;
    LengthPercentage _1;

    bool operator==(const StyleTranslate_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct StyleTranslateX_Body {
    LengthPercentage _0;

    bool operator==(const StyleTranslateX_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleTranslateY_Body {
    LengthPercentage _0;

    bool operator==(const StyleTranslateY_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleTranslateZ_Body {
    Length _0;

    bool operator==(const StyleTranslateZ_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleTranslate3D_Body {
    LengthPercentage _0;
    LengthPercentage _1;
    Length _2;

    bool operator==(const StyleTranslate3D_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2;
    }
  };

  struct StyleScale_Body {
    Number _0;
    Number _1;

    bool operator==(const StyleScale_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct StyleScaleX_Body {
    Number _0;

    bool operator==(const StyleScaleX_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleScaleY_Body {
    Number _0;

    bool operator==(const StyleScaleY_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleScaleZ_Body {
    Number _0;

    bool operator==(const StyleScaleZ_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleScale3D_Body {
    Number _0;
    Number _1;
    Number _2;

    bool operator==(const StyleScale3D_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2;
    }
  };

  struct StyleRotate_Body {
    Angle _0;

    bool operator==(const StyleRotate_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleRotateX_Body {
    Angle _0;

    bool operator==(const StyleRotateX_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleRotateY_Body {
    Angle _0;

    bool operator==(const StyleRotateY_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleRotateZ_Body {
    Angle _0;

    bool operator==(const StyleRotateZ_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleRotate3D_Body {
    Number _0;
    Number _1;
    Number _2;
    Angle _3;

    bool operator==(const StyleRotate3D_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2 &&
             _3 == other._3;
    }
  };

  struct StylePerspective_Body {
    StyleGenericPerspectiveFunction<Length> _0;

    bool operator==(const StylePerspective_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleInterpolateMatrix_Body {
    StyleGenericTransform<StyleGenericTransformOperation<Angle, Number, Length, Integer, LengthPercentage>> from_list;
    StyleGenericTransform<StyleGenericTransformOperation<Angle, Number, Length, Integer, LengthPercentage>> to_list;
    StylePercentage progress;

    bool operator==(const StyleInterpolateMatrix_Body& other) const {
      return from_list == other.from_list &&
             to_list == other.to_list &&
             progress == other.progress;
    }
  };

  struct StyleAccumulateMatrix_Body {
    StyleGenericTransform<StyleGenericTransformOperation<Angle, Number, Length, Integer, LengthPercentage>> from_list;
    StyleGenericTransform<StyleGenericTransformOperation<Angle, Number, Length, Integer, LengthPercentage>> to_list;
    Integer count;

    bool operator==(const StyleAccumulateMatrix_Body& other) const {
      return from_list == other.from_list &&
             to_list == other.to_list &&
             count == other.count;
    }
  };

  Tag tag;
  union {
    StyleMatrix_Body matrix;
    StyleMatrix3D_Body matrix3_d;
    StyleSkew_Body skew;
    StyleSkewX_Body skew_x;
    StyleSkewY_Body skew_y;
    StyleTranslate_Body translate;
    StyleTranslateX_Body translate_x;
    StyleTranslateY_Body translate_y;
    StyleTranslateZ_Body translate_z;
    StyleTranslate3D_Body translate3_d;
    StyleScale_Body scale;
    StyleScaleX_Body scale_x;
    StyleScaleY_Body scale_y;
    StyleScaleZ_Body scale_z;
    StyleScale3D_Body scale3_d;
    StyleRotate_Body rotate;
    StyleRotateX_Body rotate_x;
    StyleRotateY_Body rotate_y;
    StyleRotateZ_Body rotate_z;
    StyleRotate3D_Body rotate3_d;
    StylePerspective_Body perspective;
    StyleInterpolateMatrix_Body interpolate_matrix;
    StyleAccumulateMatrix_Body accumulate_matrix;
  };

  static StyleGenericTransformOperation Matrix(const StyleGenericMatrix<Number> &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.matrix._0) (StyleGenericMatrix<Number>)(_0);
    result.tag = Tag::Matrix;
    return result;
  }

  bool IsMatrix() const {
    return tag == Tag::Matrix;
  }

  const StyleGenericMatrix<Number>& AsMatrix() const {
    MOZ_DIAGNOSTIC_ASSERT(IsMatrix());
    return matrix._0;
  }

  static StyleGenericTransformOperation Matrix3D(const StyleGenericMatrix3D<Number> &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.matrix3_d._0) (StyleGenericMatrix3D<Number>)(_0);
    result.tag = Tag::Matrix3D;
    return result;
  }

  bool IsMatrix3D() const {
    return tag == Tag::Matrix3D;
  }

  const StyleGenericMatrix3D<Number>& AsMatrix3D() const {
    MOZ_DIAGNOSTIC_ASSERT(IsMatrix3D());
    return matrix3_d._0;
  }

  static StyleGenericTransformOperation Skew(const Angle &_0,
                                             const Angle &_1) {
    StyleGenericTransformOperation result;
    ::new (&result.skew._0) (Angle)(_0);
    ::new (&result.skew._1) (Angle)(_1);
    result.tag = Tag::Skew;
    return result;
  }

  bool IsSkew() const {
    return tag == Tag::Skew;
  }

  const StyleSkew_Body& AsSkew() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSkew());
    return skew;
  }

  static StyleGenericTransformOperation SkewX(const Angle &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.skew_x._0) (Angle)(_0);
    result.tag = Tag::SkewX;
    return result;
  }

  bool IsSkewX() const {
    return tag == Tag::SkewX;
  }

  const Angle& AsSkewX() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSkewX());
    return skew_x._0;
  }

  static StyleGenericTransformOperation SkewY(const Angle &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.skew_y._0) (Angle)(_0);
    result.tag = Tag::SkewY;
    return result;
  }

  bool IsSkewY() const {
    return tag == Tag::SkewY;
  }

  const Angle& AsSkewY() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSkewY());
    return skew_y._0;
  }

  static StyleGenericTransformOperation Translate(const LengthPercentage &_0,
                                                  const LengthPercentage &_1) {
    StyleGenericTransformOperation result;
    ::new (&result.translate._0) (LengthPercentage)(_0);
    ::new (&result.translate._1) (LengthPercentage)(_1);
    result.tag = Tag::Translate;
    return result;
  }

  bool IsTranslate() const {
    return tag == Tag::Translate;
  }

  const StyleTranslate_Body& AsTranslate() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTranslate());
    return translate;
  }

  static StyleGenericTransformOperation TranslateX(const LengthPercentage &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.translate_x._0) (LengthPercentage)(_0);
    result.tag = Tag::TranslateX;
    return result;
  }

  bool IsTranslateX() const {
    return tag == Tag::TranslateX;
  }

  const LengthPercentage& AsTranslateX() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTranslateX());
    return translate_x._0;
  }

  static StyleGenericTransformOperation TranslateY(const LengthPercentage &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.translate_y._0) (LengthPercentage)(_0);
    result.tag = Tag::TranslateY;
    return result;
  }

  bool IsTranslateY() const {
    return tag == Tag::TranslateY;
  }

  const LengthPercentage& AsTranslateY() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTranslateY());
    return translate_y._0;
  }

  static StyleGenericTransformOperation TranslateZ(const Length &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.translate_z._0) (Length)(_0);
    result.tag = Tag::TranslateZ;
    return result;
  }

  bool IsTranslateZ() const {
    return tag == Tag::TranslateZ;
  }

  const Length& AsTranslateZ() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTranslateZ());
    return translate_z._0;
  }

  static StyleGenericTransformOperation Translate3D(const LengthPercentage &_0,
                                                    const LengthPercentage &_1,
                                                    const Length &_2) {
    StyleGenericTransformOperation result;
    ::new (&result.translate3_d._0) (LengthPercentage)(_0);
    ::new (&result.translate3_d._1) (LengthPercentage)(_1);
    ::new (&result.translate3_d._2) (Length)(_2);
    result.tag = Tag::Translate3D;
    return result;
  }

  bool IsTranslate3D() const {
    return tag == Tag::Translate3D;
  }

  const StyleTranslate3D_Body& AsTranslate3D() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTranslate3D());
    return translate3_d;
  }

  static StyleGenericTransformOperation Scale(const Number &_0,
                                              const Number &_1) {
    StyleGenericTransformOperation result;
    ::new (&result.scale._0) (Number)(_0);
    ::new (&result.scale._1) (Number)(_1);
    result.tag = Tag::Scale;
    return result;
  }

  bool IsScale() const {
    return tag == Tag::Scale;
  }

  const StyleScale_Body& AsScale() const {
    MOZ_DIAGNOSTIC_ASSERT(IsScale());
    return scale;
  }

  static StyleGenericTransformOperation ScaleX(const Number &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.scale_x._0) (Number)(_0);
    result.tag = Tag::ScaleX;
    return result;
  }

  bool IsScaleX() const {
    return tag == Tag::ScaleX;
  }

  const Number& AsScaleX() const {
    MOZ_DIAGNOSTIC_ASSERT(IsScaleX());
    return scale_x._0;
  }

  static StyleGenericTransformOperation ScaleY(const Number &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.scale_y._0) (Number)(_0);
    result.tag = Tag::ScaleY;
    return result;
  }

  bool IsScaleY() const {
    return tag == Tag::ScaleY;
  }

  const Number& AsScaleY() const {
    MOZ_DIAGNOSTIC_ASSERT(IsScaleY());
    return scale_y._0;
  }

  static StyleGenericTransformOperation ScaleZ(const Number &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.scale_z._0) (Number)(_0);
    result.tag = Tag::ScaleZ;
    return result;
  }

  bool IsScaleZ() const {
    return tag == Tag::ScaleZ;
  }

  const Number& AsScaleZ() const {
    MOZ_DIAGNOSTIC_ASSERT(IsScaleZ());
    return scale_z._0;
  }

  static StyleGenericTransformOperation Scale3D(const Number &_0,
                                                const Number &_1,
                                                const Number &_2) {
    StyleGenericTransformOperation result;
    ::new (&result.scale3_d._0) (Number)(_0);
    ::new (&result.scale3_d._1) (Number)(_1);
    ::new (&result.scale3_d._2) (Number)(_2);
    result.tag = Tag::Scale3D;
    return result;
  }

  bool IsScale3D() const {
    return tag == Tag::Scale3D;
  }

  const StyleScale3D_Body& AsScale3D() const {
    MOZ_DIAGNOSTIC_ASSERT(IsScale3D());
    return scale3_d;
  }

  static StyleGenericTransformOperation Rotate(const Angle &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.rotate._0) (Angle)(_0);
    result.tag = Tag::Rotate;
    return result;
  }

  bool IsRotate() const {
    return tag == Tag::Rotate;
  }

  const Angle& AsRotate() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRotate());
    return rotate._0;
  }

  static StyleGenericTransformOperation RotateX(const Angle &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.rotate_x._0) (Angle)(_0);
    result.tag = Tag::RotateX;
    return result;
  }

  bool IsRotateX() const {
    return tag == Tag::RotateX;
  }

  const Angle& AsRotateX() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRotateX());
    return rotate_x._0;
  }

  static StyleGenericTransformOperation RotateY(const Angle &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.rotate_y._0) (Angle)(_0);
    result.tag = Tag::RotateY;
    return result;
  }

  bool IsRotateY() const {
    return tag == Tag::RotateY;
  }

  const Angle& AsRotateY() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRotateY());
    return rotate_y._0;
  }

  static StyleGenericTransformOperation RotateZ(const Angle &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.rotate_z._0) (Angle)(_0);
    result.tag = Tag::RotateZ;
    return result;
  }

  bool IsRotateZ() const {
    return tag == Tag::RotateZ;
  }

  const Angle& AsRotateZ() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRotateZ());
    return rotate_z._0;
  }

  static StyleGenericTransformOperation Rotate3D(const Number &_0,
                                                 const Number &_1,
                                                 const Number &_2,
                                                 const Angle &_3) {
    StyleGenericTransformOperation result;
    ::new (&result.rotate3_d._0) (Number)(_0);
    ::new (&result.rotate3_d._1) (Number)(_1);
    ::new (&result.rotate3_d._2) (Number)(_2);
    ::new (&result.rotate3_d._3) (Angle)(_3);
    result.tag = Tag::Rotate3D;
    return result;
  }

  bool IsRotate3D() const {
    return tag == Tag::Rotate3D;
  }

  const StyleRotate3D_Body& AsRotate3D() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRotate3D());
    return rotate3_d;
  }

  static StyleGenericTransformOperation Perspective(const StyleGenericPerspectiveFunction<Length> &_0) {
    StyleGenericTransformOperation result;
    ::new (&result.perspective._0) (StyleGenericPerspectiveFunction<Length>)(_0);
    result.tag = Tag::Perspective;
    return result;
  }

  bool IsPerspective() const {
    return tag == Tag::Perspective;
  }

  const StyleGenericPerspectiveFunction<Length>& AsPerspective() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPerspective());
    return perspective._0;
  }

  static StyleGenericTransformOperation InterpolateMatrix(const StyleGenericTransform<StyleGenericTransformOperation<Angle, Number, Length, Integer, LengthPercentage>> &from_list,
                                                          const StyleGenericTransform<StyleGenericTransformOperation<Angle, Number, Length, Integer, LengthPercentage>> &to_list,
                                                          const StylePercentage &progress) {
    StyleGenericTransformOperation result;
    ::new (&result.interpolate_matrix.from_list) (StyleGenericTransform<StyleGenericTransformOperation<Angle, Number, Length, Integer, LengthPercentage>>)(from_list);
    ::new (&result.interpolate_matrix.to_list) (StyleGenericTransform<StyleGenericTransformOperation<Angle, Number, Length, Integer, LengthPercentage>>)(to_list);
    ::new (&result.interpolate_matrix.progress) (StylePercentage)(progress);
    result.tag = Tag::InterpolateMatrix;
    return result;
  }

  bool IsInterpolateMatrix() const {
    return tag == Tag::InterpolateMatrix;
  }

  const StyleInterpolateMatrix_Body& AsInterpolateMatrix() const {
    MOZ_DIAGNOSTIC_ASSERT(IsInterpolateMatrix());
    return interpolate_matrix;
  }

  static StyleGenericTransformOperation AccumulateMatrix(const StyleGenericTransform<StyleGenericTransformOperation<Angle, Number, Length, Integer, LengthPercentage>> &from_list,
                                                         const StyleGenericTransform<StyleGenericTransformOperation<Angle, Number, Length, Integer, LengthPercentage>> &to_list,
                                                         const Integer &count) {
    StyleGenericTransformOperation result;
    ::new (&result.accumulate_matrix.from_list) (StyleGenericTransform<StyleGenericTransformOperation<Angle, Number, Length, Integer, LengthPercentage>>)(from_list);
    ::new (&result.accumulate_matrix.to_list) (StyleGenericTransform<StyleGenericTransformOperation<Angle, Number, Length, Integer, LengthPercentage>>)(to_list);
    ::new (&result.accumulate_matrix.count) (Integer)(count);
    result.tag = Tag::AccumulateMatrix;
    return result;
  }

  bool IsAccumulateMatrix() const {
    return tag == Tag::AccumulateMatrix;
  }

  const StyleAccumulateMatrix_Body& AsAccumulateMatrix() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAccumulateMatrix());
    return accumulate_matrix;
  }

  bool operator==(const StyleGenericTransformOperation& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Matrix: return matrix == other.matrix;
      case Tag::Matrix3D: return matrix3_d == other.matrix3_d;
      case Tag::Skew: return skew == other.skew;
      case Tag::SkewX: return skew_x == other.skew_x;
      case Tag::SkewY: return skew_y == other.skew_y;
      case Tag::Translate: return translate == other.translate;
      case Tag::TranslateX: return translate_x == other.translate_x;
      case Tag::TranslateY: return translate_y == other.translate_y;
      case Tag::TranslateZ: return translate_z == other.translate_z;
      case Tag::Translate3D: return translate3_d == other.translate3_d;
      case Tag::Scale: return scale == other.scale;
      case Tag::ScaleX: return scale_x == other.scale_x;
      case Tag::ScaleY: return scale_y == other.scale_y;
      case Tag::ScaleZ: return scale_z == other.scale_z;
      case Tag::Scale3D: return scale3_d == other.scale3_d;
      case Tag::Rotate: return rotate == other.rotate;
      case Tag::RotateX: return rotate_x == other.rotate_x;
      case Tag::RotateY: return rotate_y == other.rotate_y;
      case Tag::RotateZ: return rotate_z == other.rotate_z;
      case Tag::Rotate3D: return rotate3_d == other.rotate3_d;
      case Tag::Perspective: return perspective == other.perspective;
      case Tag::InterpolateMatrix: return interpolate_matrix == other.interpolate_matrix;
      case Tag::AccumulateMatrix: return accumulate_matrix == other.accumulate_matrix;

    }
    return true;
  }

  private:
  StyleGenericTransformOperation() {

  }
  public:


  ~StyleGenericTransformOperation() {
    switch (tag) {
      case Tag::Matrix: matrix.~StyleMatrix_Body(); break;
      case Tag::Matrix3D: matrix3_d.~StyleMatrix3D_Body(); break;
      case Tag::Skew: skew.~StyleSkew_Body(); break;
      case Tag::SkewX: skew_x.~StyleSkewX_Body(); break;
      case Tag::SkewY: skew_y.~StyleSkewY_Body(); break;
      case Tag::Translate: translate.~StyleTranslate_Body(); break;
      case Tag::TranslateX: translate_x.~StyleTranslateX_Body(); break;
      case Tag::TranslateY: translate_y.~StyleTranslateY_Body(); break;
      case Tag::TranslateZ: translate_z.~StyleTranslateZ_Body(); break;
      case Tag::Translate3D: translate3_d.~StyleTranslate3D_Body(); break;
      case Tag::Scale: scale.~StyleScale_Body(); break;
      case Tag::ScaleX: scale_x.~StyleScaleX_Body(); break;
      case Tag::ScaleY: scale_y.~StyleScaleY_Body(); break;
      case Tag::ScaleZ: scale_z.~StyleScaleZ_Body(); break;
      case Tag::Scale3D: scale3_d.~StyleScale3D_Body(); break;
      case Tag::Rotate: rotate.~StyleRotate_Body(); break;
      case Tag::RotateX: rotate_x.~StyleRotateX_Body(); break;
      case Tag::RotateY: rotate_y.~StyleRotateY_Body(); break;
      case Tag::RotateZ: rotate_z.~StyleRotateZ_Body(); break;
      case Tag::Rotate3D: rotate3_d.~StyleRotate3D_Body(); break;
      case Tag::Perspective: perspective.~StylePerspective_Body(); break;
      case Tag::InterpolateMatrix: interpolate_matrix.~StyleInterpolateMatrix_Body(); break;
      case Tag::AccumulateMatrix: accumulate_matrix.~StyleAccumulateMatrix_Body(); break;

    }
  }

  StyleGenericTransformOperation(const StyleGenericTransformOperation& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Matrix: ::new (&matrix) (StyleMatrix_Body)(other.matrix); break;
      case Tag::Matrix3D: ::new (&matrix3_d) (StyleMatrix3D_Body)(other.matrix3_d); break;
      case Tag::Skew: ::new (&skew) (StyleSkew_Body)(other.skew); break;
      case Tag::SkewX: ::new (&skew_x) (StyleSkewX_Body)(other.skew_x); break;
      case Tag::SkewY: ::new (&skew_y) (StyleSkewY_Body)(other.skew_y); break;
      case Tag::Translate: ::new (&translate) (StyleTranslate_Body)(other.translate); break;
      case Tag::TranslateX: ::new (&translate_x) (StyleTranslateX_Body)(other.translate_x); break;
      case Tag::TranslateY: ::new (&translate_y) (StyleTranslateY_Body)(other.translate_y); break;
      case Tag::TranslateZ: ::new (&translate_z) (StyleTranslateZ_Body)(other.translate_z); break;
      case Tag::Translate3D: ::new (&translate3_d) (StyleTranslate3D_Body)(other.translate3_d); break;
      case Tag::Scale: ::new (&scale) (StyleScale_Body)(other.scale); break;
      case Tag::ScaleX: ::new (&scale_x) (StyleScaleX_Body)(other.scale_x); break;
      case Tag::ScaleY: ::new (&scale_y) (StyleScaleY_Body)(other.scale_y); break;
      case Tag::ScaleZ: ::new (&scale_z) (StyleScaleZ_Body)(other.scale_z); break;
      case Tag::Scale3D: ::new (&scale3_d) (StyleScale3D_Body)(other.scale3_d); break;
      case Tag::Rotate: ::new (&rotate) (StyleRotate_Body)(other.rotate); break;
      case Tag::RotateX: ::new (&rotate_x) (StyleRotateX_Body)(other.rotate_x); break;
      case Tag::RotateY: ::new (&rotate_y) (StyleRotateY_Body)(other.rotate_y); break;
      case Tag::RotateZ: ::new (&rotate_z) (StyleRotateZ_Body)(other.rotate_z); break;
      case Tag::Rotate3D: ::new (&rotate3_d) (StyleRotate3D_Body)(other.rotate3_d); break;
      case Tag::Perspective: ::new (&perspective) (StylePerspective_Body)(other.perspective); break;
      case Tag::InterpolateMatrix: ::new (&interpolate_matrix) (StyleInterpolateMatrix_Body)(other.interpolate_matrix); break;
      case Tag::AccumulateMatrix: ::new (&accumulate_matrix) (StyleAccumulateMatrix_Body)(other.accumulate_matrix); break;

    }
  }
  StyleGenericTransformOperation& operator=(const StyleGenericTransformOperation& other) {
    if (this != &other) {
      this->~StyleGenericTransformOperation();
      new (this) StyleGenericTransformOperation(other);
    }
    return *this;
  }
};

/// A single operation in a computed CSS `transform`
using StyleTransformOperation = StyleGenericTransformOperation<StyleAngle, StyleNumber, StyleLength, StyleInteger, StyleLengthPercentage>;

/// A computed CSS `transform`
using StyleTransform = StyleGenericTransform<StyleTransformOperation>;

/// The computed value of a CSS horizontal position.
using StyleHorizontalPosition = StyleLengthPercentage;

/// The computed value of a CSS vertical position.
using StyleVerticalPosition = StyleLengthPercentage;

/// A generic type for representing a CSS [position](https://drafts.csswg.org/css-values/#position).
template<typename H, typename V>
struct StyleGenericPosition {
  /// The horizontal component of position.
  H horizontal;
  /// The vertical component of position.
  V vertical;

  bool operator==(const StyleGenericPosition& other) const {
    return horizontal == other.horizontal &&
           vertical == other.vertical;
  }
  inline bool HasPercent() const;
  inline bool DependsOnPositioningAreaSize() const;
  static inline StyleGenericPosition FromPercentage(float);
  inline gfx::Point ToGfxPoint(const CSSSize* aBasis = nullptr) const;
  gfx::Point ToGfxPoint(const CSSSize& aBasis) const {
    return ToGfxPoint(&aBasis);
  };
};

/// The computed value of a CSS `<position>`
using StylePosition = StyleGenericPosition<StyleHorizontalPosition, StyleVerticalPosition>;

/// A CSS value made of four components, where its `ToCss` impl will try to
/// serialize as few components as possible, like for example in `border-width`.
template<typename T>
struct StyleRect {
  T _0;
  T _1;
  T _2;
  T _3;

  bool operator==(const StyleRect& other) const {
    return _0 == other._0 &&
           _1 == other._1 &&
           _2 == other._2 &&
           _3 == other._3;
  }
  template<typename Predicate> inline bool All(Predicate) const;
  template<typename Predicate> inline bool Any(Predicate) const;

  // Defined in WritingModes.h
  inline const T& Get(mozilla::Side) const;
  inline const T& Get(LogicalSide, WritingMode) const;
  inline const T& GetIStart(WritingMode) const;
  inline const T& GetBStart(WritingMode) const;
  inline const T& Start(LogicalAxis, WritingMode) const;
  inline const T& GetIEnd(WritingMode) const;
  inline const T& GetBEnd(WritingMode) const;
  inline const T& End(LogicalAxis, WritingMode) const;

  inline T& Get(mozilla::Side);
  inline T& Get(LogicalSide, WritingMode);
  inline T& GetIStart(WritingMode);
  inline T& GetBStart(WritingMode);
  inline T& GetIEnd(WritingMode);
  inline T& GetBEnd(WritingMode);

  static StyleRect WithAllSides(const T& aSide) {
    return {aSide, aSide, aSide, aSide};
  }
};

/// A wrapper of Non-negative values.
template<typename T>
using StyleNonNegative = T;

/// A generic size, for `border-*-radius` longhand properties, or
/// `border-spacing`.
template<typename L>
struct StyleSize2D {
  L width;
  L height;

  bool operator==(const StyleSize2D& other) const {
    return width == other.width &&
           height == other.height;
  }
};

/// A generic value for the `border-*-radius` longhand properties.
template<typename L>
struct StyleGenericBorderCornerRadius {
  StyleSize2D<L> _0;

  bool operator==(const StyleGenericBorderCornerRadius& other) const {
    return _0 == other._0;
  }
};

/// A generic value for `border-radius` and `inset()`.
///
/// <https://drafts.csswg.org/css-backgrounds-3/#border-radius>
template<typename LengthPercentage>
struct StyleGenericBorderRadius {
  /// The top left radius.
  StyleGenericBorderCornerRadius<LengthPercentage> top_left;
  /// The top right radius.
  StyleGenericBorderCornerRadius<LengthPercentage> top_right;
  /// The bottom right radius.
  StyleGenericBorderCornerRadius<LengthPercentage> bottom_right;
  /// The bottom left radius.
  StyleGenericBorderCornerRadius<LengthPercentage> bottom_left;

  bool operator==(const StyleGenericBorderRadius& other) const {
    return top_left == other.top_left &&
           top_right == other.top_right &&
           bottom_right == other.bottom_right &&
           bottom_left == other.bottom_left;
  }
  inline const StyleLengthPercentage& Get(HalfCorner) const;
};

/// <https://drafts.csswg.org/css-shapes/#funcdef-inset>
template<typename LengthPercentage>
struct StyleGenericInsetRect {
  StyleRect<LengthPercentage> rect;
  StyleGenericBorderRadius<StyleNonNegative<LengthPercentage>> round;

  bool operator==(const StyleGenericInsetRect& other) const {
    return rect == other.rect &&
           round == other.round;
  }
};

/// The computed value of `inset()`.
using StyleInsetRect = StyleGenericInsetRect<StyleLengthPercentage>;

/// A generic type for representing an `Auto | <position>`.
/// This is used by <offset-anchor> for now.
/// https://drafts.fxtf.org/motion-1/#offset-anchor-property
template<typename Pos>
struct StyleGenericPositionOrAuto {
  enum class Tag : uint8_t {
    /// The <position> value.
    Position,
    /// The keyword `auto`.
    Auto,
  };

  struct StylePosition_Body {
    Pos _0;

    bool operator==(const StylePosition_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StylePosition_Body position;
  };

  static StyleGenericPositionOrAuto Position(const Pos &_0) {
    StyleGenericPositionOrAuto result;
    ::new (&result.position._0) (Pos)(_0);
    result.tag = Tag::Position;
    return result;
  }

  bool IsPosition() const {
    return tag == Tag::Position;
  }

  const Pos& AsPosition() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPosition());
    return position._0;
  }

  static StyleGenericPositionOrAuto Auto() {
    StyleGenericPositionOrAuto result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  bool operator==(const StyleGenericPositionOrAuto& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Position: return position == other.position;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericPositionOrAuto() {

  }
  public:


  ~StyleGenericPositionOrAuto() {
    switch (tag) {
      case Tag::Position: position.~StylePosition_Body(); break;
      default: break;
    }
  }

  StyleGenericPositionOrAuto(const StyleGenericPositionOrAuto& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Position: ::new (&position) (StylePosition_Body)(other.position); break;
      default: break;
    }
  }
  StyleGenericPositionOrAuto& operator=(const StyleGenericPositionOrAuto& other) {
    if (this != &other) {
      this->~StyleGenericPositionOrAuto();
      new (this) StyleGenericPositionOrAuto(other);
    }
    return *this;
  }
};

/// <https://drafts.csswg.org/css-shapes/#typedef-shape-radius>
template<typename LengthPercentage>
struct StyleGenericShapeRadius {
  enum class Tag : uint8_t {
    Length,
    ClosestSide,
    FarthestSide,
    FarthestCorner,
    ClosestCorner,
  };

  struct StyleLength_Body {
    StyleNonNegative<LengthPercentage> _0;

    bool operator==(const StyleLength_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleLength_Body length;
  };

  static StyleGenericShapeRadius Length(const StyleNonNegative<LengthPercentage> &_0) {
    StyleGenericShapeRadius result;
    ::new (&result.length._0) (StyleNonNegative<LengthPercentage>)(_0);
    result.tag = Tag::Length;
    return result;
  }

  bool IsLength() const {
    return tag == Tag::Length;
  }

  const StyleNonNegative<LengthPercentage>& AsLength() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLength());
    return length._0;
  }

  static StyleGenericShapeRadius ClosestSide() {
    StyleGenericShapeRadius result;
    result.tag = Tag::ClosestSide;
    return result;
  }

  bool IsClosestSide() const {
    return tag == Tag::ClosestSide;
  }

  static StyleGenericShapeRadius FarthestSide() {
    StyleGenericShapeRadius result;
    result.tag = Tag::FarthestSide;
    return result;
  }

  bool IsFarthestSide() const {
    return tag == Tag::FarthestSide;
  }

  static StyleGenericShapeRadius FarthestCorner() {
    StyleGenericShapeRadius result;
    result.tag = Tag::FarthestCorner;
    return result;
  }

  bool IsFarthestCorner() const {
    return tag == Tag::FarthestCorner;
  }

  static StyleGenericShapeRadius ClosestCorner() {
    StyleGenericShapeRadius result;
    result.tag = Tag::ClosestCorner;
    return result;
  }

  bool IsClosestCorner() const {
    return tag == Tag::ClosestCorner;
  }

  bool operator==(const StyleGenericShapeRadius& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Length: return length == other.length;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericShapeRadius() {

  }
  public:


  ~StyleGenericShapeRadius() {
    switch (tag) {
      case Tag::Length: length.~StyleLength_Body(); break;
      default: break;
    }
  }

  StyleGenericShapeRadius(const StyleGenericShapeRadius& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Length: ::new (&length) (StyleLength_Body)(other.length); break;
      default: break;
    }
  }
  StyleGenericShapeRadius& operator=(const StyleGenericShapeRadius& other) {
    if (this != &other) {
      this->~StyleGenericShapeRadius();
      new (this) StyleGenericShapeRadius(other);
    }
    return *this;
  }
};

/// <https://drafts.csswg.org/css-shapes/#funcdef-circle>
template<typename Position, typename LengthPercentage>
struct StyleCircle {
  StyleGenericPositionOrAuto<Position> position;
  StyleGenericShapeRadius<LengthPercentage> radius;

  bool operator==(const StyleCircle& other) const {
    return position == other.position &&
           radius == other.radius;
  }
};

/// <https://drafts.csswg.org/css-shapes/#funcdef-ellipse>
template<typename Position, typename LengthPercentage>
struct StyleEllipse {
  StyleGenericPositionOrAuto<Position> position;
  StyleGenericShapeRadius<LengthPercentage> semiaxis_x;
  StyleGenericShapeRadius<LengthPercentage> semiaxis_y;

  bool operator==(const StyleEllipse& other) const {
    return position == other.position &&
           semiaxis_x == other.semiaxis_x &&
           semiaxis_y == other.semiaxis_y;
  }
};

/// Coordinates for Polygon.
template<typename LengthPercentage>
struct StylePolygonCoord {
  LengthPercentage _0;
  LengthPercentage _1;

  bool operator==(const StylePolygonCoord& other) const {
    return _0 == other._0 &&
           _1 == other._1;
  }
};

/// A generic type for representing the `polygon()` function
///
/// <https://drafts.csswg.org/css-shapes/#funcdef-polygon>
template<typename LengthPercentage>
struct StyleGenericPolygon {
  /// The filling rule for a polygon.
  StyleFillRule fill;
  /// A collection of (x, y) coordinates to draw the polygon.
  StyleOwnedSlice<StylePolygonCoord<LengthPercentage>> coordinates;

  bool operator==(const StyleGenericPolygon& other) const {
    return fill == other.fill &&
           coordinates == other.coordinates;
  }
};

/// A position type for SVG path coordinates (just a pair of floats).
using StyleSVGPathPosition = StyleGenericPosition<StyleCSSFloat, StyleCSSFloat>;

/// Defines a pair of coordinates, representing a rightward and downward offset, respectively, from
/// a specified reference point. Percentages are resolved against the width or height,
/// respectively, of the reference box.
/// https://drafts.csswg.org/css-shapes-2/#typedef-shape-coordinate-pair
template<typename LengthPercentage>
struct StyleCoordinatePair {
  LengthPercentage x;
  LengthPercentage y;

  bool operator==(const StyleCoordinatePair& other) const {
    return x == other.x &&
           y == other.y;
  }
  inline gfx::Point ToGfxPoint(const CSSSize* aBasis = nullptr) const;
  gfx::Point ToGfxPoint(const CSSSize& aBasis) const {
    return ToGfxPoint(&aBasis);
  };
};

/// Defines the end point of the command, which can be specified in absolute or relative coordinates,
/// determined by their "to" or "by" components respectively.
/// https://drafts.csswg.org/css-shapes/#typedef-shape-command-end-point
template<typename Position, typename LengthPercentage>
struct StyleCommandEndPoint {
  enum class Tag : uint8_t {
    ToPosition,
    ByCoordinate,
  };

  struct StyleToPosition_Body {
    Position _0;

    bool operator==(const StyleToPosition_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleByCoordinate_Body {
    StyleCoordinatePair<LengthPercentage> _0;

    bool operator==(const StyleByCoordinate_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleToPosition_Body to_position;
    StyleByCoordinate_Body by_coordinate;
  };

  static StyleCommandEndPoint ToPosition(const Position &_0) {
    StyleCommandEndPoint result;
    ::new (&result.to_position._0) (Position)(_0);
    result.tag = Tag::ToPosition;
    return result;
  }

  bool IsToPosition() const {
    return tag == Tag::ToPosition;
  }

  const Position& AsToPosition() const {
    MOZ_DIAGNOSTIC_ASSERT(IsToPosition());
    return to_position._0;
  }

  static StyleCommandEndPoint ByCoordinate(const StyleCoordinatePair<LengthPercentage> &_0) {
    StyleCommandEndPoint result;
    ::new (&result.by_coordinate._0) (StyleCoordinatePair<LengthPercentage>)(_0);
    result.tag = Tag::ByCoordinate;
    return result;
  }

  bool IsByCoordinate() const {
    return tag == Tag::ByCoordinate;
  }

  const StyleCoordinatePair<LengthPercentage>& AsByCoordinate() const {
    MOZ_DIAGNOSTIC_ASSERT(IsByCoordinate());
    return by_coordinate._0;
  }

  bool operator==(const StyleCommandEndPoint& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::ToPosition: return to_position == other.to_position;
      case Tag::ByCoordinate: return by_coordinate == other.by_coordinate;

    }
    return true;
  }

  private:
  StyleCommandEndPoint() {

  }
  public:


  ~StyleCommandEndPoint() {
    switch (tag) {
      case Tag::ToPosition: to_position.~StyleToPosition_Body(); break;
      case Tag::ByCoordinate: by_coordinate.~StyleByCoordinate_Body(); break;

    }
  }

  StyleCommandEndPoint(const StyleCommandEndPoint& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::ToPosition: ::new (&to_position) (StyleToPosition_Body)(other.to_position); break;
      case Tag::ByCoordinate: ::new (&by_coordinate) (StyleByCoordinate_Body)(other.by_coordinate); break;

    }
  }
  StyleCommandEndPoint& operator=(const StyleCommandEndPoint& other) {
    if (this != &other) {
      this->~StyleCommandEndPoint();
      new (this) StyleCommandEndPoint(other);
    }
    return *this;
  }
  inline gfx::Point ToGfxPoint(const CSSSize* aBasis = nullptr) const;
  gfx::Point ToGfxPoint(const CSSSize& aBasis) const {
    return ToGfxPoint(&aBasis);
  };
};

/// Defines the end point for the commands <horizontal-line-command> and <vertical-line-command>, which
/// can be specified in absolute or relative values, determined by their "to" or "by" components respectively.
/// https://drafts.csswg.org/css-shapes-1/#typedef-shape-horizontal-line-command
/// https://drafts.csswg.org/css-shapes-1/#typedef-shape-vertical-line-command
template<typename AxisPosition, typename LengthPercentage>
union StyleAxisEndPoint {
  enum class Tag : uint8_t {
    ToPosition,
    ByCoordinate,
  };

  struct ToPosition_Body {
    Tag tag;
    AxisPosition _0;

    bool operator==(const ToPosition_Body& other) const {
      return _0 == other._0;
    }
  };

  struct ByCoordinate_Body {
    Tag tag;
    LengthPercentage _0;

    bool operator==(const ByCoordinate_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  ToPosition_Body to_position;
  ByCoordinate_Body by_coordinate;

  static StyleAxisEndPoint ToPosition(const AxisPosition &_0) {
    StyleAxisEndPoint result;
    ::new (&result.to_position._0) (AxisPosition)(_0);
    result.tag = Tag::ToPosition;
    return result;
  }

  bool IsToPosition() const {
    return tag == Tag::ToPosition;
  }

  const AxisPosition& AsToPosition() const {
    MOZ_DIAGNOSTIC_ASSERT(IsToPosition());
    return to_position._0;
  }

  static StyleAxisEndPoint ByCoordinate(const LengthPercentage &_0) {
    StyleAxisEndPoint result;
    ::new (&result.by_coordinate._0) (LengthPercentage)(_0);
    result.tag = Tag::ByCoordinate;
    return result;
  }

  bool IsByCoordinate() const {
    return tag == Tag::ByCoordinate;
  }

  const LengthPercentage& AsByCoordinate() const {
    MOZ_DIAGNOSTIC_ASSERT(IsByCoordinate());
    return by_coordinate._0;
  }

  bool operator==(const StyleAxisEndPoint& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::ToPosition: return to_position == other.to_position;
      case Tag::ByCoordinate: return by_coordinate == other.by_coordinate;

    }
    return true;
  }

  private:
  StyleAxisEndPoint() {

  }
  public:


  ~StyleAxisEndPoint() {
    switch (tag) {
      case Tag::ToPosition: to_position.~ToPosition_Body(); break;
      case Tag::ByCoordinate: by_coordinate.~ByCoordinate_Body(); break;

    }
  }

  StyleAxisEndPoint(const StyleAxisEndPoint& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::ToPosition: ::new (&to_position) (ToPosition_Body)(other.to_position); break;
      case Tag::ByCoordinate: ::new (&by_coordinate) (ByCoordinate_Body)(other.by_coordinate); break;

    }
  }
  StyleAxisEndPoint& operator=(const StyleAxisEndPoint& other) {
    if (this != &other) {
      this->~StyleAxisEndPoint();
      new (this) StyleAxisEndPoint(other);
    }
    return *this;
  }
  inline gfx::Coord ToGfxCoord(const float* aBasis = nullptr) const;
  gfx::Coord ToGfxCoord(const float& aBasis) const {
    return ToGfxCoord(&aBasis);
  };
};

/// Defines a relative control point to a quadratic or cubic Bézier curve, dependent on the
/// reference value. The default `None` is to be relative to the command’s starting point.
/// https://drafts.csswg.org/css-shapes/#typedef-shape-relative-control-point
template<typename LengthPercentage>
struct StyleRelativeControlPoint {
  StyleCoordinatePair<LengthPercentage> coord;
  StyleControlReference reference;

  bool operator==(const StyleRelativeControlPoint& other) const {
    return coord == other.coord &&
           reference == other.reference;
  }
};

/// Defines a control point for a quadratic or cubic Bézier curve, which can be specified
/// in absolute or relative coordinates.
/// https://drafts.csswg.org/css-shapes/#typedef-shape-control-point
template<typename Position, typename LengthPercentage>
struct StyleControlPoint {
  enum class Tag : uint8_t {
    Absolute,
    Relative,
  };

  struct StyleAbsolute_Body {
    Position _0;

    bool operator==(const StyleAbsolute_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleRelative_Body {
    StyleRelativeControlPoint<LengthPercentage> _0;

    bool operator==(const StyleRelative_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleAbsolute_Body absolute;
    StyleRelative_Body relative;
  };

  static StyleControlPoint Absolute(const Position &_0) {
    StyleControlPoint result;
    ::new (&result.absolute._0) (Position)(_0);
    result.tag = Tag::Absolute;
    return result;
  }

  bool IsAbsolute() const {
    return tag == Tag::Absolute;
  }

  const Position& AsAbsolute() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAbsolute());
    return absolute._0;
  }

  static StyleControlPoint Relative(const StyleRelativeControlPoint<LengthPercentage> &_0) {
    StyleControlPoint result;
    ::new (&result.relative._0) (StyleRelativeControlPoint<LengthPercentage>)(_0);
    result.tag = Tag::Relative;
    return result;
  }

  bool IsRelative() const {
    return tag == Tag::Relative;
  }

  const StyleRelativeControlPoint<LengthPercentage>& AsRelative() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRelative());
    return relative._0;
  }

  bool operator==(const StyleControlPoint& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Absolute: return absolute == other.absolute;
      case Tag::Relative: return relative == other.relative;

    }
    return true;
  }

  private:
  StyleControlPoint() {

  }
  public:


  ~StyleControlPoint() {
    switch (tag) {
      case Tag::Absolute: absolute.~StyleAbsolute_Body(); break;
      case Tag::Relative: relative.~StyleRelative_Body(); break;

    }
  }

  StyleControlPoint(const StyleControlPoint& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Absolute: ::new (&absolute) (StyleAbsolute_Body)(other.absolute); break;
      case Tag::Relative: ::new (&relative) (StyleRelative_Body)(other.relative); break;

    }
  }
  StyleControlPoint& operator=(const StyleControlPoint& other) {
    if (this != &other) {
      this->~StyleControlPoint();
      new (this) StyleControlPoint(other);
    }
    return *this;
  }
  inline gfx::Point ToGfxPoint(
    const gfx::Point aStatePos, const gfx::Point aEndPoint,
    const CSSSize* aBasis = nullptr) const;
  gfx::Point ToGfxPoint(
    const gfx::Point aStatePos, const gfx::Point aEndPoint,
    const CSSSize& aBasis) const {
    return ToGfxPoint(aStatePos, aEndPoint, &aBasis);
  }
};

/// Defines the radiuses for an <arc-command>.
///
/// The first <length-percentage> is the ellipse's horizontal radius, and the second is
/// the vertical radius. If only one value is provided, it is used for both radii, and any
/// <percentage> is resolved against the direction-agnostic size of the reference box.
/// https://drafts.csswg.org/css-shapes-1/#typedef-shape-arc-command
template<typename LengthPercentage>
struct StyleArcRadii {
  LengthPercentage rx;
  StyleOptional<LengthPercentage> ry;

  bool operator==(const StyleArcRadii& other) const {
    return rx == other.rx &&
           ry == other.ry;
  }
  inline gfx::Point ToGfxPoint(const CSSSize* aBasis = nullptr) const;
  gfx::Point ToGfxPoint(const CSSSize& aBasis) const {
    return ToGfxPoint(&aBasis);
  };
};

/// This is a more general shape(path) command type, for both shape() and path().
///
/// https://www.w3.org/TR/SVG11/paths.html#PathData
/// https://drafts.csswg.org/css-shapes-2/#shape-function
template<typename Angle, typename AxisPosition, typename Position, typename LengthPercentage>
struct StyleGenericShapeCommand {
  enum class Tag : uint8_t {
    /// The move command.
    Move,
    /// The line command.
    Line,
    /// The hline command.
    HLine,
    /// The vline command.
    VLine,
    /// The cubic Bézier curve command.
    CubicCurve,
    /// The quadratic Bézier curve command.
    QuadCurve,
    /// The smooth command.
    SmoothCubic,
    /// The smooth quadratic Bézier curve command.
    SmoothQuad,
    /// The arc command.
    Arc,
    /// The closepath command.
    Close,
  };

  struct StyleMove_Body {
    StyleCommandEndPoint<Position, LengthPercentage> point;

    bool operator==(const StyleMove_Body& other) const {
      return point == other.point;
    }
  };

  struct StyleLine_Body {
    StyleCommandEndPoint<Position, LengthPercentage> point;

    bool operator==(const StyleLine_Body& other) const {
      return point == other.point;
    }
  };

  struct StyleHLine_Body {
    StyleAxisEndPoint<AxisPosition, LengthPercentage> x;

    bool operator==(const StyleHLine_Body& other) const {
      return x == other.x;
    }
  };

  struct StyleVLine_Body {
    StyleAxisEndPoint<AxisPosition, LengthPercentage> y;

    bool operator==(const StyleVLine_Body& other) const {
      return y == other.y;
    }
  };

  struct StyleCubicCurve_Body {
    StyleCommandEndPoint<Position, LengthPercentage> point;
    StyleControlPoint<Position, LengthPercentage> control1;
    StyleControlPoint<Position, LengthPercentage> control2;

    bool operator==(const StyleCubicCurve_Body& other) const {
      return point == other.point &&
             control1 == other.control1 &&
             control2 == other.control2;
    }
  };

  struct StyleQuadCurve_Body {
    StyleCommandEndPoint<Position, LengthPercentage> point;
    StyleControlPoint<Position, LengthPercentage> control1;

    bool operator==(const StyleQuadCurve_Body& other) const {
      return point == other.point &&
             control1 == other.control1;
    }
  };

  struct StyleSmoothCubic_Body {
    StyleCommandEndPoint<Position, LengthPercentage> point;
    StyleControlPoint<Position, LengthPercentage> control2;

    bool operator==(const StyleSmoothCubic_Body& other) const {
      return point == other.point &&
             control2 == other.control2;
    }
  };

  struct StyleSmoothQuad_Body {
    StyleCommandEndPoint<Position, LengthPercentage> point;

    bool operator==(const StyleSmoothQuad_Body& other) const {
      return point == other.point;
    }
  };

  struct StyleArc_Body {
    StyleCommandEndPoint<Position, LengthPercentage> point;
    StyleArcRadii<LengthPercentage> radii;
    StyleArcSweep arc_sweep;
    StyleArcSize arc_size;
    Angle rotate;

    bool operator==(const StyleArc_Body& other) const {
      return point == other.point &&
             radii == other.radii &&
             arc_sweep == other.arc_sweep &&
             arc_size == other.arc_size &&
             rotate == other.rotate;
    }
  };

  Tag tag;
  union {
    StyleMove_Body move;
    StyleLine_Body line;
    StyleHLine_Body h_line;
    StyleVLine_Body v_line;
    StyleCubicCurve_Body cubic_curve;
    StyleQuadCurve_Body quad_curve;
    StyleSmoothCubic_Body smooth_cubic;
    StyleSmoothQuad_Body smooth_quad;
    StyleArc_Body arc;
  };

  static StyleGenericShapeCommand Move(const StyleCommandEndPoint<Position, LengthPercentage> &point) {
    StyleGenericShapeCommand result;
    ::new (&result.move.point) (StyleCommandEndPoint<Position, LengthPercentage>)(point);
    result.tag = Tag::Move;
    return result;
  }

  bool IsMove() const {
    return tag == Tag::Move;
  }

  const StyleMove_Body& AsMove() const {
    MOZ_DIAGNOSTIC_ASSERT(IsMove());
    return move;
  }

  static StyleGenericShapeCommand Line(const StyleCommandEndPoint<Position, LengthPercentage> &point) {
    StyleGenericShapeCommand result;
    ::new (&result.line.point) (StyleCommandEndPoint<Position, LengthPercentage>)(point);
    result.tag = Tag::Line;
    return result;
  }

  bool IsLine() const {
    return tag == Tag::Line;
  }

  const StyleLine_Body& AsLine() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLine());
    return line;
  }

  static StyleGenericShapeCommand HLine(const StyleAxisEndPoint<AxisPosition, LengthPercentage> &x) {
    StyleGenericShapeCommand result;
    ::new (&result.h_line.x) (StyleAxisEndPoint<AxisPosition, LengthPercentage>)(x);
    result.tag = Tag::HLine;
    return result;
  }

  bool IsHLine() const {
    return tag == Tag::HLine;
  }

  const StyleHLine_Body& AsHLine() const {
    MOZ_DIAGNOSTIC_ASSERT(IsHLine());
    return h_line;
  }

  static StyleGenericShapeCommand VLine(const StyleAxisEndPoint<AxisPosition, LengthPercentage> &y) {
    StyleGenericShapeCommand result;
    ::new (&result.v_line.y) (StyleAxisEndPoint<AxisPosition, LengthPercentage>)(y);
    result.tag = Tag::VLine;
    return result;
  }

  bool IsVLine() const {
    return tag == Tag::VLine;
  }

  const StyleVLine_Body& AsVLine() const {
    MOZ_DIAGNOSTIC_ASSERT(IsVLine());
    return v_line;
  }

  static StyleGenericShapeCommand CubicCurve(const StyleCommandEndPoint<Position, LengthPercentage> &point,
                                             const StyleControlPoint<Position, LengthPercentage> &control1,
                                             const StyleControlPoint<Position, LengthPercentage> &control2) {
    StyleGenericShapeCommand result;
    ::new (&result.cubic_curve.point) (StyleCommandEndPoint<Position, LengthPercentage>)(point);
    ::new (&result.cubic_curve.control1) (StyleControlPoint<Position, LengthPercentage>)(control1);
    ::new (&result.cubic_curve.control2) (StyleControlPoint<Position, LengthPercentage>)(control2);
    result.tag = Tag::CubicCurve;
    return result;
  }

  bool IsCubicCurve() const {
    return tag == Tag::CubicCurve;
  }

  const StyleCubicCurve_Body& AsCubicCurve() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCubicCurve());
    return cubic_curve;
  }

  static StyleGenericShapeCommand QuadCurve(const StyleCommandEndPoint<Position, LengthPercentage> &point,
                                            const StyleControlPoint<Position, LengthPercentage> &control1) {
    StyleGenericShapeCommand result;
    ::new (&result.quad_curve.point) (StyleCommandEndPoint<Position, LengthPercentage>)(point);
    ::new (&result.quad_curve.control1) (StyleControlPoint<Position, LengthPercentage>)(control1);
    result.tag = Tag::QuadCurve;
    return result;
  }

  bool IsQuadCurve() const {
    return tag == Tag::QuadCurve;
  }

  const StyleQuadCurve_Body& AsQuadCurve() const {
    MOZ_DIAGNOSTIC_ASSERT(IsQuadCurve());
    return quad_curve;
  }

  static StyleGenericShapeCommand SmoothCubic(const StyleCommandEndPoint<Position, LengthPercentage> &point,
                                              const StyleControlPoint<Position, LengthPercentage> &control2) {
    StyleGenericShapeCommand result;
    ::new (&result.smooth_cubic.point) (StyleCommandEndPoint<Position, LengthPercentage>)(point);
    ::new (&result.smooth_cubic.control2) (StyleControlPoint<Position, LengthPercentage>)(control2);
    result.tag = Tag::SmoothCubic;
    return result;
  }

  bool IsSmoothCubic() const {
    return tag == Tag::SmoothCubic;
  }

  const StyleSmoothCubic_Body& AsSmoothCubic() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSmoothCubic());
    return smooth_cubic;
  }

  static StyleGenericShapeCommand SmoothQuad(const StyleCommandEndPoint<Position, LengthPercentage> &point) {
    StyleGenericShapeCommand result;
    ::new (&result.smooth_quad.point) (StyleCommandEndPoint<Position, LengthPercentage>)(point);
    result.tag = Tag::SmoothQuad;
    return result;
  }

  bool IsSmoothQuad() const {
    return tag == Tag::SmoothQuad;
  }

  const StyleSmoothQuad_Body& AsSmoothQuad() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSmoothQuad());
    return smooth_quad;
  }

  static StyleGenericShapeCommand Arc(const StyleCommandEndPoint<Position, LengthPercentage> &point,
                                      const StyleArcRadii<LengthPercentage> &radii,
                                      const StyleArcSweep &arc_sweep,
                                      const StyleArcSize &arc_size,
                                      const Angle &rotate) {
    StyleGenericShapeCommand result;
    ::new (&result.arc.point) (StyleCommandEndPoint<Position, LengthPercentage>)(point);
    ::new (&result.arc.radii) (StyleArcRadii<LengthPercentage>)(radii);
    ::new (&result.arc.arc_sweep) (StyleArcSweep)(arc_sweep);
    ::new (&result.arc.arc_size) (StyleArcSize)(arc_size);
    ::new (&result.arc.rotate) (Angle)(rotate);
    result.tag = Tag::Arc;
    return result;
  }

  bool IsArc() const {
    return tag == Tag::Arc;
  }

  const StyleArc_Body& AsArc() const {
    MOZ_DIAGNOSTIC_ASSERT(IsArc());
    return arc;
  }

  static StyleGenericShapeCommand Close() {
    StyleGenericShapeCommand result;
    result.tag = Tag::Close;
    return result;
  }

  bool IsClose() const {
    return tag == Tag::Close;
  }

  bool operator==(const StyleGenericShapeCommand& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Move: return move == other.move;
      case Tag::Line: return line == other.line;
      case Tag::HLine: return h_line == other.h_line;
      case Tag::VLine: return v_line == other.v_line;
      case Tag::CubicCurve: return cubic_curve == other.cubic_curve;
      case Tag::QuadCurve: return quad_curve == other.quad_curve;
      case Tag::SmoothCubic: return smooth_cubic == other.smooth_cubic;
      case Tag::SmoothQuad: return smooth_quad == other.smooth_quad;
      case Tag::Arc: return arc == other.arc;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericShapeCommand() {

  }
  public:


  ~StyleGenericShapeCommand() {
    switch (tag) {
      case Tag::Move: move.~StyleMove_Body(); break;
      case Tag::Line: line.~StyleLine_Body(); break;
      case Tag::HLine: h_line.~StyleHLine_Body(); break;
      case Tag::VLine: v_line.~StyleVLine_Body(); break;
      case Tag::CubicCurve: cubic_curve.~StyleCubicCurve_Body(); break;
      case Tag::QuadCurve: quad_curve.~StyleQuadCurve_Body(); break;
      case Tag::SmoothCubic: smooth_cubic.~StyleSmoothCubic_Body(); break;
      case Tag::SmoothQuad: smooth_quad.~StyleSmoothQuad_Body(); break;
      case Tag::Arc: arc.~StyleArc_Body(); break;
      default: break;
    }
  }

  StyleGenericShapeCommand(const StyleGenericShapeCommand& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Move: ::new (&move) (StyleMove_Body)(other.move); break;
      case Tag::Line: ::new (&line) (StyleLine_Body)(other.line); break;
      case Tag::HLine: ::new (&h_line) (StyleHLine_Body)(other.h_line); break;
      case Tag::VLine: ::new (&v_line) (StyleVLine_Body)(other.v_line); break;
      case Tag::CubicCurve: ::new (&cubic_curve) (StyleCubicCurve_Body)(other.cubic_curve); break;
      case Tag::QuadCurve: ::new (&quad_curve) (StyleQuadCurve_Body)(other.quad_curve); break;
      case Tag::SmoothCubic: ::new (&smooth_cubic) (StyleSmoothCubic_Body)(other.smooth_cubic); break;
      case Tag::SmoothQuad: ::new (&smooth_quad) (StyleSmoothQuad_Body)(other.smooth_quad); break;
      case Tag::Arc: ::new (&arc) (StyleArc_Body)(other.arc); break;
      default: break;
    }
  }
  StyleGenericShapeCommand& operator=(const StyleGenericShapeCommand& other) {
    if (this != &other) {
      this->~StyleGenericShapeCommand();
      new (this) StyleGenericShapeCommand(other);
    }
    return *this;
  }
  bool IsCubicType() const { return IsCubicCurve() || IsSmoothCubic(); }
  bool IsQuadraticType() const { return IsQuadCurve() || IsSmoothQuad(); }
};

/// The SVG path command.
/// The fields of these commands are self-explanatory, so we skip the documents.
/// Note: the index of the control points, e.g. control1, control2, are mapping to the control
/// points of the Bézier curve in the spec.
///
/// https://www.w3.org/TR/SVG11/paths.html#PathData
using StylePathCommand = StyleGenericShapeCommand<StyleCSSFloat, StyleCSSFloat, StyleSVGPathPosition, StyleCSSFloat>;

/// Structure to allow Arc-managing some fixed-sized data and a variably-sized
/// slice in a single allocation.
///
template<typename H, typename T>
struct StyleHeaderSlice {
  /// The fixed-sized data.
  H header;
  /// The length of the slice at our end.
  size_t len;
  /// The dynamically-sized data.
  T data[0];
  StyleHeaderSlice() = delete;
  StyleHeaderSlice(const StyleHeaderSlice&) = delete;

  inline ~StyleHeaderSlice();
  inline bool operator==(const StyleHeaderSlice& other) const;

  inline Span<const T> AsSpan() const;
  inline size_t Length() const { return len; }
  inline bool IsEmpty() const { return len == 0; }
};

/// The object allocated by an Arc<T>
///
/// See https://github.com/mozilla/cbindgen/issues/937 for the derive-{eq,neq}=false. But we don't
/// use those anyways so we can just disable them.
template<typename T>
struct StyleArcInner {
  StyleAtomicUsize count;
#if defined(CBINDGEN_IS_SERVO)
  size_t alloc_size
#endif
  ;
  T data;
  // Increase the reference count.
  inline void IncrementRef();
  // Release the reference count, and return whether the result must be freed or not.
  [[nodiscard]] inline bool DecrementRef();
};

/// An atomically reference counted shared pointer
///
/// See the documentation for [`Arc`] in the standard library. Unlike the
/// standard library `Arc`, this `Arc` does not support weak reference counting.
///
/// See the discussion in https://github.com/rust-lang/rust/pull/60594 for the
/// usage of PhantomData.
///
/// [`Arc`]: https://doc.rust-lang.org/stable/std/sync/struct.Arc.html
///
template<typename T>
struct StyleArc {
  StyleArcInner<T> *p;
  StyleArc() = delete;
  inline StyleArc(const StyleArc& Other);
 private:
  inline void Release();
 public:
  explicit StyleArc(decltype(p) aP) : p(aP) {
    MOZ_DIAGNOSTIC_ASSERT(p, "Arc shouldn't be null");
  }
  inline ~StyleArc();

  inline StyleArc& operator=(const StyleArc&);
  inline StyleArc& operator=(StyleArc&&);

  const T* operator->() const {
    MOZ_DIAGNOSTIC_ASSERT(p, "Arc shouldn't be null");
    return &p->data;
  }
  const T& operator*() const {
    MOZ_DIAGNOSTIC_ASSERT(p, "Arc shouldn't be null");
    return p->data;
  }
  bool operator==(const StyleArc& other) const {
    return p == other.p || *(*this) == *other;
  }
};

/// This is functionally equivalent to Arc<(H, [T])>
///
/// When you create an `Arc` containing a dynamically sized type like a slice, the `Arc` is
/// represented on the stack as a "fat pointer", where the length of the slice is stored alongside
/// the `Arc`'s pointer. In some situations you may wish to have a thin pointer instead, perhaps
/// for FFI compatibility or space efficiency. `ThinArc` solves this by storing the length in the
/// allocation itself, via `HeaderSlice`.
template<typename H, typename T>
using StyleThinArc = StyleArc<StyleHeaderSlice<H, T>>;

/// A wrapper type for a refcounted slice using ThinArc.
template<typename T>
struct StyleArcSlice {
  StyleThinArc<uint64_t, T> _0;

  bool operator==(const StyleArcSlice& other) const {
    return _0 == other._0;
  }
  inline StyleArcSlice();
  inline explicit StyleArcSlice(const StyleForgottenArcSlicePtr<T>& aPtr);
  inline Span<const T> AsSpan() const;
  inline size_t Length() const;
  inline bool IsEmpty() const;
};

/// The SVG path data.
///
/// https://www.w3.org/TR/SVG11/paths.html#PathData
struct StyleSVGPathData {
  StyleArcSlice<StylePathCommand> _0;

  bool operator==(const StyleSVGPathData& other) const {
    return _0 == other._0;
  }
};

/// The path function.
///
/// https://drafts.csswg.org/css-shapes-1/#funcdef-basic-shape-path
struct StylePath {
  /// The filling rule for the svg path.
  StyleFillRule fill;
  /// The svg path data.
  StyleSVGPathData path;

  bool operator==(const StylePath& other) const {
    return fill == other.fill &&
           path == other.path;
  }
};

/// The shape function defined in css-shape-2.
/// shape() = shape(<fill-rule>? from <coordinate-pair>, <shape-command>#)
///
/// https://drafts.csswg.org/css-shapes-2/#shape-function
template<typename Angle, typename AxisPosition, typename Position, typename LengthPercentage>
struct StyleShape {
  /// The filling rule for this shape.
  StyleFillRule fill;
  /// The shape command data. Note that the starting point will be the first command in this
  /// slice.
  StyleOwnedSlice<StyleGenericShapeCommand<Angle, AxisPosition, Position, LengthPercentage>> commands;

  bool operator==(const StyleShape& other) const {
    return fill == other.fill &&
           commands == other.commands;
  }
};

/// path() function or shape() function.
template<typename Angle, typename AxisPosition, typename Position, typename LengthPercentage>
struct StyleGenericPathOrShapeFunction {
  enum class Tag : uint8_t {
    /// Defines a path with SVG path syntax.
    Path,
    /// Defines a shape function, which is identical to path() but it uses the CSS syntax.
    Shape,
  };

  struct StylePath_Body {
    StylePath _0;

    bool operator==(const StylePath_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleShape_Body {
    StyleShape<Angle, AxisPosition, Position, LengthPercentage> _0;

    bool operator==(const StyleShape_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StylePath_Body path;
    StyleShape_Body shape;
  };

  static StyleGenericPathOrShapeFunction Path(const StylePath &_0) {
    StyleGenericPathOrShapeFunction result;
    ::new (&result.path._0) (StylePath)(_0);
    result.tag = Tag::Path;
    return result;
  }

  bool IsPath() const {
    return tag == Tag::Path;
  }

  const StylePath& AsPath() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPath());
    return path._0;
  }

  static StyleGenericPathOrShapeFunction Shape(const StyleShape<Angle, AxisPosition, Position, LengthPercentage> &_0) {
    StyleGenericPathOrShapeFunction result;
    ::new (&result.shape._0) (StyleShape<Angle, AxisPosition, Position, LengthPercentage>)(_0);
    result.tag = Tag::Shape;
    return result;
  }

  bool IsShape() const {
    return tag == Tag::Shape;
  }

  const StyleShape<Angle, AxisPosition, Position, LengthPercentage>& AsShape() const {
    MOZ_DIAGNOSTIC_ASSERT(IsShape());
    return shape._0;
  }

  bool operator==(const StyleGenericPathOrShapeFunction& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Path: return path == other.path;
      case Tag::Shape: return shape == other.shape;

    }
    return true;
  }

  private:
  StyleGenericPathOrShapeFunction() {

  }
  public:


  ~StyleGenericPathOrShapeFunction() {
    switch (tag) {
      case Tag::Path: path.~StylePath_Body(); break;
      case Tag::Shape: shape.~StyleShape_Body(); break;

    }
  }

  StyleGenericPathOrShapeFunction(const StyleGenericPathOrShapeFunction& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Path: ::new (&path) (StylePath_Body)(other.path); break;
      case Tag::Shape: ::new (&shape) (StyleShape_Body)(other.shape); break;

    }
  }
  StyleGenericPathOrShapeFunction& operator=(const StyleGenericPathOrShapeFunction& other) {
    if (this != &other) {
      this->~StyleGenericPathOrShapeFunction();
      new (this) StyleGenericPathOrShapeFunction(other);
    }
    return *this;
  }
};

/// The <basic-shape>.
///
/// https://drafts.csswg.org/css-shapes-1/#supported-basic-shapes
template<typename Angle, typename AxisPosition, typename Position, typename LengthPercentage, typename BasicShapeRect>
struct StyleGenericBasicShape {
  enum class Tag : uint8_t {
    /// The <basic-shape-rect>.
    Rect,
    /// Defines a circle with a center and a radius.
    Circle,
    /// Defines an ellipse with a center and x-axis/y-axis radii.
    Ellipse,
    /// Defines a polygon with pair arguments.
    Polygon,
    /// Defines a path() or shape().
    PathOrShape,
  };

  struct StyleRect_Body {
    BasicShapeRect _0;

    bool operator==(const StyleRect_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleCircle_Body {
    StyleCircle<Position, LengthPercentage> _0;

    bool operator==(const StyleCircle_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleEllipse_Body {
    StyleEllipse<Position, LengthPercentage> _0;

    bool operator==(const StyleEllipse_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StylePolygon_Body {
    StyleGenericPolygon<LengthPercentage> _0;

    bool operator==(const StylePolygon_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StylePathOrShape_Body {
    StyleGenericPathOrShapeFunction<Angle, AxisPosition, Position, LengthPercentage> _0;

    bool operator==(const StylePathOrShape_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleRect_Body rect;
    StyleCircle_Body circle;
    StyleEllipse_Body ellipse;
    StylePolygon_Body polygon;
    StylePathOrShape_Body path_or_shape;
  };

  static StyleGenericBasicShape Rect(const BasicShapeRect &_0) {
    StyleGenericBasicShape result;
    ::new (&result.rect._0) (BasicShapeRect)(_0);
    result.tag = Tag::Rect;
    return result;
  }

  bool IsRect() const {
    return tag == Tag::Rect;
  }

  const BasicShapeRect& AsRect() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRect());
    return rect._0;
  }

  static StyleGenericBasicShape Circle(const StyleCircle<Position, LengthPercentage> &_0) {
    StyleGenericBasicShape result;
    ::new (&result.circle._0) (StyleCircle<Position, LengthPercentage>)(_0);
    result.tag = Tag::Circle;
    return result;
  }

  bool IsCircle() const {
    return tag == Tag::Circle;
  }

  const StyleCircle<Position, LengthPercentage>& AsCircle() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCircle());
    return circle._0;
  }

  static StyleGenericBasicShape Ellipse(const StyleEllipse<Position, LengthPercentage> &_0) {
    StyleGenericBasicShape result;
    ::new (&result.ellipse._0) (StyleEllipse<Position, LengthPercentage>)(_0);
    result.tag = Tag::Ellipse;
    return result;
  }

  bool IsEllipse() const {
    return tag == Tag::Ellipse;
  }

  const StyleEllipse<Position, LengthPercentage>& AsEllipse() const {
    MOZ_DIAGNOSTIC_ASSERT(IsEllipse());
    return ellipse._0;
  }

  static StyleGenericBasicShape Polygon(const StyleGenericPolygon<LengthPercentage> &_0) {
    StyleGenericBasicShape result;
    ::new (&result.polygon._0) (StyleGenericPolygon<LengthPercentage>)(_0);
    result.tag = Tag::Polygon;
    return result;
  }

  bool IsPolygon() const {
    return tag == Tag::Polygon;
  }

  const StyleGenericPolygon<LengthPercentage>& AsPolygon() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPolygon());
    return polygon._0;
  }

  static StyleGenericBasicShape PathOrShape(const StyleGenericPathOrShapeFunction<Angle, AxisPosition, Position, LengthPercentage> &_0) {
    StyleGenericBasicShape result;
    ::new (&result.path_or_shape._0) (StyleGenericPathOrShapeFunction<Angle, AxisPosition, Position, LengthPercentage>)(_0);
    result.tag = Tag::PathOrShape;
    return result;
  }

  bool IsPathOrShape() const {
    return tag == Tag::PathOrShape;
  }

  const StyleGenericPathOrShapeFunction<Angle, AxisPosition, Position, LengthPercentage>& AsPathOrShape() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPathOrShape());
    return path_or_shape._0;
  }

  bool operator==(const StyleGenericBasicShape& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Rect: return rect == other.rect;
      case Tag::Circle: return circle == other.circle;
      case Tag::Ellipse: return ellipse == other.ellipse;
      case Tag::Polygon: return polygon == other.polygon;
      case Tag::PathOrShape: return path_or_shape == other.path_or_shape;

    }
    return true;
  }

  private:
  StyleGenericBasicShape() {

  }
  public:


  ~StyleGenericBasicShape() {
    switch (tag) {
      case Tag::Rect: rect.~StyleRect_Body(); break;
      case Tag::Circle: circle.~StyleCircle_Body(); break;
      case Tag::Ellipse: ellipse.~StyleEllipse_Body(); break;
      case Tag::Polygon: polygon.~StylePolygon_Body(); break;
      case Tag::PathOrShape: path_or_shape.~StylePathOrShape_Body(); break;

    }
  }

  StyleGenericBasicShape(const StyleGenericBasicShape& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Rect: ::new (&rect) (StyleRect_Body)(other.rect); break;
      case Tag::Circle: ::new (&circle) (StyleCircle_Body)(other.circle); break;
      case Tag::Ellipse: ::new (&ellipse) (StyleEllipse_Body)(other.ellipse); break;
      case Tag::Polygon: ::new (&polygon) (StylePolygon_Body)(other.polygon); break;
      case Tag::PathOrShape: ::new (&path_or_shape) (StylePathOrShape_Body)(other.path_or_shape); break;

    }
  }
  StyleGenericBasicShape& operator=(const StyleGenericBasicShape& other) {
    if (this != &other) {
      this->~StyleGenericBasicShape();
      new (this) StyleGenericBasicShape(other);
    }
    return *this;
  }
};

/// A computed basic shape.
using StyleBasicShape = StyleGenericBasicShape<StyleAngle, StyleLengthPercentage, StylePosition, StyleLengthPercentage, StyleInsetRect>;

/// The `ray()` function, `ray( [ <angle> && <size> && contain? && [at <position>]? ] )`
///
/// https://drafts.fxtf.org/motion-1/#valdef-offsetpath-ray
template<typename Angle, typename Position>
struct StyleGenericRayFunction {
  /// The bearing angle with `0deg` pointing up and positive angles
  /// representing clockwise rotation.
  Angle angle;
  /// Decide the path length used when `offset-distance` is expressed
  /// as a percentage.
  StyleRaySize size;
  /// Clamp `offset-distance` so that the box is entirely contained
  /// within the path.
  bool contain;
  /// The "at <position>" part. If omitted, we use auto to represent it.
  StyleGenericPositionOrAuto<Position> position;

  bool operator==(const StyleGenericRayFunction& other) const {
    return angle == other.angle &&
           size == other.size &&
           contain == other.contain &&
           position == other.position;
  }
};

/// The computed value of ray() function.
using StyleRayFunction = StyleGenericRayFunction<StyleAngle, StylePosition>;

/// A struct that basically replaces a Box<str>, but with a defined layout,
/// suitable for FFI.
struct StyleOwnedStr {
  StyleOwnedSlice<uint8_t> _0;

  bool operator==(const StyleOwnedStr& other) const {
    return _0 == other._0;
  }
  inline nsDependentCSubstring AsString() const;
};

#if defined(CBINDGEN_IS_GECKO)
/// Extra data that the backend may need to resolve url values.
///
/// If the usize's lowest bit is 0, then this is a strong reference to a
/// structs::URLExtraData object.
///
/// Otherwise, shifting the usize's bits the right by one gives the
/// UserAgentStyleSheetID value corresponding to the style sheet whose
/// URLExtraData this is, which is stored in URLExtraData_sShared.  We don't
/// hold a strong reference to that object from here, but we rely on that
/// array's objects being held alive until shutdown.
///
/// We use this packed representation rather than an enum so that
/// `from_ptr_ref` can work.
struct StyleUrlExtraData {
  size_t _0;

  bool operator==(const StyleUrlExtraData& other) const {
    return _0 == other._0;
  }
  StyleUrlExtraData() = delete;

  // Could be implemented if wanted.
  StyleUrlExtraData(const StyleUrlExtraData&) = delete;
  StyleUrlExtraData& operator=(const StyleUrlExtraData&) = delete;

  inline bool IsShared() const;

  inline ~StyleUrlExtraData();
  inline const URLExtraData& get() const;
};
#endif

#if defined(CBINDGEN_IS_GECKO)
/// Various bits of mutable state that are kept for image loads.
struct StyleLoadDataFlags {
  uint8_t bits;

  constexpr explicit operator bool() const {
    return !!bits;
  }
  constexpr StyleLoadDataFlags operator~() const {
    return StyleLoadDataFlags { static_cast<decltype(bits)>(~bits) };
  }
  constexpr StyleLoadDataFlags operator|(const StyleLoadDataFlags& other) const {
    return StyleLoadDataFlags { static_cast<decltype(bits)>(this->bits | other.bits) };
  }
  StyleLoadDataFlags& operator|=(const StyleLoadDataFlags& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleLoadDataFlags operator&(const StyleLoadDataFlags& other) const {
    return StyleLoadDataFlags { static_cast<decltype(bits)>(this->bits & other.bits) };
  }
  StyleLoadDataFlags& operator&=(const StyleLoadDataFlags& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleLoadDataFlags operator^(const StyleLoadDataFlags& other) const {
    return StyleLoadDataFlags { static_cast<decltype(bits)>(this->bits ^ other.bits) };
  }
  StyleLoadDataFlags& operator^=(const StyleLoadDataFlags& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleLoadDataFlags& other) const {
    return bits == other.bits;
  }
#if defined(CBINDGEN_IS_GECKO)
  static const StyleLoadDataFlags TRIED_TO_RESOLVE_URI;
#endif
#if defined(CBINDGEN_IS_GECKO)
  static const StyleLoadDataFlags TRIED_TO_RESOLVE_IMAGE;
#endif
};
#if defined(CBINDGEN_IS_GECKO)
/// Whether we tried to resolve the uri at least once.
constexpr inline const StyleLoadDataFlags StyleLoadDataFlags::TRIED_TO_RESOLVE_URI = StyleLoadDataFlags{
  /* .bits = */ (uint8_t)(1 << 0)
};
#endif
#if defined(CBINDGEN_IS_GECKO)
/// Whether we tried to resolve the image at least once.
constexpr inline const StyleLoadDataFlags StyleLoadDataFlags::TRIED_TO_RESOLVE_IMAGE = StyleLoadDataFlags{
  /* .bits = */ (uint8_t)(1 << 1)
};
#endif
#endif

#if defined(CBINDGEN_IS_GECKO)
/// The load data for a given URL. This is mutable from C++, and shouldn't be
/// accessed from rust for anything.
struct StyleLoadData {
  /// A strong reference to the imgRequestProxy, if any, that should be
  /// released on drop.
  ///
  /// These are raw pointers because they are not safe to reference-count off
  /// the main thread.
  imgRequestProxy *resolved_image;
  /// A strong reference to the resolved URI of this image.
  nsIURI *resolved_uri;
  /// A few flags that are set when resolving the image or such.
  StyleLoadDataFlags flags;

  bool operator==(const StyleLoadData& other) const {
    return resolved_image == other.resolved_image &&
           resolved_uri == other.resolved_uri &&
           flags == other.flags;
  }
  ~StyleLoadData();
};
#endif

#if defined(CBINDGEN_IS_GECKO)
/// The data for a load, or a lazy-loaded, static member that will be stored in
/// LOAD_DATA_TABLE, keyed by the memory location of this object, which is
/// always in the heap because it's inside the CssUrlData object.
///
/// This type is meant not to be used from C++ so we don't derive helper
/// methods.
///
struct StyleLoadDataSource {
  enum class Tag : uint8_t {
#if defined(CBINDGEN_IS_GECKO)
    /// An owned copy of the load data.
    Owned,
#endif
#if defined(CBINDGEN_IS_GECKO)
    /// A lazily-resolved copy of it.
    Lazy,
#endif
  };

#if defined(CBINDGEN_IS_GECKO)
  struct StyleOwned_Body {
    StyleLoadData _0;

    bool operator==(const StyleOwned_Body& other) const {
      return _0 == other._0;
    }
  };
#endif

  Tag tag;
  union {
#if defined(CBINDGEN_IS_GECKO)
    StyleOwned_Body owned;
#endif
  };

  bool operator==(const StyleLoadDataSource& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
#if defined(CBINDGEN_IS_GECKO)
      case Tag::Owned: return owned == other.owned;
#endif
      default: break;
    }
    return true;
  }

  private:
  StyleLoadDataSource() {

  }
  public:


  ~StyleLoadDataSource() {
    switch (tag) {
#if defined(CBINDGEN_IS_GECKO)
      case Tag::Owned: owned.~StyleOwned_Body(); break;
#endif
      default: break;
    }
  }

  StyleLoadDataSource(const StyleLoadDataSource& other)
   : tag(other.tag) {
    switch (tag) {
#if defined(CBINDGEN_IS_GECKO)
      case Tag::Owned: ::new (&owned) (StyleOwned_Body)(other.owned); break;
#endif
      default: break;
    }
  }
  StyleLoadDataSource& operator=(const StyleLoadDataSource& other) {
    if (this != &other) {
      this->~StyleLoadDataSource();
      new (this) StyleLoadDataSource(other);
    }
    return *this;
  }
};
#endif

#if defined(CBINDGEN_IS_GECKO)
/// Data shared between CssUrls.
///
struct StyleCssUrlData {
  /// The URL in unresolved string form.
  StyleOwnedStr serialization;
  /// The URL extra data.
  StyleUrlExtraData extra_data;
  /// The CORS mode that will be used for the load.
  StyleCorsMode cors_mode;
  /// Data to trigger a load from Gecko. This is mutable in C++.
  ///
  /// TODO(emilio): Maybe we can eagerly resolve URLs and make this immutable?
  StyleLoadDataSource load_data;
  // Implemented in nsStyleStruct.cpp
  bool operator==(const StyleCssUrlData& other) const;
};
#endif

#if defined(CBINDGEN_IS_SERVO)
/// Data shared between CssUrls.
///
struct StyleCssUrlData {
  /// The original URI. This might be optional since we may insert computed
  /// values of images into the cascade directly, and we don't bother to
  /// convert their serialization.
  ///
  /// Refcounted since cloning this should be cheap and data: uris can be
  /// really large.
  StyleOption<StyleArc<StyleString>> original;
  /// The resolved value for the url, if valid.
  StyleOption<StyleArc<StyleUrl>> resolved;

  bool operator==(const StyleCssUrlData& other) const {
    return original == other.original &&
           resolved == other.resolved;
  }
  // Implemented in nsStyleStruct.cpp
  bool operator==(const StyleCssUrlData& other) const;
};
#endif

#if defined(CBINDGEN_IS_GECKO)
/// A CSS url() value for gecko.
struct StyleCssUrl {
  StyleArc<StyleCssUrlData> _0;

  bool operator==(const StyleCssUrl& other) const {
    return _0 == other._0;
  }
  inline nsDependentCSubstring SpecifiedSerialization() const;
  inline const URLExtraData& ExtraData() const;
  inline const StyleLoadData& LoadData() const;
  inline StyleLoadData& MutLoadData() const;
  inline nsIURI* GetURI() const;
};
#endif

#if defined(CBINDGEN_IS_SERVO)
/// A CSS url() value for servo.
///
/// Servo eagerly resolves SpecifiedUrls, which it can then take advantage of
/// when computing values. In contrast, Gecko uses a different URL backend, so
/// eagerly resolving with rust-url would be duplicated work.
///
/// However, this approach is still not necessarily optimal: See
/// <https://bugzilla.mozilla.org/show_bug.cgi?id=1347435#c6>
struct StyleCssUrl {
  StyleArc<StyleCssUrlData> _0;

  bool operator==(const StyleCssUrl& other) const {
    return _0 == other._0;
  }
  inline nsDependentCSubstring SpecifiedSerialization() const;
  inline const URLExtraData& ExtraData() const;
  inline const StyleLoadData& LoadData() const;
  inline StyleLoadData& MutLoadData() const;
  inline nsIURI* GetURI() const;
};
#endif

#if defined(CBINDGEN_IS_GECKO)
/// A specified non-image `url()` value.
using StyleSpecifiedUrl = StyleCssUrl;
#endif

#if defined(CBINDGEN_IS_SERVO)
/// A specified url() value for servo.
using StyleSpecifiedUrl = StyleCssUrl;
#endif

#if defined(CBINDGEN_IS_GECKO)
/// The computed value of a CSS non-image `url()`.
///
/// The only difference between specified and computed URLs is the
/// serialization.
struct StyleComputedUrl {
  StyleSpecifiedUrl _0;

  bool operator==(const StyleComputedUrl& other) const {
    return _0 == other._0;
  }
  // Forwarded from CssUrl.
  inline nsDependentCSubstring SpecifiedSerialization() const;
  inline const URLExtraData& ExtraData() const;
  inline nsIURI* GetURI() const;
  inline const StyleLoadData& LoadData() const;
  inline StyleLoadData& MutLoadData() const;

  inline bool IsLocalRef() const;
  inline bool HasRef() const;
  inline StyleCorsMode CorsMode() const;

  // Only relevant for images.
  inline bool IsImageResolved() const;
  inline imgRequestProxy* GetImage() const;
  void ResolveImage(dom::Document&, const StyleComputedUrl* aOldImage);
};
#endif

/// The <offset-path> value.
/// <offset-path> = <ray()> | <url> | <basic-shape>
///
/// https://drafts.fxtf.org/motion-1/#typedef-offset-path
template<typename Shapes, typename RayFunction, typename U>
struct StyleGenericOffsetPathFunction {
  enum class Tag : uint8_t {
    /// ray() function, which defines a path in the polar coordinate system.
    /// Use Box<> to make sure the size of offset-path is not too large.
    Ray,
    /// A URL reference to an SVG shape element. If the URL does not reference a shape element,
    /// this behaves as path("m 0 0") instead.
    Url,
    /// The <basic-shape> value.
    Shape,
  };

  struct StyleRay_Body {
    RayFunction _0;

    bool operator==(const StyleRay_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleUrl_Body {
    U _0;

    bool operator==(const StyleUrl_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleShape_Body {
    Shapes _0;

    bool operator==(const StyleShape_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleRay_Body ray;
    StyleUrl_Body url;
    StyleShape_Body shape;
  };

  static StyleGenericOffsetPathFunction Ray(const RayFunction &_0) {
    StyleGenericOffsetPathFunction result;
    ::new (&result.ray._0) (RayFunction)(_0);
    result.tag = Tag::Ray;
    return result;
  }

  bool IsRay() const {
    return tag == Tag::Ray;
  }

  const RayFunction& AsRay() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRay());
    return ray._0;
  }

  static StyleGenericOffsetPathFunction Url(const U &_0) {
    StyleGenericOffsetPathFunction result;
    ::new (&result.url._0) (U)(_0);
    result.tag = Tag::Url;
    return result;
  }

  bool IsUrl() const {
    return tag == Tag::Url;
  }

  const U& AsUrl() const {
    MOZ_DIAGNOSTIC_ASSERT(IsUrl());
    return url._0;
  }

  static StyleGenericOffsetPathFunction Shape(const Shapes &_0) {
    StyleGenericOffsetPathFunction result;
    ::new (&result.shape._0) (Shapes)(_0);
    result.tag = Tag::Shape;
    return result;
  }

  bool IsShape() const {
    return tag == Tag::Shape;
  }

  const Shapes& AsShape() const {
    MOZ_DIAGNOSTIC_ASSERT(IsShape());
    return shape._0;
  }

  bool operator==(const StyleGenericOffsetPathFunction& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Ray: return ray == other.ray;
      case Tag::Url: return url == other.url;
      case Tag::Shape: return shape == other.shape;

    }
    return true;
  }

  private:
  StyleGenericOffsetPathFunction() {

  }
  public:


  ~StyleGenericOffsetPathFunction() {
    switch (tag) {
      case Tag::Ray: ray.~StyleRay_Body(); break;
      case Tag::Url: url.~StyleUrl_Body(); break;
      case Tag::Shape: shape.~StyleShape_Body(); break;

    }
  }

  StyleGenericOffsetPathFunction(const StyleGenericOffsetPathFunction& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Ray: ::new (&ray) (StyleRay_Body)(other.ray); break;
      case Tag::Url: ::new (&url) (StyleUrl_Body)(other.url); break;
      case Tag::Shape: ::new (&shape) (StyleShape_Body)(other.shape); break;

    }
  }
  StyleGenericOffsetPathFunction& operator=(const StyleGenericOffsetPathFunction& other) {
    if (this != &other) {
      this->~StyleGenericOffsetPathFunction();
      new (this) StyleGenericOffsetPathFunction(other);
    }
    return *this;
  }
};

/// The computed value of <offset-path>.
using StyleOffsetPathFunction = StyleGenericOffsetPathFunction<StyleBasicShape, StyleRayFunction, StyleComputedUrl>;

/// The offset-path property.
/// offset-path: none | <offset-path> || <coord-box>
///
/// https://drafts.fxtf.org/motion-1/#offset-path-property
template<typename Function>
struct StyleGenericOffsetPath {
  enum class Tag : uint8_t {
    /// <offset-path> || <coord-box>.
    OffsetPath,
    /// Only <coord-box>. This represents that <offset-path> is omitted, so we use the default
    /// value, inset(0 round X), where X is the value of border-radius on the element that
    /// establishes the containing block for this element.
    CoordBox,
    /// None value.
    None,
  };

  struct StyleOffsetPath_Body {
    /// <offset-path> part.
    StyleBox<Function> path;
    /// <coord-box> part.
    StyleCoordBox coord_box;

    bool operator==(const StyleOffsetPath_Body& other) const {
      return path == other.path &&
             coord_box == other.coord_box;
    }
  };

  struct StyleCoordBox_Body {
    StyleCoordBox _0;

    bool operator==(const StyleCoordBox_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleOffsetPath_Body offset_path;
    StyleCoordBox_Body coord_box;
  };

  static StyleGenericOffsetPath OffsetPath(const StyleBox<Function> &path,
                                           const StyleCoordBox &coord_box) {
    StyleGenericOffsetPath result;
    ::new (&result.offset_path.path) (StyleBox<Function>)(path);
    ::new (&result.offset_path.coord_box) (StyleCoordBox)(coord_box);
    result.tag = Tag::OffsetPath;
    return result;
  }

  bool IsOffsetPath() const {
    return tag == Tag::OffsetPath;
  }

  const StyleOffsetPath_Body& AsOffsetPath() const {
    MOZ_DIAGNOSTIC_ASSERT(IsOffsetPath());
    return offset_path;
  }

  static StyleGenericOffsetPath CoordBox(const StyleCoordBox &_0) {
    StyleGenericOffsetPath result;
    ::new (&result.coord_box._0) (StyleCoordBox)(_0);
    result.tag = Tag::CoordBox;
    return result;
  }

  bool IsCoordBox() const {
    return tag == Tag::CoordBox;
  }

  const StyleCoordBox& AsCoordBox() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCoordBox());
    return coord_box._0;
  }

  static StyleGenericOffsetPath None() {
    StyleGenericOffsetPath result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  bool operator==(const StyleGenericOffsetPath& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::OffsetPath: return offset_path == other.offset_path;
      case Tag::CoordBox: return coord_box == other.coord_box;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericOffsetPath() {

  }
  public:


  ~StyleGenericOffsetPath() {
    switch (tag) {
      case Tag::OffsetPath: offset_path.~StyleOffsetPath_Body(); break;
      case Tag::CoordBox: coord_box.~StyleCoordBox_Body(); break;
      default: break;
    }
  }

  StyleGenericOffsetPath(const StyleGenericOffsetPath& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::OffsetPath: ::new (&offset_path) (StyleOffsetPath_Body)(other.offset_path); break;
      case Tag::CoordBox: ::new (&coord_box) (StyleCoordBox_Body)(other.coord_box); break;
      default: break;
    }
  }
  StyleGenericOffsetPath& operator=(const StyleGenericOffsetPath& other) {
    if (this != &other) {
      this->~StyleGenericOffsetPath();
      new (this) StyleGenericOffsetPath(other);
    }
    return *this;
  }
  // Return true if the <offset-path> is ray().
  bool IsRay() const {
    return IsOffsetPath() && AsOffsetPath().path->IsRay();
  }

  const StyleRayFunction& AsRay() const {
    return AsOffsetPath().path->AsRay();
  }

  // Return true if the <offset-path> is url().
  bool IsUrl() const {
    return IsOffsetPath() && AsOffsetPath().path->IsUrl();
  }

  const StyleComputedUrl& AsUrl() const {
    return AsOffsetPath().path->AsUrl();
  }

  // Return true if the <basic-shape> is path().
  bool IsPath() const {
    if (!IsOffsetPath()) {
      return false;
    }
    const auto& path = AsOffsetPath().path;
    if (!path->IsShape()) {
      return false;
    }
    const auto& shape = path->AsShape();
    return shape.IsPathOrShape() && shape.AsPathOrShape().IsPath();
  }

  const StyleSVGPathData& AsSVGPathData() const {
    return AsOffsetPath().path->AsShape().AsPathOrShape().AsPath().path;
  }

  // Return true if this is "<basic-shape> || <coord-box>".
  bool IsBasicShapeOrCoordBox() const {
    return IsCoordBox() || (IsOffsetPath() && AsOffsetPath().path->IsShape());
  }
};

/// The computed value of `offset-path`.
using StyleOffsetPath = StyleGenericOffsetPath<StyleOffsetPathFunction>;

/// A computed offset-rotate.
struct StyleOffsetRotate {
  /// If auto is false, this is a fixed angle which indicates a
  /// constant clockwise rotation transformation applied to it by this
  /// specified rotation angle. Otherwise, the angle will be added to
  /// the angle of the direction in layout.
  bool auto_;
  /// The angle value.
  StyleAngle angle;

  bool operator==(const StyleOffsetRotate& other) const {
    return auto_ == other.auto_ &&
           angle == other.angle;
  }
};

/// The computed value of an `auto | <position>`
using StylePositionOrAuto = StyleGenericPositionOrAuto<StylePosition>;

/// The offset-position property, which specifies the offset starting position that is used by the
/// <offset-path> functions if they don’t specify their own starting position.
///
/// https://drafts.fxtf.org/motion-1/#offset-position-property
template<typename H, typename V>
struct StyleGenericOffsetPosition {
  enum class Tag : uint8_t {
    /// The element does not have an offset starting position.
    Normal,
    /// The offset starting position is the top-left corner of the box.
    Auto,
    /// The offset starting position is the result of using the <position> to position a 0x0 object
    /// area within the box’s containing block.
    Position,
  };

  struct StylePosition_Body {
    StyleGenericPosition<H, V> _0;

    bool operator==(const StylePosition_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StylePosition_Body position;
  };

  static StyleGenericOffsetPosition Normal() {
    StyleGenericOffsetPosition result;
    result.tag = Tag::Normal;
    return result;
  }

  bool IsNormal() const {
    return tag == Tag::Normal;
  }

  static StyleGenericOffsetPosition Auto() {
    StyleGenericOffsetPosition result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleGenericOffsetPosition Position(const StyleGenericPosition<H, V> &_0) {
    StyleGenericOffsetPosition result;
    ::new (&result.position._0) (StyleGenericPosition<H, V>)(_0);
    result.tag = Tag::Position;
    return result;
  }

  bool IsPosition() const {
    return tag == Tag::Position;
  }

  const StyleGenericPosition<H, V>& AsPosition() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPosition());
    return position._0;
  }

  bool operator==(const StyleGenericOffsetPosition& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Position: return position == other.position;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericOffsetPosition() {

  }
  public:


  ~StyleGenericOffsetPosition() {
    switch (tag) {
      case Tag::Position: position.~StylePosition_Body(); break;
      default: break;
    }
  }

  StyleGenericOffsetPosition(const StyleGenericOffsetPosition& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Position: ::new (&position) (StylePosition_Body)(other.position); break;
      default: break;
    }
  }
  StyleGenericOffsetPosition& operator=(const StyleGenericOffsetPosition& other) {
    if (this != &other) {
      this->~StyleGenericOffsetPosition();
      new (this) StyleGenericOffsetPosition(other);
    }
    return *this;
  }
};

/// The computed value of `offset-position`.
using StyleOffsetPosition = StyleGenericOffsetPosition<StyleLengthPercentage, StyleLengthPercentage>;

struct StyleShouldTransitionResult {
  bool should_animate;
  bool old_transition_value_matches;

  bool operator==(const StyleShouldTransitionResult& other) const {
    return should_animate == other.should_animate &&
           old_transition_value_matches == other.old_transition_value_matches;
  }
};

#if defined(XP_UNIX)
/// Platform-specific handle to a thread.
using StylePlatformThreadHandle = pthread_t;
#endif

#if defined(XP_WIN)
/// Platform-specific handle to a thread.
using StylePlatformThreadHandle = void*;
#endif

#if !defined(CBINDGEN_IS_GECKO)
/// Platform-specific handle to a thread.
using StylePlatformThreadHandle = StyleDummyThreadHandle;
#endif

/// Additional scope rule data for matching a style rule.
struct StyleScopeRuleData {
  /// Scope rule applicable at this nesting level.
  const StyleScopeRule *scope_rule;
  /// Stylesheet this scope rule comes from.
  const StyleDomStyleSheet *sheet;
  /// Index to the last style rule in an array this scope applies to.
  size_t valid_til;

  bool operator==(const StyleScopeRuleData& other) const {
    return scope_rule == other.scope_rule &&
           sheet == other.sheet &&
           valid_til == other.valid_til;
  }
};

/// Generic template for font property type classes that use a fixed-point
/// internal representation with `FRACTION_BITS` for the fractional part.
///
/// Values are constructed from and exposed as floating-point, but stored
/// internally as fixed point, so there will be a quantization effect on
/// fractional values, depending on the number of fractional bits used.
///
/// Using (16-bit) fixed-point types rather than floats for these style
/// attributes reduces the memory footprint of gfxFontEntry and gfxFontStyle; it
/// will also tend to reduce the number of distinct font instances that get
/// created, particularly when styles are animated or set to arbitrary values
/// (e.g. by sliders in the UI), which should reduce pressure on graphics
/// resources and improve cache hit rates.
///
template<typename T, uint16_t FRACTION_BITS>
struct StyleFixedPoint {
  /// The actual representation.
  T value;

  bool operator==(const StyleFixedPoint& other) const {
    return value == other.value;
  }
  bool operator<(const StyleFixedPoint& other) const {
    return value < other.value;
  }
  bool operator<=(const StyleFixedPoint& other) const {
    return value <= other.value;
  }
  bool operator>(const StyleFixedPoint& other) const {
    return value > other.value;
  }
  bool operator>=(const StyleFixedPoint& other) const {
    return value >= other.value;
  }
};

/// This is an alias which is useful mostly as a cbindgen / C++ inference
/// workaround.
using StyleFontWeightFixedPoint = StyleFixedPoint<uint16_t, StyleFONT_WEIGHT_FRACTION_BITS>;

/// A value for the font-weight property per:
///
/// https://drafts.csswg.org/css-fonts-4/#propdef-font-weight
///
struct StyleFontWeight {
  StyleFontWeightFixedPoint _0;

  bool operator==(const StyleFontWeight& other) const {
    return _0 == other._0;
  }
  bool operator<(const StyleFontWeight& other) const {
    return _0 < other._0;
  }
  bool operator<=(const StyleFontWeight& other) const {
    return _0 <= other._0;
  }
  bool operator>(const StyleFontWeight& other) const {
    return _0 > other._0;
  }
  bool operator>=(const StyleFontWeight& other) const {
    return _0 >= other._0;
  }
 SERVO_FIXED_POINT_HELPERS(StyleFontWeight, uint16_t, StyleFONT_WEIGHT_FRACTION_BITS);
 bool IsNormal() const { return *this == NORMAL; }

 inline bool IsBold() const;
 inline bool PreferBold() const;
  static const StyleFontWeight NORMAL;
  static const StyleFontWeight BOLD;
  static const StyleFontWeight BOLD_THRESHOLD;
  static const StyleFontWeight PREFER_BOLD_THRESHOLD;
};
/// The `normal` keyword.
constexpr inline const StyleFontWeight StyleFontWeight::NORMAL = StyleFontWeight{
  /* ._0 = */ StyleFontWeightFixedPoint{
    /* .value = */ (400 << StyleFONT_WEIGHT_FRACTION_BITS)
  }
};
/// The `bold` value.
constexpr inline const StyleFontWeight StyleFontWeight::BOLD = StyleFontWeight{
  /* ._0 = */ StyleFontWeightFixedPoint{
    /* .value = */ (700 << StyleFONT_WEIGHT_FRACTION_BITS)
  }
};
/// The threshold from which we consider a font bold.
constexpr inline const StyleFontWeight StyleFontWeight::BOLD_THRESHOLD = StyleFontWeight{
  /* ._0 = */ StyleFontWeightFixedPoint{
    /* .value = */ (600 << StyleFONT_WEIGHT_FRACTION_BITS)
  }
};
/// The threshold above which CSS font matching prefers bolder faces
/// over lighter ones.
constexpr inline const StyleFontWeight StyleFontWeight::PREFER_BOLD_THRESHOLD = StyleFontWeight{
  /* ._0 = */ StyleFontWeightFixedPoint{
    /* .value = */ (500 << StyleFONT_WEIGHT_FRACTION_BITS)
  }
};

/// The computed representation of the above so Gecko and Servo can read them easily.
///
/// This one is needed because cbindgen doesn't know how to generate
/// specified::Number.
struct StyleComputedFontWeightRange {
  StyleFontWeight _0;
  StyleFontWeight _1;

  bool operator==(const StyleComputedFontWeightRange& other) const {
    return _0 == other._0 &&
           _1 == other._1;
  }
};

/// This is an alias which is useful mostly as a cbindgen / C++ inference
/// workaround.
using StyleFontWidthFixedPoint = StyleFixedPoint<uint16_t, StyleFONT_WIDTH_FRACTION_BITS>;

/// A value for the font-width property per:
///
/// https://drafts.csswg.org/css-fonts-4/#propdef-font-width
///
/// (Note that this property was formerly named font-stretch.)
///
struct StyleFontWidth {
  StyleFontWidthFixedPoint _0;

  bool operator==(const StyleFontWidth& other) const {
    return _0 == other._0;
  }
  bool operator<(const StyleFontWidth& other) const {
    return _0 < other._0;
  }
  bool operator<=(const StyleFontWidth& other) const {
    return _0 <= other._0;
  }
  bool operator>(const StyleFontWidth& other) const {
    return _0 > other._0;
  }
  bool operator>=(const StyleFontWidth& other) const {
    return _0 >= other._0;
  }
 SERVO_FIXED_POINT_HELPERS(StyleFontWidth, uint16_t, StyleFONT_WIDTH_FRACTION_BITS);
 bool IsNormal() const { return *this == NORMAL; }
  static const uint16_t FRACTION_BITS;
  static const uint16_t HALF;
  static const StyleFontWidth ULTRA_CONDENSED;
  static const StyleFontWidth EXTRA_CONDENSED;
  static const StyleFontWidth CONDENSED;
  static const StyleFontWidth SEMI_CONDENSED;
  static const StyleFontWidth NORMAL;
  static const StyleFontWidth SEMI_EXPANDED;
  static const StyleFontWidth EXPANDED;
  static const StyleFontWidth EXTRA_EXPANDED;
  static const StyleFontWidth ULTRA_EXPANDED;
};
/// The fraction bits, as an easy-to-access-constant.
constexpr inline const uint16_t StyleFontWidth::FRACTION_BITS = StyleFONT_WIDTH_FRACTION_BITS;
/// 0.5 in our floating point representation.
constexpr inline const uint16_t StyleFontWidth::HALF = (1 << (StyleFontWidth::FRACTION_BITS - 1));
/// The `ultra-condensed` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::ULTRA_CONDENSED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ (50 << StyleFontWidth::FRACTION_BITS)
  }
};
/// The `extra-condensed` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::EXTRA_CONDENSED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ ((62 << StyleFontWidth::FRACTION_BITS) + StyleFontWidth::HALF)
  }
};
/// The `condensed` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::CONDENSED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ (75 << StyleFontWidth::FRACTION_BITS)
  }
};
/// The `semi-condensed` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::SEMI_CONDENSED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ ((87 << StyleFontWidth::FRACTION_BITS) + StyleFontWidth::HALF)
  }
};
/// The `normal` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::NORMAL = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ (100 << StyleFontWidth::FRACTION_BITS)
  }
};
/// The `semi-expanded` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::SEMI_EXPANDED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ ((112 << StyleFontWidth::FRACTION_BITS) + StyleFontWidth::HALF)
  }
};
/// The `expanded` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::EXPANDED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ (125 << StyleFontWidth::FRACTION_BITS)
  }
};
/// The `extra-expanded` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::EXTRA_EXPANDED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ (150 << StyleFontWidth::FRACTION_BITS)
  }
};
/// The `ultra-expanded` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::ULTRA_EXPANDED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ (200 << StyleFontWidth::FRACTION_BITS)
  }
};

/// The computed representation of the above, so that Gecko and Servo can read them
/// easily.
struct StyleComputedFontWidthRange {
  StyleFontWidth _0;
  StyleFontWidth _1;

  bool operator==(const StyleComputedFontWidthRange& other) const {
    return _0 == other._0 &&
           _1 == other._1;
  }
};

/// This is an alias which is useful mostly as a cbindgen / C++ inference
/// workaround.
using StyleFontStyleFixedPoint = StyleFixedPoint<int16_t, StyleFONT_STYLE_FRACTION_BITS>;

/// The computed value of `font-style`.
///
/// - Define angle of zero degrees as `normal`
/// - Define out-of-range value 100 degrees as `italic`
/// - Other values represent `oblique <angle>`
///
struct StyleFontStyle {
  StyleFontStyleFixedPoint _0;

  bool operator==(const StyleFontStyle& other) const {
    return _0 == other._0;
  }
  bool operator<(const StyleFontStyle& other) const {
    return _0 < other._0;
  }
  bool operator<=(const StyleFontStyle& other) const {
    return _0 <= other._0;
  }
  bool operator>(const StyleFontStyle& other) const {
    return _0 > other._0;
  }
  bool operator>=(const StyleFontStyle& other) const {
    return _0 >= other._0;
  }
 SERVO_FIXED_POINT_HELPERS(StyleFontStyle, int16_t, StyleFONT_STYLE_FRACTION_BITS);
 bool IsNormal() const { return *this == NORMAL; }
 inline bool IsItalic() const;
 inline float ObliqueAngle() const;  // Not for use when IsItalic() is true
 inline float SlantAngle() const;  // Returns angle for any font-style, including
                                   // normal/italic as well as explicit oblique
  static const StyleFontStyle NORMAL;
  static const StyleFontStyle ITALIC;
  static const int16_t DEFAULT_OBLIQUE_DEGREES;
  static const StyleFontStyle OBLIQUE;
};
/// The `normal` keyword, equal to `oblique` with angle zero.
constexpr inline const StyleFontStyle StyleFontStyle::NORMAL = StyleFontStyle{
  /* ._0 = */ StyleFontStyleFixedPoint{
    /* .value = */ (0 << StyleFONT_STYLE_FRACTION_BITS)
  }
};
/// The italic keyword.
constexpr inline const StyleFontStyle StyleFontStyle::ITALIC = StyleFontStyle{
  /* ._0 = */ StyleFontStyleFixedPoint{
    /* .value = */ (100 << StyleFONT_STYLE_FRACTION_BITS)
  }
};
/// The default angle for `font-style: oblique`.
/// See also https://github.com/w3c/csswg-drafts/issues/2295
constexpr inline const int16_t StyleFontStyle::DEFAULT_OBLIQUE_DEGREES = 14;
/// The `oblique` keyword with the default degrees.
constexpr inline const StyleFontStyle StyleFontStyle::OBLIQUE = StyleFontStyle{
  /* ._0 = */ StyleFontStyleFixedPoint{
    /* .value = */ (StyleFontStyle::DEFAULT_OBLIQUE_DEGREES << StyleFONT_STYLE_FRACTION_BITS)
  }
};

/// The computed representation of the above, with angles in degrees stored as
/// signed 8.8 fixed-point values, so that Gecko and Servo can read them easily.
struct StyleComputedFontStyleRange {
  StyleFontStyle _0;
  StyleFontStyle _1;

  bool operator==(const StyleComputedFontStyleRange& other) const {
    return _0 == other._0 &&
           _1 == other._1;
  }
};

/// font-language-override can only have a single 1-4 ASCII character
/// OpenType "language system" tag, so we should be able to compute
/// it and store it as a 32-bit integer
/// (see http://www.microsoft.com/typography/otspec/languagetags.htm).
struct StyleFontLanguageOverride {
  uint32_t _0;

  bool operator==(const StyleFontLanguageOverride& other) const {
    return _0 == other._0;
  }
};

/// One contiguous range of code points.
///
/// Can not be empty. Can represent a single code point when start == end.
struct StyleUnicodeRange {
  /// Inclusive start of the range. In [0, end].
  uint32_t start;
  /// Inclusive end of the range. In [0, 0x10FFFF].
  uint32_t end;

  bool operator==(const StyleUnicodeRange& other) const {
    return start == other.start &&
           end == other.end;
  }
};

/// Flags for the @font-face tech() function, indicating font technologies
/// required by the resource.
struct StyleFontFaceSourceTechFlags {
  uint16_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleFontFaceSourceTechFlags operator~() const {
    return StyleFontFaceSourceTechFlags { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleFontFaceSourceTechFlags operator|(const StyleFontFaceSourceTechFlags& other) const {
    return StyleFontFaceSourceTechFlags { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleFontFaceSourceTechFlags& operator|=(const StyleFontFaceSourceTechFlags& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleFontFaceSourceTechFlags operator&(const StyleFontFaceSourceTechFlags& other) const {
    return StyleFontFaceSourceTechFlags { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleFontFaceSourceTechFlags& operator&=(const StyleFontFaceSourceTechFlags& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleFontFaceSourceTechFlags operator^(const StyleFontFaceSourceTechFlags& other) const {
    return StyleFontFaceSourceTechFlags { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleFontFaceSourceTechFlags& operator^=(const StyleFontFaceSourceTechFlags& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleFontFaceSourceTechFlags& other) const {
    return _0 == other._0;
  }
  inline static StyleFontFaceSourceTechFlags Empty() {
    return StyleFontFaceSourceTechFlags{0};
  }
  static const StyleFontFaceSourceTechFlags FEATURES_OPENTYPE;
  static const StyleFontFaceSourceTechFlags FEATURES_AAT;
  static const StyleFontFaceSourceTechFlags FEATURES_GRAPHITE;
  static const StyleFontFaceSourceTechFlags COLOR_COLRV0;
  static const StyleFontFaceSourceTechFlags COLOR_COLRV1;
  static const StyleFontFaceSourceTechFlags COLOR_SVG;
  static const StyleFontFaceSourceTechFlags COLOR_SBIX;
  static const StyleFontFaceSourceTechFlags COLOR_CBDT;
  static const StyleFontFaceSourceTechFlags VARIATIONS;
  static const StyleFontFaceSourceTechFlags PALETTES;
  static const StyleFontFaceSourceTechFlags INCREMENTAL;
};
/// Font requires OpenType feature support.
constexpr inline const StyleFontFaceSourceTechFlags StyleFontFaceSourceTechFlags::FEATURES_OPENTYPE = StyleFontFaceSourceTechFlags{
  /* ._0 = */ (uint16_t)(1 << 0)
};
/// Font requires Apple Advanced Typography support.
constexpr inline const StyleFontFaceSourceTechFlags StyleFontFaceSourceTechFlags::FEATURES_AAT = StyleFontFaceSourceTechFlags{
  /* ._0 = */ (uint16_t)(1 << 1)
};
/// Font requires Graphite shaping support.
constexpr inline const StyleFontFaceSourceTechFlags StyleFontFaceSourceTechFlags::FEATURES_GRAPHITE = StyleFontFaceSourceTechFlags{
  /* ._0 = */ (uint16_t)(1 << 2)
};
/// Font requires COLRv0 rendering support (simple list of colored layers).
constexpr inline const StyleFontFaceSourceTechFlags StyleFontFaceSourceTechFlags::COLOR_COLRV0 = StyleFontFaceSourceTechFlags{
  /* ._0 = */ (uint16_t)(1 << 3)
};
/// Font requires COLRv1 rendering support (graph of paint operations).
constexpr inline const StyleFontFaceSourceTechFlags StyleFontFaceSourceTechFlags::COLOR_COLRV1 = StyleFontFaceSourceTechFlags{
  /* ._0 = */ (uint16_t)(1 << 4)
};
/// Font requires SVG glyph rendering support.
constexpr inline const StyleFontFaceSourceTechFlags StyleFontFaceSourceTechFlags::COLOR_SVG = StyleFontFaceSourceTechFlags{
  /* ._0 = */ (uint16_t)(1 << 5)
};
/// Font has bitmap glyphs in 'sbix' format.
constexpr inline const StyleFontFaceSourceTechFlags StyleFontFaceSourceTechFlags::COLOR_SBIX = StyleFontFaceSourceTechFlags{
  /* ._0 = */ (uint16_t)(1 << 6)
};
/// Font has bitmap glyphs in 'CBDT' format.
constexpr inline const StyleFontFaceSourceTechFlags StyleFontFaceSourceTechFlags::COLOR_CBDT = StyleFontFaceSourceTechFlags{
  /* ._0 = */ (uint16_t)(1 << 7)
};
/// Font requires OpenType Variations support.
constexpr inline const StyleFontFaceSourceTechFlags StyleFontFaceSourceTechFlags::VARIATIONS = StyleFontFaceSourceTechFlags{
  /* ._0 = */ (uint16_t)(1 << 8)
};
/// Font requires CPAL palette selection support.
constexpr inline const StyleFontFaceSourceTechFlags StyleFontFaceSourceTechFlags::PALETTES = StyleFontFaceSourceTechFlags{
  /* ._0 = */ (uint16_t)(1 << 9)
};
/// Font requires support for incremental downloading.
constexpr inline const StyleFontFaceSourceTechFlags StyleFontFaceSourceTechFlags::INCREMENTAL = StyleFontFaceSourceTechFlags{
  /* ._0 = */ (uint16_t)(1 << 10)
};

#if defined(CBINDGEN_IS_GECKO)
/// A POD representation for Gecko. All pointers here are non-owned and as such
/// can't outlive the rule they came from, but we can't enforce that via C++.
///
/// All the strings are of course utf8.
union StyleFontFaceSourceListComponent {
  enum class Tag : uint8_t {
    Url,
    Local,
    FormatHintKeyword,
    FormatHintString,
    TechFlags,
  };

  struct Url_Body {
    Tag tag;
    const StyleCssUrl *_0;

    bool operator==(const Url_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Local_Body {
    Tag tag;
    nsAtom *_0;

    bool operator==(const Local_Body& other) const {
      return _0 == other._0;
    }
  };

  struct FormatHintKeyword_Body {
    Tag tag;
    StyleFontFaceSourceFormatKeyword _0;

    bool operator==(const FormatHintKeyword_Body& other) const {
      return _0 == other._0;
    }
  };

  struct FormatHintString_Body {
    Tag tag;
    size_t length;
    const uint8_t *utf8_bytes;

    bool operator==(const FormatHintString_Body& other) const {
      return length == other.length &&
             utf8_bytes == other.utf8_bytes;
    }
  };

  struct TechFlags_Body {
    Tag tag;
    StyleFontFaceSourceTechFlags _0;

    bool operator==(const TechFlags_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Url_Body url;
  Local_Body local;
  FormatHintKeyword_Body format_hint_keyword;
  FormatHintString_Body format_hint_string;
  TechFlags_Body tech_flags;

  static StyleFontFaceSourceListComponent Url(const StyleCssUrl *const &_0) {
    StyleFontFaceSourceListComponent result;
    ::new (&result.url._0) (const StyleCssUrl*)(_0);
    result.tag = Tag::Url;
    return result;
  }

  bool IsUrl() const {
    return tag == Tag::Url;
  }

  const StyleCssUrl*const & AsUrl() const {
    MOZ_DIAGNOSTIC_ASSERT(IsUrl());
    return url._0;
  }

  static StyleFontFaceSourceListComponent Local(nsAtom *const &_0) {
    StyleFontFaceSourceListComponent result;
    ::new (&result.local._0) (nsAtom*)(_0);
    result.tag = Tag::Local;
    return result;
  }

  bool IsLocal() const {
    return tag == Tag::Local;
  }

  nsAtom*const & AsLocal() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLocal());
    return local._0;
  }

  static StyleFontFaceSourceListComponent FormatHintKeyword(const StyleFontFaceSourceFormatKeyword &_0) {
    StyleFontFaceSourceListComponent result;
    ::new (&result.format_hint_keyword._0) (StyleFontFaceSourceFormatKeyword)(_0);
    result.tag = Tag::FormatHintKeyword;
    return result;
  }

  bool IsFormatHintKeyword() const {
    return tag == Tag::FormatHintKeyword;
  }

  const StyleFontFaceSourceFormatKeyword& AsFormatHintKeyword() const {
    MOZ_DIAGNOSTIC_ASSERT(IsFormatHintKeyword());
    return format_hint_keyword._0;
  }

  static StyleFontFaceSourceListComponent FormatHintString(const size_t &length,
                                                           const uint8_t *const &utf8_bytes) {
    StyleFontFaceSourceListComponent result;
    ::new (&result.format_hint_string.length) (size_t)(length);
    ::new (&result.format_hint_string.utf8_bytes) (const uint8_t*)(utf8_bytes);
    result.tag = Tag::FormatHintString;
    return result;
  }

  bool IsFormatHintString() const {
    return tag == Tag::FormatHintString;
  }

  const FormatHintString_Body& AsFormatHintString() const {
    MOZ_DIAGNOSTIC_ASSERT(IsFormatHintString());
    return format_hint_string;
  }

  static StyleFontFaceSourceListComponent TechFlags(const StyleFontFaceSourceTechFlags &_0) {
    StyleFontFaceSourceListComponent result;
    ::new (&result.tech_flags._0) (StyleFontFaceSourceTechFlags)(_0);
    result.tag = Tag::TechFlags;
    return result;
  }

  bool IsTechFlags() const {
    return tag == Tag::TechFlags;
  }

  const StyleFontFaceSourceTechFlags& AsTechFlags() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTechFlags());
    return tech_flags._0;
  }

  bool operator==(const StyleFontFaceSourceListComponent& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Url: return url == other.url;
      case Tag::Local: return local == other.local;
      case Tag::FormatHintKeyword: return format_hint_keyword == other.format_hint_keyword;
      case Tag::FormatHintString: return format_hint_string == other.format_hint_string;
      case Tag::TechFlags: return tech_flags == other.tech_flags;

    }
    return true;
  }

  private:
  StyleFontFaceSourceListComponent() {

  }
  public:


  ~StyleFontFaceSourceListComponent() {
    switch (tag) {
      case Tag::Url: url.~Url_Body(); break;
      case Tag::Local: local.~Local_Body(); break;
      case Tag::FormatHintKeyword: format_hint_keyword.~FormatHintKeyword_Body(); break;
      case Tag::FormatHintString: format_hint_string.~FormatHintString_Body(); break;
      case Tag::TechFlags: tech_flags.~TechFlags_Body(); break;

    }
  }

  StyleFontFaceSourceListComponent(const StyleFontFaceSourceListComponent& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Url: ::new (&url) (Url_Body)(other.url); break;
      case Tag::Local: ::new (&local) (Local_Body)(other.local); break;
      case Tag::FormatHintKeyword: ::new (&format_hint_keyword) (FormatHintKeyword_Body)(other.format_hint_keyword); break;
      case Tag::FormatHintString: ::new (&format_hint_string) (FormatHintString_Body)(other.format_hint_string); break;
      case Tag::TechFlags: ::new (&tech_flags) (TechFlags_Body)(other.tech_flags); break;

    }
  }
  StyleFontFaceSourceListComponent& operator=(const StyleFontFaceSourceListComponent& other) {
    if (this != &other) {
      this->~StyleFontFaceSourceListComponent();
      new (this) StyleFontFaceSourceListComponent(other);
    }
    return *this;
  }
};
#endif

/// A font four-character tag, represented as a u32 for convenience.
///
/// See:
///   https://drafts.csswg.org/css-fonts-4/#font-variation-settings-def
///   https://drafts.csswg.org/css-fonts-4/#descdef-font-face-font-feature-settings
using StyleFontTag = uint32_t;

/// Variation setting for a single feature, see:
///
/// https://drafts.csswg.org/css-fonts-4/#font-variation-settings-def
template<typename Number>
struct StyleVariationValue {
  /// A four-character tag, packed into a u32 (one byte per character).
  StyleFontTag tag;
  /// The actual value.
  Number value;

  bool operator==(const StyleVariationValue& other) const {
    return tag == other.tag &&
           value == other.value;
  }
};

/// https://drafts.csswg.org/css-fonts-4/#feature-tag-value
template<typename Integer>
struct StyleFeatureTagValue {
  /// A four-character tag, packed into a u32 (one byte per character).
  StyleFontTag tag;
  /// The actual value.
  Integer value;

  bool operator==(const StyleFeatureTagValue& other) const {
    return tag == other.tag &&
           value == other.value;
  }
};

/// <https://drafts.csswg.org/css-values-4/#custom-idents>
struct StyleCustomIdent {
  StyleAtom _0;

  bool operator==(const StyleCustomIdent& other) const {
    return _0 == other._0;
  }
  inline nsAtom* AsAtom() const;
};

/// <https://drafts.csswg.org/css-counter-styles/#typedef-symbol>
union StyleSymbol {
  enum class Tag : uint8_t {
    /// <string>
    String,
    /// <custom-ident>
    Ident,
  };

  struct String_Body {
    Tag tag;
    StyleOwnedStr _0;

    bool operator==(const String_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Ident_Body {
    Tag tag;
    StyleCustomIdent _0;

    bool operator==(const Ident_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  String_Body string;
  Ident_Body ident;

  static StyleSymbol String(const StyleOwnedStr &_0) {
    StyleSymbol result;
    ::new (&result.string._0) (StyleOwnedStr)(_0);
    result.tag = Tag::String;
    return result;
  }

  bool IsString() const {
    return tag == Tag::String;
  }

  const StyleOwnedStr& AsString() const {
    MOZ_DIAGNOSTIC_ASSERT(IsString());
    return string._0;
  }

  static StyleSymbol Ident(const StyleCustomIdent &_0) {
    StyleSymbol result;
    ::new (&result.ident._0) (StyleCustomIdent)(_0);
    result.tag = Tag::Ident;
    return result;
  }

  bool IsIdent() const {
    return tag == Tag::Ident;
  }

  const StyleCustomIdent& AsIdent() const {
    MOZ_DIAGNOSTIC_ASSERT(IsIdent());
    return ident._0;
  }

  bool operator==(const StyleSymbol& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::String: return string == other.string;
      case Tag::Ident: return ident == other.ident;

    }
    return true;
  }

  private:
  StyleSymbol() {

  }
  public:


  ~StyleSymbol() {
    switch (tag) {
      case Tag::String: string.~String_Body(); break;
      case Tag::Ident: ident.~Ident_Body(); break;

    }
  }

  StyleSymbol(const StyleSymbol& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::String: ::new (&string) (String_Body)(other.string); break;
      case Tag::Ident: ::new (&ident) (Ident_Body)(other.ident); break;

    }
  }
  StyleSymbol& operator=(const StyleSymbol& other) {
    if (this != &other) {
      this->~StyleSymbol();
      new (this) StyleSymbol(other);
    }
    return *this;
  }
};

struct StyleAdditiveSymbol {
  int32_t weight;
  nsString symbol;

  bool operator==(const StyleAdditiveSymbol& other) const {
    return weight == other.weight &&
           symbol == other.symbol;
  }
};

struct StyleCounterSpeakAs {
  enum class Tag : uint8_t {
    None,
    Auto,
    Bullets,
    Numbers,
    Words,
    Ident,
  };

  struct StyleIdent_Body {
    nsAtom *_0;

    bool operator==(const StyleIdent_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleIdent_Body ident;
  };

  static StyleCounterSpeakAs None() {
    StyleCounterSpeakAs result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleCounterSpeakAs Auto() {
    StyleCounterSpeakAs result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleCounterSpeakAs Bullets() {
    StyleCounterSpeakAs result;
    result.tag = Tag::Bullets;
    return result;
  }

  bool IsBullets() const {
    return tag == Tag::Bullets;
  }

  static StyleCounterSpeakAs Numbers() {
    StyleCounterSpeakAs result;
    result.tag = Tag::Numbers;
    return result;
  }

  bool IsNumbers() const {
    return tag == Tag::Numbers;
  }

  static StyleCounterSpeakAs Words() {
    StyleCounterSpeakAs result;
    result.tag = Tag::Words;
    return result;
  }

  bool IsWords() const {
    return tag == Tag::Words;
  }

  static StyleCounterSpeakAs Ident(nsAtom *const &_0) {
    StyleCounterSpeakAs result;
    ::new (&result.ident._0) (nsAtom*)(_0);
    result.tag = Tag::Ident;
    return result;
  }

  bool IsIdent() const {
    return tag == Tag::Ident;
  }

  nsAtom*const & AsIdent() const {
    MOZ_DIAGNOSTIC_ASSERT(IsIdent());
    return ident._0;
  }

  bool operator==(const StyleCounterSpeakAs& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Ident: return ident == other.ident;
      default: break;
    }
    return true;
  }

  private:
  StyleCounterSpeakAs() {

  }
  public:


  ~StyleCounterSpeakAs() {
    switch (tag) {
      case Tag::Ident: ident.~StyleIdent_Body(); break;
      default: break;
    }
  }

  StyleCounterSpeakAs(const StyleCounterSpeakAs& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Ident: ::new (&ident) (StyleIdent_Body)(other.ident); break;
      default: break;
    }
  }
  StyleCounterSpeakAs& operator=(const StyleCounterSpeakAs& other) {
    if (this != &other) {
      this->~StyleCounterSpeakAs();
      new (this) StyleCounterSpeakAs(other);
    }
    return *this;
  }
};

/// Bit-flags for pseudo-class. This should only be used for querying if a
/// page-rule applies.
///
/// https://drafts.csswg.org/css-page-3/#page-selectors
struct StylePagePseudoClassFlags {
  uint8_t bits;

  constexpr explicit operator bool() const {
    return !!bits;
  }
  constexpr StylePagePseudoClassFlags operator~() const {
    return StylePagePseudoClassFlags { static_cast<decltype(bits)>(~bits) };
  }
  constexpr StylePagePseudoClassFlags operator|(const StylePagePseudoClassFlags& other) const {
    return StylePagePseudoClassFlags { static_cast<decltype(bits)>(this->bits | other.bits) };
  }
  StylePagePseudoClassFlags& operator|=(const StylePagePseudoClassFlags& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StylePagePseudoClassFlags operator&(const StylePagePseudoClassFlags& other) const {
    return StylePagePseudoClassFlags { static_cast<decltype(bits)>(this->bits & other.bits) };
  }
  StylePagePseudoClassFlags& operator&=(const StylePagePseudoClassFlags& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StylePagePseudoClassFlags operator^(const StylePagePseudoClassFlags& other) const {
    return StylePagePseudoClassFlags { static_cast<decltype(bits)>(this->bits ^ other.bits) };
  }
  StylePagePseudoClassFlags& operator^=(const StylePagePseudoClassFlags& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StylePagePseudoClassFlags& other) const {
    return bits == other.bits;
  }
  static const StylePagePseudoClassFlags NONE;
  static const StylePagePseudoClassFlags FIRST;
  static const StylePagePseudoClassFlags BLANK;
  static const StylePagePseudoClassFlags LEFT;
  static const StylePagePseudoClassFlags RIGHT;
};
/// No pseudo-classes
constexpr inline const StylePagePseudoClassFlags StylePagePseudoClassFlags::NONE = StylePagePseudoClassFlags{
  /* .bits = */ (uint8_t)0
};
/// Flag for PagePseudoClass::First
constexpr inline const StylePagePseudoClassFlags StylePagePseudoClassFlags::FIRST = StylePagePseudoClassFlags{
  /* .bits = */ (uint8_t)(1 << 0)
};
/// Flag for PagePseudoClass::Blank
constexpr inline const StylePagePseudoClassFlags StylePagePseudoClassFlags::BLANK = StylePagePseudoClassFlags{
  /* .bits = */ (uint8_t)(1 << 1)
};
/// Flag for PagePseudoClass::Left
constexpr inline const StylePagePseudoClassFlags StylePagePseudoClassFlags::LEFT = StylePagePseudoClassFlags{
  /* .bits = */ (uint8_t)(1 << 2)
};
/// Flag for PagePseudoClass::Right
constexpr inline const StylePagePseudoClassFlags StylePagePseudoClassFlags::RIGHT = StylePagePseudoClassFlags{
  /* .bits = */ (uint8_t)(1 << 3)
};

/// Changes for the automatically-generated position option.
/// Note that this is order-dependent - e.g. `flip-start flip-inline` != `flip-inline flip-start`.
///
/// https://drafts.csswg.org/css-anchor-position-1/#typedef-position-try-fallbacks-try-tactic
using StylePositionTryFallbacksTryTactic = CopyableTArray<StylePositionTryFallbacksTryTacticKeyword>;

/// https://drafts.csswg.org/css-anchor-position-1/#propdef-position-try-fallbacks
/// <dashed-ident> || <try-tactic>
struct StyleDashedIdentAndOrTryTactic {
  /// `<dashed-ident>`
  StyleDashedIdent ident;
  /// `<try-tactic>`
  StylePositionTryFallbacksTryTactic try_tactic;

  bool operator==(const StyleDashedIdentAndOrTryTactic& other) const {
    return ident == other.ident &&
           try_tactic == other.try_tactic;
  }
};

/// https://drafts.csswg.org/css-anchor-position-1/#propdef-position-area
struct StylePositionArea {
  /// First keyword, if any.
  StylePositionAreaKeyword first;
  /// Second keyword, if any.
  StylePositionAreaKeyword second;

  bool operator==(const StylePositionArea& other) const {
    return first == other.first &&
           second == other.second;
  }
  inline bool IsNone() const;
  constexpr StylePositionArea()
    : first(StylePositionAreaKeyword::None),
      second(StylePositionAreaKeyword::None)
  {}
};

/// https://drafts.csswg.org/css-anchor-position-1/#propdef-position-try-fallbacks
/// [ [<dashed-ident> || <try-tactic>] | <'position-area'> ]
union StylePositionTryFallbacksItem {
  enum class Tag : uint8_t {
    /// `<dashed-ident> || <try-tactic>`
    IdentAndOrTactic,
    /// `<position-area>`
    PositionArea,
  };

  struct IdentAndOrTactic_Body {
    Tag tag;
    StyleDashedIdentAndOrTryTactic _0;

    bool operator==(const IdentAndOrTactic_Body& other) const {
      return _0 == other._0;
    }
  };

  struct PositionArea_Body {
    Tag tag;
    StylePositionArea _0;

    bool operator==(const PositionArea_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  IdentAndOrTactic_Body ident_and_or_tactic;
  PositionArea_Body position_area;

  static StylePositionTryFallbacksItem IdentAndOrTactic(const StyleDashedIdentAndOrTryTactic &_0) {
    StylePositionTryFallbacksItem result;
    ::new (&result.ident_and_or_tactic._0) (StyleDashedIdentAndOrTryTactic)(_0);
    result.tag = Tag::IdentAndOrTactic;
    return result;
  }

  bool IsIdentAndOrTactic() const {
    return tag == Tag::IdentAndOrTactic;
  }

  const StyleDashedIdentAndOrTryTactic& AsIdentAndOrTactic() const {
    MOZ_DIAGNOSTIC_ASSERT(IsIdentAndOrTactic());
    return ident_and_or_tactic._0;
  }

  static StylePositionTryFallbacksItem PositionArea(const StylePositionArea &_0) {
    StylePositionTryFallbacksItem result;
    ::new (&result.position_area._0) (StylePositionArea)(_0);
    result.tag = Tag::PositionArea;
    return result;
  }

  bool IsPositionArea() const {
    return tag == Tag::PositionArea;
  }

  const StylePositionArea& AsPositionArea() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPositionArea());
    return position_area._0;
  }

  bool operator==(const StylePositionTryFallbacksItem& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::IdentAndOrTactic: return ident_and_or_tactic == other.ident_and_or_tactic;
      case Tag::PositionArea: return position_area == other.position_area;

    }
    return true;
  }

  private:
  StylePositionTryFallbacksItem() {

  }
  public:


  ~StylePositionTryFallbacksItem() {
    switch (tag) {
      case Tag::IdentAndOrTactic: ident_and_or_tactic.~IdentAndOrTactic_Body(); break;
      case Tag::PositionArea: position_area.~PositionArea_Body(); break;

    }
  }

  StylePositionTryFallbacksItem(const StylePositionTryFallbacksItem& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::IdentAndOrTactic: ::new (&ident_and_or_tactic) (IdentAndOrTactic_Body)(other.ident_and_or_tactic); break;
      case Tag::PositionArea: ::new (&position_area) (PositionArea_Body)(other.position_area); break;

    }
  }
  StylePositionTryFallbacksItem& operator=(const StylePositionTryFallbacksItem& other) {
    if (this != &other) {
      this->~StylePositionTryFallbacksItem();
      new (this) StylePositionTryFallbacksItem(other);
    }
    return *this;
  }
};

struct StyleMatchingDeclarationBlock {
  const StyleLockedDeclarationBlock *block;
  StyleMatchingDeclarationBlockOrigin origin;

  bool operator==(const StyleMatchingDeclarationBlock& other) const {
    return block == other.block &&
           origin == other.origin;
  }
};

/// The mode to use when parsing values.
struct StyleParsingMode {
  uint8_t bits;

  constexpr explicit operator bool() const {
    return !!bits;
  }
  constexpr StyleParsingMode operator~() const {
    return StyleParsingMode { static_cast<decltype(bits)>(~bits) };
  }
  constexpr StyleParsingMode operator|(const StyleParsingMode& other) const {
    return StyleParsingMode { static_cast<decltype(bits)>(this->bits | other.bits) };
  }
  StyleParsingMode& operator|=(const StyleParsingMode& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleParsingMode operator&(const StyleParsingMode& other) const {
    return StyleParsingMode { static_cast<decltype(bits)>(this->bits & other.bits) };
  }
  StyleParsingMode& operator&=(const StyleParsingMode& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleParsingMode operator^(const StyleParsingMode& other) const {
    return StyleParsingMode { static_cast<decltype(bits)>(this->bits ^ other.bits) };
  }
  StyleParsingMode& operator^=(const StyleParsingMode& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleParsingMode& other) const {
    return bits == other.bits;
  }
  static const StyleParsingMode DEFAULT;
  static const StyleParsingMode ALLOW_UNITLESS_LENGTH;
  static const StyleParsingMode ALLOW_ALL_NUMERIC_VALUES;
  static const StyleParsingMode DISALLOW_COMPUTATIONALLY_DEPENDENT;
  static const StyleParsingMode DISALLOW_UNITLESS_ZERO_LENGTH;
  static const StyleParsingMode MEDIA_QUERY_CONDITION;
};
/// In CSS; lengths must have units, except for zero values, where the unit can be omitted.
/// <https://www.w3.org/TR/css3-values/#lengths>
constexpr inline const StyleParsingMode StyleParsingMode::DEFAULT = StyleParsingMode{
  /* .bits = */ (uint8_t)0
};
/// In SVG; a coordinate or length value without a unit identifier (e.g., "25") is assumed
/// to be in user units (px).
/// <https://www.w3.org/TR/SVG/coords.html#Units>
constexpr inline const StyleParsingMode StyleParsingMode::ALLOW_UNITLESS_LENGTH = StyleParsingMode{
  /* .bits = */ (uint8_t)1
};
/// In SVG; out-of-range values are not treated as an error in parsing.
/// <https://www.w3.org/TR/SVG/implnote.html#RangeClamping>
constexpr inline const StyleParsingMode StyleParsingMode::ALLOW_ALL_NUMERIC_VALUES = StyleParsingMode{
  /* .bits = */ (uint8_t)(1 << 1)
};
/// In CSS Properties and Values, the initial value must be computationally
/// independent.
/// <https://drafts.css-houdini.org/css-properties-values-api-1/#ref-for-computationally-independent%E2%91%A0>
constexpr inline const StyleParsingMode StyleParsingMode::DISALLOW_COMPUTATIONALLY_DEPENDENT = StyleParsingMode{
  /* .bits = */ (uint8_t)(1 << 2)
};
/// In Typed OM; unitless zero must not be interpreted as a length.
constexpr inline const StyleParsingMode StyleParsingMode::DISALLOW_UNITLESS_ZERO_LENGTH = StyleParsingMode{
  /* .bits = */ (uint8_t)(1 << 3)
};
/// Media query conditions in the preludes for @media, @custom-media, and @import.
/// <https://drafts.csswg.org/mediaqueries/>
constexpr inline const StyleParsingMode StyleParsingMode::MEDIA_QUERY_CONDITION = StyleParsingMode{
  /* .bits = */ (uint8_t)(1 << 4)
};

/// A `<length-percentage> | auto` value.
template<typename LengthPercent>
struct StyleGenericLengthPercentageOrAuto {
  enum class Tag : uint8_t {
    LengthPercentage,
    Auto,
  };

  struct StyleLengthPercentage_Body {
    LengthPercent _0;

    bool operator==(const StyleLengthPercentage_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleLengthPercentage_Body length_percentage;
  };

  static StyleGenericLengthPercentageOrAuto LengthPercentage(const LengthPercent &_0) {
    StyleGenericLengthPercentageOrAuto result;
    ::new (&result.length_percentage._0) (LengthPercent)(_0);
    result.tag = Tag::LengthPercentage;
    return result;
  }

  bool IsLengthPercentage() const {
    return tag == Tag::LengthPercentage;
  }

  const LengthPercent& AsLengthPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLengthPercentage());
    return length_percentage._0;
  }

  static StyleGenericLengthPercentageOrAuto Auto() {
    StyleGenericLengthPercentageOrAuto result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  bool operator==(const StyleGenericLengthPercentageOrAuto& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::LengthPercentage: return length_percentage == other.length_percentage;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericLengthPercentageOrAuto() {

  }
  public:


  ~StyleGenericLengthPercentageOrAuto() {
    switch (tag) {
      case Tag::LengthPercentage: length_percentage.~StyleLengthPercentage_Body(); break;
      default: break;
    }
  }

  StyleGenericLengthPercentageOrAuto(const StyleGenericLengthPercentageOrAuto& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::LengthPercentage: ::new (&length_percentage) (StyleLengthPercentage_Body)(other.length_percentage); break;
      default: break;
    }
  }
  StyleGenericLengthPercentageOrAuto& operator=(const StyleGenericLengthPercentageOrAuto& other) {
    if (this != &other) {
      this->~StyleGenericLengthPercentageOrAuto();
      new (this) StyleGenericLengthPercentageOrAuto(other);
    }
    return *this;
  }
  inline bool ConvertsToLength() const;
  inline nscoord ToLength() const;
  inline bool ConvertsToPercentage() const;
  inline float ToPercentage() const;
  inline bool HasPercent() const;
  inline bool HasLengthAndPercentage() const;

  // Just some convenient aliases for LengthOrAuto, to avoid confusing naming.
  inline bool IsLength() const;
  inline const StyleLength& AsLength() const;

  static inline StyleGenericLengthPercentageOrAuto Zero();
};

/// A generic value for the `[ [ auto | <length-percentage> ]{1,2} ]`.
///
/// https://drafts.csswg.org/scroll-animations-1/#view-timeline-inset
template<typename LengthPercent>
struct StyleGenericViewTimelineInset {
  /// The start inset in the relevant axis.
  StyleGenericLengthPercentageOrAuto<LengthPercent> start;
  /// The end inset.
  StyleGenericLengthPercentageOrAuto<LengthPercent> end;

  bool operator==(const StyleGenericViewTimelineInset& other) const {
    return start == other.start &&
           end == other.end;
  }
 public:
  inline StyleGenericViewTimelineInset();
};

/// A computed value for the `view-timeline-inset` property.
using StyleViewTimelineInset = StyleGenericViewTimelineInset<StyleLengthPercentage>;

using StyleValueType = StyleCSSFloat;

/// a single entry in a piecewise linear function.
struct StylePiecewiseLinearFunctionEntry {
  StyleValueType x;
  StyleValueType y;

  bool operator==(const StylePiecewiseLinearFunctionEntry& other) const {
    return x == other.x &&
           y == other.y;
  }
};

/// Representation of a piecewise linear function, a series of linear functions.
struct StylePiecewiseLinearFunction {
  StyleArcSlice<StylePiecewiseLinearFunctionEntry> entries;

  bool operator==(const StylePiecewiseLinearFunction& other) const {
    return entries == other.entries;
  }
};

/// A generic easing function.
template<typename Integer, typename Number, typename LinearStops>
struct StyleTimingFunction {
  enum class Tag : uint8_t {
    /// `linear | ease | ease-in | ease-out | ease-in-out`
    Keyword,
    /// `cubic-bezier(<number>, <number>, <number>, <number>)`
    CubicBezier,
    /// `step-start | step-end | steps(<integer>, [ <step-position> ]?)`
    /// `<step-position> = jump-start | jump-end | jump-none | jump-both | start | end`
    Steps,
    /// linear([<linear-stop>]#)
    /// <linear-stop> = <output> && <linear-stop-length>?
    /// <linear-stop-length> = <percentage>{1, 2}
    LinearFunction,
  };

  struct StyleKeyword_Body {
    StyleTimingKeyword _0;

    bool operator==(const StyleKeyword_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleCubicBezier_Body {
    Number x1;
    Number y1;
    Number x2;
    Number y2;

    bool operator==(const StyleCubicBezier_Body& other) const {
      return x1 == other.x1 &&
             y1 == other.y1 &&
             x2 == other.x2 &&
             y2 == other.y2;
    }
  };

  struct StyleSteps_Body {
    Integer _0;
    StyleStepPosition _1;

    bool operator==(const StyleSteps_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct StyleLinearFunction_Body {
    LinearStops _0;

    bool operator==(const StyleLinearFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleKeyword_Body keyword;
    StyleCubicBezier_Body cubic_bezier;
    StyleSteps_Body steps;
    StyleLinearFunction_Body linear_function;
  };

  static StyleTimingFunction Keyword(const StyleTimingKeyword &_0) {
    StyleTimingFunction result;
    ::new (&result.keyword._0) (StyleTimingKeyword)(_0);
    result.tag = Tag::Keyword;
    return result;
  }

  bool IsKeyword() const {
    return tag == Tag::Keyword;
  }

  const StyleTimingKeyword& AsKeyword() const {
    MOZ_DIAGNOSTIC_ASSERT(IsKeyword());
    return keyword._0;
  }

  static StyleTimingFunction CubicBezier(const Number &x1,
                                         const Number &y1,
                                         const Number &x2,
                                         const Number &y2) {
    StyleTimingFunction result;
    ::new (&result.cubic_bezier.x1) (Number)(x1);
    ::new (&result.cubic_bezier.y1) (Number)(y1);
    ::new (&result.cubic_bezier.x2) (Number)(x2);
    ::new (&result.cubic_bezier.y2) (Number)(y2);
    result.tag = Tag::CubicBezier;
    return result;
  }

  bool IsCubicBezier() const {
    return tag == Tag::CubicBezier;
  }

  const StyleCubicBezier_Body& AsCubicBezier() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCubicBezier());
    return cubic_bezier;
  }

  static StyleTimingFunction Steps(const Integer &_0,
                                   const StyleStepPosition &_1) {
    StyleTimingFunction result;
    ::new (&result.steps._0) (Integer)(_0);
    ::new (&result.steps._1) (StyleStepPosition)(_1);
    result.tag = Tag::Steps;
    return result;
  }

  bool IsSteps() const {
    return tag == Tag::Steps;
  }

  const StyleSteps_Body& AsSteps() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSteps());
    return steps;
  }

  static StyleTimingFunction LinearFunction(const LinearStops &_0) {
    StyleTimingFunction result;
    ::new (&result.linear_function._0) (LinearStops)(_0);
    result.tag = Tag::LinearFunction;
    return result;
  }

  bool IsLinearFunction() const {
    return tag == Tag::LinearFunction;
  }

  const LinearStops& AsLinearFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLinearFunction());
    return linear_function._0;
  }

  bool operator==(const StyleTimingFunction& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Keyword: return keyword == other.keyword;
      case Tag::CubicBezier: return cubic_bezier == other.cubic_bezier;
      case Tag::Steps: return steps == other.steps;
      case Tag::LinearFunction: return linear_function == other.linear_function;

    }
    return true;
  }

  private:
  StyleTimingFunction() {

  }
  public:


  ~StyleTimingFunction() {
    switch (tag) {
      case Tag::Keyword: keyword.~StyleKeyword_Body(); break;
      case Tag::CubicBezier: cubic_bezier.~StyleCubicBezier_Body(); break;
      case Tag::Steps: steps.~StyleSteps_Body(); break;
      case Tag::LinearFunction: linear_function.~StyleLinearFunction_Body(); break;

    }
  }

  StyleTimingFunction(const StyleTimingFunction& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Keyword: ::new (&keyword) (StyleKeyword_Body)(other.keyword); break;
      case Tag::CubicBezier: ::new (&cubic_bezier) (StyleCubicBezier_Body)(other.cubic_bezier); break;
      case Tag::Steps: ::new (&steps) (StyleSteps_Body)(other.steps); break;
      case Tag::LinearFunction: ::new (&linear_function) (StyleLinearFunction_Body)(other.linear_function); break;

    }
  }
  StyleTimingFunction& operator=(const StyleTimingFunction& other) {
    if (this != &other) {
      this->~StyleTimingFunction();
      new (this) StyleTimingFunction(other);
    }
    return *this;
  }
 public:
  bool IsLinearKeyword() const { return IsKeyword() && AsKeyword() == StyleTimingKeyword::Linear; }
  static StyleTimingFunction LinearKeyword() { return Keyword(StyleTimingKeyword::Linear); }

  inline double At(double, bool aBeforeFlag) const;
  inline void AppendToString(nsACString&) const;

  inline static double GetPortion(const Maybe<StyleTimingFunction>&, double, bool aBeforeFlag);
};

/// A computed timing function.
using StyleComputedTimingFunction = StyleTimingFunction<StyleInteger, StyleNumber, StylePiecewiseLinearFunction>;

/// An unsupported property value used by Typed OM.
///
/// This corresponds to `CSSUnsupportedValue` in the Typed OM specification.
/// The value is represented by a `Strong<LockedDeclarationBlock>` so the full
/// declaration block can be transferred across the Rust <-> C++ boundary and
/// associated with a specific property.
struct StyleUnsupportedValue {
  StyleStrong<StyleLockedDeclarationBlock> _0;

  bool operator==(const StyleUnsupportedValue& other) const {
    return _0 == other._0;
  }
};

#if defined(CBINDGEN_IS_GECKO)
/// String type that coerces to CssStringWriter, used when serialization code
/// needs to allocate a temporary string. In Gecko, this is backed by
/// nsCString, which allows the result to be passed directly to C++ without
/// conversion or copying. This makes it suitable not only for temporary
/// serialization but also for values that need to cross the Rust/C++ boundary.
using StyleCssString = nsCString;
#endif

#if defined(CBINDGEN_IS_SERVO)
/// String. The comments for the Gecko types explain the need for this abstraction.
using StyleCssString = StyleString;
#endif

/// A variable reference inside an unparsed Typed OM value.
///
/// This corresponds to `CSSVariableReferenceValue` in the Typed OM
/// specification.
struct StyleVariableReferenceValue {
  /// The referenced custom property name.
  ///
  /// This corresponds to the `variable` attribute of
  /// `CSSVariableReferenceValue`.
  StyleCssString variable;
  /// The fallback value, if present.
  ///
  /// This corresponds to the `fallback` attribute of
  /// `CSSVariableReferenceValue`. When `has_fallback` is false, this value
  /// must be ignored. When `has_fallback` is true, this contains the
  /// fallback tokens (which may be empty).
  StyleUnparsedValue fallback;
  /// Whether a fallback was explicitly provided.
  ///
  /// This is needed to distinguish between the absence of a fallback
  /// (`var(--a)`) and an explicitly empty fallback (`var(--a,)`), which are
  /// observable via Typed OM.
  bool has_fallback;

  bool operator==(const StyleVariableReferenceValue& other) const {
    return variable == other.variable &&
           fallback == other.fallback &&
           has_fallback == other.has_fallback;
  }
};

/// A single segment of an unparsed Typed OM value.
///
/// This corresponds to the `CSSUnparsedSegment` union in the Typed OM
/// specification. Unparsed values are represented as a list of string
/// fragments and variable references.
struct StyleUnparsedSegment {
  enum class Tag {
    /// A string fragment.
    ///
    /// This corresponds to the string branch of `CSSUnparsedSegment` and is
    /// used for the non-variable parts of a `CSSUnparsedValue`.
    String,
    /// A `var()` reference segment.
    ///
    /// This corresponds to `CSSVariableReferenceValue` in the Typed OM
    /// specification.
    VariableReference,
  };

  struct StyleString_Body {
    StyleCssString _0;

    bool operator==(const StyleString_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleVariableReference_Body {
    StyleVariableReferenceValue _0;

    bool operator==(const StyleVariableReference_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleString_Body string;
    StyleVariableReference_Body variable_reference;
  };

  static StyleUnparsedSegment String(const StyleCssString &_0) {
    StyleUnparsedSegment result;
    ::new (&result.string._0) (StyleCssString)(_0);
    result.tag = Tag::String;
    return result;
  }

  bool IsString() const {
    return tag == Tag::String;
  }

  const StyleCssString& AsString() const {
    MOZ_DIAGNOSTIC_ASSERT(IsString());
    return string._0;
  }

  static StyleUnparsedSegment VariableReference(const StyleVariableReferenceValue &_0) {
    StyleUnparsedSegment result;
    ::new (&result.variable_reference._0) (StyleVariableReferenceValue)(_0);
    result.tag = Tag::VariableReference;
    return result;
  }

  bool IsVariableReference() const {
    return tag == Tag::VariableReference;
  }

  const StyleVariableReferenceValue& AsVariableReference() const {
    MOZ_DIAGNOSTIC_ASSERT(IsVariableReference());
    return variable_reference._0;
  }

  bool operator==(const StyleUnparsedSegment& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::String: return string == other.string;
      case Tag::VariableReference: return variable_reference == other.variable_reference;

    }
    return true;
  }

  private:
  StyleUnparsedSegment() {

  }
  public:


  ~StyleUnparsedSegment() {
    switch (tag) {
      case Tag::String: string.~StyleString_Body(); break;
      case Tag::VariableReference: variable_reference.~StyleVariableReference_Body(); break;

    }
  }

  StyleUnparsedSegment(const StyleUnparsedSegment& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::String: ::new (&string) (StyleString_Body)(other.string); break;
      case Tag::VariableReference: ::new (&variable_reference) (StyleVariableReference_Body)(other.variable_reference); break;

    }
  }
  StyleUnparsedSegment& operator=(const StyleUnparsedSegment& other) {
    if (this != &other) {
      this->~StyleUnparsedSegment();
      new (this) StyleUnparsedSegment(other);
    }
    return *this;
  }
};

/// An unparsed value used by the Typed OM.
///
/// This corresponds to `CSSUnparsedValue` in the Typed OM specification. It
/// is used for values that cannot be reified into a more specific
/// property-agnostic representation and therefore need to preserve their
/// token-like structure as a sequence of string fragments and variable
/// references.
///
/// The underlying list of segments corresponds to the `[[tokens]]` internal
/// slot of `CSSUnparsedValue`.
///
/// This is represented as a type alias over `ThinVec<UnparsedSegment>` rather
/// than a dedicated struct. This avoids the need for additional wrapper types
/// when embedding unparsed values within other structures, while still
/// allowing recursive representations via the segment list.
using StyleUnparsedValue = CopyableTArray<StyleUnparsedSegment>;

/// A keyword value used by the Typed OM.
///
/// This corresponds to `CSSKeywordValue` in the Typed OM specification.
/// The keyword is stored as a `CssString` so it can be represented and
/// transferred independently of any specific property (e.g. `"none"`,
/// `"block"`, `"thin"`).
struct StyleKeywordValue {
  StyleCssString _0;

  bool operator==(const StyleKeywordValue& other) const {
    return _0 == other._0;
  }
};

/// https://drafts.css-houdini.org/css-typed-om-1/#numeric-typing
///
/// The spec models the per-base-type exponents as an ordered map keyed by base
/// type. We use a fixed-size array indexed by `NumericBaseType` instead. A
/// missing entry in the spec's map and a zero entry are observably equivalent
/// for every operation the spec defines (comparisons and iteration only
/// consider non-zero entries), so the array representation is simpler, avoids
/// allocations, and produces the same results.
///
/// `non_zero_count` and `non_zero_except_percent_count` are derived fields
/// maintained in sync with `exponents`, allowing O(1) type compatibility
/// checks. They fit without padding into the 2 bytes following `percent_hint`,
/// so the struct remains 32 bytes.
struct StyleNumericType {
  int32_t exponents[StyleNUMERIC_BASE_TYPE_COUNT];
  StyleOptional<StyleNumericBaseType> percent_hint;
  uint8_t non_zero_count;
  uint8_t non_zero_except_percent_count;
  static_assert(static_cast<size_t>(StyleNumericBaseType::Percent) + 1 ==
                StyleNUMERIC_BASE_TYPE_COUNT);

  inline StyleNumericType();

 private:
  inline static StyleNumericType Empty();

  // Keep in sync with NumericType::with_base_type() in Stylo.
  // This is a manual C++ duplicate to avoid FFI calls.
  inline static StyleNumericType WithBaseType(StyleNumericBaseType aBaseType);

 public:
  inline static StyleNumericType Number();
  inline static StyleNumericType Percent();
  inline static StyleNumericType Length();
  inline static StyleNumericType Angle();
  inline static StyleNumericType Time();
  inline static StyleNumericType Frequency();
  inline static StyleNumericType Resolution();
  inline static StyleNumericType Flex();

  inline int32_t Exponent(StyleNumericBaseType aBaseType) const;

  inline bool MatchesLength() const;
  inline bool MatchesAngle() const;
  inline bool MatchesLengthPercentage() const;
  inline bool MatchesNumber() const;

  inline bool operator==(const StyleNumericType& aOther) const;
};

/// A single numeric value with an associated unit.
///
/// This corresponds to `CSSUnitValue` in the Typed OM specification. The
/// numeric component is stored separately from the textual unit identifier.
struct StyleUnitValue {
  /// The numeric type associated with this value.
  StyleNumericType numeric_type;
  /// The numeric component of the value.
  float value;
  /// The textual unit string (e.g. `"px"`, `"em"`, `"%"`, `"deg"`).
  StyleCssString unit;

  bool operator==(const StyleUnitValue& other) const {
    return numeric_type == other.numeric_type &&
           value == other.value &&
           unit == other.unit;
  }
};

/// A sum of numeric values.
///
/// This corresponds to `CSSMathSum` in the Typed OM specification. A sum
/// value represents an expression such as `10px + 2em`. Each entry is itself
/// a `NumericValue`, allowing nested sums if needed.
struct StyleMathSum {
  /// The numeric type associated with this sum.
  StyleNumericType numeric_type;
  /// The list of numeric terms that make up the sum.
  CopyableTArray<StyleNumericValue> values;

  bool operator==(const StyleMathSum& other) const {
    return numeric_type == other.numeric_type &&
           values == other.values;
  }
};

/// A product of numeric values.
///
/// This corresponds to `CSSMathProduct` in the Typed OM specification. A
/// product value represents an expression such as `10px * 2`. Each entry is
/// itself a `NumericValue`, allowing nested math expressions if needed.
struct StyleMathProduct {
  /// The numeric type associated with this product.
  StyleNumericType numeric_type;
  /// The list of numeric terms that make up the product.
  CopyableTArray<StyleNumericValue> values;

  bool operator==(const StyleMathProduct& other) const {
    return numeric_type == other.numeric_type &&
           values == other.values;
  }
};

/// A negated numeric value.
///
/// This corresponds to `CSSMathNegate` in the Typed OM specification. A negate
/// expression represents constructs such as `-10px` or `-(10px + 2em)`.
struct StyleMathNegate {
  /// The numeric type associated with this negate.
  StyleNumericType numeric_type;
  /// The numeric value being negated.
  StyleBox<StyleNumericValue> value;

  bool operator==(const StyleMathNegate& other) const {
    return numeric_type == other.numeric_type &&
           value == other.value;
  }
};

/// An inverted numeric value.
///
/// This corresponds to `CSSMathInvert` in the Typed OM specification. An
/// invert expression represents constructs such as `1 / 2`, `1 / 10px`, or
/// more generally the reciprocal of another numeric value.
struct StyleMathInvert {
  /// The numeric type associated with this invert.
  StyleNumericType numeric_type;
  /// The numeric value being inverted.
  StyleBox<StyleNumericValue> value;

  bool operator==(const StyleMathInvert& other) const {
    return numeric_type == other.numeric_type &&
           value == other.value;
  }
};

/// A minimum expression over numeric values.
///
/// This corresponds to `CSSMathMin` in the Typed OM specification. A minimum
/// expression represents constructs such as `min(10px, 20%)`. Each entry is
/// itself a `NumericValue`, allowing nested math expressions if needed.
struct StyleMathMin {
  /// The numeric type associated with this min.
  StyleNumericType numeric_type;
  /// The list of numeric terms that make up the min.
  CopyableTArray<StyleNumericValue> values;

  bool operator==(const StyleMathMin& other) const {
    return numeric_type == other.numeric_type &&
           values == other.values;
  }
};

/// A maximum expression over numeric values.
///
/// This corresponds to `CSSMathMax` in the Typed OM specification. A maximum
/// expression represents constructs such as `max(10px, 20%)`. Each entry is
/// itself a `NumericValue`, allowing nested math expressions if needed.
struct StyleMathMax {
  /// The numeric type associated with this max.
  StyleNumericType numeric_type;
  /// The list of numeric terms that make up the max.
  CopyableTArray<StyleNumericValue> values;

  bool operator==(const StyleMathMax& other) const {
    return numeric_type == other.numeric_type &&
           values == other.values;
  }
};

/// A struct that basically replaces a `Box<[T; N]>`, but which cbindgen can
/// understand.
///
/// Every `OwnedArray` is allocation-backed with `N` fully-constructed
/// elements; there is no empty or moved-from state.
///
/// We could rely on the struct layout of `Box<[T; N]>`. Per the `Box`
/// documentation, `Box<T>` has the same ABI as `*mut T`, and since `[T; N]` is
/// `Sized`, that's a thin pointer (unlike `Box<[T]>`, which is fat):
///
///   https://doc.rust-lang.org/std/boxed/index.html#memory-layout
///
/// But handling `Box` with cbindgen both in structs and argument positions
/// more generally is a bit tricky.
///
/// This is useful when generated cbindgen code has circular references that
/// can only be broken by indirection through boxed objects. When a type needs
/// two, three, or a similar small number of such objects of the same kind,
/// `OwnedArray<T, N>` is more ergonomic and efficient than holding `N`
/// separate boxed values: it uses a single allocation and a single thin
/// pointer instead of `N` of each.
///
/// Compared to `OwnedSlice<T>`, `OwnedArray<T, N>` does not store the length
/// at runtime, `N` is part of the type, so the struct is a single
/// pointer-word instead of two. For types used as enum variant payloads, this
/// reduces the enclosing enum's footprint. The length can also be statically
/// checked, wrong-length values are unrepresentable, so consumers don't need
/// need runtime length assertions.
///
template<typename T, size_t N>
struct StyleOwnedArray {
  T *ptr;
  static_assert(N > 0);

  StyleOwnedArray() = delete;

  inline StyleOwnedArray& operator=(const StyleOwnedArray&);
  inline StyleOwnedArray& operator=(StyleOwnedArray&&) = delete;

  inline StyleOwnedArray(const StyleOwnedArray&);
  inline StyleOwnedArray(StyleOwnedArray&&) = delete;
  template <typename... Args>
    requires (sizeof...(Args) == N)
  inline explicit StyleOwnedArray(Args&&... aArgs);

  inline ~StyleOwnedArray();

  Span<const T> AsSpan() const {
    return {ptr, N};
  }

  static constexpr size_t Length() {
    return N;
  }

  bool operator==(const StyleOwnedArray& other) const {
    return AsSpan() == other.AsSpan();
  }
};

/// A clamp expression over numeric values.
///
/// This corresponds to `CSSMathClamp` in the Typed OM specification. A clamp
/// expression represents constructs such as `clamp(10px, 20%, 30px)`.
///
/// The array entries correspond to the lower bound, value, and upper bound,
/// respectively.
struct StyleMathClamp {
  /// The numeric type associated with this clamp.
  StyleNumericType numeric_type;
  /// The lower bound, value, and upper bound of the clamp expression, in
  /// that order.
  StyleOwnedArray<StyleNumericValue, 3> values;

  bool operator==(const StyleMathClamp& other) const {
    return numeric_type == other.numeric_type &&
           values == other.values;
  }
};

/// A math expression used by the Typed OM.
///
/// This corresponds to `CSSMathValue` and its subclasses in the Typed OM
/// specification.
struct StyleMathValue {
  enum class Tag {
    /// A sum of numeric values.
    ///
    /// This corresponds to `CSSMathSum`.
    Sum,
    /// A product of numeric values.
    ///
    /// This corresponds to `CSSMathProduct`.
    Product,
    /// A negated numeric value.
    ///
    /// This corresponds to `CSSMathNegate`.
    Negate,
    /// An inverted numeric value.
    ///
    /// This corresponds to `CSSMathInvert`.
    Invert,
    /// A minimum expression over numeric values.
    ///
    /// This corresponds to `CSSMathMin`.
    Min,
    /// A maximum expression over numeric values.
    ///
    /// This corresponds to `CSSMathMax`.
    Max,
    /// A clamp expression over numeric values.
    ///
    /// This corresponds to `CSSMathClamp`.
    Clamp,
  };

  struct StyleSum_Body {
    StyleMathSum _0;

    bool operator==(const StyleSum_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleProduct_Body {
    StyleMathProduct _0;

    bool operator==(const StyleProduct_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleNegate_Body {
    StyleMathNegate _0;

    bool operator==(const StyleNegate_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleInvert_Body {
    StyleMathInvert _0;

    bool operator==(const StyleInvert_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleMin_Body {
    StyleMathMin _0;

    bool operator==(const StyleMin_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleMax_Body {
    StyleMathMax _0;

    bool operator==(const StyleMax_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleClamp_Body {
    StyleMathClamp _0;

    bool operator==(const StyleClamp_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleSum_Body sum;
    StyleProduct_Body product;
    StyleNegate_Body negate;
    StyleInvert_Body invert;
    StyleMin_Body min;
    StyleMax_Body max;
    StyleClamp_Body clamp;
  };

  static StyleMathValue Sum(const StyleMathSum &_0) {
    StyleMathValue result;
    ::new (&result.sum._0) (StyleMathSum)(_0);
    result.tag = Tag::Sum;
    return result;
  }

  bool IsSum() const {
    return tag == Tag::Sum;
  }

  const StyleMathSum& AsSum() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSum());
    return sum._0;
  }

  static StyleMathValue Product(const StyleMathProduct &_0) {
    StyleMathValue result;
    ::new (&result.product._0) (StyleMathProduct)(_0);
    result.tag = Tag::Product;
    return result;
  }

  bool IsProduct() const {
    return tag == Tag::Product;
  }

  const StyleMathProduct& AsProduct() const {
    MOZ_DIAGNOSTIC_ASSERT(IsProduct());
    return product._0;
  }

  static StyleMathValue Negate(const StyleMathNegate &_0) {
    StyleMathValue result;
    ::new (&result.negate._0) (StyleMathNegate)(_0);
    result.tag = Tag::Negate;
    return result;
  }

  bool IsNegate() const {
    return tag == Tag::Negate;
  }

  const StyleMathNegate& AsNegate() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNegate());
    return negate._0;
  }

  static StyleMathValue Invert(const StyleMathInvert &_0) {
    StyleMathValue result;
    ::new (&result.invert._0) (StyleMathInvert)(_0);
    result.tag = Tag::Invert;
    return result;
  }

  bool IsInvert() const {
    return tag == Tag::Invert;
  }

  const StyleMathInvert& AsInvert() const {
    MOZ_DIAGNOSTIC_ASSERT(IsInvert());
    return invert._0;
  }

  static StyleMathValue Min(const StyleMathMin &_0) {
    StyleMathValue result;
    ::new (&result.min._0) (StyleMathMin)(_0);
    result.tag = Tag::Min;
    return result;
  }

  bool IsMin() const {
    return tag == Tag::Min;
  }

  const StyleMathMin& AsMin() const {
    MOZ_DIAGNOSTIC_ASSERT(IsMin());
    return min._0;
  }

  static StyleMathValue Max(const StyleMathMax &_0) {
    StyleMathValue result;
    ::new (&result.max._0) (StyleMathMax)(_0);
    result.tag = Tag::Max;
    return result;
  }

  bool IsMax() const {
    return tag == Tag::Max;
  }

  const StyleMathMax& AsMax() const {
    MOZ_DIAGNOSTIC_ASSERT(IsMax());
    return max._0;
  }

  static StyleMathValue Clamp(const StyleMathClamp &_0) {
    StyleMathValue result;
    ::new (&result.clamp._0) (StyleMathClamp)(_0);
    result.tag = Tag::Clamp;
    return result;
  }

  bool IsClamp() const {
    return tag == Tag::Clamp;
  }

  const StyleMathClamp& AsClamp() const {
    MOZ_DIAGNOSTIC_ASSERT(IsClamp());
    return clamp._0;
  }

  bool operator==(const StyleMathValue& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Sum: return sum == other.sum;
      case Tag::Product: return product == other.product;
      case Tag::Negate: return negate == other.negate;
      case Tag::Invert: return invert == other.invert;
      case Tag::Min: return min == other.min;
      case Tag::Max: return max == other.max;
      case Tag::Clamp: return clamp == other.clamp;

    }
    return true;
  }

  private:
  StyleMathValue() {

  }
  public:


  ~StyleMathValue() {
    switch (tag) {
      case Tag::Sum: sum.~StyleSum_Body(); break;
      case Tag::Product: product.~StyleProduct_Body(); break;
      case Tag::Negate: negate.~StyleNegate_Body(); break;
      case Tag::Invert: invert.~StyleInvert_Body(); break;
      case Tag::Min: min.~StyleMin_Body(); break;
      case Tag::Max: max.~StyleMax_Body(); break;
      case Tag::Clamp: clamp.~StyleClamp_Body(); break;

    }
  }

  StyleMathValue(const StyleMathValue& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Sum: ::new (&sum) (StyleSum_Body)(other.sum); break;
      case Tag::Product: ::new (&product) (StyleProduct_Body)(other.product); break;
      case Tag::Negate: ::new (&negate) (StyleNegate_Body)(other.negate); break;
      case Tag::Invert: ::new (&invert) (StyleInvert_Body)(other.invert); break;
      case Tag::Min: ::new (&min) (StyleMin_Body)(other.min); break;
      case Tag::Max: ::new (&max) (StyleMax_Body)(other.max); break;
      case Tag::Clamp: ::new (&clamp) (StyleClamp_Body)(other.clamp); break;

    }
  }
  StyleMathValue& operator=(const StyleMathValue& other) {
    if (this != &other) {
      this->~StyleMathValue();
      new (this) StyleMathValue(other);
    }
    return *this;
  }
};

/// A numeric value used by the Typed OM.
///
/// This corresponds to `CSSNumericValue` and its subclasses in the Typed OM
/// specification. It represents numbers that can appear in CSS values,
/// including both simple unit quantities and composite expressions.
///
/// Unlike the parser-level representation, `NumericValue` is property-agnostic
/// and suitable for conversion to or from the `CSSNumericValue` family of DOM
/// objects.
struct StyleNumericValue {
  enum class Tag {
    /// A single numeric value with a concrete unit.
    ///
    /// This corresponds to `CSSUnitValue`.
    Unit,
    /// A math expression.
    ///
    /// This corresponds to `CSSMathValue` and its subclasses.
    Math,
  };

  struct StyleUnit_Body {
    StyleUnitValue _0;

    bool operator==(const StyleUnit_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleMath_Body {
    StyleMathValue _0;

    bool operator==(const StyleMath_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleUnit_Body unit;
    StyleMath_Body math;
  };

  static StyleNumericValue Unit(const StyleUnitValue &_0) {
    StyleNumericValue result;
    ::new (&result.unit._0) (StyleUnitValue)(_0);
    result.tag = Tag::Unit;
    return result;
  }

  bool IsUnit() const {
    return tag == Tag::Unit;
  }

  const StyleUnitValue& AsUnit() const {
    MOZ_DIAGNOSTIC_ASSERT(IsUnit());
    return unit._0;
  }

  static StyleNumericValue Math(const StyleMathValue &_0) {
    StyleNumericValue result;
    ::new (&result.math._0) (StyleMathValue)(_0);
    result.tag = Tag::Math;
    return result;
  }

  bool IsMath() const {
    return tag == Tag::Math;
  }

  const StyleMathValue& AsMath() const {
    MOZ_DIAGNOSTIC_ASSERT(IsMath());
    return math._0;
  }

  bool operator==(const StyleNumericValue& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Unit: return unit == other.unit;
      case Tag::Math: return math == other.math;

    }
    return true;
  }

  private:
  StyleNumericValue() {

  }
  public:


  ~StyleNumericValue() {
    switch (tag) {
      case Tag::Unit: unit.~StyleUnit_Body(); break;
      case Tag::Math: math.~StyleMath_Body(); break;

    }
  }

  StyleNumericValue(const StyleNumericValue& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Unit: ::new (&unit) (StyleUnit_Body)(other.unit); break;
      case Tag::Math: ::new (&math) (StyleMath_Body)(other.math); break;

    }
  }
  StyleNumericValue& operator=(const StyleNumericValue& other) {
    if (this != &other) {
      this->~StyleNumericValue();
      new (this) StyleNumericValue(other);
    }
    return *this;
  }
};

/// A translate transform component used by the Typed OM.
///
/// This corresponds to `CSSTranslate` in the Typed OM specification. The `x`,
/// `y`, and `z` components are always present; omitted offsets are represented
/// as `0px`.
///
/// The `is_2d` flag indicates whether the component was reified from a 2D
/// translate function.
struct StyleTranslateComponent {
  /// The x-axis translation component.
  StyleNumericValue x;
  /// The y-axis translation component.
  StyleNumericValue y;
  /// The z-axis translation component.
  StyleNumericValue z;
  /// Whether this translate component is two-dimensional.
  bool is_2d;

  bool operator==(const StyleTranslateComponent& other) const {
    return x == other.x &&
           y == other.y &&
           z == other.z &&
           is_2d == other.is_2d;
  }
};

/// A rotate transform component used by the Typed OM.
///
/// This corresponds to `CSSRotate` in the Typed OM specification. The `angle`,
/// `x`, `y`, and `z` components are always present; omitted axis coordinates
/// are represented using the implicit axis for the corresponding rotate
/// function.
///
/// The `is_2d` flag indicates whether the component was reified from a 2D
/// rotate function.
struct StyleRotateComponent {
  /// The rotation angle.
  StyleNumericValue angle;
  /// The x-axis rotation coordinate.
  StyleNumericValue x;
  /// The y-axis rotation coordinate.
  StyleNumericValue y;
  /// The z-axis rotation coordinate.
  StyleNumericValue z;
  /// Whether this rotate component is two-dimensional.
  bool is_2d;

  bool operator==(const StyleRotateComponent& other) const {
    return angle == other.angle &&
           x == other.x &&
           y == other.y &&
           z == other.z &&
           is_2d == other.is_2d;
  }
};

/// A scale transform component used by the Typed OM.
///
/// This corresponds to `CSSScale` in the Typed OM specification. The `x`, `y`,
/// and `z` components are always present; omitted scale factors are
/// represented as `1`.
///
/// The `is_2d` flag indicates whether the component was reified from a 2D
/// scale function.
struct StyleScaleComponent {
  /// The x-axis scale factor.
  StyleNumericValue x;
  /// The y-axis scale factor.
  StyleNumericValue y;
  /// The z-axis scale factor.
  StyleNumericValue z;
  /// Whether this scale component is two-dimensional.
  bool is_2d;

  bool operator==(const StyleScaleComponent& other) const {
    return x == other.x &&
           y == other.y &&
           z == other.z &&
           is_2d == other.is_2d;
  }
};

/// A skew transform component used by the Typed OM.
///
/// This corresponds to `CSSSkew` in the Typed OM specification. The `ax` and
/// `ay` components are always present; omitted angles are represented as
/// `0deg`.
///
/// Skew components are always two-dimensional.
struct StyleSkewComponent {
  /// The x-axis skew angle.
  StyleNumericValue ax;
  /// The y-axis skew angle.
  StyleNumericValue ay;

  bool operator==(const StyleSkewComponent& other) const {
    return ax == other.ax &&
           ay == other.ay;
  }
};

/// A skewX transform component used by the Typed OM.
///
/// This corresponds to `CSSSkewX` in the Typed OM specification. The value is
/// always present; omitted angles are represented as `0deg`.
///
/// SkewX components are always two-dimensional.
using StyleSkewXComponent = StyleNumericValue;

/// A skewY transform component used by the Typed OM.
///
/// This corresponds to `CSSSkewY` in the Typed OM specification. The value is
/// always present; omitted angles are represented as `0deg`.
///
/// SkewY components are always two-dimensional.
using StyleSkewYComponent = StyleNumericValue;

/// A perspective value used by a perspective component.
///
/// This corresponds to the `CSSPerspectiveValue` union in the Typed OM
/// specification.
struct StylePerspectiveValue {
  enum class Tag {
    /// A numeric perspective value.
    ///
    /// This corresponds to `CSSNumericValue`.
    Numeric,
    /// A keyword perspective value.
    ///
    /// This corresponds to `CSSKeywordValue`.
    Keyword,
  };

  struct StyleNumeric_Body {
    StyleNumericValue _0;

    bool operator==(const StyleNumeric_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleKeyword_Body {
    StyleKeywordValue _0;

    bool operator==(const StyleKeyword_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleNumeric_Body numeric;
    StyleKeyword_Body keyword;
  };

  static StylePerspectiveValue Numeric(const StyleNumericValue &_0) {
    StylePerspectiveValue result;
    ::new (&result.numeric._0) (StyleNumericValue)(_0);
    result.tag = Tag::Numeric;
    return result;
  }

  bool IsNumeric() const {
    return tag == Tag::Numeric;
  }

  const StyleNumericValue& AsNumeric() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNumeric());
    return numeric._0;
  }

  static StylePerspectiveValue Keyword(const StyleKeywordValue &_0) {
    StylePerspectiveValue result;
    ::new (&result.keyword._0) (StyleKeywordValue)(_0);
    result.tag = Tag::Keyword;
    return result;
  }

  bool IsKeyword() const {
    return tag == Tag::Keyword;
  }

  const StyleKeywordValue& AsKeyword() const {
    MOZ_DIAGNOSTIC_ASSERT(IsKeyword());
    return keyword._0;
  }

  bool operator==(const StylePerspectiveValue& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Numeric: return numeric == other.numeric;
      case Tag::Keyword: return keyword == other.keyword;

    }
    return true;
  }

  private:
  StylePerspectiveValue() {

  }
  public:


  ~StylePerspectiveValue() {
    switch (tag) {
      case Tag::Numeric: numeric.~StyleNumeric_Body(); break;
      case Tag::Keyword: keyword.~StyleKeyword_Body(); break;

    }
  }

  StylePerspectiveValue(const StylePerspectiveValue& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Numeric: ::new (&numeric) (StyleNumeric_Body)(other.numeric); break;
      case Tag::Keyword: ::new (&keyword) (StyleKeyword_Body)(other.keyword); break;

    }
  }
  StylePerspectiveValue& operator=(const StylePerspectiveValue& other) {
    if (this != &other) {
      this->~StylePerspectiveValue();
      new (this) StylePerspectiveValue(other);
    }
    return *this;
  }
};

/// A perspective transform component used by the Typed OM.
///
/// This corresponds to `CSSPerspective` in the Typed OM specification. The
/// `length` component is always present.
///
/// Perspective components are always three-dimensional.
struct StylePerspectiveComponent {
  /// The perspective length.
  StylePerspectiveValue length;

  bool operator==(const StylePerspectiveComponent& other) const {
    return length == other.length;
  }
};

/// A matrix transform component used by the Typed OM.
///
/// This corresponds to `CSSMatrixComponent` in the Typed OM specification.
///
/// The `matrix` field always stores a full 4×4 matrix. Two-dimensional
/// matrices are expanded to their equivalent 3D representation during
/// reification.
///
/// The `is_2d` flag indicates whether the component was reified from a 2D
/// matrix function.
struct StyleMatrixComponent {
  /// The 4×4 matrix.
  StyleGenericMatrix3D<StyleCSSFloat> matrix;
  /// Whether this matrix component is two-dimensional.
  bool is_2d;

  bool operator==(const StyleMatrixComponent& other) const {
    return matrix == other.matrix &&
           is_2d == other.is_2d;
  }
};

/// A single transform component used by the Typed OM.
///
/// This corresponds to `CSSTransformComponent` in the Typed OM specification.
/// Each variant represents one concrete transform component subclass.
struct StyleTransformComponent {
  enum class Tag {
    /// A translate transform component.
    ///
    /// This corresponds to `CSSTranslate`.
    Translate,
    /// A rotate transform component.
    ///
    /// This corresponds to `CSSRotate`.
    Rotate,
    /// A scale transform component.
    ///
    /// This corresponds to `CSSScale`.
    Scale,
    /// A skew transform component.
    ///
    /// This corresponds to `CSSSkew`.
    Skew,
    /// A skewX transform component.
    ///
    /// This corresponds to `CSSSkewX`.
    SkewX,
    /// A skewY transform component.
    ///
    /// This corresponds to `CSSSkewY`.
    SkewY,
    /// A perspective transform component.
    ///
    /// This corresponds to `CSSPerspective`.
    Perspective,
    /// A matrix transform component.
    ///
    /// This corresponds to `CSSMatrixComponent`.
    Matrix,
  };

  struct StyleTranslate_Body {
    StyleTranslateComponent _0;

    bool operator==(const StyleTranslate_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleRotate_Body {
    StyleRotateComponent _0;

    bool operator==(const StyleRotate_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleScale_Body {
    StyleScaleComponent _0;

    bool operator==(const StyleScale_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleSkew_Body {
    StyleSkewComponent _0;

    bool operator==(const StyleSkew_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleSkewX_Body {
    StyleSkewXComponent _0;

    bool operator==(const StyleSkewX_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleSkewY_Body {
    StyleSkewYComponent _0;

    bool operator==(const StyleSkewY_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StylePerspective_Body {
    StylePerspectiveComponent _0;

    bool operator==(const StylePerspective_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleMatrix_Body {
    StyleMatrixComponent _0;

    bool operator==(const StyleMatrix_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleTranslate_Body translate;
    StyleRotate_Body rotate;
    StyleScale_Body scale;
    StyleSkew_Body skew;
    StyleSkewX_Body skew_x;
    StyleSkewY_Body skew_y;
    StylePerspective_Body perspective;
    StyleMatrix_Body matrix;
  };

  static StyleTransformComponent Translate(const StyleTranslateComponent &_0) {
    StyleTransformComponent result;
    ::new (&result.translate._0) (StyleTranslateComponent)(_0);
    result.tag = Tag::Translate;
    return result;
  }

  bool IsTranslate() const {
    return tag == Tag::Translate;
  }

  const StyleTranslateComponent& AsTranslate() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTranslate());
    return translate._0;
  }

  static StyleTransformComponent Rotate(const StyleRotateComponent &_0) {
    StyleTransformComponent result;
    ::new (&result.rotate._0) (StyleRotateComponent)(_0);
    result.tag = Tag::Rotate;
    return result;
  }

  bool IsRotate() const {
    return tag == Tag::Rotate;
  }

  const StyleRotateComponent& AsRotate() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRotate());
    return rotate._0;
  }

  static StyleTransformComponent Scale(const StyleScaleComponent &_0) {
    StyleTransformComponent result;
    ::new (&result.scale._0) (StyleScaleComponent)(_0);
    result.tag = Tag::Scale;
    return result;
  }

  bool IsScale() const {
    return tag == Tag::Scale;
  }

  const StyleScaleComponent& AsScale() const {
    MOZ_DIAGNOSTIC_ASSERT(IsScale());
    return scale._0;
  }

  static StyleTransformComponent Skew(const StyleSkewComponent &_0) {
    StyleTransformComponent result;
    ::new (&result.skew._0) (StyleSkewComponent)(_0);
    result.tag = Tag::Skew;
    return result;
  }

  bool IsSkew() const {
    return tag == Tag::Skew;
  }

  const StyleSkewComponent& AsSkew() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSkew());
    return skew._0;
  }

  static StyleTransformComponent SkewX(const StyleSkewXComponent &_0) {
    StyleTransformComponent result;
    ::new (&result.skew_x._0) (StyleSkewXComponent)(_0);
    result.tag = Tag::SkewX;
    return result;
  }

  bool IsSkewX() const {
    return tag == Tag::SkewX;
  }

  const StyleSkewXComponent& AsSkewX() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSkewX());
    return skew_x._0;
  }

  static StyleTransformComponent SkewY(const StyleSkewYComponent &_0) {
    StyleTransformComponent result;
    ::new (&result.skew_y._0) (StyleSkewYComponent)(_0);
    result.tag = Tag::SkewY;
    return result;
  }

  bool IsSkewY() const {
    return tag == Tag::SkewY;
  }

  const StyleSkewYComponent& AsSkewY() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSkewY());
    return skew_y._0;
  }

  static StyleTransformComponent Perspective(const StylePerspectiveComponent &_0) {
    StyleTransformComponent result;
    ::new (&result.perspective._0) (StylePerspectiveComponent)(_0);
    result.tag = Tag::Perspective;
    return result;
  }

  bool IsPerspective() const {
    return tag == Tag::Perspective;
  }

  const StylePerspectiveComponent& AsPerspective() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPerspective());
    return perspective._0;
  }

  static StyleTransformComponent Matrix(const StyleMatrixComponent &_0) {
    StyleTransformComponent result;
    ::new (&result.matrix._0) (StyleMatrixComponent)(_0);
    result.tag = Tag::Matrix;
    return result;
  }

  bool IsMatrix() const {
    return tag == Tag::Matrix;
  }

  const StyleMatrixComponent& AsMatrix() const {
    MOZ_DIAGNOSTIC_ASSERT(IsMatrix());
    return matrix._0;
  }

  bool operator==(const StyleTransformComponent& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Translate: return translate == other.translate;
      case Tag::Rotate: return rotate == other.rotate;
      case Tag::Scale: return scale == other.scale;
      case Tag::Skew: return skew == other.skew;
      case Tag::SkewX: return skew_x == other.skew_x;
      case Tag::SkewY: return skew_y == other.skew_y;
      case Tag::Perspective: return perspective == other.perspective;
      case Tag::Matrix: return matrix == other.matrix;

    }
    return true;
  }

  private:
  StyleTransformComponent() {

  }
  public:


  ~StyleTransformComponent() {
    switch (tag) {
      case Tag::Translate: translate.~StyleTranslate_Body(); break;
      case Tag::Rotate: rotate.~StyleRotate_Body(); break;
      case Tag::Scale: scale.~StyleScale_Body(); break;
      case Tag::Skew: skew.~StyleSkew_Body(); break;
      case Tag::SkewX: skew_x.~StyleSkewX_Body(); break;
      case Tag::SkewY: skew_y.~StyleSkewY_Body(); break;
      case Tag::Perspective: perspective.~StylePerspective_Body(); break;
      case Tag::Matrix: matrix.~StyleMatrix_Body(); break;

    }
  }

  StyleTransformComponent(const StyleTransformComponent& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Translate: ::new (&translate) (StyleTranslate_Body)(other.translate); break;
      case Tag::Rotate: ::new (&rotate) (StyleRotate_Body)(other.rotate); break;
      case Tag::Scale: ::new (&scale) (StyleScale_Body)(other.scale); break;
      case Tag::Skew: ::new (&skew) (StyleSkew_Body)(other.skew); break;
      case Tag::SkewX: ::new (&skew_x) (StyleSkewX_Body)(other.skew_x); break;
      case Tag::SkewY: ::new (&skew_y) (StyleSkewY_Body)(other.skew_y); break;
      case Tag::Perspective: ::new (&perspective) (StylePerspective_Body)(other.perspective); break;
      case Tag::Matrix: ::new (&matrix) (StyleMatrix_Body)(other.matrix); break;

    }
  }
  StyleTransformComponent& operator=(const StyleTransformComponent& other) {
    if (this != &other) {
      this->~StyleTransformComponent();
      new (this) StyleTransformComponent(other);
    }
    return *this;
  }
};

/// A transform value used by the Typed OM.
///
/// This corresponds to `CSSTransformValue` in the Typed OM specification. It
/// represents a `<transform-list>` as an ordered list of transform components.
using StyleTransformValue = CopyableTArray<StyleTransformComponent>;

/// An image value used by the Typed OM.
///
/// This corresponds to `CSSImageValue` in the Typed OM specification.
///
/// `CSSImageValue` objects represent values for properties that take
/// `<image>` values.
struct StyleImageValue {
  enum class Tag {
    /// A specified image URL value.
    ///
    /// Relative URLs are preserved and continue to resolve against the
    /// originating stylesheet or document when later used.
    Specified,
    /// A computed image URL value.
    ///
    /// Computed URLs are already resolved according to normal CSS computed
    /// value processing.
    Computed,
  };

  struct StyleSpecified_Body {
    StyleSpecifiedUrl _0;

    bool operator==(const StyleSpecified_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleComputed_Body {
    StyleComputedUrl _0;

    bool operator==(const StyleComputed_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleSpecified_Body specified;
    StyleComputed_Body computed;
  };

  static StyleImageValue Specified(const StyleSpecifiedUrl &_0) {
    StyleImageValue result;
    ::new (&result.specified._0) (StyleSpecifiedUrl)(_0);
    result.tag = Tag::Specified;
    return result;
  }

  bool IsSpecified() const {
    return tag == Tag::Specified;
  }

  const StyleSpecifiedUrl& AsSpecified() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSpecified());
    return specified._0;
  }

  static StyleImageValue Computed(const StyleComputedUrl &_0) {
    StyleImageValue result;
    ::new (&result.computed._0) (StyleComputedUrl)(_0);
    result.tag = Tag::Computed;
    return result;
  }

  bool IsComputed() const {
    return tag == Tag::Computed;
  }

  const StyleComputedUrl& AsComputed() const {
    MOZ_DIAGNOSTIC_ASSERT(IsComputed());
    return computed._0;
  }

  bool operator==(const StyleImageValue& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Specified: return specified == other.specified;
      case Tag::Computed: return computed == other.computed;

    }
    return true;
  }

  private:
  StyleImageValue() {

  }
  public:


  ~StyleImageValue() {
    switch (tag) {
      case Tag::Specified: specified.~StyleSpecified_Body(); break;
      case Tag::Computed: computed.~StyleComputed_Body(); break;

    }
  }

  StyleImageValue(const StyleImageValue& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Specified: ::new (&specified) (StyleSpecified_Body)(other.specified); break;
      case Tag::Computed: ::new (&computed) (StyleComputed_Body)(other.computed); break;

    }
  }
  StyleImageValue& operator=(const StyleImageValue& other) {
    if (this != &other) {
      this->~StyleImageValue();
      new (this) StyleImageValue(other);
    }
    return *this;
  }
};

/// A property-agnostic representation of a value, used by Typed OM.
///
/// `TypedValue` is the internal counterpart of the various `CSSStyleValue`
/// subclasses defined by the Typed OM specification. It captures values that
/// can be represented independently of any particular property.
struct StyleTypedValue {
  enum class Tag {
    /// An unparsed value consisting of string fragments and variable
    /// references.
    ///
    /// This corresponds to `CSSUnparsedValue` in the Typed OM specification.
    Unparsed,
    /// A keyword value such as `"block"`, `"none"`, or `"thin"`.
    ///
    /// This corresponds to `CSSKeywordValue` in the Typed OM specification.
    /// Keywords are represented as a standalone `KeywordValue` so they can
    /// be carried and compared independently of any particular property.
    Keyword,
    /// A numeric value such as a length, angle, time, or a sum thereof.
    ///
    /// This corresponds to the `CSSNumericValue` hierarchy in the Typed OM
    /// specification, including `CSSUnitValue` and `CSSMathSum`.
    Numeric,
    /// A transform value such as `translate(10px, 20px)`.
    ///
    /// This corresponds to `CSSTransformValue` in the Typed OM specification.
    Transform,
    /// An image value.
    ///
    /// This corresponds to `CSSImageValue` in the Typed OM specification.
    Image,
  };

  struct StyleUnparsed_Body {
    StyleUnparsedValue _0;

    bool operator==(const StyleUnparsed_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleKeyword_Body {
    StyleKeywordValue _0;

    bool operator==(const StyleKeyword_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleNumeric_Body {
    StyleNumericValue _0;

    bool operator==(const StyleNumeric_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleTransform_Body {
    StyleTransformValue _0;

    bool operator==(const StyleTransform_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleImage_Body {
    StyleImageValue _0;

    bool operator==(const StyleImage_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleUnparsed_Body unparsed;
    StyleKeyword_Body keyword;
    StyleNumeric_Body numeric;
    StyleTransform_Body transform;
    StyleImage_Body image;
  };

  static StyleTypedValue Unparsed(const StyleUnparsedValue &_0) {
    StyleTypedValue result;
    ::new (&result.unparsed._0) (StyleUnparsedValue)(_0);
    result.tag = Tag::Unparsed;
    return result;
  }

  bool IsUnparsed() const {
    return tag == Tag::Unparsed;
  }

  const StyleUnparsedValue& AsUnparsed() const {
    MOZ_DIAGNOSTIC_ASSERT(IsUnparsed());
    return unparsed._0;
  }

  static StyleTypedValue Keyword(const StyleKeywordValue &_0) {
    StyleTypedValue result;
    ::new (&result.keyword._0) (StyleKeywordValue)(_0);
    result.tag = Tag::Keyword;
    return result;
  }

  bool IsKeyword() const {
    return tag == Tag::Keyword;
  }

  const StyleKeywordValue& AsKeyword() const {
    MOZ_DIAGNOSTIC_ASSERT(IsKeyword());
    return keyword._0;
  }

  static StyleTypedValue Numeric(const StyleNumericValue &_0) {
    StyleTypedValue result;
    ::new (&result.numeric._0) (StyleNumericValue)(_0);
    result.tag = Tag::Numeric;
    return result;
  }

  bool IsNumeric() const {
    return tag == Tag::Numeric;
  }

  const StyleNumericValue& AsNumeric() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNumeric());
    return numeric._0;
  }

  static StyleTypedValue Transform(const StyleTransformValue &_0) {
    StyleTypedValue result;
    ::new (&result.transform._0) (StyleTransformValue)(_0);
    result.tag = Tag::Transform;
    return result;
  }

  bool IsTransform() const {
    return tag == Tag::Transform;
  }

  const StyleTransformValue& AsTransform() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTransform());
    return transform._0;
  }

  static StyleTypedValue Image(const StyleImageValue &_0) {
    StyleTypedValue result;
    ::new (&result.image._0) (StyleImageValue)(_0);
    result.tag = Tag::Image;
    return result;
  }

  bool IsImage() const {
    return tag == Tag::Image;
  }

  const StyleImageValue& AsImage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsImage());
    return image._0;
  }

  bool operator==(const StyleTypedValue& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Unparsed: return unparsed == other.unparsed;
      case Tag::Keyword: return keyword == other.keyword;
      case Tag::Numeric: return numeric == other.numeric;
      case Tag::Transform: return transform == other.transform;
      case Tag::Image: return image == other.image;

    }
    return true;
  }

  private:
  StyleTypedValue() {

  }
  public:


  ~StyleTypedValue() {
    switch (tag) {
      case Tag::Unparsed: unparsed.~StyleUnparsed_Body(); break;
      case Tag::Keyword: keyword.~StyleKeyword_Body(); break;
      case Tag::Numeric: numeric.~StyleNumeric_Body(); break;
      case Tag::Transform: transform.~StyleTransform_Body(); break;
      case Tag::Image: image.~StyleImage_Body(); break;

    }
  }

  StyleTypedValue(const StyleTypedValue& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Unparsed: ::new (&unparsed) (StyleUnparsed_Body)(other.unparsed); break;
      case Tag::Keyword: ::new (&keyword) (StyleKeyword_Body)(other.keyword); break;
      case Tag::Numeric: ::new (&numeric) (StyleNumeric_Body)(other.numeric); break;
      case Tag::Transform: ::new (&transform) (StyleTransform_Body)(other.transform); break;
      case Tag::Image: ::new (&image) (StyleImage_Body)(other.image); break;

    }
  }
  StyleTypedValue& operator=(const StyleTypedValue& other) {
    if (this != &other) {
      this->~StyleTypedValue();
      new (this) StyleTypedValue(other);
    }
    return *this;
  }
};

/// A list of property-agnostic values used by the Typed OM.
///
/// `TypedValueList` is the internal counterpart of CSS value lists exposed by
/// Typed OM. It stores one or more [`TypedValue`] items in source order and
/// is used when a value reifies to multiple property-agnostic components.
struct StyleTypedValueList {
  /// The list of reified values.
  CopyableTArray<StyleTypedValue> values;

  bool operator==(const StyleTypedValueList& other) const {
    return values == other.values;
  }
};

/// A property-aware wrapper around reification results.
///
/// While `TypedValueList` is property-agnostic, this enum represents the
/// outcome of reifying a specific property from a `PropertyDeclarationBlock`.
/// It distinguishes between properties that are not present, properties whose
/// values cannot be represented as a `TypedValueList`, and properties that
/// were successfully reified.
///
/// In the unsupported case, the full declaration block is carried via
/// `UnsupportedValue`, which in turn holds the
/// `Strong<LockedDeclarationBlock>`.
struct StylePropertyTypedValueList {
  enum class Tag {
    /// The property is not present in the declaration block.
    None,
    /// The property exists but cannot be expressed as a `TypedValueList`.
    ///
    /// This occurs for shorthands and other unrepresentable cases. In this
    /// case, an `UnsupportedValue` is returned so a `CSSUnsupportedValue`
    /// object can be created and tied to the property.
    Unsupported,
    /// The property was successfully reified into a `TypedValueList`.
    Typed,
  };

  struct StyleUnsupported_Body {
    StyleUnsupportedValue _0;

    bool operator==(const StyleUnsupported_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleTyped_Body {
    StyleTypedValueList _0;

    bool operator==(const StyleTyped_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleUnsupported_Body unsupported;
    StyleTyped_Body typed;
  };

  static StylePropertyTypedValueList None() {
    StylePropertyTypedValueList result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StylePropertyTypedValueList Unsupported(const StyleUnsupportedValue &_0) {
    StylePropertyTypedValueList result;
    ::new (&result.unsupported._0) (StyleUnsupportedValue)(_0);
    result.tag = Tag::Unsupported;
    return result;
  }

  bool IsUnsupported() const {
    return tag == Tag::Unsupported;
  }

  const StyleUnsupportedValue& AsUnsupported() const {
    MOZ_DIAGNOSTIC_ASSERT(IsUnsupported());
    return unsupported._0;
  }

  static StylePropertyTypedValueList Typed(const StyleTypedValueList &_0) {
    StylePropertyTypedValueList result;
    ::new (&result.typed._0) (StyleTypedValueList)(_0);
    result.tag = Tag::Typed;
    return result;
  }

  bool IsTyped() const {
    return tag == Tag::Typed;
  }

  const StyleTypedValueList& AsTyped() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTyped());
    return typed._0;
  }

  bool operator==(const StylePropertyTypedValueList& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Unsupported: return unsupported == other.unsupported;
      case Tag::Typed: return typed == other.typed;
      default: break;
    }
    return true;
  }

  private:
  StylePropertyTypedValueList() {

  }
  public:


  ~StylePropertyTypedValueList() {
    switch (tag) {
      case Tag::Unsupported: unsupported.~StyleUnsupported_Body(); break;
      case Tag::Typed: typed.~StyleTyped_Body(); break;
      default: break;
    }
  }
  StylePropertyTypedValueList(StylePropertyTypedValueList&& other)
      : tag(other.tag) {
    switch (tag) {
      case Tag::None:
        break;
      case Tag::Unsupported:
        ::new (&unsupported)
            StyleUnsupported_Body(std::move(other.unsupported));
        break;
      case Tag::Typed:
        ::new (&typed) StyleTyped_Body(std::move(other.typed));
        break;
    }
  }

  StylePropertyTypedValueList& operator=(StylePropertyTypedValueList&& other) {
    if (this != &other) {
      this->~StylePropertyTypedValueList();
      new (this) StylePropertyTypedValueList(std::move(other));
    }
    return *this;
  }

  StyleUnsupportedValue ExtractUnsupported() && {
    MOZ_DIAGNOSTIC_ASSERT(IsUnsupported());
    return std::move(unsupported._0);
  }
};

/// A result of reifying a standalone numeric value into a `NumericValue`.
///
/// Numeric values are normally reified as part of property value reification.
/// This type is used for a special case where a numeric value is parsed and
/// reified without being associated with a specific property.
///
/// The `Unsupported` case is not expected in normal operation and indicates
/// that the numeric value could not be represented as a `NumericValue`.
struct StyleNumericValueResult {
  enum class Tag {
    /// The numeric value could not be reified as a `NumericValue`.
    ///
    /// This may indicate that a `ToTyped` implementation for one of the
    /// underlying types is incomplete, or that reification produced a
    /// non-numeric `TypedValue`. In this case, the caller is expected to
    /// throw an error.
    Unsupported,
    /// The numeric value was successfully reified into a `NumericValue`.
    Numeric,
  };

  struct StyleNumeric_Body {
    StyleNumericValue _0;

    bool operator==(const StyleNumeric_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleNumeric_Body numeric;
  };

  static StyleNumericValueResult Unsupported() {
    StyleNumericValueResult result;
    result.tag = Tag::Unsupported;
    return result;
  }

  bool IsUnsupported() const {
    return tag == Tag::Unsupported;
  }

  static StyleNumericValueResult Numeric(const StyleNumericValue &_0) {
    StyleNumericValueResult result;
    ::new (&result.numeric._0) (StyleNumericValue)(_0);
    result.tag = Tag::Numeric;
    return result;
  }

  bool IsNumeric() const {
    return tag == Tag::Numeric;
  }

  const StyleNumericValue& AsNumeric() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNumeric());
    return numeric._0;
  }

  bool operator==(const StyleNumericValueResult& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Numeric: return numeric == other.numeric;
      default: break;
    }
    return true;
  }

  private:
  StyleNumericValueResult() {

  }
  public:


  ~StyleNumericValueResult() {
    switch (tag) {
      case Tag::Numeric: numeric.~StyleNumeric_Body(); break;
      default: break;
    }
  }

  StyleNumericValueResult(const StyleNumericValueResult& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Numeric: ::new (&numeric) (StyleNumeric_Body)(other.numeric); break;
      default: break;
    }
  }
  StyleNumericValueResult& operator=(const StyleNumericValueResult& other) {
    if (this != &other) {
      this->~StyleNumericValueResult();
      new (this) StyleNumericValueResult(other);
    }
    return *this;
  }
};

/// Either a percentage or a number.
union StyleNumberOrPercentageComponent {
  enum class Tag : uint8_t {
    /// `<number>`.
    Number,
    /// `<percentage>`
    /// The value as a float, divided by 100 so that the nominal range is 0.0 to 1.0.
    Percentage,
  };

  struct Number_Body {
    Tag tag;
    float _0;

    bool operator==(const Number_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Percentage_Body {
    Tag tag;
    float _0;

    bool operator==(const Percentage_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Number_Body number;
  Percentage_Body percentage;

  static StyleNumberOrPercentageComponent Number(const float &_0) {
    StyleNumberOrPercentageComponent result;
    ::new (&result.number._0) (float)(_0);
    result.tag = Tag::Number;
    return result;
  }

  bool IsNumber() const {
    return tag == Tag::Number;
  }

  const float& AsNumber() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNumber());
    return number._0;
  }

  static StyleNumberOrPercentageComponent Percentage(const float &_0) {
    StyleNumberOrPercentageComponent result;
    ::new (&result.percentage._0) (float)(_0);
    result.tag = Tag::Percentage;
    return result;
  }

  bool IsPercentage() const {
    return tag == Tag::Percentage;
  }

  const float& AsPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPercentage());
    return percentage._0;
  }

  bool operator==(const StyleNumberOrPercentageComponent& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Number: return number == other.number;
      case Tag::Percentage: return percentage == other.percentage;

    }
    return true;
  }

  private:
  StyleNumberOrPercentageComponent() {

  }
  public:


  ~StyleNumberOrPercentageComponent() {
    switch (tag) {
      case Tag::Number: number.~Number_Body(); break;
      case Tag::Percentage: percentage.~Percentage_Body(); break;

    }
  }

  StyleNumberOrPercentageComponent(const StyleNumberOrPercentageComponent& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Number: ::new (&number) (Number_Body)(other.number); break;
      case Tag::Percentage: ::new (&percentage) (Percentage_Body)(other.percentage); break;

    }
  }
  StyleNumberOrPercentageComponent& operator=(const StyleNumberOrPercentageComponent& other) {
    if (this != &other) {
      this->~StyleNumberOrPercentageComponent();
      new (this) StyleNumberOrPercentageComponent(other);
    }
    return *this;
  }
};

/// Represents a channel keyword inside a color.
struct StyleChannelKeyword {
  uint16_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleChannelKeyword operator~() const {
    return StyleChannelKeyword { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleChannelKeyword operator|(const StyleChannelKeyword& other) const {
    return StyleChannelKeyword { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleChannelKeyword& operator|=(const StyleChannelKeyword& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleChannelKeyword operator&(const StyleChannelKeyword& other) const {
    return StyleChannelKeyword { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleChannelKeyword& operator&=(const StyleChannelKeyword& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleChannelKeyword operator^(const StyleChannelKeyword& other) const {
    return StyleChannelKeyword { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleChannelKeyword& operator^=(const StyleChannelKeyword& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleChannelKeyword& other) const {
    return _0 == other._0;
  }
  static const StyleChannelKeyword ALPHA;
  static const StyleChannelKeyword A;
  static const StyleChannelKeyword B;
  static const StyleChannelKeyword C;
  static const StyleChannelKeyword G;
  static const StyleChannelKeyword H;
  static const StyleChannelKeyword L;
  static const StyleChannelKeyword R;
  static const StyleChannelKeyword S;
  static const StyleChannelKeyword W;
  static const StyleChannelKeyword X;
  static const StyleChannelKeyword Y;
  static const StyleChannelKeyword Z;
};
/// alpha
constexpr inline const StyleChannelKeyword StyleChannelKeyword::ALPHA = StyleChannelKeyword{
  /* ._0 = */ (uint16_t)(1 << 0)
};
/// a
constexpr inline const StyleChannelKeyword StyleChannelKeyword::A = StyleChannelKeyword{
  /* ._0 = */ (uint16_t)(1 << 1)
};
/// b, blackness, blue
constexpr inline const StyleChannelKeyword StyleChannelKeyword::B = StyleChannelKeyword{
  /* ._0 = */ (uint16_t)(1 << 2)
};
/// chroma
constexpr inline const StyleChannelKeyword StyleChannelKeyword::C = StyleChannelKeyword{
  /* ._0 = */ (uint16_t)(1 << 3)
};
/// green
constexpr inline const StyleChannelKeyword StyleChannelKeyword::G = StyleChannelKeyword{
  /* ._0 = */ (uint16_t)(1 << 4)
};
/// hue
constexpr inline const StyleChannelKeyword StyleChannelKeyword::H = StyleChannelKeyword{
  /* ._0 = */ (uint16_t)(1 << 5)
};
/// lightness
constexpr inline const StyleChannelKeyword StyleChannelKeyword::L = StyleChannelKeyword{
  /* ._0 = */ (uint16_t)(1 << 6)
};
/// red
constexpr inline const StyleChannelKeyword StyleChannelKeyword::R = StyleChannelKeyword{
  /* ._0 = */ (uint16_t)(1 << 7)
};
/// saturation
constexpr inline const StyleChannelKeyword StyleChannelKeyword::S = StyleChannelKeyword{
  /* ._0 = */ (uint16_t)(1 << 8)
};
/// whiteness
constexpr inline const StyleChannelKeyword StyleChannelKeyword::W = StyleChannelKeyword{
  /* ._0 = */ (uint16_t)(1 << 9)
};
/// x
constexpr inline const StyleChannelKeyword StyleChannelKeyword::X = StyleChannelKeyword{
  /* ._0 = */ (uint16_t)(1 << 10)
};
/// y
constexpr inline const StyleChannelKeyword StyleChannelKeyword::Y = StyleChannelKeyword{
  /* ._0 = */ (uint16_t)(1 << 11)
};
/// z
constexpr inline const StyleChannelKeyword StyleChannelKeyword::Z = StyleChannelKeyword{
  /* ._0 = */ (uint16_t)(1 << 12)
};

/// A `<length>` without taking `calc` expressions into account
///
/// <https://drafts.csswg.org/css-values/#lengths>
struct StyleNoCalcLength {
  StyleLengthUnit unit;
  StyleCSSFloat value;

  bool operator==(const StyleNoCalcLength& other) const {
    return unit == other.unit &&
           value == other.value;
  }
};

/// A non-calc `<angle>` value.
struct StyleNoCalcAngle {
  StyleAngleUnit unit;
  StyleCSSFloat value;

  bool operator==(const StyleNoCalcAngle& other) const {
    return unit == other.unit &&
           value == other.value;
  }
};

/// A time value according to CSS-VALUES § 6.2.
struct StyleNoCalcTime {
  StyleTimeUnit unit;
  StyleCSSFloat value;

  bool operator==(const StyleNoCalcTime& other) const {
    return unit == other.unit &&
           value == other.value;
  }
};

/// A non-calc `<resolution>` value.
struct StyleNoCalcResolution {
  StyleResolutionUnit unit;
  StyleCSSFloat value;

  bool operator==(const StyleNoCalcResolution& other) const {
    return unit == other.unit &&
           value == other.value;
  }
};

/// A non-calc `<number>` value.
struct StyleNoCalcNumber {
  StyleCSSFloat _0;

  bool operator==(const StyleNoCalcNumber& other) const {
    return _0 == other._0;
  }
};

/// The <random-ua-ident> part of a <random-cache-key>. This is a <custom-ident>
/// starting with `ua-` that is typically automatically constructed by the user agent.
///
/// https://drafts.csswg.org/css-values-5/#valdef-random-ua-ident
struct StyleRandomUaIdent {
  StyleCustomIdent _0;

  bool operator==(const StyleRandomUaIdent& other) const {
    return _0 == other._0;
  }
};

/// A <random-cache-key> that specifies parts of the random cache name.
///
/// https://drafts.csswg.org/css-values-5/#valdef-random-random-cache-key
struct StyleRandomCacheKey {
  /// The author-specified <dashed-ident>, or `DashedIdent::empty()` if absent.
  StyleDashedIdent name;
  /// The <random-ua-ident>, either as author-specified or as constructed to replace
  /// `property-scoped`/`property-index-scoped`, or `RandomUaIdent::empty()` if absent.
  StyleRandomUaIdent ua_ident;
  /// Whether `element-scoped` was specified.
  bool is_element_scoped;

  bool operator==(const StyleRandomCacheKey& other) const {
    return name == other.name &&
           ua_ident == other.ua_ident &&
           is_element_scoped == other.is_element_scoped;
  }
};

/// A <random-key> that specifies how to compute the random base value for
/// a random function. Note that the `auto` value is not modeled as it is
/// immediately converted to the `element-scoped property-index-scoped`
/// cache key format during parsing.
///
/// https://drafts.csswg.org/css-values-5/#typedef-random-key
union StyleRandomKey {
  enum class Tag : uint8_t {
    /// A <number> used directly as the random base value.
    /// TODO(bug 2071971): This is broken if it manages to get into a computed node. Refactor this
    /// away altogether.
    Fixed,
    /// A <random-cache-key> used to generate the random base value.
    CacheKey,
  };

  struct Fixed_Body {
    Tag tag;
    StyleNumber _0;

    bool operator==(const Fixed_Body& other) const {
      return _0 == other._0;
    }
  };

  struct CacheKey_Body {
    Tag tag;
    StyleRandomCacheKey _0;

    bool operator==(const CacheKey_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Fixed_Body fixed;
  CacheKey_Body cache_key;

  static StyleRandomKey Fixed(const StyleNumber &_0) {
    StyleRandomKey result;
    ::new (&result.fixed._0) (StyleNumber)(_0);
    result.tag = Tag::Fixed;
    return result;
  }

  bool IsFixed() const {
    return tag == Tag::Fixed;
  }

  const StyleNumber& AsFixed() const {
    MOZ_DIAGNOSTIC_ASSERT(IsFixed());
    return fixed._0;
  }

  static StyleRandomKey CacheKey(const StyleRandomCacheKey &_0) {
    StyleRandomKey result;
    ::new (&result.cache_key._0) (StyleRandomCacheKey)(_0);
    result.tag = Tag::CacheKey;
    return result;
  }

  bool IsCacheKey() const {
    return tag == Tag::CacheKey;
  }

  const StyleRandomCacheKey& AsCacheKey() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCacheKey());
    return cache_key._0;
  }

  bool operator==(const StyleRandomKey& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Fixed: return fixed == other.fixed;
      case Tag::CacheKey: return cache_key == other.cache_key;

    }
    return true;
  }

  private:
  StyleRandomKey() {

  }
  public:


  ~StyleRandomKey() {
    switch (tag) {
      case Tag::Fixed: fixed.~Fixed_Body(); break;
      case Tag::CacheKey: cache_key.~CacheKey_Body(); break;

    }
  }

  StyleRandomKey(const StyleRandomKey& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Fixed: ::new (&fixed) (Fixed_Body)(other.fixed); break;
      case Tag::CacheKey: ::new (&cache_key) (CacheKey_Body)(other.cache_key); break;

    }
  }
  StyleRandomKey& operator=(const StyleRandomKey& other) {
    if (this != &other) {
      this->~StyleRandomKey();
      new (this) StyleRandomKey(other);
    }
    return *this;
  }
};

/// A leaf node inside a `Calc` expression's AST.
union StyleSpecifiedLeaf {
  enum class Tag : uint8_t {
    /// `<length>`
    Length,
    /// `<angle>`
    Angle,
    /// `<time>`
    Time,
    /// `<resolution>`
    Resolution,
    /// A component of a color.
    ColorComponent,
    /// `<percentage>`
    Percentage,
    /// `<number>`
    Number,
    /// A tree-counting function.
    TreeCountingFunction,
    /// `<random-key>`
    RandomKey,
  };

  struct Length_Body {
    Tag tag;
    StyleNoCalcLength _0;

    bool operator==(const Length_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Angle_Body {
    Tag tag;
    StyleNoCalcAngle _0;

    bool operator==(const Angle_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Time_Body {
    Tag tag;
    StyleNoCalcTime _0;

    bool operator==(const Time_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Resolution_Body {
    Tag tag;
    StyleNoCalcResolution _0;

    bool operator==(const Resolution_Body& other) const {
      return _0 == other._0;
    }
  };

  struct ColorComponent_Body {
    Tag tag;
    StyleChannelKeyword _0;

    bool operator==(const ColorComponent_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Percentage_Body {
    Tag tag;
    StyleCalcPercentageLeaf _0;

    bool operator==(const Percentage_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Number_Body {
    Tag tag;
    StyleNoCalcNumber _0;

    bool operator==(const Number_Body& other) const {
      return _0 == other._0;
    }
  };

  struct TreeCountingFunction_Body {
    Tag tag;
    StyleTreeCountingFunction _0;

    bool operator==(const TreeCountingFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  struct RandomKey_Body {
    Tag tag;
    StyleBox<StyleRandomKey> _0;

    bool operator==(const RandomKey_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Length_Body length;
  Angle_Body angle;
  Time_Body time;
  Resolution_Body resolution;
  ColorComponent_Body color_component;
  Percentage_Body percentage;
  Number_Body number;
  TreeCountingFunction_Body tree_counting_function;
  RandomKey_Body random_key;

  static StyleSpecifiedLeaf Length(const StyleNoCalcLength &_0) {
    StyleSpecifiedLeaf result;
    ::new (&result.length._0) (StyleNoCalcLength)(_0);
    result.tag = Tag::Length;
    return result;
  }

  bool IsLength() const {
    return tag == Tag::Length;
  }

  const StyleNoCalcLength& AsLength() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLength());
    return length._0;
  }

  static StyleSpecifiedLeaf Angle(const StyleNoCalcAngle &_0) {
    StyleSpecifiedLeaf result;
    ::new (&result.angle._0) (StyleNoCalcAngle)(_0);
    result.tag = Tag::Angle;
    return result;
  }

  bool IsAngle() const {
    return tag == Tag::Angle;
  }

  const StyleNoCalcAngle& AsAngle() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAngle());
    return angle._0;
  }

  static StyleSpecifiedLeaf Time(const StyleNoCalcTime &_0) {
    StyleSpecifiedLeaf result;
    ::new (&result.time._0) (StyleNoCalcTime)(_0);
    result.tag = Tag::Time;
    return result;
  }

  bool IsTime() const {
    return tag == Tag::Time;
  }

  const StyleNoCalcTime& AsTime() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTime());
    return time._0;
  }

  static StyleSpecifiedLeaf Resolution(const StyleNoCalcResolution &_0) {
    StyleSpecifiedLeaf result;
    ::new (&result.resolution._0) (StyleNoCalcResolution)(_0);
    result.tag = Tag::Resolution;
    return result;
  }

  bool IsResolution() const {
    return tag == Tag::Resolution;
  }

  const StyleNoCalcResolution& AsResolution() const {
    MOZ_DIAGNOSTIC_ASSERT(IsResolution());
    return resolution._0;
  }

  static StyleSpecifiedLeaf ColorComponent(const StyleChannelKeyword &_0) {
    StyleSpecifiedLeaf result;
    ::new (&result.color_component._0) (StyleChannelKeyword)(_0);
    result.tag = Tag::ColorComponent;
    return result;
  }

  bool IsColorComponent() const {
    return tag == Tag::ColorComponent;
  }

  const StyleChannelKeyword& AsColorComponent() const {
    MOZ_DIAGNOSTIC_ASSERT(IsColorComponent());
    return color_component._0;
  }

  static StyleSpecifiedLeaf Percentage(const StyleCalcPercentageLeaf &_0) {
    StyleSpecifiedLeaf result;
    ::new (&result.percentage._0) (StyleCalcPercentageLeaf)(_0);
    result.tag = Tag::Percentage;
    return result;
  }

  bool IsPercentage() const {
    return tag == Tag::Percentage;
  }

  const StyleCalcPercentageLeaf& AsPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPercentage());
    return percentage._0;
  }

  static StyleSpecifiedLeaf Number(const StyleNoCalcNumber &_0) {
    StyleSpecifiedLeaf result;
    ::new (&result.number._0) (StyleNoCalcNumber)(_0);
    result.tag = Tag::Number;
    return result;
  }

  bool IsNumber() const {
    return tag == Tag::Number;
  }

  const StyleNoCalcNumber& AsNumber() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNumber());
    return number._0;
  }

  static StyleSpecifiedLeaf TreeCountingFunction(const StyleTreeCountingFunction &_0) {
    StyleSpecifiedLeaf result;
    ::new (&result.tree_counting_function._0) (StyleTreeCountingFunction)(_0);
    result.tag = Tag::TreeCountingFunction;
    return result;
  }

  bool IsTreeCountingFunction() const {
    return tag == Tag::TreeCountingFunction;
  }

  const StyleTreeCountingFunction& AsTreeCountingFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTreeCountingFunction());
    return tree_counting_function._0;
  }

  static StyleSpecifiedLeaf RandomKey(const StyleBox<StyleRandomKey> &_0) {
    StyleSpecifiedLeaf result;
    ::new (&result.random_key._0) (StyleBox<StyleRandomKey>)(_0);
    result.tag = Tag::RandomKey;
    return result;
  }

  bool IsRandomKey() const {
    return tag == Tag::RandomKey;
  }

  const StyleBox<StyleRandomKey>& AsRandomKey() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRandomKey());
    return random_key._0;
  }

  bool operator==(const StyleSpecifiedLeaf& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Length: return length == other.length;
      case Tag::Angle: return angle == other.angle;
      case Tag::Time: return time == other.time;
      case Tag::Resolution: return resolution == other.resolution;
      case Tag::ColorComponent: return color_component == other.color_component;
      case Tag::Percentage: return percentage == other.percentage;
      case Tag::Number: return number == other.number;
      case Tag::TreeCountingFunction: return tree_counting_function == other.tree_counting_function;
      case Tag::RandomKey: return random_key == other.random_key;

    }
    return true;
  }

  private:
  StyleSpecifiedLeaf() {

  }
  public:


  ~StyleSpecifiedLeaf() {
    switch (tag) {
      case Tag::Length: length.~Length_Body(); break;
      case Tag::Angle: angle.~Angle_Body(); break;
      case Tag::Time: time.~Time_Body(); break;
      case Tag::Resolution: resolution.~Resolution_Body(); break;
      case Tag::ColorComponent: color_component.~ColorComponent_Body(); break;
      case Tag::Percentage: percentage.~Percentage_Body(); break;
      case Tag::Number: number.~Number_Body(); break;
      case Tag::TreeCountingFunction: tree_counting_function.~TreeCountingFunction_Body(); break;
      case Tag::RandomKey: random_key.~RandomKey_Body(); break;

    }
  }

  StyleSpecifiedLeaf(const StyleSpecifiedLeaf& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Length: ::new (&length) (Length_Body)(other.length); break;
      case Tag::Angle: ::new (&angle) (Angle_Body)(other.angle); break;
      case Tag::Time: ::new (&time) (Time_Body)(other.time); break;
      case Tag::Resolution: ::new (&resolution) (Resolution_Body)(other.resolution); break;
      case Tag::ColorComponent: ::new (&color_component) (ColorComponent_Body)(other.color_component); break;
      case Tag::Percentage: ::new (&percentage) (Percentage_Body)(other.percentage); break;
      case Tag::Number: ::new (&number) (Number_Body)(other.number); break;
      case Tag::TreeCountingFunction: ::new (&tree_counting_function) (TreeCountingFunction_Body)(other.tree_counting_function); break;
      case Tag::RandomKey: ::new (&random_key) (RandomKey_Body)(other.random_key); break;

    }
  }
  StyleSpecifiedLeaf& operator=(const StyleSpecifiedLeaf& other) {
    if (this != &other) {
      this->~StyleSpecifiedLeaf();
      new (this) StyleSpecifiedLeaf(other);
    }
    return *this;
  }
};

/// A calc node representation for specified values.
using StyleSpecifiedCalcNode = StyleGenericCalcNode<StyleSpecifiedLeaf>;

/// A single color component.
template<typename ValueType>
union StyleColorComponent {
  enum class Tag : uint8_t {
    /// The "none" keyword.
    None,
    /// A absolute value.
    Value,
    /// A channel keyword, e.g. `r`, `l`, `alpha`, etc.
    ChannelKeyword,
    /// A calc() value.
    Calc,
    /// Used when alpha components are not specified.
    AlphaOmitted,
  };

  struct Value_Body {
    Tag tag;
    ValueType _0;

    bool operator==(const Value_Body& other) const {
      return _0 == other._0;
    }
  };

  struct ChannelKeyword_Body {
    Tag tag;
    StyleChannelKeyword _0;

    bool operator==(const ChannelKeyword_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Calc_Body {
    Tag tag;
    StyleBox<StyleSpecifiedCalcNode> _0;

    bool operator==(const Calc_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Value_Body value;
  ChannelKeyword_Body channel_keyword;
  Calc_Body calc;

  static StyleColorComponent None() {
    StyleColorComponent result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleColorComponent Value(const ValueType &_0) {
    StyleColorComponent result;
    ::new (&result.value._0) (ValueType)(_0);
    result.tag = Tag::Value;
    return result;
  }

  bool IsValue() const {
    return tag == Tag::Value;
  }

  const ValueType& AsValue() const {
    MOZ_DIAGNOSTIC_ASSERT(IsValue());
    return value._0;
  }

  static StyleColorComponent ChannelKeyword(const StyleChannelKeyword &_0) {
    StyleColorComponent result;
    ::new (&result.channel_keyword._0) (StyleChannelKeyword)(_0);
    result.tag = Tag::ChannelKeyword;
    return result;
  }

  bool IsChannelKeyword() const {
    return tag == Tag::ChannelKeyword;
  }

  const StyleChannelKeyword& AsChannelKeyword() const {
    MOZ_DIAGNOSTIC_ASSERT(IsChannelKeyword());
    return channel_keyword._0;
  }

  static StyleColorComponent Calc(const StyleBox<StyleSpecifiedCalcNode> &_0) {
    StyleColorComponent result;
    ::new (&result.calc._0) (StyleBox<StyleSpecifiedCalcNode>)(_0);
    result.tag = Tag::Calc;
    return result;
  }

  bool IsCalc() const {
    return tag == Tag::Calc;
  }

  const StyleBox<StyleSpecifiedCalcNode>& AsCalc() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCalc());
    return calc._0;
  }

  static StyleColorComponent AlphaOmitted() {
    StyleColorComponent result;
    result.tag = Tag::AlphaOmitted;
    return result;
  }

  bool IsAlphaOmitted() const {
    return tag == Tag::AlphaOmitted;
  }

  bool operator==(const StyleColorComponent& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Value: return value == other.value;
      case Tag::ChannelKeyword: return channel_keyword == other.channel_keyword;
      case Tag::Calc: return calc == other.calc;
      default: break;
    }
    return true;
  }

  private:
  StyleColorComponent() {

  }
  public:


  ~StyleColorComponent() {
    switch (tag) {
      case Tag::Value: value.~Value_Body(); break;
      case Tag::ChannelKeyword: channel_keyword.~ChannelKeyword_Body(); break;
      case Tag::Calc: calc.~Calc_Body(); break;
      default: break;
    }
  }

  StyleColorComponent(const StyleColorComponent& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Value: ::new (&value) (Value_Body)(other.value); break;
      case Tag::ChannelKeyword: ::new (&channel_keyword) (ChannelKeyword_Body)(other.channel_keyword); break;
      case Tag::Calc: ::new (&calc) (Calc_Body)(other.calc); break;
      default: break;
    }
  }
  StyleColorComponent& operator=(const StyleColorComponent& other) {
    if (this != &other) {
      this->~StyleColorComponent();
      new (this) StyleColorComponent(other);
    }
    return *this;
  }
};

/// Either an angle or a number.
union StyleNumberOrAngleComponent {
  enum class Tag : uint8_t {
    /// `<number>`.
    Number,
    /// `<angle>`
    /// The value as a number of degrees.
    Angle,
  };

  struct Number_Body {
    Tag tag;
    float _0;

    bool operator==(const Number_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Angle_Body {
    Tag tag;
    float _0;

    bool operator==(const Angle_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Number_Body number;
  Angle_Body angle;

  static StyleNumberOrAngleComponent Number(const float &_0) {
    StyleNumberOrAngleComponent result;
    ::new (&result.number._0) (float)(_0);
    result.tag = Tag::Number;
    return result;
  }

  bool IsNumber() const {
    return tag == Tag::Number;
  }

  const float& AsNumber() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNumber());
    return number._0;
  }

  static StyleNumberOrAngleComponent Angle(const float &_0) {
    StyleNumberOrAngleComponent result;
    ::new (&result.angle._0) (float)(_0);
    result.tag = Tag::Angle;
    return result;
  }

  bool IsAngle() const {
    return tag == Tag::Angle;
  }

  const float& AsAngle() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAngle());
    return angle._0;
  }

  bool operator==(const StyleNumberOrAngleComponent& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Number: return number == other.number;
      case Tag::Angle: return angle == other.angle;

    }
    return true;
  }

  private:
  StyleNumberOrAngleComponent() {

  }
  public:


  ~StyleNumberOrAngleComponent() {
    switch (tag) {
      case Tag::Number: number.~Number_Body(); break;
      case Tag::Angle: angle.~Angle_Body(); break;

    }
  }

  StyleNumberOrAngleComponent(const StyleNumberOrAngleComponent& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Number: ::new (&number) (Number_Body)(other.number); break;
      case Tag::Angle: ::new (&angle) (Angle_Body)(other.angle); break;

    }
  }
  StyleNumberOrAngleComponent& operator=(const StyleNumberOrAngleComponent& other) {
    if (this != &other) {
      this->~StyleNumberOrAngleComponent();
      new (this) StyleNumberOrAngleComponent(other);
    }
    return *this;
  }
};

/// Represents a specified color function.
template<typename OriginColor>
union StyleColorFunction {
  enum class Tag : uint8_t {
    /// <https://drafts.csswg.org/css-color-4/#rgb-functions>
    Rgb,
    /// <https://drafts.csswg.org/css-color-4/#the-hsl-notation>
    Hsl,
    /// <https://drafts.csswg.org/css-color-4/#the-hwb-notation>
    Hwb,
    /// <https://drafts.csswg.org/css-color-4/#specifying-lab-lch>
    Lab,
    /// <https://drafts.csswg.org/css-color-4/#specifying-lab-lch>
    Lch,
    /// <https://drafts.csswg.org/css-color-4/#specifying-oklab-oklch>
    Oklab,
    /// <https://drafts.csswg.org/css-color-4/#specifying-oklab-oklch>
    Oklch,
    /// <https://drafts.csswg.org/css-color-4/#color-function>
    Color,
    /// <https://drafts.csswg.org/css-color-5/#relative-alpha>
    Alpha,
  };

  struct Rgb_Body {
    Tag tag;
    StyleOptional<OriginColor> _0;
    StyleColorComponent<StyleNumberOrPercentageComponent> _1;
    StyleColorComponent<StyleNumberOrPercentageComponent> _2;
    StyleColorComponent<StyleNumberOrPercentageComponent> _3;
    StyleColorComponent<StyleNumberOrPercentageComponent> _4;

    bool operator==(const Rgb_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2 &&
             _3 == other._3 &&
             _4 == other._4;
    }
  };

  struct Hsl_Body {
    Tag tag;
    StyleOptional<OriginColor> _0;
    StyleColorComponent<StyleNumberOrAngleComponent> _1;
    StyleColorComponent<StyleNumberOrPercentageComponent> _2;
    StyleColorComponent<StyleNumberOrPercentageComponent> _3;
    StyleColorComponent<StyleNumberOrPercentageComponent> _4;

    bool operator==(const Hsl_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2 &&
             _3 == other._3 &&
             _4 == other._4;
    }
  };

  struct Hwb_Body {
    Tag tag;
    StyleOptional<OriginColor> _0;
    StyleColorComponent<StyleNumberOrAngleComponent> _1;
    StyleColorComponent<StyleNumberOrPercentageComponent> _2;
    StyleColorComponent<StyleNumberOrPercentageComponent> _3;
    StyleColorComponent<StyleNumberOrPercentageComponent> _4;

    bool operator==(const Hwb_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2 &&
             _3 == other._3 &&
             _4 == other._4;
    }
  };

  struct Lab_Body {
    Tag tag;
    StyleOptional<OriginColor> _0;
    StyleColorComponent<StyleNumberOrPercentageComponent> _1;
    StyleColorComponent<StyleNumberOrPercentageComponent> _2;
    StyleColorComponent<StyleNumberOrPercentageComponent> _3;
    StyleColorComponent<StyleNumberOrPercentageComponent> _4;

    bool operator==(const Lab_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2 &&
             _3 == other._3 &&
             _4 == other._4;
    }
  };

  struct Lch_Body {
    Tag tag;
    StyleOptional<OriginColor> _0;
    StyleColorComponent<StyleNumberOrPercentageComponent> _1;
    StyleColorComponent<StyleNumberOrPercentageComponent> _2;
    StyleColorComponent<StyleNumberOrAngleComponent> _3;
    StyleColorComponent<StyleNumberOrPercentageComponent> _4;

    bool operator==(const Lch_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2 &&
             _3 == other._3 &&
             _4 == other._4;
    }
  };

  struct Oklab_Body {
    Tag tag;
    StyleOptional<OriginColor> _0;
    StyleColorComponent<StyleNumberOrPercentageComponent> _1;
    StyleColorComponent<StyleNumberOrPercentageComponent> _2;
    StyleColorComponent<StyleNumberOrPercentageComponent> _3;
    StyleColorComponent<StyleNumberOrPercentageComponent> _4;

    bool operator==(const Oklab_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2 &&
             _3 == other._3 &&
             _4 == other._4;
    }
  };

  struct Oklch_Body {
    Tag tag;
    StyleOptional<OriginColor> _0;
    StyleColorComponent<StyleNumberOrPercentageComponent> _1;
    StyleColorComponent<StyleNumberOrPercentageComponent> _2;
    StyleColorComponent<StyleNumberOrAngleComponent> _3;
    StyleColorComponent<StyleNumberOrPercentageComponent> _4;

    bool operator==(const Oklch_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2 &&
             _3 == other._3 &&
             _4 == other._4;
    }
  };

  struct Color_Body {
    Tag tag;
    StyleOptional<OriginColor> _0;
    StyleColorComponent<StyleNumberOrPercentageComponent> _1;
    StyleColorComponent<StyleNumberOrPercentageComponent> _2;
    StyleColorComponent<StyleNumberOrPercentageComponent> _3;
    StyleColorComponent<StyleNumberOrPercentageComponent> _4;
    StyleColorSpace _5;

    bool operator==(const Color_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2 &&
             _3 == other._3 &&
             _4 == other._4 &&
             _5 == other._5;
    }
  };

  struct Alpha_Body {
    Tag tag;
    OriginColor _0;
    StyleColorComponent<StyleNumberOrPercentageComponent> _1;

    bool operator==(const Alpha_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct {
    Tag tag;
  };
  Rgb_Body rgb;
  Hsl_Body hsl;
  Hwb_Body hwb;
  Lab_Body lab;
  Lch_Body lch;
  Oklab_Body oklab;
  Oklch_Body oklch;
  Color_Body color;
  Alpha_Body alpha;

  static StyleColorFunction Rgb(const StyleOptional<OriginColor> &_0,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_1,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_2,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_3,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_4) {
    StyleColorFunction result;
    ::new (&result.rgb._0) (StyleOptional<OriginColor>)(_0);
    ::new (&result.rgb._1) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_1);
    ::new (&result.rgb._2) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_2);
    ::new (&result.rgb._3) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_3);
    ::new (&result.rgb._4) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_4);
    result.tag = Tag::Rgb;
    return result;
  }

  bool IsRgb() const {
    return tag == Tag::Rgb;
  }

  const Rgb_Body& AsRgb() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRgb());
    return rgb;
  }

  static StyleColorFunction Hsl(const StyleOptional<OriginColor> &_0,
                                const StyleColorComponent<StyleNumberOrAngleComponent> &_1,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_2,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_3,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_4) {
    StyleColorFunction result;
    ::new (&result.hsl._0) (StyleOptional<OriginColor>)(_0);
    ::new (&result.hsl._1) (StyleColorComponent<StyleNumberOrAngleComponent>)(_1);
    ::new (&result.hsl._2) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_2);
    ::new (&result.hsl._3) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_3);
    ::new (&result.hsl._4) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_4);
    result.tag = Tag::Hsl;
    return result;
  }

  bool IsHsl() const {
    return tag == Tag::Hsl;
  }

  const Hsl_Body& AsHsl() const {
    MOZ_DIAGNOSTIC_ASSERT(IsHsl());
    return hsl;
  }

  static StyleColorFunction Hwb(const StyleOptional<OriginColor> &_0,
                                const StyleColorComponent<StyleNumberOrAngleComponent> &_1,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_2,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_3,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_4) {
    StyleColorFunction result;
    ::new (&result.hwb._0) (StyleOptional<OriginColor>)(_0);
    ::new (&result.hwb._1) (StyleColorComponent<StyleNumberOrAngleComponent>)(_1);
    ::new (&result.hwb._2) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_2);
    ::new (&result.hwb._3) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_3);
    ::new (&result.hwb._4) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_4);
    result.tag = Tag::Hwb;
    return result;
  }

  bool IsHwb() const {
    return tag == Tag::Hwb;
  }

  const Hwb_Body& AsHwb() const {
    MOZ_DIAGNOSTIC_ASSERT(IsHwb());
    return hwb;
  }

  static StyleColorFunction Lab(const StyleOptional<OriginColor> &_0,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_1,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_2,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_3,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_4) {
    StyleColorFunction result;
    ::new (&result.lab._0) (StyleOptional<OriginColor>)(_0);
    ::new (&result.lab._1) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_1);
    ::new (&result.lab._2) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_2);
    ::new (&result.lab._3) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_3);
    ::new (&result.lab._4) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_4);
    result.tag = Tag::Lab;
    return result;
  }

  bool IsLab() const {
    return tag == Tag::Lab;
  }

  const Lab_Body& AsLab() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLab());
    return lab;
  }

  static StyleColorFunction Lch(const StyleOptional<OriginColor> &_0,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_1,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_2,
                                const StyleColorComponent<StyleNumberOrAngleComponent> &_3,
                                const StyleColorComponent<StyleNumberOrPercentageComponent> &_4) {
    StyleColorFunction result;
    ::new (&result.lch._0) (StyleOptional<OriginColor>)(_0);
    ::new (&result.lch._1) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_1);
    ::new (&result.lch._2) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_2);
    ::new (&result.lch._3) (StyleColorComponent<StyleNumberOrAngleComponent>)(_3);
    ::new (&result.lch._4) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_4);
    result.tag = Tag::Lch;
    return result;
  }

  bool IsLch() const {
    return tag == Tag::Lch;
  }

  const Lch_Body& AsLch() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLch());
    return lch;
  }

  static StyleColorFunction Oklab(const StyleOptional<OriginColor> &_0,
                                  const StyleColorComponent<StyleNumberOrPercentageComponent> &_1,
                                  const StyleColorComponent<StyleNumberOrPercentageComponent> &_2,
                                  const StyleColorComponent<StyleNumberOrPercentageComponent> &_3,
                                  const StyleColorComponent<StyleNumberOrPercentageComponent> &_4) {
    StyleColorFunction result;
    ::new (&result.oklab._0) (StyleOptional<OriginColor>)(_0);
    ::new (&result.oklab._1) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_1);
    ::new (&result.oklab._2) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_2);
    ::new (&result.oklab._3) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_3);
    ::new (&result.oklab._4) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_4);
    result.tag = Tag::Oklab;
    return result;
  }

  bool IsOklab() const {
    return tag == Tag::Oklab;
  }

  const Oklab_Body& AsOklab() const {
    MOZ_DIAGNOSTIC_ASSERT(IsOklab());
    return oklab;
  }

  static StyleColorFunction Oklch(const StyleOptional<OriginColor> &_0,
                                  const StyleColorComponent<StyleNumberOrPercentageComponent> &_1,
                                  const StyleColorComponent<StyleNumberOrPercentageComponent> &_2,
                                  const StyleColorComponent<StyleNumberOrAngleComponent> &_3,
                                  const StyleColorComponent<StyleNumberOrPercentageComponent> &_4) {
    StyleColorFunction result;
    ::new (&result.oklch._0) (StyleOptional<OriginColor>)(_0);
    ::new (&result.oklch._1) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_1);
    ::new (&result.oklch._2) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_2);
    ::new (&result.oklch._3) (StyleColorComponent<StyleNumberOrAngleComponent>)(_3);
    ::new (&result.oklch._4) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_4);
    result.tag = Tag::Oklch;
    return result;
  }

  bool IsOklch() const {
    return tag == Tag::Oklch;
  }

  const Oklch_Body& AsOklch() const {
    MOZ_DIAGNOSTIC_ASSERT(IsOklch());
    return oklch;
  }

  static StyleColorFunction Color(const StyleOptional<OriginColor> &_0,
                                  const StyleColorComponent<StyleNumberOrPercentageComponent> &_1,
                                  const StyleColorComponent<StyleNumberOrPercentageComponent> &_2,
                                  const StyleColorComponent<StyleNumberOrPercentageComponent> &_3,
                                  const StyleColorComponent<StyleNumberOrPercentageComponent> &_4,
                                  const StyleColorSpace &_5) {
    StyleColorFunction result;
    ::new (&result.color._0) (StyleOptional<OriginColor>)(_0);
    ::new (&result.color._1) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_1);
    ::new (&result.color._2) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_2);
    ::new (&result.color._3) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_3);
    ::new (&result.color._4) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_4);
    ::new (&result.color._5) (StyleColorSpace)(_5);
    result.tag = Tag::Color;
    return result;
  }

  bool IsColor() const {
    return tag == Tag::Color;
  }

  const Color_Body& AsColor() const {
    MOZ_DIAGNOSTIC_ASSERT(IsColor());
    return color;
  }

  static StyleColorFunction Alpha(const OriginColor &_0,
                                  const StyleColorComponent<StyleNumberOrPercentageComponent> &_1) {
    StyleColorFunction result;
    ::new (&result.alpha._0) (OriginColor)(_0);
    ::new (&result.alpha._1) (StyleColorComponent<StyleNumberOrPercentageComponent>)(_1);
    result.tag = Tag::Alpha;
    return result;
  }

  bool IsAlpha() const {
    return tag == Tag::Alpha;
  }

  const Alpha_Body& AsAlpha() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAlpha());
    return alpha;
  }

  bool operator==(const StyleColorFunction& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Rgb: return rgb == other.rgb;
      case Tag::Hsl: return hsl == other.hsl;
      case Tag::Hwb: return hwb == other.hwb;
      case Tag::Lab: return lab == other.lab;
      case Tag::Lch: return lch == other.lch;
      case Tag::Oklab: return oklab == other.oklab;
      case Tag::Oklch: return oklch == other.oklch;
      case Tag::Color: return color == other.color;
      case Tag::Alpha: return alpha == other.alpha;

    }
    return true;
  }

  private:
  StyleColorFunction() {

  }
  public:


  ~StyleColorFunction() {
    switch (tag) {
      case Tag::Rgb: rgb.~Rgb_Body(); break;
      case Tag::Hsl: hsl.~Hsl_Body(); break;
      case Tag::Hwb: hwb.~Hwb_Body(); break;
      case Tag::Lab: lab.~Lab_Body(); break;
      case Tag::Lch: lch.~Lch_Body(); break;
      case Tag::Oklab: oklab.~Oklab_Body(); break;
      case Tag::Oklch: oklch.~Oklch_Body(); break;
      case Tag::Color: color.~Color_Body(); break;
      case Tag::Alpha: alpha.~Alpha_Body(); break;

    }
  }

  StyleColorFunction(const StyleColorFunction& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Rgb: ::new (&rgb) (Rgb_Body)(other.rgb); break;
      case Tag::Hsl: ::new (&hsl) (Hsl_Body)(other.hsl); break;
      case Tag::Hwb: ::new (&hwb) (Hwb_Body)(other.hwb); break;
      case Tag::Lab: ::new (&lab) (Lab_Body)(other.lab); break;
      case Tag::Lch: ::new (&lch) (Lch_Body)(other.lch); break;
      case Tag::Oklab: ::new (&oklab) (Oklab_Body)(other.oklab); break;
      case Tag::Oklch: ::new (&oklch) (Oklch_Body)(other.oklch); break;
      case Tag::Color: ::new (&color) (Color_Body)(other.color); break;
      case Tag::Alpha: ::new (&alpha) (Alpha_Body)(other.alpha); break;

    }
  }
  StyleColorFunction& operator=(const StyleColorFunction& other) {
    if (this != &other) {
      this->~StyleColorFunction();
      new (this) StyleColorFunction(other);
    }
    return *this;
  }
  bool DependsOnCurrentColor() const;
};

/// https://drafts.csswg.org/css-color-4/#color-interpolation-method
struct StyleColorInterpolationMethod {
  /// The color-space the interpolation should be done in.
  StyleColorSpace space;
  /// The hue interpolation method.
  StyleHueInterpolationMethod hue;

  bool operator==(const StyleColorInterpolationMethod& other) const {
    return space == other.space &&
           hue == other.hue;
  }
};

/// One `(color, percentage)` component of a `color-mix()` expression.
template<typename Color, typename Percentage>
struct StyleGenericColorMixItem {
  Color color;
  /// [Optional::None] when the percentage was omitted next to a calc() sibling.
  StyleOptional<Percentage> percentage;

  bool operator==(const StyleGenericColorMixItem& other) const {
    return color == other.color &&
           percentage == other.percentage;
  }
};

/// Flags used to modify the calculation of a color mix result.
struct StyleColorMixFlags {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleColorMixFlags operator~() const {
    return StyleColorMixFlags { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleColorMixFlags operator|(const StyleColorMixFlags& other) const {
    return StyleColorMixFlags { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleColorMixFlags& operator|=(const StyleColorMixFlags& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleColorMixFlags operator&(const StyleColorMixFlags& other) const {
    return StyleColorMixFlags { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleColorMixFlags& operator&=(const StyleColorMixFlags& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleColorMixFlags operator^(const StyleColorMixFlags& other) const {
    return StyleColorMixFlags { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleColorMixFlags& operator^=(const StyleColorMixFlags& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleColorMixFlags& other) const {
    return _0 == other._0;
  }
  static const StyleColorMixFlags NORMALIZE_WEIGHTS;
  static const StyleColorMixFlags RESULT_IN_MODERN_SYNTAX;
};
/// Normalize the weights of the mix.
constexpr inline const StyleColorMixFlags StyleColorMixFlags::NORMALIZE_WEIGHTS = StyleColorMixFlags{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// The result should always be converted to the modern color syntax.
constexpr inline const StyleColorMixFlags StyleColorMixFlags::RESULT_IN_MODERN_SYNTAX = StyleColorMixFlags{
  /* ._0 = */ (uint8_t)(1 << 1)
};

/// A restricted version of the css `color-mix()` function, which only supports
/// percentages.
///
/// https://drafts.csswg.org/css-color-5/#color-mix
template<typename Color, typename Percentage>
struct StyleGenericColorMix {
  StyleColorInterpolationMethod interpolation;
  StyleOwnedSlice<StyleGenericColorMixItem<Color, Percentage>> items;
  StyleColorMixFlags flags;

  bool operator==(const StyleGenericColorMix& other) const {
    return interpolation == other.interpolation &&
           items == other.items &&
           flags == other.flags;
  }
  bool DependsOnCurrentColor() const;
};

/// This struct represents a combined color from a numeric color and
/// the current foreground color (currentcolor keyword).
template<typename Percentage>
struct StyleGenericColor {
  enum class Tag {
    /// The actual numeric color.
    Absolute,
    /// A unresolvable color.
    ColorFunction,
    /// The `CurrentColor` keyword.
    CurrentColor,
    /// The color-mix() function.
    ColorMix,
    /// The contrast-color() function.
    ContrastColor,
  };

  struct StyleAbsolute_Body {
    StyleAbsoluteColor _0;

    bool operator==(const StyleAbsolute_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleColorFunction_Body {
    StyleBox<StyleColorFunction<StyleGenericColor>> _0;

    bool operator==(const StyleColorFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleColorMix_Body {
    StyleBox<StyleGenericColorMix<StyleGenericColor, Percentage>> _0;

    bool operator==(const StyleColorMix_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleContrastColor_Body {
    StyleBox<StyleGenericColor> _0;

    bool operator==(const StyleContrastColor_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleAbsolute_Body absolute;
    StyleColorFunction_Body color_function;
    StyleColorMix_Body color_mix;
    StyleContrastColor_Body contrast_color;
  };

  static StyleGenericColor Absolute(const StyleAbsoluteColor &_0) {
    StyleGenericColor result;
    ::new (&result.absolute._0) (StyleAbsoluteColor)(_0);
    result.tag = Tag::Absolute;
    return result;
  }

  bool IsAbsolute() const {
    return tag == Tag::Absolute;
  }

  const StyleAbsoluteColor& AsAbsolute() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAbsolute());
    return absolute._0;
  }

  static StyleGenericColor ColorFunction(const StyleBox<StyleColorFunction<StyleGenericColor>> &_0) {
    StyleGenericColor result;
    ::new (&result.color_function._0) (StyleBox<StyleColorFunction<StyleGenericColor>>)(_0);
    result.tag = Tag::ColorFunction;
    return result;
  }

  bool IsColorFunction() const {
    return tag == Tag::ColorFunction;
  }

  const StyleBox<StyleColorFunction<StyleGenericColor>>& AsColorFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsColorFunction());
    return color_function._0;
  }

  static StyleGenericColor CurrentColor() {
    StyleGenericColor result;
    result.tag = Tag::CurrentColor;
    return result;
  }

  bool IsCurrentColor() const {
    return tag == Tag::CurrentColor;
  }

  static StyleGenericColor ColorMix(const StyleBox<StyleGenericColorMix<StyleGenericColor, Percentage>> &_0) {
    StyleGenericColor result;
    ::new (&result.color_mix._0) (StyleBox<StyleGenericColorMix<StyleGenericColor, Percentage>>)(_0);
    result.tag = Tag::ColorMix;
    return result;
  }

  bool IsColorMix() const {
    return tag == Tag::ColorMix;
  }

  const StyleBox<StyleGenericColorMix<StyleGenericColor, Percentage>>& AsColorMix() const {
    MOZ_DIAGNOSTIC_ASSERT(IsColorMix());
    return color_mix._0;
  }

  static StyleGenericColor ContrastColor(const StyleBox<StyleGenericColor> &_0) {
    StyleGenericColor result;
    ::new (&result.contrast_color._0) (StyleBox<StyleGenericColor>)(_0);
    result.tag = Tag::ContrastColor;
    return result;
  }

  bool IsContrastColor() const {
    return tag == Tag::ContrastColor;
  }

  const StyleBox<StyleGenericColor>& AsContrastColor() const {
    MOZ_DIAGNOSTIC_ASSERT(IsContrastColor());
    return contrast_color._0;
  }

  bool operator==(const StyleGenericColor& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Absolute: return absolute == other.absolute;
      case Tag::ColorFunction: return color_function == other.color_function;
      case Tag::ColorMix: return color_mix == other.color_mix;
      case Tag::ContrastColor: return contrast_color == other.contrast_color;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericColor() {

  }
  public:


  ~StyleGenericColor() {
    switch (tag) {
      case Tag::Absolute: absolute.~StyleAbsolute_Body(); break;
      case Tag::ColorFunction: color_function.~StyleColorFunction_Body(); break;
      case Tag::ColorMix: color_mix.~StyleColorMix_Body(); break;
      case Tag::ContrastColor: contrast_color.~StyleContrastColor_Body(); break;
      default: break;
    }
  }

  StyleGenericColor(const StyleGenericColor& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Absolute: ::new (&absolute) (StyleAbsolute_Body)(other.absolute); break;
      case Tag::ColorFunction: ::new (&color_function) (StyleColorFunction_Body)(other.color_function); break;
      case Tag::ColorMix: ::new (&color_mix) (StyleColorMix_Body)(other.color_mix); break;
      case Tag::ContrastColor: ::new (&contrast_color) (StyleContrastColor_Body)(other.contrast_color); break;
      default: break;
    }
  }
  StyleGenericColor& operator=(const StyleGenericColor& other) {
    if (this != &other) {
      this->~StyleGenericColor();
      new (this) StyleGenericColor(other);
    }
    return *this;
  }
  static inline StyleGenericColor FromColor(nscolor);

  static inline StyleGenericColor Transparent();
  static inline StyleGenericColor Black();
  static inline StyleGenericColor White();

  bool MaybeTransparent() const;

  bool DependsOnCurrentColor() const;

  /**
   * Compute the final color, taking into account the foreground color.
   **/
  StyleAbsoluteColor ResolveColor(const StyleAbsoluteColor&) const;

  /**
   * Compute the final color, taking into account the foreground color from the
   * frame's ComputedStyle.
   */
  nscolor CalcColor(const nsIFrame*) const;
  /**
   * Compute the final color, taking into account the foreground color from the
   * style.
   */
  nscolor CalcColor(const ComputedStyle&) const;
  /**
   * Compute the final color, making the argument the foreground color.
   */
  nscolor CalcColor(nscolor) const;
  nscolor CalcColor(const StyleAbsoluteColor&) const;
};

/// An animated value for `<color>`.
using StyleColor = StyleGenericColor<StylePercentage>;

/// A wrapper of Length, whose value must be >= 0.
using StyleNonNegativeLength = StyleNonNegative<StyleLength>;

/// A generic value for the `drop-shadow()` filter and the `text-shadow` property.
///
/// Contrary to the canonical order from the spec, the color is serialised
/// first, like in Gecko and Webkit.
template<typename Color, typename SizeLength, typename ShapeLength>
struct StyleGenericSimpleShadow {
  /// Color.
  Color color;
  /// Horizontal radius.
  SizeLength horizontal;
  /// Vertical radius.
  SizeLength vertical;
  /// Blur radius.
  ShapeLength blur;

  bool operator==(const StyleGenericSimpleShadow& other) const {
    return color == other.color &&
           horizontal == other.horizontal &&
           vertical == other.vertical &&
           blur == other.blur;
  }
};

/// A computed value for the `drop-shadow()` filter.
using StyleSimpleShadow = StyleGenericSimpleShadow<StyleColor, StyleLength, StyleNonNegativeLength>;

/// A wrapper of values between zero and one.
template<typename T>
using StyleZeroToOne = T;

/// A generic value for a single `filter`.
template<typename Angle, typename Factor, typename Length, typename Shadow, typename U>
struct StyleGenericFilter {
  enum class Tag : uint8_t {
    /// `blur(<length>)`
    Blur,
    /// `brightness(<factor>)`
    Brightness,
    /// `contrast(<factor>)`
    Contrast,
    /// `grayscale(<factor>)`
    Grayscale,
    /// `hue-rotate(<angle>)`
    HueRotate,
    /// `invert(<factor>)`
    Invert,
    /// `opacity(<factor>)`
    Opacity,
    /// `saturate(<factor>)`
    Saturate,
    /// `sepia(<factor>)`
    Sepia,
    /// `drop-shadow(...)`
    DropShadow,
    /// `<url>`
    Url,
  };

  struct StyleBlur_Body {
    StyleNonNegative<Length> _0;

    bool operator==(const StyleBlur_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleBrightness_Body {
    StyleNonNegative<Factor> _0;

    bool operator==(const StyleBrightness_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleContrast_Body {
    StyleNonNegative<Factor> _0;

    bool operator==(const StyleContrast_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleGrayscale_Body {
    StyleZeroToOne<Factor> _0;

    bool operator==(const StyleGrayscale_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleHueRotate_Body {
    Angle _0;

    bool operator==(const StyleHueRotate_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleInvert_Body {
    StyleZeroToOne<Factor> _0;

    bool operator==(const StyleInvert_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleOpacity_Body {
    StyleZeroToOne<Factor> _0;

    bool operator==(const StyleOpacity_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleSaturate_Body {
    StyleNonNegative<Factor> _0;

    bool operator==(const StyleSaturate_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleSepia_Body {
    StyleZeroToOne<Factor> _0;

    bool operator==(const StyleSepia_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleDropShadow_Body {
    Shadow _0;

    bool operator==(const StyleDropShadow_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleUrl_Body {
    U _0;

    bool operator==(const StyleUrl_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleBlur_Body blur;
    StyleBrightness_Body brightness;
    StyleContrast_Body contrast;
    StyleGrayscale_Body grayscale;
    StyleHueRotate_Body hue_rotate;
    StyleInvert_Body invert;
    StyleOpacity_Body opacity;
    StyleSaturate_Body saturate;
    StyleSepia_Body sepia;
    StyleDropShadow_Body drop_shadow;
    StyleUrl_Body url;
  };

  static StyleGenericFilter Blur(const StyleNonNegative<Length> &_0) {
    StyleGenericFilter result;
    ::new (&result.blur._0) (StyleNonNegative<Length>)(_0);
    result.tag = Tag::Blur;
    return result;
  }

  bool IsBlur() const {
    return tag == Tag::Blur;
  }

  const StyleNonNegative<Length>& AsBlur() const {
    MOZ_DIAGNOSTIC_ASSERT(IsBlur());
    return blur._0;
  }

  static StyleGenericFilter Brightness(const StyleNonNegative<Factor> &_0) {
    StyleGenericFilter result;
    ::new (&result.brightness._0) (StyleNonNegative<Factor>)(_0);
    result.tag = Tag::Brightness;
    return result;
  }

  bool IsBrightness() const {
    return tag == Tag::Brightness;
  }

  const StyleNonNegative<Factor>& AsBrightness() const {
    MOZ_DIAGNOSTIC_ASSERT(IsBrightness());
    return brightness._0;
  }

  static StyleGenericFilter Contrast(const StyleNonNegative<Factor> &_0) {
    StyleGenericFilter result;
    ::new (&result.contrast._0) (StyleNonNegative<Factor>)(_0);
    result.tag = Tag::Contrast;
    return result;
  }

  bool IsContrast() const {
    return tag == Tag::Contrast;
  }

  const StyleNonNegative<Factor>& AsContrast() const {
    MOZ_DIAGNOSTIC_ASSERT(IsContrast());
    return contrast._0;
  }

  static StyleGenericFilter Grayscale(const StyleZeroToOne<Factor> &_0) {
    StyleGenericFilter result;
    ::new (&result.grayscale._0) (StyleZeroToOne<Factor>)(_0);
    result.tag = Tag::Grayscale;
    return result;
  }

  bool IsGrayscale() const {
    return tag == Tag::Grayscale;
  }

  const StyleZeroToOne<Factor>& AsGrayscale() const {
    MOZ_DIAGNOSTIC_ASSERT(IsGrayscale());
    return grayscale._0;
  }

  static StyleGenericFilter HueRotate(const Angle &_0) {
    StyleGenericFilter result;
    ::new (&result.hue_rotate._0) (Angle)(_0);
    result.tag = Tag::HueRotate;
    return result;
  }

  bool IsHueRotate() const {
    return tag == Tag::HueRotate;
  }

  const Angle& AsHueRotate() const {
    MOZ_DIAGNOSTIC_ASSERT(IsHueRotate());
    return hue_rotate._0;
  }

  static StyleGenericFilter Invert(const StyleZeroToOne<Factor> &_0) {
    StyleGenericFilter result;
    ::new (&result.invert._0) (StyleZeroToOne<Factor>)(_0);
    result.tag = Tag::Invert;
    return result;
  }

  bool IsInvert() const {
    return tag == Tag::Invert;
  }

  const StyleZeroToOne<Factor>& AsInvert() const {
    MOZ_DIAGNOSTIC_ASSERT(IsInvert());
    return invert._0;
  }

  static StyleGenericFilter Opacity(const StyleZeroToOne<Factor> &_0) {
    StyleGenericFilter result;
    ::new (&result.opacity._0) (StyleZeroToOne<Factor>)(_0);
    result.tag = Tag::Opacity;
    return result;
  }

  bool IsOpacity() const {
    return tag == Tag::Opacity;
  }

  const StyleZeroToOne<Factor>& AsOpacity() const {
    MOZ_DIAGNOSTIC_ASSERT(IsOpacity());
    return opacity._0;
  }

  static StyleGenericFilter Saturate(const StyleNonNegative<Factor> &_0) {
    StyleGenericFilter result;
    ::new (&result.saturate._0) (StyleNonNegative<Factor>)(_0);
    result.tag = Tag::Saturate;
    return result;
  }

  bool IsSaturate() const {
    return tag == Tag::Saturate;
  }

  const StyleNonNegative<Factor>& AsSaturate() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSaturate());
    return saturate._0;
  }

  static StyleGenericFilter Sepia(const StyleZeroToOne<Factor> &_0) {
    StyleGenericFilter result;
    ::new (&result.sepia._0) (StyleZeroToOne<Factor>)(_0);
    result.tag = Tag::Sepia;
    return result;
  }

  bool IsSepia() const {
    return tag == Tag::Sepia;
  }

  const StyleZeroToOne<Factor>& AsSepia() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSepia());
    return sepia._0;
  }

  static StyleGenericFilter DropShadow(const Shadow &_0) {
    StyleGenericFilter result;
    ::new (&result.drop_shadow._0) (Shadow)(_0);
    result.tag = Tag::DropShadow;
    return result;
  }

  bool IsDropShadow() const {
    return tag == Tag::DropShadow;
  }

  const Shadow& AsDropShadow() const {
    MOZ_DIAGNOSTIC_ASSERT(IsDropShadow());
    return drop_shadow._0;
  }

  static StyleGenericFilter Url(const U &_0) {
    StyleGenericFilter result;
    ::new (&result.url._0) (U)(_0);
    result.tag = Tag::Url;
    return result;
  }

  bool IsUrl() const {
    return tag == Tag::Url;
  }

  const U& AsUrl() const {
    MOZ_DIAGNOSTIC_ASSERT(IsUrl());
    return url._0;
  }

  bool operator==(const StyleGenericFilter& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Blur: return blur == other.blur;
      case Tag::Brightness: return brightness == other.brightness;
      case Tag::Contrast: return contrast == other.contrast;
      case Tag::Grayscale: return grayscale == other.grayscale;
      case Tag::HueRotate: return hue_rotate == other.hue_rotate;
      case Tag::Invert: return invert == other.invert;
      case Tag::Opacity: return opacity == other.opacity;
      case Tag::Saturate: return saturate == other.saturate;
      case Tag::Sepia: return sepia == other.sepia;
      case Tag::DropShadow: return drop_shadow == other.drop_shadow;
      case Tag::Url: return url == other.url;

    }
    return true;
  }

  private:
  StyleGenericFilter() {

  }
  public:


  ~StyleGenericFilter() {
    switch (tag) {
      case Tag::Blur: blur.~StyleBlur_Body(); break;
      case Tag::Brightness: brightness.~StyleBrightness_Body(); break;
      case Tag::Contrast: contrast.~StyleContrast_Body(); break;
      case Tag::Grayscale: grayscale.~StyleGrayscale_Body(); break;
      case Tag::HueRotate: hue_rotate.~StyleHueRotate_Body(); break;
      case Tag::Invert: invert.~StyleInvert_Body(); break;
      case Tag::Opacity: opacity.~StyleOpacity_Body(); break;
      case Tag::Saturate: saturate.~StyleSaturate_Body(); break;
      case Tag::Sepia: sepia.~StyleSepia_Body(); break;
      case Tag::DropShadow: drop_shadow.~StyleDropShadow_Body(); break;
      case Tag::Url: url.~StyleUrl_Body(); break;

    }
  }

  StyleGenericFilter(const StyleGenericFilter& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Blur: ::new (&blur) (StyleBlur_Body)(other.blur); break;
      case Tag::Brightness: ::new (&brightness) (StyleBrightness_Body)(other.brightness); break;
      case Tag::Contrast: ::new (&contrast) (StyleContrast_Body)(other.contrast); break;
      case Tag::Grayscale: ::new (&grayscale) (StyleGrayscale_Body)(other.grayscale); break;
      case Tag::HueRotate: ::new (&hue_rotate) (StyleHueRotate_Body)(other.hue_rotate); break;
      case Tag::Invert: ::new (&invert) (StyleInvert_Body)(other.invert); break;
      case Tag::Opacity: ::new (&opacity) (StyleOpacity_Body)(other.opacity); break;
      case Tag::Saturate: ::new (&saturate) (StyleSaturate_Body)(other.saturate); break;
      case Tag::Sepia: ::new (&sepia) (StyleSepia_Body)(other.sepia); break;
      case Tag::DropShadow: ::new (&drop_shadow) (StyleDropShadow_Body)(other.drop_shadow); break;
      case Tag::Url: ::new (&url) (StyleUrl_Body)(other.url); break;

    }
  }
  StyleGenericFilter& operator=(const StyleGenericFilter& other) {
    if (this != &other) {
      this->~StyleGenericFilter();
      new (this) StyleGenericFilter(other);
    }
    return *this;
  }
};

#if defined(CBINDGEN_IS_GECKO)
/// A computed value for a single `filter`.
using StyleFilter = StyleGenericFilter<StyleAngle, StyleNumber, StyleLength, StyleSimpleShadow, StyleComputedUrl>;
#endif

#if defined(CBINDGEN_IS_SERVO)
/// A computed value for a single `filter`.
using StyleFilter = StyleGenericFilter<StyleAngle, StyleNumber, StyleLength, StyleSimpleShadow, StyleImpossible>;
#endif

/// Various flags to represent the color-scheme property in an efficient
/// way.
struct StyleColorSchemeFlags {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleColorSchemeFlags operator~() const {
    return StyleColorSchemeFlags { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleColorSchemeFlags operator|(const StyleColorSchemeFlags& other) const {
    return StyleColorSchemeFlags { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleColorSchemeFlags& operator|=(const StyleColorSchemeFlags& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleColorSchemeFlags operator&(const StyleColorSchemeFlags& other) const {
    return StyleColorSchemeFlags { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleColorSchemeFlags& operator&=(const StyleColorSchemeFlags& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleColorSchemeFlags operator^(const StyleColorSchemeFlags& other) const {
    return StyleColorSchemeFlags { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleColorSchemeFlags& operator^=(const StyleColorSchemeFlags& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleColorSchemeFlags& other) const {
    return _0 == other._0;
  }
  static const StyleColorSchemeFlags LIGHT;
  static const StyleColorSchemeFlags DARK;
  static const StyleColorSchemeFlags ONLY;
};
/// Whether the author specified `light`.
constexpr inline const StyleColorSchemeFlags StyleColorSchemeFlags::LIGHT = StyleColorSchemeFlags{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// Whether the author specified `dark`.
constexpr inline const StyleColorSchemeFlags StyleColorSchemeFlags::DARK = StyleColorSchemeFlags{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// Whether the author specified `only`.
constexpr inline const StyleColorSchemeFlags StyleColorSchemeFlags::ONLY = StyleColorSchemeFlags{
  /* ._0 = */ (uint8_t)(1 << 2)
};

/// <https://drafts.csswg.org/css-color-adjust/#color-scheme-prop>
struct StyleColorScheme {
  StyleArcSlice<StyleCustomIdent> idents;
  /// The computed bits for the known color schemes (plus the only keyword).
  StyleColorSchemeFlags bits;

  bool operator==(const StyleColorScheme& other) const {
    return idents == other.idents &&
           bits == other.bits;
  }
};

struct StyleCssSupportsParams {
  StyleOrigin origin;
  StyleCssSupportsUrlContext url_context;
  nsCompatibility quirks;

  bool operator==(const StyleCssSupportsParams& other) const {
    return origin == other.origin &&
           url_context == other.url_context &&
           quirks == other.quirks;
  }
};

/// The kind of restyle we need to do for a given element.
struct StyleRestyleHint {
  uint16_t bits;

  constexpr explicit operator bool() const {
    return !!bits;
  }
  constexpr StyleRestyleHint operator~() const {
    return StyleRestyleHint { static_cast<decltype(bits)>(~bits) };
  }
  constexpr StyleRestyleHint operator|(const StyleRestyleHint& other) const {
    return StyleRestyleHint { static_cast<decltype(bits)>(this->bits | other.bits) };
  }
  StyleRestyleHint& operator|=(const StyleRestyleHint& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleRestyleHint operator&(const StyleRestyleHint& other) const {
    return StyleRestyleHint { static_cast<decltype(bits)>(this->bits & other.bits) };
  }
  StyleRestyleHint& operator&=(const StyleRestyleHint& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleRestyleHint operator^(const StyleRestyleHint& other) const {
    return StyleRestyleHint { static_cast<decltype(bits)>(this->bits ^ other.bits) };
  }
  StyleRestyleHint& operator^=(const StyleRestyleHint& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleRestyleHint& other) const {
    return bits == other.bits;
  }
  static inline StyleRestyleHint RestyleSubtree();
  static inline StyleRestyleHint RecascadeSubtree();
  static inline StyleRestyleHint ForAnimations();
  // Returns true if this change hint is guaranteed to at least recascade all
  // elements in the subtree of the element it is applied to.
  inline bool DefinitelyRecascadesAllSubtree() const;
  static const StyleRestyleHint RESTYLE_SELF;
  static const StyleRestyleHint RESTYLE_PSEUDOS;
  static const StyleRestyleHint RESTYLE_SELF_IF_PSEUDO;
  static const StyleRestyleHint RESTYLE_DESCENDANTS;
  static const StyleRestyleHint RECASCADE_SELF;
  static const StyleRestyleHint RECASCADE_SELF_IF_INHERIT_RESET_STYLE;
  static const StyleRestyleHint RECASCADE_DESCENDANTS;
  static const StyleRestyleHint RESTYLE_CSS_TRANSITIONS;
  static const StyleRestyleHint RESTYLE_CSS_ANIMATIONS;
  static const StyleRestyleHint RESTYLE_STYLE_ATTRIBUTE;
  static const StyleRestyleHint RESTYLE_SMIL;
  static const StyleRestyleHint RESTYLE_IF_AFFECTED_BY_STYLE_QUERIES;
  static const StyleRestyleHint RESTYLE_IF_AFFECTED_BY_NAMED_STYLE_CONTAINER;
  static const StyleRestyleHint RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT;
  static const StyleRestyleHint RESTYLE_CHILD_IF_AFFECTED_BY_STYLE_QUERIES;
};
/// Do a selector match of the element.
constexpr inline const StyleRestyleHint StyleRestyleHint::RESTYLE_SELF = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 0)
};
/// Do a selector match of the element's pseudo-elements. Always to be combined with
/// RESTYLE_SELF.
constexpr inline const StyleRestyleHint StyleRestyleHint::RESTYLE_PSEUDOS = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 1)
};
/// Do a selector match if the element is a pseudo-element.
constexpr inline const StyleRestyleHint StyleRestyleHint::RESTYLE_SELF_IF_PSEUDO = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 2)
};
/// Do a selector match of the element's descendants.
constexpr inline const StyleRestyleHint StyleRestyleHint::RESTYLE_DESCENDANTS = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 3)
};
/// Recascade the current element.
constexpr inline const StyleRestyleHint StyleRestyleHint::RECASCADE_SELF = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 4)
};
/// Recascade the current element if it inherits any reset style.
constexpr inline const StyleRestyleHint StyleRestyleHint::RECASCADE_SELF_IF_INHERIT_RESET_STYLE = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 5)
};
/// Recascade all descendant elements.
constexpr inline const StyleRestyleHint StyleRestyleHint::RECASCADE_DESCENDANTS = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 6)
};
/// Replace the style data coming from CSS transitions without updating
/// any other style data. This hint is only processed in animation-only
/// traversal which is prior to normal traversal.
constexpr inline const StyleRestyleHint StyleRestyleHint::RESTYLE_CSS_TRANSITIONS = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 7)
};
/// Replace the style data coming from CSS animations without updating
/// any other style data. This hint is only processed in animation-only
/// traversal which is prior to normal traversal.
constexpr inline const StyleRestyleHint StyleRestyleHint::RESTYLE_CSS_ANIMATIONS = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 8)
};
/// Don't re-run selector-matching on the element, only the style
/// attribute has changed, and this change didn't have any other
/// dependencies.
constexpr inline const StyleRestyleHint StyleRestyleHint::RESTYLE_STYLE_ATTRIBUTE = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 9)
};
/// Replace the style data coming from SMIL animations without updating
/// any other style data. This hint is only processed in animation-only
/// traversal which is prior to normal traversal.
constexpr inline const StyleRestyleHint StyleRestyleHint::RESTYLE_SMIL = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 10)
};
/// Match self if this element is dependent on a style query.
constexpr inline const StyleRestyleHint StyleRestyleHint::RESTYLE_IF_AFFECTED_BY_STYLE_QUERIES = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 11)
};
/// Match self or descendants if dependent on a named style query.
constexpr inline const StyleRestyleHint StyleRestyleHint::RESTYLE_IF_AFFECTED_BY_NAMED_STYLE_CONTAINER = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 12)
};
/// Do a selector match of the element if it depends on an ancestor's font
/// or this element's writing mode. Used to handle the invalidation cases
/// for style container queries in which relative font metrics change or
/// when a writing-mode-dependant unit needs to be updated for a style
/// container query.
constexpr inline const StyleRestyleHint StyleRestyleHint::RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 13)
};
/// We don't need to match this element but do a selector match of it's
/// children if they are affected by style container queries.
constexpr inline const StyleRestyleHint StyleRestyleHint::RESTYLE_CHILD_IF_AFFECTED_BY_STYLE_QUERIES = StyleRestyleHint{
  /* .bits = */ (uint16_t)(1 << 14)
};

/// A value for animation-range-start or animation-range-end.
///
/// https://drafts.csswg.org/scroll-animations-1/#animation-range-start
/// https://drafts.csswg.org/scroll-animations-1/#animation-range-end
template<typename LengthPercent>
struct StyleGenericAnimationRangeValue {
  /// The specific timeline range. If it is None, the animation range only has length-percentage
  /// component.
  StyleTimelineRangeName name;
  /// Used to measure the specific point from the start of the named timeline.
  LengthPercent lp;

  bool operator==(const StyleGenericAnimationRangeValue& other) const {
    return name == other.name &&
           lp == other.lp;
  }
 public:
  static StyleGenericAnimationRangeValue<LengthPercent> DefaultStart();
  static StyleGenericAnimationRangeValue<LengthPercent> DefaultEnd();
};

/// A value for animation-range-start.
///
/// https://drafts.csswg.org/scroll-animations-1/#animation-range-start
template<typename LengthPercent>
using StyleGenericAnimationRangeStart = StyleGenericAnimationRangeValue<LengthPercent>;

/// A computed value for the `animation-range-start` property.
using StyleAnimationRangeStart = StyleGenericAnimationRangeStart<StyleLengthPercentage>;

/// A value for animation-range-end.
///
/// https://drafts.csswg.org/scroll-animations-1/#animation-range-end
template<typename LengthPercent>
using StyleGenericAnimationRangeEnd = StyleGenericAnimationRangeValue<LengthPercent>;

/// A computed value for the `animation-range-end` property.
using StyleAnimationRangeEnd = StyleGenericAnimationRangeEnd<StyleLengthPercentage>;

/// What anchor positioning functions are allowed to resolve in calc percentage
/// values.
struct StyleAllowAnchorPosResolutionInCalcPercentage {
  enum class Tag {
    /// Both `anchor()` and `anchor-size()` are valid and should be resolved.
    Both,
    /// Only `anchor-size()` is valid and should be resolved.
    AnchorSizeOnly,
  };

  struct StyleBoth_Body {
    StylePhysicalSide _0;

    bool operator==(const StyleBoth_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAnchorSizeOnly_Body {
    StylePhysicalAxis _0;

    bool operator==(const StyleAnchorSizeOnly_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleBoth_Body both;
    StyleAnchorSizeOnly_Body anchor_size_only;
  };

  static StyleAllowAnchorPosResolutionInCalcPercentage Both(const StylePhysicalSide &_0) {
    StyleAllowAnchorPosResolutionInCalcPercentage result;
    ::new (&result.both._0) (StylePhysicalSide)(_0);
    result.tag = Tag::Both;
    return result;
  }

  bool IsBoth() const {
    return tag == Tag::Both;
  }

  const StylePhysicalSide& AsBoth() const {
    MOZ_DIAGNOSTIC_ASSERT(IsBoth());
    return both._0;
  }

  static StyleAllowAnchorPosResolutionInCalcPercentage AnchorSizeOnly(const StylePhysicalAxis &_0) {
    StyleAllowAnchorPosResolutionInCalcPercentage result;
    ::new (&result.anchor_size_only._0) (StylePhysicalAxis)(_0);
    result.tag = Tag::AnchorSizeOnly;
    return result;
  }

  bool IsAnchorSizeOnly() const {
    return tag == Tag::AnchorSizeOnly;
  }

  const StylePhysicalAxis& AsAnchorSizeOnly() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAnchorSizeOnly());
    return anchor_size_only._0;
  }

  bool operator==(const StyleAllowAnchorPosResolutionInCalcPercentage& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Both: return both == other.both;
      case Tag::AnchorSizeOnly: return anchor_size_only == other.anchor_size_only;

    }
    return true;
  }

  private:
  StyleAllowAnchorPosResolutionInCalcPercentage() {

  }
  public:


  ~StyleAllowAnchorPosResolutionInCalcPercentage() {
    switch (tag) {
      case Tag::Both: both.~StyleBoth_Body(); break;
      case Tag::AnchorSizeOnly: anchor_size_only.~StyleAnchorSizeOnly_Body(); break;

    }
  }

  StyleAllowAnchorPosResolutionInCalcPercentage(const StyleAllowAnchorPosResolutionInCalcPercentage& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Both: ::new (&both) (StyleBoth_Body)(other.both); break;
      case Tag::AnchorSizeOnly: ::new (&anchor_size_only) (StyleAnchorSizeOnly_Body)(other.anchor_size_only); break;

    }
  }
  StyleAllowAnchorPosResolutionInCalcPercentage& operator=(const StyleAllowAnchorPosResolutionInCalcPercentage& other) {
    if (this != &other) {
      this->~StyleAllowAnchorPosResolutionInCalcPercentage();
      new (this) StyleAllowAnchorPosResolutionInCalcPercentage(other);
    }
    return *this;
  }
};

/// Result of resolving a math function node potentially containing
/// anchor positioning function.
union StyleCalcAnchorPositioningFunctionResolution {
  enum class Tag : uint8_t {
    /// Anchor positioning function is used, but at least one of them
    /// did not resolve to a valid reference - Property using this
    /// expression is now invalid at computed time.
    Invalid,
    /// Anchor positioning function is used, and all of them resolved
    /// to valid references, or specified a fallback.
    Valid,
  };

  struct Valid_Body {
    Tag tag;
    StyleLengthPercentage _0;

    bool operator==(const Valid_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Valid_Body valid;

  static StyleCalcAnchorPositioningFunctionResolution Invalid() {
    StyleCalcAnchorPositioningFunctionResolution result;
    result.tag = Tag::Invalid;
    return result;
  }

  bool IsInvalid() const {
    return tag == Tag::Invalid;
  }

  static StyleCalcAnchorPositioningFunctionResolution Valid(const StyleLengthPercentage &_0) {
    StyleCalcAnchorPositioningFunctionResolution result;
    ::new (&result.valid._0) (StyleLengthPercentage)(_0);
    result.tag = Tag::Valid;
    return result;
  }

  bool IsValid() const {
    return tag == Tag::Valid;
  }

  const StyleLengthPercentage& AsValid() const {
    MOZ_DIAGNOSTIC_ASSERT(IsValid());
    return valid._0;
  }

  bool operator==(const StyleCalcAnchorPositioningFunctionResolution& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Valid: return valid == other.valid;
      default: break;
    }
    return true;
  }

  private:
  StyleCalcAnchorPositioningFunctionResolution() {

  }
  public:


  ~StyleCalcAnchorPositioningFunctionResolution() {
    switch (tag) {
      case Tag::Valid: valid.~Valid_Body(); break;
      default: break;
    }
  }

  StyleCalcAnchorPositioningFunctionResolution(const StyleCalcAnchorPositioningFunctionResolution& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Valid: ::new (&valid) (Valid_Body)(other.valid); break;
      default: break;
    }
  }
  StyleCalcAnchorPositioningFunctionResolution& operator=(const StyleCalcAnchorPositioningFunctionResolution& other) {
    if (this != &other) {
      this->~StyleCalcAnchorPositioningFunctionResolution();
      new (this) StyleCalcAnchorPositioningFunctionResolution(other);
    }
    return *this;
  }
};

/// The value of an IntersectionObserver's (root or scroll) margin property.
///
/// Only bare px or percentage values are allowed. Other length units and
/// calc() values are not allowed.
///
/// <https://w3c.github.io/IntersectionObserver/#parse-a-margin>
using StyleIntersectionObserverMargin = StyleRect<StyleLengthPercentage>;

/// The name of a font family of choice.
struct StyleFamilyName {
  /// Name of the font family.
  StyleAtom name;
  /// Syntax of the font family.
  StyleFontFamilyNameSyntax syntax;

  bool operator==(const StyleFamilyName& other) const {
    return name == other.name &&
           syntax == other.syntax;
  }
};

/// A set of faces that vary in weight, width or slope.
union StyleSingleFontFamily {
  enum class Tag : uint8_t {
    /// The name of a font family of choice.
    FamilyName,
    /// Generic family name.
    Generic,
  };

  struct FamilyName_Body {
    Tag tag;
    StyleFamilyName _0;

    bool operator==(const FamilyName_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Generic_Body {
    Tag tag;
    StyleGenericFontFamily _0;

    bool operator==(const Generic_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  FamilyName_Body family_name;
  Generic_Body generic;

  static StyleSingleFontFamily FamilyName(const StyleFamilyName &_0) {
    StyleSingleFontFamily result;
    ::new (&result.family_name._0) (StyleFamilyName)(_0);
    result.tag = Tag::FamilyName;
    return result;
  }

  bool IsFamilyName() const {
    return tag == Tag::FamilyName;
  }

  const StyleFamilyName& AsFamilyName() const {
    MOZ_DIAGNOSTIC_ASSERT(IsFamilyName());
    return family_name._0;
  }

  StyleFamilyName& AsFamilyName() {
    MOZ_DIAGNOSTIC_ASSERT(IsFamilyName());
    return family_name._0;
  }

  static StyleSingleFontFamily Generic(const StyleGenericFontFamily &_0) {
    StyleSingleFontFamily result;
    ::new (&result.generic._0) (StyleGenericFontFamily)(_0);
    result.tag = Tag::Generic;
    return result;
  }

  bool IsGeneric() const {
    return tag == Tag::Generic;
  }

  const StyleGenericFontFamily& AsGeneric() const {
    MOZ_DIAGNOSTIC_ASSERT(IsGeneric());
    return generic._0;
  }

  StyleGenericFontFamily& AsGeneric() {
    MOZ_DIAGNOSTIC_ASSERT(IsGeneric());
    return generic._0;
  }

  bool operator==(const StyleSingleFontFamily& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::FamilyName: return family_name == other.family_name;
      case Tag::Generic: return generic == other.generic;

    }
    return true;
  }

  private:
  StyleSingleFontFamily() {

  }
  public:


  ~StyleSingleFontFamily() {
    switch (tag) {
      case Tag::FamilyName: family_name.~FamilyName_Body(); break;
      case Tag::Generic: generic.~Generic_Body(); break;

    }
  }

  StyleSingleFontFamily(const StyleSingleFontFamily& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::FamilyName: ::new (&family_name) (FamilyName_Body)(other.family_name); break;
      case Tag::Generic: ::new (&generic) (Generic_Body)(other.generic); break;

    }
  }
  StyleSingleFontFamily& operator=(const StyleSingleFontFamily& other) {
    if (this != &other) {
      this->~StyleSingleFontFamily();
      new (this) StyleSingleFontFamily(other);
    }
    return *this;
  }
  static StyleSingleFontFamily Parse(const nsACString& aName);
  void AppendToString(nsACString& aFamily, bool aIncludeQuotes = true) const;
  bool IsNamedFamily(const nsAString&) const;
};

/// A list of font families.
struct StyleFontFamilyList {
  /// The actual list of font families specified.
  StyleArcSlice<StyleSingleFontFamily> list;

  bool operator==(const StyleFontFamilyList& other) const {
    return list == other.list;
  }
  static StyleFontFamilyList WithOneUnquotedFamily(const nsACString&);
  // Constructs a font family list with a list of names.
  static StyleFontFamilyList WithNames(nsTArray<StyleSingleFontFamily>&&);
};

/// Specifies a prioritized list of font family names or generic family names.
struct StyleFontFamily {
  /// The actual list of family names.
  StyleFontFamilyList families;
  /// Whether this font-family came from a specified system-font.
  bool is_system_font;
  /// Whether this is the initial font-family that might react to language
  /// changes.
  bool is_initial;

  bool operator==(const StyleFontFamily& other) const {
    return families == other.families &&
           is_system_font == other.is_system_font &&
           is_initial == other.is_initial;
  }
};

struct StylePropDef {
  StyleAtom name;
  nsCString syntax;
  bool inherits;
  bool has_initial_value;
  nsCString initial_value;
  bool from_js;

  bool operator==(const StylePropDef& other) const {
    return name == other.name &&
           syntax == other.syntax &&
           inherits == other.inherits &&
           has_initial_value == other.has_initial_value &&
           initial_value == other.initial_value &&
           from_js == other.from_js;
  }
};

struct StyleSelectorWarningData {
  /// Index to the selector generating the warning.
  size_t index;
  /// Kind of the warning.
  StyleSelectorWarningKind kind;

  bool operator==(const StyleSelectorWarningData& other) const {
    return index == other.index &&
           kind == other.kind;
  }
};

struct StyleCSSToken {
  nsCString text;
  nsCString token_type;
  bool has_unit;
  nsCString unit;
  bool has_number;
  float number;
  bool has_value;
  nsCString value;
  uint32_t line;
  uint32_t column;

  bool operator==(const StyleCSSToken& other) const {
    return text == other.text &&
           token_type == other.token_type &&
           has_unit == other.has_unit &&
           unit == other.unit &&
           has_number == other.has_number &&
           number == other.number &&
           has_value == other.has_value &&
           value == other.value &&
           line == other.line &&
           column == other.column;
  }
};

/// Specified type for `inset` properties, which allows
/// the use of the `anchor()` function.
/// Note(dshin): `LengthPercentageOrAuto` is not used here because
/// having `LengthPercentageOrAuto` and `AnchorFunction` in the enum
/// pays the price of the discriminator for `LengthPercentage | Auto`
/// as well as `LengthPercentageOrAuto | AnchorFunction`. This increases
/// the size of the style struct, which would not be great.
/// On the other hand, we trade for code duplication, so... :(
template<typename P, typename LP>
struct StyleGenericInset {
  enum class Tag {
    /// A `<length-percentage>` value.
    LengthPercentage,
    /// An `auto` value.
    Auto,
    /// Inset defined by the anchor element.
    ///
    /// <https://drafts.csswg.org/css-anchor-position-1/#anchor-pos>
    AnchorFunction,
    /// Inset defined by the size of the anchor element.
    ///
    /// <https://drafts.csswg.org/css-anchor-position-1/#anchor-pos>
    AnchorSizeFunction,
    /// A `<length-percentage>` value, guaranteed to contain `calc()`,
    /// which then is guaranteed to contain `anchor()` or `anchor-size()`.
    AnchorContainingCalcFunction,
  };

  struct StyleLengthPercentage_Body {
    LP _0;

    bool operator==(const StyleLengthPercentage_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAnchorFunction_Body {
    StyleBox<StyleGenericAnchorFunction<P, StyleGenericInset>> _0;

    bool operator==(const StyleAnchorFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAnchorSizeFunction_Body {
    StyleBox<StyleGenericAnchorSizeFunction<StyleGenericInset>> _0;

    bool operator==(const StyleAnchorSizeFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAnchorContainingCalcFunction_Body {
    LP _0;

    bool operator==(const StyleAnchorContainingCalcFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleLengthPercentage_Body length_percentage;
    StyleAnchorFunction_Body anchor_function;
    StyleAnchorSizeFunction_Body anchor_size_function;
    StyleAnchorContainingCalcFunction_Body anchor_containing_calc_function;
  };

  static StyleGenericInset LengthPercentage(const LP &_0) {
    StyleGenericInset result;
    ::new (&result.length_percentage._0) (LP)(_0);
    result.tag = Tag::LengthPercentage;
    return result;
  }

  bool IsLengthPercentage() const {
    return tag == Tag::LengthPercentage;
  }

  const LP& AsLengthPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLengthPercentage());
    return length_percentage._0;
  }

  static StyleGenericInset Auto() {
    StyleGenericInset result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleGenericInset AnchorFunction(const StyleBox<StyleGenericAnchorFunction<P, StyleGenericInset>> &_0) {
    StyleGenericInset result;
    ::new (&result.anchor_function._0) (StyleBox<StyleGenericAnchorFunction<P, StyleGenericInset>>)(_0);
    result.tag = Tag::AnchorFunction;
    return result;
  }

  bool IsAnchorFunction() const {
    return tag == Tag::AnchorFunction;
  }

  const StyleBox<StyleGenericAnchorFunction<P, StyleGenericInset>>& AsAnchorFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAnchorFunction());
    return anchor_function._0;
  }

  static StyleGenericInset AnchorSizeFunction(const StyleBox<StyleGenericAnchorSizeFunction<StyleGenericInset>> &_0) {
    StyleGenericInset result;
    ::new (&result.anchor_size_function._0) (StyleBox<StyleGenericAnchorSizeFunction<StyleGenericInset>>)(_0);
    result.tag = Tag::AnchorSizeFunction;
    return result;
  }

  bool IsAnchorSizeFunction() const {
    return tag == Tag::AnchorSizeFunction;
  }

  const StyleBox<StyleGenericAnchorSizeFunction<StyleGenericInset>>& AsAnchorSizeFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAnchorSizeFunction());
    return anchor_size_function._0;
  }

  static StyleGenericInset AnchorContainingCalcFunction(const LP &_0) {
    StyleGenericInset result;
    ::new (&result.anchor_containing_calc_function._0) (LP)(_0);
    result.tag = Tag::AnchorContainingCalcFunction;
    return result;
  }

  bool IsAnchorContainingCalcFunction() const {
    return tag == Tag::AnchorContainingCalcFunction;
  }

  const LP& AsAnchorContainingCalcFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAnchorContainingCalcFunction());
    return anchor_containing_calc_function._0;
  }

  bool operator==(const StyleGenericInset& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::LengthPercentage: return length_percentage == other.length_percentage;
      case Tag::AnchorFunction: return anchor_function == other.anchor_function;
      case Tag::AnchorSizeFunction: return anchor_size_function == other.anchor_size_function;
      case Tag::AnchorContainingCalcFunction: return anchor_containing_calc_function == other.anchor_containing_calc_function;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericInset() {

  }
  public:


  ~StyleGenericInset() {
    switch (tag) {
      case Tag::LengthPercentage: length_percentage.~StyleLengthPercentage_Body(); break;
      case Tag::AnchorFunction: anchor_function.~StyleAnchorFunction_Body(); break;
      case Tag::AnchorSizeFunction: anchor_size_function.~StyleAnchorSizeFunction_Body(); break;
      case Tag::AnchorContainingCalcFunction: anchor_containing_calc_function.~StyleAnchorContainingCalcFunction_Body(); break;
      default: break;
    }
  }

  StyleGenericInset(const StyleGenericInset& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::LengthPercentage: ::new (&length_percentage) (StyleLengthPercentage_Body)(other.length_percentage); break;
      case Tag::AnchorFunction: ::new (&anchor_function) (StyleAnchorFunction_Body)(other.anchor_function); break;
      case Tag::AnchorSizeFunction: ::new (&anchor_size_function) (StyleAnchorSizeFunction_Body)(other.anchor_size_function); break;
      case Tag::AnchorContainingCalcFunction: ::new (&anchor_containing_calc_function) (StyleAnchorContainingCalcFunction_Body)(other.anchor_containing_calc_function); break;
      default: break;
    }
  }
  StyleGenericInset& operator=(const StyleGenericInset& other) {
    if (this != &other) {
      this->~StyleGenericInset();
      new (this) StyleGenericInset(other);
    }
    return *this;
  }
  inline bool HasPercent() const;
  inline bool ConvertsToLength() const;
  inline bool HasLengthAndPercentage() const;
  inline bool HasAnchorPositioningFunction() const;
  inline nscoord ToLength() const;
  inline bool ConvertsToPercentage() const;
  inline float ToPercentage() const;
  inline explicit StyleGenericInset(const LP &);
};

/// A computed type for `inset` properties.
using StyleInset = StyleGenericInset<StylePercentage, StyleLengthPercentage>;

/// The computed value of an `anchor()` function.
using StyleAnchorFunction = StyleGenericAnchorFunction<StylePercentage, StyleInset>;

/// Result of resolving an anchor positioning function.
union StyleAnchorPositioningFunctionResolution {
  enum class Tag : uint8_t {
    /// Anchor function invalid.
    Invalid,
    /// Anchor function resolved to a reference to fallback.
    ResolvedReference,
    /// Anchor function resolved to a value.
    Resolved,
  };

  struct ResolvedReference_Body {
    Tag tag;
    const StyleLengthPercentage *_0;

    bool operator==(const ResolvedReference_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Resolved_Body {
    Tag tag;
    StyleLengthPercentage _0;

    bool operator==(const Resolved_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  ResolvedReference_Body resolved_reference;
  Resolved_Body resolved;

  static StyleAnchorPositioningFunctionResolution Invalid() {
    StyleAnchorPositioningFunctionResolution result;
    result.tag = Tag::Invalid;
    return result;
  }

  bool IsInvalid() const {
    return tag == Tag::Invalid;
  }

  static StyleAnchorPositioningFunctionResolution ResolvedReference(const StyleLengthPercentage *const &_0) {
    StyleAnchorPositioningFunctionResolution result;
    ::new (&result.resolved_reference._0) (const StyleLengthPercentage*)(_0);
    result.tag = Tag::ResolvedReference;
    return result;
  }

  bool IsResolvedReference() const {
    return tag == Tag::ResolvedReference;
  }

  const StyleLengthPercentage*const & AsResolvedReference() const {
    MOZ_DIAGNOSTIC_ASSERT(IsResolvedReference());
    return resolved_reference._0;
  }

  static StyleAnchorPositioningFunctionResolution Resolved(const StyleLengthPercentage &_0) {
    StyleAnchorPositioningFunctionResolution result;
    ::new (&result.resolved._0) (StyleLengthPercentage)(_0);
    result.tag = Tag::Resolved;
    return result;
  }

  bool IsResolved() const {
    return tag == Tag::Resolved;
  }

  const StyleLengthPercentage& AsResolved() const {
    MOZ_DIAGNOSTIC_ASSERT(IsResolved());
    return resolved._0;
  }

  bool operator==(const StyleAnchorPositioningFunctionResolution& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::ResolvedReference: return resolved_reference == other.resolved_reference;
      case Tag::Resolved: return resolved == other.resolved;
      default: break;
    }
    return true;
  }

  private:
  StyleAnchorPositioningFunctionResolution() {

  }
  public:


  ~StyleAnchorPositioningFunctionResolution() {
    switch (tag) {
      case Tag::ResolvedReference: resolved_reference.~ResolvedReference_Body(); break;
      case Tag::Resolved: resolved.~Resolved_Body(); break;
      default: break;
    }
  }

  StyleAnchorPositioningFunctionResolution(const StyleAnchorPositioningFunctionResolution& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::ResolvedReference: ::new (&resolved_reference) (ResolvedReference_Body)(other.resolved_reference); break;
      case Tag::Resolved: ::new (&resolved) (Resolved_Body)(other.resolved); break;
      default: break;
    }
  }
  StyleAnchorPositioningFunctionResolution& operator=(const StyleAnchorPositioningFunctionResolution& other) {
    if (this != &other) {
      this->~StyleAnchorPositioningFunctionResolution();
      new (this) StyleAnchorPositioningFunctionResolution(other);
    }
    return *this;
  }
};

/// Specified type for `margin` properties, which allows
/// the use of the `anchor-size()` function.
template<typename LP>
struct StyleGenericMargin {
  enum class Tag {
    /// A `<length-percentage>` value.
    LengthPercentage,
    /// An `auto` value.
    Auto,
    /// Margin size defined by the anchor element.
    ///
    /// https://drafts.csswg.org/css-anchor-position-1/#funcdef-anchor-size
    AnchorSizeFunction,
    /// A `<length-percentage>` value, guaranteed to contain `calc()`,
    /// which then is guaranteed to contain `anchor()` or `anchor-size()`.
    AnchorContainingCalcFunction,
  };

  struct StyleLengthPercentage_Body {
    LP _0;

    bool operator==(const StyleLengthPercentage_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAnchorSizeFunction_Body {
    StyleBox<StyleGenericAnchorSizeFunction<StyleGenericMargin>> _0;

    bool operator==(const StyleAnchorSizeFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAnchorContainingCalcFunction_Body {
    LP _0;

    bool operator==(const StyleAnchorContainingCalcFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleLengthPercentage_Body length_percentage;
    StyleAnchorSizeFunction_Body anchor_size_function;
    StyleAnchorContainingCalcFunction_Body anchor_containing_calc_function;
  };

  static StyleGenericMargin LengthPercentage(const LP &_0) {
    StyleGenericMargin result;
    ::new (&result.length_percentage._0) (LP)(_0);
    result.tag = Tag::LengthPercentage;
    return result;
  }

  bool IsLengthPercentage() const {
    return tag == Tag::LengthPercentage;
  }

  const LP& AsLengthPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLengthPercentage());
    return length_percentage._0;
  }

  static StyleGenericMargin Auto() {
    StyleGenericMargin result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleGenericMargin AnchorSizeFunction(const StyleBox<StyleGenericAnchorSizeFunction<StyleGenericMargin>> &_0) {
    StyleGenericMargin result;
    ::new (&result.anchor_size_function._0) (StyleBox<StyleGenericAnchorSizeFunction<StyleGenericMargin>>)(_0);
    result.tag = Tag::AnchorSizeFunction;
    return result;
  }

  bool IsAnchorSizeFunction() const {
    return tag == Tag::AnchorSizeFunction;
  }

  const StyleBox<StyleGenericAnchorSizeFunction<StyleGenericMargin>>& AsAnchorSizeFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAnchorSizeFunction());
    return anchor_size_function._0;
  }

  static StyleGenericMargin AnchorContainingCalcFunction(const LP &_0) {
    StyleGenericMargin result;
    ::new (&result.anchor_containing_calc_function._0) (LP)(_0);
    result.tag = Tag::AnchorContainingCalcFunction;
    return result;
  }

  bool IsAnchorContainingCalcFunction() const {
    return tag == Tag::AnchorContainingCalcFunction;
  }

  const LP& AsAnchorContainingCalcFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAnchorContainingCalcFunction());
    return anchor_containing_calc_function._0;
  }

  bool operator==(const StyleGenericMargin& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::LengthPercentage: return length_percentage == other.length_percentage;
      case Tag::AnchorSizeFunction: return anchor_size_function == other.anchor_size_function;
      case Tag::AnchorContainingCalcFunction: return anchor_containing_calc_function == other.anchor_containing_calc_function;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericMargin() {

  }
  public:


  ~StyleGenericMargin() {
    switch (tag) {
      case Tag::LengthPercentage: length_percentage.~StyleLengthPercentage_Body(); break;
      case Tag::AnchorSizeFunction: anchor_size_function.~StyleAnchorSizeFunction_Body(); break;
      case Tag::AnchorContainingCalcFunction: anchor_containing_calc_function.~StyleAnchorContainingCalcFunction_Body(); break;
      default: break;
    }
  }

  StyleGenericMargin(const StyleGenericMargin& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::LengthPercentage: ::new (&length_percentage) (StyleLengthPercentage_Body)(other.length_percentage); break;
      case Tag::AnchorSizeFunction: ::new (&anchor_size_function) (StyleAnchorSizeFunction_Body)(other.anchor_size_function); break;
      case Tag::AnchorContainingCalcFunction: ::new (&anchor_containing_calc_function) (StyleAnchorContainingCalcFunction_Body)(other.anchor_containing_calc_function); break;
      default: break;
    }
  }
  StyleGenericMargin& operator=(const StyleGenericMargin& other) {
    if (this != &other) {
      this->~StyleGenericMargin();
      new (this) StyleGenericMargin(other);
    }
    return *this;
  }
  inline bool HasPercent() const;
  inline bool ConvertsToLength() const;
  inline bool HasLengthAndPercentage() const;
  inline nscoord ToLength() const;
  inline bool ConvertsToPercentage() const;
  inline float ToPercentage() const;
  inline bool HasAnchorPositioningFunction() const;
  inline explicit StyleGenericMargin(const LP &);
};

/// A computed type for `margin` properties.
using StyleMargin = StyleGenericMargin<StyleLengthPercentage>;

/// A wrapper of LengthPercentage, whose value must be >= 0.
using StyleNonNegativeLengthPercentage = StyleNonNegative<StyleLengthPercentage>;

/// A generic value for the `width`, `height`, `min-width`, or `min-height` property.
///
/// Unlike `max-width` or `max-height` properties, a Size can be `auto`,
/// and cannot be `none`.
///
/// Note that it only accepts non-negative values.
template<typename LengthPercent>
struct StyleGenericSize {
  enum class Tag : uint8_t {
    LengthPercentage,
    Auto,
    MaxContent,
    MinContent,
    FitContent,
#if defined(CBINDGEN_IS_GECKO)
    MozAvailable,
#endif
    WebkitFillAvailable,
    Stretch,
    FitContentFunction,
    AnchorSizeFunction,
    AnchorContainingCalcFunction,
  };

  struct StyleLengthPercentage_Body {
    LengthPercent _0;

    bool operator==(const StyleLengthPercentage_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleFitContentFunction_Body {
    LengthPercent _0;

    bool operator==(const StyleFitContentFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAnchorSizeFunction_Body {
    StyleBox<StyleGenericAnchorSizeFunction<StyleGenericSize>> _0;

    bool operator==(const StyleAnchorSizeFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAnchorContainingCalcFunction_Body {
    LengthPercent _0;

    bool operator==(const StyleAnchorContainingCalcFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleLengthPercentage_Body length_percentage;
    StyleFitContentFunction_Body fit_content_function;
    StyleAnchorSizeFunction_Body anchor_size_function;
    StyleAnchorContainingCalcFunction_Body anchor_containing_calc_function;
  };

  static StyleGenericSize LengthPercentage(const LengthPercent &_0) {
    StyleGenericSize result;
    ::new (&result.length_percentage._0) (LengthPercent)(_0);
    result.tag = Tag::LengthPercentage;
    return result;
  }

  bool IsLengthPercentage() const {
    return tag == Tag::LengthPercentage;
  }

  const LengthPercent& AsLengthPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLengthPercentage());
    return length_percentage._0;
  }

  static StyleGenericSize Auto() {
    StyleGenericSize result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleGenericSize MaxContent() {
    StyleGenericSize result;
    result.tag = Tag::MaxContent;
    return result;
  }

  bool IsMaxContent() const {
    return tag == Tag::MaxContent;
  }

  static StyleGenericSize MinContent() {
    StyleGenericSize result;
    result.tag = Tag::MinContent;
    return result;
  }

  bool IsMinContent() const {
    return tag == Tag::MinContent;
  }

  static StyleGenericSize FitContent() {
    StyleGenericSize result;
    result.tag = Tag::FitContent;
    return result;
  }

  bool IsFitContent() const {
    return tag == Tag::FitContent;
  }

#if defined(CBINDGEN_IS_GECKO)
  static StyleGenericSize MozAvailable() {
    StyleGenericSize result;
    result.tag = Tag::MozAvailable;
    return result;
  }

  bool IsMozAvailable() const {
    return tag == Tag::MozAvailable;
  }
#endif

  static StyleGenericSize WebkitFillAvailable() {
    StyleGenericSize result;
    result.tag = Tag::WebkitFillAvailable;
    return result;
  }

  bool IsWebkitFillAvailable() const {
    return tag == Tag::WebkitFillAvailable;
  }

  static StyleGenericSize Stretch() {
    StyleGenericSize result;
    result.tag = Tag::Stretch;
    return result;
  }

  bool IsStretch() const {
    return tag == Tag::Stretch;
  }

  static StyleGenericSize FitContentFunction(const LengthPercent &_0) {
    StyleGenericSize result;
    ::new (&result.fit_content_function._0) (LengthPercent)(_0);
    result.tag = Tag::FitContentFunction;
    return result;
  }

  bool IsFitContentFunction() const {
    return tag == Tag::FitContentFunction;
  }

  const LengthPercent& AsFitContentFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsFitContentFunction());
    return fit_content_function._0;
  }

  static StyleGenericSize AnchorSizeFunction(const StyleBox<StyleGenericAnchorSizeFunction<StyleGenericSize>> &_0) {
    StyleGenericSize result;
    ::new (&result.anchor_size_function._0) (StyleBox<StyleGenericAnchorSizeFunction<StyleGenericSize>>)(_0);
    result.tag = Tag::AnchorSizeFunction;
    return result;
  }

  bool IsAnchorSizeFunction() const {
    return tag == Tag::AnchorSizeFunction;
  }

  const StyleBox<StyleGenericAnchorSizeFunction<StyleGenericSize>>& AsAnchorSizeFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAnchorSizeFunction());
    return anchor_size_function._0;
  }

  static StyleGenericSize AnchorContainingCalcFunction(const LengthPercent &_0) {
    StyleGenericSize result;
    ::new (&result.anchor_containing_calc_function._0) (LengthPercent)(_0);
    result.tag = Tag::AnchorContainingCalcFunction;
    return result;
  }

  bool IsAnchorContainingCalcFunction() const {
    return tag == Tag::AnchorContainingCalcFunction;
  }

  const LengthPercent& AsAnchorContainingCalcFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAnchorContainingCalcFunction());
    return anchor_containing_calc_function._0;
  }

  bool operator==(const StyleGenericSize& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::LengthPercentage: return length_percentage == other.length_percentage;
      case Tag::FitContentFunction: return fit_content_function == other.fit_content_function;
      case Tag::AnchorSizeFunction: return anchor_size_function == other.anchor_size_function;
      case Tag::AnchorContainingCalcFunction: return anchor_containing_calc_function == other.anchor_containing_calc_function;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericSize() {

  }
  public:


  ~StyleGenericSize() {
    switch (tag) {
      case Tag::LengthPercentage: length_percentage.~StyleLengthPercentage_Body(); break;
      case Tag::FitContentFunction: fit_content_function.~StyleFitContentFunction_Body(); break;
      case Tag::AnchorSizeFunction: anchor_size_function.~StyleAnchorSizeFunction_Body(); break;
      case Tag::AnchorContainingCalcFunction: anchor_containing_calc_function.~StyleAnchorContainingCalcFunction_Body(); break;
      default: break;
    }
  }

  StyleGenericSize(const StyleGenericSize& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::LengthPercentage: ::new (&length_percentage) (StyleLengthPercentage_Body)(other.length_percentage); break;
      case Tag::FitContentFunction: ::new (&fit_content_function) (StyleFitContentFunction_Body)(other.fit_content_function); break;
      case Tag::AnchorSizeFunction: ::new (&anchor_size_function) (StyleAnchorSizeFunction_Body)(other.anchor_size_function); break;
      case Tag::AnchorContainingCalcFunction: ::new (&anchor_containing_calc_function) (StyleAnchorContainingCalcFunction_Body)(other.anchor_containing_calc_function); break;
      default: break;
    }
  }
  StyleGenericSize& operator=(const StyleGenericSize& other) {
    if (this != &other) {
      this->~StyleGenericSize();
      new (this) StyleGenericSize(other);
    }
    return *this;
  }
  inline bool ConvertsToLength() const;
  inline nscoord ToLength() const;
  inline bool ConvertsToPercentage() const;
  inline float ToPercentage() const;
  inline bool HasPercent() const;
  inline bool HasLengthAndPercentage() const;
  inline bool BehavesLikeStretchOnInlineAxis() const;
  inline bool BehavesLikeStretchOnBlockAxis() const;
  inline bool BehavesLikeStretch(LogicalAxis) const;
  inline bool BehavesLikeInitialValueOnBlockAxis() const;
  inline bool BehavesLikeInitialValue(LogicalAxis) const;
  inline bool HasAnchorPositioningFunction() const;
  inline explicit StyleGenericSize(const LengthPercent &);
  static inline StyleGenericSize FromAppUnits(nscoord);
};

/// A computed value for `min-width`, `min-height`, `width` or `height` property.
using StyleSize = StyleGenericSize<StyleNonNegativeLengthPercentage>;

/// A generic value for the `max-width` or `max-height` property.
template<typename LengthPercent>
struct StyleGenericMaxSize {
  enum class Tag : uint8_t {
    LengthPercentage,
    None,
    MaxContent,
    MinContent,
    FitContent,
#if defined(CBINDGEN_IS_GECKO)
    MozAvailable,
#endif
    WebkitFillAvailable,
    Stretch,
    FitContentFunction,
    AnchorSizeFunction,
    AnchorContainingCalcFunction,
  };

  struct StyleLengthPercentage_Body {
    LengthPercent _0;

    bool operator==(const StyleLengthPercentage_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleFitContentFunction_Body {
    LengthPercent _0;

    bool operator==(const StyleFitContentFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAnchorSizeFunction_Body {
    StyleBox<StyleGenericAnchorSizeFunction<StyleGenericMaxSize>> _0;

    bool operator==(const StyleAnchorSizeFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAnchorContainingCalcFunction_Body {
    LengthPercent _0;

    bool operator==(const StyleAnchorContainingCalcFunction_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleLengthPercentage_Body length_percentage;
    StyleFitContentFunction_Body fit_content_function;
    StyleAnchorSizeFunction_Body anchor_size_function;
    StyleAnchorContainingCalcFunction_Body anchor_containing_calc_function;
  };

  static StyleGenericMaxSize LengthPercentage(const LengthPercent &_0) {
    StyleGenericMaxSize result;
    ::new (&result.length_percentage._0) (LengthPercent)(_0);
    result.tag = Tag::LengthPercentage;
    return result;
  }

  bool IsLengthPercentage() const {
    return tag == Tag::LengthPercentage;
  }

  const LengthPercent& AsLengthPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLengthPercentage());
    return length_percentage._0;
  }

  static StyleGenericMaxSize None() {
    StyleGenericMaxSize result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericMaxSize MaxContent() {
    StyleGenericMaxSize result;
    result.tag = Tag::MaxContent;
    return result;
  }

  bool IsMaxContent() const {
    return tag == Tag::MaxContent;
  }

  static StyleGenericMaxSize MinContent() {
    StyleGenericMaxSize result;
    result.tag = Tag::MinContent;
    return result;
  }

  bool IsMinContent() const {
    return tag == Tag::MinContent;
  }

  static StyleGenericMaxSize FitContent() {
    StyleGenericMaxSize result;
    result.tag = Tag::FitContent;
    return result;
  }

  bool IsFitContent() const {
    return tag == Tag::FitContent;
  }

#if defined(CBINDGEN_IS_GECKO)
  static StyleGenericMaxSize MozAvailable() {
    StyleGenericMaxSize result;
    result.tag = Tag::MozAvailable;
    return result;
  }

  bool IsMozAvailable() const {
    return tag == Tag::MozAvailable;
  }
#endif

  static StyleGenericMaxSize WebkitFillAvailable() {
    StyleGenericMaxSize result;
    result.tag = Tag::WebkitFillAvailable;
    return result;
  }

  bool IsWebkitFillAvailable() const {
    return tag == Tag::WebkitFillAvailable;
  }

  static StyleGenericMaxSize Stretch() {
    StyleGenericMaxSize result;
    result.tag = Tag::Stretch;
    return result;
  }

  bool IsStretch() const {
    return tag == Tag::Stretch;
  }

  static StyleGenericMaxSize FitContentFunction(const LengthPercent &_0) {
    StyleGenericMaxSize result;
    ::new (&result.fit_content_function._0) (LengthPercent)(_0);
    result.tag = Tag::FitContentFunction;
    return result;
  }

  bool IsFitContentFunction() const {
    return tag == Tag::FitContentFunction;
  }

  const LengthPercent& AsFitContentFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsFitContentFunction());
    return fit_content_function._0;
  }

  static StyleGenericMaxSize AnchorSizeFunction(const StyleBox<StyleGenericAnchorSizeFunction<StyleGenericMaxSize>> &_0) {
    StyleGenericMaxSize result;
    ::new (&result.anchor_size_function._0) (StyleBox<StyleGenericAnchorSizeFunction<StyleGenericMaxSize>>)(_0);
    result.tag = Tag::AnchorSizeFunction;
    return result;
  }

  bool IsAnchorSizeFunction() const {
    return tag == Tag::AnchorSizeFunction;
  }

  const StyleBox<StyleGenericAnchorSizeFunction<StyleGenericMaxSize>>& AsAnchorSizeFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAnchorSizeFunction());
    return anchor_size_function._0;
  }

  static StyleGenericMaxSize AnchorContainingCalcFunction(const LengthPercent &_0) {
    StyleGenericMaxSize result;
    ::new (&result.anchor_containing_calc_function._0) (LengthPercent)(_0);
    result.tag = Tag::AnchorContainingCalcFunction;
    return result;
  }

  bool IsAnchorContainingCalcFunction() const {
    return tag == Tag::AnchorContainingCalcFunction;
  }

  const LengthPercent& AsAnchorContainingCalcFunction() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAnchorContainingCalcFunction());
    return anchor_containing_calc_function._0;
  }

  bool operator==(const StyleGenericMaxSize& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::LengthPercentage: return length_percentage == other.length_percentage;
      case Tag::FitContentFunction: return fit_content_function == other.fit_content_function;
      case Tag::AnchorSizeFunction: return anchor_size_function == other.anchor_size_function;
      case Tag::AnchorContainingCalcFunction: return anchor_containing_calc_function == other.anchor_containing_calc_function;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericMaxSize() {

  }
  public:


  ~StyleGenericMaxSize() {
    switch (tag) {
      case Tag::LengthPercentage: length_percentage.~StyleLengthPercentage_Body(); break;
      case Tag::FitContentFunction: fit_content_function.~StyleFitContentFunction_Body(); break;
      case Tag::AnchorSizeFunction: anchor_size_function.~StyleAnchorSizeFunction_Body(); break;
      case Tag::AnchorContainingCalcFunction: anchor_containing_calc_function.~StyleAnchorContainingCalcFunction_Body(); break;
      default: break;
    }
  }

  StyleGenericMaxSize(const StyleGenericMaxSize& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::LengthPercentage: ::new (&length_percentage) (StyleLengthPercentage_Body)(other.length_percentage); break;
      case Tag::FitContentFunction: ::new (&fit_content_function) (StyleFitContentFunction_Body)(other.fit_content_function); break;
      case Tag::AnchorSizeFunction: ::new (&anchor_size_function) (StyleAnchorSizeFunction_Body)(other.anchor_size_function); break;
      case Tag::AnchorContainingCalcFunction: ::new (&anchor_containing_calc_function) (StyleAnchorContainingCalcFunction_Body)(other.anchor_containing_calc_function); break;
      default: break;
    }
  }
  StyleGenericMaxSize& operator=(const StyleGenericMaxSize& other) {
    if (this != &other) {
      this->~StyleGenericMaxSize();
      new (this) StyleGenericMaxSize(other);
    }
    return *this;
  }
  inline bool ConvertsToLength() const;
  inline nscoord ToLength() const;
  inline bool ConvertsToPercentage() const;
  inline float ToPercentage() const;
  inline bool HasPercent() const;
  inline bool HasLengthAndPercentage() const;
  inline bool BehavesLikeStretchOnInlineAxis() const;
  inline bool BehavesLikeStretchOnBlockAxis() const;
  inline bool BehavesLikeStretch(LogicalAxis) const;
  inline bool BehavesLikeInitialValueOnBlockAxis() const;
  inline bool BehavesLikeInitialValue(LogicalAxis) const;
  inline bool HasAnchorPositioningFunction() const;
  inline explicit StyleGenericMaxSize(const LengthPercent &);
};

/// A computed value for `max-width` or `max-height` property.
using StyleMaxSize = StyleGenericMaxSize<StyleNonNegativeLengthPercentage>;

struct StyleWritingMode {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleWritingMode operator~() const {
    return StyleWritingMode { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleWritingMode operator|(const StyleWritingMode& other) const {
    return StyleWritingMode { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleWritingMode& operator|=(const StyleWritingMode& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleWritingMode operator&(const StyleWritingMode& other) const {
    return StyleWritingMode { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleWritingMode& operator&=(const StyleWritingMode& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleWritingMode operator^(const StyleWritingMode& other) const {
    return StyleWritingMode { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleWritingMode& operator^=(const StyleWritingMode& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleWritingMode& other) const {
    return _0 == other._0;
  }
  static const StyleWritingMode VERTICAL;
  static const StyleWritingMode INLINE_REVERSED;
  static const StyleWritingMode VERTICAL_LR;
  static const StyleWritingMode LINE_INVERTED;
  static const StyleWritingMode RTL;
  static const StyleWritingMode VERTICAL_SIDEWAYS;
  static const StyleWritingMode TEXT_SIDEWAYS;
  static const StyleWritingMode UPRIGHT;
  static const StyleWritingMode WRITING_MODE_HORIZONTAL_TB;
  static const StyleWritingMode WRITING_MODE_VERTICAL_RL;
  static const StyleWritingMode WRITING_MODE_VERTICAL_LR;
  static const StyleWritingMode WRITING_MODE_SIDEWAYS_RL;
  static const StyleWritingMode WRITING_MODE_SIDEWAYS_LR;
};
/// A vertical writing mode; writing-mode is vertical-rl,
/// vertical-lr, sideways-lr, or sideways-rl.
constexpr inline const StyleWritingMode StyleWritingMode::VERTICAL = StyleWritingMode{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// The inline flow direction is reversed against the physical
/// direction (i.e. right-to-left or bottom-to-top); writing-mode is
/// sideways-lr or direction is rtl (but not both).
///
/// (This bit can be derived from the others, but we store it for
/// convenience.)
constexpr inline const StyleWritingMode StyleWritingMode::INLINE_REVERSED = StyleWritingMode{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// A vertical writing mode whose block progression direction is left-
/// to-right; writing-mode is vertical-lr or sideways-lr.
///
/// Never set without VERTICAL.
constexpr inline const StyleWritingMode StyleWritingMode::VERTICAL_LR = StyleWritingMode{
  /* ._0 = */ (uint8_t)(1 << 2)
};
/// The line-over/line-under sides are inverted with respect to the
/// block-start/block-end edge; writing-mode is vertical-lr.
///
/// Never set without VERTICAL and VERTICAL_LR.
constexpr inline const StyleWritingMode StyleWritingMode::LINE_INVERTED = StyleWritingMode{
  /* ._0 = */ (uint8_t)(1 << 3)
};
/// direction is rtl.
constexpr inline const StyleWritingMode StyleWritingMode::RTL = StyleWritingMode{
  /* ._0 = */ (uint8_t)(1 << 4)
};
/// All text within a vertical writing mode is displayed sideways
/// and runs top-to-bottom or bottom-to-top; set in these cases:
///
/// * writing-mode: sideways-rl;
/// * writing-mode: sideways-lr;
///
/// Never set without VERTICAL.
constexpr inline const StyleWritingMode StyleWritingMode::VERTICAL_SIDEWAYS = StyleWritingMode{
  /* ._0 = */ (uint8_t)(1 << 5)
};
/// Similar to VERTICAL_SIDEWAYS, but is set via text-orientation;
/// set in these cases:
///
/// * writing-mode: vertical-rl; text-orientation: sideways;
/// * writing-mode: vertical-lr; text-orientation: sideways;
///
/// Never set without VERTICAL.
constexpr inline const StyleWritingMode StyleWritingMode::TEXT_SIDEWAYS = StyleWritingMode{
  /* ._0 = */ (uint8_t)(1 << 6)
};
/// Horizontal text within a vertical writing mode is displayed with each
/// glyph upright; set in these cases:
///
/// * writing-mode: vertical-rl; text-orientation: upright;
/// * writing-mode: vertical-lr: text-orientation: upright;
///
/// Never set without VERTICAL.
constexpr inline const StyleWritingMode StyleWritingMode::UPRIGHT = StyleWritingMode{
  /* ._0 = */ (uint8_t)(1 << 7)
};
/// Writing mode combinations that can be specified in CSS.
///
/// * writing-mode: horizontal-tb;
constexpr inline const StyleWritingMode StyleWritingMode::WRITING_MODE_HORIZONTAL_TB = StyleWritingMode{
  /* ._0 = */ (uint8_t)0
};
/// * writing-mode: vertical_rl;
constexpr inline const StyleWritingMode StyleWritingMode::WRITING_MODE_VERTICAL_RL = StyleWritingMode{
  /* ._0 = */ (uint8_t)(StyleWritingMode::VERTICAL)._0
};
/// * writing-mode: vertical-lr;
constexpr inline const StyleWritingMode StyleWritingMode::WRITING_MODE_VERTICAL_LR = StyleWritingMode{
  /* ._0 = */ (uint8_t)(((StyleWritingMode::VERTICAL)._0 | (StyleWritingMode::VERTICAL_LR)._0) | (StyleWritingMode::LINE_INVERTED)._0)
};
/// * writing-mode: sideways-rl;
constexpr inline const StyleWritingMode StyleWritingMode::WRITING_MODE_SIDEWAYS_RL = StyleWritingMode{
  /* ._0 = */ (uint8_t)((StyleWritingMode::VERTICAL)._0 | (StyleWritingMode::VERTICAL_SIDEWAYS)._0)
};
/// * writing-mode: sideways-lr;
constexpr inline const StyleWritingMode StyleWritingMode::WRITING_MODE_SIDEWAYS_LR = StyleWritingMode{
  /* ._0 = */ (uint8_t)(((StyleWritingMode::VERTICAL)._0 | (StyleWritingMode::VERTICAL_LR)._0) | (StyleWritingMode::VERTICAL_SIDEWAYS)._0)
};

/// Constants shared by multiple CSS Box Alignment properties
struct StyleAlignFlags {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleAlignFlags operator~() const {
    return StyleAlignFlags { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleAlignFlags operator|(const StyleAlignFlags& other) const {
    return StyleAlignFlags { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleAlignFlags& operator|=(const StyleAlignFlags& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleAlignFlags operator&(const StyleAlignFlags& other) const {
    return StyleAlignFlags { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleAlignFlags& operator&=(const StyleAlignFlags& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleAlignFlags operator^(const StyleAlignFlags& other) const {
    return StyleAlignFlags { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleAlignFlags& operator^=(const StyleAlignFlags& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleAlignFlags& other) const {
    return _0 == other._0;
  }
  static const StyleAlignFlags AUTO;
  static const StyleAlignFlags NORMAL;
  static const StyleAlignFlags START;
  static const StyleAlignFlags END;
  static const StyleAlignFlags FLEX_START;
  static const StyleAlignFlags FLEX_END;
  static const StyleAlignFlags CENTER;
  static const StyleAlignFlags LEFT;
  static const StyleAlignFlags RIGHT;
  static const StyleAlignFlags BASELINE;
  static const StyleAlignFlags LAST_BASELINE;
  static const StyleAlignFlags STRETCH;
  static const StyleAlignFlags SELF_START;
  static const StyleAlignFlags SELF_END;
  static const StyleAlignFlags SPACE_BETWEEN;
  static const StyleAlignFlags SPACE_AROUND;
  static const StyleAlignFlags SPACE_EVENLY;
  static const StyleAlignFlags ANCHOR_CENTER;
  static const StyleAlignFlags LEGACY;
  static const StyleAlignFlags SAFE;
  static const StyleAlignFlags UNSAFE;
  static const StyleAlignFlags FLAG_BITS;
};
/// {align,justify}-{content,items,self}: 'auto'
constexpr inline const StyleAlignFlags StyleAlignFlags::AUTO = StyleAlignFlags{
  /* ._0 = */ (uint8_t)0
};
/// 'normal'
constexpr inline const StyleAlignFlags StyleAlignFlags::NORMAL = StyleAlignFlags{
  /* ._0 = */ (uint8_t)1
};
/// 'start'
constexpr inline const StyleAlignFlags StyleAlignFlags::START = StyleAlignFlags{
  /* ._0 = */ (uint8_t)2
};
/// 'end'
constexpr inline const StyleAlignFlags StyleAlignFlags::END = StyleAlignFlags{
  /* ._0 = */ (uint8_t)3
};
/// 'flex-start'
constexpr inline const StyleAlignFlags StyleAlignFlags::FLEX_START = StyleAlignFlags{
  /* ._0 = */ (uint8_t)4
};
/// 'flex-end'
constexpr inline const StyleAlignFlags StyleAlignFlags::FLEX_END = StyleAlignFlags{
  /* ._0 = */ (uint8_t)5
};
/// 'center'
constexpr inline const StyleAlignFlags StyleAlignFlags::CENTER = StyleAlignFlags{
  /* ._0 = */ (uint8_t)6
};
/// 'left'
constexpr inline const StyleAlignFlags StyleAlignFlags::LEFT = StyleAlignFlags{
  /* ._0 = */ (uint8_t)7
};
/// 'right'
constexpr inline const StyleAlignFlags StyleAlignFlags::RIGHT = StyleAlignFlags{
  /* ._0 = */ (uint8_t)8
};
/// 'baseline'
constexpr inline const StyleAlignFlags StyleAlignFlags::BASELINE = StyleAlignFlags{
  /* ._0 = */ (uint8_t)9
};
/// 'last-baseline'
constexpr inline const StyleAlignFlags StyleAlignFlags::LAST_BASELINE = StyleAlignFlags{
  /* ._0 = */ (uint8_t)10
};
/// 'stretch'
constexpr inline const StyleAlignFlags StyleAlignFlags::STRETCH = StyleAlignFlags{
  /* ._0 = */ (uint8_t)11
};
/// 'self-start'
constexpr inline const StyleAlignFlags StyleAlignFlags::SELF_START = StyleAlignFlags{
  /* ._0 = */ (uint8_t)12
};
/// 'self-end'
constexpr inline const StyleAlignFlags StyleAlignFlags::SELF_END = StyleAlignFlags{
  /* ._0 = */ (uint8_t)13
};
/// 'space-between'
constexpr inline const StyleAlignFlags StyleAlignFlags::SPACE_BETWEEN = StyleAlignFlags{
  /* ._0 = */ (uint8_t)14
};
/// 'space-around'
constexpr inline const StyleAlignFlags StyleAlignFlags::SPACE_AROUND = StyleAlignFlags{
  /* ._0 = */ (uint8_t)15
};
/// 'space-evenly'
constexpr inline const StyleAlignFlags StyleAlignFlags::SPACE_EVENLY = StyleAlignFlags{
  /* ._0 = */ (uint8_t)16
};
/// `anchor-center`
constexpr inline const StyleAlignFlags StyleAlignFlags::ANCHOR_CENTER = StyleAlignFlags{
  /* ._0 = */ (uint8_t)17
};
/// 'legacy' (mutually exclusive w. SAFE & UNSAFE)
constexpr inline const StyleAlignFlags StyleAlignFlags::LEGACY = StyleAlignFlags{
  /* ._0 = */ (uint8_t)(1 << 5)
};
/// 'safe'
constexpr inline const StyleAlignFlags StyleAlignFlags::SAFE = StyleAlignFlags{
  /* ._0 = */ (uint8_t)(1 << 6)
};
/// 'unsafe' (mutually exclusive w. SAFE)
constexpr inline const StyleAlignFlags StyleAlignFlags::UNSAFE = StyleAlignFlags{
  /* ._0 = */ (uint8_t)(1 << 7)
};
/// Mask for the additional flags above.
constexpr inline const StyleAlignFlags StyleAlignFlags::FLAG_BITS = StyleAlignFlags{
  /* ._0 = */ (uint8_t)224
};

/// Specified value for the text-transform property.
/// (The spec grammar gives
/// `none | math-auto | [capitalize | uppercase | lowercase] || full-width || full-size-kana`.)
/// https://drafts.csswg.org/css-text-4/#text-transform-property
struct StyleTextTransform {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleTextTransform operator~() const {
    return StyleTextTransform { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleTextTransform operator|(const StyleTextTransform& other) const {
    return StyleTextTransform { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleTextTransform& operator|=(const StyleTextTransform& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleTextTransform operator&(const StyleTextTransform& other) const {
    return StyleTextTransform { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleTextTransform& operator&=(const StyleTextTransform& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleTextTransform operator^(const StyleTextTransform& other) const {
    return StyleTextTransform { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleTextTransform& operator^=(const StyleTextTransform& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleTextTransform& other) const {
    return _0 == other._0;
  }
  bool IsNone() const { return *this == NONE; }
  static const StyleTextTransform NONE;
  static const StyleTextTransform UPPERCASE;
  static const StyleTextTransform LOWERCASE;
  static const StyleTextTransform CAPITALIZE;
  static const StyleTextTransform MATH_AUTO;
  static const StyleTextTransform CASE_TRANSFORMS;
  static const StyleTextTransform FULL_WIDTH;
  static const StyleTextTransform FULL_SIZE_KANA;
};
/// none
constexpr inline const StyleTextTransform StyleTextTransform::NONE = StyleTextTransform{
  /* ._0 = */ (uint8_t)0
};
/// All uppercase.
constexpr inline const StyleTextTransform StyleTextTransform::UPPERCASE = StyleTextTransform{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// All lowercase.
constexpr inline const StyleTextTransform StyleTextTransform::LOWERCASE = StyleTextTransform{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// Capitalize each word.
constexpr inline const StyleTextTransform StyleTextTransform::CAPITALIZE = StyleTextTransform{
  /* ._0 = */ (uint8_t)(1 << 2)
};
/// Automatic italicization of math variables.
constexpr inline const StyleTextTransform StyleTextTransform::MATH_AUTO = StyleTextTransform{
  /* ._0 = */ (uint8_t)(1 << 3)
};
/// All the case transforms, which are exclusive with each other.
/// Except for math-auto, they can be mixed with full-width or full-size-kana.
constexpr inline const StyleTextTransform StyleTextTransform::CASE_TRANSFORMS = StyleTextTransform{
  /* ._0 = */ (uint8_t)((((StyleTextTransform::UPPERCASE)._0 | (StyleTextTransform::LOWERCASE)._0) | (StyleTextTransform::CAPITALIZE)._0) | (StyleTextTransform::MATH_AUTO)._0)
};
/// full-width
constexpr inline const StyleTextTransform StyleTextTransform::FULL_WIDTH = StyleTextTransform{
  /* ._0 = */ (uint8_t)(1 << 4)
};
/// full-size-kana
constexpr inline const StyleTextTransform StyleTextTransform::FULL_SIZE_KANA = StyleTextTransform{
  /* ._0 = */ (uint8_t)(1 << 5)
};

/// https://drafts.csswg.org/css-anchor-position-1/#propdef-anchor-name
using StyleAnchorNameIdent = StyleArcSlice<StyleDashedIdent>;

/// https://drafts.csswg.org/css-anchor-position-1/#propdef-anchor-name
using StyleAnchorName = StyleTreeScoped<StyleAnchorNameIdent>;

#if defined(CBINDGEN_IS_GECKO)
/// A CSS `<ident>` stored as an `Atom`.
using StyleAtomIdent = StyleAtom;
#endif

/// List of scoped names, or none.
using StyleScopedNameList = StyleArcSlice<StyleAtomIdent>;

/// A scoped name type, such as:
/// * https://drafts.csswg.org/css-anchor-position-1/#propdef-scope
using StyleScopedName = StyleTreeScoped<StyleScopedNameList>;

/// The <keyframes-name>.
///
/// <https://drafts.csswg.org/css-animations/#typedef-keyframes-name>
///
/// We use a single atom for this. Empty atom represents `none` animation.
using StyleKeyframesName = StyleAtom;

/// A value for the `animation-name` property.
struct StyleAnimationName {
  StyleKeyframesName _0;

  bool operator==(const StyleAnimationName& other) const {
    return _0 == other._0;
  }
 public:
  StyleAnimationName();
};

/// The identifier for a timeline name.
struct StyleTimelineIdent {
  StyleDashedIdent _0;

  bool operator==(const StyleTimelineIdent& other) const {
    return _0 == other._0;
  }
 public:
  StyleTimelineIdent();
  nsAtom* AsAtom() const { return _0.AsAtom(); }
};

/// The typedef of scroll-timeline-name or view-timeline-name.
///
/// https://drafts.csswg.org/scroll-animations-1/#scroll-timeline-name
/// https://drafts.csswg.org/scroll-animations-1/#view-timeline-name
using StyleTimelineName = StyleTreeScoped<StyleTimelineIdent>;

/// The scroll() notation.
/// https://drafts.csswg.org/scroll-animations-1/#scroll-notation
struct StyleScrollFunction {
  /// The scroll container element whose scroll position drives the progress of the timeline.
  StyleScroller scroller;
  /// The axis of scrolling that drives the progress of the timeline.
  StyleScrollAxis axis;

  bool operator==(const StyleScrollFunction& other) const {
    return scroller == other.scroller &&
           axis == other.axis;
  }
};

/// The view() notation.
/// https://drafts.csswg.org/scroll-animations-1/#view-notation
template<typename LengthPercent>
struct StyleGenericViewFunction {
  /// The axis of scrolling that drives the progress of the timeline.
  StyleScrollAxis axis;
  /// An adjustment of the view progress visibility range.
  StyleGenericViewTimelineInset<LengthPercent> inset;

  bool operator==(const StyleGenericViewFunction& other) const {
    return axis == other.axis &&
           inset == other.inset;
  }
};

/// A value for the <single-animation-timeline>.
///
/// https://drafts.csswg.org/css-animations-2/#typedef-single-animation-timeline
template<typename LengthPercent>
struct StyleGenericAnimationTimeline {
  enum class Tag : uint8_t {
    /// Use default timeline. The animation’s timeline is a DocumentTimeline.
    Auto,
    /// The scroll-timeline name or view-timeline-name.
    /// This also includes `none` value by using an empty atom.
    /// https://drafts.csswg.org/scroll-animations-1/#scroll-timeline-name
    /// https://drafts.csswg.org/scroll-animations-1/#view-timeline-name
    Timeline,
    /// The scroll() notation.
    /// https://drafts.csswg.org/scroll-animations-1/#scroll-notation
    Scroll,
    /// The view() notation.
    /// https://drafts.csswg.org/scroll-animations-1/#view-notation
    View,
  };

  struct StyleTimeline_Body {
    StyleTimelineName _0;

    bool operator==(const StyleTimeline_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleScroll_Body {
    StyleScrollFunction _0;

    bool operator==(const StyleScroll_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleView_Body {
    StyleGenericViewFunction<LengthPercent> _0;

    bool operator==(const StyleView_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleTimeline_Body timeline;
    StyleScroll_Body scroll;
    StyleView_Body view;
  };

  static StyleGenericAnimationTimeline Auto() {
    StyleGenericAnimationTimeline result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleGenericAnimationTimeline Timeline(const StyleTimelineName &_0) {
    StyleGenericAnimationTimeline result;
    ::new (&result.timeline._0) (StyleTimelineName)(_0);
    result.tag = Tag::Timeline;
    return result;
  }

  bool IsTimeline() const {
    return tag == Tag::Timeline;
  }

  const StyleTimelineName& AsTimeline() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTimeline());
    return timeline._0;
  }

  static StyleGenericAnimationTimeline Scroll(const StyleScrollFunction &_0) {
    StyleGenericAnimationTimeline result;
    ::new (&result.scroll._0) (StyleScrollFunction)(_0);
    result.tag = Tag::Scroll;
    return result;
  }

  bool IsScroll() const {
    return tag == Tag::Scroll;
  }

  const StyleScrollFunction& AsScroll() const {
    MOZ_DIAGNOSTIC_ASSERT(IsScroll());
    return scroll._0;
  }

  static StyleGenericAnimationTimeline View(const StyleGenericViewFunction<LengthPercent> &_0) {
    StyleGenericAnimationTimeline result;
    ::new (&result.view._0) (StyleGenericViewFunction<LengthPercent>)(_0);
    result.tag = Tag::View;
    return result;
  }

  bool IsView() const {
    return tag == Tag::View;
  }

  const StyleGenericViewFunction<LengthPercent>& AsView() const {
    MOZ_DIAGNOSTIC_ASSERT(IsView());
    return view._0;
  }

  bool operator==(const StyleGenericAnimationTimeline& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Timeline: return timeline == other.timeline;
      case Tag::Scroll: return scroll == other.scroll;
      case Tag::View: return view == other.view;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericAnimationTimeline() {

  }
  public:


  ~StyleGenericAnimationTimeline() {
    switch (tag) {
      case Tag::Timeline: timeline.~StyleTimeline_Body(); break;
      case Tag::Scroll: scroll.~StyleScroll_Body(); break;
      case Tag::View: view.~StyleView_Body(); break;
      default: break;
    }
  }

  StyleGenericAnimationTimeline(const StyleGenericAnimationTimeline& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Timeline: ::new (&timeline) (StyleTimeline_Body)(other.timeline); break;
      case Tag::Scroll: ::new (&scroll) (StyleScroll_Body)(other.scroll); break;
      case Tag::View: ::new (&view) (StyleView_Body)(other.view); break;
      default: break;
    }
  }
  StyleGenericAnimationTimeline& operator=(const StyleGenericAnimationTimeline& other) {
    if (this != &other) {
      this->~StyleGenericAnimationTimeline();
      new (this) StyleGenericAnimationTimeline(other);
    }
    return *this;
  }
};

/// A computed value for the `animation-timeline` property.
using StyleAnimationTimeline = StyleGenericAnimationTimeline<StyleLengthPercentage>;

/// A computed value for the `animation-iteration-count` property.
struct StyleAnimationIterationCount {
  float _0;

  bool operator==(const StyleAnimationIterationCount& other) const {
    return _0 == other._0;
  }
};

/// The `animation-duration` property.
///
/// https://drafts.csswg.org/css-animations-2/#animation-duration
template<typename T>
struct StyleGenericAnimationDuration {
  enum class Tag : uint8_t {
    /// The initial value. However, we serialize this as 0s if the preference is disabled.
    Auto,
    /// The time value, <time [0s,∞]>.
    Time,
  };

  struct StyleTime_Body {
    T _0;

    bool operator==(const StyleTime_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleTime_Body time;
  };

  static StyleGenericAnimationDuration Auto() {
    StyleGenericAnimationDuration result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleGenericAnimationDuration Time(const T &_0) {
    StyleGenericAnimationDuration result;
    ::new (&result.time._0) (T)(_0);
    result.tag = Tag::Time;
    return result;
  }

  bool IsTime() const {
    return tag == Tag::Time;
  }

  const T& AsTime() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTime());
    return time._0;
  }

  bool operator==(const StyleGenericAnimationDuration& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Time: return time == other.time;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericAnimationDuration() {

  }
  public:


  ~StyleGenericAnimationDuration() {
    switch (tag) {
      case Tag::Time: time.~StyleTime_Body(); break;
      default: break;
    }
  }

  StyleGenericAnimationDuration(const StyleGenericAnimationDuration& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Time: ::new (&time) (StyleTime_Body)(other.time); break;
      default: break;
    }
  }
  StyleGenericAnimationDuration& operator=(const StyleGenericAnimationDuration& other) {
    if (this != &other) {
      this->~StyleGenericAnimationDuration();
      new (this) StyleGenericAnimationDuration(other);
    }
    return *this;
  }
};

/// A computed value for the `animation-duration` property.
using StyleAnimationDuration = StyleGenericAnimationDuration<StyleTime>;

/// An App Unit, the fundamental unit of length in Servo. Usually
/// 1/60th of a pixel (see `AU_PER_PX`)
///
/// Please ensure that the values are between `MIN_AU` and `MAX_AU`.
/// It is safe to construct invalid `Au` values, but it may lead to
/// panics and overflows.
using StyleAu = int32_t;

/// A computed value for border-width (and the like).
using StyleBorderSideWidth = StyleAu;

/// A generic value for the `border-spacing` property.
template<typename L>
using StyleGenericBorderSpacing = StyleSize2D<L>;

/// A computed value for the `border-spacing` longhand property.
using StyleBorderSpacing = StyleGenericBorderSpacing<StyleNonNegativeLength>;

/// Specified value of `-moz-force-broken-image-icon`
using StyleBoolInteger = bool;

/// <https://drafts.csswg.org/css-ui/#propdef-outline-style>
struct StyleOutlineStyle {
  enum class Tag : uint8_t {
    /// auto
    Auto,
    /// <border-style>
    BorderStyle,
  };

  struct StyleBorderStyle_Body {
    StyleBorderStyle _0;

    bool operator==(const StyleBorderStyle_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleBorderStyle_Body border_style;
  };

  static StyleOutlineStyle Auto() {
    StyleOutlineStyle result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleOutlineStyle BorderStyle(const StyleBorderStyle &_0) {
    StyleOutlineStyle result;
    ::new (&result.border_style._0) (StyleBorderStyle)(_0);
    result.tag = Tag::BorderStyle;
    return result;
  }

  bool IsBorderStyle() const {
    return tag == Tag::BorderStyle;
  }

  const StyleBorderStyle& AsBorderStyle() const {
    MOZ_DIAGNOSTIC_ASSERT(IsBorderStyle());
    return border_style._0;
  }

  bool operator==(const StyleOutlineStyle& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::BorderStyle: return border_style == other.border_style;
      default: break;
    }
    return true;
  }

  private:
  StyleOutlineStyle() {

  }
  public:


  ~StyleOutlineStyle() {
    switch (tag) {
      case Tag::BorderStyle: border_style.~StyleBorderStyle_Body(); break;
      default: break;
    }
  }

  StyleOutlineStyle(const StyleOutlineStyle& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::BorderStyle: ::new (&border_style) (StyleBorderStyle_Body)(other.border_style); break;
      default: break;
    }
  }
  StyleOutlineStyle& operator=(const StyleOutlineStyle& other) {
    if (this != &other) {
      this->~StyleOutlineStyle();
      new (this) StyleOutlineStyle(other);
    }
    return *this;
  }
};

/// A value both for font-variation-settings and font-feature-settings.
template<typename T>
using StyleFontSettings = CopyableTArray<T>;

/// Use FontSettings as computed type of FontFeatureSettings.
using StyleFontFeatureSettings = StyleFontSettings<StyleFeatureTagValue<StyleInteger>>;

/// The computed value for font-variation-settings.
using StyleFontVariationSettings = StyleFontSettings<StyleVariationValue<StyleNumber>>;

/// A wrapper of Number, but the value >= 0.
using StyleNonNegativeNumber = StyleNonNegative<StyleCSSFloat>;

/// A generic value for the `font-size-adjust` property.
///
/// https://drafts.csswg.org/css-fonts-5/#font-size-adjust-prop
template<typename Factor>
union StyleGenericFontSizeAdjust {
  enum class Tag : uint8_t {
    None,
    ExHeight,
    CapHeight,
    ChWidth,
    IcWidth,
    IcHeight,
  };

  struct ExHeight_Body {
    Tag tag;
    Factor _0;

    bool operator==(const ExHeight_Body& other) const {
      return _0 == other._0;
    }
  };

  struct CapHeight_Body {
    Tag tag;
    Factor _0;

    bool operator==(const CapHeight_Body& other) const {
      return _0 == other._0;
    }
  };

  struct ChWidth_Body {
    Tag tag;
    Factor _0;

    bool operator==(const ChWidth_Body& other) const {
      return _0 == other._0;
    }
  };

  struct IcWidth_Body {
    Tag tag;
    Factor _0;

    bool operator==(const IcWidth_Body& other) const {
      return _0 == other._0;
    }
  };

  struct IcHeight_Body {
    Tag tag;
    Factor _0;

    bool operator==(const IcHeight_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  ExHeight_Body ex_height;
  CapHeight_Body cap_height;
  ChWidth_Body ch_width;
  IcWidth_Body ic_width;
  IcHeight_Body ic_height;

  static StyleGenericFontSizeAdjust None() {
    StyleGenericFontSizeAdjust result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericFontSizeAdjust ExHeight(const Factor &_0) {
    StyleGenericFontSizeAdjust result;
    ::new (&result.ex_height._0) (Factor)(_0);
    result.tag = Tag::ExHeight;
    return result;
  }

  bool IsExHeight() const {
    return tag == Tag::ExHeight;
  }

  const Factor& AsExHeight() const {
    MOZ_DIAGNOSTIC_ASSERT(IsExHeight());
    return ex_height._0;
  }

  static StyleGenericFontSizeAdjust CapHeight(const Factor &_0) {
    StyleGenericFontSizeAdjust result;
    ::new (&result.cap_height._0) (Factor)(_0);
    result.tag = Tag::CapHeight;
    return result;
  }

  bool IsCapHeight() const {
    return tag == Tag::CapHeight;
  }

  const Factor& AsCapHeight() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCapHeight());
    return cap_height._0;
  }

  static StyleGenericFontSizeAdjust ChWidth(const Factor &_0) {
    StyleGenericFontSizeAdjust result;
    ::new (&result.ch_width._0) (Factor)(_0);
    result.tag = Tag::ChWidth;
    return result;
  }

  bool IsChWidth() const {
    return tag == Tag::ChWidth;
  }

  const Factor& AsChWidth() const {
    MOZ_DIAGNOSTIC_ASSERT(IsChWidth());
    return ch_width._0;
  }

  static StyleGenericFontSizeAdjust IcWidth(const Factor &_0) {
    StyleGenericFontSizeAdjust result;
    ::new (&result.ic_width._0) (Factor)(_0);
    result.tag = Tag::IcWidth;
    return result;
  }

  bool IsIcWidth() const {
    return tag == Tag::IcWidth;
  }

  const Factor& AsIcWidth() const {
    MOZ_DIAGNOSTIC_ASSERT(IsIcWidth());
    return ic_width._0;
  }

  static StyleGenericFontSizeAdjust IcHeight(const Factor &_0) {
    StyleGenericFontSizeAdjust result;
    ::new (&result.ic_height._0) (Factor)(_0);
    result.tag = Tag::IcHeight;
    return result;
  }

  bool IsIcHeight() const {
    return tag == Tag::IcHeight;
  }

  const Factor& AsIcHeight() const {
    MOZ_DIAGNOSTIC_ASSERT(IsIcHeight());
    return ic_height._0;
  }

  bool operator==(const StyleGenericFontSizeAdjust& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::ExHeight: return ex_height == other.ex_height;
      case Tag::CapHeight: return cap_height == other.cap_height;
      case Tag::ChWidth: return ch_width == other.ch_width;
      case Tag::IcWidth: return ic_width == other.ic_width;
      case Tag::IcHeight: return ic_height == other.ic_height;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericFontSizeAdjust() {

  }
  public:


  ~StyleGenericFontSizeAdjust() {
    switch (tag) {
      case Tag::ExHeight: ex_height.~ExHeight_Body(); break;
      case Tag::CapHeight: cap_height.~CapHeight_Body(); break;
      case Tag::ChWidth: ch_width.~ChWidth_Body(); break;
      case Tag::IcWidth: ic_width.~IcWidth_Body(); break;
      case Tag::IcHeight: ic_height.~IcHeight_Body(); break;
      default: break;
    }
  }

  StyleGenericFontSizeAdjust(const StyleGenericFontSizeAdjust& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::ExHeight: ::new (&ex_height) (ExHeight_Body)(other.ex_height); break;
      case Tag::CapHeight: ::new (&cap_height) (CapHeight_Body)(other.cap_height); break;
      case Tag::ChWidth: ::new (&ch_width) (ChWidth_Body)(other.ch_width); break;
      case Tag::IcWidth: ::new (&ic_width) (IcWidth_Body)(other.ic_width); break;
      case Tag::IcHeight: ::new (&ic_height) (IcHeight_Body)(other.ic_height); break;
      default: break;
    }
  }
  StyleGenericFontSizeAdjust& operator=(const StyleGenericFontSizeAdjust& other) {
    if (this != &other) {
      this->~StyleGenericFontSizeAdjust();
      new (this) StyleGenericFontSizeAdjust(other);
    }
    return *this;
  }
};

/// Preserve the readability of text when font fallback occurs.
using StyleFontSizeAdjust = StyleGenericFontSizeAdjust<StyleNonNegativeNumber>;

/// Allows authors to choose a palette from those supported by a color font
/// (and potentially @font-palette-values overrides).
struct StyleFontPalette {
  StyleAtom _0;

  bool operator==(const StyleFontPalette& other) const {
    return _0 == other._0;
  }
  inline static StyleFontPalette Normal();
};

/// Variants for east asian variant
struct StyleFontVariantEastAsian {
  uint16_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleFontVariantEastAsian operator~() const {
    return StyleFontVariantEastAsian { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleFontVariantEastAsian operator|(const StyleFontVariantEastAsian& other) const {
    return StyleFontVariantEastAsian { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleFontVariantEastAsian& operator|=(const StyleFontVariantEastAsian& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleFontVariantEastAsian operator&(const StyleFontVariantEastAsian& other) const {
    return StyleFontVariantEastAsian { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleFontVariantEastAsian& operator&=(const StyleFontVariantEastAsian& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleFontVariantEastAsian operator^(const StyleFontVariantEastAsian& other) const {
    return StyleFontVariantEastAsian { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleFontVariantEastAsian& operator^=(const StyleFontVariantEastAsian& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleFontVariantEastAsian& other) const {
    return _0 == other._0;
  }
  static const StyleFontVariantEastAsian NORMAL;
  static const StyleFontVariantEastAsian JIS78;
  static const StyleFontVariantEastAsian JIS83;
  static const StyleFontVariantEastAsian JIS90;
  static const StyleFontVariantEastAsian JIS04;
  static const StyleFontVariantEastAsian SIMPLIFIED;
  static const StyleFontVariantEastAsian TRADITIONAL;
  static const StyleFontVariantEastAsian JIS_GROUP;
  static const StyleFontVariantEastAsian FULL_WIDTH;
  static const StyleFontVariantEastAsian PROPORTIONAL_WIDTH;
  static const StyleFontVariantEastAsian RUBY;
  static const size_t COUNT;
};
/// None of the features
constexpr inline const StyleFontVariantEastAsian StyleFontVariantEastAsian::NORMAL = StyleFontVariantEastAsian{
  /* ._0 = */ (uint16_t)0
};
/// Enables rendering of JIS78 forms (OpenType feature: jp78)
constexpr inline const StyleFontVariantEastAsian StyleFontVariantEastAsian::JIS78 = StyleFontVariantEastAsian{
  /* ._0 = */ (uint16_t)(1 << 0)
};
/// Enables rendering of JIS83 forms (OpenType feature: jp83).
constexpr inline const StyleFontVariantEastAsian StyleFontVariantEastAsian::JIS83 = StyleFontVariantEastAsian{
  /* ._0 = */ (uint16_t)(1 << 1)
};
/// Enables rendering of JIS90 forms (OpenType feature: jp90).
constexpr inline const StyleFontVariantEastAsian StyleFontVariantEastAsian::JIS90 = StyleFontVariantEastAsian{
  /* ._0 = */ (uint16_t)(1 << 2)
};
/// Enables rendering of JIS2004 forms (OpenType feature: jp04).
constexpr inline const StyleFontVariantEastAsian StyleFontVariantEastAsian::JIS04 = StyleFontVariantEastAsian{
  /* ._0 = */ (uint16_t)(1 << 3)
};
/// Enables rendering of simplified forms (OpenType feature: smpl).
constexpr inline const StyleFontVariantEastAsian StyleFontVariantEastAsian::SIMPLIFIED = StyleFontVariantEastAsian{
  /* ._0 = */ (uint16_t)(1 << 4)
};
/// Enables rendering of traditional forms (OpenType feature: trad).
constexpr inline const StyleFontVariantEastAsian StyleFontVariantEastAsian::TRADITIONAL = StyleFontVariantEastAsian{
  /* ._0 = */ (uint16_t)(1 << 5)
};
/// These values are exclusive with each other.
constexpr inline const StyleFontVariantEastAsian StyleFontVariantEastAsian::JIS_GROUP = StyleFontVariantEastAsian{
  /* ._0 = */ (uint16_t)((((((StyleFontVariantEastAsian::JIS78)._0 | (StyleFontVariantEastAsian::JIS83)._0) | (StyleFontVariantEastAsian::JIS90)._0) | (StyleFontVariantEastAsian::JIS04)._0) | (StyleFontVariantEastAsian::SIMPLIFIED)._0) | (StyleFontVariantEastAsian::TRADITIONAL)._0)
};
/// Enables rendering of full-width variants (OpenType feature: fwid).
constexpr inline const StyleFontVariantEastAsian StyleFontVariantEastAsian::FULL_WIDTH = StyleFontVariantEastAsian{
  /* ._0 = */ (uint16_t)(1 << 6)
};
/// Enables rendering of proportionally-spaced variants (OpenType feature: pwid).
constexpr inline const StyleFontVariantEastAsian StyleFontVariantEastAsian::PROPORTIONAL_WIDTH = StyleFontVariantEastAsian{
  /* ._0 = */ (uint16_t)(1 << 7)
};
/// Enables display of ruby variant glyphs (OpenType feature: ruby).
constexpr inline const StyleFontVariantEastAsian StyleFontVariantEastAsian::RUBY = StyleFontVariantEastAsian{
  /* ._0 = */ (uint16_t)(1 << 8)
};
/// The number of variants.
constexpr inline const size_t StyleFontVariantEastAsian::COUNT = 9;

/// Variants of ligatures
struct StyleFontVariantLigatures {
  uint16_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleFontVariantLigatures operator~() const {
    return StyleFontVariantLigatures { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleFontVariantLigatures operator|(const StyleFontVariantLigatures& other) const {
    return StyleFontVariantLigatures { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleFontVariantLigatures& operator|=(const StyleFontVariantLigatures& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleFontVariantLigatures operator&(const StyleFontVariantLigatures& other) const {
    return StyleFontVariantLigatures { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleFontVariantLigatures& operator&=(const StyleFontVariantLigatures& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleFontVariantLigatures operator^(const StyleFontVariantLigatures& other) const {
    return StyleFontVariantLigatures { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleFontVariantLigatures& operator^=(const StyleFontVariantLigatures& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleFontVariantLigatures& other) const {
    return _0 == other._0;
  }
  static const StyleFontVariantLigatures NORMAL;
  static const StyleFontVariantLigatures NONE;
  static const StyleFontVariantLigatures COMMON_LIGATURES;
  static const StyleFontVariantLigatures NO_COMMON_LIGATURES;
  static const StyleFontVariantLigatures DISCRETIONARY_LIGATURES;
  static const StyleFontVariantLigatures NO_DISCRETIONARY_LIGATURES;
  static const StyleFontVariantLigatures HISTORICAL_LIGATURES;
  static const StyleFontVariantLigatures NO_HISTORICAL_LIGATURES;
  static const StyleFontVariantLigatures CONTEXTUAL;
  static const StyleFontVariantLigatures NO_CONTEXTUAL;
  static const size_t COUNT;
};
/// Specifies that common default features are enabled
constexpr inline const StyleFontVariantLigatures StyleFontVariantLigatures::NORMAL = StyleFontVariantLigatures{
  /* ._0 = */ (uint16_t)0
};
/// Specifies that no features are enabled;
constexpr inline const StyleFontVariantLigatures StyleFontVariantLigatures::NONE = StyleFontVariantLigatures{
  /* ._0 = */ (uint16_t)1
};
/// Enables display of common ligatures
constexpr inline const StyleFontVariantLigatures StyleFontVariantLigatures::COMMON_LIGATURES = StyleFontVariantLigatures{
  /* ._0 = */ (uint16_t)(1 << 1)
};
/// Disables display of common ligatures
constexpr inline const StyleFontVariantLigatures StyleFontVariantLigatures::NO_COMMON_LIGATURES = StyleFontVariantLigatures{
  /* ._0 = */ (uint16_t)(1 << 2)
};
/// Enables display of discretionary ligatures
constexpr inline const StyleFontVariantLigatures StyleFontVariantLigatures::DISCRETIONARY_LIGATURES = StyleFontVariantLigatures{
  /* ._0 = */ (uint16_t)(1 << 3)
};
/// Disables display of discretionary ligatures
constexpr inline const StyleFontVariantLigatures StyleFontVariantLigatures::NO_DISCRETIONARY_LIGATURES = StyleFontVariantLigatures{
  /* ._0 = */ (uint16_t)(1 << 4)
};
/// Enables display of historical ligatures
constexpr inline const StyleFontVariantLigatures StyleFontVariantLigatures::HISTORICAL_LIGATURES = StyleFontVariantLigatures{
  /* ._0 = */ (uint16_t)(1 << 5)
};
/// Disables display of historical ligatures
constexpr inline const StyleFontVariantLigatures StyleFontVariantLigatures::NO_HISTORICAL_LIGATURES = StyleFontVariantLigatures{
  /* ._0 = */ (uint16_t)(1 << 6)
};
/// Enables display of contextual alternates
constexpr inline const StyleFontVariantLigatures StyleFontVariantLigatures::CONTEXTUAL = StyleFontVariantLigatures{
  /* ._0 = */ (uint16_t)(1 << 7)
};
/// Disables display of contextual alternates
constexpr inline const StyleFontVariantLigatures StyleFontVariantLigatures::NO_CONTEXTUAL = StyleFontVariantLigatures{
  /* ._0 = */ (uint16_t)(1 << 8)
};
/// The number of variants.
constexpr inline const size_t StyleFontVariantLigatures::COUNT = 9;

/// Variants of numeric values
struct StyleFontVariantNumeric {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleFontVariantNumeric operator~() const {
    return StyleFontVariantNumeric { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleFontVariantNumeric operator|(const StyleFontVariantNumeric& other) const {
    return StyleFontVariantNumeric { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleFontVariantNumeric& operator|=(const StyleFontVariantNumeric& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleFontVariantNumeric operator&(const StyleFontVariantNumeric& other) const {
    return StyleFontVariantNumeric { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleFontVariantNumeric& operator&=(const StyleFontVariantNumeric& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleFontVariantNumeric operator^(const StyleFontVariantNumeric& other) const {
    return StyleFontVariantNumeric { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleFontVariantNumeric& operator^=(const StyleFontVariantNumeric& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleFontVariantNumeric& other) const {
    return _0 == other._0;
  }
  static const StyleFontVariantNumeric NORMAL;
  static const StyleFontVariantNumeric LINING_NUMS;
  static const StyleFontVariantNumeric OLDSTYLE_NUMS;
  static const StyleFontVariantNumeric PROPORTIONAL_NUMS;
  static const StyleFontVariantNumeric TABULAR_NUMS;
  static const StyleFontVariantNumeric DIAGONAL_FRACTIONS;
  static const StyleFontVariantNumeric STACKED_FRACTIONS;
  static const StyleFontVariantNumeric SLASHED_ZERO;
  static const StyleFontVariantNumeric ORDINAL;
  static const size_t COUNT;
};
/// Specifies that common default features are enabled
constexpr inline const StyleFontVariantNumeric StyleFontVariantNumeric::NORMAL = StyleFontVariantNumeric{
  /* ._0 = */ (uint8_t)0
};
/// Enables display of lining numerals.
constexpr inline const StyleFontVariantNumeric StyleFontVariantNumeric::LINING_NUMS = StyleFontVariantNumeric{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// Enables display of old-style numerals.
constexpr inline const StyleFontVariantNumeric StyleFontVariantNumeric::OLDSTYLE_NUMS = StyleFontVariantNumeric{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// Enables display of proportional numerals.
constexpr inline const StyleFontVariantNumeric StyleFontVariantNumeric::PROPORTIONAL_NUMS = StyleFontVariantNumeric{
  /* ._0 = */ (uint8_t)(1 << 2)
};
/// Enables display of tabular numerals.
constexpr inline const StyleFontVariantNumeric StyleFontVariantNumeric::TABULAR_NUMS = StyleFontVariantNumeric{
  /* ._0 = */ (uint8_t)(1 << 3)
};
/// Enables display of lining diagonal fractions.
constexpr inline const StyleFontVariantNumeric StyleFontVariantNumeric::DIAGONAL_FRACTIONS = StyleFontVariantNumeric{
  /* ._0 = */ (uint8_t)(1 << 4)
};
/// Enables display of lining stacked fractions.
constexpr inline const StyleFontVariantNumeric StyleFontVariantNumeric::STACKED_FRACTIONS = StyleFontVariantNumeric{
  /* ._0 = */ (uint8_t)(1 << 5)
};
/// Enables display of slashed zeros.
constexpr inline const StyleFontVariantNumeric StyleFontVariantNumeric::SLASHED_ZERO = StyleFontVariantNumeric{
  /* ._0 = */ (uint8_t)(1 << 6)
};
/// Enables display of letter forms used with ordinal numbers.
constexpr inline const StyleFontVariantNumeric StyleFontVariantNumeric::ORDINAL = StyleFontVariantNumeric{
  /* ._0 = */ (uint8_t)(1 << 7)
};
/// The number of variants.
constexpr inline const size_t StyleFontVariantNumeric::COUNT = 8;

/// A CSS string stored as an `Atom`.
using StyleAtomString = StyleAtom;

/// Simple values we support for -moz-pref(). We don't want to deal with calc() and other
/// shenanigans for now.
template<typename I>
union StyleMozPrefFeatureValue {
  enum class Tag : uint8_t {
    /// No pref value, implicitly bool, but also used to represent missing prefs.
    None,
    /// A bool value.
    Boolean,
    /// An integer value, useful for int prefs.
    Integer,
    /// A string pref value.
    String,
  };

  struct Boolean_Body {
    Tag tag;
    StyleBoolValue _0;

    bool operator==(const Boolean_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Integer_Body {
    Tag tag;
    I _0;

    bool operator==(const Integer_Body& other) const {
      return _0 == other._0;
    }
  };

  struct String_Body {
    Tag tag;
    StyleAtomString _0;

    bool operator==(const String_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Boolean_Body boolean;
  Integer_Body integer;
  String_Body string;

  static StyleMozPrefFeatureValue None() {
    StyleMozPrefFeatureValue result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleMozPrefFeatureValue Boolean(const StyleBoolValue &_0) {
    StyleMozPrefFeatureValue result;
    ::new (&result.boolean._0) (StyleBoolValue)(_0);
    result.tag = Tag::Boolean;
    return result;
  }

  bool IsBoolean() const {
    return tag == Tag::Boolean;
  }

  const StyleBoolValue& AsBoolean() const {
    MOZ_DIAGNOSTIC_ASSERT(IsBoolean());
    return boolean._0;
  }

  static StyleMozPrefFeatureValue Integer(const I &_0) {
    StyleMozPrefFeatureValue result;
    ::new (&result.integer._0) (I)(_0);
    result.tag = Tag::Integer;
    return result;
  }

  bool IsInteger() const {
    return tag == Tag::Integer;
  }

  const I& AsInteger() const {
    MOZ_DIAGNOSTIC_ASSERT(IsInteger());
    return integer._0;
  }

  static StyleMozPrefFeatureValue String(const StyleAtomString &_0) {
    StyleMozPrefFeatureValue result;
    ::new (&result.string._0) (StyleAtomString)(_0);
    result.tag = Tag::String;
    return result;
  }

  bool IsString() const {
    return tag == Tag::String;
  }

  const StyleAtomString& AsString() const {
    MOZ_DIAGNOSTIC_ASSERT(IsString());
    return string._0;
  }

  bool operator==(const StyleMozPrefFeatureValue& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Boolean: return boolean == other.boolean;
      case Tag::Integer: return integer == other.integer;
      case Tag::String: return string == other.string;
      default: break;
    }
    return true;
  }

  private:
  StyleMozPrefFeatureValue() {

  }
  public:


  ~StyleMozPrefFeatureValue() {
    switch (tag) {
      case Tag::Boolean: boolean.~Boolean_Body(); break;
      case Tag::Integer: integer.~Integer_Body(); break;
      case Tag::String: string.~String_Body(); break;
      default: break;
    }
  }

  StyleMozPrefFeatureValue(const StyleMozPrefFeatureValue& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Boolean: ::new (&boolean) (Boolean_Body)(other.boolean); break;
      case Tag::Integer: ::new (&integer) (Integer_Body)(other.integer); break;
      case Tag::String: ::new (&string) (String_Body)(other.string); break;
      default: break;
    }
  }
  StyleMozPrefFeatureValue& operator=(const StyleMozPrefFeatureValue& other) {
    if (this != &other) {
      this->~StyleMozPrefFeatureValue();
      new (this) StyleMozPrefFeatureValue(other);
    }
    return *this;
  }
};

/// The computed -moz-pref() value.
using StyleComputedMozPrefFeatureValue = StyleMozPrefFeatureValue<StyleInteger>;

/// Misc information about a given computed style.
///
/// All flags are currently inherited for text, pseudo elements, and
/// anonymous boxes, see StyleBuilder::for_inheritance and its callsites.
/// If we ever want to add some flags that shouldn't inherit for them,
/// we might want to add a function to handle this.
struct StyleComputedValueFlags {
  uint32_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleComputedValueFlags operator~() const {
    return StyleComputedValueFlags { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleComputedValueFlags operator|(const StyleComputedValueFlags& other) const {
    return StyleComputedValueFlags { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleComputedValueFlags& operator|=(const StyleComputedValueFlags& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleComputedValueFlags operator&(const StyleComputedValueFlags& other) const {
    return StyleComputedValueFlags { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleComputedValueFlags& operator&=(const StyleComputedValueFlags& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleComputedValueFlags operator^(const StyleComputedValueFlags& other) const {
    return StyleComputedValueFlags { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleComputedValueFlags& operator^=(const StyleComputedValueFlags& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleComputedValueFlags& other) const {
    return _0 == other._0;
  }
  static const StyleComputedValueFlags HAS_TEXT_DECORATION_LINES;
  static const StyleComputedValueFlags SHOULD_SUPPRESS_LINEBREAK;
  static const StyleComputedValueFlags IS_TEXT_COMBINED;
  static const StyleComputedValueFlags IS_RELEVANT_LINK_VISITED;
  static const StyleComputedValueFlags IS_IN_FIRST_LINE_SUBTREE;
  static const StyleComputedValueFlags SELF_OR_ANCESTOR_HAS_CONTAIN_STYLE;
  static const StyleComputedValueFlags DISPLAY_OR_CONTENT_DEPEND_ON_INHERITED_STYLE;
  static const StyleComputedValueFlags INHERITS_RESET_STYLE;
  static const StyleComputedValueFlags DEPENDS_ON_SELF_FONT_METRICS;
  static const StyleComputedValueFlags DEPENDS_ON_INHERITED_FONT_METRICS;
  static const StyleComputedValueFlags IS_ROOT_ELEMENT_STYLE;
  static const StyleComputedValueFlags IS_IN_OPACITY_ZERO_SUBTREE;
  static const StyleComputedValueFlags HAS_AUTHOR_OR_USER_SPECIFIED_BORDER_BACKGROUND;
  static const StyleComputedValueFlags USES_VIEWPORT_UNITS;
  static const StyleComputedValueFlags USES_VIEWPORT_UNITS_ON_CONTAINER_QUERIES;
  static const StyleComputedValueFlags SELF_OR_ANCESTOR_HAS_SIZE_CONTAINER_TYPE;
  static const StyleComputedValueFlags USES_CONTAINER_UNITS;
  static const StyleComputedValueFlags HAS_AUTHOR_OR_USER_SPECIFIED_TEXT_COLOR;
  static const StyleComputedValueFlags CONSIDERED_NONTRIVIAL_SCOPED_STYLE;
  static const StyleComputedValueFlags DISPLAY_CONTENTS_IN_ITEM_CONTAINER;
  static const StyleComputedValueFlags HAS_AUTHOR_OR_USER_SPECIFIED_TEXT_SHADOW;
  static const StyleComputedValueFlags DEPENDS_ON_CONTAINER_STYLE_QUERY;
  static const StyleComputedValueFlags IS_IN_APPEARANCE_BASE_SUBTREE;
  static const StyleComputedValueFlags HAS_AUTHOR_OR_USER_SPECIFIED_GRID_AUTO_FLOW;
  static const StyleComputedValueFlags USES_FONT_OR_WM_RELATIVE_UNITS;
  static const StyleComputedValueFlags USES_FONT_OR_WM_RELATIVE_UNITS_ON_CONTAINER_QUERIES;
  static const StyleComputedValueFlags USES_SIBLING_COUNT;
  static const StyleComputedValueFlags USES_SIBLING_INDEX;
  static const StyleComputedValueFlags USES_VISITED_DEPENDENT_PROPERTIES;
  static const StyleComputedValueFlags USES_ELEMENT_SCOPED_RANDOM;
};
/// Whether the style or any of the ancestors has a text-decoration-line
/// property that should get propagated to descendants.
///
/// text-decoration-line is a reset property, but gets propagated in the
/// frame/box tree.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::HAS_TEXT_DECORATION_LINES = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 0)
};
/// Whether line break inside should be suppressed.
///
/// If this flag is set, the line should not be broken inside,
/// which means inlines act as if nowrap is set, <br> element is
/// suppressed, and blocks are inlinized.
///
/// This bit is propagated to all children of line participants.
/// It is currently used by ruby to make its content unbreakable.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::SHOULD_SUPPRESS_LINEBREAK = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 1)
};
/// A flag used to mark text that that has text-combine-upright.
///
/// This is used from Gecko's layout engine.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::IS_TEXT_COMBINED = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 2)
};
/// A flag used to mark styles under a relevant link that is also
/// visited.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::IS_RELEVANT_LINK_VISITED = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 3)
};
/// A flag used to mark styles which are a ::first-line or under one.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::IS_IN_FIRST_LINE_SUBTREE = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 4)
};
/// A flag used to mark styles which have contain:style or under one.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::SELF_OR_ANCESTOR_HAS_CONTAIN_STYLE = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 5)
};
/// Whether this style's `display` or `content`property depends on our parent style.
///
/// This is important because it may affect our optimizations to avoid
/// computing the style of pseudo-elements, given whether the
/// pseudo-element is generated depends on the `display` (or `content`) value.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::DISPLAY_OR_CONTENT_DEPEND_ON_INHERITED_STYLE = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 6)
};
/// Whether the child explicitly inherits any reset property.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::INHERITS_RESET_STYLE = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 7)
};
/// Whether any value on our style is font-metric-dependent on our
/// primary font.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::DEPENDS_ON_SELF_FONT_METRICS = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 8)
};
/// Whether any value on our style is font-metric-dependent on the
/// primary font of our parent.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::DEPENDS_ON_INHERITED_FONT_METRICS = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 9)
};
/// Whether this style is the style of the document element.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::IS_ROOT_ELEMENT_STYLE = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 10)
};
/// Whether this element is inside an `opacity: 0` subtree.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::IS_IN_OPACITY_ZERO_SUBTREE = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 11)
};
/// Whether there are author-specified rules for border-* properties
/// (except border-image-*), background-color, or background-image.
///
/// TODO(emilio): Maybe do include border-image, see:
///
/// https://github.com/w3c/csswg-drafts/issues/4777#issuecomment-604424845
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::HAS_AUTHOR_OR_USER_SPECIFIED_BORDER_BACKGROUND = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 12)
};
/// Whether the style depends on viewport units.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::USES_VIEWPORT_UNITS = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 13)
};
/// Whether the style depends on viewport units on container queries.
///
/// This needs to be a separate flag from `USES_VIEWPORT_UNITS` because
/// it causes us to re-match the style (rather than re-cascascading it,
/// which is enough for other uses of viewport units).
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::USES_VIEWPORT_UNITS_ON_CONTAINER_QUERIES = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 14)
};
/// A flag used to mark styles which have `container-type` of `size` or
/// `inline-size`, or under one.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::SELF_OR_ANCESTOR_HAS_SIZE_CONTAINER_TYPE = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 15)
};
/// Whether the style uses container query units, in which case the style depends on the
/// container's size and we can't reuse it across cousins (without double-checking the
/// container at least).
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::USES_CONTAINER_UNITS = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 16)
};
/// Whether there are author-specific rules for text `color`.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::HAS_AUTHOR_OR_USER_SPECIFIED_TEXT_COLOR = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 17)
};
/// Whether this style considered a scope style rule.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::CONSIDERED_NONTRIVIAL_SCOPED_STYLE = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 18)
};
/// Whether this style is that of a `display: contents` element that is either a direct
/// child of an item container or another `display: contents` element, the style of which
/// has this flag set, marked in order to cascade beyond them to the descendants of the
/// the item container that do generate a box.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::DISPLAY_CONTENTS_IN_ITEM_CONTAINER = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 19)
};
/// Whether there are author/user rules for `text-shadow`.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::HAS_AUTHOR_OR_USER_SPECIFIED_TEXT_SHADOW = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 20)
};
/// Whether this style depends on container style query.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::DEPENDS_ON_CONTAINER_STYLE_QUERY = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 21)
};
/// Whether this style is in an appearance: base subtree
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::IS_IN_APPEARANCE_BASE_SUBTREE = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 22)
};
/// Whether grid-auto-flow is author/user-specified.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::HAS_AUTHOR_OR_USER_SPECIFIED_GRID_AUTO_FLOW = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 23)
};
/// Whether this style has used font relative units. Note that this is different than the
/// FONT_METRICS bits, which don't include rem / em etc.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::USES_FONT_OR_WM_RELATIVE_UNITS = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 24)
};
/// Whether this style depends on font or writing mode relative units in container queries.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::USES_FONT_OR_WM_RELATIVE_UNITS_ON_CONTAINER_QUERIES = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 25)
};
/// Whether this style uses `sibling-count()`.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::USES_SIBLING_COUNT = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 26)
};
/// Whether this style uses `sibling-index()`.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::USES_SIBLING_INDEX = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 27)
};
/// Whether this style uses any visited-dependent properties.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::USES_VISITED_DEPENDENT_PROPERTIES = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 28)
};
/// Whether this style uses an element-scoped `random()`.
constexpr inline const StyleComputedValueFlags StyleComputedValueFlags::USES_ELEMENT_SCOPED_RANDOM = StyleComputedValueFlags{
  /* ._0 = */ (uint32_t)(1 << 29)
};

struct StyleDisplay {
  uint16_t _0;

  bool operator==(const StyleDisplay& other) const {
    return _0 == other._0;
  }
  inline StyleDisplayOutside Outside() const;
  inline StyleDisplayInside Inside() const;
  inline bool IsListItem() const;
  inline bool IsInlineFlow() const;
  inline bool IsInlineInside() const;
  inline bool IsInlineOutside() const;
  inline bool IsBlockOutside() const;
  inline bool IsRuby() const;
  inline bool IsInternalRuby() const;
  inline bool IsInternalTable() const;
  inline bool IsInternalTableExceptCell() const;
  static const uint16_t LIST_ITEM_MASK;
  static const uint16_t OUTSIDE_MASK;
  static const uint16_t INSIDE_MASK;
  static const uint16_t OUTSIDE_SHIFT;
  static const StyleDisplay None;
  static const StyleDisplay Contents;
  static const StyleDisplay Inline;
  static const StyleDisplay InlineBlock;
  static const StyleDisplay Block;
#if defined(CBINDGEN_IS_GECKO)
  static const StyleDisplay FlowRoot;
#endif
  static const StyleDisplay Flex;
  static const StyleDisplay InlineFlex;
  static const StyleDisplay Grid;
  static const StyleDisplay InlineGrid;
  static const StyleDisplay GridLanes;
  static const StyleDisplay InlineGridLanes;
  static const StyleDisplay Table;
  static const StyleDisplay InlineTable;
  static const StyleDisplay TableCaption;
#if defined(CBINDGEN_IS_GECKO)
  static const StyleDisplay Ruby;
#endif
#if defined(CBINDGEN_IS_GECKO)
  static const StyleDisplay WebkitBox;
#endif
#if defined(CBINDGEN_IS_GECKO)
  static const StyleDisplay WebkitInlineBox;
#endif
  static const StyleDisplay TableRowGroup;
  static const StyleDisplay TableHeaderGroup;
  static const StyleDisplay TableFooterGroup;
  static const StyleDisplay TableColumn;
  static const StyleDisplay TableColumnGroup;
  static const StyleDisplay TableRow;
  static const StyleDisplay TableCell;
#if defined(CBINDGEN_IS_GECKO)
  static const StyleDisplay RubyBase;
#endif
#if defined(CBINDGEN_IS_GECKO)
  static const StyleDisplay RubyBaseContainer;
#endif
#if defined(CBINDGEN_IS_GECKO)
  static const StyleDisplay RubyText;
#endif
#if defined(CBINDGEN_IS_GECKO)
  static const StyleDisplay RubyTextContainer;
#endif
};
constexpr inline const uint16_t StyleDisplay::LIST_ITEM_MASK = 32768;
constexpr inline const uint16_t StyleDisplay::OUTSIDE_MASK = 32512;
constexpr inline const uint16_t StyleDisplay::INSIDE_MASK = 255;
constexpr inline const uint16_t StyleDisplay::OUTSIDE_SHIFT = 8;
/// https://drafts.csswg.org/css-display/#the-display-properties
/// ::new() inlined so cbindgen can use it
constexpr inline const StyleDisplay StyleDisplay::None = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::None << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::None)
};
constexpr inline const StyleDisplay StyleDisplay::Contents = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::None << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::Contents)
};
constexpr inline const StyleDisplay StyleDisplay::Inline = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Inline << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::Flow)
};
constexpr inline const StyleDisplay StyleDisplay::InlineBlock = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Inline << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::FlowRoot)
};
constexpr inline const StyleDisplay StyleDisplay::Block = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Block << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::Flow)
};
#if defined(CBINDGEN_IS_GECKO)
constexpr inline const StyleDisplay StyleDisplay::FlowRoot = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Block << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::FlowRoot)
};
#endif
constexpr inline const StyleDisplay StyleDisplay::Flex = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Block << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::Flex)
};
constexpr inline const StyleDisplay StyleDisplay::InlineFlex = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Inline << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::Flex)
};
constexpr inline const StyleDisplay StyleDisplay::Grid = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Block << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::Grid)
};
constexpr inline const StyleDisplay StyleDisplay::InlineGrid = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Inline << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::Grid)
};
constexpr inline const StyleDisplay StyleDisplay::GridLanes = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Block << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::GridLanes)
};
constexpr inline const StyleDisplay StyleDisplay::InlineGridLanes = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Inline << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::GridLanes)
};
constexpr inline const StyleDisplay StyleDisplay::Table = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Block << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::Table)
};
constexpr inline const StyleDisplay StyleDisplay::InlineTable = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Inline << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::Table)
};
constexpr inline const StyleDisplay StyleDisplay::TableCaption = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::TableCaption << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::Flow)
};
#if defined(CBINDGEN_IS_GECKO)
constexpr inline const StyleDisplay StyleDisplay::Ruby = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Inline << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::Ruby)
};
#endif
#if defined(CBINDGEN_IS_GECKO)
constexpr inline const StyleDisplay StyleDisplay::WebkitBox = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Block << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::WebkitBox)
};
#endif
#if defined(CBINDGEN_IS_GECKO)
constexpr inline const StyleDisplay StyleDisplay::WebkitInlineBox = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::Inline << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::WebkitBox)
};
#endif
constexpr inline const StyleDisplay StyleDisplay::TableRowGroup = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::InternalTable << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::TableRowGroup)
};
constexpr inline const StyleDisplay StyleDisplay::TableHeaderGroup = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::InternalTable << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::TableHeaderGroup)
};
constexpr inline const StyleDisplay StyleDisplay::TableFooterGroup = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::InternalTable << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::TableFooterGroup)
};
constexpr inline const StyleDisplay StyleDisplay::TableColumn = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::InternalTable << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::TableColumn)
};
constexpr inline const StyleDisplay StyleDisplay::TableColumnGroup = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::InternalTable << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::TableColumnGroup)
};
constexpr inline const StyleDisplay StyleDisplay::TableRow = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::InternalTable << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::TableRow)
};
constexpr inline const StyleDisplay StyleDisplay::TableCell = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::InternalTable << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::TableCell)
};
#if defined(CBINDGEN_IS_GECKO)
/// Internal ruby boxes.
constexpr inline const StyleDisplay StyleDisplay::RubyBase = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::InternalRuby << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::RubyBase)
};
#endif
#if defined(CBINDGEN_IS_GECKO)
constexpr inline const StyleDisplay StyleDisplay::RubyBaseContainer = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::InternalRuby << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::RubyBaseContainer)
};
#endif
#if defined(CBINDGEN_IS_GECKO)
constexpr inline const StyleDisplay StyleDisplay::RubyText = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::InternalRuby << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::RubyText)
};
#endif
#if defined(CBINDGEN_IS_GECKO)
constexpr inline const StyleDisplay StyleDisplay::RubyTextContainer = StyleDisplay{
  /* ._0 = */ (((uint16_t)StyleDisplayOutside::InternalRuby << StyleDisplay::OUTSIDE_SHIFT) | (uint16_t)StyleDisplayInside::RubyTextContainer)
};
#endif

/// https://drafts.csswg.org/css-anchor-position-1/#propdef-position-anchor
union StylePositionAnchorKeyword {
  enum class Tag : uint8_t {
    /// `normal`
    Normal,
    /// `none`
    None,
    /// `auto`
    Auto,
    /// `<dashed-ident>`
    Ident,
  };

  struct Ident_Body {
    Tag tag;
    StyleDashedIdent _0;

    bool operator==(const Ident_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Ident_Body ident;

  static StylePositionAnchorKeyword Normal() {
    StylePositionAnchorKeyword result;
    result.tag = Tag::Normal;
    return result;
  }

  bool IsNormal() const {
    return tag == Tag::Normal;
  }

  static StylePositionAnchorKeyword None() {
    StylePositionAnchorKeyword result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StylePositionAnchorKeyword Auto() {
    StylePositionAnchorKeyword result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StylePositionAnchorKeyword Ident(const StyleDashedIdent &_0) {
    StylePositionAnchorKeyword result;
    ::new (&result.ident._0) (StyleDashedIdent)(_0);
    result.tag = Tag::Ident;
    return result;
  }

  bool IsIdent() const {
    return tag == Tag::Ident;
  }

  const StyleDashedIdent& AsIdent() const {
    MOZ_DIAGNOSTIC_ASSERT(IsIdent());
    return ident._0;
  }

  bool operator==(const StylePositionAnchorKeyword& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Ident: return ident == other.ident;
      default: break;
    }
    return true;
  }

  private:
  StylePositionAnchorKeyword() {

  }
  public:


  ~StylePositionAnchorKeyword() {
    switch (tag) {
      case Tag::Ident: ident.~Ident_Body(); break;
      default: break;
    }
  }

  StylePositionAnchorKeyword(const StylePositionAnchorKeyword& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Ident: ::new (&ident) (Ident_Body)(other.ident); break;
      default: break;
    }
  }
  StylePositionAnchorKeyword& operator=(const StylePositionAnchorKeyword& other) {
    if (this != &other) {
      this->~StylePositionAnchorKeyword();
      new (this) StylePositionAnchorKeyword(other);
    }
    return *this;
  }
};

/// https://drafts.csswg.org/css-anchor-position-1/#propdef-position-anchor
using StylePositionAnchor = StyleTreeScoped<StylePositionAnchorKeyword>;

/// https://drafts.csswg.org/css-anchor-position-1/#position-try-fallbacks
struct StylePositionTryFallbacksList {
  StyleArcSlice<StylePositionTryFallbacksItem> _0;

  bool operator==(const StylePositionTryFallbacksList& other) const {
    return _0 == other._0;
  }
};

/// https://drafts.csswg.org/css-anchor-position-1/#position-try-fallbacks
using StylePositionTryFallbacks = StyleTreeScoped<StylePositionTryFallbacksList>;

/// Specified keyword values for the position-visibility property.
struct StylePositionVisibility {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StylePositionVisibility operator~() const {
    return StylePositionVisibility { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StylePositionVisibility operator|(const StylePositionVisibility& other) const {
    return StylePositionVisibility { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StylePositionVisibility& operator|=(const StylePositionVisibility& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StylePositionVisibility operator&(const StylePositionVisibility& other) const {
    return StylePositionVisibility { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StylePositionVisibility& operator&=(const StylePositionVisibility& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StylePositionVisibility operator^(const StylePositionVisibility& other) const {
    return StylePositionVisibility { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StylePositionVisibility& operator^=(const StylePositionVisibility& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StylePositionVisibility& other) const {
    return _0 == other._0;
  }
  static const StylePositionVisibility ALWAYS;
  static const StylePositionVisibility ANCHORS_VALID;
  static const StylePositionVisibility ANCHORS_VISIBLE;
  static const StylePositionVisibility NO_OVERFLOW;
};
/// Element is displayed without regard for its anchors or its overflowing status.
constexpr inline const StylePositionVisibility StylePositionVisibility::ALWAYS = StylePositionVisibility{
  /* ._0 = */ (uint8_t)0
};
/// anchors-valid
constexpr inline const StylePositionVisibility StylePositionVisibility::ANCHORS_VALID = StylePositionVisibility{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// anchors-visible
constexpr inline const StylePositionVisibility StylePositionVisibility::ANCHORS_VISIBLE = StylePositionVisibility{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// no-overflow
constexpr inline const StylePositionVisibility StylePositionVisibility::NO_OVERFLOW = StylePositionVisibility{
  /* ._0 = */ (uint8_t)(1 << 2)
};

/// https://drafts.csswg.org/css-scroll-snap-1/#scroll-snap-align
struct StyleScrollSnapAlign {
  StyleScrollSnapAlignKeyword block;
  StyleScrollSnapAlignKeyword inline_;

  bool operator==(const StyleScrollSnapAlign& other) const {
    return block == other.block &&
           inline_ == other.inline_;
  }
};

/// https://drafts.csswg.org/css-scroll-snap-1/#scroll-snap-type
struct StyleScrollSnapType {
  StyleScrollSnapAxis axis;
  StyleScrollSnapStrictness strictness;

  bool operator==(const StyleScrollSnapType& other) const {
    return axis == other.axis &&
           strictness == other.strictness;
  }
};

/// https://drafts.csswg.org/css-overflow-4/#overflow-clip-margin
template<typename L>
struct StyleGenericOverflowClipMargin {
  /// The offset of the clip.
  L offset;
  /// The box that we're clipping to.
  StyleOverflowClipMarginBox visual_box;

  bool operator==(const StyleGenericOverflowClipMargin& other) const {
    return offset == other.offset &&
           visual_box == other.visual_box;
  }
};

/// A computed value for the `overflow-clip-margin` property.
using StyleOverflowClipMargin = StyleGenericOverflowClipMargin<StyleNonNegativeLength>;

/// The two insets of one scrollbar, for the chrome-only
/// `-moz-scrollbar-inset-block` / `-moz-scrollbar-inset-inline`. Each property
/// names the axis the scrollbar runs along, so `start` and `end` are the logical
/// start and end of that axis and flip with the writing mode.
template<typename L>
struct StyleGenericScrollbarInset {
  /// The inset at the logical start of the axis.
  L start;
  /// The inset at the logical end of the axis.
  L end;

  bool operator==(const StyleGenericScrollbarInset& other) const {
    return start == other.start &&
           end == other.end;
  }
};

/// A computed value for the `-moz-scrollbar-inset-block` / `-inline` properties.
using StyleScrollbarInset = StyleGenericScrollbarInset<StyleNonNegativeLength>;

/// A computed value for the `letter-spacing` property.
template<typename L>
using StyleGenericLetterSpacing = L;

/// This is generic just to make the #[derive()] code do the right thing for lengths.
using StyleLetterSpacing = StyleGenericLetterSpacing<StyleLengthPercentage>;

/// A computed type for `<length-percentage> | auto`.
using StyleLengthPercentageOrAuto = StyleGenericLengthPercentageOrAuto<StyleLengthPercentage>;

/// A generic value for the `line-height` property.
template<typename N, typename L>
struct StyleGenericLineHeight {
  enum class Tag : uint8_t {
    /// `normal`
    Normal,
    /// `<number>`
    Number,
    /// `<length-percentage>`
    Length,
  };

  struct StyleNumber_Body {
    N _0;

    bool operator==(const StyleNumber_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleLength_Body {
    L _0;

    bool operator==(const StyleLength_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleNumber_Body number;
    StyleLength_Body length;
  };

  static StyleGenericLineHeight Normal() {
    StyleGenericLineHeight result;
    result.tag = Tag::Normal;
    return result;
  }

  bool IsNormal() const {
    return tag == Tag::Normal;
  }

  static StyleGenericLineHeight Number(const N &_0) {
    StyleGenericLineHeight result;
    ::new (&result.number._0) (N)(_0);
    result.tag = Tag::Number;
    return result;
  }

  bool IsNumber() const {
    return tag == Tag::Number;
  }

  const N& AsNumber() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNumber());
    return number._0;
  }

  static StyleGenericLineHeight Length(const L &_0) {
    StyleGenericLineHeight result;
    ::new (&result.length._0) (L)(_0);
    result.tag = Tag::Length;
    return result;
  }

  bool IsLength() const {
    return tag == Tag::Length;
  }

  const L& AsLength() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLength());
    return length._0;
  }

  bool operator==(const StyleGenericLineHeight& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Number: return number == other.number;
      case Tag::Length: return length == other.length;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericLineHeight() {

  }
  public:


  ~StyleGenericLineHeight() {
    switch (tag) {
      case Tag::Number: number.~StyleNumber_Body(); break;
      case Tag::Length: length.~StyleLength_Body(); break;
      default: break;
    }
  }

  StyleGenericLineHeight(const StyleGenericLineHeight& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Number: ::new (&number) (StyleNumber_Body)(other.number); break;
      case Tag::Length: ::new (&length) (StyleLength_Body)(other.length); break;
      default: break;
    }
  }
  StyleGenericLineHeight& operator=(const StyleGenericLineHeight& other) {
    if (this != &other) {
      this->~StyleGenericLineHeight();
      new (this) StyleGenericLineHeight(other);
    }
    return *this;
  }
};

/// A computed value for the `line-height` property.
using StyleLineHeight = StyleGenericLineHeight<StyleNonNegativeNumber, StyleNonNegativeLength>;

/// A wrapper of LengthPercentageOrAuto, whose value must be >= 0.
using StyleNonNegativeLengthPercentageOrAuto = StyleGenericLengthPercentageOrAuto<StyleNonNegativeLengthPercentage>;

/// A generic `<length-percentage>` | normal` value.
template<typename LengthPercent>
struct StyleGenericLengthPercentageOrNormal {
  enum class Tag : uint8_t {
    LengthPercentage,
    Normal,
  };

  struct StyleLengthPercentage_Body {
    LengthPercent _0;

    bool operator==(const StyleLengthPercentage_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleLengthPercentage_Body length_percentage;
  };

  static StyleGenericLengthPercentageOrNormal LengthPercentage(const LengthPercent &_0) {
    StyleGenericLengthPercentageOrNormal result;
    ::new (&result.length_percentage._0) (LengthPercent)(_0);
    result.tag = Tag::LengthPercentage;
    return result;
  }

  bool IsLengthPercentage() const {
    return tag == Tag::LengthPercentage;
  }

  const LengthPercent& AsLengthPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLengthPercentage());
    return length_percentage._0;
  }

  static StyleGenericLengthPercentageOrNormal Normal() {
    StyleGenericLengthPercentageOrNormal result;
    result.tag = Tag::Normal;
    return result;
  }

  bool IsNormal() const {
    return tag == Tag::Normal;
  }

  bool operator==(const StyleGenericLengthPercentageOrNormal& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::LengthPercentage: return length_percentage == other.length_percentage;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericLengthPercentageOrNormal() {

  }
  public:


  ~StyleGenericLengthPercentageOrNormal() {
    switch (tag) {
      case Tag::LengthPercentage: length_percentage.~StyleLengthPercentage_Body(); break;
      default: break;
    }
  }

  StyleGenericLengthPercentageOrNormal(const StyleGenericLengthPercentageOrNormal& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::LengthPercentage: ::new (&length_percentage) (StyleLengthPercentage_Body)(other.length_percentage); break;
      default: break;
    }
  }
  StyleGenericLengthPercentageOrNormal& operator=(const StyleGenericLengthPercentageOrNormal& other) {
    if (this != &other) {
      this->~StyleGenericLengthPercentageOrNormal();
      new (this) StyleGenericLengthPercentageOrNormal(other);
    }
    return *this;
  }
};

/// Either a computed NonNegativeLengthPercentage or the `normal` keyword.
using StyleNonNegativeLengthPercentageOrNormal = StyleGenericLengthPercentageOrNormal<StyleNonNegativeLengthPercentage>;

/// Either a computed `<length>` or the `auto` keyword.
using StyleLengthOrAuto = StyleGenericLengthPercentageOrAuto<StyleLength>;

/// Either a non-negative `<length>` or the `auto` keyword.
using StyleNonNegativeLengthOrAuto = StyleGenericLengthPercentageOrAuto<StyleNonNegativeLength>;

/// The <text-edge> typedef, used by the `line-fit-edge` and
/// `text-box-edge` properties.
///
/// The first value specifies the text over edge; the second value
/// specifies the text under edge. If only one value is specified,
/// both edges are assigned that same keyword if possible; else
/// text is assumed as the missing value.
///
/// https://drafts.csswg.org/css-inline-3/#typedef-text-edge
struct StyleTextEdge {
  /// Font metric to use for the text over edge.
  StyleTextEdgeKeyword over;
  /// Font metric to use for the text under edge.
  StyleTextEdgeKeyword under;

  bool operator==(const StyleTextEdge& other) const {
    return over == other.over &&
           under == other.under;
  }
};

/// Specified value for the `text-box-edge` property.
///
/// https://drafts.csswg.org/css-inline-3/#text-box-edge
struct StyleTextBoxEdge {
  enum class Tag : uint8_t {
    /// Uses the value of `line-fit-edge`, interpreting `leading` (the initial value) as `text`.
    Auto,
    /// Uses the specified font metrics.
    TextEdge,
  };

  struct StyleTextEdge_Body {
    StyleTextEdge _0;

    bool operator==(const StyleTextEdge_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleTextEdge_Body text_edge;
  };

  static StyleTextBoxEdge Auto() {
    StyleTextBoxEdge result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleTextBoxEdge TextEdge(const StyleTextEdge &_0) {
    StyleTextBoxEdge result;
    ::new (&result.text_edge._0) (StyleTextEdge)(_0);
    result.tag = Tag::TextEdge;
    return result;
  }

  bool IsTextEdge() const {
    return tag == Tag::TextEdge;
  }

  const StyleTextEdge& AsTextEdge() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTextEdge());
    return text_edge._0;
  }

  bool operator==(const StyleTextBoxEdge& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::TextEdge: return text_edge == other.text_edge;
      default: break;
    }
    return true;
  }

  private:
  StyleTextBoxEdge() {

  }
  public:


  ~StyleTextBoxEdge() {
    switch (tag) {
      case Tag::TextEdge: text_edge.~StyleTextEdge_Body(); break;
      default: break;
    }
  }

  StyleTextBoxEdge(const StyleTextBoxEdge& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::TextEdge: ::new (&text_edge) (StyleTextEdge_Body)(other.text_edge); break;
      default: break;
    }
  }
  StyleTextBoxEdge& operator=(const StyleTextBoxEdge& other) {
    if (this != &other) {
      this->~StyleTextBoxEdge();
      new (this) StyleTextBoxEdge(other);
    }
    return *this;
  }
};

/// Specified value for the `text-box-trim` property.
///
/// https://drafts.csswg.org/css-inline-3/#text-box-edge
struct StyleTextBoxTrim {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleTextBoxTrim operator~() const {
    return StyleTextBoxTrim { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleTextBoxTrim operator|(const StyleTextBoxTrim& other) const {
    return StyleTextBoxTrim { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleTextBoxTrim& operator|=(const StyleTextBoxTrim& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleTextBoxTrim operator&(const StyleTextBoxTrim& other) const {
    return StyleTextBoxTrim { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleTextBoxTrim& operator&=(const StyleTextBoxTrim& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleTextBoxTrim operator^(const StyleTextBoxTrim& other) const {
    return StyleTextBoxTrim { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleTextBoxTrim& operator^=(const StyleTextBoxTrim& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleTextBoxTrim& other) const {
    return _0 == other._0;
  }
  static const StyleTextBoxTrim NONE;
  static const StyleTextBoxTrim TRIM_START;
  static const StyleTextBoxTrim TRIM_END;
  static const StyleTextBoxTrim TRIM_BOTH;
};
/// NONE
constexpr inline const StyleTextBoxTrim StyleTextBoxTrim::NONE = StyleTextBoxTrim{
  /* ._0 = */ (uint8_t)0
};
/// TRIM_START
constexpr inline const StyleTextBoxTrim StyleTextBoxTrim::TRIM_START = StyleTextBoxTrim{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// TRIM_END
constexpr inline const StyleTextBoxTrim StyleTextBoxTrim::TRIM_END = StyleTextBoxTrim{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// TRIM_BOTH
constexpr inline const StyleTextBoxTrim StyleTextBoxTrim::TRIM_BOTH = StyleTextBoxTrim{
  /* ._0 = */ (uint8_t)((StyleTextBoxTrim::TRIM_START)._0 | (StyleTextBoxTrim::TRIM_END)._0)
};

/// Implements type for text-decoration-thickness
/// which takes the grammar of auto | from-font | <length> | <percentage>
///
/// https://drafts.csswg.org/css-text-decor-4/
template<typename L>
struct StyleGenericTextDecorationLength {
  enum class Tag : uint8_t {
    LengthPercentage,
    Auto,
    FromFont,
  };

  struct StyleLengthPercentage_Body {
    L _0;

    bool operator==(const StyleLengthPercentage_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleLengthPercentage_Body length_percentage;
  };

  static StyleGenericTextDecorationLength LengthPercentage(const L &_0) {
    StyleGenericTextDecorationLength result;
    ::new (&result.length_percentage._0) (L)(_0);
    result.tag = Tag::LengthPercentage;
    return result;
  }

  bool IsLengthPercentage() const {
    return tag == Tag::LengthPercentage;
  }

  const L& AsLengthPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLengthPercentage());
    return length_percentage._0;
  }

  static StyleGenericTextDecorationLength Auto() {
    StyleGenericTextDecorationLength result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleGenericTextDecorationLength FromFont() {
    StyleGenericTextDecorationLength result;
    result.tag = Tag::FromFont;
    return result;
  }

  bool IsFromFont() const {
    return tag == Tag::FromFont;
  }

  bool operator==(const StyleGenericTextDecorationLength& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::LengthPercentage: return length_percentage == other.length_percentage;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericTextDecorationLength() {

  }
  public:


  ~StyleGenericTextDecorationLength() {
    switch (tag) {
      case Tag::LengthPercentage: length_percentage.~StyleLengthPercentage_Body(); break;
      default: break;
    }
  }

  StyleGenericTextDecorationLength(const StyleGenericTextDecorationLength& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::LengthPercentage: ::new (&length_percentage) (StyleLengthPercentage_Body)(other.length_percentage); break;
      default: break;
    }
  }
  StyleGenericTextDecorationLength& operator=(const StyleGenericTextDecorationLength& other) {
    if (this != &other) {
      this->~StyleGenericTextDecorationLength();
      new (this) StyleGenericTextDecorationLength(other);
    }
    return *this;
  }
};

/// Implements type for `text-decoration-thickness` property.
using StyleTextDecorationLength = StyleGenericTextDecorationLength<StyleLengthPercentage>;

/// Text decoration inset values.
///
/// https://drafts.csswg.org/css-text-decor-4/#text-decoration-skip-inset-property
template<typename LP>
struct StyleGenericTextDecorationInset {
  enum class Tag : uint8_t {
    /// `auto` value
    Auto,
    /// Start and end length values.
    LengthPercentage,
  };

  struct StyleLengthPercentage_Body {
    LP start;
    LP end;

    bool operator==(const StyleLengthPercentage_Body& other) const {
      return start == other.start &&
             end == other.end;
    }
  };

  Tag tag;
  union {
    StyleLengthPercentage_Body length_percentage;
  };

  static StyleGenericTextDecorationInset Auto() {
    StyleGenericTextDecorationInset result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleGenericTextDecorationInset LengthPercentage(const LP &start,
                                                          const LP &end) {
    StyleGenericTextDecorationInset result;
    ::new (&result.length_percentage.start) (LP)(start);
    ::new (&result.length_percentage.end) (LP)(end);
    result.tag = Tag::LengthPercentage;
    return result;
  }

  bool IsLengthPercentage() const {
    return tag == Tag::LengthPercentage;
  }

  const StyleLengthPercentage_Body& AsLengthPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLengthPercentage());
    return length_percentage;
  }

  bool operator==(const StyleGenericTextDecorationInset& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::LengthPercentage: return length_percentage == other.length_percentage;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericTextDecorationInset() {

  }
  public:


  ~StyleGenericTextDecorationInset() {
    switch (tag) {
      case Tag::LengthPercentage: length_percentage.~StyleLengthPercentage_Body(); break;
      default: break;
    }
  }

  StyleGenericTextDecorationInset(const StyleGenericTextDecorationInset& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::LengthPercentage: ::new (&length_percentage) (StyleLengthPercentage_Body)(other.length_percentage); break;
      default: break;
    }
  }
  StyleGenericTextDecorationInset& operator=(const StyleGenericTextDecorationInset& other) {
    if (this != &other) {
      this->~StyleGenericTextDecorationInset();
      new (this) StyleGenericTextDecorationInset(other);
    }
    return *this;
  }
};

/// Implements type for `text-decoration-inset` property.
using StyleTextDecorationInset = StyleGenericTextDecorationInset<StyleLengthPercentage>;

/// A generic value for the `initial-letter` property.
template<typename Number, typename Integer>
struct StyleGenericInitialLetter {
  /// The size, >=1, or 0 if `normal`.
  Number size;
  /// The sink, >=1, if specified, 0 otherwise.
  Integer sink;

  bool operator==(const StyleGenericInitialLetter& other) const {
    return size == other.size &&
           sink == other.sink;
  }
};

/// A computed value for the `initial-letter` property.
using StyleInitialLetter = StyleGenericInitialLetter<StyleCSSFloat, StyleCSSInteger>;

/// A generic value for the `flex-basis` property.
template<typename S>
struct StyleGenericFlexBasis {
  enum class Tag {
    /// `content`
    Content,
    /// `<width>`
    Size,
  };

  struct StyleSize_Body {
    S _0;

    bool operator==(const StyleSize_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleSize_Body size;
  };

  static StyleGenericFlexBasis Content() {
    StyleGenericFlexBasis result;
    result.tag = Tag::Content;
    return result;
  }

  bool IsContent() const {
    return tag == Tag::Content;
  }

  static StyleGenericFlexBasis Size(const S &_0) {
    StyleGenericFlexBasis result;
    ::new (&result.size._0) (S)(_0);
    result.tag = Tag::Size;
    return result;
  }

  bool IsSize() const {
    return tag == Tag::Size;
  }

  const S& AsSize() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSize());
    return size._0;
  }

  bool operator==(const StyleGenericFlexBasis& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Size: return size == other.size;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericFlexBasis() {

  }
  public:


  ~StyleGenericFlexBasis() {
    switch (tag) {
      case Tag::Size: size.~StyleSize_Body(); break;
      default: break;
    }
  }

  StyleGenericFlexBasis(const StyleGenericFlexBasis& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Size: ::new (&size) (StyleSize_Body)(other.size); break;
      default: break;
    }
  }
  StyleGenericFlexBasis& operator=(const StyleGenericFlexBasis& other) {
    if (this != &other) {
      this->~StyleGenericFlexBasis();
      new (this) StyleGenericFlexBasis(other);
    }
    return *this;
  }
  inline bool IsAuto() const;
};

/// A computed value for the `flex-basis` property.
using StyleFlexBasis = StyleGenericFlexBasis<StyleSize>;

/// A generic value for the `background-size` property.
template<typename LengthPercent>
struct StyleGenericBackgroundSize {
  enum class Tag : uint8_t {
    /// `<width> <height>`
    ExplicitSize,
    /// `cover`
    Cover,
    /// `contain`
    Contain,
  };

  struct StyleExplicitSize_Body {
    /// Explicit width.
    StyleGenericLengthPercentageOrAuto<LengthPercent> width;
    /// Explicit height.
    StyleGenericLengthPercentageOrAuto<LengthPercent> height;

    bool operator==(const StyleExplicitSize_Body& other) const {
      return width == other.width &&
             height == other.height;
    }
  };

  Tag tag;
  union {
    StyleExplicitSize_Body explicit_size;
  };

  static StyleGenericBackgroundSize ExplicitSize(const StyleGenericLengthPercentageOrAuto<LengthPercent> &width,
                                                 const StyleGenericLengthPercentageOrAuto<LengthPercent> &height) {
    StyleGenericBackgroundSize result;
    ::new (&result.explicit_size.width) (StyleGenericLengthPercentageOrAuto<LengthPercent>)(width);
    ::new (&result.explicit_size.height) (StyleGenericLengthPercentageOrAuto<LengthPercent>)(height);
    result.tag = Tag::ExplicitSize;
    return result;
  }

  bool IsExplicitSize() const {
    return tag == Tag::ExplicitSize;
  }

  const StyleExplicitSize_Body& AsExplicitSize() const {
    MOZ_DIAGNOSTIC_ASSERT(IsExplicitSize());
    return explicit_size;
  }

  static StyleGenericBackgroundSize Cover() {
    StyleGenericBackgroundSize result;
    result.tag = Tag::Cover;
    return result;
  }

  bool IsCover() const {
    return tag == Tag::Cover;
  }

  static StyleGenericBackgroundSize Contain() {
    StyleGenericBackgroundSize result;
    result.tag = Tag::Contain;
    return result;
  }

  bool IsContain() const {
    return tag == Tag::Contain;
  }

  bool operator==(const StyleGenericBackgroundSize& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::ExplicitSize: return explicit_size == other.explicit_size;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericBackgroundSize() {

  }
  public:


  ~StyleGenericBackgroundSize() {
    switch (tag) {
      case Tag::ExplicitSize: explicit_size.~StyleExplicitSize_Body(); break;
      default: break;
    }
  }

  StyleGenericBackgroundSize(const StyleGenericBackgroundSize& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::ExplicitSize: ::new (&explicit_size) (StyleExplicitSize_Body)(other.explicit_size); break;
      default: break;
    }
  }
  StyleGenericBackgroundSize& operator=(const StyleGenericBackgroundSize& other) {
    if (this != &other) {
      this->~StyleGenericBackgroundSize();
      new (this) StyleGenericBackgroundSize(other);
    }
    return *this;
  }
  bool IsInitialValue() const;
};

/// A computed value for the `background-size` property.
using StyleBackgroundSize = StyleGenericBackgroundSize<StyleNonNegativeLengthPercentage>;

/// A generic value for the `baseline-shift` property.
/// https://drafts.csswg.org/css-inline-3/#baseline-shift
template<typename LengthPercentage>
struct StyleGenericBaselineShift {
  enum class Tag : uint8_t {
    /// One of the baseline-shift keywords
    Keyword,
    /// Raise (positive value) or lower (negative value) by the specified length or specified percentage of the line-height.
    Length,
  };

  struct StyleKeyword_Body {
    StyleBaselineShiftKeyword _0;

    bool operator==(const StyleKeyword_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleLength_Body {
    LengthPercentage _0;

    bool operator==(const StyleLength_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleKeyword_Body keyword;
    StyleLength_Body length;
  };

  static StyleGenericBaselineShift Keyword(const StyleBaselineShiftKeyword &_0) {
    StyleGenericBaselineShift result;
    ::new (&result.keyword._0) (StyleBaselineShiftKeyword)(_0);
    result.tag = Tag::Keyword;
    return result;
  }

  bool IsKeyword() const {
    return tag == Tag::Keyword;
  }

  const StyleBaselineShiftKeyword& AsKeyword() const {
    MOZ_DIAGNOSTIC_ASSERT(IsKeyword());
    return keyword._0;
  }

  static StyleGenericBaselineShift Length(const LengthPercentage &_0) {
    StyleGenericBaselineShift result;
    ::new (&result.length._0) (LengthPercentage)(_0);
    result.tag = Tag::Length;
    return result;
  }

  bool IsLength() const {
    return tag == Tag::Length;
  }

  const LengthPercentage& AsLength() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLength());
    return length._0;
  }

  bool operator==(const StyleGenericBaselineShift& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Keyword: return keyword == other.keyword;
      case Tag::Length: return length == other.length;

    }
    return true;
  }

  private:
  StyleGenericBaselineShift() {

  }
  public:


  ~StyleGenericBaselineShift() {
    switch (tag) {
      case Tag::Keyword: keyword.~StyleKeyword_Body(); break;
      case Tag::Length: length.~StyleLength_Body(); break;

    }
  }

  StyleGenericBaselineShift(const StyleGenericBaselineShift& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Keyword: ::new (&keyword) (StyleKeyword_Body)(other.keyword); break;
      case Tag::Length: ::new (&length) (StyleLength_Body)(other.length); break;

    }
  }
  StyleGenericBaselineShift& operator=(const StyleGenericBaselineShift& other) {
    if (this != &other) {
      this->~StyleGenericBaselineShift();
      new (this) StyleGenericBaselineShift(other);
    }
    return *this;
  }
};

/// A computed value for the `baseline-shift` property.
using StyleBaselineShift = StyleGenericBaselineShift<StyleLengthPercentage>;

struct StyleNumberOrPercentage {
  enum class Tag : uint8_t {
    Percentage,
    Number,
  };

  struct StylePercentage_Body {
    StylePercentage _0;

    bool operator==(const StylePercentage_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleNumber_Body {
    StyleNumber _0;

    bool operator==(const StyleNumber_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StylePercentage_Body percentage;
    StyleNumber_Body number;
  };

  static StyleNumberOrPercentage Percentage(const StylePercentage &_0) {
    StyleNumberOrPercentage result;
    ::new (&result.percentage._0) (StylePercentage)(_0);
    result.tag = Tag::Percentage;
    return result;
  }

  bool IsPercentage() const {
    return tag == Tag::Percentage;
  }

  const StylePercentage& AsPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPercentage());
    return percentage._0;
  }

  static StyleNumberOrPercentage Number(const StyleNumber &_0) {
    StyleNumberOrPercentage result;
    ::new (&result.number._0) (StyleNumber)(_0);
    result.tag = Tag::Number;
    return result;
  }

  bool IsNumber() const {
    return tag == Tag::Number;
  }

  const StyleNumber& AsNumber() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNumber());
    return number._0;
  }

  bool operator==(const StyleNumberOrPercentage& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Percentage: return percentage == other.percentage;
      case Tag::Number: return number == other.number;

    }
    return true;
  }

  private:
  StyleNumberOrPercentage() {

  }
  public:


  ~StyleNumberOrPercentage() {
    switch (tag) {
      case Tag::Percentage: percentage.~StylePercentage_Body(); break;
      case Tag::Number: number.~StyleNumber_Body(); break;

    }
  }

  StyleNumberOrPercentage(const StyleNumberOrPercentage& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Percentage: ::new (&percentage) (StylePercentage_Body)(other.percentage); break;
      case Tag::Number: ::new (&number) (StyleNumber_Body)(other.number); break;

    }
  }
  StyleNumberOrPercentage& operator=(const StyleNumberOrPercentage& other) {
    if (this != &other) {
      this->~StyleNumberOrPercentage();
      new (this) StyleNumberOrPercentage(other);
    }
    return *this;
  }
};

/// A non-negative <number-percentage>.
using StyleNonNegativeNumberOrPercentage = StyleNonNegative<StyleNumberOrPercentage>;

/// A generic value for the `border-image-slice` property.
template<typename NumberOrPercentage>
struct StyleGenericBorderImageSlice {
  /// The offsets.
  StyleRect<NumberOrPercentage> offsets;
  /// Whether to fill the middle part.
  bool fill;

  bool operator==(const StyleGenericBorderImageSlice& other) const {
    return offsets == other.offsets &&
           fill == other.fill;
  }
};

/// A computed value for the `border-image-slice` property.
using StyleBorderImageSlice = StyleGenericBorderImageSlice<StyleNonNegativeNumberOrPercentage>;

/// The specified value for the `border-image-repeat` property.
///
/// https://drafts.csswg.org/css-backgrounds/#the-border-image-repeat
struct StyleBorderImageRepeat {
  StyleBorderImageRepeatKeyword _0;
  StyleBorderImageRepeatKeyword _1;

  bool operator==(const StyleBorderImageRepeat& other) const {
    return _0 == other._0 &&
           _1 == other._1;
  }
};

/// A computed value for the `border-radius` property.
using StyleBorderRadius = StyleGenericBorderRadius<StyleNonNegativeLengthPercentage>;

/// The computed value for a single corner shape.
///
/// Per the spec, the computed value is always `superellipse(K)` where `K` may
/// be any real value, including +infinity (for `square`) and -infinity
/// (for `notch`).
struct StyleCornerShape {
  /// The K parameter from the `superellipse()` function.
  float k;

  bool operator==(const StyleCornerShape& other) const {
    return k == other.k;
  }
};

/// A generic value for the four corners of `corner-shape`.
///
/// This mirrors the per-corner layout of `BorderRadius` so it can be used as
/// the underlying storage for the four `corner-*-*-shape` longhands and their
/// shorthand `corner-shape`.
///
/// <https://drafts.csswg.org/css-borders-4/#corner-shaping>
template<typename S>
struct StyleGenericCornerShapeRect {
  /// The top-left corner shape.
  S top_left;
  /// The top-right corner shape.
  S top_right;
  /// The bottom-right corner shape.
  S bottom_right;
  /// The bottom-left corner shape.
  S bottom_left;

  bool operator==(const StyleGenericCornerShapeRect& other) const {
    return top_left == other.top_left &&
           top_right == other.top_right &&
           bottom_right == other.bottom_right &&
           bottom_left == other.bottom_left;
  }
};

/// The four computed corner shapes for an element.
using StyleCornerShapeRect = StyleGenericCornerShapeRect<StyleCornerShape>;

/// A wrapper of greater-than-or-equal-to-one values.
template<typename T>
using StyleGreaterThanOrEqualToOne = T;

/// A wrapper of Integer, but only accept a value >= 1.
using StylePositiveInteger = StyleGreaterThanOrEqualToOne<StyleCSSInteger>;

/// A generic type for `column-count` values.
template<typename PositiveInteger>
union StyleGenericColumnCount {
  enum class Tag : uint8_t {
    /// A positive integer.
    Integer,
    /// The keyword `auto`.
    Auto,
  };

  struct Integer_Body {
    Tag tag;
    PositiveInteger _0;

    bool operator==(const Integer_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Integer_Body integer;

  static StyleGenericColumnCount Integer(const PositiveInteger &_0) {
    StyleGenericColumnCount result;
    ::new (&result.integer._0) (PositiveInteger)(_0);
    result.tag = Tag::Integer;
    return result;
  }

  bool IsInteger() const {
    return tag == Tag::Integer;
  }

  const PositiveInteger& AsInteger() const {
    MOZ_DIAGNOSTIC_ASSERT(IsInteger());
    return integer._0;
  }

  static StyleGenericColumnCount Auto() {
    StyleGenericColumnCount result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  bool operator==(const StyleGenericColumnCount& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Integer: return integer == other.integer;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericColumnCount() {

  }
  public:


  ~StyleGenericColumnCount() {
    switch (tag) {
      case Tag::Integer: integer.~Integer_Body(); break;
      default: break;
    }
  }

  StyleGenericColumnCount(const StyleGenericColumnCount& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Integer: ::new (&integer) (Integer_Body)(other.integer); break;
      default: break;
    }
  }
  StyleGenericColumnCount& operator=(const StyleGenericColumnCount& other) {
    if (this != &other) {
      this->~StyleGenericColumnCount();
      new (this) StyleGenericColumnCount(other);
    }
    return *this;
  }
};

/// A computed type for `column-count` values.
using StyleColumnCount = StyleGenericColumnCount<StylePositiveInteger>;

/// A CSS rule reference. Should mirror `CssRule`.
struct StyleCssRuleRef {
  enum class Tag {
    Style,
    Namespace,
    Import,
    Media,
    CustomMedia,
    Container,
    FontFace,
    FontFeatureValues,
    FontPaletteValues,
    CounterStyle,
    Keyframes,
    Margin,
    Supports,
    Page,
    Property,
    Document,
    LayerBlock,
    LayerStatement,
    Scope,
    StartingStyle,
    AppearanceBase,
    PositionTry,
    NestedDeclarations,
    ViewTransition,
  };

  struct StyleStyle_Body {
    const StyleLockedStyleRule *_0;

    bool operator==(const StyleStyle_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleNamespace_Body {
    const StyleNamespaceRule *_0;

    bool operator==(const StyleNamespace_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleImport_Body {
    const StyleLockedImportRule *_0;

    bool operator==(const StyleImport_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleMedia_Body {
    const StyleMediaRule *_0;

    bool operator==(const StyleMedia_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleCustomMedia_Body {
    const StyleCustomMediaRule *_0;

    bool operator==(const StyleCustomMedia_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleContainer_Body {
    const StyleContainerRule *_0;

    bool operator==(const StyleContainer_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleFontFace_Body {
    const StyleLockedFontFaceRule *_0;

    bool operator==(const StyleFontFace_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleFontFeatureValues_Body {
    const StyleFontFeatureValuesRule *_0;

    bool operator==(const StyleFontFeatureValues_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleFontPaletteValues_Body {
    const StyleFontPaletteValuesRule *_0;

    bool operator==(const StyleFontPaletteValues_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleCounterStyle_Body {
    const StyleLockedCounterStyleRule *_0;

    bool operator==(const StyleCounterStyle_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleKeyframes_Body {
    const StyleLockedKeyframesRule *_0;

    bool operator==(const StyleKeyframes_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleMargin_Body {
    const StyleMarginRule *_0;

    bool operator==(const StyleMargin_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleSupports_Body {
    const StyleSupportsRule *_0;

    bool operator==(const StyleSupports_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StylePage_Body {
    const StyleLockedPageRule *_0;

    bool operator==(const StylePage_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleProperty_Body {
    const StylePropertyRule *_0;

    bool operator==(const StyleProperty_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleDocument_Body {
    const StyleDocumentRule *_0;

    bool operator==(const StyleDocument_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleLayerBlock_Body {
    const StyleLayerBlockRule *_0;

    bool operator==(const StyleLayerBlock_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleLayerStatement_Body {
    const StyleLayerStatementRule *_0;

    bool operator==(const StyleLayerStatement_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleScope_Body {
    const StyleScopeRule *_0;

    bool operator==(const StyleScope_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleStartingStyle_Body {
    const StyleStartingStyleRule *_0;

    bool operator==(const StyleStartingStyle_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAppearanceBase_Body {
    const StyleAppearanceBaseRule *_0;

    bool operator==(const StyleAppearanceBase_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StylePositionTry_Body {
    const StyleLockedPositionTryRule *_0;

    bool operator==(const StylePositionTry_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleNestedDeclarations_Body {
    const StyleLockedNestedDeclarationsRule *_0;

    bool operator==(const StyleNestedDeclarations_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleViewTransition_Body {
    const StyleViewTransitionRule *_0;

    bool operator==(const StyleViewTransition_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleStyle_Body style;
    StyleNamespace_Body namespace_;
    StyleImport_Body import;
    StyleMedia_Body media;
    StyleCustomMedia_Body custom_media;
    StyleContainer_Body container;
    StyleFontFace_Body font_face;
    StyleFontFeatureValues_Body font_feature_values;
    StyleFontPaletteValues_Body font_palette_values;
    StyleCounterStyle_Body counter_style;
    StyleKeyframes_Body keyframes;
    StyleMargin_Body margin;
    StyleSupports_Body supports;
    StylePage_Body page;
    StyleProperty_Body property;
    StyleDocument_Body document;
    StyleLayerBlock_Body layer_block;
    StyleLayerStatement_Body layer_statement;
    StyleScope_Body scope;
    StyleStartingStyle_Body starting_style;
    StyleAppearanceBase_Body appearance_base;
    StylePositionTry_Body position_try;
    StyleNestedDeclarations_Body nested_declarations;
    StyleViewTransition_Body view_transition;
  };

  static StyleCssRuleRef Style(const StyleLockedStyleRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.style._0) (const StyleLockedStyleRule*)(_0);
    result.tag = Tag::Style;
    return result;
  }

  bool IsStyle() const {
    return tag == Tag::Style;
  }

  const StyleLockedStyleRule*const & AsStyle() const {
    MOZ_DIAGNOSTIC_ASSERT(IsStyle());
    return style._0;
  }

  static StyleCssRuleRef Namespace(const StyleNamespaceRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.namespace_._0) (const StyleNamespaceRule*)(_0);
    result.tag = Tag::Namespace;
    return result;
  }

  bool IsNamespace() const {
    return tag == Tag::Namespace;
  }

  const StyleNamespaceRule*const & AsNamespace() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNamespace());
    return namespace_._0;
  }

  static StyleCssRuleRef Import(const StyleLockedImportRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.import._0) (const StyleLockedImportRule*)(_0);
    result.tag = Tag::Import;
    return result;
  }

  bool IsImport() const {
    return tag == Tag::Import;
  }

  const StyleLockedImportRule*const & AsImport() const {
    MOZ_DIAGNOSTIC_ASSERT(IsImport());
    return import._0;
  }

  static StyleCssRuleRef Media(const StyleMediaRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.media._0) (const StyleMediaRule*)(_0);
    result.tag = Tag::Media;
    return result;
  }

  bool IsMedia() const {
    return tag == Tag::Media;
  }

  const StyleMediaRule*const & AsMedia() const {
    MOZ_DIAGNOSTIC_ASSERT(IsMedia());
    return media._0;
  }

  static StyleCssRuleRef CustomMedia(const StyleCustomMediaRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.custom_media._0) (const StyleCustomMediaRule*)(_0);
    result.tag = Tag::CustomMedia;
    return result;
  }

  bool IsCustomMedia() const {
    return tag == Tag::CustomMedia;
  }

  const StyleCustomMediaRule*const & AsCustomMedia() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCustomMedia());
    return custom_media._0;
  }

  static StyleCssRuleRef Container(const StyleContainerRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.container._0) (const StyleContainerRule*)(_0);
    result.tag = Tag::Container;
    return result;
  }

  bool IsContainer() const {
    return tag == Tag::Container;
  }

  const StyleContainerRule*const & AsContainer() const {
    MOZ_DIAGNOSTIC_ASSERT(IsContainer());
    return container._0;
  }

  static StyleCssRuleRef FontFace(const StyleLockedFontFaceRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.font_face._0) (const StyleLockedFontFaceRule*)(_0);
    result.tag = Tag::FontFace;
    return result;
  }

  bool IsFontFace() const {
    return tag == Tag::FontFace;
  }

  const StyleLockedFontFaceRule*const & AsFontFace() const {
    MOZ_DIAGNOSTIC_ASSERT(IsFontFace());
    return font_face._0;
  }

  static StyleCssRuleRef FontFeatureValues(const StyleFontFeatureValuesRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.font_feature_values._0) (const StyleFontFeatureValuesRule*)(_0);
    result.tag = Tag::FontFeatureValues;
    return result;
  }

  bool IsFontFeatureValues() const {
    return tag == Tag::FontFeatureValues;
  }

  const StyleFontFeatureValuesRule*const & AsFontFeatureValues() const {
    MOZ_DIAGNOSTIC_ASSERT(IsFontFeatureValues());
    return font_feature_values._0;
  }

  static StyleCssRuleRef FontPaletteValues(const StyleFontPaletteValuesRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.font_palette_values._0) (const StyleFontPaletteValuesRule*)(_0);
    result.tag = Tag::FontPaletteValues;
    return result;
  }

  bool IsFontPaletteValues() const {
    return tag == Tag::FontPaletteValues;
  }

  const StyleFontPaletteValuesRule*const & AsFontPaletteValues() const {
    MOZ_DIAGNOSTIC_ASSERT(IsFontPaletteValues());
    return font_palette_values._0;
  }

  static StyleCssRuleRef CounterStyle(const StyleLockedCounterStyleRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.counter_style._0) (const StyleLockedCounterStyleRule*)(_0);
    result.tag = Tag::CounterStyle;
    return result;
  }

  bool IsCounterStyle() const {
    return tag == Tag::CounterStyle;
  }

  const StyleLockedCounterStyleRule*const & AsCounterStyle() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCounterStyle());
    return counter_style._0;
  }

  static StyleCssRuleRef Keyframes(const StyleLockedKeyframesRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.keyframes._0) (const StyleLockedKeyframesRule*)(_0);
    result.tag = Tag::Keyframes;
    return result;
  }

  bool IsKeyframes() const {
    return tag == Tag::Keyframes;
  }

  const StyleLockedKeyframesRule*const & AsKeyframes() const {
    MOZ_DIAGNOSTIC_ASSERT(IsKeyframes());
    return keyframes._0;
  }

  static StyleCssRuleRef Margin(const StyleMarginRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.margin._0) (const StyleMarginRule*)(_0);
    result.tag = Tag::Margin;
    return result;
  }

  bool IsMargin() const {
    return tag == Tag::Margin;
  }

  const StyleMarginRule*const & AsMargin() const {
    MOZ_DIAGNOSTIC_ASSERT(IsMargin());
    return margin._0;
  }

  static StyleCssRuleRef Supports(const StyleSupportsRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.supports._0) (const StyleSupportsRule*)(_0);
    result.tag = Tag::Supports;
    return result;
  }

  bool IsSupports() const {
    return tag == Tag::Supports;
  }

  const StyleSupportsRule*const & AsSupports() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSupports());
    return supports._0;
  }

  static StyleCssRuleRef Page(const StyleLockedPageRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.page._0) (const StyleLockedPageRule*)(_0);
    result.tag = Tag::Page;
    return result;
  }

  bool IsPage() const {
    return tag == Tag::Page;
  }

  const StyleLockedPageRule*const & AsPage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPage());
    return page._0;
  }

  static StyleCssRuleRef Property(const StylePropertyRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.property._0) (const StylePropertyRule*)(_0);
    result.tag = Tag::Property;
    return result;
  }

  bool IsProperty() const {
    return tag == Tag::Property;
  }

  const StylePropertyRule*const & AsProperty() const {
    MOZ_DIAGNOSTIC_ASSERT(IsProperty());
    return property._0;
  }

  static StyleCssRuleRef Document(const StyleDocumentRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.document._0) (const StyleDocumentRule*)(_0);
    result.tag = Tag::Document;
    return result;
  }

  bool IsDocument() const {
    return tag == Tag::Document;
  }

  const StyleDocumentRule*const & AsDocument() const {
    MOZ_DIAGNOSTIC_ASSERT(IsDocument());
    return document._0;
  }

  static StyleCssRuleRef LayerBlock(const StyleLayerBlockRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.layer_block._0) (const StyleLayerBlockRule*)(_0);
    result.tag = Tag::LayerBlock;
    return result;
  }

  bool IsLayerBlock() const {
    return tag == Tag::LayerBlock;
  }

  const StyleLayerBlockRule*const & AsLayerBlock() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLayerBlock());
    return layer_block._0;
  }

  static StyleCssRuleRef LayerStatement(const StyleLayerStatementRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.layer_statement._0) (const StyleLayerStatementRule*)(_0);
    result.tag = Tag::LayerStatement;
    return result;
  }

  bool IsLayerStatement() const {
    return tag == Tag::LayerStatement;
  }

  const StyleLayerStatementRule*const & AsLayerStatement() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLayerStatement());
    return layer_statement._0;
  }

  static StyleCssRuleRef Scope(const StyleScopeRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.scope._0) (const StyleScopeRule*)(_0);
    result.tag = Tag::Scope;
    return result;
  }

  bool IsScope() const {
    return tag == Tag::Scope;
  }

  const StyleScopeRule*const & AsScope() const {
    MOZ_DIAGNOSTIC_ASSERT(IsScope());
    return scope._0;
  }

  static StyleCssRuleRef StartingStyle(const StyleStartingStyleRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.starting_style._0) (const StyleStartingStyleRule*)(_0);
    result.tag = Tag::StartingStyle;
    return result;
  }

  bool IsStartingStyle() const {
    return tag == Tag::StartingStyle;
  }

  const StyleStartingStyleRule*const & AsStartingStyle() const {
    MOZ_DIAGNOSTIC_ASSERT(IsStartingStyle());
    return starting_style._0;
  }

  static StyleCssRuleRef AppearanceBase(const StyleAppearanceBaseRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.appearance_base._0) (const StyleAppearanceBaseRule*)(_0);
    result.tag = Tag::AppearanceBase;
    return result;
  }

  bool IsAppearanceBase() const {
    return tag == Tag::AppearanceBase;
  }

  const StyleAppearanceBaseRule*const & AsAppearanceBase() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAppearanceBase());
    return appearance_base._0;
  }

  static StyleCssRuleRef PositionTry(const StyleLockedPositionTryRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.position_try._0) (const StyleLockedPositionTryRule*)(_0);
    result.tag = Tag::PositionTry;
    return result;
  }

  bool IsPositionTry() const {
    return tag == Tag::PositionTry;
  }

  const StyleLockedPositionTryRule*const & AsPositionTry() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPositionTry());
    return position_try._0;
  }

  static StyleCssRuleRef NestedDeclarations(const StyleLockedNestedDeclarationsRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.nested_declarations._0) (const StyleLockedNestedDeclarationsRule*)(_0);
    result.tag = Tag::NestedDeclarations;
    return result;
  }

  bool IsNestedDeclarations() const {
    return tag == Tag::NestedDeclarations;
  }

  const StyleLockedNestedDeclarationsRule*const & AsNestedDeclarations() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNestedDeclarations());
    return nested_declarations._0;
  }

  static StyleCssRuleRef ViewTransition(const StyleViewTransitionRule *const &_0) {
    StyleCssRuleRef result;
    ::new (&result.view_transition._0) (const StyleViewTransitionRule*)(_0);
    result.tag = Tag::ViewTransition;
    return result;
  }

  bool IsViewTransition() const {
    return tag == Tag::ViewTransition;
  }

  const StyleViewTransitionRule*const & AsViewTransition() const {
    MOZ_DIAGNOSTIC_ASSERT(IsViewTransition());
    return view_transition._0;
  }

  bool operator==(const StyleCssRuleRef& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Style: return style == other.style;
      case Tag::Namespace: return namespace_ == other.namespace_;
      case Tag::Import: return import == other.import;
      case Tag::Media: return media == other.media;
      case Tag::CustomMedia: return custom_media == other.custom_media;
      case Tag::Container: return container == other.container;
      case Tag::FontFace: return font_face == other.font_face;
      case Tag::FontFeatureValues: return font_feature_values == other.font_feature_values;
      case Tag::FontPaletteValues: return font_palette_values == other.font_palette_values;
      case Tag::CounterStyle: return counter_style == other.counter_style;
      case Tag::Keyframes: return keyframes == other.keyframes;
      case Tag::Margin: return margin == other.margin;
      case Tag::Supports: return supports == other.supports;
      case Tag::Page: return page == other.page;
      case Tag::Property: return property == other.property;
      case Tag::Document: return document == other.document;
      case Tag::LayerBlock: return layer_block == other.layer_block;
      case Tag::LayerStatement: return layer_statement == other.layer_statement;
      case Tag::Scope: return scope == other.scope;
      case Tag::StartingStyle: return starting_style == other.starting_style;
      case Tag::AppearanceBase: return appearance_base == other.appearance_base;
      case Tag::PositionTry: return position_try == other.position_try;
      case Tag::NestedDeclarations: return nested_declarations == other.nested_declarations;
      case Tag::ViewTransition: return view_transition == other.view_transition;

    }
    return true;
  }

  private:
  StyleCssRuleRef() {

  }
  public:


  ~StyleCssRuleRef() {
    switch (tag) {
      case Tag::Style: style.~StyleStyle_Body(); break;
      case Tag::Namespace: namespace_.~StyleNamespace_Body(); break;
      case Tag::Import: import.~StyleImport_Body(); break;
      case Tag::Media: media.~StyleMedia_Body(); break;
      case Tag::CustomMedia: custom_media.~StyleCustomMedia_Body(); break;
      case Tag::Container: container.~StyleContainer_Body(); break;
      case Tag::FontFace: font_face.~StyleFontFace_Body(); break;
      case Tag::FontFeatureValues: font_feature_values.~StyleFontFeatureValues_Body(); break;
      case Tag::FontPaletteValues: font_palette_values.~StyleFontPaletteValues_Body(); break;
      case Tag::CounterStyle: counter_style.~StyleCounterStyle_Body(); break;
      case Tag::Keyframes: keyframes.~StyleKeyframes_Body(); break;
      case Tag::Margin: margin.~StyleMargin_Body(); break;
      case Tag::Supports: supports.~StyleSupports_Body(); break;
      case Tag::Page: page.~StylePage_Body(); break;
      case Tag::Property: property.~StyleProperty_Body(); break;
      case Tag::Document: document.~StyleDocument_Body(); break;
      case Tag::LayerBlock: layer_block.~StyleLayerBlock_Body(); break;
      case Tag::LayerStatement: layer_statement.~StyleLayerStatement_Body(); break;
      case Tag::Scope: scope.~StyleScope_Body(); break;
      case Tag::StartingStyle: starting_style.~StyleStartingStyle_Body(); break;
      case Tag::AppearanceBase: appearance_base.~StyleAppearanceBase_Body(); break;
      case Tag::PositionTry: position_try.~StylePositionTry_Body(); break;
      case Tag::NestedDeclarations: nested_declarations.~StyleNestedDeclarations_Body(); break;
      case Tag::ViewTransition: view_transition.~StyleViewTransition_Body(); break;

    }
  }

  StyleCssRuleRef(const StyleCssRuleRef& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Style: ::new (&style) (StyleStyle_Body)(other.style); break;
      case Tag::Namespace: ::new (&namespace_) (StyleNamespace_Body)(other.namespace_); break;
      case Tag::Import: ::new (&import) (StyleImport_Body)(other.import); break;
      case Tag::Media: ::new (&media) (StyleMedia_Body)(other.media); break;
      case Tag::CustomMedia: ::new (&custom_media) (StyleCustomMedia_Body)(other.custom_media); break;
      case Tag::Container: ::new (&container) (StyleContainer_Body)(other.container); break;
      case Tag::FontFace: ::new (&font_face) (StyleFontFace_Body)(other.font_face); break;
      case Tag::FontFeatureValues: ::new (&font_feature_values) (StyleFontFeatureValues_Body)(other.font_feature_values); break;
      case Tag::FontPaletteValues: ::new (&font_palette_values) (StyleFontPaletteValues_Body)(other.font_palette_values); break;
      case Tag::CounterStyle: ::new (&counter_style) (StyleCounterStyle_Body)(other.counter_style); break;
      case Tag::Keyframes: ::new (&keyframes) (StyleKeyframes_Body)(other.keyframes); break;
      case Tag::Margin: ::new (&margin) (StyleMargin_Body)(other.margin); break;
      case Tag::Supports: ::new (&supports) (StyleSupports_Body)(other.supports); break;
      case Tag::Page: ::new (&page) (StylePage_Body)(other.page); break;
      case Tag::Property: ::new (&property) (StyleProperty_Body)(other.property); break;
      case Tag::Document: ::new (&document) (StyleDocument_Body)(other.document); break;
      case Tag::LayerBlock: ::new (&layer_block) (StyleLayerBlock_Body)(other.layer_block); break;
      case Tag::LayerStatement: ::new (&layer_statement) (StyleLayerStatement_Body)(other.layer_statement); break;
      case Tag::Scope: ::new (&scope) (StyleScope_Body)(other.scope); break;
      case Tag::StartingStyle: ::new (&starting_style) (StyleStartingStyle_Body)(other.starting_style); break;
      case Tag::AppearanceBase: ::new (&appearance_base) (StyleAppearanceBase_Body)(other.appearance_base); break;
      case Tag::PositionTry: ::new (&position_try) (StylePositionTry_Body)(other.position_try); break;
      case Tag::NestedDeclarations: ::new (&nested_declarations) (StyleNestedDeclarations_Body)(other.nested_declarations); break;
      case Tag::ViewTransition: ::new (&view_transition) (StyleViewTransition_Body)(other.view_transition); break;

    }
  }
  StyleCssRuleRef& operator=(const StyleCssRuleRef& other) {
    if (this != &other) {
      this->~StyleCssRuleRef();
      new (this) StyleCssRuleRef(other);
    }
    return *this;
  }
};

/// A generic `<length>` | `<number>` value for the `tab-size` property.
template<typename L, typename N>
struct StyleGenericLengthOrNumber {
  enum class Tag : uint8_t {
    /// A number.
    ///
    /// NOTE: Numbers need to be before lengths, in order to parse them
    /// first, since `0` should be a number, not the `0px` length.
    Number,
    /// A length.
    Length,
  };

  struct StyleNumber_Body {
    N _0;

    bool operator==(const StyleNumber_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleLength_Body {
    L _0;

    bool operator==(const StyleLength_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleNumber_Body number;
    StyleLength_Body length;
  };

  static StyleGenericLengthOrNumber Number(const N &_0) {
    StyleGenericLengthOrNumber result;
    ::new (&result.number._0) (N)(_0);
    result.tag = Tag::Number;
    return result;
  }

  bool IsNumber() const {
    return tag == Tag::Number;
  }

  const N& AsNumber() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNumber());
    return number._0;
  }

  static StyleGenericLengthOrNumber Length(const L &_0) {
    StyleGenericLengthOrNumber result;
    ::new (&result.length._0) (L)(_0);
    result.tag = Tag::Length;
    return result;
  }

  bool IsLength() const {
    return tag == Tag::Length;
  }

  const L& AsLength() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLength());
    return length._0;
  }

  bool operator==(const StyleGenericLengthOrNumber& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Number: return number == other.number;
      case Tag::Length: return length == other.length;

    }
    return true;
  }

  private:
  StyleGenericLengthOrNumber() {

  }
  public:


  ~StyleGenericLengthOrNumber() {
    switch (tag) {
      case Tag::Number: number.~StyleNumber_Body(); break;
      case Tag::Length: length.~StyleLength_Body(); break;

    }
  }

  StyleGenericLengthOrNumber(const StyleGenericLengthOrNumber& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Number: ::new (&number) (StyleNumber_Body)(other.number); break;
      case Tag::Length: ::new (&length) (StyleLength_Body)(other.length); break;

    }
  }
  StyleGenericLengthOrNumber& operator=(const StyleGenericLengthOrNumber& other) {
    if (this != &other) {
      this->~StyleGenericLengthOrNumber();
      new (this) StyleGenericLengthOrNumber(other);
    }
    return *this;
  }
};

/// Either a non-negative `<length>` or a `<number>`.
using StyleNonNegativeLengthOrNumber = StyleGenericLengthOrNumber<StyleNonNegativeLength, StyleNonNegativeNumber>;

/// A specified rectangle made of four `<length-or-number>` values.
using StyleNonNegativeLengthOrNumberRect = StyleRect<StyleNonNegativeLengthOrNumber>;

/// A generic value for the `perspective` property.
template<typename NonNegativeLength>
struct StyleGenericPerspective {
  enum class Tag : uint8_t {
    /// A non-negative length.
    Length,
    /// The keyword `none`.
    None,
  };

  struct StyleLength_Body {
    NonNegativeLength _0;

    bool operator==(const StyleLength_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleLength_Body length;
  };

  static StyleGenericPerspective Length(const NonNegativeLength &_0) {
    StyleGenericPerspective result;
    ::new (&result.length._0) (NonNegativeLength)(_0);
    result.tag = Tag::Length;
    return result;
  }

  bool IsLength() const {
    return tag == Tag::Length;
  }

  const NonNegativeLength& AsLength() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLength());
    return length._0;
  }

  static StyleGenericPerspective None() {
    StyleGenericPerspective result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  bool operator==(const StyleGenericPerspective& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Length: return length == other.length;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericPerspective() {

  }
  public:


  ~StyleGenericPerspective() {
    switch (tag) {
      case Tag::Length: length.~StyleLength_Body(); break;
      default: break;
    }
  }

  StyleGenericPerspective(const StyleGenericPerspective& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Length: ::new (&length) (StyleLength_Body)(other.length); break;
      default: break;
    }
  }
  StyleGenericPerspective& operator=(const StyleGenericPerspective& other) {
    if (this != &other) {
      this->~StyleGenericPerspective();
      new (this) StyleGenericPerspective(other);
    }
    return *this;
  }
};

/// A computed value for the `perspective` property.
using StylePerspective = StyleGenericPerspective<StyleNonNegativeLength>;

/// A generic value for the `z-index` property.
template<typename I>
struct StyleGenericZIndex {
  enum class Tag : uint8_t {
    /// An integer value.
    Integer,
    /// The keyword `auto`.
    Auto,
  };

  struct StyleInteger_Body {
    I _0;

    bool operator==(const StyleInteger_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleInteger_Body integer;
  };

  static StyleGenericZIndex Integer(const I &_0) {
    StyleGenericZIndex result;
    ::new (&result.integer._0) (I)(_0);
    result.tag = Tag::Integer;
    return result;
  }

  bool IsInteger() const {
    return tag == Tag::Integer;
  }

  const I& AsInteger() const {
    MOZ_DIAGNOSTIC_ASSERT(IsInteger());
    return integer._0;
  }

  static StyleGenericZIndex Auto() {
    StyleGenericZIndex result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  bool operator==(const StyleGenericZIndex& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Integer: return integer == other.integer;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericZIndex() {

  }
  public:


  ~StyleGenericZIndex() {
    switch (tag) {
      case Tag::Integer: integer.~StyleInteger_Body(); break;
      default: break;
    }
  }

  StyleGenericZIndex(const StyleGenericZIndex& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Integer: ::new (&integer) (StyleInteger_Body)(other.integer); break;
      default: break;
    }
  }
  StyleGenericZIndex& operator=(const StyleGenericZIndex& other) {
    if (this != &other) {
      this->~StyleGenericZIndex();
      new (this) StyleGenericZIndex(other);
    }
    return *this;
  }
};

/// A computed value for the `z-index` property.
using StyleZIndex = StyleGenericZIndex<StyleInteger>;

/// A generic transform origin.
template<typename H, typename V, typename Depth>
struct StyleGenericTransformOrigin {
  /// The horizontal origin.
  H horizontal;
  /// The vertical origin.
  V vertical;
  /// The depth.
  Depth depth;

  bool operator==(const StyleGenericTransformOrigin& other) const {
    return horizontal == other.horizontal &&
           vertical == other.vertical &&
           depth == other.depth;
  }
  inline bool HasPercent() const;
};

/// The computed value of a CSS `<transform-origin>`
using StyleTransformOrigin = StyleGenericTransformOrigin<StyleLengthPercentage, StyleLengthPercentage, StyleLength>;

/// A generic value for the maximum lines used by `line-clamp`.
/// <https://drafts.csswg.org/css-overflow-4/#propdef-max-lines>
template<typename I>
struct StyleGenericMaxLines {
  /// The maximum number of lines.
  StyleOptional<I> lines;
  /// Whether block-size clamping is applied.
  StyleMaxLinesKeyword kw;

  bool operator==(const StyleGenericMaxLines& other) const {
    return lines == other.lines &&
           kw == other.kw;
  }
};

/// A block ellipsis for line clamping.
struct StyleBlockEllipsis {
  enum class Tag : uint8_t {
    /// Display the ellipsis character.
    Ellipsis,
    /// Do not display an ellipsis.
    NoEllipsis,
    /// Display the given string.
    String,
  };

  struct StyleString_Body {
    StyleAtomString _0;

    bool operator==(const StyleString_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleString_Body string;
  };

  static StyleBlockEllipsis Ellipsis() {
    StyleBlockEllipsis result;
    result.tag = Tag::Ellipsis;
    return result;
  }

  bool IsEllipsis() const {
    return tag == Tag::Ellipsis;
  }

  static StyleBlockEllipsis NoEllipsis() {
    StyleBlockEllipsis result;
    result.tag = Tag::NoEllipsis;
    return result;
  }

  bool IsNoEllipsis() const {
    return tag == Tag::NoEllipsis;
  }

  static StyleBlockEllipsis String(const StyleAtomString &_0) {
    StyleBlockEllipsis result;
    ::new (&result.string._0) (StyleAtomString)(_0);
    result.tag = Tag::String;
    return result;
  }

  bool IsString() const {
    return tag == Tag::String;
  }

  const StyleAtomString& AsString() const {
    MOZ_DIAGNOSTIC_ASSERT(IsString());
    return string._0;
  }

  bool operator==(const StyleBlockEllipsis& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::String: return string == other.string;
      default: break;
    }
    return true;
  }

  private:
  StyleBlockEllipsis() {

  }
  public:


  ~StyleBlockEllipsis() {
    switch (tag) {
      case Tag::String: string.~StyleString_Body(); break;
      default: break;
    }
  }

  StyleBlockEllipsis(const StyleBlockEllipsis& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::String: ::new (&string) (StyleString_Body)(other.string); break;
      default: break;
    }
  }
  StyleBlockEllipsis& operator=(const StyleBlockEllipsis& other) {
    if (this != &other) {
      this->~StyleBlockEllipsis();
      new (this) StyleBlockEllipsis(other);
    }
    return *this;
  }
};

/// A generic value for the `line-clamp` property.
template<typename I>
struct StyleGenericLineClamp {
  /// Maximum `line-count` and `block-size` clamping behavior.
  StyleGenericMaxLines<I> max_lines;
  /// Ellipsis displayed at the clamp point.
  StyleBlockEllipsis block_ellipsis;
  /// Whether legacy line clamping behavior is used.
  bool webkit_legacy;

  bool operator==(const StyleGenericLineClamp& other) const {
    return max_lines == other.max_lines &&
           block_ellipsis == other.block_ellipsis &&
           webkit_legacy == other.webkit_legacy;
  }
};

/// A computed value for the `line-clamp` property.
using StyleLineClamp = StyleGenericLineClamp<StyleGreaterThanOrEqualToOne<StyleInteger>>;

/// Constants for contain: https://drafts.csswg.org/css-contain/#contain-property
struct StyleContain {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleContain operator~() const {
    return StyleContain { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleContain operator|(const StyleContain& other) const {
    return StyleContain { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleContain& operator|=(const StyleContain& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleContain operator&(const StyleContain& other) const {
    return StyleContain { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleContain& operator&=(const StyleContain& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleContain operator^(const StyleContain& other) const {
    return StyleContain { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleContain& operator^=(const StyleContain& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleContain& other) const {
    return _0 == other._0;
  }
  static const StyleContain NONE;
  static const StyleContain INLINE_SIZE;
  static const StyleContain BLOCK_SIZE;
  static const StyleContain LAYOUT;
  static const StyleContain STYLE;
  static const StyleContain PAINT;
  static const StyleContain SIZE;
  static const StyleContain CONTENT;
  static const StyleContain STRICT;
};
/// `none` variant, just for convenience.
constexpr inline const StyleContain StyleContain::NONE = StyleContain{
  /* ._0 = */ (uint8_t)0
};
/// `inline-size` variant, turns on single-axis inline size containment
constexpr inline const StyleContain StyleContain::INLINE_SIZE = StyleContain{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// `block-size` variant, turns on single-axis block size containment, internal only
constexpr inline const StyleContain StyleContain::BLOCK_SIZE = StyleContain{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// `layout` variant, turns on layout containment
constexpr inline const StyleContain StyleContain::LAYOUT = StyleContain{
  /* ._0 = */ (uint8_t)(1 << 2)
};
/// `style` variant, turns on style containment
constexpr inline const StyleContain StyleContain::STYLE = StyleContain{
  /* ._0 = */ (uint8_t)(1 << 3)
};
/// `paint` variant, turns on paint containment
constexpr inline const StyleContain StyleContain::PAINT = StyleContain{
  /* ._0 = */ (uint8_t)(1 << 4)
};
/// 'size' variant, turns on size containment
constexpr inline const StyleContain StyleContain::SIZE = StyleContain{
  /* ._0 = */ (uint8_t)(((1 << 5) | (StyleContain::INLINE_SIZE)._0) | (StyleContain::BLOCK_SIZE)._0)
};
/// `content` variant, turns on layout and paint containment
constexpr inline const StyleContain StyleContain::CONTENT = StyleContain{
  /* ._0 = */ (uint8_t)((((1 << 6) | (StyleContain::LAYOUT)._0) | (StyleContain::STYLE)._0) | (StyleContain::PAINT)._0)
};
/// `strict` variant, turns on all types of containment
constexpr inline const StyleContain StyleContain::STRICT = StyleContain{
  /* ._0 = */ (uint8_t)(((((1 << 7) | (StyleContain::LAYOUT)._0) | (StyleContain::STYLE)._0) | (StyleContain::PAINT)._0) | (StyleContain::SIZE)._0)
};

/// Specified value of the `margin-trim` property, which trims the margins of a
/// container's children where they meet the container's edges.
/// https://drafts.csswg.org/css-box-4/#propdef-margin-trim
/// Pending https://github.com/w3c/csswg-drafts/issues/13731, we're only targetting block
/// trimming for now and skipping `inline-start` and `inline-end`
struct StyleMarginTrim {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleMarginTrim operator~() const {
    return StyleMarginTrim { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleMarginTrim operator|(const StyleMarginTrim& other) const {
    return StyleMarginTrim { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleMarginTrim& operator|=(const StyleMarginTrim& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleMarginTrim operator&(const StyleMarginTrim& other) const {
    return StyleMarginTrim { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleMarginTrim& operator&=(const StyleMarginTrim& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleMarginTrim operator^(const StyleMarginTrim& other) const {
    return StyleMarginTrim { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleMarginTrim& operator^=(const StyleMarginTrim& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleMarginTrim& other) const {
    return _0 == other._0;
  }
  static const StyleMarginTrim NONE;
  static const StyleMarginTrim BLOCK_START;
  static const StyleMarginTrim BLOCK_END;
  static const StyleMarginTrim BLOCK;
};
/// `none` variant, no margins are trimmed.
constexpr inline const StyleMarginTrim StyleMarginTrim::NONE = StyleMarginTrim{
  /* ._0 = */ (uint8_t)0
};
/// Trim the block-start margin of the first child.
constexpr inline const StyleMarginTrim StyleMarginTrim::BLOCK_START = StyleMarginTrim{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// Trim the block-end margin of the last child.
constexpr inline const StyleMarginTrim StyleMarginTrim::BLOCK_END = StyleMarginTrim{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// `block` shorthand: both block-axis margins.
constexpr inline const StyleMarginTrim StyleMarginTrim::BLOCK = StyleMarginTrim{
  /* ._0 = */ (uint8_t)((StyleMarginTrim::BLOCK_START)._0 | (StyleMarginTrim::BLOCK_END)._0)
};

/// Specified keyword values for the container-type property.
/// Spec: normal | [ [ size | inline-size ] || scroll-state ]
///
/// Container Queries are moved from css-contain-3 to css-conditional-5 in August 2022:
/// https://drafts.csswg.org/css-contain-3/#container-type
/// https://drafts.csswg.org/css-conditional-5/#container-type
struct StyleContainerType {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleContainerType operator~() const {
    return StyleContainerType { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleContainerType operator|(const StyleContainerType& other) const {
    return StyleContainerType { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleContainerType& operator|=(const StyleContainerType& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleContainerType operator&(const StyleContainerType& other) const {
    return StyleContainerType { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleContainerType& operator&=(const StyleContainerType& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleContainerType operator^(const StyleContainerType& other) const {
    return StyleContainerType { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleContainerType& operator^=(const StyleContainerType& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleContainerType& other) const {
    return _0 == other._0;
  }
  static const StyleContainerType NORMAL;
  static const StyleContainerType INLINE_SIZE;
  static const StyleContainerType SIZE;
  static const StyleContainerType SCROLL_STATE;
};
/// The `normal` variant.
constexpr inline const StyleContainerType StyleContainerType::NORMAL = StyleContainerType{
  /* ._0 = */ (uint8_t)0
};
/// The `inline-size` variant.
constexpr inline const StyleContainerType StyleContainerType::INLINE_SIZE = StyleContainerType{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// The `size` variant.
constexpr inline const StyleContainerType StyleContainerType::SIZE = StyleContainerType{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// The `scroll-state` variant.
constexpr inline const StyleContainerType StyleContainerType::SCROLL_STATE = StyleContainerType{
  /* ._0 = */ (uint8_t)(1 << 2)
};

/// https://drafts.csswg.org/css-contain-3/#container-name
using StyleContainerName = StyleOwnedSlice<StyleCustomIdent>;

/// https://drafts.csswg.org/css-sizing-4/#intrinsic-size-override
template<typename L>
struct StyleGenericContainIntrinsicSize {
  enum class Tag : uint8_t {
    /// The keyword `none`.
    None,
    /// The keywords 'auto none',
    AutoNone,
    /// A non-negative length.
    Length,
    /// "auto <Length>"
    AutoLength,
  };

  struct StyleLength_Body {
    L _0;

    bool operator==(const StyleLength_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAutoLength_Body {
    L _0;

    bool operator==(const StyleAutoLength_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleLength_Body length;
    StyleAutoLength_Body auto_length;
  };

  static StyleGenericContainIntrinsicSize None() {
    StyleGenericContainIntrinsicSize result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericContainIntrinsicSize AutoNone() {
    StyleGenericContainIntrinsicSize result;
    result.tag = Tag::AutoNone;
    return result;
  }

  bool IsAutoNone() const {
    return tag == Tag::AutoNone;
  }

  static StyleGenericContainIntrinsicSize Length(const L &_0) {
    StyleGenericContainIntrinsicSize result;
    ::new (&result.length._0) (L)(_0);
    result.tag = Tag::Length;
    return result;
  }

  bool IsLength() const {
    return tag == Tag::Length;
  }

  const L& AsLength() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLength());
    return length._0;
  }

  static StyleGenericContainIntrinsicSize AutoLength(const L &_0) {
    StyleGenericContainIntrinsicSize result;
    ::new (&result.auto_length._0) (L)(_0);
    result.tag = Tag::AutoLength;
    return result;
  }

  bool IsAutoLength() const {
    return tag == Tag::AutoLength;
  }

  const L& AsAutoLength() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAutoLength());
    return auto_length._0;
  }

  bool operator==(const StyleGenericContainIntrinsicSize& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Length: return length == other.length;
      case Tag::AutoLength: return auto_length == other.auto_length;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericContainIntrinsicSize() {

  }
  public:


  ~StyleGenericContainIntrinsicSize() {
    switch (tag) {
      case Tag::Length: length.~StyleLength_Body(); break;
      case Tag::AutoLength: auto_length.~StyleAutoLength_Body(); break;
      default: break;
    }
  }

  StyleGenericContainIntrinsicSize(const StyleGenericContainIntrinsicSize& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Length: ::new (&length) (StyleLength_Body)(other.length); break;
      case Tag::AutoLength: ::new (&auto_length) (StyleAutoLength_Body)(other.auto_length); break;
      default: break;
    }
  }
  StyleGenericContainIntrinsicSize& operator=(const StyleGenericContainIntrinsicSize& other) {
    if (this != &other) {
      this->~StyleGenericContainIntrinsicSize();
      new (this) StyleGenericContainIntrinsicSize(other);
    }
    return *this;
  }
  bool HasAuto() const { return IsAutoLength() || IsAutoNone(); }
};

/// A computed value for the `contain-intrinsic-size` property.
using StyleContainIntrinsicSize = StyleGenericContainIntrinsicSize<StyleNonNegativeLength>;

/// Values for the `touch-action` property.
struct StyleTouchAction {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleTouchAction operator~() const {
    return StyleTouchAction { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleTouchAction operator|(const StyleTouchAction& other) const {
    return StyleTouchAction { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleTouchAction& operator|=(const StyleTouchAction& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleTouchAction operator&(const StyleTouchAction& other) const {
    return StyleTouchAction { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleTouchAction& operator&=(const StyleTouchAction& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleTouchAction operator^(const StyleTouchAction& other) const {
    return StyleTouchAction { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleTouchAction& operator^=(const StyleTouchAction& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleTouchAction& other) const {
    return _0 == other._0;
  }
  static const StyleTouchAction NONE;
  static const StyleTouchAction AUTO;
  static const StyleTouchAction PAN_X;
  static const StyleTouchAction PAN_Y;
  static const StyleTouchAction MANIPULATION;
  static const StyleTouchAction PINCH_ZOOM;
};
/// `none` variant
constexpr inline const StyleTouchAction StyleTouchAction::NONE = StyleTouchAction{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// `auto` variant
constexpr inline const StyleTouchAction StyleTouchAction::AUTO = StyleTouchAction{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// `pan-x` variant
constexpr inline const StyleTouchAction StyleTouchAction::PAN_X = StyleTouchAction{
  /* ._0 = */ (uint8_t)(1 << 2)
};
/// `pan-y` variant
constexpr inline const StyleTouchAction StyleTouchAction::PAN_Y = StyleTouchAction{
  /* ._0 = */ (uint8_t)(1 << 3)
};
/// `manipulation` variant
constexpr inline const StyleTouchAction StyleTouchAction::MANIPULATION = StyleTouchAction{
  /* ._0 = */ (uint8_t)(1 << 4)
};
/// `pinch-zoom` variant
constexpr inline const StyleTouchAction StyleTouchAction::PINCH_ZOOM = StyleTouchAction{
  /* ._0 = */ (uint8_t)(1 << 5)
};

/// The change bits that we care about.
struct StyleWillChangeBits {
  uint16_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleWillChangeBits operator~() const {
    return StyleWillChangeBits { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleWillChangeBits operator|(const StyleWillChangeBits& other) const {
    return StyleWillChangeBits { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleWillChangeBits& operator|=(const StyleWillChangeBits& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleWillChangeBits operator&(const StyleWillChangeBits& other) const {
    return StyleWillChangeBits { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleWillChangeBits& operator&=(const StyleWillChangeBits& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleWillChangeBits operator^(const StyleWillChangeBits& other) const {
    return StyleWillChangeBits { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleWillChangeBits& operator^=(const StyleWillChangeBits& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleWillChangeBits& other) const {
    return _0 == other._0;
  }
  static const StyleWillChangeBits STACKING_CONTEXT_UNCONDITIONAL;
  static const StyleWillChangeBits TRANSFORM;
  static const StyleWillChangeBits SCROLL;
  static const StyleWillChangeBits CONTAIN;
  static const StyleWillChangeBits OPACITY;
  static const StyleWillChangeBits PERSPECTIVE;
  static const StyleWillChangeBits Z_INDEX;
  static const StyleWillChangeBits FIXPOS_CB_NON_SVG;
  static const StyleWillChangeBits POSITION;
  static const StyleWillChangeBits VIEW_TRANSITION_NAME;
  static const StyleWillChangeBits BACKDROP_ROOT;
};
/// Whether a property which can create a stacking context **on any
/// box** will change.
constexpr inline const StyleWillChangeBits StyleWillChangeBits::STACKING_CONTEXT_UNCONDITIONAL = StyleWillChangeBits{
  /* ._0 = */ (uint16_t)(1 << 0)
};
/// Whether `transform` or related properties will change.
constexpr inline const StyleWillChangeBits StyleWillChangeBits::TRANSFORM = StyleWillChangeBits{
  /* ._0 = */ (uint16_t)(1 << 1)
};
/// Whether `scroll-position` will change.
constexpr inline const StyleWillChangeBits StyleWillChangeBits::SCROLL = StyleWillChangeBits{
  /* ._0 = */ (uint16_t)(1 << 2)
};
/// Whether `contain` will change.
constexpr inline const StyleWillChangeBits StyleWillChangeBits::CONTAIN = StyleWillChangeBits{
  /* ._0 = */ (uint16_t)(1 << 3)
};
/// Whether `opacity` will change.
constexpr inline const StyleWillChangeBits StyleWillChangeBits::OPACITY = StyleWillChangeBits{
  /* ._0 = */ (uint16_t)(1 << 4)
};
/// Whether `perspective` will change.
constexpr inline const StyleWillChangeBits StyleWillChangeBits::PERSPECTIVE = StyleWillChangeBits{
  /* ._0 = */ (uint16_t)(1 << 5)
};
/// Whether `z-index` will change.
constexpr inline const StyleWillChangeBits StyleWillChangeBits::Z_INDEX = StyleWillChangeBits{
  /* ._0 = */ (uint16_t)(1 << 6)
};
/// Whether any property which creates a containing block for non-svg
/// text frames will change.
constexpr inline const StyleWillChangeBits StyleWillChangeBits::FIXPOS_CB_NON_SVG = StyleWillChangeBits{
  /* ._0 = */ (uint16_t)(1 << 7)
};
/// Whether the position property will change.
constexpr inline const StyleWillChangeBits StyleWillChangeBits::POSITION = StyleWillChangeBits{
  /* ._0 = */ (uint16_t)(1 << 8)
};
/// Whether the view-transition-name property will change.
constexpr inline const StyleWillChangeBits StyleWillChangeBits::VIEW_TRANSITION_NAME = StyleWillChangeBits{
  /* ._0 = */ (uint16_t)(1 << 9)
};
/// Whether any property which establishes a backdrop-root will change.
/// See https://drafts.fxtf.org/filter-effects-2/#BackdropFilterProperty
constexpr inline const StyleWillChangeBits StyleWillChangeBits::BACKDROP_ROOT = StyleWillChangeBits{
  /* ._0 = */ (uint16_t)(1 << 10)
};

/// Provides a rendering hint to the user agent, stating what kinds of changes
/// the author expects to perform on the element.
///
/// `auto` is represented by an empty `features` list.
///
/// <https://drafts.csswg.org/css-will-change/#will-change>
struct StyleWillChange {
  /// The features that are supposed to change.
  ///
  /// TODO(emilio): Consider using ArcSlice since we just clone them from the
  /// specified value? That'd save an allocation, which could be worth it.
  StyleOwnedSlice<StyleCustomIdent> features;
  /// A bitfield with the kind of change that the value will create, based
  /// on the above field.
  StyleWillChangeBits bits;

  bool operator==(const StyleWillChange& other) const {
    return features == other.features &&
           bits == other.bits;
  }
};

/// Specified keyword values for the text-decoration-line property.
struct StyleTextDecorationLine {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleTextDecorationLine operator~() const {
    return StyleTextDecorationLine { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleTextDecorationLine operator|(const StyleTextDecorationLine& other) const {
    return StyleTextDecorationLine { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleTextDecorationLine& operator|=(const StyleTextDecorationLine& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleTextDecorationLine operator&(const StyleTextDecorationLine& other) const {
    return StyleTextDecorationLine { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleTextDecorationLine& operator&=(const StyleTextDecorationLine& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleTextDecorationLine operator^(const StyleTextDecorationLine& other) const {
    return StyleTextDecorationLine { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleTextDecorationLine& operator^=(const StyleTextDecorationLine& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleTextDecorationLine& other) const {
    return _0 == other._0;
  }
  static const StyleTextDecorationLine NONE;
  static const StyleTextDecorationLine UNDERLINE;
  static const StyleTextDecorationLine OVERLINE;
  static const StyleTextDecorationLine LINE_THROUGH;
  static const StyleTextDecorationLine BLINK;
  static const StyleTextDecorationLine SPELLING_ERROR;
  static const StyleTextDecorationLine GRAMMAR_ERROR;
#if defined(CBINDGEN_IS_GECKO)
  static const StyleTextDecorationLine COLOR_OVERRIDE;
#endif
  static const StyleTextDecorationLine MIXED_FLAGS;
};
/// No text decoration line is specified.
constexpr inline const StyleTextDecorationLine StyleTextDecorationLine::NONE = StyleTextDecorationLine{
  /* ._0 = */ (uint8_t)0
};
/// underline
constexpr inline const StyleTextDecorationLine StyleTextDecorationLine::UNDERLINE = StyleTextDecorationLine{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// overline
constexpr inline const StyleTextDecorationLine StyleTextDecorationLine::OVERLINE = StyleTextDecorationLine{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// line-through
constexpr inline const StyleTextDecorationLine StyleTextDecorationLine::LINE_THROUGH = StyleTextDecorationLine{
  /* ._0 = */ (uint8_t)(1 << 2)
};
/// blink
constexpr inline const StyleTextDecorationLine StyleTextDecorationLine::BLINK = StyleTextDecorationLine{
  /* ._0 = */ (uint8_t)(1 << 3)
};
/// spelling-error
constexpr inline const StyleTextDecorationLine StyleTextDecorationLine::SPELLING_ERROR = StyleTextDecorationLine{
  /* ._0 = */ (uint8_t)(1 << 4)
};
/// grammar-error
constexpr inline const StyleTextDecorationLine StyleTextDecorationLine::GRAMMAR_ERROR = StyleTextDecorationLine{
  /* ._0 = */ (uint8_t)(1 << 5)
};
#if defined(CBINDGEN_IS_GECKO)
/// Only set by presentation attributes
///
/// Setting this will mean that text-decorations use the color
/// specified by `color` in quirks mode.
///
/// For example, this gives <a href=foo><font color="red">text</font></a>
/// a red text decoration
constexpr inline const StyleTextDecorationLine StyleTextDecorationLine::COLOR_OVERRIDE = StyleTextDecorationLine{
  /* ._0 = */ (uint8_t)(1 << 7)
};
#endif
/// Flags that can be mixed.
constexpr inline const StyleTextDecorationLine StyleTextDecorationLine::MIXED_FLAGS = StyleTextDecorationLine{
  /* ._0 = */ (uint8_t)((((StyleTextDecorationLine::UNDERLINE)._0 | (StyleTextDecorationLine::OVERLINE)._0) | (StyleTextDecorationLine::LINE_THROUGH)._0) | (StyleTextDecorationLine::BLINK)._0)
};

/// Specified keyword values for the text-underline-position property.
/// (Non-exclusive, but not all combinations are allowed: the spec grammar gives
/// `auto | [ from-font | under ] || [ left | right ]`.)
/// https://drafts.csswg.org/css-text-decor-4/#text-underline-position-property
struct StyleTextUnderlinePosition {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleTextUnderlinePosition operator~() const {
    return StyleTextUnderlinePosition { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleTextUnderlinePosition operator|(const StyleTextUnderlinePosition& other) const {
    return StyleTextUnderlinePosition { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleTextUnderlinePosition& operator|=(const StyleTextUnderlinePosition& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleTextUnderlinePosition operator&(const StyleTextUnderlinePosition& other) const {
    return StyleTextUnderlinePosition { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleTextUnderlinePosition& operator&=(const StyleTextUnderlinePosition& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleTextUnderlinePosition operator^(const StyleTextUnderlinePosition& other) const {
    return StyleTextUnderlinePosition { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleTextUnderlinePosition& operator^=(const StyleTextUnderlinePosition& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleTextUnderlinePosition& other) const {
    return _0 == other._0;
  }
  inline bool IsAuto() const;
  inline bool IsFromFont() const;
  inline bool IsUnder() const;
  inline bool IsLeft() const;
  inline bool IsRight() const;
  static const StyleTextUnderlinePosition AUTO;
  static const StyleTextUnderlinePosition FROM_FONT;
  static const StyleTextUnderlinePosition UNDER;
  static const StyleTextUnderlinePosition LEFT;
  static const StyleTextUnderlinePosition RIGHT;
};
/// Use automatic positioning below the alphabetic baseline.
constexpr inline const StyleTextUnderlinePosition StyleTextUnderlinePosition::AUTO = StyleTextUnderlinePosition{
  /* ._0 = */ (uint8_t)0
};
/// Use underline position from the first available font.
constexpr inline const StyleTextUnderlinePosition StyleTextUnderlinePosition::FROM_FONT = StyleTextUnderlinePosition{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// Below the glyph box.
constexpr inline const StyleTextUnderlinePosition StyleTextUnderlinePosition::UNDER = StyleTextUnderlinePosition{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// In vertical mode, place to the left of the text.
constexpr inline const StyleTextUnderlinePosition StyleTextUnderlinePosition::LEFT = StyleTextUnderlinePosition{
  /* ._0 = */ (uint8_t)(1 << 2)
};
/// In vertical mode, place to the right of the text.
constexpr inline const StyleTextUnderlinePosition StyleTextUnderlinePosition::RIGHT = StyleTextUnderlinePosition{
  /* ._0 = */ (uint8_t)(1 << 3)
};

/// A generic value for the `text-overflow` property.
struct StyleTextOverflowSide {
  enum class Tag : uint8_t {
    /// Clip inline content.
    Clip,
    /// Render ellipsis to represent clipped inline content.
    Ellipsis,
    /// Render a given string to represent clipped inline content.
    String,
  };

  struct StyleString_Body {
    StyleAtomString _0;

    bool operator==(const StyleString_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleString_Body string;
  };

  static StyleTextOverflowSide Clip() {
    StyleTextOverflowSide result;
    result.tag = Tag::Clip;
    return result;
  }

  bool IsClip() const {
    return tag == Tag::Clip;
  }

  static StyleTextOverflowSide Ellipsis() {
    StyleTextOverflowSide result;
    result.tag = Tag::Ellipsis;
    return result;
  }

  bool IsEllipsis() const {
    return tag == Tag::Ellipsis;
  }

  static StyleTextOverflowSide String(const StyleAtomString &_0) {
    StyleTextOverflowSide result;
    ::new (&result.string._0) (StyleAtomString)(_0);
    result.tag = Tag::String;
    return result;
  }

  bool IsString() const {
    return tag == Tag::String;
  }

  const StyleAtomString& AsString() const {
    MOZ_DIAGNOSTIC_ASSERT(IsString());
    return string._0;
  }

  bool operator==(const StyleTextOverflowSide& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::String: return string == other.string;
      default: break;
    }
    return true;
  }

  private:
  StyleTextOverflowSide() {

  }
  public:


  ~StyleTextOverflowSide() {
    switch (tag) {
      case Tag::String: string.~StyleString_Body(); break;
      default: break;
    }
  }

  StyleTextOverflowSide(const StyleTextOverflowSide& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::String: ::new (&string) (StyleString_Body)(other.string); break;
      default: break;
    }
  }
  StyleTextOverflowSide& operator=(const StyleTextOverflowSide& other) {
    if (this != &other) {
      this->~StyleTextOverflowSide();
      new (this) StyleTextOverflowSide(other);
    }
    return *this;
  }
};

/// text-overflow.
/// When the specified value only has one side, that's the "second"
/// side, and the sides are logical, so "second" means "end".  The
/// start side is Clip in that case.
///
/// When the specified value has two sides, those are our "first"
/// and "second" sides, and they are physical sides ("left" and
/// "right").
struct StyleTextOverflow {
  /// First side
  StyleTextOverflowSide first;
  /// Second side
  StyleTextOverflowSide second;
  /// True if the specified value only has one side.
  bool sides_are_logical;

  bool operator==(const StyleTextOverflow& other) const {
    return first == other.first &&
           second == other.second &&
           sides_are_logical == other.sides_are_logical;
  }
  StyleTextOverflow()
    : first(StyleTextOverflowSide::Clip()),
      second(StyleTextOverflowSide::Clip()),
      sides_are_logical(true) {}
};

/// Implements type for text-indent
/// which takes the grammar of [<length-percentage>] && hanging? && each-line?
///
/// https://drafts.csswg.org/css-text/#propdef-text-indent
template<typename LengthPercentage>
struct StyleGenericTextIndent {
  /// The amount of indent to be applied to the inline-start of the first line.
  LengthPercentage length;
  /// Apply indent to non-first lines instead of first.
  bool hanging;
  /// Apply to each line after a hard break, not only first in block.
  bool each_line;

  bool operator==(const StyleGenericTextIndent& other) const {
    return length == other.length &&
           hanging == other.hanging &&
           each_line == other.each_line;
  }
  StyleGenericTextIndent()
    : length(StyleLengthPercentage::Zero()),
      hanging(false),
      each_line(false) {}
};

/// The computed value of `text-indent`.
using StyleTextIndent = StyleGenericTextIndent<StyleLengthPercentage>;

/// A generic value for `scrollbar-color` property.
///
/// https://drafts.csswg.org/css-scrollbars-1/#scrollbar-color
template<typename Color>
struct StyleGenericScrollbarColor {
  enum class Tag : uint8_t {
    /// `auto`
    Auto,
    /// `<color>{2}`
    Colors,
  };

  struct StyleColors_Body {
    /// First `<color>`, for color of the scrollbar thumb.
    Color thumb;
    /// Second `<color>`, for color of the scrollbar track.
    Color track;

    bool operator==(const StyleColors_Body& other) const {
      return thumb == other.thumb &&
             track == other.track;
    }
  };

  Tag tag;
  union {
    StyleColors_Body colors;
  };

  static StyleGenericScrollbarColor Auto() {
    StyleGenericScrollbarColor result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleGenericScrollbarColor Colors(const Color &thumb,
                                           const Color &track) {
    StyleGenericScrollbarColor result;
    ::new (&result.colors.thumb) (Color)(thumb);
    ::new (&result.colors.track) (Color)(track);
    result.tag = Tag::Colors;
    return result;
  }

  bool IsColors() const {
    return tag == Tag::Colors;
  }

  const StyleColors_Body& AsColors() const {
    MOZ_DIAGNOSTIC_ASSERT(IsColors());
    return colors;
  }

  bool operator==(const StyleGenericScrollbarColor& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Colors: return colors == other.colors;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericScrollbarColor() {

  }
  public:


  ~StyleGenericScrollbarColor() {
    switch (tag) {
      case Tag::Colors: colors.~StyleColors_Body(); break;
      default: break;
    }
  }

  StyleGenericScrollbarColor(const StyleGenericScrollbarColor& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Colors: ::new (&colors) (StyleColors_Body)(other.colors); break;
      default: break;
    }
  }
  StyleGenericScrollbarColor& operator=(const StyleGenericScrollbarColor& other) {
    if (this != &other) {
      this->~StyleGenericScrollbarColor();
      new (this) StyleGenericScrollbarColor(other);
    }
    return *this;
  }
};

/// A computed value for `scrollbar-color` property.
using StyleScrollbarColor = StyleGenericScrollbarColor<StyleColor>;

/// Either `<color>` or `auto`.
template<typename C>
struct StyleGenericColorOrAuto {
  enum class Tag : uint8_t {
    /// A `<color>`.
    Color,
    /// `auto`
    Auto,
  };

  struct StyleColor_Body {
    C _0;

    bool operator==(const StyleColor_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleColor_Body color;
  };

  static StyleGenericColorOrAuto Color(const C &_0) {
    StyleGenericColorOrAuto result;
    ::new (&result.color._0) (C)(_0);
    result.tag = Tag::Color;
    return result;
  }

  bool IsColor() const {
    return tag == Tag::Color;
  }

  const C& AsColor() const {
    MOZ_DIAGNOSTIC_ASSERT(IsColor());
    return color._0;
  }

  static StyleGenericColorOrAuto Auto() {
    StyleGenericColorOrAuto result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  bool operator==(const StyleGenericColorOrAuto& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Color: return color == other.color;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericColorOrAuto() {

  }
  public:


  ~StyleGenericColorOrAuto() {
    switch (tag) {
      case Tag::Color: color.~StyleColor_Body(); break;
      default: break;
    }
  }

  StyleGenericColorOrAuto(const StyleGenericColorOrAuto& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Color: ::new (&color) (StyleColor_Body)(other.color); break;
      default: break;
    }
  }
  StyleGenericColorOrAuto& operator=(const StyleGenericColorOrAuto& other) {
    if (this != &other) {
      this->~StyleGenericColorOrAuto();
      new (this) StyleGenericColorOrAuto(other);
    }
    return *this;
  }
};

/// Caret color is effectively a ColorOrAuto, but resolves `auto` to
/// currentColor.
template<typename C>
using StyleGenericCaretColor = StyleGenericColorOrAuto<C>;

/// caret-color
using StyleCaretColor = StyleGenericCaretColor<StyleColor>;

/// auto | <color>
using StyleColorOrAuto = StyleGenericColorOrAuto<StyleColor>;

/// The computed value of `ShapeRadius`.
using StyleShapeRadius = StyleGenericShapeRadius<StyleLengthPercentage>;

/// The computed value of `ShapeCommand`.
using StyleShapeCommand = StyleGenericShapeCommand<StyleAngle, StyleLengthPercentage, StylePosition, StyleLengthPercentage>;

/// The inner pointer of an ArcSlice<T>, to be sent via FFI.
/// The type of the pointer is a bit of a lie, we just want to preserve the type
/// but these pointers cannot be constructed outside of this crate, so we're
/// good.
template<typename T>
struct StyleForgottenArcSlicePtr {
  T *_0;

  bool operator==(const StyleForgottenArcSlicePtr& other) const {
    return _0 == other._0;
  }
};

/// The context properties we understand.
struct StyleContextPropertyBits {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleContextPropertyBits operator~() const {
    return StyleContextPropertyBits { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleContextPropertyBits operator|(const StyleContextPropertyBits& other) const {
    return StyleContextPropertyBits { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleContextPropertyBits& operator|=(const StyleContextPropertyBits& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleContextPropertyBits operator&(const StyleContextPropertyBits& other) const {
    return StyleContextPropertyBits { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleContextPropertyBits& operator&=(const StyleContextPropertyBits& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleContextPropertyBits operator^(const StyleContextPropertyBits& other) const {
    return StyleContextPropertyBits { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleContextPropertyBits& operator^=(const StyleContextPropertyBits& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleContextPropertyBits& other) const {
    return _0 == other._0;
  }
  static const StyleContextPropertyBits FILL;
  static const StyleContextPropertyBits STROKE;
  static const StyleContextPropertyBits FILL_OPACITY;
  static const StyleContextPropertyBits STROKE_OPACITY;
};
/// `fill`
constexpr inline const StyleContextPropertyBits StyleContextPropertyBits::FILL = StyleContextPropertyBits{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// `stroke`
constexpr inline const StyleContextPropertyBits StyleContextPropertyBits::STROKE = StyleContextPropertyBits{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// `fill-opacity`
constexpr inline const StyleContextPropertyBits StyleContextPropertyBits::FILL_OPACITY = StyleContextPropertyBits{
  /* ._0 = */ (uint8_t)(1 << 2)
};
/// `stroke-opacity`
constexpr inline const StyleContextPropertyBits StyleContextPropertyBits::STROKE_OPACITY = StyleContextPropertyBits{
  /* ._0 = */ (uint8_t)(1 << 3)
};

/// Specified MozContextProperties value.
/// Nonstandard (https://developer.mozilla.org/en-US/docs/Web/CSS/-moz-context-properties)
struct StyleMozContextProperties {
  StyleArcSlice<StyleCustomIdent> idents;
  StyleContextPropertyBits bits;

  bool operator==(const StyleMozContextProperties& other) const {
    return idents == other.idents &&
           bits == other.bits;
  }
};

/// A quote pair.
struct StyleQuotePair {
  /// The opening quote.
  StyleOwnedStr opening;
  /// The closing quote.
  StyleOwnedStr closing;

  bool operator==(const StyleQuotePair& other) const {
    return opening == other.opening &&
           closing == other.closing;
  }
};

/// List of quote pairs for the specified/computed value of `quotes` property.
using StyleQuoteList = StyleArcSlice<StyleQuotePair>;

/// Specified and computed `quotes` property: `auto`, `none`, or a list
/// of characters.
struct StyleQuotes {
  enum class Tag {
    /// list of quote pairs
    QuoteList,
    /// auto (use lang-dependent quote marks)
    Auto,
  };

  struct StyleQuoteList_Body {
    StyleQuoteList _0;

    bool operator==(const StyleQuoteList_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleQuoteList_Body quote_list;
  };

  static StyleQuotes QuoteList(const StyleQuoteList &_0) {
    StyleQuotes result;
    ::new (&result.quote_list._0) (StyleQuoteList)(_0);
    result.tag = Tag::QuoteList;
    return result;
  }

  bool IsQuoteList() const {
    return tag == Tag::QuoteList;
  }

  const StyleQuoteList& AsQuoteList() const {
    MOZ_DIAGNOSTIC_ASSERT(IsQuoteList());
    return quote_list._0;
  }

  static StyleQuotes Auto() {
    StyleQuotes result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  bool operator==(const StyleQuotes& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::QuoteList: return quote_list == other.quote_list;
      default: break;
    }
    return true;
  }

  private:
  StyleQuotes() {

  }
  public:


  ~StyleQuotes() {
    switch (tag) {
      case Tag::QuoteList: quote_list.~StyleQuoteList_Body(); break;
      default: break;
    }
  }

  StyleQuotes(const StyleQuotes& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::QuoteList: ::new (&quote_list) (StyleQuoteList_Body)(other.quote_list); break;
      default: break;
    }
  }
  StyleQuotes& operator=(const StyleQuotes& other) {
    if (this != &other) {
      this->~StyleQuotes();
      new (this) StyleQuotes(other);
    }
    return *this;
  }
};

/// A generic value for a single `box-shadow`.
template<typename Color, typename SizeLength, typename BlurShapeLength, typename ShapeLength>
struct StyleGenericBoxShadow {
  /// The base shadow.
  StyleGenericSimpleShadow<Color, SizeLength, BlurShapeLength> base;
  /// The spread radius.
  ShapeLength spread;
  /// Whether this is an inset box shadow.
  bool inset;

  bool operator==(const StyleGenericBoxShadow& other) const {
    return base == other.base &&
           spread == other.spread &&
           inset == other.inset;
  }
};

/// A computed value for a single shadow of the `box-shadow` property.
using StyleBoxShadow = StyleGenericBoxShadow<StyleColor, StyleLength, StyleNonNegativeLength, StyleLength>;

/// A generic value for a single side of a `border-image-width` property.
template<typename LP, typename N>
struct StyleGenericBorderImageSideWidth {
  enum class Tag : uint8_t {
    /// `<number>`
    ///
    /// NOTE: Numbers need to be before length-percentagess, in order to parse
    /// them first, since `0` should be a number, not the `0px` length.
    Number,
    /// `<length-or-percentage>`
    LengthPercentage,
    /// `auto`
    Auto,
  };

  struct StyleNumber_Body {
    N _0;

    bool operator==(const StyleNumber_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleLengthPercentage_Body {
    LP _0;

    bool operator==(const StyleLengthPercentage_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleNumber_Body number;
    StyleLengthPercentage_Body length_percentage;
  };

  static StyleGenericBorderImageSideWidth Number(const N &_0) {
    StyleGenericBorderImageSideWidth result;
    ::new (&result.number._0) (N)(_0);
    result.tag = Tag::Number;
    return result;
  }

  bool IsNumber() const {
    return tag == Tag::Number;
  }

  const N& AsNumber() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNumber());
    return number._0;
  }

  static StyleGenericBorderImageSideWidth LengthPercentage(const LP &_0) {
    StyleGenericBorderImageSideWidth result;
    ::new (&result.length_percentage._0) (LP)(_0);
    result.tag = Tag::LengthPercentage;
    return result;
  }

  bool IsLengthPercentage() const {
    return tag == Tag::LengthPercentage;
  }

  const LP& AsLengthPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLengthPercentage());
    return length_percentage._0;
  }

  static StyleGenericBorderImageSideWidth Auto() {
    StyleGenericBorderImageSideWidth result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  bool operator==(const StyleGenericBorderImageSideWidth& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Number: return number == other.number;
      case Tag::LengthPercentage: return length_percentage == other.length_percentage;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericBorderImageSideWidth() {

  }
  public:


  ~StyleGenericBorderImageSideWidth() {
    switch (tag) {
      case Tag::Number: number.~StyleNumber_Body(); break;
      case Tag::LengthPercentage: length_percentage.~StyleLengthPercentage_Body(); break;
      default: break;
    }
  }

  StyleGenericBorderImageSideWidth(const StyleGenericBorderImageSideWidth& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Number: ::new (&number) (StyleNumber_Body)(other.number); break;
      case Tag::LengthPercentage: ::new (&length_percentage) (StyleLengthPercentage_Body)(other.length_percentage); break;
      default: break;
    }
  }
  StyleGenericBorderImageSideWidth& operator=(const StyleGenericBorderImageSideWidth& other) {
    if (this != &other) {
      this->~StyleGenericBorderImageSideWidth();
      new (this) StyleGenericBorderImageSideWidth(other);
    }
    return *this;
  }
};

/// A computed value for a single side of a `border-image-width` property.
using StyleBorderImageSideWidth = StyleGenericBorderImageSideWidth<StyleNonNegativeLengthPercentage, StyleNonNegativeNumber>;

/// A computed value for the `border-image-width` property.
using StyleBorderImageWidth = StyleRect<StyleBorderImageSideWidth>;

/// An image url or none, used for example in list-style-image
template<typename U>
struct StyleGenericUrlOrNone {
  enum class Tag : uint8_t {
    /// `none`
    None,
    /// A URL.
    Url,
  };

  struct StyleUrl_Body {
    U _0;

    bool operator==(const StyleUrl_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleUrl_Body url;
  };

  static StyleGenericUrlOrNone None() {
    StyleGenericUrlOrNone result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericUrlOrNone Url(const U &_0) {
    StyleGenericUrlOrNone result;
    ::new (&result.url._0) (U)(_0);
    result.tag = Tag::Url;
    return result;
  }

  bool IsUrl() const {
    return tag == Tag::Url;
  }

  const U& AsUrl() const {
    MOZ_DIAGNOSTIC_ASSERT(IsUrl());
    return url._0;
  }

  bool operator==(const StyleGenericUrlOrNone& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Url: return url == other.url;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericUrlOrNone() {

  }
  public:


  ~StyleGenericUrlOrNone() {
    switch (tag) {
      case Tag::Url: url.~StyleUrl_Body(); break;
      default: break;
    }
  }

  StyleGenericUrlOrNone(const StyleGenericUrlOrNone& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Url: ::new (&url) (StyleUrl_Body)(other.url); break;
      default: break;
    }
  }
  StyleGenericUrlOrNone& operator=(const StyleGenericUrlOrNone& other) {
    if (this != &other) {
      this->~StyleGenericUrlOrNone();
      new (this) StyleGenericUrlOrNone(other);
    }
    return *this;
  }
};

/// Computed <url> | <none>
using StyleUrlOrNone = StyleGenericUrlOrNone<StyleComputedUrl>;

/// A computed gradient line direction.
struct StyleLineDirection {
  enum class Tag : uint8_t {
    /// An angle.
    Angle,
    /// A horizontal direction.
    Horizontal,
    /// A vertical direction.
    Vertical,
    /// A corner.
    Corner,
  };

  struct StyleAngle_Body {
    StyleAngle _0;

    bool operator==(const StyleAngle_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleHorizontal_Body {
    StyleHorizontalPositionKeyword _0;

    bool operator==(const StyleHorizontal_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleVertical_Body {
    StyleVerticalPositionKeyword _0;

    bool operator==(const StyleVertical_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleCorner_Body {
    StyleHorizontalPositionKeyword _0;
    StyleVerticalPositionKeyword _1;

    bool operator==(const StyleCorner_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  Tag tag;
  union {
    StyleAngle_Body angle;
    StyleHorizontal_Body horizontal;
    StyleVertical_Body vertical;
    StyleCorner_Body corner;
  };

  static StyleLineDirection Angle(const StyleAngle &_0) {
    StyleLineDirection result;
    ::new (&result.angle._0) (StyleAngle)(_0);
    result.tag = Tag::Angle;
    return result;
  }

  bool IsAngle() const {
    return tag == Tag::Angle;
  }

  const StyleAngle& AsAngle() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAngle());
    return angle._0;
  }

  static StyleLineDirection Horizontal(const StyleHorizontalPositionKeyword &_0) {
    StyleLineDirection result;
    ::new (&result.horizontal._0) (StyleHorizontalPositionKeyword)(_0);
    result.tag = Tag::Horizontal;
    return result;
  }

  bool IsHorizontal() const {
    return tag == Tag::Horizontal;
  }

  const StyleHorizontalPositionKeyword& AsHorizontal() const {
    MOZ_DIAGNOSTIC_ASSERT(IsHorizontal());
    return horizontal._0;
  }

  static StyleLineDirection Vertical(const StyleVerticalPositionKeyword &_0) {
    StyleLineDirection result;
    ::new (&result.vertical._0) (StyleVerticalPositionKeyword)(_0);
    result.tag = Tag::Vertical;
    return result;
  }

  bool IsVertical() const {
    return tag == Tag::Vertical;
  }

  const StyleVerticalPositionKeyword& AsVertical() const {
    MOZ_DIAGNOSTIC_ASSERT(IsVertical());
    return vertical._0;
  }

  static StyleLineDirection Corner(const StyleHorizontalPositionKeyword &_0,
                                   const StyleVerticalPositionKeyword &_1) {
    StyleLineDirection result;
    ::new (&result.corner._0) (StyleHorizontalPositionKeyword)(_0);
    ::new (&result.corner._1) (StyleVerticalPositionKeyword)(_1);
    result.tag = Tag::Corner;
    return result;
  }

  bool IsCorner() const {
    return tag == Tag::Corner;
  }

  const StyleCorner_Body& AsCorner() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCorner());
    return corner;
  }

  bool operator==(const StyleLineDirection& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Angle: return angle == other.angle;
      case Tag::Horizontal: return horizontal == other.horizontal;
      case Tag::Vertical: return vertical == other.vertical;
      case Tag::Corner: return corner == other.corner;

    }
    return true;
  }

  private:
  StyleLineDirection() {

  }
  public:


  ~StyleLineDirection() {
    switch (tag) {
      case Tag::Angle: angle.~StyleAngle_Body(); break;
      case Tag::Horizontal: horizontal.~StyleHorizontal_Body(); break;
      case Tag::Vertical: vertical.~StyleVertical_Body(); break;
      case Tag::Corner: corner.~StyleCorner_Body(); break;

    }
  }

  StyleLineDirection(const StyleLineDirection& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Angle: ::new (&angle) (StyleAngle_Body)(other.angle); break;
      case Tag::Horizontal: ::new (&horizontal) (StyleHorizontal_Body)(other.horizontal); break;
      case Tag::Vertical: ::new (&vertical) (StyleVertical_Body)(other.vertical); break;
      case Tag::Corner: ::new (&corner) (StyleCorner_Body)(other.corner); break;

    }
  }
  StyleLineDirection& operator=(const StyleLineDirection& other) {
    if (this != &other) {
      this->~StyleLineDirection();
      new (this) StyleLineDirection(other);
    }
    return *this;
  }
};

struct StyleAngleOrPercentage {
  enum class Tag : uint8_t {
    Percentage,
    Angle,
  };

  struct StylePercentage_Body {
    StylePercentage _0;

    bool operator==(const StylePercentage_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAngle_Body {
    StyleAngle _0;

    bool operator==(const StyleAngle_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StylePercentage_Body percentage;
    StyleAngle_Body angle;
  };

  static StyleAngleOrPercentage Percentage(const StylePercentage &_0) {
    StyleAngleOrPercentage result;
    ::new (&result.percentage._0) (StylePercentage)(_0);
    result.tag = Tag::Percentage;
    return result;
  }

  bool IsPercentage() const {
    return tag == Tag::Percentage;
  }

  const StylePercentage& AsPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPercentage());
    return percentage._0;
  }

  static StyleAngleOrPercentage Angle(const StyleAngle &_0) {
    StyleAngleOrPercentage result;
    ::new (&result.angle._0) (StyleAngle)(_0);
    result.tag = Tag::Angle;
    return result;
  }

  bool IsAngle() const {
    return tag == Tag::Angle;
  }

  const StyleAngle& AsAngle() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAngle());
    return angle._0;
  }

  bool operator==(const StyleAngleOrPercentage& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Percentage: return percentage == other.percentage;
      case Tag::Angle: return angle == other.angle;

    }
    return true;
  }

  private:
  StyleAngleOrPercentage() {

  }
  public:


  ~StyleAngleOrPercentage() {
    switch (tag) {
      case Tag::Percentage: percentage.~StylePercentage_Body(); break;
      case Tag::Angle: angle.~StyleAngle_Body(); break;

    }
  }

  StyleAngleOrPercentage(const StyleAngleOrPercentage& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Percentage: ::new (&percentage) (StylePercentage_Body)(other.percentage); break;
      case Tag::Angle: ::new (&angle) (StyleAngle_Body)(other.angle); break;

    }
  }
  StyleAngleOrPercentage& operator=(const StyleAngleOrPercentage& other) {
    if (this != &other) {
      this->~StyleAngleOrPercentage();
      new (this) StyleAngleOrPercentage(other);
    }
    return *this;
  }
};

/// A gradient item.
/// <https://drafts.csswg.org/css-images-4/#color-stop-syntax>
template<typename Color, typename T>
struct StyleGenericGradientItem {
  enum class Tag : uint8_t {
    /// A simple color stop, without position.
    SimpleColorStop,
    /// A complex color stop, with a position.
    ComplexColorStop,
    /// An interpolation hint.
    InterpolationHint,
  };

  struct StyleSimpleColorStop_Body {
    Color _0;

    bool operator==(const StyleSimpleColorStop_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleComplexColorStop_Body {
    /// The color for the stop.
    Color color;
    /// The position for the stop.
    T position;

    bool operator==(const StyleComplexColorStop_Body& other) const {
      return color == other.color &&
             position == other.position;
    }
  };

  struct StyleInterpolationHint_Body {
    T _0;

    bool operator==(const StyleInterpolationHint_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleSimpleColorStop_Body simple_color_stop;
    StyleComplexColorStop_Body complex_color_stop;
    StyleInterpolationHint_Body interpolation_hint;
  };

  static StyleGenericGradientItem SimpleColorStop(const Color &_0) {
    StyleGenericGradientItem result;
    ::new (&result.simple_color_stop._0) (Color)(_0);
    result.tag = Tag::SimpleColorStop;
    return result;
  }

  bool IsSimpleColorStop() const {
    return tag == Tag::SimpleColorStop;
  }

  const Color& AsSimpleColorStop() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSimpleColorStop());
    return simple_color_stop._0;
  }

  static StyleGenericGradientItem ComplexColorStop(const Color &color,
                                                   const T &position) {
    StyleGenericGradientItem result;
    ::new (&result.complex_color_stop.color) (Color)(color);
    ::new (&result.complex_color_stop.position) (T)(position);
    result.tag = Tag::ComplexColorStop;
    return result;
  }

  bool IsComplexColorStop() const {
    return tag == Tag::ComplexColorStop;
  }

  const StyleComplexColorStop_Body& AsComplexColorStop() const {
    MOZ_DIAGNOSTIC_ASSERT(IsComplexColorStop());
    return complex_color_stop;
  }

  static StyleGenericGradientItem InterpolationHint(const T &_0) {
    StyleGenericGradientItem result;
    ::new (&result.interpolation_hint._0) (T)(_0);
    result.tag = Tag::InterpolationHint;
    return result;
  }

  bool IsInterpolationHint() const {
    return tag == Tag::InterpolationHint;
  }

  const T& AsInterpolationHint() const {
    MOZ_DIAGNOSTIC_ASSERT(IsInterpolationHint());
    return interpolation_hint._0;
  }

  bool operator==(const StyleGenericGradientItem& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::SimpleColorStop: return simple_color_stop == other.simple_color_stop;
      case Tag::ComplexColorStop: return complex_color_stop == other.complex_color_stop;
      case Tag::InterpolationHint: return interpolation_hint == other.interpolation_hint;

    }
    return true;
  }

  private:
  StyleGenericGradientItem() {

  }
  public:


  ~StyleGenericGradientItem() {
    switch (tag) {
      case Tag::SimpleColorStop: simple_color_stop.~StyleSimpleColorStop_Body(); break;
      case Tag::ComplexColorStop: complex_color_stop.~StyleComplexColorStop_Body(); break;
      case Tag::InterpolationHint: interpolation_hint.~StyleInterpolationHint_Body(); break;

    }
  }

  StyleGenericGradientItem(const StyleGenericGradientItem& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::SimpleColorStop: ::new (&simple_color_stop) (StyleSimpleColorStop_Body)(other.simple_color_stop); break;
      case Tag::ComplexColorStop: ::new (&complex_color_stop) (StyleComplexColorStop_Body)(other.complex_color_stop); break;
      case Tag::InterpolationHint: ::new (&interpolation_hint) (StyleInterpolationHint_Body)(other.interpolation_hint); break;

    }
  }
  StyleGenericGradientItem& operator=(const StyleGenericGradientItem& other) {
    if (this != &other) {
      this->~StyleGenericGradientItem();
      new (this) StyleGenericGradientItem(other);
    }
    return *this;
  }
};

/// State flags stored on each variant of a Gradient.
struct StyleGradientFlags {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleGradientFlags operator~() const {
    return StyleGradientFlags { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleGradientFlags operator|(const StyleGradientFlags& other) const {
    return StyleGradientFlags { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleGradientFlags& operator|=(const StyleGradientFlags& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleGradientFlags operator&(const StyleGradientFlags& other) const {
    return StyleGradientFlags { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleGradientFlags& operator&=(const StyleGradientFlags& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleGradientFlags operator^(const StyleGradientFlags& other) const {
    return StyleGradientFlags { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleGradientFlags& operator^=(const StyleGradientFlags& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleGradientFlags& other) const {
    return _0 == other._0;
  }
  static const StyleGradientFlags REPEATING;
  static const StyleGradientFlags HAS_DEFAULT_COLOR_INTERPOLATION_METHOD;
};
/// Set if this is a repeating gradient.
constexpr inline const StyleGradientFlags StyleGradientFlags::REPEATING = StyleGradientFlags{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// Set if the color interpolation method matches the default for the items.
constexpr inline const StyleGradientFlags StyleGradientFlags::HAS_DEFAULT_COLOR_INTERPOLATION_METHOD = StyleGradientFlags{
  /* ._0 = */ (uint8_t)(1 << 1)
};

/// A circle shape.
template<typename NonNegativeLength>
struct StyleGenericCircle {
  enum class Tag : uint8_t {
    /// A circle radius.
    Radius,
    /// A circle extent.
    Extent,
  };

  struct StyleRadius_Body {
    NonNegativeLength _0;

    bool operator==(const StyleRadius_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleExtent_Body {
    StyleShapeExtent _0;

    bool operator==(const StyleExtent_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleRadius_Body radius;
    StyleExtent_Body extent;
  };

  static StyleGenericCircle Radius(const NonNegativeLength &_0) {
    StyleGenericCircle result;
    ::new (&result.radius._0) (NonNegativeLength)(_0);
    result.tag = Tag::Radius;
    return result;
  }

  bool IsRadius() const {
    return tag == Tag::Radius;
  }

  const NonNegativeLength& AsRadius() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRadius());
    return radius._0;
  }

  static StyleGenericCircle Extent(const StyleShapeExtent &_0) {
    StyleGenericCircle result;
    ::new (&result.extent._0) (StyleShapeExtent)(_0);
    result.tag = Tag::Extent;
    return result;
  }

  bool IsExtent() const {
    return tag == Tag::Extent;
  }

  const StyleShapeExtent& AsExtent() const {
    MOZ_DIAGNOSTIC_ASSERT(IsExtent());
    return extent._0;
  }

  bool operator==(const StyleGenericCircle& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Radius: return radius == other.radius;
      case Tag::Extent: return extent == other.extent;

    }
    return true;
  }

  private:
  StyleGenericCircle() {

  }
  public:


  ~StyleGenericCircle() {
    switch (tag) {
      case Tag::Radius: radius.~StyleRadius_Body(); break;
      case Tag::Extent: extent.~StyleExtent_Body(); break;

    }
  }

  StyleGenericCircle(const StyleGenericCircle& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Radius: ::new (&radius) (StyleRadius_Body)(other.radius); break;
      case Tag::Extent: ::new (&extent) (StyleExtent_Body)(other.extent); break;

    }
  }
  StyleGenericCircle& operator=(const StyleGenericCircle& other) {
    if (this != &other) {
      this->~StyleGenericCircle();
      new (this) StyleGenericCircle(other);
    }
    return *this;
  }
};

/// An ellipse shape.
template<typename NonNegativeLengthPercentage>
struct StyleGenericEllipse {
  enum class Tag : uint8_t {
    /// An ellipse pair of radii.
    Radii,
    /// An ellipse extent.
    Extent,
  };

  struct StyleRadii_Body {
    NonNegativeLengthPercentage _0;
    NonNegativeLengthPercentage _1;

    bool operator==(const StyleRadii_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct StyleExtent_Body {
    StyleShapeExtent _0;

    bool operator==(const StyleExtent_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleRadii_Body radii;
    StyleExtent_Body extent;
  };

  static StyleGenericEllipse Radii(const NonNegativeLengthPercentage &_0,
                                   const NonNegativeLengthPercentage &_1) {
    StyleGenericEllipse result;
    ::new (&result.radii._0) (NonNegativeLengthPercentage)(_0);
    ::new (&result.radii._1) (NonNegativeLengthPercentage)(_1);
    result.tag = Tag::Radii;
    return result;
  }

  bool IsRadii() const {
    return tag == Tag::Radii;
  }

  const StyleRadii_Body& AsRadii() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRadii());
    return radii;
  }

  static StyleGenericEllipse Extent(const StyleShapeExtent &_0) {
    StyleGenericEllipse result;
    ::new (&result.extent._0) (StyleShapeExtent)(_0);
    result.tag = Tag::Extent;
    return result;
  }

  bool IsExtent() const {
    return tag == Tag::Extent;
  }

  const StyleShapeExtent& AsExtent() const {
    MOZ_DIAGNOSTIC_ASSERT(IsExtent());
    return extent._0;
  }

  bool operator==(const StyleGenericEllipse& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Radii: return radii == other.radii;
      case Tag::Extent: return extent == other.extent;

    }
    return true;
  }

  private:
  StyleGenericEllipse() {

  }
  public:


  ~StyleGenericEllipse() {
    switch (tag) {
      case Tag::Radii: radii.~StyleRadii_Body(); break;
      case Tag::Extent: extent.~StyleExtent_Body(); break;

    }
  }

  StyleGenericEllipse(const StyleGenericEllipse& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Radii: ::new (&radii) (StyleRadii_Body)(other.radii); break;
      case Tag::Extent: ::new (&extent) (StyleExtent_Body)(other.extent); break;

    }
  }
  StyleGenericEllipse& operator=(const StyleGenericEllipse& other) {
    if (this != &other) {
      this->~StyleGenericEllipse();
      new (this) StyleGenericEllipse(other);
    }
    return *this;
  }
};

/// A radial gradient's ending shape.
template<typename NonNegativeLength, typename NonNegativeLengthPercentage>
struct StyleGenericEndingShape {
  enum class Tag : uint8_t {
    /// A circular gradient.
    Circle,
    /// An elliptic gradient.
    Ellipse,
  };

  struct StyleCircle_Body {
    StyleGenericCircle<NonNegativeLength> _0;

    bool operator==(const StyleCircle_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleEllipse_Body {
    StyleGenericEllipse<NonNegativeLengthPercentage> _0;

    bool operator==(const StyleEllipse_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleCircle_Body circle;
    StyleEllipse_Body ellipse;
  };

  static StyleGenericEndingShape Circle(const StyleGenericCircle<NonNegativeLength> &_0) {
    StyleGenericEndingShape result;
    ::new (&result.circle._0) (StyleGenericCircle<NonNegativeLength>)(_0);
    result.tag = Tag::Circle;
    return result;
  }

  bool IsCircle() const {
    return tag == Tag::Circle;
  }

  const StyleGenericCircle<NonNegativeLength>& AsCircle() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCircle());
    return circle._0;
  }

  static StyleGenericEndingShape Ellipse(const StyleGenericEllipse<NonNegativeLengthPercentage> &_0) {
    StyleGenericEndingShape result;
    ::new (&result.ellipse._0) (StyleGenericEllipse<NonNegativeLengthPercentage>)(_0);
    result.tag = Tag::Ellipse;
    return result;
  }

  bool IsEllipse() const {
    return tag == Tag::Ellipse;
  }

  const StyleGenericEllipse<NonNegativeLengthPercentage>& AsEllipse() const {
    MOZ_DIAGNOSTIC_ASSERT(IsEllipse());
    return ellipse._0;
  }

  bool operator==(const StyleGenericEndingShape& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Circle: return circle == other.circle;
      case Tag::Ellipse: return ellipse == other.ellipse;

    }
    return true;
  }

  private:
  StyleGenericEndingShape() {

  }
  public:


  ~StyleGenericEndingShape() {
    switch (tag) {
      case Tag::Circle: circle.~StyleCircle_Body(); break;
      case Tag::Ellipse: ellipse.~StyleEllipse_Body(); break;

    }
  }

  StyleGenericEndingShape(const StyleGenericEndingShape& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Circle: ::new (&circle) (StyleCircle_Body)(other.circle); break;
      case Tag::Ellipse: ::new (&ellipse) (StyleEllipse_Body)(other.ellipse); break;

    }
  }
  StyleGenericEndingShape& operator=(const StyleGenericEndingShape& other) {
    if (this != &other) {
      this->~StyleGenericEndingShape();
      new (this) StyleGenericEndingShape(other);
    }
    return *this;
  }
};

/// A CSS gradient.
/// <https://drafts.csswg.org/css-images/#gradients>
template<typename LineDirection, typename Length, typename LengthPercentage, typename Position, typename Angle, typename AngleOrPercentage, typename Color>
struct StyleGenericGradient {
  enum class Tag {
    /// A linear gradient.
    Linear,
    /// A radial gradient.
    Radial,
    /// A conic gradient.
    Conic,
  };

  struct StyleLinear_Body {
    /// Line direction
    LineDirection direction;
    /// Method to use for color interpolation.
    StyleColorInterpolationMethod color_interpolation_method;
    /// The color stops and interpolation hints.
    StyleOwnedSlice<StyleGenericGradientItem<Color, LengthPercentage>> items;
    /// State flags for the gradient.
    StyleGradientFlags flags;
    /// Compatibility mode.
    StyleGradientCompatMode compat_mode;

    bool operator==(const StyleLinear_Body& other) const {
      return direction == other.direction &&
             color_interpolation_method == other.color_interpolation_method &&
             items == other.items &&
             flags == other.flags &&
             compat_mode == other.compat_mode;
    }
  };

  struct StyleRadial_Body {
    /// Shape of gradient
    StyleGenericEndingShape<StyleNonNegative<Length>, StyleNonNegative<LengthPercentage>> shape;
    /// Center of gradient
    Position position;
    /// Method to use for color interpolation.
    StyleColorInterpolationMethod color_interpolation_method;
    /// The color stops and interpolation hints.
    StyleOwnedSlice<StyleGenericGradientItem<Color, LengthPercentage>> items;
    /// State flags for the gradient.
    StyleGradientFlags flags;
    /// Compatibility mode.
    StyleGradientCompatMode compat_mode;

    bool operator==(const StyleRadial_Body& other) const {
      return shape == other.shape &&
             position == other.position &&
             color_interpolation_method == other.color_interpolation_method &&
             items == other.items &&
             flags == other.flags &&
             compat_mode == other.compat_mode;
    }
  };

  struct StyleConic_Body {
    /// Start angle of gradient
    Angle angle;
    /// Center of gradient
    Position position;
    /// Method to use for color interpolation.
    StyleColorInterpolationMethod color_interpolation_method;
    /// The color stops and interpolation hints.
    StyleOwnedSlice<StyleGenericGradientItem<Color, AngleOrPercentage>> items;
    /// State flags for the gradient.
    StyleGradientFlags flags;

    bool operator==(const StyleConic_Body& other) const {
      return angle == other.angle &&
             position == other.position &&
             color_interpolation_method == other.color_interpolation_method &&
             items == other.items &&
             flags == other.flags;
    }
  };

  Tag tag;
  union {
    StyleLinear_Body linear;
    StyleRadial_Body radial;
    StyleConic_Body conic;
  };

  static StyleGenericGradient Linear(const LineDirection &direction,
                                     const StyleColorInterpolationMethod &color_interpolation_method,
                                     const StyleOwnedSlice<StyleGenericGradientItem<Color, LengthPercentage>> &items,
                                     const StyleGradientFlags &flags,
                                     const StyleGradientCompatMode &compat_mode) {
    StyleGenericGradient result;
    ::new (&result.linear.direction) (LineDirection)(direction);
    ::new (&result.linear.color_interpolation_method) (StyleColorInterpolationMethod)(color_interpolation_method);
    ::new (&result.linear.items) (StyleOwnedSlice<StyleGenericGradientItem<Color, LengthPercentage>>)(items);
    ::new (&result.linear.flags) (StyleGradientFlags)(flags);
    ::new (&result.linear.compat_mode) (StyleGradientCompatMode)(compat_mode);
    result.tag = Tag::Linear;
    return result;
  }

  bool IsLinear() const {
    return tag == Tag::Linear;
  }

  const StyleLinear_Body& AsLinear() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLinear());
    return linear;
  }

  static StyleGenericGradient Radial(const StyleGenericEndingShape<StyleNonNegative<Length>, StyleNonNegative<LengthPercentage>> &shape,
                                     const Position &position,
                                     const StyleColorInterpolationMethod &color_interpolation_method,
                                     const StyleOwnedSlice<StyleGenericGradientItem<Color, LengthPercentage>> &items,
                                     const StyleGradientFlags &flags,
                                     const StyleGradientCompatMode &compat_mode) {
    StyleGenericGradient result;
    ::new (&result.radial.shape) (StyleGenericEndingShape<StyleNonNegative<Length>, StyleNonNegative<LengthPercentage>>)(shape);
    ::new (&result.radial.position) (Position)(position);
    ::new (&result.radial.color_interpolation_method) (StyleColorInterpolationMethod)(color_interpolation_method);
    ::new (&result.radial.items) (StyleOwnedSlice<StyleGenericGradientItem<Color, LengthPercentage>>)(items);
    ::new (&result.radial.flags) (StyleGradientFlags)(flags);
    ::new (&result.radial.compat_mode) (StyleGradientCompatMode)(compat_mode);
    result.tag = Tag::Radial;
    return result;
  }

  bool IsRadial() const {
    return tag == Tag::Radial;
  }

  const StyleRadial_Body& AsRadial() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRadial());
    return radial;
  }

  static StyleGenericGradient Conic(const Angle &angle,
                                    const Position &position,
                                    const StyleColorInterpolationMethod &color_interpolation_method,
                                    const StyleOwnedSlice<StyleGenericGradientItem<Color, AngleOrPercentage>> &items,
                                    const StyleGradientFlags &flags) {
    StyleGenericGradient result;
    ::new (&result.conic.angle) (Angle)(angle);
    ::new (&result.conic.position) (Position)(position);
    ::new (&result.conic.color_interpolation_method) (StyleColorInterpolationMethod)(color_interpolation_method);
    ::new (&result.conic.items) (StyleOwnedSlice<StyleGenericGradientItem<Color, AngleOrPercentage>>)(items);
    ::new (&result.conic.flags) (StyleGradientFlags)(flags);
    result.tag = Tag::Conic;
    return result;
  }

  bool IsConic() const {
    return tag == Tag::Conic;
  }

  const StyleConic_Body& AsConic() const {
    MOZ_DIAGNOSTIC_ASSERT(IsConic());
    return conic;
  }

  bool operator==(const StyleGenericGradient& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Linear: return linear == other.linear;
      case Tag::Radial: return radial == other.radial;
      case Tag::Conic: return conic == other.conic;

    }
    return true;
  }

  private:
  StyleGenericGradient() {

  }
  public:


  ~StyleGenericGradient() {
    switch (tag) {
      case Tag::Linear: linear.~StyleLinear_Body(); break;
      case Tag::Radial: radial.~StyleRadial_Body(); break;
      case Tag::Conic: conic.~StyleConic_Body(); break;

    }
  }

  StyleGenericGradient(const StyleGenericGradient& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Linear: ::new (&linear) (StyleLinear_Body)(other.linear); break;
      case Tag::Radial: ::new (&radial) (StyleRadial_Body)(other.radial); break;
      case Tag::Conic: ::new (&conic) (StyleConic_Body)(other.conic); break;

    }
  }
  StyleGenericGradient& operator=(const StyleGenericGradient& other) {
    if (this != &other) {
      this->~StyleGenericGradient();
      new (this) StyleGenericGradient(other);
    }
    return *this;
  }
  inline bool Repeating() const;
  bool IsOpaque() const;

  // Return the color interpolation method of the gradient.
  inline const StyleColorInterpolationMethod& ColorInterpolationMethod() const;
};

/// Computed values for a CSS gradient.
/// <https://drafts.csswg.org/css-images/#gradients>
using StyleGradient = StyleGenericGradient<StyleLineDirection, StyleLength, StyleLengthPercentage, StylePosition, StyleAngle, StyleAngleOrPercentage, StyleColor>;

/// A range of rows or columns. Using this instead of std::ops::Range for FFI
/// purposes.
struct StyleUnsignedRange {
  /// The start of the range.
  uint32_t start;
  /// The end of the range.
  uint32_t end;

  bool operator==(const StyleUnsignedRange& other) const {
    return start == other.start &&
           end == other.end;
  }
};

/// Not associated with any particular grid item, but can be referenced from the
/// grid-placement properties.
struct StyleNamedArea {
  /// Name of the `named area`
  StyleAtom name;
  /// Rows of the `named area`
  StyleUnsignedRange rows;
  /// Columns of the `named area`
  StyleUnsignedRange columns;

  bool operator==(const StyleNamedArea& other) const {
    return name == other.name &&
           rows == other.rows &&
           columns == other.columns;
  }
};

/// https://drafts.csswg.org/css-grid/#named-grid-area
struct StyleTemplateAreas {
  /// `named area` containing for each template area
  StyleOwnedSlice<StyleNamedArea> areas;
  /// The simplified CSS strings for serialization purpose.
  /// https://drafts.csswg.org/css-grid/#serialize-template
  StyleOwnedSlice<StyleOwnedStr> strings;
  /// The number of columns of the grid.
  uint32_t width;

  bool operator==(const StyleTemplateAreas& other) const {
    return areas == other.areas &&
           strings == other.strings &&
           width == other.width;
  }
};

/// Arc type for `Arc<TemplateAreas>`
using StyleTemplateAreasArc = StyleArc<StyleTemplateAreas>;

/// This property specifies named grid areas.
///
/// The syntax of this property also provides a visualization of the structure
/// of the grid, making the overall layout of the grid container easier to
/// understand.
struct StyleGridTemplateAreas {
  enum class Tag : uint8_t {
    /// The `none` value.
    None,
    /// The actual value.
    Areas,
  };

  struct StyleAreas_Body {
    StyleTemplateAreasArc _0;

    bool operator==(const StyleAreas_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleAreas_Body areas;
  };

  static StyleGridTemplateAreas None() {
    StyleGridTemplateAreas result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGridTemplateAreas Areas(const StyleTemplateAreasArc &_0) {
    StyleGridTemplateAreas result;
    ::new (&result.areas._0) (StyleTemplateAreasArc)(_0);
    result.tag = Tag::Areas;
    return result;
  }

  bool IsAreas() const {
    return tag == Tag::Areas;
  }

  const StyleTemplateAreasArc& AsAreas() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAreas());
    return areas._0;
  }

  bool operator==(const StyleGridTemplateAreas& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Areas: return areas == other.areas;
      default: break;
    }
    return true;
  }

  private:
  StyleGridTemplateAreas() {

  }
  public:


  ~StyleGridTemplateAreas() {
    switch (tag) {
      case Tag::Areas: areas.~StyleAreas_Body(); break;
      default: break;
    }
  }

  StyleGridTemplateAreas(const StyleGridTemplateAreas& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Areas: ::new (&areas) (StyleAreas_Body)(other.areas); break;
      default: break;
    }
  }
  StyleGridTemplateAreas& operator=(const StyleGridTemplateAreas& other) {
    if (this != &other) {
      this->~StyleGridTemplateAreas();
      new (this) StyleGridTemplateAreas(other);
    }
    return *this;
  }
};

/// A `<grid-line>` type.
///
/// <https://drafts.csswg.org/css-grid/#typedef-grid-row-start-grid-line>
template<typename Integer>
struct StyleGenericGridLine {
  /// A custom identifier for named lines, or the empty atom otherwise.
  ///
  /// <https://drafts.csswg.org/css-grid/#grid-placement-slot>
  StyleCustomIdent ident;
  /// Denotes the nth grid line from grid item's placement.
  Integer line_num;
  /// Flag to check whether it's a `span` keyword.
  bool is_span;

  bool operator==(const StyleGenericGridLine& other) const {
    return ident == other.ident &&
           line_num == other.line_num &&
           is_span == other.is_span;
  }
  // Returns the `auto` value.
  inline StyleGenericGridLine();
  inline bool IsAuto() const;
  // The line name, or nsGkAtoms::_empty if not present.
  inline nsAtom* LineName() const;
};

/// The computed value of a `<grid-line>`.
using StyleGridLine = StyleGenericGridLine<StyleInteger>;

/// A CSS `<flex>` value.
///
/// https://drafts.csswg.org/css-grid-2/#typedef-flex
struct StyleFlex {
  StyleCSSFloat _0;

  bool operator==(const StyleFlex& other) const {
    return _0 == other._0;
  }
};

/// A track breadth for explicit grid track sizing. It's generic solely to
/// avoid re-implementing it for the computed type.
///
/// <https://drafts.csswg.org/css-grid/#typedef-track-breadth>
template<typename L>
struct StyleGenericTrackBreadth {
  enum class Tag : uint8_t {
    /// The generic type is almost always a non-negative `<length-percentage>`
    Breadth,
    /// A flex fraction specified in `fr` units.
    Flex,
    /// `auto`
    Auto,
    /// `min-content`
    MinContent,
    /// `max-content`
    MaxContent,
  };

  struct StyleBreadth_Body {
    L _0;

    bool operator==(const StyleBreadth_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleFlex_Body {
    StyleFlex _0;

    bool operator==(const StyleFlex_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleBreadth_Body breadth;
    StyleFlex_Body flex;
  };

  static StyleGenericTrackBreadth Breadth(const L &_0) {
    StyleGenericTrackBreadth result;
    ::new (&result.breadth._0) (L)(_0);
    result.tag = Tag::Breadth;
    return result;
  }

  bool IsBreadth() const {
    return tag == Tag::Breadth;
  }

  const L& AsBreadth() const {
    MOZ_DIAGNOSTIC_ASSERT(IsBreadth());
    return breadth._0;
  }

  static StyleGenericTrackBreadth Flex(const StyleFlex &_0) {
    StyleGenericTrackBreadth result;
    ::new (&result.flex._0) (StyleFlex)(_0);
    result.tag = Tag::Flex;
    return result;
  }

  bool IsFlex() const {
    return tag == Tag::Flex;
  }

  const StyleFlex& AsFlex() const {
    MOZ_DIAGNOSTIC_ASSERT(IsFlex());
    return flex._0;
  }

  static StyleGenericTrackBreadth Auto() {
    StyleGenericTrackBreadth result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleGenericTrackBreadth MinContent() {
    StyleGenericTrackBreadth result;
    result.tag = Tag::MinContent;
    return result;
  }

  bool IsMinContent() const {
    return tag == Tag::MinContent;
  }

  static StyleGenericTrackBreadth MaxContent() {
    StyleGenericTrackBreadth result;
    result.tag = Tag::MaxContent;
    return result;
  }

  bool IsMaxContent() const {
    return tag == Tag::MaxContent;
  }

  bool operator==(const StyleGenericTrackBreadth& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Breadth: return breadth == other.breadth;
      case Tag::Flex: return flex == other.flex;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericTrackBreadth() {

  }
  public:


  ~StyleGenericTrackBreadth() {
    switch (tag) {
      case Tag::Breadth: breadth.~StyleBreadth_Body(); break;
      case Tag::Flex: flex.~StyleFlex_Body(); break;
      default: break;
    }
  }

  StyleGenericTrackBreadth(const StyleGenericTrackBreadth& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Breadth: ::new (&breadth) (StyleBreadth_Body)(other.breadth); break;
      case Tag::Flex: ::new (&flex) (StyleFlex_Body)(other.flex); break;
      default: break;
    }
  }
  StyleGenericTrackBreadth& operator=(const StyleGenericTrackBreadth& other) {
    if (this != &other) {
      this->~StyleGenericTrackBreadth();
      new (this) StyleGenericTrackBreadth(other);
    }
    return *this;
  }
  inline bool HasPercent() const;
};

/// A `<track-size>` type for explicit grid track sizing. Like `<track-breadth>`, this is
/// generic only to avoid code bloat. It only takes `<length-percentage>`
///
/// <https://drafts.csswg.org/css-grid/#typedef-track-size>
template<typename L>
struct StyleGenericTrackSize {
  enum class Tag : uint8_t {
    /// A flexible `<track-breadth>`
    Breadth,
    /// A `minmax` function for a range over an inflexible `<track-breadth>`
    /// and a flexible `<track-breadth>`
    ///
    /// <https://drafts.csswg.org/css-grid/#valdef-grid-template-columns-minmax>
    Minmax,
    /// A `fit-content` function.
    ///
    /// This stores a TrackBreadth<L> for convenience, but it can only be a
    /// LengthPercentage.
    ///
    /// <https://drafts.csswg.org/css-grid/#valdef-grid-template-columns-fit-content>
    FitContent,
  };

  struct StyleBreadth_Body {
    StyleGenericTrackBreadth<L> _0;

    bool operator==(const StyleBreadth_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleMinmax_Body {
    StyleGenericTrackBreadth<L> _0;
    StyleGenericTrackBreadth<L> _1;

    bool operator==(const StyleMinmax_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct StyleFitContent_Body {
    StyleGenericTrackBreadth<L> _0;

    bool operator==(const StyleFitContent_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleBreadth_Body breadth;
    StyleMinmax_Body minmax;
    StyleFitContent_Body fit_content;
  };

  static StyleGenericTrackSize Breadth(const StyleGenericTrackBreadth<L> &_0) {
    StyleGenericTrackSize result;
    ::new (&result.breadth._0) (StyleGenericTrackBreadth<L>)(_0);
    result.tag = Tag::Breadth;
    return result;
  }

  bool IsBreadth() const {
    return tag == Tag::Breadth;
  }

  const StyleGenericTrackBreadth<L>& AsBreadth() const {
    MOZ_DIAGNOSTIC_ASSERT(IsBreadth());
    return breadth._0;
  }

  static StyleGenericTrackSize Minmax(const StyleGenericTrackBreadth<L> &_0,
                                      const StyleGenericTrackBreadth<L> &_1) {
    StyleGenericTrackSize result;
    ::new (&result.minmax._0) (StyleGenericTrackBreadth<L>)(_0);
    ::new (&result.minmax._1) (StyleGenericTrackBreadth<L>)(_1);
    result.tag = Tag::Minmax;
    return result;
  }

  bool IsMinmax() const {
    return tag == Tag::Minmax;
  }

  const StyleMinmax_Body& AsMinmax() const {
    MOZ_DIAGNOSTIC_ASSERT(IsMinmax());
    return minmax;
  }

  static StyleGenericTrackSize FitContent(const StyleGenericTrackBreadth<L> &_0) {
    StyleGenericTrackSize result;
    ::new (&result.fit_content._0) (StyleGenericTrackBreadth<L>)(_0);
    result.tag = Tag::FitContent;
    return result;
  }

  bool IsFitContent() const {
    return tag == Tag::FitContent;
  }

  const StyleGenericTrackBreadth<L>& AsFitContent() const {
    MOZ_DIAGNOSTIC_ASSERT(IsFitContent());
    return fit_content._0;
  }

  bool operator==(const StyleGenericTrackSize& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Breadth: return breadth == other.breadth;
      case Tag::Minmax: return minmax == other.minmax;
      case Tag::FitContent: return fit_content == other.fit_content;

    }
    return true;
  }

  private:
  StyleGenericTrackSize() {

  }
  public:


  ~StyleGenericTrackSize() {
    switch (tag) {
      case Tag::Breadth: breadth.~StyleBreadth_Body(); break;
      case Tag::Minmax: minmax.~StyleMinmax_Body(); break;
      case Tag::FitContent: fit_content.~StyleFitContent_Body(); break;

    }
  }

  StyleGenericTrackSize(const StyleGenericTrackSize& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Breadth: ::new (&breadth) (StyleBreadth_Body)(other.breadth); break;
      case Tag::Minmax: ::new (&minmax) (StyleMinmax_Body)(other.minmax); break;
      case Tag::FitContent: ::new (&fit_content) (StyleFitContent_Body)(other.fit_content); break;

    }
  }
  StyleGenericTrackSize& operator=(const StyleGenericTrackSize& other) {
    if (this != &other) {
      this->~StyleGenericTrackSize();
      new (this) StyleGenericTrackSize(other);
    }
    return *this;
  }
  // Implemented in nsGridContainerFrame.cpp
  inline const StyleGenericTrackBreadth<L>& GetMin() const;
  inline const StyleGenericTrackBreadth<L>& GetMax() const;
};

/// The computed value of a grid `<track-size>`
using StyleTrackSize = StyleGenericTrackSize<StyleLengthPercentage>;

/// The computed value of a grid `<track-breadth>`
using StyleTrackBreadth = StyleGenericTrackBreadth<StyleLengthPercentage>;

/// A `<track-size>+`.
/// We use the empty slice as `auto`, and always parse `auto` as an empty slice.
/// This means it's impossible to have a slice containing only one auto item.
template<typename T>
using StyleGenericImplicitGridTracks = StyleOwnedSlice<T>;

/// The computed value of a grid `<track-size>+`
using StyleImplicitGridTracks = StyleGenericImplicitGridTracks<StyleTrackSize>;

/// An SVG paint value without the fallback.
///
/// Whereas the spec only allows PaintServer to have a fallback, Gecko lets the
/// context properties have a fallback as well.
template<typename C, typename U>
struct StyleGenericSVGPaintKind {
  enum class Tag : uint8_t {
    /// `none`
    None,
    /// `<color>`
    Color,
    /// `url(...)`
    PaintServer,
    /// `context-fill`
    ContextFill,
    /// `context-stroke`
    ContextStroke,
  };

  struct StyleColor_Body {
    C _0;

    bool operator==(const StyleColor_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StylePaintServer_Body {
    U _0;

    bool operator==(const StylePaintServer_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleColor_Body color;
    StylePaintServer_Body paint_server;
  };

  static StyleGenericSVGPaintKind None() {
    StyleGenericSVGPaintKind result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericSVGPaintKind Color(const C &_0) {
    StyleGenericSVGPaintKind result;
    ::new (&result.color._0) (C)(_0);
    result.tag = Tag::Color;
    return result;
  }

  bool IsColor() const {
    return tag == Tag::Color;
  }

  const C& AsColor() const {
    MOZ_DIAGNOSTIC_ASSERT(IsColor());
    return color._0;
  }

  static StyleGenericSVGPaintKind PaintServer(const U &_0) {
    StyleGenericSVGPaintKind result;
    ::new (&result.paint_server._0) (U)(_0);
    result.tag = Tag::PaintServer;
    return result;
  }

  bool IsPaintServer() const {
    return tag == Tag::PaintServer;
  }

  const U& AsPaintServer() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPaintServer());
    return paint_server._0;
  }

  static StyleGenericSVGPaintKind ContextFill() {
    StyleGenericSVGPaintKind result;
    result.tag = Tag::ContextFill;
    return result;
  }

  bool IsContextFill() const {
    return tag == Tag::ContextFill;
  }

  static StyleGenericSVGPaintKind ContextStroke() {
    StyleGenericSVGPaintKind result;
    result.tag = Tag::ContextStroke;
    return result;
  }

  bool IsContextStroke() const {
    return tag == Tag::ContextStroke;
  }

  bool operator==(const StyleGenericSVGPaintKind& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Color: return color == other.color;
      case Tag::PaintServer: return paint_server == other.paint_server;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericSVGPaintKind() {

  }
  public:


  ~StyleGenericSVGPaintKind() {
    switch (tag) {
      case Tag::Color: color.~StyleColor_Body(); break;
      case Tag::PaintServer: paint_server.~StylePaintServer_Body(); break;
      default: break;
    }
  }

  StyleGenericSVGPaintKind(const StyleGenericSVGPaintKind& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Color: ::new (&color) (StyleColor_Body)(other.color); break;
      case Tag::PaintServer: ::new (&paint_server) (StylePaintServer_Body)(other.paint_server); break;
      default: break;
    }
  }
  StyleGenericSVGPaintKind& operator=(const StyleGenericSVGPaintKind& other) {
    if (this != &other) {
      this->~StyleGenericSVGPaintKind();
      new (this) StyleGenericSVGPaintKind(other);
    }
    return *this;
  }
};

/// The fallback of an SVG paint server value.
template<typename C>
struct StyleGenericSVGPaintFallback {
  enum class Tag : uint8_t {
    /// The `none` keyword.
    None,
    /// A magic value that represents no fallback specified and serializes to
    /// the empty string.
    Unset,
    /// A color.
    Color,
  };

  struct StyleColor_Body {
    C _0;

    bool operator==(const StyleColor_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleColor_Body color;
  };

  static StyleGenericSVGPaintFallback None() {
    StyleGenericSVGPaintFallback result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericSVGPaintFallback Unset() {
    StyleGenericSVGPaintFallback result;
    result.tag = Tag::Unset;
    return result;
  }

  bool IsUnset() const {
    return tag == Tag::Unset;
  }

  static StyleGenericSVGPaintFallback Color(const C &_0) {
    StyleGenericSVGPaintFallback result;
    ::new (&result.color._0) (C)(_0);
    result.tag = Tag::Color;
    return result;
  }

  bool IsColor() const {
    return tag == Tag::Color;
  }

  const C& AsColor() const {
    MOZ_DIAGNOSTIC_ASSERT(IsColor());
    return color._0;
  }

  bool operator==(const StyleGenericSVGPaintFallback& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Color: return color == other.color;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericSVGPaintFallback() {

  }
  public:


  ~StyleGenericSVGPaintFallback() {
    switch (tag) {
      case Tag::Color: color.~StyleColor_Body(); break;
      default: break;
    }
  }

  StyleGenericSVGPaintFallback(const StyleGenericSVGPaintFallback& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Color: ::new (&color) (StyleColor_Body)(other.color); break;
      default: break;
    }
  }
  StyleGenericSVGPaintFallback& operator=(const StyleGenericSVGPaintFallback& other) {
    if (this != &other) {
      this->~StyleGenericSVGPaintFallback();
      new (this) StyleGenericSVGPaintFallback(other);
    }
    return *this;
  }
};

/// An SVG paint value
///
/// <https://www.w3.org/TR/SVG2/painting.html#SpecifyingPaint>
template<typename Color, typename Url>
struct StyleGenericSVGPaint {
  /// The paint source.
  StyleGenericSVGPaintKind<Color, Url> kind;
  /// The fallback color.
  StyleGenericSVGPaintFallback<Color> fallback;

  bool operator==(const StyleGenericSVGPaint& other) const {
    return kind == other.kind &&
           fallback == other.fallback;
  }
};

/// Computed SVG Paint value
using StyleSVGPaint = StyleGenericSVGPaint<StyleColor, StyleComputedUrl>;

/// Computed SVG Paint Kind value
using StyleSVGPaintKind = StyleGenericSVGPaintKind<StyleColor, StyleComputedUrl>;

/// The initial argument of the `repeat` function.
///
/// <https://drafts.csswg.org/css-grid/#typedef-track-repeat>
template<typename Integer>
struct StyleRepeatCount {
  enum class Tag : uint8_t {
    /// A positive integer. This is allowed only for `<track-repeat>` and `<fixed-repeat>`
    Number,
    /// An `<auto-fill>` keyword allowed only for `<auto-repeat>`
    AutoFill,
    /// An `<auto-fit>` keyword allowed only for `<auto-repeat>`
    AutoFit,
  };

  struct StyleNumber_Body {
    Integer _0;

    bool operator==(const StyleNumber_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleNumber_Body number;
  };

  static StyleRepeatCount Number(const Integer &_0) {
    StyleRepeatCount result;
    ::new (&result.number._0) (Integer)(_0);
    result.tag = Tag::Number;
    return result;
  }

  bool IsNumber() const {
    return tag == Tag::Number;
  }

  const Integer& AsNumber() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNumber());
    return number._0;
  }

  static StyleRepeatCount AutoFill() {
    StyleRepeatCount result;
    result.tag = Tag::AutoFill;
    return result;
  }

  bool IsAutoFill() const {
    return tag == Tag::AutoFill;
  }

  static StyleRepeatCount AutoFit() {
    StyleRepeatCount result;
    result.tag = Tag::AutoFit;
    return result;
  }

  bool IsAutoFit() const {
    return tag == Tag::AutoFit;
  }

  bool operator==(const StyleRepeatCount& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Number: return number == other.number;
      default: break;
    }
    return true;
  }

  private:
  StyleRepeatCount() {

  }
  public:


  ~StyleRepeatCount() {
    switch (tag) {
      case Tag::Number: number.~StyleNumber_Body(); break;
      default: break;
    }
  }

  StyleRepeatCount(const StyleRepeatCount& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Number: ::new (&number) (StyleNumber_Body)(other.number); break;
      default: break;
    }
  }
  StyleRepeatCount& operator=(const StyleRepeatCount& other) {
    if (this != &other) {
      this->~StyleRepeatCount();
      new (this) StyleRepeatCount(other);
    }
    return *this;
  }
};

/// The structure containing `<line-names>` and `<track-size>` values.
template<typename L, typename I>
struct StyleGenericTrackRepeat {
  /// The number of times for the value to be repeated (could also be `auto-fit` or `auto-fill`)
  StyleRepeatCount<I> count;
  /// `<line-names>` accompanying `<track_size>` values.
  ///
  /// If there's no `<line-names>`, then it's represented by an empty vector.
  /// For N `<track-size>` values, there will be N+1 `<line-names>`, and so this vector's
  /// length is always one value more than that of the `<track-size>`.
  StyleOwnedSlice<StyleOwnedSlice<StyleCustomIdent>> line_names;
  /// `<track-size>` values.
  StyleOwnedSlice<StyleGenericTrackSize<L>> track_sizes;

  bool operator==(const StyleGenericTrackRepeat& other) const {
    return count == other.count &&
           line_names == other.line_names &&
           track_sizes == other.track_sizes;
  }
};

/// Track list values. Can be <track-size> or <track-repeat>
template<typename LengthPercentage, typename Integer>
struct StyleGenericTrackListValue {
  enum class Tag : uint8_t {
    /// A <track-size> value.
    TrackSize,
    /// A <track-repeat> value.
    TrackRepeat,
  };

  struct StyleTrackSize_Body {
    StyleGenericTrackSize<LengthPercentage> _0;

    bool operator==(const StyleTrackSize_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleTrackRepeat_Body {
    StyleGenericTrackRepeat<LengthPercentage, Integer> _0;

    bool operator==(const StyleTrackRepeat_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleTrackSize_Body track_size;
    StyleTrackRepeat_Body track_repeat;
  };

  static StyleGenericTrackListValue TrackSize(const StyleGenericTrackSize<LengthPercentage> &_0) {
    StyleGenericTrackListValue result;
    ::new (&result.track_size._0) (StyleGenericTrackSize<LengthPercentage>)(_0);
    result.tag = Tag::TrackSize;
    return result;
  }

  bool IsTrackSize() const {
    return tag == Tag::TrackSize;
  }

  const StyleGenericTrackSize<LengthPercentage>& AsTrackSize() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTrackSize());
    return track_size._0;
  }

  static StyleGenericTrackListValue TrackRepeat(const StyleGenericTrackRepeat<LengthPercentage, Integer> &_0) {
    StyleGenericTrackListValue result;
    ::new (&result.track_repeat._0) (StyleGenericTrackRepeat<LengthPercentage, Integer>)(_0);
    result.tag = Tag::TrackRepeat;
    return result;
  }

  bool IsTrackRepeat() const {
    return tag == Tag::TrackRepeat;
  }

  const StyleGenericTrackRepeat<LengthPercentage, Integer>& AsTrackRepeat() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTrackRepeat());
    return track_repeat._0;
  }

  bool operator==(const StyleGenericTrackListValue& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::TrackSize: return track_size == other.track_size;
      case Tag::TrackRepeat: return track_repeat == other.track_repeat;

    }
    return true;
  }

  private:
  StyleGenericTrackListValue() {

  }
  public:


  ~StyleGenericTrackListValue() {
    switch (tag) {
      case Tag::TrackSize: track_size.~StyleTrackSize_Body(); break;
      case Tag::TrackRepeat: track_repeat.~StyleTrackRepeat_Body(); break;

    }
  }

  StyleGenericTrackListValue(const StyleGenericTrackListValue& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::TrackSize: ::new (&track_size) (StyleTrackSize_Body)(other.track_size); break;
      case Tag::TrackRepeat: ::new (&track_repeat) (StyleTrackRepeat_Body)(other.track_repeat); break;

    }
  }
  StyleGenericTrackListValue& operator=(const StyleGenericTrackListValue& other) {
    if (this != &other) {
      this->~StyleGenericTrackListValue();
      new (this) StyleGenericTrackListValue(other);
    }
    return *this;
  }
};

/// A grid `<track-list>` type.
///
/// <https://drafts.csswg.org/css-grid/#typedef-track-list>
template<typename LengthPercentage, typename Integer>
struct StyleGenericTrackList {
  /// The index in `values` where our `<auto-repeat>` value is, if in bounds.
  size_t auto_repeat_index;
  /// A vector of `<track-size> | <track-repeat>` values.
  StyleOwnedSlice<StyleGenericTrackListValue<LengthPercentage, Integer>> values;
  /// `<line-names>` accompanying `<track-size> | <track-repeat>` values.
  ///
  /// If there's no `<line-names>`, then it's represented by an empty vector.
  /// For N values, there will be N+1 `<line-names>`, and so this vector's
  /// length is always one value more than that of the `<track-size>`.
  StyleOwnedSlice<StyleOwnedSlice<StyleCustomIdent>> line_names;

  bool operator==(const StyleGenericTrackList& other) const {
    return auto_repeat_index == other.auto_repeat_index &&
           values == other.values &&
           line_names == other.line_names;
  }
};

/// The `<name-repeat>` for subgrids.
///
/// <name-repeat> = repeat( [ <integer [1,∞]> | auto-fill ], <line-names>+)
///
/// https://drafts.csswg.org/css-grid/#typedef-name-repeat
template<typename I>
struct StyleGenericNameRepeat {
  /// The number of times for the value to be repeated (could also be `auto-fill`).
  /// Note: `RepeatCount` accepts `auto-fit`, so we should reject it after parsing it.
  StyleRepeatCount<I> count;
  /// This represents `<line-names>+`. The length of the outer vector is at least one.
  StyleOwnedSlice<StyleOwnedSlice<StyleCustomIdent>> line_names;

  bool operator==(const StyleGenericNameRepeat& other) const {
    return count == other.count &&
           line_names == other.line_names;
  }
};

/// A single value for `<line-names>` or `<name-repeat>`.
template<typename I>
struct StyleGenericLineNameListValue {
  enum class Tag : uint8_t {
    /// `<line-names>`.
    LineNames,
    /// `<name-repeat>`.
    Repeat,
  };

  struct StyleLineNames_Body {
    StyleOwnedSlice<StyleCustomIdent> _0;

    bool operator==(const StyleLineNames_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleRepeat_Body {
    StyleGenericNameRepeat<I> _0;

    bool operator==(const StyleRepeat_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleLineNames_Body line_names;
    StyleRepeat_Body repeat;
  };

  static StyleGenericLineNameListValue LineNames(const StyleOwnedSlice<StyleCustomIdent> &_0) {
    StyleGenericLineNameListValue result;
    ::new (&result.line_names._0) (StyleOwnedSlice<StyleCustomIdent>)(_0);
    result.tag = Tag::LineNames;
    return result;
  }

  bool IsLineNames() const {
    return tag == Tag::LineNames;
  }

  const StyleOwnedSlice<StyleCustomIdent>& AsLineNames() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLineNames());
    return line_names._0;
  }

  static StyleGenericLineNameListValue Repeat(const StyleGenericNameRepeat<I> &_0) {
    StyleGenericLineNameListValue result;
    ::new (&result.repeat._0) (StyleGenericNameRepeat<I>)(_0);
    result.tag = Tag::Repeat;
    return result;
  }

  bool IsRepeat() const {
    return tag == Tag::Repeat;
  }

  const StyleGenericNameRepeat<I>& AsRepeat() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRepeat());
    return repeat._0;
  }

  bool operator==(const StyleGenericLineNameListValue& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::LineNames: return line_names == other.line_names;
      case Tag::Repeat: return repeat == other.repeat;

    }
    return true;
  }

  private:
  StyleGenericLineNameListValue() {

  }
  public:


  ~StyleGenericLineNameListValue() {
    switch (tag) {
      case Tag::LineNames: line_names.~StyleLineNames_Body(); break;
      case Tag::Repeat: repeat.~StyleRepeat_Body(); break;

    }
  }

  StyleGenericLineNameListValue(const StyleGenericLineNameListValue& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::LineNames: ::new (&line_names) (StyleLineNames_Body)(other.line_names); break;
      case Tag::Repeat: ::new (&repeat) (StyleRepeat_Body)(other.repeat); break;

    }
  }
  StyleGenericLineNameListValue& operator=(const StyleGenericLineNameListValue& other) {
    if (this != &other) {
      this->~StyleGenericLineNameListValue();
      new (this) StyleGenericLineNameListValue(other);
    }
    return *this;
  }
};

/// The `<line-name-list>` for subgrids.
///
/// <line-name-list> = [ <line-names> | <name-repeat> ]+
/// <name-repeat> = repeat( [ <integer [1,∞]> | auto-fill ], <line-names>+)
///
/// https://drafts.csswg.org/css-grid/#typedef-line-name-list
template<typename I>
struct StyleGenericLineNameList {
  /// The pre-computed length of line_names, without the length of repeat(auto-fill, ...).
  size_t expanded_line_names_length;
  /// The line name list.
  StyleOwnedSlice<StyleGenericLineNameListValue<I>> line_names;

  bool operator==(const StyleGenericLineNameList& other) const {
    return expanded_line_names_length == other.expanded_line_names_length &&
           line_names == other.line_names;
  }
};

/// Variants for `<grid-template-rows> | <grid-template-columns>`
template<typename L, typename I>
struct StyleGenericGridTemplateComponent {
  enum class Tag : uint8_t {
    /// `none` value.
    None,
    /// The grid `<track-list>`
    TrackList,
    /// A `subgrid <line-name-list>?`
    /// TODO: Support animations for this after subgrid is addressed in [grid-2] spec.
    Subgrid,
  };

  struct StyleTrackList_Body {
    StyleBox<StyleGenericTrackList<L, I>> _0;

    bool operator==(const StyleTrackList_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleSubgrid_Body {
    StyleBox<StyleGenericLineNameList<I>> _0;

    bool operator==(const StyleSubgrid_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleTrackList_Body track_list;
    StyleSubgrid_Body subgrid;
  };

  static StyleGenericGridTemplateComponent None() {
    StyleGenericGridTemplateComponent result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericGridTemplateComponent TrackList(const StyleBox<StyleGenericTrackList<L, I>> &_0) {
    StyleGenericGridTemplateComponent result;
    ::new (&result.track_list._0) (StyleBox<StyleGenericTrackList<L, I>>)(_0);
    result.tag = Tag::TrackList;
    return result;
  }

  bool IsTrackList() const {
    return tag == Tag::TrackList;
  }

  const StyleBox<StyleGenericTrackList<L, I>>& AsTrackList() const {
    MOZ_DIAGNOSTIC_ASSERT(IsTrackList());
    return track_list._0;
  }

  static StyleGenericGridTemplateComponent Subgrid(const StyleBox<StyleGenericLineNameList<I>> &_0) {
    StyleGenericGridTemplateComponent result;
    ::new (&result.subgrid._0) (StyleBox<StyleGenericLineNameList<I>>)(_0);
    result.tag = Tag::Subgrid;
    return result;
  }

  bool IsSubgrid() const {
    return tag == Tag::Subgrid;
  }

  const StyleBox<StyleGenericLineNameList<I>>& AsSubgrid() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSubgrid());
    return subgrid._0;
  }

  bool operator==(const StyleGenericGridTemplateComponent& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::TrackList: return track_list == other.track_list;
      case Tag::Subgrid: return subgrid == other.subgrid;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericGridTemplateComponent() {

  }
  public:


  ~StyleGenericGridTemplateComponent() {
    switch (tag) {
      case Tag::TrackList: track_list.~StyleTrackList_Body(); break;
      case Tag::Subgrid: subgrid.~StyleSubgrid_Body(); break;
      default: break;
    }
  }

  StyleGenericGridTemplateComponent(const StyleGenericGridTemplateComponent& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::TrackList: ::new (&track_list) (StyleTrackList_Body)(other.track_list); break;
      case Tag::Subgrid: ::new (&subgrid) (StyleSubgrid_Body)(other.subgrid); break;
      default: break;
    }
  }
  StyleGenericGridTemplateComponent& operator=(const StyleGenericGridTemplateComponent& other) {
    if (this != &other) {
      this->~StyleGenericGridTemplateComponent();
      new (this) StyleGenericGridTemplateComponent(other);
    }
    return *this;
  }
  inline Maybe<size_t> RepeatAutoIndex() const;
  inline const StyleGenericTrackRepeat<L, I>* GetRepeatAutoValue() const;
  inline bool HasRepeatAuto() const;
  inline Span<const StyleOwnedSlice<StyleCustomIdent>> LineNameLists() const;
  inline Span<const StyleGenericTrackListValue<L, I>> TrackListValues() const;
};

/// `<grid-template-rows> | <grid-template-columns>`
using StyleGridTemplateComponent = StyleGenericGridTemplateComponent<StyleLengthPercentage, StyleInteger>;

/// Computed value for the text-emphasis-style property
struct StyleTextEmphasisStyle {
  enum class Tag : uint8_t {
    /// [ <fill> || <shape> ]
    Keyword,
    /// `none`
    None,
    /// `<string>` (of which only the first grapheme cluster will be used).
    String,
  };

  struct StyleKeyword_Body {
    StyleTextEmphasisFillMode fill;
    StyleTextEmphasisShapeKeyword shape;

    bool operator==(const StyleKeyword_Body& other) const {
      return fill == other.fill &&
             shape == other.shape;
    }
  };

  struct StyleString_Body {
    StyleOwnedStr _0;

    bool operator==(const StyleString_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleKeyword_Body keyword;
    StyleString_Body string;
  };

  static StyleTextEmphasisStyle Keyword(const StyleTextEmphasisFillMode &fill,
                                        const StyleTextEmphasisShapeKeyword &shape) {
    StyleTextEmphasisStyle result;
    ::new (&result.keyword.fill) (StyleTextEmphasisFillMode)(fill);
    ::new (&result.keyword.shape) (StyleTextEmphasisShapeKeyword)(shape);
    result.tag = Tag::Keyword;
    return result;
  }

  bool IsKeyword() const {
    return tag == Tag::Keyword;
  }

  const StyleKeyword_Body& AsKeyword() const {
    MOZ_DIAGNOSTIC_ASSERT(IsKeyword());
    return keyword;
  }

  static StyleTextEmphasisStyle None() {
    StyleTextEmphasisStyle result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleTextEmphasisStyle String(const StyleOwnedStr &_0) {
    StyleTextEmphasisStyle result;
    ::new (&result.string._0) (StyleOwnedStr)(_0);
    result.tag = Tag::String;
    return result;
  }

  bool IsString() const {
    return tag == Tag::String;
  }

  const StyleOwnedStr& AsString() const {
    MOZ_DIAGNOSTIC_ASSERT(IsString());
    return string._0;
  }

  bool operator==(const StyleTextEmphasisStyle& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Keyword: return keyword == other.keyword;
      case Tag::String: return string == other.string;
      default: break;
    }
    return true;
  }

  private:
  StyleTextEmphasisStyle() {

  }
  public:


  ~StyleTextEmphasisStyle() {
    switch (tag) {
      case Tag::Keyword: keyword.~StyleKeyword_Body(); break;
      case Tag::String: string.~StyleString_Body(); break;
      default: break;
    }
  }

  StyleTextEmphasisStyle(const StyleTextEmphasisStyle& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Keyword: ::new (&keyword) (StyleKeyword_Body)(other.keyword); break;
      case Tag::String: ::new (&string) (StyleString_Body)(other.string); break;
      default: break;
    }
  }
  StyleTextEmphasisStyle& operator=(const StyleTextEmphasisStyle& other) {
    if (this != &other) {
      this->~StyleTextEmphasisStyle();
      new (this) StyleTextEmphasisStyle(other);
    }
    return *this;
  }
};

/// Values for text-emphasis-position:
/// <https://drafts.csswg.org/css-text-decor/#text-emphasis-position-property>
struct StyleTextEmphasisPosition {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleTextEmphasisPosition operator~() const {
    return StyleTextEmphasisPosition { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleTextEmphasisPosition operator|(const StyleTextEmphasisPosition& other) const {
    return StyleTextEmphasisPosition { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleTextEmphasisPosition& operator|=(const StyleTextEmphasisPosition& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleTextEmphasisPosition operator&(const StyleTextEmphasisPosition& other) const {
    return StyleTextEmphasisPosition { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleTextEmphasisPosition& operator&=(const StyleTextEmphasisPosition& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleTextEmphasisPosition operator^(const StyleTextEmphasisPosition& other) const {
    return StyleTextEmphasisPosition { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleTextEmphasisPosition& operator^=(const StyleTextEmphasisPosition& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleTextEmphasisPosition& other) const {
    return _0 == other._0;
  }
  static const StyleTextEmphasisPosition AUTO;
  static const StyleTextEmphasisPosition OVER;
  static const StyleTextEmphasisPosition UNDER;
  static const StyleTextEmphasisPosition LEFT;
  static const StyleTextEmphasisPosition RIGHT;
};
/// Automatically choose mark position based on language.
constexpr inline const StyleTextEmphasisPosition StyleTextEmphasisPosition::AUTO = StyleTextEmphasisPosition{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// Draw marks over the text in horizontal writing mode.
constexpr inline const StyleTextEmphasisPosition StyleTextEmphasisPosition::OVER = StyleTextEmphasisPosition{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// Draw marks under the text in horizontal writing mode.
constexpr inline const StyleTextEmphasisPosition StyleTextEmphasisPosition::UNDER = StyleTextEmphasisPosition{
  /* ._0 = */ (uint8_t)(1 << 2)
};
/// Draw marks to the left of the text in vertical writing mode.
constexpr inline const StyleTextEmphasisPosition StyleTextEmphasisPosition::LEFT = StyleTextEmphasisPosition{
  /* ._0 = */ (uint8_t)(1 << 3)
};
/// Draw marks to the right of the text in vertical writing mode.
constexpr inline const StyleTextEmphasisPosition StyleTextEmphasisPosition::RIGHT = StyleTextEmphasisPosition{
  /* ._0 = */ (uint8_t)(1 << 4)
};

/// Set of variant alternates
struct StyleVariantAlternates {
  enum class Tag : uint8_t {
    /// Enables display of stylistic alternates
    Stylistic,
    /// Enables display with stylistic sets
    Styleset,
    /// Enables display of specific character variants
    CharacterVariant,
    /// Enables display of swash glyphs
    Swash,
    /// Enables replacement of default glyphs with ornaments
    Ornaments,
    /// Enables display of alternate annotation forms
    Annotation,
    /// Enables display of historical forms
    HistoricalForms,
  };

  struct StyleStylistic_Body {
    StyleCustomIdent _0;

    bool operator==(const StyleStylistic_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleStyleset_Body {
    StyleOwnedSlice<StyleCustomIdent> _0;

    bool operator==(const StyleStyleset_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleCharacterVariant_Body {
    StyleOwnedSlice<StyleCustomIdent> _0;

    bool operator==(const StyleCharacterVariant_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleSwash_Body {
    StyleCustomIdent _0;

    bool operator==(const StyleSwash_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleOrnaments_Body {
    StyleCustomIdent _0;

    bool operator==(const StyleOrnaments_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleAnnotation_Body {
    StyleCustomIdent _0;

    bool operator==(const StyleAnnotation_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleStylistic_Body stylistic;
    StyleStyleset_Body styleset;
    StyleCharacterVariant_Body character_variant;
    StyleSwash_Body swash;
    StyleOrnaments_Body ornaments;
    StyleAnnotation_Body annotation;
  };

  static StyleVariantAlternates Stylistic(const StyleCustomIdent &_0) {
    StyleVariantAlternates result;
    ::new (&result.stylistic._0) (StyleCustomIdent)(_0);
    result.tag = Tag::Stylistic;
    return result;
  }

  bool IsStylistic() const {
    return tag == Tag::Stylistic;
  }

  const StyleCustomIdent& AsStylistic() const {
    MOZ_DIAGNOSTIC_ASSERT(IsStylistic());
    return stylistic._0;
  }

  static StyleVariantAlternates Styleset(const StyleOwnedSlice<StyleCustomIdent> &_0) {
    StyleVariantAlternates result;
    ::new (&result.styleset._0) (StyleOwnedSlice<StyleCustomIdent>)(_0);
    result.tag = Tag::Styleset;
    return result;
  }

  bool IsStyleset() const {
    return tag == Tag::Styleset;
  }

  const StyleOwnedSlice<StyleCustomIdent>& AsStyleset() const {
    MOZ_DIAGNOSTIC_ASSERT(IsStyleset());
    return styleset._0;
  }

  static StyleVariantAlternates CharacterVariant(const StyleOwnedSlice<StyleCustomIdent> &_0) {
    StyleVariantAlternates result;
    ::new (&result.character_variant._0) (StyleOwnedSlice<StyleCustomIdent>)(_0);
    result.tag = Tag::CharacterVariant;
    return result;
  }

  bool IsCharacterVariant() const {
    return tag == Tag::CharacterVariant;
  }

  const StyleOwnedSlice<StyleCustomIdent>& AsCharacterVariant() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCharacterVariant());
    return character_variant._0;
  }

  static StyleVariantAlternates Swash(const StyleCustomIdent &_0) {
    StyleVariantAlternates result;
    ::new (&result.swash._0) (StyleCustomIdent)(_0);
    result.tag = Tag::Swash;
    return result;
  }

  bool IsSwash() const {
    return tag == Tag::Swash;
  }

  const StyleCustomIdent& AsSwash() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSwash());
    return swash._0;
  }

  static StyleVariantAlternates Ornaments(const StyleCustomIdent &_0) {
    StyleVariantAlternates result;
    ::new (&result.ornaments._0) (StyleCustomIdent)(_0);
    result.tag = Tag::Ornaments;
    return result;
  }

  bool IsOrnaments() const {
    return tag == Tag::Ornaments;
  }

  const StyleCustomIdent& AsOrnaments() const {
    MOZ_DIAGNOSTIC_ASSERT(IsOrnaments());
    return ornaments._0;
  }

  static StyleVariantAlternates Annotation(const StyleCustomIdent &_0) {
    StyleVariantAlternates result;
    ::new (&result.annotation._0) (StyleCustomIdent)(_0);
    result.tag = Tag::Annotation;
    return result;
  }

  bool IsAnnotation() const {
    return tag == Tag::Annotation;
  }

  const StyleCustomIdent& AsAnnotation() const {
    MOZ_DIAGNOSTIC_ASSERT(IsAnnotation());
    return annotation._0;
  }

  static StyleVariantAlternates HistoricalForms() {
    StyleVariantAlternates result;
    result.tag = Tag::HistoricalForms;
    return result;
  }

  bool IsHistoricalForms() const {
    return tag == Tag::HistoricalForms;
  }

  bool operator==(const StyleVariantAlternates& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Stylistic: return stylistic == other.stylistic;
      case Tag::Styleset: return styleset == other.styleset;
      case Tag::CharacterVariant: return character_variant == other.character_variant;
      case Tag::Swash: return swash == other.swash;
      case Tag::Ornaments: return ornaments == other.ornaments;
      case Tag::Annotation: return annotation == other.annotation;
      default: break;
    }
    return true;
  }

  private:
  StyleVariantAlternates() {

  }
  public:


  ~StyleVariantAlternates() {
    switch (tag) {
      case Tag::Stylistic: stylistic.~StyleStylistic_Body(); break;
      case Tag::Styleset: styleset.~StyleStyleset_Body(); break;
      case Tag::CharacterVariant: character_variant.~StyleCharacterVariant_Body(); break;
      case Tag::Swash: swash.~StyleSwash_Body(); break;
      case Tag::Ornaments: ornaments.~StyleOrnaments_Body(); break;
      case Tag::Annotation: annotation.~StyleAnnotation_Body(); break;
      default: break;
    }
  }

  StyleVariantAlternates(const StyleVariantAlternates& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Stylistic: ::new (&stylistic) (StyleStylistic_Body)(other.stylistic); break;
      case Tag::Styleset: ::new (&styleset) (StyleStyleset_Body)(other.styleset); break;
      case Tag::CharacterVariant: ::new (&character_variant) (StyleCharacterVariant_Body)(other.character_variant); break;
      case Tag::Swash: ::new (&swash) (StyleSwash_Body)(other.swash); break;
      case Tag::Ornaments: ::new (&ornaments) (StyleOrnaments_Body)(other.ornaments); break;
      case Tag::Annotation: ::new (&annotation) (StyleAnnotation_Body)(other.annotation); break;
      default: break;
    }
  }
  StyleVariantAlternates& operator=(const StyleVariantAlternates& other) {
    if (this != &other) {
      this->~StyleVariantAlternates();
      new (this) StyleVariantAlternates(other);
    }
    return *this;
  }
};

/// List of Variant Alternates
using StyleFontVariantAlternates = StyleOwnedSlice<StyleVariantAlternates>;

/// The specified value is tree `PaintOrder` values packed into the
/// bitfields below, as a six-bit field, of 3 two-bit pairs
///
/// Each pair can be set to FILL, STROKE, or MARKERS
/// Lowest significant bit pairs are highest priority.
///  `normal` is the empty bitfield. The three pairs are
/// never zero in any case other than `normal`.
///
/// Higher priority values, i.e. the values specified first,
/// will be painted first (and may be covered by paintings of lower priority)
using StyleSVGPaintOrder = uint8_t;

/// A clip rect for clip and image-region
template<typename LengthOrAuto>
struct StyleGenericClipRect {
  LengthOrAuto top;
  LengthOrAuto right;
  LengthOrAuto bottom;
  LengthOrAuto left;

  bool operator==(const StyleGenericClipRect& other) const {
    return top == other.top &&
           right == other.right &&
           bottom == other.bottom &&
           left == other.left;
  }
  // Get the layout rect, replacing auto right / bottom values for aAutoSize.
  inline nsRect ToLayoutRect(nscoord aAutoSize = NS_MAXSIZE) const;
};

/// rect(...) | auto
using StyleClipRect = StyleGenericClipRect<StyleLengthOrAuto>;

/// Either a clip-rect or `auto`.
template<typename R>
struct StyleGenericClipRectOrAuto {
  enum class Tag : uint8_t {
    Auto,
    Rect,
  };

  struct StyleRect_Body {
    R _0;

    bool operator==(const StyleRect_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleRect_Body rect;
  };

  static StyleGenericClipRectOrAuto Auto() {
    StyleGenericClipRectOrAuto result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleGenericClipRectOrAuto Rect(const R &_0) {
    StyleGenericClipRectOrAuto result;
    ::new (&result.rect._0) (R)(_0);
    result.tag = Tag::Rect;
    return result;
  }

  bool IsRect() const {
    return tag == Tag::Rect;
  }

  const R& AsRect() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRect());
    return rect._0;
  }

  bool operator==(const StyleGenericClipRectOrAuto& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Rect: return rect == other.rect;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericClipRectOrAuto() {

  }
  public:


  ~StyleGenericClipRectOrAuto() {
    switch (tag) {
      case Tag::Rect: rect.~StyleRect_Body(); break;
      default: break;
    }
  }

  StyleGenericClipRectOrAuto(const StyleGenericClipRectOrAuto& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Rect: ::new (&rect) (StyleRect_Body)(other.rect); break;
      default: break;
    }
  }
  StyleGenericClipRectOrAuto& operator=(const StyleGenericClipRectOrAuto& other) {
    if (this != &other) {
      this->~StyleGenericClipRectOrAuto();
      new (this) StyleGenericClipRectOrAuto(other);
    }
    return *this;
  }
};

/// rect(...) | auto
using StyleClipRectOrAuto = StyleGenericClipRectOrAuto<StyleClipRect>;

/// A name / value pair for counters.
template<typename Integer>
struct StyleGenericCounterPair {
  /// The name of the counter.
  StyleCustomIdent name;
  /// The value of the counter / increment / etc.
  Integer value;
  /// If true, then this represents `reversed(name)`.
  /// NOTE: It can only be true on `counter-reset` values.
  bool is_reversed;

  bool operator==(const StyleGenericCounterPair& other) const {
    return name == other.name &&
           value == other.value &&
           is_reversed == other.is_reversed;
  }
};

/// A generic value for lists of counters.
///
/// Keyword `none` is represented by an empty vector.
template<typename I>
using StyleGenericCounters = StyleOwnedSlice<StyleGenericCounterPair<I>>;

/// A generic value for the `counter-reset` property.
template<typename I>
using StyleGenericCounterReset = StyleGenericCounters<I>;

/// A computed value for the `counter-reset` property.
using StyleCounterReset = StyleGenericCounterReset<int32_t>;

/// A generic value for the `counter-set` property.
template<typename I>
using StyleGenericCounterSet = StyleGenericCounters<I>;

/// A computed value for the `counter-set` property.
using StyleCounterSet = StyleGenericCounterSet<int32_t>;

/// A generic value for the `counter-increment` property.
template<typename I>
using StyleGenericCounterIncrement = StyleGenericCounters<I>;

/// A computed value for the `counter-increment` property.
using StyleCounterIncrement = StyleGenericCounterIncrement<int32_t>;

/// An image or a color. `cross-fade` takes either when blending
/// images together.
template<typename I, typename C>
struct StyleGenericCrossFadeImage {
  enum class Tag : uint8_t {
    /// A boxed image value. Boxing provides indirection so images can
    /// be cross-fades and cross-fades can be images.
    Image,
    /// A color value.
    Color,
  };

  struct StyleImage_Body {
    I _0;

    bool operator==(const StyleImage_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleColor_Body {
    C _0;

    bool operator==(const StyleColor_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleImage_Body image;
    StyleColor_Body color;
  };

  static StyleGenericCrossFadeImage Image(const I &_0) {
    StyleGenericCrossFadeImage result;
    ::new (&result.image._0) (I)(_0);
    result.tag = Tag::Image;
    return result;
  }

  bool IsImage() const {
    return tag == Tag::Image;
  }

  const I& AsImage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsImage());
    return image._0;
  }

  static StyleGenericCrossFadeImage Color(const C &_0) {
    StyleGenericCrossFadeImage result;
    ::new (&result.color._0) (C)(_0);
    result.tag = Tag::Color;
    return result;
  }

  bool IsColor() const {
    return tag == Tag::Color;
  }

  const C& AsColor() const {
    MOZ_DIAGNOSTIC_ASSERT(IsColor());
    return color._0;
  }

  bool operator==(const StyleGenericCrossFadeImage& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Image: return image == other.image;
      case Tag::Color: return color == other.color;

    }
    return true;
  }

  private:
  StyleGenericCrossFadeImage() {

  }
  public:


  ~StyleGenericCrossFadeImage() {
    switch (tag) {
      case Tag::Image: image.~StyleImage_Body(); break;
      case Tag::Color: color.~StyleColor_Body(); break;

    }
  }

  StyleGenericCrossFadeImage(const StyleGenericCrossFadeImage& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Image: ::new (&image) (StyleImage_Body)(other.image); break;
      case Tag::Color: ::new (&color) (StyleColor_Body)(other.color); break;

    }
  }
  StyleGenericCrossFadeImage& operator=(const StyleGenericCrossFadeImage& other) {
    if (this != &other) {
      this->~StyleGenericCrossFadeImage();
      new (this) StyleGenericCrossFadeImage(other);
    }
    return *this;
  }
};

/// An optional percent and a cross fade image.
template<typename Image, typename Color, typename Percentage>
struct StyleGenericCrossFadeElement {
  /// The percent of the final image that `image` will be.
  StyleOptional<Percentage> percent;
  /// A color or image that will be blended when cross-fade is
  /// evaluated.
  StyleGenericCrossFadeImage<Image, Color> image;

  bool operator==(const StyleGenericCrossFadeElement& other) const {
    return percent == other.percent &&
           image == other.image;
  }
};

/// <https://drafts.csswg.org/css-images-4/#cross-fade-function>
template<typename Image, typename Color, typename Percentage>
struct StyleGenericCrossFade {
  /// All of the image percent pairings passed as arguments to
  /// cross-fade.
  StyleOwnedSlice<StyleGenericCrossFadeElement<Image, Color, Percentage>> elements;

  bool operator==(const StyleGenericCrossFade& other) const {
    return elements == other.elements;
  }
};

/// An optional percent and a cross fade image.
template<typename Image, typename Resolution>
struct StyleGenericImageSetItem {
  /// `<image>`. `<string>` is converted to `Image::Url` at parse time.
  Image image;
  /// The `<resolution>`.
  ///
  /// TODO: Skip serialization if it is 1x.
  Resolution resolution;
  /// The `type(<string>)`
  /// (Optional) Specify the image's MIME type
  StyleOwnedStr mime_type;
  /// True if mime_type has been specified
  bool has_mime_type;

  bool operator==(const StyleGenericImageSetItem& other) const {
    return image == other.image &&
           resolution == other.resolution &&
           mime_type == other.mime_type &&
           has_mime_type == other.has_mime_type;
  }
};

/// https://drafts.csswg.org/css-images-4/#image-set-notation
template<typename Image, typename Resolution>
struct StyleGenericImageSet {
  /// The index of the selected candidate. usize::MAX for specified values or invalid images.
  size_t selected_index;
  /// All of the image and resolution pairs.
  StyleOwnedSlice<StyleGenericImageSetItem<Image, Resolution>> items;

  bool operator==(const StyleGenericImageSet& other) const {
    return selected_index == other.selected_index &&
           items == other.items;
  }
};

/// A light-dark(<light>, <dark>) function.
template<typename T>
struct StyleGenericLightDark {
  /// The value returned when using a light theme.
  T light;
  /// The value returned when using a dark theme.
  T dark;

  bool operator==(const StyleGenericLightDark& other) const {
    return light == other.light &&
           dark == other.dark;
  }
};

/// An `<image> | none` value.
///
/// https://drafts.csswg.org/css-images/#image-values
template<typename G, typename ImageUrl, typename Color, typename Percentage, typename Resolution>
struct StyleGenericImage {
  enum class Tag : uint8_t {
    /// `none` variant.
    None,
    /// A `<url()>` image.
    Url,
    /// A `<gradient>` image.  Gradients are rather large, and not nearly as
    /// common as urls, so we box them here to keep the size of this enum sane.
    Gradient,
#if defined(CBINDGEN_IS_GECKO)
    /// A `-moz-element(# <element-id>)`
    Element,
#endif
#if defined(CBINDGEN_IS_GECKO)
    /// A `-moz-symbolic-icon(<icon-id>)`
    /// NOTE(emilio): #[css(skip)] only really affects SpecifiedValueInfo, which we want because
    /// this is chrome-only.
    MozSymbolicIcon,
#endif
#if defined(CBINDGEN_IS_SERVO)
    /// A paint worklet image.
    /// <https://drafts.css-houdini.org/css-paint-api/>
    PaintWorklet,
#endif
    /// A `<cross-fade()>` image. Storing this directly inside of
    /// GenericImage increases the size by 8 bytes so we box it here
    /// and store images directly inside of cross-fade instead of
    /// boxing them there.
    CrossFade,
    /// An `image-set()` function.
    ImageSet,
    /// A `light-dark()` function.
    LightDark,
    /// An `image(<color>)` function.
    Image,
  };

  struct StyleUrl_Body {
    ImageUrl _0;

    bool operator==(const StyleUrl_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleGradient_Body {
    StyleBox<G> _0;

    bool operator==(const StyleGradient_Body& other) const {
      return _0 == other._0;
    }
  };

#if defined(CBINDGEN_IS_GECKO)
  struct StyleElement_Body {
    StyleAtom _0;

    bool operator==(const StyleElement_Body& other) const {
      return _0 == other._0;
    }
  };
#endif

#if defined(CBINDGEN_IS_GECKO)
  struct StyleMozSymbolicIcon_Body {
    StyleAtom _0;

    bool operator==(const StyleMozSymbolicIcon_Body& other) const {
      return _0 == other._0;
    }
  };
#endif

#if defined(CBINDGEN_IS_SERVO)
  struct StylePaintWorklet_Body {
    StyleBox<StylePaintWorklet> _0;

    bool operator==(const StylePaintWorklet_Body& other) const {
      return _0 == other._0;
    }
  };
#endif

  struct StyleCrossFade_Body {
    StyleBox<StyleGenericCrossFade<StyleGenericImage, Color, Percentage>> _0;

    bool operator==(const StyleCrossFade_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleImageSet_Body {
    StyleBox<StyleGenericImageSet<StyleGenericImage, Resolution>> _0;

    bool operator==(const StyleImageSet_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleLightDark_Body {
    StyleBox<StyleGenericLightDark<StyleGenericImage>> _0;

    bool operator==(const StyleLightDark_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleImage_Body {
    StyleBox<Color> _0;

    bool operator==(const StyleImage_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleUrl_Body url;
    StyleGradient_Body gradient;
#if defined(CBINDGEN_IS_GECKO)
    StyleElement_Body element;
#endif
#if defined(CBINDGEN_IS_GECKO)
    StyleMozSymbolicIcon_Body moz_symbolic_icon;
#endif
#if defined(CBINDGEN_IS_SERVO)
    StylePaintWorklet_Body paint_worklet;
#endif
    StyleCrossFade_Body cross_fade;
    StyleImageSet_Body image_set;
    StyleLightDark_Body light_dark;
    StyleImage_Body image;
  };

  static StyleGenericImage None() {
    StyleGenericImage result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericImage Url(const ImageUrl &_0) {
    StyleGenericImage result;
    ::new (&result.url._0) (ImageUrl)(_0);
    result.tag = Tag::Url;
    return result;
  }

  bool IsUrl() const {
    return tag == Tag::Url;
  }

  const ImageUrl& AsUrl() const {
    MOZ_DIAGNOSTIC_ASSERT(IsUrl());
    return url._0;
  }

  static StyleGenericImage Gradient(const StyleBox<G> &_0) {
    StyleGenericImage result;
    ::new (&result.gradient._0) (StyleBox<G>)(_0);
    result.tag = Tag::Gradient;
    return result;
  }

  bool IsGradient() const {
    return tag == Tag::Gradient;
  }

  const StyleBox<G>& AsGradient() const {
    MOZ_DIAGNOSTIC_ASSERT(IsGradient());
    return gradient._0;
  }

#if defined(CBINDGEN_IS_GECKO)
  static StyleGenericImage Element(const StyleAtom &_0) {
    StyleGenericImage result;
    ::new (&result.element._0) (StyleAtom)(_0);
    result.tag = Tag::Element;
    return result;
  }

  bool IsElement() const {
    return tag == Tag::Element;
  }

  const StyleAtom& AsElement() const {
    MOZ_DIAGNOSTIC_ASSERT(IsElement());
    return element._0;
  }
#endif

#if defined(CBINDGEN_IS_GECKO)
  static StyleGenericImage MozSymbolicIcon(const StyleAtom &_0) {
    StyleGenericImage result;
    ::new (&result.moz_symbolic_icon._0) (StyleAtom)(_0);
    result.tag = Tag::MozSymbolicIcon;
    return result;
  }

  bool IsMozSymbolicIcon() const {
    return tag == Tag::MozSymbolicIcon;
  }

  const StyleAtom& AsMozSymbolicIcon() const {
    MOZ_DIAGNOSTIC_ASSERT(IsMozSymbolicIcon());
    return moz_symbolic_icon._0;
  }
#endif

#if defined(CBINDGEN_IS_SERVO)
  static StyleGenericImage PaintWorklet(const StyleBox<StylePaintWorklet> &_0) {
    StyleGenericImage result;
    ::new (&result.paint_worklet._0) (StyleBox<StylePaintWorklet>)(_0);
    result.tag = Tag::PaintWorklet;
    return result;
  }

  bool IsPaintWorklet() const {
    return tag == Tag::PaintWorklet;
  }

  const StyleBox<StylePaintWorklet>& AsPaintWorklet() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPaintWorklet());
    return paint_worklet._0;
  }
#endif

  static StyleGenericImage CrossFade(const StyleBox<StyleGenericCrossFade<StyleGenericImage, Color, Percentage>> &_0) {
    StyleGenericImage result;
    ::new (&result.cross_fade._0) (StyleBox<StyleGenericCrossFade<StyleGenericImage, Color, Percentage>>)(_0);
    result.tag = Tag::CrossFade;
    return result;
  }

  bool IsCrossFade() const {
    return tag == Tag::CrossFade;
  }

  const StyleBox<StyleGenericCrossFade<StyleGenericImage, Color, Percentage>>& AsCrossFade() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCrossFade());
    return cross_fade._0;
  }

  static StyleGenericImage ImageSet(const StyleBox<StyleGenericImageSet<StyleGenericImage, Resolution>> &_0) {
    StyleGenericImage result;
    ::new (&result.image_set._0) (StyleBox<StyleGenericImageSet<StyleGenericImage, Resolution>>)(_0);
    result.tag = Tag::ImageSet;
    return result;
  }

  bool IsImageSet() const {
    return tag == Tag::ImageSet;
  }

  const StyleBox<StyleGenericImageSet<StyleGenericImage, Resolution>>& AsImageSet() const {
    MOZ_DIAGNOSTIC_ASSERT(IsImageSet());
    return image_set._0;
  }

  static StyleGenericImage LightDark(const StyleBox<StyleGenericLightDark<StyleGenericImage>> &_0) {
    StyleGenericImage result;
    ::new (&result.light_dark._0) (StyleBox<StyleGenericLightDark<StyleGenericImage>>)(_0);
    result.tag = Tag::LightDark;
    return result;
  }

  bool IsLightDark() const {
    return tag == Tag::LightDark;
  }

  const StyleBox<StyleGenericLightDark<StyleGenericImage>>& AsLightDark() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLightDark());
    return light_dark._0;
  }

  static StyleGenericImage Image(const StyleBox<Color> &_0) {
    StyleGenericImage result;
    ::new (&result.image._0) (StyleBox<Color>)(_0);
    result.tag = Tag::Image;
    return result;
  }

  bool IsImage() const {
    return tag == Tag::Image;
  }

  const StyleBox<Color>& AsImage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsImage());
    return image._0;
  }

  bool operator==(const StyleGenericImage& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Url: return url == other.url;
      case Tag::Gradient: return gradient == other.gradient;
#if defined(CBINDGEN_IS_GECKO)
      case Tag::Element: return element == other.element;
#endif
#if defined(CBINDGEN_IS_GECKO)
      case Tag::MozSymbolicIcon: return moz_symbolic_icon == other.moz_symbolic_icon;
#endif
#if defined(CBINDGEN_IS_SERVO)
      case Tag::PaintWorklet: return paint_worklet == other.paint_worklet;
#endif
      case Tag::CrossFade: return cross_fade == other.cross_fade;
      case Tag::ImageSet: return image_set == other.image_set;
      case Tag::LightDark: return light_dark == other.light_dark;
      case Tag::Image: return image == other.image;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericImage() {

  }
  public:


  ~StyleGenericImage() {
    switch (tag) {
      case Tag::Url: url.~StyleUrl_Body(); break;
      case Tag::Gradient: gradient.~StyleGradient_Body(); break;
#if defined(CBINDGEN_IS_GECKO)
      case Tag::Element: element.~StyleElement_Body(); break;
#endif
#if defined(CBINDGEN_IS_GECKO)
      case Tag::MozSymbolicIcon: moz_symbolic_icon.~StyleMozSymbolicIcon_Body(); break;
#endif
#if defined(CBINDGEN_IS_SERVO)
      case Tag::PaintWorklet: paint_worklet.~StylePaintWorklet_Body(); break;
#endif
      case Tag::CrossFade: cross_fade.~StyleCrossFade_Body(); break;
      case Tag::ImageSet: image_set.~StyleImageSet_Body(); break;
      case Tag::LightDark: light_dark.~StyleLightDark_Body(); break;
      case Tag::Image: image.~StyleImage_Body(); break;
      default: break;
    }
  }

  StyleGenericImage(const StyleGenericImage& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Url: ::new (&url) (StyleUrl_Body)(other.url); break;
      case Tag::Gradient: ::new (&gradient) (StyleGradient_Body)(other.gradient); break;
#if defined(CBINDGEN_IS_GECKO)
      case Tag::Element: ::new (&element) (StyleElement_Body)(other.element); break;
#endif
#if defined(CBINDGEN_IS_GECKO)
      case Tag::MozSymbolicIcon: ::new (&moz_symbolic_icon) (StyleMozSymbolicIcon_Body)(other.moz_symbolic_icon); break;
#endif
#if defined(CBINDGEN_IS_SERVO)
      case Tag::PaintWorklet: ::new (&paint_worklet) (StylePaintWorklet_Body)(other.paint_worklet); break;
#endif
      case Tag::CrossFade: ::new (&cross_fade) (StyleCrossFade_Body)(other.cross_fade); break;
      case Tag::ImageSet: ::new (&image_set) (StyleImageSet_Body)(other.image_set); break;
      case Tag::LightDark: ::new (&light_dark) (StyleLightDark_Body)(other.light_dark); break;
      case Tag::Image: ::new (&image) (StyleImage_Body)(other.image); break;
      default: break;
    }
  }
  StyleGenericImage& operator=(const StyleGenericImage& other) {
    if (this != &other) {
      this->~StyleGenericImage();
      new (this) StyleGenericImage(other);
    }
    return *this;
  }
 public:
  // Returns the intrinsic resolution of the image.
  //
  // The resolution is in dppx, and should be used to impact the intrinsic
  // size of the image.
  //
  // @param aStyleForZoom a style, if CSS zoom should be considered as well.
  ImageResolution GetResolution(const ComputedStyle* aStyleForZoom) const;

  // If this is an image-set(), the final image we've selected, otherwise it
  // returns *this.
  const StyleGenericImage& FinalImage() const;

  // Whether this image may have an image request associated with it.
  bool IsImageRequestType() const;

  // Gets the image request URL.
  const StyleComputedUrl* GetImageRequestURLValue() const;

  // Gets the image data of this image if it has any image request.
  imgRequestProxy* GetImageRequest() const;

  // Returns true if this image is fully loaded, and its size is calculated.
  // Always returns true if there's no image request involved and this image
  // is not `none`.
  bool IsComplete() const;

  // Returns true if this image has an available size and hasn't errored.
  // Always returns true if there's no image request involved and this image
  // is not `none`.
  bool IsSizeAvailable() const;

  // Returns true if the item is definitely opaque --- i.e., paints every
  // pixel within its bounds opaquely, and the bounds contains at least a pixel.
  bool IsOpaque() const;

  // Resolves the underlying image request if any.
  void ResolveImage(dom::Document&, const StyleGenericImage* aOld);

  // Returns whether this image has been resolved.
  bool IsResolved() const;
};

/// Computed values for an image according to CSS-IMAGES.
/// <https://drafts.csswg.org/css-images/#image-values>
using StyleImage = StyleGenericImage<StyleGradient, StyleComputedUrl, StyleColor, StylePercentage, StyleResolution>;

/// <https://drafts.csswg.org/css-counter-styles/#descdef-counter-style-symbols>
struct StyleSymbols {
  StyleArcSlice<StyleSymbol> _0;

  bool operator==(const StyleSymbols& other) const {
    return _0 == other._0;
  }
};

/// <https://drafts.csswg.org/css-counter-styles/#typedef-counter-style>
///
/// Note that 'none' is not a valid name, but we include this (along with String) for space
/// efficiency when storing list-style-type.
union StyleCounterStyle {
  enum class Tag : uint8_t {
    /// The 'none' value.
    None,
    /// `<counter-style-name>`
    Name,
    /// `symbols()`
    Symbols,
    /// A single string value, useful for `<list-style-type>`.
    String,
  };

  struct Name_Body {
    Tag tag;
    StyleCustomIdent _0;

    bool operator==(const Name_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Symbols_Body {
    Tag tag;
    /// The <symbols-type>, or symbolic if not specified.
    StyleSymbolsType ty;
    /// The actual symbols.
    StyleSymbols symbols;

    bool operator==(const Symbols_Body& other) const {
      return ty == other.ty &&
             symbols == other.symbols;
    }
  };

  struct String_Body {
    Tag tag;
    StyleAtomString _0;

    bool operator==(const String_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Name_Body name;
  Symbols_Body symbols;
  String_Body string;

  static StyleCounterStyle None() {
    StyleCounterStyle result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleCounterStyle Name(const StyleCustomIdent &_0) {
    StyleCounterStyle result;
    ::new (&result.name._0) (StyleCustomIdent)(_0);
    result.tag = Tag::Name;
    return result;
  }

  bool IsName() const {
    return tag == Tag::Name;
  }

  const StyleCustomIdent& AsName() const {
    MOZ_DIAGNOSTIC_ASSERT(IsName());
    return name._0;
  }

  static StyleCounterStyle Symbols(const StyleSymbolsType &ty,
                                   const StyleSymbols &symbols) {
    StyleCounterStyle result;
    ::new (&result.symbols.ty) (StyleSymbolsType)(ty);
    ::new (&result.symbols.symbols) (StyleSymbols)(symbols);
    result.tag = Tag::Symbols;
    return result;
  }

  bool IsSymbols() const {
    return tag == Tag::Symbols;
  }

  const Symbols_Body& AsSymbols() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSymbols());
    return symbols;
  }

  static StyleCounterStyle String(const StyleAtomString &_0) {
    StyleCounterStyle result;
    ::new (&result.string._0) (StyleAtomString)(_0);
    result.tag = Tag::String;
    return result;
  }

  bool IsString() const {
    return tag == Tag::String;
  }

  const StyleAtomString& AsString() const {
    MOZ_DIAGNOSTIC_ASSERT(IsString());
    return string._0;
  }

  bool operator==(const StyleCounterStyle& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Name: return name == other.name;
      case Tag::Symbols: return symbols == other.symbols;
      case Tag::String: return string == other.string;
      default: break;
    }
    return true;
  }

  private:
  StyleCounterStyle() {

  }
  public:


  ~StyleCounterStyle() {
    switch (tag) {
      case Tag::Name: name.~Name_Body(); break;
      case Tag::Symbols: symbols.~Symbols_Body(); break;
      case Tag::String: string.~String_Body(); break;
      default: break;
    }
  }

  StyleCounterStyle(const StyleCounterStyle& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Name: ::new (&name) (Name_Body)(other.name); break;
      case Tag::Symbols: ::new (&symbols) (Symbols_Body)(other.symbols); break;
      case Tag::String: ::new (&string) (String_Body)(other.string); break;
      default: break;
    }
  }
  StyleCounterStyle& operator=(const StyleCounterStyle& other) {
    if (this != &other) {
      this->~StyleCounterStyle();
      new (this) StyleCounterStyle(other);
    }
    return *this;
  }
};

/// Items for the `content` property.
template<typename I>
union StyleGenericContentItem {
  enum class Tag : uint8_t {
    /// Literal string content.
    String,
    /// `counter(name, style)`.
    Counter,
    /// `counters(name, separator, style)`.
    Counters,
    /// `open-quote`.
    OpenQuote,
    /// `close-quote`.
    CloseQuote,
    /// `no-open-quote`.
    NoOpenQuote,
    /// `no-close-quote`.
    NoCloseQuote,
#if defined(CBINDGEN_IS_GECKO)
    /// `-moz-alt-content`.
    MozAltContent,
#endif
#if defined(CBINDGEN_IS_GECKO)
    /// `-moz-label-content`.
    /// This is needed to make `accesskey` work for XUL labels. It's basically
    /// attr(value) otherwise.
    MozLabelContent,
#endif
    /// image-set(url) | url(url)
    Image,
  };

  struct String_Body {
    Tag tag;
    StyleOwnedStr _0;

    bool operator==(const String_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Counter_Body {
    Tag tag;
    StyleCustomIdent _0;
    StyleCounterStyle _1;

    bool operator==(const Counter_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct Counters_Body {
    Tag tag;
    StyleCustomIdent _0;
    StyleOwnedStr _1;
    StyleCounterStyle _2;

    bool operator==(const Counters_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1 &&
             _2 == other._2;
    }
  };

  struct Image_Body {
    Tag tag;
    I _0;

    bool operator==(const Image_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  String_Body string;
  Counter_Body counter;
  Counters_Body counters;
  Image_Body image;

  static StyleGenericContentItem String(const StyleOwnedStr &_0) {
    StyleGenericContentItem result;
    ::new (&result.string._0) (StyleOwnedStr)(_0);
    result.tag = Tag::String;
    return result;
  }

  bool IsString() const {
    return tag == Tag::String;
  }

  const StyleOwnedStr& AsString() const {
    MOZ_DIAGNOSTIC_ASSERT(IsString());
    return string._0;
  }

  static StyleGenericContentItem Counter(const StyleCustomIdent &_0,
                                         const StyleCounterStyle &_1) {
    StyleGenericContentItem result;
    ::new (&result.counter._0) (StyleCustomIdent)(_0);
    ::new (&result.counter._1) (StyleCounterStyle)(_1);
    result.tag = Tag::Counter;
    return result;
  }

  bool IsCounter() const {
    return tag == Tag::Counter;
  }

  const Counter_Body& AsCounter() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCounter());
    return counter;
  }

  static StyleGenericContentItem Counters(const StyleCustomIdent &_0,
                                          const StyleOwnedStr &_1,
                                          const StyleCounterStyle &_2) {
    StyleGenericContentItem result;
    ::new (&result.counters._0) (StyleCustomIdent)(_0);
    ::new (&result.counters._1) (StyleOwnedStr)(_1);
    ::new (&result.counters._2) (StyleCounterStyle)(_2);
    result.tag = Tag::Counters;
    return result;
  }

  bool IsCounters() const {
    return tag == Tag::Counters;
  }

  const Counters_Body& AsCounters() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCounters());
    return counters;
  }

  static StyleGenericContentItem OpenQuote() {
    StyleGenericContentItem result;
    result.tag = Tag::OpenQuote;
    return result;
  }

  bool IsOpenQuote() const {
    return tag == Tag::OpenQuote;
  }

  static StyleGenericContentItem CloseQuote() {
    StyleGenericContentItem result;
    result.tag = Tag::CloseQuote;
    return result;
  }

  bool IsCloseQuote() const {
    return tag == Tag::CloseQuote;
  }

  static StyleGenericContentItem NoOpenQuote() {
    StyleGenericContentItem result;
    result.tag = Tag::NoOpenQuote;
    return result;
  }

  bool IsNoOpenQuote() const {
    return tag == Tag::NoOpenQuote;
  }

  static StyleGenericContentItem NoCloseQuote() {
    StyleGenericContentItem result;
    result.tag = Tag::NoCloseQuote;
    return result;
  }

  bool IsNoCloseQuote() const {
    return tag == Tag::NoCloseQuote;
  }

#if defined(CBINDGEN_IS_GECKO)
  static StyleGenericContentItem MozAltContent() {
    StyleGenericContentItem result;
    result.tag = Tag::MozAltContent;
    return result;
  }

  bool IsMozAltContent() const {
    return tag == Tag::MozAltContent;
  }
#endif

#if defined(CBINDGEN_IS_GECKO)
  static StyleGenericContentItem MozLabelContent() {
    StyleGenericContentItem result;
    result.tag = Tag::MozLabelContent;
    return result;
  }

  bool IsMozLabelContent() const {
    return tag == Tag::MozLabelContent;
  }
#endif

  static StyleGenericContentItem Image(const I &_0) {
    StyleGenericContentItem result;
    ::new (&result.image._0) (I)(_0);
    result.tag = Tag::Image;
    return result;
  }

  bool IsImage() const {
    return tag == Tag::Image;
  }

  const I& AsImage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsImage());
    return image._0;
  }

  bool operator==(const StyleGenericContentItem& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::String: return string == other.string;
      case Tag::Counter: return counter == other.counter;
      case Tag::Counters: return counters == other.counters;
      case Tag::Image: return image == other.image;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericContentItem() {

  }
  public:


  ~StyleGenericContentItem() {
    switch (tag) {
      case Tag::String: string.~String_Body(); break;
      case Tag::Counter: counter.~Counter_Body(); break;
      case Tag::Counters: counters.~Counters_Body(); break;
      case Tag::Image: image.~Image_Body(); break;
      default: break;
    }
  }

  StyleGenericContentItem(const StyleGenericContentItem& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::String: ::new (&string) (String_Body)(other.string); break;
      case Tag::Counter: ::new (&counter) (Counter_Body)(other.counter); break;
      case Tag::Counters: ::new (&counters) (Counters_Body)(other.counters); break;
      case Tag::Image: ::new (&image) (Image_Body)(other.image); break;
      default: break;
    }
  }
  StyleGenericContentItem& operator=(const StyleGenericContentItem& other) {
    if (this != &other) {
      this->~StyleGenericContentItem();
      new (this) StyleGenericContentItem(other);
    }
    return *this;
  }
};

/// The non-normal, non-none values of the content property.
template<typename Image>
struct StyleGenericContentItems {
  /// The actual content items. Note that, past the alt marker, only some subset (strings,
  /// attr(), counter())
  CopyableTArray<StyleGenericContentItem<Image>> items;
  /// The index at which alt text starts, always non-zero. If equal to items.len(), no alt text
  /// exists.
  size_t alt_start;

  bool operator==(const StyleGenericContentItems& other) const {
    return items == other.items &&
           alt_start == other.alt_start;
  }
};

/// The specified value for the `content` property.
///
/// https://drafts.csswg.org/css-content/#propdef-content
template<typename Image>
union StyleGenericContent {
  enum class Tag : uint8_t {
    /// `normal` reserved keyword.
    Normal,
    /// `none` reserved keyword.
    None,
    /// Content items.
    Items,
  };

  struct Items_Body {
    Tag tag;
    StyleGenericContentItems<Image> _0;

    bool operator==(const Items_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Items_Body items;

  static StyleGenericContent Normal() {
    StyleGenericContent result;
    result.tag = Tag::Normal;
    return result;
  }

  bool IsNormal() const {
    return tag == Tag::Normal;
  }

  static StyleGenericContent None() {
    StyleGenericContent result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericContent Items(const StyleGenericContentItems<Image> &_0) {
    StyleGenericContent result;
    ::new (&result.items._0) (StyleGenericContentItems<Image>)(_0);
    result.tag = Tag::Items;
    return result;
  }

  bool IsItems() const {
    return tag == Tag::Items;
  }

  const StyleGenericContentItems<Image>& AsItems() const {
    MOZ_DIAGNOSTIC_ASSERT(IsItems());
    return items._0;
  }

  bool operator==(const StyleGenericContent& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Items: return items == other.items;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericContent() {

  }
  public:


  ~StyleGenericContent() {
    switch (tag) {
      case Tag::Items: items.~Items_Body(); break;
      default: break;
    }
  }

  StyleGenericContent(const StyleGenericContent& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Items: ::new (&items) (Items_Body)(other.items); break;
      default: break;
    }
  }
  StyleGenericContent& operator=(const StyleGenericContent& other) {
    if (this != &other) {
      this->~StyleGenericContent();
      new (this) StyleGenericContent(other);
    }
    return *this;
  }
};

/// A computed value for the `content` property.
using StyleContent = StyleGenericContent<StyleImage>;

/// A computed content item.
using StyleContentItem = StyleGenericContentItem<StyleImage>;

/// Shared value for the `align-content` and `justify-content` properties.
///
/// <https://drafts.csswg.org/css-align/#content-distribution>
/// <https://drafts.csswg.org/css-align/#propdef-align-content>
struct StyleContentDistribution {
  StyleAlignFlags primary;

  bool operator==(const StyleContentDistribution& other) const {
    return primary == other.primary;
  }
};

/// The specified value of the {align,justify}-self properties.
///
/// <https://drafts.csswg.org/css-align/#self-alignment>
/// <https://drafts.csswg.org/css-align/#propdef-align-self>
struct StyleSelfAlignment {
  StyleAlignFlags _0;

  bool operator==(const StyleSelfAlignment& other) const {
    return _0 == other._0;
  }
};

/// Value of the `align-items` and `justify-items` properties
///
/// <https://drafts.csswg.org/css-align/#propdef-align-items>
/// <https://drafts.csswg.org/css-align/#propdef-justify-items>
struct StyleItemPlacement {
  StyleAlignFlags _0;

  bool operator==(const StyleItemPlacement& other) const {
    return _0 == other._0;
  }
};

/// Value of the `justify-items` property
///
/// <https://drafts.csswg.org/css-align/#justify-items-property>
struct StyleJustifyItems {
  StyleItemPlacement _0;

  bool operator==(const StyleJustifyItems& other) const {
    return _0 == other._0;
  }
};

/// The computed value for the `justify-items` property.
///
/// Need to carry around both the specified and computed value to handle the
/// special legacy keyword without destroying style sharing.
///
/// In particular, `justify-items` is a reset property, so we ought to be able
/// to share its computed representation across elements as long as they match
/// the same rules. Except that it's not true if the specified value for
/// `justify-items` is `legacy` and the computed value of the parent has the
/// `legacy` modifier.
///
/// So instead of computing `legacy` "normally" looking at get_parent_position(),
/// marking it as uncacheable, we carry the specified value around and handle
/// the special case in `StyleAdjuster` instead, only when the result of the
/// computation would vary.
///
/// Note that we also need to special-case this property in matching.rs, in
/// order to properly handle changes to the legacy keyword... This all kinda
/// sucks :(.
///
/// See the discussion in https://bugzil.la/1384542.
struct StyleComputedJustifyItems {
  /// The specified value for the property. Can contain the bare `legacy`
  /// keyword.
  StyleJustifyItems specified;
  /// The computed value for the property. Cannot contain the bare `legacy`
  /// keyword, but note that it could contain it in combination with other
  /// keywords like `left`, `right` or `center`.
  StyleJustifyItems computed;

  bool operator==(const StyleComputedJustifyItems& other) const {
    return specified == other.specified &&
           computed == other.computed;
  }
};

/// <https://drafts.fxtf.org/css-masking-1/#typedef-geometry-box>
union StyleShapeGeometryBox {
  enum class Tag : uint8_t {
    /// Depending on which kind of element this style value applied on, the
    /// default value of the reference-box can be different.  For an HTML
    /// element, the default value of reference-box is border-box; for an SVG
    /// element, the default value is fill-box.  Since we can not determine the
    /// default value at parsing time, we keep this value to make a decision on
    /// it.
    ElementDependent,
    FillBox,
    StrokeBox,
    ViewBox,
    ShapeBox,
  };

  struct ShapeBox_Body {
    Tag tag;
    StyleShapeBox _0;

    bool operator==(const ShapeBox_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  ShapeBox_Body shape_box;

  static StyleShapeGeometryBox ElementDependent() {
    StyleShapeGeometryBox result;
    result.tag = Tag::ElementDependent;
    return result;
  }

  bool IsElementDependent() const {
    return tag == Tag::ElementDependent;
  }

  static StyleShapeGeometryBox FillBox() {
    StyleShapeGeometryBox result;
    result.tag = Tag::FillBox;
    return result;
  }

  bool IsFillBox() const {
    return tag == Tag::FillBox;
  }

  static StyleShapeGeometryBox StrokeBox() {
    StyleShapeGeometryBox result;
    result.tag = Tag::StrokeBox;
    return result;
  }

  bool IsStrokeBox() const {
    return tag == Tag::StrokeBox;
  }

  static StyleShapeGeometryBox ViewBox() {
    StyleShapeGeometryBox result;
    result.tag = Tag::ViewBox;
    return result;
  }

  bool IsViewBox() const {
    return tag == Tag::ViewBox;
  }

  static StyleShapeGeometryBox ShapeBox(const StyleShapeBox &_0) {
    StyleShapeGeometryBox result;
    ::new (&result.shape_box._0) (StyleShapeBox)(_0);
    result.tag = Tag::ShapeBox;
    return result;
  }

  bool IsShapeBox() const {
    return tag == Tag::ShapeBox;
  }

  const StyleShapeBox& AsShapeBox() const {
    MOZ_DIAGNOSTIC_ASSERT(IsShapeBox());
    return shape_box._0;
  }

  bool operator==(const StyleShapeGeometryBox& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::ShapeBox: return shape_box == other.shape_box;
      default: break;
    }
    return true;
  }

  private:
  StyleShapeGeometryBox() {

  }
  public:


  ~StyleShapeGeometryBox() {
    switch (tag) {
      case Tag::ShapeBox: shape_box.~ShapeBox_Body(); break;
      default: break;
    }
  }

  StyleShapeGeometryBox(const StyleShapeGeometryBox& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::ShapeBox: ::new (&shape_box) (ShapeBox_Body)(other.shape_box); break;
      default: break;
    }
  }
  StyleShapeGeometryBox& operator=(const StyleShapeGeometryBox& other) {
    if (this != &other) {
      this->~StyleShapeGeometryBox();
      new (this) StyleShapeGeometryBox(other);
    }
    return *this;
  }
};

/// A value for the `clip-path` property.
template<typename BasicShape, typename U>
union StyleGenericClipPath {
  enum class Tag : uint8_t {
    None,
    Url,
    Shape,
    Box,
  };

  struct Url_Body {
    Tag tag;
    U _0;

    bool operator==(const Url_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Shape_Body {
    Tag tag;
    StyleBox<BasicShape> _0;
    StyleShapeGeometryBox _1;

    bool operator==(const Shape_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct Box_Body {
    Tag tag;
    StyleShapeGeometryBox _0;

    bool operator==(const Box_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Url_Body url;
  Shape_Body shape;
  Box_Body box;

  static StyleGenericClipPath None() {
    StyleGenericClipPath result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericClipPath Url(const U &_0) {
    StyleGenericClipPath result;
    ::new (&result.url._0) (U)(_0);
    result.tag = Tag::Url;
    return result;
  }

  bool IsUrl() const {
    return tag == Tag::Url;
  }

  const U& AsUrl() const {
    MOZ_DIAGNOSTIC_ASSERT(IsUrl());
    return url._0;
  }

  static StyleGenericClipPath Shape(const StyleBox<BasicShape> &_0,
                                    const StyleShapeGeometryBox &_1) {
    StyleGenericClipPath result;
    ::new (&result.shape._0) (StyleBox<BasicShape>)(_0);
    ::new (&result.shape._1) (StyleShapeGeometryBox)(_1);
    result.tag = Tag::Shape;
    return result;
  }

  bool IsShape() const {
    return tag == Tag::Shape;
  }

  const Shape_Body& AsShape() const {
    MOZ_DIAGNOSTIC_ASSERT(IsShape());
    return shape;
  }

  static StyleGenericClipPath Box(const StyleShapeGeometryBox &_0) {
    StyleGenericClipPath result;
    ::new (&result.box._0) (StyleShapeGeometryBox)(_0);
    result.tag = Tag::Box;
    return result;
  }

  bool IsBox() const {
    return tag == Tag::Box;
  }

  const StyleShapeGeometryBox& AsBox() const {
    MOZ_DIAGNOSTIC_ASSERT(IsBox());
    return box._0;
  }

  bool operator==(const StyleGenericClipPath& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Url: return url == other.url;
      case Tag::Shape: return shape == other.shape;
      case Tag::Box: return box == other.box;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericClipPath() {

  }
  public:


  ~StyleGenericClipPath() {
    switch (tag) {
      case Tag::Url: url.~Url_Body(); break;
      case Tag::Shape: shape.~Shape_Body(); break;
      case Tag::Box: box.~Box_Body(); break;
      default: break;
    }
  }

  StyleGenericClipPath(const StyleGenericClipPath& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Url: ::new (&url) (Url_Body)(other.url); break;
      case Tag::Shape: ::new (&shape) (Shape_Body)(other.shape); break;
      case Tag::Box: ::new (&box) (Box_Body)(other.box); break;
      default: break;
    }
  }
  StyleGenericClipPath& operator=(const StyleGenericClipPath& other) {
    if (this != &other) {
      this->~StyleGenericClipPath();
      new (this) StyleGenericClipPath(other);
    }
    return *this;
  }
};

/// A computed `clip-path` value.
using StyleClipPath = StyleGenericClipPath<StyleBasicShape, StyleComputedUrl>;

/// A value for the `shape-outside` property.
template<typename BasicShape, typename I>
union StyleGenericShapeOutside {
  enum class Tag : uint8_t {
    None,
    Image,
    Shape,
    Box,
  };

  struct Image_Body {
    Tag tag;
    I _0;

    bool operator==(const Image_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Shape_Body {
    Tag tag;
    StyleBox<BasicShape> _0;
    StyleShapeBox _1;

    bool operator==(const Shape_Body& other) const {
      return _0 == other._0 &&
             _1 == other._1;
    }
  };

  struct Box_Body {
    Tag tag;
    StyleShapeBox _0;

    bool operator==(const Box_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  Image_Body image;
  Shape_Body shape;
  Box_Body box;

  static StyleGenericShapeOutside None() {
    StyleGenericShapeOutside result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StyleGenericShapeOutside Image(const I &_0) {
    StyleGenericShapeOutside result;
    ::new (&result.image._0) (I)(_0);
    result.tag = Tag::Image;
    return result;
  }

  bool IsImage() const {
    return tag == Tag::Image;
  }

  const I& AsImage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsImage());
    return image._0;
  }

  static StyleGenericShapeOutside Shape(const StyleBox<BasicShape> &_0,
                                        const StyleShapeBox &_1) {
    StyleGenericShapeOutside result;
    ::new (&result.shape._0) (StyleBox<BasicShape>)(_0);
    ::new (&result.shape._1) (StyleShapeBox)(_1);
    result.tag = Tag::Shape;
    return result;
  }

  bool IsShape() const {
    return tag == Tag::Shape;
  }

  const Shape_Body& AsShape() const {
    MOZ_DIAGNOSTIC_ASSERT(IsShape());
    return shape;
  }

  static StyleGenericShapeOutside Box(const StyleShapeBox &_0) {
    StyleGenericShapeOutside result;
    ::new (&result.box._0) (StyleShapeBox)(_0);
    result.tag = Tag::Box;
    return result;
  }

  bool IsBox() const {
    return tag == Tag::Box;
  }

  const StyleShapeBox& AsBox() const {
    MOZ_DIAGNOSTIC_ASSERT(IsBox());
    return box._0;
  }

  bool operator==(const StyleGenericShapeOutside& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Image: return image == other.image;
      case Tag::Shape: return shape == other.shape;
      case Tag::Box: return box == other.box;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericShapeOutside() {

  }
  public:


  ~StyleGenericShapeOutside() {
    switch (tag) {
      case Tag::Image: image.~Image_Body(); break;
      case Tag::Shape: shape.~Shape_Body(); break;
      case Tag::Box: box.~Box_Body(); break;
      default: break;
    }
  }

  StyleGenericShapeOutside(const StyleGenericShapeOutside& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Image: ::new (&image) (Image_Body)(other.image); break;
      case Tag::Shape: ::new (&shape) (Shape_Body)(other.shape); break;
      case Tag::Box: ::new (&box) (Box_Body)(other.box); break;
      default: break;
    }
  }
  StyleGenericShapeOutside& operator=(const StyleGenericShapeOutside& other) {
    if (this != &other) {
      this->~StyleGenericShapeOutside();
      new (this) StyleGenericShapeOutside(other);
    }
    return *this;
  }
};

/// A computed `shape-outside` value.
using StyleShapeOutside = StyleGenericShapeOutside<StyleBasicShape, StyleImage>;

/// Controls how the auto-placement algorithm works specifying exactly how auto-placed items
/// get flowed into the grid: [ row | column ] || dense
/// https://drafts.csswg.org/css-grid-2/#grid-auto-flow-property
struct StyleGridAutoFlow {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleGridAutoFlow operator~() const {
    return StyleGridAutoFlow { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleGridAutoFlow operator|(const StyleGridAutoFlow& other) const {
    return StyleGridAutoFlow { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleGridAutoFlow& operator|=(const StyleGridAutoFlow& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleGridAutoFlow operator&(const StyleGridAutoFlow& other) const {
    return StyleGridAutoFlow { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleGridAutoFlow& operator&=(const StyleGridAutoFlow& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleGridAutoFlow operator^(const StyleGridAutoFlow& other) const {
    return StyleGridAutoFlow { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleGridAutoFlow& operator^=(const StyleGridAutoFlow& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleGridAutoFlow& other) const {
    return _0 == other._0;
  }
  static const StyleGridAutoFlow ROW;
  static const StyleGridAutoFlow COLUMN;
  static const StyleGridAutoFlow DENSE;
};
/// 'row' - mutually exclusive with 'column'
constexpr inline const StyleGridAutoFlow StyleGridAutoFlow::ROW = StyleGridAutoFlow{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// 'column' - mutually exclusive with 'row'
constexpr inline const StyleGridAutoFlow StyleGridAutoFlow::COLUMN = StyleGridAutoFlow{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// 'dense'
constexpr inline const StyleGridAutoFlow StyleGridAutoFlow::DENSE = StyleGridAutoFlow{
  /* ._0 = */ (uint8_t)(1 << 2)
};

/// The specified and computed value of the `flex-wrap` property:
/// `nowrap | [ wrap | wrap-reverse ] || balance`
///
/// <https://drafts.csswg.org/css-flexbox-2/#flex-wrap-property>
struct StyleFlexWrap {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleFlexWrap operator~() const {
    return StyleFlexWrap { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleFlexWrap operator|(const StyleFlexWrap& other) const {
    return StyleFlexWrap { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleFlexWrap& operator|=(const StyleFlexWrap& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleFlexWrap operator&(const StyleFlexWrap& other) const {
    return StyleFlexWrap { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleFlexWrap& operator&=(const StyleFlexWrap& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleFlexWrap operator^(const StyleFlexWrap& other) const {
    return StyleFlexWrap { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleFlexWrap& operator^=(const StyleFlexWrap& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleFlexWrap& other) const {
    return _0 == other._0;
  }
  static const StyleFlexWrap NOWRAP;
  static const StyleFlexWrap WRAP;
  static const StyleFlexWrap WRAP_REVERSE;
  static const StyleFlexWrap BALANCE;
};
/// `nowrap`
constexpr inline const StyleFlexWrap StyleFlexWrap::NOWRAP = StyleFlexWrap{
  /* ._0 = */ (uint8_t)0
};
/// `wrap` - mutually exclusive with `wrap-reverse`
constexpr inline const StyleFlexWrap StyleFlexWrap::WRAP = StyleFlexWrap{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// `wrap-reverse` - mutually exclusive with `wrap`
constexpr inline const StyleFlexWrap StyleFlexWrap::WRAP_REVERSE = StyleFlexWrap{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// `balance`
constexpr inline const StyleFlexWrap StyleFlexWrap::BALANCE = StyleFlexWrap{
  /* ._0 = */ (uint8_t)(1 << 2)
};

/// A generic value for item of `image cursors`.
template<typename Image, typename Number>
struct StyleGenericCursorImage {
  /// The url to parse images from.
  Image image;
  /// Whether the image has a hotspot or not.
  bool has_hotspot;
  /// The x coordinate.
  Number hotspot_x;
  /// The y coordinate.
  Number hotspot_y;

  bool operator==(const StyleGenericCursorImage& other) const {
    return image == other.image &&
           has_hotspot == other.has_hotspot &&
           hotspot_x == other.hotspot_x &&
           hotspot_y == other.hotspot_y;
  }
};

/// A computed value for item of `image cursors`.
using StyleCursorImage = StyleGenericCursorImage<StyleImage, StyleNumber>;

/// A generic value for the `cursor` property.
///
/// https://drafts.csswg.org/css-ui/#cursor
template<typename Image>
struct StyleGenericCursor {
  /// The parsed images for the cursor.
  StyleOwnedSlice<Image> images;
  /// The kind of the cursor [default | help | ...].
  StyleCursorKind keyword;

  bool operator==(const StyleGenericCursor& other) const {
    return images == other.images &&
           keyword == other.keyword;
  }
};

/// A computed value for the `cursor` property.
using StyleCursor = StyleGenericCursor<StyleCursorImage>;

/// Generic value for stroke-dasharray.
template<typename L>
struct StyleGenericSVGStrokeDashArray {
  enum class Tag : uint8_t {
    /// `[ <length> | <percentage> | <number> ]#`
    Values,
    /// `context-value`
    ContextValue,
  };

  struct StyleValues_Body {
    StyleOwnedSlice<L> _0;

    bool operator==(const StyleValues_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleValues_Body values;
  };

  static StyleGenericSVGStrokeDashArray Values(const StyleOwnedSlice<L> &_0) {
    StyleGenericSVGStrokeDashArray result;
    ::new (&result.values._0) (StyleOwnedSlice<L>)(_0);
    result.tag = Tag::Values;
    return result;
  }

  bool IsValues() const {
    return tag == Tag::Values;
  }

  const StyleOwnedSlice<L>& AsValues() const {
    MOZ_DIAGNOSTIC_ASSERT(IsValues());
    return values._0;
  }

  static StyleGenericSVGStrokeDashArray ContextValue() {
    StyleGenericSVGStrokeDashArray result;
    result.tag = Tag::ContextValue;
    return result;
  }

  bool IsContextValue() const {
    return tag == Tag::ContextValue;
  }

  bool operator==(const StyleGenericSVGStrokeDashArray& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Values: return values == other.values;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericSVGStrokeDashArray() {

  }
  public:


  ~StyleGenericSVGStrokeDashArray() {
    switch (tag) {
      case Tag::Values: values.~StyleValues_Body(); break;
      default: break;
    }
  }

  StyleGenericSVGStrokeDashArray(const StyleGenericSVGStrokeDashArray& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Values: ::new (&values) (StyleValues_Body)(other.values); break;
      default: break;
    }
  }
  StyleGenericSVGStrokeDashArray& operator=(const StyleGenericSVGStrokeDashArray& other) {
    if (this != &other) {
      this->~StyleGenericSVGStrokeDashArray();
      new (this) StyleGenericSVGStrokeDashArray(other);
    }
    return *this;
  }
};

/// [ <length> | <percentage> | <number> ]# | context-value
using StyleSVGStrokeDashArray = StyleGenericSVGStrokeDashArray<StyleNonNegativeLengthPercentage>;

/// An SVG length value supports `context-value` in addition to length.
template<typename L>
struct StyleGenericSVGLength {
  enum class Tag : uint8_t {
    /// `<length> | <percentage> | <number>`
    LengthPercentage,
    /// `context-value`
    ContextValue,
  };

  struct StyleLengthPercentage_Body {
    L _0;

    bool operator==(const StyleLengthPercentage_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleLengthPercentage_Body length_percentage;
  };

  static StyleGenericSVGLength LengthPercentage(const L &_0) {
    StyleGenericSVGLength result;
    ::new (&result.length_percentage._0) (L)(_0);
    result.tag = Tag::LengthPercentage;
    return result;
  }

  bool IsLengthPercentage() const {
    return tag == Tag::LengthPercentage;
  }

  const L& AsLengthPercentage() const {
    MOZ_DIAGNOSTIC_ASSERT(IsLengthPercentage());
    return length_percentage._0;
  }

  static StyleGenericSVGLength ContextValue() {
    StyleGenericSVGLength result;
    result.tag = Tag::ContextValue;
    return result;
  }

  bool IsContextValue() const {
    return tag == Tag::ContextValue;
  }

  bool operator==(const StyleGenericSVGLength& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::LengthPercentage: return length_percentage == other.length_percentage;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericSVGLength() {

  }
  public:


  ~StyleGenericSVGLength() {
    switch (tag) {
      case Tag::LengthPercentage: length_percentage.~StyleLengthPercentage_Body(); break;
      default: break;
    }
  }

  StyleGenericSVGLength(const StyleGenericSVGLength& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::LengthPercentage: ::new (&length_percentage) (StyleLengthPercentage_Body)(other.length_percentage); break;
      default: break;
    }
  }
  StyleGenericSVGLength& operator=(const StyleGenericSVGLength& other) {
    if (this != &other) {
      this->~StyleGenericSVGLength();
      new (this) StyleGenericSVGLength(other);
    }
    return *this;
  }
};

/// <length> | <percentage> | <number> | context-value
using StyleSVGLength = StyleGenericSVGLength<StyleLengthPercentage>;

/// A type used for opacity.
using StyleOpacity = StyleCSSFloat;

/// An SVG opacity value accepts `context-{fill,stroke}-opacity` in
/// addition to opacity value.
template<typename OpacityType>
struct StyleGenericSVGOpacity {
  enum class Tag : uint8_t {
    /// `<opacity-value>`
    Opacity,
    /// `context-fill-opacity`
    ContextFillOpacity,
    /// `context-stroke-opacity`
    ContextStrokeOpacity,
  };

  struct StyleOpacity_Body {
    OpacityType _0;

    bool operator==(const StyleOpacity_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleOpacity_Body opacity;
  };

  static StyleGenericSVGOpacity Opacity(const OpacityType &_0) {
    StyleGenericSVGOpacity result;
    ::new (&result.opacity._0) (OpacityType)(_0);
    result.tag = Tag::Opacity;
    return result;
  }

  bool IsOpacity() const {
    return tag == Tag::Opacity;
  }

  const OpacityType& AsOpacity() const {
    MOZ_DIAGNOSTIC_ASSERT(IsOpacity());
    return opacity._0;
  }

  static StyleGenericSVGOpacity ContextFillOpacity() {
    StyleGenericSVGOpacity result;
    result.tag = Tag::ContextFillOpacity;
    return result;
  }

  bool IsContextFillOpacity() const {
    return tag == Tag::ContextFillOpacity;
  }

  static StyleGenericSVGOpacity ContextStrokeOpacity() {
    StyleGenericSVGOpacity result;
    result.tag = Tag::ContextStrokeOpacity;
    return result;
  }

  bool IsContextStrokeOpacity() const {
    return tag == Tag::ContextStrokeOpacity;
  }

  bool operator==(const StyleGenericSVGOpacity& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Opacity: return opacity == other.opacity;
      default: break;
    }
    return true;
  }

  private:
  StyleGenericSVGOpacity() {

  }
  public:


  ~StyleGenericSVGOpacity() {
    switch (tag) {
      case Tag::Opacity: opacity.~StyleOpacity_Body(); break;
      default: break;
    }
  }

  StyleGenericSVGOpacity(const StyleGenericSVGOpacity& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Opacity: ::new (&opacity) (StyleOpacity_Body)(other.opacity); break;
      default: break;
    }
  }
  StyleGenericSVGOpacity& operator=(const StyleGenericSVGOpacity& other) {
    if (this != &other) {
      this->~StyleGenericSVGOpacity();
      new (this) StyleGenericSVGOpacity(other);
    }
    return *this;
  }
};

/// <opacity-value> | context-fill-opacity | context-stroke-opacity
using StyleSVGOpacity = StyleGenericSVGOpacity<StyleOpacity>;

/// An non-negative wrapper of SVGLength.
using StyleSVGWidth = StyleGenericSVGLength<StyleNonNegativeLengthPercentage>;

/// The computed value of `text-align`.
using StyleTextAlign = StyleTextAlignKeyword;

/// Specified value for the text-autospace property
/// which takes the grammar:
///     normal | <autospace> | auto
/// where:
///     <autospace> = no-autospace |
///                   [ ideograph-alpha || ideograph-numeric || punctuation ]
///                   || [ insert | replace ]
///
/// https://drafts.csswg.org/css-text-4/#text-autospace-property
///
/// Bug 1980111: 'replace' value is not supported yet.
struct StyleTextAutospace {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleTextAutospace operator~() const {
    return StyleTextAutospace { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleTextAutospace operator|(const StyleTextAutospace& other) const {
    return StyleTextAutospace { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleTextAutospace& operator|=(const StyleTextAutospace& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleTextAutospace operator&(const StyleTextAutospace& other) const {
    return StyleTextAutospace { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleTextAutospace& operator&=(const StyleTextAutospace& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleTextAutospace operator^(const StyleTextAutospace& other) const {
    return StyleTextAutospace { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleTextAutospace& operator^=(const StyleTextAutospace& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleTextAutospace& other) const {
    return _0 == other._0;
  }
  static const StyleTextAutospace NO_AUTOSPACE;
  static const StyleTextAutospace AUTO;
  static const StyleTextAutospace NORMAL;
  static const StyleTextAutospace IDEOGRAPH_ALPHA;
  static const StyleTextAutospace IDEOGRAPH_NUMERIC;
  static const StyleTextAutospace INSERT;
};
/// No automatic space is inserted.
constexpr inline const StyleTextAutospace StyleTextAutospace::NO_AUTOSPACE = StyleTextAutospace{
  /* ._0 = */ (uint8_t)0
};
/// The user agent chooses a set of typographically high quality spacing values.
constexpr inline const StyleTextAutospace StyleTextAutospace::AUTO = StyleTextAutospace{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// Same behavior as ideograph-alpha ideograph-numeric.
constexpr inline const StyleTextAutospace StyleTextAutospace::NORMAL = StyleTextAutospace{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// 1/8ic space between ideographic characters and non-ideographic letters.
constexpr inline const StyleTextAutospace StyleTextAutospace::IDEOGRAPH_ALPHA = StyleTextAutospace{
  /* ._0 = */ (uint8_t)(1 << 2)
};
/// 1/8ic space between ideographic characters and non-ideographic decimal numerals.
constexpr inline const StyleTextAutospace StyleTextAutospace::IDEOGRAPH_NUMERIC = StyleTextAutospace{
  /* ._0 = */ (uint8_t)(1 << 3)
};
/// Auto-spacing is only inserted if no space character is present in the text.
constexpr inline const StyleTextAutospace StyleTextAutospace::INSERT = StyleTextAutospace{
  /* ._0 = */ (uint8_t)(1 << 5)
};

/// A generic value for the `<ratio>` value.
template<typename N>
struct StyleRatio {
  N _0;
  N _1;

  bool operator==(const StyleRatio& other) const {
    return _0 == other._0 &&
           _1 == other._1;
  }
  inline AspectRatio ToLayoutRatio(UseBoxSizing aUseBoxSizing) const;
};

/// Ratio or None.
template<typename N>
struct StylePreferredRatio {
  enum class Tag : uint8_t {
    /// Without specified ratio
    None,
    /// With specified ratio
    Ratio,
  };

  struct StyleRatio_Body {
    StyleRatio<N> _0;

    bool operator==(const StyleRatio_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleRatio_Body ratio;
  };

  static StylePreferredRatio None() {
    StylePreferredRatio result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  static StylePreferredRatio Ratio(const StyleRatio<N> &_0) {
    StylePreferredRatio result;
    ::new (&result.ratio._0) (StyleRatio<N>)(_0);
    result.tag = Tag::Ratio;
    return result;
  }

  bool IsRatio() const {
    return tag == Tag::Ratio;
  }

  const StyleRatio<N>& AsRatio() const {
    MOZ_DIAGNOSTIC_ASSERT(IsRatio());
    return ratio._0;
  }

  bool operator==(const StylePreferredRatio& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Ratio: return ratio == other.ratio;
      default: break;
    }
    return true;
  }

  private:
  StylePreferredRatio() {

  }
  public:


  ~StylePreferredRatio() {
    switch (tag) {
      case Tag::Ratio: ratio.~StyleRatio_Body(); break;
      default: break;
    }
  }

  StylePreferredRatio(const StylePreferredRatio& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Ratio: ::new (&ratio) (StyleRatio_Body)(other.ratio); break;
      default: break;
    }
  }
  StylePreferredRatio& operator=(const StylePreferredRatio& other) {
    if (this != &other) {
      this->~StylePreferredRatio();
      new (this) StylePreferredRatio(other);
    }
    return *this;
  }
};

/// A generic value for the `aspect-ratio` property, the value is `auto || <ratio>`.
template<typename N>
struct StyleGenericAspectRatio {
  /// Specifiy auto or not.
  bool auto_;
  /// The preferred aspect-ratio value.
  StylePreferredRatio<N> ratio;

  bool operator==(const StyleGenericAspectRatio& other) const {
    return auto_ == other.auto_ &&
           ratio == other.ratio;
  }
  bool HasRatio() const { return ratio.IsRatio(); }
  bool HasFiniteRatio() const { return static_cast<bool>(ToLayoutRatio()); }
  inline AspectRatio ToLayoutRatio() const;

  static StyleGenericAspectRatio Auto() {
    return {true, StylePreferredRatio<N>::None()};
  }
};

/// A computed value for the `aspect-ratio` property.
using StyleAspectRatio = StyleGenericAspectRatio<StyleNonNegativeNumber>;

/// Page name value.
///
/// https://drafts.csswg.org/css-page-3/#using-named-pages
struct StylePageName {
  enum class Tag : uint8_t {
    /// `auto` value.
    Auto,
    /// Page name value
    PageName,
  };

  struct StylePageName_Body {
    StyleCustomIdent _0;

    bool operator==(const StylePageName_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StylePageName_Body page_name;
  };

  static StylePageName Auto() {
    StylePageName result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StylePageName PageName(const StyleCustomIdent &_0) {
    StylePageName result;
    ::new (&result.page_name._0) (StyleCustomIdent)(_0);
    result.tag = Tag::PageName;
    return result;
  }

  bool IsPageName() const {
    return tag == Tag::PageName;
  }

  const StyleCustomIdent& AsPageName() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPageName());
    return page_name._0;
  }

  bool operator==(const StylePageName& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::PageName: return page_name == other.page_name;
      default: break;
    }
    return true;
  }

  private:
  StylePageName() {

  }
  public:


  ~StylePageName() {
    switch (tag) {
      case Tag::PageName: page_name.~StylePageName_Body(); break;
      default: break;
    }
  }

  StylePageName(const StylePageName& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::PageName: ::new (&page_name) (StylePageName_Body)(other.page_name); break;
      default: break;
    }
  }
  StylePageName& operator=(const StylePageName& other) {
    if (this != &other) {
      this->~StylePageName();
      new (this) StylePageName(other);
    }
    return *this;
  }
};

/// Computed value of the @page size descriptor
///
/// The spec says that the computed value should be the same as the specified
/// value but with all absolute units, but it's not currently possibly observe
/// the computed value of page-size.
struct StylePageSize {
  enum class Tag : uint8_t {
    /// Specified size, paper size, or paper size and orientation.
    Size,
    /// `landscape` or `portrait` value, no specified size.
    Orientation,
    /// `auto` value
    Auto,
  };

  struct StyleSize_Body {
    StyleSize2D<StyleNonNegativeLength> _0;

    bool operator==(const StyleSize_Body& other) const {
      return _0 == other._0;
    }
  };

  struct StyleOrientation_Body {
    StylePageSizeOrientation _0;

    bool operator==(const StyleOrientation_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleSize_Body size;
    StyleOrientation_Body orientation;
  };

  static StylePageSize Size(const StyleSize2D<StyleNonNegativeLength> &_0) {
    StylePageSize result;
    ::new (&result.size._0) (StyleSize2D<StyleNonNegativeLength>)(_0);
    result.tag = Tag::Size;
    return result;
  }

  bool IsSize() const {
    return tag == Tag::Size;
  }

  const StyleSize2D<StyleNonNegativeLength>& AsSize() const {
    MOZ_DIAGNOSTIC_ASSERT(IsSize());
    return size._0;
  }

  static StylePageSize Orientation(const StylePageSizeOrientation &_0) {
    StylePageSize result;
    ::new (&result.orientation._0) (StylePageSizeOrientation)(_0);
    result.tag = Tag::Orientation;
    return result;
  }

  bool IsOrientation() const {
    return tag == Tag::Orientation;
  }

  const StylePageSizeOrientation& AsOrientation() const {
    MOZ_DIAGNOSTIC_ASSERT(IsOrientation());
    return orientation._0;
  }

  static StylePageSize Auto() {
    StylePageSize result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  bool operator==(const StylePageSize& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Size: return size == other.size;
      case Tag::Orientation: return orientation == other.orientation;
      default: break;
    }
    return true;
  }

  private:
  StylePageSize() {

  }
  public:


  ~StylePageSize() {
    switch (tag) {
      case Tag::Size: size.~StyleSize_Body(); break;
      case Tag::Orientation: orientation.~StyleOrientation_Body(); break;
      default: break;
    }
  }

  StylePageSize(const StylePageSize& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Size: ::new (&size) (StyleSize_Body)(other.size); break;
      case Tag::Orientation: ::new (&orientation) (StyleOrientation_Body)(other.orientation); break;
      default: break;
    }
  }
  StylePageSize& operator=(const StylePageSize& other) {
    if (this != &other) {
      this->~StylePageSize();
      new (this) StylePageSize(other);
    }
    return *this;
  }
};

/// The svg d property type.
///
/// https://svgwg.org/svg2-draft/paths.html#TheDProperty
struct StyleDProperty {
  enum class Tag : uint8_t {
    /// Path value for path(<string>) or just a <string>.
    Path,
    /// None value.
    None,
  };

  struct StylePath_Body {
    StyleSVGPathData _0;

    bool operator==(const StylePath_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StylePath_Body path;
  };

  static StyleDProperty Path(const StyleSVGPathData &_0) {
    StyleDProperty result;
    ::new (&result.path._0) (StyleSVGPathData)(_0);
    result.tag = Tag::Path;
    return result;
  }

  bool IsPath() const {
    return tag == Tag::Path;
  }

  const StyleSVGPathData& AsPath() const {
    MOZ_DIAGNOSTIC_ASSERT(IsPath());
    return path._0;
  }

  static StyleDProperty None() {
    StyleDProperty result;
    result.tag = Tag::None;
    return result;
  }

  bool IsNone() const {
    return tag == Tag::None;
  }

  bool operator==(const StyleDProperty& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Path: return path == other.path;
      default: break;
    }
    return true;
  }

  private:
  StyleDProperty() {

  }
  public:


  ~StyleDProperty() {
    switch (tag) {
      case Tag::Path: path.~StylePath_Body(); break;
      default: break;
    }
  }

  StyleDProperty(const StyleDProperty& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Path: ::new (&path) (StylePath_Body)(other.path); break;
      default: break;
    }
  }
  StyleDProperty& operator=(const StyleDProperty& other) {
    if (this != &other) {
      this->~StyleDProperty();
      new (this) StyleDProperty(other);
    }
    return *this;
  }
};

/// Values for scrollbar-gutter:
/// <https://drafts.csswg.org/css-overflow-3/#scrollbar-gutter-property>
struct StyleScrollbarGutter {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleScrollbarGutter operator~() const {
    return StyleScrollbarGutter { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleScrollbarGutter operator|(const StyleScrollbarGutter& other) const {
    return StyleScrollbarGutter { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleScrollbarGutter& operator|=(const StyleScrollbarGutter& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleScrollbarGutter operator&(const StyleScrollbarGutter& other) const {
    return StyleScrollbarGutter { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleScrollbarGutter& operator&=(const StyleScrollbarGutter& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleScrollbarGutter operator^(const StyleScrollbarGutter& other) const {
    return StyleScrollbarGutter { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleScrollbarGutter& operator^=(const StyleScrollbarGutter& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleScrollbarGutter& other) const {
    return _0 == other._0;
  }
  static const StyleScrollbarGutter AUTO;
  static const StyleScrollbarGutter STABLE;
  static const StyleScrollbarGutter BOTH_EDGES;
};
/// `auto` variant. Just for convenience if there is no flag set.
constexpr inline const StyleScrollbarGutter StyleScrollbarGutter::AUTO = StyleScrollbarGutter{
  /* ._0 = */ (uint8_t)0
};
/// `stable` variant.
constexpr inline const StyleScrollbarGutter StyleScrollbarGutter::STABLE = StyleScrollbarGutter{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// `both-edges` variant.
constexpr inline const StyleScrollbarGutter StyleScrollbarGutter::BOTH_EDGES = StyleScrollbarGutter{
  /* ._0 = */ (uint8_t)(1 << 1)
};

/// A value for the `hyphenate-character` property.
struct StyleHyphenateCharacter {
  enum class Tag : uint8_t {
    /// `auto`
    Auto,
    /// `<string>`
    String,
  };

  struct StyleString_Body {
    StyleOwnedStr _0;

    bool operator==(const StyleString_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleString_Body string;
  };

  static StyleHyphenateCharacter Auto() {
    StyleHyphenateCharacter result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleHyphenateCharacter String(const StyleOwnedStr &_0) {
    StyleHyphenateCharacter result;
    ::new (&result.string._0) (StyleOwnedStr)(_0);
    result.tag = Tag::String;
    return result;
  }

  bool IsString() const {
    return tag == Tag::String;
  }

  const StyleOwnedStr& AsString() const {
    MOZ_DIAGNOSTIC_ASSERT(IsString());
    return string._0;
  }

  bool operator==(const StyleHyphenateCharacter& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::String: return string == other.string;
      default: break;
    }
    return true;
  }

  private:
  StyleHyphenateCharacter() {

  }
  public:


  ~StyleHyphenateCharacter() {
    switch (tag) {
      case Tag::String: string.~StyleString_Body(); break;
      default: break;
    }
  }

  StyleHyphenateCharacter(const StyleHyphenateCharacter& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::String: ::new (&string) (StyleString_Body)(other.string); break;
      default: break;
    }
  }
  StyleHyphenateCharacter& operator=(const StyleHyphenateCharacter& other) {
    if (this != &other) {
      this->~StyleHyphenateCharacter();
      new (this) StyleHyphenateCharacter(other);
    }
    return *this;
  }
};

/// A generic value that is either a number or `auto`.
template<typename N>
struct StyleNumberOrAuto {
  enum class Tag : uint8_t {
    /// `auto`
    Auto,
    /// `<number>`
    Number,
  };

  struct StyleNumber_Body {
    N _0;

    bool operator==(const StyleNumber_Body& other) const {
      return _0 == other._0;
    }
  };

  Tag tag;
  union {
    StyleNumber_Body number;
  };

  static StyleNumberOrAuto Auto() {
    StyleNumberOrAuto result;
    result.tag = Tag::Auto;
    return result;
  }

  bool IsAuto() const {
    return tag == Tag::Auto;
  }

  static StyleNumberOrAuto Number(const N &_0) {
    StyleNumberOrAuto result;
    ::new (&result.number._0) (N)(_0);
    result.tag = Tag::Number;
    return result;
  }

  bool IsNumber() const {
    return tag == Tag::Number;
  }

  const N& AsNumber() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNumber());
    return number._0;
  }

  bool operator==(const StyleNumberOrAuto& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::Number: return number == other.number;
      default: break;
    }
    return true;
  }

  private:
  StyleNumberOrAuto() {

  }
  public:


  ~StyleNumberOrAuto() {
    switch (tag) {
      case Tag::Number: number.~StyleNumber_Body(); break;
      default: break;
    }
  }

  StyleNumberOrAuto(const StyleNumberOrAuto& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::Number: ::new (&number) (StyleNumber_Body)(other.number); break;
      default: break;
    }
  }
  StyleNumberOrAuto& operator=(const StyleNumberOrAuto& other) {
    if (this != &other) {
      this->~StyleNumberOrAuto();
      new (this) StyleNumberOrAuto(other);
    }
    return *this;
  }
};

/// A generic value for the `hyphenate-limit-chars` property.
template<typename Integer>
struct StyleGenericHyphenateLimitChars {
  /// Required minimum number of characters in a hyphenated word.
  StyleNumberOrAuto<Integer> total_word_length;
  /// Required minumum number of characters before the hyphen.
  StyleNumberOrAuto<Integer> pre_hyphen_length;
  /// Required minumum number of characters after the hyphen.
  StyleNumberOrAuto<Integer> post_hyphen_length;

  bool operator==(const StyleGenericHyphenateLimitChars& other) const {
    return total_word_length == other.total_word_length &&
           pre_hyphen_length == other.pre_hyphen_length &&
           post_hyphen_length == other.post_hyphen_length;
  }
  static StyleGenericHyphenateLimitChars Auto() {
    return StyleGenericHyphenateLimitChars{
      StyleNumberOrAuto<Integer>::Auto(),
      StyleNumberOrAuto<Integer>::Auto(),
      StyleNumberOrAuto<Integer>::Auto(),
    };
  };
};

/// A computed value for the `hyphenate-character` property.
using StyleHyphenateLimitChars = StyleGenericHyphenateLimitChars<StyleCSSInteger>;

/// https://svgwg.org/svg2-draft/coords.html#VectorEffects
struct StyleVectorEffect {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleVectorEffect operator~() const {
    return StyleVectorEffect { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleVectorEffect operator|(const StyleVectorEffect& other) const {
    return StyleVectorEffect { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleVectorEffect& operator|=(const StyleVectorEffect& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleVectorEffect operator&(const StyleVectorEffect& other) const {
    return StyleVectorEffect { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleVectorEffect& operator&=(const StyleVectorEffect& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleVectorEffect operator^(const StyleVectorEffect& other) const {
    return StyleVectorEffect { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleVectorEffect& operator^=(const StyleVectorEffect& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleVectorEffect& other) const {
    return _0 == other._0;
  }
  bool HasNonScalingStroke() const { return bool(*this & StyleVectorEffect::NON_SCALING_STROKE); }
  static const StyleVectorEffect NONE;
  static const StyleVectorEffect NON_SCALING_STROKE;
};
/// `none`
constexpr inline const StyleVectorEffect StyleVectorEffect::NONE = StyleVectorEffect{
  /* ._0 = */ (uint8_t)0
};
/// `non-scaling-stroke`
constexpr inline const StyleVectorEffect StyleVectorEffect::NON_SCALING_STROKE = StyleVectorEffect{
  /* ._0 = */ (uint8_t)(1 << 0)
};

/// The computed `zoom` property value.
struct StyleZoom {
  float _0;

  bool operator==(const StyleZoom& other) const {
    return _0 == other._0;
  }
 float ToFloat() const { return _0; }
 inline float Zoom(float) const;
 inline float Unzoom(float) const;
 inline nscoord ZoomCoord(nscoord) const;
 inline nscoord UnzoomCoord(nscoord) const;
 inline nsSize Zoom(const nsSize&) const;
 inline nsSize Unzoom(const nsSize&) const;
 inline nsPoint Zoom(const nsPoint&) const;
 inline nsPoint Unzoom(const nsPoint&) const;
 inline nsRect Zoom(const nsRect&) const;
 inline nsRect Unzoom(const nsRect&) const;
  static const StyleZoom ONE;
  static const StyleZoom DOCUMENT;
};
/// The value 1. This is by far the most common value.
constexpr inline const StyleZoom StyleZoom::ONE = StyleZoom{
  /* ._0 = */ 1.0
};
/// The `document` value. This can appear in the computed zoom property value, but not in the
/// `effective_zoom` field.
constexpr inline const StyleZoom StyleZoom::DOCUMENT = StyleZoom{
  /* ._0 = */ 0.0
};

/// A longhand or shorthand property.
struct StyleNonCustomPropertyId {
  uint16_t _0;

  bool operator==(const StyleNonCustomPropertyId& other) const {
    return _0 == other._0;
  }
};

/// A given transition property, that is either `All`, a longhand or shorthand
/// property, or an unsupported or custom property.
union StyleTransitionProperty {
  enum class Tag : uint8_t {
    /// A non-custom property.
    NonCustom,
    /// A custom property.
    Custom,
    /// Unrecognized property which could be any non-transitionable, custom property, or
    /// unknown property.
    Unsupported,
  };

  struct NonCustom_Body {
    Tag tag;
    StyleNonCustomPropertyId _0;

    bool operator==(const NonCustom_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Custom_Body {
    Tag tag;
    StyleAtom _0;

    bool operator==(const Custom_Body& other) const {
      return _0 == other._0;
    }
  };

  struct Unsupported_Body {
    Tag tag;
    StyleCustomIdent _0;

    bool operator==(const Unsupported_Body& other) const {
      return _0 == other._0;
    }
  };

  struct {
    Tag tag;
  };
  NonCustom_Body non_custom;
  Custom_Body custom;
  Unsupported_Body unsupported;

  static StyleTransitionProperty NonCustom(const StyleNonCustomPropertyId &_0) {
    StyleTransitionProperty result;
    ::new (&result.non_custom._0) (StyleNonCustomPropertyId)(_0);
    result.tag = Tag::NonCustom;
    return result;
  }

  bool IsNonCustom() const {
    return tag == Tag::NonCustom;
  }

  const StyleNonCustomPropertyId& AsNonCustom() const {
    MOZ_DIAGNOSTIC_ASSERT(IsNonCustom());
    return non_custom._0;
  }

  static StyleTransitionProperty Custom(const StyleAtom &_0) {
    StyleTransitionProperty result;
    ::new (&result.custom._0) (StyleAtom)(_0);
    result.tag = Tag::Custom;
    return result;
  }

  bool IsCustom() const {
    return tag == Tag::Custom;
  }

  const StyleAtom& AsCustom() const {
    MOZ_DIAGNOSTIC_ASSERT(IsCustom());
    return custom._0;
  }

  static StyleTransitionProperty Unsupported(const StyleCustomIdent &_0) {
    StyleTransitionProperty result;
    ::new (&result.unsupported._0) (StyleCustomIdent)(_0);
    result.tag = Tag::Unsupported;
    return result;
  }

  bool IsUnsupported() const {
    return tag == Tag::Unsupported;
  }

  const StyleCustomIdent& AsUnsupported() const {
    MOZ_DIAGNOSTIC_ASSERT(IsUnsupported());
    return unsupported._0;
  }

  bool operator==(const StyleTransitionProperty& other) const {
    if (tag != other.tag) {
      return false;
    }
    switch (tag) {
      case Tag::NonCustom: return non_custom == other.non_custom;
      case Tag::Custom: return custom == other.custom;
      case Tag::Unsupported: return unsupported == other.unsupported;

    }
    return true;
  }

  private:
  StyleTransitionProperty() {

  }
  public:


  ~StyleTransitionProperty() {
    switch (tag) {
      case Tag::NonCustom: non_custom.~NonCustom_Body(); break;
      case Tag::Custom: custom.~Custom_Body(); break;
      case Tag::Unsupported: unsupported.~Unsupported_Body(); break;

    }
  }

  StyleTransitionProperty(const StyleTransitionProperty& other)
   : tag(other.tag) {
    switch (tag) {
      case Tag::NonCustom: ::new (&non_custom) (NonCustom_Body)(other.non_custom); break;
      case Tag::Custom: ::new (&custom) (Custom_Body)(other.custom); break;
      case Tag::Unsupported: ::new (&unsupported) (Unsupported_Body)(other.unsupported); break;

    }
  }
  StyleTransitionProperty& operator=(const StyleTransitionProperty& other) {
    if (this != &other) {
      this->~StyleTransitionProperty();
      new (this) StyleTransitionProperty(other);
    }
    return *this;
  }
  bool IsAll() const {
    return IsNonCustom() &&
           NonCustomCSSPropertyId(AsNonCustom()._0) == eCSSProperty_all;
  }
};

/// The view-transition-class: `none | <custom-ident>+`.
///
/// https://drafts.csswg.org/css-view-transitions-2/#view-transition-class-prop
///
/// Empty slice represents `none`.
struct StyleViewTransitionClassList {
  StyleArcSlice<StyleCustomIdent> _0;

  bool operator==(const StyleViewTransitionClassList& other) const {
    return _0 == other._0;
  }
};

/// https://drafts.csswg.org/css-view-transitions-2/#view-transition-class-prop
using StyleViewTransitionClass = StyleTreeScoped<StyleViewTransitionClassList>;

/// The view-transition-name: `none | <custom-ident> | match-element`.
///
/// https://drafts.csswg.org/css-view-transitions-1/#view-transition-name-prop
/// https://drafts.csswg.org/css-view-transitions-2/#auto-vt-name
using StyleViewTransitionNameKeyword = StyleAtomIdent;

/// https://drafts.csswg.org/css-view-transitions-1/#view-transition-name-prop
using StyleViewTransitionName = StyleTreeScoped<StyleViewTransitionNameKeyword>;

/// The computed value of anchor side.
using StyleAnchorSide = StyleGenericAnchorSide<StylePercentage>;

/// Flags for the query_font_metrics() function.
struct StyleQueryFontMetricsFlags {
  uint8_t _0;

  constexpr explicit operator bool() const {
    return !!_0;
  }
  constexpr StyleQueryFontMetricsFlags operator~() const {
    return StyleQueryFontMetricsFlags { static_cast<decltype(_0)>(~_0) };
  }
  constexpr StyleQueryFontMetricsFlags operator|(const StyleQueryFontMetricsFlags& other) const {
    return StyleQueryFontMetricsFlags { static_cast<decltype(_0)>(this->_0 | other._0) };
  }
  StyleQueryFontMetricsFlags& operator|=(const StyleQueryFontMetricsFlags& other) {
    *this = (*this | other);
    return *this;
  }
  constexpr StyleQueryFontMetricsFlags operator&(const StyleQueryFontMetricsFlags& other) const {
    return StyleQueryFontMetricsFlags { static_cast<decltype(_0)>(this->_0 & other._0) };
  }
  StyleQueryFontMetricsFlags& operator&=(const StyleQueryFontMetricsFlags& other) {
    *this = (*this & other);
    return *this;
  }
  constexpr StyleQueryFontMetricsFlags operator^(const StyleQueryFontMetricsFlags& other) const {
    return StyleQueryFontMetricsFlags { static_cast<decltype(_0)>(this->_0 ^ other._0) };
  }
  StyleQueryFontMetricsFlags& operator^=(const StyleQueryFontMetricsFlags& other) {
    *this = (*this ^ other);
    return *this;
  }
  bool operator==(const StyleQueryFontMetricsFlags& other) const {
    return _0 == other._0;
  }
  static const StyleQueryFontMetricsFlags USE_USER_FONT_SET;
  static const StyleQueryFontMetricsFlags NEEDS_CH;
  static const StyleQueryFontMetricsFlags NEEDS_IC;
  static const StyleQueryFontMetricsFlags NEEDS_MATH_SCALES;
};
/// Should we use the user font set?
constexpr inline const StyleQueryFontMetricsFlags StyleQueryFontMetricsFlags::USE_USER_FONT_SET = StyleQueryFontMetricsFlags{
  /* ._0 = */ (uint8_t)(1 << 0)
};
/// Does the caller need the `ch` unit (width of the ZERO glyph)?
constexpr inline const StyleQueryFontMetricsFlags StyleQueryFontMetricsFlags::NEEDS_CH = StyleQueryFontMetricsFlags{
  /* ._0 = */ (uint8_t)(1 << 1)
};
/// Does the caller need the `ic` unit (width of the WATER ideograph)?
constexpr inline const StyleQueryFontMetricsFlags StyleQueryFontMetricsFlags::NEEDS_IC = StyleQueryFontMetricsFlags{
  /* ._0 = */ (uint8_t)(1 << 2)
};
/// Does the caller need math scales to be retrieved?
constexpr inline const StyleQueryFontMetricsFlags StyleQueryFontMetricsFlags::NEEDS_MATH_SCALES = StyleQueryFontMetricsFlags{
  /* ._0 = */ (uint8_t)(1 << 3)
};

/// Specified and computed `list-style-type` property.
using StyleListStyleType = StyleCounterStyle;

/// A struct to hold a specific '<declaration-value>'.
using StyleLinkParamValue = StyleOwnedStr;

/// A single param(--ident, value) entry: https://drafts.csswg.org/css-link-params-1/#funcdef-param
struct StyleLinkParam {
  /// link-parameters' param name, in the form of an <dashed-ident>: https://drafts.csswg.org/css-values-4/#typedef-dashed-ident
  StyleDashedIdent name;
  /// link-parameters' value, in the form of a <declaration-value>: https://drafts.csswg.org/css-syntax-3/#typedef-declaration-value
  StyleLinkParamValue value;

  bool operator==(const StyleLinkParam& other) const {
    return name == other.name &&
           value == other.value;
  }
};

/// A struct to hold all specified link-parameters: https://drafts.csswg.org/css-link-params-1/
///
/// We treat `none` as an empty slice and vis-versa
struct StyleLinkParameters {
  /// Slice of specified link-parameters properties: https://drafts.csswg.org/css-link-params-1/#link-param-prop
  StyleArcSlice<StyleLinkParam> _0;

  bool operator==(const StyleLinkParameters& other) const {
    return _0 == other._0;
  }
};

/// Internal property that reflects the lang attribute
using StyleXLang = StyleAtom;









































































































/// Every numeric base type in enum-declaration order.
constexpr static const StyleNumericBaseType StyleALL_NUMERIC_BASE_TYPES[StyleNUMERIC_BASE_TYPE_COUNT] = { StyleNumericBaseType::Length, StyleNumericBaseType::Angle, StyleNumericBaseType::Time, StyleNumericBaseType::Frequency, StyleNumericBaseType::Resolution, StyleNumericBaseType::Flex, StyleNumericBaseType::Percent, };

































/// Number of pixels per inch
constexpr static const StyleCSSFloat StylePX_PER_IN = 96.;

/// Number of pixels per centimeter
constexpr static const StyleCSSFloat StylePX_PER_CM = (StylePX_PER_IN / 2.54);

/// Number of pixels per millimeter
constexpr static const StyleCSSFloat StylePX_PER_MM = (StylePX_PER_IN / 25.4);

/// Number of pixels per quarter
constexpr static const StyleCSSFloat StylePX_PER_Q = (StylePX_PER_MM / 4.);

/// Number of pixels per point
constexpr static const StyleCSSFloat StylePX_PER_PT = (StylePX_PER_IN / 72.);

/// Number of pixels per pica
constexpr static const StyleCSSFloat StylePX_PER_PC = (StylePX_PER_PT * 12.);

























































































extern "C" {

size_t je_malloc_usable_size(const void*);

void Servo_Initialize(URLExtraData *dummy_url_data,
                      URLExtraData *dummy_chrome_url_data);

void Servo_Shutdown();

/// Traverses the subtree rooted at `root` for restyling.
///
/// Returns whether the root was restyled. Whether anything else was restyled or
/// not can be inferred from the dirty bits in the rest of the tree.
bool Servo_TraverseSubtree(const StyleRawGeckoElement *root,
                           const StylePerDocumentStyleData *raw_data,
                           const ServoElementSnapshotTable *snapshots,
                           ServoTraversalFlags raw_flags);

/// Checks whether the rule tree has crossed its threshold for unused nodes, and
/// if so, frees them.
void Servo_MaybeGCRuleTree(const StylePerDocumentStyleData *raw_data);

StyleStrong<StyleAnimationValue> Servo_AnimationValues_Interpolate(const StyleAnimationValue *from,
                                                                   const StyleAnimationValue *to,
                                                                   double progress);

bool Servo_AnimationValues_IsInterpolable(const StyleAnimationValue *from,
                                          const StyleAnimationValue *to);

StyleStrong<StyleAnimationValue> Servo_AnimationValues_Add(const StyleAnimationValue *a,
                                                           const StyleAnimationValue *b);

StyleStrong<StyleAnimationValue> Servo_AnimationValues_Accumulate(const StyleAnimationValue *a,
                                                                  const StyleAnimationValue *b,
                                                                  uint64_t count);

StyleStrong<StyleAnimationValue> Servo_AnimationValues_GetZeroValue(const StyleAnimationValue *value_to_match);

double Servo_AnimationValues_ComputeDistance(const StyleAnimationValue *from,
                                             const StyleAnimationValue *to);

StyleStrong<StyleAnimationValue> Servo_ComposeAnimationSegment(const AnimationPropertySegment *segment,
                                                               const StyleAnimationValue *underlying_value,
                                                               const StyleAnimationValue *last_value,
                                                               StyleIterationCompositeOperation iteration_composite,
                                                               double progress,
                                                               uint64_t current_iteration);

void Servo_AnimationCompose(StyleAnimationValueMap *value_map,
                            const RawServoAnimationValueTable *base_values,
                            const CSSPropertyId *css_property,
                            const AnimationPropertySegment *segment,
                            const AnimationPropertySegment *last_segment,
                            const ComputedTiming *computed_timing,
                            StyleIterationCompositeOperation iteration_composite);

void Servo_AnimationValue_Serialize(const StyleAnimationValue *value,
                                    const CSSPropertyId *property,
                                    const StylePerDocumentStyleData *raw_data,
                                    nsACString *buffer);

/// Debug: MOZ_DBG for AnimationValue.
void Servo_AnimationValue_Dump(const StyleAnimationValue *value,
                               nsACString *result);

void Servo_AnimationValue_GetColor(const StyleAnimationValue *value,
                                   const StyleAbsoluteColor *fg,
                                   StyleAbsoluteColor *result);

bool Servo_AnimationValue_IsCurrentColor(const StyleAnimationValue *value);

float Servo_AnimationValue_GetOpacity(const StyleAnimationValue *value);

StyleStrong<StyleAnimationValue> Servo_AnimationValue_Opacity(float opacity);

StyleStrong<StyleAnimationValue> Servo_AnimationValue_Color(NonCustomCSSPropertyId color_property,
                                                            nscolor color);

const StyleScale *Servo_AnimationValue_GetScale(const StyleAnimationValue *value);

const StyleTranslate *Servo_AnimationValue_GetTranslate(const StyleAnimationValue *value);

const StyleRotate *Servo_AnimationValue_GetRotate(const StyleAnimationValue *value);

const StyleTransform *Servo_AnimationValue_GetTransform(const StyleAnimationValue *value);

void Servo_AnimationValue_GetOffsetPath(const StyleAnimationValue *value,
                                        StyleOffsetPath *output);

const StyleLengthPercentage *Servo_AnimationValue_GetOffsetDistance(const StyleAnimationValue *value);

const StyleOffsetRotate *Servo_AnimationValue_GetOffsetRotate(const StyleAnimationValue *value);

const StylePositionOrAuto *Servo_AnimationValue_GetOffsetAnchor(const StyleAnimationValue *value);

const StyleOffsetPosition *Servo_AnimationValue_GetOffsetPosition(const StyleAnimationValue *value);

bool Servo_AnimationValue_IsOffsetPathUrl(const StyleAnimationValue *value);

StyleStrong<StyleAnimationValue> Servo_AnimationValue_Rotate(const StyleRotate *r);

StyleStrong<StyleAnimationValue> Servo_AnimationValue_Translate(const StyleTranslate *t);

StyleStrong<StyleAnimationValue> Servo_AnimationValue_Scale(const StyleScale *s);

StyleStrong<StyleAnimationValue> Servo_AnimationValue_Transform(const StyleTransform *transform);

StyleStrong<StyleAnimationValue> Servo_AnimationValue_OffsetPath(const StyleOffsetPath *p);

StyleStrong<StyleAnimationValue> Servo_AnimationValue_OffsetDistance(const StyleLengthPercentage *d);

StyleStrong<StyleAnimationValue> Servo_AnimationValue_OffsetRotate(const StyleOffsetRotate *r);

StyleStrong<StyleAnimationValue> Servo_AnimationValue_OffsetAnchor(const StylePositionOrAuto *p);

StyleStrong<StyleAnimationValue> Servo_AnimationValue_OffsetPosition(const StyleOffsetPosition *p);

bool Servo_AnimationValue_DeepEqual(const StyleAnimationValue *this_,
                                    const StyleAnimationValue *other);

StyleStrong<StyleLockedDeclarationBlock> Servo_AnimationValue_Uncompute(const StyleAnimationValue *value);

StyleAnimationValueMap *Servo_AnimationValueMap_Create();

void Servo_AnimationValueMap_Drop(StyleAnimationValueMap *value_map);

StyleStrong<StyleAnimationValue> Servo_AnimationValueMap_GetValue(const StyleAnimationValueMap *value_map,
                                                                  const CSSPropertyId *property_id);

StyleStrong<StyleComputedValues> Servo_StyleSet_GetBaseComputedValuesForElement(const StylePerDocumentStyleData *raw_style_set,
                                                                                const StyleRawGeckoElement *element,
                                                                                const StyleComputedValues *computed_values,
                                                                                const ServoElementSnapshotTable *snapshots);

StyleShouldTransitionResult Servo_ComputedValues_ShouldTransition(const StyleComputedValues *old,
                                                                  const StyleComputedValues *new_,
                                                                  const CSSPropertyId *prop,
                                                                  StyleTransitionBehavior behavior,
                                                                  const StyleAnimationValue *old_transition_end_value,
                                                                  const StyleAnimationValue *current_start_value,
                                                                  const StyleAnimationValue *current_end_value,
                                                                  const double *progress,
                                                                  RefPtr<StyleAnimationValue> *start,
                                                                  RefPtr<StyleAnimationValue> *end);

bool Servo_ComputedValues_TransitionValueMatches(const StyleComputedValues *style,
                                                 const CSSPropertyId *prop,
                                                 const StyleAnimationValue *transition_value);

StyleStrong<StyleAnimationValue> Servo_ComputedValues_ExtractAnimationValue(const StyleComputedValues *computed_values,
                                                                            const CSSPropertyId *property_id);

NonCustomCSSPropertyId Servo_ResolveLogicalProperty(NonCustomCSSPropertyId property_id,
                                                    const StyleComputedValues *style);

NonCustomCSSPropertyId Servo_Property_LookupEnabledForAllContent(const nsACString *prop);

const uint8_t *Servo_Property_GetName(NonCustomCSSPropertyId prop,
                                      uint32_t *out_length);

bool Servo_Property_IsShorthand(const nsACString *prop_name, bool *found);

bool Servo_Property_IsInherited(const StylePerDocumentStyleData *per_doc_data,
                                const nsACString *prop_name);

bool Servo_Property_SupportsType(const nsACString *prop_name,
                                 uint8_t ty,
                                 bool *found);

void Servo_Property_GetCSSValuesForProperty(const nsACString *prop_name,
                                            bool *found,
                                            nsTArray<nsString> *result);

void Servo_Property_GetCSSWideKeywords(nsTArray<nsString> *result);

bool Servo_Property_IsAnimatable(const CSSPropertyId *prop);

NonCustomCSSPropertyId Servo_Property_ResolveAlias(NonCustomCSSPropertyId property);

bool Servo_Property_IsDiscreteAnimatable(NonCustomCSSPropertyId property);

void Servo_Element_ClearData(const StyleRawGeckoElement *element);

size_t Servo_Element_SizeOfExcludingThisAndCVs(StyleGeckoMallocSizeOf malloc_size_of,
                                               StyleGeckoMallocSizeOf malloc_enclosing_size_of,
                                               SeenPtrs *seen_ptrs,
                                               const StyleRawGeckoElement *element);

const StyleComputedValues *Servo_Element_GetMaybeOutOfDateStyle(const StyleRawGeckoElement *element);

const StyleComputedValues *Servo_Element_GetMaybeOutOfDatePseudoStyle(const StyleRawGeckoElement *element,
                                                                      size_t index);

bool Servo_Element_IsDisplayNone(const StyleRawGeckoElement *element);

bool Servo_Element_IsDisplayContents(const StyleRawGeckoElement *element);

bool Servo_Element_IsPrimaryStyleReusedViaRuleNode(const StyleRawGeckoElement *element);

bool Servo_Element_ReferencesAttribute(const StyleRawGeckoElement *element,
                                       const nsAtom *attr);

bool Servo_Element_UsesTreeCountingFunction(const StyleRawGeckoElement *element);

StyleStrong<StyleStylesheetContents> Servo_StyleSheet_Empty(StyleOrigin origin);

/// Note: The load_data corresponds to this sheet, and is passed as the parent
/// load data for child sheet loads. It may be null for certain cases where we
/// know we won't have child loads.
StyleStrong<StyleStylesheetContents> Servo_StyleSheet_FromUTF8Bytes(StyleLoader *loader,
                                                                    StyleDomStyleSheet *stylesheet,
                                                                    StyleSheetLoadData *load_data,
                                                                    const nsACString *bytes,
                                                                    StyleOrigin origin,
                                                                    URLExtraData *extra_data,
                                                                    nsCompatibility quirks_mode,
                                                                    StyleLoaderReusableStyleSheets *reusable_sheets,
                                                                    StyleAllowImportRules allow_import_rules,
                                                                    StyleSanitizationKind sanitization_kind,
                                                                    nsAString *sanitized_output);

void Servo_StyleSheet_FromUTF8BytesAsync(StyleSheetLoadDataHolder *load_data,
                                         URLExtraData *extra_data,
                                         const nsACString *bytes,
                                         StyleOrigin origin,
                                         nsCompatibility quirks_mode,
                                         StyleAllowImportRules allow_import_rules);

void Servo_ShutdownThreadPool();

void Servo_ThreadPool_GetThreadHandles(nsTArray<StylePlatformThreadHandle> *handles);

StyleStrong<StyleStylesheetContents> Servo_StyleSheet_FromSharedData(URLExtraData *extra_data,
                                                                     const StyleLockedCssRules *shared_rules);

void Servo_StyleSet_AppendStyleSheet(const StylePerDocumentStyleData *raw_data,
                                     const StyleDomStyleSheet *sheet);

StyleAuthorStyles *Servo_AuthorStyles_Create();

void Servo_AuthorStyles_Drop(StyleAuthorStyles *styles);

void Servo_AuthorStyles_AppendStyleSheet(StyleAuthorStyles *styles,
                                         const StyleDomStyleSheet *sheet);

void Servo_AuthorStyles_InsertStyleSheetBefore(StyleAuthorStyles *styles,
                                               const StyleDomStyleSheet *sheet,
                                               const StyleDomStyleSheet *before_sheet);

void Servo_AuthorStyles_RemoveStyleSheet(StyleAuthorStyles *styles,
                                         const StyleDomStyleSheet *sheet);

void Servo_AuthorStyles_ForceDirty(StyleAuthorStyles *styles);

bool Servo_AuthorStyles_IsDirty(const StyleAuthorStyles *styles);

size_t Servo_DeclarationBlock_SizeOfIncludingThis(StyleGeckoMallocSizeOf malloc_size_of,
                                                  StyleGeckoMallocSizeOf malloc_enclosing_size_of,
                                                  const StyleLockedDeclarationBlock *declarations);

size_t Servo_AuthorStyles_SizeOfIncludingThis(StyleGeckoMallocSizeOf malloc_size_of,
                                              StyleGeckoMallocSizeOf malloc_enclosing_size_of,
                                              const StyleAuthorStyles *styles);

MediumFeaturesChangedResult Servo_StyleSet_MediumFeaturesChanged(const StylePerDocumentStyleData *document_set,
                                                                 nsTArray<StyleAuthorStyles*> *non_document_styles,
                                                                 bool may_affect_default_style);

void Servo_StyleSet_InsertStyleSheetBefore(const StylePerDocumentStyleData *raw_data,
                                           const StyleDomStyleSheet *sheet,
                                           const StyleDomStyleSheet *before_sheet);

void Servo_StyleSet_RemoveStyleSheet(const StylePerDocumentStyleData *raw_data,
                                     const StyleDomStyleSheet *sheet);

const StyleDomStyleSheet *Servo_StyleSet_GetSheetAt(const StylePerDocumentStyleData *raw_data,
                                                    StyleOrigin origin,
                                                    size_t index);

size_t Servo_StyleSet_GetSheetCount(const StylePerDocumentStyleData *raw_data,
                                    StyleOrigin origin);

void Servo_StyleSet_FlushStyleSheets(const StylePerDocumentStyleData *raw_data,
                                     const StyleRawGeckoElement *doc_element,
                                     const ServoElementSnapshotTable *snapshots,
                                     nsTArray<StyleAuthorStyles*> *non_document_styles);

void Servo_StyleSet_NoteStyleSheetsChanged(const StylePerDocumentStyleData *raw_data,
                                           OriginFlags changed_origins);

void Servo_StyleSet_SetAuthorStyleDisabled(const StylePerDocumentStyleData *raw_data,
                                           bool author_style_disabled);

bool Servo_StyleSet_UsesFontMetrics(const StylePerDocumentStyleData *raw_data);

bool Servo_StyleSet_UsesRootFontMetrics(const StylePerDocumentStyleData *raw_data);

bool Servo_StyleSheet_HasRules(const StyleStylesheetContents *raw_contents);

const StyleUseCounters *Servo_StyleSheet_UseCounters(const StyleStylesheetContents *raw_contents);

StyleStrong<StyleLockedCssRules> Servo_StyleSheet_GetRules(const StyleStylesheetContents *sheet);

StyleStrong<StyleStylesheetContents> Servo_StyleSheet_Clone(const StyleStylesheetContents *contents,
                                                            URLExtraData *data);

size_t Servo_StyleSheet_SizeOfIncludingThis(StyleGeckoMallocSizeOf malloc_size_of,
                                            StyleGeckoMallocSizeOf malloc_enclosing_size_of,
                                            const StyleStylesheetContents *sheet);

StyleOrigin Servo_StyleSheet_GetOrigin(const StyleStylesheetContents *sheet);

void Servo_StyleSheet_GetSourceMapURL(const StyleStylesheetContents *contents,
                                      nsACString *result);

void Servo_StyleSheet_GetSourceURL(const StyleStylesheetContents *contents,
                                   nsACString *result);

size_t Servo_CssRules_GetRuleCount(const StyleLockedCssRules *rules);

StyleCssRuleType Servo_CssRules_GetRuleTypeAt(const StyleLockedCssRules *rules,
                                              size_t index);

void Servo_CssRules_ListTypes(const StyleLockedCssRules *rules,
                              nsTArray<size_t> *result);

nsresult Servo_CssRules_InsertRule(const StyleLockedCssRules *rules,
                                   const StyleStylesheetContents *contents,
                                   const nsACString *rule,
                                   uint32_t index,
                                   uint32_t containing_rule_types,
                                   const StyleCssRuleType *parse_relative_rule_type,
                                   StyleLoader *loader,
                                   StyleAllowImportRules allow_import_rules,
                                   StyleDomStyleSheet *gecko_stylesheet,
                                   StyleCssRuleType *rule_type);

nsresult Servo_CssRules_DeleteRule(const StyleLockedCssRules *rules,
                                   uint32_t index);

StyleStrong<StyleLockedCssRules> Servo_StyleRule_EnsureRules(const StyleLockedStyleRule *rule,
                                                             bool read_only);

StyleStrong<StyleLockedDeclarationBlock> Servo_NestedDeclarationsRule_GetStyle(const StyleLockedNestedDeclarationsRule *rule);

void Servo_NestedDeclarationsRule_SetStyle(const StyleLockedNestedDeclarationsRule *rule,
                                           const StyleLockedDeclarationBlock *declarations);

bool Servo_DeclarationBlock_IsImmutable(const StyleLockedDeclarationBlock *declarations);

void Servo_DeclarationBlock_SetImmutable(const StyleLockedDeclarationBlock *declarations);

StyleStrong<StyleLockedDeclarationBlock> Servo_StyleRule_GetStyle(const StyleLockedStyleRule *rule);

void Servo_StyleRule_SetStyle(const StyleLockedStyleRule *rule,
                              const StyleLockedDeclarationBlock *declarations);

void Servo_StyleRule_GetSelectorText(const StyleLockedStyleRule *rule,
                                     nsACString *result);

StyleSelectorList *Servo_StyleRule_GetSelectorList(const nsTArray<const StyleLockedStyleRule*> *rules);

void Servo_StyleRule_GetSelectorDataAtIndex(const nsTArray<const StyleLockedStyleRule*> *rules,
                                            uint32_t index,
                                            nsACString *text,
                                            uint64_t *specificity);

uint32_t Servo_StyleRule_GetSelectorCount(const StyleLockedStyleRule *rule);

bool Servo_StyleRule_SelectorMatchesElement(const nsTArray<const StyleLockedStyleRule*> *rules,
                                            const nsTArray<StyleScopeRuleData> *scope_rules,
                                            const StyleRawGeckoElement *element,
                                            uint32_t index,
                                            const StyleRawGeckoElement *host,
                                            PseudoStyleType pseudo_type,
                                            const nsAtom *pseudo_id,
                                            bool relevant_link_visited);

const StyleRawGeckoElement *Servo_StyleRule_GetScopeRootFor(const nsTArray<const StyleLockedStyleRule*> *rules,
                                                            const nsTArray<StyleScopeRuleData> *scope_rules,
                                                            const StyleRawGeckoElement *element,
                                                            uint32_t index,
                                                            const StyleRawGeckoElement *host,
                                                            PseudoStyleType pseudo_type,
                                                            const nsAtom *pseudo_id,
                                                            bool relevant_link_visited);

bool Servo_StyleRule_SetSelectorText(const StyleStylesheetContents *contents,
                                     const StyleLockedStyleRule *rule,
                                     const nsACString *text,
                                     const StyleCssRuleType *parse_relative_rule_type);

const StyleRawGeckoElement *Servo_SelectorList_Closest(const StyleRawGeckoElement *element,
                                                       const StyleSelectorList *selectors);

bool Servo_SelectorList_Matches(const StyleRawGeckoElement *element,
                                const StyleSelectorList *selectors);

const StyleRawGeckoElement *Servo_SelectorList_QueryFirst(const StyleRawGeckoNode *node,
                                                          const StyleSelectorList *selectors,
                                                          bool may_use_invalidation);

void Servo_SelectorList_QueryAll(const StyleRawGeckoNode *node,
                                 const StyleSelectorList *selectors,
                                 StyleSimpleContentList *content_list,
                                 bool may_use_invalidation);

void Servo_SelectorList_QueryAllWithScope(const StyleRawGeckoNode *node,
                                          const nsTArray<const StyleLockedStyleRule*> *rules,
                                          const nsTArray<StyleScopeRuleData> *scope_rules,
                                          StyleSimpleContentList *content_list);

void Servo_ImportRule_GetHref(const StyleLockedImportRule *rule,
                              nsAString *result);

void Servo_ImportRule_GetLayerName(const StyleLockedImportRule *rule,
                                   nsACString *result);

void Servo_ImportRule_GetSupportsText(const StyleLockedImportRule *rule,
                                      nsACString *result);

const StyleDomStyleSheet *Servo_ImportRule_GetSheet(const StyleLockedImportRule *rule);

void Servo_ImportRule_SetSheet(const StyleLockedImportRule *rule,
                               StyleDomStyleSheet *sheet);

void Servo_Keyframe_GetKeyText(const StyleLockedKeyframe *keyframe,
                               nsACString *result);

bool Servo_Keyframe_SetKeyText(const StyleLockedKeyframe *keyframe,
                               const nsACString *text);

StyleStrong<StyleLockedDeclarationBlock> Servo_Keyframe_GetStyle(const StyleLockedKeyframe *keyframe);

void Servo_Keyframe_SetStyle(const StyleLockedKeyframe *keyframe,
                             const StyleLockedDeclarationBlock *declarations);

nsAtom *Servo_KeyframesRule_GetName(const StyleLockedKeyframesRule *rule);

void Servo_KeyframesRule_SetName(const StyleLockedKeyframesRule *rule,
                                 nsAtom *name);

uint32_t Servo_KeyframesRule_GetCount(const StyleLockedKeyframesRule *rule);

StyleStrong<StyleLockedKeyframe> Servo_KeyframesRule_GetKeyframeAt(const StyleLockedKeyframesRule *rule,
                                                                   uint32_t index,
                                                                   uint32_t *line,
                                                                   uint32_t *column);

uint32_t Servo_KeyframesRule_FindRule(const StyleLockedKeyframesRule *rule,
                                      const nsACString *key);

bool Servo_KeyframesRule_AppendRule(const StyleLockedKeyframesRule *rule,
                                    const StyleStylesheetContents *contents,
                                    const nsACString *css);

void Servo_KeyframesRule_DeleteRule(const StyleLockedKeyframesRule *rule,
                                    uint32_t index);

StyleStrong<StyleLockedMediaList> Servo_MediaRule_GetMedia(const StyleMediaRule *rule);

/// If the condition is null, the true/false gets communicated via the out-param
StyleStrong<StyleLockedMediaList> Servo_CustomMediaRule_GetCondition(const StyleCustomMediaRule *rule,
                                                                     bool *value);

nsAtom *Servo_NamespaceRule_GetPrefix(const StyleNamespaceRule *rule);

nsAtom *Servo_NamespaceRule_GetURI(const StyleNamespaceRule *rule);

StyleStrong<StyleLockedDeclarationBlock> Servo_MarginRule_GetStyle(const StyleMarginRule *rule);

void Servo_MarginRule_GetName(const StyleMarginRule *rule, nsACString *out);

nsAtom *Servo_CustomMediaRule_GetName(const StyleCustomMediaRule *rule);

StyleStrong<StyleLockedDeclarationBlock> Servo_PageRule_GetStyle(const StyleLockedPageRule *rule);

void Servo_PageRule_SetStyle(const StyleLockedPageRule *rule,
                             const StyleLockedDeclarationBlock *declarations);

void Servo_PageRule_GetSelectorText(const StyleLockedPageRule *rule,
                                    nsACString *result);

bool Servo_PageRule_SetSelectorText(const StyleStylesheetContents *contents,
                                    const StyleLockedPageRule *rule,
                                    const nsACString *text);

void Servo_PropertyRule_GetName(const StylePropertyRule *rule,
                                nsACString *result);

void Servo_PropertyRule_GetSyntax(const StylePropertyRule *rule,
                                  nsACString *result);

bool Servo_PropertyRule_GetInherits(const StylePropertyRule *rule);

bool Servo_PropertyRule_GetInitialValue(const StylePropertyRule *rule,
                                        nsACString *result);

void Servo_SupportsRule_GetConditionText(const StyleSupportsRule *rule,
                                         nsACString *result);

void Servo_ContainerRule_GetConditionText(const StyleContainerRule *rule,
                                          nsACString *result);

size_t Servo_ContainerRule_GetConditionsLength(const StyleContainerRule *rule);

void Servo_ContainerRule_GetContainerName(const StyleContainerRule *rule,
                                          size_t i,
                                          nsACString *result);

void Servo_ContainerRule_GetContainerQuery(const StyleContainerRule *rule,
                                           size_t i,
                                           nsACString *result);

const StyleRawGeckoElement *Servo_ContainerRule_QueryContainerFor(const StyleContainerRule *rule,
                                                                  const StyleRawGeckoElement *element,
                                                                  size_t condition_index);

bool Servo_ContainerRule_QueryConditionMatchesElement(const StyleContainerRule *rule,
                                                      const StyleRawGeckoElement *element,
                                                      size_t condition_index,
                                                      const StylePerDocumentStyleData *per_doc_data);

void Servo_DocumentRule_GetConditionText(const StyleDocumentRule *rule,
                                         nsACString *result);

void Servo_FontFeatureValuesRule_GetFontFamily(const StyleFontFeatureValuesRule *rule,
                                               nsACString *result);

void Servo_FontFeatureValuesRule_GetValueText(const StyleFontFeatureValuesRule *rule,
                                              nsACString *result);

void Servo_FontPaletteValuesRule_GetName(const StyleFontPaletteValuesRule *rule,
                                         nsACString *result);

void Servo_FontPaletteValuesRule_GetFontFamily(const StyleFontPaletteValuesRule *rule,
                                               nsACString *result);

void Servo_FontPaletteValuesRule_GetBasePalette(const StyleFontPaletteValuesRule *rule,
                                                nsACString *result);

void Servo_FontPaletteValuesRule_GetOverrideColors(const StyleFontPaletteValuesRule *rule,
                                                   nsACString *result);

StyleStrong<StyleLockedFontFaceRule> Servo_FontFaceRule_CreateEmpty();

StyleStrong<StyleLockedFontFaceRule> Servo_FontFaceRule_Clone(const StyleLockedFontFaceRule *rule);

bool Servo_FontFaceRule_Equals(const StyleLockedFontFaceRule *a,
                               const StyleLockedFontFaceRule *b);

void Servo_FontFaceRule_GetSourceLocation(const StyleLockedFontFaceRule *rule,
                                          uint32_t *line,
                                          uint32_t *column);

uint32_t Servo_FontFaceRule_Length(const StyleLockedFontFaceRule *rule);

bool Servo_FontFaceRule_IndexGetter(const StyleLockedFontFaceRule *rule,
                                    uint32_t index,
                                    FontFaceDescriptorId *out);

void Servo_FontFaceRule_GetDeclCssText(const StyleLockedFontFaceRule *rule,
                                       nsACString *result);

bool Servo_FontFaceRule_GetFontWeight(const StyleLockedFontFaceRule *rule,
                                      StyleComputedFontWeightRange *out);

bool Servo_FontFaceRule_GetFontWidth(const StyleLockedFontFaceRule *rule,
                                     StyleComputedFontWidthRange *out);

bool Servo_FontFaceRule_GetFontStyle(const StyleLockedFontFaceRule *rule,
                                     StyleComputedFontStyleRange *out);

bool Servo_FontFaceRule_GetFontDisplay(const StyleLockedFontFaceRule *rule,
                                       StyleFontDisplay *out);

bool Servo_FontFaceRule_GetFontLanguageOverride(const StyleLockedFontFaceRule *rule,
                                                StyleFontLanguageOverride *out);

bool Servo_FontFaceRule_GetAscentOverride(const StyleLockedFontFaceRule *rule,
                                          StylePercentage *out);

bool Servo_FontFaceRule_GetDescentOverride(const StyleLockedFontFaceRule *rule,
                                           StylePercentage *out);

bool Servo_FontFaceRule_GetLineGapOverride(const StyleLockedFontFaceRule *rule,
                                           StylePercentage *out);

bool Servo_FontFaceRule_GetSizeAdjust(const StyleLockedFontFaceRule *rule,
                                      StylePercentage *out);

nsAtom *Servo_FontFaceRule_GetFamilyName(const StyleLockedFontFaceRule *rule);

const StyleUnicodeRange *Servo_FontFaceRule_GetUnicodeRanges(const StyleLockedFontFaceRule *rule,
                                                             size_t *out_len);

void Servo_FontFaceRule_GetSources(const StyleLockedFontFaceRule *rule,
                                   nsTArray<StyleFontFaceSourceListComponent> *out);

void Servo_FontFaceRule_GetVariationSettings(const StyleLockedFontFaceRule *rule,
                                             nsTArray<StyleVariationValue<float>> *variations);

void Servo_FontFaceRule_GetFeatureSettings(const StyleLockedFontFaceRule *rule,
                                           nsTArray<StyleFeatureTagValue<int32_t>> *features);

void Servo_FontFaceRule_GetDescriptorCssText(const StyleLockedFontFaceRule *rule,
                                             FontFaceDescriptorId desc,
                                             nsACString *result);

bool Servo_FontFaceRule_SetDescriptor(const StyleLockedFontFaceRule *rule,
                                      FontFaceDescriptorId desc,
                                      const nsACString *value,
                                      URLExtraData *data,
                                      bool *out_changed);

void Servo_FontFaceRule_ResetDescriptor(const StyleLockedFontFaceRule *rule,
                                        FontFaceDescriptorId desc);

nsAtom *Servo_CounterStyleRule_GetName(const StyleLockedCounterStyleRule *rule);

bool Servo_CounterStyleRule_SetName(const StyleLockedCounterStyleRule *rule,
                                    const nsACString *value);

uint32_t Servo_CounterStyleRule_GetGeneration(const StyleLockedCounterStyleRule *rule);

bool Servo_CounterStyleRule_GetPad(const StyleLockedCounterStyleRule *rule,
                                   int32_t *width,
                                   nsString *symbol);

bool Servo_CounterStyleRule_GetPrefix(const StyleLockedCounterStyleRule *rule,
                                      nsString *out);

bool Servo_CounterStyleRule_GetSuffix(const StyleLockedCounterStyleRule *rule,
                                      nsString *out);

bool Servo_CounterStyleRule_GetNegative(const StyleLockedCounterStyleRule *rule,
                                        nsString *prefix,
                                        nsString *suffix);

StyleIsOrdinalInRange Servo_CounterStyleRule_IsInRange(const StyleLockedCounterStyleRule *rule,
                                                       int32_t ordinal);

const StyleSymbol *Servo_CounterStyleRule_GetSymbols(const StyleLockedCounterStyleRule *rule,
                                                     size_t *count);

void Servo_CounterStyleRule_GetAdditiveSymbols(const StyleLockedCounterStyleRule *rule,
                                               StyleOwnedSlice<StyleAdditiveSymbol> *symbols);

void Servo_CounterStyleRule_GetSpeakAs(const StyleLockedCounterStyleRule *rule,
                                       StyleCounterSpeakAs *out);

StyleCounterSystem Servo_CounterStyleRule_GetSystem(const StyleLockedCounterStyleRule *rule);

nsAtom *Servo_CounterStyleRule_GetExtended(const StyleLockedCounterStyleRule *rule);

int32_t Servo_CounterStyleRule_GetFixedFirstValue(const StyleLockedCounterStyleRule *rule);

nsAtom *Servo_CounterStyleRule_GetFallback(const StyleLockedCounterStyleRule *rule);

void Servo_CounterStyleRule_GetDescriptorCssText(const StyleLockedCounterStyleRule *rule,
                                                 CounterStyleDescriptorId desc,
                                                 nsACString *result);

bool Servo_CounterStyleRule_SetDescriptor(const StyleLockedCounterStyleRule *rule,
                                          CounterStyleDescriptorId desc,
                                          const nsACString *value);

void Servo_PositionTryRule_GetName(const StyleLockedPositionTryRule *rule,
                                   nsACString *result);

StyleStrong<StyleLockedDeclarationBlock> Servo_PositionTryRule_GetStyle(const StyleLockedPositionTryRule *rule);

void Servo_PositionTryRule_SetStyle(const StyleLockedPositionTryRule *rule,
                                    const StyleLockedDeclarationBlock *declarations);

StyleStrong<StyleComputedValues> Servo_ComputedValues_GetForPageContent(const StylePerDocumentStyleData *raw_data,
                                                                        const nsAtom *page_name,
                                                                        StylePagePseudoClassFlags pseudos);

StyleStrong<StyleComputedValues> Servo_ComputedValues_GetForPositionTry(const StylePerDocumentStyleData *raw_data,
                                                                        const StyleComputedValues *style,
                                                                        StyleCascadeLevel scope,
                                                                        const StyleRawGeckoElement *element,
                                                                        const StylePositionTryFallbacksItem *fallback_item);

StyleStrong<StyleComputedValues> Servo_ComputedValues_GetForAnonymousBox(const StyleComputedValues *parent_style_or_null,
                                                                         PseudoStyleType pseudo,
                                                                         const StylePerDocumentStyleData *raw_data);

StyleStrong<StyleComputedValues> Servo_ResolvePseudoStyle(const StyleRawGeckoElement *element,
                                                          PseudoStyleType pseudo_type,
                                                          nsAtom *functional_pseudo_parameter,
                                                          bool is_probe,
                                                          const StyleComputedValues *inherited_style,
                                                          const StylePerDocumentStyleData *raw_data);

StyleStrong<StyleComputedValues> Servo_ComputedValues_ResolveXULTreePseudoStyle(const StyleRawGeckoElement *element,
                                                                                PseudoStyleType pseudo_type,
                                                                                const StyleComputedValues *inherited_style,
                                                                                const nsTArray<RefPtr<nsAtom>> *input_word,
                                                                                const StylePerDocumentStyleData *raw_data);

void Servo_SetExplicitStyle(const StyleRawGeckoElement *element,
                            const StyleComputedValues *style);

StyleStrong<StyleComputedValues> Servo_ComputedValues_Inherit(const StylePerDocumentStyleData *raw_data,
                                                              PseudoStyleType pseudo,
                                                              const StyleComputedValues *parent_style_context,
                                                              InheritTarget target);

bool Servo_ComputedValues_SpecifiesAnimationsOrTransitions(const StyleComputedValues *values);

void Servo_ComputedValues_GetMatchingDeclarations(const StyleComputedValues *values,
                                                  bool with_starting_style,
                                                  nsTArray<StyleMatchingDeclarationBlock> *rules);

bool Servo_ComputedValues_EqualForCachedAnonymousContentStyle(const StyleComputedValues *a,
                                                              const StyleComputedValues *b);

void Servo_ComputedValues_DumpMatchedRules(const StyleComputedValues *s);

uint16_t Servo_ComputedValues_BlockifiedDisplay(const StyleComputedValues *style,
                                                bool is_root_element);

StylePerDocumentStyleData *Servo_StyleSet_Init(const StyleDocument *doc);

void Servo_StyleSet_Drop(StylePerDocumentStyleData *data);

void Servo_StyleSet_RebuildCachedData(const StylePerDocumentStyleData *raw_data);

void Servo_StyleSet_CompatModeChanged(const StylePerDocumentStyleData *raw_data);

StyleStrong<StyleLockedDeclarationBlock> Servo_ParseProperty(const CSSPropertyId *property,
                                                             const nsACString *value,
                                                             URLExtraData *data,
                                                             StyleParsingMode parsing_mode,
                                                             nsCompatibility quirks_mode,
                                                             StyleLoader *loader,
                                                             StyleCssRuleType rule_type);

bool Servo_ParseLengthPercentageForAbsoluteLengths(const nsACString *lp,
                                                   StyleLengthPercentage *output);

bool Servo_ParseViewTimelineInset(const nsACString *inset,
                                  StyleViewTimelineInset *output);

bool Servo_ParseEasing(const nsACString *easing,
                       StyleComputedTimingFunction *output);

bool Servo_ParseKeyframeSelector(const nsACString *selector,
                                 StyleTimelineRangeName *name,
                                 double *percentage);

bool Servo_ParseTimelineRangeName(const nsACString *range_name,
                                  StyleTimelineRangeName *output);

void Servo_SerializeEasing(const StyleComputedTimingFunction *easing,
                           nsACString *output);

void Servo_SerializeTimelineRangeName(StyleTimelineRangeName range_name,
                                      nsACString *output);

void Servo_GetProperties_Overriding_Animation(const StyleRawGeckoElement *element,
                                              const nsTArray<NonCustomCSSPropertyId> *list,
                                              nsCSSPropertyIDSet *set);

void Servo_MatrixTransform_Operate(bool interpolate,
                                   const StyleMatrix4x4Components *from,
                                   const StyleMatrix4x4Components *to,
                                   double progress,
                                   StyleMatrix4x4Components *output);

StyleStrong<StyleLockedDeclarationBlock> Servo_ParseStyleAttribute(const nsACString *data,
                                                                   URLExtraData *raw_extra_data,
                                                                   nsCompatibility quirks_mode,
                                                                   StyleLoader *loader,
                                                                   StyleCssRuleType rule_type);

bool Servo_PseudoStyleType_EnabledForAllContent(PseudoStyleType ty);

bool Servo_ParsePseudoElement(const nsAString *data,
                              URLExtraData *url_data,
                              bool ignore_enabled_state,
                              PseudoStyleRequest *request);

StyleStrong<StyleLockedDeclarationBlock> Servo_DeclarationBlock_CreateEmpty();

void Servo_DeclarationBlock_Clear(const StyleLockedDeclarationBlock *declarations);

StyleStrong<StyleLockedDeclarationBlock> Servo_DeclarationBlock_Clone(const StyleLockedDeclarationBlock *declarations);

bool Servo_DeclarationBlock_Equals(const StyleLockedDeclarationBlock *a,
                                   const StyleLockedDeclarationBlock *b);

void Servo_DeclarationBlock_GetCssText(const StyleLockedDeclarationBlock *declarations,
                                       nsACString *result);

void Servo_DeclarationBlock_SerializeOneValue(const StyleLockedDeclarationBlock *decls,
                                              const CSSPropertyId *property_id,
                                              nsACString *buffer,
                                              const StyleComputedValues *computed_values,
                                              const StylePerDocumentStyleData *data);

void Servo_SerializeFontValueForCanvas(const StyleLockedDeclarationBlock *declarations,
                                       nsACString *buffer);

uint32_t Servo_DeclarationBlock_Count(const StyleLockedDeclarationBlock *declarations);

bool Servo_DeclarationBlock_GetAt(const StyleLockedDeclarationBlock *declarations,
                                  uint32_t index,
                                  CSSPropertyId *result);

void Servo_DeclarationBlock_GetPropertyValue(const StyleLockedDeclarationBlock *declarations,
                                             const nsACString *property,
                                             nsACString *value);

void Servo_DeclarationBlock_GetPropertyValueByNonCustomId(const StyleLockedDeclarationBlock *declarations,
                                                          NonCustomCSSPropertyId property_id,
                                                          nsACString *value);

void Servo_DeclarationBlock_GetPropertyValueById(const StyleLockedDeclarationBlock *declarations,
                                                 const CSSPropertyId *property_id,
                                                 nsACString *value);

bool Servo_DeclarationBlock_GetPropertyIsImportant(const StyleLockedDeclarationBlock *declarations,
                                                   const nsACString *property);

bool Servo_DeclarationBlock_GetPropertyTypedValueList(const StyleLockedDeclarationBlock *declarations,
                                                      const CSSPropertyId *property_id,
                                                      StylePropertyTypedValueList *result);

void Servo_DeclarationBlock_SanitizeForCanvas(const StyleLockedDeclarationBlock *declarations);

bool Servo_DeclarationBlock_SetProperty(const StyleLockedDeclarationBlock *declarations,
                                        const nsACString *property,
                                        const nsACString *value,
                                        bool is_important,
                                        URLExtraData *data,
                                        StyleParsingMode parsing_mode,
                                        nsCompatibility quirks_mode,
                                        StyleLoader *loader,
                                        StyleCssRuleType rule_type,
                                        DeclarationBlockMutationClosure before_change_closure);

bool Servo_DeclarationBlock_SetPropertyToAnimationValue(const StyleLockedDeclarationBlock *declarations,
                                                        const StyleAnimationValue *animation_value,
                                                        DeclarationBlockMutationClosure before_change_closure);

bool Servo_DeclarationBlock_SetPropertyById(const StyleLockedDeclarationBlock *declarations,
                                            NonCustomCSSPropertyId property,
                                            const nsACString *value,
                                            bool is_important,
                                            URLExtraData *data,
                                            StyleParsingMode parsing_mode,
                                            nsCompatibility quirks_mode,
                                            StyleLoader *loader,
                                            StyleCssRuleType rule_type,
                                            DeclarationBlockMutationClosure before_change_closure);

nsresult Servo_DeclarationBlock_SetPropertyTypedValue(const StyleLockedDeclarationBlock *declarations,
                                                      const CSSPropertyId *property_id,
                                                      const nsACString *value,
                                                      URLExtraData *url_extra_data,
                                                      DeclarationBlockMutationClosure before_change_closure,
                                                      bool *changed);

bool Servo_DeclarationBlock_RemoveProperty(const StyleLockedDeclarationBlock *declarations,
                                           const nsACString *property,
                                           DeclarationBlockMutationClosure before_change_closure);

bool Servo_DeclarationBlock_RemovePropertyById(const StyleLockedDeclarationBlock *declarations,
                                               const CSSPropertyId *property_id,
                                               DeclarationBlockMutationClosure before_change_closure);

StyleStrong<StyleLockedDeclarationBlock> Servo_DeclarationBlock_Parse(const CSSPropertyId *property_id,
                                                                      const nsACString *value,
                                                                      URLExtraData *url_extra_data);

StyleNumericDeclaration *Servo_NumericDeclaration_Parse(const nsACString *text);

void Servo_NumericDeclaration_Drop(StyleNumericDeclaration *declaration);

void Servo_NumericDeclaration_GetValue(const StyleNumericDeclaration *declaration,
                                       StyleNumericValueResult *result);

bool Servo_NumericType_Create(const nsACString *unit, StyleNumericType *result);

void Servo_NumericType_Invert(StyleNumericType *numeric_type);

bool Servo_NumericType_AddTypes(const nsTArray<const StyleNumericType*> *numeric_types,
                                StyleNumericType *result);

bool Servo_NumericType_AddTypesFromValues(const nsTArray<StyleNumericType> *numeric_types,
                                          StyleNumericType *result);

bool Servo_NumericType_MultiplyTypes(const nsTArray<const StyleNumericType*> *numeric_types,
                                     StyleNumericType *result);

StyleSumValue *Servo_SumValue_Create(const StyleNumericValue *numeric_value);

void Servo_SumValue_Drop(StyleSumValue *sum_value);

/// Attempts to convert a sum value to a concrete unit.
///
/// Returns `Optional::Some` if the sum value can be converted to the
/// requested unit, or `Optional::None` if conversion is not possible.
///
/// Conversion may fail for valid reasons, such as:
/// - the sum value containing multiple items
/// - converting between incompatible units
void Servo_SumValue_ToUnit(const StyleSumValue *sum_value,
                           const nsACString *unit,
                           StyleOptional<StyleUnitValue> *result);

/// Attempts to convert a sum value to concrete units.
///
/// Returns `Optional::Some` if the sum value can be converted to the
/// requested units, or `Optional::None` if conversion is not possible.
///
/// Conversion may fail for valid reasons, such as:
/// - converting between incompatible units
/// - requested units not accounting for all items in the sum value
void Servo_SumValue_ToUnits(const StyleSumValue *sum_value,
                            const nsTArray<nsCString> *units,
                            StyleOptional<StyleMathSum> *result);

void Servo_ImageValue_ToCss(const StyleImageValue *image_value,
                            nsACString *value);

StyleStrong<StyleLockedMediaList> Servo_MediaList_Create();

StyleStrong<StyleLockedMediaList> Servo_MediaList_DeepClone(const StyleLockedMediaList *list);

bool Servo_MediaList_Matches(const StyleLockedMediaList *list,
                             const StylePerDocumentStyleData *raw_data);

bool Servo_DeclarationBlock_HasCSSWideKeyword(const StyleLockedDeclarationBlock *declarations,
                                              NonCustomCSSPropertyId property);

void Servo_MediaList_GetText(const StyleLockedMediaList *list,
                             nsACString *result);

void Servo_MediaList_SetText(const StyleLockedMediaList *list,
                             const nsACString *text,
                             StyleCallerType caller_type);

bool Servo_MediaList_IsViewportDependent(const StyleLockedMediaList *list);

uint32_t Servo_MediaList_GetLength(const StyleLockedMediaList *list);

bool Servo_MediaList_GetMediumAt(const StyleLockedMediaList *list,
                                 uint32_t index,
                                 nsACString *result);

void Servo_MediaList_AppendMedium(const StyleLockedMediaList *list,
                                  const nsACString *new_medium);

bool Servo_MediaList_DeleteMedium(const StyleLockedMediaList *list,
                                  const nsACString *old_medium);

size_t Servo_MediaList_SizeOfIncludingThis(StyleGeckoMallocSizeOf malloc_size_of,
                                           StyleGeckoMallocSizeOf malloc_enclosing_size_of,
                                           const StyleLockedMediaList *list);

bool Servo_DeclarationBlock_HasProperty(const StyleLockedDeclarationBlock *decls,
                                        const CSSPropertyId *id);

bool Servo_DeclarationBlock_HasLonghandProperty(const StyleLockedDeclarationBlock *declarations,
                                                const nsACString *property);

void Servo_DeclarationBlock_SetIdentStringValue(const StyleLockedDeclarationBlock *declarations,
                                                NonCustomCSSPropertyId property,
                                                nsAtom *value);

bool Servo_DeclarationBlock_SetKeywordValue(const StyleLockedDeclarationBlock *declarations,
                                            NonCustomCSSPropertyId property,
                                            int32_t value);

void Servo_DeclarationBlock_SetIntValue(const StyleLockedDeclarationBlock *declarations,
                                        NonCustomCSSPropertyId property,
                                        int32_t value);

void Servo_DeclarationBlock_SetMathDepthValue(const StyleLockedDeclarationBlock *declarations,
                                              int32_t value,
                                              bool is_relative);

void Servo_DeclarationBlock_SetCounterResetListItem(const StyleLockedDeclarationBlock *declarations,
                                                    int32_t counter_value,
                                                    bool is_reversed);

void Servo_DeclarationBlock_SetCounterSetListItem(const StyleLockedDeclarationBlock *declarations,
                                                  int32_t counter_value);

void Servo_DeclarationBlock_SetPixelValue(const StyleLockedDeclarationBlock *declarations,
                                          NonCustomCSSPropertyId property,
                                          float value);

bool Servo_DeclarationBlock_SetLengthValue(const StyleLockedDeclarationBlock *declarations,
                                           NonCustomCSSPropertyId property,
                                           float value,
                                           nsCSSUnit unit);

bool Servo_DeclarationBlock_SetTransform(const StyleLockedDeclarationBlock *declarations,
                                         NonCustomCSSPropertyId property,
                                         const nsTArray<StyleTransformOperation> *ops);

bool Servo_DeclarationBlock_SetBackdropFilter(const StyleLockedDeclarationBlock *declarations,
                                              NonCustomCSSPropertyId property,
                                              const StyleOwnedSlice<StyleFilter> *filters);

bool Servo_DeclarationBlock_SetColorScheme(const StyleLockedDeclarationBlock *declarations,
                                           NonCustomCSSPropertyId property,
                                           const StyleColorScheme *color_scheme);

void Servo_DeclarationBlock_SetPathValue(const StyleLockedDeclarationBlock *declarations,
                                         NonCustomCSSPropertyId property,
                                         const StyleSVGPathData *path);

void Servo_CreatePathDataFromCommands(nsTArray<StylePathCommand> *path_commands,
                                      StyleSVGPathData *dest);

bool Servo_SVGPathData_Add(StyleSVGPathData *dest,
                           const StyleSVGPathData *to_add,
                           uint32_t count);

bool Servo_SVGPathData_Parse(const nsACString *input, StyleSVGPathData *dest);

void Servo_SVGPathData_NormalizeAndReduce(const StyleSVGPathData *input,
                                          StyleSVGPathData *dest);

void Servo_SVGPathData_ToString(const StyleSVGPathData *path, nsACString *dest);

bool Servo_SVGPathData_Interpolate(const StyleSVGPathData *left,
                                   const StyleSVGPathData *right,
                                   double progress,
                                   StyleSVGPathData *dest);

void Servo_DeclarationBlock_SetPercentValue(const StyleLockedDeclarationBlock *declarations,
                                            NonCustomCSSPropertyId property,
                                            float value);

void Servo_DeclarationBlock_SetAutoValue(const StyleLockedDeclarationBlock *declarations,
                                         NonCustomCSSPropertyId property);

void Servo_DeclarationBlock_SetCurrentColor(const StyleLockedDeclarationBlock *declarations,
                                            NonCustomCSSPropertyId property);

void Servo_DeclarationBlock_SetColorValue(const StyleLockedDeclarationBlock *declarations,
                                          NonCustomCSSPropertyId property,
                                          nscolor value);

void Servo_DeclarationBlock_SetFontFamily(const StyleLockedDeclarationBlock *declarations,
                                          const nsACString *value);

void Servo_DeclarationBlock_SetBackgroundImage(const StyleLockedDeclarationBlock *declarations,
                                               const nsACString *value,
                                               URLExtraData *raw_extra_data);

void Servo_DeclarationBlock_SetTextDecorationColorOverride(const StyleLockedDeclarationBlock *declarations);

void Servo_DeclarationBlock_SetAspectRatio(const StyleLockedDeclarationBlock *declarations,
                                           float width,
                                           float height);

bool Servo_CSSSupports2(const nsACString *property, const nsACString *value);

bool Servo_CSSSupports(const nsACString *cond,
                       const StyleCssSupportsParams *params,
                       URLExtraData *raw_extra_data,
                       StyleCssRuleType rule_type);

bool Servo_CSSSupportsForImport(const nsACString *after_rule);

void Servo_NoteExplicitHints(const StyleRawGeckoElement *element,
                             StyleRestyleHint restyle_hint,
                             nsChangeHint change_hint);

uint32_t Servo_TakeChangeHint(const StyleRawGeckoElement *element,
                              bool *was_restyled);

StyleStrong<StyleComputedValues> Servo_ResolveStyle(const StyleRawGeckoElement *element);

StyleStrong<StyleComputedValues> Servo_ResolveStyleLazily(const StyleRawGeckoElement *element,
                                                          PseudoStyleType pseudo_type,
                                                          nsAtom *functional_pseudo_parameter,
                                                          StyleRuleInclusion rule_inclusion,
                                                          const ServoElementSnapshotTable *snapshots,
                                                          uint64_t cache_generation,
                                                          bool can_use_cache,
                                                          const StylePerDocumentStyleData *raw_data);

StyleStrong<StyleComputedValues> Servo_ReparentStyle(const StyleComputedValues *style_to_reparent,
                                                     const StyleComputedValues *parent_style,
                                                     const StyleComputedValues *layout_parent_style,
                                                     const StyleRawGeckoElement *element,
                                                     const StylePerDocumentStyleData *raw_data);

void Servo_GetComputedKeyframeValues(const nsTArray<Keyframe> *keyframes,
                                     const StyleRawGeckoElement *element,
                                     PseudoStyleType pseudo_type,
                                     const StyleComputedValues *style,
                                     const StylePerDocumentStyleData *raw_data,
                                     nsTArray<ComputedKeyframeValues> *computed_keyframes);

void Servo_GetAnimationValues(const StyleLockedDeclarationBlock *declarations,
                              const StyleRawGeckoElement *element,
                              const StyleComputedValues *style,
                              const StylePerDocumentStyleData *raw_data,
                              nsTArray<RefPtr<StyleAnimationValue>> *animation_values);

void Servo_AnimationValue_GetPropertyId(const StyleAnimationValue *value,
                                        CSSPropertyId *property_id);

StyleStrong<StyleAnimationValue> Servo_AnimationValue_Compute(const StyleRawGeckoElement *element,
                                                              const StyleLockedDeclarationBlock *declarations,
                                                              const StyleComputedValues *style,
                                                              const StylePerDocumentStyleData *raw_data);

bool Servo_ParseAnimationRangeStart(const nsACString *value,
                                    StyleAnimationRangeStart *output);

bool Servo_ParseAnimationRangeEnd(const nsACString *value,
                                  StyleAnimationRangeEnd *output);

void Servo_AssertTreeIsClean(const StyleRawGeckoElement *root);

bool Servo_IsWorkerThread();

bool Servo_StyleSet_GetKeyframesForName(const StylePerDocumentStyleData *raw_data,
                                        const StyleRawGeckoElement *element,
                                        const StyleComputedValues *style,
                                        nsAtom *name,
                                        const StyleComputedTimingFunction *inherited_timing_function,
                                        nsTArray<Keyframe> *keyframes);

void Servo_StyleSet_GetFontFaceRules(const StylePerDocumentStyleData *raw_data,
                                     nsTArray<nsFontFaceRuleContainer> *rules);

const StyleLockedCounterStyleRule *Servo_StyleSet_GetCounterStyleRule(const StylePerDocumentStyleData *raw_data,
                                                                      nsAtom *name);

StyleStrong<StyleViewTransitionRule> Servo_StyleSet_GetLastViewTransitionRule(const StylePerDocumentStyleData *raw_data);

gfxFontFeatureValueSet *Servo_StyleSet_BuildFontFeatureValueSet(const StylePerDocumentStyleData *raw_data);

gfx::FontPaletteValueSet *Servo_StyleSet_BuildFontPaletteValueSet(const StylePerDocumentStyleData *raw_data);

StyleStrong<StyleComputedValues> Servo_StyleSet_ResolveForDeclarations(const StylePerDocumentStyleData *raw_data,
                                                                       const StyleComputedValues *parent_style_context,
                                                                       const StyleLockedDeclarationBlock *declarations);

void Servo_StyleSet_AddSizeOfExcludingThis(StyleGeckoMallocSizeOf malloc_size_of,
                                           StyleGeckoMallocSizeOf malloc_enclosing_size_of,
                                           ServoStyleSetSizes *sizes,
                                           const StylePerDocumentStyleData *raw_data);

void Servo_UACache_AddSizeOf(StyleGeckoMallocSizeOf malloc_size_of,
                             StyleGeckoMallocSizeOf malloc_enclosing_size_of,
                             ServoStyleSetSizes *sizes);

bool Servo_StyleSet_MightHaveAttributeDependency(const StylePerDocumentStyleData *raw_data,
                                                 const StyleRawGeckoElement *element,
                                                 nsAtom *local_name);

StyleContainerAttributeDependencyKind Servo_StyleSet_MightHaveAttributeDependencyInContainer(const StylePerDocumentStyleData *raw_data,
                                                                                             const StyleRawGeckoElement *element,
                                                                                             nsAtom *local_name);

bool Servo_StyleSet_MightHaveNthOfIDDependency(const StylePerDocumentStyleData *raw_data,
                                               const StyleRawGeckoElement *element,
                                               nsAtom *old_id,
                                               nsAtom *new_id);

bool Servo_StyleSet_MightHaveNthOfClassDependency(const StylePerDocumentStyleData *raw_data,
                                                  const StyleRawGeckoElement *element,
                                                  const ServoElementSnapshotTable *snapshots);

bool Servo_StyleSet_MightHaveNthOfAttributeDependency(const StylePerDocumentStyleData *raw_data,
                                                      const StyleRawGeckoElement *element,
                                                      nsAtom *local_name);

void Servo_StyleSet_MaybeInvalidateRelativeSelectorIDDependency(const StylePerDocumentStyleData *raw_data,
                                                                const StyleRawGeckoElement *element,
                                                                nsAtom *old_id,
                                                                nsAtom *new_id,
                                                                const ServoElementSnapshotTable *snapshots);

void Servo_StyleSet_MaybeInvalidateRelativeSelectorClassDependency(const StylePerDocumentStyleData *raw_data,
                                                                   const StyleRawGeckoElement *element,
                                                                   const ServoElementSnapshotTable *snapshots);

void Servo_StyleSet_MaybeInvalidateRelativeSelectorAttributeDependency(const StylePerDocumentStyleData *raw_data,
                                                                       const StyleRawGeckoElement *element,
                                                                       nsAtom *local_name,
                                                                       const ServoElementSnapshotTable *snapshots);

void Servo_StyleSet_MaybeInvalidateRelativeSelectorStateDependency(const StylePerDocumentStyleData *raw_data,
                                                                   const StyleRawGeckoElement *element,
                                                                   uint64_t state,
                                                                   const ServoElementSnapshotTable *snapshots);

void Servo_StyleSet_MaybeInvalidateRelativeSelectorCustomStateDependency(const StylePerDocumentStyleData *raw_data,
                                                                         const StyleRawGeckoElement *element,
                                                                         nsAtom *state,
                                                                         const ServoElementSnapshotTable *snapshots);

void Servo_StyleSet_MaybeInvalidateRelativeSelectorEmptyDependency(const StylePerDocumentStyleData *raw_data,
                                                                   const StyleRawGeckoElement *element);

void Servo_StyleSet_MaybeInvalidateRelativeSelectorNthEdgeDependency(const StylePerDocumentStyleData *raw_data,
                                                                     const StyleRawGeckoElement *element,
                                                                     StyleRelativeSelectorNthEdgeInvalidateFor invalidate_for);

void Servo_StyleSet_MaybeInvalidateRelativeSelectorNthDependencyFromSibling(const StylePerDocumentStyleData *raw_data,
                                                                            const StyleRawGeckoElement *element,
                                                                            bool force);

void Servo_StyleSet_MaybeInvalidateRelativeSelectorForInsertion(const StylePerDocumentStyleData *raw_data,
                                                                const StyleRawGeckoElement *element);

void Servo_StyleSet_MaybeInvalidateRelativeSelectorForAppend(const StylePerDocumentStyleData *raw_data,
                                                             const StyleRawGeckoNode *first_node);

void Servo_StyleSet_MaybeInvalidateRelativeSelectorForRemoval(const StylePerDocumentStyleData *raw_data,
                                                              const StyleRawGeckoElement *element);

bool Servo_StyleSet_HasStateDependency(const StylePerDocumentStyleData *raw_data,
                                       const StyleRawGeckoElement *element,
                                       uint64_t state);

bool Servo_StyleSet_HasNthOfCustomStateDependency(const StylePerDocumentStyleData *raw_data,
                                                  const StyleRawGeckoElement *element,
                                                  nsAtom *state);

bool Servo_StyleSet_HasNthOfStateDependency(const StylePerDocumentStyleData *raw_data,
                                            const StyleRawGeckoElement *element,
                                            uint64_t state);

void Servo_StyleSet_RestyleSiblingsForNthOf(const StyleRawGeckoElement *element,
                                            uint32_t flags);

bool Servo_StyleSet_HasDocumentStateDependency(const StylePerDocumentStyleData *raw_data,
                                               uint64_t state);

void Servo_GetComputedValue(const StyleComputedValues *style,
                            NonCustomCSSPropertyId prop,
                            nsACString *value);

void Servo_GetResolvedValue(const StyleComputedValues *style,
                            NonCustomCSSPropertyId prop,
                            const StylePerDocumentStyleData *raw_data,
                            const StyleRawGeckoElement *element,
                            nsACString *value);

bool Servo_ComputedValues_GetPropertyTypedValueList(const StyleComputedValues *style,
                                                    const CSSPropertyId *property_id,
                                                    StylePropertyTypedValueList *result);

bool Servo_GetCustomPropertyValue(const StyleComputedValues *style,
                                  const nsACString *name,
                                  const StylePerDocumentStyleData *raw_data,
                                  const StyleRawGeckoElement *element,
                                  nsACString *value);

uint32_t Servo_GetCustomPropertiesCount(const StyleComputedValues *computed_values);

bool Servo_ComputedValues_HasCustomProperty(const StyleComputedValues *cv,
                                            nsAtom *prop);

nsAtom *Servo_GetCustomPropertyNameAt(const StyleComputedValues *computed_values,
                                      uint32_t index);

bool Servo_CssUrl_IsLocalRef(const StyleCssUrl *url);

void Servo_ProcessInvalidations(const StylePerDocumentStyleData *set,
                                const StyleRawGeckoElement *element,
                                const ServoElementSnapshotTable *snapshots);

bool Servo_HasPendingRestyleAncestor(const StyleRawGeckoElement *element,
                                     bool may_need_to_flush_layout);

StyleSelectorList *Servo_SelectorList_Parse(const nsACString *selector_list,
                                            bool is_chrome);

void Servo_SelectorList_Drop(StyleSelectorList *list);

bool Servo_IsValidCSSColor(const nsACString *value);

bool Servo_IsValidCSSImage(const nsACString *value);

bool Servo_ComputeColor(const StylePerDocumentStyleData *raw_data,
                        const nsACString *value,
                        StyleAbsoluteColor *result_color,
                        bool *was_current_color,
                        StyleLoader *loader);

void Servo_AbsoluteColor_ToCss(const StyleAbsoluteColor *s, nsACString *result);

bool Servo_ColorTo(const nsACString *from_color,
                   const nsACString *to_color_space,
                   nsACString *result_color,
                   nsTArray<float> *result_components,
                   bool *result_adjusted,
                   StyleLoader *loader);

StyleAbsoluteColor Servo_ResolveColor(const StyleColor *color,
                                      const StyleAbsoluteColor *foreground);

float Servo_ResolveCalcLengthPercentage(const StyleCalcLengthPercentage *calc,
                                        float basis);

void Servo_ResolveAnchorFunctionsInCalcPercentage(const StyleLengthPercentage *lp,
                                                  const StyleAllowAnchorPosResolutionInCalcPercentage *allowed,
                                                  const AnchorPosOffsetResolutionParams *params,
                                                  StyleCalcAnchorPositioningFunctionResolution *out);

StyleAbsoluteColor Servo_ConvertColorSpace(const StyleAbsoluteColor *color,
                                           StyleColorSpace color_space);

StyleAbsoluteColor Servo_GamutMapColorUsingBinarySearchMINDE(const StyleAbsoluteColor *color,
                                                             StyleColorSpace destination_color_space);

StyleAbsoluteColor Servo_GamutMapColorUsingRaytrace(const StyleAbsoluteColor *color,
                                                    StyleColorSpace destination_color_space);

bool Servo_IntersectionObserverMargin_Parse(const nsACString *value,
                                            StyleIntersectionObserverMargin *result);

void Servo_IntersectionObserverMargin_ToString(const StyleIntersectionObserverMargin *root_margin,
                                               nsACString *result);

bool Servo_ParseTransformIntoMatrix(const nsACString *value,
                                    bool *contain_3d,
                                    StyleMatrix4x4Components *result);

bool Servo_ParseFilters(const nsACString *value,
                        bool ignore_urls,
                        URLExtraData *data,
                        StyleOwnedSlice<StyleFilter> *out);

bool Servo_ParseFontShorthandForMatching(const nsACString *value,
                                         URLExtraData *data,
                                         StyleFontFamilyList *family,
                                         StyleFontStyle *style,
                                         StyleFontWidth *width,
                                         StyleFontWeight *weight,
                                         float *size,
                                         bool *small_caps);

StyleSourceSizeList *Servo_SourceSizeList_Parse(const nsACString *value);

int32_t Servo_SourceSizeList_Evaluate(const StylePerDocumentStyleData *raw_data,
                                      const StyleSourceSizeList *list);

void Servo_SourceSizeList_Drop(StyleSourceSizeList *list);

void Servo_InvalidateStyleForDocStateChanges(const StyleRawGeckoElement *root,
                                             const StylePerDocumentStyleData *document_style,
                                             const nsTArray<const StyleAuthorStyles*> *non_document_styles,
                                             uint64_t states_changed);

uint64_t Servo_PseudoClass_GetStates(const nsACString *name);

StyleUseCounters *Servo_UseCounters_Create();

void Servo_UseCounters_Drop(StyleUseCounters *c);

void Servo_UseCounters_Merge(const StyleUseCounters *doc_counters,
                             const StyleUseCounters *sheet_counters);

bool Servo_IsPropertyIdRecordedInUseCounter(const StyleUseCounters *use_counters,
                                            NonCustomCSSPropertyId id);

bool Servo_IsUnknownPropertyRecordedInUseCounter(const StyleUseCounters *use_counters,
                                                 CountedUnknownProperty p);

bool Servo_IsCustomUseCounterRecorded(const StyleUseCounters *use_counters,
                                      StyleCustomUseCounter c);

bool Servo_IsCssPropertyRecordedInUseCounter(const StyleUseCounters *use_counters,
                                             const nsACString *property,
                                             bool *known_prop);

StyleSharedMemoryBuilder *Servo_SharedMemoryBuilder_Create(uint8_t *buffer,
                                                           size_t len);

const StyleLockedCssRules *Servo_SharedMemoryBuilder_AddStylesheet(StyleSharedMemoryBuilder *builder,
                                                                   const StyleStylesheetContents *contents,
                                                                   nsACString *error_message);

size_t Servo_SharedMemoryBuilder_GetLength(const StyleSharedMemoryBuilder *builder);

void Servo_SharedMemoryBuilder_Drop(StyleSharedMemoryBuilder *builder);

void *Servo_StyleArcSlice_EmptyPtr();

const StyleLoadData *Servo_LoadData_GetLazy(const StyleLoadDataSource *source);

void Servo_LengthPercentage_ToCss(const StyleLengthPercentage *lp,
                                  nsACString *result);

void Servo_FontStyle_ToCss(const StyleFontStyle *s, nsACString *result);

void Servo_FontWeight_ToCss(const StyleFontWeight *w, nsACString *result);

void Servo_FontWidth_ToCss(const StyleFontWidth *s, nsACString *result);

bool Servo_FontWidth_SerializeKeyword(const StyleFontWidth *s,
                                      nsACString *result);

bool Servo_CursorKind_Parse(const nsACString *cursor, StyleCursorKind *result);

const StyleFontFamily *Servo_FontFamily_Generic(StyleGenericFontFamily generic);

void Servo_FontFamily_ForSystemFont(const nsACString *name,
                                    StyleFontFamily *out);

void Servo_FontFamilyList_WithNames(const nsTArray<StyleSingleFontFamily> *names,
                                    StyleFontFamilyList *out);

void Servo_FamilyName_Serialize(const StyleFamilyName *name,
                                nsACString *result);

StyleGenericFontFamily Servo_GenericFontFamily_Parse(const nsACString *input);

bool Servo_ColorScheme_Parse(const nsACString *input, uint8_t *out);

void Servo_LayerBlockRule_GetName(const StyleLayerBlockRule *rule,
                                  nsACString *result);

void Servo_ScopeRule_GetStart(const StyleScopeRule *rule, nsACString *result);

void Servo_ScopeRule_GetEnd(const StyleScopeRule *rule, nsACString *result);

size_t Servo_LayerStatementRule_GetNameCount(const StyleLayerStatementRule *rule);

void Servo_LayerStatementRule_GetNameAt(const StyleLayerStatementRule *rule,
                                        size_t index,
                                        nsACString *result);

StyleNavigationType Servo_ViewTransitionRule_GetNavigationDescriptor(const StyleViewTransitionRule *rule);

void Servo_ViewTransitionRule_GetNavigation(const StyleViewTransitionRule *rule,
                                            nsACString *result);

void Servo_ViewTransitionRule_GetTypes(const StyleViewTransitionRule *rule,
                                       nsTArray<nsAtom*> *result);

void Servo_InvalidateForViewportUnits(const StylePerDocumentStyleData *document_style,
                                      const StyleRawGeckoElement *root,
                                      bool dynamic_only);

StyleAbsoluteColor Servo_InterpolateColor(StyleColorInterpolationMethod interpolation,
                                          const StyleAbsoluteColor *start_color,
                                          const StyleAbsoluteColor *end_color,
                                          float progress);

double Servo_EasingFunctionAt(const StyleComputedTimingFunction *easing_function,
                              double progress,
                              StyleEasingBeforeFlag before_flag);

bool Servo_ParseLengthWithoutStyleContext(const nsACString *len,
                                          float *out,
                                          GeckoFontMetrics (*get_font_metrics)(void*),
                                          void *getter_context);

bool Servo_SlowRgbToColorName(uint8_t r,
                              uint8_t g,
                              uint8_t b,
                              nsACString *result);

bool Servo_SlowRgbToNearestColorName(float r,
                                     float g,
                                     float b,
                                     StyleColorSpace color_space,
                                     nsACString *result);

bool Servo_ColorNameToRgb(const nsACString *name, StyleAbsoluteColor *out);

/// https://drafts.css-houdini.org/css-properties-values-api-1/#the-registerproperty-function
StyleRegisterCustomPropertyResult Servo_RegisterCustomProperty(const StylePerDocumentStyleData *per_doc_data,
                                                               URLExtraData *extra_data,
                                                               const nsACString *name,
                                                               const nsACString *syntax,
                                                               bool inherits,
                                                               const nsACString *initial_value);

void Servo_GetRegisteredCustomProperties(const StylePerDocumentStyleData *per_doc_data,
                                         nsTArray<StylePropDef> *custom_properties);

bool Servo_GetRegisteredCustomProperty(const StylePerDocumentStyleData *per_doc_data,
                                       const nsACString *name,
                                       StylePropDef *custom_property);

bool Servo_Value_Matches_Syntax(const nsACString *property,
                                const nsACString *value,
                                const nsACString *syntax,
                                URLExtraData *extra_data);

void Servo_GetSelectorWarnings(const StyleLockedStyleRule *rule,
                               nsTArray<StyleSelectorWarningData> *warnings);

void Servo_GetRuleBodyText(const nsACString *initial_text, nsACString *ret_val);

void Servo_ReplaceBlockRuleBodyTextInStylesheetText(const nsACString *stylesheet_text,
                                                    uint32_t line,
                                                    uint32_t column,
                                                    const nsACString *new_body_text,
                                                    nsACString *ret_val);

StyleParserState *Servo_CSSParser_create(const nsACString *text);

void Servo_CSSParser_destroy(StyleParserState *state);

uint32_t Servo_CSSParser_GetCurrentLine(const StyleParserState *state);

uint32_t Servo_CSSParser_GetCurrentColumn(const StyleParserState *state);

bool Servo_CSSParser_NextToken(const nsACString *text,
                               StyleParserState *state,
                               StyleCSSToken *css_token);

void Servo_ResolveAnchorFunction(const StyleAnchorFunction *func,
                                 const AnchorPosOffsetResolutionParams *params,
                                 StylePhysicalSide prop_side,
                                 StyleAnchorPositioningFunctionResolution *out);

void Servo_ResolveAnchorSizeFunctionForInset(const StyleGenericAnchorSizeFunction<StyleInset> *func,
                                             const AnchorPosOffsetResolutionParams *params,
                                             StylePhysicalAxis prop_axis,
                                             StyleAnchorPositioningFunctionResolution *out);

void Servo_ResolveAnchorSizeFunctionForMargin(const StyleGenericAnchorSizeFunction<StyleMargin> *func,
                                              const AnchorPosResolutionParams *params,
                                              StylePhysicalAxis prop_axis,
                                              StyleAnchorPositioningFunctionResolution *out);

void Servo_ResolveAnchorSizeFunctionForSize(const StyleGenericAnchorSizeFunction<StyleSize> *func,
                                            const AnchorPosResolutionParams *params,
                                            StylePhysicalAxis prop_axis,
                                            StyleAnchorPositioningFunctionResolution *out);

void Servo_ResolveAnchorSizeFunctionForMaxSize(const StyleGenericAnchorSizeFunction<StyleMaxSize> *func,
                                               const AnchorPosResolutionParams *params,
                                               StylePhysicalAxis prop_axis,
                                               StyleAnchorPositioningFunctionResolution *out);

void Servo_PhysicalizePositionArea(StylePositionArea *area,
                                   const StyleWritingMode *cb_wm,
                                   const StyleWritingMode *self_wm);

/// https://drafts.csswg.org/css-anchor-position-1/#position-area-alignment
void Servo_ResolvePositionAreaSelfAlignment(const StylePositionArea *area,
                                            StyleLogicalAxis axis,
                                            const StyleWritingMode *cb_wm,
                                            const StyleWritingMode *self_wm,
                                            StyleAlignFlags *out);

const StyleRawShadowRoot *Servo_GetShadowRootForScoped(const StyleRawGeckoElement *element,
                                                       StyleCascadeLevel scope);

void Servo_GetSubstitutedValue(const nsACString *str,
                               const StyleRawGeckoElement *raw_element,
                               PseudoStyleType pseudo_type,
                               const StyleComputedValues *style,
                               const StylePerDocumentStyleData *raw_data,
                               nsACString *out);

void Servo_GetComputationStepsSupportedCSSFunctions(nsTArray<nsCString> *out);

void Servo_GetComputationSteps(const nsACString *string,
                               const StyleRawGeckoElement *raw_element,
                               PseudoStyleType pseudo_type,
                               const StyleComputedValues *style,
                               const StylePerDocumentStyleData *raw_data,
                               float percentage_basis,
                               nsTArray<nsCString> *out);

StyleTextTransformCase Servo_TextTransform_Case(StyleTextTransform text_transform);

/// Matches <length>.
bool Servo_NumericType_MatchesLength(const StyleNumericType *self);

/// Matches <angle>.
bool Servo_NumericType_MatchesAngle(const StyleNumericType *self);

/// Matches <percentage>.
bool Servo_NumericType_MatchesPercentage(const StyleNumericType *self);

/// Matches <length-percentage>.
bool Servo_NumericType_MatchesLengthPercentage(const StyleNumericType *self);

/// Matches <number>.
bool Servo_NumericType_MatchesNumber(const StyleNumericType *self);

}  // extern "C"

}  // namespace mozilla

#pragma pop_macro("STRICT")
#pragma pop_macro("TRANSPARENT")

#endif // mozilla_ServoStyleConsts_h

#pragma GCC diagnostic pop
#include "mozilla/ServoStyleConstsInlines.h"
