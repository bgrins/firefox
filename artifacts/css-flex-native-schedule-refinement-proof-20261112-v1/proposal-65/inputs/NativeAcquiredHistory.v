Require Import Reals ZArith List Bool Lia.
Require Import EntryModel SignModel.
Require Import NativeState NativeEntryModel NativePassModel NativeSourceHistory NativeStepShape NativeCaptureShape NativeResetCorrespondence NativeRoundAdmission.
Import ListNotations.
Module NativeAcquiredHistory.
Import NativeSchedule.
Open Scope Z_scope.
Definition round (line : EntryAcquisition.Line) (seeds : list Seed) (state : State) :=
  SignHistory.asRound (NativeEntry.seedsMode line seeds) (projectedState (NativeEntry.seedsMode line seeds) state).
Inductive PriorRounds (line : EntryAcquisition.Line) (seeds : list Seed) (info : bool) : State -> list EntryAcquisition.Round -> Prop :=
| prior_initial : PriorRounds line seeds info (NativeEntry.initial line seeds info) []
| prior_step : forall state result previous,
    PriorRounds line seeds info state previous ->
    NativePass.canStep (NativeEntry.config line seeds) state = true ->
    NativePass.step (NativeEntry.config line seeds) state = Some result ->
    PriorRounds line seeds info (NativePass.next result) (previous++[round line seeds state]).
Lemma step_capture : forall line seeds info state result,
  NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state = Some result ->
  saved (original (NativePass.next result)) =
    EntryAcquisition.capture (saved (original state)) (EntryAcquisition.roundFree line (round line seeds state)).
Proof.
  intros line seeds info state result History Step.
  destruct (NativeStepShape.step_shape _ _ _ Step) as [Prepared Finish].
  rewrite Finish. change (saved (NativePass.captured (NativePass.prepared result)) =
    EntryAcquisition.capture (saved (original state)) (EntryAcquisition.roundFree line (round line seeds state))).
  rewrite (NativeCaptureShape.prepare_capture _ _ _ Prepared),NativeResetCorrespondence.free_correspondence.
  change (saved (if Z.eqb (EntryAcquisition.roundFree line (round line seeds state)) 0
    then original state else match original state with None => Some (EntryAcquisition.roundFree line (round line seeds state)) | Some z => Some z end) =
    EntryAcquisition.capture (saved (original state)) (EntryAcquisition.roundFree line (round line seeds state))).
  destruct (Z.eqb (EntryAcquisition.roundFree line (round line seeds state)) 0) eqn:Zero.
  - apply Z.eqb_eq in Zero. rewrite Zero. unfold EntryAcquisition.capture.
    destruct (Z.eq_dec (saved (original state)) 0); lia.
  - apply NativeResetCorrespondence.capture_correspondence.
    exact (NativeSourceHistory.history_original line seeds info state History).
Qed.
Lemma actual_rounds : forall bytes line seeds info state,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  exists previous, PriorRounds line seeds info state previous /\
    length previous = iteration state /\
    EntryAcquisition.History line (NativeEntry.seedsMode line seeds) previous (saved (original state)).
Proof.
  intros bytes line seeds info state Admission History.
  induction History as [|state result Previous IH Can Step].
  - exists []; split; [constructor|]. split; [reflexivity|constructor].
  - destruct IH as [previous [Trace [Length EntryHistory]]].
    exists (previous++[round line seeds state]). split; [econstructor; eassumption|]. split.
    + rewrite app_length,(NativeStepShape.step_iteration (NativeEntry.config line seeds) state result Step). cbn [length]; lia.
    + rewrite (step_capture line seeds info state result Previous Step).
      apply EntryAcquisition.history_step; [exact EntryHistory|].
      eapply NativeRoundAdmission.round_admitted; eassumption.
Qed.
Print Assumptions step_capture.
Print Assumptions actual_rounds.
End NativeAcquiredHistory.
