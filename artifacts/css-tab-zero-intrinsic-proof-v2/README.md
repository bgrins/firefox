# Zero-tab intrinsic sizing companion

This artifact binds the exact-zero `AdvanceToNextTab` repair to complete extracted
Gecko callers, independently specified Lean models and an isolated native corpus.
It follows the approved `SCOPE-v1.md`. It is not a universal C++/IEEE or renderer
verification, and does not repair the separate positive-width zero-font boundary.

## Replay

From a checkout containing the declared toolchain:

```
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-tab-zero-intrinsic-proof-v2/verify.py --live
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-tab-zero-intrinsic-proof-v2/check.py --out NEW_DIRECTORY
```

`NEW_DIRECTORY` must not exist. Native compilers and Lean are isolated processes;
there is no Gecko build, browser invocation, WPT change, Git operation or network
access in the replay. A source-only package retains the paths in
`SOURCE-ONLY-v1.json`. Selected compiler/Python/Lean binaries and SDK settings are
pinned; their complete installations and the operating system are not hermetic.

`EXECUTION-v2.json` identifies the accepted terminal replay and rejected earlier
preparations. `SUMMARY.json` in the accepted output reports actual counts, theorem
names, changed mutation witnesses and diagnostics. A green diagnostic is not a
semantic mutation, and failed preparation output is not accepted evidence.

## Source binding

`source/original.cpp` and `source/candidate.cpp` are complete snapshots of
`nsTextFrame.cpp`. The checker independently reconstructs the single added
exact-zero guard. The candidate SHA is
`3f3ca6b3e0d66ff0892f37f7808853cecedb5cd1db2f384a46cd8e31fde08ed9`.
The original SHA is
`2a3310a04863c604492cc9fb6ca29a7c18555fd23e6941dbc19a39afab855ab8`.

`extract.py` extracts complete lexical bodies with unique signatures. Every
ordinary compiled body must appear exactly once, byte-for-byte, in its generated
translation unit, and every body receives a source range and SHA. No statement
inside an ordinary extracted body is rewritten or instrumented. This makes the
source recovery gate exact containment/recovery of every extraction, without an
insertion-removal certificate being needed. Mutant edits have explicit match
counts and are emitted as separate translation units.

The inventory includes both provider constructors and complete member declarations,
`GetSpacing`, complete `GetSpacingInternal`, both `CanAddSpacing` predicates,
`ComputeTabWidthAppUnits`, the minimum metric/cache functions, the shared helper,
complete `CalcTabWidths`, both intrinsic flow functions, exact spacing accessors,
and actual `TabWidth`, `TabWidthStore`, `TabwidthAdaptor` and `ApplySpacing`.
Gecko `NS_round`, `NS_lround`, integer rounding, ceil/clamp and saturating-add
bodies are extracted too. `gfxFloat`, `nscoord` and coordinate limits are checked
against their retained native declarations. This is not a helper-only capsule.

The adapter provides the surrounding frame/style/font/text-run APIs. `RefPtr`
is a nonowning pointer facade over fixture-owned objects, not a reference-counting
verification. Frames, font objects, glyph arrays, character buffers and line
state live across every provider call. Each glyph vector has a retained sentinel
slot beyond its logical length; empty windows and end pointers remain valid.
Actual tab stores are allocated, retained on the frame and deleted; a stale
store control verifies real deletion. There are no temporary owners bound to
stored references.

Builds use C++17, `-O1`, no fast math, warnings as errors, dangling diagnostics,
undefined-behavior and float-cast-overflow sanitizers with recovery disabled.
`DEBUG` is not defined; the conditional display-cache assertion loop is therefore
not executed. Other active assertions remain enabled. ASan is not executed and
no ASan result is claimed. Real font shaping, script classification, style
resolution, allocation failure, continuation discovery and reflow are providers.

## Independent specification and native-shaped models

`Tab.lean` has an independent token-event specification (`specStep/specRun`) and
separate native-shaped interpreters. The intrinsic interpreter accumulates a
pending glyph batch, commits it at tabs/end, tracks cursors, lazy minimum
initialization, both line flags and provider events. Its mode distinguishes min
flow from pref flow. The normal interpreter tracks measured advance separately
from the block-relative offset, tab records, cache initialization and provider
calls. Neither native-shaped interpreter calls the specification to compute a
transition or result.

The universal theorems quantify over arbitrary finite token lists and arbitrary
initial mathematical advances. They prove:

- Scalar zero identity and tab-deletion invariance of measured advance, including
  empty/tab-only sequences, concatenation and sequential measurement.
- Complete normalized observation equality between the independent specification
  and intrinsic interpreter: advance, cursor and ordered glyph/tab events.
- Normal zero-width agreement and preservation of its cache, offset and provider
  calls, because its tab calculation gate is bypassed.
- Zero-width agreement across caller models, with explicit initial observation
  agreement; metadata preservation facts are separate.
- Unchanged original/candidate nonzero-width policy, lifted to full model state
  and trace. This does not endorse the unresolved tiny-positive CSS policy.

`Bridge.lean` models invocation boundaries, sliced/sequential intrinsic calls,
normal cache extension/reuse/display and the ordinary glyph measurement consumer.
The consumer sum is separately proved equal to the independent identity fold.
The normal provider alone does not paint or measure glyphs; its consumer's supplied
advances are an explicit premise. `Main.lean` decodes the raw corpus and exports
full bounded state, spacing arrays, tab records and provider event sequences.

The native-shaped model is an abstraction of the simple-provider reachable domain;
it is not a formal semantics of C++ pointer arithmetic or a proof that a compiler
preserves the source. Its pending-batch invariant explains the actual loops.
Complete native bodies are compiled, then compared on a bounded corpus. Inactive
renderer branches do not acquire theorem coverage merely by compiling.

## Provider domain and numeric boundary

The universal measured-advance bridge uses preserved tabs, simple nonnegative
integer glyph advances, consistent identity skip maps, no soft/hard breaks,
no auxiliary spacing, no hanging/collapsed whitespace, and valid in-range sums
and casts. Tokens and metric results are consistent across callers. The theorem
is mathematical; applying it to a real text run requires these premises.

Native coverage also exercises numeric versus length widths, spacing before/after,
initial offsets, cache variants and early returns. Those extensions have a bounded
raw oracle; they do not silently enlarge the universal zero-spacing theorem.
The exported Lean corpus is exactly the unsaturated length-width, zero-spacing, ordinary
provider domain, including slices, sequential flows and cache operations. Other
native cases are explicitly counted separately.

Both floating zeros satisfy the guard. Direct helper fixtures retain input and
output bits, including signed-zero x. Nonzero positive and negative widths retain
the old computation; fractional and finite subnormal controls execute outside
the integer model. Signaling NaNs, infinities, floating exception environments,
out-of-range integer casts and signed overflow are excluded. `MinTabAdvance` is
still evaluated before the callee's early return; no skipped-provider-call claim
is made. These facts are native evidence, not a rational-to-IEEE proof.

Tab deletion concerns **advance**, not identical metadata: a pref tab can mark a
line nonempty while adding no width. The normal zero-width path keeps its cached
block-relative offset unchanged while the consumer still measures ordinary glyphs.

## Wire format and independent oracle

Every line starts with `id mode`. Mode 0 adds three unsigned 64-bit bit patterns
for x, width and minimum. It emits the returned double's bit pattern.

Other modes add:

```
n begin end kind width minimum initial letter model flags split token[n]
```

Tokens are `-1` for preserved tabs or nonnegative glyph advances. `kind` is 0 for
length and 1 for numeric width; the numeric fixture uses `width / 20` spaces with
a supplied 20-app-unit space metric. `split=-1` means one flow invocation; another
valid offset splits intrinsic measurement into sequential calls. Letter models
0 and 2 retain the extracted spacing predicates. Flags are absent text run 1,
text-combine 2, special wrapping 4, initially nonempty line 8, and first-letter
provider 16.

Modes: 1 minimum flow; 2 preferred flow; 3 normal spacing; 4 normal prefix/extension/
reuse; 5 reflow followed by display-cache retrieval; 6 direct intrinsic/null-container
cache early return; 7 direct normal no-tab calculation; 8 the same with an owned
stale frame property. Each output includes its ID and full relevant state.

Provider event codes: 1 text-run acquisition, 2 first-letter provider, 3 property
lookup, 4 property attachment, 5 autospace initialization, 6 initial range/skip
provider, 7 property removal, 10 minimum font metric, 11 glyph range measurement,
20 space-font lookup, 21 space-font metrics, 22 frame font metrics, 30 optional
break, 31 forced break. These are actual provider calls logged by the adapter;
providers are never called again merely to log an event. Pure field getters and
glyph classification predicates read supplied immutable data and are not logged;
the event inventory above defines the observed provider boundary. Unmodeled rendering APIs
are explicitly outside the capsule.

`oracle.py` derives expectations from raw inputs using a separate event interpreter,
without consulting native output, producer expectations or Lean output. All
original and candidate rows must match it. `cases.py` generates valid initialized
cases; the checker authenticates row IDs/counts and rejects malformed ranges.
Lean exports must additionally match the original and candidate native rows for
the stated domain. No missing rows can count as success.

## Semantic controls and limits

Each native semantic mutant compiles and executes the complete valid corpus,
then must produce a specific differing record. Mutations cover the exact-zero
guard, returning the origin instead of x, an overbroad nonpositive guard, both
intrinsic assignments, before/after spacing, the ordinary gate, cache state and
independent removal of saturation from each intrinsic loop.
No assertion failure or compile error counts as a semantic kill.

Each Lean definition mutation has a separate rejected proof compilation and
successful theorem-elided reference/changed executable witness. The six witnesses
cover identity, glyph batching, tab transition, normal zero gate, pref metadata
and tab records. Axiom auditing covers every theorem in both model files.
Extraction ambiguity/missing bodies, corrupt pins and invalid ranges are diagnostic
controls only.

Root owns the accepted standalone Gecko/WPT repair. Retained browser reviews are
historical evidence; this artifact does not require today's browser binary to
match that historical binary and does not run a browser. The positive-tab zero-font
bug and tiny-positive policy question remain separate work.

## Version 2 review corrections

The original v1 remains frozen and unaccepted against the full approved scope.
This successor addresses the four findings in the independent v1 report.

`check.py` validates every replay dependency before importing executable helper
modules. Its diagnostic makes a temporary source copy, prepends a file-creation
side effect to a helper, and invokes the direct replay entry point. The expected
result is hash rejection before the marker file exists. This is an integrity
control, not a semantic mutation.

Negative intrinsic inputs use a valid nonnegative numeric tab-size (one space),
a 20-unit space metric, and negative letter spacing (-21, -30, or -40 units).
The extracted width resolver therefore returns a negative width without violating
the length/nonnegative-number assertions. Both complete intrinsic callers execute
leading/consecutive/interior tabs, sequential windows, multiple initial positions
and minimum advances. The negative width sentinel forces recomputation on each
tab. Full raw provider traces and separate metric-call counts check that behavior.
The nonpositive-guard mutant must disagree in each caller, while original and
candidate records remain identical. These controls do not expand the zero-spacing
universal model domain.

Saturation is a separately validated domain. It uses ordinary 20/40-unit glyphs
and initial positions near the coordinate limit, with zero minimum advance.
`boundaries.py` checks every relevant batch addition and positive-tab conversion
before compilation, retains enough signed-integer headroom for the semantic
mutants, and requires actual cap/infinity branch witnesses in both loops. Each
loop's no-saturation mutant must successfully execute and disagree. These rows
are intentionally excluded from the unsaturated Lean execution bridge; claiming
ordinary integer addition models saturation would be incorrect.

`Bridge.lean` retains the unconditional mathematical algebra and adds
`windowValid`, `providerAgrees`, and `admissiblePrefixes`. They state valid source
windows/indices, an extra glyph sentinel slot, identity skip mappings,
consistent tab/glyph classification, zero spacing, consistent measurement/width/
minimum results, and representable current/pending/summed states at every prefix.
`zero_window_applicability` explicitly takes those premises and proves the final
coordinate bound and agreement with both the supplied measured range and normal
caller model. `admissible_final` extracts the final bound. These predicates are
formal model applicability conditions, not proofs that arbitrary native objects
satisfy them. Actual pointer ownership, C++ semantics, floating-point refinement
and renderer scheduling remain outside the theorem.
