Authenticate the handoff FREEZE.json and MANIFEST.json first. Replay:

```
python3 check.py --lean /absolute/path/to/pinned/lean --output /absolute/new/path
```

The checker authenticates this review, the384-file original component and the provider addendum before invoking imported helpers. It performs a fresh source-only native/Lean replay. Outputs stay under the new directory; no live source, browser, Mach or Git changes. REPORT.md states the conditional/original-source boundary. Generated object files are excluded from the source manifest.
