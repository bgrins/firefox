// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

pub enum Component {
    Attribute(Box<u32>),
    Other,
}

pub fn collect(component: &Component) -> u32 {
    match component {
        Component::Attribute(value) => **value,
        Component::Other => 0,
    }
}
