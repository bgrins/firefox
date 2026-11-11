# Specified-branch baseline

Prepared baseline-only execution of the four reviewed branch controls. Provisional outcomes are plain WAAPI PASS, replaced CSS variable expression FAIL, detached CSS singleton FAIL and transferred CSS singleton FAIL. Those are source hypotheses, not prior browser results. Exact callback inventory and full lifecycle are required; actual failure messages are preserved for setup-versus-getter review. No metadata is added.

This reuses the frozen changed-font conformance runner. RUNNER-DELTA records only callback count/status validation, the assertion's descriptive text and index-independent selection of synthetic improvement/regression controls. Transaction/analyzer/freeze helpers are unchanged and retain signed provenance. One temporary WPT is installed, linted and restored; native roles are empty, with no build/candidate path. The fixture and independent primary-spec/source reasoning are pinned to the branch proposal.

Root must check, freeze against the retained combined build at a clean HEAD/index, then run `run.py baseline baseline1`. Execution HEAD is unset until freeze. Reject incomplete results and independently verify full restoration before any next native/browser transaction. A matched status vector alone is insufficient; inspect each actual failing assertion. Nothing has executed from this capsule yet.
