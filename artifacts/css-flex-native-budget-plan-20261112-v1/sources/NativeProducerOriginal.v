Require Import Reals ZArith List Bool Lia.
Require Import WeightTarget PrefixTarget EntryModel EntryNumerals SignModel.
Require Import NativeFloatModel NativeState NativePassModel NativeEntryModel NativeProducerModel NativeRefinementSpec.
Require Import NativeProducerSums NativeProducerRun NativeProducerReset NativePrepareFinite NativePrepareProducer.
Require Import NativeActiveInputs NativeStructuralHistory NativeItemProjection.
Import ListNotations.
Module NativeProducerOriginal.
Import NativeSchedule.
Lemma producer_target : NativeRefinementTarget.ProducerTarget.
Proof.
  intros bytes line seeds info state p Admission History Prepared.
  pose proof (NativeActiveInputs.history_valid bytes line seeds info state Admission History) as Valid.
  pose proof (NativeActiveInputs.history_length bytes line seeds info state Admission History) as Length.
  pose proof (proj1 (NativeStructuralHistory.history_count_fresh line seeds info state History)) as Counted.
  change (frozenCount state = length (filter frozen (rows state))) in Counted.
  assert (Count : (Z.of_nat (length (rows state)) <= countLimit)%Z).
  { unfold countLimit. entry_numerals. lia. }
  destruct (NativePrepareFinite.prepare_finite (NativeEntry.config line seeds) state p
    Valid Count Counted Prepared) as [Finite Branch].
  split; [exact Finite|].
  destruct (NativePass.producer p) as [produced|] eqn:Produced; [|exact Branch].
  pose proof (NativePrepareProducer.producer_source (NativeEntry.config line seeds) state p produced
    Prepared Produced) as Source.
  subst produced.
  pose proof (NativeProducerReset.valid_reset (NativeEntry.seedsMode line seeds) (rows state) O
    (NativePass.spaceAvailable (NativeEntry.config line seeds)) Valid) as ResetValid.
  pose proof (NativeProducerReset.length_reset (rows state) O
    (NativePass.spaceAvailable (NativeEntry.config line seeds))) as ResetLength.
  pose proof (NativeProducerReset.count_reset (rows state) O
    (NativePass.spaceAvailable (NativeEntry.config line seeds))) as ResetCount.
  pose proof (NativeProducerRun.run_correspondence (NativeEntry.seedsMode line seeds)
    (NativePass.resetRows (NativePass.reset O (NativePass.spaceAvailable (NativeEntry.config line seeds)) (rows state)))
    (frozenCount state) ResetValid ltac:(rewrite ResetLength; exact Count)
    ltac:(rewrite ResetCount; exact Counted)) as Output.
  cbn zeta in Output.
  rewrite NativeItemProjection.reset_items in Output.
  destruct Output as [Remaining [WeightFinite [FactorFinite [Rows [Weight [Factors Shares]]]]]].
  assert (Items : map (NativeItemProjection.item (NativeEntry.seedsMode line seeds)) (rows state) =
    SignHistory.itemRows (NativeEntry.seedsMode line seeds)
      (projectedState (NativeEntry.seedsMode line seeds) state)).
  { unfold SignHistory.itemRows, projectedState. cbn [SignHistory.rows].
    rewrite map_map. reflexivity. }
  rewrite Items in Rows,Weight,Factors.
  repeat split; assumption.
Qed.
Print Assumptions producer_target.
End NativeProducerOriginal.
