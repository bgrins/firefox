Require Import Reals ZArith List Bool Lia.
Require Import SignModel ReverseTarget NativeState NativePassModel NativeEntryModel NativeRefinementSpec.
Require Import NativeStepShape NativeMainBounds NativeStructuralHistory NativeResetProof.
Require Import NativePreparedFields NativeIndexed NativeReverseEffects NativeProjectionStage NativeProjectedOne NativeClampMap NativeProjectionFlags NativeClampModel.
Import ListNotations.
Module NativeProjectionPoint.
Import NativeSchedule.
Open Scope Z_scope.
Lemma clamped_effect : forall grow model es i before prepared,
  NativePreparedFields.Fields before prepared -> NativeMainBounds.SeedRange (seed before) ->
  (frozen before=false -> minFlag before=false /\ maxFlag before=false) ->
  NativeReverseEffects.atDelta i es=SignHistory.deltaFor i model ->
  let after := NativeClampMap.each (snd (NativeReverseEffects.effect es (i,prepared))) in
  main after=SignHistory.boundedAt model i (projectedRow grow before) /\
  (frozen before=false ->
    minFlag after=Z.ltb (SignHistory.rawAt model i (projectedRow grow before)) (main after) /\
    maxFlag after=Z.ltb (main after) (SignHistory.rawAt model i (projectedRow grow before))).
Proof.
  intros grow model es i before prepared Fields Range Fresh Delta.
  destruct Fields as [Seed [Frozen [Main [Lo Hi]]]].
  unfold NativeReverseEffects.effect; cbn [fst snd]. rewrite Frozen.
  destruct (frozen before) eqn:F.
  - cbn zeta. unfold NativeClampMap.each. rewrite Frozen,F.
    split.
    + rewrite Main. unfold NativeResetProof.currentSize,SignHistory.boundedAt.
      cbn [projectedRow SignHistory.isFrozen SignHistory.main]. rewrite F; reflexivity.
    + discriminate.
  - destruct (Fresh eq_refl) as [Min Max].
    assert (MinP : minFlag prepared=false) by (rewrite Lo; exact Min).
    assert (MaxP : maxFlag prepared=false) by (rewrite Hi; exact Max).
    assert (RangeP : 0 <= minimum (seed prepared) <= maximum (seed prepared)).
    { rewrite Seed. exact (proj1 Range). }
    assert (MaxP32 : maximum (seed prepared) <= 2147483647).
    { rewrite Seed. exact (proj2 Range). }
    assert (Raw : main prepared+NativeReverseEffects.atDelta i es =
      baseSize (seed before)+SignHistory.deltaFor i model).
    { rewrite Main,Delta. unfold NativeResetProof.currentSize. rewrite F; reflexivity. }
    cbn zeta.
    assert (Each : NativeClampMap.each (NativeProjectionFlags.projected prepared
        (main prepared+NativeReverseEffects.atDelta i es)) =
      fst (NativeClamp.one (NativeProjectionFlags.projected prepared
        (main prepared+NativeReverseEffects.atDelta i es)))).
    { unfold NativeClampMap.each.
      cbn [NativeProjectionFlags.projected NativeSchedule.frozen]. rewrite Frozen,F; reflexivity. }
    rewrite Each.
    pose proof (NativeProjectedOne.main_exact prepared
      (main prepared+NativeReverseEffects.atDelta i es) RangeP MaxP32) as MainExact.
    pose proof (NativeProjectedOne.flags_exact prepared
      (main prepared+NativeReverseEffects.atDelta i es) MinP MaxP RangeP MaxP32) as Flags.
    split.
    + rewrite MainExact,Seed,Raw. unfold SignHistory.boundedAt,SignHistory.rawAt.
      cbn [projectedRow SignHistory.isFrozen SignHistory.seed SignHistory.seedBase]. rewrite F. reflexivity.
    + intro Active. rewrite MainExact. rewrite Seed,Raw in Flags |- *.
      unfold SignHistory.rawAt; cbn [projectedRow SignHistory.isFrozen SignHistory.seed SignHistory.seedBase].
      rewrite F. exact Flags.
Qed.
Lemma pointwise : forall bytes line seeds info state result,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state=Some result ->
  forall i before after,
    nth_error (rows state) i=Some before ->
    nth_error (NativeClamp.clampedRows (NativePass.clamped result)) i=Some after ->
    main after=SignHistory.boundedAt
      (SignHistory.distributed line (NativeEntry.seedsMode line seeds)
        (projectedState (NativeEntry.seedsMode line seeds) state)) i
      (projectedRow (NativeEntry.seedsMode line seeds) before) /\
    (frozen before=false ->
      minFlag after=Z.ltb (SignHistory.rawAt
        (SignHistory.distributed line (NativeEntry.seedsMode line seeds)
          (projectedState (NativeEntry.seedsMode line seeds) state)) i
        (projectedRow (NativeEntry.seedsMode line seeds) before)) (main after) /\
      maxFlag after=Z.ltb (main after) (SignHistory.rawAt
        (SignHistory.distributed line (NativeEntry.seedsMode line seeds)
          (projectedState (NativeEntry.seedsMode line seeds) state)) i
        (projectedRow (NativeEntry.seedsMode line seeds) before))).
Proof.
  intros bytes line seeds info state result Admission History Step i before after Before After.
  pose proof (proj1 (NativeStepShape.step_shape _ _ _ Step)) as Prepared.
  pose proof (NativePreparedFields.prepare_fields _ _ _ Prepared) as Fields.
  destruct (NativeIndexed.related_nth _ _ _ Fields i before Before) as [p [NthP Field]].
  pose proof (NativeProjectionStage.stage_rows bytes line seeds info state result Admission History Step) as Stage.
  pose proof (NativeProjectionStage.clamped_rows line seeds info state result History Step) as Clamped.
  rewrite Clamped,Stage,nth_error_map in After.
  rewrite (NativeIndexed.nth_map_indexed _ _ _ i p NthP) in After.
  cbn in After; inversion After; subst after.
  pose proof (NativeMainBounds.history_bounds bytes line seeds info state Admission History) as Bounds.
  assert (Member : In before (rows state)) by (eapply nth_error_In; exact Before).
  rewrite Forall_forall in Bounds. specialize (Bounds before Member).
  pose proof (proj2 (NativeStructuralHistory.history_count_fresh line seeds info state History)) as Fresh.
  unfold NativeEntry.ActiveFresh in Fresh. rewrite Forall_forall in Fresh.
  specialize (Fresh before Member).
  eapply clamped_effect; [exact Field|exact (proj1 Bounds)|exact Fresh|].
  apply NativeProjectionStage.delta_match. eapply NativeProjectionStage.events_match; eassumption.
Qed.
Print Assumptions clamped_effect.
Print Assumptions pointwise.
End NativeProjectionPoint.
