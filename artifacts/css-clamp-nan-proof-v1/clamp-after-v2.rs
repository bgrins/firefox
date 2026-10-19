            Self::Clamp {
                ref mut min,
                ref mut center,
                ref mut max,
            } => {
                let (Some(min_leaf), Some(center_leaf), Some(max_leaf)) =
                    (min.as_leaf(), center.as_leaf(), max.as_leaf())
                else {
                    return SimplificationResult::Unchanged;
                };
                let leaves = [min_leaf, center_leaf, max_leaf];
                let mut has_relative_infinity = false;
                for leaf in leaves {
                    let Some(value) = leaf.unitless_value() else {
                        return SimplificationResult::Unchanged;
                    };
                    if leaf
                        .as_percentage()
                        .is_some_and(|(_, hint)| hint != Optional::Some(NumericBaseType::Percent))
                    {
                        return SimplificationResult::Unchanged;
                    }
                    has_relative_infinity |=
                        value.is_infinite() && leaf.canonical_value().is_none();
                }

                let strict_op = |a: f32, b: f32, op: fn(f32, f32) -> f32| {
                    if a.is_nan() {
                        a
                    } else if b.is_nan() {
                        b
                    } else {
                        op(a, b)
                    }
                };
                let result = center_leaf
                    .try_op(max_leaf, |a, b| strict_op(a, b, crate::values::calc_min))
                    .and_then(|inner| {
                        min_leaf.try_op(&inner, |a, b| strict_op(a, b, crate::values::calc_max))
                    });
                if let Ok(result) = result {
                    if has_relative_infinity && result.unitless_value().is_none_or(f32::is_finite) {
                        return SimplificationResult::Unchanged;
                    }
                    *self = Self::Leaf(result);
                    return SimplificationResult::Simplified;
                }
                if has_relative_infinity || leaves.iter().any(|leaf| leaf.is_nan() != Ok(false)) {
                    return SimplificationResult::Unchanged;
                }

                // NOTE: clamp() is max(min, min(center, max))
                let min_cmp_center = match min.compare(center) {
                    Some(o) => o,
                    None => return SimplificationResult::Unchanged,
                };

                // All operands are non-NaN, so a lower bound above the center wins.
                if matches!(min_cmp_center, cmp::Ordering::Greater) {
                    replace_self_with!(&mut **min);
                    return SimplificationResult::Simplified;
                }

                // Otherwise try with max.
                let max_cmp_center = match max.compare(center) {
                    Some(o) => o,
                    None => return SimplificationResult::Unchanged,
                };

                if matches!(max_cmp_center, cmp::Ordering::Less) {
                    // max is less than center, so we need to return effectively
                    // `max(min, max)`.
                    let max_cmp_min = match max.compare(min) {
                        Some(o) => o,
                        None => return SimplificationResult::Unchanged,
                    };

                    if matches!(max_cmp_min, cmp::Ordering::Less) {
                        replace_self_with!(&mut **min);
                        return SimplificationResult::Simplified;
                    }

                    replace_self_with!(&mut **max);
                    return SimplificationResult::Simplified;
                }

                // Otherwise we're the center node.
                replace_self_with!(&mut **center);
                SimplificationResult::Simplified
            },
