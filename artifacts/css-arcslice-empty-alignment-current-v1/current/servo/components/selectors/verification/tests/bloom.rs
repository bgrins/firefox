/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use stylo_bloom_verification::{clear, contains, insert, new, remove};

#[test]
fn saturation_and_collisions_preserve_membership() {
    for hash in [0, 1, 0x0000_1001, 0x00ff_ffff, u32::MAX] {
        let mut filter = new();
        for _ in 0..300 {
            insert(&mut filter, hash);
        }
        for _ in 0..299 {
            remove(&mut filter, hash);
            assert!(contains(&filter, hash));
        }
        clear(&mut filter);
        assert!(!contains(&filter, hash));
    }
}

#[test]
fn colliding_removals_preserve_other_members() {
    let hashes = [0, 1, 0x1000, 0x1001, 0x0100_0000, u32::MAX];
    let mut filter = new();
    for hash in hashes {
        insert(&mut filter, hash);
    }
    for (index, hash) in hashes.iter().enumerate() {
        remove(&mut filter, *hash);
        for remaining in &hashes[index + 1..] {
            assert!(contains(&filter, *remaining));
        }
    }
}
