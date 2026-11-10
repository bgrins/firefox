/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

//! Gecko-specific bits for the styling DOM traversal.

use crate::context::{SharedStyleContext, StyleContext};
use crate::dom::{SendElement, TElement, TNode};
use crate::gecko::wrapper::{GeckoElement, GeckoNode};
use crate::invalidation::element::restyle_hints::RestyleHint;
use crate::traversal::{DomTraversal, recalc_style_at};
use std::sync::Mutex;
use std::sync::atomic::{AtomicBool, Ordering};

/// This is the simple struct that Gecko uses to encapsulate a DOM traversal for
/// styling.
pub struct RecalcStyleOnly<'a, 'le> {
    shared: SharedStyleContext<'a>,
    normal_descendant_restyle: AtomicBool,
    style_query_restyle: Mutex<Vec<(SendElement<GeckoElement<'le>>, RestyleHint)>>,
}

impl<'a, 'le> RecalcStyleOnly<'a, 'le> {
    /// Create a `RecalcStyleOnly` traversal from a `SharedStyleContext`.
    pub fn new(shared: SharedStyleContext<'a>) -> Self {
        RecalcStyleOnly {
            shared,
            normal_descendant_restyle: AtomicBool::new(false),
            style_query_restyle: Mutex::new(Vec::new()),
        }
    }

    /// Whether animation styling produced descendant font-dependent work.
    pub fn needs_normal_descendant_restyle(&self) -> bool {
        self.normal_descendant_restyle.load(Ordering::Relaxed)
    }

    /// Consume query invalidations after all traversal workers have joined.
    pub fn style_query_restyle_producers(
        self,
    ) -> Vec<(SendElement<GeckoElement<'le>>, RestyleHint)> {
        self.style_query_restyle.into_inner().unwrap()
    }
}

impl<'recalc, 'le> DomTraversal<GeckoElement<'le>> for RecalcStyleOnly<'recalc, 'le> {
    fn process_preorder<F>(
        &self,
        context: &mut StyleContext<GeckoElement<'le>>,
        node: GeckoNode<'le>,
        note_child: F,
    ) where
        F: FnMut(GeckoNode<'le>),
    {
        if let Some(el) = node.as_element() {
            let mut data = unsafe { el.ensure_data() };
            let child_hint = recalc_style_at(self, context, el, &mut data, note_child);
            if self.shared.traversal_flags.for_animation_only()
                && child_hint.intersects(RestyleHint::RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT)
            {
                self.normal_descendant_restyle.store(true, Ordering::Relaxed);
            }
            let query_hint = child_hint
                & (RestyleHint::RESTYLE_IF_AFFECTED_BY_STYLE_QUERIES
                    | RestyleHint::RESTYLE_IF_AFFECTED_BY_NAMED_STYLE_CONTAINER);
            if self.shared.traversal_flags.for_animation_only() && !query_hint.is_empty() {
                drop(data);
                self.style_query_restyle
                    .lock()
                    .unwrap()
                    .push((unsafe { SendElement::new(el) }, query_hint));
            }
        }
    }

    fn process_postorder(&self, _: &mut StyleContext<GeckoElement<'le>>, _: GeckoNode<'le>) {
        unreachable!();
    }

    /// We don't use the post-order traversal for anything.
    fn needs_postorder_traversal() -> bool {
        false
    }

    fn shared_context(&self) -> &SharedStyleContext<'recalc> {
        &self.shared
    }
}
