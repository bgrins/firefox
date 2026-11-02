use bitflags::bitflags;
type CowRcStr = str;
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PrioritaryPropertyId { FontSize, LineHeight, ColorScheme }
struct NoCalcLength;
impl NoCalcLength {
const EM: &'static str = "em";
const EX: &'static str = "ex";
const CAP: &'static str = "cap";
const CH: &'static str = "ch";
const IC: &'static str = "ic";
const LH: &'static str = "lh";
const REM: &'static str = "rem";
const REX: &'static str = "rex";
const RCAP: &'static str = "rcap";
const RCH: &'static str = "rch";
const RIC: &'static str = "ric";
const RLH: &'static str = "rlh";
}
/// Set of flags to references this custom property makes.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
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
                },
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


#[test] fn actual_collision() {
 let lh=ReferenceFlags::from_unit("lh");
 let ch=ReferenceFlags::from_unit("ch");
 assert_eq!(lh, lh | ch);
 assert_eq!(lh, ReferenceFlags::FONT_UNITS | ReferenceFlags::LH_UNITS | ReferenceFlags::FONT_METRICS | ReferenceFlags::FONT_ORIENTATION);
 assert_ne!(ReferenceFlags::from_unit("em"), lh);
}
#[test] fn clearing_lh_aggregate_loses_independent_ch() {
 let both=ReferenceFlags::from_unit("lh") | ReferenceFlags::from_unit("ch");
 let narrowed=both & !(ReferenceFlags::FONT_METRICS | ReferenceFlags::FONT_ORIENTATION);
 assert!(!narrowed.contains(ReferenceFlags::from_unit("ch")));
}
