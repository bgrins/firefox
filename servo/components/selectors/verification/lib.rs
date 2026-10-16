/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

extern crate self as selectors;

#[path = "../../style/bloom_recovery.rs"]
pub mod style_bloom_recovery;

#[path = "../../style/bloom_filter.rs"]
pub mod style_bloom_filter;

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

#[path = "../ancestor_hashes.rs"]
pub mod ancestor_hashes;

pub fn pack(hashes: [u32; 4], len: usize) -> ancestor_hashes::AncestorHashes {
    ancestor_hashes::AncestorHashes::from_hashes(hashes, len)
}

pub fn unpack(packed_hashes: [u32; 3]) -> u32 {
    ancestor_hashes::AncestorHashes { packed_hashes }.fourth_hash()
}

pub fn may_match(packed_hashes: [u32; 3], filter: &BloomFilter) -> bool {
    ancestor_hashes::AncestorHashes { packed_hashes }.may_match(filter)
}
