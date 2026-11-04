// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

pub trait Data {
    type Atom;
    fn hash(atom: &Self::Atom) -> u32;
}

pub struct Component<I: Data>(I::Atom);

pub trait Walk<'a>: Iterator<Item = &'a Component<Self::Impl>> {
    type Impl: Data + 'a;
}

pub fn collect<'a, It: Walk<'a>>(iter: It) -> u32 {
    let mut sum = 0u32;
    for value in iter {
        sum = sum.wrapping_add(It::Impl::hash(&value.0));
    }
    sum
}
