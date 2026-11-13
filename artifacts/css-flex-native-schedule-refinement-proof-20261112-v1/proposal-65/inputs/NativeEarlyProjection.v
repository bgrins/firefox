Require Import Reals ZArith List Bool Lia.
Require Import InputTarget SignModel.
Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeGenerationModel NativeEntryModel NativeCaseData NativeRefinementSpec NativeJointSpec NativeBinaryFacts NativePromotion NativeValues NativeEarlyProof.
Import ListNotations.
Module NativeEarlyProjection.
Import NativeSchedule.
Lemma promoted_zero : forall f, FactorInput f ->
  NativeFloat.equal (NativeFloat.promote f) NativeFloat.zero =
    if Req_EM_T (value32 f) 0 then true else false.
Proof.
  intros f H. destruct (NativePromotion.promotion_correct f H) as [F V].
  pose proof (NativeBinaryFacts.equal_correct (NativeFloat.promote f) NativeFloat.zero F NativeValues.zero_finite) as E.
  rewrite V, NativeValues.zero_value in E.
  destruct (Req_EM_T (value32 f) 0) as [Z|N].
  - apply E. exact Z.
  - destruct (NativeFloat.equal (NativeFloat.promote f) NativeFloat.zero) eqn:B; [|reflexivity].
    exfalso. apply N. apply E. reflexivity.
Qed.
Lemma constructed_projection : forall grow s,
  projectedRow grow (construct s) = SignHistory.build (projectedSeed grow s).
Proof. reflexivity. Qed.
Lemma projected_hypothetical : forall grow s,
  SignHistory.hypothetical (projectedSeed grow s) = clamp s (baseSize s).
Proof. reflexivity. Qed.
Lemma early_projection : forall grow s,
  SignHistory.SeedValid (projectedSeed grow s) ->
  projectedRow grow (earlyOne grow (construct s)) =
    SignHistory.early grow (SignHistory.build (projectedSeed grow s)).
Proof.
  intros grow s H. destruct H as [_ [_ A]].
  cbn [projectedSeed SignHistory.seedFrozen SignHistory.seedFactor SignHistory.seedBase] in A.
  unfold earlyOne, SignHistory.early.
  cbn [construct frozen seed main projectedRow projectedSeed SignHistory.build
    SignHistory.isFrozen SignHistory.seedFrozen SignHistory.seed SignHistory.main
    SignHistory.seedFactor SignHistory.seedBase SignHistory.seedMin SignHistory.seedMax
    SignHistory.hypothetical SignHistory.clamp SignHistory.share SignHistory.seedShare].
  destruct (initiallyFrozen s) eqn:F; [reflexivity|].
  specialize (A eq_refl). destruct A as [A _]. rewrite promoted_zero by exact A.
  cbn [SignHistory.seed SignHistory.seedFactor].
  rewrite !projected_hypothetical.
  destruct (if Req_EM_T (value32 (factor grow s)) 0 then true else false);
    destruct grow; cbn; destruct (Z.ltb (clamp s (baseSize s)) (baseSize s));
    destruct (Z.ltb (baseSize s) (clamp s (baseSize s)));
    cbv beta iota zeta delta [projectedRow construct setFlags freeze seed main frozen share]; rewrite ?F; reflexivity.
Qed.
Lemma projected_mode : forall line seeds grow,
  SignHistory.mode line (map (projectedSeed grow) seeds) = NativeEntry.seedsMode line seeds.
Proof.
  intros line seeds grow. unfold SignHistory.mode, NativeEntry.seedsMode.
  rewrite map_map. reflexivity.
Qed.
Print Assumptions promoted_zero.
Print Assumptions constructed_projection.
Print Assumptions projected_hypothetical.
Print Assumptions early_projection.
Print Assumptions projected_mode.
End NativeEarlyProjection.
