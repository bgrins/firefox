use std::{cmp,collections::HashSet};
type RuleCascadeFlags=u8;
type ComputedPropertyValue=VariableValue;
#[derive(Clone,Debug,Eq,PartialEq,Hash)]enum VarType{Custom(Name),Attr(Name,Namespace),NonCustom(SingleNonCustomReference)}
impl VarType{fn namespace(&self)->Option<&Namespace>{match self{Self::Attr(_,n)=>Some(n),_=>None}}}
#[derive(Clone,Copy,Debug,Eq,PartialEq,Hash)]enum SingleNonCustomReference{FontUnits,LhUnits,ColorScheme}
impl SingleNonCustomReference{fn to_prioritary_id(self)->PrioritaryPropertyId{PrioritaryPropertyId}}
#[derive(Clone,Copy)]struct PrioritaryPropertyId;impl PrioritaryPropertyId{fn to_longhand(self)->u8{0}}
#[derive(Default)]struct PrioritaryPropertyIdSet;
#[derive(Clone,Copy)]enum FontTarget{Metric}
impl FontTarget{fn same_as(self,_:Self)->bool{true}}
struct NonCustomPropertyReferences;
#[derive(Clone,Copy)]enum FontDependencyDemand{None}
#[derive(Clone,Copy)]enum PublicationDemand{Ready}
#[derive(Clone,Copy,Eq,PartialEq)]enum ComputationStatus{Ready,Pending}
#[derive(Clone,Copy)]enum FramePhase{References,Prepare,Units,LateDefault,Close,Publish}
#[derive(Clone,Copy)]enum LinkPurpose{Reference,Unit,PrioritySize,LateDefault}
#[derive(Clone,Copy,Eq,PartialEq)]enum ReferenceReadiness{Ready,SemanticOpen,SemanticCycle,ComputationPending}
#[derive(Clone)]struct MetricAction{identity:Arc<()>,root:VarType,owner:VarType,index:usize,prerequisite:FontTarget}
struct Bindings{root:Arc<()>,flags:RuleCascadeFlags,values:FxHashMap<Name,Option<ComputedRegisteredValue>>,pending:HashSet<Name>}
impl Bindings{
 fn valid_for(&mut self,f:RuleCascadeFlags)->bool{self.flags==f}
 fn value(&self,n:&Name,_:&PropertyDescriptors)->Option<Option<ComputedRegisteredValue>>{if self.pending.contains(n){None}else{Some(self.values.get(n).cloned().unwrap_or(None))}}
}
#[derive(Default)]struct LookupCascade{attribute_inputs:FxHashMap<(Name,Namespace),CapturedAttributeInput>}
#[derive(Default)]struct Builder{substitution_functions:ComputedSubstitutionFunctions,invalid_non_custom_properties:HashSet<u8>,inherited_style:Inherited,is_root_element:bool}
#[derive(Default)]struct Inherited{map:ComputedSubstitutionFunctions}impl Inherited{fn custom_properties(&self)->&ComputedSubstitutionFunctions{&self.map}}
mod computed{#[derive(Default)]pub struct Context{pub builder:super::Builder,pub included_cascade_flags:u8,pub computations:Vec<String>}impl Context{pub fn is_root_element(&self)->bool{self.builder.is_root_element}}}
#[derive(Clone)]struct Initial{css:String,url_data:UrlExtraData}
struct PropertyDescriptors{syntax:Option<SyntaxDescriptor>,initial_value:Option<Initial>,inherited:bool}
impl PropertyDescriptors{fn is_universal(&self)->bool{self.syntax.is_none()}fn inherits(&self)->bool{self.inherited}}
enum CSSWideKeyword{Initial}
impl CSSWideKeyword{fn parse(p:&mut Parser)->Result<Self,ParseError>{p.expect_ident_matching("initial")?;p.expect_exhausted()?;Ok(Self::Initial)}}
impl SpecifiedRegisteredValue{
 fn depends_on_color_scheme(&self)->bool{false}
 fn to_computed_value(self,c:&mut computed::Context)->ComputedRegisteredValue{c.computations.push(self.0.css.clone());ComputedRegisteredValue{value:self.0,attr_tainted:false}}
}
fn prepare_invalid_custom_kind(_:&Name,r:&PropertyDescriptors,_:&computed::Context)->PreparedCustomKind{
 match &r.initial_value{Some(v)=>PreparedCustomKind::Initial(SpecifiedRegisteredValue(tokens(&v.css,v.url_data.0))),None=>PreparedCustomKind::Invalid}
}
fn apply_substituted_value(n:&Name,_:Option<&Namespace>,_:&UrlExtraData,input:SubstitutionInput,s:&Stylist,c:&mut computed::Context){
 let SubstitutionInput::Prepared(v)=input;match v{Ok(v)=>{let mut value=ComputedRegisteredValue::universal(Arc::new(tokens(&v.css,0)));value.attr_tainted=v.attr_tainted;c.builder.substitution_functions.insert_var(s.get_custom_property_registration(n),n,value)},Err(())=>handle_invalid_at_computed_value_time(n,s.get_custom_property_registration(n),c)}
}
enum SubstitutionInput{Prepared(Result<Substitution<'static>,()>)}
fn compute_value(css:&str,url:&UrlExtraData,_:&PropertyDescriptors,_:&mut computed::Context,_:AttrTaint,_:Option<PropertyIdRef>)->Result<ComputedRegisteredValue,()>{Ok(ComputedRegisteredValue::universal(Arc::new(tokens(css,url.0))))}
fn substitute_references_if_needed_and_apply(_: &Name,_:Option<&Namespace>,_:&VariableValue,_:&Stylist,_:&mut computed::Context,_:&mut AttributeTracker){panic!("guarded value must not substitute twice")}
fn tokens(css:&str,url:u8)->VariableValue{VariableValue::parse(&mut Parser::new(css),None,&UrlExtraData(url)).unwrap()}
impl ComputedSubstitutionFunctions{
 fn insert_var(&mut self,_:&PropertyDescriptors,n:&Name,v:ComputedRegisteredValue){self.vars.insert(n.clone(),v);}
 fn remove_var(&mut self,_:&PropertyDescriptors,n:&Name){self.vars.remove(n);}
 fn remove_attr(&mut self,n:&Name,_:&Namespace){self.attrs.remove(n);}
 fn get(&self,_:&PropertyDescriptors,n:&Name)->Option<&ComputedRegisteredValue>{self.vars.get(n)}
}
struct TraversalFrame{guarded_custom:Option<GuardedCustomFrame>,var:VarType,index:usize,lowlink:usize,self_ref:bool,phase:FramePhase,waiting:Option<(VarType,LinkPurpose)>,reference_reply:Option<(VarType,ReferenceReadiness)>,prepared_custom:Option<PreparedCustomValue>,value:Option<Arc<VariableValue>>,value_non_custom_refs:ReferenceFlags,unit_cursor:usize,registered:bool,unit_links:Vec<SingleNonCustomReference>}
enum FrameStep{Link(VarType),Complete(VisitResult),ComputedSize,Pending(Option<FontTarget>)}
struct Context{frames:Vec<TraversalFrame>,frame_reply:Option<(VarType,VisitResult)>,deferred_size:Option<TraversalFrame>,finished_root:Option<VisitResult>,metric_action:Option<MetricAction>,frame_root:Option<VarType>,computed_context:&'static mut computed::Context,var_info:Vec<VarInfo>,stack:Vec<usize>,stylist:&'static mut Stylist,indices:FxHashMap<VarType,usize>,specs:FxHashMap<Name,VariableValue>,published:Vec<Name>,lookup_bindings:Bindings,cascade:LookupCascade,environment_inputs:Vec<(Name,UrlExtraData,Option<VariableValue>)>,blocked:HashSet<Name>,unit_ready:bool,unit_visits:Vec<SingleNonCustomReference>,lookup_reply:Option<(LonghandId,FontSelectionReply)>}
impl Context{
 fn new()->Self{Self{frames:vec![],frame_reply:None,deferred_size:None,finished_root:None,metric_action:None,frame_root:None,computed_context:Box::leak(Box::default()),var_info:vec![],stack:vec![],stylist:Box::leak(Box::default()),indices:FxHashMap::default(),specs:FxHashMap::default(),published:vec![],lookup_bindings:Bindings{root:Arc::new(()),flags:0,values:FxHashMap::default(),pending:HashSet::new()},cascade:LookupCascade::default(),environment_inputs:vec![],blocked:HashSet::new(),unit_ready:false,unit_visits:vec![],lookup_reply:None}}
 fn computed_size_ready(&self,_:usize)->bool{false}
 fn apply_prioritary_property(&mut self,_:PrioritaryPropertyId,_:&mut AttributeTracker)->ComputationStatus{unreachable!()}
 fn visited(&self,var:&VarType)->Option<VisitResult>{self.indices.get(var).map(|&i|match self.var_info[i].publication.readiness(){NodeReadiness::SemanticOpen=>VisitResult::SemanticOpen(i),NodeReadiness::ComputationPending=>VisitResult::ComputationPending(i),NodeReadiness::Complete=>VisitResult::Complete,NodeReadiness::CycleSettled=>VisitResult::CycleSettled})}
 fn record_lookup_publication(&mut self,i:usize){assert!(self.var_info[i].publication.can_retire());let VarType::Custom(n)=self.indices.iter().find(|(_,v)|**v==i).unwrap().0 else{panic!()};self.published.push(n.clone());self.lookup_bindings.pending.remove(n);self.lookup_bindings.values.insert(n.clone(),self.computed_context.builder.substitution_functions.vars.get(n).cloned());}
 fn add(&mut self,n:&str,css:&str,url:u8,registered:bool){self.specs.insert(n.into(),tokens(css,url));self.lookup_bindings.pending.insert(n.into());self.stylist.registrations.insert(n.into(),PropertyDescriptors{syntax:registered.then(||SyntaxDescriptor("<length>".into())),initial_value:registered.then(||Initial{css:"8px".into(),url_data:UrlExtraData(0)}),inherited:false});}
}
fn start_frame(var:VarType,c:&mut Context,_:&mut AttributeTracker)->Result<TraversalFrame,VisitResult>{
 if let Some(result)=c.visited(&var){return Err(result)};
 if let VarType::NonCustom(unit)=var{c.unit_visits.push(unit);return Err(if c.unit_ready{VisitResult::Complete}else{VisitResult::ComputationPending(usize::MAX)})}
 let VarType::Custom(n)=&var else{panic!("unexpected legacy attribute graph")};
 if c.blocked.contains(n){return Err(VisitResult::ComputationPending(usize::MAX))}
 let registered=!c.stylist.get_custom_property_registration(n).is_universal();
 let value=c.specs.get(n).unwrap().clone();let i=c.var_info.len();c.indices.insert(var.clone(),i);c.var_info.push(VarInfo{var:Some(var.clone()),lowlink:i,publication:NodePublication::SemanticOpen});c.stack.push(i);
 Ok(TraversalFrame{guarded_custom:None,var,index:i,lowlink:i,self_ref:false,phase:FramePhase::References,waiting:None,reference_reply:None,prepared_custom:None,value:Some(Arc::new(value)),value_non_custom_refs:ReferenceFlags::empty(),unit_cursor:0,registered,unit_links:vec![]})
}

struct FontSelectionReply{value:Arc<VariableValue>,generation:Arc<()>,lookup:Option<SubstitutionLookupReply>}
struct MetricLookup{action:MetricAction,flags:u8,generation:Arc<()>,depth:usize,semantic_floor:usize,request:SubstitutionLookup,longhand:LonghandId,value:Arc<VariableValue>}
