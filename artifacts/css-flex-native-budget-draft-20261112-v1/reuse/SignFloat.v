Require Import Reals ZArith Psatz Gappa.Gappa_library Flocq.Core.Ulp Flocq.Core.FLT.
Require Import WeightTarget ShareTarget Share PrefixControls.
Open Scope R_scope.
Definition SignFormat := Generic_fmt.generic_format radix2 (FLT.FLT_exp (-1074) 53).
Definition SignPred := Ulp.pred radix2 (FLT.FLT_exp (-1074) 53).
Definition SignUlp := Ulp.ulp radix2 (FLT.FLT_exp (-1074) 53).
Definition SignUnit := Raux.bpow radix2 (-53).
Lemma sign_format_round : forall x, SignFormat (WeightTarget.rn x).
Proof.
  intro x. exact (@Generic_fmt.generic_format_round radix2 (FLT.FLT_exp (-1074) 53)
    Share.format_valid rndNE Share.nearest_valid x).
Qed.
Lemma sign_format_repr : forall x, Representable x -> SignFormat x.
Proof.
  intros x H. unfold Representable in H. rewrite <- H. apply sign_format_round.
Qed.
Lemma sign_round_format : forall x, SignFormat x -> WeightTarget.rn x = x.
Proof.
  intros x H. exact (@Generic_fmt.round_generic radix2 (FLT.FLT_exp (-1074) 53)
    rndNE Share.nearest_valid x H).
Qed.
Lemma sign_format_pred : forall x, SignFormat x -> SignFormat (SignPred x).
Proof.
  intros x H. exact (@Ulp.generic_format_pred radix2 (FLT.FLT_exp (-1074) 53) Share.format_valid x H).
Qed.
Lemma sign_pred_one : SignPred 1 = 1 - SignUnit.
Proof.
  change (SignPred (Raux.bpow radix2 0) = 1 - SignUnit).
  unfold SignPred. rewrite Ulp.pred_bpow. reflexivity.
Qed.
Lemma sign_share_predecessor : forall s,
  Representable s -> s < 1 -> s <= 1 - SignUnit.
Proof.
  intros s Hs Hlt. rewrite <- sign_pred_one.
  apply (@Ulp.pred_ge_gt radix2 (FLT.FLT_exp (-1074) 53) Share.format_valid s 1).
  - apply sign_format_repr. exact Hs.
  - apply sign_format_repr. exact Share.rn_one.
  - exact Hlt.
Qed.
Lemma sign_pred_half : forall x,
  SignFormat x -> 1 <= x -> /2 <= SignPred x.
Proof.
  intros x Hx Hlo.
  apply (@Ulp.pred_ge_gt radix2 (FLT.FLT_exp (-1074) 53) Share.format_valid (/2) x).
  - apply sign_format_repr. exact PrefixControls.rn_half.
  - exact Hx.
  - lra.
Qed.
Lemma sign_unit_positive : 0 < SignUnit.
Proof. apply Raux.bpow_gt_0. Qed.
Lemma sign_twice_unit : Raux.bpow radix2 (-52) = 2 * SignUnit.
Proof.
  replace (-52)%Z with ((-53)+1)%Z by lia. rewrite Raux.bpow_plus.
  change (SignUnit * 2 = 2 * SignUnit). ring.
Qed.
Lemma sign_predecessor_gap : forall x,
  SignFormat x -> 1 <= x -> x - SignPred x < 2 * x * SignUnit.
Proof.
  intros x Hx Hlo. pose proof (sign_pred_half x Hx Hlo) as Hp.
  pose proof (@Ulp.pred_lt_id radix2 (FLT.FLT_exp (-1074) 53) x ltac:(lra)) as Hlt.
  pose proof (@Ulp.pred_plus_ulp radix2 (FLT.FLT_exp (-1074) 53) Share.format_valid x ltac:(lra) Hx) as Hgap.
  assert (Hsmall : Raux.bpow radix2 (-1074+53-1) <= Rabs (SignPred x)).
  { eapply Rle_trans with (/2).
    - change (Raux.bpow radix2 (-1022) <= Raux.bpow radix2 (-1)). apply Raux.bpow_le. lia.
    - rewrite Rabs_right by lra. exact Hp. }
  pose proof (@FLT.ulp_FLT_le radix2 (-1074) 53 (SignPred x) Hsmall) as Hu.
  rewrite Rabs_right in Hu by lra. change (SignUlp (SignPred x) <= SignPred x * Raux.bpow radix2 (-52)) in Hu.
  rewrite sign_twice_unit in Hu.
  change (SignPred x + SignUlp (SignPred x) = x) in Hgap.
  change (SignPred x < x) in Hlt. pose proof sign_unit_positive. nra.
Qed.
Lemma sign_product_below_pred : forall x s,
  SignFormat x -> 1 <= x -> Representable s -> s < 1 ->
  WeightTarget.rn (x*s) <= SignPred x.
Proof.
  intros x s Hx Hlo Hs Hlt.
  pose proof (sign_share_predecessor s Hs Hlt) as Hsbound.
  pose proof (sign_predecessor_gap x Hx Hlo) as Hgap.
  apply (@Ulp.round_N_le_midp radix2 (FLT.FLT_exp (-1074) 53) Share.format_valid
    (fun z => negb (Z.even z)) (SignPred x) (x*s)).
  - apply sign_format_pred. exact Hx.
  - unfold SignPred at 2. rewrite (@Ulp.succ_pred radix2 (FLT.FLT_exp (-1074) 53) Share.format_valid x Hx).
    nra.
Qed.
Lemma sign_pred_round_strict : forall x,
  1 <= x -> SignPred (WeightTarget.rn x) < x.
Proof.
  intros x Hx.
  pose proof (@Ulp.pred_round_le_id radix2 (FLT.FLT_exp (-1074) 53)
    Share.format_valid rndNE Share.nearest_valid x) as Hle.
  change (SignPred (WeightTarget.rn x) <= x) in Hle.
  destruct (Rlt_or_le (SignPred (WeightTarget.rn x)) x); [assumption|].
  assert (Heq : SignPred (WeightTarget.rn x) = x) by lra.
  assert (Hfmt : SignFormat x).
  { rewrite <- Heq. apply sign_format_pred. apply sign_format_round. }
  rewrite (sign_round_format x Hfmt) in Heq.
  pose proof (@Ulp.pred_lt_id radix2 (FLT.FLT_exp (-1074) 53) x ltac:(lra)) as Hlt.
  change (SignPred x < x) in Hlt. lra.
Qed.
Lemma sign_positive_product : forall z s,
  (1 <= z)%Z -> Representable s -> s < 1 ->
  WeightTarget.rn (WeightTarget.rn (IZR z)*s) < IZR z.
Proof.
  intros z s Hz Hs Hlt. assert (Hreal : 1 <= IZR z) by (apply IZR_le; exact Hz).
  pose proof (Share.monotone_target 1 (IZR z) Hreal) as Hcast. rewrite Share.rn_one in Hcast.
  pose proof (sign_product_below_pred (WeightTarget.rn (IZR z)) s (sign_format_round _) Hcast Hs Hlt).
  pose proof (sign_pred_round_strict (IZR z) Hreal). lra.
Qed.
Lemma sign_nearest_half_upper : forall x,
  SignFormat x -> WeightTarget.rn (x+/2) <= x+1.
Proof.
  intros x Hx.
  destruct (@Generic_fmt.round_N_pt radix2 (FLT.FLT_exp (-1074) 53)
    Share.format_valid (fun z => negb (Z.even z)) (x+/2)) as [_ Hnearest].
  specialize (Hnearest x Hx).
  change (Rabs (WeightTarget.rn (x+/2) - (x+/2)) <= Rabs (x-(x+/2))) in Hnearest.
  replace (x-(x+/2)) with (-(/2)) in Hnearest by ring.
  rewrite Rabs_Ropp in Hnearest. rewrite (Rabs_right (/2)) in Hnearest by lra.
  pose proof (Rle_abs (WeightTarget.rn (x+/2) - (x+/2))). lra.
Qed.
Print Assumptions sign_share_predecessor.
Print Assumptions sign_predecessor_gap.
Print Assumptions sign_product_below_pred.
Print Assumptions sign_pred_round_strict.
Print Assumptions sign_positive_product.
Print Assumptions sign_nearest_half_upper.
