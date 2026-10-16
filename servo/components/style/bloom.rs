/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

//! The style bloom filter is used as an optimization when matching deep
//! descendant selectors.

#![deny(missing_docs)]

use crate::LocalName;
use crate::dom::TElement;
use atomic_refcell::{AtomicRefCell, AtomicRefMut};
use selectors::bloom::BloomFilter;
use smallvec::SmallVec;

#[path = "bloom_filter.rs"]
mod bloom_filter;
#[path = "bloom_hashes.rs"]
mod bloom_hashes;
#[path = "bloom_recovery.rs"]
mod bloom_recovery;
#[path = "bloom_storage.rs"]
mod bloom_storage;

use bloom_hashes::DomHashes;
use bloom_storage::{PushedElement, RecoveryStack, Storage};

thread_local! {
    /// Bloom filters are large allocations, so we store them in thread-local storage
    /// such that they can be reused across style traversals. StyleBloom is responsible
    /// for ensuring that the bloom filter is zeroed when it is dropped.
    ///
    /// We intentionally leak this from TLS because we don't have the guarantee
    /// of TLS destructors to run in worker threads.
    ///
    /// Also, leaking it guarantees that we can borrow it indefinitely.
    ///
    /// We could change this once https://github.com/rayon-rs/rayon/issues/688
    /// is fixed, hopefully, which point we'd need to change the filter member below to be an
    /// arc and carry an owning reference around or so.
    static BLOOM_KEY: &'static AtomicRefCell<BloomFilter> = Box::leak(Default::default());
}

/// A struct that allows us to fast-reject deep descendant selectors avoiding
/// selector-matching.
///
/// This is implemented using a counting bloom filter, and it's a standard
/// optimization. See Gecko's `AncestorFilter`, and Blink's and WebKit's
/// `SelectorFilter`.
///
/// The constraints for Servo's style system are a bit different compared to
/// traditional style systems given Servo does a parallel breadth-first
/// traversal instead of a sequential depth-first traversal.
///
/// This implies that we need to track a bit more state than other browsers to
/// ensure we're doing the correct thing during the traversal, and being able to
/// apply this optimization effectively.
///
/// Concretely, we have a bloom filter instance per worker thread, and we track
/// the current DOM depth in order to find a common ancestor when it doesn't
/// match the previous element we've styled.
///
/// This is usually a pretty fast operation (we use to be one level deeper than
/// the previous one), but in the case of work-stealing, we may needed to push
/// and pop multiple elements.
///
/// See the `insert_parents_recovering`, where most of the magic happens.
///
/// Regarding thread-safety, this struct is safe because:
///
///  * We clear this after a restyle.
///  * The DOM shape and attributes (and every other thing we access here) are
///    immutable during a restyle.
///
pub struct StyleBloom<E: TElement> {
    /// A handle to the bloom filter from the thread upon which this StyleBloom
    /// was created. We use AtomicRefCell so that this is all |Send|, which allows
    /// StyleBloom to live in ThreadLocalStyleContext, which is dropped from the
    /// parent thread.
    filter: AtomicRefMut<'static, BloomFilter>,

    /// The stack of elements that this bloom filter contains, along with the
    /// number of hashes pushed for each element.
    elements: SmallVec<[PushedElement<E>; 16]>,

    /// Stack of hashes that have been pushed onto this filter.
    pushed_hashes: SmallVec<[u32; 64]>,

    /// Largest hash stack since clear(), including hashes removed by pop().
    max_pushed_hashes: usize,
}

/// Returns whether the attribute name is excluded from the bloom filter.
///
/// We do this for attributes that are very common but not commonly used in
/// selectors.
#[inline]
pub fn is_attr_name_excluded_from_filter(name: &LocalName) -> bool {
    *name == local_name!("class") || *name == local_name!("id") || *name == local_name!("style")
}

/// Gather all relevant hash for fast-reject filters from an element.
pub fn each_relevant_element_hash<E, F>(element: E, mut f: F)
where
    E: TElement,
    F: FnMut(u32),
{
    f(element.local_name().get_hash32());
    f(element.namespace().get_hash32());

    if let Some(id) = element.id() {
        f(id.get_hash32());
    }

    element.each_class(|class| f(class.get_hash32()));

    element.each_attr_name(|name| {
        if !is_attr_name_excluded_from_filter(name) {
            f(name.get_hash32())
        }
    });
}

impl<E: TElement> Drop for StyleBloom<E> {
    fn drop(&mut self) {
        // Leave the reusable bloom filter in a zeroed state.
        self.clear();
    }
}

impl<E: TElement> Default for StyleBloom<E> {
    fn default() -> Self {
        Self::new()
    }
}

impl<E: TElement> StyleBloom<E> {
    /// Create an empty `StyleBloom`. Because StyleBloom acquires the thread-
    /// local filter buffer, creating multiple live StyleBloom instances at
    /// the same time on the same thread will panic.

    // Forced out of line to limit stack frame sizes after extra inlining from
    // https://github.com/rust-lang/rust/pull/43931
    //
    // See https://github.com/servo/servo/pull/18420#issuecomment-328769322
    #[inline(never)]
    pub fn new() -> Self {
        let filter = BLOOM_KEY.with(|b| b.borrow_mut());
        debug_assert!(
            filter.is_zeroed(),
            "Forgot to zero the bloom filter last time"
        );
        StyleBloom {
            filter,
            elements: Default::default(),
            pushed_hashes: Default::default(),
            max_pushed_hashes: 0,
        }
    }

    /// Return the bloom filter used properly by the `selectors` crate.
    pub fn filter(&self) -> &BloomFilter {
        &self.filter
    }

    /// Push an element to the bloom filter, knowing that it's a child of the
    /// last element parent.
    pub fn push(&mut self, element: E) {
        self.storage().push::<DomHashes>(element);
    }

    fn storage(&mut self) -> Storage<'_, E> {
        Storage::new(
            &mut self.filter,
            &mut self.elements,
            &mut self.pushed_hashes,
            &mut self.max_pushed_hashes,
        )
    }

    /// Returns the DOM depth of elements that can be correctly
    /// matched against the bloom filter (that is, the number of
    /// elements in our list).
    pub fn matching_depth(&self) -> usize {
        self.elements.len()
    }

    /// Clears the bloom filter.
    pub fn clear(&mut self) {
        self.storage().clear();
    }

    /// Rebuilds the bloom filter up to the parent of the given element.
    pub fn rebuild(&mut self, element: E) {
        bloom_recovery::rebuild(
            &mut RecoveryStack::<E, DomHashes>::new(self.storage()),
            element,
        );
    }

    /// In debug builds, asserts that all the parents of `element` are in the
    /// bloom filter.
    ///
    /// Goes away in release builds.
    pub fn assert_complete(&self, mut element: E) {
        if cfg!(debug_assertions) {
            let mut checked = 0;
            while let Some(parent) = element.traversal_parent() {
                assert_eq!(
                    parent,
                    *(self.elements[self.elements.len() - 1 - checked].element)
                );
                element = parent;
                checked += 1;
            }
            assert_eq!(checked, self.elements.len());
        }
    }

    /// Get the element that represents the chain of things inserted
    /// into the filter right now.  That chain is the given element
    /// (if any) and its ancestors.
    #[inline]
    pub fn current_parent(&self) -> Option<E> {
        self.elements.last().map(|el| *el.element)
    }

    /// Insert the parents of an element in the bloom filter, trying to recover
    /// the filter if the last element inserted doesn't match.
    ///
    /// Gets the element depth in the dom, to make it efficient, or if not
    /// provided always rebuilds the filter from scratch.
    ///
    /// Returns the new bloom filter depth, that the traversal code is
    /// responsible to keep around if it wants to get an effective filter.
    pub fn insert_parents_recovering(&mut self, element: E, element_depth: usize) {
        bloom_recovery::recover(
            &mut RecoveryStack::<E, DomHashes>::new(self.storage()),
            element,
            element_depth,
            cfg!(feature = "gecko"),
        );
    }
}

pub(crate) trait AtomExt {
    fn get_hash32(&self) -> u32;
}

#[cfg(feature = "servo")]
impl<Static: string_cache::StaticAtomSet> AtomExt for string_cache::Atom<Static> {
    fn get_hash32(&self) -> u32 {
        let hash64 = self.get_hash();
        (hash64 >> 32) as u32 ^ (hash64 as u32)
    }
}

#[cfg(feature = "gecko")]
impl AtomExt for crate::Atom {
    fn get_hash32(&self) -> u32 {
        self.get_hash()
    }
}

#[cfg(feature = "gecko")]
impl AtomExt for crate::WeakAtom {
    fn get_hash32(&self) -> u32 {
        self.get_hash()
    }
}
