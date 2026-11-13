Require Import Reals ZArith Psatz Classical Gappa.Gappa_library.
Require Import Target Provider ConversionTarget Witness.
Open Scope R_scope.

Theorem floor_target : FloorTarget.
Proof.
  intro x.
  unfold integerRound, Generic_fmt.round, Generic_fmt.scaled_mantissa,
    Generic_fmt.cexp, FIX.FIX_exp, Defs.F2R.
  cbn [Defs.Fnum Defs.Fexp].
  change (IZR (Raux.Zfloor (rn (x+half))) =
    IZR (Raux.Zfloor (rn (x+half)*1))*1).
  rewrite !Rmult_1_r. reflexivity.
Qed.

Theorem correspondence_target : CorrespondenceTarget.
Proof.
  intros free choice.
  destruct choice as [ | | share | count].
  - reflexivity.
  - reflexivity.
  - exact (floor_target (rn (rn (IZR free)*share))).
  - exact (floor_target (rn (rn (IZR free)/count))).
Qed.

Theorem safety_target : SafetyTarget.
Proof.
  intros free choice Hfree Hvalid.
  pose proof (integer_target free (integerDelta free choice) choice Hfree
    Hvalid (correspondence_target free choice)) as H.
  split; [exact H | unfold Fits64].
  destruct (Z_le_dec 0 free).
  - rewrite Z.min_r, Z.max_l in H by lia. lia.
  - rewrite Z.min_l, Z.max_r in H by lia. lia.
Qed.

Theorem factor_integer_target : FactorIntegerTarget.
Proof.
  intros free share Hfree Hshare.
  assert (Hreal : -576460752303423488 <= IZR free <= 576460752303423488).
  { split; apply IZR_le; lia. }
  pose proof (factor_target (IZR free) share Hreal Hshare) as H.
  change (-576460752303423488 <= computeDelta (IZR free) (Fraction share) <=
    576460752303423488) in H.
  rewrite <- correspondence_target in H.
  split; apply le_IZR.
  - exact (proj1 H).
  - exact (proj2 H).
Qed.

Theorem overshoot_target : OvershootTarget.
Proof.
  apply eq_IZR.
  rewrite correspondence_target.
  change (Witness._delta = 576460752303423488).
  assert (H : Witness.p1).
  { apply NNPP. intro Hbad. apply Witness.l1. left. exact Hbad. }
  cbv [Witness.p1 Witness.i1 Witness.f1 BND lower upper
    float2R Fnum Fexp Defs.F2R] in H.
  cbn [Defs.Fnum Defs.Fexp] in H.
  replace (Raux.bpow radix2 59) with (576460752303423488:R) in H by reflexivity.
  cbv [IZR IPR IPR_2] in H.
  lra.
Qed.

Theorem inhabited_target : InhabitedTarget.
Proof.
  unfold InhabitedTarget, ValidChoice. repeat split; lra.
Qed.

Theorem full_conversion_target : FullConversionTarget.
Proof.
  exact (conj floor_target (conj correspondence_target (conj safety_target
    (conj factor_integer_target (conj overshoot_target inhabited_target))))).
Qed.

Print Assumptions floor_target.
Print Assumptions correspondence_target.
Print Assumptions safety_target.
Print Assumptions factor_integer_target.
Print Assumptions overshoot_target.
Print Assumptions inhabited_target.
Print Assumptions full_conversion_target.
