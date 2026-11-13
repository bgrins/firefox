Require Import Reals ZArith Bool Lia Psatz Gappa.Gappa_library.
Require Import Flocq.IEEE754.BinarySingleNaN Flocq.Core.Raux.
Require Import NativeFloatModel WeightTarget.
Module NativeOperations.
Open Scope R_scope.
Definition NoOverflow (x : R) := Rabs (WeightTarget.rn x) < bpow radix2 1024.
Lemma normalize_correct : forall m e sign,
  NoOverflow (IZR m * bpow radix2 e) ->
  NativeFloat.value (NativeFloat.normalize m e sign) = WeightTarget.rn (IZR m*bpow radix2 e) /\
  NativeFloat.finite (NativeFloat.normalize m e sign) = true.
Proof.
  intros m e sign H.
  pose proof (@BinarySingleNaN.binary_normalize_correct 53 1024
    ltac:(constructor; lia) ltac:(constructor; lia) BinarySingleNaN.mode_NE m e sign) as C.
  cbn zeta in C.
  rewrite Rlt_bool_true in C by exact H. destruct C as [V [F S]]. split; assumption.
Qed.
Lemma add_correct : forall x y,
  NativeFloat.finite x = true -> NativeFloat.finite y = true -> 
  NoOverflow (NativeFloat.value x + NativeFloat.value y) ->
  NativeFloat.value (NativeFloat.add x y) = WeightTarget.rn (NativeFloat.value x + NativeFloat.value y) /\
  NativeFloat.finite (NativeFloat.add x y) = true.
Proof.
  intros x y Fx Fy H.
  pose proof (@BinarySingleNaN.Bplus_correct 53 1024
    ltac:(constructor; lia) ltac:(constructor; lia) BinarySingleNaN.mode_NE x y Fx Fy) as C.
  cbn zeta in C.
  rewrite Rlt_bool_true in C by exact H.  destruct C as [V [F S]]. split; assumption.
Qed.
Lemma multiply_correct : forall x y,
  NativeFloat.finite x = true -> NativeFloat.finite y = true -> 
  NoOverflow (NativeFloat.value x * NativeFloat.value y) ->
  NativeFloat.value (NativeFloat.multiply x y) = WeightTarget.rn (NativeFloat.value x * NativeFloat.value y) /\
  NativeFloat.finite (NativeFloat.multiply x y) = true.
Proof.
  intros x y Fx Fy H.
  pose proof (@BinarySingleNaN.Bmult_correct 53 1024
    ltac:(constructor; lia) ltac:(constructor; lia) BinarySingleNaN.mode_NE x y ) as C.
  cbn zeta in C.
  rewrite Rlt_bool_true in C by exact H. unfold NativeFloat.finite in Fx,Fy. rewrite Fx,Fy in C. destruct C as [V [F S]]. split; assumption.
Qed.
Lemma divide_correct : forall x y,
  NativeFloat.finite x = true -> NativeFloat.finite y = true -> NativeFloat.value y <> 0 ->
  NoOverflow (NativeFloat.value x / NativeFloat.value y) ->
  NativeFloat.value (NativeFloat.divide x y) = WeightTarget.rn (NativeFloat.value x / NativeFloat.value y) /\
  NativeFloat.finite (NativeFloat.divide x y) = true.
Proof.
  intros x y Fx Fy Ny H.
  pose proof (@BinarySingleNaN.Bdiv_correct 53 1024
    ltac:(constructor; lia) ltac:(constructor; lia) BinarySingleNaN.mode_NE x y Ny) as C.
  cbn zeta in C.
  rewrite Rlt_bool_true in C by exact H. unfold NativeFloat.finite in Fx. rewrite Fx in C. destruct C as [V [F S]]. split; assumption.
Qed.
Print Assumptions normalize_correct.
Print Assumptions add_correct.
Print Assumptions multiply_correct.
Print Assumptions divide_correct.
End NativeOperations.
