/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

pub struct Inner<'a> {
    pub value: &'a mut u32,
}
pub struct Outer<'a> {
    pub inner: Inner<'a>,
}
impl Outer<'_> {
    fn push(&mut self, value: u32) {
        *self.inner.value += value;
    }
}
fn enumerate<F: FnMut(u32)>(_callback: F) {
    unimplemented!()
}
pub fn invoke(mut value: Outer<'_>) {
    enumerate(move |input| value.push(input));
}
