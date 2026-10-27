# Original-2 saved evidence review

**PASS as a complete original observation; no native fix acceptance.** The wrapper exits 0 while WPT exits 1 for the expected baseline assertions. The sealed capsule, raw JSONL and assessment agree exactly.

| Group | PASS | FAIL |
|---|---:|---:|
| Corrected attr-cycle targets |34|3|
| New raw/EOF targets |22|14|
| Unchanged regression assertions |329|0|
| Reftests |6|0|

All 13 failures from original-1 remain. The sole outcome change among existing identities is `CSS Values and Units Test: attr 28`, PASS to FAIL, caused by the explicit EOF oracle correction. The seven added controls contribute three failures and four passes:

| Added control | Original-2 |
|---|---|
| eof-bare-self | FAIL |
| eof-raw-string-self | FAIL |
| eof-typed-self | PASS |
| eof-nested-type-self | PASS |
| raw-self-with-valid-trailing-value | FAIL |
| raw-self-with-invalid-string-trailing-value | PASS |
| raw-self-with-unmatched-closing-token | PASS |

The complete failure roster is retained with raw assertion messages in AUDIT.json:

- `attr-cycle.html` — `CSS Values and Units Test: attr 3`
- `attr-cycle.html` — `CSS Values and Units Test: attr 28`
- `attr-cycle.html` — `CSS Values and Units Test: attr 29`
- `attr-raw-nested-cycle.html` — `typed-self-bare`
- `attr-raw-nested-cycle.html` — `typed-self-raw`
- `attr-raw-nested-cycle.html` — `nested-bare`
- `attr-raw-nested-cycle.html` — `nested-raw`
- `attr-raw-nested-cycle.html` — `typed-string-self-bare`
- `attr-raw-nested-cycle.html` — `typed-typed-raw-chain`
- `attr-raw-nested-cycle.html` — `numeric-self-uses-literal-fallback`
- `attr-raw-nested-cycle.html` — `invalid-number-fallback-typed-cycle`
- `attr-raw-nested-cycle.html` — `invalid-number-fallback-property-cycle`
- `attr-raw-nested-cycle.html` — `eof-bare-self`
- `attr-raw-nested-cycle.html` — `eof-raw-string-self`
- `attr-raw-nested-cycle.html` — `raw-self-with-valid-trailing-value`
- `attr-raw-nested-cycle.html` — `Mutating between raw reads and typed cycles updates the result`
- `attr-raw-nested-cycle.html` — `Mutating a raw primary selects or excludes a typed cyclic fallback`

Saved pre/post records are exactly equal for root and nested indices and confirm source, binary and research preservation. The saved epoch pins the correct compiled original source role, both normal binaries, HEAD `bb88e8e6b31de9b832e896110e39504d68020c71`, and application BuildID `20261027161407`. The build-published epoch exactly equals the WPT epoch. Application metadata bytes, resolved symlink target and identities match pre/post records and actual WPT run_info. All copied test, metadata, reference and configuration hashes match their pins. The unchanged regression outcome/expectation/intermittent signatures exactly match original-1.

The saved cleanup records report the owned group absent and temporary profile root removed. The original build child exits 0 and logs success at 42.45 seconds. Its output includes four non-fatal `KeyError: export` progress-monitor exceptions, explicitly preserved in BUILD-LOG-NOTE.json; this review does not claim an exception-free build log.

Full preservation is supported by authenticated saved wrapper/build records and the epoch inventory: 1,224 pins, 45 installed identities, 50 modified native paths, 15 untracked native paths and 12,691 committed research payloads. This review does not recalculate live repository or binary state during the candidate transition. It imports the sealed pure assessment checks to independently reassess raw events and authenticates the saved owned files. No browser, build, live native/epoch query or source/Git mutation occurred.

Candidate validation remains outstanding. It must pass all 73 target assertions and preserve all 329 regression assertions and six reftests under the same capsule and frozen HEAD.
