# Finite-depth comparison: all first reads still fail

The exact four authored callbacks remain FAIL with an OK page ending in both runs. The candidate improves some later samples; that does not satisfy these first-read tests. The original is frozen runtime `495d2c02…`, actual 81249/88aff8/0 with browser exit 1. Candidate owner actual 34257/ffd55f/1 had a successful build and an ordinary comparison failure, not an infrastructure error.

| Intermediate depth | Expected leaf | Original: first, frames 1–3 | Candidate: first, frames 1–3 |
| --- | --- | --- | --- |
| 1 | 1 | 0, 0, 0, 0 | 0, 1, 1, 1 |
| 2 | 0 | 1, 1, 1, 1 | 1, 0, 0, 0 |
| 4 | 0 | 1, 1, 1, 1 | 1, 1, 0, 0 |
| 8 | 0 | 1, 1, 1, 1 | 1, 1, 1, 1 |

All four records are complete in each arm. Both initial calibrations and every literal trajectory match the exact stepped 1000/2000 ms oracle. Raw failure messages identify the contextual first-leaf assertion, after literal assertions. The first leaf getter precedes effect timing and membership queries; the later samples each include a computed-style getter following a frame opportunity. These are neither read-free waits nor measurements of a native traversal count.

The later detailed snapshots add useful limits. Original outputs decode to new root/new first intermediate, then old outputs at every remaining stage. Candidate depths 1, 2 and 4 have all-new outputs in these later snapshots. At depth 8, root and intermediates 1–7 decode as new, while intermediate 8's font and the opacity leaf remain old. Intermediate 8 already reports CSS duration 1000 ms, applied duration 1000 ms and progress 1, yet its recorded font is 16 px instead of the fixed oracle's 32 px. The leaf reports opacity 1. Thus equal CSS/applied durations alone do not establish fresh rendered composition. This is a later sequential collection, not a simultaneous snapshot or proof of the state during the first getter.

Before/after membership snapshots are equal, and all retained animation/effect identities are current in both arms. This bounds the observed intervention; it does not prove that membership queries are incapable of causing other work. No queue-state, native pass count, per-frame propagation law, eventual depth-8 recovery or starvation conclusion follows from these records. The parity model supplies an output encoding; its abstract rounds are not native passes. The general DAG completion model's full-batch premises remain external implementation obligations.

`replay.py` replays the frozen original and candidate raw streams through the exact assessors, verifies complete private records and their existing comparison, initial/literal numeric calibrations, candidate three-source build/binary joins, WPT metadata and PRE/POST equality, and cleanup receipts. Actual saved replay 366d91/0 passed; final frozen replay is recorded in CHECK.json. It reads only completed owner files and writes REPLAY.json here. It does not execute a live guard or independently inspect the app/worktree. Root verifier 76336/a6b1a8/0 separately verified restored sources/app and deleted the verified 1,008,605,176-byte retained backup. Frozen runtime seal 7439b1de… authenticates all 60 regular payloads (85059a/0). The linked refresh changes only the raw-index observation, with no acceptance increment. This saved receipt authentication is not a second live-state verification by this reviewer.

The inherited comparison diagnostic says “all 32 authored callbacks across the two target fixtures must pass.” This is stale wording from the shared assessor. Actual policy, raw stream, replay and records have four callbacks on one page. The saved error is preserved verbatim; its text neither changes cardinality nor reclassifies the four ordinary assertion failures. The collector's `numeric_or_convergence_oracle: false` describes structural collection only; authored numeric assertions and the separate calibration check still apply.

No fixture, frozen result, native source, app or canonical state was modified. No native acceptance or new bug count is claimed.
