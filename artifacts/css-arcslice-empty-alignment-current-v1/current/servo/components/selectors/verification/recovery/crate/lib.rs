/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

#![allow(private_bounds, private_interfaces)]
include!("../../lib.rs");
pub mod dom {
    pub trait TElement: Copy + Eq + std::fmt::Debug {
        fn traversal_parent(&self) -> Option<Self>;
    }

    pub struct SendElement<E: TElement>(E);

    impl<E: TElement> SendElement<E> {
        pub unsafe fn new(element: E) -> Self {
            Self(element)
        }
    }

    impl<E: TElement> std::ops::Deref for SendElement<E> {
        type Target = E;

        fn deref(&self) -> &E {
            &self.0
        }
    }
}

use style_bloom_filter as bloom_filter;
use style_bloom_recovery as bloom_recovery;
#[path = "../../../../style/bloom_storage.rs"]
mod bloom_storage;
use bloom_storage::{HashInsert, HashProvider, RecoveryStack, Storage};
use dom::TElement;
pub fn storage_hash(sink: &mut HashInsert<'_>, hash: u32) {
    sink.borrowed().push_hash(hash);
}
pub fn storage_push<E: TElement, P: HashProvider<E>>(s: &mut Storage<'_, E>, e: E) {
    s.push::<P>(e);
}
pub fn storage_clear<E: TElement>(s: &mut Storage<'_, E>) {
    s.clear();
}
pub fn storage_recover<E: TElement, P: HashProvider<E>>(
    s: &mut RecoveryStack<'_, E, P>,
    e: E,
    d: usize,
    cross: bool,
) {
    bloom_recovery::recover(s, e, d, cross);
}
pub fn storage_rebuild<E: TElement, P: HashProvider<E>>(s: &mut RecoveryStack<'_, E, P>, e: E) {
    bloom_recovery::rebuild(s, e);
}

fn each_relevant_element_hash<E: dom::TElement, F: FnMut(u32)>(_element: E, _f: F) {
    unimplemented!()
}
#[path = "../../../../style/bloom_hashes.rs"]
mod bloom_hashes;
pub fn provider_insert<E: dom::TElement>(element: E, sink: &mut HashInsert<'_>) {
    bloom_hashes::DomHashes::insert(element, sink);
}
pub fn provider_expected<E: dom::TElement>(element: E) -> Vec<u32> {
    bloom_hashes::DomHashes::expected(element)
}

pub fn provider_storage_push<E: dom::TElement>(s: &mut Storage<'_, E>, e: E) {
    storage_push::<E, bloom_hashes::DomHashes>(s, e);
}
