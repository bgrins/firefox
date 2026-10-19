#[derive(Clone, Copy, Eq, Ord, PartialEq, PartialOrd)]
enum PropertyCategory {
    Custom,
    PhysicalLonghand,
    LogicalLonghand,
    Shorthand,
}

impl PropertyCategory {
    fn of(id: &PropertyId) -> Self {
        match *id {
            PropertyId::NonCustom(id) => match id.longhand_or_shorthand() {
                Ok(id) => {
                    if id.is_logical() {
                        PropertyCategory::LogicalLonghand
                    } else {
                        PropertyCategory::PhysicalLonghand
                    }
                },
                Err(..) => PropertyCategory::Shorthand,
            },
            PropertyId::Custom(..) => PropertyCategory::Custom,
        }
    }
}

/// A comparator to sort PropertyIds such that physical longhands are sorted
/// before logical longhands and shorthands, shorthands with fewer components
/// are sorted before shorthands with more components, and otherwise shorthands
/// are sorted by IDL name as defined by [Web Animations][property-order].
///
/// Using this allows us to prioritize values specified by longhands (or smaller
/// shorthand subsets) when longhands and shorthands are both specified on the
/// one keyframe.
///
/// [property-order] https://drafts.csswg.org/web-animations/#calculating-computed-keyframes
pub fn compare_property_priority(a: &PropertyId, b: &PropertyId) -> cmp::Ordering {
    let a_category = PropertyCategory::of(a);
    let b_category = PropertyCategory::of(b);

    if a_category != b_category {
        return a_category.cmp(&b_category);
    }

    if a_category != PropertyCategory::Shorthand {
        return cmp::Ordering::Equal;
    }

    let a = a.as_shorthand().unwrap();
    let b = b.as_shorthand().unwrap();
    // Within shorthands, sort by the number of subproperties, then by IDL
    // name.
    let subprop_count_a = a.longhands().count();
    let subprop_count_b = b.longhands().count();
    subprop_count_a
        .cmp(&subprop_count_b)
        .then_with(|| a.idl_name_sort_order().cmp(&b.idl_name_sort_order()))
}
