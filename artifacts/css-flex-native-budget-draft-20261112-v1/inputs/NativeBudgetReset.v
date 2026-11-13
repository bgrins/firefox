Require Import Reals ZArith List Bool Lia.
Require Import NativeFloatModel NativeProducerModel NativeState NativePassModel NativeResetProof NativeBudgetArithmetic.
Import ListNotations.
Module NativeBudgetReset.
Import NativeSchedule.
Open Scope Z_scope.
Lemma reset_events : forall rs index free,
  Forall (fun r => Fits64 (NativeResetProof.currentSize r)) rs ->
  (forall k, Fits64 (fold_left Z.sub (firstn k (map NativeResetProof.currentSize rs)) free)) ->
  Forall NativeSchedule.FitsEvent (NativePass.resetEvents (NativePass.reset index free rs)).
Proof.
  induction rs as [|r tail IH]; intros index free Values Prefix; [constructor|].
  inversion Values as [|head rest Head Tail]; subst.
  change (Forall NativeSchedule.FitsEvent
    ({| eventPhase:=Acquiring; eventOrdinal:=index; leftOperand:=free;
        rightOperand:=main (NativeResetProof.resetRow r);
        resultValue:=free-main (NativeResetProof.resetRow r) |}::
      NativePass.resetEvents (NativePass.reset (S index) (free-main (NativeResetProof.resetRow r)) tail))).
  rewrite NativeResetProof.reset_row_main.
  constructor.
  - split; [exact (Prefix O)|]. split; [exact Head|exact (Prefix 1%nat)].
  - apply IH; [exact Tail|]. intro k. exact (Prefix (S k)).
Qed.
Lemma acquisition_record : forall config state prepared,
  NativePass.prepare config state=Some prepared ->
  NativePass.acquisition prepared=NativePass.reset O (NativePass.spaceAvailable config) (rows state).
Proof.
  intros config state prepared H.
  set (acquired:=NativePass.reset O (NativePass.spaceAvailable config) (rows state)).
  set (free:=NativePass.freeSpace acquired).
  set (produced:=NativeProducer.run (NativePass.growing config) (NativePass.resetRows acquired) (frozenCount state)).
  unfold NativePass.prepare in H. fold acquired free produced in H.
  destruct (Z.eqb free 0).
  - inversion H; reflexivity.
  - destruct (NativeFloat.equal (NativeProducer.weightSum produced) NativeFloat.zero).
    + inversion H; reflexivity.
    + destruct (NativeFloat.less (NativeProducer.factorSum produced) NativeFloat.one).
      * destruct (NativeFloat.scale
          (saved (match original state with None=>Some free | Some z=>Some z end))
          (NativeProducer.factorSum produced)) as [wanted|] eqn:Scaled; [|discriminate].
        inversion H; reflexivity.
      * inversion H; reflexivity.
Qed.
Print Assumptions reset_events.
Print Assumptions acquisition_record.
End NativeBudgetReset.
