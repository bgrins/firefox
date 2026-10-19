# Independent replay

Authenticate the review MANIFEST.json and producer pins, then run from the repository root:

```sh
python3 artifacts/css-tokenizer-string-provider-independent-v1/check.py
python3 artifacts/css-tokenizer-string-provider-independent-v1/check.py --replay-output /private/tmp/string-provider-fresh-review
```

Use a new output directory for each full replay. The checker authenticates the complete producer closure before invoking its gates. Python 3, the pinned Lean 4.35.0-rc4 executable, and Rust 1.92.0 are required; the producer TOOLCHAIN.json records exact paths and identities. The source-only replay regenerates Rust witnesses, compiles actual retained helper/CowRcStr sources in debug and release, checks Lean, mutations, and authentication-before-execution failures. No Gecko build, browser, network, Git, retained executable, or retained .olean is needed.

The exact producer commit roster is PRODUCER-COMMIT-FILES.txt; the exact review roster is REVIEW-COMMIT-FILES.txt. This component has no native patch. The report explicitly preserves all twelve original obligations.
