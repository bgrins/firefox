Require Import Reals ZArith List Bool.
Require Import NativeFloatModel NativeState NativePassModel NativeProducerModel.
Module NativePrepareProducer.
Import NativeSchedule.
Open Scope Z_scope.
Lemma producer_source : forall config state prepared produced,
  NativePass.prepare config state = Some prepared ->
  NativePass.producer prepared = Some produced ->
  produced = NativeProducer.run (NativePass.growing config)
    (NativePass.resetRows (NativePass.reset O (NativePass.spaceAvailable config) (rows state)))
    (frozenCount state).
Proof.
  intros config state prepared produced Prepared Produced.
  unfold NativePass.prepare in Prepared.
  destruct (Z.eqb (NativePass.freeSpace
    (NativePass.reset O (NativePass.spaceAvailable config) (rows state))) 0).
  - inversion Prepared; subst prepared; discriminate.
  - destruct (NativeFloat.equal
      (NativeProducer.weightSum (NativeProducer.run (NativePass.growing config)
        (NativePass.resetRows (NativePass.reset O (NativePass.spaceAvailable config) (rows state)))
        (frozenCount state))) NativeFloat.zero).
    + inversion Prepared; subst prepared. inversion Produced. reflexivity.
    + destruct (NativeFloat.less
        (NativeProducer.factorSum (NativeProducer.run (NativePass.growing config)
          (NativePass.resetRows (NativePass.reset O (NativePass.spaceAvailable config) (rows state)))
          (frozenCount state))) NativeFloat.one).
      * destruct (NativeFloat.scale
          (saved (match original state with None => Some (NativePass.freeSpace
             (NativePass.reset O (NativePass.spaceAvailable config) (rows state))) | Some z => Some z end))
          (NativeProducer.factorSum (NativeProducer.run (NativePass.growing config)
            (NativePass.resetRows (NativePass.reset O (NativePass.spaceAvailable config) (rows state)))
            (frozenCount state)))) as [wanted|]; [|discriminate].
        inversion Prepared; subst prepared. inversion Produced. reflexivity.
      * inversion Prepared; subst prepared. inversion Produced. reflexivity.
Qed.
Print Assumptions producer_source.
End NativePrepareProducer.
