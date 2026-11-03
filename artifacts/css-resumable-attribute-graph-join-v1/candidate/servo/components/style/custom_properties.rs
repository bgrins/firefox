/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

//! Support for [custom properties for cascading variables][custom].
//!
//! [custom]: https://drafts.csswg.org/css-variables/

use crate::FxHashMap;
use crate::computed_value_flags::ComputedValueFlags;
use crate::custom_properties_map::{CustomPropertiesMap, OwnMap};
use crate::device::Device;
use crate::dom::AttributeTracker;
use crate::properties::{CSSWideKeyword, PrioritaryPropertyId, PropertyIdRef};
use crate::properties_and_values::{
    rule::Descriptors as PropertyDescriptors,
    syntax::Descriptor as SyntaxDescriptor,
    value::{
        AllowComputationallyDependent, ComputedValue as ComputedRegisteredValue,
        SpecifiedValue as SpecifiedRegisteredValue,
    },
};
use crate::selector_map::PrecomputedHashMap;
use crate::stylesheets::UrlExtraData;
use crate::stylesheets::container_rule::AttrReferenceSet;
use crate::stylist::Stylist;
use crate::typed_om::{
    ToTyped, TypedValue, UnparsedSegment, UnparsedValue, VariableReferenceValue,
};
use crate::values::computed;
use crate::values::computed::ToComputedValue;
use crate::values::generics::calc::SortKey as AttrUnit;
use crate::values::specified::{NoCalcLength, ParsedNamespace};
use crate::{Atom, LocalName, Namespace, Prefix, derives::*};
use cssparser::{CowRcStr, Delimiter, Parser, SourcePosition, Token, TokenSerializationType};
use selectors::parser::SelectorParseErrorKind;
use servo_arc::Arc;
use smallvec::SmallVec;
use std::borrow::Cow;
use std::fmt::{self, Write};
use std::num;
use std::ops::{Index, IndexMut};
use style_traits::{CssString, CssWriter, ParseError, StyleParseErrorKind, ToCss};
use thin_vec::ThinVec;

/// The environment from which to get `env` function values.
///
/// TODO(emilio): If this becomes a bit more complex we should probably move it
/// to the `media_queries` module, or something.
#[derive(Debug, MallocSizeOf)]
pub struct CssEnvironment;

type EnvironmentEvaluator = fn(device: &Device, url_data: &UrlExtraData) -> VariableValue;

struct EnvironmentVariable {
    name: Atom,
    evaluator: EnvironmentEvaluator,
}

macro_rules! make_variable {
    ($name:expr, $evaluator:expr) => {{
        EnvironmentVariable {
            name: $name,
            evaluator: $evaluator,
        }
    }};
}

fn get_safearea_inset_top(device: &Device, url_data: &UrlExtraData) -> VariableValue {
    VariableValue::pixels(device.safe_area_insets().top, url_data)
}

fn get_safearea_inset_bottom(device: &Device, url_data: &UrlExtraData) -> VariableValue {
    VariableValue::pixels(device.safe_area_insets().bottom, url_data)
}

fn get_safearea_inset_left(device: &Device, url_data: &UrlExtraData) -> VariableValue {
    VariableValue::pixels(device.safe_area_insets().left, url_data)
}

fn get_safearea_inset_right(device: &Device, url_data: &UrlExtraData) -> VariableValue {
    VariableValue::pixels(device.safe_area_insets().right, url_data)
}

#[cfg(feature = "gecko")]
fn get_content_preferred_color_scheme(device: &Device, url_data: &UrlExtraData) -> VariableValue {
    use crate::queries::values::PrefersColorScheme;
    let prefers_color_scheme = unsafe {
        crate::gecko_bindings::bindings::Gecko_MediaFeatures_PrefersColorScheme(
            device.document(),
            /* use_content = */ true,
        )
    };
    VariableValue::ident(
        match prefers_color_scheme {
            PrefersColorScheme::Light => "light",
            PrefersColorScheme::Dark => "dark",
        },
        url_data,
    )
}

#[cfg(feature = "servo")]
fn get_content_preferred_color_scheme(_device: &Device, url_data: &UrlExtraData) -> VariableValue {
    // TODO: Add an implementation for Servo.
    VariableValue::ident("light", url_data)
}

fn get_scrollbar_inline_size(device: &Device, url_data: &UrlExtraData) -> VariableValue {
    VariableValue::pixels(device.scrollbar_inline_size().px(), url_data)
}

fn get_hairline(device: &Device, url_data: &UrlExtraData) -> VariableValue {
    VariableValue::pixels(
        app_units::Au(device.app_units_per_device_pixel()).to_f32_px(),
        url_data,
    )
}

static ENVIRONMENT_VARIABLES: [EnvironmentVariable; 4] = [
    make_variable!(atom!("safe-area-inset-top"), get_safearea_inset_top),
    make_variable!(atom!("safe-area-inset-bottom"), get_safearea_inset_bottom),
    make_variable!(atom!("safe-area-inset-left"), get_safearea_inset_left),
    make_variable!(atom!("safe-area-inset-right"), get_safearea_inset_right),
];

#[cfg(feature = "gecko")]
macro_rules! lnf_int {
    ($id:ident) => {
        unsafe {
            crate::gecko_bindings::bindings::Gecko_GetLookAndFeelInt(
                crate::gecko_bindings::bindings::LookAndFeel_IntID::$id as i32,
            )
        }
    };
}

#[cfg(feature = "servo")]
macro_rules! lnf_int {
    ($id:ident) => {
        // TODO: Add an implementation for Servo.
        0
    };
}

macro_rules! lnf_int_variable {
    ($atom:expr, $id:ident, $ctor:ident) => {{
        fn __eval(_: &Device, url_data: &UrlExtraData) -> VariableValue {
            VariableValue::$ctor(lnf_int!($id), url_data)
        }
        make_variable!($atom, __eval)
    }};
}

fn eval_gtk_csd_titlebar_radius(device: &Device, url_data: &UrlExtraData) -> VariableValue {
    let int_pixels = lnf_int!(TitlebarRadius);
    let unzoomed_scale =
        device.device_pixel_ratio_ignoring_full_zoom().get() / device.device_pixel_ratio().get();
    VariableValue::pixels(int_pixels as f32 * unzoomed_scale, url_data)
}

static CHROME_ENVIRONMENT_VARIABLES: [EnvironmentVariable; 9] = [
    make_variable!(
        atom!("-moz-gtk-csd-titlebar-radius"),
        eval_gtk_csd_titlebar_radius
    ),
    lnf_int_variable!(
        atom!("-moz-gtk-csd-tooltip-radius"),
        TooltipRadius,
        int_pixels
    ),
    lnf_int_variable!(
        atom!("-moz-gtk-csd-close-button-position"),
        GTKCSDCloseButtonPosition,
        integer
    ),
    lnf_int_variable!(
        atom!("-moz-gtk-csd-minimize-button-position"),
        GTKCSDMinimizeButtonPosition,
        integer
    ),
    lnf_int_variable!(
        atom!("-moz-gtk-csd-maximize-button-position"),
        GTKCSDMaximizeButtonPosition,
        integer
    ),
    lnf_int_variable!(
        atom!("-moz-overlay-scrollbar-fade-duration"),
        ScrollbarFadeDuration,
        int_ms
    ),
    make_variable!(
        atom!("-moz-content-preferred-color-scheme"),
        get_content_preferred_color_scheme
    ),
    make_variable!(atom!("scrollbar-inline-size"), get_scrollbar_inline_size),
    make_variable!(atom!("hairline"), get_hairline),
];

impl CssEnvironment {
    /// Get an env() variable, either custom or not.
    #[inline]
    pub fn get(
        &self,
        name: &Atom,
        device: &Device,
        url_data: &UrlExtraData,
    ) -> Option<VariableValue> {
        #[cfg(feature = "gecko")]
        let is_link_parameter = name.as_slice().starts_with(&[b'-' as u16, b'-' as u16]);
        #[cfg(feature = "servo")]
        let is_link_parameter = name.starts_with("--");
        if is_link_parameter {
            let param = device
                .link_parameters()?
                .0
                .iter()
                .find(|p| p.name.0 == *name)?;
            let mut parser = cssparser::Parser::new(param.value.0.as_ref());
            // need to carry around full variable value https://bugzilla.mozilla.org/show_bug.cgi?id=2028998
            return VariableValue::parse(&mut parser, None, url_data).ok();
        }

        if let Some(var) = ENVIRONMENT_VARIABLES.iter().find(|var| var.name == *name) {
            return Some((var.evaluator)(device, url_data));
        }
        if !url_data.chrome_rules_enabled() {
            return None;
        }
        let var = CHROME_ENVIRONMENT_VARIABLES
            .iter()
            .find(|var| var.name == *name)?;
        Some((var.evaluator)(device, url_data))
    }
}

/// A custom property name is just an `Atom`.
///
/// Note that this does not include the `--` prefix
pub type Name = Atom;

impl LocalName {
    #[cfg(feature = "gecko")]
    fn with_name<R>(name: &Name, callback: impl FnOnce(&Self) -> R) -> R {
        callback(Self::cast(name))
    }

    #[cfg(feature = "servo")]
    fn with_name<'a, R>(name: &'a Name, callback: impl FnOnce(&Self) -> R) -> R {
        callback(&name.as_str().into())
    }
}

impl From<Name> for LocalName {
    #[cfg(feature = "gecko")]
    fn from(name: Name) -> Self {
        Self::new(name)
    }

    #[cfg(feature = "servo")]
    fn from(name: Name) -> Self {
        name.as_str().into()
    }
}

/// Parse a custom property name.
///
/// <https://drafts.csswg.org/css-variables/#typedef-custom-property-name>
pub fn parse_name(s: &str) -> Result<&str, ()> {
    if s.starts_with("--") && s.len() > 2 {
        Ok(&s[2..])
    } else {
        Err(())
    }
}

/// A value for a custom property is just a set of tokens.
///
/// We preserve the original CSS for serialization, and also the variable
/// references to other custom property names.
#[derive(Clone, Debug, MallocSizeOf, ToShmem)]
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

trivial_to_computed_value!(VariableValue);

/// Given a potentially registered variable value turn it into a computed custom property value.
pub(crate) fn compute_variable_value(
    value: &Arc<VariableValue>,
    registration: &PropertyDescriptors,
    computed_context: &computed::Context,
    property_id: Option<PropertyIdRef>,
) -> Option<ComputedRegisteredValue> {
    if registration.is_universal() {
        return Some(ComputedRegisteredValue::universal(Arc::clone(value)));
    }
    compute_value(
        &value.css,
        &value.url_data,
        registration,
        computed_context,
        AttrTaint::default(),
        property_id,
    )
    .ok()
}

// For all purposes, we want values to be considered equal if their css text is equal.
impl PartialEq for VariableValue {
    fn eq(&self, other: &Self) -> bool {
        self.css == other.css
    }
}

impl Eq for VariableValue {}

impl ToCss for SpecifiedValue {
    fn to_css<W>(&self, dest: &mut CssWriter<W>) -> fmt::Result
    where
        W: Write,
    {
        dest.write_str(&self.css)
    }
}

impl ToTyped for SpecifiedValue {
    fn to_typed(&self, dest: &mut ThinVec<TypedValue>) -> Result<(), ()> {
        let unparsed_value = reify_variable_value(self)?;
        dest.push(TypedValue::Unparsed(unparsed_value));
        Ok(())
    }
}

fn reify_variable_value(value: &VariableValue) -> Result<UnparsedValue, ()> {
    let mut reference_index = 0;
    reify_variable_value_range(
        &value.css,
        &value.references.refs,
        &mut reference_index,
        0,
        value.css.len(),
    )
}

/// Reify a slice of the CSS string into UnparsedSegment entries.
///
/// References are stored in source order, with outer substitution functions
/// inserted before references in their fallback. The shared `reference_index`
/// relies on this ordering to recurse into fallbacks without reprocessing
/// nested referecences.
fn reify_variable_value_range(
    css: &str,
    references: &[SubstitutionFunctionReference],
    reference_index: &mut usize,
    start: usize,
    end: usize,
) -> Result<UnparsedValue, ()> {
    debug_assert!(start <= end);
    debug_assert!(end <= css.len());

    let mut values = ThinVec::new();
    let mut cur_pos = start;

    while *reference_index < references.len() {
        let reference = &references[*reference_index];

        if reference.start >= end {
            break;
        }

        debug_assert!(reference.start >= cur_pos);
        debug_assert!(reference.start <= reference.end);
        debug_assert!(reference.end <= css.len());

        if cur_pos < reference.start {
            values.push(UnparsedSegment::String(CssString::from(
                &css[cur_pos..reference.start],
            )));
        }

        *reference_index += 1;

        if reference.substitution_kind != SubstitutionFunctionKind::Var {
            return Err(());
        }

        let (fallback, has_fallback) = if let Some(fallback) = &reference.fallback {
            debug_assert!(fallback.start.get() < reference.end);

            (
                reify_variable_value_range(
                    css,
                    references,
                    reference_index,
                    fallback.start.get(),
                    reference.end - 1, // Skip the closing ')'.
                )?,
                true,
            )
        } else {
            (ThinVec::new(), false)
        };

        values.push(UnparsedSegment::VariableReference(VariableReferenceValue {
            variable: CssString::from(format!("--{}", reference.name)),
            fallback,
            has_fallback,
        }));

        cur_pos = reference.end;
    }

    if cur_pos < end {
        values.push(UnparsedSegment::String(CssString::from(&css[cur_pos..end])));
    }

    Ok(values)
}

/// A pair of separate CustomPropertiesMaps, split between custom properties
/// that have the inherit flag set and those with the flag unset.
#[repr(C)]
#[derive(Clone, Debug, Default, PartialEq)]
pub struct ComputedCustomProperties {
    /// Map for custom properties with inherit flag set, including non-registered
    /// ones.
    pub inherited: CustomPropertiesMap,
    /// Map for custom properties with inherit flag unset.
    pub non_inherited: CustomPropertiesMap,
}

impl ComputedCustomProperties {
    /// Return whether the inherited and non_inherited maps are none.
    pub fn is_empty(&self) -> bool {
        self.inherited.is_empty() && self.non_inherited.is_empty()
    }

    /// Return the name and value of the property at specified index, if any.
    pub fn property_at(&self, index: usize) -> Option<(&Name, &Option<ComputedRegisteredValue>)> {
        // Just expose the custom property items from custom_properties.inherited, followed
        // by custom property items from custom_properties.non_inherited.
        self.inherited
            .get_index(index)
            .or_else(|| self.non_inherited.get_index(index - self.inherited.len()))
    }

    /// Insert a custom property in the corresponding inherited/non_inherited
    /// map, depending on whether the inherit flag is set or unset.
    pub fn insert(
        &mut self,
        registration: &PropertyDescriptors,
        name: &Name,
        value: ComputedRegisteredValue,
    ) {
        self.map_mut(registration).insert(name, value)
    }

    /// Remove a custom property from the corresponding inherited/non_inherited
    /// map, depending on whether the inherit flag is set or unset.
    pub fn remove(&mut self, registration: &PropertyDescriptors, name: &Name) {
        self.map_mut(registration).remove(name);
    }

    /// Shrink the capacity of the inherited maps as much as possible.
    pub fn shrink_to_fit(&mut self) {
        self.inherited.shrink_to_fit();
        self.non_inherited.shrink_to_fit();
    }

    fn map_mut(&mut self, registration: &PropertyDescriptors) -> &mut CustomPropertiesMap {
        if registration.inherits() {
            &mut self.inherited
        } else {
            &mut self.non_inherited
        }
    }

    /// Returns the relevant custom property value given a registration.
    pub fn get(
        &self,
        registration: &PropertyDescriptors,
        name: &Name,
    ) -> Option<&ComputedRegisteredValue> {
        if registration.inherits() {
            self.inherited.get(name)
        } else {
            self.non_inherited.get(name)
        }
    }

    /// Returns a property just by the name. Slightly less efficient than get(), if you already have
    /// a custom registration handy, thus the longer name.
    pub fn get_for_cssom(&self, name: &Name) -> Option<&ComputedRegisteredValue> {
        self.inherited
            .get(name)
            .or_else(|| self.non_inherited.get(name))
    }
}

/// Both specified and computed values are VariableValues, the difference is
/// whether var() functions are expanded.
pub type SpecifiedValue = VariableValue;
/// Both specified and computed values are VariableValues, the difference is
/// whether var() functions are expanded.
pub type ComputedValue = VariableValue;

/// Set of flags to references this custom property makes.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq, MallocSizeOf, ToShmem)]
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
    /// Iterate for each non custom
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

    /// Iterate semantic cycle edges with their requested font inputs.
    pub fn for_each_non_custom_dependency<F>(self, is_root_element: bool, mut f: F)
    where
        F: FnMut(NonCustomDependency),
    {
        let metrics = self.intersects(Self::FONT_METRICS)
            || (is_root_element && self.intersects(Self::ROOT_FONT_METRICS));
        let orientation = self.intersects(Self::FONT_ORIENTATION)
            || (is_root_element && self.intersects(Self::ROOT_FONT_ORIENTATION));
        self.for_each_non_custom(is_root_element, |reference| {
            let font_demand = match reference {
                SingleNonCustomReference::FontUnits if orientation => {
                    FontDependencyDemand::OrientedMetrics
                }
                SingleNonCustomReference::FontUnits if metrics => FontDependencyDemand::FontMetrics,
                SingleNonCustomReference::FontUnits => FontDependencyDemand::ComputedSize,
                SingleNonCustomReference::LhUnits => FontDependencyDemand::OrientedMetrics,
                SingleNonCustomReference::ColorScheme => FontDependencyDemand::None,
            };
            f(NonCustomDependency {
                reference,
                font_demand,
            });
        });
    }

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

/// Requested computation inputs, separate from semantic cycle identity.
#[derive(Clone, Copy, Debug, Default, Eq, Ord, PartialEq, PartialOrd)]
pub enum FontDependencyDemand {
    /// No font inputs.
    #[default]
    None,
    /// The computed font size.
    ComputedSize,
    /// Computed size and current font metrics.
    FontMetrics,
    /// Font metrics and writing-mode-dependent orientation.
    OrientedMetrics,
}

impl FontDependencyDemand {
    /// Preserve the stronger requested input set.
    pub fn join(self, other: Self) -> Self {
        if self >= other { self } else { other }
    }
}

/// A semantic cycle edge and its separate computation demand.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct NonCustomDependency {
    /// The existing cycle identity.
    pub reference: SingleNonCustomReference,
    /// Requested inputs, not evidence that they are ready.
    pub font_demand: FontDependencyDemand,
}

/// A non-custom reference that participates in cycle resolution.
/// TODO(emilio): This should probably eventually become just PrioritaryPropertyId.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
#[allow(missing_docs)]
pub enum SingleNonCustomReference {
    FontUnits = 0,
    LhUnits,
    ColorScheme,
}

impl SingleNonCustomReference {
    /// Returns a prioritary id for this reference.
    pub fn to_prioritary_id(self) -> PrioritaryPropertyId {
        match self {
            Self::FontUnits => PrioritaryPropertyId::FontSize,
            Self::LhUnits => PrioritaryPropertyId::LineHeight,
            Self::ColorScheme => PrioritaryPropertyId::ColorScheme,
        }
    }
}

/// A map from NonCustomReferenceMap to a T.
pub struct NonCustomReferenceMap<T>([Option<T>; 3]);

impl<T> Default for NonCustomReferenceMap<T> {
    fn default() -> Self {
        NonCustomReferenceMap(Default::default())
    }
}

impl<T> Index<SingleNonCustomReference> for NonCustomReferenceMap<T> {
    type Output = Option<T>;

    fn index(&self, reference: SingleNonCustomReference) -> &Self::Output {
        &self.0[reference as usize]
    }
}

impl<T> IndexMut<SingleNonCustomReference> for NonCustomReferenceMap<T> {
    fn index_mut(&mut self, reference: SingleNonCustomReference) -> &mut Self::Output {
        &mut self.0[reference as usize]
    }
}

/// Substitution function source: var, env, attr.
#[derive(Copy, Clone, Debug, MallocSizeOf, Hash, Eq, PartialEq, ToShmem, Parse)]
pub enum SubstitutionFunctionKind {
    /// CSS variable / custom property
    Var,
    /// Environment variable
    Env,
    /// DOM attribute
    Attr,
}

/// A wrapper map that encapsulates both the custom properties and attributes
/// for a given element.
#[repr(C)]
#[derive(Clone, Debug, Default, PartialEq)]
pub struct ComputedSubstitutionFunctions {
    /// The applicable custom properties (includes inherited and non-inherited).
    pub custom_properties: ComputedCustomProperties,
    /// The applicable DOM attributes.
    pub attributes: PrecomputedHashMap<Namespace, OwnMap>,
}

impl ComputedSubstitutionFunctions {
    /// Creates a substitution function map from optional custom properties
    /// and DOM attributes.
    #[inline(always)]
    pub fn new(
        custom_properties: Option<ComputedCustomProperties>,
        attributes: Option<PrecomputedHashMap<Namespace, OwnMap>>,
    ) -> Self {
        Self {
            custom_properties: custom_properties.unwrap_or_default(),
            attributes: attributes.unwrap_or_default(),
        }
    }

    #[inline(always)]
    pub(crate) fn insert_var(
        &mut self,
        registration: &PropertyDescriptors,
        name: &Name,
        value: ComputedRegisteredValue,
    ) {
        self.custom_properties.insert(registration, name, value);
    }

    /// Store a computed attribute value by its expanded name.
    #[inline(always)]
    pub fn insert_attr(
        &mut self,
        name: &Name,
        namespace: &Namespace,
        value: ComputedRegisteredValue,
    ) {
        self.attributes
            .entry(namespace.clone())
            .or_default()
            .insert(name.clone(), Some(value));
    }

    #[inline(always)]
    pub(crate) fn remove_var(&mut self, registration: &PropertyDescriptors, name: &Name) {
        self.custom_properties.remove(registration, name);
    }

    #[inline(always)]
    pub(crate) fn remove_attr(&mut self, name: &Name, namespace: &Namespace) {
        self.attributes
            .entry(namespace.clone())
            .or_default()
            .insert(name.clone(), None);
    }

    #[inline(always)]
    pub(crate) fn get_var(
        &self,
        registration: &PropertyDescriptors,
        name: &Name,
    ) -> Option<&ComputedRegisteredValue> {
        self.custom_properties.get(registration, name)
    }

    #[inline(always)]
    pub(crate) fn contains_attr(&self, name: &Name, namespace: &Namespace) -> bool {
        self.attributes
            .get(namespace)
            .is_some_and(|attributes| attributes.contains_key(name))
    }

    #[inline(always)]
    pub(crate) fn get_attr(
        &self,
        name: &Name,
        namespace: &Namespace,
    ) -> Option<&ComputedRegisteredValue> {
        self.attributes
            .get(namespace)?
            .get(name)
            .and_then(|p| p.as_ref())
    }
}

#[derive(Clone, Debug, MallocSizeOf, PartialEq, ToShmem, Parse)]
enum AttributeType {
    Invalid,
    None,
    RawString,
    Type(SyntaxDescriptor),
    Unit(AttrUnit),
}

fn parse_attr_number<'i>(input: &mut Parser<'i>) -> Result<&'i str, ()> {
    input.skip_whitespace();
    let start = input.position();
    input.expect_number().map_err(|_| ())?;
    let number = input.slice_from(start);
    input.expect_exhausted().map_err(|_| ())?;
    Ok(number)
}

/// Data specific to an attr() call like type and namespace.
#[derive(Clone, Debug, MallocSizeOf, PartialEq, ToShmem)]
pub struct AttributeData {
    kind: AttributeType,
    namespace: ParsedNamespace,
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

/// For a CSS string, the range, counted in bytes, that is attr()-tainted.
#[derive(Clone, Debug, Default, MallocSizeOf, PartialEq, ToShmem, ToComputedValue)]
pub struct AttrTaintedRange {
    /// Start of the range, counted in bytes. Inclusive.
    start: usize,
    /// End of the range, counted in bytes. Exclusive.
    end: usize,
}

impl AttrTaintedRange {
    /// Creates a range within a CSS string that is tainted by attr().
    #[inline(always)]
    pub fn new(start: usize, end: usize) -> Self {
        debug_assert!(start <= end);
        Self { start, end }
    }
}

/// In CSS Values and Units, values produced by `attr()` are considered attr()-tainted, as are
/// functions that contain an attr()-tainted value. Using an attr()-tainted value as or in a <url>
/// makes a declaration invalid at computed-value time.
/// https://drafts.csswg.org/css-values-5/#attr-security
#[derive(Clone, Debug, Default, MallocSizeOf, PartialEq, ToShmem)]
pub struct AttrTaint(SmallVec<[AttrTaintedRange; 1]>);

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

/// The fallback of a particular value.
#[derive(Clone, Debug, MallocSizeOf, PartialEq, ToShmem)]
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

/// A reference to a substitution function like env() / var() / attr().
#[derive(Clone, Debug, MallocSizeOf, PartialEq, ToShmem)]
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

impl SubstitutionFunctionReference {
    /// Whether we're an attr(... type(...)) reference.
    pub fn is_attr_with_type(&self) -> bool {
        self.substitution_kind == SubstitutionFunctionKind::Attr
            && matches!(self.attribute_data.kind, AttributeType::Type(..))
    }
}

/// A struct holding information about the external references to that a custom property value may
/// have.
#[derive(Clone, Debug, Default, MallocSizeOf, PartialEq, ToShmem)]
pub struct References {
    /// The actual list of references that we end up with.
    pub refs: Vec<SubstitutionFunctionReference>,
    /// Various flags about the kind of references we hold. Note that these include data about our
    /// nested references.
    ///
    /// TODO(emilio): Do we need to distinguish between own and nested flags?
    pub flags: ReferenceFlags,
}

impl References {
    fn has_references(&self) -> bool {
        !self.refs.is_empty()
    }

    pub(crate) fn non_custom_references(&self, is_root_element: bool) -> ReferenceFlags {
        let mut mask = ReferenceFlags::NON_ROOT_DEPENDENCIES;
        if is_root_element {
            mask |= ReferenceFlags::ROOT_DEPENDENCIES
        }
        self.flags & mask
    }
}

fn resolved_token_dependencies(mut css: &str) -> Option<ReferenceFlags> {
    let mut flags = ReferenceFlags::empty();
    while !css.is_empty() {
        // Restart at each token to visit block contents without recursion.
        let mut input = Parser::new(css);
        match input.next_including_whitespace_and_comments().ok()? {
            Token::Dimension { unit, .. } => flags.insert(ReferenceFlags::from_unit(unit)),
            Token::Function(name) if SubstitutionFunctionKind::from_ident(name).is_ok() => {
                return None;
            }
            Token::BadUrl(_) | Token::BadString(_) => return None,
            _ => {}
        }
        let consumed = input.position().byte_index();
        debug_assert!(consumed > 0);
        css = &css[consumed..];
    }
    Some(flags)
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

    /// Create a new custom property without parsing if the CSS is known to be valid and contain no
    /// references.
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

    fn new_resolved(
        css: String,
        url_data: &UrlExtraData,
        first_token_type: TokenSerializationType,
        last_token_type: TokenSerializationType,
    ) -> Self {
        let mut value = Self::new(css, url_data, first_token_type, last_token_type);
        // Unresolved env payloads keep the previous empty summary.
        if let Some(flags) = resolved_token_dependencies(&value.css) {
            value.references.flags = flags;
        }
        value
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

    /// Parse a custom property value.
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

    /// Returns whether this value is tainted by `attr()`.
    pub fn is_attr_tainted(&self) -> bool {
        self.references.flags.intersects(ReferenceFlags::ATTR) | self.explicitly_attr_tainted
    }

    /// Create VariableValue from an int.
    fn integer(number: i32, url_data: &UrlExtraData) -> Self {
        Self::from_token(
            Token::Number {
                has_sign: false,
                value: number as f32,
                int_value: Some(number),
            },
            url_data,
        )
    }

    /// Create VariableValue from an int.
    fn ident(ident: &'static str, url_data: &UrlExtraData) -> Self {
        Self::from_token(Token::Ident(ident.into()), url_data)
    }

    /// Create VariableValue from a float amount of CSS pixels.
    fn pixels(number: f32, url_data: &UrlExtraData) -> Self {
        // FIXME (https://github.com/servo/rust-cssparser/issues/266):
        // No way to get TokenSerializationType::Dimension without creating
        // Token object.
        Self::from_token(
            Token::Dimension {
                has_sign: false,
                value: number,
                int_value: None,
                unit: CowRcStr::from("px"),
            },
            url_data,
        )
    }

    /// Create VariableValue from an integer amount of milliseconds.
    fn int_ms(number: i32, url_data: &UrlExtraData) -> Self {
        Self::from_token(
            Token::Dimension {
                has_sign: false,
                value: number as f32,
                int_value: Some(number),
                unit: CowRcStr::from("ms"),
            },
            url_data,
        )
    }

    /// Create VariableValue from an integer amount of CSS pixels.
    fn int_pixels(number: i32, url_data: &UrlExtraData) -> Self {
        Self::from_token(
            Token::Dimension {
                has_sign: false,
                value: number as f32,
                int_value: Some(number),
                unit: CowRcStr::from("px"),
            },
            url_data,
        )
    }

    fn from_token(token: Token, url_data: &UrlExtraData) -> Self {
        let token_type = token.serialization_type();
        let mut css = token.to_css_string();
        css.shrink_to_fit();

        VariableValue {
            css,
            url_data: url_data.clone(),
            first_token_type: token_type,
            last_token_type: token_type,
            references: Default::default(),
            explicitly_attr_tainted: false,
        }
    }

    /// Returns the raw CSS text from this VariableValue
    pub fn css_text(&self) -> &str {
        &self.css
    }

    /// Returns whether this variable value has any reference to the environment or other
    /// variables.
    pub fn has_references(&self) -> bool {
        self.references.has_references()
    }

    /// Returns the attribute references in this variable value, if any.
    pub fn collect_attribute_references(&self, references: &mut AttrReferenceSet) {
        self.references.refs.iter().for_each(|r| {
            if r.substitution_kind == SubstitutionFunctionKind::Attr {
                // For a non-ascii-lowercase attribute, whether we match
                // case-sensitively depends on whether the element we're
                // matching against is an HTML element in an HTML document.
                // So to simplify invalidation we collect both potential
                // references here.
                references.insert(r.name.clone().into());
                let lowercase = r.name.to_ascii_lowercase();
                if *lowercase != *r.name {
                    references.insert(Atom::from(lowercase).into());
                }
            }
        })
    }
}

/// <https://drafts.csswg.org/css-syntax-3/#typedef-declaration-value>
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

/// Like parse_declaration_value, but accept `!` and `;` since they are only invalid at the top level.
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

/// Parse <attr-type> = type( <syntax> ) | raw-string | number | <attr-unit>.
/// https://drafts.csswg.org/css-values-5/#attr-notation
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

/// Attribute values may reference other substitution functions we may need to process.
/// See step 6: https://drafts.csswg.org/css-values-5/#attr-substitution
pub fn get_attr_value_for_cycle_resolution(
    name: &Name,
    attribute_data: &AttributeData,
    url_data: &UrlExtraData,
    attribute_tracker: &mut AttributeTracker,
) -> Result<ComputedRegisteredValue, ()> {
    let namespace = match attribute_data.namespace {
        ParsedNamespace::Known(ref ns) => ns,
        ParsedNamespace::Unknown => return Err(()),
    };
    CapturedAttributeInput::query(name, namespace, attribute_tracker).parse(url_data)
}

/// See https://drafts.csswg.org/css-variables-2/#invalid-at-computed-value-time
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

/// Replace `var()`, `env()`, and `attr()` functions in a pre-existing variable value.
pub fn substitute_references_if_needed_and_apply(
    name: &Name,
    namespace: Option<&Namespace>,
    value: &Arc<VariableValue>,
    stylist: &Stylist,
    context: &mut computed::Context,
    attribute_tracker: &mut AttributeTracker,
) {
    let is_var = namespace.is_none();
    let registration = stylist.get_custom_property_registration(name);
    if is_var && !value.has_references() && registration.is_universal() {
        // Trivial path: no references and no need to compute the value, just apply it directly.
        let computed_value = ComputedRegisteredValue::universal(Arc::clone(value));
        context
            .builder
            .substitution_functions
            .insert_var(registration, name, computed_value);
        return;
    }

    let url_data = &value.url_data;
    apply_substituted_value(
        name,
        namespace,
        url_data,
        SubstitutionInput::Unresolved(value, attribute_tracker),
        stylist,
        context,
    );
}

enum SubstitutionInput<'a, 'b> {
    Unresolved(&'a VariableValue, &'a mut AttributeTracker<'b>),
    Prepared(Result<Substitution<'static>, ()>),
}

fn apply_substituted_value(
    name: &Name,
    namespace: Option<&Namespace>,
    url_data: &UrlExtraData,
    input: SubstitutionInput<'_, '_>,
    stylist: &Stylist,
    context: &mut computed::Context,
) {
    let is_var = namespace.is_none();
    let registration = stylist.get_custom_property_registration(name);
    let substitution = match input {
        SubstitutionInput::Unresolved(value, attribute_tracker) => substitute_internal(
            value,
            Some(PropertyIdRef::from(name)),
            &context.builder.substitution_functions,
            stylist,
            context,
            attribute_tracker,
            &mut SmallVec::new(),
            None,
        ),
        SubstitutionInput::Prepared(substitution) => substitution,
    };
    let Ok(substitution) = substitution else {
        if is_var {
            handle_invalid_at_computed_value_time(name, registration, context);
        } else if let Some(namespace) = namespace {
            context
                .builder
                .substitution_functions
                .remove_attr(name, namespace);
        }
        return;
    };

    // If variable fallback results in a wide keyword, deal with it now.
    let inherited = context.builder.inherited_style.custom_properties();
    if is_var {
        let css = &substitution.css;
        let css_wide_kw = {
            let mut input = Parser::new(css);
            input.try_parse(CSSWideKeyword::parse)
        };

        if let Ok(kw) = css_wide_kw {
            // TODO: It's unclear what this should do for revert / revert-layer, see
            // https://github.com/w3c/csswg-drafts/issues/9131. For now treating as unset
            // seems fine?
            match (kw, registration.inherits(), context.is_root_element()) {
                (CSSWideKeyword::Initial, _, _)
                | (CSSWideKeyword::Revert, false, _)
                | (CSSWideKeyword::RevertLayer, false, _)
                | (CSSWideKeyword::RevertRule, false, _)
                | (CSSWideKeyword::Unset, false, _)
                | (CSSWideKeyword::Revert, true, true)
                | (CSSWideKeyword::RevertLayer, true, true)
                | (CSSWideKeyword::RevertRule, true, true)
                | (CSSWideKeyword::Unset, true, true)
                | (CSSWideKeyword::Inherit, _, true) => {
                    remove_and_insert_initial_value(
                        name,
                        registration,
                        stylist.get_custom_property_initial_values(),
                        &mut context.builder.substitution_functions,
                    );
                }
                (CSSWideKeyword::Revert, true, false)
                | (CSSWideKeyword::RevertLayer, true, false)
                | (CSSWideKeyword::RevertRule, true, false)
                | (CSSWideKeyword::Inherit, _, false)
                | (CSSWideKeyword::Unset, true, false) => {
                    if !registration.inherits() {
                        context
                            .style()
                            .add_flags(ComputedValueFlags::INHERITS_RESET_STYLE);
                    }
                    match inherited.get(registration, name) {
                        Some(value) => {
                            context.builder.substitution_functions.insert_var(
                                registration,
                                name,
                                value.clone(),
                            );
                        }
                        None => {
                            context
                                .builder
                                .substitution_functions
                                .remove_var(registration, name);
                        }
                    };
                }
            }
            return;
        }
    }

    match namespace {
        None => {
            let value = match substitution.into_value(
                url_data,
                registration,
                context,
                Some(PropertyIdRef::from(name)),
            ) {
                Ok(v) => v,
                Err(()) => {
                    handle_invalid_at_computed_value_time(name, registration, context);
                    return;
                }
            };
            context
                .builder
                .substitution_functions
                .insert_var(registration, name, value);
        }
        Some(namespace) => {
            let mut value =
                ComputedRegisteredValue::universal(Arc::new(VariableValue::new_resolved(
                    substitution.css.into_owned(),
                    url_data,
                    substitution.first_token_type,
                    substitution.last_token_type,
                )));
            value.attr_tainted |= substitution.attr_tainted;
            context
                .builder
                .substitution_functions
                .insert_attr(name, namespace, value);
        }
    }
}

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

pub(crate) fn prepare_custom_value(
    name: &Name,
    value: &VariableValue,
    stylist: &Stylist,
    context: &computed::Context,
    attribute_tracker: &mut AttributeTracker,
) -> PreparedCustomValue {
    let url_data = value.url_data.clone();
    let substitution = substitute_internal(
        value,
        Some(PropertyIdRef::from(name)),
        &context.builder.substitution_functions,
        stylist,
        context,
        attribute_tracker,
        &mut SmallVec::new(),
        None,
    )
    .map(|value| Substitution {
        css: Cow::Owned(value.css.into_owned()),
        first_token_type: value.first_token_type,
        last_token_type: value.last_token_type,
        attr_tainted: value.attr_tainted,
    });
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
        url_data: value.url_data.clone(),
        kind,
    }
}

fn prepare_invalid_custom_kind(
    name: &Name,
    registration: &PropertyDescriptors,
    context: &computed::Context,
) -> PreparedCustomKind {
    if !registration.is_universal()
        && (!registration.inherits() || context.builder.is_root_element)
        && let (Some(initial), Some(syntax)) = (&registration.initial_value, &registration.syntax)
    {
        let mut parser = Parser::new(&initial.css);
        if let Ok(parsed) = SpecifiedRegisteredValue::parse(
            &mut parser,
            syntax,
            &initial.url_data,
            None,
            AllowComputationallyDependent::Yes,
            AttrTaint::default(),
            Some(PropertyIdRef::from(name)),
        ) {
            return PreparedCustomKind::Initial(parsed);
        }
    }
    PreparedCustomKind::Invalid
}

pub(crate) fn invalid_custom_value_depends_on_color_scheme(
    name: &Name,
    stylist: &Stylist,
    context: &computed::Context,
) -> bool {
    match prepare_invalid_custom_kind(
        name,
        stylist.get_custom_property_registration(name),
        context,
    ) {
        PreparedCustomKind::Initial(value) => value.depends_on_color_scheme(),
        _ => false,
    }
}

#[derive(Default, Debug)]
struct Substitution<'a> {
    css: Cow<'a, str>,
    first_token_type: TokenSerializationType,
    last_token_type: TokenSerializationType,
    attr_tainted: bool,
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

    fn into_value(
        self,
        url_data: &UrlExtraData,
        registration: &PropertyDescriptors,
        computed_context: &computed::Context,
        property_id: Option<PropertyIdRef>,
    ) -> Result<ComputedRegisteredValue, ()> {
        if registration.is_universal() {
            let mut value =
                ComputedRegisteredValue::universal(Arc::new(VariableValue::new_resolved(
                    self.css.into_owned(),
                    url_data,
                    self.first_token_type,
                    self.last_token_type,
                )));
            value.attr_tainted |= self.attr_tainted;
            return Ok(value);
        }
        let taint = if self.attr_tainted {
            // Per spec: substitution value of an arbitrary substitution function is
            // attr()-tainted as a whole if any attr()-tainted values were involved
            // in creating that substitution value.
            // https://drafts.csswg.org/css-values-5/#attr-security
            AttrTaint::new_fully_tainted(self.css.len())
        } else {
            AttrTaint::default()
        };
        let mut v = compute_value(
            &self.css,
            url_data,
            registration,
            computed_context,
            taint,
            property_id,
        )?;
        v.attr_tainted |= self.attr_tainted;
        Ok(v)
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

/// Result of var(), env(), and attr() substitution.
#[derive(Debug)]
pub struct SubstitutionResult<'a> {
    /// The resolved CSS string after substitution.
    pub css: Cow<'a, str>,
    /// Regions in the `css` string that are attr()-tainted, if any.
    pub attr_taint: AttrTaint,
}

fn compute_value(
    css: &str,
    url_data: &UrlExtraData,
    registration: &PropertyDescriptors,
    computed_context: &computed::Context,
    attr_taint: AttrTaint,
    property_id: Option<PropertyIdRef>,
) -> Result<ComputedRegisteredValue, ()> {
    debug_assert!(!registration.is_universal());

    let mut input = Parser::new(css);
    SpecifiedRegisteredValue::compute(
        &mut input,
        registration,
        None,
        url_data,
        computed_context,
        AllowComputationallyDependent::Yes,
        attr_taint,
        property_id,
    )
}

/// Removes the named registered custom property and inserts its computed initial value.
pub(crate) fn remove_and_insert_initial_value(
    name: &Name,
    registration: &PropertyDescriptors,
    initial_values: &ComputedCustomProperties,
    substitution_functions: &mut ComputedSubstitutionFunctions,
) {
    substitution_functions.remove_var(registration, name);
    if let Some(value) = initial_values.get(registration, name) {
        substitution_functions.insert_var(registration, name, value.clone());
    }
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

fn quoted_css_string(src: &str) -> String {
    let mut dest = String::with_capacity(src.len() + 2);
    cssparser::serialize_string(src, &mut dest).unwrap();
    dest
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

/// Replace `var()`, `env()`, and `attr()` functions. Return `Err(..)` for invalid at computed time.
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

/// Replace var(), env(), and attr() functions, returning the resulting CSS string.
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

struct AttributeAttempt {
    identity: Arc<()>,
    name: Name,
    namespace: Namespace,
    marked: bool,
}

pub(crate) struct ResumableSubstitution<'a> {
    frames: Vec<SubstitutionFrame>,
    seen: Vec<Name>,
    attributes: Vec<AttributeAttempt>,
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
            attributes: Vec::new(),
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
            attribute_attempt: self
                .attributes
                .last()
                .map(|attempt| attempt.identity.clone()),
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
        if let Some(start) = self.attributes.iter().position(|attempt| {
            attempt.name == frame.reference.name && attempt.namespace == namespace
        }) {
            for attempt in &mut self.attributes[start..] {
                attempt.marked = true;
            }
            self.invalid_primary(frame);
            return;
        }
        let identity = Arc::new(());
        self.attributes.push(AttributeAttempt {
            identity: identity.clone(),
            name: frame.reference.name.clone(),
            namespace,
            marked: false,
        });
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
                    .parse_typed_value(&mut parser, &frame.value.url_data, self.property_id)
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
                            let attempt = self.attributes.pop().expect("attribute body completed");
                            assert!(Arc::ptr_eq(&attempt.identity, identity));
                            assert_eq!(attempt.name, frame.reference.name);
                            assert_eq!(
                                Some(&attempt.namespace),
                                frame.reference.attribute_data.namespace()
                            );
                            let result = self.returned.take().expect("attribute body result");
                            let value = if attempt.marked {
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
