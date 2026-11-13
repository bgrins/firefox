Require Import Reals ZArith List Psatz Gappa.Gappa_library.
Require Import WeightTarget InputTarget PrefixTarget PrefixProof ReverseTarget.
Import ListNotations.
Open Scope R_scope.

Definition activePairs (xs : list (nat * Item)) := filter (fun p => negb (frozen (snd p))) xs.
Definition pairCount (xs : list (nat * Item)) := length (activePairs xs).
Lemma loop_shape : forall xs free,
  reverseRemaining (reverseLoop (pairCount xs) free xs) = O /\
  (examined (reverseLoop (pairCount xs) free xs) <= length xs)%nat /\
  map ordinal (events (reverseLoop (pairCount xs) free xs)) = map fst (activePairs xs).
Proof.
  induction xs as [|[i x] xs IH]; intro free; [cbn; repeat split; constructor|].
  unfold pairCount at 1 2 3. cbn [activePairs filter snd]. fold (activePairs xs).
  destruct (frozen x) eqn:Hx; cbn [negb length].
  - destruct (length (activePairs xs)) eqn:Hcount.
    + cbn [reverseLoop reverseRemaining examined events map].
      apply length_zero_iff_nil in Hcount. rewrite Hcount. cbn. repeat split; lia.
    + cbn [reverseLoop]. rewrite Hx. cbn [reverseRemaining examined events length].
      specialize (IH free). unfold pairCount in IH. rewrite Hcount in IH.
      destruct IH as [Ha [Hb Hc]]. split; [exact Ha|]. split; [apply le_n_S; exact Hb|exact Hc].
  - cbn [reverseLoop]. rewrite Hx. cbn [reverseRemaining examined events map ordinal fst length].
    specialize (IH (free - producedDelta free x)%Z).
    destruct IH as [Ha [Hb Hc]]. split; [exact Ha|]. split; [apply le_n_S; exact Hb|].
    f_equal. exact Hc.
Qed.
Lemma pairs_rev : forall xs, activePairs (rev xs) = rev (activePairs xs).
Proof.
  intro xs. unfold activePairs. induction xs as [|x xs IH]; [reflexivity|].
  cbn [rev]. rewrite filter_app. cbn [filter]. rewrite IH.
  destruct (negb (frozen (snd x))); cbn [rev]; [reflexivity|apply app_nil_r].
Qed.
Lemma count_rev : forall xs, pairCount (rev xs) = pairCount xs.
Proof. intro xs. unfold pairCount. rewrite pairs_rev, rev_length. reflexivity. Qed.
Lemma positioned_length : forall xs, length (positioned xs) = length xs.
Proof. intro xs. unfold positioned. rewrite combine_length, seq_length, Nat.min_id. reflexivity. Qed.
Lemma positioned_count : forall xs n,
  pairCount (combine (seq n (length xs)) xs) = activeCount xs.
Proof.
  induction xs as [|x xs IH]; intro n; [reflexivity|].
  cbn [length seq combine pairCount activePairs filter snd activeCount activeWeights].
  destruct (frozen x); cbn [negb length]; [apply IH|f_equal; apply IH].
Qed.
Lemma spec_weights : forall xs before, activeWeights (specification before xs) = activeWeights xs.
Proof.
  induction xs as [|x xs IH]; intros before; [reflexivity|].
  cbn [specification]. destruct (frozen x) eqn:Hx.
  - cbn [activeWeights]. rewrite Hx. apply IH.
  - cbn [activeWeights setStored frozen payload]. rewrite Hx. f_equal. apply IH.
Qed.
Lemma rows_count : forall xs, activeCount (rows (run xs)) = activeCount xs.
Proof. intro xs. rewrite specification_target. unfold activeCount. rewrite spec_weights. reflexivity. Qed.
Lemma rows_length : forall xs, length (rows (run xs)) = length xs.
Proof.
  intro xs. pose proof (f_equal (@length _) (proj1 (preservation_target xs))) as H.
  rewrite !map_length in H. exact H.
Qed.
Lemma reverse_pair_count : forall xs,
  pairCount (rev (positioned (rows (run xs)))) = activeCount xs.
Proof. intro xs. rewrite count_rev. unfold positioned. rewrite positioned_count. apply rows_count. Qed.
Lemma reverse_pair_length : forall xs,
  length (rev (positioned (rows (run xs)))) = length xs.
Proof. intro xs. rewrite rev_length, positioned_length. apply rows_length. Qed.
Fixpoint indices (n : nat) (xs : list Item) : list nat :=
  match xs with [] => [] | x :: tail =>
    if frozen x then indices (S n) tail else n :: indices (S n) tail end.
Lemma indices_positioned : forall xs n,
  map fst (activePairs (combine (seq n (length xs)) xs)) = indices n xs.
Proof.
  induction xs as [|x xs IH]; intro n; [reflexivity|].
  cbn [length seq combine activePairs filter snd indices].
  destruct (frozen x); cbn [negb map fst]; rewrite IH; reflexivity.
Qed.
Lemma indices_spec : forall xs before n,
  indices n (specification before xs) = indices n xs.
Proof.
  induction xs as [|x xs IH]; intros before n; [reflexivity|].
  cbn [specification]. destruct (frozen x) eqn:Hx.
  - cbn [indices]. rewrite Hx. apply IH.
  - cbn [indices setStored frozen]. rewrite Hx. f_equal. apply IH.
Qed.
Lemma rows_positions : forall xs, activePositions (rows (run xs)) = activePositions xs.
Proof.
  intro xs. unfold activePositions, positioned. rewrite !indices_positioned.
  rewrite specification_target. apply indices_spec.
Qed.
Theorem reverse_count_target : ReverseCountTarget.
Proof.
  intros xs free. unfold reverseRun. destruct (Req_EM_T (total (run xs)) 0).
  - cbn [reverseRemaining examined events length]. repeat split; lia.
  - rewrite <- (reverse_pair_count xs).
    destruct (loop_shape (rev (positioned (rows (run xs)))) free) as [Ha [Hb Hc]].
    split; [exact Ha|]. split.
    + rewrite reverse_pair_length in Hb. exact Hb.
    + pose proof (f_equal (@length _) Hc) as Hlen. rewrite !map_length in Hlen. exact Hlen.
Qed.
Theorem reverse_order_target : ReverseOrderTarget.
Proof.
  intros xs free. unfold reverseRun. destruct (Req_EM_T (total (run xs)) 0); [reflexivity|].
  rewrite <- (reverse_pair_count xs).
  rewrite (proj2 (proj2 (loop_shape (rev (positioned (rows (run xs)))) free))).
  rewrite pairs_rev, map_rev. change (rev (activePositions (rows (run xs))) = rev (activePositions xs)).
  rewrite rows_positions. reflexivity.
Qed.
Lemma loop_trace : forall xs left free,
  Chained free (events (reverseLoop left free xs)) (finalFree (reverseLoop left free xs)).
Proof.
  induction xs as [|[i x] xs IH]; intros left free; destruct left; cbn [reverseLoop events finalFree Chained]; try reflexivity.
  destruct (frozen x); cbn [events finalFree Chained beforeFree afterFree delta]; [apply IH|].
  repeat split; try reflexivity. apply IH.
Qed.
Theorem trace_target : TraceTarget.
Proof.
  intros xs free. unfold reverseRun. destruct (Req_EM_T (total (run xs)) 0); [reflexivity|apply loop_trace].
Qed.
Lemma chained_sum : forall es start finish,
  Chained start es finish -> finish = (start - eventSum es)%Z.
Proof.
  induction es as [|e es IH]; intros start finish H.
  - cbn [Chained] in H. cbn [eventSum map fold_right]. lia.
  - destruct H as [Ha [Hb Htail]]. specialize (IH (afterFree e) finish Htail).
    cbn [eventSum map fold_right]. unfold eventSum in IH. lia.
Qed.
Theorem conservation_target : ConservationTarget.
Proof. intros xs free. apply chained_sum. apply trace_target. Qed.
Theorem reverse_branches_target : ReverseBranchesTarget.
Proof.
  split.
  - intros xs free Hzero. unfold reverseRun. rewrite Hzero.
    destruct (Req_EM_T 0 0); [split; reflexivity|contradiction].
  - intro free. unfold deltaAt, shareChoice.
    destruct (Req_EM_T 1 1); [|contradiction].
    destruct (Req_EM_T 0 1); [lra|]. destruct (Rlt_dec 0 0); [lra|]. split; reflexivity.
Qed.

Print Assumptions reverse_count_target.
Print Assumptions reverse_order_target.
Print Assumptions trace_target.
Print Assumptions conservation_target.
Print Assumptions reverse_branches_target.
