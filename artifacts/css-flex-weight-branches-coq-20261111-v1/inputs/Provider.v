Require Import Reals Psatz Classical Gappa.Gappa_library.
Require Import Target mul_positive mul_negative div_positive div_negative factor_adjustment.
Open Scope R_scope.

Lemma mul_positive_output (i s : R) :
  mul_positive.p1 i -> mul_positive.p2 s -> mul_positive.p10 i s /\ mul_positive.p11 i s.
Proof.
  intros Hi Hs.
  split; apply NNPP; intro Hbad; apply (mul_positive.l1 i s).
  - split; [split; assumption | left; right; exact Hbad].
  - split; [split; assumption | right; exact Hbad].
Qed.

Lemma mul_positive_numeric (i s : R) :
  0 <= i <= 1152921504606846976 -> 0 <= s <= 1 -> -1048576 <= mul_positive._delta i s <= i+1048576.
Proof.
  intros Hi Hs.
  pose proof (mul_positive_output i s) as H.
  cbv delta [mul_positive.p1 mul_positive.p2 mul_positive.p10 mul_positive.p11 mul_positive.r22 mul_positive.f1 mul_positive.f2 mul_positive.i1 mul_positive.f3 mul_positive.i2 mul_positive.f4 mul_positive.i3 mul_positive.f5 mul_positive.f6 mul_positive.i4 mul_positive.f7 mul_positive.f8 mul_positive.i5 mul_positive.i6 mul_positive.i7 mul_positive.f9 mul_positive.f10 mul_positive.i8 mul_positive.i9 mul_positive.i10 mul_positive.i11 mul_positive.f11 mul_positive.i12 mul_positive.f12 mul_positive.f13 mul_positive.i13 mul_positive.f14 mul_positive.f15 mul_positive.i14 mul_positive.f16 mul_positive.f17 mul_positive.i15 mul_positive.f18 mul_positive.f19 mul_positive.i16 mul_positive.f20 mul_positive.i17 mul_positive.f21 mul_positive.i18 mul_positive.f22 mul_positive.i19 mul_positive.i20 mul_positive.i21 mul_positive.i22 mul_positive.i23 mul_positive.f23 mul_positive.i24] in H.
  cbv [BND lower upper float2R Fnum Fexp Defs.F2R] in H.
  cbn [Defs.Fnum Defs.Fexp] in H.
  try replace (Raux.bpow radix2 0) with (1:R) in H by reflexivity.
  try replace (Raux.bpow radix2 20) with (1048576:R) in H by reflexivity.
  try replace (Raux.bpow radix2 27) with (134217728:R) in H by reflexivity.
  try replace (Raux.bpow radix2 59) with (576460752303423488:R) in H by reflexivity.
  try replace (Raux.bpow radix2 60) with (1152921504606846976:R) in H by reflexivity.
  try replace (Raux.bpow radix2 61) with (2305843009213693952:R) in H by reflexivity.
  cbv [IZR IPR IPR_2] in H.
  specialize (H ltac:(lra) ltac:(lra)).
  lra.
Qed.

Lemma mul_negative_output (i s : R) :
  mul_negative.p1 i -> mul_negative.p2 s -> mul_negative.p10 i s /\ mul_negative.p11 i s.
Proof.
  intros Hi Hs.
  split; apply NNPP; intro Hbad; apply (mul_negative.l1 i s).
  - split; [split; assumption | left; right; exact Hbad].
  - split; [split; assumption | right; exact Hbad].
Qed.

Lemma mul_negative_numeric (i s : R) :
  -1152921504606846976 <= i <= 0 -> 0 <= s <= 1 -> i-1048576 <= mul_negative._delta i s <= 1048576.
Proof.
  intros Hi Hs.
  pose proof (mul_negative_output i s) as H.
  cbv delta [mul_negative.p1 mul_negative.p2 mul_negative.p10 mul_negative.p11 mul_negative.r22 mul_negative.f1 mul_negative.f2 mul_negative.i1 mul_negative.f3 mul_negative.i2 mul_negative.f4 mul_negative.i3 mul_negative.f5 mul_negative.f6 mul_negative.i4 mul_negative.f7 mul_negative.f8 mul_negative.i5 mul_negative.i6 mul_negative.i7 mul_negative.f9 mul_negative.i8 mul_negative.i9 mul_negative.f10 mul_negative.f11 mul_negative.i10 mul_negative.f12 mul_negative.f13 mul_negative.i11 mul_negative.f14 mul_negative.f15 mul_negative.i12 mul_negative.f16 mul_negative.f17 mul_negative.i13 mul_negative.f18 mul_negative.i14 mul_negative.f19 mul_negative.i15 mul_negative.f20 mul_negative.i16 mul_negative.i17 mul_negative.i18 mul_negative.i19 mul_negative.i20 mul_negative.i21 mul_negative.f21 mul_negative.i22 mul_negative.i23 mul_negative.f22 mul_negative.i24] in H.
  cbv [BND lower upper float2R Fnum Fexp Defs.F2R] in H.
  cbn [Defs.Fnum Defs.Fexp] in H.
  try replace (Raux.bpow radix2 0) with (1:R) in H by reflexivity.
  try replace (Raux.bpow radix2 20) with (1048576:R) in H by reflexivity.
  try replace (Raux.bpow radix2 27) with (134217728:R) in H by reflexivity.
  try replace (Raux.bpow radix2 59) with (576460752303423488:R) in H by reflexivity.
  try replace (Raux.bpow radix2 60) with (1152921504606846976:R) in H by reflexivity.
  try replace (Raux.bpow radix2 61) with (2305843009213693952:R) in H by reflexivity.
  cbv [IZR IPR IPR_2] in H.
  specialize (H ltac:(lra) ltac:(lra)).
  lra.
Qed.

Lemma div_positive_output (i s : R) :
  div_positive.p1 i -> div_positive.p2 s -> div_positive.p10 i s /\ div_positive.p11 i s.
Proof.
  intros Hi Hs.
  split; apply NNPP; intro Hbad; apply (div_positive.l1 i s).
  - split; [split; assumption | left; right; exact Hbad].
  - split; [split; assumption | right; exact Hbad].
Qed.

Lemma div_positive_numeric (i s : R) :
  0 <= i <= 1152921504606846976 -> 1 <= s <= 134217728 -> -1048576 <= div_positive._delta i s <= i+1048576.
Proof.
  intros Hi Hs.
  pose proof (div_positive_output i s) as H.
  cbv delta [div_positive.p1 div_positive.p2 div_positive.p10 div_positive.p11 div_positive.r22 div_positive.f1 div_positive.f2 div_positive.i1 div_positive.f3 div_positive.f4 div_positive.i2 div_positive.f5 div_positive.i3 div_positive.f6 div_positive.f7 div_positive.i4 div_positive.f8 div_positive.f9 div_positive.i5 div_positive.i6 div_positive.i7 div_positive.f10 div_positive.f11 div_positive.i8 div_positive.i9 div_positive.i10 div_positive.i11 div_positive.f12 div_positive.i12 div_positive.f13 div_positive.f14 div_positive.i13 div_positive.f15 div_positive.f16 div_positive.i14 div_positive.f17 div_positive.f18 div_positive.i15 div_positive.f19 div_positive.f20 div_positive.i16 div_positive.f21 div_positive.i17 div_positive.f22 div_positive.i18 div_positive.f23 div_positive.i19 div_positive.f24 div_positive.i20 div_positive.f25 div_positive.i21 div_positive.f26 div_positive.i22 div_positive.f27 div_positive.i23 div_positive.i24 div_positive.i25] in H.
  cbv [BND lower upper float2R Fnum Fexp Defs.F2R] in H.
  cbn [Defs.Fnum Defs.Fexp] in H.
  try replace (Raux.bpow radix2 0) with (1:R) in H by reflexivity.
  try replace (Raux.bpow radix2 20) with (1048576:R) in H by reflexivity.
  try replace (Raux.bpow radix2 27) with (134217728:R) in H by reflexivity.
  try replace (Raux.bpow radix2 59) with (576460752303423488:R) in H by reflexivity.
  try replace (Raux.bpow radix2 60) with (1152921504606846976:R) in H by reflexivity.
  try replace (Raux.bpow radix2 61) with (2305843009213693952:R) in H by reflexivity.
  cbv [IZR IPR IPR_2] in H.
  specialize (H ltac:(lra) ltac:(lra)).
  lra.
Qed.

Lemma div_negative_output (i s : R) :
  div_negative.p1 i -> div_negative.p2 s -> div_negative.p10 i s /\ div_negative.p11 i s.
Proof.
  intros Hi Hs.
  split; apply NNPP; intro Hbad; apply (div_negative.l1 i s).
  - split; [split; assumption | left; right; exact Hbad].
  - split; [split; assumption | right; exact Hbad].
Qed.

Lemma div_negative_numeric (i s : R) :
  -1152921504606846976 <= i <= 0 -> 1 <= s <= 134217728 -> i-1048576 <= div_negative._delta i s <= 1048576.
Proof.
  intros Hi Hs.
  pose proof (div_negative_output i s) as H.
  cbv delta [div_negative.p1 div_negative.p2 div_negative.p10 div_negative.p11 div_negative.r22 div_negative.f1 div_negative.f2 div_negative.i1 div_negative.f3 div_negative.f4 div_negative.i2 div_negative.f5 div_negative.i3 div_negative.f6 div_negative.f7 div_negative.i4 div_negative.f8 div_negative.f9 div_negative.i5 div_negative.i6 div_negative.i7 div_negative.f10 div_negative.i8 div_negative.i9 div_negative.f11 div_negative.f12 div_negative.i10 div_negative.f13 div_negative.f14 div_negative.i11 div_negative.f15 div_negative.f16 div_negative.i12 div_negative.f17 div_negative.f18 div_negative.i13 div_negative.f19 div_negative.i14 div_negative.f20 div_negative.i15 div_negative.f21 div_negative.i16 div_negative.i17 div_negative.i18 div_negative.f22 div_negative.i19 div_negative.f23 div_negative.i20 div_negative.f24 div_negative.i21 div_negative.f25 div_negative.i22 div_negative.i23 div_negative.f26 div_negative.i24] in H.
  cbv [BND lower upper float2R Fnum Fexp Defs.F2R] in H.
  cbn [Defs.Fnum Defs.Fexp] in H.
  try replace (Raux.bpow radix2 0) with (1:R) in H by reflexivity.
  try replace (Raux.bpow radix2 20) with (1048576:R) in H by reflexivity.
  try replace (Raux.bpow radix2 27) with (134217728:R) in H by reflexivity.
  try replace (Raux.bpow radix2 59) with (576460752303423488:R) in H by reflexivity.
  try replace (Raux.bpow radix2 60) with (1152921504606846976:R) in H by reflexivity.
  try replace (Raux.bpow radix2 61) with (2305843009213693952:R) in H by reflexivity.
  cbv [IZR IPR IPR_2] in H.
  specialize (H ltac:(lra) ltac:(lra)).
  lra.
Qed.

Lemma factor_adjustment_output (i s : R) :
  factor_adjustment.p1 i -> factor_adjustment.p2 s -> factor_adjustment.p8 i s.
Proof.
  intros Hi Hs.
  apply NNPP; intro Hbad; apply (factor_adjustment.l1 i s).
  split; [split; assumption | right; exact Hbad].
Qed.

Lemma factor_adjustment_numeric (i s : R) :
  -576460752303423488 <= i <= 576460752303423488 -> 0 <= s <= 1 -> -576460752303423488 <= factor_adjustment._delta i s <= 576460752303423488.
Proof.
  intros Hi Hs.
  pose proof (factor_adjustment_output i s) as H.
  cbv delta [factor_adjustment.p1 factor_adjustment.p2 factor_adjustment.p8 factor_adjustment.f1 factor_adjustment.f2 factor_adjustment.i1 factor_adjustment.f3 factor_adjustment.f4 factor_adjustment.i2 factor_adjustment.f5 factor_adjustment.f6 factor_adjustment.i3 factor_adjustment.f7 factor_adjustment.f8 factor_adjustment.i4 factor_adjustment.f9 factor_adjustment.i5 factor_adjustment.f10 factor_adjustment.i6] in H.
  cbv [BND lower upper float2R Fnum Fexp Defs.F2R] in H.
  cbn [Defs.Fnum Defs.Fexp] in H.
  try replace (Raux.bpow radix2 0) with (1:R) in H by reflexivity.
  try replace (Raux.bpow radix2 20) with (1048576:R) in H by reflexivity.
  try replace (Raux.bpow radix2 27) with (134217728:R) in H by reflexivity.
  try replace (Raux.bpow radix2 59) with (576460752303423488:R) in H by reflexivity.
  try replace (Raux.bpow radix2 60) with (1152921504606846976:R) in H by reflexivity.
  try replace (Raux.bpow radix2 61) with (2305843009213693952:R) in H by reflexivity.
  cbv [IZR IPR IPR_2] in H.
  specialize (H ltac:(lra) ltac:(lra)).
  lra.
Qed.

Theorem mul_target : MulTarget.
Proof.
  intros free share Hfree Hshare.
  unfold DomainR in Hfree.
  unfold EnvelopeR.
  destruct (Rle_dec 0 free) as [Hpos | Hneg].
  - rewrite Rmin_right, Rmax_left by lra.
    pose proof (mul_positive_numeric free share ltac:(lra) Hshare) as H.
    change (-1048576 <= mulDelta free share <= free+1048576) in H.
    lra.
  - rewrite Rmin_left, Rmax_right by lra.
    pose proof (mul_negative_numeric free share ltac:(lra) Hshare) as H.
    change (free-1048576 <= mulDelta free share <= 1048576) in H.
    lra.
Qed.

Theorem div_target : DivTarget.
Proof.
  intros free count Hfree Hcount.
  unfold DomainR in Hfree.
  unfold EnvelopeR.
  destruct (Rle_dec 0 free) as [Hpos | Hneg].
  - rewrite Rmin_right, Rmax_left by lra.
    pose proof (div_positive_numeric free count ltac:(lra) Hcount) as H.
    change (-1048576 <= divDelta free count <= free+1048576) in H.
    lra.
  - rewrite Rmin_left, Rmax_right by lra.
    pose proof (div_negative_numeric free count ltac:(lra) Hcount) as H.
    change (free-1048576 <= divDelta free count <= 1048576) in H.
    lra.
Qed.

Theorem factor_target : FactorTarget.
Proof.
  intros free share Hfree Hshare.
  exact (factor_adjustment_numeric free share Hfree Hshare).
Qed.

Theorem provider_target : ProviderTarget.
Proof.
  intros free choice Hfree Hvalid.
  destruct choice as [ | | share | count].
  - unfold computeDelta, EnvelopeR.
    destruct (Rle_dec 0 free).
    + rewrite Rmin_right, Rmax_left by lra. lra.
    + rewrite Rmin_left, Rmax_right by lra. lra.
  - unfold computeDelta, EnvelopeR.
    destruct (Rle_dec 0 free).
    + rewrite Rmin_right, Rmax_left by lra. lra.
    + rewrite Rmin_left, Rmax_right by lra. lra.
  - apply mul_target; assumption.
  - apply div_target; assumption.
Qed.

Theorem integer_target : IntegerTarget.
Proof.
  intros free delta choice Hfree Hvalid Hcompute.
  assert (Hdomain : DomainR (IZR free)).
  { unfold DomainR. destruct Hfree as [Hlo Hhi].
    split; apply IZR_le; assumption. }
  pose proof (provider_target (IZR free) choice Hdomain Hvalid) as H.
  rewrite <- Hcompute in H.
  unfold EnvelopeR in H.
  destruct (Z_le_dec 0 free) as [Hpos | Hneg].
  - assert (Hsign : 0 <= IZR free) by (apply IZR_le; lia).
    rewrite Rmin_right, Rmax_left in H by lra.
    rewrite Z.min_r, Z.max_l by lia.
    split.
    + apply le_IZR. change (-1048576 <= IZR delta). lra.
    + apply le_IZR. rewrite plus_IZR.
      change (IZR delta <= IZR free+1048576). lra.
  - assert (Hsign : IZR free <= 0) by (apply IZR_le; lia).
    rewrite Rmin_left, Rmax_right in H by lra.
    rewrite Z.min_l, Z.max_r by lia.
    split.
    + apply le_IZR. rewrite minus_IZR.
      change (IZR free-1048576 <= IZR delta). lra.
    + apply le_IZR. change (IZR delta <= 1048576). lra.
Qed.

Theorem full_target : FullTarget.
Proof.
  exact (conj mul_target (conj div_target (conj factor_target
    (conj provider_target integer_target)))).
Qed.

Print Assumptions mul_target.
Print Assumptions div_target.
Print Assumptions factor_target.
Print Assumptions provider_target.
Print Assumptions integer_target.
Print Assumptions full_target.
