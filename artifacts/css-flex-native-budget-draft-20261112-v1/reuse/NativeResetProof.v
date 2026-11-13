Require Import Reals ZArith List Bool Lia.
Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel.
Import ListNotations.
Module NativeResetProof.
Import NativeSchedule.
Open Scope Z_scope.
Definition resetRow (r : Row) := if frozen r then r else replaceMain r (baseSize (seed r)).
Definition currentSize (r : Row) := if frozen r then main r else baseSize (seed r).
Lemma reset_row_seed : forall r, seed (resetRow r) = seed r.
Proof. intro r. unfold resetRow. destruct (frozen r); reflexivity. Qed.
Lemma reset_row_frozen : forall r, frozen (resetRow r) = frozen r.
Proof. intro r. unfold resetRow. destruct (frozen r) eqn:F; exact F. Qed.
Lemma reset_row_share : forall r, share (resetRow r) = share r.
Proof. intro r. unfold resetRow. destruct (frozen r); reflexivity. Qed.
Lemma reset_row_main : forall r, main (resetRow r) = currentSize r.
Proof. intro r. unfold resetRow, currentSize. destruct (frozen r); reflexivity. Qed.
Lemma reset_rows : forall rs index free,
  NativePass.resetRows (NativePass.reset index free rs) = map resetRow rs.
Proof.
  induction rs as [|r tail IH]; intros index free; [reflexivity|].
  change (resetRow r :: NativePass.resetRows
    (NativePass.reset (S index) (free-main (resetRow r)) tail) = resetRow r :: map resetRow tail).
  rewrite IH. reflexivity.
Qed.
Lemma reset_free : forall rs index free,
  NativePass.freeSpace (NativePass.reset index free rs) = fold_left Z.sub (map currentSize rs) free.
Proof.
  induction rs as [|r tail IH]; intros index free; [reflexivity|].
  change (NativePass.freeSpace (NativePass.reset (S index) (free-main (resetRow r)) tail) =
    fold_left Z.sub (map currentSize tail) (free-currentSize r)).
  rewrite reset_row_main. apply IH.
Qed.
Lemma reset_seed_map : forall rs index free,
  map seed (NativePass.resetRows (NativePass.reset index free rs)) = map seed rs.
Proof. intros. rewrite reset_rows, map_map. apply map_ext. apply reset_row_seed. Qed.
Lemma reset_frozen_map : forall rs index free,
  map frozen (NativePass.resetRows (NativePass.reset index free rs)) = map frozen rs.
Proof. intros. rewrite reset_rows, map_map. apply map_ext. apply reset_row_frozen. Qed.
Lemma reset_share_map : forall rs index free,
  map share (NativePass.resetRows (NativePass.reset index free rs)) = map share rs.
Proof. intros. rewrite reset_rows, map_map. apply map_ext. apply reset_row_share. Qed.
Print Assumptions reset_row_seed.
Print Assumptions reset_row_frozen.
Print Assumptions reset_row_share.
Print Assumptions reset_row_main.
Print Assumptions reset_rows.
Print Assumptions reset_free.
Print Assumptions reset_seed_map.
Print Assumptions reset_frozen_map.
Print Assumptions reset_share_map.
End NativeResetProof.
