# Quote provider freshness: existing language failure, scoped candidate

The strongest independent next candidate is the already-known `quotes-lang-dynamic-001.html` failure. This audit identifies a concrete two-part dependency gap and provides an uncompiled scratch patch. It is not a newly discovered expected failure, an accepted fix, or a claim that the patch has passed a browser. The active contained-append experiment is unchanged.

The two first-letter failures are separate: `quotes-first-letter-003.html` changes first-letter attachment by removing an id; `004` changes its color. Both keep the explicit quote strings and quote depth fixed. Their red/green generated-content styling failures are not evidence of a stale language provider. This proposal neither changes their metadata nor claims to repair them.

## Source chain and proposed change

1. `nsStyleFont::CalcDifference` includes changed mLanguage in a reflow condition. It does not reconstruct generated quote text. `nsStyleList::CalcDifference` already reconstructs frames when the explicit quotes value changes, so ordinary explicit-pair updates are not the missing path identified here.
2. `nsQuoteNode::Text` resolves auto quotes using the originating element's parent frame language (with the root exception). A child element can have its own fixed lang while the actual surrounding provider changes. Watching only the quote pseudo's own language would miss that case.
3. The inspected QuotesDirty callers cover quote-node insertion/removal. `RecalcQuotesAndCounters` only runs the quote traversal when that dirty flag is set.
4. Even when traversal occurs, `nsQuoteList::RecalcAll` currently republishes text only when depth-before changes. Scheduling a depth-only traversal is therefore insufficient for a provider change at unchanged depth.

The three-file native proposal conservatively marks quotes dirty from `nsIFrame::DidSetComputedStyle` when the frame's language changes, exposing the existing QuotesDirty entry point. The traversal calculates the current string for each real quote and publishes only when CharacterData::DataBuffer().Equals reports an actual string difference. This preserves the existing script-blocked traversal and avoids same-text SetData notifications. The exact CharacterData/DataBuffer APIs are archived, not invented.

This watches potential provider frames, not only quote frames; the existing global dirty bit coalesces repeated notifications. It adds string calculation/comparison on each real quote during existing quote traversals, including traversals caused by ordinary quote mutations. That cost is unmeasured and must be reviewed. A provider-only force flag could preserve the old depth-only work pattern, but would require threading new state through the scope manager and quote lists; no such expansion is included here. Same-flush delivery, first-letter reconstruction interactions, fallible text publication and reentrant dirty signaling still require actual execution.

`native.patch` and `gecko-wpt.patch` are source-only proposals. The latter adds one reftest and its fresh-state reference. PREIMAGES/POSTIMAGES bind three exact native bodies. The quote preimage is the archived append-candidate body, which the active C/O/C owner will restore; it is not the temporary scoped-original source currently being compiled. nsIFrame.cpp is copied from the guarded current body, matching the archived research-checkpoint epoch. nsCSSFrameConstructor.h matches the prior quote archive. Other WIP is preserved by applying only these hunks. The proposal has not been applied to live sources.

## Standards trace

Scenario: a connected parent initially has lang=en; its quotes:auto child is rendered, then only the parent language changes to fr. The child may explicitly retain lang=en. Neither quote depth nor the computed auto keyword changes.

1. [HTML's language determination](https://html.spec.whatwg.org/multipage/dom.html#the-lang-and-xml:lang-attributes) selects an element's own language attribute before inheritance. Changing the parent's attribute therefore changes its language; a child override does not change that parent fact.
2. [CSS Generated Content, quotes:auto](https://drafts.csswg.org/css-content/#valdef-quotes-auto) chooses the quotation system from the parent's content language while the computed value remains auto.
3. [Quote insertion](https://drafts.csswg.org/css-content/#quote-values) selects the resulting string using the current quotation system and depth. Equal depth alone is not a sufficient cache key when the provider changes.

**Verdict: REACHED** for refreshing the generated result consistently with the current surrounding language. This does not standardize a particular CLDR string or mandate a particular invalidation implementation. Existing `quotes-lang-dynamic-001` uses a French-guillemet reference; the additional proposal instead compares dynamic content with freshly constructed content in the final language, avoiding a new fixed-CLDR oracle.

Current official pages and anchors were validated directly; PRIMARY-SOURCES records hashes and deciding excerpts. webspec-index is absent, so the primary-web fallback was used. Searchfox discovery supplied the unchanged style/publication definitions; exact locally relevant bodies are separately archived. Failed/empty Searchfox captures are retained as unavailable evidence, not counted as definitions. The available CLI cannot emit pinned permalinks, so native correspondence is stated by symbols and archived hashes rather than invented revision URLs.

## Bounded next observation

Run the existing language reftest and the new dynamic/fresh pair on original and candidate builds. The new pair includes inherited language, fixed child language under a changing parent, reverse mutation, nested containment, and explicit quote strings as an unchanged control. It flushes the initial state before mutation; it does not force reconstruction afterward. The two fixed-child cases discriminate an insufficient pseudo-own-language hook. The reference uses the same UA's fresh auto quotes; no assumed textContent/computed-style getter exposes generated rendered strings.

Preserve first-letter003/004 as expected failing controls and the contained-append corpus as regression coverage. Do not remove the language FAIL metadata until a paired actual result confirms the repair; no metadata change is part of this proposal. If useful, a separate diagnostic can compare dirty-only versus publication-only components, but no new runner is required. The native patch is source-supported, not instrumented proof of the existing failure's exact execution path.

Validation completed: exact three-native-file scratch apply/reverse; JavaScript syntax check for the new reftest; all owned scratch removed. No compiler, browser or WPT lint execution occurred. Exact-body scoped WPT lint, formatting, compilation and browser evidence remain prerequisites before landing. No Git object/ref/index, canonical or ledger changes occurred.

Formal opportunity: replace the uniform stable Provider premise with per-node current providers and a cache invariant over both depth and rendered text. Model provider-change demand independently of depth-change demand. The ordered-scope calculation theorem remains useful for depth, but it does not prove this invalidation/publication obligation; no duplicate theorem or coverage credit is claimed here.
