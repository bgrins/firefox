# Ahom/LF oracle and upstream adjudication

## Result

The root-owned combined-build browser run has eight failures, 305 passing subtests and one OK file. Independent parsing of retained raw JSONL agrees with the receipt; all recorded pins are stable. All 24 calibrated CJK controls pass. Failures are exactly the Ahom prefix, normal breaking, narrow width, before-LF adjacent/nested partitions, in both preserved-LF modes and both transforms. This establishes a browser-visible discrepancy on that combined project build. It is not an original-release browser result or a completed formal acceptance.

## Normative trace

Question: can splitting the same styled text immediately before LF remove the opportunity between the following two Han characters?

1. CSS Text 3 §1.5 requires inline boundaries to be ignored for text-processing adjacency. The exact anchor is [text-encoding](https://drafts.csswg.org/css-text-3/#text-encoding). Adjacent Text nodes introduce no styled boundary; the nested spans have identical inherited styles and zero decorations.
2. [White-space values](https://drafts.csswg.org/css-text-3/#white-space-property), [segment transformation](https://drafts.csswg.org/css-text-3/#line-break-transform), and [line-breaking details](https://drafts.csswg.org/css-text-3/#line-break-details) preserve LF and require its forced break for pre-wrap/pre-line, while permitting wrapping.
3. [Normal word breaking](https://drafts.csswg.org/css-text-3/#valdef-word-break-normal) follows customary rules. Han letters ordinarily admit intervening opportunities; [UAX14 LB31](https://www.unicode.org/reports/tr14/#LB31) supplies the default ID–ID opportunity. CSS permits language tailoring and UA choice of precise strictness rules, so LB31 is not an unconditional CSS mandate for every lang=th string.
4. The CJK suffix remains within one Text node in every fixture. The boundary-property ambiguity in §5.5 does not apply there. The independent suffix calibration and whole/after-LF controls establish this UA’s chosen opportunity. Splitting before a preserved LF cannot change text adjacency or that suffix’s styles.

Verdict: REACHED for partition invariance under these identical-style fixtures. The fixed suffix expectation is supported by customary Han breaking plus explicit calibration; the test makes no claim about correct Ahom dictionary boundaries. Typographic-unit splitting and shaping-boundary exceptions are rejected routes: no surrogate/grapheme or CJK pair is split, and spans add no shaping decorations. This trace uses the current ED fetched on 2026-10-19 (14 August 2026 document), not an unidentified historical TR. webspec-index was unavailable; exact primary HTML and verified anchors are retained.

## WPT adapter review

The root adapter preserves the original strings, scalar-aware Range offsets, four partitions, both white-space modes and transforms, three word-break modes, and calibrated narrow/wide widths. It independently asserts suffix wrapping for every fixture; it does not infer expected results from candidate output. Retain all existing controls and exact paired bytes. For a landable revision, use a descriptive title, spec help links above, an assertion meta, and remove the diagnostic pre/output JSON. Explicitly set text-transform:none for the none variant and line-break:auto/overflow-wrap:normal/text-wrap-mode:wrap to document defaults. Keep calibration failures as failures, never skips. No extra browser matrix is proposed.

Generic sans-serif and fallback are deliberate measured providers, not Ahem coverage. The test requires positive individual advances and pair advance greater than either single by >2px. The midpoint then fits either single and excludes the pair with >=1px margin. Ranges identify both Han scalar positions; comparing suffix y uses a 1px tolerance against a 48px line-height. The test does not compare total heights (prefix fallback may differ), and its partitionEqual diagnostic only compares suffix wrapping. A deterministic font would improve portability but must cover Thai/Ahom/Han explicitly; do not silently use Ahem fallback. Browser acceptance remains root-owned.

## Upstream identity and minimal repair

The current official GitHub API records [#8143](https://github.com/unicode-org/icu4x/pull/8143) merged 2026-08-27 at fb5e25f59bb1addb8da87d592ecb810923383257. It optimizes cache consumption and retains the problematic UTF-16 handler. The web cache displayed an obsolete draft; the retained API record resolves that discrepancy.

The separate [#8144](https://github.com/unicode-org/icu4x/pull/8144), merged 2026-08-31 at a9cbb9cda7cc0b1e832ace6a0f633fc6a3f3726d, deletes the truncating UTF-16 handler. It preserves original encoded input slices and uses encoding-specific widths in the generic handler. Its exact diff structurally removes both our diagnosed causes. It changes multiple iterator/encoding paths and builds on the cache refactor, so the proposed local encoding+width repair is a smaller backport. We have not executed our witness on that upstream revision and do not claim its whole segmentation implementation proved.

[#8574](https://github.com/unicode-org/icu4x/pull/8574), commit 436f666f87c0dbb18b5aab39478b80f6d324e0bc dated 2026-10-08, separately defers the final complex-run boundary to normal rules. That issue is relevant to end-boundary semantics, not a substitute for encoding/width repair, and remains outside this repair’s claims.

## Candidate contract

For every valid decoded scalar admitted to a complex run, encode_utf16 must preserve its scalar value and produce exactly Utf16::char_len units. Temporary input and both initial/subsequent cache seeks then use the same coordinates. The current generic cached seek already uses char_len. Invalid-value replacement is harmless for the actual SA domain (no surrogates), but is not unconditional preservation of arbitrary malformed UTF-16. Provider boundaries must be increasing, in range, and scalar-aligned; the repair does not validate arbitrary malicious provider offsets. Restored iterator/current-position state, EOF behavior, cache subtraction, run-end semantics and allocation failure remain unchanged. Supplementary runs can allocate twice as many units as the old truncated buffer; this is required correct representation, with ordinary vector capacity behavior retained.

## Historical font provenance

The language standalone receipt names base 32226ddf3a29d58a52291babebdff2a5a7ce46c6 and HEAD 11482ee213bf63c749b6d205c2c7591d783bdaa8. Root now independently obtained both revisions’ gfx/thebes/gfxFont.cpp and gfxFont.h. ROOT-PROVENANCE-v1.json records both equal the separately retained current supplements: cpp 1a469c462fa1fb37a82831ede96fb8c948b236e7497efc270ca7dae95644d740; header 71b21b7f48e6a7ca37839479c508094c2a5c2526315b784417eb1b5f140b9571. This closes the byte-identity gap for those files; it does not prove font provider semantics.

## Remaining work

Root’s corrected native source requires exact paired browser/build acceptance and independent provider/full-breaker replay. All original failed partition/locality claims remain retained. Conditional consumer theorems are not upgraded to universal conformance by this browser evidence.
