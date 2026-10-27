# Corrected verdict: calculation step counts clamp to the conditional range

**Question:** Must `steps(calc(0 / 0), jump-none)` be rejected while finite `calc(0)` and `calc(1)` clamp to two?

**Scenario:** A well-typed context-free calculation, no variables or relative units. This is a current-draft normative assessment, not a browser execution or implementation acceptance.

1. [CSS Easing 1 §2.3](https://drafts.csswg.org/css-easing-1/#step-easing-functions) defines the step count's numeric minimum as greater than one for `jump-none`; [Easing 2 §2.3](https://drafts.csswg.org/css-easing-2/#step-easing-functions) states minimum two. Thus the integer argument's allowed range in this branch starts at two, not one.
2. **The missing v1 link:** [Values 4 §5.1](https://drafts.csswg.org/css-values-4/#numeric-ranges) recognizes ranges stated in prose as well as bracket notation. The accompanying note says prose limitations are equally binding. A conditional minimum is still a range; nothing makes it a distinct non-range syntax constraint.
3. [Values 4 §9.1](https://drafts.csswg.org/css-values-4/#numeric-function) provides the exception to ordinary out-of-range rejection: numeric functions “never cause a declaration to become invalid” merely by returning an out-of-range value. They clamp to the range allowed by their context. Integer rounding does not alter zero or one.
4. [Values 4 §10.9.2](https://drafts.csswg.org/css-values-4/#top-level-calculation) evaluates zero divided by zero as NaN, censored to zero at the calculation boundary. `steps()` is not an enclosing math function; its `calc()` argument is top-level. Censoring changes the calculated number, not its provenance into an authored literal token.
5. [Values 4 §10.12](https://drafts.csswg.org/css-values-4/#calc-range) applies clamping/rounding to that top-level result. Consequently **calc(0/0) → NaN → 0 → 2**, exactly as **calc(0) → 2** and **calc(1) → 2**. The resulting count satisfies Easing's minimum. Literal zero/one remain invalid.
6. [Web Animations timing update, step 4](https://drafts.csswg.org/web-animations-1/#update-the-timing-properties-of-an-animation-effect) uses easing parsing before assigning timing fields in step 5. It supplies no special rejection for NaN inside a CSS calculation; its separate NaN checks concern numeric duration/iterations members. Context-free cases do not need font, target, document or timeline semantics.

**Verdict: REACHED** — the current normative chain requires the calculated NaN count to clamp to two for `jump-none`. The invalid-value expectation imported by WPT 52199 is inconsistent with this chain. A CSSWG decision naming this exact example is unnecessary; the existing general rules already determine it.

## Why the apparent exception does not hold

Easing's invalid-range wording states the function's domain. Values §5.1 itself uses default invalidation for range violations, then §9.1 specifies the numeric-function exception. Applying that exception yields a valid two-step function; it does not ignore Easing's minimum. Reading Easing as a special exception that re-rejects calculation results would also reject finite `calc(0)` and `calc(1)`, undoing the same generic rule. Neither current Easing section states such a math-function exception.

Likewise, an implementation's intermediate positive-integer storage range is not a normative extra validation stage. The real consumer knows `jump-none`, so the applicable final minimum is two. Generic integer clamping to one cannot justify subsequently rejecting the calculation as though it were authored literal one.

## Implementation and test provenance retained

The v1 source audit remains valid. Chromium change 6494566 adds top-level NaN censoring to `GetValueIfKnown`. Its historical parser then clamps to stored positive-integer minimum one and rejects known jump-none counts below two. The same guard rejects known finite `calc(1)`; the invalid NaN test does not demonstrate an intended normative NaN exception. WebKit 278925 deliberately delays math evaluation and clamps jump-none at creation time to two. The WPT 50533 finite expectations agree with the normative chain; the WPT 52199 invalid NaN expectation does not.

CSSWG 7067's explicit top-level NaN-to-zero resolution corroborates step 4. Absence of a steps-specific discussion is no longer treated as a blocker. Historical engine code and WPT chronology explain the conflicting tests; they do not override the specifications. No current engine behavior is inferred from those historical sources.

## Concrete next validation

A corrected local test proposal may replace the invalid-NaN expectation with acceptance and computed two-step behavior, alongside `calc(0)`, `calc(1)`, `calc(0/0)`, `calc(NaN)` and literal zero/one rejection controls. Keep old results and proposed test correction separately identified; do not silently edit metadata to conceal a failing oracle. Check both CSS timing properties and targetless WAAPI parsing/update atomicity. Observe progress at a nondiscontinuous sample against literal `steps(2, jump-none)`.

This resolves the normative oracle hold. It does **not** accept the uncompiled native patch: actual parser, conversion, computation and regression testing remain required, including preservation of literal rejection and other step positions. It provides no new font-context/API decision, no held-120 acceptance, and no new bug count. No native/test/metadata changes or browser execution occurred here.

## Supersession and authentication

V2 supersedes only v1's INCONCLUSIVE verdict, missing-decision demand and corresponding hold recommendation. It references, rather than duplicates, v1's primary-source/discussion captures. V1 remains immutable and all 42 payloads authenticate. Root's reported CHECK mismatch was a manifest-schema comparison error (object versus digest), acknowledged by root; there was no payload mutation. The original substantive mistake was omitting Values §5.1, not a genuine gap requiring a new CSSWG resolution.
