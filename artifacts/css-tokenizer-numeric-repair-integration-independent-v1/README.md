# Independent numeric integration review

Authenticate the communicated FREEZE, MANIFEST and checker hashes, then run:

```sh
python3 check.py
python3 check.py --replay --output /private/tmp/numeric-integration-independent-fresh
```

The second command requires a new output directory and the pinned Lean/Rust toolchains. It authenticates this package and its copied producer before invoking any retained helper. All input sources are included; no network, Firefox/Mach build or browser is needed. See REPORT.md for the exact conditional acceptance and retained trust boundaries. `replay/` and replay.log are local generated outputs excluded from the closed source inventory; evidence contains the retained results of that run.
