/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

fn enumerate<F: FnMut(u32)>(_callback: F) {
    unimplemented!()
}
pub fn invoke(value: &mut u32) {
    let mut inner = |input| *value += input;
    enumerate(move |input| inner(input));
}
