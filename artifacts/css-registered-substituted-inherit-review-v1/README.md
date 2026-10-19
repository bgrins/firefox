# Independent source review of substituted inherit invalidation

Read REPORT.md for the scoped recommendation and remaining root gates.

Replay with Python 3 and /usr/bin/patch; no builds, Git, browser, or third-party imports:

```
python3 -I -S /absolute/path/to/check.py --output NEW_DIRECTORY
```

Authenticate MANIFEST.json against the external handoff hash first. check.py authenticates every input before creating output, reconstructs the six original browser outcomes, and applies/reverses the exact patch on project and upstream copies. Source snapshots and retained browser evidence are inputs; this is not a rerun of Firefox.

To relocate, copy exactly the MANIFEST paths plus MANIFEST.json and FREEZE.json. Keep replay output outside this sealed directory. No generated targets are needed in the source inventory.
