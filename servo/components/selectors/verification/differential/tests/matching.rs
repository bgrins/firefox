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

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
enum HashProfile {
    #[default]
    Normal,
    Colliding,
    ZeroLowBits,
    MixedZeroLowBits,
    SharedLowBits,
}

thread_local! {
    static HASH_PROFILE: Cell<HashProfile> = const { Cell::new(HashProfile::Normal) };
    static OMIT_CLASS_HASHES: Cell<bool> = const { Cell::new(false) };
}

fn with_profile<T>(profile: HashProfile, f: impl FnOnce() -> T) -> T {
    struct Reset(HashProfile);
    impl Drop for Reset {
        fn drop(&mut self) {
            HASH_PROFILE.set(self.0);
        }
    }
    let _reset = Reset(HASH_PROFILE.replace(profile));
    f()
}

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
        let hash = self.0.bytes().fold(2166136261, |hash, byte| {
            (hash ^ u32::from(byte)).wrapping_mul(16777619)
        });
        match HASH_PROFILE.get() {
            HashProfile::Normal => hash,
            HashProfile::Colliding => 0x123456,
            HashProfile::ZeroLowBits => hash << 24,
            HashProfile::MixedZeroLowBits => {
                if hash & 1 == 0 {
                    hash << 24
                } else {
                    hash
                }
            },
            HashProfile::SharedLowBits => (hash << 24) | 0x123456,
        }
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
impl Node {
    fn sync_class_attr(&mut self) {
        let value = self
            .classes
            .iter()
            .map(|class| class.0.as_str())
            .collect::<Vec<_>>()
            .join(" ");
        for (namespace, name, attr) in &mut self.attrs {
            if namespace.0.is_empty() && name.0 == "class" {
                *attr = Atom::from(value.as_str());
            }
        }
    }

    fn clear_id(&mut self) {
        self.id = Atom::default();
        for (namespace, name, value) in &mut self.attrs {
            if namespace.0.is_empty() && name.0 == "id" {
                *value = Atom::default();
            }
        }
    }

    fn remove_attr(&mut self, index: usize) {
        let (namespace, name, _) = self.attrs.remove(index);
        if namespace.0.is_empty() {
            match name.0.as_str() {
                "class" => self.classes.clear(),
                "id" => self.id = Atom::default(),
                _ => {},
            }
        }
    }
}
#[derive(Debug)]
struct Tree {
    nodes: Vec<Node>,
    html_document: bool,
    provide_hashes: Cell<bool>,
    unavailable: Cell<Option<usize>>,
    hash_calls: Cell<usize>,
    successful_hash_calls: Cell<usize>,
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
        for name in [&node.name, &node.namespace] {
            filter.insert_hash(name.precomputed_hash());
        }
        if !node.id.0.is_empty() {
            filter.insert_hash(node.id.precomputed_hash());
        }
        if !OMIT_CLASS_HASHES.get() {
            for name in &node.classes {
                filter.insert_hash(name.precomputed_hash());
            }
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
        self.tree
            .successful_hash_calls
            .set(self.tree.successful_hash_calls.get() + 1);
        true
    }
}

fn parse(css: &str) -> SelectorList<Impl> {
    SelectorList::parse(&Parser, &mut cssparser::Parser::new(css), ParseRelative::No)
        .unwrap_or_else(|err| panic!("{css}: {err:?}"))
}

#[derive(Clone, Debug)]
struct Probe {
    css: String,
    index: usize,
    unavailable: Option<usize>,
}

#[derive(Clone, Debug)]
struct Case {
    css: String,
    nodes: Vec<Node>,
    html_document: bool,
    index: usize,
    quirks: QuirksMode,
    ancestor: bool,
    relative: bool,
    pass: usize,
    profile: HashProfile,
    history: Vec<Probe>,
    unavailable: Option<usize>,
}

impl Case {
    fn disagrees(&self) -> bool {
        with_profile(self.profile, || {
            let Ok(parsed) = SelectorList::parse(
                &Parser,
                &mut cssparser::Parser::new(&self.css),
                ParseRelative::No,
            ) else {
                return false;
            };
            let mut tree = make_tree(&[], 0);
            tree.nodes = self.nodes.clone();
            tree.html_document = self.html_document;
            let el = El {
                tree: &tree,
                index: self.index,
            };
            let expected = matches(
                &parsed,
                el,
                self.quirks,
                false,
                &mut SelectorCaches::default(),
            );
            tree.provide_hashes.set(self.relative);
            let mut caches = SelectorCaches::default();
            for probe in &self.history {
                tree.unavailable.set(probe.unavailable);
                caches.relative_selector = Default::default();
                matches(
                    &parse(&probe.css),
                    El {
                        tree: &tree,
                        index: probe.index,
                    },
                    self.quirks,
                    self.ancestor,
                    &mut caches,
                );
            }
            tree.unavailable.set(self.unavailable);
            let mut actual = expected;
            for _ in 0..=self.pass {
                caches.relative_selector = Default::default();
                actual = matches(&parsed, el, self.quirks, self.ancestor, &mut caches);
            }
            actual != expected
        })
    }

    fn without_node(&self, index: usize) -> Self {
        let mut reduced = self.clone();
        let parent = reduced.nodes[index].parent;
        reduced.nodes.remove(index);
        for node in &mut reduced.nodes {
            if node.parent == Some(index) {
                node.parent = parent;
            }
            node.parent = node.parent.map(|p| if p > index { p - 1 } else { p });
        }
        if reduced.index > index {
            reduced.index -= 1;
        }
        let remap = |i: usize| if i > index { i - 1 } else { i };
        reduced.unavailable = reduced.unavailable.filter(|&i| i != index).map(remap);
        reduced.history.retain(|probe| probe.index != index);
        for probe in &mut reduced.history {
            probe.index = remap(probe.index);
            probe.unavailable = probe.unavailable.filter(|&i| i != index).map(remap);
        }
        reduced
    }

    fn shrink(mut self) -> Self {
        assert!(self.disagrees());
        loop {
            let mut candidates = Vec::new();
            for i in 0..self.history.len() {
                let mut candidate = self.clone();
                candidate.history.remove(i);
                candidates.push(candidate);
            }
            for i in 0..self.nodes.len() {
                if i != self.index {
                    candidates.push(self.without_node(i));
                }
                for class in 0..self.nodes[i].classes.len() {
                    let mut candidate = self.clone();
                    candidate.nodes[i].classes.remove(class);
                    candidate.nodes[i].sync_class_attr();
                    candidates.push(candidate);
                }
                for attr in 0..self.nodes[i].attrs.len() {
                    let mut candidate = self.clone();
                    candidate.nodes[i].remove_attr(attr);
                    candidates.push(candidate);
                }
                for field in 0..5 {
                    let mut candidate = self.clone();
                    let node = &mut candidate.nodes[i];
                    let changed = match field {
                        0 => {
                            !node.classes.is_empty() && {
                                node.classes.clear();
                                node.sync_class_attr();
                                true
                            }
                        },
                        1 => {
                            !node.attrs.is_empty() && {
                                node.attrs.clear();
                                node.classes.clear();
                                node.id = Atom::default();
                                true
                            }
                        },
                        2 => {
                            !node.id.0.is_empty() && {
                                node.clear_id();
                                true
                            }
                        },
                        3 => {
                            node.name.0 != "x" && {
                                node.name = Atom::from("x");
                                true
                            }
                        },
                        _ => {
                            !node.namespace.0.is_empty() && {
                                node.namespace = Atom::default();
                                true
                            }
                        },
                    };
                    if changed {
                        candidates.push(candidate);
                    }
                }
            }
            let boundaries: Vec<_> = self
                .css
                .char_indices()
                .map(|(i, _)| i)
                .chain(std::iter::once(self.css.len()))
                .collect();
            for width in (1..boundaries.len()).rev() {
                for start in 0..boundaries.len() - width {
                    let mut candidate = self.clone();
                    candidate
                        .css
                        .replace_range(boundaries[start]..boundaries[start + width], "");
                    candidates.push(candidate);
                }
            }
            if let Some(reduced) = candidates.into_iter().find(Self::disagrees) {
                self = reduced;
            } else {
                return self;
            }
        }
    }

    fn assert_consistent_attributes(&self) {
        for node in &self.nodes {
            let attr = |name| {
                node.attrs
                    .iter()
                    .find(|(namespace, local, _)| namespace.0.is_empty() && local.0 == name)
                    .map_or("", |(_, _, value)| value.0.as_str())
            };
            assert_eq!(node.id.0, attr("id"));
            let classes: Vec<_> = node.classes.iter().map(|class| class.0.as_str()).collect();
            assert_eq!(
                classes,
                attr("class").split_ascii_whitespace().collect::<Vec<_>>()
            );
        }
    }
}

fn check_case(case: Case, actual: bool, expected: bool) {
    if actual != expected {
        let reduced = case.clone().shrink();
        panic!("filter mismatch\noriginal: {case:#?}\nreduced: {reduced:#?}");
    }
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
        successful_hash_calls: Cell::new(0),
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
                                let actual = matches(parsed, el, quirks, ancestor, &mut caches);
                                if actual != expected {
                                    check_case(
                                        Case {
                                            css: css.clone(),
                                            nodes: tree.nodes.clone(),
                                            html_document: tree.html_document,
                                            index,
                                            quirks,
                                            ancestor,
                                            relative,
                                            pass,
                                            profile: HashProfile::Normal,
                                            history: Vec::new(),
                                            unavailable: None,
                                        },
                                        actual,
                                        expected,
                                    );
                                }
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
        let mut history = Vec::new();
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
                    let actual = matches(parsed, el, quirks, true, &mut caches);
                    if actual != expected {
                        check_case(
                            Case {
                                css: (*css).into(),
                                nodes: tree.nodes.clone(),
                                html_document: tree.html_document,
                                index,
                                quirks,
                                ancestor: true,
                                relative: true,
                                pass: 0,
                                profile: HashProfile::Normal,
                                history: history.clone(),
                                unavailable,
                            },
                            actual,
                            expected,
                        );
                    }
                    history.push(Probe {
                        css: (*css).into(),
                        index,
                        unavailable,
                    });
                }
            }
        }
    }
}

#[test]
fn adversarial_hashes_and_deep_selectors() {
    let mut corpus = selectors();
    for depth in [4, 8, 16] {
        let chain = std::iter::repeat_n("[data-x]", depth)
            .collect::<Vec<_>>()
            .join(" > ");
        for css in [
            format!("{chain} .a"),
            format!(":has({chain})"),
            format!(":has(> :is(:where({chain}), .missing))"),
            format!(":is(:where(:is({chain}))) .b"),
        ] {
            corpus.push((css.clone(), parse(&css)));
        }
    }
    let forests = [
        (0usize..24).map(|i| i.checked_sub(1)).collect::<Vec<_>>(),
        (0..24)
            .map(|i| if i == 0 { None } else { Some((i - 1) / 2) })
            .collect(),
        (0..24)
            .map(|i| if i % 8 == 0 { None } else { Some(i - 1) })
            .collect(),
    ];
    let mut comparisons = 0;
    for profile in [
        HashProfile::Normal,
        HashProfile::Colliding,
        HashProfile::ZeroLowBits,
        HashProfile::MixedZeroLowBits,
        HashProfile::SharedLowBits,
    ] {
        with_profile(profile, || {
            for parents in &forests {
                for variant in 0..2 {
                    let tree = make_tree(parents, variant);
                    for quirks in [QuirksMode::NoQuirks, QuirksMode::Quirks] {
                        for (css, parsed) in &corpus {
                            for index in [0, 7, 15, 23] {
                                let el = El { tree: &tree, index };
                                tree.provide_hashes.set(false);
                                let expected = matches(
                                    parsed,
                                    el,
                                    quirks,
                                    false,
                                    &mut SelectorCaches::default(),
                                );
                                for (ancestor, relative) in
                                    [(true, false), (false, true), (true, true)]
                                {
                                    tree.provide_hashes.set(relative);
                                    let mut caches = SelectorCaches::default();
                                    for pass in 0..3 {
                                        caches.relative_selector = Default::default();
                                        let actual =
                                            matches(parsed, el, quirks, ancestor, &mut caches);
                                        if actual != expected {
                                            check_case(
                                                Case {
                                                    css: css.clone(),
                                                    nodes: tree.nodes.clone(),
                                                    html_document: tree.html_document,
                                                    index,
                                                    quirks,
                                                    ancestor,
                                                    relative,
                                                    pass,
                                                    profile,
                                                    history: Vec::new(),
                                                    unavailable: None,
                                                },
                                                actual,
                                                expected,
                                            );
                                        }
                                        comparisons += 1;
                                    }
                                }
                            }
                        }
                    }
                    assert!(
                        tree.successful_hash_calls.get() > 0,
                        "relative filter construction: {profile:?}"
                    );
                }
            }
        });
    }
    eprintln!("{comparisons} deep/adversarial differential comparisons");
}

#[test]
fn shrinker_preserves_an_injected_false_negative() {
    struct Reset;
    impl Drop for Reset {
        fn drop(&mut self) {
            OMIT_CLASS_HASHES.set(false);
        }
    }
    let _reset = Reset;
    let mut tree = make_tree(&[None, Some(0), Some(1), Some(2), Some(0)], 0);
    tree.nodes[1].classes.push(Atom::from("needle"));
    tree.nodes[1].sync_class_attr();
    let case = Case {
        css: ":is(.needle[data-x]) > [data-x] > .A".into(),
        nodes: tree.nodes,
        html_document: true,
        index: 3,
        quirks: QuirksMode::NoQuirks,
        ancestor: true,
        relative: false,
        pass: 0,
        profile: HashProfile::Normal,
        history: Vec::new(),
        unavailable: None,
    };
    assert!(!case.disagrees());
    OMIT_CLASS_HASHES.set(true);
    assert!(case.disagrees());
    let reduced = case.clone().shrink();
    reduced.assert_consistent_attributes();
    assert!(reduced.disagrees());
    assert!(reduced.nodes.len() < case.nodes.len());
    assert!(reduced.css.len() < case.css.len());
    assert!(
        reduced.nodes.iter().map(|n| n.attrs.len()).sum::<usize>()
            < case.nodes.iter().map(|n| n.attrs.len()).sum::<usize>()
    );
    for i in 0..reduced.nodes.len() {
        if i != reduced.index {
            assert!(!reduced.without_node(i).disagrees());
        }
    }
    OMIT_CLASS_HASHES.set(false);
    assert!(!reduced.disagrees());
    eprintln!("injected failure reduced to: {reduced:#?}");
}

#[test]
fn ancestor_filter_rejects_before_element_matching() {
    let tree = make_tree(&[None, Some(0)], 0);
    let parsed = parse(".missing .also-missing");
    let el = El {
        tree: &tree,
        index: 1,
    };
    assert!(!matches(
        &parsed,
        el,
        QuirksMode::NoQuirks,
        false,
        &mut SelectorCaches::default()
    ));
    assert!(tree.class_checks.get() > 0);
    tree.class_checks.set(0);
    assert!(!matches(
        &parsed,
        el,
        QuirksMode::NoQuirks,
        true,
        &mut SelectorCaches::default()
    ));
    assert_eq!(tree.class_checks.get(), 0);
}

#[test]
fn adversarial_hash_profiles_have_the_intended_collisions() {
    let hashes = |profile| {
        with_profile(profile, || {
            [
                Atom::from("a").precomputed_hash(),
                Atom::from("b").precomputed_hash(),
            ]
        })
    };
    let colliding = hashes(HashProfile::Colliding);
    assert_eq!(colliding[0], colliding[1]);
    let zero = hashes(HashProfile::ZeroLowBits);
    assert_ne!(zero[0], zero[1]);
    assert!(zero.iter().all(|h| h & 0xffffff == 0));
    let mixed = hashes(HashProfile::MixedZeroLowBits);
    assert_eq!(mixed[0] & 0xffffff, 0);
    assert_ne!(mixed[1] & 0xffffff, 0);
    let shared = hashes(HashProfile::SharedLowBits);
    assert_ne!(shared[0], shared[1]);
    assert_eq!(shared[0] & 0xffffff, shared[1] & 0xffffff);
    assert_ne!(shared[0] & 0xffffff, 0);
}

#[test]
fn shrinker_preserves_cache_warmup_for_an_injected_relative_failure() {
    struct Reset;
    impl Drop for Reset {
        fn drop(&mut self) {
            OMIT_CLASS_HASHES.set(false);
        }
    }
    let _reset = Reset;
    let mut tree = make_tree(&[None, Some(0), Some(0), Some(2)], 0);
    tree.nodes[3].classes.push(Atom::from("needle"));
    tree.nodes[3].sync_class_attr();
    let case = Case {
        css: ":has(:is(.needle))".into(),
        nodes: tree.nodes,
        html_document: true,
        index: 0,
        quirks: QuirksMode::NoQuirks,
        ancestor: false,
        relative: true,
        pass: 0,
        profile: HashProfile::Normal,
        history: vec![
            Probe {
                css: ".unused".into(),
                index: 1,
                unavailable: None,
            },
            Probe {
                css: ":has(.missing)".into(),
                index: 0,
                unavailable: None,
            },
        ],
        unavailable: None,
    };
    assert!(!case.disagrees());
    OMIT_CLASS_HASHES.set(true);
    assert!(case.disagrees());
    let reduced = case.clone().shrink();
    reduced.assert_consistent_attributes();
    assert!(reduced.disagrees());
    assert_eq!(reduced.history.len(), 1);
    assert_eq!(reduced.nodes.len(), 2);
    let mut no_warmup = reduced.clone();
    no_warmup.history.clear();
    assert!(!no_warmup.disagrees());
    OMIT_CLASS_HASHES.set(false);
    assert!(!reduced.disagrees());
    eprintln!("injected relative failure reduced to: {reduced:#?}");
}
