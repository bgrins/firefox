# Replay

After authenticating this review using its externally supplied FREEZE/MANIFEST hashes:

```sh
python3 artifacts/css-parser-cache-observer-independent-v1/check.py
python3 artifacts/css-parser-cache-observer-independent-v1/check.py --replay-output /private/tmp/cache-observer-review-new
```

The second command requires a new output directory. It authenticates the entire producer closure, makes a manifest-only copy, and performs full source replay plus four tamper gates. Python 3 and the pinned Rust/Lean tools are required; their paths and hashes are recorded by the producer. No Firefox build, browser, Git, network, retained native executable or .olean is used.

Exact inventories are PRODUCER-COMMIT-FILES.txt and REVIEW-COMMIT-FILES.txt. PRODUCER-PINS.json authenticates the producer roster. This is a conditional event component and source audit, not a native repair.
