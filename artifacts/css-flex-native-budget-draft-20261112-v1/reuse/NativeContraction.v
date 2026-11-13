Require Import Reals ZArith Lia.
Require Import ReverseTarget SignTarget SignContraction.
Require Import NativeFloatModel NativeFloatProof NativeRepresentation.
Module NativeContraction.
Open Scope Z_scope.
Lemma delta_contraction : forall free share d,
  ReverseTarget.FreeDomain free -> NativeFloat.finite share = true ->
  (0 <= NativeFloat.value share <= 1)%R -> NativeFloat.fractionDelta free share = Some d ->
  NativeHistorySignTarget.BetweenZero free d /\
  NativeHistorySignTarget.BetweenZero free (free-d) /\
  Z.abs d + Z.abs (free-d) = Z.abs free.
Proof.
  intros free share d Domain Finite Range Delta.
  rewrite NativeFloatProof.fraction_correct in Delta by assumption.
  inversion Delta; subst d.
  destruct (SignContraction.sign_contraction_target free (NativeFloat.value share)
    Domain (NativeRepresentation.value_representable share) Range) as [Step Remainder].
  split; [exact Step|]. split; [exact Remainder|].
  unfold NativeHistorySignTarget.BetweenZero in *.
  destruct (Z_le_dec 0 free) as [Positive|Negative].
  - rewrite Z.min_r,Z.max_l in Step,Remainder by lia. rewrite !Z.abs_eq by lia. lia.
  - rewrite Z.min_l,Z.max_r in Step,Remainder by lia. rewrite !Z.abs_neq by lia. lia.
Qed.
Print Assumptions delta_contraction.
End NativeContraction.
