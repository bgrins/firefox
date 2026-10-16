// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

pub trait Value {
    fn value(&self) -> u32;
}

pub trait Pair {
    type Left: Value;
    type Right: Value;
    fn left(&self) -> &Self::Left;
    fn right(&self) -> &Self::Right;
}

pub fn collect<T: Pair>(pair: &T) -> u32 {
    pair.left().value().wrapping_add(pair.right().value())
}
