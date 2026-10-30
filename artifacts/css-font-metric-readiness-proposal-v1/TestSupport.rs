use std::borrow::Cow;
use std::cell::Cell;
use std::collections::{HashMap, HashSet};
use std::sync::Arc;

type DeclarationIndex = u32;
type LonghandId = PrioritaryPropertyId;
#[derive(Clone, Copy, Debug, Eq, PartialEq, Hash)]
enum PrioritaryPropertyId { FontWeight, FontWidth, FontStyle, FontSizeAdjust, Direction, WritingMode, TextOrientation, Appearance }
#[derive(Clone, Copy, Default)]
struct PrioritaryPropertyIdSet(u16);
impl PrioritaryPropertyIdSet {
    fn contains(&self, id: PrioritaryPropertyId) -> bool { self.0 & (1 << id as u8) != 0 }
    fn insert(&mut self, id: PrioritaryPropertyId) { self.0 |= 1 << id as u8; }
    fn contains_all(&self, other: &Self) -> bool { self.0 & other.0 == other.0 }
}
impl PrioritaryPropertyId {
    fn to_longhand(self) -> Self { self }
    fn dependencies(self) -> &'static PrioritaryPropertyIdSet {
        static APPEARANCE: PrioritaryPropertyIdSet = PrioritaryPropertyIdSet(1 << 7);
        static EMPTY: PrioritaryPropertyIdSet = PrioritaryPropertyIdSet(0);
        if (self as u8) < 4 { &APPEARANCE } else { &EMPTY }
    }
}
#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
struct RuleCascadeFlags(u8);
impl std::ops::Sub for RuleCascadeFlags { type Output = Self; fn sub(self, rhs: Self) -> Self { Self(self.0 & !rhs.0) } }
impl RuleCascadeFlags { fn is_empty(self) -> bool { self.0 == 0 } }
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum RevertKind { Origin, Layer, Rule }
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct CascadePriority { origin: u8, layer: u8, rule: u8, flags: RuleCascadeFlags }
impl CascadePriority {
    fn flags(self) -> RuleCascadeFlags { self.flags }
    fn allows_when_reverted(self, next: &Self, kind: RevertKind) -> bool {
        match kind { RevertKind::Origin => next.origin < self.origin, RevertKind::Layer => (next.origin,next.layer) < (self.origin,self.layer), RevertKind::Rule => (next.origin,next.layer,next.rule) < (self.origin,self.layer,self.rule) }
    }
}
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum CSSWideKeyword { Revert(RevertKind), Initial, Inherit, Unset }
impl CSSWideKeyword { fn revert_kind(self) -> Option<RevertKind> { if let Self::Revert(kind)=self {Some(kind)} else {None} } }
#[derive(Clone, Debug)]
struct UnparsedValue { result: Box<PropertyDeclaration> }
#[derive(Clone, Debug)]
struct VariableDeclaration { value: Arc<UnparsedValue> }
#[derive(Clone, Debug)]
enum PropertyDeclaration { WithVariables(VariableDeclaration), Wide(CSSWideKeyword), Value(u16) }
impl PropertyDeclaration { fn get_css_wide_keyword(&self) -> Option<CSSWideKeyword> { if let Self::Wide(kw)=self {Some(*kw)} else {None} } }
#[derive(Clone, Copy)]
struct Declaration<'a> { decl: &'a PropertyDeclaration, priority: CascadePriority, next_index: DeclarationIndex }
#[derive(Clone, Copy)]
struct DeclarationPosition { most_important: DeclarationIndex }
struct Declarations<'a> { longhand_declarations: Vec<Declaration<'a>>, prioritary_positions: [DeclarationPosition;8] }
#[derive(Default)]
struct Seen { longhands: LonghandSet }
#[derive(Default)]
struct LonghandSet(HashSet<LonghandId>);
impl LonghandSet {
 fn contains(&self, id: LonghandId) -> bool { self.0.contains(&id) }
 fn insert(&mut self, id: LonghandId) { self.0.insert(id); }
 fn is_empty(&self) -> bool { self.0.is_empty() }
}
#[derive(Default)]
struct Reverted { longhands: HashMap<LonghandId,(CascadePriority,RevertKind)> }
#[derive(Default)]
struct Cascade<'a> { seen: Seen, reverted: Reverted, ensured_prioritary: PrioritaryPropertyIdSet, substitutions: Cell<usize>, publications: Vec<PropertyDeclaration>, fixups: usize, lifetime: std::marker::PhantomData<&'a ()> }
mod computed { #[derive(Default)] pub struct Context { pub included_cascade_flags: super::RuleCascadeFlags } }
struct ShorthandsWithPropertyReferencesCache;
struct AttributeTracker;
impl Cascade<'_> {
    fn substitute_variables_if_needed<'a>(&self, _: &mut computed::Context, _: &mut ShorthandsWithPropertyReferencesCache, declaration: &'a PropertyDeclaration, _: &mut AttributeTracker) -> Cow<'a,PropertyDeclaration> {
        if let PropertyDeclaration::WithVariables(v)=declaration { self.substitutions.set(self.substitutions.get()+1); Cow::Owned((*v.value.result).clone()) } else {Cow::Borrowed(declaration)}
    }
    fn apply_one_longhand(&mut self, _: &mut computed::Context, id: LonghandId, declaration: &PropertyDeclaration, priority: CascadePriority, _: &mut ShorthandsWithPropertyReferencesCache, _: &mut AttributeTracker) {
        assert!(!matches!(declaration, PropertyDeclaration::WithVariables(..)));
        if let Some(kind)=declaration.get_css_wide_keyword().and_then(|kw|kw.revert_kind()) { self.reverted.longhands.insert(id,(priority,kind)); } else { self.seen.longhands.insert(id); }
        self.publications.push(declaration.clone());
    }
    fn did_apply_prioritary_property(&mut self, _: &mut computed::Context, _: PrioritaryPropertyId) { self.fixups+=1; }
}
fn var(value: PropertyDeclaration) -> PropertyDeclaration { PropertyDeclaration::WithVariables(VariableDeclaration { value: Arc::new(UnparsedValue { result: Box::new(value) }) }) }
fn declarations<'a>(values: &'a [PropertyDeclaration], priorities: &[CascadePriority]) -> Declarations<'a> {
    Declarations { longhand_declarations: values.iter().enumerate().map(|(i,decl)|Declaration { decl, priority: priorities[i], next_index: if i+1==values.len(){0}else{(i+1)as u32} }).collect(), prioritary_positions: [DeclarationPosition { most_important: if values.is_empty(){DeclarationIndex::MAX}else{0} };8] }
}
fn priority(origin:u8,layer:u8,rule:u8,flags:u8) -> CascadePriority { CascadePriority { origin,layer,rule,flags:RuleCascadeFlags(flags) } }

#[test]
fn reached_rollback_continuation_and_single_publication() {
    for kind in [RevertKind::Origin,RevertKind::Layer,RevertKind::Rule] {
        let values=[var(PropertyDeclaration::Wide(CSSWideKeyword::Revert(kind))),var(PropertyDeclaration::Value(999)),var(PropertyDeclaration::Value(700)),var(PropertyDeclaration::Value(400))];
        let blocked=match kind { RevertKind::Origin=>priority(2,1,1,0), RevertKind::Layer=>priority(2,2,1,0), RevertKind::Rule=>priority(2,2,2,0) };
        let priorities=[priority(2,2,2,0),blocked,priority(1,1,1,0),priority(0,0,0,0)];
        let decls=declarations(&values,&priorities); let mut c=Cascade::default(); let mut cx=computed::Context::default(); let mut cache=ShorthandsWithPropertyReferencesCache; let mut attr=AttributeTracker;
        let complete=PrioritaryPropertyIdSet(255); let mut state=c.begin_metric_preparation(&cx,&decls,PrioritaryPropertyId::FontWeight);
        let MetricPreparationStep::References(id,first)=c.resume_metric_preparation(&mut cx,&mut cache,&mut attr,&mut state,&complete,None) else {panic!()}; assert_eq!(id,PrioritaryPropertyId::FontWeight);
        let MetricPreparationStep::References(_,second)=c.resume_metric_preparation(&mut cx,&mut cache,&mut attr,&mut state,&complete,Some(first)) else {panic!()};
        for _ in 0..4 { assert!(matches!(c.resume_metric_preparation(&mut cx,&mut cache,&mut attr,&mut state,&complete,None),MetricPreparationStep::References(..))); }
        assert_eq!(c.substitutions.get(),1); assert!(c.publications.is_empty()); assert!(c.seen.longhands.is_empty()); assert!(c.reverted.longhands.is_empty()); assert!(!c.ensured_prioritary.contains(PrioritaryPropertyId::FontWeight));
        assert!(matches!(c.resume_metric_preparation(&mut cx,&mut cache,&mut attr,&mut state,&complete,Some(second)),MetricPreparationStep::Complete));
        assert_eq!(c.substitutions.get(),2); assert!(c.publications.is_empty());
        assert!(c.publish_prepared_metric(&mut cx,&mut cache,&mut attr,state,&complete).is_ok());
        assert_eq!(c.substitutions.get(),2); assert_eq!(c.publications.len(),2); assert!(matches!(c.publications[1],PropertyDeclaration::Value(700))); assert_eq!(c.fixups,1); assert!(c.ensured_prioritary.contains(PrioritaryPropertyId::FontWeight));
    }
}

#[test]
fn prerequisites_wrong_reference_and_changed_eligibility_block() {
    let values=[var(PropertyDeclaration::Value(700))]; let priorities=[priority(2,2,2,0)]; let decls=declarations(&values,&priorities);
    let mut c=Cascade::default(); let mut cx=computed::Context::default(); let mut cache=ShorthandsWithPropertyReferencesCache; let mut attr=AttributeTracker;
    let mut state=c.begin_metric_preparation(&cx,&decls,PrioritaryPropertyId::FontWeight); let complete=PrioritaryPropertyIdSet(255);
    assert!(matches!(c.resume_metric_preparation(&mut cx,&mut cache,&mut attr,&mut state,&PrioritaryPropertyIdSet(0),None),MetricPreparationStep::Prerequisites(_)));
    let MetricPreparationStep::References(_,value)=c.resume_metric_preparation(&mut cx,&mut cache,&mut attr,&mut state,&complete,None) else {panic!()};
    assert!(matches!(c.resume_metric_preparation(&mut cx,&mut cache,&mut attr,&mut state,&complete,Some(Arc::new((*value).clone()))),MetricPreparationStep::Invalidated)); assert_eq!(c.substitutions.get(),0);
    cx.included_cascade_flags=RuleCascadeFlags(1);
    assert!(matches!(c.resume_metric_preparation(&mut cx,&mut cache,&mut attr,&mut state,&complete,Some(value)),MetricPreparationStep::Invalidated));
    assert!(c.publish_prepared_metric(&mut cx,&mut cache,&mut attr,state,&complete).is_err()); assert!(c.publications.is_empty());
}

#[test]
fn terminal_excludes_losers_defaults_and_empty_chain() {
    for first in [PropertyDeclaration::Value(700),PropertyDeclaration::Wide(CSSWideKeyword::Initial),PropertyDeclaration::Wide(CSSWideKeyword::Inherit),PropertyDeclaration::Wide(CSSWideKeyword::Unset)] {
        let values=[var(PropertyDeclaration::Value(1)),first,var(PropertyDeclaration::Value(2))]; let priorities=[priority(3,3,3,1),priority(2,2,2,0),priority(1,1,1,0)]; let decls=declarations(&values,&priorities);
        let mut c=Cascade::default(); let mut cx=computed::Context::default(); let mut cache=ShorthandsWithPropertyReferencesCache; let mut attr=AttributeTracker; let complete=PrioritaryPropertyIdSet(255);
        let mut state=c.begin_metric_preparation(&cx,&decls,PrioritaryPropertyId::FontWeight);
        assert!(matches!(c.resume_metric_preparation(&mut cx,&mut cache,&mut attr,&mut state,&complete,None),MetricPreparationStep::Complete)); assert_eq!(c.substitutions.get(),0);
        assert!(c.publish_prepared_metric(&mut cx,&mut cache,&mut attr,state,&complete).is_ok()); assert_eq!(c.publications.len(),1);
    }
    let decls=declarations(&[],&[]); let mut c=Cascade::default(); let mut cx=computed::Context::default(); let mut cache=ShorthandsWithPropertyReferencesCache; let mut attr=AttributeTracker; let complete=PrioritaryPropertyIdSet(255);
    let mut state=c.begin_metric_preparation(&cx,&decls,PrioritaryPropertyId::FontWeight);
    assert!(matches!(c.resume_metric_preparation(&mut cx,&mut cache,&mut attr,&mut state,&complete,None),MetricPreparationStep::Complete));
    assert!(c.publish_prepared_metric(&mut cx,&mut cache,&mut attr,state,&complete).is_ok()); assert_eq!(c.fixups,0); assert!(c.ensured_prioritary.contains(PrioritaryPropertyId::FontWeight));
}

#[test]
fn completed_state_rejects_intervening_changes_before_publication() {
    for change in 0..5 {
        let values=[PropertyDeclaration::Value(700)]; let priorities=[priority(2,2,2,0)]; let decls=declarations(&values,&priorities);
        let mut c=Cascade::default(); let mut cx=computed::Context::default(); let mut cache=ShorthandsWithPropertyReferencesCache; let mut attr=AttributeTracker; let mut complete=PrioritaryPropertyIdSet(255);
        let id=PrioritaryPropertyId::FontWeight;
        let mut state=c.begin_metric_preparation(&cx,&decls,id);
        assert!(matches!(c.resume_metric_preparation(&mut cx,&mut cache,&mut attr,&mut state,&complete,None),MetricPreparationStep::Complete));
        match change {
            0=>cx.included_cascade_flags=RuleCascadeFlags(1),
            1=>c.seen.longhands.insert(id),
            2=>{c.reverted.longhands.insert(id,(priorities[0],RevertKind::Rule));},
            3=>c.ensured_prioritary.insert(id),
            4=>complete=PrioritaryPropertyIdSet(0),
            _=>unreachable!(),
        }
        assert!(c.publish_prepared_metric(&mut cx,&mut cache,&mut attr,state,&complete).is_err());
        assert!(c.publications.is_empty()); assert_eq!(c.fixups,0);
    }
}
