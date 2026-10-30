use std::cell::{Cell, RefCell, RefMut};
use std::sync::Arc;
use std::ops::BitOr;
use std::marker::PhantomData;
type ComputedValues = usize;
#[derive(Clone)] struct Pseudos([Option<Arc<usize>>; 2]);
impl Pseudos { fn as_array(&self) -> &[Option<Arc<usize>>; 2] { &self.0 } }
#[derive(Clone)] struct ElementStyles { primary: Option<Arc<usize>>, pseudos: Pseudos }
struct ResolvedElementStyles { value: Arc<usize>, pseudos: Pseudos }
impl ResolvedElementStyles { fn primary_style(&self) -> &Arc<usize> { &self.value } }
struct ElementData { styles: ElementStyles, restyled: bool }
impl ElementData { fn has_styles(&self) -> bool { self.styles.primary.is_some() } fn set_restyled(&mut self) { self.restyled = true; } }
#[derive(Clone, Copy, PartialEq, Eq)] struct TraversalFlags(u8);
impl TraversalFlags { fn for_animation_only(&self) -> bool { self.0 == 1 } }
struct Shared { traversal_flags: TraversalFlags }
struct StyleContext<E> { shared: Shared, _element: PhantomData<E> }
#[derive(Clone, Copy, Debug)] struct RestyleHint(u8);
impl RestyleHint { const RESTYLE_CSS_ANIMATIONS: Self = Self(1); const RESTYLE_CSS_TRANSITIONS: Self = Self(2); }
impl BitOr for RestyleHint { type Output = Self; fn bitor(self, rhs: Self) -> Self { Self(self.0 | rhs.0) } }
struct ElementCascadeInputs { start: usize, value: usize, pseudos: Pseudos }
impl ElementCascadeInputs { fn new_from_resolved_styles(styles: &ResolvedElementStyles) -> Self { Self { start: *styles.value, value: *styles.value, pseudos: styles.pseudos.clone() } } }
enum RuleInclusion { All }
enum PseudoElementResolution { IfApplicable }
trait TElement: Copy {
 fn mutate_data(&self) -> Option<RefMut<'_, ElementData>>;
 fn replace_rules(&self, flags: RestyleHint, context: &mut StyleContext<Self>, inputs: &mut ElementCascadeInputs) -> bool;
 fn publish_restyle(&self, context: &mut StyleContext<Self>, data: &mut ElementData, styles: ResolvedElementStyles) -> RestyleHint;
 fn animation_update_task(&self, context: &mut StyleContext<Self>, old: &mut ElementStyles, styles: &mut ResolvedElementStyles, important: bool) -> Option<context::SequentialTask<Self>>;
 fn compose(&self, inputs: ElementCascadeInputs) -> ResolvedElementStyles;
 fn published_inputs(&self) -> ElementCascadeInputs;
     fn prepare_restyle(
        &self,
        context: &mut StyleContext<Self>,
        data: &ElementData,
        mut styles: ResolvedElementStyles,
        important_rules_changed: bool,
    ) -> (PendingRestyle<Self>, Option<crate::context::SequentialTask<Self>>) {
        let original = data.styles.clone();
        let mut animation_before = original.clone();
        let task = self.animation_update_task(
            context,
            &mut animation_before,
            &mut styles,
            important_rules_changed,
        );
        let task = task.map(|task| task.with_prepared_style(Some(styles.primary_style().clone())));
        (PendingRestyle {
            element: *self,
            original,
            publication_flags: context.shared.traversal_flags,
            styles,
        }, task)
    }
}
mod context {
 use super::*;
 pub struct SequentialTask<E> { pub element: E, pub input: Option<Arc<usize>> }
 impl<E> SequentialTask<E> { pub fn with_prepared_style(mut self, value: Option<Arc<usize>>) -> Self { self.input = value; self } }
}
struct StyleResolverForElement<E>(E);
impl<E: TElement> StyleResolverForElement<E> {
 fn new(element: E, _: &mut StyleContext<E>, _: RuleInclusion, _: PseudoElementResolution) -> Self { Self(element) }
 fn cascade_styles_with_default_parents(&mut self, inputs: ElementCascadeInputs) -> ResolvedElementStyles { self.0.compose(inputs) }
}
/// An unpublished restyle; it does not certify animation or input completion.
#[cfg(feature = "gecko")]
#[must_use]
pub struct PendingRestyle<E: TElement> {
    element: E,
    original: ElementStyles,
    publication_flags: TraversalFlags,
    styles: ResolvedElementStyles,
}

#[cfg(feature = "gecko")]
impl<E: TElement> PendingRestyle<E> {
    /// Recascade updated animation rules after external exact-target preparation.
    pub fn recascade_animation_rules(&self, context: &mut StyleContext<E>) -> ResolvedElementStyles {
        assert!(context.shared.traversal_flags.for_animation_only());
        let mut inputs = ElementCascadeInputs::new_from_resolved_styles(&self.styles);
        self.element.replace_rules(
            RestyleHint::RESTYLE_CSS_ANIMATIONS | RestyleHint::RESTYLE_CSS_TRANSITIONS,
            context,
            &mut inputs,
        );
        let mut resolver = StyleResolverForElement::new(
            self.element,
            context,
            RuleInclusion::All,
            PseudoElementResolution::IfApplicable,
        );
        resolver.cascade_styles_with_default_parents(inputs)
    }

    /// Publish once, retaining the pending work if the stored style changed.
    pub fn try_publish(
        self,
        context: &mut StyleContext<E>,
        styles: ResolvedElementStyles,
    ) -> Result<RestyleHint, (Self, ResolvedElementStyles)> {
        fn same(a: &Option<Arc<ComputedValues>>, b: &Option<Arc<ComputedValues>>) -> bool {
            match (a, b) {
                (Some(a), Some(b)) => Arc::ptr_eq(a, b),
                (None, None) => true,
                _ => false,
            }
        }
        if context.shared.traversal_flags != self.publication_flags {
            return Err((self, styles));
        }
        let element = self.element;
        let mut data = element.mutate_data();
        let Some(data) = data.as_deref_mut() else {
            return Err((self, styles));
        };
        if !same(&data.styles.primary, &self.original.primary)
            || !data.styles.pseudos.as_array().iter().zip(self.original.pseudos.as_array())
                .all(|(a, b)| same(a, b))
        {
            return Err((self, styles));
        }
        if data.has_styles() {
            data.set_restyled();
        }
        Ok(element.publish_restyle(context, data, styles))
    }
}


struct State { data: RefCell<Option<ElementData>>, root: Cell<usize>, animation: Cell<usize>, events: RefCell<Vec<String>> }
#[derive(Clone, Copy)] struct Element(&'static State);
impl TElement for Element {
 fn mutate_data(&self) -> Option<RefMut<'_, ElementData>> { RefMut::filter_map(self.0.data.borrow_mut(), |data| data.as_mut()).ok() }
 fn replace_rules(&self, flags: RestyleHint, _: &mut StyleContext<Self>, inputs: &mut ElementCascadeInputs) -> bool {
  assert_eq!(flags.0, 3);self.0.events.borrow_mut().push(format!("rules:{}", inputs.start));inputs.value = self.0.animation.get();false
 }
 fn publish_restyle(&self, _: &mut StyleContext<Self>, data: &mut ElementData, styles: ResolvedElementStyles) -> RestyleHint {
  self.0.events.borrow_mut().push("publish".into());self.0.root.set(*styles.value);data.styles=ElementStyles{primary:Some(styles.value),pseudos:styles.pseudos};RestyleHint(4)
 }
 fn animation_update_task(&self, _: &mut StyleContext<Self>, _: &mut ElementStyles, _: &mut ResolvedElementStyles, _: bool) -> Option<context::SequentialTask<Self>> {
  self.0.events.borrow_mut().push("discover".into());Some(context::SequentialTask{element:*self,input:None})
 }
 fn compose(&self, inputs: ElementCascadeInputs) -> ResolvedElementStyles {
  self.0.events.borrow_mut().push("cascade".into());ResolvedElementStyles{value:Arc::new(inputs.value),pseudos:inputs.pseudos}
 }
 fn published_inputs(&self) -> ElementCascadeInputs { let d=self.0.data.borrow();let styles=&d.as_ref().unwrap().styles;ElementCascadeInputs{start:**styles.primary.as_ref().unwrap(),value:**styles.primary.as_ref().unwrap(),pseudos:styles.pseudos.clone()} }
}
fn context(flag:u8)->StyleContext<Element>{StyleContext{shared:Shared{traversal_flags:TraversalFlags(flag)},_element:PhantomData}}
fn styles(value:usize)->ResolvedElementStyles{ResolvedElementStyles{value:Arc::new(value),pseudos:Pseudos([Some(Arc::new(2)),None])}}
fn setup()->(Element,PendingRestyle<Element>,context::SequentialTask<Element>){
 let s=styles(10);let state=Box::leak(Box::new(State{data:RefCell::new(Some(ElementData{styles:ElementStyles{primary:Some(s.value),pseudos:s.pseudos},restyled:false})),root:Cell::new(10),animation:Cell::new(0),events:RefCell::new(Vec::new())}));let element=Element(state);
 let data=state.data.borrow();let (pending,task)=element.prepare_restyle(&mut context(0),data.as_ref().unwrap(),styles(20),false);drop(data);(element,pending,task.unwrap())
}
#[test] fn prepared_tasks_do_not_publish(){let(e,_,task)=setup();assert_eq!(e.0.root.get(),10);assert!(!e.0.data.borrow().as_ref().unwrap().restyled);assert_eq!(task.input.as_deref(),Some(&20));assert_eq!(&*e.0.events.borrow(),&["discover"]);}
#[test] fn rules_use_unpublished_style_and_publish_only_final(){let(e,pending,task)=setup();e.0.events.borrow_mut().push("update".into());e.0.animation.set(*task.input.unwrap()+10);let final_style=pending.recascade_animation_rules(&mut context(1));assert_eq!(e.0.root.get(),10);assert!(pending.try_publish(&mut context(0),final_style).is_ok());assert_eq!(e.0.root.get(),30);assert_eq!(&*e.0.events.borrow(),&["discover","update","rules:20","cascade","publish"]);}
#[test] fn changed_primary_retains_work(){let(e,pending,_)=setup();e.0.data.borrow_mut().as_mut().unwrap().styles.primary=Some(Arc::new(10));assert!(pending.try_publish(&mut context(0),styles(30)).is_err());assert_eq!(e.0.root.get(),10);}
#[test] fn changed_pseudo_retains_work(){let(e,pending,_)=setup();e.0.data.borrow_mut().as_mut().unwrap().styles.pseudos.0[0]=Some(Arc::new(2));assert!(pending.try_publish(&mut context(0),styles(30)).is_err());assert_eq!(e.0.root.get(),10);}
#[test] fn missing_data_retains_work(){let(e,pending,_)=setup();*e.0.data.borrow_mut()=None;assert!(pending.try_publish(&mut context(0),styles(30)).is_err());assert_eq!(e.0.root.get(),10);}
#[test] fn wrong_publication_flags_reject(){let(e,pending,_)=setup();assert!(pending.try_publish(&mut context(1),styles(30)).is_err());assert_eq!(e.0.root.get(),10);}
#[test] #[should_panic] fn recascade_requires_animation_context(){let(_,pending,_)=setup();pending.recascade_animation_rules(&mut context(0));}
