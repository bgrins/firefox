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
