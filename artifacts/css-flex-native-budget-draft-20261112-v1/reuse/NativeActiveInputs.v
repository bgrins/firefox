Require Import Reals ZArith List Bool Lia.
Require Import InputTarget PrefixTarget EntryAcquisitionProof SignModel SignInvariant.
Require Import NativeState NativeEntryModel NativePassModel NativeProducerSums NativeWeightProof.
Require Import NativeProtection NativePassProtection NativeInitialProof NativeEarlyProjection NativeSourceHistory.
Import ListNotations.
Module NativeActiveInputs.
Import NativeSchedule NativeProtection.NativeProtection.
Lemma protected_valid : forall grow before after,
  Forall2 Protect before after -> NativeProducerSums.Valid grow before ->
  NativeProducerSums.Valid grow after.
Proof.
  intros grow before after Protected. induction Protected; intros Valid.
  - constructor.
  - inversion Valid as [|? ? Head Tail]; subst. constructor.
    + intros Active. destruct H as [Seed Frozen].
      assert (OldActive : frozen x = false).
      { destruct (frozen x) eqn:F; [|reflexivity].
        specialize (Frozen eq_refl). subst y. congruence. }
      specialize (Head OldActive).
      unfold NativeWeightProof.payload. rewrite Seed. exact Head.
    + apply IHProtected. exact Tail.
Qed.
Lemma initial_valid : forall bytes line seeds info,
  NativeEntry.Admitted bytes line seeds ->
  NativeProducerSums.Valid (NativeEntry.seedsMode line seeds)
    (rows (NativeEntry.initial line seeds info)).
Proof.
  intros bytes line seeds info Admission.
  pose proof (proj2 (proj2 Admission)) as Seeds.
  pose proof (sign_initial_good line (NativeEntry.modelSeeds line seeds) Seeds) as Good.
  rewrite <- (NativeInitialProof.initial_projection line seeds info Seeds) in Good.
  assert (Mode : SignHistory.mode line (NativeEntry.modelSeeds line seeds) =
    NativeEntry.seedsMode line seeds).
  { unfold NativeEntry.modelSeeds. apply NativeEarlyProjection.projected_mode. }
  rewrite Mode in Good.
  change (Forall (SignRowGood (NativeEntry.seedsMode line seeds))
    (map (projectedRow (NativeEntry.seedsMode line seeds))
      (rows (NativeEntry.initial line seeds info)))) in Good.
  apply Forall_forall. intros r In Active.
  apply (sign_good_item (NativeEntry.seedsMode line seeds)
    (projectedRow (NativeEntry.seedsMode line seeds) r)).
  - rewrite Forall_forall in Good. apply Good. apply in_map. exact In.
  - exact Active.
Qed.
Lemma history_valid : forall bytes line seeds info state,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativeProducerSums.Valid (NativeEntry.seedsMode line seeds) (rows state).
Proof.
  intros bytes line seeds info state Admission History.
  induction History as [|state result Previous IH Can Step].
  - eapply initial_valid; exact Admission.
  - eapply protected_valid; [eapply NativePassProtection.step_protected; exact Step|exact IH].
Qed.
Lemma history_length : forall bytes line seeds info state,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  (length (rows state) <= 134217727)%nat.
Proof.
  intros bytes line seeds info state [Line [Ids Valid]] History.
  pose proof (entry_line_count bytes line Line) as Count.
  pose proof (f_equal (@length nat) Ids) as Length.
  unfold NativeEntry.modelSeeds in Length. rewrite !map_length in Length.
  pose proof (f_equal (@length Seed) (NativeSourceHistory.history_seeds line seeds info state History)) as Rows.
  rewrite map_length in Rows. destruct Line as [_ [_ [Committed _]]]. lia.
Qed.
Print Assumptions protected_valid.
Print Assumptions initial_valid.
Print Assumptions history_valid.
Print Assumptions history_length.
End NativeActiveInputs.
