Require Import Reals ZArith List Bool Lia.
Require Import NativeState NativeProducerModel.
Import ListNotations.
Module NativeProducerStructure.
Import NativeSchedule.
Lemma loop_remaining : forall rs grow left index sum factors largest count,
  NativeProducer.remaining (NativeProducer.loop grow left index sum factors largest count rs) =
    (left-active rs)%nat.
Proof.
  induction rs as [|r tail IH]; intros grow left index sum factors largest count.
  - destruct left; reflexivity.
  - destruct left as [|k]; [reflexivity|].
    cbn [NativeProducer.loop]. destruct (frozen r) eqn:F; cbn; rewrite IH;
      unfold active; cbn; rewrite ?F; cbn; reflexivity.
Qed.
Lemma run_remaining : forall grow rs count,
  count = length (filter frozen rs) -> NativeProducer.remaining (NativeProducer.run grow rs count) = O.
Proof.
  intros grow rs count H; subst count. unfold NativeProducer.run. rewrite loop_remaining.
  assert (length rs = (length (filter frozen rs)+active rs)%nat).
  { induction rs as [|r tail IH]; [reflexivity|]. unfold active in *; cbn.
    destruct (frozen r); cbn; lia. }
  lia.
Qed.
Print Assumptions loop_remaining.
Print Assumptions run_remaining.
End NativeProducerStructure.
