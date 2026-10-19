# Container content-size cache proof companion

This package supports the one-expression repair in `nsPresContext::UpdateContainerQueryStylesAndAnchorPosLayout`: capture `frame->GetContentRectRelativeToSelf().Size()` in `QueryContainerState`, instead of `frame->GetSize()`. The comparison algorithm remains unchanged.

It proves a conditional cache-observable theorem over arbitrary integer sizes and tests exact extracted native routines with explicit adapters. It does not prove layout, container selection, invalidation scheduling, convergence, or all observables of container queries.

## Replay

From the repository root, use a fresh output directory:

```sh
python3 artifacts/css-query-content-box-proof-v1/check.py \
  --out artifacts/css-query-content-box-proof-v1/root-replay-v1 \
  > artifacts/css-query-content-box-proof-v1/root-replay-v1.log 2>&1
```

Independent reviewers can choose their own artifact output directory. `RECEIPT-v1.json` is written only after all gates pass. Require both a PASS receipt and process exit zero. This compiles isolated Lean, C++ and Rust artifacts, and does not build or run Firefox. C++ checks use undefined-behavior sanitization, with recovery disabled. Unexpected compiler/Lean output is rejected.

Native identities:

- Original nsPresContext.cpp: `286d3ba60931235d84b7bde33c764f0f8e9b7ce531d5ce85f50fd4a46792e591`.
- Candidate nsPresContext.cpp: `4d2305277a3b7ca61cffc717cc678f41d80ac458a88bbcb6bdc79067e338b9b6`.

`SOURCE-v1.json` authenticates source inputs and live native files. Drift is an intentional replay failure. `TOOLCHAIN-v1.json` records compiler versions and executable hashes. Compiler runtime libraries, Lean Std, system headers and the host OS remain trusted inputs rather than exhaustively pinned dependencies. `tooling-paths-v1.txt` lists companion source files; development output, executables, mutants and logs are generated replay products.

## Contract and model

In `ContentSize.lean`, `sameKey` independently specifies the existing native comparison for a **fixed container type**:

- Size containment compares the physical size pair.
- Inline-size containment compares the logical inline dimension.
- A type without size/inline-size bits tracks neither dimension.

Native full-type inequality always returns changed. The model categorizes a fixed type by the native precedence of SIZE over INLINE_SIZE; it does not equate distinct flag sets. Writing-mode direction/text orientation are abstracted to the physical inline-axis orientation used by these routines.

`observable` takes current content dimensions, stable physical availability booleans and the type-eligible axis mask. It preserves absence and performs the Rust wrapper's negative-coordinate-to-None normalization. The theorem covers all integer dimensions, so arithmetic over border/padding, overflow, floating-point conversion and rounding are deliberately absent. The native bridge checks representable signed 32-bit extrema separately. Production sizes are supplied by the current frame getter; correctness of that getter and reflow freshness are premises.

Eleven kernel-audited theorems establish:

- Equal content cache keys imply equal eligible optional physical dimensions for fixed type, orientation and availability.
- A changed eligible observable requires a changed key under those premises.
- Every deterministic consumer of the same optional-size pair has the same result. Other inputs to such a consumer must be fixed; this is not a theorem that dimensions alone determine arbitrary CSS queries.
- Raw unmasked size projection is preserved only if every available axis is type-eligible.
- Old border-key counterexamples for size and inline-size containers.
- Explicit counterexamples showing why writing orientation, availability and eligible-axis restrictions cannot be dropped.

The proofs use only `propext`; concrete counterexamples depend on no axioms. There are no additional axioms, `sorry`, unchecked solvers or native-decide shortcuts. Six semantic mutations test the comparison/axis obligations. Diagnostic controls reject missing audits, unexpected output, stderr, admitted proofs, added axioms and syntax errors.

## Why the theorem must be restricted

`Gecko_GetQueryContainerSize` exposes the content dimensions allowed by `GetContainSizeAxes()`. These axes are not identical to the container-type mask. An inline-size container can have extra block containment through `contain:size` or skipped content. Its raw Gecko result can therefore include a block dimension that `QueryContainerState::Changed` does not track.

Actual consumers narrow that result: `container_type_axes` filters `ContainerCondition::valid_container_info`, while `ContainerSizeQuery::evaluate_potential_size_container` explicitly returns only the inline physical dimension for an INLINE_SIZE type. Both mask algorithms are extracted and exercised in a separate Rust bridge. Proving equality of the complete raw Gecko pair for arbitrary fixed containment axes would still be false. The model contains a counterexample with inline width 100 and block size changing 50→60: the eligible pair is stable, but the raw pair changes.

Writing-mode changes also require separate treatment. A horizontal 100×50 inline-size container and a vertical 50×100 container have equal inline cache dimensions but expose different physical eligible axes. Under SIZE, an unchanged physical 100×50 pair can yield a changed logical inline dimension when orientation changes. Neither is a newly established browser defect: style reconstruction, other invalidation paths and consumer recomputation may handle those changes. This package does not investigate or modify those paths.

Availability is similarly independent: frame absence, `display:contents`, applicability of containment and content-visibility can change optional results without changing a stored size pair. The theorem assumes these conditions fixed, or equivalently assumes their effective physical availability mask fixed. It does not assert that size equality proves availability equality.

## Exact native binding

The C++ bridge copies, without reimplementing their bodies:

- The complete `QueryContainerState` declaration, including `GetInlineSize` and `Changed`.
- `Gecko_GetQueryContainerSize`.
- The original and candidate `newState` initializer statements, each placed in a small standalone constructor wrapper.

`bridge.preservation` requires exact full-file equality after replacing only the initializer. Its intended change check permits formatting whitespace within that initializer and requires precisely the border-to-content getter substitution. It rejects mutations to the comparator, writing-mode capture, wrong getter and the once-per-flush update guard. No claim is made that preserving the rest of the file proves its behavior correct.

The C++ adapters supply signed 32-bit `nscoord`, physical sizes, logical inline selection, container-type bits, frame presence, containment axes and separately supplied border/content sizes. Frame getter implementations are adapters, not compiled Gecko geometry. The extracted projection writes into -1 sentinels; a declared bridge wrapper applies the inspected Rust `display:contents` and negative-to-None behavior. `GetUsedBorderAndPadding`, skip sides, rectangle deflation and reflow are not part of the proved algorithm.

The separate Rust bridge copies exact `container_type_axes`, `FeatureFlags::all_container_axes`, and the final type-dependent result branch of `evaluate_potential_size_container`. It uses small bitflag, writing-mode and result adapters; it does not execute ancestor traversal, style lookup or feature parsing. The archived actual flag declarations establish adapter constants. The bridge checks all eight flag combinations, both orientations and 25 optional-size pairs, including adapter-only SIZE|INLINE_SIZE combinations that the parser rejects. Treat those combinations as robustness controls, not valid CSS claims.

Finite C++ checks cover 17,384 old/new state pairs: all type-bit combinations, orientations, containment axes, frame/display availability, eight boundary/asymmetric size pairs and 1,000 deterministic arbitrary transitions. Native output is compared against an independent Python oracle, and the actual native outputs are also checked for the conditional cache-observable implication. The old border-key comparison must produce counterexamples. Six compiled C++ mutations and three compiled Rust-mask mutations must fail comparisons. These finite checks bind source and detect semantic mistakes; they are not a proof of the C++/Rust machine code over all inputs.

## Integration premises

1. Before/after states refer to the relevant current primary frame, with content geometry supplied consistently to both the cache capture and query projection.
2. Reflow/layout freshness is sufficient at both observations. The update routine flushes in specified branches, but this package does not verify flush completion or callback/frame lifetime.
3. Container type, writing orientation, selected container, effective availability and non-size consumer inputs are fixed. Feature eligibility reflects the queried axes; deferred query reparsing is outside the theorem.
4. The native primitive adapters correctly represent size equality, writing-mode axis projection, bitflags and optional coordinate normalization.
5. A changed comparison is consumed by the existing restyle/invalidation mechanism as intended. Ancestor suppression, once-per-element-per-flush suppression, registration, frame reconstruction, scrollbars and convergence are not proved.
6. For logical units or thresholds, the additional context (writing mode, zoom, fonts, registration, custom properties, viewport fallback and other ancestors) is held fixed. Missing-axis merging and ancestor selection are separate contracts.

The retained `nsStyleDisplay::GetContainSizeAxes` and Rust wrapper sources document why availability must be supplied, not inferred from type alone. The retained getter shows content geometry uses border/padding with skipped sides; this package intentionally does not replace it with a simplistic border-minus-padding arithmetic model.

## Evidence ownership

The root owns the native/WPT repair and browser evidence. Root reported baseline session 25143 exited 1 with 72 border-box failures, 72 content-box controls passing, and 92 existing subtests passing. This companion does not rerun or independently authenticate those browser receipts and claims no post-fix browser outcome. The mathematical old-key witnesses explain the shape of the established failure; formal proof did not discover the original browser bug.

The primary specification basis is CSS Conditional 5's content-box size features and container units, retained by the earlier independent conditions review. `SPEC-SOURCES-v1.json` and `css-conditional-5.html` are copied unchanged from that review with provenance. Current source analysis and the explicit model boundaries, rather than a claim of whole-spec translation, connect that requirement to this narrow cache repair.
