Require Import Reals Bool.
Require Import NativeFloatModel NativeBinaryFacts NativeValues.
Module NativeCompareDecisions.
Open Scope R_scope.
Lemma zero_test : forall x,
  NativeFloat.finite x = true ->
  NativeFloat.equal x NativeFloat.zero = if Req_EM_T (NativeFloat.value x) 0 then true else false.
Proof.
  intros x Finite.
  pose proof (NativeBinaryFacts.equal_correct x NativeFloat.zero Finite NativeValues.zero_finite) as Equal.
  rewrite NativeValues.zero_value in Equal.
  destruct (Req_EM_T (NativeFloat.value x) 0) as [Zero|Nonzero].
  - apply Equal; exact Zero.
  - destruct (NativeFloat.equal x NativeFloat.zero) eqn:Test; [|reflexivity].
    exfalso. apply Nonzero. apply Equal. reflexivity.
Qed.
Lemma one_test : forall x,
  NativeFloat.finite x = true ->
  NativeFloat.less x NativeFloat.one = if Rlt_dec (NativeFloat.value x) 1 then true else false.
Proof.
  intros x Finite.
  pose proof (NativeBinaryFacts.less_correct x NativeFloat.one Finite NativeValues.one_finite) as Less.
  rewrite NativeValues.one_value in Less.
  destruct (Rlt_dec (NativeFloat.value x) 1) as [Below|Above].
  - apply Less; exact Below.
  - destruct (NativeFloat.less x NativeFloat.one) eqn:Test; [|reflexivity].
    exfalso. apply Above. apply Less. reflexivity.
Qed.
Print Assumptions zero_test.
Print Assumptions one_test.
End NativeCompareDecisions.
