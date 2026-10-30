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
