/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use super::bloom_storage::{HashInsert, HashProvider};
use super::each_relevant_element_hash;
use crate::dom::TElement;

pub(super) struct DomHashes;

impl<E: TElement> HashProvider<E> for DomHashes {
    fn insert(element: E, sink: &mut HashInsert<'_>) {
        let mut borrowed = sink.borrowed();
        each_relevant_element_hash(element, move |hash| borrowed.push_hash(hash));
    }

    fn expected(element: E) -> Vec<u32> {
        let mut hashes = vec![];
        each_relevant_element_hash(element, |hash| hashes.push(hash));
        hashes
    }
}
