# Independent review replay

Authenticate this review's externally supplied FREEZE/MANIFEST/checker hashes, then run `python3 -I -S check.py`. This authenticates the closed review and its retained receipts; it does not rerun Lean.

To repeat the actual proof replay, authenticate the producer hashes in PRODUCER.json, copy only its MANIFEST-listed files plus MANIFEST.json and FREEZE.json into a fresh directory, then run:

```
python3 -I -S /absolute/copied-producer/check.py --output /absolute/new/external/output
```

The producer's pinned Lean toolchain must be present. See its README/SCOPE for trust boundaries. This review retained every generated command log and CHECK.json, then removed only its completed owned output directory. Its authenticated copied source remains in the separate development directory.
