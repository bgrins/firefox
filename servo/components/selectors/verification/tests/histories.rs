/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use stylo_bloom_verification::{clear, contains, insert, new, remove, BloomFilter};

const HASHES: [u32; 5] = [0, 1, 0x1000, 0x1001, 0x0100_0000];

#[derive(Clone, Copy, Debug)]
enum Operation {
    Insert(usize),
    Remove(usize),
    Clear,
}

fn counts(live: &[usize; 5]) -> [usize; 2] {
    [2 * live[0] + live[1] + live[2] + 2 * live[4], live[1] + live[2] + 2 * live[3]]
}

fn explore(
    filter: &BloomFilter,
    live: [usize; 5],
    mut saturated: [bool; 2],
    remaining: usize,
    history: &mut Vec<Operation>,
) -> usize {
    let contributions = counts(&live);
    for slot in 0..2 {
        saturated[slot] |= contributions[slot] >= 255;
        let hash = slot as u32 | ((slot as u32) << 12);
        assert_eq!(
            contains(filter, hash),
            saturated[slot] || contributions[slot] != 0,
            "history {history:?}, live {live:?}, slot {slot}"
        );
    }
    for (index, hash) in HASHES.iter().enumerate() {
        if live[index] != 0 {
            assert!(contains(filter, *hash), "history {history:?}, live {live:?}");
        }
    }
    if remaining == 0 {
        return 1;
    }
    let operations = (0..5).map(Operation::Insert)
        .chain((0..5).filter(|&i| live[i] != 0).map(Operation::Remove))
        .chain(std::iter::once(Operation::Clear));
    let mut visited = 1;
    for operation in operations {
        let mut next = filter.clone();
        let mut next_live = live;
        let mut next_saturated = saturated;
        match operation {
            Operation::Insert(i) => {
                insert(&mut next, HASHES[i]);
                next_live[i] += 1;
            }
            Operation::Remove(i) => {
                remove(&mut next, HASHES[i]);
                next_live[i] -= 1;
            }
            Operation::Clear => {
                clear(&mut next);
                next_live.fill(0);
                next_saturated.fill(false);
            }
        }
        history.push(operation);
        visited += explore(&next, next_live, next_saturated, remaining - 1, history);
        history.pop();
    }
    visited
}

#[test]
fn exhaustive_valid_operation_histories() {
    let mut visited = 0;
    for live in [
        [0, 0, 0, 0, 0],
        [127, 0, 0, 0, 0],
        [126, 1, 0, 0, 0],
        [128, 0, 0, 0, 0],
        [0, 254, 0, 0, 0],
    ] {
        let mut filter = new();
        for (index, count) in live.iter().enumerate() {
            for _ in 0..*count {
                insert(&mut filter, HASHES[index]);
            }
        }
        visited += explore(&filter, live, [false; 2], 5, &mut Vec::new());
    }
    assert_eq!(visited, 148602);
}
