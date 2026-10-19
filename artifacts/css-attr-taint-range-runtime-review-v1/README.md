# Runtime evidence replay

Authenticate the external FREEZE/MANIFEST/checker hashes, then run:

```
python3 -I -S artifacts/css-attr-taint-range-runtime-review-v1/check.py
```

This checks captured evidence and exact test identities only. It does not run the retained root driver or any native/browser/build/Git operation. Read REVIEW.md for the combined-baseline and upstream-runtime boundaries.
