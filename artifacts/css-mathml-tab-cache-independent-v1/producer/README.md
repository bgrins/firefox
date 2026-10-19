# MathML tab-cache design

Read `REPORT.md`. The root-owned baseline confirms four calibrated glyph-range discrepancies. The proposed repair and WPT-style regression have not been built or run.

Authenticate/replay the independent review with Python 3.9 or newer, from any working directory:

```
python3 -I -S -B /absolute/path/to/capsule/check.py --manifest-sha HANDOFF_SHA256
```

Use the digest from the independent handoff. The checker authenticates all source/evidence/proposal files before importing local helpers, repeats the raw receipt adjudication, and checks the exact sole-function patch. It needs no browser, compiler, network or live Gecko checkout. Node syntax checking is recorded separately; it is not runtime validation.

Root owns final patch application, formatting, standalone/base verification, paired native/WPT testing and acceptance. Original full ownership, partition and persistent-cache obligations remain open.
