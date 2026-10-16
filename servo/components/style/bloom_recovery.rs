/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

pub(super) trait RecoveryState {
    type Element: Copy + Eq;

    fn parent(element: Self::Element) -> Option<Self::Element>;
    fn len(&self) -> usize;
    fn current_parent(&self) -> Option<Self::Element>;
    fn clear(&mut self);
    fn pop(&mut self) -> Option<Self::Element>;
    fn push(&mut self, element: Self::Element);
    fn pending_push(&mut self, element: Self::Element);
    fn pending_pop(&mut self) -> Option<Self::Element>;
}

pub(super) fn rebuild<S: RecoveryState>(state: &mut S, mut element: S::Element) {
    state.clear();
    while let Some(parent) = S::parent(element) {
        state.pending_push(parent);
        element = parent;
    }
    while let Some(parent) = state.pending_pop() {
        state.push(parent);
    }
}

pub(super) fn recover<S: RecoveryState>(
    state: &mut S,
    element: S::Element,
    element_depth: usize,
    allow_separate_roots: bool,
) {
    // Easy case, we're in a different restyle, or we're empty.
    if state.len() == 0 {
        rebuild(state, element);
        return;
    }

    let traversal_parent = match S::parent(element) {
        Some(parent) => parent,
        None => {
            // Yay, another easy case.
            state.clear();
            return;
        },
    };

    if let Some(parent) = state.current_parent() {
        if parent == traversal_parent {
            // Ta da, cache hit, we're all done.
            return;
        }
    }

    if element_depth == 0 {
        state.clear();
        return;
    }

    // We should've early exited above.
    debug_assert!(
        element_depth != 0,
        "We should have already cleared the bloom filter"
    );
    debug_assert!(state.len() != 0, "How! We should've just rebuilt!");

    // Now the fun begins: We have the depth of the dom and the depth of the
    // last element inserted in the filter, let's try to find a common
    // parent.
    //
    // The current depth, that is, the depth of the last element inserted in
    // the bloom filter, is the number of elements _minus one_, that is: if
    // there's one element, it must be the root -> depth zero.
    let mut current_depth = state.len() - 1;

    // If the filter represents an element too deep in the dom, we need to
    // pop ancestors.
    while current_depth > element_depth - 1 {
        assert!(state.pop().is_some(), "Emilio is bad at math");
        current_depth -= 1;
    }

    // Now let's try to find a common parent in the bloom filter chain,
    // starting with traversal_parent.
    let mut common_parent = traversal_parent;
    let mut common_parent_depth = element_depth - 1;

    // Let's collect the parents we are going to need to insert once we've
    // found the common one.

    // If the bloom filter still doesn't have enough elements, the common
    // parent is up in the dom.
    while common_parent_depth > current_depth {
        // TODO(emilio): Seems like we could insert parents here, then
        // reverse the slice.
        state.pending_push(common_parent);
        let Some(parent) = S::parent(common_parent) else {
            panic!("We were lied to");
        };
        common_parent = parent;
        common_parent_depth -= 1;
    }

    // Now the two depths are the same.
    debug_assert_eq!(common_parent_depth, current_depth);

    // Happy case: The parents match, we only need to push the ancestors
    // we've collected and we'll never enter in this loop.
    //
    // Not-so-happy case: Parent's don't match, so we need to keep going up
    // until we find a common ancestor.
    //
    // Gecko currently models native anonymous content that conceptually
    // hangs off the document (such as scrollbars) as a separate subtree
    // from the document root.
    //
    // Thus it's possible with Gecko that we do not find any common
    // ancestor.
    while state.current_parent().unwrap() != common_parent {
        state.pending_push(common_parent);
        state.pop().unwrap();
        common_parent = match S::parent(common_parent) {
            Some(parent) => parent,
            None => {
                debug_assert!(state.len() == 0);
                if allow_separate_roots {
                    break;
                } else {
                    panic!("should have found a common ancestor");
                }
            },
        }
    }

    // Now the parents match, so insert the stack of elements we have been
    // collecting so far.
    while let Some(parent) = state.pending_pop() {
        state.push(parent);
    }

    debug_assert_eq!(state.len(), element_depth);

    // We're done! Easy.
}
