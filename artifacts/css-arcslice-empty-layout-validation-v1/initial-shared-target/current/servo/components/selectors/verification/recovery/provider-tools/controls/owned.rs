/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

pub struct Sink {
    pub value: u32,
    pub count: usize,
}
impl Sink {
    fn push(&mut self, hash: u32) {
        self.count += 1;
        self.value += hash;
    }
}
fn enumerate<F: FnMut(u32)>(_callback: F) {
    unimplemented!()
}
pub fn invoke(sink: &mut Sink) {
    enumerate(|hash| sink.push(hash));
}
