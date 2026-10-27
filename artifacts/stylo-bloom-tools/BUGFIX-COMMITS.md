# CSS verification bugfix commits

Latest signed fixes: calculated jump-none minimum `ea6cde0db70c` now includes its two expectation corrections; calculated cubic-bezier x ranges `8ccca4c4901c` includes its WPT and two expectation corrections. All 133 accepted fixes are committed; repair 120 stays held and excluded. The current local browser contains both fixes. See the [signing record](../css-local-signing-20261027-v4/CHECKPOINT.md).

| Fix | Native/WPT commit | Preceding evidence |
|---|---|---|
| 134: calculated cubic-bezier x range | `8ccca4c4901cc778c30485a3b85c69c0aa62724f` | `df58b1c6808b1cf4c77403c5b99a60487fec88ce` |
| 133: calculated jump-none minimum | `ea6cde0db70c1fc85baf4fb8d0adc35b83545477` | `56c3cda25c7c6e167db523cb4365ab20dc716422` |

Twenty observed failures repaired; 22 targets pass, 55 controls unchanged, all 77 restored outcomes exact. Tentative P3 conformance. Source/spec audit and browser reproduction found this issue; the separate Lean model supports conditional laws. No full bug 2037743, clean-upstream browser or security claim. Earlier checkpoint text below is historical.


**133 accepted fixes: 133 committed locally, 0 accepted pending, and 1 additional held repair excluded.**

| Area | Committed | Accepted, pending |
|---|---:|---:|
| Selectors, Bloom filters and scoping | 10 | 0 |
| Cascade, layers and shorthands | 6 | 0 |
| Parsing, tokens and CSS math | 26 | 0 |
| Attributes and custom properties | 16 | 0 |
| Animations, timelines and transitions | 16 | 0 |
| Text and fonts | 13 | 0 |
| Layout, sizing and positioning | 22 | 0 |
| Container queries | 3 | 0 |
| Colors, images, SVG and shapes | 8 | 0 |
| CSSOM geometry and hidden layout | 13 | 0 |
| **Total** | **133** | **0** |

| Fix | Gecko/WPT commit | Preceding research |
|---|---|---|
| 121: integer-stored-range-resolution | `231120268a02a948a08a0180fe693997c34e355f` | `55c31aba8fcfd32c10802a8bb8b00a1a53a59d8d` |
| 122: saturated-subgrid-line-name-cache | `cef7cba29d6c1796af9c3aa17f9468ceb747fe6d` | `d129e631ca88e736e28bdb67df7749cd6a1d86f1` |
| 123: counter-range-calculated-bound-export | `412a58792433a108e1dd9f97c026a07369fe40f8` | `96f07a02d0dbebcc120dcf2b51aaca0b4b0ec09b`, `422eaa2798f486d867e8ac127935c6df1b493c00` |
| 124: additive-symbol-resolved-weight-ordering | `e9947a86cff12ff54ef6c6b993f8a41e4f75bea3` | `96f07a02d0dbebcc120dcf2b51aaca0b4b0ec09b`, `541c2f3cf4a406e974dc5f28f95ad1f32507c98a` |
| 125: round-runtime-nan-propagation | `ac466b84f24739b473d59fe26707963ad40ffede` | `b1a7c887f651890edbc0bdcd545f1d0f27043aea` |
| 126: round-finite-negative-zero-bound | `cf7e06c3e1adf7265acfb5a9c9fad025fffa1cd8` | `75c3a91d48e2403a672cb3c544a92216dbb5eb5c` |
| 127: subgrid-contextual-name-repeat | `6760efc232f48a9ce4a92442cd2d3a4f72b78fd0` | `faf46a8f43d95106b2e0c9c1b3d2f6fc3dfdea45` |
| 128: finite-mod-rem-quotient-reconstruction | `354b58aa74696e71f7d824e3c117aad09eca2754` | `6365632906ba37c5c698d9e72f94c9ca26a1fd92` |
| 129: css-duration-reactivation-keyframe-properties | `3fcacaa09e010bcb9fb41ab46b165d316e73dc43` | `a10ed0ad617c0f1eb52eaf3aed4fb8c86338441a` |
| 130: ordinary-keyframe-attribute-initialization | `f8f045833d29a20b2b50531b078739d56274f3e7` | `4529efd84c0dd82561df5ce1184737940cba6ce6` |
| 131: active-keyframe-attribute-dependency-publication | `9b8a7506422f4f9b5e8ef31bc08c9bcf161f6bd9` | `3df09487e3d72e3fbe00104bffeca5eabd242fb4` |

All 23 signed-item receipts passed exact parent/content and configured-key signature verification: 11 native/WPT commits and 12 research commits. Shared counter evidence precedes both fixes 123 and 124; prior research dependencies remain in the authenticated recipes. Existing fix 132 and held fix 120 are unchanged. Per-fix prerequisite, standalone, release-exposure and formal-scope caveats remain intact in the JSON records; signing is not a new build, browser test or clean-upstream validation. Source and binary bodies were preserved; main staging is empty, and nested-library index state is retained. Remaining prototype work is not counted as accepted fixes.

The descriptor/operation prototype passed the normal Firefox and GTest-host builds, ten native GTests and the exact browser comparison: 166 unchanged subtest outcomes (162 PASS, four known provider FAIL), two passing crash endpoints and eleven normal harness endpoints OK. Owned-process and fixture cleanup, source/binary/research preservation and both index checks pass. The earlier wrapper failures remain recorded; separate successful validation accounts for the exact GTest packaging copy and the 23 signed commits. This adds no accepted fix or native-refinement result. The computed-name model is now integrated and passes the full checker: 11,830 declaration audits, 12,424 executable cases, 170 expected-false cases and 2,153 source fingerprints. The exact old cases, axiom map and unrelated sources are preserved; 25 statements and 15 cases transfer from reviewed research. Raw CSS name parsing and native refinement remain explicit gaps. Next are presentation-backed descriptor tests and compact rule ownership. A direct transition-start mutation can leave the prototype descriptor naming an old snapshot; this is not an observed rendering bug. Current-provider resolution, animated cycles and complete memory reporting remain open. [Full model check](../css-variables-computed-name-library-application-v1/REPORT.md). [Capture report](../css-keyframe-operation-descriptor-capture-runtime-v1/REPORT.md).

Historical checkpoint text follows; its counts and future-work statements describe that earlier state.

**131 accepted fixes: 120 committed locally and 11 awaiting commits.** One additional numbered repair remains held and excluded.

| Fix | Gecko/WPT commit | Preceding research |
|---|---|---|
| 117: counter-calculated-integer-sentinel | `33ae2e8349e96d1778603385d39cdb74b26a12df` | `2f1085d3c8ee068bb012a906b664b5e7a7450d05` |
| 118: css-integer-math-rounding | `d68543e601c40bf64d1777dfa6b7c79b838f21ae` | `1690a8cd5886ff68209dd3ea1dcbe97b9784d264` |
| 119: relative-length-nonfinite-intermediates | `6a363fc372c9cc0734faee64ab20f03bc762e97c` | `49862ae74751926b2c3600fe6cf1625e5b31c691` |

Six signed commits passed exact parent/path/blob checks and configured-key signature verification. Each of fixes 117–119 has one native/WPT commit, preceded by its research. The disjoint research selections add 65, 48 and 146 paths. Fix 118 reuses 40 exact files from the preceding fix 117 research commit; fix 119 retains its already-committed reviewer-log dependency. All working native bodies remain unchanged, including later edits sharing committed files. Main staging is empty; existing nested-library staging is preserved. Signing ran no new browser tests and does not establish clean-upstream independence.

Earlier checkpoints follow; their counts describe their recorded state.

**131 accepted fixes: 117 committed locally and 14 awaiting commits.** One additional numbered repair remains held and excluded.

| Fix | Gecko/WPT commit | Preceding research |
|---|---|---|
| 109: hidden-float-owner-query | `8a5df95cf9d56c8d0dfde9939f2a7c92151f092c` | `854c39c17bbd177e49addfc48b56872b03a836e0`, `6b9f50396a7bd72368a35c39a71de14dc564f6c9` |
| 110: hidden-mathml-skipped-child-query | `aaca499a3257e1f196b9dacace42041ab523f399` | `d492f094405606062eb943e0240bacee30c8d1a5` |
| 111: central-baseline-synthesis-origin | `ee836eba6ca6070cec5c8a25208fd51d9df0a7f0` | `54e8683a6dfbfa686d801f2a6285d81938c5cef5` |
| 112: cssom-integer-geometry-precision | `b616622d2cd7fa69376261c600f3c9a2ba1e4da4` | `c67102a4c8f6ad1a7190f17a8c1213e4bce5e0a8` |
| 113: hidden-svg-matrix-viewport-query | `cc52e66ca64a4afde2f5d078f1326249ff106033` | `bf0a7cb4a980d0df51302ab0e7771d068b353c90` |
| 114: svg-length-context-freshness | `53adf727ea052bb6a08b60be8bbec76c8abccc74` | `a5a6c6545471b8872cdae4e12ec9eb558312d1d8` |
| 115: svg-absolute-unit-factors | `fa9dff982cecc234294981fb8f668767816f1652` | `e7ec30d7d15993a80a167e6667200c1263dac10b` |
| 116: svg-hidden-embedding-viewport-readiness | `9c2257a80e3ff6c97080657f5c9a08b717f34cfa` | `01bd90af282902df9f21cf4bd0ddebdef511a824` |

Seventeen signed commits passed exact parent/path/blob checks and configured-key signature verification. Each of fixes 109–116 has one native/WPT commit, preceded by its research. The corrected MathML selection adds 710 paths and retains 341 identical already-committed inputs; fix 116 uses the accepted stack variant after fixes 114 and 115. All working native bodies remain unchanged, including later edits sharing committed files. Main staging is empty; existing nested-library staging is preserved. Signing ran no new browser tests and does not establish clean-upstream independence.

Earlier checkpoints follow; their counts describe their recorded state.

**131 accepted fixes: 109 committed locally and 22 awaiting commits.** One additional numbered repair remains held and excluded.

The canonical Lean library passes its full check with 11,791 audited declarations, 12,401 executable cases, 164 expected-false cases and 2,149 source fingerprints. Contributing-keyframe refresh integration is complete: six previously reviewed declarations were transferred without increasing normative CSS coverage. The model assumes current provider context and a complete contributing prefix; native refinement remains unproved. Both repository indexes and native sources/binaries were preserved. [Integration evidence](../css-keyframe-commit-styles-library-application-v1/REPORT.md).

| Fix | Gecko/WPT commit | Preceding research |
|---|---|---|
| 106: hidden-table-column-provider-query | `29e2df85a4a979f7aab73485b7d77ce4b1ea6bf4` | `9cab8f29f688480dd563092ed19e3f3d157c9d38` |
| 107: hidden-skipped-block-line-query | `e6c73b63765376dbf74daaa0d4f489ea615a2888` | `9cab8f29f688480dd563092ed19e3f3d157c9d38` |
| 108: hidden-grid-skipped-child-query | `a578671e967f9eac837497481d2012b288b98b5b` | `b6871ca3458e882339873f39fa520fdc19f7edc6` |

Five signed commits passed exact parent/path/blob checks and configured-key signature verification. The three native commits contain only their accepted Gecko changes and WPT files; research precedes them. All working native bodies remain unchanged, including later Block/Grid edits. Staging is empty. The original scoped browser evidence remains authoritative; committing ran no new browser tests.

Tested committed prerequisites and scope limits remain in each acceptance record; these commits do not claim a new pristine-upstream run.

Earlier checkpoints follow; their counts describe their recorded state.

Current: **131 accepted fixes: 106 committed and 25 pending; one additional repair held.**

| Fix | Standalone Gecko/WPT commit | Preceding research commit |
|---|---|---|
|132: refresh contributing keyframes before commitStyles |`d477d0c331057847673d3e25646b3f39cd38c1a5`|`ca65cf6d142d4d10a361f2dc3ff7d620a77fd05e`|

The native commit contains exactly EffectCompositor.cpp and two WPT files. Clean-upstream original/candidate/restored comparison repairs12 failures, passes all17 landing cases and retains61 control outcomes; main integration passes146 subtests and two crashes. Signed parent/path/body verification passes, with no working source changes during committing. [Acceptance](../css-keyframe-commit-styles-acceptance-v1/REPORT.md). The earlier prepared research package is committed as `9ad2738c6bdd010d97d607d7e8252dbe619caaa6`.

Earlier checkpoints follow. Their counts and pending/running statements describe those historical checkpoints.

The normal-only keyframe recascade comparison is complete and root-verified: 190 tests improve from 177 PASS/13 FAIL to 187 PASS/3 FAIL, all 22 targeted checks pass, and all 168 controls remain exact. Original sources and generated headers are restored and rebuilt; every baseline outcome returns exactly. All six timing captures complete, but restored controls slow substantially, so performance remains inconclusive and the candidate is unaccepted. A balanced comparison using independent retained browser copies is being prepared. HEAD and staged content are preserved; raw index bytes changed with no established cause. Signing remains blocked by the last 1Password failure.

The dormant-animation candidate passed its 182-case correctness comparison, but local timing now shows an added first-style-flush cost. For 1,000 targets, several literal first-play/replay cases rose from 2–3 ms to about 4.5–6 ms and returned to 2–3 ms after restoration. All six browser runs and both builds passed; root checks verify the original source/build and index are restored. The candidate remains unaccepted. Next: investigate a distinct normal-only recascade request that refreshes every provider without selector rematching, retain the planned 190-case correctness scope, and repeat timings. [Measurements and limits](../css-keyframe-dormant-replay-timing-analysis-v1/REPORT.md).

A follow-up on the restored build reproduces four more stale-value cases: cancelled animations using changed `em` or custom-property inputs return 20 instead of 40 for width/transform; all four fresh-animation controls pass. Root verification and independent review confirm the temporary fixture is removed and source/build/index are preserved. This extends the same dormant-cache investigation, not the accepted bug count. Candidate validation for these eight cases is still pending. [Measured observations](../css-keyframe-dormant-provider-baseline-runtime-v1/SUMMARY.json).

Fix131 is accepted: active animations now refresh attribute-dependent keyframes after attribute changes. The eight-native-file/four-WPT patch passes all46 landing cases and repairs33 failures across162 cases, preserving116 controls and exactly reproducing all baseline outcomes after restoration. Both builds, root verification, terminal review, formatting and exact-body WPT lint pass. Fix130 is a functional prerequisite. Installation and rebuild are complete: all 46 regression checks pass again, and root preservation checks pass. Independent installation review also passes; the signed commit is pending. **130 accepted fixes:105 committed and25 pending; one additional repair held.** [Acceptance and patch](../css-keyframe-attr-effect-publication-acceptance-v1/REPORT.md).

Fix130 is accepted: ordinary keyframe attr() now prepares attribute values and uses the real element provider. Its two-Rust-file/one-WPT patch repairs18 assertions across116 cases, passes all24 landing cases, preserves84 controls, and reproduces every baseline outcome after restoration. Both builds, root preservation, independent terminal review and WPT lint pass. One changed custom-context diagnostic is observational only. Installed and rebuilt: all24 landing cases pass, with root preservation checks and independent installation review complete. Signing remains pending. **129 accepted fixes:105 committed and24 pending; one additional repair held.** [Acceptance and standalone patch](../css-keyframe-ordinary-attr-acceptance-v1/REPORT.md).

Fix129 is accepted: CSS duration changes that reactivate an effect now rebuild its contextual keyframe values. The one-line Rust/six-case WPT patch repairs two failures; all173 strict controls and179 restored non-observational outcomes remain exact across182 cases. Both builds, root preservation, independent terminal review and WPT lint pass. Existing viewport-message variation and unequal raw-index bytes remain explicitly qualified. Installation is complete: the rebuilt browser passes all six landing tests, root preservation checks pass, and the archived result review agrees. Signing is pending. At fix129 acceptance: **128 accepted fixes:105 committed and23 pending; one additional repair held**. [Acceptance and standalone patch](../css-keyframe-css-duration-acceptance-v1/REPORT.md).

Fix128 is accepted: finite mod()/rem() quotient reconstruction loses small remainders. Its one-Rust-file/one-WPT patch repairs16 failures and passes all700 selected assertions. Original-source restoration reproduces the exact baseline; root preservation and independent terminal review pass. The Lean counterexample and replacement contract have independent root replays with explicit native arithmetic assumptions. It is now installed and rebuilt: all 24 landing cases pass, and root verification preserves the source, test and staging state. Independent installation review passes; signing remains pending. [Acceptance and patches](../css-finite-mod-rem-acceptance-v1/REPORT.md), [installation](../css-finite-mod-rem-install-runtime-v2/REPORT.md).

Local branch: `stylo-bloom-verification-2`. No fixes have been pushed or submitted.
Each fix is packaged in one commit containing its Gecko change, regression WPT,
and any necessary test metadata. Research, proofs, tooling, and this index stay
outside those commits. Full commit hashes are the management identifiers.

Historical checkpoint: **105 committed fixes; twenty-four accepted repairs awaited commits and fix120 was held (130 tracked repairs).**

Fix 127 is accepted for the subgrid portion of existing bug 2037744. All ten landing cases pass, repairing eight admission failures; every other outcome is preserved across 1,532 assertions and eight rendering tests. Both builds, exact original-stack restoration and independent terminal review pass. Its patch contains two Rust files and one WPT, with fix 122 retained as an explicit prerequisite. It is now installed and rebuilt: all ten landing tests pass, with root preservation checks and independent installation review complete. It is not yet committed and is not a newly discovered issue. [Acceptance and patch](../css-name-repeat-context-acceptance-v1/REPORT.md).

Fixes 125 and 126 are accepted as separate two-path Gecko/WPT repairs. Runtime NaN propagation fixes eight failures and passes ten landing cases; finite negative-zero preservation fixes four failures and passes eight landing cases. The 1,484-assertion comparison preserves every other outcome and all eight references in both isolated phases and their composition. Original source/build restoration and independent review pass. Both are now installed in the local build:1,420PASS/64unchangedFAIL and8PASS references, with all18 landing cases passing. Final and post-lint preservation checks pass; independent installation review passes. All twenty-two pending repairs are installed; held120 remains excluded. Signing remains unresolved. [Installation](../css-round-runtime-finite-install-runtime-v1/REPORT.md). [NaN acceptance](../css-round-runtime-nan-acceptance-v1/REPORT.md), [negative-zero acceptance](../css-round-finite-negative-zero-acceptance-v1/REPORT.md).

[Grouped team readout with all primary commit IDs](../css-fix-readout-20261023/README.md).

Fixes119/121/122 are installed in the working tree and built browser after local run28306, root verification45302 and independent terminal review. The1,382-case comparison improves1,317PASS/65FAIL to1,337PASS/45FAIL, with all99 mandatory assertions and six reftests passing, no lost passes and no changed retained failures. Seven source changes and four WPTs remain; both temporary controls are removed. Signing remains pending. [Installed build](../css-accepted-119-121-122-install-runtime-v1/REPORT.md).

Fixes123 and124 are accepted as independent five-path Gecko/WPT repairs. Counter-range resolution removes the content-process unwrap crash and preserves all28 range CSSOM cases. Additive weight resolution repairs ten CSSOM failures and its rendering reference, with all32 landing cases passing. Both isolated phases and their composition preserve prior outcomes; root and independent terminal review verify full original-stack restoration. Both are installed and independently verified: all60 new assertions and both new rendering tests pass, with all1,388 prior outcomes unchanged. The combined run completes1,397PASS/45retainedFAIL and8PASS references; all159mandatory assertions pass. Signing remains pending. [Installation](../css-counter-additive-install-runtime-v1/REPORT.md). [Counter range](../css-counter-range-acceptance-v1/REPORT.md), [additive weights](../css-additive-symbols-order-acceptance-v1/REPORT.md).

Release evidence for123: pinned Firefox158.0 build20261007201254 passes literal rendering and calculated CSSOM admission, then crashes its content process on calculated-range rendering. Retained annotations report an `Option::unwrap()` None panic. Root verification and independent terminal review pass, with all source/index/app/test state preserved. This uses WPT preferences and a fresh profile; exact native-site symbolication, stock-profile reproduction and memory-safety impact are unestablished. No new fix is counted. [Release result](../css-counter-range-release-browser-runtime-v2/REPORT.md), [independent review](../css-counter-range-release-terminal-review-v2/REVIEW.md).

Fixes121 and122 are accepted as separate standalone repairs after controlled comparison, successful original-stack rebuild, root preservation checks and independent result review. Integer stored-range resolution repairs eight failures and passes25 landing cases; saturated subgrid counts repair six failures and pass six cases. All prior passes and retained-failure diagnostics survive; all six reftests pass. Both are now installed and independently verified; commits remain pending. [Integer range](../css-integer-resolve-range-acceptance-v1/REPORT.md), [subgrid cache](../css-subgrid-saturated-cache-acceptance-v1/REPORT.md).

Fixes119 and120 passed their scoped three-phase comparison, verified restoration and independent terminal review. Fix120 is now held: root and independent source review predict an admission regression at contextual integer consumers. Do not install or sign120 until prerequisite repairs and browser validation resolve the hold. [Consumer review](../css-integer-consumer-root-review-v1/REPORT.md). Preserving relative-length intermediates repairs six failures and passes its eight-case WPT; deferring contextual `sign()` adds five repairs and passes its eleven-case WPT. All1,018 prior control outcomes are unchanged. **Fix120 requires119**; it is not independently safe on HEAD90. Fix119 is now installed and independently verified;120 remains held and uninstalled. Neither is committed. [Intermediate values](../css-relative-length-intermediate-acceptance-v1/REPORT.md), [contextual Sign](../css-contextual-sign-acceptance-v1/REPORT.md).

Fixes117 and118 are accepted after isolated browser comparisons and root/independent restoration review. Counter-marker handling repairs14 failures and passes all23 landing cases; integer rounding repairs13 failures and passes all37 landing cases. Both preserve all prior passes and exact retained failure diagnostics across213 subtests and two reftests. Each has a separate minimal Gecko/WPT patch; working-stack installation passes build/lint, all60 landing cases and the314-subtest/two-reftest integration. Root preservation verification and installation result review pass; signing remains pending. [Counter acceptance](../css-counter-calc-sentinel-acceptance-v1/REPORT.md), [integer acceptance](../css-integer-math-rounding-acceptance-v1/REPORT.md).

Fix116 is accepted: hidden embedding layout is refreshed before viewport-relative SVGLength reads/conversions. The normalized standalone comparison improves32PASS20FAIL to52PASS, preserving28controls; restoration and independent review pass. Its six-path Gecko/WPT patch is packaged separately from research. Working-stack installation passes101cases across12files plus build/lint. Root verifies all source/index/binary roles and nine installed-test identities; no commit exists yet. [Acceptance and patches](../css-svg-hidden-embedder-acceptance-v1/REPORT.md).

Fix115 is accepted: three incorrect Q-related SVG constants produced wrong conversion values and animated positions. Its isolated comparison improves26 PASS/8 FAIL to34 PASS, preserving18 existing controls; original-stack restoration and independent review pass. Four finite Lean results independently corroborate all49 corrected factors against exact CSS ratios within the stated engineering tolerance. The native patch contains one Gecko file and two WPT files (16 cases). Working-stack installation passes build/lint and all16 integration cases, preserving the prior changes and test files. Signing is pending. [Acceptance and patch](../css-svg-absolute-factor-acceptance-v1/REPORT.md). [Separate research and native commit recipes](../css-svg-absolute-factor-commit-queue-v3/README.md) are finalized.

Expanded fix114 is accepted: two Gecko files and three WPT files with25 cases. The isolated comparison improves35 PASS/16 FAIL to51 PASS and preserves all26 controls. Full restoration and independent comparison review pass. Combined-stack installation passes all25 cases, build and lint; independent installation review passes. This expands114 without adding a new fix number. [Acceptance](../css-svg-length-conversion-acceptance-v3/REPORT.md). [Research and native commit recipes](../css-svg-length-conversion-commit-queue-v3/README.md) are finalized; signing parents remain unset.

Fix113 is accepted: hidden SVG viewport matrix queries use the existing hidden-content-aware layout path. Its exact two-path Gecko/WPT patch gives34/34 passes on normalizedHEAD90, preserving26 controls and8 availability observations; pending107 is absent. Full restoration and independent review pass. Working-tree installation passes build/lint and all eight integration cases. [Separate research and native commit recipes](../css-hidden-svg-matrix-commit-queue-v1/README.md) are finalized; signing remains pending. [Acceptance and patch](../css-hidden-svg-matrix-acceptance-v1/REPORT.md), [installation](../css-hidden-svg-matrix-install-runtime-v1/REPORT.md).

Expanded fix 112 is accepted: Element.cpp/Element.h conversion repairs plus two WPT files fix ten offset/scroll/client precision failures. All 40 regression checks pass and all 130 controls are preserved; restoration is independently verified. Expanded working-tree installation passes its build, lint and all40 integration checks; signing remains pending. [Exact four-path patch and acceptance](../css-cssom-integer-geometry-acceptance-v1/REPORT.md).

Three hidden-query repairs are accepted for separate native/WPT commits: column-provider query admission (7 landing cases), skipped-block-line marking (14), and skipped-Grid-child marking (8). Each passes independently; together all 79 final cases pass, including 50 existing controls. The five builds and restoration pass, with no new failures. Native commits are pending the existing 1Password signing flow. The final installed-tree build also passes all 79 cases with the older prototypes preserved. [Acceptance](../css-hidden-query-landing-acceptance-v1/REPORT.md), [independent review](../css-hidden-query-landing-review-v1/REPORT.md).

Float repair109 is now accepted: its unchanged eight-case regression WPT improves from4 PASS/4 FAIL to8 PASS with only the float patch, and the composed95-case run preserves all79 prior controls. The paired benchmark removes480 stale geometry reads. The landing patch contains only nsBlockFrame.cpp and that WPT; calibration/proofs/tooling stay in preceding research. [Acceptance](../css-hidden-float-acceptance-v1/REPORT.md), [two-path patch](../css-hidden-float-acceptance-v1/gecko-wpt.patch). Signing is pending. Float109 and MathML110 are installed and pass all91 combined landing subtests; [working build](../css-hidden-query-consolidation-runtime-v1/REPORT.md).

MathML repair110 is accepted: the isolated four-case WPT improves from2 PASS/2 FAIL to4 PASS, and integration passes299 subtests across18 files. Restoration and independent review pass. Its standalone patch has one native line plus the four-case WPT; formal and diagnostic evidence precedes the fix. [Acceptance](../css-hidden-mathml-acceptance-v1/REPORT.md), [two-path patch](../css-hidden-mathml-acceptance-v1/gecko-wpt.patch). Signing is pending; the candidate is installed in the verified combined working build.

Fix 111 is accepted: central baseline synthesis now uses the correct origin in vertical writing modes. Its twelve-case WPT improves from 8 passes/4 failures to 12 passes; all existing comparison outcomes are preserved. Conditional Lean proofs and source correspondence passed independent review. The two-path patch is installed; all103 combined subtests across12 files pass, including the prior91 cases. Signing remains pending. [Acceptance and patch](../css-central-baseline-acceptance-v1/REPORT.md).

## Latest signed fixes: 104–105

| Fix | Repair | Native + WPT commit | Preceding evidence |
| --- | --- | --- | --- |
| 104 | Dirty skipped hidden flex children | `29611cb584fdd0e54d5e7f7e0d70ad47cfff1653` | `2c27b25853ff18acc4e0423410e932742829bfaf` |
| 105 | Dirty hidden absolute subtrees before child reflow | `f8104759d383bd324cdda1e78e3229902e97fb39` | `2c27b25853ff18acc4e0423410e932742829bfaf` |

Each commit contains only its native change and its own WPT files: four files/38 cases for 104, three files/12 cases for 105. Each passes its isolated landing partition. Both pass all 50 landing tests; the fresh 66-case comparison has 25 improvements, no regressions and 11 unchanged column/ordinary-block failures.

Controlled timing completes 13,440 rectangle observations per variant. Both fixes produce no incorrect rectangles, versus 3,213 hidden absolute errors before. At 256 branches, first-query batch medians rise from 1 ms to 8 ms (principal) and 7 ms (absolute); repeated and visible controls show no blocker in this limited sample. Formal models remain conditional. These are geometry-correctness fixes; no security impact is established.

[Acceptance and limits](../css-hidden-layout-landing-decision-v1/REPORT.md). [Exact commit checks](../css-hidden-layout-column-commits-v1/COMMIT-CHECK.json).

## Landing prerequisite: fix 101

Fix 101 (`6cf27eadddf9e63d9bfbcc87ff2bf354e091ae7c`) requires **fix 104 above, or an equivalent repair, to land first**. Its known hidden-layout exposure is repaired in the combined branch. Cherry-picking fix 101 alone onto a base without that remedy remains unsafe for the observed geometry cases. Preserve its required containing-block cache key. Fix 104 is independently useful with the original key; fix 105 is a separate defect and is not shown necessary for fix 101's cache exposure.

## Earlier signed fix: 103

| Fix | Repair | Native + WPT commit | Preceding companion |
| --- | --- | --- | --- |
| 103 | Untransformed client rectangle app-unit precision | `7309af28e360d5d9544eb04dbbbe7f74a102e164` | `5c3fe8efdb1dd46a5f4dbccfdb7099bc0a9d523f` |

The commit contains four native files and its WPT. Six preceding research commits
retain source review, proofs, browser results, independent checks and acceptance.
All four own WPT cases pass without fix 102; other keyed outcomes match the
historical oracle. The possible deep root-transform cost remains disclosed
(about 10 ns/call in this local sample). The source patch is now installed;
the local binary has since been rebuilt with it. Signing adds no new test results.
[Acceptance](../css-cssom-exact-traversal-acceptance-v4/REPORT.md),
[commit verification](../css-signing-resume-20261020-v3/ROOT-COMMIT-CHECK.json).

All seven queued commits are signed; the index is empty and all 20 other modified
native files retain their exact bytes. Nothing was pushed or submitted.

## Previous signed fix: 102

| Fix | Repair | Native + WPT commit | Preceding companion |
| --- | --- | --- | --- |
| 102 | DOMRect layout coordinate double precision | `c0e8c7fd1deb9320b0bae747c043c100ac842f49` | `752c83eb28346d73a28d48748a8cb52adf4057dc` |

Four standalone WPT cases pass with this repair alone; two failed before.
Existing selected regressions retain their outcomes, including two expected
failures. The native commit contains only DOMRect.cpp and its WPT; evidence,
source review, bounded Lean proof and runtime trials precede it.
[Acceptance](../css-domrect-edge-precision-commit-v1/ACCEPTANCE.json).

## Previous signed fixes: 88–101

| Fix | Repair | Native + WPT commit | Preceding companion |
| --- | --- | --- | --- |
| 88 | view-transition-type-style-invalidation | `c67505af9aae8c06150d74d81a67011e7921d3cd` | `85ed2f301cf00df468f6d071c1322c9767e64bba` |
| 89 | sticky-explicit-inset-auto-alias | `fdd7dcb11653c3c3808557708969c7e1eb803b82` | `de1fa6e8539a1d7d08514cfde240f0f572a16046` |
| 90 | sticky-auto-inset-normalization | `983931aa5fad14b5d86120cfd66635be7f1b844f` | `402fc4d824b0a8064b1e124fb0d2de413bf64fac` |
| 91 | sticky-containing-block-writing-mode | `67bcf64fc28f181859c6dc726e532430475e49e7` | `05b8cda1a77cb28ce532c3bf3e40483b6dd8d212` |
| 92 | sticky-negative-inset-overflow | `d3c505adc9e99a293a44bde5a3f04557aac255d0` | `b0d56f61ff11561282f0bdf5500959ae1a79fdb9` |
| 93 | flex-baseline-cross-size-sum | `71a523a4c5267ba4c07a59329e57317fafc31f1b` | `edd86929946a555f4c8527577ee10d582efdf716` |
| 94 | sticky-finite-sentinel | `68686da757592b0de4d1b064966d81f8b9265fc1` | `8ce52f459152c455bfdde8ee74fc39d447e62cf8` |
| 95 | flex-line-cross-size-sum | `958e63a947e4a97dd224d60c5699b42061af5422` | `5c3d2e1ec59a4cdb940f40a837daf108189adef2` |
| 96 | flex-relative-item-exported-baseline | `b4894d6329df7b9cae8f81cbd72e89d61f1b4adc` | `2ba42b38c6557fcbda3ae8bcefdcdc1835c86c09` |
| 97 | scroll-container-natural-baseline-border-conversion | `9980b7b7a0fb894c963a69c0ef0e17b12e6d6350` | `2dc0fa3aa371a02d67ce129c3c394c1c82b81b03` |
| 98 | flex-baseline-percentage-padding-measurement-cache | `f5926c6dab500569fc2345aade1a43aebc7e3796` | `55ca79bc149d5ffc2773e3e0b0216bfe3dc8dbf8` |
| 99 | flex-vertical-rl-overflow-container-position | `a6c78d9502504d07432fd0c81c168847bbfa25a4` | `052dc13ae43ddb8a86edda92f70abba7ba9fdbe7` |
| 100 | overflow-continuation-relative-position | `2b769488eef1e2ae18ed27d014402591110e3ed1` | `dcdf5a89d3589bd31ad115988fd8af898b2c753b` |
| 101 | flex-table-auto-caption-percentage-height-cache | `6cf27eadddf9e63d9bfbcc87ff2bf354e091ae7c` | `4d0749e7d3c43516d8d265901d7c6a918c99f7fa` |

All 48 queue commits contain signatures. Each of the 14 native commits matches its
accepted patch against its actual parent and includes its WPT; research and proofs
are in preceding commits. No new build or test results are claimed by signing.
[Commit verification](../css-signing-resume-20261020-v1/ROOT-COMMIT-CHECK.json).

The sections below retain earlier research checkpoints. Their pending-signing
statements are historical; use the current count and table above.

## Historical flex verification checkpoint

- **Scroll-container baseline provider repair accepted:** ordinary asymmetric
  borders expose a preexisting last-baseline coordinate error in release Firefox.
  The standalone two-file patch repairs 72 failures in 384 WPT cases;
  312 controls and all 38 focused regression files pass. Root accepts the
  conditional full-method companion after 48 fresh audits, 1,536 candidate
  cases, twelve independent reviewer audits and five root projection joins.
  Child baseline truth, geometry and lifecycle remain provider premises.
  [Acceptance](../css-scroll-baseline-provider-proof-root-v2/ACCEPTANCE.json).
- **Natural donor acceptance withdrawn:** a new calibrated 64-case probe
  finds six asymmetric scroll-border last-baseline failures in the candidate;
  installed release passes all 64. The conditional proof remains valid, but
  its native-provider premise is not established for these ordinary cases.
  The accepted provider repair removes those six failures, but the donor patch
  still depends on it semantically. Resolve independent landability before
  restoring donor acceptance; source commutation is insufficient.
  [Probe](../css-flex-scroll-baseline-border-probe-v1/probe.html).
- **Relative-position baseline repair accepted:** the separate two-file patch
  repairs 192 failures in 288 WPT cases and preserves 96 controls. Fresh root
  replay passes 29 kernel audits and 1,080 source/model cases per variant;
  eight independent checks and three rejected false claims pass. Property
  lifetime and full downstream/provider histories remain open. Its evidence,
  review and formal companions precede the native/WPT commit in the queue.
  [Acceptance](../css-flex-relative-baseline-proof-root-v1/ACCEPTANCE.json).
- **Packing v1 rejected:** the reviewer’s fragment-cancellation witness
  reproduces in the browser. Two large, calibrated multicolumn cases pass
  in release and fail in the candidate; two smaller controls pass in both.
  The earlier 432-case WPT and unfragmented controls remain useful evidence,
  but narrowing before consumed-fragment subtraction changes valid placement.
  V2 must preserve wide coordinates through fragment adjustments, line metrics
  and cumulative-size storage. The shared build still contains rejected v1.
  [Counterexample](../css-flex-packing-fragment-probe-v1/REPORT.md).
- Counts: **87 committed fixes and ten accepted repairs awaiting signing**.
  Latest user-requested signing retry failed; HEAD and the verified 297-file
  staged snapshot are unchanged. No pushes or external submissions.

[Relative triage priority](../css-bugfix-triage-20261019/README.md) groups the first 80
native commits by demonstrated crashes, security-boundary review,
broader correctness and narrower triggers. It records exposure limitations and
standalone alternatives; the rankings are recommendations, not assigned severity.
The [addendum for fixes 81–87](../css-bugfix-triage-20261019-addendum-v1/README.md)
brings that review order up to the current committed count.

Latest committed fixes:

| Fix | Native + WPT | Evidence companion |
| --- | --- | --- |
| 83: leading-whitespace attribute crash | `ad608a212bd8d7f77a2f0b9df62df18d33c12b96` | `1d4940ff2211b3a7256999f8090e0f0d61cb8733` |
| 84: trailing-whitespace token boundaries | `bccea9c1fffc59e41a9f9bef16fcaf0056ff1f10` | `35c04a32169744c3c75e2dfef9b8d18b673d8b06` |
| 85: escaped trailing whitespace | `fff2d758ef6bb39b4465cb072767bc5db6d5e09f` | `3029d557014c83c6ad6260253243700536499176` |
| 86: backslash/newline preservation | `246f1ff43250ec24e177f03cde923c9d11ee86e9` | `45721455b1e409b438520a9a4f0ec5f097a523d5` |

Each native commit contains only the Rust fix and its WPT. Independently applicable
upstream alternatives are now signed local commits with separate evidence parents:

| Fix | Standalone native + WPT | Local branch |
| --- | --- | --- |
| 83 | `4be5b070191054a263197654d1f30096a9306b43` | `stylo-css-attr-leading-whitespace-fix` |
| 84 | `5b4fe54b37bc5a3bb848ceb8300f5d92ea4c2e3a` | `stylo-css-variable-trailing-token-fix` |
| 85 | `8a528dbb92bbaca6db31123f8b0da45983fa798a` | `stylo-css-variable-escaped-whitespace-fix` |
| 86 | `95b6a9b03c1c7726fd8061ae3ef48e8c52448209` | `stylo-css-variable-backslash-newline-fix` |

Use these alternatives when extracting a fix independently of the integration stack.
No isolated upstream build/runtime is claimed.
[Stack verification](../css-signing-resume-20261019-v3/ROOT-COMMIT-CHECK.json) and
[standalone verification](../css-variable-whitespace-standalone-root-v1/ROOT-COMMIT-CHECK.json).
The registered-animation calibration remains a separate test-only commit,
`5cdd697e02d209bff0368711764523f5d26dba30`, excluded from the native-fix count.

### Backslash/newline repair committed

Trimming the newline after a backslash delimiter changes an invalid animation
name into an identifier. All 30 final WPT cases pass; the corresponding baseline
subset has 16 failures and 14 passes. The earlier combined matrix preserves all
435 prior outcomes. Root and independent formal review accept 53 conditional
audits and 15 independent kernel challenges. Native metadata correspondence
remains a source-review admission; the native traces directly observe stored bytes.
[Runtime evidence](../css-variable-backslash-newline-root-v1/FINAL-WPT.json),
[formal acceptance](../css-variable-backslash-newline-proof-root-v1/ACCEPTANCE.json),
and [standalone commit receipt](../css-variable-backslash-newline-root-v1/STANDALONE-86.json).
No release or isolated upstream browser result is claimed.

### Fix 87: initial view-transition types have set semantics

Native + WPT: `2db94380203863bced9e3a7147505beabaaf7599`; preceding evidence:
`baa7f955bacd6e7bc5b4faf752cb9a1616be1d3a`. The native commit contains only
`Document.cpp` and the 21-case duplicate-initialization WPT. Deleting a duplicate
initial type previously left native selector membership behind after public set
membership disappeared. Five baseline failures become passes; all 21 candidate
cases and three existing mutable-type cases pass.

Root and independent proof replays pass 90 audited declarations and 1,755
extracted-native/model/oracle cases, with 12 additional independent challenges.
The conditional result covers initial uniqueness and successful mutations/direct
matching. Native providers, lifecycle installation, failure/OOM/GC and cached
style invalidation remain outside the proved contract. The exact two-file patch
applies independently to the retained upstream base; no isolated build is claimed.
[Acceptance](../css-view-transition-types-root-v1/ACCEPTANCE.json) and
[commit verification](../css-view-transition-types-commit-v1/ROOT-COMMIT-CHECK.json).

### Pending commit: view-transition type invalidation

The separate four-file Gecko/WPT repair fixes six stale-style failures, including
ordinary and generated pseudo-elements. All 42 matrix cases pass. Native and
formal reviews pass, including the corrected closed-input independent review v2.
The latest signed-commit retry still failed in 1Password; no native commit is
counted yet. [Acceptance](../css-view-transition-type-invalidation-proof-root-v1/ACCEPTANCE.json).

The geometric sticky, explicit-inset encoding, and collapsed-flex baseline
candidates remain outside the accepted count while their required review gates
are open. The baseline candidate now passes 60 paired WPT cases against 22 failures;
see [its report](../css-flex-collapsed-baseline-fix-v1/REPORT.md).
A separate [negative-inset overflow lead](../css-sticky-negative-inset-overflow-probe-v1/REPORT.md) now reproduces in release and the local build; its candidate remains outside the count.

<!-- CURRENT-SIGNED-QUEUE -->
## Signed commit queue

Full hashes below are the current management identifiers. Earlier evidence records retain their historical hashes and signing status. Each native fix includes its WPT; proof/tooling commits precede it. See the [machine-readable ledger](CURRENT-COMMITS.json) and [original queue check](../css-signing-resume-20261019/ROOT-COMMIT-CHECK.json) and [Ahom commit check](../css-ahom-lf-partition-probe-v1/ROOT-COMMIT-CHECK-v1.json).

| Repair | Native + WPT commit | Proof/tooling commit |
| --- | --- | --- |
| attr-leading-whitespace-origin | `ad608a212bd8d7f77a2f0b9df62df18d33c12b96` | `1d4940ff2211b3a7256999f8090e0f0d61cb8733` |
| variable-trailing-whitespace-token-boundary | `bccea9c1fffc59e41a9f9bef16fcaf0056ff1f10` | `35c04a32169744c3c75e2dfef9b8d18b673d8b06` |
| variable-escaped-trailing-whitespace | `fff2d758ef6bb39b4465cb072767bc5db6d5e09f` | `3029d557014c83c6ad6260253243700536499176` |
| color-missing | `82b254686378e57711759c238b975cdf4678a287` | `a75f70c97b155b46b3820be79fe4b41e272f7b8d` |
| color-zero-prefix | `591b3e12567865c7e047530753e510c54d18b3db` | `519f2b2a756969dbba9c45415d2b40506560d94d` |
| transform-deferred | `c9274972124198e8f8466ddcd667d1c23cb044ec` | `4c401192c6ae79b5a6c3b4328f939d70e2474be2` |
| clamp-nan | `a4fe7dd06fd7dac3924b2dc9aea4f57103eb1b98` | `7b2f125756a218c548cdd95d2693e5a022bbb61b` |
| mod-rem-infinity | `bfbce1cc7e9a5b53d5cc00317a265d7141428997` | `033c4ac60d396dd9dde7ce085b76edae15353696` |
| attr-numeric | `499c0c6b72ac4bc0a6396bffa3fa0d71665409ce` | `607a4fcfbab31bf37f2495b38c9841be83cbfc66` |
| logical-shorthand | `e27beeac5129d7331f8aca9babbe6bfc199d7d24` | `f5b175e01f2182d26ee2e137ca2072f60d185d4c` |
| grid-abspos | `7f5a1105253e60b283174ea890862b1943e8702a` | `739139c30e536e6ac655a4597bca14f3d97f8e06` |
| sigma | `8e78ffd376c4d478b5d614f568f3bf09d894ad8b` | `5dc0849a15e83215ae89fb809752014a3ba241f1` |
| sizing-stretch | `2a61f0b7433628e8a77159b968ca570632591b8e` | `4a696e8c980f4f5432cc31653fed0a327308c5cd` |
| query-attribute-wrappers | `16ff45a117b149ec95fc633c7ac18d8a1c38ca0b` | `3dc4259d2dd035c248512062d84eafd8bc1dc15b` |
| query-content-box | `ef3d32280505b7fb6c1b35989d7e74c56f1aee0a` | `dc96c3763a4d175db6539c57cf5ece7fcd4614eb` |
| table-span-spacing | `98fd7a22a32744ab429828d609cf5bfb3affc4a5` | `799efd5a456feaafaa905f91b6e7ef1c3a8aa0ee` |
| polygon-intercept | `06be3d7e722c55ffbff97e6be237bd39a4920295` | `1a86773b4a5ec6f53f5f0a0b7a6e35da06cf8a38` |
| stroke-reference-box | `96e0ad8c6a0ae58b9ce8c47579c9bc06f67fc1e2` | `b709247b5f33999576d743e0183d2d7867f18b7b` |
| object-fit-partial | `66fb24648a15769f80c2adf37030e68598dae68f` | `ff354bf3100dbe2cea2b83ab87dbee11793fbbe3` |
| abspos-auto-margin | `f67ddfaa3dc328d7359c7fca56e61a1249e1ee96` | `1c9e80b2228a27ed596e6865f510c9ab994f713b` |
| block-flow-collapse | `e09ffb35c0b47c6c29c43c64d887fb524b5e7423` | `8621e83c91428e627c710fcac796b2de8efae7a0` |
| bad-url-recovery | `83bc2bd3922697d44a602bf48902e821796a60e3` | `366b0542b5595614895a17e5e334019f0fcf5d20` |
| svg-empty-mask | `065183ac8449800f0dbef3c23a15be3863ca60ae` | `629771d9fd8c5b18782647a5b4d21e8e978d15b0` |
| image-zero-mask | `6bb2557507bcd6346664e539f9f4b9628d8e6078` | `c767ea97fb253ae03b852b095beca0b14f452948` |
| nesting-specificity | `c57d0c806d94c6e6dd56e23acdeed847c5ea1571` | `ab6513e805c725c11d3e61ffb82583123f209ee3` |
| scroll-fixed-anchor | `e606244c4546e522cf4a6e86dac98e216305003b` | `e0494649157d12b7d42b6e3f750ddcc81e2474fe` |
| text-overflow-line-state | `c348436003653a08b6766339d9e0c8f89084d062` | `e32b6ba35b6e09ea87f685ebbc09639669bc55a5` |
| tab-zero-intrinsic | `eca9efde2991b5a458d23efd1c6d33d58fdf4a77` | `ba9ebc9d81b7e8ac2fa25ac58425ee0f76c151f5` |
| font-threshold | `9da730d5ebd6cb59a0a5b2a666d6679808d58889` | `153b0e8d9bf36a49b3575629371cf5c0a0d81db6` |
| timeline-pseudo-axis | `0af700c67a5aef6048b19b72350320cd1fe82346` | `5388c30dc8ec99a5b0016580aaa59ce6849142bc` |
| font-priority | `9cca10125782ebe2bf076a5e5d8becdacae5ff16` | `0cafb33759540c5f6b794312351b3315b1590235` |
| root-rlh-zoom | `43afd2c6f3500cee4a2dd07d07eb14aca723fae3` | `635b8995326d0c8ca526bc9aea8d8cc7d295d2c7` |
| animation-composite | `6b8dc654e8d017562533308571af23c3099fd5cc` | `7ee385b8404b0e332950ae4e4edaf4a1bb3e20a2` |
| text-emphasis-pua | `bbf5a4095f85fb250ea442695a311f2547ffdc19` | `75401fe2983110104c3f0a3bef1686d807701033` |
| negative-ligature | `8ee543a6ff23cc097f54f1c3e984f7d5f7e56fea` | `3f61a60e15b32e88afdf5975fd65b49fd760d568` |
| complex-utf16-ahom | `39ce7571a61097a80d5bf07adbc3ae48a2f0262e` | `28d9e8cc1065d7b00e3d891b42049c82d5e7058c` |
| worker-font-removal | `32ba35ffb9a17f5e91df5c56f01a06a452dfdc8a` | `07dc1d27343268a8add266605c33fc5f966ef155` |
| hyphenation-coordinate | `18871240dc7d077bf223822013e7a50cf581e2d1` | `a1eed2e249aed69af41142c5a55e49a5d88fbb2e` |
| attr-namespace-cache | `3aa7d25635ff9dc3bc105269dd9b7b13b5f80cb0` | `adde61d9742f3f9939514bdfe10fde08a794aeff` |
| attr-invalid-entry | `fd9c07e1130bcb68684c25e7527f5b0ff3c3bd73` | `76bda27b8dfdb88ebdcb7e4706508688d0a3f064` |
| attr-fallback-preparation | `7822bb6d17b1381cdb3e56deb20c5ec3e078adec` | `31265260cc3daa2bbea93c237a9491b6f2afcaa4` |
| mathml-token-range-origin | `f843fd7568f30e14e664c37c36544d8d88e8c1bb` | `6eb5a90e3fa3b6128ddd6397d9dae9f1ab34b88d` |
| attr-typed-fallback-eligibility | `e3ba54f6f826fe265eb5bc4731f66f64465dd47c` | `30c8dfeb4b746104b53ad5bc6440c1d53734f570` |
| attr-noncustom-dependency-collection | `3892ab844694fedd987f5ce1dd2165f53fc2dbed` | `0db19774e6f2bf6692790459f8e6e54ca426e366` |
| resolved-unit-dependency-summary | `58200fa81a6f92f92a1898ba2866a2fbcbac0daa` | `03bad7f708329254a9af2073f0b4106ba557e914` |
| unit-token-classification | `26e0fa16e89eacd9fd9cab0ce6bb1be813d9e406` | `2e1f5f62c8a6325679a83adc7f637e104c488bf7` |
| identifier-start-escaped-newline | `09b008b3320fa29fcbcf081b252053e3721c5e10` | `b69763a1817a7a4824e6df0d04e0e4e52684c897` |
| loaded-fontface-descriptors | `6bd0b00dcff5514a3234423787920ed44491a4bc` | `ae298df56390ff98baa873bfcea3896e6c112d48` |
| numeric-compensated-exponent | `4391deb4751a8be2be98e838360f00c94808c5d5` | `ddb1799ad54ecdd4528ee894b09c44e80bd6816b` |
| quoted-eof-fallback-endpoints | `2d658a9c5aa4139dc7f196933511abf4a594163f` | `5faa99644ddc4b49594651a34721119484ec88ef` |
| quoted-eof-backslash-parity | `89bad2d8b5260ad5fc9d5660a3a18a09433902e3` | `5e0f8696a8de0b931b2aa679457683e3f881ecb8` |
| quoted-eof-escaped-terminal-quote | `ed9505d25ee4333c1764acc173f95f9517ca9b07` | `1b9022a98dc38e54dc9415d5eab6a51980003d13` |
| parser-depth-limit-declaration-recovery | `55d251b7a90003546994f6576e5ee78e8fa07cb2` | `19ca0c3c68c2fb7320290be7562c02dedf02d7da` |
| declaration-fallback-top-level-curly | `095c5be548a2bddf5f3ff01e01da66c6098a8ee5` | `320a3d100d7669c4508ab89570b9833390baed2d` |
| declaration-substitution-publication | `780495d90a85052cff69713f1086180253cb9730` | `53e30d418ef77e3b9626aa3c1cd99e7fb9a87cbf` |
| all-shorthand-logical-order | `074086719e445ca72d3056f7fbf793af5e69d6f6` | `bad8f7998dbbb3ad1fa88c0ca6892488f912e898` |
| registered-keyframe-substitution | `188644f6d9833b485f35c2abcfad23cef2c5e9f7` | `1cf91c4def90e6e7cce4e76106020ffcd4b45692` |
| registered-initial-computed-value | `6aa2138c144aa6eee8e07aac77e7a68a8c7f7617` | `3d194d59545c331fabc7ad1502af96522aa67c90` |
| registered-inherit-invalid | `3a01fc986c7974161aadf4bfafe65c234b036b07` | `2e0f9f6b9ee5450cd21ac9341ef116dd91a8119b` |
| registered-substituted-inherit-restyle | `60bf34f48ac63ca595d519c1e0c2b4a2fa731b66` | `1ad6ea9740aa7f73ca299625208edf9856be807a` |
| custom-property-live-count | `0cac5c270615d04239bd4a4024a3ab5ffd0d24ae` | `d9d1047dd4b1592794229f3f7f7610ddedfd9aba` |
| custom-property-enumeration-shadowing | `90ffac0a5e4076b6117ca152249f342a13995ee3` | `215c881ef243f0268be11836d6c2a45e91b29b6f` |
| custom-property-equal-payload-taint | `e04d672a735edcf0e6529c854207b5ee9555ea7c` | `01c98e4fd49ed6061c1a7ebdd87c124cd2b77254` |
| attr-taint-half-open-ranges | `8c04b6787e36c9ee42fec440103cf33372c097f1` | `91e709f931abf5ef2d59a77158f66662500bd2ff` |
| animation-retained-endpoint-taint | `4b4a00e707583382f4773039f13a4f335f48f41a` | `922272780824ee77c05f96972c7bb51a95de7ead` |
| animation-underlying-base-taint | `2c09cb2e4ff81bbc4af65d1d069517420b9c1529` | `91d47c020cb9c4855e0e35ad51012d2ccf2aeac9` |
| animation-interpolation-taint | `ede7ceb101d83f0c4044585a5a687f5286b072c9` | `a9b8e799ce9785008c72d63b6539305284cbf9ef` |
| registered-token-boundaries | `34e4e755cb81332819e56457f5fb68b9b305c394` | `76d4707974532db89589ffa39f2728db46527114` |
| animation-invalid-publication | `d63735091bf8dc469d900ddba56e8a43bcac26d7` | `5e540197f9afb45e30d0f5714ffbf716115da302` |

<!-- END-CURRENT-SIGNED-QUEUE -->

## Quoted EOF endpoint repair

`2d658a9c5aa4139dc7f196933511abf4a594163f` contains only the Rust endpoint correction and its WPT,
following proof/evidence companion `5faa99644ddc4b49594651a34721119484ec88ef`.
The baseline content crash becomes 38 passes; all 34 other outcomes are unchanged.
The patch applies and reverses on the upstream base. Browser testing used the
shared local tree. The proof covers conditional endpoint arithmetic; it does
not close the full parser/provider model. Parity and escaped-quote value defects
are repaired in separate commits below. See
[acceptance](../css-quoted-eof-offset-root-v1/ROOT-SCOPED-ACCEPTANCE.json) and
[commit check](../css-quoted-eof-offset-root-v1/ROOT-COMMIT-CHECK.json).

## Quoted EOF backslash parity repair

Stack commit: `89bad2d8b5260ad5fc9d5660a3a18a09433902e3`; companion: `5e0f8696a8de0b931b2aa679457683e3f881ecb8`.
For independent landing without the endpoint repair, use
`d4a792717bddfb6f757327b5ac23af3e3e96555f` on `stylo-css-quoted-eof-parity-fix`,
following companion `62e25919335875d7db961f1d30c55bf74ab240a1`.
Both contain only the applicable Rust predicate change and the same WPT.
Four failures become 18 passes; 50 other outcomes remain unchanged. The standalone
patch applies/reverses at upstream base but was not separately browser-built.
Conditional terminal-run proofs preserve explicit tokenizer/native assumptions.
See [acceptance](../css-quoted-eof-parity-root-v1/ROOT-SCOPED-ACCEPTANCE.json)
and [commit check](../css-quoted-eof-parity-root-v1/ROOT-COMMIT-CHECK.json).

## Quoted EOF escaped terminal quote repair

Stack commit: `ed9505d25ee4333c1764acc173f95f9517ca9b07`; companion: `1b9022a98dc38e54dc9415d5eab6a51980003d13`.
For independent landing, use `2933b8c870641670e4c33950665a482cc11d47a0` on
`stylo-css-quoted-eof-closure-fix`, following companion
`811cadc617155a2260daf14c883e7a0b28bd78b6`. Each native commit contains only the
Rust closure predicate change and its WPT. Four failures become 18 passes;
the combined string diagnostic passes all 22 checks and 69 other outcomes are
unchanged. The final run has no unexpected results. The standalone patch
applies/reverses at upstream base but was not separately browser-built.
The proof covers conditional terminal-quote classification and recovery,
with tokenizer/native assumptions retained. Discovery was source inspection
followed by browser reproduction, before the Lean companion.
See [acceptance](../css-quoted-eof-closure-root-v1/ROOT-SCOPED-ACCEPTANCE.json)
and [commit check](../css-quoted-eof-closure-root-v1/ROOT-COMMIT-CHECK.json).

## Parser nesting-limit recovery repair

Stack commit: `55d251b7a90003546994f6576e5ee78e8fa07cb2`; companion: `19ca0c3c68c2fb7320290be7562c02dedf02d7da`.
For independent landing, use `c653dfe4227ca193c18ff6ae8d6e8ccc06f88947` on
`stylo-css-parser-depth-recovery-fix`, following companion
`45e55b2280eb99fde35165cfd0c702d5fc9dca0b`. Each fix contains only the one-line
parser cleanup, its required vendor checksum and the 22-case WPT.
One failure becomes a pass; all 22 new checks pass and 46 other outcomes remain
unchanged. The nesting limit stays unchanged. Root and independent review pass
the 21-theorem token-level recovery component; byte/native/caller admissions
remain open. The standalone patch applies/reverses at upstream base but was not
separately browser-built. Discovery was source inspection followed by browser
reproduction; the formal companion followed discovery. No novelty claim.
See [acceptance](../css-parser-depth-recovery-root-v1/ROOT-SCOPED-ACCEPTANCE.json)
and [commit check](../css-parser-depth-recovery-root-v1/ROOT-COMMIT-CHECK.json).

## Test-only corrections

These commits improve existing tests and are excluded from the native-fix count.

Pending signing: the registered animation-consumer test now spells
`initial-value` correctly and checks the registered initial value and animated
producer before retaining its original consumer assertion. The typo fails the
new calibration; the correction passes, with all 18 other status/message pairs
unchanged. WPT lint passes. This is a separate test-only repair, not native fix 82.
Evidence: [calibration acceptance](../css-animation-registered-consumer-runtime-v1/ACCEPTANCE.json).

| Correction | WPT + metadata commit | Evidence/tooling commit |
| --- | --- | --- |
| Await imported stylesheet completion before identifier round-trip comparison | `ae4db18e4b3ec93bd9bd16bfa77236c484e2695d` | `8d1658d8e6743a853126093b0888a00cc2ffc7ba` |

The original equality assertion now passes. The correction uses a fresh style
element and its completion event; no native serializer change is included.


## Hyphenation coordinates committed

`18871240dc7d077bf223822013e7a50cf581e2d1` contains one native comparison and its WPT,
following companion `a1eed2e249aed69af41142c5a55e49a5d88fbb2e`. Two browser failures
become passes; all eight new checks pass and 20 existing results are unchanged.
Root's relocated native/model replay preserves 40,608 controls in both provider
variants and passes the 31-module guard proof. The full ownership and persistent
spacing-cache obligations remain open. See
[acceptance](../css-hyphenation-measurement-offset-probe-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)
and [commit check](../css-hyphenation-measurement-offset-probe-v1/ROOT-COMMIT-CHECK-v1.json).

## Worker font removal committed

`32ba35ffb9a17f5e91df5c56f01a06a452dfdc8a` contains only the four-line worker-family
rebuild and its WPT. Proof/evidence companion: `07dc1d27343268a8add266605c33fc5f966ef155`.
Four worker failures become passes; all 16 new checks pass. Nine existing files
retain 10 passes and one expected failure. Root freshly replayed the 18 Lean
list-model theorems and accepted the independent source/lifetime review within
its explicit provider, heap and concurrency limits. Discovery was static audit
and browser isolation, not Lean. Final WPT differs from the paired test only by
two spec metadata comments. The loaded-descriptor/provider repair is separate.
See [acceptance](../css-worker-font-removal-fix-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)
and [commit check](../css-worker-font-removal-fix-v1/ROOT-COMMIT-CHECK-v1.json).

## New native-verified patches

These are not yet signed commits or additions to the formally accepted count.
Each patch contains only the native repair and its WPT. Full proof/tooling
companions remain separate.

| Repair | Minimal patch | Landing constraint |
| --- | --- | --- |
| Cumulative rollback exclusions (A+B+D) | [fix-a-b-d-v1.patch](../css-layer-cutoff-composition-probe-v1/fix-a-b-d-v1.patch) | Coherent repair supersedes original A/B patches; 80 assigned cases pass without C |
| Logical/physical rule exclusion (C) | [fix-c-after-a-b-d-v1.patch](../css-layer-cutoff-composition-probe-v1/fix-c-after-a-b-d-v1.patch) | Follows A+B+D; final browser gate passes; local performance pair recorded; full source quotient remains open |

## Further counterexamples and repairs in progress

The full line-break provider proof found a supplementary Ahom/Thai UTF-16
counterexample that reaches browser layout: splitting a text node immediately
before a preserved newline suppresses an interior CJK wrap on the following
line. The final paired WPT has eight failures/305 controls before and 313 passes
after the narrow encoding/seek-width backport. Eight existing files retain all
46 passing checks; all paired source/binary pins are stable. ICU4X PR8144 already
structurally fixes this mechanism upstream; this is an old-version backport,
not a novel upstream defect. The three-file native/checksum/WPT patch applies
and reverses at historical HEAD/base. Lint and rustfmt pass. Independent exact
provider/full-breaker replay now passes from a fresh source-only copy. The
narrow backport is accepted and signed as `39ce7571a61097a80d5bf07adbc3ae48a2f0262e`,
following companion `28d9e8cc1065d7b00e3d891b42049c82d5e7058c`. Original language/LF
proof obligations remain open or refuted. Evidence:
`css-ahom-lf-partition-probe-v1/ROOT-SCOPED-ACCEPTANCE-v1.json`.

The expanded proof found a regression in important-inline candidate A: a
following outer `revert-layer` replaces its exclusion and revives a normal inline
physical alias. The 64-case WPT fails four cases on A+B+C. Removing A passes those
four but fails four distinct outer-value controls. The corrected implementation
preserves the intersection of origin, ordinary-layer and important-inline
cutoffs in constant space and passes all 64 cases. Related A/B/C tests pass
16/16/72 cases; existing tests retain six passes and two expected cycle failures.
All browser runs have stable source/binary pins. **Do not land A v1.** Independent native review and root replay of 24 Lean modules support the
correction within the recorded source/model boundaries. A+B+D passes its 80
assigned cases without C, with existing results unchanged. The C baseline atop
that correction has eight alias failures and twelve additional D alias failures;
its 116 controls pass. The proposed stack is one coherent A+B+D repair followed
by C, which adds its 72-case WPT and the remaining 16 D cases. Earlier A/B approval and
patch applicability are historical scoped evidence. No accepted count increment.
Evidence: `css-layer-cutoff-composition-probe-v1/ROOT-NATIVE-WPT-v2.json`.

Logical/physical `revert-rule` rollback (C) now has a corrected stack boundary:
the A+B+D predecessor passes its assigned 80 cases; C then fixes 20 failures
across its 72-case WPT and the complete 64-case composition WPT. All 136 pass on
the restored candidate, with stable source/binary pins. Root verified the
five-file predecessor and four-file C patch apply in order and reverse exactly
at historical HEAD. Both contain only native changes and their assigned WPTs.
A local three-cycle StyleBench pair scored 525.69 without C and 532.91 with C
(+1.37%, higher is better); this is exploratory evidence, not a speedup or
statistical no-regression claim. Actual compiled Declaration size grows from
24 to 32 bytes. The block-pointer/normalized-priority quotient and complete
observer/evaluation composition remain open. No signed commit or aggregate
formal acceptance increment is claimed. Evidence:
`css-layer-cutoff-composition-probe-v1/ROOT-STACK-VALIDATION-v1.json`.

Full cascade proof work exposed an important-inline layer rollback discrepancy:
an outer normal part rule is wrongly excluded. A second counterexample shows
that an intervening revert-rule replaces an earlier cutoff and restores an
excluded animation. Separate 16-case WPTs each reproduce one failure with 15
controls on the corrected v2 baseline. Repair A alone passes its 16 cases and
leaves B's failure unchanged. B alone passes its 16 cases but exposes a second
A failure previously masked by cutoff replacement. Thus B applies independently
as source but requires A first to avoid an observable regression. The original two-patch layout was superseded by the coherent A+B+D
repair above; neither historical patch should be landed alone. Both patches apply/reverse exactly at base and HEAD.
Existing rollback tests are unchanged on A-only, B-only and both: six passes
and two expected cycle failures. The combined build passes all 32 new cases.
The earlier independent review accepted that limited A/B matrix; its replay
is retained as historical evidence and is superseded by the composition review. The missing-body original
draft remains a harness-error record; no new full formal acceptance.
Evidence: `css-rollback-compound-fix-v1/ROOT-NATIVE-WPT-v1.json` and
`css-shadow-context-order-proof-v1/rollback-candidate-review-v1/REVIEW.md`.

The extended scoped-reference ownership WPT reproduces four inheritance
failures with eight controls; twelve existing tree-scope cases pass. A light
descendant inherits a slot-root reference despite having no local root/slot
lookup path. Exact decoder replay and a specialized all-integer Lean theorem
rule out numeric rebasing alone with the unchanged decoder. Root identity or
equivalent provenance, lifetime and style-reuse handling are required before
implementing the sparse/inheritance repair. Evidence:
`css-shadow-scope-ownership-probe-v1/ROOT-BASELINE-v2.json` and
`css-shadow-scope-ownership-probe-v1/SCOPE-REPRESENTATION-v2.md`.

The hyphenation proof's complete native consumer extraction produced a
coordinate-sensitive witness. A dictionary/font-pinned WPT now reproduces two
auto+soft-hyphen failures with six controls and passing line-origin calibrations.
The one-comparison native repair now passes all eight cases. Twenty existing
tests retain nineteen passes and one expected failure. Source, font, dictionary
and metadata inputs are pinned across the paired runs. Its two-file patch
applies/reverses at base and HEAD, excluding the signed-ligature repair. Root
independently rechecked nine Lean coordinate/refill theorems; complete native
consumer composition and machine/font premises remain open.
Evidence: `css-hyphenation-measurement-offset-probe-v1/ROOT-NATIVE-WPT-v1.json`.

C10/C11/C13 of the full saturation composition scope are refuted on the frozen
saturation-only candidate by the rollback witnesses. The scope is preserved;
unaffected lemmas continue, and corrected combined sources will need explicit
binding and independent review. These new leads do not change accepted counts.

## Shadow cascade and line-break checkpoint

Configured signing retry 36738 again failed with the 1Password buffer error;
HEAD and the staged companion are unchanged. Signing remains enabled. Evidence:
`css-shadow-context-order-fix-v1/SIGNING-RETRY-v1.json`.

The shadow-order baseline has 26 failing and 118 passing new WPT subtests.
Failures cover exported-part important/layer rollback at depths 8–32 and
forwarded-slot important/layer rollback at counts 7–32. Ten existing regression
files retain 71 passes, two expected failures and one OK harness result.
The four-file native candidate widens the packed level to u32, assigns negative
slot ordinals directly and checks representability instead of aliasing contexts.
The build, formatting and independent actual-source boundary replay pass. All
144 new WPT subtests pass, fixing all 26 baseline failures; the ten existing
regression files are unchanged. Lint has zero errors and two ignored-WPT
warnings. The standalone six-file patch applies/reverses at base and HEAD.
Full C1–C13 formal production is now active; no aggregate acceptance increment.
Evidence: `css-shadow-context-order-fix-v1/ROOT-NATIVE-WPT-v1.json`.

A separate sparse scoped-name lookup probe has one failure and three controls;
its complete pseudo-map/provider design is frozen and is not folded into
the saturation repair. The expanded saturation-only pseudo probe has 12 failures
and 12 controls across depths 2/6/8/32, with all support and geometry calibrations
passing. Evidence: `css-shadow-sparse-pseudo-probe-v1/ROOT-SATURATION-ONLY-v1.json`. The newline consumer probe has no geometry or independent
expectation discrepancies across 1,440 calibrated fixtures. The raw partition
invariant remains refuted. Additional consumer proof work is approved without
changing that failed obligation. Full language and hyphenation caller proofs
continue. Accepted and committed counts are unchanged.

### Current acceptance and signing status

- Private-use text emphasis: root accepted the full v2 scoped proof after the
  independent review closed the earlier arbitrary-run gap and supplied missing
  original exhaustive executions. Three new and nine existing reftests pass;
  two baseline failures repaired. Separate eight-file native/WPT patch remains
  uncommitted. Evidence: `css-text-emphasis-pua-fix-v1/ROOT-FORMAL-ACCEPTED-v2.json`.
- Signed ligature advances: root accepted independent native/font/oracle and
  formal review. Four baseline failures repaired; all 48 new cases pass, with
  unchanged results across 26 existing files. Separate three-file native/WPT/font
  patch: `css-negative-ligature-fix-v1/fix-candidate-v1.patch`.
  Evidence: `css-negative-ligature-fix-v1/ROOT-FORMAL-ACCEPTED-v1.json`.
- Sticky auto-inset and writing-mode repairs pass independent native review;
  their full formal companions remain pending.
  Their four-combination build/WPT matrix passes; neither is counted above.
- Latest signing retry 41911 failed with the 1Password buffer error. No new commit
  hashes exist. HEAD and the staged RGB companion remain unchanged, with signing
  enabled. Evidence: `css-sticky-writing-mode-fix-v1/SIGNING-RETRY-v1.json`.

The sections below retain the chronological evidence and earlier checkpoints.

### Earlier uncommitted checkpoint — 18 October 2026

- Animation composite-only updates: 70 new and 340 existing subtests pass,
  fixing 52 baseline failures. Independent native review passes. Full formal
  review found required import-closure, consumer-cache and null-provider
  corrections; root replay confirmed the v1 review findings. Independent v2
  review closes import/null/restyle issues but still requires delivered-readiness
  and equal-setter cache preservation. Root rechecked the frozen review;
  Full v3 correction and independent review are now root-accepted after
  1,498-file authentication and recheck0, with the original scope retained.
  Evidence: `css-animation-composite-fix-v1/ROOT-FORMAL-ACCEPTED-v3.json`.
  Single native/WPT commit remains pending configured signing.
- Root `rlh` zoom: final isolated two-file patch applies at branch base and
  HEAD. Build and 34 new/28 existing subtests pass, fixing 15 baseline failures.
  Evidence: `css-root-rlh-zoom-fix-v1/ROOT-NATIVE-WPT-v2.json`.
  The v2 supplement closes the dependency-state gap. Root accepted full scoped
  independent review after authenticating 528 files and rerunning its checks.
  Evidence: `css-root-rlh-zoom-fix-v1/ROOT-FORMAL-ACCEPTED-v2.json`.
  Single native/WPT commit remains pending configured signing.
- Private-use text emphasis: isolated eight-file native/WPT patch; three new
  and nine existing reftests pass, fixing two original failures. Root accepted
  independent native review and approved the full formal scope, now in production.
  Evidence: `css-text-emphasis-pua-fix-v1/ROOT-INDEPENDENT-NATIVE-v1.json`.
- Percentage `shape-margin`: isolated four-native/two-WPT patch; all 306 new
  subtests pass, fixing 148 baseline failures. Twelve existing reftests pass;
  three expected failures remain. Build/format pass; root accepted the independent
  native review. Formal work remains. Evidence:
  `css-shape-margin-basis-fix-v1/ROOT-INDEPENDENT-NATIVE-v1.json`.
- Initial View Transition types: five duplicate-deletion selector failures
  reproduced with sixteen controls. Startup deduplication passes all 21 new and
  three existing subtests; isolated two-file patch applies at both bases.
  Root accepted independent native review; formal work remains. Evidence:
  `css-view-transition-types-fix-v1/ROOT-INDEPENDENT-NATIVE-v1.json`.

- Language-sensitive line breaking: the final three-file native/WPT patch fixes
  29 original failures; all 360 new cases, 48 existing subtests and two reftests
  pass. Immediate words use their own language, and Latin-1 buffering now updates
  language state. Root accepted independent native review and approved the full
  formal scope; implementation is active. Evidence:
  `css-line-break-language-fix-v1/ROOT-INDEPENDENT-NATIVE-v1.json`.

- Hyphenation policy ownership: six browser failures and 43 passing cases,
  including dictionary calibration, with dictionary/loader inputs pinned.
  Later inline limits affect an earlier whole word. Expanded coverage has
  54 failures among 289 cases; candidate passes all 289. Nineteen own-limit
  controls, 360 language cases, 48 existing subtests and two reftests pass.
  Separate five-file patch applies at both bases. Independent review then found
  a per-continuation style omission: four first-line/first-letter probes fail on
  candidate1 and all four pass before the repair. Candidate2's range correction
  passes 722 checks. Final candidate4 preserves offset guards and empty-range
  finalization; build and 722 checks pass. Lint has zero errors and three
  ignored-WPT warnings. Root accepted the collaborative native/evidence review
  after 762-file authentication and 66-live-pin recheck. Full formal work is
  active; no aggregate acceptance yet. Final evidence:
  `css-hyphenation-ownership-fix-v1/ROOT-NATIVE-REVIEW-v4.json`.
  Evidence:
  `css-hyphenation-ownership-probe-v1/ROOT-BASELINE-v2.json`.

- Contained quote append invalidation: expanded baseline has 12 failures and
  52 controls; candidate passes all 64. Fifteen existing tests pass and three
  fail as unchanged metadata expects. Build/format pass, lint has zero errors
  and one ignored-WPT warning. A standalone three-file patch applies at both
  bases. Independent review and formal work are queued; no aggregate acceptance.
  Evidence: `css-quote-scope-append-fix-v1/ROOT-NATIVE-WPT-v1.json`.

Latest signing retry (session98203) failed with the existing 1Password buffer error. HEAD and
index are unchanged; signing remains enabled. The RGB companion remains the
only staged change. No new commit hashes are assigned to the work above.

| Finding | Fix commit | Regression test | Status |
| --- | --- | --- | --- |
| StyleBloom clear loses evidence of earlier counter saturation | `d855b3483b493c7e596b5d1d30d613fa7b7e2db5` | `testing/web-platform/tests/css/selectors/ancestor-filter-saturation-crash.html` | Previously completed; standalone Gecko change and WPT crashtest |
| Recursive relative-selector Bloom construction overflows on deep subtrees | `93a062cded54c974dff03ce2618aaf612a9c8d61` | `testing/web-platform/tests/css/selectors/has-deep-subtree.html` | Previously completed; standalone Gecko change, WPT, and required metadata |
| False-supports import incorrectly establishes layer order | `5d3638a91adf7b662041e192d121c7fd91c86f0a` | `testing/web-platform/tests/css/css-cascade/import-supports-layer-order.html` | Verified: baseline 4/16 fail; patched 16/16 pass; committed |
| Important user/UA declarations retain normal layer order | `e28cb48d656ba83097fb0960734e4317252e7d81` | `testing/web-platform/mozilla/tests/css/css-cascade/important-origin-layer-order.html` | Verified: baseline 10/21 fail; patched 21/21 pass; committed |
| Nested scopes choose the first outer scope's inner root instead of the closest matching inner root | `075be5516374d31c55a1e0f71b3fa80591042503` | `testing/web-platform/tests/css/css-cascade/scope-nested-proximity.html` | Baseline 4/14 fail; patched 14/14 pass plus 86 existing scope subtests; committed |
| Shadow-host traversal reports an unmatched scope-end selector as a limit | `a46e5310cd604adff10e914e82e8a326b9fb7957` | `testing/web-platform/tests/css/css-cascade/scope-shadow-limit.html` | Baseline 6/9 fail; patched 9/9 pass; 58 subtests and scope-part reftest pass; committed |
| Scope root is treated as its own scoping limit, contrary to the April 2026 draft update | `78c11c75170af5480a88fd9682db41183760f652` | `testing/web-platform/tests/css/css-cascade/scope-root-is-not-limit.html` | Baseline 5/10 fail; patched 10/10 pass; 128 scope subtests, 8 focus/hover subtests and reftest pass; committed |
| Relative-selector result cache reuses scope-dependent :has() matches across different scope roots | `d4a2b600f078d4c29e6dd8e0f1668121941a64e5` | `testing/web-platform/tests/css/css-cascade/scope-has-cache-scope-element.html` | Baseline 7/13 fail; patched 13/13 pass plus 58 related scope subtests; committed |
| Filtered nth-index cache reuses sibling counts across different scope roots | `92c013c16908bd30593ca7385b24dad1be4288dc` | `testing/web-platform/tests/css/css-cascade/scope-nth-cache-scope-element.html` | Baseline 10/20 fail; patched 20/20 pass, 13 has regressions and four reftests pass; committed |
| Scope-limit changes stop invalidation inside a relative selector instead of reaching the enclosing rule subject | `64ac54569f1cc202172ded92ee23ba749cd3284e` | `testing/web-platform/tests/css/css-cascade/scope-limit-has-invalidation.html` | Baseline 32/40 fail; patched 40/40 pass, 131 total selected subtests; independent 138/138 mutation comparisons pass; committed |
| Filtered nth positions are not propagated when a relative anchor has a non-subject tail | `b1b1bacb9406d75f35648d40a70ce9ad0fc3ab69` | `testing/web-platform/tests/css/selectors/invalidation/nth-of-has-nonsubject.html` | Original baseline 5/8 fail; final expanded WPT 10/10 pass, 70 total subtests and two reftests pass; independent 130/130 comparisons pass; committed |
| Scope wildcard revalidation gives equal nth results for elements with different real filtered positions | `f4b34bf7fef125857979a210616d201e28eefded` | `testing/web-platform/tests/css/css-cascade/scope-nth-revalidation-sharing.html` | Baseline 10/20 fail; patched 20/20 pass, 103 total selected subtests and two reftests pass; 78 static comparisons and 960 mutation comparisons pass; committed |
| Relative-length round simplification loses negative zero with infinite steps | `708b914901eeb7a2d348855c2efcf099e6003317` | `testing/web-platform/tests/css/css-values/round-infinite-step-relative-length.html` | Six valid original WPT cases fail; final corrected 64/64 pass, 217 existing subtests pass with two unchanged expected NaN failures; committed; literal-zero prose conflict documented separately |
| Name-only container queries do not invalidate after ancestor name changes | `238710ff9db7f54449c075bf80c7c3d40b43387a` | `testing/web-platform/tests/css/css-conditional/container-queries/container-name-only-invalidation.html` | Baseline 12/12 fail; patched 12/12 pass, 26 selected subtests pass; committed |
| Saturated animation iteration indices alias infinity, lose direction, and suppress iteration events | `0a81e1f36ab08a6d67ddd0bdd590e4661ff9b0a1` | `web-animations/timing-model/animation-effects/current-iteration-large-and-infinite.html`; `css/css-animations/CSSAnimation-large-iteration-events.html` under WPT | Baseline 12/52 fail; patched 52/52 pass, 246 selected subtests pass with five existing expected failures; committed |
| Registered numeric calculations resolve direct font-relative operands before the own font is ready | pending | `testing/web-platform/tests/css/css-properties-values-api/registered-numeric-relative-units.html` | Known failure area; baseline 24/76 fail, substituted/absolute/length controls pass; candidate built, existing tentative font-consumer expectations under review |
| Variable-bearing shorthand cache reuses another declaration after partial revert-layer | `11482ee213bf63c749b6d205c2c7591d783bdaa8` | `testing/web-platform/tests/css/css-variables/shorthand-substitution-partial-revert-layer.html` | Baseline20/28fail; patched28/28pass,74total subtest passes plus2reftests,4unchanged expected failures; preceding proof/tooling `f32fc6f2831ebe0987c9f0e9003b4597e3bce019`; committed |
| Color conversion loses analogous missing RGB components before interpolation | pending signing | `testing/web-platform/tests/css/css-color/color-mix-missing-cross-space.html` | Known-WPT-failure rediscovery;81baseline failures become132passes;42existing failures also fixed; final gate1374PASS/412unchanged expectedFAIL/4OK; proof companion staged separately |
| Multi-color mixing skips zero-weight prefix state needed by a later missing component | pending | `testing/web-platform/tests/css/css-color/color-mix-zero-weight-prefix.html` | Baseline12FAIL/4PASS →16PASS; selected1134PASS/67unchanged expectedFAIL, build passes; rational fold proof/source binding accepted (17audits); signing pending |
| Eager transform evaluation replaces deferred percentage-dependent accumulation with identity | pending signing | `testing/web-platform/tests/css/css-transforms/animation/transform-deferred-composition.html` | Baseline9FAIL/4PASS becomes13PASS;206total WPT passes and5OK,676distance/SMIL checks unchanged; bounded22-audit proof and final independent review accepted; native/WPT-only patch applies independently |
| Clamp simplification discards NaN operands | pending | `testing/web-platform/tests/css/css-values/clamp-nan-preservation.html` |49FAIL/45PASS→94PASS; existing406PASS/2expectedFAIL unchanged; full candidate47audit proof accepted with explicit native bridge premises; signing pending |
| Mod/rem lose finite dividends with valid infinite divisors | pending signing | `testing/web-platform/tests/css/css-values/mod-rem-infinite-divisor.html` | Baseline12FAIL/36PASS becomes48PASS;315total subtests pass and3OK; bounded12-audit proof and independent terminal review accepted; native/WPT-only patch applies independently |
| Nested progress censors NaN before outer calculation completes | pending spec-history review | Focused WPT pending | Nested opacity expression returns.5 instead of0; top-level NaN, finite and equal-endpoint controls pass |

The import finding has normal and important manifestations, covered by one fix.
The origin finding covers both user and UA sheets, also with one fix. Its WPT is
Mozilla-only because installing these origins requires `SpecialPowers`; it still
runs in the WPT harness. It includes author-origin and stable-order controls.

## Evidence

- Import investigation: `artifacts/css-spec-lean/research/import-layer-investigation-20261017/REPORT-v2.md`.
- Origin investigation: `artifacts/css-spec-lean/research/origin-important-layer-order-trace-20261017.md`.
- New WPT baseline: `artifacts/stylo-css-bugfix-baseline-v2.log` and `.jsonl`; local Firefox build ID `20261016094926`. Binary and test hashes: `artifacts/stylo-css-baseline-inputs.json`.
- The first baseline attempt is retained as `artifacts/stylo-css-bugfix-baseline.log`/`.jsonl`; port 8000 was occupied, so that attempt is infrastructure failure, not bug evidence.
- Patched tests: `artifacts/stylo-css-bugfix-patched.log`/`.jsonl`; 66/66 subtests pass across both new WPTs and existing `import-conditions.html`. Exact before/after outcomes and hashes: `artifacts/stylo-css-bugfix-verification.json`.
- Both committed patches independently pass `git apply --check` against `32226ddf3a29d58a52291babebdff2a5a7ce46c6`; browser testing used the combined build. Patch files and checks are recorded in the verification JSON.
- Targeted lint: 0 errors, two warnings because ESLint excludes these WPT files. Explicit warning output: `artifacts/stylo-css-bugfix-lint-warnings-v2.log`.
- Build and lint logs: `artifacts/stylo-css-bugfix-build.log` and `artifacts/stylo-css-bugfix-lint.log`.
- Local server configuration: `artifacts/stylo-css-wpt-ports.json` (temporary WPT override removed after testing; no test expectation changes).
- Patched full CSS-model replay: `artifacts/stylo-css-patched-origin-replay-v1/verification.json`; 141/141 queries, 1,310 metadata readbacks and 21 controls pass. Independent supplement: `artifacts/stylo-css-patched-origin-review-v1/REVIEW-v1.json` (15 corruptions rejected). Historical disagreement evidence remains unchanged.
- Nested scope verification: `artifacts/stylo-scope-investigation-v1/verification.json`, investigation `REPORT.md`, and independent source/terminal review in `artifacts/stylo-scope-review-v1/`.
- Shadow limit verification: `artifacts/stylo-shadow-limit-v1/verification.json`; independent investigation in `artifacts/stylo-scope-root-limit-review-v1/` and patch/terminal review in `artifacts/stylo-shadow-limit-review-v1/`.
- Root-limit verification: `artifacts/stylo-root-limit-v1/verification.json`; intentional spec change and original WPT expectations retained in the same directory. Independent source, expanded nesting-test, lint, and terminal reviews in `artifacts/stylo-strict-root-review-v1/`.
- Follow-up invalidation probe (no new defect): `artifacts/stylo-scope-invalidation-review-v1/DYNAMIC-REPORT-v1.md`; six mutation cases, 18 states and 36 computed values agree with fresh DOM controls.
- Relative-selector frontier audit (no new defect): `artifacts/stylo-relative-frontier-audit-v1/REVIEW-v1.json`; 48 browser cases pass. Search hints were inferred from source; Bloom activation was not observed, and the accepted proof domain was not extended.
- Earlier Bloom verification: `servo/components/selectors/verification/NATIVE-STORAGE-CHECKPOINT.md`.
- Scope-sensitive relative result cache: `artifacts/stylo-scope-has-fix-v1/verification.json`;
  independent investigation and patch review in `artifacts/stylo-scope-has-independent-v1/`
  and `artifacts/stylo-scope-has-patch-review-v1/`.
- Scope-sensitive nth indices: `artifacts/stylo-scope-nth-independent-v1/REPORT.md`;
  WPT baseline in `artifacts/stylo-scope-nth-fix-v1/`.
- Handwritten scope-cache contract and finite bug witnesses:
  `artifacts/stylo-scope-cache-proof-v1/README.md`. These proofs followed source/native
  discovery; they do not establish Rust or Gecko refinement.
- Implicit owner movement (no defect): `artifacts/stylo-implicit-scope-owner-v1/OWNER-MOVE-REPORT.md`;
  192 state comparisons with fresh DOMs agree. Shared/adopted/cloned sheet audit:
  `artifacts/stylo-implicit-scope-independent-v1/REPORT.md`.
- Accepted CSS scope-model checkpoint and source-only archive reproduction:
  [ROOT-CHECKPOINT-20261017.md](ROOT-CHECKPOINT-20261017.md). The independent
  research commit is not a production bugfix.

- Scope-limit relative invalidation: `artifacts/stylo-scope-limit-fix-v1/verification.json`;
  independent reduction and patched replay in
  `artifacts/stylo-scope-limit-invalidation-independent-v1/` and
  `artifacts/stylo-scope-limit-invalidation-patch-review-v1/`.

## Maintenance

Add a pending entry when a defect is confirmed. Replace it with the full hash
after the standalone fix and regression test are committed; record actual local
test outcomes and limitations. Refresh hashes after any history rewrite. Keep
new findings separate from already completed fixes, and never record a research
or tooling commit as a production bugfix.

- Filtered nth relative invalidation: `artifacts/stylo-filtered-nth-fix-v1/verification.json`; independent terminal review and replay in `artifacts/stylo-filtered-nth-relative-audit-v1/`.

- Scope-dependent nth sharing: `artifacts/stylo-scope-nth-sharing-fix-v1/verification.json`; bounded proof and independent replay in `artifacts/stylo-scope-nth-revalidation-proof-v1/`.

## Breadth audit follow-up

- Name-only container query invalidation: the final 12-case WPT covers name
  addition and removal, three container types, and document/shadow descendants.
  Baseline 12 failures become 12 passes; all 26 selected subtests pass after the
  one-line dependency fix. Six original state comparisons also pass. Build and
  source/spec review complete; committed as `238710ff9db7f54449c075bf80c7c3d40b43387a`. Evidence:
  `artifacts/css-container-name-fix-v1/verification.json`.
- Animation finite iteration identity/parity and true-infinity direction:
  independent expanded 44-case timing WPT has nine failures; eight event
  tests have three failures. Committed as `0a81e1f36ab08a6d67ddd0bdd590e4661ff9b0a1`; all 52 new cases pass. Consumer/FFI trace and spec oracles:
  `artifacts/css-animation-iteration-review-v1/REPORT.md`.
- Literal negative zero: a follow-up 12-case probe finds three mismatches with
  current CSS Values prose, which requires literal `-0` to be positive zero.
  Existing upstream `signed-zero.html` deliberately expects the opposite.
  CSSWG issue9750 contains a later editor statement supporting literal
  negative zero, consistent with existing WPT. This is a spec/test conflict,
  not an accepted new Gecko bug; parser behavior and Round commit stay unchanged.
  The arithmetic-generated negative-zero tests avoid either interpretation. Evidence: `artifacts/css-literal-zero-review-v1/REPORT.md`; original probe retained in
  `artifacts/css-literal-zero-investigation-v1/`. Existing signed-zero WPT
  passes all 162 subtests on the combined Round/container build.

- Animation iteration verification: `artifacts/css-animation-iteration-fix-v1/verification.json`.

- Animation bounded proof and independent replay: `artifacts/css-animation-iteration-proof-v1/ROOT-REVIEW-v2.json`; six audits, no native/IEEE/event refinement.

## Second breadth audit follow-up

Static reports and finite native confirmations are collected under
`artifacts/css-breadth-audit-round2-v1/`. The three new pending entries above
are not committed fixes or formal-verifier discoveries. They arose from static
spec/source audits and explicit browser probes. Actual process42002 and39481
both exited1 for the expected mismatches; binary/script inputs stayed unchanged.
`probes/RESULTS-v1.json` binds raw evidence. Generic runner exception text refers
to mutation/fresh parse, but these probes use explicit computed-value oracles.

- Shorthand-cache fix verification: `artifacts/css-shorthand-cache-fix-v1/verification.json`; independent terminal review and bounded8-law proof accepted.

## Third breadth audit follow-up

`artifacts/css-breadth-probes-round3-v1/RESULTS-v1.json` records actual terminal
sessions28562 and46879, each exit1 for semantic mismatches. All26cases parse;
browser, XUL, scripts and runner hashes remain unchanged. Math has12mismatches
across21cases, including2already-known pow failures. Transforms has6component
mismatches in2of5cases, with all3controls passing. These observations followed
static spec/source analysis; no Lean-discovery or release-prevalence claim is
made. Independent source/spec reviews are in `css-math-oracle-review-v1` and
`css-transform-deferred-review-v1` under artifacts. Known pow failures remain
calibration evidence rather than an additional newly discovered bug.

## Fourth breadth follow-up: reproduced candidates

No commits yet for these candidates. Independent normative acceptance is still
in progress; these are browser mismatches, not formal-verifier discoveries.

| Candidate | Commit | Evidence |
| --- | --- | --- |
| Numeric attr whitespace and whole-token fallback | pending signing | 22 FAIL / 31 PASS become 53 PASS; 247 existing passes unchanged; token-model proof and 2,450 bridge cases accepted; `artifacts/css-attr-numeric-fix-v1/verification.json` |
| Active attr fallback-cycle discovery | pending |16of32cases disagree, ordinary/valid-primary controls pass; same evidence |
| Equal-size physical/logical animation shorthand precedence | pending signing | 12 FAIL / 7 PASS become 19 PASS; 23 existing passes and two expected failures unchanged; isolated native/WPT patch and 14-audit conditional winner proof accepted; `artifacts/css-logical-shorthand-fix-v1/verification.json` |
| Early calc length conversion normalizes exceptional operands | pending review |Clamp-free width/opacity probes fail,2finite controls pass; `artifacts/css-calc-conversion-probes-v1/RESULTS-v1.json` |

Counter sentinel and reversed repeated-name candidates remain unexecuted static
hypotheses and are not counted as confirmed bugs.

Independent review accepts the two attr behaviors as separate conformance bugs:
`artifacts/css-breadth-audit-round4-v1/independent-attr-review/REVIEW.md`. Root
accepts equal-size animation conflict after checking the current ordered spec
rules and native comparator; receipt:
`artifacts/css-breadth-probes-round4-v1/ROOT-LOGICAL-REVIEW-v1.json`.
These acceptance decisions do not establish novelty or regression ranges.

## Fifth breadth follow-up: accepted observable bugs

Independent current-spec/native review accepts the following behavior families.
They were discovered by static comparison and browser probes, not by Lean.
Novelty and release-browser prevalence remain unestablished. Turkish dotted I
is existing bug 1887395 and is excluded from this list.

| Finding | Commit | Regression evidence / next gate |
| --- | --- | --- |
| Abspos subgrid placement clamps nonexistent lines into valid endpoints | pending signing | Expanded WPT: 32 FAIL / 164 PASS become 196 PASS; 16 existing subtests and four reftests pass, one expected reftest failure unchanged; `artifacts/css-grid-abspos-fix-v1/verification.json`. |
| Greek sigma casing uses Letter/Mark instead of required Unicode context properties | pending signing | 67 FAIL / 44 PASS become 111 PASS, and the new fixed-font rendering test now passes; 105 masking and 287 existing password assertions plus 24 compatibility reftests unchanged; `artifacts/css-sigma-fix-v1/verification-final-v1.json`; independent source, browser and scoped proof review accepted. |
| Lithuanian casing loses context across combining marks and omits above-mark cases | pending | Four incorrect innerText results; context-scanner repair and paired rendering WPT pending. |
| Whitespace transformation changes across equivalent text-node/inline partitions | pending | Six geometry discrepancies with all control partitions passing; WPT and mapped-flow repair pending. |

Evidence: `artifacts/css-breadth-probes-round5-v1/RESULTS-v1.json`. Independent
acceptance and root authentication:
`artifacts/css-breadth-audit-round5-v1/independent-review/ROOT-ACCEPTANCE-v1.json`.
The corrected adjacency citation is CSS Text `#text-encoding`; historical
producer reports are preserved, with the correction recorded independently.

## Sixth breadth follow-up: accepted observable bugs

These were found through static spec/native comparison and browser probes.
Independent review accepts the bounded scenarios below; root authenticated
101 evidence identities before the sizing native edit. No novelty or release
prevalence claim is made. The ratio family already has expected WPT failures,
and broad fragmentation/aliasing issues have historical Bugzilla coverage.

| Finding | Commit | Regression evidence / next gate |
| --- | --- | --- |
| Replaced Grid max-content inline size is overridden by initial stretch | pending signing | 24 FAIL / 24 PASS become 48 PASS; three existing reftests and four expected WPT042 failures unchanged; initial-selection proof and isolated native/WPT patch accepted; `artifacts/css-sizing-stretch-fix-v1/verification.json`. |
| Replaced border-box aspect ratio loses box adjustment under min/max constraints | pending | Canvas height 55.550003 instead of 50; three controls pass; existing WPT042 four expected failures reproduced. |
| Page-only requests affect fieldset/Grid placement in screen columns | pending | Four fieldset and eight Grid scenarios disagree with auto; ordinary-block page-only and nine incremental/fresh controls pass. |
| Ordinary block ignores modern break-before:always in columns | pending native investigation | Separate positive control stays at (0,20) instead of next column (100,0); not folded into page-only filtering repair. |

Evidence: `artifacts/css-breadth-probes-round6-v1/RESULTS-v1.json` and
`artifacts/css-breadth-audit-round6-v1/independent-review/ROOT-ACCEPTANCE-v1.json`.


## Seventh breadth follow-up: accepted observable bugs

The independent conditions review accepts six bounded defect families after
recomputing the probe oracles and authenticating sources, inputs and results.
Root read the review and authenticated its six retained files. These findings
come from static analysis and browser probes, not from Lean discovery. Novelty,
regression ranges and release-browser prevalence have not been established.

| Finding | Commit | Regression evidence / next gate |
| --- | --- | --- |
| Outer container-query operators omit attribute dependencies | pending signing | 76 FAIL / 8 PASS become 84 PASS; all 139 existing subtests unchanged. Independent native/WPT and scoped proof reviews accepted; `artifacts/css-query-attribute-wrappers-fix-v1/verification-final-v1.json`. |
| Constant border-box dimensions conceal changed query content dimensions | pending signing | 72 FAIL / 72 PASS become 144 PASS; 92 controls pass with the same four existing unexpected passes. Independent native/WPT and scoped proof reviews accepted; `artifacts/css-query-content-box-fix-v1/verification-final-v1.json`. |
| Deferred size query selects an ineligible nearer ancestor | pending | Two intervening-ancestor cases fail in both reused and fresh documents; direct/literal/named/eligible-inner controls pass. |
| Deferred query threshold changes do not invalidate the result | pending | Named and unnamed threshold mutations remain stale at fixed size; fresh results are correct. |
| Registered boolean style queries test presence instead of initial-value equality | pending | Three initial/default-value cases incorrectly match; noninitial and explicit-initial controls pass. |
| Style queries treat unset as absence instead of resolving the property's default | pending | Four inherited/registered cases incorrectly fail; differing-value controls pass. |

Evidence: `artifacts/css-breadth-probes-round7-v1/conditions/RESULTS-v1.md` and
`artifacts/css-breadth-audit-round7-v1/conditions-independent/REPORT.md`.
Root authentication: `artifacts/css-query-attribute-wrappers-fix-v1/ROOT-REVIEW-PINS-v1.json`.
Four unknown-feature OR failures are existing WPT expectations, not new entries.
Each family retains a separate prospective fix/WPT commit. No commit hash exists
for these entries yet; signing remains blocked and has not been disabled.


### Seventh breadth rendering and timing follow-up

| Finding | Commit | Evidence / qualification |
| --- | --- | --- |
| Displaced gradient hints discard linear-sRGB interpolation while materializing stops | pending compositor gate and repair | Six software snapshot samples are 128 instead of approximately 188; 34 controls pass. `artifacts/css-breadth-probes-round7-v1/runtime-independent/REVIEW.md`. No compositor/release output claim. |

Large-step extrapolation is a confirmed observable consequence of the known
bug 1706157 fallback, retained as a scoped repair candidate rather than a novel
overflow discovery. Distinct keyframe offset collapse is observed precision loss
with unresolved conformance; it is not an accepted conformance-bug entry.


## Eighth breadth follow-up: accepted scroll-snap defects

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Off-axis oversized snap area admits an invalid resting position | pending | Both x/y stop at 400 despite the only valid position being 0; removal, small-area and semantic controls pass. |
| Zero-area snap target loses retention after consecutive layout changes | pending | Both x/y, with and without competitor, follow 500→550 then remain at550 when target moves to800; nonzero-area and single-jump controls pass. |

Root normative/source/raw geometry review:
`artifacts/css-breadth-probes-round8-v1/scroll-snap/ROOT-REVIEW-v1.md`.
The fixture author's separate receipt recalculation is explicitly disclosed.
The completed run has 24 cases/44 states, six differences in64 correctness
comparisons, and840 passing geometry comparisons; all support/setup/settling
checks pass. No release, regression-range or novelty claim. Each family needs
its own native/WPT repair and preceding proof/tooling companion.

## Eighth breadth follow-up: accepted table sizing defects

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Negative spanning-cell contribution removes required table border spacing | pending signing | 30 FAIL / 60 PASS become 90 PASS; 61 existing passes and 11 expected failures unchanged. Native/WPT and scoped proof reviews accepted; `artifacts/css-table-span-spacing-fix-v1/verification-final-v1.json`. |
| Unassigned fixed-layout columns discard the allocation remainder | pending | 18 states yield a 101px table, 100px track sum and 1px end gap instead of zero; explicit-zero and divisible controls fill. |

Independent review: `artifacts/css-breadth-probes-round8-v1/tables-independent/REPORT.md`.
Root acceptance: `artifacts/css-breadth-probes-round8-v1/tables/ROOT-REVIEW-v1.json`.
Both fresh and mutated documents show the same failures; 15,558 consistency
checks agree. These are two sizing families, not 102 distinct bugs. WPT baseline
settings include disabled pixel alignment and must be tested separately. The
residual tolerance is a Gecko diagnostic criterion, not universal CSS precision.
Each fix needs a separate native/WPT commit and preceding proof companion.

## Ninth breadth follow-up: accepted polygon defect

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Large polygon coordinates corrupt float exclusion before margin-box clipping | pending signing | 16 FAIL / 16 PASS become 32 PASS; two existing clipping reftests unchanged. Native/WPT and bounded arithmetic proof accepted; `artifacts/css-polygon-intercept-fix-v1/verification-final-v1.json`. |

Independent acceptance: `artifacts/css-breadth-probes-round9-v1/polygon-independent/REVIEW.md`.
Root evidence: `artifacts/css-breadth-probes-round9-v1/polygon/ROOT-REVIEW-v1.json`.
The native signed product exceeds its range even when the correct intercept is
small. Browser evidence is not an instrumented UB trace. No release, novelty or
security-impact claim. The widened helper preserves anchored integer rounding;
15 Lean audits and 29,615 native cases pass under explicit bounded-difference
and defined-preprocessing premises. The standalone patch contains only native
source and WPT; its 17-file proof companion is separate. Signing remains pending.

## Ninth breadth follow-up: accepted transform geometry defects

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| CSS-layout stroke-box leaves reference dimensions empty | pending signing | 72 FAIL / 144 PASS become 216 PASS; four CSS/SVG reftests unchanged. Native/WPT and scoped alias/cache proof accepted; `artifacts/css-stroke-reference-box-fix-v1/verification-final-v1.json`. |
| Perspective origin omits the reference-box displacement | pending | 12 states fail; padded content-box origins project child positions using the wrong center. Equivalent border-box, zero-padding and zero-Z controls pass. |
| Overflow clip incorrectly forces preserve-3d flattening | pending rendering gate and repair | 12 states give 25px instead of 100px along the rotated axis. Visible, hidden, flat, opacity and paint-containment controls pass; compositor/clipping not verified. |

Independent acceptance: `artifacts/css-breadth-probes-round9-v1/transforms-independent/REPORT.md`.
Root authentication: `artifacts/css-breadth-probes-round9-v1/transforms-geometry/ROOT-REVIEW-v1.json`.
All 47 semantic-control states pass. All 324 fresh/mutated component comparisons
agree. These are three geometry families, not 56 distinct bugs. Each needs its
own native/WPT commit and preceding companion. No release or novelty claim.

## Ninth breadth follow-up: accepted partial image sizing defect

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Missing intrinsic ratio discards an available natural dimension under object-fit none/scale-down | pending signing | Two new reftests improve FAIL→PASS; six existing SVG controls unchanged. Native/WPT and scoped proof accepted; `artifacts/css-object-fit-partial-fix-v1/verification-final-v1.json`. |

Evidence: `artifacts/css-breadth-probes-round9-v1/object-fit/ROOT-REVIEW-v3.json`
and `artifacts/css-breadth-probes-round9-v1/object-fit-independent/REPORT.md`.
All V3 source-loading, support, geometry and literal-reference gates pass.
V1 failed before measurement; V2 remains unqualified because two source metadata
observations were stale. Those attempts are preserved. The missing-ratio shortcut
has prior code history; no novelty, release-browser or compositor claim is made.
Next is a separate native/WPT repair and preceding optional-dimension proof.

## Tenth breadth follow-up: accepted positioning defects

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Fixed-margin excess is lost before absolute auto-margin resolution | pending signing | Expanded WPT: 240 FAIL / 552 PASS become 792 PASS; 70 existing subtests, two reftests and eight expected failures unchanged. Native/WPT and scoped proof accepted; `artifacts/css-abspos-auto-margin-fix-v1/verification-final-v1.json`. |
| Explicit-inset self-alignment uses a differently oriented static wrapper’s coordinates | pending | 24 displaced-position states per active/fresh mode; actual-CB alignment controls pass. Native/WPT repair and coordinate provenance proof pending. |

Independent report: artifacts/css-breadth-probes-round10-v1/positioning-independent/REPORT.md.
Root checker replay exits 0 and matches the independent receipt byte-for-byte;
root acceptance: artifacts/css-breadth-probes-round10-v1/positioning/ROOT-REVIEW-v1.json.
All 70 semantic-control states and 1,440 calibration components per mode pass;
all 600 active/fresh components agree. Two defect families, not 74 bugs.
The initial acceptance excluded negative IMCBs. Later primary issue review found
the CSSWG zero-floor resolution and reaffirmation; the expanded repair tests
negative IMCBs separately from negative post-margin space. See
artifacts/css-abspos-auto-margin-fix-v1/DESIGN-v1.md. No invalidation, novelty, or release claim.
Each family requires its own native/WPT commit with a preceding proof companion.

### Object-fit partial natural dimensions repair accepted

Native/WPT repair and scoped proof reviews are complete; commits are pending
configured signing. Both new reftests improve from FAIL (48,000 pixels each) to
PASS; all six existing SVG controls remain PASS. Fifteen Lean audits and 2,355
extracted-helper cases pass producer/root/independent replays with identical
receipts. ScaleDown whole-candidate selection is proved only for at most one
natural dimension; two both-present/no-ratio boundary changes are explicitly
excluded. Positive-ratio dispatch is preserved, not newly proved geometrically.
The standalone patch contains native source plus four WPT files; its 15-file
tooling companion precedes it. Final evidence:
artifacts/css-object-fit-partial-fix-v1/verification-final-v1.json.

## Eleventh breadth follow-up: accepted block-flow discrepancy

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Endpoint zero tests allow positive size or padding to collapse through | pending signing | New WPT: 36 FAIL / 54 PASS become 90 PASS; five existing reftests unchanged. V2 boundary probes pass: ten wrong offsets become zero; fragmented expression/literal geometry agrees, with no literal-control changes. |

Independent review: artifacts/css-breadth-probes-round11-v1/block-flow-independent/REPORT.md.
Root replay exits 0 with identical checker bytes and 146 authenticated review files;
acceptance: artifacts/css-breadth-probes-round11-v1/block-flow/ROOT-REVIEW-v1.json.
Positive preferred-height and bottom-padding paths are one candidate collapse
classification repair family. All raw active/fresh rectangles and styles agree;
this is not an invalidation finding. Repair design must preserve zero/unknown
eligibility and consider resolved sizes, padding, min/max sizing and fragmentation.
No release, novelty or universal used-zero/computed-zero equivalence claim.
The fix needs a standalone native/WPT commit with a preceding proof companion.

## Eleventh breadth follow-up: accepted masking defects

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Empty explicit SVG mask region skips required subtract/intersect composition | pending signing | Two new 80-cell static/mutation reftests improve FAIL→PASS; four existing reftests unchanged. Zero width/height and alpha/luminance covered; explicit empty-region output preserves other null causes. `artifacts/css-svg-empty-mask-fix-v1/ROOT-NATIVE-REVIEW-v1.json`; three-layer partial-alpha/transform/clip reference also passes. |
| Prepared CSS mask image with empty fill skips required subtract/intersect composition | pending signing | Four new reftests improve FAIL to PASS; four existing reftests unchanged. Covers zero dimensions and images positioned outside the painting area. Ten-line native repair and standalone WPT, plus passing rounded-clip boundary; `artifacts/css-image-zero-mask-fix-v1/ROOT-NATIVE-REVIEW-v1.json`. |

Independent review: artifacts/css-breadth-probes-round11-v1/masking-independent/REPORT.md.
Root replay 27773 exits 0 and matches the independent checker byte for byte;
438 review files authenticate. All 208 PNGs were independently decoded through
ImageIO, with eight wrong states/80,000 pixels per mode, 96 passing semantic
controls per mode, and no retained/fresh differences. Root acceptance:
artifacts/css-breadth-probes-round11-v1/masking/ROOT-REVIEW-v1.json.
These are two independently repairable native sites under one alpha-composition
contract; each needs its own native/WPT commit and preceding companion. Evidence
is software drawSnapshot only, with no compositor, release or novelty claim.

## Twelfth breadth follow-up: accepted duplicate adoption defect

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Last-occurrence sheet filtering discards earlier named-layer introductions | design reviewed; prototype/standards gates pending | 48 wrong named-layer colors per active/fresh mode across Document and ShadowRoot; all 180 semantic-control states per mode pass. |

Independent report: css-breadth-probes-round12-v1/cssom-duplicates-independent/REPORT.md.
Root replay matches the independent receipt byte for byte, with 174 frozen files
authenticated. Root acceptance: css-breadth-probes-round12-v1/cssom-duplicates/ROOT-REVIEW-v1.json.
This is one ordering family, not an invalidation-only defect or one bug per state.
The 12 anonymous-important differences per mode remain exploratory. A repair
must preserve both first layer introductions and last declaration precedence;
changing to first-only filtering or passing duplicates into unique storage is
insufficient. Native/WPT repair and preceding formal companion remain pending.

## Thirteenth breadth follow-up: accepted bad-URL recovery defect

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Whitespace-to-bad-URL handoff consumes a backslash before escape-aware recovery | pending signing | New WPT: 28 FAIL / 36 PASS become 64 PASS; five adjacent passes and three expected failures unchanged. |

Independent report: css-bad-url-recovery-independent-v1/REPORT.md. Root replay
matches its paired checker byte for byte, with 87 review files authenticated.
Root acceptance: css-bad-url-recovery-fix-v1/ROOT-NATIVE-REVIEW-v1.json.
The standalone patch contains only the tokenizer, required vendor checksum, and
WPT and applies to original base and HEAD. Initial builds that reused the cached
vendored crate are preserved; acceptance uses confirmed recompilation/relink and
paired WPT run 79528. The scalar suffix proof and finite exact native capsule
have passed root and independent review; see final acceptance below.
This was found by static spec/source analysis, then reproduced in the browser;
no Lean discovery, release impact, novelty or security claim is made.

### Block-flow collapse repair fully accepted

Native/WPT and scoped formal reviews are complete. Producer 9753, root 22432
and independent 78776 exit 0 with identical receipts: 34 Lean audits, 2,180 native
fixtures and 2,532 model evaluations. Independent stack-machine reconstruction
matches all 4,360 original/candidate outputs and all model outputs. Root replay
of the review verifier authenticates 156 frozen files. The universal model covers
finite normal-line trees with supplied providers; arbitrary fragmentation and
provider correctness remain outside it. A 25-file source/tooling companion must
precede the two-file native/WPT commit. Final acceptance:
artifacts/css-block-flow-collapse-fix-v1/verification-final-v1.json.

### Bad-URL recovery repair fully accepted

Native/WPT and scoped formal gates are complete. Producer 18271, root 24730
and independent 61915 exit 0 with identical receipts: 25 Lean audits, 7,132 native
fixtures in each macro mode and 8,268 model evaluations. The independent oracle
checks 85,584 candidate fields and 33,072 model suffix fields; root replay of the
review verifier authenticates 428 frozen files. The universal scalar theorem
does not prove raw UTF-8/native-state correspondence. A 229-file source/tooling
companion precedes the three-file tokenizer/checksum/WPT fix. Final acceptance:
artifacts/css-bad-url-recovery-fix-v1/verification-final-v1.json.

## Fourteenth breadth follow-up: accepted nesting specificity defects

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Packed specificity delta borrows across components during nesting substitution | pending signing | 22 failing WPT subtests become PASS; all38new,11existing subtests and3reftests pass. Optimized native/performance and scoped formal reviews accepted; verification-final-v1.json in css-nesting-specificity-fix-v1. |
| Invalid nesting parent arm retains ID/class prefix specificity | pending repair | Two browser discrepancies; plain parent substitution independently exhibits the error. Whole-arm filtering must preserve inner forgiving boundaries. |

Five shared controls pass. Root read the independent report and checker, replayed
it with exit 0 and authenticated 20 retained files and 36 stable runtime pins.
These are two separate reproduced defect families, requiring separate native/WPT
commits. They were found by source inspection and browser probes, not Lean.
Expanded controls and mutation/fresh equivalence remain required before repair
acceptance. Evidence: css-breadth-probes-round14-v1/ROOT-NESTING-REVIEW-v1.json.

## SVG formal acceptance and round 15 browser lead

SVG native/WPT and corrected v2 formal companion are accepted. Final packaging:
`artifacts/css-svg-empty-mask-fix-v1/verification-final-v1.json`. This is the
twentieth fully accepted repair awaiting configured signing. The v1 native
capsule remains rejected historical evidence.

The round15 bidi image probe reproduced four ordering discrepancies with eight
passing controls and 49 stable input pins. Independent defect review is pending;
no native patch or formal acceptance is claimed. Evidence:
`artifacts/css-breadth-probes-round15-v1/bidi-baseline-v1/ROOT-RESULTS-v1.json`.

## Fifteenth breadth follow-up: browser discrepancies under review

| Family | Commit | Gate |
| --- | --- | --- |
| Inline image embed/override loses specified strong bidi direction | pending repair | Four failures and eight controls pass; loaded images and both paragraph directions. |
| Collapsed spanning ruby annotation retains width | pending repair | Fresh/mutated collapse fails across three writing modes; explicit collapse and visible/hidden controls pass. |
| Sole preserved ruby whitespace is removed | pending repair | Direct, split-run and rbc cases fail across three writing modes with computed pre; explicit rb references pass. |
| Scrolling element style change misses anchor suppression | pending repair | Margin plus growth reaches 130 instead of 100; six controls pass. |
| Transformed fixed child can be selected as scroll anchor | native/WPT pass; independent review and proof pending | New WPT repairs one failure and preserves four controls; three existing tests pass. Original thirteen-case probe changes only the intended fixed-child case. |

These are not fixed or formally accepted yet. Root evidence:
`artifacts/css-breadth-probes-round15-v1/REPORT-v1.md`. Independent reviews are
assigned; retain separate repair/WPT commits if accepted.

Bidi independent defect review is now root-accepted:
`artifacts/css-breadth-probes-round15-v1/ROOT-BIDI-REVIEW-v1.json`. The other
round15 families remain under independent review. No patch acceptance is implied.

Ruby independent defect review is root-accepted for two separate inline-geometry
repairs: `artifacts/css-breadth-probes-round15-v1/ROOT-RUBY-REVIEW-v1.json`.
The trim-only repair is explicitly unsafe because later whitespace interpretation
assumes nonboundary neighbors. No production fix is accepted yet.

## CSS image final acceptance; nesting performance correction

The CSS image empty-fill repair is fully accepted within native/WPT and scoped
formal boundaries: `artifacts/css-image-zero-mask-fix-v1/verification-final-v1.json`.
The preceding source-only companion uses `tooling-paths-v2.txt` and
`SOURCE-PACKAGE-v2.md`; historical full-artifact verification is separate.
This is the twenty-first fully accepted repair awaiting configured signing.

Nesting A's first native candidate fixes all 22 failing WPT subtests; all 38 new
subtests and existing 11 subtests/3 reftests pass. Expanded boundary tests preserve
four separate B failures. However, actual-crate benchmarks show a material
35.06x slowdown at 1,000 parent arms/100 ampersands. This candidate is not accepted
for landing. A cached direct-parent contribution revision is under development.
Evidence: `artifacts/css-nesting-specificity-fix-v1/ROOT-WPT-REVIEW-v1.json` and
`artifacts/css-nesting-specificity-proof-v1/PERFORMANCE-REVIEW-v1.json`.

Both scroll anchoring defects are now independently reviewed and root-accepted
for separate repairs: `artifacts/css-breadth-probes-round15-v1/ROOT-SCROLL-REVIEW-v1.json`.
All five round15 findings have passed defect review; no round15 native patch
is accepted yet.

### Optimized nesting repair passes rebuilt browser gates

V2 caches direct-parent contributions and freshly counts other substituted
components. Root and independent source/performance reviews accept this strategy;
small overhead remains possible. Build26044 and WPT86724 exit0: all38new subtests,
11existing subtests and3reftests pass. Boundary87668 exits0 with all88observations
matching the earlier correctness-passing candidate, including four unchanged
separate B failures. The three-file patch applies independently at original base
and HEAD. Formal companion and final independent native binding remain pending.
Evidence: css-nesting-specificity-fix-v1/ROOT-WPT-REVIEW-v2.json,
ROOT-BOUNDARY-REVIEW-v2.json and ROOT-PERFORMANCE-GATE-v2.json.

The new fixed-scroll-anchor WPT baseline94273 reproduces one expected failure
and passes four semantic controls plus three existing tests. The isolated native
exclusion is applied, but not yet built or accepted. Evidence:
css-scroll-fixed-anchor-fix-v1/ROOT-BASELINE-REVIEW-v1.json.

### Nesting proof replay and fixed-anchor candidate

Optimized nesting native/WPT is independently accepted and root-reviewed in
css-nesting-specificity-fix-v1/ROOT-NATIVE-REVIEW-v2.json. Producer87069 and root91589
formal/native replays exit0 with identical receipt7863647d:29Lean theorems,133typed
comparisons,145actual-crate cases per variant,10native and6Lean semantic mutants.
Independent formal review remains required; no universal Rust refinement is
claimed. Source-only companion packaging is being clarified before acceptance.

Fixed-anchor build17708 and paired41566 exit0:all5new subtests and3existing tests
pass. Boundary25742 exits0 with159stablepins:all13case objects match original
except the repaired fixed-transformed case. The separate scroller-margin failure
remains;11controls pass. Format76021 exits0 with12unrelated restorations;lint12686
exits1 with0errors/1ignored-WPTwarning. The two-file patch applies at original
base and HEAD. Independent native/WPT review and a complete classifier/traversal
proof companion remain pending. Evidence:css-scroll-fixed-anchor-fix-v1/ROOT-WPT-REVIEW-v1.json
and ROOT-BOUNDARY-REVIEW-v1.json.

### Round16 lead, pending independent defect review

Zero-area motion-path reference geometry is reproduced in local run54822:
18polygon candidate cases fail,54controls pass,99inputs stable,all288observations
checked against an independent coordinate oracle. Fresh/mutated results agree.
This is a preliminary discrepancy, not an accepted new bug or native fix.
Evidence:css-breadth-probes-round16-v1/ROOT-MOTION-RESULTS-v1.json.

Configured signing retry36232 again exits128 with the 1Password buffer error.
HEAD and the12staged proof files remain unchanged; no local commit was created.

### Optimized nesting repair fully accepted

Final native/WPT/performance and scoped formal acceptance:
`artifacts/css-nesting-specificity-fix-v1/verification-final-v1.json`.
The standalone fix contains parser.rs,builder.rs and its WPT;43source/tooling/
guidance files precede it. Producer,root and independent replay receipts match.
The29producer theorems and one independent packed-order supplement have distinct
scopes; finite actual-crate execution is not universal Rust refinement. Invalid
parent-prefix defectB remains separate. This is the twenty-second fully accepted
repair awaiting signing; no new commit hash exists yet.

## Round16 motion defect accepted; generated-grid and text-overflow gates

| Finding | Commit | Current gate |
| --- | --- | --- |
| Valid literal polygon is discarded for a zero-area motion-path reference | pending repair | Independent normative/native review accepted; 18 failing cases and 54 passing controls, 288 observations |
| Whitespace-only generated grid content creates an anonymous row | pending repair | 12 failing cases, 36 passing controls; 192 observations |
| Text-overflow effective marker width leaks between lines | pending repair | 400 wrong pixels per capture; related controls pass |
| Vertical text-overflow marker paints into inline-end padding | pending repair | Both vertical modes show 400 wrong pixels per capture |
| Clip-to-marker mutation lacks cached float line edges | pending repair | 1,600 wrong pixels before and after separate control reflow; fresh/reflowed controls pass |

Root runtime records and motion acceptance live in
`artifacts/css-breadth-probes-round16-v1/`. Text-overflow strict pixel run59089
is rejected; versioned run22747 passes font/reference/control gates with an
explicit bounded glyph-edge mixture rule. These are source/browser findings,
not bugs discovered by Lean. No native repair is accepted from these probes.

Fixed-anchor independent native/WPT review now passes root replay:
`css-scroll-fixed-anchor-fix-v1/ROOT-NATIVE-INDEPENDENT-REVIEW-v1.json`.
Its scoped formal companion remains pending, so the fully accepted repair
count remains 22 awaiting configured signing.

### Round16 independent defect reviews complete

All five round16 families are accepted for separate repairs. Generated-grid
review/root replay authenticates 73 files and all 192 observations. Text-overflow
review/root replay13525 exits0, authenticating 204 files/180 origins, all three
retained PNGs and 78 crops (including the rejected strict run). Independent
source/spec, font and rational pixel oracles support all three families.
Accepted review records are ROOT-*-INDEPENDENT-REVIEW-v1.json under
css-breadth-probes-round16-v1; synthesis is css-breadth-audit-round16-v1/REPORT-v2.md.

Fixed-anchor producer67512 and root69253 full formal replays exit0 with identical
summary00fb866e: 4,929 native cases per variant and Lean exports, 48 audited
theorems, 12 complete native semantic mutants, six executable Lean mutation
witnesses and eight separate diagnostics. Independent formal review remains
pending; no change to the count of 22 fully accepted repairs awaiting signing.


### Text-overflow line-state repair: paired browser gates passed

Commit remains pending. The isolated fix is two assignments in TextOverflow.cpp
plus four WPT reftests and one shared reference. Static/growth/restoration change
FAIL→PASS; shrink and ten existing outcomes are unchanged. Six-file patch applies
at originalbase+HEAD: css-text-overflow-line-state-fix-v1/fix-candidate-v1.patch.
Formal companion and independent native acceptance remain pending. The separate
rectangle probe retains one corner-pixel rejection; do not report it as a full
pixel-oracle pass. Evidence: ROOT-WPT-REVIEW-v1.json and ROOT-BOUNDARY-REVIEW-v1.json.

Fixed-anchor formal v1 is partial against its original scope. Independent raw-list
Lean traversal and rich-trace agreement are required in v2 before final acceptance;
its native/WPT review remains accepted. No new fully accepted repair is counted.

Round17 font matching has two reproduced preliminary families, awaiting independent
defect review: fractional scalar-score priority inversion and oblique search
threshold. Sixteen candidate cases reproduce, twelve controls pass. No fix commit
exists; css-breadth-probes-round17-v1/ROOT-FONT-RESULTS-v1.json records the gate.

Signing retry41015 exits128 (1Password buffer error); original HEAD and twelve
staged companion files remain unchanged. Twenty-two fully accepted repairs still
await signing. No unsigned commits or pushes were made.


### Round18 checkpoint: formal gates and preliminary breadth leads

Text-overflow A now has accepted independent native/WPT review and an exact
same-glyph boundary reference in both phases. The older rectangle oracle retains
its recorded one-pixel rejection. Root formal replay2756 passes and matches the
producer:20 theorem audits,138 cases,776 native rows per variant, seven native
semantic mutants and four executed Lean counterexamples. Independent formal
review is pending. Records: css-text-overflow-line-state-fix-v1/
ROOT-NATIVE-INPUT-CLOSURE-v2.json, ROOT-GLYPH-BOUNDARY-REVIEW-v2.json and
ROOT-FORMAL-REPLAY-v1.json. No final acceptance or new commit is claimed.

Fixed-anchor v2 root replay23530 passes with48 inherited plus37 new theorem
audits. Its4170 classifier rows and766 traversal rows are distinct coverage;
only the latter exercise independent traversal implementations. Source-only
closure verifies; independent formal review remains pending. Record:
css-scroll-fixed-anchor-fix-v1/ROOT-FORMAL-REPLAY-v2.json.

Round18 whitespace runtime retains two unexpected ASCII partition-control
failures; the overall run is not a pass. Zero-tab intrinsic sizing and positive
tabs at zero font size are reproduced leads awaiting independent adjudication.
Tiny-tab advance policy remains unresolved, and partition extensions overlap an
existing family. No new accepted bug is added. Record:
css-breadth-probes-round18-v1/ROOT-WHITESPACE-RESULTS-v1.json.

Counts remain16 committed fixes and22 fully accepted repairs awaiting signing.


### Fixed-anchor repair fully accepted

Independent v2 formal replay91017 and root checker both pass, matching producer
and root full replay summary0471241f. Root read the complete independent report,
raw-wire oracle and verifiers. The required independent interpreter milestone is
satisfied:37 new and48 inherited theorem audits,766 traversal graphs and4170
separate classifier inputs, with complete semantic trace comparison. Frame
construction, geometry, ownership and stable provider assumptions remain explicit;
this is not universal C++ refinement.

Final acceptance: css-scroll-fixed-anchor-fix-v1/verification-final-v2.json.
The39-file source-only companion precedes the standalone two-file native/WPT
patch. All current patch bytes still match the paired browser inputs. This is
the twenty-third fully accepted repair awaiting configured signing; no new
commit hash exists. Text-overflow formal independent review is now active.


### Text-overflow ordinary line-state repair fully accepted

Independent formal replay47771, root2756 and a fresh source-only replay16102 all
exit0 with identical receipt f2af5871. Root read and replayed the independent
raw-input oracle and verifier. The20 theorem audits and bounded native/model
comparison are accepted within the explicitly limited entry/cache scope; the
finite sequence theorem is definitional normalization, not C++ refinement.

Final acceptance: css-text-overflow-line-state-fix-v1/verification-final-v1.json.
The21-file source-only companion precedes the six-file native/WPT patch. This is
the twenty-fourth fully accepted repair pending configured signing. The original
rectangle residual remains documented alongside exact same-glyph references.

Round18 timeline run12247 reproduces two logical-axis errors on an orthogonal
pseudo scroller, with all six controls passing and39 stable inputs. Independent
review is queued after the anchor scout. Zero-tab WPT baseline56364 has126 FAIL
and18 PASS across144 subtests; thirteen existing reftests pass and one expected
failure remains. The zero-tab candidate is not yet applied. Independent tab
review is active. Signing retry86680 fails with the same1Password buffer error;
HEAD and twelve staged companion files are unchanged.


## Accepted defect queue and current repairs — 18 October 2026

| Finding | Commit | Evidence and remaining gates |
| --- | --- | --- |
| Zero-sized tabs inflate intrinsic inline size | accepted; signing pending | 126 failures become passes; all 144 new WPT cases pass. Native/WPT and corrected formal v2 independent reviews accepted and root replay passes. Final evidence: css-tab-zero-intrinsic-fix-v1/verification-final-v1.json. Preceding 33-file tooling commit; standalone two-file Gecko/WPT commit. |
| Positive tabs at zero font size fail to advance at an exact stop | pending repair | Independent defect/design review accepted; separate patch/WPT/formal gates still required. |
| Fractional font scores violate width/style/weight priority | accepted; signing pending | All26new WPT pass,12baseline failures repaired independently of font threshold B. Full scoped proof, independent review, four-way browser matrix and final build/lint pass. Preceding96-path source companion; separate6-file repair. Final record: css-font-priority-fix-v1/verification-final-v2.json. |
| Oblique font search uses 14 degrees instead of the 11-degree threshold | accepted; signing pending | All38new WPT pass;18baseline failures repaired; existing outcomes unchanged. Scoped proof and independent formal/native/WPT review accepted. Default oblique remains14. Preceding62-file source companion; separate2-file repair. Final record: css-font-threshold-fix-v1/verification-final-v1.json. |
| Pseudo scroll timelines resolve logical axes using their host's writing mode | accepted; signing pending | Final40-case WPT passes,16baseline failures repaired; full scoped proof and independent review accepted. Preceding42-path source companion; separate3-file repair. Final record: css-timeline-pseudo-axis-fix-v1/verification-final-v1.json. Four recreation-opacity failures retained separately. |

Root acceptance records: `css-tab-zero-intrinsic-fix-v1/ROOT-NATIVE-INDEPENDENT-v1.json`,
`css-tab-zero-intrinsic-fix-v1/ROOT-BOUNDARY-REVIEW-v1.json`,
`css-tab-boundary-independent-v1/REPORT.md`,
`css-breadth-probes-round17-v1/ROOT-FONT-INDEPENDENT-REVIEW-v1.json`,
`css-breadth-probes-round17-v1/ROOT-FONT-DESIGN-v1.json`, and
`css-breadth-probes-round18-v1/ROOT-TIMELINE-INDEPENDENT-v1.json`.

The timeline baseline preserves an existing vertical view-timeline failure.
Recreation-opacity and anchor changed-phase discrepancies remain unaccepted
separate leads. Counts remain 16 committed fixes and 24 fully accepted repairs
pending configured signing; no new commit hash is claimed.


### Pseudo-timeline isolated repair gate

Exact final40case pair:16FAIL→PASS, all40newPASS,24existing subtestPASS,
1existing expectedFAIL and1reftestPASS unchanged. Native original/candidate
builds and final candidate WPT succeed in cycle78913. Three-file patch:
`css-timeline-pseudo-axis-fix-v1/fix-candidate-v2.patch`; exact application at
original base and HEAD is recorded in `standalone-apply-v2.json`.
Root evidence: `ROOT-WPT-REVIEW-v2.json`. Orthogonal-root controls, independent
native review and formal acceptance remain pending; this is not repair25 yet.
Four separate recreation-opacity failures are preserved in the full diagnostic.

Round19 scrollIntoView center probe reproduces8discrepancies with14controls.
Independent review must establish the normative oracle and relationship to
known clipping bug2036965 before accepting a new defect. Filter component-transfer
hypothesis remains static-only. Neither is counted as an accepted repair.
Signing retry46762 failed; no additional commit hash exists.


### Round20 verification checkpoint

Timeline root paired cycle31715 passes:128time observations in eightfixtures are
identical original/candidate. Final independent native/WPT review and root live
replay pass (319closed origins,42live); ROOT-NATIVE-INDEPENDENT-v1.json records
acceptance within that scope. Formal completion/review remains required.

Zero-tab formal v1 was rejected against four explicit scope/integrity gates.
Corrected v2 preparation23824 and source-only56319 pass with identical summary
2176ea22:35theorems,2931native cases per variant,12native and6Lean semantic mutants.
New coverage includes432negative intrinsic and120saturation cases. Independent
v2 review is active. This is not final repair acceptance.

Zoom probe26576 reproduces six inherited-lh and two root-rlh discrepancies, with
41passing controls and42stable inputs. These are preliminary findings pending
independent adjudication; inheritance overlaps bug1887627, and root rlh extends
the earlier round2 lead. ROOT-ZOOM-RESULTS-v1.json retains the limits.

Signing retry78531 exits128 with the same1Password buffer error. HEAD, index
tree and all12staged companion file hashes are unchanged. Counts remain
16committed fixes and24fully accepted repairs pending configured signing.

### Zero-tab intrinsic sizing repair fully accepted

The frozen v2 independent review accepts all four corrections. Root authenticated
758 review files, read its report, both independent oracles, applicability witness
and verifier, and replayed its live integrity/oracle gate successfully. Independent
full source-only replay5887 matches producer23824 and root56319, summary2176ea22.
The formal boundary remains explicit: model agreement and bounded native execution,
with saturation outside the unsaturated Lean bridge; no universal C++/IEEE proof.

Final acceptance: css-tab-zero-intrinsic-fix-v1/verification-final-v1.json.
The current native/WPT bytes match the accepted pair. A supplemental source-commit
guide uses --source-only for packaged verification; that invocation passes on the
isolated 32-file package. The guide makes the preceding tooling commit33files;
the following repair commit contains only nsTextFrame.cpp and its WPT.

Counts are16committed fixes and25fully accepted repairs awaiting configured
signing. No new commit hash exists. Positive tabs at zero font size remain separate.

### Font B paired repair; failed marker image preliminary finding

Final font B cycle40521 exits0 with both builds successful and all38new WPT
subtests passing, improving18baseline failures. Six existing reftests and four
parser subtests pass; three existing expected failures remain. Lint has0errors
and one ignored-file warning. The final two-file patch applies at original base
and HEAD; independent formal/native/WPT review remains required before acceptance.
Record: css-font-threshold-fix-v1/ROOT-WPT-REVIEW-v3.json.

Marker runtime25533 reproduces five empty-item40px-vs0observations with32controls,
including settled removal/restoration and fresh-clone comparison. This remains
a preliminary lead pending independent adjudication, with no repair or commit.
Record: css-breadth-probes-round21-v1/ROOT-MARKER-RESULTS-v1.json.
Sixteen committed fixes and25fully accepted pending repairs remain authoritative.


### Current acceptance and runtime checkpoint

Font B is repair26accepted pending signing;16fixes remain committed.
Final record: css-font-threshold-fix-v1/verification-final-v1.json.
No commit hash is claimed: configured signing retry50594 exits128 with the
1Password buffer error and unchanged HEAD/index. Tooling62files must precede
the standalone2-file Gecko/WPT commit; no other fixes belong in that commit.

Two new preliminary leads have local runtime evidence, without repairs:

- Opacity/pointer-events descendant touch-action: one native APZ failure,
  four passing mode controls and existing zero-opacity control;74stablepins.
  css-breadth-probes-round21-v1/ROOT-OPACITY-RESULTS-v1.json.
- Private-use text emphasis: seven missing-mark observations and five exact
  controls with a loaded, identical-glyph font;70stablepins.
  css-breadth-probes-round21-v1/ROOT-TEXT-EMPHASIS-RESULTS-v1.json.

Both require independent normative/native/known-issue adjudication. Neither
changes accepted repair counts. Timeline clean formal replay passes; deep root
and independent formal acceptance remain pending.


### Independent lead review and font A replay checkpoint

Marker, opacity/touch and private-use emphasis have passed independent defect
adjudication and root authenticated replay; repairs/WPT/formal gates remain.
They are not included in the26accepted pending repairs. Multicol inline-filter
and highlight registered-value leads remain static, with probes prepared.

Font A native matrix is active, with original failures reproduced. Its complete
source-only proof replay22160 passes; independent full review remains required.
Timeline deep root review is complete and independent formal review is active.
There are still16committed fixes; no new commit hash or push is claimed.


### Timeline repair27 accepted; font A final cleanup gate

Pseudo-timeline logical-axis repair is accepted pending signing:42preceding
source/doc files, then the3-file Gecko/WPT patch. Authoritative record:
css-timeline-pseudo-axis-fix-v1/verification-final-v1.json. Counts:16committed
fixes,27fully accepted repairs pending configured signing.

Font A four-way matrix and independent formal/native review pass. A final unused
math.h cleanup requires refreshed build/WPT/lint and source binding; these are
active, so A is not counted yet. Its patch remains separate from font threshold B.

Highlight and inline-filter multicol probes each reproduce4predicted discrepancies
with24and20controls respectively. Their independent adjudication/repair gates
remain, and neither receives an accepted-repair count or commit hash yet.


### Font priority accepted; breadth scouts reproduced three leads

Font A is accepted repair28pending configured signing. Final build/WPT/lint
cycle76289 exits0:26A and38B subtests pass, all80raw result identities/outcomes
match the prior combined run,53pins stay fixed; lint reports0errors and one
ignored-WPT warning. Original/A-only/B-only/AB matrix proves the repairs work
independently. The final6-file patch applies at original base and HEAD.

The v2 source refresh changes only the unused header include and count labels.
Root authenticated93inputs/180receipts and independently checked57unchanged
native/oracle/mutation receipts; four generated translation units remain exact.
Independent full replay44525 and root verification of187review inputs pass.
The32general Lean theorems/11semantic witnesses and full five-consumer/global
scope are retained. Counts mean53628harness rows/30204consumer-entry rows,
not nested invocations. Provider, numeric, lifetime and platform boundaries
remain explicit. Source-only96-path companion precedes the6-file repair.
Final record: css-font-priority-fix-v1/verification-final-v2.json.

Composition run40649 reproduces3discrepancies among16observations with34stable
pins: composite-only updates leave both the getter and rendered value unchanged.
The null-target empty-property case removes CSS parsing as a prerequisite.
Value-changing/default-composite, ordered folds and commit-prefix controls pass.
Bug1778407 comments2–4 already report the symptom; no novelty claim is made.
Independent review is active. ROOT-COMPOSITION-v1.json retains root raw review.
Highlight4/28 and multicol4/24discrepancies also have active independent review.

Round23 font variation scout is frozen and root-read/replayed:131closed files.
Ranked leads are FreeType cast-before-clamp, optical-auto/face-descriptor order,
known font-size-adjust optical sizing, and feature-map/lifecycle invariants.
The first needs a complete native sanitizer gate and Linux/Android rendering;
Mac uses a different clamping path. Optical precedence needs normative review.
All remain static hypotheses or assurance targets. ROOT-FONT-VARIATIONS-SCOUT-v1.json
records the scope; no browser/native bug acceptance is inferred from arithmetic.

Zoom independent review is accepted as defect adjudication, with root replay;
root-rlh scaled/unscaled provenance is the narrower proposed first repair.
Marker, opacity and private-use emphasis remain separate accepted defect leads
requiring implementation/WPT/formal work. No new commit hash exists:16fixes are
committed and28repairs accepted pending configured signing. No push or signing
retry was made in this checkpoint. All root browser/build processes are terminal.

## Collapsed flex items: native gates complete, review/formal pending

No commit yet; excluded from the 30 accepted repairs awaiting signing.
Round28 static inspection found that collapsed struts remain participants in
main-axis distributed spacing and auto-margin allocation. The three-file patch
contains only nsFlexContainerFrame.cpp and two relevant WPT files.

- Paired WPT: 78 FAIL / 72 PASS become 150 PASS.
- Additional candidate controls: 240 PASS, including logical/reversed axes,
  ordinary zero-size participants and visible automatic margins.
- Existing checks: 82 PASS; build/format pass; lint zero errors/two ignored warnings.
- Standalone patch applies at base and HEAD; no isolated-base build performed.
- Patch: `css-flex-collapsed-alignment-fix-v1/fix-candidate-v1.patch`.
- Evidence: `css-flex-collapsed-alignment-fix-v1/ROOT-NATIVE-WPT-v1.json`.
- Independent native review and full formal companion/review are pending.

Column intrinsic cross-size and collection-stage gap leads are separate and
unaccepted. Large hyphenation-limit saturation is a reproduced range-policy
question, not another accepted defect or repair.


## Page-selector names: native gates complete, review/formal pending

No commit yet; excluded from the 30 accepted repairs awaiting signing.
The page-rule matcher accepted selectors with a different name from its lookup
bucket, affecting both applicability and specificity. The candidate passes the
bucket name into the matcher and filters before computing the maximum.

- Paired new print tests: 10 FAIL / 8 PASS become 18 PASS, with 47 unchanged
  inputs; only two Rust files and two binaries differ across the 51-pin pair.
- Six existing print regressions pass on original and candidate.
- Saved failing pages have a 20px green square displaced downward by exactly
  96px; all candidate test/reference images agree and retain the square.
- Build exits 0 (existing build-monitor KeyError diagnostics retained); format
  exits 0; lint has zero errors and six ignored-HTML warnings.
- Proposed standalone patch has two Rust files and six WPT files. It applies
  at original base and HEAD. Base stylist.rs retains its unrelated older scope
  code; the complete PageRuleMap implementation matches the current candidate.
  No isolated-base build was performed.
- Patch: css-page-selector-name-fix-v1/fix-candidate-v1.patch.
- Receipt: css-page-selector-name-fix-v1/ROOT-NATIVE-WPT-v1.json.
- Independent native review and full formal companion/review remain pending.

Signing retry71799 returns commit exit128: 1Password failed to fill whole buffer.
HEAD and the original twelve staged RGB companion files remain unchanged;
signing stays enabled. No new commit hash or push is claimed.

## Nowrap partitions: verifier-development lead reproduced in the browser

The language proof producer found a false arbitrary-partition glyph/sink equality
obligation using actual extracted native code. Root executed its standalone
probe and independently rederived 12 discrepancies and 60 passing controls from
character rectangles, computed styles and intrinsic widths. A nowrap inline in
a wrapping block breaks under break-all/anywhere: whole text has four lines,
while adjacent/nested partitions have two, where the independent nowrap oracle
requires one. Capitalization variants reproduce; block-nowrap and normal/keep-all
controls pass. Forty source/evidence/binary pins stay fixed.

This is a combined-worktree browser observation, not an original/release-browser
run or a completed Lean proof of a bug. The separate extracted original and
language-candidate evidence is retained. No repair or accepted count yet;
normative/native/known-issue adjudication and a standalone WPT repair are next.
Receipt: css-nowrap-partitions-probe-v1/ROOT-BASELINE-v1.json. The language proof
scope is unchanged, and its separate LF counterexample remains unresolved.

## Nowrap publication repair: native gates complete

No commit or formal acceptance yet; excluded from the 30 accepted repairs
awaiting signing. The language verifier's retained counterexample led to a
separate suppression repair in both AppendText publication paths. The helper
uses chunk-relative positions: INITIAL governs zero and INSIDE governs later
positions, preserving allowed breaks before the nowrap inline.

- New exact WPT pair: 36 FAIL / 133 PASS becomes 169 PASS. All 24 input
  identities stay fixed within each run; only one C++ file and two binaries
  differ between runs.
- Paired shared-service regressions: 724 PASS / 17 OK before and after, across
  21 files. Of 71 identities, the same three differ between runs.
- Build exits 0 with four retained build-monitor KeyError diagnostics. Format
  exits 0; unrelated changes restored exactly. Lint has zero errors and one
  ignored-HTML warning.
- Standalone patch contains nsLineBreaker.cpp and one WPT. It applies and
  reverses exactly at original base and HEAD, without language or hyphenation
  prerequisites. No isolated-base build or release-browser test was performed.
- Patch: css-nowrap-partitions-fix-v1/fix-candidate-v1.patch.
- Receipt: css-nowrap-partitions-fix-v1/ROOT-NATIVE-WPT-v1.json.
- Proposed full proof: css-nowrap-partitions-fix-v1/FORMAL-TARGET-DRAFT.md.
  Independent review and formal production/review remain pending. Existing
  language-only scope and LF/partition counterexamples are preserved.

The source-only PUA emphasis replay also passes freshly under root execution;
84 deterministic JSON/text receipts match the producer exactly. Only elapsed
cost timings differ, with identical units/draw counts/output sizes. This is
reproducibility evidence, not final formal acceptance. Root record:
css-text-emphasis-pua-root-review-v1/ROOT-REPLAY-v1.json.

## Negative ligature advance: browser baseline and candidate patch

No commit or final acceptance yet. Root tested an excluded numeric premise in
the PUA emphasis model and reproduced unsigned width expansion in
ComputeLigatureData. The native candidate uses a signed 64-bit quotient and
products, preserving the existing truncation and final-part remainder policy.

- New WPT baseline: 4 FAIL / 44 PASS, across text-node/span partitions and
  LTR/RTL. A retained standalone font creates negative advances through GPOS.
- Baseline shaping regressions: 24 PASS and 2 existing expected FAIL across
  26 files. Candidate browser gates remain pending while the build runs.
- Separate three-file patch: gfxTextRun.cpp, WPT HTML, and its test font.
  It applies and reverses exactly at original base and HEAD; no isolated build.
- Patch: css-negative-ligature-fix-v1/fix-candidate-v1.patch.
- Packaging receipt: css-negative-ligature-fix-v1/standalone-apply-v1.json.
- Tooling/font generator/proof must precede the eventual standalone fix commit.
  Independent native and formal review remain required. No acceptance increment.

PUA emphasis v1 has a separate root-identified universal dispatcher-to-plan
gap. It remains unaccepted; v2 correction retains the full approved scope.
Sticky positioning has three reproduced hypotheses awaiting additional controls
and independent adjudication, not three accepted repairs.

### Negative ligature candidate native gates complete

The candidate passes all 48 new WPT subtests (4 baseline failures repaired).
All 26 regression outcomes/expectations are unchanged: 24 PASS and 2 existing
expected FAIL. Build and format pass; lint reports zero errors and one ignored
HTML warning. The final three-file patch SHA-256 is
f82e0f68140c9754ad7db4bdff4f978457b9f8caccdfd71a10c9e37a73203f71.
Final native record: css-negative-ligature-fix-v1/ROOT-NATIVE-WPT-v1.json.
Independent native/font/oracle review and formal acceptance remain pending.
No commit hash exists yet and the accepted-repair count is unchanged.

## Sticky auto inset: native gates complete, review/formal pending

No commit or final acceptance yet. The candidate constructs the sticky view
using zero for auto insets and applies end reduction when either side is active.
Movement still tests the original specified-inset flags.

- Corrected exact WPT pair: 18 FAIL / 198 PASS becomes 216 PASS.
- V1 had two extra negative-zero expectation mistakes; preserved evidence and
  correction are in css-sticky-auto-inset-fix-v1/ORACLE-CORRECTION-v1.json.
- Seventeen existing sticky files retain 30 PASS / 2 expected FAIL / 8 OK.
  Fourteen shared view-timeline files retain 17 PASS / 14 OK.
- Build and format pass; lint zero errors, one ignored-HTML warning.
- Two-file patch: StickyScrollContainer.cpp and one WPT. Exact apply/reverse
  checks pass at original base and HEAD; no isolated build.
- Patch SHA-256: 001466c48760c278bc639cdb0ae2e8fe2ddb31886fd357f51d51536368b5fc85.
- Receipt: css-sticky-auto-inset-fix-v1/ROOT-NATIVE-WPT-v1.json.
- Independent review and formal companion remain pending; proposed full scope
  is in FORMAL-TARGET-DRAFT.md. Tooling/proof precedes the standalone fix commit.

The separate containing-block writing-mode and nested-invalidation leads remain
unrepaired. No acceptance-count increment. Signing retry41988 still fails with
the same 1Password error; HEAD and the twelve staged RGB companion files are
unchanged. Details: css-negative-ligature-fix-v1/SIGNING-RETRY-v1.json.

## Sticky writing-mode repair: independent patch matrix complete

No commit or full formal acceptance yet. Standalone patch:
`css-sticky-writing-mode-fix-v1/fix-candidate-v1.patch` (one Gecko file and one WPT).
Native/WPT receipt: `css-sticky-writing-mode-fix-v1/ROOT-NATIVE-WPT-v1.json`.

| Sticky source variant | Auto-inset WPT | Writing-mode WPT |
| --- | --- | --- |
| Original | 198 pass, 18 fail | 912 pass, 168 fail |
| Auto-inset only | 216 pass | 912 pass, 168 fail |
| Writing-mode only | 198 pass, 18 fail | 1,080 pass |
| Both | 216 pass | 1,080 pass |

All four builds succeed. Final combined source and binary are restored.
Existing sticky and view-timeline results are unchanged. Full proof companions
remain queued; independent native/spec/oracle review is root-accepted.

## Shadow-context depth: reproduced lead, no repair yet

Eight failing rows and 72 controls in the root's 80-case browser probe match the
static scout prediction. Both margin-left and an unregistered custom property
choose the wrong context at depths 8/9 when unrelated part-rule maps are present.
Fresh construction agrees with the dynamic result. Evidence:
`css-shadow-context-depth-probe-v1/ROOT-BASELINE-v1.json`.
Independent adjudication and representation design precede a fix; excluded from
the accepted-repair count. Discovery came from static analysis, not a Lean proof.

## Recursive attribute fallback preparation committed

`7822bb6d17b1381cdb3e56deb20c5ec3e078adec` contains only `Cascade::update_attributes_map` and its sixteen-case WPT.
Proof companion: `31265260cc3daa2bbea93c237a9491b6f2afcaa4`; browser evidence: `222c13771e052dae71bb6f62cc35e1a0522a91c3`.
Ten failures become passes; seventy existing checks pass. Three unchanged
type-eligibility diagnostics remain failing. Fresh root Lean replay passes
54 theorem audits (38 new) and rejects four semantic mutants. This is a finite
worklist/preparation model with manual source binding; native parser, provider,
observer and graph composition remain open. The browser pair used the shared
experimental tree; the exact commit excludes those unrelated changes.
See [acceptance](../css-attr-fallback-preload-browser-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)
and [commit check](../css-attr-fallback-preload-browser-v1/ROOT-COMMIT-CHECK-v1.json).

## MathML token range origin committed

`f843fd7568f30e14e664c37c36544d8d88e8c1bb` changes only `GetTrimmedOffsets` and includes two regression WPTs.
Review/evidence companion: `6eb5a90e3fa3b6128ddd6397d9dae9f1ab34b88d`.
Eight original failures become passes; all 26 new and 260 existing checks pass.
Original/candidate builds, repeated candidate results and lint passed. The
independent source review checks 128 branch combinations and distinguishes
significant trailing trimming. This is not a Lean proof of native geometry.
Pre-reflow/intrinsic measurement, element-box sizing and broader cache lifetime
remain separate. Browser pairing used the shared experimental tree.
See [acceptance](../css-mathml-tab-cache-wpt-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)
and [commit check](../css-mathml-tab-cache-wpt-v1/ROOT-COMMIT-CHECK-v1.json).

## Typed attribute fallback eligibility committed

`e3ba54f6f826fe265eb5bc4731f66f64465dd47c` contains only three Rust files and the twelve-case WPT.
Review and browser evidence precede it in `30c8dfeb4b746104b53ad5bc6440c1d53734f570`.
Five new-case failures and three retained diagnostics become passes; all 183
checks pass. Build and lint pass (zero errors, two warnings). The earlier
generic-parser model has fifteen theorem audits; this integration adds no
new theorem and does not close native parser, provider or graph admission.
The exact isolated patch excludes unrelated experiments; browser pairing used
the shared tree. Additional parse cost is unmeasured.
See [acceptance](../css-attr-typed-eligibility-browser-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)
and [commit check](../css-attr-typed-eligibility-browser-v1/ROOT-COMMIT-CHECK-v1.json).

## Attribute-only non-custom dependencies committed

`3892ab844694fedd987f5ce1dd2165f53fc2dbed` deletes the lexical-VAR early return in
`Cascade::maybe_note_non_custom_dependency` and adds a ten-case WPT.
Review/browser companion: `0db19774e6f2bf6692790459f8e6e54ca426e366`.
The ten new and 183 prior checks pass. Four baseline failures improve across
the scoped WPT and diagnostic; three resolved-unit metadata failures remain.
Build passes; warning-enabled lint has zero errors and one ignored-WPT warning.
Independent syntax and source/oracle review pass. No new native graph theorem
is claimed; discovery came from manual analysis of formal admission gaps.
See [acceptance](../css-attr-noncustom-browser-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)
and [commit check](../css-attr-noncustom-browser-v1/ROOT-COMMIT-CHECK-v1.json).

## Resolved relative-unit summaries committed

`58200fa81a6f92f92a1898ba2866a2fbcbac0daa` contains one Rust file and the 21-case WPT. It restores relative-unit
dependency metadata when storing resolved attribute and universal values. The
final formatted build passes all 227 checks; 13 baseline failures are repaired.
Evidence and independent reviews precede it in `03bad7f708329254a9af2073f0b4106ba557e914`. Lean selected-output
composition is conditional on token/provider correspondence; full tokenizer and
graph proofs remain open. Incomplete env payload scans retain their previous
behavior, and added scan cost is unmeasured.

## Token-category dependency repair committed

`26e0fa16e89eacd9fd9cab0ce6bb1be813d9e406` contains the Dimension-only guard and its 14-case WPT.
Identifiers, URLs, at-keywords and hashes no longer acquire false relative-unit
dependencies from their spelling. Seven baseline failures are repaired; all
241 checks pass. Evidence precedes the repair in `2e1f5f62c8a6325679a83adc7f637e104c488bf7`. The patch applies
and reverses against retained upstream/main `976279105b2e78b8666a959eb3f25c9176cefaf8`
without earlier local fixes; that isolated base was not built or browser-tested.
The discovery came from manual source/spec admission review, not a new Lean
counterexample. Full tokenizer and graph proofs remain open.

## Identifier-start escaped-newline repair

Prior upstream report: [cssparser issue440](https://github.com/servo/rust-cssparser/issues/440). The local work adds browser regression coverage and scoped formal evidence for the same defect.

Standalone native + WPT commit: `2ad505512c621776d62be9f1eb0bd7c137b93ee8` on local branch
`stylo-css-identifier-start-fix`, after proof/evidence companion
`bebbe8380a6982e94f8fcd61cfc4375ee6485d7e`. This is the independently applicable version
based on retained upstream `976279105b2e78b8666a959eb3f25c9176cefaf8`.

Working-branch integration: `09b008b3320fa29fcbcf081b252053e3721c5e10`. Both versions contain only the one-line
parser correction, its required vendor checksum update and the identical WPT.
The standalone version preserves upstream's URL recovery; the branch version
includes the prior URL correction in the file hash. They represent one repair,
not two fixes. No pushes or submissions were made.

Four reproduced LF/CR/CRLF/FF failures now pass. All eleven new subtests pass;
nine existing checks are unchanged, including four expected failures. A forced
vendored-crate rebuild and relink were necessary after the first incremental
build reused a stale parser library. Both attempts are retained. Lean proves
the modeled predicate correction and exact change domain under the stated
source/primitive assumptions. Source applicability is checked on upstream;
runtime validation uses the shared experimental tree, not an isolated build.

## Loaded FontFace descriptors committed

Standalone native + WPT: `f393d2d8c3b0abd6fa17709ab8dd519d8fdd5db2` on local branch
`stylo-fontface-loaded-descriptors-fix`, after evidence companion
`b8aa63373899fdab2d6b93848a12e8c2d506ad91`. Working-branch integration: `6bd0b00dcff5514a3234423787920ed44491a4bc`.
These are two versions of one repair. The standalone patch includes the required
worker family cleanup; the stack already has it from repair #50.

The standalone upstream-based candidate builds and passes all 76 new subtests;
all 90 checks have expected outcomes, including one unchanged expected failure.
Removing only the worker cleanup produces eight failures. Earlier shared-tree
pairing repaired 38 failures in the original 68-case matrix. Source and binary
pins, exact patches and both isolated runs are in
[validation](../css-fontface-provider-isolated-v1/README.md). Runtime validation
is macOS only; other backends have source review. The existing abstract provider
model does not establish full native lifetime or concurrency correctness.

## Compensating numeric exponents committed

Standalone native + WPT: `12c1208d2c4f485942164b7df7c276401b8e7b8c` on local branch
`stylo-css-numeric-range-fix`, after evidence companion
`b1e034259a8e3d553bb1528fa1982769f1002236`. Working-branch integration: `4391deb4751a8be2be98e838360f00c94808c5d5`.
Both versions contain only the numeric tokenizer change, vendor checksum and
one eleven-case WPT. They count as one repair.

Five reproduced failures become passes; all eleven new cases pass and 21
existing checks are unchanged, including four expected failures. Root and
independent source replays, rational bounds and semantic mutants pass. These
are conditional range arguments and bounded execution, not a complete numeric
or IEEE proof. The measured extracted-body overhead remains approximately
0.3–0.85 ns/token; browser performance is unmeasured. Runtime pairing uses the
shared tree. The standalone version applies and reverses on upstream without
prior local repairs, but has no isolated-base browser run.
See [validation](../css-tokenizer-numeric-root-v1/README.md).

## Whole-value declaration fallback committed

Native + WPT: `095c5be548a2bddf5f3ff01e01da66c6098a8ee5`, after proof/evidence companion
`320a3d100d7669c4508ab89570b9833390baed2d`. The commit contains only the parser reset and
its 48-check WPT. Property-parser cleanup can consume a forbidden top-level
curly block; validation now restarts at the saved value beginning.

All 24 reproduced failures become passes; all 48 new and 41 existing subtests
pass. The unchanged patch applies and reverses on retained upstream without
previous local repairs. Runtime pairing uses the shared macOS tree; no isolated
upstream build is claimed. Root and independent reviews accept 27 conditional
component theorems, four compiled native mutations and five integrity gates.
Raw byte/pending-state mapping, generated property grammars and complete
VariableValue semantics remain admitted. Source inspection found the bug before
the Lean component. Evidence: [acceptance](../css-declaration-curly-root-v1/ROOT-SCOPED-ACCEPTANCE.json).

## Declaration substitution publication repair

Stack commit: `780495d90a85052cff69713f1086180253cb9730`; preceding proof/tooling: `53e30d418ef77e3b9626aa3c1cd99e7fb9a87cbf`.
The native commit contains only the scratch-clear line and its 49-case WPT.
With link-parameters enabled, successful ordinary parsing containing var/env/attr
previously published both ordinary and deferred declarations. Fresh CSSOM setting
duplicated names; removal left a stale length/item/cssText entry with empty getters.
Twelve failing checks now pass and 135 other outcomes are unchanged, including one
existing metadata-expected ident() failure. All 49 new checks pass with normal and
important priorities. The same patch applies/reverses on the retained upstream base;
isolated upstream runtime was not run. No release-default exposure claim.

Root and independent fresh replay accept 29 conditional scratch-publication lemmas,
five native variants and four semantic witnesses. Callback canonicality, native
representation and full CSSOM destination lifecycle remain separate obligations.
Discovery was source inspection and browser reproduction before the Lean companion.
See [acceptance](../css-declaration-publication-root-v1/ROOT-SCOPED-ACCEPTANCE.json)
and [commit check](../css-declaration-publication-root-v1/ROOT-COMMIT-CHECK.json).

## All-shorthand logical ordering committed

Native + WPT: `074086719e445ca72d3056f7fbf793af5e69d6f6`, after formal companion
`bad8f7998dbbb3ad1fa88c0ca6892488f912e898`. The native commit contains only the shared
per-declaration ordering planner, sequential all executor and 40-case WPT.
Sixteen baseline failures are repaired; all 40 new and 61 existing subtests pass,
with 89 other outcomes unchanged. The same patch applies and reverses on retained
upstream; isolated upstream runtime was not run. The WPT compares relative order
with a fixed fresh expansion, without choosing the absolute canonical order left
open by CSSWG issue 5741. No rendering or measured performance impact is claimed.

Root and independent fresh source-only replays accept 55 model theorem audits,
3,042 passing candidate operations and six compiled mutation witnesses. Native container,
provider/equality, callback, compiler and full CSSOM lifecycle premises remain
explicit. Ordinary batching's universal proof is separate. Source/spec inspection
and browser reproduction preceded the formal companion.
See [acceptance](../css-all-logical-order-root-v1/ROOT-SCOPED-ACCEPTANCE.json) and
[commit check](../css-all-logical-order-root-v1/ROOT-COMMIT-CHECK.json).

## Registered keyframe substitution committed

Native + WPT: `188644f6d9833b485f35c2abcfad23cef2c5e9f7`, following evidence companion
`1cf91c4def90e6e7cce4e76106020ffcd4b45692`. Its three files expose the existing computed
custom-value constructor, consume the completed keyframe map for typed Unparsed
declarations, and add the sixteen-case WPT. Direct CSS-wide, Parsed, universal
and other declaration conversion paths are preserved.

Eight baseline failures become passes; all sixteen new checks pass. Six adjacent
passes remain and the existing cross-animation test remains expected FAIL, now
reaching a later assertion with different diagnostic values. Both builds and
scoped format/lint exit 0, with one ignored-WPT warning. Exact source application
and reversal pass on upstream and branch snapshots; browser pairing uses the
shared macOS tree, with no isolated upstream runtime claim.

Discovery was source inspection and browser reproduction during verifier work.
Independent source/spec, dependency and final native/WPT reviews passed. The
separate animation-identity proof does not establish numeric payload correctness.
The subsequent registered initial-value repair below resolves the fallback-initial
provider defect. Dynamic animation dependency behavior remains separate.
[Acceptance](../css-animation-taint-probe-v1/ROOT-SCOPED-ACCEPTANCE.json) and
[commit check](../css-registered-keyframe-root-commit-v1/ROOT-COMMIT-CHECK.json).

## Computed registered initial values committed

Native + WPT: `6aa2138c144aa6eee8e07aac77e7a68a8c7f7617`, following evidence companion
`3d194d59545c331fabc7ad1502af96522aa67c90`. Two Rust files use the existing computed initial-value
cache when explicit initial defaulting replaces a custom property. The twelve-case
WPT covers inherited/reset lengths, universal syntax and absent initial values.
Registration descriptor text is preserved.

Three ordinary failures become passes; all twelve new cases and 85 existing
checks pass. A separate five-case animation diagnostic also passes, repairing one
additional observation of this same provider defect; it depends on fix 70 and is
excluded from this standalone WPT. Both builds exit 0 with retained monitor errors.
Exact patch application/reversal passes on upstream and branch snapshots; runtime
pairing uses the shared macOS tree. Unrelated cascade changes are excluded from
the commit. No isolated upstream execution or performance claim.

Discovery was source inspection and browser reproduction during verifier work;
there is no Lean-discovered counterexample or universal theorem for this repair.
Root and independent source/spec/runtime reviews passed. Existing Stylist cache
freshness remains a provider contract.
[Acceptance](../css-registered-initial-value-fix-v1/ROOT-SCOPED-ACCEPTANCE.json) and
[commit check](../css-registered-initial-value-root-commit-v1/ROOT-COMMIT-CHECK.json).

## Explicit inheritance of invalid registered values committed

Native + WPT: `3a01fc986c7974161aadf4bfafe65c234b036b07`, following evidence `2e0f9f6b9ee5450cd21ac9341ef116dd91a8119b`.
The two-file patch copies an absent parent value instead of keeping the registered
initial value, while preserving root defaulting and restyle dependency tracking.
Three baseline failures become passes; all 40 subtests pass. Exact upstream patch
application/reversal passes; isolated upstream runtime was not run.

Independent replay accepts 17 conditional Lean audits and four model mutants.
Initial seeding, map/flag APIs, callers and compiler behavior remain admitted.
Source inspection and browser reproduction preceded this proof. The separate
substituted-inherit dynamic restyle defect remains a candidate.
[Acceptance](../css-registered-inherit-invalid-fix-v1/ROOT-SCOPED-ACCEPTANCE.json).

## Substituted inheritance restyle dependency committed

Native + WPT: `60bf34f48ac63ca595d519c1e0c2b4a2fa731b66`, after evidence `1ad6ea9740aa7f73ca299625208edf9856be807a`.
The two-file patch records reset-property inheritance after substitution, including
an absent parent value. Three baseline failures become passes; all 44 subtests
pass. Exact upstream patch apply/reverse succeeds, without isolated upstream
runtime. Format/lint pass; WPT ESLint ignore warning is retained.

Independent fresh replay accepts 14 conditional selected-value/dependency audits.
The model history's unrelated-flag preservation is a frame assumption; a native
recascade constructs a new style and is not proved to preserve those flags.
Caller delivery, change providers, maps and compiler remain admitted. Discovery
preceded formalization. [Acceptance](../css-registered-substituted-inherit-fix-v1/ROOT-SCOPED-ACCEPTANCE.json).

## Fix 74: exclude invalid custom properties from enumeration

Native + WPT: `0cac5c270615d04239bd4a4024a3ab5ffd0d24ae`, following count proof/review `d9d1047dd4b1592794229f3f7f7610ddedfd9aba` and runtime evidence `7b2926f6ac7eeffee378a18d8321c3e6dbcfd32c`.
The two-file commit updates live-value counting and filters tombstones from indexed
access, with a ten-case WPT. Tombstones still mask ancestor values.

The final local comparison improves 30/41 passing checks to 38/41; the remaining
three shadowing failures belong to the separate iterator repair. Count-only adds
no failures in this matrix and applies independently to the recorded upstream.
Fifty-five conditional Lean audits cover count changes and COW histories;
independent replay and four compiled model mutants passed their gates. Native
container/compiler/bounds and complete CSSOM lifecycle assumptions remain.
Discovery preceded the proof. See [acceptance](../css-custom-properties-map-count-root-v1/ROOT-SCOPED-ACCEPTANCE.json).

## Fix 75: skip shadowed custom-property ancestors

Stack native + WPT: `90ffac0a5e4076b6117ca152249f342a13995ee3`, following proof/composition
`215c881ef243f0268be11836d6c2a45e91b29b6f`. Its three files contain the loop-label correction
and two WPTs (nine cases). It follows fix 74's count/filter repair.

Independently applicable upstream alternative: `5d6308daf5f914cf851b69af0e04c146ef68aca6`
on `stylo-css-custom-property-iterator-fix`, preceded by evidence
`0dccc47ad01cadf9734aa06324c2b9870d5ee5c2`. This four-file alternative includes
necessary count/filter support and all three WPTs. The historical label-only
patch exposes an old count mismatch and is not a safe standalone option.

The three remaining local enumeration failures become passes; all 41 checks
pass in seven harnesses. The generic per-map Lean composition derives
RawEnumeration, live-count coherence, valid indexed access, unique keys and
nearest-owner values from finite repaired histories. Independent fresh replay
passes 137 audits and eleven semantic model mutants. Native containers,
compiler/bounds and complete CSSOM registration/publication remain admitted.
The checker has a documented lexical output-path limitation; accepted replays
used canonical external paths. No isolated-upstream or release runtime claim.

[Acceptance](../css-custom-properties-map-iterator-root-v1/ROOT-SCOPED-ACCEPTANCE.json).

## Fix 76: preserve taint when equal custom-property payloads are replaced

Native + WPT: `e04d672a735edcf0e6529c854207b5ee9555ea7c`, after independent acceptance
`01c98e4fd49ed6061c1a7ebdd87c124cd2b77254`, proof `7466d4284b1e946050a4d649ceab9a6944ee1ce6`
and paired runtime `017ddb9cb213e3870afca39af6f37dac5db9937f`. The three-file repair
checks taint in shared-map insertion and the universal cascade shortcut, with a
nine-case WPT. Global payload equality is unchanged.

Four final image-result failures become passes; all 82 local checks pass in nine
harnesses. The exact patch applies to the recorded upstream base. Unrelated
cascade work is excluded; no isolated upstream runtime is claimed.

Thirty-one conditional Lean results and four compiled semantic mutants passed
root and independent fresh replay. Both shortcuts must preserve metadata: either
old shortcut can mask repair of the other. Native payload/URL-data quotient,
state-dependent eligibility, reference-free provider, byte ranges and complete
map/caller refinement remain open. Source investigation and browser reproduction
preceded this formalization.

[Acceptance](../css-custom-properties-map-taint-acceptance-v1/ACCEPTANCE.json) and
[commit check](../css-custom-properties-map-taint-root-v1/ROOT-COMMIT-CHECK.json).

The range candidate below is now committed. Equal-payload keyframe replacement
remains separate: two failures with four controls passing, not counted above.

## Fix 77: use half-open byte ranges for attribute-tainted URLs

Native + WPT: `8c04b6787e36c9ee42fec440103cf33372c097f1`, following proof/runtime companion
`91e709f931abf5ef2d59a77158f66662500bd2ff`. The two-file commit changes one overlap expression
and adds a seven-case WPT. Min/max intersection rejects touching and empty spans
while preserving genuinely shared bytes and existing whole-substitution taint.

Two final URL-adjacency failures become passes; all 89 local checks pass in ten
harnesses. Baseline is the joined validated 82-case run and seven-case diagnostic
on identical binaries. Independent runtime/source/dependency review and exact
upstream patch apply/reverse passed. No isolated upstream runtime is claimed.

Fourteen Lean results characterize overlap by existence of a shared byte and
compose finite taint lists. Extracted original/candidate methods yield 146/0
mismatches across 441 pairs; an independent strict-pairwise mutation leaves 40
mismatches. Range producers, URL parser positions, SmallVec/compiler and full
native behavior remain outside the proved helper contract.

Discovery came from reviewing the source-shaped range observer used in the taint
proof, followed by source investigation and browser reproduction.
[Acceptance](../css-attr-taint-touching-ranges-final-root-v1/ACCEPTANCE.json) and
[commit check](../css-attr-taint-touching-ranges-final-root-v1/ROOT-COMMIT-CHECK.json).

## Fix 78: retain attribute taint when replacing animation endpoints

Stack native + WPT: `4b4a00e707583382f4773039f13a4f335f48f41a`; preceding
proof/runtime/review companion: `922272780824ee77c05f96972c7bb51a95de7ead`.
The four-file stack commit depends on fix76's shared-map insertion check.

For independent landing, use `f1a3f777395b157a2c098dae1b3f2ad29fa5c642` on
`stylo-css-animation-endpoint-taint-fix`, preceded by evidence commit
`5ebe0eff84805264edd6696356e29b8123f7a895`. It includes that one necessary map
prerequisite, three endpoint source files and the six-case CSS-wide WPT.
Both variants apply/reverse exactly; isolated upstream runtime was not run.

Four equal-payload replacement failures become passes; all 101 matrix cases and
80 existing setKeyframes cases pass. The CSS-wide test avoids the earlier typed
keyframe provider repair. Format/lint pass with one warning; one checked C++
line-wrap is the sole difference from compiled/proof-bound source.

The bounded Lean component passes 25 audits and two compiled endpoint-omission
mutants. It derives safe shape and preserves metadata through finite modeled
replacement histories. Native providers, publication, scheduler and full URL
semantics remain admitted. Source investigation/browser reproduction preceded
formalization. A separate base-style scheduling probe has four reproduced
failures and is under independent review; it is not included in this fix.

[Acceptance](../css-animation-endpoint-final-root-v1/ACCEPTANCE.json),
[commit verification](../css-animation-endpoint-final-root-v1/ROOT-COMMIT-CHECK.json),
[standalone verification](../css-animation-endpoint-final-root-v1/ROOT-STANDALONE-CHECK.json).

## Fix 79: restyle animations when underlying attribute taint changes

Native + WPT: `2c09cb2e4ff81bbc4af65d1d069517420b9c1529`; preceding
proof/runtime/review companion: `91d47c020cb9c4855e0e35ad51012d2ccf2aeac9`.
The two-file stack patch adds metadata comparison to EnsureBaseStyles and an
eight-case WPT. It reuses the accessor from fix 78.

Standalone native + WPT: `1181f7b5751c2a98ad08f28a7b63f30036b53ae7`, on
`stylo-css-animation-base-taint-fix`, preceded by evidence commit
`1a6b758e40e1276b510086ba23e7777c0ee37b5f`. Its four files include the getter
and FFI but need no endpoint-loop or map repair. The standalone alternatives
for fixes 78 and 79 share accessors; use the stack patch when they already exist.
Exact upstream apply/reverse and committed blobs were verified; an isolated
upstream build/browser run was not performed.

Fresh baseline: four failures and four passes. The joined reference of 189
checks becomes 189 passes across 14 successful harnesses: four improvements,
185 unchanged. Reads after control flushes but before seeking preserve the
failure, distinguishing control flushing from the resample that recovers it.
The older attr-security suite includes conditional assertions; its passing
entries are not all unconditional coverage.

The formal component has 23 new audits, 14 source bindings and a compiled
metadata-omission mutant. Root fresh replay and independent seven kernel
challenges/six integrity negatives pass. It establishes metadata-change
recognition and the modeled restyle-call decision. Native provider/key
alignment, delivered scheduling, publication and complete URL observations
remain assumptions. Source investigation and browser reproduction preceded
formalization.

[Acceptance](../css-animation-base-metadata-final-root-v1/ACCEPTANCE.json),
[commit verification](../css-animation-base-metadata-final-root-v1/ROOT-COMMIT-CHECK.json),
[standalone verification](../css-animation-base-metadata-final-root-v1/ROOT-STANDALONE-CHECK.json).

## Fix 80: preserve both interpolation operands' attribute taint

Native + WPT: `ede7ceb101d83f0c4044585a5a687f5286b072c9`; preceding proof/runtime/review
companion: `a9b8e799ce9785008c72d63b6539305284cbf9ef`. The patch contains one Rust line in
Value<Component>::animate and a 24-case WPT. Successful combinations union both
operands' provenance; the existing payload operation, failure path and first
operand's URL data remain unchanged.

Standalone native + WPT: `ed3ad9b8e4ea95d36731e08311c6bb04f904071b`, on
`stylo-css-interpolation-taint-fix`, preceded by evidence
`7b51b4de426f54184f155e515d0f1cd65de23eec`. Both stack and upstream variants contain
exactly two files and require no earlier map, accessor or retention repair.
Exact source apply/reverse, parent chains and all committed blobs were checked.
An isolated upstream build/browser run was not performed.

The focused baseline has 22 passes and two failures. The joined reference has
248 passes and five failures; the candidate has 253 passes across 16 successful
harnesses. Five assertions improve and 248 statuses are unchanged. The final
WPT only corrects a help-link fragment after the paired run. Two diagnostic
boundary cases allow either taint polarity; older conditional tests retain
that limitation. These failures represent one defect.

Root and independent fresh formal replay pass 15 audits and 45 extracted-native
observations per variant. The original implementation differs only on three
successful clean-first/tainted-second cases. The result covers wrapper metadata
union and finite admitted pure compositions; numerical providers, complete URL
semantics and native scheduler histories remain assumptions. Zero-weight taint
policy is not promoted to a new normative assertion. Source/spec investigation
and browser reproduction preceded formalization.

[Acceptance](../css-animation-interpolation-taint-final-root-v1/ACCEPTANCE.json),
[commit check](../css-animation-interpolation-taint-final-root-v1/ROOT-COMMIT-CHECK.json),
[standalone check](../css-animation-interpolation-taint-final-root-v1/ROOT-STANDALONE-CHECK.json).

## Attribute-taint release request follow-up

Fix 80 (`ede7ceb101d83f0c4044585a5a687f5286b072c9`; standalone
`ed3ad9b8e4ea95d36731e08311c6bb04f904071b`) now has script-free release
Firefox 158 evidence of actual requests from URL uses that should be taint-blocked.
Four forbidden loopback requests disappear in the patched shared build; ten
controls remain. This adds release/network evidence, not a new fix. Arbitrary
unknown-byte extraction and incremental disclosure remain unproved; permitted
static density selection exposes the same tested numeric distinction. No
isolated-fix binary comparison or external destination was used.

[Security review](../css-attr-taint-security-review-v1/REPORT.md) and
[root evidence check](../css-attr-taint-security-root-v1/REVIEW.json).

## Fix 82: preserve guaranteed-invalid animated custom properties

Native + WPT: `d63735091bf8dc469d900ddba56e8a43bcac26d7`; preceding
proof/runtime/review companion: `5e540197f9afb45e30d0f5714ffbf716115da302`.

The bounded v2 proof and independent review are accepted: 81 audits (42 new),
29 source bindings, five Lean mutants, three Rust mutants and 14 independent
boundary theorems. Native/WPT review, build, 22-case final WPT and standalone
source packaging pass. The 343-check joined comparison repairs ten failures;
333 outcomes remain unchanged, including two expected failures. Six final WPT
controls have candidate-only evidence. See
[acceptance](../css-animation-invalid-publication-final-v1/ACCEPTANCE.json) and
[commit plan](../css-animation-invalid-publication-final-v1/COMMIT-PLAN.json).

There are 82 committed native fixes. Configured signing remains enabled.

## Fix 81: preserve registered custom property token boundaries

Native + WPT: `34e4e755cb81332819e56457f5fb68b9b305c394`; preceding
proof/runtime/review companion: `76d4707974532db89589ffa39f2728db46527114`.
The 37-case WPT changes ten failures to passes; the wider run has 308 passes.
The bounded proof has 22 audited results, 24 actual-parser cases and four
compiled mutants. Parser-event projection, balanced serialization and downstream
concatenation remain explicit assumptions. The two-file patch has an independently
applicable upstream alternative, with no isolated upstream runtime claim.
[Acceptance](../css-registered-token-boundary-final-v1/ACCEPTANCE.json).

## Fixes 83–85: constructor origin and terminal whitespace

Fix83 normalizes the leading token before recording reference offsets. A minimal
script-free input crashes a content process in installed Firefox 158; the patched
build passes all 26 new cases. This establishes a bounds panic, not memory
corruption. The origin proof has 88 audits and four compiled native mutants with
explicit tokenizer, provider, machine and caller-protocol assumptions.

Fix84 keeps trailing token metadata aligned with stored bytes: 28 failing cases
become passes and all 40 new cases pass. Fix85 removes only an outer whitespace
token's exact raw span, preserving escaped space/tab inside identifiers: 16
failures become passes and all 20 new cases pass. The shared bounded proof has
37 audits, 23 independent challenges and explicit token/EOF provider premises.
It does not prove general serialization; the backslash/newline counterexample
led to the next candidate. The final 435-check run preserves all 415 prior
outcomes, including two expected failures.

## View-transition invalidation review correction accepted

Independent review v2 removes the generated cache from its copied producer capsule, independently checks the nested closed roster, and passes a fresh full replay and 19 negative controls. Root authenticated the seals, reran the review checker, and verified unchanged challenge sources against its previous successful compilation. The 39 audits, 15,234 cases, and 51,702 snapshots retain their conditional scope. Native evidence remains six failures to 42 passes. The repair is accepted pending its separate signed native/WPT commit. See `artifacts/css-view-transition-type-invalidation-proof-root-v1/ACCEPTANCE.json`.

## Explicit sticky inset encoding accepted

The independent native/WPT review and corrected formal companion are accepted. Root replay confirms 31 audited results, 236 cases, six native configurations, five paired semantic mutations, 11 provider negatives, 33 integrity controls and two axiom controls. The proof retains explicit numeric/anchor/provider and C++ interpretation assumptions. The two-file patch and 80-case WPT remain separate from the preceding evidence/tooling; no commit ID exists yet. See [root acceptance](../css-sticky-offset-alias-proof-root-v3/ACCEPTANCE.json).

The latest requested signing retry failed with the 1Password buffer error. HEAD and all 297 staged evidence files were reauthenticated unchanged. Signing remains enabled.

## Sticky auto-inset and logical-end repairs accepted

H1 and H2 now have root acceptance of the full scoped formal companion, following their existing independent native/WPT reviews. The new proof checks both coordinates executed by the range/displacement callers. Root replay passes 191 audits and all35 integrity/comparator controls; nine independent kernel checks and twelve extracted-native continuation cases pass their expected outcomes. The original domain witnesses remain excluded explicitly. See [root acceptance](../css-sticky-insets-proof-root-v3/ACCEPTANCE.json). Each repair retains its own two-file Gecko/WPT patch; signed commit IDs remain pending.

The negative-inset arithmetic candidate has independent native/WPT acceptance but remains outside the accepted-fix count until its complete formal companion is reviewed. Root removed23.2MB of completed H1/H2 compiler products, preserving sources and receipts.

## Review pending: flex baseline cross-size sum

The separate two-file [candidate patch](../css-flex-cross-baseline-overflow-fix-v1/fix-candidate-v2.patch) repairs a signed arithmetic overflow that makes a 100px-max-height flex container collapse to zero. The 54-case WPT changes 12 failures to passes; 42 controls remain unchanged. All 29 regression files pass. Installed Firefox 158 reproduces the defect. Primitive Lean results and extracted-native UBSan evidence accompany the patch; independent review is pending. No commit ID or accepted-fix count is assigned yet.

## Safe-scroll candidate and retained collapsed-frame overflow

Counts remain **87 committed fixes and 4 accepted pending**. Signing retry still fails in 1Password; HEAD and the authenticated297-file staged checkpoint are unchanged.

The own-scroller safe-flex repair is now a sealed native/WPT candidate:484 failures become passes across640cases, with156unchanged controls. A paired72-case ownership probe changes only four body-owned safe cases;14regression files pass798subtests and10reftests. The exact two-file patch is independent of other pending flex changes. Ten preliminary reachability lemmas pass, but complete formal/source joins and independent review remain open. See [candidate](../css-flex-safe-scroll-origin-fix-v1/REPORT.md).

Full F11 review found another observable retained-frame defect: a collapsed240px child with border/margin/descendants can enlarge a100px flex scrollport. Release and repaired builds have24identical observations, including12collapsed overflow cases. The plainzero-width control passes. Earlier420controls used shorter items and did not refute this case; their broad no-overflow conclusion is superseded. A kernel/source-extraction counterexample now preserves the full domain; a separate145-case WPT baseline is running. See [discovery](../css-flex-collapsed-tall-strut-root-v1/REPORT.md).

The negative-inset v2 complete conditional companion passed a fresh root replay:219audits,544Lean rows,2164genuine native observations,9semantic mutants and the retained clamp-UB exclusion. Independent review is active. Geometric-sentinel v3 is also sealed, with167audits and the formerly missing indexed/machine joins; independent review remains pending. No acceptance is inferred from successful replay alone.

Next: finish the collapsed-overflow repair and paired WPT; address the baseline-sum WPT numeric-range portability review; complete independent sticky reviews; build the safe-scroll source/consumer companion without narrowing its contract.

## Historical checkpoint: six repairs pending signing

Counts: **87 committed fixes, 6 accepted pending**. The opposing-negative-inset repair now has accepted full conditional source/caller proof and native/WPT review. Root's219-audit replay,2,164genuine native observations and12fresh independent kernel checks are sealed in [root acceptance](../css-sticky-negative-inset-overflow-proof-root-v2/REPORT.md). Its original preexisting clamp-UB exclusion remains explicit.

The baseline cross-size sum repair also passes final review after a portability correction: the WPT explicitly marks unsupported extreme numeric ranges optional while retaining its unconditional100px oracle on admitted inputs. All54Gecko inputs are admitted;12failures become passes and42controls are unchanged. The native body/patch is identical to the accepted v1 arithmetic change. See [corrected package](../css-flex-cross-baseline-overflow-fix-v2/REPORT.md).

The new collapsed-frame overflow repair passes145paired cases (93improvements) and34regression files (29reftests,757subtests), plus build and lint. It retains a separate two-file patch; independent native review and full F11/F12 composition remain open. See [candidate](../css-flex-collapsed-scroll-overflow-fix-v1/REPORT.md). The safe-scroll candidate is undergoing independent native review and full formal-scope planning.

Geometric-sentinel v3 passed a fresh root replay with all30raw streams identical to canonical/relocated evidence. Root inspected indexed and machine joins; final sequential update/source review and independent challenges remain open. No acceptance promotion yet. Completed root proof/native products were cleaned:20.3MB for negative insets and2.47MB for the sentinel replay; the main Firefox build remains available with every repair restored.

Next priorities: finish collapsed-overflow and safe-scroll reviews; complete the original retained-frame/machine contracts; finish sentinel v3 review; prepare preceding evidence/formal commits for the two newly accepted fixes. Signed commits remain blocked by1Password; no new retry until user readiness.

## Prepared queues and native review decisions

Counts remain **87 committed fixes and 6 accepted pending**. The latest requested signing attempt failed with the same 1Password buffer error; HEAD and all 297 staged evidence files remain unchanged.

The [negative-inset queue](../css-sticky-negative-inset-overflow-commit-v1/QUEUE.json) and [baseline-sum queue](../css-flex-cross-baseline-overflow-commit-v1/QUEUE.json) are prepared. Each has preceding evidence/formal commits and a separate Gecko/WPT commit. Temporary-index checks verify both retained bases, the complete queued native order, exact three-file/two-file deltas, and inverse application. The negative-inset integration preserves earlier normalized-inset and logical-end fixes; its original standalone patch remains available. No production source, browser build, or real index was changed by packaging.

Independent native/WPT reviews now accept both [safe-scroll](../css-flex-safe-scroll-origin-review-v1/REPORT.md) and [collapsed-item overflow](../css-flex-collapsed-scroll-overflow-review-v1/REPORT.md). Root authenticated the sealed reviews and adopted their native decisions. Their full formal companions remain open, so neither increments the accepted-pending count yet.

Active work: implement the complete twelve-obligation safe-scroll source/consumer proof; finish collapsed allocation's F11/F12 joins with the separately accepted baseline-sum prerequisite; independently review sentinel v3's indexed lifecycle, machine arithmetic and sequential update joins. Producer self-review is not counted as independent review. The shared browser build remains restored with all repairs.

## Latest checkpoint: seven accepted repairs awaiting signed commits

Counts: **87 committed native/WPT fixes; 7 accepted pending**. The geometric
sticky-sentinel repair now has [root acceptance](../css-sticky-sentinel-proof-root-v3/ACCEPTANCE.json)
after independent v3 review: 167 producer audits, 10 independent kernel checks
and identical canonical, relocated and root replay streams. The original
conditional positional-consumer contract includes indexed sequential updates
and both-coordinate machine operations. Geometry/provider freshness, upstream
limit construction, compiler correspondence and actual overflow delivery remain
explicit premises; range/timeline consumers are separate.

The multiline flex cross-size sum candidate passes all 144 paired WPT cases
against 96 failures and 48 passes. Its regression run has 914 passing subtests,
20 passing reftests, six OK harnesses and one known-intermittent failure in
`content-height-with-scrollbars.html`; that file has no paired baseline result.
Build, scoped formatting and WPT lint pass. Independent review remains open,
so this candidate is excluded from the accepted count. Earlier per-item sums
and downstream packing arithmetic remain separate obligations.
[Candidate report](../css-flex-line-cross-sum-fix-v1/REPORT.md).

Collapsed-allocation v2 is a sealed producer checkpoint with 419 audits and 91
native cases; root adoption is pending. Full F11/F12 still have provider and
row-strut edge-policy gaps. Work continues in v3 without narrowing those targets.
The full twelve-obligation safe-scroll companion remains in progress.

The latest user-requested signing retry failed with `1Password: failed to fill whole buffer` (exit 128). HEAD remains `92a6fddf18e5828b17d7491a34663a0d5a9c12ad`; all 297 staged paths and content hashes still match the prepared recipe. Signing remains enabled.

## Latest checkpoint: eight accepted repairs; two new reproduced leads

Counts: **87 committed native/WPT fixes; 8 accepted pending signing**. The wrapped
line-size sum repair now has [root acceptance](../css-flex-line-cross-sum-root-v1/ACCEPTANCE.json):
21 freshly checked kernel results and three negative/axiom controls, plus root
recounting of all 144 paired WPT results and both standalone patch round trips.
The one metadata-known intermittent regression remains explicit. Both this fix
and the geometric sticky fix now have complete preceding evidence/formal and
separate two-file native commit recipes. The staged signing snapshot is intact.

Two distinct leads now reproduce identically in release and the shared build:

- [Cross-axis packing arithmetic](../css-flex-cross-packing-boundary-probe-v1/REPORT.md):
  ten failures among 48 calibrated rows. Safe alignment moves the first item far
  from its expected start when large lines or gaps overflow the packing budget.
  A 64-row follow-up preserves reverse-wrap controls; simple early lower clamping
  would break already-defined cancellation. The complete wide-coordinate path
  is under design review; no native repair has been applied.
- [Natural-baseline donor selection](../css-flex-natural-baseline-donor-probe-v1/REPORT.md):
  eight failures among 24 rows, all removal/restoration and geometry controls
  passing. An ordinary 160x80px flex box shifts 34px when an empty 5px item masks
  a natural text baseline. This is separate from collapsed-item donor exclusion
  and the unresolved strut-only edge-line specification question.

Collapsed-allocation v2's 147 source inputs and 234 receipt files are authenticated
as a producer checkpoint. Full F11/F12 remain open; v3 continues the original
sixteen obligations. The safe-scroll proof retains all twelve obligations and
keeps the newly reproduced packing failure separate from its policy repair.
Next: implement and verify natural donor selection, finish the complete packing
arithmetic design, and continue the full consumer/provider proofs. The signer
remains unavailable; no further retry was attempted without new readiness.

## Checkpoint: relative baseline formal acceptance

Counts: **87 committed native/WPT fixes; nine accepted pending signing**.
The relative-position baseline companion is accepted under its explicit provider,
property-lifetime and numeric premises. [Its commit queue](../css-flex-relative-baseline-commit-v1/QUEUE.json)
contains separate evidence, review and formal companions followed by the two-file
Gecko/WPT patch. Completed root compiler products (3,787,976 bytes) were removed.

Next: finish the scroll-provider source/theorem review and natural-donor prerequisite
resolution; complete packing v2 arithmetic across fragment coordinates, metrics
and cumulative storage. Full safe-scroll twelve-obligation and collapsed-allocation
sixteen-obligation work continues. The latest requested signing retry failed;
HEAD and the 297 staged evidence files remain unchanged.

## Checkpoint: scroll-provider formal acceptance

Counts: **87 committed native/WPT fixes; ten accepted pending signing**.
[Root acceptance](../css-scroll-baseline-provider-proof-root-v2/ACCEPTANCE.json)
covers the complete conditional scroll-provider method, including early legacy
synthesis, containment, absence, coordinate conversion, clamp and numeric bounds.
Its [commit queue](../css-scroll-baseline-provider-commit-v1/QUEUE.json) preserves
separate evidence/review/formal companions and one two-file native/WPT fix.
Completed root compiler outputs (5,015,200 bytes) were removed.

Next: finish packing v2 correlated fragment bounds and storage design, then
implement and replay the full regression/verification gates. The native consumed-size
provider uses unchecked signed32 accumulation; its actual range is an explicit
caller obligation, not an assumed saturating helper. The natural-donor patch
remains withdrawn until its semantic prerequisite and independent-landability
requirement are resolved. Full safe-scroll and allocation milestones continue.
Signing remains blocked, with the original297 staged snapshot intact.

### Open lead: oversized final fragment after forced flex breaks

No commit or accepted-fix count yet. The [reduction and source evidence](../css-fragment-forced-break-probe-v2/REPORT.md)
show eight failures among24 release/shared cases:80px flex items are placed
correctly, but an oversized final container fragment pushes a following sibling
into an extra column. The WPT reproduces16PASS/8FAIL. This requires extreme
fragment heights; no security impact is established. Consumed-size and flex
cumulative arithmetic need a joined source repair. It may overlap the existing
packingv2 candidate and must not be double-counted before that boundary is known.

The forced-break lead now has an [actual reflow trace](../css-flex-fragment-consumed-trace-v2/REPORT.md)
confirming the negative-counter/zero-growth/oversized-output route. The source
and build were restored after diagnosis. Its fix boundary and complete proof
remain open; accepted and committed counts are unchanged.

### Publication proof review checkpoint

[Independent replay and source review](../css-flex-publication-root-review-v1/REPORT.md)
passed60-module compilation and74 combined publication/root theorem audits. It
identified a missing equality between requested cache fields and actual child
reflow-input fields; lifecycle work now treats them separately. This adds no
accepted bug or native commit. Counts remain87 committed fixes and ten accepted
pending signing. Completed root compiler outputs (31,422,768bytes) were removed.

### Forced-break regression coverage and repair scope

The [expanded144-case WPT](../css-flex-fragment-writing-mode-probe-v1/REPORT.md)
reproduces48 failures in both release and the project build across writing modes
and directions, preserving96 controls. A [runtime provider trace](../css-flex-consumed-caller-trace-v1/REPORT.md)
confirms overflow in the block ancestor as well as the flex container. The fix
therefore needs shared-provider handling in addition to exact flex cancellation.
A source prototype is in progress; no additional accepted bug or commit is counted.
All diagnostic source/build changes were restored.

## Checkpoint: percentage-padding measurement cache

The F11 freshness audit yielded a new ordinary-size browser failure: changing
a flex item’s percentage padding leaves its baseline alignment one update behind.
Release and project builds agree on four discrepancies among eighteen cases;
the new WPT reproduces fourteen passes and four failures. A focused cache-key
repair built successfully; candidate tests and a separate Lean companion are
in progress. See [repair evidence](../css-flex-padding-measurement-cache-fix-v1/REPORT.md).
Counts remain87 committed and ten accepted pending signing; seven unaccepted
candidates/leads are now tracked. Full twelve/sixteen-obligation work continues.

The latest user-requested signing retry failed with the same 1Password error;
HEAD and all297 staged file hashes remain unchanged. All36 queued recipes
passed preflight checks of15,335 file pins. No unsigned commit was attempted.

## Checkpoint: percentage-padding cache repair accepted

Counts: **87 committed native/WPT fixes; 11 accepted pending signing; six
unaccepted candidates/leads**. The new ordinary-size baseline repair adds actual
logical border/padding to the measuring cache key. Paired WPT results change
from 14 PASS / 4 FAIL to 18 PASS; the final formatted build passes 20 subtests
and seven reftests. The two-file patch applies independently to HEAD and the
retained upstream base. No isolated upstream runtime is claimed.

[Root acceptance](../css-flex-padding-key-root-review-v1/ACCEPTANCE.json) follows
independent native/WPT review and a fresh scoped Lean/native replay. The
[commit queue](../css-flex-padding-key-commit-v1/QUEUE.json) places evidence and
formal companions before the separate Gecko/WPT commit. Root removed 1,000,832
bytes of completed compiler products; the shared browser build remains.

The broader safe-scroll review found missing joins from actual child reflow
output sizes and from mixed-axis/definite-single construction. Its twelve
obligations remain open, with corrections proceeding in a new version. The
allocation sixteen-obligation effort also remains open; this cache-key fix
does not establish universal provider freshness. Next: build the sealed exact
fragment prototype, preserve all packing/fragmentation gates, and continue
those source/provider joins. Signing is still blocked; the staged snapshot
remains intact.

The expanded queue passes all 39 recipe checks and all 11 native patch
apply/reverse steps in a disposable index. HEAD and every hash in the real
297-file staged snapshot are unchanged.

## Checkpoint: exact fragment prototype clears observed regression

The first exact-fragment integration fixed final-size failures but introduced
24 vertical-rl item-position failures. A [revised local experiment](../css-flex-fragment-exact-build-v2/REPORT.md)
lower-bounds the temporary border-box block size at zero while preserving exact
cumulative arithmetic. All 634 core observations now pass, including all 144
forced-break cases. Across 48 files, the run passes 2,404 subtests and 27 reftests,
with 21 OK harnesses. Candidate and restoration builds succeed with zero compiler
warnings; the known mach monitor exception remains recorded. Original source,
shared browser build, HEAD and staged index are restored.

This is not native acceptance. Root freshly replayed the [physical review](../css-flex-fragment-physical-composition-review-v1/REPORT.md),
which keeps actual callback geometry, both-coordinate intermediate bounds,
relative/sticky offsets, finite sentinel handling, overflow containers and
placeholder/abspos observers open. Dedicated shifted-item and fragmentation
controls are next, alongside the full original packing/provider/cache obligations.
The existing abspos controls do not establish fragmented placeholder correctness.

The [independent safe-scroll review](../css-flex-safe-scroll-origin-proof-independent-v2/REPORT.md)
replays 49 modules and 386 exact axiom audits but holds full F1–F12 composition:
actual returned/current frame sizes must reach the observer, constructor and
mixed-axis branches need coverage, and the machine suffix must use the same
producer path. Corrective v3 work continues. Allocation's original sixteen
obligations remain open, including callback/dirty/cache coherence; protocol
counterexamples are not counted as browser bugs.

Counts remain **87 committed fixes; 11 accepted pending signing; six unaccepted
candidates/leads**. The latest explicitly requested signed retry again failed in
1Password; all 297 staged paths and hashes remain unchanged. No retry was made
during the fragment experiment. No unsigned commits or pushes occurred.

### Relative-position preservation and branch-calibration follow-up

The [paired relative-offset experiment](../css-flex-fragment-exact-build-v3/REPORT.md)
passes all 1,296 candidate observations: 144 baseline flow failures become passes,
and all 432 item-position plus 432 restoration controls remain passing. The full
candidate run covers 49 files with 3,700 passing subtests, 27 passing reftests and
22 OK harnesses. Both builds succeed; original source/build and staged snapshot
are restored. This adds relative-offset evidence without closing universal
physical arithmetic or the full fragmentation scope.

Two separate branch probes exposed an invalid test assumption: nested tiny
children did not each enter a new column, for either `always` or `column` break
values, including small controls. All release/project raw results match. The
[abspos](../css-abspos-fragment-cumulative-probe-v2/REPORT.md) and
[overflow-container](../css-flex-overflow-container-probe-v2/REPORT.md) capsules
retain those negative calibrations. They establish neither a new bug nor execution
of the intended overflow path. Next: trace the native fragmentation-state guards
and use a calibrated construction or tall unforced content. A separate abspos
cumulative signed32 source lead remains unconfirmed at runtime.

Allocation now has a 73-module producer checkpoint with clean-cache coherence
and whole-memory callback publication, while actual callback trace/getter/lifetime
and full F11/F12 obligations remain open. The agent removed 71,197,664 bytes of
superseded compiler products, retaining active dependencies. Counts are unchanged:
87 committed fixes, 11 accepted pending signing, six unaccepted candidates/leads.

### New ordinary-size overflow-container lead

Tall-content probes now reach a useful fragmentation shape. The
[16-row overflow-container probe](../css-flex-overflow-container-probe-v3/REPORT.md)
returns identical release/project observations: all eight horizontal controls
pass, while eight vertical-rl cases differ, including four with ordinary 160px
columns. Descendants are displaced by 160–560px in the small cases. Reference
geometry and restoration pass. The source's tentative versus final width accounts
for the small-case displacement; independent source/spec review and a standalone
repair/WPT are in progress. No fix is accepted yet.

The [48-row abspos probe](../css-abspos-fragment-cumulative-probe-v3/REPORT.md)
preserves all child rectangles but produces one extra fragment in twelve large
spanning cases. Attribution between shared consumed-size and distinct abspos
cumulative arithmetic remains open, so this is not yet counted separately from
the fragmentation lead. Earlier failed forced-break calibrations remain retained.

The [32-row actual-provider probe](../css-flex-actual-provider-probe-v1/REPORT.md)
disconfirms the predicted table residual-placement error in the repaired build.
The source audit must explain why the table's used size is already accounted for;
it must not assume flex basis equals actual output. Release's eight reverse-safe
failures match the previously known safe-origin issue, with 24 unchanged controls.

Counts: **87 committed fixes; 11 accepted pending signing; seven unaccepted
candidates/leads**. Source/build remain restored and all browser profiles are
removed. No new signer attempt, commit or push occurred.

### Standalone overflow candidate and exact-size provider counterexample

The [standalone overflow-container candidate](../css-flex-overflow-container-fix-v1/REPORT.md)
passes all 336 paired WPT observations: 112 failures become passes and all 224
previous passes remain passing. Its two-file Gecko/WPT proposal applies and
reverses on retained HEAD independently of the wide cumulative arithmetic patch.
The [lifecycle diagnostic](../css-flex-overflow-lifecycle-runtime-v1/REPORT.md)
passes all eight candidate stages, correcting seven baseline failures through
normal/overflow transitions and continuation deletion/regrowth. No repair is
accepted on these results alone.

The [first branch trace](../css-flex-overflow-container-skip-trace-v1/REPORT.md)
contains 12 reflow visits and no skips. The [external resize trace](../css-flex-overflow-external-resize-trace-v1/REPORT.md)
then changes only an outer sibling's width. All eight candidate stages pass,
but all 24 eligible helper visits still reflow: exact frame identity joins show
column MarkSubtreeDirty reaching the flex parent, including 18 column children
that were clean before marking. This rules out that proposed clean-skip route;
it does not prove universal skip safety. Next are the remaining fragmentation
entry paths, source/formal ordering review, and focused regression gates.

The [24-row float round-trip probe](../css-flex-provider-roundtrip-runtime-v1/REPORT.md)
confirms a separate provider limitation. Fractional large reversed flex items
retain approximately 1 or 2 app units of origin residual even with the safe-origin
repair; explicit reversed flex-start controls show the same residual in release
and project builds. Integer controls are exact. This refutes the exact provider
join for those inputs and remains attached to the full safe-scroll F1–F12 work.
It is not yet an additional accepted spec bug. The goal remains exact containment;
a tolerance theorem does not close it. Next is preserving resolved app units
through sizing without changing aspect-ratio, table, fragment or min/max semantics.

Allocation's agent has sealed a 74-module ordinary callback checkpoint, with
actual source guards and native calibration; full F11/F12 remains open, especially
table ancestry, later special reflow, and cache freshness. Root review of this
new checkpoint remains pending. The agent removed 133,403,112 bytes of completed
compiler products while retaining active dependencies.

Counts remain **87 committed fixes; 11 accepted pending signing; seven unaccepted
candidates/leads**. The user-authorized signer retry v11 failed with the same
1Password error. All 39 prepared recipe inputs still match their pins; the exact
297-file staged snapshot and HEAD are unchanged. Both new native experiments
restored source and browser build; all temporary browser profiles are removed.
No unsigned commit, push, or new acceptance occurred.

## Overflow positioning acceptance and next validation (20 October)

**87 committed fixes; 12 accepted pending signing; seven unaccepted candidates/leads.**
The new accepted repair positions flex overflow-container children with the final
fragment size. Its 336-case WPT fixes 112 failures and preserves 224 passes;
34 existing regression file outcomes are unchanged (24 PASS, 10 expected FAIL).
Root replay, ordering review, actual-path formatting, WPT lint and final build
passed. The two-file native patch has separate preceding evidence and formal
recipes in [the queue](../css-flex-overflow-final-position-commit-v1/QUEUE.json).
The fix is installed in the local source and build.

[Root acceptance](../css-flex-overflow-root-review-v1/ACCEPTANCE.json) is bounded:
normalized list/continuation invariants remain source premises; universal clean
skip correctness, callback/geometry providers, wide arithmetic and full fragment
composition remain open. It does not accept the earlier wide packing prototype.

A separate initial relative-positioning defect is under paired native/WPT
validation. Fresh layout and a position-only update disagree at identical final
styles; independent ordinary horizontal controls reproduce it. The candidate
uses predecessor normal inline position and applies each continuation's own
relative offsets. Its 140-case WPT also tests nonzero-to-double and return-to-zero
updates. This candidate is not counted among accepted repairs yet.

The ordinary allocation component passed a fresh root 74-module replay, ten
audits, two semantic false claims, native cases and mutations. This closes a
conditional component only; full allocation F11/F12 remains open. The table
warm/fresh diagnostic passed all 24 cases in both browsers. Source inspection
explains why that probe changes its computed-size cache key; a caption variant
is ready to test a different path. The new table source checkpoint awaits root
review. See [ordinary root review](../css-flex-allocation-ordinary-root-v1/REPORT.md).
Completed root replay outputs were removed (36,110,328 bytes), with source,
commands, receipts and active build dependencies retained.

The latest requested signing retry (v12) failed with the same 1Password error.
HEAD and all 297 staged files remain pinned; no unsigned commit or push occurred.
Next: finish the relative-positioning browser pair and source/provider proof,
then review exact resolved-length transport and the table-caption cache probe.
Keep the original full verification requirements intact.

### New caption lead and relative-position candidate result

The separate relative-position candidate corrected **30 failures among 140 WPT subtests**
while preserving 110 passes. Thirty-five retained regression files were unchanged
(including all 336 final-size WPT subtests); both builds passed and source/build
were restored. RTL and non-flex caller regressions plus independent review are
running before acceptance. See [paired evidence](../css-overflow-relative-position-runtime-v1/REPORT.md).

The table-caption followup found **four discrepancies in 16 cases**, identical
in release and project browsers. Auto-height caption plus percentage table height
retains the old size after a containing flex height change; fixed-height caption
and literal table height controls pass. All initial, restoration and repeat
controls pass. This is a new unaccepted lead, with source/cache attribution and
repair pending: [evidence](../css-flex-table-caption-runtime-v1/REPORT.md).

Current counts: **87 committed; 12 accepted pending signing; eight unaccepted
candidates/leads.** All 42 prepared recipes were hash-checked, and all 12 accepted
native patches apply and reverse in order in a disposable index. The real staged
snapshot remains unchanged. The natural-donor queue remains blocked on its
semantic provider dependency; it is not part of the accepted stack.

## Accepted relative-position and table-caption repairs (20 October)

Current counts: **87 committed native/WPT fixes; 14 accepted pending signing;
six unaccepted candidates.** Each new repair has a separate two-file native/WPT
recipe preceded by evidence and formal commits:

- [Relative overflow positioning](../css-overflow-relative-position-commit-v1/QUEUE.json):
  30 failures corrected in the140-case standalone WPT; supplementary RTL suite
  corrects60 of280 cases, preserving prior passes. Existing35/61 file outcomes
  stay unchanged, with expected failures retained. Root fresh replay passes33
  kernel audits and source/native/mutant checks. The formatted patch changes only
  one tested argument-list line break. Full seven-part lifecycle scope stays open.
- [Captioned flex-table percentage height](../css-flex-table-caption-commit-v1/QUEUE.json):
  four failures corrected in16 WPT cases;354 other subtests pass, and sevenPASS/
  oneexpectedFAIL table reftest outcomes are unchanged. Root fresh replay passes19
  audits, four semantic falseclaims and384 native cases in15 runs. Actual
  containing-block size joins the measuring key. The two-stage stale-plan witness
  keeps fresh-provider assumptions explicit. Standalone upstream patch has no
  padding-key dependency; the queued stack patch has the same two additions and
  WPT with context reflecting the earlier padding-key repair.

Both passed independent native review, actual-path formatting and WPT lint.
The combined local install/build/four-WPT run is tracked in
[installed state](../css-overflow-caption-installed-v1/STATE.json); it restores
prior source/build on failure. No signed commit or push has occurred. The latest
signer retry remains v12, with HEAD and the297-file staged snapshot pinned.

The table observer component now has a fresh root manifest-only replay:23audits,
four semantic negatives,14bindings and646 native cases in3modes. It proves the
stated ancestry/scheduling/propagation component only. New root replay cleanup
removed1,401,112 bytes there and1,229,192 bytes for the caption key; source,
commands, raw output and active dependencies were retained. Producer caption
replays separately removed3,687,576 bytes of their owned terminal products.

Next: independently review exact app-unit override transport before full native
integration, then continue the actual cache-pointer/dirty-recovery lifetime join.
The exact-size prototype has seven files,30 kernel results and52 extracted checks;
its38-case WPT remains unexecuted. It preserves the existing coordinate cap and
costs16 additional bytes in the measured arm64 override bundle; full virtual-output,
fragment and ratio/min/max semantics remain review gates. No tolerance theorem
replaces the original exact safe-origin F1–F12 requirement. Full allocation
F1–F16/F11/F12 and full fragment observer composition remain open.

### Installed build checkpoint

The combined build completed successfully and all **510 subtests in four WPT
files passed**. Relative overflow positioning and captioned-table percentage
height are now installed alongside the earlier final-size and padding-key
repairs. [Integration evidence](../css-overflow-caption-installed-v1/REPORT.md)
pins the exact source/tests and binary. All14 accepted native patches applied
and reversed in order in a disposable index;48 recipes were checked. Signing
remains enabled, HEAD is unchanged, and the297 staged files still match their
original snapshot. Counts remain87 committed/14 accepted pending/six unaccepted.

## Historical local checkpoint

Counts remain **87 committed / 14 accepted pending signing / six unaccepted**.
Signing retryv13 failed; HEAD and the297-file staged snapshot remain unchanged.
The [exact-size transport experiment](../css-exact-size-transport-runtime-v1/REPORT.md)
corrected12 draft cases with retained regressions unchanged, but is not an
additional accepted bug or installed repair. Its source/build were restored.
The [recovery proof checkpoint](../css-flex-cache-recovery-root-v1/REPORT.md)
is a bounded component result; full cache lifetime remains open.
