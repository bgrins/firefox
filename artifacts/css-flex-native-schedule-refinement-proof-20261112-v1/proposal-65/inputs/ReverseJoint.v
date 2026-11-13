Require Import Reals ZArith List Psatz Gappa.Gappa_library Flocq.IEEE754.Binary.
Require Import WeightTarget ShareTarget Share InputTarget InputProof BranchTarget PrefixTarget PrefixProof PrefixControls ReverseTarget ReverseStructure.
Import ListNotations.
Open Scope R_scope.

Definition three32 : Float32 := Binary.B754_finite 24 128 false 12582912 (-22) eq_refl.
Lemma three_value : value32 three32 = 3.
Proof. change ((12582912:R) * /4194304 = 3). field. Qed.
Definition activeThree : Item :=
  {| itemId := 7;
     payload := {| factor := three32; base := -2147483648; growing := true |};
     frozen := false; stored := -8 |}.
Definition jointRows := [frozenBad; activeOne; activeThree; frozenBad].
Lemma three_valid : ItemValid activeThree.
Proof.
  intro H. unfold InputValid. cbn [activeThree payload factor base growing].
  split.
  - split; [reflexivity|rewrite three_value; lra].
  - split; [lia|discriminate].
Qed.
Lemma source_three : sourceWeight (payload activeThree) = 3.
Proof. change (value32 three32 = 3). exact three_value. Qed.
Lemma joint_admitted : Admitted jointRows.
Proof.
  split; [cbn; unfold countLimit; lia|].
  constructor; [exact frozen_bad_valid|]. constructor; [exact active_one_valid|].
  constructor; [exact three_valid|]. constructor; [exact frozen_bad_valid|constructor].
Qed.
Lemma joint_weights : activeWeights jointRows = [1;3].
Proof.
  change ([sourceWeight (payload activeOne); sourceWeight (payload activeThree)] = [1;3]).
  rewrite source_one, source_three. reflexivity.
Qed.
Lemma rn_four : WeightTarget.rn 4 = 4.
Proof.
  unfold WeightTarget.rn. apply (@Generic_fmt.round_generic radix2 (FLT.FLT_exp (-1074) 53) rndNE Share.nearest_valid).
  change (Generic_fmt.generic_format radix2 (FLT.FLT_exp (-1074) 53) (Raux.bpow radix2 2)).
  apply Generic_fmt.generic_format_bpow. vm_compute. discriminate.
Qed.
Lemma joint_sum : total (run jointRows) = 4.
Proof.
  rewrite sum_target, joint_weights. unfold accumulate. cbn [fold_left].
  rewrite Rplus_0_l, Share.rn_one. replace (1+3) with 4 by ring. exact rn_four.
Qed.
Lemma joint_event_count : forall free, length (events (reverseRun jointRows free)) = 2%nat.
Proof.
  intro free. rewrite (proj2 (proj2 (reverse_count_target jointRows free))). rewrite joint_sum.
  destruct (Req_EM_T 4 0); [lra|]. unfold activeCount. rewrite joint_weights. reflexivity.
Qed.
Theorem joint_uniform_growing :
  Forall (fun x => frozen x = false -> growing (payload x) = true) jointRows.
Proof.
  apply Forall_forall. intros x Hin Hactive.
  destruct Hin as [Hx|[Hx|[Hx|[Hx|[]]]]]; subst x;
    cbn [frozenBad activeOne activeThree frozen payload growOne growing] in *;
    try discriminate; reflexivity.
Qed.
Theorem reverse_joint_target : ReverseJointTarget.
Proof.
  exists jointRows. split; [exact joint_admitted|]. split; [exact joint_weights|].
  split; [reflexivity|]. split.
  - exists frozenBad. split; [left; reflexivity|]. split; [reflexivity|exact frozen_payload_not_valid].
  - split; [rewrite joint_sum; lra|]. split; apply joint_event_count.
Qed.

Print Assumptions joint_uniform_growing.
Print Assumptions reverse_joint_target.
