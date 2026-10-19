            Self::Clamp {
                ref mut min,
                ref mut center,
                ref mut max,
            } => {
                // NOTE: clamp() is max(min, min(center, max))
                let min_cmp_center = match min.compare(center) {
                    Some(o) => o,
                    None => return SimplificationResult::Unchanged,
                };

                // So if we can prove that min is more than center, then we won,
                // as that's what we should always return.
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
