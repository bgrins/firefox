Require Import Reals ZArith List Bool Lia.
Require Import SignModel ReverseTarget NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeEntryModel NativeRefinementSpec.
Require Import NativeStepShape NativeReverseOriginal NativeReverseEffects NativeIndexed NativePreparedFields.
Require Import NativePassProtection NativeStructuralHistory NativePhaseProtection NativeProtection NativeClampMap NativeExecutionSums.
Import ListNotations.
Module NativeProjectionStage.
Import NativeSchedule.
Open Scope Z_scope.
Definition events (p : NativePass.Pass) :=
  match NativePass.reverse p with None => [] | Some r => NativeReverse.events r end.
Definition stage (p : NativePass.Pass) :=
  match NativePass.reverse p with None => NativePass.preparedRows (NativePass.prepared p)
  | Some r => NativeReverse.restored r end.
Lemma events_match : forall bytes line seeds info state result,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state=Some result ->
  Forall2 NativeRefinementTarget.EventMatches (events result)
    (ReverseTarget.events (SignHistory.distributed line (NativeEntry.seedsMode line seeds)
      (projectedState (NativeEntry.seedsMode line seeds) state))).
Proof.
  intros bytes line seeds info state result Admission History Step.
  pose proof (NativeReverseOriginal.reverse_target bytes line seeds info state result Admission History Step) as R.
  cbn zeta in R. unfold events. destruct (NativePass.reverse result).
  - exact (proj1 (proj2 R)).
  - rewrite R. constructor.
Qed.
Lemma delta_match : forall native scalar,
  Forall2 NativeRefinementTarget.EventMatches native scalar -> forall i,
  NativeReverseEffects.atDelta i native =
    SignHistory.sumZ (map (fun e => if Nat.eqb (ReverseTarget.ordinal e) i
      then ReverseTarget.delta e else 0) scalar).
Proof.
  intros native scalar H; induction H as [|x y xs ys Match Rest IH]; intro i; [reflexivity|].
  destruct Match as [Ordinal [Before [Delta Other]]].
  cbn [NativeReverseEffects.atDelta SignHistory.sumZ fold_right map].
  rewrite Ordinal,Delta. fold (NativeReverseEffects.atDelta i xs).
  rewrite IH; reflexivity.
Qed.
Lemma delta_sum_match : forall native scalar,
  Forall2 NativeRefinementTarget.EventMatches native scalar ->
  NativeExecutionSums.deltaSum native = ReverseTarget.eventSum scalar.
Proof.
  intros native scalar H; induction H as [|x y xs ys Match Rest IH]; [reflexivity|].
  destruct Match as [_ [_ [Delta _]]].
  cbn [NativeExecutionSums.deltaSum ReverseTarget.eventSum fold_right map].
  rewrite Delta. fold (NativeExecutionSums.deltaSum xs). rewrite IH; reflexivity.
Qed.
Lemma stage_rows : forall bytes line seeds info state result,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state=Some result ->
  stage result = map (fun p => snd (NativeReverseEffects.effect (events result) p))
    (NativeIndexed.indexed (NativePass.preparedRows (NativePass.prepared result))).
Proof.
  intros bytes line seeds info state result Admission History Step.
  unfold NativePass.step in Step.
  destruct (NativePass.prepare (NativeEntry.config line seeds) state) as [p|] eqn:Prepared; [|discriminate].
  pose proof (NativePreparedFields.history_prepare_fits bytes line seeds info state p Admission History Prepared) as Fits.
  destruct (NativePass.distributes p) eqn:Distributes.
  - destruct (NativePass.producer p) as [prod|] eqn:Producer; [|discriminate].
    destruct (NativeReverse.run (NativePass.growing (NativeEntry.config line seeds)) prod (frozenCount state)
      (NativePass.entryFree p) (reports state)) as [reversed|] eqn:Run; [|discriminate].
    inversion Step; subst result; cbn [stage events NativePass.finish].
    pose proof (proj1 (NativePassProtection.prepare_output _ _ _ Prepared)) as Rows.
    rewrite Producer in Rows; cbn in Rows. rewrite Rows in Fits |- *.
    exact (NativeReverseEffects.run_rows _ _ _ _ _ _ Fits Run).
  - inversion Step; subst result; cbn [stage events NativePass.finish].
    assert (Pairs : Forall (fun p => NativeReverseEffects.ActiveFits (snd p))
      (NativeIndexed.indexed (NativePass.preparedRows p))).
    { apply Forall_forall. intros [i r] Member. apply in_combine_r in Member.
      rewrite Forall_forall in Fits; exact (Fits r Member). }
    rewrite <- map_map,NativeReverseEffects.empty_effect by exact Pairs.
    unfold NativeIndexed.indexed. rewrite NativeIndexed.second. reflexivity.
Qed.
Lemma stage_kept : forall config state result,
  NativePass.step config state=Some result ->
  Forall2 NativeProtection.NativeProtection.KeepFrozen (rows state) (stage result).
Proof. intros; eapply NativeStructuralHistory.step_stage_kept; exact H. Qed.
Lemma clamped_rows : forall line seeds info state result,
  NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state=Some result ->
  NativeClamp.clampedRows (NativePass.clamped result)=map NativeClampMap.each (stage result).
Proof.
  intros line seeds info state result History Step.
  pose proof (proj1 (NativeStructuralHistory.history_count_fresh line seeds info state History)) as Count.
  pose proof (stage_kept _ _ _ Step) as Kept.
  destruct (NativeStepShape.step_shape _ _ _ Step) as [_ Shape].
  rewrite Shape. apply NativeClampMap.finish_rows; [exact Count|exact Kept].
Qed.
Lemma clamped_kept : forall config state result,
  NativePass.step config state=Some result ->
  Forall2 NativeProtection.NativeProtection.KeepFrozen (rows state)
    (NativeClamp.clampedRows (NativePass.clamped result)).
Proof.
  intros config state result Step.
  eapply NativePassProtection.kept_trans; [eapply stage_kept; exact Step|].
  destruct (NativeStepShape.step_shape _ _ _ Step) as [_ Shape].
  rewrite Shape. apply NativePhaseProtection.clamp_kept.
Qed.
Lemma total_balance : forall config state result,
  NativePass.step config state=Some result ->
  NativeClamp.total (NativePass.clamped result) =
    NativeExecutionSums.rowSum (NativeClamp.clampedRows (NativePass.clamped result))-
    NativeExecutionSums.rowSum (NativePass.preparedRows (NativePass.prepared result))-
    NativeExecutionSums.deltaSum (events result).
Proof.
  intros config state result Step. unfold NativePass.step in Step.
  destruct (NativePass.prepare config state) as [p|] eqn:Prepared; [|discriminate].
  destruct (NativePass.distributes p) eqn:Distributes.
  - destruct (NativePass.producer p) as [prod|] eqn:Producer; [|discriminate].
    destruct (NativeReverse.run (NativePass.growing config) prod (frozenCount state)
      (NativePass.entryFree p) (reports state)) as [reversed|] eqn:Run; [|discriminate].
    inversion Step; subst result.
    pose proof (proj1 (NativePassProtection.prepare_output config state p Prepared)) as Rows.
    rewrite Producer in Rows; cbn in Rows.
    rewrite (NativeExecutionSums.finish_reverse_balance config state p prod reversed Run).
    cbn [events NativePass.finish]. rewrite Rows; reflexivity.
  - inversion Step; subst result. rewrite NativeExecutionSums.finish_no_reverse_balance.
    cbn [events NativePass.finish NativeExecutionSums.deltaSum]. lia.
Qed.
Print Assumptions events_match.
Print Assumptions delta_match.
Print Assumptions delta_sum_match.
Print Assumptions stage_rows.
Print Assumptions stage_kept.
Print Assumptions clamped_rows.
Print Assumptions clamped_kept.
Print Assumptions total_balance.
End NativeProjectionStage.
