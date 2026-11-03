#[derive(Clone,PartialEq,Eq,Hash)]enum VarType{Custom(Name),Attr(Name,Namespace)}
#[derive(Clone,Copy)]enum VisitResult{Complete,CycleSettled,SemanticOpen(usize),ComputationPending(usize),ComputedSize(usize)}
#[derive(Default)]struct LookupBindings{pending:HashSet<Name>,values:FxHashMap<Name,Option<ComputedRegisteredValue>>,flags:RuleCascadeFlags,valid:bool}
impl LookupBindings{
    fn valid_for(&mut self,flags:RuleCascadeFlags)->bool{self.valid&=flags==self.flags;self.valid}
    fn value(&self,name:&Name,_:&())->Option<Option<ComputedRegisteredValue>>{if self.pending.contains(name){None}else{Some(self.values.get(name).cloned().unwrap_or(None))}}
}
#[derive(Default)]struct LookupCascade{attribute_inputs:FxHashMap<(Name,Namespace),CapturedAttributeInput>,attribute_value_urls:FxHashMap<(Name,Namespace),UrlExtraData>}
struct LookupContext{
    lookup_bindings:LookupBindings,computed_context:computed::Context,cascade:LookupCascade,stylist:Stylist,
    environment_inputs:Vec<(Name,UrlExtraData,Option<VariableValue>)>,
    settled_attributes:FxHashMap<(Name,Namespace),Option<ComputedRegisteredValue>>,
    functions:ComputedSubstitutionFunctions,nodes:FxHashMap<VarType,VisitResult>,
}
impl LookupContext{
    fn new()->Self{Self{lookup_bindings:LookupBindings{valid:true,..Default::default()},computed_context:computed::Context::default(),cascade:LookupCascade::default(),stylist:Stylist::default(),environment_inputs:Vec::new(),settled_attributes:FxHashMap::default(),functions:ComputedSubstitutionFunctions::default(),nodes:FxHashMap::default()}}
    fn visited(&self,var:&VarType)->Option<VisitResult>{self.nodes.get(var).copied()}
    fn map(&self)->&ComputedSubstitutionFunctions{&self.functions}
    fn map_mut(&mut self)->&mut ComputedSubstitutionFunctions{&mut self.functions}
}
impl ComputedSubstitutionFunctions{
    fn contains_attr(&self,name:&Name,_:&Namespace)->bool{self.attrs.contains_key(name)}
    fn insert_attr(&mut self,name:&Name,_:&Namespace,value:ComputedRegisteredValue){self.attrs.insert(name.clone(),value);}
}
