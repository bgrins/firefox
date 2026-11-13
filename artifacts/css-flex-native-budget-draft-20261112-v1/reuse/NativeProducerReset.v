Require Import Reals ZArith List Bool Lia.
Require Import NativeState NativePassModel NativeResetProof NativeWeightProof NativeProducerSums.
Import ListNotations.
Module NativeProducerReset.
Import NativeSchedule.
Lemma valid_reset : forall grow rs index free,
  NativeProducerSums.Valid grow rs ->
  NativeProducerSums.Valid grow (NativePass.resetRows (NativePass.reset index free rs)).
Proof.
  intros grow rs index free Valid. rewrite NativeResetProof.reset_rows.
  unfold NativeProducerSums.Valid in *. apply Forall_map.
  eapply Forall_impl; [|exact Valid]. intros r Head Fresh.
  rewrite NativeResetProof.reset_row_frozen in Fresh. specialize (Head Fresh).
  unfold NativeWeightProof.payload. rewrite NativeResetProof.reset_row_seed. exact Head.
Qed.
Lemma count_reset : forall rs index free,
  length (filter frozen (NativePass.resetRows (NativePass.reset index free rs))) =
    length (filter frozen rs).
Proof.
  intros rs index free. rewrite NativeResetProof.reset_rows.
  induction rs as [|r tail IH]; [reflexivity|].
  cbn [map filter]. rewrite NativeResetProof.reset_row_frozen.
  destruct (frozen r); cbn; congruence.
Qed.
Lemma length_reset : forall rs index free,
  length (NativePass.resetRows (NativePass.reset index free rs)) = length rs.
Proof. intros; rewrite NativeResetProof.reset_rows,map_length; reflexivity. Qed.
Print Assumptions valid_reset.
Print Assumptions count_reset.
Print Assumptions length_reset.
End NativeProducerReset.
