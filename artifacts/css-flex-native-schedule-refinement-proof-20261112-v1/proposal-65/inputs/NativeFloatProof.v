Require Import Reals ZArith Bool.
Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeGenerationModel NativeEntryModel NativeCaseData NativeRefinementSpec.
Require Import NativeBinaryFacts NativePromotion NativeValues NativeScale.
Require Import ReverseTarget PrefixTarget ConversionTarget.
Module NativeFloatProof.
Open Scope R_scope.
Theorem fraction_correct : forall free share,
  FreeDomain free -> NativeFloat.finite share = true ->
  0 <= NativeFloat.value share <= 1 ->
  NativeFloat.fractionDelta free share = Some (deltaAt free (NativeFloat.value share)).
Proof.
  intros free share HF FS HS.
  unfold NativeFloat.fractionDelta, deltaAt, shareChoice.
  destruct (NativeFloat.equal share NativeFloat.one) eqn:E.
  - pose proof (proj1 (NativeBinaryFacts.equal_correct share NativeFloat.one FS NativeValues.one_finite) E) as V.
    rewrite NativeValues.one_value in V.
    destruct (Req_EM_T (NativeFloat.value share) 1); [reflexivity|contradiction].
  - destruct (Req_EM_T (NativeFloat.value share) 1) as [V|V].
    + assert (T : NativeFloat.equal share NativeFloat.one = true).
      { apply (proj2 (NativeBinaryFacts.equal_correct share NativeFloat.one FS NativeValues.one_finite)).
        rewrite NativeValues.one_value. exact V. } congruence.
    + destruct (NativeFloat.less NativeFloat.zero share) eqn:L.
      * pose proof (proj1 (NativeBinaryFacts.less_correct NativeFloat.zero share NativeValues.zero_finite FS) L) as P.
        rewrite NativeValues.zero_value in P.
        destruct (Rlt_dec 0 (NativeFloat.value share)); [apply NativeScale.scale_correct; assumption|contradiction].
      * destruct (Rlt_dec 0 (NativeFloat.value share)) as [P|P]; [|reflexivity].
        assert (T : NativeFloat.less NativeFloat.zero share = true).
        { apply (proj2 (NativeBinaryFacts.less_correct NativeFloat.zero share NativeValues.zero_finite FS)).
          rewrite NativeValues.zero_value. exact P. } congruence.
Qed.
Theorem float_target : NativeRefinementTarget.FloatTarget.
Proof.
  exact (conj NativePromotion.promotion_correct
    (conj NativeBinaryFacts.floor_correct fraction_correct)).
Qed.
Print Assumptions fraction_correct.
Print Assumptions float_target.
End NativeFloatProof.
