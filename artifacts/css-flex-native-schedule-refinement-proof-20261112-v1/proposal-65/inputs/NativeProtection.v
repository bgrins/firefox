Require Import Reals ZArith List Bool Lia.
Require Import NativeFloatModel NativeState.
Import ListNotations.
Module NativeProtection.
Import NativeSchedule.
Definition Protect (before after : Row) := seed after = seed before /\
  (frozen before = true -> after = before).
Definition KeepFrozen (before after : Row) := Protect before after /\ frozen after = frozen before.
Lemma protect_refl : forall r, Protect r r.
Proof. intros; split; auto. Qed.
Lemma keep_refl : forall r, KeepFrozen r r.
Proof. intros; split; [apply protect_refl|reflexivity]. Qed.
Lemma protect_trans : forall a b c, Protect a b -> Protect b c -> Protect a c.
Proof.
  intros a b c [S F] [T G]. split; [congruence|]. intro H.
  rewrite (F H) in G. exact (G H).
Qed.
Lemma keeps_trans : forall a b c, KeepFrozen a b -> KeepFrozen b c -> KeepFrozen a c.
Proof. intros a b c [P F] [Q G]. split; [eapply protect_trans; eassumption|congruence]. Qed.
Lemma protected_refl : forall xs, Forall2 Protect xs xs.
Proof. intro xs; induction xs; constructor; [apply protect_refl|assumption]. Qed.
Lemma kept_refl : forall xs, Forall2 KeepFrozen xs xs.
Proof. intro xs; induction xs; constructor; [apply keep_refl|assumption]. Qed.
Lemma protected_trans : forall xs ys zs,
  Forall2 Protect xs ys -> Forall2 Protect ys zs -> Forall2 Protect xs zs.
Proof.
  intros xs ys zs H. revert zs. induction H; intros zs K; inversion K; subst; constructor.
  - eapply protect_trans; eassumption.
  - eapply IHForall2; eassumption.
Qed.
Lemma protected_seeds : forall xs ys, Forall2 Protect xs ys -> map seed ys = map seed xs.
Proof.
  intros xs ys H. induction H; cbn; [reflexivity|]. destruct H as [S F]. rewrite S, IHForall2. reflexivity.
Qed.
Lemma protected_frozen_nth : forall xs ys,
  Forall2 Protect xs ys -> forall i r,
    nth_error xs i = Some r -> frozen r = true -> nth_error ys i = Some r.
Proof.
  intros xs ys H. induction H; intros i r N F.
  - destruct i; discriminate.
  - destruct i as [|i]; cbn in N |- *.
    + inversion N; subst r. destruct H as [S K]. rewrite K by exact F. reflexivity.
    + eapply IHForall2; eassumption.
Qed.
Print Assumptions protect_refl.
Print Assumptions keep_refl.
Print Assumptions protect_trans.
Print Assumptions keeps_trans.
Print Assumptions protected_refl.
Print Assumptions kept_refl.
Print Assumptions protected_trans.
Print Assumptions protected_seeds.
Print Assumptions protected_frozen_nth.
End NativeProtection.
