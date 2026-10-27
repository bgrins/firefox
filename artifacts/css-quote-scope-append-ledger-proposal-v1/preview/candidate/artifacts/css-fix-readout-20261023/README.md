# Local CSS/Stylo fixes by area

Fix 135, contained quote append invalidation, is committed as `PENDING_NATIVE_COMMIT` after research `PENDING_RESEARCH_COMMIT`. The candidate/original/candidate comparison gives 64 PASS / 52 PASS + 12 FAIL / 64 PASS, with all 18 existing regressions unchanged (15 PASS and three expected FAIL). Tentative P3 visual correctness. Discovery came from source audit and browser reproduction; conditional Lean models corroborate scope/dependency laws, not universal native correctness. No clean-upstream build, security or measured performance claim. The adjacent counter hypothesis remains unrun and uncounted.


Fix 121 now includes its validated one-block expectation correction. The signed history rewrite preserves the final tree; current commit IDs below come from the [new rewrite receipt](../../artifacts/css-integer-stored-range-history-publication-runtime-v1/RESULT.json). Historical signing receipts retain their original IDs. All 134 accepted fixes remain committed; held repair 120 stays excluded.


**134 accepted fixes: 134 committed locally, 0 accepted pending, and 1 additional held repair excluded.**

| Area | Committed | Accepted, pending |
|---|---:|---:|
| Selectors, Bloom filters and scoping | 10 | 0 |
| Cascade, layers and shorthands | 6 | 0 |
| Parsing, tokens and CSS math | 26 | 0 |
| Attributes and custom properties | 16 | 0 |
| Animations, timelines and transitions | 16 | 0 |
| Text and fonts | 14 | 0 |
| Layout, sizing and positioning | 22 | 0 |
| Container queries | 3 | 0 |
| Colors, images, SVG and shapes | 8 | 0 |
| CSSOM geometry and hidden layout | 13 | 0 |
| **Total** | **134** | **0** |

| Fix | Gecko/WPT commit | Preceding research |
|---|---|---|
| 134: calculated cubic-bezier x range | `70cc9c30ef4420d8dba76ce3e5aab10504339ceb` | `906c05d72653ecf46a591b197a06bc973a8accc3` |
| 133: calculated-jump-none-minimum | `e414c8f7cfcd64ccca1a944b5f8e901ec3db2feb` | `be4240e9d1ccab6395139ba975e1a13aeb9f8762` |
| 121: integer-stored-range-resolution | `b218397700bd4ad701a232fad806cf99dd8f9f7b` | `3b1fc453848bd1ef03a5dc118e39cb6d9411ef42` |
| 122: saturated-subgrid-line-name-cache | `8d0eb95794ebcd0b0dd5585047c9316ae075df92` | `7abb33ffcb2480da8ddddc213249496b902db102` |
| 123: counter-range-calculated-bound-export | `0f68c5c1a7a556dd3907fdf7caf2d97110c53c12` | `a2eea3d47919f698604fa869593ccab8feccd7ea`, `53989ac9bd082a4dcbe497cf35b6009a9da53e54` |
| 124: additive-symbol-resolved-weight-ordering | `656b54ea29efd83de6873663882afa0cab6b0e39` | `a2eea3d47919f698604fa869593ccab8feccd7ea`, `b4592416a12e5c9b7c81e1afccc9accbfca9f6c2` |
| 125: round-runtime-nan-propagation | `a9b7886a5f470942b5e8e9d5863237b301d64425` | `f8b9a6bc48b86d3bbea32e8094f5e664cd4e3394` |
| 126: round-finite-negative-zero-bound | `4c4ff0d440cd3d1ffd1021e831258043dbb926ed` | `0b3d341c8367da1fd832fabfe85d3628e18839ec` |
| 127: subgrid-contextual-name-repeat | `f946a0921b8b5ee87661284a827208b00cee5398` | `79f8d7f1ea56ac293fc86a00f70cf327cb58f98a` |
| 128: finite-mod-rem-quotient-reconstruction | `10b6eabed27195aa21e41f62d8179af3a065a1dc` | `3d889a60923562ff9d0d07b5373ba12698a2592c` |
| 129: css-duration-reactivation-keyframe-properties | `d13af8f7e9fd232b3d950f4f9bb59436ec6ef29f` | `7626b6ca8866ba2e6288a9b070b5e8d880ede2d1` |
| 130: ordinary-keyframe-attribute-initialization | `e91224fd2e9e163bfb73d8e3fcdd4a1017b34ef1` | `e40adf1616f3f485163cc4c65176ce0e21b3ddf1` |
| 131: active-keyframe-attribute-dependency-publication | `65355573964a31a08b3ae3e133c224cbab46e098` | `e9b759281bca085273ddbdfe0895e1adb688f6f0` |

All 23 signed-item receipts passed exact parent/content and configured-key signature verification: 11 native/WPT commits and 12 research commits. Shared counter evidence precedes both fixes 123 and 124; prior research dependencies remain in the authenticated recipes. Existing fix 132 and held fix 120 are unchanged. Per-fix prerequisite, standalone, release-exposure and formal-scope caveats remain intact in the JSON records; signing is not a new build, browser test or clean-upstream validation. Source and binary bodies were preserved; main staging is empty, and nested-library index state is retained. Remaining prototype work is not counted as accepted fixes.

The callable current-provider resolver passed the normal and GTest builds and all 19 native tests; normal pending recipe production remains disabled. The 113-case metadata comparison preserved all 110 PASS and three expected FAIL observations, changing only the fix 121 expectation. The canonical library is signed at `162b20fb7c53a0ab89b20875a965baee98fb66bb` and its full check passes 11,840 audits, 12,438 cases, 173 expected-false cases and 2,155 source fingerprints. Ten audits transfer from reviewed steps research, with no new discovery, normative coverage or native-refinement credit.

Next: Integrate winning pending animation providers through the real cascade and dependency scheduler; preserve explicit current-base, cycle-policy, dependency-publication and memory-reporting obligations. Preserve unresolved animated-cycle policy, current underlying-value provenance, dependency publication and memory-reporting obligations.

Historical checkpoint text follows; its counts and future-work statements describe that earlier state.

**131 accepted fixes: 120 committed locally and 11 awaiting commits.** One additional numbered repair remains held and excluded.

Endpoint source-index integration passed the full canonical checker after adding three missing helper audits. Fourteen existing theorem audits and eight executable cases are transferred implementation support, with no new proof-discovery or normative CSS coverage credit. Both indexes, all 147 staged research files, native sources and browser binaries are preserved. [Full check](../css-keyframe-endpoint-index-library-application-v1/REPORT.md).

The concrete animation-rule transport build and browser comparison passed. All 166 subtests retain their baseline outcomes (162 PASS and four known provider FAIL), and both crash tests pass. Source, binary, research and index preservation checks and owned-process cleanup pass. The transport remains installed for the next implementation step; this adds no accepted fix. [Comparison](../css-keyframe-animation-rule-sample-capture-runtime-v1/REPORT.md).

The authored-endpoint indexing model also passes independent source review and Lean replay: eight implementation lemmas, five positive examples and three decisive false controls. Native correspondence remains conditional; this adds no normative CSS coverage.

Six signed commits passed exact parent/path/blob checks and configured-key signature verification. Each of fixes 117–119 has one native/WPT commit, preceded by its research. The disjoint research selections add 65, 48 and 146 paths. Fix 118 reuses 40 exact files from the preceding fix 117 research commit; fix 119 retains its already-committed reviewer-log dependency. All working native bodies remain unchanged, including later edits sharing committed files. Main staging is empty; existing nested-library staging is preserved. Signing ran no new browser tests and does not establish clean-upstream independence.

The active-provider trace completed and the production sources/build are restored. Both captures reproduce six PASS and four calibrated FAIL. During the red-provider interval, the consumer uses cached 20/30 endpoints and produces 20/25/30; no recomputation records were observed in that retained interval. Native emitting PID and complete log delivery remain unproved. [Trace interpretation](../css-keyframe-active-provider-trace-interpretation-v1/REPORT.md).

The animation operation-arena test host builds and both native GTests pass, including 28 differential comparisons against production animation composition. Frozen Cargo resolution, the normal binaries build, the GTest host build and source/index preservation checks pass. This adds no accepted bug or native-refinement claim. Current-provider resolution and animated cycles remain open. [Execution record](../css-keyframe-operation-arena-host-runtime-v1/REPORT.md).

The canonical Lean library completed its full check with 11,805 audited declarations, 12,409 executable cases, 167 expected-false cases and 2,151 source fingerprints. Prefix-refresh integration is complete; copied proofs add no normative coverage. Current-provider context and a complete contributing prefix remain explicit model assumptions, not native refinement results.

Next: compile and test the production operation arena and authored-endpoint descriptors. Resume the prepared commit queue when 1Password signing is available. Winning-provider admission, animated cycles and descriptor memory reporting remain open; the implicit-underlying animated-provider oracle is inconclusive. Fix 120 and the normal-recascade performance candidate remain held.

Historical checkpoints follow; their counts describe their recorded state.

**131 accepted fixes: 117 committed locally and 14 awaiting commits.** One additional numbered repair remains held and excluded.

The animation operation-arena test host builds and both native GTests pass, including 28 differential comparisons against production animation composition. Frozen Cargo resolution, the normal binaries build, the GTest host build and source/index preservation checks pass. This adds no accepted bug or native-refinement claim. Current-provider resolution and animated cycles remain open. [Execution record](../css-keyframe-operation-arena-host-runtime-v1/REPORT.md).

Seventeen signed commits passed exact parent/path/blob checks and configured-key signature verification. Each of fixes 109–116 has one native/WPT commit, preceded by its research. The corrected MathML selection adds 710 paths and retains 341 identical already-committed inputs; fix 116 uses the accepted stack variant after fixes 114 and 115. All working native bodies remain unchanged, including later edits sharing committed files. Main staging is empty; existing nested-library staging is preserved. Signing ran no new browser tests and does not establish clean-upstream independence.

The active-provider trace completed and the production sources/build are restored. Both captures reproduce six PASS and four calibrated FAIL. During the red-provider interval, the consumer uses cached 20/30 endpoints and produces 20/25/30; no recomputation records were observed in that retained interval. Native emitting PID and complete log delivery remain unproved. [Trace interpretation](../css-keyframe-active-provider-trace-interpretation-v1/REPORT.md).

The canonical Lean library completed its full check with 11,791 audited declarations, 12,401 executable cases, 164 expected-false cases and 2,149 source fingerprints. Prefix-refresh integration is complete; copied proofs add no normative coverage. Current-provider context and a complete contributing prefix remain explicit model assumptions, not native refinement results.

Next: review and compile the distinct normal animation-rule transport, then carry endpoint recipes through cascade admission and resolve them against current winning providers. The transport-only step predicts no bug repair. Prepare separate research/native commits for accepted fixes 117–119. Animated cycles and the broader formal milestones remain open; fix 120 remains held. The normal-recascade candidate stays on performance hold and all four retained browser copies remain needed.

Historical checkpoints follow; their counts describe their recorded state.

**131 accepted fixes: 109 committed locally and 22 awaiting commits.** One additional numbered repair remains held and excluded.

Five signed commits passed exact parent/path/blob checks and configured-key signature verification. The three native commits contain only their accepted Gecko changes and WPT files; research precedes them. All working native bodies remain unchanged, including later Block/Grid edits. Staging is empty. The original scoped browser evidence remains authoritative; committing ran no new browser tests.

The active-provider trace completed and the production sources/build are restored. Both captures reproduce six PASS and four calibrated FAIL. During the red-provider interval, the consumer uses cached 20/30 endpoints and produces 20/25/30; no recomputation records were observed in that retained interval. Native emitting PID and complete log delivery remain unproved. [Trace interpretation](../css-keyframe-active-provider-trace-interpretation-v1/REPORT.md).

The canonical Lean library passes its full check with 11,791 audited declarations, 12,401 executable cases, 164 expected-false cases and 2,149 source fingerprints. Contributing-keyframe refresh integration is complete: six previously reviewed declarations were transferred without increasing normative CSS coverage. The model assumes current provider context and a complete contributing prefix; native refinement remains unproved. Both repository indexes and native sources/binaries were preserved. [Integration evidence](../css-keyframe-commit-styles-library-application-v1/REPORT.md).

Next: sign the prepared fixes 109–116 sequence using the corrected MathML research selection; build and execute the Gecko operation-arena tests, then compare them with production animation composition. Active provider delivery/cycles and the broader formal milestones remain open. The recascade candidate remains on performance hold; four retained browser copies are still needed.

The entries below are historical checkpoints; earlier pending/running statements and performance interpretations are superseded by current status.

Active dependent animations now have a calibrated six-case capture: the provider advances from 225 to 275 while dependent endpoints keep yielding 125/175. Repeated reads and creation/getter order do not repair the values; an unrelated normal style change repairs 125 to the expected 143.75. Both literal controls pass. Source, build, staging and fixture cleanup are preserved. This supports the active-sampling dependency boundary, with no new accepted fix. [Capture](../css-keyframe-acyclic-sampling-diagnostic-runtime-v2/REPORT.md).

The normal-only keyframe recascade comparison is complete and root-verified: 190 tests improve from 177 PASS/13 FAIL to 187 PASS/3 FAIL, all 22 targeted checks pass, and all 168 controls remain exact. Original sources and generated headers are restored and rebuilt; every baseline outcome returns exactly. All six timing captures complete, but restored controls slow substantially, so performance remains inconclusive and the candidate is unaccepted. A balanced comparison using independent retained browser copies is being prepared. HEAD and staged content are preserved; raw index bytes changed with no established cause. Signing remains blocked by the last 1Password failure.

The dormant-animation candidate passed its 182-case correctness comparison, but local timing now shows an added first-style-flush cost. For 1,000 targets, several literal first-play/replay cases rose from 2–3 ms to about 4.5–6 ms and returned to 2–3 ms after restoration. All six browser runs and both builds passed; root checks verify the original source/build and index are restored. The candidate remains unaccepted. Next: investigate a distinct normal-only recascade request that refreshes every provider without selector rematching, retain the planned 190-case correctness scope, and repeat timings. [Measurements and limits](../css-keyframe-dormant-replay-timing-analysis-v1/REPORT.md).

A follow-up on the restored build reproduces four more stale-value cases: cancelled animations using changed `em` or custom-property inputs return 20 instead of 40 for width/transform; all four fresh-animation controls pass. Root verification and independent review confirm the temporary fixture is removed and source/build/index are preserved. This extends the same dormant-cache investigation, not the accepted bug count. Candidate validation for these eight cases is still pending. [Measured observations](../css-keyframe-dormant-provider-baseline-runtime-v1/SUMMARY.json).

Fix131 is accepted: active animations now refresh attribute-dependent keyframes after attribute changes. The eight-native-file/four-WPT patch passes all46 landing cases and repairs33 failures across162 cases, preserving116 controls and exactly reproducing all baseline outcomes after restoration. Both builds, root verification, terminal review, formatting and exact-body WPT lint pass. Fix130 is a functional prerequisite. Installation and rebuild are complete: all 46 regression checks pass again, and root preservation checks pass. Independent installation review also passes; the signed commit is pending. **130 accepted fixes:105 committed and25 pending; one additional repair held.** [Acceptance and patch](../css-keyframe-attr-effect-publication-acceptance-v1/REPORT.md).

Local comparison69119 completes126PASS/36FAIL →159PASS/3FAIL →exact126PASS/36FAIL. Both builds pass; all46 selected cases pass on the candidate, repairing33 assertions with116 controls exact. Root42681 verifies restoration,779 roles,925 staged working payloads and six-fixture cleanup. Raw index bytes change75dd→bc3412 with semantic staging preserved; cause unknown. Independent terminal review passes; accepted as fix131. [Comparison](../css-keyframe-attr-publication-comparison-runtime-v2/REPORT.md).

The expanded attribute-publication baseline completes162 cases:126PASS/36FAIL across19 OK harnesses. All128 prior outcomes and20 unchanged lifecycle outcomes remain exact. All22 lifecycle cases now reach calibrated stale-value assertions, alongside five retained-mutation, four retained-pseudo and two detached-replacement cases. Fresh pseudo and ordinary controls pass. Root preservation, six-fixture cleanup and independent terminal review pass. The native repair remains unapplied and no new fix is counted. [Baseline](../css-keyframe-attr-publication-baseline-runtime-v2/STATUS.md).

The provisional Boolean-watch extension passes an independent Lean replay:15 support audits, five closed examples and three expected-false controls. It proves finite-history preservation under conservative strengthening; target reassociation, native correspondence and scheduler delivery remain unproved. [Root replay](../css-keyframe-provisional-bit-watch-root-replay-v1/REPORT.md).

Latest investigation: the 150-case attribute-publication baseline records 120 PASS and 30 FAIL, with all prior 128 outcomes unchanged. Twenty lifecycle and five retained-mutation cases reach calibrated stale-value assertions. Two styled-retarget tests need a separate initial-provider observation; a reviewed fixture successor preserves their mutation expectations. Root preservation, four-fixture cleanup and independent terminal review pass. Native comparison awaits the successor baseline; no additional fix is counted. [Baseline](../css-keyframe-attr-publication-baseline-runtime-v1/STATUS.md).

Fix130 is accepted: ordinary keyframe attr() now prepares attribute values and uses the real element provider. Its two-Rust-file/one-WPT patch repairs18 assertions across116 cases, passes all24 landing cases, preserves84 controls, and reproduces every baseline outcome after restoration. Both builds, root preservation, independent terminal review and WPT lint pass. One changed custom-context diagnostic is observational only. Installed and rebuilt: all24 landing cases pass, with root preservation checks and independent installation review complete. Signing remains pending. **129 accepted fixes:105 committed and24 pending; one additional repair held.** [Acceptance and standalone patch](../css-keyframe-ordinary-attr-acceptance-v1/REPORT.md).

Fix129 is accepted: CSS duration changes that reactivate an effect now rebuild its contextual keyframe values. The one-line Rust/six-case WPT patch repairs two failures; all173 strict controls and179 restored non-observational outcomes remain exact across182 cases. Both builds, root preservation, independent terminal review and WPT lint pass. Existing viewport-message variation and unequal raw-index bytes remain explicitly qualified. Installation is complete: the rebuilt browser passes all six landing tests, root preservation checks pass, and the archived result review agrees. Signing is pending. At fix129 acceptance: **128 accepted fixes:105 committed and23 pending; one additional repair held**. [Acceptance and standalone patch](../css-keyframe-css-duration-acceptance-v1/REPORT.md).

The one-line duration-reactivation repair passes its local three-phase comparison:182 cases improve148PASS/34FAIL →150PASS/32FAIL →148PASS/34FAIL after restoration. All six landing cases pass on the candidate; all173 strict controls remain exact, and all179 non-observational baseline outcomes return after restoration. Both builds pass. One existing viewport FAIL moves from its initial assertion to its resize assertion in both candidate and restored runs, so full182 diagnostic equality is not claimed. Root verifies696 roles,80 source guards,25 installed identities,925 staged payloads and six-fixture cleanup. Semantic staging is preserved; raw index bytes changed6d7860→75dd5b. The runtime report's contrary raw-equality sentence is explicitly corrected by the linked clarification. Terminal review and WPT lint are pending; accepted counts remain105 committed +22 pending, with one held. [Comparison](../css-keyframe-css-duration-comparison-runtime-v1/REPORT.md), [raw-index clarification](../css-keyframe-css-duration-comparison-root-clarification-v1/REPORT.md).

The four-case custom-property-context probe now completes with two PASS/two FAIL. Direct var opacity interpolates [.25,.375,.5,.625,.75] while measured --n changes discretely [.25,.25,.75,.75,.75]; literal and unchanged-context controls pass. The attr case stays at fallback .125 and fails initial provider calibration, so its final context assertion is not reached. Capture80377 and root verification29906 pass; all696 roles and the single-fixture cleanup are verified. Independent terminal review passes. The spec route is supported by CSSWG issue5125/PR5255 and prior Firefox discussion in bugs1402219/1846516; this is a known problem class, with current cross-browser behavior unmeasured. No native repair or new accepted count is added. [Diagnostic](../css-keyframe-custom-context-diagnostic-runtime-v1/REPORT.md).

The latest 52-case keyframe diagnostic completed with 25 PASS/27 FAIL across eight OK harnesses. Root verification and the archive review confirm source, staging and binary preservation and removal of all six temporary fixtures. Two duration-reactivation targets fail while four controls pass; both calibrated viewport companions remain stale across measured viewport changes. Attribute initialization failures remain under investigation. One incorrect experimental oracle is excluded, and the two URL observations do not establish taint loss or exfiltration. Counts remain **105 committed +22 accepted pending commits; one additional repair held**. [Diagnostic evidence](../css-keyframe-followup-diagnostic-runtime-v1/REPORT.md), [archive review](../css-keyframe-followup-diagnostic-terminal-review-v1/REPORT.md).

A one-line Rust duration-reactivation repair passes root patch-transport and fixture checks; native compilation and comparison are next. A separate attribute-initialization repair has a corrected landing fixture but is also uncompiled. The Lean attribute-preparation companion passes its independent root replay under explicit provider, resolver and context assumptions; it is not a native implementation proof or new canonical CSS coverage. A four-case custom-property-context diagnostic is prepared to distinguish current-context behavior from missing attribute preparation. [Duration proposal](../css-keyframe-css-duration-reactivation-repair-v1/REPORT.md), [Lean replay](../css-keyframe-attribute-preparation-root-replay-v1/REPORT.md).

The unchanged 167-case repeat (22755, exit 1) reproduced the same single viewport failure-location change as run 12255: 138 PASS/29 FAIL across 14 OK harnesses. Root preservation verification passed (74006, exit 0), with all five fixtures removed and no native change or build. Automatic candidate comparison remains stopped while a separately calibrated viewport companion is prepared. The original test and exact outcomes remain preserved. Typed-attribute initialization has a reviewed repair design; its artifact-only implementation is in progress. Counts remain 105 committed, 22 accepted pending commits, and one held repair. [Repeat evidence](../css-keyframe-tree-counting-baseline-repeat-runtime-v1/REPORT.md).

The combined 167-case attempt (12255, exit 1) rejected its fresh baseline before any native mutation. Counts remain 138 PASS/29 FAIL, but the existing CSS viewport test failed its initial100px assertion with150px instead of reaching the later resize failure. Every other outcome matches; all five fixtures are removed and driver preservation passes. Root preservation verification passed (38552, exit 0); the terminal archive review and one unchanged baseline-only repeat are next. The setup audit leaves the cause of the viewport variation unresolved. The v2 candidate has not yet run the six inactive-replay cases; no build or source change occurred in this attempt.

The 20-case keyframe diagnostic (66317, exit 0; root 14935, exit 0) completed 13 PASS/seven FAIL. Replaying the sole cancelled effect after an inactive sibling change leaves width and translation at 20px instead of 40px; all four replay controls pass. Ordinary typed-attribute keyframes use fallback0.125 instead of0.25, while registered custom-property keyframes resolve initially but miss attribute changes until an explicit recascade. Two existing viewport expectations still fail; ordinary cancellation/font/container/literal controls pass. Root verifies680 roles,79 source guards,25 installed identities,925 staged working payloads,43 native paths and removal of all three fixtures, with current raw index unchanged. Independent terminal review passes. These are observations on the restored original stack, not new accepted fixes or a measured v2-candidate replay failure. Next: combine these20 cases with the prior147 and evaluate the candidate's remaining lifecycle obligation. [Diagnostic](../css-keyframe-dependency-diagnostic-runtime-v1/REPORT.md).

The expanded keyframe comparison (62217, exit 0) passes all three phases: 125 PASS/22 FAIL → 140 PASS/seven FAIL → exact original baseline. All 17 targeted cases pass and all 130 controls are unchanged; both builds pass. Root verification (77683, exit 0) confirms source, test, binary and semantic-stage preservation after restoration. Raw index bytes changed from 9530… to 6d7860… with unchanged staged entries/diff; the initial failed extra check is retained and the cause is unknown. Independent terminal review passes. Acceptance also requires the prepared 20-case diagnostic, particularly cancelled-effect replay after inactive sibling changes. Counts remain 105 committed fixes, 22 accepted pending commits, and one held repair.

Expanded animation baseline16714 passes the corrected exact-order gate: **147 subtests, nine OK harnesses,125PASS/22FAIL**. Added controls contribute123PASS/seven expectedFAIL; the original17 and all repeated normalized observations remain exact. Root45595 and independent terminal review verify655 roles,79 source guards,25 installed identities,925 staged working payloads,43 native paths and two-fixture removal. Currentrawindex9530 remains unchanged during this capture; the older raw-byte limitation is retained. At this baseline checkpoint the v2 native candidate had not been applied; the subsequent comparison is recorded above. [Verified baseline](../css-keyframe-effect-regression-baseline-runtime-v2/REPORT.md).

Focused local comparison27003 rejected the first animation tree-counting candidate: **2PASS/15FAIL → 15PASS/2FAIL → exact2PASS/15FAIL after restoration**. Both builds succeeded. The two remaining failures occur after cancelling another effect and mutating siblings without an intervening style flush. Source reviews identify consumption of the normal recascade request by animation-only traversal; the unchanged WPTs expose missing keyframe recomputation. A narrow v2 proposal now requests RESTYLE_SELF only for animated dependents and passes root patch replay and independent source review; it remains unapplied and uncompiled. The147-case preservation gate is still required before acceptance. [Comparison](../css-keyframe-tree-counting-comparison-runtime-v1/REPORT.md), [successor](../css-keyframe-tree-counting-effect-prototype-v2/REPORT.md).

Root verification preserves637 roles,79 source guards,25 installed tests,925 staged working payloads and the exact HEAD/stage/native snapshots. An extra historical raw-index hash check differed despite identical staged entries and diff; current index bytes were preserved, with no established cause or byte-equality claim. The initial failed check is retained. Independent terminal review verifies restoration under that semantic stage contract and retains the raw-index limitation. No new accepted fix or commit is added.

Keyframe lifecycle baseline 55798 completed: **2 PASS / 15 FAIL across 17 cases**, with four OK harnesses. All seven new cases fail at calibrated target-value assertions; the previous ten outcomes remain exact. Width/translation stay stale after sibling mutations across clone, retarget, reparent, equal-value replacement and multiple-effect histories. Later assertions after each first failure are unobserved. Both temporary fixtures were removed; root preservation checks and independent terminal review pass. This extends known bug 1883255 evidence, with no new accepted fix. The first candidate later compiled but failed two cancellation assertions; see the completed comparison above. All17 candidate cases and the separate147-case regression gate remain required before acceptance. [Baseline](../css-keyframe-tree-counting-baseline-runtime-v1/REPORT.md).

Canonical run 5941 passes **11,752 declaration audits, 12,336 executable cases, 2,140 source fingerprints and 142 expected-false controls**. The reviewed finite ModRem witness and replacement contract are now integrated as implementation support. This transfers 28 existing audits with no new research theorem credit or normative CSS coverage. Prior outputs, unrelated library files, both indexes and the installed native build are preserved; root verification and independent terminal review pass. [Integration](../css-finite-mod-rem-library-integration-runtime-v1/REPORT.md).

Fix128 is accepted: finite mod()/rem() quotient reconstruction loses small remainders. Its one-Rust-file/one-WPT patch repairs16 failures and passes all700 selected assertions. Original-source restoration reproduces the exact baseline; root preservation and independent terminal review pass. The Lean counterexample and replacement contract have independent root replays with explicit native arithmetic assumptions. It is now installed and rebuilt: all 24 landing cases pass, and root verification preserves the source, test and staging state. Independent installation review passes; signing remains pending. [Acceptance and patches](../css-finite-mod-rem-acceptance-v1/REPORT.md), [installation](../css-finite-mod-rem-install-runtime-v2/REPORT.md).

Earlier arithmetic diagnostic: local run44048 reproduces16 calibrated finite mod/rem mismatches; all8 signed-zero/infinite-divisor controls pass. Source/build/index preservation and owned-fixture cleanup pass. Independent terminal and repair-source reviews pass; the subsequent comparison accepted this repair as fix128. The bounded Lean witness independently replays with six examples and five false controls, deriving the old rounded formula's zero result against an independent remainder of two under explicit rounding/source contracts. This is not a universal native/compiler proof or a CSS precision guarantee. [Browser evidence](../css-finite-mod-rem-runtime-v1/REPORT.md), [Lean replay](../css-finite-mod-rem-witness-root-replay-v1/REPORT.md).

Earlier keyframe diagnostic: local run24853 completes ten cases: six calibrated sibling-mutation mismatches, two passing initial controls and two known expected failures linked to bug1883255. Width and translation stay22→22→22px rather than22→44→22px across sibling indices1→2→1, including cloned and retargeted effects. The temporary fixture is removed; source/build/index preservation passes. Terminal archive review passes, independently recounting the raw outcomes. This adds no accepted fix. [Evidence](../css-keyframe-sibling-dependency-runtime-v1/REPORT.md).

At `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e`: **105 committed fixes, twenty-five pending fixes, and one held repair**. Nothing pushed. Each fix appears in one area; overlapping concerns are assigned once. Counts exclude proofs/tooling, test-only changes, alternative branch copies and unaccepted prototypes. These groups are not severity assignments. All 105 primary commit IDs were checked against branch history; each contains WPT paths and none contains research artifact paths. Fix 4 uses the Mozilla-specific WPT directory; the other 104 use the shared WPT directory.

| Area | Committed | Pending | Held | Total |
| --- | ---: | ---: | ---: | ---: |
| Selectors, Bloom filters and scoping | 10 | 0 | 0 | 10 |
| Cascade, layers and shorthands | 6 | 0 | 0 | 6 |
| Parsing, tokens and CSS math | 17 | 9 | 1 | 27 |
| Attributes and custom properties | 15 | 1 | 0 | 16 |
| Animations, timelines and transitions | 11 | 2 | 0 | 13 |
| Text and fonts | 13 | 0 | 0 | 13 |
| Layout, sizing and positioning | 19 | 3 | 0 | 22 |
| Container queries | 3 | 0 | 0 | 3 |
| Colors, images, SVG and shapes | 7 | 1 | 0 | 8 |
| CSSOM geometry and hidden layout | 4 | 9 | 0 | 13 |
| **Total** | **105** | **25** | **1** | **131** |

Fix 127 is accepted for the subgrid portion of existing bug 2037744. All ten landing cases pass, repairing eight admission failures; every other outcome is preserved across 1,532 assertions and eight rendering tests. Both builds, exact original-stack restoration and independent terminal review pass. Its patch contains two Rust files and one WPT, with fix 122 retained as an explicit prerequisite. It is now installed and rebuilt: all ten landing tests pass, with root preservation checks and independent installation review complete. It is not yet committed and is not a newly discovered issue. [Acceptance and patch](../css-name-repeat-context-acceptance-v1/REPORT.md).

Fixes 125 and 126 are accepted as separate two-path Gecko/WPT repairs. Runtime NaN propagation fixes eight failures and passes ten landing cases; finite negative-zero preservation fixes four failures and passes eight landing cases. The 1,484-assertion comparison preserves every other outcome and all eight references in both isolated phases and their composition. Original source/build restoration and independent review pass. Both are now installed in the local build:1,420PASS/64unchangedFAIL and8PASS references, with all18 landing cases passing. Final and post-lint preservation checks pass; independent installation review passes. All twenty-two pending repairs are installed; held120 remains excluded. Signing remains unresolved. [Installation](../css-round-runtime-finite-install-runtime-v1/REPORT.md). [NaN acceptance](../css-round-runtime-nan-acceptance-v1/REPORT.md), [negative-zero acceptance](../css-round-finite-negative-zero-acceptance-v1/REPORT.md).

Fixes119/121/122 are installed in the working tree and built browser after local run28306, root verification45302 and independent terminal review. The1,382-case comparison improves1,317PASS/65FAIL to1,337PASS/45FAIL, with all99 mandatory assertions and six reftests passing, no lost passes and no changed retained failures. Seven source changes and four WPTs remain; both temporary controls are removed. Signing remains pending. [Installed build](../css-accepted-119-121-122-install-runtime-v1/REPORT.md).

Release follow-up for **fix123**: installed Firefox158.0 build20261007201254 crashes during calculated-range rendering after literal rendering and CSSOM admission pass. Retained crash annotations identify a content-process `Option::unwrap()` None panic. Run69761 and root checker56524 complete; all source/index/app/test roles and cleanup are verified. This uses WPT preferences and fresh profiles; exact native-site symbolication, stock-profile exposure and memory-safety impact remain unestablished. Independent terminal review passes. [Release evidence](../css-counter-range-release-browser-runtime-v2/REPORT.md).

Fixes123 and124 are accepted as independent five-path Gecko/WPT repairs. Counter-range resolution removes the content-process unwrap crash and preserves all28 range CSSOM cases. Additive weight resolution repairs ten CSSOM failures and its rendering reference, with all32 landing cases passing. Both isolated phases and their composition preserve prior outcomes; root and independent terminal review verify full original-stack restoration. Both are installed and independently verified: all60 new assertions and both new rendering tests pass, with all1,388 prior outcomes unchanged. The combined run completes1,397PASS/45retainedFAIL and8PASS references; all159mandatory assertions pass. Signing remains pending. [Installation](../css-counter-additive-install-runtime-v1/REPORT.md). [Counter range](../css-counter-range-acceptance-v1/REPORT.md), [additive weights](../css-additive-symbols-order-acceptance-v1/REPORT.md).

Fixes121 and122 are accepted as separate standalone repairs after controlled comparison, successful original-stack rebuild, root preservation checks and independent result review. Integer stored-range resolution repairs eight failures and passes25 landing cases; saturated subgrid counts repair six failures and pass six cases. All prior passes and retained-failure diagnostics survive; all six reftests pass. Both are now installed and independently verified; commits remain pending. [Integer range](../css-integer-resolve-range-acceptance-v1/REPORT.md), [subgrid cache](../css-subgrid-saturated-cache-acceptance-v1/REPORT.md).

Fixes119 and120 passed the scoped three-phase comparison and restoration review. **Fix120 now has an installation hold** after root and independent source review identified a contextual-integer admission regression; browser confirmation and prerequisite repairs remain pending; no new defect is counted. Preserving relative-length intermediates repairs six failures and passes its eight-case WPT; deferring contextual `sign()` adds five repairs and passes its eleven-case WPT. All1,018 prior control outcomes are unchanged. **Fix120 requires119**; it is not independently safe on HEAD90. Fix119 is now installed and independently verified;120 remains held and uninstalled. Neither is committed. [Intermediate values](../css-relative-length-intermediate-acceptance-v1/REPORT.md), [contextual Sign](../css-contextual-sign-acceptance-v1/REPORT.md).

Fixes117 and118 are accepted after isolated browser comparisons and root/independent restoration review. Counter-marker handling repairs14 failures and passes all23 landing cases; integer rounding repairs13 failures and passes all37 landing cases. Both preserve all prior passes and exact retained failure diagnostics across213 subtests and two reftests. Each has a separate minimal Gecko/WPT patch; working-stack installation passes build/lint and314 subtests plus two reftests (310PASS, four unchanged expectedFAIL, two referencePASS). All60 landing cases pass. Root preservation verification and installation result review pass; signing remains pending. [Counter acceptance](../css-counter-calc-sentinel-acceptance-v1/REPORT.md), [integer acceptance](../css-integer-math-rounding-acceptance-v1/REPORT.md).

Fix116 is accepted: hidden iframe viewport readiness for SVGLength reads/conversions. Its normalized comparison improves32PASS20FAIL to52PASS, preserving28controls; restoration and independent review pass. The exact patch contains five Gecko files plus one24-case WPT. Its working-stack installation passes all101 cases across12 files, build and lint. Root verified source/index/binary and nine installed-test identities; signing remains pending. [Acceptance](../css-svg-hidden-embedder-acceptance-v1/REPORT.md).

Current investigations (not counted): reversed-counter element grouping reproduces four calibrated failures with four controls passing; powerless color conversion reproduces four failures with twelve controls passing. Both diagnostic runs preserve the tree and rebuilt binaries. The 1,559-case color comparison rejected its candidate: all16 new cases pass and22 cases improve, but two previously passing tests fail and48 retained failure diagnostics change. The original working tree and binaries are restored, and the root restoration audit passes; the candidate is not accepted. Counter arithmetic safety and element grouping are being separated into independently reviewable candidates. 

The new column/block/Grid repairs pass their own isolated landing partitions (7, 14 and 8 cases), and all 79 tests pass together and on the preserved working tree. The float repair improves four cases in a controlled 95-case comparison and passes its separate float-only 12-case comparison (baseline 8/12), with no regressions. Its paired benchmark removes 480 stale geometry reads; it is accepted as fix109 after independent review. Its fix commit will contain only Gecko and the main eight-case regression WPT. MathML repair110 is now accepted: its independent four-case WPT improves from2/4 to4/4, and integration passes299 subtests across18 files. Restoration and independent review pass. Its patch contains one native line and the four-case WPT. Both float109 and MathML110 are now installed alongside the existing working changes; all91 combined landing subtests pass. [Verified working build](../css-hidden-query-consolidation-runtime-v1/REPORT.md).

Fix101 retains its landing prerequisite on fix104 (or an equivalent repair). Preserve the containing-block cache key. See the [central ledger](../stylo-bloom-tools/BUGFIX-COMMITS.md) for prerequisites and alternate standalone branches.

Fix 111 is accepted: central baseline synthesis now uses the correct origin in vertical writing modes. Its twelve-case WPT improves from 8 passes/4 failures to 12 passes; all existing comparison outcomes are preserved. Conditional Lean proofs and source correspondence passed independent review. The two-path patch is installed; all103 combined subtests across12 files pass, including the prior91 cases. Signing remains pending. [Acceptance and patch](../css-central-baseline-acceptance-v1/REPORT.md).

Fix113 is accepted: the hidden SVG matrix repair improves the normalized comparison from32PASS/2FAIL to34PASS, preserving26 existing controls and8 availability observations. It needs no pending107 for these histories. Full source/build restoration and independent review pass. Its native commit will contain only SVGGraphicsElement.cpp and the eight-case WPT; working-tree installation passes build/lint and all eight integration cases. Its [research and native commit recipes](../css-hidden-svg-matrix-commit-queue-v1/README.md) are ready; signing remains pending. [Acceptance](../css-hidden-svg-matrix-acceptance-v1/REPORT.md), [installed build](../css-hidden-svg-matrix-install-runtime-v1/REPORT.md).

Pending fixes: 106 table columns, 107 skipped block lines, 108 Grid, 109 floats, 110 MathML, 111 central baseline origin, 112 integer CSSOM geometry, 113 hidden SVG matrices, 114 SVG length conversion, 115 SVG absolute-unit factors, 116 hidden SVG embedding viewport readiness, 117 calculated counter marker handling, 118 CSS integer math rounding, 119 relative-length intermediates,121 stored integer bounds,122 saturated subgrid counts,123 calculated counter-range export, 124 additive-symbol weight resolution,125 runtime Round NaN priority, 126 finite Round negative-zero preservation, 127 contextual subgrid name repeats, and128 finite mod()/rem() remainders. Repair120 contextual Sign folding is held. Fix120 requires119 and is held for the contextual-integer admission regression; 119 is now installed;120 remains held and uninstalled. The latest signed retry (24 October, session 90997) failed in 1Password. HEAD, all 925 staged research payloads and the restored source/build state remain verified unchanged; no unsigned substitute was created.

Expanded fix114 is accepted: two Gecko files and three WPT files with25 cases. The isolated comparison improves35 PASS/16 FAIL to51 PASS and preserves all26 controls. Full restoration and independent comparison review pass. Combined-stack installation passes all25 cases, build and lint; independent installation review passes. This expands114 without adding a new fix number. [Acceptance](../css-svg-length-conversion-acceptance-v3/REPORT.md). [Research and native commit recipes](../css-svg-length-conversion-commit-queue-v3/README.md) are finalized; signing parents remain unset.

Fix115 is accepted: three incorrect Q-related SVG constants produced wrong conversion values and animated positions. Its isolated comparison improves26 PASS/8 FAIL to34 PASS, preserving18 existing controls; original-stack restoration and independent review pass. Four finite Lean results independently corroborate all49 corrected factors against exact CSS ratios within the stated engineering tolerance. The native patch contains one Gecko file and two WPT files (16 cases). Working-stack installation passes build/lint and all16 integration cases, preserving the prior changes and test files. Signing is pending. [Acceptance and patch](../css-svg-absolute-factor-acceptance-v1/REPORT.md). [Separate research and native commit recipes](../css-svg-absolute-factor-commit-queue-v3/README.md) are finalized.

## Current investigations and supporting evidence

The infinite-value/contextual-step Round diagnostic now reproduces 14 calibrated numerical failures with 24 passes. All strict controls and four detached policy observations pass; independent terminal review verifies preservation and cleanup. A conditional canonical-value guard passes extracted helper checks but remains uninstalled and unaccepted. Known contextual integer support gaps in subgrid name repeats and easing must be addressed; no new fix count is added. [Diagnostic](../css-round-infinite-value-step-runtime-v1/REPORT.md), [prerequisite design](../css-contextual-integer-prerequisite-design-v1/DESIGN.md).

The 42-case Round diagnostic (session 61360) completes with 11 PASS and 31 FAIL: 29 calibrated numerical mismatches and two nonnormative integer-admission policy differences. All controls pass and the installed source/build/index state is preserved; no new fix is counted. Independent terminal review passes. [Diagnostic](../css-round-numerical-baseline-runtime-v1/REPORT.md).

Canonical run 77965 now passes 11,724 declaration audits, 12,312 executable cases, 2,135 source fingerprints and 131 expected-false controls. Four existing Round class-level support laws and eight controls are integrated; independent results review passes. This adds no new normative CSS coverage or research theorem credit. [Integration](../css-round-knowledge-library-integration-v1/REPORT.md).

The preceding finite Round, remainder-capacity and binary32 integration checkpoint32137 passes **11,720 declaration audits and12,304 executable cases**, with2,133 source fingerprints and127 expected-false controls. Previous outputs and both indexes are preserved; independent execution-result review passes. This is partial specification coverage, not a proof of native/browser floating-point refinement. [Integration](../css-round-scalar-capacity-library-integration-v1/REPORT.md).

The counter/additive comparison completed successfully; the two repairs are accepted as123 and124 after root and independent restoration review. The finite parse-time `round()` negative-zero lead subsequently became accepted fix126 and is now installed. [Comparison](../css-counter-additive-comparison-runtime-v1/README.md), [new lead](../css-round-parse-negative-zero-audit-v1/REPORT.md).

The counter-range probe now reproduces a content-process crash with `range: calc(1) calc(1)`. Literal rendering and calculated CSSOM admission pass; rendering then panics on `Option::unwrap()` in `Servo_CounterStyleRule_IsInRange`, matching the source audit. Root verifies all source/index/binary/test preservation. Independent result review passes; the later four-phase comparison accepts the repair as123. The counter-range repair is now counted as123; the installed158.0 release now reproduces the content-process panic under WPT preferences; memory-safety impact remains unestablished. [Browser evidence](../css-counter-range-isolated-browser-runtime-v2/REPORT.md).

The additive-symbol diagnostic completes32 CSSOM cases with22PASS/10FAIL and one eight-row rendering reftestFAIL. Root preservation verification and independent result review pass; the later controlled comparison accepts the additive repair as124. [Browser evidence](../css-additive-symbols-order-browser-runtime-v1/REPORT.md).

The whole-auto-fill Lean extension passes root replay and independent review: eight audited declarations connect cached counts to whole-pattern repetition, truncation and trailing unnamed groups. Twenty literal WPT oracles and four rejected false claims pass. These are conditional model results, now registered in the canonical library as part of the subgrid integration; registration adds no new research theorem credit or accepted fixes. [Root review](../css-subgrid-whole-autofill-root-review-v1/REPORT.md).

The integer-range/subgrid retry92779 completed all four comparison phases and successfully rebuilt the original working stack. Baseline291PASS/48FAIL improves to299PASS/40FAIL with the range repair,297PASS/42FAIL with the cache repair, and305PASS/34FAIL combined. All31 targeted landing cases and six reftests pass combined, with no lost passes or changed retained-failure diagnostics. Final restoration verification and independent terminal review pass; these are now accepted fixes121 and122. Five general Lean prefix results across two capsules pass root replay and independent review, with explicit source-correspondence premises.

The integer-range/subgrid diagnostic is now complete: session83357 and root checker93382 exit0. All82 subtests finish (66PASS/16FAIL); eight new calibrated failures comprise six calculated steps() range failures, one calculated-zero subgrid mismatch and one large-positive count mismatch. The56 existing controls have48PASS/eight expectedFAIL and no unexpected failures. All505 preserved roles,67 sources,36 native differences,925 staged paths and11 installed test identities remain intact, with all three fixtures removed. The subsequent339-subtest/six-reftest comparison accepted these as fixes121 and122. [Browser evidence](../css-integer-resolve-range-browser-runtime-v1/REPORT.md).

Context-dependent CSS `round()` now reproduces four calibrated opacity discrepancies, with two controls passing. The target returns1 instead of about0.667, or0 instead of about0.333, while constant expressions return the expected values. Browser/root preservation and independent result review pass. The one-file repair passes independent source review and 1,976 extracted-helper checks. The four-phase comparison (session 18353) completed its 658-case baseline, then stopped before candidate phases because the both-infinite control returned 1 instead of 0. All eight added parse-time signed-zero cases passed, providing no repair witness. The unchanged rejection policy triggered original-stack restoration; root checker40823 and independent terminal review verify its successful completion. The separate15-case diagnostic now completes10PASS/5calibratedFAIL with all10controls passing: four Pow-observed signed-zero failures and one deferred-value/infinite-step failure. Root preservation verification and independent terminal review pass. No new fix is accepted. [Follow-up](../css-round-baseline-surprises-browser-runtime-v1/REPORT.md). Six supporting Lean results pass root replay; floating-point reconstruction remains a separate obligation. This is not an accepted fix yet. [Evidence](../css-round-context-quotient-browser-runtime-v1/REPORT.md).

The viewport-unit follow-up is included in accepted fix114. Eight new first-read failures are repaired in the isolated comparison; combined-stack installation passes all25 main cases. [Comparison](../css-svg-length-readiness-comparison-runtime-v1/REPORT.md).

The earlier four-case hidden-iframe diagnostic returned30px instead of its predicted20px and was correctly rejected by its classifier, with all inputs preserved. The eight-case follow-up and revised declarative assessment above supersede that diagnostic’s initial interpretation; the original evidence remains unchanged. [Diagnostic review](../css-svg-length-hidden-provider-results-review-v1/REPORT.md).

The font-unit follow-up is now included in accepted fix114. A separate zero-axis probe reproduces four calibrated getter discrepancies (about5e-21 instead of0), with source/index/test preservation. This remains unaccepted pending interoperability and compatibility analysis; no practical or security impact is established. [Probe](../css-svg-length-zero-axis-runtime-v1/REPORT.md), [decision](../css-svg-length-zero-axis-decision-v1/DECISION.md).

The ancestor-overflow investigation has 96 calibrated, stable browser observations: every leaf rectangle is correct, but 18 large-coordinate cases miss the leaf during hit testing. Native tracing now observes both the lost overflow coverage and the earlier absolute-frame query clipping/rejection; independent replay verifies all 30,065 trace records and complete source/build restoration. A repair must preserve coverage through cached bounds and query transport. Nine bounded rendering snapshots now corroborate missing leaf pixels in two large-coordinate cases, with all seven ordinary/reset/alternating controls passing. These are headless drawSnapshot results, not presented compositor pixels. The extreme-range specification boundary remains unresolved, and no security impact has been established. [Rendering evidence](../css-ancestor-paint-pixel-runtime-v1/REPORT.md), [independent pixel review](../css-ancestor-paint-pixel-results-review-v1/REPORT.md). [Causal analysis](../css-ancestor-oof-causal-analysis-v1/REPORT.md), [independent review](../css-ancestor-cancellation-oof-results-review-v1/REPORT.md).

The standalone CSS model now includes the reviewed CSSOM View hit-observation relation. The earlier counter descriptor integration passed 11,699 declaration audits and 12,284 executable checks, registering eleven existing support results once with eight executable controls and no normative coverage increment. The later finite Round integration above is the current canonical result. [Counter descriptor integration](../css-counter-descriptor-library-integration-v1/REPORT.md). The [subgrid integration](../css-subgrid-library-integration-v1/REPORT.md) registers19 existing results and28 checks with explicit scope limits. The earlier numeric-support integration registers twelve existing dyadic/remainder support results and twelve examples; all prior results and staged changes are preserved. The color integration registers seven existing results and six examples; the subsequent counter-provenance integration registers five existing implementation-support laws and six controls. Conditional machine bounds and provenance remain separate from CSS coverage. [Latest integration](../css-numeric-support-library-integration-v1/REPORT.md). [Color integration](../css-relative-color-channel-library-integration-v2/REPORT.md), [independent review](../css-relative-color-channel-library-integration-review-v1/REPORT.md). [Counter integration](../css-counter-library-integration-v1/REPORT.md). The earlier conversion integration registered 14 existing proofs once, with five executable examples; this adds no new research-proof count. [Conversion integration](../css-unit-conversion-integration-v1/REPORT.md). The new model distinguishes actual hit targets from overlap-ignoring enumeration and proves conditional pruning properties for a supplied rendered state. It does not prove native culling, full hit testing or complete CSS coverage. [Integration](../css-hit-observation-integration-v1/REPORT.md), [independent review](../css-hit-observation-integration-review-v1/REPORT.md).

The composed flex arithmetic/fragmentation candidate remains rejected: it improves 398 of 4,122 core subtests, but follow-on checks expose a large nested last-baseline regression. Separate ordinary-size vertical-lr baseline observations and exact-origin prototypes remain research work. Their model/helper checks do not establish a safe consumer migration or another accepted fix. [Comparison](../css-flex-fragment-composed-extras-results-review-v1/REPORT.md), [nested evidence](../css-baseline-nested-edge-execution-v3/REPORT.md), [placement plan](../css-inline-placement-plan-v1/REPORT.md).

## Individual fixes

### Selectors, Bloom filters and scoping

| Fix | Repair | Native + WPT commit |
| --- | --- | --- |
| 1 | StyleBloom clear loses evidence of earlier counter saturation | `d855b3483b493c7e596b5d1d30d613fa7b7e2db5` |
| 2 | Recursive relative-selector Bloom construction overflows on deep subtrees | `93a062cded54c974dff03ce2618aaf612a9c8d61` |
| 5 | Nested scopes choose the first outer scope's inner root instead of the closest matching inner root | `075be5516374d31c55a1e0f71b3fa80591042503` |
| 6 | Shadow-host traversal reports an unmatched scope-end selector as a limit | `a46e5310cd604adff10e914e82e8a326b9fb7957` |
| 7 | Scope root is treated as its own scoping limit, contrary to the April 2026 draft update | `78c11c75170af5480a88fd9682db41183760f652` |
| 8 | Relative-selector result cache reuses scope-dependent :has() matches across different scope roots | `d4a2b600f078d4c29e6dd8e0f1668121941a64e5` |
| 9 | Filtered nth-index cache reuses sibling counts across different scope roots | `92c013c16908bd30593ca7385b24dad1be4288dc` |
| 10 | Scope-limit changes stop invalidation inside a relative selector instead of reaching the enclosing rule subject | `64ac54569f1cc202172ded92ee23ba749cd3284e` |
| 11 | Filtered nth positions are not propagated when a relative anchor has a non-subject tail | `b1b1bacb9406d75f35648d40a70ce9ad0fc3ab69` |
| 12 | Scope wildcard revalidation gives equal nth results for elements with different real filtered positions | `f4b34bf7fef125857979a210616d201e28eefded` |

### Cascade, layers and shorthands

| Fix | Repair | Native + WPT commit |
| --- | --- | --- |
| 3 | False-supports import incorrectly establishes layer order | `5d3638a91adf7b662041e192d121c7fd91c86f0a` |
| 4 | Important user/UA declarations retain normal layer order | `e28cb48d656ba83097fb0960734e4317252e7d81` |
| 16 | Variable-bearing shorthand cache reuses another declaration after partial revert-layer | `11482ee213bf63c749b6d205c2c7591d783bdaa8` |
| 23 | logical-shorthand | `e27beeac5129d7331f8aca9babbe6bfc199d7d24` |
| 38 | nesting-specificity | `c57d0c806d94c6e6dd56e23acdeed847c5ea1571` |
| 69 | all-shorthand-logical-order | `074086719e445ca72d3056f7fbf793af5e69d6f6` |

### Parsing, tokens and CSS math

| Fix | Repair | Native + WPT commit |
| --- | --- | --- |
| 13 | Relative-length round simplification loses negative zero with infinite steps | `708b914901eeb7a2d348855c2efcf099e6003317` |
| 20 | clamp-nan | `a4fe7dd06fd7dac3924b2dc9aea4f57103eb1b98` |
| 21 | mod-rem-infinity | `bfbce1cc7e9a5b53d5cc00317a265d7141428997` |
| 35 | bad-url-recovery | `83bc2bd3922697d44a602bf48902e821796a60e3` |
| 59 | unit-token-classification | `26e0fa16e89eacd9fd9cab0ce6bb1be813d9e406` |
| 60 | identifier-start-escaped-newline | `09b008b3320fa29fcbcf081b252053e3721c5e10` |
| 62 | numeric-compensated-exponent | `4391deb4751a8be2be98e838360f00c94808c5d5` |
| 63 | quoted-eof-fallback-endpoints | `2d658a9c5aa4139dc7f196933511abf4a594163f` |
| 64 | quoted-eof-backslash-parity | `89bad2d8b5260ad5fc9d5660a3a18a09433902e3` |
| 65 | quoted-eof-escaped-terminal-quote | `ed9505d25ee4333c1764acc173f95f9517ca9b07` |
| 66 | parser-depth-limit-declaration-recovery | `55d251b7a90003546994f6576e5ee78e8fa07cb2` |
| 67 | declaration-fallback-top-level-curly | `095c5be548a2bddf5f3ff01e01da66c6098a8ee5` |
| 68 | declaration-substitution-publication | `780495d90a85052cff69713f1086180253cb9730` |
| 81 | registered-token-boundaries | `34e4e755cb81332819e56457f5fb68b9b305c394` |
| 84 | variable-trailing-whitespace-token-boundary | `bccea9c1fffc59e41a9f9bef16fcaf0056ff1f10` |
| 85 | variable-escaped-trailing-whitespace | `fff2d758ef6bb39b4465cb072767bc5db6d5e09f` |
| 86 | variable-backslash-newline | `246f1ff43250ec24e177f03cde923c9d11ee86e9` |
| 117 | Calculated counter values collide with the reserved reset marker | `33ae2e8349e96d1778603385d39cdb74b26a12df` |
| 118 | Premature binary32 addition misrounds computed integers | `d68543e601c40bf64d1777dfa6b7c79b838f21ae` |
| 119 | Relative-length conversions normalize calc intermediates too early | `6a363fc372c9cc0734faee64ab20f03bc762e97c` |
| 120 | Contextual sign() folds before resolving its unit basis | Held for contextual-integer admission prerequisites; requires119; not installed or committed |
| 121 | Integer resolution drops the stored numeric range | Installed and verified; signing pending |
| 123 | Calculated counter-range bounds crash during rendering | Installed and verified; signing pending |
| 124 | Additive-symbol weights use representation-dependent ordering and inconsistent range projection | Installed and verified; signing pending |
| 125 | NaN is lost during round() numeric resolution | Installed; signing pending |
| 126 | Finite round() upper bounds lose negative zero | Installed; signing pending |
| 128 | Finite mod()/rem() lose small remainders through quotient rounding | Installed; signing pending |

### Attributes and custom properties

| Fix | Repair | Native + WPT commit |
| --- | --- | --- |
| 22 | attr-numeric | `499c0c6b72ac4bc0a6396bffa3fa0d71665409ce` |
| 52 | attr-namespace-cache | `3aa7d25635ff9dc3bc105269dd9b7b13b5f80cb0` |
| 53 | attr-invalid-entry | `fd9c07e1130bcb68684c25e7527f5b0ff3c3bd73` |
| 54 | attr-fallback-preparation | `7822bb6d17b1381cdb3e56deb20c5ec3e078adec` |
| 56 | attr-typed-fallback-eligibility | `e3ba54f6f826fe265eb5bc4731f66f64465dd47c` |
| 57 | attr-noncustom-dependency-collection | `3892ab844694fedd987f5ce1dd2165f53fc2dbed` |
| 58 | resolved-unit-dependency-summary | `58200fa81a6f92f92a1898ba2866a2fbcbac0daa` |
| 71 | registered-initial-computed-value | `6aa2138c144aa6eee8e07aac77e7a68a8c7f7617` |
| 72 | registered-inherit-invalid | `3a01fc986c7974161aadf4bfafe65c234b036b07` |
| 73 | registered-substituted-inherit-restyle | `60bf34f48ac63ca595d519c1e0c2b4a2fa731b66` |
| 74 | custom-property-live-count | `0cac5c270615d04239bd4a4024a3ab5ffd0d24ae` |
| 75 | custom-property-enumeration-shadowing | `90ffac0a5e4076b6117ca152249f342a13995ee3` |
| 76 | custom-property-equal-payload-taint | `e04d672a735edcf0e6529c854207b5ee9555ea7c` |
| 77 | attr-taint-half-open-ranges | `8c04b6787e36c9ee42fec440103cf33372c097f1` |
| 83 | attr-leading-whitespace-origin | `ad608a212bd8d7f77a2f0b9df62df18d33c12b96` |
| 130 | Ordinary keyframe attr() skips attribute preparation and uses a dummy provider | Installed and verified; signing pending |

### Animations, timelines and transitions

| Fix | Repair | Native + WPT commit |
| --- | --- | --- |
| 15 | Saturated animation iteration indices alias infinity, lose direction, and suppress iteration events | `0a81e1f36ab08a6d67ddd0bdd590e4661ff9b0a1` |
| 19 | transform-deferred | `c9274972124198e8f8466ddcd667d1c23cb044ec` |
| 43 | timeline-pseudo-axis | `0af700c67a5aef6048b19b72350320cd1fe82346` |
| 46 | animation-composite | `6b8dc654e8d017562533308571af23c3099fd5cc` |
| 70 | registered-keyframe-substitution | `188644f6d9833b485f35c2abcfad23cef2c5e9f7` |
| 78 | animation-retained-endpoint-taint | `4b4a00e707583382f4773039f13a4f335f48f41a` |
| 79 | animation-underlying-base-taint | `2c09cb2e4ff81bbc4af65d1d069517420b9c1529` |
| 80 | animation-interpolation-taint | `ede7ceb101d83f0c4044585a5a687f5286b072c9` |
| 82 | animation-invalid-publication | `d63735091bf8dc469d900ddba56e8a43bcac26d7` |
| 87 | view-transition-initial-type-deduplication | `2db94380203863bced9e3a7147505beabaaf7599` |
| 88 | view-transition-type-style-invalidation | `c67505af9aae8c06150d74d81a67011e7921d3cd` |
| 129 | Recompute contextual keyframes after CSS duration reactivation | Installed and verified; signing pending |
| 131 | Publish active keyframe attribute dependencies | Accepted and installed; signing pending |
| 132 | Refresh contributing keyframes before commitStyles | `d477d0c331057847673d3e25646b3f39cd38c1a5` |

### Text and fonts

| Fix | Repair | Native + WPT commit |
| --- | --- | --- |
| 25 | sigma | `8e78ffd376c4d478b5d614f568f3bf09d894ad8b` |
| 40 | text-overflow-line-state | `c348436003653a08b6766339d9e0c8f89084d062` |
| 41 | tab-zero-intrinsic | `eca9efde2991b5a458d23efd1c6d33d58fdf4a77` |
| 42 | font-threshold | `9da730d5ebd6cb59a0a5b2a666d6679808d58889` |
| 44 | font-priority | `9cca10125782ebe2bf076a5e5d8becdacae5ff16` |
| 45 | root-rlh-zoom | `43afd2c6f3500cee4a2dd07d07eb14aca723fae3` |
| 47 | text-emphasis-pua | `bbf5a4095f85fb250ea442695a311f2547ffdc19` |
| 48 | negative-ligature | `8ee543a6ff23cc097f54f1c3e984f7d5f7e56fea` |
| 49 | complex-utf16-ahom | `39ce7571a61097a80d5bf07adbc3ae48a2f0262e` |
| 50 | worker-font-removal | `32ba35ffb9a17f5e91df5c56f01a06a452dfdc8a` |
| 51 | hyphenation-coordinate | `18871240dc7d077bf223822013e7a50cf581e2d1` |
| 55 | mathml-token-range-origin | `f843fd7568f30e14e664c37c36544d8d88e8c1bb` |
| 61 | loaded-fontface-descriptors | `6bd0b00dcff5514a3234423787920ed44491a4bc` |

### Layout, sizing and positioning

| Fix | Repair | Native + WPT commit |
| --- | --- | --- |
| 24 | grid-abspos | `7f5a1105253e60b283174ea890862b1943e8702a` |
| 26 | sizing-stretch | `2a61f0b7433628e8a77159b968ca570632591b8e` |
| 29 | table-span-spacing | `98fd7a22a32744ab429828d609cf5bfb3affc4a5` |
| 33 | abspos-auto-margin | `f67ddfaa3dc328d7359c7fca56e61a1249e1ee96` |
| 34 | block-flow-collapse | `e09ffb35c0b47c6c29c43c64d887fb524b5e7423` |
| 39 | scroll-fixed-anchor | `e606244c4546e522cf4a6e86dac98e216305003b` |
| 89 | sticky-explicit-inset-auto-alias | `fdd7dcb11653c3c3808557708969c7e1eb803b82` |
| 90 | sticky-auto-inset-normalization | `983931aa5fad14b5d86120cfd66635be7f1b844f` |
| 91 | sticky-containing-block-writing-mode | `67bcf64fc28f181859c6dc726e532430475e49e7` |
| 92 | sticky-negative-inset-overflow | `d3c505adc9e99a293a44bde5a3f04557aac255d0` |
| 93 | flex-baseline-cross-size-sum | `71a523a4c5267ba4c07a59329e57317fafc31f1b` |
| 94 | sticky-finite-sentinel | `68686da757592b0de4d1b064966d81f8b9265fc1` |
| 95 | flex-line-cross-size-sum | `958e63a947e4a97dd224d60c5699b42061af5422` |
| 96 | flex-relative-item-exported-baseline | `b4894d6329df7b9cae8f81cbd72e89d61f1b4adc` |
| 97 | scroll-container-natural-baseline-border-conversion | `9980b7b7a0fb894c963a69c0ef0e17b12e6d6350` |
| 98 | flex-baseline-percentage-padding-measurement-cache | `f5926c6dab500569fc2345aade1a43aebc7e3796` |
| 99 | flex-vertical-rl-overflow-container-position | `a6c78d9502504d07432fd0c81c168847bbfa25a4` |
| 100 | overflow-continuation-relative-position | `2b769488eef1e2ae18ed27d014402591110e3ed1` |
| 101 | flex-table-auto-caption-percentage-height-cache | `6cf27eadddf9e63d9bfbcc87ff2bf354e091ae7c` |
| 111 | central-baseline-synthesis-origin | `ee836eba6ca6070cec5c8a25208fd51d9df0a7f0` |
| 122 | Expanded subgrid line-name counts overflow or narrow before capacity checks | Installed and verified; signing pending |
| 127 | Contextual subgrid name-repeat counts are rejected (known bug 2037744) | Installed; requires122; signing pending |

### Container queries

| Fix | Repair | Native + WPT commit |
| --- | --- | --- |
| 14 | Name-only container queries do not invalidate after ancestor name changes | `238710ff9db7f54449c075bf80c7c3d40b43387a` |
| 27 | query-attribute-wrappers | `16ff45a117b149ec95fc633c7ac18d8a1c38ca0b` |
| 28 | query-content-box | `ef3d32280505b7fb6c1b35989d7e74c56f1aee0a` |

### Colors, images, SVG and shapes

| Fix | Repair | Native + WPT commit |
| --- | --- | --- |
| 17 | color-missing | `82b254686378e57711759c238b975cdf4678a287` |
| 18 | color-zero-prefix | `591b3e12567865c7e047530753e510c54d18b3db` |
| 30 | polygon-intercept | `06be3d7e722c55ffbff97e6be237bd39a4920295` |
| 31 | stroke-reference-box | `96e0ad8c6a0ae58b9ce8c47579c9bc06f67fc1e2` |
| 32 | object-fit-partial | `66fb24648a15769f80c2adf37030e68598dae68f` |
| 36 | svg-empty-mask | `065183ac8449800f0dbef3c23a15be3863ca60ae` |
| 37 | image-zero-mask | `6bb2557507bcd6346664e539f9f4b9628d8e6078` |
| 115 | Incorrect SVG quarter-millimeter conversion factors | `fa9dff982cecc234294981fb8f668767816f1652` |

### CSSOM geometry and hidden layout

| Fix | Repair | Native + WPT commit |
| --- | --- | --- |
| 102 | domrect-layout-coordinate-double-precision | `c0e8c7fd1deb9320b0bae747c043c100ac842f49` |
| 103 | cssom-integer-translation-precision | `7309af28e360d5d9544eb04dbbbe7f74a102e164` |
| 104 | hidden-flex-skipped-layout | `29611cb584fdd0e54d5e7f7e0d70ad47cfff1653` |
| 105 | hidden-absolute-child-invalidation | `f8104759d383bd324cdda1e78e3229902e97fb39` |
| 106 | hidden-table-column-provider-query | `29e2df85a4a979f7aab73485b7d77ce4b1ea6bf4` |
| 107 | hidden-skipped-block-line-query | `e6c73b63765376dbf74daaa0d4f489ea615a2888` |
| 108 | hidden-grid-skipped-child-query | `a578671e967f9eac837497481d2012b288b98b5b` |
| 109 | hidden-float-owner-query | `8a5df95cf9d56c8d0dfde9939f2a7c92151f092c` |
| 110 | hidden-mathml-skipped-child-query | `aaca499a3257e1f196b9dacace42041ab523f399` |
| 112 | Integer offset, scroll and client geometry precision | `b616622d2cd7fa69376261c600f3c9a2ba1e4da4` |
| 113 | Hidden SVG viewport matrix queries | `cc52e66ca64a4afde2f5d078f1326249ff106033` |
| 114 | SVG length reads and conversions use stale context | `53adf727ea052bb6a08b60be8bbec76c8abccc74` |
| 116 | Hidden iframe SVG viewport readiness | `9c2257a80e3ff6c97080657f5c9a08b717f34cfa` |

Expanded fix 112 repairs ten offset/scroll/client precision failures. All 40 regression checks pass; all 130 controls retain their outcomes and diagnostics (162 PASS/8 retained FAIL overall). Restoration and independent review pass. The exact four-file Gecko/WPT patch preserves the two distinct rounding policies, backed by 21 offset/scroll and 14 client arithmetic results. [Acceptance](../css-cssom-integer-geometry-acceptance-v1/REPORT.md). The expanded fix is installed; its build, lint and all40 integration checks pass. [Installed build](../css-cssom-client-install-runtime-v1/REPORT.md).

The ancestor-overflow hit-testing investigation remains unaccepted. Relative rejection and the earlier absolute-frame clipping/rejection path are now traced and independently reviewed. Its extreme-range specification boundary remains unresolved. The client-size correction is part of expanded fix112 and adds no new fix count.
