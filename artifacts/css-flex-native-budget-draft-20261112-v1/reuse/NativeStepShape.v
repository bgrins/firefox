Require Import Reals ZArith List Bool Lia.
Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeGenerationModel NativeEntryModel NativeCaseData NativeRefinementSpec NativeJointSpec.
Module NativeStepShape.
Import NativeSchedule.
Lemma step_shape : forall config state result,
  NativePass.step config state = Some result ->
  NativePass.prepare config state = Some (NativePass.prepared result) /\
  result = NativePass.finish config state (NativePass.prepared result) (NativePass.reverse result).
Proof.
  intros config state result H. unfold NativePass.step in H.
  destruct (NativePass.prepare config state) as [p|] eqn:P; [|discriminate].
  destruct (NativePass.distributes p) eqn:D.
  - destruct (NativePass.producer p) as [prod|] eqn:W; [|discriminate].
    destruct (NativeReverse.run (NativePass.growing config) prod (frozenCount state)
      (NativePass.entryFree p) (reports state)) as [r|] eqn:R; [|discriminate].
    inversion H; subst result. split; reflexivity.
  - inversion H; subst result. split; reflexivity.
Qed.
Lemma step_mode : forall config state result,
  NativePass.step config state = Some result -> reportMode (NativePass.next result) = reportMode state.
Proof.
  intros config state result H. destruct (step_shape config state result H) as [_ E].
  rewrite E at 1. reflexivity.
Qed.
Lemma step_iteration : forall config state result,
  NativePass.step config state = Some result -> iteration (NativePass.next result) = S (iteration state).
Proof.
  intros config state result H. destruct (step_shape config state result H) as [_ E].
  rewrite E at 1. reflexivity.
Qed.
Print Assumptions step_shape.
Print Assumptions step_mode.
Print Assumptions step_iteration.
End NativeStepShape.
