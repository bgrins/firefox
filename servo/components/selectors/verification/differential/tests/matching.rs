/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use cssparser::ToCss;
use precomputed_hash::PrecomputedHash;
use selectors::attr::{AttrSelectorOperation, CaseSensitivity, NamespaceConstraint};
use selectors::bloom::BloomFilter;
use selectors::context::{
    MatchingContext, MatchingForInvalidation, MatchingMode, NeedsSelectorFlags, QuirksMode,
    SelectorCaches,
};
use selectors::matching::{ElementSelectorFlags, matches_selector};
use selectors::parser::{AncestorHashes, ParseRelative, SelectorList, SelectorParseErrorKind};
use selectors::{Element, OpaqueElement, SelectorImpl};
use std::cell::Cell;
use std::fmt;

#[derive(Clone, Debug, Default, Eq, PartialEq)]
struct Atom(String);
impl From<&str> for Atom {
    fn from(value: &str) -> Self {
        Self(value.into())
    }
}
impl AsRef<str> for Atom {
    fn as_ref(&self) -> &str {
        &self.0
    }
}
impl ToCss for Atom {
    fn to_css<W: fmt::Write>(&self, dest: &mut W) -> fmt::Result {
        cssparser::serialize_identifier(&self.0, dest)
    }
}
impl PrecomputedHash for Atom {
    fn precomputed_hash(&self) -> u32 {
        self.0.bytes().fold(2166136261, |hash, byte| {
            (hash ^ u32::from(byte)).wrapping_mul(16777619)
        })
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Never {}
impl ToCss for Never {
    fn to_css<W: fmt::Write>(&self, _: &mut W) -> fmt::Result {
        match *self {}
    }
}
impl selectors::parser::PseudoElement for Never {}
impl selectors::parser::NonTSPseudoClass for Never {
    fn is_active_or_hover(&self) -> bool {
        match *self {}
    }
    fn is_user_action_state(&self) -> bool {
        match *self {}
    }
}

#[derive(Clone, Debug)]
struct Impl;
impl SelectorImpl for Impl {
    type ExtraMatchingData<'a> = ();
    type AttrValue = Atom;
    type Identifier = Atom;
    type LocalName = Atom;
    type NamespaceUrl = Atom;
    type NamespacePrefix = Atom;
    type BorrowedLocalName = Atom;
    type BorrowedNamespaceUrl = Atom;
    type NonTSPseudoClass = Never;
    type PseudoElement = Never;
    fn should_collect_attr_hash(name: &Atom) -> bool {
        !matches!(name.0.as_str(), "class" | "id" | "style")
    }
}
struct Parser;
impl<'i> selectors::Parser<'i> for Parser {
    type Impl = Impl;
    type Error = SelectorParseErrorKind;
    fn parse_is_and_where(&self) -> bool {
        true
    }
    fn parse_has(&self) -> bool {
        true
    }
    fn parse_nth_child_of(&self) -> bool {
        true
    }
    fn namespace_for_prefix(&self, prefix: &Atom) -> Option<Atom> {
        match prefix.0.as_str() {
            "svg" => Some(Atom::from("urn:svg")),
            "html" => Some(Atom::from("urn:html")),
            _ => None,
        }
    }
}

#[derive(Clone, Debug)]
struct Node {
    parent: Option<usize>,
    name: Atom,
    namespace: Atom,
    id: Atom,
    classes: Vec<Atom>,
    attrs: Vec<(Atom, Atom, Atom)>,
}
#[derive(Debug)]
struct Tree {
    nodes: Vec<Node>,
    html_document: bool,
    provide_hashes: Cell<bool>,
    unavailable: Cell<Option<usize>>,
    hash_calls: Cell<usize>,
    class_checks: Cell<usize>,
}
#[derive(Clone, Copy, Debug)]
struct El<'a> {
    tree: &'a Tree,
    index: usize,
}
impl El<'_> {
    fn node(&self) -> &Node {
        &self.tree.nodes[self.index]
    }
    fn at(&self, index: usize) -> Self {
        Self { index, ..*self }
    }
    fn add_hashes(&self, filter: &mut BloomFilter) {
        let node = self.node();
        for name in [&node.name, &node.namespace, &node.id]
            .into_iter()
            .chain(node.classes.iter())
        {
            filter.insert_hash(name.precomputed_hash());
        }
        for (_, name, _) in &node.attrs {
            if Impl::should_collect_attr_hash(name) {
                filter.insert_hash(name.precomputed_hash());
            }
        }
    }
}
impl Element for El<'_> {
    type Impl = Impl;
    fn opaque(&self) -> OpaqueElement {
        OpaqueElement::new(self.node())
    }
    fn parent_element(&self) -> Option<Self> {
        self.node().parent.map(|i| self.at(i))
    }
    fn parent_node_is_shadow_root(&self) -> bool {
        false
    }
    fn containing_shadow_host(&self) -> Option<Self> {
        None
    }
    fn is_pseudo_element(&self) -> bool {
        false
    }
    fn prev_sibling_element(&self) -> Option<Self> {
        self.node().parent?;
        (0..self.index)
            .rev()
            .find(|&i| self.tree.nodes[i].parent == self.node().parent)
            .map(|i| self.at(i))
    }
    fn next_sibling_element(&self) -> Option<Self> {
        self.node().parent?;
        (self.index + 1..self.tree.nodes.len())
            .find(|&i| self.tree.nodes[i].parent == self.node().parent)
            .map(|i| self.at(i))
    }
    fn first_element_child(&self) -> Option<Self> {
        self.tree
            .nodes
            .iter()
            .position(|n| n.parent == Some(self.index))
            .map(|i| self.at(i))
    }
    fn is_html_element_in_html_document(&self) -> bool {
        self.tree.html_document && self.node().namespace.0 == "urn:html"
    }
    fn has_local_name(&self, name: &Atom) -> bool {
        self.node().name == *name
    }
    fn has_namespace(&self, namespace: &Atom) -> bool {
        self.node().namespace == *namespace
    }
    fn is_same_type(&self, other: &Self) -> bool {
        self.node().name == other.node().name && self.node().namespace == other.node().namespace
    }
    fn attr_matches(
        &self,
        namespace: &NamespaceConstraint<&Atom>,
        name: &Atom,
        operation: &AttrSelectorOperation<&Atom>,
    ) -> bool {
        self.node().attrs.iter().any(|(ns, n, value)| {
            let ns_matches = match namespace {
                NamespaceConstraint::Any => true,
                NamespaceConstraint::Specific(expected) => ns == *expected,
            };
            ns_matches && n == name && operation.eval_str(&value.0)
        })
    }
    fn match_non_ts_pseudo_class(&self, pc: &Never, _: &mut MatchingContext<Impl>) -> bool {
        match *pc {}
    }
    fn match_pseudo_element(&self, pe: &Never, _: &mut MatchingContext<Impl>) -> bool {
        match *pe {}
    }
    fn apply_selector_flags(&self, _: ElementSelectorFlags) {}
    fn is_link(&self) -> bool {
        false
    }
    fn is_html_slot_element(&self) -> bool {
        false
    }
    fn has_id(&self, id: &Atom, sensitivity: CaseSensitivity) -> bool {
        sensitivity.eq(self.node().id.0.as_bytes(), id.0.as_bytes())
    }
    fn has_class(&self, name: &Atom, sensitivity: CaseSensitivity) -> bool {
        self.tree.class_checks.set(self.tree.class_checks.get() + 1);
        self.node()
            .classes
            .iter()
            .any(|class| sensitivity.eq(class.0.as_bytes(), name.0.as_bytes()))
    }
    fn has_custom_state(&self, _: &Atom) -> bool {
        false
    }
    fn imported_part(&self, _: &Atom) -> Option<Atom> {
        None
    }
    fn is_part(&self, _: &Atom) -> bool {
        false
    }
    fn is_empty(&self) -> bool {
        self.first_element_child().is_none()
    }
    fn is_root(&self) -> bool {
        self.node().parent.is_none()
    }
    fn add_element_unique_hashes(&self, filter: &mut BloomFilter) -> bool {
        self.tree.hash_calls.set(self.tree.hash_calls.get() + 1);
        if !self.tree.provide_hashes.get() || self.tree.unavailable.get() == Some(self.index) {
            return false;
        }
        self.add_hashes(filter);
        true
    }
}

fn parse(css: &str) -> SelectorList<Impl> {
    SelectorList::parse(&Parser, &mut cssparser::Parser::new(css), ParseRelative::No)
        .unwrap_or_else(|err| panic!("{css}: {err:?}"))
}
fn matches(
    list: &SelectorList<Impl>,
    element: El<'_>,
    quirks: QuirksMode,
    ancestor: bool,
    caches: &mut SelectorCaches,
) -> bool {
    let mut filter = BloomFilter::new();
    let mut parent = element.parent_element();
    while let Some(el) = parent {
        el.add_hashes(&mut filter);
        parent = el.parent_element();
    }
    let mut context = MatchingContext::new(
        MatchingMode::Normal,
        ancestor.then_some(&filter),
        caches,
        quirks,
        NeedsSelectorFlags::No,
        MatchingForInvalidation::No,
    );
    list.slice().iter().any(|selector| {
        let hashes = AncestorHashes::new(selector, quirks);
        matches_selector(
            selector,
            0,
            ancestor.then_some(&hashes),
            element,
            &mut context,
        )
    })
}

fn make_tree(parents: &[Option<usize>], variant: usize) -> Tree {
    let nodes = parents
        .iter()
        .enumerate()
        .map(|(i, &parent)| {
            let label = ["a", "b", "c", "A"][(i + variant) % 4];
            let (name, ns) = match (i + variant) % 4 {
                0 => ("div", "urn:html"),
                1 => ("g", "urn:svg"),
                2 => ("DIV", ""),
                _ => ("div", ""),
            };
            Node {
                parent,
                name: Atom::from(name),
                namespace: Atom::from(ns),
                id: Atom::from(label),
                classes: vec![Atom::from(label)],
                attrs: vec![
                    (Atom::default(), Atom::from("data-x"), Atom::from(label)),
                    (Atom::from("urn:svg"), Atom::from("data-y"), Atom::from("A")),
                    (Atom::default(), Atom::from("class"), Atom::from(label)),
                    (Atom::default(), Atom::from("id"), Atom::from(label)),
                ],
            }
        })
        .collect();
    Tree {
        nodes,
        html_document: variant % 2 == 0,
        provide_hashes: Cell::new(false),
        unavailable: Cell::new(None),
        hash_calls: Cell::new(0),
        class_checks: Cell::new(0),
    }
}

fn selectors() -> Vec<(String, SelectorList<Impl>)> {
    let mut css = std::collections::BTreeSet::new();
    let atoms = [
        "*",
        "div",
        "DIV",
        "svg|g",
        "*|g",
        "|div",
        ".a",
        ".A",
        ".b",
        "#a",
        "#A",
        "[data-x]",
        "[DATA-X]",
        "[data-x=A i]",
        "[svg|data-y]",
        "[class]",
        "[id]",
        ":not(.a)",
        ":is(.a, .b)",
        ":where(.a)",
    ];
    for atom in atoms {
        css.insert(atom.to_owned());
        for left in [".a", ".b", "div", "[data-x]"] {
            for combinator in [" ", " > ", " + ", " ~ "] {
                let pair = format!("{left}{combinator}{atom}");
                for selector in [
                    pair.clone(),
                    format!(":is({pair})"),
                    format!(":where({pair}) .c"),
                    format!(":has({pair})"),
                    format!(":has(+ {pair})"),
                    format!(":has(~ {pair})"),
                    format!(":has(:is({pair}))"),
                    format!(":has(:is({pair}) .c)"),
                ] {
                    css.insert(selector);
                }
            }
        }
        for prefix in ["", "> ", "+ ", "~ "] {
            css.insert(format!(":has({prefix}{atom})"));
        }
    }
    for selector in [
        ":has(.a):has(.b)",
        ":has(:where(.a .b) .c)",
        ":has(:is(.a, .b) .c)",
        ":is(.a .b, .c) > div",
        ":where(:is(.a .b)) .c",
        ".a.b#c[data-x][svg|data-y] div",
        ":not(:has(.a))",
        ":nth-child(2 of .a, .b)",
    ] {
        css.insert(selector.into());
    }
    css.into_iter()
        .map(|css| {
            let parsed = parse(&css);
            (css, parsed)
        })
        .collect()
}

#[test]
fn generated_matching_agrees_with_filters_disabled() {
    let selectors = selectors();
    fn enumerate(
        parents: &mut Vec<Option<usize>>,
        selectors: &[(String, SelectorList<Impl>)],
        checks: &mut usize,
    ) {
        if parents.len() < 4 {
            for parent in std::iter::once(None).chain((0..parents.len()).map(Some)) {
                parents.push(parent);
                enumerate(parents, selectors, checks);
                parents.pop();
            }
            return;
        }
        for variant in 0..4 {
            let tree = make_tree(parents, variant);
            for quirks in [
                QuirksMode::NoQuirks,
                QuirksMode::LimitedQuirks,
                QuirksMode::Quirks,
            ] {
                for (css, parsed) in selectors {
                    for index in 0..tree.nodes.len() {
                        let el = El { tree: &tree, index };
                        tree.provide_hashes.set(false);
                        let expected =
                            matches(parsed, el, quirks, false, &mut SelectorCaches::default());
                        for (ancestor, relative) in [(true, false), (false, true), (true, true)] {
                            tree.provide_hashes.set(relative);
                            let mut caches = SelectorCaches::default();
                            for pass in 0..3 {
                                caches.relative_selector = Default::default();
                                assert_eq!(
                                    matches(parsed, el, quirks, ancestor, &mut caches),
                                    expected,
                                    "selector={css}, parents={parents:?}, variant={variant}, element={index}, quirks={quirks:?}, ancestor={ancestor}, relative={relative}, pass={pass}"
                                );
                                *checks += 1;
                            }
                        }
                    }
                }
            }
        }
    }
    let mut checks = 0;
    enumerate(&mut Vec::new(), &selectors, &mut checks);
    eprintln!(
        "{} selectors; {checks} differential comparisons",
        selectors.len()
    );
}

#[test]
fn repeated_has_lookups_build_reuse_and_reject() {
    let tree = make_tree(&[None, Some(0), Some(0)], 0);
    let el = El {
        tree: &tree,
        index: 0,
    };
    let parsed = parse(":has(.missing)");
    let mut caches = SelectorCaches::default();
    tree.provide_hashes.set(true);
    assert!(!matches(
        &parsed,
        el,
        QuirksMode::NoQuirks,
        false,
        &mut caches
    ));
    assert_eq!(tree.hash_calls.get(), 0);
    assert!(tree.class_checks.get() > 0);
    for pass in 0..2 {
        caches.relative_selector = Default::default();
        tree.class_checks.set(0);
        assert!(!matches(
            &parsed,
            el,
            QuirksMode::NoQuirks,
            false,
            &mut caches
        ));
        assert_eq!(tree.hash_calls.get(), 2, "pass {pass}");
        assert_eq!(tree.class_checks.get(), 0, "pass {pass}");
    }
}

#[test]
fn shared_filters_agree_across_selectors_and_retry_incomplete_builds() {
    let tree = make_tree(
        &[None, Some(0), Some(1), Some(0), Some(3), Some(4), Some(0)],
        0,
    );
    let selectors: Vec<_> = [
        ":has(> .a)",
        ":has(.a)",
        ":has(+ .b)",
        ":has(~ .b .c)",
        ":has(+ .b > .c)",
        ":has(:is(.a .b))",
        ":has(:is(.a .b) .c)",
        ":not(:has(.missing))",
        ":has([data-x])",
        ":has([svg|data-y])",
    ]
    .into_iter()
    .map(|css| (css, parse(css)))
    .collect();
    for quirks in [QuirksMode::NoQuirks, QuirksMode::Quirks] {
        let mut caches = SelectorCaches::default();
        for unavailable in [Some(2), None, None] {
            tree.unavailable.set(unavailable);
            for (css, parsed) in &selectors {
                for index in (0..tree.nodes.len()).rev() {
                    let el = El { tree: &tree, index };
                    tree.provide_hashes.set(false);
                    let expected =
                        matches(parsed, el, quirks, false, &mut SelectorCaches::default());
                    tree.provide_hashes.set(true);
                    caches.relative_selector = Default::default();
                    assert_eq!(
                        matches(parsed, el, quirks, true, &mut caches),
                        expected,
                        "{css}, {index}, {quirks:?}, unavailable={unavailable:?}"
                    );
                }
            }
        }
    }
}
