Require Import Reals ZArith List Bool Lia Psatz.
Require Import InputTarget WeightTarget ShareTarget PrefixTarget BranchTarget BranchProof SignModel.
Require Import NativeFloatModel NativeState NativeProducerModel NativeWeightProof NativeItemProjection NativeSumProof NativeStoredShare NativeEarlyProof.
Import ListNotations.
Module NativeProducerRows.
Import NativeSchedule.
Open Scope R_scope.
Definition Shared (r : Row) := frozen r = false ->
  NativeFloat.finite (share r) = true /\ 0 <= NativeFloat.value (share r) <= 1.
Lemma frozen_shared : forall rs, active rs = O -> Forall Shared rs.
Proof.
  intros rs H. apply NativeEarlyProof.active_zero in H.
  induction H.
  - constructor.
  - constructor; [unfold Shared; intro F; congruence|assumption].
Qed.
Lemma loop_rows : forall rs grow index sum factors largest count processed,
  Forall (fun r => frozen r = false -> InputTarget.InputValid (NativeWeightProof.payload grow r)) rs ->
  (0 <= processed)%Z -> (processed + Z.of_nat (length rs) <= countLimit)%Z ->
  NativeFloat.finite sum = true -> 0 <= NativeFloat.value sum <= IZR processed*stride ->
  let out := NativeProducer.loop grow (active rs) index sum factors largest count rs in
  map (NativeItemProjection.item grow) (NativeProducer.producedRows out) =
    PrefixTarget.rows (PrefixTarget.produce (active rs) (NativeFloat.value sum) (map (NativeItemProjection.item grow) rs)) /\
  Forall Shared (NativeProducer.producedRows out).
Proof.
  induction rs as [|r tail IH]; intros grow index sum factors largest count processed
    Valid Processed Count SumFinite SumBound.
  - cbn; split; [reflexivity|constructor].
  - inversion Valid as [|head rest Head Tail]; subst.
    destruct (frozen r) eqn:Frozen.
    + assert (Active : active (r::tail) = active tail) by (unfold active; cbn; rewrite Frozen; reflexivity).
      rewrite Active. destruct (active tail) as [|k] eqn:Left.
      * cbn. split; [reflexivity|]. apply frozen_shared. rewrite Active; assumption || reflexivity.
      * specialize (IH grow (S index) sum factors largest count processed Tail Processed
          ltac:(cbn [length] in Count; lia) SumFinite SumBound).
        cbn [NativeProducer.loop]; rewrite Frozen; cbn.
        cbn [map PrefixTarget.produce NativeItemProjection.item SignHistory.asItem projectedRow].
        rewrite Frozen; cbn. destruct IH as [Rows Shares].
        split; [f_equal; exact Rows|]. constructor; [unfold Shared; intro F; congruence|exact Shares].
    + assert (Active : active (r::tail) = S (active tail)) by (unfold active; cbn; rewrite Frozen; reflexivity).
      specialize (Head eq_refl).
      destruct (NativeItemProjection.source_weight grow r Head) as [WeightFinite WeightValue].
      pose proof (BranchProof.source_finite_target _ Head) as WeightFacts.
      change (FiniteWeight (BranchTarget.sourceWeight (PrefixTarget.payload (NativeItemProjection.item grow r)))) in WeightFacts.
      rewrite <- WeightValue in WeightFacts.
      assert (Domain : (0 <= processed <= countLimit)%Z) by (cbn [length] in Count; lia).
      destruct (NativeSumProof.add_stride sum (weight grow r) processed SumFinite WeightFinite
        Domain SumBound (proj1 WeightFacts)) as [NextFinite [NextValue NextBound]].
      destruct (NativeStoredShare.store_correspondence (weight grow r) (NativeFloat.value sum)
        (NativeFloat.add sum (weight grow r)) WeightFinite NextFinite (proj1 SumBound) WeightFacts NextValue)
        as [ShareFinite [ShareValue ShareRange]].
      set (w := weight grow r) in *.
      set (nextSum := NativeFloat.add sum w) in *.
      set (nextFactors := NativeFloat.add factors (NativeFloat.promote (factor grow (seed r)))).
      set (bigger := NativeFloat.less largest w).
      set (nextLargest := if bigger then w else largest).
      set (nextCount := if bigger then 1%nat else if NativeFloat.equal w largest then S count else count).
      specialize (IH grow (S index) nextSum nextFactors nextLargest nextCount (processed+1)%Z
        Tail ltac:(lia) ltac:(cbn [length] in Count; lia) NextFinite NextBound).
      destruct IH as [Rows Shares]. rewrite NextValue, WeightValue in Rows.
      rewrite Active. cbn [NativeProducer.loop]; rewrite Frozen; cbn.
      fold w nextSum nextFactors nextLargest nextCount. rewrite NextFinite; cbn.
      cbn [map PrefixTarget.produce NativeItemProjection.item SignHistory.asItem projectedRow].
      rewrite Frozen; cbn. split.
      * f_equal.
        -- change (NativeItemProjection.item grow (replaceShare r (NativeStoredShare.store w nextSum)) =
             PrefixTarget.setStored (NativeItemProjection.item grow r)
               (PrefixTarget.shareAt (BranchTarget.sourceWeight (NativeWeightProof.payload grow r))
                 (WeightTarget.rn (NativeFloat.value sum + BranchTarget.sourceWeight (NativeWeightProof.payload grow r))))).
           rewrite NativeItemProjection.replace_share, ShareValue, NextValue, WeightValue. reflexivity.
        -- exact Rows.
      * constructor; [|exact Shares]. unfold Shared. intro F. split; assumption.
Qed.
Print Assumptions frozen_shared.
Print Assumptions loop_rows.
End NativeProducerRows.
