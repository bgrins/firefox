/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use super::bloom_filter;
use super::bloom_recovery::RecoveryState;
use crate::dom::{SendElement, TElement};
use selectors::bloom::BloomFilter;
use smallvec::SmallVec;
use std::marker::PhantomData;

pub(super) struct PushedElement<E: TElement> {
    /// The element that was pushed.
    pub(super) element: SendElement<E>,

    /// The number of hashes pushed for the element.
    num_hashes: usize,
}

impl<E: TElement> PushedElement<E> {
    fn new(element: E, num_hashes: usize) -> Self {
        Self {
            element: unsafe { SendElement::new(element) },
            num_hashes,
        }
    }
}

pub(super) struct HashInsert<'a> {
    filter: &'a mut BloomFilter,
    hashes: &'a mut SmallVec<[u32; 64]>,
    count: usize,
}

impl HashInsert<'_> {
    #[inline]
    pub(super) fn push_hash(&mut self, hash: u32) {
        self.count += 1;
        self.filter.insert_hash(hash);
        self.hashes.push(hash);
    }
}

pub(super) trait HashProvider<E> {
    fn insert(element: E, sink: &mut HashInsert<'_>);
    fn expected(element: E) -> Vec<u32>;
}

pub(super) struct Storage<'a, E: TElement> {
    filter: &'a mut BloomFilter,
    elements: &'a mut SmallVec<[PushedElement<E>; 16]>,
    pushed_hashes: &'a mut SmallVec<[u32; 64]>,
    max_pushed_hashes: &'a mut usize,
}

impl<'a, E: TElement> Storage<'a, E> {
    pub(super) fn new(
        filter: &'a mut BloomFilter,
        elements: &'a mut SmallVec<[PushedElement<E>; 16]>,
        pushed_hashes: &'a mut SmallVec<[u32; 64]>,
        max_pushed_hashes: &'a mut usize,
    ) -> Self {
        Self {
            filter,
            elements,
            pushed_hashes,
            max_pushed_hashes,
        }
    }

    pub(super) fn push<P: HashProvider<E>>(&mut self, element: E) {
        if cfg!(debug_assertions) && self.elements.is_empty() {
            assert!(element.traversal_parent().is_none());
        }
        self.push_internal::<P>(element);
    }

    /// Same as `push`, but without asserting, in order to use it from
    /// `rebuild`.
    fn push_internal<P: HashProvider<E>>(&mut self, element: E) {
        let mut sink = HashInsert {
            filter: self.filter,
            hashes: self.pushed_hashes,
            count: 0,
        };
        P::insert(element, &mut sink);
        let count = sink.count;
        *self.max_pushed_hashes =
            bloom_filter::update_high_water(*self.max_pushed_hashes, self.pushed_hashes.len());
        self.elements.push(PushedElement::new(element, count));
    }

    /// Pop the last element in the bloom filter and return it.
    #[inline]
    fn pop<P: HashProvider<E>>(&mut self) -> Option<E> {
        let PushedElement {
            element,
            num_hashes,
        } = self.elements.pop()?;
        let popped_element = *element;

        // Verify that the pushed hashes match the ones we'd get from the element.
        let mut expected_hashes = vec![];
        if cfg!(debug_assertions) {
            expected_hashes = P::expected(popped_element);
        }

        let mut remaining = num_hashes;
        while remaining != 0 {
            remaining -= 1;
            let hash = self.pushed_hashes.pop().unwrap();
            debug_assert_eq!(expected_hashes.pop().unwrap(), hash);
            self.filter.remove_hash(hash);
        }

        Some(popped_element)
    }

    pub(super) fn clear(&mut self) {
        self.elements.clear();
        bloom_filter::clear_filter(self.filter, self.pushed_hashes, *self.max_pushed_hashes);
        self.pushed_hashes.clear();
        debug_assert!(self.filter.is_zeroed());
        *self.max_pushed_hashes = 0;
    }
}

pub(super) struct RecoveryStack<'a, E: TElement, P> {
    storage: Storage<'a, E>,
    pending: SmallVec<[E; 16]>,
    provider: PhantomData<P>,
}

impl<'a, E: TElement, P> RecoveryStack<'a, E, P> {
    pub(super) fn new(storage: Storage<'a, E>) -> Self {
        Self {
            storage,
            pending: SmallVec::new(),
            provider: PhantomData,
        }
    }
}

impl<E: TElement, P: HashProvider<E>> RecoveryState for RecoveryStack<'_, E, P> {
    type Element = E;

    fn parent(element: E) -> Option<E> {
        element.traversal_parent()
    }

    fn len(&self) -> usize {
        self.storage.elements.len()
    }

    fn current_parent(&self) -> Option<E> {
        self.storage.elements.last().map(|el| *el.element)
    }

    fn clear(&mut self) {
        self.storage.clear();
    }

    fn pop(&mut self) -> Option<E> {
        self.storage.pop::<P>()
    }

    fn push(&mut self, element: E) {
        self.storage.push::<P>(element);
    }

    fn pending_push(&mut self, element: E) {
        self.pending.push(element);
    }

    fn pending_pop(&mut self) -> Option<E> {
        self.pending.pop()
    }
}
