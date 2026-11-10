# Animation timeline renewal source gates

Read `REPORT.md` for the conditional source result and the distinct animation-taint hypothesis. `animation-tainted-timeline-calibration.html` is a four-callback WPT preparation, not a browser result. The parent owns runtime testing and any live installation.

Replay without changing source or the live WPT tree:

```sh
python3 -I artifacts/css-animation-timeline-renewal-gates-20261110-v1/check_sources.py SOURCE-CHECK-replay.json
python3 -I artifacts/css-animation-timeline-renewal-gates-20261110-v1/check_wpt.py check-replay
```

Output names must be fresh. `SOURCE-CHECK2.json` records source and spec authentication. `check2` is the authoritative lint/syntax/manifest preparation; `check1` retains the pre-rename check. The JavaScript registration check does not invoke browser callbacks.

`FILES.json` freezes capsule bytes except itself and `FINAL.json`; `FINAL.json` pins that manifest and records actual check exits. Do not infer browser conformance, stale-registry behavior, or convergence from preparation checks.
