Require Import Reals ZArith List Bool Lia Psatz.
Require Import Flocq.IEEE754.BinarySingleNaN Flocq.Core.Raux.
Require Import Gappa.Gappa_library InputTarget InputProof WeightTarget ShareTarget Share.
Require Import NativeFloatModel.
Module NativeBinaryFacts.
Open Scope R_scope.
Lemma equal_correct : forall x y,
  NativeFloat.finite x = true -> NativeFloat.finite y = true ->
  (NativeFloat.equal x y = true <-> NativeFloat.value x = NativeFloat.value y).
Proof.
  intros x y Fx Fy. unfold NativeFloat.equal.
  rewrite BinarySingleNaN.Bcompare_correct by assumption.
  change ((match Rcompare (NativeFloat.value x) (NativeFloat.value y) with Eq => true | _ => false end) = true <-> NativeFloat.value x = NativeFloat.value y).
  case Rcompare_spec; intro H; simpl; split; intro E; try discriminate; try reflexivity; lra.
Qed.
Lemma less_correct : forall x y,
  NativeFloat.finite x = true -> NativeFloat.finite y = true ->
  (NativeFloat.less x y = true <-> NativeFloat.value x < NativeFloat.value y).
Proof.
  intros x y Fx Fy. unfold NativeFloat.less.
  rewrite BinarySingleNaN.Bcompare_correct by assumption.
  change ((match Rcompare (NativeFloat.value x) (NativeFloat.value y) with Lt => true | _ => false end) = true <-> NativeFloat.value x < NativeFloat.value y).
  case Rcompare_spec; intro H; simpl; split; intro E; try discriminate; try reflexivity; lra.
Qed.
Lemma floor_scaled : forall m e,
  Zfloor (IZR m*bpow radix2 e) =
    (if Z.leb 0 e then m*Z.pow 2 e else Z.div m (Z.pow 2 (-e)))%Z.
Proof.
  intros m e. destruct (Z.leb 0 e) eqn:E.
  - apply Z.leb_le in E. rewrite <- IZR_Zpower by exact E.
    rewrite <- mult_IZR,Zfloor_IZR. reflexivity.
  - apply Z.leb_gt in E.
    assert (P : bpow radix2 e = / IZR (Z.pow 2 (-e))).
    { replace e with (-(-e))%Z at 1 by lia. rewrite bpow_opp.
      rewrite <- IZR_Zpower by lia. reflexivity. }
    rewrite P. apply Zfloor_div. pose proof (Z.pow_pos_nonneg 2 (-e) ltac:(lia) ltac:(lia)). lia.
Qed.
Lemma floor_correct : forall x z,
  NativeFloat.floorFinite x = Some z ->
  NativeFloat.finite x = true /\ z = Zfloor (NativeFloat.value x).
Proof.
  intros x z. destruct x as [sign|sign| |sign mant exponent valid]; simpl [NativeFloat.floorFinite]; intro H; try discriminate.
  - inversion H; subst. split; [reflexivity|]. symmetry. apply Zfloor_IZR.
  - inversion H; subst. split; [reflexivity|].
    unfold NativeFloat.value, BinarySingleNaN.B2R, Defs.F2R. simpl.
    rewrite floor_scaled. destruct sign; reflexivity.
Qed.
Print Assumptions equal_correct.
Print Assumptions less_correct.
Print Assumptions floor_scaled.
Print Assumptions floor_correct.
End NativeBinaryFacts.
