#![allow(dead_code)]
use std::sync::Arc;
type Name = String;
type Namespace = String;
type UrlExtraData = String;
type VariableValue = String;
type ComputedRegisteredValue = u8;
#[derive(Clone, Debug, Eq, PartialEq)]
enum PropertyId { Custom(Name), NonCustom(u8) }
#[derive(Clone, Copy)]
enum PropertyIdRef<'a> { Custom(&'a Name), NonCustom(u8) }
impl<'a> From<&'a PropertyId> for PropertyIdRef<'a> {
    fn from(value: &'a PropertyId) -> Self {
        match value { PropertyId::Custom(name) => Self::Custom(name), PropertyId::NonCustom(id) => Self::NonCustom(*id) }
    }
}
#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct AttrInvocation {
    owner: usize,
    occurrence: usize,
    ancestors: Vec<usize>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct AttrUseKey {
    pub name: Name,
    pub namespace: Namespace,
    pub property: Option<PropertyId>,
    pub suppress_animation_taint_sink: bool,
    pub url_data: UrlExtraData,
    pub guard_identity: usize,
    invocation: Option<AttrInvocation>,
}

impl AttrUseKey {
    pub fn new(
        name: &Name,
        namespace: &Namespace,
        property: Option<PropertyIdRef>,
        suppress_animation_taint_sink: bool,
        url_data: &UrlExtraData,
        guard_identity: usize,
    ) -> Self {
        Self {
            name: name.clone(),
            namespace: namespace.clone(),
            property: property.map(|property| match property {
                PropertyIdRef::Custom(name) => PropertyId::Custom(name.clone()),
                PropertyIdRef::NonCustom(id) => PropertyId::NonCustom(id),
            }),
            suppress_animation_taint_sink,
            url_data: url_data.clone(),
            guard_identity,
            invocation: None,
        }
    }

    fn same_prepared_use(&self, other: &Self) -> bool {
        self.invocation.is_some()
            && self.invocation == other.invocation
            && self.name == other.name && self.namespace == other.namespace
            && self.property == other.property
            && self.suppress_animation_taint_sink == other.suppress_animation_taint_sink
            && self.url_data == other.url_data
    }

    pub fn property_id(&self) -> Option<PropertyIdRef> {
        self.property.as_ref().map(PropertyIdRef::from)
    }
}

pub(crate) enum AttrUseState {
    New,
    Evaluating,
    Pending,
    Ready(ComputedRegisteredValue),
    Invalid,
    Cyclic,
}

pub(crate) struct AttrUse {
    pub key: AttrUseKey,
    pub input: Option<Arc<VariableValue>>,
    pub state: AttrUseState,
    pub custom_depth: usize,
}

pub(crate) enum AttrEntry {
    Evaluate,
    Existing,
    PhysicalCycle(usize),
}

#[derive(Default)]
pub(crate) struct AttrResolution {
    pub uses: Vec<AttrUse>,
    active: Vec<usize>,
    pub prepared_owner: Option<usize>,
}

impl AttrResolution {
    pub fn reset(&mut self) {
        assert!(self.active.is_empty());
        self.uses.clear();
        self.prepared_owner = None;
    }

    pub fn request(&mut self, key: AttrUseKey, input: Option<Arc<VariableValue>>) -> usize {
        if let Some(index) = self.uses.iter().position(|request| request.key == key) {
            return index;
        }
        let index = self.uses.len();
        self.uses.push(AttrUse { key, input, state: AttrUseState::New, custom_depth: 0 });
        index
    }

    fn invocation_key(
        &self, owner: usize, occurrence: usize, name: &Name, namespace: &Namespace,
        property: Option<PropertyIdRef>, suppress: bool, url_data: &UrlExtraData,
    ) -> AttrUseKey {
        let mut key = AttrUseKey::new(name, namespace, property, suppress, url_data, self.uses.len());
        key.invocation = Some(AttrInvocation { owner, occurrence, ancestors: self.active.clone() });
        key
    }

    pub fn admit(
        &mut self, owner: usize, occurrence: usize, name: &Name, namespace: &Namespace,
        property: Option<PropertyIdRef>, suppress: bool, url_data: &UrlExtraData,
        input: Option<Arc<VariableValue>>,
    ) -> usize {
        let key = self.invocation_key(owner, occurrence, name, namespace, property, suppress, url_data);
        if let Some(index) = self.uses.iter().position(|request| request.key.same_prepared_use(&key)) {
            return index;
        }
        self.request(key, input)
    }

    fn prepared_request(
        &self, owner: usize, occurrence: usize, name: &Name, namespace: &Namespace,
        property: Option<PropertyIdRef>, suppress: bool, url_data: &UrlExtraData,
    ) -> Option<usize> {
        let key = self.invocation_key(owner, occurrence, name, namespace, property, suppress, url_data);
        self.uses.iter().position(|request| request.key.same_prepared_use(&key))
    }

    pub fn suspend(&mut self, index: usize) {
        assert_eq!(self.active.pop(), Some(index));
        if matches!(self.uses[index].state, AttrUseState::Evaluating) {
            self.uses[index].state = AttrUseState::Pending;
        }
    }

    pub fn enter(&mut self, index: usize) -> AttrEntry {
        let key = &self.uses[index].key;
        if let Some(position) = self.active.iter().position(|active| {
            let other = &self.uses[*active].key;
            key.name == other.name && key.namespace == other.namespace
        }) {
            let previous = self.active[position];
            for active in &self.active[position..] {
                self.uses[*active].state = AttrUseState::Cyclic;
            }
            self.uses[index].state = AttrUseState::Cyclic;
            return AttrEntry::PhysicalCycle(previous);
        }
        if !matches!(self.uses[index].state, AttrUseState::New) {
            return AttrEntry::Existing;
        }
        self.uses[index].state = AttrUseState::Evaluating;
        self.active.push(index);
        AttrEntry::Evaluate
    }

    fn mark_active_since(&mut self, depth: usize) {
        for request in &self.active[depth..] {
            self.uses[*request].state = AttrUseState::Cyclic;
        }
    }

    pub fn leave(&mut self, index: usize, value: Option<ComputedRegisteredValue>) {
        assert_eq!(self.active.pop(), Some(index));
        if matches!(self.uses[index].state, AttrUseState::Cyclic) {
            return;
        }
        assert!(matches!(self.uses[index].state, AttrUseState::Evaluating));
        self.uses[index].state = match value {
            Some(value) => AttrUseState::Ready(value),
            None => AttrUseState::Invalid,
        };
    }
}

#[derive(Default)]
struct SubstitutionState {
    names: Vec<Name>,
    attribute_depths: Vec<usize>,
    cyclic_names: Vec<Name>,
}

impl SubstitutionState {
    fn push_name(&mut self, name: &Name, attributes: &AttrResolution) {
        self.names.push(name.clone());
        self.attribute_depths.push(attributes.active.len());
    }

    fn pop_name(&mut self) {
        self.names.pop();
        self.attribute_depths.pop();
    }

    fn mark_names_since(&mut self, index: usize) {
        for name in &self.names[index..] {
            if !self.cyclic_names.contains(name) {
                self.cyclic_names.push(name.clone());
            }
        }
    }
}

fn key(name: &str, namespace: &str, property: u8, guard: usize) -> AttrUseKey {
    AttrUseKey::new(&name.into(), &namespace.into(), Some(PropertyIdRef::NonCustom(property)), false, &"url".into(), guard)
}

#[test]
fn changed_context_cannot_escape_physical_cycle() {
    let mut store = AttrResolution::default();
    let a = store.request(key("a", "", 1, 0), None);
    let b = store.request(key("b", "", 1, 1), None);
    let again = store.request(key("a", "", 2, 2), None);
    assert!(matches!(store.enter(a), AttrEntry::Evaluate));
    assert!(matches!(store.enter(b), AttrEntry::Evaluate));
    assert!(matches!(store.enter(again), AttrEntry::PhysicalCycle(i) if i == a));
    store.leave(b, Some(7));
    store.leave(a, Some(8));
    for id in [a,b,again] { assert!(matches!(store.uses[id].state, AttrUseState::Cyclic)); }
}

#[test]
fn namespace_is_part_of_physical_identity() {
    let mut store = AttrResolution::default();
    let a = store.request(key("a", "one", 1, 0), None);
    let b = store.request(key("a", "two", 1, 1), None);
    assert!(matches!(store.enter(a), AttrEntry::Evaluate));
    assert!(matches!(store.enter(b), AttrEntry::Evaluate));
    store.leave(b, Some(2)); store.leave(a, Some(1));
    assert!(matches!(store.uses[a].state, AttrUseState::Ready(1)));
    assert!(matches!(store.uses[b].state, AttrUseState::Ready(2)));
}

#[test]
fn ready_result_does_not_bypass_active_physical_guard() {
    let mut store = AttrResolution::default();
    let prior = store.request(key("a", "", 1, 0), None);
    assert!(matches!(store.enter(prior), AttrEntry::Evaluate));
    store.leave(prior, Some(9));
    let active = store.request(key("a", "", 2, 1), None);
    assert!(matches!(store.enter(active), AttrEntry::Evaluate));
    assert!(matches!(store.enter(prior), AttrEntry::PhysicalCycle(i) if i == active));
    store.leave(active, Some(3));
    assert!(matches!(store.uses[prior].state, AttrUseState::Cyclic));
}

#[test]
fn independent_context_is_not_globally_poisoned() {
    let mut store = AttrResolution::default();
    let a = store.request(key("a", "", 1, 0), None);
    assert!(matches!(store.enter(a), AttrEntry::Evaluate));
    assert!(matches!(store.enter(a), AttrEntry::PhysicalCycle(_)));
    store.leave(a, Some(1));
    let clean = store.request(key("a", "", 2, 2), None);
    assert!(matches!(store.enter(clean), AttrEntry::Evaluate));
    store.leave(clean, Some(4));
    assert!(matches!(store.uses[clean].state, AttrUseState::Ready(4)));
    assert!(matches!(store.uses[a].state, AttrUseState::Cyclic));
}

#[test]
#[should_panic]
fn active_session_cannot_be_reset() {
    let mut store = AttrResolution::default();
    let id = store.request(key("a", "", 1, 0), None);
    store.enter(id); store.reset();
}

#[test]
fn attribute_cycle_marks_intervening_custom_guards() {
    let mut attrs = AttrResolution::default();
    let mut vars = SubstitutionState::default();
    let a = attrs.request(key("a", "", 1, 0), None);
    attrs.uses[a].custom_depth = vars.names.len();
    attrs.enter(a);
    vars.push_name(&"--c".into(), &attrs);
    let again = attrs.request(key("a", "", 2, 1), None);
    let AttrEntry::PhysicalCycle(previous) = attrs.enter(again) else { panic!() };
    vars.mark_names_since(attrs.uses[previous].custom_depth);
    vars.pop_name(); attrs.leave(a, Some(3));
    assert!(vars.cyclic_names.contains(&"--c".into()));
    assert!(matches!(attrs.uses[a].state, AttrUseState::Cyclic));
}

#[test]
fn custom_cycle_marks_intervening_attribute_guards() {
    let mut attrs = AttrResolution::default();
    let mut vars = SubstitutionState::default();
    vars.push_name(&"--c".into(), &attrs);
    let a = attrs.request(key("a", "", 1, 0), None);
    attrs.enter(a);
    vars.mark_names_since(0);
    attrs.mark_active_since(vars.attribute_depths[0]);
    attrs.leave(a, Some(3)); vars.pop_name();
    assert!(vars.cyclic_names.contains(&"--c".into()));
    assert!(matches!(attrs.uses[a].state, AttrUseState::Cyclic));
}

#[test]
fn guards_before_the_cycle_are_not_marked() {
    let mut attrs = AttrResolution::default();
    let mut vars = SubstitutionState::default();
    vars.push_name(&"--outer".into(), &attrs);
    let a = attrs.request(key("a", "", 1, 0), None);
    attrs.uses[a].custom_depth = vars.names.len(); attrs.enter(a);
    vars.push_name(&"--inner".into(), &attrs);
    let again = attrs.request(key("a", "", 2, 1), None);
    let AttrEntry::PhysicalCycle(previous) = attrs.enter(again) else { panic!() };
    vars.mark_names_since(attrs.uses[previous].custom_depth);
    vars.pop_name(); attrs.leave(a, Some(3)); vars.pop_name();
    assert!(!vars.cyclic_names.contains(&"--outer".into()));
    assert!(vars.cyclic_names.contains(&"--inner".into()));
}

#[test]
fn prepared_and_final_use_share_identity_and_ready_value() {
    let mut store = AttrResolution::default();
    let name = "a".into(); let namespace = "".into(); let url = "url".into();
    let id = store.admit(1, 100, &name, &namespace, Some(PropertyIdRef::NonCustom(1)), false, &url, None);
    assert!(matches!(store.enter(id), AttrEntry::Evaluate));
    store.leave(id, Some(7));
    let final_id = store.prepared_request(1, 100, &name, &namespace, Some(PropertyIdRef::NonCustom(1)), false, &url).unwrap();
    assert_eq!(id, final_id);
    assert!(matches!(store.enter(final_id), AttrEntry::Existing));
    assert!(matches!(store.uses[final_id].state, AttrUseState::Ready(7)));
}

#[test]
fn changed_ancestry_does_not_poison_prior_prepared_result() {
    let mut store = AttrResolution::default();
    let name = "a".into(); let namespace = "".into(); let url = "url".into();
    let first = store.admit(1, 100, &name, &namespace, Some(PropertyIdRef::NonCustom(1)), false, &url, None);
    store.enter(first); store.leave(first, Some(7));
    let parent = store.admit(2, 200, &name, &namespace, Some(PropertyIdRef::NonCustom(2)), false, &url, None);
    store.enter(parent);
    assert!(store.prepared_request(1, 100, &name, &namespace, Some(PropertyIdRef::NonCustom(1)), false, &url).is_none());
    let nested = store.admit(1, 100, &name, &namespace, Some(PropertyIdRef::NonCustom(1)), false, &url, None);
    assert_ne!(first, nested);
    assert!(matches!(store.enter(nested), AttrEntry::PhysicalCycle(i) if i == parent));
    store.leave(parent, Some(9));
    assert!(matches!(store.uses[first].state, AttrUseState::Ready(7)));
    assert!(matches!(store.uses[nested].state, AttrUseState::Cyclic));
}

#[test]
fn changed_graph_owner_or_occurrence_is_not_admitted_by_other_use() {
    let mut store = AttrResolution::default();
    let name = "a".into(); let namespace = "".into(); let url = "url".into();
    store.admit(1, 100, &name, &namespace, Some(PropertyIdRef::NonCustom(1)), false, &url, None);
    assert!(store.prepared_request(2, 100, &name, &namespace, Some(PropertyIdRef::NonCustom(1)), false, &url).is_none());
    assert!(store.prepared_request(1, 101, &name, &namespace, Some(PropertyIdRef::NonCustom(1)), false, &url).is_none());
    assert!(store.prepared_request(1, 100, &name, &namespace, Some(PropertyIdRef::NonCustom(2)), false, &url).is_none());
    assert!(store.prepared_request(1, 100, &name, &namespace, Some(PropertyIdRef::NonCustom(1)), true, &url).is_none());
}

#[test]
fn ancestor_backedge_stays_pending_until_scc_resolution() {
    let mut store = AttrResolution::default();
    let id = store.request(key("a", "", 1, 0), None);
    assert!(matches!(store.enter(id), AttrEntry::Evaluate));
    store.suspend(id);
    assert!(matches!(store.uses[id].state, AttrUseState::Pending));
    assert!(matches!(store.enter(id), AttrEntry::Existing));
    store.uses[id].state = AttrUseState::Cyclic;
    assert!(matches!(store.enter(id), AttrEntry::Existing));
    assert!(matches!(store.uses[id].state, AttrUseState::Cyclic));
    store.reset();
}

#[test]
fn graph_result_session_does_not_leak_into_new_keyframe() {
    let mut store = AttrResolution::default();
    let id = store.request(key("a", "", 1, 0), None);
    store.enter(id); store.leave(id, Some(1));
    store.reset();
    let next = store.request(key("a", "", 1, 0), None);
    assert!(matches!(store.enter(next), AttrEntry::Evaluate));
    store.leave(next, Some(2));
    assert!(matches!(store.uses[next].state, AttrUseState::Ready(2)));
}
