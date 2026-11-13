Require Import Reals ZArith List Bool Lia.
Require Import InputTarget PrefixTarget BranchTarget BranchProof SignModel.
Require Import NativeFloatModel NativeState NativePassModel NativeResetProof NativeWeightProof.
Import ListNotations.
Module NativeItemProjection.
Import NativeSchedule.
Definition item (grow : bool) (r : Row) := SignHistory.asItem grow (projectedRow grow r).
Lemma payload_item : forall grow r, PrefixTarget.payload (item grow r) = NativeWeightProof.payload grow r.
Proof. reflexivity. Qed.
Lemma replace_share : forall grow r s,
  item grow (replaceShare r s) = PrefixTarget.setStored (item grow r) (NativeFloat.value s).
Proof. reflexivity. Qed.
Lemma reset_item : forall grow r,
  item grow (NativeResetProof.resetRow r) = item grow r.
Proof. intros; unfold NativeResetProof.resetRow; destruct (frozen r); reflexivity. Qed.
Lemma reset_items : forall grow rs index free,
  map (item grow) (NativePass.resetRows (NativePass.reset index free rs)) = map (item grow) rs.
Proof.
  intros; rewrite NativeResetProof.reset_rows, map_map. apply map_ext. apply reset_item.
Qed.
Lemma active_items : forall grow rs, PrefixTarget.activeCount (map (item grow) rs) = active rs.
Proof.
  intros grow rs; induction rs as [|r tail IH]; [reflexivity|].
  unfold PrefixTarget.activeCount in *. cbn [map PrefixTarget.activeWeights].
  change (length (if frozen r then PrefixTarget.activeWeights (map (item grow) tail)
    else BranchTarget.sourceWeight (PrefixTarget.payload (item grow r)) ::
      PrefixTarget.activeWeights (map (item grow) tail)) = active (r::tail)).
  unfold active in *; cbn; destruct (frozen r); cbn; congruence.
Qed.
Lemma source_weight : forall grow r,
  InputTarget.InputValid (PrefixTarget.payload (item grow r)) ->
  NativeFloat.finite (weight grow r) = true /\
  NativeFloat.value (weight grow r) = BranchTarget.sourceWeight (PrefixTarget.payload (item grow r)).
Proof.
  intros grow r H. rewrite BranchProof.weight_equivalence_target by exact H.
  apply NativeWeightProof.weight_correspondence; exact H.
Qed.
Print Assumptions payload_item.
Print Assumptions replace_share.
Print Assumptions reset_item.
Print Assumptions reset_items.
Print Assumptions active_items.
Print Assumptions source_weight.
End NativeItemProjection.
