# Archived depth and initial-animation WPT preparation

This disabled, seven-callback setup reuses the executed `css-root-self-smil-archived-original-v1` runner. It stages the exact sealed depth fixture `61d91092` and initial-animation fixture `72e920d5`, with no assertion edits. Two pages contain four depth callbacks and three initial-animation callbacks. Original and candidate results are separate observations; neither result is predicted or a native acceptance gate.

The sole runtime delta changes the assessor from one seven-case page to two pages with three/four cases, checks two starts/endings, accepts the candidate CLI role, and changes the owned temporary-directory prefix. The seven-case identity/duplicate/status/lifecycle/crash/exit checks, archive inventory/build checks, staging, process-group cleanup and preservation logic are unchanged. `entry.py` and all support files are byte-identical to the executed parent. No new native owner, build or capture workflow is introduced.

Resources are exactly `/resources/testharness.js`, `/resources/testharnessreport.js`, `/web-animations/animation-model/keyframe-effects/root-font-cancel-child-depth.html` and `/web-animations/animation-model/keyframe-effects/initial-root-font-child-keyframes.html`. `RESOURCES.json` pins their sealed original bytes; `INPUTS.json`, `MANIFEST.json` and `ROSTER.json` describe the local copies. There are no preferences or expected-failure metadata. Both pages have a long timeout. Full first/settled arrays in JavaScript are not automatically exported by the inherited WPT runner: raw callbacks retain assertion results and first failing messages.

Genuine upstream WPT path/content lint passes for both authored HTML pages. Genuine manifest generation and inert registration produce seven exact names and two URLs. The initial preparation incorrectly linted unchanged testharness.js without its upstream exclusions; that failed attempt and source are retained. The corrected check limits lint to the two authored pages and authenticates harness bytes. Saved check `7c4092 / 19159 / 6446c1 / exit 0` passes two synthetic streams, twelve rejecting streams, both disabled gates, actual isolated resource staging and genuine WPT `--check-args` for both archive policies. Both scratch stages were removed. No browser, live application, archive inventory scan, native source or canonical/index mutation occurred.

## Archive bindings and execution

Original: `/private/tmp/css-original-e86-browser-1wxwyapk/Nightly.app`, snapshot `b8ba7f9b...`, original e86 build receipt. Candidate: `/private/tmp/css-font-unit-candidate-q42fzypj/Nightly.app`, snapshot `4a25d2ff...`, exact three-role route-only build receipt `8d96a143...`. Each snapshot has 8,326 files and no `.purgecaches` marker. The candidate is the broad route-only patch; it does not include the separate font-membership repair or selective handoff proposal.

Both policies join completed owner `ef947a / 96261 / 022c3d / exit 0`, runtime seal `25ca83c0...`, independent restoration report `40f6577f...` and audit terminal. The saved checker joins candidate source/build/snapshot to that report's verified archive handoff. This supplies completed preservation evidence, not permission for concurrent archive use. Root must verify each archive is idle and retained, preserve disabled policy/manifest preimages, activate only the selected policy's `execution_enabled`, and reseal FILES before its serial run. Runtime `archive()` authenticates the entire archive inventory before and after execution. Any later archive change must reject rather than silently adopting new bytes.

Root may replay the saved check without running Firefox:

```
python3 -I -S -B artifacts/css-root-font-route-supplement-archived-wpt-v1/check.py > artifacts/css-root-font-route-supplement-saved-check.log 2>&1
```

After root activation, run original and candidate serially:

```
python3 -I -S -B artifacts/css-root-font-route-supplement-archived-wpt-v1/run.py --role original --run > artifacts/css-root-font-route-supplement-original-root.log 2>&1
python3 -I -S -B artifacts/css-root-font-route-supplement-archived-wpt-v1/run.py --role candidate --run > artifacts/css-root-font-route-supplement-candidate-root.log 2>&1
```

Outputs are respectively `css-root-font-route-supplement-original-runtime-v1` and `css-root-font-route-supplement-candidate-runtime-v1`. Each run uses auto server ports, isolated tests/metadata/config/mozinfo, fresh owned TMPDIR/profile/process group and the archive binary explicitly. It does not call mach or write live build run-info. Root records actual owner terminal and independently checks exact seven identities, two starts/OK endings, suite lifecycle, no crashes, archive/staging preservation and process/temp absence. Complete FAIL observations remain valid observations; owner exit zero does not mean all callbacks PASS.

Depth cases remain proposed coverage until the unpatched baseline is measured. Initial-animation results do not prove that `FinalAnimationTraversal` occurred; a numerical PASS cannot close that source boundary without tracing the actual branch. The already-completed native8/full34 evidence remains separate and unchanged.
