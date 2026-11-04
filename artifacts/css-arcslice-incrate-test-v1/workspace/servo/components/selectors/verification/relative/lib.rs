/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

#[path = "../../bloom.rs"]
pub mod bloom;

pub fn insert(filter: &mut bloom::BloomFilter, hash: u32) {
    filter.insert_hash(hash);
}

pub fn contains(filter: &bloom::BloomFilter, hash: u32) -> bool {
    filter.might_contain_hash(hash)
}

extern crate self as hashbrown;

pub mod hash_map {
    pub use std::collections::hash_map::Entry;
}

pub type FxHashMap<K, V> = std::collections::HashMap<K, V>;
pub trait SelectorImpl {}

pub mod context {
    #[derive(Clone, Copy)]
    pub struct QuirksMode;
}

pub mod parser {
    use super::{SelectorImpl, context::QuirksMode};

    pub enum RelativeSelectorMatchHint {
        InNextSibling,
        InSibling,
        InNextSiblingSubtree,
        InSiblingSubtree,
        InSubtree,
        InChild,
    }

    pub struct Selector<I>(pub u32, pub std::marker::PhantomData<I>);

    impl<I> Selector<I> {
        pub fn iter(&self) -> std::iter::Once<&Self> {
            std::iter::once(self)
        }
    }

    pub struct RelativeSelector<I: SelectorImpl> {
        pub selector: Selector<I>,
        pub match_hint: RelativeSelectorMatchHint,
    }

    pub fn collect_selector_hashes<'a, I: SelectorImpl + 'a, Iter>(
        iter: Iter,
        _: QuirksMode,
        hashes: &mut [u32; 4],
        len: &mut usize,
    ) -> bool
    where
        Iter: Iterator<Item = &'a Selector<I>>,
    {
        for selector in iter {
            hashes[*len] = selector.0;
            *len += 1;
        }
        true
    }
}

pub mod tree {
    use super::bloom::BloomFilter;

    pub type OpaqueElement = usize;

    pub trait Element: Copy {
        fn opaque(self) -> OpaqueElement;
        fn first_element_child(self) -> Option<Self>;
        fn next_sibling_element(self) -> Option<Self>;
        fn parent_element(self) -> Option<Self>;
        fn add_element_unique_hashes(self, filter: &mut BloomFilter) -> bool;
    }
}

pub mod relative_filter {
    include!("../../relative_selector/filter.rs");

    pub fn walk<E: Element>(element: E, filter: &mut BloomFilter, descendants: bool) -> bool {
        add_to_filter(
            element,
            filter,
            if descendants {
                TraversalKind::Descendants
            } else {
                TraversalKind::Children
            },
        )
    }

    pub fn cached<E: Element>(
        map: &mut RelativeSelectorFilterMap,
        element: E,
        descendants: bool,
    ) -> bool {
        map.get_filter(
            element,
            if descendants {
                TraversalKind::Descendants
            } else {
                TraversalKind::Children
            },
        )
        .is_some()
    }

    pub fn update<E: Element>(
        filter: Option<Box<BloomFilter>>,
        element: E,
        descendants: bool,
    ) -> Option<Box<BloomFilter>> {
        let mut entry = match filter {
            Some(filter) => Entry::HasFilter(filter),
            None => Entry::Lookup,
        };
        entry.update(
            element,
            if descendants {
                TraversalKind::Descendants
            } else {
                TraversalKind::Children
            },
        );
        match entry {
            Entry::Lookup => None,
            Entry::HasFilter(filter) => Some(filter),
        }
    }

    pub fn target<E: Element>(element: E, hint: &RelativeSelectorMatchHint) -> Option<(E, bool)> {
        match filter_target(element, hint) {
            Some((element, kind)) => Some((element, kind == TraversalKind::Descendants)),
            None => None,
        }
    }

    pub fn same_key(
        first: usize,
        first_descendants: bool,
        second: usize,
        second_descendants: bool,
    ) -> bool {
        let first_kind = if first_descendants {
            TraversalKind::Descendants
        } else {
            TraversalKind::Children
        };
        let second_kind = if second_descendants {
            TraversalKind::Descendants
        } else {
            TraversalKind::Children
        };
        Key(first, first_kind) == Key(second, second_kind)
    }
}
