/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

pub trait State {
    fn step(&mut self);
}
pub struct Storage<'a> {
    pub value: &'a mut usize,
}
impl State for Storage<'_> {
    fn step(&mut self) {
        *self.value += 1;
    }
}
pub fn advance<S: State>(state: &mut S, mut count: usize) {
    while count > 0 {
        state.step();
        count -= 1;
    }
}
pub fn invoke(state: &mut Storage<'_>, count: usize) {
    advance(state, count);
}
