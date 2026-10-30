use std::ops;
use std::sync::Arc;
use std::cell::{Cell, RefCell};
use std::rc::Rc;

type ComputedValues = usize;
type UpdateAnimationsTasks = u8;
struct ThreadState;
impl ThreadState { const LAYOUT: Self = Self; fn contains(&self, _: Self) -> bool { true } }
mod thread_state { pub fn get() -> super::ThreadState { super::ThreadState } }
pub trait TElement {
    fn update_animations(&self, before: Option<Arc<ComputedValues>>, tasks: UpdateAnimationsTasks);
    fn update_animations_with_style(&self, before: Option<Arc<ComputedValues>>, after: Option<Arc<ComputedValues>>, tasks: UpdateAnimationsTasks);
}
pub struct SendElement<E>(E);
impl<E> SendElement<E> { unsafe fn new(element: E) -> Self { Self(element) } }
impl<E> ops::Deref for SendElement<E> { type Target = E; fn deref(&self) -> &E { &self.0 } }
/// The style input selected for a main-thread animation task.
#[cfg(feature = "gecko")]
pub enum AnimationTaskStyle {
    /// Read the published primary style when the task executes.
    Published,
    /// Use an owned prepared style, or cancel for an unstyled target.
    Prepared(Option<Arc<ComputedValues>>),
}

/// A task to be run in sequential mode on the parent (non-worker) thread. This
/// is used by the style system to queue up work which is not safe to do during
/// the parallel traversal.
pub enum SequentialTask<E: TElement> {
    /// Entry to avoid an unused type parameter error on servo.
    Unused(SendElement<E>),

    /// Performs one of a number of possible tasks related to updating
    /// animations based on the |tasks| field. These include updating CSS
    /// animations/transitions that changed as part of the non-animation style
    /// traversal, and updating the computed effect properties.
    #[cfg(feature = "gecko")]
    UpdateAnimations {
        /// The target element or pseudo-element.
        el: SendElement<E>,
        /// The before-change style for transitions. We use before-change style
        /// as the initial value of its Keyframe. Required if |tasks| includes
        /// CSSTransitions.
        before_change_style: Option<Arc<ComputedValues>>,
        /// The after-change style source for this task.
        style: AnimationTaskStyle,
        /// The tasks which are performed in this SequentialTask.
        tasks: UpdateAnimationsTasks,
    },
}

impl<E: TElement> SequentialTask<E> {
    /// Executes this task.
    pub fn execute(self) {
        use self::SequentialTask::*;
        debug_assert!(thread_state::get().contains(ThreadState::LAYOUT));
        match self {
            Unused(_) => unreachable!(),
            #[cfg(feature = "gecko")]
            UpdateAnimations {
                el,
                before_change_style,
                style,
                tasks,
            } => match style {
                AnimationTaskStyle::Published => el.update_animations(before_change_style, tasks),
                AnimationTaskStyle::Prepared(style) => {
                    el.update_animations_with_style(before_change_style, style, tasks);
                },
            },
        }
    }

    /// Creates a task to update various animation-related state on a given
    /// (pseudo-)element.
    #[cfg(feature = "gecko")]
    pub fn update_animations(
        el: E,
        before_change_style: Option<Arc<ComputedValues>>,
        tasks: UpdateAnimationsTasks,
    ) -> Self {
        use self::SequentialTask::*;
        UpdateAnimations {
            el: unsafe { SendElement::new(el) },
            before_change_style,
            style: AnimationTaskStyle::Published,
            tasks,
        }
    }

    /// Select an owned style for execution after the preparing traversal ends.
    #[cfg(feature = "gecko")]
    pub fn with_prepared_style(mut self, after_change_style: Option<Arc<ComputedValues>>) -> Self {
        match &mut self {
            Self::UpdateAnimations { style, .. } => {
                *style = AnimationTaskStyle::Prepared(after_change_style);
            },
            Self::Unused(_) => unreachable!(),
        }
        self
    }
}

/// A list of SequentialTasks that get executed on Drop.
pub struct SequentialTaskList<E>(Vec<SequentialTask<E>>)
where
    E: TElement;

impl<E: TElement> SequentialTaskList<E> {
    /// Transfer tasks without running them while traversal contexts are alive.
    pub fn take_tasks(&mut self) -> Vec<SequentialTask<E>> {
        std::mem::take(&mut self.0)
    }
}

impl<E> ops::Deref for SequentialTaskList<E>
where
    E: TElement,
{
    type Target = Vec<SequentialTask<E>>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<E> ops::DerefMut for SequentialTaskList<E>
where
    E: TElement,
{
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}

impl<E> Drop for SequentialTaskList<E>
where
    E: TElement,
{
    fn drop(&mut self) {
        debug_assert!(thread_state::get().contains(ThreadState::LAYOUT));
        for task in self.0.drain(..) {
            task.execute()
        }
    }
}

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
fn transfer(mut scoped_tls: ScopedTLS, root: usize) -> (usize, Vec<SequentialTask<Element>>) {
    let mut tasks = Vec::new();
    for slot in scoped_tls.slots() {
        if let Some(context) = slot.get_mut() {
            tasks.extend(context.tasks.take_tasks());
        }
    }
    drop(scoped_tls);
    (root, tasks)
}
