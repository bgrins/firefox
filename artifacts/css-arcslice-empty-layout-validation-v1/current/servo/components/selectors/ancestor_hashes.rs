/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use crate::bloom::{BLOOM_HASH_MASK, BloomFilter};

/// Ancestor hashes for the bloom filter. We precompute these and store them
/// inline with selectors to optimize cache performance during matching.
/// This matters a lot.
///
/// We use 4 hashes, which is copied from Gecko, who copied it from WebKit.
/// Note that increasing the number of hashes here will adversely affect the
/// cache hit when fast-rejecting long lists of Rules with inline hashes.
///
/// Because the bloom filter only uses the bottom 24 bits of the hash, we pack
/// the fourth hash into the upper bits of the first three hashes in order to
/// shrink Rule (whose size matters a lot). This scheme minimizes the runtime
/// overhead of the packing for the first three hashes (we just need to mask
/// off the upper bits) at the expense of making the fourth somewhat more
/// complicated to assemble, because we often bail out before checking all the
/// hashes.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct AncestorHashes {
    pub packed_hashes: [u32; 3],
}

impl AncestorHashes {
    pub(crate) fn from_hashes(mut hashes: [u32; 4], len: usize) -> Self {
        // Now, pack the fourth hash (if it exists) into the upper byte of each of
        // the other three hashes.
        if len == 4 {
            let fourth = hashes[3];
            hashes[0] |= (fourth & 0x000000ff) << 24;
            hashes[1] |= (fourth & 0x0000ff00) << 16;
            hashes[2] |= (fourth & 0x00ff0000) << 8;
        }

        AncestorHashes {
            packed_hashes: [hashes[0], hashes[1], hashes[2]],
        }
    }

    /// Returns the fourth hash, reassembled from parts.
    pub fn fourth_hash(&self) -> u32 {
        ((self.packed_hashes[0] & 0xff000000) >> 24)
            | ((self.packed_hashes[1] & 0xff000000) >> 16)
            | ((self.packed_hashes[2] & 0xff000000) >> 8)
    }

    #[inline(always)]
    pub(crate) fn may_match(&self, bf: &BloomFilter) -> bool {
        // Check the first three hashes. A zero packed word conservatively stops
        // rejection, even if later hashes are nonzero. Defer unpacking the fourth
        // hash until we actually reach it, because we usually don't.
        //
        // To be clear: this is all extremely hot.
        for packed in &self.packed_hashes {
            if *packed == 0 {
                // No more hashes left - unable to fast-reject.
                return true;
            }

            if !bf.might_contain_hash(*packed & BLOOM_HASH_MASK) {
                // Hooray! We fast-rejected on this hash.
                return false;
            }
        }

        // Now do the slighty-more-complex work of synthesizing the fourth hash,
        // and check it against the filter if it exists.
        let fourth = self.fourth_hash();
        fourth == 0 || bf.might_contain_hash(fourth)
    }
}
