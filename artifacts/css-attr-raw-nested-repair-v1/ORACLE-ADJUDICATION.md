# Explicit adjudication of the existing attr-cycle oracles

The current algorithm and independent root review support correcting two expectations in attr-cycle.html. Neither correction is a metadata allowance. Both must be exercised on original and candidate binaries before acceptance.

## Earlier typed-to-typed-to-raw case

```text
--y: attr(data-foo type(*))
data-foo: attr(data-bar type(*))
data-bar: attr(data-foo)
```

The current fixture calls test_attr_cycle, expecting the property's previous invalid/default result. The guard sequence is property(--y), attribute(data-foo), attribute(data-bar). The final raw read returns data-foo's literal text, without another attribute guard. Proposed replacement calls test_attr_no_cycle with:

```css
"attr(data-bar type(*))"
```

This row predates the later WebKit addition discussed below; this review does not assign it a specific introduction commit. It is a second oracle conflict identified during this full-file review. Its new reduced case has not been run separately in a browser.

## Later two-raw-reads case

```text
--x: attr(data-foo type(*), abc)
data-foo: attr(data-bar type(*), fallback)
data-bar: attr(data-foo) attr(data-bar)
```

The existing expected value is abc. The same three distinct guard contexts are entered, then both raw calls produce strings. Proposed expected value:

```css
"attr(data-bar type(*), fallback)" "attr(data-foo) attr(data-bar)"
```

This exact reduced scenario disagreed with the current-spec prediction in both the installed release and the local branch probes. The existing oracle was added through WebKit PR 61321 / bug 310641 and exported as WPT commit 7a585ef3249c5c385edeb3738526efa54d9cc0bd. The prior sealed audit preserves the patch, issue/PR context and source snapshots. That implementation history explains the expectation but does not override the current normative branch ordering. No cross-engine consensus or new upstream ruling is claimed.

## Scope of the existing-file edit

Only these two helper-call expectations change. The later case's comment is corrected, and the stale attr-notations help URL is replaced with attr-substitution. Static argument enumeration confirms all 37 helper calls remain in order and the other 35 call argument lists are unchanged. Existing metadata is untouched.

The earlier type(<ident>) raw-self case and the transitive length example retain their invalid outcomes: a returned CSS string cannot satisfy the required identifier/length syntax. Such outcomes alone do not establish a repeated substitution context. Genuine typed self/mutual cycles, cycles through var(), unused fallbacks and both attribute-resolution-order variants retain their existing assertions.

For validation, use the corrected fixture on both the used-fallback baseline and raw candidate. Expected failures caused by these two corrected oracles are original observations, not grounds to weaken metadata. Require their repair and unchanged behavior for all remaining existing cases. A separate run with the historical fixture may document the deliberate oracle incompatibility, but must not be presented as an unexplained regression or silently waived.
