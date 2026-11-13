Require Import Reals ZArith Psatz Gappa.Gappa_library Flocq.Core.Ulp.
Require Import WeightTarget ShareTarget Share Target ConversionTarget PrefixTarget ReverseTarget ReverseSign.
Require Import SignTarget SignFloat.
Open Scope R_scope.
Lemma sign_fraction_upper : forall z s,
  (1 <= z)%Z -> Representable s -> s < 1 ->
  (integerDelta z (Fraction s) <= z)%Z.
Proof.
  intros z s Hz Hs Hlt.
  pose proof (sign_positive_product z s Hz Hs Hlt) as Hp.
  pose proof (sign_nearest_half_upper (WeightTarget.rn (WeightTarget.rn (IZR z)*s)) (sign_format_round _)) as Hround.
  change (Raux.Zfloor (WeightTarget.rn (WeightTarget.rn (WeightTarget.rn (IZR z)*s)+Target.half)) <= z)%Z.
  rewrite ReverseSign.half_value.
  set (v := WeightTarget.rn (WeightTarget.rn (WeightTarget.rn (IZR z)*s)+/2)) in *.
  pose proof (Raux.Zfloor_lb v).
  destruct (Z_le_dec (Raux.Zfloor v) z); [assumption|].
  assert (Hbad : (z+1 <= Raux.Zfloor v)%Z) by lia.
  apply IZR_le in Hbad. rewrite plus_IZR in Hbad. cbn [IZR] in Hbad. lra.
Qed.
Lemma sign_round_opp : forall x, WeightTarget.rn (-x) = -WeightTarget.rn x.
Proof. intro x. apply Round_NE.round_NE_opp. Qed.
Lemma sign_product_opp : forall z s,
  WeightTarget.rn (WeightTarget.rn (IZR (-z))*s) =
    -WeightTarget.rn (WeightTarget.rn (IZR z)*s).
Proof.
  intros. rewrite opp_IZR, sign_round_opp.
  replace ((-WeightTarget.rn (IZR z))*s) with (-(WeightTarget.rn (IZR z)*s)) by ring.
  rewrite sign_round_opp. reflexivity.
Qed.
Lemma sign_fraction_lower : forall z s,
  (z <= -1)%Z -> Representable s -> s < 1 ->
  (z <= integerDelta z (Fraction s))%Z.
Proof.
  intros z s Hz Hs Hlt.
  pose proof (sign_positive_product (-z)%Z s ltac:(lia) Hs Hlt) as Hp.
  pose proof (sign_product_opp (-z)%Z s) as Heq.
  rewrite Z.opp_involutive in Heq. rewrite opp_IZR in Heq, Hp.
  assert (Hproduct : IZR z < WeightTarget.rn (WeightTarget.rn (IZR z)*s)) by lra.
  pose proof (Share.monotone_target (WeightTarget.rn (WeightTarget.rn (IZR z)*s))
    (WeightTarget.rn (WeightTarget.rn (IZR z)*s)+/2) ltac:(lra)) as Hround.
  rewrite (sign_round_format _ (sign_format_round _)) in Hround.
  change (z <= Raux.Zfloor (WeightTarget.rn (WeightTarget.rn (WeightTarget.rn (IZR z)*s)+Target.half)))%Z.
  rewrite ReverseSign.half_value.
  set (v := WeightTarget.rn (WeightTarget.rn (WeightTarget.rn (IZR z)*s)+/2)) in *.
  pose proof (Raux.Zfloor_ub v).
  destruct (Z_le_dec z (Raux.Zfloor v)); [assumption|].
  assert (Hbad : (Raux.Zfloor v+1 <= z)%Z) by lia.
  apply IZR_le in Hbad. rewrite plus_IZR in Hbad. cbn [IZR] in Hbad.
  lra.
Qed.
Theorem sign_contraction_target : NativeHistorySignTarget.ContractionTarget.
Proof.
  intros current stored Hfree Hrepr Hrange.
  pose proof (ReverseSign.sign_target current stored Hrange) as [Hpositive Hnegative].
  assert (Hbound : NativeHistorySignTarget.BetweenZero current (deltaAt current stored)).
  { unfold deltaAt, shareChoice.
    destruct (Req_EM_T stored 1); [cbn [integerDelta]; unfold NativeHistorySignTarget.BetweenZero;
      split; [apply Z.le_min_l|apply Z.le_max_l]|].
    destruct (Rlt_dec 0 stored); [|cbn [integerDelta]; unfold NativeHistorySignTarget.BetweenZero;
      split; [apply Z.le_min_r|apply Z.le_max_r]].
    assert (Hs : stored < 1) by lra.
    assert (Hdelta : deltaAt current stored = integerDelta current (Fraction stored)).
    { unfold deltaAt, shareChoice. destruct (Req_EM_T stored 1); [contradiction|].
      destruct (Rlt_dec 0 stored); [reflexivity|contradiction]. }
    rewrite Hdelta in Hpositive, Hnegative.
    unfold NativeHistorySignTarget.BetweenZero.
    destruct (Z_le_dec 1 current) as [Hp|Hp].
    - rewrite Z.min_r, Z.max_l by lia. split; [apply Hpositive; lia|].
      apply sign_fraction_upper; assumption.
    - destruct (Z_le_dec current (-1)) as [Hn|Hn].
      + rewrite Z.min_l, Z.max_r by lia. split; [apply sign_fraction_lower; assumption|apply Hnegative; lia].
      + assert (current=0)%Z by lia. subst current. specialize (Hpositive ltac:(lia)).
        specialize (Hnegative ltac:(lia)). cbn [Z.min Z.max]. lia. }
  split; [exact Hbound|]. unfold NativeHistorySignTarget.BetweenZero in *.
  destruct (Z_le_dec 0 current); rewrite ?Z.min_r, ?Z.max_l in * by lia;
    rewrite ?Z.min_l, ?Z.max_r in * by lia; lia.
Qed.
Print Assumptions sign_fraction_upper.
Print Assumptions sign_fraction_lower.
Print Assumptions sign_contraction_target.
