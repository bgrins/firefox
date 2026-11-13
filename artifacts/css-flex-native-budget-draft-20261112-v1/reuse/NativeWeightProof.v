Require Import Reals ZArith List Bool Lia Psatz.
Require Import Flocq.Core.Raux Gappa.Gappa_library.
Require Import InputTarget InputProof WeightTarget ShareTarget Share.
Require Import NativeFloatModel NativeState NativeOperations NativePromotion NativeValues.
Module NativeWeightProof.
Import NativeSchedule.
Open Scope R_scope.
Definition payload (grow : bool) (r : Row) : WeightInput :=
  {| InputTarget.factor := NativeSchedule.factor grow (seed r);
     InputTarget.base := baseSize (seed r); InputTarget.growing := grow |}.
Lemma weight_correspondence : forall grow r,
  InputTarget.InputValid (payload grow r) ->
  NativeFloat.finite (weight grow r) = true /\
  NativeFloat.value (weight grow r) = InputTarget.inputWeight (payload grow r).
Proof.
  intros grow r H. destruct H as [F [B S]].
  cbn [payload InputTarget.factor InputTarget.base InputTarget.growing] in F,B,S.
  destruct (NativePromotion.promotion_correct _ F) as [PF PV].
  pose proof (proj2 (InputProof.promotion_target _ F)) as PR.
  unfold ShareTarget.Representable in PR.
  assert (D : ReverseTarget.FreeDomain (baseSize (seed r))) by
    (unfold ReverseTarget.FreeDomain; lia).
  destruct (NativeValues.integer_correct _ D) as [IV IF].
  destruct grow.
  - split; [exact PF|].
    change (NativeFloat.value (NativeFloat.promote (NativeSchedule.factor true (seed r))) =
      WeightTarget.rn (value32 (NativeSchedule.factor true (seed r)))).
    rewrite PR. exact PV.
  - assert (V : InputTarget.InputValid (payload false r)) by (split; [exact F|]; split; [exact B|exact S]).
    pose proof (proj1 (InputProof.input_weight_target _ V)) as W.
    unfold WeightTarget.WeightValid in W.
    unfold weight. destruct (Z.eqb (baseSize (seed r)) 0) eqn:Z.
    + apply Z.eqb_eq in Z. split; [exact NativeValues.zero_finite|].
      rewrite NativeValues.zero_value.
      cbv beta iota zeta delta [InputTarget.inputWeight payload InputTarget.factor InputTarget.base InputTarget.growing].
      rewrite Z. cbn [IZR]. rewrite Share.rn_zero, Rmult_0_r, Share.rn_zero. reflexivity.
    + assert (N : NativeOperations.NoOverflow
        (NativeFloat.value (NativeFloat.promote (NativeSchedule.factor false (seed r))) *
         NativeFloat.value (NativeFloat.integer (baseSize (seed r))))).
      { unfold NativeOperations.NoOverflow. rewrite PV, IV.
        rewrite <- PR at 1.
        change (Rabs (InputTarget.inputWeight (payload false r)) < bpow radix2 1024).
        rewrite Rabs_pos_eq by exact (proj1 W).
        assert (L : WeightTarget.weightLimit < bpow radix2 1024).
        { change (bpow radix2 159 < bpow radix2 1024). apply bpow_lt. lia. }
        lra. }
      destruct (NativeOperations.multiply_correct _ _ PF IF N) as [M MF].
      split; [exact MF|]. rewrite M, PV, IV.
      cbv beta iota zeta delta [InputTarget.inputWeight payload InputTarget.factor InputTarget.base InputTarget.growing].
      rewrite PR. reflexivity.
Qed.
Print Assumptions weight_correspondence.
End NativeWeightProof.
