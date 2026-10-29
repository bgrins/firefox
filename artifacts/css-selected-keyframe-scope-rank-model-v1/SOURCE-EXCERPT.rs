    pub fn get_shadow_root_for_scoped<E: TElement>(
        &self,
        element: E,
    ) -> Option<<<E as TElement>::ConcreteNode as TNode>::ConcreteShadowRoot> {
        let mut cascade_order = self.shadow_order().0;
        if cascade_order < 0 {
            let element = element.ultimate_originating_element();
            let mut slot = element.assigned_slot();
            while let Some(s) = slot {
                cascade_order += 1;
                if cascade_order == 0 {
                    return s.containing_shadow();
                }
                slot = s.assigned_slot();
            }
            if cascade_order != -1 {
                return None;
            }

            return element.shadow_root();
        }
        debug_assert!(cascade_order >= 0);
        let mut containing_shadow = element.containing_shadow();
        while let Some(s) = containing_shadow {
            if cascade_order == 0 {
                break;
            }
            cascade_order -= 1;
            containing_shadow = s.host().containing_shadow();
        }
        containing_shadow
    }
}

/// A counter to track how many shadow root rules deep we are. This is used to
/// handle:
///
/// https://drafts.csswg.org/css-scoping/#shadow-cascading
///
/// See the static functions for the meaning of different values.
#[derive(Clone, Copy, Debug, Eq, Hash, MallocSizeOf, Ord, PartialEq, PartialOrd)]
#[repr(transparent)]
pub struct ShadowCascadeOrder(i8);

impl ShadowCascadeOrder {
    /// We keep a maximum of 3 bits of order as a limit so that we can pack CascadeLevel in 1 byte.
    const MAX: i8 = 0b111;
    const MIN: i8 = -Self::MAX;

    /// A level for the outermost shadow tree (the shadow tree we own, and the
    /// ones from the slots we're slotted in).
    #[inline]
    pub fn for_outermost_shadow_tree() -> Self {
        Self(-1)
    }

    /// A level for the element's tree.
    #[inline]
    pub fn for_same_tree() -> Self {
        Self(0)
    }

    /// A level for the innermost containing tree (the one closest to the
    /// element).
    #[inline]
    pub fn for_innermost_containing_tree() -> Self {
        Self(1)
    }

    /// Returns true if the level is in the same or a containing shadow tree.
    #[inline]
    pub fn is_in_same_or_containing_tree(&self) -> bool {
        self.0 > 0
    }

    /// Decrement the level, moving inwards. We should only move inwards if
    /// we're traversing slots.
    #[inline]
    pub fn dec(&mut self) {
        debug_assert!(self.0 < 0);
        if self.0 != Self::MIN {
            self.0 -= 1;
        }
    }

    /// The level, moving inwards. We should only move inwards if we're
    /// traversing slots.
    #[inline]
    pub fn inc(&mut self) {
        debug_assert_ne!(self.0, -1);
        if self.0 != Self::MAX {
            self.0 += 1;
        }
    }
}

