# Local fix status

Latest checkpoint: computed-name research `19a313060adb` and presentation GTest `73a62b1ecf58` are signed locally. The transition descriptor prototype passes its before/after native tests; it adds no accepted browser bug. All 131 accepted fixes remain committed, with repair 120 held and excluded. See the current [plan of record](../stylo-bloom-tools/PLAN-OF-RECORD.md).


**131 accepted fixes: 131 committed locally, 0 accepted pending, and 1 additional held repair excluded.**

| Area | Committed | Accepted, pending |
|---|---:|---:|
| Selectors, Bloom filters and scoping | 10 | 0 |
| Cascade, layers and shorthands | 6 | 0 |
| Parsing, tokens and CSS math | 26 | 0 |
| Attributes and custom properties | 16 | 0 |
| Animations, timelines and transitions | 14 | 0 |
| Text and fonts | 13 | 0 |
| Layout, sizing and positioning | 22 | 0 |
| Container queries | 3 | 0 |
| Colors, images, SVG and shapes | 8 | 0 |
| CSSOM geometry and hidden layout | 13 | 0 |
| **Total** | **131** | **0** |

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

Endpoint source-index integration passed the full canonical checker after adding three missing helper audits. Fourteen existing theorem audits and eight executable cases are transferred implementation support, with no new proof-discovery or normative CSS coverage credit. Both indexes, all 147 staged research files, native sources and browser binaries are preserved. [Full check](../css-keyframe-endpoint-index-library-application-v1/REPORT.md).

Signing the next research commit failed in 1Password; no commit was created. The exact 147 research files remain staged, with the nested library index preserved. Signing will resume after the signer is available. [Attempt record](../css-pending-121-131-signing-execution-v1/STATUS.md).

The concrete animation-rule transport build and browser comparison passed. All 166 subtests retain their baseline outcomes (162 PASS and four known provider FAIL), and both crash tests pass. Source, binary, research and index preservation checks and owned-process cleanup pass. The transport remains installed for the next implementation step; this adds no accepted fix. [Comparison](../css-keyframe-animation-rule-sample-capture-runtime-v1/REPORT.md).

The authored-endpoint indexing model also passes independent source review and Lean replay: eight implementation lemmas, five positive examples and three decisive false controls. Native correspondence remains conditional; this adds no normative CSS coverage.

| Area | Committed | Accepted, pending |
|---|---:|---:|
| Selectors, Bloom filters and scoping | 10 | 0 |
| Cascade, layers and shorthands | 6 | 0 |
| Parsing, tokens and CSS math | 20 | 6 |
| Attributes and custom properties | 15 | 1 |
| Animations, timelines and transitions | 12 | 2 |
| Text and fonts | 13 | 0 |
| Layout, sizing and positioning | 20 | 2 |
| Container queries | 3 | 0 |
| Colors, images, SVG and shapes | 8 | 0 |
| CSSOM geometry and hidden layout | 13 | 0 |
| **Total** | **120** | **11** |

| Fix | Gecko/WPT commit | Preceding research |
|---|---|---|
| 117: counter-calculated-integer-sentinel | `33ae2e8349e96d1778603385d39cdb74b26a12df` | `2f1085d3c8ee068bb012a906b664b5e7a7450d05` |
| 118: css-integer-math-rounding | `d68543e601c40bf64d1777dfa6b7c79b838f21ae` | `1690a8cd5886ff68209dd3ea1dcbe97b9784d264` |
| 119: relative-length-nonfinite-intermediates | `6a363fc372c9cc0734faee64ab20f03bc762e97c` | `49862ae74751926b2c3600fe6cf1625e5b31c691` |

Six signed commits passed exact parent/path/blob checks and configured-key signature verification. Each of fixes 117–119 has one native/WPT commit, preceded by its research. The disjoint research selections add 65, 48 and 146 paths. Fix 118 reuses 40 exact files from the preceding fix 117 research commit; fix 119 retains its already-committed reviewer-log dependency. All working native bodies remain unchanged, including later edits sharing committed files. Main staging is empty; existing nested-library staging is preserved. Signing ran no new browser tests and does not establish clean-upstream independence.

The active-provider trace completed and the production sources/build are restored. Both captures reproduce six PASS and four calibrated FAIL. During the red-provider interval, the consumer uses cached 20/30 endpoints and produces 20/25/30; no recomputation records were observed in that retained interval. Native emitting PID and complete log delivery remain unproved. [Trace interpretation](../css-keyframe-active-provider-trace-interpretation-v1/REPORT.md).

The animation operation-arena test host builds and both native GTests pass, including 28 differential comparisons against production animation composition. Frozen Cargo resolution, the normal binaries build, the GTest host build and source/index preservation checks pass. This adds no accepted bug or native-refinement claim. Current-provider resolution and animated cycles remain open. [Execution record](../css-keyframe-operation-arena-host-runtime-v1/REPORT.md).

The canonical Lean library completed its full check with 11,805 audited declarations, 12,409 executable cases, 167 expected-false cases and 2,151 source fingerprints. Prefix-refresh integration is complete; copied proofs add no normative coverage. Current-provider context and a complete contributing prefix remain explicit model assumptions, not native refinement results.

Next: compile and test the production operation arena and authored-endpoint descriptors. Resume the prepared commit queue when 1Password signing is available. Winning-provider admission, animated cycles and descriptor memory reporting remain open; the implicit-underlying animated-provider oracle is inconclusive. Fix 120 and the normal-recascade performance candidate remain held.

[Individual fixes and commits](../stylo-bloom-tools/BUGFIX-COMMITS.md) · [Grouped ledger](GROUPS.json).
