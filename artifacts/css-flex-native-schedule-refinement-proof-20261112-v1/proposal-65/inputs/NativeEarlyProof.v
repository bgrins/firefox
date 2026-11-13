Require Import Reals ZArith List Bool Lia.
Require Import NativeFloatModel NativeState NativeProducerModel NativeReverseModel NativeClampModel NativePassModel NativeGenerationModel NativeEntryModel NativeCaseData NativeRefinementSpec NativeJointSpec.
Import ListNotations.
Module NativeEarlyProof.
Import NativeSchedule.
Lemma early_seed : forall grow r, seed (earlyOne grow r) = seed r.
Proof.
  intros grow r. unfold earlyOne. destruct (frozen r); [reflexivity|].
  destruct (NativeFloat.equal (NativeFloat.promote (factor grow (seed r))) NativeFloat.zero ||
    (if grow then Z.ltb (main r) (baseSize (seed r)) else Z.ltb (baseSize (seed r)) (main r))); reflexivity.
Qed.
Lemma early_main : forall grow r, main (earlyOne grow r) = main r.
Proof.
  intros grow r. unfold earlyOne. destruct (frozen r); [reflexivity|].
  destruct (NativeFloat.equal (NativeFloat.promote (factor grow (seed r))) NativeFloat.zero ||
    (if grow then Z.ltb (main r) (baseSize (seed r)) else Z.ltb (baseSize (seed r)) (main r))); reflexivity.
Qed.
Lemma early_share : forall grow r, share (earlyOne grow r) = share r.
Proof.
  intros grow r. unfold earlyOne. destruct (frozen r); [reflexivity|].
  destruct (NativeFloat.equal (NativeFloat.promote (factor grow (seed r))) NativeFloat.zero ||
    (if grow then Z.ltb (main r) (baseSize (seed r)) else Z.ltb (baseSize (seed r)) (main r))); reflexivity.
Qed.
Lemma early_frozen : forall grow r, frozen r = true -> earlyOne grow r = r.
Proof. intros grow r H. unfold earlyOne; rewrite H; reflexivity. Qed.
Lemma active_zero : forall rs, active rs = O -> Forall (fun r => frozen r = true) rs.
Proof.
  intros rs. induction rs as [|r tail IH]; intro H; [constructor|].
  unfold active in H. cbn in H. destruct (frozen r) eqn:F; cbn in H; [|discriminate].
  constructor; [exact F|apply IH; exact H].
Qed.
Lemma early_all_frozen : forall grow rs,
  Forall (fun r => frozen r = true) rs -> map (earlyOne grow) rs = rs.
Proof.
  intros grow rs H. induction H; cbn; [reflexivity|].
  rewrite early_frozen by exact H. rewrite IHForall. reflexivity.
Qed.
Lemma early_stop : forall grow count rs, earlyLoop grow O count rs = (rs,count).
Proof. intros grow count [|r tail]; reflexivity. Qed.
Lemma early_loop_rows : forall rs grow count,
  fst (earlyLoop grow (active rs) count rs) = map (earlyOne grow) rs.
Proof.
  induction rs as [|r tail IH]; intros grow count; [reflexivity|].
  destruct (frozen r) eqn:F.
  - assert (A : active (r::tail) = active tail) by (unfold active; cbn; rewrite F; reflexivity).
    rewrite A. destruct (active tail) as [|k] eqn:K.
    + cbn [earlyLoop fst map]. rewrite early_frozen by exact F.
      rewrite early_all_frozen; [reflexivity|apply active_zero; exact K].
    + cbn [earlyLoop]. rewrite F. cbn [fst map].
      rewrite early_frozen by exact F. f_equal. apply IH.
  - assert (A : active (r::tail) = S (active tail)) by (unfold active; cbn; rewrite F; reflexivity).
    rewrite A. cbn [earlyLoop]. rewrite F. cbn [fst map]. f_equal. apply IH.
Qed.
Lemma early_active_same : forall grow r,
  frozen (earlyOne grow r) = false -> earlyOne grow r = r.
Proof.
  intros grow r. unfold earlyOne. destruct (frozen r); [intros; reflexivity|].
  destruct (NativeFloat.equal (NativeFloat.promote (factor grow (seed r))) NativeFloat.zero ||
    (if grow then Z.ltb (main r) (baseSize (seed r)) else Z.ltb (baseSize (seed r)) (main r)));
    [discriminate|intros; reflexivity].
Qed.
Lemma construct_fresh : forall s,
  frozen (construct s) = false -> minFlag (construct s) = false /\ maxFlag (construct s) = false.
Proof.
  intros s. change (initiallyFrozen s = false ->
    (if initiallyFrozen s then initialMinFlag s else false) = false /\
    (if initiallyFrozen s then initialMaxFlag s else false) = false).
  destruct (initiallyFrozen s); [discriminate|auto].
Qed.
Lemma early_fresh : forall grow r,
  (frozen r = false -> minFlag r = false /\ maxFlag r = false) ->
  frozen (earlyOne grow r) = false -> minFlag (earlyOne grow r) = false /\ maxFlag (earlyOne grow r) = false.
Proof.
  intros grow r H F. pose proof (early_active_same grow r F) as E.
  rewrite E in *. apply H. exact F.
Qed.
Lemma count_partition : forall rs,
  length rs = (length (filter frozen rs) + active rs)%nat.
Proof.
  intro rs. induction rs as [|r tail IH]; [reflexivity|].
  unfold active in *. cbn. destruct (frozen r); cbn; lia.
Qed.
Lemma active_complement : forall rs,
  (length rs - length (filter frozen rs))%nat = active rs.
Proof. intro rs. pose proof (count_partition rs). lia. Qed.
Lemma early_loop_count : forall rs grow count,
  snd (earlyLoop grow (active rs) count rs) =
    (count + length (filter (fun r => negb (frozen r) && frozen (earlyOne grow r)) rs))%nat.
Proof.
  induction rs as [|r tail IH]; intros grow count; [cbn; lia|].
  destruct (frozen r) eqn:F.
  - assert (A : active (r::tail) = active tail) by (unfold active; cbn; rewrite F; reflexivity).
    rewrite A. cbn [filter]. rewrite F. cbn.
    specialize (IH grow count). destruct (active tail) as [|k] eqn:K.
    + rewrite early_stop in IH. cbn in IH. exact IH.
    + cbn [earlyLoop]. rewrite F. cbn [snd]. exact IH.
  - assert (A : active (r::tail) = S (active tail)) by (unfold active; cbn; rewrite F; reflexivity).
    rewrite A. cbn [earlyLoop]. rewrite F. cbn [snd filter]. rewrite F. cbn.
    destruct (frozen (earlyOne grow r)) eqn:N; cbn.
    + rewrite IH. lia.
    + rewrite IH. reflexivity.
Qed.
Lemma early_frozen_partition : forall grow rs,
  length (filter frozen (map (earlyOne grow) rs)) =
    (length (filter frozen rs) + length (filter (fun r => negb (frozen r) && frozen (earlyOne grow r)) rs))%nat.
Proof.
  intros grow rs. induction rs as [|r tail IH]; [reflexivity|].
  cbn [map filter]. destruct (frozen r) eqn:F.
  - rewrite early_frozen by exact F. rewrite F. cbn. lia.
  - destruct (frozen (earlyOne grow r)); cbn; lia.
Qed.
Print Assumptions count_partition.
Print Assumptions active_complement.
Print Assumptions early_loop_count.
Print Assumptions early_frozen_partition.
Print Assumptions early_active_same.
Print Assumptions construct_fresh.
Print Assumptions early_fresh.
Print Assumptions early_seed.
Print Assumptions early_main.
Print Assumptions early_share.
Print Assumptions early_frozen.
Print Assumptions active_zero.
Print Assumptions early_all_frozen.
Print Assumptions early_stop.
Print Assumptions early_loop_rows.
End NativeEarlyProof.
