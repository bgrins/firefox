Require Import Reals ZArith List Bool Lia.
Require Import InputTarget PrefixTarget ReverseTarget EntryModel SignModel.
Import ListNotations SignHistory.
Open Scope Z_scope.

Lemma sign_clamp_bounds : forall s value,
  seedMin s <= seedMax s -> seedMin s <= clamp s value <= seedMax s.
Proof.
  intros s value H. unfold clamp. split; [apply Z.le_max_l|].
  apply Z.max_lub; [assumption|apply Z.le_min_r].
Qed.
Lemma sign_clamp_identity : forall s value,
  seedMin s <= value <= seedMax s -> clamp s value = value.
Proof.
  intros s value [Hl Hu]. unfold clamp.
  rewrite Z.min_l by assumption. rewrite Z.max_r by assumption. reflexivity.
Qed.
Lemma sign_clamp_monotone : forall s a b,
  a <= b -> clamp s a <= clamp s b.
Proof.
  intros s a b H. unfold clamp. apply Z.max_le_compat_l. apply Z.min_le_compat_r. assumption.
Qed.
Lemma sign_build_seed : forall s, seed (build s) = s.
Proof. reflexivity. Qed.
Lemma sign_early_seed : forall grow row, seed (early grow row) = seed row.
Proof.
  intros grow row. unfold early. destruct (isFrozen row); reflexivity.
Qed.
Lemma sign_early_main : forall grow row, main (early grow row) = main row.
Proof.
  intros grow row. unfold early. destruct (isFrozen row); reflexivity.
Qed.
Lemma sign_early_share : forall grow row, share (early grow row) = share row.
Proof.
  intros grow row. unfold early. destruct (isFrozen row); reflexivity.
Qed.
Lemma sign_early_active : forall grow row,
  isFrozen (early grow row) = false ->
  isFrozen row = false /\ ActiveBase grow (early grow row).
Proof.
  intros grow row. unfold early. destruct (isFrozen row) eqn:Hf; [intro H; rewrite Hf in H; discriminate|].
  cbn [isFrozen seed]. intro H.
  apply orb_false_iff in H. destruct H as [_ Hwrong].
  split; [reflexivity|]. unfold ActiveBase. cbn [seed isFrozen]. intros _.
  destruct grow; apply Z.ltb_ge in Hwrong; lia.
Qed.
Lemma sign_commit_seed : forall line grow state result total final pair,
  seed (commit line grow state result total final pair) = seed (snd pair).
Proof.
  intros. unfold commit. destruct (isFrozen (snd pair)); reflexivity.
Qed.
Lemma sign_commit_frozen : forall line grow state result total final i row,
  isFrozen row = true -> commit line grow state result total final (i,row) = row.
Proof. intros. unfold commit. cbn [snd]. rewrite H. reflexivity. Qed.
Lemma sign_commit_active : forall line grow state result total final i row,
  isFrozen (commit line grow state result total final (i,row)) = false -> isFrozen row = false.
Proof.
  intros. unfold commit in H. cbn [snd fst] in H.
  destruct (isFrozen row) eqn:Hf; [rewrite Hf in H; discriminate|reflexivity].
Qed.
Lemma sign_commit_bounds : forall line grow state result total final i row,
  seedMin (seed row) <= seedMax (seed row) ->
  seedMin (seed row) <= main row <= seedMax (seed row) ->
  seedMin (seed row) <= main (commit line grow state result total final (i,row)) <= seedMax (seed row).
Proof.
  intros line grow state result total final i row Hbounds Hmain.
  unfold commit. cbn [fst snd]. destruct (isFrozen row) eqn:Hf; [exact Hmain|].
  cbn [main]. unfold boundedAt. rewrite Hf. apply sign_clamp_bounds. exact Hbounds.
Qed.
Lemma sign_initial_seeds : forall line seeds,
  map seed (rows (initial line seeds)) = seeds.
Proof.
  intros line seeds. unfold initial. cbn [rows]. rewrite !map_map.
  transitivity (map (fun s => s) seeds).
  - apply map_ext. intro s. rewrite sign_early_seed. reflexivity.
  - apply map_id.
Qed.
Lemma sign_indexed_snd : forall xs, map snd (indexed xs) = xs.
Proof.
  intro xs. unfold indexed.
  assert (H : forall start, map snd (combine (seq start (length xs)) xs) = xs).
  { induction xs as [|x tail IH]; intro start; cbn [length seq combine map]; [reflexivity|].
    rewrite IH. reflexivity. }
  apply H.
Qed.
Lemma sign_pass_seeds : forall line grow limit iteration state,
  map seed (rows (next (pass line grow limit iteration state))) = map seed (rows state).
Proof.
  intros. unfold pass. cbn [next rows]. rewrite map_map.
  transitivity (map seed (map snd (indexed (rows state)))).
  - rewrite map_map. apply map_ext. intro pair. apply sign_commit_seed.
  - rewrite sign_indexed_snd. reflexivity.
Qed.
Lemma sign_history_seeds : forall line seeds info iteration state,
  History line seeds info iteration state -> map seed (rows state) = seeds.
Proof.
  intros line seeds info iteration state H. induction H.
  - apply sign_initial_seeds.
  - rewrite sign_pass_seeds. assumption.
Qed.

Print Assumptions sign_clamp_bounds.
Print Assumptions sign_clamp_identity.
Print Assumptions sign_clamp_monotone.
Print Assumptions sign_early_active.
Print Assumptions sign_commit_bounds.
Print Assumptions sign_history_seeds.
