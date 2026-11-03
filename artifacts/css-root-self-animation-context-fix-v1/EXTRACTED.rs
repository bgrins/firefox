
#![allow(dead_code)]
struct Device;
struct Stylist { device: Device }
impl Stylist { fn device(&self) -> &Device { &self.device } fn quirks_mode(&self) {} }
struct PerDocumentStyleDataImpl { stylist: Stylist }
struct ComputedValues { sentinel: u8 }
struct RuleCacheConditions;
struct ContainerSizeQuery<'a>(&'a ());
trait ElementContext {}
struct TreeCountingCaches;
struct StyleBuilder<'a> { is_root_element: bool, source: &'a ComputedValues, parent: Option<&'a ComputedValues> }
impl<'a> StyleBuilder<'a> {
    fn for_derived_style(_: &'a Device, _: Option<&'a Stylist>, style: &'a ComputedValues, parent: Option<&'a ComputedValues>) -> Self {
        Self { is_root_element: false, source: style, parent }
    }
}
struct Context<'a> { builder: StyleBuilder<'a>, smil: bool }
impl<'a> Context<'a> {
    fn new_for_animation(builder: StyleBuilder<'a>, smil: bool, _: (), _: &'a mut RuleCacheConditions, _: ContainerSizeQuery<'a>, _: &'a dyn ElementContext, _: &'a mut TreeCountingCaches) -> Self { Self { builder, smil } }
}
#[derive(Clone, Copy)]
struct Element { root: bool }
impl Element { fn is_root(&self) -> bool { self.root } }
impl ElementContext for Element {}
struct Substitution { element: Element, is_pseudo: bool }
fn create_context_for_animation<'a>(
    per_doc_data: &'a PerDocumentStyleDataImpl,
    style: &'a ComputedValues,
    parent_style: Option<&'a ComputedValues>,
    is_root_element: bool,
    for_smil_animation: bool,
    rule_cache_conditions: &'a mut RuleCacheConditions,
    container_size_query: ContainerSizeQuery<'a>,
    element_context: &'a dyn ElementContext,
    tree_counting_caches: &'a mut TreeCountingCaches,
) -> Context<'a> {
    let mut builder = StyleBuilder::for_derived_style(
        per_doc_data.stylist.device(),
        Some(&per_doc_data.stylist),
        style,
        parent_style,
    );
    builder.is_root_element = is_root_element;
    Context::new_for_animation(
        builder,
        for_smil_animation,
        per_doc_data.stylist.quirks_mode(),
        rule_cache_conditions,
        container_size_query,
        element_context,
        tree_counting_caches,
    )
}
fn keyframes(element: Element, pseudo: Option<()>) -> bool { element.is_root() && pseudo.is_none() }
fn direct(element: Element) -> bool { element.is_root() }
fn smil(element: Element) -> bool { element.is_root() }
impl Substitution { fn selected_root(&self) -> bool { self.element.is_root() && !self.is_pseudo } }

fn apply(root: bool, smil: bool, parent_present: bool) -> (bool, bool, u8, bool) {
    let data = PerDocumentStyleDataImpl { stylist: Stylist { device: Device } };
    let style = ComputedValues { sentinel: 73 };
    let parent = ComputedValues { sentinel: 91 };
    let mut conditions = RuleCacheConditions;
    let mut caches = TreeCountingCaches;
    let element = Element { root };
    let context = create_context_for_animation(&data, &style, parent_present.then_some(&parent), root, smil, &mut conditions, ContainerSizeQuery(&()), &element, &mut caches);
    (context.builder.is_root_element, context.smil, context.builder.source.sentinel, context.builder.parent.is_some())
}
#[test] fn root_keyframes_supply_identity() {
    let root = Element { root: true };
    assert!(keyframes(root, None));
    assert_eq!(apply(keyframes(root, None), false, false), (true,false,73,false));
}
#[test] fn host_pseudo_is_not_root() {
    assert!(!keyframes(Element { root: true }, Some(())));
    assert_eq!(apply(keyframes(Element { root: true }, Some(())), false, true), (false,false,73,true));
}
#[test] fn substitution_retains_target_and_pseudo_identity() {
    assert!(Substitution { element: Element { root: true }, is_pseudo: false }.selected_root());
    assert!(!Substitution { element: Element { root: true }, is_pseudo: true }.selected_root());
    assert!(!Substitution { element: Element { root: false }, is_pseudo: false }.selected_root());
}
#[test] fn direct_and_smil_use_the_actual_element() {
    for root in [false,true] {
        assert_eq!(direct(Element { root }), root);
        assert_eq!(smil(Element { root }), root);
        assert_eq!(apply(smil(Element { root }),true,false), (root,true,73,false));
    }
}
#[test] fn parent_absence_does_not_make_a_detached_element_root() {
    assert!(!keyframes(Element { root: false },None));
    assert_eq!(apply(false,false,false),(false,false,73,false));
    assert_eq!(apply(false,false,true),(false,false,73,true));
}
