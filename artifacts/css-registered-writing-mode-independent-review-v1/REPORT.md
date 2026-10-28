# Independent writing-mode proposal review

Proposal v2 has a concrete panic path and should not execute unchanged. This is a source review and a small replay of the actual iterator predicate, not an observed Firefox crash.

`ReferenceFlags` declares the new WRITING_MODE single bit after NON_ROOT_DEPENDENCIES and NON_CUSTOM. `for_each_non_custom` uses `iter_names()` and only accepts single bits. The fetched bitflags `IterNames::next` yields a named flag when the original source contains all of that flag and any of its bits remain uncovered. For FONT_UNITS | LH_UNITS | WRITING_MODE (261), it yields FONT_UNITS, LH_UNITS, then the composite NON_ROOT_DEPENDENCIES (261), reaching `unreachable!("Unexpected single bit value")`.

An acyclic source witness is a registered `<length>` value `calc(1lh + 1vi)` with independent fixed font-size, line-height and literal writing-mode. Parsing 1lh contributes FONT_UNITS | LH_UNITS; parsing 1vi contributes WRITING_MODE. Grammar admission keeps the selected logical token, so preparation does not remove this bit before contextual traversal. This does not require a disputed cycle or an open provider.

Move the WRITING_MODE declaration before the composite masks without changing its bit number. The saved replay confirms that this ordering emits the three individual bits. A real mixed lh/logical native or browser control remains required; the eight fixed-lh controls contain no logical unit and do not cover this combination.

## Other bounded findings

The 16 original acyclic cases have a plausible corrected path: direct or substituted logical flags defer early computation; selected providers settle; the admitted specified value is captured without computing it; WritingMode is traversed/applied before that captured value is converted to computed form. The selected-token scan preserves logical references even if specified math simplifies. Invalid grammar, CSS-wide results and an unused logical fallback can remove only the new WM bit. No concrete stale captured-value counterexample was found in those closed-provider acyclic cases.

V2 restores the original LineHeight-to-FontSize SCC edge exactly and removes v1's unconditional LineHeight-to-WritingMode edge. This closes the documented fixed-lh synthetic cycle. Implementation application dependencies remain unchanged, including recursive prioritary application. The provider-settled check gates preparation but does not make ensure_prioritary_property a readiness evaluator; broader open-provider application and genuine logical-unit cycle policy remain explicitly unresolved in the proposal. These limits do not replace the concrete blocker above and are not claims that the 16 acyclic cases fail.

No native files, WPT, index, HEAD, epoch, browser, build or sealed proposal were changed. No compilation or browser callback was executed. Review is bounded to the proposal delta and captured call chain; it is not a whole-CSS correctness proof.
