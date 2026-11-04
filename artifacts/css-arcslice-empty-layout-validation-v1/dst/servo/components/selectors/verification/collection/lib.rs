/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

// Make |cargo bench| work.
#![cfg_attr(feature = "bench", feature(test))]

#[path = "../../ancestor_hashes.rs"]
mod ancestor_hashes;
#[path = "../../attr.rs"]
pub mod attr;
#[path = "../../bloom.rs"]
pub mod bloom;
#[path = "../../builder.rs"]
mod builder;
#[path = "../../context.rs"]
pub mod context;
#[path = "../../kleene_value.rs"]
pub mod kleene_value;
#[path = "../../matching.rs"]
pub mod matching;
#[path = "../../nth_index_cache.rs"]
mod nth_index_cache;
pub mod parser {
    include!("../../parser.rs");
    pub fn collect_simple(
        component: &Component<crate::concrete::Impl>,
        quirks: QuirksMode,
    ) -> Option<u32> {
        simple_selector_hash(component, quirks)
    }

    pub fn collect_ancestors<Impl: SelectorImpl>(
        selector: &Selector<Impl>,
        quirks: QuirksMode,
    ) -> ([u32; 4], usize) {
        let mut hashes = [0; 4];
        let mut len = 0;
        collect_ancestor_hashes(selector.iter(), quirks, &mut hashes, &mut len);
        (hashes, len)
    }

    pub fn collect_relative_compound<Impl: SelectorImpl>(
        selector: &Selector<Impl>,
        quirks: QuirksMode,
    ) -> ([u32; 4], usize) {
        let mut hashes = [0; 4];
        let mut len = 0;
        collect_selector_hashes(selector.iter(), quirks, &mut hashes, &mut len);
        (hashes, len)
    }
}
#[path = "../../relative_selector/mod.rs"]
pub mod relative_selector;
#[path = "../../sink.rs"]
pub mod sink;
#[path = "../../subtree_filter.rs"]
pub mod subtree_filter;
#[path = "../../tree.rs"]
mod tree;
#[path = "../../visitor.rs"]
pub mod visitor;

pub use crate::nth_index_cache::NthIndexCache;
pub use crate::parser::{Parser, SelectorImpl, SelectorList};
pub use crate::tree::{Element, OpaqueElement};

/// A hash map using the Fx hasher.
pub type FxHashMap<K, V> = hashbrown::HashMap<K, V, rustc_hash::FxBuildHasher>;

mod concrete;
