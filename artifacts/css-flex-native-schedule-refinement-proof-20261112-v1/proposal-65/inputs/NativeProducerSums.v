Require Import Reals ZArith List Bool Lia Psatz.
Require Import InputTarget WeightTarget ShareTarget PrefixTarget BranchTarget BranchProof EntryModel SignModel.
Require Import NativeFloatModel NativeState NativeProducerModel NativeWeightProof NativeItemProjection NativeFactorProof NativeSumProof.
Import ListNotations.
Module NativeProducerSums.
Import NativeSchedule.
Open Scope R_scope.
Definition Valid (grow : bool) (rs : list Row) :=
  Forall (fun r => frozen r = false -> InputTarget.InputValid (NativeWeightProof.payload grow r)) rs.
Lemma loop_sums : forall rs grow left index sum factors largest count processed,
  Valid grow rs -> (0 <= processed)%Z ->
  (processed + Z.of_nat (length rs) <= countLimit)%Z ->
  NativeFloat.finite sum = true -> NativeFloat.finite factors = true ->
  0 <= NativeFloat.value sum <= IZR processed*stride ->
  0 <= NativeFloat.value factors <= IZR processed*stride ->
  let out := NativeProducer.loop grow left index sum factors largest count rs in
  NativeFloat.finite (NativeProducer.weightSum out) = true /\
  NativeFloat.finite (NativeProducer.factorSum out) = true /\
  NativeFloat.value (NativeProducer.weightSum out) = PrefixTarget.total
    (PrefixTarget.produce left (NativeFloat.value sum) (map (NativeItemProjection.item grow) rs)) /\
  NativeFloat.value (NativeProducer.factorSum out) = EntryAcquisition.factorTotal
    (EntryAcquisition.factorLoop left (NativeFloat.value factors) (map (NativeItemProjection.item grow) rs)).
Proof.
  induction rs as [|r tail IH]; intros grow left index sum factors largest count processed
    ValidRows Processed Count SumFinite FactorsFinite SumBound FactorBound.
  - destruct left; cbn; repeat split; assumption || reflexivity.
  - destruct left as [|k]; [cbn; repeat split; assumption || reflexivity|].
    inversion ValidRows as [|head rest Head Tail]; subst.
    destruct (frozen r) eqn:Frozen.
    + specialize (IH grow (S k) (S index) sum factors largest count processed Tail Processed
        ltac:(cbn [length] in Count; lia) SumFinite FactorsFinite SumBound FactorBound).
      cbn [NativeProducer.loop]; rewrite Frozen; cbn.
      cbn [map PrefixTarget.produce EntryAcquisition.factorLoop NativeItemProjection.item SignHistory.asItem projectedRow].
      rewrite Frozen; cbn. exact IH.
    + specialize (Head eq_refl).
      destruct (NativeItemProjection.source_weight grow r Head) as [WeightFinite WeightValue].
      pose proof (proj1 (BranchProof.source_finite_target _ Head)) as WeightBound.
      change (WeightValid (BranchTarget.sourceWeight (PrefixTarget.payload (NativeItemProjection.item grow r)))) in WeightBound.
      rewrite <- WeightValue in WeightBound.
      destruct (NativeFactorProof.factor_weight_bound grow r Head) as [FactorFinite [FactorValue FactorWeight]].
      assert (Domain : (0 <= processed <= countLimit)%Z) by (cbn [length] in Count; lia).
      destruct (NativeSumProof.add_stride sum (weight grow r) processed SumFinite WeightFinite
        Domain SumBound WeightBound) as [NextSumFinite [NextSumValue NextSumBound]].
      destruct (NativeSumProof.add_stride factors (NativeFloat.promote (factor grow (seed r))) processed
        FactorsFinite FactorFinite Domain FactorBound FactorWeight)
        as [NextFactorFinite [NextFactorValue NextFactorBound]].
      set (w := weight grow r) in *.
      set (nextSum := NativeFloat.add sum w) in *.
      set (nextFactors := NativeFloat.add factors (NativeFloat.promote (factor grow (seed r)))) in *.
      set (bigger := NativeFloat.less largest w).
      set (nextLargest := if bigger then w else largest).
      set (nextCount := if bigger then 1%nat else if NativeFloat.equal w largest then S count else count).
      specialize (IH grow k (S index) nextSum nextFactors nextLargest nextCount (processed+1)%Z
        Tail ltac:(lia) ltac:(cbn [length] in Count; lia)
        NextSumFinite NextFactorFinite NextSumBound NextFactorBound).
      destruct IH as [SFinite [FFinite [SValue FValue]]].
      rewrite NextSumValue, WeightValue in SValue.
      rewrite NextFactorValue, FactorValue in FValue.
      cbn [NativeProducer.loop]; rewrite Frozen; cbn.
      cbn [map PrefixTarget.produce EntryAcquisition.factorLoop NativeItemProjection.item SignHistory.asItem projectedRow].
      rewrite Frozen; cbn.
      split; [exact SFinite|]. split; [exact FFinite|]. split; [exact SValue|exact FValue].
Qed.
Print Assumptions loop_sums.
End NativeProducerSums.
