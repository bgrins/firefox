/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

extern crate stylo_bloom_verification as selectors;

#[derive(Clone, Copy, PartialEq)]
pub enum LocalName {
    Named(&'static str),
    Hashed(u32),
}

pub type Atom = LocalName;

pub struct WeakAtom(u32);

impl WeakAtom {
    pub fn get_hash(&self) -> u32 {
        self.0
    }
}

macro_rules! local_name {
    ($name:literal) => {
        crate::LocalName::Named($name)
    };
}

#[path = "../../../style/bloom.rs"]
#[allow(unexpected_cfgs)]
mod style_bloom;

impl LocalName {
    pub fn get_hash(&self) -> u32 {
        match *self {
            Self::Hashed(hash) => hash,
            Self::Named("div") => 0x001002,
            Self::Named("namespace") => 0x003004,
            _ => unreachable!(),
        }
    }
}

#[cfg(not(feature = "gecko"))]
impl style_bloom::AtomExt for LocalName {
    fn get_hash32(&self) -> u32 {
        self.get_hash()
    }
}

mod dom {
    use super::LocalName;

    pub trait TElement: Copy + Eq + std::fmt::Debug {
        fn traversal_parent(self) -> Option<Self>;
        fn local_name(self) -> LocalName;
        fn namespace(self) -> LocalName;
        fn id(self) -> Option<LocalName>;
        fn each_class(self, f: impl FnMut(&LocalName));
        fn each_attr_name(self, f: impl FnMut(&LocalName));
    }

    pub struct SendElement<E>(E);

    impl<E> SendElement<E> {
        pub unsafe fn new(element: E) -> Self {
            Self(element)
        }
    }

    impl<E> std::ops::Deref for SendElement<E> {
        type Target = E;

        fn deref(&self) -> &E {
            &self.0
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct Element(usize);

impl dom::TElement for Element {
    fn traversal_parent(self) -> Option<Self> {
        self.0.checked_sub(1).map(Self)
    }

    fn local_name(self) -> LocalName {
        local_name!("div")
    }

    fn namespace(self) -> LocalName {
        local_name!("namespace")
    }

    fn id(self) -> Option<LocalName> {
        None
    }

    fn each_class(self, _: impl FnMut(&LocalName)) {}

    fn each_attr_name(self, _: impl FnMut(&LocalName)) {}
}

fn assert_empty(filter: &selectors::BloomFilter) {
    for slot in 0..4096 {
        assert!(
            !filter.might_contain_hash(slot | (slot << 12)),
            "slot {slot}"
        );
    }
}

#[test]
fn clear_after_recovering_from_a_saturated_ancestor_chain() {
    for depth in [12, 13, 127, 128, 254, 255, 256, 512] {
        // Avoid a second panic in Drop if an assertion detects a dirty filter.
        let mut bloom = std::mem::ManuallyDrop::new(style_bloom::StyleBloom::new());
        bloom.rebuild(Element(depth));
        bloom.insert_parents_recovering(Element(1), 1);
        assert_eq!(bloom.matching_depth(), 1);
        bloom.assert_complete(Element(1));
        bloom.clear();
        assert_empty(bloom.filter());
        unsafe { std::mem::ManuallyDrop::drop(&mut bloom) };
    }
}

#[test]
fn drop_after_recovering_from_a_saturated_ancestor_chain() {
    {
        let mut bloom = style_bloom::StyleBloom::new();
        bloom.rebuild(Element(256));
        bloom.insert_parents_recovering(Element(1), 1);
    }
    let bloom = style_bloom::StyleBloom::<Element>::new();
    assert_empty(bloom.filter());
}

#[derive(Debug)]
struct Node {
    parent: Option<usize>,
    classes: usize,
}

#[derive(Clone, Copy, Debug)]
struct TreeElement<'a> {
    nodes: &'a [Node],
    index: usize,
}

impl PartialEq for TreeElement<'_> {
    fn eq(&self, other: &Self) -> bool {
        std::ptr::eq(self.nodes, other.nodes) && self.index == other.index
    }
}

impl Eq for TreeElement<'_> {}

impl dom::TElement for TreeElement<'_> {
    fn traversal_parent(self) -> Option<Self> {
        self.nodes[self.index]
            .parent
            .map(|index| Self { index, ..self })
    }

    fn local_name(self) -> LocalName {
        let slot = self.index as u32 % 16 + 1;
        LocalName::Hashed(slot | (slot << 12))
    }

    fn namespace(self) -> LocalName {
        LocalName::Hashed(63 | (63 << 12))
    }

    fn id(self) -> Option<LocalName> {
        Some(LocalName::Hashed((self.index as u32 % 16 + 1) << 12))
    }

    fn each_class(self, mut f: impl FnMut(&LocalName)) {
        for _ in 0..self.nodes[self.index].classes {
            f(&LocalName::Hashed(0));
        }
    }

    fn each_attr_name(self, mut f: impl FnMut(&LocalName)) {
        for name in ["class", "id", "style"] {
            f(&LocalName::Named(name));
        }
        let slot = self.index as u32 % 16 + 32;
        f(&LocalName::Hashed(slot | (slot << 12)));
    }
}

fn check_tree_filter(
    bloom: &style_bloom::StyleBloom<TreeElement<'_>>,
    nodes: &[Node],
    mut parent: Option<usize>,
    saturated: &mut [bool; 64],
) {
    assert_eq!(bloom.current_parent().map(|e| e.index), parent);
    let mut counts = [0; 64];
    let mut depth = 0;
    while let Some(index) = parent {
        counts[index % 16 + 1] += 3;
        counts[63] += 2;
        counts[0] += 1 + 2 * nodes[index].classes;
        counts[index % 16 + 32] += 2;
        depth += 1;
        parent = nodes[index].parent;
    }
    assert_eq!(bloom.matching_depth(), depth);
    for slot in 0..64 {
        saturated[slot] |= counts[slot] >= 255;
        let hash = slot as u32 | ((slot as u32) << 12);
        assert_eq!(
            bloom.filter().might_contain_hash(hash),
            counts[slot] != 0 || saturated[slot],
            "slot {slot}, nodes {nodes:?}"
        );
    }
}

fn check_recovery_history(nodes: &[Node], targets: &[usize], pushes: usize) {
    let mut bloom = std::mem::ManuallyDrop::new(style_bloom::StyleBloom::new());
    let mut saturated = [false; 64];
    for (step, &index) in targets.iter().enumerate() {
        let element = TreeElement { nodes, index };
        let mut depth = 0;
        let mut parent = nodes[index].parent;
        while let Some(index) = parent {
            depth += 1;
            parent = nodes[index].parent;
        }
        bloom.insert_parents_recovering(element, depth);
        bloom.assert_complete(element);
        if depth == 0 {
            saturated.fill(false);
        }
        check_tree_filter(&bloom, nodes, nodes[index].parent, &mut saturated);
        if pushes & (1 << step) != 0 {
            bloom.push(element);
            check_tree_filter(&bloom, nodes, Some(index), &mut saturated);
        }
    }
    bloom.clear();
    assert_empty(bloom.filter());
    unsafe { std::mem::ManuallyDrop::drop(&mut bloom) };
    let reused = style_bloom::StyleBloom::<TreeElement<'_>>::new();
    assert_empty(reused.filter());
}

#[test]
fn exhaustive_small_tree_recovery() {
    fn enumerate(nodes: &mut Vec<Node>, trees: &mut usize, histories: &mut usize) {
        if nodes.len() != 5 {
            let parents = std::iter::once(None).chain((0..nodes.len()).map(Some));
            for parent in parents {
                if !cfg!(feature = "gecko") && !nodes.is_empty() && parent.is_none() {
                    continue;
                }
                nodes.push(Node {
                    parent,
                    classes: nodes.len() % 3,
                });
                enumerate(nodes, trees, histories);
                nodes.pop();
            }
            return;
        }
        *trees += 1;
        for first in 0..nodes.len() {
            for second in 0..nodes.len() {
                for third in 0..nodes.len() {
                    for pushes in 0..4 {
                        let targets = [first, second, third];
                        let result = std::panic::catch_unwind(|| {
                            check_recovery_history(nodes, &targets, pushes);
                        });
                        assert!(
                            result.is_ok(),
                            "targets {targets:?}, pushes {pushes}, nodes {nodes:?}"
                        );
                        *histories += 1;
                    }
                }
            }
        }
    }
    let mut trees = 0;
    let mut histories = 0;
    enumerate(&mut Vec::new(), &mut trees, &mut histories);
    assert_eq!(trees, if cfg!(feature = "gecko") { 120 } else { 24 });
    assert_eq!(histories, trees * 500);
}

#[test]
fn saturated_branch_recovery_histories() {
    for classes in [12, 13, 126, 127, 128, 254, 255, 256] {
        let mut nodes: Vec<_> = (0usize..260)
            .map(|i| Node {
                parent: i.checked_sub(1),
                classes: 0,
            })
            .collect();
        nodes[1].classes = classes;
        nodes.push(Node {
            parent: Some(0),
            classes: 0,
        });
        nodes.push(Node {
            parent: Some(260),
            classes: 0,
        });
        for targets in [
            [259, 261, 2, 0, 259, 1],
            [2, 261, 259, 1, 2, 261],
            [261, 259, 261, 2, 259, 261],
        ] {
            for pushes in 0..64 {
                check_recovery_history(&nodes, &targets, pushes);
            }
        }
    }
}
