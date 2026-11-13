Require Import Reals ZArith List Bool Lia Psatz.
Require Import WeightTarget PrefixTarget ReverseTarget EntryModel EntryNumerals SignModel.
Require Import NativeFloatModel NativeState NativePassModel NativeEntryModel NativeProducerModel.
Require Import NativeActiveInputs NativeStructuralHistory NativeSourceHistory NativeProducerReset NativeProducerRun NativeItemProjection.
Require Import NativeAcquiredDomain NativeCompareDecisions NativeResetCorrespondence NativeScale.
Import ListNotations.
Module NativePrepareCorrespondence.
Import NativeSchedule.
Open Scope Z_scope.
Lemma prepare_matches : forall bytes line seeds info state p,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.prepare (NativeEntry.config line seeds) state = Some p ->
  saved (NativePass.captured p) = EntryAcquisition.originalAfter
    (SignHistory.prepared line (NativeEntry.seedsMode line seeds) (projectedState (NativeEntry.seedsMode line seeds) state)) /\
  NativePass.entryFree p = EntryAcquisition.entryFree
    (SignHistory.prepared line (NativeEntry.seedsMode line seeds) (projectedState (NativeEntry.seedsMode line seeds) state)) /\
  NativePass.distributes p = EntryAcquisition.enters
    (SignHistory.prepared line (NativeEntry.seedsMode line seeds) (projectedState (NativeEntry.seedsMode line seeds) state)).
Proof.
  intros bytes line seeds info state p Admission History Prepared.
  pose proof (NativeActiveInputs.history_valid bytes line seeds info state Admission History) as Valid.
  pose proof (NativeActiveInputs.history_length bytes line seeds info state Admission History) as Length.
  pose proof (proj1 (NativeStructuralHistory.history_count_fresh line seeds info state History)) as Counted.
  change (frozenCount state = length (filter frozen (rows state))) in Counted.
  assert (Count : Z.of_nat (length (rows state)) <= countLimit).
  { unfold countLimit. entry_numerals. lia. }
  set (grow := NativeEntry.seedsMode line seeds) in *.
  set (acquired := NativePass.reset O (EntryAcquisition.initialSpace line) (rows state)).
  set (free := NativePass.freeSpace acquired).
  set (produced := NativeProducer.run grow (NativePass.resetRows acquired) (frozenCount state)).
  set (xs := SignHistory.itemRows grow (projectedState grow state)).
  pose proof (NativeProducerReset.valid_reset grow (rows state) O (EntryAcquisition.initialSpace line) Valid) as ResetValid.
  pose proof (NativeProducerReset.length_reset (rows state) O (EntryAcquisition.initialSpace line)) as ResetLength.
  pose proof (NativeProducerReset.count_reset (rows state) O (EntryAcquisition.initialSpace line)) as ResetCount.
  fold acquired in ResetValid,ResetLength,ResetCount.
  pose proof (NativeProducerRun.run_correspondence grow (NativePass.resetRows acquired) (frozenCount state)
    ResetValid ltac:(rewrite ResetLength; exact Count) ltac:(rewrite ResetCount; exact Counted)) as Run.
  cbn zeta in Run. fold produced in Run.
  assert (Items : map (NativeItemProjection.item grow) (NativePass.resetRows acquired) = xs).
  { unfold acquired. rewrite NativeItemProjection.reset_items.
    unfold xs,SignHistory.itemRows,projectedState. cbn [SignHistory.rows]. rewrite map_map. reflexivity. }
  rewrite Items in Run. destruct Run as [_ [WeightFinite [FactorFinite [Rows [WeightValue [FactorValue Shares]]]]]].
  destruct (NativeAcquiredDomain.source_domain bytes line seeds info state Admission History)
    as [FreeDomain [SavedDomain [CaptureDomain [EntryDomain [Factors Remaining]]]]].
  fold grow xs in Factors.
  pose proof (NativeResetCorrespondence.free_correspondence line seeds state) as Free.
  change (free = EntryAcquisition.roundFree line (SignHistory.asRound grow (projectedState grow state))) in Free.
  assert (Captured : saved (match original state with None => Some free | Some z => Some z end) =
    EntryAcquisition.capture (saved (original state)) free).
  { apply NativeResetCorrespondence.capture_correspondence.
    exact (NativeSourceHistory.history_original line seeds info state History). }
  assert (CaptureFree : ReverseTarget.FreeDomain (EntryAcquisition.capture (saved (original state)) free)).
  { rewrite Free. exact CaptureDomain. }
  pose proof (NativeCompareDecisions.zero_test (NativeProducer.weightSum produced) WeightFinite) as WeightTest.
  rewrite WeightValue in WeightTest.
  pose proof (NativeCompareDecisions.one_test (NativeProducer.factorSum produced) FactorFinite) as FactorTest.
  rewrite FactorValue in FactorTest.
  unfold NativePass.prepare in Prepared.
  cbn [NativeEntry.config NativePass.spaceAvailable NativePass.growing] in Prepared.
  fold grow acquired free produced in Prepared.
  unfold SignHistory.prepared,EntryAcquisition.prepare.
  rewrite <- Free.
  change (SignHistory.saved (projectedState grow state)) with (saved (original state)).
  destruct (Z.eqb free 0) eqn:Zero.
  - apply Z.eqb_eq in Zero.
    destruct (Z.eq_dec free 0) as [Equal|Unequal]; [|contradiction].
    inversion Prepared; subst p; cbn; repeat split; reflexivity.
  - apply Z.eqb_neq in Zero.
    destruct (Z.eq_dec free 0) as [Equal|Unequal]; [contradiction|].
    rewrite WeightTest in Prepared.
    change (EntryAcquisition.items (SignHistory.asRound grow (projectedState grow state))) with xs.
    destruct (Req_EM_T (PrefixTarget.total (PrefixTarget.run xs)) 0%R) as [NoWeight|HasWeight].
    + inversion Prepared; subst p; cbn.
      rewrite Captured. repeat split; reflexivity.
    + rewrite FactorTest in Prepared.
      destruct (Rlt_dec (EntryAcquisition.factorTotal (EntryAcquisition.factorRun xs)) 1%R) as [Below|Above].
      * assert (Range : (0 <= NativeFloat.value (NativeProducer.factorSum produced) <= 1)%R).
        { rewrite FactorValue. lra. }
        pose proof (NativeScale.scale_correct
          (saved (match original state with None => Some free | Some z => Some z end))
          (NativeProducer.factorSum produced) ltac:(rewrite Captured; exact CaptureFree) FactorFinite Range) as Scale.
        rewrite Scale in Prepared. inversion Prepared; subst p.
        cbn [NativePass.captured NativePass.entryFree NativePass.distributes NativePass.branch
          EntryAcquisition.originalAfter EntryAcquisition.entryFree EntryAcquisition.enters EntryAcquisition.selectedBranch].
        rewrite Captured,FactorValue. rewrite ?WeightFinite.
        unfold EntryAcquisition.adjustAvailable. repeat split; reflexivity.
      * inversion Prepared; subst p.
        cbn [NativePass.captured NativePass.entryFree NativePass.distributes NativePass.branch
          EntryAcquisition.originalAfter EntryAcquisition.entryFree EntryAcquisition.enters EntryAcquisition.selectedBranch].
        rewrite Captured. rewrite ?WeightFinite. repeat split; reflexivity.
Qed.
Print Assumptions prepare_matches.
End NativePrepareCorrespondence.
