#![allow(dead_code)]
use std::collections::{HashMap, HashSet};
use std::sync::Arc;
type Name = String;
type PrecomputedHashMap<K, V> = HashMap<K, V>;
type PrecomputedHashSet<T> = HashSet<T>;
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct RuleCascadeFlags(u8);
impl Default for RuleCascadeFlags { fn default()->Self{Self(0)} }
#[derive(Clone, Debug, PartialEq, Eq)]
struct ComputedRegisteredValue(&'static str);
struct PropertyDescriptors { inherits: bool }
#[derive(Clone, Default)]
struct ComputedCustomProperties {
    inherited: HashMap<Name, ComputedRegisteredValue>,
    non_inherited: HashMap<Name, ComputedRegisteredValue>,
}
impl ComputedCustomProperties {
    fn get(&self, registration: &PropertyDescriptors, name: &Name) -> Option<&ComputedRegisteredValue> {
        if registration.inherits { self.inherited.get(name) } else { self.non_inherited.get(name) }
    }
    fn is_empty(&self) -> bool { self.inherited.is_empty() && self.non_inherited.is_empty() }
}
#[derive(Default)]
struct ComputedSubstitutionFunctions { custom_properties: ComputedCustomProperties }
impl ComputedSubstitutionFunctions {
    fn new(properties: Option<ComputedCustomProperties>, _: Option<()>) -> Self { Self { custom_properties: properties.unwrap_or_default() } }
    fn get_var(&self, registration: &PropertyDescriptors, name: &Name) -> Option<&ComputedRegisteredValue> { self.custom_properties.get(registration, name) }
}
#[derive(Default)]
struct SeenSubstitutionFunctions<'a> { var: PrecomputedHashMap<&'a Name, bool> }
struct Stylist { initial: ComputedCustomProperties }
impl Stylist { fn get_custom_property_registration(&self, name: &Name) -> &PropertyDescriptors { static INHERITED:PropertyDescriptors=PropertyDescriptors{inherits:true};static RESET:PropertyDescriptors=PropertyDescriptors{inherits:false}; if name == "reset" {&RESET} else {&INHERITED} } fn get_custom_property_initial_values(&self) -> &ComputedCustomProperties { &self.initial } }
struct Cascade { stylist: Stylist }
#[derive(Default)]
struct Builder { substitution_functions: ComputedSubstitutionFunctions }
mod computed {
    use super::*;
    #[derive(Default)]
    pub struct Context { pub included_cascade_flags: RuleCascadeFlags, pub root: bool, pub inherited: ComputedCustomProperties, pub builder: Builder }
    impl Context {
        pub fn is_root_element(&self) -> bool { self.root }
        pub fn inherited_custom_properties(&self) -> &ComputedCustomProperties { &self.inherited }
    }
}
#[derive(Default)]
struct PriorityCompletion { active: HashSet<u8>, claimed: HashSet<u8>, computed_size: Option<()> }
enum VarType { Custom(Name), Attr(Name) }
struct VarInfo { var: Option<VarType>, publication: NodePublication<()> }
struct Context {
    receipt: CustomInitializationReceipt, stylist: Stylist, computed_context: computed::Context,
    deferred_size: Option<()>, finished_root: Option<()>, size_preparation: Option<()>,
    metric_action: Option<()>, font_preparation: Option<()>, metric_references: Option<()>,
    priority_completion: PriorityCompletion, frames: Vec<()>, frame_root: Option<()>, frame_reply: Option<()>,
    stack: Vec<usize>, var_info: Vec<VarInfo>, size_node: Option<usize>, size_identity: Arc<()>,
    count: usize, index_map: HashMap<Name, usize>, non_custom_index_map: HashMap<u8, usize>,
}
impl Context {
    fn empty() -> Self { let computed_context = computed::Context::default(); let receipt = CustomInitializationReceipt::after_selection(&SeenSubstitutionFunctions::default(), &computed_context.builder.substitution_functions, RuleCascadeFlags(0)); Self { receipt, stylist: Stylist { initial: ComputedCustomProperties::default() }, computed_context, deferred_size: None, finished_root: None, size_preparation: None, metric_action: None, font_preparation: None, metric_references: None, priority_completion: PriorityCompletion::default(), frames: vec![], frame_root: None, frame_reply: None, stack: vec![], var_info: vec![], size_node: None, size_identity: Arc::new(()), count: 0, index_map: HashMap::new(), non_custom_index_map: HashMap::new() } }
}
