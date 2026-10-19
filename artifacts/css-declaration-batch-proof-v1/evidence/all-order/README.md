# All shorthand logical ordering

Read REPORT.md for proved contracts and native/provider limits. Authenticate the externally supplied FREEZE/MANIFEST/checker hashes, then run:

```
python3 -I -S check.py --output /tmp/all-order-fresh-replay
```

The output path must be new and outside this capsule. MANIFEST.json plus root MANIFEST.json/FREEZE.json is the exact commit roster; generated binaries are excluded. Frozen prior artifacts are unchanged.
