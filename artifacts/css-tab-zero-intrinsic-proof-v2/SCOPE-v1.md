# Zero-tab intrinsic width: proposed formal scope

18 October 2026. **Plan only; approval required before implementation.** This
companion concerns the exact-zero tab-width guard accepted in the independent
boundary review. Positive-width/zero-font strict-successor repair is separate.
Tiny-positive tab policy, whitespace partitioning and font shaping are excluded.

## Source and browser boundary

The retained original `nsTextFrame.cpp` hashes to
`2a3310a04863c604492cc9fb6ca29a7c18555fd23e6941dbc19a39afab855ab8`.
The formatted candidate hashes to
`3f3ca6b3e0d66ff0892f37f7808853cecedb5cd1db2f384a46cd8e31fde08ed9`.
It adds only `if (aTabWidth == 0.0) { return aX; }` to `AdvanceToNextTab`.
The checker authenticates the complete files and exactly reconstructs this
single insertion. No native candidate execution is claimed by this plan.

The independent review accepted the baseline: 108 static and 18 mutation zero
cases fail; 18 positive controls pass. The WPT covers three writing modes, two
directions, three intrinsic sizing modes, three zero syntaxes and one/three tabs.
Parent owns the candidate build and browser test. Candidate acceptance must also
execute the positive restoration assertion skipped after baseline failures.
Browser evidence and this companion remain separate gates.

Current primary [CSS Text 3 phase II](https://drafts.csswg.org/css-text-3/#white-space-phase-2)
requires zero-sized tabs not to render. For the unwrapped Ahem fixture, the
independent oracle is the measured advance of `AB`: 40px. The original intrinsic
paths add half ch per tab while ordinary layout bypasses tab spacing at zero.
The spec is interpreted into the model; no mechanical spec-to-Lean conversion is
claimed. The retained primary snapshot and prior review document the derivation.

## Required source-bound execution

Extract whole definitions, including early returns and branch structure. The
capsule must compile the actual retained function bodies; adapters must not
replace the loops being verified with a fresh implementation.

| Required body or declaration | Obligation |
| --- | --- |
| `AdvanceToNextTab`, original and candidate | Exact branch and arithmetic execution, direct input corpus, unchanged nonzero branch |
| `GetMinTabAdvanceAppUnits`, `PropertyProvider::MinTabAdvance` | Real metric rounding expression and lazy minimum cache; provider metric is explicit |
| `ComputeTabWidthAppUnits` | Length and numeric cases, containing-block metrics/spacing resolution and zero computation |
| Both out-of-line `PropertyProvider` constructors and relevant member declarations | Actual initialization, ownership, null intrinsic line container, sentinel/cache and display-vs-reflow mode |
| `PropertyProvider::GetSpacing` and complete `GetSpacingInternal` | Actual `HasTab` dispatch, zero-width gate, buffer initialization, tab/justification ordering and `aIgnoreTabs` recursion guard |
| `PropertyProvider::CalcTabWidths` | Complete cluster loop, before/after spacing, helper call, rounded records, cache reuse, stale property removal and limits |
| `AddInlineMinISizeForFlow` | Complete simple-glyph batching, tab path, range/state updates and early exits |
| `AddInlinePrefISizeForFlow` | Complete simple-glyph batching, tab path, line-state updates, first-letter entry and early exits |
| Exact relevant inline spacing/cache accessors and `TabWidthStore` operations | Do not silently stub a bridge that determines actual tab displacement or stored records |

The extractor will use unique signatures with a checked lexical body boundary,
record exact body hashes and source offsets, and reject missing or duplicate
matches. Preprocessing choices (including DEBUG) and extracted declarations will
be explicit. Any necessary signature adaptation will be a counted inventory
with before/after hashes and executable exact reversal; ordinary bodies remain
verbatim. A fresh source-only replay must close over all inputs without depending
on preparation output or the live tree.

`GetSpacingInternal` is substantial and references font/script/autospace helpers.
It remains complete, with external providers implementing the constrained domain
below. Compiling those references does not establish the inactive branches.
If the complete required loops cannot be compiled without replacing their
semantics, stop and present a revised scope; a helper-only capsule does not meet
this plan. Public `AddInlineMinISize`/`AddInlinePrefISize` continuation traversal,
actual font inflation and full reflow remain caller premises. Their invocation
and continuation behavior are not proved by the per-flow companion.

## Transparent provider domain

For the universal caller agreement theorem, quantify over every finite sequence
of simple glyphs and preserved tabs, every valid nonempty or empty window, and
all admissible initial advances. Glyphs have nonnegative integer app-unit
advances. Tabs have zero glyph advance, are non-simple cluster/ligature starts,
and remain in a consistent identity skip-character map. There are no newlines,
soft breaks, hyphenation, text-combine, first-letter splitting, collapsed or
hanging whitespace, discretionary glyphs, bidi reordering or overflow-wrap
special handling in this theorem domain. No auxiliary letter/word/justification
or autospace spacing is present. Provider outputs are consistent across callers.

Additional exact premises:

- Source and glyph arrays have valid lengths and stable owners; ranges and
  original/skipped offsets agree; no out-of-range sentinel dereference occurs.
- `HasTab`, `CharIsTab`, compressed glyph flags, cluster flags and text buffers
  agree. Glyph range measurement equals the sum of supplied advances.
- Font/style objects, containing block and line container have stable identities;
  metric and width results are deterministic for the invocation. Numeric zero
  tab size resolves to zero under finite spacing/metric products.
- Real layout has a line container and valid reflow/cache state; intrinsic
  providers use their actual null-container constructor and do their own tabs.
  A zero-width run need not fabricate a `TabWidthStore`: the normal gate skips it.
- Inputs and every intermediate glyph sum, position, cast and range offset stay
  within their declared representable bounds. The theorem states this premise,
  rather than assuming every arbitrarily large finite string fits `nscoord`.
- Allocation succeeds in the theorem domain. Separate controls exercise absent
  runs and cache state. No simulated OOM is called a valid measured sequence.

Shaping, Unicode classification, font selection, actual glyph buffers, style
resolution, continuation discovery and reflow scheduling are explicit providers.
A text run with tab glyph advance accidentally set to a nonzero value is invalid
input, not a counterexample to the real caller agreement theorem.

## Independent models and required universal theorems

Implement two definitions that do not call each other:

1. A specification event fold over glyph/tab tokens, tracking measured advance.
   A zero tab is an identity step. Glyphs add their supplied advances. For
   nonzero widths, use an explicit parameter for the existing advancement
   policy; this permits preservation claims without endorsing the disputed
   tiny-positive rule.
2. Native-shaped transition interpreters for min flow, pref flow and the normal
   spacing/cache path. They retain native cursors, batching, range boundaries,
   zero-width gate, initialization, tab records and public line fields. The
   normal zero path bypasses `CalcTabWidths`; positive-width normal controls
   execute it. Neither interpreter may call the specification fold to determine
   a branch, a winner or an output.

Required Lean results, universally quantified over the finite domain above:

- Zero-width scalar identity and finite fold deletion invariance for **measured
  advance**. Include leading/trailing/consecutive tabs, empty and tab-only runs,
  concatenation, and continuation-like sequential invocation with matching state.
- Both intrinsic interpreter advances and normal measured advances agree with
  the independent fold at width zero, subject to the explicit provider/range
  premises. Establish batching invariants and termination; do not prove only a
  manually simplified loop presented as the native model.
- Original and candidate helper models agree for every nonzero width, using the
  same policy parameter. Lift this pointwise equality to unchanged caller state
  and traces for identical valid nonzero-width provider streams. This includes
  the negative-width fallback at the helper level; normal `CalcTabWidths`
  requires positive width and must not be invoked with invalid negative inputs.
- The separate model algorithms agree on the measured projection, while their
  public metadata is related by explicit per-caller invariants. Tab deletion
  does **not** promise identical `mLineIsEmpty`, `mAtStartOfLine`, cache records,
  cursor values or provider call counts. In particular, a tab can intentionally
  mark the pref line nonempty even while contributing zero advance.

For zero-width agreement, compare a common semantic event projection: ordered
source indices and glyph advances, tab identity steps, and final measured value.
Expanding a glyph batch into its input token indices is structural, not an oracle
that recomputes a branch result. Raw native calls/count/order and cache/public
state are separately compared to each caller's native-shaped model on the
bounded corpus; they need not equal a token-deleted run or another caller.

Audit every theorem declaration and its quantified hypotheses and print axioms.
No `sorry`, admitted theorem, unsafe proof shortcut or imported axiom beyond
Lean's declared standard foundations. Proof failures and executable semantic
counterexamples must be recorded separately. This proves agreement between
models; it does not prove universal refinement of the C++ compiler or renderer.

## Floating-point and integer limits

The rational/integer model is not an IEEE-754 or reflow proof. Native fixtures
must retain actual `gfxFloat`, `nscoord`, conversions and rounding helpers, or
explicitly authenticate exact extracted definitions of those helpers. Do not
substitute Python rounding or an assumed cast policy.

- C++ equality to `0.0` accepts both positive and negative zero. Direct helper
  cases must include both signs, positive/negative finite x, and signed-zero x;
  compare returned bits for the candidate zero branch. Returning x avoids the
  original addition and preserves its represented value. `MinTabAdvance` can
  still be evaluated by a caller before the helper call; no skipped metric-call
  theorem is implied by the early return inside the callee.
- Preserve nonzero positive and negative widths with identical original and
  candidate results under the same compiler/options. Include fractional values,
  subnormal finite inputs, near-zero values and representable boundary inputs
  in helper-only tests where all exercised arithmetic is defined. Exclude
  signaling NaNs, floating exception environments and unbounded infinities from
  the preservation claim. No fast-math assumptions may silently erase signed
  zero or permit reassociation.
- Intrinsic casts truncate to integer; normal tab record conversion rounds the
  difference. Zero-tab caller proof initially uses integer app-unit inputs with
  zero auxiliary spacing, so neither operation introduces a fractional loss.
  The compiled corpus still checks the actual operations and signed-zero cases.
- Bound ordinary sequence sums strictly inside integer/saturation limits;
  separately test defined saturation branches as preservation controls. Never
  use out-of-range casts or signed overflow as semantic witnesses.
- Font metric rounding and numeric tab-size multiplication are executed but real
  font metrics remain assumptions. A finite-factor requirement excludes zero
  times infinity producing NaN. The positive-width zero-font defect remains
  present and must not be described as repaired.

A future bitvector/SMT or IEEE formal layer can strengthen this bridge, but is
not required or claimed by this scope.

## Native corpus, independent oracle and mutations

Use owned initialized frame, font, buffer, glyph, spacing and cache storage.
Pin compiler version, target, SDK, flags and numeric type widths; compile without
fast math. Attempt supported undefined-behavior/float-cast checks, record actual
sanitizer capabilities, and never claim unavailable ASan passed. If instrumentation
is added, prove exact removal/recovery and compare ordinary/instrumented public
state and provider event order/count without evaluating a provider again to log.

Generate a deterministic corpus with a raw versioned input schema and a separate
oracle derived from that schema. It must include:

- Empty, tab-only, leading/trailing/consecutive, and glyph-tab-glyph sequences;
  counts beyond the one/three browser witnesses; multiple valid subranges and
  sequential calls; several glyph advances, initial offsets and minimum metrics.
- Zero length/numeric results, both signed zeros in direct helper tests, positive
  width controls and negative-width helper/intrinsic fallback preservation where
  inputs remain valid. Keep cases testing unresolved tiny-positive policy tagged
  preservation-only and do not use a normative spec oracle for them.
- Both intrinsic full loops, normal `GetSpacing` zero bypass, positive normal
  `CalcTabWidths`, cache fill/reuse/extension/removal and null-line-container
  intrinsic early return. Separate null-run, text-combine, first-letter-provider
  and special-wrap controls from the universal simple-stream domain.
- Additional nonzero integer spacing controls to detect loss of before/after
  ordering, with an explicitly versioned provider extension and raw expected
  traces; these controls do not expand the first universal zero-spacing theorem.
- Original vs candidate runs, independent Lean exports, exact public fields,
  spacing buffers, tab records, cache limits, result classifications and provider
  traces. Every valid semantic mutant must compile and execute the complete
  applicable corpus. Any input-domain restriction needs an explicit separate
  corpus and cannot be reported as the main full-corpus result.

Semantic mutations: remove/negate the zero guard; return zero instead of x;
change the guard to nonpositive (negative-width preservation witness); skip one
intrinsic tab assignment; drop before or after spacing; alter normal gate/cache
behavior. Require specific mismatches and successful execution. Lean definition
mutations need successful theorem-elided executable counterexamples in addition
to failed proof checks. Missing extraction, corrupted source hashes, unsafe
provider arrays, invalid range/count metadata and assertion-only failures are
integrity/diagnostic controls, not semantic mutation kills.

## Deliverables and acceptance order

After approval, implement in a new artifact-only proof directory. Deliver source
pins, exact-body extraction and adapter inventory, independent Lean models and
axiom audit, full native fixture/checker with raw inputs and outputs, semantic
and diagnostic mutation receipts, compiler/SDK records, independent raw oracle,
source-only closure, and a frozen manifest/integrity verifier. Preserve rejected
preparations with their actual exit status; final replay uses a fresh output dir.

Acceptance requires: exact pinned delta; full required bodies; audited universal
model theorems; bounded original/candidate/native/Lean agreement with independently
derived expectations; mutation evidence; source recovery and packaging; parent
fresh replay and independent review. Browser candidate WPT remains a separate
required native repair gate. If any planned gate is missing, report partial work
and complete it or obtain explicit scope revision; do not silently narrow the
milestone to scalar arithmetic.
