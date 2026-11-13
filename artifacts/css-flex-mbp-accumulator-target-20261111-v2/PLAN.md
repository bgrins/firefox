# Proof plan awaiting target review

The exact definitions and propositions are in `proof/FlexMBP/Model.lean` and `Target.lean`. A bounded cold typecheck has compiled them with the pinned Lean 4.35.0-rc4 toolchain; no target theorem has yet been proved.

1. Prove generic list-sum bounds by induction from the per-item bounds. Specialize to prefixes, derive their lengths, then derive signed-int64 safety from the UINT32_MAX bound. Include both extremal negative and positive contributions; do not use an absolute-value bound that silently excludes −2^31.
2. Prove the checked left fold returns the initial accumulator plus the mathematical sum when all resulting prefix totals lie in its range. Establish the converse exact-result fact on success independently of the wide bounds. Instantiate for wide success and old/wide compatibility.
3. Prove a symbolic replicate characterization, then specialize the three old-fold first-failure boundaries. This avoids reducing 35,792 repeated steps using a native evaluator. Add checked concrete witnesses for both endpoint contributions, mixed signs and distinct identities with equal contributions.
4. Prove the analogous sequential subtraction lemma and compose it with wide accumulation and the explicit `DownstreamFits` condition. Preserve the occupied-sum/add/sub order.
5. Compile meaningful deliberately wrong variants (e.g. skipping a contribution or using the narrow range), prove their concrete wrong results and refute the corresponding unchanged claim. Audit exact theorem names with only standard logical axioms; no `sorry`, native decision certificates, trusted evaluation or extra axioms.
6. Cold replay the complete owned closure with the inherited fail-closed process runner, one Lean worker, 4GiB/180s per command. Retain failed diagnostics and remove owned compiled scratch only after confirmed group absence. Authenticate target and predecessor inputs before and after execution.

The native candidate and browser/WPT runs remain root-owned. No theorem claim will be inferred from those observations.
