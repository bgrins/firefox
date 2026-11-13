Require Import Reals ZArith List Bool Lia.
Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeStepShape NativeProtection NativePhaseProtection NativeReverseProtection.
Import ListNotations.
Module NativePassProtection.
Import NativeSchedule NativeProtection.NativeProtection.
Lemma kept_protected : forall xs ys, Forall2 KeepFrozen xs ys -> Forall2 Protect xs ys.
Proof. intros xs ys H; induction H; constructor; [exact (proj1 H)|assumption]. Qed.
Lemma kept_trans : forall xs ys zs, Forall2 KeepFrozen xs ys ->
  Forall2 KeepFrozen ys zs -> Forall2 KeepFrozen xs zs.
Proof.
  intros xs ys zs H; revert zs. induction H; intros zs K; inversion K; subst; constructor.
  - eapply keeps_trans; eassumption.
  - eapply IHForall2; eassumption.
Qed.
Lemma prepare_output : forall config state p,
  NativePass.prepare config state = Some p ->
  NativePass.preparedRows p =
    match NativePass.producer p with None => NativePass.resetRows
      (NativePass.reset O (NativePass.spaceAvailable config) (rows state))
    | Some prod => NativeProducer.producedRows prod end /\
  (forall prod, NativePass.producer p = Some prod -> prod =
    NativeProducer.run (NativePass.growing config)
      (NativePass.resetRows (NativePass.reset O (NativePass.spaceAvailable config) (rows state)))
      (frozenCount state)).
Proof.
  intros config state p H. unfold NativePass.prepare in H.
  set (acquired := NativePass.reset O (NativePass.spaceAvailable config) (rows state)) in *.
  set (free := NativePass.freeSpace acquired) in *.
  destruct (Z.eqb free 0) eqn:F.
  - inversion H; subst p; split; [reflexivity|intros; discriminate].
  - set (produced := NativeProducer.run (NativePass.growing config)
      (NativePass.resetRows acquired) (frozenCount state)) in *.
    destruct (NativeFloat.equal (NativeProducer.weightSum produced) NativeFloat.zero) eqn:W.
    + inversion H; subst p; split; [reflexivity|intros prod E; inversion E; reflexivity].
    + destruct (NativeFloat.less (NativeProducer.factorSum produced) NativeFloat.one) eqn:A.
      * destruct (NativeFloat.scale
          (saved (match original state with None => Some free | Some z => Some z end))
          (NativeProducer.factorSum produced)) as [wanted|] eqn:D; [|discriminate].
        inversion H; subst p; split; [reflexivity|intros prod E; inversion E; reflexivity].
      * inversion H; subst p; split; [reflexivity|intros prod E; inversion E; reflexivity].
Qed.
Lemma prepare_kept : forall config state p,
  NativePass.prepare config state = Some p ->
  Forall2 KeepFrozen (rows state) (NativePass.preparedRows p).
Proof.
  intros config state p H. destruct (prepare_output config state p H) as [Rows Producer].
  rewrite Rows. destruct (NativePass.producer p) as [prod|] eqn:P.
  - rewrite (Producer prod eq_refl). eapply kept_trans.
    + apply NativePhaseProtection.reset_kept.
    + apply NativePhaseProtection.producer_kept.
  - apply NativePhaseProtection.reset_kept.
Qed.
Lemma finish_protected : forall config state p reversed,
  Forall2 Protect (rows state)
    (match reversed with None => NativePass.preparedRows p | Some r => NativeReverse.restored r end) ->
  Forall2 Protect (rows state) (rows (NativePass.next (NativePass.finish config state p reversed))).
Proof.
  intros config state p reversed H. unfold NativePass.finish; cbn.
  eapply protected_trans; [exact H|].
  eapply protected_trans.
  - apply kept_protected. apply NativePhaseProtection.clamp_kept.
  - apply NativePhaseProtection.selection_protected.
Qed.
Lemma step_protected : forall config state result,
  NativePass.step config state = Some result ->
  Forall2 Protect (rows state) (rows (NativePass.next result)).
Proof.
  intros config state result H. unfold NativePass.step in H.
  destruct (NativePass.prepare config state) as [p|] eqn:P; [|discriminate].
  pose proof (prepare_kept config state p P) as K.
  destruct (NativePass.distributes p) eqn:D.
  - destruct (NativePass.producer p) as [prod|] eqn:W; [|discriminate].
    destruct (NativeReverse.run (NativePass.growing config) prod (frozenCount state)
      (NativePass.entryFree p) (reports state)) as [r|] eqn:R; [|discriminate].
    inversion H; subst result. apply finish_protected. apply kept_protected.
    destruct (prepare_output config state p P) as [Rows _]. rewrite W in Rows; cbn in Rows.
    rewrite Rows in K. eapply kept_trans; [exact K|]. eapply NativeReverseProtection.run_kept; exact R.
  - inversion H; subst result. apply finish_protected. apply kept_protected; exact K.
Qed.
Lemma step_seed_map : forall config state result,
  NativePass.step config state = Some result ->
  map seed (rows (NativePass.next result)) = map seed (rows state).
Proof. intros; apply protected_seeds; eapply step_protected; eassumption. Qed.
Lemma step_frozen_record : forall config state result,
  NativePass.step config state = Some result -> forall i r,
  nth_error (rows state) i = Some r -> frozen r = true ->
  nth_error (rows (NativePass.next result)) i = Some r.
Proof. intros; eapply protected_frozen_nth; [eapply step_protected| |]; eassumption. Qed.
Lemma step_count_monotone : forall config state result,
  NativePass.step config state = Some result ->
  (frozenCount state <= frozenCount (NativePass.next result))%nat.
Proof.
  intros config state result H. destruct (NativeStepShape.step_shape config state result H) as [_ E].
  rewrite E at 1. apply NativePhaseProtection.selection_count_monotone.
Qed.
Print Assumptions kept_protected.
Print Assumptions kept_trans.
Print Assumptions prepare_output.
Print Assumptions prepare_kept.
Print Assumptions finish_protected.
Print Assumptions step_protected.
Print Assumptions step_seed_map.
Print Assumptions step_frozen_record.
Print Assumptions step_count_monotone.
End NativePassProtection.
