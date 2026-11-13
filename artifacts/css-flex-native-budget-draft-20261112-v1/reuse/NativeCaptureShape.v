Require Import Reals ZArith List Bool Lia.
Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeGenerationModel NativeEntryModel NativeStepShape.
Module NativeCaptureShape.
Import NativeSchedule.
Open Scope Z_scope.
Lemma prepare_capture : forall config state p,
  NativePass.prepare config state = Some p ->
  NativePass.captured p =
    if Z.eqb (NativePass.freeSpace (NativePass.reset O (NativePass.spaceAvailable config) (rows state))) 0
    then original state else match original state with None => Some (NativePass.freeSpace
      (NativePass.reset O (NativePass.spaceAvailable config) (rows state))) | Some z => Some z end.
Proof.
  intros config state p H. unfold NativePass.prepare in H.
  set (acquired := NativePass.reset O (NativePass.spaceAvailable config) (rows state)) in *.
  set (free := NativePass.freeSpace acquired) in *.
  destruct (Z.eqb free 0) eqn:F; [inversion H; reflexivity|].
  set (produced := NativeProducer.run (NativePass.growing config)
    (NativePass.resetRows acquired) (frozenCount state)) in *.
  destruct (NativeFloat.equal (NativeProducer.weightSum produced) NativeFloat.zero) eqn:W;
    [inversion H; reflexivity|].
  destruct (NativeFloat.less (NativeProducer.factorSum produced) NativeFloat.one) eqn:A.
  - destruct (NativeFloat.scale
      (saved (match original state with None => Some free | Some z => Some z end))
      (NativeProducer.factorSum produced)) as [wanted|] eqn:D; [|discriminate].
    inversion H; reflexivity.
  - inversion H; reflexivity.
Qed.
Lemma prepare_original_agrees : forall config state p,
  NativeEntry.OriginalAgrees state -> NativePass.prepare config state = Some p ->
  match NativePass.captured p with None => True | Some z => z <> 0 end.
Proof.
  intros config state p Original H. unfold NativeEntry.OriginalAgrees in Original.
  rewrite (prepare_capture config state p H).
  destruct (Z.eqb (NativePass.freeSpace (NativePass.reset O (NativePass.spaceAvailable config) (rows state))) 0) eqn:F.
  - exact Original.
  - apply Z.eqb_neq in F. destruct (original state) as [z|] eqn:Z; [exact Original|exact F].
Qed.
Lemma step_original_agrees : forall config state result,
  NativeEntry.OriginalAgrees state -> NativePass.step config state = Some result ->
  NativeEntry.OriginalAgrees (NativePass.next result).
Proof.
  intros config state result Original H. destruct (NativeStepShape.step_shape config state result H) as [P E].
  rewrite E. change (match NativePass.captured (NativePass.prepared result) with None => True | Some z => z <> 0 end).
  eapply prepare_original_agrees; eassumption.
Qed.
Print Assumptions prepare_capture.
Print Assumptions prepare_original_agrees.
Print Assumptions step_original_agrees.
End NativeCaptureShape.
