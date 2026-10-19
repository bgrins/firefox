# LF complex-script partition counterexample

The complete pinned original and language candidate `nsLineBreaker` produce a different break **inside the next line**, beyond LF and the first boundary after LF. This disproves the proposed unconditional native LF-locality admission. It does not yet prove browser reachability or CSS nonconformance.

## Input and native observations

Input scalars are Thai U+0E01, Ahom U+11700, Thai U+0E01, LF, U+4E00, U+4E8C. UTF-16 storage is `[3585,55301,57088,3585,10,19968,20108]`.

| Partition | Complete glyph break vector |
| --- | --- |
| One Append | `0100001` |
| Append first four units, then LF and the CJK pair | `0100000` |
| Append through LF, then the CJK pair | `0100001` |

The only difference is offset 6, before the second CJK character. Both native versions agree, and all calls return success. No ownership or nowrap repair is substituted. Initial storage is zero; distinct sink instances share one run with disjoint base offsets. All callbacks, identities, requests, provider inputs, states and shutdown events are retained in `evidence/*.raw.txt`.

The BMP control replaces Ahom with U+1950: whole and after-LF yield `011001`; before-LF yields `011111`. Its differences are confined to LF and the first boundary after LF. It retains the known raw inequality without the new interior suppression.

## Causal trace

Whole input runs immediate segmentation on the pre-LF word `[3585,55301,57088,3585]`, retains the two CJK units as a new word, then segments `[19968,20108]` at reset. Before-LF partition first buffers the four-unit prefix. The continuation path uses `IsSegmentSpace`, which does not delimit LF, and extends that word with `[10,19968,20108]`. Reset therefore calls the provider once on all seven units. After-LF partition follows the same provider decomposition as whole input.

The independent provider diagnostic `complex-encoding-diagnostic-v1` established the underlying mismatch: UTF-16 complex handling truncates supplementary scalar values to `u16` and uses one-unit complex-cache positions, while general cache consumption advances two units for Ahom. A target can be overshot and subsequent text skipped. That diagnostic freshly rebuilt the actual ICU trie/segmenter and complete Gecko provider. Its manifest is `cd95022d7abf2ae31c6d34d8a4245a12107dcf60d7c44483fe09ce8924753a1b`; it remains a separate immutable artifact.

## Replay and closure

`check.py --manifest-sha <MANIFEST SHA> --lean <pinned Lean executable>` authenticates every source before executing nested helpers, freshly rebuilds the complete retained language/dictionary/provider closure offline, replays these six inputs in both variants, and derives final storage independently from callback identities/base offsets and last-nonzero writes. It reports all difference positions and checks the post-LF-local relation directly. Literal stored traces are regression evidence; they are not the sole oracle for locality or publication.

The nested source capsule remains unchanged and retains its existing fixed finite matrix, Lean checks, complete native bodies and extraction/adaptation records. Resource registration, atom/refcount/container/URI/IPC facades and foreign Unicode providers remain explicit. This supplement does not prove C++ heap semantics, caller readiness, shaping, all native paths or CSS conformance. The earlier receipt documents prior binary execution; the new replay receipt binds the freshly rebuilt binaries separately.

## Browser proposal, not executed

`browser/probe.html` is standalone and exposes `window.probePromise`. It measures the individual CJK widths and pair width, then chooses a narrow width that fits either individual character but not the pair, plus a wide control. It compares whole, adjacent before-LF, adjacent after-LF, and nested before-LF structures. Thai/Ahom, BMP replacement and ASCII prefixes are tested with preserved LF (`pre-wrap` and `pre-line`), normal/break-all/keep-all, and none/capitalize. The observation of interest is whether the second CJK moves to the next line, independently of the number of prefix lines or fallback font widths. There are 72 groups, 288 partition fixtures and 24 suffix-only calibration controls.

Under normal/break-all at narrow width, the isolated CJK pair must wrap; keep-all and wide controls must keep it together. The probe preserves all glyph coordinates and flags a failed calibration instead of treating unsupported metrics as a defect. Adjacent unstyled text nodes isolate chunking; nested spans check actual continuation traversal. A browser run must bind exact live source, binary, served resources and preferences. Font fallback may split construction, so a negative browser outcome does not undo the native counterexample.

CSS Text 3 Editor's Draft (14 August 2026), [white-space processing](https://drafts.csswg.org/css-text-3/#white-space-phase-1) and [line breaking details](https://drafts.csswg.org/css-text-3/#line-break-details), supplies the preserved segment-break and inline-boundary context. The oracle concerns the unchanged CJK suffix, not a claimed normative Ahom dictionary boundary. Exact CSS bug adjudication remains with the root reviewer.

## Effect on the proof

Existing conditional LF measurement and hyphen-provider lemmas remain valid on their explicit local-patch premises. This witness prevents deriving those premises for all admitted source text. The failed raw partition obligation and newly failed LF-locality obligation remain open; excluding Ahom or assuming encoding equivalence would reduce the approved scope. The language-selection repair is unchanged and this is not its regression. Universal successful/fallible source/provider/sink references that intentionally preserve actual native behavior remain independent progress.
