/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

//! Gecko-specific bits for the styling DOM traversal.

use crate::context::{SharedStyleContext, StyleContext};
use crate::dom::{TElement, TNode};
use crate::gecko::wrapper::{GeckoElement, GeckoNode};
use crate::invalidation::element::restyle_hints::RestyleHint;
use crate::traversal::{DomTraversal, recalc_style_at};
use std::sync::atomic::{AtomicBool, Ordering};

/// This is the simple struct that Gecko uses to encapsulate a DOM traversal for
/// styling.
pub struct RecalcStyleOnly<'a> {
    shared: SharedStyleContext<'a>,
    normal_descendant_restyle: AtomicBool,
}

impl<'a> RecalcStyleOnly<'a> {
    /// Create a `RecalcStyleOnly` traversal from a `SharedStyleContext`.
    pub fn new(shared: SharedStyleContext<'a>) -> Self {
        RecalcStyleOnly {
            shared,
            normal_descendant_restyle: AtomicBool::new(false),
        }
    }

    /// Whether animation styling produced descendant font-dependent work.
    pub fn needs_normal_descendant_restyle(&self) -> bool {
        self.normal_descendant_restyle.load(Ordering::Relaxed)
    }
}

impl<'recalc, 'le> DomTraversal<GeckoElement<'le>> for RecalcStyleOnly<'recalc> {
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
            if std::env::var_os("MOZ_ROOT_FONT_STARTUP_TRACE").is_some() {
                eprintln!(
                    "RFST returned node={:#x} flags={:?} hint={:?} thread={:?}",
                    el.as_node().opaque().0,
                    self.shared.traversal_flags,
                    child_hint,
                    std::thread::current().id()
                );
            }
            if self.shared.traversal_flags.for_animation_only()
                && child_hint.intersects(RestyleHint::RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT)
            {
                self.normal_descendant_restyle.store(true, Ordering::Relaxed);
                if std::env::var_os("MOZ_ROOT_FONT_STARTUP_TRACE").is_some() {
                    eprintln!(
                        "RFST signal node={:#x} flags={:?} thread={:?}",
                        el.as_node().opaque().0,
                        self.shared.traversal_flags,
                        std::thread::current().id()
                    );
                }
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
