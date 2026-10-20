# Scroll baseline provider: independent native review

## Decision

**ACCEPT_BOUNDED_NATIVE_WPT. Full source-bound formal companion remains pending.**

The exact two-file patch `f23e2c05119aad4303f332659d387a75ba259a8a4ec7c3284b0f4e70c365f5c5` correctly repairs the changed group-relative baseline conversion under the existing API's completed-reflow, parallel-writing-mode and valid-frame geometry premises. No blocking defect was found in the changed native expression, unchanged early branch order, optional handling, or submitted WPT oracle. This is not approval of every natural-baseline provider, fragmentation lifecycle, or unrestricted layout arithmetic.

The provider repair may land independently of the natural-donor change. The natural-donor change should follow this prerequisite or be submitted as an explicitly dependent stack: its additional nested-block provider selection exposes this preexisting provider defect. Source patch independence does not establish semantic independence. This review does not reinstate the donor's withdrawn acceptance or discharge its separate reflow-readiness concern.

## Authenticated target and source roles

`inputs/native` is the exact 98-payload-file producer package. FILES is `1631d0bad4dbd5c654c233fb9747c8c18e80105be8c1c4fe507d6a8aae13cf3b`; FREEZE is `68dd474d92b91a32b6827b3584bd1f92f4a3ef7e8b10c3d80d2c4348bee40c2b`. The closed nested file and directory rosters are independently checked, including rejection of extra caches. Before CPP equals the retained Git object at both packaging bases. Candidate and both genuine standalone CPPs are byte-identical. Independent patch replay creates only the native CPP and new WPT in disposable directories, and reverses to the exact before files.

The API contract and CSSMinMax are retained from authenticated Git providers. Searchfox was used for discovery. `indexed-method-source.log` contains selected locally changed implementation despite the search request; it is not evidence of indexed-upstream identity. The actual source roles rely on bytes and Git identities, not that filename. API-CONTRACT.txt agrees with the selected header's contract. PROVIDERS.json records the five exact provider files.

## Native reasoning

The nsIFrame API returns an inward distance from block-start for First and block-end for Last. For inner size I, outer size O, start border B and supplied baseline A, the last baseline therefore has outer-start position B + I - A. The requested result is O - clamp(B + I - A, 0, O). The candidate implements that expression, with the clamp performed before converting back to block-end distance. The first result remains clamp(B + A, 0, O).

A substitution of the end border alone is valid only with the extra equal-content-size relation and an unclipped baseline. Independent counterexample: O=100, I=200, B=9, end border=11, A=12 gives correct last offset 0, while end-border addition gives 23. A=300 gives the opposite outer-start clamp and offset100. Both are checked against the extracted method, the independent arbitrary-precision oracle and kernel challenges.

For nonnegative signed32 inner/outer sizes and any signed32 baseline, I-A lies in [-2147483647,4294967295]. Even allowing a signed32 border, B+(I-A) lies in [-4294967295,6442450942], comfortably within signed64. First-group addition also fits64. CSSMinMax with O>=0 returns [0,O], so narrowing and final O-result subtraction are safe signed32 operations. This deliberately permits negative baseline offsets, zero-size frames and full signed32 extremes. First-group behavior is preserved whenever its old signed32 addition was defined; newly widened formerly overflowing inputs have no old-defined equivalence claim.

The exact full method preserves the legacy LineLayout/Last non-button block branch before containment. Containment returns absence without asking the child. Child absence does not evaluate the map or geometry. Group, context and writing mode are forwarded unchanged. First avoids the new inner-size query; Last uses it exactly once. These details are tested through observable facade counters as well as output values.

## Independent checks

- Exact method and exact CSSMinMax extraction: 720 bounded before rows, 2848 candidate rows, and 2848 rows for each of two genuine standalone variants; all run at O0 and O2 with terminating UBSan and match an independently written Python integer oracle.
- Seven compiled mutations run at both optimization levels. Six alter numeric/optional results on the corpus; the forwarding mutation is caught by the forwarded group contract. MUTANT-VALUE-RESULTS distinguishes value differences from call-contract differences. The end-border-only mutation has 450 value counterexamples.
- Twelve independent Lean kernel results prove projection range, first preservation, last orientation, intermediate/narrowing bounds, the conditional end-border simplification and concrete boundary refutations. They are challenges to the review's mathematics, not the producer's complete source/caller proof. Only standard axioms appear in the final successful log. The initial failed proof attempt is preserved and excluded from acceptance.
- Source-only relocated replay matches all22 native stdout streams and all12 kernel audits. Three integrity controls reject nested extra files, empty cache directories and provider drift. A false mathematical claim fails compilation; a compiling custom-axiom proof is rejected by the stated axiom policy. No native products or relocation caches remain.

## Browser evidence and WPT review

Independent raw JSON recount confirms 384 submitted cases:72 FAIL→PASS and312 identical status/message controls. Every before failure reaches the final alignment assertion after equal geometry, content-position, overflow removal and restoration checks. Both harnesses finish OK. Pinned input changes between the paired runs are only ScrollContainerFrame.cpp and the two browser binaries. The run receipts are stable before/after.

The WPT covers horizontal-tb, vertical-lr and vertical-rl; ltr/rtl; flex/grid; first/last; four asymmetric/symmetric border patterns; hidden/auto/scroll/clip. Comparing identical text positions against a visible-overflow reference is valid for these parallel-writing-mode, identical-content, initially unscrolled geometries. Clip provides a non-scroll control. There is no unusual numeric-range prerequisite. The [CSS Alignment baseline export rule](https://drafts.csswg.org/css-align-3/#baseline-export), retained in the producer package, supplies the initial-scroll-position and border-clamp semantics; the inward edge convention comes from the native API, not the spec.

The new WPT uses equal content-box sizes and is not by itself evidence against an end-border-only implementation. Existing retained overflow regressions and the independent unequal-size source/kernel cases complement it; no browser mutation experiment or exhaustive overflow/scroll-position coverage is claimed. Adding a focused unequal inner/outer browser case would strengthen future regression coverage but is not required to establish correctness of this narrowly reviewed conversion.

Raw regression recount confirms38 files,24 PASS reftests,675 PASS subtests and14 OK harnesses. Build and scoped lint success are authenticated producer evidence, not repeated builds. The authenticated nested diagnostic receipt has64 geometrically calibrated, stable matched rows; this review does not independently recount the earlier six-failure diagnostic. Both paired and regression browsers contain other pending project repairs; isolated upstream browser success is not claimed.

## Admissions and remaining formal gates

The facade supplies child baseline truth, dimensions, borders, style, block classification and synthesis as explicit inputs. It preserves the changed method and CSSMinMax source, but does not prove those provider implementations, object lifetime, virtual dispatch, Maybe implementation, completed reflow or writing-mode parallelism. Negative outer geometry is outside the valid-frame premise; this review does not turn it into a silent universally quantified case. Legacy synthesis internals and their old arithmetic remain outside the changed expression.

The complete companion must bind all genuine source variants, full branch order, optional/map laziness, forwarding and actual numeric conversions to its independently defined semantics. It must expose rather than assume away child baseline orientation/truth, initial-scroll-position placement, geometry availability, containment and legacy synthesis providers. Fragmented and orthogonal callers require their actual provider/lifecycle premises; no broader equivalence is inferred from the parallel unfragmented WPT. The primitive kernel results here do not close those composition obligations.

The compiler, Lean executable/import runtime and operating system are trusted. Executable/version identities are recorded; this native review does not claim a self-contained or verified toolchain. Replay requires the local retained Git bases for packaging, and the named installed Lean toolchain for kernel challenges.

No shared source, WPT, index, browser or build was modified or run by this review. Only owned disposable compiler/replay products were removed.
