# Independent MathML tab-cache origin review

## Verdict and identity

The exact candidate has no blocking issue found in this bounded native/source review. The root's retained WPT pair fixes the four glyph-range failures (12 PASS / 4 FAIL to 16 PASS), with 260 ignored-properties subtests unchanged. The additional ten boundary controls are proposed here and were not executed by this reviewer. Their runtime gate belongs to root; this report does not infer its outcome.

Authenticated producer: `css-mathml-tab-cache-design-v1`, manifest `8d6aa7b4e1aaac3715537e29ffe88b9e7ecba2644322d4d983c74978a551e50e`, freeze `3386ad09986aa7ea651da69bdd57876d42e55108dc019465a7bdb190280c29bf`. All 36 inputs were authenticated before use and copied under `producer/`. Candidate complete `nsTextFrame.cpp`: `ec44924925012a5c059b5bd6c43e609cc6ecb1838a1e73918518fcb7c17d4077`. Native patch: `542a671949aa0fc3dd585abec99641589180417670274360cd4664728ce3c03c`. Existing 16-case WPT: `fd3bec6f92f95ac83ad076a681e9343c0fd7d293416e29f557f5ea4580843734`.

This reviewer did not author the native repair or original 16 tests. The ten additional controls and review checker are reviewer-authored. No native edits, Git operations, compiler, or browser execution were performed by this reviewer.

## Source cause and exact repair boundary

The Range path is `AbstractRange::CollectClientRectsAndText` → `GetPartialTextRect` → `ExtractRectFromOffset` → `nsTextFrame::GetPointFromOffset` → display `PropertyProvider` → `GetPointFromIterator` → text-run advance measurement. It is not the separate `GetCharacterRectsInRange` path.

`PropertyProvider::CalcTabWidths` uses the provider start as the coordinate origin for cached tab positions. Reflow already removes MathML token leading whitespace independently of `WhiteSpaceIsSignificant` and line-start state. The old `GetTrimmedOffsets` returns early for significant whitespace, so a later display provider starts before the prefix. `GetSpacingInternal` then applies cached relative positions using that mismatched start. A tab's extra advance can be assigned to A, and clipping can reduce B's reported range to zero. The preserved diagnostic has calibrated Ahem glyph widths 160, 160, 0 and 80 where isolated same-style ASCII advances are 20. Token element-box width inconsistencies are a separate observation; this repair is not accepted as their solution.

The candidate changes only `GetTrimmedOffsets`: MathML is allowed into leading trimming even for significant whitespace or away from line start, while `NoTrimBefore` still forbids it. A second significant-whitespace return precedes trailing trimming. Non-MathML control flow is unchanged for every combination of the seven relevant Boolean conditions. The supplied branch model checks all 128 combinations; it is a finite source-condition audit, not a universal compiled C++ theorem.

The second return is required to preserve significant trailing-whitespace behavior in consumers using default or `NotPostReflow` flags. A mutant omitting it changes the trailing-trim decision for significant MathML text `A\t` at line end. `review.py` rejects that decision. This is a native compatibility contract, not a normative assertion that a MathML trailing tab has a particular advance. Range initializes display with `NoTrimAfter`, so Range glyph tests alone cannot discriminate this mutant.

## Preserved-newline and empty-range reasoning

`GetTrimmableWhitespaceCount` uses normal/nowrap trimmability, including LF and tabs, rather than consulting the style's significant-newline flag. Both width branches test `count < aLength`; zero length returns before forming or reading the text pointer. Two-byte trimmability retains the existing combining-sequence guard. The patch does not alter this helper.

`ReflowText` first restricts the current length through the first significant LF, then supplies at most `length - 1` to leading trimming so the LF remains assigned to the current frame. Its post-measurement endpoint normalization increments `charsFit` when the measured endpoint is at that LF. It computes `contentLength = offset + charsFit - GetContentOffset()` and publishes it with `SetLength`. A post-reflow `GetTrimmedOffsets` scans `GetContentOffset()/GetContentLength()`, not the entire continuation chain. Given current published content ranges, it can trim the final LF of an otherwise whitespace-only frame but cannot scan into the following frame. A new display start after that LF is not literally equal to reflow's start before it; no all-input equality of provider origins is claimed.

For an all-whitespace frame interval, the bounded count can consume the interval completely: start becomes its end, length becomes zero. Empty intervals remain empty. The source's existing post-reflow assertions, valid frame/content interval, up-to-date continuation boundaries, skip map and zero-advance newline storage remain native caller/provider premises. This static review is not a proof of those heap and shaping premises. The targeted runtime controls exercise leading/interior LF and whitespace-only-to-text rebuilding without relying on line count or newline advance assertions.

There are also **pre-reflow consumers**. `PropertyProvider::InitializeForMeasure`, used by `GetPrefWidthTightBounds`, explicitly passes `NotPostReflow`; `SetupJustificationSpacing(false)` does likewise. The post-reflow frame-boundary argument does not establish origin equality for them. The patched helper still returns a bounded subinterval of their supplied content range, but it can skip LF and whitespace before a later glyph when their range spans a preserved newline. These consumers therefore retain a separate supplied-range/measurement semantics boundary. No universal newline-origin or full intrinsic-measurement equivalence follows from this patch review or the Range WPT.

## Independent WPT oracle and portability

[CSSOM View Range geometry](https://drafts.csswg.org/cssom-view/#dom-range-getclientrects) derives a selected text fragment's horizontal bounds from its advance. The tests select full ASCII A/B units in horizontal text with Ahem, zero added spacing, no transform, and explicit same-style calibration. This avoids surrogate, combining-cluster and partial-ligature ambiguity. `mtext` also avoids the source's math-script treatment used for other token elements.

[MathML Core CSS styling](https://w3c.github.io/mathml-core/#css-styling) currently requires nowrap treatment of white-space on MathML elements. Consequently the tests do not require a browser to implement preserved tabs or line breaks for `pre`. Each A/B glyph still has the calibrated advance whether the browser follows Core nowrap or the current Firefox preserved-whitespace path. No expected tab width, token width, leading position, or line count is asserted. These tests therefore do not standardize Firefox's broader `pre` behavior.

`proposal/token-whitespace-range-controls.html` has ten cases: normal/pre crossed with leading LF, interior LF, trailing tab, whitespace-with-LF reconstruction, and tab-only reconstruction. Whitespace-only Range reads exercise the empty path; finite/nonnegative width is merely a sanity condition. The substantive post-mutation oracle is calibrated A/B advance and equality to a freshly created same-content/style token. There are no optional-precondition exits. These cases are deliberately limited to the concrete risk in this patch.

Primary documents were read through the web tool on 2026-10-19 and the rendered source extracts are retained in `spec/WEB-READ.json`. Direct HTML retrieval failed DNS resolution; `spec/RETRIEVAL.json` records the failures. The capsule does not pretend to contain complete HTML snapshots or independently authenticated literal HTML anchor IDs.

## Evidence and regressions

The copied raw root logs are parsed independently by `review.py`. It checks one suite end per phase, exact test status counts and stable before/after pins. Between phases, the only changed common pins are `nsTextFrame.cpp` and the two browser binaries. The candidate source hash matches the reviewed complete file. This authenticates the recorded runtime evidence; replaying this review does not rerun Firefox.

`ignored-properties-001.html` is the relevant existing MathML gate and has 260 passing subtests in both phases. Its retained metadata has an assertion-count annotation; it has no expected-failure exemption. Its white-space case is normal, so its success alone does not cover preserved-newline behavior. `pre-wrap-tab-001.html` is an optional ordinary HTML trailing-tab/wrapping regression identified through Searchfox and retained with metadata-presence inventory. It has not been executed here. Non-MathML source-branch preservation already substantially limits that risk; do not broaden testing without a remaining concrete concern.

Searchfox discovery covered `GetTrimmedOffsets`, `GetTrimmableWhitespaceCount`, MathML token flags, existing MathML whitespace tests, and CSS Text tab tests. This installed CLI rejects `--permalink`; the failed query is noted rather than constructing an unverified revision URL. Source evidence uses complete authenticated local snapshots and function names. Metadata absence is not execution evidence. No new issue-priority or novelty claim is made.

## Inspected scope and limits

Inspected: complete changed function and helper; reflow leading trim/LF clipping/length publication; display/measure initialization and justification setup; tab cache setup/application; Range offset geometry; token marking/reflow and mtext script distinction; original test, focused proposal, producer diagnostic and root exact paired statuses. The complete source files are retained for independent expansion.

Not established: universal frame lifecycle/memory safety; arbitrary font, bidi, complex-script, justification or continuation correctness; element-box/intrinsic sizing repair; all MathML whitespace conformance; broad cross-browser runtime execution. No formal proof acceptance is implied. The candidate is a narrow alignment with the already-existing MathML reflow leading-origin choice.
