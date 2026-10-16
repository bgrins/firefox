/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

fn generic<T>(value: &mut u32, output: T) -> T {
    *value += 1;
    output
}
pub fn invoke(value: &mut u32) {
    generic(value, ())
}
