# CSS and Stylo verification plan

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

The production operation arena, authored-endpoint descriptors and bulk differential supplement are applied across 21 source paths. Frozen Cargo metadata, export and binaries passed; GTest-host compilation is running in local session 62680. Ten selected native tests and the calibrated browser comparison remain pending. The 147 staged research files remain reserved for the signing retry. [Build record](../css-keyframe-operation-descriptor-runtime-v1/build-driver.log).

The computed-property-name model passes root source review and independent Lean replay: 25 audited statements, 12 examples, three decisive false controls and 18 negative-log gate checks. It preserves complete value/state results for embedded old expressions and threads cycle marks through name evaluation and fallback. Parsing remains an explicit normalized-token contract; no native correspondence or canonical coverage increment is claimed. Canonical integration is being prepared separately, with a native support audit and browser probes. The old/static versus modern/guarded fallback distinction was already covered and receives no duplicate credit. [Root review](../css-variables-computed-name-root-replay-v1/REPORT.md).

The next native owner/test proposal is reviewed but unapplied. Real presentation-backed descriptor tests are gated on a proposed windowless-browser calibration fixture. Memory accounting and valid Servo-only compile prerequisites remain open.

Endpoint source-index integration passed the full canonical checker after adding three missing helper audits. Fourteen existing theorem audits and eight executable cases are transferred implementation support, with no new proof-discovery or normative CSS coverage credit. Both indexes, all 147 staged research files, native sources and browser binaries are preserved. [Full check](../css-keyframe-endpoint-index-library-application-v1/REPORT.md).

The concrete animation-rule transport build and browser comparison passed. All 166 subtests retain their baseline outcomes (162 PASS and four known provider FAIL), and both crash tests pass. Source, binary, research and index preservation checks and owned-process cleanup pass. The transport remains installed for the next implementation step; this adds no accepted fix. [Comparison](../css-keyframe-animation-rule-sample-capture-runtime-v1/REPORT.md).

The authored-endpoint indexing model also passes independent source review and Lean replay: eight implementation lemmas, five positive examples and three decisive false controls. Native correspondence remains conditional; this adds no normative CSS coverage.

Six signed commits passed exact parent/path/blob checks and configured-key signature verification. Each of fixes 117–119 has one native/WPT commit, preceded by its research. The disjoint research selections add 65, 48 and 146 paths. Fix 118 reuses 40 exact files from the preceding fix 117 research commit; fix 119 retains its already-committed reviewer-log dependency. All working native bodies remain unchanged, including later edits sharing committed files. Staging was empty immediately after those commits; the later failed signing attempt now leaves 147 research files staged. Existing nested-library staging is preserved. Signing ran no new browser tests and does not establish clean-upstream independence.

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

Historical checkpoints follow; pending/running statements below are superseded by the current checkpoint.


Latest timing checkpoint: A/B/A attempt 55284 ended incomplete after four of six captures (original 2, candidate 1, restored 1). Both second-capture port preflights reported address-in-use before their browsers started. The original source was restored and rebuilt successfully; root verified all 835 main guards, 925 staged payloads, 31 installed identities, 53 clean phase roles and eight process groups absent. All 216 raw rows remain archived separately, with no performance acceptance. The failed ports/states were not recorded; later probes found them free. [Attempt and restoration](../css-keyframe-commit-styles-clean-cost-runtime-v1/REPORT.md).

A controlled ephemeral-socket test demonstrates that the old plain-bind preflight rejects TCP TIME_WAIT. The reviewed v3 probe uses TCP address reuse plus bind/listen, keeps UDP exclusive, rejects live listeners, and records the failing protocol/port/operation. This proves a tool defect, not the cause of attempt 55284. The fixture, parser and timing policy are unchanged. Next: a fresh complete six-capture comparison with v3; do not combine missing captures from separate attempts.

Latest clean-upstream checkpoint (2026-10-26): the standalone commitStyles candidate passes all 74 subtests and both crash tests on pristine base `976279105b2e78b8666a959eb3f25c9176cefaf8`. It repairs all 11 stale inline-value failures, preserving 59 upstream controls. Restoring and rebuilding the original source reproduces every baseline outcome exactly (63 PASS / 11 FAIL, two crash PASS). Both builds, root live preservation and terminal review pass. All 835 main guards, 925 staged payloads and 31 installed test identities remain intact. The isolated raw index changed with unknown cause; semantic indexes are preserved. Main raw index bytes remained equal. [Clean comparison](../css-keyframe-commit-styles-clean-comparison-terminal-review-v1/REPORT.md).

Next: measure commitStyles cost with original/candidate/restored captures at 1, 8 and 32 effects, using literal and variable cases and observing control drift. The disabled phase adapter is reviewed; its enclosing build/restoration owner is being prepared. Extra endpoint resolution can legitimately add cost; acceptance will consider absolute cost, scaling and controls rather than requiring zero overhead. A separate two-case implicit/additive-endpoint diagnostic passes static checks and lint but has not run in a browser. Accepted fix count remains 130; no new fix is accepted yet.

Current checkpoint: **130 accepted fixes, 105 committed and 25 pending; one additional repair held.** The one-function commitStyles refresh comparison completed: candidate 74 PASS plus two passing crash tests; restored 63 PASS / 11 FAIL, with every baseline outcome reproduced exactly. All 59 upstream subtests remain unchanged. Root verification 3794 and terminal review pass; original source/build restored and both research fixtures removed. Semantic staging is preserved. Raw Git index bytes changed during comparison for an unknown reason and were stable during root verification; this is not a claim of raw-byte preservation.

The refresh-coverage Lean companion passes root replay and review, conditional on a current provider context. The original custom-consumer regression file requires earlier fix 70. An ordinary margin-left consumer alternative avoids that identified source prerequisite; its 15-case baseline completed as session 70637 with 4 PASS / 11 FAIL, all at the intended stale inline snapshot assertion. The ordinary-consumer comparison completed as session 78529: all 74 subtests and both crash tests pass with the candidate; restoration reproduces every baseline outcome exactly. Root 9719 and terminal review pass, and the owned fixture is removed. The detached clean-base checkout configured successfully with matching tools, optimization and compiled tests, and debug symbols disabled. Its first full build (74985) stopped at the disk guard after a long monitoring gap, with source/config unchanged and its process group removed. Recovery 77478 succeeded with two jobs, one-second disk sampling and an AC-only wake assertion. Its build result records exit 0, no cleanup errors and no remaining owned process group; clean-base browser validation is next. The15GiB guard is sampled, not reserved space. The clean-base candidate/restoration comparison now passes as recorded above; prefix-refresh cost at 1, 8 and 32 effects remains to be measured before acceptance. The registered-invalid-endpoint diagnostic completed with six static/literal PASS and four calibrated dynamic history failures: numeric endpoints remain stale while the provider changes from 20 to red and back. Independent result review passes; fixture removal and root preservation checks are complete. Runner termination and semaphore shutdown warnings are retained explicitly. This extends the existing active-dependency investigation, without a new accepted fix. The cost parser now passes root replay with a binary64 subtraction-rounding bound replacing invalid exact duration addition; no browser timings have been captured. General active-dependency integration remains open. The earlier normal-only recascade candidate remains on performance hold; four retained browsers are still needed. Signed research retry 90874 failed in 1Password; staging remains intact. [Current grouped status](../css-fix-readout-20261023/STATUS.md).

The typed endpoint-defaulting Lean companion now passes independent root replay and source/evidence review: six theorem audits, eleven examples and four decisive false controls. It proves dependency congruence and selective refresh across finite provider-context histories, and reproduces the invalid-provider stale-cache case. The negative checker now rejects incomplete reduction and malformed/error logs; the qualified v1 evidence remains preserved. Native current-provider correspondence remains a premise, and canonical-library integration is not yet claimed. [Proof and limits](../css-keyframe-endpoint-defaulting-model-v1/REPORT.md), [corrected root replay](../css-keyframe-endpoint-defaulting-root-replay-v2/REPORT.md).

The clean baseline runner passes root review and thirteen inert checks. It binds the isolated binary/config/profile paths and build Python, records its process group, verifies the fresh 74-subtest/two-crash roster without an assumed failure count, and removes the owned fixture only after process cleanup. Recovery 77478 succeeded, but the v3 baseline attempt failed before valid tests: unrelated local servers occupy ports 8000 and 8003. The owned WPT group and fixture were removed; five generated source-tree manifests/caches remain recorded for exact cleanup. A retry will use unused ports and the generated object-directory WPT configuration. The v4 retry on unused ports completes the exact 74-subtest/two-crash roster: 63 PASS / 11 FAIL, including all 59 upstream controls and both crashes passing. All 11 failures are the intended stale inline snapshot assertions; the fixture and temporary server configuration are removed, with no cleanup errors. Root baseline review and the subsequent candidate/restoration comparison now pass. The clean-base runtime evidence is complete for this selected roster. [Prepared runner](../css-keyframe-commit-styles-clean-wpt-preparation-v3/README.md).

The token-list adapter passes root replay and independent review: seven audits, twelve examples and five decisive false controls. It reuses canonical variable/defaulting semantics and explicitly distinguishes missing substitution from present empty/multi-token values. The import package passes focused root replay and source review: 33 audits, 56 cases and 19 decisive false controls. Eight older standalone reduction-only failures are explicitly qualified and replaced by same-claim controls in the package. The rebased package is applied and the full canonical check passes: 11,785 audits, 12,392 cases, 2,147 source fingerprints and 161 expected-false cases. Root authenticated every reported source and command log. Read-only terminal verification and root review pass, preserving the prior audit/case prefixes, both indexes, unrelated sources and native diffs. Two wrapper verification mistakes are documented in the application evidence; neither changed canonical source or required a full-check rerun. [Applied package](../css-keyframe-animation-library-application-v1/REPORT.md). No normative coverage increment is claimed. [Adapter and limits](../css-keyframe-token-list-adapter-root-replay-v1/REPORT.md).

Root removed570 reviewed obsolete hyphenation .dSYM bundles (1710 files,11.398GiB allocated), preserving all570 sibling binaries and all referenced sources/results. Current native builds and the four retained performance browsers were excluded. Exact-path open-file/tracked/identity/body checks and a removal journal are retained. [Cleanup](../css-hyphenation-symbol-cleanup-runtime-v1/REPORT.md).

The canonical failure-classifier audit closes the concern about its142 false executable rows: all require successful execution and the exact12,336-row output; current2140source hashes and six command logs match. Two separate intentional type-error controls had valid retained evidence but permissive substring classification. Narrow hardening is now applied separately from the animation import: both gates require exit 1 and the exact complete diagnostic. Two positive and 32 negative inert checks pass; the other 2,139 source fingerprints, both indexes and the main native diff were preserved. The subsequent full canonical check passes both hardened controls. [Audit](../css-canonical-negative-control-audit-v1/REPORT.md).

Earlier checkpoints follow; their pending/running statements describe the state at those checkpoints.

Active dependent animations now have a calibrated six-case capture: the provider advances from 225 to 275 while dependent endpoints keep yielding 125/175. Repeated reads and creation/getter order do not repair the values; an unrelated normal style change repairs 125 to the expected 143.75. Both literal controls pass. Source, build, staging and fixture cleanup are preserved. This supports the active-sampling dependency boundary, with no new accepted fix. [Capture](../css-keyframe-acyclic-sampling-diagnostic-runtime-v2/REPORT.md).

The normal-only keyframe recascade comparison is complete and root-verified: 190 tests improve from 177 PASS/13 FAIL to 187 PASS/3 FAIL, all 22 targeted checks pass, and all 168 controls remain exact. Original sources and generated headers are restored and rebuilt; every baseline outcome returns exactly. All six timing captures complete, but restored controls slow substantially, so performance remains inconclusive and the candidate is unaccepted. The balanced comparison in `css-keyframe-normal-recascade-balanced-runtime-v1` ended with exit1 (session35990, terminal e7a1c1) before any timing capture: the copied B browser contained the sole extra `Contents/Resources/browser/.purgecaches` marker, one newline byte. Both exports/builds succeeded; all five source bodies and generated headers were restored. Root verification passed (94136/0803ed), preserving 791 roles, 83 source guards plus six supplemental roles, 31 fixture identities, 51 native paths and 925 staged/working research payloads. Both original app copies remain unchanged. This failed measurement experiment is now the latest root-verified restored epoch; terminal peer review also passes. The timing-only successor is now running as session64229 in `css-keyframe-normal-recascade-balanced-reuse-runtime-v1`, using the actual restored epoch. It normalizes only that marker in independent derivative copies, then runs eight fresh-profile ABBABAAB captures without builds. Its controller and terminal verifier pass source review/root static replay; actual timing results remain pending. Semantic index contents are preserved; current raw bytes are stable at root verification, with a historical raw change whose cause is not established. Signing remains blocked by the last 1Password failure.

The finite-DAG sampling model now passes independent root replay and review: dependency-respecting complete evaluations produce current values regardless of valid evaluation order or prior cache contents, under fixed graph/computation and sample-progress assumptions. Eight examples and five false controls pass. This extends the research model, not native verification or canonical CSS coverage. [Model and limits](../css-keyframe-finite-dag-sampling-model-v1/REPORT.md), [root replay](../css-keyframe-finite-dag-sampling-root-replay-v1/REPORT.md).

The active-dependency implementation audit identifies two concrete integration boundaries: animation-rule conversion must be separated from public resolved-value conversion, and pending recipes must participate explicitly in the cascade dependency resolver. A subsequent spec trace resolves commitStyles for the scoped numeric case: truncate the consumer stack but use full current provider computed context; a dedicated post-composition resolver is still needed before values reach public declaration conversion. [Trace and proposed controls](../css-keyframe-commit-styles-dependency-spec-trace-v1/REPORT.md). A two-path in-crate prototype now registers the real-type recipe and converts successfully resolved endpoints to a concrete AnimationValue. It has no callers and remains uncompiled/unapplied; internal rule transport and cascade dependency resolution are the next implementation work. [Prototype](../css-keyframe-deferred-number-incrate-prototype-v1/REPORT.md). No complete native repair is claimed. [Feasibility audit](../css-keyframe-deferred-number-feasibility-v1/REPORT.md).

The seven-case commitStyles diagnostic has passed independent source review and root static replay (32 decisions plus syntax and registration checks); browser behavior remains unmeasured. Its disabled capture controller now passes root replay of 16 lifecycle/cleanup checks; independent controller review is complete. No live capture has run. The next implementation step is a faithful in-style typecheck and an internal animation-rule conversion boundary: the external recipe compile hit crate-private field access, while the real public interpolation API control passed. The constructive Lean extension now passes root replay: it constructs a complete admitted schedule from finite dependency ranks and proves sample/history equality from arbitrary old caches (nine audits, eight examples, four false controls). Rank certificates and faithful dependencies/computations remain premises; maximum-rank-dependent cost is not a native scheduling recommendation. [Proof and limits](../css-keyframe-finite-dag-schedule-root-replay-v1/REPORT.md). Neither checkpoint is a completed native repair. A further root-replayed arena bridge derives older-operand ordering from checked append, proves an ascending index scan valid, and proves selected-root results under a dependency-closed mask. Seven audits, six examples and three false controls pass; exact Rust reachability and successful pure endpoint/float semantics remain external. [Arena bridge](../css-keyframe-operation-arena-schedule-root-replay-v1/REPORT.md).

The native composition audit exposes a concrete integration gate: additive/implicit endpoints and iteration accumulation may consume an earlier unresolved result. The deferred representation must preserve those operations and native arithmetic fallbacks. Existing computed-value animation already preserves attribute taint; the initial prototype's taint rejection is not a production requirement. Ordinary registered-cycle/defaulting and short-circuit fallback controls have supported spec oracles, but correspondence between mutually animated endpoint dependencies and declaration SCC invalidation remains inconclusive. Unsupported evaluation must not become CSS invalidity, cached output or a production panic. [Cycle trace and controls](../css-keyframe-animated-cycle-spec-audit-v1/TRACE.md).

The first pending-rule transport draft is rejected for application: it exposed unsupported evaluator states with no valid recovery owner, and provisional cycle handling was not justified. The replacement direction reuses complete native endpoint semantics. A one-file extraction now returns substituted computed values/CSS-wide keywords or genuine parse failure without publishing endpoints, while preserving the original apply/defaulting and attribute paths; it is source-reviewed but uncompiled. [Extraction](../css-keyframe-deferred-number-endpoint-resolver-v1/REPORT.md). A separate scoped trace confirms invalid acyclic registered-number endpoints default to their registered initial and remain in the keyframe. [Trace](../css-keyframe-invalid-registered-endpoint-trace-v1/REPORT.md). The iterative operation arena is source-reviewed and removes the earlier prototype's numeric/depth restrictions, uses actual AnimationValue operations, and excludes discarded roots. The exact arena module now type-checks against the actual built style metadata in both library and test modes; no substitute API was used. Test mode emitted an empty metadata file and executed no tests. In-crate integration and successful arithmetic/metadata execution still need validation; the four drafted graph tests have not run. [Typecheck and limits](../css-keyframe-operation-arena-typecheck-v1/REPORT.md). A ten-case invalid-endpoint diagnostic now passes root static replay and isolated WPT lint; its browser run is pending. It covers valid-to-invalid animated providers in both creation orders, missing versus wrong-type fallback and registered initial defaulting. [Diagnostic](../css-keyframe-invalid-registered-endpoint-diagnostic-v1/README.md). No producers are enabled and no native fix is accepted.

The dormant candidate's five-Gecko/three-WPT patch has a clean-base transport adaptation with no identified semantic prerequisite on fixes 129–131; clean-base runtime validation remains outstanding. [Independent-patch assessment](../css-keyframe-dormant-v5-clean-base-assessment-v1/REPORT.md).

Earlier broad-recascade experiment (superseded by the 190-case normal-only candidate above): the dormant-animation candidate passed its 182-case correctness comparison, but local timing showed an added first-style-flush cost. For 1,000 targets, several literal first-play/replay cases rose from 2–3 ms to about 4.5–6 ms and returned to 2–3 ms after restoration. All six browser runs and both builds passed; root checks verify the original source/build and index are restored. The candidate remains unaccepted. Next: investigate a distinct normal-only recascade request that refreshes every provider without selector rematching, retain the planned 190-case correctness scope, and repeat timings. [Measurements and limits](../css-keyframe-dormant-replay-timing-analysis-v1/REPORT.md).

A follow-up on the restored build reproduces four more stale-value cases: cancelled animations using changed `em` or custom-property inputs return 20 instead of 40 for width/transform; all four fresh-animation controls pass. Root verification and independent review confirm the temporary fixture is removed and source/build/index are preserved. This extends the same dormant-cache investigation, not the accepted bug count. These eight cases were subsequently included in the completed 190-case comparison above. [Measured observations](../css-keyframe-dormant-provider-baseline-runtime-v1/SUMMARY.json).

Fix131 is accepted: active animations now refresh attribute-dependent keyframes after attribute changes. The eight-native-file/four-WPT patch passes all46 landing cases and repairs33 failures across162 cases, preserving116 controls and exactly reproducing all baseline outcomes after restoration. Both builds, root verification, terminal review, formatting and exact-body WPT lint pass. Fix130 is a functional prerequisite. Installation and rebuild are complete: all 46 regression checks pass again, and root preservation checks pass. Independent installation review also passes; the signed commit is pending. **130 accepted fixes:105 committed and25 pending; one additional repair held.** [Acceptance and patch](../css-keyframe-attr-effect-publication-acceptance-v1/REPORT.md).

Local comparison69119 completes126PASS/36FAIL →159PASS/3FAIL →exact126PASS/36FAIL. Both builds pass; all46 selected cases pass on the candidate, repairing33 assertions with116 controls exact. Root42681 verifies restoration,779 roles,925 staged working payloads and six-fixture cleanup. Raw index bytes change75dd→bc3412 with semantic staging preserved; cause unknown. Independent terminal review passes; accepted as fix131. [Comparison](../css-keyframe-attr-publication-comparison-runtime-v2/REPORT.md).

The expanded attribute-publication baseline completes162 cases:126PASS/36FAIL across19 OK harnesses. All128 prior outcomes and20 unchanged lifecycle outcomes remain exact. All22 lifecycle cases now reach calibrated stale-value assertions, alongside five retained-mutation, four retained-pseudo and two detached-replacement cases. Fresh pseudo and ordinary controls pass. Root preservation, six-fixture cleanup and independent terminal review pass. The native repair remains unapplied and no new fix is counted. [Baseline](../css-keyframe-attr-publication-baseline-runtime-v2/STATUS.md).

The provisional Boolean-watch extension passes an independent Lean replay:15 support audits, five closed examples and three expected-false controls. It proves finite-history preservation under conservative strengthening; target reassociation, native correspondence and scheduler delivery remain unproved. [Root replay](../css-keyframe-provisional-bit-watch-root-replay-v1/REPORT.md).

The 150-case publication baseline completed with 120 PASS and 30 FAIL across 17 OK harnesses. All prior 128 outcomes remain exact. Twenty new lifecycle cases reach their final stale-value assertion; two styled-retarget cases fail before their initial provider is independently calibrated. Root preservation verifies all 773 roles and four-fixture cleanup; independent terminal review passes. Native comparison remains stopped until those two tests distinguish initial retargeting from the following mutation. A successor baseline will also measure prepared after/marker and detached-setKeyframes probes, for 162 planned cases. The eight-source native proposal remains unapplied. [Baseline](../css-keyframe-attr-publication-baseline-runtime-v1/STATUS.md), [proposal](../css-keyframe-attr-effect-publication-repair-v1/REPORT.md).

The Boolean-watch model independently replays in Lean: its general finite-history simulation preserves every admitted exact-name update, while permitting conservative extra updates. All 18 audited declarations and three intended false controls pass. Native provisional flags, target mapping and scheduler delivery remain external obligations; canonical counts are unchanged. [Proof and limits](../css-keyframe-attribute-bit-watch-root-replay-v1/REPORT.md).

The attribute-mutation diagnostic completed with 7 PASS and 5 calibrated retained-effect failures across 12 cases. All matching fresh effects and ordinary styles pass; forced recascade repairs the stale values. Driver and root preservation checks, fixture cleanup and independent terminal review pass. Next: implement and compare per-effect attribute dependency publication, including lifecycle and pseudo-element tests. The Lean watch model has 24 audited declarations and three rejected false controls; native refinement and scheduler delivery remain explicit premises. Canonical coverage counts are unchanged. [Browser diagnostic](../css-keyframe-attr-mutation-diagnostic-runtime-v1/REPORT.md), [model and limits](../css-keyframe-attribute-watch-model-v1/REPORT.md).

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

The inactive-cache companion now passes root and independent Lean replay: five support declarations, six closed examples and four rejected false claims. It separates persistent cached objects from active registration and characterizes the freshness-or-pending obligation on reuse; it does not prove native scheduling or add canonical CSS coverage. The next 20-case browser diagnostic (attributes, viewport, ordinary cancellation and inactive replay) passes static review and awaits the actual restored build binding.

The animation obligation model now passes root replay and independent review. One finite-history protocol result covers preserving pending work through animation/normal passes, cancellation and retargeting;27 audited declarations include19 general/support results and8 closed examples, with four false claims rejected. Dependency admission, native transition refinement, computed-value correctness and eventual task delivery remain explicit premises; no canonical or normative CSS coverage increment. [Model](../css-animation-obligation-conservation-v1/REPORT.md).

The expanded147 baseline32993 completed all expected browser callbacks but rejected a planned order for12 style-change-events names. Actual125PASS/22FAIL includes123PASS/seven expectedFAIL in the130 added controls; old17 outcomes remain exact. Source/build/index preservation and cleanup pass, including unchanged currentrawindex9530. Correct the planned order and rerun unchanged tests before using it as an accepted baseline. [Rejected capture](../css-keyframe-effect-regression-baseline-runtime-v1/REPORT.md).

Focused local comparison27003 rejected the first animation tree-counting candidate: **2PASS/15FAIL → 15PASS/2FAIL → exact2PASS/15FAIL after restoration**. Both builds succeeded. The two remaining failures occur after cancelling another effect and mutating siblings without an intervening style flush. Source reviews identify consumption of the normal recascade request by animation-only traversal; the unchanged WPTs expose missing keyframe recomputation. A narrow v2 proposal now requests RESTYLE_SELF only for animated dependents and passes root patch replay and independent source review; it remains unapplied and uncompiled. The147-case preservation gate is still required before acceptance. [Comparison](../css-keyframe-tree-counting-comparison-runtime-v1/REPORT.md), [successor](../css-keyframe-tree-counting-effect-prototype-v2/REPORT.md).

Root verification preserves637 roles,79 source guards,25 installed tests,925 staged working payloads and the exact HEAD/stage/native snapshots. An extra historical raw-index hash check differed despite identical staged entries and diff; current index bytes were preserved, with no established cause or byte-equality claim. The initial failed check is retained. Independent terminal review verifies restoration under that semantic stage contract and retains the raw-index limitation. No new accepted fix or commit is added.

Keyframe lifecycle baseline 55798 completed: **2 PASS / 15 FAIL across 17 cases**, with four OK harnesses. All seven new cases fail at calibrated target-value assertions; the previous ten outcomes remain exact. Width/translation stay stale after sibling mutations across clone, retarget, reparent, equal-value replacement and multiple-effect histories. Later assertions after each first failure are unobserved. Both temporary fixtures were removed; root preservation checks and independent terminal review pass. This extends known bug 1883255 evidence, with no new accepted fix. The first candidate later compiled but failed two cancellation assertions; see the completed comparison above. All17 candidate cases and the separate147-case regression gate remain required before acceptance. Before acceptance, also compare existing KeyframeEffect copy-constructor, target, setKeyframes and style-change-events tests plus CSSAnimation-canceling.tentative; the initial 17-case experiment alone is insufficient. [Baseline](../css-keyframe-tree-counting-baseline-runtime-v1/REPORT.md).

Canonical run 5941 passes **11,752 declaration audits, 12,336 executable cases, 2,140 source fingerprints and 142 expected-false controls**. The reviewed finite ModRem witness and replacement contract are now integrated as implementation support. This transfers 28 existing audits with no new research theorem credit or normative CSS coverage. Prior outputs, unrelated library files, both indexes and the installed native build are preserved; root verification and independent terminal review pass. [Integration](../css-finite-mod-rem-library-integration-runtime-v1/REPORT.md).

Fix128 is accepted: finite mod()/rem() quotient reconstruction loses small remainders. Its one-Rust-file/one-WPT patch repairs16 failures and passes all700 selected assertions. Original-source restoration reproduces the exact baseline; root preservation and independent terminal review pass. The Lean counterexample and replacement contract have independent root replays with explicit native arithmetic assumptions. It is now installed and rebuilt: all 24 landing cases pass, and root verification preserves the source, test and staging state. Independent installation review passes; signing remains pending. [Acceptance and patches](../css-finite-mod-rem-acceptance-v1/REPORT.md), [installation](../css-finite-mod-rem-install-runtime-v2/REPORT.md).

Completed ModRem comparison: session59511 exits0. Baseline684PASS/16FAIL improves to700PASS; restored source/build reproduces every baseline outcome. Both builds pass, only16 target failures change, the temporary WPT is removed, and root live628-role/24-identity preservation passes. Independent terminal review passes; the repair is accepted as128 and is now installed. [Comparison](../css-finite-mod-rem-comparison-runtime-v1/REPORT.md).

Earlier arithmetic diagnostic: local run44048 reproduces16 calibrated finite mod/rem mismatches; all8 signed-zero/infinite-divisor controls pass. Source/build/index preservation and owned-fixture cleanup pass. Independent terminal and repair-source reviews pass; the subsequent comparison accepted this repair as fix128. The bounded Lean witness independently replays with six examples and five false controls, deriving the old rounded formula's zero result against an independent remainder of two under explicit rounding/source contracts. This is not a universal native/compiler proof or a CSS precision guarantee. [Browser evidence](../css-finite-mod-rem-runtime-v1/REPORT.md), [Lean replay](../css-finite-mod-rem-witness-root-replay-v1/REPORT.md).

Earlier keyframe diagnostic: local run24853 completes ten cases: six calibrated sibling-mutation mismatches, two passing initial controls and two known expected failures linked to bug1883255. Width and translation stay22→22→22px rather than22→44→22px across sibling indices1→2→1, including cloned and retargeted effects. The temporary fixture is removed; source/build/index preservation passes. Terminal archive review passes, independently recounting the raw outcomes. This adds no accepted fix. [Evidence](../css-keyframe-sibling-dependency-runtime-v1/REPORT.md).

Previous installation: accepted127 is installed. Session63017 and root verification78872 exit0; the full build and all ten landing tests pass. Independent terminal review passes. That epoch preserved611 roles,72 source guards,24 installed test identities,43 modified native paths and925 staged/working research payloads. [Installation](../css-name-repeat-context-install-runtime-v2/REPORT.md).

Latest subgrid comparison: session 92179 exits 0. The candidate passes all ten new cases and repairs exactly eight admission failures; every other outcome remains unchanged across 1,532 assertions and eight rendering tests. Both full builds pass, the original stack reproduces the exact baseline, and all 611 roles / 72 sources / 23 installed identities / 925 staged payloads are preserved. Seven temporary fixtures are removed. Whole-run review passes and fix127 is accepted; it is now installed, with signing pending. [Comparison](../css-name-repeat-context-comparison-runtime-v1/REPORT.md).

Latest comparison: session 27331 exited 0 after all five phases. Runtime NaN repairs eight failures, finite negative zero repairs four, and both repair twelve; every other outcome stays exact. All phases pass the 159 installed mandatory assertions and eight references. The original source is restored, rebuilt and retested to the exact 1,408 PASS / 76 retained FAIL baseline. All 605 roles, 72 sources, 21 identities and 925 staged payloads are preserved; six temporary fixtures are removed. Independent terminal review passes; fixes 125 and 126 are accepted. [Comparison](../css-round-runtime-finite-comparison-runtime-v1/REPORT.md).

Signing: v6 retry session90997 failed with the 1Password buffer error. After-index18904 and root preservation45716 exit0: HEAD, raw/semantic index, all925 staged and working payloads,611roles,72sources,23installed identities and43native paths are unchanged. No unsigned fallback or further retry is queued. [Attempt](../css-hidden-query-signing-execution-v6/REPORT.md).

Previous installation: accepted125/126 are installed after session58409. All1,484 assertions complete with1,420PASS/64unchangedFAIL; all18 new landing cases,159 prior mandatory assertions and8references pass. Only the12 expected failures improve. Four controls are removed;605roles,72sources,23installed identities,43native paths and925staged payloads pass final and post-lint preservation checks. Lint reports no errors; five warnings concern unchanged Rust regions and ESLint ignoring the WPT files. Independent terminal review passes. [Installation](../css-round-runtime-finite-install-runtime-v1/REPORT.md).

Previous diagnostic: session 5177 completes 38 assertions with 24 PASS and 14 calibrated numerical FAIL. All 18 strict controls, two literal-NaN comparisons and four detached policy observations pass. Independent terminal review verifies raw classification and preservation of 609 roles, 72 sources, 23 installed identities and 925 staged payloads; both temporary fixtures are removed. The unknown-step discrepancy is reproduced, but its guard is not accepted or installed. [Diagnostic](../css-round-infinite-value-step-runtime-v1/REPORT.md).

Latest diagnostic: contextual subgrid name-repeat baseline session 66325 exits 0, with two controls passing and eight exact declaration-admission failures in one completed harness. This reproduces known bug 2037744; no new fix is accepted. The temporary WPT is removed and all 611 roles, 72 sources, 23 installed identities, 43 native paths and 925 staged/working research payloads are preserved. Independent terminal review passes. The 1,532-assertion plus eight-reftest candidate/restore comparison is being prepared. [Baseline](../css-name-repeat-context-baseline-runtime-v1/REPORT.md).

Updated 24 October 2026. Work stays local; the user owns pushing. This status and execution queue supersede every historical checkpoint below.

## Current status

**127 accepted fixes: 105 committed locally and 22 awaiting commits. One additional repair, 120, is held (128 tracked).** All twenty-two accepted pending fixes are installed in the working tree and local build. Repair120 remains held and uninstalled. Each fix has a separate Gecko/WPT patch, with research and tooling in preceding commits. The most recent signing attempt, session 90997, failed in 1Password; no unsigned replacement or automatic retry is queued. [Commit ledger](CURRENT-COMMITS.json), [grouped fixes and commit IDs](../css-fix-readout-20261023/README.md).

The preceding119/121/122 installation is session 28306, verified by root checker 45302 and independent terminal review. Fixes 119, 121 and 122 repair relative-length intermediate normalization, stored integer bounds and saturated subgrid counts. The 1,382-assertion comparison improves 1,317 PASS / 65 FAIL to 1,337 PASS / 45 FAIL, preserves every prior pass and retained failure, and passes all 99 required assertions and six reftests. The seven native changes and four WPT files are installed. [Installation](../css-accepted-119-121-122-install-runtime-v1/REPORT.md).

**Earlier rejected numerical comparison: session 18353 stopped after its baseline control failure and restored the working stack.** Each phase runs the same 658 assertions in six harnesses: explicit HEAD90, quotient repair alone, parse-time signed-zero repair alone, and both repairs. A fifth build restores the installed working stack. Root final checker 40823 exited 0 and verifies the restored source/index/test/resource maps and rebuilt binaries; independent terminal review passes. That restored epoch superseded the earlier installer binary hashes; current installation58409 now supplies the live binaries. Live preflight 17616, controller/binding reviews, fixture lint and baseline build passed. Baseline completed 641 PASS / 17 FAIL across all 658 assertions and six OK harnesses. The both-infinite control returned opacity 1 instead of 0, triggering the unchanged rejection policy before any candidate phase. All eight signed-zero cases passed, so that proposed bug did not reproduce. Root source review supports an eager-division bypass for the signed-zero fixture and a separate unresolved-value infinite-step simplification path. The 15-case follow-up now completes10PASS/5calibratedFAIL: the original eight controls pass, four Pow observers fail, and deferred value/literal infinite step fails while literal/both-deferred controls pass. Root preservation checks and independent terminal review pass. Unknown-step, unit-basis and runtime NaN handling are being audited separately. Session 18353 exited 1 after restoration build exit 0 with no recovery errors. Neither candidate is accepted. Final review confirms complete restoration and the rejected baseline control. No single-fix or combined phase ran, so no comparison or repair claim follows. [Runtime](../css-round-four-phase-comparison-runtime-v1/README.md), [terminal checker](../css-round-four-phase-final-checker-v1/README.md).

Fixes 123 and 124 passed isolated and combined comparisons, root restoration checks and independent review. Calculated counter ranges reproduce a content-process unwrap crash in the local build; additive-symbol weights produce incorrect CSSOM and rendering results. Separate five-path Gecko/WPT patches are ready. Release follow-up69761 now reproduces a content-process unwrap panic in installed Firefox158.0 under WPT preferences, after literal rendering and CSSOM admission controls pass. Root preservation and independent terminal review pass. Stock-profile reproduction, exact symbolicated native call site and memory-safety impact remain unestablished. [Counter range acceptance](../css-counter-range-acceptance-v1/REPORT.md), [additive acceptance](../css-additive-symbols-order-acceptance-v1/REPORT.md).

Canonical validation session77965 passes **11,724 declaration audits,12,312 executable cases,2,135 source fingerprints and131 expected-false controls**. Four existing Round special-value support laws and eight controls are now registered; all prior audit/example output and both indexes are preserved. Installed counter correspondence is appended without changing descriptor proofs. No new normative coverage or research theorem credit is claimed. Independent terminal review passes. [Integration](../css-round-knowledge-library-integration-v1/REPORT.md).

Prior canonical checkpoint: Canonical validation session 32137 passes **11,720 declaration audits, 12,304 executable cases, 2,133 source fingerprints and 127 expected-false controls**. Root preservation checks and independent result review pass. Finite rational Round is a partial specification fragment; binary32 magnitude decoding and remainder capacity are separate implementation support. These counts are not a percentage of CSS coverage or a proof of native Stylo. Four new SMT obligations and three SAT controls support a conditional floating-point reconstruction argument; they are not Lean-certified solver proofs and are not registered as new canonical results. A separate reviewed special-value audit adds four conditional Lean class laws and four rejected false claims. Its extracted runtime helper has16 NaN mismatches among196 representative inputs per optimization level; a NaN-first helper has none on that matrix. At that checkpoint these were unaccepted leads; runtime NaN priority is now accepted125, while unknown expressions and context-dependent leaf coefficients remain open. [Canonical integration](../css-round-scalar-capacity-library-integration-v1/REPORT.md), [reconstruction review](../css-round-reconstruction-projection-review-v1/REPORT.md).

New standalone observer model: root replay8171 passes18 kernel examples and4 false-claim controls for negative-infinity retention and bounded observations. Three general support results and two corollaries remain conditional on supplied classes, provider behavior and admission; canonical integration and native refinement are not claimed. Compiler scratch was removed. [Root replay](../css-round-infinite-step-observer-root-replay-v1/REPORT.md).

## Current execution queue

1. **Implement contextual integer prerequisites, starting with subgrid name repeats.** Resolve retained counts using the actual style context, then rebuild the saturated expanded-name cache. Removing the parser restriction alone would expose a context-free unwrap. Follow with context-aware steps conversion and its publication callers; the targetless Web Animations path needs an explicit policy rather than a fabricated font context. These are source-tracked bugs 2037744/2037743, not newly counted findings. Keep the conditional unknown-step Round guard and held120 unaccepted until their admission consequences are addressed. A separate experimental comparison may measure those consequences while preserving the restored stack. [Design](../css-contextual-integer-prerequisite-design-v1/DESIGN.md), [guard review](../css-round-infinite-value-step-repair-root-review-v1/REPORT.md).
2. **Preserve release exposure evidence with fix123.** The installed Firefox158.0 run69761 passes literal rendering and CSSOM admission, then records a content-process unwrap panic for calculated-range rendering. Root checker56524 and independent terminal review verify the result and preservation. Its failed socket-path predecessor remains archived. The fresh WPT profile result does not establish stock-profile exposure, exact symbolicated source site or memory-safety impact. Keep this evidence in the review package; no repeat release run is required for installation. [Release result](../css-counter-range-release-browser-runtime-v2/REPORT.md), [review](../css-counter-range-release-terminal-review-v2/REVIEW.md).
3. **Commit accepted work in separate pieces.** All twenty accepted pending fixes are installed;125/126 terminal review passes. Preserve independent patches, their exact WPTs and preceding research commits. The new125/126 recipes keep the shared calc hunks separate and leave actual signed parents unbound. Use the new verified installation and fresh binary hashes; earlier restored binaries are historical. Resume signed commits when signing is available, binding each recipe to its actual parent. Keep 120 held until context-free integer admission is repaired and tested.
4. **Test reversed-counter arithmetic and element grouping.** The reviewed proposal uses counter-local signed 128-bit arithmetic without a shared quote-list cap. Its Lean capacity bound is conditional on valid distinct-node traversal and pointer width. Prepare explicit HEAD90, arithmetic-only and arithmetic-plus-grouping phases, followed by restoration. The small roster contains eight diagnostic assertions and eight reftests; require separate arithmetic and grouping repair witnesses. The disabled controller passes root static replay and independent review, including 32 rejection cases. Actual post-restoration adapter and execution binding remain pending. Native portability and browser validation remain outstanding. [Proposal review](../css-counter-wide-initializer-review-v1/REPORT.md), [comparison plan](../css-counter-wide-three-phase-plan-v1/PLAN.md).
5. **Extend formal coverage and native correspondence.** Continue the versioned CSS requirements ledger, provider ownership/completion, parser progress, mutation histories and animation provenance. Connect exact rational Round, representable remainder and final binary32 projection without silently assuming native/compiler equivalence. Keep external premises and normative coverage separate. Original Bloom milestones 1–6 retain their recorded scope. [Closure checklist](FORMAL-CLOSURE-CHECKLIST.md), [whole-CSS assessment](../css-whole-spec-completion-strategy-v1/README.md).
6. **Resume the remaining validated leads.** The color candidate remains rejected for two lost passes and 48 changed retained failures despite 22 improvements; preserve the original oracles while separating missing-channel repairs and powerlessness arithmetic. Ancestor-overflow traces and snapshots establish extreme-coordinate coverage failures, with the normative range boundary unresolved. The composed flex candidate remains rejected by a nested last-baseline regression; finish wide-coordinate publication and consumer transport before retesting. [Color rejection](../css-color-powerless-rejection-analysis-v1/REPORT.md), [overflow design](../css-ancestor-coverage-repair-design-v1/REPORT.md), [baseline API inventory](../css-wide-baseline-api-inventory-v1/REPORT.md).

Preserve the active build and every artifact needed to reproduce accepted or rejected results. Remove obsolete build targets only after confirming they have no active consumer or retained validation role. No full-CSS completion is claimed.

## Superseded 24 October status and queue (historical)

The following snapshot retains the earlier decisions and evidence. Statements about current counts, running sessions, acceptance or pending work are superseded by the status and queue above.

### Earlier installation and finite Round integration checkpoint

Actual canonical run32137 exited0 after applying the reviewed fourteen-path integration: **11,720 declaration audits / 12,304 executable cases / 2,133 source fingerprints / 127 expected-false controls**. Prior outputs, unrelated library files and both staged indexes are preserved. Independent execution-result review passes. Finite Round adds one partial specification fragment; magnitude decoding and remainder capacity stay separate implementation support, with native/compiler correspondence external. No new accepted native fix or research theorem credit. Installation28306 and root checker45302 exited0; independent terminal review passes. Its1,382 assertions improve1,317PASS/65FAIL to1,337PASS/45FAIL, with29OK harnesses and sixPASS references in both phases. All99 mandatory assertions pass. No baseline pass is lost or retained failure changed. The seven source changes and four persistent WPTs are installed; both temporary controls are removed. Round comparison18353 is now running from reviewedv2 after livepreflight17616 and independent binding review. Four scientificHEAD90 phases each run658cases/sixharnesses; a fifth build restores the verified119/121/122 working stack. No candidate is accepted yet. The batched gate preserves every staged-payload check and measured2.760seconds in actual preflight.

New research also supplies a reviewed counter-local signed128 initializer proposal and one conditional Lean bound, removing the shared quote-list cap. Four focused Round SMT obligations are UNSAT with three SAT controls; the finite-case composition is independently reviewed, with remainder/IEEE/compiler bridges explicit. Neither research capsule adds an accepted fix.

### Earlier plan checkpoint

Current count: **105 committed fixes,18 accepted awaiting commits, and one held repair (124 tracked)**. The verified working stack includes119/121/122;123/124 await installation and120 stays held.

Finite rational Round now passes root replay55848 and independent v2 review: eleven declarations include the general toward-zero absolute-bound equivalence, with thirteen examples and five false controls. The eight-observer vector contains seven finite Round evaluations and one explicitly supplied infinite-step control. The module excludes parsing, units, defaulting, line-width, nonfinite Round and native machine refinement. [Model](../css-finite-round-scalar-model-v2/REPORT.md), [review](../css-finite-round-scalar-model-review-v2/REPORT.md).

Binary32 magnitude refinement now passes root replay14349 and independent review: seven new audits prove both directions between finite32-bit magnitude patterns and the capacity predicate, then compose exact remainder representability. Twelve examples and four false controls pass. Native remainder/compiler behavior and signed-zero policy remain external. The seven audits are now registered in the canonical integration above; the new conditional reconstruction/projection argument narrows the numerical gap without proving native runtime refinement. [Model](../css-binary32-magnitude-decoder-v1/REPORT.md), [root review](../css-binary32-magnitude-decoder-root-review-v1/REPORT.md).

Next Round comparison: retain all650 reviewed context-dependent cases and add the eight finite parse-time signed-zero cases. Plan four phases to attribute the two repairs independently and preserve both single-repair outcomes in the combined phase. The new two-path proposal passes root source review,512 finite helper cases and224 special controls; it remains browser-unrun. Actual execution requires binding to the verified119/121/122 installed epoch and review. [Candidate](../css-round-parse-negative-zero-repair-v1/REPORT.md), [root review](../css-round-parse-negative-zero-root-review-v1/REPORT.md).

New numeric research: the general dyadic remainder-capacity proof passes root receipt/log verification and independent replay: three results, twelve examples and five rejected false claims. Mathematical binary32 decoding is supplied by its separate reviewed model; native remainder behavior and signed zero remain external. These three results are now registered in the canonical library. A separate finite parse-time round() signed-zero lead passes source/spec and fixture review, with four predicted witnesses and four controls; browser execution remains pending. Neither changes fix counts. [Remainder proof](../css-round-remainder-capacity-v1/REPORT.md), [review](../css-round-remainder-capacity-review-v1/REPORT.md), [signed-zero lead](../css-round-parse-negative-zero-audit-v1/REPORT.md).

The accepted119/121/122 installation is complete and independently verified. It preserves118 rounding and mixed Grid changes, passes1,382-case paired comparison with20repairs and99mandatory candidate passes, and passes both actual64-bit binary gates and all six reftests.120 stays excluded. [Plan](../css-accepted-119-121-122-install-plan-v2/README.md), [review](../css-accepted-119-121-122-install-plan-review-v1/REPORT.md).

Standalone library: counter descriptor representation support is integrated. Full check91026 and root verifier67401 exit0:11,699 audits/12,284 executable cases/2,127 source fingerprints, including122 expected-false cases. Eleven existing results register once; normative coverage stays unchanged. All prior results, unrelated files and nested/main staged work are preserved. Independent final review passes. [Integration](../css-counter-descriptor-library-integration-v1/REPORT.md), [review](../css-counter-descriptor-library-integration-results-review-v1/REPORT.md).

Counter/additive comparison49842 exited0 after all four phases and successful original-stack rebuilding. Root final checker82153 exited0 and independently verifies every phase plus the complete restored source/index/test/resource/binary state. All twelve observed improvements survive the combined phase, with no regressions or changed retained failures. The runtime is sealed; independent terminal review passes and fixes123/124 are accepted as separate Gecko/WPT patches, pending installation and signing. [Runtime](../css-counter-additive-comparison-runtime-v1/REPORT.md).

Earlier signing attempt9680 failed with the same 1Password buffer error; root checker17557 verifies all925 staged payloads,72 sources,539 roles,11 installed identities and native differences unchanged. No commit was created and no signing retry is queued. Continue the counter/additive repair comparison after source review and actual epoch binding. [Signing evidence](../css-hidden-query-signing-execution-bound-v4/REPORT.md).

Both browser diagnostics are terminal and root preservation checks pass. Counter-range session27424 reproduces a content-process unwrap panic in Servo_CounterStyleRule_IsInRange after literal/admission controls pass; independent result review passes. Additive-symbol session88110 reproduces22PASS/10FAIL CSSOM outcomes and one rendering reftestFAIL; root checker66961 verifies preservation and cleanup, with independent review passing. Neither proposed repair is accepted yet. Those diagnostics preserved their input state; session49842 now owns the source/build tree for the comparison. [Counter evidence](../css-counter-range-isolated-browser-runtime-v2/REPORT.md), [additive evidence](../css-additive-symbols-order-browser-runtime-v1/REPORT.md).

Previous completed comparison: session92779 terminated with exit0 after all four browser comparison phases passed and the original stack was restored and rebuilt successfully. Root final checker46766 exited0 and verifies all69 source guards,42 saved originals,36 native differences,925 staged paths,11 installed test identities,461 resources and532 final roles, including rebuilt binaries. The combined comparison improves291PASS/48FAIL to305PASS/34FAIL with all31 targeted cases and six reftests passing; no prior passes or retained-failure diagnostics change. Independent terminal/result review and root registration now pass. The two repairs are accepted as121 and122, pending installation and signing. [Terminal evidence](../css-integer-range-subgrid-comparison-runtime-v2/REPORT.md).

The integer-range/subgrid diagnostic is now complete: session83357 and root checker93382 exit0. All82 subtests finish (66PASS/16FAIL); eight new calibrated failures comprise six calculated steps() range failures, one calculated-zero subgrid mismatch and one large-positive count mismatch. The56 existing controls have48PASS/eight expectedFAIL and no unexpected failures. All505 preserved roles,67 sources,36 native differences,925 staged paths and11 installed test identities remain intact, with all three fixtures removed. The subsequent339-subtest/six-reftest comparison accepted the range and saturated-count repairs as121 and122. [Browser evidence](../css-integer-resolve-range-browser-runtime-v1/REPORT.md). Independent terminal review passes; the first comparison attempt stopped at lint and verified restoration; retry92779 completed and restoration was verified.

Completed comparison: Sign session80904 completed all three1,037-case phases. Baseline996PASS/41FAIL becomes raw-only1002PASS/35FAIL and combined1007PASS/30FAIL. Raw repairs six cases; Sign adds five repairs; all19 landing cases pass combined, with no prior PASS loss or changed retained FAIL diagnostics. The original stack through117/118 was restored and rebuilt; session80904 exited0. Root checker24470 verifies all phase evidence and full preservation (67 sources,40 saved originals,36 native differences,925 staged paths,11 test identities and496 final roles). Independent terminal review passes. Fix119 remains accepted pending installation. Fix120 requires119 and is now held for contextual-integer admission prerequisites despite this scoped comparison result. Neither candidate is installed. At that checkpoint the counts were105 committed,16 pending commits and one held repair.

Updated 24 October 2026. Work stays local; the user owns pushing.

New subgrid research: five general Lean prefix theorems across the single-repeat and arbitrary-sequence extensions pass root replay and independent review. The sequence extension permits fixed repeats and ordinary groups in any order with auto-fill anywhere, under exhausted capacity. They connect capped count arithmetic to the explicit line-name prefix in the exhausted-capacity case, conditional on valid native inputs and ordered successful appends/serialization. Earlier results were rebuilt unchanged without duplicate credit; these results are now registered once through the subgrid integration, with no new accepted fix. [Model](../css-subgrid-line-prefix-model-v1/REPORT.md), [root review](../css-subgrid-line-prefix-root-review-v1/REPORT.md), [sequence extension](../css-subgrid-sequence-prefix-root-review-v1/REPORT.md).

### Superseded status snapshot

The standalone CSS library now includes the reviewed subgrid chain and conditional counter descriptor representation support. Full canonical validation and root preservation checks pass: **11,699 declaration audits,12,284 executable cases and2,127 source fingerprints**, including122 expected-false cases. The counter descriptor integration registers11 existing results and8 controls; independent final review passes. It adds no normative coverage feature. The earlier subgrid integration registered19 existing results and28 checks, with its supplied-semantics and native-refinement limits unchanged. [Counter descriptor integration](../css-counter-descriptor-library-integration-v1/REPORT.md), [subgrid integration](../css-subgrid-library-integration-v1/REPORT.md).

Next sequence: validate the independently landable counter-range and additive-symbol repairs in the prepared four-phase comparison, then inspect raw results and full source/build restoration before acceptance. The disabled controller passed root source review and45 rejection checks; actual state bindings and independent reviews are in progress. Both diagnostic findings are reproduced and independently reviewed. After those repairs, install/validate accepted119,121 and122 as separate changes and resume contextual round()/integer admission work. Repair120 stays held until its contextual admission prerequisites are implemented and validated. Signed commits remain queued after the latest1Password failure; no automatic signing retry is planned. [Comparison preparation](../css-counter-additive-comparison-v1/README.md).

Whole-auto-fill proofs pass root replay and independent review: eight audited declarations (including two list-support results), twenty literal WPT oracles and four semantic false-claim controls. The results are now registered through the canonical subgrid integration without duplicate research credit or new accepted fixes. The separate counter-range source audit is ready for isolated browser reproduction after the running comparison restores the tree; no crash or severity is established. [Subgrid review](../css-subgrid-whole-autofill-root-review-v1/REPORT.md), [consumer review](../css-integer-consumer-root-review-v1/REPORT.md).

Additive landing requirement: the standalone two-file local resolver candidate now passes source review, exact patch/composition checks, formatting and WPT lint. It applies the nonnegative projection consistently in parsing and export while preserving stored serialization; the generic integer-range repair is no longer a prerequisite for this alternative. All32 CSSOM cases and the eight-row reftest retain negative/fractional controls. Validate on the original base first, then check composition on the generic-corrected base. The earlier comparator-only variant remains an explicitly dependent alternative. Neither is accepted or compiled yet. [Standalone candidate](../css-additive-symbols-local-weight-repair-v1/REPORT.md), [independent review](../css-additive-symbols-local-weight-review-v1/REPORT.md).

Installation hold: fix120 has a new source-audit risk at context-free integer consumers (`steps()` and subgrid repeat counts). The ordinary positive-font case may become a parse rejection after contextual Sign folding is deferred. Root and independent source review confirm the predicted admission transition. Browser validation and prerequisite implementation remain pending. Existing scoped acceptance is historical evidence; do not install or sign120 from it until this hold is resolved. The prepared1,097-case integration roster may need targeted additions. No new defect is counted.

**122 tracked repairs: 105 committed, 16 pending commits, and fix120 held after its scoped comparison.** Each counted fix has a minimal native/WPT patch; research and tooling are separate. Fix 116's installed-stack validation passed 101 cases across 12 files. The rejected color experiment has restored and rebuilt that installed stack; the root restoration audit passed. [Current ledger](CURRENT-COMMITS.json), [grouped fixes and commit IDs](../css-fix-readout-20261023/README.md).

The color candidate is **rejected**. Its 1,559-case comparison changed 1,264 PASS / 295 FAIL to 1,284 PASS / 275 FAIL: 22 improvements, two prior-pass regressions and 48 changed retained failure diagnostics. All 16 new cases pass, which is insufficient for acceptance. Session 51821 terminated with the expected rejection exit 1. Root verification session 71231 passed, authenticating original sources, installed tests, index, resources and rebuilt binaries. A source-preparation successor is independently source-reviewed but uncompiled; numerical hue errors and relative-color missing-channel behavior remain separate obligations. [Rejection analysis](../css-color-powerless-rejection-analysis-v1/REPORT.md).

Calculated counter marker handling and CSS integer math rounding are accepted as fixes117 and118 after independent source/model review, isolated browser comparisons and complete restoration review. Counter117 repairs14 failures and passes23 landing cases; integer118 repairs13 failures and passes37. All prior passes and exact retained failures survive each isolated phase. Their combined working-stack installation passes314 subtests and two reftests with no unexpected results; root preservation verification passes. The earlier53-case sentinel comparison remains a rejected baseline-only experiment: its classifier incorrectly expected the internal sentinel to serialize. Counter grouping, arithmetic and HTML mapped-marker aliasing remain separate unaccepted leads. [Accepted counter repair](../css-counter-calc-sentinel-acceptance-v1/REPORT.md), [accepted integer repair](../css-integer-math-rounding-acceptance-v1/REPORT.md).

Before the subgrid integration, the standalone CSS library passed **11,669 declaration audits and 12,248 executable cases**, with 2,117 source fingerprints. That earlier integration registered twelve already-reviewed dyadic/remainder support results and twelve examples under ImplementationSupport. Full canonical session5513 and root preservation60693 pass; all prior results,116 expected-false cases,3,111 unrelated files and the nested index are preserved. Independent final integration review passes. Machine arithmetic support is separate from normative CSS coverage; these counts are not a coverage percentage or a proof of native Stylo. [Latest canonical integration](../css-numeric-support-library-integration-v1/REPORT.md).

### Superseded execution queue — 24 October

A shared integer range-policy follow-up has passed independent source/helper review: the existing `steps(calc(-10), start)` failure traces to `Integer::resolve` dropping its stored clamp mode, while the context-bearing path applies it. All18 indexed callers are mapped. HEAD90/installed118 one-expression proposals preserve their respective rounding policies. A new symbolic model passes five UNSAT obligations over arbitrary binary32 inputs and produces three omission counterexamples; all three match the extracted Rust facade at opt0/2. Independent review replayed all eight solver outputs exactly and recompiled the witnesses at both optimization levels. The same-resolved-leaf premise and manual source mapping remain explicit; this is not a Lean-checked certificate or arbitrary-tree refinement. [Audit](../css-easing-integer-range-audit-v1/REPORT.md), [symbolic result](../css-integer-range-symbolic-v1/REPORT.md), [independent review](../css-integer-range-symbolic-review-v1/REPORT.md).

Preparation history: the earlier81-case diagnostic was superseded by the completed82-case run above. Independent review caught a forbidden `[auto]` line name in the separate, unrun subgrid fixture; immutable v2 uses `[fill]` and passes its32 static rejection checks and peer review. The24 timing landing cases are unchanged. A separate positive subgrid count lead concerns narrowing4,294,967,294 to signed−2; its fixture received the same identifier correction. Both corrected subgrid witnesses have now reproduced calibrated browser mismatches in session83357; neither candidate repair is accepted yet, and no security impact is established.

The successor82-case diagnostic has passed root independent review and54 static rejection checks. It includes the reviewed positive-count diagnostic as a third owned fixture, preserving all81 earlier cases. The completed browser-only pass distinguishes and reproduces both the calc(0) mismatch and the separate large-positive narrowing lead. A new Lean model proves five general capped-product/sum/remaining-capacity results with eight concrete checks; independent replay and review pass. The companion proof for a full-width guarded consumer is complete and independently reviewed; it narrows only the bounded remaining count. The apparent abspos coordinate-origin lead was rejected after tracing the earlier independent-formatting-context gate: ordinary absolutely positioned grids never acquire the required subgrid flags. This corrects the earlier conditional lead without claiming universal cap validity. The guarded full-width count consumer remains useful for the independently supported large-positive-count issue; its proposed patch is not installed or accepted. [Root diagnostic review](../css-integer-range-browser-root-review-v3/REPORT.md), [count strategy](../css-subgrid-count-repair-strategy-v1/REPORT.md), [conditional model](../css-subgrid-count-transport-model-v1/REPORT.md).

The Sign final checker has passed root and peer review, including42 static rejection controls. All three phases passed their comparison policy; original-stack restoration, root terminal verification and independent terminal review pass. A successful checker exit will verify its stated verdict, not automatically accept either candidate. [Root checker review](../css-sign-split-final-root-review-v1/REPORT.md).

The subgrid count proposal is now a separate three-native-file patch: usize saturating product and prefix sum, saturation documentation, and a full-width guarded C++ consumer. Root source review and exact historical/scratch transport checks pass. The guarded-consumer companion proves one additional general result and eight examples, with independent replay and review; root joined its prospective source bytes to the final sealed proposal exactly. Compiled-helper validation passes at opt0/2 with checked Rust arithmetic and C++ sanitizers; root replay matches. The six-case bounded WPT proposal and focused60 parser/four reftest controls pass independent review. The disabled joint range/cache comparison has passed root and peer review with 339 subtests and six reftests, retaining the prior counter/integer controls. Static replay passes 27 comparison-policy, 18 architecture and five cleanup negative checks. It requires actual 64-bit browser binaries before testing the extreme-count cases and preserves changed fixture bodies during cleanup. Actual restored-epoch and diagnostic bindings remain pending. [Root controller review](../css-integer-range-subgrid-comparison-root-review-v3/REPORT.md), [peer controller review](../css-integer-range-subgrid-controller-review-v1/REPORT.md). The separate82-case diagnostic now reproduces both subgrid witnesses; no native comparison or fix acceptance has occurred for these proposals. [Source proposal](../css-subgrid-saturated-cache-proposal-v1/REPORT.md), [root source review](../css-subgrid-saturated-cache-root-source-review-v1/REPORT.md), [guarded proof](../css-subgrid-guarded-consumer-model-v1/REPORT.md).

Shared campaign8941 and root final checker6479 pass. Independent final review verifies all213 subtests, two reftests, four builds, lint and complete original-stack restoration. Counter117 repairs14 failures with23/23 landing passes; integer118 repairs13 with37/37. Both are accepted as separate Gecko/WPT patches. The sign237 diagnostic, root audit and independent preservation review have completed. Combined installation and root preservation verification pass; installation result review passes; signing remains pending.

The source/spec/helper-reviewed `sign(±1em)` lead now reproduces two browser failures caused by premature coefficient-only folding when the computed font size becomes zero. The four-case 16→0→16 probe checks both signs, an absolute control and a deferred mixed-unit control, with all calibrations and reset checks before the final assertion. Diagnostic59403 and root audit9271 pass:2/4 main cases fail at their final semantic assertion, while227 existing controls pass and six retain expected failures. Complete source/index/test/binary preservation has passed root and independent final review. This work is now accepted as fixes119 and120, with120 dependent on119. The first candidate is held after an independently replayed21-case producer-chain experiment exposed a NaN regression. Its successor preserves intermediate special values through both calc mappers and passes455 scalar checks at two optimization levels, and has now passed the split browser comparison described above; final restoration verification and independent review pass. The successor is split into a three-file raw-conversion prerequisite with8 WPT cases and a one-line Sign folding repair with11 cases. Root scratch replay and peer split review pass. The planned baseline/raw-only/combined comparison retains all1,018 existing controls, for1,037 cases. The original14-case identities and expectations remain intact; five additional controls/witnesses support the split. Positive-font semantic assertions remain distinct from input calibration. The raw fix must prove its own browser repair before acceptance; the Sign fix explicitly depends on it. The original237-case diagnostic remains unchanged. Four standalone contextual-censorship theorems and three concrete false controls pass independent replay after rebuilding12 pinned dependencies. They explain why early normalization is not generally interchangeable with final normalization; native IEEE/unit-resolution refinement remains outside the proof. Canonical counts are unchanged. [Source audit](../css-sign-zero-font-audit-v1/REPORT.md), [held repair review](../css-sign-zero-font-repair-review-v1/REPORT.md), [successor](../css-sign-zero-font-repair-v2/REPORT.md).

A separate context-dependent `round()` lead now reproduces four opacity errors with two controls passing. Both browser84818 and root preservation11310 pass; the source audit distinguishes the deferred quotient path from constant remainder simplification. The one-file repair has passed independent source review and 1,976 extracted-helper checks. Its disabled 650-case comparison (14 landing cases and 636 existing controls) passes root static replay and independent controller review; actual source/build binding follows session8941 restoration. Six exact-arithmetic remainder/rounding support results now pass root and independent Lean replay, with the native floating-point reconstruction and projection still under investigation. Six separate standalone Lean support lemmas for the integer widening argument also replay successfully. These candidates remain unaccepted; no canonical coverage increment is claimed. Root replay of 4,151,200 finite native-helper strategy executions finds zero final-result differences. Inexact intermediate bounds and different nearest choices do occur, so universal refinement must prove final f32 projection rather than exact intermediate arithmetic. This sampled evidence is not browser acceptance or a universal IEEE proof. [Round diagnostic](../css-round-context-quotient-browser-runtime-v1/REPORT.md).

1. **Commit accepted work after verified restoration.** Session 51821 is terminal and all 35 saved originals, 58 source guards, nine installed WPT identities, HEAD/index and rebuilt binaries passed root verification. The authorized signed retry, session 36027, terminated with exit 128: 1Password failed to fill whole buffer. HEAD, all 925 staged payloads and all 419 restored-state pins are verified preserved. No unsigned substitute or automatic retry is queued; continue native verification while retaining the signing failure record. On success, bind each next research/native recipe to its actual signed parent; on a 1Password failure retain staged work and receipts. Do not disable signing, push, or mix research into native fixes. The accepted queue is 106–118;117/118 are installed with root preservation verification.
2. **Install accepted117/118, then continue counter leads.** The counter-marker and integer-rounding repairs passed their isolated213-subtest/two-reftest comparison, root restoration audit and independent review. Keep their separate Gecko/WPT patches and preceding research commits. The unchanged sign237 diagnostic and independent review are complete. The installation includes the prior installed-stack tests and full comparison controls; it passes with complete root source/index/test preservation. Installation result review also passes; bind the next native campaign to this verified state. Counter grouping and automatic-initializer arithmetic remain separate unaccepted proposals. Independently replayed ordinary-increment overflow proofs/helper checks still need browser reproduction and full native validation. The HTML mapped-marker alias and start-boundary leads remain source/helper findings, with no additional accepted bug. Preserve rejected baseline97100 and its narrow classifier correction as historical evidence; do not rerun it as a current acceptance gate.
3. **Validate separate color missing-state repairs, then resolve the powerlessness comparison.** Bare relative-keyword substitution and remaining-analogous-set carry each have an independent one-file Rust patch and 16-case WPT. The latter matches the Lean relation in 57,600 extracted-helper states, with 4,000 old-helper mismatches; this is not browser evidence. The separate relative-origin acquisition repair C now has two-file source review and14 math/control WPT cases. Its individual-analog behavior is independent of A; full remaining-set handling needs B. The disabled five-phase successor has passed independent review (4,601 cases across nine files, 37 rejection controls): baseline, A, B, C, A+B+C, using exact composed source maps. Bind only to a verified actual epoch; preserve individual acceptance decisions. Full conversion arithmetic remains outside the channel model. **Powerlessness:** Keep the full 1,559-case roster and original oracles. Review and test source LCH/OkLCh preparation without changing same-space values or original missing-component carry. Investigate 14 numerical hue failures using stored-channel precision and independent conversion references; separate the 32 preexisting relative missing-hue failures from source-boundary failures. Keep original tolerances and review changed failures individually. Any accepted successor must address the two lost passes and preserve its required improvements. Remove only newly repaired expected-FAIL metadata and rerun final metadata-aware validation before preparing its native commit.
4. **Extend formal coverage and implementation connections.** Preserve canonical source fingerprints and staged work. Keep source/spec mapping, mathematical model proofs, executable cases and native correspondence separate. Continue provider completion/ownership, parser progress, mutation histories, animation provenance and the versioned whole-CSS requirements ledger. Counter provenance laws are now integrated as implementation support; they do not increase normative CSS coverage. Use the [closure checklist](FORMAL-CLOSURE-CHECKLIST.md) and [whole-CSS assessment](../css-whole-spec-completion-strategy-v1/README.md). Original Bloom milestones 1–6 remain accepted only within their recorded scope.
5. **Complete ancestor-overflow reasoning before a repair.** Existing native traces and bounded snapshots establish lost coverage and missed pixels in two extreme-coordinate cases. Resolve coverage propagation/reset, invalidation, clipping and safe query-coordinate transport. The normative range boundary and any security impact remain unestablished. [Causal analysis](../css-ancestor-oof-causal-analysis-v1/REPORT.md), [repair design](../css-ancestor-coverage-repair-design-v1/REPORT.md).
6. **Resume baseline/fragmentation at its unresolved boundary.** Keep accepted fix 111 intact. The composed flex candidate remains rejected by its nested last-baseline regression; complete wide-coordinate publication and consumer transport before activating it or the ordinary-size margin-edge repair. Preserve the recorded 4,122-case core suite and inspector/reversal/margin/reftest obligations. [API inventory](../css-wide-baseline-api-inventory-v1/REPORT.md).

This snapshot is historical. The current status and execution queue at the beginning of this document supersede its counts, source state and pending gates.

## Earlier 24 October update notes (historical)

Color comparison update (2026-10-24): candidate rejected by the full 1,559-case comparison. Baseline1264PASS/295FAIL becomes1284PASS/275FAIL, with all16 landing cases passing but two prior-pass regressions and48 changed retained failures. Session51821 is restoring/rebuilding the original tree. Investigate source powerlessness and missing-channel/conversion effects before any successor acceptance; keep test oracles intact. The accepted count remains116.

Counter sentinel successor (2026-10-24): landing-v2 covers both geckolib constructors and preserves raw HTML-mapped values. Independent source review passes; the original one-file candidate remains held. Next gates are scoped provenance-model review, full Gecko compilation and the 53-subtest/two-reftest comparison. The separate mapped-MIN reset lead is unobserved and unaccepted.

Counter library integration (2026-10-24): full canonical verification passes 11,645 declaration audits and 12,224 executable cases. The 24 counter results and six examples are now registered; all prior results, 3,084 unrelated files and the nested index are preserved. Arithmetic bounds remain implementation support, not additional CSS coverage. See `artifacts/css-counter-library-integration-v1/REPORT.md`.

Counter sentinel repair update (2026-10-24): the reproduced bug is unchanged, but the one-file candidate is on hold. `Servo_DeclarationBlock_SetCounterResetListItem` and `Servo_DeclarationBlock_SetCounterSetListItem` also construct the specified value; trace their HTML-list inputs and revise all producers before compilation. Preserve the original evidence and keep this candidate out of the accepted count.

Updated 24 October 2026. Work stays local; the user owns pushing.

## Earlier checkpoint details (historical)

Fix116 is accepted after the standalone hidden-embedder comparison, complete restoration and independent review. Total116:105committed+11pending signing. Its working-stack installation completed in session39391:101PASS across12files, build/lint0, root live verification passed in session64491. Five native overlays preserve114/115, and all nine installed-test identities are recorded. [Acceptance](../css-svg-hidden-embedder-acceptance-v1/REPORT.md).

Counter grouping and color conversion are reproduced browser defects, not accepted repairs: four failures with four and twelve controls passing, respectively. Both diagnostic runs preserve source/index/binary/test identity. The color candidate, runner and actual installed116 binding have independent review. Its normalized1,559-case comparison is running in session51821; every original source must be restored and the original working stack rebuilt before accepting results. The counter model has twenty independently replayed results and five rejected false claims, now also reviewed by root. Separate automatic-initialization arithmetic safety from element grouping before preparing native commits. The calculated-value counter sentinel bypass is now reproduced: four calibrated failures and four controls pass on the installed116 build, with full preservation verified. Its one-file producer repair and23-case landing WPT have source review; native compilation and paired comparison remain pending. Arithmetic and grouping patches are split, with four independently replayed arithmetic laws and an explicit grouping dependency on the arithmetic layer.

The hidden-embedder standalone comparison completed locally (session83213 exit0): normalize all30 pending native edits to HEAD90, test the five-path candidate against24 landing cases and28 controls, then restore all33 saved inputs and rebuild the original stack. Source and runner reviews pass. Baseline build/lint pass;52 cases complete with32 PASS/20 FAIL. Candidate build passes and all52 cases pass, preserving all28 controls. Eight repaired visible cases overlap114; twelve hidden cases extend provider behavior. Root independently recounted raw outcomes and phase source/binary joins. Original-stack restoration build and root source/index/binary/test-identity verification pass; final independent result review passes. This supports accepted fix116. [Runtime](../css-svg-hidden-embedder-comparison-runtime-v1/STATE.json).

Two breadth leads remain unaccepted: converted powerless hue thresholds (16-case probe, nine-result rational rotation model independently replayed, with nine finite extracted Rust helper checks) and element grouping during reversed-counter initialization (eight-case probe covering duplicate sets, duplicate increments, cancellation, and Ahem-calibrated controls). Neither changes accepted fix or canonical coverage counts. Both browser diagnostics completed with calibrated failures and preserved the restored epoch before116 installation.

The cross-document provider model passes independent Lean replay: nine scoped result audits and two rejected false claims. It separates request, embedder completion and publication, and prevents stale generation/revision certificates from establishing readiness. Completion correctness and the CSS-required viewport remain explicit supplied premises; no native refinement or canonical coverage increase is claimed. [Root review](../css-svg-length-cross-document-provider-root-review-v1/REPORT.md).

The eight-case hidden-iframe follow-up reproduces four calibrated viewport-unit mismatches: hiding a fixed 240x120 iframe changes 10vw/10vh from 24/12 to 30/15; the same fallback-compatible values appear after resizing to 460x260. A subsequent host/iframe/child geometry query sequence recovers the expected values; the responsible query is not isolated. Four visible/px controls pass. Session96209 exits0 with source/index,399 resource/binary roles and eight installed tests preserved. Independent result review passes. No repair is accepted; next prepare a targeted provider-readiness fix and extend the explicit completion/publication model. [Evidence](../css-svg-length-hidden-provider-fallback-runtime-v1/REPORT.md).

The declarative specification assessment now supports the expected dimensions under the stated ordinary-iframe and HTML rendering premises. It supersedes the earlier INCONCLUSIVE missing-flush-call-edge rationale without changing the sealed historical diagnostic. Native fallback attribution remains unobserved. [Assessment](../css-svg-length-hidden-provider-root-assessment-v1/REPORT.md).

Expanded fix114 is accepted and installed. The isolated comparison improves35 PASS/16 FAIL to51 PASS, preserving all26 controls. Original-stack restoration and independent comparison review pass. The combined working-stack installation passes all25 main cases across three WPT files, with build/lint0 and root preservation checks; independent installation review passes. The standalone patch contains two Gecko files and three WPT files. Total remains115:105 committed and10 pending signing. [Installation](../css-svg-length-readiness-install-runtime-v1/REPORT.md).

The extended flush-policy model has23 independently replayed results and four rejected false claims. It proves conditional freshness and exact unit-classification changes given successful provider completion. Native hidden readiness, lifetime and IEEE arithmetic remain open. The preceding research and standalone native commit recipes are finalized, with signing parents still unset. The hidden-iframe follow-up exposes an unmet provider-completion obligation; see the current checkpoint above. It is not a new accepted repair. [Model review](../css-svg-length-extended-flush-root-review-v1/REPORT.md), [provider audit](../css-svg-length-hidden-provider-audit-v1/REPORT.md).

- **Fix115 accepted:** three SVG quarter-millimeter constants repaired; isolated26 PASS/8 FAIL→34 PASS, preserving18 controls. Both builds, original-stack restoration and independent review pass. Four finite Lean results check49 corrected binary32 factors against exact CSS ratios. One Gecko file plus two WPT files; working-stack installation passes build/lint and all16 cases. Signing pending. Current total105 committed+10 pending. [Acceptance](../css-svg-absolute-factor-acceptance-v1/REPORT.md).

- **Prior15-case fix114 scope:** two Gecko files and two WPT files; final15 cases and lint pass. Normalized viewport comparison23 PASS/4 FAIL→27 PASS and separate font comparison2 PASS/4 FAIL→6 PASS have independent review. Counts remain105 committed+9 pending. [Expanded acceptance](../css-svg-length-conversion-acceptance-v2/REPORT.md).

- **SVG conversion discovery and proof:** source/browser analysis reproduced stale source and destination bases;14 independently reviewed rational-model results specify current-context value preservation. These results are integrated in the canonical library, whose validation passes11,621 declaration audits and12,218 executable checks. Native freshness, IEEE arithmetic and complete CSS/SVG refinement remain outside that proof. [Canonical integration](../css-unit-conversion-integration-v1/REPORT.md).

- **Fix113 accepted:** hidden SVG viewport matrix queries, exact native+eight-caseWPT patch. NormalizedHEAD90 comparison32PASS/2FAIL→34PASS;26 controls and8 availability observations preserved, full restoration and independent review pass. Installation passes build/lint and all8 integration cases, preserving the earlier26 native edits and925 staged paths. Separate research/native commit recipes are finalized; signing remains pending. Counts105committed+8pending. [Acceptance](../css-hidden-svg-matrix-acceptance-v1/REPORT.md).

- **SVG matrix standalone comparison restored:** normalizedHEAD90 gives32PASS/2FAIL; changing only SVGGraphicsElement.cpp gives34PASS. All26 existing controls and8 availability observations are preserved. Pending107 is absent. Session85899 exits0; all27 original source bodies,355 roles,925 staged paths and both112 test identities are restored. Full independent result review precedes acceptance/installation. [Comparison](../css-hidden-svg-matrix-comparison-runtime-v1/REPORT.md).

- **Bounded rendering evidence:** nine240×200 snapshots complete; the two large-coordinate hit-miss cases show the parent instead of the leaf, while all seven ordinary/reset/alternating rendering controls pass. Headless drawSnapshot evidence is distinct from presented compositor pixels. Session90235 exits0, all339roles and source/index/test ownership are preserved, and all nine profiles are removed. Independent result review and independent full-image decoding pass; accepted count unchanged. [Rendering evidence](../css-ancestor-paint-pixel-runtime-v1/REPORT.md).

- **Ordinary-size hidden SVG matrix lead reproduced:** all8 cases calibrate and repeat; six controls pass, while hidden viewBox-dependent getCTM/getScreenCTM retain scale1 after a100→200px host resize. Subsequent matrix observations after the twin/host/style/getBBox sequence and later layout/reveal match scale2; these are not independent recovery trials. Session71193 exits0 with49sources/337roles and index/native/test ownership preserved. No repair accepted; prepare minimal native/WPT proposal and isolated comparison. [Reproduction](../css-hidden-svg-provider-runtime-v1/REPORT.md).

- **Expanded fix112 accepted and installed:** the170-case comparison improves152 PASS/18 FAIL to162 PASS/8 retained FAIL. All40 regression cases pass, exactly10 failures are repaired, and all130 controls preserve their outcomes/diagnostics. Full restoration and independent review pass. One four-file Gecko/WPT patch preserves distinct offset/scroll and client rounding policies; counts remain105 committed plus7 pending. Installer session9196 adds only the client header/new8 test; build/lint and all40 integration cases pass, with48source guards,336pins and925staged paths verified. [Acceptance](../css-cssom-integer-geometry-acceptance-v1/REPORT.md).

- **Prior narrower fix112 acceptance:** the consolidated integer offset/scroll conversion repairs eight failures; all 32 new cases pass and 109 controls are preserved. Terminal restoration and independent review pass. Working-tree installation completed (session 54811): build and all 32 integration cases pass; native signing remains pending. Its final two-item research/native commit queue is prepared with unbound signing parents. Counts are 105 committed and seven accepted pending. [Acceptance](../css-cssom-offset-scroll-acceptance-v1/REPORT.md).

- **Signing retry failed:** session 51872 again returned `1Password: failed to fill whole buffer`; no commit was created. HEAD, all 925 staged paths, index bytes and native diff are unchanged. The 13-item queue through fix 111 remains prepared; stop signing retries until the signer is available, while validation proceeds. [Signing receipt](../css-hidden-query-signing-execution-v2/ROOT-FINAL-CHECK.json).

- **Rounding comparison and scroll reproduction complete:** all 24 offset precision tests pass, repairing six failures; 80 controls preserve 76 PASS and four expected FAIL. Original source/build restoration passes independent review. The eight-case scroll probe confirms the same conversion error in scrollWidth/scrollHeight, with exact calibration in all 32 phases, recovery in all eight cases and unchanged client controls. Consolidate these as one defect family. The expanded comparison completed successfully (session 64175): 53 PASS/8 FAIL fresh baseline, 137 PASS/4 expected FAIL candidate, with the 80 historical baseline controls authenticated and full restoration verified. [Offset comparison](../css-cssom-integer-rounding-candidate-runtime-v1/REPORT.md), [scroll reproduction](../css-cssom-scroll-client-browser-v1/REPORT.md).
- **Rounding repair preparation:** the Element-local candidate passes2,100,046 actual-header sanitizer checks, and21 arithmetic theorems pass independent Lean replay. Eight additional strict browser size calibrations expose the same conversion error in offsetWidth/offsetHeight (6matches/2mismatches;8recovery matches). A single24-case WPT draft covers positions and sizes. The candidate browser run succeeds with the native portions of fixes 102/103 reversed; root restoration checks and independent terminal review pass. [Helper evidence](../css-cssom-integer-rounding-repair-helper-v1/REPORT.md), [proof review](../css-cssom-integer-rounding-model-review-v1/REPORT.md), [size reproduction](../css-cssom-integer-size-browser-v1/REPORT.md).
- **New integral CSSOM rounding reproduction:** all16 browser calibration/stability checks pass; offsetLeft/offsetTop return ±8388610 for exact ±8388609 geometry in four cases. Same-DOM margin reset recovers all16. Actual-header helper independently reproduces the conversion defect for supplied native inputs. No repair accepted. Next: narrow Element conversion repair, paired WPT and observer controls. [Browser evidence](../css-cssom-integer-rounding-browser-v1/REPORT.md).
- **Overflow coverage proof and trace preparation:** 24 conditional Lean results pass independent replay. The reviewed trace proposal snapshots final ink before storage mutation; the native run now captures9,049 events with every value in the96-row DOM payload unchanged. Both temporary sources and the working build are restored; root preservation checks pass. Independent runtime review passes. Interpretation directly ties relative overflow loss to native query rejection; absolute admission already has an empty query rectangle, so the earlier out-of-flow decision remains to trace. [Coverage review](../css-ancestor-overflow-coverage-review-v1/REPORT.md), [trace review](../css-ancestor-cancellation-trace-review-v3/REPORT.md).
- **Hit-testing coverage lead remains unaccepted:** all96 observed leaf rectangles calibrate and repeat, while18 large-coordinate stages miss the leaf. Native tracing now directly connects relative overflow loss to rejection. Absolute grouped cases arrive with an already-empty query, and the reviewed supplemental trace targets the earlier OOF marking and direct child union. CSS numeric-limit and detailed-hit-testing rules leave the normative verdict INCONCLUSIVE. Preserve clips and safe newly admitted coordinate arithmetic in any repair. [Measured trace analysis](../css-ancestor-cancellation-trace-analysis-v1/REPORT.md), [supplemental audit](../css-ancestor-cancellation-oof-trace-proposal-v1/AUDIT.md).
- **Executable exact-coordinate preparation advanced:** the source-order root continuation passes 2,418 sanitizer cases and seven Lean results with independent replay. The persistent-origin model adds 37 independently replayed results for admitted transitions, sequence invariants and rollback. A source-shaped observer prototype passes 425 UBSan checks and independent source review. These remain research artifacts: native adapters, rounding and complete rendering-reader closure are open. [Root continuation](../css-inline-placement-root-continuation-review-v1/REPORT.md), [state proof](../css-frame-origin-state-model-review-v1/REPORT.md), [observer review](../css-frame-origin-observer-review-v1/REPORT.md).
- **Nested inline range and actual-input models:** the 26 range/depth results and 24 new metric-aware results pass independent Lean replay. The latter bind all 64 retained native records, including wrapper baseline 30 and the rounded second margin 600006016 app units. Corrected positions remain hypothetical; root translation and ancestor origins stay symbolic. An artifact-only C++ placement plan now passes 6,525 cases under undefined-behavior/integer sanitizers, including those 64 inputs, and identifies unrepresentable publications explicitly. Independent replay passes; the root continuation must still preserve default-zero enlargement. An exact-origin state prototype passes 166 UBSan checks and independent source review; the transport audit pins 17 source files and identifies size-only/RTL mutation, scroll/shadow dispatch and final CSS-int conversion requirements. The next research checkpoints complete root continuation and synthetic observer transport; native adapters and overflow/paint/hit-test consumers still require closure before activation. No new fix is accepted. [Input model review](../css-baseline-native-input-model-review-v1/REPORT.md), [placement plan](../css-inline-placement-plan-v1/REPORT.md).
- **Exact baseline synthesis preparation passed independent runtime review:** 131 UBSan helper cases, successful inactive API compilation, successful restoration. No consumer is enabled and no new fix is accepted. Nested observation is terminal with 8/32 calibrated rows: all 24 nested cases fail the zero-width-wrapper assumption (observed offsetWidth 1px). Preserve that failure and attribute it before changing the fixture. Eighteen new conditional coordinate-representability theorems passed independent Lean replay. The source audit attributes the width to vertical font metrics, and a 16-case browser probe confirms populated references are needed (empty wrappers measure zero). The separate reference-calibrated diagnostic now passes all 32 calibration/repeat gates: 16 vertical-rl controls align, and 16 vertical-lr cases mismatch by 100px at both ordinary and large sizes. This is working-tree reproduction, not repair acceptance. The scoped nested arithmetic bound and actual-input binding are now complete; exact frame-origin storage and consumer changes remain open. Preserve the original failed calibration and withhold its zero-metric origin predictions. [Review](../css-exact-synthesis-runtime-independent-review-v1/REPORT.md).
- **105 native fixes committed; seven accepted repairs await signing.** Fixes106–108 cover hidden column-provider admission, block-line marking and Grid-child marking. Fix109 covers current-owner floats; fix110 covers skipped MathML subtrees. Each native commit contains only its repair and relevant WPT; research precedes it. [Ledger](BUGFIX-COMMITS.md).
- **Fix101 requires fix104 or an equivalent repair.** Retain the containing-block cache key and do not cherry-pick101 onto an unremedied base.
- **Column/block/Grid validation is complete:** their isolated landing partitions pass, together all79 cases pass, and the installed working tree passes with older prototypes preserved. The broader700-case comparison had no calibration failures or additive regressions; table continuation coverage remains unreached. [Acceptance](../css-hidden-query-landing-acceptance-v1/REPORT.md), [integration](../css-hidden-query-installed-v1/REPORT.md).
- **Float109 is accepted:** exact main WPT4 PASS/4 FAIL becomes8 PASS with only the float repair on committed HEAD. All12 standalone campaign cases pass, the earlier composed95 cases pass, and480 stale benchmark geometry reads become zero. Restoration and independent reviews pass. The native patch and eight-case WPT are packaged separately from calibration/tooling; it is now installed with MathML110; all91 combined landing subtests pass. [Acceptance](../css-hidden-float-acceptance-v1/REPORT.md).
- **Cost evidence is bounded:** first correct recovery does more work than stale baseline answers. Float clean-query median changes stay within1ms in this coarse sample; five measured rounds do not establish a general performance bound. Grid-specific cost remains unmeasured. [Float timings](../css-hidden-float-standalone-results-review-v1/TIMINGS.md).
- **Formal query-readiness models remain conditional:** provider admission, skipped-line/path composition and float ownership have kernel-checked results. Native lifecycle, stable frame ownership, publication and provider completion remain explicit obligations. Existing producer lemmas already establish ordinary IS_DIRTY closure; partial clearing at the next owner pass is the useful next refinement. [Proposal](../css-hidden-float-closure-next-step-v1/PROPOSAL.md). Owned float compiler products were removed.
- **MathML110 is accepted after isolated/integration and independent review:** unchanged and marked controls both give6 PASS/2 FAIL. The trace captures clean row/leaf state through skipped reflow and zero publication, then first/repeat clean-target rejection. All34 source guards and restoration pass. The one-line candidate improves the independent four-case WPT from2 PASS/2 FAIL to4 PASS; restoration and staged-payload verification pass. The integration run passes all299 subtests across18 files (87 known controls and212 ordinary MathML subtests), and restoration is verified. The outer-block cases remain interaction controls. [Trace](../css-hidden-mathml-trace-runtime-v3/REPORT.md), [proposal](../css-hidden-mathml-repair-proposal-v2/README.md).
- **Signing remains the commit blocker:** the latest retry failed with the1Password buffer error. The exact925 staged research paths remain preserved during experiments. The next signing sequence keeps evidence before separate native/WPT commits106–111. No try, push or external submission.

- **Portable observation infrastructure is integrated:** ProviderObservation is exported and its five existing proofs are registered in the central audit. The unchanged standard verifier passes11569 theorem audits,12172 executable cases and both rejection controls; root authenticated all2100 source fingerprints and six command receipts. The cohesive four-file library change is staged in its separate repository, pending signing. Specification/native adapters remain open; no added CSS coverage is claimed. [Package report](../css-provider-observation-package-check-v1/REPORT.md).
- **Further hidden-float searches:** six concrete recovery histories pass, and a bounded pushed/overflow audit finds no source-backed DOM witness. Close these searches without adding a fix; this does not prove all ownership histories. [Audit](../css-hidden-float-fragment-owner-audit-v1/REPORT.md).
- **CSSOM policy question:** seven calibrated observations match positive-area rectangle inclusion; four mixed lists differ from a literal OR reading of the current draft predicate. Both policies now have a four-theorem model with independent root replay and all seven finite fixture values checked. The historical2016 CSSWG edit explicitly intended Gecko's positive-area behavior; treat the literal OR difference as a wording concern, not a native bug. [History](../cssom-bounding-box-history-v1/REPORT.md). [Measurements](../cssom-bounding-box-browser-probe-v1/REPORT.md).

- **General rectangle hull proof passes independent root replay:** union-containment equivalence, least enclosure for any nonempty list, and least enclosure of the selected positive-area rectangles. Exact integer model only; native arithmetic and fragment production remain open. [Root review](../cssom-bounding-box-hull-root-review-v1/REPORT.md).

- **Isolated fragment candidate has regressions and is not accepted:** the paired4122-subtest raw results improve3109 PASS/1013 FAIL to3309 PASS/813 FAIL. The targeted144 cases and all32 dynamic stages now pass;202 failures improve overall. Two formerly passing extreme-size cross-packing cases now fail, and four existing failures change their first diagnostic. Keep these gates intact and investigate the packing/fragment arithmetic interaction. All27 WPT reftests and five Mozilla reftests pass both phases; all390 accepted-fix checks remain passing. The controller rejected the candidate and root verified restored sources/index/tests/build. Trace the earlier cross-position producer and push/reflow decision before revising the patch. [Comparison](../css-flex-fragment-isolated-runtime-v2/REPORT.md).
- **Packing trace completed and the working tree/build are restored:** the original 40 outcomes remain identical; four selected cases reproduce 1 PASS / 3 FAIL with 305 native records and five DOM snapshots. Three threshold items enter first-fragment reflow with negative cross positions and zero consumed/cumulative values. Native heights remain correct; pinned observer endpoint clamping accounts for the zero DOM heights. Root verified HEAD/index, sources, tests/resources and rebuilt binaries. [Trace](../css-flex-fragment-packing-trace-runtime-v1/REPORT.md). The reviewed six-path exact producer/fragment proposal passes the paired core comparison (session70987): 3109 PASS/1013 FAIL becomes3507 PASS/615 FAIL, with398 improvements, no lost passes and no changed retained-failure diagnostics. All144 main cases,32 dynamic stages and40 cross-packing fragmentation cases pass; all27 WPT reftests and five Mozilla reftests pass both phases. Restoration/rebuild and root source/index/test/resource/binary verification pass; no acceptance yet. [Core result](../css-flex-fragment-composed-runtime-v1/REPORT.md). The follow-on run (session72617) rejects the composed candidate: inspector286/316 becomes316/316 and reversal49/64 becomes64/64, but the new extreme last-baseline row loses its match. Baseline tops100/100 become approximately−17.9millionpx with100px difference; all inputs calibrate and repeats are stable. Other3 last-baseline rows and the six margin-row outcomes are preserved. Restoration/rebuild and independent review are complete. The native trace captured419 events and the complete four-row browser payload equals the uninstrumented candidate byte-for-byte. Distinct exact last-end offsets−4079994000/−4079988000 both project toINT32_MIN; the actual natural-baseline consumer converts them to negative narrow values. The controller and independent root verification completed successfully; the working sources, index, tests/resources and rebuilt binaries are restored. Preserve exact values through parent grouping and placement; a wide subtraction alone cannot recover the lost distinction. [Trace diagnosis](../css-flex-last-baseline-trace-analysis-v1/REPORT.md). The implementation boundary must include concrete shared consumers and a finite-range/export policy. Source ordering confirms baseline lookup intentionally uses the current completed child frame after a BSize-cache hit; do not require the baseline snapshot to match the older measurement key or add speculative reflows. Performance remains pending. Preserve old exact/nonwrapping arithmetic; defined unsigned wrapping is intentionally corrected. Baseline consumer bounds and performance remain open. [Proposal](../css-flex-fragment-composed-proposal-v1/REPORT.md).
- **Cache scheduling audit excludes one suspected path:** ordinary uninterrupted dirty flex block-line reflow prevents skipPull and propagates reflow through subsequent columns. Root authenticated the16 source excerpts against committed HEAD. Exceptions and full current-prefix correspondence remain open; this is neither a new bug nor a universal freshness proof. [Audit](../css-flex-fragment-ordered-refresh-audit-v1/REPORT.md).
- **Ordinary flex cost fixture is prepared:** eight32/256-item positioning/resizing configurations, exact geometry calibration, rotating samples and separate clean reads. The first browser calibration stopped before measured rows. A failure-message-only diagnostic then confirmed a correct clean checksum with0ms elapsed over4096 reads. Source/binary roles and cleanup verified; the reviewed65536-read clean batches now complete80 measured rows,196 progress receipts and5253120 reads with zero geometry mismatches. Source roles and cleanup pass. This is fixture calibration only; possible concurrent Lean compilation precludes treating these numbers as an isolated performance result. Paired timings remain pending. [Fixture](../css-flex-ordinary-cost-v2/README.md).

- **Standalone baseline alignment model passes canonical checks and independent review:** the fitting supplied-provider fragment and per-occurrence extension add31 audited results and28 executable cases, bringing the checked library to11600 audits and12200 cases. Placement is characterized independently, and recomputed group-relative positions are preserved exactly when baseline representation errors are constant across members. Native refinement and provider lifecycle remain open. The per-occurrence origin conversion theorem also passes, permitting identical inputs to choose distinct origins. Root authenticated all2102 live source hashes and six command receipts; independent review passed. The staged ProviderObservation package is unchanged. [Model](../css-baseline-alignment-implementation-v1/REPORT.md).

- **Portability correction:** the compiler probe rejects raw builtin `__int128` for i686, but the actual fragment helper uses `absl::int128`. The earlier inference that the candidate therefore fails portability was incorrect; the actual fallback covers the candidate operations and retained software-backend tests use headers identical to HEAD. Keep Abseil for this wider cancellation domain; checked64 is not an equivalent replacement. [Audit](../css-flex-fragment-portability-audit-v1/REPORT.md). The separate shared interface now uses CheckedInt64 with explicit binary-operation boundaries, preserving range failure rather than promising fused cancellation. [Correction](../css-wide-coordinate-portability-correction-20261023.json).
- **Cross-consumer diagnostics are calibrated on the restored working build:** all12 rows have stable input/output copies; all six ordinary cases and three large-first cases match. Direct flex, block-wrapped flex and grid large-last rows each yield200/100px against the fitting-group100/100px hypothesis. This is neither a HEAD/candidate comparison nor a new accepted defect. Source/index/resources/build and owned cleanup remain unchanged. [Fixture and receipts](../css-baseline-cross-consumer-probe-v1/README.md).

- **Wide-query interface preparation is concrete:** the seven-path HEAD patch preserves narrow providers/synthesis and adds explicit value/absent/not-ready/out-of-range results. Source review and30 actual helper cases under UBSan pass; no wide producers or existing call sites are enabled. Combined ASan+UBSan timed out without output and is not validated. Helper binaries/debug products were removed. The focused checked-operation proof also passes independent replay: seven local audits, one reused origin theorem, and three rejected false claims. This models exact checked results and explicit states, not compiler builtins, narrow synthesis or whole-frame correctness. [Proof and limits](../css-wide-baseline-checked-refinement-v2/README.md). The guarded full Gecko/API compile passed (session97678), and all32 saved originals were restored and rebuilt successfully. Root verified44 source guards,925 staged paths,61 existing tests and196 resources; independent result review passed. No runtime behavior is claimed from compilation. [Contract and evidence](../css-wide-baseline-interface-proposal-v1/CONTRACT.md).

- **Central baseline origin repair 111 accepted:** the clean HEAD/candidate comparison repairs all four new failures, yielding 12/12 in its own WPT and preserving all 204 existing outcomes plus the reference. All builds and restoration pass. Twenty-six Lean declarations replay independently; actual constructor/caller audits close the raised range concern for well-formed shipped layout with defined prior arithmetic. The Gecko+WPT patch is installed and awaits signing. Its local binary build and combined103-subtest/12-file suite pass; HEAD,925 staged paths, other native edits and the prior91 case identities are preserved. [Acceptance](../css-central-baseline-acceptance-v1/REPORT.md). The separate alphabetic/hanging edge lead reproduces 8 failures/40 passes and remains unaccepted. Its four-row range probe preserves the working build but rejects both large extent calibrations: requested styles apply, while CSSOM reports17,895,697.05px instead30,000,000px. The pinned DOM conversion exactly predicts both capped width and shifted left edge from the proposed native rectangle. A restored native trace now confirms BSize1.8b and margins−600m/+600m app units, with old helper outputs1.2b/600m for First/Last. The exact corrected logical point is2.4b, outside signed32; prior whole-execution definedness remains unproved. Choose a justified shared range boundary or complete exact consumer transport before accepting the edge repair. The existing DOM clamp is not a synthesized-baseline projection policy.

## Execution queue snapshot — 23 October (historical)


There are **105 committed fixes and nine accepted repairs awaiting signing**. Fixes106–114 are installed. The latest native build includes114; final test-scope validation passes15 cases, preserving29 modified native files,925 staged research paths and five installed WPT identities. [Current ledger](CURRENT-COMMITS.json), [grouped fixes](../css-fix-readout-20261023/README.md).

1. **SVG length conversion:** prioritize the independently confirmed absolute-factor table lead: three incorrect Q-related literals, six reproduced browser failures and six passing controls. The internal Q-target SMIL witness now reproduces two additional errors with independent review. Complete the minimal repair and isolated34-case paired native/browser validation. Expanded114 is accepted with unchanged native repair and15 WPT cases. Its preceding research and four-path native/WPT commit recipes are finalized; signing remains pending. The normalized viewport comparison, separate mixed-tree font comparison, successful installation and final-path tests remain distinct evidence. The forward-only zero-axis probe reproduces four calibrated getter discrepancies; independent result review passes, and interoperability/compatibility assessment remains before selecting any repair. No additional repair is accepted. [Acceptance](../css-svg-length-conversion-acceptance-v2/REPORT.md), [zero-axis decision](../css-svg-length-zero-axis-decision-v1/DECISION.md).
2. **Commit accepted fixes:** preserve the signed-commit workflow for106–114. Each fix gets preceding research and a separate minimal Gecko/WPT commit; bind the next parent only from an actual successful signed receipt. The last1Password signing attempt failed; do not replace signatures or mix the925 staged research files with native patches. [Fix112 package](../css-cssom-integer-geometry-commit-queue-v1/README.md), [fix113 package](../css-hidden-svg-matrix-commit-queue-v1/README.md), [fix114 package](../css-svg-length-conversion-commit-queue-v1/README.md).
3. **Formal library:** canonical validation passes11,621 declaration audits and12,218 executable cases after integrating the14 reviewed conversion results. Preserve supplied-factor, rational-arithmetic and nonzero-basis premises. Continue refining query readiness through ownership/list reachability, dirty-root barriers, helper/caller order, provider completion and metric publication. A separate18-result flush-tier bridge has independent review; it composes with conversion preservation under an explicit successful-provider contract and is not yet canonical. Counts are not CSS coverage percentages. [Conversion integration](../css-unit-conversion-integration-v1/REPORT.md), [observer integration](../css-hit-observation-integration-v1/REPORT.md).
4. **Ancestor overflow:** native tracing identifies coverage lost during union and grouped out-of-flow query clipping. Nine bounded rendering snapshots also show missing leaf pixels in two large-coordinate cases, with seven controls passing. Before selecting a repair, resolve persistent coverage propagation/reset, metadata-sensitive invalidation, real clipping and safe query-coordinate transport. Keep the extreme-range normative question open; no security impact or accepted repair follows from the snapshots alone. [Causal analysis](../css-ancestor-oof-causal-analysis-v1/REPORT.md), [repair design](../css-ancestor-coverage-repair-design-v1/REPORT.md), [rendering evidence](../css-ancestor-paint-pixel-runtime-v1/REPORT.md).
5. **Baseline and fragmentation:** the composed flex candidate remains rejected because of the nested last-baseline regression. Preserve accepted111 while developing the typed wide-query/conversion interface, narrow override dispatch, exact first/last baselines and connected flex/grid/inline/table storage paths. The [API inventory](../css-wide-baseline-api-inventory-v1/REPORT.md) identifies18 overrides. Inactive helpers have131 real-source UBSan assertions and a reversible nine-file compile experiment; no wide consumer is activated. The two-box oracle has16 passing controls and16 inverted failures, and15 scoped Lean results expose early projection loss. Close the nested frame-local publication boundary before consumer activation. Retain the4,122 core subtests, inspector/reversal/margin/last-baseline checks, accepted-fix preservation, reftests and later controlled cost comparison. The ordinary-size atomic-inline inverted Alphabetic/Hanging margin-edge lead already has40 PASS/8 FAIL browser evidence and its native export/inline consumer path is resolved. It still needs the wide-range export obstruction fixed before a global side-swap is safe; reuse the48-case test plus accepted111’s12 controls. Ordinary flex-margin controls pass.
6. **Broader CSS program:** continue parser progress and callback histories, custom-property/CSSOM lifecycle admission, animation provenance, cascade/cache ownership, and the standalone requirement ledger with versioned specification mappings. Follow the [closure checklist](FORMAL-CLOSURE-CHECKLIST.md) and [whole-CSS completion assessment](../css-whole-spec-completion-strategy-v1/README.md). Keep specification coverage, executable model results and Gecko refinement separate. The original Bloom milestones1–6 remain accepted only within their recorded scope; they do not certify subsequently changed native sources.

## Earlier checkpoints (historical)

The following entries preserve prior counts, holds and incomplete attempts. The current status above supersedes them.

- **Launcher update escape retained and cleaned:** installed Firefox158 completed
  the progress fixture but its updater relaunched the test profile outside the
  original group, causing profile cleanup failure. Root verified/stopped that
  exact-profile process and removed the profile; the original result stays
  rejected. Further comparison uses the local-built binary and an early update
  processing guard, without enabling unsafe automation preferences.
- **Compact tests isolate a column-query residual:** all50 proposed landing
  tests pass with both repairs. Four new col/colgroup cases still fail while
  separately constructed table/cell controls recover. The original-key principal
  comparison fixes14 cases; every pair has zero regressions. This was led by the
  formal model's explicit column-pruning barrier. Independent upstream reachability
  and a native repair remain open.
- **Absolute traces confirm dirty retention:** four clean entries commit zero
  geometry while staying clean before the repair, and become/stay dirty with it.
  The query-forcing gate itself is not logged. All12 instrumented cases pass with
  the repair and reproduce uninstrumented outcomes.
- **Combined cost remains unresolved:** three v2 runs complete84 batches each;
  first-query cost dominates, repeated-query medians are0ms at coarse resolution.
  The combined run returns no observation by75seconds, with clean verified
  termination. A Safe Mode startup message is a clue, not a proven cause.
  Controlled-startup/progress v3 will compare baseline/both consistently.
  The Firefox158 ordinary-block WPT attempt also failed startup and gives no
  correctness verdict; its temporary test/process group are cleaned.
- **Independent repair comparison passes:** 22 WPT files and 686 subtests yield
  41 baseline failures, seven with principal marking, 34 with absolute marking,
  and zero with both. All four pair comparisons have zero regressions; all three
  reftests pass. The combined timing run reported a cleanup permission error, so
  its timing result is rejected and planned traces did not run. Restoration
  and its rebuild passed, with all26 guarded sources and empty index verified;
  no native acceptance follows yet.
- **Next gates:** finish the controlled baseline/both timing comparison and
  trace column target/table-provider dirty bits. The formal subtree barrier now
  has a calibrated browser residual; ordinary-block reachability and a sufficient
  native repair remain unconfirmed. The compact tests and absolute traces above
  have completed, and source/build restoration passed.
- **Absolute sequence proof reviewed:** 23 new and 66 imported kernel results,
  6,144 rows per optimization and eight semantic mutants. Independent source/math
  review accepts the conditional component; native provider/lifetime obligations
  remain explicit. [Review](../css-hidden-oof-proof-review-v1/REVIEW.md).
- **Latest research signed:** compact runtime/traces `0f73c7d76ef6`,
  column diagnostics `0987b9e43a83`, startup diagnostics `c19121785fb5`.
  All exact blob/path/signature checks pass; native prototypes are preserved.
- **Uninstrumented hidden-flex WPT comparison complete:** all four builds and
  restoration passed. Each phase has 656 subtests and 15 files. The principal
  subtree repair fixes 34 failures with the current key and 18 with the original
  key, with zero regressions in either pair. One static-position absolute-child
  failure remains in both pairs; the original key also preserves eight deliberately
  reintroduced caption/padding failures. [Independent runtime review](../css-hidden-geometry-wpt-runtime-review-v1/REVIEW.md).
- **Subtree proof extends the direct-item model:** 36 new results plus 30 imported,
  6,144 extracted comparisons per optimization level, seven semantic mutants,
  and nine independent kernel checks. This establishes conditional marking and
  query admission, with actual native histories and layout recovery still open.
  [Independent proof review](../css-hidden-subtree-proof-review-v1/REVIEW.md).
- **Separate absolute-child repair under test:** source review supports marking
  its subtree before constructing reflow input. Next run compares neither repair,
  principal only, absolute only, and both, including leaf queries, actual
  fragmentation and non-block providers. Trace the absolute zero-output producer,
  then sample cost before native acceptance. Hidden containment establishes its
  own containing block; external-to-inner-flex tests must preserve that boundary.
  Both repairs remain unaccepted, and fix 101 remains on landing hold.
  [Absolute-child review](../css-hidden-flex-oof-independent-v1/REPORT.md).
- **Hidden-layout research signed:** reproduction `b04de6f7890c`,
  scoped model `b990b03e87d3`, experiment `54017a2b4c76`.
  The count remains 103 committed native fixes, with fix 101 on landing hold.
  [Commit checks](../css-hidden-geometry-commits-v1/COMMIT-CHECK.json).
- **Traversal v4 committed as fix 103:** `7309af28e360`.
  The paired 23-file/74-subtest run repairs both large untransformed-edge failures.
  The final check without DOMRect fix 102 passes all four own cases and preserves
  the historical keyed oracle. Independent review closes that dependency gate.
  Qualified performance acceptance retains the possible deep root-transform cost
  of about 10 ns/call; no broad no-regression claim follows. The source patch is
  installed and rebuilt after the hidden-geometry experiments. [Acceptance](../css-cssom-exact-traversal-acceptance-v4/REPORT.md).
- **Signing resumed successfully.** Six research commits precede the standalone
  native/WPT fix. Exact paths, evidence blobs, signature headers and native parent
  delta pass verification. The index is empty; all 20 other modified native files
  are preserved. Nothing was pushed or submitted.
- **Hidden-flex geometry bug reproduced in release Firefox 158.** Twelve of 240
  shrink/descendant stages return zero or stale dimensions. Exact committed-source
  isolation preserves all 32 failures in the earlier fixed-size probe. Four
  instrumented variants produce 44, 12, 4 and zero mismatches across 400 stages.
  The broader skipped-children repair remains unaccepted pending the remaining
  fragmentation/provider boundaries and cost/dependency review. Uninstrumented
  WPT and position/history results are recorded above.
  **Fix 101 is on landing hold:** its required containing-block key exposes the
  preexisting protocol bug more widely. Do not drop that key as a final repair.
  [Experiment](../css-hidden-geometry-measure-trace-v2/REPORT.md).
- **Hidden measurement model checked:** 30 Lean results, 768 extracted native/model
  comparisons per replay, six semantic mutants and nine independent kernel checks.
  Conditional direct-item recovery is proved; clean descendants and changed-key
  histories remain explicit countermodels. This does not verify the broader repair.
  [Scope and review](../css-hidden-geometry-proof-review-v1/REVIEW.md).
- **Ownership refinement accepted within its modeled scope.** Canonical and
  relocated Lean replay pass 74 audits and five semantic rejection controls;
  independent review adds seven kernel checks. Ordinary-array shape and owner
  separation suffice to preserve other modeled owners through selected cleanup.
  A full nested coherent fixture still frees the selected captured cache.
  Native decoding, installation coverage, callbacks and generation identity remain
  open. [Independent review](../css-primary-destruction-ownership-refinement-review-v1/REPORT.md).
- **Translation carrier proof committed:** `63bf6c30eef0`. Nine Lean
  results and six independent checks bound translations for admitted cumulative
  coordinates without a frame-count limit. Corrected fresh replay passes; the
  original replay harness failure is retained with an erratum. The native
  checked64 successor still needs final review, browser tests and performance
  checks. [Numeric checkpoint](../css-cssom-exact-traversal-bounds-root-replay-v2/REPORT.md).
- **Destruction callback audit committed:** `6e53130a808e`. Fifty of 51 selected
  definitions match the live tree; the remaining difference is the committed
  cache-key value field. Property destruction can precede the second primary-bit
  read, and SVG observer dispatch can be synchronous. Actual selected-path
  reachability and lifetime safety remain open; this is no new native bug claim.
  [Callback checkpoint](../css-primary-destruction-callback-root-v1/REPORT.md).
- **Primary ownership component accepted and committed:** producer
  `885c94769ed3`, review `2c441db9213b`.
  Root replay passes 40 audits over 26 bound definitions; independent review adds
  12 kernel challenges and seven integrity controls. This proves admitted stable
  histories and selected initialization, with actual destructor callbacks and
  heap representation still open. The live constructor has a retained generated
  cleanup difference; no broad indexed-source lifecycle transfer is claimed.
  [Root acceptance](../css-primary-bit-coherence-root-v1/ACCEPTANCE.json).
- **Traversal v2 browser checks pass; native repair remains held on cost.**
  Signed evidence `c29fd817ebc3`, runtime `3ec270d944da`. Actual builds and formatting
  pass. The 23-file/74-subtest comparison fixes both untransformed large-edge
  failures, with all four new cases passing and all other outcomes unchanged.
  Six timing runs show deep ordinary medians of 400 ns versus 300–350 ns in surrounding
  baselines; near-root transforms at 450 ns versus 350–400 ns. Quantization and fixed
  phase order limit interpretation, but root and independent review recommend
  holding this version. Source/build restoration completed; no integer candidate
  remains installed. [Actual experiment](../css-cssom-exact-traversal-runtime-v2/REPORT.md),
  [independent review](../css-cssom-exact-traversal-runtime-review-v2/REPORT.md).
- **Traversal v3 browser correctness passes; transformed cost remains unresolved.**
  All three builds pass. The 23-file/74-subtest comparison repairs two failures;
  all four new cases pass and the other 70 outcomes are unchanged. Six fresh
  timing processes contain 396 batches and 39.6 million measured calls. Ordinary
  deep-path medians are 310–320 ns against surrounding 310–330 ns baselines;
  transformed paths retain a modest unresolved cost trend. Fixed phase order,
  coarse timers and two processes per phase limit interpretation. Source and
  build are restored. V3 remains unaccepted; the superseding v4 checkpoint is above.
  [Runtime](../css-cssom-exact-traversal-runtime-v3/REPORT.md),
  [independent review](../css-cssom-exact-traversal-runtime-review-v3/REPORT.md).
- **Selected allocation footprint component has root and independent review.**
  Producer `505bbb00e328` passes 51 Lean audits and four semantic rejections.
  Four independent kernel witnesses expose representation and global-ownership
  boundaries. Selected role-correct deletion preserves primary coherence while
  a captured cache is freed; this does not establish a browser use-after-free.
  Capture and descriptor source audits found no actual same-owner free during
  the selected callback interval. A focused replacement audit likewise found
  no reachable destructor/table-mutation sequence. Payload decoding, global
  ownership, transitive callbacks and generation identity remain open.
  [Proof review](../css-primary-destruction-callback-proof-review-v1/REPORT.md),
  [capture audit](../css-flex-cache-capture-lifetime-audit-v1/REPORT.md),
  [replacement audit](../css-frame-property-replacement-reentrancy-audit-v1/REPORT.md).
- **DOMRect precision committed:** `c0e8c7fd1deb` preserves already calculated
  double coordinates. Its four-case WPT passes independently; selected existing
  regressions retain their outcomes. The bounded 26-audit numeric component has
  root and independent review, 53 native/reference cases per optimization mode,
  and 11 complete source bindings. Universal IEEE and full CSSOM claims remain open.
- **Historical v1 integer-translation hold:** correctness witnesses pass, but a deep
  transform-near-root microbenchmark repeatedly rises from 400 to 550 ns per call. The
  next design should carry exact translation through the existing traversal.
  Retain SVG/context/viewport/clipping guards and checked numeric bounds.
  [Performance decision](../css-cssom-rectangle-performance-runtime-v1/REPORT.md).
- **Full obligations continue:** numeric component acceptance does not close
  safe-origin F1–F12, allocation F1–F16/F11/F12, provider lifetimes or fragment
  observers. Signed table subtraction remains a separate investigation with
  no accepted native repair or established memory-corruption impact.
- **103 committed native/WPT fixes; no accepted repair awaits signing.** The
  14-fix queue is complete, including its 34 preceding evidence/proof commits.
  All 48 signatures and exact native parent deltas were checked. See
  [BUGFIX-COMMITS.md](BUGFIX-COMMITS.md) and
  [CURRENT-COMMITS.json](CURRENT-COMMITS.json) for management identifiers.
- **Earlier fixes:** leading-whitespace attribute origin (`ad608a212bd8`),
  trailing-whitespace token metadata (`bccea9c1fffc`) and escaped trailing
  whitespace (`fff2d758ef6b`). Each has a preceding evidence companion and
  a separate two-file native/WPT commit. All three also have signed standalone
  upstream alternatives; see the commit ledger. No isolated upstream runtime is claimed.
- URL native state/capture, ordinary batching, parser-priority winners, animation
  identity and primary parser-history admission are accepted within scope. Public
  parser wrappers and storage composition remain active.
- **Committed token-boundary repair:** registered-value token boundaries. The corrected 37-case
  baseline has 27 PASS / 10 FAIL across fonts, margins and token serialization.
  The repaired build passes 308 cases across 18 WPT files. Native/WPT review and
  standalone source packaging and bounded proof review pass. It is committed with its preceding evidence companion.
- **Committed animation repair:** animation publication converts guaranteed-invalid values to
  registered initial values. The three-file repair fixes ten reproduced failures;
  the 343-check matrix has 341 passes and two unchanged expected failures. Six
  added lower-priority suppression/valid-empty controls also pass. Independent
  native/WPT review, lint and standalone source packaging pass, with root replay.
  Root and independent review accept the v2 bounded Lean companion: 81 audits,
  including 42 new results, plus 14 independent boundary challenges. Separate signed
  evidence/native commits are complete.
- **Whitespace repairs committed:** the leading-origin bounds panic also
  reproduces without script in installed Firefox 158. Its 26 new tests pass;
  the accepted origin proof has 88 audits. Trailing token metadata repairs
  28 failures in a 40-case WPT. Escaped whitespace repairs 16 failures in a
  20-case WPT. Their shared terminal-span proof has 37 audits and 23 independent
  challenges. Tokenizer, EOF, native correspondence and caller premises remain
  explicit; these are bounded components, not complete serialization proofs.
- **Backslash/newline repair committed:** `246f1ff43250` retains required
  newline whitespace after an actual backslash delimiter. Its final WPT has
  30 passes against a baseline subset with 16 failures and 14 passes. Root and
  independent proof review accept 53 audits plus 15 independent kernel challenges;
  lexical projection, EOF compatibility and reference bounds remain explicit.
  Signed standalone upstream alternative: `95b6a9b03c1c`.
- **Attribute-taint follow-up:** both bounded reviews are complete. Actual
  prohibited local image requests remain established for fix80; no new unknown
  value disclosure was found. Thirty-six calibrated registration observations
  preserve raw-string taint. Link-parameter provenance loss is source-confirmed,
  but current transport/resource restrictions block the proposed HTTP path.
  Epoch-aware provenance and link-env provider contracts remain open.
- **Anonymous-box provider:** root accepts the bounded 42-audit component after
  fresh replay and source review, with six model mutants and 50 passing browser
  states. Actual reflow-input/frame ancestry, numeric providers and dynamic
  reconstruction remain open. Completed root compiler outputs were removed.
- **Parser controls:** the earlier seven wrapper results remain accepted.
  Nested-control v3 now has root and independent scoped acceptance: 39 audits,
  59 modules, 18 cases and 91 native/model snapshots in debug and release. Three
  native mutants differ in 10, 25 and five rows; five additional root kernel
  challenges demonstrate progress and callback-control limits.
  The revised capsule rejects pre-import shadowing and nonclosed file rosters.
  Universal callback grammar, native termination, full LinkParameters and
  whole-program annotation correspondence remain open.
- The [triage proposal](../css-bugfix-triage-20261019/README.md) groups the first 80
  committed fixes with exposure limits and standalone alternatives. A separate
  registered-animation WPT calibration correction is committed separately;
  it does not increase the native-fix count.
- Signing succeeded for the complete accepted queue. Signing stays enabled. Nothing has been pushed or submitted externally. Later signing-blocker statements describe earlier checkpoints.

[Historical checkpoints](PLAN-HISTORY-20261019.md) preserve the previous plan
verbatim. Their counts, signing blockers, agent states and “next” sections are
historical observations. The current schedule is below; historical open proof
obligations remain open unless a later acceptance record explicitly closes them.

## Earlier flex verification checkpoint (historical)

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

## Earlier implementation tracks (historical)

### 1. Ordinary batching accepted; compose public operations

The indexed ordinary algorithm is accepted under explicit source/comparator/
storage premises. It composes initial planning, sorted descending removals,
ascending count/rank correction and source-order execution with separate raw
storage. Source uniqueness and mapping uniformity are proved by the optional
publication shape under the inspected metadata contract. Native parser lowering,
callback readiness, sort/container/compiler and value abstraction remain open.

The component has 172 audits (109 newly authored), 18 extracted-native
transactions per original/candidate variant and five distinguished compiled
mutations. Independent manifest-only relocated replay, complete proof/source
review and separate outcome checks passed. A supplied comparator allows false
negatives, preserving the NaN audit's distinction between publication and changed
serialization. No additional browser bug was found.

[Scoped acceptance](../css-declaration-batch-root-v1/ROOT-SCOPED-ACCEPTANCE.json).
Next join this accepted component to legal mixed public operation histories and
actual caller readiness. A separate declarative parser-winner proof is accepted in
`../css-declaration-parse-winner-proof-v1/`: last important occurrence, otherwise
last occurrence, retained in original source order. Its producer is frozen with
46 new universal lemmas and nine kernel examples; independent fresh relocated
replay and complete proof review passed. It also characterizes push/extend return flags without equating a true
flag to a different final serialization. No new native execution is claimed.
[Scoped acceptance](../css-declaration-parse-winner-root-v1/ROOT-SCOPED-ACCEPTANCE.json).

### 2. URL state accepted; continue public parser histories

The v2 state/capture component is accepted after independent model/source review,
fresh complete replay, root authentication and ordered-trace rechecking. It has
51 modules / 388 reports (17 new / 107), actual cssparser builds in three modes,
59 cases and 503 input-derived ordered events. It derives mutable metadata and
original-source capture; codec, machine headroom, allocation/compiler and public
history premises remain explicit.

V1's trace validator accepted five malformed traces. The sealed negative review
remains valid; v2 rejects those exact traces and 3,043 corruption checks. No Lean
theorem was refuted and no new browser bug was established.

[Scoped acceptance](../css-tokenizer-url-native-state-root-v1/ROOT-SCOPED-ACCEPTANCE-V2.json).
The primary public-history component is accepted in `1c787870e8f816d6610872d15d1f0d995de7b667`:
46 modules / 371 reports (108 new), constructor-derived cache coherence, raw
pending cleanup, fetch/save/reset and admitted enable/query histories. Independent
fresh replay agrees on 87 snapshots per debug/release mode; three Lean and four
native semantic mutations distinguish the modeled behavior. Metadata, provider,
machine and safe-entry premises remain explicit.
[Acceptance](../css-parser-public-history-root-acceptance-v1/ACCEPTANCE.json).

Next compose actual skip_whitespace/next wrappers and production cold/Colon entry.
The source audit finds no reachable late-enable defect in the two production
enable sites. The wrapper component is accepted in `ea0a06720982c8716a501fb58f8fbb95d7029ece`
(57 modules / 448 audits, 77 new), after independent fresh replay and full review; nested/depth/callback protocols and
the declaration helper's saved-query/short-circuit automaton remain separate.
[Source audit](../css-parser-entry-wrapper-static-v1/REPORT.md).

### 3. Compose parsing, removal and clear

The root model now kernel-checks 44 lemmas for parser-priority push/extend,
separate storage operations, deletion target bounds, removal-loop safety, the
earliest-removal query certificate, callback stability under unchanged ordered
IDs, and arbitrary mixed parse/remove/clear histories.
The first 35 results have independent review; nine new joins prove the native
membership shortcut and single-property early return and use them in the history.
Duplicate source identities are admitted for sequential extend. These histories
do not yet include CSSOM setting; native interpretation and caller stability
remain open. The immutable flag and changed-return bits are outside this model.

[Checkpoint and replay](../css-declaration-public-storage-proof-v1/PLAN.md).
Static caller review completed without a new bug. It retains native callback
stability and animation-map key/value identity coherence as provider premises.
[Audit](../css-declaration-public-operations-static-v1/REPORT.md).

The source-shaped changing-vector removal loop is now accepted in
`../css-declaration-native-removal-loop-v1/`. Its current-vector reads, separate
index/local length, termination, bounds and same-index-on-removal behavior
compose with the direct query and mixed histories. Independent replay passed
65 audits (44 inherited, 21 new including five examples), a semantic mutation
rejection and two integrity guards. Native containers/compiler/usize and actual
callback readiness remain open.
[Acceptance](../css-declaration-native-removal-root-v1/ROOT-SCOPED-ACCEPTANCE.json).

Animation identity follow-up found no reachable key/value mismatch. Non-null
keyframe entries derive keys from computed values, base extraction uses the map
key, and transition replacement checks the owning property before assignment.
Segment grouping and generated layout remain provider obligations. The new
identity component derives option readiness from the map wrapper and proves
coherent finite composition histories under explicit arithmetic/provider premises. Non-NaN offset validity is required by the grouping
control flow. [Source audit](../css-declaration-animation-identity-static-v1/REPORT.md).
The endpoint/composition and separate map-constructor component is accepted after
full root model/source review and independent fresh replay: 49 audits and nine
integrity controls. It targets the frozen historical source and does not certify
the keyframe-substitution candidate or numeric payload correctness.
[Acceptance](../css-animation-identity-root-v1/ROOT-SCOPED-ACCEPTANCE.json).

## Earlier priority list (historical)

1. Complete the separate view-transition type-mutation style-invalidation repair
   and its runtime/formal gates, then sticky H1/H2 obligations. Initial-type
   deduplication is committed as fix87. Preserve separate evidence and native/WPT commits. The [worktree audit](../css-native-worktree-reconciliation-v1/REPORT.md)
   records the remaining intentional native candidates and their gates.
   Continue epoch-aware attribute provenance and link-env providers. Close the next
   animation provenance boundary after fix80: audit actual
   fallback/composition/publication callers and derive one end-to-end observation
   from admitted constructors. Successful wrapper union is accepted, but it does
   not establish numeric providers or scheduler histories.
   [Accepted repair](../css-animation-interpolation-taint-final-root-v1/REVIEW.md).
   Keep the transition-retention lead INCONCLUSIVE: provenance equality remains
   unresolved, so no restart or refresh repair is justified.
   [Oracle](../css-transition-retention-taint-oracle-v1/REPORT.md).
2. Derive source-dispatch-specific progress or total admitted provider families.
   Root and independent review accept the five-theorem delimiter bridge and 12
   review results; its driver delimiter law does not establish global progress.
   Then extend URL annotation projection through represented callback programs,
   and compose the declaration helper's saved-query/short-circuit paths after the
   accepted skip/next wrapper and production entry component;
   metadata, providers, callbacks and compiler admissions remain explicit.
3. Extend persistent-map caller admission. Count and actual iteration now compose
   through finite COW histories. Registration routing has a coherent-epoch source
   argument, but arbitrary lifecycle/scheduler and two-map disjointness remain open.
4. Continue the public declaration storage/CSSOM composition obligations above.
5. Continue cascade source/observer and hyphenation stateful consumer admission,
   including reflow-to-display cache association and lifetime. Preserve the
   cycle/animation, scope-ownership and uncovered-cache counterexamples.
6. Use ranked spec/implementation audits for further extensions, and the
   [closure checklist](FORMAL-CLOSURE-CHECKLIST.md) for unresolved obligations.
   Finite corpora and theorem counts do not establish whole-CSS coverage.

The same-effect animation dependency audit remains separate: overwriting skipped
CSS-wide defaults is not a general repair because keyframe dependencies use
current computed values.

The explicit-inherit repair has a separately accepted conditional component:
17 audits, four model mutants, and independent fresh replay. Readiness, root
parent absence, concrete map/flag APIs and native compilation semantics remain
admitted. It does not certify the substituted-inherit scheduler path.


## Accepted checkpoints

- **Custom-property count/iterator composition:** 32 new plus 105 inherited
  audits derive RawEnumeration, finite-history live count, exact indexed access,
  unique keys and nearest-owner values. Independent fresh replay and eleven
  semantic model mutants pass. Payload CompareSound is needed only for
  requested-update value equivalence; native representation/compiler/bounds and
  complete CSSOM lifecycle remain open.
  [Acceptance](../css-custom-properties-map-iterator-root-v1/ROOT-SCOPED-ACCEPTANCE.json).

- **Direct declaration removal loop:** 21 new audits connect a changing-vector
  execution to query, singleton/shorthand removal and public operation histories.
  Actual callback stability and native runtime/provider premises remain open.
  [Acceptance](../css-declaration-native-removal-root-v1/ROOT-SCOPED-ACCEPTANCE.json).
- **Parser-priority winners:** 46 new universal lemmas connect arbitrary source
  histories to independent last-important/otherwise-last selection, source order,
  raw representation and exact return flags. Native interpretation and parser,
  provider, container and compiler premises remain open.
  [Acceptance](../css-declaration-parse-winner-root-v1/ROOT-SCOPED-ACCEPTANCE.json).
- **Ordinary declaration batching:** `bb029748eaa6f3aab43b3afa58a1ab0c594ddc2d`
  accepts indexed/scheduled batch refinement
  and optional-publication transfer under explicit native/source admissions.
  [Acceptance](../css-declaration-batch-root-v1/ROOT-SCOPED-ACCEPTANCE.json).
- **URL mutable state and raw capture:** `e69ef82d29d9c3c9f9244a5174c46245634a3f89`
  accepts v2 and closes the selected model
  bridges with derived helper assignments and original-source endpoint proofs.
  Whole parser histories and codec/machine/heap/compiler premises remain open.
  [Acceptance](../css-tokenizer-url-native-state-root-v1/ROOT-SCOPED-ACCEPTANCE-V2.json).

- **All-shorthand ordering:** native `074086719e445ca72d3056f7fbf793af5e69d6f6`
  follows companion `bad8f7998dbbb3ad1fa88c0ca6892488f912e898`. Sixteen baseline
  failures are repaired; all 40 new and 61 existing subtests pass. Independent
  native/spec and formal review plus root replay accept 55 model theorem audits,
  3,042 candidate transactions and six compiled mutant witnesses. Actual raw
  declaration/importance/membership operations and arbitrary sequential all
  histories refine the forward setter under explicit admissions. The gate
  characterizes a changing intermediate step, not final cssText inequality.
  Pair order converges for any fixed unique expansion; absolute canonical order
  remains open. Ordinary batching and full native/provider/CSSOM lifecycle are
  not proved. [Acceptance](../css-all-logical-order-root-v1/ROOT-SCOPED-ACCEPTANCE.json).
- **Original Bloom milestones 1–6:** accepted within their declared selector,
  provider and native-interpretation scope. Historical M6 replay and the separate
  bounded cache-delta review are recorded in [CONTINUATION-20261017.md](CONTINUATION-20261017.md).
  The original source gate remains immutable; the historical replay explicitly
  does not claim current-source verification or cover changed cached dispatch.
- **Standalone CSS model:** `251269ad1a3b769828efc3321c41464bec50a18a`
  composes ordinary imports with explicit scopes through acquisition, scope,
  cascade and computed visibility. It is a bounded handwritten model with
  finite native comparisons, not full CSS conformance or mechanical spec translation.
- **Comment/string/numeric providers:** accepted component checkpoints retain
  codec, machine, compiler and caller admissions. The closure checklist records
  their exact boundaries and evidence. Native numeric repair is committed;
  full floating-point/library correctness remains open.
- **Parser tracking epoch:** `e9f6a83409e49efdd3018acc2263f247baf007e6`
  supplies ten conditional event-level lemmas and fourteen native observations.
  The later public-history checkpoint composes query/disable and selected byte
  providers under explicit safe-entry and provider premises; wrapper composition
  remains open.
- **Declaration structure/publication:** the top-level curly fallback and
  exclusive-publication repairs are committed as
  `095c5be548a2bddf5f3ff01e01da66c6098a8ee5` and
  `780495d90a85052cff69713f1086180253cb9730`. Their 27 and 29 conditional audits
  preserve parser/provider premises; independent transaction sequences do not
  prove state-dependent CSSOM destination merging. Link-parameters coverage
  enables its pref explicitly and makes no release-default exposure claim.
- **URL provider:** `1a67c0ab4a65227222ce5d3e553b84a2c5914f56`
  accepts 34 modules / 281 exact axiom reports (11 new modules / 96 new reports),
  44 complete native definitions and 57 fixed cases in three modes. Quoted
  Function cursor equality is false; completed string observation is proved
  under derived admission. Body metadata/raw slices, canonical codecs, native
  memory and public histories remain open. Acceptance:
  `../css-tokenizer-url-provider-root-v1/ROOT-ACCEPTANCE.json`.

## Working rules

- Each bugfix commit contains only its necessary native change and WPT/metadata.
  Proofs, tooling and research records precede it in separate commits.
- Record full hashes, paired results, standalone applicability and material limits
  in the bugfix index. Keep accepted source capsules immutable.
- Preserve failed runs and distinguish unsupported syntax, setup errors and
  semantic discrepancies. A fresh-DOM comparison alone is not a spec proof.
- Retain explicit unavailable results for unmodeled semantics. Historical proof
  replay does not certify changed native code; compiler/heap assumptions remain visible.
- Do not expand finite matrices without a concrete remaining risk. Once the
  required local gates pass, proceed to the accepted commit rather than repeat them.
- No pushes, Try jobs or external submissions.

## Build output retention

Retire task-owned generated build targets after their work is complete, active
process/open-file checks pass, and source plus required logs/receipts are retained.
Keep active Firefox object directories and ongoing independent replay outputs.
Record exact removed paths and verify retained evidence rather than deleting
entire research capsules.

## Whole-CSS library research

The user requested three parallel assessments of eventual complete CSS coverage.
Their outputs are kept under ../css-whole-spec-roadmap-research-v1/:

- Specification inventory, version policy, supersession and dependency closure.
- Lean semantic architecture, composition contracts and staged implementation.
- Spec-to-model interpretation, validation, maintenance and completion criteria.

This research does not replace the bug-fix queue or close existing assumptions.
Separate specification-model coverage, executable-model correctness and native
refinement. The existing standalone inventory's 127 fragment records overlap;
its line/audit counts are not coverage percentages. The [research synthesis](../css-whole-spec-roadmap-research-v1/README.md) proposes
a requirement-ledger and property-stage/dependency pilot, then box/layout and
animation integration. These are proposed library milestones; no new semantic
coverage or native refinement is claimed by the research.

The [second research pass](../css-whole-spec-feasibility-v2/README.md) makes the
inventory concrete with 19 provisional requirement records, adds a layout and
fragmentation protocol, distinguishes external inputs from unmodeled CSS
algorithms, and works through a historical CSSOM semantic change. Root reviewed
and authenticated all three tracks. No requirement is newly certified closed.
Next implement the source-lock/ledger validator and bind a complete custom-property
CSSOM slice; use the property/dependency pilot to reach an ordinary box/layout
observation before expanding independent families. The [third research pass](../css-whole-spec-feasibility-v3/README.md) is reviewed
and authenticated: versioned normative views, persistent permitted choices,
phase/owner-aware interfaces, observation-specific sampling and transitive
assumption closure. It adds research proposals, not coverage claims. Comparator-to-map-history composition is accepted after root and independent
fresh replay: nine new results and three compiled mutants connect payload and
taint to lookup and indexed observations of already-computed map updates.
Full native provider/COW and CSSOM routing admissions remain.
[Acceptance](../css-custom-properties-map-taint-history-root-v1/ACCEPTANCE.json).

## Animation endpoint retention accepted — 19 October 2026

Twenty-five audited results derive array/segment read readiness, independent
metadata-scan equivalence, exact added change decisions and finite/prefix
retention histories. Root replay and two compiled missing-endpoint mutants pass.
Native traversal,providers, publication, scheduler and payload/URL-data quotient
remain explicit admissions. This closes the local endpoint retention component,
not the whole animation path. See
[review](../css-animation-endpoint-final-root-v1/REVIEW.md).

Whole-CSS v4 research is producing an executable requirement-ledger prototype,
compiled phase/epoch interface experiments and independent acceptance examples.
Review these before adopting them as infrastructure; no new whole-spec coverage
claim follows from the prototypes.

## Whole-CSS source-ledger pilots — 19 October 2026

The [v4 research and executable prototypes](../css-whole-spec-feasibility-v4/README.md)
are committed in `bd7952da0a6585c32fb7d26e71b184ea25ae93ee`. The source importer
now passes root manifest-only relocated replay: three documents, 2,029,554 bytes,
75,626 lexical units and 16 rejected corruption/edit controls. Independent
fragmentation review matches the final importer and ledger exactly. Its thirteen
requirements and eight scenarios remain proposed interpretations.
[Root accounting review](../css-spec-source-ledger-root-v1/REVIEW.md).

The [architecture extension](../css-whole-spec-architecture-v5/REPORT.md) connects
existing library modules to proposed host-observation, content-continuation and
consumer-relative equality contracts. All new sketches are uncompiled. Next:
review a finite fragmentation domain and feasibility/escalation interfaces, then
implement a source-bound relation and executable selector. Reconcile HTML
style-block and font-cluster interpretations separately. Source bytes and theorem
counts are not a whole-CSS semantic coverage measure.

## Underlying animation base metadata — accepted

Fix 79 adds metadata comparison to the existing new-base-entry scan. The local
proof preserves original changed decisions and derives selected-entry metadata
agreement on no-change. It reasons about requesting a restyle, not actual queue
delivery. Provider identity, native representation, scheduling and full URL
observations remain open. See
[review](../css-animation-base-metadata-final-root-v1/REVIEW.md).

## Numeric interpolation provenance — accepted

Fix80 preserves both operands' attribute taint after a successful generic value
operation. Its 24-case WPT and one-line native patch are independent of earlier
repairs. Root and independent formal replay accept 15 results with 45 native
observations per variant. Numeric providers, admitted fixture observers and
native histories remain open. The whole-CSS coverage, architecture and evolution
agents have delivered the next integration assessment. Root accepts the
fragmentation rule/grid pilot within its stated conditional domain.
[Acceptance](../css-animation-interpolation-taint-final-root-v1/ACCEPTANCE.json).

## Fragmentation rule/grid pilot — accepted conditional component

Root and independent replays pass 34 audited results and nine compiled semantic
mutants. The independent reviewer adds seven kernel challenges and four integrity
controls. Rules, finite grid search, stage selection and conditional positive
slice progress are accepted. Natural-number extents and supplied layout inputs
remain the domain. No native fix or whole-fragmentation claim is added.

The next gate is normative admission: clarify sufficient break opportunities and
the emergency region, then construct actual flow/opportunity/continuation inputs
and prove that the chosen cut materializes permitted fragments. Forced events,
common decorations at all candidates and zero-size after-overflow handling must
remain visible. Do not import an uninstantiated SufficiencyCorrespondence as a
closed CSS premise. [Root acceptance](../css-fragmentation-unforced-root-v1/REVIEW.md).

## Whole-CSS next implementation decisions

The new three-agent [assessment](../css-whole-spec-next-assessment-v1/README.md)
uses the accepted fragmentation pilot as a composition test. Priority: reconcile
its interpreted requirement ledger and normative sufficiency/region frontier,
then derive a real opportunity/geometry/continuation provider and selected-cut
materialization bridge. Next add two independent fragment consumers and
persistent resource/sampling histories. The catalog/CSS2-residual/host universe
remains an explicit parallel accounting task; 127 historical library feature
records cannot serve as a coverage denominator.

The cloned-decoration correction exercise passes ten structural/arithmetic
checks, including stale binding and missing observer/assumption rejection.
Those inputs are supplied; this is not automated CSS interpretation. Standalone
specification, executable reference and Gecko-adapter claims remain separate.
No completion percentage or timeline is inferred from proof counts.

## Animation and fragmentation admission frontiers

The post-interpolation [source audit](../css-animation-post-interpolation-frontier-v1/REPORT.md)
finds no additional demonstrated metadata bug: failed iteration keeps the
already-composed endpoint, and final discrete fallback preserves the selected
whole value. Full segment composition provenance is now the next formal task;
an independent numeric/length provider oracle will establish a reachable branch
before browser testing. This is a correct-path proof target, not fix81.

Fragmentation [admission research](../css-fragmentation-admission-research-v1/REPORT.md)
leaves general sufficiency and emergency-region definitions unresolved. It
identifies a useful ordinary normal-flow sibling domain on initially empty
identical fragmentainers. A paragraph-only failure can miss a legal preceding
deferral; candidate-dependent decorations also defeat a naive shared list.
CSSWG history resolves the zero-after-overflow policy, while actual box/input
correspondence remains open. A requirements-ledger pilot is starting from the
existing174-unit window and explicit adjacent dependencies, before validator
implementation and independent review.

## Full segment composition provider — browser admission checkpoint

The independently derived mixed-number/length probe passes18 checks and one
harness on the unchanged fix80 candidate. Numeric10 retains underlying taint
after failed iteration accumulation; clean40px late selection and tainted32.5
same-type accumulation controls pass. Exact provider/keyframe/timing/grammar and
URL assertions are mandatory. This supports a reachable provider instance for
the next full-segment contributor proof; it is not a new bug or arbitrary native
history theorem. Producer and independent contributor/admission review are active.
[Runtime review](../css-animation-segment-provider-root-v1/REVIEW.md).

## Whole-CSS completion strategy and token-boundary candidate

The latest two-agent [completion assessment](../css-whole-spec-completion-strategy-v1/README.md)
adds a 17-family gap matrix, catalog/CSS2-residual completion gates, standalone
library boundaries and explicit soundness/availability/construction/preservation
obligations. Priorities remain a reviewed requirement ledger, a constructed flow
provider, actual selected fragments, distinct observations and versioned host
histories. A complete corpus inventory runs alongside the integration experiment.
The fragmentation requirement pilot now has independent bounded mapping review.
V3 corrects statement-extractor profile failures while preserving the 18 exact
claims and ten open providers; independent and root final replays pass. Accounting checks do
not establish complete semantic coverage.

Typed registered-value conversion exposed a new browser defect: a
length-percentage serialized as a dimension retains percentage boundary metadata;
a list also takes both boundary classes from its first component. The corrected
37-case fixture demonstrates ten failures with 27 passing controls. The patch
scans the already-serialized tokens and treats block closers explicitly. A first
compile attempt caught a parser-borrow lifetime error; the corrected build and
308-case candidate/regression run pass. Independent native/WPT review and
standalone two-file source apply/reverse pass. Dedicated WPT lint passes; the
general lint warning is the expected ESLint WPT exclusion. The formal producer
has completed 22 audited results and 24 native fixtures; independent and root
fresh replays pass. The bounded component and native/WPT repair are accepted
in their stated scopes. Native/WPT commit `34e4e755cb81332819e56457f5fb68b9b305c394`
follows evidence `76d4707974532db89589ffa39f2728db46527114`. The committed bug count is 82.

## Requirements-ledger review defect and segment replay

Independent review found a truncated `Emergency.graphic_slice_contract` claim in
fragmentation requirements v1. Its extractor selects the first `:=`, including
record-field assignments inside binders, so a partial statement incorrectly
passes. Root confirmed the exact source discrepancy. Keep v1 frozen and
unaccepted; correct extraction in a new version and reject this exact case.
The underlying accepted Lean theorem and lexical source accounting are intact.

Full segment provenance has passed root fresh replay: 45 new + 15 imported audits,
15 source bindings and 8 compiling model mutants. Independent review and root outcome reconciliation pass; this conditional
component is accepted. Publication and actual provider/caller histories remain
open. [Acceptance](../css-animation-segment-provenance-root-v1/ACCEPTANCE.json). Completed owned
root and agent compiler outputs have been removed after preserving receipts.
The whole-spec inventory has independent reconstruction and root replay of all
402 catalog occurrences and 841 CSS2 TOC entries. The 191 identities remain
provisional; none of these counts measures normative coverage. The next corpus
step has retained 26 full CSS2 chapter/appendix bodies, dated counterparts and
31 errata entries. Independent and root review accept bounded source spans,
heading reconciliation and the retained unapplied errata overlay. Packaging needs
the authenticated transitive closure, including two nested manifests omitted
from top-level FILES. Full normative requirement/dependency mapping remains open.
[Corpus acceptance](../css-css2-residual-corpus-root-v1/REVIEW.json).
[Fragmentation ledger acceptance](../css-fragmentation-requirements-root-v3/REVIEW.json).

## Animation publication repair accepted and committed

The selected endpoint's inner guaranteed-invalid value currently uncomputes to
CSS-wide initial, which can select a valid registration initial value. A revised
16-case browser fixture independently produces invalid underlying values rather
than relying on the earlier explicit-inheritance fix: ten failures, six controls.
The candidate introduces an internal GuaranteedInvalid declaration, marks it seen
and removes its routed map value. Explicit initial behavior remains distinct.

Build and the 343-case paired matrix pass, fixing precisely ten failures with
333 other status/message pairs unchanged. The final 22-case WPT additionally
checks suppression of valid underlying declarations/effects, cancellation and
valid-empty values; these six additions have candidate-only runtime evidence.
Root excluded an unrelated formatter signature change with an exact recorded
transfer. Independent native/WPT review, dedicated lint and standalone source
packaging pass; root freshly replays both review checkers. Root and independent
review accept the v2 publication/suppression proof: 81 audits (42 new), 29 source
bindings, five Lean mutants and three Rust mutants in debug/release. Fourteen
independent boundary theorems also pass. V1 mathematical replay passed, but its
checker was rejected because Python optimization disabled assertions; v2 rejects
optimized modes before dispatch. Native translation, providers and scheduling
remain admitted. [Acceptance](../css-animation-invalid-publication-final-v1/ACCEPTANCE.json).
The wider comparison combines contemporary and historical baselines;
neither standalone source package has an isolated browser run.

[Build and paired runtime](../css-animation-invalid-publication-fix-v1/RUN.json).
[Additional controls](../css-animation-invalid-publication-controls-v1/RUN.json).
[Proof scope](../css-animation-invalid-publication-proof-v1/SCOPE-PROPOSAL.md).

## Attribute-taint security investigation

The dedicated review reproduced a CSS-only URL-taint policy violation in installed
Firefox 158 with default CSS feature preferences. Script-free loopback testing
observed four forbidden image requests in release that disappear in the patched
shared build; ten literal/permitted controls remain. No arbitrary unknown-byte
extraction or incremental disclosure was demonstrated. The numeric selection
experiment also works through permitted static CSS. Fix 80 is the first candidate
for security triage; official severity remains unassigned. This comparison uses
an all-fixes development binary, not an isolated fix 80 build.

The formal target remains metadata-preserving optimization and the specified
URL boundary. Global network noninterference is stronger than that contract.
[Report](../css-attr-taint-security-review-v1/REPORT.md).
[Root review](../css-attr-taint-security-root-v1/REVIEW.json).

## Nested parser control accepted

Root and independent v3 replays match all 91 snapshots and the three compiled
native mutation deltas. The source-bound model derives raw cache retention,
pending-none recovery, raw comment annotation writes and nested/until-before
control correspondence for represented callbacks. The six Link paths are finite
kernel facts, not a universal grammar proof. Root adds five premise challenges.
The independent package's 20 negative guards and intact positive passed.

Next: inspect and model parse_until_after's direct delimiter advance and curly
recovery; extend the represented callback grammar where it exposes real callers.
Lexical progress, native byte bounds, full annotations and Link value parsing
remain open. [Acceptance](../css-parser-nested-control-root-v1/ACCEPTANCE.json).

## Accepted until-after continuation

Root and independent review accept the [delimiter continuation component](../css-parser-until-after-root-v1/ACCEPTANCE.json):
22 general theorem audits, 11 root kernel challenges and ten independent checks
recompiled by root. Fresh manifest-only replays agree with exact-source cssparser
in debug and release across 27 histories and 138 snapshots. Six successfully
compiled native mutants are detected. The independent review adds six native
cases in both modes. Current parser/tokenizer bytes match the retained sources.

The proof connects direct byte advance to source-token consumption using explicit
progress and delimiter laws, preserves enclosing ownership and Stop/error state,
and covers curly recovery. Main alignment excludes URL annotations; separate
continuation write laws cover those effects. Full callback annotation composition,
arbitrary callbacks, omitted tokenizer providers and native machine correspondence
remain open. The predecessor renderer correction is recorded: all old 91 snapshots
had zero stop masks, while new tests exercise nonzero enclosing masks. No new
browser defect is counted.

The [accepted provider bridge](../css-parser-delimiter-provider-root-v1/ACCEPTANCE.json)
derives the delimiter law from ByteLex and a one-byte punctuation contract.
Fresh root and independent 59-module replays pass five general results and 12 review
results, including the exact driver law for arbitrary input and jointly inhabited
provider premises. Its global progress corollary cannot be applied to the actual
partial driver without further admissions; the explicit counterexample is retained.

## View-transition mutation invalidation lead

The calibrated loopback probe reports six discrepancies among 18 rows: successful
Add/Delete/Clear update public membership and direct selector matching but retain
stale computed root color and descendant width, both synchronously and after ready.
All before-state and forced-refresh calibrations pass; twelve no-op/completed/old
transition controls pass. No duplicate initial types are used. Source/binary pins
are stable. Evidence: `../css-view-transition-type-invalidation-v1/v2/runtime-v1/`.
Independent source/spec/native/WPT review is accepted. The paired 42-case WPT
now passes completely: six improvements, 36 unchanged. Warmed root/descendant
::before and ready-only transition-group opacity checks are included. Build,
scoped C++/WPT lint and exact four-file upstream apply/reverse pass. Formal
companion and independent mathematical review remain pending; no native commit
is counted yet. [Native acceptance](../css-view-transition-type-invalidation-root-v1/ROOT-NATIVE-ACCEPTANCE-v1.json).

## Initial view-transition type deduplication committed

Fix87 (`2db943802038`) contains only the Gecko startup repair and its 21-case WPT;
`baa7f955bacd` contains preceding evidence. Five baseline failures become passes.
Fresh root and independent formal replays accept 90 conditional audits and 1,755
cases; 12 independent challenges exercise provider boundaries. Exact upstream
source applicability is checked, without an isolated upstream browser claim.
[Acceptance](../css-view-transition-types-root-v1/ACCEPTANCE.json).

The distinct invalidation lead now also has a baseline WPT run: six failures
and 12 controls pass, with all 24 initial-type/existing mutable controls passing.
A separate calibrated probe confirms stale ordinary and transition pseudo-element
styles. The candidate native repair is now applied and its build, paired 42-pass WPT,
scoped lint and independent native/WPT review pass. The formal companion and
independent proof review remain pending. It is not counted as a committed repair.

Sticky H1/H2 formal implementation has resumed with all ten preserved obligations
and explicit rectangle, writing-mode, finite-sentinel, clamp and caller boundaries.
[Scope checkpoint](../css-view-transition-type-invalidation-root-v1/STICKY-SCOPE-CHECKPOINT.md). No acceptance or H3 repair is claimed.

The [triage addendum](../css-bugfix-triage-20261019-addendum-v1/README.md) covers
fixes81–87, prioritizing the minimal release bounds-panic reproduction in fix83.

## Type invalidation accepted; signing pending

The native repair, final 42-case paired WPT, source-only upstream packaging and
scoped lint are accepted. Root and independent fresh formal replays pass 39 audited
results, 15,234 cases and 51,702 snapshots. Root additionally compiled eight independent
kernel examples and two exact-mutant incoherence theorems. Two C++ mutants alter
production control; two alter substituted traversal/cache providers. Full native
resolver, traversal, scheduler and lifecycle correctness remain admitted.
[Acceptance](../css-view-transition-type-invalidation-proof-root-v1/ACCEPTANCE.json).

Configured 1Password signing failed with “failed to fill whole buffer”; the user
was notified. 297 evidence-only files remain staged for the exact retry recipe.
The three native files and WPT remain unstaged. There are 87 committed fixes and
one accepted repair awaiting its separate evidence/fix commits.

Final packaging found a generated Python bytecode cache inside the independent
review copy, outside the producer closed manifest. Mathematical/native replay
results remain valid; final review-artifact acceptance is reopened until a
corrected version authenticates the nested capsule and replays without it. The
original sealed review is preserved. Signing also remains pending.

## View-transition invalidation review correction accepted

Independent review v2 removes the generated cache from its copied producer capsule, independently checks the nested closed roster, and passes a fresh full replay and 19 negative controls. Root authenticated the seals, reran the review checker, and verified unchanged challenge sources against its previous successful compilation. The 39 audits, 15,234 cases, and 51,702 snapshots retain their conditional scope. Native evidence remains six failures to 42 passes. The repair is accepted pending its separate signed native/WPT commit. See `artifacts/css-view-transition-type-invalidation-proof-root-v1/ACCEPTANCE.json`.

## Collapsed-flex review and two runtime findings

Root authenticated and replayed the independent collapsed-flex native review:150 paired cases show78 improvements,240 additional candidate controls and82 existing checks are retained. Another420 focused overflow observations disprove the proposed strut-scroll regression. The full16-obligation formal scope was reviewed and implementation assigned; retained-frame consumer safety remains a required derivation, not a provider assumption. See `../css-flex-collapsed-alignment-root-v1/NATIVE-REVIEW.json`.

Two separate leads now reproduce in installedFirefox158 and the shared development build. Safe alignment in reversed scrollable flex containers loses reachable content:24 calibrated scroller discrepancies per280-row run, with the broader non-scroller spec/WPT conflict kept separate. The sticky proof's finite-sentinel boundary predicts unwanted movement of all-auto boxes beyond about8.95millionpx; calibrated42-row runs yield6sticky discrepancies and36matching rows. The latter's initial overlystrict precision oracle is preserved and corrected with ordinary controls. Reports: `../css-flex-safe-overflow-probe-v1/REPORT.md` and `../css-sticky-sentinel-probe-v1/REPORT.md`. Neither is counted as fixed.

The sticky sentinel WPT has a24-case baseline:4failures and20passes. A separate per-inset positional-clamp repair is being built; H1/H2 proofs remain tied to their earlier source snapshots, and range/timeline extreme behavior is not claimed repaired. Quote containment also has a new source/scope review in `../css-quote-scope-append-root-review-v1/SCOPE-REVIEW.md`; full proof remains pending. Signing remains unavailable; the exact297-file evidence checkpoint is preserved.

## Sticky repairs and formal checkpoints

The finite geometric-sentinel repair passes all 24 paired WPT cases (four improvements), a successful build, scoped native lint, 1,328 regression subtests and three reftests. Follow-up sticky/timeline tests retain eight passes, two pinned expected failures and one passing reftest. Its independent native review is accepted.

The combined positional companion now passes original and relocated replay: 59 audited declarations, 856 cases and 5,136 complete Lean/native comparisons of results, frame positions and caller traces. Seven native mutants and five executable lifecycle-model mutants are detected. Fifteen integrity controls and two forbidden-axiom controls pass. All 20 raw streams match after relocation. The replay pins 15,308 installed Lean files and 959 native header dependencies. Numerical projection substitution into the common lifecycle model is proved. Independent review v2 is now frozen with HOLD: actual indexed continuation/common-translation refinement, graph/fuel termination and executed machine-operation joins remain missing. Root authenticated all228 review files. Preserve the full original contract when implementing these joins; the existing theorem must not stand in for the missing caller semantics. Geometry/lifecycle providers remain explicit admissions. See [the frozen producer checkpoint](../css-sticky-sentinel-proof-v2/REPORT.md). Range/timeline sentinel collisions remain outside this positional repair.

The separate explicit-offset repair reserves NS_AUTOOFFSET after resolving an explicit value. The 80-case WPT improves from 32 FAIL/48 PASS to 80 PASS, with explicit opposite-edge zero to avoid depending on the automatic-inset repair. Build, scoped lint, 1,328 regression subtests and three reftests pass. The two-file patch applies and reverses on HEAD/upstream; no isolated upstream build is claimed. Its extended formal producer v2 passed replay, but independent review found the final formatted source duplicated in the browser-tested source role. The real tested snapshot remains in the native evidence. Native/WPT review passes; correct this source identity and replay all three genuine variants in a new immutable version before formal acceptance.

H1/H2's independent review is frozen with HOLD on the original full scope. All 106 existing audits and fresh native/model replay pass, but universal GetScrollRanges rectangle composition/bounds and Earliest/Latest signed32 caller joins are missing. Root authenticated all 599 outer and 268 nested files. V2 now supplies both components and root replay passes all 162 audits, 2,224 full absolute observers and 11,898 endpoint comparisons. Root review found R3: chosen-axis EntrySafe omits the other axis executed by ComputeStickyLimits and complete nsPoint subtraction. Three kernel witnesses and six UBSan runs confirm the gap, including coordinate-bounded inputs. Preserve the full contract and add the two-axis execution admission/derivation in v3. See [the v2 root verdict](../css-sticky-insets-proof-root-v2/VERDICT.json); the original [v1 verdict](../css-sticky-insets-proof-review-v1/VERDICT.json) remains historical evidence.

## Collapsed flex exported-baseline repair

The retained-frame observer audit exposed six mismatches in the same 20-case release/shared-browser roster. All ordinary, removal and restoration controls pass. The unconditional F11 baseline observer obligation is false for the frozen allocation candidate; the remaining allocation work continues under its original 16-obligation contract.

A separate native candidate now excludes struts from baseline donor selection and requests synthesis when there are no participants. The expanded WPT covers both column directions, both baseline groups and nowrap/wrap/wrap-reverse. Its directly paired result is 22 FAIL/38 PASS to 60 PASS, with all 38 other status/message pairs unchanged. Twenty-five existing files pass (23 reftests and three subtests). Builds and scoped native/WPT lint pass. The repaired local build was restored after the baseline experiment.

The exact two-file Gecko/WPT patch applies and reverses on HEAD and retained upstream without absorbing the allocation changes. Independent native/WPT review and the formal companion remain open. A row with a strut-only edge line exposes a specification ambiguity, even with zero gap; the candidate retains the existing no-donor numerical fallback and does not claim a normative resolution. Continuation synthesis-state publication also needs review because later fragments can bypass DoFlexLayout. These gates are not discharged by unfragmented WPT success. See [the candidate report](../css-flex-collapsed-baseline-fix-v1/REPORT.md).

## Signing and retained state

The latest user-requested signing retry again failed in 1Password with “failed to fill whole buffer”. HEAD remains 92a6fddf18e5828b17d7491a34663a0d5a9c12ad; all 297 staged evidence files were reauthenticated. The count remains 87 committed fixes and one accepted invalidation repair awaiting signed commits. Runtime/proof checkpoints do not increment that count. The formal companion's documentation pins track the newer unstaged roadmap/ledger; the staged evidence snapshot remains intact. Do not retry signing until the user indicates readiness.

Completed root native replay products were removed after matching the original and relocated results; recipes, sources and raw evidence remain. Temporary Lean products are removed by the runners. The main Firefox build remains available with the baseline and sticky candidates applied, including the new negative-inset arithmetic candidate. Root removed37.3MB of completed proof/native replay products; generated sources and raw receipts remain.

## New observable lead: opposing negative sticky insets

Review of the caller arithmetic domain led to a separate small-tree browser reproduction. Installed Firefox158 and the shared Firefox160 build produce the same60 observations:24 failures and36 passing controls, with all dimensions, scroll and static-reference checks passing. The standalone60-case WPT baseline reproduces24FAIL/36PASS. Huge opposing negative insets unexpectedly move a target200px; smaller or asymmetric negative controls pass.

The native candidate widens view-rectangle arithmetic and stores sticky limits as direct edges, since widening normalization alone can leave origin-plus-width overflow. Its initial build exposed two direct-field consumers; those now use accessors and build-v2 succeeds. The candidate passes all60 paired WPT cases,1408 regression subtests and3 reftests, plus scoped native/WPT lint. An exact three-file patch applies/reverses on HEAD and retained upstream without H1/H2/sentinel/alias changes. Twelve preliminary Lean integer results establish normalization identity, wide intermediate bounds, conditional stored-result bounds and concrete wide-interval witnesses; full source/provider/observer composition and independent native/formal review remain pending. Keep this separate from H1/H2, geometric sentinels and explicit-auto encoding. [Probe](../css-sticky-negative-inset-overflow-probe-v1/REPORT.md), [candidate evidence](../css-sticky-negative-inset-overflow-fix-v1/). No count increment.

## Current handoff: two accepted repairs pending signing

There are 87 committed fixes and two accepted repairs awaiting signed commits: view-transition invalidation and explicit sticky-inset encoding. The alias v3 source-role correction passes root review and fresh replay: 31 audits, 236 cases, six genuine-source native configurations, five paired mutations, 11 provider negatives, 33 integrity controls and two axiom controls. See [root review](../css-sticky-offset-alias-proof-root-v3/REPORT.md). Earlier source-role HOLD records remain historical evidence.

The latest user-requested signing retry again failed in 1Password; HEAD and the exact 297 staged files remain unchanged. The negative-inset standalone sticky source passes all 60 WPT cases; the combined source and successful build are restored. Its full proof and independent review remain pending. H1/H2 v3 is undergoing producer replay with full two-coordinate arithmetic admission; the geometric-sentinel lifecycle proof still needs its indexed-graph and machine-operation joins.

## H1/H2 full caller review accepted

The v3 correction retains the complete two-coordinate frame through core construction and displacement subtraction, with the real early-return guards. Root authenticated all1044 producer files and replayed17modules/191audits, all four2224-case source variants, existing range/endpoint calibration and mutants. All35 integrity/comparator controls pass. Nine additional root kernel checks and twelve extracted-native runs distinguish selected-continuation position/normal properties from canonical range geometry, including missing-property fallbacks and expected excluded overflows. The full stated conditional contract is accepted; H1 and H2 are two separate accepted repairs awaiting signed commits. See [root review](../css-sticky-insets-proof-root-v3/REPORT.md).

Current count:87committed,4accepted pending. Explicit-inset commit recipes are prepared; H1/H2 queue packaging is next. Root cleaned23.2MB of completed products. The geometric-sentinel agent is closing indexed lifecycle/termination and machine joins. The negative-inset agent is implementing the full companion after independent native/WPT acceptance, including the retained preexisting range-clamp witness. Collapsed allocation retains F11refuted and explicit incomplete F12native boundaries while its expanded source checkpoint is finalized. No count is assigned to those incomplete repairs.

H1/H2 native packaging now verifies both standalone patches on current HEAD and retained upstream. The context-adjusted H2-after-H1 patch reproduces the exact archived combined browser source and reverses cleanly. Each patch retains only one Gecko file and its WPT; all real index/worktree state is preserved. See [packaging](../css-sticky-insets-commit-v1/PACKAGING.json). The seven evidence/formal/native commit recipes are ready in `artifacts/css-sticky-insets-commit-v1/QUEUE.json`; each native repair retains its own WPT. Signing is being retried at the user’s request.

## Collapsed allocation checkpoint replay

Root authenticated the sealed source and durable replay manifests, then reproduced all 266 audits and 52,160 native/model cases. F11 remains refuted and F12 retains concrete source/provider and downstream arithmetic gaps; this is a successful checkpoint replay, not acceptance of the repair. The baseline candidate remains under independent review. Root removed 18.7 MB of completed replay products while retaining sources, commands and observations. See [checkpoint review](../css-flex-collapsed-allocation-proof-root-v1/REPORT.md).

## Flex baseline sum overflow: paired repair candidate

The F12 operation review found a separate observable arithmetic defect: independent baseline-edge maxima overflow a signed32 sum. A two-item probe reproduces zero height instead of 100px in installed Firefox 158 and the shared 160 build, even with max-height: 100px. The new 54-case WPT changes 12 failures to passes, with 42 unchanged. All 29 regression files pass; build/native/WPT lint pass. The exact two-file patch applies/reverses on HEAD and retained upstream. Six primitive kernel results and extracted-native UBSan comparisons accompany the repair. Independent review remains pending; counts stay 87 committed and 4 accepted pending. See [repair report](../css-flex-cross-baseline-overflow-fix-v1/REPORT.md).

The collapsed-baseline donor repair now has an authenticated independent native/WPT review. Full F11/F12 remain open; the agent is implementing versioned source/provider/frame/overflow joins in a new v2 component, preserving the original contract and earlier refutation. Its first audit found that the detached rectangle union model differs from the native both-empty case; no new browser defect is claimed from that distinction.

Signing retry still fails in 1Password. The 297-file staged evidence snapshot and HEAD remain unchanged. The shared local build now includes the separate cross-size sum repair; only whitespace formatting followed its successful build.

## Safe-scroll candidate and retained collapsed-frame overflow

Counts remain **87 committed fixes and 4 accepted pending**. Signing retry still fails in 1Password; HEAD and the authenticated297-file staged checkpoint are unchanged.

The own-scroller safe-flex repair is now a sealed native/WPT candidate:484 failures become passes across640cases, with156unchanged controls. A paired72-case ownership probe changes only four body-owned safe cases;14regression files pass798subtests and10reftests. The exact two-file patch is independent of other pending flex changes. Ten preliminary reachability lemmas pass, but complete formal/source joins and independent review remain open. See [candidate](../css-flex-safe-scroll-origin-fix-v1/REPORT.md).

Full F11 review found another observable retained-frame defect: a collapsed240px child with border/margin/descendants can enlarge a100px flex scrollport. Release and repaired builds have24identical observations, including12collapsed overflow cases. The plainzero-width control passes. Earlier420controls used shorter items and did not refute this case; their broad no-overflow conclusion is superseded. A kernel/source-extraction counterexample now preserves the full domain; a separate145-case WPT baseline is running. See [discovery](../css-flex-collapsed-tall-strut-root-v1/REPORT.md).

The negative-inset v2 complete conditional companion passed a fresh root replay:219audits,544Lean rows,2164genuine native observations,9semantic mutants and the retained clamp-UB exclusion. Independent review is active. Geometric-sentinel v3 is also sealed, with167audits and the formerly missing indexed/machine joins; independent review remains pending. No acceptance is inferred from successful replay alone.

Next: finish the collapsed-overflow repair and paired WPT; address the baseline-sum WPT numeric-range portability review; complete independent sticky reviews; build the safe-scroll source/consumer companion without narrowing its contract.

## Current accepted queue: six repairs pending signing

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
  would break already-defined cancellation. The complete wide-coordinate design review is authenticated and recommends exact
  64-bit propagation; no native repair has been applied.
- [Natural-baseline donor selection](../css-flex-natural-baseline-donor-probe-v1/REPORT.md):
  eight failures among 24 rows, all removal/restoration and geometry controls
  passing. An ordinary 160x80px flex box shifts 34px when an empty 5px item masks
  a natural text baseline. This is separate from collapsed-item donor exclusion
  and the unresolved strut-only edge-line specification question.

Collapsed-allocation v2's 147 source inputs and 234 receipt files are authenticated
as a producer checkpoint. Full F11/F12 remain open; v3 continues the original
sixteen obligations. The safe-scroll proof retains all twelve obligations and
keeps the newly reproduced packing failure separate from its policy repair.
Next: review the relative-baseline companion, finish the scroll-provider proof/repair, and resolve the natural-donor prerequisite before restoring native acceptance,
finish the implemented wide packing candidate’s source/formal review, including
final-coordinate, sentinel and downstream fragmentation obligations, and continue the full twelve/sixteen-obligation consumer proofs.
The latest user-requested signing retry failed; no further retry is planned
without a change in signer readiness.

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

## Checkpoint: forced-break final-fragment lead

Counts remain **87 committed native/WPT fixes; ten accepted pending signing**.
The latest user-requested retry again failed in1Password; HEAD and the297 staged
evidence files remain unchanged. There are now six unaccepted candidates/leads;
the new lead is not counted as a distinct accepted bug.

The [40-case fragment probe](../css-fragment-consumed-size-probe-v1/REPORT.md)
and WPT retain the rejected packingv1 failures (29PASS/11FAIL). Normative review
clarifies that flex's exact fragmentation algorithm is unspecified; do not turn
the informative sample algorithm into a universal exact-coordinate claim.

A [forced-break reduction](../css-fragment-forced-break-probe-v2/REPORT.md)
uses only80px items yet reproduces eight oversized final fragments and misplaced
following siblings among24 cases, identically in release and the shared build.
The focused WPT has16PASS/8FAIL and passes lint. Six kernel results establish
ideal cancellation and show why premature size caps are insufficient. Exact
consumed-size extraction reports signed overflow with the observed fragment
sizes atO0/O2; no full browser-state trace or repair is claimed. All generated
executables and temporary browser profiles are removed.

Next work, in order:

1. Join packingv2's fragment coordinate recurrence with the real consumed-size
   provider and final content-minus-consumed observer. Preserve all passing tiny-item
   forced-break cases as well as the original defined packing controls. The new
   observed failures remain a required integration gate, not a hidden out-of-domain
   exception. Do not cap cumulative totals before their cancellation.
2. Implement the reviewed representation only after its branch/API bounds are
   settled, then build and run paired WPT/targeted regression and source proofs.
   Preserve the original full packing obligation roster and independent patch scope.
3. Continue safe-scroll's twelve and allocation's sixteen obligations. Current
   agents are joining placement/overflow/snap and parent publication/frame-cache
   identity respectively; provider freshness and full F11/F12 remain open.
4. Resolve natural-donor semantic dependency/independent-landability before
   restoring native acceptance. Resume signed commits after signer readiness changes.

## Checkpoint: runtime fragmentation diagnosis and restoration

The [runtime trace](../css-flex-fragment-consumed-trace-v2/REPORT.md) confirms the
forced-break failure route on32 complete selected fragment reflows. Consumed
and cumulative sizes become negative; growth processing yields zero, and final
subtraction emits an oversized block size. Four DOM rows exactly match the
uninstrumented baseline. The temporary logging is removed and the original
source/build, HEAD and staged index are verified restored. The initial failed
logging compile is retained separately; both successfulv2 builds have zero
compiler warnings and the existing mach monitor exception remains explicit.

Seven new kernel results establish residual-size placement, update and optional
min/max translation identities, with two rejected false claims. These do not
yet close machine bounds or the complete emitted-size/cache recurrence. The
next repair design must preserve actual source metric ordering: row forced-break
processing may push an item after its extent contributed to child-end metrics.

The independent design agent is comparing normalized displacement with exact
portable wider accumulation, while deriving residual observer bounds. No native
implementation has been accepted. Safe-scroll's twelve obligations and allocation's
sixteen continue; the latter has a new parent-publication/cache-identity producer
checkpoint, with lifecycle and full F11/F12 still open. Counts remain87 committed
fixes, ten accepted pending signing, and six unaccepted candidates/leads.

## Checkpoint: independent publication replay and cache producer gap

The [root publication review](../css-flex-publication-root-review-v1/REPORT.md)
freshly compiled all60 checkpoint modules, checked60 exact standard-axiom audit
results and rejected four producer false claims. Fourteen independent kernel
checks and three rejected false claims cover cache ordering, publication status,
sentinel edges and cancellation. The completed31,422,768bytes of compiler
outputs were removed; all104 retained payload files are authenticated.

Source review found that final cache installation receives the actual child's
reflow-input padding and indefinite flag, while measuring-reflow reuse receives
item fields. The prior publication model had not derived equality of those
producers. The lifecycle agent is separating them before closing the stateful
interleaving proof. This is a model/source admission gap, not a new browser bug.
Full safe-scroll twelve-obligation and allocation sixteen-obligation targets
remain unchanged, with F11/F12 still open.

Packing design now has a tested portable128 exact-provider approach and a
separate justified cap for the child-growth observer under review. Integration
must read actual predecessor content sizes, skip true overflow containers before
cache lookup, preserve previous-continuation versus previous-in-flow semantics,
and keep tentative/final/physical conversion bounds explicit. No v2 production
patch is applied or accepted yet. Next: review the complete recommendation and
implement only once those source joins are settled.

Counts remain87 committed native/WPT fixes, ten accepted pending signing, six
unaccepted candidates/leads. The latest requested signed retry failed again;
HEAD and all297 staged paths/content pins remained unchanged.

## Checkpoint: writing-mode WPT and actual shared-provider reachability

The [expanded reduction](../css-flex-fragment-writing-mode-probe-v1/REPORT.md)
now covers144 cases across three writing modes, both directions and row/column
flex layout. Release and project raw observations are identical. The expanded
WPT has96 PASS/48 FAIL with all failures at the following-sibling assertion;
lint is clean. Independent reference boxes preserve eight controls that would
otherwise be misclassified due to CSSOM rounding. Initial development runs and
the corrected numeric-origin calibration are retained.

The [new diagnostic trace](../css-flex-consumed-caller-trace-v1/REPORT.md) confirms
that the shared consumed-size helper overflows in a block ancestor before its
flex child. A flex-only bypass cannot eliminate that executed overflow. Both
logging/restoration builds succeed; eight DOMrows match the uninstrumented
baseline; original source/build/HEAD/index are restored.

The sealed [v3 design](../css-flex-cross-packing-design-proof-v3/REPORT.md) prefers
exact portable128 fragment totals. Root has authenticated its166 payloads/source
roles and reviewed the recommendation, without claiming a full root replay or
implementation acceptance. A real retained-source prototype is now comparing
a capped legacy signed32 prefix cache with a separate exact flex cache. The
cache-free child-walk option was falsified by quadratic read counts. Next: finish
actual source-slice/type calibration, compile a reversible candidate, and run the
144-case gate and full prior packing/fragmentation controls before acceptance.

Allocation lifecycle work has a new66-module/45-audit producer checkpoint; root
review remains pending. Safe-scroll's final machine/consumer composition and
closed replay are progressing. The original twelve/sixteen obligations remain
open. Counts stay87 committed fixes, ten accepted pending signing, six unaccepted
candidates/leads. No further signer retry without changed readiness.

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

## Exact-size transport and recovery checkpoint (20 October)

The first full seven-file exact-size prototype experiment passed: candidate build
exit0, draft38 cases26PASS/12FAIL→38PASS, and all510 existing subtests preserved.
The57 reftest outcomes remain44PASS/13expectedFAIL. Source and build were restored
successfully; the prototype is not installed or accepted for landing. See
[paired experiment](../css-exact-size-transport-runtime-v1/REPORT.md).

The independent recovery checkpoint passed root relocation:63modules,31audits,
three false claims,1,024 extracted native cases in three modes and three semantic
mutants. Recovery follows prior nested cache writes and invalidates in place.
Actual callback-path/heap representation, observer closure and owner survival
remain open. Root removed33,529,896 bytes of terminal replay products.
See [root review](../css-flex-cache-recovery-root-v1/REPORT.md).

Next in order:

1. Run the prepared144 supplemental browser diagnostics paired against the
   exact-size prototype, retaining all240 observed/fresh stage records. Calibrate
   signed-caption source-policy tests separately from normative alignment checks.
2. Complete signed table arithmetic and source-admitted caller bounds. Individually
   bounded negative margins can still exceed the subtraction domain; extracted
   witnesses alone do not establish actual browser reachability or a new bug.
3. Derive actual ordinary-block output and current/primary/continuation ownership
   relations, then extend to remaining frame families and observer paths.
4. Continue the original full safe-originF1–F12, allocationF1–F16/F11/F12 and
   fragment observer obligations. Coordinate caps and fragment cases remain in
   scope; successful transport or a conditional component does not close them.

The nonmeasuring table static audit found no new counterexample. Ordinary column
and orthogonal tables can still measure through automatic minimum sizing; absence
of a final-cache field alone is not a bug. The diagnostic remains unexecuted.

Counts remain87committed/14accepted pending signing/six unaccepted. Requested
signing retryv13 failed with the same 1Password error; HEAD and the297-file staged
snapshot remain unchanged. No unsigned workaround, push or CI run occurred.

## Signed caption reachability and block output (20 October)

The signed-table domain correction passed fresh root replay:51 audits,34 native
rows per variant, semantic mutations and expected UBSan domain failures. It retains
signed occupancy and checks each executed intermediate, rather than treating
negative margins as natural numbers. Full caller/output coverage remains open.

Browser tracing now distinguishes two routes. Fixed-basis extreme negative-caption
fixtures never enter the reducer. Auto-basis flex growth does: actual720Mau minus
negative1.44Bau reaches mathematical2.16Bau, outside signed32, and the traced build
returns0. This matches the earlier extracted UBSan witness. A safe signed32 control
also returns a tiny table through a separate Q-as-auto conversion, so final geometry
alone is not an overflow oracle. The repair and a discriminating WPT remain open;
no new fix is accepted. See the [growth trace](../css-exact-size-signed-caption-grow-trace-runtime-v1/REPORT.md).

The ordinary-block output checkpoint passed independent root relocation:24 kernel
audits,867 native rows at each of O0/O2, four false claims and three semantic
mutations. It derives both returned dimensions for admitted unfragmented stretched
ordinary blocks. Actual dispatch, stable border/padding/cross policy and completed
child-state restrictions remain explicit. Non-stretched frames, other frame types,
cache/move paths, physical observers and full F1–F12 remain open. See
[root block review](../css-exact-block-output-root-v1/REPORT.md).

Independent cache-owner review identified a missing native relation: destruction
uses a cached primary-frame bit while the model tests content-primary pointer
equality. The twenty logical results remain valid conditionally; native admission
needs cached-bit/pointer coherence, including setter callbacks. Normalization and
continuation reparenting phase invariants remain active. Full F1–F16/F11/F12 is open.

The paired144 supplemental diagnostics plus38 original transport tests are running
in css-exact-size-supplement-runtime-v1. Baseline completed182 subtests with all48
fixture collections complete; final candidate/restoration results are pending.

Next: finish that paired run and inspect raw measurements; test a calibrated
observer for signed-caption repair; close primary-owner coherence and the next
ordinary-block caller admission. Preserve all original cap, fragmentation and
lifecycle requirements. Signing retryv14 failed; HEAD and297 staged files were
verified unchanged. Counts remain87 committed/14 accepted pending/six existing
unaccepted repair candidates, with the newly reached arithmetic finding separately
under investigation. No push or CI run occurred.

### Supplemental result and observer corrections

The paired experiment is terminal and the original source/build restored. Combined
results are122PASS/60FAIL→150PASS/32FAIL, with no PASS→FAIL transitions. All38
original cases pass. All48 supplemental calibration and48 fresh/update checks pass;
remaining failures are28 table diagnostics and4 image geometry checks. Each variant
retains240 stages,240 fresh peers,80 explicit references and96 small controls.
See [paired supplement](../css-exact-size-supplement-runtime-v1/REPORT.md).

Do not classify those32 outcomes as32 defects. Independent source review found the
original table reconstruction assumed an inner-table-only DOMRect, whereas Gecko
includes caption boxes in the bounding union. Correct that observer in a successor
while preserving these inputs/results. Every candidate image sample's main/cross
size and end coordinate exactly matches its explicit reference. A source-shaped
float-conversion calculation reproduces the residual with exact native geometry;
actual native integer path admission remains needed. Preserve the full exact
observer requirement rather than increasing tolerance or waiving remaining checks.

The signed-caption percentage observer produced14 identical rows in installed
Firefox and the restored project build. Auto/zero reference vectors coincide in
both profiles; this is negative calibration, not a regression oracle. The reached
signed subtraction remains established by the earlier trace. The25-audit widening
companion compares Q and INTMAX caps explicitly; independent review is running.
No arithmetic repair is installed or accepted. See
[observer calibration](../css-table-signed-reduction-observer-runtime-v1/REPORT.md).

Next priorities:

1. Bind CSSOM frame collection and float coordinate conversion to a correct
   observer; reduce a non-flex geometry case and trace native integer edges before
   proposing a separate repair. Keep table-caption union and replaced sizing distinct.
2. Finish independent review of widened subtraction/cap preservation and choose
   appropriate direct regression coverage; do not infer visual improvement from
   removing undefined arithmetic or treat Q as an ordinary finite size.
3. Review the normalization checkpoint and close cached-primary-bit/pointer
   coherence, pair-list readiness and actual callback ownership joins. The new18
   producer results exclude specific column/paginated interrupt paths conditionally,
   not all ways to reach a continuation state. Producer cleaned3,136,248 bytes.
4. Continue full safe-origin F1–F12, allocation F1–F16/F11/F12 and fragment observer
   obligations, including non-stretched and other frame classes. Earlier bounded
   block/output and recovery components remain components, not completion claims.

The48 recipes/14 accepted native patches passed the disposable-index check after
checkpoint updates. No new accepted fix or signed commit;87 committed/14 accepted
pending/six existing unaccepted repair candidates remain. Signer retryv14 is still
the latest attempt. The original297-file staged snapshot is preserved.

### Minimal rectangle discrepancy reproduced

The follow-up observer probe completed 56 identical records in installed Firefox
and the restored project build, with every ResizeObserver callback delivered.
Four small non-flex controls report an edge of 100px. Four large plain boxes
(horizontal/vertical, padded/unpadded) report a bounding edge of 100.015625px while
a zero-size marker at the same edge reports 100px. No flex, table, image or authored
transform is required. getBoxQuads is unavailable under defaults, so no corner-API
measurement is claimed. See [observer isolation](../css-exact-size-observer-runtime-v1/REPORT.md).

Source-shaped numerical replay reproduces the discrepancy from perfect native
geometry through float rectangle conversion. This supplies a concrete next repair
candidate, but complete ancestor/viewport/zoom/SVG admission and actual integer
path binding still precede native acceptance. A separate narrow repair/WPT proposal
is underway; no original exact observer requirement or failing assertion is waived.

The signed-reduction independent review accepts the bounded arithmetic component:
25 producer audits, 11 independent checks, native mutation/UBSan controls and eight
guards pass. It does not accept a production cap policy or observable CSS repair.
INTMAX preserves all old signed-defined publication arguments; source percentage
analysis supports the negative observer result while retaining internal zero/Q
branch differences. Full table, IEEE conversion and caller/lifecycle joins remain
open. All runtime source/build restoration is complete; signing/index state and
accepted-fix counts remain unchanged.
