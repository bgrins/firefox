# Font style threshold companion

Artifact-only implementation of approved DESIGN-B, with reusable complete caller extraction for the eventual DESIGN-A companion. The candidate patch remains `design/threshold-proposal.patch`; it changes only `StyleDistance` and applies independently of A. No live Gecko/WPT files, builds, browser runs, or Git state were changed by this work.

## Claims

`Threshold.lean` proves 24 kernel-checked theorems. The independent spec model visits ordered angular intervals and their directions; the native-shaped model separately computes integer-scaled distances. The universal domain is ordered, strictly positive or strictly negative angle intervals, with same-sign requests, each within the exact signed 8.8 domain −90..90 degrees. Italic fallback is separately proved for strictly positive intervals, including strict preference for an actual italic face.

Theorems cover inclusive endpoints and containment, the inclusive ±11-degree boundary, positive/negative symmetry, pairwise order, finite-list minimum membership, italic order/minima, and unchanged normal/oblique-only arithmetic. Finite-list theorems characterize all minimizers; they do not establish an ordered identity-list implementation or A's lexicographic theorem. Zero-touching, sign-crossing and other cross-kind policies are excluded from spec agreement, with unchanged/native compatibility controls retained. The known normal-request negative-oblique versus italic discrepancy remains an unexecuted separate lead.

The proof audits allow only Lean's standard `propext`, `Classical.choice`, and `Quot.sound` axioms. No `sorry`, custom axioms, unsafe proof evaluation, or `native_decide` is accepted. Native source correspondence is a separately tested finite bridge, not a universal proof about C++, IEEE arithmetic, compilation, Rust parsing, or browser rendering.

## Native connection

The complete bodies of these 15 functions are compiled without semantic edits in original, B-only, A-only, and combined translation units:

- `StyleDistance`, `WidthDistance`, `WeightDistance`.
- `WeightStyleWidthDistance`, `WSSDistance`.
- `gfxFontFamily::FindAllFontsForStyle`, `FindFontForChar`, `SearchAllFontsForChar`.
- `fontlist::Family::FindAllFacesForStyleInternal`, `FindAllFacesForStyle`, `SearchAllFontsForChar`.
- `gfxPlatformFontList::GlobalFontFallback`, including both early exits.
- `gfxFontFamily::CheckForSimpleFamily`, `fontlist::Family::AddFaces`, `gfxFontEntry::SupportsBold`.

The manifest counts every extracted body and provider declaration: 37 items each for original/B, 34 each for A/combined. The difference is A's score class replacing four scalar constants. Every extracted body must be present verbatim in its generated translation unit and its entire originating source is retained and hashed. Types are enclosed in the adapter's namespace; A's otherwise global score class is resolved through the same imported namespace. Namespace/library adapters do not claim ABI equivalence.

The actual five-value `FontPresentation` enum, `PrefersColor`, and `gfxFontStyle::IsNormalStyle` inline are also extracted, with both default and explicit text/emoji controls. Actual generated fixed-point types/constants, the fixed-point helper macro, relevant C++ inlines, and the complete `FontPropertyRange` template/specializations are compiled. Exhaustive single-value tests execute all 46,081 angle encodings, all 64,001 valid width encodings, and all 63,937 valid weight encodings through `FromRaw`, `ToFloat`, `FromFloat`, and scalar range serialization/deserialization. Italic's raw tag is separately checked. The actual generated `StyleFontStyle::OBLIQUE` provider and `DEFAULT_OBLIQUE_DEGREES` remain 14 degrees; the mutation changes that real provider to 11 and observes its changed result. This is the approved separately pinned provider gate, not execution of the Rust CSS parser.

Native raw inputs are valid ordered 16-bit descriptors. Angles occupy signed 8.8 units; width/weight occupy unsigned 10.6 units. Exact conversions and returned style scores in 1/256 units are asserted at runtime. UBSan and assertions are enabled. The initial development run with the additional implicit-integer-truncation sanitizer rejected the intentional unsigned scalar-to-signed angle deserialization; it was not a native defect. Final runs use UBSan and exhaustive round-trip assertions. The fixed toolchain is recorded; its full SDK/standard libraries are not packaged hermetically.

## Provider boundary

`adapter.h` is an explicit environment, not an extracted font system. Raw input records provide inclusive descriptors, coverage, skipped status, font-creation success, color-glyph status, cmap presence, descriptor validity, mapped pointer/entry presence, bitmap size, family visibility/readiness, initialization success, and platform fallback policy. `CORPUS-v1.json` and `*-input.txt` retain every value; `*-stdout.txt` retains selected identities, exact style scores, counters, and ordered provider observations keyed to those raw values.

These are the native-bridge premises:

- Rust parsing, computed descriptor production, `FontFaceImpl::GetAttributesFromRule`, user-font entry creation, and variation-axis discovery deliver the recorded valid values. Their complete sources are pinned but their implementations are not executed here.
- Range getters return the recorded values. Names are stable ASCII face identities; tests include both name-order directions. No platform collation claim is made.
- Cmap/font-creation/color queries return the recorded results. Lazy failure paths execute the actual caller bodies. The adapter does not load a real font or perform shaping.
- Shared pointer mapping is stable during an invocation. Allocator/constructor and shared-memory concurrency are premises; actual `AddFaces` slot selection, range rejection, and publication control flow execute. The constructor initializes the recorded fields. No IPC, reference ownership, or race theorem is claimed.
- Locks, reference ownership, logging and profiling are inert adapter facilities. Actual `GlobalFontMatch` and A score storage are compiled; caller-owned style references remain live.
- Simple-family checks use actual code. Auto-weight flags are zero; variation-axis auto descriptors are outside these fixtures. User-font source inspection establishes that downloaded range families bypass ordinary simple-family treatment.
- Platform fallback, visibility, async readiness and cmap loading are controlled outcomes. The complete global fallback routine executes, including platform short circuit, visibility, async skip, both global zero exits, and final font creation.
- The GTK bitmap postfilter executes with `MOZ_WIDGET_GTK` on the host compiler. This checks the conditional code, not a GTK build or Linux font inventory.

Source-only replay includes these providers' retained source files and all generated declaration provenance. Actual outer consumers (`gfxFontGroup::FindFallbackFaceForChar`, family/face list consumers, and user-font creation) are source-audited through retained files/inventories; no claim is made that these outer callers were compiled. The five requested distance consumers and global exits were compiled in every version.

## Finite results

The final corpus has 9,322 records per version, plus 692 GTK records per version: 40,056 native invocations. It includes approved A/B case tables in both orders, boundary/range grids, deterministic random same-sign/italic/coordinate cases, and provider controls. There are 118,166 native score-order comparisons against the independent interval-visit oracle. The 1,136 normal-request or italic-oblique-only records have identical complete outputs/traces between original/B and A/combined.

All five consumers are exercised, including ties and identity order, duplicate identities, list clearing, shared strict improvement, reverse unshared name ties, unavailable faces/maps, mapped-null pointers, missing glyphs/entries, font failures, mismatch-only candidates, matching-versus-mismatched incumbents, Any/text/emoji, empty permitted fallback collections, singleton/general/simple families, bitmap tolerance/fallback and both global zero exits. Empty unshared `FindAllFontsForStyle` and empty general shared matching are excluded because their native assertions require a nonempty valid family; empty fallback collections are tested.

The Python compatibility oracle covers original arithmetic, preserved cross-kind policy, and caller-specific existing decisions. It is explicitly separate from the spec interval oracle. A/combined expected general selections use successive minimum filtering, not a translated lexicographic comparator. These finite comparisons do not constitute A's missing universal theorem.

One control intentionally differs for B alone: a mismatched exact-style first family versus a mismatched slightly worse later family can lose its small style difference through the old float accumulator near 1e12, allowing the later name to win. Original/A/combined select the first family in that fixture. This is the already known A narrowing defect, not a new threshold defect and not a new bug report. The expected table records it explicitly.

## Mutation gates

All ten mutations compile and run successfully, with literal reference/mutated winner expectations: restore 14; positive-only repair; negative-only repair; italic target left at 14; strict positive boundary; strict negative boundary; actual default provider changed to 11; removed positive containment; erased exact-italic advantage; overridden oblique-only zero reset. Each also has a rejected Lean theorem file and separate successfully executed Lean reference/mutant witness. Assertion/compile/proof rejection alone never counts as semantic mutation evidence. Reference and mutated scores, winners, raw inputs and provider traces are retained.

A score-policy mutations and an A universal theorem are not implemented in this B companion. The reusable complete caller harness makes that next step possible.

## Replay and closure

Use `check.py --manifest-sha256 <INPUTS-v1.json SHA-256> --out <new-directory>`. The checker authenticates all source inputs before importing the artifact's Python modules. `--source-only-replay` copies only that authenticated input closure into a fresh directory and executes from there; it does not copy historical receipts, generated binaries, or development outputs, and reads no live Gecko sources. Supply the manifest identity from `FREEZE-v1.json` or the parent handoff. The checker itself is the bootstrap trust boundary and its hash is separately frozen.

`INPUTS-v1.json` closes over proof/scripts/adapters, full original/candidate sources, copied design/case tables, primary spec evidence, toolchain identities and provider provenance. `receipts/source-only/SOURCE-ONLY-v1.json` records the clean replay. `FREEZE-v1.json` freezes the source manifest, checker, report and retained receipt tree separately. Development failures remain historical, outside the authenticated replay closure.

## Remaining gates

- Root-owned browser baseline/B-only/A-only/combined WPT runs are pending for the proposed tests.
- The actual existing `oblique-last-resort-weight-selection.html` outcome, including known bug 2033377, must be compared in the browser; this artifact retains the bug evidence and native last-resort controls but does not substitute them for that WPT run.
- A's complete universal ordered-filter/identity theorem, its required semantic mutations, and cost measurements are separate work.
- Cross-kind style policy, complete native refinement and CSS-to-Lean specification extraction remain outside this result.

Primary basis: CSS Fonts 4 [font-style matching](https://drafts.csswg.org/css-fonts-4/#font-style-matching), copied from the accepted design's current 2026-10-18 evidence. The retained HTML, text, original provenance and Searchfox inventories have content identities in the input manifest. All 21 retained original source files matched the live checkout in the final read-only check; no source overlap was edited.
