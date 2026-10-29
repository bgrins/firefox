# Pow v3 fixture and baseline owner review

No blocker found. This supplements independent review v1, which remains an accurate review of historical proposal v2.

Proposal v3 changes exactly four signed-zero observers, leaving the other 20 callbacks, names, native candidate and roster unchanged. Mapping sign through (2 + sign(result)) / 4 produces 0.25 for negative infinity and 0.75 for positive infinity; NaN remains NaN until the outer calculation and becomes opacity zero. The four controls now distinguish both infinity signs from NaN. Generated negative zero remains nested. The prior v2 opacity-observer limitation is resolved; the other bounded coverage limits remain.

Read the full baseline.py and its complete delta from executed Hypot corrected-baseline-v3. The shared WPT runner is byte-identical. Assessor changes are diagnostic wording only, retaining exact callback identity/cardinality, all original passing signatures, all 129 controls and two endings, all 18 candidate targets and all 24 authored callbacks. No fresh failure count is assumed.

The original linked application was built with the pending Hypot source/fixture at build HEAD 5858dbe. Its source was b7a6 while that HEAD's Git source was df7e and the fixture was untracked. The new guard explicitly checks those preimages, build-epoch compiled pins, exact later two-file native commit 36b693, accepted Hypot 149 metadata and current HEAD bytes. It preserves all 28 current accepted claims and historical 145 metadata. It does not equate historical Git source with actual compiled source. Complete recorded application metadata and binary pins remain checked.

Static --check passed 2dfb84/0. All 80 references and proposal/plan/capture payloads authenticated; current control hashes, accepted records and all 28 claim bindings checked 452a43/0. Full executable reading and exact fixture delta:561d2b/0. No live guard, browser, build or canonical mutation performed by this reviewer.

Root subsequently launched the baseline as session 17634. This review makes no terminal or test-result claim. Root deferred V61 signing until the reversible pair completes, keeping both phase harness revisions at 20ab7. A future artifact checkpoint must bind actual paired evidence and restoration before standalone native acceptance.
