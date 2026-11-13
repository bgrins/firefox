Require Import ZArith List Bool Lia.
Require Import EntryModel SignModel NativeState NativePassModel NativeEntryModel NativeResetProof.
Import ListNotations.
Module NativeResetCorrespondence.
Import NativeSchedule.
Open Scope Z_scope.
Lemma current_size : forall grow r,
  SignHistory.currentSize (projectedRow grow r) = NativeResetProof.currentSize r.
Proof. reflexivity. Qed.
Lemma free_correspondence : forall line seeds state,
  NativePass.freeSpace (NativePass.reset O (NativePass.spaceAvailable (NativeEntry.config line seeds)) (rows state)) =
  SignHistory.free line (NativeEntry.seedsMode line seeds) (projectedState (NativeEntry.seedsMode line seeds) state).
Proof.
  intros. rewrite NativeResetProof.reset_free.
  unfold SignHistory.free,EntryAcquisition.roundFree,SignHistory.asRound,projectedState.
  cbn. rewrite map_map. reflexivity.
Qed.
Lemma capture_correspondence : forall old free,
  (match old with None => True | Some value => value <> 0 end) ->
  saved (match old with None => Some free | Some value => Some value end) =
    EntryAcquisition.capture (saved old) free.
Proof.
  intros [value|] free Original; unfold saved,EntryAcquisition.capture; cbn.
  - destruct (Z.eq_dec value 0); [contradiction|reflexivity].
  - destruct (Z.eq_dec 0 0); [reflexivity|contradiction].
Qed.
Print Assumptions current_size.
Print Assumptions free_correspondence.
Print Assumptions capture_correspondence.
End NativeResetCorrespondence.
