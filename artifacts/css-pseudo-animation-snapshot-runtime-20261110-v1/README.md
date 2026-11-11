# Property-input snapshot runtime experiment

Prepared only; no build, browser test or live source/fixture mutation was executed by the author. Native snapshot.patch is the independently reviewed two-file prerequisite b37e4885614c5b2acb7fa4320ca734fd2c7fa1062e12f5b55c6e60be71d25166. This experiment expects preservation, not a missing-pseudo fix.

The source basis is7382007a; the execution HEAD gate is f3949d2992abdc02536b9a61e51dc7d603ce0868. Baseline uses the retained committed clip-fix171 browser, BuildID20261110165601, from css-clip-auto-current-build-20261110-v1/build-result.json. runtime-inputs/retained-build.json records its source/config/binary hashes and original receipt digest. No unnecessary baseline rebuild is planned.

After review, root may run:

```sh
python3 -I artifacts/css-pseudo-animation-snapshot-runtime-20261110-v1/run.py baseline baseline1
python3 -I artifacts/css-pseudo-animation-snapshot-runtime-20261110-v1/run.py candidate candidate1 baseline1
```

Each output name must be new. Candidate requires a successful restored baseline with the same RUN-INPUTS digest and then runs a real mach build binaries -j6 (2400s limit). WPT uses eleven explicit pages with one process, headless, and full unfiltered text/JSON logs. Exit0/1 is only an admission to parsing: exact callback/harness preservation determines the gate. No other native build/browser test, Git mutation or affected-file edit may run concurrently.

## Inventory and baseline

The frozen source [TEST-PLAN](../css-pseudo-animation-next-candidate-20261110-v1/TEST-PLAN.md) supplies ten pages: retained20/9 pseudo fixtures and target.html; CSS getKeyframes, setKeyframes and effect-replacement pages; and four CSS named-range generation pages. The retained fixtures are installed verbatim only while testing and must be absent beforehand, along with their metadata. All other pages are existing tracked tests.

This runtime adds exactly one page: css/css-animations/keyframe-attribute-mutation.html from committed fix131/65355573964a. Its12 cases compare retained and fresh paused CSS/WAAPI effects through attribute change/removal/re-addition, with ordinary/literal controls and namespace discrimination. It specifically guards the aReferencesAttributes forwarding/refreshed-keyframe dependency path changed by this extraction. This addition does not expand into attribute-taint policy or security tests, and the frozen source plan remains unchanged.

A fresh baseline is required; old287/258 status tables are not copied. Known subtest failures are retained and compared, not relabeled or waived. Baseline output should also be reviewed to confirm the selected CSS-generation/attribute cases actually reach their intended assertions. A failed harness, timeout/not-run callback, crash, incomplete lifecycle, generic ERROR/CRITICAL structured log or unexpected native assertion count fails the parser. Full logs remain available for other diagnostics.

Thirty-four served-page/script and metadata-presence entries are pinned, including absent metadata and ancestor directory metadata. This is a bounded directly included script closure, not a proof of all dynamically loaded harness dependencies; exact clean Git HEAD and source verification additionally constrain the checkout.

## Comparison and restoration

Comparison keys are `(record kind, test URL, subtest)`: assertion and harness records are distinct even when subtest is null. Duplicate callbacks, duplicate harness endings and duplicate comparison keys are rejected. Exact key inventory and statuses must match. All raw callback messages/expected fields are retained; message strings are not equality-gated. The old clip comparator's null-name collision is reproduced by a synthetic control and rejected by this comparator.

The complete-app/process helpers are byte-identical to the reviewed composition-extraction wrapper. Before mutation, the runner backs up the full Nightly.app and explicit gtest XUL/application.ini/wptrunner.local.ini extras and records modes/symlinks/hashes and Git index identity. Candidate installs only the two copied native files; both modes temporarily install the two approved fixture files. The source/test-source/config/binary identity is verified before and after testing.

On success, failure, timeout or ordinary cancellation, owned processes are made quiescent before restoration. Source, full application and extras are restored; fixtures are removed only if their bytes still match this runner's installation. Concurrent changes or surviving processes cause a restoration failure and retained backups. Successful verification removes owned backups. Build intermediate objects are not rolled back; restored source mtimes allow subsequent rebuilds. The final retained browser must remain the original clip-fix171 browser.

BUILD.json, SAMPLED-BINARIES.json, raw logs, TEST-RESULTS.json, COMPARISON.json and RESULT.json distinguish compilation/testing outcomes from restoration. No metadata is altered. Source/current browser checks and synthetic parser controls are preparation evidence, not runtime results.

## Coverage limit

The configuration is optimized. This is a prerequisite preservation experiment, with no CSSOM hook or new pseudo traversal. It cannot close the separate missing-pseudo debug gate or prove current range offsets, provider-aware endpoints, timing coherence, fresh masks or transient recascade. The source report and independent review retain those integration obligations. The [ownership addendum](../css-pseudo-animation-next-candidate-20261110-v1/OWNERSHIP-ADDENDUM.md) also records that the copied pseudo request changes aliasing across hypothetical reentrant retargeting: captured target/pseudo coherence is intentional, while ordinary preservation is scoped to the current synchronous path. No browser bug/fix is counted by this refactor.
