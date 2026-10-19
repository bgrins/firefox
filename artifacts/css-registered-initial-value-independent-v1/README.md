# Independent review replay

Run from any working directory:

```sh
python3 -I -S /absolute/path/to/css-registered-initial-value-independent-v1/check.py --output /private/tmp/new-initial-review-output
```

Requires Python 3 and `/usr/bin/patch`. No Git, compiler, Mach, network or browser is invoked. The checker authenticates all retained files, reconstructs the raw pair, and applies/reverses the final patch in new artifact copies. The historical provider source-only replay is retained under replay; its separate checker additionally requires Node for JavaScript syntax.

REPORT.md is the recommendation. SPEC.md records independent normative sources. The complete frozen provider capsule remains unchanged. Final runtime logs are copied inputs, not a browser rerun by this reviewer. Standalone base snapshots came from read-only Git show. No generated build targets are included.
