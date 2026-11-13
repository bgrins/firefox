Require Import Reals ZArith List Bool.
Require Import NativeState NativeProducerModel.
Import ListNotations.
Module NativeProducerFields.
Import NativeSchedule.
Definition ShareOnly (before after : Row) := after = replaceShare before (share after).
Lemma share_only_refl : forall r, ShareOnly r r.
Proof. intros []; reflexivity. Qed.
Lemma share_only_write : forall r value, ShareOnly r (replaceShare r value).
Proof. reflexivity. Qed.
Lemma share_only_rows : forall rs, Forall2 ShareOnly rs rs.
Proof. induction rs; constructor; [apply share_only_refl|assumption]. Qed.
Lemma loop_fields : forall rs grow left index sum factors largest count,
  Forall2 ShareOnly rs
    (NativeProducer.producedRows (NativeProducer.loop grow left index sum factors largest count rs)).
Proof.
  induction rs as [|r tail IH]; intros grow left index sum factors largest count.
  - destruct left; constructor.
  - destruct left as [|k]; [apply share_only_rows|].
    cbn [NativeProducer.loop]. destruct (frozen r); cbn.
    + constructor; [apply share_only_refl|apply IH].
    + constructor; [apply share_only_write|apply IH].
Qed.
Lemma share_only_main : forall before after, ShareOnly before after -> main after = main before.
Proof. intros before after H; unfold ShareOnly in H; rewrite H; reflexivity. Qed.
Lemma share_only_flags : forall before after, ShareOnly before after ->
  minFlag after = minFlag before /\ maxFlag after = maxFlag before.
Proof. intros before after H; unfold ShareOnly in H; rewrite H; split; reflexivity. Qed.
Print Assumptions share_only_refl.
Print Assumptions share_only_write.
Print Assumptions share_only_rows.
Print Assumptions loop_fields.
Print Assumptions share_only_main.
Print Assumptions share_only_flags.
End NativeProducerFields.
