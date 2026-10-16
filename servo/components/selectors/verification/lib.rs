/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

#[path = "../bloom.rs"]
pub mod bloom;

pub use bloom::BloomFilter;

pub fn new() -> BloomFilter {
    BloomFilter::new()
}

pub fn insert(filter: &mut BloomFilter, hash: u32) {
    filter.insert_hash(hash);
}

pub fn remove(filter: &mut BloomFilter, hash: u32) {
    filter.remove_hash(hash);
}

pub fn contains(filter: &BloomFilter, hash: u32) -> bool {
    filter.might_contain_hash(hash)
}

pub fn clear(filter: &mut BloomFilter) {
    filter.clear();
}
