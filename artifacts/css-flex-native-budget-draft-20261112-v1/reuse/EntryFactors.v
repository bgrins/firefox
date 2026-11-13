Require Import EntryNumerals.
Require Import Reals ZArith List Psatz.
Require Import WeightTarget Weights InputTarget InputProof PrefixTarget PrefixProof.
Require Import EntryAllocation EntryModel EntryTarget EntryAllocationProof.
Import ListNotations EntryAcquisition InitialEntryTarget.
Open Scope R_scope.
Lemma entry_factors_length : forall xs, length (activeFactors xs)=activeCount xs.
Proof.
  induction xs as [|x xs IH]; [reflexivity|].
  unfold activeFactors, activeCount in *. cbn [filter map activeWeights length].
  destruct (frozen x); cbn; exact (f_equal S IH) || exact IH.
Qed.
Lemma entry_frozen_factors : forall xs, activeCount xs=O -> activeFactors xs=[].
Proof.
  intros xs H. apply length_zero_iff_nil. rewrite entry_factors_length. exact H.
Qed.
Lemma entry_factor_sum : forall xs sum,
  factorTotal (factorLoop (activeCount xs) sum xs)=accumulate (activeFactors xs) sum.
Proof.
  induction xs as [|x xs IH]; intro sum; [reflexivity|].
  unfold activeCount at 1. cbn [activeWeights length]. destruct (frozen x) eqn:Hx.
  - destruct (length (activeWeights xs)) eqn:Hcount.
    + cbn [factorLoop factorTotal]. unfold activeFactors. cbn [filter map]. rewrite Hx. cbn.
      fold (activeFactors xs). rewrite entry_frozen_factors; [reflexivity|exact Hcount].
    + cbn [factorLoop]. rewrite Hx. cbn [factorTotal]. specialize (IH sum).
      unfold activeCount in IH. rewrite Hcount in IH.
      unfold activeFactors. cbn [filter map]. rewrite Hx. cbn. exact IH.
  - cbn [factorLoop]. rewrite Hx. cbn [factorTotal].
    unfold activeFactors. cbn [filter map]. rewrite Hx. cbn [negb filter map accumulate fold_left].
    apply IH.
Qed.
Lemma entry_factor_stop : forall xs sum,
  factorRemaining (factorLoop (activeCount xs) sum xs)=O /\
  (factorVisited (factorLoop (activeCount xs) sum xs)<=length xs)%nat.
Proof.
  induction xs as [|x xs IH]; intro sum; [cbn; split; reflexivity|].
  unfold activeCount at 1 2. cbn [activeWeights length]. destruct (frozen x) eqn:Hx.
  - destruct (length (activeWeights xs)) eqn:Hcount.
    + cbn [factorLoop factorRemaining factorVisited]. split; [reflexivity|lia].
    + specialize (IH sum). unfold activeCount in IH. rewrite Hcount in IH.
      cbn [factorLoop]. rewrite Hx. cbn [factorRemaining factorVisited]. destruct IH; split; [assumption|lia].
  - cbn [factorLoop]. rewrite Hx. cbn [factorRemaining factorVisited].
    specialize (IH (WeightTarget.rn (sum+value32 (factor (payload x))))).
    unfold activeCount in IH. destruct IH as [Hleft Hvisited]. cbn [length].
    split; [exact Hleft|]. apply le_n_S. exact Hvisited.
Qed.
Lemma entry_factor_valid : forall xs, Forall ItemValid xs -> Forall FactorValid (activeFactors xs).
Proof.
  intros xs H. induction H; [constructor|]. unfold activeFactors in *. cbn [filter map].
  destruct (frozen x) eqn:Hx; cbn; [exact IHForall|].
  constructor; [|exact IHForall]. apply (proj1 (promotion_target _ (proj1 (H Hx)))).
Qed.
Lemma entry_factor_prefix_valid : forall xs k, Forall FactorValid xs -> Forall FactorValid (firstn k xs).
Proof. intros xs k H. revert k. induction H; intros [|k]; cbn; constructor; auto. Qed.
Theorem entry_factor_target : InitialEntryTarget.FactorTarget.
Proof.
  intros e line mode round [He [Hr Hline]] [Hids [Hpairs [Hvalid Hmode]]].
  pose proof (entry_allocation_target e (allocation line) He Hr) as [_ [_ [_ Hcount]]].
  pose proof (f_equal (@length nat) Hids) as Hlength. rewrite map_length in Hlength.
  assert (Hrows : (Z.of_nat (length (items round))<=countLimit)%Z).
  { unfold countLimit. entry_numerals. lia. }
  assert (Hfcount : (Z.of_nat (length (activeFactors (items round)))<=countLimit)%Z).
  { rewrite entry_factors_length. unfold activeCount. pose proof (weights_length (items round)). lia. }
  pose proof (entry_factor_valid _ Hvalid) as Hfvalid.
  pose proof (entry_factor_stop (items round) 0) as [Hleft Hvisited].
  unfold factorRun. split; [exact Hleft|]. split; [exact Hvisited|].
  split; [apply entry_factor_sum|]. split.
  - rewrite entry_factor_sum. apply factor_sum_target; assumption.
  - split.
    + intro k. apply factor_sum_target; [|apply entry_factor_prefix_valid; exact Hfvalid].
      rewrite firstn_length. pose proof (Nat.le_min_r k (length (activeFactors (items round)))). lia.
    + split; assumption.
Qed.
Print Assumptions entry_factors_length.
Print Assumptions entry_frozen_factors.
Print Assumptions entry_factor_sum.
Print Assumptions entry_factor_stop.
Print Assumptions entry_factor_valid.
Print Assumptions entry_factor_prefix_valid.
Print Assumptions entry_factor_target.
