Require Import Reals ZArith List Psatz Gappa.Gappa_library.
Require Import WeightTarget ShareTarget Target ConversionTarget Conversion DistributionTarget Distribution InputTarget BranchTarget BranchProof PrefixTarget.
Import ListNotations.
Open Scope R_scope.

Lemma weights_app : forall xs ys,
  activeWeights (xs ++ ys) = activeWeights xs ++ activeWeights ys.
Proof.
  induction xs as [|x xs IH]; intro ys; [reflexivity|].
  cbn. destruct (frozen x); cbn; rewrite IH; reflexivity.
Qed.
Lemma count_zero : forall xs, activeCount xs = O ->
  Forall (fun x => frozen x = true) xs.
Proof.
  induction xs as [|x xs IH]; intro H; [constructor|].
  unfold activeCount in H. cbn in H. destruct (frozen x) eqn:Hx.
  - constructor; [exact Hx|apply IH; exact H].
  - discriminate.
Qed.
Lemma frozen_weights : forall xs, Forall (fun x => frozen x = true) xs -> activeWeights xs = [].
Proof.
  intros xs H. induction H; [reflexivity|]. cbn. rewrite H. exact IHForall.
Qed.
Lemma frozen_spec : forall xs before, Forall (fun x => frozen x = true) xs ->
  specification before xs = xs.
Proof.
  induction xs as [|x xs IH]; intros before H; [reflexivity|].
  inversion H; subst. cbn. rewrite H2. rewrite IH by assumption. reflexivity.
Qed.
Lemma stop_general : forall xs sum,
  remaining (produce (activeCount xs) sum xs) = O /\
  (visited (produce (activeCount xs) sum xs) <= length xs)%nat /\
  Forall (fun x => frozen x = true) (skipn (visited (produce (activeCount xs) sum xs)) xs).
Proof.
  induction xs as [|x xs IH]; intro sum; [cbn; repeat split; constructor|].
  unfold activeCount at 1 2 3. cbn [activeWeights length]. destruct (frozen x) eqn:Hx.
  - destruct (length (activeWeights xs)) eqn:Hcount.
    + cbn [produce visited remaining skipn]. repeat split; try lia.
      constructor; [exact Hx|apply count_zero; exact Hcount].
    + specialize (IH sum). unfold activeCount in IH. rewrite Hcount in IH.
      cbn [length produce]. rewrite Hx. cbn [remaining visited skipn].
      destruct IH as [Ha [Hb Hc]]. cbn [length]. split; [exact Ha|]. split; [apply le_n_S; exact Hb|exact Hc].
  - cbn [length produce]. rewrite Hx. cbn [remaining visited skipn].
    specialize (IH (WeightTarget.rn (sum + sourceWeight (payload x)))). unfold activeCount in IH.
    destruct IH as [Ha [Hb Hc]]. cbn [length]. split; [exact Ha|]. split; [apply le_n_S; exact Hb|exact Hc].
Qed.
Theorem stop_target : StopTarget.
Proof.
  intro xs. destruct (stop_general xs 0) as [Ha [Hb Hc]].
  unfold run. repeat split; try assumption.
  pose proof (f_equal activeWeights (firstn_skipn (visited (produce (activeCount xs) 0 xs)) xs)) as Hsplit.
  rewrite weights_app, (frozen_weights _ Hc), app_nil_r in Hsplit.
  exact (f_equal (@length R) Hsplit).
Qed.
Lemma accumulate_app : forall a b s,
  accumulate (a ++ b) s = accumulate b (accumulate a s).
Proof. intros. unfold accumulate. apply fold_left_app. Qed.
Lemma sum_general : forall xs s,
  total (produce (activeCount xs) s xs) = accumulate (activeWeights xs) s.
Proof.
  induction xs as [|x xs IH]; intro s; [reflexivity|].
  unfold activeCount at 1. cbn [activeWeights length]. destruct (frozen x) eqn:Hx.
  - destruct (length (activeWeights xs)) eqn:Hcount.
    + cbn [produce total]. apply length_zero_iff_nil in Hcount. rewrite Hcount. reflexivity.
    + cbn [length produce]. rewrite Hx. cbn [total]. specialize (IH s).
      unfold activeCount in IH. rewrite Hcount in IH. exact IH.
  - cbn [length produce]. rewrite Hx. cbn [total accumulate fold_left]. apply IH.
Qed.
Theorem sum_target : SumTarget.
Proof. intro xs. apply sum_general. Qed.
Lemma specification_general : forall xs before,
  rows (produce (activeCount xs) (accumulate (activeWeights before) 0) xs) = specification before xs.
Proof.
  induction xs as [|x xs IH]; intros before; [reflexivity|].
  unfold activeCount at 1. cbn [activeWeights length]. destruct (frozen x) eqn:Hx.
  - destruct (length (activeWeights xs)) eqn:Hcount.
    + cbn [produce rows]. symmetry. apply frozen_spec. constructor; [exact Hx|].
      apply count_zero. exact Hcount.
    + cbn [length produce]. rewrite Hx. cbn [rows specification]. rewrite Hx. f_equal.
      specialize (IH (before ++ [x])). rewrite weights_app in IH.
      cbn [activeWeights] in IH. rewrite Hx, app_nil_r in IH.
      unfold activeCount in IH. rewrite Hcount in IH. exact IH.
  - cbn [length produce]. rewrite Hx. cbn [rows specification]. rewrite Hx. f_equal.
    + unfold prefixShare, storedShare, shareAt.
      rewrite weights_app. cbn [activeWeights]. rewrite Hx.
      rewrite accumulate_app. reflexivity.
    + specialize (IH (before ++ [x])). rewrite weights_app in IH.
      cbn [activeWeights] in IH. rewrite Hx, accumulate_app in IH.
      exact IH.
Qed.
Theorem specification_target : SpecificationTarget.
Proof. intro xs. exact (specification_general xs []). Qed.
Lemma spec_identity : forall xs before,
  map identity (specification before xs) = map identity xs.
Proof.
  induction xs as [|x xs IH]; intros before; [reflexivity|].
  cbn [specification map]. rewrite IH. destruct (frozen x); reflexivity.
Qed.
Lemma spec_frozen : forall xs before i x,
  nth_error xs i = Some x -> frozen x = true ->
  nth_error (specification before xs) i = Some x.
Proof.
  induction xs as [|a xs IH]; intros before i x H Hf; destruct i; cbn in H; try discriminate.
  - inversion H; subst. cbn [specification nth_error]. rewrite Hf. reflexivity.
  - cbn [specification nth_error]. eapply IH; eauto.
Qed.
Theorem preservation_target : PreservationTarget.
Proof.
  intro xs. rewrite specification_target. split; [apply spec_identity|].
  intros. eapply spec_frozen; eauto.
Qed.
Lemma spec_prefix : forall before prefix x after,
  frozen x = false ->
  nth_error (specification prefix (before ++ x :: after)) (length before) =
    Some (setStored x (prefixShare (prefix ++ before) x)).
Proof.
  induction before as [|a before IH]; intros prefix x after Hx.
  - cbn [app length specification nth_error]. rewrite Hx, app_nil_r. reflexivity.
  - cbn [app length specification nth_error]. rewrite IH by exact Hx.
    rewrite <- app_assoc. reflexivity.
Qed.
Theorem prefix_target : PrefixTarget.PrefixTarget.
Proof.
  intros before x after Hx. rewrite specification_target.
  exact (spec_prefix before [] x after Hx).
Qed.
Lemma weights_length : forall xs, (length (activeWeights xs) <= length xs)%nat.
Proof. induction xs; [cbn; lia|]. cbn. destruct (frozen a); cbn; lia. Qed.
Lemma weights_valid : forall xs, Forall ItemValid xs -> Forall FiniteWeight (activeWeights xs).
Proof.
  intros xs H. induction H; [constructor|]. cbn. destruct (frozen x) eqn:Hx; [exact IHForall|].
  constructor; [apply BranchProof.source_finite_target; apply H; exact Hx|exact IHForall].
Qed.
Lemma prefix_range : forall before x after,
  Admitted (before ++ x :: after) -> frozen x = false -> 0 <= prefixShare before x <= 1.
Proof.
  intros before x after [Hcount Hvalid] Hx. unfold prefixShare.
  apply Distribution.stored_target. split.
  - pose proof (weights_length (before ++ [x])). rewrite app_length in Hcount.
    cbn in Hcount. rewrite app_length in H. cbn in H. lia.
  - split.
    + apply weights_valid. rewrite Forall_app in Hvalid. destruct Hvalid as [Hb Htail].
      inversion Htail; subst. apply Forall_app. split; [exact Hb|constructor; [assumption|constructor]].
    + rewrite weights_app. cbn [activeWeights]. rewrite Hx. apply in_or_app. right. left. reflexivity.
Qed.
Lemma nth_split : forall (xs : list Item) i x, nth_error xs i = Some x ->
  exists before after, xs = before ++ x :: after /\ length before = i.
Proof.
  induction xs as [|a xs IH]; intros i x H; destruct i; cbn in H; try discriminate.
  - inversion H; subst. exists [], xs. split; reflexivity.
  - destruct (IH i x H) as [before [after [Heq Hlen]]].
    exists (a :: before), after. split; cbn; [rewrite Heq; reflexivity|rewrite Hlen; reflexivity].
Qed.
Theorem range_target : RangeTarget.
Proof.
  intros xs i x y Ha Hx Hf Hy.
  destruct (nth_split xs i x Hx) as [before [after [Heq Hlen]]]. subst xs i.
  rewrite prefix_target in Hy by exact Hf. inversion Hy; subst.
  cbn [stored setStored]. eapply prefix_range; eauto.
Qed.
Theorem delta_target : PrefixTarget.DeltaTarget.
Proof.
  intros xs i x y free Ha Hx Hf Hy Hfree.
  pose proof (range_target xs i x y Ha Hx Hf Hy) as Hr.
  unfold producedDelta. apply Conversion.safety_target; [exact Hfree|].
  unfold shareChoice. destruct (Req_EM_T (stored y) 1); [exact I|].
  destruct (Rlt_dec 0 (stored y)); [exact Hr|exact I].
Qed.
Theorem branch_target : PrefixTarget.BranchTarget.
Proof.
  split; intros free x H; unfold producedDelta, shareChoice; rewrite H.
  - destruct (Req_EM_T 1 1); [reflexivity|contradiction].
  - destruct (Req_EM_T 0 1); [lra|]. destruct (Rlt_dec 0 0); [lra|reflexivity].
Qed.
Theorem full_stored_prefix_target : FullStoredPrefixTarget.
Proof.
  exact (conj stop_target (conj specification_target (conj preservation_target
    (conj prefix_target (conj sum_target (conj range_target (conj delta_target branch_target))))))).
Qed.

Print Assumptions stop_target.
Print Assumptions specification_target.
Print Assumptions preservation_target.
Print Assumptions prefix_target.
Print Assumptions sum_target.
Print Assumptions range_target.
Print Assumptions delta_target.
Print Assumptions branch_target.
Print Assumptions full_stored_prefix_target.
