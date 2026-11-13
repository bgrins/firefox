Require Import ZArith List Lia.
Require Import NativeState.
Import ListNotations.
Module NativeIndexed.
Import NativeSchedule.
Definition indexed (rs : list Row) := combine (seq 0 (length rs)) rs.
Lemma first : forall (rs : list Row) start,
  map fst (combine (seq start (length rs)) rs) = seq start (length rs).
Proof. induction rs; intros; cbn; [reflexivity|rewrite IHrs; reflexivity]. Qed.
Lemma second : forall (rs : list Row) start,
  map snd (combine (seq start (length rs)) rs) = rs.
Proof. induction rs; intros; cbn; [reflexivity|rewrite IHrs; reflexivity]. Qed.
Lemma unique : forall rs, NoDup (map fst (indexed rs)).
Proof. intros; unfold indexed; rewrite first; apply seq_NoDup. Qed.
Lemma nth_indexed : forall (rs : list Row) start i r,
  nth_error rs i = Some r ->
  nth_error (combine (seq start (length rs)) rs) i = Some ((start+i)%nat,r).
Proof.
  induction rs as [|head tail IH]; intros start [|i] r N; cbn in N; try discriminate.
  - inversion N; subst. cbn. rewrite Nat.add_0_r. reflexivity.
  - cbn. rewrite (IH (S start) i r N). f_equal. f_equal. lia.
Qed.
Lemma member : forall rs i r, In (i,r) (indexed rs) -> nth_error rs i = Some r.
Proof.
  assert (General : forall (rs : list Row) start i r,
    In (i,r) (combine (seq start (length rs)) rs) ->
    exists n, i=(start+n)%nat /\ nth_error rs n=Some r).
  { induction rs as [|head tail IH]; intros start i r N; cbn in N; [contradiction|].
    destruct N as [E|N].
    - inversion E; subst; exists 0%nat; cbn; split; [lia|reflexivity].
    - destruct (IH (S start) i r N) as [n [E Nth]].
      exists (S n); cbn; split; [lia|exact Nth]. }
  intros rs i r N. destruct (General rs 0%nat i r N) as [n [E Nth]]. cbn in E; subst i; exact Nth.
Qed.
Lemma nth_map_indexed : forall (A : Type) (f : nat*Row -> A) rs i r,
  nth_error rs i=Some r -> nth_error (map f (indexed rs)) i=Some (f (i,r)).
Proof. intros A f rs i r N. unfold indexed. rewrite nth_error_map,(nth_indexed rs 0 i r N). reflexivity. Qed.
Lemma length_indexed : forall rs, length (indexed rs) = length rs.
Proof. intro rs. pose proof (f_equal (@length Row) (second rs 0)). rewrite map_length in H. exact H. Qed.
Lemma nth_ext : forall (A : Type) (xs ys : list A),
  (forall i, nth_error xs i=nth_error ys i) -> xs=ys.
Proof.
  intros A xs; induction xs as [|x xs IH]; intros [|y ys] H; try reflexivity.
  - specialize (H 0%nat); discriminate.
  - specialize (H 0%nat); discriminate.
  - pose proof (H 0%nat) as Head. cbn in Head; inversion Head; subst y.
    f_equal; apply IH; intro i; exact (H (S i)).
Qed.
Lemma related_nth : forall (R : Row -> Row -> Prop) xs ys,
  Forall2 R xs ys -> forall i x, nth_error xs i=Some x ->
  exists y, nth_error ys i=Some y /\ R x y.
Proof.
  intros R xs ys H; induction H as [|x y xs ys Rel Rest IH];
    intros [|i] item N; cbn in N; try discriminate.
  - inversion N; subst item. exists y; split; [reflexivity|exact Rel].
  - destruct (IH i item N) as [value [Nth Related]]. exists value; split; assumption.
Qed.
Lemma combine_map : forall (A B : Type) (f : A -> B) (indices : list nat) xs,
  combine indices (map f xs)=map (fun p => (fst p,f (snd p))) (combine indices xs).
Proof.
  intros A B f indices; induction indices as [|i tail IH]; intros [|x xs]; cbn; try reflexivity.
  rewrite IH; reflexivity.
Qed.
Print Assumptions combine_map.
Print Assumptions first.
Print Assumptions second.
Print Assumptions unique.
Print Assumptions nth_indexed.
Print Assumptions member.
Print Assumptions nth_map_indexed.
Print Assumptions length_indexed.
Print Assumptions nth_ext.
Print Assumptions related_nth.
End NativeIndexed.
