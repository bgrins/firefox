# Replay

Authenticate `MANIFEST.json` against `FREEZE.json` before executing the checker. Then run:

```sh
python3 artifacts/css-quoted-eof-offset-design-v1/check.py --output /private/tmp/quoted-eof-offset-clean
```

The output directory must not exist. The checker authenticates every input before loading helpers, regenerates the exact candidate, rebuilds cssparser and the extracted original/candidate/mutant offline, checks the 40 rows, audits all ten Lean theorem names, rejects the Lean mutation, and verifies source tampering fails before helper execution. Rust and Lean binaries are external pinned toolchain dependencies; no network, Gecko build, shared browser or Git operations occur.

Commit the manifest-listed source inputs plus `MANIFEST.json`, `FREEZE.json`, and the separately retained producer replay receipt. Exclude generated binaries, rlibs, `__pycache__`, and temporary replay trees. `native.patch` is a proposal for a separate native+WPT repair; the complete snapshots are proof inputs, not production edits.
