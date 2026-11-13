Require Import Reals ZArith List Bool Lia.
Require Import SignModel NativeState NativeReverseModel NativeClampModel NativePassModel NativeEntryModel NativeRefinementSpec NativeStepShape.
Require Import NativePassProtection NativeReverseProtection NativeStructuralHistory.
Require Import NativeBudgetArithmetic NativeBudgetReset NativeBudgetReverse NativeBudgetClamp NativeBudgetInputs.
Import ListNotations.
Module NativeBudgetOriginal.
Import NativeSchedule NativeBudgetArithmetic.
Open Scope Z_scope.
Definition stage (p : NativePass.Prepared) (r : option NativeReverse.Result) :=
  match r with None=>NativePass.preparedRows p | Some out=>NativeReverse.restored out end.
Definition start (r : option NativeReverse.Result) :=
  match r with None=>0 | Some out=>NativeReverse.violation out end.
Lemma finish_budget : forall config state p reversed n,
  Forall Good (stage p reversed) -> (length (stage p reversed)<=n)%nat -> (n<=134217727)%nat ->
  Z.abs (start reversed)<=Z.abs (NativePass.entryFree p) -> ReverseTarget.FreeDomain (NativePass.entryFree p) ->
  Forall NativeClamp.FitsEvent (NativeClamp.events (NativePass.clamped (NativePass.finish config state p reversed))) /\
  Fits64 (NativeClamp.total (NativePass.clamped (NativePass.finish config state p reversed))) /\
  Forall (fun e => Z.abs (NativeClamp.totalAfter e)<=Z.abs (NativePass.entryFree p)+Z.of_nat n*4294967295)
    (NativeClamp.events (NativePass.clamped (NativePass.finish config state p reversed))).
Proof.
  intros config state p reversed n GoodRows Length Count Acc Free.
  destruct (NativeBudgetClamp.bounded_loop (stage p reversed)
    (length (stage p reversed)-frozenCount state)%nat O (start reversed) (NativePass.entryFree p) n
    GoodRows Length Count Acc (domain_abs _ Free)) as [Events [Prefixes Final]].
  cbn [NativePass.finish]. fold (stage p reversed) (start reversed).
  split; [exact Events|]. split; assumption.
Qed.
Lemma step_budget : forall bytes line seeds info state result,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state=Some result ->
  NativePass.FitsPass result /\ Fits64 (NativeClamp.total (NativePass.clamped result)) /\
  (match NativePass.reverse result with None=>True | Some out=>
    SignHistory.sumZ (map (fun e=>Z.abs (NativeReverse.delta e)) (NativeReverse.events out))<=
      Z.abs (NativePass.entryFree (NativePass.prepared result)) /\
    Forall (fun e=>Z.abs (NativeReverse.totalAfter e)<=Z.abs (NativePass.entryFree (NativePass.prepared result)))
      (NativeReverse.events out) end) /\
  Forall (fun e=>Z.abs (NativeClamp.totalAfter e)<=
    Z.abs (NativePass.entryFree (NativePass.prepared result))+Z.of_nat (length seeds)*4294967295)
    (NativeClamp.events (NativePass.clamped result)).
Proof.
  intros bytes line seeds info state result Admission History Step.
  destruct (NativeBudgetInputs.seeds_count bytes line seeds info state Admission History) as [Count Length].
  unfold NativePass.step in Step.
  destruct (NativePass.prepare (NativeEntry.config line seeds) state) as [p|] eqn:Prepared; [|discriminate].
  pose proof (NativeBudgetInputs.prepared_good bytes line seeds info state p Admission History Prepared) as GoodRows.
  pose proof (NativeBudgetInputs.prepared_domain bytes line seeds info state p Admission History Prepared) as Domain.
  pose proof (proj1 (NativeBudgetInputs.acquisition bytes line seeds info state p Admission History Prepared)) as Acquisition.
  assert (EntryFit : Fits64 (NativePass.entryFree p)).
  { apply abs_fits; pose proof (domain_abs _ Domain); unfold cap in *; lia. }
  pose proof (NativePassProtection.prepare_kept _ _ _ Prepared) as Kept.
  pose proof (NativeStructuralHistory.kept_length _ _ Kept) as PreparedLength.
  destruct (NativePass.distributes p) eqn:Distributes.
  - destruct (NativePass.producer p) as [produced|] eqn:Producer; [|discriminate].
    destruct (NativeReverse.run (NativePass.growing (NativeEntry.config line seeds)) produced (frozenCount state)
      (NativePass.entryFree p) (reports state)) as [reversed|] eqn:Run; [|discriminate].
    pose proof (proj1 (NativePassProtection.prepare_output _ _ _ Prepared)) as Rows.
    rewrite Producer in Rows; cbn in Rows. rewrite Rows in GoodRows,PreparedLength.
    destruct (NativeBudgetInputs.producer_shared bytes line seeds info state p produced Admission History Prepared Producer)
      as [Shares Finite].
    pose proof (NativeBudgetReverse.run_budget _ _ _ _ _ _ GoodRows Shares Finite Domain Run) as Reverse.
    pose proof (NativeBudgetReverse.restored_good _ _ _ Reverse) as StageGood.
    pose proof (NativeReverseProtection.run_kept _ _ _ _ _ _ Run) as ReverseKept.
    pose proof (NativeStructuralHistory.kept_length _ _ ReverseKept) as ReverseLength.
    destruct Reverse as [ReverseEvents [Corrections [Terminal [Mass Restored]]]].
    assert (Acc : Z.abs (NativeReverse.violation reversed)<=Z.abs (NativePass.entryFree p)).
    { pose proof (Z.abs_nonneg (NativeReverse.finalFree reversed)); lia. }
    assert (FinalFit : Fits64 (NativeReverse.finalFree reversed)).
    { apply abs_fits; pose proof (domain_abs _ Domain); unfold cap in *.
      pose proof (Z.abs_nonneg (NativeReverse.violation reversed)); lia. }
    destruct (finish_budget (NativeEntry.config line seeds) state p (Some reversed) (length seeds)
      StageGood ltac:(cbn [stage]; lia) Count Acc Domain) as [ClampEvents [ClampFinal ClampPrefixes]].
    inversion Step; subst result. cbn [NativePass.prepared NativePass.reverse NativePass.finish].
    split.
    + unfold NativePass.FitsPass; cbn [NativePass.finish].
      split; [exact Acquisition|]. split; [exact EntryFit|]. split; [split; assumption|exact ClampEvents].
    + split; [exact ClampFinal|]. split; [|exact ClampPrefixes]. split; [|exact Corrections].
      rewrite <- NativeBudgetReverse.delta_mass_map.
      pose proof (Z.abs_nonneg (NativeReverse.finalFree reversed)); lia.
  - destruct (finish_budget (NativeEntry.config line seeds) state p None (length seeds)
      GoodRows ltac:(cbn [stage]; lia) Count ltac:(cbn [start]; apply Z.abs_nonneg) Domain)
      as [ClampEvents [ClampFinal ClampPrefixes]].
    inversion Step; subst result. split.
    + unfold NativePass.FitsPass; cbn [NativePass.finish].
      split; [exact Acquisition|]. split; [exact EntryFit|]. split; [exact I|exact ClampEvents].
    + split; [exact ClampFinal|]. split; [exact I|exact ClampPrefixes].
Qed.
Theorem budget_target : NativeRefinementTarget.BudgetTarget.
Proof.
  intros bytes line seeds info state result Admission History Step.
  destruct (step_budget bytes line seeds info state result Admission History Step)
    as [Pass [Total [Reverse ClampPrefixes]]].
  pose proof (proj1 (NativeStepShape.step_shape _ _ _ Step)) as Prepared.
  destruct (NativeBudgetInputs.acquisition bytes line seeds info state (NativePass.prepared result)
    Admission History Prepared) as [_ [Space [Inner [Gap [MBP Fixed]]]]].
  pose proof (proj1 (NativeBudgetInputs.seeds_count bytes line seeds info state Admission History)) as Count.
  split; [exact Pass|]. split; [exact Space|]. split; [exact Inner|]. split; [exact Gap|].
  split; [exact MBP|]. split; [exact Fixed|]. split; [exact Total|]. split; [exact Count|].
  split; assumption.
Qed.
Print Assumptions finish_budget.
Print Assumptions step_budget.
Print Assumptions budget_target.
End NativeBudgetOriginal.
