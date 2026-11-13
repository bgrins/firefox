Require Import Reals ZArith List Bool Lia.
Require Import InputTarget PrefixTarget ReverseTarget EntryModel SignModel SignBasics.
Import ListNotations SignHistory.
Open Scope Z_scope.
Definition SignRowGood (grow : bool) (row : Row) : Prop :=
  SeedValid (seed row) /\
  seedMin (seed row) <= main row <= seedMax (seed row) /\
  ActiveBase grow row /\
  (isFrozen row = false -> seedFrozen (seed row) = false).
Lemma sign_early_good : forall grow s,
  SeedValid s -> SignRowGood grow (early grow (build s)).
Proof.
  intros grow s Hs. unfold SignRowGood.
  rewrite sign_early_seed, sign_early_main. cbn [build seed main].
  split; [exact Hs|]. split.
  - apply sign_clamp_bounds. unfold SeedValid in Hs. lia.
  - split.
    + intro Ha. exact ((proj2 (sign_early_active grow (build s) Ha)) Ha).
    + intro Ha. exact (proj1 (sign_early_active grow (build s) Ha)).
Qed.
Lemma sign_initial_good : forall line seeds,
  Forall SeedValid seeds -> Forall (SignRowGood (mode line seeds)) (rows (initial line seeds)).
Proof.
  intros line seeds H. unfold initial. cbn [rows]. rewrite map_map.
  apply Forall_forall. intros row Hin. apply in_map_iff in Hin.
  destruct Hin as [s [Heq Hin]]. subst row. apply sign_early_good.
  rewrite Forall_forall in H. exact (H s Hin).
Qed.
Lemma sign_commit_good : forall line grow state result total final i row,
  SignRowGood grow row -> SignRowGood grow (commit line grow state result total final (i,row)).
Proof.
  intros line grow state result total final i row [Hs [Hm [Ha Ho]]].
  unfold SignRowGood. rewrite sign_commit_seed. cbn [snd].
  split; [exact Hs|]. split.
  - apply sign_commit_bounds; [unfold SeedValid in Hs; lia|exact Hm].
  - split.
    + unfold ActiveBase. rewrite sign_commit_seed. cbn [snd]. intro Hactive.
      apply Ha. eapply sign_commit_active; exact Hactive.
    + intro Hactive. apply Ho. eapply sign_commit_active; exact Hactive.
Qed.
Lemma sign_pass_good : forall line grow limit iteration state,
  Forall (SignRowGood grow) (rows state) ->
  Forall (SignRowGood grow) (rows (next (pass line grow limit iteration state))).
Proof.
  intros line grow limit iteration state H.
  unfold pass. cbn [next rows]. apply Forall_forall.
  intros row Hin. apply in_map_iff in Hin. destruct Hin as [[i before] [Heq Hin]]. subst row.
  apply sign_commit_good. rewrite Forall_forall in H. apply H.
  rewrite <- sign_indexed_snd. apply in_map with (f:=@snd nat Row) in Hin. exact Hin.
Qed.
Lemma sign_history_good : forall e line seeds info iteration state,
  InputValid e line seeds -> History line seeds info iteration state ->
  Forall (SignRowGood (mode line seeds)) (rows state).
Proof.
  intros e line seeds info iteration state [_ [_ Hseeds]] Hhistory.
  induction Hhistory.
  - apply sign_initial_good. exact Hseeds.
  - apply sign_pass_good. exact IHHhistory.
Qed.
Lemma sign_good_item : forall grow row,
  SignRowGood grow row -> ItemValid (asItem grow row).
Proof.
  intros grow row [Hs [Hm [Ha Ho]]] Hactive.
  change (isFrozen row = false) in Hactive.
  destruct Hs as [[Hmin Hbounds] [Hmax Horigin]].
  destruct (Horigin (Ho Hactive)) as [Hfactor Hbase].
  unfold InputTarget.InputValid. cbn [asItem payload factor base growing].
  split; [exact Hfactor|]. split; [exact Hbase|].
  intro Hg. subst grow. specialize (Ha Hactive).
  pose proof (sign_clamp_bounds (seed row) (seedBase (seed row)) Hbounds) as Hhypo.
  cbn in Ha. unfold hypothetical in Ha. lia.
Qed.
Lemma sign_good_used : forall grow row,
  SignRowGood grow row -> EntryAcquisition.UsedSource (currentSize row) (asItem grow row).
Proof.
  intros grow row [Hs [Hm [Ha Ho]]]. unfold EntryAcquisition.UsedSource.
  unfold currentSize. cbn [asItem frozen payload base].
  destruct (isFrozen row) eqn:Hf.
  - split; [|discriminate]. destruct Hs as [[Hmin Hbounds] [Hmax Horigin]].
    unfold EntryAcquisition.Acquired32 in *. lia.
  - split; [|intros; reflexivity]. apply (proj2 (proj2 (proj2 Hs) (Ho eq_refl))).
Qed.
Print Assumptions sign_early_good.
Print Assumptions sign_commit_good.
Print Assumptions sign_history_good.
Print Assumptions sign_good_item.
Print Assumptions sign_good_used.
