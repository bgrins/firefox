Require Import Reals ZArith List Psatz Gappa.Gappa_library.
Require Import WeightTarget ShareTarget Share ConversionTarget BranchTarget PrefixTarget PrefixProof PrefixControls ReverseTarget ReverseStructure ReverseJoint.
Import ListNotations.
Open Scope R_scope.

Theorem envelope_only_closure_false :
  ~ (forall free d, FreeDomain free -> EnvelopeZ free d -> Fits64 d -> FreeDomain (free-d)%Z).
Proof.
  intro H.
  assert (Hfree : FreeDomain 1152921504606846976) by (unfold FreeDomain; lia).
  assert (Henv : EnvelopeZ 1152921504606846976 (-1)).
  { unfold EnvelopeZ. rewrite Z.min_r, Z.max_l by lia. lia. }
  assert (Hfit : Fits64 (-1)) by (unfold Fits64; lia).
  specialize (H 1152921504606846976%Z (-1)%Z Hfree Henv Hfit).
  unfold FreeDomain in H. lia.
Qed.
Lemma single_sum : total (run [activeOne]) = 1.
Proof.
  rewrite sum_target. change (WeightTarget.rn (0+sourceWeight (payload activeOne)) = 1).
  rewrite source_one, Rplus_0_l. exact Share.rn_one.
Qed.
Lemma single_event_count : forall free, length (events (reverseRun [activeOne] free)) = 1%nat.
Proof.
  intro free. rewrite (proj2 (proj2 (reverse_count_target [activeOne] free))). rewrite single_sum.
  destruct (Req_EM_T 1 0); [lra|reflexivity].
Qed.
Theorem too_small_count_loses_event : forall free,
  events (reverseLoop 0 free (rev (positioned (rows (run [activeOne]))))) <>
  events (reverseRun [activeOne] free).
Proof.
  intros free H. apply (f_equal (@length Event)) in H.
  rewrite single_event_count in H. cbn [reverseLoop events length] in H. discriminate.
Qed.
Theorem too_large_count_not_exhausted : forall free,
  reverseRemaining (reverseLoop 2 free (rev (positioned (rows (run [activeOne]))))) = 1%nat.
Proof. intro free. reflexivity. Qed.
Lemma joint_order : map ordinal (events (reverseRun jointRows 150)) = [2%nat;1%nat].
Proof.
  rewrite reverse_order_target, joint_sum. destruct (Req_EM_T 4 0); [lra|reflexivity].
Qed.
Theorem forward_order_false : map ordinal (events (reverseRun jointRows 150)) <> [1%nat;2%nat].
Proof. rewrite joint_order. discriminate. Qed.

Print Assumptions envelope_only_closure_false.
Print Assumptions too_small_count_loses_event.
Print Assumptions too_large_count_not_exhausted.
Print Assumptions forward_order_false.
