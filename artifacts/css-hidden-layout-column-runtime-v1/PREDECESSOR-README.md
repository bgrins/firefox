# Compact hidden-layout experiment v3 — unprepared draft

This additive successor preserves v1/v2. Do not prepare or execute until root reviews this driver, accepts the independently reviewed cost-v2 inputs, confirms prior restoration, and completes signing. No INPUTS or native snapshots have been captured.

The six uninstrumented phases, exact six-file/58-test roster, original-key pair, optional two trace phases/12 tests, 21 native write targets, 26 guards, nine absent temporary paths, and restoration protocol remain unchanged from v2. Retained v2 README is available as PREDECESSOR-README.md. Tests and selected native source copies remain byte-identical.

`--with-timings` adds one fresh local process after WPT only in baseline, principal-only, oof-only, and both. It never measures either original-key phase or either instrumented trace phase. `--with-traces` remains independently optional. All six cost execution inputs, including cleanup.py, are copied and pinned. Preparation still occurs only after the root supplies the actual post-signing HEAD.

The parent independently checks native, binary, resource and fixture pins around each timing run; authenticates the runner's full pin map; and requires successful leader termination/reaping, verified no live original-group members, empty cleanup errors, and profile removal. An absent or uncertain cleanup receipt aborts further phases and enters restoration. A measurement timeout/calibration failure may continue only after these cleanup and integrity gates pass. A zero runner exit additionally requires independently reconstructed validator summary equality. Geometry discrepancies remain descriptive data, never normalized to passing correctness.

The cost fixture separates first query, same-leaf repeat, distinct leaves, second pass, and no-mutation passes. It calibrates full rectangles against visible references. Short bucket timings can be zero or quantized; size1 has an empty distinct bucket. Fixed phase order and one process per phase cannot establish broad absence of performance regressions. Original-group cleanup does not prove that processes which escaped the session are absent.

Root commands after final draft review:

```
python3 -I -S prepare.py --draft-sha REVIEWED_SHA --expected-head POST_SIGNING_HEAD
python3 -I -S experiment.py --inputs-sha REVIEWED_INPUTS_SHA --with-traces --with-timings
```

Cost-v2 independent source review is sealed GO for a bounded diagnostic. This driver draft is frozen for root and independent review; it is not prepared or authorized for execution by the seal. No browser, build, Git mutation, preparation or native modification has been performed.
