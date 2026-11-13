# Projection proposal 65: source-only review

No Coq command or Docker operation was run. The original ProjectionTarget remains byte-identical. This proposal is not a proved clause and does not change the accepted checkpoint64 scope. Execution requires a fresh explicit root lane release.

## Endpoint and assumptions

NativeProjectionOriginal.projection_target has exactly NativeRefinementTarget.ProjectionTarget as its statement. It introduces only the original admitted entry, executable ModelHistory and successful modeled step hypotheses. All pointwise bounds/freshness/count premises used by helpers are obtained from those hypotheses. The endpoint does not assume scalar SignHistory.History, final-sum representability, full traversal or the desired result.

## Reviewed dependency chain

NativeIndexed provides ordered lookup and identity-independent list equality. NativeReversePositions proves event ordinals originate in the actual traversed input. NativeReverseEffects uses distinct input ordinals to reconstruct each updated row from its own event delta; a remaining-count-zero suffix is unchanged because already-acquired active main sizes fit signed32. Frozen records are preserved with their arbitrary metadata.

NativePreparedFields derives seed, frozen, main and flag correspondence from the actual reset and producer loops. The producer changes only share; admitted history provides active input bounds. NativeClampMap derives the full clamp map from actual active count, using the existing count/frozen-preservation lemmas. It does not assume that the clamp loop visited every active item.

NativeExecutionSums proves equations over the actual reverse correction accumulator and forward clamp accumulator in their execution order. NativeProjectionStage follows both distributing and non-distributing branches of NativePass.step. NativeProjectionPoint then uses the accepted reverse event correspondence and exact indexed lookup to identify every clamped main and active min/max flag. NativeProjectionTotals combines the two accumulator equations, the row correspondence and the existing scalar sum identities. NativeProjectionOriginal assembles both original conclusions.

## Mechanical checks and successor change

All local Require imports were resolved and their selected topological order checked. The exact imported input signatures, helper argument counts, tuple/list types, reverse/forward argument order and branch-specific frozen/active equations were inspected. Explicit induction names and nth_error membership arguments avoid the earlier inferred-binder failure patterns. A row_sum_map lemma supplies the non-definitional fold/map equation rather than asserting conversion. No malformed conjunction tokens, ambiguous explicit change RHS holes, admitted proofs or new axioms are present in this source batch.

The saved 19-file projection-draft-65 remains immutable. Its sole proof-script successor change keeps the projected row opaque while rewriting NativeClampMap.each into the actual clamp-one result, so the main/flag lemmas can match that expression. The change is retained in projection-review-65/CORRECTION.patch. No helper statement or original target changed. Existing NativeProjectionAlgebra and NativeProjectionFlags bytes are reused exactly.

These checks do not guarantee elaboration. Remaining uncertainty is ordinary Coq rewriting/conversion and induction elaboration in the new scripts; any failed bounded run must be retained and corrected separately without target changes. The original full 20-clause aggregate remains open.

## Exact proposed execution

From the proof root:

    python3 -I -B launch.py 65 --cache development-1/output/base-cache --select NativeProjectionOriginal

The unchanged original runner selects 126 modules: 53 authenticated base-cache imports, 73 fresh coqc commands, then full selected coqchk. The source-derived exact audit roster has 313 roots. The pinned offline image, one CPU, 1 GiB, 120 seconds per command, read-only root filesystem and retained terminal/absence checks are unchanged. No development-cache prototype adoption, automatic retry or target amendment is authorized.

The pure Python prepare_retry65.py authenticates all 106 transported definitions, unchanged 108 checkpoint64 selected inputs, the active cache, runner pins, dependency ordering and exact roster. Its PASS is preparation evidence only. All actual compiler/kernel/audit results are pending.

Native getters, ideal CSS geometry, actual binary/ABI/memory execution and cross-prover joins remain separate open obligations. Native tree, tests, Git and accepted repair commits were not touched.
