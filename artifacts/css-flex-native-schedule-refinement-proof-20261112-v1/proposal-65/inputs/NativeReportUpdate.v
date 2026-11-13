Require Import Reals ZArith List Bool Lia.
Require Import NativeFloatModel NativeState.
Import ListNotations.
Module NativeReportUpdate.
Import NativeSchedule.
Lemma indexed_snd : forall (xs : list Report) start,
  map snd (combine (seq start (length xs)) xs) = xs.
Proof.
  intro xs. induction xs as [|x tail IH]; intro start; cbn; [reflexivity|].
  f_equal. apply IH.
Qed.
Lemma indexed_length : forall (xs : list Report) start,
  length (combine (seq start (length xs)) xs) = length xs.
Proof. intros. rewrite combine_length, seq_length, Nat.min_id. reflexivity. Qed.
Lemma update_identity : forall xs i d updated,
  updateReport i d (Some xs) = Some updated ->
  map reportIdentity updated = map reportIdentity xs.
Proof.
  intros xs i d updated H. unfold updateReport in H. inversion H; subst updated.
  rewrite map_map.
  transitivity (map reportIdentity (map snd (combine (seq 0 (length xs)) xs))).
  - rewrite map_map. apply map_ext. intros [index r]. cbn.
    destruct (Nat.eqb index i); reflexivity.
  - rewrite indexed_snd. reflexivity.
Qed.
Lemma update_base : forall xs i d updated,
  updateReport i d (Some xs) = Some updated ->
  map reportBase updated = map reportBase xs.
Proof.
  intros xs i d updated H. unfold updateReport in H. inversion H; subst updated.
  rewrite map_map.
  transitivity (map reportBase (map snd (combine (seq 0 (length xs)) xs))).
  - rewrite map_map. apply map_ext. intros [index r]. cbn.
    destruct (Nat.eqb index i); reflexivity.
  - rewrite indexed_snd. reflexivity.
Qed.
Lemma update_length : forall xs i d updated,
  updateReport i d (Some xs) = Some updated -> length updated = length xs.
Proof.
  intros xs i d updated H. unfold updateReport in H. inversion H; subst updated.
  rewrite map_length. apply indexed_length.
Qed.
Print Assumptions indexed_snd.
Print Assumptions indexed_length.
Print Assumptions update_identity.
Print Assumptions update_base.
Print Assumptions update_length.
End NativeReportUpdate.
