Require Import Reals ZArith List Bool Lia.
Require Import WeightTarget EntryModel EntryCapture EntryComposition EntryFactors PrefixTarget ReverseTarget SignModel.
Require Import NativeState NativeEntryModel NativeRoundAdmission NativeAcquiredHistory.
Module NativeAcquiredDomain.
Import NativeSchedule.
Open Scope Z_scope.
Lemma source_domain : forall bytes line seeds info state,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  ReverseTarget.FreeDomain (SignHistory.free line (NativeEntry.seedsMode line seeds)
    (projectedState (NativeEntry.seedsMode line seeds) state)) /\
  EntryAcquisition.SmallDomain (saved (original state)) /\
  ReverseTarget.FreeDomain (EntryAcquisition.capture (saved (original state))
    (SignHistory.free line (NativeEntry.seedsMode line seeds) (projectedState (NativeEntry.seedsMode line seeds) state))) /\
  ReverseTarget.FreeDomain (EntryAcquisition.entryFree (SignHistory.prepared line (NativeEntry.seedsMode line seeds)
    (projectedState (NativeEntry.seedsMode line seeds) state))) /\
  (0 <= EntryAcquisition.factorTotal (EntryAcquisition.factorRun
    (SignHistory.itemRows (NativeEntry.seedsMode line seeds) (projectedState (NativeEntry.seedsMode line seeds) state))) <= WeightTarget.sumLimit)%R /\
  ReverseTarget.reverseRemaining (SignHistory.distributed line (NativeEntry.seedsMode line seeds)
    (projectedState (NativeEntry.seedsMode line seeds) state)) = O.
Proof.
  intros bytes line seeds info state Admission History.
  pose proof (proj1 Admission) as Line.
  pose proof (NativeRoundAdmission.round_admitted bytes line seeds info state Admission History) as Round.
  destruct (NativeAcquiredHistory.actual_rounds bytes line seeds info state Admission History)
    as [previous [Trace [Length EntryHistory]]].
  pose proof (entry_round_small bytes line (NativeEntry.seedsMode line seeds)
    (NativeAcquiredHistory.round line seeds state) Line Round) as Current.
  pose proof (proj1 (entry_history_capture bytes line (NativeEntry.seedsMode line seeds)
    previous (saved (original state)) Line EntryHistory)) as Saved.
  pose proof (entry_capture_small _ _ Saved Current) as Captured.
  destruct (entry_entry_target bytes line (NativeEntry.seedsMode line seeds) previous (saved (original state))
    (NativeAcquiredHistory.round line seeds state) Line EntryHistory Round) as [_ [_ [Domain Rest]]].
  pose proof (entry_factor_target bytes line (NativeEntry.seedsMode line seeds)
    (NativeAcquiredHistory.round line seeds state) Line Round) as [_ [_ [_ [Factors _]]]].
  pose proof (entry_composition_target bytes line (NativeEntry.seedsMode line seeds) previous (saved (original state))
    (NativeAcquiredHistory.round line seeds state) Line EntryHistory Round)
      as [_ [_ [_ [_ [_ [Remaining _]]]]]].
  split; [apply entry_small_domain; exact Current|].
  split; [exact Saved|]. split; [apply entry_small_domain; exact Captured|].
  split; [exact Domain|]. split; assumption.
Qed.
Print Assumptions source_domain.
End NativeAcquiredDomain.
