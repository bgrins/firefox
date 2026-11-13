Require Import Reals ZArith Lia Psatz.
Require Import InputTarget InputProof WeightTarget NativeFloatModel NativeState NativePromotion NativeWeightProof.
Module NativeFactorProof.
Import NativeSchedule.
Open Scope R_scope.
Lemma factor_weight_bound : forall grow r,
  InputTarget.InputValid (NativeWeightProof.payload grow r) ->
  NativeFloat.finite (NativeFloat.promote (factor grow (seed r))) = true /\
  NativeFloat.value (NativeFloat.promote (factor grow (seed r))) = value32 (factor grow (seed r)) /\
  WeightValid (NativeFloat.value (NativeFloat.promote (factor grow (seed r)))).
Proof.
  intros grow r [F Rest].
  change (FactorInput (factor grow (seed r))) in F.
  destruct (NativePromotion.promotion_correct _ F) as [Finite Value].
  pose proof (proj1 (InputProof.promotion_target _ F)) as Bound.
  split; [exact Finite|]. split; [exact Value|]. rewrite Value.
  unfold FactorValid in Bound. unfold WeightValid, factorLimit, weightLimit in *; lra.
Qed.
Print Assumptions factor_weight_bound.
End NativeFactorProof.
