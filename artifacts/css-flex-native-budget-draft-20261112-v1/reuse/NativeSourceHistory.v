Require Import ZArith List Bool.
Require Import NativeState NativePassModel NativeEntryModel NativeStepShape NativePassProtection NativeCaptureShape NativeInitialProof.
Import ListNotations.
Module NativeSourceHistory.
Import NativeSchedule.
Lemma history_seeds : forall line seeds info state,
  NativeEntry.ModelHistory line seeds info state -> map seed (rows state) = seeds.
Proof.
  intros line seeds info state H; induction H as [|state result Previous IH Can Step].
  - apply NativeInitialProof.initial_seeds.
  - erewrite NativePassProtection.step_seed_map by eassumption. exact IH.
Qed.
Lemma history_original : forall line seeds info state,
  NativeEntry.ModelHistory line seeds info state -> NativeEntry.OriginalAgrees state.
Proof.
  intros line seeds info state H; induction H as [|state result Previous IH Can Step].
  - exact I.
  - eapply NativeCaptureShape.step_original_agrees; eassumption.
Qed.
Lemma history_mode : forall line seeds info state,
  NativeEntry.ModelHistory line seeds info state ->
  reportMode state = if info then Some (NativeEntry.seedsMode line seeds) else None.
Proof.
  intros line seeds info state H; induction H as [|state result Previous IH Can Step].
  - reflexivity.
  - erewrite NativeStepShape.step_mode by eassumption. exact IH.
Qed.
Print Assumptions history_seeds.
Print Assumptions history_original.
Print Assumptions history_mode.
End NativeSourceHistory.
