Require Import Reals ZArith List Bool Lia.
Require Import EntryModel SignModel NativeState NativeEntryModel NativePassModel NativeClampModel NativeReverseModel.
Require Import NativeProtection NativeClampFacts NativeEarlyProof NativeInitialProof NativeStructuralHistory NativeStepShape.
Import ListNotations.
Module NativeMainBounds.
Import NativeSchedule NativeProtection.NativeProtection.
Open Scope Z_scope.
Definition SeedRange (s : Seed) := 0 <= minimum s <= maximum s /\ maximum s <= 2147483647.
Definition MainRange (r : Row) := minimum (seed r) <= main r <= maximum (seed r).
Definition Bounds (r : Row) := SeedRange (seed r) /\ MainRange r.
Definition StageBounds (r : Row) := SeedRange (seed r) /\ (frozen r = true -> MainRange r).
Lemma clamp_range : forall s z, minimum s <= maximum s -> minimum s <= clamp s z <= maximum s.
Proof.
  intros s z B. unfold clamp.
  pose proof (Z.min_spec z (maximum s)).
  pose proof (Z.max_spec (minimum s) (Z.min z (maximum s))). intuition lia.
Qed.
Lemma one_bounds : forall r, SeedRange (seed r) -> Bounds (fst (NativeClamp.one r)).
Proof.
  intros r Range. unfold Bounds,MainRange.
  rewrite NativeClampFacts.one_seed. split; [exact Range|].
  rewrite NativeClampFacts.one_main by (unfold SeedRange in Range; lia).
  apply clamp_range. unfold SeedRange in Range; lia.
Qed.
Lemma kept_stage : forall xs ys,
  Forall2 KeepFrozen xs ys -> Forall Bounds xs -> Forall StageBounds ys.
Proof.
  intros xs ys K; induction K; intros B; [constructor|].
  inversion B as [|? ? Head Tail]; subst. destruct H as [[Seed Frozen] Same].
  destruct Head as [Range Main]. constructor.
  - split; [rewrite Seed; exact Range|]. intro F.
    rewrite Same in F. rewrite (Frozen F). exact Main.
  - apply IHK; exact Tail.
Qed.
Lemma frozen_bounds : forall rs,
  Forall StageBounds rs -> active rs = O -> Forall Bounds rs.
Proof.
  intros rs Stage Zero. apply NativeEarlyProof.active_zero in Zero.
  induction Stage; inversion Zero; subst; constructor; [destruct H; split; auto|auto].
Qed.
Lemma loop_bounds : forall rs index acc,
  Forall StageBounds rs ->
  Forall Bounds (NativeClamp.clampedRows (NativeClamp.loop (active rs) index acc rs)).
Proof.
  induction rs as [|r tail IH]; intros index acc Stage; [constructor|].
  inversion Stage as [|? ? Head Tail]; subst.
  destruct (frozen r) eqn:F.
  - assert (A : active (r::tail) = active tail) by (unfold active; cbn; rewrite F; reflexivity).
    rewrite A. destruct (active tail) as [|k] eqn:K.
    + cbn [NativeClamp.loop NativeClamp.clampedRows].
      apply frozen_bounds; [exact Stage|exact A].
    + cbn [NativeClamp.loop]; rewrite F; cbn [NativeClamp.clampedRows].
      constructor; [destruct Head; split; auto|]. apply IH; exact Tail.
  - assert (A : active (r::tail) = S (active tail)) by (unfold active; cbn; rewrite F; reflexivity).
    rewrite A. cbn [NativeClamp.loop]; rewrite F; cbn [NativeClamp.clampedRows].
    constructor; [apply one_bounds; exact (proj1 Head)|apply IH; exact Tail].
Qed.
Lemma selection_bounds : forall rs final total left index count,
  Forall Bounds rs -> Forall Bounds (NativeClamp.selectedRows
    (NativeClamp.select final total left index count rs)).
Proof.
  induction rs as [|r tail IH]; intros final total left index count B.
  - destruct left; constructor.
  - destruct left as [|k]; [exact B|]. inversion B as [|? ? Head Tail]; subst.
    cbn [NativeClamp.select]. destruct (frozen r); cbn [NativeClamp.selectedRows].
    + constructor; [exact Head|apply IH; exact Tail].
    + constructor; [|apply IH; exact Tail]. destruct (selectedFlags total r),final; exact Head.
Qed.
Lemma initial_bounds : forall bytes line seeds info,
  NativeEntry.Admitted bytes line seeds -> Forall Bounds (rows (NativeEntry.initial line seeds info)).
Proof.
  intros bytes line seeds info Admission.
  pose proof (proj2 (proj2 Admission)) as Valid.
  rewrite NativeInitialProof.initial_rows,map_map.
  apply Forall_forall. intros r MemberRow. apply in_map_iff in MemberRow.
  destruct MemberRow as [s [E InSeed]]; subst r.
  rewrite Forall_forall in Valid.
  specialize (Valid (projectedSeed (NativeEntry.seedsMode line seeds) s)).
  assert (Member : In (projectedSeed (NativeEntry.seedsMode line seeds) s) (NativeEntry.modelSeeds line seeds)).
  { unfold NativeEntry.modelSeeds. apply in_map; exact InSeed. }
  specialize (Valid Member). destruct Valid as [Min [Max Origin]].
  change (0 <= minimum s <= maximum s) in Min.
  change (-2147483648 <= maximum s <= 2147483647) in Max.
  unfold Bounds,SeedRange,MainRange.
  rewrite NativeEarlyProof.early_seed,NativeEarlyProof.early_main.
  cbn [construct seed main]. split; [split; lia|apply clamp_range; lia].
Qed.
Lemma step_bounds : forall config state result,
  NativeStructuralHistory.Counted state -> Forall Bounds (rows state) ->
  NativePass.step config state = Some result -> Forall Bounds (rows (NativePass.next result)).
Proof.
  intros config state result Count B Step.
  pose proof (NativeStructuralHistory.step_stage_kept config state result Step) as K.
  pose proof (kept_stage _ _ K B) as Stage.
  pose proof (NativeStructuralHistory.kept_length _ _ K) as Length.
  pose proof (NativeStructuralHistory.kept_active _ _ K) as Active.
  set (rs := match NativePass.reverse result with None => NativePass.preparedRows (NativePass.prepared result)
      | Some r => NativeReverse.restored r end) in *.
  assert (Left : (length rs-frozenCount state)%nat = active rs).
  { unfold NativeStructuralHistory.Counted in Count.
    rewrite Length,Count,NativeEarlyProof.active_complement. symmetry; exact Active. }
  destruct (NativeStepShape.step_shape config state result Step) as [_ E].
  rewrite E. unfold NativePass.finish; cbn [NativePass.next rows]. fold rs. rewrite Left.
  apply selection_bounds. apply loop_bounds. exact Stage.
Qed.
Lemma history_bounds : forall bytes line seeds info state,
  NativeEntry.Admitted bytes line seeds -> NativeEntry.ModelHistory line seeds info state ->
  Forall Bounds (rows state).
Proof.
  intros bytes line seeds info state Admission History.
  induction History as [|state result Previous IH Can Step].
  - eapply initial_bounds; exact Admission.
  - eapply step_bounds; [exact (proj1 (NativeStructuralHistory.history_count_fresh line seeds info state Previous))|exact IH|exact Step].
Qed.
Print Assumptions clamp_range.
Print Assumptions one_bounds.
Print Assumptions kept_stage.
Print Assumptions frozen_bounds.
Print Assumptions loop_bounds.
Print Assumptions selection_bounds.
Print Assumptions initial_bounds.
Print Assumptions step_bounds.
Print Assumptions history_bounds.
End NativeMainBounds.
