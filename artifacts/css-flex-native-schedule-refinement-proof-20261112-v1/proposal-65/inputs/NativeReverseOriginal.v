Require Import Reals ZArith List Bool Lia.
Require Import WeightTarget EntryModel EntryComposition EntryNumerals PrefixTarget ReverseTarget SignModel.
Require Import NativeFloatModel NativeState NativePassModel NativeEntryModel NativeReverseModel NativeProducerModel NativeRefinementSpec.
Require Import NativeStepShape NativeActiveInputs NativeStructuralHistory NativeProducerReset NativePrepareProducer NativeItemProjection.
Require Import NativePrepareCorrespondence NativeAcquiredDomain NativeReverseRun.
Import ListNotations.
Module NativeReverseOriginal.
Import NativeSchedule.
Lemma reverse_target : NativeRefinementTarget.ReverseTarget.
Proof.
  intros bytes line seeds info state result Admission History Step.
  cbn zeta.
  unfold NativePass.step in Step.
  destruct (NativePass.prepare (NativeEntry.config line seeds) state) as [p|] eqn:Prepared; [|discriminate].
  destruct (NativePrepareCorrespondence.prepare_matches bytes line seeds info state p Admission History Prepared)
    as [Capture [Entry Branch]].
  destruct (NativePass.distributes p) eqn:Distributes.
  - destruct (NativePass.producer p) as [prod|] eqn:Producer; [|discriminate].
    destruct (NativeReverse.run (NativePass.growing (NativeEntry.config line seeds)) prod (frozenCount state)
      (NativePass.entryFree p) (reports state)) as [reversed|] eqn:Reverse; [|discriminate].
    inversion Step; subst result. cbn [NativePass.reverse NativePass.finish].
    assert (Enters : EntryAcquisition.enters (SignHistory.prepared line (NativeEntry.seedsMode line seeds)
      (projectedState (NativeEntry.seedsMode line seeds) state)) = true).
    { exact (eq_sym Branch). }
    pose proof (entry_enters_nonzero line (saved (original state))
      (SignHistory.asRound (NativeEntry.seedsMode line seeds) (projectedState (NativeEntry.seedsMode line seeds) state)) Enters) as Nonzero.
    pose proof (NativeActiveInputs.history_valid bytes line seeds info state Admission History) as Valid.
    pose proof (NativeActiveInputs.history_length bytes line seeds info state Admission History) as Length.
    pose proof (proj1 (NativeStructuralHistory.history_count_fresh line seeds info state History)) as Counted.
    change (frozenCount state = length (filter frozen (rows state))) in Counted.
    assert (Count : (Z.of_nat (length (rows state)) <= countLimit)%Z).
    { unfold countLimit. entry_numerals. lia. }
    pose proof (NativeProducerReset.valid_reset (NativeEntry.seedsMode line seeds) (rows state) O
      (EntryAcquisition.initialSpace line) Valid) as ResetValid.
    pose proof (NativeProducerReset.count_reset (rows state) O (EntryAcquisition.initialSpace line)) as ResetCount.
    pose proof (NativeProducerReset.length_reset (rows state) O (EntryAcquisition.initialSpace line)) as ResetLength.
    assert (Items : map (NativeItemProjection.item (NativeEntry.seedsMode line seeds))
      (NativePass.resetRows (NativePass.reset O (EntryAcquisition.initialSpace line) (rows state))) =
      SignHistory.itemRows (NativeEntry.seedsMode line seeds) (projectedState (NativeEntry.seedsMode line seeds) state)).
    { rewrite NativeItemProjection.reset_items.
      unfold SignHistory.itemRows,projectedState. cbn [SignHistory.rows]. rewrite map_map. reflexivity. }
    destruct (NativeAcquiredDomain.source_domain bytes line seeds info state Admission History)
      as [_ [_ [_ [Domain _]]]].
    destruct (NativeReverseRun.run_matches (NativeEntry.seedsMode line seeds)
      (NativePass.resetRows (NativePass.reset O (EntryAcquisition.initialSpace line) (rows state)))
      (frozenCount state) (NativePass.entryFree p) (reports state) ResetValid
      ltac:(rewrite ResetLength; exact Count) ltac:(rewrite ResetCount; exact Counted)
      ltac:(rewrite Entry; exact Domain) ltac:(rewrite Items; exact Nonzero))
      as [out [Run [Left [Events Free]]]].
    pose proof (NativePrepareProducer.producer_source (NativeEntry.config line seeds) state p prod Prepared Producer) as Source.
    rewrite Source in Reverse. change (NativeReverse.run (NativeEntry.seedsMode line seeds)
      (NativeProducer.run (NativeEntry.seedsMode line seeds)
        (NativePass.resetRows (NativePass.reset O (EntryAcquisition.initialSpace line) (rows state)))
        (frozenCount state)) (frozenCount state) (NativePass.entryFree p) (reports state) = Some reversed) in Reverse.
    rewrite Run in Reverse. inversion Reverse; subst out.
    rewrite Items,Entry in Events,Free.
    unfold SignHistory.distributed,EntryAcquisition.execute.
    change (EntryAcquisition.enters (EntryAcquisition.prepare line (SignHistory.saved (projectedState (NativeEntry.seedsMode line seeds) state))
      (SignHistory.asRound (NativeEntry.seedsMode line seeds) (projectedState (NativeEntry.seedsMode line seeds) state)))) with
      (EntryAcquisition.enters (SignHistory.prepared line (NativeEntry.seedsMode line seeds)
        (projectedState (NativeEntry.seedsMode line seeds) state))).
    rewrite Enters. split; [exact Left|]. split; assumption.
  - inversion Step; subst result. cbn [NativePass.reverse NativePass.finish].
    unfold SignHistory.distributed,EntryAcquisition.execute.
    change (EntryAcquisition.enters (EntryAcquisition.prepare line (SignHistory.saved (projectedState (NativeEntry.seedsMode line seeds) state))
      (SignHistory.asRound (NativeEntry.seedsMode line seeds) (projectedState (NativeEntry.seedsMode line seeds) state)))) with
      (EntryAcquisition.enters (SignHistory.prepared line (NativeEntry.seedsMode line seeds)
        (projectedState (NativeEntry.seedsMode line seeds) state))).
    rewrite <- Branch. reflexivity.
Qed.
Print Assumptions reverse_target.
End NativeReverseOriginal.
