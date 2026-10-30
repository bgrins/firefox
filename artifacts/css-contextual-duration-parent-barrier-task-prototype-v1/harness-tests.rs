#[derive(Default)]
struct Shared {
    current: RefCell<Option<Arc<usize>>>,
    live_contexts: Cell<usize>,
    calls: RefCell<Vec<(usize, Option<usize>, Option<usize>, u8)>>,
}
#[derive(Clone)]
struct Element { id: usize, state: Rc<Shared> }
impl TElement for Element {
    fn update_animations(&self, before: Option<Arc<usize>>, tasks: u8) {
        let current = self.state.current.borrow().clone();
        self.update_animations_with_style(before, current, tasks);
    }
    fn update_animations_with_style(&self, before: Option<Arc<usize>>, after: Option<Arc<usize>>, tasks: u8) {
        assert_eq!(self.state.live_contexts.get(), 0, "task ran before all contexts dropped");
        self.state.calls.borrow_mut().push((self.id, before.as_deref().copied(), after.as_deref().copied(), tasks));
    }
}
struct Guard(Rc<Shared>);
impl Drop for Guard { fn drop(&mut self) { self.0.live_contexts.set(self.0.live_contexts.get() - 1); } }
struct Context { _guard: Guard, tasks: SequentialTaskList<Element> }
struct ScopedTLS(Vec<RefCell<Option<Context>>>);
impl ScopedTLS { fn slots(&mut self) -> &mut [RefCell<Option<Context>>] { &mut self.0 } }
fn element(id: usize, state: &Rc<Shared>) -> Element { Element { id, state: state.clone() } }
fn task(id: usize, state: &Rc<Shared>) -> SequentialTask<Element> { SequentialTask::update_animations(element(id, state), Some(Arc::new(3)), 5) }

#[test]
fn published_input_stays_late_bound() {
    let state = Rc::new(Shared::default());
    *state.current.borrow_mut() = Some(Arc::new(7));
    let pending = task(1, &state);
    *state.current.borrow_mut() = Some(Arc::new(9));
    pending.execute();
    assert_eq!(*state.calls.borrow(), [(1, Some(3), Some(9), 5)]);
}
#[test]
fn prepared_input_owns_value_without_reading_published_data() {
    let state = Rc::new(Shared::default());
    let value = Arc::new(42);
    let pending = task(1, &state).with_prepared_style(Some(value.clone()));
    assert_eq!(Arc::strong_count(&value), 2);
    drop(value);
    let _exclusive_published_borrow = state.current.borrow_mut();
    pending.execute();
    assert_eq!(*state.calls.borrow(), [(1, Some(3), Some(42), 5)]);
}
#[test]
fn prepared_null_is_not_fallback_to_published() {
    let state = Rc::new(Shared::default());
    *state.current.borrow_mut() = Some(Arc::new(99));
    let pending = task(1, &state).with_prepared_style(None);
    let _exclusive_published_borrow = state.current.borrow_mut();
    pending.execute();
    assert_eq!(*state.calls.borrow(), [(1, Some(3), None, 5)]);
}
#[test]
fn all_contexts_drop_before_ordered_tasks_execute() {
    let state = Rc::new(Shared::default());
    state.live_contexts.set(2);
    let slots = vec![
        RefCell::new(Some(Context { _guard: Guard(state.clone()), tasks: SequentialTaskList(vec![task(1, &state), task(2, &state)]) })),
        RefCell::new(None),
        RefCell::new(Some(Context { _guard: Guard(state.clone()), tasks: SequentialTaskList(vec![task(3, &state)]) })),
    ];
    let (root, tasks) = transfer(ScopedTLS(slots), 17);
    assert_eq!(root, 17);
    assert_eq!(state.live_contexts.get(), 0);
    assert!(state.calls.borrow().is_empty());
    for task in tasks { task.execute(); }
    assert_eq!(state.calls.borrow().iter().map(|call| call.0).collect::<Vec<_>>(), [1, 2, 3]);
}
#[test]
fn extraction_empties_drop_owner_and_executes_once() {
    let state = Rc::new(Shared::default());
    let mut list = SequentialTaskList(vec![task(1, &state)]);
    let tasks = list.take_tasks();
    assert!(list.is_empty());
    drop(list);
    assert!(state.calls.borrow().is_empty());
    for task in tasks { task.execute(); }
    assert_eq!(state.calls.borrow().len(), 1);
}
#[test]
fn untransferred_list_retains_legacy_drop_execution() {
    let state = Rc::new(Shared::default());
    drop(SequentialTaskList(vec![task(1, &state)]));
    assert_eq!(state.calls.borrow().len(), 1);
}
