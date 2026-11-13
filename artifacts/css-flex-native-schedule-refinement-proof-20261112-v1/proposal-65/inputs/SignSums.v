Require Import ZArith List Lia.
Require Import SignModel.
Import ListNotations SignHistory.
Open Scope Z_scope.
Lemma sign_sum_add : forall (A : Type) (xs : list A) f g,
  sumZ (map (fun x => f x + g x) xs) = sumZ (map f xs) + sumZ (map g xs).
Proof.
  intros A xs f g. induction xs as [|x xs IH]; [reflexivity|].
  change ((f x+g x)+sumZ (map (fun y => f y+g y) xs) =
    (f x+sumZ (map f xs))+(g x+sumZ (map g xs))).
  rewrite IH. lia.
Qed.
Lemma sign_sum_sub : forall (A : Type) (xs : list A) f g,
  sumZ (map (fun x => f x - g x) xs) = sumZ (map f xs) - sumZ (map g xs).
Proof.
  intros A xs f g. induction xs as [|x xs IH]; [reflexivity|].
  change ((f x-g x)+sumZ (map (fun y => f y-g y) xs) =
    (f x+sumZ (map f xs))-(g x+sumZ (map g xs))).
  rewrite IH. lia.
Qed.
Lemma sign_sum_le : forall (A : Type) (xs : list A) f g,
  (forall x, In x xs -> f x <= g x) -> sumZ (map f xs) <= sumZ (map g xs).
Proof.
  intros A xs. induction xs as [|x xs IH]; intros f g H; [cbn; lia|].
  specialize (IH f g ltac:(intros y Hy; apply H; right; exact Hy)).
  pose proof (H x (or_introl eq_refl)).
  change (f x+sumZ (map f xs) <= g x+sumZ (map g xs)). lia.
Qed.
Lemma sign_sum_constant_zero : forall (A : Type) (xs : list A),
  sumZ (map (fun _ => 0) xs) = 0.
Proof.
  intros A xs. induction xs as [|x xs IH]; [reflexivity|].
  change (0+sumZ (map (fun _ : A => 0) xs) = 0). rewrite IH. reflexivity.
Qed.
Lemma sign_sum_zero_pointwise : forall (A : Type) (xs : list A) f,
  (forall x, In x xs -> 0 <= f x) -> sumZ (map f xs) = 0 ->
  forall x, In x xs -> f x = 0.
Proof.
  intros A xs. induction xs as [|x xs IH]; intros f Hnonnegative Hzero y Hin; [contradiction|].
  assert (Htail : forall z, In z xs -> 0 <= f z) by (intros z Hz; apply Hnonnegative; right; exact Hz).
  assert (Hsum : 0 <= sumZ (map f xs)).
  { pose proof (sign_sum_le A xs (fun _ => 0) f Htail) as Hle.
    rewrite sign_sum_constant_zero in Hle.
    lia. }
  pose proof (Hnonnegative x (or_introl eq_refl)) as Hhead.
  cbn [map sumZ fold_right] in Hzero. unfold sumZ in Hsum.
  destruct Hin as [Heq|Hin].
  - subst y. lia.
  - apply IH; [exact Htail|unfold sumZ; lia|exact Hin].
Qed.
Print Assumptions sign_sum_add.
Print Assumptions sign_sum_sub.
Print Assumptions sign_sum_le.
Print Assumptions sign_sum_zero_pointwise.
