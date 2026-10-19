# Animation endpoint proposal

Read `REPORT.md`, especially standalone dependencies. No candidate compile or runtime acceptance is claimed.

Authenticate the external freeze digest, then run:

```
python3 -I -S check.py --checks
```

Requires Python 3, Node for syntax checks and `patch`. It verifies all retained bytes before any subprocess, checks historical raw results, reconstructs patches and applies/reverses them only in automatically removed temporary copies. It never edits the Firefox tree or runs a browser/build.

The stack package changes three native files and adds the proposed CSS-wide test. The separate upstream package adds one explicitly identified map-taint prerequisite already fixed in the current stack. The old typed probe remains regression evidence and depends on earlier keyframe computation support.
