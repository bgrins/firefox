# FontFace candidate integration review

Read REPORT.md. This is a second-pass review by the original artifact producer, with exact live-original admission and static provider/publication analysis. No native build or browser execution is included.

Authenticate MANIFEST.json and check.py against externally supplied hashes, then replay from this directory:

```sh
/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -I -S -B check.py --manifest-sha <external manifest SHA256>
```

All package files are authenticated before generator execution. The pinned Python executable is checked as well. Replay regenerates candidate sources and patches in temporary directories, without native compilation or access to production source. Recorded live comparisons describe the review-time tree, not a claim about later tree state. This directory can be relocated for replay.
