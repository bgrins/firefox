Require Import Reals ZArith List Bool Lia Psatz.
Require Import InputTarget WeightTarget PrefixTarget EntryModel.
Require Import NativeFloatModel NativeState NativeProducerModel NativeValues NativeEarlyProof.
Require Import NativeItemProjection NativeProducerStructure NativeProducerSums NativeProducerRows.
Import ListNotations.
Module NativeProducerRun.
Import NativeSchedule.
Open Scope R_scope.
Lemma run_correspondence : forall grow rs count,
  NativeProducerSums.Valid grow rs ->
  (Z.of_nat (length rs) <= countLimit)%Z ->
  count = length (filter frozen rs) ->
  let out := NativeProducer.run grow rs count in
  NativeProducer.remaining out = O /\
  NativeFloat.finite (NativeProducer.weightSum out) = true /\
  NativeFloat.finite (NativeProducer.factorSum out) = true /\
  map (NativeItemProjection.item grow) (NativeProducer.producedRows out) =
    PrefixTarget.rows (PrefixTarget.run (map (NativeItemProjection.item grow) rs)) /\
  NativeFloat.value (NativeProducer.weightSum out) =
    PrefixTarget.total (PrefixTarget.run (map (NativeItemProjection.item grow) rs)) /\
  NativeFloat.value (NativeProducer.factorSum out) =
    EntryAcquisition.factorTotal (EntryAcquisition.factorRun (map (NativeItemProjection.item grow) rs)) /\
  Forall NativeProducerRows.Shared (NativeProducer.producedRows out).
Proof.
  intros grow rs count Valid Count Counted.
  pose proof (NativeProducerStructure.run_remaining grow rs count Counted) as Remaining.
  assert (Active : (length rs-count)%nat = active rs).
  { subst count. pose proof (NativeEarlyProof.count_partition rs). lia. }
  pose proof (NativeProducerSums.loop_sums rs grow (active rs) O NativeFloat.zero NativeFloat.zero
    NativeFloat.zero O 0 Valid ltac:(lia) ltac:(lia) NativeValues.zero_finite NativeValues.zero_finite
    ltac:(rewrite NativeValues.zero_value; cbn [IZR]; lra)
    ltac:(rewrite NativeValues.zero_value; cbn [IZR]; lra)) as Sums.
  pose proof (NativeProducerRows.loop_rows rs grow O NativeFloat.zero NativeFloat.zero NativeFloat.zero O 0
    Valid ltac:(lia) ltac:(lia) NativeValues.zero_finite
    ltac:(rewrite NativeValues.zero_value; cbn [IZR]; lra)) as Stored.
  cbn zeta in Sums,Stored. rewrite NativeValues.zero_value in Sums,Stored.
  destruct Sums as [SumFinite [FactorFinite [SumValue FactorValue]]].
  destruct Stored as [Rows Shares].
  split; [exact Remaining|]. unfold NativeProducer.run. rewrite Active.
  unfold PrefixTarget.run,EntryAcquisition.factorRun. rewrite NativeItemProjection.active_items.
  repeat split; assumption.
Qed.
Print Assumptions run_correspondence.
End NativeProducerRun.
