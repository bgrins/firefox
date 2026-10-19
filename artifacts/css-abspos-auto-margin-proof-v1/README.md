# Absolute-positioned automatic margins

This companion binds an explicit inset-provenance and signed-residual model to the revised native caller/helper. It does not prove complete absolute positioning, anchor resolution, or reflow.

## Normative contract and correction

[Position 3 overconstrained insets](https://drafts.csswg.org/css-position-3/#resolving-inset-overconstraint) floors the inset-modified containing-block size at zero by adjusting the weaker inset. [Automatic margins](https://drafts.csswg.org/css-position-3/#abspos-margins) then allocate signed remaining space. CSSWG issue11478's August2025 resolution and November reaffirmation are retained with all eight comments. Its still-open editorial status is not treated as unresolved policy. The primary snapshot and resolution identities are in `SPEC-v1.json`.

For an axis with automatic margins and two definite anchor-resolved insets:

```
raw = containingSize - (startInset + endInset)
available = max(0, raw)
residual = available - fixedMarginSum - borderBoxSize
```

The floor applies before subtracting fixed margins. Any automatic inset forces automatic margins to zero. Numeric offsets alone cannot identify this case: earlier layout can replace an automatic inset with a finite number. Consequently, the model retains separate `autoProvenance`, numeric offset, and unresolved-sentinel fields.

The repaired caller reuses its existing anchor-resolved side flags, moves the margin call after computing both axis flags, and passes them in inline/block order. The helper retains sentinel checks as an additional defensive zero branch. It first resolves margin tags and returns from that axis when neither margin is automatic, avoiding unused residual arithmetic.

Historical failure examples:

- CB100, insets0/0, fixed margin150, border box20: the correct residual is−70; the old misplaced floor gives−20.
- CB100, insets60/60: floored IMCB0 gives residual−170 for fixed150 and residual30 for fixed−50, with border box20.
- An automatic start inset numerically resolved to130, definite end0, automatic start margin, fixed end−50, and border box20 must keep the automatic margin0. A missing provenance flag would compute30 after moving the floor.

## Mathematical model

`Margins.lean` uses unbounded integers, tagged automatic/fixed margins, explicit inset provenance, and a result paired with `geometryEvaluated`. Initial automatic margin values are zero; fixed margin values may be signed. The geometry flag denotes demand for the residual calculation, not an operational proof about all C++ effects.

Twenty-one audited theorems cover no-auto preservation without residual demand; zero allocation with either auto-inset flag or a retained sentinel; one-auto-side assignment; preservation of fixed sides; both-auto conservation; inline safe allocation of negative space; block splitting; at-most-one-unit split remainder; representability of both split outputs given a representable signed residual; conservation against the floored IMCB, including the composed definite-inset resolution pipeline; both-auto floor compatibility; and the three concrete failure examples, including negative-odd truncation.

For block splitting, `half(r)` is truncation toward zero, explicitly defined by sign. The second side receives `r-half(r)`; for−21 the split is−10/−11. For two inline auto margins and negative residual, start stays0 and end receives the residual. These existing helper rules are retained. No theorem silently substitutes Euclidean negative division for C++ truncation.

The no-auto theorem imposes no arithmetic-fit premise because that model branch never requests geometry. Other universal integer theorems are not arbitrary-int32 C++ safety proofs. For the source bridge, every evaluated inset sum, CB subtraction, margin sum, floored-size minus margin sum, and final kid-size subtraction must be representable. A positive residual can overflow with a large negative fixed margin and large IMCB; no upstream bound excluding that is proved. Split representability covers only division/remainder allocation once the residual is representable. Positioning and margin-box additions later in the caller remain outside the proof.

The audited standard axioms are `propext`, `Quot.sound`, and `Classical.choice` where used by integer division/simplification. No admitted declarations, unsafe proof shortcuts, or unlisted theorem output are accepted.

## Exact native bridge

Candidate identities:

- `AbsoluteContainingBlock.cpp`: `a2fcecf806b786267b181131c7f204eb40575c75eb4313caa0d794e5efee0824`
- `AbsoluteContainingBlock.h`: `133edbd33195a178ea4cb7fdadb1278b5b5d5f8b7d2a2a9947b3f171d5f84e93`

The bridge extracts the complete `ResolveAutoMarginsAfterLayout` definition and the complete unchanged `ReflowInput::ComputeAbsPosInlineAutoMargin` / `ComputeAbsPosBlockAutoMargin` definitions. It also extracts the exact contiguous provenance/dispatch block from `ReflowAbsoluteFrame`: `StylePosition`, `AnchorPosOffsetResolutionParams::ExplicitCBFrameSize`, all four `GetAnchorResolvedInset` calls, both axis flags, and the final margin call with its actual argument order. The original wrapper uses the original call-before-flags order. The rest of `ReflowAbsoluteFrame` is neither compiled nor represented as verified.

Whole-file before/candidate preservation permits only the reviewed helper changes, caller movement, and header signature/documentation update. Both complete source files are checked, so unrelated edits, helper synchronization changes, or caller flag mutations cannot hide outside the extracted region. The unchanged ReflowInput source is independently pinned.

Adapters implement logical rectangles and six physical mappings, style margin tags, already anchor-resolved inset values, frame property storage, and reflow margin storage. `GetAnchorResolvedInset` returns explicitly supplied resolved values; the bridge records that all four logical sides were queried. **This does not prove anchor functions/fallbacks, automatic-to-zero overrides, resolution caches, or style-provider purity.** Those are input-provider premises. Numeric offsets are supplied after earlier resolution; `ResolveSizeDependentOffsets` and `InitAbsoluteConstraints` are not executed. The candidate's use of the right named API and actual caller argument order is source-bound and finitely exercised.

Logical Size and StartEnd getters count accesses separately in each axis. The no-auto and auto-inset branches must have zero residual-geometry accesses. For an active definite-inset axis exactly four are expected (CB size, offset sum, margin sum, kid size). The bridge also compares the final passed margin, the computed-margin copy, optional UsedMargin property, physical mapping, write/read counts, and the two caller flags. Adapter copies do not prove Gecko's actual setter/property implementation.

## Finite fixtures and controls

The 2,124 fixtures cover six writing-mode/direction mappings, both axes, all four margin-tag combinations, positive/zero/negative fixed margins, positive/zero/negative raw IMCB, all four inset-auto flag combinations, explicitly numeric automatic offsets, retained sentinels, positive/negative odd splits, missing properties when no auto margins exist, and large fixed margins. Automatic inputs start at zero. The other axis is retained as an isolation control.

Before and candidate compile separately with exact bodies. Python arbitrary-precision oracles separately predict each version. Bounded combinations are tests of the helper's explicit input contract, not a claim that every combination is a reachable browser state. The numeric130/negative-fixed example has separate browser evidence in the root's regression gate; no browser was run for this companion.

The large no-auto fixture uses CB6000, fixed margins1,020,000,000 each, and kid size1,020,000,000 in one axis. Original local residual arithmetic stays defined; the candidate avoids it. Removing the early return makes the local residual exceed signed32, which an isolated UBSan guard must diagnose. **Downstream `kidMarginBox` arithmetic can also overflow for these values.** Therefore this fixture demonstrates the helper's local arithmetic-domain distinction; it is not a newly established browser bug or a whole-execution definedness claim.

Eight Lean semantic mutations, six Lean diagnostic guards, nine native semantic mutations, compiler/runtime diagnostics, a large-unused-residual UBSan control, per-source identity corruptions and whole-file-preservation controls are required to be detected. The no-auto semantic mutation first runs on the bounded set and must disagree in geometry counts; its large-case overflow is checked separately. Native semantic mutations otherwise must compile and run cleanly before output disagreement counts as detection.

## Executed development result

The development checker exited0 with all 2,124 original and candidate expectations matched. It detected eight Lean semantic mutations, six Lean diagnostic guards, nine native semantic mutations, four general native diagnostic guards, the separate unused-residual UBSan control, 27 source identity guards, and four preservation mutations. The mathematical model initially had19 audits; two explicit composed-conservation theorems were added for the final21-audit package.

Of the bounded input-contract fixtures,120 changed margin values with all inset provenance flags false. Another1,008 arbitrary numeric/provenance combinations changed; these are synthetic API-routing tests, not1,008 claimed browser defects or evidence that those offset combinations are reachable. The72 explicit numeric-auto regression controls retain their original margin values. Final results are authenticated by `PREPARATION-v1.json` and its receipt.

## Reproduce and commit separation

```sh
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-abspos-auto-margin-proof-v1/check.py --out artifacts/css-abspos-auto-margin-proof-v1/replay-new > artifacts/css-abspos-auto-margin-proof-v1/replay-new.log 2>&1
```

Use a new output directory. `RECEIPT-v1.json` records theorem axioms, extracted hashes, exact fixture inventory, separate original/candidate agreement, changes in values versus geometry access, and all control results. Compiler flags are `-std=c++17 -O1 -Wall -Wextra -Werror -fsanitize=undefined,implicit-integer-truncation -fno-sanitize-recover=all`. Toolchain identities are pinned. `PREPARATION-v1.json` authenticates the terminal producer result; independent replay remains a separate gate.

`prepare.py` creates the manifest and source-only `tooling-paths-v1.txt` before freezing. The companion belongs in a tooling commit preceding the standalone native/header+WPT repair. Generated binaries, replay fixtures and logs are evidence artifacts. No WPT/browser acceptance, anchor correctness, complete negative-IMCB alignment behavior, or entire reflow theorem is claimed here.
