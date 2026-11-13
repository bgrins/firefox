Require Import Reals ZArith List Bool Lia.
Require Import NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeEntryModel NativeRefinementSpec.
Require Import NativeProtection NativePhaseProtection NativeReverseProtection NativePassProtection NativeSelectionStructure NativeEarlyProof NativeInitialProof NativeStepShape.
Import ListNotations.
Module NativeStructuralHistory.
Import NativeSchedule NativeProtection.NativeProtection.
Definition Counted (s : State) := frozenCount s = length (filter frozen (rows s)).
Lemma kept_length : forall xs ys, Forall2 KeepFrozen xs ys -> length ys = length xs.
Proof. intros xs ys H; induction H; cbn; congruence. Qed.
Lemma kept_active : forall xs ys, Forall2 KeepFrozen xs ys -> active ys = active xs.
Proof.
  intros xs ys H; induction H; [reflexivity|].
  destruct H as [P F]. unfold active in *; cbn. rewrite F.
  destruct (frozen x); cbn; congruence.
Qed.
Lemma protected_length : forall xs ys, Forall2 Protect xs ys -> length ys = length xs.
Proof. intros xs ys H; induction H; cbn; congruence. Qed.
Lemma step_stage_kept : forall config state result,
  NativePass.step config state = Some result ->
  Forall2 KeepFrozen (rows state)
    (match NativePass.reverse result with None => NativePass.preparedRows (NativePass.prepared result)
     | Some r => NativeReverse.restored r end).
Proof.
  intros config state result H. unfold NativePass.step in H.
  destruct (NativePass.prepare config state) as [p|] eqn:P; [|discriminate].
  pose proof (NativePassProtection.prepare_kept config state p P) as K.
  destruct (NativePass.distributes p) eqn:D.
  - destruct (NativePass.producer p) as [prod|] eqn:W; [|discriminate].
    destruct (NativeReverse.run (NativePass.growing config) prod (frozenCount state)
      (NativePass.entryFree p) (reports state)) as [r|] eqn:R; [|discriminate].
    inversion H; subst result; cbn.
    destruct (NativePassProtection.prepare_output config state p P) as [Rows _]. rewrite W in Rows; cbn in Rows.
    rewrite Rows in K. eapply NativePassProtection.kept_trans; [exact K|].
    eapply NativeReverseProtection.run_kept; exact R.
  - inversion H; subst result; exact K.
Qed.
Lemma finish_count_fresh : forall config state p reversed,
  Counted state -> Forall2 KeepFrozen (rows state)
    (match reversed with None => NativePass.preparedRows p | Some r => NativeReverse.restored r end) ->
  Counted (NativePass.next (NativePass.finish config state p reversed)) /\
  NativeEntry.ActiveFresh (NativePass.next (NativePass.finish config state p reversed)).
Proof.
  intros config state p reversed Count K.
  set (rs := match reversed with None => NativePass.preparedRows p | Some r => NativeReverse.restored r end) in *.
  pose proof (kept_length _ _ K) as Len.
  pose proof (kept_active _ _ K) as Active.
  assert (Left : (length rs-frozenCount state)%nat = active rs).
  { unfold Counted in Count. rewrite Len, Count, NativeEarlyProof.active_complement. symmetry; exact Active. }
  unfold NativePass.finish; cbn.
  fold rs. rewrite Left.
  set (clamped := NativeClamp.loop (active rs) O
    (match reversed with None => 0%Z | Some r => NativeReverse.violation r end) rs).
  assert (CK : Forall2 KeepFrozen rs (NativeClamp.clampedRows clamped)) by apply NativePhaseProtection.clamp_kept.
  pose proof (kept_active _ _ CK) as CA.
  pose proof (kept_length _ _ CK) as CL.
  rewrite <- CA.
  set (selected := NativeClamp.select (Nat.eqb (S (iteration state)) (NativePass.itemLimit config))
    (NativeClamp.total clamped) (active (NativeClamp.clampedRows clamped)) O (frozenCount state)
    (NativeClamp.clampedRows clamped)).
  pose proof (NativeSelectionStructure.selection_balance (NativeClamp.clampedRows clamped)
    (Nat.eqb (S (iteration state)) (NativePass.itemLimit config)) (NativeClamp.total clamped) O (frozenCount state)) as Balance.
  fold selected in Balance.
  pose proof (NativePhaseProtection.selection_protected (NativeClamp.clampedRows clamped)
    (Nat.eqb (S (iteration state)) (NativePass.itemLimit config)) (NativeClamp.total clamped)
    (active (NativeClamp.clampedRows clamped)) O (frozenCount state)) as Selected.
  fold selected in Selected. apply protected_length in Selected.
  split.
  - change (NativeClamp.frozenAfter selected = length (filter frozen (NativeClamp.selectedRows selected))).
    pose proof (NativeEarlyProof.count_partition (NativeClamp.selectedRows selected)) as Partition.
    pose proof (NativeEarlyProof.count_partition (rows state)) as OldPartition.
    unfold Counted in Count. lia.
  - change (NativeSelectionStructure.FreshRows (NativeClamp.selectedRows selected)).
    apply NativeSelectionStructure.selection_fresh.
Qed.
Lemma step_count_fresh : forall config state result,
  Counted state -> NativePass.step config state = Some result ->
  Counted (NativePass.next result) /\ NativeEntry.ActiveFresh (NativePass.next result).
Proof.
  intros config state result C H.
  pose proof (step_stage_kept config state result H) as K.
  destruct (NativeStepShape.step_shape config state result H) as [_ E].
  rewrite E at 1 2. apply finish_count_fresh; assumption.
Qed.
Lemma history_count_fresh : forall line seeds info state,
  NativeEntry.ModelHistory line seeds info state -> Counted state /\ NativeEntry.ActiveFresh state.
Proof.
  intros line seeds info state H. induction H.
  - split; [apply NativeInitialProof.initial_count|apply NativeInitialProof.initial_fresh].
  - eapply step_count_fresh; [exact (proj1 IHHistory)|eassumption].
Qed.
Lemma preservation_target : NativeRefinementTarget.PreservationTarget.
Proof.
  intros bytes line seeds info state result Admitted History Step.
  split; [eapply NativePassProtection.step_seed_map; exact Step|].
  split; [eapply NativePassProtection.step_frozen_record; exact Step|].
  split.
  - exact (proj2 (step_count_fresh _ _ _ (proj1 (history_count_fresh line seeds info state History)) Step)).
  - eapply NativePassProtection.step_count_monotone; exact Step.
Qed.
Print Assumptions kept_length.
Print Assumptions kept_active.
Print Assumptions protected_length.
Print Assumptions step_stage_kept.
Print Assumptions finish_count_fresh.
Print Assumptions step_count_fresh.
Print Assumptions history_count_fresh.
Print Assumptions preservation_target.
End NativeStructuralHistory.
