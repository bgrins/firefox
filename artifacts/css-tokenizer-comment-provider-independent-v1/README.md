# Review replay

Authenticate this capsule's `MANIFEST.json` against `FREEZE.json`, then run:

```sh
python3 artifacts/css-tokenizer-comment-provider-independent-v1/check.py
```

The checker authenticates the exact external producer freeze and all 102 source dependencies before reading bodies, deriving theorem inventory, or checking the independent row oracle. To repeat the full source-only relocation, native debug/release runs, Lean audit/mutations and tamper gates, supply a nonexistent output path:

```sh
python3 artifacts/css-tokenizer-comment-provider-independent-v1/check.py --replay-output /private/tmp/comment-provider-review-repeat
```

`--producer` permits relocation of the unchanged producer capsule. No precompiled output is needed. Rust and Lean toolchain dependencies are the producer's pinned versions. Evidence contains this review's fresh logs and independent checks; compiled binaries/oleans and duplicated source trees are excluded. Read REPORT.md for conditional acceptance and all twelve scope dispositions.
