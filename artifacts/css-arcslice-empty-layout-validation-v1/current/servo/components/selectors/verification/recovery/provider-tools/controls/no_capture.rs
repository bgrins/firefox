/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

pub fn invoke<'a>(value: &'a u32) -> Option<u32> {
    Some(*value).map(|value| value)
}
