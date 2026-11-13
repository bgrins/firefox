Require Import Reals ZArith List Bool Lia.
Require Import SignModel SignResultBinding NativeState NativePassModel NativeEntryModel NativeRefinementSpec.
Require Import NativeIndexed NativePreparedFields NativeResetCorrespondence NativeProjectionStage NativeProjectionPoint.
Require Import NativeStructuralHistory NativeExecutionSums NativeStepShape.
Import ListNotations.
Module NativeProjectionTotals.
Import NativeSchedule.
Open Scope Z_scope.
Lemma fields_sum : forall grow xs ys,
  Forall2 NativePreparedFields.Fields xs ys ->
  NativeExecutionSums.rowSum ys =
    SignHistory.sumZ (map SignHistory.currentSize (map (projectedRow grow) xs)).
Proof.
  intros grow xs ys H; induction H as [|x y xs ys Field Tail IH]; [reflexivity|].
  destruct Field as [_ [_ [Main _]]].
  cbn [NativeExecutionSums.rowSum SignHistory.sumZ fold_right map].
  rewrite Main,NativeResetCorrespondence.current_size.
  fold (NativeExecutionSums.rowSum ys). rewrite IH; reflexivity.
Qed.
Lemma clamped_sum : forall bytes line seeds info state result,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state=Some result ->
  NativeExecutionSums.rowSum (NativeClamp.clampedRows (NativePass.clamped result)) =
  SignHistory.sumZ (map (fun pair => SignHistory.boundedAt
    (SignHistory.distributed line (NativeEntry.seedsMode line seeds)
      (projectedState (NativeEntry.seedsMode line seeds) state)) (fst pair) (snd pair))
    (SignHistory.indexed (SignHistory.rows (projectedState (NativeEntry.seedsMode line seeds) state)))).
Proof.
  intros bytes line seeds info state result Admission History Step.
  set (grow := NativeEntry.seedsMode line seeds).
  set (model := SignHistory.distributed line grow (projectedState grow state)).
  assert (Lists : map main (NativeClamp.clampedRows (NativePass.clamped result)) =
    map (fun pair => SignHistory.boundedAt model (fst pair) (projectedRow grow (snd pair)))
      (NativeIndexed.indexed (rows state))).
  { apply NativeIndexed.nth_ext. intro i.
    pose proof (NativeProjectionStage.clamped_kept _ _ _ Step) as Kept.
    destruct (nth_error (rows state) i) as [before|] eqn:Before.
    - destruct (NativeIndexed.related_nth _ _ _ Kept i before Before) as [after [After K]].
      rewrite nth_error_map,After,(NativeIndexed.nth_map_indexed _ _ _ i before Before). cbn.
      f_equal. exact (proj1 (NativeProjectionPoint.pointwise bytes line seeds info state result
        Admission History Step i before after Before After)).
    - apply nth_error_None in Before.
      assert (Left : nth_error (map main (NativeClamp.clampedRows (NativePass.clamped result))) i=None).
      { apply nth_error_None. rewrite map_length,(NativeStructuralHistory.kept_length _ _ Kept). exact Before. }
      assert (Right : nth_error (map (fun pair => SignHistory.boundedAt model (fst pair)
          (projectedRow grow (snd pair))) (NativeIndexed.indexed (rows state))) i=None).
      { apply nth_error_None. rewrite map_length,NativeIndexed.length_indexed. exact Before. }
      rewrite Left,Right; reflexivity. }
  rewrite NativeExecutionSums.row_sum_map.
  change (SignHistory.sumZ (map main (NativeClamp.clampedRows (NativePass.clamped result))) =
    SignHistory.sumZ (map (fun pair => SignHistory.boundedAt model (fst pair) (snd pair))
      (SignHistory.indexed (SignHistory.rows (projectedState grow state))))).
  rewrite Lists. unfold SignHistory.indexed,projectedState; cbn [SignHistory.rows].
  rewrite map_length,NativeIndexed.combine_map,map_map. reflexivity.
Qed.
Lemma total : forall bytes line seeds info state result,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  NativePass.step (NativeEntry.config line seeds) state=Some result ->
  NativeClamp.total (NativePass.clamped result) =
    SignHistory.violation (SignHistory.distributed line (NativeEntry.seedsMode line seeds)
      (projectedState (NativeEntry.seedsMode line seeds) state))
      (projectedState (NativeEntry.seedsMode line seeds) state).
Proof.
  intros bytes line seeds info state result Admission History Step.
  pose proof (proj1 (NativeStepShape.step_shape _ _ _ Step)) as Prepared.
  pose proof (NativePreparedFields.prepare_fields _ _ _ Prepared) as Fields.
  pose proof (fields_sum (NativeEntry.seedsMode line seeds) _ _ Fields) as PreparedSum.
  pose proof (NativeProjectionStage.events_match bytes line seeds info state result Admission History Step) as Events.
  pose proof (NativeProjectionStage.delta_sum_match _ _ Events) as Deltas.
  rewrite (NativeProjectionStage.total_balance _ _ _ Step),
    (clamped_sum bytes line seeds info state result Admission History Step),PreparedSum,Deltas.
  rewrite sign_violation_difference,sign_raw_sum.
  cbn [projectedState SignHistory.rows]. lia.
Qed.
Print Assumptions fields_sum.
Print Assumptions clamped_sum.
Print Assumptions total.
End NativeProjectionTotals.
