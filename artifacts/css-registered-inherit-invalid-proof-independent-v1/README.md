# Independent explicit-inherit proof review

Read REVIEW.md for exact claims and limits. Recheck the retained review with:

```sh
python3 -I -S /absolute/path/to/css-registered-inherit-invalid-proof-independent-v1/check.py
```

Repeat the producer kernel replay from the authenticated manifest-only relocation:

```sh
python3 -I -S /absolute/path/to/css-registered-inherit-invalid-proof-independent-v1/relocated/check.py --output /unused/external/output
```

The latter requires the exact pinned Lean executable in relocated/TOOLCHAIN.json. It creates only external generated outputs. The review checker requires only Python standard library and does not use live native files, browser, Git or retained .olean products.
