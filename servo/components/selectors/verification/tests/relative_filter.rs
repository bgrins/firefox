/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use std::cell::{Cell, RefCell};

pub use stylo_bloom_verification::bloom;
pub type FxHashMap<K, V> = std::collections::HashMap<K, V>;
pub trait SelectorImpl {}

mod context {
    #[derive(Clone, Copy)]
    pub struct QuirksMode;
}

#[allow(dead_code)]
mod parser {
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
        pub marker: std::marker::PhantomData<I>,
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

mod tree {
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

#[path = "../../relative_selector/filter.rs"]
mod filter;

struct Impl;
impl SelectorImpl for Impl {}

#[derive(Clone, Copy)]
struct Chain<'a> {
    index: usize,
    length: usize,
    visited: &'a Cell<usize>,
}

impl tree::Element for Chain<'_> {
    fn opaque(self) -> usize {
        self.index
    }

    fn first_element_child(self) -> Option<Self> {
        (self.index + 1 < self.length).then_some(Self {
            index: self.index + 1,
            ..self
        })
    }

    fn next_sibling_element(self) -> Option<Self> {
        None
    }

    fn parent_element(self) -> Option<Self> {
        self.index
            .checked_sub(1)
            .map(|index| Self { index, ..self })
    }

    fn add_element_unique_hashes(self, filter: &mut bloom::BloomFilter) -> bool {
        self.visited.set(self.visited.get() + 1);
        filter.insert_hash(self.index as u32);
        true
    }
}

fn visit_chain(length: usize) {
    let visited = Cell::new(0);
    let root = Chain {
        index: 0,
        length,
        visited: &visited,
    };
    let selector = parser::RelativeSelector::<Impl> {
        selector: parser::Selector(1, std::marker::PhantomData),
        match_hint: parser::RelativeSelectorMatchHint::InSubtree,
        marker: std::marker::PhantomData,
    };
    let mut filters = filter::RelativeSelectorFilterMap::default();
    assert!(!filters.fast_reject(root, &selector, context::QuirksMode));
    assert_eq!(visited.get(), 0);
    assert!(!filters.fast_reject(root, &selector, context::QuirksMode));
    assert_eq!(visited.get(), length - 1);
    assert!(!filters.fast_reject(root, &selector, context::QuirksMode));
    assert_eq!(visited.get(), length - 1);
}

#[test]
fn deep_subtree_filter_uses_bounded_stack() {
    if std::env::var_os("STYLO_BLOOM_STACK_CHILD").is_some() {
        std::thread::Builder::new()
            .stack_size(128 * 1024)
            .spawn(|| visit_chain(100_000))
            .unwrap()
            .join()
            .unwrap();
        return;
    }
    let output = std::process::Command::new(std::env::current_exe().unwrap())
        .args([
            "--exact",
            "deep_subtree_filter_uses_bounded_stack",
            "--nocapture",
        ])
        .env("STYLO_BLOOM_STACK_CHILD", "1")
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "child failed: {}\n{}",
        output.status,
        String::from_utf8_lossy(&output.stderr)
    );
}

#[derive(Clone, Copy)]
struct TreeElement<'a> {
    index: usize,
    parents: &'a [Option<usize>],
    visited: &'a RefCell<Vec<usize>>,
    unavailable: &'a Cell<Option<usize>>,
}

impl tree::Element for TreeElement<'_> {
    fn opaque(self) -> usize {
        self.index
    }

    fn first_element_child(self) -> Option<Self> {
        self.parents
            .iter()
            .position(|parent| *parent == Some(self.index))
            .map(|index| Self { index, ..self })
    }

    fn next_sibling_element(self) -> Option<Self> {
        let parent = self.parents[self.index]?;
        (self.index + 1..self.parents.len())
            .find(|&index| self.parents[index] == Some(parent))
            .map(|index| Self { index, ..self })
    }

    fn parent_element(self) -> Option<Self> {
        self.parents[self.index].map(|index| Self { index, ..self })
    }

    fn add_element_unique_hashes(self, filter: &mut bloom::BloomFilter) -> bool {
        self.visited.borrow_mut().push(self.index);
        if self.unavailable.get() == Some(self.index) {
            return false;
        }
        filter.insert_hash(element_hash(self.index));
        true
    }
}

fn element_hash(index: usize) -> u32 {
    (index as u32 + 1) * 0x1001
}

fn selector(hash: u32, subtree: bool) -> parser::RelativeSelector<Impl> {
    parser::RelativeSelector {
        selector: parser::Selector(hash, std::marker::PhantomData),
        match_hint: if subtree {
            parser::RelativeSelectorMatchHint::InSubtree
        } else {
            parser::RelativeSelectorMatchHint::InChild
        },
        marker: std::marker::PhantomData,
    }
}

#[test]
fn branching_traversal_stays_inside_the_requested_subtree() {
    let parents = [
        None,
        Some(0),
        Some(1),
        Some(2),
        Some(1),
        Some(4),
        Some(0),
        Some(6),
    ];
    let visited = RefCell::new(Vec::new());
    let unavailable = Cell::new(None);
    let root = TreeElement {
        index: 1,
        parents: &parents,
        visited: &visited,
        unavailable: &unavailable,
    };
    for (subtree, expected) in [(false, &[2, 4][..]), (true, &[2, 3, 4, 5][..])] {
        let mut filters = filter::RelativeSelectorFilterMap::default();
        visited.borrow_mut().clear();
        assert!(!filters.fast_reject(root, &selector(0, subtree), context::QuirksMode));
        for index in 0..parents.len() {
            assert_eq!(
                filters.fast_reject(
                    root,
                    &selector(element_hash(index), subtree),
                    context::QuirksMode
                ),
                !expected.contains(&index),
                "subtree={subtree}, index={index}"
            );
        }
        assert_eq!(&*visited.borrow(), expected);
    }
}

#[test]
fn incomplete_filter_is_discarded_and_retried() {
    let parents = [None, Some(0), Some(1), Some(0)];
    let visited = RefCell::new(Vec::new());
    let unavailable = Cell::new(Some(2));
    let root = TreeElement {
        index: 0,
        parents: &parents,
        visited: &visited,
        unavailable: &unavailable,
    };
    let mut filters = filter::RelativeSelectorFilterMap::default();
    let last = selector(element_hash(3), true);
    for _ in 0..3 {
        assert!(!filters.fast_reject(root, &last, context::QuirksMode));
    }
    assert_eq!(&*visited.borrow(), &[1, 2, 1, 2]);
    unavailable.set(None);
    visited.borrow_mut().clear();
    assert!(!filters.fast_reject(root, &last, context::QuirksMode));
    assert_eq!(&*visited.borrow(), &[1, 2, 3]);
    assert!(filters.fast_reject(root, &selector(element_hash(4), true), context::QuirksMode));
    assert_eq!(&*visited.borrow(), &[1, 2, 3]);
}
