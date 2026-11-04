/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

pub trait Step {
    fn step(&mut self);
}
pub struct Borrowed<'a: 'b, 'b: 'a> {
    pub first: &'a mut usize,
    pub second: &'b mut usize,
    pub owned: usize,
}
impl Step for Borrowed<'_, '_> {
    fn step(&mut self) {
        *self.first += 1;
        *self.second += 1;
        self.owned += 1;
    }
}
pub fn generic<S: Step>(state: &mut S) {
    state.step();
}
pub fn invoke(state: &mut Borrowed<'_, '_>) {
    generic(state);
}
