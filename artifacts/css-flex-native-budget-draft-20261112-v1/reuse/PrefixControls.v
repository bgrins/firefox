Require Import Reals ZArith List Psatz Gappa.Gappa_library Flocq.IEEE754.Binary.
Require Import WeightTarget ShareTarget Share Target ConversionTarget DistributionTarget Distribution InputTarget InputProof BranchTarget BranchProof PrefixTarget PrefixProof.
Import ListNotations.
Open Scope R_scope.

Definition activeOne : Item :=
  {| itemId := 7; payload := growOne; frozen := false; stored := -3 |}.
Definition frozenBad : Item :=
  {| itemId := 7;
     payload := {| factor := Binary.B754_infinity 24 128 false;
                   base := -1099511627776; growing := false |};
     frozen := true; stored := 42 |}.
Definition exampleRows := [frozenBad; activeOne; activeOne; frozenBad].
Lemma active_one_valid : ItemValid activeOne.
Proof.
  intro H. unfold InputValid. cbn [activeOne payload growOne factor base growing].
  split; [exact one_input|]. split; [lia|discriminate].
Qed.
Lemma frozen_bad_valid : ItemValid frozenBad.
Proof. intro H. discriminate H. Qed.
Theorem example_admitted : Admitted exampleRows.
Proof.
  split; [cbn; unfold countLimit; lia|].
  constructor; [exact frozen_bad_valid|].
  constructor; [exact active_one_valid|].
  constructor; [exact active_one_valid|].
  constructor; [exact frozen_bad_valid|constructor].
Qed.
Theorem frozen_payload_not_valid : ~ InputValid (payload frozenBad).
Proof. intros [[Hfinite Hnonnegative] Hrest]. discriminate Hfinite. Qed.
Theorem duplicate_ids : map itemId exampleRows = [7%nat;7%nat;7%nat;7%nat].
Proof. reflexivity. Qed.
Theorem actual_stop_after_last_active : visited (run exampleRows) = 3%nat.
Proof. reflexivity. Qed.
Theorem frozen_records_preserved :
  nth_error (rows (run exampleRows)) 0 = Some frozenBad /\
  nth_error (rows (run exampleRows)) 3 = Some frozenBad.
Proof.
  split; apply (proj2 (preservation_target exampleRows)); reflexivity.
Qed.
Lemma source_one : sourceWeight (payload activeOne) = 1.
Proof. change (value32 one32 = 1). exact one_value. Qed.
Lemma initial_prefix_one : prefixShare [frozenBad] activeOne = 1.
Proof.
  unfold prefixShare. cbn [activeWeights app frozenBad activeOne frozen].
  change (storedShare [sourceWeight (payload activeOne)] (sourceWeight (payload activeOne)) = 1).
  rewrite source_one. exact Distribution.singleton_share.
Qed.
Theorem actual_first_share : nth_error (rows (run exampleRows)) 1 = Some (setStored activeOne 1).
Proof.
  change (nth_error (rows (run ([frozenBad] ++ activeOne :: [activeOne; frozenBad])))
    (length [frozenBad]) = Some (setStored activeOne 1)).
  rewrite prefix_target by reflexivity. rewrite initial_prefix_one. reflexivity.
Qed.
Lemma rn_two : WeightTarget.rn 2 = 2.
Proof.
  unfold WeightTarget.rn. apply (@Generic_fmt.round_generic radix2 (FLT.FLT_exp (-1074) 53) rndNE Share.nearest_valid).
  change (Generic_fmt.generic_format radix2 (FLT.FLT_exp (-1074) 53) (Raux.bpow radix2 1)).
  apply Generic_fmt.generic_format_bpow. vm_compute. discriminate.
Qed.
Lemma rn_half : WeightTarget.rn (/2) = /2.
Proof.
  unfold WeightTarget.rn. apply (@Generic_fmt.round_generic radix2 (FLT.FLT_exp (-1074) 53) rndNE Share.nearest_valid).
  change (Generic_fmt.generic_format radix2 (FLT.FLT_exp (-1074) 53) (Raux.bpow radix2 (-1))).
  apply Generic_fmt.generic_format_bpow. vm_compute. discriminate.
Qed.
Lemma final_total_half : storedShare [1;1] 1 = /2.
Proof.
  unfold storedShare. destruct (Req_EM_T 1 0); [lra|].
  unfold ShareTarget.share, accumulate. cbn [fold_left].
  rewrite Rplus_0_l, Share.rn_one. replace (1+1) with 2 by ring.
  rewrite rn_two. replace (1/2) with (/2) by field. exact rn_half.
Qed.
Theorem final_total_substitution_false :
  prefixShare [frozenBad] activeOne <> storedShare [1;1] 1.
Proof. rewrite initial_prefix_one, final_total_half. intro H. lra. Qed.
Theorem skipping_first_active_false :
  nth_error (rows (run exampleRows)) 1 <> Some activeOne.
Proof.
  rewrite actual_first_share. intro H.
  apply (f_equal (fun x => match x with Some y => stored y | None => 0 end)) in H.
  cbn [setStored activeOne stored] in H. lra.
Qed.

Print Assumptions example_admitted.
Print Assumptions frozen_payload_not_valid.
Print Assumptions duplicate_ids.
Print Assumptions actual_stop_after_last_active.
Print Assumptions frozen_records_preserved.
Print Assumptions actual_first_share.
Print Assumptions final_total_substitution_false.
Print Assumptions skipping_first_active_false.
