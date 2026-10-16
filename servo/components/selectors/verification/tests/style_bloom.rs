/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

extern crate stylo_bloom_verification as selectors;

#[derive(Clone, Copy, PartialEq)]
pub struct LocalName(&'static str);

macro_rules! local_name {
    ($name:literal) => {
        crate::LocalName($name)
    };
}

#[path = "../../../style/bloom.rs"]
#[allow(unexpected_cfgs)]
mod style_bloom;

impl style_bloom::AtomExt for LocalName {
    fn get_hash32(&self) -> u32 {
        match self.0 {
            "div" => 0x001002,
            "namespace" => 0x003004,
            _ => unreachable!(),
        }
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
#[ignore = "opt-in regression reproducer"]
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
#[ignore = "opt-in regression reproducer"]
fn drop_after_recovering_from_a_saturated_ancestor_chain() {
    {
        let mut bloom = style_bloom::StyleBloom::new();
        bloom.rebuild(Element(256));
        bloom.insert_parents_recovering(Element(1), 1);
    }
    let bloom = style_bloom::StyleBloom::<Element>::new();
    assert_empty(bloom.filter());
}
