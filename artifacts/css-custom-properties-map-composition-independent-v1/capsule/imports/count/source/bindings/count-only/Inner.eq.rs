    fn eq(&self, other: &Self) -> bool {
        if self.len != other.len {
            return false;
        }
        // NOTE(emilio): In order to speed up custom property comparison when tons of custom
        // properties are involved, we return false in some cases where the ordering might be
        // different, but the computed values end up being the same.
        //
        // This is a performance trade-off, on the assumption that if the ordering is different,
        // there's likely a different value as well, but might over-invalidate.
        //
        // Doing the slow thing (checking all the keys) shows up a lot in profiles, see bug 1926423.
        //
        // Note that self.own_properties != other.own_properties is not the same, as by default
        // IndexMap comparison is not order-aware.
        //
        // Note also that for this comparison we do care about e.g. attribute-tainting being
        // different.
        {
            let own = self.own_properties.as_slice();
            let other = other.own_properties.as_slice();
            if own.len() != other.len() {
                return false;
            }
            for ((own_k, own_v), (other_k, other_v)) in own.iter().zip(other.iter()) {
                if own_k != other_k || !can_deduplicate_values(own_v.as_ref(), other_v.as_ref()) {
                    return false;
                }
            }
        }
        self.parent == other.parent
    }
