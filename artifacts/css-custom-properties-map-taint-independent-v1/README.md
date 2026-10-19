# Static review replay

Authenticate the externally supplied freeze/manifest/checker hashes, then run:

```sh
python3 -I -S artifacts/css-custom-properties-map-taint-independent-v1/check.py
```

This checks closed source identity, the exact two-site proposal, complete source bindings and the retained nine-case root baseline. It executes no native compiler, browser, WPT or Git operation. `proposed.patch` and `candidate/` are unapplied source proposals; root owns runtime acceptance. The checker writes no files.
