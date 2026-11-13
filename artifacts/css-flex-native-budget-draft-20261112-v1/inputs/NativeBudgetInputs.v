Require Import Reals ZArith List Bool Lia.
Require Import EntryModel EntryTarget EntryAcquisitionProof EntryNumerals SignModel ReverseTarget.
Require Import NativeFloatModel NativeProducerModel NativeState NativePassModel NativeEntryModel NativeStepShape NativeSourceHistory.
Require Import NativeMainBounds NativeActiveInputs NativeProducerSums NativeProducerRows NativeProducerRun.
Require Import NativeProducerReset NativePrepareProducer NativeStructuralHistory NativePreparedFields.
Require Import NativeResetProof NativeResetCorrespondence NativeRoundAdmission NativeAcquiredDomain NativePrepareCorrespondence.
Require Import NativeBudgetArithmetic NativeBudgetReset.
Import ListNotations.
Module NativeBudgetInputs.
Import NativeSchedule NativeBudgetArithmetic.
Open Scope Z_scope.
Lemma seeds_count : forall bytes line seeds info state,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  (length seeds<=134217727)%nat /\ length (rows state)=length seeds.
Proof.
  intros bytes line seeds info state Admission History.
  pose proof (NativeActiveInputs.history_length bytes line seeds info state Admission History) as Count.
  pose proof (f_equal (@length Seed) (NativeSourceHistory.history_seeds line seeds info state History)) as Length.
  rewrite map_length in Length. split; lia.
Qed.
Lemma fields_good : forall grow xs ys,
  Forall2 NativePreparedFields.Fields xs ys -> Forall NativeMainBounds.Bounds xs ->
  NativeProducerSums.Valid grow xs -> Forall Good ys.
Proof.
  intros grow xs ys Fields; induction Fields as [|x y xs ys Field Tail IH]; intros Bounds Valid; [constructor|].
  inversion Bounds as [|head rest HeadBounds TailBounds]; subst.
  unfold NativeProducerSums.Valid in Valid. inversion Valid as [|head rest HeadValid TailValid]; subst.
  destruct Field as [Seed [Frozen [Main Flags]]]. constructor; [|apply IH; assumption].
  split; [rewrite Seed; exact (proj1 HeadBounds)|].
  rewrite Main. unfold NativeResetProof.currentSize. destruct (frozen x) eqn:F.
  - destruct HeadBounds as [Range Size]. unfold NativeMainBounds.SeedRange,NativeMainBounds.MainRange in *.
    unfold EntryAcquisition.Acquired32; lia.
  - exact (proj1 (proj2 (HeadValid ltac:(assumption || reflexivity)))).
Qed.
Lemma prepared_good : forall bytes line seeds info state p,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.prepare (NativeEntry.config line seeds) state=Some p -> Forall Good (NativePass.preparedRows p).
Proof.
  intros bytes line seeds info state p Admission History Prepared.
  eapply fields_good; [eapply NativePreparedFields.prepare_fields; exact Prepared| |].
  - exact (NativeMainBounds.history_bounds bytes line seeds info state Admission History).
  - exact (NativeActiveInputs.history_valid bytes line seeds info state Admission History).
Qed.
Lemma producer_shared : forall bytes line seeds info state p produced,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.prepare (NativeEntry.config line seeds) state=Some p -> NativePass.producer p=Some produced ->
  Forall NativeProducerRows.Shared (NativeProducer.producedRows produced) /\
  NativeFloat.finite (NativeProducer.weightSum produced)=true.
Proof.
  intros bytes line seeds info state p produced Admission History Prepared Produced.
  rewrite (NativePrepareProducer.producer_source _ _ _ _ Prepared Produced).
  pose proof (NativeActiveInputs.history_valid bytes line seeds info state Admission History) as Valid.
  pose proof (NativeActiveInputs.history_length bytes line seeds info state Admission History) as Length.
  pose proof (proj1 (NativeStructuralHistory.history_count_fresh line seeds info state History)) as Counted.
  unfold NativeStructuralHistory.Counted in Counted.
  pose proof (NativeProducerReset.valid_reset _ _ O (NativePass.spaceAvailable (NativeEntry.config line seeds)) Valid) as ResetValid.
  pose proof (NativeProducerRun.run_correspondence (NativeEntry.seedsMode line seeds)
    (NativePass.resetRows (NativePass.reset O (NativePass.spaceAvailable (NativeEntry.config line seeds)) (rows state)))
    (frozenCount state) ResetValid
    ltac:(rewrite NativeProducerReset.length_reset; unfold WeightTarget.countLimit; entry_numerals; lia)
    ltac:(rewrite NativeProducerReset.count_reset; exact Counted)) as P.
  cbn zeta in P. destruct P as [_ [Finite [_ [_ [_ [_ Shares]]]]]]. split; assumption.
Qed.
Lemma prepared_domain : forall bytes line seeds info state p,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.prepare (NativeEntry.config line seeds) state=Some p -> ReverseTarget.FreeDomain (NativePass.entryFree p).
Proof.
  intros bytes line seeds info state p Admission History Prepared.
  destruct (NativePrepareCorrespondence.prepare_matches bytes line seeds info state p Admission History Prepared)
    as [_ [Free _]]. rewrite Free.
  exact (proj1 (proj2 (proj2 (proj2 (NativeAcquiredDomain.source_domain bytes line seeds info state Admission History))))).
Qed.
Lemma acquisition : forall bytes line seeds info state p,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.prepare (NativeEntry.config line seeds) state=Some p ->
  Forall NativeSchedule.FitsEvent (NativePass.resetEvents (NativePass.acquisition p)) /\
  Fits64 (NativePass.spaceAvailable (NativeEntry.config line seeds)) /\
  Fits64 (EntryAcquisition.inner line) /\ Fits64 (EntryAcquisition.gap line) /\
  Fits64 (EntryAcquisition.mbpTotal line) /\ Fits64 (SignHistory.fixed line).
Proof.
  intros bytes line seeds info state p Admission History Prepared.
  pose proof (proj1 Admission) as Line.
  pose proof (NativeRoundAdmission.round_admitted bytes line seeds info state Admission History) as Round.
  set (actual := SignHistory.asRound (NativeEntry.seedsMode line seeds)
    (projectedState (NativeEntry.seedsMode line seeds) state)) in *.
  destruct (entry_acquisition_target bytes line (NativeEntry.seedsMode line seeds) actual Line Round)
    as [MBPPrefix [FixedBound [SpaceBound [MBPFit [FixedFit [SpaceFit [Prefixes Formula]]]]]]].
  assert (Used : EntryAcquisition.used actual=map NativeResetProof.currentSize (rows state)).
  { unfold actual,SignHistory.asRound,projectedState; cbn [SignHistory.rows EntryAcquisition.used].
    rewrite map_map. apply map_ext. apply NativeResetCorrespondence.current_size. }
  pose proof (proj2 (entry_round_count bytes line (NativeEntry.seedsMode line seeds) actual Line Round)) as Values.
  rewrite Used in Values. apply Forall_map in Values.
  split.
  - rewrite (NativeBudgetReset.acquisition_record _ _ _ Prepared).
    apply NativeBudgetReset.reset_events.
    + eapply Forall_impl; [|exact Values]. intros r V; apply acquired_fits; exact V.
    + intro k. rewrite <- Used. exact (proj2 (Prefixes k)).
  - split; [exact SpaceFit|].
    destruct Line as [_ [_ [_ [_ [Inner Gap]]]]].
    split; [apply acquired_fits; exact Inner|]. split; [apply acquired_fits; exact Gap|].
    split; assumption.
Qed.
Print Assumptions seeds_count.
Print Assumptions fields_good.
Print Assumptions prepared_good.
Print Assumptions producer_shared.
Print Assumptions prepared_domain.
Print Assumptions acquisition.
End NativeBudgetInputs.
