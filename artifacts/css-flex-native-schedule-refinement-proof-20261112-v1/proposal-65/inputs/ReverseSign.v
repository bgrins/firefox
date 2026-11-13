Require Import Reals ZArith List Psatz Gappa.Gappa_library.
Require Import WeightTarget ShareTarget Share Target ConversionTarget Conversion PrefixTarget PrefixControls ReverseTarget.
Open Scope R_scope.

Lemma half_value : Target.half = /2.
Proof. change (5 * /10 = /2). field. Qed.
Lemma round_half : Target.rn Target.half = Target.half.
Proof. rewrite half_value. exact PrefixControls.rn_half. Qed.
Lemma floor_nonnegative : forall v, 0 <= v ->
  (0 <= Raux.Zfloor (Target.rn (v + Target.half)))%Z.
Proof.
  intros v Hv.
  pose proof (Share.monotone_target Target.half (v + Target.half) ltac:(lra)) as Hround.
  change (Target.rn Target.half <= Target.rn (v + Target.half)) in Hround.
  rewrite round_half in Hround. pose proof half_value as Hhalf.
  pose proof (Raux.Zfloor_ub (Target.rn (v + Target.half))) as Hfloor.
  rewrite ?plus_IZR in Hfloor.
  destruct (Z_le_dec 0 (Raux.Zfloor (Target.rn (v + Target.half)))); [assumption|].
  assert (Hz : (Raux.Zfloor (Target.rn (v + Target.half)) <= -1)%Z) by lia.
  pose proof (IZR_le _ _ Hz) as Hr. cbn [IZR] in Hr. lra.
Qed.
Lemma floor_nonpositive : forall v, v <= 0 ->
  (Raux.Zfloor (Target.rn (v + Target.half)) <= 0)%Z.
Proof.
  intros v Hv.
  pose proof (Share.monotone_target (v + Target.half) Target.half ltac:(lra)) as Hround.
  change (Target.rn (v + Target.half) <= Target.rn Target.half) in Hround.
  rewrite round_half in Hround. pose proof half_value as Hhalf.
  pose proof (Raux.Zfloor_lb (Target.rn (v + Target.half))) as Hfloor.
  destruct (Z_le_dec (Raux.Zfloor (Target.rn (v + Target.half))) 0); [assumption|].
  assert (Hz : (1 <= Raux.Zfloor (Target.rn (v + Target.half)))%Z) by lia.
  pose proof (IZR_le _ _ Hz) as Hr. cbn [IZR] in Hr. lra.
Qed.
Theorem sign_target : SignTarget.
Proof.
  intros free share Hshare. unfold deltaAt, shareChoice.
  destruct (Req_EM_T share 1); [cbn [integerDelta]; auto|].
  destruct (Rlt_dec 0 share); [|cbn [integerDelta]; lia].
  cbn [integerDelta]. split; intro Hfree.
  - apply floor_nonnegative. apply Share.rn_nonnegative.
    apply Rmult_le_pos; [apply Share.rn_nonnegative; exact (IZR_le _ _ Hfree)|lra].
  - apply floor_nonpositive.
    assert (Hcast : Target.rn (IZR free) <= 0).
    { pose proof (Share.monotone_target (IZR free) 0 (IZR_le _ _ Hfree)) as H.
      rewrite Share.rn_zero in H. exact H. }
    pose proof (Share.monotone_target (Target.rn (IZR free) * share) 0 ltac:(nra)) as H.
    rewrite Share.rn_zero in H. exact H.
Qed.
Lemma delta_envelope : forall free share,
  FreeDomain free -> 0 <= share <= 1 ->
  EnvelopeZ free (deltaAt free share) /\ Fits64 (deltaAt free share).
Proof.
  intros free share Hfree Hshare. unfold deltaAt.
  apply Conversion.safety_target; [exact Hfree|].
  unfold shareChoice. destruct (Req_EM_T share 1); [exact I|].
  destruct (Rlt_dec 0 share); [exact Hshare|exact I].
Qed.
Theorem remainder_target : RemainderTarget.
Proof.
  intros free share Hfree Hshare.
  destruct (delta_envelope free share Hfree Hshare) as [Henv Hfit].
  destruct (sign_target free share Hshare) as [Hp Hn].
  pose proof (Z.le_min_l free (-1048576)) as Hml.
  pose proof (Z.le_min_r free (-1048576)) as Hmr.
  pose proof (Z.le_max_l free 1048576) as Hxl.
  pose proof (Z.le_max_r free 1048576) as Hxr.
  unfold EnvelopeZ in Henv. unfold FreeDomain, Fits64 in *.
  destruct (Z_le_dec 0 free).
  - specialize (Hp l). rewrite Z.min_r, Z.max_l in Henv by lia. repeat split; lia.
  - specialize (Hn ltac:(lia)). rewrite Z.min_l, Z.max_r in Henv by lia. repeat split; lia.
Qed.

Print Assumptions sign_target.
Print Assumptions remainder_target.
