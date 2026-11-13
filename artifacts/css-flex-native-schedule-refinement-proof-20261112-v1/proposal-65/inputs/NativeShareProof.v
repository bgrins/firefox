Require Import Reals ZArith Lia Psatz Gappa.Gappa_library Flocq.Core.Raux.
Require Import WeightTarget ShareTarget Share NativeFloatModel NativeOperations NativeBounds NativeBinaryFacts NativeValues.
Module NativeShareProof.
Open Scope R_scope.
Lemma divide_unit : forall weight sum,
  NativeFloat.finite weight = true -> NativeFloat.finite sum = true ->
  0 < NativeFloat.value weight <= NativeFloat.value sum ->
  NativeFloat.finite (NativeFloat.divide weight sum) = true /\
  NativeFloat.value (NativeFloat.divide weight sum) = rn (NativeFloat.value weight / NativeFloat.value sum) /\
  0 <= NativeFloat.value (NativeFloat.divide weight sum) <= 1.
Proof.
  intros weight sum W S Bounds.
  assert (Positive : 0 < NativeFloat.value sum) by lra.
  assert (Ratio : 0 < NativeFloat.value weight / NativeFloat.value sum <= 1).
  { split; [apply Rdiv_lt_0_compat; lra|].
    apply (Rmult_le_reg_r (NativeFloat.value sum)); [exact Positive|].
    unfold Rdiv. rewrite Rmult_assoc, Rinv_l by lra. lra. }
  assert (Safe : NativeOperations.NoOverflow (NativeFloat.value weight / NativeFloat.value sum)).
  { apply (NativeBounds.interval_safe 0); [lia|]. change (-1 <= NativeFloat.value weight / NativeFloat.value sum <= 1); lra. }
  destruct (NativeOperations.divide_correct weight sum W S ltac:(lra) Safe) as [Value Finite].
  split; [exact Finite|]. split; [exact Value|]. rewrite Value.
  pose proof (Share.monotone_target 0 (NativeFloat.value weight / NativeFloat.value sum) ltac:(lra)) as Lo.
  pose proof (Share.monotone_target _ 1 (proj2 Ratio)) as Hi.
  rewrite Share.rn_zero in Lo. rewrite Share.rn_one in Hi. lra.
Qed.
Lemma next_dominates : forall previous weight,
  0 <= previous -> 0 <= weight -> Representable weight -> weight <= rn (previous+weight).
Proof.
  intros previous weight P W Repr. pose proof (Share.monotone_target weight (previous+weight) ltac:(lra)) as H.
  unfold Representable in Repr. rewrite Repr in H. exact H.
Qed.
Print Assumptions divide_unit.
Print Assumptions next_dominates.
End NativeShareProof.
