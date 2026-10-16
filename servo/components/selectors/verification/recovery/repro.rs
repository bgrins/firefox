/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

pub trait Step {
    fn step(&mut self);
}
pub struct Borrowed<'a> {
    pub value: &'a mut usize,
    pub owned: usize,
}
impl Step for Borrowed<'_> {
    fn step(&mut self) {
        *self.value += 1;
        self.owned += 1;
    }
}
pub fn generic<S: Step>(state: &mut S) {
    state.step();
}
pub fn invoke(state: &mut Borrowed<'_>) {
    generic(state);
}
