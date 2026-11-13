Require Import Reals ZArith List Bool Lia Psatz.
Require Import NativeState NativeClampModel NativeClampFacts NativeBudgetArithmetic.
Import ListNotations.
Module NativeBudgetClamp.
Import NativeSchedule NativeBudgetArithmetic.
Open Scope Z_scope.
Definition bound (acc : Z) (rs : list Row) := Z.abs acc+Z.of_nat (length rs)*differenceCap.
Lemma loop_budget : forall rs left index acc,
  Forall Good rs -> bound acc rs<=9223372036854775807 ->
  Forall NativeClamp.FitsEvent (NativeClamp.events (NativeClamp.loop left index acc rs)) /\
  Forall (fun e => Z.abs (NativeClamp.totalAfter e)<=bound acc rs)
    (NativeClamp.events (NativeClamp.loop left index acc rs)) /\
  Z.abs (NativeClamp.total (NativeClamp.loop left index acc rs))<=bound acc rs.
Proof.
  induction rs as [|r tail IH]; intros left index acc GoodRows Safe.
  - destruct left; cbn [NativeClamp.loop bound]; split; [constructor|]. split; [constructor|lia].
  - destruct left as [|k].
    + cbn [NativeClamp.loop]. split; [constructor|]. split; [constructor|].
      unfold bound,differenceCap; pose proof (Nat2Z.is_nonneg (length (r::tail))); nia.
    + inversion GoodRows as [|head rest Head Tail]; subst.
      assert (Count : Z.of_nat (length (r::tail))=1+Z.of_nat (length tail)).
      { cbn [length]; rewrite Nat2Z.inj_succ; lia. }
      cbn [NativeClamp.loop]. destruct (frozen r) eqn:Frozen.
      * assert (B : bound acc tail<=bound acc (r::tail)).
        { unfold bound,differenceCap; rewrite Count; lia. }
        destruct (IH (S k) (S index) acc Tail ltac:(lia)) as [Events [Prefixes Terminal]].
        cbn [NativeClamp.events NativeClamp.total]. split; [exact Events|]. split.
        -- eapply Forall_impl; [|exact Prefixes]. intros e E; lia.
        -- lia.
      * pose proof (clamp_difference r Head) as Delta.
        assert (Next : bound (acc+snd (NativeClamp.one r)) tail<=bound acc (r::tail)).
        { unfold bound; rewrite Count. pose proof (Z.abs_triangle acc (snd (NativeClamp.one r))); nia. }
        destruct (IH k (S index) (acc+snd (NativeClamp.one r)) Tail ltac:(lia))
          as [Events [Prefixes Terminal]].
        assert (FitsBefore : Fits64 (main r)) by (apply acquired_fits; exact (proj2 Head)).
        assert (FitsAfter : Fits64 (main (fst (NativeClamp.one r)))) by
          (apply acquired_fits; exact (proj2 (clamp_good r Head))).
        assert (FitsDelta : Fits64 (snd (NativeClamp.one r))) by (apply abs_fits; unfold differenceCap in Delta; lia).
        assert (FitsAcc : Fits64 acc).
        { apply abs_fits. unfold bound,differenceCap in Safe; pose proof (Nat2Z.is_nonneg (length (r::tail))); nia. }
        assert (FitsNext : Fits64 (acc+snd (NativeClamp.one r))).
        { apply abs_fits. unfold bound,differenceCap in Next,Safe; pose proof (Nat2Z.is_nonneg (length tail)); nia. }
        cbn [NativeClamp.events NativeClamp.total]. split.
        -- constructor; [unfold NativeClamp.FitsEvent; cbn; repeat (constructor; [assumption|]); constructor|exact Events].
        -- split.
           ++ constructor.
              ** cbn; unfold bound,differenceCap in *; pose proof (Nat2Z.is_nonneg (length tail)); nia.
              ** eapply Forall_impl; [|exact Prefixes]. intros e E; lia.
           ++ lia.
Qed.
Lemma bounded_loop : forall rs left index acc free n,
  Forall Good rs -> (length rs<=n)%nat -> (n<=134217727)%nat ->
  Z.abs acc<=Z.abs free -> Z.abs free<=cap ->
  Forall NativeClamp.FitsEvent (NativeClamp.events (NativeClamp.loop left index acc rs)) /\
  Forall (fun e => Z.abs (NativeClamp.totalAfter e)<=Z.abs free+Z.of_nat n*differenceCap)
    (NativeClamp.events (NativeClamp.loop left index acc rs)) /\
  Fits64 (NativeClamp.total (NativeClamp.loop left index acc rs)).
Proof.
  intros rs left index acc free n GoodRows Length Count Acc Free.
  assert (Bound : bound acc rs<=Z.abs free+Z.of_nat n*differenceCap).
  { unfold bound,differenceCap; assert (Z.of_nat (length rs)<=Z.of_nat n) by lia; nia. }
  pose proof (budget_fits n free Count Free) as Safe.
  destruct (loop_budget rs left index acc GoodRows ltac:(lia)) as [Events [Prefixes Terminal]].
  split; [exact Events|]. split.
  - eapply Forall_impl; [|exact Prefixes]. intros e E; lia.
  - apply abs_fits; lia.
Qed.
Print Assumptions loop_budget.
Print Assumptions bounded_loop.
End NativeBudgetClamp.
