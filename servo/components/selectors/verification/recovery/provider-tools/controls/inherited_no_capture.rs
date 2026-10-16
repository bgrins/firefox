/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

pub struct Holder<'a> {
    pub value: Option<&'a u32>,
}
impl<'a> Holder<'a> {
    fn current_parent(&self) -> Option<u32> {
        self.value.map(|value| *value)
    }
}
pub fn invoke(value: &Holder<'_>) -> Option<u32> {
    value.current_parent()
}
