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
mod base { use super::*;
/// Set of flags to references this custom property makes.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
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
                | Self::VAR
                | Self::ENV
                | Self::ATTR => continue,
                _ => unreachable!("Unexpected single bit value"),
            };
            f(single);
        }
    }

    pub(crate) fn from_unit(value: &CowRcStr) -> Self {
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

}
mod candidate { use super::*;
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

    pub(crate) fn from_unit(value: &CowRcStr) -> Self {
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

}
#[cfg(test)]
mod tests {
    use super::*;
    fn demands(flags: candidate::ReferenceFlags, root: bool) -> Vec<candidate::NonCustomDependency> {
        let mut result = vec![];
        flags.for_each_non_custom_dependency(root, |v| result.push(v));
        result
    }
    #[test]
    fn unit_inputs_and_root_mapping() {
        use candidate::{FontDependencyDemand as D, ReferenceFlags as F, SingleNonCustomReference as R};
        for (unit, wanted) in [("em", D::ComputedSize), ("ex", D::FontMetrics), ("cap", D::FontMetrics), ("ch", D::OrientedMetrics), ("ic", D::OrientedMetrics)] {
            for spelling in [unit.to_string(), unit.to_uppercase()] {
                assert_eq!((F::from_unit(&spelling).bits() & 255) as u8, base::ReferenceFlags::from_unit(&spelling).bits());
                let found=demands(F::from_unit(&spelling), false);
                assert_eq!(found, vec![candidate::NonCustomDependency { reference:R::FontUnits, font_demand:wanted }]);
            }
            let root_unit = format!("r{unit}");
            assert!(demands(F::from_unit(&root_unit), false).is_empty());
            assert_eq!(demands(F::from_unit(&root_unit), true)[0].font_demand, wanted);
        }
        assert!(demands(F::from_unit("px"), true).is_empty());
        for unit in ["lh", "rlh"] {
            let found=demands(F::from_unit(unit), true);
            assert_eq!(found.len(),2);
            assert!(found.iter().all(|v| v.font_demand==D::OrientedMetrics));
        }
        let mixed=F::from_unit("em")|F::from_unit("rch");
        assert_eq!(demands(mixed,false)[0].font_demand,D::ComputedSize);
        assert_eq!(demands(mixed,true)[0].font_demand,D::OrientedMetrics);
    }
    #[test]
    fn every_flag_combination_preserves_semantic_projection() {
        for mask in 0..4096u16 {
            for root in [false,true] {
                let mut expected=vec![];
                base::ReferenceFlags::from_bits_retain(mask as u8).for_each_non_custom(root, |r|expected.push(r as usize));
                let found=demands(candidate::ReferenceFlags::from_bits_retain(mask),root);
                assert_eq!(found.iter().map(|d|d.reference as usize).collect::<Vec<_>>(),expected);
            }
        }
        assert_eq!(candidate::SingleNonCustomReference::FontUnits.to_prioritary_id(),PrioritaryPropertyId::FontSize);
    }
    #[test]
    fn alias_union_and_later_requests_cannot_downgrade() {
        use candidate::{FontDependencyDemand as D, ReferenceFlags as F};
        let all=[D::None,D::ComputedSize,D::FontMetrics,D::OrientedMetrics];
        for a in all { for b in all { for c in all {
            assert_eq!(a.join(b).join(c),a.join(b.join(c)));
            assert!(a.join(b)>=a && a.join(b)>=b);
        }}}
        let alias=F::from_unit("em")|F::from_unit("ex");
        let first=demands(alias,false)[0].font_demand;
        let second=demands(F::from_unit("ch"),false)[0].font_demand;
        assert_eq!(first,D::FontMetrics);
        assert_eq!(first.join(second).join(D::ComputedSize),D::OrientedMetrics);
        let inventory=alias|F::from_unit("cap")|F::from_unit("rem");
        assert_eq!(demands(inventory,false)[0].font_demand,D::FontMetrics);
    }
}
