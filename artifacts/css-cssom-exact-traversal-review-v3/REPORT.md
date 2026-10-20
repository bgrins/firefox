# Independent v3 traversal review

**GO for the next reversible Gecko/browser/performance experiment only.** No landing, runtime, speedup or full CSSOM acceptance is implied. V2's actual performance hold remains valid for that implementation.

Authenticated proposal: `css-cssom-exact-traversal-proposal-v3`, FILES `7f38aefc3a57825eff20508e95d183ae571514f128958bb2d0033228e134d6b6` (463 payloads), inner FILES `993dde69e30ebadf821bafb8587baba61f010bfc537600fad61a0839652db5eb` (31 payloads). The native patch is `2aa367b0531bf96a881ca62b8b89b9438f4bfcbe83bdc10fe2c3ef753dc1b9c1`. The inner capsule was authenticated and relocated by manifest before a fresh extraction replay. All prior sealed reviews remain unchanged.

## Specialization and source preservation

I read the optimization recommendation, full changed method, exact v2 delta, public carrier/signatures, wrapper and caller integration. Automated byte comparisons confirm v3's original and v2 roles match the previously reviewed snapshots. Only `nsIFrame.cpp` differs from v2; both headers, `nsLayoutUtils.cpp` including wrapper/metadata integration, and DOMRect are unchanged.

The dispatch partitions calls correctly:

| Mode | Required runtime condition | Preserved operations |
|---|---|---|
| Legacy | Null metadata output | Original nsPoint additions/scaling, flag-dependent positions and stopping |
| Common layout | Nonnull metadata, empty flags, layout source and target | Wide checked sums; plain positions; transform-only stopping |
| Generic wide | Remaining nonnull metadata calls | Wide checked sums; complete original flags/viewport/provider behavior |

The common predicates make the omitted IgnoreScrolling, visual-root and stacking/display-port clauses false. They do not establish exact-result eligibility. Source/ancestor context checks, SVG exclusions, parent/target/APD checks and metadata reset remain in place. The target comparison still precedes transform stopping; the target's own transform remains outside the relative coordinate conversion. The source transformed/zoom early branch is unchanged.

Legacy code has no checked-add operation or runtime metadata branch within its instantiated loop. It still declares some raw scalar locals in the shared definition; this review makes no claim about their optimized machine-code cost. The extra saved PresContext load is a direct field read under the retained frame/context lifetime admission, not a new callback. Three template instantiations may affect code size and inlining.

## SafeAdd sequencing

Every v2 CheckedInt accumulator reaching a continued loop/flush point is valid: signed32 initialization is exact; checked additions return on failure; reset writes zero. On this invariant, a raw signed64 value carries the same mathematical sum.

Each v3 pair computes checked temporary outputs, then commits both coordinates only after both calls succeed. If x fails, omitting y's pure local addition cannot skip a frame/provider call. If y fails, v2 may already have modified a private x accumulator; v3 has not committed it. Both abandon that state through the same null-output restart. No partial or overflow output is read or published. The public SafeAdd uses the same overflow builtin underlying CheckedInt; this is a source equivalence argument, not a newly proved compiler primitive.

Mixed-APD narrowing retains CheckedInt range checks and the original `ScaleToOtherAppUnits` call with the same arguments. APD flush/reset order, ancestor choices, conversion and matrix composition remain unchanged. Thus old-defined matrix preservation and the **full successful v2 wide exact domain**, including v2's expansion beyond the v1 rectangle-prefix filter, are retained by the source argument. No smaller signed32 intermediate filter or frame-depth bound was substituted to improve speed.

The existing restart can execute legacy undefined arithmetic outside the old-defined and supported exact domains. The cross-document witness remains an explicit expected UBSan failure. This review does not claim universal numerical safety or that all possible paths avoid a second traversal.

## SVG provider correction

Before seal, I found that the draft facade's SVG-text boolean and state field could disagree: `IsInSVGTextSubtree` read only the boolean, whereas `HasAnyStateBits` also read the independent state field. A bit-only SVG_TEXT state therefore broke the native accessor equivalence used by the combined-mask optimization.

The producer corrected the facade to the exact native accessor expression and added a bit-only ancestor control. Native source was unchanged. The sealed replay uses the corrected provider; preliminary evidence is retained as development history, not final acceptance. Independent checks cover leaf and ancestor states with either/both SVG bits and an unrelated bit.

Native `IsInSVGTextSubtree` delegates to `HasAnyStateBits(NS_FRAME_IS_SVG_TEXT)`, and `HasAnyStateBits` tests `mState & mask`; unioning the two masks therefore preserves the predicate. The facade's small numeric bit labels are an explicit representation adapter, not the native bit-number ABI. Retained full source/accessor snapshots supply this evidence. A fresh Searchfox attempt failed DNS; the installed CLI also rejected `--permalink`. No unverified permalink is presented.

## Independent checks

Fresh manifest-only replay completed 20 variant/optimization runs at O0/O2 with UBSan and the retained Mozilla checked-arithmetic headers:

- Original/v2/v3 agree on 168 matrix/ancestor/operation/method-count configurations per optimization; full normal v2/v3 logs agree.
- 2,048 generated v1-admitted finite chains, v2 expanded-domain witness, two wide-domain cases, metadata/cache/self and corrected SVG controls pass.
- Seven semantic mutants are rejected. Six fail normal cases; the suppressed overflow-check mutant intentionally passes normal cases and fails the positive/negative injected x-overflow controls.
- Eight signed64 accumulator injections per optimization exercise doc/offset, x/y, positive/negative failure sequencing and single restart. These are deliberately injected private states, **not reachable small frame histories**.

Additional independently authored checks compile v2 and v3 at both optimizations: 48 combined-flag/viewport/transformed dispatch configurations, 16 SVG state representations, four both-coordinate/negative-wide/expanded-domain/final-clipping cases, and 81 direct SafeAdd-versus-CheckedInt operand pairs. The complete outputs agree. Direct primitive boundary operands are arithmetic controls, not browser reachability evidence.

The extraction uses complete method bodies but explicit frame, scale, viewport and affine-matrix providers. It does not compile full headers/Gecko translation units or execute actual 3D, perspective, SVG, APZ, clipping or frame-lifetime machinery. Compiler-driver identity was checked before replay; installed backend, SDK and standard-library behavior remain external. The independent relocation additionally checks canonical paths, regular entries and directory roster; no general untrusted-archive security guarantee is attributed to the producer's simpler checker.

All compiler sessions reached terminal success. Temporary executables were removed; sources, diagnostics and expected-failure logs remain. No production, Git, browser or shared-build mutations were performed.

## Reversible driver and remaining gates

`DRIVER-REVIEW.json` pins the reviewed v3 scripts. Their changes from the reviewed v2 driver are the proposal reference, explicit per-WPT DOMRect snapshot and increased timing batches. The page's validated parameters admit 100,000 iterations, 11 samples and 10,000 warmup calls. Analyzer counts agree: 6.6 million measured calls per process, 39.6 million overall, 396 batches, and 10 ns/call per integer-millisecond timer tick. Restoration, exact outcome comparison, expected failures, geometry/checksum/visibility controls and fresh profiles remain intact.

No driver blocker was found. Root must bind final INPUTS/HEAD and candidate/test/script identities before execution. Higher resolution does not remove the fixed phase order, two processes per phase, build differences or drift concerns. Actual full compilation, unchanged 23-file correctness outcomes and measured distributions remain required. The source optimization is not evidence that v3 is faster. Full original safe-origin/provider/lifecycle obligations remain open.
