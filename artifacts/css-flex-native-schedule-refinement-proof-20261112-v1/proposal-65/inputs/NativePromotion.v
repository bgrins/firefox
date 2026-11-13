Require Import Reals ZArith Lia Psatz Gappa.Gappa_library.
Require Import Flocq.IEEE754.Binary Flocq.Core.Raux.
Require Import InputTarget InputProof ShareTarget WeightTarget NativeFloatModel NativeOperations.
Module NativePromotion.
Open Scope R_scope.
Theorem promotion_correct : forall factor,
  FactorInput factor -> NativeFloat.finite (NativeFloat.promote factor) = true /\
    NativeFloat.value (NativeFloat.promote factor) = value32 factor.
Proof.
  intros factor H.
  destruct (InputProof.promotion_target factor H) as [_ Hrepr].
  unfold Representable in Hrepr.
  assert (Hsafe : NativeOperations.NoOverflow (value32 factor)).
  { unfold NativeOperations.NoOverflow. rewrite Hrepr.
    eapply Rlt_trans; [apply Binary.abs_B2R_lt_emax |].
    apply bpow_lt. lia. }
  destruct H as [Hfinite Hnonnegative].
  destruct factor as [sign|sign|sign payload valid|sign mant exponent valid];
    simpl in Hfinite; try discriminate.
  - split; reflexivity.
  - unfold NativeFloat.promote.
    pose proof (NativeOperations.normalize_correct
      (if sign then -Z.pos mant else Z.pos mant)%Z exponent sign Hsafe) as [V F].
    split; [exact F|]. rewrite V. exact Hrepr.
Qed.
Print Assumptions promotion_correct.
End NativePromotion.
