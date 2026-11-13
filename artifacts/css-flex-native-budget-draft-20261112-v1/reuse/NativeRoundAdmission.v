Require Import Reals ZArith List Bool Lia.
Require Import EntryModel EntryAllocation InputTarget PrefixTarget SignModel.
Require Import NativeState NativeEntryModel NativeProducerSums NativeActiveInputs NativeMainBounds NativeSourceHistory NativeWeightProof.
Import ListNotations.
Module NativeRoundAdmission.
Import NativeSchedule.
Open Scope Z_scope.
Lemma used_pair : forall grow r,
  NativeMainBounds.Bounds r ->
  (frozen r = false -> InputTarget.InputValid (NativeWeightProof.payload grow r)) ->
  EntryAcquisition.UsedSource (SignHistory.currentSize (projectedRow grow r))
    (SignHistory.asItem grow (projectedRow grow r)).
Proof.
  intros grow r [Range Main] Valid.
  unfold EntryAcquisition.UsedSource,SignHistory.currentSize.
  cbn [projectedRow SignHistory.isFrozen SignHistory.main SignHistory.seed
    SignHistory.seedBase SignHistory.asItem PrefixTarget.frozen PrefixTarget.payload InputTarget.base].
  destruct (frozen r) eqn:F.
  - split; [|discriminate]. unfold EntryAcquisition.Acquired32.
    unfold NativeMainBounds.SeedRange,NativeMainBounds.MainRange in *; lia.
  - split; [exact (proj1 (proj2 (Valid eq_refl)))|intros; reflexivity].
Qed.
Lemma used_rows : forall grow rs,
  Forall NativeMainBounds.Bounds rs ->
  Forall (fun r => frozen r = false -> InputTarget.InputValid (NativeWeightProof.payload grow r)) rs ->
  Forall2 EntryAcquisition.UsedSource
    (map (fun r => SignHistory.currentSize (projectedRow grow r)) rs)
    (map (fun r => SignHistory.asItem grow (projectedRow grow r)) rs).
Proof.
  intros grow rs B. induction B; intros V; inversion V; subst; cbn; constructor.
  - apply used_pair; assumption.
  - apply IHB; assumption.
Qed.
Lemma round_admitted : forall bytes line seeds info state,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  EntryAcquisition.RoundAdmitted line (NativeEntry.seedsMode line seeds)
    (SignHistory.asRound (NativeEntry.seedsMode line seeds)
      (projectedState (NativeEntry.seedsMode line seeds) state)).
Proof.
  intros bytes line seeds info state Admission History.
  pose proof (NativeMainBounds.history_bounds bytes line seeds info state Admission History) as Bounds.
  pose proof (NativeActiveInputs.history_valid bytes line seeds info state Admission History) as Valid.
  unfold NativeProducerSums.Valid in Valid.
  pose proof (NativeSourceHistory.history_seeds line seeds info state History) as Seeds.
  destruct Admission as [Line [Ids SeedValid]].
  unfold EntryAcquisition.RoundAdmitted,SignHistory.asRound,SignHistory.itemRows,projectedState.
  cbn [EntryAcquisition.items EntryAcquisition.used SignHistory.rows]. rewrite !map_map.
  split.
  - rewrite <- Ids. unfold NativeEntry.modelSeeds. rewrite map_map.
    pose proof (f_equal (map (fun s => identity s)) Seeds) as Equal.
    rewrite map_map in Equal. exact Equal.
  - split; [apply used_rows; assumption|]. split.
    + apply Forall_forall. intros item Member. apply in_map_iff in Member.
      destruct Member as [r [Equal Member]]; subst item.
      rewrite Forall_forall in Valid. exact (Valid r Member).
    + apply Forall_forall. intros item Member. apply in_map_iff in Member.
      destruct Member as [r [Equal Member]]; subst item. intros _. reflexivity.
Qed.
Print Assumptions used_pair.
Print Assumptions used_rows.
Print Assumptions round_admitted.
End NativeRoundAdmission.
