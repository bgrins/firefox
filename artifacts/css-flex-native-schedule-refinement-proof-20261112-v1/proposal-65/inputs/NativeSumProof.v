Require Import Reals ZArith List Bool Lia Psatz.
Require Import Flocq.Core.Raux Gappa.Gappa_library.
Require Import WeightTarget Weights ShareTarget Share.
Require Import NativeFloatModel NativeOperations.
Module NativeSumProof.
Open Scope R_scope.
Lemma add_bounded : forall x y,
  NativeFloat.finite x = true -> NativeFloat.finite y = true ->
  0 <= NativeFloat.value x <= sumLimit -> WeightValid (NativeFloat.value y) ->
  NativeFloat.finite (NativeFloat.add x y) = true /\
  NativeFloat.value (NativeFloat.add x y) = rn (NativeFloat.value x + NativeFloat.value y) /\
  StepBound (NativeFloat.value x) (NativeFloat.value y).
Proof.
  intros x y FX FY X Y.
  pose proof (Weights.addition_target _ _ X Y) as Bounds.
  assert (N : NativeOperations.NoOverflow (NativeFloat.value x + NativeFloat.value y)).
  { unfold NativeOperations.NoOverflow. destruct Bounds as [_ [Rounded _]].
    rewrite Rabs_pos_eq by exact (proj1 Rounded).
    assert (L : intermediateLimit < bpow radix2 1024).
    { change (bpow radix2 193 < bpow radix2 1024). apply bpow_lt; lia. }
    lra. }
  destruct (NativeOperations.add_correct x y FX FY N) as [Value Finite].
  split; [exact Finite|]. split; [exact Value|exact Bounds].
Qed.
Lemma add_stride : forall x y processed,
  NativeFloat.finite x = true -> NativeFloat.finite y = true ->
  (0 <= processed <= countLimit)%Z ->
  0 <= NativeFloat.value x <= IZR processed*stride -> WeightValid (NativeFloat.value y) ->
  NativeFloat.finite (NativeFloat.add x y) = true /\
  NativeFloat.value (NativeFloat.add x y) = rn (NativeFloat.value x + NativeFloat.value y) /\
  0 <= NativeFloat.value (NativeFloat.add x y) <= IZR (processed+1)*stride.
Proof.
  intros x y processed FX FY Count X Y.
  destruct (add_bounded x y FX FY (Weights.count_bound processed _ Count X) Y)
    as [Finite [Value [_ [Rounded Upper]]]].
  split; [exact Finite|]. split; [exact Value|].
  rewrite Value, plus_IZR. cbn [IZR]. lra.
Qed.
Print Assumptions add_bounded.
Print Assumptions add_stride.
End NativeSumProof.
