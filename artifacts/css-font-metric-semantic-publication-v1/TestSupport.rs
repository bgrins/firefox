use std::collections::HashMap;
use std::sync::Arc;
type Name = u32;
type Namespace = u32;
type PrioritaryPropertyId = usize;
type AttributeTracker = ();
type SmallVec<T> = Vec<<T as Array>::Item>;
trait Array { type Item; }
impl<T, const N: usize> Array for [T; N] { type Item = T; }
#[derive(Clone, Eq, PartialEq, Debug)]
enum VarType { Custom(Name), Attr(Name, Namespace), NonCustom(usize) }
impl VarType {
    fn namespace(&self) -> Option<&Namespace> {
        match self { Self::Attr(_, ns) => Some(ns), _ => None }
    }
}
struct ComputedPropertyValue(u32);
struct PreparedCustomValue(u32);
#[derive(Default)]
struct Observations { applied: Vec<(u32, Option<Namespace>, u32)>, cycle_steps: Vec<Vec<NodeReadiness>> }
impl PreparedCustomValue {
    fn apply(self, name: &Name, _: &(), output: &mut Observations) {
        output.applied.push((*name, None, self.0));
    }
}
fn substitute_references_if_needed_and_apply(name: &Name, ns: Option<&Namespace>, value: &ComputedPropertyValue, _: &(), output: &mut Observations, _: &mut AttributeTracker) {
    output.applied.push((*name, ns.copied(), value.0));
}
#[derive(Default)]
struct OrderIndexMap { var: HashMap<Name, usize>, attr: HashMap<Namespace, HashMap<Name, usize>> }
impl OrderIndexMap { fn clear(&mut self) { self.var.clear(); self.attr.clear(); } }
struct Context<'a> {
    count: usize,
    index_map: OrderIndexMap,
    non_custom_index_map: [Option<usize>; 3],
    var_info: Vec<VarInfo>,
    stack: Vec<usize>,
    stylist: &'a (),
    computed_context: &'a mut Observations,
}
impl<'a> Context<'a> {
    fn new(output: &'a mut Observations) -> Self {
        Self {count: 0, index_map: OrderIndexMap::default(), non_custom_index_map: [None;3], var_info: vec![], stack: vec![], stylist: &(), computed_context: output}
    }
    fn insert(&mut self, var: VarType) -> usize {
        let i = self.count; self.count += 1;
        match &var {
            VarType::Custom(n) => {self.index_map.var.insert(*n,i);},
            VarType::Attr(n,ns) => {self.index_map.attr.entry(*ns).or_default().insert(*n,i);},
            VarType::NonCustom(id) => self.non_custom_index_map[*id] = Some(i),
        }
        self.var_info.push(VarInfo {var: Some(var), lowlink:i, publication: NodePublication::SemanticOpen}); self.stack.push(i); i
    }
    fn apply_prioritary_property(&mut self, id: usize, _: &mut AttributeTracker) {
        assert!(matches!(self.visited(&VarType::NonCustom(id)),Some(VisitResult::ComputationPending(_))));
        self.computed_context.applied.push((100 + id as u32,None,1));
    }
    fn handle_loop(&mut self, _: &VarType) {
        self.computed_context.cycle_steps.push(self.var_info.iter().map(|v|v.publication.readiness()).collect());
    }
}
