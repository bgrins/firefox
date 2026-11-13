Require Import Reals ZArith List Lia.
Require Import ShareTarget PrefixTarget ReverseTarget ReverseStructure ReverseBinding.
Require Import SignTarget SignStored SignContraction.
Import ListNotations.
Open Scope Z_scope.
Import NativeHistorySignTarget.
Lemma sign_between_self : forall x, BetweenZero x x.
Proof. intro x. split; [apply Z.le_min_l|apply Z.le_max_l]. Qed.
Lemma sign_between_trans : forall a b c,
  BetweenZero a b -> BetweenZero b c -> BetweenZero a c.
Proof.
  intros a b c. unfold BetweenZero.
  destruct (Z_le_dec 0 a); destruct (Z_le_dec 0 b);
    rewrite ?Z.min_r, ?Z.max_l in * by lia;
    rewrite ?Z.min_l, ?Z.max_r in * by lia; lia.
Qed.
Lemma sign_between_domain : forall a b,
  FreeDomain a -> BetweenZero a b -> FreeDomain b.
Proof.
  intros a b. unfold FreeDomain, BetweenZero.
  destruct (Z_le_dec 0 a); rewrite ?Z.min_r, ?Z.max_l by lia;
    rewrite ?Z.min_l, ?Z.max_r by lia; lia.
Qed.
Definition SignEventShare (event : Event) : Prop :=
  Representable (usedShare event) /\ (0 <= usedShare event <= 1)%R /\
  delta event = deltaAt (beforeFree event) (usedShare event).
Lemma sign_actual_event_shares : forall xs free,
  Admitted xs -> Forall SignEventShare (events (reverseRun xs free)).
Proof.
  intros xs free Hadmitted.
  eapply Forall_impl; [|apply event_binding_target].
  intros event [before [x [after [y [Hxs [Hindex [Hx [Hy [Hs [Hp [Hd Ha]]]]]]]]]]].
  assert (Hnth : nth_error xs (ordinal event) = Some x).
  { rewrite Hxs, Hindex. rewrite nth_error_app2 by lia. rewrite Nat.sub_diag. reflexivity. }
  destruct (sign_stored_target xs (ordinal event) x y Hadmitted Hnth Hx Hy) as [Hr Hrange].
  unfold SignEventShare. rewrite Hs. split; [exact Hr|]. split; [exact Hrange|exact Hd].
Qed.
Lemma sign_chained_interval : forall es start finish bound,
  Chained start es finish -> Forall SignEventShare es ->
  FreeDomain bound -> BetweenZero bound start ->
  Forall (fun event => BetweenZero (beforeFree event) (delta event) /\
    BetweenZero bound (beforeFree event) /\ BetweenZero bound (afterFree event)) es /\
  BetweenZero bound finish.
Proof.
  induction es as [|event es IH]; intros start finish bound Hchain Hshares Hdomain Hstart.
  - cbn [Chained] in Hchain. subst finish. split; [constructor|exact Hstart].
  - destruct Hchain as [Hbefore [Hafter Hchain]].
    apply Forall_cons_iff in Hshares. destruct Hshares as [Hevent Htail].
    destruct Hevent as [Hrepr [Hrange Hdelta]].
    assert (Hcurrent : FreeDomain (beforeFree event)).
    { eapply sign_between_domain; [exact Hdomain|]. rewrite Hbefore. exact Hstart. }
    destruct (sign_contraction_target (beforeFree event) (usedShare event)
      Hcurrent Hrepr Hrange) as [Hd Hr].
    rewrite <- Hdelta in Hd, Hr.
    assert (Hnext : BetweenZero bound (afterFree event)).
    { rewrite Hafter. eapply sign_between_trans; [|exact Hr]. rewrite Hbefore. exact Hstart. }
    destruct (IH (afterFree event) finish bound Hchain Htail Hdomain Hnext) as [Hrest Hfinish].
    split; [constructor|exact Hfinish].
    + split; [exact Hd|]. split; [rewrite Hbefore; exact Hstart|exact Hnext].
    + exact Hrest.
Qed.
Theorem sign_reverse_interval : forall xs current,
  Admitted xs -> FreeDomain current ->
  Forall (fun event => BetweenZero (beforeFree event) (delta event) /\
    BetweenZero current (beforeFree event) /\ BetweenZero current (afterFree event))
    (events (reverseRun xs current)) /\
  BetweenZero current (finalFree (reverseRun xs current)).
Proof.
  intros xs current Ha Hfree. eapply sign_chained_interval.
  - apply trace_target.
  - apply sign_actual_event_shares. exact Ha.
  - exact Hfree.
  - apply sign_between_self.
Qed.
Print Assumptions sign_between_trans.
Print Assumptions sign_between_domain.
Print Assumptions sign_actual_event_shares.
Print Assumptions sign_chained_interval.
Print Assumptions sign_reverse_interval.
