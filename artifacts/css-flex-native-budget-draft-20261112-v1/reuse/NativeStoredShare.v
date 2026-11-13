Require Import Reals ZArith Lia Psatz.
Require Import WeightTarget ShareTarget Share PrefixTarget.
Require Import NativeFloatModel NativeBinaryFacts NativeValues NativeShareProof.
Module NativeStoredShare.
Open Scope R_scope.
Definition store (weight total : NativeFloat.F64) :=
  if NativeFloat.equal weight NativeFloat.zero then NativeFloat.zero else NativeFloat.divide weight total.
Lemma store_correspondence : forall weight previous total,
  NativeFloat.finite weight = true -> NativeFloat.finite total = true ->
  0 <= previous -> FiniteWeight (NativeFloat.value weight) ->
  NativeFloat.value total = rn (previous + NativeFloat.value weight) ->
  NativeFloat.finite (store weight total) = true /\
  NativeFloat.value (store weight total) = PrefixTarget.shareAt (NativeFloat.value weight) (NativeFloat.value total) /\
  0 <= NativeFloat.value (store weight total) <= 1.
Proof.
  intros weight previous total WF TF Previous [Weight Repr] Total.
  unfold WeightValid in Weight.
  pose proof (NativeBinaryFacts.equal_correct weight NativeFloat.zero WF NativeValues.zero_finite) as Eq.
  rewrite NativeValues.zero_value in Eq.
  unfold store. destruct (NativeFloat.equal weight NativeFloat.zero) eqn:Zero.
  - assert (Value : NativeFloat.value weight = 0) by (apply Eq; assumption || reflexivity).
    split; [exact NativeValues.zero_finite|]. rewrite NativeValues.zero_value, Value.
    unfold PrefixTarget.shareAt. destruct (Req_EM_T 0 0); [split; [reflexivity|lra]|contradiction].
  - assert (Nonzero : NativeFloat.value weight <> 0).
    { intro Equal. apply Eq in Equal. congruence. }
    assert (Dominates : NativeFloat.value weight <= NativeFloat.value total).
    { rewrite Total. apply NativeShareProof.next_dominates; [exact Previous|exact (proj1 Weight)|exact Repr]. }
    destruct (NativeShareProof.divide_unit weight total WF TF ltac:(lra)) as [Finite [Value Range]].
    split; [exact Finite|]. split; [|exact Range].
    unfold PrefixTarget.shareAt. destruct (Req_EM_T (NativeFloat.value weight) 0); [contradiction|exact Value].
Qed.
Print Assumptions store_correspondence.
End NativeStoredShare.
