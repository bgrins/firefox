mod historical {
use bitflags::bitflags;
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
        /// All dependencies not depending on the root element.
        const NON_ROOT_DEPENDENCIES = Self::FONT_UNITS.0 | Self::LH_UNITS.0 | Self::WRITING_MODE.0;
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
        /// Logical lengths depend on the element's writing mode.
        const WRITING_MODE = 1 << 8;
    }
}
#[derive(Debug, PartialEq, Eq)]
pub enum SingleNonCustomReference { FontUnits, LhUnits, ColorScheme, WritingMode }
impl ReferenceFlags { pub fn for_each_non_custom<F>(mut self, is_root_element: bool, mut f: F)
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
                Self::WRITING_MODE => SingleNonCustomReference::WritingMode,
                Self::ROOT_FONT_UNITS
                | Self::ROOT_LH_UNITS
                | Self::VAR
                | Self::ENV
                | Self::ATTR => continue,
                _ => unreachable!("Unexpected single bit value"),
            };
            f(single);
        }
    } }
pub fn visit(bits:u16) -> Vec<SingleNonCustomReference> {
let mut out=vec![];ReferenceFlags::from_bits_retain(bits).for_each_non_custom(false,|v|out.push(v));out
}
pub fn named(bits:u16) -> Vec<u16> {ReferenceFlags::from_bits_retain(bits).iter_names().map(|(_,v)|v.bits()).collect()}
}
mod candidate {
use bitflags::bitflags;
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
        /// Logical lengths depend on the element's writing mode.
        const WRITING_MODE = 1 << 8;
        /// All dependencies not depending on the root element.
        const NON_ROOT_DEPENDENCIES = Self::FONT_UNITS.0 | Self::LH_UNITS.0 | Self::WRITING_MODE.0;
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
#[derive(Debug, PartialEq, Eq)]
pub enum SingleNonCustomReference { FontUnits, LhUnits, ColorScheme, WritingMode }
impl ReferenceFlags { pub fn for_each_non_custom<F>(mut self, is_root_element: bool, mut f: F)
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
                Self::WRITING_MODE => SingleNonCustomReference::WritingMode,
                Self::ROOT_FONT_UNITS
                | Self::ROOT_LH_UNITS
                | Self::VAR
                | Self::ENV
                | Self::ATTR => continue,
                _ => unreachable!("Unexpected single bit value"),
            };
            f(single);
        }
    } }
pub fn visit(bits:u16) -> Vec<SingleNonCustomReference> {
let mut out=vec![];ReferenceFlags::from_bits_retain(bits).for_each_non_custom(false,|v|out.push(v));out
}
pub fn named(bits:u16) -> Vec<u16> {ReferenceFlags::from_bits_retain(bits).iter_names().map(|(_,v)|v.bits()).collect()}
}

fn main() {
std::panic::set_hook(Box::new(|_| {}));
assert_eq!(historical::named(261), vec![1,4,261]);
assert!(std::panic::catch_unwind(||historical::visit(261)).is_err());
assert_eq!(candidate::named(261), vec![1,4,256]);
assert_eq!(candidate::visit(261),vec![candidate::SingleNonCustomReference::FontUnits,candidate::SingleNonCustomReference::LhUnits,candidate::SingleNonCustomReference::WritingMode]);
for bits in 0u16..512 {
let got=candidate::visit(bits);
let mut want=vec![];
if bits&1!=0 {want.push(candidate::SingleNonCustomReference::FontUnits);}
if bits&4!=0 {want.push(candidate::SingleNonCustomReference::LhUnits);}
if bits&16!=0 {want.push(candidate::SingleNonCustomReference::ColorScheme);}
if bits&256!=0 {want.push(candidate::SingleNonCustomReference::WritingMode);}
assert_eq!(got,want,"mask {}",bits);
}
println!("historical mask261 panics; candidate all512 nonroot masks yield exact contextual singletons");
}
