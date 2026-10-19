# Independent native/WPT review: keyframe composite update

## Verdict

Accept the final native repair and paired WPT evidence. Formal acceptance remains pending the separate proof producer's complete implementation and independent replay. This artifact does not run a browser, build Gecko, alter live files, or modify Git.

The production patch adds exactly one mismatch condition, `a.mComposite != b.mComposite`, inside the complete `KeyframesEqualIgnoringComputedOffsets` function. The comparison now includes every specified Keyframe field: optional offset, timing function, composite operation and ordered property declarations. Computed offset remains derived and excluded. Exact final candidate SHA256 is `e17ad778f6279f17eda31b764ea2d52edbe82de50aa44d69a1a995d4d51b75d8`.

The patch comparison uses the complete production function's anchor. It verifies that inserting this one line into the retained original produces the entire candidate file byte-for-byte. There are no other native changes in that file. This does not claim the working tree is pristine upstream; prior accepted project changes remain part of the original snapshot.

## DEBUG comparator

The separate DEBUG-only `SpecifiedKeyframeArraysAreEqual` also omits composite. Its only call is a BuildProperties assertion; it does not control production assignment, replacement, rebuilding or sampling. BuildProperties clones the full Keyframe list and later restores that clone. Updating the diagnostic would strengthen it, but no necessary correctness dependency requires that change for this repair.

The existing assertion must not be used as proof of composite preservation. The proof companion must observe the full clone/restore path and getter field directly. Its exact extraction and mutation anchors must distinguish the production and DEBUG functions. This review makes no second web-visible defect claim.

## Seventy regression cases

The final WPT SHA256 is `a140ac383d46dbfb9b922876e768c9e06069cdc82bd6a0a4e909c277fcbf241c`. I read the entire file, including setup, helpers, cleanup, assertions, and CSSOM case. The byte-identical file is used on both sides of the pair.

| Cases | Purpose | Baseline prediction |
| --- | --- | --- |
| 48 | All 16 old/new pairs of four operations, independently for array/no-properties, property-indexed scalar, and property-indexed list input; null target getter | 36 failures, 12 identical-input passes |
| 12 | Rendered bidirectional replace/add/accumulate/auto changes under replace/add effect defaults | 10 failures; two same-rendering-value passes |
| 4 | Change only first or last endpoint to add/accumulate | Four failures, expected 35px |
| 1 | Repeated and reversed changes | Fails at first changed operation |
| 1 | Value changes along with operation | Pass, expected 41px |
| 2 | Effect-default change for auto versus explicit add | Both pass; specified operations remain distinguishable |
| 1 | Invalid new offset on an already populated effect | Pass; TypeError preserves previous getter and style |
| 1 | CSSOM updates to an existing CSS animation's explicit keyframe operations | Fails, expected 40px |

The independent checker generates every full subtest name and predicts the original status from the omitted-field behavior and ordinary length arithmetic. All 70 predictions match the raw baseline log exactly. The case counts are not inferred from the root summary.

The tests use a 10px underlying margin, 20px and 40px endpoints, duration 1000ms and currentTime 500ms while paused. Replace gives 30px, addition or one accumulation gives 40px, and one additive endpoint gives 35px. These are exact simple values and require no sleep. Getter cases distinguish add/accumulate and explicit/auto even when present rendering agrees. The CSSOM case reaches the shared style-driven array setter after computed-style flushing; the invalid-input case exercises processing atomicity. Cleanup cancels animations and removes elements/styles through testharness helpers.

This is a meaningful bounded matrix. It does not cover all offsets, missing endpoints, timeline ranges, CSS value types, property ordering, JS conversion side effects, allocation failures, or mutation observer scheduling. Those are either existing tests or the formal/native bridge's declared scope, not implied by 70 passes.

## Independent raw pair authentication

Original session 41338 exits 1 with exactly the expected new failures. Candidate cycle 92678 records build exit 0 and candidate WPT exit 0. For each run, 27 before/after pins agree, all 25 retained nonbinary snapshots authenticate, and all six explicitly absent metadata paths remain absent. The historical binary hashes are retained; reproduction does not require later binaries to match them.

The independent checker parses both raw JSONL logs and checks their complete 417 unique outcome keys: 410 subtests plus seven harness results. It also checks the receipt's full copied status records equal the raw events and that the original/candidate key sets agree. All 70 new candidate subtests pass; all 340 existing subtests remain PASS; all seven harness results remain OK. Only the production C++ source pin and the two binary pins change across runs. WPT sources, shared resources, configuration and metadata pins remain identical.

| Result | Original | Candidate |
| --- | ---: | ---: |
| New PASS | 18 | 70 |
| New FAIL | 52 | 0 |
| Existing PASS | 340 | 340 |
| Harness OK | 7 | 7 |

The root receipt and its six evidence hashes authenticate before this comparison. The format receipt binds the final native/WPT snapshots. Lint reports zero errors and one warning because ESLint ignores the WPT file; `-W` makes lint exit 1. This is accurately retained as a warning gate, not falsely reported as lint exit 0 or full JavaScript lint coverage. The browser execution itself parses and executes the WPT.

## Formal scope review

I read the complete producer SCOPE and its versioned addendum; snapshots are retained here. The full ordinary-WAAPI contract is appropriate: specified-state and derived-state observational refinement over arbitrary finite successful-update, failure, default-change and context-refresh sequences; actual whole comparator, property equality, both setters, getter, offset computation/refresh, property rebuilding and segment construction; independently derived state and ordered provider/event traces.

The addendum resolves the initially soft qualifications: complete named-range normalization and missing-segment helpers remain mandatory; actual SetComposite/context entry paths execute; finite specified offsets are distinct from unresolved computed NaNs; +/-0 receive native controls; raw declaration identity is quotiented only under immutable structural equality/serialization congruence; the DEBUG helper supplies no preservation proof. A failure to implement these gates requires explicit root scope revision.

CSS-generated augmentation/override bookkeeping and full Rust sampling remain traced source/WPT boundaries. The proof cannot assume provider outputs already equal the expected final state or segment list. Getter dictionaries, stored fields, offsets, segment state and event gates must be independently observed. Scope approval is not acceptance of an uncompleted proof.

## Reproduce

Run `verify.py --expected-manifest DIGEST` using the external handoff digest. The verifier authenticates every local input before executing the independent checker. It then rederives the exact patch, per-case baseline predictions, raw paired outcomes and source identities. The earlier normative adjudication remains in `artifacts/css-animation-composite-independent-v1/REPORT.md` with its separate frozen manifest; this artifact adds final patch/WPT review.
