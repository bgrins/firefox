/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

fn apply<F: Fn(u32) -> u32>(_callback: F) -> u32 {
    unimplemented!()
}
pub fn invoke(value: &u32) -> u32 {
    apply(|input| *value + input)
}
