# Reproduce

Authenticate `FREEZE.json` against the handoff digest, then run:

```
python3 artifacts/css-resolved-summary-repair-v1/check.py --scanner --output /private/tmp/resolved-summary-replay
```

Use a new output directory. The checker authenticates all manifest inputs before running generators/compiler helpers, copies the complete source closure into the output, regenerates/applies/reverses the native patch, checks WPT syntax/registration and rebuilds/runs the exact scanner offline. Python 3, Node, patch, and the pinned rustc from scanner/TOOLCHAIN.json are required. The rustc distribution's standard library and system linker are external toolchain dependencies. No repository paths or network are needed after copying this directory. Run from any working directory.

`native.patch` is the one-source-file proposal. Install `wpt/attr-resolved-unit-dependencies.html` at `testing/web-platform/tests/css/css-values/attr-resolved-unit-dependencies.html` for the root-owned browser pair. External WPT harness paths/hashes are listed in DEPENDENCIES.json. The companion is every MANIFEST entry plus MANIFEST.json and FREEZE.json; source vendor license/manifests are included. Exclude all replay output directories, objects and binaries. `REPORT.md` states exact assumptions and open gates.
