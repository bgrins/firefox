Require Import Reals ZArith List Bool Lia.
Require Import InputTarget SignModel.
Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeGenerationModel NativeEntryModel NativeCaseData NativeRefinementSpec NativeJointSpec NativeEarlyProof NativeEarlyProjection.
Import ListNotations.
Module NativeInitialProof.
Import NativeSchedule.
Lemma initial_rows : forall line seeds info,
  rows (NativeEntry.initial line seeds info) =
    map (earlyOne (NativeEntry.seedsMode line seeds)) (map construct seeds).
Proof.
  intros line seeds info. unfold NativeEntry.initial, initialize. cbn [rows].
  rewrite NativeEarlyProof.active_complement. apply NativeEarlyProof.early_loop_rows.
Qed.
Lemma initial_count : forall line seeds info,
  frozenCount (NativeEntry.initial line seeds info) =
    length (filter frozen (rows (NativeEntry.initial line seeds info))).
Proof.
  intros line seeds info. rewrite initial_rows.
  unfold NativeEntry.initial, initialize. cbn [frozenCount].
  rewrite NativeEarlyProof.active_complement, NativeEarlyProof.early_loop_count,
    NativeEarlyProof.early_frozen_partition. reflexivity.
Qed.
Lemma initial_seeds : forall line seeds info,
  map seed (rows (NativeEntry.initial line seeds info)) = seeds.
Proof.
  intros line seeds info. rewrite initial_rows, map_map, map_map.
  transitivity (map (fun s => s) seeds).
  - apply map_ext. intro s. rewrite NativeEarlyProof.early_seed. reflexivity.
  - apply map_id.
Qed.
Lemma initial_fresh : forall line seeds info,
  NativeEntry.ActiveFresh (NativeEntry.initial line seeds info).
Proof.
  intros line seeds info. unfold NativeEntry.ActiveFresh. rewrite initial_rows, map_map.
  apply Forall_forall. intros r H. apply in_map_iff in H. destruct H as [s [E H]]. subst r.
  apply NativeEarlyProof.early_fresh. apply NativeEarlyProof.construct_fresh.
Qed.
Lemma initial_projection : forall line seeds info,
  Forall SignHistory.SeedValid (NativeEntry.modelSeeds line seeds) ->
  projectedState (NativeEntry.seedsMode line seeds) (NativeEntry.initial line seeds info) =
    SignHistory.initial line (NativeEntry.modelSeeds line seeds).
Proof.
  intros line seeds info V.
  change ({| SignHistory.rows := map (projectedRow (NativeEntry.seedsMode line seeds))
    (rows (NativeEntry.initial line seeds info)); SignHistory.saved := 0 |} =
    SignHistory.initial line (NativeEntry.modelSeeds line seeds)).
  rewrite initial_rows. unfold SignHistory.initial, NativeEntry.modelSeeds.
  rewrite NativeEarlyProjection.projected_mode. f_equal.
  rewrite !map_map. apply map_ext_in. intros s H.
  apply NativeEarlyProjection.early_projection.
  apply Forall_forall with (x:=projectedSeed (NativeEntry.seedsMode line seeds) s) in V.
  - exact V.
  - unfold NativeEntry.modelSeeds. apply in_map. exact H.
Qed.
Lemma initial_report_shape : forall line seeds info,
  NativeEntry.ReportShape (NativeEntry.initial line seeds info).
Proof.
  intros line seeds info. destruct info; [|exact I].
  change (map reportIdentity (reportsFor (map construct seeds)) =
    map (fun r => identity (seed r)) (rows (NativeEntry.initial line seeds true)) /\
    map reportBase (reportsFor (map construct seeds)) =
    map (fun r => baseSize (seed r)) (rows (NativeEntry.initial line seeds true))).
  split.
  - transitivity (map identity seeds).
    + unfold reportsFor. rewrite !map_map. reflexivity.
    + pose proof (f_equal (map identity) (initial_seeds line seeds true)) as E.
      rewrite map_map in E. symmetry; exact E.
  - transitivity (map baseSize seeds).
    + unfold reportsFor. rewrite !map_map. reflexivity.
    + pose proof (f_equal (map baseSize) (initial_seeds line seeds true)) as E.
      rewrite map_map in E. symmetry; exact E.
Qed.
Theorem initial_target : NativeRefinementTarget.InitialTarget.
Proof.
  intros bytes line seeds info H.
  assert (V : Forall SignHistory.SeedValid (NativeEntry.modelSeeds line seeds)) by exact (proj2 (proj2 H)).
  split.
  - unfold NativeEntry.NativeInvariant. split; [apply initial_count|].
    split; [apply initial_fresh|]. split; [exact I|].
    split; [apply initial_report_shape|]. split; [reflexivity|].
    split; [apply initial_seeds|]. rewrite initial_projection by exact V.
    apply SignHistory.history_initial.
  - split; reflexivity.
Qed.
Print Assumptions initial_report_shape.
Print Assumptions initial_target.
Print Assumptions initial_projection.
Print Assumptions initial_rows.
Print Assumptions initial_count.
Print Assumptions initial_seeds.
Print Assumptions initial_fresh.
End NativeInitialProof.
