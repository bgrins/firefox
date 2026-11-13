Require Import Reals ZArith List Bool Lia.
Require Import NativeState NativePassModel NativeProducerModel NativeClampModel NativeProtection NativeClampFacts NativeResetProof.
Import ListNotations.
Module NativePhaseProtection.
Import NativeSchedule NativeProtection.NativeProtection.
Lemma reset_kept : forall rs index free,
  Forall2 KeepFrozen rs (NativePass.resetRows (NativePass.reset index free rs)).
Proof.
  intros rs index free. rewrite NativeResetProof.reset_rows.
  induction rs as [|r tail IH]; cbn; constructor; [|exact IH].
  unfold NativeResetProof.resetRow. destruct (frozen r) eqn:F.
  - apply keep_refl.
  - split; [split; [reflexivity|congruence]|reflexivity].
Qed.
Lemma producer_kept : forall rs grow left index sum factors largest count,
  Forall2 KeepFrozen rs (NativeProducer.producedRows
    (NativeProducer.loop grow left index sum factors largest count rs)).
Proof.
  induction rs as [|r tail IH]; intros grow left index sum factors largest count.
  - destruct left; constructor.
  - destruct left as [|k]; [apply kept_refl|].
    cbn [NativeProducer.loop]. destruct (frozen r) eqn:F; cbn.
    + constructor; [apply keep_refl|apply IH].
    + constructor; [|apply IH]. split; [split; [reflexivity|congruence]|reflexivity].
Qed.
Lemma clamp_kept : forall rs left index acc,
  Forall2 KeepFrozen rs (NativeClamp.clampedRows (NativeClamp.loop left index acc rs)).
Proof.
  induction rs as [|r tail IH]; intros left index acc.
  - destruct left; constructor.
  - destruct left as [|k]; [apply kept_refl|].
    cbn [NativeClamp.loop]. destruct (frozen r) eqn:F; cbn.
    + constructor; [apply keep_refl|apply IH].
    + constructor; [|apply IH]. split.
      * split; [apply NativeClampFacts.one_seed|congruence].
      * apply NativeClampFacts.one_frozen.
Qed.
Lemma selection_protected : forall rs final violation left index count,
  Forall2 Protect rs (NativeClamp.selectedRows
    (NativeClamp.select final violation left index count rs)).
Proof.
  induction rs as [|r tail IH]; intros final violation left index count.
  - destruct left; constructor.
  - destruct left as [|k]; [apply protected_refl|].
    cbn [NativeClamp.select]. destruct (frozen r) eqn:F; cbn.
    + constructor; [apply protect_refl|apply IH].
    + constructor; [|apply IH]. split; [|congruence].
      destruct (selectedFlags violation r), final; reflexivity.
Qed.
Lemma selection_count_monotone : forall rs final violation left index count,
  (count <= NativeClamp.frozenAfter (NativeClamp.select final violation left index count rs))%nat.
Proof.
  induction rs as [|r tail IH]; intros final violation left index count.
  - destruct left; cbn; lia.
  - destruct left as [|k]; [cbn; lia|].
    cbn [NativeClamp.select]. destruct (frozen r) eqn:F; cbn.
    + apply IH.
    + specialize (IH final violation k (S index)
        (if selectedFlags violation r || final then S count else count)).
      destruct (selectedFlags violation r), final; cbn in *; lia.
Qed.
Print Assumptions reset_kept.
Print Assumptions producer_kept.
Print Assumptions clamp_kept.
Print Assumptions selection_protected.
Print Assumptions selection_count_monotone.
End NativePhaseProtection.
