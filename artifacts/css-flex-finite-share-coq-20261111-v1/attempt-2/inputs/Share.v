Require Import Reals ZArith List Psatz Gappa.Gappa_library.
Require Import WeightTarget Weights ShareTarget.
Open Scope R_scope.

Lemma format_valid : Generic_fmt.Valid_exp (FLT.FLT_exp (-1074) 53).
Proof. apply FLT.FLT_exp_valid. unfold FLX.Prec_gt_0. lia. Qed.

Lemma nearest_valid : Generic_fmt.Valid_rnd rndNE.
Proof. apply Generic_fmt.valid_rnd_N. Qed.

Theorem monotone_target : MonotoneTarget.
Proof.
  intros x y H. exact (@Generic_fmt.round_le radix2 (FLT.FLT_exp (-1074) 53)
    format_valid rndNE nearest_valid x y H).
Qed.

Theorem idempotent_target : IdempotentTarget.
Proof.
  intro x. unfold Representable, rn.
  apply (@Generic_fmt.round_generic radix2 (FLT.FLT_exp (-1074) 53) rndNE nearest_valid).
  exact (@Generic_fmt.generic_format_round radix2 (FLT.FLT_exp (-1074) 53)
    format_valid rndNE nearest_valid x).
Qed.

Lemma rn_zero : rn 0 = 0.
Proof. exact (@Generic_fmt.round_0 radix2 (FLT.FLT_exp (-1074) 53) rndNE nearest_valid). Qed.

Lemma rn_one : rn 1 = 1.
Proof.
  unfold rn. apply (@Generic_fmt.round_generic radix2 (FLT.FLT_exp (-1074) 53) rndNE nearest_valid).
  change (Generic_fmt.generic_format radix2 (FLT.FLT_exp (-1074) 53) (Raux.bpow radix2 0)).
  apply Generic_fmt.generic_format_bpow. vm_compute. discriminate.
Qed.

Lemma rn_nonnegative : forall x, 0 <= x -> 0 <= rn x.
Proof.
  intros x H. pose proof (monotone_target 0 x H) as Hround.
  rewrite rn_zero in Hround. exact Hround.
Qed.

Lemma fold_nondecreasing : forall weights initial,
  0 <= initial -> Representable initial -> Forall FiniteWeight weights ->
  initial <= accumulate weights initial.
Proof.
  induction weights as [ | w rest IH]; intros initial Hinitial Hrepr Hvalid.
  - cbn [accumulate fold_left]. lra.
  - inversion Hvalid as [ | head tail Hw Hrest]; subst.
    destruct Hw as [[Hw _] _].
    pose proof (monotone_target initial (initial+w) ltac:(lra)) as Hstep.
    unfold Representable in Hrepr. rewrite Hrepr in Hstep.
    pose proof (IH (rn (initial+w)) ltac:(lra) (idempotent_target _) Hrest) as Hlater.
    change (initial <= accumulate rest (rn (initial+w))). lra.
Qed.

Theorem sum_dominates_target : SumDominatesTarget.
Proof.
  induction weights as [ | w rest IH]; intros initial weight Hinitial Hvalid Hin.
  - inversion Hin.
  - inversion Hvalid as [ | head tail Hw Hrest]; subst.
    destruct Hw as [[Hwnonneg Hwbound] Hwrepr].
    assert (Hnext : 0 <= rn (initial+w)) by (apply rn_nonnegative; lra).
    change (weight <= accumulate rest (rn (initial+w))).
    destruct Hin as [Heq | Hin].
    + subst weight.
      pose proof (monotone_target w (initial+w) ltac:(lra)) as Hfirst.
      unfold Representable in Hwrepr. rewrite Hwrepr in Hfirst.
      pose proof (fold_nondecreasing rest (rn (initial+w)) Hnext
        (idempotent_target _) Hrest). lra.
    + exact (IH (rn (initial+w)) weight Hnext Hrest Hin).
Qed.

Theorem share_target : ShareTarget.
Proof.
  intros weights weight Hcount Hvalid Hin Hpositive.
  pose proof (sum_dominates_target weights 0 weight ltac:(lra) Hvalid Hin) as Hdom.
  assert (Hweights : Forall WeightValid weights).
  { eapply Forall_impl; [ | exact Hvalid]. intros x H. exact (proj1 H). }
  pose proof (ordered_target weights Hcount Hweights) as Hordered.
  pose proof (count_bound (Z.of_nat (length weights)) (accumulate weights 0)
    ltac:(lia) Hordered) as Hbound.
  assert (Hden : 0 < accumulate weights 0) by lra.
  assert (Hratio : 0 < weight / accumulate weights 0 <= 1).
  { split.
    - apply Rdiv_lt_0_compat; assumption.
    - apply (Rmult_le_reg_r (accumulate weights 0)); [exact Hden | ].
      unfold Rdiv. rewrite Rmult_assoc, Rinv_l by lra. lra. }
  assert (Hshare : 0 <= share weight (accumulate weights 0) <= 1).
  { unfold share.
    pose proof (monotone_target 0 (weight / accumulate weights 0) ltac:(lra)) as Hlo.
    pose proof (monotone_target (weight / accumulate weights 0) 1 ltac:(lra)) as Hhi.
    rewrite rn_zero in Hlo. rewrite rn_one in Hhi. lra. }
  split; [lra | ]. split; [exact Hratio | ]. split; [exact Hshare | ].
  apply idempotent_target.
Qed.

Theorem scaled_target : ScaledTarget.
Proof.
  intros factor base Hfactor Hbase. split.
  - exact (product_target factor base Hfactor Hbase).
  - apply idempotent_target.
Qed.

Theorem zero_target : ZeroTarget.
Proof. intros denominator H. unfold share, Rdiv. rewrite Rmult_0_l, rn_zero. reflexivity. Qed.

Theorem witness_target : WitnessTarget.
Proof.
  split.
  - split; [unfold WeightValid, weightLimit; lra | exact rn_one].
  - split.
    + cbn [accumulate fold_left]. rewrite Rplus_0_l. exact rn_one.
    + unfold share. replace (1/1) with (1:R) by field. exact rn_one.
Qed.

Theorem full_share_target : FullShareTarget.
Proof.
  exact (conj monotone_target (conj idempotent_target (conj sum_dominates_target
    (conj share_target (conj scaled_target (conj zero_target witness_target)))))).
Qed.

Print Assumptions monotone_target.
Print Assumptions idempotent_target.
Print Assumptions sum_dominates_target.
Print Assumptions share_target.
Print Assumptions scaled_target.
Print Assumptions zero_target.
Print Assumptions witness_target.
Print Assumptions full_share_target.
