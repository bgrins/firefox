# Independent tab-boundary adjudication

18 October 2026. **Accept two narrow defects for separate native/WPT repairs.**
This reviewer independently read the source, current primary specification and
history, authenticated root's browser receipt, and recomputed the expected
observations without using the producer's `equal` or `expected` fields. No new
browser, build, native compilation, formal proof or Git action was performed.

| Defect | Independently checked runtime evidence | Verdict |
| --- | --- | --- |
| Zero tab size adds intrinsic width | 18 max-content/min-content/shrink-to-fit rows reserve 50px or 70px instead of 40px | Accepted |
| Positive tab size at exact stops with zero font | Prefix 0 and 20px put marker at 0 and 20px instead of 20 and 40px | Accepted |
| Tiny positive tabs | Literal subsequent-stop rule and historical minimum-width policy differ | Excluded pending policy decision |
| Whitespace partition effects | Separate existing family, including two failed ASCII/pre-line controls | Excluded from these repairs |

## Evidence authenticity and actual execution

Root session 27156's driver exited **1**, not zero. Its 141 observations completed,
but two unexpected partition controls made the aggregate run fail. The browser
was subsequently terminated with exit -15; that is not a successful browser test
exit and is not used as such. Root's summary pins the raw receipt; this review
checks that digest, all 52 before/after runtime pins, all 15 metadata-absence
checks, the delivered probe and Ahem HTTP hashes, successful font loading,
computed support gates, devicePixelRatio 1 and 40×20px `AB` calibration.

`check.py` independently checks 18 zero-tab differences, two zero-font exact-stop
differences, and 15 relevant passing controls. The eight incremental/fresh
controls from the overall survey are not correctness oracles: in particular,
zero-tab mutation and fresh construction both reserve the same wrong 50px.
They help rule out a stale-state-only explanation.

The local binary identifies itself as 160.0a1, build 20261018140112. This review
makes no release-browser claim and no novelty/regression-range claim. The survey's
87-file integrity check with live inputs exited zero before this review. Its
archived source agrees with the live source and root receipt used here.

## Focused WPT baseline independently accepted

Root's separate zero-tab baseline session 56364 exited 1 as expected. This review
read the WPT and independently counted its retained statuses: 108 static zero
cases and 18 mutation-to-zero cases fail with 50/70px versus 40px; all 18 positive
controls pass. Thirteen existing reftests pass; one retains its expected failure.
All 42 input pins and 13 absence checks match before/after. The three writing
modes and two directions measure the appropriate physical dimension for inline
size, and every static case first verifies its `AB` reference is exactly 40px.
The mutation baseline stops at its failing zero assertion; restoration to 20px
is not yet executed in those 18 cases. The candidate run must exercise that
remaining assertion. This establishes the WPT baseline gate, not native repair
acceptance.

## Independent normative derivation

Fresh [CSS Text 3 phase II](https://drafts.csswg.org/css-text-3/#white-space-phase-2)
and [tab-size](https://drafts.csswg.org/css-text-3/#tab-size-property) snapshots are
retained. Zero size explicitly suppresses tab rendering. For positive size, the
next stop is strictly beyond the current position; the extra-stop threshold is
strictly less than half ch. These two boundary obligations survive either
interpretation of the disputed tiny-positive policy.

For zero-sized tabs in unwrapped `pre` text, deleting the tab preserves glyph
advances. With the authenticated Ahem calibration, `A` plus `B` advances 40px.
There is no soft wrap, hanging trailing space or soft hyphen in these strings,
so min-content and max-content both measure that same line. The absolutely
positioned auto-width fixture has ample available width; its shrink-to-fit width
must likewise be 40px. The explicit fixed-width marker tests independently show
zero tab displacement during ordinary layout. This is a measurement mismatch,
not evidence of damaged glyph painting.

For a zero-sized font and positive **length** tab-size 20px, the tab grid remains
20px while half ch is zero. At positions 0, 3 and 20, the least strictly greater
grid points are 20, 20 and 40. The threshold comparison cannot move these further
because a positive advance is not less than zero. Root's observations are 0, 20
and 20. The middle case is the decisive non-boundary control. Numeric tab size
would collapse with the font and is deliberately not used for this defect.

CSSWG issue 2883's 2018 discussion and bug 1432198 comment 7 describe a half-ch
minimum, while current prose describes one subsequent stop. Neither permits a
zero-sized tab to consume half ch, nor a positive tab to remain on its current
stop when half ch is zero. No tiny-positive algorithm change is approved here.

## Complete helper and three caller audit

Searchfox finds exactly one definition and three direct calls in
`nsTextFrame.cpp`. Exact local source is retained.

1. `AdvanceToNextTab` computes `nextPos = x + minimum`, then returns
   `ceil(nextPos / width) * width` for positive width, or `nextPos` otherwise.
   At width zero this adds minimum. At minimum zero and exact positive-width
   stops it returns x.
2. `PropertyProvider::CalcTabWidths` requires positive width. It walks tabs and
   clusters, adds spacing before each item, invokes the helper for tabs, rounds
   the returned delta for `TabWidthStore`, assigns the new block-relative
   position, and adds after-spacing. Cache reuse, intrinsic/no-line-container
   early return and stale property removal were inspected. Its caller
   `GetSpacingInternal` only enters tab processing when computed width is
   positive; zero width therefore gets no normal tab spacing.
3. `AddInlineMinISizeForFlow` constructs the intrinsic provider with null line
   container, identifies preserved tabs, adds before-spacing, obtains the tab
   width, invokes the helper even at zero, and assigns after-spacing. Its null
   run, text-combine and overflow-wrap-anywhere early paths, word measurement,
   saturation, trimming/break branches and final skip state were inspected.
4. `AddInlinePrefISizeForFlow` likewise does its own preserved-tab processing,
   including zero width. Its first-letter preparation, null run/text-combine
   early paths, simple-glyph batching, line measurement, newline handling,
   line-empty updates and trailing-state handling were inspected.

`ComputeTabWidthAppUnits` takes absolute lengths directly in app units; numeric
values use the containing block's space advance plus letter/word spacing.
`MinTabAdvance` caches half the rounded zero/average-character metric supplied
by `GetMinTabAdvanceAppUnits`. The arithmetic source and observed zero-font
boundary agree; this does not independently verify every font provider.

## Separate minimal repair proposals

Both proposed patches apply independently to the retained original source.
They are artifact-only and have not been compiled or browser-tested.

### A. Zero tab identity

`zero-tab-proposal.patch` adds an early `aTabWidth == 0.0` return of `aX` in the
shared helper. It repairs both intrinsic callers, while ordinary zero-tab
spacing continues to bypass the helper. Positive widths, zero-threshold behavior
for positive widths, and negative-width fallback are byte-for-byte unchanged.
The exact-zero guard also covers negative floating zero.

A blanket nonpositive return would also change negative derived widths, which
can interact with negative letter/word spacing even though authored tab-size is
nonnegative. That behavior is outside these accepted witnesses. The explicit
zero guard keeps this repair narrow rather than silently choosing a negative
spacing policy.

WPT gate: independent 40px reference with 20px Ahem, `A\tB` and `A\t\t\tB`,
number zero and length zero, max-content/min-content/auto shrink-to-fit. Keep
positive 20px tab controls and fixed-width zero-placement controls. A calculated
negative length clamped to zero is useful extra parser coverage but not required
to establish the helper defect. Require font readiness/calibration. Test the
actual content box so an oversized overlay cannot conceal the surplus.

### B. Strict next stop at zero threshold

`zero-threshold-proposal.patch` adds a separate branch for positive width and
exactly zero minimum: `(floor(x / width) + 1) * width`. The existing positive
minimum formula and nonpositive-width behavior remain unchanged. This patch does
not require A and does not repair A; the two guards have disjoint conditions.
They can later coexist in either order.

WPT gate: font-size zero, positive length 20px, visible 20px marker, exact inline
prefixes 0 and 20px, nonexact 3px control; compare 20/40/20px marker offsets.
Use DOM insertion without incidental markup whitespace. Add multiple tabs as a
small composition control and retain `white-space-zero-fontsize-002.html`.
That existing test has a nonzero text prefix and does not force an exact stop.

For very large floating inputs, adding one to a quotient or multiplying back
can lose strictness. These proposals do not claim to solve every representational
limit. Ordinary app-unit witnesses are exact; a future native corpus must bound
representable inputs and include signed origins/equality cases before a universal
numeric claim. Do not replace minimum-positive behavior with a new tiny-tab
policy in this commit.

## Meaningful formal boundary

A scalar lemma alone would not explain the intrinsic discrepancy: the important
fact is that ordinary layout skips a zero-width helper call while intrinsic
measurement still executes it. Use two layers:

- **Independent Lean relation:** ordered tab-stop grid, explicit zero-size
  identity, positive-size strict successor when threshold is zero, and a
  parameterized positive-threshold policy. Prove these boundary rules,
  translation by whole grid steps, composition over finite sequences, and
  zero-tab deletion invariance for line advance. Restrict any minimum-threshold
  agreement theorem to the domain where historical and literal policies agree.
- **Source-bound native transitions:** extract the complete helper, complete
  `CalcTabWidths`, complete intrinsic min/pref flow functions, the complete
  `GetSpacingInternal` gate and the width/minimum metric functions. Include
  provider construction and lazy minimum/cache behavior in the adapter scope.
  Use owned initialized arrays and frame/text-run identities. Stub shaping,
  skip-character maps, line-break/hyphenation, style/font metrics, allocation,
  text autospace and line-container discovery explicitly; retain branch
  structure and actual tab iteration. Do not rewrite the three loops into a
  hand-created miniature renderer and then call that exact native evidence.

For an initial companion, define a transparent text-run provider domain with
simple nonnegative glyph advances, preserved tabs, no discretionary breaks,
zero auxiliary spacing and finite in-range app-unit positions. Exact complete
functions can compile with other provider branches available; the theorem must
only claim the constrained reachable domain. Exercise early returns and
preservation branches as separate native controls. A subsequent extension can
admit spacing, newline/line-state and continuation sequences. The complete
renderer, glyph shaping, bidi ordering, real font tables and reflow scheduling
remain assumptions, not theorem conclusions.

Lean plus an isolated C++ capsule is appropriate. Prove universal agreement
between an independently specified event fold and a native-shaped model over
finite provider streams, then separately compare extracted C++ state and tab
width records on a bounded corpus. Audit axioms, compiler/SDK pins, source
recovery, object lifetimes, integer casts and rounding. Require compiling,
fully executed semantic mutants for removing the zero guard, returning the
current exact stop, and losing caller before/after spacing. Keep compilation
errors and invalid provider graphs as diagnostics. No formal implementation is
claimed in this review.

## Exclusions and integrity

Tiny positive 2px/4px tabs remain policy-sensitive. The pre-line ASCII and
LRM/combining partition findings remain in the existing partition family; this
review neither accepts nor rejects their separate repair. Existing bidi/spacing
expected failures do not invalidate the isolated unwrapped zero-boundary cases.

`verify.py` authenticates this report, source proposals, snapshots and independent
checker. `--live` checks the six retained native/test/font/metadata origins; historical
survey and runtime evidence are frozen snapshots. `RESULTS-v1.json` records the
successful independent evidence checker, not an executed patched browser or
proof. Root still owns standalone WPT baseline/candidate gates and final native
acceptance.
