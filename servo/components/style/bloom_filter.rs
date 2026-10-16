/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use selectors::bloom::BloomFilter;

/// The very rough benchmarks in the selectors crate show clear()
/// costing about 25 times more than remove_hash(). We use this to implement
/// clear() more efficiently when only a small number of hashes have been
/// pushed.
///
/// remove_hash() leaves saturated counters unchanged, even after pop() shrinks
/// the stack. Use the largest stack since clear() when choosing this fast path.
/// Each hash increments at most twice per slot, and 2 * 25 < 255.
const MEMSET_CLEAR_THRESHOLD: usize = 25;

#[inline]
pub(super) fn update_high_water(previous: usize, length: usize) -> usize {
    previous.max(length)
}

#[inline]
pub(super) fn clear_filter(filter: &mut BloomFilter, hashes: &[u32], high_water: usize) {
    if high_water > MEMSET_CLEAR_THRESHOLD {
        filter.clear();
    } else {
        for hash in hashes {
            filter.remove_hash(*hash);
        }
    }
}
