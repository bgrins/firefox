// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

pub enum Component {
    Value(u32),
    Nested(Vec<Component>),
}

pub trait Walk<'a>: Iterator<Item = &'a Component> {
    fn for_inner(values: &'a [Component]) -> Self;
}

fn collect_component<'a, I: Walk<'a>>(value: &'a Component, sum: &mut u32) {
    match value {
        Component::Value(hash) => *sum = sum.wrapping_add(*hash),
        Component::Nested(values) => collect_selector(I::for_inner(values), sum),
    }
}

fn collect_selector<'a, I: Walk<'a>>(iter: I, sum: &mut u32) {
    for value in iter {
        collect_component::<I>(value, sum);
    }
}

pub fn collect<'a, I: Walk<'a>>(iter: I) -> u32 {
    let mut sum = 0;
    collect_selector(iter, &mut sum);
    sum
}
