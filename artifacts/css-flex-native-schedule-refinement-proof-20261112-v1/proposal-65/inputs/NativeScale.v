Require Import Reals ZArith Lia Psatz Gappa.Gappa_library.
Require Import Flocq.Core.Raux.
Require Import WeightTarget Target ConversionTarget ReverseTarget.
Require Import NativeFloatModel NativeOperations NativeBounds NativeValues.
Module NativeScale.
Open Scope R_scope.
Lemma scale_correct : forall free share,
  FreeDomain free -> NativeFloat.finite share = true ->
  0 <= NativeFloat.value share <= 1 ->
  NativeFloat.scale free share = Some (integerDelta free (Fraction (NativeFloat.value share))).
Proof.
  intros free share HF FS HS.
  destruct (NativeValues.integer_correct free HF) as [IV IF].
  pose proof (NativeValues.free_interval free HF) as FI.
  assert (IB : -bpow radix2 60 <= NativeFloat.value (NativeFloat.integer free) <= bpow radix2 60).
  { rewrite IV. apply NativeBounds.rounded_interval; [lia|exact FI]. }
  assert (PB : -bpow radix2 60 <= NativeFloat.value (NativeFloat.integer free)*NativeFloat.value share <= bpow radix2 60).
  { apply NativeBounds.interval_product; [pose proof (bpow_gt_0 radix2 60); lra|exact IB|exact HS]. }
  assert (PS : NativeOperations.NoOverflow (NativeFloat.value (NativeFloat.integer free)*NativeFloat.value share)).
  { apply (NativeBounds.interval_safe 60); [lia|exact PB]. }
  destruct (NativeOperations.multiply_correct _ _ IF FS PS) as [MV MF].
  assert (MB : -bpow radix2 60 <= NativeFloat.value (NativeFloat.multiply (NativeFloat.integer free) share) <= bpow radix2 60).
  { rewrite MV. apply NativeBounds.rounded_interval; [lia|exact PB]. }
  assert (AB : -bpow radix2 61 <= NativeFloat.value (NativeFloat.multiply (NativeFloat.integer free) share)+NativeFloat.value NativeFloat.half <= bpow radix2 61).
  { rewrite NativeValues.half_value. change (-1152921504606846976 <= NativeFloat.value (NativeFloat.multiply (NativeFloat.integer free) share) <= 1152921504606846976) in MB.
    change (-2305843009213693952 <= NativeFloat.value (NativeFloat.multiply (NativeFloat.integer free) share)+ /2 <= 2305843009213693952). lra. }
  assert (AS : NativeOperations.NoOverflow (NativeFloat.value (NativeFloat.multiply (NativeFloat.integer free) share)+NativeFloat.value NativeFloat.half)).
  { apply (NativeBounds.interval_safe 61); [lia|exact AB]. }
  destruct (NativeOperations.add_correct _ _ MF NativeValues.half_finite AS) as [AV AF].
  unfold NativeFloat.scale,NativeFloat.roundInteger. rewrite NativeValues.floor_value by exact AF.
  rewrite AV,MV,IV,NativeValues.half_value.
  assert (HH : Target.half = /2) by (change (5 * /10 = /2); field).
  unfold integerDelta. rewrite HH. reflexivity.
Qed.
Print Assumptions scale_correct.
End NativeScale.
