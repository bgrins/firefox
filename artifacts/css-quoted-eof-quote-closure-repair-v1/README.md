# Quoted-string EOF repair component

Read `REPORT.md` for the exact proved and admitted boundaries. No Gecko build/browser acceptance is claimed.

Authenticate `FREEZE.json` by its communicated hash, then authenticate `MANIFEST.json` and `check.py` against its fields before executing the checker. The checker authenticates every input before invoking helpers, Rust or Lean. Replay writes only to a new output directory:

```sh
python3 check.py --output /private/tmp/quoted-eof-replay-NEW
```

`--auth-only` authenticates without tool execution. The two pinned tool installations are dependencies named in `TOOLCHAIN.json`; no network or tool installation is needed. `native.patch` is the standalone pre-endpoint proposal. `integration/native.patch` is the exact adaptation on the preserved formatted endpoint proposal. No WPT is included in either native patch; root owns the independent WPT/commit packaging.

The source inventory excludes `.olean` files and development outputs. Native dependencies and original/candidate source are included. Replay rebuilds every executable from source, audits every declared theorem, rejects two false-model mutants, checks patch apply/reverse and source composition, and runs exact-source original/candidate/native mutants in all three configurations. The fixed finite matrix retains unrelated failures rather than narrowing its expected results.
