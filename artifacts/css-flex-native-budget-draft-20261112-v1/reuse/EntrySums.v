Require Import ZArith List Psatz.
Require Import EntryModel.
Import ListNotations EntryAcquisition.
Open Scope Z_scope.
Lemma entry_fold_add : forall xs start,
  fold_left Z.add xs start = start + fold_right Z.add 0 xs.
Proof. induction xs; intros start; simpl; [lia|rewrite IHxs; lia]. Qed.
Lemma entry_fold_sub : forall xs start,
  fold_left Z.sub xs start = start - fold_right Z.add 0 xs.
Proof. induction xs; intros start; simpl; [lia|rewrite IHxs; lia]. Qed.
Lemma entry_sum_range : forall xs, Forall Acquired32 xs ->
  -(Z.of_nat (length xs)*2147483648) <= fold_right Z.add 0 xs <=
    Z.of_nat (length xs)*2147483648.
Proof.
  intros xs H. induction H.
  - simpl; lia.
  - cbn [length fold_right]. rewrite Nat2Z.inj_succ.
    unfold Acquired32 in H. lia.
Qed.
Lemma entry_sum_abs : forall xs, Forall Acquired32 xs ->
  Z.abs (fold_right Z.add 0 xs) <= Z.of_nat (length xs)*2147483648.
Proof. intros xs H. apply Z.abs_le. exact (entry_sum_range xs H). Qed.
Lemma entry_firstn_admitted : forall xs n, Forall Acquired32 xs -> Forall Acquired32 (firstn n xs).
Proof.
  intros xs n H. revert n. induction H; intros n; destruct n; simpl; constructor; auto.
Qed.
Lemma entry_used_admitted : forall values items, Forall2 UsedSource values items ->
  Forall Acquired32 values /\ length values = length items.
Proof.
  intros values items H. induction H.
  - split; constructor.
  - destruct IHForall2 as [Hv Hl]. split; [constructor; [exact (proj1 H)|exact Hv]|simpl; lia].
Qed.
Print Assumptions entry_fold_add.
Print Assumptions entry_fold_sub.
Print Assumptions entry_sum_range.
Print Assumptions entry_sum_abs.
Print Assumptions entry_firstn_admitted.
Print Assumptions entry_used_admitted.
