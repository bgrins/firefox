# Standalone zoom passed-reftest port adjudication

The candidate run completed and preserved its environment. Its original wrapper verdict remains false. All636 assertions were captured:573PASS/63FAIL; the566 broad assertions are signature-identical to original, while56 zoom assertions repair and14 remain passing. All six reftests pass. The only broad comparison rejections are diagnostic messages containing the phase-local HTTP server port62150 versus62607.

This closed-evidence replay authenticates both sealed capsules, saved raw logs and assessments, exact copied fixture/resources and manifests, build/source/epoch/binary bindings, metadata and cleanup. It replays both raw assessors and the unchanged comparator, requiring exact equality with the saved false comparison. RAW-COMPARISON.json is a byte-for-byte copy; neither runtime file is rewritten.

Only the six declared reftest PASS test_end message strings are normalized in deep copies. Both test/reference URLs, HTTP scheme, web-platform.test host, operator, newline framing, valid matching ports inside each message, and one port per phase must match. Expected-field addition, intermittent changes, other outcomes, malformed messages or reference paths are rejected. Every other event field remains unchanged in each copy; the original comparator retains its full status/message/expectation signature rules everywhere else. No generic URL normalization is installed in a runner.

VERDICT.json records the separate adjudicated broad gate. REPLAY.json retains both comparisons and every raw message/port pair. All six passed references and566 broad assertions are preserved; all70 zoom assertions pass. Native fix acceptance remains false: this evidence resolves only the spurious port comparison rejection, not other source/spec/landability obligations.

Replay read-only with:

```
python3 -I -S -B artifacts/css-registered-zoom-reftest-port-adjudication-v1/replay.py
python3 -I -S -B artifacts/css-registered-zoom-reftest-port-adjudication-v1/test_controls.py
```

Final replay95128b/0 and controls a8d5e4/0 passed (2positive/108rejects). Counter reviewer cleared the bounded normalization. An intermediate strengthening check3abae0/1 used the wrong saved metadata directory name; correcting meta to metadata made the complete check pass. No browser rerun, live source/index/epoch/control modification or accepted-count increment occurred.
