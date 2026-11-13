Require Import Reals ZArith List Bool Lia.
Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel.
Module NativeClampFacts.
Import NativeSchedule.
Open Scope Z_scope.
Lemma one_seed : forall r, seed (fst (NativeClamp.one r)) = seed r.
Proof.
  intro r. unfold NativeClamp.one. destruct (Z.ltb (main r) (minimum (seed r))); [reflexivity|].
  destruct (Z.ltb (maximum (seed r)) (main r)); reflexivity.
Qed.
Lemma one_frozen : forall r, frozen (fst (NativeClamp.one r)) = frozen r.
Proof.
  intro r. unfold NativeClamp.one. destruct (Z.ltb (main r) (minimum (seed r))); [reflexivity|].
  destruct (Z.ltb (maximum (seed r)) (main r)); reflexivity.
Qed.
Lemma one_share : forall r, share (fst (NativeClamp.one r)) = share r.
Proof.
  intro r. unfold NativeClamp.one. destruct (Z.ltb (main r) (minimum (seed r))); [reflexivity|].
  destruct (Z.ltb (maximum (seed r)) (main r)); reflexivity.
Qed.
Lemma one_difference : forall r,
  snd (NativeClamp.one r) = main (fst (NativeClamp.one r))-main r.
Proof.
  intro r. unfold NativeClamp.one. destruct (Z.ltb (main r) (minimum (seed r))); [reflexivity|].
  destruct (Z.ltb (maximum (seed r)) (main r)); [reflexivity|]. cbn. lia.
Qed.
Lemma one_main : forall r,
  minimum (seed r) <= maximum (seed r) ->
  main (fst (NativeClamp.one r)) = clamp (seed r) (main r).
Proof.
  intros r B. unfold NativeClamp.one, clamp.
  pose proof (Z.min_spec (main r) (maximum (seed r))) as N.
  pose proof (Z.max_spec (minimum (seed r)) (Z.min (main r) (maximum (seed r)))) as M.
  destruct (Z.ltb (main r) (minimum (seed r))) eqn:L.
  - apply Z.ltb_lt in L. cbn. intuition lia.
  - apply Z.ltb_ge in L. destruct (Z.ltb (maximum (seed r)) (main r)) eqn:H.
    + apply Z.ltb_lt in H. cbn. intuition lia.
    + apply Z.ltb_ge in H. cbn. intuition lia.
Qed.
Print Assumptions one_seed.
Print Assumptions one_frozen.
Print Assumptions one_share.
Print Assumptions one_difference.
Print Assumptions one_main.
End NativeClampFacts.
