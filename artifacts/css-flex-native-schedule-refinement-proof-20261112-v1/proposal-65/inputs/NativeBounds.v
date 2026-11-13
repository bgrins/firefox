Require Import Reals ZArith Lia Psatz Gappa.Gappa_library.
Require Import Flocq.Core.Raux Flocq.Core.Round_NE.
Require Import WeightTarget ShareTarget Share NativeOperations.
Module NativeBounds.
Open Scope R_scope.
Lemma power_exact : forall e, (-1074 <= e)%Z ->
  WeightTarget.rn (bpow radix2 e) = bpow radix2 e.
Proof.
  intros e H. unfold WeightTarget.rn.
  apply (@Generic_fmt.round_generic radix2 (FLT.FLT_exp (-1074) 53) rndNE Share.nearest_valid).
  apply Generic_fmt.generic_format_bpow. unfold FLT.FLT_exp. apply Z.max_lub; lia.
Qed.
Lemma round_opp : forall x, WeightTarget.rn (-x) = -WeightTarget.rn x.
Proof. intro x. apply Round_NE.round_NE_opp. Qed.
Lemma rounded_interval : forall e x,
  (-1074 <= e)%Z -> -bpow radix2 e <= x <= bpow radix2 e ->
  -bpow radix2 e <= WeightTarget.rn x <= bpow radix2 e.
Proof.
  intros e x E [L U]. pose proof (Share.monotone_target _ _ L) as L'.
  pose proof (Share.monotone_target _ _ U) as U'.
  rewrite round_opp, (power_exact e E) in L'. rewrite (power_exact e E) in U'. tauto.
Qed.
Lemma interval_safe : forall e x,
  (-1074 <= e < 1024)%Z -> -bpow radix2 e <= x <= bpow radix2 e ->
  NativeOperations.NoOverflow x.
Proof.
  intros e x [E B] H. unfold NativeOperations.NoOverflow.
  pose proof (rounded_interval e x E H) as R.
  pose proof (bpow_lt radix2 e 1024 B) as P.
  destruct (Rcase_abs (WeightTarget.rn x)) as [N|N];
    [rewrite Rabs_left by exact N|rewrite Rabs_right by exact N]; lra.
Qed.
Lemma interval_product : forall bound x share,
  0 <= bound -> -bound <= x <= bound -> 0 <= share <= 1 ->
  -bound <= x*share <= bound.
Proof.
  intros bound x share B X S.
  assert (L : 0 <= (x+bound)*share) by (apply Rmult_le_pos; lra).
  assert (U : 0 <= (bound-x)*share) by (apply Rmult_le_pos; lra).
  pose proof (Rmult_le_compat_l bound share 1 B (proj2 S)). nra.
Qed.
Print Assumptions power_exact.
Print Assumptions round_opp.
Print Assumptions rounded_interval.
Print Assumptions interval_safe.
Print Assumptions interval_product.
End NativeBounds.
