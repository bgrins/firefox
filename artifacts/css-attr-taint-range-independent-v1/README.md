# Review integrity and replay

Authenticate externally supplied FREEZE, MANIFEST and checker hashes, then run:

```
python3 -I -S artifacts/css-attr-taint-range-independent-v1/check.py
```

This authenticates this closed review, source copies and retained receipts. It does not run Lean/Rust or a browser. To repeat the producer proof replay, authenticate its hashes in PRODUCER.json, copy manifest-listed files plus both seals, and run the copied checker with a new external output directory as documented in its README. That separate source-only replay requires the pinned Lean and Rust tools. Both the proof source and copied source remain unchanged.

Root browser evidence is retained as received; the reviewer did not run it. The candidate browser outcome remains a separate root gate. REPLAY logs include exact commands; completed owned output was removed after preserving logs and generated Rust text.
