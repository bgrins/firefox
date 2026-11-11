# CSS getKeyframes computed-value baseline

Prepared, not executed. This baseline-only experiment installs one temporary conformance WPT with no metadata, lints it, and runs the retained combined #172 browser. SOURCE-ROLES is empty and no candidate/build branch exists. The old observation parser and marker collection are removed entirely. The execution HEAD remains null pending root review/freeze; new research artifacts are hash-authenticated, not claimed signed.

The eight callback names are derived by executing only script registration in a Node VM where test() records names without invoking callback bodies. Expected results are provisional source/probe hypotheses: five FAIL (ordinary relative length, registered relative length, unregistered var, changed var source, animated font) and three PASS (unregistered tokens, WAAPI specified, CSS setKeyframes specified), plus one OK harness ending. An exact inventory/status gate rejects any different vector for review; it does not silently waive failures. WPT must exit 1 for these unannotated baseline failures, and lint must exit 0. Actual messages and expected classifications are saved without inventing a message oracle. No expected-failure metadata is added.

Runtime/analyzer/transaction origins are authenticated through custom-probe v2's frozen manifest b71bb9e8150c7d4f33ef63c4acfd190d23b6d6750f4a9f967c2b8321056fc31b and signed helper origin 3f8f7324c20de730eddcf07b224dd93e9be6694d. RUN-DIFF records the reduced runner. The full app/extras backup, process-group containment, source/test/config/HEAD/index checks and restoration helpers are preserved. On success all fixture/backups/lock are removed; on an unverifiable restore diagnostics/backups remain. Root holds the exclusive transaction throughout execution and independent restoration review.

The proposal is exact from css-keyframe-computed-serialization-investigation-20261110-v1, FILES manifest f45db45c70a132ec9da685d78a802e31ac457a69fd4a410b5a69007307df663c. The independent conformance review is in css-keyframe-computed-serialization-review-20261110-v1. Frozen primary clauses distinguish CSS computed values from WAAPI/replaced-keyframe specified values and require current element dependency context. No source repair, bug count, broad CSS coverage, or final missing-pseudo/debug acceptance follows from merely preparing this experiment.

Root commands after review:

```sh
python3 -I artifacts/css-keyframe-computed-serialization-probe-20261110-v1/freeze.py FULL_HEAD artifacts/css-keyframe-order-combined-current-build-20261110-v1/build-result.json
python3 -I artifacts/css-keyframe-computed-serialization-probe-20261110-v1/run.py baseline baseline1
```

Freeze authenticates the artifact-only source bridge and live binary/config/test inputs before emitting readiness. The run cannot execute without that receipt. Raw logs, exact callback messages, sampled binary hashes, command/process receipts and full restoration records remain for independent inspection. Twenty synthetic rejection controls cover lifecycle, crash/error events, missing/duplicate callbacks, truncation, wrong inventory, unexpected improvements and regressions. Positive controls demonstrate preservation of arbitrary actual failure messages.
